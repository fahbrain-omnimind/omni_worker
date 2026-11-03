"""tests/test_spiking_glial.py"""
import numpy as np

from omni_coworker.activation_beta import spiking_glial


def test_bridge_basic_state():
    b = spiking_glial.SpikingGlialVagusBridge(rate=0.2, window=8)
    assert b.state()["pause_code"] is None
    b.observe(0.1, ("topic",))
    st = b.state()
    assert "habituated" in st and "sensitized" in st
    assert "vagus_sedative" in st


def test_habituation_increases_with_repeats():
    b = spiking_glial.SpikingGlialVagusBridge(rate=0.3, window=8)
    for _ in range(5):
        b.observe(0.2, ("t1",))
    st = b.state()
    assert st["habituated"] > 0.0


def test_sensitization_strong_signals():
    b = spiking_glial.SpikingGlialVagusBridge(rate=0.3, window=8, threshold=0.5)
    for _ in range(4):
        b.observe(2.0, ("err",))
    st = b.state()
    assert st["sensitized"] > 0.0


def test_vagus_pause_on_high_stress():
    b = spiking_glial.SpikingGlialVagusBridge(rate=0.3, window=8, threshold=0.5)
    for _ in range(4):
        b.observe(-2.0, ("x",))
    st = b.state()
    assert st["pause_code"] == "pause_code"
    assert st["vagus_sedative"] >= 0.5


def test_glial_features_floats():
    w = [0.1, 0.2, 0.3, 0.4]
    f = spiking_glial.glial_features(w)
    assert f["n"] == 4
    assert "habituated" in f


def test_glial_features_dicts():
    w = [{"entropy": 2.0, "tags": ("a",)}, {"entropy": 1.5, "pressure": 2.0, "tags": ("a",)}]
    f = spiking_glial.glial_features(w)
    assert f["n"] == 2
    assert f["pause_code"] == "pause_code"


def test_empty():
    f = spiking_glial.glial_features([])
    assert f["n"] == 0
    assert f["pause_code"] is None
