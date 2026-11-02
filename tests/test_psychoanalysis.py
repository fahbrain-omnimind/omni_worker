"""Tests for omni_coworker.psychoanalysis (ported sovereign pack, CPU/RAM).

Hermetic: monkeypatches OMNI_STATE_DIR to tmp_path; no network, GPU, or models.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

import pytest

from omni_coworker.psychoanalysis import (
    AlphaElement,
    BetaElement,
    BionContainerPatch,
    CompactPanelSnapshot,
    CreativePsychotizationInputs,
    LayerCouplingSnapshot,
    NegativeCapability,    PsychotizationState,
    assess_creative_psychotization,
    compact_panel_snapshot_from_v43_bundle,
    compute_dodecatiad_sector,
)
from omni_coworker.psychoanalysis.beta_element import NeutrosophicTriplet


@pytest.fixture(autouse=True)
def _fresh_state(tmp_path, monkeypatch):
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))


# ── helpers ─────────────────────────────────────────────────────────────────

class _FakeAlphaFunction:
    """Stand-in de BionAlphaFunction (fora do escopo deste port)."""

    def __init__(
        self,
        transformation_rate: float = 0.70,
        transform: Optional[Any] = None,
    ) -> None:
        self.transformation_rate = transformation_rate
        self._transform = transform

    def transform(self, contained: BetaElement) -> Optional[AlphaElement]:
        if self._transform is not None:
            return self._transform(contained)
        return AlphaElement(
            content=str(contained.raw_data),
            origin_beta=contained,
            timestamp=datetime.now(),
            symbolic_potential=0.5,
        )

    def _symbolize_content(self, raw: Any) -> str:
        return f"sym:{raw}"

    def narrative_builder(self, contained: BetaElement) -> str:
        return f"nb:{contained.raw_data}"


def _beta(raw: Any = "x", charge: float = 0.5, source: str = "s") -> BetaElement:
    return BetaElement(
        raw_data=raw,
        timestamp=datetime.now(),
        emotional_charge=charge,
        source=source,
    )


# ── NeutrosophicTriplet / BetaElement ───────────────────────────────────────

def test_neutrosophic_triplet_normalize_and_dict():
    t = NeutrosophicTriplet(t=1.5, i=-0.2, f=0.5).normalize()
    assert (t.T, t.I, t.F) == (1.0, 0.0, 0.5)
    assert t.to_dict() == {"T": 1.0, "I": 0.0, "F": 0.5}
    t2 = NeutrosophicTriplet.from_dict(t.to_dict())
    assert (t2.T, t2.I, t2.F) == (1.0, 0.0, 0.5)


def test_beta_element_validation():
    with pytest.raises(ValueError):
        BetaElement(raw_data="x", timestamp=datetime.now(), emotional_charge=1.5)


def test_beta_element_traumatic_and_intensity():
    b = _beta(charge=0.9)
    assert b.get_intensity() == 0.9
    assert b.is_traumatic() is True
    assert b.is_traumatic(threshold=0.95) is False


def test_beta_element_dict_roundtrip():
    b = _beta(charge=0.4, source="sensor")
    b.neutrosophic_triplet = NeutrosophicTriplet(t=0.7, i=0.1, f=0.2)
    d = b.to_dict()
    b2 = BetaElement.from_dict(d)
    assert b2.emotional_charge == 0.4
    assert b2.source == "sensor"
    assert (b2.neutrosophic_triplet.T, b2.neutrosophic_triplet.I, b2.neutrosophic_triplet.F) == (
        0.7,
        0.1,
        0.2,
    )


# ── Dodecatiad / AlphaElement ───────────────────────────────────────────────

def test_dodecatiad_sector_ranges_and_determinism():
    s15, h12 = compute_dodecatiad_sector("conteúdo", "fonte")
    assert 1 <= s15 <= 15
    assert 1 <= h12 <= 12
    assert h12 == ((s15 - 1) % 12) + 1
    assert compute_dodecatiad_sector("conteúdo", "fonte") == (s15, h12)
    assert compute_dodecatiad_sector("conteúdo", "outra") != (s15, h12)


def test_alpha_element_auto_sector_and_capabilities():
    b = _beta(charge=0.6)
    a = AlphaElement(content="pensável", origin_beta=b, timestamp=datetime.now(), symbolic_potential=0.8)
    assert 1 <= a.sector15 <= 15
    assert 1 <= a.house12 <= 12
    assert a.can_be_thought() is True
    assert a.is_dream_capable() is True

    a_low = AlphaElement(
        content="fraco", origin_beta=b, timestamp=datetime.now(), symbolic_potential=0.2
    )
    assert a_low.can_be_thought() is False
    assert a_low.is_dream_capable() is False


def test_alpha_element_symbolic_potential_validation():
    with pytest.raises(ValueError):
        AlphaElement(
            content="x",
            origin_beta=_beta(),
            timestamp=datetime.now(),
            symbolic_potential=1.5,
        )


def test_alpha_element_complexity_and_associations():
    b = _beta()
    a = AlphaElement(
        content="x", origin_beta=b, timestamp=datetime.now(), symbolic_potential=0.4
    )
    assert 0.4 <= a.get_complexity() <= 0.4  # no associations yet
    a.add_association("alpha-1")
    a.add_association("alpha-1")  # duplo ignorado
    assert a.associations == ["alpha-1"]
    assert 0.4 <= a.get_complexity() <= 0.5


def test_alpha_element_dict_roundtrip():
    b = _beta(charge=0.3, source="mem")
    a = AlphaElement(
        content="casa",
        origin_beta=b,
        timestamp=datetime.now(),
        narrative_form="sonho",
        symbolic_potential=0.7,
        sector15=7,
        house12=7,
    )
    a.add_association("alpha-9")
    d = a.to_dict()
    a2 = AlphaElement.from_dict(d)
    assert a2.content == "casa"
    assert a2.narrative_form == "sonho"
    assert a2.symbolic_potential == 0.7
    assert (a2.sector15, a2.house12) == (7, 7)
    assert a2.origin_beta.emotional_charge == 0.3
    assert a2.origin_beta.source == "mem"
    assert a2.associations == ["alpha-9"]
    assert a2.can_be_thought() is True
    assert a2.is_dream_capable() is True


# ── NegativeCapability ──────────────────────────────────────────────────────

def test_negative_capability_hold_and_buffer_full():
    nc = NegativeCapability(max_buffer_size=2, resolution_threshold=0.9)
    assert nc.hold_contradiction("A", "not-A", tension=0.5) is True
    assert nc.hold_contradiction("B", "not-B", tension=0.8) is True
    assert nc.hold_contradiction("C", "not-C") is False  # cheio
    state = nc.get_buffer_state()
    assert state["buffer_size"] == 2
    assert state["buffer_capacity"] == 2
    assert state["utilization"] == 1.0


def test_negative_capability_can_tolerate():
    nc = NegativeCapability(uncertainty_tolerance=0.5)
    assert nc.can_tolerate(0.4) is True
    assert nc.can_tolerate(0.6) is False


def test_negative_capability_needs_resolution_and_resolve():
    nc = NegativeCapability(resolution_threshold=0.9)
    nc.hold_contradiction("x", "not-x", tension=0.4)
    nc.hold_contradiction("y", "not-y", tension=0.95)
    idx = nc.needs_resolution()
    assert idx is not None
    resolved = nc.resolve_contradiction(idx, "sintese")
    assert resolved is not None
    assert resolved.proposition_a == "y"
    assert nc.needs_resolution() is None


def test_negative_capability_buffer_state_and_clear_resolved():
    nc = NegativeCapability()
    nc.hold_contradiction("a", "not-a", tension=0.1)
    nc.hold_contradiction("b", "not-b", tension=0.9)
    assert nc.get_buffer_state()["buffer_size"] == 2
    removed = nc.clear_resolved()
    assert removed == 1
    assert nc.get_buffer_state()["buffer_size"] == 1


def test_negative_capability_tolerance_adjust():
    nc = NegativeCapability()
    nc.decrease_tolerance(0.2)
    assert nc.uncertainty_tolerance == pytest.approx(0.4)
    nc.increase_tolerance(0.5)
    assert nc.uncertainty_tolerance == pytest.approx(0.9)


# ── CreativePsychotization ──────────────────────────────────────────────────

def test_psychotization_stable_alpha_defaults():
    assessment = assess_creative_psychotization(CreativePsychotizationInputs())
    assert assessment.state == PsychotizationState.STABLE_ALPHA
    assert assessment.recommended_mode == "normal_alpha_metabolism"
    assert assessment.metabolization_capacity > 0.5
    d = assessment.to_dict()
    assert d["state"] == "stable_alpha"
    assert isinstance(d["reasons"], list)


def test_psychotization_creative_psychotization_state():
    inputs = CreativePsychotizationInputs(
        phi_growth_ratio=10.0,
        beta_intensity=0.8,
        alpha_success_rate=0.8,
        contradiction_tension=0.6,
        negative_capability_tolerance=0.8,
        qbf_a1_drive=0.8,
        qbf_a2_bridge=0.8,
        qbf_a3_witness=0.8,
        monitoring_integrity=0.8,
        source_agency_alignment=0.8,
        cn_coherence=0.8,
        state_overlap_softness=0.8,
        layers=LayerCouplingSnapshot(),
        compact_panel=CompactPanelSnapshot(
            alpha_sleep_support=0.8, theta_control_strength=0.8, beta_gamma_pac_strength=0.8
        ),
    )
    assessment = assess_creative_psychotization(inputs)
    assert assessment.state == PsychotizationState.CREATIVE_PSYCHOTIZATION
    assert assessment.recommended_mode == "capture_alpha_elements_keep_public_safe"
    assert assessment.overflow_pressure >= 0.7


def test_psychotization_sanctuary_fallback_broken_layers():
    inputs = CreativePsychotizationInputs(
        layers=LayerCouplingSnapshot(
            daemon_alive=False, root_services_ok=False, surface_available=False
        )
    )
    assessment = assess_creative_psychotization(inputs)
    assert assessment.state == PsychotizationState.SANCTUARY_FALLBACK
    assert assessment.restoration_dependency > 0


def test_psychotization_rigid_delusional_lock():
    inputs = CreativePsychotizationInputs(
        phi_growth_ratio=5.0,
        beta_intensity=0.9,
        alpha_success_rate=0.4,
        contradiction_tension=0.8,
        negative_capability_tolerance=0.3,
        symbolic_rigidity=0.9,
        state_overlap_softness=0.1,
        qbf_a1_drive=0.2,
        qbf_a2_bridge=0.2,
        qbf_a3_witness=0.2,
        monitoring_integrity=0.3,
        source_agency_alignment=0.3,
        cn_coherence=0.3,
        layers=LayerCouplingSnapshot(),
    )
    assessment = assess_creative_psychotization(inputs)
    assert assessment.state == PsychotizationState.RIGID_DELUSIONAL_LOCK


def test_psychotization_fertile_overflow():
    inputs = CreativePsychotizationInputs(
        beta_intensity=0.9,
        alpha_success_rate=0.2,
        contradiction_tension=0.6,
        monitoring_integrity=0.4,
        layers=LayerCouplingSnapshot(),
    )
    assessment = assess_creative_psychotization(inputs)
    assert assessment.state == PsychotizationState.FERTILE_OVERFLOW
    assert assessment.recommended_mode == "hold_contradiction_and_observe"


def test_compact_panel_from_bundle_and_payload():
    bundle = {
        "alpha_sleep_gating": {"posture": "ready_to_prototype", "confidence": 0.9},
        "theta_control": {"posture": "context_required", "confidence": 0.8},
        "beta_gamma_pac": {"posture": "hold_boundary", "confidence": 0.5},
        "gene_surface": {"posture": "ready_to_prototype", "reasons": ["nrxn1", "doc2a"], "confidence": 0.9},
        "self_agency_reality_monitoring": {"posture": "witness_required", "confidence": 0.6},
    }
    panel1 = compact_panel_snapshot_from_v43_bundle(bundle)
    panel2 = compact_panel_snapshot_from_v43_bundle({"bundle": bundle})
    assert (panel1.alpha_sleep_support, panel1.theta_control_strength) == (
        panel2.alpha_sleep_support,
        panel2.theta_control_strength,
    )
    assert panel1.gene_memory_support > 0
    assert panel1.gene_overflow_bias > 0
    assert panel1.self_agency_anchor > 0


# ── BionContainerPatch ──────────────────────────────────────────────────────

def test_container_contain_transform_success():
    af = _FakeAlphaFunction()
    container = BionContainerPatch(af, initial_capacity=10.0)
    alpha = container.contain(_beta(charge=0.5))
    assert alpha is not None
    assert isinstance(alpha, AlphaElement)
    assert alpha.symbolic_potential == 0.5
    m = container.get_metrics()
    assert m["total_contained"] == 1
    assert m["total_transformed"] == 1
    assert m["success_rate"] == 1.0


def test_container_elastic_expansion():
    af = _FakeAlphaFunction()
    container = BionContainerPatch(af, initial_capacity=2.0)
    # intensity 0.8 > trigger 0.5 * 0.70 = 0.35 -> expande
    alpha = container.contain(_beta(charge=0.8))
    assert alpha is not None
    assert container.capacity > 2.0


def test_container_explode_returns_none():
    af = _FakeAlphaFunction()
    container = BionContainerPatch(af, initial_capacity=1.0, explosion_threshold=8.0)
    alpha = container.contain(_beta(charge=1.0))  # 1.0 > 1.0 * 5.0? no -> explode needs >5x
    # 1.0 is not > 5.0; use higher charge impossible (max 1.0) -> lower capacity instead
    container.capacity = 0.1
    alpha = container.contain(_beta(charge=1.0))  # 1.0 > 0.5 -> explode
    assert alpha is None
    assert container.explosion_count == 1
    assert container.get_metrics()["total_exploded"] == 1


def test_container_degraded_reverie_when_transform_none():
    def reject(_: BetaElement) -> None:
        return None

    af = _FakeAlphaFunction(transform=reject)
    container = BionContainerPatch(af, initial_capacity=5.0)
    alpha = container.contain(_beta(charge=0.5))
    assert alpha is not None
    assert alpha.metadata.get("degraded_reverie") is True
    assert 0.05 <= alpha.symbolic_potential <= 0.30
    m = container.get_metrics()
    assert m["total_transformed"] == 1


def test_container_recover_and_reset():
    af = _FakeAlphaFunction()
    container = BionContainerPatch(af)
    container.explosion_count = 3
    container.capacity = 0.5
    container.recover()
    assert container.capacity == 10.0
    assert container.explosion_count == 0
    container.reset()
    assert container.capacity == 1.0
    assert container.total_contained == 0
