# agents/ — Camada de Agentes / Agent Layer

**pt-BR:** Agentes por papel (Debug / Analyst / Reviewer / Code), bus
inter-agentes, configs de persona, modes estilo Roo e ponte para CLIs
agênticos externos. Todo trabalho de LLM passa por `_llm.brain_chat*` para os
servidores brain externos (analista `:8098` / executor `:8099`,
`/v1/chat/completions` OpenAI-compatible); cada agente degrada para payload
heurístico/stub quando os backends caem (`llm: False` nos resultados).

**English:** Role agents (Debug / Analyst / Reviewer / Code), an inter-agent
message bus, persona configs, Roo-style modes, and a bridge to external
agentic CLIs. All LLM work is routed through `_llm.brain_chat*` to the
external brain servers (analyst `:8098` / executor `:8099`, OpenAI-compatible
`/v1/chat/completions`); every agent degrades to a heuristic/stub payload
when the backends are down (`llm: False` in results).

## Files

| File | Role | Public API |
|---|---|---|
| `_llm.py` | Shared brain helper (internal) | `brain_chat(messages, role, max_tokens, temperature, include_soma)` → text or `None`; `brain_chat_json(...)` → first `{...}` parsed or `None`. Soma injection: prepends `[soma live]` telemetry (cpu/ram/gpu/vram/virt) as system msg when `include_soma` (default on; `OMNI_SOMA_INJECT=0` disables) — the model sees the live machine body, incl. VM detection |
| `bus.py` | Synchronous pub/sub bus | `MessageBus` (`subscribe`/`publish`/`pending`/`consume`/`resolve_conflict`), `get_message_bus()` singleton, `canonical_bus_available()` |
| `persona.py` | Persona loader + prompt builder | `load_persona(name, config_dir)`, `system_prompt(role, mode)`, `ROLE_PERSONA_MAP`, `PERSONA_DESCRIPTIONS` |
| `modes.py` | Roo-style modes with sticky model role | `MODES`, `switch_mode(mode)`, `set_role(mode, role)`, `spec_for(mode)`, `current_mode()` |
| `debug_agent.py` | Read-only diagnostician | `DebugAgent.diagnose(issue, context)`, `analyze_logs(logs)`, `suggest_fix(diagnosis)` |
| `analyst_agent.py` | Clinical session analyst | `AnalystAgent.analyze(session)`, `interpret(context)` |
| `reviewer_agent.py` | Adversarial reviewer (judge 1) | `ReviewerAgent.review(code, context)`, `validate_tests(test_results)` |
| `code_agent.py` | Gated patch producer | `CodeAgent.generate(spec, context)`, `submit_patch(code, test_results, target_files)` |
| `external_cli_agent.py` | External agentic CLI bridge | `ExternalCLIAgent.execute/publish_to_bus`, `ACPClient`, `ShellCLIAdapter`, `sanitized_env`, `default_clis`, `register_cli`, `list_available` |

## Governance surface / Superfície de governança

- **DebugAgent** is read-only by contract: `diagnose` calls the executor brain
  with a "may NOT edit files" system prompt and returns `can_fix: False`;
  fixes are delegated to CodeAgent.
- **CodeAgent.submit_patch** enforces the anti-impulsivity prosthesis in
  order: reject `empty_diff` → reject `tests_failing`/`no_tests_passed` →
  `safety.matrix.check_permission("modify_code", trust_level)` (≥0.8) →
  `safety.gate.evaluate_action("submit_patch", ...)` (ConstitutionalGate;
  `allowed=True` only on EXECUTE/TEACH). Trust comes from an injected
  `trust_provider` (duck-typed `get_trust`) or `orchestration.governance.
  TrustSystem`; falls back to 0.9.
- **ReviewerAgent.review** merges local heuristics (TODO/FIXME, `print(`)
  with an analyst-brain JSON verdict; any `severity="high"` issue forces
  `approved=False`. `validate_tests` requires `failed==0` and coverage ≥0.8.

## External CLI bridge (`external_cli_agent.py`)

- **Adapter selection:** `auto` (default) prefers `ACPClient` when both the
  `acp` SDK and the binary exist → `ShellCLIAdapter` → `none` (failure dict).
  A failed ACP run degrades to shell at `execute()` time.
- **ACP path:** stdio JSON-RPC (`initialize → session/new → session/prompt`)
  via `acp.spawn_agent_process`; `_ACPSessionHandler` is DENY-by-default —
  only `read/edit/delete/move/search` with all locations inside the session
  cwd (plus `think`) are permitted.
- **Shell path:** `subprocess` in an isolated workdir
  (`OMNI_EXTERNAL_CLI_WORKDIR`, default `/tmp/omni_coworker_external`), hard
  timeout that SIGKILLs the process group, best-effort JSON parse of stdout.
- **Env sanitization:** children get `SANITIZED_BASE_ENV`
  (`OPENAI_BASE_URL=http://127.0.0.1:8098`) + the `ALLOWED_ENV_NAMES`
  allowlist; prefixes (`ANTHROPIC_`, `OPENAI_`, `HF_`, `AWS_`, …) and
  secret-looking substrings (`TOKEN`, `SECRET`, `API_KEY`, …) are always
  dropped — no credentials reach child processes.
- **Registry:** `DEFAULT_CLIS` (dev, opencode, kilo, hermes) overridable via
  `OMNI_CLI_<NAME>` env or `register_cli`; `list_available` probes PATH.

## Data/control flow / Fluxo de dados e controle

```
issue ─► DebugAgent.diagnose ─► _llm.brain_chat_json(executor) ─► {diagnosis, suggestions}
spec  ─► CodeAgent.generate ───► _llm.brain_chat(executor) ──────► code
code  ─► ReviewerAgent.review ─► heuristics + brain_chat_json(analyst, persona="critic")
patch ─► CodeAgent.submit_patch ─► matrix.check_permission ─► gate.evaluate_action ─► verdict
task  ─► ExternalCLIAgent.execute ─► ACPClient|ShellCLIAdapter ─► publish_to_bus ─► MessageBus
```

## Dependencies & fallbacks / Dependências e fallbacks

- **Imports:** `brain.server.get_brain_client` (httpx, cached per role),
  `safety.matrix`/`safety.gate` (canonical adapters), `agency.analyst`
  (AnalystAgent), `orchestration.governance.TrustSystem` (CodeAgent).
- **Optional:** `acp` SDK (`agent-client-protocol`) — lazy probe, never
  imported at module level; `src.agentes.agent_protocol.AgentMessageBus` —
  probed by `canonical_bus_available()` only as an availability flag (the
  canonical async bus is intentionally reimplemented as a sync surface).
- **Config:** personas read `config/agents/*.json` (`OMNI_AGENTS_CONFIG_DIR`
  override); modes persist to `OMNI_MODES_STATE` (default
  `/tmp/omni_modes_state.json`). Missing/invalid config → minimal dict with
  `fallback: True`; `system_prompt` is always non-empty.
