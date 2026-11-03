"""Brain server wrapper.

English: Reuses src.erika.erika_torch_server as the brain substrate.
pt-BR: Reutiliza src.erika.erika_torch_server como substrato cerebral.
"""

from __future__ import annotations

import os
from typing import Any

__all__ = ["create_brain_router", "get_brain_client", "ERIKA_HOST", "ERIKA_PORT"]


ERIKA_HOST = os.getenv("ERIKA_HOST", "127.0.0.1")
ERIKA_PORT = int(os.getenv("ERIKA_PORT", "8098"))
ERIKA_BASE_URL = f"http://{ERIKA_HOST}:{ERIKA_PORT}"
EXECUTOR_PORT = int(os.getenv("ERIKA_EXECUTOR_PORT", "8099"))
EXECUTOR_BASE_URL = f"http://{ERIKA_HOST}:{EXECUTOR_PORT}"


def _base_for_role(role: str) -> str:
    """Return the upstream base URL for a brain role.

    English: 'executor' targets the tactical model server, anything else
    targets the analyst/brain server.
    pt-BR: 'executor' aponta para o servidor do modelo tático, o restante
    aponta para o servidor analista/brain.
    """
    return EXECUTOR_BASE_URL if role == "executor" else ERIKA_BASE_URL


def create_brain_router():
    """Create a router that proxies to Erika brain server.
    
    English: Creates FastAPI router bridging to Erika endpoints.
    pt-BR: Cria router FastAPI fazendo bridge para endpoints da Erika.
    """
    try:
        from fastapi import APIRouter, HTTPException
        import httpx
        
        router = APIRouter(prefix="/brain", tags=["brain"])

        @router.post("/unload")
        async def unload(role: str = "executor"):
            """Evict a brain role from GPU (swap scheduler)."""
            try:
                base = _base_for_role(role)
                async with httpx.AsyncClient(timeout=60.0) as client:
                    resp = await client.post(f"{base}/erika/unload")
                    return {"role": role, **resp.json()}
            except Exception as e:
                return {"role": role, "status": "error", "reason": str(e)}

        @router.post("/reload")
        async def reload_model(role: str = "executor"):
            """Reload a brain role on GPU (swap scheduler)."""
            try:
                base = _base_for_role(role)
                async with httpx.AsyncClient(timeout=300.0) as client:
                    resp = await client.post(f"{base}/erika/reload")
                    return {"role": role, **resp.json()}
            except Exception as e:
                return {"role": role, "status": "error", "reason": str(e)}

        @router.get("/health")
        async def health():
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    resp = await client.get(f"{ERIKA_BASE_URL}/health")
                    return resp.json()
            except Exception as e:
                raise HTTPException(status_code=503, detail=f"Brain server unavailable: {e}")
        
        @router.get("/activations")
        async def activations(limit: int = 16):
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    resp = await client.get(f"{ERIKA_BASE_URL}/erika/activations", params={"limit": limit})
                    return resp.json()
            except Exception as e:
                raise HTTPException(status_code=503, detail=f"Brain server unavailable: {e}")
        
        @router.get("/affect")
        async def affect():
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    resp = await client.get(f"{ERIKA_BASE_URL}/erika/affect")
                    return resp.json()
            except Exception as e:
                raise HTTPException(status_code=503, detail=f"Brain server unavailable: {e}")
        
        @router.post("/chat")
        async def chat(payload: dict, role: str = "analyst"):
            try:
                payload = dict(payload or {})
                with_affect = bool(payload.pop("with_affect", False))
                if with_affect:
                    try:
                        from ..agency.affect_tracer import AffectTracer

                        user_turn = " ".join(
                            m.get("content", "")
                            for m in (payload.get("messages") or [])
                            if m.get("role") == "user"
                        )
                        verdict = AffectTracer().observe(user_turn)
                        note = f"[affect] level={verdict.get('level')} reasons={verdict.get('reasons')}"
                        msgs = list(payload.get("messages") or [])
                        payload["messages"] = [{"role": "system", "content": note}] + msgs
                    except Exception:
                        pass
                # gate glial degenerativo: bloqueia geração repetitiva (fail-open)
                _gate_default = os.getenv("OMNI_GATE_FAIL_CLOSED") == "1"
                if payload.pop("with_glial_gate", _gate_default):
                    try:
                        from ..activation_beta.attractor import glial_verdict

                        verdict = glial_verdict()
                        if not verdict.get("allow_generation", True):
                            return {
                                "choices": [{
                                    "message": {
                                        "role": "assistant",
                                        "content": ("[glial_gate] geração bloqueada: "
                                                    f"{verdict.get('reason')}"),
                                    }
                                }],
                                "glial_gate": verdict,
                            }
                        # injeta veredito glial como contexto (transparente)
                        msgs = list(payload.get("messages") or [])
                        glial = verdict.get("glial") or {}
                        payload["messages"] = [{
                            "role": "system",
                            "content": ("[glial] habituated="
                                        f"{glial.get('habituated', 0.0)} "
                                        f"vagus={glial.get('vagus_sedative', 0.0)}"),
                        }] + msgs
                    except Exception:
                        pass
                # memtrias: retorno do recalcado (recall) + inscrição (log)
                mem_recall = bool(payload.pop("memory_recall", False))
                mem_log = bool(payload.pop("memory_log", False))
                mem_chat = str(payload.pop("chat_id", "") or "")
                mem = None
                if mem_recall or mem_log:
                    try:
                        from ..memory.memtrias_ai import get_memtrias

                        mem = get_memtrias()
                    except Exception:
                        mem = None
                user_turn = " ".join(
                    m.get("content", "")
                    for m in (payload.get("messages") or [])
                    if m.get("role") == "user"
                )
                if mem is not None and mem_recall and user_turn:
                    try:
                        hits = mem.recall(
                            user_turn,
                            namespaces=["user", "interaction", "chat", "machine"],
                            chat_id=mem_chat or None, top_k=3)
                        if hits:
                            note = "[memtrias] " + " | ".join(
                                f"{h['namespace']}:{h['content'][:80]}"
                                for h in hits)
                            msgs = list(payload.get("messages") or [])
                            payload["messages"] = [{"role": "system",
                                                    "content": note}] + msgs
                    except Exception:
                        pass
                async with httpx.AsyncClient(timeout=120.0) as client:
                    resp = await client.post(
                        f"{_base_for_role(role)}/v1/chat/completions", json=payload
                    )
                    out = resp.json()
                    if mem is not None and mem_log and user_turn:
                        try:
                            meta = {"instance": role,
                                    "chat_id": mem_chat or None}
                            mem.remember("user", user_turn, **meta)
                            ans = ((out.get("choices") or [{}])[0]
                                   .get("message") or {}).get("content") or ""
                            if ans:
                                mem.remember("interaction",
                                             f"u: {user_turn}\na: {ans}",
                                             **meta)
                        except Exception:
                            pass
                    return out
            except Exception as e:
                raise HTTPException(status_code=503, detail=f"Brain server unavailable: {e}")

        @router.get("/executor/health")
        async def executor_health():
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    resp = await client.get(f"{EXECUTOR_BASE_URL}/health")
                    return resp.json()
            except Exception as e:
                raise HTTPException(status_code=503, detail=f"Executor server unavailable: {e}")

        @router.get("/topology")
        async def topology():
            """Report which brain roles have live servers.

            English: analyst (ERIKA_PORT) + executor (ERIKA_EXECUTOR_PORT).
            pt-BR: analista (ERIKA_PORT) + executor (ERIKA_EXECUTOR_PORT).
            """
            out: dict = {}
            async with httpx.AsyncClient(timeout=3.0) as client:
                for role, base in (("analyst", ERIKA_BASE_URL), ("executor", EXECUTOR_BASE_URL)):
                    try:
                        r = await client.get(f"{base}/health")
                        out[role] = {"status": "up", "base": base, **r.json()}
                    except Exception:
                        out[role] = {"status": "down", "base": base}
            return out

        return router
    except Exception as e:
        # Return a dummy router if dependencies missing
        from fastapi import APIRouter
        router = APIRouter(prefix="/brain", tags=["brain"])
        @router.get("/health")
        def health_fallback():
            return {"status": "unavailable", "error": str(e)}
        return router


_CLIENTS: dict = {}


def get_brain_client(role: str = "analyst"):
    """Get a synchronous client for a brain server role.

    English: Returns cached httpx client for the analyst (default) or
    executor backend.
    pt-BR: Retorna cliente httpx cacheado para o backend analista
    (default) ou executor.
    """
    client = _CLIENTS.get(role)
    if client is not None:
        return client
    try:
        import httpx
        client = httpx.Client(base_url=_base_for_role(role), timeout=300.0)
        _CLIENTS[role] = client
        return client
    except Exception:
        return None
