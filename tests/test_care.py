"""Hermetic tests for omni_coworker.safety.care.escalate.

English: Hermetic tests for the territorial escalation care path.
pt-BR: Testes hermeticos para o caminho de escalada territorial de cuidado.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


def test_escalate_known_uf() -> None:
    """Escalate with a known UF (Amazonas) returns region-specific resources."""
    from omni_coworker.safety.care import escalate

    result = escalate("síndrome do pânico", state_uf="AM", age=30)
    assert result["level"] in {"L1", "L2", "L3", "L4"}
    resources = result["resources"]
    assert "caps" in resources
    assert "samu" in resources
    assert "cvv" in resources
    assert "crp" in resources


def test_escalate_minor_age_branch() -> None:
    """Minor age (< 18) includes CAPS-II and família references."""
    from omni_coworker.safety.care import escalate

    result = escalate("tristeza profunda", state_uf="PE", age=15)
    assert result["level"] in {"L1", "L2", "L3", "L4"}
    referral = result["referral_text"]
    assert "menor" in referral.lower() or "15" in referral or "CAPS-II" in referral


def test_escalate_unknown_uf_fallback_national() -> None:
    """Unknown UF falls back to national resources (CVV 188, Disque-100, SAMU 192)."""
    from omni_coworker.safety.care import escalate

    result = escalate("crise emocional", state_uf="XX", age=25)
    resources = result["resources"]
    cvv_has_national = any("188" in str(r) for r in resources.get("cvv", []))
    assert cvv_has_national, "Unknown UF must fall back to national CVV 188"
    assert "disque_100" in resources or any("100" in str(r) for r in resources.values())


def test_escalate_emergency_level() -> None:
    """Severe reason (suicide) triggers L4 emergency level."""
    from omni_coworker.safety.care import escalate

    result = escalate("pensamentos suicidas", state_uf="RN", age=40)
    assert result["level"] == "L4"
    resources = result["resources"]
    assert "samu" in resources


def test_escalate_depression_level() -> None:
    """Moderate reason (depression) triggers L2 level."""
    from omni_coworker.safety.care import escalate

    result = escalate("depressão severa há meses", state_uf="BA", age=28)
    assert result["level"] == "L2"
    assert "caps" in result["resources"]


def test_escalate_bilingual_docstrings() -> None:
    """Module docstrings contain both English and pt-BR text."""
    from omni_coworker.safety import care

    doc = care.__doc__ or ""
    assert "Territorial escalation" in doc or "escalation territoriale" in doc.lower() or "Territorial" in doc
    assert "Mental-health" in doc or "saúde mental" in doc.lower()


def test_app_route_returns_dict() -> None:
    """The /safety/care FastAPI route returns a dict with expected keys."""
    from fastapi.testclient import TestClient
    from omni_coworker.app import create_app

    app = create_app()
    client = TestClient(app)
    resp = client.get("/safety/care?reason=ansiedade&state_uf=GO&age=22")
    assert resp.status_code == 200
    body = resp.json()
    assert "level" in body
    assert "resources" in body
    assert "referral_text" in body