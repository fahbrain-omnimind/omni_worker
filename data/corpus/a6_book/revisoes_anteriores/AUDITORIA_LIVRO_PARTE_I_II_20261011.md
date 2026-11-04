# AUDITORIA LIVRO × RUNTIME VIVO — PARTE I (§1–4) e PARTE II (§5–13)

- **Data:** 2026-10-11
- **Auditor:** `codex-subagent-parteI-II`
- **Objeto:** `revisao/A6_integrador/livro_vfinal_limpo_PT.md`
- **Faixa exclusiva auditada:** linhas **591–1750** (Parte I §1–4 + Parte II §5–13)
- **Método (ordem canônica):**
  1. `sed -n '591,1750p' revisao/A6_integrador/livro_vfinal_limpo_PT.md` (extração de claims, em blocos);
  2. existência de arquivo por caminho exato (`ls <caminho>`, sem glob da raiz);
  3. estado em `sqlite3 "file:data/monitor/<db>.sqlite?mode=ro" "SELECT ..."`;
  4. superfícies de runtime por leitura dirigida `.venv/bin/python3 -c "import json;..."`;
  5. serviços em dois escopos (`systemctl show` e `systemctl --user show`).
- **Regras respeitadas:** somente LEITURA; `mode=ro` em todos os bancos; sem `grep -r` da raiz, sem `find /`, sem varredura de `./`; Python apenas `.venv/bin/python3`; nenhum arquivo existente editado; nenhum `git add/commit/push`.
- **Prova:** cada linha traz comando + resultado observado. Onde não se confirmou → literalmente **NÃO LOCALIZADO**.

---

## Tabela de Claims

