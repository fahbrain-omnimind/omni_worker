"""psychology.hawking_motivation — evaporação de conhecimento não usado → urgência.

Orquestração runtime / Runtime orchestration:
    `HawkingMotivationEngine` registra KnowledgeItem, marca uso, adiciona
    correlações e evapora conhecimento não usado gerando sinais de urgência.
    Persistência sqlite em OMNI_STATE_DIR/hawking.sqlite (registry sobrevive
    restart). Decay reusa `omni_coworker.store.evaporation.evaporation_score`.

Arquitetura / Architecture:
    Port de src/psychology/motivation/hawking_motivation.py (sovereign,
    OW-STU-008b: PORTAR). Mudanças vs fonte: (a) decay via evaporation_score
    (REUSE-A, sem duplicar decaimento); (b) persistência sqlite WAL.

Princípios teóricos invocados / Theoretical principles:
    Conhecimento não usado evapora (radiação Hawking); uso preserva;
    informação preservada em correlações (paradoxo da informação).

pt-BR: registro de conhecimento com evaporação e urgência persistente.
"""

from __future__ import annotations

import json
import logging
import os
import random
import sqlite3
import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from omni_coworker.store.evaporation import evaporation_score

logger = logging.getLogger(__name__)

HAWKING_CONSTANT = 1.0
MIN_TEMPERATURE = 0.001
MAX_TEMPERATURE = 10.0

_LOCK = threading.RLock()


def _db_path() -> Path:
    return Path(os.getenv("OMNI_STATE_DIR", "data")) / "hawking.sqlite"


def _con() -> sqlite3.Connection:
    with _LOCK:
        _db_path().parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(_db_path(), timeout=10)
        con.execute("PRAGMA journal_mode=WAL")
        con.execute(
            "CREATE TABLE IF NOT EXISTS knowledge("
            "id TEXT PRIMARY KEY, content TEXT, mass REAL, last_used TEXT,"
            "use_count INTEGER, correlations TEXT, creation_time TEXT)"
        )
        con.execute(
            "CREATE TABLE IF NOT EXISTS evap_history("
            "knowledge_id TEXT, mass_lost REAL, correlations TEXT,"
            "frustration REAL, motivation REAL, ts TEXT)"
        )
        return con


def _dt(s: str | None) -> datetime:
    if not s:
        return datetime.now(UTC)
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt
    except Exception:  # noqa: BLE001
        return datetime.now(UTC)


@dataclass
class KnowledgeItem:
    content: str
    mass: float
    last_used: datetime
    use_count: int = 0
    correlations: list[str] = field(default_factory=list)
    creation_time: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class EvaporationEvent:
    knowledge_id: str
    mass_lost: float
    correlations_preserved: list[str]
    frustration_energy: float
    motivation_boost: float
    timestamp: datetime


