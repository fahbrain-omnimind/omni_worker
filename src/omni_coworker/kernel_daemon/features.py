"""kernel_daemon.features — agregação numpy do bundle por ciclo.

Orquestração runtime / Runtime orchestration:
    `aggregate(raw)` transforma o dict bruto do collector num
    FeatureBundle (dict plano, JSON-safe). Sem torch; numpy apenas.
    Registros são agrupados por `model` (12B analyst vs E4B executor).

Arquitetura / Architecture:
    Saída contém por modelo: n_records, médias de prompt/gen tokens,
    attention_entropy médio, hidden-norm médio/std global e da última
    camada, gen_tokens máximo (pressão de KV) — mais deltas vs o ciclo
    anterior (chamado mantém `_PREV`). Sombras Rust via kernel_hooks
    quando importáveis (maat_balance/sigma), fallback None.

Princípios teóricos invocados / Theoretical principles:
    Entropia de atenção e normas de camada como proxies observáveis de
    "intensidade" de processamento; deltas entre ciclos como sinal de
    deriva (drift) do regime operacional.

pt-BR: agrega registros de ativação + telemetria por ciclo, numpy only.
"""

from __future__ import annotations

import statistics
from typing import Any

_PREV: dict[str, dict] = {}


def _f(xs: list[float]) -> float | None:
    xs = [x for x in xs if isinstance(x, (int, float))]
    return round(statistics.fmean(xs), 4) if xs else None


def _per_model(records: list[dict]) -> dict[str, Any]:
    """Aggregate activation records grouped by model id."""
    by_model: dict[str, list[dict]] = {}
    for r in records:
        by_model.setdefault(r.get("model") or "unknown", []).append(r)
    out: dict[str, Any] = {}
    for model, rs in by_model.items():
        entropy = [r.get("attention_entropy_last") for r in rs]
        last_norms = [
            (r.get("layers") or [{}])[-1].get("norm")
            for r in rs if r.get("layers")
        ]
        all_norms = [l.get("norm") for r in rs for l in (r.get("layers") or [])]
        gens = [r.get("gen_tokens") for r in rs]
        out[model] = {
            "n_records": len(rs),
            "prompt_tokens_mean": _f([r.get("prompt_tokens") for r in rs]),
            "gen_tokens_mean": _f(gens),
            "gen_tokens_max": max((g for g in gens if isinstance(g, int)), default=None),
            "attention_entropy_mean": _f([e for e in entropy if e is not None]),
            "hidden_norm_mean": _f(all_norms),
            "hidden_norm_std": round(statistics.pstdev(all_norms), 4)
                if len(all_norms) > 1 else None,
            "last_layer_norm_mean": _f(last_norms),
        }
    return out


def aggregate(raw: dict[str, Any]) -> dict[str, Any]:
    """Collector dict → flat FeatureBundle (JSON-safe)."""
    per_model = _per_model(raw.get("activations") or [])
    soul = raw.get("soul") or {}
    soma = raw.get("soma") or {}
    gpu = ((soma.get("gpu") or {}).get("gpus") or [{}])[0]
    bundle = {
        "ts": raw.get("ts"),
        "models": per_model,
        "affect": raw.get("affect") or {},
        "soul": {k: soul.get(k) for k in ("phi", "psi", "sigma", "epsilon", "dominant_token")},
        "soma": {
            "cpu_percent": soma.get("cpu_percent"),
            "ram_percent": soma.get("ram_percent"),
            "load_per_core": soma.get("load_per_core"),
            "disk_percent": (soma.get("disk") or {}).get("root_percent"),
            "psi_cpu_some": (((soma.get("psi") or {}).get("cpu") or {})
                            .get("some") or {}).get("avg10"),
            "psi_io_some": (((soma.get("psi") or {}).get("io") or {})
                           .get("some") or {}).get("avg10"),
            "psi_mem_some": (((soma.get("psi") or {}).get("memory") or {})
                            .get("some") or {}).get("avg10"),
            "gpu_vram_used_gb": gpu.get("vram_used_gb"),
            "gpu_vram_total_gb": gpu.get("vram_total_gb"),
            "gpu_util_percent": gpu.get("util_percent"),
            "gpu_power_w": gpu.get("power_w"),
            "gpu_temp_c": gpu.get("temp_c"),
        },
        "mesh_topics": sorted((raw.get("mesh") or {}).keys()),
    }
    # deltas vs previous cycle — drift signal
    drift = {}
    for model, m in per_model.items():
        prev = _PREV.get(model) or {}
        for k in ("gen_tokens_mean", "attention_entropy_mean", "hidden_norm_mean"):
            if m.get(k) is not None and prev.get(k) is not None:
                drift.setdefault(model, {})[k] = round(m[k] - prev[k], 4)
    bundle["drift"] = drift
    _PREV.update(per_model)
    return bundle
