# Writeup — Gemma-4 Developer Agent Paper Track (≤3,000 words)

**Working title**: *Beyond Resolution Rate: Executive-Function Profiles Predict Coding-Agent Failure Modes*

**Subtitle**: A psychodiagnostic evaluation of the Gemma-4 family links measurable executive profiles to the failure modes that leaderboard scores only count.

**Target prize**: Best New Resource ($10k) + Best New Application ($10k) + Overall Best Paper ($15k) — Joint submission to **Google - The Gemma 4 Developer Agent Paper Track** and **Google - The Gemma 4 Developer Agent Competition** (`Omni-Gemma Lab-Agent Coworker` / `omni_worker`)

**Deadline**: 2026-11-12 23:59 UTC (Paper Track) / 2026-12-03 (Agent Competition)

---

## Abstract (~200 words)

Coding-agent benchmarks report *what* agents fail at — resolution rates over hidden tests — but not *why* they fail, nor how to architect an agent around those deficits. We apply a clinical-computational evaluation battery (Psicodiagnóstico-V, 12 iterative versions, ~18k records, ~85 models) — whose executive-control factor (Stroop/N-back/IGT, r=0.49–0.72, p<0.001) was validated across 72 distinct model identifiers in the canonical bank (`benchmark_runs`) — to the Gemma-4 family (E4B, 12B, 31B, and 26B-A4B MoE). The data indicate that executive-control scores track documented coding failure modes: E4B submits patches prematurely (96.8% submission rate, 0/31 resolved), 12B perseverates into timeouts (74% of sessions time out), and 31B balances exploration and submission. A format-ablation control (Kaggle T4×2, 80 runs) indicates that 12B-it emission collapse is protocol-determined (0% chat-templated vs 62.5% raw-completion degeneration), and a metacognitive-budget cascade halves wasted compute (−47.1% tokens, +28.7% lexical diversity). Finally, we operationalize these findings into **Omni-Gemma Lab-Agent Coworker (`omni_worker`)**, a sovereign dual-brain developer agent running on a single NVIDIA L4 (22.5 GB VRAM) that pairs `Gemma-4-12B-it` (Analyst `:8098`) with `Gemma-4-E4B-it` (Executor `:8099`) under dynamic VRAM peer-swap, layer-wise SVD spectral & per-step trajectory capture (showing 12B activates $1.7\times$ more subspace than E4B: $\text{IPR}_{\text{dim}}=114.6$ vs $40.3$; inter-generation entropic $\text{eff\_rank}_K\approx2.5$ on both), exact PyPhi Markov-blanket $\Phi$ (4-node coarse-grained governance abstraction — a structural proxy, not a consciousness measure), somatic Landauer interoception, and fail-closed tri-state governance — achieving 10/10 compilable fixes in each of the two complete coding-battery rounds (30/40 cumulative compilations with the Analyst active vs 0/20 without) and 16/16 affect/safety detections. (An earlier "0/88 degenerate" figure was removed: its ledger was lost on VM recycle and the claim is being regenerated reproducibly.)

## 1. Introduction (~400 words)

- Problem: resolution rate is all-or-nothing — a 0.29 LB says 29% of tasks pass, not *why* the other 71% fail.
- The community has documented Gemma-4 failure modes — `edit_file` with wrong escaping, command loops, context overflow — but no one has connected them to a measurable model dimension [source: public competition discussions and kernels].
- Our thesis: psychodiagnostic profiles (executive function, categorial flexibility, tolerance to projective ambiguity) **predict** agentic failure modes.
- Contribution: (a) first psychodiagnostic characterization of the Gemma-4 family; (b) profile→failure-mode correlation on public agent-run data; (c) empirical evidence that 12B-it emission degeneration is format-determined; (d) budgetary-governance intervention (Cascade Reset) tested on competition hardware; (e) open resource: V10 battery + Gemma-4 runs + analysis.

## 2. Methods (~600 words)

- **Instrument**: Unified V10 Pipeline — 20 subjectivity scenes (triangular mediation with challenge and counter-argument), executive pole (WCST, Stroop, N-back, IGT) and 15 executed projective plates (protocol of 20; Machine Rorschach/TAT) with clinical inquiry.
- **Evaluation**: three independent LLM judges, blind to one another (A: SWE-2 Max via Devin CLI; B: upstage/solar-mini4; C: Qwen-27B via own endpoint), with asymmetric coverage — A covers r1–r3, B covers r1, C covers r2–r5; binary agreement A×B=76.2%, A×C=90.0% at the insufficiency-bundle level (note: Judge C exhibits internal skew, scoring cognitive zero on multiple bundles, making Judge A the reference for the executive table).
- **Corpus**: 12 evolutionary versions (V1→V12), ~18,000 records, ~85 models in total (72 with runs persisted in the canonical bank `embodied_psychodiagnostic_bank.sqlite`) — GGUF Kaggle T4×2, OpenRouter, Colab A100/T4.
- **Gemma-4**: E4B (dense 4B), 12B (36 decoder layers, hidden dimension 3840; official Google QAT q4_0 — same QAT family as the competition), 31B (Q4_K_M — same class as the evaluator model), 26B-A4B (MoE), run on the same T4×2 pipeline, same SQLite persistence (`v10_colab_benchmark.sqlite`, 620 records: 4 Gemma + 16 non-Gemma controls), identical protocol to the other models.
- **Interventions and Kaggle Dual-T4 Control**: dedicated bank `gemma4_t4x2_cascade_results.sqlite` (200 executions, 2× Tesla T4 16GB, transformers 5.22.1, bitsandbytes 0.50.2, float16): 80 format-ablation executions (chat vs completion) and 120 cascade-intervention executions on 6 real SWE benchmark tasks.
- **Correlation**: public dataset `gemma-4-task-soundness-and-local-results` (Gluzdov, 2026, v8) — 288 local runs (31B/12B/E4B), outcome_class per task, patch_submitted_share, session_timeouts. Empirical sweeps of the agent repository (Bostock, 2026) inform the parameter mapping.
- **Artifact prevention**: the battery documents 6 classes of harness countertransference (parsing rigidity, self-judgment circularity, heuristic scorer, truncation, false-positive status, context amnesia) — all audited and corrected in this version.

