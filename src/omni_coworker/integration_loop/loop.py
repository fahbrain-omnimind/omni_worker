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
from .schema import CycleResult, ModuleState, new_cycle_id

INTERVAL_S = float(os.getenv("OMNI_LOOP_INTERVAL_S", "60"))
CYCLE_TIMEOUT_S = float(os.getenv("OMNI_LOOP_TIMEOUT_S", "25"))
_STATE: dict[str, Any] = {"cycles": 0, "errors": 0, "last_cycle": None,
                        "last_modulation": None, "last_ts": None}


def _publish_modulation(mod, resource_postures=None) -> bool:
    try:
        from ..shared_workspace import bus
        payload = mod.to_dict()
        if resource_postures is not None:
            payload["resource_postures"] = resource_postures
        bus.publish("feedback.loop", payload)
        return True
    except Exception:  # noqa: BLE001
        return False


_GOV: dict[str, Any] | None = None


def _gov() -> dict[str, Any]:
    """Governança por iteração: EventBus→TrustSystem + breakers + quarentena.

    English: One lazy wiring — the gov EventBus feeds the SHARED
    TrustSystem (same scores other consumers see), each stage runs
    under a CircuitBreaker, and a stage that trips its breaker is
    quarantined (skipped in later cycles until `release`) with a
    witness record. Missing governance deps → empty dict, loop runs
    unguarded (fail-open, same as before).
    pt-BR: Uma fiação lazy — o EventBus de governança alimenta o
    TrustSystem COMPARTILHADO (mesmos scores que outros consumidores
    veem), cada estágio roda sob um CircuitBreaker, e um estágio que
    abre o breaker é quarentenado (pulado nos ciclos seguintes até
    `release`) com registro no witness. Dependências ausentes → dict
    vazio, loop roda desguarnecido (fail-open, como antes).
    """
    global _GOV
    if _GOV is not None:
        return _GOV
    try:
        from ..orchestration.governance import (
            EventBus,
            QuarantineSystem,
            get_trust_system,
        )
        bus, trust, quar = EventBus(), get_trust_system(), QuarantineSystem()

        def _feed(etype: str, data: dict[str, Any]) -> None:
            stage = (data or {}).get("stage")
            trust.record_event(
                etype, f"stage.{stage}" if stage else "integration_loop")

        for et in ("loop.stage.ok", "loop.stage.failed",
                   "loop.stage.quarantined",
                   "loop.cycle.completed", "loop.cycle.failed"):
            bus.subscribe(et, _feed)
        _GOV = {"bus": bus, "trust": trust, "quarantine": quar,
                "breakers": {}}
    except Exception:  # noqa: BLE001
        _GOV = {}
    return _GOV


def _run_stage(gov: dict[str, Any], name: str, fn) -> tuple[Any, str | None]:
    """Stage sob breaker+quarentena; retorna (resultado, nota_de_skip).

    English: Quarantined → skip without calling; open breaker → skip;
    failure → record + publish; an opened breaker quarantines the stage
    (witnessed) so a chronically failing component stops being retried
    every cycle.
    pt-BR: Quarentenado → pula sem chamar; breaker aberto → pula;
    falha → registra + publica; breaker aberto quarentena o estágio
    (testemunhado) para que um componente falhando cronicamente pare
    de ser tentado a cada ciclo.
    """
    quar = gov.get("quarantine")
    bus = gov.get("bus")
    cid = f"stage.{name}"
    if quar is not None and quar.is_quarantined(cid):
        return None, "quarantined"
    brs = gov.get("breakers")
    br = None
    if brs is not None:
        from ..orchestration.governance import CircuitBreaker
        br = brs.get(name) or brs.setdefault(
            name, CircuitBreaker(failure_threshold=3,
                                 recovery_timeout=120.0,
                                 name=f"loop.{name}"))
        if not br.is_available():
            return None, "circuit_open"
    try:
        out = fn()
    except Exception as e:  # noqa: BLE001
        err_name = type(e).__name__
        if br is not None:
            br.record_failure()
        if bus is not None:
            bus.publish("loop.stage.failed", {"stage": name,
                                              "error": err_name})
        if br is not None and br.state == "open" and quar is not None:
            quar.quarantine(cid, reason=err_name,
                            evidence={"failures": br.failure_count})
            if bus is not None:
                bus.publish("loop.stage.quarantined", {"stage": name})
            try:
                from ..agency.witness import witness_event
                witness_event("stage_quarantined",
                              {"stage": name, "error": err_name,
                               "failures": br.failure_count})
            except Exception:  # noqa: BLE001, S110
                pass
        return None, err_name
    if br is not None:
        br.record_success()
    if bus is not None:
        bus.publish("loop.stage.ok", {"stage": name})
    return out, None


_PHYLO = None
_PHYLO_TRIED = False


def _phylo_signature():
    """Singleton lazy da assinatura filogenética (fail-open)."""
    global _PHYLO, _PHYLO_TRIED
    if _PHYLO_TRIED:
        return _PHYLO
    _PHYLO_TRIED = True
    try:
        from ..narrative.phylogenetic_signature import PhylogeneticSignature
        _PHYLO = PhylogeneticSignature()
    except Exception:  # noqa: BLE001
        _PHYLO = None
    return _PHYLO


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


