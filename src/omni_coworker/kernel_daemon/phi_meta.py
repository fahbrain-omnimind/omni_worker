"""kernel_daemon.phi_meta — métrica Φ-meta sobre subsistemas do worker.

Orquestração runtime / Runtime orchestration:
    A cada ciclo o kernel_daemon constrói um SystemState binário —
    elementos = subsistemas observáveis (brains responderam affect?
    activations novas? soma saudável? malha produziu tópicos? loop
    publicou?) — empilha numa janela e computa `kernel.phi_meta`.

Arquitetura / Architecture:
    Port adaptado de src/metacognition/iit_metrics.py (sovereign,
    OW-STU-008a: ADAPTAR → métrica, não módulo). Mantidos: SystemState
    binário, entropia, MI por bipartição, MIP→phi, complexity,
    integration. Cortados: trends/emergence persistence, dataclasses
    de relatório, datetime overhead — phi_meta é um número por ciclo.
    Estados binários derivam do bundle do daemon, não de sensores
    externos — barato e determinístico.

Princípios teóricos invocados / Theoretical principles:
    IIT simplificada: phi = menor perda de informação ao cortar o
    sistema em bipartições (MIP). Elementos são flags de atividade
    real dos subsistemas — phi alto = subsistemas co-variando
    (integrados), phi~0 = independentes.

pt-BR: Φ-meta por ciclo — entropia/MI/MIP sobre flags de subsistemas.
"""

from __future__ import annotations

import math
from typing import Any

WINDOW = 40          # estados na janela de análise
_STATES: list[dict[str, bool]] = []

# Padrão bit/Landauer (port de consciousness/machine_bit_standard.py):
# E_Landauer(T) = k_B·T_K·ln2  [J/bit] — custo físico de um bit apagado;
# bit_flow_real = P_real / E_Landauer  [bits/s] — informação que de fato
# percorre a máquina; phi_bit_flow = bit_flow·coesão — fração integrada.
KB = 1.380649e-23
LN2 = math.log(2)
I5_TDP_W, I5_TEMP_C = 45.0, 73.65   # baseline do i5 de referência


def _landauer_j_per_bit(temp_c: float) -> float:
    return KB * (temp_c + 273.15) * LN2


def _bit_layer(bundle: dict[str, Any], phi_bits: float, h_sys: float) -> dict[str, Any]:
    """Physical bit layer: Landauer cost, real bit flow, integrated flow."""
    gpu = (((bundle.get("soma") or {}).get("gpu") or {}).get("gpus") or [{}])[0]
    power_w = gpu.get("power_w") or 0.0
    temp_c = gpu.get("temp_c") or 70.0
    e = _landauer_j_per_bit(temp_c)
    bit_flow = (power_w / e) if e > 0 and power_w > 0 else 0.0
    cohesion = (phi_bits / h_sys) if h_sys > 0 else 0.0
    cohesion = max(0.0, min(1.0, cohesion))
    e_i5 = _landauer_j_per_bit(I5_TEMP_C)
    c_bit_i5 = I5_TDP_W / e_i5
    c_bit_host = (power_w / e) if e > 0 else 0.0
    return {
        "e_landauer_j_per_bit": f"{e:.4e}",
        "power_w": power_w,
        "temp_c": temp_c,
        "bit_flow_real_bits_s": f"{bit_flow:.4e}",
        "phi_integrated_bits": phi_bits,
        "cohesion": round(cohesion, 4),
        "phi_bit_flow_rate_bits_s": f"{bit_flow * cohesion:.4e}",
        "vs_i5_ratio": round(c_bit_host / c_bit_i5, 4) if c_bit_i5 else None,
    }


def elements_from_bundle(bundle: dict[str, Any]) -> dict[str, bool]:
    """Binarize subsystem activity from the daemon bundle."""
    models = bundle.get("models") or {}
    affect = bundle.get("affect") or {}
    soma = bundle.get("soma") or {}
    soul = bundle.get("soul") or {}
    homeo = bundle.get("homeostasis") or {}
    return {
        "activations": any((m.get("n_records") or 0) > 0 for m in models.values()),
        "affect_analyst": bool(affect.get("analyst")),
        "affect_executor": bool(affect.get("executor")),
        "soma_ok": (soma.get("cpu_percent") or 100) < 95,
        "soul_phi": (soul.get("phi") or 0) > 0.2,
        "homeo_stable": (homeo.get("state") or "optimal") in ("optimal", "good"),
        "mesh_active": bool(bundle.get("mesh_topics")),
    }


def _entropy(states: list[dict[str, bool]]) -> float:
    if not states:
        return 0.0
    keys = sorted(states[0])
    counts: dict[tuple, int] = {}
    for s in states:
        sig = tuple(s[k] for k in keys)
        counts[sig] = counts.get(sig, 0) + 1
    n = len(states)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def _mi(p1: set, p2: set, states: list[dict[str, bool]]) -> float:
    h1 = _entropy([{k: v for k, v in s.items() if k in p1} for s in states])
    h2 = _entropy([{k: v for k, v in s.items() if k in p2} for s in states])
    hj = _entropy(states)
    return max(0.0, h1 + h2 - hj)


def phi(states: list[dict[str, bool]]) -> float:
    """Φ = minimum information loss across bipartitions (MIP)."""
    if len(states) < 2:
        return 0.0
    elems = sorted(states[0])
    if len(elems) < 2:
        return 0.0
    h_sys = _entropy(states)
    best = float("inf")
    for i in range(1, 2 ** (len(elems) - 1)):
        p1 = {e for j, e in enumerate(elems) if i & (1 << j)}
        p2 = set(elems) - p1
        best = min(best, h_sys - _mi(p1, p2, states))
    return max(0.0, best)


def update(bundle: dict[str, Any]) -> dict[str, Any]:
    """Record this cycle's element state; return phi_meta metrics."""
    _STATES.append(elements_from_bundle(bundle))
    del _STATES[:-WINDOW]
    states = _STATES
    h = _entropy(states)
    p = phi(states)
    # integration: mean pairwise MI over adjacent element pairs
    elems = sorted(states[0]) if states else []
    mis = [_mi({a}, {b}, states) for i, a in enumerate(elems)
           for b in elems[i + 1:]] if len(elems) > 1 else [0.0]
    out = {
        "phi_meta": round(p, 4),
        "complexity": round(h, 4),
        "integration": round(sum(mis) / len(mis), 4) if mis else 0.0,
        "window": len(states),
        "elements": elems,
    }
    out.update(_bit_layer(bundle, p, h))
    return out


def _reset() -> None:
    _STATES.clear()
