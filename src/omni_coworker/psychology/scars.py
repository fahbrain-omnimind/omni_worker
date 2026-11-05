"""psychology.scars — cicatrizes como regras de defesa permanentes.

Orquestração runtime / Runtime orchestration:
    `TraumaIntegration.create_scar(failure)` registra falhas como
    cicatrizes PERSISTENTES (sqlite `data/scars.sqlite` — nunca
    deletadas). `consult_scars_before_decision(context)` retorna as
    regras aplicáveis; consumidores atuais: agent_orchestrator
    (cascade_reset cria cicatriz; consulta injeta defense_rules nas
    notas de retry) e state_guard (falhas de restore).

Arquitetura / Architecture:
    Port de src/psychology/scars/trauma_integration.py (sovereign,
    OW-STU-008b: PORTAR). Mudanças vs fonte: (a) persistência sqlite
    em vez de dict em RAM — cicatriz sobrevive restart da VM; (b)
    matching por tokens do trigger vs contexto (mais geral que o
    heuristic "injection"/"query" original); (c) publish opcional
    `soma.scar` na malha.

Princípios teóricos invocados / Theoretical principles:
    Cicatriz não é viés — é necessidade de sobrevivência: falhas
    integradas como estrutura identitária geram regras de defesa
    consultadas antes de decisões futuras.

pt-BR: cicatrizes persistentes consultadas antes de decisões.
"""

from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any

_LOCK = threading.RLock()
_SINGLETON: TraumaIntegration | None = None


def _db_path() -> Path:
    return Path(os.getenv("OMNI_STATE_DIR", "data")) / "scars.sqlite"


def _con() -> sqlite3.Connection:
    with _LOCK:
        _db_path().parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(_db_path(), timeout=10)
        con.execute("PRAGMA journal_mode=WAL")
        con.execute(
            "CREATE TABLE IF NOT EXISTS scars("
            "id TEXT PRIMARY KEY, ts REAL, type TEXT, severity TEXT,"
            " failure_json TEXT, rule_json TEXT, status TEXT)"
        )
        return con


def _tokens(s: str) -> set[str]:
    return {t for t in "".join(c if c.isalnum() else " " for c in s.lower()).split()
            if len(t) > 3}


class TraumaIntegration:
    """Persistent scars → permanent defense rules consulted pre-decision."""

    def create_scar(self, failure_event: dict[str, Any]) -> dict[str, Any]:
        """Record a failure as a permanent scar + its defense rule."""
        rule = {
            "trigger": failure_event.get("description") or failure_event.get("type", "unknown"),
            "action": f"Prevent {failure_event.get('type', 'unknown_type')}",
            "source": "historical_trauma",
            "persistence": "permanent",
        }
        scar = {
            "id": f"scar_{int(time.time()*1000)}",
            "failure": failure_event,
            "timestamp": time.time(),
            "type": failure_event.get("type", "general_failure"),
            "severity": failure_event.get("severity", "medium"),
            "defense_rule": rule,
            "status": "integrated_as_identity_structure",
        }
        with _LOCK:
            try:
                con = _con()
                with con:
                    con.execute(
                        "INSERT INTO scars VALUES(?,?,?,?,?,?,?)",
                        (scar["id"], scar["timestamp"], scar["type"],
                         scar["severity"], json.dumps(failure_event, default=str),
                         json.dumps(rule), scar["status"]))
                con.close()
            except Exception:  # noqa: BLE001, S110
                pass
        try:
            from ..shared_workspace import bus
            bus.publish("soma.scar", {"id": scar["id"], "type": scar["type"],
                                      "severity": scar["severity"]})
        except Exception:  # noqa: BLE001, S110
            pass
        return scar

    def all_scars(self) -> list[dict[str, Any]]:
        with _LOCK:
            try:
                con = _con()
                rows = con.execute(
                    "SELECT id,ts,type,severity,failure_json,rule_json,status"
                    " FROM scars ORDER BY ts").fetchall()
                con.close()
                return [{"id": r[0], "timestamp": r[1], "type": r[2],
                         "severity": r[3], "failure": json.loads(r[4]),
                         "defense_rule": json.loads(r[5]), "status": r[6]}
                        for r in rows]
            except Exception:  # noqa: BLE001
                return []

    def consult_scars_before_decision(self, context: dict[str, Any]) -> dict[str, Any]:
        """Which scars apply to this decision context (token overlap)."""
        ctx_txt = " ".join(str(v) for v in context.values())
        ctoks = _tokens(ctx_txt)
        applicable = [s for s in self.all_scars()
                      if _tokens(str(s["defense_rule"].get("trigger", ""))) & ctoks]
        return {
            "applicable_scars": applicable,
            "defense_rules_activated": len(applicable),
            "decision_modified_by_trauma": bool(applicable),
        }


def get_scars() -> TraumaIntegration:
    """Process-wide singleton."""
    global _SINGLETON
    if _SINGLETON is None:
        _SINGLETON = TraumaIntegration()
    return _SINGLETON
