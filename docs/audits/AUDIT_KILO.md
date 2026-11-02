<!-- doc_id: OW-AUD-002 | title: Audit Kilo — omni-agent-coworker (/content/omni_worker) | author: kilo | requester: artifice-operator | project: omni-agent-coworker (kaggle) | date: 2026-11-02 | status: active -->

# AUDIT KILO — omni-agent-coworker (`/content/omni_worker`)

**Auditor:** Kilo · **Date:** 2026-11-02 · **Repo:** `/content/omni_worker` (branch `master`, HEAD `3ee0e77`)
**Scope / Fatia:** `src/omni_coworker/brain/`, `soma/`, `store/`, `soul/`, `server/`, `app.py`, `cli.py` + `tests/`

> EN: Section 1 audits real implementation vs stubs, test coverage, README accuracy,
> and proposes concrete loop-closures for persistence / session continuity / VM-recycle
> integrity. Section 2 maps 2025–2026 research (agent interoceptive telemetry,
> activation→affect probing, thinking-leakage detection) onto this codebase.
> pt-BR: Seção 1 audita implementação real vs stubs, cobertura de testes, acurácia
> dos READMEs e propõe fechamentos de loop para persistência / continuidade de
> sessão / integridade entre recycles de VM. Seção 2 mapeia pesquisa 2025–2026
> (telemetria interoceptiva de agentes, probing ativação→afeto, detecção de
> thinking-leakage) sobre este codebase.

**Test baseline:** `pytest tests` → **75 passed, 0 failed** (70s, `/content/omni_node/.venv`, CPython 3.14.8). One warning: `asyncio_mode` config set in `pyproject.toml:35` but `pytest-asyncio` not installed.

---

## 1. AUDITORIA

### 1.1 Real implementation vs stub — per module / por módulo

| File | Lines | Verdict | Evidence |
|---|---|---|---|
| `brain/server.py` | 140 | **REAL** (contract `type: adapter`) | `create_brain_router()` (:33-117) — 6 endpoints (`/brain/health`, `/activations`, `/affect`, `/chat`, `/executor/health`, `/topology`), role-routed httpx proxy, degraded fallback router when fastapi/httpx missing (:110-117). `get_brain_client()` (:123-140) — per-role cached sync `httpx.Client`, timeout 300s. |
| `brain/affect.py` | 51 | **MIXED** | `derive_affect()` (:12-23) is a **zero-returning stub** — accepts `hidden_states`/`attentions` and ignores both. `derive_affect_from_brain()` (:26-51) is real code but **uncalibrated and saturating** — see §1.4. |
| `brain/activations.py` | 29 | **DEAD CODE** (effectively stub) | `push()` (:14) / `recent()` (:23) over `deque(maxlen=256)` (:11) — **never called anywhere in `src/`** (grep-verified). Only re-exported via `brain/__init__.py:12`. Duplicates the upstream server's own deque without being fed by it. |
| `soma/probe.py` | 262 | **REAL** | `probe()` (:165-184) → psutil cpu/ram/swap/load. `_gpu_probe()` (:17-94) → pynvml first, `nvidia-smi` CSV subprocess fallback — genuine dual path. `_virt_probe()` (:97-162) → container/hypervisor/DMI/platform detection (kaggle/colab aware). `soma_context_line()` (:187-218) → live `[soma live]` injection consumed by `agents/_llm.py:16-38`. `probe_recorded()` (:221-237), `probe_with_brain()` (:240-262) real — **but `probe_recorded` has no production caller** (§1.6). |
| `soma/somatic_store.py` | 170 | **REAL, clean** | `SomaticStore` (:64-171) — WAL, one connection per write, schema `probes(id,ts,cpu,ram_*,swap_gb,load1,extra_json)` (:29-39), `record/recent/summary`. Deliberate clean-room vs canonical `somatic_mesh_sql` (docstring :6-13) — sound decision. |
| `store/node_db.py` | 121 | **REAL, half-wired** | WAL store, tables `missions` + `artifacts` (:30-45). `add_artifact` used once in production (`orchestration/agent_orchestrator.py:275`, inside silent `try/except`). `add_mission/get_mission/list_missions/list_artifacts` have **zero production callers** — missions table is dead schema at runtime. |
| `store/code_index.py` | 158 | **REAL, with gaps** | AST chunker (:39-62), `build_index` (:65-108) verified live (145 chunks, 384d, faiss — `omni_code_index/manifest.json`). Gaps: no CLI/API build entry (manual only); `search()` → unhandled `FileNotFoundError` when index missing (verified, §1.4); `_load` (:111-126) caches `_INDEX/_ROWS` globally and ignores `out_dir` → stale results after rebuild or dir switch. |
| `soul/api.py` | 185 | **REAL** | `_compute_state()` (:16-82) — kernel path (Rust `vctr_six_params` → phi/psi/sigma/epsilon :48-58) with telemetry fallback (:60-71); `/soul/state` :85, `/soul/dodeca` :95, `/soul/stream` SSE 2s :120-153 (sse-starlette → StreamingResponse fallback), static UI :162-185. Minor: sync httpx/psutil calls inside the async SSE generator block the event loop per tick; `/soul/dodeca` recomputes `affect_state` a second time (:109-111). |
| `soul/dodeca.py` | 169 | **REAL, honest** | S01–S15 houses with per-house `{value, source, formula}` (:91-141); unavailable axes truthfully report `unavailable_standalone`; `active_face` = strongest computable house (:143-149). Stale comment at :25 claims 3-tuples; `_HOUSES` holds 2-tuples. `explain()` (:161-169) triggers `generate_missions` as a side effect via S10. |
| `server/erika_torch_server.py` | 117 | **STUB — intentional, contract-faithful** | Declared `type: stub` in `DIRECTORY_CONTRACT.yaml:33-35`. Import-guarded (:17-26); `/health`, `/erika/activations`, `/erika/affect` functional over an empty deque; `/v1/*` → 503 by design (`_MODEL` never set). `ACTIVATIONS_LOG` (:33) defined but never written (documented "reserved"). Correct as a minimal-install surface. |
| `app.py` | 89 | **REAL** | `create_app()` (:15-89) — mounts soul + brain routers + 7 inline routes. `/soma/probe` (:32-36) calls `probe_with_brain()` — **not** `probe_recorded()` → probes are never persisted by the running app (§1.6). |
| `cli.py` | 199 | **REAL** | 5 subcommands: `serve` :14, `doctor` :31 (always exits 0, reports analyst/executor), `demo` :82, `soul-export` :120, `missions` :138. Missing lifecycle commands for the stores (§1.6). |

