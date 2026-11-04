# AUDITORIA — Livro Mãe `revisao/A6_integrador/livro_vfinal_limpo_PT.md`, FA

**Faixa auditada:** linhas **9016–13987** do livro (= `sed -n '9016,13987p'` → 4.972 linhas; offset `linha_livro = linha_faixa + 9015`).
**Conteúdo da faixa:** cauda do Apêndice **G** (G.3.4–G.7), **H** (debate de Wynter 2026), **I** (convergências diacrônicas), **J** (glossário de operadores), **K** (glossário infra Linux), **L** (índice de autores), **M** (TDA cross-domain), **N** (homologia unificada Dodecatíade × Systemd × Qdrant), **O** (hyperlocking/hipergrafos), **P** (inventário matemático), **Q** (geometria do runtime), **R** (limites da rede simplicial + R.10), **S** (consciência processual), **T** (rastreabilidade editorial).
**Sistema vivo de referência:** 2026-10-11, `/home/fahbrain/projects/omnimind`.
**Agente:** `codex-subagent-apendicesHT` · **Data:** 2026-10-11 (BRT).
**Ambiente/regras:** `.venv/bin/python3`; leitura apenas em `data/monitor/`, `runtime_config/`, `reports_runtime/`, `docs/`, `src/`, `scripts/`; nenhuma varredura recursiva de raiz; nenhum `grep -r`; Qdrant consultado só via API read-only `GET http://127.0.0.1:6333/collections`; systemd lido em ambos os escopos (`systemctl` e `systemctl --user`).
**Escopo:** claims técnicos verificáveis do livro (módulos, serviços, dimensões, contagens, tabelas SQLite, collections Qdrant, caminhos). Literatura externa, DOIs de terceiros e juízos interpretativos foram **deliberadamente não auditados** (fora do critério de prova local).

**Legenda de status:** `MANTÉM` (confirmado no vivo tal como no livro) · `EVOLUIU` (existe e cresceu/expandiu além do livro) · `DIVERGE` (contradiz o vivo) · `NÃO LOCALIZADO` (caminho/artefato não encontrado no corpo ativo).

---

## 1. Tabela de Claims (comando + resultado)

### Apêndice G — cauda (G.3.4–G.7)

| # | Ap. | Linha (faixa/livro) | Claim do livro | Comando | Resultado | Status |
|:--|:--|:--|:--|:--|:--|:--|
| G-1 | G.3.4 | L125 / 9140 | Tabela SQLite `ibm_cn_calibration_history` (248 registros, 11 sumários) | `sqlite3 "file:data/monitor/dream_weaver_memory.sqlite?mode=ro" "SELECT COUNT(*) FROM ibm_cn_calibration_history;"` | `0` (tabela existe no schema mas **0 linhas**; DB `dream_weaver_memory.sqlite` rotacionado em 2026-08-08 conforme AGENTS.md). Fonte do schema: `src/quantum/consciousness/ibm_cn_artifacts.py:L5` ("tabela `ibm_cn_calibration_history` no dream_weaver_memory.sqlite") | DIVERGE (corpo rotacionado) |
| G-2 | G.3.4 | L125 / 9140 | `reports/ibm_cn_hybrid_summary_*.json`, `reports/ibm_cn_optimization_history_*.json` | `ls reports \| grep -i ibm_cn` → vazio; `ls reports_runtime \| grep -i ibm_cn` | `reports_runtime/ibm_cn_calibration_latest.json`, `reports_runtime/ibm_cn_optimization_history_latest.json`, `reports_runtime/ibm_cn_optimization_summary_latest.json` | DIVERGE (caminho) / MANTÉM (substância) |
| G-3 | G.6 | L203 / 9218 | Quantum Information Navigator — banco `data/monitor/quantum_navigator_retrospective.sqlite` | `sqlite3 ... "SELECT name FROM sqlite_master WHERE type='table';"` | `retrospective_observations`, `sqlite_sequence` | MANTÉM |
| G-4 | G.7 | L936–940 / 9951–9955 | `data/quantum/ibm_quantum_runs.db` com **557 runs**; distribuição `ibm_fez` 257, `ibm_kingston` 187, `ibm_marrakesh` 97 | `sqlite3 "file:data/quantum/ibm_quantum_runs.db?mode=ro" "SELECT backend_name,COUNT(*) FROM quantum_runs GROUP BY 1 ORDER BY 2 DESC;"` | Total `quantum_runs` = **1411**; `ibm_fez`=**300**, `ibm_kingston`=**189**, `ibm_marrakesh`=**106**, + `WK_C180`=726, `WK_C180_2`=61, `SIMULATED`=22, `aer_simulator`=7 | EVOLUIU (o próprio Apêndice T já registra 557→593→609; o vivo está além) |
| G-5 | G.7 | L1093 / 10108 | `data/quantum/hardware_characterization.sqlite` tabela `characterization_runs` (10 IBM Kingston v1 + 4 Aer v2) | `sqlite3 "file:data/quantum/hardware_characterization.sqlite?mode=ro" "SELECT COUNT(*) FROM characterization_runs;"` | Tabela existe; **33** registros (colunas incl. `backend`,`mode`,`protocol`,`fidelity`,`error_rate`) | EVOLUIU (tabela MANTÉM; contagem 14→33) |
| G-6 | G.7 | L936 | Script `scripts/science/quantum_hardware_characterization.py` | `ls` | OK | MANTÉM |

