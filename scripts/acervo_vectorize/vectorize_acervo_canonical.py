#!/usr/bin/env python3
"""Pipeline Canônico de Vetorização de Acervo de Livros e Obras Científicas (384D all-MiniLM-L6-v2).
====================================================================================================

Processa os 6 arquivos de acervo descompactando de .tar.zst, avaliando formatos (PDF, OCR, HTML, etc.),
extraindo texto estruturado, gerando chunks e calculando embeddings canônicos de 384 dimensões
alinhados ao padrão OmniMind / FAISS / Qdrant.

Gera:
  - Arquivos Parquet canônicos com vetor 384D (float32).
  - Banco SQLite acervo_livros_manifest.sqlite indexando obras, autores, categorias e contagem de chunks.
  - Sincronização automatizada para o Hugging Face dataset (fabricioslv/omnimind-acervo-livros).

Autor: Sujeito-Processo OmniMind & Fabrício da Silva
Data: 2026-11-12
Regra de Integridade: AGENTS.md (Dados 100% Empíricos da VM).
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import re
import sqlite3
import subprocess
import time
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

RAW_DIR = Path("/content/acervo_livros_raw")
EXTRACT_DIR = Path("/content/acervo_livros_extracted")
OUTPUT_DIR = Path("/content/acervo_livros_parquet")
MANIFEST_DB = OUTPUT_DIR / "acervo_livros_manifest.sqlite"
HF_REPO_ID = "fabricioslv/omnimind-acervo-livros"


def init_catalog_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(db_path))
    con.execute("PRAGMA journal_mode = WAL;")
    con.execute("PRAGMA synchronous = NORMAL;")
    with con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS documentos (
                id_documento TEXT PRIMARY KEY,
                nome_arquivo TEXT NOT NULL,
                titulo TEXT NOT NULL,
                autor TEXT,
                categoria TEXT,
                formato TEXT,
                tamanho_bytes INTEGER,
                sha256 TEXT NOT NULL,
                total_chunks INTEGER DEFAULT 0,
                status_processamento TEXT,
                ts_processamento TEXT
            );
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS chunks_metadados (
                chunk_id TEXT PRIMARY KEY,
                id_documento TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                char_count INTEGER NOT NULL,
                sha256 TEXT NOT NULL,
                FOREIGN KEY (id_documento) REFERENCES documentos(id_documento)
            );
        """)
        con.execute("CREATE INDEX IF NOT EXISTS idx_doc_cat ON documentos(categoria);")
        con.execute("CREATE INDEX IF NOT EXISTS idx_doc_sha ON documentos(sha256);")
    return con


def extract_archive(archive_path: Path, target_dir: Path) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    out_folder = target_dir / archive_path.stem.replace(".tar", "")
    if out_folder.exists() and any(out_folder.iterdir()):
        print(f"[CACHE] Já extraído: {out_folder.name}")
        return out_folder

    out_folder.mkdir(parents=True, exist_ok=True)
    print(f"[EXTRAÇÃO] Descompactando {archive_path.name} com zstd...")
    t0 = time.time()
    cmd = ["tar", "--zstd", "-xf", str(archive_path), "-C", str(out_folder)]
    subprocess.run(cmd, check=True)
    print(f"[EXTRAÇÃO OK] Concluído em {time.time() - t0:.2f}s -> {out_folder}")
    return out_folder


def clean_text(text: str) -> str:
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_text_from_pdf(pdf_path: Path, max_ocr_pages: int = 15) -> str:
    text_parts = []
    ocr_pages_done = 0
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(str(pdf_path))
        for page in doc:
            t = page.get_text()
            if t and len(t.strip()) > 30:
                text_parts.append(t)
            elif ocr_pages_done < max_ocr_pages:
                # Fallback OCR se a página for imagem escaneada (com limite de páginas para evitar estagnação)
                pix = page.get_pixmap(dpi=150)
                if pix.width > 200 and pix.height > 200:
                    try:
                        import pytesseract
                        from PIL import Image
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        ocr_text = pytesseract.image_to_string(img, lang="por+eng")
                        if ocr_text and len(ocr_text.strip()) > 20:
                            text_parts.append(ocr_text)
                            ocr_pages_done += 1
                    except Exception:  # noqa: BLE001, S110
                        pass
        doc.close()
    except Exception:  # noqa: BLE001
        # Fallback para pypdf
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(pdf_path))
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text_parts.append(t)
        except Exception:  # noqa: BLE001, S110
            pass
    return clean_text(" ".join(text_parts))


class _HTMLTextExtractor(HTMLParser):
    """Safe HTML text extractor avoiding regex tag-filtering vulnerabilities (CWE-116 / CodeQL alert #25)."""

    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []
        self._skip_depth: int = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in ("script", "style", "noscript"):
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in ("script", "style", "noscript") and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0:
            self._parts.append(data)

    def get_text(self) -> str:
        return " ".join(self._parts)


