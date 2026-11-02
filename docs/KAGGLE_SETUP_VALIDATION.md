# Kaggle Gemma 4 — Setup & Validation Study (omni-agent-coworker)

Study document for the competition submission. Covers environment setup, the
dual-brain GPU topology, install corrections, code vectorization, and
end-to-end validation results on the NVIDIA L4 node.

*Documento de estudo para a submissão da competition: setup do ambiente,
topologia dual-brain na GPU, correções de instalação, vetorização do código
e validação end-to-end no nó NVIDIA L4.*

## 1. Environment

| Item | Value |
|---|---|
| Working repo | `/content/omni_worker` (branch master) |
| Canonical/coupled repo | `/content/omni_node` (adapters via PYTHONPATH) |
| Python env | `/content/omni_node/.venv` — CPython 3.14.8 (`uv venv`) |
| GPU | NVIDIA L4 — 23.7 GB total, ~22.5 GB usable |
| HF token | `/root/.cache/huggingface/token` (gated `google/gemma-4-*` access OK) |

## 2. Install

```bash
uv venv /content/omni_node/.venv --python 3.14
cd /content/omni_worker
uv pip install --python /content/omni_node/.venv/bin/python -e '.[test]'
# kernel stack (symbolic body / dream_cycle / curiosity)
uv pip install --python /content/omni_node/.venv/bin/python \
    torch --index-url https://download.pytorch.org/whl/cu126
uv pip install --python /content/omni_node/.venv/bin/python \
    sentence-transformers faiss-cpu pandas pyarrow numpy \
    bitsandbytes accelerate
```

### Corrections applied during install

- `pyproject.toml`: extra `[kernel]` was missing `pandas` + `pyarrow`, which
  `store/code_index.py` requires for `chunks.parquet` — `POST /dream/cycle`
  and `GET /curiosity/explore` returned 500 with `ModuleNotFoundError`
  even under `.[kernel]`. Fixed (commit `8865afe`).
- Canonical `src/erika/erika_torch_server.py` (omni_node): added
  `--eager-attn` flag → `attn_implementation="eager"`. Without it the model
  loads under SDPA and `output_attentions` comes back `None`, leaving
  `attention_entropy_mean` null on `/erika/affect` and `/soul/state` —
  this restores the documented "eager attn patch" provenance of the brain
  substrate. Default off, additive, backward compatible.

## 3. Dual-brain topology (no CPU offload)

Both models coexist on a single L4 (22.5 GB). `bf16` does NOT fit:
E4B raw = 16 GB + 12B raw = 24 GB. Both run **bnb nf4** via
`--load-4bit` (double-quant, fp16 compute):

| Role | Model | Port | Quant | VRAM resident |
|---|---|---|---|---|
| analyst | `google/gemma-4-12B-it` | 8098 | nf4 | 7.68 GB |
| executor | `google/gemma-4-E4B-it` | 8099 | nf4 | 9.30 GB |
| **total** | | | | **16.9 GB / 22.5 GB** |

Launch (canonical server from omni_node):

```bash
export PYTHONPATH=/content/omni_node:/content/omni_node/src
.venv/bin/python src/erika/erika_torch_server.py \
    --model google/gemma-4-12B-it --load-4bit --port 8098 --device cuda --eager-attn
.venv/bin/python src/erika/erika_torch_server.py \
    --model google/gemma-4-E4B-it --load-4bit --port 8099 --device cuda --eager-attn
```

Notes:

- `AutoModelForCausalLM` maps `Gemma4ForConditionalGeneration` /
  `Gemma4UnifiedForConditionalGeneration` correctly on transformers 5.22.1.
- Sequential startup matters: concurrent loads during nf4 warmup can OOM
  (`caching_allocator_warmup` allocates ~half the fp16 footprint transiently).
- E4B is "effective 4B" — raw ~8B params (16 GB bf16), hence nf4 also for it.

## 4. Symbolic body (code vectorization, real data)

`store/code_index.py` AST-chunks the package and embeds it with
`sentence-transformers/all-MiniLM-L6-v2` (384d), persisting
`chunks.parquet` + `code_index.faiss`. Index dir is env-overridable;
repo-root `omni_code_index/` is gitignored and is the canonical local path:

```bash
OMNI_CODE_INDEX_DIR=/content/omni_worker/omni_code_index \
  python -c "from omni_coworker.store import code_index; \
             code_index.build_index('src/omni_coworker', code_index.index_dir())"
# -> {'model': 'all-MiniLM-L6-v2', 'chunks': 145, 'dim': 384, 'faiss': True}
```

Consumers: `agency.dream.dream_cycle` (samples the code corpus, asks the
analyst brain to weave an associative reflection — the agent literally
dreams over its own body) and `agency.curiosity.explore` (semantic search).
Both degrade to extractive fallback without the index or the brain.

## 5. Validation results (L4, both brains live)

| Check | Result |
|---|---|
| `pytest` | **69 passed** (suite is hermetic — no LLM needed) |
| `omni-coworker doctor` | fastapi/torch(cu126)/httpx/psutil/pydantic OK; Rust kernels `unavailable` (optional); brains `up` when servers run |
| `omni-coworker serve` | ASGI up (port 8080 taken by env `node` → used `--port 8081`) |
| `GET /soma/probe` `/soul/state` `/agency/missions` `/safety/check` `/kernel/status` `/curiosity/explore?topic=` | all HTTP 200 |
| `GET /brain/topology` | analyst+executor `ok` — `gemma-4-12B-it` / `gemma-4-E4B-it` on CUDA |
| `POST /v1/chat/completions` (8098/8099) | real generations, coherent, per-role routing |
| `GET /erika/affect` | `attention_entropy_mean` ≈ 1.83 + `hidden_norm_mean` ≈ 121–139 (eager attn ON) |
| `POST /dream/cycle` | `"source": "brain:analyst"` — real 12B dream over code fragments |
| `omni-coworker demo` | `llm: {debug, code, review} = true` — real Debug→Code→Review; reviewer correctly rejected a non-code generation (governance working) |
| `GET /soul/state` | `brain` block populated from live tensor affect (psi/sigma/epsilon) |

### Observed caveats

- `soma/probe.py` docstring mentions GPU temp/`pynvml` but GPU telemetry is
  not actually read — documented as docstring-level.
- `pytest` warns `asyncio_mode` unknown (pytest-asyncio not installed) —
  harmless; add `pytest-asyncio` to `[test]` if async tests arrive.
- `server/erika_torch_server.py` (package stub) intentionally never loads a
  model — `/v1/*` 503s by design; real serving is the canonical omni_node
  server above.

## 6. Provenance

Substrate comes from the canonical OmniMind repos for the competition:
`src/erika/erika_torch_server.py` (brain), `src.orchestration`,
`src.autopoietic`, `src.agentes`, `src.cognitive.dream_weaver` (adapters
with standalone fallbacks — see `DIRECTORY_CONTRACT.yaml`), plus
`omnimind_*` Rust crates (optional `kernel_hooks`). Models are Google's
gated `gemma-4-*-it` checkpoints on HuggingFace.
