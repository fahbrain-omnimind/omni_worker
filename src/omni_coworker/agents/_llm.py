"""Shared LLM backend helper for coworker agents.

English: Minimal role-routed chat over the brain servers
(analyst :8098 / executor :8099). Returns None when backend is down.
pt-BR: Chat mínimo roteado por role sobre os servidores brain
(analista :8098 / executor :8099). Retorna None se o backend cair.
"""

from __future__ import annotations

import json
from typing import Any


def brain_chat(
    messages: list[dict[str, str]],
    role: str = "analyst",
    max_tokens: int = 256,
    temperature: float = 0.3,
) -> str | None:
    """Call a brain server chat completion.

    English: Returns assistant text or None on failure.
    pt-BR: Retorna texto do assistente ou None em falha.
    """
    try:
        from ..brain.server import get_brain_client
        client = get_brain_client(role)
        if client is None:
            return None
        resp = client.post(
            "/v1/chat/completions",
            json={
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
        )
        if resp.status_code != 200:
            return None
        return resp.json()["choices"][0]["message"]["content"]
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
