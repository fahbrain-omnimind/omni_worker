<!-- doc_id: OW-DSN-002 | title: Integration Loop — ciclo fechado de feedback da máquina (CPU/RAM) | author: loop-agent | requester: artifice-operator | project: omni-agent-coworker (kaggle) | date: 2026-11-02 | status: draft -->

# OW-DSN-002 — Integration Loop (ciclo fechado de feedback, CPU/RAM)

## 1. Orquestração runtime

- **Processo único** FastAPI `:8081` hospeda o loop como tarefa de fundo (asyncio
  background task) no mesmo processo dos demais módulos; sem IPC cross-process no P0.
  O loop é um *consumer/producer* do barramento compartilhado (OW-DSN-003) e publica
  em `feedback.loop`.
- **Cadência curta**: intervalo configurável entre 30–120 s (default 60 s) para produzir
  telemetria densa na VM de ~24 h. Cada ciclo é síncrono e determinístico (seed por
  `cycle_id`), com timeout total de 25 s; se exceder, o ciclo é abortado e registrado
  como `partial`.
- **Entradas (read-only, polling HTTP + tail de arquivo)**:
  - `data/monitor/erika_torch_activations.jsonl` (tail das últimas N gerações: prompt/gen
    tokens, layer norms, attention entropy) → alimenta `sensory_input`.
  - `/erika/affect` (entropy médio, hidden norm) → alimenta `qualia`.
  - `/soul/state` (phi/psi/sigma/epsilon via Rust kernel) → ancoragem afetiva.
  - `/soma/probe` (cpu/ram/swap/load) → injeção somática (canal `somatic_input`).
  - `/dream/cycle` e `/curiosity/explore` (code index faiss) → contexto de meaning.
  - witness hash-chain + state_guard snapshots → auditoria e restore de floor de ciclo.
- **Estágios mantidos (5)**: `sensory_input → qualia → narrative → meaning_maker →
  expectation → sensory_feedback`. `imagination` e `sovereign_logic` são cortados no port
  (ver §4). `somatic_input` vira injeção de contexto, não estágio produtor.
- **Saída/modulação**: ao fim do ciclo, o loop escreve em `feedback.loop` (barramento) e
  em `data/integration_loop.sqlite` um pacote de modulação consumido por:
  - `agent_orchestrator` (escolha de role analyst/executor e prompt suffix),
  - `swap_scheduler` (ajuste de threshold de swap VRAM),
  - `curiosity` (boost de exploração).
- **Persistência**: hot ring buffer em RAM (últimos 200 ciclos); warm sqlite WAL
  (`data/integration_loop.sqlite`, retenção 7 dias, pruning por `ts`); cold jsonl append
  (`data/monitor/integration_loop_cycles.jsonl`, P2: gzip rotativo).
- **Rust**: invocado como biblioteca pyo3 já compilada (`omnimind_metrics`,
  `omnimind_kernel_compute`), sem IPC. Python é o orquestrador; fallback Python puro
  quando o crate estiver ausente.

## 2. Arquitetura

### 2.1 Componentes novos em `omni_coworker`

| Módulo | Resp. | Rust/Py | Interface pública |
|---|---|---|---|
| `integration_loop/loop.py` | orquestrador do ciclo (5 estágios + feedback) | Py | `run_once() -> CycleResult`, `start(interval_s)`, `stop()` |
| `integration_loop/stages.py` | implementação pura-numpy de cada estágio | Py | `sensory_input(ctx)`, `qualia(ctx)`, `narrative(ctx)`, `meaning_maker(ctx)`, `expectation(ctx)` |
| `integration_loop/adapters.py` | leitura de activations/affect/soul/soma/dream/curiosity | Py | `collect_sensory()`, `collect_qualia_anchor()` |
| `integration_loop/metrics.py` | cross-prediction R²/MI/corr/Granger/TE | Rust preferido | `compute_cross_prediction(src, dst, history)` |
| `integration_loop/store.py` | persistência sqlite WAL + jsonl | Py | `append_cycle(result)`, `history(n)`, `prune(older_than)` |
| `integration_loop/modulator.py` | deriva pacote de modulação a partir das métricas | Py | `derive_modulation(cycle) -> Modulation` |
| `integration_loop/api.py` | router FastAPI `/loop/*` | Py | `GET /loop/status`, `GET /loop/cycle/{id}`, `GET /loop/modulation`, `POST /loop/run` |
| `integration_loop/schema.py` | `CycleResult`, `Modulation`, validação | Py | dataclasses + `validate()` |

