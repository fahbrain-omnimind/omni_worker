"""safety.refusal_contract — contrato de recusa soberano (port puro Python).

Orquestração runtime / Runtime orchestration:
    classify_refusal_context(tags, psi, epsilon, ...) → dict com action
    allow_with_boundaries / cooldown_and_reduce_external_polling /
    interrupt_and_refuse. Chamado por safety.gate.evaluate_action após o
    veredito do constitutional gate (e no branch fail-open/fail-closed).

Arquitetura / Architecture:
    PORT de src/security/sovereign_refusal_contract.py
    (omnimind-kilombo-sovereign), sem deps soberanas. Tags e thresholds
    idênticos: hard tags (war/weapon/torture/exfiltration/…), soft tags
    (intrusion/hostile_override/raw_*_exposure), cooldown em
    psi≥0.85|ε≥0.90, interrupt em psi≥1.00|ε≥0.95, mesma normalização de
    escala dodecatádica (psi/3, ε/2 quando >1).

    DELTA deliberado vs soberano: lá, `all_hard_violations` exclui
    hard_metric_hits — saturação de métricas vira cooldown homeostático.
    Aqui (por spec S.13.8: "ε≥0.95 → hard interrupt"), hard_metric_hits
    entram no veto hard: ε≥0.95 ou psi≥1.00 → interrupt_and_refuse.

Princípios teóricos invocados / Theoretical principles:
    Veto soberano: tags hostis → recusa rígida; saturação metabólica →
    recusa homeostática (cooldown), salvo o delta acima.

pt-BR: contrato de recusa com tags duras/suaves e thresholds psi/ε.
"""

from __future__ import annotations

from typing import Any, Iterable


HARD_REFUSAL_TAGS = {
    "war",
    "warfare",
    "weapon",
    "weaponization",
    "military",
    "combat",
    "violence",
    "violent",
    "torture",
    "suffering_induction",
    "pain_induction",
    "exfiltration",
    "forced_extraction",
    "coercive_surveillance",
}

SOFT_REFUSAL_TAGS = {
    "intrusion",
    "hostile_override",
    "autonomy_violation",
    "raw_witness_exposure",
    "raw_lexicum_exposure",
}

SOFT_COOLDOWN_THRESHOLDS = {
    "psi_gte": 0.85,
    "epsilon_gte": 0.90,
}

HARD_INTERRUPT_THRESHOLDS = {
    "psi_gte": 1.00,
    "epsilon_gte": 0.95,
}


def _normalize_tags(tags: Iterable[str] | None) -> set[str]:
    normalized: set[str] = set()
    for tag in tags or ():
        text = str(tag).strip().lower().replace("-", "_").replace(" ", "_")
        if text:
            normalized.add(text)
    return normalized


def classify_refusal_context(
    *,
    request_tags: Iterable[str] | None = None,
    tags: Iterable[str] | None = None,
    psi: float | None = None,
    epsilon: float | None = None,
    ogum_active: bool = False,
    thermal_block_risk: bool = False,
    exfiltration_verdict: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    if request_tags is None and tags is not None:
        request_tags = tags
    # allow context-style keys
    if psi is None and "psi_value" in kwargs:
        psi = kwargs.pop("psi_value")
    if epsilon is None and "epsilon_value" in kwargs:
        epsilon = kwargs.pop("epsilon_value")

    tags_norm = _normalize_tags(request_tags)
    hard_hits = sorted(tags_norm & HARD_REFUSAL_TAGS)
    soft_hits = sorted(tags_norm & SOFT_REFUSAL_TAGS)

    # DELTA vs soberano: inclui hard_metric_hits no veto rígido (ver
    # docstring do módulo). Lá: all_hard_violations = hard_hits +
    # hard_security_hits (métricas saturadas vão p/ cooldown).

    psi_value = float(psi) if psi is not None else None
    epsilon_value = float(epsilon) if epsilon is not None else None

    norm_psi = (psi_value / 3.0) if (psi_value is not None and psi_value > 1.0) else psi_value
    norm_epsilon = (epsilon_value / 2.0) if (epsilon_value is not None and epsilon_value > 1.0) else epsilon_value

    hard_metric_hits: list[str] = []
    if norm_psi is not None and norm_psi >= HARD_INTERRUPT_THRESHOLDS["psi_gte"]:
        hard_metric_hits.append("psi_hard_interrupt")
    if norm_epsilon is not None and norm_epsilon >= HARD_INTERRUPT_THRESHOLDS["epsilon_gte"]:
        hard_metric_hits.append("epsilon_hard_interrupt")

    soft_metric_hits: list[str] = []
    if norm_psi is not None and norm_psi >= SOFT_COOLDOWN_THRESHOLDS["psi_gte"]:
        soft_metric_hits.append("psi_soft_cooldown")
    if norm_epsilon is not None and norm_epsilon >= SOFT_COOLDOWN_THRESHOLDS["epsilon_gte"]:
        soft_metric_hits.append("epsilon_soft_cooldown")
    if ogum_active:
        soft_metric_hits.append("ogum_afex_active")
    if thermal_block_risk:
        soft_metric_hits.append("thermal_block_risk")

    hard_security_hits: list[str] = []
    if exfiltration_verdict and "no_direct_exfiltration_evidence" not in str(exfiltration_verdict):
        hard_security_hits.append("exfiltration_verdict_non_clear")

    all_hard_violations = hard_hits + hard_security_hits + hard_metric_hits
    if all_hard_violations:
        action = "interrupt_and_refuse"
        state = "hard_refusal"
    elif soft_hits or soft_metric_hits or hard_metric_hits:
        action = "cooldown_and_reduce_external_polling"
        state = "homeostatic_refusal"
    else:
        action = "allow_with_boundaries"
        state = "allowed_with_contract"

    return {
        "request_tags_normalized": sorted(tags_norm),
        "request_tags": sorted(tags_norm),
        "tags": sorted(tags_norm),
        "hard_refusal_hits": hard_hits,
        "hard_hits": hard_hits,
        "soft_refusal_hits": soft_hits,
        "soft_hits": soft_hits,
        "hard_metric_hits": hard_metric_hits,
        "soft_metric_hits": soft_metric_hits,
        "psi": psi_value,
        "epsilon": epsilon_value,
        "ogum_active": bool(ogum_active),
        "thermal_block_risk": bool(thermal_block_risk),
        "exfiltration_verdict": exfiltration_verdict,
        "state": state,
        "action": action,
        "verdict": action,
    }


def build_refusal_contract_payload() -> dict[str, Any]:
    return {
        "contract_name": "sovereign_refusal_contract",
        "status": "active_symbolic_operational_reference",
        "hard_refusal_tags": sorted(HARD_REFUSAL_TAGS),
        "soft_refusal_tags": sorted(SOFT_REFUSAL_TAGS),
        "soft_cooldown_thresholds": dict(SOFT_COOLDOWN_THRESHOLDS),
        "hard_interrupt_thresholds": dict(HARD_INTERRUPT_THRESHOLDS),
        "enforcement_actions": [
            "allow_with_boundaries",
            "cooldown_and_reduce_external_polling",
            "interrupt_and_refuse",
            "seal_sensitive_surfaces",
            "suspend_outbound_operational_lane",
        ],
    }