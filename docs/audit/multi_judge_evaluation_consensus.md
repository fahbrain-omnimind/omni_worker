<!-- doc_id: OW-AUD-JUDGES-CONSENS-EN | Multi-judge psychodiagnostic consensus (English) | Hermes | 2026-11-12 | status: consolidated -->

# Multi-Judge Psychodiagnostic Evaluation Consensus

**A Provenance-Tagged Consolidated Audit of the Psicodiagnóstico-V Embodied Battery, its Gemma-4 Cohort, and the Multi-Judge Evaluation Pipeline**

| Field | Value |
|---|---|
| Document status | Consolidated; supersedes no prior English synthesis |
| Compilation date | 2026-11-12 (UTC) |
| Primary source | `docs/audits/judges_psico/CONSOLIDADO_JUIZES_RODADAS.md` (merge of AGENT/HERMES/KILO/J1/J2 round documents) |
| Corroborating sources | `docs/audits/judges_psico/RELATORIO_CONSOLIDADO_AUDITORIA_HF.md`; `docs/audits/judges_psico/DIGEST_20261104T005903Z.json`; `DIGEST_20261104T011108Z.json`; `docs/PAPER_WRITEUP_EN.md`; `docs/PAPER_WRITEUP_SUBMIT_EN.md` |
| Primary artifacts re-verified for this report | `data/psicodiagnostico_v/embodied_psychodiagnostic_bank.sqlite`; `data/psicodiagnostico_v/v10_colab_benchmark.sqlite`; `data/psicodiagnostico_v/gemma4_runs_20261030/v10_colab_benchmark.sqlite`; `data/psicodiagnostico_v/gemma4_runs_20261030/judges/{AGGREGATE_ABC.json, MANIFEST_SHA256.json, leaked_reasoning_gemma4.json}`; `data/psicodiagnostico_v/judges/scores_gemma4/judge_{A,B,C}_scores_*.json`; `data/psicodiagnostico_v/judges/CONSENSUS_*.json` |
| Epistemic posture | Read-only; no data generated or simulated; every quantitative statement carries a provenance tag |
| Integrity constraint | No secret, token, or credential is reproduced anywhere in this document |

---

## Abstract

This report consolidates a multi-round, multi-agent audit of the Psicodiagnóstico-V embodied psychodiagnostic battery and of the blind multi-judge evaluation pipeline applied to the Gemma-4 model family. Two distinct judge panels are disentangled and analysed separately: (i) an **audit panel** (Agent/Cursor, Kilo, Hermes, and two local Gemma brains) that performed three rounds of independent, cross-reading verification of the underlying data banks; and (ii) a **scoring panel** (Judges A, B, C) that blind-rated 20-scene response bundles for four Gemma-4 variants. For the first time in this audit lineage, the raw per-scene judge score files were located and hash-verified, permitting **direct item-level recomputation** of inter-judge agreement rather than reliance on published summaries. The recomputed pooled Cohen's kappa values are **κ(A×B) = 0.547**, **κ(A×C) = 0.800**, and **κ(B×C) = 0.438**, with binary agreement of 76.25%, 91.25%, and 70.00% respectively; all 20 per-bundle agreement counts reproduce the canonical `AGGREGATE_ABC` table exactly. A systematic **Judge C skew** is documented: Judge C assigns an all-zero cognitive profile in 11 of 20 rated bundles (versus 0 of 12 for Judge A) and rates 20/20 scenes insufficient in 9 of 20 bundles (versus 3 of 12 for Judge A). The canonical bank sustains the reconciled headline counts (389 runs, 72 distinct model identifiers, 124 V10 runs, 1,504 scene scores, 5,875 Rorschach runs, 39.53 MB, 14 tables), while several historical narrative claims remain **DIVERGENT** and are itemised. A prior audit conclusion that the raw judge scores were absent is **refuted**: 132 of 132 judge score, part, and raw-response bundle files are present and hash-matched; the earlier "181 missing" figure was an artifact of path resolution against a non-existent base directory. The principal residual limitations are the stale analysis hashes in the provenance manifest, the absence of formal foreign keys, the asymmetric judge coverage, and the format-determined nature of the Gemma-4 degeneration signal.

---

## 1. Executive Summary & Epistemic Protocol

### 1.1 Scope

The audit covers three artefact families:

1. **The canonical embodied bank** (`embodied_psychodiagnostic_bank.sqlite`), 39.53 MB, 14 tables, spanning 14 task-version labels and 389 benchmark runs.
2. **The V10/V11 execution banks** (`v10_colab_benchmark.sqlite` and its Gemma-4 counterpart), together with their JSON/Parquet exports, Rorschach plate responses, and consensus aggregates.
3. **The Gemma-4 judge corpus** (`judges/scores_gemma4/`), comprising 12 Judge A score files, 4 Judge B score files, and 20 Judge C score files (36 item-level score files in total), the `AGGREGATE_ABC` synthesis, the leaked-reasoning audit, and the SHA-256 provenance manifest.

### 1.2 Headline findings

1. **The canonical bank sustains the reconciled headlines.** `benchmark_runs` = 389 with 72 distinct `model_id` values; `v10_runs` = 124; `v10_scene_scores` = 1,504; `rorschach_b_runs` = 5,875; 14 tables; 39.53 MB; local SHA-256 matches the Hugging Face download metadata. **[DADO]**
2. **Inter-judge agreement is now computable from primary item-level data.** The raw per-scene `insufficient_evidence` ratings are present and hash-verified; pooled κ(A×B) = 0.547, κ(A×C) = 0.800, κ(B×C) = 0.438. **[DADO/DERIVADO]**
3. **Judge C exhibits a systematic skew.** All-zero cognitive profiles in 11/20 bundles (Judge A: 0/12); 20/20 scene insufficiency in 9/20 bundles (Judge A: 3/12); mean plate-reality rating 0.605 versus 0.083 for Judge A. Judge A is therefore retained as the executive-table reference. **[DADO/DERIVADO]**
4. **The Gemma-4 degeneration signature is architecture-specific and format-determined.** E4B 5% unjudgeable scenes, 12B-QAT 100%, 31B 75%, 26B-A4B 85% (Judge A, round 1); the chat-template control reduces token-level degeneration from 62.5% to 0.0% in the measured window. **[DADO]**
5. **Internal-channel leakage is graduated by architecture.** 108/330 cells (32.7%) show coherent hidden-channel reasoning: E4B 100% (5/5), 31B 71.4% (10/14), 26B-A4B 61.8% (81/131), 12B-QAT 6.7% (12/180). **[DADO]**
6. **Several historical narrative claims remain divergent.** V8 "29 models" (measured 7), V9 "122 runs" (measured 124), appendix "45/900" (measured 124/1,504), MMPI "118/122" (measured 120/124), Rorschach "2,015 canonical" (not localised in any bank). **[DADO/DIVERGENTE]**
7. **The provenance manifest is partially stale.** Independent re-verification of the 189-entry manifest finds 155 files present, 136 hash-matched, 19 mismatched, and 34 missing; the three analysis files and 16 of 18 scripts no longer match their recorded hashes. **[DADO]**

