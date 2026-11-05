<!-- doc_id: OW-MAP-001 | title: Mapa Primário — omni_worker × kilombo-sovereign | date: 2026-11-04 | author: kiro | status: active -->

# Mapa Primário — omni_worker × omnimind-kilombo-sovereign

> **Classificação epistêmica**: [DADO] = verificado em arquivo/log/código;
> [DERIVADO] = calculado de dados; [INTERPRETAÇÃO] = análise do agente;
> [LIMITE] = restrição conhecida não implementada.

---

## 1. TOPOLOGIA DE SERVIÇOS VIVOS

### 1.1 Serviços em produção (`omni_worker`)

| Serviço | Processo | Porta | Estado declarado | Fonte |
|---------|----------|-------|-----------------|-------|
| Worker API | `omni-coworker serve` (uvicorn, `app.create_app()`) | `:8081` | ATIVO | [DADO] `README.md`, `app.py` |
| Brain Analyst | `erika_torch_server --model gemma-4-12B-it --load-4bit --eager-attn --port 8098` | `:8098` | ATIVO ~11.2 GB VRAM | [DADO] `CONTINUITY_MAP.md §3` |
| Brain Executor | `erika_torch_server --model gemma-4-E4B-it --port 8099` | `:8099` | CARREGADO/EVICTED por swap | [DADO] `CONTINUITY_MAP.md §3` |
| Brain Judge | `erika_torch_server --model gemma-4-31B-it --port 8100` | `:8100` | ATIVO em tier xl (>=60GB VRAM) / OMNI_JUDGE_BRAIN=1 | [DADO] `start_omni_worker.sh:110`, commit `36b41ad` |
| State Guard | `omni_coworker.store.state_guard` (loop 6h, snapshots tar.gz) | — | ATIVO PID em `runtime_config/pids/` | [DADO] `PENDING_ROADMAP.md P1` |
| Swap Scheduler | `omni_coworker.orchestration.swap_scheduler` (tick 600s) | — | ATIVO | [DADO] `CONTINUITY_MAP.md §3` |
| Kernel Daemon | `kernel_daemon/` (ignition + collector) | via API | ATIVO | [DADO] `app.py:44-57` |
| Integration Loop | `integration_loop/loop.py` (interval_s=60) | via API | ATIVO | [DADO] `app.py:59-74`, `loop.py:32` |
| Soma Probe | `GET /soma/probe → probe_recorded()` | via API `:8081` | on-demand | [DADO] `README.md`, `app.py:76` |
| Witness | `agency/witness.py` JSONL hash-chain (`data/witness.jsonl`) | via API | append-only in-process | [DADO] `README.md` |
| Supervisor Battery | `scripts/supervisor_battery/run_supervisor_battery.py` | — | batch manual | [DADO] `README.md` |

### 1.2 Processos do soberano (`omnimind-kilombo-sovereign`)

O repositório soberano é **read-only** (referência histórica e teórica privada do autor); seus serviços não são gerenciados pelo `omni_worker`. O `omni_worker` é desacoplado e autossuficiente: crates Rust vendored em `vendor/kernel/`, dunker em `src/omni_coworker/vendor/` e bateria canônica V10 em `vendor/benchmarks/`. Processos relevantes declarados no arquivo histórico:

- `kernel/sovereign_daemon/` — daemon soberano (v1–v5 em `src/erika/`)
- `kernel/sovereign_kuramoto/` — ritmo basal (Kuramoto coupling)
- `kernel/somatic_daemon/` — interoceptor somático soberano
- `erika/kernel_daemon*.py` — versões v1/v4/v5 do daemon Erika
- `erika/mesh_runtime_daemon.py` — runtime de malha de agentes
- `llm/` — watsonx client, prompt registry, telemetria LLM

**[LIMITE]** Sem log vivo do soberano acessível a este agente. Estado presumido de docs.

---

## 2. CAMADAS DA ARQUITETURA

### 2.1 Stack omni_worker (7 camadas)

