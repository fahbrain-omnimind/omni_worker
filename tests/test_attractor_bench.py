"""attractor_bench: Hopfield + RBM-CD1 reais + benches executáveis."""

from __future__ import annotations

import numpy as np

from omni_coworker.activation_beta.attractor_bench import (
    Hopfield, RBM, bench_dmn_proxy, bench_energy_perturbation,
    bench_rbm_vs_hopfield)


def _patterns(n=32, k=4, seed=5):
    return np.random.default_rng(seed).choice([-1.0, 1.0], size=(k, n))


def test_hopfield_recall_from_noisy_cue():
    # n=64, 4 padrões → carga ~6% << capacidade ~0.138n: recall exato
    hop = Hopfield(64, seed=1)
    pats = _patterns(n=64)
    hop.store(pats)
    cue = pats[0].copy()
    cue[:8] *= -1
    rec, iters = hop.recall(cue)
    assert np.array_equal(rec, pats[0])
    assert iters < 30
    # energia do atrator < energia do cue ruidoso (bacia real)
    assert hop.energy(rec) < hop.energy(cue)


def test_rbm_cd1_reduces_reconstruction_error():
    rbm = RBM(24, 8, seed=1)
    data = (np.random.default_rng(0).choice([0.0, 1.0], size=(4, 24)))
    err_first, err_last = None, None
    for ep in range(60):
        for v in data:
            e = rbm.train_step(v, lr=0.1)
        if ep == 0:
            err_first = e
        err_last = e
    assert err_last < err_first


def test_bench_energy_perturbation():
    hop = Hopfield(32, seed=1)
    hop.store(_patterns())
    out = bench_energy_perturbation(hop, n_trials=16)
    assert out["n_trials"] == 16
    assert 0.0 <= out["mean_recall_accuracy"] <= 1.0
    assert out["mean_recovery_iters"] > 0


def test_bench_dmn_proxy_wanders_or_collapse():
    hop = Hopfield(32, seed=1)
    hop.store(_patterns())
    out = bench_dmn_proxy(hop, n_steps=100, noise=0.4, seed=9)
    assert out["switches"] >= 0
    assert 0 < out["mean_dwell"] <= 100


def test_bench_rbm_vs_hopfield_ab():
    out = bench_rbm_vs_hopfield(n=24, n_patterns=3, epochs=40, seed=4)
    assert 0.0 <= out["hopfield_mean_overlap"] <= 1.0
    assert 0.0 <= out["rbm_mean_overlap"] <= 1.0
    # Hopfield armazena exato: overlap deve ser alto sob 30% de ruído
    assert out["hopfield_mean_overlap"] >= 0.8