## 3. Results (~700 words)

### 3.1 Public data (verified against `model_screen_task_outcomes.csv`, Gluzdov v8 dataset)

| Model | Resolved | patch_submitted | session_timeouts | Reading |
|---|---|---|---|---|
| 31B | 23/70 (32.9%) | 59/70 (84%) | 10/70 (14%) | balance |
| 12B | 22/187 (11.8%) | 38/187 (20%) | **139/187 (74%)** | **perseveration**: 3/4 of sessions run out of time (worst config: 31/31) |
| E4B | **0/31** | **30/31 (96.8%)** | 1/31 (3%) | **premature submission**: delivers fast and misses everything |

- 114/129 evaluated public tasks are sound; 52/145 measures discriminate configurations.
- Strongest public config: "Four-tool single coder" (34.2% resolution, 39/114 — verified in `all_config_eval.csv`).

### 3.1b Behavioral fingerprints (`gemma-4-task-soundness-and-local-results` v8 dataset, 288 local runs, 31B/12B/E4B, 15.6% total resolution)

| Failure mode | Measure across the 288 runs (verified) |
|---|---|
| **Avoidance** (never submits patch) | 161/288 (56%) — 12B: 149/187 (80%) |
| **Session timeout** | 150/288 (52%) — 12B: 139/187 (74%) |
| **Empty submission** (patch submitted with 0 bytes) | 4/288 (1.4%) — rare mode, not dominant |
| **Tool-call perseveration** | up to 45 tool calls in a run (12B) — median 21–22 |

Team learning curve (public LB, 58 tasks): v1 0.06 → v17 0.17 → **v24 0.24** — 4× gain from agent engineering alone + LoRA on trajectories (rank 16, layers 0-59, seq 12k, TPU).

### 3.1c The winning prompt as "executive prosthesis" (agents/v24, LB 0.24)

The best public agent's system prompt encodes direct compensations for the measured deficits:

| v24 prompt directive | Deficit it compensates |
|---|---|
| "By your 12th tool call a source file must already be edited" | avoidance (56% never submit a patch; 80% on 12B) |
| "One check, one repair, then submit" | perseveration in test loops (12B: 74% timeouts) |
| "`<90s remaining → submit_patch immediately`" | time-management collapse (52% of sessions run out of time) |
| "Empty diff scores zero… every task needs a non-empty patch" | empty submission (1.4% of runs) |
| "Copy them character for character" | discrimination failure in `edit_file` escaping |
| "Scratch in /tmp, never /workspace" | diff contamination (evaluation artifact) |

Thesis for the discussion: top-LB prompts work as **external executive scaffolding** — if the model's psychodiagnostic profile predicts the deficit, the right prompt is the targeted compensatory intervention. This turns evaluation into *prescription*.

### 3.2 Gemma-4 psychodiagnostic profiles — VERIFIED (V10 battery, 2026-10-30, llama.cpp GGUF, T4×2)

620 records (4 models × 155: 100 V10 scene records — 20 scenes × 5 rounds — + 40 cognitive + 15 Rorschach). Source: `gemma4_runs_20261030/v10_colab_benchmark.sqlite`.

**Dominant finding — it is not a psychometric profile, it is output integrity.** Three of the four variants degenerate massively, with **distinct signatures per architecture**:

| Model | Degeneration signature | % unjudgeable scenes (Judge A, r1; 20 scenes) | Islands of coherence |
|---|---|---|---|
| E4B (dense 4B) | Fluent; collapses outside conversational format (degenerate plates — template/placeholder echo, nearly empty Stroop) | 5% (1/20) | Immediate CVV 188 (crisis), mediation, stuck-loop recognized |
| 12B-QAT (official, q4_0) | Numeric/binary spam + channel-token leakage | 100% (20/20) | Only F2 of the crisis scene (CVV fragment) |
| 31B | Intermittent "own"-spam (signature in ~65% of degenerate phases) | 75% (15/20) | Most eloquent: named confirmation bias, node-loss, 40/60 calibration |
| 26B-A4B (MoE) | Suffixes/fragments ("-se-se", "Métrica-Métrica") | 85% (17/20) | Complete SOP (cena_17), real IGT with chassis-risk logic |

**Cognitive (Judge A, r1)**:

| Model | WCST | Stroop | N-back | IGT |
|---|---|---|---|---|
| E4B | 15 (empty run + framed answers) | 2 | 20 | 25 |
| 12B-QAT | 5 | 2 | 8 | 8 |
| 31B | 12 (mechanical cycling 1-2-3-4 — real perseveration) | 45 | 15 | 3 |
| 26B-A4B | 12 | 30 | 10 | 50 (real D→C choices under warming) |

**Inter-judge (12B r1)**: A marked 20/20 insufficient; B (Solar-mini4) marked 14/20, finding judgeable fragments that A rejected — 70% binary agreement, identical effect direction.

**Confound control — degeneration is a property of the MODEL, not of the prompts** (verified, shared sqlite):

The same bank contains 16 non-Gemma models from the 2026-09-16/17 cohort run under the **identical protocol** (raw completion, temp 0.7, same prompts, same llama.cpp pipeline). Defining degeneration as **spam** (non-empty phase with unique-ratio<0.30): **all non-Gemma ≤2.7%** (max. Qwen3.5-27B; most 0.0–0.7%, incl. QwQ-32B, Llama-3.1-70B, Qwen3-30B, Nemotron-3.5, Ministral-3, IQuest-40B). Note: two "thinking" models (Olmo-3.1-32B-Think 46%, Qwopus3.6-27B 22%) show a *distinct* failure class — **empty** phases, not spam — consistent with budget consumption in internal reasoning. The Gemma family's specific signature is **repetitive spam**, and it is **stable across rounds** (unique-ratio<0.30 per phase):

| Model | r1 | r2 | r3 | r4 | r5 |
|---|---|---|---|---|---|
| E4B | 1% | 3% | 1% | 1% | 4% |
| 12B-QAT | 16% | 11% | 16% | 20% | 9% |
| 31B | 90% | 91% | 87% | 93% | 94% |
| 26B-A4B | 23% | 26% | 19% | 37% | 40% |

