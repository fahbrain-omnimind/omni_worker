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


def run_cycle() -> dict[str, Any]:
    """One collect→aggregate→publish pass; updates _STATE."""
    from .collector import collect_cycle
    from .features import aggregate
    from .feedback import publish_feedback

    t0 = time.time()
    try:
        raw = collect_cycle()
        bundle = aggregate(raw)
        bundle["published_topics"] = publish_feedback(bundle)
        _STATE["last_bundle"] = bundle
    except Exception as e:  # ciclo ruim não derruba o daemon
        _STATE["errors"] += 1
        bundle = {"ts": t0, "error": str(e)}
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
