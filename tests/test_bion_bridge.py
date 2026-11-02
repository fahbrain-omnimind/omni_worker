"""bion_bridge wiring — β→α metabolization inside the loop."""
import time

from omni_coworker.integration_loop import bion_bridge


def _bundle(homeo_state="optimal"):
    return {
        "ts": time.time(),
        "models": {"gemma4": {"gen_tokens_mean": 10, "attention_entropy_mean": 2.1}},
        "soul": {"phi": 0.4},
        "soma": {"cpu_percent": 20.0, "gpu_vram_used_gb": 9.0},
        "homeostasis": {"state": homeo_state, "action": "none"},
        "drift": {},
    }


def test_metabolize_heuristic_tier():
    out = bion_bridge.metabolize({"bundle": _bundle()}, arousal=0.2, cycle_n=3)
    assert out["metabolized"] is True
    assert out["tier"] == "heuristic"
    assert out["beta_charge"] == 0.2
    assert isinstance(out["alpha_content"], str) and out["alpha_content"]
    assert 0.0 <= out["symbolic_potential"] <= 1.0


def test_metabolize_llm_gating():
    # processable + aroused → llm_chain tier
    out = bion_bridge.metabolize({"bundle": _bundle()}, arousal=0.45, cycle_n=1)
    assert out["tier"] == "llm_chain"
    # charge ≥ 0.6 → unprocessable β: heuristic tier + unmetabolized flag
    out2 = bion_bridge.metabolize({"bundle": _bundle()}, arousal=0.9, cycle_n=1)
    assert out2["tier"] == "heuristic"
    assert out2.get("beta_unmetabolized") is True
    # homeostasis degraded + processable → LLM tier
    out3 = bion_bridge.metabolize({"bundle": _bundle("warning")}, arousal=0.4, cycle_n=1)
    assert out3["tier"] == "llm_chain"


def test_metabolize_empty_bundle_no_raise():
    out = bion_bridge.metabolize({"bundle": {}}, arousal=0.0, cycle_n=0)
    assert "metabolized" in out  # never raises


def test_digest_content():
    d = bion_bridge._digest(_bundle())
    assert "gemma4" in d and "homeo=optimal" in d and "phi=0.4" in d
