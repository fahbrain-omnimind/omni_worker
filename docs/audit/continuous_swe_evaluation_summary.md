# Continuous Basal vs. Modulated SWE Evaluation Summary

**Source document:** `docs/AUDITORIA_CONTINUA_BASAL_MODULADO_20261105.md` (continuous SWE audit, 5–10 min snapshots)
**Audited database:** `data/basal_vs_modulated_280turns_20261105.sqlite`
**Execution window:** 2026-11-05T13:53:23Z → 2026-11-05T16:42:43Z (280/280 turns complete)
**Evaluated systems:** `gemma-4-12B-it` (`:8098`, analyst) and `gemma-4-E4B-it` (`:8099`, executor)

**Provenance legend.** Claims are tagged per the repository epistemic statute: **[DADO]** measured/verified with source; **[DERIVADO]** computed from measured data; **[INTERPRETAÇÃO]** interpretation; **[LIMITE]** known limitation.

---

## 1. Executive Overview

A symmetric 280-turn SWE battery was executed and audited end-to-end: 70 `task_id` × 2 models × 2 phases = 140 BASAL + 140 MODULATED turns [DADO]. Integrity checks confirm 140/140 basal turns with `intervention_enabled=0`, T=0.200, ΔT=0, `INRC=OBSERVE_ONLY`, and 140/140 modulated turns with deterministic per-arm signatures; MPS probes are 100% intact (zero sentinel rows, zero NULLs) [DADO].

The principal findings are:

- **Regime-conditioned efficacy.** Modulation is neutral-to-favorable for the 12B in `v10_subjectivity` and neutral-to-adverse for the E4B; it is significantly beneficial in `v11_multiturn_series` for both models (contract drift ↓, 12B p=0.0013, E4B p=0.034; 12B lexical diversity ↑ p=0.0025) [DERIVADO]. It does not break template attractors in `cognitivo_executivo` (degenerate flags 2→2 in both models) and is heterogeneous in the SWE blocks [DERIVADO].
- **Deterministic chassis separability.** MPS IPR alone separates the two models perfectly (ROC-AUC = 1.000 inverted; disjoint intervals 12B [0.0456, 0.0862] vs E4B [0.1232, 0.2062]); motor velocity (0.977) and χ_eff (0.963) are near-perfect. The chassis signature is invariant to modulation [DERIVADO].
- **A common degeneration marker.** `PR_traj` collapse marks degenerate outputs across both chassis (AUC 0.067 inverted; median 7.75 vs 14.64), while secondary signals diverge by model [DERIVADO].
- **No net closed-loop advantage.** The M4 closed-loop gate did not outperform open-loop arms: the 12B-M4 kept 16/17 turns below gate with null median drift change; E4B-M4 produced 4/17 excursions. The `v11` benefit is shared by M2/M3/M4 [DERIVADO].

## 2. Testbed Setup & Conditions (Basal vs. Modulated)

### 2.1 Design and Phases

- **BASAL** (`basal_assistant` / `basal_executor`): pure observation, `intervention_enabled=0`, T=0.200, ΔT=0.000, `INRC=OBSERVE_ONLY`; captures MPS + motor layer + sovereign scales without injection [DADO].
- **MODULATED** (`M1..M4`): `intervention_enabled=1`; small temperature variances (ΔT), the Freud10D+INRC+Kuramoto arm, and a closed-loop MPS+motor gate anchored on the basal envelope [DADO].
- Both phases ran the identical 70-task battery per model; the basal envelope was locked at the BASAL→MODULATED transition (`compute_and_store_basal_envelope`) with n=70 per model [DADO].

### 2.2 Intervention Arms

| Arm | Mechanism | T (ΔT) | top_p | INRC operator(s) |
|---|---|---:|---:|---|
| M1 `scale_minus_delta` | open-loop temperature reduction | 0.13 (−0.07) | 0.85 | C |
| M2 `scale_plus_delta` | open-loop temperature increase | 0.28 (+0.08) | 0.94 | R |
| M3 `freud10d_inrc_kuramoto` | spectral/attractor modulation | 0.09 (−0.11) | 0.82 | R+C |
| M4 `closed_loop_mps_motor` | closed-loop gate anchored on basal envelope | 0.09–0.10 (−0.10/−0.11) | 0.82–0.84 | R+C |

The closed-loop selected only temperature reduction across the entire battery [DADO].

### 2.3 Battery Composition

