# soma/ — interocepção do host / host interoception

pt-BR: `soma` é a camada somática do agente — telemetria real do host
(CPU/RAM/swap/load via `psutil`, GPU via pynvml/nvidia-smi, virtualização)
mais um histórico opcional em SQLite WAL dos snapshots. Apenas métricas;
sem metáfora.

English: `soma` is the agent's somatic layer — real host telemetry
(CPU/RAM/swap/load via `psutil`, GPU via pynvml/nvidia-smi,
virtualization) plus an optional SQLite WAL history of probe snapshots.
Metrics only; no metaphor.

## Files / Arquivos

| File | Role | Key API |
|---|---|---|
| `__init__.py` | Re-exports | `probe`, `probe_recorded`, `probe_with_brain`, `SomaticStore` |
| `probe.py` | Telemetry snapshot | `probe()` → `{cpu_percent, ram_used_gb, ram_total_gb, swap_used_gb, load_avg, gpu, virt}`; `soma_context_line()` → `[soma live]` one-liner; `probe_recorded(path)` → probe + `recorded: bool`; `probe_with_brain()` → probe + `brain_activations`/`brain_last_ts`/`brain_affect` |
| `somatic_store.py` | Persistence | `SomaticStore(path)` — `.record(dict) -> rowid`, `.recent(n)`, `.summary(n)` (count + per-column means) |

## Schema (`probes` table) / Esquema

`id INTEGER PK, ts TEXT (UTC ISO), cpu REAL, ram_used_gb REAL,
ram_total_gb REAL, swap_gb REAL, load1 REAL, extra_json TEXT`.
`record()` maps `cpu_percent→cpu`, `swap_used_gb→swap_gb`,
`load_avg→load1` (first element of the `os.getloadavg()` tuple);
unrecognized keys are serialized into `extra_json`. WAL mode, one
connection per write — same pattern as `store/node_db.py`.

## Design note / Nota de design

`SomaticStore` is a **clean reimplementation**, not an adapter: the
canonical `src.infrastructure.somatic_mesh_sql` (omni_node) is
entangled with production paths (`data/monitor`, Rust engine, parquet
dual-writer), so it is deliberately not reused here.

## Consumers / Consumidores

- `app.py` — `GET /soma/probe` → `probe_recorded()` (persists each call
  to `data/somatic_probes.sqlite`);
  `GET /agency/missions` → `probe()` feeds teleology (`cpu_high` flag).
- `soul/api.py::_compute_state` — `probe()` feeds the phi/psi/sigma
  fallback derivation (`ram_ratio`, `cpu`, `load`).
- `cli.py missions` — `probe()` for the same teleology payload.

## Dependencies & fallbacks / Dependências e fallbacks

- `psutil` (required, core dep); `pynvml`/`nvidia-ml-py` optional for
  real GPU telemetry (temp/util/VRAM/power — `nvidia-smi` subprocess
  fallback). `virt` block always present: container (dockerenv/cgroup),
  hypervisor flag, DMI vendor match, platform
  (`kaggle`/`colab`/`colab-family`/`cloud-vm`/`container`/`metal`).
  `soma_context_line()` renders the compact `[soma live]` string injected
  into brain chats. `os.getloadavg` is guarded
  (`None` on non-POSIX).
- `probe_recorded` returns `recorded=False` if SQLite write fails.
- `probe_with_brain` uses `brain.server.get_brain_client()`
  (analyst role); all brain errors are swallowed — soma works with the
  brain down.
- Default DB path: `data/somatic_probes.sqlite` (cwd-relative,
  overridable via `SomaticStore(path)` / `probe_recorded(path)`).
