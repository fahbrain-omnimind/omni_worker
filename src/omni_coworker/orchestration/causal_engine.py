"""causal_engine — validação correlação→causa usável pela governance.

Orquestração runtime / Runtime orchestration:
Executado sob demanda pela governance para validar se uma diferença
observada é causalmente significativa antes de autorizar intervenção.

Arquitetura / Architecture:
Portado de omnimind-kilombo-sovereign/src/metacognition/causal_engine.py
(OW-STU-008a). Diferenças vs original: removida dependência de scipy;
testes t de Welch e Mann-Whitney implementados com numpy/stdlib;
register_event mantido como log forense. Sem deps sovereign.

Princípios teóricos invocados / Theoretical principles:
Pearl do-calculus; distinção P(Y|X) vs P(Y|do(X)); tamanho de efeito
(Cohen's d); regra 2-sigma para threshold adaptativo.

Analogia–homologia (interpretativo):
Correlação observacional ≈ sombra; intervenção do() ≈ ato.

Linha final pt-BR: correlação não é causa; só intervenção valida.
"""

from __future__ import annotations

import logging
import math
import time
from typing import Any, Dict, List

import numpy as np

logger = logging.getLogger(__name__)


def _betacf(a: float, b: float, x: float) -> float:
    """Continued fraction for the incomplete beta function (NR)."""
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    if abs(d) < 1e-30:
        d = 1e-30
    d, h = 1.0 / d, d
    for m in range(1, 101):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 / max(1e-30, 1.0 + aa * d)
        c = max(1e-30, 1.0 + aa / c)
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 / max(1e-30, 1.0 + aa * d)
        c = max(1e-30, 1.0 + aa / c)
        de = d * c
        h *= de
        if abs(de - 1.0) < 3e-14:
            break
    return h


def _betai(a: float, b: float, x: float) -> float:
    """Regularized incomplete beta I_x(a,b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
                  + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def _t_two_tailed_p(t: float, df: float) -> float:
    """Two-tailed p-value for Student's t: I_{df/(df+t²)}(df/2, 1/2)."""
    if df <= 0:
        return 1.0
    return min(1.0, max(0.0, _betai(df / 2.0, 0.5, df / (df + t * t))))


def _norm_sf(z: float) -> float:
    """Standard normal survival function via erfc."""
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def _mann_whitney_p(obs: np.ndarray, inter: np.ndarray) -> tuple[float, float]:
    """Mann-Whitney U + two-tailed normal-approx p (continuity corr.)."""
    a, b = np.sort(obs), np.sort(inter)
    n1, n2 = a.size, b.size
    ranks = np.empty(n1 + n2)
    merged = np.concatenate([a, b])
    order = np.argsort(merged, kind="stable")
    ranks[order] = np.arange(1, n1 + n2 + 1)
    r1 = float(ranks[:n1].sum())
    u1 = r1 - n1 * (n1 + 1) / 2.0
    mu, sigma = n1 * n2 / 2.0, math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12.0)
    if sigma == 0:
        return u1, 1.0
    z = (u1 - mu - 0.5 * (1 if u1 > mu else -1)) / sigma
    return u1, min(1.0, 2.0 * _norm_sf(abs(z)))


class CausalEngine:
    def __init__(self, confidence_level: float = 0.95) -> None:
        self.confidence_level = float(confidence_level)
        self.logger = logger
        self._intervention_history: List[Dict[str, Any]] = []

    def compute_causal_effect(
        self, observational_data: List[float], interventional_data: List[float]
    ) -> Dict[str, Any]:
        obs = np.asarray(observational_data, dtype=float)
        inter = np.asarray(interventional_data, dtype=float)
        if obs.size == 0 or inter.size == 0:
            return {"error": "Insufficient data"}
        mean_obs = float(np.mean(obs))
        mean_int = float(np.mean(inter))
        ace = mean_int - mean_obs
        v1 = float(np.var(obs, ddof=1)) if obs.size > 1 else 0.0
        v2 = float(np.var(inter, ddof=1)) if inter.size > 1 else 0.0
        se = math.sqrt(v1 / obs.size + v2 / inter.size) if (v1 or v2) else 0.0
        t_stat = (mean_int - mean_obs) / se if se > 0 else 0.0
        num = (v1 / obs.size + v2 / inter.size) ** 2
        den = (v1 / obs.size) ** 2 / max(obs.size - 1, 1) + (v2 / inter.size) ** 2 / max(inter.size - 1, 1)
        df = num / den if den > 0 else 1.0
        p_value_t = _t_two_tailed_p(t_stat, df) if se > 0 else 0.0
        _, p_value_u = (_mann_whitney_p(obs, inter)
                        if obs.size > 1 and inter.size > 1 else (0.0, 1.0))
        alpha = 1.0 - self.confidence_level
        is_significant = (p_value_t < alpha or p_value_u < alpha
                          or abs(t_stat) > 1.96
                          or (se == 0.0 and ace != 0.0))
        pooled_std = math.sqrt((float(np.std(obs)) ** 2 + float(np.std(inter)) ** 2) / 2)
        cohens_d = ace / pooled_std if pooled_std > 0 else 0.0
        result = {
            "ace": ace,
            "is_causal": bool(is_significant),
            "p_value_t": float(p_value_t),
            "p_value_u": float(p_value_u),
            "effect_size_cohen": float(cohens_d),
            "sample_size_obs": int(obs.size),
            "sample_size_int": int(inter.size),
            "t_stat": float(t_stat),
            "df": float(df),
        }
        self.logger.info("causal_effect_computed ace=%s significant=%s", ace, is_significant)
        return result

    def validate_intervention_necessity(
        self, current_state_metrics: Dict[str, float], predicted_outcome_metrics: Dict[str, float]
    ) -> bool:
        differences = {}
        for key in current_state_metrics:
            if key in predicted_outcome_metrics:
                differences[key] = abs(current_state_metrics[key] - predicted_outcome_metrics[key])
        if not differences:
            return False
        avg_difference = sum(differences.values()) / len(differences)
        if len(self._intervention_history) >= 5:
            past = [h.get("avg_difference", 0.0) for h in self._intervention_history[-10:]]
            if past:
                arr = np.asarray(past, dtype=float)
                mean_diff = float(np.mean(arr))
                std_diff = float(np.std(arr))
                threshold = mean_diff + 2 * std_diff
            else:
                threshold = 0.1
        else:
            threshold = 0.1
        should_intervene = avg_difference > threshold
        self._intervention_history.append({
            "timestamp": time.time(),
            "current_metrics": dict(current_state_metrics),
            "predicted_metrics": dict(predicted_outcome_metrics),
            "differences": differences,
            "avg_difference": avg_difference,
            "threshold": threshold,
            "intervened": should_intervene,
        })
        if len(self._intervention_history) > 100:
            self._intervention_history = self._intervention_history[-100:]
        return bool(should_intervene)

    def register_event(self, cause: str, effect: str, metadata: Dict[str, Any] = None) -> None:
        if metadata is None:
            metadata = {}
        try:
            self.logger.info("CAUSAL_REGISTRY: %s -> %s", cause, effect, extra={"metadata": metadata})
        except Exception:
            print(f"CAUSAL_REGISTRY: {cause} -> {effect} | {metadata}")
