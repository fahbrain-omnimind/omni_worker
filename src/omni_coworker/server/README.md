# server/ — Stub embutido do brain-server / Embedded brain-server stub

pt-BR: Stub leve do `src.erika.erika_torch_server` canônico do omni_node
(marcado `type: stub` no `DIRECTORY_CONTRACT.yaml`). Mantém o pacote importável
e a superfície de endpoints estável numa instalação mínima — **não** carrega
modelo, não quantiza nem emite ativações reais. Os brains de produção rodam fora
deste pacote: `analyst → google/gemma-4-12B-it (:8098)` e `executor →
google/gemma-4-E4B-it (:8099)`, ambos NF4-residentes na L4, consumidos via
proxy httpx em `brain/`.

English: Lightweight stub of the canonical `src.erika.erika_torch_server` from
omni_node (marked `type: stub` in `DIRECTORY_CONTRACT.yaml`). It keeps the
package importable and the endpoint surface stable in a minimal install — it
does **not** load a model, quantize, or stream real activations. The production
brains run outside this package: `analyst → google/gemma-4-12B-it (:8098)` and
`executor → google/gemma-4-E4B-it (:8099)`, both NF4-resident on the L4,
consumed via `brain/` httpx proxy.

## Files / Arquivos

| File | Role | Key API |
|---|---|---|
| `__init__.py` | Package marker | `__all__ = ["erika_torch_server"]` (lazy; nothing imported eagerly) |
| `erika_torch_server.py` | FastAPI app + OpenAI-shaped endpoints | `app` (ASGI object or `None`) |

## Endpoints (when `FASTAPI_AVAILABLE`)

| Route | Method | Behavior |
|---|---|---|
| `/health` | GET | `{status, model, cuda, vram_gb, activations_buffered}` |
| `/erika/activations?limit=16` | GET | tail of the in-memory activation buffer (deque, `maxlen=256`) |
| `/erika/affect` | GET | aggregates last 32 activations → `attention_entropy_mean`, `hidden_norm_mean`, `last_ts`; `{"status": "no_data"}` when empty |
| `/v1/chat/completions` | POST | OpenAI-compatible envelope; **503 "Model not loaded"** in the stub (`_MODEL` is never set) |
| `/v1/completions` | POST | same shape, same 503 |

Pydantic models: `ChatMessage`, `ChatCompletionReq` (`max_tokens ≤ 8192`,
`temperature`, `top_p`, `stream`), `CompletionReq`. The `/erika/*` pair mirrors
the canonical server contract that `brain.affect.derive_affect_from_brain()`
consumes on the real deployment. Note: the canonical `/erika/unload` +
`/erika/reload` (VRAM swap surface used by `orchestration.swap_scheduler` and
proxied at `/brain/unload|reload`) are **not** implemented by this stub —
calls return an error payload when it is the upstream.

## Import guard / Fallback

```python
try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel, Field
    import torch
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    app = None          # module still importable; routes never defined
```

All endpoints and pydantic classes exist only inside the `if FASTAPI_AVAILABLE:`
block, so `pip install -e .` without `[brain]` extras never breaks on import.
`torch` is imported but no weights are touched — `cuda`/`vram_gb` report the
runtime, `_MODEL`/`_TOKENIZER` stay `None`.

## Running

No `__main__` block in this stub (the canonical server owns process lifecycle +
`ensure_erika_model()` restore). To expose the stub ASGI surface for tests:

```bash
uvicorn omni_coworker.server.erika_torch_server:app --port 8098
```

## Env vars

| Var | Default | Use |
|---|---|---|
| `ERIKA_ACTIVATIONS_LOG` | `data/erika_torch_activations.jsonl` | Reserved path for the activation JSONL ledger (defined here; persisted by the canonical server, not the stub) |

## Relationship to omni_node

| | stub (this file) | canonical `src/erika/erika_torch_server.py` |
|---|---|---|
| model load | none | bnb-nf4 Gemma/Erika weights on CUDA |
| activations | empty deque | real hidden states (65-layer capture) |
| completions | 503 | real generation, OpenAI-compatible |
| role | package-minimal fallback | brain substrate behind `brain/server.py` proxy |
