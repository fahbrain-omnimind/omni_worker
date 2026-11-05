"""audit_adapter — ponte para o ImmutableAuditSystem canônico.

English: Appends audit events to the worker-owned canonical
`ImmutableAuditSystem` (sha256 chain + fcntl lock, anchored at
OMNI_STATE_DIR/audit). When the audit write itself fails, falls back
to the witness hash-chain — the caller never depends on either.
pt-BR: Anexa eventos de auditoria ao `ImmutableAuditSystem` canônico
do próprio worker (cadeia sha256 + lock fcntl, ancorado em
OMNI_STATE_DIR/audit). Se a escrita de auditoria falhar, cai na
hash-chain do witness — o chamador nunca depende de nenhum dos dois.
"""

from __future__ import annotations

from typing import Any


def audit_append(event_type: str, data: dict[str, Any] | None = None) -> dict:
    """Append an audit event via the canonical chain or witness fallback."""
    data = data or {}
    try:
        from ..audit import get_audit

        h = get_audit().log_action(event_type, dict(data))
        return {"source": "canonical:immutable_audit", "appended": True,
                "hash": h}
    except Exception as e:  # noqa: BLE001
        canonical_err = str(e)
    try:
        from ..agency.witness import witness_event

        witness_event(f"audit.{event_type}", data)
        return {"source": "witness_fallback", "appended": True,
                "canonical_error": canonical_err}
    except Exception as e:  # noqa: BLE001
        return {"source": None, "appended": False,
                "reason": str(e), "canonical_error": canonical_err}


def audit_verify() -> dict:
    """Verify the audit chain (canonical first, witness fallback)."""
    try:
        from ..audit import get_audit

        return {"source": "canonical",
                "verify": get_audit().verify_chain_integrity()}
    except Exception:  # noqa: BLE001, S110
        pass
    try:
        from ..agency.witness import verify_witness

        return {"source": "witness_fallback", "verify": verify_witness()}
    except Exception as e:  # noqa: BLE001
        return {"source": None, "verify": {"valid": False, "reason": str(e)}}
