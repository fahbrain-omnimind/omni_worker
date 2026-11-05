"""Somatic store: persisted probe telemetry.

English: SQLite WAL store for host telemetry probes
(`probes(id, ts, cpu, ram_used_gb, ram_total_gb, swap_gb, load1,
extra_json)`). Clean implementation — the canonical
`src.infrastructure.somatic_mesh_sql` is entangled with production paths
(data/monitor, Rust engine, parquet dual-writer), so it is not reused.
pt-BR: Store SQLite WAL para sondas de telemetria do host
(`probes(id, ts, cpu, ram_used_gb, ram_total_gb, swap_gb, load1,
extra_json)`). Implementação limpa — o canônico
`src.infrastructure.somatic_mesh_sql` está entrelaçado com caminhos de
produção (data/monitor, engine Rust, dual-writer parquet), por isso não
é reutilizado.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

__all__ = ["SomaticStore"]

_COLUMNS = ("cpu", "ram_used_gb", "ram_total_gb", "swap_gb", "load1")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS probes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT,
    cpu REAL,
    ram_used_gb REAL,
    ram_total_gb REAL,
    swap_gb REAL,
    load1 REAL,
    extra_json TEXT
)
"""


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _as_float(value: Any) -> float | None:
    """Coerce a value to float; None when not numeric.

    English: Lists/tuples (e.g. os.getloadavg()) use their first element.
    pt-BR: Listas/tuplas (ex.: os.getloadavg()) usam o primeiro elemento.
    """
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        value = value[0] if value else None
        if value is None:
            return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


class SomaticStore:
    """SQLite-backed store for probe snapshots.

    English: WAL mode, one connection per write (pattern of
    `store/node_db.py`).
    pt-BR: Modo WAL, uma conexão por escrita (padrão de
    `store/node_db.py`).
    """

    def __init__(self, path: str | Path = "data/somatic_probes.sqlite") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _init(self) -> None:
        """Create the probes table if needed."""
        with sqlite3.connect(self.path) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute(_SCHEMA)
            conn.commit()

    def record(self, probe_dict: dict[str, Any]) -> int:
        """Persist a probe dict; returns the row id.

        English: Maps cpu_percent->cpu, swap_used_gb->swap_gb,
        load_avg->load1; unknown keys go to extra_json.
        pt-BR: Mapeia cpu_percent->cpu, swap_used_gb->swap_gb,
        load_avg->load1; chaves desconhecidas vão para extra_json.
        """
        standard_keys = {
            "cpu",
            "cpu_percent",
            "ram_used_gb",
            "ram_total_gb",
            "swap_gb",
            "swap_used_gb",
            "load1",
            "load_avg",
            "ts",
            "id",
        }
        extra = {k: v for k, v in probe_dict.items() if k not in standard_keys}
        row = (
            probe_dict.get("ts") or _now(),
            _as_float(probe_dict.get("cpu_percent", probe_dict.get("cpu"))),
            _as_float(probe_dict.get("ram_used_gb")),
            _as_float(probe_dict.get("ram_total_gb")),
            _as_float(probe_dict.get("swap_used_gb", probe_dict.get("swap_gb"))),
            _as_float(probe_dict.get("load_avg", probe_dict.get("load1"))),
            json.dumps(extra, ensure_ascii=False, default=str) if extra else None,
        )
        with sqlite3.connect(self.path) as conn:
            cur = conn.execute(
                "INSERT INTO probes(ts, cpu, ram_used_gb, ram_total_gb, swap_gb, load1, extra_json)"
                " VALUES (?,?,?,?,?,?,?)",
                row,
            )
            conn.commit()
            return int(cur.lastrowid)

    def recent(self, n: int = 10) -> list[dict[str, Any]]:
        """Return the most recent n probes (chronological)."""
        n = max(0, int(n))
        with sqlite3.connect(self.path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT id, ts, cpu, ram_used_gb, ram_total_gb, swap_gb, load1, extra_json"
                " FROM probes ORDER BY id DESC LIMIT ?",
                (n,),
            ).fetchall()
        probes = []
        for row in reversed(rows):
            probe = {
                "id": row["id"],
                "ts": row["ts"],
                "cpu": row["cpu"],
                "ram_used_gb": row["ram_used_gb"],
                "ram_total_gb": row["ram_total_gb"],
                "swap_gb": row["swap_gb"],
                "load1": row["load1"],
            }
            if row["extra_json"]:
                try:
                    probe["extra"] = json.loads(row["extra_json"])
                except Exception:  # noqa: BLE001
                    probe["extra"] = row["extra_json"]
            probes.append(probe)
        return probes

    def summary(self, n: int = 100) -> dict[str, Any]:
        """Means over the last n probes.

        English: Returns count + average for each numeric column.
        pt-BR: Retorna count + média para cada coluna numérica.
        """
        probes = self.recent(n)
        if not probes:
            return {"count": 0, "window": n}

        def _mean(key: str) -> float | None:
            values = [p[key] for p in probes if p.get(key) is not None]
            return round(sum(values) / len(values), 3) if values else None

        return {
            "count": len(probes),
            "window": n,
            **{col: _mean(col) for col in _COLUMNS},
        }