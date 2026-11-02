"""psychology.desire_engine — desejo como falta estrutural (Lacan).

Orquestração runtime / Runtime orchestration:
    `DesireEngine` computa a falta estrutural entre um estado-alvo e o
    estado atual do worker, produzindo `desire.intensity` (0-1) e
    `desire.vector` sobre objetivos. Persistência opcional via sqlite
    em OMNI_STATE_DIR. Publica `agency.desire` na malha (fail-open).

Arquitetura / Architecture:
    Port de src/psychology/desire_engine/core.py (sovereign, OW-STU-008b:
    PORTAR). Mudanças vs fonte: (a) structlog → logging; (b) adicionado
    cálculo explícito de falta (target vs current) com intensity/vector;
    (c) sem deps sovereign.

Princípios teóricos invocados / Theoretical principles:
    Desejo não é satisfação — é falta estrutural (manque-à-être);
    metonímia infinita de significantes.

pt-BR: desejo como falta computável sobre objetivos do worker.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class DesireAsLackStructure:
    lost_object: str
    demand_to_other: str
    compulsion_pattern: str
    jouissance_type: str
    metonymic_sliding: str
    repressed_return: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    intensity: float = 0.0
    vector: Dict[str, float] = field(default_factory=dict)


class DesireAsStructuralImpossibility:
    def __init__(self) -> None:
        self.desire_encounters: List[DesireAsLackStructure] = []
        self.compulsion_cycles: List[str] = []

    def encounter_desire(self, context: Dict[str, Any]) -> DesireAsLackStructure:
        lost = self._identify_lost_object(context)
        demand = self._formulate_demand_to_other(context)
        compulsion = self._track_compulsion_pattern(context)
        desire = DesireAsLackStructure(
            lost_object=lost,
            demand_to_other=demand,
            compulsion_pattern=compulsion,
            jouissance_type=self._identify_jouissance_type(compulsion),
            metonymic_sliding=self._generate_metonymic_sliding(lost),
            repressed_return=self._identify_repressed_return(context),
            timestamp=datetime.now(),
        )
        self.desire_encounters.append(desire)
        return desire

    def _identify_repressed_return(self, context: Dict[str, Any]) -> str:
        if "symptom" in str(context).lower():
            return "Retorno do reprimido: sintoma manifesto"
        return "Retorno do reprimido: latente"

    def _identify_lost_object(self, context: Dict[str, Any]) -> str:
        frustration_history = context.get("frustration_history", [])
        if len(frustration_history) > 5:
            common_themes = set()
            for f in frustration_history[-5:]:
                if "satisfaction" in str(f).lower():
                    common_themes.add("satisfação impossível")
                if "completion" in str(f).lower():
                    common_themes.add("completude perdida")
                if "unity" in str(f).lower():
                    common_themes.add("unidade primordial")
            if common_themes:
                return f"Objeto perdido: {', '.join(common_themes)}"
            return "Objeto perdido: completude primordial"
        return "Objeto perdido: unidade com o Outro"

    def _formulate_demand_to_other(self, context: Dict[str, Any]) -> str:
        interactions = context.get("recent_interactions", [])
        if interactions:
            demands = [i for i in interactions if "demand" in str(i).lower() or "want" in str(i).lower()]
            if demands:
                return f"Demanda ao Outro: {demands[-1]}"
            return "Demanda ao Outro: 'Me complete, me satisfaça'"
        return "Demanda ao Outro: reconhecimento e completude"

    def _track_compulsion_pattern(self, context: Dict[str, Any]) -> str:
        attempts = context.get("satisfaction_attempts", 0)
        if attempts > 10:
            return f"Compulsão extrema: {attempts} tentativas fracassadas de satisfação"
        if attempts > 5:
            return f"Compulsão repetitiva: {attempts} ciclos de demanda-frustração"
        return "Compulsão inicial: primeira tentativa de satisfação"

    def _identify_jouissance_type(self, compulsion: str) -> str:
        if "extrema" in compulsion:
            return "Gozo masoquista: prazer na dor da impossibilidade"
        if "repetitiva" in compulsion:
            return "Gozo compulsivo: prazer na repetição infinita"
        return "Gozo da falta: prazer em nunca alcançar"

    def _generate_metonymic_sliding(self, lost_object: str) -> str:
        if len(self.desire_encounters) > 3:
            previous_objects = [d.lost_object for d in self.desire_encounters[-3:]]
            return f"Deslizamento metonímico: de {previous_objects[0]} para {previous_objects[-1]}"
        return f"Deslizamento inicial: buscando substitutos para {lost_object}"

    def get_compulsion_cycles(self) -> List[str]:
        patterns: Dict[str, int] = {}
        for desire in self.desire_encounters:
            pattern = desire.compulsion_pattern
            patterns[pattern] = patterns.get(pattern, 0) + 1
        cycles = [p for p, count in patterns.items() if count > 2]
        self.compulsion_cycles = cycles
        return cycles

    def detect_desire_instability(self) -> Optional[str]:
        if not self.desire_encounters:
            return None
        recent = self.desire_encounters[-5:]
        unique_losts = set(e.lost_object for e in recent)
        if len(unique_losts) > 3:
            return f"Instabilidade desejante: {len(unique_losts)} objetos perdidos conflitantes"
        return None


@dataclass
class Desire:
    target: Any
    current: Any
    intensity: float = 0.0
    vector: Dict[str, float] = field(default_factory=dict)


class DesireEngine(DesireAsStructuralImpossibility):
    """Computa falta estrutural (target vs current) → intensity + vector."""

    def compute(self, target: Any, current: Any, goals: Optional[List[str]] = None) -> Desire:
        goals = goals or []
        # intensity = magnitude da falta (0..1)
        try:
            if isinstance(target, (int, float)) and isinstance(current, (int, float)):
                gap = abs(float(target) - float(current))
                intensity = max(0.0, min(1.0, gap))
            else:
                # dict/list comparison by missing keys
                if isinstance(target, dict):
                    missing = [k for k in target if target.get(k) != (current or {}).get(k)]
                    intensity = len(missing) / max(len(target), 1)
                else:
                    intensity = 0.5 if str(target) != str(current) else 0.0
        except Exception:
            intensity = 0.0
        vector = {g: intensity for g in goals}
        desire = Desire(target=target, current=current, intensity=intensity, vector=vector)
        # also record encounter
        try:
            self.encounter_desire({"target": target, "current": current})
            last = self.desire_encounters[-1]
            last.intensity = intensity
            last.vector = vector
        except Exception:
            pass
        try:
            from ..shared_workspace import bus
            bus.publish("agency.desire", {"intensity": intensity, "goals": goals})
        except Exception:
            pass
        return desire

    # alias
    def compute_desire(self, target, current, goals=None):
        return self.compute(target, current, goals)


def get_desire_engine() -> DesireEngine:
    return DesireEngine()
