"""psychoanalysis.alpha_element — α-elements transformados + setor dodecatiad.

Orquestração runtime / Runtime orchestration:
    `AlphaElement` é um β-element já transformado pela função alpha: pensável,
    armazenável como memória e combinável em pensamentos. `compute_dodecatiad_sector()`
    atribui determinísticamente (sector15 in [1,15], house12 in [1,12]) via
    SHA-256 de content+source — compatível direto com soul/dodeca do worker.
    Sem efeitos colaterais além de `logging.debug`.

Arquitetura / Architecture:
    Port de src/psychoanalysis/alpha_element.py (sovereign,
    OW-STU-008b: PORTAR). Diferenças vs fonte:
    - `NeutrosophicTriplet` importado de `.beta_element` (triplet mínimo
      local) — dep `src.metrics.neutrosophic_metrics` cortada;
    - `neutrosophic_triplet` permanece `Optional` e não é serializado
      (mesma escolha do original).

Princípios teóricos invocados / Theoretical principles:
    α-elementos são o resultado da transformação de β-elementos pela função
    alpha: simbólicos, integrados à experiência consciente, armazenáveis
    como memória (Bion, 1962; 1963).

Analogia–homologia (interpretativo):
    setor15/house12 por hash funciona como "casa psíquica" determinística do
    elemento — análogo à distribuição dodecatiad usada pelo soul do worker.

pt-BR: elemento alpha pensável com setor dodecatiad computado por hash.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from .beta_element import BetaElement, NeutrosophicTriplet

logger = logging.getLogger(__name__)


# ── Dodecatiad helpers (self-contained, no circular import) ─────────────────
def compute_dodecatiad_sector(content: Any, source: str) -> tuple[int, int]:
    """
    Compute (sector15, house12) for an alpha-element.

    Hashes the combined content+source string via SHA-256 to get a
    deterministic, uniformly distributed sector in [1,15].

    sector15: 1-15 — Dodecatíade 15-house classification
    house12:  1-12 — Classical 12-house mapping (sector15 mod 12)

    Returns:
        (sector15, house12)
    """
    combined = f"{content}::{source}"
    digest = hashlib.sha256(combined.encode("utf-8", errors="ignore")).hexdigest()
    s15 = (int(digest[:8], 16) % 15) + 1  # 1-indexed, range [1,15]
    h12 = ((s15 - 1) % 12) + 1
    return s15, h12


@dataclass
class AlphaElement:
    """
    Elemento Alpha - Experiência transformada e pensável.

    Representa β-elements que foram transformados pela função alpha em
    elementos que podem ser pensados, armazenados e combinados.

    Attributes:
        content: Conteúdo processado e simbólico
        origin_beta: BetaElement de origem
        timestamp: Momento da transformação
        narrative_form: Forma narrativa do elemento
        symbolic_potential: Potencial de simbolização (0.0-1.0)
        neutrosophic_triplet: Estado neutrosófico resultante {T, I, F}
        associations: Outros α-elements associados
        metadata: Informações adicionais
    """

    content: Any
    origin_beta: BetaElement
    timestamp: datetime
    narrative_form: str = ""
    symbolic_potential: float = 0.0
    neutrosophic_triplet: Optional[NeutrosophicTriplet] = None
    associations: List[str] = field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None
    # ── Dodecatiad fields ──────────────────────────────────────────────────
    sector15: int = 0  # 1-15 (0 = unassigned, computed in __post_init__)
    house12: int = 0  # 1-12 (derived from sector15)
    dodecatiad_origin: str = "hash_initial"  # provenance of sector assignment

    def __post_init__(self) -> None:
        """Valida elementos após inicialização."""
        if not 0.0 <= self.symbolic_potential <= 1.0:
            raise ValueError(
                f"symbolic_potential deve estar entre 0.0 e 1.0, "
                f"recebido: {self.symbolic_potential}"
            )

        if self.metadata is None:
            self.metadata = {}

        # Auto-compute dodecatiad sector if not provided
        if self.sector15 == 0:
            source = getattr(self.origin_beta, "source", "unknown")
            self.sector15, self.house12 = compute_dodecatiad_sector(
                self.content, source
            )

        logger.debug(
            f"AlphaElement criado: symbolic_potential={self.symbolic_potential:.2f}, "
            f"sector15={self.sector15}, house12={self.house12}"
        )

    def can_be_thought(self) -> bool:
        """
        Verifica se elemento pode ser pensado.

        Um α-element é pensável se tem potencial simbólico suficiente.

        Returns:
            bool: True se pensável
        """
        return self.symbolic_potential >= 0.3

    def is_dream_capable(self) -> bool:
        """
        Verifica se elemento pode ser usado em sonhos (dream-thoughts).

        Elements com alto potencial simbólico podem formar pensamentos oníricos.

        Returns:
            bool: True se pode ser usado em sonhos
        """
        return self.symbolic_potential >= 0.6

    def get_complexity(self) -> float:
        """
        Retorna complexidade do elemento.

        Baseado em potencial simbólico e número de associações.

        Returns:
            float: Complexidade (0.0-1.0)
        """
        base_complexity = self.symbolic_potential
        association_bonus = min(len(self.associations) * 0.1, 0.3)
        return min(base_complexity + association_bonus, 1.0)

    def add_association(self, other_alpha_id: str) -> None:
        """
        Adiciona associação com outro α-element.

        Args:
            other_alpha_id: ID do outro α-element
        """
        if other_alpha_id not in self.associations:
            self.associations.append(other_alpha_id)
            logger.debug(f"Associação adicionada: {other_alpha_id}")

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializa elemento para dicionário.

        Returns:
            Dict com dados do elemento
        """
        return {
            "content": str(self.content),
            "origin_beta": self.origin_beta.to_dict(),
            "timestamp": self.timestamp.isoformat(),
            "narrative_form": self.narrative_form,
            "symbolic_potential": self.symbolic_potential,
            "associations": self.associations,
            "metadata": self.metadata or {},
            "type": "alpha_element",
            "sector15": self.sector15,
            "house12": self.house12,
            "dodecatiad_origin": self.dodecatiad_origin,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AlphaElement:
        """
        Cria AlphaElement a partir de dicionário.

        Args:
            data: Dicionário com dados do elemento

        Returns:
            AlphaElement reconstruído
        """
        origin_beta = BetaElement.from_dict(data["origin_beta"])

        return cls(
            content=data["content"],
            origin_beta=origin_beta,
            timestamp=datetime.fromisoformat(data["timestamp"]),
            narrative_form=data.get("narrative_form", ""),
            symbolic_potential=data.get("symbolic_potential", 0.0),
            associations=data.get("associations", []),
            metadata=data.get("metadata"),
            sector15=data.get("sector15", 0),
            house12=data.get("house12", 0),
            dodecatiad_origin=data.get("dodecatiad_origin", "hash_initial"),
        )