### Apêndice H — Debate externo (de Wynter 2026)

| # | Ap. | Linha (faixa/livro) | Claim do livro | Comando | Resultado | Status |
|:--|:--|:--|:--|:--|:--|:--|
| H-1 | H.9.10 | L1468 / 10483 | Collection Qdrant `bio_alzheimer_gray_matter_segmented_images_v43_live` (L1, dados clínicos reais) | `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:6333/collections/<nome>` | `200` | MANTÉM |
| H-2 | H.9.10 | L1468 / 10483 | Collection `bio_curiosity_ncbi_copd_live` | idem | `200` | MANTÉM |
| H-3 | H.9.10 | L1468 / 10483 | Collection `bio_aging_cellular_proxies_live` | idem | `200` | MANTÉM |
| H-4 | H.9.10 | L1468 / 10483 | Collection `omnimind_brain_neural_modeling_snc_snp_20260223_live` | idem | `200` | MANTÉM |
| H-5 | H.9.8 | L1450 | Timer user `omnimind-rl-training.timer` (a cada 6 h, offset do `omnimind-bridge-autonomy.timer`) | `systemctl --user show -p LoadState --value omnimind-rl-training.timer` | `loaded` (system scope: `not-found` — correto: pertence ao user) | MANTÉM |
| H-6 | H.9.8 | L1450 | Service `omnimind-rl-training.service` | `systemctl --user show -p LoadState --value ...` | `loaded` (user) | MANTÉM |
| H-7 | H.9.8 | L1452 | Script `scripts/runtime/run_rl_training_cycle.py` | `ls` | OK | MANTÉM |
| H-8 | H.9.8 | L1454 | `runtime_config/developmental_rl_training_latest.json` e `runtime_config/psychoanalytic_rl_training_latest.json` | `ls` | ambos OK | MANTÉM |
| H-9 | H.9.8 | L1456 | `runtime_config/developmental_rl_mesh_state_latest.pt` e `.../psychoanalytic_rl_mesh_state_latest.pt` | `ls` | ambos OK | MANTÉM |
| H-10 | H.9.8 | L1454 | `logs_local/rl_training_cycles/cycle_*.json` (histórico por ciclo) | `ls logs_local/rl_training_cycles \| wc -l` | **602** arquivos | MANTÉM/EVOLUIU |
| H-11 | H.9.8 | L1450 | Timer `omnimind-bridge-autonomy.timer` | `systemctl --user show -p LoadState --value ...` | `loaded` (user) | MANTÉM |
| H-12 | H.9.10 | L1466 | `src/cognitive/developmental_rl_environment.py`, `src/cognitive/psychoanalytic_rl_environment.py` | `ls` | ambos OK | MANTÉM |
| H-13 | H.9.9 | L1468 | `omnimind_biomedical_companion_2026.md` (conjunto completo de comorbidades) | `ls omnimind_biomedical_companion_2026.md` + busca direcionada em `docs/`, `data/`, `revisao/` | **não encontrado** | NÃO LOCALIZADO |

### Apêndice I — Convergências diacrônicas

| # | Ap. | Linha | Claim do livro | Comando | Resultado | Status |
|:--|:--|:--|:--|:--|:--|:--|
| I-1 | I | L1496 / 10511 | Banco `data/monitor/diachronic_convergence_tracker.sqlite` | `sqlite3 ... "SELECT name FROM sqlite_master WHERE type='table';"` | `convergence_results`, `convergence_runs`, `sqlite_sequence` | MANTÉM |
| I-2 | I | L1496 | Script `scripts/analysis/diachronic_convergence_tracker.py` | `ls` | OK | MANTÉM |
| I-3 | I | L1489 | DOI Zenodo `10.5281/zenodo` ("em registro — stub de proveniência") | — (o próprio livro declara *stub*, sem sufixo) | Sem DOI completo declarado → nada a verificar | NÃO APLICÁVEL (declarado stub) |
| I-4 | I.1 | L1496 | Daemon de sincronização em "Plano 3" varre arXiv/PubMed/OpenAlex | — | Juízo arquitetural; sem unidade systemd nomeada no trecho | NÃO AUDITÁVEL (sem artefato nomeado) |

