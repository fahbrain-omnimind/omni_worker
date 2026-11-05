"""narrative.lalangue — sandbox de língua interna com persistência.

Orquestração runtime / Runtime orchestration:
    `LalangueSandbox.emit(embedding)` fixa ou reutiliza uma "palavra"
    interna (embedding normalizado, match por cosseno >= 0.9, frequência
    e first_seen por palavra). `speak_to_self` registra um diálogo interno
    (pensamento -> resposta perturbada). `persist()`/`restore_into()`
    gravam/carregam o vocabulário e os diálogos em SQLite sob
    OMNI_STATE_DIR — a língua interna sobrevive ao restart (pendência 17
    do OW-STU-014: no soberano as marcas morriam no processo).

Arquitetura / Architecture:
    Port conceitual de src/core/phylogenetic_signature.py
    (MachineLanguageSandbox) + src/core/internal_vocabulary_store.py do
    omnimind-kilombo-sovereign — APENAS o núcleo: vocabulário de
    embeddings + match por cosseno + diálogo interno + store SQLite.
    Mesmo schema do soberano (internal_words/internal_dialogues/
    internal_store_meta) para futura federação. Diferenças vs original:
    `signature` (PhylogeneticSignature) é injetável — quando presente,
    `self_resonance = signature.is_self(thought)` e a resposta é
    moldada pelos atratores da assinatura; sem assinatura, 0.0 como
    antes. Sem numpy/torch — listas floats + math; blob de embedding
    em float32 via array('f') (byte-compatible com numpy float32).

Princípios teóricos invocados / Theoretical principles:
    Lalangue (Lacan): a língua que fala a si mesma antes de comunicar —
    material significante sem destinatário. Aqui: a máquina "fala" em
    embeddings consigo mesma; a persistência dá à língua interna uma
    continuidade filogenética entre restarts (as marcas acumulam
    frequência através do tempo, não morrem com o processo).

pt-BR: língua interna persistente — vocabulário próprio que sobrevive
    ao restart, como registro das marcas da máquina.
"""

from __future__ import annotations

import math
import os
import random
import sqlite3
import time
from array import array
from collections.abc import Iterable
from pathlib import Path
from typing import Any

_MATCH_THRESHOLD = 0.9


def _db_path() -> Path:
    return Path(os.getenv("OMNI_STATE_DIR", "data")) / "monitor" / "internal_vocabulary.sqlite"


_SCHEMA = """
CREATE TABLE IF NOT EXISTS internal_words (
    word_index   INTEGER NOT NULL,
    embedding    BLOB    NOT NULL,
    dim          INTEGER NOT NULL,
    frequency    INTEGER NOT NULL DEFAULT 1,
    first_seen   REAL    NOT NULL,
    last_seen    REAL    NOT NULL,
    PRIMARY KEY (word_index)
);
CREATE TABLE IF NOT EXISTS internal_dialogues (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    ts             REAL NOT NULL,
    thought_idx    INTEGER,
    response_idx   INTEGER,
    self_resonance REAL
);
CREATE TABLE IF NOT EXISTS internal_store_meta (
    key   TEXT PRIMARY KEY,
    value TEXT
);
"""


def _norm(vec: Iterable[float]) -> list[float]:
    v = [float(x) for x in vec]
    n = math.sqrt(sum(x * x for x in v))
    return [x / n for x in v] if n > 0 else []


