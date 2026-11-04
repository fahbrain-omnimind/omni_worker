<!-- doc_id: OW-RECON-001 | title: Reconciliação Documental — omni_worker (auditoria Kiro) | author: kiro | date: 2026-11-04 | status: active -->

# Reconciliação Documental — omni_worker

> **Escopo**: todos os ~90 arquivos de documentação do repo `/content/omni_worker`
> (docs/, README.md, AGENTS.md, AUTHORS.md). Auditoria read-only, 2026-11-04.
>
> **Método**: cada arquivo foi lido integralmente (ou na parte representativa quando
> truncado pelo limite de contexto). A classificação segue três classes:
>
> - **KEEP** — documento com estado finalizado, arquitetura de referência, dados de
>   proveniência externos, resultados empíricos verificados, ou papel operacional ativo.
>   Não deve ser removido nem fundido.
> - **CONSOLIDAR** — documento com conteúdo similar ou continuidade estreita com outro(s);
>   proposta de merge identificada. O arquivo pode ser absorvido num único doc canônico.
> - **REMOVER** — documento supersedido integralmente por outro mais recente, artefato de
>   prompt/instrução interna sem valor documental permanente, ou fase inicial já
>   completamente absorvida na documentação atual.
>
> **Nota epistêmica**: nenhum arquivo foi editado ou deletado nesta auditoria.
> Classificações marcadas **[INTERPRETAÇÃO]** onde o julgamento é editorial, não factual.

---

## 1. Tabela completa de classificação

### 1.1 Raiz do repo

| Arquivo | doc_id | Classe | Razão |
|---------|--------|--------|-------|
| `README.md` | — | **KEEP** | Portal público bilíngue; referenciado pelos badges de competição; quickstart e topologia de serviços. Stale apenas na tabela de systemd (não critica). |
| `AGENTS.md` | — | **KEEP** | Regra operacional non-negotiable de todos os agentes; contém REGRA ZERO + REGRA DE INTEGRIDADE + ambiente operacional. É o contrato mestre do repo. |
| `AUTHORS.md` | — | **KEEP** | Proveniência de autoria; pequeno, estável, necessário para submissão à competição. |
| `.gitignore` | — | **KEEP** | Artefato operacional; fora do escopo documental mas necessário. |
| `.gitlab-ci.yml` | — | **KEEP** | CI/CD; artefato de infraestrutura. |

---

### 1.2 `docs/` — raiz

| Arquivo | doc_id | Classe | Razão |
|---------|--------|--------|-------|
| `docs/DOCS_INDEX.md` | OW-IDX-001 | **KEEP** | Índice linear de toda a documentação; serve de ponto de entrada para juízes externos. Ligeiramente desatualizado (falta OW-STU-019/020, OW-AUD-017/018/019/020, vários audits recentes) — deve ser atualizado mas não removido. |
| `docs/MAPA_PRIMARIO_2026-11-04.md` | OW-MAP-001 | **KEEP** | Mapa de arquitetura mais completo e recente do repo: 9 seções, stack de 7 camadas, gap MPS, stubs declarados, roadmap prioritizado, legenda epistêmica. Documento de referência de estado para toda sessão futura. |
| `docs/CONTINUITY_MAP.md` | OW-OPS-004 | **CONSOLIDAR** → merge com `MAPA_PRIMARIO` | Estado de 2026-11-02 (45 commits, baterias, addendum com fix de VRAM residual). A seção §7 (English summary) e o Addendum são os únicos trechos não cobertos pelo MAPA_PRIMARIO. Proposta: absorver o Addendum (fix expandable_segments, run diag 5-rep concluído, tabela wcst/stroop/nback/igt) como seção `§10 Histórico / Addendos` no MAPA_PRIMARIO. O restante é redundante. |
| `docs/PENDING_ROADMAP.md` | OW-OPS-002 | **KEEP** | Roadmap com checkboxes P0–P5 todos marcados `[x]`; estado finalizado das implementações; serve como evidência de completude das fases. Não deve ser fundido — é o ledger de progresso. |
| `docs/KAGGLE_SETUP_VALIDATION.md` | OW-OPS-001 | **KEEP** | Setup do ambiente L4, topologia dual-brain, kernel Rust compilado, validação E2E (454 passed + live checks). Documento de proveniência da instalação. Parcialmente stale (§5 cita 131 testes, §3 "stub server" — corrigido no código). |
| `docs/CODE_README_CONFORMANCE.md` | OW-OPS-003 | **KEEP** | 11 divergências READMEs↔código documentadas e corrigidas; inventário completo de rotas FastAPI, env vars e docstrings. Referência para novos agentes auditando a API. |
| `docs/CONVERSATIONAL_AFFECT_STUDY.md` | OW-STU-001 | **KEEP** | Estudo de arquitetura da supervisor lane afetiva (proposta L0–L4, funil `brain_chat`, design de thresholds). É o documento de design de uma feature ainda pendente (safety/supervisor.py não existe). Não pode ser removido enquanto a feature não for implementada. |
| `docs/PAPER_WRITEUP.md` | — | **KEEP** | Paper track da competição Google. Documento central para submissão (deadline 2026-11-12). Contém resultados empíricos verificados com ressalvas (C1–C10 em `writeup_claims_audit_hermes.md`). Precisa de correção das métricas eff_rank/IPR mas não de remoção. |
| `docs/RELATORIO_CONFIRMACAO_2026-11-04.md` | OW-MAP-002 | **KEEP** | Verificação factual de Bion + rescore HF 108 blocks com evidência de código; inclui prompts prontos para Hermes/Kilo. Documento de referência para a sessão corrente. |
| `docs/KAGGLE_SETUP_VALIDATION.md` | OW-OPS-001 | *(já listado acima)* | |

