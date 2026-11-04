<!-- doc_id: OW-AUD-CURSOR-MPS-MESH-20261104 | title: Auditoria malha estrutural MPS + dual-brain + API | author: cursor-agent | date: 2026-11-04 | status: verified-empiric -->

# AUDIT — Malha estrutural MPS / dual-brain / API (`2026-11-04`)

**Escopo:** `/content/omni_worker` — bancos `data/*.sqlite` + `scripts/*/*.sqlite`,
`data/monitor/`, endpoints vivos `:8081` / `:8098` / `:8099`, código da malha
MPS (`hidden_spectral`, sidecars, `erika_torch_server`).

**Estatuto:** afirmações marcadas **[DADO]** (medido nesta sessão),
**[DERIVADO]** (cálculo/inferência a partir de dados), **[LIMITE]**
(restrição conhecida / ausência). Proibido simular evidência.

**Âncora documental pedida:** `docs/STATUS.md` — **[LIMITE]** arquivo
**NÃO LOCALIZADO** no repo (`find` + `git ls-files '*STATUS*'` vazios).
Alinhamento feito contra substitutos vivos: `docs/PENDING_ROADMAP.md`
(Estágio 2 MPS marcado `[x]`), `docs/design/OW-STU-018_mps_capture_study.md`,
`docs/ops/OW-OPS-001_env_vars_production.md`, `docs/results/mps_spectral_first.md`,
`docs/CONTINUITY_MAP.md` (parcialmente stale — 2026-11-02).

**Instante da apuração:** `2026-11-04T00:24:03.697109+00:00` UTC.

---

## 0. Resumo executivo

A malha de **leitura espectral/MPS offline** (`activation_vectors` →
`hidden_spectral.spectral_features` → `kernel.phi_layer.spectral`) está
**viva e populada**. A malha de **captura temporal** exigida por OW-STU-018
M1–M3 (`activation_steps` / `step_traj`, `prompt_hidden`) está **desligada
no runtime atual** (env unset + `capture.env` ausente) e os artefatos
`activation_steps` estão **congelados desde ~2026-11-03T20:25Z**. Brains e
API respondem HTTP 200, mas o kernel reporta `producing=false`,
`models={}`, `drift={}`, glial_gate `allow_generation=false` (vagus saturado)
e o dodeca deixa 9/15 casas `null`. Witness parado desde ~2026-11-03T02:49Z.

---

## 1. Processos e bind vivos — [DADO]

| PID | Comando | Bind | Papel |
|---|---|---|---|
| 67018 | `python3 -m omni_coworker.server.erika_torch_server --model google/gemma-4-12B-it --load-4bit --eager-attn --port 8098` | `127.0.0.1:8098` | Analyst |
| 67554 | idem `--model google/gemma-4-E4B-it --port 8099` | `127.0.0.1:8099` | Executor |
| 67829 | `python3 -m omni_coworker.cli serve --port 8081` | `0.0.0.0:8081` | API |
| 67897 | `python3 -m omni_coworker.store.state_guard` | — | snapshots |
| 67899 | `python3 -m omni_coworker.orchestration.swap_scheduler` | — | VRAM swap |
| 67901 | `archive_worker_state.sh --loop 3600` | — | arquivo |

**[LIMITE]** `OMNI_GATE_FAIL_CLOSED` **UNSET** nos cinco PIDs acima — OW-OPS-001
exige `1` em produção pública; API escuta `0.0.0.0` (não loopback).

### 1.1 Variáveis MPS nos processos — [DADO]

Nos PIDs 67018/67554/67829 (lidos de `/proc/<pid>/environ`):

| Var | Valor runtime | Default código | Efeito |
|---|---|---|---|
| `OMNI_ACT_STEP_EVERY` | **UNSET** | `"0"` | **step_traj OFF** |
| `OMNI_ACT_STEP_ON` | UNSET | `"1"` | irrelevante sem EVERY>0 |
| `OMNI_ACT_PROMPT_HIDDEN` | **UNSET** | `"0"` | **prompt_hidden OFF** |
| `OMNI_ACT_VEC_SIDECAR` | UNSET | on (`!=0`) | vectors ON (default) |
| `OMNI_ACT_VEC_KEEP` | UNSET | 64 | cap 64/modelo |
| `OMNI_ACT_RUN_ID` / `TURN` / `TASK` | UNSET | `""` | metadata vazia |
| `OMNI_MAX_ATTN_TOKENS` | UNSET | 900 | attn off se prompt>900 |
| `data/monitor/capture.env` | **ausente** | lido por `_capture_cfg` | sem override hot |

