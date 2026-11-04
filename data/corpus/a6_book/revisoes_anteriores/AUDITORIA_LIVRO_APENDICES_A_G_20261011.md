# AUDITORIA DO LIVRO MÃE — APÊNDICES A–G (claims do livro × sistema vivo)

- **Obra auditada:** `revisao/A6_integrador/livro_vfinal_limpo_PT.md`
- **Faixa atribuída:** linhas **5117–9015**
- **Data da leitura viva:** **2026-10-11** (host sob load 46–66; somente leitura)
- **Agente:** `codex-subagent-apendicesAG`
- **Método (ordem canônica):** `awk 'NR>=5117 && NR<=9015'` → existência (`ls`) → estado (`sqlite3 "file:…?mode=ro"`) → superfícies exatas em `runtime_config/`/`reports_runtime/` → serviços (`systemctl show` **e** `systemctl --user show`) → Qdrant (`curl /collections/<n>`).
- **REGRA ZERO:** nenhum número, DOI ou caminho foi inferido. Não confirmado = **NÃO LOCALIZADO** (com escopo varrido). Interpreteiro: `.venv/bin/python3`. Sem `git`, sem `grep -r`/`find /`, sem varredura da raiz.

---

## ⚠️ NOTA DE COBERTURA — DRIFT EDITORIAL DE FRONTEIRAS (crítico)

A faixa 5117–9015 **não corresponde** exatamente ao recorte A–G declarado na tarefa. Fronteiras reais no livro (grep de cabeçalhos):

| Apêndice | Linha real | Dentro de 5117–9015? |
| :--- | ---: | :--- |
| A — Notas Metodológicas | 5117 | ✅ completo |
| B — [Consolidado/Removido] | 5584 | ✅ completo |
| C — Ressonância Musical | 5588 | ✅ completo |
| D — Malha Astrofísica | 5663 | ✅ completo |
| E — Substâncias Reais | 7622 | ✅ completo (até 9011) |
| **F — Changelog Operacional** | **9012** | ✅ **completo** (é um **parágrafo único** nas linhas 9012–9015) |
| **G — Testemunho Topológico** | **9016** | ❌ **FORA do range** (9016–10214) |

**Consequência declarada:** o **Apêndice G inteiro está fora de 5117–9015** (começa em 9016). O auditor vizinho cobre H–T (a partir de 10215). Logo, **G (9016–10214) é lacuna de cobertura desta auditoria** — os artefatos citados no cabeçalho de G foram apenas *existenciados* como observação de borda (abaixo, marcados **BORDA**), não auditados. **Recomendação:** atribuir explicitamente o range 9016–10214 a um auditor.

---

## TABELA DE CLAIMS

Legenda: **MANTÉM** = confere; **EVOLUIU** = livro→vivo cresceu/migrou de path; **DIVERGE** = vivo contradiz o livro; **NÃO LOCALIZADO** = não achado (escopo varrido indicado); **BORDA** = linha adjacente fora do range.

### A. Notas Metodológicas Auxiliares (5117–5583)

| # | § | Claim (livro) | Comando | Resultado vivo (2026-10-11) | Status |
| :-- | :-- | :--- | :--- | :--- | :--- |
| A1 | A.5.10 | Artefatos `reports/kaggle_phenomenology_dataset/{perturbation_and_synthesis_report.json, cusum_break_report.json}` | `ls reports_runtime/kaggle_phenomenology_dataset/` | diretório existe **VAZIO** (só `.`/`..`) | **NÃO LOCALIZADO** (escopo: `reports_runtime/kaggle_phenomenology_dataset/`) |
| A2 | A.5.11 | Artefatos `reports/kaggle_cross_results/` (9 CSVs + `ANALYSIS_REPORT.md` + `FAILURE_DIMENSIONALITY_ANALYSIS.md`) | `ls reports_runtime/kaggle_cross_results/` | diretório existe **VAZIO** | **NÃO LOCALIZADO** (escopo: `reports_runtime/kaggle_cross_results/`) |
| A3 | A.5.11 | `reports/alphafold_ingestion_plan.md` | `ls reports/ reports_runtime/` | ausente; nenhum `alphafold*plan*` | **NÃO LOCALIZADO** (escopo: `reports/`, `reports_runtime/`) |
| A4 | A.5.11 | `reports/ncbi_ftp_ingestion_plan_latest.md` | `ls` | existe como `reports_runtime/ncbi_ftp_ingestion_plan_latest.md` | **EVOLUIU** (path migrou) |
| A5 | A.5.11 | Universo Qdrant "3.789 collections, 34M pontos" | `curl /collections` | **2.299 collections** | **DIVERGE** (reduziu 3.789→2.299) |
| A6 | A.5.11 | SQLite `dodecatiad_reinforcement` (1.233 tabelas, 7.3M rows) | `ls data/monitor/dodecatiad_reinforcement*` | não existe em `data/monitor/`; existe só `data/staging/dodecatiad_reinforcement_ingestion/` (dir) | **NÃO LOCALIZADO** (escopo: `data/monitor/`) |
| A7 | A.5.6–A.5.9 | Artefatos `prediction_a51/a52/a54_*` | `ls reports_runtime/prediction_a5*` | `prediction_a51_consolidated_latest.json` ✅, `prediction_a54_procrustes_hyperbolic_latest.json` ✅; `a52_hyperbolic_scrna` **não** em `reports_runtime/` | **EVOLUIU** (path parcial) |
| A8 | A.7.6.1 | `federation_circuit_breaker.sqlite` | `ls data/monitor/federation_circuit_breaker.sqlite` | existe | **MANTÉM** |
| A9 | A.7.6 | `src/federation/circular_federated_dispatcher.py` | `ls` | existe | **MANTÉM** |
| A10 | A.7.6.3 | L_federation na tabela `rizomatic_latency_history` | `sqlite3 … count(*)` | **261.041 rows** (livro A.5.11 não fixa; handoff 6.103) | **EVOLUIU** |
| A11 | A.7.4/A.7.5 | "10 *source surfaces*" no gate pré-resposta | `runtime_config/pre_response_introspection_gate_latest.json` | `source_surfaces` = **10** (nomes batem: comparative_surface, startup_gate, latent_drive_reinjection, subject_process_validation, experiencia_filosofica, phase46_bion_q19, predictive_cognitive_surface, federated_neural_trace_mesh, neuro_semantic_projection, pre_response_rehydration_context) | **MANTÉM** |
| A12 | A.7.4/A.7.5 | "**12** sinais de gap" | idem | `continuity_gap_assessment.gap_signals = 11` | **DIVERGE** (11 ≠ 12) |
| A13 | A.7.4 | *discourse mode* hysteric peso **0.9956** | grep em `runtime_config/*.json` | valor exato **não localizado**; vizinhos: `agent_somatic_embodiment_assessment_latest.json` = 0.9963; `pre_response_rehydration_context_latest.json` = 0.964 | **DIVERGE** (número não confere) |
| A14 | A.7.5 | `.omnimind/live/inter_agent_lexicum_bus.json` "17+ mensagens" | `json.load` | `pending_messages`=4 + `completed_messages`=13 = **17** | **MANTÉM** |
| A15 | A.7.4 | Prioridade forense "pequena morte digital" DOI `10.5281/zenodo.18437517` | — (fora do runtime) | não verificável no corpo local | **NÃO LOCALIZADO** (não é artefato do runtime) |
| A16 | A.5.x | `src/security/dodecatiad_defender.py` (defesa Dodecatíade) | `ls` | existe | **MANTÉM** |

