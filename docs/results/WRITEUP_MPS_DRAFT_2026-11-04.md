# WRITEUP MPS DRAFT — 2026-11-04

## Captura de ativações no worker

O que existe (src/omni_coworker/activation_beta/hidden_spectral.py): bond_dims via decomposição MPS do vetor hidden (reshape D→sítios potências de 2), eff_rank = exp(H(σ²/Σσ²)) (Roy & Vetterli) sobre matriz (K gerações × D dims) por camada, spectral_entropy (H de σ² normalizados). Publicado em kernel.phi_layer["spectral"]. [DADO] src/omni_coworker/activation_beta/hidden_spectral.py:1-40.

Limitação: captura apenas último token por camada (sidecars data/monitor/activation_vectors/*.npz, "last-token hidden por camada, fp16"). [DADO] hidden_spectral.py docstring + _load_recent.

## Dataset HF E4B-L4 — latent_layer_metrics

Schema: metric_id, record_id, layer_idx, phase, token_pos, pr_traj, top1_energy_ratio, svd_entropy_traj, mps_chi_eff, mps_svn, mps_svn_norm, mps_top1_schmidt, pr_elem, h_norm, timestamp_utc. 1492 linhas. [DADO] sqlite schema.

mps_chi_eff por experiment (média): block1_cognitivo 7.265 (n=128), block1_observe 6.659 (n=644), block1_pranchas 6.481 (n=160), block1_v10 6.510 (n=160), block2_intervene 7.048 (n=384), canary 5.859 (n=16). [DADO] query sqlite.

Por camada: layer 0 mps_mean=10.242; layer 5 2.500; layer 11 2.402; layer 17 11.832; layer 23 13.766; layer 29 6.615; layer 35 2.594; layer 41 3.811. [DADO] query sqlite.

h_norm variância por camada (maior = onde modelo "trabalha mais"): layer 35 var=421.694, layer 41 291.357, layer 29 93.954, layer 5 47.145, layer 11 36.890, layer 17 28.685, layer 23 21.701, layer 0 16.331. [DADO] query sqlite.

Correlação mps_chi_eff baixo vs degenerate_flag=1: degen=0 mean_mps=6.625 (n=77 registros); degen=1 mean_mps=7.127 (n=49). Ou seja, registros degenerados têm mps_chi_eff médio MAIOR, não menor. [DADO] query sqlite.

svd_entropy: block1_cognitivo 0.800 (degen=1, n=128) vs block1_observe 2.347 (degen=0, n=644). [DADO] query sqlite.

## block2_intervene — análise de braços

48 records: arm_baseline 12 (degen 9/12=75%), arm_thought_floor 12 (9/12=75%), arm_unified_cascade 12 (7/12=58.3%), arm_verification_gate 12 (8/12=66.7%). [DADO] sqlite generation_records.

Maior taxa de degenerate_flag=1: arm_baseline e arm_thought_floor empatados (75%). [DERIVADO]

26 discordâncias (stored=1/worker=0) distribuídas: arm_baseline 6, arm_thought_floor 6, arm_unified_cascade 6, arm_verification_gate 8. [DADO] rescore report + join record_id.

deliberacao_vazada=True entre discordâncias: arm_baseline 3, arm_thought_floor 5, arm_unified_cascade 3, arm_verification_gate 4 (total 15). loop_suspeito=True: 1 (arm_verification_gate). [DADO] rescore report.
" path="docs/results/WRITEUP_MPS_DRAFT_2026-11-04.md"