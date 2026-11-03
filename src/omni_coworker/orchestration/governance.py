"""Autopoietic governance plane.

English: Clean adapters over the canonical orchestration modules
(src.orchestration.event_bus / trust_system / quarantine_system /
rollback_system / circuit_breaker and src.agentes.orchestrator_metrics).
Each class exposes a small synchronous surface; where the canonical
surface differs (async, dataclass/enum-heavy) we fall back to a minimal
pure-Python engine instead of forcing async into the coworker loop.
pt-BR: Adaptadores limpos sobre os módulos canônicos de orquestração
(src.orchestration.event_bus / trust_system / quarantine_system /
rollback_system / circuit_breaker e src.agentes.orchestrator_metrics).
Cada classe expõe uma pequena superfície síncrona; onde a superfície
canônica difere (async, dataclass/enums pesados) caímos em um motor
puro-Python mínimo em vez de forçar async no loop do coworker.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Callable

__all__ = [
    "EventBus",
    "TrustSystem",
    "QuarantineSystem",
    "RollbackSystem",
    "CircuitBreaker",
    "CircuitBreakerOpen",
    "OrchestratorMetrics",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


# ── EventBus ──────────────────────────────────────────────────────────────────


class EventBus:
    """Synchronous publish/subscribe event bus.

    English: Canonical `OrchestratorEventBus` is async and event-object
    based; reimplemented as a small sync handler registry.
    pt-BR: O `OrchestratorEventBus` canônico é async e baseado em objetos
    de evento; reimplementado como um pequeno registro síncrono.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable[[str, dict[str, Any]], None]]] = {}
        self._history: list[dict[str, Any]] = []

    def subscribe(
        self, event_type: str, handler: Callable[[str, dict[str, Any]], None]
    ) -> Callable[[str, dict[str, Any]], None]:
        """Register a handler for an event type."""
        self._handlers.setdefault(event_type, []).append(handler)
        return handler

    def unsubscribe(self, event_type: str, handler: Callable) -> bool:
        """Remove a handler for an event type."""
        try:
            self._handlers[event_type].remove(handler)
            return True
        except (KeyError, ValueError):
            return False

    def publish(self, event_type: str, data: dict[str, Any] | None = None) -> None:
        """Dispatch an event to subscribers and record it in history."""
        data = data or {}
        record = {"type": event_type, "data": data, "ts": _now()}
        self._history.append(record)
        for handler in list(self._handlers.get(event_type, [])):
            try:
                handler(event_type, data)
            except Exception:
                continue

    def history(self, event_type: str | None = None) -> list[dict[str, Any]]:
        """Return event history, optionally filtered by type."""
        if event_type is None:
            return list(self._history)
        return [e for e in self._history if e["type"] == event_type]

    def clear(self) -> None:
        """Clear handlers and history."""
        self._handlers.clear()
        self._history.clear()


# ── TrustSystem ──────────────────────────────────────────────────────────────