```
┌─────────────────────────────────────────────────────────────────────┐
│  CAMADA 7 — SOUL / UI PÚBLICA                                        │
│  soul/state (SSE live), soul/static/superapp.html (464ln),          │
│  soul/api.py, dashboard (docs/index.html)                            │
├─────────────────────────────────────────────────────────────────────┤
│  CAMADA 6 — AGENTES / ORQUESTRAÇÃO                                   │
│  agents/{debug,analyst,reviewer,code}_agent.py                       │
│  agents/bus.py (EventBus inter-agentes)                              │
│  agents/persona.py, modes.py, external_cli_agent.py (ACP/Shell)     │
│  orchestration/agent_orchestrator.py (juízes adversariais + reset)  │
│  orchestration/governance.py (trust/quarantine/rollback/breaker)     │
│  orchestration/swap_scheduler.py                                     │
├─────────────────────────────────────────────────────────────────────┤
│  CAMADA 5 — SAFETY / GOVERNANÇA                                      │
│  safety/matrix.py (PermissionMatrix adapter)                         │
│  safety/gate.py (ConstitutionalGate adapter, OMNI_GATE_FAIL_CLOSED) │
│  safety/jail.py (107ln, política real em camadas)                    │
│  safety/care.py (251ln, escalação territorial Brasil: CVV/CAPS/CRP) │
│  safety/supervisor.py [NÃO EXISTE — pendência aberta P2]            │
├─────────────────────────────────────────────────────────────────────┤
│  CAMADA 4 — AGENCY / PSIQUE                                          │
│  agency/affect_tracer.py (L0–L4, 6 famílias afex)                   │
│  agency/analyst.py (adapter psychoanalytic_analyst)                  │
│  agency/dream.py + dream_cycle (metabolize real + memtrias)         │
│  agency/teleology.py [pendência — import integration_loop é stub]   │
│  agency/curiosity.py [zero testes]                                   │
│  agency/dunker.py (adapter soler/dunker)                             │
│  agency/discourse_discovery.py (4 Discursos Lacan — léxico)         │
│  agency/witness.py (JSONL hash-chain)                                │
├─────────────────────────────────────────────────────────────────────┤
│  CAMADA 3 — BRAIN / LLM PROXY                                        │
│  brain/server.py (proxy httpx role-routed → :8098/:8099)            │
│  brain/activations.py [dead code — Kilo P5: wire ou deletar]        │
│  server/erika_torch_server.py (servidor real: NF4, eager-attn,       │
│    output_hidden_states, output_attentions, ring buffer 256,         │
│    /erika/unload|reload, PYTORCH_CUDA_ALLOC_CONF fix)               │
├─────────────────────────────────────────────────────────────────────┤
│  CAMADA 2 — SOMA / PERCEPÇÃO / STORE                                 │
│  soma/probe.py (psutil + pynvml, probe_recorded(), SQLite WAL)       │
│  soma/store.py (somatic_store, somatic_probes.sqlite)                │
│  store/node_db.py (SQLite WAL, artifacts/missions/events)            │
│  store/code_index.py (all-MiniLM + faiss, 201 chunks, 384d)         │
│  store/state_guard.py (snapshots tar.gz, retenção N=3)              │
│  store/audit_adapter.py (ImmutableAuditSystem ponte soberano)        │
│  memory/ (memtrias: 7 namespaces, >250 memórias)                    │
├─────────────────────────────────────────────────────────────────────┤
│  CAMADA 1 — KERNEL / MÉTRICAS / ATIVAÇÕES                           │
│  kernel_hooks/ (3 crates Rust/pyo3: compute.py wrapper)             │
│  kernel_daemon/ (ignition.py GWT-lite + collector.py)               │
│  activation_beta/ (attractor, phi_layer, hidden_spectral, dendritic)│
│  integration_loop/ (sensory→qualia→narrative→meaning→expectation)   │
│  psychoanalysis/ (markov_blanket, beta_element, bion_patches)       │
│  psychology/ + narrative/ + metacognition/                           │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Integração com o soberano (kilombo) — o que trazemos vs. o que não trazemos

| Componente soberano | Trazido para omni_worker? | Como | Fonte |
|---------------------|--------------------------|------|-------|
| `src.erika.erika_torch_server` | **SIM — portado integralmente** | `server/erika_torch_server.py` (eager-attn + /erika/unload\|reload adicionados) | [DADO] `CONTINUITY_MAP §1` commit `9fabc4d` |
| `src.orchestration.permission_matrix.PermissionMatrix` | **SIM — adapter** | `safety/matrix.py` (fallback standalone) | [DADO] `DIRECTORY_CONTRACT.yaml` |
| `src.autopoietic.constitutional_gate` | **SIM — adapter** | `safety/gate.py` (ChangePayload→DeliberationCertificate) | [DADO] `DIRECTORY_CONTRACT.yaml` |
| `src.agentes.psychoanalytic_analyst` | **SIM — adapter** | `agency/analyst.py` (guard OMNI_ANALYST_CONFIG) | [DADO] `DIRECTORY_CONTRACT.yaml` |
| `src.cognitive.dream_weaver` | **SIM — adapter + ciclo próprio** | `agency/dream.py` + `dream_cycle`; probe canônico morto removido | [DADO] `PENDING_ROADMAP.md P2` |
| `src.kernel.*` (9 crates pyo3) | **SIM — compilados opcionais** | `kernel_hooks/` via `scripts/build_kernel.sh` | [DADO] `DIRECTORY_CONTRACT.yaml`, `README.md` |
| `src.psychoanalysis/` (BionAlphaFunction, container_contained) | **PARCIAL** | `psychoanalysis/` reimplementa NeutrosophicTriplet mínimo; BionAlphaFunction **não portada** | [DADO] `psychoanalysis/__init__.py:16-23` |
| `src.kernel.sovereign_daemon*` | **NÃO** | Não gerenciado pelo worker; referência read-only | [INTERPRETAÇÃO] |
| `src.llm.watsonx_bounded_client` | **NÃO** | Substituído por `brain/server.py` proxy httpx → erika_torch_server | [INTERPRETAÇÃO] |
| `src.erika.intersubjective_affect_pipeline` | **NÃO** | Afeto no worker via `agency/affect_tracer.py` (L0-L4 léxico+LLM) | [INTERPRETAÇÃO] |
| `src.infrastructure.federation_witness_incremental` | **NÃO** | Worker tem `agency/witness.py` próprio (JSONL hash-chain sha256+fcntl) | [INTERPRETAÇÃO] |
| `src.kernel.sovereign_kuramoto` | **NÃO** | Sem ritmo basal Kuramoto no worker; GWT-lite via `kernel_daemon/ignition.py` | [INTERPRETAÇÃO] |
| `src.quantum_*` (quantum_ai, quantum_metrics, quantum_real) | **NÃO diretamente** | MPS bridge soberano é read-only reference; worker tem `activation_beta/hidden_spectral.py` (SVD/bond_dims) como MPS-lite | [DADO] `OW-STU-018 §2.4` |
| `src.erika.memory.py` / `src.embeddings` | **PARCIAL** | `store/code_index.py` (all-MiniLM+faiss) + `memory/` (memtrias); acervo vetorizado HF via env `OMNI_ACERVO_DIR` | [DADO] `README.md`, `CONTINUITY_MAP §3` |
| `src.autopoietic.*` completo | **NÃO** | Somente o gate (adapter); autopoiese plena requer `omni_node` no PYTHONPATH | [DADO] `README.md Compatibilidade` |
| `src.consciousness / phenomenology` | **NÃO** | IIT/GWT medidos via proxies locais: `psychoanalysis/markov_blanket.py` (PyPhi 4-6 nós) + `kernel_daemon/ignition.py` | [DADO] `PENDING_ROADMAP P0 OW-STU-016` |

---

## 3. INTEGRAÇÃO LLM — FLUXO COMPLETO

### 3.1 Caminho de uma chamada LLM (`/brain/chat`)

```
Requisição HTTP → brain/server.py
  │
  ├─ [affect] affect_tracer.get_affect_tracer().observe(user_turn)
  │    └─ AffectTracer (singleton) → L0-L4 escada léxica+LLM
  │         L0: lexicon puro (sem custo)
  │         L1: densidade familiar (threshold 0.4)
  │         L2/L3: juiz-analista 12B (brain_chat_json)
  │         L4: retém geração (bloqueia)
  │
  ├─ [gate] safety/gate.py → ConstitutionalGate
  │    └─ OMNI_GATE_FAIL_CLOSED=1 → fail-closed em produção
  │
  ├─ [inject] memtrias recall + acervo vetorizado (OMNI_MEMTRIAS_AUTO_LOG)
  │
  ├─ [route] role-based routing → analyst :8098 | executor :8099
  │
  └─ erika_torch_server (NF4 on L4)
       ├─ model.generate(output_hidden_states=True, output_attentions=True)
       ├─ _summarize_hidden() → norm/mean/std por camada
       ├─ _summarize_attention() → entropia escalar última camada
       ├─ _emit_activation() → ring buffer 256 + JSONL
       └─ _emit_vectors() → sidecar .npz (n_layers × hidden, fp16)
            └─ data/monitor/activation_vectors/ (últimos 64 por modelo)
