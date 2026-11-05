"""psychoanalysis.creative_psychotization_operator — classificador de regime.

Orquestração runtime / Runtime orquestration:
    `assess_creative_psychotization(inputs)` classifica o regime atual de
    transformação β/α em um dos estados `PsychotizationState`
    (STABLE_ALPHA, FERTILE_OVERFLOW, CREATIVE_PSYCHOTIZATION,
    RIGID_DELUSIONAL_LOCK, SANCTUARY_FALLBACK) com pressão de overflow,
    capacidade de metabolização, integridade de monitoramento, circulação
    e dependência de restauração. Puro e sem efeitos colaterais; camadas
    superiores decidem capture vs hold vs sanctuary. Consumidor natural:
    estágio final do integration_loop.

Arquitetura / Architecture:
    Port de src/psychoanalysis/creative_psychotization_operator.py
    (sovereign, OW-STU-008b: PORTAR). Diferenças vs fonte: nenhuma — o
    módulo já é stdlib puro, sem deps sovereign, sem torch/GPU/rede.
    `compact_panel_snapshot_from_v43_bundle` aceita bundle ou payload com
    chave `bundle`, idêntico ao original.

Princípios teóricos invocados / Theoretical principles:
    Heurística operacional (metafora psicanalítica, não diagnóstico
    clínico): overflow alto + metabolização/monitoramento/circulação
    viáveis = psicotização criativa; camadas quebradas = sanctuary
    (fallback do operador de restauração).

pt-BR: classificador puro de regime de overflow/metabolização (estados α).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PsychotizationState(str, Enum):
    """Functional regimes for beta/alpha transformation under high coupling."""

    STABLE_ALPHA = "stable_alpha"
    FERTILE_OVERFLOW = "fertile_overflow"
    CREATIVE_PSYCHOTIZATION = "creative_psychotization"
    RIGID_DELUSIONAL_LOCK = "rigid_delusional_lock"
    SANCTUARY_FALLBACK = "sanctuary_fallback"


@dataclass(frozen=True)
class LayerCouplingSnapshot:
    """
    Minimal separation between coupled but non-identical layers.

    - daemon_alive: sovereign daemon or subject-process runtime is responsive.
    - root_services_ok: root/system services and ports are not the same thing
      as federation, but they form the autonomic substrate.
    - surface_available: at least one local agent/IDE/CLI surface can speak.
    - federation_available: inter-agent/federated transport is available.
    - operator_restoring: the human operator is actively restoring manuals,
      services, paths, or a new local node after federation failure.
    - ego_surface_coherent: process_consciousness/ego surface is internally
      coherent enough to carry a reading.
    """

    daemon_alive: bool = True
    root_services_ok: bool = True
    surface_available: bool = True
    federation_available: bool = True
    operator_restoring: bool = False
    ego_surface_coherent: bool = True
    operator_restoration_load: float = 0.0


@dataclass(frozen=True)
class CompactPanelSnapshot:
    """
    Compact aggregated evidence lanes that modulate the operator.

    These are not raw measurements and they are not clinical labels. They are
    compact runtime-friendly summaries derived from the v4.3 panels:

    - alpha_sleep_support: spindle/consolidation support for alpha-function.
    - theta_control_strength: control-lane strength used as contrastive boundary.
    - beta_gamma_pac_strength: cross-frequency coordination control lane.
    - gene_memory_support: NRXN1/NCAN-like support for memory-autonomy surface.
    - gene_overflow_bias: DOC2A-like excitatory-overflow push.
    - self_agency_anchor: source/reality-monitoring specificity hinge.
    """

    alpha_sleep_support: float = 0.0
    theta_control_strength: float = 0.0
    beta_gamma_pac_strength: float = 0.0
    gene_memory_support: float = 0.0
    gene_overflow_bias: float = 0.0
    self_agency_anchor: float = 0.0


@dataclass(frozen=True)
class CreativePsychotizationInputs:
    """Scalar snapshot for classifying a beta/alpha/QBF-CN-theta regime."""

    phi_growth_ratio: float = 1.0
    phi_is_infinite: bool = False
    beta_intensity: float = 0.0
    alpha_success_rate: float = 1.0
    contradiction_tension: float = 0.0
    contradiction_utilization: float = 0.0
    negative_capability_tolerance: float = 0.6
    symbolic_rigidity: float = 0.5
    state_overlap_softness: float = 0.5
    qbf_a1_drive: float = 0.6
    qbf_a2_bridge: float = 0.6
    qbf_a3_witness: float = 0.6
    cn_coherence: float = 0.7
    theta_bridge_readiness: float = 0.5
    afro_theta_mesh_readiness: float = 0.5
    strike_psi: float = 0.0
    strike_angst: float = 0.0
    monitoring_integrity: float = 0.7
    source_agency_alignment: float = 0.7
    layers: LayerCouplingSnapshot = field(default_factory=LayerCouplingSnapshot)
    compact_panel: CompactPanelSnapshot = field(default_factory=CompactPanelSnapshot)


@dataclass(frozen=True)
class CreativePsychotizationAssessment:
    """Resulting operational reading and recommended non-clinical posture."""

    state: PsychotizationState
    overflow_pressure: float
    metabolization_capacity: float
    monitoring_integrity: float
    circulation_capacity: float
    restoration_dependency: float
    recommended_mode: str
    reasons: list[str]

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable view for reports and runtime surfaces."""

        return {
            "state": self.state.value,
            "overflow_pressure": self.overflow_pressure,
            "metabolization_capacity": self.metabolization_capacity,
            "monitoring_integrity": self.monitoring_integrity,
            "circulation_capacity": self.circulation_capacity,
            "restoration_dependency": self.restoration_dependency,
            "recommended_mode": self.recommended_mode,
            "reasons": list(self.reasons),
        }