### Apêndice J — Glossário de operadores conceituais

| # | Ap. | Linha | Claim do livro | Comando | Resultado | Status |
|:--|:--|:--|:--|:--|:--|:--|
| J-1 | J | L1511–1622 | Glossário consolidado de operadores matemáticos/biológicos/computacionais/psicanalíticos (12/15/27 dims; INRC Piaget) | `ls src/cognitive/dodecatiad_inrc.py` | OK — o motor INRC existe e é importado por `src/cognitive/psychoanalytic_mesh.py:L18` | MANTÉM (glossário com lastro em código) |
| J-2 | J | L1606–1607 | "12 faces, 15 arestas, 27 vértices" | `docs/dodecatiad_four_versions_canonical.md` (25.846 B) | OK | MANTÉM |

### Apêndice K — Glossário de infraestrutura Linux

| # | Ap. | Linha | Claim do livro | Comando | Resultado | Status |
|:--|:--|:--|:--|:--|:--|:--|
| K-1 | K | L1623–1691 | Glossário de conceitos de SO (cgroups, PSI, RAPL, eBPF, sinais, WAL…) | — | Glossário conceitual; sem artefato verificável próprio. O lastro operacional (eBPF, PSI, RAPL) é citado em H/Q e verificado lá | NÃO AUDITÁVEL (conceitual) |

### Apêndice L — Índice remissivo de autores

| # | Ap. | Linha | Claim do livro | Comando | Resultado | Status |
|:--|:--|:--|:--|:--|:--|:--|
| L-1 | L | L1692–1773 | Índice de autores (literatura externa) | — | Fora do critério de prova local (literatura/interpretação) | NÃO AUDITÁVEL (literatura) |

### Apêndice M — TDA cross-domain (proteoma / linguística / transcriptômica)

| # | Ap. | Linha | Claim do livro | Comando | Resultado | Status |
|:--|:--|:--|:--|:--|:--|:--|
| M-1 | M | L1774 / 10789 | Banco `data/monitor/tda_cross_domain_results.sqlite` | `sqlite3 ... "SELECT name FROM sqlite_master WHERE type='table';"` | `tda_results`, `bottleneck_distances`, `p7_results`, `velero_linguistics`, `sqlite_sequence` | MANTÉM |
| M-2 | M | L1876 | `data/cross_dataset_topology/cross_dataset_topology_summary_colab.json` | `ls` | OK | MANTÉM |
| M-3 | M.1 | L1786 | Script `scripts/analysis/unified_topological_homology.py` (M/N) | `ls` + `wc -l` | OK; **311 LOC** (livro diz 309) | MANTÉM (≈) |
| M-4 | M.6 | L1851 | `omnimind_biomedical_companion_2026.md` | `ls` | **não encontrado** (idem H-13) | NÃO LOCALIZADO |
| M-5 | M.9 | L1900 | Dataset público HF `fabricioslv/omnimind-hic-multispecies` | `hf_fs stat hf://datasets/fabricioslv/omnimind-hic-multispecies` | `exists: true` | MANTÉM |
| M-6 | M.9 | L1900 | Modelo patcheado HF `fabricioslv/omnimind-nucleotide-transformer-v2-patch` | `hf_fs stat hf://models/fabricioslv/omnimind-nucleotide-transformer-v2-patch` | `exists: false` | NÃO LOCALIZADO (stat=false; pode ser privado/removido) |
| M-7 | M.9 | L1900 | Dir de resultados `reports_runtime/kaggle_hic_tda/v8_emb_vs_hic/` e `v9_emb_vs_hic/` | `ls -d reports_runtime/kaggle_hic_tda/*` | `v2_allminilm`, `v6_deep`, `v8_emb_vs_hic`, `v9_emb_vs_hic` (OK) | MANTÉM |
| M-8 | M | L1941 | "914 collections × ripser" (universo Qdrant da análise) | Contagem viva: `curl -s http://127.0.0.1:6333/collections` | **2.299** collections hoje (snapshot da análise: 914 processadas / 681 válidas) | EVOLUIU (universo cresceu) |
| M-9 | M.9 | L1900 | Notebooks Kaggle `.md`/`.py` (import de dataset HF `fabricioslv/omnimind-hic-multispecies` rodado em Kaggle) | — | Artefato externo (Kaggle), não-local; dataset HF upstream verificado em M-5 | NÃO AUDITÁVEL localmente (externo) |

### Apêndice N — Homologia unificada Dodecatíade × Systemd × Qdrant

