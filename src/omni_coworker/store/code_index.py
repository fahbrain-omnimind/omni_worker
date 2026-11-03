"""Vectorized code index (all-MiniLM-L6-v2).

English: Chunks the omni_coworker package into embeddable units
(module, class, function), embeds with sentence-transformers
all-MiniLM-L6-v2, persists to parquet + optional faiss index.
This is the "symbolic body" the agent studies and dreams over.

pt-BR: Fati o pacote omni_coworker em unidades embutíveis (módulo,
classe, função), vetoriza com all-MiniLM-L6-v2, persiste em parquet +
índice faiss opcional. É o "corpo simbólico" que o agente estuda e
sonha.
"""

from __future__ import annotations

import ast
import json
import os
from pathlib import Path

_MODEL = None
_INDEX = None
_ROWS: list[dict] = []

MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"


def _get_model():
    """Lazy sentence-transformers model singleton."""
    global _MODEL
    if _MODEL is None:
        from sentence_transformers import SentenceTransformer

        _MODEL = SentenceTransformer(MODEL_ID)
    return _MODEL


def _chunk_file(path: Path, root: Path) -> list[dict]:
    """Split a Python file into embeddable chunks via AST.

    English: module docstring + one chunk per top-level def/class.
    pt-BR: docstring do módulo + um chunk por def/classe de topo.
    """
    rel = str(path.relative_to(root))
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    chunks = []
    doc = ast.get_docstring(tree)
    if doc:
        chunks.append({"path": rel, "kind": "module", "name": path.stem, "text": doc[:1200]})
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            seg = ast.get_docstring(node) or ""
            header = f"{type(node).__name__} {node.name}: {seg}"
            chunks.append({
                "path": rel, "kind": type(node).__name__.lower(),
                "name": node.name, "text": header[:1200],
            })
    return chunks


