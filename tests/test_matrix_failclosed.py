"""Tests for matrix fail-closed behavior."""

from __future__ import annotations

from omni_coworker.safety import matrix


class _BoomMatrix:
    def can_execute(self, *a, **k):
        raise RuntimeError("boom")


def _boom(monkeypatch):
    monkeypatch.setattr(matrix, "get_matrix", lambda: _BoomMatrix())


def test_matrix_exception_fail_closed_default(monkeypatch):
    _boom(monkeypatch)
    monkeypatch.delenv("OMNI_GATE_FAIL_CLOSED", raising=False)
    assert matrix.check_permission("modify_code", {"trust_level": 1.0}) is False


def test_matrix_exception_fail_closed_one(monkeypatch):
    _boom(monkeypatch)
    monkeypatch.setenv("OMNI_GATE_FAIL_CLOSED", "1")
    assert matrix.check_permission("modify_code", {"trust_level": 1.0}) is False


def test_matrix_exception_lab_open(monkeypatch):
    _boom(monkeypatch)
    monkeypatch.setenv("OMNI_GATE_FAIL_CLOSED", "0")
    assert matrix.check_permission("modify_code", {"trust_level": 1.0}) is True
