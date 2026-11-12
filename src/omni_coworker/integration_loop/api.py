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


def _sanitize_for_api(payload: dict) -> dict:
    """Sanitize any exception messages or internal error details before returning via HTTP.

    Closes CodeQL Alert #21 (CWE-209: Information exposure through an exception).
    """
    safe = dict(payload)
    if safe.get("error") is not None:
        safe["error"] = "cycle_error"
    if "governance" in safe and isinstance(safe["governance"], dict):
        gov = dict(safe["governance"])
        if "skipped" in gov and isinstance(gov["skipped"], list):
            gov["skipped"] = [
                s.split(":")[0] + ":skipped" if ":" in s else s
                for s in gov["skipped"]
            ]
        safe["governance"] = gov
    if "stage_states" in safe and isinstance(safe["stage_states"], dict):
        stages_copy = {}
        for k, v in safe["stage_states"].items():
            if isinstance(v, dict):
                st = dict(v)
                if "metadata" in st and isinstance(st["metadata"], dict):
                    meta = dict(st["metadata"])
                    if "skipped" in meta:
                        meta["skipped"] = "skipped"
                    st["metadata"] = meta
                stages_copy[k] = st
            else:
                stages_copy[k] = v
        safe["stage_states"] = stages_copy
    return safe


@router.post("/run")
def loop_run() -> dict:
    """On-demand cycle (short-horizon observation).

    English: Runs one full integration cycle and returns the payload.
    Internal error details are stripped from the HTTP response — only
    a sanitized status string is exposed (closes CodeQL CWE-209:
    information exposure through an exception).
    pt-BR: Executa um ciclo completo e retorna o payload. Detalhes de
    erro interno são removidos da resposta HTTP — apenas status sanitizado.
    """
    try:
        payload = _loop.run_once()
    except Exception:  # noqa: BLE001
        return {"status": "error", "error": "cycle_error"}
    return _sanitize_for_api(payload)