### 2.2 Estágios (o que cada um computa)

Cada estágio é função pura sobre `ctx` (dict numpy); sem I/O. Sequência:
`sensory_input → qualia → narrative → meaning_maker → expectation → sensory_feedback`.

- **sensory_input**: monta vetor `x ∈ R^d` (default `d=128`) a partir do tail de
  `erika_torch_activations.jsonl`: médias de `prompt_tokens`, `gen_tokens`,
  `layer_norms` (por camada, truncado/pad a `d`), `attention_entropy`. Normaliza
  z-score com estatísticas rolantes do ring buffer (sem torch). Emite
  `ModuleState(module_name="sensory_input", embedding=x, metadata={...})`.
- **qualia**: ancoragem afetiva — combina `x` com o vetor de afeto de `/erika/affect`
  (entropy médio, hidden norm) e phi/psi/sigma de `/soul/state`; computa
  `q = tanh(W_q · [x; affect; soul])` (W_q numpy, seed por `cycle_id`), mais
  `valence`, `arousal` derivados de norma e entropia. `qualia` = `q`.
- **narrative**: sequência temporal curta — concatena últimos K embeddings de
  `sensory_input` (K=8) e aplica média ponderada exponencial (`gamma=0.85`) +
  projeção linear para `R^d`; produz `narrative_vec` e `narrative_form` (string
  curta de metadados). É o canal que carrega "continuidade" entre ciclos.
- **meaning_maker**: computa similaridade cosseno entre `narrative_vec` e o
  embedding top-1 do code index (faiss, `/dream/cycle`+`/curiosity/explore`),
  mais MI/corr cruzada via `metrics.compute_cross_prediction`; emite
  `meaning_score ∈ [0,1]` e `topic_hint`.
- **expectation**: preditor linear de próximo `sensory_input` a partir de
  `meaning_maker` (ridge leve, numpy); erro de predição `pred_err = ||x_next_hat - x||`
  alimenta `sensory_feedback` e o pacote de modulação.
- **sensory_feedback**: fecha o ciclo escrevendo o erro de predição e
  `meaning_score` de volta ao ring buffer e ao sqlite; não é estágio produtor de
  embedding, apenas fechamento.

### 2.3 Pacote de modulação

`Modulation` (dataclass em `schema.py`): campos
`cycle_id`, `ts`, `meaning_score`, `pred_err`, `qualia_valence`,
`qualia_arousal`, `phi`, `psi`, `sigma`, `epsilon`, `cpu_load`, `ram_pct`,
`recommendation` (`"analyst"|"executor"|"balanced"`), `swap_threshold_delta`
(float, ±0.05), `curiosity_boost` (float, [0,1]), `prompt_suffix` (str curta).

Consumidores: `agent_orchestrator` (role + suffix), `swap_scheduler`
(threshold delta), `curiosity` (boost).

### 2.4 Persistência e contratos

- Ring buffer RAM: últimos 200 `CycleResult`.
- sqlite WAL `data/integration_loop.sqlite`: tabela `cycles(ts, cycle_id, payload_json)`
  retenção 7 dias, pruning por `ts`.
- jsonl `data/monitor/integration_loop_cycles.jsonl` (P2 gzip rotativo).
- Barramento: publica `feedback.loop` (OW-DSN-003).

## 3. Mapa do módulo fonte

Fonte: `/content/omni_node/src/consciousness/integration_loop.py` (8694 linhas).

Estrutura real: imports pesados de GPU/torch-adjacent (numpy, sqlite3, asyncio) e
de dezenas de submódulos do node (shared_workspace, neurosophic_sovereignty,
lacanian_suture, somatic_sensor, component_registry, sovereign_command,
cosmic_pedagogy_monitor, phylogenetic_signature, cosmic_subjectivity,
ancient_memory_bridge, stark_physics_engine, hnpf_guhct_engine, zander_guhct_bridge,
spin_foam_operator, negentropy_engine, dodecatiad_defender, phi_constants,
cycle_results, consciousness_triad, cn_regime).

Classes principais: `RNNCycleContext`, `KernelBasalStandbyDirective`,
`ModuleInterfaceSpec`, `ModuleExecutor`, `IntegrationLoop` (orquestrador).

