"""kernel_daemon.ignition — GWT-lite workspace ignition + synergy proxy.

English: subscribes to every canonical prefix on the shared-workspace
bus and, once per kernel cycle, measures broadcast diversity:

- `distinct_prefixes` — how many canonical sources published this
  cycle. A workspace "ignition" in GWT terms is a non-linear burst of
  global broadcast: here, distinct sources crossing a baseline AND
  metastability coherence above threshold [TXT].
- `synergy_proxy` — mean pairwise mutual information between binary
  prefix-activation series over a sliding window (ΦID-lite: is the
  workspace carrying *joint* structure, not just parallel channels?)
  [PRX].
- `scale` field per OW-MATH-001 scale_stack convention.

Not consciousness, not Φ — a falsifiable broadcast-texture metric.
pt-BR: mede a diversidade de broadcast do workspace (GWT-lite) e a
sinergia entre prefixos (ΦID-lite) — textura falsificável, nunca Φ.
"""

from __future__ import annotations

import math
from collections import deque
from typing import Any

WINDOW = 40            # cycles of prefix-activation history
K_MIN_DISTINCT = 3     # minimum distinct sources for an ignition event
THETA_COHERENCE = 0.5  # metastability coherence gate

_CYCLE_PREFIXES: set[str] = set()
_HISTORY: deque = deque(maxlen=WINDOW)
_HOOKED = False


def _hook() -> None:
    """Subscribe once to all canonical prefixes (lazy, fail-open)."""
    global _HOOKED
    if _HOOKED:
        return
    try:
        from ..shared_workspace import bus
        from ..shared_workspace.schema import CANONICAL_PREFIXES
        for p in CANONICAL_PREFIXES:
            bus.subscribe(p, lambda topic, evt:
                          _CYCLE_PREFIXES.add(topic.split(".")[0]))
        _HOOKED = True
    except Exception:
        pass


def _pairwise_mi(series_a: list[int], series_b: list[int]) -> float:
    """MI between two binary activation series (bits)."""
    n = len(series_a)
    if n < 4:
        return 0.0
    pa = sum(series_a) / n
    pb = sum(series_b) / n
    joint = sum(1 for a, b in zip(series_a, series_b) if a and b) / n
    if pa in (0.0, 1.0) or pb in (0.0, 1.0):
        return 0.0

    def h(p: float) -> float:
        return -(p * math.log2(p) + (1 - p) * math.log2(1 - p)) \
            if 0.0 < p < 1.0 else 0.0
    # joint entropy over the 4 cells
    p11, p10, p01, p00 = joint, pa - joint, pb - joint, 1 - pa - pb + joint
    hj = -sum(c * math.log2(c) for c in (p11, p10, p01, p00) if c > 0.0)
    return max(0.0, h(pa) + h(pb) - hj)


def cycle(bundle: dict[str, Any]) -> dict[str, Any]:
    """One ignition/synergy measurement per kernel cycle."""
    _hook()
    prefixes = set(_CYCLE_PREFIXES)
    _CYCLE_PREFIXES.clear()
    _HISTORY.append(prefixes)
    distinct = len(prefixes)

    # synergy: mean pairwise MI across prefix-activation series
    all_prefixes = sorted({p for win in _HISTORY for p in win})
    series = {p: [int(p in win) for win in _HISTORY] for p in all_prefixes}
    pairs = [(a, b) for i, a in enumerate(all_prefixes)
             for b in all_prefixes[i + 1:]]
    mis = [_pairwise_mi(series[a], series[b]) for a, b in pairs]
    synergy = sum(mis) / len(mis) if mis else 0.0

    coherence = (bundle.get("metastability") or {}).get("coherence_t")
    ignited = (distinct >= K_MIN_DISTINCT
               and (coherence is None or coherence > THETA_COHERENCE))
    return {
        "distinct_prefixes": distinct,
        "prefixes": sorted(prefixes),
        "n_active_prefixes": len(all_prefixes),
        "synergy_proxy": round(synergy, 4),
        "coherence_t": coherence,
        "ignited": bool(ignited),
        "window": len(_HISTORY),
        "scale": "prefix-count + bits [TXT/PRX]",
        "statute": "GWT-lite broadcast texture — not consciousness, not Φ",
    }


def _reset() -> None:
    _CYCLE_PREFIXES.clear()
    _HISTORY.clear()
