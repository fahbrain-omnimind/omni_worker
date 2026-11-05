"""shared_workspace.bus — pub/sub in-process com hot ring buffer.

Orquestração runtime / Runtime orchestration:
    `publish()` valida, timestampa, empurra no deque do tópico (hot),
    chama subscribers por prefixo e persiste via store (write-through —
    cadência atual ~1 ev/s é trivial para sqlite WAL). Subscribers com
    exceção são isolados: um consumidor ruim não pode derrubar o
    publicador nem os demais.

Arquitetura / Architecture:
    Hot state = `dict[topic, deque(maxlen=HOT_MAX)]` protegido por um
    único RLock (throughput baixo, contenção irrelevante). Warm state =
    store sqlite WAL — fonte da verdade para histórico. O buffer por
    tópico evita que um canal barulhento expulse os demais.

Princípios teóricos invocados / Theoretical principles:
    Broadcast do workspace global: uma vez publicado, o estado fica
    disponível a qualquer módulo — acoplamento causal via endereço, não
    via referência de objeto.

Analogia–homologia (interpretativo, não mecanístico):
    Análogo a um barramento neural onde módulos "escutam" canais;
    mecanicamente é apenas dict + deques + callbacks.

pt-BR: barramento em processo com ring buffer por tópico e
persistência write-through em sqlite.
"""

from __future__ import annotations

import threading
import time
from collections import deque
from collections.abc import Callable
from typing import Any

from .schema import validate

HOT_MAX = 2000  # estados quentes por tópico

_lock = threading.RLock()
_hot: dict[str, deque] = {}
_subs: list[tuple[str, Callable[[str, dict], None]]] = []


def publish(topic: str, payload: Any, ts: float | None = None) -> dict:
    """Validate + broadcast + persist one canonical state.

    English: returns the stored event `{ts, topic, payload}`.
    pt-BR: retorna o evento persistido `{ts, topic, payload}`.
    """
    validate(topic, payload)
    evt = {"ts": ts or time.time(), "topic": topic, "payload": payload}
    with _lock:
        _hot.setdefault(topic, deque(maxlen=HOT_MAX)).append(evt)
        subs = [cb for pfx, cb in _subs if topic.startswith(pfx)]
    for cb in subs:
        try:
            cb(topic, evt)
        except Exception:  # noqa: BLE001, S110
            pass  # consumidor ruim não derruba o barramento
    try:
        from .store import put
        put(evt["ts"], topic, evt["payload"])
    except Exception:  # noqa: BLE001, S110
        pass  # persistência degradada não impede o hot path
    return evt


def subscribe(prefix: str, cb: Callable[[str, dict], None]) -> None:
    """Register cb(topic, evt) for every topic starting with prefix."""
    with _lock:
        _subs.append((prefix, cb))


def latest(topic: str) -> dict | None:
    """Newest event on topic, or None."""
    with _lock:
        dq = _hot.get(topic)
        return dict(dq[-1]) if dq else None


def history(topic: str, n: int = 50) -> list[dict]:
    """Last n hot events on topic (newest last)."""
    with _lock:
        dq = _hot.get(topic)
        return [dict(e) for e in list(dq)[-n:]] if dq else []


def topics() -> list[str]:
    """Topics with hot state."""
    with _lock:
        return sorted(_hot)


def snapshot() -> dict[str, dict]:
    """Latest event per topic — the mesh's current face."""
    with _lock:
        return {t: dict(dq[-1]) for t, dq in _hot.items() if dq}


def _reset() -> None:
    """Test seam: clears bus state (not for production use)."""
    with _lock:
        _hot.clear()
        _subs.clear()
