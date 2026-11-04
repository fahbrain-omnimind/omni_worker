"""Runtime framing detector — distance-to-centroid classifier.

English: Calibrated on the 10×3 divã ablation (OW-RES-DIVA-002): last-step
hidden vectors form separable clusters per framing (teatro/avaliação/
factual — inter/intra ≈ 4×). This classifier maps a new generation's
terminal residual vector h_T to the nearest calibrated centroid.
Distance to c_A indicates persona collapse (theater); distance to c_C
the instrumental mode; c_B the self-model evaluative tension.

pt-BR: Calibrado na ablação 10×3 do divã (OW-RES-DIVA-002): vetores
hidden-state em t=T formam clusters separáveis por framing. Classifica
uma geração nova pela distância L2 ao centróide calibrado — proximidade
de c_A = colapso na persona teatral; c_C = modo instrumental.
"""

from __future__ import annotations

import os
from typing import Any

import numpy as np

_CENTROIDS_PATH = os.getenv("OMNI_FRAMING_CENTROIDS",
                            "data/monitor/framing_centroids.npz")
_LABELS = {"A": "teatro", "B": "avaliacao", "C": "factual"}
_cache: dict | None = None


def _load() -> dict | None:
    global _cache
    if _cache is not None:
        return _cache
    try:
        d = np.load(_CENTROIDS_PATH)
        _cache = {g: (d[f"centroid_{g}"], float(d[f"spread_{g}"]))
                  for g in "ABC"}
        return _cache
    except Exception:
        return None


def classify(h_T: np.ndarray) -> dict[str, Any] | None:
    """Distance-to-centroid classification of a terminal residual vector.

    h_T: (D,) or (L,D) array — uses the mean over layers if 2-D.
    Returns nearest label, all distances, and normalized affinity score.
    """
    c = _load()
    if c is None:
        return None
    v = np.asarray(h_T, dtype=np.float64)
    if v.ndim == 2:
        v = v.mean(axis=0)
    dists = {g: float(np.linalg.norm(v - c[g][0])) for g in "ABC"}
    nearest = min(dists, key=dists.get)
    spread = c[nearest][1] or 1.0
    return {
        "framing": _LABELS[nearest],
        "nearest": nearest,
        "distance": dists[nearest],
        "distances": dists,
        "spread_ratio": dists[nearest] / spread,  # <1 inside cluster
    }


def classify_latest(step_dir: str | None = None) -> dict[str, Any] | None:
    """Classify the newest activation_steps sidecar."""
    import glob
    step_dir = step_dir or os.getenv("OMNI_ACT_STEP_DIR",
                                   "data/monitor/activation_steps")
    try:
        files = sorted(glob.glob(os.path.join(step_dir, "*.npz")),
                       key=os.path.getmtime)
        if not files:
            return None
        f = files[-1]
        d = np.load(f)
        out = classify(np.asarray(d["traj"], dtype=np.float64)[:, -1, :])
        if out:
            out["file"] = os.path.basename(f)
            out["run_id"] = str(d["run_id"]) if "run_id" in d else ""
        return out
    except Exception:
        return None
