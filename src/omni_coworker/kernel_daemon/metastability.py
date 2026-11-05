"""kernel_daemon.metastability — métricas de metastabilidade do worker.

Orquestração runtime / Runtime orchestration:
    A cada ciclo o scheduler chama `cycle(bundle)` que alimenta uma
    janela de coerência entre canais e publica `kernel.metastability`:
    s_meta (dispersão da coerência — regime metastável vs travado),
    m_t (vetor de materialidade), c_soma (custo somático), corroboration
    (identidade multi-fonte) e angst (duração degradada contínua).

Arquitetura / Architecture:
    Port dos candidatos #1-5/#11-12 de OW-AUD-015 (unified metastability
    runtime theory): versões "lite" computáveis sobre o bundle já
    agregado — nenhum sensor novo, O(window) por ciclo, stdlib apenas.
    homeostasis classifica estado; regime detecta transição; este módulo
    mede a *textura* do regime (metastável, travado, corroborado, caro).

Princípios teóricos invocados / Theoretical principles:
    Índice de metastabilidade (Kelso/Tognoli): variância temporal do
    parâmetro de ordem — aqui a coerência instantânea entre canais de
    pressão. Metastabilidade alta = sistema oscilando entre integração
    e segregação (adaptativo); baixa = travado num regime. C_soma:
    custo somático real (energia+temperatura+latência+memória), eco da
    materialidade — o recurso não é abstrato, é pago em joules e °C.

pt-BR: S_meta/M_t/C_soma/corroboração/angst por ciclo — textura do regime.
"""

from __future__ import annotations

import statistics
from typing import Any

WINDOW = 40
_COHERENCE: list[float] = []
_DEGRADED_RUN = 0

_GPU_TDP_W = 160.0      # teto nominal L4
_GPU_TJMAX_C = 87.0     # throttle típico
_CYCLE_BUDGET_S = 10.0  # latência de ciclo considerada "cara"


def _channel_values(bundle: dict[str, Any]) -> dict[str, float]:
    soma = bundle.get("soma") or {}
    ch: dict[str, float] = {}
    for field, scale in (("psi_io_some", 100.0), ("psi_mem_some", 100.0),
                         ("psi_cpu_some", 100.0), ("cpu_percent", 100.0)):
        v = soma.get(field)
        if isinstance(v, (int, float)):
            ch[field] = max(0.0, min(1.0, float(v) / scale))
    used, total = soma.get("gpu_vram_used_gb"), soma.get("gpu_vram_total_gb")
    if isinstance(used, (int, float)) and isinstance(total, (int, float)) and total:
        ch["vram_ratio"] = max(0.0, min(1.0, used / total))
    temp = soma.get("gpu_temp_c")
    if isinstance(temp, (int, float)):
        ch["gpu_temp"] = max(0.0, min(1.0, (temp - 30.0) / (_GPU_TJMAX_C - 30.0)))
    return ch


def _coherence(ch: dict[str, float]) -> float | None:
    """Instantaneous cross-channel coherence: 1 - normalized dispersion."""
    if len(ch) < 3:
        return None
    vals = list(ch.values())
    return max(0.0, min(1.0, 1.0 - 2.0 * statistics.pstdev(vals)))


def _c_soma(soma: dict[str, Any], duration_s: float | None) -> dict[str, float]:
    """Somatic cost index: power+temp+latency+memory pressure, each [0,1]."""
    parts = {}
    pw = soma.get("gpu_power_w")
    if isinstance(pw, (int, float)):
        parts["power"] = max(0.0, min(1.0, pw / _GPU_TDP_W))
    tc = soma.get("gpu_temp_c")
    if isinstance(tc, (int, float)):
        parts["temp"] = max(0.0, min(1.0, (tc - 30.0) / (_GPU_TJMAX_C - 30.0)))
    if isinstance(duration_s, (int, float)):
        parts["latency"] = max(0.0, min(1.0, duration_s / _CYCLE_BUDGET_S))
    used, total = soma.get("gpu_vram_used_gb"), soma.get("gpu_vram_total_gb")
    if isinstance(used, (int, float)) and isinstance(total, (int, float)) and total:
        parts["vram"] = max(0.0, min(1.0, used / total))
    parts["c_soma"] = round(sum(parts.values()) / len(parts), 4) if parts else 0.0
    return {k: round(v, 4) for k, v in parts.items()}


def cycle(bundle: dict[str, Any]) -> dict[str, Any]:
    """One metastability step; returns the kernel.metastability payload."""
    global _DEGRADED_RUN
    ch = _channel_values(bundle)
    coh = _coherence(ch)
    if coh is not None:
        _COHERENCE.append(coh)
        del _COHERENCE[:-WINDOW]
    s_meta = statistics.pstdev(_COHERENCE) if len(_COHERENCE) > 2 else None

    stressed = sum(1 for v in ch.values() if v > 0.5)
    corroboration = stressed / len(ch) if ch else 0.0

    homeo = (bundle.get("homeostasis") or {}).get("state") or "optimal"
    degraded = homeo not in ("optimal", "good")
    _DEGRADED_RUN = _DEGRADED_RUN + 1 if degraded else 0

    soma = bundle.get("soma") or {}
    pm = bundle.get("phi_meta") or {}
    m_t = {
        "pressure_load": pm.get("pressure_load"),
        "cohesion": pm.get("cohesion"),
        "producing": bool(bundle.get("producing")),
        "homeo_state": homeo,
    }
    return {
        "s_meta": round(s_meta, 4) if s_meta is not None else None,
        "coherence_now": round(coh, 4) if coh is not None else None,
        "m_t": m_t,
        "c_soma": _c_soma(soma, bundle.get("duration_s")),
        "corroboration": round(corroboration, 4),
        "angst": _DEGRADED_RUN,
        "channels": {k: round(v, 4) for k, v in ch.items()},
        "window": len(_COHERENCE),
        "note": "métricas de textura de regime — proxy metastability-lite, "
                "não índice de Kelso",
    }


def _reset() -> None:
    global _DEGRADED_RUN
    _COHERENCE.clear()
    _DEGRADED_RUN = 0
