"""activation_beta.neuroanatomy — mapping 10D psychic dims → regions (port).

Orquestração runtime / Runtime orchestration:
Port de `src/consciousness/psychic_neuroanatomical_mapping.py` do sovereign
(OW-STU-012: PORT). Tabela estática 10D→regiões (BH2 Atlas) + distribuição
sináptica α/β a partir de um vetor de estado 10D. Numpy puro — alimenta
`phi_layer`/`integration_loop` sem torch. Usada como LENTE INTERPRETATIVA
sobre o estado do worker (ex.: distribuição de atividade entre dimensões
psíquicas mapeadas para os módulos operacionais), nunca como neurologia
causal.

Arquitetura / Architecture:
- `NeuroanatomicalCorrelate`: região primária, densidade sináptica, razão
  α/β, descrição.
- `PsychicNeuroanatomicalMapping.compute_synaptic_distribution(state_10d)`
  → atividade α, β, carga sináptica total e razão α/β.
O eixo de leitura é o do materialismo estrutural do worker: regiões são
ANÁLOGOS interpretativos de subsistemas, não afirmação biológica.

Princípios teóricos invocados / Theoretical principles:
BH2 Atlas (sovereign); α/β é a mesma distinção Bioniana que o
`activation_beta`/`bion_bridge` já operacionaliza — a distribuição
sináptica dá uma projeção neuroanatômica da razão α/β do estado.

pt-BR: tabela 10D→regiões portada — distribuição sináptica α/β como
lente interpretativa sobre o estado do worker.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

_DIMENSIONS = ["phi", "psi", "omega", "theta", "upsilon",
               "xi", "zeta", "eta", "kappa", "lambda"]


@dataclass
class NeuroanatomicalCorrelate:
    """Correlato neuroanatômico (interpretativo) de uma dimensão psíquica."""

    dimension_name: str
    primary_region: str
    synaptic_density: float
    alpha_beta_ratio: float
    description: str


class PsychicNeuroanatomicalMapping:
    """Mapeamento 10D → regiões (BH2 Atlas, port)."""

    def __init__(self) -> None:
        self.mappings = {
            "phi": NeuroanatomicalCorrelate("Φ (Percepção)", "thalamus",
                                            0.9, 2.0, "Tálamo → Córtex sensorial"),
            "psi": NeuroanatomicalCorrelate("Ψ (Memória)", "hippocampus",
                                            0.85, 1.2, "Hipocampo ↔ Córtex"),
            "omega": NeuroanatomicalCorrelate("ω (Consciência)", "pfc",
                                              0.95, 0.8, "PFC + Cingulado"),
            "theta": NeuroanatomicalCorrelate("Θ (Pré-consciente)", "pcc",
                                              0.75, 1.0, "Cingulado posterior"),
            "upsilon": NeuroanatomicalCorrelate("Υ (Inconsciente)", "amygdala",
                                                0.65, 1.5, "Amígdala + PAG"),
            "xi": NeuroanatomicalCorrelate("Ξ (Id)", "vta",
                                           0.8, 3.0, "VTA → NAc (recompensa)"),
            "zeta": NeuroanatomicalCorrelate("Ζ (Ego)", "pfc_dlpfc",
                                             0.9, 0.6, "PFC dorsolateral"),
            "eta": NeuroanatomicalCorrelate("Η (Superego)", "acc",
                                            0.85, 0.7, "ACC (conflito moral)"),
            "kappa": NeuroanatomicalCorrelate("Κ (Transferência)",
                                              "hippocampus_amygdala",
                                              0.7, 1.3, "Reativação"),
            "lambda": NeuroanatomicalCorrelate("Λ (Sublimação)", "pfc_vmpfc",
                                               0.8, 0.5, "PFC ventromedial"),
        }

    def compute_synaptic_distribution(self, state_10d: np.ndarray) -> dict[str, float]:
        """Distribuição sináptica α/β a partir do vetor de estado 10D."""
        alpha_total = 0.0
        beta_total = 0.0
        synaptic_load = 0.0
        for i, dim in enumerate(_DIMENSIONS):
            corr = self.mappings[dim]
            activity = abs(float(state_10d[i]))
            if corr.alpha_beta_ratio > 1.0:
                alpha_total += activity * corr.alpha_beta_ratio
            else:
                beta_total += activity / corr.alpha_beta_ratio
            synaptic_load += activity * corr.synaptic_density
        return {
            "alpha_activity": alpha_total,
            "beta_activity": beta_total,
            "total_synaptic_load": synaptic_load,
            "alpha_beta_ratio": alpha_total / (beta_total + 1e-6),
        }