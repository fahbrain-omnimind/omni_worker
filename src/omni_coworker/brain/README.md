# brain/ — role-routed proxy to the external Erika/Gemma servers

English: `brain` is the package's interface to the two LLM "brain"
servers that run **outside** this package (`erika_torch_server`
instances, OpenAI-compatible). `server.py` is an adapter per
`DIRECTORY_CONTRACT.yaml` — it proxies HTTP, it does not load models.

pt-BR: `brain` é a interface do pacote para os dois servidores LLM que
rodam **fora** do pacote (instâncias `erika_torch_server`, compatíveis
com OpenAI). `server.py` é um adapter conforme
`DIRECTORY_CONTRACT.yaml` — faz proxy HTTP, não carrega modelos.

## Upstream topology

| Role | Model | Default URL | Used for |
|---|---|---|---|
| `analyst` | `google/gemma-4-12B-it` | `http://127.0.0.1:8098` | decomposition, clinical reasoning, judges, dreams |
| `executor` | `google/gemma-4-E4B-it` | `http://127.0.0.1:8099` | tactical tool-calling, curiosity synthesis |

Both servers expose `/health`, `/v1/chat/completions`,
`/erika/activations` (hidden-state summaries) and `/erika/affect`.

## Files

| File | Role | Key API |
|---|---|---|
| `__init__.py` | Re-exports | `create_brain_router`, `get_brain_client`, `ERIKA_HOST`, `ERIKA_PORT`, `derive_affect*`, `push`, `recent` |
| `server.py` | httpx adapter (contract: `adapter`) | `create_brain_router()` → FastAPI `APIRouter("/brain")`; `get_brain_client(role)` → cached sync `httpx.Client` or `None`; `_base_for_role(role)` routes `executor` vs anything-else |
| `affect.py` | Affect derivation | `derive_affect()` → zeroed `{phi, psi, sigma, epsilon}`; `derive_affect_from_brain()` → maps `/erika/affect` (`attention_entropy_mean`, `hidden_norm_mean`) into the 4-metric affect space |
| `activations.py` | Ring buffer | `push(record)` / `recent(limit)` over a `deque(maxlen=256)` of activation summaries |

## `create_brain_router()` endpoints

`GET /brain/health`, `GET /brain/activations?limit=`,
`GET /brain/affect`, `GET /brain/executor/health`,
`GET /brain/topology` (both roles up/down), `POST /brain/chat?role=`
(role-routed to `/v1/chat/completions`). Upstream failures surface as
HTTP 503. If `fastapi`/`httpx` are missing at build time the factory
returns a degraded router whose `/health` reports `unavailable`.

## Consumers

- `app.py` mounts the router; `cli.py doctor` probes `*/health`.
- `agents/_llm.py` (`brain_chat`/`brain_chat_json`) calls
  `get_brain_client(role)` → `/v1/chat/completions`; `None` on failure.
- `soma/probe.py::probe_with_brain` merges `/erika/activations` +
  `/erika/affect` into host telemetry.
- `soul/api.py::_compute_state` uses `derive_affect_from_brain()`.

## Env vars

`ERIKA_HOST` (default `127.0.0.1`), `ERIKA_PORT` (default `8098`,
analyst), `ERIKA_EXECUTOR_PORT` (default `8099`, executor).

## Fallbacks

`get_brain_client` → `None` when `httpx` is unavailable; all callers
treat `None`/non-200 as "brain down" and degrade to extractive/local
behavior. `derive_affect_from_brain` falls back to the zeroed metrics
on any error.