class HawkingMotivationEngine:
    def __init__(self, base_temperature: float = 1.0, evaporation_threshold_days: float = 7.0,
                 correlation_strength: float = 0.7) -> None:
        self.temperature = base_temperature
        self.evaporation_threshold = timedelta(days=evaporation_threshold_days)
        self.correlation_strength = correlation_strength
        self.knowledge_base: dict[str, KnowledgeItem] = {}
        self.evaporation_history: list[EvaporationEvent] = []
        self.evaporation_rate = self._calculate_rate()
        self._load()
        logger.info(f"HawkingMotivationEngine initialized: T={base_temperature:.2f}")

    def _calculate_rate(self) -> float:
        temp = max(MIN_TEMPERATURE, min(self.temperature, MAX_TEMPERATURE))
        rate = HAWKING_CONSTANT * temp / MAX_TEMPERATURE
        return float(max(0.0, min(rate, 1.0)))

    def _load(self) -> None:
        try:
            con = _con()
            for r in con.execute("SELECT id,content,mass,last_used,use_count,correlations,creation_time FROM knowledge").fetchall():
                self.knowledge_base[r[0]] = KnowledgeItem(
                    content=r[1], mass=r[2], last_used=_dt(r[3]), use_count=r[4],
                    correlations=json.loads(r[5] or "[]"), creation_time=_dt(r[6]))
            for r in con.execute("SELECT knowledge_id,mass_lost,correlations,frustration,motivation,ts FROM evap_history").fetchall():
                self.evaporation_history.append(EvaporationEvent(
                    knowledge_id=r[0], mass_lost=r[1], correlations_preserved=json.loads(r[2] or "[]"),
                    frustration_energy=r[3], motivation_boost=r[4], timestamp=_dt(r[5])))
            con.close()
        except Exception:  # noqa: BLE001, S110
            pass

    def _save_item(self, kid: str) -> None:
        item = self.knowledge_base.get(kid)
        if not item:
            return
        try:
            con = _con()
            with con:
                con.execute(
                    "INSERT OR REPLACE INTO knowledge VALUES(?,?,?,?,?,?,?)",
                    (kid, item.content, item.mass, item.last_used.isoformat(),
                     item.use_count, json.dumps(item.correlations), item.creation_time.isoformat()))
            con.close()
        except Exception:  # noqa: BLE001, S110
            pass

    def _remove_item(self, kid: str) -> None:
        try:
            con = _con()
            with con:
                con.execute("DELETE FROM knowledge WHERE id=?", (kid,))
            con.close()
        except Exception:  # noqa: BLE001, S110
            pass

    def add_knowledge(self, knowledge_id: str, content: str, mass: float = 1.0) -> None:
        item = KnowledgeItem(content=content, mass=mass, last_used=datetime.now(UTC))
        self.knowledge_base[knowledge_id] = item
        self._save_item(knowledge_id)

    def use_knowledge(self, knowledge_id: str) -> bool:
        if knowledge_id not in self.knowledge_base:
            return False
        item = self.knowledge_base[knowledge_id]
        item.last_used = datetime.now(UTC)
        item.use_count += 1
        self._save_item(knowledge_id)
        return True

    def add_correlation(self, knowledge_id: str, related_id: str, bidirectional: bool = True) -> None:
        if knowledge_id in self.knowledge_base:
            item = self.knowledge_base[knowledge_id]
            if related_id not in item.correlations:
                item.correlations.append(related_id)
            self._save_item(knowledge_id)
        if bidirectional and related_id in self.knowledge_base:
            related = self.knowledge_base[related_id]
            if knowledge_id not in related.correlations:
                related.correlations.append(knowledge_id)
            self._save_item(related_id)

    def _extract_correlations(self, item: KnowledgeItem) -> list[str]:
        preserved = []
        for corr_id in item.correlations:
            if random.random() < self.correlation_strength:
                preserved.append(corr_id)
        return preserved

    def _compute_frustration(self, item: KnowledgeItem, time_unused: timedelta) -> float:
        age_factor = (datetime.now(UTC) - item.creation_time).days
        recency_frustration = 1.0 / max(age_factor, 1.0)
        mass_frustration = item.mass / 10.0
        usage_frustration = 1.0 / max(item.use_count + 1, 1.0)
        total = (recency_frustration + mass_frustration + usage_frustration) / 3.0
        return float(max(0.0, min(total, 1.0)))

    def _generate_urgency(self, correlations: list[str]) -> float:
        urgency = len(correlations) / 10.0
        for corr_id in correlations:
            if corr_id in self.knowledge_base:
                corr_item = self.knowledge_base[corr_id]
                time_unused = (datetime.now(UTC) - corr_item.last_used).total_seconds()
                if time_unused > self.evaporation_threshold.total_seconds() * 0.5:
                    urgency += 0.1
        return float(max(0.0, min(urgency, 1.0)))

    def evaporate_unused_knowledge(self, current_time: datetime | None = None) -> tuple[list[str], dict[str, Any]]:
        if current_time is None:
            current_time = datetime.now(UTC)
        evaporated_ids: list[str] = []
        total_frustration = 0.0
        total_motivation = 0.0
        total_mass_lost = 0.0
        threshold_seconds = self.evaporation_threshold.total_seconds()

        for knowledge_id, item in list(self.knowledge_base.items()):
            time_unused = current_time - item.last_used
            if time_unused > self.evaporation_threshold:
                score = evaporation_score(
                    {"last_used_ts": item.last_used, "use_count": item.use_count,
                     "half_life": threshold_seconds}, now=current_time)
                evap_prob = min(score, 1.0)
                if random.random() < evap_prob:
                    correlations = self._extract_correlations(item)
                    frustration = self._compute_frustration(item, time_unused)
                    motivation = self._generate_urgency(correlations)
                    event = EvaporationEvent(
                        knowledge_id=knowledge_id, mass_lost=item.mass,
                        correlations_preserved=correlations, frustration_energy=frustration,
                        motivation_boost=motivation, timestamp=current_time)
                    self.evaporation_history.append(event)
                    total_frustration += frustration
                    total_motivation += motivation
                    total_mass_lost += item.mass
                    del self.knowledge_base[knowledge_id]
                    self._remove_item(knowledge_id)
                    # persist event
                    try:
                        con = _con()
                        with con:
                            con.execute("INSERT INTO evap_history VALUES(?,?,?,?,?,?)",
                                        (knowledge_id, item.mass, json.dumps(correlations),
                                         frustration, motivation, current_time.isoformat()))
                        con.close()
                    except Exception:  # noqa: BLE001, S110
                        pass
                    evaporated_ids.append(knowledge_id)

        motivation_data = {
            "evaporated_count": len(evaporated_ids),
            "total_mass_lost": total_mass_lost,
            "frustration": total_frustration,
            "motivation": total_motivation,
            "urgency_factor": (len(evaporated_ids) / 10.0 if evaporated_ids else 0.0),
            "correlations_at_risk": self._identify_at_risk_correlations(),
        }
        return evaporated_ids, motivation_data

    def _identify_at_risk_correlations(self) -> list[str]:
        at_risk = []
        current_time = datetime.now(UTC)
        for knowledge_id, item in self.knowledge_base.items():
            time_unused = current_time - item.last_used
            if time_unused > self.evaporation_threshold * 0.5:
                at_risk.append(knowledge_id)
        return at_risk

    def adjust_temperature(self, new_temperature: float) -> None:
        self.temperature = max(MIN_TEMPERATURE, min(new_temperature, MAX_TEMPERATURE))
        self.evaporation_rate = self._calculate_rate()

    def get_statistics(self) -> dict[str, Any]:
        at_risk = self._identify_at_risk_correlations()
        return {
            "total_knowledge": len(self.knowledge_base),
            "temperature": self.temperature,
            "evaporation_rate": self.evaporation_rate,
            "total_evaporated": len(self.evaporation_history),
            "at_risk_count": len(at_risk),
            "at_risk_ids": at_risk,
            "average_mass": (sum(i.mass for i in self.knowledge_base.values()) / len(self.knowledge_base) if self.knowledge_base else 0.0),
            "average_use_count": (sum(i.use_count for i in self.knowledge_base.values()) / len(self.knowledge_base) if self.knowledge_base else 0.0),
        }

    def get_knowledge_status(self, knowledge_id: str) -> dict[str, Any] | None:
        if knowledge_id not in self.knowledge_base:
            return None
        item = self.knowledge_base[knowledge_id]
        current_time = datetime.now(UTC)
        time_unused = current_time - item.last_used
        evaporation_risk = time_unused.total_seconds() / self.evaporation_threshold.total_seconds()
        evaporation_risk = min(evaporation_risk, 1.0)
        return {
            "content": item.content, "mass": item.mass,
            "last_used": item.last_used.isoformat(), "use_count": item.use_count,
            "correlations": item.correlations, "time_unused_days": time_unused.days,
            "evaporation_risk": evaporation_risk,
            "status": "critical" if evaporation_risk > 0.8 else "at_risk" if evaporation_risk > 0.5 else "safe",
        }
