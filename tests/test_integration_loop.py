"""Tests for integration_loop stages/store/modulator/loop."""

from __future__ import annotations

import numpy as np
import pytest

from omni_coworker.integration_loop import loop as _loop
from omni_coworker.integration_loop import modulator, stages, store
from omni_coworker.integration_loop.schema import STAGES, CycleResult, ModuleState
from omni_coworker.shared_workspace import bus
from omni_coworker.shared_workspace import store as mesh_store


@pytest.fixture(autouse=True)
def _fresh(tmp_path, monkeypatch):
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))
    mesh_store._reset(); bus._reset(); store._reset()
    _loop._STATE.update({"cycles": 0, "errors": 0, "last_cycle": None,
                        "last_modulation": None, "last_ts": None})
    yield
    bus._reset(); mesh_store._reset(); store._reset()


def _ctx(rng_seed=1):
    return {"bundle": {
        "models": {"gemma-e4b": {"prompt_tokens_mean": 100, "gen_tokens_mean": 50,
                                 "gen_tokens_max": 60, "attention_entropy_mean": 2.0,
                                 "hidden_norm_mean": 75.0, "hidden_norm_std": 3.0,
                                 "last_layer_norm_mean": 80.0, "n_records": 2}},
        "affect": {"analyst": {"attention_entropy_mean": 1.9}},
        "soul": {"phi": 0.27, "psi": 0.82, "sigma": 0.30, "epsilon": 0.6},
        "soma": {"cpu_percent": 40.0, "ram_percent": 55.0,
                 "gpu_vram_used_gb": 17.0, "gpu_util_percent": 12},
        "mesh_topics": ["kernel.cycle"]},
        "rng": np.random.default_rng(rng_seed), "history": [],
        "feat_stats": {}}


def test_stages_pipeline():
    ctx = _ctx()
    s = stages.sensory_input(ctx)
    assert len(s.embedding) == stages.DIM and s.metadata["norm"] >= 0
    x = np.asarray(s.embedding)
    q = stages.qualia(ctx, x)
    assert -1 <= q.metadata["valence"] <= 1 and 0 <= q.metadata["arousal"] <= 1
    n = stages.narrative(ctx, x)
    assert len(n.embedding) == stages.DIM
    ctx["meaning_hit"] = {"score": 0.8, "name": "foo.py"}
    m = stages.meaning_maker(ctx, np.asarray(n.embedding))
    assert 0 <= m.metadata["meaning_score"] <= 1
    e = stages.expectation(ctx, x)
    assert e.metadata["pred_err"] is None  # história < 3
    fb = stages.sensory_feedback("c1", {"meaning_maker": m, "expectation": e})
    assert fb.metadata["closed"] is True


def test_expectation_with_history():
    rng = np.random.default_rng(0)
    hist = [list(rng.normal(size=stages.DIM)) for _ in range(5)]
    ctx = {"history": hist}
    x = rng.normal(size=stages.DIM)
    e = stages.expectation(ctx, x)
    assert e.metadata["pred_err"] is not None and e.metadata["pred_err"] >= 0


def test_modulator_rules():
    ss = {"meaning_maker": ModuleState("meaning_maker", metadata={"meaning_score": 0.8}),
          "expectation": ModuleState("expectation", metadata={"pred_err": 0.1}),
          "qualia": ModuleState("qualia", metadata={"valence": 0.1, "arousal": 0.3})}
    c = CycleResult("c1", 0.0, ss, 0.1)
    mod = modulator.derive_modulation(c, {"soul": {"phi": 0.3}, "soma": {}})
    assert mod.recommendation == "executor" and mod.swap_threshold_delta == -0.02
    ss["expectation"].metadata["pred_err"] = 0.9
    mod2 = modulator.derive_modulation(c, {})
    assert mod2.recommendation == "analyst" and mod2.swap_threshold_delta == 0.03


def test_run_once_persists_and_publishes():
    payload = _loop.run_once()
    assert payload["status"] in ("ok", "partial")
    assert set(STAGES) <= set((payload.get("stage_states") or {}).keys())
    assert store.get_cycle(payload["cycle_id"]) is not None
    assert bus.latest("feedback.loop") is not None
    m = payload["modulation"]
    assert m["recommendation"] in ("analyst", "executor", "balanced")


def test_loop_api():
    from fastapi.testclient import TestClient

    from omni_coworker.app import create_app
    c = TestClient(create_app())
    r = c.get("/loop/status")
    assert r.status_code == 200
    r = c.post("/loop/run")
    assert r.status_code == 200 and r.json()["cycle_id"].startswith("cyc-")
    cid = r.json()["cycle_id"]
    assert c.get(f"/loop/cycle/{cid}").status_code == 200
    assert c.get("/loop/modulation").status_code == 200