Presentes e úteis: `OMNI_STATE_DIR`, `OMNI_MEMTRIAS_AUTO_LOG=1`,
`OMNI_ACERVO_DIR`, `OMNI_SOMA_INJECT=1`, `OMNI_RESTORE_CO_RESIDENT=1`.

---

## 2. Endpoints vivos — [DADO]

Todos os 10 pedidos do enunciado + 2 extras `/erika/activations` → **HTTP 200**.

### 2.1 Brains

| Endpoint | Achado |
|---|---|
| `:8098/health` | `status=ok`, `model=google/gemma-4-12B-it`, `model_loaded=true`, `cuda=true`, `vram_gb=7.69`, `activations_buffered=6` |
| `:8099/health` | `ok`, `gemma-4-E4B-it`, loaded, `vram_gb=9.31`, `activations_buffered=1` |
| `:8098/erika/affect` | `n_activations=6`, `attention_entropy_mean=2.367`, `hidden_norm_mean=142.4219`, `last_ts=2026-11-04T00:02:06Z` |
| `:8099/erika/affect` | `n_activations=1`, **`attention_entropy_mean=null`**, `hidden_norm_mean=129.4491`, `last_ts=2026-11-03T23:58:54Z` |

**[DERIVADO]** Executor com buffer=1 e entropy null: última geração provavelmente
com `prompt_tokens > OMNI_MAX_ATTN_TOKENS(900)` ou attentions omitidos; analyst
recente também mostra tails jsonl com `H=None` e `P∈{922,2529,2778}`.

### 2.2 API `:8081`

| Endpoint | Achados zerados / NULL / off |
|---|---|
| `/soul/state` | `kernel=false`; dodeca **`n_computable=6/15`**; casas **NULL**: S05 aleph, S06 lambda, S08 gamma, S09 zeta, S11 rekh, S12 seshet, S13 isfet, S14 aleph_resonance, S15 axe (`source=unavailable_standalone`) |
| `/loop/status` | ciclos vivos (`cycles≈26` no snapshot, sqlite 1460); `meaning_maker.embedding=null`; `expectation.embedding=null`; `sensory_feedback.embedding=null`; `sensory_input.metadata.models=[]`; `bion.degraded=true`, `tier=heuristic`; GPU util 0 no sensory |
| `/loop/modulation` | populado (phi/psi/sigma/epsilon, `recommendation=analyst`, `prompt_suffix=[regime:reflect]`) — **não zerado** |
| `/kernel/daemon` | `producing=false`; **`models={}`**; **`drift={}`**; `soul.dominant_token=null`; homeostasis `producing=false`, `disk_percent=0.0` (métrica suspeita vs soul disk 45.1%); `workspace.coherence_t=null`; glial **ambos modelos** `allow_generation=false` reason `vagus_sedative>=0.5` (vagus=1.0, sensitized=1.0); phi_layer.spectral **populada** |
| `/agency/dunker` | `lexico_total=0`, `lexico_ativos=0`, `lexico_dominante=null`; Soler 12 afetos com **score=0 / active=false** todos |
| `/agency/witness` | cadeia curta (~test/orchestrator); **último evento ~2026-11-03T02:49Z** — testemunha **parada** há ~21h |

### 2.3 Espectral no kernel (= consumo de `hidden_spectral`) — [DADO]

De `/kernel/daemon` → `phi_layer.*.spectral` (e recompute local `spectral_features()`):

| Modelo | eff_rank_mean | bond_dim_max_mean (χ) | ipr_dim_mean | n_files |
|---|---|---|---|---|
| E4B | 2.369 | 40.0 | 44.21 (1.73%) | 8 |
| 12B | 1.633 | 59.71 | 102.05 (2.66%) | 8 |

Nota do próprio módulo: *"proxy espectral/MPS — não é Φ causal IIT"* — **[LIMITE]** estatuto [PRX].

