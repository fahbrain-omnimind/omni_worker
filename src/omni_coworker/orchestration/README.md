# orchestration/ — Plano de Orquestração e Governança / Orchestration & Governance Plane

**pt-BR:** `AgentOrchestrator` roda o loop tarefa → executor → juízes
adversariais → auditoria (com cascade reset), persistindo artefatos no
`node.db`. `governance.py` provê stand-ins síncronos dos módulos canônicos de
governança autopoiética (event bus, trust, quarentena, rollback, circuit
breaker, métricas) — as superfícies canônicas async/dataclass são
reimplementadas como motores síncronos mínimos para o loop do coworker nunca
precisar de asyncio. `swap_scheduler.py` gerencia a coabitação dos dois
brains na GPU (evict/reload do executor por folga de VRAM e ociosidade).

**English:** `AgentOrchestrator` runs the task → executor → adversarial
judges → audit feedback loop (with cascade reset), persisting artifacts to
`node.db`. `governance.py` provides synchronous stand-ins for the canonical
autopoietic governance modules (event bus, trust, quarantine, rollback,
circuit breaker, metrics) — the canonical async/dataclass surfaces are
deliberately reimplemented as small sync engines so the coworker loop never
needs asyncio. `swap_scheduler.py` manages GPU cohabitation of the two
brains (executor evict/reload by VRAM headroom and idleness).

## Files / Arquivos

| File | Role | Public API |
|---|---|---|
| `agent_orchestrator.py` | Feedback-loop orchestrator (also runnable as `__main__`) | `AgentOrchestrator.setup_agents`, `create_task`, `execute_task`, `run_judge_review`, `run_audit`, `run_external`, `feedback_loop`, `stall`, `reset_count` |
| `governance.py` | Sync governance stand-ins | `EventBus`, `TrustSystem`, `QuarantineSystem`, `RollbackSystem`, `CircuitBreaker` (+`CircuitBreakerOpen`), `OrchestratorMetrics` |
| `swap_scheduler.py` | VRAM-aware brain swap loop (runnable as `__main__`) | `SwapScheduler(interval_s=600)`, `.tick()` → state dict, `.loop(once)`; CLI `--interval-s`, `--once` |
| `__init__.py` | Re-exports the orchestrator + governance classes | — (`swap_scheduler` importable as submodule) |

## Feedback loop (`AgentOrchestrator.feedback_loop`)

```
task ─► execute_task (executor brain :8099, prior feedback fed back into prompt)
     ─► run_judge_review ──► judge1: ReviewerAgent (heuristics + analyst LLM)
                            judge2: executor brain, second-opinion JSON verdict
                            judge3: analyst brain, concurring verdict over prior verdicts
     ─► run_audit (static checks: modularity/security/tests)
     ─► db.add_artifact → store.node_db.NodeDB at base_dir/node.db
     ─► consensus AND audit.passed → status=approved (break)
        else needs_revision → feedback_notes += dissenting judge comments
           stall() >= CASCADE_STALL_THRESHOLD (3) → "cascade_reset" event +
           SIMPLIFY_NOTE injected into the next executor prompt
```

- Consensus requires **all three** judges to approve; the loop always
  terminates at `max_iterations` (default 5) — never deadlocks.
- Filesystem layout under `OMNI_ORCHESTRATOR_DIR` (default
  `/tmp/omni_coworker_orch`): `agents_pool/`, `audit/` (judge reviews +
  audits as JSON), `feedback/`, `results/`, `tasks/` (task state JSON),
  `node.db` (SQLite artifacts via `NodeDB`).
- `run_external(name, task)` delegates to `agents.ExternalCLIAgent` (ACP →
  shell → none); never touches the brain backends.
- Judge fallbacks: ReviewerAgent exception or dead brain → static
  `approved=True` / `all(verdicts)` concurrence with `llm: False` — the loop
  keeps running when backends are down.

## Swap scheduler (`swap_scheduler.py`)

