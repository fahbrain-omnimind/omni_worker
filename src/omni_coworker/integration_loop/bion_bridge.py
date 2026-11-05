"""bion_bridge — metabolização β→α do estado bruto do ciclo.

Orquestração runtime / Runtime orchestration:
Chamado pelo loop após `qualia` (arousal vira `emotional_charge`) e antes
de `meaning_maker` (o conteúdo α entra no metadata). Custo controlado:
a chamada LLM só dispara quando arousal ≥ 0.5, homeostase não-ótima,
ou a cada 5º ciclo — demais ciclos usam MiniLM/heurístico direto.

Arquitetura / Architecture:
Adapta `psychoanalysis.BionAlphaFunction` ao bundle `kernel.cycle`:
o digest do bundle (modelos, drift, homeostase, soul) é o BetaElement;
o AlphaElement produzido enriquece `meaning_maker` como `alpha_content`
+ `symbolic_potential`. Beta não-metabolizável (charge traumática >
tolerance) é reportado como `beta_unmetabolized` — insumo para
negative_capability/scars, não erro.

Princípios teóricos invocados / Theoretical principles:
Bion: β-elementos (experiência bruta) → função-α → α-elementos
(conteúdo pensável/onírico). Arousal da malha ≈ carga emocional.

Analogia–homologia (interpretativo):
Digestão de telemetria ≈ metabolização psíquica; NÃO é processamento
fenomenal — é verbalização operacional do estado da máquina.

Linha final pt-BR: o que a máquina não digere vira ruído; o α é legível.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime
from typing import Any

from ..psychoanalysis.beta_element import BetaElement

_FN = None       # BionAlphaFunction singleton (keeps processing_history)
_CONTAINER = None  # BionContainerPatch singleton (capacity learns)


def _container(use_llm: bool):
    global _FN, _CONTAINER
    if _FN is None:
        from ..psychoanalysis.bion_alpha_function import BionAlphaFunction
        _FN = BionAlphaFunction(use_llm_symbolizer=use_llm)
    _FN.use_llm_symbolizer = use_llm  # gate muda por ciclo; fn é singleton
    if _CONTAINER is None:
        from ..psychoanalysis.bion_patches.container_contained import (
            BionContainerPatch,
        )
        _CONTAINER = BionContainerPatch(_FN)
    return _CONTAINER


def _digest(bundle: dict[str, Any]) -> str:
    """Compact text digest of the kernel cycle — the raw β material."""
    models = bundle.get("models") or {}
    parts = []
    for m in sorted(models):
        mm = models[m] or {}
        parts.append(
            f"{m}: tok={mm.get('gen_tokens_mean')} ent={mm.get('attention_entropy_mean')}"
        )
    homeo = bundle.get("homeostasis") or {}
    soul = bundle.get("soul") or {}
    soma = bundle.get("soma") or {}
    parts.append(f"homeo={homeo.get('state')}:{homeo.get('action')}")
    parts.append(f"soul phi={soul.get('phi')}")
    parts.append(
        f"soma cpu={soma.get('cpu_percent')} vram={soma.get('gpu_vram_used_gb')}"
    )
    drift = bundle.get("drift") or {}
    if drift:
        parts.append(f"drift={sorted(drift)}")
    return " | ".join(parts) or "ciclo sem dados"


def _should_llm(arousal: float, homeo_state: str, cycle_n: int) -> bool:
    # charge ≥ tolerance(0.6) → β não-processável: transform rejeita antes
    # do symbolizer — não gaste LLM onde a resposta é sempre None.
    processable = arousal < 0.6
    return bool(processable and (arousal >= 0.3
                or homeo_state not in ("optimal", "", None)
                or cycle_n % 5 == 0))


def metabolize(ctx: dict[str, Any], arousal: float, cycle_n: int = 0) -> dict[str, Any]:
    """β→α for this cycle. Never raises; always returns a metadata dict."""
    bundle = ctx.get("bundle") or {}
    homeo = (bundle.get("homeostasis") or {}).get("state") or ""
    out: dict[str, Any] = {
        "beta_charge": round(arousal, 4),
        "alpha_content": None,
        "symbolic_potential": None,
        "metabolized": False,
        "tier": "heuristic",
    }
    try:
        beta = BetaElement(
            raw_data=_digest(bundle),
            timestamp=datetime.now(UTC),
            emotional_charge=max(0.0, min(1.0, float(arousal))),
            source="kernel.cycle",
        )
    except Exception:  # noqa: BLE001
        return out
    use_llm = _should_llm(arousal, homeo, cycle_n)
    out["tier"] = "llm_chain" if use_llm else "heuristic"
    t0 = time.time()
    try:
        # container.contain: transform primeiro; β traumático rejeitado cai na
        # reverie degradada (α parcial marcado) em vez de ser evacuado.
        alpha = _container(use_llm).contain(beta)
        if alpha is not None:
            narrative = str(getattr(alpha, "narrative_form", ""))
            out["alpha_content"] = str(getattr(alpha, "content", ""))[:400]
            out["symbolic_potential"] = round(
                float(getattr(alpha, "symbolic_potential", 0.0)), 4
            )
            out["metabolized"] = True
            out["degraded"] = narrative.startswith("[REVERIE")
        else:
            out["beta_unmetabolized"] = True
    except Exception:  # noqa: BLE001
        out["beta_unmetabolized"] = True
    # OW-STU-009: a produção do modelo é β próprio — segundo β quando a
    # janela de ativações mostra atrator (score alto) — metabolizado no
    # mesmo container, marcado como source="activations.window".
    try:
        att = bundle.get("attractor") or {}
        att_score = max((f.get("attractor_score") or 0.0)
                        for f in att.values()) if att else 0.0
        if att and att_score >= 0.5:
            from ..activation_beta.attractor import digest as att_digest
            beta2 = BetaElement(
                raw_data=att_digest(att),
                timestamp=datetime.now(UTC),
                emotional_charge=max(0.0, min(1.0, att_score)),
                source="activations.window")
            a2 = _container(False).contain(beta2)
            if a2 is not None:
                out["attractor_alpha"] = str(getattr(a2, "content", ""))[:400]
                out["attractor_score"] = round(att_score, 4)
    except Exception:  # noqa: BLE001, S110
        pass
    out["elapsed_ms"] = round((time.time() - t0) * 1000, 1)
    return out
