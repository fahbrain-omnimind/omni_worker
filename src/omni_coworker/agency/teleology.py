"""Teleology (mission cycles).

English: Endogenous mission generation; reuses omega_teleology concept.
pt-BR: Geração endógena de missões; reutiliza conceito omega_teleology.
"""

from __future__ import annotations

from typing import Any

_LAST_OMEGA: float | None = None


def generate_missions(context: dict | None = None) -> list[dict[str, Any]]:
    """Generate mission list.
    
    English: Returns structured missions (short/medium/long term).
    pt-BR: Retorna missões estruturadas (curto/médio/longo prazo).
    """
    context = context or {}
    missions = []
    
    # Short-term: immediate needs
    if context.get("cpu_high"):
        missions.append({
            "id": "m_short_01",
            "term": "short",
            "priority": "high",
            "description": "Stabilize resource usage",
            "descricao": "Estabilizar uso de recursos",
            "type": "maintenance"
        })
    
    # Medium-term: structure improvement
    missions.append({
        "id": "m_med_01",
        "term": "medium",
        "priority": "medium",
        "description": "Consolidate modular architecture",
        "descricao": "Consolidar arquitetura modular",
        "type": "evolution"
    })
    
    # Long-term: teleological goal
    missions.append({
        "id": "m_long_01",
        "term": "long",
        "priority": "low",
        "description": "Pursue coherent self-organization",
        "descricao": "Buscar auto-organização coerente",
        "type": "teleology"
    })
    
    return missions


def compute_omega_teleology(state: dict | None = None) -> float:
    """Compute omega teleology metric.
    
    English: Computes endogenous teleological coherence from state.
    pt-BR: Computa coerência teleológica endógena a partir do estado.
    """
    import numpy as np

    state = state or {}
    # Directionality indicators from missions/goals
    missions = state.get("missions") or []
    goals = state.get("goals") or []
    coherence = 0.5
    coherence += min(0.3, len(missions) * 0.1)
    coherence += min(0.2, len(goals) * 0.05)

    # Temporal persistence term: delta between calls (module-level)
    global _LAST_OMEGA
    if _LAST_OMEGA is not None:
        persistence = 1.0 - abs(float(_LAST_OMEGA) - float(coherence))
        coherence = 0.7 * coherence + 0.3 * persistence
    _LAST_OMEGA = float(coherence)

    return round(float(np.clip(coherence, 0.0, 1.0)), 4)
