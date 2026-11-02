"""Activations ring buffer helpers.

English: Thin adapter over Erika activation summaries.
pt-BR: Adaptador fino sobre resumos de ativação da Erika.
"""

from __future__ import annotations

from collections import deque

_ACTIVATIONS: deque = deque(maxlen=256)


def push(record: dict) -> None:
    """Push an activation summary into the ring buffer.

    English: Stores last 256 activation summaries.
    pt-BR: Armazena os últimos 256 resumos de ativação.
    """
    _ACTIVATIONS.append(record)


def recent(limit: int = 16) -> list:
    """Return recent activation summaries.

    English: Returns up to limit most recent summaries.
    pt-BR: Retorna até limit resumos mais recentes.
    """
    return list(_ACTIVATIONS)[-limit:]
