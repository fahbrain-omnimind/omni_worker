"""agency.ewc — Elastic Weight Consolidation port (OW-STU-012).

Orquestração runtime / Runtime orchestration:
Port de `src/learning/ewc.py` do sovereign (port classificado PORT em
OW-STU-012). Mantém pesos de agentes estáveis entre tarefas: a Fisher
Information é aproximada pela contribuição de cada agente em decisões
bem-sucedidas de alta confiança, e mudanças propostas são amortecidas
proporcionalmente à importância histórica. Puro stdlib — sem torch.

Arquitetura / Architecture:
Sem rede neural real no worker (Gemma vive no brain server) — o EWC aqui
age sobre os PESOS DE AGENTES (agency: trust/prioridade por agente), o
mesmo uso que o sovereign faz para ICAC. `penalty_loss` e
`adjust_weights_with_protection` compõem com o feedback_loop e os juízes.

Princípios teóricos invocados / Theoretical principles:
EWC (Kirkpatrick et al. 2017) — penalidade quadrática ponderada pela
importância (Fisher) evita esquecimento catastrófico entre tarefas.
Aplicação aqui é informacional/operacional (pesos de governança), não
treino de rede.

pt-BR: EWC portado — estabilidade de pesos de agentes entre tarefas.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ElasticWeightConsolidation:
    """Elastic Weight Consolidation over agent weights.

    English: Maintains an approximate Fisher Information per weight
    (agent) from decision history and damps proposed changes to
    important weights.
    pt-BR: Mantém Fisher aproximada por peso (agente) a partir do
    histórico de decisões e amortece mudanças em pesos importantes.
    """

    def __init__(self, lambda_ewc: float = 0.4, prior_strength: float = 0.05):
        self.lambda_ewc = float(lambda_ewc)
        self.prior_strength = max(0.0, float(prior_strength))
        self.fisher_matrix: dict[str, float] = {}
        self.optimal_weights: dict[str, float] = {}

    def compute_fisher_information(
        self, agent_weights: dict[str, float],
        audit_history: list[dict[str, Any]] | None = None,
    ) -> None:
        """Approximate Fisher importance from decision history.

        English: High-confidence successful decisions raise the Fisher
        value of contributing agents; failed decisions count at 25%.
        pt-BR: Decisões bem-sucedidas de alta confiança elevam a Fisher
        dos agentes contribuintes; falhas contam a 25%.
        """
        self.optimal_weights = dict(agent_weights)
        base = (self.prior_strength / max(1, len(agent_weights))
                if self.prior_strength > 0 else 0.0)
        self.fisher_matrix = {k: base for k in agent_weights}

        for event in (audit_history or []):
            if event.get("type") != "decision":
                continue
            confidence = float(event.get("confidence", 0.5))
            is_success = bool(event.get("success", False))
            agents = event.get("contributing_agents") or []
            weight = confidence if is_success else confidence * 0.25
            if agents:
                for name in agents:
                    if name in self.fisher_matrix:
                        self.fisher_matrix[name] += weight
            elif self.fisher_matrix:
                diluted = weight / len(self.fisher_matrix)
                for name in self.fisher_matrix:
                    self.fisher_matrix[name] += diluted

        total = sum(self.fisher_matrix.values())
        if total <= 0:
            uniform = 1.0 / max(1, len(self.fisher_matrix))
            for k in self.fisher_matrix:
                self.fisher_matrix[k] = uniform
        else:
            for k in self.fisher_matrix:
                self.fisher_matrix[k] /= total

    def penalty_loss(self, new_weights: dict[str, float]) -> float:
        """EWC penalty: (lambda/2) * sum(F_i * (theta_i - theta_i*)^2)."""
        loss = 0.0
        for name, new_w in new_weights.items():
            if name in self.optimal_weights and name in self.fisher_matrix:
                old_w = self.optimal_weights[name]
                loss += self.fisher_matrix[name] * (new_w - old_w) ** 2
        return (self.lambda_ewc / 2.0) * loss

    def adjust_weights_with_protection(
        self, current_weights: dict[str, float],
        proposed_changes: dict[str, float],
    ) -> dict[str, float]:
        """Apply deltas damped by Fisher importance, bounds [0,1]."""
        new_weights = dict(current_weights)
        for name, delta in proposed_changes.items():
            if name not in new_weights:
                continue
            importance = self.fisher_matrix.get(name, 0.0)
            resistance = 1.0 + (importance * self.lambda_ewc * 10.0)
            new_weights[name] = max(0.0, min(1.0,
                                             new_weights[name] + delta / resistance))
        return new_weights