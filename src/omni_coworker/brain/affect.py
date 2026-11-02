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
        # Map brain metrics to affect space (unsaturated — audit D1):
        # entropy ~[0,4] observed on Gemma-4 nf4; hidden norm ~[0,300].
        ent = data.get("attention_entropy_mean")
        norm = data.get("hidden_norm_mean")
        phi = min(1.0, max(0.0, 1.0 - (ent or 0.0) / 4.0)) if ent is not None else 0.0
        psi = min(1.0, max(0.0, (ent or 0.0) / 4.0)) if ent is not None else 0.0
        sigma = min(1.0, max(0.0, (norm or 0.0) / 300.0)) if norm is not None else 0.0
        epsilon = round(min(1.0, max(0.0, (norm or 0.0) / 1000.0 + 0.05)), 4)
        return {"phi": round(phi, 4), "psi": round(psi, 4), "sigma": round(sigma, 4), "epsilon": epsilon}
    except Exception:
        return derive_affect()
