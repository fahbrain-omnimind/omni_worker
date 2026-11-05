"""Tests for glial gate."""


from omni_coworker.activation_beta import spiking_glial


def test_repetitive_signals_habituated_false():
    recs = [{"tags": ["x"]} for _ in range(30)]
    gate = spiking_glial.glial_gate({}, recs)
    assert gate["allow_generation"] is False


def test_high_stress_vagus_false():
    w = [{"pressure": 1.0} for _ in range(5)]
    gate = spiking_glial.glial_gate({}, w)
    assert gate["allow_generation"] is False


def test_healthy_true():
    w = [{"entropy": 0.5, "tags": ["a"]}, {"entropy": 0.6, "tags": ["b"]}]
    gate = spiking_glial.glial_gate({}, w)
    assert gate["allow_generation"] is True


def test_fail_open_exception(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("x")
    monkeypatch.setattr(spiking_glial, "glial_features", boom)
    gate = spiking_glial.glial_gate({}, [{"entropy": 1.0}])
    assert gate["allow_generation"] is True
    assert gate["reason"] == "fail-open"
