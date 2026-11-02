"""Erika Torch Server - Brain server wrapper.

English: FastAPI server for Erika brain model with activation tracking.
pt-BR: Servidor FastAPI para modelo cerebral Erika com rastreamento de ativações.
"""

from __future__ import annotations

import json
import os
import time
import uuid
from collections import deque
from datetime import datetime, timezone
from typing import Any

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel, Field
    import torch
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    FastAPI = None
    BaseModel = object
    Field = lambda *args, **kwargs: None


_MODEL = None
_TOKENIZER = None
_MODEL_ID = ""
_ACTIVATIONS: deque[dict[str, Any]] = deque(maxlen=256)
ACTIVATIONS_LOG = os.getenv("ERIKA_ACTIVATIONS_LOG", "data/erika_torch_activations.jsonl")


if FASTAPI_AVAILABLE:
    app = FastAPI(title="erika-torch", version="0.1.0")
    
    class ChatMessage(BaseModel):
        role: str
        content: str
    
    class ChatCompletionReq(BaseModel):
        model: str | None = None
        messages: list[ChatMessage]
        max_tokens: int | None = Field(default=256, le=8192)
        temperature: float | None = 0.7
        top_p: float | None = 0.9
        stream: bool | None = False
    
    class CompletionReq(BaseModel):
        model: str | None = None
        prompt: str
        max_tokens: int | None = Field(default=256, le=8192)
        temperature: float | None = 0.7
        top_p: float | None = 0.9
    
    
    @app.get("/health")
    def health() -> dict[str, Any]:
        return {
            "status": "ok",
            "model": _MODEL_ID,
            "cuda": torch.cuda.is_available() if FASTAPI_AVAILABLE else False,
            "vram_gb": round(torch.cuda.memory_allocated() / 1e9, 2) if (FASTAPI_AVAILABLE and torch.cuda.is_available()) else 0,
            "activations_buffered": len(_ACTIVATIONS),
        }
    
    
    @app.get("/erika/activations")
    def activations(limit: int = 16) -> list[dict[str, Any]]:
        return list(_ACTIVATIONS)[-limit:]
    
    
    @app.get("/erika/affect")
    def affect() -> dict[str, Any]:
        if not _ACTIVATIONS:
            return {"status": "no_data"}
        recent = list(_ACTIVATIONS)[-32:]
        ent = [a.get("attention_entropy_last") for a in recent if a.get("attention_entropy_last") is not None]
        norms = [l["norm"] for a in recent for l in a.get("layers", [])]
        return {
            "status": "ok",
            "n_activations": len(recent),
            "attention_entropy_mean": round(sum(ent) / len(ent), 4) if ent else None,
            "hidden_norm_mean": round(sum(norms) / len(norms), 4) if norms else None,
            "last_ts": recent[-1]["ts"] if recent else None,
        }
    
    
    @app.post("/v1/chat/completions")
    def chat_completions(req: ChatCompletionReq) -> dict[str, Any]:
        if _MODEL is None:
            raise HTTPException(status_code=503, detail="Model not loaded")
        # Simplified response if model not fully implemented
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": _MODEL_ID or req.model or "erika",
            "choices": [{"index": 0, "message": {"role": "assistant", "content": "..."}, "finish_reason": "stop"}],
        }
    
    
    @app.post("/v1/completions")
    def completions(req: CompletionReq) -> dict[str, Any]:
        if _MODEL is None:
            raise HTTPException(status_code=503, detail="Model not loaded")
        return {
            "id": f"cmpl-{uuid.uuid4().hex[:12]}",
            "object": "text_completion",
            "created": int(time.time()),
            "model": _MODEL_ID or req.model or "erika",
            "choices": [{"text": "...", "index": 0, "finish_reason": "stop"}],
        }
else:
    app = None
