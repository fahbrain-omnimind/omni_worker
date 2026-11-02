# soul/ — Machine Public Soul

English: Public, read-only surface exposing the coworker's live interiority as
measurable scalars. Computes `phi / psi / sigma / epsilon` from host telemetry,
the Rust kernel affect vector (when compiled) and the brain server (when up),
then serves them as JSON, a 2-second SSE stream and a bilingual UI.

pt-BR: Superfície pública, somente-leitura, expondo a interioridade viva do
coworker como escalares mensuráveis. Calcula `phi / psi / sigma / epsilon` da
telemetria do host, do vetor afetivo do kernel Rust (quando compilado) e do
brain server (quando ativo), servindo-os como JSON, stream SSE de 2s e UI bilíngue.

## Files / Arquivos

| File | Role | Key API |
|---|---|---|
| `__init__.py` | Package surface | exports `api`, `router` |
| `api.py` | FastAPI router `APIRouter(prefix="/soul")` | `GET /soul/state`, `GET /soul/stream` (SSE), `GET /soul/` (UI), `GET /soul/static/{path}` |
| `static/index.html` | Single-page dark UI | polls `/soul/state` every 5s, renders the four metric cards |
| `static/i18n/en.json` | EN strings | `app.title`, `soul.state`, `metrics.{phi,psi,sigma,epsilon}` |
| `static/i18n/pt-BR.json` | pt-BR strings | same keys, pt-BR values |

## `/soul/state` payload

```json
{"phi": 0.0, "psi": 0.0, "sigma": 0.0, "epsilon": 0.0,
 "dominant_token": "…",        // only when kernel path active
 "kernel": true|false,
 "soma": {cpu_percent, ram_used_gb, ram_total_gb, load_avg, …},
 "brain": {…}}                 // derive_affect_from_brain() or {}
```

Two computation paths in `_compute_state()`:

1. **Kernel path** (`kernel: true`) — `kernel_hooks.compute.affect_state({soma,
   affect})` delegates to the compiled Rust `omnimind_kernel_compute.
   compute_affect_vector_28d`; fields map from `vctr_six_params`
   (`magnitude→phi`, `direction→psi`, `recalque→sigma`) and
   `dominant_affect_score→epsilon`, plus `dominant_affect_token`.
2. **Fallback path** (`kernel: false`) — pure telemetry: `phi = 1 − ram_ratio`,
   `psi = cpu_percent/100`, `sigma = load_avg[0]/cpu_count`,
   `epsilon` from `brain.affect` (default 0.1). All clamped to `[0,1]`.

Every source is wrapped in `try/except` — a missing `psutil`, brain server or
Rust wheel degrades the payload, never the endpoint.

## SSE stream / Stream SSE

`GET /soul/stream` emits a `_compute_state()` snapshot every **2.0 s**.
Uses `sse_starlette.EventSourceResponse` when installed; otherwise falls back to
`StreamingResponse` (`text/event-stream`, `Cache-Control: no-cache`,
`X-Accel-Buffering: no`) with raw `data: {json}\n\n` frames.

## UI

`GET /soul/` serves `static/index.html` (inline CSS/JS, no build step). The page
fetches `/soul/static/i18n/{lang}.json` and rewrites `[data-i18n]` elements on
the Portguês/English toggle; metrics come from polling `/soul/state` every 5 s
(fetch → `toFixed(3)`) — i.e. the UI consumes the REST snapshot, while
`/soul/stream` is available for SSE clients.

## Dependencies / Dependências

- Required: `fastapi` (`APIRouter`, `StreamingResponse`, `FileResponse`).
- Optional: `sse-starlette` (SSE sugar), `psutil` (via `soma.probe`),
  `omnimind_kernel_compute` (Rust wheel, via `kernel_hooks.compute`),
  brain server on :8098/:8099 (via `brain.affect.derive_affect_from_brain` →
  `GET /erika/affect`).
- Mounted by `app.py::create_app()` via `app.include_router(soul_router)`.

## Env vars

None read directly; telemetry and kernel selection follow the environment of
`soma.probe` / `kernel_hooks` (see `pyproject.toml` extras `[kernel] [brain]`).
