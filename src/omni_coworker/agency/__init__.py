"""Agency plane: teleology, analyst, dream, witness.

English: Composes existing OmniMind modules into the agency plane.
pt-BR: Compõe módulos existentes do OmniMind no plano de agência.
"""

from __future__ import annotations

from . import analyst, curiosity, dream, teleology, witness
from .analyst import analyze_session, get_insights
from .curiosity import explore
from .dream import dream_cycle, metabolize, weave
from .teleology import compute_omega_teleology, generate_missions
from .witness import append_witness, read_witness, verify_witness, witness_event

__all__ = [
    "analyst",
    "analyze_session",
    "append_witness",
    "compute_omega_teleology",
    "curiosity",
    "dream",
    "dream_cycle",
    "explore",
    "generate_missions",
    "get_insights",
    "metabolize",
    "read_witness",
    "teleology",
    "verify_witness",
    "weave",
    "witness",
    "witness_event"
]
