"""Inter-agent message bus.

English: Lightweight publish/subscribe bus with pending queues and
last-writer-with-weight conflict resolution. The canonical source
(`src.agentes.agent_protocol.AgentMessageBus`) is asyncio/queue based
with a different surface (register/send/receive), so we reimplement the
small synchronous surface here instead of forcing async into agents.
pt-BR: Bus publish/subscribe leve com filas pendentes e resolução de
conflitos last-writer-com-peso. A fonte canônica
(`src.agentes.agent_protocol.AgentMessageBus`) é baseada em asyncio/
filas com superfície diferente (register/send/receive), por isso
reimplementamos aqui a pequena superfície síncrona em vez de forçar
async nos agentes.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

__all__ = ["MessageBus", "canonical_bus_available", "get_message_bus"]

# Canonical source is probed lazily; only used as an availability flag so
# callers can decide whether to bridge to the async bus. No import cost at
# module level (avoids pulling asyncio agent protocol into every import).
_canonical_available: bool | None = None


def canonical_bus_available() -> bool:
    """Check if the canonical AgentMessageBus is importable.

    English: True when src.agentes.agent_protocol loads cleanly.
    pt-BR: True quando src.agentes.agent_protocol carrega limpo.
    """
    global _canonical_available
    if _canonical_available is None:
        try:
            from src.agentes.agent_protocol import AgentMessageBus  # noqa: F401

            _canonical_available = True
        except Exception:  # noqa: BLE001
            _canonical_available = False
    return _canonical_available


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


class MessageBus:
    """Synchronous inter-agent message bus.

    English: In-memory dict of channel queues + handler registry.
    pt-BR: Dict em memória de filas por canal + registro de handlers.
    """

    def __init__(self) -> None:
        self._queues: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self._handlers: dict[str, list[Callable[[dict[str, Any]], None]]] = defaultdict(list)
        self._conflicts: list[dict[str, Any]] = []

    # -- pub/sub -------------------------------------------------------------
    def subscribe(
        self, channel: str, handler: Callable[[dict[str, Any]], None]
    ) -> Callable[[dict[str, Any]], None]:
        """Register a handler for a channel.

        English: Returns the handler so it can be unsubscribed later.
        pt-BR: Registra um handler para o canal; retorna o handler para
        permitir unsubscribe posterior.
        """
        if handler not in self._handlers[channel]:
            self._handlers[channel].append(handler)
        return handler

    def unsubscribe(self, channel: str, handler: Callable[[dict[str, Any]], None]) -> bool:
        """Remove a handler from a channel.

        English: True when the handler was present.
        pt-BR: True quando o handler estava registrado.
        """
        try:
            self._handlers[channel].remove(handler)
            return True
        except ValueError:
            return False

    def publish(self, channel: str, message: dict[str, Any]) -> None:
        """Publish a message to a channel.

        English: Enqueues the message (pending) and dispatches to
        handlers. Missing timestamp/weight fields are defaulted so
        conflict resolution is deterministic.
        pt-BR: Enfileira a mensagem (pending) e despacha aos handlers.
        Campos ts/weight ausentes ganham default para resolução de
        conflitos determinística.
        """
        msg = dict(message)
        msg.setdefault("ts", _now())
        msg.setdefault("weight", 0.0)
        self._queues[channel].append(msg)
        for handler in list(self._handlers.get(channel, [])):
            try:
                handler(msg)
            except Exception:  # noqa: BLE001, S112
                continue

    # -- queues --------------------------------------------------------------
    def pending(self, channel: str) -> list[dict[str, Any]]:
        """Return a snapshot of undelivered messages on a channel.

        English: Messages stay pending until consumed.
        pt-BR: Mensagens ficam pendentes até serem consumidas.
        """
        return list(self._queues.get(channel, []))

    def consume(self, channel: str) -> dict[str, Any] | None:
        """Pop the oldest pending message (FIFO).

        English: Returns None when the channel is empty.
        pt-BR: Remove a mensagem mais antiga (FIFO); None se vazio.
        """
        queue = self._queues.get(channel)
        if not queue:
            return None
        return queue.pop(0)

    def channels(self) -> list[str]:
        """List channels with pending messages."""
        return [c for c, q in self._queues.items() if q]

    def size(self, channel: str) -> int:
        """Number of pending messages on a channel."""
        return len(self._queues.get(channel, []))

    # -- conflict resolution -------------------------------------------------
    def resolve_conflict(
        self, channel: str, key: str = "weight"
    ) -> dict[str, Any] | None:
        """Resolve conflicting pending messages on a channel.

        English: Winner = highest `key` value, tie-broken by most recent
        `ts` (last-writer). The decision is recorded in _conflicts.
        pt-BR: Vencedor = maior valor de `key`, desempate pelo `ts` mais
        recente (last-writer). A decisão fica registrada em _conflicts.
        """
        messages = self.pending(channel)
        if not messages:
            return None

        def _sort_key(m: dict[str, Any]) -> tuple[Any, Any]:
            return (m.get(key, 0.0), m.get("ts", ""))

        winner = max(messages, key=_sort_key)
        self._conflicts.append(
            {
                "channel": channel,
                "key": key,
                "candidates": len(messages),
                "winner": winner.get("agent") or winner.get("sender"),
                "ts": _now(),
            }
        )
        return winner

    # Alias matching the broader "conflict_resolution" wording.
    conflict_resolution = resolve_conflict

    def conflicts(self) -> list[dict[str, Any]]:
        """Return the conflict resolution log."""
        return list(self._conflicts)

    def stats(self) -> dict[str, Any]:
        """Summary of bus state.

        English: Channels with pending counts + total conflicts.
        pt-BR: Canais com contagens pendentes + total de conflitos.
        """
        return {
            "channels": {c: len(q) for c, q in self._queues.items()},
            "handlers": {c: len(h) for c, h in self._handlers.items()},
            "total_conflicts": len(self._conflicts),
        }


_bus: MessageBus | None = None


def get_message_bus() -> MessageBus:
    """Return the process-wide MessageBus singleton.

    English: Lazy singleton; pure-Python, no canonical dependency.
    pt-BR: Singleton do processo; puro-Python, sem dependência canônica.
    """
    global _bus
    if _bus is None:
        _bus = MessageBus()
    return _bus