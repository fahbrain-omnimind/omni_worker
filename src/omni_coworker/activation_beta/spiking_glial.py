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
import os
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


def _raw_signal(item) -> float:
    if not isinstance(item, dict):
        try:
            return float(item)
        except (TypeError, ValueError):
            return 0.0
    for key in ("entropy", "attention_entropy_last", "signal", "value",
                "norm", "norm_drift_mean", "attractor_score"):
        if key in item and item[key] is not None:
            try:
                return float(item[key])
            except (TypeError, ValueError):
                continue
    for v in item.values():
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            return float(v)
    return 0.0


def glial_features(window) -> dict[str, Any]:
    """Glial features sobre sinal bruto com threshold relativo ao regime.

    O bridge recebe a entropia bruta e threshold=mediana+2·mad da própria
    janela: geração normal fica abaixo → sem stress; vagus só sobe com
    entropia acima de ~2 desvios do regime recente. Registros sem `tags`
    ganham tag sintética (modelo, banda de entropia 0.5) — habituação =
    repetição de saída com perfil similar (degeneração real), não
    contagem de janela.
    """
    if not window:
        return {"habituated": 0.0, "sensitized": 0.0,
                "vagus_sedative": 0.0, "pause_code": None, "n": 0}
    raw = [_raw_signal(item) for item in window]
    med = float(np.median(raw))
    mad = max(0.1, float(np.median([abs(s - med) for s in raw])))
    bridge = SpikingGlialVagusBridge(rate=0.1, window=len(window),
                                    threshold=med + 2.0 * mad)
    signals = []
    pressures: list[float] = []
    for item, sig_raw in zip(window, raw):
        if isinstance(item, dict):
            tags = item.get("tags")
            if isinstance(tags, (tuple, list)):
                tags = tuple(tags)
            else:
                tags = (str(item.get("model") or "m"), round(sig_raw * 2) / 2)
            bridge.observe(sig_raw, tags)
            # stress hint from pressure — canal absoluto [0,1+]
            for pk in ("pressure", "stress"):
                if pk in item and item[pk] is not None:
                    try:
                        pressures.append(float(item[pk]))
                    except (TypeError, ValueError):
                        pass
        else:
            bridge.observe(sig_raw, ())
        signals.append(sig_raw)
    st = bridge.state()
    if pressures and max(pressures) >= 0.8:
        st["vagus_sedative"] = max(float(st.get("vagus_sedative") or 0.0), 0.5)
        st["pause_code"] = "pause_code"
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
        if os.getenv("OMNI_GATE_FAIL_CLOSED") == "1":
            return {"allow_generation": False, "glial": {},
                    "reason": "fail-closed"}
        return {"allow_generation": True, "glial": {},
                "reason": "fail-open"}