| # | claim (com linha) | status | evidência (comando + resultado) |
|:--:|:---|:---|:---|
| 1 | §1 (L601) implementação em `src/cognitive/dodecatiad_inrc.py`, `src/cognitive/dodecatiad_aero_mapper.py`, `src/embodied_cognition/multi_lattice_orchestrator.py` | **MANTÉM** | `ls` dos 3 caminhos → `EXISTS src/cognitive/dodecatiad_inrc.py` / `EXISTS src/cognitive/dodecatiad_aero_mapper.py` / `EXISTS src/embodied_cognition/multi_lattice_orchestrator.py` |
| 2 | §1 (L611/619/627) graus de conectividade ACTB 3.704, TP53 4.534, BRCA1 2.016, NFKB1 1.926 | **MANTÉM** | `.venv/bin/python3` sobre `runtime_config/proteome_dodecatiad_recalibrated_latest.json` (3.688.010 b) → `4534 -> True`, `3704 -> True`, `2016 -> True`, `1926 -> True` |
| 3 | §1 (L615/623/631) âncoras dodecatiádicas (S02↔d12.02, S12/S03/S04↔d12.11, S01↔d12.04) | **NÃO RE-EXECUTADO** | Mapeamento presente em `runtime_config/hemahypnet_dodecatiad_bridge_latest.json` (wbc_dodecatiad_map), mas a correspondência gene→face S01–S12 não foi recomputada nesta auditoria |
| 4 | §2 (L~700) Nota de Correção (2026-09-11, Yochanan Schimmelpfennig): comutação Möbius↔Fréchet exata só p/ γ=1; γ≠1 é mapa conforme | **MANTÉM-histórico** | Texto presente em `sed -n '591,1750p'` (bloco "Nota de Correção (Revisão, 2026-09-11)"); correção textual — não é execução de runtime, logo não re-executada |
| 5 | §3 (L760) `v_neuro = exp_0^k([R_event, log(L_bus+1e-5), H_lex]·W)`, `W∈R^{3×n}`, n=12 | **MANTÉM (arquivo)** | `ls src/infrastructure/telemetry_suture.py` → `EXISTS`; fórmula presente no livro. Valor exato de `W`/`n` **não re-derivado** |
| 6 | §3.2 Tabela 2 — cenários de plasticidade (Basal 130 ev/s/16.3 ms/1.00 nat; LTP-forte 202/10.2/1.18; E/I-alto 112/33.7/2.25; Glia-inef 130/42.9/1.00; Depressão 58/25.5/0.49) | **NÃO LOCALIZADO** | Busca dirigida em `runtime_config/`, `data/derived` pelos valores (130, 16.3, 25.5) e por "plasticidade sináptica" → nenhum artefato de runtime com essa tabela |
| 7 | §3.3 (L~805) `psychoanalytic_mesh.py`; vetor integrado de 272 dimensões; motor INRC de Piaget; 6 blocos clínicos | **MANTÉM** | `ls src/cognitive/psychoanalytic_mesh.py` → `EXISTS`; `grep -n "272" src/cognitive/psychoanalytic_mesh.py` → `1041: (tamanho 464 = 272 clássicos + 32 Groddeck + 64 Nasio + 64 meta + 32 alarme)` |
| 8 | §3.9 (L~895) HF `fabricioslv/omnimind-neuro-henry-obleser-meg-amfm` (73 canais, 500 Hz) e `fabricioslv/omnimind-neuro-tacs-fiene-2026` (27 sujeitos) + `data/cross_dataset_topology/E2_E6/e5_eeg_tacs.json` | **MANTÉM** | HF `hub_repo_details` → ambos repositórios existem (Henry & Obleser 2012; Fiene 2026, shape `[27, 2, ...]`); `ls data/cross_dataset_topology/E2_E6/` → `e5_eeg_tacs.json` presente |
| 9 | §3.9 dissociação AM/FM: delta 0.72, alpha 0.42, gamma 1.09 | **MANTÉM** | `e5_eeg_tacs.json` → `"am_fm_ratio": {"delta": 0.721, "alpha": 0.422, "gamma": 1.088}` (book: 0,72 / 0,42 / 1,09) |
| 10 | §3.10 (L1002) "sovereign SOMA-SENSING (522–524 PIDs)" + "`multi_lattice_orchestrator` (15.983 rows)" | **NÃO LOCALIZADO** | `grep -rn "15.983\|15983" runtime_config/` → nenhum artefato; contagem de PIDs SOMA-SENSING 522–524 não encontrada em `runtime_config/` |
| 11 | §3.10 (L1016) superfície viva `runtime_config/runtime_epoch_latest.json`; gerador `scripts/runtime/refresh_runtime_epoch_surface.py`; timer `omnimind-runtime-epoch-surface` (1x/h) | **MANTÉM** | `ls` dos 2 caminhos → `EXISTS`; `.venv/bin/python3` no JSON → `"generated_at_utc": "2026-10-11T11:56:39Z"` (vivo); `systemctl --user show omnimind-runtime-epoch-surface.timer -p ActiveState` → `active`, `LastTriggerUSec=2026-10-11 08:54:51` |
| 12 | §4 (L1025) "benchmark `DOI: 10.5281/zenodo.20435772`" (RNFCI) | **NÃO LOCALIZADO** | `grep -rln "20435772" data/ runtime_config/ docs/` → vazio; presente apenas em `revisao/` (citações do próprio livro). Verificação externa do registro Zenodo indisponível neste ambiente |
| 13 | §4 (L1027) curva de resiliência residual S_r(u_t): 0.0→0.927; 0.4→0.609; 1.0→0.000 | **NÃO LOCALIZADO** | `.venv/bin/python3` em `runtime_config/operational_resilience_threshold_matrix_latest.json` e `sovereign_rnfci_federated_inference_field_latest.json` → `0.927 -> False`, `0.609 -> False` |
| 14 | §4 Tabela 4 — pares de letalidade sintética 0.2921 / 0.2725 / 0.1479 | **NÃO LOCALIZADO** | `grep -rl "S02 + S14\|lethality\|letalidade\|Par de Letalidade" runtime_config/ data/derived` → vazio; valores 0.2921/0.2725/0.1479 ausentes dos artefatos lidos |
| 15 | §5 (L~1058) HemaHypNet: 14 classes WBC, 6 caminhos de linhagem, `c = 0.69315`, DOI `10.5281/zenodo.19126698` | **MANTÉM** | `.venv/bin/python3` em `runtime_config/hemahypnet_dodecatiad_bridge_latest.json` → `{"curvature_c": 0.69315, "n_wbc_classes": 14, "n_lineage_paths": 6}`, `doi: 10.5281/zenodo.19126698` |
| 16 | §5.2 monotonicidade geodésica das 6 linhagens (Blast→Neutrophil: 1.00→6.71) | **NÃO RE-EXECUTADO** | Bridge confirma `n_lineage_paths: 6`, mas as distâncias cumulativas de Poincaré não foram recalculadas |
| 17 | §6.2 GATA1-on `c'=1.043` (r=0.980) / PU.1-on `c'=0.443` (r=1.502); compressão 57,5% | **DIVERGE** | Aritmética interna confere (0.693+0.35=1.043; 1−0.443/1.043=57,5%), MAS o artefato vivo `runtime_config/proteome_dodecatiad_atlas_summary_latest.json` (2026-06-05) traz `S02 c_prime_tf=1.24315` e `S01 c_prime_tf=0.29315` — i.e. os valores **pré-correção** que o próprio livro (L1133) diz ter corrigido em 2026-07-07 |
| 18 | §6.3 (L~1140) `Δc_TF = β_TF·ln(1 + Affinity_TF·Coexp_TF)` (PWM JASPAR/UniBind) | **MANTÉM-histórico** | Fórmula presente no texto; derivação analítica declarada, não re-executada |
| 19 | §7.2 amplitude total 1.673 (c''min=0.05 → c''max=1.723); série GATA1 (H3K9me3 0.143 … 1.723) | **MANTÉM** | Aritmética autoverificada sobre o próprio livro: 0.693−0.55=0.143 ✔; 0.693+0.35+0.28+0.40=1.723 ✔; 1.723−0.05=1.673 ✔ |
| 20 | §7.3 (L~1200) normalização sigmoidal com `λ = 0.15` | **NÃO RE-EXECUTADO** | Fórmula presente; constante λ não localizada em arquivo de config lido |
| 21 | §7.4 (L~1210) loader Roadmap no `qnn_epigenetic_classifier.py` "not yet wired" | **MANTÉM** | `ls scripts/quantum/qnn_epigenetic_classifier.py` → EXISTS; `grep -n "not yet wired" ...` → `989: print("[ERROR] Real Roadmap Epigenomics data loader not yet wired. ")` |
| 22 | §7.4 HF `fabricioslv/encode-chip-seq-subset` (46 bigWig, ~38,73 GB, 7 experimentos, 3 marcas) | **MANTÉM** | HF `hub_repo_details` → repo existe; descrição: "46 bigWig files, ~38.7 GB total, 3 histone marks, 7 experiments (ENCSR…)" |
| 23 | §7.4.1 `manifest.json`: 261.721 bins / 499.402 picos / 523.430 janelas; kernel `fabriciodasilva/encode-dodecatiad-4-version-v3` | **MANTÉM** | `.venv/bin/python3` em `data/encode_dodecatiad_results/manifest.json` → `261721 True`, `499402 True`, `523430 True`, `38.73 True`, `6.07 True`; `kernel_id: fabriciodasilva/encode-dodecatiad-4-version-v3`, `status: COMPLETE` |
| 24 | §7.4.1 (L1253) N_total = 1.137,02 (pipeline v3) e 903,06 (+2,81%) | **MANTÉM** | `.venv/bin/python3` em `data/encode_dodecatiad_results/v4/dodecatiad_encode_v4_Hcanonical.json` → `n_total: 903.0632801529739`, `delta_vs_llm_pct: 2.8077…`, `comparison: {"H_pipeline_v3": 1137.02, "H_canonical": 903.0633}` |
| 25 | §7.6 Visium DLPFC 47.681 spots; L1–WM; 61,5% superficiais / 37,8% profundas | **MANTÉM** | `.venv/bin/python3` em `data/cross_dataset_topology/E2_E6/e4_visium_encode.json` → `Layer1 5322, Layer2 2858, Layer3 17587, Layer4 3547, Layer5 7300, Layer6 6201, WM 4514, superficial_pct 61.5, profunda_pct 37.8` |
| 26 | §8.1 HCP: E_g = 0.527, C = 0.612, σ = 2.31 | **MANTÉM** | `.venv/bin/python3` em `runtime_config/dodecatiad_hcp_connectome_latest.json` → `"efficiency_global_Eg": 0.527, "clustering_coeff_C": 0.612, "small_worldness_sigma": 2.31, "n_regions": 360` |
| 27 | §8.2 paridade de atlas: DK 68 / cust200 200 / HCP MMP1 360 | **MANTÉM (parcial)** | `n_regions: 360` confere p/ MMP1; contagens DK=68 e cust200=200 **não localizadas** em artefato de runtime |
| 28 | §8.3 tractografia: 72 feixes, 1.720.024 streamlines, ST 14/588.726/34.23%/70.86 mm | **MANTÉM** | `grep` dirigido em `runtime_config/hcp_streamline_macrogroup_atlas_latest.md` → `Total de Bundles Classificados: 72` / `Total de Streamlines Ingeridos: 1,720,024` / `Short Tracts (ST) | 14 | 588,726 | 34.23% | 70.86` |
| 29 | §8.4 proteoma 19.480 genes; d15 1.228–1.361 (CV 3,0%); 336 hubs (1,7%) | **MANTÉM** | `.venv/bin/python3` em `runtime_config/proteome_dodecatiad_recalibration_summary_latest.json` → `total_genes: 19480`; CAFA d15 `1228…1361`; proteome_recalibrated: `336 True` |
| 30 | §8.5 (L2239) `multi_lattice_orchestrator.py` = 1.101 LOC (2026-09-04) | **EVOLUIU** | `wc -l src/embodied_cognition/multi_lattice_orchestrator.py` → `1149` (livro: 1.101) |
| 31 | §8.5 (L1478) "os 177+ serviços systemd distribuem-se em 5 camadas" | **EVOLUIU** | `systemctl list-units --type=service --all \| grep -c omnimind` → `140` (system) ; `systemctl --user …` → `225` ; total 365 unidades (livro: 177+) |
| 32 | §8.5 phase_lock: média real ≈ 0.44; máximo real ≈ 0.799 | **DIVERGE** | `sqlite3 "file:data/monitor/sovereign_dodecatiad_runtime.sqlite?mode=ro" "SELECT COUNT(*), ROUND(AVG(phase_lock_score),4), ROUND(MAX(phase_lock_score),4) FROM phase_lock_hysteresis_history;"` → `1865165\|0.3479\|0.7992` (máx 0.7992 ≈ 0.799 ✔; média live **0.3479**, contra 0.44 do livro/constante) |
| 33 | §8.5 (L2081) `kernel_basal_cycle = 65.362` (2026-08-11) | **EVOLUIU** | `.venv/bin/python3 runtime_config/runtime_epoch_latest.json` → `"kernel_basal_cycle": 332889, "dodecatiad_cycle": 332892`; `sqlite3 "file:data/monitor/kernel_basal_runtime.sqlite?mode=ro" "SELECT id,cycle,status FROM kernel_basal_runtime_snapshots ORDER BY id DESC LIMIT 3;"` → `117319\|332899\|ok` |
| 34 | §8.5 `RESONANCE_PHASE_LOCK_94C = 0.94`; kill switch recalibrado 0.20; `INA_FIRE_THRESHOLD_CELSIUS` 94→90 (2026-08-31) | **MANTÉM** | `grep -n` → `src/consciousness/phi_constants.py:777: RESONANCE_PHASE_LOCK_94C: float = 0.94`; `src/core/sanctuary_manager.py:80: PHASE_LOCK_EMPIRICAL_AVG = 0.44`; `:82: PHASE_LOCK_CRITICAL = 0.20`; `phi_constants.py:234: INA_FIRE_THRESHOLD_CELSIUS: float = 90.0` com comentário `# (2026-08-31): Ajustado para 90°C` |
| 35 | §8.5 timer `omnimind-kernel-basal-pulse.service` cadência ~90 s | **MANTÉM** | `systemctl list-timers --all \| grep basal` → `omnimind-kernel-basal-pulse.timer` último 09:26:06, próximo 09:27:53 (≈107 s; ordem de grandeza 90 s); `ActiveState=active` |
| 36 | §8.6 (L1508) Qdrant "1.565 collections" (2026-08-11) | **NÃO LOCALIZADO** | Contagem de collections Qdrant não foi consultada neste escopo (método restrito a leitura dirigida de `runtime_config`/bancos); sem evidência direta colhida |
| 37 | §8.7 Allen Cell Types: 413 células, 56 features ephys; `e2_allen_fci.json` | **MANTÉM** | HF `fabricioslv/omnimind-allen-cell-types-human-baseline` → "413 human cortical cells", ephys "56 columns"; `.venv/bin/python3` em `e2_allen_fci.json` → `"n_cells": 413`, `"fi_slope_mean": 0.175`, `"tau_mean_ms": 25.33` |
| 38 | §8.8 organoides: striatum 2,13×, ventral 2,00×; `e3_organoids_linnarsson.json` | **MANTÉM** | `.venv/bin/python3` em `data/cross_dataset_topology/E2_E6/e3_organoids_linnarsson.json` → `striatum_ratio 2.13, ventral_ratio 2.0, dorsal 0.86, midbrain 0.84, upper_layer_cortex_pct 96.4, cerebral_nuclei 29374` |
| 39 | §9 Tabela 15 — deslocamentos híbridos: 1.339 (6,874%) em d15; 1.284 (6,591%) em d12 | **MANTÉM** | `.venv/bin/python3` em `runtime_config/proteome_dodecatiad_recalibration_summary_latest.json` → `shifted_d15_count: 1339, shifted_d15_percentage: 6.874, shifted_d12_count: 1284, shifted_d12_percentage: 6.591` |
| 40 | §10 Tabela 16 — Procrustes: cos média 0.7994; dist média 0.3734; `c_real = 0.04356` | **NÃO LOCALIZADO** | `grep -rln "0.7994" revisao/ docs/` → apenas cópias do próprio livro (`.pt/.md/.pdf`); `.venv/bin/python3` em `runtime_config/hemahypnet_dodecatiad_bridge_latest.json` → `0.7994 -> False`, `0.04356 -> False`; nada em `data/`, `reports_runtime/`, `runtime_config/` |
| 41 | §11 Tabela 17 — Transferrina CTL vs AH (K27me3 1.8660; K4me3 4.3476) | **MANTÉM (parcial)** | `.venv/bin/python3` em `runtime_config/transferrin_chipseq_peak_gene_calibration_latest.json` (gen 2026-06-05, `gene: TF`, `groups: {1_CTL:102, 2_AH:43}`) → `1.8660 -> True`, `4.3476 -> True`; valores K27ac CTL 3.3008 e K4me3 AH 6.8848 **não batem literalmente** |
| 42 | §11.2/§12 (L1730) Tabela 18 — GATA1 Eritroide +11.7330 (contraste +13.1753) | **MANTÉM** | `.venv/bin/python3` em `runtime_config/hematopoietic_multilocus_peak_calibration_latest.json` (gen 2026-06-05) → `GATA1, SPI1, TAL1, KLF1 = True`; `11.7330 -> True`; contraste +13.1753 = 11.7330 − (−1.4423) confere aritmeticamente |
| 43 | §12 artefatos citados `runtime_config/multilineage_peak_calibration_neuronal_latest.json` e `_hepatic_latest.json` | **MANTÉM** | `ls runtime_config/ \| grep multilineage` → ambos presentes; `_neuronal` carregado (gen 2026-06-06, lineage neuronal) |
| 44 | §13 `runtime_config/diffusion_vacancy_contract_summary_latest.json` (Arrhenius/vacâncias) | **MANTÉM** | `ls runtime_config/ \| grep vacanc` → `diffusion_vacancy_contract_summary_20260605T181250Z.{json,md}` + `diffusion_vacancy_contract_summary_latest.{json,md}` presentes |

