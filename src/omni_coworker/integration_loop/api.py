"""integration_loop.api — endpoints /loop/*.

pt-BR: `GET /loop/status`, `GET /loop/cycle/{id}`, `GET
/loop/modulation`, `POST /loop/run` (ciclo sob demanda).
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from . import loop as _loop
from . import store

router = APIRouter(prefix="/loop", tags=["integration-loop"])


@router.get("/status")
def loop_status() -> dict:
    """Loop status: cadence, cycle count, last cycle/modulation."""
    return _loop.status()


@router.get("/cycle/{cycle_id}")
def loop_cycle(cycle_id: str) -> dict:
    """Fetch one persisted cycle by id (ring → sqlite)."""
    c = store.get_cycle(cycle_id)
    if c is None:
        raise HTTPException(status_code=404, detail="cycle not found")
    return c


@router.get("/modulation")
def loop_modulation() -> dict:
    """Latest derived modulation package."""
    mod = _loop.status().get("last_modulation")
    if mod is None:
        raise HTTPException(status_code=404, detail="no cycles yet")
    return mod


@router.post("/run")
def loop_run() -> dict:
    """On-demand cycle (short-horizon observation)."""
    return _loop.run_once()
