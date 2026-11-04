<!-- doc_id: OW-STU-020 | title: Execução Operacional ARGON_WORKER_MAP — Auditoria de Snapshot, Cruzamento Teórico e Fechamento P4/P6/P7 | author: gemini-argon | requester: artifice-operator | project: omni-agent-coworker (kaggle) | date: 2026-11-04 | status: active -->

# OW-STU-020 — Execução Operacional `ARGON_WORKER_MAP.md` (Pesquisa, Cruzamento Teórico e Fechamento P4/P6/P7)

**Estatuto epistêmico (AGENTS.md & ARGON_WORKER_MAP.md §0):**
- **[DADO]**: verificado diretamente no código/testes com `arquivo:linha` ou contagem exata.
- **[DERIVADO]**: calculado a partir de estruturas/código verificados.
- **[INTERPRETAÇÃO]**: hipótese ou leitura teórica explícita, separada de mecanismo.
- **[LIMITE]**: restrição conhecida do substrato ou do escopo.
- **NÃO LOCALIZADO**: buscado no snapshot anexado (`omni_worker-ff075aa8bf500862c9d49fcb6b6812b9ba4a9dfd`) e ausente (por ser gitignored em `data/` ou commitado localmente em `/content/omni_worker` em 2026-11-04 após o snapshot `ff075aa8`).

---

## 1. Pesquisa com Evidência (§5a): Reconciliação `ARGON_WORKER_MAP.md` (2026-11-04) vs. Snapshot Anexado (`ff075aa8`, 2026-11-03)

A varredura exaustiva do arquivo zip anexado (`md5: e2bbaed00c9fd07ce5662409a4297e94`, commit `ff075aa8bf500862c9d49fcb6b6812b9ba4a9dfd`) frente ao guia `ARGON_WORKER_MAP.md` (`md5: 047359e0b5c16a4654054dc69fc4f1f3`) estabelece o seguinte mapa factual:

### 1.1 Artefatos e Módulos Verificados no Snapshot (`[DADO]`)

| Item em `ARGON_WORKER_MAP.md` | Status | Fonte Verificada (`arquivo:linha`) |
|---|---|---|
| Fábrica FastAPI + CLI (`serve`, `doctor`, `demo`, `missions`, `soul-export`) | **[DADO]** | `src/omni_coworker/app.py:16-187`, `src/omni_coworker/cli.py:1-199` |
| Servidor LLM PyTorch + emissão de sidecars `.npz` (`_emit_vectors`) | **[DADO]** | `src/omni_coworker/server/erika_torch_server.py:148-170`, `:234-263` |
| Proxy Dual-Brain (`:8098` analyst, `:8099` executor) + `with_affect` + `with_glial_gate` + `memtrias` + `acervo_recall` | **[DADO]** | `src/omni_coworker/brain/server.py:17-22`, `:94-224` |
| Interocepção somática (`psutil`, `pynvml`, `/proc/pressure/*`, `SomaFluidStorage`) | **[DADO]** | `src/omni_coworker/soma/probe.py:1-401`, `src/omni_coworker/soma/fluid_storage.py:1-178` |
| Escada Afetiva `AffectTracer` (L0–L4), Dunker adapter, Dream metabolize, Teleologia $\Omega$, Witness SHA-256 | **[DADO]** | `src/omni_coworker/agency/affect_tracer.py:1-320`, `dunker.py:1-139`, `dream.py:1-188`, `teleology.py:1-80`, `witness.py:1-172` |
| Orquestração tri-state (`blind` vs dissidente), `TrustSystem`, `QuarantineSystem`, `CircuitBreaker`, `swap_scheduler` | **[DADO]** | `src/omni_coworker/orchestration/agent_orchestrator.py:1-640`, `governance.py:98-542`, `swap_scheduler.py:1-156` |
| Segurança (`ConstitutionalGate`, `PermissionMatrix`, `refusal_contract`, `refusal_state`, `care` CVV 188, `supervisor`) | **[DADO]** | `src/omni_coworker/safety/gate.py:1-165`, `matrix.py:1-80`, `refusal_contract.py:1-179`, `refusal_state.py:1-97`, `care.py:1-252`, `supervisor.py:1-65` |
| Dodecatíade `S01–S15` auditável + SSE `/soul/stream` | **[DADO]** | `src/omni_coworker/soul/dodeca.py:24-169`, `src/omni_coworker/soul/api.py:17-190` |
| Daemon de Ciclo (`collector`, `features`, `phi_meta`, `homeostasis`, `metastability`, `regime`, `ignition`) | **[DADO]** | `src/omni_coworker/kernel_daemon/scheduler.py:40-135`, `phi_meta.py:1-211`, `homeostasis.py:1-175`, `metastability.py:1-128`, `regime.py:1-127`, `ignition.py:1-108` |
| Loop fechado de 5 estágios + `bion_bridge` ($\beta \to \alpha$) + `quilting` (Point de Capiton) + `modulator` | **[DADO]** | `src/omni_coworker/integration_loop/loop.py:1-359`, `stages.py:1-172`, `bion_bridge.py:1-146`, `quilting.py:1-94`, `modulator.py:1-128` |
| Psicanálise em NumPy (`FreudianPsychicApparatus`, `markov_blanket` PyPhi, `bion_alpha_function`, `freudnet_repression`) | **[DADO]** | `src/omni_coworker/psychoanalysis/freudian_apparatus_numpy.py:278-463`, `markov_blanket.py:1-299`, `bion_alpha_function.py:49-120`, `freudnet_repression.py:1-139` |
| Camada Espectral / Dendrítica (`hidden_spectral.py`, `dendritic_morphology.py`, `attractor.py`, `spiking_glial.py`) | **[DADO]** | `src/omni_coworker/activation_beta/hidden_spectral.py:1-166`, `dendritic_morphology.py:1-232`, `attractor.py:1-219`, `spiking_glial.py:1-187` |