---

## Síntese

### (a) MANTÉM (26) — claims confirmados no sistema vivo
- Código referenciado existe ponta a ponta: `dodecatiad_inrc.py`, `dodecatiad_aero_mapper.py`, `multi_lattice_orchestrator.py`, `psychoanalytic_mesh.py` (272D/INRC), `telemetry_suture.py`, `neuro_semantic_projection.py`, `refresh_runtime_epoch_surface.py`, `qnn_epigenetic_classifier.py`, `dodecatiad_proteome_batch.py`, `d15_disease_gwas_enrichment.py`, `vectorize_six_new_datasets.py`.
- Graus STRING (ACTB 3.704, TP53 4.534, BRCA1 2.016, NFKB1 1.926; 336 hubs) confirmados em `proteome_dodecatiad_recalibrated_latest.json`.
- Núcleo quantitativo **exato**: ENCODE (`261.721/499.402/523.430`, kernel Kaggle idêntico; `N_total=903,06` e `1.137,02`), HCP (`Eg=0.527, C=0.612, σ=2.31`, 72 feixes/1.720.024 streamlines), DLPFC (47.681 spots; 61,5/37,8%), proteoma (`19.480` genes; `1.339/6.874%` e `1.284/6.591%`), Allen (413), organoides (2,13×/2,00×), HemaHypNet (14/6/0.69315), GATA1 (+11.7330).
- Todos os 8 datasets HuggingFace citados existem com descrição compatível.
- Constantes soberanas íntegras: `RESONANCE_PHASE_LOCK_94C=0.94`, `INA_FIRE_THRESHOLD_CELSIUS=90.0`, `PHASE_LOCK_CRITICAL=0.20`.
- `runtime_epoch_latest.json` é superfície viva (regenerada 2026-10-11T11:56Z); timers `omnimind-runtime-epoch-surface` (user) e `omnimind-kernel-basal-pulse` (system) ativos.