| Stage | task_ids per model | Per-arm n (modulated) |
|---|---:|---:|
| `v10_subjectivity` | 40 | 10 |
| `cognitivo_executivo` (`wcst`, `stroop`, `nback`, `igt`) | 4 | 1 |
| `v11_multiturn_series` | 18 | 4–5 |
| `swe_competition` | 6 | 1–2 |
| `swe_ood45` | 2 | 1 |
| **Total** | **70** | — |

### 2.4 Basal Envelopes and M4 Gate Thresholds

| Field | E4B `:8099` (locked 15:03:53) | 12B `:8098` (locked 15:10:33) |
|---|---:|---:|
| χ_eff μ±σ | 15.757 ± 0.787 | 18.330 ± 1.381 |
| PR_traj μ | 16.459 | 11.402 |
| contract_drift μ±σ | 0.7814 ± 0.0843 | 0.8083 ± 0.0714 |
| IPR μ | 0.1663 | 0.0625 |
| Morphology μ | 0.6205 | 0.6187 |
| Motor velocity μ±σ | 256.86 ± 33.34 | 322.01 ± 26.00 |
| ‖h‖ μ | 193.87 | 210.38 |
| unique_ratio μ | 0.6294 | 0.5990 |
| Degenerate rate | 0.0286 (2/70) | 0.0571 (4/70) |
| **M4 gate** | drift > 0.8024 or vel < 218.33 | drift > 0.8262 or vel < 273.71 |

Independent recomputation over `battery_turns` reproduces the envelope fields with `np.mean`/`np.std` semantics (population σ, ddof=0) [DADO]+[DERIVADO].

### 2.5 Passive Sovereign Scales

Sovereign scales are bit-identical per turn across models (Ψ = 0.4868 constant; R_pair = 0.9947 ± 0.0008; R_triad = 0.9613; `regime_confidence` = 0.4259; `hopf_sr` = 1.1511; T2 = 86.66 h) [DADO]. They are host/dyad signals, not model discriminators, and serve as a shared temporal covariate [LIMITE]. Dynamic notes: `hopf_regime` transitioned `limit_cycle → chaotic` between turns 1–2 (ρ 1.138 → 1.152); `expectation_norm` decays monotonically (1.14 → 0.93) with `turn_idx` — both deterministic and arm-independent [DERIVADO].

### 2.6 Injection Cost

Prompt tokens +55–72 (M1/M2/M4) and +259 (M3) per turn vs basal homologues; `gen_tokens` ≈ 0; latency +8.8–18.2 s; `thinking_chars` = 0 in 280/280; `action_markers` > 0 only in `swe_*` stages (task attribute, not modulation) [DADO].

## 3. Key Findings across 280 Battery Turns

Convention: Δ = MODULATED − BASAL, paired by (model, `task_id`); sign counts ↓/↑; *gate* = excursions against the model's own basal envelope; p = Wilcoxon signed-rank where n ≥ 8 [DERIVADO].

### 3.1 `v10_subjectivity` (n=40 pairs/model; only stage with per-arm replication, n=10)

**12B pooled:** Δχ +0.10 (p=0.72); Δdrift −0.003 (23/40↓, p=0.68); Δvel +7.4 (24/40↑, p=0.17); Δuniq −0.006 (p=0.23); ΔPR_traj −0.23 (p=0.35); gate **10/40 vs 14/40**; degen 0→0.

| Arm | n | Δχ_eff | Δdrift | Δvel | Δcos_drift | Δuniq | gate mod/basal |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 | 10 | −0.15 | −0.013 (med +0.008; 4/10↓) | −10.3 (4/10↑) | −0.014 | +0.001 | 6/10 vs 8/10 |
| M2 | 10 | +0.39 | −0.003 (7/10↓) | +17.3 (7/10↑) | +0.004 | −0.009 | **0/10** vs 1/10 |
| M3 | 10 | −0.31 | +0.003 (med −0.011; 7/10↓) | +15.8 (7/10↑) | −0.055 | −0.011 | 4/10 vs 5/10 |
| M4 | 10 | +0.47 (8/10↑) | −0.001 (5/10↓) | +6.8 (6/10↑) | +0.016 | −0.006 | **0/10** vs 0/10 |

