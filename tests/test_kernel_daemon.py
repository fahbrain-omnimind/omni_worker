"""Tests for kernel_daemon collector/features/feedback/scheduler."""

from __future__ import annotations

import json

import pytest

from omni_coworker.kernel_daemon import collector, features, scheduler
from omni_coworker.shared_workspace import bus, store


@pytest.fixture(autouse=True)
def _fresh(tmp_path, monkeypatch):
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))
    store._reset(); bus._reset()
    features._PREV.clear()
    scheduler._STATE.update({"cycles": 0, "errors": 0, "last_bundle": None,
                            "last_ts": None, "last_duration_s": None})
    yield
    bus._reset(); store._reset(); features._PREV.clear()


def _write_log(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")


def test_tail_incremental(tmp_path):
    log = tmp_path / "act.jsonl"
    _write_log(log, [{"ts": "1", "model": "m1", "gen_tokens": 10}])
    collector.reset_offset(log)
    assert len(collector._read_new_activations(log)) == 1
    assert collector._read_new_activations(log) == []  # offset consumed
    _write_log(log, [{"ts": "2", "model": "m1", "gen_tokens": 20}])
    assert len(collector._read_new_activations(log)) == 1


def test_aggregate_bundle():
    raw = {
        "ts": 1.0,
        "activations": [
            {"model": "gemma-e4b", "prompt_tokens": 100, "gen_tokens": 50,
             "attention_entropy_last": 1.9,
             "layers": [{"layer": 0, "norm": 70.0}, {"layer": 41, "norm": 80.0}]},
            {"model": "gemma-e4b", "prompt_tokens": 120, "gen_tokens": 60,
             "attention_entropy_last": 2.1,
             "layers": [{"layer": 0, "norm": 72.0}, {"layer": 41, "norm": 82.0}]},
        ],
        "affect": {"analyst": {"attention_entropy_mean": 1.9}, "executor": None},
        "soul": {"phi": 0.27, "psi": 0.82, "sigma": 0.30, "epsilon": 0.6},
        "soma": {"cpu_percent": 40.0, "ram_percent": 55.0,
                "gpu": {"gpus": [{"vram_used_gb": 17.0, "util_percent": 12}]}},
        "mesh": {"soul.phi": {}},
    }
    b = features.aggregate(raw)
    m = b["models"]["gemma-e4b"]
    assert m["n_records"] == 2 and m["gen_tokens_max"] == 60
    assert m["attention_entropy_mean"] == 2.0
    assert b["soma"]["gpu_vram_used_gb"] == 17.0
    assert b["mesh_topics"] == ["soul.phi"]
    # second call → drift computed vs first
    b2 = features.aggregate(raw)
    assert b2["drift"]["gemma-e4b"]["attention_entropy_mean"] == 0.0


def test_run_cycle_publishes(tmp_path, monkeypatch):
    log = tmp_path / "act.jsonl"
    _write_log(log, [{"ts": "1", "model": "m", "gen_tokens": 5,
                     "layers": [{"layer": 0, "norm": 1.0}]}])
    monkeypatch.setattr(collector, "ACTIVATIONS_LOG", log)
    bundle = scheduler.run_cycle()
    assert "kernel.cycle" in (bundle.get("published_topics") or [])
    assert bus.latest("kernel.cycle") is not None
    assert store.latest_per_topic().get("kernel.drift") is not None


def test_status_endpoint(tmp_path):
    from fastapi.testclient import TestClient
    from omni_coworker.app import create_app
    c = TestClient(create_app())
    r = c.get("/kernel/daemon")
    assert r.status_code == 200 and "interval_s" in r.json()
