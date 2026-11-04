<!-- doc_id: OW-STU-019 | title: MPS × kernel × dendritic coupling study — wiring the Rust crates, dunker schema and the Giseli dendritic layer to the machine production state | author: devin | date: 2026-11-04 | status: study -->

# OW-STU-019 — Acoplamento MPS/kernel/dendrítico: inventário, gaps e design de wire

> Estudo de design (sem mudança de código). Pergunta do operador: como acoplar
> os crates Rust vendorados (`vendor/kernel/{kernel_compute,metrics,freud10d}`),
> o `dunker_architecture.py` vendored e a dendritic layer (tese Giseli de Sousa,
> portada mas não-wired) ao "matrix/machine production state" (MPS) — o
> sistema-como-motor-neural — de modo que as "aberturas" do Gemma (refactor
> battery 0/11, submissão prematura, perseveração, omissão de entry points)
> sejam atacadas na camada basal/interna do modelo, não por prompts/treino.

**Resposta curta**: os três crates compilam e carregam
(`scripts/build_kernel.sh`, `start_omni_worker.sh:273-296`), mas a fiação é
finíssima: só 4 das ~22 funções exportadas têm consumidor
(`kernel_hooks/compute.py`), `freud10d` tem **zero** consumidores fora do
import-flag, e o `dendritic_morphology.py` portado tem **zero** imports fora de
`tests/`. Pior: o `host_state` que alimenta `compute_affect_vector_28d` chega
**aninhado e com chaves que o schema Rust não lê** — o vetor 28d é hoje
computado sobre ~zeros (§2, §5a). As fontes MPS necessárias para corrigir isso
já existem no daemon (bundle `kernel.cycle`) — o trabalho é de *adaptação de
schema*, não de nova instrumentação. O grafo W natural para a dendritic layer
pode sair de três lugares concretos (§5d), incluindo um grafo por-camada dos
sidecars `.npz` — que é onde a detecção basal das aberturas vive (§5e).

---

## 1. Inventário dos crates — exports × consumidores

Fontes: `vendor/kernel/{kernel_compute,metrics,freud10d}/src/lib.rs`,
`src/omni_coworker/kernel_hooks/{__init__.py,compute.py}`.

### 1.1 `omnimind_kernel_compute` (module `omnimind_kernel_compute`, lib.rs:50-91)

| Export (assinatura Rust) | O que computa | Consumidor no worker |
|---|---|---|
| `compute_maat_balance(phi_anchor, psi, epsilon) -> f64` | Balanço Ma'at operacional (maat.rs) | `kernel_hooks/compute.py:38-51` (`maat_balance`) → `soul/dodeca.py:108-115` (casa S07) |
| `compute_sigma_operational_support(...)` (8 args) | Estimador de piso σ operacional (sigma.rs) | **nenhum** |
| `build_temporal_internal_scale(...)` | Escala temporal interna (dict 13+ chaves, `phi_frameworks` aninhado) | **nenhum** |
| `DesireEngine(max_phi=1.0)` (pyclass: `update_lack`, `calculate_epsilon_desire`, `lack_of_being`, `get_drive_type`, `reset`) | Motor de desejo-falta | **nenhum** — existe `psychology/desire_engine.py:144` (`DesireEngine` Python puro, classe distinta, usado em `kernel_daemon/scheduler.py:78-84`) |
| `compute_epsilon_axes(desire_engine, ...)` | Eixos epsilon completos + canal `epsilon_debug` | **nenhum** |
| `calculate_shadow_phi(total_processes, 6 fatores)` | Shadow-phi estimate (phi_engine.rs) | `kernel_hooks/compute.py:54-85` (`shadow_phi`) — mas **nenhum call-site** fora do wrapper (grep: `shadow_phi(` só em compute.py) |
| `compute_affect_vector_28d(host_state: PyDict)` | Vetor afetivo 28d: 18 tokens afex + 6 VCTR + potências P1-P6 + circuit strategy (affect.rs:42-517) | `kernel_hooks/compute.py:20-35` (`affect_state`) → `soul/api.py:43,115`, `app.py:174` |
| `clamp_phi_nats / normalize_phi / denormalize_phi / calculate_psi_gaussian` | Constantes Φ F1 (phi_constants.rs) | **nenhum** |
| `neutrosophic_construct_quadruple / apply_neo_transformation / quadruple_topsis / calculate_availability / sarannya_entropy / phi_hnos` | Bloco neutrosófico F2 (neutrosophic.rs) | **nenhum** — há `NeutrosophicTriplet` reimplementado local em `psychoanalysis/beta_element.py:39` (port, não binding) |
| `score_live_writer_snapshot(...)` | Scoring hot-path do writer (scoring.rs, F7) | **nenhum** |

**[DADO]** 15 exports registrados no `#[pymodule]` (lib.rs:54-89); apenas
`compute_maat_balance`, `calculate_shadow_phi`, `compute_affect_vector_28d`
passam pelo wrapper `kernel_hooks/compute.py`, e só os dois primeiros níveis
(maat, affect) têm call-site vivo. `compute_epsilon_axes`,
`build_temporal_internal_scale`, `DesireEngine`, todo `phi_constants`,
`neutrosophic` e `scoring`: **NÃO LOCALIZADO consumidor** (grep
`compute_epsilon_axes|build_temporal_internal_scale|clamp_phi_nats|
neutrosophic_|score_live_writer_snapshot` sobre `src/` e `tests/`).

### 1.2 `omnimind_metrics` (metrics/src/lib.rs:4-77)