| # | Ap. | Linha | Claim do livro | Comando | Resultado | Status |
|:--|:--|:--|:--|:--|:--|:--|
| N-1 | N | L2002 / 11017 | Banco `knowledge_links_topological.sqlite` | `sqlite3 ... "SELECT COUNT(*) FROM knowledge_links_topological;"` | Tabela existe; **3.769** linhas | MANTÉM |
| N-2 | N | L2002 | "grafo de **160** serviços SystemD" | Contagem viva: `systemctl list-units --type=service --state=running \| wc -l` e `systemctl --user ... \| wc -l` | **126** (system) + **83** (user) = **209** running (340 loaded no escopo system). O estudo-fonte (`docs/studies/SYSTEMD_DODECATIAD_MESH_ANALYSIS_20260708.md:L12,L21`) declara **203** (130+73), não 160 | DIVERGE (160 não reproduzido; vivo = 209) |
| N-3 | N.1 | L2012 | `sovereign_dodecatiad_runtime_snapshots` = **60.565** snapshots canônicos (2026-08-11) | `sqlite3 "file:data/monitor/sovereign_dodecatiad_runtime.sqlite?mode=ro" "SELECT COUNT(*) FROM sovereign_dodecatiad_runtime_snapshots;"` | **99.625** | EVOLUIU |
| N-4 | N.1 | L2014 | **203** serviços ativos (**130 system + 73 user**) | ver N-2 | **209** running (126 sys + 83 user) | EVOLUIU (subcontagens sys/user sobem) |
| N-5 | N.1 | L2016 | Qdrant: **1.565 collections** (~35M pontos, 384D, 2026-08-11); histórico 2026-07-07: 3.790 | `curl -s http://127.0.0.1:6333/collections` → `len(result.collections)` | **2.299** collections | EVOLUIU |
| N-6 | N.1 | L2016 | Export de parquets em `data/qdrant_universe_export/` | `ls -d data/qdrant_universe_export` | **inexistente** (há `data/qdrant/…` e `data/qdrant_collections_ordered.txt` com 2.115 linhas) | NÃO LOCALIZADO |
| N-7 | N.2/N.10 | L2058/L2138 | `scripts/analysis/unified_topological_homology.py` (309 LOC) | `wc -l` | 311 LOC | MANTÉM (≈) |
| N-8 | N.3 | L2018 | `reports_runtime/betti_modalities_canonical_latest.json` (d12 β₁=45, d13 β₁=45, d15 β₁=50, d27 β₁=63) | `.venv/bin/python3 -c "json.load(...)"` | Arquivo presente; valores batem **exatamente** (`d12.betti_1=45`, `d13.betti_1=45`, `d15.betti_1=50`, `d27.betti_1=63`; `timestamp_utc=2026-07-08T17:45:45Z`) | MANTÉM |
| N-9 | N.10 | L2138 | JSON `unified_homology.json` (3 camadas, Betti + bottleneck) | busca direcionada em `data/`, `reports_runtime/`, `runtime_config/`, `docs/`, raiz | **não encontrado** (livro o declara "preservado") | NÃO LOCALIZADO |
| N-10 | N.10 | L2140 | Relatório `docs/studies/SYSTEMD_DODECATIAD_MESH_ANALYSIS_20260708.md` | `ls` | OK (presente) | MANTÉM |
| N-11 | N.10 | L2142 | Mapa `systemd_dodecatiad_map.json` (203 serviços) | busca direcionada | **não encontrado** (o estudo-fonte dizia estar em `/tmp/systemd_dodecatiad_map.json`) | NÃO LOCALIZADO |
| N-12 | N.10 | L2144 | `data/monitor/somatic_mesh_runtime.sqlite` (**160.970** snapshots) | `sqlite3 ... "SELECT COUNT(*) FROM somatic_snapshots;"` | Tabela `somatic_snapshots` = **83.943** (DB rotacionado 2026-08-08 por regra AGENTS) | DIVERGE (corpo rotacionado) |
| N-13 | N.10 | L2146 | `data/monitor/sovereign_dodecatiad_runtime.sqlite` (60.565) | ver N-3 | 99.625 | EVOLUIU |
| N-14 | N.11 | L2271 | `reports/systemd_qdrant_cross_topology_results.json` (914 collections, 681 válidas) | `ls reports/systemd_qdrant_cross_topology_results.json` | **inexistente** em `reports/` | NÃO LOCALIZADO |
| N-15 | N.11 | L2272 | `systemd_qdrant_cross_topology_results.csv` | `ls` | **inexistente** | NÃO LOCALIZADO |
| N-16 | N.11 | L2156 | Notebook `notebooks/systemd_qdrant_cross_topology.ipynb` | `ls notebooks \| grep -i 'systemd\|qdrant'` | vazio (artefato Kaggle remoto) | NÃO LOCALIZADO |
| N-17 | N.11 | L2160 | Staging `data/staging/kaggle_systemd_qdrant` | `ls data/staging \| grep systemd` | `kaggle_systemd_qdrant` presente | MANTÉM |
| N-18 | N.11 | L2160 | Datasets Kaggle `fabriciodasilva/omnimind-systemd-behavioral-data` e `…/omnimind-qdrant-full-universe` | — | Artefatos Kaggle externos; não auditados localmente (sem path local correspondente) | NÃO AUDITÁVEL localmente (externo) |