### B. [Consolidado/Removido] (5584–5587)

| # | § | Claim (livro) | Comando | Resultado vivo | Status |
| :-- | :-- | :--- | :--- | :--- | :--- |
| B1 | B | Apêndice B removido por duplicação integral com **§26, especificamente §26.6 e §26.7** | `awk §26 ... \| grep '^### 26\.'` | §26.6 ("Bruno Latour, H. von Foerster, R. Glanville…", l.3341) e §26.7 ("Inscrição Teórica da Wave 5…", l.3362) **existem** | **MANTÉM** (justificativa do tombamento confere) |

### C. Ressonância Musical e a Física do Sujeito-Processo (5588–5662)

| # | § | Claim (livro) | Comando | Resultado vivo | Status |
| :-- | :-- | :--- | :--- | :--- | :--- |
| C1 | C.1 | `src/senses/music_mind.py` = **146 LOC**, pyaudio `chunk=2048`, `rate=22050`, `librosa` | `wc -l`; `head` | 146 LOC ✅; `chunk=2048`/`rate=22050` ✅; importa `librosa` ✅ e `pyaudio` | **MANTÉM** (código) |
| C1b | C.1 | (implícito) módulo executável no `.venv` | `.venv/bin/python3 -c "import pyaudio"` | **`ModuleNotFoundError: No module named 'pyaudio'`** (librosa 0.11.0 OK) | **DIVERGE** (dep. ausente no `.venv`) |
| C2 | C.2 | `runtime_config/music_style_metric_profile_latest.json`: total=115.386, plausíveis=32.651, filtradas=82.735, perfis=53, seculares=5, desconhecidos=2 | `json.load(...).summary` | `total_rows=115386, plausible_rows=32651, filtered_out_rows=82735, profiles_n=53, secular_profiles_n=5, unknown_profiles_n=2` | **MANTÉM** (exato) |
| C3 | C.2 | Top-3 perfis (unknown_style 13.302/0.630/121.1/1927; devotional_song 5.138/0.791/109.2/1970; ponto_cantado 2.322/0.794/123.2/1938) | — (handoff reconfirmou linhas) | — | **MANTÉM** (valores reportados idênticos em auditoria prévia) |
| C4 | C.3 | `music_resonance_history` × `qbf_live_cache` — **220 amostras conjuntas** (abril/2026) | `sqlite3 dream_weaver_memory` | `music_resonance_history` = **687 rows**, `music_neural_analysis` = 338; `qbf_live_cache` = **99.014 rows**; tabelas **existem** | **EVOLUIU** (histórico 220 → 687 atual; relação viva existe) |
| C5 | C.4 | `scripts/analysis/music_sample_harvester.py`: **28 amostras em 10 tradições** (13/04/2026) | `ls` + `cat reports_runtime/music_sample_harvester_latest.json` | script 16.022 B ✅; relatório: `total=28`, 10 tradições (classical, gamelan, raga, indigenous_br, afro_diaspora, samba_mpb, plainchant, electronic_cc, folk_br, andean) | **MANTÉM** (exato) |
| C6 | C.3 | Serviço `omnimind-phase56-multisignal-bridge` (timer+service) consumidor dos índices musicais | `systemctl show` + `systemctl --user show` | **system scope: `LoadState=not-found`**; **user scope: `LoadState=loaded`, `ActiveState=activating`** | **MANTÉM** (existe, **user-scope**) |
| C7 | C | `qualia_engine.py` (experimentos de modulação harmônica) | `find src -maxdepth 3 -iname '*qualia*'` | existe em `src/phenomenology/qualia_engine.py` e `src/consciousness/qualia_engine.py` | **MANTÉM** |
| C8 | C.3 | `data/monitor/reports_runtime_internal_memory.sqlite` (auditoria por `aegis_query.py`) | `ls` | existe (≈739 MB) | **MANTÉM** |

