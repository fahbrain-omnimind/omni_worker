# safety/ — Governance plane (plano de segurança)

English: Permission matrix + constitutional gate + workspace jail. This is the
enforcement side of the "executive prosthesis" policy: agents diagnose read-only,
and code/config mutation only passes through `check_permission` (trust-gated) and
`evaluate_action` (constitutional deliberation).

pt-BR: Matriz de permissões + portão constitucional + jail do workspace. É o lado
coercitivo da política de "prótese executiva": agentes diagnosticam somente-leitura,
e mutação de código/config só passa por `check_permission` (gateado por trust) e
`evaluate_action` (deliberação constitucional).

## Files / Arquivos

| File | Role | Key API |
|---|---|---|
| `__init__.py` | Package surface | re-exports `matrix`, `gate`, `jail` + all public functions |
| `matrix.py` | **Adapter** → `src.orchestration.permission_matrix.PermissionMatrix` (omni_node) | `get_matrix()`, `check_permission(action, context)` |
| `gate.py` | **Adapter** → `src.autopoietic.constitutional_gate` (omni_node) | `get_gate()` (lazy singleton), `evaluate_action(action, context)` |
| `jail.py` | Standalone workspace sandbox (no canonical dep) | `is_safe(cmd)`, `is_command_safe(cmd)`, `validate_path(path)` |

## Control flow / Fluxo

```
CodeAgent.submit_patch(code, test_results, target_files)     agents/code_agent.py
  ├─ refuses: empty_diff | tests_failing | no_tests_passed
  ├─ check_permission("modify_code", {"trust_level": trust})  ← matrix.py
  └─ evaluate_action("submit_patch", {proponent, target_files, content[:4000]})
                                                              ← gate.py
```

`GET /safety/check?action=...` (app.py) exposes both verdicts for introspection:
`{"action", "matrix": bool, "gate": {...}}`.

## Behavior / Comportamento

- `check_permission` — canonical path calls `PermissionMatrix.can_execute(action,
  emergency=…, trust_level=…)`; **standalone fallback** (no omni_node on
  PYTHONPATH) mirrors the policy: `read_*`/search/inspect/list/communicate are
  free; `modify_code` requires `trust_level ≥ 0.8`, `modify_config` ≥ 0.9,
  everything else ≥ 1.0. Note: if the canonical matrix raises, it fails **open**
  (returns `True`) — the gate is the second line of defense.
- `evaluate_action` — wraps the action in a `ChangePayload` (uuid, proponent,
  intent, target_files, diff_or_content≤4000 chars, context) and calls
  `gate.evaluate()`; the `DeliberationCertificate` verdict maps to
  `allowed = verdict in ("EXECUTE", "TEACH")` (`REFUSE` → denied). Returns
  `{allowed, verdict, grade, reason}`. Gate unavailable → `{"allowed": True,
  "reason": "no_gate"}`; gate raises → `allowed: False, reason: "gate_error: …"`.
- `jail` — pure-Python denylist checks: `is_command_safe` blocks fork bombs,
  `rm -rf /`, `mkfs`, `dd if=/dev/zero`, `curl|sh`, `eval $(`, `nc -l`, etc.;
  `validate_path` blocks `..` traversal, `/etc/passwd`, `/root/.ssh`, and
  absolute paths outside `/content/` and `/tmp/`.

## Dependencies / Dependências

- Optional (omni_node via `PYTHONPATH`): `src.orchestration.permission_matrix`,
  `src.autopoietic.constitutional_gate` — see `DIRECTORY_CONTRACT.yaml`
  (`stubs_and_shims`, type `adapter`).
- Stdlib only otherwise (`os`, `uuid`, `pathlib`).

## Env vars

| Var | Default | Use |
|---|---|---|
| `OMNI_GATE_DB` | `/tmp/omni_coworker_gate.sqlite` | SQLite path for the `ConstitutionalGate` deliberation ledger |

## Callers / Consumidores

`agents/code_agent.py::submit_patch`, `app.py::/safety/check`. Debug/Analyst/
Reviewer agents stay read-only and do not traverse this plane.