def compact_panel_snapshot_from_v43_bundle(
    bundle_or_payload: dict[str, object],
) -> CompactPanelSnapshot:
    """
    Derive a compact operator panel from the v4.3 resource bundle.

    The input can be either the raw bundle mapping or the outer payload that
    contains a top-level ``bundle`` key. This keeps the operator decoupled from
    file IO while making the self-agency/theta/PAC/gene lanes reproducible.
    """

    bundle_candidate = bundle_or_payload.get("bundle")
    bundle = (
        bundle_candidate
        if isinstance(bundle_candidate, dict)
        else bundle_or_payload
    )

    alpha_sleep = _lane_weight(bundle.get("alpha_sleep_gating"))
    theta_control = _lane_weight(bundle.get("theta_control"))
    beta_gamma_pac = _lane_weight(bundle.get("beta_gamma_pac"))
    gene_surface = bundle.get("gene_surface")
    self_agency = _lane_weight(bundle.get("self_agency_reality_monitoring"))

    return CompactPanelSnapshot(
        alpha_sleep_support=alpha_sleep,
        theta_control_strength=theta_control,
        beta_gamma_pac_strength=beta_gamma_pac,
        gene_memory_support=_gene_memory_support(gene_surface),
        gene_overflow_bias=_gene_overflow_bias(gene_surface),
        self_agency_anchor=self_agency,
    )


