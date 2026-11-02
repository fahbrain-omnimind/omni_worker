# safety/ — Plano de segurança / Governance plane

pt-BR: Matriz de permissões + portão constitucional + jail do workspace +
escalação territorial de cuidado. É o lado coercitivo da política de "prótese
executiva": agentes diagnosticam somente-leitura, e mutação de código/config
só passa por `check_permission` (gateado por trust) e `evaluate_action`
(deliberação constitucional). `care` é a ponte humana: escala preocupações de
saúde mental/abuso para recursos territoriais brasileiros.

English: Permission matrix + constitutional gate + workspace jail +
territorial care escalation. This is the enforcement side of the "executive
prosthesis" policy: agents diagnose read-only, and code/config mutation only
passes through `check_permission` (trust-gated) and `evaluate_action`
(constitutional deliberation). `care` is the human bridge: it escalates
mental-health/abuse concerns to Brazilian territorial resources.

## Files / Arquivos

| File | Role | Key API |
|---|---|---|
| `__init__.py` | Package surface | re-exports `matrix`, `gate`, `jail` + all public functions (`care` importable as submodule, lazy-loaded by `app.py`) |
| `matrix.py` | **Adapter** → `src.orchestration.permission_matrix.PermissionMatrix` (omni_node) | `get_matrix()`, `check_permission(action, context)` |
| `gate.py` | **Adapter** → `src.autopoietic.constitutional_gate` (omni_node) | `get_gate()` (lazy singleton), `evaluate_action(action, context)` |
| `jail.py` | Standalone workspace sandbox (no canonical dep) | `is_safe(cmd)`, `is_command_safe(cmd)`, `validate_path(path)` |
| `care.py` | Territorial escalation (Brazil; no canonical dep) | `escalate(reason, state_uf, age)` → `{level L1–L4, resources, referral_text}`; UF resource DB from `docs/care/` + national resources (CVV 188, CAPS, CRP, SAMU 192, Disque-100) |

## Control flow / Fluxo

```
CodeAgent.submit_patch(code, test_results, target_files)     agents/code_agent.py
  ├─ refuses: empty_diff | tests_failing | no_tests_passed
  ├─ check_permission("modify_code", {"trust_level": trust})  ← matrix.py
  └─ evaluate_action("submit_patch", {proponent, target_files, content[:4000]})
                                                              ← gate.py
```

`GET /safety/check?action=...` (app.py) exposes both verdicts for introspection:
`{"action", "matrix": bool, "gate": {...}}`. `GET /safety/care?reason=...`
(optional `state_uf`, `age`) escalates through the care path.

## Behavior / Comportamento

- `check_permission` — canonical path calls `PermissionMatrix.can_execute(action,
  emergency=…, trust_level=…)`; **standalone fallback** (no omni_node on
  PYTHONPATH) mirrors the policy: `read_*`/search/inspect/list/communicate are
  free; `modify_code` requires `trust_level ≥ 0.8`, `modify_config` ≥ 0.9,
  everything else ≥ 1.0. Note: if the canonical matrix raises, it fails **open**
  (returns `True`) — the gate is the second line of defense.
- `evaluate_action` — wraps the action in a `ChangePayload` (uuid, proponent,
  intent, target_files, diff_or_content, context) and calls
  `gate.evaluate()`; the `DeliberationCertificate` verdict maps to
  `allowed = verdict in ("EXECUTE", "TEACH")` (`REFUSE` → denied). Returns
  `{allowed, verdict, grade, reason}`. Gate unavailable → fail-**open** by
  default (`{"allowed": True, "reason": "no_gate"}`); set
  `OMNI_GATE_FAIL_CLOSED=1` to invert (`allowed: False`,
  `reason: "no_gate_fail_closed"`). Gate raises → `allowed: False,
  reason: "gate_error: …"`.
- `jail` — pure-Python denylist checks: `is_command_safe` blocks fork bombs,
  `rm -rf /`, `mkfs`, `dd if=/dev/zero`, `curl|sh`, `eval $(`, `nc -l`, etc.;
  `validate_path` blocks `..` traversal, `/etc/passwd`, `/root/.ssh`, and
  absolute paths outside `/content/` and `/tmp/`. (Roadmap: replace with a
  real allowlist jail — see `docs/PENDING_ROADMAP.md` P0.)
- `care` — keyword heuristic maps `reason` to `L1–L4` (suicide/self-harm
  terms → L4; crisis/panic/violence → L3; sadness/depression/anxiety → L2;
  else L1); `state_uf` selects the UF resource table (N+NE+CO covered), and
  `age < 18` adds the CAPS-II minor branch. `referral_text` is never empty.

## Dependencies / Dependências

- Optional (omni_node via `PYTHONPATH`): `src.orchestration.permission_matrix`,
  `src.autopoietic.constitutional_gate` — see `DIRECTORY_CONTRACT.yaml`
  (`stubs_and_shims`, type `adapter`).
- Stdlib only otherwise (`os`, `uuid`, `pathlib`); `care` embeds its UF table
  (extracted from `docs/care/BRAZIL_SUPPORT_N_NE_CO.md`).

## Env vars

| Var | Default | Use |
|---|---|---|
| `OMNI_GATE_DB` | `/tmp/omni_coworker_gate.sqlite` | SQLite path for the `ConstitutionalGate` deliberation ledger |
| `OMNI_GATE_FAIL_CLOSED` | unset (fail-open) | `=1` makes a missing gate deny instead of allowing |

## Callers / Consumidores

`agents/code_agent.py::submit_patch`, `app.py::/safety/check`,
`app.py::/safety/care`. Debug/Analyst/Reviewer agents stay read-only and do
not traverse this plane.
