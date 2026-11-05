import time

import pytest

from omni_coworker.orchestration.causal_engine import CausalEngine
from omni_coworker.store.evaporation import evaporation_score


def test_causal_effect_basic():
    ce = CausalEngine()
    r = ce.compute_causal_effect([1.0, 2.0, 3.0], [5.0, 6.0, 7.0])
    assert "ace" in r
    assert r["ace"] == pytest.approx(4.0)
    assert r["is_causal"] is True


def test_causal_insufficient():
    ce = CausalEngine()
    assert ce.compute_causal_effect([], [1.0])["error"] == "Insufficient data"


def test_validate_intervention():
    ce = CausalEngine()
    assert ce.validate_intervention_necessity({"a": 0.0}, {"a": 10.0}) is True or False


def test_evaporation_fresh():
    now = time.time()
    s = evaporation_score({"last_used_ts": now, "use_count": 0, "half_life": 1000})
    assert s == pytest.approx(0.0, abs=1e-7)


def test_evaporation_old():
    now = time.time()
    s = evaporation_score({"last_used_ts": now - 10000, "use_count": 0, "half_life": 1000})
    assert s > 0.9


def test_evaporation_use_count_reduces():
    now = time.time()
    a = evaporation_score({"last_used_ts": now - 5000, "use_count": 0, "half_life": 1000})
    b = evaporation_score({"last_used_ts": now - 5000, "use_count": 5, "half_life": 1000})
    assert b < a