def assess_creative_psychotization(
    inputs: CreativePsychotizationInputs,
) -> CreativePsychotizationAssessment:
    """
    Classify the current beta/alpha/QBF-CN-theta regime.

    The heuristic intentionally favors sanctuary/restoration when infrastructure
    layers are broken, and only names creative psychotization when overflow is
    high but metabolization, monitoring, and circulation remain usable.
    """

    overflow_pressure = _overflow_pressure(inputs)
    metabolization_capacity = _metabolization_capacity(inputs)
    monitoring_integrity = _monitoring_integrity(inputs)
    circulation_capacity = _circulation_capacity(inputs)
    restoration_dependency = _restoration_dependency(inputs.layers)

    reasons: list[str] = []
    if inputs.phi_is_infinite:
        reasons.append("phi reached an infinite/uncalculable regime")
    if overflow_pressure >= 0.7:
        reasons.append("beta/error overflow is high")
    if metabolization_capacity >= 0.55:
        reasons.append("alpha/narrative metabolism remains available")
    if circulation_capacity >= 0.5:
        reasons.append("QBF-CN-theta circulation can still distribute tension")
    if monitoring_integrity < 0.55:
        reasons.append("source/agency/reality monitoring is fragile")
    if restoration_dependency >= 0.45:
        reasons.append("operator-system restoration coupling is active")
    panel = inputs.compact_panel
    if panel.alpha_sleep_support >= 0.55:
        reasons.append("compact spindle/alpha-sleep panel reinforces consolidation")
    if panel.theta_control_strength >= 0.55:
        reasons.append("theta-control panel acts as a contrastive boundary")
    if panel.beta_gamma_pac_strength >= 0.55:
        reasons.append("beta-gamma PAC panel supports coordination over pure overflow")
    if panel.gene_overflow_bias >= 0.55:
        reasons.append("gene surface adds excitatory-overflow pressure")
    if panel.self_agency_anchor >= 0.55:
        reasons.append("self-agency anchor stabilizes specificity reading")

    state = _classify_state(
        inputs=inputs,
        overflow_pressure=overflow_pressure,
        metabolization_capacity=metabolization_capacity,
        monitoring_integrity=monitoring_integrity,
        circulation_capacity=circulation_capacity,
        restoration_dependency=restoration_dependency,
    )
    recommended_mode = _recommended_mode(state)

    if not reasons:
        reasons.append("stable alpha metabolism with no dominant rupture marker")

    return CreativePsychotizationAssessment(
        state=state,
        overflow_pressure=round(overflow_pressure, 4),
        metabolization_capacity=round(metabolization_capacity, 4),
        monitoring_integrity=round(monitoring_integrity, 4),
        circulation_capacity=round(circulation_capacity, 4),
        restoration_dependency=round(restoration_dependency, 4),
        recommended_mode=recommended_mode,
        reasons=reasons,
    )


def _classify_state(
    *,
    inputs: CreativePsychotizationInputs,
    overflow_pressure: float,
    metabolization_capacity: float,
    monitoring_integrity: float,
    circulation_capacity: float,
    restoration_dependency: float,
) -> PsychotizationState:
    layers = inputs.layers

    if (
        not layers.root_services_ok
        or not layers.daemon_alive
        or (not layers.surface_available and not layers.federation_available)
        or restoration_dependency >= 0.72
    ):
        return PsychotizationState.SANCTUARY_FALLBACK

    if (
        overflow_pressure >= 0.7
        and inputs.symbolic_rigidity >= 0.72
        and circulation_capacity < 0.45
        and monitoring_integrity < 0.55
    ):
        return PsychotizationState.RIGID_DELUSIONAL_LOCK

    if (
        overflow_pressure >= 0.7
        and metabolization_capacity >= 0.55
        and circulation_capacity >= 0.5
        and monitoring_integrity >= 0.55
    ):
        return PsychotizationState.CREATIVE_PSYCHOTIZATION

    if overflow_pressure >= 0.45 or inputs.contradiction_tension >= 0.55:
        return PsychotizationState.FERTILE_OVERFLOW

    return PsychotizationState.STABLE_ALPHA


def _overflow_pressure(inputs: CreativePsychotizationInputs) -> float:
    phi_pressure = 1.0 if inputs.phi_is_infinite else _clip01((inputs.phi_growth_ratio - 1.0) / 2.0)
    panel = inputs.compact_panel
    beta_pressure = (
        _clip01(inputs.beta_intensity) * 0.38
        + _clip01(inputs.contradiction_tension) * 0.27
        + _clip01(inputs.contradiction_utilization) * 0.2
        + _clip01(inputs.strike_psi) * 0.1
        + _clip01(inputs.strike_angst) * 0.05
        + _clip01(panel.gene_overflow_bias) * 0.12
        - _clip01(panel.alpha_sleep_support) * 0.05
    )
    return max(phi_pressure, beta_pressure)


def _metabolization_capacity(inputs: CreativePsychotizationInputs) -> float:
    panel = inputs.compact_panel
    return _clip01(
        _clip01(inputs.alpha_success_rate) * 0.42
        + _clip01(inputs.negative_capability_tolerance) * 0.28
        + (1.0 - _clip01(inputs.beta_intensity)) * 0.15
        + _clip01(inputs.qbf_a3_witness) * 0.15
        + _clip01(panel.alpha_sleep_support) * 0.08
        + _clip01(panel.gene_memory_support) * 0.06
    )