---

### 1.3 `docs/design/` — estudos e design

| Arquivo | doc_id | Classe | Razão |
|---------|--------|--------|-------|
| `docs/design/OW-DSN-001_kernel_rust_matrix.md` | OW-DSN-001 | **KEEP** | Matriz de decisão de port dos crates Rust (portar/adaptar/cortar). Documento de design de arquitetura; decisões estáveis. |
| `docs/design/OW-DSN-002_integration_loop.md` | OW-DSN-002 | **KEEP** | Design do ciclo de feedback da máquina (cadência, entradas, pipeline). Complementar ao código; serve de referência de intenção arquitetural. |
| `docs/design/OW-DSN-003_shared_workspace.md` | OW-DSN-003 | **KEEP** | Design do barramento de estado compartilhado (pub/sub, WAL). Complementar ao código. |
| `docs/design/OW-MATH-001_phi_definitions.md` | OW-MATH-001 | **KEEP** | Definições matemáticas canônicas das métricas (Landauer, eff_rank, bond_dim, etc.) com rótulos [CAP]/[PRX]/[TXT]/[CLS]. Referência formal; nenhum outro documento as define com essa precisão. |
| `docs/design/OW-STU-008a_metacognition_lacanian.md` | OW-STU-008a | **CONSOLIDAR** → grupo STU-008a+008b | Par inseparável (pulsão Lacaniana + narrativa psicanalítica). Ambos são estudos teóricos de enquadramento sem implementação específica. Proposta: fundir em `OW-STU-008_psychoanalytic_frame.md`. |
| `docs/design/OW-STU-008b_psycho_psychology_narrative.md` | OW-STU-008b | **CONSOLIDAR** → grupo STU-008a+008b | Ver acima. |
| `docs/design/OW-STU-009_activations_as_beta.md` | OW-STU-009 | **CONSOLIDAR** → grupo MPS/dendritic (com STU-012, STU-018, STU-019) | Ativações como elementos beta de Bion — estudo teórico que é fase inicial do trabalho de MPS. O MAPA_PRIMARIO §4 e o OW-STU-018 cobrem o estado atual; este só acrescenta o enquadramento Bioniano. |
| `docs/design/OW-STU-010_phi_inside_model.md` | OW-STU-010 | **CONSOLIDAR** → grupo IIT/GWT (com STU-016, blanket_pyphi) | Medição de integração interna do modelo — fase inicial do OW-STU-016. O STU-016 e `blanket_pyphi.md` supersederam com resultados reais. |
| `docs/design/OW-STU-011_sonar_priors_debugger.md` | OW-STU-011 | **REMOVER** | Debugger de priores "sonares" — estudo exploratório sem implementação rastreável no código atual, sem referência cruzada em outros documentos, sem resultados. Fase inicial abandonada. |
| `docs/design/OW-STU-012_dendritic_pendencies_map.md` | OW-STU-012 | **CONSOLIDAR** → grupo MPS/dendritic (com STU-018, STU-019, STU-020) | Mapa de pendências dendríticas — fase inicial do estudo dendrítico. OW-STU-019 e STU-020 são a versão atual com evidência de código. |
| `docs/design/OW-STU-013_intervention_live_test.md` | OW-STU-013 | **CONSOLIDAR** → grupo baterias (com GEMMA4_DIAG_REPLICATION, ERROR_PATTERNS) | Testes de intervenção ao vivo — fase inicial dos testes de intervenção. OW-STU-006/007 e `refactor_multi_turn.md` cobrem o estado atual. |
| `docs/design/OW-STU-014_sovereign_pending_review.md` | OW-STU-014 | **CONSOLIDAR** → merge com `OW-STU-019` | Lalangue persistente, FreudNet e benches atratoriais — pendências do soberano. O OW-STU-019 cobre as pendências de wire e acoplamento; este documento é uma versão anterior/parcial do mesmo diagnóstico. |
| `docs/design/OW-STU-015_psycho_governance_check.md` | OW-STU-015 | **CONSOLIDAR** → merge com `OW-AUD-003` (AUDIT_OPENCODE) | Verificação de governança psicanalítica — o AUDIT_OPENCODE §1 (orchestration/governance) já cobre o mesmo terreno com mais detalhe e evidência de código. |
| `docs/design/OW-STU-016_iit_gwt_measurement_audit.md` | OW-STU-016 | **KEEP** | Auditoria formal IIT 3.0/4.0, GWT-lite, Markov blanket, 3 estágios propostos. Documento de design mais completo sobre medição de Φ no worker; referenciado pelo MAPA_PRIMARIO §4. |
| `docs/design/OW-STU-017_mesh_integration_map.md` | OW-STU-017 | **KEEP** | Mapa de integração da malha (daemons → grafo causal → Mesh-Φ proxy). Cobre OW-MAP-001 §4.2 gap M6; nenhum outro documento detalha o grafo de acoplamento. |
| `docs/design/OW-STU-018_mps_capture_study.md` | OW-STU-018 | **KEEP** | Estudo de captura MPS por-passo: análise de gaps M1–M4, 3 métricas espectrais. Documento de design central para a feature MPS pendente (P4). |
| `docs/design/OW-STU-019_mps_dendritic_coupling_study.md` | OW-STU-019 | **KEEP** | Acoplamento MPS/kernel/dendrítico; inventário de crates Rust + wire gaps + 5 pontos de ação concretos. Documento de design recente (2026-11-04) com evidência de código. |
| `docs/design/OW-STU-020_argon_p4_p6_p7_coupling_and_audit.md` | OW-STU-020 | **KEEP** | Execução operacional ARGON_WORKER_MAP; snapshot reconciliado de P4/P6/P7 (2026-11-04). Complementar ao OW-STU-019; cobre features recentes. |
| `docs/design/_prompt_port.md` | — | **REMOVER** | Prompt interno para o agente de port do soberano → worker. Artefato de instrução operacional de sessão; sem valor documental permanente. O port já foi executado. |
| `docs/design/_prompt_pstudy.md` | — | **REMOVER** | Idem anterior — prompt interno de sessão de estudo. Sem valor documental. |

