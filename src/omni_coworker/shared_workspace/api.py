"""shared_workspace.api — router FastAPI `/mesh/*` do barramento.

Orquestração runtime / Runtime orchestration:
    Expõe o barramento a consumidores fora do processo (daemons
    standalone como swap_scheduler/state_guard publicam via POST
    /mesh/publish; observadores leem via GETs). Single-worker uvicorn é
    premissa: o hot buffer é in-process e não compartilhado entre
    workers.

pt-BR: endpoints do barramento — estado agregado, tópicos, histórico,
publicação externa e saúde.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from . import bus, store

router = APIRouter(prefix="/mesh", tags=["mesh"])


class PublishReq(BaseModel):
    topic: str
    payload: Any


@router.get("/state")
def mesh_state() -> dict:
    """Latest event per canonical topic — current face of the mesh."""
    hot = bus.snapshot()
    if not hot:
        hot = store.latest_per_topic()  # cold boot: serve last persisted
    return {"topics": bus.topics(), "state": hot}


@router.get("/topic/{name:path}")
def mesh_topic(name: str, n: int = 1) -> dict:
    """Latest event (n>1 → history) on one topic."""
    return {"topic": name, "events": bus.history(name, n) or store.history(name, n)}


@router.post("/publish")
def mesh_publish(req: PublishReq) -> dict:
    """External producer path — same validation as in-process publish."""
    try:
        return bus.publish(req.topic, req.payload)
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=422, detail=str(e)) from e


@router.get("/metrics")
def mesh_metrics() -> dict:
    """Bus health: topics, hot depth, persisted rows, publish rate hint."""
    return {
        "topics": len(bus.topics()),
        "hot": {t: len(v) for t, v in bus._hot.items()},
        "persisted_latest": len(store.latest_per_topic()),
    }