```

### 3.2 Consumo downstream das ativações (MPS)

```
erika_torch_server → data/monitor/erika_torch_activations.jsonl
  │
  ├─ kernel_daemon/collector.py (_read_new_activations, tail incremental)
  │    └─ activation_beta/attractor.py (norm_drift, entropy_collapse,
  │         divergent_layer, attractor_score — janela ≥4)
  │
  ├─ activation_beta/phi_layer.py (phi_breadth, phi_temporal_mi,
  │    phi_internal) ← hidden_spectral.spectral_features()
  │
  └─ activation_beta/hidden_spectral.py [MPS-lite]
       ├─ _load_recent() → últimos K=8 sidecars .npz por modelo
       ├─ _eff_rank() → SVD sobre matriz K×D por camada (participation ratio)
       ├─ _bond_dims() → Schmidt rank por corte MPS do vetor hidden
       └─ spectral_features() → {eff_rank_mean, spectral_entropy_mean,
            bond_dim_max_mean}
```

**[LIMITE]** `brain/activations.py` = dead code (não wired). MPS temporal
(por-passo) não implementado — hoje só último passo de geração é capturado
(`OW-STU-018 §2.1 L248`). MPS bridge soberano
(`transformer_mps_bridge_pilot.py`) é referência read-only, não integrado.

### 3.3 Swap inteligente (VRAM-aware)

```
orchestration/swap_scheduler.py (tick 600s)
  ├─ GET /health :8098/:8099 → VRAM usage + activations_buffered
  ├─ evict executor (:8099) se VRAM alta + delta ativações baixo
  │    └─ POST /erika/unload :8099
  └─ reload executor se headroom disponível
       └─ POST /erika/reload :8099
       └─ PYTORCH_CUDA_ALLOC_CONF=expandable_segments:False (fix OOM)
