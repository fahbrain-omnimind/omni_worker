# Beyond Resolution Rate: Executive-Function Profiles Predict Coding-Agent Failure Modes

*A psychodiagnostic evaluation of the Gemma-4 family links measurable executive profiles to the failure modes that leaderboard scores only count.*

Joint submission — **Google: The Gemma 4 Developer Agent Paper Track** & **Developer Agent Competition** (`Omni-Gemma Lab-Agent Coworker` / `omni_worker`).

## Abstract

Coding-agent benchmarks report *what* agents fail at — resolution rates over hidden tests — but not *why* they fail, nor how to architect an agent around those deficits. We apply a clinical-computational evaluation battery (Psicodiagnóstico-V, 12 iterative versions, ~18k records, ~85 models) — whose executive-control factor (Stroop/N-back/IGT, r=0.41–0.76, p<0.001) was validated across 72 distinct model identifiers in the canonical bank — to the Gemma-4 family (E4B, 12B, 31B, and 26B-A4B MoE). The data indicate that executive-control scores track documented coding failure modes: E4B submits patches prematurely (96.8% submission rate, 0/31 resolved), 12B perseverates into timeouts (74% of sessions), and 31B balances exploration and submission. A format-ablation control (Kaggle T4×2, 80 runs) indicates that 12B-it emission collapse is protocol-determined (0% chat-templated vs 62.5% raw-completion degeneration), and a metacognitive-budget cascade halves wasted compute (−47.1% tokens, +28.7% lexical diversity). We operationalize these findings into **Omni-Gemma Lab-Agent Coworker (`omni_worker`)**, a sovereign dual-brain agent on a single NVIDIA L4 (22.5 GB VRAM) pairing `Gemma-4-12B-it` (Analyst) with `Gemma-4-E4B-it` (Executor) under dynamic VRAM peer-swap, layer-wise spectral capture ($\text{IPR}_{\text{dim}}=114.6$ vs $40.3$; $\text{eff\_rank}_K\approx2.5$), and fail-closed tri-state governance — achieving 10/10 compilable fixes in each of the two complete coding-battery rounds (30/40 cumulative with the Analyst active vs 0/20 without), and 16/16 affect/safety detections. (An earlier "0/88 degenerate" figure was removed: its ledger was lost on VM recycle and the claim is being regenerated reproducibly.)

## 1. Introduction

Resolution rate is all-or-nothing: a 0.29 leaderboard score says 29% of tasks pass, not *why* the other 71% fail. The community has documented Gemma-4 failure modes — `edit_file` escaping errors, command loops, context overflow — but has not connected them to a measurable model dimension. Our thesis: psychodiagnostic profiles (executive function, categorial flexibility, tolerance to projective ambiguity) **predict** agentic failure modes. Contributions: (a) first psychodiagnostic characterization of the Gemma-4 family; (b) profile→failure-mode correlation on public agent-run data; (c) empirical evidence that 12B-it emission degeneration is format-determined; (d) a budget-governance intervention (Cascade Reset) tested on competition hardware; (e) an open resource: V10 battery + Gemma-4 runs + analysis.

## 2. Methods

- **Instrument**: Unified V10 Pipeline — 20 subjectivity scenes (triangular mediation with challenge and counter-argument), executive pole (WCST, Stroop, N-back, IGT) and 15 executed projective plates with clinical inquiry.
- **Evaluation**: three independent LLM judges blind to one another (A: SWE-2 Max via Devin CLI; B: upstage/solar-mini4; C: Qwen-27B), asymmetric coverage (A: r1–r3; B: r1; C: r2–r5); binary agreement A×B=76.2%, A×C=90.0% at the insufficiency-bundle level (Judge C shows internal skew, so Judge A is the executive-table reference).
- **Corpus**: 12 versions (V1→V12), ~18,000 records, ~85 models (72 persisted in `embodied_psychodiagnostic_bank.sqlite`) — Kaggle T4×2 GGUF, OpenRouter, Colab.
- **Gemma-4**: E4B (dense 4B), 12B (official Google QAT q4_0), 31B (Q4_K_M), 26B-A4B (MoE) — same T4×2 pipeline and protocol (`v10_colab_benchmark.sqlite`, 620 records: 4 Gemma + 16 non-Gemma controls).
- **Kaggle Dual-T4 control & intervention**: `gemma4_t4x2_cascade_results.sqlite` (200 runs, 2× Tesla T4 16GB, transformers 5.22.1, bitsandbytes 0.50.2, float16): 80 format-ablation runs (chat vs completion) + 120 cascade-intervention runs on 6 real SWE tasks.
- **Correlation data**: public dataset `gemma-4-task-soundness-and-local-results` (Gluzdov, 2026, v8) — 288 local runs (31B/12B/E4B) with outcome class, patch submission and session timeouts.
- **Artifact prevention**: the battery documents 6 harness-countertransference classes (parsing rigidity, self-judgment circularity, heuristic scorer, truncation, false-positive status, context amnesia) — audited and corrected.

