"""Personas: agent configuration loader.

English: Loads persona configs from `config/agents/*.json`
(architect, critic, paradox, titan, visionary) and maps coworker roles
(debug/analyst/reviewer/code/judge) to a persona system prompt.
Fallback is always a minimal dict — missing/invalid configs never raise.
pt-BR: Carrega configs de persona de `config/agents/*.json`
(architect, critic, paradox, titan, visionary) e mapeia papéis do
coworker (debug/analyst/reviewer/code/judge) para um system prompt de
persona. O fallback é sempre um dict mínimo — configs ausentes/inválidas
nunca levantam erro.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

__all__ = ["load_persona", "system_prompt", "ROLE_PERSONA_MAP", "PERSONA_DESCRIPTIONS"]

# Coworker role -> persona config name.
ROLE_PERSONA_MAP: dict[str, str] = {
    "debug": "paradox",
    "analyst": "visionary",
    "reviewer": "critic",
    "code": "architect",
    "judge": "titan",
}

# Human-readable descriptors used when the config has none.
PERSONA_DESCRIPTIONS: dict[str, str] = {
    "architect": "Structural design and code generation authority",
    "critic": "Adversarial reviewer that hunts defects and gaps",
    "paradox": "Contrarian probe of assumptions and edge cases",
    "titan": "Final arbiter judge holding high standards",
    "visionary": "Long-horizon synthesist and analyst",
}


def _default_config_dir() -> Path:
    """Config dir: $OMNI_AGENTS_CONFIG_DIR or <repo>/config/agents.

    English: <repo> is resolved from this file's location so the loader
    works regardless of CWD.
    pt-BR: <repo> é resolvido pela localização deste arquivo para o
    loader funcionar independentemente do CWD.
    """
    env = os.environ.get("OMNI_AGENTS_CONFIG_DIR")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[3] / "config" / "agents"


def load_persona(name: str, config_dir: str | Path | None = None) -> dict[str, Any]:
    """Load a persona config as a dict.

    English: Tries `{name}_config.json`, `{name}.json`, then
    `{name}_agent.json`; fills missing agent_name/mode/version and falls
    back to a minimal dict (with `fallback: True`) when nothing loads.
    pt-BR: Tenta `{name}_config.json`, `{name}.json`, depois
    `{name}_agent.json`; preenche agent_name/mode/version ausentes e cai
    em um dict mínimo (com `fallback: True`) quando nada carrega.
    """
    base = _default_config_dir() if config_dir is None else Path(config_dir)
    candidates = [
        base / f"{name}_config.json",
        base / f"{name}.json",
        base / f"{name}_agent.json",
    ]
    for candidate in candidates:
        try:
            if candidate.exists() and candidate.stat().st_size > 0:
                data = json.loads(candidate.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    data.setdefault("agent_name", name)
                    data.setdefault("mode", name)
                    data.setdefault("version", "0.0.0")
                    return data
        except Exception:
            continue
    return {
        "agent_name": name,
        "mode": name,
        "version": "0.0.0",
        "fallback": True,
    }


def system_prompt(role: str) -> str:
    """Build a persona-based system prompt for a coworker role.

    English: Maps role -> persona (reviewer->critic, code->architect,
    judge->titan, ...) and returns name + description + mode. Always
    non-empty, even when persona configs are unavailable.
    pt-BR: Mapeia papel -> persona (reviewer->critic, code->architect,
    judge->titan, ...) e retorna nome + descrição + mode. Sempre não
    vazio, mesmo sem configs de persona disponíveis.
    """
    persona_name = ROLE_PERSONA_MAP.get(role, role)
    persona = load_persona(persona_name)
    name = str(persona.get("agent_name") or persona_name)
    mode = str(persona.get("mode") or persona_name)
    description = PERSONA_DESCRIPTIONS.get(persona_name.lower(), "")

    lines = [f"You are {name}.", f"Role: {role}. Mode: {mode}."]
    if description:
        lines.append(f"Description: {description}.")
    return "\n".join(lines)