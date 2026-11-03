"""activation_beta — attractor features over activation windows."""
import numpy as np

from omni_coworker.activation_beta import attractor


def _rec(ent, norms, model="m1"):
    return {"model": model, "attention_entropy_last": ent,
            "layers": [{"layer": i, "norm": n} for i, n in enumerate(norms)]}


def setup_function():
    attractor.reset()


def test_features_need_window():
    attractor.push([_rec(2.0, [1.0] * 43)])
    assert attractor.features() == {}


def test_stable_window_low_score():
    for _ in range(10):
        attractor.push([_rec(2.0, [10.0 + i for i in range(43)])])
    f = attractor.features()["m1"]
    assert f["attractor_score"] == 0.0
    assert f["entropy_collapse"] == 0.0
    assert f["divergent_layer"] == 0  # all drift equal → argmax first


def test_entropy_collapse_and_drift():
    # stable first half, collapse + layer-5 spike in second half
    for _ in range(8):
        attractor.push([_rec(4.0, [10.0] * 43)])
    norms = [10.0] * 43
    for _ in range(8):
        norms[5] += 3.0
        attractor.push([_rec(1.0, list(norms))])
    f = attractor.features()["m1"]
    assert f["entropy_collapse"] > 0.5
    assert f["divergent_layer"] == 5
    assert f["drift_concentration"] > 0.8
    assert f["attractor_score"] > 0.4


def test_multimodel_windows():
    for _ in range(5):
        attractor.push([_rec(2.0, [1.0] * 10, model="a"),
                        _rec(3.0, [5.0] * 10, model="b")])
    f = attractor.features()
    assert set(f) == {"a", "b"}


def test_digest():
    attractor.push([_rec(2.0, [1.0] * 43)] * 5)
    d = attractor.digest(attractor.features())
    assert "m1" in d and "score=" in d


def test_bridge_attractor_beta():
    from omni_coworker.integration_loop import bion_bridge
    bundle = {"attractor": {"m1": {"attractor_score": 0.8,
                                  "entropy_collapse": 0.7,
                                  "norm_drift_mean": 2.0,
                                  "divergent_layer": 5,
                                  "drift_concentration": 0.9,
                                  "n_records": 16}}}
    out = bion_bridge.metabolize({"bundle": bundle}, arousal=0.2, cycle_n=1)
    assert out.get("attractor_score") == 0.8
    assert isinstance(out.get("attractor_alpha"), str)