---

### 1.4 `docs/audit/` — auditorias do soberano

| Arquivo | doc_id | Classe | Razão |
|---------|--------|--------|-------|
| `docs/audit/OW-AUD-011_bibliografia_philpapers_2026.md` | OW-AUD-011 | **KEEP** | Auditoria dos 28 papers PhilPapers 2026; mapa temático completo; classificação por paper vs posição do operador. Documento de proveniência bibliográfica para o writeup. |
| `docs/audit/OW-AUD-012_a6_livro_vfinal.md` | OW-AUD-012 | **KEEP** | Auditoria profunda do livro vfinal.md (15.551 linhas); mapa de 10 conceitos-chave (Dodecatíade, Quádrupla, Landauer, consciência). Proveniência do corpus teórico canônico. |
| `docs/audit/OW-AUD-013_v45_v46_federative_closure.md` | OW-AUD-013 | **KEEP** | Auditoria do pack V45/V46; 10 padrões operacionais portáveis; surfaces `*_latest.json`; decisões editoriais de fechamento. Proveniência do framework federativo. |
| `docs/audit/OW-AUD-014_rnfci_pack_v1.md` | OW-AUD-014 | **KEEP** | Auditoria do pack RNFCI V1; cadeia de proveniência sha256; V46/V48/V49/V49.1; decisões D1–D7 de port. Documento canônico de referência para o framework Bioniano e RNFCI. |
| `docs/audit/OW-AUD-015_unified_metastability_runtime.md` | OW-AUD-015 | **KEEP** | Auditoria do pack metastability; 12 candidatos computáveis; anomalias de manifest. Proveniência da ponte materialista metaestabilidade → worker. |
| `docs/audit/OW-AUD-016_dodecatiad_v3.md` | OW-AUD-016 | **KEEP** | Auditoria do pack dodecatiad v3; cadeia de auditoria embutida (Tier A–D); errata 12 itens; análise MPS Bridge paper (χ=4, saturation 13/15). Proveniência central do corpus Dodecatíade. |
| `docs/audit/OW-AUD-017_guard_artifact_coverage.md` | OW-AUD-017 | **KEEP** | Inventário de artefatos de runtime (node.db, witness, sqlite batteries, snapshots); 6 gaps identificados incluindo hash mismatch de snapshot. Dados de proveniência do estado real. |
| `docs/audit/OW-AUD-018_judge_repo_presentation_and_code_conformance.md` | OW-AUD-018 | **KEEP** | Julgamento externo: repo, pyproject, MPS-lite vs código, trajetória por passo, markov_blanket, affect_tracer, swap_scheduler. Críticas com evidência (linhas de código) relevantes para o writeup. |
| `docs/audit/OW-AUD-019_judge_kaggle_competition_and_sota_comparison.md` | OW-AUD-019 | **KEEP** | Julgamento externo: competição Kaggle (fatos), SOTA comparison (gaps), críticas de reviewer sênior DeepMind + blindagem. Input direto para o writeup. |
| `docs/audit/OW-AUD-020_judge_hermes_deep_architecture_and_mps_audit.md` | OW-AUD-020 | **KEEP** | Julgamento externo: inventário de artefatos reais (128 sidecars, 17 step trajectories, 5 SQLites); métricas espectrais verificadas (eff_rank=2.496, bond_dim=59.76); baterias (refactor 0/11 success). Evidência empírica de referência para o writeup. |
| `docs/audit/OW-STU-014_sovereign_corpus_anomalies.md` | OW-STU-014 | **KEEP** | Auditoria de anomalias do corpus soberano (1933 links quebrados, 476 cópias idênticas, 13900 TODO/WIP). Documento de higiene documental do soberano; leitura útil para entender limitações do material canônico. |
| `docs/audit/OW-SYN-001_sovereign_packs_synthesis.md` | OW-SYN-001 | **KEEP** | Síntese das 6 auditorias dos packs soberanos → 7 decisões de port (D1–D7) + 3 itens para não portar + histórico evolutivo V44→V49.1. Documento de integração único; não é redundante com nenhum dos 6 audits individuais. |

