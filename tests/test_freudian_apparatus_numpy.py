"""Tests for freudian_apparatus_numpy port."""
import numpy as np

from omni_coworker.psychoanalysis.freudian_apparatus_numpy import (
    FreudianNeuralLayer,
    FreudianNeuron,
    FreudianPsychicApparatus,
    to_numpy,
)


def test_neuron_forward_shape_and_activation():
    n = FreudianNeuron(4, activation="tanh", seed=1)
    x = np.array([0.1, 0.2, -0.3, 0.4])
    y = n.forward(x)
    assert isinstance(y, (float, np.floating))
    assert -1.0 <= float(y) <= 1.0
    # determinism
    n2 = FreudianNeuron(4, activation="tanh", seed=1)
    assert np.isclose(n2.forward(x), y)


def test_layer_forward_shape_and_noise():
    layer = FreudianNeuralLayer(5, input_dim=3, seed=2)
    x = np.array([1.0, 2.0, 3.0])
    out = layer.forward(x)
    assert isinstance(out, np.ndarray)
    assert out.shape == (5,)
    # noise optional changes output when enabled (seeded)
    out2 = layer.forward(x, noise=0.1)
    assert out2.shape == (5,)


def test_apparatus_layers_present_and_forward_shape():
    app = FreudianPsychicApparatus(seed=7)
    assert hasattr(app, "id") and hasattr(app, "ego") and hasattr(app, "superego")
    assert hasattr(app, "id_layer") and hasattr(app, "ego_layer") and hasattr(app, "superego_layer")
    x = np.zeros(8)
    res = app.forward(x)
    assert isinstance(res, dict)
    assert "id" in res and "ego" in res and "superego" in res
    assert res["id"].shape == (app.n_id,)
    assert res["ego"].shape == (app.n_ego,)
    assert res["superego"].shape == (app.n_superego,)
    # activations sub-dict
    assert "activations" in res
    assert set(res["activations"].keys()) == {"id", "ego", "superego"}


def test_determinism_with_seed():
    x = np.linspace(-1, 1, 8)
    a = FreudianPsychicApparatus(seed=42)
    b = FreudianPsychicApparatus(seed=42)
    ra = a.forward(x)
    rb = b.forward(x)
    np.testing.assert_allclose(ra["id"], rb["id"])
    np.testing.assert_allclose(ra["ego"], rb["ego"])
    np.testing.assert_allclose(ra["superego"], rb["superego"])
    # different seed differs
    c = FreudianPsychicApparatus(seed=99)
    rc = c.forward(x)
    assert not np.allclose(ra["id"], rc["id"])


def test_to_numpy_helper():
    app = FreudianPsychicApparatus(seed=1)
    x = np.ones(4)
    res = app.forward(x)
    arr = to_numpy(res)
    assert isinstance(arr, dict)
    assert "id" in arr
    # method
    arr2 = app.to_numpy()
    assert isinstance(arr2, dict)