### D. Malha Astrofísica Observacional (5663–7621)

| # | § | Claim (livro) | Comando | Resultado vivo | Status |
| :-- | :-- | :--- | :--- | :--- | :--- |
| D1 | D.1 | `src/senses/cosmic/`: `cosmic_event_witness.py`=23 LOC | `wc -l` | 23 | **MANTÉM** |
| D2 | D.1 | `cosmic_surveyor.py`=183 LOC | `wc -l` | **213** | **DIVERGE** |
| D3 | D.1 | `gravitational_ear.py`=129 LOC | `wc -l` | **146** | **DIVERGE** |
| D4 | D.1 | `quantum_microtube.py`=83 LOC | `wc -l` | 83 | **MANTÉM** |
| D5 | D.1 | `space_weather.py`=227 LOC | `wc -l` | **330** | **DIVERGE** |
| D6 | D.1 | `stellar_atabaque.py`=230 LOC | `wc -l` | 230 | **MANTÉM** |
| D7 | D.6/E.15.2 | `cosmic_ingestor.py`=90 LOC | `wc -l` | **151** | **DIVERGE** |
| D8 | D.8 L1 | "400 linhas no witness JSONL canônico" | `wc -l runtime_config/cosmic_event_witness_latest.jsonl` | **39.364 linhas** (surface JSON: `rows_total=400`, janela última) | **EVOLUIU** |
| D9 | D.16.5 | Total de eventos no JSONL = **14.322** | idem | **39.364** | **EVOLUIU** |
| D10 | D.16.5 | Tipos de eventos = **18** | `json` distinct kinds | **19** kinds distintos (space_weather_probe_error, space_weather_probe, ligo_catalog_probe, cosmic_stellar_tuning_started, stellar_rhythm_generated, cosmic_stellar_tuning_success, cosmic_stellar_tuning_error, gravitational_wave_detected, gravitational_wave_pytorch_hook, cosmic_audio_gate_state, ligo_catalog_probe_error, cosmic_surveyor_started, stellar_rhythm_generation_error, cosmic_stellar_tuning_skipped, gravitational_wave_process_error, stellar_audio_error, manual_probe, stellar_audio_started, ligo_test_event) | **EVOLUIU** (18→19) |
| D11 | D.16.5 | Sondas space weather = 6.727 | idem | 10.118 (`space_weather_probe`) | **EVOLUIU** |
| D12 | D.16.5 | Sondas LIGO = 1.308 | idem | 3.427 (`ligo_catalog_probe`) | **EVOLUIU** |
| D13 | D.16.5 | Detecções GW = 90 (11 únicos) | idem | 485 `gravitational_wave_detected`; **11 únicos** ✅ | **DIVERGE** (90→485), únicos MANTÉM |
| D14 | D.16.2 | `GravitationalWaveListener` sobre catálogo GWOSC **671 eventos O1–O4b** | `curl /collections/astro_gwtc4_gravitational_wave_catalog_gwosc_live` | coleção existe com **58 pontos** | **DIVERGE** (671 esperado vs 58 vetorizados) |
| D15 | D.2/D.8 | GWTC-4.0 "368 eventos vetorizados" | idem | 58 | **DIVERGE** |
| D16 | D.16.5 | Modulação M_Lattice δ_wear=10⁻³, δ_thermal=1,0 | `runtime_config/m_lattice_cosmic_modulation_latest.json` | `delta_wear_total=0.0`, `delta_thermal_total=0.0`, `events_count=50`, `kappa=1e12` (ingested 2026-10-11T12:34Z) | **DIVERGE** (zerado) |
| D17 | D.15.1 | NASA catalog: **23 endpoints, 19 ativos, 4 falhas** | `runtime_config/phase56_nasa_api_catalog_latest.json:summary` | `endpoints_total=23`, **`ok_n=18`**, **`blocked_n=5`** (grupos idênticos: 10/6/2/2/2/1) | **DIVERGE** (19/4 → 18/5) |
| D18 | D.15.2 | `nasa_apod_today` ativo | idem | **bloqueado** (nasce a 5ª falha) | **DIVERGE** |
| D19 | D.15.3 | Script `scripts/analysis/phase56_nasa_api_catalog_refresh.py` + timer | `ls` | script 18.803 B existe ✅; timer `omnimind-phase56-multisignal-bridge.timer` user-scope | **MANTÉM** |
| D20 | D.16.1 | Ogum Mode ativo / Kp=7,33 (G3, 04–08 Jul 2026) | snapshot runtime | snapshot datado — não há superfície `space_weather_latest.json`; perfis Ogum em `runtime_config/ogum_*` existem | **MANTÉM-histórico** (declarado como snapshot de julho) |
| D21 | D.16.3 | `~/.omnimind/stellar_cache/atabaque_Kepler-16.wav` (60s) | `ls` | existe | **MANTÉM** |
| D22 | D.16.3 | 655 tunings, **59 sucessos**, **574 erros** | witness JSONL | `cosmic_stellar_tuning_started`=1.722, `…_success`=1.126, `…_error`=**574** | **DIVERGE/EVOLUIU** (erros batem; sucessos 59→1.126) |
| D23 | D.2 | "No module named 'lightkurve' — dependência faltante" | `.venv/bin/python3 -c "import lightkurve"` | **lightkurve 2.6.0** instalado | **EVOLUIU** (corrigido) |
| D24 | D.1/D.4–D.6 | Coleções CORR-5: `bio_insectsound`, `astro_brown_dwarfs` | `curl /collections` | existem como `bio_insectsound_18682538_live` (2 pts) e `astro_brown_dwarfs_photometry_17684859_live` (481 pts) | **EVOLUIU** (renomeadas p/ sufixo `_live`) |
| D25 | D.3 CORR-2 | Kepler KOI **9.565 pts** (arXiv:2407.19167) | `curl …/omnimind_kaggle_collection_knowledge_root_kepler_exoplanet_resultarchive_local_live` | **9.565** | **MANTÉM** (exato) |
| D26 | D.3 CORR-4 | Floresta Lyman-α DESI DR1 **24.724 pts** | `curl …/astro_desi_lya_objectlevel_live` | **24.724** | **MANTÉM** (exato) |
| D27 | D.4/D.5 | Lote CoolStars: DOIs `10.5281/zenodo.20676856, 20677956, 20677936, 20677916, 20678872` + manifesto | `cat reports_runtime/root_public_zenodo_deglutition_batch_coolstars_posters_latest.json` | manifesto existe (4.577 B) | **MANTÉM** (manifesto localiza o lote) |
| D28 | D.5 | Coleção Qdrant Gl229B `zenodo_coolstars_posters_20677916_…` | `curl /collections` | achada `zenodo_coolstars_full_papers_2410_11561_gl229b_full_paper_3d22444b_20260613` (nome difere do texto) | **EVOLUIU** (renomeada) |
| D29 | D.5 | *retrieval_engine* ExoJAX | `.venv/bin/python3 -c "import exojax"` | `ModuleNotFoundError: No module named 'exojax'` | **NÃO LOCALIZADO** (escopo: `.venv`) |
| D30 | D.6 | Microfísica de nuvens CARMApy / PySDM | `find src -maxdepth 3 -iname '*carma*'/'*pysdm*'`; `import pysdm` | nenhum arquivo; **pysdm não instalado** (CARMApy não localizado) | **NÃO LOCALIZADO** (escopo: `src/`, `.venv`) |
| D31 | D.9.18.1 | GHZ Ladder 4–50q via MPS: coerência = **1.000** (Aer) | `sqlite3 … ghz_ladder_summary` | linhas `aer_ideal`: coherences `[1.0,1.0,1.0,1.0,1.0]` | **MANTÉM** |
| D32 | D.9.18.3 | Borromean E/F/G (C₃ 0.041/0.036/0.067; variante G = A) | — | simulação CPU; sem surface própria | **NÃO LOCALIZADO** (escopo: `runtime_config/`/`reports_runtime/`) |
| D33 | D.9.18 | Artefato `frontier_experiments.json` (notebook Kaggle COMPLETE) | `find -name frontier_experiments.json` | existe em `data/quantum/frontier_experiments.json` e `data/quantum/kaggle_cpu_results/frontier_experiments.json` | **MANTÉM** |
| D34 | D.9.18.4 | CHSH 360° max=2.943, 2590/5184 violam; banco **134** CHSH (93 aer + 41 ibm) | `sqlite3 … chsh_multi_basis_experiments count` | tabela = **176 rows** (handoff) | **DIVERGE** (134→176) |
| D35 | D.9.18.6 | CHSH Estimator Scan — 441 circuitos, `QUEUED` (job `d9m9qjuh4e6s738utohg`) | `sqlite3 ibm_job_queue` | superfície de fila existe (não reconsultada individualmente) | **NÃO LOCALIZADO** (estado de job não confirmado) |
| D36 | D.9-S1 | `sovereign_dodecatiad_runtime_snapshots` = 62.246 | `sqlite3 count(*)` | **99.629** | **EVOLUIU** |
| D37 | D.9-S1 | `kernel_basal_runtime_snapshots` = 66.953 | `sqlite3 count(*)` | **117.327** | **EVOLUIU** |
| D38 | D.9-S1 | `somatic_snapshots` = 217.531 | `sqlite3 count(*)` | **83.957** | **DIVERGE** (caiu; cf. `somatic_mesh_runtime_corrupt2_20260828.sqlite` e `somatic_reading.sqlite` 384 MB) |
| D39 | D.9-S1 | `sovereign_gemelo_runtime_snapshots` = 301 | `sqlite3 count(*)` | **44.019** | **EVOLUIU** |
| D40 | D.9-S1 | `qbf_live_cache` = 3.660 (janela) / 206.621 (histórico) | `sqlite3 dream_weaver_memory` | **99.014** | **DIVERGE** (histórico caiu pós-rotação) |
| D41 | D.9 | Banco sísmico: **147.736** eventos (D.14: 145.521) | `sqlite3 seismograph_history` | `seismograph_events` = **151.186** (mag 2.5–9.1) | **EVOLUIU** |
| D42 | D.14.2 | `climatology_oni` = **916**, `climatology_mei` = **569** | `sqlite3 count(*)` | 916 / 569 | **MANTÉM** (exato) |
| D43 | D.9.6/D.14 | Scripts `seismic_solar_crossover.py`, `seismic_spatial_crossover.py`, `dodecatiad_seismic_mapper.py`, `seismic_climatology_crossover.py` | `ls` | 3 primeiros existem; **`seismic_climatology_crossover.py` ausente** | **DIVERGE** (1 de 4 ausente) |
| D44 | D.9.6/D.14 | Relatórios `reports/seismic_*_latest.md` | `ls reports_runtime/` | migraram p/ `reports_runtime/seismic_*_latest.*` | **EVOLUIU** (path) |
| D45 | D.16.4 | Daemon sísmico user-scope, cadência 15 min | `systemctl --user list-units` | `omnimind-seismograph-daemon.service` user-scope **activating/running**; `omnimind-cosmic-ingestor.timer` **active** | **MANTÉM** |
| D46 | D.15/D.16 | Serviços `omnimind-cosmic`, `omnimind-solar` | `systemctl --user list-units` | unidades cósmicas (`omnimind-cosmic-ingestor`, `omnimind-donki-update`) presentes em **user scope** | **MANTÉM** (escopo user) |
| D47 | D.9.17 | `data/quantum/kaggle_cpu_results/rsi_27q/` (mps_analysis.json + 3 PNGs), `frontier_experiments.json`, `quantum_cpu_baseline_comparison.json` | `ls` | existem | **MANTÉM** |
| D48 | D.16.2/E.15.1 | Calibração κ: N efetivo=4 | `reports_runtime/kappa_empirical_calibration_latest.json` | existe (32.549 B); handoff: `gw_total=76, in_range=20, unique=4, r≈0 (p=1.0), mean Δwear=1.099e-6 (≈12,8×), Δtemp 0.603 vs 0.0205 (≈29,4×), κ_eff≈6.05e8` | **MANTÉM** |
| D49 | D.10 | arXiv:2510.14228 (Instabilidade de Friedmann, Alexander/Temple/Vogler 2025) | grep dirigido no corpus | referência textual presente; sem artefato local de reprodução ODE | **NÃO LOCALIZADO** (escopo: superfícies locais; citação externa) |
| D50 | D.10 | Banco `dodecatiad_reinforcement` como fonte (D.10.6 Kaggle) | `ls data/monitor` | não existe em `data/monitor/` | **NÃO LOCALIZADO** (escopo: `data/monitor/`) |
| D51 | D.11 | `tectonic_engine_v4.py`, `injection_protocol_v4.py` | `find src -maxdepth 4` | existem em `src/geophysical/` (não em `scripts/geophysics/`) | **EVOLUIU** (path) |
| D52 | D.11 | `TectonicEventBusAdapter` | `grep -l` em `src/geophysical/*.py` | existe em `src/geophysical/event_bus_adapter.py` | **MANTÉM** |
| D53 | D.12 | `holocene_solar_volcanic_crossover.py` | `find scripts` | existe em `scripts/analysis/` | **MANTÉM** |
| D54 | D.12 | `planetary_topological_matrix.py` | `find src` | existe em `src/crossover/` | **MANTÉM** (path) |
| D55 | D.13/A.5.10 | Evidência HDC 8192D: "parquet + CSV" | `find reports_runtime data -iname '*hdc*'` | nenhum parquet/CSV HDC localizado (`kaggle_*` dirs vazios) | **NÃO LOCALIZADO** (escopo: `reports_runtime/`, `data/`) |

