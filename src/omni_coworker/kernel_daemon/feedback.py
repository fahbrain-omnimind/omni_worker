"""kernel_daemon.feedback — publicação do bundle na malha.

Orquestração runtime / Runtime orchestration:
    `publish_feedback(bundle)` escreve os tópicos canônicos do ciclo.
    Transporte: tenta o bus in-process primeiro (daemon dentro do
    FastAPI); se o pacote rodar standalone, cai para POST /mesh/publish
    na API local. Falha de transporte nunca derruba o ciclo — retorna a
    lista de tópicos efetivamente publicados.

Arquitetura / Architecture:
    Tópicos: `kernel.cycle` (bundle completo), `kernel.affect`,
    `kernel.soul`, `kernel.soma`, `kernel.drift` — consumidores podem
    assinar o prefixo `kernel` para receber tudo.

pt-BR: publicação dos tópicos canônicos kernel.* — bus in-process com
fallback HTTP /mesh/publish.
"""

from __future__ import annotations

import os
from typing import Any

_API_PORT = os.getenv("API_PORT", "8081")


def _publish(topic: str, payload: Any) -> bool:
    """In-process bus first; HTTP /mesh/publish when standalone."""
    try:
        from ..shared_workspace import bus
        bus.publish(topic, payload)
        return True
    except Exception:  # noqa: BLE001, S110
        pass
    try:
        import httpx
        r = httpx.post(
            f"http://127.0.0.1:{_API_PORT}/mesh/publish",
            json={"topic": topic, "payload": payload}, timeout=2.0,
        )
        return r.status_code == 200
    except Exception:  # noqa: BLE001
        return False


def publish_feedback(bundle: dict[str, Any]) -> list[str]:
    """Publish canonical kernel.* topics; returns published names."""
    # Síndrome do Afeto Monotípico (OW-SYN-001 D4): afeto nunca pode
    # depender de fonte única — mono_source=True = diversidade degradada,
    # consumidores devem tratar o afeto como frágil nesse ciclo.
    affect = dict(bundle.get("affect") or {})
    affect["mono_source"] = sum(
        1 for r in ("analyst", "executor") if affect.get(r)) < 2
    topics = {
        "kernel.cycle": bundle,
        "kernel.affect": affect,
        "kernel.soul": bundle.get("soul") or {},
        "kernel.soma": bundle.get("soma") or {},
        "kernel.drift": bundle.get("drift") or {},
    }
    return [t for t, p in topics.items() if _publish(t, p)]