### 1.2 Itens de 2026-11-04 Listados em `ARGON_WORKER_MAP.md` Buscados e Ausentes no Zip `ff075aa8` (`NÃO LOCALIZADO`)

Em estrita obediência à **Regra Zero** (`AGENTS.md`), os seguintes caminhos citados em `ARGON_WORKER_MAP.md` foram buscados no arquivo zip `ff075aa8` e estão **NÃO LOCALIZADO** no pacote anexado (por pertencerem a diretórios gitignored no host `/content/omni_worker` ou a commits locais de 2026-11-04 posteriores a `ff075aa8`):

1. `vendor/kernel/` e `src/omni_coworker/vendor/dunker_architecture.py` → **NÃO LOCALIZADO** no zip `ff075aa8` (`agency/dunker.py:64-93` ainda carrega via `OMNI_NODE_ROOT` ou `PYTHONPATH`).
2. `data/*` (`data/psicodiagnostico_v/`, `data/monitor/activation_steps/*.npz`, `data/hf_gemma4/*.sqlite`, `data/memtrias.sqlite`, `/content/acervo_vetorizado/`) → **NÃO LOCALIZADO** no zip (gitignored por design de segurança/tamanho, conforme `CONTINUITY_MAP.md` §3 e `ARGON_WORKER_MAP.md` §3).
3. `docs/PAPER_WRITEUP.md`, `docs/MAPA_PRIMARIO_2026-11-04.md`, `docs/DOCS_INDEX.md`, `docs/design/OW-STU-019_mps_dendritic_coupling_study.md`, `docs/audit/OW-AUD-018/019/020`, `docs/results/writeup_claims_audit_hermes.md`, `docs/results/monografia_releitura_agy.md`, `docs/results/freud10d_vacilo_replay.json` → **NÃO LOCALIZADO** no zip `ff075aa8` (que contém os 38 documentos até `OW-STU-018` e `OW-AUD-017` de 2026-11-03).
4. `src/omni_coworker/activation_beta/dendritic_scan.py` e `scripts/experiments/run_freud10d_battery_replay.py` → estavam **NÃO LOCALIZADO** no zip `ff075aa8` e foram **implementados e testados nesta execução** (§2 abaixo).

