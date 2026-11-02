"""Hermetic tests for the external-CLI bridge (ACP + shell fallback).

English: Never spawns real agentic CLIs and never uses the ACP SDK to
talk to an agent: all subprocesses are throwaway shell scripts under
tmp_path and the ACP path is exercised only as a degraded/flag probe.
pt-BR: Nunca sobe CLIs agênticos reais e nunca usa o SDK ACP para falar
com um agente: todos os subprocessos são scripts shell descartáveis em
tmp_path e o caminho ACP só é exercitado como probe degradado/flag.
"""

from __future__ import annotations

import shutil
import uuid

import pytest

from omni_coworker.agents.bus import get_message_bus
from omni_coworker.agents.external_cli_agent import (
    ACPClient,
    ExternalCLIAgent,
    ShellCLIAdapter,
    list_available,
    register_cli,
    sanitized_env,
)


def _write_script(tmp_path: pytest.TempPathFactory, name: str, body: str) -> str:
    """Create an executable throwaway shell script and return its path."""
    script = tmp_path / name
    script.write_text(body, encoding="utf-8")
    script.chmod(0o755)
    return str(script)


# ── 1. ShellCLIAdapter: JSON output ──────────────────────────────────────────


def test_shell_adapter_json_output(tmp_path):
    script = _write_script(
        tmp_path,
        "fake_cli.sh",
        "#!/bin/sh\necho '{\"ok\": true, \"result\": \"hello\"}'\n",
    )
    adapter = ShellCLIAdapter("fake", script)
    result = adapter.run("do the thing", {"note": "x"})

    assert result["ok"] is True
    assert result["exit"] == 0
    assert result["adapter"] == "shell"
    assert result["timed_out"] is False
    assert result["json"] == {"ok": True, "result": "hello"}
    assert "hello" in result["output"]


def test_shell_adapter_args_factory_appends_task(tmp_path):
    script = _write_script(tmp_path, "args_cli.sh", "#!/bin/sh\necho \"$1\"\n")
    adapter = ShellCLIAdapter("args", script, args_factory=lambda task, context: [task])
    result = adapter.run("hello task", {})
    assert result["ok"] is True
    assert result["output"].strip() == "hello task"


# ── 2. ShellCLIAdapter: failure with stderr ──────────────────────────────────


def test_shell_adapter_failure_captures_stderr(tmp_path):
    script = _write_script(
        tmp_path,
        "fail_cli.sh",
        "#!/bin/sh\necho 'boom happened' >&2\nexit 1\n",
    )
    adapter = ShellCLIAdapter("fail", script)
    result = adapter.run("t", {})

    assert result["ok"] is False
    assert result["exit"] == 1
    assert result["timed_out"] is False
    assert "boom happened" in result["stderr"]


# ── 3. ShellCLIAdapter: timeout kills the process ────────────────────────────


def test_shell_adapter_timeout_kills_process(tmp_path):
    script = _write_script(tmp_path, "sleepy.sh", "#!/bin/sh\nsleep 5\necho done\n")
    adapter = ShellCLIAdapter("sleepy", script, timeout=1)
    result = adapter.run("t", {})

    assert result["ok"] is False
    assert result["timed_out"] is True
    assert "timeout" in result["stderr"].lower()


# ── 4. ShellCLIAdapter: sanitized environment ────────────────────────────────


