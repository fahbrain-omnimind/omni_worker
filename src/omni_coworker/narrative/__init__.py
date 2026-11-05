"""narrative — identity construction (web of belief + values) + life story (Nachträglichkeit).

Orquestração runtime / Runtime orchestration:
    `IdentityConstruction` evolui identidade a partir de valores e web de
    crenças; `LifeStory` inscreve eventos narrativos retroativamente.
    Consumidores: soul/meaning_maker e estágio narrative do integration_loop.

Arquitetura / Architecture:
    Port de src/narrative_consciousness/{identity_construction,life_story_model}.py
    (sovereign, OW-STU-008b: PORTAR). Diferenças vs fonte:
    - persistência sqlite WAL append-only (OMNI_STATE_DIR);
    - classes PascalCase; sem structlog; sem deps pesadas.

Princípios teóricos invocados / Theoretical principles:
    Web of belief (Quine), valores (Rokeach), Nachträglichkeit (Lacan).

pt-BR: identidade evolutiva + narrativa retroativa.
"""

from __future__ import annotations

from .identity import (
    Belief,
    BeliefNetwork,
    IdentityConstruction,
    IdentitySnapshot,
    Value,
    ValueSystem,
    ValueType,
)
from .life_story import LifeStory, NarrativeEvent

__all__ = [
    "Belief",
    "BeliefNetwork",
    "IdentityConstruction",
    "IdentitySnapshot",
    "LifeStory",
    "NarrativeEvent",
    "Value",
    "ValueSystem",
    "ValueType",
]