### 1.2 Verified defects / Defeitos verificados (reproduced, not inferred)

**D1 — `derive_affect_from_brain` saturates under real upstream values**
`brain/affect.py:45-49`. Reproduced with the values documented in
`docs/KAGGLE_SETUP_VALIDATION.md` (`attention_entropy_mean ≈ 1.83`,
`hidden_norm_mean ≈ 121–139`):

```
upstream {attention_entropy_mean: 1.83, hidden_norm_mean: 130.0}
→ derive_affect_from_brain() = {phi: 0.0, psi: 1.0, sigma: 1.0, epsilon: 0.1}
```

3 of 4 metrics pegged at the rail. Root causes: (a) entropy ≈1.83 nats is raw —
`phi = 1 − ent` clamps to 0 and `psi = ent` clamps to 1; (b) `sigma = norm/2`
with hidden norms ~120–140 → 60+ → clamps to 1; (c) `epsilon = 0.1` hardcoded
(:48). The brain-affect surface is effectively a **constant vector** in
production. Secondary quirk: `(norm or 1.0)` at :47 maps a real `0.0` norm to
0.5 instead of 0. Also: when the upstream returns `{"status": "no_data"}`
(the stub server on an empty deque), the function returns
`{0,0,0,0.1}` — distinguishable from "server down" (`{0,0,0,0}`) only by the
epsilon constant; the `no_data` status is swallowed rather than propagated.

**D2 — `code_index.search` crashes when the index is missing**
`store/code_index.py:111-126` → `pd.read_parquet(out_dir/"chunks.parquet")` →
`FileNotFoundError` propagates uncaught through `agency/dream.py:76` and
`agency/curiosity.py:32` → `POST /dream/cycle` / `GET /curiosity/explore`
return HTTP 500. Verified empirically. This **contradicts**
`docs/KAGGLE_SETUP_VALIDATION.md` §4, which claims "Both degrade to extractive
fallback without the index" — the fallback covers brain-down, not index-missing.

