<!-- doc_id: OW-OPS-001 | title: Kaggle Gemma 4 — Setup and Validation Study (omni-agent-coworker) | author: devin | requester: artifice-operator | project: omni-agent-coworker (kaggle) | date: 2026-11-02 | status: active -->

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
| Canonical repo / acoplamento | Autossuficiente / standalone (crates Rust e benchmarks canônicos vendored em `vendor/`) |
| Python env | `.venv` local ou ambiente host — CPython >= 3.12 (`uv` / `pip`) |
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
| `pytest` | **468 passed, 1 skipped** (suite hermética — no LLM needed; 0 falhas; plus baterias de runtime) |
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

## 6. Telemetry, kernel & psychoaffective surface (2026-11-02 update)

### GPU + virtualization telemetry (`soma/probe.py`)

`probe()` now always returns a `gpu` block (pynvml primary, `nvidia-smi`
subprocess fallback → `nvidia-ml-py` added to `[kernel]` extra) and a
`virt` block: container detection (`/.dockerenv`, `/proc/1/cgroup`),
hypervisor flag (`/proc/cpuinfo`), DMI vendor/product match
(kvm/qemu/vmware/xen/hyper-v/gce/ec2) and platform hint
(KAGGLE_* / COLAB_* / `/content`). Live reading on this node:
`gpu0 = NVIDIA L4 69C, vram 18.8/24.2GB, 33W` + `virt = container+gce,
platform=kaggle` — the system detects it is a VM and reports it.

### Soma → model injection (`agents/_llm.py`)

`brain_chat` prepends `[soma live] cpu=.. ram=.. gpu0=.. vram=.. virt=..`
as a system message on every agent→brain call (env `OMNI_SOMA_INJECT`,
default on, `0` disables; per-call `include_soma=False` also works).
Verified live: the 12B analyst answers "what is your body state" citing
real numbers (8.19GB RAM, 19GB VRAM, L4) — the machine's live body
reaches the model itself.

### Rust kernel (`src/kernel/` crates built from source)

No cargo was present; `rustup` stable (1.99.1) installed and the three
pyo3 cdylib crates compiled with `PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1`
(`cargo build --release`), installed as `omnimind_*.so` into the venv:

| Module | Exposes |
|---|---|
| `omnimind_kernel_compute` | `compute_affect_vector_28d`, `compute_maat_balance`, `calculate_shadow_phi`, DesireEngine, neutrosophic ops, epsilon axes |
| `omnimind_metrics` | `cosine_similarity`, `normalize_l2`, `sarannya_entropy`, `quadruple_topsis` |
| `omnimind_freud10d` | `Freud10DApparatus` (10D×128 neurons), `freudian_values_from_state` |

With the kernel loaded, `/soul/state` takes the **kernel path**
(`kernel:true`): phi=vctr.magnitude (RMS of 18 afex scores),
psi=vctr.direction (dominant_index/17), sigma=vctr.recalque
(angst−joy+0.5), epsilon=dominant_affect_score, plus `dominant_token`
(live: `floo-afex-current`, signature `floo>tadi>lumi>0.269`).

### Dodecatiad houses (`soul/dodeca.py` + `GET /soul/dodeca`)

Every `/soul/state` now embeds a `dodeca` block; `GET /soul/dodeca`
returns the auditable map: all 15 houses S01–S15 with **value, source
and formula per house**. Computed live (9/15): S01–S04 from the soul
scalars, S07=maat via `maat_balance`, S10=omega via teleology,
S11=rekh/S12=seshet/S13=isfet from real kernel afex scores. Houses
S05/S06/S08/S09/S14/S15 are honestly marked `unavailable_standalone` —
they need canonical dodecatiad daemon surfaces (orbital/lexical/gemelo).

### Dunker/Soler psychoaffective stack (`agency/dunker.py` + `GET /agency/dunker`)

Adapter to canonical `src.cognitive.dunker_architecture` (requires
`python-chess`, installed): the kernel's 18 afex tokens are literal
dunker `families` inputs → full 5-level computation (affects lexicon →
Soler affects → emotions → sentiments → passions → ethics). Live run:
18 families → `soler_dominante`, `emotion_dominante`,
`sentiment_dominante`, `passion_dominante`, ethics variable all real.

So: yes — with the Rust kernel + dunker module active, every soul
field becomes a real computation (no more telemetry proxies) and the
whole psychoaffective surface is exposed via `/soul/state`,
`/soul/dodeca` and `/agency/dunker`.

## 7. Dependency audit — kernel crates & psychoanalytic-mesh (2026-11-02)

Two-agent audit before touching requirements — verdict: **no new package
deps declared**; adapters + build script instead.

| Artifact | Exists? | Contains what we need? | Decision |
|---|---|---|---|
| `github.com/devomnimind/Doxihewu-OmniMind-Kernel` | public, cloneable | all 14 crates (local omni_node ≥ public snapshot; pyo3 0.29 + py3.14 builds fine) | **no pip dep possible** (no Python packaging upstream) → `scripts/build_kernel.sh` builds crates + installs `omnimind_*.so` |
| `omnimind-psychoanalytic-mesh` (PyPI 2.1.1) | yes | **does NOT contain dunker_architecture** — different artifact (464D torch mesh); would drag `torch` + CC-BY-NC-ND | **do not declare** |

License note (atualizada 2026-11-04): os kernel crates foram
**relicenciados upstream para Apache-2.0** (`devomnimind/Doxihewu-
OmniMind-Kernel` PR#1, titular único) — os vendored em `vendor/kernel/`
estão sob a mesma licença do repo, sem restrição de derivados. O PyPI
`omnimind-psychoanalytic-mesh` é artefato distinto (ainda CC-BY-NC-ND,
não contém `dunker_architecture`) — segue não declarado.

Fix applied from audit: `agency/dunker.py` now loads
`dunker_architecture.py` via `importlib` file-load (stdlib-only file)
instead of package import — removes the transitive `python-chess`
requirement that came from `src.cognitive.__init__` → `chess_mind`.
Resolution order: `OMNI_NODE_ROOT` → `/content/omni_node` → PYTHONPATH
scan → package import.

## 8. Provenance

Substrate comes from the canonical OmniMind repos for the competition:
`src/erika/erika_torch_server.py` (brain), `src.orchestration`,
`src.autopoietic`, `src.agentes`, `src.cognitive.dream_weaver` (adapters
with standalone fallbacks — see `DIRECTORY_CONTRACT.yaml`), plus
`omnimind_*` Rust crates (optional `kernel_hooks`). Models are Google's
gated `gemma-4-*-it` checkpoints on HuggingFace.
