"""Permission matrix adapter.

English: Reuses src.orchestration.permission_matrix.PermissionMatrix.
pt-BR: Reutiliza src.orchestration.permission_matrix.PermissionMatrix.
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

try:
    from src.orchestration.permission_matrix import PermissionMatrix
except Exception:  # noqa: BLE001  # pragma: no cover
    PermissionMatrix = None  # type: ignore


_READ_ONLY_ACTIONS = {
    "read_file", "search_files", "list_files", "inspect_context",
    "codebase_search", "list_code_definitions", "communicate_with_agent",
}


def get_matrix():
    """Return a permission matrix instance.

    English: Factory for PermissionMatrix.
    pt-BR: Fábrica para PermissionMatrix.
    """
    if PermissionMatrix is None:
        return None
    return PermissionMatrix()


def check_permission(action: str, context: dict | None = None) -> bool:
    """Check permission for an action.
    
    English: Checks against permission matrix.
    pt-BR: Verifica contra matriz de permissões.
    """
    matrix = get_matrix()
    if matrix is None:
        # Fallback standalone — espelha a política do canônico sem
        # depender dele: leitura livre, escrita exige trust mínimo.
        safe = {
            "read_file", "search_files", "list_files", "inspect_context",
            "codebase_search", "list_code_definitions", "communicate_with_agent",
        }
        if action in safe or action.startswith("read_"):
            allowed = True
        else:
            min_trust = {"modify_code": 0.8, "modify_config": 0.9}.get(action, 1.0)
            trust = float((context or {}).get("trust_level", 0.0))
            allowed = trust >= min_trust
        _record_matrix_verdict(allowed, action)
        return allowed
    try:
        context = context or {}
        allowed, _reason = matrix.can_execute(
            action,
            emergency=bool(context.get("emergency", False)),
            trust_level=float(context.get("trust_level", 0.5)),
        )
        allowed = bool(allowed)
        if (not allowed and "action_not_defined" in str(_reason)
                and (action in _READ_ONLY_ACTIONS or action.startswith("read_"))):
            # canônico não define ações de leitura: política local = leitura livre
            allowed = True
        _record_matrix_verdict(allowed, action)
        return allowed
    except Exception as e:  # noqa: BLE001
        logger.warning("permission matrix failed: %s", e)
        if os.getenv("OMNI_GATE_FAIL_CLOSED") == "0":
            # laboratório: fail-open explícito — o veredito ainda é
            # registrado (estava saindo da cadeia de evidência)
            _record_matrix_verdict(True, action)
            return True
        _record_matrix_verdict(False, action)
        return False


def _record_matrix_verdict(allowed: bool, action: str) -> None:
    try:
        from .refusal_state import record_verdict

        record_verdict(allowed, {"source": "matrix", "action": action})
    except Exception:  # noqa: BLE001, S110
        pass