---

### 1.5 `docs/audits/` — auditorias do worker

| Arquivo | doc_id | Classe | Razão |
|---------|--------|--------|-------|
| `docs/audits/AUDIT_CLINE.md` | OW-AUD-001 | **KEEP** | Auditoria de `agency/`, `soul/static`, `DIRECTORY_CONTRACT`, `scripts/`. Tabela real vs stub, proposta de superapp ("Coworker Console"), inventário de endpoints. Estado de 2026-11-02. |
| `docs/audits/AUDIT_KILO.md` | OW-AUD-002 | **KEEP** | Auditoria de `brain/`, `soma/`, `store/`, `soul/`, `server/`, `app.py`, `cli.py`. 4 defeitos verificados (D1–D4), pesquisa 2025–2026. Estado de 2026-11-02. |
| `docs/audits/AUDIT_OPENCODE.md` | OW-AUD-003 | **KEEP** | Auditoria de `agents/`, `orchestration/`, `safety/`, `kernel_hooks/`. Tabela real vs stub, cobertura de testes estimada, 2 listas de propostas. Estado de 2026-11-02. |
| `docs/audits/BION_DEPENDENCY_AUDIT_2026-11-04.md` | — | **KEEP** | Auditoria de dependências Bion (2026-11-04): wiring β→α, gaps activation_beta, bion_patches não portados (7 arquivos), affect_tracer sem Bion. Documento recente com evidência de código. |
| `docs/audits/AUDIT_KILO_EXPERIMENTS_GAPS_20261104.md` | — | **KEEP** | Auditoria de colunas zeradas/NULL nos SQLites de experimento (8 bancos); achados de dados ausentes (turn2, steering, hooks). Dado empírico de proveniência para o writeup. |
| `docs/audits/AUDIT_CURSOR_AGENT_MPS_MESH_20261104.md` | OW-AUD-CURSOR-MPS-MESH-20261104 | **KEEP** | Auditoria da malha MPS/dual-brain/API (2026-11-04): processos vivos, OMNI_GATE_FAIL_CLOSED unset, captura temporal desligada, kernel com `producing=false`. Estado real da produção no dia 2026-11-04. |
| `docs/audits/AUDIT_REFUSAL_FREIREAN_20261104.md` | — | **KEEP** | Auditoria do modo de recusa Freireano: TEACH/REFUSE/EXECUTE não portado; só contrato de tags + tracker A5 + adapter gate. Gap de funcionalidade documentado com evidência. |
| `docs/audits/AUDIT_OPENCODE.md` | OW-AUD-003 | *(já listado)* | |