class TrustSystem:
    """Event-driven per-agent trust.

    English: Default trust 0.5; `tests_passed` adds +0.1 (cap 1.0),
    `review_dissent` subtracts -0.2 (floor 0.0). The canonical
    `TrustSystem` computes trust as a success-rate over decisions, which
    does not match this additive event contract, so it is reimplemented.
    pt-BR: Confiança por agente com default 0.5; `tests_passed` soma +0.1
    (teto 1.0), `review_dissent` desconta -0.2 (piso 0.0). O `TrustSystem`
    canônico calcula confiança como taxa de sucesso de decisões, o que
    não corresponde a este contrato aditivo de eventos; reimplementado.
    """

    EVENT_DELTAS: dict[str, float] = {
        "tests_passed": +0.1,
        "review_dissent": -0.2,
        # integration_loop: a confiança acumula evidência por estágio/ciclo
        "loop.stage.ok": +0.02,
        "loop.stage.failed": -0.05,
        "loop.stage.quarantined": -0.1,
        "loop.cycle.completed": +0.01,
        "loop.cycle.failed": -0.03,
    }
    DEFAULT_TRUST = 0.5

    def __init__(self, default_trust: float = DEFAULT_TRUST) -> None:
        self.default_trust = float(default_trust)
        self._state_dir = Path(os.getenv("OMNI_STATE_DIR", "data"))
        self._scores_path = self._state_dir / "trust_scores.json"
        self._events_path = self._state_dir / "trust_events.jsonl"
        self._scores: dict[str, float] = {}
        self._events: list[dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        try:
            if self._scores_path.exists():
                raw = json.loads(self._scores_path.read_text(encoding="utf-8"))
                if isinstance(raw, dict):
                    self._scores = {
                        str(k): float(v) for k, v in raw.items()
                        if isinstance(v, (int, float)) and not isinstance(v, bool)
                    }
        except Exception:
            self._scores = {}

    def _save_scores(self) -> None:
        try:
            self._scores_path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self._scores_path.with_name(self._scores_path.name + ".tmp")
            tmp.write_text(json.dumps(self._scores, ensure_ascii=False), encoding="utf-8")
            os.replace(tmp, self._scores_path)
        except Exception:
            try:
                tmp.unlink(missing_ok=True)
            except Exception:
                pass

    def _append_event(self, record: dict[str, Any]) -> None:
        try:
            self._events_path.parent.mkdir(parents=True, exist_ok=True)
            with self._events_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
        except Exception:
            pass

    def get_trust(self, agent: str = "CodeAgent") -> float:
        """Return current trust for an agent (default DEFAULT_TRUST)."""
        return self._scores.get(agent, self.default_trust)

    def set_trust(self, agent: str, value: float) -> float:
        """Set trust explicitly, clamped to [0.0, 1.0]."""
        value = max(0.0, min(1.0, float(value)))
        self._scores[agent] = value
        self._save_scores()
        return value

    def record_event(self, event_type: str, agent: str = "CodeAgent") -> float:
        """Apply the event delta to an agent's trust.

        English: Unknown event types are no-ops (trust unchanged).
        pt-BR: Tipos de evento desconhecidos são no-ops (confiança
        inalterada).
        """
        delta = self.EVENT_DELTAS.get(event_type, 0.0)
        before = self.get_trust(agent)
        after = round(max(0.0, min(1.0, before + delta)), 6)
        self._scores[agent] = after
        record = {"event": event_type, "agent": agent, "delta": delta, "before": before, "after": after, "ts": _now()}
        self._events.append(record)
        self._save_scores()
        self._append_event(record)
        return after

    def events(self) -> list[dict[str, Any]]:
        """Return the event log."""
        return list(self._events)

    def summary(self) -> dict[str, Any]:
        """Per-agent trust map + event count."""
        return {
            "trust": dict(self._scores),
            "default_trust": self.default_trust,
            "events": len(self._events),
        }


_SHARED_TRUST: "TrustSystem | None" = None


def get_trust_system() -> "TrustSystem":
    """Process-wide shared TrustSystem (audit P0: loop must feed trust).

    English: Singleton so battery, agents and orchestrator accumulate
    evidence on the SAME trust scores instead of fresh 0.5 defaults.
    pt-BR: Singleton para bateria, agentes e orquestrador acumularem
    evidência nos MESMOS scores de confiança em vez de defaults 0.5.
    """
    global _SHARED_TRUST
    if _SHARED_TRUST is None:
        _SHARED_TRUST = TrustSystem()
    return _SHARED_TRUST


# ── QuarantineSystem ─────────────────────────────────────────────────────────


class QuarantineSystem:
    """Quarantine for compromised components.

    English: Canonical `QuarantineSystem` requires an orchestrator and
    async coroutines; reimplemented as a small sync registry.
    pt-BR: O `QuarantineSystem` canônico exige um orquestrador e
    corrotinas async; reimplementado como um pequeno registro síncrono.
    """

    _FILES = ("quarantine.json", "quarantine_records.json")

    def __init__(self) -> None:
        self._state_dir = Path(os.getenv("OMNI_STATE_DIR", "data"))
        self._paths = [self._state_dir / name for name in self._FILES]
        self._records: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        for p in self._paths:
            try:
                if p.exists():
                    raw = json.loads(p.read_text(encoding="utf-8"))
                    if isinstance(raw, dict):
                        self._records = {str(k): v for k, v in raw.items() if isinstance(v, dict)}
                        return
            except Exception:
                continue

    def _save(self) -> None:
        for p in self._paths:
            try:
                p.parent.mkdir(parents=True, exist_ok=True)
                tmp = p.with_name(p.name + ".tmp")
                tmp.write_text(json.dumps(self._records, ensure_ascii=False, default=str), encoding="utf-8")
                os.replace(tmp, p)
            except Exception:
                try:
                    tmp.unlink(missing_ok=True)
                except Exception:
                    pass

    def quarantine(
        self, component_id: str, reason: str, evidence: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Quarantine a component; returns its record."""
        record = {
            "component_id": component_id,
            "reason": reason,
            "evidence": evidence or {},
            "ts": _now(),
        }
        self._records[component_id] = record
        self._save()
        return record

    def release(self, component_id: str) -> bool:
        """Release a component; True when it was quarantined."""
        removed = self._records.pop(component_id, None) is not None
        if removed:
            self._save()
        return removed

    def is_quarantined(self, component_id: str) -> bool:
        """Check quarantine status."""
        return component_id in self._records

    def quarantined(self) -> list[str]:
        """List quarantined component ids."""
        return list(self._records.keys())

    def status(self) -> dict[str, Any]:
        """Summary of quarantined components."""
        return {
            "quarantined": list(self._records.keys()),
            "count": len(self._records),
        }


# ── RollbackSystem ───────────────────────────────────────────────────────────


class RollbackSystem:
    """Snapshot versioning + rollback.

    English: Canonical `rollback_component` is async; reimplemented as a
    synchronous snapshot stack per component.
    pt-BR: O `rollback_component` canônico é async; reimplementado como
    uma pilha síncrona de snapshots por componente.
    """

    def __init__(self, max_versions: int = 10) -> None:
        self.max_versions = int(max_versions)
        self._versions: dict[str, list[dict[str, Any]]] = {}

    def create_snapshot(
        self, component_id: str, state: dict[str, Any], metadata: dict[str, Any] | None = None
    ) -> int:
        """Snapshot a component state; returns the new version number."""
        stack = self._versions.setdefault(component_id, [])
        version = len(stack) + 1
        stack.append(
            {
                "component_id": component_id,
                "version": version,
                "ts": _now(),
                "state": dict(state),
                "metadata": metadata or {},
            }
        )
        # Keep only the last max_versions entries.
        if len(stack) > self.max_versions:
            del stack[: len(stack) - self.max_versions]
        return version

    def rollback_component(self, component_id: str) -> dict[str, Any] | None:
        """Restore the previous snapshot; returns its state (or None).

        English: The most recent snapshot becomes the active version.
        pt-BR: O snapshot mais recente vira a versão ativa.
        """
        stack = self._versions.get(component_id)
        if not stack:
            return None
        return dict(stack[-1]["state"])

    def get_current_version(self, component_id: str) -> int | None:
        """Current version number for a component."""
        stack = self._versions.get(component_id)
        return stack[-1]["version"] if stack else None

    def get_version_history(self, component_id: str, limit: int = 10) -> list[dict[str, Any]]:
        """Recent version metadata for a component."""
        stack = self._versions.get(component_id, [])
        return [
            {"version": s["version"], "ts": s["ts"], "metadata": s["metadata"]}
            for s in stack[-limit:]
        ]

    def get_snapshot(self, component_id: str, version: int) -> dict[str, Any] | None:
        """Snapshot state for a specific version."""
        for s in self._versions.get(component_id, []):
            if s["version"] == version:
                return dict(s["state"])
        return None

    def summary(self) -> dict[str, Any]:
        """Components and their current versions."""
        return {
            "components": {
                cid: {"version": stack[-1]["version"], "snapshots": len(stack)}
                for cid, stack in self._versions.items()
                if stack
            },
            "max_versions": self.max_versions,
        }


# ── CircuitBreaker ───────────────────────────────────────────────────────────


class CircuitBreakerOpen(Exception):
    """Raised when the circuit is open and calls are blocked."""


class CircuitBreaker:
    """Failure-count circuit breaker.

    English: Canonical `AgentCircuitBreaker` is asyncio-based; the sync
    subset (states, record_success/failure, reset) is reimplemented with
    the same state machine and a synchronous call_with_protection.
    pt-BR: O `AgentCircuitBreaker` canônico é baseado em asyncio; o
    subconjunto síncrono (estados, record_success/failure, reset) é
    reimplementado com a mesma máquina de estados e um
    call_with_protection síncrono.
    """

    def __init__(
        self,
        failure_threshold: int = 3,
        timeout: float = 30.0,
        recovery_timeout: float = 60.0,
        name: str | None = None,
    ) -> None:
        self.failure_threshold = int(failure_threshold)
        self.timeout = float(timeout)
        self.recovery_timeout = float(recovery_timeout)
        self.name = name
        self.failure_count = 0
        self.state = "closed"
        self.last_failure_time: float | None = None
        self.last_success_time: float | None = None
        if name:
            self._load()

    # --- persistence (R2: governance amnesia on recycle) -------------
    # Named breakers share OMNI_STATE_DIR/circuit_breakers.json. The
    # timestamps are restored verbatim — an `open` left by a dead process
    # expires on its own via recovery_timeout in is_available(), so a
    # recycle inherits the failure memory without pinning the gate shut.
    @classmethod
    def _store_path(cls) -> Path:
        import os
        d = Path(os.getenv("OMNI_STATE_DIR", "data"))
        d.mkdir(parents=True, exist_ok=True)
        return d / "circuit_breakers.json"

    @classmethod
    def _read_store(cls) -> dict:
        try:
            return json.loads(cls._store_path().read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _load(self) -> None:
        rec = self._read_store().get(self.name) or {}
        try:
            self.failure_count = int(rec.get("failure_count", 0))
            self.state = rec.get("state", "closed")
            self.last_failure_time = rec.get("last_failure_time")
            self.last_success_time = rec.get("last_success_time")
        except Exception:
            pass

    def _save(self) -> None:
        if not self.name:
            return
        try:
            store = self._read_store()
            store[self.name] = {
                "failure_count": self.failure_count,
                "state": self.state,
                "last_failure_time": self.last_failure_time,
                "last_success_time": self.last_success_time,
            }
            path = self._store_path()
            tmp = path.with_name(path.name + ".tmp")
            tmp.write_text(json.dumps(store, ensure_ascii=False),
                           encoding="utf-8")
            os.replace(tmp, path)
        except Exception:
            pass

    def is_available(self) -> bool:
        """True when calls may proceed.

        English: OPEN allows a recovery probe after recovery_timeout
        (HALF_OPEN); HALF_OPEN allows one attempt.
        pt-BR: OPEN permite sonda de recuperação após recovery_timeout
        (HALF_OPEN); HALF_OPEN permite uma tentativa.
        """
        if self.state == "closed":
            return True
        if self.state == "open":
            if (
                self.last_failure_time is not None
                and time.time() - self.last_failure_time >= self.recovery_timeout
            ):
                self.state = "half_open"
                return True
            return False
        return True  # half_open

    def record_success(self) -> None:
        """Register a success; closes a half-open circuit."""
        self.failure_count = 0
        self.last_success_time = time.time()
        if self.state == "half_open":
            self.state = "closed"
        self._save()

    def record_failure(self) -> None:
        """Register a failure; opens the circuit at the threshold."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.state == "half_open":
            self.state = "open"
        elif self.failure_count >= self.failure_threshold:
            self.state = "open"
        self._save()

    def call_with_protection(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Run a sync call guarded by the breaker.

        English: Raises CircuitBreakerOpen when unavailable; failures
        increment the counter, successes reset it.
        pt-BR: Levanta CircuitBreakerOpen quando indisponível; falhas
        incrementam o contador, sucessos resetam.
        """
        if not self.is_available():
            raise CircuitBreakerOpen(f"circuit {self.state}: blocking calls")
        try:
            result = func(*args, **kwargs)
        except Exception:
            self.record_failure()
            raise
        self.record_success()
        return result

    def get_stats(self) -> dict[str, Any]:
        """Breaker state snapshot."""
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "timeout": self.timeout,
            "recovery_timeout": self.recovery_timeout,
            "last_failure_time": self.last_failure_time,
            "last_success_time": self.last_success_time,
        }

    def reset(self) -> None:
        """Reset the breaker to its initial closed state."""
        self.failure_count = 0
        self.state = "closed"
        self.last_failure_time = None
        self.last_success_time = None


# ── OrchestratorMetrics ──────────────────────────────────────────────────────


class OrchestratorMetrics:
    """Per-operation latency/error metrics.

    English: Thin adapter: when the canonical pure-Python collector
    (`src.agentes.orchestrator_metrics.OrchestratorMetricsCollector`) is
    importable it is used as the engine; otherwise a minimal deque-based
    engine with the same semantics is used.
    pt-BR: Adapter fino: quando o coletor canônico puro-Python
    (`src.agentes.orchestrator_metrics.OrchestratorMetricsCollector`) é
    importável, ele é usado como motor; senão um motor mínimo baseado em
    deque com a mesma semântica.
    """

    def __init__(self) -> None:
        self._engine = None
        self._ops: dict[str, list[float]] = {}
        self._errors: dict[str, int] = {}
        self._counts: dict[str, int] = {}
        self.total_requests = 0
        self.total_errors = 0
        try:
            from src.agentes.orchestrator_metrics import OrchestratorMetricsCollector

            self._engine = OrchestratorMetricsCollector()
            self._engine_source = "canonical"
        except Exception:
            self._engine_source = "fallback"

    def push(self, name: str, latency: float, success: bool = True) -> None:
        """Record one operation result."""
        if self._engine is not None:
            self._engine.record(name, float(latency), bool(success))
            return
        self._ops.setdefault(name, []).append(float(latency))
        self._counts[name] = self._counts.get(name, 0) + 1
        self.total_requests += 1
        if not success:
            self._errors[name] = self._errors.get(name, 0) + 1
            self.total_errors += 1

    # Alias matching the canonical `record` name.
    record = push

    def mean(self, name: str) -> float:
        """Mean latency for an operation (0.0 when empty)."""
        if self._engine is not None:
            op = getattr(self._engine, "operations", {}).get(name)
            if op is None:
                return 0.0
            avg = getattr(op, "avg_latency", None)
            return float(avg) if avg is not None else 0.0
        lats = self._ops.get(name, [])
        return sum(lats) / len(lats) if lats else 0.0

    def count(self, name: str) -> int:
        """Number of recorded operations for a name."""
        if self._engine is not None:
            op = getattr(self._engine, "operations", {}).get(name)
            return int(getattr(op, "count", 0)) if op is not None else 0
        return self._counts.get(name, 0)

    def summary(self) -> dict[str, Any]:
        """Aggregate metrics dict (mirrors canonical summary shape)."""
        if self._engine is not None:
            return self._engine.summary()
        return {
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "operations": {
                name: {
                    "count": self._counts.get(name, 0),
                    "errors": self._errors.get(name, 0),
                    "avg_latency": round(self.mean(name), 3),
                }
                for name in self._counts
            },
        }