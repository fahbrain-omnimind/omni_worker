"""kernel_daemon.regime — detecção de mudança de regime (Page-Hinkley).

Orquestração runtime / Runtime orchestration:
    A cada ciclo o scheduler alimenta sinais escalares do bundle
    (pressure_load, cpu_percent, gpu_temp_c, attractor_score por
    modelo). Cada sinal tem um tracker Page-Hinkley independente;
    ao disparar, o evento entra no retorno do ciclo e o tracker
    re-baselina. Publicado como `kernel.regime_shift`.

Arquitetura / Architecture:
    Port do candidato D3/OW-AUD-015 (metastability pack): regime
    shift detection online, O(1) por ciclo, sem torch, sem I/O.
    Complementa `homeostasis` (classifica o estado corrente) com
    detecção de *transição* — ex.: GPU entrando em throttle,
    degradação súbita de geração, disco saturando.

Princípios teóricos invocados / Theoretical principles:
    Page-Hinkley (1954): U_t = Σ(x_i − m_t − δ) acumula desvio da
    média corrente; alarme quando max(U) − U_t > λ. λ adapta-se ao
    desvio observado (k·σ) com piso absoluto, δ é a magnitude mínima
    de shift considerada (fração da escala do sinal).

pt-BR: Page-Hinkley por sinal — transições de regime, O(1)/ciclo.
"""

from __future__ import annotations

import math
from typing import Any

# λ = max(lambda_floor, k_sigma·σ); δ = delta_frac da escala observada.
_K_SIGMA = 4.0
_LAMBDA_FLOOR = {"vram_ratio": 0.15, "cpu_percent": 25.0,
                 "gpu_temp_c": 6.0, "attractor": 0.4}
_DELTA_FRAC = 0.15
_MIN_SAMPLES = 10


class _PH:
    """Two-sided Page-Hinkley tracker (running mean/var + drift both ways)."""

    __slots__ = ("cum_dn", "cum_up", "m2", "mean", "min_dn", "min_up", "n")

    def __init__(self) -> None:
        self.n = 0
        self.mean = 0.0
        self.m2 = 0.0
        self.cum_up = 0.0
        self.min_up = 0.0
        self.cum_dn = 0.0
        self.min_dn = 0.0

    def update(self, x: float, delta: float,
               lam: float) -> tuple[float, str] | None:
        """Feed x; return (ph_stat, direction) when alarm fires."""
        self.n += 1
        d = x - self.mean
        self.mean += d / self.n
        self.m2 += d * (x - self.mean)
        self.cum_up += x - self.mean - delta
        self.min_up = min(self.min_up, self.cum_up)
        self.cum_dn += self.mean - x - delta
        self.min_dn = min(self.min_dn, self.cum_dn)
        ph_up, ph_dn = self.cum_up - self.min_up, self.cum_dn - self.min_dn
        if self.n >= _MIN_SAMPLES and (ph_up > lam or ph_dn > lam):
            ph, direction = ((ph_up, "up") if ph_up >= ph_dn
                             else (ph_dn, "down"))
            self.cum_up = self.min_up = 0.0
            self.cum_dn = self.min_dn = 0.0  # re-baseline após detecção
            return ph, direction
        return None

    @property
    def std(self) -> float:
        return math.sqrt(self.m2 / self.n) if self.n > 1 else 0.0


_TRACKERS: dict[str, _PH] = {}
_LAST_SHIFT: dict[str, float] = {}


def feed(name: str, value: float, ts: float,
         *, lam_floor: float | None = None) -> dict[str, Any] | None:
    """Feed one sample; return shift event dict when regime changes."""
    tr = _TRACKERS.setdefault(name, _PH())
    lam = lam_floor if lam_floor is not None else _LAMBDA_FLOOR.get(
        name.split(":")[0], 0.3)
    res = tr.update(float(value), _DELTA_FRAC * lam,
                    max(lam, _K_SIGMA * tr.std))
    if res is None:
        return None
    ph, direction = res
    _LAST_SHIFT[name] = ts
    return {"signal": name, "direction": direction, "ph_stat": round(ph, 4),
            "mean_before": round(tr.mean, 4), "value": round(float(value), 4),
            "ts": ts}


def cycle(bundle: dict[str, Any]) -> dict[str, Any]:
    """Feed this cycle's signals from the aggregated bundle."""
    ts = float(bundle.get("ts") or 0.0)
    soma = bundle.get("soma") or {}
    events = []
    feeds: dict[str, Any] = {}
    for field in ("cpu_percent", "gpu_temp_c"):
        if isinstance(soma.get(field), (int, float)):
            feeds[field] = float(soma[field])
    used, total = soma.get("gpu_vram_used_gb"), soma.get("gpu_vram_total_gb")
    if isinstance(used, (int, float)) and isinstance(total, (int, float)) \
            and total:
        feeds["vram_ratio"] = float(used) / float(total)
    for model, att in (bundle.get("attractor") or {}).items():
        sc = att.get("attractor_score") if isinstance(att, dict) else None
        if isinstance(sc, (int, float)):
            feeds[f"attractor:{model}"] = float(sc)
    for name, x in feeds.items():
        ev = feed(name, x, ts)
        if ev:
            events.append(ev)
    return {"events": events,
            "tracked": sorted(_TRACKERS),
            "last_shift": dict(_LAST_SHIFT)}


def _reset() -> None:
    _TRACKERS.clear()
    _LAST_SHIFT.clear()