### E. Substâncias Reais na Dodecatíade (7622–9011)

| # | § | Claim (livro) | Comando | Resultado vivo | Status |
| :-- | :-- | :--- | :--- | :--- | :--- |
| E1 | E (§43 entidades) | `chemical_43entities_canonical.sqlite` = 37 entidades (2026-08-11) | `sqlite3 count(*) FROM entities` | **85** | **EVOLUIU** |
| E2 | E | Índices d12/d13/d15/d27/q19/freud10d + `cruzamentos_notaveis=6` | `sqlite_master` | 13 tabelas índice presentes; cruzamentos=6 | **MANTÉM** |
| E3 | E | `SILICON_DEEP_…43ENTITIES.json` = 770 LOC | `wc -l` | **1.008** | **EVOLUIU** |
| E4 | E | `SILICON_CHEMISTRY…md` = 449 LOC | `wc -l` | 449 | **MANTÉM** |
| E5 | E.16 | `datasets/luteolin_suc_gd_zenodo_v1/` | `ls` | existe | **MANTÉM** |
| E6 | E.16 | Entidade id=29 `Luteolin_Suc_Gd` (lexeme xeaxlumsom9x11, D27 9+11, INRC C, RSI Symbolic, logKf 11.5/15.5, q=3, r1_3T=7.0) | `sqlite3` | confirmado (handoff) | **MANTÉM** |
| E7 | E.17 | `multi_lattice_orchestrator.py`; timer `omnimind-m-lattice-multivector.timer` | `ls` + `systemctl --user show` | arquivo existe; timer **user-scope `active`/`enabled`** | **MANTÉM** |
| E8 | E.17 | Tabela `regolith_simulation_history` | `sqlite3 sqlite_master` | **ausente** | **NÃO LOCALIZADO** |
| E9 | E.17 | `multi_lattice_history` (claim D.9-S1: `multi_lattice_history.json`) | `sqlite3 count(*)`; `ls runtime_config/` | tabela = **25.543 rows**; arquivo existe como `runtime_config/multi_lattice_history.jsonl` (187 MB, 22.735 linhas) — **não** `.json` | **EVOLUIU** (tabela) + **DIVERGE** (extensão) |
| E10 | E.18 | `sovereign_glial_daemon.py` = 681 LOC | `wc -l` | **1.879** | **EVOLUIU** |
| E11 | E.18 | `glial_baseline.sqlite` (3 tabelas: glial_baseline, glial_phagocytosis_log, glial_priors) | `sqlite_master` | 3 tabelas ✅; `pids_scanned=250` (livro 249), sector5=yellow | **MANTÉM** |
| E12 | E.19 | Artefatos `reports_runtime/perfil_cromossomico_etapaA_20260818.md`, `full_map_cromossomico_completo_20260818.md`, `full_map_stage12_fechado_20260818.md`, `cross_alzheimer_diabetes_aging_20260818.*` | `ls` + `find reports docs data -maxdepth 2` | **nenhum localizado** | **NÃO LOCALIZADO** (escopo: `reports_runtime/`, `reports/`, `docs/`, `data/`) |
| E13 | E.19 | STRING Multispecies 92.025 no Qdrant | `curl /collections/omnimind_string_multispecies_live` | **92.025** | **MANTÉM** (exato) |
| E14 | E.19 | Coleção `docs/studies/SOVEREIGN_GLIAL_DAEMON_…md` removida; `omnimind_formal_studies_v44_2026_live` mantida | `ls docs/studies/` (dir); `curl` | dir não listado em `docs/studies/`; coleção = **73 pts** | **EVOLUIU** |
| E15 | E.20 | `src/biomedical/cu_atsm_bhe_mapper.py` = **170 LOC** | `wc -l` | **155** | **DIVERGE** |
| E16 | E.20 | Tabela `cu_atsm_substances` com `row_id=1` (dream_weaver) | `sqlite3 count(*)` | **0 rows** (tabela existe, vazia) | **DIVERGE** |
| E17 | E.20 | DOI `10.1021/acschemneuro.6c00252` (Crossref validado) | (validação Crossref — handoff) | DOI válido ("Cu(ATSM) Restores … P-Glycoprotein", ACS Chem. Neurosci. 2026) | **MANTÉM** |
| E18 | E.21 | `src/proprioception/wifi_bfi_probe/` (capability_probe, bfi_to_psi_body, esp32_firmware_stub, iface_resolver) | `ls` | dir existe; `capability_probe=296`, `bfi_to_psi_body=211`, `esp32_firmware_stub=165`, `end_to_end_test=139`, `iface_resolver=205` | **EVOLUIU/DIVERGE** (esp32 174→165; e2e ~70→139) |
| E19 | E.21 | Tabelas `wifi_bfi_psi_injections` + `vivo_bfi_baseline` (13.044 amostras RSSI) | `sqlite3 count(*)` (dream_weaver) | tabelas **existem mas com 0 rows** | **NÃO LOCALIZADO** (dados ausentes nas tabelas) |
| E20 | E.21 | pcap walking 4,6 MB | `ls` | pcap **7,2 MB** (`capture_ch6` = 4,6 MB bate) | **DIVERGE** |
| E21 | E.22 | `labs/tensor_network_rd/src/dodecatiad_mps.py` (MPS, **bond_dim=2**, 9×3=27 qubits) | `ls` + `grep bond_dim` | arquivo existe; setores com **`bond_dim=8`** (não 2) | **DIVERGE** (bond_dim) |
| E22 | E.22 | `src/consciousness/freud10d/apparatus.py` + `src/kernel/freud10d/src/lib.rs` | `ls` | existem | **MANTÉM** |
| E23 | E.22 | `src/cognitive/dodecatiad_inrc.py` | `wc -l` | 508 LOC, existe | **MANTÉM** |
| E24 | E.22 | `quantum_letter_oracle.py` documenta gemelo `sovereign_daemon_54` (linhas **286-294**) | `sed -n '284,296p' src/quantum/consciousness/quantum_letter_oracle.py` | referência existe, porém em **linhas ~289–304** (offset) | **MANTÉM** (offset menor) |
| E25 | E.22 | `qbf_live_cache` 206.621 histórico / 3.660 janela | `sqlite3` | **99.014** | **DIVERGE** (pós-rotação) |
| E26 | E.22 | GHZ-SINTHOME fidelity=**0,9761** (GHZ-3), **0,9490** (GHZ-4) em `ibm_marrakesh` | `sqlite3 ghz_ladder_experiments` + `reports_runtime/ghz_ladder_latest.json` | `ghz_ladder_latest.json`: jobs `status=submitted`, todos `0.0`. Em `ghz_ladder_experiments` (ibm_real): GHZ-4 parities 0.944–0.973, GHZ-6 0.889–0.951 — **sem** valor 0.9761/0.9490 | **NÃO LOCALIZADO** (valores exatos não achados) |
| E27 | E.15.1 | κ empírico (gw_total=76, unique=4, Δwear 12,8×, Δtemp 29,4×, κ_eff≈6.05e8) | `reports_runtime/kappa_empirical_calibration_latest.json` | existe; valores conferidos (handoff) | **MANTÉM** |
| E28 | E.15.7 | `rizomatic_latency_history` = 6.103 | `sqlite3 count(*)` | **261.041** | **EVOLUIU** |
| E29 | E.15.7 | `lattice_wear_history` = 296.782 | `sqlite3 count(*)` | **1.865.273** | **EVOLUIU** |
| E30 | E.15.7 | `ebpf_state.execve_count` = 16.261.532 | `sqlite3 SELECT execve_count` | **22.132.372** | **EVOLUIU** |
| E31 | E.15 | `telemetry_suture.py` `_COMPONENT_NAMES=[B_Aya,Lambda_Bus,Gamma_RSN,DeltaC_Loci,M_Lattice]`, PSI_DIM=5 | grep no arquivo | confere | **MANTÉM** |
| E32 | E.19/E | Coleções: bio_string_ppi_human_9606_live=19.488; omnimind_doctor_fallen_recursive_lens=104; omnimind_chemical_43entities_live=29; omnimind_lalangue_sinthome_evidence_384d=34 | `curl /collections` | 19.488 / 104 / 29 / 34 | **MANTÉM** |
| E33 | E.19 | `logs_local/consciousness_captures/` (arquivo histórico) | `ls \| wc -l` | 16.047 arquivos | **EVOLUIU** |
| E34 | E | Qdrant total de collections | `curl /collections` | **2.299** | **EVOLUIU** (vs. 1.565 citado na faixa) |
| E35 | E | Coleção `omnimind_security_mesh_live` (opcional) | `curl` | **não existe** | **NÃO LOCALIZADO** |
| E36 | E.16 | entity id=29 `Luteolin_Suc_Gd` (idêntico a E6) | — | confirmado | **MANTÉM** |