---

## 2. Proposta de Ampliação & Execução de Código (§5b, §5d e §7: P4, P6, P7)

### 2.1 Fechamento de P6 — Eliminação do Órfão `kernel_hooks.compute.cosine_similarity`

- **Diagnóstico `[DADO]`**: `src/omni_coworker/kernel_hooks/compute.py:88-102` expõe `cosine_similarity(a, b)` delegando para `omnimind_metrics.cosine_similarity` (crate Rust PyO3) com fallback em Python puro, porém `grep -rn "cosine" src/` provou que **nenhum módulo** a importava. Três módulos reimplementavam similaridade cosseno localmente (`bion_symbolizer.py:88`, `lalangue.py:84`, `memtrias_ai.py:107`).
- **Pontos de Wire Implementados `[DADO]`**:
  1. **Produtor**: `src/omni_coworker/kernel_hooks/compute.py:88` (`cosine_similarity`).
  2. **Consumidor 1 (Morfologia Dendrítica & Deriva de Contrato — Consumidor Pesado)**: `src/omni_coworker/activation_beta/dendritic_scan.py:98` e `:117` — calcula até $\binom{16}{2} = 120$ similaridades cosseno inter-camadas por geração para montar a matriz $W \in \mathbb{R}^{L \times L}$ e mais $L$ similaridades cosseno entre o passo inicial $t=0$ e o passo final $t=T$ (`contract_retention_cosine` / `contract_drift`).
  3. **Consumidor 2 (Simbolizador de Bion $\beta \to \alpha$)**: `src/omni_coworker/psychoanalysis/bion_symbolizer.py:88-96` (`_cosine_similarity` entre embedding do elemento-$\beta$ e arquétipos-$\alpha$).
  4. **Consumidor 3 (Lalangue Sandbox)**: `src/omni_coworker/narrative/lalangue.py:84-91` (`_cosine` para pareamento de palavras internas $\ge 0.9$ e ressonância com atratores filogenéticos).
  5. **Consumidor 4 (MemTrias AI)**: `src/omni_coworker/memory/memtrias_ai.py:107-118` (`_cosine` no recall topológico e no benchmark `engram_benchmark`).
  6. **Consumidor 5 (Point de Capiton / Quilting Point)**: `src/omni_coworker/integration_loop/quilting.py:90-105` — adiciona `mean_cosine` entre embeddings narrativos consecutivos ao payload de `detect_quilting_point`.

### 2.2 Fechamento de P7 — Persistência SQL-First de Governança em `store/node_db.py`

