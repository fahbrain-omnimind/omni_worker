"""Safety plane: permission matrix, constitutional gate, jail adapter.

English: Composes permission matrix + constitutional gate + security.
pt-BR: Compõe matriz de permissões + portão constitucional + segurança.
"""

from __future__ import annotations

from . import gate, jail, matrix, pedagogical_refusal, refusal_contract
from .gate import evaluate_action, get_gate
from .jail import is_command_safe, is_safe, validate_path
from .matrix import check_permission, get_matrix
from .refusal_contract import classify_refusal_context

__all__ = ["check_permission", "classify_refusal_context", "evaluate_action", "gate", "get_gate", "get_matrix", "is_command_safe", "is_safe", "jail", "matrix", "pedagogical_refusal", "refusal_contract", "validate_path"]