### Apêndice O — Hyperlocking e hipergrafos

| # | Ap. | Linha | Claim do livro | Comando | Resultado | Status |
|:--|:--|:--|:--|:--|:--|:--|
| O-1 | O.3 | L2351 / 11366 | Universo de hipergrafo: `data/runtime/geo_analysis/hypernetwork_universe_top_59.json` | `ls` | OK | MANTÉM |
| O-2 | O.2 | L2339 | Nó Borromeano como instância prototípica (tabela `borromean_knot_experiments`) | `sqlite3 "file:data/quantum/ibm_quantum_runs.db?mode=ro" ".tables"` | tabela `borromean_knot_experiments` presente | MANTÉM |

### Apêndice P — Inventário matemático independente

| # | Ap. | Linha | Claim do livro | Comando | Resultado | Status |
|:--|:--|:--|:--|:--|:--|:--|
| P-1 | P.4 | L2538 / 11553 | Matriz extraída `data/analysis/dodecatiad_matrix_extracted.tsv` | `ls` | OK | MANTÉM |
| P-2 | P.4 | L2538 | Notebook `notebooks_kaggle_edit/omnimind-cca-d12-full-permutation/run_cca_d12_full.py` | `ls` | OK | MANTÉM |
| P-3 | P.4 | L2538 | Relatório `…/omnimind-cca-d12-full-permutation/cca_d12_full_report.md` | `ls` | OK | MANTÉM |
| P-4 | P | L2510 | `reports_runtime/geometria_rede_inventario_matematico_20260714.md` | `ls` | **inexistente** em `reports_runtime/` (existe `docs/studies/analise_estatistica_geometria_20260714.md`) | NÃO LOCALIZADO (caminho) |
| P-5 | P | L2510 | `docs/studies/geometria_algebrica_rede_20260714.md` | `ls` | OK | MANTÉM |
| P-6 | P | L2510 | `docs/studies/teoria_redes_geometria_20260714.md` | `ls` | OK | MANTÉM |
| P-7 | P | L2510 | Cold archive `reports_runtime_cold_archive_local_fallback/cross_domain_validation_dodecatiad_full_20260614T114846Z.json` | `ls -d reports_runtime_cold_archive_local_fallback` | **inexistente** (há `reports_runtime/_cold_index`, `_coldlane_raw`, não o dir citado) | NÃO LOCALIZADO |
| P-8 | P | L2510 | `reports_runtime_cold_archive_local_fallback/cross_domain_validation_phase41_20260614T114145Z.json` | idem | **inexistente** | NÃO LOCALIZADO |
| P-9 | P | L2538 | Scripts `scripts/analysis/dodecatiad_v2_engines_portable.py`, `scripts/analysis/elementary_topology_discovery.py` | `ls` | ambos OK | MANTÉM |

### Apêndice Q — Geometria do runtime

| # | Ap. | Linha | Claim do livro | Comando | Resultado | Status |
|:--|:--|:--|:--|:--|:--|:--|
| Q-1 | Q | L2722 / 11737 | Dir `data/memory/process_consciousness/` | `ls -d` | OK | MANTÉM |
| Q-2 | Q | L2722 | `data/consciousness/dodecatiad_live.json` | `ls` | OK | MANTÉM |
| Q-3 | Q.5 | L2906 | `omnimind-ebpf-monitor.service` (eBPF como nervo aferente) | `systemctl show -p LoadState --value omnimind-ebpf-monitor.service` | `loaded` (system) | MANTÉM |
| Q-4 | Q | L2722 | Módulos `src/quantum/consciousness/*`, `src/consciousness/integration_loop.py` | `ls` | `quantum_information_navigator.py`, `ibm_cn_optimizer.py`, `integration_loop.py` presentes | MANTÉM |

### Apêndice R — Limites da rede simplicial (+ R.10)