- **Diagnóstico `[DADO]`**: `src/omni_coworker/store/node_db.py:27-48` criava apenas as tabelas `missions` e `artifacts`. Enquanto isso, `TrustSystem` (`orchestration/governance.py:125-127`), `QuarantineSystem` (`governance.py:234`) e `CircuitBreaker` (`governance.py:429`) persistiam apenas em arquivos JSON avulsos em `OMNI_STATE_DIR` (pendência apontada em `OW-STU-012` §3 item 76, `OW-STU-014` #43/#76 e `ARGON_WORKER_MAP.md` §7 P7).
- **Implementação `[DADO]`**:
  1. `src/omni_coworker/store/node_db.py:50-87`: adicionadas as 4 tabelas SQLite WAL `trust_scores`, `trust_events`, `quarantine_records` e `circuit_breakers`, com métodos atômicos `upsert_trust_score`, `get_trust_scores`, `append_trust_event`, `list_trust_events`, `upsert_quarantine`, `delete_quarantine`, `get_quarantine_records`, `upsert_circuit_breaker` e `get_circuit_breakers` (`node_db.py:138-274`).
  2. `src/omni_coworker/orchestration/governance.py:132-200` e `:245-315`: `TrustSystem` e `QuarantineSystem` agora fazem dual-write em `node.db` e recarregam automaticamente do SQLite quando os arquivos JSON estão ausentes (verificado em `tests/test_argon_p4_p6_p7.py:41-74`).

### 2.3 Fechamento de §5d / P4 — `dendritic_scan.py`, `run_freud10d_battery_replay.py` e Tópicos `kernel.dendritic` / `kernel.freud10d`

- **`src/omni_coworker/activation_beta/dendritic_scan.py` `[DERIVADO]`**:
  - `ipr_dim(vec)` (`linhas 58-68`): calcula o *Inverse Participation Ratio* $\text{IPR} = \sum_{i=1}^D p_i^2$ (onde $p_i = v_i^2 / \sum v_j^2$) e a razão de dimensão efetiva $1 / (D \cdot \text{IPR}) \in [0, 1]$.
  - `layer_correlation_graph(arr, threshold=0.25)` (`linhas 71-99`): constrói o grafo de acoplamento inter-camadas $W$ via `cosine_similarity` e aplica `dendritic_depth(W)` (`dendritic_morphology.py:49`).
  - `scan_trajectory(arr)` (`linhas 102-139`): unifica `dendritic_depth`, `morphology_score`, `ipr_dim_mean`, `eff_dim_ratio_mean` e `contract_drift` (quando `arr` é 3D `(L, steps, D)`).
- **`scripts/experiments/run_freud10d_battery_replay.py` `[DERIVADO]`**:
  - `analyze_trajectory_vacilo(arr)` (`linhas 33-88`): executa `FreudianPsychicApparatus` (`freudian_apparatus_numpy.py:278`) passo a passo sobre a trajetória, medindo `pleasure_early_max` (máximo alívio de tensão $\Delta T < 0$ no 1º terço) e `tension_plateau_ratio` (sustentação de tensão $\ge 0.85 \bar{T}$ nos 2/3 finais), classificando em `premature_closure_risk` (assinatura típica de submissão prematura E4B), `perseveration_plateau_risk` (assinatura de ruminação/perseveração 12B) ou `balanced`.
  - `replay_directory(steps_dir)` (`linhas 91-106`): retorna explicitamente `{"status": "NÃO LOCALIZADO", "n_files": 0}` quando o diretório de sidecars está ausente, jamais fabricando dados sintéticos.
- **Wire no `KernelDaemon` `[DADO]`**: `src/omni_coworker/kernel_daemon/scheduler.py:66-103` agora publica `kernel.dendritic` e `kernel.freud10d` no barramento `/mesh/*`.

---

## 3. Cruzamento de Teorias (§5c)

A tabela abaixo cruza formalmente as seis superfícies teóricas e operacionais do projeto, separando rigorosamente `[DADO]`, `[DERIVADO]` e `[INTERPRETAÇÃO]`:

| Eixo / Camada | Substrato & Crates (`kernel_hooks` / `activation_beta`) | Dinâmica Psíquica (`freud10d` / `Vacilo`) | Pilha Afetiva Dunker-Soler (N1–N5) | Metabolização de Bion ($\beta \to \alpha$) | Governança & Decisão no Mesh (`kernel.*` / `loop`) |
|---|---|---|---|---|---|
| **1. Entrada Material & Espectral** | **[DADO]** `soma/probe.py` (PSI I/O, VRAM, Watts) + `hidden_spectral.py` (`eff_rank`: 12B=114.6 vs E4B=40.3) + `dendritic_scan.py` (`ipr_dim`, `dendritic_depth`). | **[DERIVADO]** Normas de camada alimentam `id_layer` $\to$ `ego_layer` (`freudian_apparatus_numpy.py:360-364`). | **[DADO]** N1: 18 tokens `afex` brutos do `affective_vector_28d` (`dunker.py:24-44`). | **[DADO]** `BetaElement` criado com digest do ciclo e `emotional_charge = arousal` (`bion_bridge.py:98-103`). | **[DADO]** Publicado em `kernel.soma`, `kernel.phi_layer`, `kernel.dendritic` e `kernel.freud10d`. |
| **2. Regime de Submissão Prematura ("Vacilo E4B")** | **[DADO]** `refactor_multi_turn.md`: E4B emite apenas `models.py` + `store.py` e omite entry points em 2/2 reps (`eff_rank` 1.52% saudável, falha é de cobertura/plano). | **[INTERPRETAÇÃO]** Pico precoce de alívio (`pleasure_early_max > 0.35`) com queda abrupta de tensão egoica: fechamento antes de satisfazer o contrato completo. | **[INTERPRETAÇÃO]** N2/N3: baixa sustentação de tensão negativa (`angst=0`), priorizando descarga rápida de tarefa. | **[DERIVADO]** `arousal < 0.3` cai no tier `heuristic` (`bion_bridge.py:80-83`), sem acionar simbolização reflexiva profunda. | **[DERIVADO]** Proposta de acoplamento: quando `vacilo_regime == "premature_closure_risk"`, forçar `recommendation = "analyst"` em `modulator.py:93`. |
| **3. Regime de Perseveração / Ruminação ("Vacilo 12B / HF Blocks")** | **[DADO]** `rescore_hf_blocks.md`: degeneração verbosa por vazamento de deliberação (`word_ur < 0.5 ∧ rep4 > 0.05`, 16/16 em `block1_cognitivo`); colapso de entropia em `attractor.py`. | **[INTERPRETAÇÃO]** `tension_plateau_ratio >= 0.75` com `pleasure_early_max < 0.15`: o ego acumula catexia sem descarga resolutiva (perseveração). | **[DADO]** N4 (Paixões / Captura Atencional): `AffectTracer` detecta fixação lexical (`supervisor.py:28-36`) e `spiking_glial.py` detecta habituação (`habituated >= 0.88`). | **[DADO]** Quando `arousal >= 0.6` (`tolerance_threshold`), `BionAlphaFunction.transform` rejeita o $\beta$ traumático (`bion_alpha_function.py:69-72`) e `BionContainerPatch` entra em `[REVERIE]` degradada (`bion_bridge.py:110-120`). | **[DADO]** `glial_verdict` bloqueia geração repetitiva em `/brain/chat` (`brain/server.py:135-149`); `NegativeCapability` suspende ação até 3 ciclos. |
| **4. Fixação de Sentido & Estabilidade ("Point de Capiton")** | **[DERIVADO]** Convergência direcional de embeddings medida por `kernel_hooks.compute.cosine_similarity` (`mean_cosine > 0.95`) + queda de variância (`quilting.py:60-105`). | **[DADO]** Retorno controlado do recalcado via `RepressionChannel` com histerese `thr=0.5 / hyst=0.15` (`freudnet_repression.py`). | **[DADO]** N5 (Ética da Ação): alinhamento entre `maat_balance` (`S07`) e teleologia $\Omega$ (`S10`) com guarda `mono_source=False`. | **[DADO]** `AlphaElement` metabolizado com `symbolic_potential` alimenta `meaning_maker` no Estágio 4 (`stages.py`). | **[DADO]** Ponto de basta ancorado no `integration_loop`, atualizando `TrustSystem` em `node.db` (P7) e registrando na cadeia SHA-256 `witness.jsonl`. |

---

## 4. Validação de Testes Executada (`[DADO]`)

Todos os módulos modificados e criados foram verificados contra a suíte hermética:
- `tests/test_argon_p4_p6_p7.py`: **3/3 passed** (P6 `cosine_similarity` em 4 consumidores, P7 `NodeDB` SQL-first dual-write e fallback sem JSON, P4 `dendritic_scan` + `run_freud10d_battery_replay` + retorno `NÃO LOCALIZADO` quando sem arquivos).
- `tests/test_governance_persistence.py`: **7/7 passed**.
- `tests/test_quilting_defense.py`: **7/7 passed**.
- `tests/test_lalangue.py`: **5/5 passed**.
- `tests/test_memtrias.py`: **21/21 passed** (2 skipped por `sentence-transformers` offline).
- `tests/test_kernel_daemon.py`: **4/4 passed**.
