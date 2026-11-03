"""Herméticos: quilting + defense_mechanisms."""

from __future__ import annotations

import numpy as np

from omni_coworker.integration_loop.quilting import detect_quilting_point
from omni_coworker.psychoanalysis.defense_mechanisms import assess


def test_quilting_none_insufficient():
    assert detect_quilting_point([[1.0, 2.0]] * 2) is None


def test_quilting_converges():
    base = [0.5, 0.5, 0.5]
    seq = [base[:] for _ in range(6)]
    out = detect_quilting_point(seq, ["topicA"] * 6)
    assert out is not None
    assert out["fixed_topic"] == "topicA"
    assert 0 <= out["stability"] <= 1
    assert "window" in out


def test_quilting_no_convergence():
    rng = np.random.default_rng(0)
    seq = rng.normal(size=(8, 4)).tolist()
    assert detect_quilting_point(seq, ["t"] * 8) is None


def test_quilting_wire_live_convergent(tmp_path, monkeypatch):
    """Ciclos reais run_once: bundle estavel → quilting_point no payload."""
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))
    import omni_coworker.integration_loop.store as st
    from omni_coworker.integration_loop import loop
    st._RING.clear()
    stable = {"models": {"analyst": {"prompt_tokens_mean": 10.0,
                                     "gen_tokens_mean": 20.0,
                                     "gen_tokens_max": 30.0,
                                     "attention_entropy_mean": 1.5,
                                     "hidden_norm_mean": 5.0,
                                     "hidden_norm_std": 0.1,
                                     "last_layer_norm_mean": 6.0,
                                     "n_records": 4}},
              "soma": {"cpu_percent": 30.0, "gpu_vram_used_gb": 8.0,
                       "gpu_util_percent": 20.0},
              "soul": {"phi": 0.5, "psi": 0.4, "sigma": 0.3, "epsilon": 0.2}}
    fired = 0
    for _ in range(8):
        c = loop.run_once(dict(stable))
        qp = ((c["stage_states"].get("narrative") or {})
              .get("metadata") or {}).get("quilting_point")
        if qp:
            fired += 1
    assert fired >= 4, f"quilting deveria fixar em regime convergente ({fired})"


def test_quilting_wire_live_divergent(tmp_path, monkeypatch):
    """Ciclos reais run_once: bundles aleatorios → sem quilting_point."""
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))
    import omni_coworker.integration_loop.store as st
    from omni_coworker.integration_loop import loop
    st._RING.clear()
    rng = np.random.default_rng(7)
    fired = 0
    for _ in range(8):
        b = {"models": {"analyst": {
                 "prompt_tokens_mean": float(rng.uniform(0, 100)),
                 "attention_entropy_mean": float(rng.uniform(0, 5)),
                 "hidden_norm_mean": float(rng.uniform(0, 50)),
                 "n_records": 1}},
             "soma": {"cpu_percent": float(rng.uniform(0, 100))},
             "soul": {"phi": float(rng.uniform(0, 1)),
                      "psi": float(rng.uniform(0, 1)),
                      "sigma": float(rng.uniform(0, 1)),
                      "epsilon": float(rng.uniform(0, 1))}}
        c = loop.run_once(b)
        qp = ((c["stage_states"].get("narrative") or {})
              .get("metadata") or {}).get("quilting_point")
        if qp:
            fired += 1
    assert fired == 0, f"quilting nao deveria fixar em regime divergente ({fired})"


def test_defense_keys_and_range():
    res = assess({"negation_count": 2, "length": 10, "ambiguity": 0.5, "threat_score": 0.8})
    assert set(res.keys()) == {
        "recalque","projecao","introjecao","identificacao_projetiva","splitting",
        "sublimacao","negacao","racionalizacao","formacao_reativa","deslocamento",
        "foraclusao","clivagem",
    }
    assert all(0.0 <= v <= 1.0 for v in res.values())


def test_defense_empty():
    res = assess({})
    assert all(v == 0.0 or isinstance(v, float) for v in res.values())
