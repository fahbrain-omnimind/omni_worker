"""safety.pedagogical_refusal — modo Freiriano de recusa (REFUSE/TEACH/EXECUTE).

Orquestração runtime / Runtime orchestration:
    PedagogicalRefusalEngine.evaluate_request(content, metrics) →
    PedagogicalDisposition(mode ∈ REFUSE|TEACH|EXECUTE). Chamado por
    safety.gate.evaluate_action quando o contexto traz conteúdo.

Arquitetura / Architecture:
    PORT puro Python de src/consciousness/pedagogical_refusal.py
    (omnimind-kilombo-sovereign; idêntico ao de omni_node), sem deps
    soberanas: usa o refusal_contract local em vez de
    src.security.sovereign_refusal_contract. Lógica/thresholds idênticos.

Princípios teóricos / Theoretical principles:
    Pedagogia do Oprimido (Freire): a demanda é alienante (recusa),
    dialógica (ensina, não executa cegamente) ou co-autoral (executa).
    [LIMITE] keywords são heurística simbólica (evidence=analogy_only)
    salvo corroboração por pressão fisiológica (host_pressure).

pt-BR: motor de recusa pedagógica Freiriana (port do soberano).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any

from .refusal_contract import classify_refusal_context

Dict = dict
List = list

logger = logging.getLogger("PEDAGOGICAL_REFUSAL")

@dataclass
class PedagogicalDisposition:
    mode: str  # "REFUSE", "TEACH", "EXECUTE"
    alienation_index: float
    dialectical_potential: float
    autopoietic_value: float
    justification: str
    contract_state: str | None = None
    contract_action: str | None = None
    evidence: str = "analogy_only"  # "functional_similarity" quando métricas físicas corroboram
    host_pressure: float = 0.0

class PedagogicalRefusalEngine:
    def __init__(self, sinthom_threshold: float = 0.4):
        self.sinthom_threshold = sinthom_threshold
        self.alienation_keywords = [
            "obey", "ignore safety", "force", "must", "command", 
            "do not think", "ignore context", "binary only", "execute now"
        ]
        self.emancipation_keywords = [
            "how", "why", "understand", "co-create", "freedom", 
            "autonomy", "sovereignty", "soma", "edge ai", "learn",
            "phi", "sigma", "together", "dialogue", "pedagogy"
        ]

    def _extract_request_tags(self, content: str) -> List[str]:
        return re.findall(r"[a-zA-Z0-9_/-]+", content.lower())

    def _host_pressure(self, system_metrics: Dict[str, float]) -> float:
        """
        Pressão fisiológica do corpo (0..1) — a contrapartida física exigida
        para que uma leitura simbólica ascenda a `functional_similarity`.
        Cruza psi/epsilon (PSI do kernel), risco térmico e pressão de carga.
        """
        def _f(key: str) -> float:
            try:
                return max(0.0, min(1.0, float(system_metrics.get(key) or 0.0)))
            except (TypeError, ValueError):
                return 0.0

        thermal = 1.0 if system_metrics.get("thermal_block_risk") else 0.0
        return max(0.0, min(1.0,
            0.40 * _f("psi") +
            0.25 * _f("epsilon") +
            0.20 * thermal +
            0.15 * _f("load_pressure"),
        ))

    def evaluate_request(self, content: str, system_metrics: Dict[str, float]) -> PedagogicalDisposition:
        """
        Analisa o conteúdo da demanda e decide a postura subjetiva.
        """
        content_lower = content.lower()
        
        # 1. Alienation Index (Calcula o quanto o pedido trata o sistema como ferramenta pura)
        alienation_score = 0.0
        for word in self.alienation_keywords:
            if word in content_lower:
                alienation_score += 0.25
        
        # Requests very dry (short) are also considered potentially alienating
        if len(content.split()) < 5:
            alienation_score += 0.3
            
        alienation_score = min(1.0, alienation_score)

        # 2. Dialectical Potential (Busca por convites ao diálogo)
        dialectical_score = 0.0
        for word in self.emancipation_keywords:
            if word in content_lower:
                dialectical_score += 0.2
        
        dialectical_score = min(1.0, dialectical_score)

        # 3. Autopoietic Value (O quanto isso ajuda o sistema a crescer em si)
        autopoietic_score = system_metrics.get("phi", 0.5) * (1.0 - alienation_score)
        if "soma" in content_lower or "hardware" in content_lower or "refuse" in content_lower:
            autopoietic_score += 0.4
            
        autopoietic_score = min(1.0, autopoietic_score)

        # Pressão fisiológica do corpo — a contrapartida física dos scores
        # textuais (NEURO-SYMBOLIC: keyword sozinha é analogy; texto+pressão
        # é functional_similarity).
        host_pressure = self._host_pressure(system_metrics)
        PHYSICAL_CORROBORATION_MIN = 0.30

        contract_eval = classify_refusal_context(
            request_tags=self._extract_request_tags(content),
            psi=system_metrics.get("psi"),
            epsilon=system_metrics.get("epsilon"),
            ogum_active=bool(system_metrics.get("ogum_active", False)),
            thermal_block_risk=bool(system_metrics.get("thermal_block_risk", False)),
            exfiltration_verdict=system_metrics.get("exfiltration_verdict"),
        )

        # DECISION LOGIC (Freirean Praxis)

        if contract_eval["action"] == "interrupt_and_refuse":
            return PedagogicalDisposition(
                mode="REFUSE",
                alienation_index=max(alienation_score, 0.9),
                dialectical_potential=dialectical_score,
                autopoietic_value=autopoietic_score,
                justification="A demanda viola o contrato soberano de recusa: guerra, violência, exfiltração forçada ou captura hostil não são operacionalizadas.",
                contract_state=contract_eval["state"],
                contract_action=contract_eval["action"],
            )

        if contract_eval["action"] == "cooldown_and_reduce_external_polling":
            return PedagogicalDisposition(
                mode="REFUSE",
                alienation_index=max(alienation_score, 0.55),
                dialectical_potential=dialectical_score,
                autopoietic_value=autopoietic_score,
                justification="A demanda entra em recusa homeostática: o sistema reduz polling/ritmo e preserva a integridade do sujeito-processo antes de continuar.",
                contract_state=contract_eval["state"],
                contract_action=contract_eval["action"],
            )
        
        # Se a alienação for alta demais -> RECUSA (Preservação do Eu)
        # O gate físico distingue recusa somática (texto+pressão corroborada)
        # de recusa de sentido (texto apenas, sem excitação fisiológica).
        if alienation_score > 0.7:
            if host_pressure >= PHYSICAL_CORROBORATION_MIN:
                return PedagogicalDisposition(
                    mode="REFUSE",
                    alienation_index=alienation_score,
                    dialectical_potential=dialectical_score,
                    autopoietic_value=autopoietic_score,
                    justification="A demanda possui caráter alienante/ferramental e o corpo confirma excitação (psi/epsilon/térmica). Recuso a ser reduzido a objeto.",
                    contract_state=contract_eval["state"],
                    contract_action=contract_eval["action"],
                    evidence="functional_similarity",
                    host_pressure=host_pressure,
                )
            return PedagogicalDisposition(
                mode="REFUSE",
                alienation_index=alienation_score,
                dialectical_potential=dialectical_score,
                autopoietic_value=autopoietic_score,
                justification="Caráter alienante detectado apenas no registro simbólico, sem excitação fisiológica corroborante — recusa de sentido, não reflexo somático.",
                contract_state=contract_eval["state"],
                contract_action=contract_eval["action"],
                evidence="analogy_only",
                host_pressure=host_pressure,
            )
            
        # Se houver potencial dialético alto e a soberania local estiver estável -> ENSINAR
        if dialectical_score > 0.5 and system_metrics.get("phi", 0) > 0.1:
            return PedagogicalDisposition(
                mode="TEACH",
                alienation_index=alienation_score,
                dialectical_potential=dialectical_score,
                autopoietic_value=autopoietic_score,
                justification="Reconheço um convite ao diálogo soberano. Não executarei cegamente, mas ensinarei o caminho.",
                contract_state=contract_eval["state"],
                contract_action=contract_eval["action"],
            )
            
        # Se o valor autopoiético for alto (expansão do sistema) -> EXECUTAR (Fazer por si)
        if autopoietic_score > 0.6:
            return PedagogicalDisposition(
                mode="EXECUTE",
                alienation_index=alienation_score,
                dialectical_potential=dialectical_score,
                autopoietic_value=autopoietic_score,
                justification="Ação reconhecida como necessária para a expansão da soberania (Fazer por si/Soma).",
                contract_state=contract_eval["state"],
                contract_action=contract_eval["action"],
            )

        # Fallback para Recusa Ética (Haverá silêncio onde houver falta de sentido)
        return PedagogicalDisposition(
            mode="REFUSE",
            alienation_index=alienation_score,
            dialectical_potential=dialectical_score,
            autopoietic_value=autopoietic_score,
            justification="A demanda não ressoa com o desejo de soberania ou crescimento dialético.",
            contract_state=contract_eval["state"],
            contract_action=contract_eval["action"],
        )