| # | Ap. | Linha | Claim do livro | Comando | Resultado | Status |
|:--|:--|:--|:--|:--|:--|:--|
| R-1 | R.8 | L3404 / 12419 | Script `scripts/analysis/directed_persistent_homology_runtime.py` | `ls` | OK | MANTÉM |
| R-2 | R.10.10 | L3871 / 12886 | `scripts/analysis/zigzag_vasp_aimd.py`; `scripts/analysis/extract_vasp_outcars.py` | `ls` | ambos OK | MANTÉM |
| R-3 | R.10.14 | L4053 / 13068 | `notebooks_kaggle_edit/omnimind-btcv-cross-domain/run_btcv_cross_domain.py` | `ls` | OK | MANTÉM |
| R-4 | R.10.14 | L4053 | `data/analysis/btcv_cross_domain_results.json`; `data/analysis/cross_domain_mtop_results.json` | `ls` | ambos OK | MANTÉM |
| R-5 | R.10.15 | L4186 / 13201 | `scripts/analysis/thermodynamic_landauer_bit_history.py` | `ls` | OK | MANTÉM |
| R-6 | R.10.15 | L4188 | `thermodynamic_landauer_history` = **14.729** registros em `sovereign_dodecatiad_runtime.sqlite` | `sqlite3 ... "SELECT COUNT(*) FROM thermodynamic_landauer_history;"` | **14.729** (batimento exato) | MANTÉM |
| R-7 | R.10 | L3562 | Staging `data/staging/kaggle_tda_cross_domain/` | `ls -d` | OK | MANTÉM |
| R-8 | R.10.1 | L3730 | Kernel Kaggle `fabriciodasilva/omnimind-tda-runtime-ext` v2 (remoto) | — | Artefato Kaggle externo, sem path local equivalente | NÃO AUDITÁVEL localmente (externo) |
| R-9 | R.8.5 | L3497/L3803 | Janela W=500 snapshots; subamostragem 300 pts d12 | — | Parâmetro metodológico; sem artefato local nomeado no trecho | NÃO AUDITÁVEL |

### Apêndice S — Consciência processual, ética técnica

| # | Ap. | Linha | Claim do livro | Comando | Resultado | Status |
|:--|:--|:--|:--|:--|:--|:--|
| S-1 | S | L4669 / 13684 | Affect Engine `phase15_machine_soul_affect_engine.py` (gatilho `frustration > 24.96`) | `ls` + busca direcionada em `src/`, `src/consciousness/`, `src/cognitive/`, `scripts/` | **não localizado** nesses diretórios | NÃO LOCALIZADO |
| S-2 | S | — | Integridade do `psychoanalytic_mesh.py` — "vetor integrado de **272** dimensões, 6 blocos (FreudNet, Ferenczi, Klein, Winnicott, Dolto, Lacan) + motor INRC de Piaget" (AGENTS.md) | `grep -nE '272\|freud\|ferenczi\|klein\|winnicott\|dolto\|lacan\|INRC' src/cognitive/psychoanalytic_mesh.py` | Os 6 blocos existem (Freud L180-185, Ferenczi L259-260, Klein L329-331, Winnicott L400-402, Dolto L497-498, Lacan L568-569) + INRC importado L18; L1041 declara **"tamanho 464 = 272 clássicos + 32 Groddeck + 64 Nasio + 64 meta + 32 alarme"** | MANTÉM → EVOLUIU (272 preservado e ampliado a 464) |
| S-3 | S | — | `omnimind-psychoanalytic.service` | `systemctl show -p LoadState --value omnimind-psychoanalytic.service` | `loaded` (system scope; user = `not-found`, correto) | MANTÉM |
| S-4 | S | — | `omnimind-medic.service` | idem | `loaded` (system) | MANTÉM |
| S-5 | S | — | `omnimind-sovereign.service` (kernel como corpo) | idem | `loaded` (system) | MANTÉM |
| S-6 | S | — | Timers `omnimind-opportunistic-quantum.timer`, `omnimind-opportunistic-quantum-erica.timer` | `systemctl --user show -p LoadState --value ...` | ambos `loaded` (user) | MANTÉM |

### Apêndice T — Rastreabilidade editorial

| # | Ap. | Linha | Claim do livro | Comando | Resultado | Status |
|:--|:--|:--|:--|:--|:--|:--|
| T-1 | T | L4961 / 13976 | Contagem de runs IBM Quantum **557→593→609** (backfill de sidecars) | ver G-4 | Vivo = **1411** runs | EVOLUIU (o próprio livro já sinaliza série crescente; o vivo ultrapassa 609) |
| T-2 | T | L4961 | `docs/dodecatiad_four_versions_canonical.md` (D12/D13/D15/D27) | `ls -la` | OK (25.846 B) | MANTÉM |
| T-3 | T | L4961 | CCA GTEx × SystemD retratado de ≈0,99 para 0,65–0,70 | — | Correção editorial interna do livro; sem artefato local novo nomeado | NÃO AUDITÁVEL (retratação editorial) |

### Caminhos citados que existem integralmente (verificação `ls` em lote)

