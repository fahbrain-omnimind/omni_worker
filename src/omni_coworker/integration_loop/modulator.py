"""integration_loop.modulator — pacote de modulação derivado do ciclo.

Orquestração runtime / Runtime orchestration:
    `derive_modulation(cycle, bundle)` mapeia métricas do ciclo em
    sinais consumíveis: recomendação de role, delta de threshold de
    swap, boost de curiosidade, suffix de prompt. Regras simples e
    auditáveis (sem modelo treinado) — cada campo tem fórmula clara.

Regras (determinísticas):
    - recommendation: arousal alto OU pred_err alto → "analyst";
      soma saudável + meaning_score alto → "executor"; senão "balanced".
    - swap_threshold_delta: +0.03 se pred_err alto (regime instável →
      mais headroom), -0.02 se meaning_score alto e pred_err baixo.
    - curiosity_boost: (1 - meaning_score) quando score existe; 0.3 default.
    - prompt_suffix: marcador curto de regime, ex "[regime:explore]".

pt-BR: derivação determinística do pacote de modulação publicado em
feedback.loop.
"""

from __future__ import annotations

from typing import Any

from .schema import CycleResult, Modulation

HIGH_ERR = 0.5
HIGH_AROUSAL = 0.7


def _m(cycle: CycleResult, stage: str, key: str):
    st = cycle.stage_states.get(stage)
    return (st.metadata.get(key) if st else None)


def derive_modulation(cycle: CycleResult, bundle: dict[str, Any]) -> Modulation:
    ms = _m(cycle, "meaning_maker", "meaning_score")
    err = _m(cycle, "expectation", "pred_err")
    val = _m(cycle, "qualia", "valence")
    aro = _m(cycle, "qualia", "arousal")
    soul = (bundle.get("soul") or {})
    soma = (bundle.get("soma") or {})

    if (aro or 0) >= HIGH_AROUSAL or (err or 0) >= HIGH_ERR:
        rec = "analyst"
    elif ms is not None and ms >= 0.6:
        rec = "executor"
    else:
        rec = "balanced"

    if (err or 0) >= HIGH_ERR:
        delta = 0.03
    elif ms is not None and ms >= 0.6 and (err or 1) < HIGH_ERR:
        delta = -0.02
    else:
        delta = 0.0

    boost = round(max(0.0, min(1.0, 1.0 - ms)), 4) if ms is not None else 0.3
    suffix = {"analyst": "[regime:reflect]", "executor": "[regime:execute]",
              "balanced": "[regime:steady]"}[rec]

    return Modulation(
        cycle_id=cycle.cycle_id, ts=cycle.ts, meaning_score=ms,
        pred_err=err, qualia_valence=val, qualia_arousal=aro,
        phi=soul.get("phi"), psi=soul.get("psi"), sigma=soul.get("sigma"),
        epsilon=soul.get("epsilon"),
        cpu_load=soma.get("cpu_percent"), ram_pct=soma.get("ram_percent"),
        recommendation=rec, swap_threshold_delta=delta,
        curiosity_boost=boost, prompt_suffix=suffix,
    )