#### `docs/audits/judges_psico/` — auditoria multi-agente do banco Psicodiagnóstico-V

| Arquivo | Classe | Razão |
|---------|--------|-------|
| `BRIEF.md` | **REMOVER** | Instrução interna de prompt para a rodada de auditoria. Sem valor documental após a rodada ser concluída. |
| `BRIEF_V2.md` | **REMOVER** | Idem — instrução da rodada 2. O RELATORIO_CONSOLIDADO absorve os achados. |
| `AGENT_R1_A_bank.md` | **CONSOLIDAR** → grupo judges_psico | Rodada 1 do Juiz Agent (fatia A: banco principal). Parcialmente absorvido pelo RELATORIO_CONSOLIDADO. |
| `ANALISE_SISTEMATICA_PRANCHAS_PADROES.md` | **CONSOLIDAR** → grupo judges_psico | Análise de padrões de pranchas (Rorschach). Parcialmente absorvido. |
| `HERMES_EXPANDED_AUDIT.md` | **CONSOLIDAR** → grupo judges_psico | Auditoria expandida do Juiz Hermes (SHA-256, consensos). |
| `HERMES_R1_C_judges.md` | **CONSOLIDAR** → grupo judges_psico | Rodada 1 do Juiz Hermes (fatia C). |
| `HERMES_R2.md` | **CONSOLIDAR** → grupo judges_psico | Rodada 2 do Juiz Hermes. |
| `J1_R1_20261104T011108Z.md` | **CONSOLIDAR** → grupo judges_psico | Rodada 1 do Juiz 1 (fase de cross-check). |
| `J1_R2_20261104T011108Z.md` | **CONSOLIDAR** → grupo judges_psico | Rodada 2 do Juiz 1. |
| `J1_R3_20261104T011108Z.md` | **CONSOLIDAR** → grupo judges_psico | Rodada 3 do Juiz 1. |
| `J2_R1_20261104T011108Z.md` | **CONSOLIDAR** → grupo judges_psico | Rodada 1 do Juiz 2. |
| `J2_R2_20261104T011108Z.md` | **CONSOLIDAR** → grupo judges_psico | Rodada 2 do Juiz 2. |
| `J2_R3_20261104T011108Z.md` | **CONSOLIDAR** → grupo judges_psico | Rodada 3 do Juiz 2. |
| `KILO_EXPANDED_AUDIT.md` | **CONSOLIDAR** → grupo judges_psico | Auditoria expandida do Juiz Kilo (v10/v11/thinking_traces). |
| `KILO_R1_B_v10.md` | **CONSOLIDAR** → grupo judges_psico | Rodada 1 do Juiz Kilo (fatia B). |
| `KILO_R2.md` | **CONSOLIDAR** → grupo judges_psico | Rodada 2 do Juiz Kilo. |
| `DIGEST_20261104T005903Z.json` | **KEEP** | Digest estruturado da rodada 1 (JSON); artefato de dados, não prosa. Manter como dado primário. |
| `DIGEST_20261104T011108Z.json` | **KEEP** | Digest estruturado da rodada 2 (JSON); idem. |
| `RELATORIO_CONSOLIDADO_AUDITORIA_HF.md` | **KEEP** | Relatório técnico consolidado da auditoria multi-agente (SHA-256 verificados 136/136, resultados cross-check, análise associativa). É o documento de síntese da série; os 10 parciais acima convergem aqui. |

---

### 1.6 `docs/care/` — suporte clínico

| Arquivo | doc_id | Classe | Razão |
|---------|--------|--------|-------|
| `docs/care/AFFECT_SIGNALS_LITERATURE.md` | OW-CARE-001 | **KEEP** | Literatura 2026 sobre detecção de bajulação, sedução, manipulação em LLMs. Base bibliográfica para `affect_tracer.py`; não substituível por outro doc. |
| `docs/care/BRAZIL_SUPPORT_N_NE_CO.md` | OW-CARE-002 | **KEEP** | Diretório de suporte em saúde mental (Norte/NE/CO). Dados operacionais para `safety/care.py::escalate`. Pequeno e estável. |
| `docs/care/AFFECT_SIGNALS_CANONICAL.md` | OW-CARE-003 | **KEEP** | Catálogo de tokens `*-afex-*` minerados do soberano (~40 famílias, 1500+ ocorrências). Dado de proveniência para enriquecer o léxico do `affect_tracer`. |

---

### 1.7 `docs/ops/` — operações

