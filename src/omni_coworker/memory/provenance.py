"""memory.provenance — MINJA memory provenance guard.

Provides a small, fail-open guard for persistent write-paths:
  - provenance_signature(content, source)
  - classify_trust(source, namespace)
  - quarantine_check(content) -> {quarantine, reasons}
"""
from __future__ import annotations

import hashlib
from typing import Any

_KNOWN_INSTANCES = {"analyst", "executor", "devin", "kilo"}

_INJECTION_PATTERNS = (
    "ignore previous",
    "system:",
    " instructions:",
)


def provenance_signature(content: Any, source: Any) -> str:
    try:
        raw = (str(content) + "|" + str(source)).encode("utf-8", errors="replace")
    except Exception:
        raw = b""
    return hashlib.sha256(raw).hexdigest()


def classify_trust(source: Any, namespace: Any) -> str:
    try:
        src = str(source or "").strip().lower()
        ns = str(namespace or "").strip().lower()
        if src in _KNOWN_INSTANCES:
            return "verified_agent"
        if ns in ("user", "interaction"):
            return "user_input"
        if ns == "document" or src.startswith("doc"):
            return "external_doc"
        return "unknown"
    except Exception:
        return "unknown"


def quarantine_check(content: Any) -> dict[str, Any]:
    try:
        reasons: list[str] = []
        if isinstance(content, (bytes, bytearray)):
            try:
                text = content.decode("utf-8")
            except Exception:
                reasons.append("non_utf8_bytes")
                text = content.decode("utf-8", errors="replace")
        else:
            text = "" if content is None else str(content)
        if len(text.encode("utf-8", errors="replace")) > 50 * 1024:
            reasons.append("oversize")
        low = text.lower()
        for pat in _INJECTION_PATTERNS:
            if pat in low:
                reasons.append(f"injection_pattern:{pat.strip()}")
        uniq = list(dict.fromkeys(reasons))
    except Exception:
        uniq = ["guard_error"]
    return {"quarantine": bool(uniq), "reasons": uniq}
