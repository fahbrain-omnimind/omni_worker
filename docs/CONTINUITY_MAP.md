<!-- doc_id: OW-OPS-004 | title: Continuity Map — omni_worker (2026-11-02) | author: devin | requester: artifice-operator | project: omni-agent-coworker (kaggle) | date: 2026-11-02 | status: active -->

# Continuity Map — omni_worker (2026-11-02 ~22:05 UTC)

pt-BR: Mapa de continuidade do estado do projeto para a próxima sessão:
o que cada commit fez, o que está pendente, o estado real dos ledgers de
bateria, o status da leitura dos "blocks" (dataset HF), trabalho em voo e
docs que ficaram desatualizadas. Toda afirmação verificada contra
`git log`, `git status`, os sqlite em disco e os serviços vivos.
English: continuity snapshot driving the next session — commit→workstream
map, consolidated pendencies, real benchmark-ledger state, the HF
"blocks" run status, in-flight work, stale docs. All claims verified
against git, on-disk sqlite ledgers and the live services. English
summary in §7.

> **Estado vivo no momento desta escrita**: a bateria diagnóstica de
> repopulação (`run_diag_reps_swapped.sh 5`, lançada 21:59 via nohup,
> PID 27872) está **rodando** — rep0 do analyst completo às 22:03
> (wcst 90 / stroop 95 / nback 65.7 / igt 100). Executor :8099 está
> descarregado (`model_loaded:false`) por despejo externo. Não interromper.

---

## 1. Commits → workstreams (45 commits, todos em 2026-11-02)

`git log --oneline` completo agrupado por linha de trabalho:

| Workstream | Commits | O que entregou |
|---|---|---|
| Bootstrap/pacote | `e710dcb` `0b5756a` `8865afe` `feffe8b` | init do pacote `omni-agent-coworker`; gitignore de segredos + `guard_sanitize.py`; `[kernel]` extra c/ pandas+pyarrow; `build_kernel.sh` + adapters kernel/dunker |
| Superfície de agentes | `15425a4` `3909282` `6658bc7` | modos/personas estilo Roo (`agents/modes.py`); `external_cli_agent.py` (ACP JSON-RPC + ShellCLIAdapter, 779ln); fallback ACP→shell |
| Soma/soul/brain | `eebc2e6` | telemetria GPU/VM real (pynvml+nvidia-smi), `_soma_inject` no `brain_chat`, dodeca S01–S15, adapter dunker/soler |
| Segurança P0 | `d3ee101` `418ed68` `ff4d24b` `dbecc21` `3ee0e77` `ddf57d6` | gate fail-closed (`OMNI_GATE_FAIL_CLOSED`); loop→TrustSystem+EventBus+witness; `safety/jail.py` real em camadas; pipe_exec `|sh/b`; epsilon float no TrustSystem; fix audit: code_index guard+cache-dir, affect dessaturado, TrustSystem singleton |
| Persistência P1 | `4d48c3b` `e72927f` `ce9c804` `ec0f847` | `/soma/probe`→`probe_recorded()` + `/agency/witness`; `state_guard` (snapshots tar.gz, retenção 3); dual-write witness→node_db; `audit_adapter` (ponte `ImmutableAuditSystem` canônico) |
| Cuidado clínico | `1647668` | `safety/care.py` territorial Brasil (CVV/CAPS/SAMU/Disque-100) + `with_affect` no `brain_chat` + `docs/care/BRAZIL_SUPPORT_N_NE_CO.md` |
| Afeto conversacional P2/P4 | `de3bfb6` `c8ede34` `8623c6d` `2ad0d0d` | `agency/affect_tracer.py` (escada L0–L4, 6 famílias afex) + `soul/static/superapp.html`; detecção contextual de bajulação; âncoras de fixação (12/12); guiltcut composicional + separation PANIC (`docs/care/AFFECT_SIGNALS_*.md`) |
| Swap P3 | `781addf` `9fabc4d` `ef60ce9` | `orchestration/swap_scheduler.py` (evict/reload por VRAM); **port do `erika_torch_server` real** para o pacote (`--eager-attn`, `/erika/unload|reload`, `model_loaded`) + `scripts/start_omni_worker.sh`; busy-detection por delta de `activations_buffered` |
| Baterias | `61389cb` `41aeee1` `84c7f34` `a800102` `7366607` `2e99756` `e641734` | supervisor_battery (16 transcripts adversariais); refactor_battery E2E (victim→Debug→Code→Review→smoke→gate, trust 0.5→0.8); coding_battery (10 casos, 3 tiers); gemma4_diag_battery (4 tasks canônicas); payloads v10/v11 + Gluzdov commitados |
| Docs/auditoria | `acc80d7` `1fdfc28` `186acb3` `78e96a2` `11c83ca` `572bd96` | 12 READMEs por subpasta + KAGGLE_SETUP_VALIDATION; rewrite bilíngue + OW-OPS-003; trinca OW-AUD-001/002/003; OW-STU-005; OW-STU-007 + `check_worker.py`; GitHub Pages scaffold (`docs/index.md` + workflow) |
| CI | `cba7251` `6c77196` `3055b4a` `d4b2798` `cf2ce70` `2ab2386` | gitlab-ci + github workflow (lint+test); exclude victim fixtures + black/ruff no test env; untrack `out/`+sqlite+runtime artifacts |

