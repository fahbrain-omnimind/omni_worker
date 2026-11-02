"""Constitutional gate adapter.

English: Reuses src.autopoietic.constitutional_gate.ConstitutionalGate.
pt-BR: Reutiliza src.autopoietic.constitutional_gate.ConstitutionalGate.
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path

try:
    from src.autopoietic.constitutional_gate import (
        ChangePayload,
        ConstitutionalGate,
    )
except Exception:  # pragma: no cover
    ConstitutionalGate = None  # type: ignore
    ChangePayload = None  # type: ignore

_GATE = None
_GATE_FAILED = False


def get_gate():
    """Return a constitutional gate instance.

    English: Lazy singleton factory for ConstitutionalGate.
    pt-BR: Fábrica singleton lazy para ConstitutionalGate.
    """
    global _GATE, _GATE_FAILED
    if ConstitutionalGate is None or _GATE_FAILED:
        return None
    if _GATE is None:
        try:
            db_path = Path(os.getenv("OMNI_GATE_DB", "/tmp/omni_coworker_gate.sqlite"))
            _GATE = ConstitutionalGate(db_path=db_path)
        except Exception:
            _GATE_FAILED = True
            return None
    return _GATE


def evaluate_action(action: str, context: dict | None = None) -> dict:
    """Evaluate action through constitutional gate.

    English: Wraps the action in a ChangePayload and maps the
    DeliberationCertificate verdict (EXECUTE/TEACH/REFUSE).
    pt-BR: Encapsula a ação num ChangePayload e mapeia o veredito do
    DeliberationCertificate (EXECUTE/TEACH/REFUSE).
    """
    gate = get_gate()
    if gate is None or ChangePayload is None:
        return {"allowed": True, "reason": "no_gate"}
    context = context or {}
    try:
        change = ChangePayload(
            change_id=str(uuid.uuid4()),
            proponent=context.get("proponent", "omni_coworker"),
            intent=action,
            target_files=list(context.get("target_files", [])),
            diff_or_content=str(context.get("content", action)),
            context=dict(context),
        )
        cert = gate.evaluate(change)
        verdict = getattr(cert, "verdict", "REFUSE")
        return {
            "allowed": verdict in ("EXECUTE", "TEACH"),
            "verdict": verdict,
            "grade": getattr(cert, "grade", None),
            "reason": getattr(cert, "justification", ""),
        }
    except Exception as e:
        return {"allowed": False, "reason": f"gate_error: {e}"}
