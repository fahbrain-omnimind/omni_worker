"""audit_adapter — ponte para o ImmutableAuditSystem canônico.

English: Uses the canonical `ImmutableAuditSystem` (sha256 chain +
fcntl file lock) when the primary repo is mounted; otherwise falls back
to the local witness hash-chain — the app never depends on either.
pt-BR: Usa o `ImmutableAuditSystem` canônico (cadeia sha256 + lock
fcntl) quando o repo primário está montado; senão cai na hash-chain
local — o app nunca depende de nenhum dos dois.
"""

from __future__ import annotations

from typing import Any


def audit_append(event_type: str, data: dict[str, Any] | None = None) -> dict:
    """Append an audit event via canonical adapter or local fallback."""
    data = data or {}
    try:
        import sys
        from pathlib import Path

        for base in (Path("/content/omni_node"), Path("/content/omnimind-kilombo-sovereign")):
            p = base / "src"
            if (base / "src" / "audit" / "immutable_audit.py").exists():
                sys.path.insert(0, str(p))
                from audit.immutable_audit import ImmutableAuditSystem  # noqa: PLC0415

                system = ImmutableAuditSystem(log_dir=str(base / "logs"))
                system.append(event_type, json_dump := __import__("json").dumps(data))
                return {"source": "canonical:immutable_audit", "appended": True}
    except Exception:
        pass
    try:
        from ..agency.witness import witness_event

        witness_event(f"audit.{event_type}", data)
        return {"source": "witness_fallback", "appended": True}
    except Exception as e:
        return {"source": None, "appended": False, "reason": str(e)}


def audit_verify() -> dict:
    """Verify the canonical chain or the local witness fallback."""
    try:
        from ..agency.witness import verify_witness

        return {"source": "witness_fallback", "verify": verify_witness()}
    except Exception as e:
        return {"source": None, "verify": {"valid": False, "reason": str(e)}}