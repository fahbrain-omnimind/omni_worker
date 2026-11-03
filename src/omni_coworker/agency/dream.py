"""Dream mode (metabolization in inactivity).

English: Real symbolic metabolization during idle periods — reads the
memtrias records written since the last run (high-water mark persisted
in OMNI_STATE_DIR/metabolize_state.json), weaves them into a compressed
digest (analyst brain when online, extractive condensation offline)
and inscribes the result as a `dream`-namespace memory carrying the
source ids in `events`. Nothing is invented: no new records → zero.
pt-BR: Metabolização simbólica real em períodos de inatividade — lê os
registros memtrias escritos desde a última rodada (marca d'água
persistida em OMNI_STATE_DIR/metabolize_state.json), tece-os num
digest comprimido (brain analista online, condensação extrativa
offline) e inscreve o resultado como memória do namespace `dream` com
os ids de origem em `events`. Nada é inventado: sem registros novos →
zero.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

_STATE_NAME = "metabolize_state.json"
_MAX_SOURCES = 50


def _state_path() -> Path:
    return Path(os.getenv("OMNI_STATE_DIR", "data")) / _STATE_NAME


def _load_mark() -> float:
    try:
        return float(json.loads(_state_path().read_text()).get("last_ts", 0.0))
    except Exception:
        return 0.0


def _save_mark(ts: float) -> None:
    try:
        p = _state_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"last_ts": ts}))
    except Exception:
        pass


def _weave_dream(residue: list[dict[str, Any]]) -> tuple[str, str]:
    """Analyst weaves a synthesis over the day's residues; extractive
    fallback condenses sources verbatim. Returns (text, source)."""
    corpus = "\n".join(
        f"- [{r['namespace']}] {r['content'][:160]}" for r in residue)
    try:
        from ..agents._llm import brain_chat

        text = brain_chat(
            [{"role": "system", "content": (
                "You are metabolizing the day's memory residues into dream "
                "material. Compress these fragments into a short synthesis "
                "(2-4 sentences): what recurs, what tensions, what was "
                "integrated. No lists, no code.")},
             {"role": "user", "content": corpus}],
            role="analyst", max_tokens=180, temperature=0.85)
        if text:
            return text, "brain:analyst"
    except Exception:
        pass
    return " | ".join(r["content"][:80] for r in residue[:8]), "extractive"


def metabolize(idle_seconds: float = 0.0,
               context: dict | None = None) -> dict[str, Any]:
    """Run dream metabolization over unintegrated memtrias records.

    English: Integrates records newer than the persisted high-water
    mark into one compressed `dream` memory. Returns honest counts.
    pt-BR: Integra registros mais novos que a marca d'água persistida
    numa memória `dream` comprimida. Retorna contagens honestas.
    """
    try:
        from ..memory.memtrias_ai import get_memtrias

        mem = get_memtrias()
    except Exception as e:
        return {"metabolized": 0, "source": "unavailable", "reason": str(e)}

    mark = _load_mark()
    residue = mem.records_since(mark, limit=_MAX_SOURCES)
    if not residue:
        return {"metabolized": 0, "source": "memtrias",
                "reason": "no_new_records", "mark": mark,
                "idle_seconds": idle_seconds}

    text, source = _weave_dream(residue)
    ids = [r["id"] for r in residue]
    new_mark = max(r["ts"] for r in residue)
    rec = mem.remember(
        "dream", text,
        tags=["metabolized"],
        instance="dream",
        events=[{"type": "metabolize", "source_ids": ids,
                 "source_count": len(ids), "idle_seconds": idle_seconds}],
        state_ref={"mark": new_mark, "residue_ns":
                   sorted({r["namespace"] for r in residue})},
    )
    _save_mark(new_mark)
    return {"metabolized": len(residue), "source": source,
            "dream_id": rec["id"], "mark": new_mark,
            "namespaces": sorted({r["namespace"] for r in residue}),
            "idle_seconds": idle_seconds}


def weave(context: dict | None = None) -> dict[str, Any]:
    """Weave dream narrative — one metabolization pass.

    English: Creates symbolic synthesis over pending residues.
    pt-BR: Cria síntese simbólica sobre resíduos pendentes.
    """
    return metabolize(0, context)


def dream_cycle(
    out_dir: str | None = None,
    n_chunks: int = 4,
    witness_path: str | None = None,
) -> dict[str, Any]:
    """Run a dream cycle over the vectorized code corpus.

    English: Samples code chunks from the index, asks the analyst
    brain to weave an associative reflection ("dreaming" with the
    symbolic body), appends it to the witness JSONL and returns the
    dream record. Works without LLM (extractive fallback).

    pt-BR: Amostra chunks de código do índice, pede ao brain analista
    uma reflexão associativa ("sonhar" com o corpo simbólico), anexa ao
    JSONL de testemunho e retorna o registro do sonho. Funciona sem
    LLM (fallback extrativo).
    """
    import random

    from ..store import code_index
    from .witness import witness_event

    out_dir = out_dir or code_index.index_dir()
    chunks = code_index.search("architecture agency safety soul store brain", out_dir, k=n_chunks * 2)
    sample = random.sample(chunks, min(n_chunks, len(chunks))) if chunks else []

    corpus = "\n".join(f"- [{c['kind']}] {c['path']}::{c['name']}: {c['text'][:200]}" for c in sample)
    dream_text = None
    source = "extractive"
    try:
        from ..agents._llm import brain_chat
        dream_text = brain_chat(
            [
                {
                    "role": "system",
                    "content": (
                        "You are dreaming over your own code body. Weave a short "
                        "associative reflection (2-4 sentences) connecting these "
                        "fragments to the system's growth. No lists, no code."
                    ),
                },
                {"role": "user", "content": corpus or "(empty corpus)"},
            ],
            role="analyst",
            max_tokens=180,
            temperature=0.9,
        )
        if dream_text:
            source = "brain:analyst"
    except Exception:
        dream_text = None

    if not dream_text:
        dream_text = " | ".join(f"{c['path']}::{c['name']}" for c in sample) or "no corpus"

    record = {
        "type": "dream_cycle",
        "source": source,
        "dream": dream_text,
        "fragments": [{"path": c["path"], "name": c["name"], "score": c["score"]} for c in sample],
    }
    try:
        witness_event("dream_cycle", record, path=witness_path)
    except Exception:
        pass
    return record
