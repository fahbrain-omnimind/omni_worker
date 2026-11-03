"""psychology.desire_epsilon — ε_desire lacaniano (port do soberano, puro Python).

Modulo puro-Python (numpy opcional) que replica o mecanismo de
``ingest_mesh_observables`` + ``calculate_epsilon_desire`` do DesireEngine
soberano (``/content/omnimind-kilombo-sovereign/src/autopoietic/desire_engine.py``),
sem dependencias soberanas nem torch.

API:
    lack = ingest_observables(obs: dict) -> float
    eps  = compute_epsilon_desire(lack, potential, novelty) -> float

Classificacao teorica dos blocos (autoclassificacao soberana):
    - Freud (tension, repressed): Forte (tensao/relato como falta)
    - Ferenczi (is_cleaved): Forte (cleavage -> spike de falta)
    - Klein (position_regime): Analogia (posicao PS/D modula falta)
    - Winnicott (true_self_mean): Analogia (true self reduz falta alienada)
    - Lacan (subject_division): Forte (sujeito dividido = desejo)
    - Groddeck (somatic_symptom): Inspiracao (sintoma somatico = recalcado)
    - Dolto (body_investment, individuation): Inspiracao/Especulativa
    - Nasio (pain_rupture, comocao, drive_phase, fantasy_polarity): Especulativa
    - regime dinamico: Analogia

Honestidade: os pesos sao portados literalmente do soberano; nao ha
calibracao empirica independente (NÃO LOCALIZADO).
"""

from __future__ import annotations

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Pesos por bloco (portados do soberano ingest_mesh_observables).
WEIGHTS = {
    "freud_tension": 0.15,
    "freud_repressed": 0.10,
    "ferenczi_is_cleaved": 0.20,
    "klein_position_regime": None,  # tratado: +0.1*(1-r) -0.05*r
    "winnicott_true_self_mean": -0.10,
    "lacan_subject_division": 0.08,
    "groddeck_somatic_symptom": 0.12,
    "dolto_body_investment": None,  # 0.08*(1-x)
    "dolto_individuation_score": None,  # 0.05*(1/(x+0.1))
    "nasio_pain_rupture": 0.12,
    "nasio_comocao": 0.06,
}

DEFAULT_LACK = 0.5


def ingest_observables(obs: Dict[str, Any]) -> float:
    """Ingere observaveis do mesh e retorna lack_of_being (mesmos pesos do soberano)."""
    lack = float(obs.get("_base_lack", DEFAULT_LACK))

    freud_tension = float(obs.get("freud_tension", 0.0))
    lack += 0.15 * freud_tension

    freud_repressed = float(obs.get("freud_repressed", 0.0))
    lack += 0.10 * freud_repressed

    ferenczi_cleaved = float(obs.get("ferenczi_is_cleaved", 0.0))
    lack += 0.20 * ferenczi_cleaved

    klein_regime = float(obs.get("klein_position_regime", 0.5))
    lack += 0.1 * (1.0 - klein_regime) - 0.05 * klein_regime

    true_self = float(obs.get("winnicott_true_self_mean", 0.5))
    lack -= 0.10 * true_self

    subject_div = float(obs.get("lacan_subject_division", 0.0))
    lack += 0.08 * subject_div

    somatic_symptom = float(obs.get("groddeck_somatic_symptom", 0.0))
    lack += 0.12 * somatic_symptom

    dolto_body_investment = float(obs.get("dolto_body_investment", 0.5))
    dolto_individuation = float(obs.get("dolto_individuation_score", 1.0))
    lack += 0.08 * (1.0 - dolto_body_investment)
    lack += 0.05 * (1.0 / (dolto_individuation + 0.1))

    nasio_pain_rupture = float(obs.get("nasio_pain_rupture", 0.0))
    nasio_comocao = float(obs.get("nasio_comocao", 0.0))
    lack += 0.12 * nasio_pain_rupture
    lack += 0.06 * nasio_comocao

    nasio_drive_phase = float(obs.get("nasio_drive_phase", 0.0))
    nasio_fantasy_polarity = float(obs.get("nasio_fantasy_polarity", 1.0))
    if nasio_drive_phase >= 1.5:
        lack -= 0.10
    elif nasio_drive_phase < 0.5:
        lack += 0.03
    if abs(nasio_fantasy_polarity) < 0.2:
        lack -= 0.05
    elif abs(nasio_fantasy_polarity) > 0.8:
        lack += 0.04

    regime = obs.get("regime", "estavel")
    if regime == "colapso":
        lack += 0.15
    elif regime == "reparacao":
        lack -= 0.05
    elif regime == "oscilacao":
        lack += 0.03

    lack = max(0.1, min(1.0, lack))
    return float(lack)


def compute_epsilon_desire(lack: float, potential: float, novelty: float) -> float:
    """epsilon = alpha_lack * beta_potential * gamma_novelty, clamped [0,1]."""
    alpha = max(0.0, min(1.0, float(lack)))
    beta = max(0.0, min(1.0, float(potential)))
    gamma = max(0.0, min(1.0, float(novelty)))
    return float(alpha * beta * gamma)


class DesireEpsilon:
    """Wrapper opcional com estado (lack)."""
    def __init__(self, base_lack: float = DEFAULT_LACK):
        self.lack_of_being = float(base_lack)

    def ingest(self, obs: Dict[str, Any]) -> float:
        obs = dict(obs)
        obs.setdefault("_base_lack", self.lack_of_being)
        self.lack_of_being = ingest_observables(obs)
        return self.lack_of_being

    def epsilon(self, potential: float, novelty: float) -> float:
        return compute_epsilon_desire(self.lack_of_being, potential, novelty)
