"""Tests for judge fail-closed behavior on backend outage."""

from __future__ import annotations

from omni_coworker.orchestration import agent_orchestrator as ao


def _make_orch(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "omni_coworker.orchestration.agent_orchestrator.time.sleep",
        lambda *_a, **_k: None,
    )
    return ao.AgentOrchestrator(base_dir=str(tmp_path / "orch"))


def test_judges_not_silent_approved_on_backend_down(tmp_path, monkeypatch):
    orch = _make_orch(tmp_path, monkeypatch)

    # Backend down: brain_chat_json returns None.
    monkeypatch.setattr("omni_coworker.agents._llm.brain_chat_json", lambda *a, **k: None)

    # ReviewerAgent raises (backend unavailable).
    class _BoomReviewer:
        def __init__(self, *a, **k):
            pass

        def review(self, *a, **k):
            raise RuntimeError("reviewer down")

    monkeypatch.setattr("omni_coworker.agents.reviewer_agent.ReviewerAgent", _BoomReviewer)

    review = orch.run_judge_review("t1", {"artifact": "x"})
    assert review["consensus"] is False
    for j in review["judges"]:
        assert j["approved"] is False
        assert "reason" in j or "comments" in j
