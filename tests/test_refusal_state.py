"""A5 — refusal_state transitions instrumentation."""
import json

import pytest


@pytest.fixture()
def st(tmp_path, monkeypatch):
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))
    from omni_coworker.safety import refusal_state
    return refusal_state


def test_enter_and_exit_episode(st):
    st.record_verdict(False, {"action": "write", "verdict": "REFUSE"})
    s = st.current_state()
    assert s["in_refusal"] and s["entered_at"] and s["trigger"]["action"] == "write"
    st.record_verdict(True, {"action": "read"})
    s = st.current_state()
    assert not s["in_refusal"] and s["exited_at"]
    assert len(s["episodes"]) == 1
    assert s["episodes"][0]["trigger"]["action"] == "write"
    assert s["episodes"][0]["duration_s"] >= 0


def test_repeated_refusal_updates_trigger(st):
    st.record_verdict(False, {"action": "a1"})
    st.record_verdict(False, {"action": "a2"})
    s = st.current_state()
    assert s["in_refusal"] and s["trigger"]["action"] == "a2"
    assert s["total_refusals"] == 2 and len(s["episodes"]) == 0


def test_persistence(tmp_path, monkeypatch):
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))
    from omni_coworker.safety import refusal_state as rs
    rs.record_verdict(False, {"action": "x"})
    raw = json.loads((tmp_path / "refusal_state.json").read_text())
    assert raw["in_refusal"] is True


def test_matrix_denial_records(st):
    from omni_coworker.safety import matrix
    matrix.check_permission("modify_code", {"trust_level": 0.0})
    s = st.current_state()
    assert s["in_refusal"] and s["trigger"]["source"] == "matrix"
    matrix.check_permission("read_file")
    assert not st.current_state()["in_refusal"]
