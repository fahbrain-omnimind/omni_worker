"""Persistence tests for governance (trust/quarantine) and witness."""
import json

import pytest

from omni_coworker.agency import witness as W
from omni_coworker.orchestration.governance import QuarantineSystem, TrustSystem


@pytest.fixture(autouse=True)
def _state(tmp_path, monkeypatch):
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))
    yield


def test_trust_persists_between_instances(tmp_path):
    ts = TrustSystem()
    ts.set_trust("CodeAgent", 0.9)
    ts.record_event("tests_passed", "CodeAgent")

    ts2 = TrustSystem()
    # record_event: 0.9 + 0.1 capped -> 1.0
    assert ts2.get_trust("CodeAgent") == pytest.approx(1.0)


def test_trust_event_appended_to_jsonl(tmp_path):
    ts = TrustSystem()
    ts.record_event("review_dissent", "CodeAgent")

    events_path = tmp_path / "trust_events.jsonl"
    assert events_path.exists()
    lines = events_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    rec = json.loads(lines[0])
    assert rec["event"] == "review_dissent"
    assert rec["agent"] == "CodeAgent"


def test_trust_unknown_defaults_half(tmp_path):
    # fail-closed: no file -> default
    ts = TrustSystem()
    assert ts.get_trust("UnknownAgent") == pytest.approx(0.5)


def test_trust_io_failure_fail_open(tmp_path, monkeypatch):
    # make state dir unwritable by pointing to a file
    bad = tmp_path / "notadir"
    bad.write_text("x")
    monkeypatch.setenv("OMNI_STATE_DIR", str(bad))
    # should not raise
    ts = TrustSystem()
    ts.set_trust("CodeAgent", 0.7)
    assert ts.get_trust("CodeAgent") == pytest.approx(0.7)


def test_quarantine_persists(tmp_path):
    q = QuarantineSystem()
    q.quarantine("c1", "reason")
    q2 = QuarantineSystem()
    assert q2.is_quarantined("c1")


def test_witness_honors_state_dir(tmp_path):
    W.witness_event("alpha", {"x": 1})
    p = tmp_path / "witness.jsonl"
    assert p.exists()
    records = W.read_witness()
    assert len(records) == 1
    assert records[0]["type"] == "alpha"


def test_witness_explicit_path_overrides(tmp_path, monkeypatch):
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path / "state"))
    custom = tmp_path / "custom.jsonl"
    W.witness_event("beta", {"y": 2}, path=str(custom))
    assert custom.exists()
    assert not (tmp_path / "state" / "witness.jsonl").exists()
