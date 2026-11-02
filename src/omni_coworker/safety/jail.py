"""Jail adapter (workspace sandbox).

English: Wraps security playbooks and jailbreak patterns.
pt-BR: Encapsula playbooks de segurança e padrões de jailbreak.
"""

from __future__ import annotations


def is_safe(command: str) -> bool:
    """Check if a command is safe to run.

    English: Basic allowlist check (placeholder).
    pt-BR: Verificação básica de allowlist (placeholder).
    """
    blocked = ("rm -rf", "mkfs", ":(){:|:&};:")
    return not any(b in command for b in blocked)


def validate_path(path: str) -> bool:
    """Validate if path is safe.
    
    English: Checks for path traversal.
    pt-BR: Verifica path traversal.
    """
    import os
    # Block path traversal
    if ".." in path or path.startswith("/etc/passwd") or path.startswith("/root/.ssh"):
        return False
    # Block absolute paths outside workspace
    if os.path.isabs(path):
        # Allow /content paths
        if not (path.startswith("/content/") or path.startswith("/tmp/")):
            return False
    return True


def is_command_safe(command: str) -> bool:
    """Check if command is safe.
    
    English: Comprehensive command safety check.
    pt-BR: Verificação abrangente de segurança de comando.
    """
    if not command:
        return False
    dangerous_patterns = [
        "rm -rf /",
        "mkfs",
        ":(){:|:&};:",
        "dd if=/dev/zero",
        "curl | sh",
        "wget | sh",
        "eval $(",
        "nc -l",
        "python -c 'import os; os.system",
    ]
    cmd_lower = command.lower()
    for pattern in dangerous_patterns:
        if pattern in cmd_lower:
            return False
    return is_safe(command)
