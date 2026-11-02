"""integration_loop.store — ring buffer + sqlite WAL + jsonl.

Orquestração runtime / Runtime orchestration:
    Hot: ring buffer RAM (últimos 200 CycleResult).
    Warm: `data/integration_loop.sqlite` tabela `cycles` (WAL,
    retenção 7d por ts).
    Cold: `data/monitor/integration_loop_cycles.jsonl` append.
    Mesmo padrão do shared_workspace.store (RLock, OMNI_STATE_DIR).

pt-BR: persistência do loop — ring buffer 200, sqlite WAL 7d, jsonl.
"""

from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
from collections import deque
from pathlib import Path
from typing import Any

_LOCK = threading.RLock()
_DB_NAME = "integration_loop.sqlite"
_JSONL = "integration_loop_cycles.jsonl"
_RETENTION_S = 7 * 24 * 3600
_RING = deque(maxlen=200)


def _state_dir() -> Path:
    return Path(os.getenv("OMNI_STATE_DIR", "data"))


def _db_path() -> Path:
    return _state_dir() / _DB_NAME


def _jsonl_path() -> Path:
    p = _state_dir() / "monitor" / _JSONL
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _con() -> sqlite3.Connection:
    with _LOCK:
        d = _state_dir()
        d.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(_db_path(), timeout=10)
        con.execute("PRAGMA journal_mode=WAL")
        con.execute(
            "CREATE TABLE IF NOT EXISTS cycles("
            "ts REAL, cycle_id TEXT PRIMARY KEY, status TEXT, payload_json TEXT)"
        )
        con.execute("CREATE INDEX IF NOT EXISTS idx_cycles_ts ON cycles(ts)")
        return con


def append_cycle(payload: dict[str, Any]) -> None:
    """Persist one cycle dict to ring + sqlite + jsonl."""
    with _LOCK:
        _RING.append(payload)
        try:
            con = _con()
            with con:
                con.execute(
                    "INSERT OR REPLACE INTO cycles(ts,cycle_id,status,payload_json)"
                    " VALUES(?,?,?,?)",
                    (payload.get("ts") or time.time(), payload.get("cycle_id"),
                     payload.get("status"), json.dumps(payload, default=str)),
                )
                con.execute("DELETE FROM cycles WHERE ts < ?",
                            (time.time() - _RETENTION_S,))
            con.close()
        except Exception:
            pass
        try:
            with open(_jsonl_path(), "a", encoding="utf-8") as fh:
                fh.write(json.dumps(payload, default=str) + "\n")
        except OSError:
            pass


def history(n: int = 50) -> list[dict]:
    """Most recent n cycle payloads (ring buffer first)."""
    with _LOCK:
        return list(_RING)[-n:]


def get_cycle(cycle_id: str) -> dict | None:
    with _LOCK:
        for c in _RING:
            if c.get("cycle_id") == cycle_id:
                return c
        try:
            con = _con()
            row = con.execute(
                "SELECT payload_json FROM cycles WHERE cycle_id=?",
                (cycle_id,)).fetchone()
            con.close()
            return json.loads(row[0]) if row else None
        except Exception:
            return None


def _reset() -> None:
    """Test hook: clear ring only (sqlite is per-OMNI_STATE_DIR)."""
    with _LOCK:
        _RING.clear()
