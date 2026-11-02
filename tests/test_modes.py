"""Tests for Roo-style modes (sticky model per mode)."""

from omni_coworker.agents import modes


def test_switch_mode_default(monkeypatch, tmp_path):
    monkeypatch.setattr(modes, "state_path", lambda: tmp_path / "modes.json")
    spec = modes.switch_mode("architect")
    assert spec["persona"] == "architect"
    assert spec["sticky_role"] == "analyst"
    assert spec["role"] == "analyst"


def test_sticky_role_persists(monkeypatch, tmp_path):
    monkeypatch.setattr(modes, "state_path", lambda: tmp_path / "modes.json")
    modes.set_role("code", "executor")
    spec = modes.switch_mode("code")
    assert spec["sticky_role"] == "executor"
    assert modes.current_mode() == "code"


def test_invalid_mode_falls_back():
    spec = modes.switch_mode("nope")
    assert spec["persona"] == "code"


def test_spec_for_current(monkeypatch, tmp_path):
    monkeypatch.setattr(modes, "state_path", lambda: tmp_path / "modes.json")
    modes.switch_mode("reviewer")
    spec = modes.spec_for()
    assert spec["persona"] == "critic"