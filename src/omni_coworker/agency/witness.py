"""Witness (append-only lineage).

English: Append-only witness log (JSONL) with a sha256 hash chain.
Each record carries `prev_hash` (hash of the previous record, "" for the
first) and `hash` (sha256 over the record content excluding its own hash
field). `verify_witness` walks the chain and reports where it breaks,
including legacy records that predate hashing.
pt-BR: Log de testemunho append-only (JSONL) com hash-chain sha256.
Cada registro carrega `prev_hash` (hash do registro anterior, "" no
primeiro) e `hash` (sha256 sobre o conteúdo do registro excluindo o
próprio campo hash). `verify_witness` percorre a cadeia e reporta onde
ela quebra, inclusive registros legados anteriores ao hashing.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

__all__ = ["append_witness", "read_witness", "verify_witness", "witness_event"]


def _hash_record(record: dict[str, Any]) -> str:
    """Hash a record's content (excluding its own `hash` field).

    English: Deterministic sha256 over the sorted JSON payload.
    pt-BR: sha256 determinístico sobre o payload JSON ordenado.
    """
    payload = {k: v for k, v in record.items() if k != "hash"}
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _last_hash(records: list[dict[str, Any]]) -> str:
    """Hash of the last record, or "" when the chain is empty.

    English: Legacy records without a `hash` field yield "".
    pt-BR: Registros legados sem campo `hash` rendem "".
    """
    if not records:
        return ""
    return records[-1].get("hash", "") or ""


def append_witness(path: str | Path | None = None, event: dict[str, Any] | None = None) -> None:
    """Append an event to witness JSONL.

    English: Appends one JSON line with timestamp, prev_hash and hash.
    pt-BR: Adiciona uma linha JSON com timestamp, prev_hash e hash.
    """
    if path is None:
        path = Path(os.getenv("OMNI_STATE_DIR", "data")) / "witness.jsonl"
    if event is None:
        event = {}
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    # Add timestamp if not present
    if "ts" not in event:
        event = dict(event)
        event["ts"] = datetime.now(UTC).isoformat()

    # MINJA provenance guard (lightweight)
    try:
        from ..memory.provenance import classify_trust, provenance_signature

        ev = event if isinstance(event, dict) else {}
        src = ev.get("instance") or ev.get("source")
        prov = {
            "signature": provenance_signature(ev.get("data", ev), src),
            "trust_class": classify_trust(src, "instance"),
        }
    except Exception:  # noqa: BLE001
        prov = {"signature": "", "trust_class": "unknown"}
    existing = read_witness(p)
    record = dict(event)
    record["provenance"] = prov
    record["prev_hash"] = _last_hash(existing)
    record["hash"] = _hash_record(record)

    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def read_witness(path: str | Path | None = None, limit: int | None = None) -> list[dict[str, Any]]:
    """Read witness log.

    English: Reads JSONL events (skips malformed lines).
    pt-BR: Lê eventos JSONL (ignora linhas malformadas).
    """
    if path is None:
        path = Path(os.getenv("OMNI_STATE_DIR", "data")) / "witness.jsonl"
    p = Path(path)
    if not p.exists():
        return []

    events = []
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except Exception:  # noqa: BLE001, S112
                    continue

    if limit:
        return events[-limit:]
    return events


def witness_event(event_type: str, data: dict[str, Any] | None = None, path: str | Path | None = None) -> None:
    """Create and append a witness event.

    English: Convenience function for witness events.
    pt-BR: Função de conveniência para eventos de testemunho.
    """
    event = {
        "type": event_type,
        "data": data or {},
    }
    if path is None:
        path = Path(os.getenv("OMNI_STATE_DIR", "data")) / "witness.jsonl"
    append_witness(path, event)
    # Audit P1 dual-write: mirror into the node database so the witness
    # survives even if the jsonl is lost (VM recycle, pruning).
    try:
        import json as _json

        from ..store.node_db import NodeDB

        _db = NodeDB()
        _db.init()
        _db.add_artifact(
            task_id=f"witness:{event_type}", kind="witness",
            content=_json.dumps(event, ensure_ascii=False),
        )
    except Exception:  # noqa: BLE001, S110
        pass


def verify_witness(path: str | Path | None = None) -> dict[str, Any]:
    """Verify the witness hash chain.

    English: Walks records and validates prev_hash continuity + content
    hashes. Legacy records without `hash` break the chain at their index.
    Returns {"valid": bool, "records": int, "broken_at": int | None}.
    pt-BR: Percorre os registros e valida a continuidade do prev_hash e
    os hashes de conteúdo. Registros legados sem `hash` quebram a cadeia
    no próprio índice. Retorna {"valid": bool, "records": int,
    "broken_at": int | None}.
    """
    if path is None:
        path = Path(os.getenv("OMNI_STATE_DIR", "data")) / "witness.jsonl"
    records = read_witness(path)
    prev = ""
    for i, record in enumerate(records):
        if not isinstance(record, dict):
            return {"valid": False, "records": len(records), "broken_at": i}
        if record.get("prev_hash", "") != prev:
            return {"valid": False, "records": len(records), "broken_at": i}
        record_hash = record.get("hash")
        if not record_hash:
            return {"valid": False, "records": len(records), "broken_at": i}
        if record_hash != _hash_record(record):
            return {"valid": False, "records": len(records), "broken_at": i}
        prev = record_hash
    return {"valid": True, "records": len(records), "broken_at": None}