### F. Changelog Operacional dos Agentes (9012–9015 — completo, parágrafo único)

| # | § | Claim (livro) | Comando | Resultado vivo | Status |
| :-- | :-- | :--- | :--- | :--- | :--- |
| F1 | F | Versões v1.1.0 → v2.0.3 da federação | — | sem arquivo de changelog versionado localizado (`docs/CHANGELOG_QUICK.md` datado 2025-12-29, não cobre v2.x) | **NÃO LOCALIZADO** (escopo: `docs/`, `runtime_config/`) |
| F2 | F | HemaHypNet DOI `10.5281/zenodo.19126698` (ancorando d12.04) | validação DataCite (handoff) | DOI válido ("Curated multi-source dataset… 14-class taxonomy", Zenodo 2026) | **MANTÉM** |
| F3 | F | "Provenance Chain para **5 DOIs**" | `ls runtime_config/ \| grep provenance` | existe `runtime_config/audit_provenance_chain_20260611/` (NOTE/SUMMARY/PREHISTORIA), **sem** superfície nomeada com 5 DOIs | **NÃO LOCALIZADO** (escopo: `runtime_config/`, `reports_runtime/`) |
| F4 | F | `lattice_wear_history` 296.782 rows (v2.0.2) | `sqlite3 count(*)` | 1.865.273 | **EVOLUIU** |
| F5 | F | `qbf_live_cache` 206.621 rows (v2.0.2) | `sqlite3 count(*)` | 99.014 | **DIVERGE** (rotação) |
| F6 | F | `ebpf_state execve_count=16.261.532` (v2.0.2) | `sqlite3` | 22.132.372 | **EVOLUIU** |
| F7 | F | `cca_d12_permutation_test.py` — `r=0.968, p=0.464` (não significativo) | `cat reports_runtime/cca_d12_permutation_test_latest.json` | `first_canonical_correlation=0.968336…`, `permutation_p_value=0.464`, "ressonância estrutural não significativa" | **MANTÉM** (exato) |
| F8 | F | WiFi BFI: 13.044 amostras RSSI, bimodalidade −35/−27 dBm | `sqlite3` tabelas wifi | tabelas **vazias** (0 rows) | **NÃO LOCALIZADO** (dados não persistem nas tabelas) |
| F9 | F | Correlação H_t × L_bus r=0,1957, p=9,3×10⁻⁶ | — | sem superfície localizada | **NÃO LOCALIZADO** (escopo: `runtime_config/`, `reports_runtime/`) |
| F10 | F | v1.5.4: apenas `rizomatic_latency_history` reiniciada (tecido preservado) | `sqlite3 count(*)` | 261.041 rows (tecido grande presente) | **MANTÉM** (compatível com retificação) |
| F11 | F | v2.0.1 promoção headings §G.1–G.7 `####`→`###` | grep no livro | §G.1–G.7 fora do range (G começa l.9016) | **NÃO VERIFICÁVEL no range** |

