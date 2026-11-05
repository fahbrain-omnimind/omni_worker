"""integration_loop.adapters — leitura das fontes do ciclo.

Orquestração runtime / Runtime orchestration:
    Fonte primária: `kernel.cycle` no barramento (bundle do
    kernel_daemon — activations por modelo, affect, soul, soma).
    Fallback quando o daemon ainda não publicou: `collect_cycle()`
    direto do kernel_daemon (mesma leitura, sem duplicar código).
    Contexto de meaning: code index faiss via `store.code_index`.

Arquitetura / Architecture:
    Tudo read-only, timeout-bounded; falha → campo None, nunca
    bloqueia o ciclo.

pt-BR: adapters leem kernel.cycle da malha (fallback: collector
direto) + soma/soul + busca semântica no code index.
"""

from __future__ import annotations

from typing import Any

_DIM = 64  # sensory embedding dim


def collect_kernel_bundle() -> dict[str, Any] | None:
    """Latest kernel.cycle bundle from the mesh; None when absent."""
    try:
        from ..shared_workspace import bus
        ev = bus.latest("kernel.cycle")
        return (ev or {}).get("payload")
    except Exception:  # noqa: BLE001
        return None


def collect_sensory() -> dict[str, Any]:
    """Kernel bundle (mesh-first, daemon fallback) for the cycle."""
    bundle = collect_kernel_bundle()
    if bundle is None:
        try:
            from ..kernel_daemon.collector import collect_cycle
            bundle = collect_cycle()
        except Exception:  # noqa: BLE001
            bundle = {}
    # fresh per-cycle soul/soma are already inside the bundle
    return bundle or {}


def collect_meaning_context(query: str) -> dict[str, Any]:
    """Top-1 code-index hit for `query`; None-safe."""
    if not query:
        return {}
    try:
        from ..store.code_index import index_dir, search
        hits = search(query, index_dir(), k=1)
        return hits[0] if hits else {}
    except Exception:  # noqa: BLE001
        return {}
