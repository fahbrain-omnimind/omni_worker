#!/usr/bin/env python3
"""Erika Torch Server — brain model via PyTorch/transformers with instrumentation.

English: Real brain substrate for the coworker — OpenAI-compatible
endpoints plus per-generation telemetry (hidden states + attention by
layer) that feeds the affect surface. Ported from the canonical
``src/erika/erika_torch_server.py`` (omni_node) so the package is
self-contained — the previous stub never loaded a model and the
canonical path does not exist outside this VM.

pt-BR: Substrato cerebral real do coworker — endpoints compatíveis com
OpenAI mais telemetria por geração (hidden states + atenção por camada)
que alimenta a superfície de afeto. Portado do canônico
``src/erika/erika_torch_server.py`` (omni_node) para o pacote ser
autocontido — o stub anterior nunca carregava modelo e o caminho
canônico não existe fora desta VM.

Deltas vs canonical / Diferenças do canônico:
  * ``--eager-attn`` flag → ``attn_implementation="eager"`` (sem ele o
    modelo carrega com SDPA e ``output_attentions`` volta None — zera
    ``attention_entropy_mean`` em /erika/affect e /soul/state).
  * ``POST /erika/unload`` + ``POST /erika/reload`` — evict/reload do
    modelo para o swap scheduler (``orchestration/swap_scheduler.py``).

Surfaces / Superfícies:
  POST /v1/chat/completions   — OpenAI-compatible chat
  POST /v1/completions        — idem, plain text
  GET  /health                — alive + model + VRAM + loaded flag
  GET  /erika/activations     — ring buffer of recent activation summaries
  GET  /erika/affect          — affective aggregate derived from tensors
  POST /erika/unload          — evict model from VRAM (frees the GPU)
  POST /erika/reload          — reload evicted model

Each generation also appends one line to the activations log
(``$ERIKA_ACTIVATIONS_LOG``, default ``data/monitor/erika_torch_activations.jsonl``
relative to the process cwd).

Usage / Uso:
  python -m omni_coworker.server.erika_torch_server \
      --model google/gemma-4-12B-it --load-4bit --eager-attn --port 8098
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import time
import uuid
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO, format="%(asctime)s [erika-torch] %(message)s")
logger = logging.getLogger("erika_torch")

ACTIVATIONS_LOG = Path(os.getenv(
    "ERIKA_ACTIVATIONS_LOG",
    "data/monitor/erika_torch_activations.jsonl",
))
ACTIVATIONS_LOG.parent.mkdir(parents=True, exist_ok=True)

_MODEL = None
_TOKENIZER = None
_MODEL_ID = ""
_LOAD_KWARGS: dict[str, Any] = {}
_ACTIVATIONS: deque[dict[str, Any]] = deque(maxlen=256)


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


# ── Instrumentation / Instrumentação ────────────────────────────────────────
def _summarize_hidden(hidden_states: tuple | None) -> list[dict[str, Any]]:
    if not hidden_states:
        return []
    out = []
    for i, h in enumerate(hidden_states):
        last = h[:, -1, :].float()
        out.append({
            "layer": i,
            "norm": round(float(last.norm(dim=-1).mean()), 4),
            "mean": round(float(last.mean()), 6),
            "std": round(float(last.std()), 4),
        })
    return out


def _summarize_attention(attentions: tuple | None) -> dict[str, Any]:
    if not attentions:
        return {}
    try:
        last = attentions[-1][0].float()
        p = last[:, -1, :].clamp_min(1e-9)
        p = p / p.sum(dim=-1, keepdim=True)
        entropy = float((-(p * p.log())).sum(-1).mean())
        return {"attention_entropy_last": round(entropy, 4), "n_layers": len(attentions)}
    except Exception:
        return {}


def _emit_activation(record: dict[str, Any]) -> None:
    _ACTIVATIONS.append(record)
    try:
        with open(ACTIVATIONS_LOG, "a") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        pass


# ── Model / Modelo ──────────────────────────────────────────────────────────
def load_model(model_id: str, load_4bit: bool, device: str,
               cpu_offload: bool = False, vram_gb: float | None = None,
               eager_attn: bool = False) -> None:
    global _MODEL, _TOKENIZER, _MODEL_ID, _LOAD_KWARGS
    from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

    cfg = AutoConfig.from_pretrained(model_id, trust_remote_code=False)
    qc = getattr(cfg, "quantization_config", None) or {}
    quant_method = qc.get("quant_method")
    prequantized = quant_method is not None
    is_bnb = quant_method == "bitsandbytes"

    kwargs: dict[str, Any] = {"device_map": device}
    if eager_attn:
        # SDPA returns no attentions on generate() — eager keeps the
        # attention tensors that feed /erika/affect and /soul/state.
        kwargs["attn_implementation"] = "eager"
    if cpu_offload:
        kwargs["max_memory"] = {
            0: f"{vram_gb or 19}GiB",
            "cpu": "40GiB",
        }
        if is_bnb or load_4bit or not prequantized:
            from transformers import BitsAndBytesConfig
            base = dict(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_quant_type=qc.get("bnb_4bit_quant_type", "nf4"),
                bnb_4bit_use_double_quant=bool(qc.get("bnb_4bit_use_double_quant", True)),
                llm_int8_enable_fp32_cpu_offload=True,
            )
            kwargs["quantization_config"] = BitsAndBytesConfig(**base)
        # non-bnb quantization (awq/gptq/compressed-tensors): the checkpoint's
        # own quant_config handles offload via max_memory
    elif is_bnb:
        # checkpoint already bnb-quantized — transformers reads
        # quantization_config from config.json
        kwargs["dtype"] = torch.bfloat16
    elif load_4bit:
        from transformers import BitsAndBytesConfig
        kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True,
        )
    else:
        kwargs["dtype"] = torch.float16 if device == "auto" or "cuda" in device else torch.float32

    logger.info("Carregando %s (4bit=%s, prequantizado=%s, eager=%s)…",
                model_id, load_4bit, prequantized, eager_attn)
    _TOKENIZER = AutoTokenizer.from_pretrained(model_id)
    _MODEL = AutoModelForCausalLM.from_pretrained(model_id, **kwargs)
    _MODEL.eval()
    _MODEL_ID = model_id
    _LOAD_KWARGS = {
        "model_id": model_id, "load_4bit": load_4bit, "device": device,
        "cpu_offload": cpu_offload, "vram_gb": vram_gb, "eager_attn": eager_attn,
    }
    if torch.cuda.is_available():
        logger.info("VRAM alocada: %.1f GB", torch.cuda.memory_allocated() / 1e9)


@torch.inference_mode()
def _generate(prompt_ids: torch.Tensor, max_new: int, temperature: float, top_p: float):
    gen = _MODEL.generate(
        prompt_ids.to(_MODEL.device),
        max_new_tokens=max_new,
        do_sample=temperature > 0,
        temperature=max(temperature, 1e-4),
        top_p=top_p,
        output_hidden_states=True,
        output_attentions=True,
        return_dict_in_generate=True,
        pad_token_id=_TOKENIZER.eos_token_id,
    )
    seq = gen.sequences
    new_ids = seq[0, prompt_ids.shape[1]:]
    text = _TOKENIZER.decode(new_ids, skip_special_tokens=True)

    last_step = gen.hidden_states[-1] if getattr(gen, "hidden_states", None) else None
    attn_last = gen.attentions[-1] if getattr(gen, "attentions", None) else None
    act = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "model": _MODEL_ID,
        "prompt_tokens": int(prompt_ids.shape[1]),
        "gen_tokens": int(new_ids.shape[0]),
        "layers": _summarize_hidden(last_step),
        **_summarize_attention(attn_last),
    }
    _emit_activation(act)
    return text, act


def _chat_prompt(messages: list[ChatMessage]) -> torch.Tensor:
    msgs = [{"role": m.role, "content": m.content} for m in messages]
    try:
        text = _TOKENIZER.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    except Exception:
        text = "".join(f"[{m['role']}] {m['content']}\n" for m in msgs) + "[assistant] "
    return _TOKENIZER(text, return_tensors="pt").input_ids


# ── API ──────────────────────────────────────────────────────────────────────
app = FastAPI(title="erika-torch", version="0.2.0")


@app.get("/health")
def health() -> dict[str, Any]:
    cuda = torch.cuda.is_available()
    return {
        "status": "ok",
        "model": _MODEL_ID,
        "model_loaded": _MODEL is not None,
        "cuda": cuda,
        "vram_gb": round(torch.cuda.memory_allocated() / 1e9, 2) if cuda else 0,
        "vram_reserved_gb": round(torch.cuda.memory_reserved() / 1e9, 2) if cuda else 0,
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
        "last_ts": recent[-1]["ts"],
    }


@app.post("/erika/unload")
def erika_unload() -> dict[str, Any]:
    """Evict the model from VRAM; activations log and tokenizer stay."""
    global _MODEL
    if _MODEL is None:
        return {"status": "already_unloaded", "model": _MODEL_ID}
    del _MODEL
    _MODEL = None
    import gc
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.synchronize()
        torch.cuda.empty_cache()
        try:
            torch.cuda.ipc_collect()
        except Exception:
            pass
        gc.collect()  # bnb/accelerate hooks pode segurar refs de Params4bit
        torch.cuda.empty_cache()
    logger.info("Modelo %s despejado da VRAM", _MODEL_ID)
    return {
        "status": "unloaded",
        "model": _MODEL_ID,
        "vram_gb": round(torch.cuda.memory_allocated() / 1e9, 2) if torch.cuda.is_available() else 0,
        "vram_reserved_gb": round(torch.cuda.memory_reserved() / 1e9, 2) if torch.cuda.is_available() else 0,
    }


@app.post("/erika/reload")
def erika_reload() -> dict[str, Any]:
    """Reload the evicted model with the same launch parameters."""
    if _MODEL is not None:
        return {"status": "already_loaded", "model": _MODEL_ID}
    if not _LOAD_KWARGS:
        raise HTTPException(status_code=503, detail="no load parameters recorded")
    load_model(**_LOAD_KWARGS)
    return {
        "status": "loaded",
        "model": _MODEL_ID,
        "vram_gb": round(torch.cuda.memory_allocated() / 1e9, 2) if torch.cuda.is_available() else 0,
    }


@app.post("/v1/chat/completions")
def chat_completions(req: ChatCompletionReq) -> dict[str, Any]:
    if _MODEL is None:
        raise HTTPException(status_code=503, detail="model unloaded — POST /erika/reload first")
    ids = _chat_prompt(req.messages)
    text, act = _generate(ids, req.max_tokens or 256, req.temperature or 0.7, req.top_p or 0.9)
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": req.model or _MODEL_ID,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}],
        "usage": {
            "prompt_tokens": act["prompt_tokens"],
            "completion_tokens": act["gen_tokens"],
            "total_tokens": act["prompt_tokens"] + act["gen_tokens"],
        },
    }


@app.post("/v1/completions")
def completions(req: CompletionReq) -> dict[str, Any]:
    if _MODEL is None:
        raise HTTPException(status_code=503, detail="model unloaded — POST /erika/reload first")
    ids = _TOKENIZER(req.prompt, return_tensors="pt").input_ids
    text, act = _generate(ids, req.max_tokens or 256, req.temperature or 0.7, req.top_p or 0.9)
    return {
        "id": f"cmpl-{uuid.uuid4().hex[:12]}",
        "object": "text_completion",
        "created": int(time.time()),
        "model": req.model or _MODEL_ID,
        "choices": [{"index": 0, "text": text, "finish_reason": "stop"}],
        "usage": {
            "prompt_tokens": act["prompt_tokens"],
            "completion_tokens": act["gen_tokens"],
            "total_tokens": act["prompt_tokens"] + act["gen_tokens"],
        },
    }


def main() -> None:
    # expandable_segments (torch>=2.9 default) keeps VMM segments mapped
    # while ANY block inside is still referenced — empty_cache() then
    # cannot unmap them, so an "unloaded" server kept ~9GB at driver
    # level and the next reload saw no free VRAM. Classic allocator
    # releases whole cudaMalloc blocks on empty_cache. Must be set
    # before CUDA init (setdefault respects explicit overrides).
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:False")
    ap = argparse.ArgumentParser(description="Erika Torch Server")
    ap.add_argument("--model", required=True, help="HF model id ou path local (safetensors)")
    ap.add_argument("--load-4bit", action="store_true", help="quantiza fp16→nf4 no load (checkpoints crus)")
    ap.add_argument("--eager-attn", action="store_true",
                    help="attn_implementation=eager — mantém output_attentions p/ /erika/affect")
    ap.add_argument("--port", type=int, default=8098)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--device", default="auto", help="auto|cuda|cpu")
    ap.add_argument("--max-vram-gb", type=float, default=None, help="cap VRAM — resto vai p/ CPU (device_map auto)")
    ap.add_argument("--cpu-offload", action="store_true", help="permite camadas/KV na RAM quando VRAM estoura")
    args = ap.parse_args()
    load_model(args.model, args.load_4bit, args.device,
               cpu_offload=args.cpu_offload, vram_gb=args.max_vram_gb,
               eager_attn=args.eager_attn)
    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