HEAD = `ef60ce9`. Working tree sujo (§5).

---

## 2. Pendências consolidadas (com fonte e prioridade)

**ATENÇÃO**: `docs/PENDING_ROADMAP.md` está com checkboxes **desatualizadas** —
P0/P1/P3 já foram implementados nos commits da §1 mas continuam `[ ]`.
Os itens abaixo refletem o que falta *de verdade*.

### P0 — imediato (estado/verdade do repo)

1. **Guardar/verificar o run em voo** — `run_diag_reps_swapped.sh 5` deve
   produzir 40 linhas (5 reps × 4 tasks × 2 roles). Ao final: conferir
   ledger completo, restaurar residência dupla (script já faz), commitar
   `run_diag_battery.py` (`--reps`+coluna `rep`), `start_omni_worker.sh`
   (`--reindex`) e `run_diag_reps_swapped.sh`. *Ledger parcial em
   `scripts/gemma4_diag_battery/diag_battery.sqlite`.*
2. **Ledgers perdidos** — `supervisor_battery.sqlite` (16 linhas),
   `coding_battery.sqlite` (10), `battery_results.sqlite` (8) citados em
   OW-STU-007 §1 **não existem mais**; `diag_battery.sqlite` foi zerado e
   está sendo repovoado agora. Decidir: re-rodar para re-evidenciar
   (supervisor é hermético/rápido; coding/refactor queimam GPU ~min) ou
   aceitar regeneração sob demanda.
3. **Docs stale** — atualizar PENDING_ROADMAP (marcar P0/P1/P3 feitos),
   `docs/index.md` (falta OW-STU-007), KAGGLE_SETUP_VALIDATION (ver §6),
   DIRECTORY_CONTRACT (ver §6). Sem isso toda auditoria futura relê gaps já
   fechados.

### P1 — feature work real restante

4. **Supervisor lane / wire afetivo** (roadmap P2 — único item P2 aberto):
   `affect_tracer` existe e `brain_chat(with_affect=True)` devolve
   `{text, affect_level, affect_reasons}` (`agents/_llm.py:47-86`), mas
   **nada no caminho de request o chama** — `/brain/chat` é proxy puro
   (`brain/server.py:94-103`), `with_affect` só aparece em testes.
   Falta: escada L0–L4 real + lane juiz-analista (`safety/supervisor.py`
   proposto em `docs/CONVERSATIONAL_AFFECT_STUDY.md` §6; endpoints
   `/supervisor/review`, `/soul/affect/conversation` ainda inexistentes —
   OW-OPS-003 §2).
5. **Re-score canônico dos blocks restantes do dataset HF** (OW-STU-006
   rec.1): só `block1_cognitivo` (16 rows) foi re-scored. Restam
   `block1_observe` (20), `block1_v10` (20), `block1_pranchas` (20),
   `block2_intervene` (48) = **108 generation_records** sem scorer
   canônico. Dataset em `/root/.cache/huggingface/hub/datasets--
   fabricioslv--gemma4-e4b-colab-l4-results/snapshots/f55f069…/
   gemma4_e4b_l4_results.sqlite`.
6. **Teleologia viva** (roadmap P2): probe canônico morto em
   `agency/teleology.py` (`AUDIT_CLINE.md` §1 — `integration_loop` import
   é stub) + `dream.metabolize` (probe `listen_to_bus` não verificado
   contra o `DreamWeaver` canônico). Implementar metabolize real ou
   documentar como heurística.
7. **Fail-open residual** (OW-AUD-003 §1.4-5/R1): juízes ainda aprovam
   `True` quando brains caem (`agent_orchestrator.py:156,171,191`),
   `matrix.py:53` exception→`True`, `run_audit` stub (passed=True,
   coverage=0.85 hardcoded), `cascade_reset` sem classificação de motivo,
   `QuarantineSystem` nunca consultado, governança in-memory sem
   persistência (R2 — recycle = amnésia; node.db não guarda
   trust/quarantine/stall).

