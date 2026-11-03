"""activation_beta.spiking_glial — glial/spiking heuristic (CPU-only, numpy).

Port heuristico do src/immune/spiking_glial_vagus_bridge.py do sovereign
(OW-STU-012: ADAPT). Como SpikingNetwork nao existe neste repo, esta e
uma versao heuristica pura-numpy que emula as tres dinamicas relevantes:

- habituacao: exposicao repetida a um mesmo estimulo (mesmo topico/embedding)
  reduz a resposta ao longo da janela (decaimento exponencial/leaky).
- sensibilizacao: estimulo forte (erro/feedback negativo repetido) AUMENTA
  a resposta (janela com threshold).
- vagus_sedative: funcao sedativa — quando o estresse do sistema (ex.:
  pressure alto no bundle) excede threshold, reduz atividade/pausa
  (com echo 'pause_code').

Arquitetura / Architecture:
- SpikingGlialVagusBridge(rate=..., window=8) com observe(signal, tags)
  e state() -> dict.
- glial_features(window) consome sinais de ativacao (dicts com entropia,
  norms, etc.) ou lista de floats.
"""

from __future__ import annotations

from collections import deque
from typing import Any

import numpy as np


class SpikingGlialVagusBridge:
    """Heuristica de modulacao glial (CPU-only)."""

    def __init__(self, rate: float = 0.1, window: int = 8, threshold: float = 0.5) -> None:
        self.rate = float(rate)
        self.window = int(window)
        self.threshold = float(threshold)
        self._signals: deque = deque(maxlen=window)
        self._tags: deque = deque(maxlen=window)
        self._stress: deque = deque(maxlen=window)
        self._pause_code: str | None = None

    def observe(self, signal: float, tags: tuple = ()) -> None:
        sig = float(signal)
        self._signals.append(sig)
        self._tags.append(tags)
        stress = max(0.0, -sig) if sig < 0 else max(0.0, sig - self.threshold)
        # vagus sedative: stress alto do sistema (ex: pressure) -> observar via tags? 
        self._stress.append(stress)
        if len(self._stress) >= 2:
            mean_stress = float(np.mean(self._stress))
            if mean_stress > self.threshold:
                self._pause_code = "pause_code"
            else:
                self._pause_code = None

    def observe_stress(self, stress: float) -> None:
        s = float(stress)
        self._stress.append(max(0.0, s))
        if len(self._stress) >= 1:
            mean_stress = float(np.mean(self._stress))
            if mean_stress > self.threshold:
                self._pause_code = "pause_code"
            else:
                self._pause_code = None

    def state(self) -> dict[str, Any]:
        n = len(self._signals)
        if n == 0:
            return {"habituated": 0.0, "sensitized": 0.0,
                    "vagus_sedative": 0.0, "pause_code": self._pause_code}
        arr = np.asarray(self._signals, dtype=float)
        tags_list = list(self._tags)
        habituated = 0.0
        if n >= 2:
            last = tags_list[-1]
            reps = sum(1 for t in tags_list if t == last)
            habituated = float(1.0 - np.exp(-self.rate * (reps - 1))) if reps > 1 else 0.0
            habituated = max(0.0, min(1.0, habituated))
        sensitized = 0.0
        strong = [s for s in arr if abs(s) > self.threshold]
        if len(strong) >= 2:
            sensitized = float(min(1.0, self.rate * len(strong) * float(np.mean(np.abs(strong)))))
        mean_stress = float(np.mean(self._stress)) if self._stress else 0.0
        vagus = float(min(1.0, mean_stress)) if mean_stress > self.threshold else 0.0
        if self._pause_code == "pause_code":
            vagus = max(vagus, 0.5)
        return {
            "habituated": round(habituated, 4),
            "sensitized": round(sensitized, 4),
            "vagus_sedative": round(vagus, 4),
            "pause_code": self._pause_code,
        }


def glial_features(window) -> dict[str, Any]:
    if not window:
        return {"habituated": 0.0, "sensitized": 0.0,
                "vagus_sedative": 0.0, "pause_code": None, "n": 0}
    bridge = SpikingGlialVagusBridge(rate=0.1, window=len(window))
    signals = []
    for item in window:
        if isinstance(item, dict):
            sig = None
            for key in ("entropy", "attention_entropy_last", "signal", "value",
                        "norm", "norm_drift_mean", "attractor_score"):
                if key in item and item[key] is not None:
                    try:
                        sig = float(item[key])
                        break
                    except (TypeError, ValueError):
                        continue
            if sig is None:
                for v in item.values():
                    if isinstance(v, (int, float)) and not isinstance(v, bool):
                        sig = float(v)
                        break
            if sig is None:
                sig = 0.0
            tags = item.get("tags")
            tags = tuple(tags) if isinstance(tags, (tuple, list)) else ()
            bridge.observe(sig, tags)
            # stress hint from pressure
            for pk in ("pressure", "stress"):
                if pk in item and item[pk] is not None:
                    try:
                        bridge.observe_stress(float(item[pk]))
                    except (TypeError, ValueError):
                        pass
            signals.append(sig)
        else:
            try:
                sig = float(item)
            except (TypeError, ValueError):
                sig = 0.0
            bridge.observe(sig, ())
            signals.append(sig)
    st = bridge.state()
    st["n"] = len(window)
    st["mean_signal"] = round(float(__import__("numpy").mean(signals)), 4) if signals else 0.0
    return st


def glial_gate(features: dict, window) -> dict[str, Any]:
    """Gate de degeneração glial: decide se permite geração.

    Fail-open: se qualquer erro, allow_generation=True.
    """
    try:
        if window is not None:
            feats = glial_features(window)
        else:
            feats = features if isinstance(features, dict) else {}
        glial = feats if isinstance(feats, dict) else {}
        vagus = float(glial.get("vagus_sedative", 0.0) or 0.0)
        habituated = float(glial.get("habituated", 0.0) or 0.0)
        if vagus >= 0.5:
            return {"allow_generation": False, "glial": glial,
                    "reason": "vagus_sedative>=0.5"}
        if habituated >= 0.8:
            return {"allow_generation": False, "glial": glial,
                    "reason": "habituated>=0.8"}
        return {"allow_generation": True, "glial": glial, "reason": "ok"}
    except Exception:
        return {"allow_generation": True, "glial": {},
                "reason": "fail-open"}