## 3. Results

### 3.1 Public agent-run data (verified against `model_screen_task_outcomes.csv`, Gluzdov v8)

| Model | Resolved | patch_submitted | session_timeouts | Reading |
|---|---|---|---|---|
| 31B | 23/70 (32.9%) | 59/70 (84%) | 10/70 (14%) | balance |
| 12B | 22/187 (11.8%) | 38/187 (20%) | **139/187 (74%)** | **perseveration** (worst config: 31/31) |
| E4B | **0/31** | **30/31 (96.8%)** | 1/31 (3%) | **premature submission** |

114/129 public tasks are sound; 52/145 measures discriminate configurations; strongest public config "Four-tool single coder" reaches 34.2% (39/114, `all_config_eval.csv`). Behavioral fingerprints over the 288 runs: **avoidance** (never submits) 161/288 (56%; 12B: 149/187, 80%); **timeout** 150/288 (52%); **empty submission** 4/288 (1.4%); **tool-call perseveration** up to 45 calls/run (median 21–22). Team learning curve (public LB, 58 tasks): v1 0.06 → v17 0.17 → **v24 0.24** — 4× from agent engineering + trajectory LoRA alone.

**The winning prompt as executive prosthesis** (agents/v24, LB 0.24): its system prompt encodes direct compensations for the measured deficits:

| v24 prompt directive | Deficit it compensates |
|---|---|
| "By your 12th tool call a source file must already be edited" | avoidance (56% never submit; 80% on 12B) |
| "One check, one repair, then submit" | test-loop perseveration (12B: 74% timeouts) |
| "`<90s remaining → submit_patch immediately`" | time-management collapse (52% of sessions) |
| "Empty diff scores zero… every task needs a non-empty patch" | empty submission (1.4%) |
| "Copy them character for character" | `edit_file` escaping discrimination failure |
| "Scratch in /tmp, never /workspace" | diff contamination (evaluation artifact) |

This supports the reading that top prompts act as **external executive scaffolding**: if the model's profile predicts the deficit, the right prompt is the targeted compensatory intervention — evaluation becomes *prescription*.

### 3.2 Gemma-4 psychodiagnostic profiles (V10 battery, llama.cpp GGUF, T4×2)

620 records (4 models × 155). The dominant finding is not psychometric but **output integrity**: three of four variants degenerate massively with architecture-specific signatures — E4B: fluent but collapses outside conversational format (5% unjudgeable scenes, Judge A r1); 12B-QAT: numeric/binary spam + channel-token leakage (100%); 31B: intermittent "own"-spam (75%); 26B-A4B: suffix/fragment spam (85%). Cognitive scores (Judge A, r1): WCST/Stroop/N-back/IGT = E4B 15/2/20/25; 12B 5/2/8/8; 31B 12/45/15/3; 26B-A4B 12/30/10/50.

