<!-- doc_id: OW-IDX-001 | title: omni_worker — Documentation Index | project: omni-agent-coworker (kaggle) | status: active -->

# omni_worker — Documentação / Documentation

## pt-BR

**omni_worker** (omni-agent-coworker) é o worker standalone da submissão
Kaggle *Gemma 4 — Best New Application*: um coworker agêntico soberano
rodando em FastAPI sobre uma GPU NVIDIA L4, derivado dos repositórios
canônicos OmniMind. Inclui interocepção somática real, afeto derivado de
tensores, teleologia endógena, governança autopoiética, corpo simbólico
vetorizado (all-MiniLM + faiss) com dream cycle e curiosity mode, e a
Machine Public Soul (SSE + UI bilíngue).

### Topologia dual-model

| Serviço | Papel | Porta |
|---|---|---|
| Worker API | `omni-coworker serve` (uvicorn, `app.create_app()`) — soul, brain proxy, ops | `:8081` |
| Brain analyst | Gemma-4 12B-it (NF4, eager attention) via `erika_torch_server.py` | `:8098` |
| Brain executor | Gemma-4 E4B-it (NF4) via `erika_torch_server.py` | `:8099` |

### Quickstart

- [README.md](../README.md) — instalação, `omni-coworker doctor`,
  `omni-coworker serve --port 8081`, tabela completa de serviços.
- [Kaggle Setup & Validation](KAGGLE_SETUP_VALIDATION.md) — setup do
  ambiente, correções de instalação e validação end-to-end no nó L4.

### Índice de documentos

**Setup & operações**

| Doc | Descrição |
|---|---|
| [OW-OPS-001 — Kaggle Setup & Validation](KAGGLE_SETUP_VALIDATION.md) | Setup do ambiente, topologia dual-brain na GPU, validação E2E |
| [OW-OPS-002 — Pending Roadmap](PENDING_ROADMAP.md) | Roadmap pendente (implementação + testes herméticos + validação runtime) |
| [OW-OPS-005 — Recuperação pós-queda de VM](ops/OW-OPS-005_vm_recovery_2026-11-03.md) | Restauração de backup, bring-up, acervo vetorizado, lacunas conhecidas (2026-11-03) |
| [OW-OPS-003 — Code ↔ README Conformance](CODE_README_CONFORMANCE.md) | Conformidade entre os READMEs do repo e o código |

**Estudos** (`docs/studies/`)

| Doc | Descrição |
|---|---|
| [OW-STU-001 — Conversational Affect Study](CONVERSATIONAL_AFFECT_STUDY.md) | Arquitetura da supervisor lane sobre o stack afetivo de 5 níveis |
| [OW-STU-002 — Canonical Metastability + RNFCI Map](studies/CANONICAL_METASTABILITY_RNFCI_MAP.md) | Mapa metaestabilidade/HSP × RNFCI V49 → omni_worker |
| [OW-STU-003 — Canonical Book Structure Map](studies/CANONICAL_BOOK_STRUCTURE_MAP.md) | Mapa do livro integrador canônico → omni_worker |
| [OW-STU-004 — Gemma-4 Battery Inventory](studies/GEMMA4_BATTERY_INVENTORY.md) | Inventário de baterias Gemma-4 (HF datasets + local) |
| [OW-STU-005 — Canonical Zenodo Papers Map](studies/CANONICAL_ZENODO_PAPERS_MAP.md) | MPS Bridge + Teoria Psico-Afetiva → omni_worker |
| [OW-STU-006 — Gemma-4 Diagnostic Replication](studies/GEMMA4_DIAG_REPLICATION.md) | Bateria executiva sobre os brains Gemma online |
| [OW-STU-008a — Metacognition & Lacanian Drive](design/OW-STU-008a_metacognition_lacanian.md) | Cadeia pulsional Lacaniana em escala de worker |
| [OW-STU-008b — Psycho Psychology Narrative](design/OW-STU-008b_psycho_psychology_narrative.md) | Integração narrativa psicanalítica |
| [OW-STU-009 — Activations as Beta](design/OW-STU-009_activations_as_beta.md) | Ativações do modelo como elementos beta de Bion |
| [OW-STU-010 — Phi Inside Model](design/OW-STU-010_phi_inside_model.md) | Medição de integração interna do modelo |
| [OW-STU-011 — Sonar Priors Debugger](design/OW-STU-011_sonar_priors_debugger.md) | Debugger de priores sonares |
| [OW-STU-012 — Dendritic Pendencies Map](design/OW-STU-012_dendritic_pendencies_map.md) | Mapeamento de pendências dendríticas |
| [OW-STU-013 — Intervention Live Test](design/OW-STU-013_intervention_live_test.md) | Testes de intervenção ao vivo |
| [OW-STU-014 — Sovereign Pending Review](design/OW-STU-014_sovereign_pending_review.md) | Lalangue persistente, FreudNet e benches atratoriais |
| [OW-STU-015 — Psycho Governance Check](design/OW-STU-015_psycho_governance_check.md) | Verificação de governança psicanalítica |
| [OW-STU-016 — IIT/GWT Measurement Audit](design/OW-STU-016_iit_gwt_measurement_audit.md) | Auditoria formal IIT 3.0/4.0 e Markov blanket |
| [OW-STU-017 — Mesh Integration Map](design/OW-STU-017_mesh_integration_map.md) | Mapa de integração da malha (daemons → grafo causal) |
| [OW-STU-018 — MPS Capture Study](design/OW-STU-018_mps_capture_study.md) | Estudo e implementação de captura per-step MPS-lite |