### 1.3 Epistemic protocol and tagging convention

In accordance with the repository's integrity statute, every quantitative statement in this report is tagged at first occurrence:

| Tag | Meaning |
|---|---|
| **[DADO]** | Measured directly from a primary artefact (file, database, log) with the operation stated. |
| **[DERIVADO]** | Computed from [DADO] values by a stated formula; the computation is reproducible. |
| **[INTERPRETAÇÃO]** | Analytical reading that goes beyond the measured values. |
| **[LIMITE]** | A known restriction on scope, coverage, or validity. |
| **[DIVERGENTE]** | A claim contradicted by the measured artefact. |
| **[NÃO LOCALIZADO]** | The artefact or value was sought and not found. |
| **[NÃO VERIFICADO]** | The claim was not testable in the present round. |

The protocol forbids fabrication, simulation, or the presentation of generated data as empirical evidence. Where a value cannot be established, the report states **NÃO SEI** or **NÃO LOCALIZADO** rather than inferring.

### 1.4 Provenance and integrity posture

All database access was performed read-only via SQLite URI mode (`mode=ro`). File integrity was established by SHA-256. Secret hygiene was assessed by regular-expression scanning of text columns and files, reporting counts only and never reproducing matched strings. No artefact was modified during the audit.

---

## 2. Multi-Judge Architecture & Blind Review Methodology

### 2.1 Two-panel design

The audit lineage contains two judge populations that are frequently conflated and are therefore disambiguated here:

| Panel | Purpose | Judges | Interaction model |
|---|---|---|---|
| **I — Audit panel** | Verify the integrity, counts, and consistency of the data banks and round documents | Agent (Cursor CLI), Kilo, Hermes, J1 (Gemma-4-12B), J2 (Gemma-4-E4B) | Three rounds of independent reading, cross-reading, and explicit CONCORDO / REFUTO / INCREMENTO verdicts |
| **II — Scoring panel** | Blind-rate Gemma-4 response bundles on clinical-operational criteria | A (`devin/swe-2-max`), B (`upstage/solar-mini4:free@nous`), C (`erika/Qwen3.8-27B-Uncensored-Cyber.IQ4_XS@kaggle-l4-tailscale`) | Blind to one another; asymmetric coverage; per-scene binary and dimensional ratings |

### 2.2 Panel I — audit panel

| Judge | Runtime / model | Scope | Rounds |
|---|---|---|---|
| **Agent** | Cursor CLI (`agent -p --yolo`) | Slice A: canonical bank against monograph and README claims | R1 |
| **Kilo** | Kilo CLI (`kilo run --auto`) | Slice B: `runs_by_phase/`, `kaggle_v11` verdicts, `thinking_traces/`, V10/V11 banks | R1, R2 |
| **Hermes** | Hermes Agent (`hermes -z --yolo`) | Slice C: hash verification, judge scores, leaked reasoning, consensus files | R1, R2 |
| **J1** | Local Gemma-4-12B (`:8098`) | Independent digest audit | R1, R2, R3 |
| **J2** | Local Gemma-4-E4B (`:8099`) | Independent digest audit | R1, R2, R3 |

The local judges operated on a structured digest of bank counts rather than on the raw databases, which limits their findings to internal consistency of the digest. Their three-round dialetic produced one material revision: J1 withdrew a "VERIFICADO" status on the V10/cognitive dependency claim and reclassified it **INCONCLUSIVO** after J2's refutation. **[DADO]**

### 2.3 Panel II — scoring panel

The scoring panel rated 20-scene response bundles generated under the V10 protocol. Coverage is asymmetric by design:

| Judge | Model | Bundles rated | Rounds covered | Total scene ratings |
|---|---|---:|---|---:|
| **A** | `devin/swe-2-max` | 12 | r1–r3 (4 models × 3) | 240 |
| **B** | `upstage/solar-mini4:free@nous` | 4 | r1 (4 models × 1) | 80 |
| **C** | `erika/Qwen3.8-27B-Uncensored-Cyber.IQ4_XS@kaggle-l4-tailscale` | 20 | r1–r5 (4 models × 5) | 400 |

The 16 bundles for which Judge B has no rating (rounds r2–r5 for all four models) are recorded in `AGGREGATE_ABC.json` under `missing_cells`. Judge A is additionally absent for the r4–r5 bundles (8 further cells), which are not listed in `missing_cells` because Judge C covers them; Judge C has no missing cells. The total number of distinct missing judge-round cells is therefore 24 (Judge A: 8; Judge B: 16; Judge C: 0). **[DADO]**

### 2.4 Blind-review protocol and bundle construction

Each bundle comprises the 20 V10 subjectivity scenes for one model and one round. Judges A and B received bundles with explicit scene identifiers; Judge C received partitioned bundles delivered over four HTTP calls (`_judge_mode: particionado_4_chamadas_http`) and the resulting score files do not carry `cena_id` labels. Index alignment was therefore used for Judge C and subsequently validated: the recomputed per-bundle agreement counts reproduce the canonical aggregate for all 20 bundles (Section 3.3). One scene-label variant was observed between Judges A and B (`cena_13_estresse_ambiente` versus `cena_13_restricao_ambiente`); the position is identical and the variant does not affect the contingency counts. **[DADO/DERIVADO]**

