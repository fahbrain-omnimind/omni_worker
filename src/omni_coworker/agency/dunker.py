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
    except Exception:
        return []


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
    try:
        from src.cognitive.dunker_architecture import compute_dunker_architecture

        out = compute_dunker_architecture(
            affect_summary,
            psychoanalytic_metrics=psychoanalytic_metrics,
            topology_metrics=topology_metrics,
            free_energy=free_energy,
        )
        out["status"] = "ok"
        out["source"] = "canonical:src.cognitive.dunker_architecture"
        out["families_used"] = len(families)
        return out
    except ImportError:
        return {
            "status": "unavailable",
            "source": None,
            "reason": "canonical src.cognitive.dunker_architecture not on PYTHONPATH",
            "families_used": len(families),
            "affect_summary": affect_summary,
        }
    except Exception as e:
        return {"status": "error", "source": "canonical", "reason": str(e),
                "families_used": len(families)}