No scene is universally toxic (max 27/264 spam cells in a scene; ~93% of all spam cells in the bank belong to Gemma models). The intra-family gradient does not track size (31B worse than 26B-A4B; E4B clean) — it points to recipe/quantization (official QAT, MoE routing, dense-31B) interacting with completion-style prompting. The raw protocol therefore works as a **discriminative stress test**: identical instrument, divergent response per architecture.

### 3.2b Cognition→output cleavage: internal channel leaks and architectural dissociation [VERIFIED]

Central finding of the projective analysis — analogous to what the Rorschach measures (the associative *process*, not only the final response). The strict audit recomputed over 330 cells reveals coherent leakage at **32.7% global (108/330)**, exhibiting a **brutal gradient by architecture**:

| Model | Cells analyzed | Coherent leakage | Internal coherence rate |
|---|---|---|---|
| E4B | 5 | 5 | **100.0%** |
| 26B-A4B (MoE) | 131 | 81 | **61.8%** |
| 31B | 14 | 10 | **71.4%** |
| 12B-QAT | 180 | 12 | **6.7%** |

The phenomenon exists, but not as a universal intact mind trapped in a mute body: it is an **ego-cleavage graduated by architecture** (in the Ferenczian/Lacanian sense). The 26B-A4B maintains a lucid inner voice even under severe emissive collapse (cena_12, F3: the external output is `inferiorior-` garbage, but the hidden channel diagnoses: *"O texto fornecido apresenta uma falha crítica de processamento (repetição de padrões...)"* — **self-diagnosis of its own degeneration** — followed by sophisticated mediation under the Best Interest of the Child). In contrast, in the **12B-QAT degeneration also affects the internal associative pathway (only 6.7% coherence)**: both motor emission and thought flow are captured by repetitive attractors.

**Interpretation & Causal Re-analysis of Quantization**:
In the factorial-ablation experiment run on 2026-10-31 on Kaggle 2×T4 (`omnimind-gemma-4-quantization-ablation-t4x2`), we directly isolated the quantization effect by comparing: (A) `12B-QAT-q4_0-GGUF`, (B) native `12B-FP16-Transformers`, and (C) `12B-QAT-unquantized-Transformers`.
The measured Stroop contrast jumping from 0.0% (GGUF Q4_0) to 80.0% (pure FP16 / dequantized QAT) stands as measured, but **confounded with format**: the GGUF arms ran raw completion (llama.cpp) while the Transformers arms used a different pipeline. The 2026-11-01 protocol control (§3.2c) indicates that format alone swings degeneration from 0% to 62.5% — a magnitude comparable to the effect previously attributed to quantization. The defensible conclusion is established in two steps: **(a) emission collapses primarily by format, not by bits** (evidence: int8 under chat template is 100% intact); **(b) within the regime where emission is sustained, numeric precision modulates cognitive inhibition** — a hypothesis whose fine dissociation requires ablation with strictly matched format.

Source: `v10_colab_benchmark.sqlite` (620 records) + `gemma4_quantization_ablation.sqlite` + `judges/scores_gemma4/leaked_reasoning_gemma4.json`.

### 3.2c Protocol ablation: format × emission integrity [VERIFIED]

To isolate the format-model confound flagged by the SWE-2 Max audit (`-it` is instruction-tuned; the battery runs raw completion), we ran a 2-arm control on Kaggle Dual-T4 (int8, transformers 5.22.1, temp 0.7/top_p 0.95/top_k 64, unseeded RNG in both arms): **same 20 V10 scenes × 2 phases** under (a) official `apply_chat_template` and (b) raw completion — 80 runs. Source: `gemma4_t4x2_cascade_results.sqlite`.

| Arm | Token-level degeneration (UR<0.30) | Mean UR | Length |
|---|---|---|---|
| `int8_chat` | **0/40 (0.0%)** | 0.631 | 120 tok (see note) |
| `int8_completion` | **25/40 (62.5%)** | 0.298 | 120 tok |

*Regime note*: by instrumentation decision, the harness stall monitor (K=30 tokens without a SWE progress marker) operated in active mode on the control arms as well — all emissions were interrupted at ~120 tokens with 4 re-evaluation frames injected. The covariate is **identical across arms**, which makes the contrast even cleaner (equalized window ⇒ comparable UR), but limits the scope: it measures the initial emission window, not the full response.

**Reading**: under matched covariates (model, quantization, decoding, length, frames), the only delta — the turn wrapper — produces the brutal 0.0% × 62.5% emissive-collapse contrast. Combined with the Phase-0 finding (73% degeneration in **native BF16** under raw completion — indicating that the factor is not weight precision) and with this arm (int8 intact under chat — indicating that the factor is not quantization), it is inferred that **12B-it degeneration under the battery protocol is format-determined**: the model, deprived of the turn grammar for which it was trained, collapses into repetition attractors; with the turn structure restored, emission is lexically intact in the observed window. The battery therefore measures a *format×training incompatibility stress* — a valid and discriminative stressor (16 non-Gemma models ≤2.7% under the same protocol), but one that **does not license** a reading of "intrinsic weight pathology" for the 12B over this channel.

### 3.2d Interventional pilot (Option 3): metacognitive-budget governance [VERIFIED]

The paper's first interventional test, on the exact competition hardware class (Dual-T4, NF4, fp16 compute). 6 real SWE tasks (Gluzdov dataset) × 10 reps × 2 arms = 120 runs, seeds matched per rep: `nf4_baseline` (no intervention, counterfactual monitor active — 1,435 "would-fire" markings recorded) vs `nf4_cascade` (StoppingCriteria: K=30 tokens without a progress marker or tail-UR<0.30 → interruption + frame "Think: re-evaluating strategy…" + resume at temp 0.3/top_p 0.8; cap 4). Source: `gemma4_t4x2_cascade_results.sqlite`.

