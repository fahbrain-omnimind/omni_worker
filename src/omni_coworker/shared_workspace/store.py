"""shared_workspace.store — persistência quente (sqlite WAL) do barramento.

Orquestração runtime / Runtime orchestration:
    Write-through por evento via `put()` (chamado pelo bus); WAL permite
    leitores concorrentes sem bloquear o escritor único. `prune()` roda
    sob demanda (chamado periódico ou via /mesh/health ops).

Arquitetura / Architecture:
    `data/shared_workspace.sqlite`, tabela `events(ts, topic, payload_json)`
    com índice em (topic, ts). Caminho via $OMNI_STATE_DIR (default
    `data/` do repo), coerente com os demais stores do pacote.

Princípios teóricos invocados / Theoretical principles:
    Memória quente vs fria: sqlite WAL é a camada warm entre o ring
    buffer RAM (hot) e os arquivos de snapshot/Drive (cold).

pt-BR: persistência sqlite WAL por evento do barramento compartilhado.
"""

from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any

_LOCK = threading.RLock()  # reentrant: put/prune hold it while _con() re-acquires
_CON: sqlite3.Connection | None = None
RETENTION_S = float(os.getenv("OMNI_MESH_RETENTION_S", str(7 * 86400)))


def _db_path() -> Path:
    base = Path(os.getenv("OMNI_STATE_DIR", "data"))
    base.mkdir(parents=True, exist_ok=True)
    return base / "shared_workspace.sqlite"


def _con() -> sqlite3.Connection:
    global _CON
    with _LOCK:
        if _CON is None:
            _CON = sqlite3.connect(str(_db_path()), check_same_thread=False)
            _CON.execute("PRAGMA journal_mode=WAL")
            _CON.execute(
                "CREATE TABLE IF NOT EXISTS events("
                " ts REAL NOT NULL, topic TEXT NOT NULL, payload_json TEXT NOT NULL)"
            )
            _CON.execute(
                "CREATE INDEX IF NOT EXISTS ix_events_topic_ts ON events(topic, ts)"
            )
    return _CON


def put(ts: float, topic: str, payload: Any) -> None:
    """Persist one event (called by bus.publish on the write path)."""
    with _LOCK:
        _con().execute(
            "INSERT INTO events VALUES (?,?,?)", (ts, topic, json.dumps(payload))
        )
        _con().commit()


def history(topic: str, n: int = 50) -> list[dict]:
    """Last n persisted events on topic (newest last)."""
    rows = _con().execute(
        "SELECT ts, payload_json FROM events WHERE topic=? ORDER BY ts DESC LIMIT ?",
        (topic, n),
    ).fetchall()
    return [
        {"ts": ts, "topic": topic, "payload": json.loads(pj)}
        for ts, pj in reversed(rows)
    ]


def latest_per_topic() -> dict[str, dict]:
    """Newest persisted event per topic."""
    rows = _con().execute(
        "SELECT topic, ts, payload_json FROM events e1 WHERE ts = ("
        " SELECT MAX(ts) FROM events e2 WHERE e2.topic = e1.topic)"
    ).fetchall()
    return {
        t: {"ts": ts, "topic": t, "payload": json.loads(pj)} for t, ts, pj in rows
    }


def prune(older_than: float | None = None) -> int:
    """Drop events older than retention horizon; returns deleted count."""
    cutoff = (older_than if older_than is not None else time.time() - RETENTION_S)
    with _LOCK:
        cur = _con().execute("DELETE FROM events WHERE ts < ?", (cutoff,))
        _con().commit()
        return cur.rowcount


def _reset() -> None:
    """Test seam: reopen the db (e.g. after OMNI_STATE_DIR changed)."""
    global _CON
    with _LOCK:
        if _CON is not None:
            _CON.close()
        _CON = None