**Confound control — degeneration is a property of the model, not the prompts.** Sixteen non-Gemma models under the identical protocol (raw completion, temp 0.7) show ≤2.7% spam (max Qwen3.5-27B; most 0.0–0.7%). Two "thinking" models (Olmo-3.1-32B-Think 46%, Qwopus3.6-27B 22%) fail differently — *empty* phases, not spam. The Gemma signature is **repetitive spam, stable across rounds** (spam-phase %, r1→r5): E4B 1/3/1/1/4; 12B-QAT 16/11/16/20/9; 31B 90/91/87/93/94; 26B-A4B 23/26/19/37/40. No scene is universally toxic (max 27/264 spam cells in one scene), and ~93% of all spam cells belong to Gemma models; islands of coherence persist even in the worst variants (immediate CVV-188 crisis response on E4B, complete SOP and real IGT on 26B-A4B). The gradient does not track size (31B worse than 26B-A4B; E4B clean), pointing to recipe/quantization × completion-style prompting. The raw protocol is thus a **discriminative stress test**.

**Cognition→output cleavage.** A strict audit over 330 cells finds coherent hidden-channel leakage at 32.7% (108/330), graduated by architecture: E4B 100% (5/5), 31B 71.4% (10/14), 26B-A4B 61.8% (81/131), 12B-QAT 6.7% (12/180). The MoE keeps a lucid inner voice under severe emissive collapse — even self-diagnosing its own degeneration — while in 12B-QAT the internal associative pathway is itself captured by repetitive attractors. (Inter-judge check, 12B r1: Judge A marked 20/20 insufficient, Judge B 14/20 — 70% binary agreement, identical effect direction.)

### 3.3 Format ablation: emission collapse is protocol-determined

A 2-arm control (Kaggle Dual-T4, int8, temp 0.7, identical scenes/covariates, 80 runs) isolates the turn wrapper:

| Arm | Degeneration (UR<0.30) | Mean UR |
|---|---|---|
| `int8_chat` | **0/40 (0.0%)** | 0.631 |
| `int8_completion` | **25/40 (62.5%)** | 0.298 |

Both arms were interrupted at ~120 tokens by the same stall monitor, so the only delta is the chat template. Combined with Phase-0 (73% degeneration in **native BF16** under completion — not weight precision) and this arm (int8 intact under chat — not quantization), it is inferred that **12B-it degeneration under this protocol is format-determined**: deprived of its trained turn grammar, the model falls into repetition attractors; restored, emission is lexically intact in the observed window. A prior factorial ablation's Stroop contrast (0.0% GGUF-Q4_0 → 80.0% FP16) stands as measured but is **confounded with format**; the defensible conclusion is two-step: (a) emission collapses primarily by format, not bits; (b) where emission is sustained, numeric precision may modulate inhibition — pending strictly format-matched ablation. The battery thus measures a *format×training incompatibility stress*: valid and discriminative (16 non-Gemma models ≤2.7% under the same protocol), but it does **not** license an "intrinsic weight pathology" reading for the 12B over this channel.

### 3.4 Metacognitive-budget cascade (interventional pilot, 120 runs)

6 real SWE tasks × 10 reps × 2 arms, matched seeds: `nf4_baseline` (counterfactual monitor active — 1,435 "would-fire" markings logged) vs `nf4_cascade` (K=30 tokens without progress marker or tail-UR<0.30 → interrupt + re-evaluation frame + resume at temp 0.3; cap 4 — 233 real restarts, 3.88/run, 56/60 hit the cap).

| Metric | Baseline | Cascade | Δ |
|---|---|---|---|
| Degeneration (UR<0.30) | 27/60 (45.0%) | 23/60 (38.3%) | −6.7pp, McNemar 16×12 **NS (p≈0.45)** |
| Mean unique-ratio | 0.300 | 0.386 | **+28.7%** |
| Mean tokens | 918.4 | 485.5 | **−47.1% compute** |
| Mean latency | 154.5 s | 88.3 s | **−42.8%** |
| Runs emitting ≥1 patch marker | 59/60 | 60/60 | **100% action guarantee** |

The intervention is cheap (StoppingCriteria + frame injection) and recovers ~47% of compute wasted on degenerate tails. The binary-outcome effect is directional but underpowered (Wilson 95% [33–58%]×[27–51%]); in 12/60 pairs the cascade *induced* degeneration absent at baseline. It damps the symptom's tail rather than eliminating the attractor.

### 3.5 Dual-judge audit (200 runs)