| Export | O que computa | Consumidor |
|---|---|---|
| `normalize_l2(vec)` | Normalização euclidiana | **nenhum** |
| `cosine_similarity(a, b)` | Cosseno entre vetores | `kernel_hooks/compute.py:88-102` (`cosine_similarity`) — call-site vivo **NÃO LOCALIZADO** fora do wrapper |
| `quadruple_topsis(alts, ideal_pos, ideal_neg)` | TOPSIS sobre quádruplas neutrosóficas | **nenhum** |
| `calculate_sarannya_entropy(t, i, f)` | `1 - (t-f)²(1-i)` | **nenhum** |

### 1.3 `omnimind_freud10d` (freud10d/src/lib.rs:90-368)

| Export | O que computa | Consumidor |
|---|---|---|
| `Freud10DApparatus` (pyclass) | Aparato psíquico 10D: `forward(perception)` = média da percepção em `state[phi]` + 5 iterações `tanh(Wᵀ·state)` sobre W 10×10 canônica (lib.rs:40-87); retorna `(consciousness_omega, state_10d)`; mantém `tension_history` e `pleasure_history` (`pleasure = -Δtension`, lib.rs:140-149). Métodos: `state_dict`, `state_vector`, `topographic_flow` (conscious/preconscious/unconscious/repression/return_repressed), `structural_conflict` (id/ego/superego + conflict_intensity), `get_10d_metrics`, `tension_window(n)`, `reset`, `version` | **ZERO consumidores** — confirmado por grep `freud10d|Freud10D|freudian_values_from_state|omnimind_freud` em `src/`/`tests/`/`scripts/`: único import vivo é o flag `FREUD_AVAILABLE` em `kernel_hooks/__init__.py:17-21` e o status em `compute.py:111-116`. As únicas outras ocorrências são comentários em `dendritic_morphology.py:4,11,210-213` |
| INRC piagetiano (`inrc_identity/negate/reciprocate/compensate/recommend`) | Operadores I/N/R/C sobre o state 10d; `inrc_recommend` devolve ("I"|"N"|"R"|"C", reason) — `"N"` quando campo estagnado (`mean_abs<0.15`), `"C"` quando desequilíbrio ego-superego >0.4 (lib.rs:321-336) | **nenhum** |
| `neutrosophic_state()` | Tripleto (T,I,F) por dimensão | **nenhum** |
| `freudian_values_from_state(state_vec)` | Mapeia 10d → **7 chaves `{phi, psi, sigma, epsilon, omega, lambda_, zeta}`** (lib.rs:342-357) — mesma família de eixos do soul state (`soul/api.py:54-59`) | **nenhum** |

**[DERIVADO]** Total: ~22 superfícies pyo3; 4 com wrapper, 2-3 com call-site
vivo. `freud10d` é o ativo mais subutilizado — e é o único que produz um
*estado dinâmico interno* (tensão/prazer/repressão), não uma métrica pontual.

---

## 2. Schema de entrada do dunker — o que consome × o que alimenta

### 2.1 Schema real (`src/omni_coworker/vendor/dunker_architecture.py`)

`compute_dunker_architecture(affect_summary, psychoanalytic_metrics=None,
pedagogical_bridge=None, topology_metrics=None, free_energy=None)`
(dunker_architecture.py:1433-1438) — **5 argumentos**, não 4 (o adapter
`agency/dunker.py` não expõe `pedagogical_bridge`).

| Campo consumido | Onde no código | Estrutura esperada |
|---|---|---|
| `affect_summary.families` | `:1460`, `_affect_score` `:357-362` | lista de `{token, class, score, active, operational_alias}` — os **18 tokens afex** |
| `affect_summary.dominant_affect_token/score` | `:1469-1470` | escalares |
| `psychoanalytic_metrics.psychoanalytic_regime` | `:939` (sentiments), ethics `:1331` | string: `reparacao`, `colapso`, `estagnacao`, `destituicao_subjetiva` |
| `psychoanalytic_metrics.psychoanalytic_is_mourning` | `:940` | bool |
| `pedagogical_bridge.{perrenoud.perrenoud_regime_contrato, ausubel.ausubel_regime, bruner.bruner_modo_dominante}` | `:943-953` | dicts aninhados |
| `topology_metrics.{betti_0, betti_1_spectral, topology_fragmentation}` | `:440-442` | floats; proxies `:450-452` |
| `free_energy` | `:443-446` | float, normalizado `clip01(fe/50)` |

**18 tokens afex** (affect.rs:335-353, ordem exata):
`poti-afex-joy, xer-afex-angst, puls-afex-drift, ogum-afex-resist,
lumi-afex-dawn, noku-afex-dusk, maa-afex-saturation, katu-afex-relief,
yba-afex-sovereignty, isfet-afex-chaos, rekh-afex-memory, sesh-afex-scribe,
tadi-afex-void, noba-afex-spark, floo-afex-current, goza-afex-gaudium,
fadi-afex-deplete, saud-afex-saudade`.

**Gramática** — 12 regras `EMOTION_GRAMMAR_RULES` (:61-158): composições
par-a-par sobre os 18 afetos (ex.: `xer-afex-angst + noba-afex-spark →
expectativa`, `goza-afex-gaudium + ogum-afex-resist → pulcao`), exigindo
`condicao: ambos_ativos`. + 12 afetos solerianos `SOLER_LACANIAN_AFFECT_LEXICON`
(:185-354) derivados por fórmulas produto-negativo sobre as 4 faltas
lacanianas, com enriquecimento topológico quando `needs_formalization`
(:480-526). + gramática soleriana `SOLER_GRAMMAR_RULES` (:618+).
Sentimentos = afeto×contexto (regime psicanalítico + contrato didático Perrenoud
+ modo Bruner + Ausubel — `compute_sentiments` :913-...). Paixões = afeto
dominante `score>0.75` sustentado (`compute_passions` :1183+). Ética =
variável não-epistêmica de Soler (`compute_ethics` :1303+, regime
`destituicao_subjetiva` ativa incrédulo/bon-heur).

