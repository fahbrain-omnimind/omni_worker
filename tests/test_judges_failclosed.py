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
    # §1.4-5: todos cegos → consensus=None (indecidível → fila de
    # aprovação), não False — juiz cego não é juiz dissidente
    assert review["consensus"] is None
    for j in review["judges"]:
        assert j["approved"] is False
        assert j["blind"] is True
        assert "reason" in j or "comments" in j


def test_consensus_false_when_sighted_judge_rejects(tmp_path, monkeypatch):
    """Um juiz que deliberou e rejeitou → dissent real (False)."""
    orch = _make_orch(tmp_path, monkeypatch)
    monkeypatch.setattr(
        "omni_coworker.agents._llm.brain_chat_json",
        lambda *a, **k: {"approved": False, "comments": "código frágil"})

    class _BoomReviewer:
        def __init__(self, *a, **k):
            pass

        def review(self, *a, **k):
            raise RuntimeError("reviewer down")

    monkeypatch.setattr("omni_coworker.agents.reviewer_agent.ReviewerAgent", _BoomReviewer)
    review = orch.run_judge_review("t2", {"artifact": "x"})
    # j2/j3 deliberaram (llm) e rejeitaram → consensus False
    assert review["consensus"] is False


def test_consensus_true_when_sighted_judges_approve(tmp_path, monkeypatch):
    """Juízes deliberados aprovando → consensus True (votos de cegos não contam)."""
    orch = _make_orch(tmp_path, monkeypatch)
    monkeypatch.setattr(
        "omni_coworker.agents._llm.brain_chat_json",
        lambda *a, **k: {"approved": True, "comments": "ok"})

    class _BoomReviewer:
        def __init__(self, *a, **k):
            pass

        def review(self, *a, **k):
            raise RuntimeError("reviewer down")

    monkeypatch.setattr("omni_coworker.agents.reviewer_agent.ReviewerAgent", _BoomReviewer)
    review = orch.run_judge_review("t3", {"artifact": "x"})
    assert review["consensus"] is True


def test_approval_queue_entry(tmp_path, monkeypatch):
    """consensus=None → approval_queue.jsonl ganha uma linha testemunhável."""
    import json

    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path / "state"))
    orch = _make_orch(tmp_path, monkeypatch)
    review = {"judges": [{"judge": 1, "approved": False, "blind": True,
                          "reason": "down"}]}
    task = {"id": "tq", "type": "code", "attempts": 2,
            "last_artifact": "diff --git ..."}
    orch._enqueue_approval(task, review)
    qpath = orch.audit_dir / "approval_queue.jsonl"
    assert qpath.exists()
    entry = json.loads(qpath.read_text().splitlines()[0])
    assert entry["task_id"] == "tq"
    assert entry["judges"][0]["blind"] is True
