# brain/ — proxy role-routed para os servidores Erika/Gemma externos

pt-BR: `brain` é a interface do pacote para os dois servidores LLM que
rodam **fora** do pacote (instâncias `erika_torch_server`, compatíveis
com OpenAI). `server.py` é um adapter conforme
`DIRECTORY_CONTRACT.yaml` — faz proxy HTTP, não carrega modelos.

English: `brain` is the package's interface to the two LLM "brain"
servers that run **outside** this package (`erika_torch_server`
instances, OpenAI-compatible). `server.py` is an adapter per
`DIRECTORY_CONTRACT.yaml` — it proxies HTTP, it does not load models.

## Upstream topology / Topologia upstream

| Role | Model | Default URL | Used for |
|---|---|---|---|
| `analyst` | `google/gemma-4-12B-it` | `http://127.0.0.1:8098` | decomposition, clinical reasoning, judges, dreams |
| `executor` | `google/gemma-4-E4B-it` | `http://127.0.0.1:8099` | tactical tool-calling, curiosity synthesis |

Both servers are bnb-NF4 resident on the same NVIDIA L4 (no CPU offload)
and expose `/health`, `/v1/chat/completions`, `/erika/activations`
(hidden-state summaries), `/erika/affect`, `/erika/unload` and
`/erika/reload` — the last pair is the swap surface used by
`orchestration.swap_scheduler` (canonical server only; the package stub
`server/erika_torch_server.py` does not implement them).

## Files / Arquivos

| File | Role | Key API |
|---|---|---|
| `__init__.py` | Re-exports | `create_brain_router`, `get_brain_client`, `ERIKA_HOST`, `ERIKA_PORT`, `derive_affect`, `derive_affect_from_brain`, `push`, `recent` |
| `server.py` | httpx adapter (contract: `adapter`) | `create_brain_router()` → FastAPI `APIRouter("/brain")`; `get_brain_client(role)` → cached sync `httpx.Client` or `None`; `_base_for_role(role)` routes `executor` vs anything-else |
| `affect.py` | Affect derivation | `derive_affect()` → zeroed `{phi, psi, sigma, epsilon}`; `derive_affect_from_brain()` → maps `/erika/affect` (`attention_entropy_mean`, `hidden_norm_mean`) into the 4-metric affect space |
| `activations.py` | Ring buffer | `push(record)` / `recent(limit)` over a `deque(maxlen=256)` of activation summaries |

## `create_brain_router()` endpoints

| Route | Method | Upstream |
|---|---|---|
| `/brain/health` | GET | analyst `/health` |
| `/brain/activations?limit=` | GET | analyst `/erika/activations` |
| `/brain/affect` | GET | analyst `/erika/affect` |
| `/brain/executor/health` | GET | executor `/health` |
| `/brain/topology` | GET | both roles up/down (`analyst` + `executor` bases) |
| `/brain/chat?role=` | POST | role-routed `/v1/chat/completions` |
| `/brain/unload?role=` | POST | role-routed `/erika/unload` (default `executor`) |
| `/brain/reload?role=` | POST | role-routed `/erika/reload` (default `executor`) |

Upstream failures surface as HTTP 503 on GET routes; `unload`/`reload`
return `{"role", "status": "error", "reason"}` on failure. If
`fastapi`/`httpx` are missing at build time the factory returns a
degraded router whose `/health` reports `unavailable`.

## Consumers / Consumidores

- `app.py` mounts the router; `cli.py doctor` probes `*/health`.
- `agents/_llm.py` (`brain_chat`/`brain_chat_json`) calls
  `get_brain_client(role)` → `/v1/chat/completions`; `None` on failure.
- `soma/probe.py::probe_with_brain` merges `/erika/activations` +
  `/erika/affect` into host telemetry.
- `soul/api.py::_compute_state` uses `derive_affect_from_brain()`.
- `orchestration/swap_scheduler.py` calls `/erika/unload|reload`
  directly on the executor base (`_base_for_role("executor")`).

## Env vars / Variáveis de ambiente

`ERIKA_HOST` (default `127.0.0.1`), `ERIKA_PORT` (default `8098`,
analyst), `ERIKA_EXECUTOR_PORT` (default `8099`, executor).

## Fallbacks

`get_brain_client` → `None` when `httpx` is unavailable; all callers
treat `None`/non-200 as "brain down" and degrade to extractive/local
behavior. `derive_affect_from_brain` falls back to the zeroed metrics
on any error.