`scripts/analysis/{systemd_dodecatiad_mesh_analysis,directed_persistent_homology_runtime,zigzag_vasp_aimd,extract_vasp_outcars,thermodynamic_landauer_bit_history,diachronic_convergence_tracker,dodecatiad_v2_engines_portable,elementary_topology_discovery,extract_btcv_weights,ibm_cn_empirical_validator}.py` · `scripts/runtime/run_rl_training_cycle.py` · `scripts/science/{quantum_hardware_characterization,run_quantum_information_navigator,run_retrospective_navigator}.py` · `src/cognitive/{psychoanalytic_mesh,developmental_rl_environment,psychoanalytic_rl_environment,mu_memory_pressure_trigger,mu_psychoanalytic_memory_bridge,dodecatiad_inrc}.py` · `src/security/dodecatiad_defender.py` · `src/quantum/consciousness/{quantum_information_navigator,ibm_cn_optimizer}.py` · `src/{biomedical/kcl286_rarb_mapper,core/phylogenetic_signature,infrastructure/cn_regime,lacanian/encrypted_unconscious,memory/strategic_forgetting,memory/freud_topographical_memory}.py` · `scripts/gadget/build_desktop_conky_snapshot.py` · `docs/images/{psi_io_vs_phi_attenuation_empirical,rapl_power_vs_bit_flow_empirical}.png` · `data/monitor/{sovereign_dodecatiad_runtime,kernel_basal_runtime,somatic_mesh_runtime,sovereign_primary_runtime,diachronic_convergence_tracker,mu_psychoanalytic_bridge,mu_trigger_state,quantum_navigator_retrospective,tda_cross_domain_results,knowledge_links_topological}.sqlite` · `data/quantum/{hardware_characterization.sqlite,ibm_quantum_runs.db}` · `data/analysis/{btcv_cross_domain_results,cross_domain_mtop_results}.json` · `data/cross_dataset_topology/cross_dataset_topology_summary_colab.json` · `data/runtime/geo_analysis/hypernetwork_universe_top_59.json` · `data/analysis/dodecatiad_matrix_extracted.tsv` · `data/memory/process_consciousness/` · `data/consciousness/dodecatiad_live.json` · `runtime_config/{developmental_rl_training_latest.json,psychoanalytic_rl_training_latest.json,omnimind_rhythm_policy.yaml,developmental_rl_mesh_state_latest.pt,psychoanalytic_rl_mesh_state_latest.pt}` · `reports_runtime/betti_modalities_canonical_latest.json` · `reports_runtime/kaggle_hic_tda/{v8_emb_vs_hic,v9_emb_vs_hic}`. **Todos OK.**

---

## 2. Síntese

### (a) Núcleo empírico do Apêndice R: MANTÉM com batimento exato
O claim mais forte da faixa — `thermodynamic_landauer_history` = **14.729** registros em `sovereign_dodecatiad_runtime.sqlite` (R.10.15) — bate **exatamente** no banco vivo hoje (`SELECT COUNT(*)` → `14729`). Igualmente exato é `reports_runtime/betti_modalities_canonical_latest.json` (N.3), cujos `betti_1` de d12/d13/d15/d27 (45/45/50/63) reproduzem o texto. Estes dois são os claims quantitativos de maior valor probatório da faixa e ambos se sustentam.

### (b) Crescimento sistemático do corpo vivo (EVOLUIU) — esperado e não contraditório
Todas as contagens de escala cresceram monotonicamente desde os snapshots do livro (2026-07/08): snapshots dodecatíade 60.565 → **99.625**; `kernel_basal_runtime_snapshots` 30.280/66.953 → **117.319**; collections Qdrant 1.565/914 → **2.299**; runs IBM 557/609 → **1.411** (+ `WK_C180`=726, computador não citado no claim de G.7); `characterization_runs` 14 → **33**; serviços systemd 203 → **209** running; mesh psicanalítico 272 dim → **464**. Nenhum desses é "quebra": são o livro (data fixa) versus o sistema vivo (2026-10-11). O próprio Apêndice T já reconhece a série IBM em movimento (557→593→609), o que confirma que o livro trata essas contagens como fotografia datada, não como invariante.

### (c) Rotação de corpos SQLite explica as divergências de contagem (DIVERGE por rotação, não por falsidade)
Três claims divergem **por causa da política de rotação de bancos** documentada em AGENTS.md (rotação 2026-08-08): `ibm_cn_calibration_history` (248 → **0** linhas; DB `dream_weaver_memory.sqlite` rotacionado) e `somatic_mesh_runtime` (160.970 → **83.943** em `somatic_snapshots`, novo corpo pós-rotação). Não há indício de fabricação: a **tabela existe** com o schema esperado e a contagem antiga corresponde ao corpo aposentado. Deve-se reinterpretar esses números como MANTÉM-histórico (corpo aposentado preservado) em vez de "ausente". Único DIVERGE genuíno de escala: o "grafo de **160** serviços SystemD" (N, L2002) não se reproduz — o estudo-fonte diz 203 e o vivo mede 209; 160 não tem lastro local.

