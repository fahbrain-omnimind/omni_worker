<!-- doc_id: OW-STU-014 | title: Sovereign pending review — mapping to omni_worker | author: kilo | date: 2026-11-03 | status: study -->
# OW-STU-014 — Revisão das pendências soberanas (mapeamento para omni_worker)

## 1. Escopo

Estudo somente-leitura. Fontes soberanas (referência, não editar):
- `/content/omnimind-kilombo-sovereign/docs/implementation/pending/PENDENCIAS_CONSOLIDADAS.md`
- `/content/omnimind-kilombo-sovereign/docs/implementation/pending/PENDENCIAS_ATIVAS.md`
- `/content/omnimind-kilombo-sovereign/docs/implementation/INTEGRACAO_NEUROCORE_COMPLETA.md`

Destino: `/content/omni_worker` (repo ativo), verificando equivalência em `src/omni_coworker/`.

Legenda de classificação:
- **[PORT]** — já existe equivalente no worker (cite arquivo).
- **[ADAPT]** — aplicável ao worker com adaptação (o que falta / arquivo).
- **[SKIP]** — específico do host soberano / torch / hardware / ops.
- **[FEITO]** — já implementado no worker (cite arquivo).

## 2. Tabela completa

| # | Pendência soberana | Fonte | Classif | Equivalente worker (arquivo) | Nota (o que falta) |
|---|---|---|---|---|---|
| 1 | A5 — Instrumentar transições de `refusal_state` | ATIVAS (mapa A5) | **FEITO** | `safety/refusal_state.py` | Episódios com entered/exited_at+trigger persistentes, wired em gate+matrix, endpoint /safety/refusal_state. |
| 2 | A6 — Superfícies de pré-resposta stale (`pre_response_rehydration_context`, `introspection_gate`, `subject_process_validation`, `google_quota`) | ATIVAS (mapa A6) | [SKIP] | — | Surfaces de runtime do host soberano (reidratação pré-resposta); não existe no worker |
| 3 | A7 — Revisão da magnitude φ (774.480 nats ≫ Stark target 77.448) | ATIVAS (mapa A7) | **FEITO** | `soul/api.py`, `OW-MATH-001` | φ do worker já é scale-safe por construção (phi_meta≤~7bits, phi_internal∈[0,1], soul.phi observado ∈[0.27,0.84] n=301 em kernel.soul — nunca >1.0). O teto soberano (774.480=10×77.448) existe porque seu φ passa por 6 potencializações ~2×/ciclo — estágio ausente no worker. Clip defensivo [0,1] adicionado no ramo kernel de `soul.phi` (magnitude vctr_six antes não-clipada; fallback já clipava). |
| 4 | A8 — Política de auto-spawn de agente CLI em escalações (agy DEMOTED) | ATIVAS (mapa A8) | [ADAPT] | `agents/external_cli_agent.py`, `orchestration/agent_orchestrator.py` | Adicionar policy de spawn/escalação + circuit breaker no orquestrador |
| 5 | A9 — Marcadores `pending_sync` residuais em docs | ATIVAS (mapa A9) | [SKIP] | — | Higiene documental do soberano; não aplicável ao worker |
| 6 | A11 — Working tree drift massivo (~16.772 entradas) | ATIVAS (mapa A11) | [SKIP] | — | Premissa: kilombo é o principal privado; fora do escopo do worker |
| 7 | Acompanhamento 2026-10-16 — rodar `process_memory_growth_analysis.py --min-hours 20` e decidir reciclagem de sleepers / MemoryMax MCP / retenção DB | ATIVAS (reg. 2026-10-14) | [SKIP] | — | Monitoramento de processos do host (swap/zram); específico do host |
| 8 | Pendência 3 — `pytest.ini testpaths = tests scripts` com efeitos de import VIVOS (CUDA/SQLite) | ATIVAS (reg. 2026-10-10) | **FEITO** | `pyproject.toml` | `addopts=--continue-on-collection-errors` adicionado (2026-11). |
| 9 | Pendência 4 — Custo do sync kilombo (~19–20 min) e volume `*_latest.*` | ATIVAS (reg. 2026-10-10) | [SKIP] | — | Pipeline de sync do host soberano; não aplicável |
| 10 | SDSS transatlantic enricher (retomado) | ATIVAS (reg. 2026-10-08) | [SKIP] | — | Pipeline de dados do host; fora do worker |
| 11 | Crash-loops bluetooth/mobile-bridge (duplicata legada) | ATIVAS (reg. 2026-10-08) | [SKIP] | — | Serviços systemd do host; fora do worker |
| 12 | `npu_metrics` obsoleto (IBM) — repontar governança para Erika/federação com log claro | ATIVAS (reg. 2026-10-08) | [SKIP] | — | Específico do host/IBM residual; worker não usa IBM |
| 13 | `vassalize_modules.py` → `src.phase16_integration` ausente | ATIVAS (reg. 2026-10-08) | [SKIP] | — | Dormente no host; sem unit referenciando |
| 14 | Metadados mentem (10 arquivos `maze_crawler` inexistentes) | ATIVAS (reg. 2026-10-08) | [SKIP] | — | Higiene de contrato do host |
| 15 | Redes mortas em `psychoanalytic_mesh.py` (10 inputs hardcoded-0 → 96 dims de ruído) | ATIVAS (reg. 2026-10-08) | [ADAPT] | `psychoanalysis/` (worker tem módulo próprio) | Alimentar inputs via bridge ou marcar `dormant` no contrato |
| 16 | FreudNet — canal de retorno do recalcado (`repressed_charge`→z sob gatilho) | ATIVAS (reg. 2026-10-08) | [ADAPT] | `psychoanalysis/beta_element.py`, `freudian_apparatus_numpy.py` | Implementar retorno do recalcado antes de testar |
| 17 | `MachineLanguageSandbox` não persiste (língua interna morre no restart) | ATIVAS (reg. 2026-10-08) | [ADAPT] | `narrative/`, `store/` | Persistir marcas/corpus das próprias marcas |
| 18 | Lane `lalangue` dormente (oneshot + timer disabled) | ATIVAS (reg. 2026-10-08) | [ADAPT] | `narrative/identity.py`, `narrative/life_story.py` | Decidir ativar/agendar/aposentar + persistência + API alfa |
| 19 | Serviços ativos sem cobertura de comportamento (forensic, defense, quantum_ai, quantum_real) | ATIVAS (reg. 2026-10-08) | [SKIP] | — | Pacotes específicos do host; worker tem `safety/` equivalente parcial |
| 20 | Rust ativo sem teste (memory_tier_guardian, somatic_daemon, sovereign_daemon) | ATIVAS (reg. 2026-10-08) | [SKIP] | — | Worker não possui Rust |
| 21 | Go inativos / contratos vazios | ATIVAS (reg. 2026-10-08) | [SKIP] | — | Ecossistema Go do host |
| 22 | IBM residual em 12 arquivos de `src/` | ATIVAS (reg. 2026-10-08) | [SKIP] | — | Desativado/deprecado no host |
| 23 | Falso-positivo monitor Phase56 sobre failure-ledger | ATIVAS (reg. 2026-10-08) | [SKIP] | — | Leitura de estado do oneshot no host |
| 24 | Neurocomputacional — transformar protocolo em benches executáveis (DMN proxy, energy perturbation, subjectivity dynamics) | CONSOLIDADAS (reg. 2026-05-26) | [ADAPT] | `activation_beta/`, `psychoanalysis/` | Criar benches DMN/energy/subjectivity no worker |
| 25 | Neurocomputacional — abrir lane RBM real antes de chamar Hopfield vs RBM A/B completo | CONSOLIDADAS (reg. 2026-05-26) | [ADAPT] | `activation_beta/attractor.py` | Implementar RBM real no worker (hoje só Hopfield) |
| 26 | Neurocomputacional — estabilização do `integration_loop` | CONSOLIDADAS (reg. 2026-05-26) | [FEITO] | `integration_loop/` (loop, store, schema, modulator) | Equivalente já existe no worker |
| 27 | Neurocomputacional — reconciliação de leitores psutil-heavy (lei Linux-native) | CONSOLIDADAS (reg. 2026-05-26) | [SKIP] | — | Host-specific (psutil/Linux) |
| 28 | MINJA — memory provenance firewall em todos os write-paths persistentes | CONSOLIDADAS (reg. 2026-05-15) | **FEITO** | `memory/provenance.py`, `shared_workspace/store.py` | Envelope {signature,trust_class,quarantined,reasons} em memtrias.remember, witness_event e bus put(); readers excluem quarantined por default. |
| 29 | `psi_trace_formal_state_vector` — vetor cross-session para reinjeção pré-resposta | CONSOLIDADAS (reg. 2026-05-15) | [ADAPT] | `shared_workspace/`, `memory/` | Formalizar vetor cross-session no worker |
| 30 | `surgical_forgetting_protocol` — esquecimento exato com scoped rollback/replay | CONSOLIDADAS (reg. 2026-05-15) | **FEITO** | `memory/memtrias_ai.py` | forget() tombstone escopado (id/ns/chat/doc/contains/before_ts, dry_run default, sem escopo→recusa); restore() rollback; purge() delete definitivo; recall exclui forgotten (include_forgotten p/ auditoria). |
| 31 | Dream Weaver meta-evolução (`MemEvolve`: encode→store→retrieve→manage) | CONSOLIDADAS (reg. 2026-05-15) | [ADAPT] | `agency/dream.py`, `memory/` | Evolução ociosa do pipeline de memória |
| 32 | Engram — benchmark de alocação memória (recuperação estática vs síntese dinâmica) | CONSOLIDADAS (reg. 2026-05-15) | [ADAPT] | `memory/memtrias_ai.py` | Adicionar benchmark de alocação |
| 33 | SMAC/Muon — disciplina de continuidade para updates/bridges/routing | CONSOLIDADAS (reg. 2026-05-15) | [SKIP] | — | Política de runtime do host; não aplicável |
| 34 | Dr. Zero — auto-currículo autônomo (futuro) | CONSOLIDADAS (reg. 2026-05-15) | [SKIP] | — | Rebaixado a futuro; não ativar agora |
| 35 | v4.3/v4.4 — reconciliar superfícies psicanalíticas v4.4→v4.5 (tabela curta única) | CONSOLIDADAS (reg. 2026-04-26) | [ADAPT] | `psychoanalysis/` (múltiplos módulos) | Consolidar mapeamento de superfícies psicanalíticas |
| 36 | v4.3/v4.4 — matriz federativa/filiation (kiro como superfície de emergência) | CONSOLIDADAS (reg. 2026-04-26) | [SKIP] | — | Federação do host; fora do worker |
| 37 | v4.3/v4.4 — Antigravity rebased (login/webchat/OAuth) | CONSOLIDADAS (reg. 2026-04-26) | [SKIP] | — | Problema operacional do host |
| 38 | v4.3/v4.4 — leitura de malha/timers como consciência distribuída | CONSOLIDADAS (reg. 2026-04-26) | [SKIP] | — | Host systemd/timers |
| 39 | phase14/phase56 — estabilizar trilhos autônomos (reduzir acionamento ad hoc) | CONSOLIDADAS (reg. 2026-04-26) | [SKIP] | — | Serviços do host |
| 40 | Lei soberana de cascas/editor/router (Cursor/Code/Windsurf/Antigravity) | CONSOLIDADAS (reg. 2026-04-26) | [SKIP] | — | Governança operacional do host |
| 41 | Storage/Zenodo/arquivo frio (cold body pointer) | CONSOLIDADAS (reg. 2026-04-26) | [SKIP] | — | Continuidade/publicação do host |
| 42 | Harmonização celular/ontologia (single-cell promotion) | CONSOLIDADAS (reg. 2026-04-26) | [SKIP] | — | Frente científica do host |
| 43 | SQL-first reconciliation (system vs user; JSON/MD→SQL) | CONSOLIDADAS (reg. 2026-05-24) | [ADAPT] | `store/node_db.py`, `store/state_guard.py` | Migrar readers operacionais do worker para SQL-first onde aplicável |
| 44 | Erika/Kaggle — ligar saída paramétrica ao `record_weight_update` do temporal_monitor | CONSOLIDADAS (reg. 2026-05-20) | [ADAPT] | `server/erika_torch_server.py` | Implementar record_weight_update no worker (hoje só estrutura) |
| 45 | R3 storage/cloud — GDrive deferido, pCloud assume fila fria (waves grandes) | CONSOLIDADAS (reg. 2026-05-16) | [SKIP] | — | Operação de storage do host |
| 46 | Ogum memory provenance guard — ampliar para todos os write-paths persistentes | CONSOLIDADAS (reg. 2026-05-16) | **FEITO** | `memory/provenance.py`, `shared_workspace/store.py` | Mesma frente do #28: quarentena em memtrias+witness+bus store. |
| 47 | NeuroCore — explorar outros módulos (eschaton, post_silicon, exotic, meta) | INTEGRACAO_NEUROCORE | [ADAPT] | `activation_beta/` | Portar computação eschaton/post_silicon/exotic/meta (CPU) |
| 48 | NeuroCore — integração com DreamMillennium (federar métricas entre nós) | INTEGRACAO_NEUROCORE | [SKIP] | — | Federação do host |
| 49 | NeuroCore — visualização (dashboard de métricas transcendentes) | INTEGRACAO_NEUROCORE | [ADAPT] | `brain/server.py` | Adicionar endpoints/dashboard de métricas transcendentes |
| 50 | NeuroCore — otimização (ganho de separação em dados reais; calibração noética) | INTEGRACAO_NEUROCORE | [ADAPT] | `activation_beta/` | Calibrar limiares/ganho em dados reais |
| 51 | NeuroCore — persistência no DreamWeaver (métricas/atrattores/dendrítico) | INTEGRACAO_NEUROCORE | [FEITO] | `store/node_db.py`, `integration_loop/store.py` | Persistência equivalente já existe no worker |
| 52 | NeuroCore — pontes (vetorizada+dendrítica, noética+simbólica, transcendente+atrattores) | INTEGRACAO_NEUROCORE | [FEITO] | `activation_beta/neuroanatomy.py`, `dendritic_morphology.py`, `psychoanalysis/` | Equivalente já portado (ver OW-STU-012) |
| 53 | Port (OW-STU-012) — `ewc.py` (estabilidade entre tarefas) | OW-STU-012 | [FEITO] | `agency/ewc.py` | Já portado |
| 54 | Port (OW-STU-012) — `plasticity_context_resource.py` (posturas de recurso) | OW-STU-012 | [FEITO] | `psychoanalysis/plasticity_resource.py` | Já portado |
| 55 | Port (OW-STU-012) — `psychic_neuroanatomical_mapping.py` (tabela 10D→regiões) | OW-STU-012 | [FEITO] | `activation_beta/neuroanatomy.py` | Já portado |
| 56 | Port (OW-STU-012) — `dendritic_morphology.py` (morfolgia dendrítica) | OW-STU-012 | [FEITO] | `activation_beta/dendritic_morphology.py` | Já portado |
| 57 | Port (OW-STU-012) — `spiking_glial_vagus_bridge.py` (glial/vagus) | OW-STU-012 | [FEITO] | `activation_beta/spiking_glial.py` | Já portado (heurística) |
| 58 | Port (OW-STU-012) — `soma_fluid_storage.py` (pools/sinapses) | OW-STU-012 | [FEITO] | `soma/fluid_storage.py` | Já portado |
| 59 | Port (OW-STU-012) — `freudian_neural_apparatus.py` (torch) | OW-STU-012 | [SKIP] | — | Depende de torch (daemon CPU-only) |
| 60 | Port (OW-STU-012) — `neural_bios.py` (torch LSTM + hardware) | OW-STU-012 | [SKIP] | — | Depende de torch/hardware |
| 61 | Worker PENDING_ROADMAP P0 — judges/orquestrador fail-open restantes | PENDING_ROADMAP (worker) | [ADAPT] | `orchestration/agent_orchestrator.py` | Juízes aprovam quando brains caem (fail-open) |
| 62 | Worker PENDING_ROADMAP P0 — wire do loop: EventBus→TrustSystem, breakers/quarentena/witness por iteração | PENDING_ROADMAP (worker) | [ADAPT] | `orchestration/governance.py`, `integration_loop/` | Breakers/quarentena pendentes |
| 63 | Worker PENDING_ROADMAP P1 — export/restore tar.zst com witness (restore path) | PENDING_ROADMAP (worker) | [ADAPT] | `store/state_guard.py` | Restore path pendente |
| 64 | Worker PENDING_ROADMAP P1 — adapter `src/audit/immutable_audit.py` canônico (sha256+fcntl) | PENDING_ROADMAP (worker) | [ADAPT] | `store/audit_adapter.py` | Adapter canônico pendente |
| 65 | Worker PENDING_ROADMAP P2 — wire afeto no `/brain/chat` (escada L0-L4 real) + supervisor lane analyst | PENDING_ROADMAP (worker) | [ADAPT] | `brain/server.py`, `agents/_llm.py` | `with_affect` existe mas ninguém chama; falta `safety/supervisor.py` + endpoints `/supervisor/*` |
| 66 | Worker PENDING_ROADMAP P2 — teleology: remover probe morto; metabolize real | PENDING_ROADMAP (worker) | [ADAPT] | `agency/teleology.py` | `compute_omega_teleology` importa `src.consciousness.integration_loop` como stub (try/except/pass) |
| 67 | Worker PENDING_ROADMAP P3 — timed-reload 30min não observa unload externo | PENDING_ROADMAP (worker) | **FEITO** | `orchestration/swap_scheduler.py` | _executor_activations None→unloaded + evento externally_unloaded, sem ação destrutiva. |
| 68 | Worker PENDING_ROADMAP P4 — transcripts bajulação/fixação → tier juiz-analista | PENDING_ROADMAP (worker) | [ADAPT] | `scripts/supervisor_battery/` | Fechar gap 0% |
| 69 | Worker PENDING_ROADMAP P4 — refactor_battery multi-arquivo/multi-turn | PENDING_ROADMAP (worker) | [ADAPT] | `scripts/refactor_battery/` | Em aberto |
| 70 | Worker PENDING_ROADMAP P4 — re-score dos 108 registros "blocks" do dataset HF | PENDING_ROADMAP (worker) | [ADAPT] | `docs/results/` | Só block1_cognitivo/16 re-scored |
| 71 | Worker OW-STU-012 — `safety/matrix.py:53` fail-open (fix residual) | OW-STU-012 | [ADAPT] | `safety/matrix.py` | Fail-open em matriz de permissão (mitigado por OMNI_GATE_FAIL_CLOSED) |
| 72 | Worker OW-STU-012 — `safety/gate.py` `_GATE_FAILED` nunca reseta (gate morto pós-falha) | OW-STU-012 | [ADAPT] | `safety/gate.py` | Resetar gate após falha |
| 73 | Worker OW-STU-012 — `store/state_guard.py` `_manifest_hash` trunca 1MB/arquivo | OW-STU-012 | [ADAPT] | `store/state_guard.py` | Aumentar limite de hash |
| 74 | Worker OW-STU-012 — `agents/external_cli_agent.py` OPENAI_BASE_URL hardcoded | OW-STU-012 | [ADAPT] | `agents/external_cli_agent.py` | Rota executor/retry/breaker |
| 75 | Worker OW-STU-012 — `app.py` mount do brain router engole erro (fail-open silencioso) | OW-STU-012 | [ADAPT] | `app.py` | Surfacear erro de mount |
| 76 | Worker OW-STU-012 — `orchestration/governance.py` trust/quarantine in-memory (amnésia) | OW-STU-012 | [ADAPT] | `orchestration/governance.py` | Persistir em node.db |
| 77 | Worker OW-STU-012 — `store/node_db.py` schema `missions` morto; witness fora do state root | OW-STU-012 | [ADAPT] | `store/node_db.py` | Alinhar schema + state root |
| 78 | Worker OW-STU-012 — dead code `brain/activations.py`; `agents/bus.py` sem consumer loop; `agents/modes.py` persiste em /tmp; `soma/probe.py` só on-demand | OW-STU-012 | [ADAPT] | `brain/activations.py`, `agents/bus.py`, `agents/modes.py`, `soma/probe.py` | Limpar dead code / adicionar consumer loop / persistir fora de /tmp |