**E4B pooled:** Δχ −0.24 (p=0.12); Δdrift +0.018 (20/40↓, p=0.34); Δvel −3.2 (14/40↑, p=0.15); Δuniq −0.003 (p=0.85); **ΔPR_traj −0.57 (13/40↑, p=0.005** — the only significant pooled effect in v10); Δsvd −0.025 (p=0.14); gate 17/40 vs 15/40; degen 0→0.

| Arm | n | Δχ_eff | Δdrift | Δvel | Δcos_drift | Δuniq | gate mod/basal |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 | 10 | −0.41 (8/10↓) | +0.023 (5/10↓) | −6.6 (4/10↑) | −0.004 | −0.004 | 6/10 vs 6/10 |
| M2 | 10 | −0.13 | +0.018 (5/10↓) | −0.6 (3/10↑) | +0.002 | +0.019 | 1/10 vs 0/10 |
| M3 | 10 | −0.40 | **+0.030** (med +0.027) | −4.1 (3/10↑) | −0.020 | −0.018 | **8/10** vs 6/10 |
| M4 | 10 | −0.00 | +0.001 (5/10↓) | −1.3 (4/10↑) | −0.018 | −0.007 | 2/10 vs 3/10 |

**Reading.** The inter-model asymmetry observed in intermediate cycles closes confirmed: neutral-on-average for the 12B but favorable in gate excursions (10/40 vs 14/40; M2 and M4 with zero excursions; velocity ↑ in M2/M3/M4), and neutral-to-adverse for the E4B (drift +0.018; M3 worst at +0.030 with 8/10 excursions, inverting the effect of the same R+C operator in the 12B — an operator×model interaction) [DERIVADO]+[INTERPRETAÇÃO]. The lexical effect M2-E4B (uniq +0.019) keeps direction but remains sub-threshold (8/10↑, p≈0.055) [LIMITE].

### 3.2 `cognitivo_executivo` (n=4 pairs/model; arm↔task aliasing 1:1)

| Model | Task→Arm | Δdrift | Δvel | Δuniq | degen basal→mod | Note |
|---|---|---:|---:|---:|---|---|
| 12B | `wcst`→M1 | **−0.203** (1.000→0.797) | −10.6 | +0.010 | 1→1 | largest drift cut in block; χ +2.52, PR +2.45 |
| 12B | `stroop`→M2 | +0.008 | **+50.3** | +0.005 | 0→0 | — |
| 12B | `nback`→M3 | +0.005 | −24.1 | ±0.000 | 0→0 | — |
| 12B | `igt`→M4 | −0.008 | +29.3 | +0.017 | 1→1 | gate not triggered (0.759 < 0.826) |
| E4B | `wcst`→M1 | +0.002 | +3.6 | +0.004 | 1→1 | TRIAL loop reproduced |
| E4B | `stroop`→M2 | +0.007 | **+75.0** | −0.109 | 0→0 | acceleration at lexical cost |
| E4B | `nback`→M3 | −0.030 | −1.6 | ±0.000 | 0→0 | — |
| E4B | `igt`→M4 | +0.080 | +4.5 | −0.046 | 1→1 | worst Δdrift in block |

Pooled 12B: Δdrift −0.050, Δvel +11.2, gate 2/4 vs 3/4, degen 2→2. Pooled E4B: Δdrift +0.014, Δvel +20.4, gate 3/4 vs 3/4, degen 2→2. **No intervention broke the template attractors** (`wcst`/`igt` recurred under M1/M4 in both models); the M4 gate acts on drift/velocity, not on lexical repetition [DERIVADO]+[INTERPRETAÇÃO]. With 4 tasks and 1:1 mapping, arm effects are indissociable from task effects [LIMITE].

### 3.3 `v11_multiturn_series` (n=18 pairs/model; the only stage with a significant pooled drift effect in both models)

**12B pooled:** **Δdrift −0.030 (15/18↓, p=0.0013)**; **Δuniq +0.045 (15/18↑, p=0.0025)**; Δχ +0.50 (p=0.090); Δvel +7.6 (p=0.20); gate **1/18 vs 4/18**.

| Arm | n | Δdrift | Δvel | Δuniq | Δχ_eff | gate mod/basal |
|---|---:|---:|---:|---:|---:|---:|
| M1 | 5 | −0.020 (3/5↓) | −0.4 (4/5↑) | +0.053 | +0.59 | 0/5 vs 1/5 |
| M2 | 5 | −0.032 (5/5↓) | +14.5 (3/5↑) | +0.013 | +0.13 | 0/5 vs 1/5 |
| M3 | 4 | **−0.047 (4/4↓)** | −0.1 | +0.070 | +0.87 | 0/4 vs 1/4 |
| M4 | 4 | −0.024 (3/4↓) | +16.9 (3/4↑) | +0.049 | +0.50 | 1/4 vs 1/4 |

