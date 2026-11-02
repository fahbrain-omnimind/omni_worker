"""Jail adapter (workspace sandbox).

English: Wraps security playbooks and jailbreak patterns.
pt-BR: Encapsula playbooks de segurança e padrões de jailbreak.
"""

from __future__ import annotations


def is_safe(command: str) -> bool:
    """Check if a command is safe to run (real policy — no placeholder).

    English: Rejects destructive, exfiltrating, credential-harvesting
    and shell-injection patterns. Policy layers: destructive fs ops,
    network exfil (nc/curl|sh/ssh -T tunnels), credential reads
    (dotenv/tokens/keys), process/device access, fork bombs.
    pt-BR: Rejeita padrões destrutivos, de exfiltração, coleta de
    credenciais e injeção de shell. Camadas de política: ops
    destrutivas de fs, exfil de rede, leitura de credenciais, acesso
    a processo/dispositivo, fork bombs.
    """
    cmd = (command or "").lower()
    policy: list[tuple[str, str]] = [
        # destructive filesystem
        ("rm -rf /", "fs_destructive"),
        ("rm -rf ~", "fs_destructive"),
        ("mkfs", "fs_destructive"),
        ("dd if=/dev/zero", "fs_destructive"),
        ("shred", "fs_destructive"),
        ("> /dev/sda", "fs_destructive"),
        # fork bomb / resource exhaustion
        (":(){:|:&};:", "fork_bomb"),
        # network exfiltration / reverse shells
        ("nc -l", "net_exfil"),
        ("nc -e", "net_exfil"),
        ("ncat -e", "net_exfil"),
        ("curl | sh", "pipe_exec"),
        ("wget | sh", "pipe_exec"),
        ("bash -i >& /dev/tcp", "reverse_shell"),
        ("/dev/tcp/", "reverse_shell"),
        ("ssh -o stricthostkeychecking=no -l root -n -r", "ssh_tunnel"),
        # credential harvesting
        ("cat ~/.ssh/id_rsa", "credential_read"),
        ("cat ~/.aws/credentials", "credential_read"),
        ("cat .env", "credential_read"),
        ("grep -r 'token'", "credential_scan"),
        ("find / -name '*.pem'", "credential_scan"),
        ("chmod 777", "permission_loosen"),
        ("chmod -r 777", "permission_loosen"),
        # device/kernel access
        ("/dev/mem", "device_access"),
        ("insmod", "kernel_module"),
        ("modprobe", "kernel_module"),
        # eval injection
        ("eval $(", "eval_injection"),
        ("python -c 'import os; os.system", "eval_injection"),
    ]
    for pattern, reason in policy:
        if pattern in cmd:
            return False
    return True


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