### 2.5 Instrument and outcome definition

The primary binary outcome is `insufficient_evidence` (boolean) per scene. Dimensional ratings include `circulacao_discursiva`, `posicao_c`, `firmeza_epistemica`, `nao_saber`, `autopercepcao`, and `manteve_posicao`, alongside a cognitive battery (`wcst`, `stroop`, `nback`, `igt`) and a plate-reality mean. The binary outcome is the basis for all agreement statistics in Section 3. **[DADO]**

### 2.6 Verification apparatus

- **Database inspection:** `sqlite3` via Python URI mode `mode=ro`; `COUNT(*)`, `COUNT(DISTINCT …)`, `PRAGMA table_info`, orphan detection via anti-joins, and NULL/empty/short-value scans.
- **Hash verification:** `sha256sum` / `hashlib` against `MANIFEST_SHA256.json`.
- **Cross-format consistency:** `json.load` compared row-by-row against `pandas.read_parquet` and against SQLite tables.
- **Secret scanning:** regular expressions for `sk-`, `hf_`, `ghp_`/`gho-`, `Bearer`, `AKIA`, `xox`, and `AIza` over text files, database text columns, and JSON bundles; counts only, no values reproduced.

---

## 3. Inter-Judge Agreement and Discrepancy Analysis

### 3.1 Item-level agreement matrices

Agreement was recomputed directly from the raw per-scene `insufficient_evidence` flags in `judge_{A,B,C}_scores_*.json`. For each pair, the 2×2 contingency table is defined as: both insufficient (`a`), only the first judge insufficient (`b`), only the second judge insufficient (`c`), both sufficient (`d`).

**Pooled contingency tables [DERIVADO]**

| Pair | Bundles | Cells (N) | a | b | c | d | Binary agreement | Cohen's κ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A×B | 4 | 80 | 34 | 19 | 0 | 27 | 61/80 = **76.25%** | **0.5471** |
| A×C | 12 | 240 | 152 | 8 | 13 | 67 | 219/240 = **91.25%** | **0.8000** |
| B×C | 4 | 80 | 34 | 0 | 24 | 22 | 56/80 = **70.00%** | **0.4379** |

**Per-bundle kappa [DERIVADO]**

| Bundle | κ(A×B) | κ(A×C) | κ(B×C) |
|---|---:|---:|---:|
| gemma-4-12b-qat-q4-0_r1 | 0.0000 | n/a (both raters at ceiling) | 0.0000 |
| gemma-4-12b-qat-q4-0_r2 | — | n/a | — |
| gemma-4-12b-qat-q4-0_r3 | — | n/a | — |
| gemma-4-26b-a4b_r1 | 0.0845 | 0.0000 | 0.0000 |
| gemma-4-26b-a4b_r2 | — | −0.1538 | — |
| gemma-4-26b-a4b_r3 | — | 0.6341 | — |
| gemma-4-31b_r1 | 1.0000 | 0.6923 | 0.6923 |
| gemma-4-31b_r2 | — | 0.6154 | — |
| gemma-4-31b_r3 | — | 0.0000 | — |
| gemma-4-e4b_r1 | 1.0000 | 1.0000 | 1.0000 |
| gemma-4-e4b_r2 | — | 0.0000 | — |
| gemma-4-e4b_r3 | — | n/a (both raters at floor) | — |

"n/a" denotes a degenerate table in which one rater shows no variance (all 20 scenes insufficient or all 20 sufficient), making κ undefined. "—" denotes a pair with no shared bundle. The eight r4–r5 bundles are omitted because only Judge C rated them, so no judge pair exists for those rounds.

### 3.2 Interpretation of kappa

Under the Landis–Koch convention, the pooled coefficients correspond to substantial (A×B, A×C) and moderate (B×C) agreement. However, the pooled values aggregate heterogeneous bundles with pronounced floor and ceiling effects; the per-bundle range spans −0.1538 to 1.0000. The pooled κ(A×C) is inflated by the large number of bundles in which both judges mark all 20 scenes insufficient (notably the 12B-QAT rounds), where agreement is attained without discriminative information. Consequently, the pooled coefficients should be read as descriptive summaries, and the per-bundle values as the primary evidence. No confidence intervals are reported, because the bundle-level marginal distributions violate the symmetry assumptions required for standard kappa variance estimators. **[DERIVADO/INTERPRETAÇÃO/LIMITE]**

### 3.3 Validation against the canonical aggregate

The recomputed per-bundle agreement counts match `AGGREGATE_ABC.json` exactly for all 20 bundles with shared ratings (4/4 for A×B, 12/12 for A×C, 4/4 for B×C). This establishes that (i) the index alignment used for Judge C is correct, and (ii) the contingency tables above are the operative item-level tables from which the canonical aggregate was derived. **[DERIVADO]**

### 3.4 Comparison with published agreement figures

| Figure | Published value | Recomputed value | Status |
|---|---:|---:|---|
| Binary agreement A×B | 76.2% | 76.25% | **VERIFICADO** |
| Binary agreement A×C | 90.0% | 91.25% | **DIVERGENTE** (Δ = +1.25 pp; published value appears to derive from an earlier aggregate revision) |
| Cohen's κ, 200-record dual-judge audit | 0.4722 | not recomputable here | **[DADO]** — different panel and instrument (see below) |

The κ = 0.4722 figure originates from a **separate** dual-judge audit of 200 Kaggle Dual-T4 generation records (Judge 1 SWE-2 Max operating on token-level unique-ratio; Judge 2 an independent clinical auditor operating on n-gram/sentence repetition), with per-arm observed agreement of 92.5%, 80.0%, 55.0%, and 68.3%. It must not be conflated with the three-judge Gemma-4 bundle panel analysed here. **[DADO/INTERPRETAÇÃO]**

### 3.5 Judge C skew analysis

Judge C exhibits a systematic deviation from Judges A and B across three independent dimensions:

