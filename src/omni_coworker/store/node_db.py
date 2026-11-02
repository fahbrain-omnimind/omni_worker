"""Node DB (SQLite WAL).

English: Atomic per-write connections; reuses src.storage.
pt-BR: Conexões atômicas por escrita; reutiliza src.storage.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path


class NodeDB:
    """Minimal SQLite node store.

    English: WAL mode, one connection per write.
    pt-BR: Modo WAL, uma conexão por escrita.
    """

    def __init__(self, path: str = "data/node.db"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def init(self) -> None:
        """Initialize schema.

        English: Creates missions table.
        pt-BR: Cria tabela de missões.
        """
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
            conn.commit()

    def add_artifact(
        self, task_id: str, kind: str, content: str, verdict: str = "", ts: str = ""
    ) -> int:
        """Persist a task artifact.

        English: Stores deliverable content with its verdict.
        pt-BR: Armazena conteúdo entregável com seu veredito.
        """
        from datetime import datetime, timezone

        ts = ts or datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.path) as conn:
            cur = conn.execute(
                "INSERT INTO artifacts(task_id, kind, content, verdict, ts) VALUES (?,?,?,?,?)",
                (task_id, kind, content, verdict, ts),
            )
            conn.commit()
            return int(cur.lastrowid)

    def list_artifacts(self, task_id: str | None = None, limit: int = 20) -> list[dict]:
        """List persisted artifacts.

        English: Recent artifacts, optionally filtered by task.
        pt-BR: Artefatos recentes, opcionalmente filtrados por tarefa.
        """
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
        """Add a mission spec.

        English: Inserts and returns row id.
        pt-BR: Insere e retorna o id da linha.
        """
        with sqlite3.connect(self.path) as conn:
            cur = conn.execute("INSERT INTO missions(spec) VALUES (?)", (spec,))
            conn.commit()
            return int(cur.lastrowid)


    def get_mission(self, mission_id: int) -> dict | None:
        """Get a mission by id.
        
        English: Retrieves mission.
        pt-BR: Recupera missão.
        """
        with sqlite3.connect(self.path) as conn:
            cur = conn.execute("SELECT id, spec FROM missions WHERE id = ?", (mission_id,))
            row = cur.fetchone()
            if row:
                return {"id": row[0], "spec": row[1]}
            return None

    def list_missions(self, limit: int = 10) -> list[dict]:
        """List missions.
        
        English: Lists recent missions.
        pt-BR: Lista missões recentes.
        """
        with sqlite3.connect(self.path) as conn:
            cur = conn.execute("SELECT id, spec FROM missions ORDER BY id DESC LIMIT ?", (limit,))
            return [{"id": row[0], "spec": row[1]} for row in cur.fetchall()]
