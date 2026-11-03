"""Tests for gate re-initialization reset."""

from __future__ import annotations

from omni_coworker.safety import gate


class _OkGate:
    def __init__(self, db_path=None):
        self.db_path = db_path


def test_gate_failed_resets_on_success(monkeypatch):
    gate._GATE = None
    gate._GATE_FAILED = True
    monkeypatch.setattr(gate, "ConstitutionalGate", _OkGate)
    g = gate.get_gate()
    assert g is not None
    assert gate._GATE_FAILED is False


def test_gate_failed_stays_on_failure(monkeypatch):
    gate._GATE = None
    gate._GATE_FAILED = False

    def _boom(db_path=None):
        raise RuntimeError("nope")

    monkeypatch.setattr(gate, "ConstitutionalGate", _boom)
    assert gate.get_gate() is None
    assert gate._GATE_FAILED is True
