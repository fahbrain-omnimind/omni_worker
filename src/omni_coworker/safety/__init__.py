"""Safety plane: permission matrix, constitutional gate, jail adapter.

English: Composes permission matrix + constitutional gate + security.
pt-BR: Compõe matriz de permissões + portão constitucional + segurança.
"""

from __future__ import annotations

from . import matrix, gate, jail, refusal_contract
from .matrix import get_matrix, check_permission
from .gate import get_gate, evaluate_action
from .jail import is_safe, is_command_safe, validate_path
from .refusal_contract import classify_refusal_context

__all__ = ["matrix", "gate", "jail", "refusal_contract", "get_matrix", "check_permission", "get_gate", "evaluate_action", "is_safe", "is_command_safe", "validate_path", "classify_refusal_context"]
