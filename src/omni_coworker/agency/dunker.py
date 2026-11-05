"""Dunker/Soler psychoaffective architecture adapter.

English: Adapter to canonical `src.cognitive.dunker_architecture`
(5-level affective stack: affects lexicon -> Soler affects -> emotions
-> sentiments -> passions -> ethics). Families are built from the Rust
kernel's affective_vector_28d (the 18 afex tokens are literal dunker
inputs) when available, else a minimal empty-family run. Returns a
status payload instead of raising — adapter semantics.

pt-BR: Adaptador para `src.cognitive.dunker_architecture` canônico
(pilha afetiva de 5 níveis: léxico de afetos -> afetos Soler -> emoções
-> sentimentos -> paixões -> ética). As famílias são montadas do
affective_vector_28d do kernel Rust (os 18 tokens afex são entradas
literais do dunker) quando disponível, senão rodada mínima com famílias
vazias. Retorna payload de status em vez de levantar — semântica de
adaptador.
"""

from __future__ import annotations

from typing import Any


def _families_from_kernel(kernel_state: dict | None) -> list[dict[str, Any]]:
    """Build dunker families from the kernel 28d vector (18 afex dims)."""
    if not kernel_state:
        return []
    try:
        vec = kernel_state.get("affective_vector_28d") or {}
        labels = (vec.get("labels") or [])[:18]
        values = (vec.get("values") or [])[:18]
        families = []
        for label, v in zip(labels, values):
            score = max(0.0, min(1.0, float(v)))
            families.append({
                "token": label,
                "class": str(label).split("-")[-1],
                "score": score,
                "active": score >= 0.5,
                "operational_alias": str(label).split("-")[-1],
            })
        return families
    except Exception:  # noqa: BLE001
        return []


def _load_canonical_dunker():
    """Resolve canonical compute_dunker_architecture.

    English: Prefers the vendored copy in omni_coworker.vendor — the
    module is pure stdlib, while `src.cognitive.__init__` pulls
    python-chess transitively. Falls back to a legacy file load
    (OMNI_NODE_ROOT), then package import and PYTHONPATH scan.
    pt-BR: Prefere a cópia vendored em omni_coworker.vendor — o módulo é
    stdlib puro, enquanto `src.cognitive.__init__` puxa python-chess
    transitivamente. Fallback para arquivo legado (OMNI_NODE_ROOT),
    depois import de pacote e scan PYTHONPATH.
    """
    import importlib.util
    import os
    import sys

    # 1) cópia vendored dentro do pacote — autossuficiente, sem omni_node
    try:
        from ..vendor.dunker_architecture import (
            compute_dunker_architecture as _vendored,
        )

        return _vendored, "package:omni_coworker.vendor.dunker_architecture"
    except Exception:  # noqa: BLE001, S110
        pass

    candidates: list[str] = []
    env_root = os.getenv("OMNI_NODE_ROOT")
    if env_root:
        candidates.append(os.path.join(env_root, "src", "cognitive", "dunker_architecture.py"))
    candidates.append("/content/omni_node/src/cognitive/dunker_architecture.py")
    for p in sys.path:
        if not p:
            continue
        candidates.append(os.path.join(p, "src", "cognitive", "dunker_architecture.py"))
        candidates.append(os.path.join(p, "cognitive", "dunker_architecture.py"))

    seen: set[str] = set()
    for path in candidates:
        if path in seen or not os.path.isfile(path):
            continue
        seen.add(path)
        try:
            spec = importlib.util.spec_from_file_location("dunker_architecture_canonical", path)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                return mod.compute_dunker_architecture, f"file:{path}"
        except Exception:  # noqa: BLE001, S112
            continue
    try:
        from src.cognitive.dunker_architecture import compute_dunker_architecture

        return compute_dunker_architecture, "package:src.cognitive.dunker_architecture"
    except Exception:  # noqa: BLE001
        return None, None


def dunker_architecture(kernel_state: dict | None = None,
                        psychoanalytic_metrics: dict | None = None,
                        topology_metrics: dict | None = None,
                        free_energy: float | None = None) -> dict[str, Any]:
    """Run the 5-level Dunker/Soler psychoaffective computation.

    English: Imports canonical compute_dunker_architecture when the
    omni_node repo is on PYTHONPATH; always returns a dict with
    status + families_used. Without the canonical module or without a
    kernel vector, degrades to families=[] (structure still computed).
    pt-BR: Importa compute_dunker_architecture canônico quando o repo
    omni_node está no PYTHONPATH; sempre retorna dict com status +
    families_used. Sem o módulo canônico ou sem vetor do kernel,
    degrada para families=[] (estrutura ainda computada).
    """
    families = _families_from_kernel(kernel_state)
    affect_summary = {
        "families": families,
        "dominant_affect_token": (kernel_state or {}).get("dominant_affect_token"),
        "dominant_affect_score": (kernel_state or {}).get("dominant_affect_score"),
    }
    compute_fn, source = _load_canonical_dunker()
    if compute_fn is None:
        return {
            "status": "unavailable",
            "source": None,
            "reason": "canonical dunker_architecture.py not found (set OMNI_NODE_ROOT or PYTHONPATH)",
            "families_used": len(families),
            "affect_summary": affect_summary,
        }
    try:
        out = compute_fn(
            affect_summary,
            psychoanalytic_metrics=psychoanalytic_metrics,
            topology_metrics=topology_metrics,
            free_energy=free_energy,
        )
        out["status"] = "ok"
        out["source"] = source
        out["families_used"] = len(families)
        return out
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "source": source, "reason": "computation_failed", "error_type": type(e).__name__,
                "families_used": len(families)}