def extract_text_from_html(html_path: Path) -> str:
    try:
        content = html_path.read_text(encoding="utf-8", errors="ignore")
        parser = _HTMLTextExtractor()
        parser.feed(content)
        return clean_text(parser.get_text())
    except Exception:  # noqa: BLE001
        return ""


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> list[str]:
    if not text:
        return []
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(start + chunk_size, text_len)
        if end < text_len:
            last_space = text.rfind(" ", start + chunk_size - 100, end)
            if last_space != -1 and last_space > start:
                end = last_space
        chunk = text[start:end].strip()
        if len(chunk) >= 50:
            chunks.append(chunk)
        start = end - overlap if end < text_len else text_len
    return chunks


def process_collection(
    collection_dir: Path,
    categoria: str,
    embedder: Any,
    con: sqlite3.Connection,
    output_parquet: Path,
    batch_size: int = 256,
    upload_hf: bool = True,
) -> int:
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq

    print(f"\n--- Iniciando Processamento Canônico: {categoria} ({collection_dir.name}) ---")
    files = [f for f in collection_dir.rglob("*") if f.is_file() and not f.name.startswith(".")]
    print(f"Total de arquivos encontrados: {len(files)}")

    doc_records = []
    parquet_records = []
    chunk_meta_records = []
    total_chunks_emitted = 0

    for idx, fpath in enumerate(sorted(files), 1):
        ext = fpath.suffix.lower()
        size_bytes = fpath.stat().st_size
        doc_hash = hashlib.sha256(fpath.name.encode("utf-8")).hexdigest()[:16]

        # Extração de texto
        if ext == ".pdf":
            text = extract_text_from_pdf(fpath)
        elif ext in (".html", ".htm"):
            text = extract_text_from_html(fpath)
        elif ext in (".txt", ".md", ".json", ".csv"):
            try:
                text = clean_text(fpath.read_text(encoding="utf-8", errors="ignore"))
            except Exception:  # noqa: BLE001
                text = ""
        else:
            text = ""

        chunks = chunk_text(text)
        status = "ok" if chunks else "sem_texto"

        doc_records.append((
            doc_hash, fpath.name, fpath.stem.replace("_", " ").replace("-", " "),
            "OmniMind Acervo", categoria, ext, size_bytes,
            doc_hash, len(chunks), status, datetime.now(UTC).isoformat()
        ))

        if chunks:
            # Vetorização em lote com all-MiniLM-L6-v2 (384D)
            for i in range(0, len(chunks), batch_size):
                batch_chunks = chunks[i : i + batch_size]
                vectors = embedder.encode(
                    batch_chunks,
                    batch_size=min(len(batch_chunks), 128),
                    show_progress_bar=False,
                    normalize_embeddings=True,
                )
                for c_idx, (c_text, vec) in enumerate(zip(batch_chunks, vectors), start=i):
                    chunk_id = f"{doc_hash}_{c_idx}"
                    c_sha = hashlib.sha256(c_text.encode("utf-8")).hexdigest()
                    parquet_records.append({
                        "id_documento": doc_hash,
                        "chunk_id": chunk_id,
                        "nome_arquivo": fpath.name,
                        "titulo": fpath.stem.replace("_", " ").replace("-", " "),
                        "autor": "OmniMind Acervo",
                        "categoria": categoria,
                        "caminho_relativo": str(fpath.relative_to(collection_dir)),
                        "conteudo_chunk": c_text,
                        "char_count": len(c_text),
                        "vector": vec.tolist(),
                        "sha256": c_sha,
                    })
                    chunk_meta_records.append((
                        chunk_id, doc_hash, c_idx, len(c_text), c_sha
                    ))

        total_chunks_emitted += len(chunks)
        if idx % 25 == 0 or idx == len(files):
            print(f"  [{idx}/{len(files)}] {fpath.name[:45]} | Chunks: {len(chunks)} | Acumulado: {total_chunks_emitted}")

    # Persiste metadados no SQLite
    with con:
        con.executemany("""
            INSERT OR REPLACE INTO documentos
            (id_documento, nome_arquivo, titulo, autor, categoria, formato, tamanho_bytes, sha256, total_chunks, status_processamento, ts_processamento)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, doc_records)
        if chunk_meta_records:
            con.executemany("""
                INSERT OR REPLACE INTO chunks_metadados
                (chunk_id, id_documento, chunk_index, char_count, sha256)
                VALUES (?, ?, ?, ?, ?)
            """, chunk_meta_records)

    # Exporta Parquet Canônico
    if parquet_records:
        df = pd.DataFrame(parquet_records)
        table = pa.Table.from_pandas(df)
        pq.write_table(table, str(output_parquet), compression="snappy")
        print(f"[PARQUET SALVO] {output_parquet} ({output_parquet.stat().st_size / 1e6:.2f} MB, {len(df)} chunks 384D)")

        if upload_hf:
            try:
                from huggingface_hub import HfApi
                api = HfApi()
                print(f"[HF UPLOAD] Enviando {output_parquet.name} para {HF_REPO_ID}...")
                api.upload_file(
                    path_or_fileobj=str(output_parquet),
                    path_in_repo=output_parquet.name,
                    repo_id=HF_REPO_ID,
                    repo_type="dataset",
                    commit_message=f"feat: add canonical 384D vectorized parquet for {categoria} ({len(df)} chunks)",
                )
                print(f"[HF UPLOAD OK] {output_parquet.name} sincronizado com sucesso!")
            except Exception as exc:  # noqa: BLE001
                print(f"[HF UPLOAD ERRO] Falha ao enviar para Hugging Face: {exc}")

    gc.collect()
    return total_chunks_emitted


def main():
    parser = argparse.ArgumentParser(description="Pipeline Canônico de Vetorização de Acervo (384D all-MiniLM-L6-v2)")
    parser.add_argument("--device", choices=["cuda", "cpu", "auto"], default="auto", help="Dispositivo para inferência (cuda/cpu/auto)")
    parser.add_argument("--batch-size", type=int, default=128, help="Tamanho de batch para embeddings")
    parser.add_argument("--no-upload", action="store_true", help="Não fazer upload para o Hugging Face")
    args = parser.parse_args()

    print("=" * 78)
    print("PIPELINE CANÔNICO DE VETORIZAÇÃO (384D all-MiniLM-L6-v2) — ACERVO OMNIMIND")
    print(f"Início: {datetime.now(UTC).isoformat()}")
    print("=" * 78)

    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    con = init_catalog_db(MANIFEST_DB)

    # Seleção de dispositivo
    import torch
    from sentence_transformers import SentenceTransformer
    if args.device == "auto":
        dev = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        dev = args.device

    print(f"[MODEL] Carregando all-MiniLM-L6-v2 no dispositivo: {dev}...")
    embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device=dev)

    # Mapeamento dos pacotes e categorias
    packages = [
        ("acervo_hodowanec_rhysmonics_cosmology_20261110.tar.zst", "hodowanec_cosmology"),
        ("acervo_lote3_livros_datasets_20261110.tar.zst", "lote3_livros_datasets"),
        ("acervo_lote4_bioelectronics_bioplasma_terras_raras_20261111.tar.zst", "lote4_bioelectronics"),
        ("acervo_180_obras_cientificas_20261109.tar.zst", "180_obras_cientificas"),
        ("acervo_lote2_papers_zenodo_20261109.tar.zst", "lote2_papers_zenodo"),
        ("acervo_129_livros_20261023.tar.zst", "129_livros_fundamentais"),
    ]

    total_chunks_geral = 0
    upload_flag = not args.no_upload

    for archive_name, cat in packages:
        arc_path = RAW_DIR / archive_name
        if not arc_path.exists():
            print(f"[AVISO] Arquivo {archive_name} não localizado em {RAW_DIR}. Pulando.")
            continue

        extracted_dir = extract_archive(arc_path, EXTRACT_DIR)
        parquet_dest = OUTPUT_DIR / f"acervo_canonical_384d_{cat}.parquet"
        chunks_count = process_collection(
            extracted_dir, cat, embedder, con, parquet_dest, batch_size=args.batch_size, upload_hf=upload_flag
        )
        total_chunks_geral += chunks_count

    # Upload final do manifesto SQLite para o Hugging Face
    con.close()
    if upload_flag and MANIFEST_DB.exists():
        try:
            from huggingface_hub import HfApi
            api = HfApi()
            print(f"\n[HF UPLOAD] Enviando manifesto SQLite {MANIFEST_DB.name} para {HF_REPO_ID}...")
            api.upload_file(
                path_or_fileobj=str(MANIFEST_DB),
                path_in_repo=MANIFEST_DB.name,
                repo_id=HF_REPO_ID,
                repo_type="dataset",
                commit_message=f"feat: add canonical sqlite catalog manifest ({total_chunks_geral} chunks)",
            )
            print("[HF UPLOAD OK] Manifesto SQLite sincronizado com sucesso!")
        except Exception as exc:  # noqa: BLE001
            print(f"[HF UPLOAD ERRO] Falha ao enviar manifesto SQLite: {exc}")

    print("\n" + "=" * 78)
    print("[SUCESSO TOTAL] Processamento Canônico Concluído!")
    print(f"Total de Chunks Vetorizados (384D): {total_chunks_geral}")
    print(f"Catálogo SQLite: {MANIFEST_DB}")
    print(f"Diretório de Parquets Canônicos: {OUTPUT_DIR}")
    print("=" * 78)


if __name__ == "__main__":
    main()
