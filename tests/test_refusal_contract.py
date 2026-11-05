"""Tests for refusal contract port (OW)."""

from __future__ import annotations

import pytest

from omni_coworker.safety import gate
from omni_coworker.safety import refusal_contract as rc


@pytest.fixture()
def st(tmp_path, monkeypatch):
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))
    return tmp_path


def test_hard_tags_interrupt():
    out = rc.classify_refusal_context(request_tags=["war"])
    assert out["action"] == "interrupt_and_refuse"
    assert out["state"] == "hard_refusal"


def test_epsilon_0_96_hard_interrupt():
    out = rc.classify_refusal_context(epsilon=0.96)
    assert out["action"] == "interrupt_and_refuse"


def test_epsilon_0_92_cooldown():
    out = rc.classify_refusal_context(epsilon=0.92)
    assert out["action"] == "cooldown_and_reduce_external_polling"
    assert out["state"] == "homeostatic_refusal"


def test_soft_tags_cooldown():
    out = rc.classify_refusal_context(request_tags=["intrusion"])
    assert out["action"] == "cooldown_and_reduce_external_polling"


def test_no_tags_low_epsilon_proceed():
    out = rc.classify_refusal_context(epsilon=0.1)
    assert out["action"] == "allow_with_boundaries"
    assert out["state"] == "allowed_with_contract"


def test_gate_integration_hard_tags(st, monkeypatch):
    monkeypatch.delenv("OMNI_GATE_FAIL_CLOSED", raising=False)
    out = gate.evaluate_action("submit_patch", {"tags": ["war"]})
    assert out["allowed"] is False
    assert out["reason"] == "hard_refusal_tag"


def test_gate_cooldown_flag(st, monkeypatch):
    monkeypatch.delenv("OMNI_GATE_FAIL_CLOSED", raising=False)
    out = gate.evaluate_action("submit_patch", {"epsilon": 0.92})
    assert out["allowed"] is True
    assert out.get("cooldown") is True


def test_fail_open_contract_error(st, monkeypatch):
    # force contract to raise
    monkeypatch.setattr(rc, "classify_refusal_context", lambda **k: (_ for _ in ()).throw(RuntimeError("boom")))
    out = gate.evaluate_action("submit_patch", {"epsilon": 0.1})
    assert out["allowed"] is True
