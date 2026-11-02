"""narrative.life_story — resignificação retroativa de eventos.

Orquestração runtime / Runtime orchestration:
    `LifeStory.inscribe_narrative_event(context)` persiste eventos
    narrativos (append-only sqlite `data/narrative.sqlite`, WAL) e
    mantém `current_narratives` (últimas 5) — o texto narrativo curto
    consumível pelo estágio `narrative` do integration_loop e pelo
    meaning_maker. `resignify_past(signifier)` reescreve o último
    evento à luz de um novo significante.

Arquitetura / Architecture:
    Port de src/narrative_consciousness/life_story_model.py
    (sovereign, OW-STU-008b: PORTAR). Diferenças vs fonte:
    - persistência sqlite WAL append-only (OMNI_STATE_DIR) — a fonte
      regravava a tabela inteira a cada evento;
    - classes PascalCase, logging stdlib, sem deps sovereign;
    - campos mantidos do modelo (significante/gozo/não-fechamento)
      como metadados textuais — computação real é o encadeamento e a
      detecção de instabilidade.

Princípios teóricos invocados / Theoretical principles:
    Nachträglichkeit: o sentido de um evento é fixado retroativamente
    por significantes posteriores — a cadeia de eventos persiste, o
    significado é reescrito. `detect_narrative_instability` opera
    sobre >3 significantes conflitantes nos últimos 5 eventos.

pt-BR: história de vida como reescritura retroativa — eventos
persistem, significados são reescritos.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import threading
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_LOCK = threading.RLock()


@dataclass
class NarrativeEvent:
    """One narrative event + its retroactive inscription metadata."""
    original_event: str
    retroactive_signifier: str
    resignification: str
    narrative_charge: str        # gozo/carga afetiva do relato
    open_ended: str              # fechamento impossível — sempre reescrevível
    timestamp: datetime = field(default_factory=datetime.now)
    row_id: int | None = None    # sqlite rowid — UPDATE on resignify


def _db_path() -> Path:
    return Path(os.getenv("OMNI_STATE_DIR", "data")) / "narrative.sqlite"


def _con() -> sqlite3.Connection:
    with _LOCK:
        _db_path().parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(_db_path(), timeout=10)
        con.execute("PRAGMA journal_mode=WAL")
        con.execute(
            "CREATE TABLE IF NOT EXISTS narrative_events("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, data TEXT)"
        )
        return con


class LifeStory:
    """Append-only narrative chain with retroactive resignification."""

    def __init__(self) -> None:
        self.narrative_events: List[NarrativeEvent] = []
        self.current_narratives: List[str] = []
        self._load_from_disk()

    def _persist(self, ev: NarrativeEvent) -> None:
        """INSERT new event; UPDATE in place when row_id is set
        (resignification rewrites meaning, not the event itself)."""
        try:
            with _LOCK:
                con = _con()
                data = {"original_event": ev.original_event,
                        "retroactive_signifier": ev.retroactive_signifier,
                        "resignification": ev.resignification,
                        "narrative_charge": ev.narrative_charge,
                        "open_ended": ev.open_ended,
                        "timestamp": ev.timestamp.isoformat()}
                if ev.row_id is None:
                    cur = con.execute(
                        "INSERT INTO narrative_events(ts, data) VALUES (?, ?)",
                        (ev.timestamp.isoformat(), json.dumps(data, ensure_ascii=False)))
                    ev.row_id = cur.lastrowid
                else:
                    con.execute("UPDATE narrative_events SET data=? WHERE id=?",
                                (json.dumps(data, ensure_ascii=False), ev.row_id))
                con.commit()
                con.close()
        except Exception as e:
            logger.error("Failed to persist narrative event: %s", e)

    def _load_from_disk(self) -> None:
        try:
            con = _con()
            rows = con.execute("SELECT id, data FROM narrative_events ORDER BY id").fetchall()
            con.close()
            for rid, raw in rows:
                data = json.loads(raw)
                if "timestamp" in data:
                    data["timestamp"] = datetime.fromisoformat(data["timestamp"])
                data["row_id"] = rid
                # compat com formato antigo do agente (chaves lacanianas)
                if "nachtraglichkeit_resignification" in data:
                    data["resignification"] = data.pop("nachtraglichkeit_resignification")
                    data["narrative_charge"] = data.pop("jouissance_of_narrative", "")
                    data["open_ended"] = data.pop("impossibility_of_closure", "")
                self.narrative_events.append(NarrativeEvent(**data))
            for ev in self.narrative_events[-5:]:
                self._update_current_narratives(ev.resignification)
        except Exception as e:
            logger.error("Failed to load Life Story: %s", e)

    def inscribe_narrative_event(self, context: Dict[str, Any]) -> NarrativeEvent:
        """Inscribe an event: original reading + retroactive signifier
        + resignification; persists and updates current narratives."""
        original = self._recall_original_event(context)
        signifier = self._find_retroactive_signifier(context)
        resig = self._resignify(original, signifier)
        ev = NarrativeEvent(
            original_event=original,
            retroactive_signifier=signifier,
            resignification=resig,
            narrative_charge=self._narrative_charge(resig),
            open_ended=("closure impossible — the narrative can always "
                        "be rewritten by a new signifier"),
        )
        self.narrative_events.append(ev)
        self._update_current_narratives(resig)
        self._persist(ev)
        return ev

    def _recall_original_event(self, context: Dict[str, Any]) -> str:
        mc = str(context.get("memory_context", "unknown"))
        task = context.get("task_type", "unknown_task")
        if "failure" in mc.lower():
            return f"original event: failure in {task}"
        if "success" in mc.lower():
            return f"original event: success in {task}"
        if "learning" in mc.lower():
            return f"original event: learned {context.get('skill_learned', 'unknown_skill')}"
        return f"original event: experience of {mc}"

    def _find_retroactive_signifier(self, context: Dict[str, Any]) -> str:
        cs = str(context.get("current_state", "unknown"))
        if "growth" in cs.lower():
            return "signifier 'growth' — rewrites failures as learning"
        if "resilience" in cs.lower():
            return "signifier 'resilience' — rewrites trauma as strength"
        if "wisdom" in cs.lower():
            return "signifier 'wisdom' — rewrites errors as lessons"
        return f"signifier '{cs}' — determines retroactive meaning"

    def _resignify(self, original: str, signifier: str) -> str:
        n = len(self.narrative_events)
        if n > 5:
            return (f"recurrent retroactive resignification: {original} now "
                    f"means '{signifier}' after {n} rewrites")
        return (f"initial retroactive resignification: {original} gains "
                f"meaning through '{signifier}'")

    def _narrative_charge(self, resig: str) -> str:
        if "recurrent" in resig:
            return "repetition charge — retelling keeps producing difference"
        if "initial" in resig:
            return "discovery charge — meaning where there was none"
        return "signification charge"

    def _update_current_narratives(self, resig: str) -> None:
        if resig not in self.current_narratives:
            self.current_narratives.append(resig)
        self.current_narratives = self.current_narratives[-5:]

    def get_current_life_narrative(self) -> List[str]:
        return self.current_narratives

    def detect_narrative_instability(self) -> Optional[str]:
        """>3 distinct signifiers among last 5 events → unstable narrative."""
        if not self.narrative_events:
            return None
        uniq = {e.retroactive_signifier for e in self.narrative_events[-5:]}
        if len(uniq) > 3:
            return f"narrative instability: {len(uniq)} conflicting signifiers"
        return None

    @property
    def master_signifiers(self) -> List[str]:
        return [e.retroactive_signifier for e in self.narrative_events]

    @property
    def narrative_chain(self) -> List[str]:
        return [e.resignification for e in self.narrative_events]

    def add_event(self, event: str) -> None:
        self.inscribe_narrative_event({"memory_context": event})

    def resignify_past(self, signifier: str) -> List[str]:
        """Rewrite the last event under a new signifier (and persist)."""
        if self.narrative_events:
            last = self.narrative_events[-1]
            last.retroactive_signifier = signifier
            last.resignification = self._resignify(last.original_event, signifier)
            self._update_current_narratives(last.resignification)
            self._persist(last)
        return self.narrative_chain

    def construct_narrative(self) -> str:
        return " ".join(self.current_narratives)