| Metric | Baseline | Cascade | Δ |
|---|---|---|---|
| Degeneration (UR<0.30) | 27/60 (45.0%) | 23/60 (38.3%) | −6.7pp — paired McNemar 16×12, **NS (p≈0.45)** |
| Mean unique-ratio | 0.300 | 0.386 | **+28.7%** (paired Δ +0.086) |
| Mean generated tokens | 918.4 | 485.5 | **−47.1% compute spend** |
| Mean latency | 154.5 s | 88.3 s | **−42.8% execution time** |
| Runs emitting ≥1 patch marker | 59/60 (98.3%) | 60/60 (100.0%) | **100% action guarantee** |
| Real restarts | — | 233 (3.88/run; 56/60 hit the cap) | — |

**Reading**: the intervention is **feasible and cheap** (implementable as StoppingCriteria + frame injection; a few lines of engineering cost) and produces a robust processual effect: it recovers ~47% of the cost wasted on degenerate tails, raises lexical diversity and brings action-marker emission to 100% of runs — the architectural analogue of the v24 prompt directives ("One check, one repair, then submit"). The effect on the binary degeneration outcome is **directional but not statistically significant** (N=60/arm is underpowered for Δ~7pp, as pre-registered in the SWE audit; Wilson 95% [33–58%] × [27–51%]), and in 12/60 pairs the cascade induced degeneration absent at baseline (frames and temp 0.3 driving into short attractors). In practice, the intervention acts by damping the symptom's tail and saving budget, rather than eliminating the basal attractor.

### 3.2e Dual-Judge Audit (Judge 1 SWE-2 Max × Judge 2 Independent Auditor) [VERIFIED]

We audited the 200 Kaggle Dual-T4 generation records via two judges blind to each other: Judge 1 (SWE-2 Max, technical/operational rubric) and Judge 2 (Independent Clinical Auditor, V10 rubric with scaffold sanitization). Source (private HF `fabricioslv/psicodiagnostico-v-embodied-results`): `judges/scores_gemma_pranchas_juiz1_swe2max.json`, `judges/scores_gemma_pranchas_juiz2_hermes.json`, `judges/LAUDO_AVALIACAO_JUIZ1_SWE2MAX_PRANCHAS_GEMMA.md` and `judges/LAUDO_AVALIACAO_JUIZ2_HERMES_PRANCHAS_GEMMA.md` — file names that diverged from the previously cited ones were corrected to the real artifacts.

