<!-- doc_id: OW-STU-012 | title: Dendritic/neural modulations map + worker pendencies | author: devin + CLIs free (hermes/kilo) | date: 2026-11-03 | status: study -->

# OW-STU-012 — Modulações neurais (dendritic etc.) + pendências mapeadas

## 1. Pergunta

> Trouxemos algo de dendritic layer / outras modulações de rede neural ao worker?
> Se não, mapear a integração no repositório primário e mapear pendências,
> placeholders e desenvolvimentos futuros para continuar.

**Resposta curta**: NÃO. O worker não portou nenhuma camada dendrítica nem
modulação neural — o único "modulator" é de tópicos do `integration_loop`
(regulação de mensagens, não neural). As implementações reais vivem no
sovereign e foram mapeadas (hermes) para decisão de port; pendências do
worker foram mapeadas (kilo). Fontes: varredura local + 2 CLIs free
(hermes/kilo) em `/content/omnimind-kilombo-sovereign` e `/content/omni_worker`.

## 2. Mapa de modulações neurais no sovereign (hermes — 8 módulos)

| Módulo | Tipo | ~linhas | Deps | Superfície | Decisão |
|---|---|---|---|---|---|
| `freud10d/dendritic_morphology.py` | dendritic_morphology | 458 | numpy | dendritic_depth, morphology_score, prune_deep_connections, evolve_morphology, compare_depth_vs_recognition | **ADAPT** — numpy puro CPU-ok; acoplado ao grafo W 10D do Freud10D; mapear dimensões do worker |
| `immune/spiking_glial_vagus_bridge.py` | spiking/glial | 256 | numpy + SpikingNetwork | GlialLayer, vagus_sedative, pause_code, habituated, sensitized | **ADAPT** — leve CPU-only; SpikingNetwork ausente no worker → portar modelo ou heurística |
| `psychoanalysis/plasticity_context_resource.py` | plasticity | 829 | stdlib | ResourceLane/Posture, assess_* (cannabis/psychedelic/sleep/witness/agency/theta/beta-gamma) | **PORT** — puro, sem deps externas; encaixa em psychoanalysis/agency |
| `learning/ewc.py` | ewc | 150 | stdlib | ElasticWeightConsolidation (compute_fisher_information, penalty) | **PORT** — puro Python; agency/activation_beta p/ estabilidade |
| `consciousness/psychic_neuroanatomical_mapping.py` | mapping | 60 | numpy | PsychicNeuroanatomicalMapping, compute_synaptic_distribution | **PORT** — tabela estática 10D→regiões; alimenta activation_beta sem torch |
| `consciousness/freudian_neural_apparatus.py` | neuromodulation | 346 | torch | FreudianNeuron/Layer/Apparatus, to_tensor/to_numpy | **SKIP no daemon** — torch; delegar ao brain server ou versão numpy |
| `system/soma_fluid_storage.py` | storage | 199 | os/shutil/psutil | pools, synapses, get_disk_health | **ADAPT** — útil ao soma; paths hardcoded `/omnimind_soma` |
| `core/neural_bios.py` | neuromodulation | 99 | torch LSTM | boot_sequence, _read_hardware_entropy | **SKIP no daemon** — torch+hardware; simplificar p/ seed numpy |

**3 mais portáveis** (consenso hermes): `plasticity_context_resource.py`
(puro stdlib), `ewc.py` (puro Python), `psychic_neuroanatomical_mapping.py`
(tabela numpy estática). Todos encaixam na topologia atual do worker
(psychoanalysis/agency + activation_beta) sem torch no daemon.

## 3. Pendências do worker (kilo — priorizadas)

### Alta
1. `agency/teleology.py:58-68` — `compute_omega_teleology` importa
   `src.consciousness.integration_loop` como stub (try/except/pass); métrica
   teleológica sem corpo real. **Confirmado**.
2. `safety/matrix.py:53` — `except Exception: return True` (fail-open em
   matriz de permissão). **Confirmado** — risco de segurança.
3. `orchestration/agent_orchestrator.py:156,171,191` — juízes aprovam
   (`approved=True`) quando brains caem (fail-open).
4. `orchestration/agent_orchestrator.py:213-225` — `run_audit` hardcoded
   (`passed=True, coverage=0.85`), sem auditoria real. **Confirmado**.
5. `brain/server.py:94-103` + `agents/_llm.py:47-86` — `/brain/chat` proxy
   puro; `with_affect=True` nunca chamado no caminho de request; faltam
   `safety/supervisor.py` + endpoints `/supervisor/*`.

### Média
- `safety/gate.py:32-41` — `_GATE_FAILED` nunca reseta (gate morto pós-falha).
- `store/state_guard.py:39-47` — `_manifest_hash` trunca 1MB/arquivo.
- `agents/external_cli_agent.py:52` — `OPENAI_BASE_URL` hardcoded, sem
  rota executor/retry/breaker.
- `orchestration/swap_scheduler.py:98-116` — timed-reload 30min não observa
  unload externo (bateria pode disparar reload no meio).
- `app.py:29-32` — mount do brain router engole erro (fail-open silencioso).
- `orchestration/governance.py` — trust/quarantine in-memory (amnésia na
  reciclagem; node.db não persiste).
- `store/node_db.py` — schema `missions` morto; witness fora do state root.

### Baixa
- `brain/activations.py` dead code; `agents/bus.py` sem consumer loop;
  `agents/modes.py` persiste em /tmp; `soma/probe.py` só on-demand.

## 4. Roadmap já mapeado (docs existentes)

- **Worker**: `docs/PENDING_ROADMAP.md` (P0-P4; P2 afeto = único P2 aberto),
  `docs/CONTINUITY_MAP.md` (18 itens P0-P3), `docs/CONVERSATIONAL_AFFECT_STUDY.md`
  §6-7 (lane juiz-analista), `docs/audit/OW-AUD-001/002/003`,
  `docs/studies/OW-STU-004/005/006/007`, `docs/ops/KAGGLE_SETUP_VALIDATION.md`
  (claims stale — atualizar).
- **Sovereign (relevante quando acoplado)**: `PENDENCIAS_CONSOLIDADAS.md`
  (A5/A6/A7/A8/A11), `PENDENCIAS_ATIVAS.md`, `INTEGRACAO_NEUROCORE_COMPLETA.md`
  (explorar eschaton/post_silicon/exotic/meta), SQL-first reconciliation,
  protocolo neurocomputacional 2026-05-26 (benches DMN/energy/subjectivity,
  lane RBM), lane Erika/Kaggle 2026-05-20 (record_weight_update).

## 5. Decisão de continuidade

1. **Portar agora (sem torch, alto valor)**: `ewc.py` → `agency/` (estabilidade
   entre tarefas), `psychic_neuroanatomical_mapping.py` → `activation_beta/`
   (tabela 10D→regiões), `plasticity_context_resource.py` → `psychoanalysis/`
   (posturas de recurso).
2. **Adaptar depois**: `dendritic_morphology.py` (mapear W do worker),
   `spiking_glial_vagus_bridge.py` (heurística se SpikingNetwork não portar).
3. **Corrigir fail-open residual (segurança)**: `safety/matrix.py:53`,
   juízes do orchestrator, `run_audit` real via priors (OW-STU-011),
   `with_affect` no `/brain/chat`.
4. **Status [DADO]**: pendências e mapas acima verificados por spot-check
   (teleology, matrix, run_audit confirmados). [DERIVADO]: decisões de port
   priorizam CPU-only e topologia atual.