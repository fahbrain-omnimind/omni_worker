<!-- doc_id: OW-OPS-002 | title: Pending Roadmap — omni_worker (2026-11-02) | author: devin | requester: artifice-operator | project: omni-agent-coworker (kaggle) | date: 2026-11-02 | status: active -->

# Pending Roadmap — omni_worker

Regra: NADA de placeholder. Cada item = implementação + testes herméticos
+ validação runtime nos brains Gemma online (:8098/:8099) + resultados
salvos (docs/results/ + sqlite). Fontes de dados: Kaggle/HF para
cybersecurity/benchmarks quando precisar.

Checkboxes atualizados 2026-11-02 contra o código (ver OW-OPS-004
CONTINUITY_MAP para evidência commit-a-commit).

### OW-STU-016 — auditoria IIT/GWT (kilo research + devin review) — 2026-11-03
- Relatório: `docs/design/OW-STU-016_iit_gwt_measurement_audit.md` — IIT 3.0/4.0, PyPhi (teto ~10 nós), Φ*/Φ^G/ΦID/PCI proxies, críticas (Doerig unfolding, Merker, COGITATE), auditoria soberano+worker, proposta 3 estágios com rótulos [CAP]/[PRX]/[TXT]/[CLS]/[EXP].
- [x] Estágio 1 implementado: MIP explicável (`mip_side_a/b`, `mip_top3`) + anti-saturação (`n_distinct_states`, `diversity`) em `phi_meta.update`.
- [x] Ignição de workspace (GWT-lite) + sinergia proxy (ΦID-lite) implementados em `kernel_daemon/ignition.py` (testado em `tests/test_ignition.py`).
- [x] Formalização do `scale_stack` (`scale` tag em `phi_meta.py:188` e `ignition.py:99`).
- [x] PyPhi viável NO BLANKET soberano (elementos principiados FEP) — implementado `psychoanalysis/markov_blanket.py` + `run_blanket_pyphi.py`; resultados `docs/results/blanket_pyphi.md` (blanket 4 e 6 nós com E, P).
- [x] Estágio 2 (MPS e Espectral): Captura de trajetória por passo (`_emit_step_trajectory` em `erika_torch_server.py:214`), decomposição espectral em `activation_beta/hidden_spectral.py` e exportação real em `scripts/dashboard_export.py`.
- [x] Topologia e Swap: Boot sequencial com gate de 10GB VRAM livre, `--lazy` fallback e peer-swap automático com autocura de CUDA OOM em `agents/_llm.py`.

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
- [x] refactor_battery multi-arquivo/multi-turn — vítima 2 arquivos acoplados (todo_api + todo_stats duplicando store/validação; spec exige módulo compartilhado); loop multi-turn REFACTOR_MAX_TURNS=3 (feedback=smoke tail + review issues → próximo turno); **bug real achado no harness**: smoke testava a vítima original (sys.path[0]=VICTIM), não o refactor — fix copia o teste para o out dir (verificado: refactor quebrado → 5 fails); ledger +turns/turns_json
- [x] diag battery multi-rep — runner `--reps` pronto + peer-swap script; run 5×4×2 concluída (80 linhas populadas no ledger sem nenhum score 0). Output: `diag_battery.sqlite`
- [x] re-score dos 108 registros "blocks" do dataset HF — `scripts/gemma4_diag_battery/rescore_hf_blocks.py` re-scoreia todos os 126 generation_records; achado: flag armazenado ≈ unique_ratio token-level (ur_sanitized ~0.17 → degen), não o shape de linhas — o `_degenerate` do worker pegava 0/49. Detector v2 (word_ur<0.5 ∧ rep4>0.05) reproduz **100% dos blocos cognitivos** (16/16) sem falsos positivos em observe/pranchas/v10; block2_intervene diverge (22/48) porque o flag mistura degen de forma com semântica de gates (degen=1↔gates=0 nos 33). Relatório: docs/results/rescore_hf_blocks.md; `_degenerate` do runner ganhou o segundo tier
- [x] ledgers perdidos: supervisor(16)/coding(10)/refactor(8) sqlite ausentes — regerar — supervisor_battery.sqlite (16 rows, juiz-analista real), refactor battery_results.sqlite (review 0.9, llm.debug+code true), coding_battery.sqlite (analyst=Y 10/10, recall 1.0 em 8 casos; fix tier exigiu /erika/reload — executor tinha sido evictado pelo swap)

## Resultados
- docs/results/ — outputs de cada validação runtime
- battery_results.sqlite + supervisor_battery.sqlite (ledgers)