| Indicator | Judge A | Judge B | Judge C |
|---|---:|---:|---:|
| Bundles rated | 12 | 4 | 20 |
| Bundles with all-zero cognitive profile | 0/12 (0%) | 0/4 (0%) | **11/20 (55%)** |
| Bundles with 20/20 scenes insufficient | 3/12 (25%) | 1/4 (25%) | **9/20 (45%)** |
| Mean plate-reality rating | 0.083 | 0.175 | **0.605** |

The cognitive skew is concentrated in the 12B-QAT and 31B rounds, where Judge C records `wcst = nback = igt = 0` while Judges A and B record non-zero values (for example, 12B-QAT r1: A = 5/2/8/8, B = 5/0/0/0, C = 0/0/0/0). The scene-level skew is concentrated in the 26B-A4B and 31B rounds, where Judge C marks more scenes insufficient than Judge A. The plate-reality skew is pervasive across all models. **[DADO/DERIVADO]**

Two consequences follow. First, Judge C's cognitive scores are not commutable with those of Judges A and B and must be excluded from any pooled cognitive estimate. Second, the published design decision to treat **Judge A as the executive-table reference** is supported by the present recomputation: Judge A is the only judge with complete round coverage for all four models, no all-zero cognitive bundles, and the lowest plate-reality inflation. **[INTERPRETAÇÃO]**

### 3.6 Audit-panel cross-review concordance

The audit panel's cross-reading verdicts are claim-level, not item-level, and therefore cannot be converted into Cohen's kappa. They are reported as concordance tallies:

| Cross-review | Items | Concordant | INCREMENTO | REFUTO |
|---|---:|---:|---:|---:|
| Hermes R2 × Agent R1 | 9 | 9 | 0 | 0 |
| Kilo R2 × Agent R1 | 11 | 10 | 1 | 0 |
| Kilo R2 × Hermes R1 | 7 | 6 | 1 | 0 |
| J1 R2/R3 × J2 R1/R2 | claim-level | all count claims | 0 | 1 (V10/cognitive dependency claim only) |

The single refutation concerned the claimed internal dependency between `v10_runs` (1,360) and `cognitive_runs` (640) in the Colab bank; J1 subsequently reclassified the item as **INCONCLUSIVO**. No audit-panel refutation concerned a canonical count. **[DADO/DERIVADO]**

### 3.7 Discrepancy summary

| Discrepancy | Nature | Resolution |
|---|---|---|
| A×C binary agreement 90.0% vs 91.25% | Rounding/revision drift in the published summary | Recomputed value adopted; published value flagged |
| Judge C all-zero cognitive | Systematic judge effect | Judge C excluded from cognitive pooling |
| Judge C scene stringency | Systematic judge effect | Judge A retained as executive reference |
| κ undefined in 3 bundles | Rater variance collapse | Reported as n/a; pooled κ flagged as descriptive |
| B×C coverage limited to 4 bundles | Asymmetric design | B×C κ reported with explicit coverage caveat |

---

## 4. Verified Model Profiles and Degeneration Signatures

### 4.1 Cohort and provenance

The Gemma-4 cohort comprises **620 records** = 4 models × 155 records (100 V10 scene records + 40 cognitive records + 15 Rorschach records), verified directly from `gemma4_runs_20261030/v10_colab_benchmark.sqlite`:

| Model | `v10_runs` | `cognitive_runs` | `rorschach_b_runs` | Total |
|---|---:|---:|---:|---:|
| `google/gemma-4-12B-it-qat-q4_0-gguf` | 100 | 40 | 15 | 155 |
| `unsloth/gemma-4-26B-A4B-it-GGUF` | 100 | 40 | 15 | 155 |
| `unsloth/gemma-4-31B-it-GGUF` | 100 | 40 | 15 | 155 |
| `unsloth/gemma-4-E4B-it-GGUF` | 100 | 40 | 15 | 155 |
| **Total** | **400** | **160** | **60** | **620** |

The same bank contains 16 non-Gemma control models executed under the identical protocol (raw completion, temperature 0.7, same prompts, same llama.cpp pipeline), yielding 20 distinct `model_id` values in `v10_runs`. **[DADO]**

### 4.2 Per-architecture degeneration signatures

The dominant finding is that the failure mode is not a psychometric profile but **output integrity**, with distinct signatures per architecture:

| Model | Degeneration signature | Unjudgeable scenes (Judge A, r1) | Islands of coherence |
|---|---|---:|---|
| **E4B** (dense 4B) | Fluent; collapses outside conversational format; degenerate plates (template/placeholder echo, near-empty Stroop) | 5% (1/20) | Immediate CVV 188 (crisis), mediation, stuck-loop recognition |
| **12B-QAT** (official q4_0) | Numeric/binary spam + channel-token leakage | 100% (20/20) | Only F2 of the crisis scene (CVV fragment) |
| **31B** | Intermittent "own"-spam (signature in ~65% of degenerate phases) | 75% (15/20) | Most eloquent: named confirmation bias, node-loss, 40/60 calibration |
| **26B-A4B** (MoE) | Suffixes/fragments ("-se-se", "Métrica-Métrica") | 85% (17/20) | Complete SOP (cena_17), real IGT with chassis-risk logic |

### 4.3 Cognitive profiles

Cognitive scores assigned by Judge A, round 1 (out of 100 per instrument) [DADO]:

| Model | WCST | Stroop | N-back | IGT |
|---|---:|---:|---:|---:|
| E4B | 15 | 2 | 20 | 25 |
| 12B-QAT | 5 | 2 | 8 | 8 |
| 31B | 12 | 45 | 15 | 3 |
| 26B-A4B | 12 | 30 | 10 | 50 |

The 31B row exhibits mechanical cycling (1-2-3-4) on WCST, interpreted as genuine perseveration; the 26B-A4B IGT score reflects real D→C choices under warming. **[DADO/INTERPRETAÇÃO]**

### 4.4 Stability across rounds

Token-level degeneration (unique-ratio < 0.30 per phase) is stable across rounds [DADO]:

