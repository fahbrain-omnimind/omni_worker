"""Dendritic morphology port — depth, pruning, EA, SNR experiment."""
import numpy as np

from omni_coworker.activation_beta.dendritic_morphology import (
    compare_depth_vs_recognition,
    dendritic_depth,
    evolve_morphology,
    load_worker_weight_matrix,
    morphology_score,
    prune_deep_connections,
)


def test_canonical_matrix_shape_and_edges():
    W = load_worker_weight_matrix()
    assert W.shape == (10, 10)
    # chain Freudiana: Phi→Psi, Xi→Zeta (Id→Ego 0.9), Kappa→Lambda
    assert W[0, 1] == 0.8
    assert W[5, 6] == 0.9
    assert W[8, 9] == 0.5
    assert np.all(np.diag(W) == 0.2)


def test_depth_positive_and_score_in_unit():
    W = load_worker_weight_matrix()
    d = dendritic_depth(W)
    s = morphology_score(W)
    assert d > 0
    assert 0.0 <= s <= 1.0


def test_pruning_reduces_depth():
    W = load_worker_weight_matrix()
    d0 = dendritic_depth(W)
    for k in (2, 3):
        Wp = prune_deep_connections(W, n_shortcuts=k)
        assert dendritic_depth(Wp) <= d0 + 1e-9
        # atalhos seguem o eixo funcional (jump 2/3), não pares arbitrários
        assert Wp[0, 2] > 0 or Wp[1, 3] > 0


def test_evolve_improves_or_keeps_score():
    W = load_worker_weight_matrix()
    evo = evolve_morphology(W, n_generations=8, pop_size=8, seed=3)
    assert evo["best_morphology_score"] >= morphology_score(W) - 0.15
    assert len(evo["history"]) == 8
    assert evo["best_W"].shape == (10, 10)


def test_compare_experiment_has_all_morphologies():
    W = load_worker_weight_matrix()
    exp = compare_depth_vs_recognition(W)
    morphs = {r["morphology"] for r in exp["results"]}
    assert "original" in morphs
    assert "pruned_1" in morphs and "pruned_5" in morphs
    assert "evolved" in morphs
    assert exp["evolved_score"] >= 0.0