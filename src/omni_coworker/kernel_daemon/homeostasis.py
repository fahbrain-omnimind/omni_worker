"""kernel_daemon.homeostasis — máquina de estados homeostática.

Orquestração runtime / Runtime orchestration:
    Sem loop próprio — o kernel_daemon chama `regulate(soma)` a cada
    ciclo de 60s e publica `kernel.homeostasis` na malha (estado,
    ação, throttled, vram). `should_execute_task(priority)` é o gate
    consultável por consumidores (orchestrator, swap scheduler).

Arquitetura / Architecture:
    Port adaptado de src/metacognition/homeostasis.py (sovereign,
    OW-STU-008a: PORTAR). Diferenças vs fonte:
    - métricas injetadas do `soma.probe` do worker (+ vram_ratio,
      recurso crítico ausente no original — L4 saturável);
    - sem asyncio loop interno — cadência externa do daemon;
    - `current_phi` alimentado do mesh `soul.phi` (sublimação:
      phi>0.3 + task CRITICAL ignora EMERGENCY);
    - thresholds incluem VRAM no max() — GPU conta como recurso.

Princípios teóricos invocados / Theoretical principles:
    Homeostase: estados OPTIMAL→EMERGENCY por uso máximo de recursos;
    "soul over body" — tarefa crítica com phi alto sobrevive ao
    throttle (sublimação controlada, não auto-aplicação destrutiva).

pt-BR: máquina de estados de recursos (cpu/ram/disk/vram) chamada
pelo kernel_daemon; publica kernel.homeostasis na malha.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ResourceState(str, Enum):
    OPTIMAL = "optimal"      # <60%
    GOOD = "good"            # 60-80%
    WARNING = "warning"      # 80-90%
    CRITICAL = "critical"    # 90-95%
    EMERGENCY = "emergency"  # >95%


class TaskPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    BACKGROUND = "background"


@dataclass
class ResourceMetrics:
    """cpu/ram/disk/vram snapshot; state = worst axis."""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    vram_percent: float = 0.0
    timestamp: float = field(default_factory=time.time)

    def get_overall_state(self) -> ResourceState:
        m = max(self.cpu_percent, self.memory_percent,
                self.disk_percent, self.vram_percent)
        if m >= 95: return ResourceState.EMERGENCY
        if m >= 90: return ResourceState.CRITICAL
        if m >= 80: return ResourceState.WARNING
        if m >= 60: return ResourceState.GOOD
        return ResourceState.OPTIMAL

    def to_dict(self) -> dict[str, Any]:
        return {"cpu_percent": self.cpu_percent,
                "memory_percent": self.memory_percent,
                "disk_percent": self.disk_percent,
                "vram_percent": self.vram_percent,
                "timestamp": self.timestamp,
                "state": self.get_overall_state().value}


class HomeostaticController:
    """State machine; the kernel daemon drives the cadence."""

    def __init__(self) -> None:
        self._metrics: ResourceMetrics | None = None
        self._history: list[dict] = []
        self._regulation_history: list[dict] = []
        self._throttled = False
        self._throttle_start: float | None = None
        self.prev_state = ResourceState.OPTIMAL
        # Sublimation: soul over body
        self.current_phi = 0.0
        self.current_priority = TaskPriority.MEDIUM

    def update_consciousness_state(self, phi: float,
                                   priority: TaskPriority = TaskPriority.MEDIUM) -> None:
        self.current_phi = phi
        self.current_priority = priority

    def metrics_from_soma(self, soma: dict[str, Any]) -> ResourceMetrics:
        """Build metrics from the worker's soma.probe payload."""
        gpu = ((soma.get("gpu") or {}).get("gpus") or [{}])[0]
        used, total = gpu.get("vram_used_gb", 0.0), gpu.get("vram_total_gb", 1.0)
        disk = (soma.get("disk") or {}).get("percent") or 0.0
        return ResourceMetrics(
            cpu_percent=soma.get("cpu_percent") or 0.0,
            memory_percent=soma.get("ram_percent") or soma.get("memory_percent") or 0.0,
            disk_percent=disk,
            vram_percent=(used / total * 100.0) if total else 0.0,
        )

    def regulate(self, soma: dict[str, Any]) -> dict[str, Any]:
        """One regulation step; returns action dict for the daemon."""
        m = self.metrics_from_soma(soma or {})
        self._metrics = m
        self._history.append(m.to_dict())
        self._history = self._history[-100:]
        state = m.get_overall_state()
        action = "monitor"
        sublimated = False

        if state == ResourceState.EMERGENCY:
            sublimated = (self.current_phi > 0.3
                          and self.current_priority == TaskPriority.CRITICAL)
            if sublimated:
                action = "sublimated_override"
                self._deactivate_throttling()
            else:
                action = "emergency_throttle"
                if not self._throttled:
                    self._activate_throttling()
        elif state == ResourceState.CRITICAL:
            action = "reduce_load"
        elif self._throttled and state in (ResourceState.OPTIMAL, ResourceState.GOOD):
            action = "throttle_released"
            self._deactivate_throttling()

        changed = state != self.prev_state
        self.prev_state = state
        rec = {"timestamp": time.time(), "state": state.value,
               "action": action, "state_changed": changed,
               "sublimated": sublimated}
        self._regulation_history.append(rec)
        self._regulation_history = self._regulation_history[-200:]
        return {**rec, "metrics": m.to_dict(), "throttled": self._throttled}

    def should_execute_task(self, priority: TaskPriority) -> bool:
        if not self._metrics:
            return True
        state = self._metrics.get_overall_state()
        if state == ResourceState.EMERGENCY:
            return (priority == TaskPriority.CRITICAL
                    and self.current_phi > 0.3) or priority == TaskPriority.CRITICAL
        if state == ResourceState.CRITICAL:
            return priority in (TaskPriority.CRITICAL, TaskPriority.HIGH)
        if state == ResourceState.WARNING:
            return priority != TaskPriority.BACKGROUND
        return True

    def _activate_throttling(self) -> None:
        self._throttled = True
        self._throttle_start = time.time()

    def _deactivate_throttling(self) -> None:
        self._throttled = False
        self._throttle_start = None

    def get_stats(self) -> dict[str, Any]:
        return {"throttled": self._throttled,
                "state": self.prev_state.value,
                "metrics": self._metrics.to_dict() if self._metrics else None,
                "history_size": len(self._history),
                "regulations": self._regulation_history[-10:]}
