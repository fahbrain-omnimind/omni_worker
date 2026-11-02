"""integration_loop.schema — CycleResult / Modulation.

Arquitetura / Architecture:
    `CycleResult` é o registro imutável de um ciclo (5 estágios +
    fechamento). `Modulation` é o pacote derivado publicado em
    `feedback.loop` e persistido — consumido por orchestrator (role +
    suffix), swap_scheduler (threshold delta) e curiosity (boost).

pt-BR: dataclasses + validação leve; tudo JSON-safe.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any

STAGES = ("sensory_input", "qualia", "narrative", "meaning_maker",
          "expectation", "sensory_feedback")


@dataclass
class ModuleState:
    """Per-stage output (embedding + scalar metadata)."""
    module_name: str
    embedding: list[float] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CycleResult:
    """One full loop cycle record (JSON-safe)."""
    cycle_id: str
    ts: float
    stage_states: dict[str, ModuleState]
    duration_s: float
    status: str = "ok"           # ok | partial | error
    error: str | None = None

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


@dataclass
class Modulation:
    """Modulation package derived from a cycle + recent history."""
    cycle_id: str
    ts: float
    meaning_score: float | None
    pred_err: float | None
    qualia_valence: float | None
    qualia_arousal: float | None
    phi: float | None
    psi: float | None
    sigma: float | None
    epsilon: float | None
    cpu_load: float | None
    ram_pct: float | None
    recommendation: str          # analyst | executor | balanced
    swap_threshold_delta: float  # ±0.05
    curiosity_boost: float       # [0,1]
    prompt_suffix: str

    def to_dict(self) -> dict:
        return asdict(self)


def new_cycle_id(ts: float | None = None) -> str:
    """Deterministic-ish cycle id: epoch-s + suffix."""
    ts = ts or time.time()
    return f"cyc-{int(ts)}-{abs(hash(ts)) % 100000:05d}"
