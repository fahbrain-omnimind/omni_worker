"""shared_workspace.schema — chaves canônicas e validação de payloads.

Orquestração runtime / Runtime orchestration:
    `publish()` exige tópico dentro de CANONICAL_PREFIXES e payload
    JSON-serializável; validação é barata e fail-fast (ValueError) para
    não poluir o barramento com ruído não-endereçável.

Arquitetura / Architecture:
    Prefixos canônicos = contrato de endereçamento da malha. Consumidores
    assinam por prefixo (`subscribe("soul", cb)`) e recebem tudo que
    começa com ele. Chaves sugeridas (não exaustivas):
      soul.phi|psi|sigma|epsilon   soma.probe    agency.missions|dunker
      witness.append    swap.state    kernel.status|affect|maat
      feedback.loop     mesh.*        dream.cycle

Princípios teóricos invocados / Theoretical principles:
    Broadcast de workspace global — um endereçamento estável é o que
    torna o estado observável por módulos não acoplados.

Analogia–homologia (interpretativo, não mecanístico):
    O espaço de chaves é análogo a "canais" de um barramento neural;
    homologia estrutural com tópicos de pub/sub em sistemas distribuídos.

pt-BR: validação leve e fail-fast de tópicos canônicos + payloads JSON.
"""

from __future__ import annotations

import json

CANONICAL_PREFIXES: tuple[str, ...] = (
    "soul", "soma", "agency", "witness", "swap",
    "kernel", "feedback", "mesh", "dream", "loop", "agent",
)


def canonical(topic: str) -> bool:
    """True when topic starts with a canonical prefix (`soul.phi` ∈ soul)."""
    return any(topic == p or topic.startswith(p + ".") for p in CANONICAL_PREFIXES)


def validate(topic: str, payload: object) -> None:
    """Fail-fast contract check; raises ValueError/TypeError on breach.

    English: topic must be canonical, payload must be JSON-serializable.
    pt-BR: tópico deve ser canônico, payload deve ser serializável em JSON.
    """
    if not isinstance(topic, str) or not canonical(topic):
        raise ValueError(f"non-canonical topic: {topic!r}")
    try:
        json.dumps(payload)
    except (TypeError, ValueError) as e:
        raise TypeError(f"payload not JSON-serializable on {topic}: {e}") from e
