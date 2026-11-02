"""kernel_daemon.api — endpoints do daemon de feedback.

pt-BR: `GET /kernel/daemon` expõe status/último bundle; `POST
/kernel/daemon/run` dispara um ciclo sob demanda (observação curta).
"""

from __future__ import annotations

from fastapi import APIRouter

from . import scheduler

router = APIRouter(prefix="/kernel", tags=["kernel-daemon"])


@router.get("/daemon")
def kernel_daemon_status() -> dict:
    """Daemon status: interval, cycle count, last bundle topics."""
    return scheduler.status()


@router.post("/daemon/run")
def kernel_daemon_run() -> dict:
    """On-demand cycle (short-horizon observation)."""
    return scheduler.run_cycle()