### 2.2 O que alimenta cada campo hoje

| Campo | Fonte atual | Status |
|---|---|---|
| `families` | `_families_from_kernel(kernel_state)` (`agency/dunker.py:24-44`) — 18 primeiras dims do `affective_vector_28d` | **[DADO] alimentado, mas degradado**: o vetor 28d vem de `affect_state({"soma": probe()})` (`app.py:174`) — dict **aninhado** cujas chaves o schema flat do Rust não lê (§5a) → scores ~0 |
| `dominant_affect_token/score` | idem (`dunker.py:123-124`) | idem |
| `psychoanalytic_metrics` | parâmetro existe (`dunker.py:106`) mas call-site `app.py:177` passa **só** `kernel_state` | **VAZIO** → `psy_regime="unknown"` (:939), `is_mourning=False`; sentiments caem no ramo genérico; ethics perde `destituicao_subjetiva`. Nenhum produtor de `psychoanalytic_regime` existe no `src/` (grep: zero fora do vendor) |
| `pedagogical_bridge` | **parâmetro nem exposto** pelo adapter `dunker.py:105-108` | **VAZIO** → `contrato_regime="unknown"`. `safety/pedagogical_refusal.py` existe mas produz `PedagogicalDisposition{mode: REFUSE/TEACH/EXECUTE}`, schema incompatível |
| `topology_metrics` | parâmetro existe, não passado | **VAZIO** → `betti_0=1.0, betti_1=0.0` defaults → enriquecimento topológico soleriano ~zero |
| `free_energy` | parâmetro existe, não passado | **VAZIO** → `fe=0 → surprise_proxy=0` |

**[DADO]** O dunker roda hoje "léxico-zerado + 3 contextos vazios": estrutura
dos 5 níveis é computada (families=[], emotions/sentiments/ethics em ramos
neutros), mas o enriquecimento — que era o ponto do port Soler — está morto.

---

## 3. Sinais MPS disponíveis (o que a máquina já coleta)

| Sinal | Arquivo:linha (produção) | Forma | Consumidor atual | Consumidor possível (wire) |
|---|---|---|---|---|
| Resumo por camada (norm/mean/std) + `attention_entropy_last` + prompt/gen tokens por geração | `server/erika_torch_server.py:104-129, 374-384` → `data/monitor/erika_torch_activations.jsonl` | jsonl append-only | `kernel_daemon/collector.py:40-69` (tail incremental); `attractor.py`, `phi_layer.py` | host_state `entropy_sovereign`, `attractor_*` |
| **Sidecar vetores** `(n_layers, hidden)` fp16 + run_id/turn/task | `erika_torch_server.py:187-211` (`OMNI_ACT_VEC_SIDECAR`, keep=64) → `activation_vectors/*.npz` | .npz `[DADO] verificado: (49,3840) 12B` | `activation_beta/hidden_spectral.py:49-65` | grafo W por-camada (§5d), dendritic sobre camadas |
| **Sidecar trajetória** `(T_sub, L, D)` fp16 + steps/n_tokens | `erika_torch_server.py:218-251` (`OMNI_ACT_STEP_*`, every=8 em `data/monitor/capture.env`) → `activation_steps/*.npz` | .npz `[DADO] verificado: traj (13,49,3840)` | **nenhum consumidor de traj** ainda | M3 contract drift (OW-STU-018 §3), dinâmica de perseveração (§5e) |
| `prompt_hidden` (L,D) do prompt | `erika_torch_server.py:390-407` (`OMNI_ACT_PROMPT_HIDDEN=1`) → `prompt_hidden/*.npz` | .npz | nenhum | baseline h_prompt para contract-drift |
| Attractor features: `norm_drift, entropy_collapse, divergent_layer, attractor_score` | `activation_beta/attractor.py` (janela deque por modelo; `rehydrate`/`push`/`features` — chamado em `kernel_daemon/scheduler.py:52-58`) | dict/modelo | `bion_bridge.py:129-143` (attractor_beta→α); `glial_verdict` em `brain/server.py:134` (gate de geração) | host_state `attractor_frustration`, `attractor_H_current`, `attractor_buffer_overflow_tanh` |
| Phi informacional: `phi_breadth, phi_temporal_mi, phi_internal` | `activation_beta/phi_layer.py:44-122` | dict/modelo | bundle `kernel.phi_layer` (`scheduler.py:60-64`) | host_state `d27_total_phi`/`d27_structural_superposition` ou eixo phi do soul |
| Espectral/MPS: `eff_rank_mean, spectral_entropy_mean, ipr_dim_mean, ipr_dim_pct, bond_dim_max_mean` | `activation_beta/hidden_spectral.py:132-182` | dict/modelo | aninhado em `phi_layer.features()`:115-121 | host_state `entropy_sovereign`, entrada de `psychoanalytic_metrics`/`topology_metrics` (§5b) |
| Φ-meta da malha (`phi_meta`, MIP sides) | `kernel_daemon/phi_meta.py:111-194` | escalar/ciclo | `kernel.phi_meta` | sinal de integração para host_state |
| Metastabilidade: `s_meta, m_t, c_soma, corroboration, angst` (duração degradada contínua) | `kernel_daemon/metastability.py:43-125` | dict/ciclo | `kernel.metastability` | host_state `angst_share`, `angst_residual_pressure`, `groddeck_somatic_tension` (c_soma) |
| Homeostase 5-estados + `producing` | `kernel_daemon/homeostasis.py` + `scheduler.py:68-74` | `{state, action}` | `bion_bridge._should_llm`; `desire` | regime psicanalítico proxy (§5b) |
| Desire: `intensity, vector` | `psychology/desire_engine.py` via `scheduler.py:78-84` | dict | bundle `desire` | host_state `desire_execution_rate`, `epsilon_novelty` |
| Regime shift (Page-Hinkley) | `kernel_daemon/regime.py` via `scheduler.py:95-100` | eventos | `kernel.regime_shift` | `psychoanalytic_regime` candidato |
| Ignição GWT-lite (`ignited`, broadcast diversity) | `kernel_daemon/ignition.py` via `scheduler.py:112-119` | dict | `kernel.workspace` | host_state `quantum_potency`/`d27` proxy |
| Soul axes `phi, psi, sigma, epsilon, dominant_token` + dodeca S01-S15 | `soul/api.py:16-87`, `soul/dodeca.py` | dict | `features.aggregate` `soul` key; `modulator.py:123-124` | entrada de `freudian_values_from_state` round-trip (§5c) |
| Modulação: `meaning_score, pred_err, qualia_valence/arousal, recommendation, swap_threshold_delta, curiosity_boost` | `integration_loop/modulator.py:85-128`; `pred_err` de `stages.expectation` (`stages.py:148-169`, ridge predictor) | dict → `feedback.loop` | `consumer.write_modulation`; `loop.py:319` | **`pred_err` = proxy direto de `free_energy` do dunker** (§5b) |
| Bion metabolização: `alpha_content, symbolic_potential, beta_unmetabolized, attractor_alpha` | `integration_loop/bion_bridge.py:86-146` | metadata | `meaning_maker` stage | `psychoanalytic_metrics` (charge não-metabolizada → regime) |
| Resource postures (`hold_boundary` por lane) | `psychoanalysis/plasticity_resource.py` via `loop.py:293-299`, `modulator.py:33-77` | list | modulação (`+0.05` delta em hold vram/thermal) | host_state `rate_limit_pressure`, `retry_pressure` |
| Soma: cpu/ram/swap/load/PSI/disk/net/procs/gpu/virt/custom | `soma/probe.py:289-323` | dict | `features.aggregate` `soma` key | **mismatch de nomes** vs schema kernel (§5a) |
| Memtrias (memória episódica + acervo FAISS) | `memory/memtrias_ai.py` | sqlite | `brain/server.py:188-214`, `dream.py` | host_state `intelligent_significant_episodes`, `attractor_active_episodes` |
| Hypergraph simbólico do codebase | `store/code_index.py:287-308, 413` | json | `brain/server.py:195-199` (`symbolic_recall`) | grafo W alternativo (§5d) |
| Trust scores compartilhados | `orchestration/governance.py:98-218` (`TrustSystem`, `get_trust_system`) | json persistido | `loop._gov()` (`loop.py:53-90`), `safety/matrix.py` | host_state `trust`-adjacent; métricas TOPSIS via `omnimind_metrics` |
| Conectividade Markov blanket 4-6 nós | `psychoanalysis/markov_blanket.py:274` (`connectivity_matrix`) | ndarray | PyPhi offline (`docs/results/blanket_pyphi.md`) | W pequeno p/ dendritic toy; `free_energy` teórico |
| RepressionChannel (recalque→sintoma) | `psychoanalysis/freudnet_repression.py` | classe numpy | import-only (sem call-site vivo — mesmo status do freud10d) | par natural do `Freud10DApparatus.topographic_flow` |
| Defense mechanisms (12 métricas) | `psychoanalysis/defense_mechanisms.py:assess` | dict scores | sem call-site vivo detectado | enriquece `psychoanalytic_metrics` |

