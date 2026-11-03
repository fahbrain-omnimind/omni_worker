"""psychoanalysis.plasticity_resource — operational resource postures (port).

Orquestração runtime / Runtime orchestration:
Port ADAPTADO do `src/psychoanalysis/plasticity_context_resource.py` do
sovereign (OW-STU-012). O MECANISMO é fiel (lanes → posturas com
confiança, eixo primário, ação recomendada, razões); os LANES foram
remapeados das superfícies clínicas do sovereign (cannabis/psicodélico/
sono) para as superfícies OPERACIONAIS do worker: VRAM, swap/modelo,
entropia de atenção, térmico, janela de ativações e homeostase.
Puro stdlib — o daemon consome sem torch.

Arquitetura / Architecture:
Cada `assess_*` recebe um dataclass imutável de inputs (valores 0..1
normalizados) e devolve `ResourceAssessment` (posture, confidence,
primary_axis, recommended_action, reasons). `assess_worker_bundle`
agrega o snapshot do `kernel.soma`/`kernel.homeostasis` em uma lista de
posturas — o que o integration_loop e o scheduler usam para modular
comportamento (ex.: postura de pressão VRAM → swap ou degradação).

Princípios teóricos invocados / Theoretical principles:
Posturas de recurso = classificação operacional de contexto conhecido
(como no soberano: "não prescreve, classifica"). Aqui: não diagnóstica
o modelo, classifica o ESTADO MATERIAL da máquina (OW-STU-009/OW-MATH-001
— materialidade, não consciência).

pt-BR: posturas de recurso operacionais — VRAM/swap/entropia/térmico
mapeadas para ação, com o mecanismo portado do sovereign.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ResourceLane(str, Enum):
    """Lanes operacionais do worker (remap dos lanes soberanos)."""

    VRAM_PRESSURE = "vram_pressure"
    MODEL_SWAP_REGIME = "model_swap_regime"
    ATTENTION_ENTROPY = "attention_entropy"
    THERMAL = "thermal"
    ACTIVATION_WINDOW = "activation_window"
    HOMEOSTASIS = "homeostasis"


class ResourcePosture(str, Enum):
    """Como o worker deve tratar o lane agora."""

    READY_TO_PROTOTYPE = "ready_to_prototype"
    CONTEXT_REQUIRED = "context_required"
    WITNESS_REQUIRED = "witness_required"
    STUDY_REQUIRED = "study_required"
    HOLD_BOUNDARY = "hold_boundary"


@dataclass(frozen=True)
class VramPressureInputs:
    """Marcadores de pressão de VRAM (0..1 normalizado)."""

    vram_ratio: float = 0.0        # usado / total
    swap_active: bool = False
    headroom: float = 0.0          # 1 - vram_ratio
    eviction_pending: bool = False
    evict_threshold: float = 0.9   # espelha OMNI_SWAP_EVICT_THRESHOLD


@dataclass(frozen=True)
class SwapRegimeInputs:
    """Marcadores do regime de swap de modelo."""

    unloaded_minutes: float = 0.0
    evict_threshold: float = 0.9
    reload_threshold: float = 0.75
    external_unload: bool = False   # descarga externa (bateria/CI) detectada


@dataclass(frozen=True)
class AttentionEntropyInputs:
    """Entropia de atenção média na janela (0..1 normalizada)."""

    entropy_mean: float = 0.5
    entropy_collapse: float = 0.0  # fração de janelas colapsadas
    divergent_layer: bool = False


@dataclass(frozen=True)
class ThermalInputs:
    """Térmico do host (normalizado)."""

    temp_ratio: float = 0.0        # temp / tjmax
    throttling: bool = False


@dataclass(frozen=True)
class ActivationWindowInputs:
    """Janela de ativações (produção real vs vazia)."""

    n_records: int = 0
    min_window: int = 6
    rehydrated: bool = False


@dataclass(frozen=True)
class HomeostasisInputs:
    """Estado da homeostase."""

    state: str = "stable"          # stable | warning | degraded
    producing: bool = False
    angst: int = 0                 # ciclos consecutivos degradados


@dataclass(frozen=True)
class ResourceAssessment:
    """Avaliação operacional de um lane de recurso."""

    lane: ResourceLane
    posture: ResourcePosture
    confidence: float
    primary_axis: str
    recommended_action: str
    reasons: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "lane": self.lane.value,
            "posture": self.posture.value,
            "confidence": self.confidence,
            "primary_axis": self.primary_axis,
            "recommended_action": self.recommended_action,
            "reasons": list(self.reasons),
        }


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def _mean(vals: list[float]) -> float:
    return sum(vals) / max(1, len(vals))


def assess_vram_pressure(inputs: VramPressureInputs) -> ResourceAssessment:
    """Pressão de VRAM → postura de swap ou degradação."""
    reasons: list[str] = []
    if inputs.vram_ratio >= inputs.evict_threshold and inputs.eviction_pending:
        reasons.append("vram_ratio no limite com eviction pendente — evictar")
    elif inputs.vram_ratio >= inputs.evict_threshold:
        reasons.append("vram_ratio no limite — preparar swap scheduler")
    if inputs.swap_active:
        reasons.append("swap ativo — headroom comprometido")
    if inputs.headroom < 0.1:
        reasons.append("headroom < 10% — degradação de qualidade esperada")
    if inputs.vram_ratio < 0.6:
        reasons.append("headroom folgado — modelo pode ser reloaded")

    if inputs.vram_ratio >= inputs.evict_threshold:
        posture = ResourcePosture.HOLD_BOUNDARY
    elif inputs.vram_ratio >= 0.8:
        posture = ResourcePosture.CONTEXT_REQUIRED
    else:
        posture = ResourcePosture.READY_TO_PROTOTYPE

    return ResourceAssessment(
        lane=ResourceLane.VRAM_PRESSURE,
        posture=posture,
        confidence=round(_clip01(inputs.vram_ratio), 4),
        primary_axis="vram_ratio_headroom",
        recommended_action=(
            "evictar modelo ou reduzir batch — pressão no teto"
            if posture == ResourcePosture.HOLD_BOUNDARY
            else "monitorar headroom — operação normal"
        ),
        reasons=reasons or ["headroom adequado"],
    )


def assess_swap_regime(inputs: SwapRegimeInputs) -> ResourceAssessment:
    """Regime de swap → postura de reload/espera."""
    reasons: list[str] = []
    if inputs.external_unload:
        reasons.append("descarga externa detectada — não recarregar ainda")
    elif inputs.unloaded_minutes > 0 and inputs.unloaded_minutes >= 30:
        reasons.append(f"modelo descarregado {inputs.unloaded_minutes:.0f}min — "
                       "janela timed-reload aberta")
    if inputs.unloaded_minutes == 0:
        reasons.append("modelo residente — sem ação de swap")

    if inputs.external_unload:
        posture = ResourcePosture.CONTEXT_REQUIRED
    elif inputs.unloaded_minutes >= 30:
        posture = ResourcePosture.READY_TO_PROTOTYPE
    else:
        posture = ResourcePosture.STUDY_REQUIRED

    return ResourceAssessment(
        lane=ResourceLane.MODEL_SWAP_REGIME,
        posture=posture,
        confidence=round(_clip01(inputs.unloaded_minutes / 60.0), 4),
        primary_axis="unload_window_external_observation",
        recommended_action=(
            "respeitar descarga externa — adiar reload"
            if posture == ResourcePosture.CONTEXT_REQUIRED
            else "reload seguro liberado"
        ),
        reasons=reasons or ["swap inativo"],
    )


def assess_attention_entropy(inputs: AttentionEntropyInputs) -> ResourceAssessment:
    """Entropia de atenção → risco de degeneração."""
    reasons: list[str] = []
    if inputs.entropy_collapse >= 0.5:
        reasons.append("colapso de entropia frequente — bacia atratora")
    if inputs.divergent_layer:
        reasons.append("camada divergente ativa — atenção concentrada")
    if inputs.entropy_mean < 0.3:
        reasons.append("entropia média baixa — padrão repetitivo provável")

    if inputs.entropy_collapse >= 0.5:
        posture = ResourcePosture.HOLD_BOUNDARY
    elif inputs.entropy_mean < 0.3:
        posture = ResourcePosture.WITNESS_REQUIRED
    else:
        posture = ResourcePosture.READY_TO_PROTOTYPE

    return ResourceAssessment(
        lane=ResourceLane.ATTENTION_ENTROPY,
        posture=posture,
        confidence=round(_clip01(inputs.entropy_mean), 4),
        primary_axis="entropy_collapse_vs_baseline",
        recommended_action=(
            "intervir em geração degenerada (gate de atrator)"
            if posture == ResourcePosture.HOLD_BOUNDARY
            else "entropia saudável"
        ),
        reasons=reasons or ["entropia dentro do esperado"],
    )


def assess_thermal(inputs: ThermalInputs) -> ResourceAssessment:
    """Térmico → postura de carga."""
    reasons: list[str] = []
    if inputs.temp_ratio >= 0.9:
        reasons.append("temp no teto — throttling iminente")
    if inputs.throttling:
        reasons.append("throttling ativo — reduzir carga")
    if inputs.temp_ratio < 0.5:
        reasons.append("temp folgada — carga normal")

    if inputs.temp_ratio >= 0.9 or inputs.throttling:
        posture = ResourcePosture.HOLD_BOUNDARY
    elif inputs.temp_ratio >= 0.7:
        posture = ResourcePosture.CONTEXT_REQUIRED
    else:
        posture = ResourcePosture.READY_TO_PROTOTYPE

    return ResourceAssessment(
        lane=ResourceLane.THERMAL,
        posture=posture,
        confidence=round(_clip01(inputs.temp_ratio), 4),
        primary_axis="temp_tjmax_throttling",
        recommended_action=(
            "reduzir carga ou pausar ciclo"
            if posture == ResourcePosture.HOLD_BOUNDARY
            else "térmico ok"
        ),
        reasons=reasons or ["térmico normal"],
    )


def assess_activation_window(inputs: ActivationWindowInputs) -> ResourceAssessment:
    """Janela de ativações → se há material β suficiente."""
    reasons: list[str] = []
    if inputs.n_records >= inputs.min_window:
        reasons.append(f"janela com {inputs.n_records} registros — material β ok")
    else:
        reasons.append(f"janela com {inputs.n_records} registros (< {inputs.min_window})")
    if inputs.rehydrated:
        reasons.append("janela reidratada do jsonl — contexto preservado")

    if inputs.n_records >= inputs.min_window:
        posture = ResourcePosture.READY_TO_PROTOTYPE
    else:
        posture = ResourcePosture.STUDY_REQUIRED

    return ResourceAssessment(
        lane=ResourceLane.ACTIVATION_WINDOW,
        posture=posture,
        confidence=round(_clip01(inputs.n_records / inputs.min_window), 4),
        primary_axis="window_size_vs_min",
        recommended_action=(
            "publicar phi_layer/attractor — janela pronta"
            if posture == ResourcePosture.READY_TO_PROTOTYPE
            else "aguardar gerações para popular a janela"
        ),
        reasons=reasons or ["janela vazia"],
    )


def assess_homeostasis(inputs: HomeostasisInputs) -> ResourceAssessment:
    """Homeostase → postura do ciclo."""
    reasons: list[str] = []
    if inputs.state == "degraded":
        reasons.append("estado degradado")
    elif inputs.state == "warning":
        reasons.append("estado warning")
    if not inputs.producing:
        reasons.append("idle — repouso ≠ produzindo")
    if inputs.angst >= 2:
        reasons.append(f"{inputs.angst} ciclos consecutivos degradados — angst")

    if inputs.state == "degraded" or inputs.angst >= 2:
        posture = ResourcePosture.HOLD_BOUNDARY
    elif inputs.state == "warning":
        posture = ResourcePosture.WITNESS_REQUIRED
    else:
        posture = ResourcePosture.READY_TO_PROTOTYPE

    return ResourceAssessment(
        lane=ResourceLane.HOMEOSTASIS,
        posture=posture,
        confidence=round(_clip01(1.0 if inputs.state == "stable" else 0.4), 4),
        primary_axis="homeo_state_producing",
        recommended_action=(
            "pausar produção — homeostase degradada"
            if posture == ResourcePosture.HOLD_BOUNDARY
            else "ciclo normal"
        ),
        reasons=reasons or ["homeostase estável"],
    )


def assess_worker_bundle(bundle: dict[str, Any]) -> list[ResourceAssessment]:
    """Agrega o snapshot do kernel em posturas (lista ordenada por lane).

    English: Maps kernel.soma/kernel.homeostasis fields to postures.
    pt-BR: Mapeia campos do kernel.soma/homeostasis para posturas.
    """
    soma = bundle.get("soma") or {}
    homeo = bundle.get("homeostasis") or {}
    vram_ratio = _clip01(float(soma.get("vram_ratio", 0.0)))
    assessments = [
        assess_vram_pressure(VramPressureInputs(
            vram_ratio=vram_ratio,
            swap_active=bool(soma.get("swap_active", False)),
            headroom=1.0 - vram_ratio,
            eviction_pending=bool(bundle.get("eviction_pending", False)),
        )),
        assess_attention_entropy(AttentionEntropyInputs(
            entropy_mean=_clip01(float(soma.get("entropy_mean", 0.5))),
            entropy_collapse=_clip01(float(soma.get("entropy_collapse", 0.0))),
            divergent_layer=bool(soma.get("divergent_layer", False)),
        )),
        assess_thermal(ThermalInputs(
            temp_ratio=_clip01(float(soma.get("temp_ratio", 0.0))),
            throttling=bool(soma.get("throttling", False)),
        )),
        assess_homeostasis(HomeostasisInputs(
            state=str(homeo.get("state", "stable")),
            producing=bool(homeo.get("producing", False)),
            angst=int(homeo.get("angst", 0)),
        )),
    ]
    return assessments