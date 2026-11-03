"""phi_layer — informational integration proxies over activation windows."""
import numpy as np

from omni_coworker.activation_beta import attractor, phi_layer


def _rec(ent, norms, model="m1"):
    return {"model": model, "attention_entropy_last": ent,
            "layers": [{"layer": i, "norm": n} for i, n in enumerate(norms)]}


def setup_function():
    attractor.reset()


def test_features_need_min_window(tmp_path, monkeypatch):
    # isola sidecars do runtime (brains vivos escrevem .npz reais)
    monkeypatch.setenv("OMNI_ACT_VEC_DIR", str(tmp_path / "vecs"))
    attractor.push([_rec(2.0, [1.0] * 43)] * 4)
    assert phi_layer.features() == {}


def test_flat_profile_max_breadth():
    # all layers equal norm → uniform profile → breadth ≈ 1
    for _ in range(12):
        attractor.push([_rec(2.0, [10.0] * 43)])
    f = phi_layer.features()["m1"]
    assert f["phi_breadth"] > 0.95
    assert 0.0 <= f["phi_internal"] <= 1.0


def test_spiked_profile_low_breadth():
    norms = [0.01] * 43
    norms[20] = 100.0  # single hot layer
    for _ in range(12):
        attractor.push([_rec(2.0, list(norms))])
    f = phi_layer.features()["m1"]
    assert f["phi_breadth"] < 0.3


def test_temporal_mi_positive_when_covarying():
    rng = np.random.default_rng(7)
    base = rng.normal(0, 1, 16)
    for i in range(16):
        # adjacent layers co-vary strongly
        norms = [10 + base[i] * 5 + 0.1 * j for j in range(12)]
        attractor.push([_rec(2.0, norms)])
    f = phi_layer.features()["m1"]
    assert f["phi_temporal_mi"] is not None
    assert f["phi_temporal_mi"] > 0.1