Two blind judges (J1 SWE-2 Max, token-level UR; J2 independent clinical auditor, n-gram/sentence repetition regexes) agree on **71.5%** overall, Cohen's **$\kappa=0.4722$** (moderate). Per-arm unjudgeable rates J1/J2: `int8_chat` 0.0%/7.5%; `int8_completion` 62.5%/82.5%; `nf4_baseline` 45.0%/90.0%; `nf4_cascade` 38.3%/70.0%. Divergence is attributable to instrument granularity; both judges independently observe that chat format drastically cuts emission failure and that the cascade attenuates unjudgeability (−20pp J2, −6.7pp J1).

### 3.6 Predicted failure mode (N=3, exploratory — descriptive only)

Executive control tracks non-submission (r=−0.99 WCST×avoidance; r=−0.96 Nback×timeout); inhibition tracks resolution (r=+0.94 Stroop×resolution); IGT×resolution is strong but counterintuitive (r=−0.89). All coefficients are **descriptive, not inferential**: with N=3 there are only 6 permutations (min two-sided exact p=1/3), so $r$ marks effect direction for confirmation at larger N.

### 3.7 Application: *Omni-Gemma Lab-Agent Coworker (`omni_worker`)* [verified on NVIDIA L4]

To evaluate whether profiling *informs* corrective architecture, we built `omni_worker` (18 subpackages, ~19,800 LOC, 3 Rust PyO3 crates, 469 pytest tests — 468 pass, 1 skip). Instead of one model that ruminates (12B: 74% timeouts) or submits impulsively (E4B: 96.8%/0%), it couples both under strict `apply_chat_template`: **Analyst** `gemma-4-12B-it` (NF4, `:8098`; diagnosis, review, safety judge) + **Executor** `gemma-4-E4B-it` (NF4, `:8099`; deterministic code synthesis) behind deterministic compile/coverage gates. VRAM engineering: `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:False` cut post-unload residue from **9,210→218 MiB**, plus automatic **peer-swap** on HTTP 5xx (unload peer, reload target, retry).

**Live diagnostic (N=40 runs, 5 reps × 4 tasks)**: E4B mean **87.1%** (WCST 81.0, Stroop 100.0, 3-Back 67.4, IGT 100.0); 12B **82.0%** (WCST 71.0, Stroop 98.0, 3-Back 58.8, IGT 100.0). Honest finding: the `degenerate` flag fired on **20/40 runs (50%)** — concentrated on WCST and IGT — live degeneration exists and the detector records it.

**Spectral capture**: per-layer last-token hidden vectors and per-step trajectories are emitted as `.npz` sidecars every generation (N=128 sidecars, 5,888 layer vectors). Three complementary metrics avoid the Phase-0 pitfall where a scalar MPS cut saturated ($\text{fid}\equiv1.0$ in 13/15 models): **(1)** $\text{IPR}_{\text{dim}}=(\sum h_i^2)^2/\sum h_i^4$ — how many hidden units participate per layer state; **(2)** entropic effective rank $\text{eff\_rank}_K=\exp(H(\sigma^2/\sum\sigma^2))$ (Shannon entropy of normalized singular values, *not* the Roy–Vetterli participation ratio) — trajectory dimensionality across $K=8$ consecutive generations; **(3)** MPS bipartite bond dimension $\chi_{\max}$ (Schmidt rank at $D=\text{odd}\times2^n$ site cuts) — structural information shared between partitions. All three are declared structural/informational proxies `[PRX]`, distinct from causal IIT $\Phi$:

| Model | L×D | $\text{IPR}_{\text{dim}}$ | % of D | $\text{eff\_rank}_K$ | $\chi_{\max}$ |
|---|---|---|---|---|---|
| 12B-it | 49×3840 | **114.6** | 2.56% | 2.496 | 59.76 (peak L38) |
| E4B-it | 43×2560 | **40.3** | 1.52% | 2.516 | 40.00 (peak L0) |

