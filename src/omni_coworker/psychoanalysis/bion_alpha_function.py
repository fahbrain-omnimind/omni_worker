"""bion_alpha_function — função α Bion (β→α) para o worker.

Orquestração runtime / Runtime orchestration:
    `BionAlphaFunction.transform(beta)` metaboliza β→α via symbolizer,
    com cadeia de fallback LLM→MiniLM→heurístico. Sem efeitos colaterais
    além de logging e history em memória.

Arquitetura / Architecture:
    Port de src/psychoanalysis/bion_alpha_function.py (sovereign,
    OW-STU-008b: ADAPTAR). Diferenças vs original:
    - LLM → omni_coworker.agents._llm.brain_chat(role='executor') via
      bion_symbolizer (sem endpoints fixos, sem Erika, sem torch);
    - NeutrosophicLogic → fallback inline (entropy_factor=1.0);
    - imports locais alpha_element/beta_element.

Princípios teóricos invocados / Theoretical principles:
    Função alpha transforma β-elements (brutos) em α-elements (pensáveis)
    (Bion, 1962; 1963; 1970).

pt-BR: função alpha Bioniana adaptada ao worker (CPU/RAM).
"""

from __future__ import annotations

import logging
import os
from collections.abc import Callable
from datetime import datetime
from typing import Any

import numpy as np

from .alpha_element import AlphaElement
from .beta_element import BetaElement
from .bion_symbolizer import BionAsyncSymbolizer

logger = logging.getLogger(__name__)


def _default_llm_symbolize(raw_data: Any, emotional_charge: float = 0.0) -> str | None:
    try:
        timeout = float(os.environ.get("OMNI_WORKER_BION_SYMBOL_TIMEOUT", "2.0"))
        symbolizer = BionAsyncSymbolizer()
        return symbolizer.symbolize(raw_data=raw_data, emotional_charge=emotional_charge, timeout=timeout)
    except Exception as e:  # noqa: BLE001
        logger.debug("Bion symbolize falhou: %s", e)
        return str(raw_data)


