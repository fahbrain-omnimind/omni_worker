"""Safety plane: permission matrix, constitutional gate, jail adapter.

English: Composes permission matrix + constitutional gate + security.
pt-BR: Compõe matriz de permissões + portão constitucional + segurança.
"""

from __future__ import annotations

from . import matrix, gate, jail
from .matrix import get_matrix, check_permission
from .gate import get_gate, evaluate_action
from .jail import is_safe, is_command_safe, validate_path

__all__ = ["matrix", "gate", "jail", "get_matrix", "check_permission", "get_gate", "evaluate_action", "is_safe", "is_command_safe", "validate_path"]
