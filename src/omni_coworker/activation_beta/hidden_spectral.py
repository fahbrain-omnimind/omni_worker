"""activation_beta.hidden_spectral — espectral/MPS sobre vetores hidden (P2).

Orquestração runtime / Runtime orchestration:
Lê os sidecars `data/monitor/activation_vectors/*.npz` produzidos pelo
`erika_torch_server` (last-token hidden por camada, fp16) e computa,
por modelo, effective rank espectral por camada (matriz K×D das últimas
K gerações) e bond dimension médio via decomposição MPS do vetor.
Publica dentro de `kernel.phi_layer` como seção `spectral`.

Arquitetura / Architecture:
Daemon-side numpy puro (o torch fica no brain). Effective rank =
exp(H(σ²/Σσ²)) (Roy & Vetterli) sobre a matriz (K gerações × D dims)
de cada camada — quão espalhado é o subespaço usado por aquela camada.
Bond dimension: reshape D → sítios (fatoração de D em potências de 2
× fator ímpar, como o pilot soberano 1152=9·2⁷) → Schmidt rank por
corte bipartido — quanta informação precisa fluir entre as metades do
vetor. OW-STU-010 P2: a versão "de dentro" dos proxies de norma.

Princípios teóricos invocados / Theoretical principles:
MPS/TT: um vetor D-dimensional admite decomposição em trem; o rank de
Schmidt em cada corte é o bond dimension — medida direta de emaranha-
mento/informação compartilhada entre partições do estado interno.
Effective rank mede dimensionalidade efetiva do subespaço ativado.
Proxy informacional — não Φ causal (OW-MATH-001).

pt-BR: SVD effective rank + bond dimension MPS sobre hidden vectors.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import numpy as np

_MAX_FILES = 8        # últimas K gerações por modelo
_MAX_DIM_SITES = 11   # cap de sítios MPS (D = odd × 2^10)


def _vec_dir() -> Path:
    from ..kernel_daemon.collector import ACTIVATIONS_LOG
    override = os.getenv("OMNI_ACT_VEC_DIR")
    if override:
        return Path(override)
    return ACTIVATIONS_LOG.parent / "activation_vectors"


def _load_recent(model: str, k: int = _MAX_FILES) -> list[np.ndarray]:
    """Last k sidecars for model → list of (n_layers, hidden) arrays."""
    d = _vec_dir()
    if not d.is_dir():
        return []
    safe = "".join(c if c.isalnum() else "_" for c in model)
    files = sorted(d.glob(f"*_{safe}.npz"))[-k:]
    out = []
    for f in files:
        try:
            z = np.load(f)
            v = z["vectors"].astype(np.float32)
            if v.ndim == 2:
                out.append(v)
        except Exception:
            continue
    return out


def _spectral_entropy(s: np.ndarray) -> float:
    """H of normalized squared singular values (nats)."""
    p = s * s
    p = p / p.sum() if p.sum() > 0 else p
    return float(-(p * np.log(p + 1e-12)).sum())


def _eff_rank(vecs: list[np.ndarray], layer: int) -> tuple[float, float] | None:
    """(eff_rank, spec_entropy) for `layer` across recent generations."""
    try:
        m = np.stack([v[layer] for v in vecs if layer < v.shape[0]])
    except Exception:
        return None
    if m.shape[0] < 2:
        return None
    s = np.linalg.svd(m, compute_uv=False)
    h = _spectral_entropy(s)
    return float(np.exp(h)), h


def _factor_sites(d: int) -> list[int]:
    """D = odd × 2^n → [odd, 2,2,...,2]; falls back to [8]×(D/8) if needed."""
    odd = d
    twos = 0
    while odd % 2 == 0 and odd > 1:
        odd //= 2
        twos += 1
    if odd > 1 and twos <= _MAX_DIM_SITES - 1:
        return [odd] + [2] * twos
    if odd == 1:
        return [2] * twos
    # não fatora limpo: repartição grosseira em sítios ~iguais
    n = min(_MAX_DIM_SITES, 8)
    base, rem = divmod(d, n)
    return [base + (1 if i < rem else 0) for i in range(n)]


def _bond_dims(vec: np.ndarray) -> list[int]:
    """Schmidt rank per MPS cut of the hidden vector (≤64 cap)."""
    d = vec.size
    sites = _factor_sites(d)
    tensor = vec.reshape(sites)
    ranks = []
    left = tensor.reshape(sites[0], -1)
    for cut in range(len(sites) - 1):
        s = np.linalg.svd(left, compute_uv=False)
        ranks.append(int((s > s[0] * 1e-3).sum()) if s.size else 1)
        if cut < len(sites) - 2:
            # reagrupa: (prod sites ≤cut+1) × resto
            prod = int(np.prod(sites[: cut + 2]))
            left = tensor.reshape(prod, -1)
    return ranks


def spectral_features() -> dict[str, Any]:
    """Per-model spectral/MPS features over recent sidecars."""
    out: dict[str, Any] = {}
    d = _vec_dir()
    if not d.is_dir():
        return out
    models = {f.name.split("_", 1)[1][:-4] for f in d.glob("*.npz")
              if "_" in f.name}
    # map safe-name back to real model id via npz metadata
    for safe in models:
        files = sorted(d.glob(f"*_{safe}.npz"))
        model = safe
        for f in files[-1:]:
            try:
                m = np.load(f)["model"]
                model = str(m.item() if hasattr(m, "item") else m)
            except Exception:
                pass
        vecs = _load_recent(model)
        if len(vecs) < 2:
            continue
        n_layers = min(v.shape[0] for v in vecs)
        effs, hent, bonds = [], [], []
        for layer in range(n_layers):
            er = _eff_rank(vecs, layer)
            if er:
                effs.append(er[0])
                hent.append(er[1])
            try:
                v = vecs[-1][layer].astype(np.float64)
                v = v / (np.linalg.norm(v) + 1e-12)
                bonds.append(max(_bond_dims(v)))
            except Exception:
                continue
        if not effs:
            continue
        out[model] = {
            "eff_rank_mean": round(float(np.mean(effs)), 3),
            "spectral_entropy_mean": round(float(np.mean(hent)), 4),
            "bond_dim_max_mean": round(float(np.mean(bonds)), 2) if bonds else None,
            "n_layers": n_layers,
            "n_files": len(vecs),
            "note": "proxy espectral/MPS — não é Φ causal IIT",
        }
    return out
