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
    if ConstitutionalGate is None:
        return None
    if _GATE is not None:
        return _GATE
    try:
        db_path = Path(os.getenv("OMNI_GATE_DB", "/tmp/omni_coworker_gate.sqlite"))
        _GATE = ConstitutionalGate(db_path=db_path)
        _GATE_FAILED = False
        return _GATE
    except Exception:
        _GATE_FAILED = True
        _GATE = None
        return None


def evaluate_action(action: str, context: dict | None = None) -> dict:
    """Evaluate action through constitutional gate.

    English: Wraps the action in a ChangePayload and maps the
    DeliberationCertificate verdict (EXECUTE/TEACH/REFUSE).
    pt-BR: Encapsula a ação num ChangePayload e mapeia o veredito do
    DeliberationCertificate (EXECUTE/TEACH/REFUSE).
    """
    gate = get_gate()
    if gate is None or ChangePayload is None:
        fail_closed = os.getenv("OMNI_GATE_FAIL_CLOSED") == "1"
        return {"allowed": not fail_closed,
                "reason": "no_gate_fail_closed" if fail_closed else "no_gate"}
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
        allowed = verdict in ("EXECUTE", "TEACH")
        try:
            from .refusal_state import record_verdict

            record_verdict(allowed, {"source": "gate", "action": action,
                                     "verdict": verdict})
        except Exception:
            pass
        return {
            "allowed": allowed,
            "verdict": verdict,
            "grade": getattr(cert, "grade", None),
            "reason": getattr(cert, "justification", ""),
        }
    except Exception as e:
        try:
            from .refusal_state import record_verdict

            record_verdict(False, {"source": "gate", "action": action,
                                   "verdict": "gate_error"})
        except Exception:
            pass
        return {"allowed": False, "reason": f"gate_error: {e}"}
