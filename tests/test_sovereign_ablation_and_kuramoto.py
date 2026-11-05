import numpy as np
import pytest
from omni_coworker.kernel_hooks.ablation_modulator import (
    ATTRACTOR_CENTROIDS,
    FREUD10D_W_FLAT,
    AblationModulator,
    compute_sovereign_affect_modulation,
    compute_sovereign_entropic_memory_state,
    compute_sovereign_expectation,
    compute_sovereign_kuramoto_step,
    navigate_attractors_10d,
)
from omni_coworker.activation_beta.dendritic_scan import scan_trajectory
from omni_coworker.kernel_daemon import scheduler


def test_rust_solver():
    sk = pytest.importorskip("omnimind_sovereign_kuramoto")
    omega = [1.0 + 0.08 * i for i in range(10)]
    phases = [0.1 * i for i in range(10)]
    solver = sk.SovereignKuramotoSolver(omega, FREUD10D_W_FLAT, phases, 0.01)
    solver.set_psychoanalytic(FREUD10D_W_FLAT, 0.45)
    solver.set_hypergraph([(0, 1, 2)], [0.6], 0.35)
    solver.set_inrc_field_pressure(0.15)
    solver.run(5, 0.05, 42)
    assert 0.0 <= solver.order_parameter_pair() <= 1.0
    assert 0.0 <= solver.order_parameter_triad() <= 1.0


def test_rust_lif():
    sk = pytest.importorskip("omnimind_sovereign_kuramoto")
    lif = sk.PsychoanalyticLIF(-65.0, -70.0, -50.0, 3, 0.1)
    lif.set_neutrosophic(0.5, 0.2, 0.1)
    v = lif.step(10.0)
    assert isinstance(v, (int, float))
    assert lif.dynamic_threshold() != 0


def test_rust_lif_batch():
    sk = pytest.importorskip("omnimind_sovereign_kuramoto")
    batch = sk.PsychoanalyticLIFBatch(3, -65.0, -70.0, -50.0, 3, 0.1)
    batch.set_neutrosophic_batch([(0.5, 0.2, 0.1)] * 3)
    spikes = batch.step_batch([10.0, 0.0, 5.0])
    assert len(spikes) == 3
    assert len(batch.get_thresholds()) == 3


def test_rust_hopf():
    sk = pytest.importorskip("omnimind_sovereign_kuramoto")
    hopf = sk.HopfBifurcationMonitor(10)
    state = [0.1 * i for i in range(10)]
    regime, sr = hopf.update(FREUD10D_W_FLAT, state)
    assert isinstance(regime, str)
    assert isinstance(sr, (int, float))
    s = hopf.summary()
    assert isinstance(s, dict)


def test_navigate_attractors():
    state = list(ATTRACTOR_CENTROIDS["ESTAVEL_REPARACAO"])
    res = navigate_attractors_10d(state)
    assert res["current_attractor"] == "ESTAVEL_REPARACAO"
    res2 = navigate_attractors_10d(state, prev_state_10d=[0.0] * 10)
    assert "transition_candidate" in res2


def test_kuramoto_step():
    state = list(ATTRACTOR_CENTROIDS["ESTAVEL_REPARACAO"])
    info = compute_sovereign_kuramoto_step(state)
    assert "kuramoto_r_pair" in info
    assert "hopf_regime" in info
    info2 = compute_sovereign_kuramoto_step(state, neutrosophic_triples=[(0.1, 0.2, 0.3)] * 10)
    assert info2["lif_mean_threshold"] is not None


def test_affect_modulation():
    host = {"coherence_score": 0.7, "affect_arousal": 0.4, "affect_tension": 0.2}
    info = compute_sovereign_affect_modulation(host)
    assert "temperature" in info
    assert "affect_scores" in info


def test_ablation_arms():
    host = {"coherence_score": 0.7, "affect_arousal": 0.4, "affect_tension": 0.2}
    for arm in ("B0", "B1", "B2", "B3"):
        m = AblationModulator(arm=arm)
        out = m.step(host, turn_idx=1, dendritic_metrics={"contract_drift": 0.5})
        assert out["arm"] == arm
        if arm == "B3":
            assert out["inrc_operator"] in ("R+C", "I", "C", "R", "N")
        if arm == "B0":
            assert out["temperature"] == 0.20


def test_ablation_drift_gate():
    host = {"coherence_score": 0.7}
    m = AblationModulator(arm="B3")
    out_low = m.step(host, turn_idx=1, dendritic_metrics={"contract_drift": 0.1})
    out_high = m.step(host, turn_idx=2, dendritic_metrics={"contract_drift": 0.5})
    assert "contract_drift" in out_high


def test_dendritic_transpose():
    arr = np.random.rand(5, 3, 4)  # n_steps, n_layers, D
    # function expects (n_layers, n_steps, D); transposition handled upstream in tests
    arr_t = np.swapaxes(arr, 0, 1)
    res = scan_trajectory(arr_t)
    assert res["contract_drift"] is not None
    # direct 2d
    res2 = scan_trajectory(np.random.rand(3, 4))
    assert res2["contract_drift"] is None