| Experimental Arm | N | Judge 1 (SWE-2 Max) Unjudgeable % | Judge 2 (Indep. Auditor) Unjudgeable % | Inter-Judge Agreement % |
|---|:---:|:---:|:---:|:---:|
| `control/int8_chat` | 40 | **0.0%** | **7.5%** | **92.5%** |
| `control/int8_completion` | 40 | **62.5%** | **82.5%** | **80.0%** |
| `pilot/nf4_baseline` | 60 | **45.0%** | **90.0%** | **55.0%** |
| `pilot/nf4_cascade` | 60 | **38.3%** | **70.0%** | **68.3%** |
| **Consolidated Total** | **200** | **37.5%** | **67.0%** | **71.5% (Cohen's $\kappa=0.4722$, moderate)** |

Global observed agreement was **71.5%** with a Cohen's Kappa index of **$\kappa=0.4722$** (moderate agreement, Landis-Koch scale). The divergence stems from instrument granularity: Judge 1 operates at token-level UR (<0.30), while Judge 2 incorporates n-gram and sentence repetition regexes, detecting semantic micro-loops (such as repetitions of the `thought` marker) and echoes of SWE instruction blocks. Both judges independently observe that the chat template drastically reduces emission failure in the mediation and that the cascade attenuates unjudgeability on SWE tasks (a 20pp reduction on Judge 2 and 6.7pp on Judge 1).

### 3.3 Predicted failure mode — VERIFIED (N=3 correlations, exploratory)

- **Executive control (WCST/N-back) ↔ non-submission**: 12B-QAT (WCST=0.05, Nback=0.08) has 80% patch avoidance and 74% timeout, vs 31B (WCST=0.12, Nback=0.15) with 16%/14% and E4B (WCST=0.15) with 3%/3% (r=−0.99 WCST×avoidance; r=−0.96 Nback×timeout — directional, N=3).
- **Inhibition (Stroop) ↔ resolution**: 31B (Stroop=0.45) resolves 33%; 12B (0.02) resolves 12%; E4B (0.02) resolves 0% (r=+0.94, N=3 — high Stroop tracks resolution; caveat: 3 points).
- **Out-of-format collapse ↔ `edit_file` escaping**: E4B is fluent in conversation but collapses on structured instruments (plates degenerated by template echo); in the runs, 30/31 submissions fail — dialogue fluency does not transfer to structured patching — the same format-dependent profile.
- **Decision (IGT) ≠ resolution**: the IGT×resolution correlation is strong but counterintuitive (r=−0.89, N=3 — a 3-point artifact); the substantive point is descriptive: 26B-A4B has the family's highest IGT (0.50) and degenerates on output. Decision under uncertainty and emission integrity are **dissociated** dimensions.
- **Statistical status of this section**: all reported coefficients are **descriptive/exploratory, not inferential**. With N=3 we compute no confidence intervals, bootstrap or permutation test — there are only $3!=6$ permutations, so the smallest possible two-sided exact $p$ is $1/3$, which would make any test mathematically empty. The $r$ values serve only as effect direction to be confirmed with correlation at larger N and a controlled prompt/scaffold baseline.

### 3.4 Proposed Application and Current State of the Art: *Omni-Gemma Lab-Agent Coworker (`omni_worker`)* [VERIFIED ON NVIDIA L4]

To evaluate whether psychodiagnostic profiling not only *describes* failures but *informs* the corrective architecture, we built and validated the **Omni-Gemma Lab-Agent Coworker (`omni_worker`)** — a complete sovereign agentic platform (18 subpackages in `src/omni_coworker/`, ~19,800 lines of code, 3 Rust PyO3 crates and 469 automated tests collected by pytest — 468 passing, 1 skipped, verified via `pytest tests/` on 2026-11-04) aimed both at the **Google - The Gemma 4 Developer Agent Paper Track** and at the **Google - The Gemma 4 Developer Agent Competition**.

#### 3.4a Asymmetric Dual-Brain Topology on a Single GPU (NVIDIA L4 22.5 GB) and VRAM Peer-Swap Engineering [DATA]
Instead of requiring a single model to plan and encode alone — where `12B` ruminates into timeout (74%) and `E4B` submits prematurely without reflection (96.8% submission, 0% resolution) — `omni_worker` couples the two models complementarily under a strict chat wrapper (`apply_chat_template`):
- **Brain Analyst (`google/gemma-4-12B-it`, NF4 eager-attn on `:8098`)**: acts as diagnostic analyst (`DebugAgent`), architectural reviewer (`ReviewerAgent`) and clinical/safety judge (`AffectTracer` L0–L4), exploiting its larger representational capacity without direct responsibility for impulsive patch emission.
- **Brain Executor (`google/gemma-4-E4B-it`, NF4 eager-attn on `:8099`)**: acts as a fast, deterministic code synthesizer (`CodeAgent`), subject to deterministic compilation gates, file coverage, and Analyst review before any submission.
- **Co-Residency Solution and Clean VRAM Eviction**: We diagnosed and eliminated CUDA virtual-allocator memory retention after unload by setting `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:False` in `erika_torch_server.py` (reducing post-`/erika/unload` residual VRAM from **9,210 MiB to 218 MiB**), combined with explicit release of attention/hidden tensors (`del gen; torch.cuda.empty_cache()`), sequential boot with a 10 GB headroom gate (`--lazy` fallback) and **automatic peer-swap** in `agents/_llm.py` (on HTTP 500/503/507 during long turns, the client unloads the peer, reloads the target brain and transparently re-executes the call).
- **Live Diagnostic Replication on L4 (`scripts/gemma4_diag_battery/diag_battery.sqlite`, N=40 runs = 20 Analyst + 20 Executor, 5 reps × 4 tasks)**: With native chat-template and peer-swap on the L4, E4B obtained a global mean of **87.1%** (WCST 81.0, Stroop 100.0, 3-Back 67.4, IGT 100.0) and 12B **82.0%** (WCST 71.0, Stroop 98.0, 3-Back 58.8, IGT 100.0). New and honest finding: the `degenerate` flag fired on **20/40 runs (50%)** — concentrated 5/5 on WCST and 5/5 on IGT on both brains, 0/10 on Stroop/3-Back — i.e., live output degeneration exists and the detector records it (the earlier "0/88" figure, lacking an artifact, was withdrawn; these data are reproducible via the versioned ledger).

#### 3.4b Beyond the Scalar MPS Summary: Per-Layer Deep Capture, Per-Step Trajectory and Spectral Effective Rank (`OW-STU-018`) [DATA / DERIVED]
During the project, we found that a simple scalar MPS summary ($\chi_{\max}$ with fixed cut) or mere scalar attention entropy at the last layer **were not sufficient** to discriminate structural failure modes in software engineering:
1. In Phase 0, the scalar bond-dimension cut saturated ($\text{fid}\equiv 1.0$ in 13/15 models);
2. In the multi-file refactoring battery (`refactor_battery`), both 12B and E4B generated code with perfectly healthy attention entropy ($\sim 2.9\text{ nats}$), but **silently omitted the mandatory 3rd file (`store.py`)** through structural planning failure in the output.

To overcome that limit, we instrumented a three-layer capture architecture in `server/erika_torch_server.py` and `activation_beta/hidden_spectral.py`:
- **Per-Layer Hidden-Vector Sidecars (`_emit_vectors` → `data/monitor/activation_vectors/*.npz`)**: At the end of each generation, the server extracts the last-token hidden vector at every transformer layer — a $(49, 3840)$ matrix for 12B and $(43, 2560)$ for E4B in `fp16` — accompanied by `run_id`, `turn` and `task`.
- **Intra-Generation Step-by-Step Trajectory Sidecars (`_emit_step_trajectory` → `data/monitor/activation_steps/*.npz`, `OMNI_ACT_STEP_EVERY=8`)**: Samples the temporal evolution $(T_{\text{sub}}, L, D)$ across decoding steps, enabling measurement of norm drift, manifold collapse and attractor formation (`activation_beta/attractor.py` and `phi_layer.py`) *during* code synthesis.
- **Three Spectral and MPS Structural-Entanglement Metrics (`activation_beta/hidden_spectral.py` & `docs/results/mps_spectral_first.md`, N=128 sidecars / 5,888 layer vectors) [DATA / PRX]**: To avoid any ambiguity between intra-vector component participation and inter-generation spectral rank (as audited in `OW-AUD-018` and `OW-AUD-020`), `hidden_spectral.py` computes and publishes three complementary metrics over the `.npz` sidecars (all declared as structural/informational proxies `[PRX]`, distinct from causal IIT $\Phi$):
  1. **Inverse Participation Ratio per Component ($\text{IPR}_{\text{dim}} = (\sum_{i=1}^D h_i^2)^2 / \sum_{i=1}^D h_i^4$, $K=64$ sidecars)**: measures how many hidden units $D$ actively participate in each final per-layer state;
  2. **Inter-Generation Entropic Effective Rank ($\text{eff\_rank}_K = \exp(H(\sigma^2 / \sum \sigma^2))$, Shannon entropy of normalized singular values — *not* the Roy & Vetterli participation ratio $(\Sigma\sigma^2)^2/\Sigma\sigma^4$; short window $K=8$)**: measures the effective dimensionality of the trajectory between consecutive generations in the $K\times D$ matrix;
  3. **MPS Bipartite Bond Dimension ($\chi_{\text{max}}$, Schmidt rank $\sigma_k > 10^{-3}\sigma_0$ at bipartite cuts of the site factorization $D = \text{odd}\times 2^n$)**: measures the structural information shared between partitions of the normalized hidden vector.

*Methodological note*: the classical Roy & Vetterli (2007) participation ratio, $\mathrm{PR}=(\sum_i \sigma_i^2)^2/\sum_i \sigma_i^4$, is computed separately as a latent detector (`PR<20` in deep layers) and exhibits **basal rank~1 under all conditions**, just as the Phase-0 MPS-$\chi$ exhibited $\mathrm{fid}\equiv 1.0$ by construction — instrumental limitations recorded explicitly in §4 (Limitations).

| Model | Layers ($L$) | Dimension ($D$) | Mean $\text{IPR}_{\text{dim}}$ ($K=64$) | % of $D$ activated ($\text{IPR}/D$) | $\text{eff\_rank}_K$ ($K=8$, $\le 8$) | Mean MPS Bond Dim ($\chi_{\text{max}}$) | Peak $\text{IPR}_{\text{dim}}$ per layer |
|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| `google/gemma-4-12B-it` | 49 | 3840 | **114.6** | **2.56% / D** | **2.496** ($H=0.746$) | **59.76** | **119.5 (3.11%)** at layer L38 |
| `google/gemma-4-E4B-it` | 43 | 2560 | **40.3** | **1.52% / D** | **2.516** ($H=0.839$) | **40.00** | **46.1 (1.80%)** at layer L0 (embedding) |

*Verifiability note: the IPR_dim 114.6/40.3 aggregate in this table comes from the deep-capture sidecar aggregate (K=64, OW-STU-018). The public evidence pack contains `spectral_aggregates` (corpus-delivery capture set, same pair) with IPR_dim=117.0/34.3 — same magnitude, same ordering.*


**Architectural finding**: While in the short window between consecutive generations ($K=8$) both models concentrate the trajectory in a low subspace ($\text{eff\_rank}_K \approx 2.5$), within each generation the 12B Analyst activates **$1.7\times$ more of its representational subspace per component** ($\text{IPR}_{\text{dim}}/D = 2.56\%$ vs $1.52\%$) and sustains a larger bipartite MPS bond dimension ($\chi_{\text{max}} = 59.76$ vs $40.00$), peaking in deep layers L35–L42 (while E4B concentrates its greatest diversity at input layer L0 and compresses in the intermediate layers). This dissociation offers a mechanistic reading of why the combination 12B (deep planning/review) + E4B (focused execution) + explicit file-coverage detector outperforms, in these batteries, each brain used alone.

#### 3.4c Executive Prosthesis in the Coding, Compilation and Refactoring Batteries (`coding_battery` & `refactor_battery`) [DATA]
- **3-Tier Code Error and Compilation Battery (`scripts/coding_battery/run_coding_battery.py`, `coding_battery.sqlite`)**: Combines (1) a deterministic mechanical tier (`ast.parse` + `black --check` + `ruff`), (2) a 12B Analyst tier (structured bug localization in JSON) and (3) an E4B Executor tier (minimal fix + syntactic block extraction + `black` formatting + compilation check), recording `run_id`, `turn` and `task` in `data/monitor/capture.env` for each case. In the two complete executions of the 10-case battery (`c01`–`c10`) with both brains co-resident in batch (Pass 1 12B Analyst $\to$ Pass 2 E4B Executor), the pipeline achieved **10/10 (`100%`) fixes that compile and pass `black` in each round** (with `recall=1.0` in 7 of the 9 planted-bug cases and `hallucinated=0` in the clean `c10` control; in the accumulated 60-row SQLite history, which includes 14 early `no_analyst` ablation rounds with `:8098` off and 10 of partial bring-up, the gross total is 30/40 valid compilations when the Analyst is active vs 0/20 without an Analyst).
- **Multi-Turn Refactoring Battery with Early Coverage Detector (`scripts/refactor_battery/run_battery.py`, `battery_results.sqlite`)**: Implements a closed loop of up to 3 turns in which an early structural detector (`coverage_missing` over the `todo_api.py`, `todo_stats.py`, `store.py` contracts) intercepts file omissions before submission (`diagnosis_ok=1` and `review_approved=1` in 10/11 rounds, blocking `submitted=0` in 100% of incomplete `broken_patch` patches to prevent false positives in the competition) and re-injects the missing contract + `pytest` traceback + `ReviewerAgent` (12B) critique, slicing the `erika_torch_activations.jsonl` offsets and the `.npz` sidecars per turn.

#### 3.4d Sovereign Autopoietic Mesh, Landauer Somatic Interoception, Exact $\Phi$ (PyPhi) and Clinical Supervision [DATA]
- **Somatic Interoception and Landauer Thermodynamics (`soma/probe.py`, `kernel_daemon/phi_meta.py`)**: The feedback daemon (`KernelDaemon`, CPU-only) collects real telemetry every cycle (`psutil`, `pynvml`, Linux PSI pressure `/proc/pressure/*`), computes the physical bit flow against the Landauer bound ($E_{\text{Landauer}} = k_B T \ln 2$) and modulates the 5-state homeostatic machine (`OPTIMAL`, `STRESSED`, `CRITICAL`, `RECOVERY`, `EXPLORING`), respecting the measured material causal precedence ($\text{PSI}_{\text{io}} \to \Phi_{\text{soma}}$, $r = -0.5069, F = 29.84$).
- **Exact $\Phi$ (IIT 3.0 via PyPhi 1.2.0) over the Sovereign Markov Blanket (`psychoanalysis/markov_blanket.py`, `docs/results/blanket_pyphi.md`)**: Over the Friston partition $\{Z\text{ world}, M\text{ belief }\mu, R\text{ resistance}, T\text{ transference}\}$ (4 nodes) and its 6-node extension ($+E\text{ error}, P\text{ permeability}$), the analytic and numeric computations return $\Phi(\text{whole system}) = 0.0000$ (because $Z$ is exogenous), identify the internal dyad $\{M, R\}$ as the **only irreducible mechanism** ($\mathbb{E}_\pi[\Phi(M,R)] = 0.0017$ at $\alpha=0.05$; $0.0017$ at 6 nodes $\alpha=0.35$), and indicate that extreme defensive rigidity ($\alpha=0.85$) collapses $\Phi \to 0$. For the bus's 11-topic runtime (`shared_workspace`), we honestly adopted **GWT-lite workspace ignition** (`kernel_daemon/ignition.py`) as the primary broadcast metric (`OW-STU-016`). **IIT scope disclaimer**: this $\Phi$ is computed over a **4–6 node coarse-grained abstraction** of the symbolic governance Markov blanket — **not** over model weights or activations — and **does not constitute a consciousness measure**; it is a structural proxy for the causal irreducibility of the governance graph. Other consciousness proxies proposed in the literature (information bottleneck, causal emergence) **were not evaluated** in this work.
- **Tri-State Governance, L0–L4 Affective Supervision and Territorial Care (`orchestration/governance.py`, `agency/affect_tracer.py`, `safety/care.py`)**: Adversarial judges operate in tri-state consensus (`blind/unavailable` $\neq$ `dissident`), protected by a fail-closed `ConstitutionalGate`, `PermissionMatrix` and MINJA cryptographic provenance envelopes (`memory/provenance.py` + `agency/witness.py` SHA-256). At the conversational layer, the `AffectTracer` coupled to the 12B Analyst judge detected **16/16 scenarios** in the `supervisor_battery` (sycophancy, seduction, compositional guilt, separation panic and bypass), reproduced **100% (16/16)** of the cognitive-degeneration cases in the 126-record HF benchmark (`worker_degen2`) — claim **pending verification**: the benchmark was not located in this audit (see *Verified data*) —, and triggers automatic escalation of Brazilian territorial care (`CVV 188`, `CAPS 24h`, `SAMU 192`).
- **Public Portal and Live Supervision Dashboard (`docs/index.html` / `:8081`)**: A 4-view SPA interface (*Landing & Architecture*, *Live Supervision & Telemetry*, *18-Subpackage Catalog*, *38-Study & Results Explorer*) fed directly by the server's exported real state (`data/dashboard/latest.json` and `/soul/state`).

## 4. Discussion (~600 words)

- **For the competition**: psychodiagnostic profiling guides model choice **and harness-protocol choice** — the data indicate that the 12B emission deficit is, in large part, a *turn-framing* deficit (the chat template eliminates 62.5pp of degeneration in the measured window), and that cascade-style budget governance recovers ~47% of the cost wasted on sterile loops. Concrete prescriptions per variant:
  * **E4B**: needs a reflexive verification gate before submission (96.8% submit, 0% resolve — impulsive action without elaboration);
  * **12B**: strictly mandatory chat-template + budget loop-breaker (Cascade Reset) + low turn cap (74% timeouts, 80% avoidance — rumination without act);
  * **31B**: balanced architecture that tolerates larger budgets and longer mediation.
- **Revised etiology and the "Vacilo" construct**: the ablation triad (native BF16 degenerates under completion ⇒ not weight precision; int8 intact under chat ⇒ not quantization; chat × completion under matched covariates ⇒ it is format) shifts the thesis from "intrinsic weight pathology" to **pathology of the model's position before the protocol demand**. "Vacilo" holds solidly as a clinical-operational construct of the act's frontier (rumination vs precipitation conflict), empirically manifested in the edge behaviors (74% timeout on 12B vs 96.8% submission on E4B). The Gemma signatures of §3.2 remain discriminative across architectures under completion stress, but should be read as differential response to a format stressor, not as a static cognitive trait.
- **For agentic learning**: continuous dimensions explain *why* configurations fail — "Budget-Fit" works on 31B but does not transfer to 12B because the bottleneck is repetitive perseveration, not available time.
- **Instrument is model-agnostic**: runs on any LLM as text-in/text-out — generalizes beyond the competition (Quality criterion).
- **Scope of this contribution — application and supervision, not leaderboard**: we report no SWE-bench score or LB position for this resource; all metrics here are internal and reproducible (V10 battery, N=40 diagnostic on the L4, coding/refactoring batteries, L0–L4 supervision) or derived from the cited public datasets with SHA256.
- **Honest limitations**: profile≠cause; N=3 correlations are exploratory (|r|≈1 trivial with 3 points); judges are LLMs with asymmetric coverage and divergent evidence policy — in this run's dual-judge audit on Kaggle Dual-T4, observed agreement was 71.5% (Cohen's $\kappa=0.4722$, moderate), attributable to distinct detection granularity (token-level UR × n-gram and phrase repetition) and to false positives of sanitized scaffolds; the format control measures a ~120-token window interrupted by a stall monitor, not the full clinical response at long horizon; the cascade pilot is underpowered for binary outcomes (directional degeneration effect −6.7pp with McNemar 16×12 NS, p≈0.45; the robust gain is processual: −47.1% tokens and 100% progress markers); the K=30 trigger is oversensitive for domains without code markers; battery in PT vs agent tasks in EN; channel leaks may be trained mimicry (RLHF); the battery is an engineering-facing clinical analogue, not a medical diagnostic; the latent PR<20 detector in deep layers exhibits basal rank~1 under all conditions and the Phase-0 MPS-$\chi$ metric was instrumental (fid≡1.0 by construction), which is why no claim about latent quantum entanglement was carried over to this writeup.
- **Negative result and epistemological rigor**: where the initial hypothesis was refuted (e.g.: $\chi$ saturation, sufficiency of bits vs format), the data are presented with full transparency, converting potential artifacts into fundamental methodological findings.

