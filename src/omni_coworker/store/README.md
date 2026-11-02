# store/ — SQLite node DB + "corpo simbólico" vetorizado

pt-BR: `store` reúne as camadas de persistência: `node_db`
(missões + artefatos, SQLite WAL), `code_index` (índice do próprio
código do pacote fatiado via AST, vetorizado e persistido em
faiss/parquet — o "corpo simbólico" que o agente estuda e sonha),
`state_guard` (snapshots tar.gz com retenção p/ continuidade da VM) e
`audit_adapter` (ponte p/ o ImmutableAuditSystem canônico com fallback
na hash-chain witness local).

English: `store` holds the persistence layers: `node_db` (missions
+ artifacts, SQLite WAL), `code_index` (AST-chunked, embedded and
faiss/parquet-persisted index of this package's own source — the
"symbolic body" the agent studies and dreams over), `state_guard`
(retained tar.gz snapshots for VM continuity) and `audit_adapter`
(bridge to the canonical ImmutableAuditSystem with fallback to the
local witness hash-chain).

## Files / Arquivos

| File | Role | Key API |
|---|---|---|
| `__init__.py` | Re-exports | `node_db`, `NodeDB` |
| `node_db.py` | SQLite WAL node store | `NodeDB(path)` — `.init()`, `.add_mission/get_mission/list_missions`, `.add_artifact/list_artifacts` |
| `code_index.py` | Vectorized code index | `build_index(root, out_dir)`, `search(query, out_dir, k=5)`, `index_dir()`; lazy `_get_model()` singleton |
| `state_guard.py` | Snapshot/restore manager (runnable as `__main__`) | `snapshot(force)` → `{created, skipped, path, kept}`; `restore(path)`; `loop(interval_hours=6.0, once)`; CLI `--once`, `--interval-hours`, `--restore PATH` |
| `audit_adapter.py` | Canonical audit bridge | `audit_append(event_type, data)` → `{"source", "appended"}`; `audit_verify()` — canonical `src.audit.immutable_audit` when mounted, else `agency.witness` fallback |

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

## state_guard — continuity snapshots

Anchored at `OMNI_STATE_DIR` (default `data/`): `snapshot()` tars the
state dir into `state_snapshots/state_<ts>.tar.gz` (with a
`manifest.json` carrying a content hash), skips when nothing changed,
hash-verifies the newest snapshot before pruning, and keeps at most
`N_SNAPSHOTS=3` — never pruning the last valid chain head.
`restore(path)` extracts with tarfile `filter="data"`. As `__main__`
it runs a periodic loop (`--interval-hours`, default 6h) — the
continuity daemon of the Runtime table (root README).

## audit_adapter — audit bridge

`audit_append(event_type, data)` tries the canonical
`ImmutableAuditSystem` (`/content/omni_node` or
`/content/omnimind-kilombo-sovereign` → `src/audit/immutable_audit.py`,
sha256 chain + fcntl lock) and falls back to
`agency.witness.witness_event(f"audit.{type}")` on the local JSONL —
returns `{"source": "canonical:immutable_audit" | "witness_fallback" |
None, "appended": bool}`. `audit_verify()` verifies the local witness
chain (`verify_witness("data/witness.jsonl")`) — the canonical chain
verification is not wired yet.

## Consumers / Consumidores

- `agency/dream.py::dream_cycle` — samples chunks, asks the analyst
  brain to weave an associative "dream"; extractive fallback.
- `agency/curiosity.py::explore` — topic → top-k fragments + executor
  brain synthesis of gaps/suggestions.
- `app.py` — `POST /dream/cycle`, `GET /curiosity/explore`.
- `orchestration/agent_orchestrator.py` — `NodeDB` artifacts.
- Runtime loops — `python -m omni_coworker.store.state_guard` (6h).

## Dependencies & env / Dependências e env

- Required for build/search: `numpy`, `pandas` + `pyarrow` (parquet),
  `sentence-transformers`.
- Optional: `faiss-cpu` (else `embeddings.npy` + NumPy search).
- All vector deps ship in the `[kernel]` extra
  (`pip install -e .[kernel]`).
- `OMNI_CODE_INDEX_DIR` — overrides `index_dir()` default
  (`/tmp/omni_code_index`). Built artifacts are gitignored
  (`/omni_code_index/`).
- `OMNI_STATE_DIR` — state root for `state_guard` (default `data/`).