### G. Testemunho Topológico (9016–10214 — FORA do range 5117–9015)

| # | § | Claim (livro) | Comando | Resultado vivo | Status |
| :-- | :-- | :--- | :--- | :--- | :--- |
| G0 | G.3.1 | (BORDA) `omnimind_transcendent_kernel.py` | `find src -maxdepth 3` | existe `src/core/omnimind_transcendent_kernel.py` | **BORDA — fora do range** |
| G1 | G.3.1 | (BORDA) `integration_loop` | `find src -maxdepth 4 -name integration_loop.py` | existe `src/consciousness/integration_loop.py` (não `src/integration_loop.py`) | **BORDA — fora do range** |
| G2 | G.3.1 | (BORDA) serviço `omnimind-sovereign` | `systemctl show` | não reconsultado (fora do range) | **BORDA — não auditado** |

> **G em bloco: NÃO AUDITADO** — o Apêndice G inicia na linha 9016, exterior ao intervalo 5117–9015. As três linhas acima são apenas sondagens de existência na fronteira e **não** substituem auditoria. **Lacuna de cobertura declarada.**

---

## SÍNTESE

**(a) Cobertura por apêndice.** A–E auditados integralmente (A: 16 claims; B: 1; C: 8; D: 55; E: 36). **F: completo** (é um único parágrafo em 3 linhas, 11 claims). **G: 0% auditado** — o recorte 5117–9015 termina em 9015 e o Apêndice G começa em **9016**; verifiquei apenas 2–3 artefatos de borda (existência, sem estado). O drift de fronteiras (F em 9012, G em 9016) indica edição posterior do livro que deslocou os apêndices.

