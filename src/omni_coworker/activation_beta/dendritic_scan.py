"""activation_beta.dendritic_scan — morfologia da trajetória interna sobre camadas.

Orquestração runtime / Runtime orchestration:
    Constrói o grafo de correlação inter-camadas W ∈ R^{L×L} a partir dos
    sidecars `.npz` (`activation_vectors/*.npz` shape `(L, D)` ou
    `activation_steps/*.npz` shape `(L, steps, D)`) usando
    `kernel_hooks.compute.cosine_similarity` (consumidor pesado da crate
    Rust `omnimind_metrics` — fechando P6) e aplica `dendritic_depth(W)`
    e `morphology_score(W)` de `dendritic_morphology.py`.

Arquitetura / Architecture:
    - `layer_correlation_graph(arr, threshold=0.25)`: computa similaridade
      cosseno absoluta entre pares de camadas adjacentes e de salto;
    - `ipr_dim(vec)`: Inverse Participation Ratio (Σ p_i²) e dimensão
      efetiva `1 / IPR` sobre as energias normalizadas das coordenadas;
    - `scan_trajectory(arr)`: retorna `dendritic_depth`, `morphology_score`,
      `ipr_dim_mean`, `eff_dim_mean`, e `contract_drift_cosine` (M3 de
      OW-STU-018: similaridade cosseno entre passo inicial e passo final
      quando `arr` é 3D `(L, steps, D)`);
    - `dendritic_features()`: varre os sidecars recentes por modelo para
      publicação em `kernel.dendritic`.

Princípios teóricos invocados / Theoretical principles:
    Giseli de Sousa (2012/2015): profundidade média do grafo de acoplamento
    como proxy estrutural de separabilidade; Roy & Vetterli (2007) IPR;
    OW-STU-018 M3 (contract drift).

Analogia–homologia (interpretativo, não mecanístico):
    O grafo W entre camadas de um Transformer é tratado como análogo
    topológico de ramificação dendrítica — proxy estrutural [PRX]/[TXT],
    nunca morfologia celular literal nem medida de consciência (OW-MATH-001).

pt-BR: varredura dendrítica e IPR sobre vetores/trajetórias de camadas.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import numpy as np

from ..kernel_hooks.compute import cosine_similarity
from .dendritic_morphology import dendritic_depth


def _steps_dir() -> Path:
    from ..kernel_daemon.collector import ACTIVATIONS_LOG
    override = os.getenv("OMNI_ACT_STEPS_DIR")
    if override:
        return Path(override)
    return ACTIVATIONS_LOG.parent / "activation_steps"


def _vec_dir() -> Path:
    from ..kernel_daemon.collector import ACTIVATIONS_LOG
    override = os.getenv("OMNI_ACT_VEC_DIR")
    if override:
        return Path(override)
    return ACTIVATIONS_LOG.parent / "activation_vectors"


def ipr_dim(vec: np.ndarray) -> tuple[float, float]:
    """Compute (IPR, effective_dim = 1 / (D * IPR)) for a vector."""
    v = np.asarray(vec, dtype=np.float64).reshape(-1)
    d = max(1, v.size)
    e = v * v
    total = float(e.sum())
    if total <= 1e-15:
        return 1.0, 0.0
    p = e / total
    ipr = float(np.sum(p * p))
    eff_dim_ratio = float(1.0 / max(1.0, d * ipr))
    return round(ipr, 6), round(eff_dim_ratio, 6)


def layer_correlation_graph(arr: np.ndarray, threshold: float = 0.25) -> np.ndarray:
    """Build layer connectivity matrix W (L×L) via cosine_similarity."""
    a = np.asarray(arr, dtype=np.float64)
    if a.ndim == 3:
        # (L, steps, D) -> mean across steps or flatten (steps*D)
        l_cnt = a.shape[0]
        flat = a.reshape(l_cnt, -1)
    elif a.ndim == 2:
        l_cnt = a.shape[0]
        flat = a
    else:
        return np.zeros((1, 1), dtype=np.float64)

    # Subsample layers to <= 16 nodes so BFS + pairwise cosine stays O(1)
    if l_cnt > 16:
        idx = np.linspace(0, l_cnt - 1, 16, dtype=int)
        flat = flat[idx]
        l_cnt = 16

    w = np.zeros((l_cnt, l_cnt), dtype=np.float64)
    rows = [flat[i, :256].tolist() for i in range(l_cnt)]
    for i in range(l_cnt):
        for j in range(i + 1, l_cnt):
            sim = abs(float(cosine_similarity(rows[i], rows[j])))
            if sim >= threshold or j == i + 1:
                val = max(sim, 0.02 if j == i + 1 else 0.0)
                w[i, j] = val
                w[j, i] = val
    return w


def scan_trajectory(arr: np.ndarray, threshold: float = 0.25) -> dict[str, Any]:
    """Compute dendritic morphology, IPR, and contract drift over (L, D) or (L, steps, D)."""
    a = np.asarray(arr, dtype=np.float64)
    w = layer_correlation_graph(a, threshold=threshold)
    n_nodes = max(2, w.shape[0])
    depth = float(dendritic_depth(w))
    morph_score = float(max(0.0, 1.0 - depth / float(n_nodes - 1)))

    if a.ndim == 3:
        last_vecs = a[:, -1, :]
        first_vecs = a[:, 0, :]
        drifts = [
            float(cosine_similarity(first_vecs[l, :256].tolist(), last_vecs[l, :256].tolist()))
            for l in range(a.shape[0])
        ]
        contract_retention = round(float(np.mean(drifts)), 4) if drifts else 1.0
        contract_drift = round(float(1.0 - contract_retention), 4)
    elif a.ndim == 2:
        last_vecs = a
        contract_retention = None
        contract_drift = None
    else:
        last_vecs = a.reshape(1, -1)
        contract_retention = None
        contract_drift = None

    iprs, eff_ratios = [], []
    for l in range(last_vecs.shape[0]):
        ipr_val, eff_r = ipr_dim(last_vecs[l])
        iprs.append(ipr_val)
        eff_ratios.append(eff_r)

    return {
        "n_graph_nodes": int(w.shape[0]),
        "dendritic_depth": round(depth, 4),
        "morphology_score": round(morph_score, 4),
        "ipr_dim_mean": round(float(np.mean(iprs)), 6) if iprs else 0.0,
        "eff_dim_ratio_mean": round(float(np.mean(eff_ratios)), 6) if eff_ratios else 0.0,
        "contract_retention_cosine": contract_retention,
        "contract_drift": contract_drift,
        "scale": "layer correlation graph [PRX/TXT]",
    }


def dendritic_features() -> dict[str, Any]:
    """Scan latest sidecars per model and return dendritic/IPR telemetry."""
    out: dict[str, Any] = {}
    for d in (_steps_dir(), _vec_dir()):
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.npz"))[-4:]:
            try:
                z = np.load(f)
                arr = z["trajectory"] if "trajectory" in z else z["vectors"]
                model = str(z["model"].item() if hasattr(z["model"], "item") else z["model"]) if "model" in z else f.stem
                out[model] = scan_trajectory(arr)
            except Exception:
                continue
    return out


def scan_latest(step_dir: str | None = None) -> dict[str, Any] | None:
    """Compat shim for kernel_daemon scheduler (Devin wire): newest
    activation_steps sidecar -> dendritic metrics. Uses Argon's
    scan_trajectory internally."""
    import glob
    import os
    step_dir = step_dir or os.getenv("OMNI_ACT_STEP_DIR", "data/monitor/activation_steps")
    try:
        files = sorted(glob.glob(os.path.join(step_dir, "*.npz")), key=os.path.getmtime)
        if not files:
            return None
        f = files[-1]
        d = np.load(f)
        traj = d["traj"]
        out = scan_trajectory(traj)
        out["file"] = os.path.basename(f)
        out["model"] = str(d["model"]) if "model" in d else None
        out["n_layers"] = int(traj.shape[0])
        out["n_steps"] = int(traj.shape[1])
        return out
    except Exception:
        return None
