"""Tests for gate fail-closed option (OMNI_GATE_FAIL_CLOSED)."""

from __future__ import annotations

import os

from omni_coworker.safety import gate


def _force_no_gate(monkeypatch):
    monkeypatch.setattr(gate, "get_gate", lambda: None)
    monkeypatch.setattr(gate, "ChangePayload", None)


def test_default_stays_open(monkeypatch):
    _force_no_gate(monkeypatch)
    monkeypatch.delenv("OMNI_GATE_FAIL_CLOSED", raising=False)
    assert gate.evaluate_action("submit_patch")["allowed"] is True


def test_fail_closed_blocks(monkeypatch):
    _force_no_gate(monkeypatch)
    monkeypatch.setenv("OMNI_GATE_FAIL_CLOSED", "1")
    out = gate.evaluate_action("submit_patch")
    assert out["allowed"] is False
    assert out["reason"] == "no_gate_fail_closed"


def test_fail_closed_zero_allows(monkeypatch):
    _force_no_gate(monkeypatch)
    monkeypatch.setenv("OMNI_GATE_FAIL_CLOSED", "0")
    assert gate.evaluate_action("submit_patch")["allowed"] is True