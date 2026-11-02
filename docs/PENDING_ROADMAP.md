<!-- doc_id: OW-OPS-002 | title: Pending Roadmap — omni_worker (2026-11-02) | author: devin | requester: artifice-operator | project: omni-agent-coworker (kaggle) | date: 2026-11-02 | status: active -->

# Pending Roadmap — omni_worker (2026-11-02)

Regra: NADA de placeholder. Cada item = implementação + testes herméticos
+ validação runtime nos brains Gemma online (:8098/:8099) + resultados
salvos (docs/results/ + sqlite). Fontes de dados: Kaggle/HF para
cybersecurity/benchmarks quando precisar.

## P0 — Segurança/governança (auditorias OpenCode/Kilo/Cline)
- [ ] gate fail-closed opcional (OMNI_GATE_FAIL_CLOSED=1) — hoje fail-open (allowed:true,no_gate)
- [ ] wire do loop: EventBus→TrustSystem, breakers/quarentena/witness por iteração (9 itens P0)
- [ ] safety/jail.py — substituir allowlist placeholder por jail real (canônico como referência)
- [ ] safety/care.py — escalação territorial Brasil (diretórios docs/care/ + CVV 188/CAPS/CRP) — módulo novo, sem equivalente canônico

## P1 — Loop de continuidade (Kilo)
- [ ] probe_recorded no /soma/probe (persistência do loop)
- [ ] OMNI_STATE_DIR + export/restore tar.zst com witness
- [ ] dual-write witness→node_db + endpoints /agency/witness + verify
- [ ] adapter src/audit/immutable_audit.py canônico (sha256+fcntl)

## P2 — Afeto conversacional (estudo + opencode)
- [x] agency/affect_tracer.py L0-L4 + 6 testes (feito)
- [ ] wire no /brain/chat (escada L0-L4 real) + supervisor lane analyst
- [ ] teleology: remover probe canônico morto; metabolize real

## P3 — Swap inteligente (alocação sob demanda)
- [ ] /brain/unload + /brain/reload wrapper (patch erika_torch_server)
- [ ] scheduler orchestration: evicta E4B quando 12B precisa de KV maior
- [ ] testes de swap (VRAM freed/restored, latência reload)

## P4 — Baterias amplas (Cline/kilo)
- [x] scripts/supervisor_battery/ (12 transcripts, 8/12 detecção)
- [ ] transcripts bajulação/fixação → tier juiz-analista (fechar gap 0%)
- [ ] refactor_battery multi-arquivo/multi-turn

## Resultados
- docs/results/ — outputs de cada validação runtime
- battery_results.sqlite + supervisor_battery.sqlite (ledgers)