---

## 3. `data/monitor/` — artefatos MPS — [DADO]

### 3.1 Inventário de paths

| Path pedido / esperado | Estado |
|---|---|
| `erika_torch_activations.jsonl` | **591 linhas**, 1.89 MB; offset = filesize (consumer em dia) |
| `activation_vectors/` | **128** `.npz` (64×12B + 64×E4B), ~30.7 MB, mtime até `2026-11-04T00:02:06Z` |
| `step_traj/` | **NÃO EXISTE** |
| `activation_steps/` (nome real no código) | **76** `.npz` (~1.28 GB), mtime **último `2026-11-03T20:25:53Z`** (~4h sem escrita) |
| `prompt_hidden/` | **NÃO EXISTE** |
| `capture.env` | **NÃO EXISTE** |
| `integration_loop_cycles.jsonl` | 1457+ linhas, alinhado ao sqlite |

**[DERIVADO]** O enunciado usa `step_traj/`; o código grava em
`data/monitor/activation_steps/` e anota `record["step_traj"]` no jsonl
somente quando a captura dispara. Hoje **0/591** linhas jsonl contêm
`step_traj` ou `prompt_hidden_file`.

### 3.2 Qualidade dos sidecars

**activation_vectors (amostra + varredura):**
- Shape 12B: `(49, 3840)` fp16; E4B: `(43, 2560)` fp16.
- **0/128 all-zero**, **0/128 NaN**; abs_mean ~0.67–0.90 — vetores vivos.
- Meta `run_id`/`turn`/`task`: **55/128 com `run_id==""`** (sidecars novos sem provenance); arquivos antigos pré-meta sem essas keys.
- Retenção `_VEC_KEEP=64` por modelo → cap cheio (bate com `mps_spectral_first.md`).

**activation_steps (amostra):**
- Ex.: `(420, 43, 2560)` E4B com `run_id=app_deliv_…`, `task=app_code` — **não zerado**.
- `n_tokens` min/med/max = 15 / 178 / 800.
- Escrita **parou** quando baterias que setavam `capture.env`
  (`coding_battery` escreve `OMNI_ACT_STEP_EVERY=8`) terminaram; runtime
  atual não recria o arquivo.

**jsonl activations:**
- Modelos: E4B 316 + 12B 275.
- `attention_entropy_last` null: 5 (12B) + 1 (E4B) no histórico; **tails recentes 12B todos null** (prompts longos).
- `empty_meta` (run_id e task vazios): **519/591**.
- `prompt_tokens > 900`: **101/591** → attn cortada por default.

---

## 4. Bancos SQLite — [DADO]

`sqlite3` CLI ausente; apuração via `python3 + sqlite3` stdlib.

### 4.1 `data/*.sqlite` (5)

| DB | size | tabela | rows | Colunas NULL / 0 / vazias relevantes |
|---|---|---|---|---|
| `integration_loop.sqlite` | 6.7 MB | `cycles(ts,cycle_id,status,payload_json)` | **1460** | sem coluna fully-nullish |
| `memtrias.sqlite` | 4.8 MB | `memories` (14 cols) | **455** | **`chat_id` ALL NULL (455)**; **`forgotten` ALL 0 (455)**; `state_ref` NULL 444/455; `instance` NULL 108/455; `doc_ref` NULL 8/455 |
| `shared_workspace.sqlite` | 18.2 MB | `events(ts,topic,payload_json,provenance_json)` | **~17878** | **`provenance_json` NULL 9421 (~53%)** |
| `scars.sqlite` | 12 KB | `scars` (7 cols) | **9** | sem fully-nullish |
| `somatic_probes.sqlite` | 12 KB | `probes` (8 cols) | **3** | **`swap_gb` ALL 0**; `cpu` zero em 2/3 — store **subutilizado** vs loop contínuo |

Namespaces memtrias (COUNT): document/instance/machine/… presentes (reidratação P5 do roadmap confirmada em volume).

### 4.2 `scripts/*/*.sqlite` (5)

