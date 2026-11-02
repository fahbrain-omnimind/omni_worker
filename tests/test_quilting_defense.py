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
