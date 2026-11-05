"""Modes — personas especializadas com modelo sticky (padrão Roo Code).

English: Roo-style modes with per-mode persona + sticky model (role).
Each mode remembers its last-used model role; switching modes selects
the stored role automatically. State persists to a small JSON file.

pt-BR: Modes estilo Roo com persona por modo + modelo sticky (role).
Cada modo lembra o último role usado; trocar de modo seleciona o role
gravado automaticamente. Estado persiste em JSON pequeno.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

MODES: dict[str, dict[str, Any]] = {
    "architect": {"persona": "architect", "role": "analyst", "desc": "Planejamento e decomposição"},
    "ask": {"persona": "analyst", "role": "analyst", "desc": "Perguntas e leitura clínica"},
    "debug": {"persona": "debug", "role": "executor", "desc": "Diagnóstico somente-leitura"},
    "code": {"persona": "code", "role": "executor", "desc": "Geração e patches"},
    "reviewer": {"persona": "critic", "role": "analyst", "desc": "Revisão e juízes"},
    "orchestrator": {"persona": "titan", "role": "analyst", "desc": "Coordenação e veredito"},
    "judge": {"persona": "judge", "role": "judge", "desc": "Juiz pesado (tier xl, :8100)"},
}


def state_path() -> Path:
    """JSON state path (env-overridable)."""
    return Path(os.getenv("OMNI_MODES_STATE", "/tmp/omni_modes_state.json"))


def _load_state() -> dict[str, str]:
    p = state_path()
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:  # noqa: BLE001, S110
            pass
    return {}


def _save_state(state: dict[str, str]) -> None:
    try:
        state_path().write_text(json.dumps(state, indent=2))
    except Exception:  # noqa: BLE001, S110
        pass


def current_mode() -> str:
    """Last active mode (default 'code')."""
    return _load_state().get("_current", "code")


def switch_mode(mode: str) -> dict[str, Any]:
    """Switch mode, restoring its sticky model role.

    English: Persists the mode and returns mode spec with the stored
    role (or the default for the mode).
    pt-BR: Persiste o modo e retorna a spec com o role gravado (ou o
    default do modo).
    """
    if mode not in MODES:
        mode = "code"
    state = _load_state()
    state["_current"] = mode
    _save_state(state)
    spec = dict(MODES[mode])
    spec["sticky_role"] = state.get(f"role:{mode}", spec["role"])
    return spec


def set_role(mode: str, role: str) -> None:
    """Pin a model role to a mode (sticky model)."""
    if mode not in MODES or role not in ("analyst", "executor", "judge"):
        return
    state = _load_state()
    state[f"role:{mode}"] = role
    _save_state(state)


def spec_for(mode: str | None = None) -> dict[str, Any]:
    """Spec of a mode (current by default) with sticky role."""
    return switch_mode(mode or current_mode())