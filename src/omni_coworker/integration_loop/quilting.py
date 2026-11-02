"""integration_loop.quilting — quilting point (point de capiton) sobre embeddings.

Orquestração runtime / Runtime orchestration:
    `detect_quilting_point` consome a sequência recente de embeddings
    narrativos (listas de floats) + topic hints e, quando a variância
    entre embeddings cai (convergência), fixa um ponto de basta
    (quilting point): tópico/sentido estável com timestamp e janela de
    validade. Retorna dict {fixed_topic, stability, window} ou None.
    Função pura, sem I/O, sem torch.

Arquitetura / Architecture:
    Port conceitual de src/lacanian/desire_graph.py (SignifierChain.
    create_quilting_point) — APENAS o conceito de ponto de capiton.
    Diferenças vs original: sem grafo II, sem significantes, sem
    jouissance; apenas detecção numérica de convergência sobre
    embeddings + hints. Sem deps sovereign.

Princípios teóricos invocados / Theoretical principles:
    Point de capiton (Lacan): ponto que fixa temporariamente o
    deslizamento metonímico, estabilizando significação. Aqui: queda de
    variância entre embeddings recentes → fixação temporária de sentido.

pt-BR: detecção de convergência em embeddings narrativos recentes.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import numpy as np


def detect_quilting_point(
    embeddings: list[list[float]] | None,
    topic_hints: list[str] | None = None,
    *,
    min_points: int = 4,
    var_threshold: float = 0.05,
    window_seconds: float = 300.0,
) -> Optional[dict[str, Any]]:
    """Detecta quilting point: convergência (variância caindo) → tópico fixo.

    Args:
        embeddings: sequência recente de embeddings narrativos (listas floats).
        topic_hints: hints de tópico alinhados à sequência (opcional).
        min_points: mínimo de pontos para considerar convergência.
        var_threshold: limiar de variância média por dimensão para "fixar".
        window_seconds: janela de validade do ponto fixado.

    Returns:
        dict {fixed_topic, stability, window} ou None se sem convergência.
    """
    if not embeddings or len(embeddings) < min_points:
        return None
    arr = np.asarray(embeddings, dtype=float)
    if arr.ndim != 2 or arr.shape[0] < min_points:
        return None
    # variância por dimensão ao longo da sequência
    per_dim_var = arr.var(axis=0)
    mean_var = float(np.mean(per_dim_var)) if per_dim_var.size else 0.0
    if not np.isfinite(mean_var) or mean_var > var_threshold:
        return None
    # tendência: variância da segunda metade <= primeira metade (caindo)
    half = arr.shape[0] // 2
    var_first = float(np.mean(arr[:half].var(axis=0))) if half > 1 else mean_var
    var_second = float(np.mean(arr[half:].var(axis=0))) if half > 1 else mean_var
    if var_second > var_first + 1e-12:
        return None
    # topic: hint mais frequente na segunda metade (ou último não-vazio)
    hints = topic_hints or []
    candidates = [h for h in hints[-half:] if h]
    if candidates:
        # mais frequente
        from collections import Counter
        fixed_topic = Counter(candidates).most_common(1)[0][0]
    elif hints:
        fixed_topic = hints[-1]
    else:
        fixed_topic = None
    if not fixed_topic:
        return None
    stability = float(np.clip(1.0 - mean_var / max(var_threshold, 1e-9), 0.0, 1.0))
    now = datetime.now(timezone.utc)
    window = {
        "start": now.isoformat(),
        "end": (now + timedelta(seconds=window_seconds)).isoformat(),
        "seconds": window_seconds,
    }
    return {
        "fixed_topic": fixed_topic,
        "stability": round(stability, 6),
        "window": window,
    }