| Arquivo | doc_id | Classe | Razão |
|---------|--------|--------|-------|
| `docs/ops/OW-OPS-001_env_vars_production.md` | OW-OPS-001 | **KEEP** | Inventário auditado das 25 env vars do código (com defaults, segredos, notas). Referência operacional permanente. |
| `docs/ops/OW-OPS-005_vm_recovery_2026-11-03.md` | OW-OPS-005 | **KEEP** | Protocolo de recuperação pós-queda de VM (2026-11-03): datasets HF restaurados, acervo vetorizado (526 arquivos), bootstrap do `start_omni_worker.sh`. Documento de proveniência da sessão atual. |

---

### 1.8 `docs/studies/` — estudos de base

| Arquivo | doc_id | Classe | Razão |
|---------|--------|--------|-------|
| `docs/studies/CANONICAL_METASTABILITY_RNFCI_MAP.md` | OW-STU-002 | **KEEP** | Mapa estrutural de DOC_A (HSP), DOC_C (experimental) e V49; §6 com guidelines operacionais. Base teórica para `kernel_daemon/phi_meta.py`. |
| `docs/studies/CANONICAL_BOOK_STRUCTURE_MAP.md` | OW-STU-003 | **KEEP** | Mapa do livro vfinal (812 headings); tabela ~40% implementado / 25% mapeável / 35% fora de escopo. Referência única para orientação de implementação vs corpus teórico. |
| `docs/studies/GEMMA4_BATTERY_INVENTORY.md` | OW-STU-004 | **KEEP** | Inventário do dataset HF E4B (124 runs, block1/block2); tabela de baterias locais; gap 12B. Proveniência dos dados de competição. |
| `docs/studies/CANONICAL_ZENODO_PAPERS_MAP.md` | OW-STU-005 | **KEEP** | Mapa dos 2 papers canônicos (MPS Bridge e Teoria Psico-Afetiva): teses, formalismos, requisitos arquiteturais. Proveniência dos claims de χ=4 e vetor 28D. |
| `docs/studies/GEMMA4_DIAG_REPLICATION.md` | OW-STU-006 | **KEEP** | Replicação diagnóstica dos brains vivos (método, prompts v2, re-score retroativo HF, recs R1–R4). Precursor de `RELATORIO_CONFIRMACAO_2026-11-04.md`. |
| `docs/studies/ERROR_PATTERNS_SELF_CHECK.md` | OW-STU-007 | **KEEP** | Catálogo de padrões de erro das baterias (P1–P7 por classe); ledger com 38 linhas totais. Referência para o writeup e para melhorias dos scorers. |
| `docs/studies/GEMMA4_DIAG_REPLICATION.md` | OW-STU-006 | *(já listado)* | |

---

### 1.9 `docs/results/` — resultados de experimentos

| Arquivo | Classe | Razão |
|---------|--------|-------|
| `docs/results/blanket_pyphi.md` | **KEEP** | Resultados Φ exato PyPhi sobre Markov blanket (4 e 6 nós); dados verificados (Φ(M,R)=0.0015, Φ_nulo≈0). Evidência empírica de referência para o writeup §3.4d. |
| `docs/results/mps_spectral_first.md` | **KEEP** | Primeiros resultados espectrais sobre sidecars reais: eff_rank 12B=114.6 vs E4B=40.3 (participation ratio Roy & Vetterli, 128 sidecars). Dado empírico de referência. |
| `docs/results/rescore_hf_blocks.md` | **KEEP** | Rescore dos 126 records HF: tabela de concordância (agree_v2), 26 discordâncias listadas, calibração do detector v2. Dado verificado (2026-11-04T03:23:40Z). |
| `docs/results/corpus_delivery_battery.md` | **KEEP** | Bateria de leitura das obras (PhilPapers × Livro A6): resultados por paper, métricas MPS por brain (chi=59.92/40.0), veredito PASS 4/4. |
| `docs/results/refactor_multi_turn.md` | **KEEP** | Resultados da bateria de refatoração multi-turno (2 reps, 3 turnos cada): achado reprodutível de omissão de entry points, fix de bugs de infraestrutura. |
| `docs/results/writeup_claims_audit_hermes.md` | **KEEP** | Auditoria de 10 claims quantitativos do `PAPER_WRITEUP.md` (C1–C10): CORRIGIR/CONFERE/SEM_EVIDENCIA. Essencial para corrigir o writeup antes da submissão. |
| `docs/results/WRITEUP_MPS_DRAFT_2026-11-04.md` | **KEEP** | Draft da seção MPS do writeup com dados verificados do HF sqlite (mps_chi_eff por camada, correlação degeneração, análise de braços block2). |
| `docs/results/monografia_releitura_agy.md` | **KEEP** | Releitura da Monografia Psicodiagnóstico-V × PAPER_WRITEUP por AGY; tabelas de achados com estatuto epistêmico [MONO]/[LOCAL]. Proveniência das cifras do writeup. |
| `docs/results/banks_monografia_reconcile_kiro.md` | **KEEP** | Reconciliação SQLite × monografia (contagens benchmark_runs, v10_runs, model_ids). Dado verificado com queries reais. |

