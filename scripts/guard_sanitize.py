#!/usr/bin/env python3
"""Guard sanitizador — bloqueia commit com segredos (pre-commit opcional).

English: Scans staged files for high-signal secret patterns; exits 1
when found. Run manually or as pre-commit hook.
pt-BR: Varre arquivos staged por padrões de segredo de alto sinal;
exit 1 quando encontra. Rode manualmente ou como hook pre-commit.
"""

from __future__ import annotations

import re
import subprocess
import sys

PATTERNS = [
    re.compile(r"(ghp|gho|ghu|ghs|github_pat)_[A-Za-z0-9_]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
    re.compile(r"-----BEGIN (RSA|OPENSSH|EC|PRIVATE) KEY-----"),
    re.compile(r"HF_TOKEN\s*[=:]\s*\S+"),
    re.compile(r"(api[_-]?key|secret|password|token)\s*[=:]\s*[\"'][A-Za-z0-9_\-]{12,}[\"']", re.I),
    re.compile(r"AKIA[0-9A-Z]{16}"),
]

def main() -> int:
    staged = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "-z"], capture_output=True, text=True
    ).stdout.split("\0")
    files = [f for f in staged if f]
    if not files:
        return 0
    bad = []
    for f in files:
        try:
            content = open(f, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for pat in PATTERNS:
            if pat.search(content):
                bad.append(f)
                break
    if bad:
        print("[guard] SEGREDOS detectados em arquivos staged — bloqueado:")
        for f in bad:
            print(f"  - {f}")
        return 1
    print(f"[guard] OK: {len(files)} arquivos staged limpos.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
