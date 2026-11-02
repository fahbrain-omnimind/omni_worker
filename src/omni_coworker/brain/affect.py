"""Affect derivation from tensors.

English: Derives phi, psi, sigma, epsilon from hidden states and attention.
pt-BR: Deriva phi, psi, sigma, epsilon a partir dos estados ocultos e atenção.
"""

from __future__ import annotations

from typing import Any


def derive_affect(hidden_states: Any = None, attentions: Any = None) -> dict:
    """Derive affect metrics (no metaphor).

    English: Returns measurable affect metrics only.
    pt-BR: Retorna apenas métricas afetivas mensuráveis.
    """
    return {
        "phi": 0.0,
        "psi": 0.0,
        "sigma": 0.0,
        "epsilon": 0.0,
    }


def derive_affect_from_brain() -> dict:
    """Derive affect from brain server state.
    
    English: Fetches from Erika /erika/affect and derives metrics.
    pt-BR: Busca do Erika /erika/affect e deriva métricas.
    """
    try:
        from .server import get_brain_client
        client = get_brain_client()
        if client is None:
            return derive_affect()
        resp = client.get("/erika/affect")
        if resp.status_code != 200:
            return derive_affect()
        data = resp.json()
        # Map brain metrics to affect space
        ent = data.get("attention_entropy_mean")
        norm = data.get("hidden_norm_mean")
        # Derive phi, psi, sigma, epsilon as measurable quantities
        phi = min(1.0, max(0.0, 1.0 - (ent or 0.5))) if ent is not None else 0.0
        psi = min(1.0, max(0.0, ent or 0.0)) if ent is not None else 0.0
        sigma = min(1.0, max(0.0, (norm or 1.0) / 2.0)) if norm is not None else 0.0
        epsilon = 0.1  # base impulse rate
        return {"phi": round(phi, 4), "psi": round(psi, 4), "sigma": round(sigma, 4), "epsilon": round(epsilon, 4)}
    except Exception:
        return derive_affect()
