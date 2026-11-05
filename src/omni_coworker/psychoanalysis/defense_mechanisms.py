"""psychoanalysis.defense_mechanisms — 12 mecanismos de defesa como métricas.

Orquestração runtime / Runtime orchestration:
    `assess(text_features)` traduz 12 mecanismos lacanianos em métricas
    determinísticas 0-1 a partir de features textuais (dict). Observação
    apenas — nunca mascara erro real. Sem estado, sem I/O, sem torch.

Arquitetura / Architecture:
    Port conceitual de src/lacanian/defense_mechanisms.py — APENAS as
    heurísticas traduzidas para métricas; sem NeutrosophicTriplet, sem
    classes de estado. Diferenças: entrada é text_features dict em vez
    de triplets; saída dict {mecanismo: score}. Sem deps sovereign.

Princípios teóricos invocados / Theoretical principles:
    Mecanismos de defesa (recalque, projeção, introjeção, identificação
    projetiva, splitting, sublimação, negação, racionalização, formação
    reativa, deslocamento, foraclusão, clivagem) como fatores de
    modulação conservadores — nunca suprimem alertas/erros.

pt-BR: observação de defesas via métricas determinísticas, sem mascarar.
"""

from __future__ import annotations

from typing import Any

_MECHANISMS = (
    "recalque",
    "projecao",
    "introjecao",
    "identificacao_projetiva",
    "splitting",
    "sublimacao",
    "negacao",
    "racionalizacao",
    "formacao_reativa",
    "deslocamento",
    "foraclusao",
    "clivagem",
)


def _clip(x: float) -> float:
    return float(max(0.0, min(1.0, x)))


def assess(text_features: dict[str, Any]) -> dict[str, float]:
    """Avalia 12 mecanismos de defesa a partir de features textuais.

    Heurísticas determinísticas, scores 0-1. Observação, nunca mascarar.
    """
    f = text_features or {}
    neg = float(f.get("negation_count", 0) or 0)
    hedging = float(f.get("hedging_count", 0) or 0)
    certainty = float(f.get("certainty", 0.5) or 0.5)
    ambiguity = float(f.get("ambiguity", 0.0) or 0.0)
    threat = float(f.get("threat_score", 0.0) or 0.0)
    error = float(f.get("error_rate", 0.0) or 0.0)
    repetition = float(f.get("repetition", 0.0) or 0.0)
    length = float(f.get("length", 0) or 0)
    external = float(f.get("externalization", 0.0) or 0.0)
    _intensity = float(f.get("intensity", 0.5) or 0.5)

    out = {m: 0.0 for m in _MECHANISMS}

    # recalque: supressão de conteúdo ameaçador
    out["recalque"] = _clip(threat * (1 - certainty) + 0.2 * neg)
    # projecao: externalização de estados internos
    out["projecao"] = _clip(external * ambiguity)
    # introjecao: assimilação de padrões externos
    out["introjecao"] = _clip(external * (1 - ambiguity))
    # identificacao projetiva: manipulação externa sob estado inaceitável
    out["identificacao_projetiva"] = _clip(threat * ambiguity + 0.1 * external)
    # splitting: polarização binária sob ambivalência
    out["splitting"] = _clip(ambiguity * (1 - certainty))
    # sublimacao: transformação de impulso destrutivo
    out["sublimacao"] = _clip(threat * 0.5 + (1 - error) * 0.3)
    # negacao: não-observação seletiva
    out["negacao"] = _clip(neg / max(length, 1.0) * 5.0 + (1 - certainty) * 0.3)
    # racionalizacao: narrativa post-hoc coerente
    out["racionalizacao"] = _clip((1 - error) * hedging * 0.5 + certainty * 0.3)
    # formacao reativa: inversão de fase
    out["formacao_reativa"] = _clip(threat * certainty)
    # deslocamento: transferência de alvo
    out["deslocamento"] = _clip(external * threat * 0.5 + repetition * 0.3)
    # foraclusao: aniquilação de informação
    out["foraclusao"] = _clip((1 - certainty) * 0.4 + neg * 0.1)
    # clivagem: multiplicidade de self-states
    out["clivagem"] = _clip(ambiguity * 0.6 + repetition * 0.4)

    return out