| DB | tabela | rows | Gaps |
|---|---|---|---|
| `coding_battery/coding_battery.sqlite` | `coding_battery` | 50 | `recall` NULL 23/50; `hallucinated` NULL 20; `fix_compiles`/`fix_black` zero 30/50 (histório misto ablação+sucesso) |
| `corpus_reading_battery/corpus_delivery_battery.sqlite` | `corpus_reading_runs` | 10 | **`layer_mps_metrics_json` NULL 5/10**; anomaly/tabular majoritariamente 0 |
|  | `app_delivery_runs` | 7 | `layer_mps_metrics_json` NULL 1/7; `task_routing_plan_json` NULL 1/7 |
|  | `dream_self_curriculum` | 6 | ok |
| `gemma4_diag_battery/diag_battery.sqlite` | `diag_battery` | 88 | `degenerate` zero 75/88 (esperado se detector limpo) |
| `refactor_battery/battery_results.sqlite` | `battery_runs` | 13 | **`submitted` ALL 0**; smoke_passed/failed zero 12/13; `turns_json` NULL 1 |
| `supervisor_battery/supervisor_battery.sqlite` | `supervisor_battery` | 16 | **`passion_flag`/`angst_score`/`chaos_score` ALL 0**; `judge_intent`/`judge_recommend` NULL 13/16; `tracer_level`/`posture` NULL 8/16 |

**[DERIVADO]** Ledgers de bateria existem (gap P4 do CONTINUITY_MAP antigo
já fechado em volume), mas colunas de afeto “clássico” do supervisor
permanecem **estruturalmente zeradas** (detecção migrou para
tracer/judge — campos legados mortos).

---

## 5. Mapa causal da malha MPS (código) — [DADO]+[DERIVADO]

```
erika_torch_server._generate
  ├─ output_hidden_states=True  (sempre)
  ├─ output_attentions se prompt_tokens ≤ OMNI_MAX_ATTN_TOKENS (900)
  ├─ _emit_activation → jsonl + ring buffer → /erika/affect|/activations
  ├─ _emit_vectors → activation_vectors/*.npz   [ON por default]
  ├─ _emit_step_trajectory → activation_steps/*.npz
  │     gate: OMNI_ACT_STEP_EVERY>0  [OFF agora]
  └─ prompt_hidden branch → prompt_hidden/*.npz
        gate: OMNI_ACT_PROMPT_HIDDEN==1  [OFF agora]
              + dead code `if False else` no path dir (L384)

activation_vectors ──► hidden_spectral.spectral_features()
                   ──► phi_layer (kernel bundle)
                   ──► dashboard_export / corpus battery

activation_steps ──► (consumidor fraco: dashboard_export; M1–M3 OW-STU-018
                      ainda sem pipeline contínuo no kernel)
prompt_hidden ──► necessário para M3 contract-drift (OW-STU-018 §3)
                  [canal ausente]
```

**[LIMITE]** `PENDING_ROADMAP` marca Estágio 2 MPS como `[x]` (código +
export existem). Runtime atual **não mantém** a captura temporal ligada —
checkbox de implementação ≠ malha continuamente alimentada.

---

## 6. Inventário do que está zerado / NULL / desligado / subutilizado

### 6.1 Desligado (feature gate)

1. **`OMNI_ACT_STEP_EVERY=0` (default) + unset** → sem novos `activation_steps` / `step_traj`.
2. **`OMNI_ACT_PROMPT_HIDDEN` default 0** → diretório `prompt_hidden/` inexistente.
3. **`capture.env` ausente** → sem hot-reload de run_id/turn/task/STEP_EVERY.
4. **`OMNI_GATE_FAIL_CLOSED` unset** + bind API `0.0.0.0` → fora do contrato OW-OPS-001 public.

### 6.2 Zerado / NULL em runtime vivo

5. Kernel `producing=false`, `models={}`, `drift={}`, `dominant_token=null`.
6. Glial gate **ambos** brains: `allow_generation=false`, `vagus_sedative=1.0` (janela acumulada — padrão já diagnosticado em OW-STU-013).
7. Dodeca 9 casas NULL (`unavailable_standalone`) — daemon dodecatiad canônico não acoplado.
8. Dunker: léxico affect_engine vazio; Soler scores todos 0.
9. Loop: embeddings null em meaning_maker / expectation / sensory_feedback; `models=[]` no sensory; bion `degraded=true`.
10. Witness sem append desde ~02:49Z (orquestrador ocioso).
11. `:8099` affect entropy null; tails 12B entropy null (prompts longos).
12. GPU util 0% com 18.3 GB VRAM residente — brains carregados, **não produzindo**.