```

**[DADO]** Fix de VRAM residual: `expandable_segments:False` resolve
9210→218 MiB após unload (`CONTINUITY_MAP Addendum`).

---

## 4. INTEGRAÇÃO LLM × CAMADAS NEURAIS (MPS)

### 4.1 O que o worker implementa de MPS

| Componente | Onde | O que mede | Status |
|-----------|------|-----------|--------|
| Bond dimension (SVD) | `hidden_spectral._bond_dims()` | Schmidt rank por corte MPS do vetor hidden (reshape D→sites×2) | [DADO] implementado, testado `test_hidden_spectral.py` |
| Effective rank | `hidden_spectral._eff_rank()` | Participation ratio SVD sobre matriz K×D por camada | [DADO] implementado |
| Spectral entropy | `hidden_spectral.spectral_features()` | Entropia dos valores singulares por camada | [DADO] implementado |
| Ativação por passo | `erika_torch_server._generate()` | **Somente último passo** — sem trajetória temporal | [LIMITE] `OW-STU-018 §2.1` |
| MPS bridge soberano (χ trajectory) | `kilombo/scripts/experiments/transformer_mps_bridge_pilot.py` | χ completo (reshape, SVD sequencial, fidelidade) | [DADO] referência read-only, não consumido pelo worker |
| Phi proxy (GWT-lite) | `kernel_daemon/ignition.py` | `distinct_prefixes ≥3 ∧ coherence>0.5` → ignited; `synergy_proxy` (MI entre séries) | [DADO] implementado, **testado** `tests/test_ignition.py` |
| Phi (IIT PyPhi real) | `psychoanalysis/markov_blanket.py` | Φ de blanket 4-6 nós (E, P, mundo Z) | [DADO] executado, resultados em `docs/results/blanket_pyphi.md` |
| MIP explicável | `activation_beta/phi_layer.py:phi_meta.update` | `mip_side_a/b`, `mip_top3`, `n_distinct_states`, `diversity` | [DADO] Estágio 1 OW-STU-016 |

### 4.2 O que NÃO está implementado (gaps MPS)

| Gap | Descrição | Documento de referência |
|-----|-----------|------------------------|
| Captura por-passo (temporal) | `_generate()` só captura o último step; trajetória H∈R^{T×L×D} inexistente | [LIMITE] `OW-STU-018 §2.1`, M1-M3 propostos |
| MPS χ trajectory (M1) | Bond dim por camada × passo — requer captura temporal | [LIMITE] `OW-STU-018 §3 M1` |
| Contract drift / entanglement temporal (M3) | Correlação h_t ↔ h_{t+k} e similaridade com vetor do prompt | [LIMITE] `OW-STU-018 §3 M3` |
| Matrizes de atenção completas (M4) | Hoje só entropia escalar última camada; MPO sobre heads inexistente | [LIMITE] `OW-STU-018 §3 M4` |
| Integração MPS→feedback em produção | Nenhum consumidor do `activation_beta/` alimenta o prompt de geração | [LIMITE] `OW-STU-018 §1` |
| Mesh-Φ proxy (grafo causal) | Grafo de acoplamento de daemons + min-cut como Φ-proxy | [LIMITE] `OW-STU-017 §6 Estágio 3` |

---

## 5. PENDÊNCIAS ATIVAS (não concluídas — estado 2026-11-04)

> Fonte primária: `CONTINUITY_MAP.md §2`, `PENDING_ROADMAP.md`.
> Checkboxes do PENDING_ROADMAP **estão atualizadas para P0-P5**.

### 5.1 P0 — Segurança / Governança (residual)

| # | Item | Localização do gap | Prioridade |
|---|------|--------------------|-----------|
| G1 | Juízes fail-open residuais | `agent_orchestrator.py:156,171,191` — brains caídos aprovam True | ALTA |
| G2 | `matrix.py:53` exception→True | `safety/matrix.py:53` | ALTA |
| G3 | `run_audit` stub (passed=True hardcoded, coverage=0.85) | `orchestration/` | ALTA |
| G4 | QuarantineSystem nunca consultado | `orchestration/governance.py` | MÉDIA |
| G5 | Governança in-memory (trust/quarantine/stall) sem persistência | node_db não guarda — recycle = amnésia | MÉDIA |
| G6 | `cascade_reset` sem classificação de motivo | `orchestration/` | BAIXA |

### 5.2 P1 — Supervisor lane afetiva (ABERTO — item central)

| # | Item | Status |
|---|------|--------|
| A1 | `safety/supervisor.py` **não existe** | Ausente — proposto em `CONVERSATIONAL_AFFECT_STUDY §6` |
| A2 | Endpoints `/supervisor/review`, `/soul/affect/conversation` | **Não existem** |
| A3 | `/brain/chat` proxy puro — `with_affect` **nunca chamado** no path real | `brain/server.py:94-103` wired como proxy; `with_affect` só em testes |
| A4 | `agency/teleology.py` — import `integration_loop` é stub/morto | `AUDIT_CLINE.md §1` |
| A5 | `agency/curiosity.py` — zero testes | `CONTINUITY_MAP §2 item 17` |

### 5.3 P2 — Baterias / Estudos (residual)

| # | Item | Status |
|---|------|--------|
| B1 | Re-score canônico dos 108 HF blocks não-cognitivos | `block1_observe/v10/pranchas` (60 records) + `block2_intervene` (48) sem scorer |
| B2 | Réplica local nf4 dos braços `block2_intervene` (12 tasks Gluzdov × 4 braços) | Payloads commitados, run não executado |
| B3 | Hipótese scratchpad N-back (nf4 57-66 vs bf16 91-100) | `OW-STU-006 §7` — teste com deliberação visível não feito |
| B4 | Separação canal `thinking` vs `visible` no erika_torch_server | `OW-STU-006 rec.3` — não implementado |
| B5 | Parser scorer tolerante `Cn`/`Card N` | `OW-STU-006 rec.2` |
| B6 | Writeup/paper (`WRITEUP_ESQUELETO.md`) deadline 2026-11-12 | Depende B1/B2/B3 |

### 5.4 P3 — Dívida técnica / Conformidade

| # | Item | Arquivo : linha |
|---|------|-----------------|
| D1 | `node.db` fora do snapshot root (`/tmp/omni_coworker_orch`) | `CONTINUITY_MAP §2 item 13` |
| D2 | `witness.jsonl` hardcoded `data/witness.jsonl` fora do state root | `store/state_guard.py` |
| D3 | `_manifest_hash` trunca a 1MB/arquivo | `state_guard.py:47` |
| D4 | `_GATE_FAILED` nunca reseta | `safety/gate.py:39-41` |
| D5 | Brain router monta engolindo erro | `app.py:29-32` |
| D6 | Soma probe sem loop periódico (só on-demand) | `app.py:76` |
| D7 | `external_cli_agent.py:52` OPENAI_BASE_URL=:8098 hardcoded | `external_cli_agent.py:52` |
| D8 | `cpu_percent(0.0)` frio na 1ª chamada | `soma/probe.py` |
| D9 | `DIRECTORY_CONTRACT.yaml` desatualizado (40 módulos, falta swap_scheduler/state_guard) | `DIRECTORY_CONTRACT.yaml` |
| D10 | `brain/activations.py` dead code | `CONTINUITY_MAP §2 item 17` |
| D11 | `bus.publish` sem consumer loop (dead letters) | `agents/bus.py` — `OW-AUD-003` |
| D12 | `agents/modes.py` persiste em `/tmp` (efêmero) | `agents/modes.py` |

### 5.5 P4 — MPS / Métricas avançadas (novo — derivado de OW-STU-018)

| # | Item | Esforço |
|---|------|---------|
| M1 | Captura hidden states **por passo** (amostragem esparsa cada 8 tokens) | ALTO — modifica `_generate()` |
| M2 | Bond dim χ trajectory por camada × passo | Depende M1 |
| M3 | Contract drift: cosine(h_t, h_prompt) por camada | Médio — depende M1 |
| M4 | Alinhamento turn-level no harvester | Médio |
| M5 | Consumer em `activation_beta/` que injeta feedback no prompt | Alto — arquitetural |
| M6 | Mesh-Φ proxy (grafo de acoplamento de daemons → min-cut) | Médio — offline script |

---

## 6. STUBS DECLARADOS NO CÓDIGO

> Grep verificado em `src/omni_coworker/**/*.py`.

| Arquivo | Stub / Issue | Tipo |
|---------|-------------|------|
| `safety/matrix.py` | Adapter — fallback standalone se `src.orchestration.PermissionMatrix` ausente | shim |
| `safety/gate.py` | Adapter — fallback se `src.autopoietic.constitutional_gate` ausente; `_GATE_FAILED` nunca reseta (`:39-41`) | shim + bug |
| `agency/analyst.py` | Adapter — guard `OMNI_ANALYST_CONFIG`; sem canônico = fallback vazio | shim |
| `agency/dream.py` | Adapter + ciclo próprio; probe canônico `src.cognitive.dream_weaver` morto removido | shim parcial |
| `brain/server.py` | Proxy httpx puro em `/brain/chat` — `with_affect` nunca chamado | comportamento ausente |
| `brain/activations.py` | Dead code — não wired em nenhum path | dead |
| `agency/teleology.py` | Import `integration_loop` declarado como stub/morto (`AUDIT_CLINE §1`) | stub morto |
| `app.py:29-37` | Monta brain router + supervisor router com `except: pass` (engole erros silenciosamente) | bug silencioso |
| `orchestration/agent_orchestrator.py:156,171,191` | Juízes aprovam `True` quando brain cai | fail-open |
| `store/state_guard.py:47` | `_manifest_hash` trunca a 1MB (snapshots grandes ficam sem hash completo) | limite funcional |
| `safety/supervisor.py` | **Arquivo não existe** — proposto, não implementado | ausente |
| `km/src/stubs/huggingface_hub_stub.py` | Stub HF Hub no soberano (ambiente offline) | shim soberano |

---

## 7. ROADMAP PRIORITIZADO (próximas sessões)

### Imediato (antes do deadline 2026-11-12)

1. **Supervisor lane** (A1-A3): criar `safety/supervisor.py` + endpoints `/supervisor/review` + wire `with_affect` no path real de `/brain/chat` — é o único P2 genuinamente aberto e afeta o writeup.
2. **Re-score 108 blocks HF** (B1): `scripts/gemma4_diag_battery/rescore_hf_blocks.py` estendido para `observe/v10/pranchas/block2_intervene`.
3. **Writeup** (B6): `docs/WRITEUP_ESQUELETO.md` — depende dos resultados B1/B2.
4. **Docs stale** (D9): atualizar `DIRECTORY_CONTRACT.yaml` + `PENDING_ROADMAP.md` checkboxes restantes.

### Médio prazo

5. **Fail-open residual** (G1-G4): corrigir orchestrator + matrix + run_audit.
6. **Snapshot root** (D1-D2): mover `node.db` e `witness.jsonl` para `OMNI_STATE_DIR`.
7. **Captura MPS por-passo** (M1-M3): modificar `_generate()` com amostragem esparsa.

### Longo prazo / pesquisa

8. **Mesh-Φ proxy** (M6): grafo de acoplamento offline → min-cut como [PRX] de integração da malha.
9. **Separação `thinking`/`visible`** (B4): canal de cadeia de pensamento no erika_torch_server.
10. **BionAlphaFunction** do soberano: portar para `psychoanalysis/` (completar o que `__init__.py:21` declara como "todos PORTAR").

---

## 8. MAPA DE ARQUIVOS CRÍTICOS

```
omni_worker/
├── src/omni_coworker/
│   ├── app.py                          ← ponto de entrada ASGI
│   ├── cli.py                          ← omni-coworker CLI
│   ├── server/erika_torch_server.py    ← SERVIDOR LLM REAL (NF4 + MPS)
│   ├── brain/server.py                 ← proxy httpx (STUB: with_affect ausente)
│   ├── brain/activations.py            ← DEAD CODE
│   ├── agency/affect_tracer.py         ← escada L0-L4
│   ├── agency/teleology.py             ← STUB MORTO
│   ├── safety/supervisor.py            ← NÃO EXISTE
│   ├── safety/gate.py                  ← adapter (bug: _GATE_FAILED não reseta)
│   ├── safety/matrix.py                ← adapter (fail-open residual)
│   ├── orchestration/agent_orchestrator.py ← juízes fail-open :156,171,191
│   ├── activation_beta/hidden_spectral.py  ← MPS-lite (bond_dims, eff_rank)
│   ├── kernel_daemon/ignition.py           ← GWT-lite (distinct_prefixes, synergy)
│   ├── psychoanalysis/markov_blanket.py    ← IIT PyPhi real (4-6 nós)
│   ├── integration_loop/loop.py            ← ciclo sensory→narrative (60s)
│   └── store/state_guard.py                ← snapshots tar.gz (bug: trunca 1MB)
│
├── docs/
│   ├── PENDING_ROADMAP.md              ← roadmap com checkboxes (atualizado P5)
│   ├── CONTINUITY_MAP.md               ← estado do projeto (2026-11-02)
│   ├── design/OW-STU-018_mps_capture_study.md  ← análise MPS completa
│   ├── design/OW-STU-017_mesh_integration_map.md ← IIT/GWT na malha
│   ├── design/OW-STU-016_iit_gwt_measurement_audit.md ← auditoria Φ formal
│   └── results/blanket_pyphi.md        ← Φ PyPhi real (blanket 4-6 nós)
│
└── scripts/
    ├── start_omni_worker.sh            ← bring-up completo (restore+deps+brains)
    ├── gemma4_diag_battery/            ← baterias diagnósticas
    └── refactor_battery/               ← bateria de refatoração multi-turno