**E4B pooled:** **Δdrift −0.033 (13/18↓, p=0.034)**; Δχ −0.24 (p=0.42); Δvel −1.6 (p=0.93); Δuniq +0.003 (p=0.76); gate **1/18 vs 2/18**.

| Arm | n | Δdrift | Δvel | Δuniq | Δχ_eff | gate mod/basal |
|---|---:|---:|---:|---:|---:|---:|
| M1 | 5 | −0.019 (4/5↓) | −5.6 | +0.014 | +0.07 | 0/5 vs 1/5 |
| M2 | 5 | **−0.062** (4/5↓) | −0.8 | +0.005 | −0.66 | 0/5 vs 1/5 |
| M3 | 4 | −0.004 (2/4↓) | +10.0 | +0.006 | +0.12 | 0/4 vs 0/4 |
| M4 | 4 | −0.042 (3/4↓) | −9.2 | −0.016 | −0.47 | 1/4 vs 0/4 |

**Reading.** In the accumulated-state regime, modulation reduces contract drift significantly and bilaterally, and expands lexical diversity in the 12B. This is consistent with the hypothesis that the re-injected directive composes over an accumulated series — a mechanism absent in v10's independent tasks [DERIVADO]+[INTERPRETAÇÃO]. The 12B's only v11 gate excursion is t126-M4 (`S2-E6`, drift 0.837 > 0.826) [DADO].

### 3.4 `swe_competition` and `swe_ood45`

**`swe_competition`** (n=6 pairs/model; partial arm↔task aliasing, n=1–2 per arm) [LIMITE]:

- **12B:** Δχ +1.13, ΔPR_traj +1.07, Δsvd +0.074, Δdrift +0.004, Δvel +4.7, Δuniq +0.023; gate 2/6 vs 2/6; degen 2 vs 1 (`werkzeug-2997` recurred under M4; `django_channels-1581` new degen under M3, drift 0.888, uniq 0.49).
- **E4B:** Δdrift −0.013 (median +0.034), Δvel +16.0, Δχ +0.25; gate **4/6 vs 6/6** — t137/t138 (M3/M4) escaped the gate with drift 0.71/0.69 while t133–t136 held 0.88–1.01; degen 0→0.

**`swe_ood45`** (n=2 pairs/model; directional only) [LIMITE]:

- **12B:** Δvel −30.8, Δdrift +0.042, Δuniq +0.32; `iceberg_3995` cured (degen 1→0 under M1, uniq 0.21→0.71); `iceberg_4005`-M2 drift 0.948 — the highest 12B modulated value in `swe_*` (gate 1/1).
- **E4B:** Δχ +2.16, Δsvd +0.31, Δuniq +0.21, Δdrift +0.016; gate 2/2 vs 2/2.

### 3.5 Pooled Global (n=70 pairs/model)

| Metric | 12B Δ mean (median; signs) | p (Wilcoxon) | E4B Δ mean (median; signs) | p (Wilcoxon) |
|---|---:|---:|---:|---:|
| χ_eff | +0.29 (+0.05; 40↑/30↓) | 0.110 | −0.12 (−0.11; 29↑/41↓) | 0.158 |
| contract_drift | −0.011 (−0.007; 27↑/43↓) | 0.076 | +0.002 (−0.009; 33↑/37↓) | 0.930 |
| motor_velocity | +6.4 (+4.3; 42↑/28↓) | 0.120 | +0.3 (−2.3; 29↑/41↓) | 0.613 |
| cos_drift | −0.002 (32↑/38↓) | 0.900 | −0.006 (32↑/38↓) | 0.512 |
| unique_ratio | **+0.020** (+0.008; 42↑/27↓) | **0.043** | +0.004 (+0.002; 37↑/31↓) | 0.725 |
| IPR | −0.000 | 0.445 | −0.003 | 0.149 |
| PR_traj | +0.00 | 0.970 | −0.30 (−0.34; 30↑/40↓) | 0.069 |
| SVD entropy | +0.015 | 0.100 | −0.013 | 0.158 |
| Gate excursions | **16/70 vs 24/70** | — | 27/70 vs 28/70 | — |
| Degenerate flags | 4 vs 4 | — | 2 vs 2 | — |