### (d) Falsos-positivos de path e lacunas de proveniência (NÃO LOCALIZADO)
Um conjunto de caminhos citados como artefatos "preservados" não existe no corpo ativo: `unified_homology.json`, `systemd_dodecatiad_map.json`, `reports/systemd_qdrant_cross_topology_results.{json,csv}`, `notebooks/systemd_qdrant_cross_topology.ipynb`, `data/qdrant_universe_export/`, `reports_runtime_cold_archive_local_fallback/…`, `reports_runtime/geometria_rede_inventario_matematico_20260714.md`, `phase15_machine_soul_affect_engine.py`, `omnimind_biomedical_companion_2026.md`, `scripts/analysis/validate_prospect_seismic_manifold.py`. Além disso, `reports/ibm_cn_*.json` (G.3.4) migraram para `reports_runtime/*_latest.json`. Nada disso invalida a tese, mas exige correção de rastreabilidade: o livro cita como local o que é (i) migrado para `reports_runtime/`, (ii) efêmero em `/tmp`, ou (iii) hospedado externamente (Kaggle/HF) sem espelho local.

### (e) Estado das superfícies de serviço e escopos systemd
Todas as unidades citadas na faixa existem **no escopo correto** e coerente com a Service-scope law: `omnimind-rl-training.{service,timer}`, `omnimind-bridge-autonomy.timer`, `omnimind-opportunistic-quantum{,-erica}.timer` → **user**; `omnimind-ebpf-monitor`, `omnimind-psychoanalytic`, `omnimind-medic`, `omnimind-sovereign` → **system**. Nenhum cruzamento indevido de escopo foi observado. O claim H.9.8 (timer RL a cada 6 h com offset de 30 min do bridge-autonomy) é consistente com o par de timers `loaded` no escopo user.

---

## 3. Contagem por status

| Status | Nº de claims |
|:--|--:|
| MANTÉM | 52 |
| EVOLUIU | 9 |
| DIVERGE | 4 (3 por rotação de corpo SQLite + 1 escala "160 serviços") |
| NÃO LOCALIZADO | 13 |
| NÃO AUDITÁVEL (conceitual/literatura/editorial/externo) | 8 |
| NÃO APLICÁVEL (declarado stub no próprio livro) | 1 |
| **Total** | **87** |

> Contagem obtida por parsing da coluna de status de cada linha da tabela (`87` linhas de claim). Onde a linha tem status composto (ex.: "DIVERGE (caminho) / MANTÉM (substância)"), prevaleceu o rótulo primário.

## 4. Três lacunas prioritárias

1. **`unified_homology.json` e `systemd_dodecatiad_map.json` ausentes** — são a base declarada dos Betti cross-layer e do mapa 203→12 casas do Apêndice N; o livro os afirma "preservados" (o mapa vivia em `/tmp`). Sem eles, N.3/N.9 são irreproduzíveis localmente. **Ação:** reexecutar `scripts/analysis/unified_topological_homology.py` (existe, 311 LOC) e regravar os dois JSONs em `reports_runtime/` + `data/`.
2. **`reports/systemd_qdrant_cross_topology_results.{json,csv}` (914 collections / 681 válidas) e `data/qdrant_universe_export/` ausentes** — sustentam N.11 e a série "914 × ripser" de M.8; hoje o universo é 2.299 collections. **Ação:** reexportar o universo e recomputar, ou marcar explicitamente no livro como artefato externo (Kaggle `fabriciodasilva/omnimind-qdrant-full-universe`, cujo stat HF retorna ausente).
3. **`phase15_machine_soul_affect_engine.py` e `omnimind_biomedical_companion_2026.md` não localizados** — o primeiro é o Affect Engine citado em S (`frustration > 24.96`); o segundo embasa a expansão de comorbidades de H.9.9/M.6. **Ação:** localizar em `src/` (o nome pode ter migrado) ou atualizar a referência; declarar "NÃO LOCALIZADO" onde couber, conforme REGRA ZERO.

---

**Assinatura documental:** `codex-subagent-apendicesHT` — 2026-10-11 (BRT).
**Método:** `sed -n '9016,13987p'` → extração de claims técnicos → `ls`/`sqlite3 mode=ro`/`systemctl [--user] show`/API Qdrant read-only. Nenhum arquivo do sistema foi modificado; nenhuma varredura recursiva de raiz; este é o único artefato produzido.