pt-BR: A L4 hospeda os dois brains NF4 (≈16.9GB dos 22.5GB). O scheduler
roda `tick()` a cada `interval_s` (default 600s): se `vram_ratio >=
OMNI_SWAP_EVICT_THRESHOLD` (0.9) e o executor não produziu novas
activations desde o último check (`/health → activations_buffered`), faz
`POST /erika/unload` no executor (libera ~9-10GB p/ janelas KV maiores do
analyst); se `vram_ratio <= OMNI_SWAP_RELOAD_THRESHOLD` (0.75) ou o tempo
descarregado excede `OMNI_SWAP_MAX_UNLOADED_MIN` (30), faz
`POST /erika/reload`. Nunca despeja executor ocupado. Estado em
`self.state` (`executor`, `last_evict`, `last_reload`, `checks`,
`events`, `vram_ratio`).

English: The L4 hosts both NF4 brains (≈16.9GB of 22.5GB). The scheduler
runs `tick()` every `interval_s` (default 600s): when `vram_ratio` hits
the evict threshold and the executor produced no new activations
(`/health → activations_buffered`), it POSTs `/erika/unload` on the
executor (frees ~9-10GB for larger analyst KV windows); when VRAM frees
below the reload threshold or the unloaded time exceeds the max, it
POSTs `/erika/reload`. Never evicts a busy executor. Exposed as
`__main__` (`--interval-s`, `--once`); the same surface is proxied by
`POST /brain/unload|reload` on the worker API.

## Governance engines (`governance.py`)

| Class | Surface | Canonical relationship |
|---|---|---|
| `EventBus` | `subscribe`/`publish`/`history`/`clear` | Canonical `OrchestratorEventBus` is async → reimplemented sync + history log |
| `TrustSystem` | `get_trust`/`set_trust`/`record_event`/`summary`/`reset` | Canonical computes success-rate; here additive deltas — `tests_passed` **+0.1**, `review_dissent` **−0.2**, default **0.5**, clamped [0,1] |
| `QuarantineSystem` | `quarantine`/`release`/`is_quarantined`/`status` | Canonical needs orchestrator + coroutines → sync registry |
| `RollbackSystem` | `create_snapshot`/`rollback_component`/`get_current_version`/`get_snapshot`/`get_version_history` | Canonical async → per-component snapshot stack (`max_versions=10`) |
| `CircuitBreaker` | `is_available`/`record_success`/`record_failure`/`call_with_protection`/`get_stats`/`reset` | Same state machine as canonical `AgentCircuitBreaker`; opens at `failure_threshold=3`, half-open probe after `recovery_timeout` |
| `OrchestratorMetrics` | `push`/`record`/`mean`/`count`/`summary` | **Thin adapter** — uses canonical `src.agentes.orchestrator_metrics.OrchestratorMetricsCollector` when importable, else in-memory fallback (`_engine_source` reports which) |

## Dependencies / Dependências

- **Imports (lazy):** `agents._llm.brain_chat(_json)` (brains `:8098`/`:8099`),
  `agents.reviewer_agent`, `agents.persona.system_prompt("judge")`,
  `agents.external_cli_agent.ExternalCLIAgent`, `store.node_db.NodeDB`,
  `brain.server._base_for_role` + `httpx` (swap scheduler), `soma.probe`
  (VRAM ratio).
- **Optional canonical:** `src.agentes.orchestrator_metrics` (probed once in
  `OrchestratorMetrics.__init__`); the other canonical governance modules are
  referenced in docstrings but intentionally reimplemented, not imported.
- **Imported by:** `agents.code_agent` (`TrustSystem`), `omni_coworker`
  package API, CLI/tests; `agent_orchestrator.py` is a declared standalone
  executable (DIRECTORY_CONTRACT `with_main`); `swap_scheduler.py` also has
  a `__main__` block (`--interval-s`, `--once`) though it is not yet listed
  in the contract.