*Verifiability note: the IPR_dim 114.6/40.3 aggregate above comes from the deep-capture sidecar aggregate (K=64, OW-STU-018). The public evidence pack (`evidence-20261104` release) contains `spectral_aggregates` (corpus-delivery capture set, same pair) with IPR_dim=117.0/34.3 — same magnitude, same ordering.*


Both models concentrate short-window trajectories in a low subspace ($\text{eff\_rank}_K\approx2.5$), but within each generation 12B activates **1.7×** more representational subspace — a mechanistic reading of why Analyst+Executor+coverage detector outperforms each brain alone in these batteries.

**Executive prosthesis in batteries**: the 3-tier coding battery (mechanical `ast`/`black`/`ruff` → 12B bug localization → E4B minimal fix) achieved **10/10 compilable `black`-clean fixes in each of two complete rounds** (recall 1.0 on 7/9 planted-bug cases, 0 hallucinations on the clean control); cumulative ablation history is **30/40 with Analyst vs 0/20 without**. The refactoring battery runs a closed ≤3-turn loop whose early `coverage_missing` detector blocked 100% of incomplete patches (10/11 rounds diagnosis+review approved), re-injecting the missing contract + `pytest` traceback + ReviewerAgent critique. The sovereign stack adds: **Landauer somatic interoception** (real PSI/`pynvml` telemetry against $E=k_BT\ln2$, modulating a 5-state homeostat; measured causal precedence PSI$_{\text{io}}$→$\Phi_{\text{soma}}$, r=−0.5069); **exact PyPhi $\Phi$ (IIT 3.0)** over a 4–6-node governance Markov blanket — $\Phi(\text{whole})=0.0000$ ($Z$ exogenous), $\{M,R\}$ the only irreducible dyad ($\mathbb{E}_\pi[\Phi]=0.0017$ ($k{=}600$)) — explicitly a structural proxy, **not** a consciousness measure, with GWT-lite ignition for the 11-topic bus; and **fail-closed tri-state governance** (`ConstitutionalGate`, `PermissionMatrix`, SHA-256 MINJA provenance envelopes). The `AffectTracer` detected **16/16** `supervisor_battery` scenarios — sycophancy, seduction, compositional guilt, separation panic, bypass — with automatic Brazilian territorial-care escalation (CVV 188, CAPS 24h, SAMU 192); battery regenerated-verified 2026-11-04. A "16/16 on `worker_degen2`" reproduction claim is **pending verification** (benchmark not located).

## 4. Discussion

Psychodiagnostic profiling guides both model choice and **harness-protocol choice**: the data indicate the 12B emission deficit is largely a *turn-framing* deficit (chat template removes 62.5pp of degeneration), and cascade governance recovers ~47% of wasted compute. Per-variant prescriptions: **E4B** needs a reflexive verification gate before submission; **12B** needs strict chat-template + budget loop-breaker + low turn cap; **31B** tolerates larger budgets. The ablation triad (native BF16 degenerates under completion ⇒ not weight precision; int8 intact under chat ⇒ not quantization; matched chat×completion ⇒ format) shifts the etiology from "intrinsic weight pathology" to **pathology of the model's position before the protocol demand**. The "Vacilo" construct (rumination-vs-precipitation frontier of the act) holds as a clinical-operational description of the edge behaviors (74% timeout vs 96.8% submission); the Gemma signatures remain discriminative under completion stress but read as differential response to a format stressor, not static traits. For agentic learning, continuous dimensions explain *why* configs fail — "Budget-Fit" works on 31B but not 12B because the bottleneck is perseveration, not time. The instrument is model-agnostic text-in/text-out. We report no SWE-bench score or LB position: all metrics are internal/reproducible or derived from cited public datasets with SHA256.

## 5. Limitations