class BionAlphaFunction:
    def __init__(
        self,
        transformation_rate: float = 0.7,
        tolerance_threshold: float = 0.6,
        narrative_builder: Callable[[BetaElement], str] | None = None,
        use_llm_symbolizer: bool = True,
    ) -> None:
        if not 0.0 <= transformation_rate <= 1.0:
            raise ValueError("transformation_rate deve estar entre 0.0 e 1.0")
        if not 0.0 <= tolerance_threshold <= 1.0:
            raise ValueError("tolerance_threshold deve estar entre 0.0 e 1.0")
        self.transformation_rate = transformation_rate
        self.tolerance_threshold = tolerance_threshold
        self.narrative_builder = narrative_builder or self._default_narrative_builder
        self.use_llm_symbolizer = use_llm_symbolizer
        self.processing_history: list[dict[str, Any]] = []
        logger.info(f"BionAlphaFunction inicializada: rate={transformation_rate:.2f}, tolerance={tolerance_threshold:.2f}")

    def transform(self, beta: BetaElement) -> AlphaElement | None:
        if not self._is_processable(beta):
            logger.warning(f"BetaElement não-processável: emotional_charge={beta.emotional_charge:.2f}")
            self._record_failure(beta, reason="too_intense")
            return None
        try:
            alpha = self._apply_transformation(beta)
            self._record_success(beta, alpha)
            return alpha
        except Exception as e:  # noqa: BLE001
            logger.error(f"Erro na transformação: {e}")
            self._record_failure(beta, reason=f"error: {e!s}")
            return None

    def transform_batch(self, betas: list[BetaElement]) -> list[AlphaElement]:
        alphas = []
        for beta in betas:
            alpha = self.transform(beta)
            if alpha is not None:
                alphas.append(alpha)
        return alphas

    def _is_processable(self, beta: BetaElement) -> bool:
        if beta.is_traumatic(threshold=self.tolerance_threshold):
            return self.transformation_rate > 0.9
        return True

    def _apply_transformation(self, beta: BetaElement) -> AlphaElement:
        content = self._symbolize_content(beta.raw_data, beta.emotional_charge)
        if self.narrative_builder == self._default_narrative_builder:
            narrative = content
        else:
            narrative = self.narrative_builder(beta)
        symbolic_potential = self._compute_symbolic_potential(beta)
        alpha = AlphaElement(
            content=content,
            origin_beta=beta,
            timestamp=datetime.now(),
            narrative_form=narrative,
            symbolic_potential=symbolic_potential,
        )
        return alpha

    def _compute_symbolic_potential(self, beta: BetaElement) -> float:
        entropy_factor = 1.0
        if getattr(beta, "neutrosophic_triplet", None) is not None:
            try:
                nt = beta.neutrosophic_triplet
                # sarannya entropy approx: I + |T-F| normalized
                entropy = (nt.I + abs(nt.T - nt.F)) / 2.0
                entropy_factor = max(0.01, 1.0 - entropy)
            except Exception:  # noqa: BLE001
                entropy_factor = 1.0

        base = self.transformation_rate * entropy_factor
        emotional_penalty = beta.emotional_charge * 0.3
        source_bonus = 0.1 if beta.source != "unknown" else 0.0

        content_variation = 0.0
        if isinstance(beta.raw_data, (list, tuple)) and len(beta.raw_data) > 0:
            try:
                data_array = np.array(beta.raw_data, dtype=float)
                if len(data_array) > 1:
                    std_dev = np.std(data_array)
                    mean_abs = np.mean(np.abs(data_array))
                    cv = std_dev / (mean_abs + 1e-8) if mean_abs > 1e-8 else 0.0
                    skewness = np.mean(((data_array - np.mean(data_array)) / (std_dev + 1e-8)) ** 3)
                    skewness_normalized = np.tanh(np.abs(skewness)) * 0.05
                    hash_input = str(data_array[:10].tolist()) + str(data_array[-10:].tolist()) + str(round(float(np.mean(data_array)), 6)) + str(round(float(std_dev), 6))
                    content_hash = hash(hash_input) % 1000
                    hash_variation = (content_hash / 1000.0) * 0.08
                    content_variation = (cv * 0.05) + skewness_normalized + hash_variation
                    content_variation = min(0.15, content_variation)
            except (ValueError, TypeError):
                content_hash = hash(str(beta.raw_data)) % 1000
                content_variation = (content_hash / 1000.0) * 0.1
        elif isinstance(beta.raw_data, str):
            content_hash = hash(beta.raw_data) % 1000
            length_factor = min(1.0, len(beta.raw_data) / 100.0)
            content_variation = (content_hash / 1000.0) * 0.1 * length_factor
        else:
            content_hash = hash(str(beta.raw_data)) % 1000
            content_variation = (content_hash / 1000.0) * 0.05

        history_factor = 0.0
        if len(self.processing_history) > 0:
            recent_history = self.processing_history[-10:]
            if len(recent_history) > 1:
                recent_potentials = [h.get("alpha_potential", 0.0) for h in recent_history if h.get("status") == "success" and "alpha_potential" in h]
                if len(recent_potentials) > 1:
                    history_std = float(np.std(recent_potentials))
                    history_factor = min(0.05, history_std * 2.0)

        symbolic_potential = base - emotional_penalty + source_bonus + content_variation + history_factor
        return max(0.0, min(1.0, symbolic_potential))

    def _symbolize_content(self, raw_data: Any, emotional_charge: float = 0.0) -> str:
        if self.use_llm_symbolizer:
            llm_result = _default_llm_symbolize(raw_data, emotional_charge)
            if llm_result:
                return llm_result
        return str(raw_data)

    def _default_narrative_builder(self, beta: BetaElement) -> str:
        return f"Experiência de {beta.source} em {beta.timestamp.isoformat()}"

    def _record_success(self, beta: BetaElement, alpha: AlphaElement) -> None:
        self.processing_history.append({"timestamp": datetime.now().isoformat(), "status": "success", "beta_charge": beta.emotional_charge, "alpha_potential": alpha.symbolic_potential})

    def _record_failure(self, beta: BetaElement, reason: str) -> None:
        self.processing_history.append({"timestamp": datetime.now().isoformat(), "status": "failure", "beta_charge": beta.emotional_charge, "reason": reason})

    def get_statistics(self) -> dict[str, Any]:
        total = len(self.processing_history)
        if total == 0:
            return {"total_processed": 0, "success_rate": 0.0, "failure_rate": 0.0}
        successes = sum(1 for entry in self.processing_history if entry["status"] == "success")
        failures = total - successes
        return {"total_processed": total, "successes": successes, "failures": failures, "success_rate": successes / total, "failure_rate": failures / total, "current_transformation_rate": self.transformation_rate}
