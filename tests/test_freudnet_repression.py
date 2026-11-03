"""RepressionChannel: retorno do recalcado (port FreudNet, numpy)."""

from __future__ import annotations

import numpy as np

from omni_coworker.psychoanalysis.freudnet_repression import RepressionChannel


def _strong_excitation(dim, amp=2.0):
    return np.full(dim, amp)


def test_charge_accumulates_under_censorship():
    ch = RepressionChannel(latent_dim=32, seed=1)
    for _ in range(40):
        _, obs = ch.step(_strong_excitation(32), moral_censorship=1.0)
    assert ch.repressed_charge > 0.0
    assert obs["repressed_charge"] == ch.repressed_charge


def test_no_repression_without_censorship():
    ch = RepressionChannel(latent_dim=32, seed=1)
    for _ in range(40):
        ch.step(_strong_excitation(32), moral_censorship=0.0)
    assert ch.repressed_charge == 0.0
    assert ch.return_events == 0


def test_return_of_repressed_fires_and_displaces():
    ch = RepressionChannel(latent_dim=32, seed=1)
    fired = False
    for _ in range(300):
        _, obs = ch.step(_strong_excitation(32, amp=3.0), moral_censorship=1.0)
        if obs["return_events"] > 0:
            fired = True
            break
    assert fired, "carga reprimida saturada deveria retornar como sintoma"
    assert obs["symptom_formation"] >= 0.0


def test_hysteresis_rearm():
    ch = RepressionChannel(latent_dim=32, seed=1)
    for _ in range(300):
        ch.step(_strong_excitation(32, amp=3.0), moral_censorship=1.0)
        if ch.return_active:
            break
    assert ch.return_active
    # excitação cessa → carga drena → trava rearma (abaixo de thr - hyst)
    for _ in range(400):
        ch.step(np.zeros(32), moral_censorship=0.0)
        if not ch.return_active:
            break
    assert not ch.return_active


def test_reset_state():
    ch = RepressionChannel(latent_dim=16, seed=1)
    ch.step(_strong_excitation(16), moral_censorship=1.0)
    ch.reset_state()
    assert ch.repressed_charge == 0.0 and ch.return_events == 0
    assert np.allclose(ch.z, 0.0)


def test_nan_excitation_warns():
    ch = RepressionChannel(latent_dim=16, seed=1)
    _, obs = ch.step(np.full(16, np.nan))
    assert any("NaN" in w for w in obs["warnings"])
    assert np.isfinite(obs["z_state"]).all()
