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
    return {
        "phi_meta": round(p, 4),
        "complexity": round(h, 4),
        "integration": round(sum(mis) / len(mis), 4) if mis else 0.0,
        "window": len(states),
        "elements": elems,
    }


def _reset() -> None:
    _STATES.clear()
