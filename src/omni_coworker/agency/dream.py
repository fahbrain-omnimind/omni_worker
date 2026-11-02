"""Dream mode (metabolization in inactivity).

English: Symbolic metabolization during idle periods.
pt-BR: Metabolização simbólica em períodos de inatividade.
"""

from __future__ import annotations

from typing import Any


def metabolize(idle_seconds: float = 0.0, context: dict | None = None) -> dict[str, Any]:
    """Run dream metabolization.
    
    English: Returns metabolization summary.
    pt-BR: Retorna resumo da metabolização.
    """
    context = context or {}

    # Try canonical DreamWeaver bus listener if available
    try:
        from src.cognitive.dream_weaver import DreamWeaver
        dw = DreamWeaver()
        received = dw.listen_to_bus()
        return {"metabolized": int(bool(received)), "source": "DreamWeaver", "bus_received": bool(received)}
    except Exception:
        pass
    
    # Fallback metabolization
    metabolized_count = min(10, int(idle_seconds / 60) + 1)
    return {
        "metabolized": metabolized_count,
        "source": "fallback",
        "summary": {
            "integrated": metabolized_count,
            "compressed": metabolized_count // 2,
            "tempo": "inatividade"
        },
        "idle_seconds": idle_seconds
    }


def weave(context: dict | None = None) -> dict[str, Any]:
    """Weave dream narrative.
    
    English: Creates symbolic synthesis.
    pt-BR: Cria síntese simbólica.
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
    from pathlib import Path

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