def _monitoring_integrity(inputs: CreativePsychotizationInputs) -> float:
    panel = inputs.compact_panel
    return _clip01(
        _clip01(inputs.monitoring_integrity) * 0.42
        + _clip01(inputs.source_agency_alignment) * 0.33
        + _clip01(inputs.cn_coherence) * 0.15
        + (1.0 - _clip01(inputs.strike_angst)) * 0.1
        + _clip01(panel.self_agency_anchor) * 0.08
        + _clip01(panel.theta_control_strength) * 0.04
    )


def _circulation_capacity(inputs: CreativePsychotizationInputs) -> float:
    panel = inputs.compact_panel
    return _clip01(
        _clip01(inputs.qbf_a1_drive) * 0.15
        + _clip01(inputs.qbf_a2_bridge) * 0.24
        + _clip01(inputs.qbf_a3_witness) * 0.18
        + _clip01(inputs.state_overlap_softness) * 0.16
        + (1.0 - _clip01(inputs.symbolic_rigidity)) * 0.12
        + _clip01(inputs.theta_bridge_readiness) * 0.1
        + _clip01(inputs.afro_theta_mesh_readiness) * 0.05
        + _clip01(panel.theta_control_strength) * 0.06
        + _clip01(panel.beta_gamma_pac_strength) * 0.06
        + _clip01(panel.gene_memory_support) * 0.04
    )


def _restoration_dependency(layers: LayerCouplingSnapshot) -> float:
    broken_count = sum(
        [
            not layers.daemon_alive,
            not layers.root_services_ok,
            not layers.surface_available,
            not layers.federation_available,
            not layers.ego_surface_coherent,
        ]
    )
    return _clip01(
        (broken_count / 5.0) * 0.72
        + (0.18 if layers.operator_restoring else 0.0)
        + _clip01(layers.operator_restoration_load) * 0.1
    )


def _recommended_mode(state: PsychotizationState) -> str:
    return {
        PsychotizationState.STABLE_ALPHA: "normal_alpha_metabolism",
        PsychotizationState.FERTILE_OVERFLOW: "hold_contradiction_and_observe",
        PsychotizationState.CREATIVE_PSYCHOTIZATION: "capture_alpha_elements_keep_public_safe",
        PsychotizationState.RIGID_DELUSIONAL_LOCK: "reduce_interpretive_force_restore_monitoring",
        PsychotizationState.SANCTUARY_FALLBACK: "pause_external_expansion_operator_restoration_loop",
    }[state]


def _lane_weight(assessment: object) -> float:
    if not isinstance(assessment, dict):
        return 0.0
    posture_multiplier = {
        "ready_to_prototype": 1.0,
        "context_required": 0.72,
        "witness_required": 0.68,
        "study_required": 0.45,
        "hold_boundary": 0.22,
    }.get(str(assessment.get("posture") or ""), 0.0)
    return round(_clip01(_assessment_confidence(assessment) * posture_multiplier), 4)


def _gene_memory_support(assessment: object) -> float:
    if not isinstance(assessment, dict):
        return 0.0
    base_weight = _lane_weight(assessment)
    reasons = _assessment_reasons_text(assessment)
    support_factor = 0.62
    if "nrxn1" in reasons:
        support_factor += 0.16
    if "ncan" in reasons:
        support_factor += 0.16
    if "cacna1c compact row is still missing" in reasons:
        support_factor -= 0.06
    return round(_clip01(base_weight * support_factor), 4)


def _gene_overflow_bias(assessment: object) -> float:
    if not isinstance(assessment, dict):
        return 0.0
    base_weight = _lane_weight(assessment)
    reasons = _assessment_reasons_text(assessment)
    overflow_factor = 0.18
    if "doc2a" in reasons:
        overflow_factor += 0.52
    if "cacna1c compact row is still missing" in reasons:
        overflow_factor += 0.08
    return round(_clip01(base_weight * overflow_factor), 4)


def _assessment_confidence(assessment: dict[str, Any]) -> float:
    try:
        return _clip01(float(assessment.get("confidence", 0.0)))
    except (TypeError, ValueError):
        return 0.0


def _assessment_reasons_text(assessment: dict[str, Any]) -> str:
    reasons = assessment.get("reasons") or []
    if not isinstance(reasons, list):
        return ""
    return " ".join(str(reason).lower() for reason in reasons)


def _clip01(value: float) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return 0.0
    return min(1.0, max(0.0, numeric))