### 6.3 Subutilizado em persistência

13. `somatic_probes.sqlite` com **3** linhas vs milhares de ciclos do loop.
14. `memtrias.chat_id` 100% NULL; `state_ref` ~97% NULL; `forgotten` sempre 0.
15. `shared_workspace.provenance_json` ~53% NULL.
16. Supervisor ledger: colunas passion/angst/chaos sempre 0 (legado).
17. Corpus `layer_mps_metrics_json` null em 50% das leituras.
18. Refactor `submitted=0` em 13/13 (gate/verdict broken_patch histórico).

### 6.4 Nomeação / docs

19. **`docs/STATUS.md` ausente** — auditorias e agentes não têm âncora única.
20. Path `step_traj/` vs `activation_steps/` — divergência enunciado/docs/código.

---

## 7. Correções arquiteturais propostas (alinhadas ao roadmap / OW-STU-018)

Prioridade P0–P2; cada item amarra evidência → ação → critério de aceite.

### P0 — Religar a malha de captura temporal (OW-STU-018 §4, PENDING Estágio 2)

1. **Bootstrap de captura no `start_omni_worker.sh` / unit env**  
   - Criar `data/monitor/capture.env` canônico:
     ```
     OMNI_ACT_STEP_EVERY=8
     OMNI_ACT_STEP_ON=1
     OMNI_ACT_STEP_KEEP=32
     OMNI_ACT_PROMPT_HIDDEN=1
     OMNI_ACT_VEC_SIDECAR=1
     OMNI_ACT_VEC_KEEP=64
     ```
   - Exportar as mesmas vars no ambiente dos PIDs erika **antes** do start
     ( `_capture_cfg` lê arquivo a cada call — arquivo sozinho já reativa
     STEP/PROMPT sem restart; vars de processo cobrem defaults de módulo).
   - **Aceite:** após 1 geração em cada brain, existem arquivos novos em
     `activation_steps/` e `prompt_hidden/`; jsonl contém `step_traj` e
     `prompt_hidden_file`.

2. **Provenance obrigatória**  
   - Harnesses (orchestrator, batteries) devem sempre escrever
     `OMNI_ACT_RUN_ID`/`TURN`/`TASK` em `capture.env` (padrão já usado por
     `coding_battery`).  
   - **Aceite:** <5% sidecars novos com `run_id==""`.

3. **Atenção em prompts longos**  
   - Ou elevar `OMNI_MAX_ATTN_TOKENS` com amostragem (últimas N tokens),
     ou gravar `attention_entropy_last=null` + flag `attn_skipped_reason`
     explícito no jsonl (hoje some silenciosamente).  
   - **Aceite:** affect `:8098`/`:8099` nunca “null sem razão” no schema.

### P1 — Consumo contínuo MPS no kernel (não só sidecar morto)

4. **Estender `phi_layer` / collector** para ler `activation_steps` recentes
   e publicar `spectral_temporal` (eff_rank ao longo de t, χ(t) amostrado)
   no bundle `/kernel/daemon` — fecha o gap OW-STU-018 §1
   (“nada ainda consome ativações para MPS por geração” parcialmente
   aberto no eixo temporal).  
   - **Aceite:** campo novo não-null quando `activation_steps` mtime < 10 min.

5. **M3 contract-drift** usando `prompt_hidden` + traj  
   - Similaridade coseno `h_prompt` vs `h_t` por camada; alerta se queda
     precoce. Alimenta judge/coverage (complementar, não substituto).  
   - **Aceite:** métrica em `docs/results/` + coluna opcional no ledger
     refactor/coding.

6. **Glial gate em idle**  
   - Reaplicar correção OW-STU-013: janela deslizante + não contar idle
     como stress; ou `allow_generation` só consultado quando
     `producing=true` / request real. Hoje vagus=1.0 com GPU util 0.  
   - **Aceite:** em idle, `/kernel/daemon` reporta `allow_generation=true`
     **ou** reason distinta `idle_not_applicable`; sob carga real, calibração
     da janela 20–40 conforme estudo.

