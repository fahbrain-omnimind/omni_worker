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
import re
from pathlib import Path

_SECRET_PATTERNS = [
    re.compile(r"(ghp|gho|ghu|ghs|github_pat)_[A-Za-z0-9_]{20,}"),
    re.compile(r"glpat-[A-Za-z0-9_\-]{16,}"),
    re.compile(r"hf_[A-Za-z0-9]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
    re.compile(r"-----BEGIN (RSA|OPENSSH|EC|PRIVATE) KEY-----"),
    re.compile(r"HF_TOKEN\s*[=:]\s*\S+"),
    re.compile(
        r"(api[_-]?key|secret|password|token)\s*[=:]\s*[\"'][A-Za-z0-9_\-]{12,}[\"']",
        re.I,
    ),
    re.compile(r"AKIA[0-9A-Z]{16}"),
]

_CONCEPT_KEYWORDS = {
    "dodecatiad": ("dodecatíade", "dodecatiad", "d12", "poincaré", "mobius"),
    "quadrupla_federativa": ("phi", "psi", "sigma", "epsilon", "borromean", "quádrupla"),
    "markov_blanket": ("markov blanket", "blanket", "fep", "free energy", "pyphi"),
    "memtrias_recalcado": ("memtrias", "recalcado", "provenance", "minja", "acervo"),
    "affect_care": ("affect_tracer", "flattery", "passion", "care", "cvv", "caps"),
    "mps_spectral": ("mps", "ipr", "eff_rank", "spectral", "bond_dim", "entanglement"),
    "dual_brain_swap": ("analyst", "executor", "peer-swap", "unload", "reload", "vram"),
    "governance_witness": ("witness", "constitutional", "circuit_breaker", "quarantine", "scar"),
}


def sanitize_secret_text(text: str) -> tuple[str, int]:
    """Redact any secret-like token before indexing or embedding.

    English: Returns (sanitized_text, redaction_count).
    pt-BR: Retorna (texto_sanitizado, contagem_de_redações).
    """
    if not text:
        return "", 0
    redactions = 0
    out = text
    for pat in _SECRET_PATTERNS:
        out, n = pat.subn("<REDACTED_SECRET>", out)
        redactions += n
    return out, redactions

_MODEL = None
_INDEX = None
_ROWS: list[dict] = []

MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"


def _get_model():
    """Lazy sentence-transformers model singleton (defaults to CPU to preserve GPU VRAM for brains)."""
    global _MODEL
    if _MODEL is None:
        from sentence_transformers import SentenceTransformer

        _MODEL = SentenceTransformer(MODEL_ID, device=os.getenv("OMNI_EMBED_DEVICE", "cpu"))
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
        clean_doc, _ = sanitize_secret_text(doc[:1200])
        chunks.append({"path": rel, "kind": "module", "name": path.stem, "text": clean_doc})
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            seg = ast.get_docstring(node) or ""
            header, _ = sanitize_secret_text(f"{type(node).__name__} {node.name}: {seg}"[:1200])
            chunks.append({
                "path": rel, "kind": type(node).__name__.lower(),
                "name": node.name, "text": header,
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


def build_symbolic_hypergraph(
    root: str | Path,
    out_path: str | Path | None = None,
) -> dict:
    """Build a sanitary symbolic hypergraph of the repository codebase.

    English: Extracts modules, classes, functions, internal imports,
    SQLite tables, FastAPI routes, and theoretical concepts into multi-way
    hyperedges so the system can traverse its own symbolic architecture.
    All strings pass through `sanitize_secret_text`.
    pt-BR: Extrai módulos, classes, funções, imports internos, tabelas
    SQLite, rotas FastAPI e conceitos teóricos em hiperarestas para que o
    sistema navegue topologicamente seu próprio corpo simbólico.
    """
    root = Path(root).resolve()
    if out_path is None:
        # Resolve the state dir from env to an absolute path before joining.
        # This closes CodeQL CWE-22: uncontrolled data used in path expression —
        # the env var is resolved and the final path is kept as a concrete
        # absolute path rather than an unvalidated concatenation.
        _state_dir = Path(os.getenv("OMNI_STATE_DIR", "data")).resolve()
        out_path = _state_dir / "symbolic_hypergraph.json"
    out_path = Path(out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    nodes: dict[str, dict] = {}
    hyperedges: list[dict] = []
    redactions_total = 0

    for py in sorted(root.rglob("*.py")):
        if "__pycache__" in py.parts:
            continue
        rel = str(py.relative_to(root))
        try:
            raw_src = py.read_text(encoding="utf-8", errors="replace")
            src, n_red = sanitize_secret_text(raw_src)
            redactions_total += n_red
            tree = ast.parse(src)
        except Exception:
            continue

        mod_id = f"mod:{rel}"
        subpkg = rel.split("/")[0] if "/" in rel else "root"
        doc = (ast.get_docstring(tree) or "").strip()
        doc_short, _ = sanitize_secret_text(" ".join(doc.split())[:240])
        nodes[mod_id] = {
            "id": mod_id,
            "kind": "module",
            "subpackage": subpkg,
            "path": rel,
            "summary": doc_short,
        }

        defs: list[str] = []
        imports: list[str] = []
        routes: list[str] = []
        tables: list[str] = []
        concepts: list[str] = []

        lower_src = src.lower()
        for cname, kw_tuple in _CONCEPT_KEYWORDS.items():
            if any(kw in lower_src for kw in kw_tuple):
                cid = f"concept:{cname}"
                nodes.setdefault(cid, {"id": cid, "kind": "concept", "name": cname})
                concepts.append(cid)

        for tbl_match in re.findall(r"CREATE TABLE IF NOT EXISTS\s+([a-zA-Z0-9_]+)", src, re.I):
            tid = f"table:{tbl_match}"
            nodes.setdefault(tid, {"id": tid, "kind": "sqlite_table", "name": tbl_match})
            if tid not in tables:
                tables.append(tid)

        for route_match in re.findall(r'@\w+\.(?:get|post|put|delete)\(\s*["\']([^"\']+)["\']', src):
            rid = f"route:{route_match}"
            nodes.setdefault(rid, {"id": rid, "kind": "endpoint", "path": route_match})
            if rid not in routes:
                routes.append(rid)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                kind = "class" if isinstance(node, ast.ClassDef) else "function"
                did = f"{kind}:{rel}:{node.name}"
                if len(defs) < 25:
                    defs.append(did)
                    nodes.setdefault(did, {"id": did, "kind": kind, "name": node.name, "module": rel})
            elif isinstance(node, ast.ImportFrom) and node.module:
                if "omni_coworker" in node.module or (node.level and node.level > 0):
                    imp = f"import:{node.module}"
                    if imp not in imports:
                        imports.append(imp)

        members = [mod_id, *defs[:12], *imports[:8], *tables, *routes, *concepts]
        if len(members) > 1:
            hyperedges.append(
                {
                    "id": f"he:{rel}",
                    "subpackage": subpkg,
                    "module": rel,
                    "members": members,
                    "concepts": [c.removeprefix("concept:") for c in concepts],
                    "tables": [t.removeprefix("table:") for t in tables],
                    "routes": [r.removeprefix("route:") for r in routes],
                    "summary": doc_short,
                }
            )

    graph = {
        "version": "1.0",
        "node_count": len(nodes),
        "hyperedge_count": len(hyperedges),
        "redactions_total": redactions_total,
        "concepts": sorted(
            [n["name"] for n in nodes.values() if n.get("kind") == "concept"]
        ),
        "tables": sorted(
            [n["name"] for n in nodes.values() if n.get("kind") == "sqlite_table"]
        ),
        "routes": sorted(
            [n["path"] for n in nodes.values() if n.get("kind") == "endpoint"]
        ),
        "hyperedges": hyperedges,
    }
    out_path.write_text(json.dumps(graph, indent=2, ensure_ascii=False), encoding="utf-8")
    return graph


def search_hypergraph(
    query: str,
    hypergraph_path: str | Path | None = None,
    k: int = 4,
) -> list[dict]:
    """Retrieve the top-k symbolic hyperedges matching a task or difficulty query."""
    if hypergraph_path is None:
        hypergraph_path = Path(os.getenv("OMNI_STATE_DIR", "data")) / "symbolic_hypergraph.json"
    p = Path(hypergraph_path)
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []
    tokens = [
        t.lower()
        for t in re.split(r"[^a-zA-Z0-9_À-ÿ]+", query or "")
        if len(t) >= 3
    ]
    if not tokens:
        return data.get("hyperedges", [])[:k]
    scored: list[tuple[float, dict]] = []
    for he in data.get("hyperedges", []):
        blob = (
            f"{he.get('module', '')} {he.get('subpackage', '')} "
            f"{' '.join(he.get('members', []))} {he.get('summary', '')}"
        ).lower()
        score = sum(2.0 if tok in he.get("module", "").lower() else 1.0 for tok in tokens if tok in blob)
        if score > 0:
            scored.append((score, he))
    scored.sort(key=lambda x: -x[0])
    return [he for _, he in scored[:k]]