**D3 — Module-global cache in `code_index._load` ignores `out_dir`**
`_INDEX`/`_ROWS` are loaded once and never re-checked: searching a second
`out_dir` returns the first dir's rows; rebuilding the index mid-process is
invisible until restart (no mtime/manifest check).

**D4 — Persistence loop is open at runtime**
`/soma/probe` → `probe_with_brain()` (app.py:35) — reads telemetry, never
writes. `probe_recorded()` exists but is invoked only by tests. Nothing calls
`brain.activations.push()`. `NodeDB` missions API is unused. Net effect:
the three persistence surfaces (somatic_probes.sqlite, node.db missions,
activations ring) are write-capable but **idle in production**.

**D5 — cwd-relative state paths**
`data/somatic_probes.sqlite` (somatic_store.py:73, probe.py:233),
`data/node.db` (node_db.py:20), `data/erika_torch_activations.jsonl`
(erika_torch_server.py:33) — all resolve against the process CWD; uvicorn from
a different directory silently forks the state. No `OMNI_DATA_DIR` equivalent
exists (`OMNI_CODE_INDEX_DIR` is the only env-anchored path).

### 1.3 Test coverage — per file / por arquivo (75 tests, `tests/`)

| File | Tests touching it | Est. functional coverage |
|---|---|---|
| `cli.py` | 8 (`test_cli_and_loop.py`: serve/doctor×/demo×2/soul-export×2/missions/help) | **~85%** — all subcommands exercised with mocked uvicorn/LLM |
| `soma/probe.py` | 5 (`test_smoke`, `test_adapters`, `test_telemetry_dodeca` ×3, `test_importables.test_probe_recorded`) | **~60%** — keys, virt block, context line, `OMNI_SOMA_INJECT` env, recorded path; **untested:** `_gpu_probe` (pynvml + nvidia-smi branches), `probe_with_brain` |
| `soma/somatic_store.py` | 3 (`test_importables`) | **~85%** — record/recent/summary/empty/extra_json round-trip |
| `soul/dodeca.py` | 2 (`test_telemetry_dodeca` ×2) | **~70%** — 15 houses, kernel afex families, active_face; untested: S10 omega path, `explain()` |
| `store/node_db.py` | 3 (`test_smoke`, `test_adapters` ×2) | **~50%** — missions CRUD; **untested:** artifacts table (the only production-used one) |
| `brain/affect.py` | 2 (`test_smoke`, `test_adapters`) | **~30%** — zero-stub only; **`derive_affect_from_brain` untested** — D1 would have been caught by a fake-response test |
| `app.py` | 1 (`test_app_create`) + indirect via CLI | **~40%** — app builds; zero `TestClient` endpoint tests (`/soul/state`, `/soma/probe`, `/safety/check`…) |
| `brain/server.py` | indirect (`doctor` monkeypatch) | **~10%** — constants/probe path; router endpoints never tested |
| `soul/api.py` | indirect (`soul-export` → `_compute_state`) | **~15%** — no route-level tests; SSE never exercised |
| `brain/activations.py` | 0 | **0%** (dead code anyway) |
| `server/erika_torch_server.py` | 0 | **0%** — stub endpoints untested; a 200-line test of `/health` + `/erika/affect` no_data shape would pin the contract |
| `store/code_index.py` | 0 | **0%** — chunker/build/search untested (heaviest deps, but `_chunk_file` is pure stdlib and could be tested hermetically) |

Missing coverage concentrated exactly where the two verified defects live
(affect mapping, code_index error paths).

### 1.4 README accuracy / Acurácia dos READMEs

| Doc | Verdict |
|---|---|
| `brain/README.md` | **Accurate** — topology, endpoints, env vars, fallbacks all match code. |
| `soma/README.md` | **Accurate** — GPU telemetry documented is now real (was stale in the study doc). |
| `store/README.md` | **Accurate** — schema, pipeline, env var correct. |
| `soul/README.md` | **Accurate** — both compute paths, SSE fallback, UI polling described correctly. |
| `server/README.md` | **Accurate and honest** — explicitly documents stub status vs canonical server. |
| `src/omni_coworker/README.md` | Mostly accurate; claims `soul/state` uses "kernel Rust 28d" — true only when wheel present (documented). |
| `docs/KAGGLE_SETUP_VALIDATION.md` | **Two stale/wrong claims:** (a) "GPU telemetry is not actually read — docstring-level" — **fixed since commit `eebc2e6`**, `_gpu_probe` is real; (b) "dream/curiosity degrade to extractive fallback **without the index**" — false, missing index → `FileNotFoundError` → 500 (D2). Also says "69 passed" (now 75). |
| `soma/probe.py` docstring | Mentions "PSI" (:3,:6) — no `/proc/pressure/*` is read; ambiguous with the `psi` affect scalar. Minor drift. |