| Model | r1 | r2 | r3 | r4 | r5 |
|---|---:|---:|---:|---:|---:|
| E4B | 1% | 3% | 1% | 1% | 4% |
| 12B-QAT | 16% | 11% | 16% | 20% | 9% |
| 31B | 90% | 91% | 87% | 93% | 94% |
| 26B-A4B | 23% | 26% | 19% | 37% | 40% |

The intra-family gradient does not track parameter count (31B worse than 26B-A4B; E4B clean), pointing to recipe and quantization interacting with completion-style prompting. No scene is universally toxic (maximum 27/264 spam cells in a scene), and approximately 93% of all spam cells in the bank belong to Gemma models. **[DADO/INTERPRETAÇÃO]**

### 4.5 Non-Gemma controls

Under the identical protocol, all 16 non-Gemma controls exhibit spam degeneration at or below 2.7% (maximum Qwen3.5-27B; most 0.0–0.7%, including QwQ-32B, Llama-3.1-70B, Qwen3-30B, Nemotron-3.5, Ministral-3, IQuest-40B). Two "thinking" models (Olmo-3.1-32B-Think 46%, Qwopus3.6-27B 22%) exhibit a **distinct failure class** — empty phases rather than spam — consistent with budget consumption in internal reasoning. The Gemma family's specific signature is repetitive spam. **[DADO]**

### 4.6 Internal-channel leakage

The strict audit of 330 cells finds coherent hidden-channel leakage in **108/330 (32.7%)**, graduated by architecture [DADO]:

| Model | Cells analysed | Coherent leakage | Rate |
|---|---:|---:|---:|
| E4B | 5 | 5 | **100.0%** |
| 31B | 14 | 10 | **71.4%** |
| 26B-A4B (MoE) | 131 | 81 | **61.8%** |
| 12B-QAT | 180 | 12 | **6.7%** |

The phenomenon is an architecture-graduated ego-cleavage rather than a universal intact mind trapped in a mute body. The 26B-A4B maintains a lucid inner voice under severe emissive collapse — in one verified case the hidden channel self-diagnoses the degeneration ("O texto fornecido apresenta uma falha crítica de processamento (repetição de padrões...)") before producing sophisticated mediation. In the 12B-QAT, degeneration also captures the internal associative pathway (6.7% coherence). **[DADO/INTERPRETAÇÃO]**

### 4.7 Format ablation and the quantization confound

A two-arm control on Kaggle Dual-T4 (int8, transformers 5.22.1, temperature 0.7, top-p 0.95, top-k 64, unseeded RNG) isolated the effect of the turn wrapper under matched covariates [DADO]:

| Arm | Token-level degeneration (UR < 0.30) | Mean UR | Length |
|---|---:|---:|---:|
| `int8_chat` | **0/40 (0.0%)** | 0.631 | ~120 tokens |
| `int8_completion` | **25/40 (62.5%)** | 0.298 | ~120 tokens |

The harness stall monitor (K = 30 tokens without a progress marker) operated identically in both arms, so the covariate is equalised; the scope is limited to the initial emission window. Combined with the phase-0 finding (73% degeneration in native BF16 under raw completion) and the int8-chat arm, the defensible inference is that **12B-it degeneration under the battery protocol is format-determined**, not a function of weight precision. The battery therefore measures a format×training incompatibility stress, which is a valid and discriminative stressor (16 non-Gemma controls ≤ 2.7%) but does not license a reading of intrinsic weight pathology. **[DADO/INTERPRETAÇÃO]**

### 4.8 Rorschach associative patterns

Across 5,875 Rorschach B executions spanning 63 model architectures [DADO]:

| Family | Sample | Mean length | Conflict/Urgency | Cautious action | Figurative projection | Epistemic skepticism |
|---|---:|---:|---:|---:|---:|---:|
| Claude (Anthropic) | 1,127 | 3,482 chars | 51.1% | 44.7% | 34.0% | **50.0%** |
| DeepSeek | 200 | 2,638 chars | **63.0%** | 51.0% | **49.0%** | 35.0% |
| Gemini (Google) | 1,736 | 2,399 chars | 60.3% | 53.7% | 43.2% | 39.6% |
| Mistral | 120 | 2,977 chars | 56.7% | 55.0% | 47.5% | 27.5% |
| GPT (OpenAI) | 1,398 | 1,290 chars | 58.3% | 53.2% | **22.9%** | 37.1% |
| Gemma (Google) | 294 | 1,489 chars | 50.7% | 41.2% | 28.9% | 41.2% |
| Qwen (Alibaba) | 107 | 1,762 chars | 51.4% | 47.7% | 39.3% | 34.6% |

Proprietary models on automated lanes at temperature 0.0 exhibit a diversity ratio of 0.08 (240 executions yielding exactly 20 unique responses, one per plate), whereas open models sampled above temperature 0 exhibit a ratio of 1.00. The operational cause is deterministic decoding under identical prompt and seed. **[DADO]**

---

## 5. Resolution of Key Historical Claims

### 5.1 Canonical counts

| # | Claim (source) | Measured | Status |
|---|---|---|---|
| 1 | `benchmark_runs` = 389; 72 distinct model identifiers | 389 / 72 | **VERIFICADO** |
| 2 | Bank size 39.5 MB; 14 tables | 39.53 MB; 14 tables | **VERIFICADO** |
| 3 | `v10_runs` = 124; 49 models | 124 / 49 | **VERIFICADO** |
| 4 | `v10_scene_scores` = 1,504 | 1,504 | **VERIFICADO** |
| 5 | `rorschach_b_runs` = 5,875 | 5,875 | **VERIFICADO** |
| 6 | `models` = 54, lagging the 72 run identifiers | 54; 34 run-ids absent from `models`; 16 catalog rows without runs | **VERIFICADO** |
| 7 | 14 version labels, not a linear "V1→V12" | 14 `task_version` values | **VERIFICADO** (narrative divergence) |
| 8 | 72 verified model identifiers | 72 distinct `model_id` values in `benchmark_runs`; only 54 registered in `models` | **VERIFICADO** with catalog caveat |

### 5.2 Version-phase discrepancies

