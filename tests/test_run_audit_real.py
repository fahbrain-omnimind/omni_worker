"""Tests for real run_audit."""

from __future__ import annotations

from pathlib import Path

from omni_coworker.orchestration.agent_orchestrator import AgentOrchestrator


def _make_orch(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "omni_coworker.orchestration.agent_orchestrator.time.sleep",
        lambda *_a, **_k: None,
    )
    return AgentOrchestrator(base_dir=str(tmp_path / "orch"))


def test_run_audit_passes_with_tests_and_good_imports(tmp_path, monkeypatch):
    orch = _make_orch(tmp_path, monkeypatch)
    src = tmp_path / "m.py"
    src.write_text("import os\n\ndef f():\n    return 1\n")
    tst = tmp_path / "test_m.py"
    tst.write_text("from m import f\n\ndef test_f():\n    assert f() == 1\n")
    task = orch.create_task("refactor", "desc", files=[str(src), str(tst)])
    audit = orch.run_audit(task["id"])
    assert audit["passed"] is True
    assert audit["checks"]["tests"]["passed"] is True
    assert audit["checks"]["imports"]["passed"] is True
    assert audit["metrics"]["coverage"] != 0.85


def test_run_audit_fails_missing_tests(tmp_path, monkeypatch):
    orch = _make_orch(tmp_path, monkeypatch)
    src = tmp_path / "m.py"
    src.write_text("import os\n\ndef f():\n    return 1\n")
    task = orch.create_task("refactor", "desc", files=[str(src)])
    audit = orch.run_audit(task["id"])
    assert audit["passed"] is False
    assert audit["checks"]["tests"]["passed"] is False


def test_run_audit_fails_broken_import(tmp_path, monkeypatch):
    orch = _make_orch(tmp_path, monkeypatch)
    src = tmp_path / "m.py"
    src.write_text("import definitely_missing_module_xyz\n\ndef f():\n    return 1\n")
    tst = tmp_path / "test_m.py"
    tst.write_text("def test_x():\n    assert True\n")
    task = orch.create_task("refactor", "desc", files=[str(src), str(tst)])
    audit = orch.run_audit(task["id"])
    assert audit["passed"] is False
    assert audit["checks"]["imports"]["passed"] is False
    assert audit["metrics"]["broken_imports"] >= 1


def test_run_audit_fails_syntax_error(tmp_path, monkeypatch):
    orch = _make_orch(tmp_path, monkeypatch)
    src = tmp_path / "m.py"
    src.write_text("def f(\n")
    tst = tmp_path / "test_m.py"
    tst.write_text("def test_x():\n    assert True\n")
    task = orch.create_task("refactor", "desc", files=[str(src), str(tst)])
    audit = orch.run_audit(task["id"])
    assert audit["passed"] is False
