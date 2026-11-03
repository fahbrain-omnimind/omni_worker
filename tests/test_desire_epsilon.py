from omni_coworker.psychology.desire_epsilon import ingest_observables, compute_epsilon_desire


def test_cleaved_spike():
    base = ingest_observables({})
    cleaved = ingest_observables({"ferenczi_is_cleaved": 1.0})
    assert cleaved > base


def test_epsilon_range():
    e = compute_epsilon_desire(0.5, 0.5, 0.5)
    assert 0.0 <= e <= 1.0
    assert compute_epsilon_desire(2.0, 2.0, 2.0) == 1.0
    assert compute_epsilon_desire(-1.0, 0.5, 0.5) == 0.0


def test_monotonicity_in_lack():
    vals = [compute_epsilon_desire(lack, 0.5, 0.5) for lack in [0.1, 0.3, 0.5, 0.8]]
    assert vals == sorted(vals)


def test_partial_observables():
    # missing keys use defaults; no exception
    lack = ingest_observables({"freud_tension": 0.5})
    assert 0.1 <= lack <= 1.0