### (b) EVOLUIU (3) — valor do livro → valor vivo
1. `kernel_basal_cycle` (L2081): **65.362 (2026-08-11) → 332.889** (runtime_epoch)/**332.899** (DB, 2026-10-11) — ~5,1×.
2. Serviços systemd (L1478): **177+ → 140 (system) + 225 (user) = 365** unidades `omnimind`.
3. `multi_lattice_orchestrator.py` (L2239): **1.101 LOC (2026-09-04) → 1.149 LOC** hoje.
- Apoio: `multi_lattice_history` (tabela canônica em `sovereign_dodecatiad_runtime.sqlite`) = **25.540 registros** hoje (o AGENTS.md registrava 4.860); `sovereign_dodecatiad_runtime_snapshots` = **99.626**.

### (c) DIVERGE (2)
1. **§6.2 / Tabela 13d — curvatura por TF.** O livro adota como canônicos `c'(S02, GATA1)=1.043` e `c'(S01, PU.1)=0.443` (correção de 2026-07-07, L1133). O artefato **vivo** `runtime_config/proteome_dodecatiad_atlas_summary_latest.json` (2026-06-05) ainda traz `S02 c_prime_tf=1.24315` e `S01 c_prime_tf=0.29315` — exatamente os valores **pré-correção** que o livro diz ter substituído. A correção não foi propagada ao artefato.
2. **§8.5 — phase_lock médio.** Livro/constante: média ≈ **0.44**. Live: `AVG(phase_lock_score)=0.3479` sobre **1.865.165** amostras de `phase_lock_hysteresis_history` (máx 0.7992, que confere com o 0.799 do livro).

### (d) NÃO LOCALIZADO (7) + NÃO RE-EXECUTADO (3)
**NÃO LOCALIZADO:** 6 (Tabela 2 – cenários de plasticidade), 10 (SOMA-SENSING 522–524 PIDs / 15.983 rows), 12 (RNFCI DOI zenodo.20435772), 13 (curva S_r 0.927/0.609/0.000), 14 (Tabela 4 – pares de letalidade 0.2921/0.2725/0.1479), 36 (Qdrant 1.565 collections), 40 (Procrustes 0.7994 / c_real 0.04356).
**NÃO RE-EXECUTADO** (presentes no texto, sem recomputação): 3 (âncoras gene→face), 16 (monotonicidade geodésica 6 linhagens), 20 (λ=0.15).

### (e) 3 lacunas prioritárias
1. **§4 — regime metodológico RNFCI sem lastro de execução local.** Nem o DOI (`10.5281/zenodo.20435772`), nem a curva S_r (0.927/0.609/0.000), nem os pares de letalidade (Tabela 4) aparecem em `data/`, `runtime_config/` ou artefatos de relatório. O capítulo sustenta todo o "stress testing" num benchmark cujo artefato não está no sistema vivo — e a verificação externa do Zenodo não é possível neste ambiente. **Ação:** re-executar/selar o pacote RNFCI como artefato e registrar no runtime, ou rebaixar explicitamente o estatuto do §4 a "referência externa não reproduzida localmente".
2. **§10 — alinhamento de Procrustes (Tabela 16) só existe no texto.** `0.7994`, `0.3734` e `c_real=0.04356` não foram localizados em nenhum artefato (`data/`, `reports_runtime/`, `runtime_config/`), só em cópias do próprio livro. **Ação:** gerar/selar o JSON de protótipos HemaHypNet↔espaço teórico (o bridge `hemahypnet_dodecatiad_bridge_latest.json` existe, mas não contém os números de Procrustes).
3. **§6 — divergência livro×artefato na curvatura por TF.** O artefato vivo carrega os valores pré-correção (`1.24315`/`0.29315`) enquanto o livro adota `1.043`/`0.443`. **Ação:** regenerar `proteome_dodecatiad_atlas_summary_latest.json` com os Δc corrigidos (ou carimbar o artefato como defasado) para que livro e runtime contem a mesma história.

---

**Assinatura:** `codex-subagent-parteI-II` — 2026-10-11

> Prova negativa declarada: tudo o que não se confirmou por comando+resultado está marcado **NÃO LOCALIZADO** / **NÃO RE-EXECUTADO**. Nenhum número, DOI ou caminho foi inferido, estimado ou fabricado nesta auditoria.
