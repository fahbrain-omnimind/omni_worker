"""integration_loop.loop — orquestrador do ciclo fechado.

Orquestração runtime / Runtime orchestration:
    `run_once()` executa um ciclo completo (5 estágios + fechamento),
    persiste CycleResult, deriva Modulation e publica `feedback.loop`
    na malha. `IntegrationLoop` é o wrapper asyncio (mesmo padrão do
    KernelDaemon) — cadência `OMNI_LOOP_INTERVAL_S` (default 60s);
    timeout por ciclo 25s → status `partial`.

Arquitetura / Architecture:
    O loop consome `kernel.cycle` do barramento (adapters) — não
    duplica coleta. Ring buffer em `store` alimenta `narrative` e
    `expectation` (histórico de embeddings sensoriais).

pt-BR: orquestra run_once → estágios → persistência → modulação →
publish feedback.loop; wrapper asyncio com cadência configurável.
"""

from __future__ import annotations

import asyncio
import os
import time
from typing import Any

import numpy as np

from . import adapters, bion_bridge, stages, store
from .modulator import derive_modulation
from .schema import CycleResult, new_cycle_id

INTERVAL_S = float(os.getenv("OMNI_LOOP_INTERVAL_S", "60"))
CYCLE_TIMEOUT_S = float(os.getenv("OMNI_LOOP_TIMEOUT_S", "25"))
_STATE: dict[str, Any] = {"cycles": 0, "errors": 0, "last_cycle": None,
                        "last_modulation": None, "last_ts": None}


def _publish_modulation(mod) -> bool:
    try:
        from ..shared_workspace import bus
        bus.publish("feedback.loop", mod.to_dict())
        return True
    except Exception:
        return False


def _sensory_history(n: int = 8) -> list[list[float]]:
    """Last n sensory embeddings from persisted cycles."""
    out = []
    for c in store.history(n):
        st = (c.get("stage_states") or {}).get("sensory_input") or {}
        if st.get("embedding"):
            out.append(st["embedding"])
    return out


def _narrative_history(n: int = 8) -> tuple[list[list[float]], list[str]]:
    """Last n narrative embeddings + aligned topic hints (quilting input)."""
    embs, hints = [], []
    for c in store.history(n):
        ss = c.get("stage_states") or {}
        st = ss.get("narrative") or {}
        if st.get("embedding"):
            embs.append(st["embedding"])
            hints.append(((ss.get("meaning_maker") or {}).get("metadata") or {})
                         .get("topic_hint") or "")
    return embs, hints


def run_once() -> dict[str, Any]:
    """One full cycle; returns persisted payload dict."""
    t0 = time.time()
    cid = new_cycle_id(t0)
    rng = np.random.default_rng(abs(hash(cid)) % (2**32))
    stage_states = {}
    bundle: dict[str, Any] = {}
    status = "ok"
    err = None
    try:
        bundle = adapters.collect_sensory()
        ctx = {"bundle": bundle, "rng": rng,
               "history": _sensory_history(), "feat_stats": {}}

        s = stages.sensory_input(ctx)
        stage_states["sensory_input"] = s
        x = np.asarray(s.embedding, dtype=float)

        stage_states["qualia"] = stages.qualia(ctx, x)
        stage_states["narrative"] = stages.narrative(ctx, x)
        nvec = np.asarray(stage_states["narrative"].embedding, dtype=float)

        # quilting point: narrativa convergindo → tópico fixado temporário
        try:
            from .quilting import detect_quilting_point
            qp = detect_quilting_point(*_narrative_history())
            if qp:
                stage_states["narrative"].metadata["quilting_point"] = qp
        except Exception:
            pass

        hint = ",".join((ctx.get("bundle") or {}).get("mesh_topics") or
                        (ctx.get("bundle") or {}).get("models") or ["omni"])
        ctx["meaning_hit"] = adapters.collect_meaning_context(str(hint))
        stage_states["meaning_maker"] = stages.meaning_maker(ctx, nvec)

        # bion β→α: metabolize raw cycle state (arousal = emotional_charge)
        arousal = float(stage_states["qualia"].metadata.get("arousal") or 0.0)
        stage_states["meaning_maker"].metadata["bion"] = bion_bridge.metabolize(
            ctx, arousal, _STATE["cycles"])

        stage_states["expectation"] = stages.expectation(ctx, x)
        stage_states["sensory_feedback"] = stages.sensory_feedback(cid, stage_states)
    except Exception as e:
        status, err = "error", str(e)

    dur = time.time() - t0
    if dur > CYCLE_TIMEOUT_S:
        status = "partial"
    cycle = CycleResult(cycle_id=cid, ts=t0, stage_states=stage_states,
                        duration_s=round(dur, 3), status=status, error=err)
    payload = cycle.to_dict()
    mod = derive_modulation(cycle, bundle)
    payload["modulation"] = mod.to_dict()
    store.append_cycle(payload)
    from .consumer import write_modulation
    write_modulation(mod.to_dict())
    if _publish_modulation(mod):
        payload["published"] = True
    _STATE.update({"cycles": _STATE["cycles"] + 1,
                   "errors": _STATE["errors"] + (status == "error"),
                   "last_cycle": payload, "last_modulation": mod.to_dict(),
                   "last_ts": t0})
    return payload


class IntegrationLoop:
    """Asyncio wrapper — mirrors KernelDaemon lifecycle."""

    def __init__(self, interval_s: float = INTERVAL_S) -> None:
        self.interval_s = interval_s
        self._task: asyncio.Task | None = None
        self._stop = asyncio.Event()

    async def _loop(self) -> None:
        while not self._stop.is_set():
            await asyncio.to_thread(run_once)
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
    return {"interval_s": INTERVAL_S, "cycle_timeout_s": CYCLE_TIMEOUT_S,
            **_STATE}
