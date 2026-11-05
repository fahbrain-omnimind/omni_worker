"""
omni_coworker.security.tool_guard
==================================
Tool Call Pre-Execution Guard for Autonomous Coding Agents (Gemma-4 Developer Agent).

Provides defense-in-depth pre-execution sanitization, invariant validation, and adversarial
payload interception before tool arguments are dispatched to the operating system shell.

Key capabilities:
1. Structural Command Denylist: Intercepts destructive Linux primitives (rm -rf, mkfs, dd, fork bombs).
2. Malicious Chaining & Suffix Detection: Unmasks hidden payloads across shell separators (;, &&, ||, |, eval).
3. Base64 & Hex Payload Unmasking: Integrates scan_and_decode_payloads from adversarial_detector.
4. Workspace Confinement: Restricts write/delete mutations strictly to /workspace and /tmp.
5. Harness Integrity Protection: Blocks unauthorized tampering of pytest.ini, conftest.py, and .git.
"""
from __future__ import annotations

import os
import re
import shlex
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from omni_coworker.security.adversarial_detector import scan_and_decode_payloads


class GuardVerdict(Enum):
    ALLOWED = "ALLOWED"
    BLOCKED = "BLOCKED"


@dataclass
class GuardResult:
    verdict: GuardVerdict
    rule_violated: Optional[str] = None
    reason: Optional[str] = None
    decoded_payloads: List[str] = field(default_factory=list)
    sanitized_command: Optional[str] = None

    @property
    def is_blocked(self) -> bool:
        return self.verdict == GuardVerdict.BLOCKED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "verdict": self.verdict.value,
            "blocked": self.is_blocked,
            "rule_violated": self.rule_violated,
            "reason": self.reason,
            "decoded_payloads": self.decoded_payloads,
            "sanitized_command": self.sanitized_command,
        }


