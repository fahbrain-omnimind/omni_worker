"""evaporation — score de decaimento por não-uso para chunks do code index.

Orquestração runtime / Runtime orchestration:
Função pura usada pelo revisor para ponderar chunks do code index;
sem estado, sem I/O.

Arquitetura / Architecture:
Portado de omnimind-kilombo-sovereign/src/psychology/motivation/hawking_motivation.py
(OW-STU-008b), reduzido à função pura evaporation_score. Diferenças:
sem engine de estado, sem RNG, sem persistência; entrada é dict com
last_used_ts/use_count/half_life.

Princípios teóricos invocados / Theoretical principles:
Decaimento exponencial por meia-vida (Hawking radiation analogy);
uso repetido aumenta retenção.

Linha final pt-BR: conhecimento não usado evapora; uso preserva.
"""

from __future__ import annotations

import math
import time
from datetime import datetime, timezone
from typing import Any, Mapping


def _to_epoch(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, datetime):
        dt = value
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
    # try parse iso
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except Exception:
        return float(time.time())


def evaporation_score(chunk: Mapping[str, Any], now: Any = None) -> float:
    """Retorna score de decaimento [0,1] para um chunk.

    chunk: {last_used_ts, use_count, half_life}. half_life em segundos.
    """
    last_used_ts = chunk.get("last_used_ts")
    use_count = int(chunk.get("use_count", 0) or 0)
    half_life = float(chunk.get("half_life", 0) or 0)
    now_ts = _to_epoch(now) if now is not None else time.time()
    last_ts = _to_epoch(last_used_ts) if last_used_ts is not None else now_ts
    age = max(0.0, now_ts - last_ts)
    if half_life <= 0:
        half_life = 7 * 24 * 3600  # default: 7-day half-life
    decay = 1.0 - math.pow(0.5, age / half_life)
    # uso repetido retém
    retention = 1.0 / (1.0 + max(0, use_count))
    score = decay * retention
    return float(max(0.0, min(1.0, score)))
