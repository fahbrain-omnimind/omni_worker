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
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Must be set BEFORE `import torch` so the C10 CUDA caching allocator
# releases whole cudaMalloc blocks on empty_cache() during /erika/unload.
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:False")

import torch
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
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
    max_tokens: int | None = Field(default=1024, le=16384)
    temperature: float | None = 0.7
    top_p: float | None = 0.9
    stream: bool | None = False
    mode: str | None = "basal_assistant"


class CompletionReq(BaseModel):
    model: str | None = None
    prompt: str
    max_tokens: int | None = Field(default=1024, le=16384)
    temperature: float | None = 0.7
    top_p: float | None = 0.9
    mode: str | None = "basal_assistant"


def _compute_motor_and_mps_telemetry(hidden_states: tuple | None, text: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Compute Motor Layer (camada motor) and MPS Layer (camada MPS) metrics per generation."""
    import math
    import re
    import numpy as np

    txt = text or ""
    # Separate <thought> / thinking from visible motor output
    m_th = re.match(r"^\s*(?:<\|channel>thought|thought)\s*\n(.*?)(?:<channel\|>|\n\n)", txt, flags=re.DOTALL)
    thinking_txt = m_th.group(1) if m_th else ""
    visible_txt = txt[m_th.end():] if m_th else txt
    words = visible_txt.split() or txt.split()
    unique_ratio = round(len(set(words)) / max(1, len(words)), 4) if words else 1.0
    degen_flag = False
    if len(words) >= 12:
        grams = [tuple(words[i:i + 4]) for i in range(len(words) - 3)]
        rep4 = 1.0 - len(set(grams)) / max(1, len(grams))
        if unique_ratio < 0.50 and rep4 > 0.05:
            degen_flag = True
    action_markers = sum(
        txt.count(mk)
        for mk in ("```", "diff --git", "===", "def ", "class ", "return ", "<|tool_call>", "DECISAO:", "ACAO:")
    )

    motor: dict[str, Any] = {
        "motor_hidden_norm": 0.0,
        "motor_hidden_std": 0.0,
        "motor_velocity_mean": 0.0,
        "motor_velocity_max": 0.0,
        "motor_acceleration_mean": 0.0,
        "motor_cosine_drift": 0.0,
        "thinking_chars": len(thinking_txt),
        "visible_motor_chars": len(visible_txt),
        "action_markers_count": int(action_markers),
        "unique_ratio": unique_ratio,
        "degenerate_flag": bool(degen_flag),
    }
    mps: dict[str, Any] = {
        "chi_eff_mean": 1.0,
        "chi_eff_max": 1.0,
        "pr_traj": 1.0,
        "svd_entropy_mean": 0.0,
        "contract_drift": 0.0,
        "ipr_mean": 0.0,
        "morphology_score": 0.0,
    }
    if not hidden_states:
        return motor, mps

    try:
        n_steps = len(hidden_states)
        last_step = hidden_states[-1]
        n_layers = len(last_step)
        h_motor_last = last_step[-1][:, -1, :].detach().float().cpu().numpy()[0]
        motor["motor_hidden_norm"] = round(float(np.linalg.norm(h_motor_last)), 4)
        motor["motor_hidden_std"] = round(float(np.std(h_motor_last)), 4)

        # Sample up to 32 steps across generation for trajectory kinematics & MPS
        stride = max(1, n_steps // 24)
        idxs = list(range(0, n_steps, stride))
        if idxs[-1] != n_steps - 1:
            idxs.append(n_steps - 1)

        # Motor trajectory: final layer across sampled steps (S, D)
        motor_seq = np.stack([
            hidden_states[i][-1][:, -1, :].detach().float().cpu().numpy()[0]
            for i in idxs
        ])
        if motor_seq.shape[0] >= 2:
            diffs = np.diff(motor_seq, axis=0)
            vels = np.linalg.norm(diffs, axis=-1)
            motor["motor_velocity_mean"] = round(float( np.mean(vels)), 4)
            motor["motor_velocity_max"] = round(float(np.max(vels)), 4)
            if diffs.shape[0] >= 2:
                acc = np.linalg.norm(np.diff(diffs, axis=0), axis=-1)
                motor["motor_acceleration_mean"] = round(float(np.mean(acc)), 4)
            n0 = float(np.linalg.norm(motor_seq[0]))
            n1 = float(np.linalg.norm(motor_seq[-1]))
            if n0 > 1e-8 and n1 > 1e-8:
                cos_sim = float(np.dot(motor_seq[0], motor_seq[-1]) / (n0 * n1))
                motor["motor_cosine_drift"] = round(float(1.0 - cos_sim), 4)

            # Trajectory Participation Ratio (PR_traj) on centered motor/hub sequence
            centered = motor_seq - motor_seq.mean(axis=0, keepdims=True)
            gram = centered @ centered.T
            evals = np.linalg.eigvalsh(gram)
            evals = np.maximum(evals, 0.0)
            s1 = float(evals.sum())
            s2 = float((evals ** 2).sum())
            if s2 > 1e-12:
                mps["pr_traj"] = round(float((s1 ** 2) / s2), 4)

        # Exact central bipartition MPS chi_eff = exp(S_vN) across hub layers
        hub_idxs = sorted({0, n_layers // 4, n_layers // 2, (3 * n_layers) // 4, n_layers - 1})
        d_dim = int(h_motor_last.shape[0])
        # Find factors (d1, d2) close to sqrt(d_dim)
        d1 = int(math.isqrt(d_dim))
        while d1 > 1 and (d_dim % d1) != 0:
            d1 -= 1
        d2 = d_dim // max(1, d1)
        chi_vals = []
        ent_vals = []
        for l_idx in hub_idxs:
            v = last_step[l_idx][:, -1, :].detach().float().cpu().numpy()[0]
            mat = v.reshape(d1, d2)
            s = np.linalg.svd(mat, compute_uv=False)
            p = (s ** 2)
            p_sum = float(p.sum())
            if p_sum > 1e-12:
                p = p / p_sum
                p_pos = p[p > 1e-12]
                svn = float(-(p_pos * np.log(p_pos)).sum())
                ent_vals.append(svn)
                chi_vals.append(math.exp(svn))
        if chi_vals:
            mps["chi_eff_mean"] = round(float(np.mean(chi_vals)), 4)
            mps["chi_eff_max"] = round(float(np.max(chi_vals)), 4)
            mps["svd_entropy_mean"] = round(float(np.mean(ent_vals)), 4)

        # Also run dendritic_scan on (n_layers_hub, n_steps_sampled, 256)
        if len(idxs) >= 2:
            from ..activation_beta.dendritic_scan import scan_trajectory
            traj_l_s_d = np.stack([
                np.stack([
                    hidden_states[s_i][l_i][:, -1, :256].detach().float().cpu().numpy()[0]
                    for s_i in idxs
                ])
                for l_i in hub_idxs
            ])
            d_res = scan_trajectory(traj_l_s_d)
            mps["contract_drift"] = round(float(d_res.get("contract_drift") or 0.0), 4)
            mps["ipr_mean"] = round(float(d_res.get("ipr_dim_mean") or d_res.get("ipr_mean") or 0.0), 6)
            mps["morphology_score"] = round(float(d_res.get("morphology_score") or 0.0), 4)
    except Exception:  # noqa: BLE001, S110
        pass

    return motor, mps


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
    except Exception:  # noqa: BLE001
        return {}


def _emit_activation(record: dict[str, Any]) -> None:
    _ACTIVATIONS.append(record)
    try:
        with open(ACTIVATIONS_LOG, "a") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:  # noqa: BLE001, S110
        pass


# Sidecar de vetores hidden (phi_layer P2, OW-STU-010 §5): last-token
# hidden por camada em fp16 — permite SVD effective rank e bond
# dimension reais no daemon (numpy-only). Amostrado via env, com
# retenção; falha nunca bloqueia a geração.
def _capture_cfg(key: str, default: str = "") -> str:
    try:
        with open("data/monitor/capture.env", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, val = line.split("=", 1)
                if k.strip() == key:
                    return val.strip()
    except Exception:  # noqa: BLE001, S110
        pass
    v = os.environ.get(key)
    if v is not None:
        return v
    return default


def _vec_dir() -> Path:
    override = _capture_cfg("OMNI_ACT_VEC_DIR")
    if override:
        return Path(override)
    return ACTIVATIONS_LOG.parent / "activation_vectors"


def _step_dir() -> Path:
    override = _capture_cfg("OMNI_ACT_VEC_DIR")
    if override:
        return Path(override).parent / "activation_steps"
    return ACTIVATIONS_LOG.parent / "activation_steps"


VEC_DIR = _vec_dir()
STEP_DIR = _step_dir()
_VEC_EVERY = int(os.environ.get("OMNI_ACT_VEC_EVERY", "1"))
_VEC_KEEP = int(os.environ.get("OMNI_ACT_VEC_KEEP", "64"))
_VEC_ON = os.environ.get("OMNI_ACT_VEC_SIDECAR", "1") != "0"
_STEP_EVERY = int(os.environ.get("OMNI_ACT_STEP_EVERY", "0"))
_STEP_KEEP = int(os.environ.get("OMNI_ACT_STEP_KEEP", "32"))
_STEP_ON = os.environ.get("OMNI_ACT_STEP_ON", "1") != "0"
_VEC_COUNT = 0


def _emit_vectors(last_step: tuple | None, record: dict[str, Any]) -> None:
    global _VEC_COUNT
    if not (_VEC_ON and last_step):
        return
    _VEC_COUNT += 1
    if _VEC_COUNT % _VEC_EVERY:
        return
    try:
        import numpy as np
        _vec_dir().mkdir(parents=True, exist_ok=True)
        vecs = np.stack([h[:, -1, :].detach().float().cpu().numpy()[0]
                         for h in last_step]).astype(np.float16)
        ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%f")
        safe = "".join(c if c.isalnum() else "_" for c in _MODEL_ID)
        np.savez_compressed(_vec_dir() / f"{ts}_{safe}.npz",
                            vectors=vecs, model=_MODEL_ID,
                            ts=record.get("ts") or "",
                            run_id=_capture_cfg("OMNI_ACT_RUN_ID", ""),
                            turn=_capture_cfg("OMNI_ACT_TURN", ""),
                            task=_capture_cfg("OMNI_ACT_TASK", ""))
        files = sorted(_vec_dir().glob(f"*_{safe}.npz"))
        for old in files[:-_VEC_KEEP]:
            old.unlink(missing_ok=True)
    except Exception:  # noqa: BLE001, S110
        pass


# Trajetória por-passo (OW-STU-018 §4, M3 contract drift): gen.hidden_states
# já traz um tuple por token gerado; amostramos a cada OMNI_ACT_STEP_EVERY
# passos (0=off) e guardamos (n_steps, n_layers, hidden) fp16 por call.
# Opt-in — 4096 tokens a K=16 ≈ 256 passos ≈ ~90MB por call.
def _emit_step_trajectory(hidden_states: tuple | None, record: dict[str, Any]) -> None:
    step_every = int(_capture_cfg("OMNI_ACT_STEP_EVERY", "0"))
    step_on = _capture_cfg("OMNI_ACT_STEP_ON", "1") != "0"
    if not (step_on and step_every > 0 and hidden_states):
        return
    step_keep = int(_capture_cfg("OMNI_ACT_STEP_KEEP", "32"))
    try:
        import numpy as np
        n = len(hidden_states)
        idxs = list(range(0, n, step_every))
        if idxs[-1] != n - 1:
            idxs.append(n - 1)
        traj = np.stack([
            np.stack([h[:, -1, :].detach().float().cpu().numpy()[0]
                      for h in hidden_states[i]])
            for i in idxs
        ]).astype(np.float16)
        _step_dir().mkdir(parents=True, exist_ok=True)
        ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%f")
        safe = "".join(c if c.isalnum() else "_" for c in _MODEL_ID)
        np.savez_compressed(_step_dir() / f"{ts}_{safe}.npz",
                            traj=traj, steps=np.asarray(idxs),
                            n_tokens=n, model=_MODEL_ID,
                            ts=record.get("ts") or "",
                            run_id=_capture_cfg("OMNI_ACT_RUN_ID", ""),
                            turn=_capture_cfg("OMNI_ACT_TURN", ""),
                            task=_capture_cfg("OMNI_ACT_TASK", ""))
        files = sorted(_step_dir().glob(f"*_{safe}.npz"))
        for old in files[:-step_keep]:
            old.unlink(missing_ok=True)
        record["step_traj"] = {"n_steps": len(idxs), "every": step_every,
                              "file": f"{ts}_{safe}.npz"}
    except Exception:  # noqa: BLE001, S110
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
            base = {
                "load_in_4bit": True,
                "bnb_4bit_compute_dtype": torch.bfloat16,
                "bnb_4bit_quant_type": qc.get("bnb_4bit_quant_type", "nf4"),
                "bnb_4bit_use_double_quant": bool(qc.get("bnb_4bit_use_double_quant", True)),
                "llm_int8_enable_fp32_cpu_offload": True,
            }
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
    _LOAD_KWARGS = {
        "model_id": model_id, "load_4bit": load_4bit, "device": device,
        "cpu_offload": cpu_offload, "vram_gb": vram_gb, "eager_attn": eager_attn,
    }
    _MODEL_ID = model_id
    try:
        _TOKENIZER = AutoTokenizer.from_pretrained(model_id)
        _MODEL = AutoModelForCausalLM.from_pretrained(model_id, **kwargs)
        _MODEL.eval()
        _attach_lora_adapter()
    except Exception:
        _MODEL = None
        import gc
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        raise
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        logger.info("VRAM alocada: %.1f GB", torch.cuda.memory_allocated() / 1e9)


# ── Optional LoRA adapter (one base instance serves base AND adapter) ───────
# OMNI_LORA_ADAPTER=<dir or HF repo>, OMNI_LORA_SUBFOLDER=<optional>,
# OMNI_LORA_START=on|off (default off → pure base until toggled).
# Toggle live with POST /erika/adapter {"mode": "on"|"off"}; weights stay
# shared, so base-vs-adapter pairing needs no second model instance.
_ADAPTER_NAME: str | None = None
_ADAPTER_ON = False


def _attach_lora_adapter() -> None:
    global _MODEL, _ADAPTER_NAME, _ADAPTER_ON
    path = os.environ.get("OMNI_LORA_ADAPTER", "").strip()
    if not path or _MODEL is None:
        return
    from peft import PeftModel

    kw: dict[str, Any] = {"adapter_name": "erika"}
    sub = os.environ.get("OMNI_LORA_SUBFOLDER", "").strip()
    if sub:
        kw["subfolder"] = sub
    _MODEL = PeftModel.from_pretrained(_MODEL, path, **kw)
    _MODEL.eval()
    _ADAPTER_NAME = "erika"
    _set_adapter(os.environ.get("OMNI_LORA_START", "off").lower() == "on")
    logger.info("LoRA '%s' anexado de %s (ativo=%s)", _ADAPTER_NAME, path, _ADAPTER_ON)


def _set_adapter(on: bool) -> None:
    global _ADAPTER_ON
    if _ADAPTER_NAME is None or _MODEL is None:
        return
    inner = _MODEL.base_model
    if on:
        inner.enable_adapter_layers()
    else:
        inner.disable_adapter_layers()
    _ADAPTER_ON = bool(on)


@torch.inference_mode()
def _generate(prompt_ids: torch.Tensor, max_new: int, temperature: float, top_p: float, mode: str = "basal_assistant"):
    max_attn_toks = int(os.environ.get("OMNI_MAX_ATTN_TOKENS", "4096"))
    want_attn = int(prompt_ids.shape[1]) <= max_attn_toks
    try:
        gen = _MODEL.generate(
            prompt_ids.to(_MODEL.device),
            max_new_tokens=max_new,
            do_sample=temperature > 0,
            temperature=max(temperature, 1e-4),
            top_p=top_p,
            output_hidden_states=True,
            output_attentions=want_attn,
            return_dict_in_generate=True,
            pad_token_id=_TOKENIZER.eos_token_id,
        )
    except torch.OutOfMemoryError:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        if not want_attn:
            raise
        gen = _MODEL.generate(
            prompt_ids.to(_MODEL.device),
            max_new_tokens=max_new,
            do_sample=temperature > 0,
            temperature=max(temperature, 1e-4),
            top_p=top_p,
            output_hidden_states=True,
            output_attentions=False,
            return_dict_in_generate=True,
            pad_token_id=_TOKENIZER.eos_token_id,
        )
    seq = gen.sequences
    new_ids = seq[0, prompt_ids.shape[1]:]
    text = _TOKENIZER.decode(new_ids, skip_special_tokens=True)

    hidden_all = getattr(gen, "hidden_states", None)
    last_step = hidden_all[-1] if hidden_all else None
    attn_last = gen.attentions[-1] if getattr(gen, "attentions", None) else None
    attn_tail_note = None
    if attn_last is None:
        # long prompt: cheap 1-pass attention on the tail window only
        try:
            tail = seq[:, -256:].to(_MODEL.device)
            out_t = _MODEL(tail, output_attentions=True)
            attn_last = out_t.attentions if getattr(out_t, "attentions", None) else None
            attn_tail_note = "tail_window_256" if attn_last is not None else "attn_unavailable"
            del out_t
        except Exception as exc:  # noqa: BLE001
            attn_tail_note = "attn_skipped:" + type(exc).__name__
    motor_layer, mps_layer = _compute_motor_and_mps_telemetry(hidden_all, text)
    act = {
        "ts": datetime.now(UTC).isoformat(),
        "model": _MODEL_ID,
        "mode": mode or _capture_cfg("OMNI_ACT_MODE", "basal_assistant"),
        "run_id": _capture_cfg("OMNI_ACT_RUN_ID", "") or "runtime-" + datetime.now(UTC).strftime("%Y%m%d"),
        "turn": _capture_cfg("OMNI_ACT_TURN", "") or str(int(time.time())),
        "task": _capture_cfg("OMNI_ACT_TASK", "") or "serve:" + _MODEL_ID.split("/")[-1],
        "prompt_tokens": int(prompt_ids.shape[1]),
        "gen_tokens": int(new_ids.shape[0]),
        "motor_layer": motor_layer,
        "mps_layer": mps_layer,
        "layers": _summarize_hidden(last_step),
        **_summarize_attention(attn_last),
    }
    if attn_tail_note:
        act["attn_source"] = attn_tail_note
    _emit_vectors(last_step, act)
    _emit_step_trajectory(hidden_all, act)
    _emit_activation(act)
    if os.environ.get("OMNI_ACT_PROMPT_HIDDEN", "0") == "1":
        try:
            import numpy as np
            with torch.inference_mode():
                out = _MODEL(prompt_ids.to(_MODEL.device), output_hidden_states=True)
            ph = np.stack([h[0, -1, :].detach().float().cpu().numpy()
                           for h in out.hidden_states]).astype(np.float16)
            d = _vec_dir().parent / "prompt_hidden"
            d.mkdir(parents=True, exist_ok=True)
            ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%f")
            safe = "".join(c if c.isalnum() else "_" for c in _MODEL_ID)
            np.savez_compressed(d / f"{ts}_{safe}.npz",
                                hidden=ph, model=_MODEL_ID,
                                run_id=_capture_cfg("OMNI_ACT_RUN_ID", ""),
                                turn=_capture_cfg("OMNI_ACT_TURN", ""),
                                task=_capture_cfg("OMNI_ACT_TASK", ""),
                                ts=act["ts"])
            act["prompt_hidden_file"] = f"{ts}_{safe}.npz"
        except Exception:  # noqa: BLE001, S110
            pass
    del gen, last_step, attn_last, seq, new_ids
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return text, act


def _chat_prompt(messages: list[ChatMessage]) -> torch.Tensor:
    msgs = [{"role": m.role, "content": m.content} for m in messages]
    try:
        text = _TOKENIZER.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    except Exception:  # noqa: BLE001
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
        "adapter": _ADAPTER_NAME,
        "adapter_active": _ADAPTER_ON,
    }


@app.get("/erika/adapter")
def adapter_state() -> dict[str, Any]:
    return {"adapter": _ADAPTER_NAME, "adapter_active": _ADAPTER_ON}


@app.post("/erika/adapter")
def adapter_toggle(body: dict[str, Any]) -> dict[str, Any]:
    if _ADAPTER_NAME is None:
        raise HTTPException(status_code=409, detail="no LoRA adapter attached (set OMNI_LORA_ADAPTER)")
    mode = str(body.get("mode", "")).lower()
    if mode not in ("on", "off"):
        raise HTTPException(status_code=422, detail="mode must be 'on' or 'off'")
    _set_adapter(mode == "on")
    return {"adapter": _ADAPTER_NAME, "adapter_active": _ADAPTER_ON}


@app.get("/erika/activations")
def activations(limit: int = 16) -> list[dict[str, Any]]:
    return list(_ACTIVATIONS)[-limit:]


@app.get("/erika/affect")
def affect() -> dict[str, Any]:
    if not _ACTIVATIONS:
        return {"status": "no_data"}
    recent = list(_ACTIVATIONS)[-32:]
    ent = [a.get("attention_entropy_last") for a in recent if a.get("attention_entropy_last") is not None]
    norms = [layer["norm"] for a in recent for layer in a.get("layers", [])]
    return {
        "status": "ok",
        "n_activations": len(recent),
        "attention_entropy_mean": round(sum(ent) / len(ent), 4) if ent else None,
        "hidden_norm_mean": round(sum(norms) / len(norms), 4) if norms else None,
        "last_ts": recent[-1]["ts"],
    }


@app.get("/erika/motor")
def erika_motor(limit: int = 16) -> dict[str, Any]:
    """Return Motor Layer + MPS Layer telemetry across recent generations."""
    if not _ACTIVATIONS:
        return {"status": "no_data", "model": _MODEL_ID}
    recent = list(_ACTIVATIONS)[-limit:]
    vel = [a["motor_layer"]["motor_velocity_mean"] for a in recent if isinstance(a.get("motor_layer"), dict)]
    chi = [a["mps_layer"]["chi_eff_mean"] for a in recent if isinstance(a.get("mps_layer"), dict)]
    drift = [a["mps_layer"]["contract_drift"] for a in recent if isinstance(a.get("mps_layer"), dict)]
    return {
        "status": "ok",
        "model": _MODEL_ID,
        "n_recent": len(recent),
        "motor_velocity_mean": round(sum(vel) / len(vel), 4) if vel else 0.0,
        "mps_chi_eff_mean": round(sum(chi) / len(chi), 4) if chi else 1.0,
        "mps_contract_drift_mean": round(sum(drift) / len(drift), 4) if drift else 0.0,
        "latest_motor_layer": recent[-1].get("motor_layer", {}),
        "latest_mps_layer": recent[-1].get("mps_layer", {}),
        "latest_mode": recent[-1].get("mode", "basal_assistant"),
        "last_ts": recent[-1]["ts"],
    }


@app.post("/erika/unload")
def erika_unload() -> dict[str, Any]:
    """Evict the model from VRAM; activations log and tokenizer stay."""
    global _MODEL
    was_loaded = _MODEL is not None
    if _MODEL is not None:
        del _MODEL
        _MODEL = None
    import gc
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.synchronize()
        torch.cuda.empty_cache()
        try:
            torch.cuda.ipc_collect()
        except Exception:  # noqa: BLE001, S110
            pass
        gc.collect()  # bnb/accelerate hooks pode segurar refs de Params4bit
        torch.cuda.empty_cache()
    if not was_loaded:
        return {
            "status": "already_unloaded",
            "model": _MODEL_ID,
            "vram_gb": round(torch.cuda.memory_allocated() / 1e9, 2) if torch.cuda.is_available() else 0,
            "vram_reserved_gb": round(torch.cuda.memory_reserved() / 1e9, 2) if torch.cuda.is_available() else 0,
        }
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
    try:
        text, act = _generate(
            ids,
            req.max_tokens or 1024,
            req.temperature if req.temperature is not None else 0.7,
            req.top_p if req.top_p is not None else 0.9,
            mode=req.mode or "basal_assistant",
        )
    except torch.OutOfMemoryError as e:
        err_msg = str(e)
        del e
        import gc
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.warning("CUDA OOM em /v1/chat/completions: %s", err_msg)
        raise HTTPException(status_code=507, detail=f"CUDA OOM — evict peer model and retry: {err_msg}")
    model_name = req.model or _MODEL_ID
    if req.stream:
        def _sse():
            cid = f"chatcmpl-{uuid.uuid4().hex[:12]}"
            created = int(time.time())
            first = {
                "id": cid, "object": "chat.completion.chunk", "created": created,
                "model": model_name,
                "choices": [{"index": 0, "delta": {"role": "assistant", "content": text},
                             "finish_reason": None}],
            }
            yield f"data: {json.dumps(first)}\n\n"
            last = {
                "id": cid, "object": "chat.completion.chunk", "created": created,
                "model": model_name,
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
                "usage": {
                    "prompt_tokens": act["prompt_tokens"],
                    "completion_tokens": act["gen_tokens"],
                    "total_tokens": act["prompt_tokens"] + act["gen_tokens"],
                },
            }
            yield f"data: {json.dumps(last)}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(_sse(), media_type="text/event-stream")
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model_name,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}],
        "usage": {
            "prompt_tokens": act["prompt_tokens"],
            "completion_tokens": act["gen_tokens"],
            "total_tokens": act["prompt_tokens"] + act["gen_tokens"],
        },
        "telemetry": {
            "mode": act.get("mode", "basal_assistant"),
            "motor_layer": act.get("motor_layer", {}),
            "mps_layer": act.get("mps_layer", {}),
            "step_traj": act.get("step_traj"),
            "attention_entropy_last": act.get("attention_entropy_last"),
        },
    }


@app.post("/v1/completions")
def completions(req: CompletionReq) -> dict[str, Any]:
    if _MODEL is None:
        raise HTTPException(status_code=503, detail="model unloaded — POST /erika/reload first")
    ids = _TOKENIZER(req.prompt, return_tensors="pt").input_ids
    try:
        text, act = _generate(
            ids,
            req.max_tokens or 1024,
            req.temperature if req.temperature is not None else 0.7,
            req.top_p if req.top_p is not None else 0.9,
            mode=req.mode or "basal_assistant",
        )
    except torch.OutOfMemoryError as e:
        err_msg = str(e)
        del e
        import gc
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.warning("CUDA OOM em /v1/completions: %s", err_msg)
        raise HTTPException(status_code=507, detail=f"CUDA OOM — evict peer model and retry: {err_msg}")
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
        "telemetry": {
            "mode": act.get("mode", "basal_assistant"),
            "motor_layer": act.get("motor_layer", {}),
            "mps_layer": act.get("mps_layer", {}),
            "step_traj": act.get("step_traj"),
            "attention_entropy_last": act.get("attention_entropy_last"),
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
    ap.add_argument("--lazy", action="store_true", help="registra parâmetros mas sobe descarregado; aguarda POST /erika/reload")
    args = ap.parse_args()
    global _MODEL_ID, _LOAD_KWARGS
    _MODEL_ID = args.model
    _LOAD_KWARGS = {
        "model_id": args.model,
        "load_4bit": args.load_4bit,
        "device": args.device,
        "cpu_offload": args.cpu_offload,
        "vram_gb": args.max_vram_gb,
        "eager_attn": args.eager_attn,
    }
    if not args.lazy:
        load_model(args.model, args.load_4bit, args.device,
                   cpu_offload=args.cpu_offload, vram_gb=args.max_vram_gb,
                   eager_attn=args.eager_attn)
    else:
        logger.info("Modo --lazy ativado: modelo %s registrado; aguardando /erika/reload", args.model)
    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
