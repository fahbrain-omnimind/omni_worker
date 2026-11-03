"""Tests for the Markov blanket port + PyPhi TPM construction."""

import numpy as np
import pytest

from omni_coworker.psychoanalysis import markov_blanket as mb


def _run(alpha: float, t: int = 120, seed: int = 0):
    rng = np.random.default_rng(seed)
    st = mb.BlanketState()
    z = np.array([0.1, -0.1])
    obs = None
    for _ in range(t):
        if rng.random() < 0.25:  # world shifts like the sovereign t=30
            z = np.array([0.62, 0.38])
        st, obs = mb.blanket_step(
            st, z, alpha, rng.normal(0, mb.NOISE_STD, 2), rng)
    return st, obs


def test_mobius_add_stays_in_disk():
    rng = np.random.default_rng(1)
    for _ in range(50):
        u = rng.uniform(-0.7, 0.7, 2)
        v = rng.uniform(-0.3, 0.3, 2)
        out = mb.mobius_add(u, v)
        assert np.dot(out, out) <= 1.0 + 1e-9


def test_moderate_alpha_lets_belief_approach_target():
    st, obs = _run(0.35)
    # α=0.35 with world at target: belief should get meaningfully closer
    assert obs["dH"] < 2.0


def test_resistance_bounded_and_permeable():
    for alpha in (0.05, 0.35, 0.85):
        st, obs = _run(alpha, t=60)
        assert 0.0 <= st.r <= 1.0
        assert 0.05 <= obs["permeability"] <= 0.95


def test_binarize_uses_sovereign_thresholds():
    st = mb.BlanketState(mu=np.array([0.6, 0.4]), r=0.5,
                         tau=np.array([0.8, 0.0]))
    bits = mb.binarize(np.array([0.62, 0.38]), st,
                       {"dH": mb.hyperbolic_dist(st.mu, mb.TARGET)})
    assert bits == (1, 1, 1, 1)


def test_tpm_row_stochastic_and_persistent():
    joint, sbn, meta = mb.build_tpm(0.35, k=40, seed=3)
    assert np.allclose(joint.sum(1), 1.0, atol=1e-9)
    # states are largely self-persistent at the binary grain
    assert np.diag(joint).mean() > 0.5
    assert sbn.shape == (16, 4)


def test_tpm6_unreachable_absorbing():
    joint, sbn, meta = mb.build_tpm(0.35, k=40, seed=3, nodes6=True)
    assert joint.shape == (64, 64)
    assert np.allclose(joint.sum(1), 1.0, atol=1e-9)
    # dynamics rule out a large chunk of the binary space (e.g. R=0∧P=0)
    assert len(meta["unreachable"]) > 10
    for s in meta["unreachable"]:
        assert joint[s, s] == 1.0


def test_pyphi_irreducible_core_mr():
    import collections
    import collections.abc
    for n in ("Iterable", "Mapping", "Sequence", "Hashable", "Callable"):
        if not hasattr(collections, n):
            setattr(collections, n, getattr(collections.abc, n))
    pyphi = pytest.importorskip("pyphi")
    pyphi.config.PROGRESS_BARS = False
    pyphi.config.VALIDATE_CONDITIONAL_INDEPENDENCE = False
    joint, _, _ = mb.build_tpm(0.05, k=80, seed=0)
    net = pyphi.Network(joint, cm=mb.connectivity_matrix())
    # {M,R} carries the blanket's causal core: belief↔resistance loop.
    sub = pyphi.Subsystem(net, (1, 0, 1, 1), nodes=(1, 2))
    assert pyphi.compute.phi(sub) >= 0.0  # finite, irreducible-ish
    # independence null → zero
    mean_row = joint.mean(axis=0)
    null = np.tile(mean_row, (16, 1))
    net0 = pyphi.Network(null, cm=mb.connectivity_matrix())
    assert pyphi.compute.phi(pyphi.Subsystem(net0, (1, 0, 1, 1),
                                             nodes=(1, 2))) == pytest.approx(0.0, abs=1e-9)
