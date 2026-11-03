"""integration_loop.stages — os 5 estágios + fechamento (numpy puro).

Arquitetura / Architecture:
    Funções puras sobre `ctx` (dict); sem I/O, sem torch. Sequência:
    sensory_input → qualia → narrative → meaning_maker → expectation
    → sensory_feedback. Embeddings em `list[float]` (JSON-safe).
    `ctx` carrega: `bundle` (kernel daemon), `history` (ring buffer
    de ModuleStates), `rng` (numpy Generator seeded por cycle_id),
    `x_prev` (último sensory embedding p/ expectation).

Princípios teóricos invocados / Theoretical principles:
    - sensory_input: vetorização z-score das estatísticas de ativação
      (tokens, entropia, normas de camada) — Bion β→α como *analogia*
      de transformação bruto→elemento processável.
    - qualia: ancoragem afetiva — tanh sobre [x; afeto; phi/psi/sigma/
      epsilon] gera vetor q + valence/arousal escalares.
    - narrative: EMA (gamma=0.85) sobre últimos K embeddings — canal
      de continuidade entre ciclos.
    - meaning_maker: cosseno(narrative, top-1 code index) →
      meaning_score + topic_hint.
    - expectation: preditor ridge leve de x_{t+1}; pred_err alimenta
      feedback e modulação.

pt-BR: implementação numpy dos estágios do loop; docstring acima
separa orquestração, arquitetura e princípios (analogia marcada).
"""

from __future__ import annotations

from typing import Any

import numpy as np

from .schema import ModuleState

DIM = 64
GAMMA = 0.85


def _bucket(vals: list[float], n: int) -> np.ndarray:
    """Mean-pool `vals` into `n` buckets (pad with last value)."""
    if not vals:
        return np.zeros(n)
    a = np.asarray(vals, dtype=float)
    means = [c.mean() for c in np.array_split(a, n) if c.size]
    pad = means[-1] if means else 0.0
    means += [pad] * (n - len(means))
    return np.asarray(means[:n])


def _zscore(v: np.ndarray, stats: dict) -> np.ndarray:
    mu, sd = stats.get("mu"), stats.get("sd")
    if mu is None or sd is None:
        return v
    return (v - mu) / np.where(sd < 1e-8, 1.0, sd)


def sensory_input(ctx: dict[str, Any]) -> ModuleState:
    """Activation stats → z-scored embedding vector x ∈ R^DIM."""
    bundle = ctx.get("bundle") or {}
    models = bundle.get("models") or {}
    feats: list[float] = []
    for m in sorted(models):
        mm = models[m] or {}
        feats += [
            mm.get("prompt_tokens_mean") or 0.0,
            mm.get("gen_tokens_mean") or 0.0,
            mm.get("gen_tokens_max") or 0.0,
            mm.get("attention_entropy_mean") or 0.0,
            mm.get("hidden_norm_mean") or 0.0,
            mm.get("hidden_norm_std") or 0.0,
            mm.get("last_layer_norm_mean") or 0.0,
            float(mm.get("n_records") or 0),
        ]
    soma = bundle.get("soma") or {}
    feats += [soma.get("cpu_percent") or 0.0,
              soma.get("gpu_vram_used_gb") or 0.0,
              soma.get("gpu_util_percent") or 0.0]
    soul = bundle.get("soul") or {}
    feats += [soul.get("phi") or 0.0, soul.get("psi") or 0.0,
              soul.get("sigma") or 0.0, soul.get("epsilon") or 0.0]
    x = _bucket(feats, DIM)
    x = _zscore(x, ctx.get("feat_stats") or {})
    norm = float(np.linalg.norm(x))
    return ModuleState("sensory_input", embedding=[round(float(v), 6) for v in x],
                       metadata={"norm": round(norm, 4),
                                 "models": sorted(models)})