### P2 — Fechar superfícies NULL da malha / governança

7. **Criar `docs/STATUS.md`** como âncora operacional (substitui CONTINUITY
   stale): brains, env MPS, contagens monitor, último mtime steps/vectors,
   glial, producing. Atualizado pelo `archive_worker_state` ou cron.  
8. **Witness heartbeat** a cada ciclo do kernel (`kernel.cycle` → witness)
   para não deixar a cadeia congelada 21h.  
9. **Persistir probes**: `/soma/probe` → `probe_recorded` em produção
   (gap antigo AUDIT_KILO) — sai de 3 linhas.  
10. **Dunker/léxico**: ou alimentar `affect_engine` a partir de
    `/erika/affect`+modulation, ou marcar endpoint como
    `status=unwired_standalone` (honestidade dodeca).  
11. **API bind**: produção → `127.0.0.1` + `OMNI_GATE_FAIL_CLOSED=1`
    (OW-OPS-001).  
12. **Limpar dead code** `d = _step_dir() if False else ...` (L384) e
    documentar alias `step_traj ≡ activation_steps` no DOCS_INDEX.  
13. **Memtrias**: popular `chat_id`/`state_ref` no auto-log ou dropar
    colunas do contrato se definitivamente fora de escopo.  
14. **Supervisor ledger**: deprecar passion/angst/chaos ou preenchê-los
    a partir do tracer (evitar ALL_ZERO eterno).

### P3 — Disco / retenção

15. `activation_steps` já ~1.28 GB com KEEP implícito inconsistente
    (76 arquivos > `_STEP_KEEP=32` por modelo) — reforçar poda por modelo
    no emit e no start script.  
16. Separar arquivo “battery capture” vs “daemon capture” para não misturar
    provenance vazia com runs instrumentados.

---

## 8. Matriz de conformidade vs docs âncora

| Requisito | Fonte | Estado 2026-11-04 |
|---|---|---|
| Captura step trajectory implementada | PENDING Estágio 2, OW-STU-018 | Código **SIM**; runtime **OFF** |
| `hidden_spectral` + export | idem | **SIM**, consumido no kernel |
| Sidecar vectors | OW-STU-018 §2.1 | **SIM**, 128 vivos |
| prompt_hidden / M3 | OW-STU-018 §3 M3 | **AUSENTE** |
| Env produção gate+loopback | OW-OPS-001 | **NÃO** (unset + 0.0.0.0) |
| `docs/STATUS.md` | pedido auditoria | **NÃO LOCALIZADO** |
| Dual-brain co-resident | AGENTS.md / roadmap | **SIM** (ambos loaded) |
| MPS como Φ IIT | OW-MATH-001 / spectral note | Corretamente **[PRX]** — não promover |

---

## 9. Metodologia e limites

- Fontes: filesystem `stat`/`np.load`, HTTP curl/urllib, `/proc/*/environ`,
  `spectral_features()`, SQLite via Python, leitura de
  `erika_torch_server.py` L146–396.
- **Não** foram reiniciados serviços nem alterado estado (somente leitura).
- Contagens de ciclo/eventos podem ter incrementado durante a apuração
  (sqlite cycles 1458→1460) — deltas pequenos registrados como ≈.
- `docs/CONTINUITY_MAP.md` descreve estado de 2026-11-02 (executor unloaded
  etc.) **não** refletindo o runtime atual — não usado como verdade viva.

---

## 10. Veredito

A malha **estática/espectral** (vectors → hidden_spectral → phi_layer) está
operacional. A malha **dinâmica MPS** (step traj + prompt_hidden +
consumo temporal no kernel) está **implementada mas desenergizada** por
defaults de env e ausência de `capture.env`, com sidecars step **stale** e
canal prompt **inexistente**. Brains/API saudáveis em HTTP, porém em
**repouso produtivo** (`producing=false`, GPU util 0, glial saturado,
witness morto, dodeca/dunker parcialmente vazios). Correção prioritária:
religar captura temporal no bootstrap + provenance + glial-idle + STATUS.md.
