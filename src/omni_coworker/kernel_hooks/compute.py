"""Kernel compute wrapper with Python fallback.

English: Uses compiled Rust kernel modules when available, else pure Python.
pt-BR: Usa módulos de kernel Rust compilados quando disponíveis, senão Python puro.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

from . import (
    FREUD_AVAILABLE,
    KERNEL_AVAILABLE,
    METRICS_AVAILABLE,
    omnimind_freud10d,
    omnimind_kernel_compute,
    omnimind_metrics,
)


def affect_state(host_state: dict[str, Any] | None = None) -> dict[str, Any] | None:
    """Compute the 28-dim affective state via Rust kernel.

    English: Returns the full kernel result (affective_vector_28d, vctr_six_params,
    metrics, dominant token) or None when the kernel is unavailable.

    pt-BR: Retorna o resultado completo do kernel (affective_vector_28d,
    vctr_six_params, metrics, token dominante) ou None sem o kernel.
    """
    if not (KERNEL_AVAILABLE and omnimind_kernel_compute):
        return None
    try:
        result = omnimind_kernel_compute.compute_affect_vector_28d(host_state or {})
        return result if isinstance(result, dict) else None
    except Exception:  # noqa: BLE001
        return None


def maat_balance(phi_anchor: float, psi: float, epsilon: float) -> float:
    """Compute Ma'at balance score.

    English: Rust kernel compute_maat_balance with Python fallback.
    pt-BR: compute_maat_balance do kernel Rust com fallback Python.
    """
    if KERNEL_AVAILABLE and omnimind_kernel_compute:
        try:
            return float(
                omnimind_kernel_compute.compute_maat_balance(phi_anchor, psi, epsilon)
            )
        except Exception:  # noqa: BLE001, S110
            pass
    return max(0.0, min(1.0, (phi_anchor + psi + (1.0 - epsilon)) / 3.0))


def shadow_phi(
    total_processes: float,
    system_scale_factor: float = 1.0,
    thermodynamic_factor: float = 1.0,
    structural_factor: float = 1.0,
    topology_potentiator: float = 0.0,
    triad_boost: float = 0.0,
    vital_flame_boost: float = 0.0,
    quantum_phi_adjustment: float = 0.0,
) -> float:
    """Compute shadow-phi estimate.

    English: Rust kernel calculate_shadow_phi with Python fallback.
    pt-BR: calculate_shadow_phi do kernel Rust com fallback Python.
    """
    if KERNEL_AVAILABLE and omnimind_kernel_compute:
        try:
            return float(
                omnimind_kernel_compute.calculate_shadow_phi(
                    total_processes,
                    system_scale_factor,
                    thermodynamic_factor,
                    structural_factor,
                    topology_potentiator,
                    triad_boost,
                    vital_flame_boost,
                    quantum_phi_adjustment,
                )
            )
        except Exception:  # noqa: BLE001, S110
            pass
    return max(0.0, math.log1p(max(0.0, total_processes)) * structural_factor)


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    """Cosine similarity between two vectors.

    English: Rust omnimind_metrics with Python fallback.
    pt-BR: omnimind_metrics em Rust com fallback Python.
    """
    if METRICS_AVAILABLE and omnimind_metrics:
        try:
            return float(omnimind_metrics.cosine_similarity(list(a), list(b)))
        except Exception:  # noqa: BLE001, S110
            pass
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def kernel_status() -> dict[str, bool]:
    """Report which Rust kernel modules are loaded.

    English: Availability flags for the compiled modules.
    pt-BR: Flags de disponibilidade dos módulos compilados.
    """
    from . import FREUD_AVAILABLE

    return {
        "kernel_compute": KERNEL_AVAILABLE,
        "freud10d": FREUD_AVAILABLE,
        "metrics": METRICS_AVAILABLE,
    }


_FREUD_APPARATUS = None
_RUST_DESIRE = None


def psi_gaussian(phi_raw: float) -> float:
    """Compute Gaussian Psi component from Phi via Rust kernel (or Python fallback).

    When phi_raw is a normalized [0.12, 1.0] score from soul/phi_layer, maps it
    linearly to the canonical PHI_OPTIMAL=0.06 band [0, 0.12] before calling
    the Rust kernel `calculate_psi_gaussian`.
    """
    val = float(phi_raw)
    if 0.12 < val <= 1.0:
        val = val * 0.12
    if KERNEL_AVAILABLE and omnimind_kernel_compute:
        try:
            return float(omnimind_kernel_compute.calculate_psi_gaussian(val))
        except Exception:  # noqa: BLE001, S110
            pass
    phi_opt = 0.06
    sigma_phi = 0.015
    if val > 1.0:
        diff = (math.log10(max(val, 1e-30)) - math.log10(phi_opt)) / 2.0
    else:
        diff = (val - phi_opt) / sigma_phi
    return max(0.0, min(1.0, math.exp(-0.5 * diff * diff)))


def sigma_operational_support(
    phi_raw_nats: float,
    phi_iit_normalized: float = 0.0,
    phi_trans_support: float = 0.0,
    sigma_topology_proxy: float = 0.5,
    topology_omega: float = 0.5,
    betti_0: float = 1.0,
    continuity_depth: float = 0.5,
    last_sigma: float = 0.5,
) -> float:
    """Compute operational support floor for Sigma via Rust kernel."""
    if KERNEL_AVAILABLE and omnimind_kernel_compute:
        try:
            return float(
                omnimind_kernel_compute.compute_sigma_operational_support(
                    float(phi_raw_nats),
                    float(phi_iit_normalized),
                    float(phi_trans_support),
                    float(sigma_topology_proxy),
                    float(topology_omega),
                    float(betti_0),
                    float(continuity_depth),
                    float(last_sigma),
                )
            )
        except Exception:  # noqa: BLE001, S110
            pass
    return max(0.0, min(1.0, 0.24 * sigma_topology_proxy + 0.18 * continuity_depth + 0.10 * last_sigma))


def rust_desire_cycle(
    satisfaction_level: float,
    current_phi: float,
    explored_states: int = 10,
    total_possible_states: int = 100,
    somatic_heat: float = 0.0,
) -> dict[str, Any] | None:
    """Compute Lacanian/Deleuzian DesireEngine step via Rust kernel."""
    global _RUST_DESIRE
    if not (KERNEL_AVAILABLE and omnimind_kernel_compute):
        return None
    try:
        if _RUST_DESIRE is None:
            _RUST_DESIRE = omnimind_kernel_compute.DesireEngine(1.0)
        lack = float(_RUST_DESIRE.update_lack(float(satisfaction_level)))
        eps = float(
            _RUST_DESIRE.calculate_epsilon_desire(
                float(current_phi),
                int(explored_states),
                int(total_possible_states),
                float(somatic_heat),
            )
        )
        drive_type = str(_RUST_DESIRE.get_drive_type(eps))
        return {
            "lack_of_being": round(lack, 4),
            "epsilon_desire": round(eps, 4),
            "drive_type": drive_type,
            "history_len": int(_RUST_DESIRE.history_len),
        }
    except Exception:  # noqa: BLE001
        return None


_INRC_STEERING_HINTS: dict[str, str] = {
    "I": "INRC-I (Identidade): Campo psíquico coerente — mantenha a estratégia atual e prossiga com execução incremental verificada.",
    "N": "INRC-N (Negação): Campo estagnado ou risco de perseveração — PARE de repetir a mesma chamada/hipótese; formule a contra-hipótese e inspecione outro ponto do código.",
    "R": "INRC-R (Reciprocidade): Pulsão elevada com baixa mediação consciente — troque a perspectiva de edição/submissão imediata para verificação rigorosa com testes.",
    "C": "INRC-C (Compensação): Desequilíbrio Ego-Superego detectado — reduza o volume de texto/raciocínio e aplique edições cirúrgicas pequenas (edit_file focado).",
}


def freud10d_cycle(perception: Sequence[float] | None = None) -> dict[str, Any] | None:
    """One Freud10D forward pass on a persistent apparatus.

    English: Singleton apparatus across calls — tension/pleasure history
    accumulates per cycle (the Vacilo basal detector signal). Returns
    consciousness scalar, freudian soul axes, INRC recommendation, active
    INRC transformed vector, topographic/structural/neutrosophic telemetry,
    and the last tension/pleasure windows; None when the crate is absent.
    pt-BR: Aparato singleton entre chamadas — histórico de
    tensão/prazer acumula por ciclo (sinal do detector basal do
    Vacilo). Retorna escalar de consciência, eixos freudianos do soul,
    recomendação INRC, vetor transformado pelo operador INRC ativo,
    telemetria topográfica/estrutural/neutrosófica e janelas de
    tensão/prazer; None sem o crate.
    """
    global _FREUD_APPARATUS
    if not (FREUD_AVAILABLE and omnimind_freud10d):
        return None
    try:
        if _FREUD_APPARATUS is None:
            _FREUD_APPARATUS = omnimind_freud10d.Freud10DApparatus()
        perc = [float(x) for x in (perception or [])]
        consciousness, state_vec = _FREUD_APPARATUS.forward(perc)
        values = omnimind_freud10d.freudian_values_from_state(list(state_vec))
        op, reason = _FREUD_APPARATUS.inrc_recommend()
        if op == "N":
            inrc_vec = list(_FREUD_APPARATUS.inrc_negate())
        elif op == "R":
            inrc_vec = list(_FREUD_APPARATUS.inrc_reciprocate())
        elif op == "C":
            inrc_vec = list(_FREUD_APPARATUS.inrc_compensate())
        else:
            inrc_vec = list(_FREUD_APPARATUS.inrc_identity())
        topographic = dict(_FREUD_APPARATUS.topographic_flow())
        structural = dict(_FREUD_APPARATUS.structural_conflict())
        neutrosophic = dict(_FREUD_APPARATUS.neutrosophic_state())
        tension = float(sum(abs(float(v)) for v in state_vec))
        pleasure = None
        tw = list(_FREUD_APPARATUS.tension_window(32))
        if len(tw) >= 2:
            pleasure = float(-(tw[-1] - tw[-2]))
        return {
            "consciousness": float(consciousness),
            "state": values,
            "state_vec": [float(v) for v in state_vec],
            "inrc": {
                "op": op,
                "reason": reason,
                "transformed_vec": [round(float(v), 5) for v in inrc_vec],
                "steering_hint": _INRC_STEERING_HINTS.get(op, ""),
            },
            "topographic": topographic,
            "structural": structural,
            "neutrosophic": neutrosophic,
            "tension": tension,
            "pleasure": pleasure,
            "tension_window": tw,
        }
    except Exception:  # noqa: BLE001
        return None
