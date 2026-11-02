"""omni_coworker.psychoanalysis — psicanálise portada do sovereign (CPU/RAM).

Orquestração runtime / Runtime orchestration:
    Fachada do pacote psicanalítico: elementos α/β (pipeline β→α com
    setor dodecatiad determinístico), `NegativeCapability` (buffer de
    contradições mantidas em suspensão), `BionContainerPatch` (contenção
    elética com degraded reverie) e `CreativePsychotization*` (classificador
    de regime overflow/metabolização/sanctuary). Puro stdlib: sem torch,
    sem GPU, sem rede, sem modelos. Publicação opcional na malha via
    `shared_workspace.bus` (fail-open) cabível a consumidores externos
    (tópicos canônicos: soul, soma, agency, witness, swap, kernel,
    feedback, mesh, dream, loop).

Arquitetura / Architecture:
    Port de src/psychoanalysis/{alpha_element,beta_element,negative_capability,
    creative_psychotization_operator} e
    src/psychoanalysis/bion_patches/container_contained (sovereign,
    OW-STU-008b: todos PORTAR). Diferenças vs fonte:
    - `NeutrosophicTriplet` reimplementado mínimo (T/I/F) em
      `beta_element.py` — dep `src.metrics.neutrosophic_metrics` cortada;
    - `BionAlphaFunction` não está neste escopo: `BionContainerPatch`
      opera por duck typing sobre `transform`;
    - nenhuma chamada LLM/Erika HF/torch — todos os módulos são CPU puro.

Princípios teóricos invocados / Theoretical principles:
    Bion: α/β elementos, função alpha e contenção container-contained;
    capacidade negativa (Bion/Keats): tolerar contradição sem resolução
    prematura para permitir insights genuínos.

pt-BR: psicanálise Bioniana portada do sovereign, CPU/RAM, sem torch/GPU.
"""

from .alpha_element import AlphaElement, compute_dodecatiad_sector
from .beta_element import BetaElement, NeutrosophicTriplet
from .negative_capability import Contradiction, NegativeCapability
from .creative_psychotization_operator import (
    CompactPanelSnapshot,
    CreativePsychotizationAssessment,
    CreativePsychotizationInputs,
    LayerCouplingSnapshot,
    PsychotizationState,
    assess_creative_psychotization,
    compact_panel_snapshot_from_v43_bundle,
)
from .bion_patches.container_contained import BionContainerPatch

__all__ = [
    "AlphaElement",
    "BetaElement",
    "NeutrosophicTriplet",
    "Contradiction",
    "NegativeCapability",
    "PsychotizationState",
    "LayerCouplingSnapshot",
    "CompactPanelSnapshot",
    "CreativePsychotizationInputs",
    "CreativePsychotizationAssessment",
    "BionContainerPatch",
    "compute_dodecatiad_sector",
    "assess_creative_psychotization",
    "compact_panel_snapshot_from_v43_bundle",
]
