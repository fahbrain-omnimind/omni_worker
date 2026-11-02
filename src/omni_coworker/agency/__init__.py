"""Agency plane: teleology, analyst, dream, witness.

English: Composes existing OmniMind modules into the agency plane.
pt-BR: Compõe módulos existentes do OmniMind no plano de agência.
"""

from __future__ import annotations

from . import teleology, analyst, dream, witness, curiosity
from .teleology import generate_missions, compute_omega_teleology
from .analyst import analyze_session, get_insights
from .dream import metabolize, weave, dream_cycle
from .curiosity import explore
from .witness import append_witness, read_witness, verify_witness, witness_event

__all__ = [
    "teleology", "analyst", "dream", "witness", "curiosity",
    "dream_cycle", "explore",
    "generate_missions", "compute_omega_teleology",
    "analyze_session", "get_insights",
    "metabolize", "weave",
    "append_witness", "read_witness", "verify_witness", "witness_event"
]
