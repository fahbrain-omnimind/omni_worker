"""Brain: server wrapper, affect derivation, activations.

English: Brain substrate integration.
pt-BR: Integração com substrato cerebral.
"""

from __future__ import annotations

from . import server, affect, activations
from .server import create_brain_router, get_brain_client, ERIKA_HOST, ERIKA_PORT
from .affect import derive_affect, derive_affect_from_brain
from .activations import push, recent

__all__ = [
    "server", "affect", "activations",
    "create_brain_router", "get_brain_client", "ERIKA_HOST", "ERIKA_PORT",
    "derive_affect", "derive_affect_from_brain",
    "push", "recent"
]