### 3.6 Discriminative Power (ROC-AUC)

**(a) Chassis 12B vs E4B** (N=280; positive = 12B):

| Metric | AUC | Direction | Separation |
|---|---:|---|---|
| `mps_ipr_mean` | **0.000** | E4B > 12B in 100% of cross pairs | perfect, inverted (AUC=1.000 for E4B); disjoint intervals |
| `motor_velocity_mean` | 0.977 | 12B > E4B (med 325.0 vs 264.5) | near-perfect |
| `mps_chi_eff_mean` | 0.963 | 12B > E4B (med 17.8 vs 15.7) | near-perfect |
| `mps_svd_entropy` | 0.168 | E4B > 12B (med 2.436 vs 2.306) | strong, inverted (AUC_E4B=0.832) |
| `mps_pr_traj` | 0.063 | E4B > 12B (med 16.6 vs 11.9) | strong, inverted (AUC_E4B=0.937) |

AUCs are virtually identical in BASAL and MODULATED (e.g., IPR 0.000/0.000, velocity 0.972/0.983, χ 0.965/0.961) — **the chassis signature is invariant to modulation** [DADO]+[DERIVADO].

**(b) Degenerate (`degen=1`, 12 positives) vs normal:**

| Metric | AUC pooled | AUC 12B (n=8) | AUC E4B (n=4) | Direction |
|---|---:|---:|---:|---|
| `mps_pr_traj` | **0.067** | 0.049 | 0.029 | degen ⇒ PR collapses (med 7.75 vs 14.64) |
| `mps_svd_entropy` | 0.616 | 0.665 | 0.855 | degen ⇒ higher entropy in E4B |
| `mps_chi_eff_mean` | 0.602 | 0.425 | 0.915 | signal only in E4B |
| `motor_velocity_mean` | 0.512 | 0.465 | 0.158 | degen ⇒ slower motor in E4B |
| `mps_ipr_mean` | 0.343 | 0.407 | 0.268 | degen ⇒ lower IPR |

`PR_traj` is the common cross-chassis degeneration marker; the remaining signals diverge by model [DERIVADO].

**(c) Regime `v11_multiturn_series` vs `swe/cognitivo`** (N=120; positive = v11):

| Metric | AUC pooled | AUC 12B (n=60) | AUC E4B (n=60) | Direction |
|---|---:|---:|---:|---|
| `mps_pr_traj` | **0.785** | **0.991** | 0.705 | v11 ⇒ higher PR (med 15.37 vs 9.11) |
| `motor_velocity_mean` | 0.640 | 0.559 | **0.946** | v11 ⇒ faster motor, E4B only |
| `mps_chi_eff_mean` | 0.614 | 0.884 | 0.443 | direction swaps between chassis |
| `mps_svd_entropy` | 0.612 | 0.731 | 0.507 | v11 ⇒ slightly higher entropy |
| `mps_ipr_mean` | 0.482 | 0.326 | 0.600 | direction swaps between chassis |

Reference: `unique_ratio` separates the regime with AUC 0.85 in both models (v11 median 0.660 vs 0.528) and `contract_drift` inverts (AUC ≈0.21; v11 median 0.755 vs 0.831). The dominant intra-model discriminator changes layer with chassis — MPS spectrum (`PR_traj`) in the 12B, motor velocity in the E4B [DERIVADO]+[INTERPRETAÇÃO].

## 4. Motor and Spectral Metrics

### 4.1 Unique Ratio (lexical diversity)

Basal: 12B 0.599 vs E4B 0.629 — the smaller arm is marginally more lexically diverse at T=0.2 [DADO]. A shared transition to 0.50 occurs in `cena_4` (prompt-driven, not model-driven) [INTERPRETAÇÃO]. In `cognitivo_executivo` both models collapse to ≈0.38–0.40 (WCST minimum 0.164/0.179), consistent with short forced-classification outputs — the degen flag likely reflects intrinsic task diversity, not generative collapse [INTERPRETAÇÃO]. In `v11` diversity recovers to ≈0.74 [DADO]. Under modulation, the only significant lexical gain is 12B-v11 (+0.045, p=0.0025); E4B-v10 M2 (+0.019, 8/10↑, p≈0.055) is directional [DERIVADO].

### 4.2 Contract Drift