### 1.5 Loop-closure proposals / Propostas para fechar o loop

**P1 — Persist soma continuously (persistence).**
App lifespan background task or `probe_recorded()` at each `/soma/probe` hit
(`OMNI_SOMA_RECORD_INTERVAL`, default e.g. 30s). Cheapest variant: switch
`app.py:35` to `probe_recorded()` and merge `brain_affect` post-record. Add
`omni-coworker soma record|summary|recent` CLI. Cost: ~20 lines; instantly
makes `SomaticStore` a real interoceptive history instead of dead code.
*pt-BR: tarefa de fundo no lifespan ou `probe_recorded()` por request; hoje a
loja só escreve em testes.*

**P2 — Single state root + recycle-resilient export (integrity across VM recycles).**
Introduce `OMNI_STATE_DIR` (default `<repo>/data`) and anchor
`somatic_probes.sqlite`, `node.db`, `witness.jsonl`, `erika_torch_activations.jsonl`
to it — kills the cwd-fragility (D5). Add `omni-coworker state export|restore`:
`tar.zst` of `OMNI_STATE_DIR` + `omni_code_index/` (mirroring the omni_node
`data/exports/*.tar.zst` policy), plus `verify_witness()` on restore — the
hash-chain machinery already exists (`agency/witness.py`) and is the natural
integrity proof after an ephemeral-VM recycle. `code_index` is deterministically
rebuildable (manifest records model+chunks+dim), so restore can offer
`--rebuild-index` instead of shipping embeddings.
*pt-BR: raiz única de estado, export tar.zst + verificação da cadeia de hashes
na restauração — integridade entre recycles sem depender de disco persistente.*

**P3 — Session continuity (continuidade de sessão).**
Reuse `missions(id, spec)` — currently dead schema — to log orchestrator
missions from `create_task` (`agent_orchestrator.py:93-108`), and add a
`soul_state` snapshot table (or reuse `probes.extra_json` with
`kind:"soul_state"`) written by a `soul-export --record` flag; on boot,
`doctor` can print last-snapshot delta → continuity across process/VM
restarts without new infrastructure.
*pt-BR: reusar a tabela missions morta + snapshot de soul_state; doctor
mostra o delta do último snapshot — continuidade sem infra nova.*

**P4 — Recalibrate `derive_affect_from_brain` (fix D1).**
Replace the raw linear map with baseline-normalized scalars: keep
`attention_entropy_mean`/`hidden_norm_mean` raw in the payload, compute
normalized metrics against an EMA baseline persisted in `SomaticStore`
(e.g. `z = clip01((x − μ)/3σ)`), or divide entropy by `log(n_heads)` when the
upstream exposes head count. Propagate `status:"no_data"` distinctly from a
zero vector. Medium-term: a trained linear probe on mid-layer hidden states
(see §2.2) is the research-grade replacement for this hand-map.
*pt-BR: normalizar por baseline EMA persistido; propagar no_data; médio prazo,
probe linear treinado em camadas médias.*

**P5 — Wire or delete `brain/activations` (D4).**
Either feed the ring buffer — mirror upstream `/erika/activations` summaries
after each `/brain/chat` response in `brain/server.py`, giving local code a
push-free recent-activations API — or delete the module and drop the re-exports.
Today it is dead weight that masquerades as a live activation buffer.
*pt-BR: alimentar o buffer espelhando o upstream após cada chat, ou remover —
hoje é peso morto que finge ser buffer vivo.*

**P6 — `code_index` lifecycle (D2+D3).**
Guard `search()`/`_load` against missing artifacts → return
`{"status":"index_missing","fragments":[]}`-style empty result instead of 500
(this also makes the Kaggle doc claim true); key the `_INDEX` cache by
`out_dir` + manifest mtime; add `omni-coworker index build|search` so the
index no longer requires a manual python one-liner.
*pt-BR: resposta vazia estruturada em vez de 500; cache por out_dir+mtime;
subcomando index no CLI.*

