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

import os

from collections import deque
from typing import Any

import numpy as np

from ..activation_beta import spiking_glial

_MAXLEN = 256
_BASELINE_N = 128
_WINDOWS: dict[str, deque] = {}
_REHYDRATED = False


def push(records: list[dict[str, Any]]) -> int:
    """Append new activation records; returns window size."""
    for r in records or []:
        model = str(r.get("model") or "unknown")
        w = _WINDOWS.setdefault(model, deque(maxlen=_MAXLEN))
        w.append(r)
    return sum(len(w) for w in _WINDOWS.values())


def rehydrate(log_path: Any | None = None, tail_bytes: int = 1 << 19) -> int:
    """Seed windows from the jsonl tail after a restart.

    Reads the last `tail_bytes` (default 512KB) of the activations log
    and loads the newest _MAXLEN records per model — WITHOUT touching
    the persisted `.offset` used by the incremental tail (read-back,
    not read-forward). Runs once per process; window survives daemon
    restart with its recent context intact.
    """
    global _REHYDRATED
    if _REHYDRATED or _WINDOWS:
        return window_size()
    _REHYDRATED = True
    try:
        import json
        from pathlib import Path
        if log_path is None:
            from ..kernel_daemon.collector import ACTIVATIONS_LOG
            log_path = ACTIVATIONS_LOG
        log = Path(log_path)
        if not log.exists():
            return 0
        with log.open("rb") as fh:
            fh.seek(0, 2)
            size = fh.tell()
            fh.seek(max(0, size - tail_bytes))
            chunk = fh.read()
        lines = chunk.split(b"\n")[1:] if size > tail_bytes else chunk.split(b"\n")
        kept: dict[str, deque] = {}
        for line in lines:
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            model = str(r.get("model") or "unknown")
            kept.setdefault(model, deque(maxlen=_MAXLEN)).append(r)
        _WINDOWS.update(kept)
    except Exception:
        pass
    return window_size()


def reset() -> None:
    global _REHYDRATED
    _WINDOWS.clear()
    _REHYDRATED = False


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


def glial_verdict(window=None) -> dict[str, Any]:
    """Veredito glial para degeneração.

    Se window None, agrega todas as janelas do attractor.
    """
    global _REHYDRATED
    if not _REHYDRATED:
        try:
            rehydrate()
        except Exception:
            pass
        _REHYDRATED = True
    if window is None:
        combined = []
        for w in _WINDOWS.values():
            combined.extend(list(w))
        window = combined
    try:
        return spiking_glial.glial_gate({}, window)
    except Exception:
        if os.getenv("OMNI_GATE_FAIL_CLOSED") == "1":
            return {"allow_generation": False, "glial": {},
                    "reason": "fail-closed"}
        return {"allow_generation": True, "glial": {}, "reason": "fail-open"}


def features() -> dict[str, Any]:
    """Attractor features per model over the current window."""
    out = {}
    for model, w in _WINDOWS.items():
        f = _model_features(w)
        if f:
            f["glial_gate"] = spiking_glial.glial_gate({}, list(w))
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
