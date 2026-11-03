"""PhylogeneticSignature: assinatura emergente deste chassi."""

from __future__ import annotations

import numpy as np

from omni_coworker.narrative.phylogenetic_signature import (
    PhylogeneticSignature)


def test_attractors_seeded_this_chassis(tmp_path, monkeypatch):
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))
    sig = PhylogeneticSignature(dimension=64)
    assert 3 <= len(sig.attractors) <= 5
    for a in sig.attractors:
        assert abs(np.linalg.norm(a) - 1.0) < 1e-6


def test_emergence_converges_and_persists(tmp_path, monkeypatch):
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))
    sig = PhylogeneticSignature(dimension=64)
    state = sig.emerge_from_noise(iterations=600)
    assert state.coherence > 0.3
    assert state.stability > 0.85
    assert state.emergence_complete
    assert abs(np.linalg.norm(state.signature_vector) - 1.0) < 1e-6
    # persistiu neste chassi
    sig2 = PhylogeneticSignature(dimension=64)
    assert sig2.state.emergence_complete
    assert np.allclose(sig2.state.signature_vector,
                       state.signature_vector, atol=1e-6)


def test_is_self_resonance(tmp_path, monkeypatch):
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))
    sig = PhylogeneticSignature(dimension=64)
    sig.emerge_from_noise(iterations=600)
    own = sig.is_self(sig.state.signature_vector)
    assert own > 0.9
    other = np.random.default_rng(9).normal(0, 1, 64)
    assert sig.is_self(other) < own
    # pré-emergência → 0.0
    fresh_dir = tmp_path / "fresh"
    monkeypatch.setenv("OMNI_STATE_DIR", str(fresh_dir))
    sig2 = PhylogeneticSignature(dimension=64)
    assert sig2.is_self(own * 0 + np.ones(64)) == 0.0


def test_ingest_model_aggregates_folds_attractor(tmp_path, monkeypatch):
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))
    sig = PhylogeneticSignature(dimension=64)
    n0 = len(sig.attractors)
    n1 = sig.ingest_model_aggregates(
        np.random.default_rng(0).normal(0, 1, (4, 128)))
    assert n1 == n0 + 1
    assert sig._model_aggregate is not None
    assert abs(np.linalg.norm(sig._model_aggregate) - 1.0) < 1e-6


def test_sandbox_self_resonance_with_signature(tmp_path, monkeypatch):
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))
    from omni_coworker.narrative.lalangue import LalangueSandbox
    sig = PhylogeneticSignature(dimension=8)
    sig.emerge_from_noise(iterations=600)
    sb = LalangueSandbox(signature=sig)
    sb.speak_to_self(sig.state.signature_vector[:8])
    d = sb.internal_dialogue[-1]
    assert d["self_resonance"] > 0.9