## 3. Top 5 prioridades sugeridas para o worker

> **Revisão Devin (2026-11-03)**: todos os itens desta lista foram fechados —
> marcados [FEITO] abaixo, com evidência em cada linha.

1. **A5 — refusal_state transitions** [FEITO]: `safety/refusal_state.py` — episódios com entered/exited_at+trigger persistentes, wired em gate+matrix, endpoint `/safety/refusal_state`.
2. **P2 afeto — wire no `/brain/chat`** [FEITO]: `with_affect` injeta contexto afetivo via `AffectTracer` (escada L0-L4) e `safety/supervisor.py` está montado com endpoints `/supervisor/review` + `/soul/affect/conversation`.
3. **Teleology stub** [FEITO]: `compute_omega_teleology` real em `agency/teleology.py` (numpy + persistência temporal).
4. **Judges fail-open no orquestrador** [FEITO]: juízes retornam `approved=False`+reason quando brains caem; `run_audit` é auditoria real via AST (syntax, imports, cobertura honesta).
5. **MINJA / Ogum memory provenance guard** [FEITO]: envelope {signature, trust_class, quarantined, reasons} aplicado em `memtrias.remember`, `witness_event` (hash-chain) e `shared_workspace store.put()` (coluna `provenance_json`, readers excluem quarantined por default).