def run_once(bundle: dict[str, Any] | None = None) -> dict[str, Any]:
    """One full cycle; returns persisted payload dict."""
    t0 = time.time()
    cid = new_cycle_id(t0)
    rng = np.random.default_rng(abs(hash(cid)) % (2**32))
    stage_states = {}
    if bundle is None:
        bundle = adapters.collect_sensory()
    else:
        bundle = bundle or {}
    status = "ok"
    err = None
    skipped: list[str] = []
    gov = _gov()
    try:
        ctx = {"bundle": bundle, "rng": rng,
               "history": _sensory_history(), "feat_stats": {}}

        s, note = _run_stage(gov, "sensory_input",
                             lambda: stages.sensory_input(ctx))
        if s is None:
            raise RuntimeError(f"sensory_input unavailable: {note}")
        stage_states["sensory_input"] = s
        x = np.asarray(s.embedding, dtype=float)

        # qualia e narrativa são independentes entre si (ambas leem x)
        for name, fn in (("qualia", lambda: stages.qualia(ctx, x)),
                         ("narrative", lambda: stages.narrative(ctx, x))):
            r, note = _run_stage(gov, name, fn)
            if r is None:
                skipped.append(f"{name}:{note}")
                stage_states[name] = ModuleState(
                    name, metadata={"skipped": note})
            else:
                stage_states[name] = r

        nav = stage_states.get("narrative")
        nvec = (np.asarray(nav.embedding, dtype=float)
                if getattr(nav, "embedding", None) else None)

        if nvec is not None:
            # quilting point: narrativa convergindo → tópico fixado
            try:
                from .quilting import detect_quilting_point
                qp = detect_quilting_point(*_narrative_history())
                if qp:
                    nav.metadata["quilting_point"] = qp
            except Exception:  # noqa: BLE001, S110
                pass
            # filogenética: produção matricial alimenta a assinatura
            try:
                sig = _phylo_signature()
                if sig is not None and not sig.state.emergence_complete:
                    n_att = sig.ingest_from_activation_windows()
                    nav.metadata["phylo_attractors"] = n_att
            except Exception:  # noqa: BLE001, S110
                pass

            hint = ",".join((ctx.get("bundle") or {}).get("mesh_topics") or
                            (ctx.get("bundle") or {}).get("models") or ["omni"])
            ctx["meaning_hit"] = adapters.collect_meaning_context(str(hint))
            r, note = _run_stage(
                gov, "meaning_maker",
                lambda: stages.meaning_maker(ctx, nvec))
            if r is None:
                skipped.append(f"meaning_maker:{note}")
                stage_states["meaning_maker"] = ModuleState(
                    "meaning_maker", metadata={"skipped": note})
            else:
                stage_states["meaning_maker"] = r
                # bion β→α: metabolize raw cycle state
                arousal = float(
                    (stage_states["qualia"].metadata or {}).get("arousal") or 0.0)
                r.metadata["bion"] = bion_bridge.metabolize(
                    ctx, arousal, _STATE["cycles"])
        else:
            skipped.append("meaning_maker:no_narrative")
            stage_states["meaning_maker"] = ModuleState(
                "meaning_maker", metadata={"skipped": "no_narrative"})

        for name, fn in (("expectation", lambda: stages.expectation(ctx, x)),
                         ("sensory_feedback",
                          lambda: stages.sensory_feedback(cid, stage_states))):
            r, note = _run_stage(gov, name, fn)
            if r is None:
                skipped.append(f"{name}:{note}")
                stage_states[name] = ModuleState(
                    name, metadata={"skipped": note})
            else:
                stage_states[name] = r
    except Exception:  # noqa: BLE001
        status, err = "error", "loop_execution_failed"
    if skipped and status == "ok":
        status = "partial"

    dur = time.time() - t0
    if dur > CYCLE_TIMEOUT_S:
        status = "partial"
    cycle = CycleResult(cycle_id=cid, ts=t0, stage_states=stage_states,
                        duration_s=round(dur, 3), status=status, error=err)
    payload = cycle.to_dict()
    # posturas de recurso (fail-open: import/avaliação nunca bloqueia o ciclo)
    resource_postures: list[Any] = []
    try:
        from ..psychoanalysis.plasticity_resource import assess_worker_bundle
        resource_postures = [a.to_dict() for a in assess_worker_bundle(bundle or {})]
        if isinstance(bundle, dict):
            bundle["resource_postures"] = resource_postures
    except Exception:  # noqa: BLE001
        resource_postures = []
    payload["resource_postures"] = resource_postures
    mod = derive_modulation(cycle, bundle)
    payload["modulation"] = mod.to_dict()
    # governança por iteração: resumo visível + evento de ciclo p/ trust
    if gov:
        payload["governance"] = {
            "skipped": skipped,
            "quarantined": (gov["quarantine"].quarantined()
                            if gov.get("quarantine") else []),
            "breakers": {n: b.get_stats()["state"]
                         for n, b in (gov.get("breakers") or {}).items()},
        }
        if gov.get("bus") is not None:
            gov["bus"].publish(
                "loop.cycle.failed" if status == "error"
                else "loop.cycle.completed",
                {"cycle_id": cid, "status": status, "skipped": skipped})
    store.append_cycle(payload)
    from .consumer import write_modulation
    write_modulation(mod.to_dict())
    if _publish_modulation(mod, resource_postures):
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
            except TimeoutError:
                pass

    def start(self) -> None:
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        self._stop.set()
        if self._task:
            try:
                await asyncio.wait_for(self._task, timeout=5.0)
            except (TimeoutError, asyncio.CancelledError):
                pass


def status() -> dict[str, Any]:
    return {"interval_s": INTERVAL_S, "cycle_timeout_s": CYCLE_TIMEOUT_S,
            **_STATE}