**P7 — Cheap tests where the defects were.**
(a) `derive_affect_from_brain` with a fake 200-response client (catches D1);
(b) `code_index.search` on an empty tmp dir (catches D2); (c) artifacts-table
round-trip on `NodeDB` (the production-used table is the untested one);
(d) `TestClient` smoke for `/soul/state`, `/soma/probe`, `/brain/health`;
(e) stub server `/erika/affect` no_data contract. ~150 lines of tests, all
hermetic.
*pt-BR: ~150 linhas de testes herméticos cobrindo exatamente onde os defeitos
estavam.*

**P8 — Thinking-leakage guard for external CLIs (see §2.3).**
A small downstream detector in `ExternalCLIAgent.execute`/`reviewer_agent`:
scan output for `</?think`/`</?thinking` tag fragments and reasoning-trigger
prefixes ("Okay,", "Alright,", "I need to") → flag into the artifact verdict.
Cheap insurance for the day an executor brain is a reasoning model.
*pt-BR: detector downstream barato de tags/fragmentos de raciocínio no output
dos CLIs externos.*

### 1.6 Dependency/ops notes / Notas de deps e ops

- `pyproject.toml:35` sets `asyncio_mode = "auto"` but `[test]` extra lacks `pytest-asyncio` → harmless warning; add it or drop the option.
- `[kernel]` extra now correctly ships pandas+pyarrow (fix `8865afe`); `nvidia-ml-py` included — matches the pynvml path in `soma/probe.py`.
- `soul/api.py` SSE: synchronous `probe()` + sync `httpx` inside `async def stream()` blocks the loop each 2s tick — acceptable at current scale; an `anyio.to_thread` wrapper is the tidy fix.
- `docker`/`kaggle`/`colab` detection in `_virt_probe` is solid; consider also `/proc/1/cgroup` `kubepods` (already covered) and `/.dockerenv` (covered).

---

## 2. PESQUISA 2025–2026 — mapping onto this codebase / mapeamento

### 2.1 Interoceptive telemetry — psutil vs NVML vs DCGM/Prometheus

**Finding:** the `soma/probe.py` design (in-process `pynvml` → `nvidia-smi`
subprocess fallback) matches NVIDIA's own guidance. AIPerf (NVIDIA's
benchmarking tool) exposes exactly two collector paths:
`--gpu-telemetry pynvml` for local/single-node monitoring with zero
infrastructure, vs DCGM endpoints for multi-node/production
(docs.nvidia.com/aiperf; `aiperf/gpu_telemetry/pynvml_collector.py`). DCGM +
`dcgm-exporter` + Prometheus is the fleet-scale answer (~50 metrics/GPU,
DaemonSet), not a single-agent answer. So: **pynvml is the right choice for a
Kaggle/Colab single-agent; DCGM would be over-engineering here.**

