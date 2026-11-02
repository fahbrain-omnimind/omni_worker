"""shared_workspace — barramento de estado compartilhado do worker.

English: In-process state bus where worker modules publish and read
canonical states (soul, soma, agency, swap, kernel, feedback). Derived
from the canonical shared_workspace concept, redesigned CPU/RAM-only
for the Kaggle worker — no torch, no cross-process IPC in P0.
pt-BR: Barramento de estado em processo onde os módulos do worker
publicam e leem estados canônicos (soul, soma, agency, swap, kernel,
feedback). Derivado do shared_workspace canônico, redesenhado CPU/RAM
para o worker Kaggle — sem torch, sem IPC cross-process no P0.
"""

from .bus import publish, subscribe, latest, history, topics
from .schema import CANONICAL_PREFIXES, validate

__all__ = [
    "publish", "subscribe", "latest", "history", "topics",
    "CANONICAL_PREFIXES", "validate",
]
