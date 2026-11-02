# store/ — SQLite node DB + vectorized "symbolic body"

English: `store` holds the two persistence layers: `node_db` (missions
+ artifacts, SQLite WAL) and `code_index` (AST-chunked, embedded and
faiss/parquet-persisted index of this package's own source — the
"symbolic body" the agent studies and dreams over).

pt-BR: `store` reúne as duas camadas de persistência: `node_db`
(missões + artefatos, SQLite WAL) e `code_index` (índice do próprio
código do pacote fatiado via AST, vetorizado e persistido em
faiss/parquet — o "corpo simbólico" que o agente estuda e sonha).

## Files

| File | Role | Key API |
|---|---|---|
| `__init__.py` | Re-exports | `node_db`, `NodeDB` |
| `node_db.py` | SQLite WAL node store | `NodeDB(path)` — `.init()`, `.add_mission/get_mission/list_missions`, `.add_artifact/list_artifacts` |
| `code_index.py` | Vectorized code index | `build_index(root, out_dir)`, `search(query, out_dir, k=5)`, `index_dir()`; lazy `_get_model()` singleton |

## node_db — schema

- `missions(id INTEGER PK, spec TEXT)`
- `artifacts(id INTEGER PK, task_id TEXT, kind TEXT, content TEXT,
  verdict TEXT, ts TEXT)`

WAL mode (`PRAGMA journal_mode=WAL`), one connection per write.
Default path `data/node.db`; `orchestration/agent_orchestrator.py`
opens a lazy `NodeDB` at `<base_dir>/node.db` for artifact persistence.

## code_index — the symbolic body

Pipeline: `rglob("*.py")` → `_chunk_file` splits each file via `ast`
(module docstring + one chunk per top-level `def`/`class`, text
truncated at 1200 chars) → embeds with `sentence-transformers/
all-MiniLM-L6-v2` (`normalize_embeddings=True`, float32) → persists:

- `chunks.parquet` — path/kind/name/text per chunk (pandas + pyarrow)
- `code_index.faiss` — `IndexFlatIP` (inner product = cosine on
  normalized vectors) **or** `embeddings.npy` when faiss is missing
- `manifest.json` — `{model, chunks, dim, faiss}`

`search()` loads lazily into module globals (`_INDEX`, `_ROWS`), then
queries faiss or falls back to a NumPy dot-product + `argsort`
top-k — identical ranking semantics either way.

## Consumers

- `agency/dream.py::dream_cycle` — samples chunks, asks the analyst
  brain to weave an associative "dream"; extractive fallback.
- `agency/curiosity.py::explore` — topic → top-k fragments + executor
  brain synthesis of gaps/suggestions.
- `app.py` — `POST /dream/cycle`, `GET /curiosity/explore`.

## Dependencies & env

- Required for build/search: `numpy`, `pandas` + `pyarrow` (parquet),
  `sentence-transformers`.
- Optional: `faiss-cpu` (else `embeddings.npy` + NumPy search).
- All vector deps ship in the `[kernel]` extra
  (`pip install -e .[kernel]`).
- `OMNI_CODE_INDEX_DIR` — overrides `index_dir()` default
  (`/tmp/omni_code_index`). Built artifacts are gitignored
  (`/omni_code_index/`).