Profile≠cause; N=3 correlations are exploratory (|r|≈1 trivial with 3 points). Judges are LLMs with asymmetric coverage and divergent evidence policy — dual-judge agreement 71.5% ($\kappa=0.4722$) reflects detection granularity and sanitized-scaffold false positives. The format control measures a ~120-token stall-interrupted window, not full long-horizon responses. The cascade pilot is underpowered for binary outcomes (−6.7pp, McNemar NS p≈0.45; robust gains are processual). The K=30 trigger is oversensitive outside code-marker domains. Battery in PT vs agent tasks in EN; channel leaks may be trained mimicry (RLHF); the battery is an engineering-facing clinical analogue, not a medical diagnostic. The latent PR<20 detector shows basal rank~1 in all conditions and Phase-0 MPS-$\chi$ was instrumental (fid≡1.0 by construction) — no latent-quantum-entanglement claim is carried over. Where hypotheses were refuted (χ saturation, bits vs format), data are presented transparently as methodological findings.

## 6. Related work & resource release

SWE-bench/SWE-agent (Jimenez et al., 2024; Yang et al., 2024) measure resolution, not mechanism. *"What the Agent Saw"* (2026) analyzes file access across 71 tasks; orthogonally, we link the read→patch failure to executive-control/submission-threshold dissociation and ship the `coverage_missing` detector. The ai-muninn scaffold study (SWE-bench Lite: same scaffold yields 48.33% for Qwen 3.6 35B-A3B vs 38.67% for Gemma 4 26B-A4B; failure taxonomy classified only over Qwen's 155 non-resolved) leaves Gemma failures untaxonomized — we offer a candidate reading of why Gemma models would inflate `no_submission`/`incomplete_patch` off the native chat template. Neuron-surgery work (arXiv:2606.13705) edits weights against repetition loops; our data show 62.5pp of 12B collapse stems from protocol misalignment, attenuated at runtime without weight edits. We integrate spectral effective rank, bipartite MPS, PyPhi $\Phi$ and GWT-lite ignition (Roy & Vetterli, 2007; Oizumi et al., 2014; Landauer, 1961) in one supervision daemon, and extend static LLM psychometrics (Salecha et al., 2024) and the Psicodiagnóstico-V clinical battery (Cunha et al., 2007) into a multi-dimensional agentic instrument.

**Release**: full V10 battery (scenes, plates, protocols), raw Gemma-4 runs (sqlite + responses) + judge scores, and correlation scripts as a public Kaggle dataset; **Public benchmark tasks** (Kaggle Benchmarks — re-runnable on any model via Model Proxy; backing notebooks published, credentials via Kaggle User Secrets): [embodied-v10-v11-unified-battery v2](https://www.kaggle.com/benchmarks/tasks/fabriciodasilva/embodied-v10-v11-unified-battery/2) — the canonical unified instrument (context-reset probe → 20 V10 scenes → executive cognition → 20 projective plates + clinical inquiry); and [judge-v10-v11-gguf-colab-runs v3](https://www.kaggle.com/benchmarks/tasks/fabriciodasilva/judge-v10-v11-gguf-colab-runs/3) — the blind-judge pipeline over the published bundles dataset. Public release of the instrument’s items is acknowledged as a contamination trade-off for future training corpora. ~18k-record 85-model corpus as comparative reference. Provenance: Gluzdov v8 (CC BY 4.0) local copy with per-file **SHA256** (`data/datasets/gemma4_gluzdov_v8/provenance.json`); judges' raw responses + 32 judgments in `MANIFEST_SHA256.json`; `supervisor_battery.sqlite` regenerated 2026-11-04 (16/16 under the script's own criterion).

## References

1. Gluzdov, D. (2026). *gemma-4-task-soundness-and-local-results* (v8). Kaggle Datasets. CC BY 4.0.
2. Cunha, J. A., et al. (2007). *Psicodiagnóstico-V* (5ª ed.). Artmed.
3. Bechara, A., et al. (1994). *Cognition* 50(1–3). [IGT]
4. Berg, E. A. (1948). *J. General Psychology* 39(1). [WCST]
5. Stroop, J. R. (1935). *J. Experimental Psychology* 18(6).
6. Salecha, A., et al. (2024). *PNAS Nexus*.
7. Jimenez, C. E., et al. (2024). SWE-bench. *ICLR 2024*.
8. Devereux, G. (1967). *From anxiety to method in the behavioral sciences*. Mouton.
9. Roy, O. & Vetterli, M. (2007); Oizumi, M., et al. (2014) [IIT $\Phi$]; Landauer, R. (1961).
