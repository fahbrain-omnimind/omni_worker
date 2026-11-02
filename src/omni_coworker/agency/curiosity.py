"""Curiosity mode: explore topics against the code corpus.

English: Embeds a user-interest topic, retrieves related code
fragments, and asks the brain to surface gaps/suggestions the agent
can fill and bring back.
pt-BR: Vetoriza um tópico de interesse do usuário, recupera fragmentos
de código correlatos e pede ao brain que traga lacunas/sugestões que o
agente pode preencher e trazer.
"""

from __future__ import annotations

from typing import Any


def explore(
    topic: str,
    out_dir: str | None = None,
    k: int = 6,
    use_llm: bool = True,
) -> dict[str, Any]:
    """Explore a topic against the vectorized code index.

    English: Returns related fragments plus optional LLM synthesis of
    gaps/opportunities. Extractive fallback when the brain is down.
    pt-BR: Retorna fragmentos correlatos mais síntese LLM opcional de
    lacunas/oportunidades. Fallback extrativo quando o brain cai.
    """
    from ..store import code_index

    out_dir = out_dir or code_index.index_dir()
    # feedback.loop modulation: curiosity_boost widens retrieval
    # (boost∈[0,1] → up to +100% k). Fail-open.
    boost = 0.0
    try:
        from ..integration_loop.consumer import latest_modulation
        boost = float((latest_modulation() or {}).get("curiosity_boost") or 0.0)
    except Exception:
        pass
    k_eff = k + int(round(k * max(0.0, min(1.0, boost))))
    hits = code_index.search(topic, out_dir, k=k_eff)

    synthesis = None
    if use_llm and hits:
        try:
            from ..agents._llm import brain_chat_json

            corpus = "\n".join(
                f"- {h['path']}::{h['name']} ({h['kind']}): {h['text'][:180]}" for h in hits
            )
            synthesis = brain_chat_json(
                [
                    {
                        "role": "system",
                        "content": (
                            "Given a topic and related code fragments, reply ONLY "
                            'with JSON: {"relevance": 0..1, "gaps": [str], '
                            '"suggestions": [str]}.'
                        ),
                    },
                    {"role": "user", "content": f"Topic: {topic}\n\nFragments:\n{corpus}"},
                ],
                role="executor",
                max_tokens=280,
            )
        except Exception:
            synthesis = None

    return {
        "topic": topic,
        "fragments": hits,
        "synthesis": synthesis,
        "k_effective": k_eff,
        "curiosity_boost": boost,
        "source": "brain:executor" if synthesis else "extractive",
    }
