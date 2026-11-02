"""Tests for feedback.loop modulation consumers (consumer.py wiring)."""

from __future__ import annotations

import json
import time

import pytest

from omni_coworker.integration_loop import consumer
from omni_coworker.orchestration import swap_scheduler


@pytest.fixture(autouse=True)
def _fresh(tmp_path, monkeypatch):
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))
    yield


def _write_mod(tmp_path, **over):
    mod = {"ts": time.time(), "cycle_id": "cyc-t", "recommendation": "analyst",
           "swap_threshold_delta": 0.03, "curiosity_boost": 0.5,
           "prompt_suffix": "[regime:reflect]"}
    mod.update(over)
    consumer.write_modulation(mod)
    return mod


def test_write_read_roundtrip(tmp_path):
    m = _write_mod(tmp_path)
    d = consumer.latest_modulation()
    assert d and d["cycle_id"] == "cyc-t" and d["swap_threshold_delta"] == 0.03


def test_stale_modulation_returns_none(tmp_path):
    _write_mod(tmp_path, ts=time.time() - 4000)
    assert consumer.latest_modulation(max_age_s=300) is None


def test_missing_returns_none(tmp_path):
    assert consumer.latest_modulation() is None


def test_scheduler_applies_delta(tmp_path, monkeypatch):
    _write_mod(tmp_path, swap_threshold_delta=0.03)
    monkeypatch.setattr(swap_scheduler, "_vram_ratio", lambda: 0.91)
    monkeypatch.setattr(swap_scheduler, "_executor_activations", lambda: None)
    captured = {}

    class _Client:
        def __init__(self, *a, **k): pass
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def post(self, url):
            captured["url"] = url
            class R:
                def json(self): return {"status": "unloaded"}
            return R()

    import httpx
    monkeypatch.setattr(httpx, "Client", _Client)
    s = swap_scheduler.SwapScheduler()
    s.state["executor"] = "loaded"
    s.tick()
    # evict_at = 0.9 - 0.03 = 0.87 → ratio 0.91 evicts even though < 0.9 env
    assert captured.get("url", "").endswith("/erika/unload")
    assert s.state["modulation"]["swap_threshold_delta"] == 0.03


def test_scheduler_no_modulation_default(tmp_path, monkeypatch):
    monkeypatch.setattr(swap_scheduler, "_vram_ratio", lambda: 0.91)
    monkeypatch.setattr(swap_scheduler, "_executor_activations", lambda: None)
    captured = {}

    class _Client:
        def __init__(self, *a, **k): pass
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def post(self, url):
            captured["url"] = url
            class R:
                def json(self): return {"status": "unloaded"}
            return R()

    import httpx
    monkeypatch.setattr(httpx, "Client", _Client)
    s = swap_scheduler.SwapScheduler()
    s.state["executor"] = "loaded"
    s.tick()
    # sem modulação: ratio 0.91 ≥ 0.9 → evict normal
    assert captured.get("url", "").endswith("/erika/unload")
    assert s.state["modulation"]["swap_threshold_delta"] == 0.0
