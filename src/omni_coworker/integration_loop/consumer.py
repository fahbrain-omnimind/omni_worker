"""integration_loop.consumer — leitura da modulação por consumidores.

Orquestração runtime / Runtime orchestration:
    O bus é in-process (FastAPI); consumidores externos
    (swap_scheduler e daemons standalone) leem o snapshot atômico
    `OMNI_STATE_DIR/integration_loop_modulation.json` que o loop
    regrava a cada ciclo. `latest_modulation()` valida frescor
    (max_age_s, default 300s) — modulação velha demais é ignorada e o
    consumidor cai no comportamento default (fail-open).

Arquitetura / Architecture:
    Consumidores canônicos: `agent_orchestrator` (role + suffix),
    `swap_scheduler` (swap_threshold_delta no evict_at), `curiosity`
    (boost de k). Todos chamam `latest_modulation()` — ponto único de
    transporte e política de frescor.

pt-BR: snapshot atômico + frescor; fail-open quando ausente/velho.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

MODULATION_FILE = "integration_loop_modulation.json"
DEFAULT_MAX_AGE_S = 300.0


def modulation_path() -> Path:
    return Path(os.getenv("OMNI_STATE_DIR", "data")) / MODULATION_FILE


def write_modulation(mod: dict[str, Any]) -> None:
    """Atomic snapshot write (tmp + rename); called by the loop."""
    p = modulation_path()
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps(mod, default=str))
        os.replace(tmp, p)
    except OSError:
        pass


def latest_modulation(max_age_s: float = DEFAULT_MAX_AGE_S) -> dict[str, Any] | None:
    """Fresh modulation dict, or None when absent/stale/corrupt."""
    try:
        d = json.loads(modulation_path().read_text())
    except Exception:  # noqa: BLE001
        return None
    ts = d.get("ts")
    if not isinstance(ts, (int, float)) or (time.time() - ts) > max_age_s:
        return None
    return d