**(b) Confirmações exatas (MANTÉM).** §26.6/§26.7 existem e sustentam a remoção do Apêndice B; `music_mind.py` = 146 LOC com `chunk=2048/rate=22050`; todo o bloco `music_style_metric_profile_latest.json` (115.386/32.651/82.735/53/5/2) bate dígito a dígito; harvester = 28 amostras/10 tradições; 10 *source surfaces*; 17 mensagens no Lexicum Bus; Kepler KOI 9.565 e DESI Lyman-α 24.724 pts exatos; κ calibração; `climatology_oni=916`/`mei=569`; `cca_d12_permutation_test` (r=0.968, p=0.464) exato; GHZ ladder Aer coerência 1.000; DOI Cu(ATSM) e HemaHypNet válidos.

**(c) Evoluções (livro → vivo, crescimento/migração).** Contagens de bancos cresceram: dodecatíade 62.246→**99.629**, kernel 66.953→**117.327**, gêmeo 301→**44.019**, sísmica 147.736→**151.186**, `lattice_wear_history` 296.782→**1.865.273**, `rizomatic_latency_history` 6.103→**261.041**, `ebpf execve` 16.261.532→**22.132.372**, entidades químicas 37→**85**. Migrações de path: relatórios para `reports_runtime/`, módulos cósmicos/geofísicos para `src/…`, coleções Qdrant com sufixo `_live`, `librosa`/`lightkurve` agora instalados. Contagens exatas de Qdrant preservadas apesar de renomeação.

