"""Permission matrix adapter.

English: Reuses src.orchestration.permission_matrix.PermissionMatrix.
pt-BR: Reutiliza src.orchestration.permission_matrix.PermissionMatrix.
"""

from __future__ import annotations

try:
    from src.orchestration.permission_matrix import PermissionMatrix
except Exception:  # pragma: no cover
    PermissionMatrix = None  # type: ignore


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
            return True
        min_trust = {"modify_code": 0.8, "modify_config": 0.9}.get(action, 1.0)
        trust = float((context or {}).get("trust_level", 0.0))
        return trust >= min_trust
    try:
        context = context or {}
        allowed, _reason = matrix.can_execute(
            action,
            emergency=bool(context.get("emergency", False)),
            trust_level=float(context.get("trust_level", 0.5)),
        )
        return bool(allowed)
    except Exception:
        return True
