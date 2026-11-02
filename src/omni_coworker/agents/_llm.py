"""Shared LLM backend helper for coworker agents.

English: Minimal role-routed chat over the brain servers
(analyst :8098 / executor :8099). Returns None when backend is down.
pt-BR: Chat mínimo roteado por role sobre os servidores brain
(analista :8098 / executor :8099). Retorna None se o backend cair.
"""

from __future__ import annotations

import json
import os
from typing import Any


def _soma_inject(messages: list[dict[str, str]]) -> list[dict[str, str]]:
    """Prepend live machine telemetry to the chat.

    English: When OMNI_SOMA_INJECT != "0" (default on), prepends a
    system message with the compact soma context line (cpu/ram/gpu/
    vram/virt) so the model sees the live body of the machine it runs
    on — including virtualization when the host is a VM.
    pt-BR: Quando OMNI_SOMA_INJECT != "0" (default ligado), prepende uma
    mensagem de sistema com a linha de contexto soma (cpu/ram/gpu/vram/
    virt) para o modelo ver o corpo vivo da máquina onde roda —
    incluindo virtualização quando o host é VM.
    """
    if os.getenv("OMNI_SOMA_INJECT", "1") in ("0", "false", "no"):
        return messages
    try:
        from ..soma.probe import soma_context_line

        line = soma_context_line()
        if not line:
            return messages
        return [{"role": "system", "content": f"[soma live] {line}"}] + list(messages)
    except Exception:
        return messages


def brain_chat(
    messages: list[dict[str, str]],
    role: str = "analyst",
    max_tokens: int = 256,
    temperature: float = 0.3,
    include_soma: bool = True,
    with_affect: bool = False,
) -> str | dict | None:
    """Call a brain server chat completion.

    English: Returns assistant text or None on failure. When
    include_soma (default), injects live host telemetry. When
    with_affect, returns a dict {text, affect_level, affect_reasons}
    from the conversational AffectTracer (L0-L4 ladder).
    pt-BR: Retorna texto do assistente ou None em falha. Com
    include_soma (default), injeta telemetria viva do host. Com
    with_affect, retorna dict {text, affect_level, affect_reasons}
    do AffectTracer conversacional (escada L0-L4).
    """
    try:
        from ..brain.server import get_brain_client
        client = get_brain_client(role)
        if client is None:
            return None
        resp = client.post(
            "/v1/chat/completions",
            json={
                "messages": _soma_inject(messages) if include_soma else messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
        )
        if resp.status_code != 200:
            return None
        text = resp.json()["choices"][0]["message"]["content"]
        if not with_affect:
            return text
        from ..agency.affect_tracer import AffectTracer

        user_turn = " ".join(m.get("content", "") for m in messages if m.get("role") == "user")
        verdict = AffectTracer().observe(user_turn + " " + (text or ""))
        return {
            "text": text,
            "affect_level": verdict["level"],
            "affect_reasons": verdict["reasons"],
        }
    except Exception:
        return None


def brain_chat_json(
    messages: list[dict[str, str]],
    role: str = "analyst",
    max_tokens: int = 256,
    temperature: float = 0.2,
) -> dict[str, Any] | None:
    """Call brain chat and parse a JSON object from the reply.

    English: Extracts the first {...} block as JSON; None on failure.
    pt-BR: Extrai o primeiro bloco {...} como JSON; None em falha.
    """
    text = brain_chat(messages, role=role, max_tokens=max_tokens, temperature=temperature)
    if not text:
        return None
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        return json.loads(text[start : end + 1])
    except Exception:
        return None
