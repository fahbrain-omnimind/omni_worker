"""safety.refusal_state — instrumentação das transições de recusa (A5).

Orquestração runtime / Runtime orchestration:
    `record_verdict(allowed, trigger)` mantém o refusal_state: quando um
    veredito de recusa chega, abre um episódio (refusal_entered_at +
    trigger por episódio); quando uma ação é permitida estando em
    recusa, fecha (refusal_exited_at). Persiste em
    OMNI_STATE_DIR/refusal_state.json (atômico) para sobreviver restart.
    Fail-open em IO — nunca derruba o gate por falha do tracker.

Arquitetura / Architecture:
    Adapta a pendência soberana A5 (PENDENCIAS_ATIVAS): refusal_state
    com timestamps e trigger por episódio, observável via
    `current_state()`. Estado: {"in_refusal", "entered_at",
    "trigger": {...}, "episodes": [...], "total_refusals"}.

Princípios teóricos invocados / Theoretical principles:
    n/a — modulo utilitario de observabilidade de segurança.

pt-BR: transições de recusa com timestamp e trigger, persistentes.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any


def _path() -> Path:
    return Path(os.getenv("OMNI_STATE_DIR", "data")) / "refusal_state.json"


def _load() -> dict[str, Any]:
    try:
        p = _path()
        if p.exists():
            raw = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                return raw
    except Exception:  # noqa: BLE001, S110
        pass
    return {"in_refusal": False, "entered_at": None, "exited_at": None,
            "trigger": None, "episodes": [], "total_refusals": 0}


def _save(state: dict[str, Any]) -> None:
    try:
        p = _path()
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(state, ensure_ascii=False, default=str),
                       encoding="utf-8")
        os.replace(tmp, p)
    except Exception:  # noqa: BLE001, S110
        pass


def record_verdict(allowed: bool, trigger: dict[str, Any] | None = None) -> dict[str, Any]:
    """Registra um veredito e transiciona o refusal_state.

    - allowed=False: abre/mantém episódio de recusa (entered_at, trigger).
    - allowed=True com in_refusal: fecha episódio (exited_at).
    Retorna o estado atualizado.
    """
    st = _load()
    now = time.time()
    if not allowed:
        st["total_refusals"] = int(st.get("total_refusals") or 0) + 1
        if not st.get("in_refusal"):
            st["in_refusal"] = True
            st["entered_at"] = now
            st["exited_at"] = None
            st["trigger"] = trigger or {}
        else:
            # recusa repetida: atualiza trigger do episódio aberto
            st["trigger"] = trigger or st.get("trigger")
    else:
        if st.get("in_refusal"):
            st["in_refusal"] = False
            st["exited_at"] = now
            ep = {"entered_at": st.get("entered_at"), "exited_at": now,
                  "duration_s": round(now - float(st.get("entered_at") or now), 3),
                  "trigger": st.get("trigger")}
            eps = list(st.get("episodes") or [])
            eps.append(ep)
            st["episodes"] = eps[-50:]
            st["trigger"] = None
    _save(st)
    return st


def current_state() -> dict[str, Any]:
    """Estado atual de recusa (observabilidade)."""
    return _load()