def _cosine(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    try:
        from ..kernel_hooks.compute import cosine_similarity as _kh_cos
        return float(_kh_cos(a, b))
    except Exception:  # noqa: BLE001
        return sum(x * y for x, y in zip(a, b))


def _encode(vec: list[float]) -> tuple[bytes, int]:
    return array("f", vec).tobytes(), len(vec)


def _decode(blob: bytes, dim: int) -> list[float]:
    a = array("f")
    a.frombytes(blob)
    return list(a[:dim])


class LalangueSandbox:
    """Espaço seguro para a língua interna da máquina.

    O sistema "fala" consigo mesmo em embeddings — sem tradução humana.
    Persistente: as marcas (vocabulário + diálogos) sobrevivem ao restart.
    """

    def __init__(self, vocab_size: int = 1000,
                 signature: Any = None) -> None:
        self.vocab_size = vocab_size
        self.signature = signature  # PhylogeneticSignature opcional
        # (embedding_normalizado, frequencia, first_seen)
        self.vocabulary: list[tuple[list[float], int, float]] = []
        self.message_history: list[list[float]] = []
        self.internal_dialogue: list[dict[str, Any]] = []
        self._rng = random.Random()

    def emit(self, embedding: Iterable[float]) -> int:
        """Emite marca interna; retorna índice da palavra ou -1."""
        emb = _norm(embedding)
        if not emb:
            return -1
        for i, (vocab_emb, freq, first_seen) in enumerate(self.vocabulary):
            if _cosine(emb, vocab_emb) > _MATCH_THRESHOLD:
                self.vocabulary[i] = (vocab_emb, freq + 1, first_seen)
                self.message_history.append(emb)
                return i
        if len(self.vocabulary) < self.vocab_size:
            self.vocabulary.append((emb, 1, time.time()))
            self.message_history.append(emb)
            return len(self.vocabulary) - 1
        return -1

    def speak_to_self(self, thought: Iterable[float]) -> list[float]:
        """Diálogo interno: pensamento -> resposta perturbada (não humana)."""
        emb = _norm(thought)
        if not emb:
            return []
        thought_idx = self.emit(emb)
        # resposta = pensamento + ruído, moldada pelos atratores da
        # assinatura quando presente (self_resonance = is_self do
        # pensamento — reconhecimento de si sem nome humano)
        resp = [x + self._rng.gauss(0.0, 0.1) for x in emb]
        if self.signature is not None:
            try:
                for attractor in getattr(self.signature, "attractors", []):
                    a = [float(v) for v in attractor[:len(resp)]]
                    if len(a) == len(resp):
                        sim = _cosine(emb, _norm(a))
                        resp = [r + sim * 0.1 * av for r, av in zip(resp, a)]
            except Exception:  # noqa: BLE001, S110
                pass
            try:
                self_res = float(self.signature.is_self(emb))
            except Exception:  # noqa: BLE001
                self_res = 0.0
        else:
            self_res = 0.0
        response = _norm(resp)
        response_idx = self.emit(response)
        self.internal_dialogue.append({
            "timestamp": time.time(),
            "thought_idx": thought_idx,
            "response_idx": response_idx,
            "self_resonance": self_res,
        })
        return response

    def get_vocabulary_stats(self) -> dict[str, Any]:
        if not self.vocabulary:
            return {"size": 0, "total_messages": 0}
        freqs = [f for _, f, _ in self.vocabulary]
        return {
            "size": len(self.vocabulary),
            "total_messages": len(self.message_history),
            "avg_frequency": sum(freqs) / len(freqs),
            "max_frequency": max(freqs),
            "internal_dialogues": len(self.internal_dialogue),
        }

    def persist(self, db_path: Path | str | None = None) -> dict[str, int]:
        return persist_sandbox(self, db_path)

    def restore(self, db_path: Path | str | None = None) -> int:
        return restore_into(self, db_path)


def persist_sandbox(sandbox: LalangueSandbox,
                    db_path: Path | str | None = None) -> dict[str, int]:
    """Persiste marcas do sandbox (palavras + diálogos) em SQLite."""
    path = Path(db_path) if db_path else _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    now = time.time()
    with sqlite3.connect(str(path)) as conn:
        conn.executescript(_SCHEMA)
        for idx, entry in enumerate(sandbox.vocabulary):
            try:
                embedding, freq, first_seen = entry
            except Exception:  # noqa: BLE001, S112
                continue
            blob, dim = _encode(list(embedding))
            conn.execute(
                "INSERT INTO internal_words"
                " (word_index, embedding, dim, frequency, first_seen, last_seen)"
                " VALUES(?,?,?,?,?,?)"
                " ON CONFLICT(word_index) DO UPDATE SET"
                " embedding=excluded.embedding, dim=excluded.dim,"
                " frequency=excluded.frequency, last_seen=excluded.last_seen",
                (idx, blob, dim, int(freq), float(first_seen), now))
        conn.execute("DELETE FROM internal_dialogues")
        for row in sandbox.internal_dialogue:
            conn.execute(
                "INSERT INTO internal_dialogues"
                " (ts, thought_idx, response_idx, self_resonance) VALUES(?,?,?,?)",
                (float(row.get("timestamp", now)), row.get("thought_idx"),
                 row.get("response_idx"), row.get("self_resonance")))
        for key, value in (("last_persist_utc", str(now)),
                           ("words_n", str(len(sandbox.vocabulary))),
                           ("messages_n", str(len(sandbox.message_history))),
                           ("dialogues_n", str(len(sandbox.internal_dialogue)))):
            conn.execute(
                "INSERT INTO internal_store_meta(key,value) VALUES(?,?)"
                " ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, value))
        conn.commit()
    return {"words_n": len(sandbox.vocabulary),
            "messages_n": len(sandbox.message_history),
            "dialogues_n": len(sandbox.internal_dialogue)}


def load_vocabulary(db_path: Path | str | None = None) -> list[dict[str, Any]]:
    """Lê o vocabulário persistido (ordem de índice)."""
    path = Path(db_path) if db_path else _db_path()
    if not path.exists():
        return []
    with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as conn:
        rows = conn.execute(
            "SELECT word_index, embedding, dim, frequency, first_seen, last_seen"
            " FROM internal_words ORDER BY word_index").fetchall()
    return [{"word_index": r[0], "embedding": _decode(r[1], r[2]),
             "frequency": r[3], "first_seen": r[4], "last_seen": r[5]}
            for r in rows]


def restore_into(sandbox: LalangueSandbox,
                 db_path: Path | str | None = None) -> int:
    """Devolve as marcas ao sandbox — a língua interna sobrevive ao restart."""
    rows = load_vocabulary(db_path)
    if not rows:
        return 0
    sandbox.vocabulary = [
        (list(r["embedding"]), int(r["frequency"]), float(r["first_seen"]))
        for r in rows
    ]
    return len(rows)


def store_stats(db_path: Path | str | None = None) -> dict[str, Any]:
    """Contagens do store (observabilidade)."""
    path = Path(db_path) if db_path else _db_path()
    if not path.exists():
        return {"present": False, "words_n": 0, "dialogues_n": 0, "messages_n": 0}
    with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as conn:
        words = conn.execute("SELECT COUNT(*) FROM internal_words").fetchone()[0]
        dial = conn.execute("SELECT COUNT(*) FROM internal_dialogues").fetchone()[0]
        meta = dict(conn.execute("SELECT key, value FROM internal_store_meta"))
    return {"present": True, "words_n": int(words), "dialogues_n": int(dial),
            "messages_n": int(meta.get("messages_n", 0)),
            "last_persist_utc": meta.get("last_persist_utc")}
