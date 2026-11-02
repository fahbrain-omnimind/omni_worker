"""Tests for store.audit_adapter (canonical immutable audit bridge)."""

from __future__ import annotations

from omni_coworker.store.audit_adapter import audit_append, audit_verify


def test_append_fallback_writes_witness():
    out = audit_append("test.event", {"k": 1})
    assert out["appended"] is True
    assert out["source"] in ("canonical:immutable_audit", "witness_fallback")


def test_verify_returns_valid_shape():
    v = audit_verify()
    assert v["source"] in ("witness_fallback", "canonical")
    assert "verify" in v