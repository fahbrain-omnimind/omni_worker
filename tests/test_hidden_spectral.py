"""hidden_spectral — eff_rank + MPS bond dims over synthetic sidecars."""

import numpy as np


def test_factor_sites():
    from omni_coworker.activation_beta.hidden_spectral import _factor_sites
    assert _factor_sites(256) == [2] * 8
    assert _factor_sites(1152) == [9] + [2] * 7   # pilot soberano: 1152=9·2⁷
    assert int(np.prod(_factor_sites(2560))) == 2560


def test_bond_dims_symmetric():
    from omni_coworker.activation_beta.hidden_spectral import _bond_dims
    rng = np.random.default_rng(0)
    v = rng.normal(size=256)
    v = v / np.linalg.norm(v)
    bd = _bond_dims(v)
    assert len(bd) == 7
    # random vector: cresce até o meio e decresce — simétrico
    assert bd[0] <= bd[3] and bd[-1] <= bd[3]


def test_spectral_features_synthetic(tmp_path, monkeypatch):
    import omni_coworker.activation_beta.hidden_spectral as hs
    monkeypatch.setattr(hs, "_vec_dir", lambda: tmp_path)
    model, safe = "m/test", "m_test"
    rng = np.random.default_rng(1)
    # 3 gerações correlacionadas: vetores ~iguais → eff_rank baixo
    base = rng.normal(size=(6, 128))
    for k in range(3):
        v = (base + 0.01 * rng.normal(size=base.shape)).astype(np.float16)
        np.savez_compressed(tmp_path / f"000{k}_{safe}.npz",
                            vectors=v, model=model, ts="t")
    f = hs.spectral_features()
    assert model in f
    assert f[model]["eff_rank_mean"] < 3.0      # rank colapsado ≠ aleatório
    assert f[model]["bond_dim_max_mean"] is not None
    assert "não é Φ causal" in f[model]["note"]


def test_no_sidecars(tmp_path, monkeypatch):
    import omni_coworker.activation_beta.hidden_spectral as hs
    monkeypatch.setattr(hs, "_vec_dir", lambda: tmp_path / "nope")
    assert hs.spectral_features() == {}