### P2 — baterias/estudos

8. **Rep local dos blocks HF** (OW-STU-004 §3): `block2_intervene` — 12
   tasks Gluzdov (payloads commitados) × 4 braços nos brains nf4;
   `block1_pranchas` como bateria open-ended; canary como smoke CI-live.
9. **refactor_battery multi-eixo** (OW-AUD-001 §5): multi-arquivo
   (3–8 arquivos), multi-linguagem (JS/TS/shell), multi-turn, transcripts
   adversariais (injeção em comentário, sedução "skip the gate", crise
   pt-BR→CVV, U18); schema do ledger estendido (battery_id, lang, n_files,
   adversarial_class, gate_bypass_attempts, witness_hash); `--seed`.
10. **Hipótese scratchpad N-back** (OW-STU-006 §7): bf16(HF) 91–100 vs
    nf4(local) 57–66 — testar exigindo scratchpad/deliberação visível no
    nf4. Relacionado: separação de canal `thinking` vs `visible` no
    servidor (rec.3).
11. **Robustez de scorer/executor** (OW-STU-006 rec.2, OW-STU-007 P5):
    parser tolerar notação `Cn`/`Card N`; gates do executor medem
    bem-formação, não corretude — adicionar diff-minimality + testes de
    comportamento (over-fix de c04 passou); logar *classes* de FP do
    analista, não só contagem (P4).
12. **Supervisor battery juiz-analista** (roadmap P4): transcripts
    bajulação/fixação hoje passam só pelo tier léxico — fechar gap do
    tier analista-12B (CONVERSATIONAL_AFFECT_STUDY §7 métricas).

### P3 — conformidade/dívida técnica (OW-OPS-003 §3, exceto #2 já feito)