omnimind-kilombo-sovereign/ [READ-ONLY]
├── src/erika/erika_torch_server.py     ← fonte original do servidor LLM
├── src/kernel/sovereign_daemon/        ← daemon soberano (não gerenciado aqui)
├── src/kernel/sovereign_kuramoto/      ← ritmo basal (não portado)
├── src/llm/watsonx_bounded_client.py   ← LLM soberano (substituído por proxy)
├── scripts/experiments/
│   └── transformer_mps_bridge_pilot.py ← MPS bridge completo (referência)
└── src/stubs/huggingface_hub_stub.py   ← shim offline
```

---

## 9. LEGENDA EPISTÊMICA

| Rótulo | Significado |
|--------|-------------|
| [DADO] | Verificado em arquivo, log, código ou execução real |
| [DERIVADO] | Calculado a partir de dados verificados |
| [INTERPRETAÇÃO] | Análise do agente — não verificado diretamente |
| [LIMITE] | Restrição conhecida, não implementada |
| [CAP] | Capacidade real implementada e testada |
| [PRX] | Proxy — aproximação, não medida direta |
| [TXT] | Marcador textual / topológico, sem causalidade |
| [IIT] | Medida IIT 3.0/4.0 causal real (teto: PyPhi ≤10 nós) |
| [EXP] | Experimental — não em produção |

---

*Gerado por Kiro em 2026-11-04. Atualizar a cada sessão de trabalho.*

---
## §10 Histórico — CONTINUITY_MAP (merged 2026-11-04)

## 7. English summary — what the next session must know

**Live state**: a 5-rep diagnostic battery repopulation
(`run_diag_reps_swapped.sh`, launched 21:59 UTC) is RUNNING — analyst rep0
done (~22:03), then peer-swap → 5 executor reps → dual-residency restore.
Do not kill PID 27872. Executor is currently unloaded by design.

**Truth vs docs**: `PENDING_ROADMAP.md` checkboxes lag reality — P0/P1/P3
are committed and working; the genuinely open P2 item is the affect
supervisor wire (`with_affect` exists but nothing calls it on the request
path; no `/supervisor/*` endpoints; `safety/supervisor.py` unwritten).
Three of four battery ledgers cited in OW-STU-007 are gone
(`supervisor/coding/refactor` sqlite absent); `diag_battery.sqlite` was
wiped and is being repopulated with a new `rep` column.

**Blocks**: the HF E4B-bf16 dataset (124 ledger + 126 gen records) has 5
experiments; only `block1_cognitivo` (16 rows) was canonically re-scored.
108 records (observe/v10 cenas, pranchas, 4-arm SWE block) await
re-scoring + local nf4 replication. Payloads are committed under
`scripts/gemma4_diag_battery/payloads/`.

**Batteries needing more reps**: `coding` (1 rep/case → 3–5),
`refactor` (--n 10–20 for verdict distribution), `diag` (5-rep run in
flight fixes it). `supervisor` is deterministic until an LLM judge tier
exists.

**Operational traps**: swap_scheduler doesn't observe external
unload/reload — its `max_unloaded` clock can fire `/erika/reload`
mid-battery; dual-resident brains + activation capture OOM at high
max_tokens (keep peer-swap flow); `node.db`/`witness.jsonl` outside
snapshot root; orchestrator trust/quarantine in-memory only.

## Addendum 2026-11-02 (session 2 — live findings)

**Resolved traps**: (a) `swap_scheduler` timed-reload now requires
`ratio < evict_at` — commit `f439dbf`; the 30-min clock can no longer
fire `/erika/reload` into a saturated GPU mid-battery. (b) `code_index`
rebuild is automatic on staleness (`--reindex` forces, CPU-only build)
and `_load()` keys its cache on parquet mtime — in-place rebuilds are
picked up live, no API restart.

**Open anomaly — executor residual VRAM**: after `/erika/unload`,
`/health` reports `memory_allocated ≈ 0.01GB` but `nvidia-smi` still
shows the erika_torch_server process holding ~9.0GB (bnb/accelerate
allocator residue or unreleased reserved pool). Effect: the "freed"
VRAM is not actually available to the peer — the analyst phase runs
with ~1GB OS headroom instead of ~10GB. Mitigation shipped
(`vram_reserved_gb` in `/health`, `ipc_collect` + second `empty_cache`
in unload) — verify empirically on next brain restart/reload; if
reservation persists, candidates are `remove_hook_from_submodules`
(accelerate) or allocator `expandable_segments`.

**In flight**: `run_diag_reps_swapped.sh 5` — rep ledger at
`scripts/gemma4_diag_battery/diag_battery.sqlite` (expect 40 rows:
5 reps × 4 tasks × 2 roles). Analyst rep0≈87.7, rep1≈85.2, rep2≈82.5.

**diag battery 5-rep run COMPLETE (40/40 rows)**: peer-swap run with
per-role eviction. Mean±range per task (n=5):

| task | analyst (12B) | executor (E4B) |
|---|---|---|
| wcst | 73.0 (45–90) | 86.8 (70–90) |
| stroop | 97.0 (95–100) | 100.0 |
| nback | 65.7 (flat) | 68.6 (65.7–74.3) |
| igt | 100.0 | 100.0 |

`degenerate=0` on all 40 rows — consistent with OW-STU-006: local NF4
runs show no lexical degeneration even at 1800 tokens. Per-rep spread
is driven by WCST variance on the analyst (77.7–87.7 rep means);
executor is nearly deterministic (86.1–88.9). Garbage 503 rows from
the failed mid-run reload were deleted (latency<1s, all-zero) — real
executor rows were re-run with the allocator fix.

**Residual VRAM root cause SOLVED**: `expandable_segments` (torch 2.9+
VMM allocator default) pinned whole segments while any interior block
survived — `empty_cache()` could not unmap them, so unload freed
`memory_allocated` but not driver memory, and `device_map="auto"`
reload then saw ~1GB free → bnb dispatch ValueError. Fix shipped:
`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:False` set by the brain