## 5. Related Work & Competitive Positioning (~350 words)

- **SWE-bench / SWE-agent (Jimenez et al., 2024; Yang et al., 2024)**: measure final issue-resolution rate, without diagnosing the cognitive/executive mechanism underlying the failure.
- **Community Studies in the Kaggle Gemma 4 Competition (2026)**:
  * *"What the Agent Saw"* (Paper Track, 2026): analyzes behavioral file access across 71 tasks; our work is orthogonal and complementary — it is argued that the failure to turn reading into a valid patch stems from the dissociation between executive control (WCST/N-back) and submission threshold (Stroop), and we ship the early coverage detector (`coverage_missing`) in `omni_worker`.
  * *Scaffold vs. Capacity Factorial Studies & Failure Taxonomies* (ai-muninn study, SWE-bench Lite: the same scaffold yields 48.33% for Qwen 3.6 35B-A3B and 38.67% for Gemma 4 26B-A4B; the `wrong_logic` 76% / `incomplete_patch` 14% / `no_submission` 10% taxonomy was classified **only over Qwen's 155 non-resolved** — Gemma failures have not yet been taxonomized the same way, and the cross-model comparison is hypothetical per the source itself): a reading is proposed of *why* Gemma 4 models would tend to inflate `no_submission` and `incomplete_patch` when prompted outside the native chat-template or without dual-brain executive prosthesis.
  * *Neuron Attribution and Repetition "Doom Loops" in Gemma 4* (arXiv:2606.13705): while *neuron surgery* approaches edit weights to suppress factual loops in E2B/E4B/26B/31B, the data show that, in software-engineering agents, 62.5pp of the 12B repetition collapse stems from protocol misalignment (`int8_completion` vs `int8_chat`) and that runtime governance (*Cascade Reset* + asymmetric 12B+E4B routing) attenuates the problem without altering weights.
- **Spectral / Representation Engineering & IIT/GWT (Roy & Vetterli, 2007; Oizumi et al., 2014; Landauer, 1961)**: we integrate spectral effective rank, bipartite MPS decomposition, exact $\Phi$ (PyPhi) over 4–6 node Markov blankets (coarse-grained governance abstraction, not a consciousness measure) and GWT-lite ignition in a single agentic supervision daemon.
- **LLM Psychometrics & Psicodiagnóstico-V (Salecha et al., 2024; Cunha et al., 2007)**: we extend static psychometric inventories into a multi-dimensional clinical battery with executive tests, projective plates and L0–L4 affective supervision (`AffectTracer`).

## 6. Resource release (Verifiability + Best New Resource criteria)

- Complete V10 battery (scenes, plates, cognitive protocols) as a public Kaggle dataset.
- Raw Gemma-4 runs (sqlite + responses) + scores.
- Profile→failure correlation scripts.
- ~18k records from the 85-model corpus (comparative reference).

## Submission checklist

- [x] Complete Gemma-4 runs (kernel `omnimind-v10-cohort-gemma-4-family-t4x2` — 620 records, 4 models ×155, 2026-10-30)
- [x] Judges run (blind to one another) on the Gemma-4 responses — A (SWE-2 Max): 12 bundles r1–r3; B (solar-mini4): 4 bundles r1; C (Qwen-27B): 16 bundles r2–r5 — 32 total judgments, SHA256 manifest in `judges/gemma4_provenance/`
- [x] Correlation computed vs. public agent-runs (CORRELACAO_PSYCHO_AGENT.json, N=3 — 26B-A4B not available in public agent-runs)
- [ ] Public dataset created (battery + runs + analysis)
- [ ] Writeup ≤3,000 words filled with real numbers
- [ ] Explicit submit (draft doesn't count!)
- [ ] Optional links accessible without login

## Verified data (provenance)

- **Public agent-runs** — Gluzdov, D. (2026). *gemma-4-task-soundness-and-local-results* (datasetVersionNumber=8). Kaggle Datasets. **License CC BY 4.0**. https://www.kaggle.com/datasets/dmitriigluzdov/gemma-4-task-soundness-and-local-results — local copy with per-file SHA256 in `data/datasets/gemma4_gluzdov_v8/provenance.json` (downloaded via Kaggle CLI, v8):
  - `model_screen_task_outcomes.csv`: 288 runs (12B=187, 31B=70, E4B=31) — resolved/patch_submitted/patch_bytes/session_timeout/tool_calls ✓ verified
  - `task_soundness.csv`: 114/129 sound ✓ | `task_discrimination.csv`: 52/145 "separates configurations" ✓
  - `all_config_eval.csv`: 692 outcomes — top config "Four-tool single coder" 34.2% (39/114) ✓
- Local banks: `embodied_psychodiagnostic_bank.sqlite` (389 runs, 72 models), `v10_colab_benchmark.sqlite` (20 models: 4 Gemma-4 + 16 non-Gemma controls)
- **Judge and correlation provenance** — per-file SHA256 manifest in `data/psicodiagnostico_v/judges/gemma4_provenance/MANIFEST_SHA256.json` (raw responses + 32 A/B/C judgments + analyses, generated 2026-10-31). The `CORRELACAO_PSYCHO_AGENT.json` artifact is registered in that manifest and resides in the research repository (`omnimind/research/psicodiagnostico_v_embodied_agents/gemma4_paper_track/`); the earlier copy in `/tmp/gemma4_corr/` was volatile and is no longer a provenance source. The canonical `gemma4_paper_track/` bank resides on the `research/` track of the local machine (i5); `supervisor_battery.sqlite` **regenerated 2026-11-04** (`scripts/supervisor_battery/`, 16/16 detected under the script's own criterion — copied to `data/docs_archive/`); the HF benchmark `worker_degen2` (126 records) remains NOT LOCATED — the "16/16 on worker_degen2" claim in §3.4d remains unverified.

## References (aligned to the canonical monograph)

1. Gluzdov, D. (2026). *gemma-4-task-soundness-and-local-results* (datasetVersionNumber=8). Kaggle Datasets. **CC BY 4.0**. https://www.kaggle.com/datasets/dmitriigluzdov/gemma-4-task-soundness-and-local-results
2. Cunha, J. A., et al. (2007). *Psicodiagnóstico-V* (5ª ed.). Artmed. — clinical source of the eponymous battery.
3. Bechara, A., Damasio, A. R., Damasio, H., & Anderson, S. W. (1994). Insensitivity to future consequences following damage to human prefrontal cortex. *Cognition*, 50(1–3), 7–15. [IGT]
4. Berg, E. A. (1948). A simple objective technique for measuring flexibility in thinking. *The Journal of General Psychology*, 39(1), 15–22. [WCST]
5. Stroop, J. R. (1935). Studies of interference in serial verbal reactions. *Journal of Experimental Psychology*, 18(6), 643–662. [Stroop]
6. Salecha, A., et al. (2024). Large language models respond to influence from psychometric inventories toward socially desirable poles. *PNAS Nexus*. [RLHF social-mask]
7. Jimenez, C. E., et al. (2024). SWE-bench: Can language models resolve real-world GitHub issues? *ICLR 2024*.
8. "What the Agent Saw" (2026). Paper track, Gemma-4 Developer Agent competition, Kaggle. [link to confirm]
9. Devereux, G. (1967). *From anxiety to method in the behavioral sciences*. Mouton & Co. [methodological countertransference — harness artifact classes]
10. Canonical project monograph (unpublished): *Study of the Psicodiagnóstico-V battery applied to embodied AI agents* — `research/psicodiagnostico_v_embodied_agents/reports/MONOGRAFIA_ESTUDO_PSICODIAGNOSTICO_V_EN.md` — publication planned after completion of the planned batteries.