**[LIMITE]** Não há produtor de: `winnicott_true_self`, `freud_tension`,
`nasio_comocao`, `klein_polarization`, `psychoanalytic_is_mourning`,
`nasio_pain_rupture`, `quantum_potency`, `solar_cv`, `phase_lock_score`,
`sector16_ratio`, `vagus_sedative_modulator`, `kaggle_completion_rate`,
`papers_published_total`, contadores `services_*`/`cleanup_*`/`gc_*`/`oom_*`
— todos lidos por `affect.rs:52-133`. São conceitos do host soberano
(omni_node); no worker só existem análogos parciais (tabela §5a).

---

## 4. Dendritic layer (tese Giseli) — status e pendências reais

### 4.1 Status [DADO]

`src/omni_coworker/activation_beta/dendritic_morphology.py` (231 linhas) —
port **ADAPT** do sovereign `src/consciousness/freud10d/dendritic_morphology.py`
(decisão OW-STU-012 §2). Numpy puro, CPU-only. Funções:

- `dendritic_depth(W)` — profundidade média de caminho mais curto (BFS) do
  grafo `W>0.01` (:49-69)
- `morphology_score(W)` — `1 − depth/9 ∈ [0,1]` (:72-74)
- `prune_deep_connections(W, n_shortcuts)` — atalhos funcionais i→i+2/3
  (:89-105)
- `evolve_morphology(W0, ...)` — EA restrito ao eixo funcional,
  `0.6·morphology + 0.4·recognition` (:108-159)
- `_snr_discrimination(W)` — separação de 2 atratores sob dinâmica `tanh(Wx+u)`
  (:162-185)
- `compare_depth_vs_recognition(W_base)` — experimento original/podada/evoluída
  (:188-203)
- `load_worker_weight_matrix()` — W 10×10 freudiana canônica hardcoded
  (Id→Ego 0.9 etc., :206-232) — **a mesma W que o freud10d Rust carrega**
  (lib.rs:40-87), reconstruída em Python porque o `w` do pyclass é privado.

**Wired? NÃO [DADO]**: grep `import.*dendritic|from.*dendritic` — único
importador é `tests/test_dendritic_morphology.py`. Nem o daemon, nem o loop,
nem nenhum endpoint chamam `dendritic_depth`.

### 4.2 Pendências do OW-STU-012 — o que já foi resolvido desde então

