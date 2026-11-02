"""Tests for orchestration.swap_scheduler (hermetic, fake probes)."""

from __future__ import annotations

from omni_coworker.orchestration import swap_scheduler as ss


class _FakeResp:
    def __init__(self, status):
        self._s = status

    def json(self):
        return {"status": self._s}


class _FakeClient:
    def __init__(self):
        self.posts = []

    def post(self, url, *a, **k):
        self.posts.append(url)
        return _FakeResp("unloaded" if url.endswith("unload") else "loaded")

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_evicts_when_vram_tight_and_idle(monkeypatch):
    monkeypatch.setattr(ss, "_vram_ratio", lambda: 0.95)
    monkeypatch.setattr(ss, "_executor_activations", lambda: 0)
    s = ss.SwapScheduler()
    fc = _FakeClient()
    monkeypatch.setattr("httpx.Client", lambda *a, **k: fc)
    st = s.tick()
    assert st["executor"] == "unloaded"
    assert st["events"][-1]["evt"] == "evicted"


def test_no_evict_when_busy(monkeypatch):
    monkeypatch.setattr(ss, "_vram_ratio", lambda: 0.95)
    monkeypatch.setattr(ss, "_executor_activations", lambda: 1)
    s = ss.SwapScheduler()
    fc = _FakeClient()
    monkeypatch.setattr("httpx.Client", lambda *a, **k: fc)
    st = s.tick()
    assert st["executor"] == "loaded"
    assert fc.posts == []


def test_busy_detection_uses_delta(monkeypatch):
    """A stagnant cumulative counter must not pin the executor busy."""
    s = ss.SwapScheduler()
    assert s._executor_active(3) is True   # first sight of activity counts as busy
    assert s._executor_active(3) is False  # same count next tick -> idle again
    assert s._executor_active(4) is True   # new generation -> busy
    assert s._executor_active(None) is False  # unreachable -> treat as idle


def test_timed_reload_suppressed_while_vram_tight(monkeypatch):
    """An expired max_unloaded clock must not reload into a saturated GPU."""
    import time

    s = ss.SwapScheduler()
    s.state["executor"] = "unloaded"
    s.state["last_evict"] = time.time() - 99999  # expired clock
    monkeypatch.setattr(ss, "_vram_ratio", lambda: 0.95)
    monkeypatch.setattr(ss, "_executor_activations", lambda: 0)
    fc = _FakeClient()
    monkeypatch.setattr("httpx.Client", lambda *a, **k: fc)
    st = s.tick()
    assert st["executor"] == "unloaded"
    assert fc.posts == []  # no reload under pressure


def test_timed_reload_fires_with_headroom(monkeypatch):
    import time

    s = ss.SwapScheduler()
    s.state["executor"] = "unloaded"
    s.state["last_evict"] = time.time() - 99999
    monkeypatch.setattr(ss, "_vram_ratio", lambda: 0.80)  # below evict, above reload
    monkeypatch.setattr(ss, "_executor_activations", lambda: 0)
    fc = _FakeClient()
    monkeypatch.setattr("httpx.Client", lambda *a, **k: fc)
    st = s.tick()
    assert st["executor"] == "loaded"
    assert any(u.endswith("reload") for u in fc.posts)


def test_reloads_when_vram_frees(monkeypatch):
    monkeypatch.setattr(ss, "_vram_ratio", lambda: 0.95)
    monkeypatch.setattr(ss, "_executor_activations", lambda: 0)
    s = ss.SwapScheduler()
    fc = _FakeClient()
    monkeypatch.setattr("httpx.Client", lambda *a, **k: fc)
    s.tick()  # evict
    monkeypatch.setattr(ss, "_vram_ratio", lambda: 0.5)
    s.tick()  # reload
    assert s.state["executor"] == "loaded"
    assert s.state["events"][-1]["evt"] == "reloaded"