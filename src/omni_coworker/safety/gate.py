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


def _apply_refusal_contract(result: dict, action: str,
                            context: dict | None) -> dict:
    """Apply the sovereign refusal contract onto a gate result.

    English: hard_refusal → allowed=False (hard_refusal_tag /
    hard_interrupt); homeostatic_refusal → cooldown flag; contract errors
    fail open except when hard tags are detected.
    pt-BR: aplica o contrato de recusa sobre o resultado do gate —
    recusa rígida bloqueia, recusa homeostática marca cooldown; erro do
    contrato é fail-open exceto com tags duras.
    """
    ctx = context or {}
    try:
        from . import refusal_contract as rc

        assessment = rc.classify_refusal_context(
            request_tags=ctx.get("tags", ctx.get("request_tags")),
            psi=ctx.get("psi"),
            epsilon=ctx.get("epsilon"),
            ogum_active=bool(ctx.get("ogum_active", False)),
            thermal_block_risk=bool(ctx.get("thermal_block_risk", False)),
            exfiltration_verdict=ctx.get("exfiltration_verdict"),
        )
    except Exception:
        try:
            from . import refusal_contract as rc

            tags = rc._normalize_tags(ctx.get("tags", ctx.get("request_tags")))
            if tags & rc.HARD_REFUSAL_TAGS:
                result["allowed"] = False
                result["reason"] = "hard_refusal_tag"
        except Exception:
            pass
        return result

    is_hard = assessment.get("state") == "hard_refusal"
    is_cooldown = assessment.get("state") == "homeostatic_refusal"
    if is_hard:
        result["allowed"] = False
        result["reason"] = ("hard_refusal_tag"
                            if assessment.get("hard_refusal_hits")
                            else "hard_interrupt")
    elif is_cooldown:
        result["cooldown"] = True
    result["refusal_contract"] = assessment
    if is_hard or is_cooldown:
        try:
            from .refusal_state import record_verdict

            record_verdict(result["allowed"], {"source": "refusal_contract",
                                               "action": action,
                                               "assessment": assessment})
        except Exception:
            pass
    return result


def evaluate_action(action: str, context: dict | None = None) -> dict:
    """Evaluate action through constitutional gate.

    English: Wraps the action in a ChangePayload and maps the
    DeliberationCertificate verdict (EXECUTE/TEACH/REFUSE), then applies
    the refusal contract.
    pt-BR: Encapsula a ação num ChangePayload, mapeia o veredito do
    DeliberationCertificate (EXECUTE/TEACH/REFUSE) e aplica o contrato
    de recusa.
    """
    gate = get_gate()
    if gate is None or ChangePayload is None:
        fail_closed = os.getenv("OMNI_GATE_FAIL_CLOSED") == "1"
        result = {"allowed": not fail_closed,
                  "reason": "no_gate_fail_closed" if fail_closed else "no_gate"}
        result = _apply_refusal_contract(result, action, context)
        try:
            from .refusal_state import record_verdict

            record_verdict(result["allowed"], {"source": "gate",
                                               "action": action,
                                               "verdict": "no_gate"})
        except Exception:
            pass
        return result
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
        result = {
            "allowed": allowed,
            "verdict": verdict,
            "grade": getattr(cert, "grade", None),
            "reason": getattr(cert, "justification", ""),
        }
        return _apply_refusal_contract(result, action, context)
    except Exception as e:
        try:
            from .refusal_state import record_verdict

            record_verdict(False, {"source": "gate", "action": action,
                                   "verdict": "gate_error"})
        except Exception:
            pass
        return {"allowed": False, "reason": f"gate_error: {e}"}
