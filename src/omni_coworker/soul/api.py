"""Soul API endpoints.

English: GET /soul/state and GET /soul/stream (SSE).
pt-BR: GET /soul/state e GET /soul/stream (SSE).
"""

from __future__ import annotations

import os

from fastapi import APIRouter

router = APIRouter(prefix="/soul", tags=["soul"])


def _compute_state() -> dict:
    """Compute live soul state from soma probe + kernel + brain.

    English: phi/psi/sigma/epsilon derived from host telemetry and,
    when available, the Rust kernel affect vector and brain server.
    pt-BR: phi/psi/sigma/epsilon derivados da telemetria do host e,
    quando disponível, do vetor afetivo do kernel Rust e do brain server.
    """
    soma: dict = {}
    try:
        from ..soma.probe import probe
        soma = probe()
    except Exception:
        pass

    affect: dict = {}
    try:
        from ..brain.affect import derive_affect_from_brain
        affect = derive_affect_from_brain() or {}
    except Exception:
        affect = {}

    payload: dict = {"soma": soma, "affect": affect}

    kernel_state = None
    try:
        from ..kernel_hooks.compute import affect_state
        kernel_state = affect_state(payload)
    except Exception:
        kernel_state = None

    if kernel_state:
        vctr = kernel_state.get("vctr_six_params") or {}
        flat = {
            "phi": round(float((vctr.get("magnitude") or {}).get("value", 0.0)), 4),
            "psi": round(float((vctr.get("direction") or {}).get("value", 0.0)), 4),
            "sigma": round(float((vctr.get("recalque") or {}).get("value", 0.0)), 4),
            "epsilon": round(float(kernel_state.get("dominant_affect_score") or 0.0), 4),
            "dominant_token": kernel_state.get("dominant_affect_token"),
            "kernel": True,
            "soma": soma,
            "brain": affect,
        }
    else:
        ram_ratio = (soma.get("ram_used_gb") or 0.0) / (soma.get("ram_total_gb") or 1.0)
        cpu = (soma.get("cpu_percent") or 0.0) / 100.0
        load = (soma.get("load_avg") or [0.0])[0] / max(1, os.cpu_count() or 1)
        flat = {
            "phi": round(max(0.0, min(1.0, 1.0 - ram_ratio)), 4),
            "psi": round(max(0.0, min(1.0, cpu)), 4),
            "sigma": round(max(0.0, min(1.0, load)), 4),
            "epsilon": round(float(affect.get("epsilon", 0.1)), 4),
            "kernel": False,
            "soma": soma,
            "brain": affect,
        }

    try:
        from .dodeca import compute_dodeca
        flat["dodeca"] = compute_dodeca(
            {k: flat.get(k) for k in ("phi", "psi", "sigma", "epsilon")},
            kernel_state=kernel_state,
            brain=affect,
        )
    except Exception:
        pass
    return flat


@router.get("/state")
def state() -> dict:
    """Return current soul state.

    English: Live state payload (soma + kernel + brain + dodeca).
    pt-BR: Payload de estado ao vivo (soma + kernel + brain + dodeca).
    """
    return _compute_state()


@router.get("/dodeca")
def dodeca() -> dict:
    """Dodecatiad house calculations.

    English: Full S01–S15 house map with per-house value, source and
    formula — all dodecatiad calculations exposed and auditable.
    pt-BR: Mapa completo das casas S01–S15 com valor, fonte e fórmula
    por casa — todos os cálculos da dodecatíade expostos e auditáveis.
    """
    from .dodeca import compute_dodeca

    state = _compute_state()
    kernel_state = None
    try:
        from ..kernel_hooks.compute import affect_state
        kernel_state = affect_state({"soma": state.get("soma") or {}, "affect": state.get("brain") or {}})
    except Exception:
        pass
    return compute_dodeca(
        {k: state.get(k) for k in ("phi", "psi", "sigma", "epsilon")},
        kernel_state=kernel_state,
        brain=state.get("brain"),
    )


@router.get("/stream")
async def stream():
    """SSE stream of soul state.

    English: Emits state snapshots every 2s via sse-starlette when
    available, else StreamingResponse.
    pt-BR: Emite snapshots de estado a cada 2s via sse-starlette quando
    disponível, senão StreamingResponse.
    """
    import asyncio
    import json

    try:
        from sse_starlette.sse import EventSourceResponse

        async def gen():
            while True:
                yield {"data": json.dumps(_compute_state())}
                await asyncio.sleep(2.0)

        return EventSourceResponse(gen())
    except ImportError:
        from fastapi.responses import StreamingResponse

        async def gen_raw():
            while True:
                yield f"data: {json.dumps(_compute_state())}\n\n"
                await asyncio.sleep(2.0)

        return StreamingResponse(
            gen_raw(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )


from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path

STATIC_DIR = Path(__file__).parent / "static"


@router.get("/", response_class=HTMLResponse)
def root():
    """Serve Machine Public Soul UI.
    
    English: Serves the bilingual HTML interface.
    pt-BR: Serve interface HTML bilíngue.
    """
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return index_path.read_text(encoding="utf-8")
    return "<html><body><h1>Machine Public Soul</h1></body></html>"


@router.get("/static/{path:path}")
def static_files(path: str):
    """Serve static files.
    
    English: Serves static assets.
    pt-BR: Serve arquivos estáticos.
    """
    file_path = STATIC_DIR / path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    return {"error": "not found"}