**The real gap is cgroup-awareness, not the GPU path.** Inside a container,
`psutil` reads host `/proc`: `virtual_memory()`, `cpu_count()`, `loadavg`
describe the *node*, not the agent's actual envelope (giampaolo/psutil#1011).
Production telemetry tools (Metrana autocapture; `whisperx-web/back/metrics.py`)
differentiate cgroup `cpu.stat`/`memory.max` against wall-time instead.
For a Kaggle kernel — where the agent's "body" is a cgroup slice, not the host —
**the interoceptive signal should read `/sys/fs/cgroup` quotas** (v1+v2) and
report limit-relative usage. Otherwise `phi = 1 − ram_ratio` measures the
host's RAM, which on a shared node is interoception of *someone else's body*.
Also: NVML device-aggregate utilization cannot attribute usage per process
(dcgm-exporter#642) — acceptable here (one agent, one GPU), worth a doc note.

**Formal grounding exists:** INTERO (CEUR 2025, `Vol-4169/paper6`) builds an
ontology of robotic interoception explicitly citing CPU load, temperature and
power as interoceptive signals; *Body-Grounded Perspective Formation*
(arXiv 2605.16728) models interoception as a bounded, saturating channel —
structurally identical to `clip01` scalars in `soul/api.py`. The soma→LLM
injection (`_soma_inject`, `agents/_llm.py:16-38`) is, in literature terms,
giving the model an interoceptive readout channel — sensorimotor
self-recognition work (arXiv 2505.19237) shows embodied agents develop
self-identification from exactly this kind of structured self-telemetry.

**Interop option:** OpenTelemetry GenAI semantic conventions
(opentelemetry.io/blog/2025/ai-agent-observability; repo
`open-telemetry/semantic-conventions-genai`) now standardize agent spans
(`invoke_agent`, `plan`, `execute_tool`) and `gen_ai.*` metrics. Mapping
`soma` probes + soul scalars into OTel attributes would make the coworker's
interoception legible to standard observability stacks without changing the
internal model.

### 2.2 Affective computing applied to LLMs — internal-state → affect

**The 2025–2026 literature strongly supports the architecture (activations →
affect scalars) and equally strongly indicts the current hand-tuned mapping
(D1).**

- **Probing beats prompting for state readout.** *LLaMAs Have Feelings Too*
  (ACL 2025, anth `2025.acl-long.306`): probe classifiers on hidden states
  beat prompting by up to +14% accuracy and cut memory ~57%; signal peaks in
  **mid-layers**, and last-token pooling is not always best. *Decoding Emotion
  in the Deep* (arXiv 2510.04064, Qwen3/LLaMA): emotion forms a "well-defined
  internal geometry" that sharpens with scale, emerges early, peaks
  mid-network, persists for hundreds of tokens, and is malleable by system
  prompts. The canonical erika server already captures 65-layer hidden states
  — a linear probe trained on labeled activations is a drop-in replacement
  for `affect.py:45-49` and is the research-standard way to get calibrated
  scalars.
- **Causal validation exists.** *Mechanistic Interpretability of Emotion
  Inference* (ACL Findings 2025, `2025.findings-acl.679`): mid-layer MHSA
  causally drives emotion inference (activation patching). *Do LLMs "Feel"?*
  (PMLR 306, 2026): context-agnostic emotion directions + circuits → 99.65%
  controllable expression. *EmoVec* (EMNLP Findings 2026, `2026.findings-emnlp.1707`):
  contrastive activation addition steers affective intensity at inference
  time — the write-side counterpart of this repo's read-side `/erika/affect`.
- **The safety link is now documented.** *Emotion Concepts and their Function
  in a Large Language Model* (Anthropic, Apr 2026, arXiv 2604.07729):
  internal emotion-concept representations in Claude Sonnet 4.5 *causally
  influence* outputs — including misaligned behaviors (sycophancy, reward
  hacking). Implication for omni_worker: brain-affect should feed
  `safety/`+`governance` (e.g. dissent/quarantine triggers), not only the
  `/soul/state` display.
- **Monitoring precedents.** Therapeutic-persona-drift monitoring via
  activation vectors (Llama-3-8B/Qwen2-7B/Mistral, contrastive probing)
  tracked persona quality better than text-based detection — a validated
  template for an activation-space health monitor over the analyst brain.
  *Gnosis* (arXiv 2512.20578): compress hidden states + attention maps into
  fixed-budget descriptors → hallucination-risk scalar, ~5M params, ~zero
  latency — exactly the "internal state → calibrated scalar" pattern needed
  to replace D1's saturating map. Tooling: `a9lim/drowse` ships a local
  manifold/probing workbench with a 20-emotion concept set.

**Concrete path:** keep `attention_entropy_mean`/`hidden_norm_mean` as raw
inputs; add a per-model linear probe over mid-layer hidden-state summaries
(served alongside, not inside, the 4-metric API); normalize against an EMA
baseline in `SomaticStore` until the probe exists. This closes D1 with a
2026-state-of-the-art mechanism rather than another hand-tuned rescale.

### 2.3 Thinking-leakage detection (reasoning trace → user-visible output)

**This is now a documented, recurring failure mode — not hypothetical.**

- **Empirical rates.** *Leaky Thoughts* (EMNLP 2025, `2025.emnlp-main.1347`):
  reasoning traces leak private data; reasoning text bleeds into final
  answers **5.55% of the time on average, up to 26.4% (s1), 6.0%
  (DeepSeek-R1)**; more test-time compute *increases* leakage. Their
  detection method is simple: scan answers for reasoning-trigger openers
  ("Okay,", "Alright,", "I need to"). *R2MU* (EMNLP 2025): even after
  unlearning, ~19.7% of samples keep sensitive traces in reasoning.
- **Serve-layer leakage is endemic in OpenAI-compatible stacks:** vLLM
  `Qwen3ReasoningParser` leaks `</think>` into `content` under
  `stream=True` + `stop` sequences (issue 38789); GLM-5.3 templates ignore
  `enable_thinking=false` and pass the scratchpad through (PR 54825);
  `qwen3_xml` tool parser consumes `</think>` and merges reasoning into
  `content` with no boundary marker (issue 51679). LiteLLM PR 28691 adds a
  `ThinkTagParser` streaming state machine + `parse_think_tags` opt-in — the
  reusable pattern: *detect downstream, never trust the upstream boundary.*
- **Implication for omni_worker:** today's brains are non-reasoning Gemma-4-it
  (no think channel), but the architecture already pipes third-party agentic
  CLIs (`agents/external_cli_agent.py` — ACP + shell) and any future
  reasoning-model executor would inherit this failure mode. The detection
  surface is cheap and localized: (a) tag/state-machine scan
  (`<think>`, `</think>`, `<thinking>`, split-across-chunks) on
  `ExternalCLIAgent` output and `brain_chat` returns; (b) reasoning-trigger
  prefix lexicon at answer start; (c) flag into `NodeDB` artifact `verdict`
  so leakage becomes auditable state, and `witness_event` the detection for
  the hash-chained trail. This also guards the `_soma_inject` path: a model
  that echoes its interoceptive preamble is exhibiting boundary confusion of
  the same family.

---

## Appendix A — Evidence commands / Comandos de evidência

```bash
# test baseline
cd /content/omni_worker && /content/omni_node/.venv/bin/python -m pytest tests -q
# -> 75 passed, 1 warning (asyncio_mode unknown)

# D1 reproduction (fake upstream with documented real values)
# attention_entropy_mean=1.83, hidden_norm_mean=130.0 ->
#   {phi:0.0, psi:1.0, sigma:1.0, epsilon:0.1}

# D2 reproduction
code_index.search("q", tempfile.mkdtemp())  # -> FileNotFoundError chunks.parquet
```

## Appendix B — Key references / Referências-chave

- NVIDIA AIPerf GPU telemetry (pynvml vs DCGM paths) — docs.nvidia.com/aiperf; github.com/ai-dynamo/aiperf
- `nvidia/dcgm-exporter` — Prometheus exporter; per-process attribution limitation: issue #642
- psutil container/host stats — giampaolo/psutil issue #1011
- OpenTelemetry GenAI agent observability — opentelemetry.io/blog/2025/ai-agent-observability; semantic-conventions-genai repo
- ACL 2025 — "LLaMAs Have Feelings Too" (2025.acl-long.306)
- arXiv 2510.04064 — "Decoding Emotion in the Deep" (Qwen3/LLaMA emotion geometry)
- ACL Findings 2025 — "Mechanistic Interpretability of Emotion Inference" (2025.findings-acl.679); "Emotion Neurons" (2025.findings-acl.806)
- PMLR v306 (2026) — "Do LLMs Feel? Emotion Circuits Discovery and Control"
- EMNLP Findings 2026 — "EmoVec: Controllable Affective Generation via Latent Vector Steering" (2026.findings-emnlp.1707)
- Anthropic Apr 2026 — "Emotion Concepts and their Function in a Large Language Model" (arXiv 2604.07729)
- arXiv 2512.20578 — "Gnosis: self-awareness via hidden-state descriptors"
- CEUR Vol-4169 — "INTERO: robotic interoceptive sensing ontology"
- arXiv 2605.16728 — "Body-Grounded Perspective Formation (interoceptive viability channel)"
- arXiv 2505.19237 — "Sensorimotor Self-Recognition in MM-LLM robots"
- EMNLP 2025 — "Leaky Thoughts: Large Reasoning Models Are Not Private Thinkers" (2025.emnlp-main.1347); R2MU (2025.emnlp-main.220)
- vLLM issues/PRs — #38789, #51679, PR #54825; LiteLLM PR #28691 (ThinkTagParser)
