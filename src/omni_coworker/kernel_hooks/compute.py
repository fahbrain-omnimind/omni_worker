"""Kernel compute wrapper with Python fallback.

English: Uses compiled Rust kernel modules when available, else pure Python.
pt-BR: Usa módulos de kernel Rust compilados quando disponíveis, senão Python puro.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Sequence

from . import (
    FREUD_AVAILABLE,
    KERNEL_AVAILABLE,
    METRICS_AVAILABLE,
    omnimind_freud10d,
    omnimind_kernel_compute,
    omnimind_metrics,
)


def affect_state(host_state: Dict[str, Any] | None = None) -> Dict[str, Any] | None:
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
    except Exception:
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
        except Exception:
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
        except Exception:
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
        except Exception:
            pass
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def kernel_status() -> Dict[str, bool]:
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


def freud10d_cycle(perception: Sequence[float] | None = None) -> Dict[str, Any] | None:
    """One Freud10D forward pass on a persistent apparatus.

    English: Singleton apparatus across calls — tension/pleasure history
    accumulates per cycle (the Vacilo basal detector signal). Returns
    consciousness scalar, freudian soul axes, INRC recommendation and
    the last tension/pleasure windows; None when the crate is absent.
    pt-BR: Aparato singleton entre chamadas — histórico de
    tensão/prazer acumula por ciclo (sinal do detector basal do
    Vacilo). Retorna escalar de consciência, eixos freudianos do soul,
    recomendação INRC e janelas de tensão/prazer; None sem o crate.
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
        tension = float(sum(abs(float(v)) for v in state_vec))
        pleasure = None
        tw = list(_FREUD_APPARATUS.tension_window(32))
        if len(tw) >= 2:
            pleasure = float(-(tw[-1] - tw[-2]))
        return {
            "consciousness": float(consciousness),
            "state": values,
            "state_vec": [float(v) for v in state_vec],
            "inrc": {"op": op, "reason": reason},
            "tension": tension,
            "pleasure": pleasure,
            "tension_window": tw,
        }
    except Exception:
        return None
