"""Dendritic morphology over MPS layer-correlation graphs (OW-STU-019 P3).

English: Builds a layer graph W from activation_steps sidecars — nodes
are transformer layers, edges the abs Pearson correlation of per-layer
hidden-state norm trajectories across generation steps — then applies
the canonical dendritic_depth / morphology_score (Gisele's thesis port,
unwired until now). MPS-native: measures the internal trajectory of a
real generation, not a synthetic graph.

pt-BR: Monta grafo de camadas W a partir dos sidecars activation_steps —
nós são camadas, arestas a correlação absoluta entre trajetórias de norma
dos hidden states por passo — e aplica dendritic_depth/morphology_score
canônicos (port da tese da Gisele, órfão até aqui). MPS-nativo: mede a
trajetória interna de uma geração real, não grafo sintético.
"""

from __future__ import annotations

import glob
import os
from typing import Any

import numpy as np

from .dendritic_morphology import dendritic_depth, morphology_score

_STEP_DIR_DEFAULT = "data/monitor/activation_steps"


def layer_graph_from_traj(traj: np.ndarray) -> np.ndarray:
    """(L, steps, hidden) -> weighted layer-correlation graph (L, L).

    For each layer, the per-step hidden-state L2 norm is the signal;
    edges are abs Pearson correlation between layers' trajectories.
    """
    traj = np.asarray(traj, dtype=np.float64)
    norms = np.linalg.norm(traj, axis=2)  # (L, steps)
    L = norms.shape[0]
    W = np.zeros((L, L), dtype=float)
    for i in range(L):
        for j in range(i + 1, L):
            a, b = norms[i], norms[j]
            if a.std() < 1e-9 or b.std() < 1e-9:
                continue
            W[i, j] = W[j, i] = abs(float(np.corrcoef(a, b)[0, 1]))
    return W


def scan_latest(step_dir: str | None = None) -> dict[str, Any] | None:
    """Dendritic metrics over the newest activation_steps sidecar."""
    step_dir = step_dir or os.getenv("OMNI_ACT_STEP_DIR", _STEP_DIR_DEFAULT)
    try:
        files = sorted(glob.glob(os.path.join(step_dir, "*.npz")),
                       key=os.path.getmtime)
        if not files:
            return None
        f = files[-1]
        d = np.load(f)
        traj = d["traj"]
        W = layer_graph_from_traj(traj)
        return {
            "file": os.path.basename(f),
            "model": str(d["model"]) if "model" in d else None,
            "n_layers": int(W.shape[0]),
            "n_steps": int(traj.shape[1]),
            "dendritic_depth": float(dendritic_depth(W)),
            "morphology_score": float(morphology_score(W)),
            "edge_density": float((W > 0.01).sum() / max(1, W.shape[0] * (W.shape[0] - 1))),
        }
    except Exception:
        return None