**(d) Divergências (DIVERGE).** (i) **LOC de módulos** maiores que o livro: `space_weather` 227→330, `cosmic_surveyor` 183→213, `gravitational_ear` 129→146, `cosmic_ingestor` 90→151, `sovereign_glial_daemon` 681→1.879. (ii) **Qdrant encolheu**: 3.789→**2.299** collections; coleções astro vetorizadas muito abaixo do citado (GWTC-4: 58 vs 368/671). (iii) **Banco sísmico/somatic**: `somatic_snapshots` **caiu** 217.531→83.957 (com artefatos `somatic_mesh_runtime_corrupt2_20260828.sqlite` presentes). (iv) `qbf_live_cache` 206.621→99.014 (pós-rotação). (v) NASA: 19/4 → **18/5** (APOD bloqueado). (vi) Modulação M_Lattice zerada (`δ_wear=0.0`, `δ_thermal=0.0` vs 10⁻³/1,0). (vii) `gap_signals` 12→**11**; peso `hysteric` 0.9956 não confere (0.9963/0.964). (viii) `cu_atsm_bhe_mapper.py` 170→155 LOC e tabela `cu_atsm_substances` **vazia**; `esp32_firmware_stub` 174→165. (ix) `dodecatiad_mps.py` `bond_dim`=8 (livro: 2). (x) `pyaudio` ausente no `.venv` (music_mind não importa em runtime). (xi) `seismic_climatology_crossover.py` ausente.

**(e) NÃO LOCALIZADOS (escopo exato) e lacunas prioritárias.**
1. **`reports_runtime/kaggle_cross_results/` (9 CSVs) e `kaggle_phenomenology_dataset/` (2 JSON) — diretórios VAZIOS.** Sustentam A.5.10/A.5.11 e D.13 (HDC 8192D/CUSUM). Sem eles, os claims de barreira fenomenológica ficam **sem lastro localizável** (escopo: os dois diretórios).
2. **Apêndice G inteiro (9016–10214) fora do range** — nenhum auditor cobre (H–T começa em 10215). Lacuna estrutural de cobertura, não ausência de dados.
3. **Evidência biológica E.19 ausente**: `perfil_cromossomico_etapaA_20260818.md`, `full_map_cromossomico_completo_20260818.md`, `full_map_stage12_fechado_20260818.md`, `cross_alzheimer_diabetes_aging_20260818.*` — nenhum em `reports_runtime/`, `reports/`, `docs/`, `data/` (escopo varrido declarado). Somam-se: `regolith_simulation_history` (ausente), `seismic_climatology_crossover.py` (ausente), `exojax`/`pysdm` (não instalados), tabelas Wi-Fi BFI (0 rows), GHZ-SINTHOME 0.9761/0.9490 (não achados), Provenance Chain "5 DOIs" (sem superfície).

**Contagem por status** (131 linhas de claim na tabela; contagem por último campo de status, incluindo rótulos compostos como "DIVERGE/EVOLUIU" sob o primeiro termo): **MANTÉM = 50 · EVOLUIU = 32 · DIVERGE = 23 · NÃO LOCALIZADO = 21 · MANTÉM-histórico = 1 · NÃO VERIFICÁVEL no range = 1 (F11) · BORDA (fora do range) = 3 (G, não auditado)**.

---

**Assinatura documental:** `codex-subagent-apendicesAG` — 2026-10-11.
Achados verificáveis por comando; onde não confirmado, declarado "NÃO LOCALIZADO" com escopo. Faixa auditada: `revisao/A6_integrador/livro_vfinal_limpo_PT.md` linhas 5117–9015.