def build_index(root: str | Path, out_dir: str | Path) -> dict:
    """Embed all Python files under root and persist.

    English: Writes chunks.parquet (+ code_index.faiss when faiss is
    installed) and manifest.json under out_dir.
    pt-BR: Escreve chunks.parquet (+ code_index.faiss quando faiss está
    instalado) e manifest.json em out_dir.
    """
    import hashlib
    import numpy as np
    import pandas as pd

    root = Path(root)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for py in sorted(root.rglob("*.py")):
        if "__pycache__" in py.parts:
            continue
        rows.extend(_chunk_file(py, root))
    if not rows:
        return {"chunks": 0}

    # Tentativa de carregar cache incremental anterior
    cached_vecs: dict[str, np.ndarray] = {}
    old_parquet = out_dir / "chunks.parquet"
    old_npy = out_dir / "embeddings.npy"
    if old_parquet.exists() and old_npy.exists():
        try:
            old_df = pd.read_parquet(old_parquet)
            old_embs = np.load(old_npy)
            if len(old_df) == len(old_embs):
                for idx, row in old_df.iterrows():
                    th = hashlib.sha256(str(row["text"]).encode("utf-8")).hexdigest()
                    cached_vecs[th] = old_embs[idx]
        except Exception:
            cached_vecs.clear()

    # Identificar chunks novos vs cacheados
    row_hashes = [hashlib.sha256(r["text"].encode("utf-8")).hexdigest() for r in rows]
    missing_indices = [i for i, h in enumerate(row_hashes) if h not in cached_vecs]

    if missing_indices:
        model = _get_model()
        new_texts = [rows[i]["text"] for i in missing_indices]
        encoded = model.encode(new_texts, normalize_embeddings=True)
        encoded = np.asarray(encoded, dtype="float32")
        dim = int(encoded.shape[1])
        for idx_in_new, orig_idx in enumerate(missing_indices):
            cached_vecs[row_hashes[orig_idx]] = encoded[idx_in_new]
    else:
        # Nenhum chunk novo/modificado
        if cached_vecs:
            dim = next(iter(cached_vecs.values())).shape[0]
        else:
            model = _get_model()
            dim = 384

    # Monta matriz final preservando ordem
    embs = np.empty((len(rows), dim), dtype="float32")
    for i, h in enumerate(row_hashes):
        embs[i] = cached_vecs[h]

    df = pd.DataFrame([{k: r[k] for k in ("path", "kind", "name", "text")} for r in rows])
    df.to_parquet(out_dir / "chunks.parquet", index=False)
    np.save(out_dir / "embeddings.npy", embs)

    used_faiss = False
    try:
        import faiss

        index = faiss.IndexFlatIP(embs.shape[1])
        index.add(embs)
        faiss.write_index(index, str(out_dir / "code_index.faiss"))
        used_faiss = True
    except Exception:
        pass

    manifest = {
        "model": MODEL_ID,
        "chunks": len(rows),
        "dim": int(embs.shape[1]),
        "faiss": used_faiss,
        "incremental_hits": len(rows) - len(missing_indices),
        "incremental_misses": len(missing_indices),
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    global _INDEX, _LOADED_DIR
    _INDEX, _LOADED_DIR = None, None
    return manifest


_LOADED_DIR: tuple[Path, float] | None = None


def _load(out_dir: str | Path) -> bool:
    """Load persisted index into memory (cached per out_dir + mtime).

    English: Returns False when the index files don't exist — callers
    degrade to empty results instead of crashing (audit D2/D3). The
    cache key includes chunks.parquet's mtime so an in-place rebuild
    is picked up without restarting the consumer.
    pt-BR: Retorna False quando os arquivos do índice não existem —
    callers degradam para resultados vazios em vez de quebrar. A chave
    do cache inclui o mtime do chunks.parquet, então um rebuild no
    lugar é percebido sem reiniciar o consumidor.
    """
    global _INDEX, _ROWS, _LOADED_DIR
    import numpy as np
    import pandas as pd

    out_dir = Path(out_dir)
    mani = out_dir / "chunks.parquet"
    try:
        stamp = (out_dir, mani.stat().st_mtime)
    except OSError:
        return False
    if _INDEX is not None and _LOADED_DIR == stamp:
        return True
    _ROWS = pd.read_parquet(out_dir / "chunks.parquet").to_dict("records")
    try:
        import faiss

        _INDEX = ("faiss", faiss.read_index(str(out_dir / "code_index.faiss")))
    except Exception:
        if not (out_dir / "embeddings.npy").exists():
            _INDEX = None
            return False
        _INDEX = ("numpy", np.load(out_dir / "embeddings.npy"))
    _LOADED_DIR = stamp
    return True


def search(query: str, out_dir: str | Path, k: int = 5) -> list[dict]:
    """Semantic search over the code corpus.

    English: Returns top-k chunks with path/name/score.
    pt-BR: Retorna top-k chunks com path/name/score.
    """
    import numpy as np

    if not _load(out_dir):
        return []
    q = _get_model().encode([query], normalize_embeddings=True).astype("float32")

    kind, store = _INDEX
    if kind == "faiss":
        scores, idx = store.search(q, k)
        pairs = list(zip(idx[0], scores[0]))
    else:
        sims = (store @ q[0])
        top = np.argsort(-sims)[:k]
        pairs = [(int(i), float(sims[i])) for i in top]

    return [
        {**_ROWS[i], "score": round(float(s), 4)}
        for i, s in pairs
        if 0 <= int(i) < len(_ROWS)
    ]


def index_dir() -> str:
    """Default index directory (env-overridable).

    Falls back to the repo-root `omni_code_index/` when the env var is
    absent and the directory exists there, then to /tmp (fresh build
    target). Keeps manual starts working without the start script's
    exports.
    """
    env = os.getenv("OMNI_CODE_INDEX_DIR")
    if env:
        return env
    repo_dir = Path(__file__).resolve().parents[3] / "omni_code_index"
    if (repo_dir / "chunks.parquet").exists():
        return str(repo_dir)
    return "/tmp/omni_code_index"