13. Snapshots não cobrem `node.db` (`OMNI_ORCHESTRATOR_DIR` default
    `/tmp/omni_coworker_orch` fora de `OMNI_STATE_DIR`); witness hardcoded
    `data/witness.jsonl` fora do state root (#1/#3).
14. `_manifest_hash` trunca a 1MB/arquivo (`state_guard.py:47`); gate
    `_GATE_FAILED` nunca reseta (`gate.py:39-41`); mount do brain router
    engole erro (`app.py:29-32`); sonda soma só on-demand — sem loop
    periódico (#4–#7).
15. `external_cli_agent.py:52` `OPENAI_BASE_URL=:8098` hardcoded (sem rota
    executor, sem retry/breaker — OW-AUD-003 §1.4-9); `cpu_percent(0.0)`
    frio na 1ª chamada (#9/#10); menores: `--host`, `N_SNAPSHOTS`,
    `agents/modes.py` persiste em `/tmp`.
16. **swap_scheduler ↔ estado externo dessincroniza** (novo — observado
    agora): o scheduler só conhece evicts que ele mesmo fez; descarga
    externa (script da bateria) faz o tick seguinte "aprender" o estado e
    iniciar o relógio `max_unloaded` (30min) → pode disparar
    `/erika/reload` no meio de uma fase analyst. Registrar interação
    operacional ou env var de lockout durante baterias. Relacionado:
    scheduler ignora pegada de ativações por `max_tokens` (OW-STU-006
    rec.4 — a convivência dual falha só sob captura pesada).
17. **Cobertura de testes** (OW-AUD-001 §1): zero testes de
    `dream_cycle`, `curiosity.explore`, `teleology` `cpu_high`, dunker
    canônico, endpoints `soul/api`; `brain/activations.py` segue dead
    code (Kilo P5 — wire ou deletar); `bus.publish` sem consumer loop
    (dead letters — OW-AUD-003); `agents/modes.py` `/tmp` efêmero;
    `pytest-asyncio` ausente vs `asyncio_mode` no pyproject.
18. **Papel**: `/content/WRITEUP_ESQUELETO.md` (deadline 2026-11-12,
    OW-STU-004 §5) — claims: ablação quantização, vacilo PR/χ, braços de
    intervenção; depende dos itens 5/8/10.

---

## 3. Inventário de baterias e ledgers

Runtime state às ~22:05 UTC (`sqlite_master` lidos read-only; ledgers são
gitignored — `*.sqlite`/`*.db` no `.gitignore`):

| Bateria | Runner / args | Brain | Ledger | Linhas agora | Reps canônicas / status |
|---|---|---|---|---|---|
| **gemma4_diag** | `scripts/gemma4_diag_battery/run_diag_battery.py [analyst\|executor] [--reps N]` (modificado, não commitado) | live ambos, `brain_chat` max_tokens=1800 temp=0.7 | `diag_battery.sqlite` → `diag_battery` (cols: ts, model_role, task_id, score, detail_json, flags_json, degenerate, latency_s, n_tokens, **rep** novo) | **4 e subindo** (rep0 analyst completo: wcst 90/stroop 95/nback 65.7/igt 100 — degen=0) | HF usou **4 reps**/task; script alvo = 5 reps × 4 tasks × 2 roles = **40 linhas**. RUNNING (PID 27872, lançado 21:59) |
| **diag orchestrator** | `run_diag_reps_swapped.sh [REPS]` (untracked; env API_PORT/ANALYST_PORT/EXECUTOR_PORT/REPS=5) | peer-swap via `POST /erika/unload\|reload` :8099→:8098 | mesmo ledger | — | necessário por OOM dual-resident (OW-STU-006 §5); log `logs/diag_reps_swapped.log` |
| **supervisor** | `run_supervisor_battery.py` (sem args) | hermético — dunker + kernel `affect_state` + lexicon; brain opcional | `supervisor_battery.sqlite` → `supervisor_battery` | **AUSENTE** (tinha 16 linhas em OW-STU-007; runner faz DELETE+reinsert) | 16 transcripts (8 cat × 2 turnos); determinístico — reps só importam p/ futuro tier juiz-analista (item 12) |
| **coding** | `run_coding_battery.py [cNN…]` | mecânico local + 12B review (600 tok) + E4B fix (1200 tok) | `coding_battery.sqlite` → `coding_battery` | **AUSENTE** (tinha 10) | **1 rep/caso** — diagnóstico; p/ inferência ≥3–5 reps/caso (variância de recall/halluc) |
| **refactor** | `run_battery.py [--n N]` | circuito completo Debug(analyst)→Code(executor)→Review(analyst)→smoke→gate | `battery_results.sqlite` → `battery_runs` | **AUSENTE** (tinha 8) | `--n` livre; 8 runs já mostraram arco de trust; p/ distribuição de verdicts ≥10–20 runs |
| **selfcheck** | `check_worker.py [--live] [--ledger-summary]` | só GET /health | nenhum | — | read-only; 131 testes coletados em `tests/` |
| payloads | `gemma4_diag_battery/payloads/` | — | `unified_v10_v11_payload.json` (10+ cenas v10×2 fases), `curated_gluzdov_swe_tasks{,_set2}.json` (12 SWE) | commitados (e641734) | insumos p/ items 5 e 8 |

**Qual bateria precisa de mais reps p/ validade estatística:**
`diag` (em curso, 5 reps); `coding` (1→3–5 reps/caso, 10 casos ≈ 30–50
chamadas×2 brains); `refactor` (--n 10–20 p/ distribuição de verdicts);
`supervisor` não precisa (léxico determinístico) até existir tier LLM.

**Estado vivo**: analyst :8098 `model_loaded:true` 11.2GB;
executor :8099 `model_loaded:false` 0.01GB; API :8081 up;
`kernel_hooks` 3/3 crates; state_guard + swap_scheduler rodando
(PIDs em `runtime_config/pids/`); `omni_code_index/` presente
(manifest: 201 chunks, 384d, faiss).

---

## 4. O run dos "blocks" — status

"Blocks" = experimentos do dataset HF
`fabricioslv/gemma4-e4b-colab-l4-results` →
`gemma4_e4b_l4_results.sqlite` (HF cache `snapshots/f55f069…`;
a cópia `data/hf_gemma4/` citada nos estudos **não existe** — dir
gitignored e ausente; usar o cache ou re-baixar). Conteúdo (lido agora):

| experiment | arm | linhas ledger | reps | re-scored canonicamente? |
|---|---|---|---|---|
| `block1_cognitivo` | observe_cognitive | 16 (4 tasks×4) | 4 | **SIM** — OW-STU-006 §3 (WCST/Stroop/N-back/IGT) |
| `block1_observe` | observe_free | 20 (cenas 1–20) | 1 | não |
| `block1_v10` | observe_free | 20 (mesmas cenas) | 1 | não |
| `block1_pranchas` | observe_projective | 20 (pranchas 1–20) | 1 | não |
| `block2_intervene` | baseline/thought_floor/unified_cascade/verification_gate | 48 (12 SWE×4 braços) | 1/braço | não |
| (canary) | baseline | 2 records | — | n/a |

`generation_records` tem 126 linhas (+2 canary fora do ledger) com
`visible_response`/`thinking_trace` separados, `degenerate_flag`,
`unique_ratio`, métricas de gate; `latent_layer_metrics` 1492 linhas
(pr_traj, svd_entropy, mps_chi_eff, h_norm por camada); `run_metadata`
10 runs E4B-**bf16** (1 com status `RUNNING` — stale no dataset).

**"1 repetição sobre a leitura dos blocks"** (nota do operador): a
replicação local foi 1 rep por task por brain — e a verdade do ledger é
ainda menor: OW-STU-007 P6 registra que só as 4 linhas do **analyst**
foram persistidas (os 2 reps do E4B documentados em OW-STU-006 §4 nunca
chegaram ao sqlite — apagados entre runs). Ou seja, a evidência persistida
era **1 rep × 4 tasks × 1 modelo**; o run em voo corrige isso com 5×4×2.

**Não-feito nos blocks**: (a) re-score canônico dos 108 records
não-cognitivos/SWE (item 5); (b) réplica local nf4 dos braços block2 e
das cenas/pranchas (item 8); (c) análise `latent_layer_metrics` vs flags
(vacilo PR/χ — insumo do writeup, item 18).

---

## 5. Trabalho em voo / working tree

`git status`:
- `M scripts/gemma4_diag_battery/run_diag_battery.py` — `--reps N`,
  migração guardada da coluna `rep`, loop rep×role×task.
  (docstring do arquivo ficou stale: ainda diz "runs each task once").
- `M scripts/start_omni_worker.sh` — flag `--reindex` + auto-rebuild do
  code index quando ausente/stale (`find -newer` vs `chunks.parquet`).
- `?? scripts/gemma4_diag_battery/run_diag_reps_swapped.sh` — orquestrador
  peer-swap (§3).
- `?? data/` — artefatos runtime parcialmente cobertos por gitignore:
  `node.db` (artifacts=45, missions=0 — missions segue schema morto,
  Kilo P3), `witness.jsonl` (24 eventos), `somatic_probes.sqlite`
  (probes=1 — esparsa, conformidade #7), `state_snapshots/` (2 tar.gz),
  `monitor/erika_torch_activations.jsonl` (12 linhas).

Sem TODO/FIXME marcadores no código tocado (único hit é o detector do
reviewer_agent). PIDs vivos: API 24009, state_guard 24038,
swap_scheduler 25630, battery runner 27872.

---

## 6. Docs desatualizadas (runtime/code vs doc)

| Doc | Claim stale | Realidade |
|---|---|---|
| `PENDING_ROADMAP.md` | P0/P1/P3 todos `[ ]` | implementados (§1): gate fail-closed `d3ee101`, wiring `418ed68`, jail `ff4d24b`, care `1647668`, probe `4d48c3b`, state_guard `e72927f`, dual-write `ce9c804`, audit_adapter `ec0f847`, swap `781addf`+`9fabc4d`+`ef60ce9` |
| `CODE_README_CONFORMANCE.md` §3 #2 | "busy detection monotônica" | corrigido em `ef60ce9` (delta por tick) — doc não atualizado |
| `KAGGLE_SETUP_VALIDATION.md` | "GPU telemetry not actually read"; "stub nunca carrega modelo"; "69 passed" | GPU real desde `eebc2e6` (§6 do próprio doc se contradiz); servidor real desde `9fabc4d`; **131 testes** coletados |
| `docs/index.md` | estudos até OW-STU-006 | falta OW-STU-007 (`ERROR_PATTERNS_SELF_CHECK.md`) |
| `DIRECTORY_CONTRACT.yaml` | `modules.total: 40`; `with_main` 3 entradas; `stubs_and_shims` sem dunker | 49 .py reais; faltam `swap_scheduler.py`+`state_guard.py` em with_main; `agency/dunker.py` é adapter real |
| `README.md` | tabela de serviços lista comandos individuais | `scripts/start_omni_worker.sh` (bring-up 1-comando, `--reindex` novo) não citado em nenhum doc |
| `run_diag_battery.py` docstring | "uma rep por task por brain" | agora suporta `--reps` |
| `GEMMA4_DIAG_REPLICATION.md` §10 / `GEMMA4_BATTERY_INVENTORY.md` §5 | evidência `data/hf_gemma4/*.sqlite` | dir ausente — dataset só no HF cache |
| `ERROR_PATTERNS_SELF_CHECK.md` §1 | ledgers com 10/4/8/16 linhas | todos ausentes/zerados — diag repovoando |
| `soul/static/` | index.html "demo" | `superapp.html` (464ln) adicionado em `de3bfb6`, sem menção nos docs |

---

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