def qualia(ctx: dict[str, Any], x: np.ndarray) -> ModuleState:
    """Affective anchoring: q = tanh(W_q·[x; affect; soul])."""
    bundle = ctx.get("bundle") or {}
    rng = ctx["rng"]
    affect = bundle.get("affect") or {}
    avals = [v for r in ("analyst", "executor")
             for k in ("attention_entropy_mean", "hidden_norm_mean")
             for v in [((affect.get(r) or {}).get(k))] if v is not None]
    soul = bundle.get("soul") or {}
    svec = np.array([soul.get("phi") or 0.0, soul.get("psi") or 0.0,
                     soul.get("sigma") or 0.0, soul.get("epsilon") or 0.0])
    avec = _bucket(avals, 8)
    W = rng.normal(0, 1.0 / np.sqrt(DIM + 12), size=(DIM, DIM + 12))
    q = np.tanh(W @ np.concatenate([x, avec, svec]))
    arousal = float(np.clip(np.linalg.norm(q) / np.sqrt(DIM), 0, 1))
    valence = float(np.clip(np.mean(np.tanh(svec - 0.5)) * 0.5 +
                            np.mean(q) * 0.5, -1, 1))
    return ModuleState("qualia", embedding=[round(float(v), 6) for v in q],
                       metadata={"valence": round(valence, 4),
                                 "arousal": round(arousal, 4)})


_W_NARRATIVE = np.random.default_rng(20261102).normal(
    0, 1.0 / np.sqrt(DIM), size=(DIM, DIM))


def narrative(ctx: dict[str, Any], x: np.ndarray) -> ModuleState:
    """EMA over last K sensory embeddings — continuity channel."""
    hist = (ctx.get("history") or [])[-8:]
    emb = np.asarray(x, dtype=float)
    for i, past in enumerate(hist):
        w = GAMMA ** (len(hist) - i)
        emb = emb + w * np.asarray(past, dtype=float)
    emb = emb / (1.0 + sum(GAMMA ** i for i in range(1, len(hist) + 1)))
    # projeção fixa (não seed-por-ciclo): embeddings comparáveis entre
    # ciclos — pré-requisito do quilting point (convergência de variância).
    nvec = _W_NARRATIVE @ emb
    return ModuleState("narrative",
                       embedding=[round(float(v), 6) for v in nvec],
                       metadata={"history_len": len(hist),
                                 "narrative_form": f"ema{len(hist)}g{GAMMA}"})


def meaning_maker(ctx: dict[str, Any], nvec: np.ndarray) -> ModuleState:
    """Cosine(narrative, top-1 code index) → meaning_score + hint."""
    hit = ctx.get("meaning_hit") or {}
    score = hit.get("score")
    # correlate narrative energy with retrieval score
    energy = float(np.linalg.norm(nvec) / np.sqrt(DIM))
    ms = None
    if isinstance(score, (int, float)):
        ms = round(float(np.clip(0.5 * score + 0.5 * min(energy, 1.0), 0, 1)), 4)
    return ModuleState("meaning_maker",
                       metadata={"meaning_score": ms,
                                 "topic_hint": hit.get("name"),
                                 "retrieval_score": score})


def expectation(ctx: dict[str, Any], x: np.ndarray) -> ModuleState:
    """Ridge predict x_next from recent x's; pred_err vs current x."""
    hist = [np.asarray(h, dtype=float) for h in (ctx.get("history") or [])[-8:]]
    pred_err = None
    if len(hist) >= 3:
        X = np.stack(hist[:-1])
        Y = np.stack(hist[1:])
        lam = 1e-3
        A = np.linalg.solve(X.T @ X + lam * np.eye(DIM), X.T @ Y)
        x_next_hat = hist[-1] @ A
        pred_err = round(float(np.linalg.norm(x_next_hat - x) /
                               (np.linalg.norm(x) + 1e-8)), 4)
    return ModuleState("expectation",
                       metadata={"pred_err": pred_err,
                                 "history_used": len(hist)})


def sensory_feedback(cycle_id: str, stages: dict[str, ModuleState]) -> ModuleState:
    """Closure: error + meaning written back (no new embedding)."""
    return ModuleState("sensory_feedback", metadata={
        "cycle_id": cycle_id,
        "pred_err": (stages.get("expectation") or ModuleState("")).metadata.get("pred_err"),
        "meaning_score": (stages.get("meaning_maker") or ModuleState("")).metadata.get("meaning_score"),
        "closed": True,
    })