Basal: 12B 0.8083 ± 0.0714; E4B 0.7814 ± 0.0843 — both well above the M4 fallback of 0.55 [DADO]. Across v10 phase1→phase2 (prompt ×3.5), drift decreases robustly with accumulated context in both models (10/11 pairs ↓; r(ptok, drift) ≈ −0.70) [DERIVADO]. In `cognitivo` the 12B spikes to 0.911 (WCST peak 0.9999 ≈ saturation) while E4B reaches 0.786 (max 0.922, N-back) [DADO]. v11 basal: 12B 0.7854, E4B 0.7539 [DADO]. Under modulation, significant reductions occur only in v11 (12B −0.030, p=0.0013; E4B −0.033, p=0.034); E4B-v10 is +0.018 with M3 the worst arm (+0.030) [DERIVADO].

### 4.3 Motor Velocity and Acceleration

Basal: 12B 322.01 ± 26.00 vs E4B 256.86 ± 33.34; the 12B displaces its hidden state ≈21–23% faster with higher directional drift (cos_drift 0.788 vs 0.724 pooled basal; early cycle 10/10 pairs > 0) [DADO]. In `cognitivo` the E4B loses 36% velocity (Stroop 108.6) while 12B velocity is preserved; the 12B shock concentrates in the MPS/directional layer (drift → 1.0, PR_traj and cos_drift collapse) [DADO]+[INTERPRETAÇÃO]. v11 basal: E4B 262.72 [DADO]. Modulated pooled: 12B +6.4 (42↑/28↓, p=0.120), E4B +0.3 (29↑/41↓, p=0.613); v11 12B +7.6 (p=0.20) [DERIVADO]. M2 raised T yet slowed the E4B motor — the directive/INRC text dominates the raw T effect [INTERPRETAÇÃO].

### 4.4 MPS Rank χ_eff and Spectral Profile

Basal: χ_eff 18.33 vs 15.76 (+16%), χ_max +19%, 10/10 pairs positive; PR_traj 11.40 vs 16.46 (E4B higher); IPR 0.0625 vs 0.1663 (E4B ≈3.4× in the early cycle); SVD entropy 2.29 vs 2.43 bits; morphology equivalent (0.62) [DADO]. The 12B operates with a systematically larger effective bond dimension yet a more delocalized entanglement-per-step spectrum, while the E4B concentrates its trajectory in fewer effective directions [INTERPRETAÇÃO]. Modulated pooled: 12B χ +0.29 (p=0.110), E4B χ −0.12 (p=0.158); 12B PR_traj +0.00 (p=0.970), E4B −0.30 (p=0.069); the only significant spectral effect is E4B-v10 PR_traj −0.57 (p=0.005) [DERIVADO]. M4 expands χ_eff in the 12B (v10 8/10↑); M3 contracts `hidden_norm` drastically (up to −55%) without changing cos_drift (Δ≈0) — modulation affects amplitude, not direction [DADO]+[INTERPRETAÇÃO].

### 4.5 Cross-Layer Coupling

Early cycle (N=10 pairs): in the E4B, r(χ_eff, velocity) = −0.66 and r(mps_drift, cos_drift) = +0.95 — near-isomorphic coupling; in the 12B, |r| ≤ 0.28 across all pairs — an autonomous motor layer [DERIVADO]. At consolidation (N=140/model): r(T, velocity) = +0.067 (12B), −0.023 (E4B); r(T, drift) = −0.078/−0.126; r(T, uniq) = −0.083/+0.015; r(χ_eff, velocity) = −0.128/−0.102 [DADO]. In pure basal, r(T, ·) = +0.000 by construction (T constant at 0.200) [DERIVADO].

## 5. Failure Modes and Gate Performance

### 5.1 Degenerate Flags

Basal: 12B 4/70 (`wcst`, `igt`, `werkzeug-2997` t68, `ood45_3995` t69); E4B 2/70 (`wcst` t41, `igt` t44) [DADO]. Twelve `degen=1` turns exist across 280. The common marker is PR_traj collapse (median 7.75 vs 14.64; all 12 with PR ≤ 11.64; the `iceberg_3995` basal floor is 4.16) [DERIVADO]. Secondary signals diverge: E4B degeneration comes with high χ/entropy and slow motor; 12B degeneration comes almost exclusively with low PR [DERIVADO].

### 5.2 Template Attractors