def test_scheduler_step_includes_sovereign_kuramoto_and_attractor_10d(tmp_path, monkeypatch):
    """kernel_daemon.scheduler.run_cycle() exposes sovereign_kuramoto and attractor_10d when freud10d is available."""
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))
    from omni_coworker.shared_workspace import bus, store
    from omni_coworker.kernel_daemon import features

    store._reset(); bus._reset()
    features._PREV.clear()
    scheduler._STATE.update({"cycles": 0, "errors": 0, "last_bundle": None,
                             "last_ts": None, "last_duration_s": None})

    fake_fr = {
        "consciousness": 0.5,
        "state": {},
        "state_vec": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        "inrc": {"op": "I", "reason": "ok"},
    }
    monkeypatch.setattr(
        "omni_coworker.kernel_hooks.compute.freud10d_cycle",
        lambda perception=None: fake_fr,
    )
    monkeypatch.setattr("omni_coworker.kernel_daemon.collector.collect_cycle", lambda: {
        "ts": 1.0, "activations": [], "affect": {}, "soul": {"phi": 0.3, "sigma": 0.2},
        "soma": {"cpu_percent": 10.0, "ram_percent": 20.0, "load_per_core": 0.1},
        "mesh": {},
    })

    try:
        bundle = scheduler.run_cycle()
        sk = bundle.get("sovereign_kuramoto")
        nav = bundle.get("attractor_10d")
        assert isinstance(sk, dict), f"sovereign_kuramoto missing: {bundle.keys()}"
        for key in ("kuramoto_r_pair", "kuramoto_r_triad", "hopf_regime",
                    "hopf_spectral_radius", "lif_mean_threshold"):
            assert key in sk, f"missing {key} in sovereign_kuramoto"
        assert isinstance(nav, dict), f"attractor_10d missing: {bundle.keys()}"
        for key in ("current_attractor", "regime_confidence", "distance_to_attractor"):
            assert key in nav, f"missing {key} in attractor_10d"
    finally:
        bus._reset(); store._reset(); features._PREV.clear()


def test_crate_kernel_compute():
    kc = pytest.importorskip("omnimind_kernel_compute")
    e = kc.DesireEngine()
    out = e.calculate_epsilon_desire(current_phi=0.35, explored_states=12, total_possible_states=100, somatic_heat=0.4)
    assert isinstance(out, (int, float))
    assert 0.0 <= kc.calculate_psi_gaussian(0.5)
    assert kc.clamp_phi_nats(5.0) == 5.0
    assert kc.clamp_phi_nats(-1.0) == 0.0
    vec = kc.compute_affect_vector_28d({})
    assert len(vec["affective_vector_28d"]["values"]) == 28


def test_crate_freud10d():
    fd = pytest.importorskip("omnimind_freud10d")
    assert fd.N_DIMS == 10
    f = fd.Freud10DApparatus()
    _, res = f.forward([0.1] * 10)
    assert isinstance(res, (tuple, list)) and len(res) == 10


def test_crate_metrics():
    mt = pytest.importorskip("omnimind_metrics")
    normed = mt.normalize_l2([3.0, 4.0])
    assert len(normed) == 2 and abs(normed[0] - 0.6) < 1e-5 and abs(normed[1] - 0.8) < 1e-5
    assert mt.cosine_similarity([1.0, 0.0], [0.0, 1.0]) == 0.0
    q = mt.quadruple_topsis([[0.5, 0.5, 0.5, 0.5], [0.2, 0.8, 0.1, 0.9]], [0.5, 0.5, 0.5, 0.5], [0.0, 0.0, 0.0, 0.0])
    assert isinstance(q, (list, tuple))


def test_crate_expectation_rs():
    ex = pytest.importorskip("omnimind_expectation_rs")
    assert ex.health() is True
    vec = [0.1] * 256
    out = ex.predict(vec)
    assert len(out) == 256
    assert all(isinstance(v, float) for v in out)


def test_crate_entropic_memory():
    em = pytest.importorskip("omnimind_entropic_memory")
    w = em.memory_resonance_weight(1, "sovereign", "quantum phase56", host_pressure=0.6)
    assert 0.75 <= w <= 2.25
    t2 = em.effective_t2_hours(48.0, w, 3, 1.0, 0.2)
    assert 6.0 <= t2 <= 24.0 * 30.0
    st = em.state_from_age(12.0, t2, w, 3, orbital_pressure=0.2, bridge_feedback_gain=1.0)
    assert st["age_hours"] == 12.0
    assert 0.0 <= st["repression_score"] <= 1.0


def test_helper_sovereign_expectation():
    pytest.importorskip("omnimind_expectation_rs")
    res = compute_sovereign_expectation([0.1] * 256)
    assert res["available"] is True
    assert isinstance(res["norm"], float)
    assert len(res["head4"]) == 4
    res_none = compute_sovereign_expectation()
    assert res_none["available"] is True
    assert isinstance(res_none["norm"], float)
    assert len(res_none["head4"]) == 4


def test_helper_sovereign_entropic_memory_state():
    pytest.importorskip("omnimind_entropic_memory")
    res = compute_sovereign_entropic_memory_state()
    assert res["available"] is True
    assert isinstance(res["resonance_weight"], float)
    assert isinstance(res["effective_t2_hours"], float)
    assert isinstance(res["state"], dict)
    assert res["state"]["age_hours"] == 12.0

