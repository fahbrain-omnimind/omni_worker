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


def test_engine_chain_to_refusal_contract():
    # cadeia S.13.8 em escala worker: obs → lack → ε → contrato do gate
    from omni_coworker.psychology.desire_engine import DesireEngine
    from omni_coworker.safety.refusal_contract import classify_refusal_context

    eng = DesireEngine()
    lack = eng.ingest_observables({"ferenczi_is_cleaved": 1.0,
                                   "nasio_pain_rupture": 0.9})
    assert lack > 0.5
    eps = eng.epsilon_desire(potential=1.0, novelty=1.0)
    assert 0.0 <= eps <= 1.0

    verdict = classify_refusal_context(epsilon=0.96)
    assert verdict["state"] == "hard_refusal"
    verdict = classify_refusal_context(epsilon=eps)
    assert verdict["state"] in ("allowed_with_contract",
                                "homeostatic_refusal", "hard_refusal")