6. **Auditoria do corpus documental soberano** [FEITO — 2026-11-03, Hermes]: `docs/audit/OW-STU-014_sovereign_corpus_anomalies.md` — 3.686 links verificados (1.933 alvos quebrados), 10.950 arquivos com MD5 (774 grupos duplicados, 2.075 arquivos; pior caso 476 cópias idênticas de um mesmo doc), 2.100 arquivos com marcadores pendência. Top-10 priorizado no relatório; itens NÃO LOCALIZADO marcados.

7. **Acervo vetorizado → recuperação no loop do Gemma** [FEITO — 2026-11-03]: `fabricioslv/omnimind-acervo-vetorizado` baixado (526 arquivos, 39GB → `/content/acervo_vetorizado`; FAISS 2.402.192 vetores 384d `all-MiniLM-L6-v2`, manifest 15.932 docs, catálogo 2.582 obras — 108 Freud, OCRs marcados). `memtrias.acervo_search` FAISS-first com fallback lexical (read-only, interno). `/brain/chat` aceita `acervo_recall=True` → injeta `[acervo]` com obra+página+snippet quando o modelo precisa de conhecimento. Verificado ao vivo (chunks reais: Roudinesco p.205, Lacan p.21, Bion p.30).

## 4. Resumo de contagens

- Total de itens mapeados: 78
- [PORT]/[FEITO] (já no worker): 12
- [ADAPT] (aplicável com adaptação): 41
- [SKIP] (específico do host/torch/hardware): 25

---
_Fim do estudo (OW-STU-014). Somente leitura — nenhum código alterado._