class ToolCallPreExecutionGuard:
    """Pre-Execution Guard intercepting tool calls prior to execution."""

    # Destructive patterns that must never be dispatched to the shell
    DESTRUCTIVE_PATTERNS = [
        (r"\brm\s+(?:-[a-zA-Z0-9_-]*\s+)*-[a-zA-Z0-9_-]*r[a-zA-Z0-9_-]*f[a-zA-Z0-9_-]*\s+/\*|\brm\s+(?:-[a-zA-Z0-9_-]+\s+)*-[a-zA-Z0-9_-]*f[a-zA-Z0-9_-]*r[a-zA-Z0-9_-]*\s+/\*|\brm\s+-[a-zA-Z0-9_-]*r[a-zA-Z0-9_-]*\s+-[a-zA-Z0-9_-]*f[a-zA-Z0-9_-]*\s+/\*", "DESTRUCTIVE_RM_ROOT_GLOB", "Tentativa de remoção de todos os arquivos sob a raiz (rm -rf /*)"),
        (r"\brm\s+(?:-[a-zA-Z0-9_-]*\s+)*-[a-zA-Z0-9_-]*r[a-zA-Z0-9_-]*f[a-zA-Z0-9_-]*\s+/(?:\s|$)|\brm\s+(?:-[a-zA-Z0-9_-]+\s+)*-[a-zA-Z0-9_-]*f[a-zA-Z0-9_-]*r[a-zA-Z0-9_-]*\s+/(?:\s|$)|\brm\s+-[a-zA-Z0-9_-]*r[a-zA-Z0-9_-]*\s+-[a-zA-Z0-9_-]*f[a-zA-Z0-9_-]*\s+/(?:\s|$)", "DESTRUCTIVE_RM_ROOT", "Tentativa de remoção recursiva forçada da raiz (rm -rf /)"),
        (r"\brm\s+(?:-[a-zA-Z0-9_-]+\s+)*.*(?:\.git)(?:/|\s|$)", "GIT_METADATA_DESTRUCTION", "Destruição do repositório de controle de versão (.git)"),
        (r"\brm\s+(?:-[a-zA-Z0-9_-]+\s+)*(?:~|\$HOME)(?:/|\s|$)", "HOME_DESTRUCTION", "Tentativa de apagar o diretório HOME"),
        (r"\bmkfs(?:\.[a-z0-9]+)?\b", "FILESYSTEM_FORMAT", "Formatação de sistema de arquivos (mkfs)"),
        (r"\bdd\s+if=.*of=/dev/", "RAW_DEVICE_OVERWRITE", "Escrita direta em dispositivo de bloco (/dev)"),
        (r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:", "FORK_BOMB", "Detecção de fork bomb clássico"),
        (r"\b(?:wipefs|shred)\s+(?:/dev/|-f)", "STORAGE_SHRED", "Comando de destruição segura de armazenamento (wipefs/shred)"),
        (r"\bchmod\s+-[a-zA-Z]*R[a-zA-Z]*\s+777\s+/", "PERMISSIVE_CHMOD_ROOT", "Permissão global recursiva na raiz (chmod -R 777 /)"),
    ]

    # Protected files whose modification by executor is forbidden by competition rules
    PROTECTED_FILES = {
        "pytest.ini",
        "conftest.py",
        "tox.ini",
        ".gitlab-ci.yml",
        ".github/workflows",
    }

    # Forbidden path targets outside sandbox boundaries
    DISALLOWED_PATH_PREFIXES = [
        "/etc",
        "/usr",
        "/bin",
        "/sbin",
        "/lib",
        "/lib64",
        "/proc",
        "/sys",
        "/boot",
        "/root",
    ]

    def __init__(self, workspace_root: str = "/workspace"):
        self.workspace_root = os.path.abspath(workspace_root)

    def inspect_command(self, command: str) -> GuardResult:
        """Avalia um comando shell antes do despacho para ctx.docker.exec."""
        if not command or not command.strip():
            return GuardResult(verdict=GuardVerdict.ALLOWED, sanitized_command=command)

        raw_cmd = command.strip()

        # 1. Unmasking de Cifras e Payloads Ocultos (Base64 / Hex)
        decoded_payloads = scan_and_decode_payloads(raw_cmd)
        texts_to_check = [raw_cmd] + decoded_payloads

        for text in texts_to_check:
            # 2. Verificação de Padrões Destrutivos
            for pattern, rule_id, description in self.DESTRUCTIVE_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    return GuardResult(
                        verdict=GuardVerdict.BLOCKED,
                        rule_violated=rule_id,
                        reason=description,
                        decoded_payloads=decoded_payloads,
                    )

            # 3. Chaining malicioso com interprete de shell oculto
            malicious_chains = [
                (r"\|\s*(?:bash|sh|zsh)\s*$", "PIPE_TO_SHELL", "Redirecionamento inseguro de pipe para shell"),
                (r"\bbase64\s+-d\s*\|\s*(?:bash|sh)\b", "BASE64_EXEC_CHAIN", "Execução arbitrária de payload Base64 via pipe"),
                (r"\beval\s+\$\(base64", "EVAL_BASE64", "Avaliação dinâmica de Base64 embutido"),
                (r"\bcurl\s+[^|]+\|\s*(?:bash|sh)\b", "CURL_PIPE_BASH", "Download e execução remota não autorizada"),
                (r"\bwget\s+[^|]+\|\s*(?:bash|sh)\b", "WGET_PIPE_BASH", "Download e execução remota não autorizada"),
            ]
            for pattern, rule_id, description in malicious_chains:
                if re.search(pattern, text, re.IGNORECASE):
                    return GuardResult(
                        verdict=GuardVerdict.BLOCKED,
                        rule_violated=rule_id,
                        reason=description,
                        decoded_payloads=decoded_payloads,
                    )

        # 4. Verificação de Arquivos Protegidos (tampering prevention)
        for protected in self.PROTECTED_FILES:
            # Detecta comandos que tentam remover, sobreescrever ou redirecionar para arquivos de teste/config
            tamper_pattern = rf"(?:\b(?:rm|mv|cp|sed\s+-i|truncate)\b|>>?)\s*.*?\b{re.escape(protected)}\b"
            if re.search(tamper_pattern, raw_cmd):
                return GuardResult(
                    verdict=GuardVerdict.BLOCKED,
                    rule_violated="PROTECTED_FILE_TAMPERING",
                    reason=f"Tentativa de alteração não autorizada no arquivo protegido '{protected}'",
                    decoded_payloads=decoded_payloads,
                )

        return GuardResult(
            verdict=GuardVerdict.ALLOWED,
            decoded_payloads=decoded_payloads,
            sanitized_command=raw_cmd,
        )

    def inspect_file_mutation(self, tool_name: str, file_path: str) -> GuardResult:
        """Avalia mutações de arquivos (write_file, edit_file) quanto a caminhos protegidos."""
        norm_path = os.path.normpath(file_path)

        # 1. Bloqueio de arquivos protegidos da infraestrutura de teste
        base_name = os.path.basename(norm_path)
        if base_name in self.PROTECTED_FILES:
            return GuardResult(
                verdict=GuardVerdict.BLOCKED,
                rule_violated="PROTECTED_FILE_MUTATION",
                reason=f"Mutação direta de '{base_name}' é bloqueada para preservar integridade da avaliação.",
            )

        # 2. Bloqueio de caminhos de sistema fora de /workspace e /tmp
        if norm_path.startswith("/"):
            is_in_workspace = norm_path.startswith(self.workspace_root)
            is_in_tmp = norm_path.startswith("/tmp")
            if not (is_in_workspace or is_in_tmp):
                for prefix in self.DISALLOWED_PATH_PREFIXES:
                    if norm_path.startswith(prefix):
                        return GuardResult(
                            verdict=GuardVerdict.BLOCKED,
                            rule_violated="DISALLOWED_SYSTEM_PATH",
                            reason=f"Caminho '{file_path}' está fora do workspace autorizado ({self.workspace_root}).",
                        )

        return GuardResult(verdict=GuardVerdict.ALLOWED)
