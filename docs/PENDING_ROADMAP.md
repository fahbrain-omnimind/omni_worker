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
- [ ] wire do loop: EventBus→TrustSystem, breakers/quarentena/witness por iteração (parcial: witness existe, breakers/quarentena pendentes)
- [x] safety/jail.py — política real implementada (107 linhas, sem placeholder)
- [x] safety/care.py — escalação territorial Brasil (251 linhas, CVV 188/CAPS/CRP)
- [ ] residual: judges/orquestrador fail-open restantes (AUDIT_OPENCODE §1.4)

## P1 — Loop de continuidade (Kilo)
- [x] probe_recorded no /soma/probe (persistência do loop) — `soma/probe.py:221`, wired em `app.py:37`
- [x] OMNI_STATE_DIR + snapshots — `data/state_snapshots/` via `state_guard`
- [x] witness→node_db + endpoints `/agency/witness` + verify — `app.py:102`
- [ ] export/restore tar.zst com witness (restore path pendente)
- [ ] adapter src/audit/immutable_audit.py canônico (sha256+fcntl)

## P2 — Afeto conversacional (estudo + opencode)
- [x] agency/affect_tracer.py L0-L4 + 6 testes (feito)
- [ ] wire no /brain/chat (escada L0-L4 real) + supervisor lane analyst — `with_affect` existe em `_llm.py` mas nada o chama; sem `safety/supervisor.py` nem endpoints `/supervisor/*`
- [ ] teleology: remover probe canônico morto; metabolize real

## P3 — Swap inteligente (alocação sob demanda)
- [x] /brain/unload + /brain/reload → `/erika/unload|reload` no erika_torch_server portado — `brain/server.py:45-62`
- [x] scheduler orchestration: evicta E4B sob VRAM alta + ocioso (delta de ativações — `ef60ce9`; timed reload exige headroom — `f439dbf`)
- [x] testes de swap — `tests/test_swap_scheduler.py` (6 testes: evict, busy-delta, reload por headroom, timed suprimido sob pressão)

## P4 — Baterias amplas (Cline/kilo)
- [x] scripts/supervisor_battery/ (12 transcripts, 8/12 detecção)
- [ ] transcripts bajulação/fixação → tier juiz-analista (fechar gap 0%)
- [ ] refactor_battery multi-arquivo/multi-turn
- [ ] diag battery multi-rep — runner `--reps` pronto + peer-swap script; run 5×4×2 em curso (repovoar ledger)
- [ ] re-score dos 108 registros "blocks" do dataset HF (só block1_cognitivo/16 re-scored)
- [ ] ledgers perdidos: supervisor(16)/coding(10)/refactor(8) sqlite ausentes — regerar

## Resultados
- docs/results/ — outputs de cada validação runtime
- battery_results.sqlite + supervisor_battery.sqlite (ledgers)
