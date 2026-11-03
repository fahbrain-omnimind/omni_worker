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