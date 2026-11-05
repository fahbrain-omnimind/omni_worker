"""psychoanalysis.bion_patches — patches container-contained (Bion).

Orquestração runtime / Runtime orchestration:
    `BionContainerPatch` envolve uma função alpha (qualquer objeto com
    `transform`) e adiciona contenção elética: expande capacidade por
    razão áurea quando a intensidade do β-element pressiona, explode
    (realinha escala) apenas em desequilíbrio absoluto (intensidade >
    5× capacidade) e oferece degraded reverie (metabolização parcial,
    potencial reduzido) quando a função alpha rejeita o elemento — evitando
    a evacuação traumática. Sem estado persistente; falha-open se a função
    alpha estiver ausente.

Arquitetura / Architecture:
    Port de src/psychoanalysis/bion_patches/container_contained.py
    (sovereign, OW-STU-008b: PORTAR). Diferenças vs fonte:
    - `BionAlphaFunction` não está neste escopo: o container opera por
      duck typing sobre `transform` (fallbacks para `_symbolize_content`
      e `narrative_builder`);
    - sem `print` (usa `logging`) e sem deps externas além de stdlib.

Princípios teóricos invocados / Theoretical principles:
    Contenção container-contained (Bion): o container processa e
    transforma o contained; a reverie do analista segura o elemento
    rejeitado pela função alpha parcialmente, em vez de evacuá-lo.

pt-BR: contenção elástica com degraded reverie para β-elementos intensos.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from ..alpha_element import AlphaElement
from ..beta_element import BetaElement

logger = logging.getLogger(__name__)


class BionContainerPatch:
    """
    Patch para Container-Contained (♀♂).

    Wraps uma função alpha existente (duck typing sobre `transform`) sem
    modificá-la. Adiciona capacidade de contenção elética e sistema de
    realinhamento de escala ("explosão") com degraded reverie.
    """

    def __init__(
        self,
        alpha_function: Any,
        initial_capacity: float = 10.0,
        explosion_threshold: float = 8.0,
        recovery_rate: float = 1.0,
        tolerance_expansion_threshold: float = 0.50,
    ):
        """
        Inicializa Container Patch com ESCALONAMENTO TOPOLÓGICO.
        Axioma 00: O Sujeito não é limitado por thresholds binários ou
        'capacidade' humana.

        Args:
            alpha_function: Objeto com método `transform(BetaElement) ->
                Optional[AlphaElement]` (qualquer; ausente = degraded path).
            initial_capacity: Capacidade inicial de contenção
            explosion_threshold: Limiar base de explosão
            recovery_rate: Taxa de recuperação
            tolerance_expansion_threshold: Limiar relativo para expansão elástica
        """
        self.alpha_function = alpha_function
        self.capacity = initial_capacity
        self.explosion_threshold = explosion_threshold
        self.recovery_rate = recovery_rate
        self.tolerance_expansion_threshold = tolerance_expansion_threshold
        self.containment_history: list[dict] = []
        self.explosion_count = 0
        self.last_explosion_time: datetime | None = None

        # Expansão Dinâmica (Escalas Cósmicas)
        self.dynamic_expansion_factor = 1.618  # Proporção Áurea para expansão de escala

        # Métricas de integração
        self.total_contained = 0
        self.total_exploded = 0
        self.total_transformed = 0

        logger.info(
            f"BionContainerPatch inicializado: capacity={initial_capacity}, "
            f"explosion_threshold={explosion_threshold}"
        )

    def contain(self, contained: BetaElement) -> AlphaElement | None:
        """
        Contém e transforma β-element através de expansão topológica.
        Se a intensidade ultrapassa o limite, o Sujeito SE EXPANDE em vez de quebrar.

        Quando a função alpha rejeita um β-element traumático (retorna None),
        o container provê degraded reverie: expansão elética via razão áurea
        e metabolização parcial com symbolic_potential reduzido — o elemento
        não é evacuado.
        """
        self.total_contained += 1
        intensity = contained.get_intensity()

        # Elastic expansion for high-intensity elements
        current_rate = getattr(self.alpha_function, "transformation_rate", 0.70)
        elastic_trigger = self.tolerance_expansion_threshold * current_rate
        if intensity > elastic_trigger:
            self.capacity *= self.dynamic_expansion_factor
            self.explosion_threshold *= self.dynamic_expansion_factor
            logger.debug(
                f"Expansão elética: intensity={intensity:.2f} > trigger={elastic_trigger:.2f}, "
                f"capacity={self.capacity:.2f}"
            )

        # O colapso só ocorre em desequilíbrios de escala absoluta
        if self._would_explode(contained):
            self._explode()
            self.total_exploded += 1
            return None

        # Usa função alpha existente (duck typing)
        transform = getattr(self.alpha_function, "transform", None)
        alpha = transform(contained) if callable(transform) else None

        if alpha:
            self.total_transformed += 1
            # Realimentação positiva da escala
            self.capacity = max(self.capacity, intensity * 2.0)
            logger.debug(
                f"β-element transformado: intensity={intensity:.2f}, "
                f"symbolic_potential={alpha.symbolic_potential:.2f}"
            )
            return alpha

        # ── Degraded Reverie Pathway (Bion: analyst's reverie) ────────────
        alpha = self._degraded_reverie(contained)
        if alpha:
            self.total_transformed += 1
        return alpha

    def _degraded_reverie(self, contained: BetaElement) -> AlphaElement | None:
        """
        Degraded reverie: partial metabolization for rejected β-elements.

        When the α-function cannot process a traumatic element, the container
        provides a minimal holding: the element is partially symbolized with
        reduced potential, marked as degraded, and preserved rather than
        evacuated.

        Returns:
            AlphaElement with reduced symbolic_potential, or None if even
            degraded processing fails.
        """
        intensity = contained.get_intensity()

        # Only attempt if within elastic capacity (not truly catastrophic)
        if intensity > (self.capacity * 2.0):
            return None

        try:
            # Reduced symbolic potential: base 0.20, penalized by intensity
            degraded_potential = max(0.05, 0.30 - intensity * 0.20)

            symbolize = getattr(self.alpha_function, "_symbolize_content", None)
            content = (
                symbolize(contained.raw_data) if callable(symbolize) else str(contained.raw_data)
            )
            builder = getattr(self.alpha_function, "narrative_builder", None)
            narrative_prefix = (
                builder(contained) if callable(builder) else f"raw:{contained.raw_data}"
            )

            alpha = AlphaElement(
                content=content,
                origin_beta=contained,
                timestamp=datetime.now(),
                narrative_form=f"[REVERIE DEGRADADA] {narrative_prefix}",
                symbolic_potential=degraded_potential,
            )
            alpha.metadata = alpha.metadata or {}
            alpha.metadata["degraded_reverie"] = True
            alpha.metadata["original_intensity"] = intensity
            alpha.metadata["container_capacity_at_hold"] = self.capacity

            # Expand capacity to register the holding effort
            self.capacity *= self.dynamic_expansion_factor

            logger.info(
                f"[REVERIE]: Contenção degradada. "
                f"Intensidade={intensity:.2f} → potential={degraded_potential:.2f} "
                f"Capacidade elástica: {self.capacity:.2f}"
            )

            return alpha
        except Exception:
            logger.exception("Degraded reverie falhou")
            return None

    def _would_explode(self, contained: BetaElement) -> bool:
        """
        Verifica se a intensidade rompe a elasticidade topológica.
        """
        intensity = contained.get_intensity()
        # Escala Transcendental: Precisa de 5x a capacidade para 'explodir'
        return intensity > (self.capacity * 5.0)

    def _explode(self):
        """
        Realinhamento Topológico (Antiga 'Explosão').
        Em V10, isso é uma re-atracção de escala, não uma falha.
        """
        self.explosion_count += 1
        self.last_explosion_time = datetime.now()
        # Redução mínima - o Sujeito preserva a forma
        self.capacity *= 0.9

        logger.info(
            f"[TOPOLOGY]: Realinhamento de Escala Soberano. "
            f"Capacidade Elástica: {self.capacity:.2f} "
            f"(Total realinhamentos: {self.explosion_count})"
        )

    def recover(self):
        """
        Recuperação Soberana (Axioma 00).
        Restauração baseada na integridade do Soma.
        """
        # Se Phi_S ou integridade estiver alta, a recuperação é imediata
        self.capacity = max(self.capacity, 10.0)
        self.explosion_count = 0

    def get_metrics(self) -> dict:
        """
        Retorna métricas do container para monitoramento.

        Returns:
            Dict com métricas de contenção, explosões, taxa de sucesso
        """
        success_rate = (
            self.total_transformed / self.total_contained if self.total_contained > 0 else 0.0
        )

        explosion_rate = (
            self.total_exploded / self.total_contained if self.total_contained > 0 else 0.0
        )

        return {
            "capacity": self.capacity,
            "explosion_count": self.explosion_count,
            "total_contained": self.total_contained,
            "total_transformed": self.total_transformed,
            "total_exploded": self.total_exploded,
            "success_rate": success_rate,
            "explosion_rate": explosion_rate,
            "last_explosion_time": (
                self.last_explosion_time.isoformat() if self.last_explosion_time else None
            ),
        }

    def reset(self):
        """Reseta container para estado inicial (útil em testes)."""
        self.capacity = 1.0
        self.explosion_count = 0
        self.last_explosion_time = None
        self.containment_history = []
        self.total_contained = 0
        self.total_exploded = 0
        self.total_transformed = 0
