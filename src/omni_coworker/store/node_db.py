"""Node DB (SQLite WAL).

English: Atomic per-write connections; persists artifacts, missions, and
governance state (trust_scores, trust_events, quarantine_records,
circuit_breakers — closing P7 / OW-STU-012 §3).
pt-BR: Conexões atômicas por escrita; persiste artefatos, missões e
estado de governança (trust_scores, trust_events, quarantine_records,
circuit_breakers — fechando P7 / OW-STU-012 §3).
"""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class NodeDB:
    """Minimal SQLite node store (WAL mode, atomic per-write connections)."""

    def __init__(self, path: str | None = None):
        if path is None:
            path = str(Path(os.getenv("OMNI_STATE_DIR", "data")) / "node.db")
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def init(self) -> None:
        """Initialize schema (missions, artifacts, and P7 governance tables)."""
        with sqlite3.connect(self.path) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute(
                "CREATE TABLE IF NOT EXISTS missions (id INTEGER PRIMARY KEY, spec TEXT)"
            )
            conn.execute(
                """CREATE TABLE IF NOT EXISTS artifacts (
                    id INTEGER PRIMARY KEY,
                    task_id TEXT,
                    kind TEXT,
                    content TEXT,
                    verdict TEXT,
                    ts TEXT
                )"""
            )
            conn.execute(
                """CREATE TABLE IF NOT EXISTS trust_scores (
                    agent TEXT PRIMARY KEY,
                    score REAL NOT NULL,
                    updated_at TEXT NOT NULL
                )"""
            )
            conn.execute(
                """CREATE TABLE IF NOT EXISTS trust_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event TEXT NOT NULL,
                    agent TEXT NOT NULL,
                    delta REAL NOT NULL,
                    before_score REAL NOT NULL,
                    after_score REAL NOT NULL,
                    ts TEXT NOT NULL
                )"""
            )
            conn.execute(
                """CREATE TABLE IF NOT EXISTS quarantine_records (
                    component_id TEXT PRIMARY KEY,
                    reason TEXT NOT NULL,
                    evidence_json TEXT NOT NULL,
                    ts TEXT NOT NULL
                )"""
            )
            conn.execute(
                """CREATE TABLE IF NOT EXISTS circuit_breakers (
                    name TEXT PRIMARY KEY,
                    state TEXT NOT NULL,
                    failure_count INTEGER NOT NULL,
                    last_failure_time REAL,
                    last_success_time REAL,
                    updated_at TEXT NOT NULL
                )"""
            )
            conn.commit()

    def add_artifact(
        self, task_id: str, kind: str, content: str, verdict: str = "", ts: str = ""
    ) -> int:
        """Persist a task artifact."""
        ts = ts or datetime.now(timezone.utc).isoformat()
        self.init()
        with sqlite3.connect(self.path) as conn:
            cur = conn.execute(
                "INSERT INTO artifacts(task_id, kind, content, verdict, ts) VALUES (?,?,?,?,?)",
                (task_id, kind, content, verdict, ts),
            )
            conn.commit()
            return int(cur.lastrowid)

    def list_artifacts(self, task_id: str | None = None, limit: int = 20) -> list[dict]:
        """List persisted artifacts."""
        self.init()
        with sqlite3.connect(self.path) as conn:
            if task_id:
                cur = conn.execute(
                    "SELECT id, task_id, kind, verdict, ts FROM artifacts WHERE task_id=? ORDER BY id DESC LIMIT ?",
                    (task_id, limit),
                )
            else:
                cur = conn.execute(
                    "SELECT id, task_id, kind, verdict, ts FROM artifacts ORDER BY id DESC LIMIT ?",
                    (limit,),
                )
            return [
                {"id": r[0], "task_id": r[1], "kind": r[2], "verdict": r[3], "ts": r[4]}
                for r in cur.fetchall()
            ]

    def add_mission(self, spec: str) -> int:
        """Add a mission spec."""
        self.init()
        with sqlite3.connect(self.path) as conn:
            cur = conn.execute("INSERT INTO missions(spec) VALUES (?)", (spec,))
            conn.commit()
            return int(cur.lastrowid)

    def get_mission(self, mission_id: int) -> dict | None:
        """Get a mission by id."""
        self.init()
        with sqlite3.connect(self.path) as conn:
            cur = conn.execute("SELECT id, spec FROM missions WHERE id = ?", (mission_id,))
            row = cur.fetchone()
            if row:
                return {"id": row[0], "spec": row[1]}
            return None

    def list_missions(self, limit: int = 10) -> list[dict]:
        """List missions."""
        self.init()
        with sqlite3.connect(self.path) as conn:
            cur = conn.execute("SELECT id, spec FROM missions ORDER BY id DESC LIMIT ?", (limit,))
            return [{"id": row[0], "spec": row[1]} for row in cur.fetchall()]

    # ── P7: SQL-First Governance Persistence ────────────────────────────────

    def upsert_trust_score(self, agent: str, score: float, ts: str = "") -> None:
        """Persist per-agent trust score in node.db."""
        ts = ts or datetime.now(timezone.utc).isoformat()
        self.init()
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """INSERT INTO trust_scores(agent, score, updated_at)
                   VALUES (?, ?, ?)
                   ON CONFLICT(agent) DO UPDATE SET score=excluded.score, updated_at=excluded.updated_at""",
                (str(agent), float(score), ts),
            )
            conn.commit()

    def get_trust_scores(self) -> dict[str, float]:
        """Load all persisted trust scores from node.db."""
        self.init()
        with sqlite3.connect(self.path) as conn:
            cur = conn.execute("SELECT agent, score FROM trust_scores")
            return {str(r[0]): float(r[1]) for r in cur.fetchall()}

    def append_trust_event(self, record: dict[str, Any]) -> int:
        """Persist a trust delta event in node.db."""
        self.init()
        ts = str(record.get("ts") or datetime.now(timezone.utc).isoformat())
        with sqlite3.connect(self.path) as conn:
            cur = conn.execute(
                """INSERT INTO trust_events(event, agent, delta, before_score, after_score, ts)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    str(record.get("event", "")),
                    str(record.get("agent", "CodeAgent")),
                    float(record.get("delta", 0.0)),
                    float(record.get("before", 0.5)),
                    float(record.get("after", 0.5)),
                    ts,
                ),
            )
            conn.commit()
            return int(cur.lastrowid)

    def list_trust_events(self, limit: int = 50) -> list[dict[str, Any]]:
        """List recent trust events from node.db."""
        self.init()
        with sqlite3.connect(self.path) as conn:
            cur = conn.execute(
                """SELECT event, agent, delta, before_score, after_score, ts
                   FROM trust_events ORDER BY id DESC LIMIT ?""",
                (limit,),
            )
            return [
                {
                    "event": r[0],
                    "agent": r[1],
                    "delta": float(r[2]),
                    "before": float(r[3]),
                    "after": float(r[4]),
                    "ts": r[5],
                }
                for r in cur.fetchall()
            ]

    def upsert_quarantine(
        self, component_id: str, reason: str, evidence: dict[str, Any] | None = None, ts: str = ""
    ) -> None:
        """Persist a quarantine record in node.db."""
        ts = ts or datetime.now(timezone.utc).isoformat()
        self.init()
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """INSERT INTO quarantine_records(component_id, reason, evidence_json, ts)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(component_id) DO UPDATE SET
                       reason=excluded.reason,
                       evidence_json=excluded.evidence_json,
                       ts=excluded.ts""",
                (str(component_id), str(reason), json.dumps(evidence or {}, ensure_ascii=False, default=str), ts),
            )
            conn.commit()

    def delete_quarantine(self, component_id: str) -> bool:
        """Remove a quarantine record from node.db."""
        self.init()
        with sqlite3.connect(self.path) as conn:
            cur = conn.execute(
                "DELETE FROM quarantine_records WHERE component_id = ?",
                (str(component_id),),
            )
            conn.commit()
            return cur.rowcount > 0

    def get_quarantine_records(self) -> dict[str, dict[str, Any]]:
        """Load all quarantine records from node.db."""
        self.init()
        out: dict[str, dict[str, Any]] = {}
        with sqlite3.connect(self.path) as conn:
            cur = conn.execute("SELECT component_id, reason, evidence_json, ts FROM quarantine_records")
            for cid, reason, ev_json, ts in cur.fetchall():
                try:
                    ev = json.loads(ev_json) if ev_json else {}
                except Exception:
                    ev = {}
                out[str(cid)] = {
                    "component_id": str(cid),
                    "reason": str(reason),
                    "evidence": ev,
                    "ts": str(ts),
                }
        return out

    def upsert_circuit_breaker(
        self,
        name: str,
        state: str,
        failure_count: int,
        last_failure_time: float | None,
        last_success_time: float | None,
        ts: str = "",
    ) -> None:
        """Persist named CircuitBreaker state in node.db."""
        ts = ts or datetime.now(timezone.utc).isoformat()
        self.init()
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """INSERT INTO circuit_breakers(name, state, failure_count, last_failure_time, last_success_time, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?)
                   ON CONFLICT(name) DO UPDATE SET
                       state=excluded.state,
                       failure_count=excluded.failure_count,
                       last_failure_time=excluded.last_failure_time,
                       last_success_time=excluded.last_success_time,
                       updated_at=excluded.updated_at""",
                (str(name), str(state), int(failure_count), last_failure_time, last_success_time, ts),
            )
            conn.commit()

    def get_circuit_breakers(self) -> dict[str, dict[str, Any]]:
        """Load all persisted CircuitBreakers from node.db."""
        self.init()
        out: dict[str, dict[str, Any]] = {}
        with sqlite3.connect(self.path) as conn:
            cur = conn.execute(
                "SELECT name, state, failure_count, last_failure_time, last_success_time FROM circuit_breakers"
            )
            for name, state, fc, lft, lst in cur.fetchall():
                out[str(name)] = {
                    "state": str(state),
                    "failure_count": int(fc),
                    "last_failure_time": float(lft) if lft is not None else None,
                    "last_success_time": float(lst) if lst is not None else None,
                }
        return out
