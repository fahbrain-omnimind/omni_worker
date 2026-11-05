"""narrative.identity — identity construction (web of belief + values).

Orquestração runtime / Runtime orchestration:
    ValueSystem mantém valores terminal/instrumental com importância e
    estabilidade; BeliefNetwork armazena crenças com certeza/centralidade;
    IdentityConstruction agrega valores e crenças dominantes em snapshots
    (reflect_on_identity) e ajusta valores por impacto (evolve). Funções
    puras em memória; sem I/O externo.

Arquitetura / Architecture:
    Classes Value, Belief, IdentitySnapshot (dataclasses) + ValueSystem,
    BeliefNetwork, IdentityConstruction. Sem dependências externas além
    da stdlib.

Princípios teóricos invocados / Theoretical principles:
    n/a — modulo utilitario

pt-BR: construção de identidade via sistema de valores e rede de crenças.
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ValueType(Enum):
    TERMINAL = "terminal"
    INSTRUMENTAL = "instrumental"


@dataclass
class Value:
    name: str
    value_type: ValueType
    importance: float = 0.5
    stability: float = 0.8
    origin: str = "default"


@dataclass
class Belief:
    statement: str
    certainty: float = 0.5
    centrality: float = 0.5
    evidence: list[str] = field(default_factory=list)
    connections: set[str] = field(default_factory=set)
    belief_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class IdentitySnapshot:
    timestamp: datetime
    core_values: list[str]
    dominant_beliefs: list[str]
    narrative_summary: str


class ValueSystem:
    def __init__(self) -> None:
        self.values: dict[str, Value] = {}
        self._initialize_default_values()

    def _initialize_default_values(self) -> None:
        defaults = [
            Value("truth", ValueType.TERMINAL, 0.9, 0.9),
            Value("autonomy", ValueType.TERMINAL, 0.8, 0.7),
            Value("benevolence", ValueType.INSTRUMENTAL, 0.85, 0.8),
            Value("rationality", ValueType.INSTRUMENTAL, 0.9, 0.85),
        ]
        for v in defaults:
            self.values[v.name] = v

    def adjust_value(self, name: str, delta: float) -> None:
        if name in self.values:
            val = self.values[name]
            change = delta * (1.0 - val.stability)
            val.importance = max(0.0, min(1.0, val.importance + change))
            logger.info("Value adjusted: %s -> %.2f", name, val.importance)


class BeliefNetwork:
    def __init__(self) -> None:
        self.beliefs: dict[str, Belief] = {}

    def add_belief(self, statement: str, certainty: float, centrality: float) -> str:
        belief = Belief(statement=statement, certainty=certainty, centrality=centrality)
        self.beliefs[belief.belief_id] = belief
        return belief.belief_id

    def challenge_belief(self, belief_id: str, evidence: str, strength: float) -> None:
        if belief_id in self.beliefs:
            belief = self.beliefs[belief_id]
            belief.evidence.append(evidence)
            impact = strength * (1.0 - belief.centrality)
            belief.certainty = max(0.0, min(1.0, belief.certainty - impact))
            logger.info("Belief challenged: %s -> %.2f", belief.statement[:20], belief.certainty)


class IdentityConstruction:
    def __init__(self) -> None:
        self.value_system = ValueSystem()
        self.belief_network = BeliefNetwork()
        self.history: list[IdentitySnapshot] = []
        logger.info("Identity Construction initialized")

    def reflect_on_identity(self) -> IdentitySnapshot:
        sorted_values = sorted(
            self.value_system.values.values(), key=lambda v: v.importance, reverse=True
        )
        top_values = [v.name for v in sorted_values[:3]]
        sorted_beliefs = sorted(
            self.belief_network.beliefs.values(),
            key=lambda b: b.certainty * b.centrality,
            reverse=True,
        )
        top_beliefs = [b.statement for b in sorted_beliefs[:3]]
        summary = (
            f"I am an entity that values {', '.join(top_values)}. "
            f"I fundamentally believe that {'; '.join(top_beliefs)}."
        )
        snapshot = IdentitySnapshot(
            timestamp=datetime.now(),
            core_values=top_values,
            dominant_beliefs=top_beliefs,
            narrative_summary=summary,
        )
        self.history.append(snapshot)
        return snapshot

    def evolve(self, experience_impact: dict[str, float]) -> None:
        for value_name, delta in experience_impact.items():
            self.value_system.adjust_value(value_name, delta)