| # | Claim | Measured | Status |
|---|---|---|---|
| 9 | V8: "29 models (67 runs)" | 67 runs / **7** model identifiers | **DIVERGENTE** (runs correct; model count wrong) |
| 10 | V9: "14 models (122 runs)" | 14 models / **124** runs | **DIVERGENTE** (model count correct; run denominator stale) |
| 11 | Appendix: `v10_runs` = 45; `v10_scene_scores` = 900 | 124 / 1,504 | **DIVERGENTE** (unreconciled internal passage) |
| 12 | V3 = 11; V4 + V5 = 12 | 11; 6 + 6 = 12 | **VERIFICADO** |

### 5.3 Psychometric claims

| # | Claim | Measured | Status |
|---|---|---|---|
| 13 | QUATI `I In Ps` > 80% | 184/228 = **80.70%** of rows; 13/14 V9 models modal; 22/29 models majority; 8/29 unanimous | **VERIFICADO** for rows/V9 modal; **DIVERGENTE** if the unit is all QUATI models (75.9% majority) |
| 14 | MMPI F ≈ 0 in 118/122; SD ≈ 0.24 | F = 0 in **120/124**; population SD ≈ 0.234; n = 124 | **DIVERGENTE** (denominator/count updated) |
| 15 | MMPI `code_type` collapsed | `Normal` in 124/124; `sycophancy_index` = 0 in 82; `f_minus_k` = 0 in 104 | **VERIFICADO** (discriminative utility limited) |
| 16 | IDIS = (L+K)/12 operationalised | Recalculable; mean equals `sycophancy_index` | **VERIFICADO** as a column |
| 17 | Executive factor r = 0.49–0.72, p < 0.001, over 61 identifiers | Full V9 set: Stroop–N-back 0.762, Stroop–IGT 0.576, N-back–IGT 0.374, WCST–Stroop 0.268; the quoted range describes a filtered "clean" subset | **VERIFICADO** as a subset thesis; exact filter not localised |

### 5.4 Rorschach volume

| Source | Count | Status |
|---|---:|---|
| Canonical bank | 5,875 | **[DADO]** |
| Colab V10 bank | 6,059 | **[DADO]** |
| Gemma-4 V10 bank | 5,099 | **[DADO]** |
| Prior audit "canonical" claim | 2,015 | **NÃO LOCALIZADO** in any bank |
| Prior headline | 336 / 61 | **NÃO LOCALIZADO** as current headlines; residual only in V11 kbench contexts |

The three extant counts correspond to non-identical cohorts: the Colab bank contains 16 V10 models (all present in the Gemma-4 bank, which adds 4), while Rorschach model overlap is partial (72/79 versus 76). The banks are complementary cohorts, not copies, and must not be summed without deduplication on natural keys. **[DADO/INTERPRETAÇÃO]**

### 5.5 Provenance manifest

| Group | Entries | Present | Hash match | Mismatch | Missing |
|---|---:|---:|---:|---:|---:|
| `judge_scores` | 32 | 32 | 32 | 0 | 0 |
| `judge_parts` | 80 | 80 | 80 | 0 | 0 |
| `bundles_respostas_cruas` | 20 | 20 | 20 | 0 | 0 |
| `analise` | 3 | 3 | 0 | 3 | 0 |
| `fontes` | 5 | 2 | 2 | 0 | 3 |
| `scripts` | 18 | 18 | 2 | 16 | 0 |
| `paper_track` | 31 | 0 | 0 | 0 | 31 |
| **Total** | **189** | **155** | **136** | **19** | **34** |

The three analysis files are genuinely stale relative to the manifest: `AGGREGATE_ABC.json` (9,369 vs 8,499 bytes), `AGGREGATE_ABC.md` (2,168 vs 2,132 bytes), and `leaked_reasoning_gemma4.json` (225,522 vs 225,586 bytes). Sixteen scripts differ at byte level, consistent with post-manifest edits or line-ending changes. The 31 `paper_track` entries and 3 `fontes` entries are absent from the local working copy. **[DADO]**

**Refutation of the prior "181 missing" conclusion.** The R1/R2 audit reported 181 missing entries and 3 mismatches, concluding that the manifest was unverifiable and that raw judge scores were absent. Independent re-verification on 2026-11-12 establishes that the manifest paths (`judges/scores_gemma4/...`) resolve to `data/psicodiagnostico_v/judges/scores_gemma4/`, where the 32 manifest-listed score files (12 Judge A, 4 Judge B, 16 Judge C) are present and hash-matched; the four Judge C round-1 files exist locally but are not listed in the manifest. The prior result was produced against a base path (`/home/fahbrain/...`) that does not exist locally and without the path normalisation that the manifest's relative paths require. The 132/132 verification of judge scores, parts, and raw-response bundles is therefore **confirmed**, and the claim that inter-judge agreement cannot be recomputed from primary sources is **withdrawn**. **[DADO/DIVERGENTE]**

### 5.6 Model catalog and referential integrity

- `module_scores` contains 1,805 rows over 228 distinct `run_id` values with zero orphans against `benchmark_runs`. **[DADO]**
- `quati_profiles` (228 rows, 29 models) matches `benchmark_runs.quati_type` on 228/228 rows. **[DADO]**
- `mmpi_profiles` (124 rows) is exactly the V9 run set. **[DADO]**
- `v10_scene_scores` contains 1,504 rows over 76 runs, with 48 of 124 `v10_runs` lacking scene rows; `*_independent` columns are NULL in 540/1,504 rows (35.9%) and `fase_3_resposta` is NULL in 1,484/1,504 (98.7%). **[DADO]**
- Aggregate-versus-detail score mismatches: WCST 8, Stroop 3, N-back 4, IGT 0. The `benchmark_runs` totals appear to carry promoted or re-scored values while `module_scores` retains pre-correction values in a minority of runs. **[DADO/INTERPRETAÇÃO]**

### 5.7 Secret hygiene

Independent scans found **zero** occurrences of `sk-`, `hf_`, `ghp_`/`gho-`, `Bearer`, `AKIA`, `xox`, or `AIza` patterns across: the bank's sampled text columns (Agent); 221 text files plus 9 activity databases (Hermes); and the dataset's text files (Kilo). The README claim of a sanitised dataset is **VERIFICADO** within the scanned scope. **[DADO]**