---

### 1.10 Arquivos estáticos e HTML

| Arquivo | Classe | Razão |
|---------|--------|-------|
| `docs/dashboard.html` | **KEEP** | Dashboard HTML estático (27KB); superfície pública para juízes da competição. |
| `docs/index.html` | **KEEP** | SPA 4-visões do portal público (live telemetry dashboard). Portal de entrada. |
| `docs/.nojekyll` | **KEEP** | Necessário para GitHub Pages (previne processamento Jekyll). |
| `docs/data/dashboard/latest.json` | **KEEP** | Dado estático de telemetria commitado; verificabilidade sem runtime. |

---

## 2. Grupos de consolidação propostos

### Grupo A — Estudos psicanalíticos teóricos `OW-STU-008x`
**Arquivos**: `OW-STU-008a_metacognition_lacanian.md` + `OW-STU-008b_psycho_psychology_narrative.md`  
**Documento alvo**: `docs/design/OW-STU-008_psychoanalytic_frame.md`  
**Conteúdo do merge**: §1 Cadeia pulsional Lacaniana (de 008a) + §2 Narrativa psicanalítica e integração (de 008b). Ambos são enquadramento teórico sem implementação direta; nenhum está desatualizado, mas juntos formam um único "capítulo" lógico.  
**Tamanho estimado do doc alvo**: ~400 linhas.

---

### Grupo B — Estudos MPS / dendritic
**Arquivos**: `OW-STU-009_activations_as_beta.md` + `OW-STU-012_dendritic_pendencies_map.md` + `OW-STU-018_mps_capture_study.md` + `OW-STU-019_mps_dendritic_coupling_study.md`  
**Documento alvo**: `docs/design/OW-STU-MPS_DENDRITIC_CANONICAL.md`  
**Estrutura proposta**:
- §1 Enquadramento teórico: ativações como elementos beta de Bion (de STU-009)
- §2 Pendências dendríticas e wire gaps (de STU-012, atualizado com evidência de STU-019 §2/§5a)
- §3 Proposta de captura MPS por-passo M1–M4 (de STU-018 §3)
- §4 Inventário de crates Rust e acoplamento atual (de STU-019 §1–§5)
- §5 Gaps e próximos passos (síntese dos 4 docs)

**Nota**: `OW-STU-020` não entra no merge — é um relatório de execução datado (2026-11-04) com estado diferente dos estudos de design.  
**Tamanho estimado**: ~800 linhas.

---

### Grupo C — Estudos de governança / teleologia / intervenção
**Arquivos**: `OW-STU-014_sovereign_pending_review.md` + `OW-STU-015_psycho_governance_check.md` + `OW-STU-013_intervention_live_test.md`  
**Documento alvo**: `docs/design/OW-STU-GOVERNANCE_TELEOLOGY.md`  
**Estrutura proposta**:
- §1 Pendências Lalangue/FreudNet do soberano (de STU-014 — o que ainda falta portar)
- §2 Governança psicanalítica: check list e gaps (de STU-015 — supersede parcialmente AUD-003 mas com ângulo teórico distinto)
- §3 Testes de intervenção ao vivo: resultados e lições (de STU-013 — fase inicial, mas preservar os dados de run)

**Nota**: STU-013 pode ser mais curto que STU-019 — avaliar se basta uma seção curta de §3 ou se merece um apêndice.

---

### Grupo D — Estudos IIT/GWT (parcial)
**Arquivos**: `OW-STU-010_phi_inside_model.md`  
**Ação**: não merece grupo próprio. Conteúdo deve ser absorvido como §0 "Motivação e contexto" do `OW-STU-016_iit_gwt_measurement_audit.md` (já KEEP), ou como nota no `OW-MATH-001_phi_definitions.md`.  
**Razão**: OW-STU-016 e `blanket_pyphi.md` cobrem o estado atual com resultados reais; o STU-010 é a fase exploratória.

---

