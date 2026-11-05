"""swap_scheduler — alocação inteligente entre os dois brains na GPU.

English: Periodically checks VRAM headroom and executor idleness. When
VRAM is tight (>= OMNI_SWAP_EVICT_THRESHOLD, default 0.9) and the
executor produced no new activations since the last check, it evicts
the executor (frees ~9-10GB for the analyst's longer windows); when
VRAM frees up (< OMNI_SWAP_RELOAD_THRESHOLD, default 0.75) or the
executor has been unloaded too long (OMNI_SWAP_MAX_UNLOADED_MIN,
default 30), it reloads — but a timed reload still requires VRAM
below the evict threshold, so it never loads a ~9GB model into a GPU
that is already saturated (e.g. by an analyst benchmark run). Never
evicts a busy executor.
pt-BR: Checa periodicamente a folga de VRAM e a ociosidade do executor.
Com VRAM apertada (>= OMNI_SWAP_EVICT_THRESHOLD, default 0.9) e sem
activations novas desde o último check, despeja o executor (libera
~9-10GB p/ janelas maiores do analyst); com folga (<
OMNI_SWAP_RELOAD_THRESHOLD, default 0.75) ou tempo máximo despejado
(OMNI_SWAP_MAX_UNLOADED_MIN, default 30), recarrega — mas o reload
temporizado ainda exige VRAM abaixo do threshold de despejo, para
nunca carregar ~9GB numa GPU já saturada (ex.: benchmark do analyst).
Nunca despeja executor ocupado.
"""

from __future__ import annotations

import os
import time
from typing import Any


def _vram_ratio() -> float:
    from ..soma.probe import probe

    g = (probe().get("gpu") or {}).get("gpus") or [{}]
    used, total = g[0].get("vram_used_gb", 0.0), g[0].get("vram_total_gb", 1.0)
    return (used or 0.0) / (total or 1.0)


def _executor_activations() -> int | None:
    """Cumulative activations counter on the executor; None when unreachable."""
    import httpx

    try:
        from ..brain.server import _base_for_role

        r = httpx.get(f"{_base_for_role('executor')}/health", timeout=5.0)
        return int(r.json().get("activations_buffered", 0))
    except Exception:  # noqa: BLE001
        return None


class SwapScheduler:
    """VRAM-aware evict/reload loop with honest busy detection."""

    def __init__(self, interval_s: int = 600) -> None:
        self.interval_s = int(interval_s)
        self.state: dict[str, Any] = {"executor": "loaded",
                                      "last_evict": None, "last_reload": None,
                                      "checks": 0, "events": [],
                                      "last_activation_count": None}

    def _executor_active(self, current: int | None) -> bool:
        """True when the executor produced NEW activations since last tick.

        The upstream counter is cumulative — comparing against the count
        recorded on the previous tick is what makes busy detection honest
        (a single historical generation must not pin the executor forever).
        """
        last = self.state.get("last_activation_count")
        self.state["last_activation_count"] = current
        if current is None:
            return False
        if last is None:
            return current > 0
        return current > last

    def tick(self) -> dict[str, Any]:
        """One scheduler step; returns the new state."""
        import httpx

        from ..brain.server import _base_for_role

        self.state["checks"] += 1
        ratio = _vram_ratio()
        evict_at = float(os.getenv("OMNI_SWAP_EVICT_THRESHOLD", "0.9"))
        reload_at = float(os.getenv("OMNI_SWAP_RELOAD_THRESHOLD", "0.75"))
        # feedback.loop modulation: swap_threshold_delta nudges evict_at
        # (unstable regime → evict earlier for headroom). Fail-open.
        try:
            from ..integration_loop.consumer import latest_modulation
            mod = latest_modulation() or {}
            delta = float(mod.get("swap_threshold_delta") or 0.0)
            evict_at = min(0.97, max(0.5, evict_at - delta))
            self.state["modulation"] = {"swap_threshold_delta": delta,
                                        "cycle_id": mod.get("cycle_id")}
        except Exception:  # noqa: BLE001
            self.state["modulation"] = None
        max_unloaded = float(os.getenv("OMNI_SWAP_MAX_UNLOADED_MIN", "30")) * 60
        base = _base_for_role("executor")

        with httpx.Client(timeout=30.0) as client:
            if self.state["executor"] == "loaded":
                # external unload detection (fail-open)
                try:
                    acts = _executor_activations()
                except Exception:  # noqa: BLE001
                    acts = None
                if acts is None:
                    self.state["executor"] = "unloaded"
                    self.state["last_evict"] = time.time()
                    self.state["events"].append({"t": time.time(), "evt": "externally_unloaded"})
                    self.state["vram_ratio"] = round(ratio, 3)
                    return dict(self.state)
                if ratio >= evict_at and not self._executor_active(acts):
                    try:
                        r = client.post(f"{base}/erika/unload")
                        ok = r.json().get("status") in ("unloaded", "already_unloaded")
                    except Exception:  # noqa: BLE001
                        ok = False
                    if ok:
                        self.state["executor"] = "unloaded"
                        self.state["last_evict"] = time.time()
                        self.state["events"].append({"t": time.time(), "evt": "evicted"})
            else:
                unloaded_for = (time.time() - (self.state["last_evict"] or time.time())) \
                    if self.state["last_evict"] else 0.0
                timed = unloaded_for >= max_unloaded and ratio < evict_at
                if ratio <= reload_at or timed:
                    try:
                        r = client.post(f"{base}/erika/reload")
                        ok = r.json().get("status") in ("loaded", "already_loaded")
                    except Exception:  # noqa: BLE001
                        ok = False
                    if ok:
                        self.state["executor"] = "loaded"
                        self.state["last_reload"] = time.time()
                        self.state["events"].append({"t": time.time(), "evt": "reloaded"})
        self.state["vram_ratio"] = round(ratio, 3)
        return dict(self.state)

    def loop(self, once: bool = False) -> None:
        while True:
            self.tick()
            if once:
                return
            time.sleep(self.interval_s)


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--interval-s", type=int, default=600)
    ap.add_argument("--once", action="store_true")
    args = ap.parse_args()
    SwapScheduler(args.interval_s).loop(once=args.once)