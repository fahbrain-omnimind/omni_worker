"""Tests for psychology.scars (persistent trauma → defense rules)."""

from __future__ import annotations

import pytest

from omni_coworker.psychology import TraumaIntegration
from omni_coworker.shared_workspace import bus, store


@pytest.fixture(autouse=True)
def _fresh(tmp_path, monkeypatch):
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))
    store._reset(); bus._reset()
    yield
    bus._reset(); store._reset()


def test_create_and_persist(tmp_path):
    ti = TraumaIntegration()
    s = ti.create_scar({"type": "oom_swap", "severity": "high",
                       "description": "executor reload OOM during battery"})
    assert s["status"] == "integrated_as_identity_structure"
    # fresh instance reads from sqlite (persistence)
    ti2 = TraumaIntegration()
    scars = ti2.all_scars()
    assert len(scars) == 1 and scars[0]["type"] == "oom_swap"


def test_consult_applies(tmp_path):
    ti = TraumaIntegration()
    ti.create_scar({"type": "oom", "description": "executor reload OOM during battery"})
    hit = ti.consult_scars_before_decision(
        {"action": "reload executor brain", "description": "swap reload executor"})
    assert hit["decision_modified_by_trauma"] is True
    miss = ti.consult_scars_before_decision({"action": "unrelated xyz"})
    assert miss["decision_modified_by_trauma"] is False


def test_scar_published_on_mesh(tmp_path):
    TraumaIntegration().create_scar({"type": "stall", "description": "x"})
    ev = bus.latest("soma.scar")
    assert ev is not None and ev["payload"]["type"] == "stall"