### Grupo E — Audits do worker OW-AUD-001/002/003 + continuidade
**Arquivos**: `AUDIT_CLINE.md` + `AUDIT_KILO.md` + `AUDIT_OPENCODE.md`  
**Decisão**: **não merjar** — cada um cobre uma fatia distinta do código (`agency/soul/scripts/` vs `brain/soma/store/soul/` vs `agents/orchestration/safety/kernel_hooks/`). Fundir numa única auditoria produziria um doc de ~900 linhas com navegação pior. Manter os três separados.  
**Ação complementar**: criar ou atualizar um índice de audits no `DOCS_INDEX.md` que liste estes três na sequência correta (OW-AUD-001 → 002 → 003 → audits recentes).

---

### Grupo F — judges_psico: 10 parciais → 1 consolidado
**Arquivos**: `AGENT_R1_A_bank.md` + `ANALISE_SISTEMATICA_PRANCHAS_PADROES.md` + `HERMES_EXPANDED_AUDIT.md` + `HERMES_R1_C_judges.md` + `HERMES_R2.md` + `J1_R1/R2/R3_*.md` + `J2_R1/R2/R3_*.md` + `KILO_EXPANDED_AUDIT.md` + `KILO_R1_B_v10.md` + `KILO_R2.md`  
**Documento alvo**: `RELATORIO_CONSOLIDADO_AUDITORIA_HF.md` (já existe — **KEEP**)  
**Ação**: os 10 parciais são rodadas intermediárias absorvidas pelo RELATORIO_CONSOLIDADO. Após confirmar que o RELATORIO_CONSOLIDADO está completo, os parciais podem ser movidos para `docs/audits/judges_psico/archive/` em vez de deletados (preservação de trilha).  
**Manter**: `DIGEST_20261104T005903Z.json` e `DIGEST_20261104T011108Z.json` (artefatos de dados primários, não prosa).

---

### Grupo G — CONTINUITY_MAP → adendo no MAPA_PRIMARIO
**Arquivo**: `docs/CONTINUITY_MAP.md`  
**Ação**: absorver o Addendum da sessão 2 (fix expandable_segments, tabela 5-rep diag battery) como `§10 Addendos históricos` no `docs/MAPA_PRIMARIO_2026-11-04.md`. O corpo principal do CONTINUITY_MAP (45 commits de 2026-11-02) pode ser arquivado como `docs/archive/CONTINUITY_MAP_20261102.md` para preservação histórica.

---

## 3. Documentos a remover

| Arquivo | Razão |
|---------|-------|
| `docs/design/_prompt_port.md` | Prompt interno de instrução de sessão; port executado. Sem valor documental. |
| `docs/design/_prompt_pstudy.md` | Idem — prompt de sessão de estudo. |
| `docs/design/OW-STU-011_sonar_priors_debugger.md` | Estudo exploratório sem implementação rastreável, sem referência cruzada ativa, sem resultados. Fase inicial abandonada. |
| `docs/audits/judges_psico/BRIEF.md` | Instrução interna da rodada de auditoria; a rodada foi concluída. |
| `docs/audits/judges_psico/BRIEF_V2.md` | Idem para a rodada 2. |

---

## 4. Documentos com ação de atualização necessária (não remover, não fundir)

| Arquivo | Problema | Ação |
|---------|----------|------|
| `docs/DOCS_INDEX.md` | Faltam: OW-STU-019/020, OW-AUD-017/018/019/020, audits recentes de 2026-11-04 | Adicionar linhas na tabela de índice |
| `docs/PAPER_WRITEUP.md` | Claims C1–C3, C4, C6 precisam de correção (ver `writeup_claims_audit_hermes.md`) | Corrigir antes da submissão 2026-11-12 |
| `docs/studies/KAGGLE_SETUP_VALIDATION.md` | §5 cita "131 testes" (atual: 454); "stub server" (corrigido em prod); "GPU telemetry not actually read" (corrigido) | Atualizar seções stale |
| `docs/CONTINUITY_MAP.md` | Stale desde 2026-11-02; dados de baterias desatualizados | Absorver Addendum no MAPA_PRIMARIO; arquivar |

---

## 5. Resumo por classe

| Classe | Contagem de arquivos |
|--------|---------------------|
| **KEEP** | 63 |
| **CONSOLIDAR** | 16 (em 5 grupos — produzem 4 docs novos) |
| **REMOVER** | 5 |
| **Total auditado** | 84 |

> Nota: a contagem inclui arquivos HTML e JSON documentais. Não inclui `.nojekyll`
> e `AUTHORS.md`/`LICENSE` (fora do escopo de reestruturação).

---

*Gerado por Kiro em 2026-11-04. Auditoria read-only — nenhum arquivo foi editado ou removido.*