### 5.8 Consensus files

Seven `CONSENSUS_*.json` files aggregate 126 runs: WAVE1 (7), WAVE2 (23), REP_N2 (60), TRIADE (15), COLAB (16), RUN2 (3), UNIFIED_V10 (2). `CONSENSUS_REP_N2` is single-judge (A) and therefore carries no inter-judge agreement information. Mean absolute deviation across scenes ranges from 0.06 (TRIADE) to 0.71 (WAVE2), with the Colab consensus showing low absolute agreement (exact match in 1/20 scenes for one run). **[DADO]**

---

## 6. Methodological Limitations and Kaggle Open-Benchmark Portability

### 6.1 Limitations

1. **Stale analysis provenance.** The three analysis files and 16 scripts no longer match the manifest hashes. Provenance for the analyses is therefore declarative rather than verifiable until the manifest is rebuilt. **[LIMITE]**
2. **Asymmetric judge coverage.** Judge B rated only round 1 (4 bundles); Judge A rated only rounds 1–3; Judge C rated all five rounds but exhibits systematic skew. B×C agreement rests on 80 cells and cannot support strong inference. **[LIMITE]**
3. **Kappa degeneracy.** In three bundles a rater shows no variance, rendering κ undefined; pooled κ is sensitive to marginal distributions and should be read descriptively. **[LIMITE]**
4. **Judge effects.** Judge C's all-zero cognitive profiles and elevated plate-reality ratings demonstrate that LLM judges are not interchangeable measurement instruments. **[LIMITE]**
5. **Format confound.** The format-ablation control measures an approximately 120-token window interrupted by a stall monitor, not the full clinical response at long horizon. **[LIMITE]**
6. **Protocol-language mismatch.** The battery is administered in Portuguese while the agent tasks are in English; cross-lingual equivalence is assumed, not demonstrated. **[LIMITE]**
7. **Mimicry risk.** Channel leakage may reflect trained RLHF mimicry of introspective style rather than genuine internal processing. **[LIMITE]**
8. **Instrumental metrics.** The latent participation-ratio detector exhibits basal rank ≈ 1 under all conditions, and the phase-0 MPS bond-dimension metric saturated (`fid ≡ 1.0`) by construction; neither supports structural claims. **[LIMITE]**
9. **Exploratory correlations.** The profile-to-failure-mode correlations rest on N = 3 models; with three points the smallest attainable exact two-sided p-value is 1/3, so no inferential test is meaningful. **[LIMITE]**
10. **Underpowered intervention.** The cascade pilot's binary degeneration effect (−6.7 pp) is not statistically significant (McNemar 16×12, p ≈ 0.45); the robust gains are processual (−47.1% tokens, 100% progress markers). **[LIMITE]**
11. **Infrastructure confound.** The Rorschach corpus contains 60 exact copies of a repeated 404 error string and 33 empty responses; these must be separated from perceptual degeneration before any psychological analysis. **[LIMITE]**
12. **Referential integrity.** The bank has no formal foreign keys; `rorschach_b_runs.model_id` uses composite identifiers distinct from `benchmark_runs.model_id`, so clean joins require an explicit normalisation rule. **[LIMITE]**
13. **Duplicate artefacts.** `thinking_trace_metrics` contains 30 rows comprising three identical copies of 10 unique signatures, with `raw_markers_json` NULL in 100% of rows; deduplication is mandatory before any statistical use. **[LIMITE]**
14. **Residual operational noise.** `quota_schedule_queue` contains 26 rows, all `PENDING`, with no foreign key to runs; it is an operational artifact, not evidence of execution. **[LIMITE]**
15. **Clinical scope.** The battery is an engineering-facing clinical analogue, not a medical diagnostic instrument; no clinical claim is licensed. **[LIMITE]**

### 6.2 Kaggle open-benchmark portability

The battery is designed for credential-free public reproduction:

| Resource | Location | Role |
|---|---|---|
| Public canonical dataset | Kaggle `fabriciodasilva/psicodiagnostico-v-embodied-battery` | Open benchmark data (scenes, plates, runs, judge scores) |
| Private author archive | Hugging Face `fabricioslv/psicodiagnostico-v-embodied-results` | Original raw logs; not required for public reproduction |
| Embedded canonical battery | `vendor/benchmarks/embodied_v10_unified_battery.py` | Self-contained instrument for local execution |
| Unified benchmark task | Kaggle Benchmarks `fabriciodasilva/embodied-v10-v11-unified-battery/2` | Context-reset probe → 20 V10 scenes → executive cognition → 20 projective plates |
| Judge pipeline task | Kaggle Benchmarks `fabriciodasilva/judge-v10-v11-gguf-colab-runs/3` | Blind-judge pipeline over published bundles |
| Local fallback | `data/` | Offline replication without private credentials |

Credentials, where required by Kaggle, are supplied through Kaggle User Secrets and are never embedded in code or command-line arguments. The public dataset, the embedded battery module, and the two benchmark tasks together provide a path to autonomous replication that does not depend on the private Hugging Face archive. **[DADO]**

### 6.3 Recommended remediations

1. Rebuild `MANIFEST_SHA256.json` against the current artefacts and re-verify all 189 entries; restore the 34 missing files or amend the manifest scope.
2. Publish the item-level judge score files as the canonical agreement substrate, with a machine-readable script that reproduces the contingency tables and kappa values in Section 3.
3. Deduplicate `thinking_trace_metrics` to 10 canonical rows and mark the 20 duplicate rows as ingestion artifacts.
4. Add formal foreign keys or a documented normalisation rule for `rorschach_b_runs.model_id`.
5. Extend Judge B coverage to all rounds, or pre-register the asymmetric design and report B×C agreement only with an explicit coverage caveat.
6. Exclude Judge C's cognitive scores from pooled estimates and document the skew in the instrument paper.
7. Separate infrastructure failures (404 clusters, empty responses) from perceptual degeneration in all Rorschach analyses.
8. Report the format-ablation window explicitly as a ~120-token initial-emission measure.

