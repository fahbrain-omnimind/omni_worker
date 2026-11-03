"""kernel_daemon.scheduler — loop de coleta com cadência curta.

Orquestração runtime / Runtime orchestration:
    `KernelDaemon.run()` executa um ciclo (collect→aggregate→publish)
    a cada `interval_s` (env OMNI_KERNEL_DAEMON_INTERVAL_S, default
    60s — denso o bastante para a janela ~24h da VM). Pode rodar como
    asyncio task dentro do FastAPI (lifespan hook em app.py) ou como
    processo standalone (`python -m ...scheduler --loop`). Ciclo que
    excede o intervalo é registrado; exceções não derrubam o loop.

Arquitetura / Architecture:
    Um único objeto `KernelDaemon` mantém `last_bundle`, `cycles`,
    `errors` — expostos via `status()` e `GET /kernel/daemon`.

pt-BR: loop asyncio (ou standalone) que executa o ciclo collect→
aggregate→publish a cada intervalo configurável.
"""

from __future__ import annotations

import asyncio
import os
import time
from typing import Any

INTERVAL_S = float(os.getenv("OMNI_KERNEL_DAEMON_INTERVAL_S", "60"))
_STATE: dict[str, Any] = {"cycles": 0, "errors": 0, "last_bundle": None,
                        "last_ts": None, "last_duration_s": None}
_HOMEOSTASIS: "Any" = None


def _homeostasis():
    global _HOMEOSTASIS
    if _HOMEOSTASIS is None:
        from .homeostasis import HomeostaticController
        _HOMEOSTASIS = HomeostaticController()
    return _HOMEOSTASIS


def run_cycle() -> dict[str, Any]:
    """One collect→aggregate→publish pass; updates _STATE."""
    from .collector import collect_cycle
    from .features import aggregate
    from .feedback import publish_feedback, _publish

    t0 = time.time()
    try:
        raw = collect_cycle()
        bundle = aggregate(raw)
        # activation_beta: atratores sobre a janela de ativações (OW-STU-009)
        try:
            from ..activation_beta import attractor
            attractor.push(raw.get("activations") or [])
            att = attractor.features()
            if att:
                bundle["attractor"] = att
                _publish("kernel.attractor", att)
            # phi_layer: proxies informacionais sobre a mesma janela (OW-STU-010)
            from ..activation_beta import phi_layer
            pl = phi_layer.features()
            if pl:
                bundle["phi_layer"] = pl
                _publish("kernel.phi_layer", pl)
        except Exception:
            pass
        # homeostasis: phi feeds sublimation; soma feeds the state machine
        homeo = _homeostasis()
        homeo.update_consciousness_state(
            ((bundle.get("soul") or {}).get("phi")) or 0.0)
        homeo_out = homeo.regulate(raw.get("soma") or {})
        bundle["homeostasis"] = homeo_out
        _publish("kernel.homeostasis", homeo_out)
        # desire: falta estrutural = distância do ótimo homeostático;
        # compute() já publica agency.desire na malha
        try:
            from ..psychology.desire_engine import DesireEngine
            d = DesireEngine().compute(
                target={"homeostasis": "optimal"},
                current={"homeostasis": homeo_out.get("state")},
                goals=["homeostatic_optimum", "vram_headroom"])
            bundle["desire"] = {"intensity": d.intensity, "vector": d.vector}
        except Exception:
            pass
        # phi_meta: IIT-simplified over subsystem activity flags
        try:
            from .phi_meta import update as _phi_update
            pm = _phi_update(bundle)
            bundle["phi_meta"] = pm
            _publish("kernel.phi_meta", pm)
        except Exception:
            pass
        # regime: Page-Hinkley shift detection sobre sinais do bundle (D3)
        try:
            from . import regime
            reg = regime.cycle(bundle)
            if reg.get("events"):
                _publish("kernel.regime_shift", reg)
        except Exception:
            pass
        bundle["published_topics"] = publish_feedback(bundle)
        _STATE["last_bundle"] = bundle
    except Exception as e:  # ciclo ruim não derruba o daemon
        _STATE["errors"] += 1
        bundle = {"ts": t0, "error": str(e)}
        try:
            from ..agency import rca
            rca.register_failure("kernel.cycle", str(e), t0)
        except Exception:
            pass
    _STATE["cycles"] += 1
    _STATE["last_ts"] = t0
    _STATE["last_duration_s"] = round(time.time() - t0, 3)
    return bundle


class KernelDaemon:
    """Asyncio wrapper around run_cycle with graceful stop."""

    def __init__(self, interval_s: float = INTERVAL_S) -> None:
        self.interval_s = interval_s
        self._task: asyncio.Task | None = None
        self._stop = asyncio.Event()

    async def _loop(self) -> None:
        while not self._stop.is_set():
            await asyncio.to_thread(run_cycle)
            try:
                await asyncio.wait_for(self._stop.wait(), timeout=self.interval_s)
            except asyncio.TimeoutError:
                pass

    def start(self) -> None:
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        self._stop.set()
        if self._task:
            try:
                await asyncio.wait_for(self._task, timeout=5.0)
            except (asyncio.TimeoutError, asyncio.CancelledError):
                pass


def status() -> dict[str, Any]:
    """Daemon status for /kernel/daemon."""
    return {
        "interval_s": INTERVAL_S,
        **_STATE,
        "last_bundle_topics": (_STATE["last_bundle"] or {}).get("published_topics"),
    }


if __name__ == "__main__":
    import argparse
    import json

    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--interval-s", type=float, default=INTERVAL_S)
    args = ap.parse_args()
    if args.once:
        print(json.dumps(run_cycle(), indent=2, default=str))
    else:
        while True:
            run_cycle()
            time.sleep(args.interval_s)