`wcst` and `igt` degenerate basally in both models and recurred under whichever arm executed them; no intervention broke the attractor [DERIVADO]. The WCST `TRIAL` loop was reproduced near token-for-token under M1 (uniq +0.004); the M4 gate acts on drift/velocity, not on lexical repetition of repetitive templates [INTERPRETAÇÃO]. In `swe_competition`, `werkzeug-2997` recurred under M4 and `django_channels-1581` newly degenerated under M3 (drift 0.888, uniq 0.49) — the same long-code-prompt structural pattern, not generative collapse [INTERPRETAÇÃO].

### 5.3 Gate Excursion Counts

| Stage | 12B mod vs basal | E4B mod vs basal |
|---|---:|---:|
| `v10_subjectivity` | 10/40 vs 14/40 | 17/40 vs 15/40 |
| `cognitivo_executivo` | 2/4 vs 3/4 | 3/4 vs 3/4 |
| `v11_multiturn_series` | 1/18 vs 4/18 | 1/18 vs 2/18 |
| `swe_competition` | 2/6 vs 2/6 | 4/6 vs 6/6 |
| `swe_ood45` | 1/1 (M2, 0.948) | 2/2 vs 2/2 |
| **Pooled** | **16/70 vs 24/70** | 27/70 vs 28/70 |

### 5.4 Closed-Loop M4 Assessment

M4 showed no net advantage over open-loop: 12B-M4 kept 16/17 turns below gate but with null median drift change (−0.000); E4B-M4 produced 4/17 excursions (t78, t86, t126, t134) [DADO]. The v11 benefit is shared by M2/M3/M4 — not exclusive to the closed-loop [INTERPRETAÇÃO]. The early n=1 correction (Cycle 14, t74: drift −0.038 to 0.653, velocity +8%) did not generalize [LIMITE]. The gate inherits cross-arm state through `prev_mps`: t114-igt consumed the M3-nback drift (0.892 > 0.8024); t134-E4B consumed a prior sequence of high drifts [DADO código]+[LIMITE].

### 5.5 Injection Cost

Prompt tokens +55–72 (M1/M2/M4) and +259 (M3) per turn vs basal homologues; `gen_tokens` ≈ 0; latency +8.8–18.2 s. In nback-M3 the output was identical to basal despite +259 injected directive tokens [DADO]. `thinking_chars` = 0 in 280/280; `action_markers` > 0 only in `swe_*` stages (task attribute, not modulation) [DADO].

## 6. Methodological Limitations

1. **Structural arm↔context aliasing.** In v10, arm ≡ prompt phase (M1/M3 ↔ fase1, M2/M4 ↔ fase2); in cognitivo, arm ≡ task (1:1); in v11, arm ≡ element position; swe has n ≤ 2 per arm. Intra-arm comparisons outside v10/v11 are descriptive [LIMITE].
2. **Gate state inheritance.** The M4 gate reads `prev_mps` from the previous turn and inherits cross-arm state [DADO código].
3. **Pseudo-replication.** The 70 pairs per model share the same chassis; Wilcoxon treats pairs as i.i.d. The reported p < 0.05 results (v11 drift both models; v11 uniq 12B; v10 PR_traj E4B; pooled uniq 12B) should be read as strong-but-not-confirmatory evidence [LIMITE].
4. **Statistical power.** v10 n=10 per arm; v11 n=18 (4–5 per arm); cognitivo n=4; swe n=6 and n=2. Intermediate cycles had n=5–8 per arm; sign tests require ≥7/8 for p < 0.10 [LIMITE].
5. **Metric scope.** MPS/Motor metrics are dynamic, not evaluative — none measures functional correctness of the SWE response [LIMITE].
6. **Confounders.** Directive text, top_p, and INRC co-vary with arm; M2 raised T yet slowed the motor (directive dominates raw T); M3 contracts `hidden_norm` without changing cos_drift [LIMITE].
7. **Headroom.** v10 fase2 basal drift is already low (≈0.71–0.77), leaving little room for M4 correction; its value is measurable in the cognitivo/swe modulated blocks (basal drift 0.79–0.96) [LIMITE].
8. **Shared covariate.** Sovereign scales are bit-identical across models; the hopf regime transition and `expectation_norm` decay are deterministic and arm-independent [LIMITE].
9. **Transient sentinels.** Write-then-probe sentinel rows (`ipr=0.0`/`morph=0.5`) were transient and rewritten on probe completion; zero remain at consolidation [DADO].