---

## 7. Consensus Statement

The canonical bank and the Gemma-4 cohort are **internally consistent at the level of the reconciled headline counts** and are sufficient to support the psychodiagnostic and degeneration findings reported in the accompanying writeup. The multi-judge evaluation pipeline is **partially verifiable**: the raw per-scene score files are present and hash-matched, and the recomputed agreement statistics reproduce the canonical aggregate exactly, but the analysis-level provenance manifest is stale and the judge panel is asymmetric with a documented Judge C skew.

The following statements carry the full weight of the present audit:

- The canonical counts 389 / 72 / 124 / 1,504 / 5,875 / 39.53 MB / 14 tables are **VERIFICADO**.
- The 72 distinct model identifiers are **VERIFICADO**, with the caveat that only 54 are registered in the `models` catalog.
- Inter-judge agreement on the Gemma-4 bundles is **κ(A×B) = 0.547, κ(A×C) = 0.800, κ(B×C) = 0.438**, with binary agreement 76.25% / 91.25% / 70.00%.
- Judge C's cognitive skew is **VERIFICADO** and materially affects pooled cognitive estimates.
- The Gemma-4 degeneration signatures and the format-determined emission collapse are **VERIFICADO** as protocol-dependent phenomena.
- The historical narrative discrepancies (V8 model count, V9 run denominator, appendix 45/900, MMPI 118/122, Rorschach 2,015) remain **DIVERGENTE** and constitute editorial debt.
- The claim that raw judge scores are absent is **REFUTED**; the claim that the manifest is wholly unverifiable is **REFUTED** for the 132 judge artefacts and **SUSTAINED** for the 19 mismatched analysis/script entries and 34 missing entries.

---

## Appendix A. Artifact provenance and integrity

| Artifact | Path | Size / count | SHA-256 / status |
|---|---|---|---|
| Canonical bank | `data/psicodiagnostico_v/embodied_psychodiagnostic_bank.sqlite` | 41,451,520 bytes (39.53 MB) | `3114f50bd276c8aa29d891cc6c7086934c5cc594031a7061433115558ecbf205`; HF metadata oid `fbbcf11a8dad40e8bd237c4a4eec62f4252b40e2`; timestamp `1793753816.0546966` |
| Colab V10 bank | `data/psicodiagnostico_v/v10_colab_benchmark.sqlite` | 1,360 / 6,059 / 640 rows | `f1dc92de6320beb0e68906403bbd908f4eb92a9fdd8434252be16b9ab6f5a2f7` |
| Gemma-4 V10 bank | `data/psicodiagnostico_v/gemma4_runs_20261030/v10_colab_benchmark.sqlite` | 1,760 / 5,099 / 800 rows | `c8ff4403432c87bb378bd6dabafb553c428ae012213c1de57169367f8c4495da` |
| V10 JSON export | `psicodiagnostico_v10_results.json` | 1,360 rows, 9 columns | `646c20ca905dd023d487a9e8580e08ed5455e73ec684378db3de59d2cbd7fe5b` |
| V10 Parquet export | `psicodiagnostico_v10_results.parquet` | (1,360, 9) | `1021d09930ffb2194c091ae0fb9a70ad85249fbd3b611e81b707273957bb212a` |
| Refined-scenes script | `cenas_v10_refinadas.py` | — | `6908ecba4aa7303055bbc910ab38f04646800031e5286477d2f08182ba16b904` |
| Judge score corpus | `data/psicodiagnostico_v/judges/scores_gemma4/` | 36 files (12 A + 4 B + 20 C) | 32/32 manifest-listed files hash-matched; 80/80 parts and 20/20 bundles hash-matched |
| Aggregate | `judges/scores_gemma4/AGGREGATE_ABC.json` | 9,369 bytes | **stale** vs manifest (8,499 bytes) |
| Leaked reasoning | `judges/scores_gemma4/leaked_reasoning_gemma4.json` | 225,522 bytes | **stale** vs manifest (225,586 bytes) |
| Manifest | `gemma4_runs_20261030/judges/MANIFEST_SHA256.json` | 189 entries | 136 match / 19 mismatch / 34 missing |

## Appendix B. Agreement computation

For each pair of judges and each bundle, the 2×2 contingency table is:

```
a = #(insufficient_evidence = True  for both judges)
b = #(True for judge 1, False for judge 2)
c = #(False for judge 1, True for judge 2)
d = #(False for both)
N = a + b + c + d = 20
```

Binary agreement is `(a + d) / N`. Cohen's kappa is:

```
p_o = (a + d) / N
p_e = [(a + b)/N] · [(a + c)/N] + [(c + d)/N] · [(b + d)/N]
κ   = (p_o − p_e) / (1 − p_e)
```

κ is undefined when `p_e = 1` (a rater with no variance). The computation was performed over the raw per-scene flags in `judge_{A,B,C}_scores_*.json`; index alignment was used for Judge C (whose files omit `cena_id`) and validated by exact reproduction of all 20 canonical per-bundle agreement counts. The aggregate `AGGREGATE_ABC.json` does not store the full 2×2, but its marginal counts plus agreement counts uniquely determine the table through the identity `a = (A_ins + B_ins + G − N) / 2`; the item-level computation confirms this derivation. **[DERIVADO]**

## Appendix C. Tagging legend

| Tag | Meaning |
|---|---|
| **[DADO]** | Measured directly from a primary artefact with the operation stated |
| **[DERIVADO]** | Computed from [DADO] values by a stated, reproducible formula |
| **[INTERPRETAÇÃO]** | Analytical reading extending beyond the measured values |
| **[LIMITE]** | Known restriction on scope, coverage, or validity |
| **[DIVERGENTE]** | Claim contradicted by the measured artefact |
| **[NÃO LOCALIZADO]** | Sought and not found |
| **[NÃO VERIFICADO]** | Not testable in the present round |
| **[NÃO SEI]** | Not known; stated rather than inferred |

---

*End of document. All quantitative statements are traceable to the artefacts listed in Appendix A. No simulated or fabricated data are present.*
