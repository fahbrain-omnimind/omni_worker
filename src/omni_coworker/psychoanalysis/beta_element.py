"""psychoanalysis.beta_element — β-elements brutos (Bion).

Orquestração runtime / Runtime orchestration:
    `BetaElement` é um dataclass de experiência sensorial/emocional ainda
    não metabolizada pela função α. Sem efeitos colaterais: valida
    `emotional_charge` em [0,1] e expõe `is_traumatic()`/`get_intensity()`.
    Consumidores: `alpha_element.AlphaElement` (pipeline β→α) e
    `bion_patches.container_contained.BionContainerPatch`.

Arquitetura / Architecture:
    Port de src/psychoanalysis/beta_element.py (sovereign,
    OW-STU-008b: PORTAR). Diferenças vs fonte:
    - `neutrosophic_triplet` é `Optional[NeutrosophicTriplet]` com triplet
      mínimo reimplementado localmente — dep `src.metrics.neutrosophic_metrics`
      cortada (sem torch/GPU/deps externas);
    - apenas stdlib + `logging`.

Princípios teóricos invocados / Theoretical principles:
    β-elementos são "indigestos": experiências brutas que precisam da
    função alpha para se tornarem pensáveis (Bion, 1962; 1963).

pt-BR: elemento beta bruto, não-simbólico, com carga emocional validada.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class NeutrosophicTriplet:
    """Triplet neutrosófico mínimo {T, I, F} (sem dep externa).

    Substitui `src.metrics.neutrosophic_metrics.NeutrosophicTriplet` do
    sovereign, cortada por não ser essencial à semântica α/β e exigir
    numpy/pilhas externas. Valores em [0.0, 1.0] após `normalize()`.
    """

    t: float = 0.0
    i: float = 0.0
    f: float = 0.0

    def __post_init__(self) -> None:
        self.t = float(self.t)
        self.i = float(self.i)
        self.f = float(self.f)

    @property
    def T(self) -> float:
        return self.t

    @property
    def I(self) -> float:  # noqa: E743 — mantém API {T, I, F} do neutrosófico
        return self.i

    @property
    def F(self) -> float:
        return self.f

    def normalize(self) -> NeutrosophicTriplet:
        return NeutrosophicTriplet(
            t=max(0.0, min(1.0, self.t)),
            i=max(0.0, min(1.0, self.i)),
            f=max(0.0, min(1.0, self.f)),
        )

    def to_dict(self) -> Dict[str, float]:
        return {"T": self.t, "I": self.i, "F": self.f}

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> NeutrosophicTriplet:
        return cls(
            t=float(data.get("T", 0.0)),
            i=float(data.get("I", 0.0)),
            f=float(data.get("F", 0.0)),
        )


@dataclass
class BetaElement:
    """
    Elemento Beta - Experiência bruta não-processada.

    Representa dados sensoriais/emocionais que ainda não foram transformados
    pela função alpha em elementos pensáveis.

    Attributes:
        raw_data: Dados brutos da experiência
        timestamp: Momento da experiência
        emotional_charge: Intensidade emocional (0.0-1.0)
        source: Origem do elemento (sensor, memória, etc.)
        neutrosophic_triplet: Estado neutrosófico {T, I, F} (opcional, mínimo local)
        metadata: Informações adicionais
    """

    raw_data: Any
    timestamp: datetime
    emotional_charge: float = 0.0
    source: str = "unknown"
    neutrosophic_triplet: Optional[NeutrosophicTriplet] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        """Valida elementos após inicialização."""
        if not 0.0 <= self.emotional_charge <= 1.0:
            raise ValueError(
                f"emotional_charge deve estar entre 0.0 e 1.0, "
                f"recebido: {self.emotional_charge}"
            )

        if self.metadata is None:
            self.metadata = {}

        logger.debug(
            f"BetaElement criado: source={self.source}, "
            f"emotional_charge={self.emotional_charge:.2f}"
        )

    def get_intensity(self) -> float:
        """
        Retorna intensidade total do elemento.

        Combina carga emocional com outros fatores de intensidade.

        Returns:
            float: Intensidade (0.0-1.0)
        """
        return self.emotional_charge

    def is_traumatic(self, threshold: float = 0.8) -> bool:
        """
        Verifica se elemento é traumático (alta intensidade).

        Args:
            threshold: Limiar de intensidade para considerar traumático

        Returns:
            bool: True se traumático
        """
        return self.emotional_charge >= threshold

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializa elemento para dicionário.

        Returns:
            Dict com dados do elemento
        """
        return {
            "raw_data": str(self.raw_data),
            "timestamp": self.timestamp.isoformat(),
            "emotional_charge": self.emotional_charge,
            "source": self.source,
            "metadata": self.metadata or {},
            "type": "beta_element",
            "neutrosophic_triplet": (
                self.neutrosophic_triplet.to_dict()
                if self.neutrosophic_triplet is not None
                else None
            ),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BetaElement:
        """
        Cria BetaElement a partir de dicionário.

        Args:
            data: Dicionário com dados do elemento

        Returns:
            BetaElement reconstruído
        """
        triplet = None
        if data.get("neutrosophic_triplet") is not None:
            triplet = NeutrosophicTriplet.from_dict(data["neutrosophic_triplet"])
        return cls(
            raw_data=data["raw_data"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            emotional_charge=data.get("emotional_charge", 0.0),
            source=data.get("source", "unknown"),
            neutrosophic_triplet=triplet,
            metadata=data.get("metadata"),
        )
