"""Ports OW-STU-012 — EWC, neuroanatomy, plasticity resource."""
import numpy as np

from omni_coworker.activation_beta.neuroanatomy import PsychicNeuroanatomicalMapping
from omni_coworker.agency.ewc import ElasticWeightConsolidation
from omni_coworker.psychoanalysis.plasticity_resource import (
    ActivationWindowInputs,
    AttentionEntropyInputs,
    HomeostasisInputs,
    ResourceLane,
    ResourcePosture,
    ThermalInputs,
    VramPressureInputs,
    assess_activation_window,
    assess_attention_entropy,
    assess_homeostasis,
    assess_thermal,
    assess_vram_pressure,
    assess_worker_bundle,
)


# --- EWC -------------------------------------------------------------------
def test_ewc_fisher_from_successful_decisions():
    ewc = ElasticWeightConsolidation()
    ewc.compute_fisher_information(
        {"analyst": 0.5, "executor": 0.5},
        [{"type": "decision", "confidence": 0.9, "success": True,
          "contributing_agents": ["analyst"]}] * 10)
    assert ewc.fisher_matrix["analyst"] > ewc.fisher_matrix["executor"]


def test_ewc_penalty_damps_important_weights():
    ewc = ElasticWeightConsolidation()
    ewc.compute_fisher_information({"a": 0.5, "b": 0.5},
                                   [{"type": "decision", "confidence": 1.0,
                                     "success": True,
                                     "contributing_agents": ["a"]}] * 20)
    # mudança proposta é amortecida mais no peso importante
    out = ewc.adjust_weights_with_protection({"a": 0.5, "b": 0.5},
                                             {"a": +0.2, "b": +0.2})
    delta_a = out["a"] - 0.5
    delta_b = out["b"] - 0.5
    assert delta_b > delta_a > 0


def test_ewc_bounds_and_penalty_formula():
    ewc = ElasticWeightConsolidation()
    ewc.compute_fisher_information({"a": 0.9}, [])
    out = ewc.adjust_weights_with_protection({"a": 0.9}, {"a": +5.0})
    assert out["a"] <= 1.0
    loss = ewc.penalty_loss({"a": 0.9})
    assert loss == 0.0  # pesos idênticos → sem penalidade


# --- Neuroanatomy ----------------------------------------------------------
def test_neuroanatomy_mapping_covers_10_dims():
    m = PsychicNeuroanatomicalMapping()
    assert len(m.mappings) == 10
    assert m.mappings["omega"].primary_region == "pfc"


def test_synaptic_distribution_beta_dominant():
    m = PsychicNeuroanatomicalMapping()
    # upsilon (razão α/β 1.5 → α) e zeta (0.6 → β): estado com zeta alto
    state = np.zeros(10)
    state[6] = 1.0  # zeta (ego, β)
    d = m.compute_synaptic_distribution(state)
    assert d["beta_activity"] > d["alpha_activity"]
    assert d["alpha_beta_ratio"] < 1.0
    assert d["total_synaptic_load"] > 0


def test_synaptic_distribution_alpha_dominant():
    m = PsychicNeuroanatomicalMapping()
    state = np.zeros(10)
    state[0] = 1.0  # phi (percepção, α)
    d = m.compute_synaptic_distribution(state)
    assert d["alpha_beta_ratio"] > 1.0


# --- Plasticity resource ---------------------------------------------------
def test_vram_pressure_hold_boundary_at_limit():
    a = assess_vram_pressure(VramPressureInputs(vram_ratio=0.95,
                                                eviction_pending=True))
    assert a.posture == ResourcePosture.HOLD_BOUNDARY
    assert "evictar" in a.recommended_action
    assert a.lane == ResourceLane.VRAM_PRESSURE


def test_vram_pressure_ready_when_headroom():
    a = assess_vram_pressure(VramPressureInputs(vram_ratio=0.4))
    assert a.posture == ResourcePosture.READY_TO_PROTOTYPE


def test_attention_entropy_hold_on_collapse():
    a = assess_attention_entropy(AttentionEntropyInputs(
        entropy_mean=0.5, entropy_collapse=0.8, divergent_layer=True))
    assert a.posture == ResourcePosture.HOLD_BOUNDARY
    assert "degenera" in a.recommended_action


def test_thermal_hold_when_hot():
    a = assess_thermal(ThermalInputs(temp_ratio=0.95, throttling=True))
    assert a.posture == ResourcePosture.HOLD_BOUNDARY


def test_activation_window_ready_when_full():
    a = assess_activation_window(
        ActivationWindowInputs(n_records=40, min_window=6, rehydrated=True))
    assert a.posture == ResourcePosture.READY_TO_PROTOTYPE
    assert "phi_layer" in a.recommended_action


def test_homeostasis_hold_when_degraded():
    a = assess_homeostasis(HomeostasisInputs(state="degraded",
                                             producing=False, angst=3))
    assert a.posture == ResourcePosture.HOLD_BOUNDARY


def test_worker_bundle_aggregates():
    bundle = {"soma": {"vram_ratio": 0.95, "entropy_mean": 0.5,
                       "entropy_collapse": 0.0, "temp_ratio": 0.4},
              "homeostasis": {"state": "stable", "producing": True, "angst": 0}}
    out = assess_worker_bundle(bundle)
    assert len(out) == 4
    by_lane = {a.lane.value: a.posture for a in out}
    assert by_lane["vram_pressure"] == ResourcePosture.HOLD_BOUNDARY
    assert by_lane["thermal"] == ResourcePosture.READY_TO_PROTOTYPE
    assert all(a.to_dict()["lane"] for a in out)