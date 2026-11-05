"""Tests for CLI commands and cascade reset in the feedback loop.

English: Hermetic tests — LLM calls (brain_chat/brain_chat_json) and
uvicorn are mocked; no backend or network required.
pt-BR: Testes herméticos — chamadas de LLM (brain_chat/brain_chat_json)
e uvicorn são mockadas; sem backend nem rede.
"""

import json
import sys
import types

from omni_coworker import cli


def _mock_llm(monkeypatch, chat_text="ok", json_payload=None):
    """Patch _llm helpers so agents never hit the brain servers."""
    payload = json_payload if json_payload is not None else {"diagnosis": "d", "suggestions": []}
    monkeypatch.setattr(
        "omni_coworker.agents._llm.brain_chat",
        lambda *a, **k: chat_text,
    )
    monkeypatch.setattr(
        "omni_coworker.agents._llm.brain_chat_json",
        lambda *a, **k: payload,
    )


def test_cli_serve(monkeypatch):
    """serve parses --port and calls uvicorn.run with the app."""
    calls = {}
    fake_uvicorn = types.SimpleNamespace(
        run=lambda app, host=None, port=None: calls.update(
            {"app": app, "host": host, "port": port}
        )
    )
    monkeypatch.setitem(sys.modules, "uvicorn", fake_uvicorn)
    assert cli.main(["serve", "--port", "18099"]) == 0
    assert calls["port"] == 18099
    assert calls["host"] == "0.0.0.0"
    assert calls["app"] is not None


def test_cli_doctor_backends_down(monkeypatch, capsys):
    """doctor reports up/down lines and exits 0 even with backends down."""
    monkeypatch.setattr(
        "omni_coworker.brain.server.ERIKA_BASE_URL", "http://127.0.0.1:1"
    )
    monkeypatch.setattr(
        "omni_coworker.brain.server.EXECUTOR_BASE_URL", "http://127.0.0.1:1"
    )
    assert cli.main(["doctor"]) == 0
    out = capsys.readouterr().out
    assert "fastapi:" in out
    assert "brain.analyst: down" in out
    assert "brain.executor: down" in out
    assert "kernel." in out


def test_cli_demo(monkeypatch, capsys):
    """demo runs the lean pipeline and prints a JSON summary."""
    _mock_llm(monkeypatch, chat_text="def f():\n    return 1\n")
    assert cli.main(["demo", "--task", "hello"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["task"] == "hello"
    assert "review" in payload and "approved" in payload["review"]
    assert "code" in payload


def test_cli_demo_no_backends(capsys):
    """demo still prints JSON when brain_chat returns None (backends down)."""
    payload_in = None
    import omni_coworker.agents._llm as llm

    orig_chat, orig_json = llm.brain_chat, llm.brain_chat_json
    try:
        llm.brain_chat = lambda *a, **k: None
        llm.brain_chat_json = lambda *a, **k: payload_in
        assert cli.main(["demo", "--task", "hello"]) == 0
    finally:
        llm.brain_chat, llm.brain_chat_json = orig_chat, orig_json
    payload = json.loads(capsys.readouterr().out)
    assert payload["task"] == "hello"
    assert payload["llm"] == {"debug": False, "code": False, "review": False}


def test_cli_soul_export(capsys):
    """soul-export prints the soul state JSON including phi."""
    assert cli.main(["soul-export"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert "phi" in payload


def test_cli_soul_export_out(tmp_path, capsys):
    """soul-export --out writes the JSON payload to disk."""
    out_file = tmp_path / "soul.json"
    assert cli.main(["soul-export", "--out", str(out_file)]) == 0
    payload = json.loads(out_file.read_text())
    assert "phi" in payload
    capsys.readouterr()


def test_cli_missions(capsys):
    """missions prints the /agency/missions payload without HTTP."""
    assert cli.main(["missions"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert "missions" in payload and "omega" in payload
    assert isinstance(payload["missions"], list)


def test_cli_no_command_prints_help(capsys):
    """Bare invocation prints help and exits 0."""
    assert cli.main([]) == 0
    assert "omni-coworker" in capsys.readouterr().out


# ── Cascade reset in feedback_loop ────────────────────────────────────────────


def _make_orch(tmp_path, monkeypatch):
    from omni_coworker.orchestration.agent_orchestrator import AgentOrchestrator

    monkeypatch.setattr(
        "omni_coworker.orchestration.agent_orchestrator.time.sleep",
        lambda *_a, **_k: None,
    )
    orch = AgentOrchestrator(base_dir=str(tmp_path / "orch"))
    return orch


def test_cascade_reset_after_three_stalls(tmp_path, monkeypatch):
    """3 consecutive needs_revision iterations trigger a cascade_reset event
    and inject the SIMPLIFY note into the next execute_task call."""
    orch = _make_orch(tmp_path, monkeypatch)

    notes_seen = []
    monkeypatch.setattr(
        orch,
        "execute_task",
        lambda task, notes=None: notes_seen.append(list(notes or []))
        or {"artifact": "partial", "llm": False},
    )
    monkeypatch.setattr(
        orch,
        "run_judge_review",
        lambda tid, result: {
            "task_id": tid,
            "consensus": False,
            "judges": [{"judge": 1, "approved": False, "comments": "too complex"}],
        },
    )
    monkeypatch.setattr(
        orch, "run_audit", lambda tid: {"task_id": tid, "passed": True}
    )

    task = orch.create_task("refactor", "do something")
    out = orch.feedback_loop(task, max_iterations=5)

    # Loop ran to completion without deadlock.
    assert out["status"] == "needs_revision"
    assert out["attempts"] == 5
    assert len(notes_seen) == 5

    events = [e for e in out["feedback"] if e.get("type") == "cascade_reset"]
    assert events, "cascade_reset event must be recorded in task['feedback']"
    assert events[0]["iteration"] == 3

    # SIMPLIFY note injected from the 4th call onward (stall hit at iter 3).
    assert orch.SIMPLIFY_NOTE not in (notes_seen[2])
    assert orch.SIMPLIFY_NOTE in notes_seen[3]
    assert orch.SIMPLIFY_NOTE in notes_seen[4]


def test_cascade_reset_counter_resets_on_approval(tmp_path, monkeypatch):
    """An approval clears the stall counter and ends the loop."""
    orch = _make_orch(tmp_path, monkeypatch)
    reviews = iter(
        [
            {"consensus": False, "judges": [{"approved": False, "comments": "x"}]},
            {"consensus": True, "judges": [{"approved": True, "comments": "ok"}]},
        ]
    )
    monkeypatch.setattr(
        orch, "execute_task", lambda task, notes=None: {"artifact": "a", "llm": False}
    )
    monkeypatch.setattr(
        orch,
        "run_judge_review",
        lambda tid, result: {"task_id": tid, **next(reviews)},
    )
    monkeypatch.setattr(
        orch, "run_audit", lambda tid: {"task_id": tid, "passed": True}
    )

    task = orch.create_task("fix", "fix it")
    out = orch.feedback_loop(task, max_iterations=5)

    assert out["status"] == "approved"
    assert orch._stall_count == 0
    assert not [e for e in out["feedback"] if e.get("type") == "cascade_reset"]


def test_stall_and_reset_count(tmp_path, monkeypatch):
    """stall()/reset_count() are plain counters with no deps."""
    orch = _make_orch(tmp_path, monkeypatch)
    assert orch.stall() == 1
    assert orch.stall() == 2
    orch.reset_count()
    assert orch.stall() == 1
