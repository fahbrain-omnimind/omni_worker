"""Hermetic tests for the CLI circuit breaker (OW-STU-014).

English: Never spawns real agentic CLIs; uses throwaway shell scripts and
tmp_path state dirs.
pt-BR: Nunca sobe CLIs agênticos reais; usa scripts shell descartáveis e
dirs de estado em tmp_path.
"""

from __future__ import annotations

import subprocess

from omni_coworker.agents.external_cli_agent import (
    CLICircuitBreaker,
    ExternalCLIAgent,
)


def _write_script(tmp_path, name, body):
    script = tmp_path / name
    script.write_text(body, encoding="utf-8")
    script.chmod(0o755)
    return str(script)


def _env(monkeypatch, tmp_path, threshold=3, cooldown=300):
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))
    monkeypatch.setenv("OMNI_CLI_CB_THRESHOLD", str(threshold))
    monkeypatch.setenv("OMNI_CLI_CB_COOLDOWN_S", str(cooldown))


def test_failures_three_open(tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    cb = CLICircuitBreaker("agent")
    assert cb.is_available()
    cb.record_failure()
    cb.record_failure()
    assert cb.is_available()
    cb.record_failure()
    assert cb.is_available() is False
    assert cb.state == "open"
    assert cb.failures == 3


def test_open_returns_without_spawn(tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    fail_script = _write_script(tmp_path, "fail.sh", "#!/bin/sh\nexit 1\n")
    agent = ExternalCLIAgent("agent", adapter="shell", cmd=fail_script)
    for _ in range(3):
        agent.execute("t", {})
    assert agent.circuit_breaker.state == "open"

    calls = []

    def tracked(*a, **k):
        calls.append((a, k))
        raise RuntimeError("spawn should not happen")

    monkeypatch.setattr(subprocess, "Popen", tracked)
    monkeypatch.setattr(
        "omni_coworker.agents.external_cli_agent.subprocess.Popen", tracked
    )

    result = agent.execute("t", {})
    assert result["ok"] is False
    assert calls == []


def test_cooldown_half_open(tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path, cooldown=0)
    cb = CLICircuitBreaker("agent")
    for _ in range(3):
        cb.record_failure()
    assert cb.is_available() is True
    assert cb.state == "half_open"


def test_success_closes(tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path, cooldown=0)
    ok_script = _write_script(tmp_path, "ok.sh", "#!/bin/sh\necho '{\"ok\": true}'\n")
    agent = ExternalCLIAgent("agent", adapter="shell", cmd=ok_script)
    cb = agent.circuit_breaker
    for _ in range(3):
        cb.record_failure()
    # allow one probe
    cb.cooldown = 0
    assert cb.state == "half_open"
    result = agent.execute("t", {})
    assert result["ok"] is True
    assert cb.state == "closed"
    assert cb.failures == 0


def test_state_persists_between_instances(tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    cb1 = CLICircuitBreaker("agent")
    for _ in range(3):
        cb1.record_failure()
    assert cb1.state == "open"

    cb2 = CLICircuitBreaker("agent")
    assert cb2.state == "open"
    assert cb2.failures == 3


def test_empty_output_counts_as_failure(tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    empty_script = _write_script(tmp_path, "empty.sh", "#!/bin/sh\nexit 0\n")
    agent = ExternalCLIAgent("agent", adapter="shell", cmd=empty_script)
    for _ in range(3):
        r = agent.execute("t", {})
        assert r["ok"] is True
    assert agent.circuit_breaker.state == "open"


def test_publishes_transition(tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    from omni_coworker.shared_workspace import bus

    seen = []
    bus.subscribe("agent", lambda topic, evt: seen.append((topic, evt)))
    cb = CLICircuitBreaker("agent")
    for _ in range(3):
        cb.record_failure()
    topics = [t for t, _ in seen]
    assert "agent.circuit_breaker" in topics
    assert "agent.escalation" in topics
