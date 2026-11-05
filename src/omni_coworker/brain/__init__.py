"""Brain: server wrapper, affect derivation, activations.

English: Brain substrate integration.
pt-BR: Integração com substrato cerebral.
"""

from __future__ import annotations

from . import activations, affect, server
from .activations import push, recent
from .affect import derive_affect, derive_affect_from_brain
from .server import ERIKA_HOST, ERIKA_PORT, create_brain_router, get_brain_client

__all__ = [
    "ERIKA_HOST",
    "ERIKA_PORT",
    "activations",
    "affect",
    "create_brain_router",
    "derive_affect",
    "derive_affect_from_brain",
    "get_brain_client",
    "push",
    "recent",
    "server"
]