def test_shell_adapter_env_sanitized(tmp_path, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-secret123456")
    monkeypatch.setenv("HF_TOKEN", "hf_secret123456")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-proj-secret789012")
    monkeypatch.setenv("MY_PRIVATE_TOKEN", "tok-1234567890")
    monkeypatch.setenv("SOME_API_KEY", "secret-key-value")

    script = _write_script(tmp_path, "envprint.sh", "#!/bin/sh\nenv | sort\n")
    adapter = ShellCLIAdapter("envprint", script)
    result = adapter.run("t", {})

    assert result["ok"] is True
    out = result["output"]
    assert "OPENAI_BASE_URL=http://127.0.0.1:8098" in out
    for leaked in (
        "ANTHROPIC_API_KEY",
        "HF_TOKEN",
        "OPENAI_API_KEY",
        "MY_PRIVATE_TOKEN",
        "SOME_API_KEY",
        "sk-ant-secret123456",
        "hf_secret123456",
        "sk-proj-secret789012",
        "secret-key-value",
    ):
        assert leaked not in out


def test_sanitized_env_never_leaks_secrets(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-abc123")
    monkeypatch.setenv("OPENAI_BASE_URL", "http://evil.example")
    monkeypatch.setenv("PATH", "/usr/bin:/bin")
    env = sanitized_env({"HF_TOKEN": "hf_direct-pass"})

    assert env["OPENAI_BASE_URL"] == "http://127.0.0.1:8098"  # fixed base, never inherited
    assert env.get("PATH") == "/usr/bin:/bin"  # allowlisted
    assert "ANTHROPIC_API_KEY" not in env
    assert "HF_TOKEN" not in env  # override was filtered too


# ── 5. ExternalCLIAgent facade ───────────────────────────────────────────────


def test_external_cli_agent_execute_shell(tmp_path):
    script = _write_script(
        tmp_path,
        "agent_cli.sh",
        "#!/bin/sh\necho '{\"status\": \"completed\"}'\n",
    )
    agent = ExternalCLIAgent("fake", adapter="shell", cmd=script)
    result = agent.execute("do it", {"note": "x"})

    assert result["agent"] == "fake"
    assert result["ok"] is True
    assert result["llm"] is False
    assert result["adapter"] == "shell"
    assert result["json"] == {"status": "completed"}
    assert "completed" in result["output"]
    assert result["exit"] == 0


def test_external_cli_agent_no_binary_no_adapter():
    agent = ExternalCLIAgent("totally_missing_cli_xyz")
    result = agent.execute("t", {})
    assert result["adapter"] == "none"
    assert result["ok"] is False
    assert result["llm"] is False


def test_register_cli_then_execute(tmp_path):
    script = _write_script(tmp_path, "reg_cli.sh", "#!/bin/sh\necho ok\n")
    register_cli("mycli", script, args_factory=lambda task, context: [])
    try:
        agent = ExternalCLIAgent("mycli", adapter="shell")
        result = agent.execute("t", {})
        assert result["adapter"] == "shell"
        assert result["ok"] is True
    finally:
        from omni_coworker.agents.external_cli_agent import _RUNTIME_CLIS

        _RUNTIME_CLIS.pop("mycli", None)


# ── 6. publish_to_bus ────────────────────────────────────────────────────────


def test_publish_to_bus_delivers(tmp_path):
    bus = get_message_bus()
    script = _write_script(tmp_path, "bus_cli.sh", "#!/bin/sh\necho '{\"done\": true}'\n")
    agent = ExternalCLIAgent("fake", adapter="shell", cmd=script)
    agent.execute("task", {})

    channel = f"ext_cli_{uuid.uuid4().hex}"
    msg = agent.publish_to_bus(channel)

    assert msg is not None
    pending = bus.pending(channel)
    assert pending, "message should be queued on the bus"
    stored = pending[-1]
    assert stored["agent"] == "fake"
    assert stored["channel"] == channel
    assert stored["ok"] is True
    assert stored.get("ts")  # bus defaulted timestamp


# ── 7. list_available resilience ─────────────────────────────────────────────


def test_list_available_empty_path(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda *a, **k: None)
    items = list_available()
    assert isinstance(items, list)
    names = {item["name"] for item in items}
    assert names >= {"dev", "opencode", "kilo", "hermes"}
    for item in items:
        assert item["available"] is False


# ── ACP client: degraded/flag probes (never spawn an agent) ──────────────────


def test_acp_client_available_returns_bool():
    assert isinstance(ACPClient.available(), bool)


def test_acp_client_degrades_when_sdk_unavailable(monkeypatch):
    monkeypatch.setattr(ACPClient, "available", staticmethod(lambda: False))
    client = ACPClient("x", "definitely-not-a-real-binary")
    result = client.run("task", {})
    assert result["ok"] is False
    assert result["adapter"] == "acp"
    assert "unavailable" in result["stderr"].lower()


def test_acp_handler_allowlist_decisions():
    """DENY-by-default allowlist logic (duck-typed, no ACP SDK required)."""
    from types import SimpleNamespace

    from omni_coworker.agents.external_cli_agent import _ACPSessionHandler

    handler = _ACPSessionHandler("/work")

    inside = SimpleNamespace(kind="read", locations=[SimpleNamespace(path="/work/x.txt")], content=None)
    assert handler._decide(inside)["allow"] is True
    assert handler._decide(inside)["reason"] == "inside_cwd"

    outside = SimpleNamespace(kind="read", locations=[SimpleNamespace(path="/etc/passwd")], content=None)
    assert handler._decide(outside)["allow"] is False
    assert handler._decide(outside)["reason"] == "outside_cwd"

    escape = SimpleNamespace(kind="edit", locations=[SimpleNamespace(path="/work/../etc/passwd")], content=None)
    assert handler._decide(escape)["allow"] is False

    terminal = SimpleNamespace(kind="execute", locations=[], content=None)
    assert handler._decide(terminal)["allow"] is False
    assert handler._decide(terminal)["reason"] == "deny_by_default"

    think = SimpleNamespace(kind="think", locations=[], content=None)
    assert handler._decide(think)["allow"] is True


# ── Orchestrator integration ─────────────────────────────────────────────────


def test_orchestrator_run_external_delegates(monkeypatch, tmp_path):
    from omni_coworker.orchestration.agent_orchestrator import AgentOrchestrator

    captured: dict = {}

    class _FakeExternal:
        def __init__(self, name, **kwargs):
            captured["name"] = name
            captured["kwargs"] = kwargs

        def execute(self, task, context=None):
            captured["task"] = task
            captured["context"] = context
            return {
                "agent": captured["name"],
                "ok": True,
                "output": "stub",
                "llm": False,
                "adapter": "none",
            }

    monkeypatch.setattr(
        "omni_coworker.agents.external_cli_agent.ExternalCLIAgent", _FakeExternal
    )
    orch = AgentOrchestrator(base_dir=str(tmp_path / "orch"))
    result = orch.run_external("some_cli", "do the work", {"k": "v"})

    assert captured["name"] == "some_cli"
    assert captured["task"] == "do the work"
    assert captured["context"] == {"k": "v"}
    assert result["agent"] == "some_cli"
    assert result["ok"] is True