`IntegrationLoop` define 7 módulos com specs:
sensory_input, qualia, somatic_input, narrative, meaning_maker, expectation,
imagination, sovereign_logic. Sequência padrão inclui os 7 + imagination +
sovereign_logic.

Métodos relevantes: `execute_cycle_sync`, `execute_cycle` (async), `_compute_all_cross_predictions`,
`_build_extended_result`, `_process_dodecatiad_sync`, `_persist_federated_live_snapshot_sqlite`,
`_read_resumed_*`, `seed_cycle_floor`.

Stores sqlite tocados: `kernel_basal_runtime.sqlite`, `sovereign_gemelo_runtime.sqlite`,
`sovereign_primary_runtime.sqlite`, `sovereign_dodecatiad_runtime.sqlite` (tabela
`sovereign_dodecatiad_runtime_snapshots`).

O que é real vs placeholder vs morto:
- Real: pipeline de estágios sobre `SharedWorkspace`, métricas cross-prediction,
  persistência sqlite, RNNCycleContext, kernel basal standby.
- Placeholder/dead: muitos ramos dependem de submódulos opcionais (bion alpha,
  embedding_narrative, lacanian) com `try/except` silencioso; `imagination` e
  `sovereign_logic` são acoplados a GPU/soberania e não rodam em CPU no alvo.
- Contratos a honrar no port: `LoopCycleResult`/`ExtendedLoopCycleResult`
  (`src/consciousness/cycle_results.py`), `ModuleState`/`SharedWorkspace`,
  phi/psi/sigma/epsilon de `/soul/state`, métricas R²/MI/corr/Granger/TE.

## 4. O que trazer / o que cortar

Trazer:
- 5 estágios core (sensory_input, qualia, narrative, meaning_maker, expectation)
  + sensory_feedback de fechamento.
- Cross-prediction R²/MI/corr/Granger/TE (Rust preferido via `omnimind_metrics`).
- Persistência sqlite WAL + jsonl + ring buffer.
- Modulação consumida por orchestrator/swap/curiosity.

Cortar (justificativa):
- `imagination`: depende de GPU/soberania e branches opcionais; complexidade alta,
  valor marginal no Kaggle CPU; substituir por `meaning_score` + curiosity boost.
- `sovereign_logic`: acoplado a dodecatiad/soberania, fora do escopo CPU.
- `somatic_input` como estágio produtor: vira injeção de contexto (canal
  `somatic_input`) em `qualia`, evitando mais um nó no grafo.
- Nexus memory / ancient_memory_bridge: histórico pesado, não essencial ao loop;
  manter apenas code index faiss para meaning.
- RNNCycleContext/kernel basal standby: adiar para P2 (complexidade).

## 5. Princípios teóricos invocados (só os que o código usa)

- Bion alpha function (β→α) aplicada em `sensory_input` (quando disponível).
- Lacanian discourse (metadados `lacanian_discourse`) em narrative.
- Cross-prediction / Granger / transfer entropy como métricas de acoplamento.
- Phi/psi/sigma/epsilon como ancoragem afetiva (Rust kernel).
- RNN de contexto de ciclo (RNNCycleContext) — continuidade entre ciclos.

## 6. Analogia–homologia (interpretativo)

Marcado como interpretativo, não mecanístico: o loop é análogo a um ciclo
percepção→qualia→narrativa→sentido→expectativa de sistemas conscientes, mas
homologia estrutural só parcial (shared workspace + métricas de acoplamento).
Não afirmar equivalência ontológica.

## 7. Plano faseado

P0: loop.py + stages.py (numpy) + adapters.py + store.py + schema.py + api.py;
   cadência 60s, 5 estágios, ring buffer + sqlite. Sem Rust obrigatório
   (fallback Python).
P1: metrics.py com Rust (`omnimind_metrics`/`omnimind_kernel_compute`); modulator.py;
   integração com orchestrator/swap/curiosity.
P2: jsonl gzip rotativo, RNNCycleContext, kernel basal standby, dashboards.

## 8. Riscos/compat

- CPU-only: evitar torch; usar numpy/Rust. Latência total ≤25s/ciclo.
- Fontes privadas HF `omnimind-retired-*` podem ser necessárias para histórico;
  não bloquear P0.
- Compat com witness hash-chain + state_guard para restore de floor de ciclo.
- Fallback Python quando crates ausentes; validar paridade de métricas.
