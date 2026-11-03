"""activation_beta.attractor — features de atrator sobre a janela.

Orquestração runtime / Runtime orchestration:
Deque in-process (maxlen 256) por modelo; `push(records)` por ciclo do
daemon (registros novos do tail incremental); `features()` devolve o
dict JSON-safe publicado em `kernel.attractor` e inserido no bundle.

Arquitetura / Architecture:
Janela deslizante pura (stdlib + numpy): norm por camada de cada
registro vira uma série temporal; comparar registros consecutivos dá
norm_drift; entropia de atenção contra baseline rolante dá collapse.
`token_repetition` fica fora do P0 — o jsonl não guarda texto.

Princípios teóricos invocados / Theoretical principles:
Atrator = colapso de variabilidade: entropia caindo + drift
concentrado numa camada. Score composto [0,1] alimenta
emotional_charge do BetaElement.

Linha final pt-BR: a produção do modelo vira sinal observável.
"""

from __future__ import annotations

from collections import deque
from typing import Any

import numpy as np

_MAXLEN = 256
_BASELINE_N = 128
_WINDOWS: dict[str, deque] = {}


def push(records: list[dict[str, Any]]) -> int:
    """Append new activation records; returns window size."""
    for r in records or []:
        model = str(r.get("model") or "unknown")
        w = _WINDOWS.setdefault(model, deque(maxlen=_MAXLEN))
        w.append(r)
    return sum(len(w) for w in _WINDOWS.values())


def reset() -> None:
    _WINDOWS.clear()


def window_size() -> int:
    return sum(len(w) for w in _WINDOWS.values())


def _norm_series(w: deque) -> np.ndarray:
    """(n_records, n_layers) norm matrix; missing layers → nan."""
    rows = []
    for r in w:
        layers = r.get("layers") or []
        if layers:
            rows.append([float(l.get("norm") or np.nan) for l in layers])
    if not rows:
        return np.empty((0, 0))
    n = max(len(r) for r in rows)
    arr = np.full((len(rows), n), np.nan)
    for i, r in enumerate(rows):
        arr[i, : len(r)] = r
    return arr


def _entropy_series(w: deque) -> np.ndarray:
    return np.asarray([float(r.get("attention_entropy_last") or np.nan)
                       for r in w], dtype=float)


def _model_features(w: deque) -> dict[str, Any] | None:
    n = len(w)
    if n < 4:
        return None
    norms = _norm_series(w)
    ents = _entropy_series(w)
    out: dict[str, Any] = {"n_records": n}

    if norms.shape[0] >= 2 and norms.shape[1] >= 1:
        drift = np.abs(np.diff(norms, axis=0))
        drift_mean = float(np.nanmean(drift))
        per_layer = np.nanmean(drift, axis=0)
        out["norm_drift_mean"] = round(drift_mean, 4)
        out["divergent_layer"] = int(np.nanargmax(per_layer))
        # concentração: fração do drift total na camada divergente
        tot = float(np.nansum(per_layer))
        out["drift_concentration"] = round(
            float(per_layer[out["divergent_layer"]]) / tot, 4) if tot > 0 else 0.0
    else:
        out.update({"norm_drift_mean": 0.0, "divergent_layer": None,
                    "drift_concentration": 0.0})

    e = ents[~np.isnan(ents)]
    if e.size >= 4:
        k = min(8, e.size // 2)
        baseline = float(np.mean(e[:-k]))  # porção antiga
        h_t = float(np.mean(e[-k:]))        # porção recente
        collapse = 1.0 - (h_t / baseline) if baseline > 0 else 0.0
        out["entropy_now"] = round(h_t, 4)
        out["entropy_baseline"] = round(baseline, 4)
        out["entropy_collapse"] = round(max(0.0, min(1.0, collapse)), 4)
    else:
        out.update({"entropy_now": None, "entropy_baseline": None,
                    "entropy_collapse": 0.0})

    drift_norm = min(1.0, out["norm_drift_mean"] / 10.0)
    out["attractor_score"] = round(
        0.6 * out["entropy_collapse"] + 0.4 * drift_norm, 4)
    return out


def features() -> dict[str, Any]:
    """Attractor features per model over the current window."""
    out = {}
    for model, w in _WINDOWS.items():
        f = _model_features(w)
        if f:
            out[model] = f
    return out


def digest(out: dict[str, Any]) -> str:
    """Text digest of attractor features — β raw_data material."""
    parts = []
    for model, f in sorted(out.items()):
        parts.append(
            f"{model}: score={f.get('attractor_score')} "
            f"collapse={f.get('entropy_collapse')} "
            f"drift={f.get('norm_drift_mean')} "
            f"div_layer={f.get('divergent_layer')} "
            f"conc={f.get('drift_concentration')} n={f.get('n_records')}")
    return " | ".join(parts) or "janela vazia"
