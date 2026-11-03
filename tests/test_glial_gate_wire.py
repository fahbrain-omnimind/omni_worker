"""glial_gate wiring in /brain/chat + intervention script imports."""
import json

import pytest


def test_glial_gate_blocks_when_habituated():
    from omni_coworker.activation_beta import spiking_glial

    # exposição repetida ao mesmo tag -> habituated alto -> bloquear
    # (rate=0.1 em glial_features: precisa de ~18 repetições para >= 0.8)
    window = [{"value": 0.7, "tags": ("topic_a",)}] * 20
    gate = spiking_glial.glial_gate({}, window)
    assert gate["allow_generation"] is False
    assert "habituated" in gate["reason"] or "vagus" in gate["reason"]


def test_glial_gate_allows_healthy_signal():
    from omni_coworker.activation_beta import spiking_glial

    window = [{"value": 0.3 + (i % 3) * 0.1, "tags": (f"t{i}",)} for i in range(6)]
    gate = spiking_glial.glial_gate({}, window)
    assert gate["allow_generation"] is True


def test_glial_gate_fail_open_on_error():
    from omni_coworker.activation_beta import spiking_glial

    gate = spiking_glial.glial_gate({}, None)  # janela vazia -> features vazias
    assert gate["allow_generation"] is True


def test_glial_verdict_aggregates_windows():
    from omni_coworker.activation_beta import attractor

    attractor.reset()
    rec = {"model": "m1", "attention_entropy_last": 2.0,
           "layers": [{"layer": i, "norm": 1.0} for i in range(43)]}
    attractor.push([rec] * 4)
    v = attractor.glial_verdict()
    assert "allow_generation" in v
    assert isinstance(v["allow_generation"], bool)


def test_brain_chat_glial_gate_in_payload():
    # verifica que o flag with_glial_gate é consumido e o fluxo é fail-open
    import sys
    from pathlib import Path

    src = Path(__file__).resolve().parents[1] / "src"
    sys.path.insert(0, str(src))
    from omni_coworker.brain import server as bs

    assert hasattr(bs, "create_brain_router")


def test_intervention_script_imports():
    import importlib.util
    from pathlib import Path

    p = Path(__file__).resolve().parents[1] / "scripts" / "experiments" \
        / "run_intervention_experiment.py"
    spec = importlib.util.spec_from_file_location("interv", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.BASE and mod.INTERV
    assert mod.hits("elevated memory pressure") == 2

def test_glial_gate_fail_closed_on_error(monkeypatch):
    import os
    from omni_coworker.activation_beta import spiking_glial

    monkeypatch.setenv("OMNI_GATE_FAIL_CLOSED", "1")

    def boom(*a, **k):
        raise RuntimeError("x")

    monkeypatch.setattr(spiking_glial, "glial_features", boom)
    gate = spiking_glial.glial_gate({}, [{"entropy": 1.0}])
    assert gate["allow_generation"] is False
    assert gate["reason"] == "fail-closed"


def test_glial_verdict_fail_closed_on_error(monkeypatch):
    import os
    from omni_coworker.activation_beta import spiking_glial, attractor

    monkeypatch.setenv("OMNI_GATE_FAIL_CLOSED", "1")
    attractor.reset()

    def boom(*a, **k):
        raise RuntimeError("x")

    monkeypatch.setattr(spiking_glial, "glial_gate", boom)
    v = attractor.glial_verdict()
    assert v["allow_generation"] is False
    assert v["reason"] == "fail-closed"


def test_rehydrate_lazy_on_first_gate(monkeypatch):
    from omni_coworker.activation_beta import attractor

    attractor.reset()
    calls = {"n": 0}
    orig = attractor.rehydrate

    def spy(*a, **k):
        calls["n"] += 1
        return orig(*a, **k)

    monkeypatch.setattr(attractor, "rehydrate", spy)
    attractor.glial_verdict()
    assert calls["n"] == 1


def test_brain_chat_default_glial_gate_on(monkeypatch):
    monkeypatch.setenv("OMNI_GATE_FAIL_CLOSED", "1")
    from omni_coworker.brain import server as bs
    from omni_coworker.activation_beta import attractor

    monkeypatch.setattr(
        attractor, "glial_verdict",
        lambda *a, **k: {"allow_generation": False, "glial": {}, "reason": "blocked"},
    )

    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    app = FastAPI()
    app.include_router(bs.create_brain_router())
    client = TestClient(app)
    resp = client.post("/brain/chat", json={"messages": []})
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("glial_gate", {}).get("reason") == "blocked"
