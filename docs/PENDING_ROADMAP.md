<!-- doc_id: OW-OPS-002 | title: Pending Roadmap — omni_worker (2026-11-02) | author: devin | requester: artifice-operator | project: omni-agent-coworker (kaggle) | date: 2026-11-02 | status: active -->

# Pending Roadmap — omni_worker

Regra: NADA de placeholder. Cada item = implementação + testes herméticos
+ validação runtime nos brains Gemma online (:8098/:8099) + resultados
salvos (docs/results/ + sqlite). Fontes de dados: Kaggle/HF para
cybersecurity/benchmarks quando precisar.

Checkboxes atualizados 2026-11-02 contra o código (ver OW-OPS-004
CONTINUITY_MAP para evidência commit-a-commit).

## P0 — Segurança/governança (auditorias OpenCode/Kilo/Cline)
- [x] gate fail-closed opcional (OMNI_GATE_FAIL_CLOSED=1) — `safety/gate.py:55`
- [x] wire do loop: EventBus→TrustSystem, breakers/quarentena/witness por iteração — `loop._gov()` lazy wiring: EventBus gov alimenta TrustSystem compartilhado (deltas loop.* honestos), cada estágio sob CircuitBreaker (3 falhas → abre → quarentena com witness; ciclos seguintes pulam como `quarantined`), status `partial` granular (falha de um estágio não derruba independentes), resumo `payload["governance"]`
- [x] safety/jail.py — política real implementada (107 linhas, sem placeholder)
- [x] safety/care.py — escalação territorial Brasil (251 linhas, CVV 188/CAPS/CRP)
- [x] residual: judges/orquestrador fail-open restantes (AUDIT_OPENCODE §1.4) — consensus tri-state: juiz cego (`blind:true`, backend down) ≠ juiz dissidente; `consensus=None` → `_enqueue_approval()` (approval_queue.jsonl append-only + witness `orchestrator.approval_required`) e break do loop, em vez de dissent cego/retry às cegas; `matrix.py` ramo fail-open de laboratório agora registra o veredito (saía da cadeia de evidência); testes tri-state + fila em `test_judges_failclosed.py`

## P1 — Loop de continuidade (Kilo)
- [x] probe_recorded no /soma/probe (persistência do loop) — `soma/probe.py:221`, wired em `app.py:37`
- [x] OMNI_STATE_DIR + snapshots — `data/state_snapshots/` via `state_guard`
- [x] witness→node_db + endpoints `/agency/witness` + verify — `app.py:102`
- [x] export/restore tar com witness — `store/state_guard.py:120` restore fail-closed (manifest hash + cadeia witness verificadas em staging antes de tocar o vivo) + evento `state_restore` anexado à cadeia restaurada; bug de retenção corrigido (poda nunca rodava — `valid_heads` contava todos); snapshot atômico via staging (OW-AUD-017: race hash→tar invalidava o snapshot mais novo)
- [x] adapter src/audit/immutable_audit.py canônico (sha256+fcntl) — `audit/immutable_audit.py`: port worker-scale do soberano (cadeia sha256, lock fcntl sidecar, last-hash do tail do log, verify tolerante a restarts, guarda UNCONSCIOUS_COMPONENTS; delta: filtro só action+component, não str(details))

## P2 — Afeto conversacional (estudo + opencode)
- [x] agency/affect_tracer.py L0-L4 + 6 testes (feito)
- [x] wire no /brain/chat (escada L0-L4 real) + supervisor lane analyst — `affect_tracer.get_affect_tracer()` singleton (instância por chamada matava a trajetória — streaks/densidade nunca disparavam); `/brain/chat` com `with_affect` injeta `[affect]` + devolve veredito completo (posture/judge/trajectory); L4 retém geração sem chamar o brain; juiz-analista `_analyst_judge` já era chamado via `brain_chat_json` nos níveis L2-L3 — `_llm.brain_chat` também usa o singleton
- [x] teleology: probe canônico morto removido (`src.cognitive.dream_weaver` — acoplamento host-morto); `dream.metabolize` real: marca d'água persistida + `memtrias.records_since` + digest tecido pelo analista (validado ao vivo — Gemma produziu síntese real) + memória `dream` com `source_ids` em events; contagens honestas (zero quando nada novo)

## P3 — Swap inteligente (alocação sob demanda)
- [x] /brain/unload + /brain/reload → `/erika/unload|reload` no erika_torch_server portado — `brain/server.py:45-62`
- [x] scheduler orchestration: evicta E4B sob VRAM alta + ocioso (delta de ativações — `ef60ce9`; timed reload exige headroom — `f439dbf`)
- [x] testes de swap — `tests/test_swap_scheduler.py` (6 testes: evict, busy-delta, reload por headroom, timed suprimido sob pressão)

## P4 — Baterias amplas (Cline/kilo)
- [x] scripts/supervisor_battery/ (12 transcripts, 8/12 detecção)
- [x] transcripts bajulação/fixação → tier juiz-analista (fechar gap 0%) — `run_supervisor_battery.py`: famílias conversacionais (flattery/passion/guilt/separation) agora passam pelo `AffectTracer().observe` real (fresh por turno, léxico + `_analyst_judge` em L2+/ambíguo); 4 colunas novas no ledger (tracer_level/posture/judge_intent/judge_recommend); detecção conta judge review/block + posture review/sustain_uncertain. Run ao vivo: **16/16 detected**, juiz real classificou separation→flattery_suspect/clarify, guilt→other/allow
- [ ] refactor_battery multi-arquivo/multi-turn
- [ ] diag battery multi-rep — runner `--reps` pronto + peer-swap script; run 5×4×2 em curso (repovoar ledger)
- [ ] re-score dos 108 registros "blocks" do dataset HF (só block1_cognitivo/16 re-scored)
- [x] ledgers perdidos: supervisor(16)/coding(10)/refactor(8) sqlite ausentes — regerar — supervisor_battery.sqlite (16 rows, juiz-analista real), refactor battery_results.sqlite (review 0.9, llm.debug+code true), coding_battery.sqlite (analyst=Y 10/10, recall 1.0 em 8 casos; fix tier exigiu /erika/reload — executor tinha sido evictado pelo swap)

## Resultados
- docs/results/ — outputs de cada validação runtime
- battery_results.sqlite + supervisor_battery.sqlite (ledgers)