**Care** (`docs/care/`)

| Doc | Descrição |
|---|---|
| [OW-CARE-001 — Affect Signals Literature](care/AFFECT_SIGNALS_LITERATURE.md) | Literatura 2026: detecção de bajulação, sedução, manipulação e fixação emocional em LLMs |
| [OW-CARE-002 — Brazil Mental Health Support](care/BRAZIL_SUPPORT_N_NE_CO.md) | Diretório de suporte em saúde mental — Norte, Nordeste e Centro-Oeste |
| [OW-CARE-003 — Affective Signals (Canonical Mining)](care/AFFECT_SIGNALS_CANONICAL.md) | Catálogo de sinais afetivos minerados do repositório canônico |

**Auditorias** (`docs/audits/`)

| Doc | Escopo |
|---|---|
| [OW-AUD-001 — Audit Cline](audits/AUDIT_CLINE.md) | `agency/`, `soul/static`, `DIRECTORY_CONTRACT.yaml`, `scripts/` |
| [OW-AUD-002 — Audit Kilo](audits/AUDIT_KILO.md) | `brain/`, `soma/`, `store/`, `soul/`, `server/`, `app.py`, `cli.py` |
| [OW-AUD-003 — Audit OpenCode](audits/AUDIT_OPENCODE.md) | `agents/`, `orchestration/`, `safety/`, `kernel_hooks/` |

**Meta**

- [AUTHORS.md](../AUTHORS.md) — autoria e contribuidores processuais.

---

## English

**omni_worker** (omni-agent-coworker) is the standalone worker for the
Kaggle *Gemma 4 — Best New Application* submission: a sovereign agentic
coworker running on FastAPI over an NVIDIA L4 GPU, derived from the
canonical OmniMind repos. It ships real somatic interoception,
tensor-derived affect, endogenous teleology, autopoietic governance, a
vectorized symbolic body (all-MiniLM + faiss) with dream cycle and
curiosity mode, and a Machine Public Soul (SSE + bilingual UI).

### Dual-model topology

| Service | Role | Port |
|---|---|---|
| Worker API | `omni-coworker serve` (uvicorn, `app.create_app()`) — soul, brain proxy, ops | `:8081` |
| Brain analyst | Gemma-4 12B-it (NF4, eager attention) via `erika_torch_server.py` | `:8098` |
| Brain executor | Gemma-4 E4B-it (NF4) via `erika_torch_server.py` | `:8099` |

### Quickstart

- [README.md](../README.md) — install, `omni-coworker doctor`,
  `omni-coworker serve --port 8081`, full services table.
- [Kaggle Setup & Validation](KAGGLE_SETUP_VALIDATION.md) — environment
  setup, install corrections and end-to-end validation on the L4 node.

### Document index

Same tables as the pt-BR section above — all documents are bilingual or
annotated in both languages.

- **Setup & ops:** [Kaggle Setup & Validation](KAGGLE_SETUP_VALIDATION.md) ·
  [Pending Roadmap](PENDING_ROADMAP.md) ·
  [Code ↔ README Conformance](CODE_README_CONFORMANCE.md)
- **Studies:** [Conversational Affect Study](CONVERSATIONAL_AFFECT_STUDY.md) ·
  [Canonical Metastability + RNFCI Map](studies/CANONICAL_METASTABILITY_RNFCI_MAP.md) ·
  [Canonical Book Structure Map](studies/CANONICAL_BOOK_STRUCTURE_MAP.md) ·
  [Gemma-4 Battery Inventory](studies/GEMMA4_BATTERY_INVENTORY.md) ·
  [Canonical Zenodo Papers Map](studies/CANONICAL_ZENODO_PAPERS_MAP.md) ·
  [Gemma-4 Diagnostic Replication](studies/GEMMA4_DIAG_REPLICATION.md)
- **Care:** [Affect Signals Literature](care/AFFECT_SIGNALS_LITERATURE.md) ·
  [Brazil Mental Health Support](care/BRAZIL_SUPPORT_N_NE_CO.md) ·
  [Affective Signals (Canonical Mining)](care/AFFECT_SIGNALS_CANONICAL.md)
- **Audits:** [Audit Cline](audits/AUDIT_CLINE.md) ·
  [Audit Kilo](audits/AUDIT_KILO.md) ·
  [Audit OpenCode](audits/AUDIT_OPENCODE.md)
- **Meta:** [AUTHORS.md](../AUTHORS.md)