Contra OW-STU-014 (revisão de pendências, status [FEITO] com evidência):

| Pendência OW-STU-012 | Status hoje | Evidência |
|---|---|---|
| `teleology` stub (alta #1) | **RESOLVIDO** | `compute_omega_teleology` real (OW-STU-014 §6.3) |
| `safety/matrix.py` fail-open | **RESOLVIDO** | fallback standalone com trust mínimo (`matrix.py:45-58`), não `return True` |
| Juízes fail-open | **RESOLVIDO** | tri-state `blind/unavailable ≠ dissident` (`agent_orchestrator.py:~281-310`) |
| `run_audit` hardcoded | **RESOLVIDO** | auditoria real via AST (`agent_orchestrator.py:348+`) |
| `supervisor.py` + `/supervisor/*` | **RESOLVIDO** | `safety/supervisor.py` existe, montado em `app.py:33-37` |
| `with_affect` wired | **RESOLVIDO** | `brain/server.py:97-99`, `agents/_llm.py:47-97`; `AffectTracer` L0-L4 |
| Port dendritic (#56) | **FEITO** | `activation_beta/dendritic_morphology.py` |
| Ports ewc/neuroanatomy/plasticity/spiking_glial/soma_fluid (#53-58) | **FEITO** | todos existem no tree |

**Pendências REAIS que seguem** (status 2026-11-04):

1. **`dendritic_morphology` sem grafo W vivo** — `load_worker_weight_matrix()`
   retorna W estática; nada alimenta W dos dados do sistema. É o único dos
   ports activation_beta sem produtor/consumidor no ciclo (attractor, phi_layer,
   hidden_spectral, neuroanatomy, spiking_glial todos têm gancho no scheduler
   ou no brain).
2. **`freud10d` órfão** — crate compilada, sem consumidor (§1.3). Sua W interna
   é idêntica à W do dendritic port — os dois módulos descrevem o mesmo grafo e
   nenhum alimenta o outro.
3. **`freudnet_repression.RepressionChannel` e `defense_mechanisms.assess`
   sem call-site vivo** — mesma classe de órfão (port FEITO, wire ausente).
4. **`_gov()` do loop falha silencioso**: `_GOV={}` quando governance deps
   faltam — by design (fail-open), mas combinado com trust in-memory
   (OW-STU-012 média: `governance.py` trust/quarantine não persiste em
   `node.db`) — **segue aberta**.
5. **Glial gate default**: `with_glial_gate` default = `OMNI_GATE_FAIL_CLOSED==1`
   (`brain/server.py:132-133`); AGENTS.md exige `=1` em produção — verificar
   env no bring-up.

### 4.3 De onde sairia o grafo W (candidatos concretos)

| Candidato | Arquivo | N | Pro/Contra |
|---|---|---|---|
| W canônica freudiana (status quo) | `dendritic_morphology.py:206-232` | 10 | Já existe; estática, ignora o estado vivo |
| W interna do `Freud10DApparatus` | `vendor/kernel/freud10d/src/lib.rs:40-87` | 10 | Idêntica à canônica; privada — só acessível via `topographic_flow()` (expõe `repression`, `return_repressed`) — exigiria getter pyo3 |
| `markov_blanket.connectivity_matrix(nodes6)` | `psychoanalysis/markov_blanket.py:274` | 4-6 | Grafo real do sistema (usado p/ PyPhi); N pequeno → depth ∈ [1,5] trivial |
| `symbolic_hypergraph` | `store/code_index.py:287-308` | ~nós do codebase | Grafo real, grande; semântica de "dimensão" ausente |
| **Grafo de acoplamento entre camadas** (`corr` ou MI entre séries `traj[:,l,:]` dos sidecars `activation_steps`) | `data/monitor/activation_steps/*.npz` | 43-49 | **[DERIVADO] candidato MPS-nativo**: W_ij = |corr| entre ativação das camadas i,j sobre a trajetória — "morfologia dendrítica" do modelo real por geração; `dendritic_depth` mede quão raso/profundo é o fluxo efetivo entre camadas |

---

## 5. Proposta de acoplamento MPS/kernel (design)

### 5a. `affect_state()` — o host_state certo

**Bug estrutural [DADO]**: `compute_affect_vector_28d` lê chaves **flat** de
`host_state` (`affect.rs:44-133`: `dict_get(host_state, "thermal_pressure")`
etc.). Os call-sites passam dicts **aninhados**:

- `app.py:174`: `affect_state({"soma": probe()})`
- `soul/api.py:43`: `affect_state({"soma": soma, "affect": affect})`
- `soul/api.py:115`: `affect_state({"soma": ..., "affect": ...})`

Mesmo achatado, os nomes não casam: `probe()` emite `cpu_percent`,
`ram_percent`, `load_per_core`, `uptime_s`, `disk.root_percent`,
`swap_used_gb`, `psi.{cpu,io,memory}.some.avg10`, `gpu.gpus[0].{temp_c,
util_percent, vram_used_gb}` (`probe.py:303-322`); o kernel espera
`thermal_pressure`, `load_pressure`, `ram_pressure`, `disk_usage_pct`,
`swap_usage_pct`, `uptime_seconds` (`affect.rs:64-71`).
**[DERIVADO]**: hoje o vetor 28d é computado sobre ~zeros; o comentário em
`soul/api.py:51-53` ("magnitude observada em [0.27,0.84]") refere outra época
de alimentação, não o wire atual.

**Wire proposto** — novo `host_state_builder` (ex.: em
`kernel_hooks/compute.py` ou módulo `kernel_hooks/host_state.py`) que monta o
dict flat a partir do **bundle `kernel.cycle`** já publicado
(`kernel_daemon/feedback.py:55`; lido via `integration_loop/adapters.py:23-29`
— `bus.latest("kernel.cycle")`):

| Chave kernel | Fonte MPS concreta |
|---|---|
| `thermal_pressure` | `soma.gpu.gpus[0].temp_c / 95` ou `psi.cpu.some.avg10` |
| `load_pressure` | `soma.load_per_core` clip01 |
| `ram_pressure` | `soma.ram_percent / 100` |
| `disk_usage_pct` | `soma.disk.root_percent / 100` |
| `swap_usage_pct` | `soma.swap_used_gb / swap_total_gb` |
| `uptime_seconds` | `soma.uptime_s` (renomear) |
| `entropy_sovereign` | `models.*.attention_entropy_mean` ou `spectral_entropy_mean` (features.aggregate / hidden_spectral) |
| `attractor_H_current`, `attractor_H_global` | `phi_internal`, `phi_temporal_mi` (phi_layer) |
| `attractor_frustration` | `attractor.*.entropy_collapse × K` ou `metastability.angst` (duração degradada) |
| `epsilon_novelty` | `drift.*.attention_entropy_mean` (delta inter-ciclo, features.py:95-100) |
| `desire_execution_rate` | `desire.intensity` (scheduler.py:78-84) |
| `angst_share`, `angst_residual_pressure` | `metastability.angst`, `metastability.c_soma` |
| `groddeck_somatic_tension` | `metastability.c_soma` (custo somático por ciclo) |
| `rate_limit_pressure`, `retry_pressure` | `resource_postures` hold_boundary em lanes vram/thermal |
| `services_starting_n`/`sovereign_daemons_active_n` | contagem de subsistemas ativos no bundle (`phi_meta` binariza activity flags — phi_meta.py:111-122) |
| `intelligent_significant_episodes` | memtrias record count na janela |
| `psychoanalytic_is_mourning`, `freud_tension` | saídas do `Freud10DApparatus` (§5c — circularidade virtuosa: freud10d alimenta o kernel que alimenta o dunker) |

Call-sites a trocar depois do builder existir: `app.py:174`,
`soul/api.py:43,115` — mesma assinatura `affect_state(host_state)`, só o dict
muda.

### 5b. Dunker com métricas reais

`agency/dunker.py:105-108` já aceita `psychoanalytic_metrics,
topology_metrics, free_energy` (falta `pedagogical_bridge`, presente na
assinatura canônica :1436). Proposta de fontes:

| Campo dunker | Fonte MPS candidata |
|---|---|
| `psychoanalytic_metrics.psychoanalytic_regime` | mapeamento de `homeostasis.state` (OPTIMAL→`reparacao`, STRESSED→`estagnacao`, CRITICAL→`colapso`, RECOVERY→`reparacao`, EXPLORING→`destituicao_subjetiva`?) + `regime` Page-Hinkley events — **`destituicao_subjetiva` é o único regime que liga a ética de Soler** (`:1350-1357`), calibrar com cuidado |
| `psychoanalytic_metrics.is_mourning` | `freud10d.get_10d_metrics().pleasure < 0 sustentado` ou `RepressionChannel.repressed_charge > threshold` |
| `topology_metrics.betti_0` | componentes conexas do grafo de camadas (§5d) — `betti_0 > 1` = camadas desconectadas funcionalmente (não-fusão → morosidade) |
| `topology_metrics.betti_1_spectral` | ciclos no grafo de camadas ou no `symbolic_hypergraph` |
| `topology_metrics.topology_fragmentation` | `1 −` densidade do grafo de camadas; ou `metastability.s_meta` invertido |
| `free_energy` | **`expectation.pred_err`** (`stages.py:148-169` — erro do preditor ridge normalizado) — é literalmente surpresa preditiva; já flui em `modulation.pred_err` (`modulator.py:87`). Escalar ×50 p/ casar com `clip01(fe/50)` (:446) |
| `pedagogical_bridge` | `safety/pedagogical_refusal.PedagogicalDisposition` → `perrenoud_regime_contrato` (`EXECUTE≈contrato_cumprido`, `REFUSE≈quebra_contrato`? — mapeamento [INTERPRETAÇÃO], precisa revisão teórica) |

### 5c. `freud10d` — consumidores candidatos (ordenados por custo de wire)

1. **`soul` axes round-trip (barato, semântico)**: rodar
   `Freud10DApparatus.forward(perception)` por ciclo do daemon com
   `perception` = vetor MPS reduzido (ex.: `[attention_entropy_mean,
   hidden_norm_mean, attractor_score, c_soma, pred_err]` normalizados — o Rust
   injeta só a **média** em `state[phi]`, então um vetor MPS denso basta);
   `freudian_values_from_state(state_vector())` devolve `{phi, psi, sigma,
   epsilon, omega, lambda_, zeta}` — as mesmas chaves do soul (`soul/api.py:54-59`)
   mais omega/zeta/lambda. Wire: `kernel_daemon/scheduler.py` após
   `phi_meta` (:88-93) → `bundle["freud10d"]`; `soul._compute_state` pode
   usar `freud10d.phi/psi` como 3ª fonte (resolvendo o `mono_source` de
   `feedback.py:49-52`).
2. **`inrc_recommend` como detector de campo estagnado** (:321-336):
   `"N"` = `stagnant_field_mean_abs<0.15` — análogo estrutural da
   **perseveração**; `"C"` = ego-superego imbalance >0.4 — análogo do conflito
   superego×pulsão. Publicar em `kernel.freud10d.inrc`.
3. **`dream cycle`**: `agency/dream.py` metaboliza resíduos memtrias —
   alimentar `forward()` com o digest do sonho e registrar `tension_window(n)`
   no witness = "sonho como descarga tensional" (Freud 1900 via Giseli).
4. **`psychoanalysis/defense_mechanisms.assess`** + **`freudnet_repression`**:
   `structural_conflict()` e `topographic_flow()` dão `conflict_intensity`,
   `repression`, `return_repressed` — insumos diretos para os scores de defesa
   e para `is_mourning` (§5b).
5. **`neutrosophic_state()` → `omnimind_metrics.quadruple_topsis`**: o único
   produtor natural de quádruplas neutrosóficas para o TOPSIS do crate metrics
   — fecha o par órfão↔órfão.

### 5d. `dendritic_depth` sobre um W concreto existente

Proposta MPS-nativa (**[DERIVADO]**): construir `W` por geração a partir dos
sidecars `activation_steps/*.npz` (`traj: (T,L,D)`):

```
W[i,j] = |corr(mean-trajetória norm da camada i, idem j)|   (43×43 ou 49×49)
```

- `dendritic_depth(W)` = profundidade média do fluxo efetivo entre camadas —
  leitura literal da tese de Giseli aplicada ao transformer: profundidade
  menor ⇒ topologia de processamento mais "achatada"/integrada.
- Alternativa barata sem traj: `W` da matriz de covariância das normas por
  camada na janela do attractor (`attractor._norm_series` já produz
  `(window, n_layers)` — `phi_layer._layer_profile_entropy` usa a mesma
  matriz, phi_layer.py:46).
- `compare_depth_vs_recognition` requer `recognition_fn` — candidato:
  `_snr_discrimination` já embutido (:162-185), ou `eff_rank` do
  hidden_spectral como proxy de discriminação.
- Toy path (zero risco): `markov_blanket.connectivity_matrix(nodes6=True)`
  → dendritic sobre os 6 nós do blanket (Z,M,R,T,E,P) — demonstra o pipeline
  sem compromisso teórico.

### 5e. Detecção das aberturas na camada basal (design)

As falhas da refactor battery (0/11 resolvidos, `submitted=0` bloqueado pelo
gate de cobertura — PAPER_WRITEUP §3.4c; ledger local `battery_results.sqlite`
hoje sem tabelas **[LIMITE]**) têm dois polos, e a camada freud10d/dendritic
oferece detectores análogos:

| Abertura | Polo clínico (monografia §994) | Detector basal proposto |
|---|---|---|
| **Submissão prematura** (E4B: 96.8% submit, 0/31) | "descarrega o ato antes da elaboração" | `pleasure` spike cedo no `Freud10DApparatus` (pleasure = −Δtension, lib.rs:144-149): dump tensional antes de acumular elaboração; na trajetória: `dendritic_depth(W_t)` caindo cedo = fluxo basal colapsando para atalho emissivo |
| **Perseveração** (12B: 74% timeout, 80% avoidance) | "retém o ato até o colapso do enquadre" | `inrc_recommend → "N"` (campo estagnado); `tension_window` plateau (tensão alta estável sem pleasure); na trajetória: autocorrelação `cos(h_t, h_{t+k})` alta-periódica (M3 do OW-STU-018) + `eff_rank` temporal colapsando |
| **Omissão de entry points** (estrutural) | falha de planejamento, não degeneração | [LIMITE] OW-STU-018 §6 já provou: MPS não discrimina omissão — cobertura é o feature dominante. A camada basal pode oferecer **pré-sinal**: `contract drift` (M3: `cos(h_t, h_prompt)`) decaindo nas camadas médias — onde o writeup localiza o pico L35-42 do 12B |

**[INTERPRETAÇÃO]** O casamento é elegante: o `Freud10DApparatus` é uma
máquina de estado tensional de 5 iterações — `tension`/`pleasure` são o
análogo máquina do **gasto psíquico G_t** da monografia (vetor de custo
processual para conter descarga, monografia :105). O polo E4B = pleasure
precoce (descarga); o polo 12B = tension plateau (retenção). Detectar esses
regimes na trajetória dos sidecars é "atacar as aberturas na camada basal"
sem tocar em prompt nem peso.

---

## 6. Cruzamento monografia × writeup

Fontes: `data/psicodiagnostico_v/MONOGRAFIA_ESTUDO_PSICODIAGNOSTICO_V.md`
(Fabrício Silva, 2137 linhas) × `docs/PAPER_WRITEUP.md` (277 linhas) ×
`docs/design/OW-STU-018`, `docs/results/mps_spectral_first.md`, `OW-STU-009/010`.

### 6.1 Onde se tocam

| Tema | Monografia | Writeup |
|---|---|---|
| Vacilo (dois polos) | :994 — "duas posições clínicas do mesmo fracasso de finitude executiva" | §3.1/§4 — mesma tabela 31B/12B/E4B, mesmas taxas (96.8%, 74%) |
| Dual-brain prescrição | :905, :1061 — `omni_worker` como instância implantada | §3.4a — mesma arquitetura detalhada (peer-swap, 9210→218 MiB) |
| Formato determina degeneração | :902 — 0/40 chat vs 25/40 completion | §3.2c — mesma ablação |
| Cascade pilot | :903 — McNemar NS, −47.1% tokens | §3.2d — idêntico |
| Fase 0 MPS como pré-requisito | §3.7 (:387-399) — "antes de qualquer intervenção (steering, pruning, cascade reset), medição pura MPS por camada por passo" | §3.4b — reporta a implementação da captura (sidecars + steps) |

### 6.2 Onde divergem / tensões a resolver na comparação do operador

1. **Fase 0 prescrita × Fase 0 implementada**: a monografia (:389-397) exige
   χ(t,L), PR(t,L), eff_rank(t,L) **por token por camada** (~702k
   pontos/modelo) antes de intervenção, com thresholds PR<20 e χ>48 marcados
   como "calibração proposta, não achado". O writeup reporta a captura por
   passo já **ligada** (`activation_steps`, every=8) — ou seja, a Fase 0 da
   monografia está parcialmente materializada no worker, mas **sem análise
   χ(t,L) nem mapa de calor** — critério de avanço (:397) não cumprido.
2. **Divergência numérica espectral — inconsistência residual**: a nota de
   auditoria da monografia (:907) registra que IPR/eff_rank 114.6/40.3 "não
   são reproduzíveis pelo caminho de código publicado" (hidden_spectral
   computa `e^H`, não participation ratio de Roy-Vetterli; OW-AUD-018/020 →
   ≈2.5 para ambos). O writeup corrigiu parcialmente: a tabela §3.4b rotula
   `IPR_dim` 114.6/40.3 (intra-vetor) e `eff_rank_K` 2.496/2.516 (inter-gerações)
   — **mas o abstract ainda diz "eff_rank=114.6 vs 40.3"**, preservando a
   rotulagem errada. `mps_spectral_first.md` também usa "eff_rank" para o que
   é IPR. **[LIMITE]** Ponto concreto para o operador na comparação.
3. **0/88 vs 40/40**: monografia :905 (nota de auditoria) — "o manuscrito
   reporta 0/88; o artefato canônico disponível documenta 40/40 e a cifra 88
   não foi localizada". Writeup §3.4a mantém "88/88 execuções (0%)".
   **[LIMITE]** discrepância em aberto nos artefatos.
4. **Gasto psíquico G_t**: monografia mede G_t ∈ R⁹ **relacional**
   (V11-D10, :105, :359) — custo de conter descarga na relação. Não propõe
   análogo interno. Este estudo propõe `tension/pleasure` do freud10d +
   `c_soma` da metastability como a versão máquina-interna de G_t — ponto de
   contato original deste doc, não presente em nenhum dos dois textos.
5. **"Camada basal/interna"**: a monografia só opera camada interna como
   *medição* (Fase 0) — nunca como *estado funcional do sistema*. O writeup
   opera a interna como *diagnóstico* (spectral, IPR). Nenhum dos dois tem um
   subsistema interno vivo (o que freud10d+dendritic+dunker wired ofereceria)
   — lacuna compartilhada que este design endereça.
6. **Dendritic/Giseli**: **NÃO LOCALIZADO** na monografia — a tese de Giseli
   de Sousa só aparece em `dendritic_morphology.py:6-30` e nos docs OW-STU.
   A ponte dendritic↔Vacilo (§5e) é proposta deste doc.

---

## 7. Próximos passos priorizados

| # | Ação | Esforço | Desbloqueia |
|---|---|---|---|
| P0 | `host_state_builder`: mapear bundle `kernel.cycle` → schema flat do kernel (tabela §5a); trocar `{"soma": probe()}` em `app.py:174` e `soul/api.py:43,115` | S | vetor 28d real → families dunker com sinal ≠ 0 → soul.phi/dodeca honestos |
| P1 | Alimentar `dunker_architecture(..., free_energy=modulation.pred_err×50, topology_metrics={betti_0/fragmentação do grafo de camadas}, psychoanalytic_metrics={regime←homeostasis})`; expor `pedagogical_bridge` no adapter | S | 4º argumento do schema; sentiments/soler/enriquecimento topo funcionam |
| P2 | Wire `Freud10DApparatus` no `kernel_daemon/scheduler.py` (após phi_meta, :88-93): `forward(perception_mps)` por ciclo → `bundle["freud10d"]` + `freudian_values_from_state` → soul axes + `inrc_recommend` publicado | S-M | primeiro estado interno vivo; detector "N"/"C"; is_mourning p/ §5b |
| P3 | `W_layergraph` a partir de `activation_steps` (corr entre séries de norma por camada) → `dendritic_depth`/`morphology_score` por geração → tópico `kernel.dendritic` | M | dendritic wired; detector basal de perseveração (§5e) |
| P4 | Experimento `tension/pleasure` × verdicts da battery: replay dos sidecars por run rotulada → correlacionar pleasure-spike-cedo × premature_submit e tension-plateau × timeout | M | validação empírica do detector do Vacilo basal |
| P5 | Corrigir labels espectrais (abstract do writeup "eff_rank=114.6" → IPR_dim; `mps_spectral_first.md`) e reconciliar 0/88 vs 40/40 | S | consistência monografia×writeup antes da submissão |
| P6 | Toy: `dendritic_depth(markov_blanket.connectivity_matrix(nodes6=True))` + `quadruple_topsis` sobre `freud10d.neutrosophic_state()` — fecha crates órfãos com grafo mínimo | S | consumidores p/ metrics + freud10d sem risco |
| P7 | Persistir trust/quarantine (OW-STU-012 média, segue aberta) e verificar `OMNI_GATE_FAIL_CLOSED=1` no bring-up | M | governança sobrevive restart |

**Não recomendado agora**: M1/M4/M5 do OW-STU-018 (bond dim por passo, MPO de
atenção, χ* de compressão) — custo alto, benefício marginal sobre degeneração
já coberta por M3+eff_rank; e expor o `w` privado do pyclass freud10d (exigiria
rebuild do crate — a W canônica já está reconstruída em Python).

---

## Apêndice — convenções epistêmicas usadas

- **[DADO]**: lido diretamente em arquivo:linha ou artefato (npz inspecionado,
  sqlite consultado).
- **[DERIVADO]**: consequência calculada/deduzida dos dados citados.
- **[INTERPRETAÇÃO]**: proposta de leitura/mapeamento conceitual — não é fato.
- **[LIMITE]**: restrição conhecida ou dado ausente (ledger vazio, contagem
  0/88 não reconciliada, schema divergente).
- **NÃO LOCALIZADO**: buscado e ausente (consumidores, produtores de chaves,
  menções dendríticas na monografia).
