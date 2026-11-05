"""Flat host_state builder for the Rust kernel.

English: `omnimind_kernel_compute.compute_affect_vector_28d` reads a FLAT
dict (thermal_pressure, ram_pressure, uptime_seconds, ...) — but call
sites were passing nested payloads like `{"soma": probe()}` whose inner
keys also had different names (ram_percent, uptime_s). Result: the 28d
vector was computed over ~zeros and dunker families inherited noise.
This module maps the live worker signals (soma probe + kernel.cycle
bundle + brain affect) onto the flat schema.

pt-BR: `compute_affect_vector_28d` lê um dict FLAT — os call-sites
passavam payloads aninhados com nomes diferentes, zerando o vetor 28d.
Este módulo mapeia os sinais vivos do worker (soma + bundle kernel.cycle
+ afeto dos brains) para o schema flat. Mapeamentos conceituais marcados
[INTERPRETAÇÃO] — não são o schema soberano original.
"""

from __future__ import annotations

from typing import Any


def _f(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, x))


def collect_kernel_bundle() -> dict[str, Any]:
    """Latest kernel.cycle bundle from the mesh; {} when absent."""
    try:
        from ..shared_workspace import bus
        ev = bus.latest("kernel.cycle")
        return (ev or {}).get("payload") or {}
    except Exception:  # noqa: BLE001
        return {}


def build_host_state(
    soma: dict | None = None,
    affect: dict | None = None,
    bundle: dict | None = None,
    extra: dict | None = None,
) -> dict[str, Any]:
    """Build the flat host_state dict the Rust kernel expects.

    soma:   `soma.probe()` output (cpu/ram/disk/net/psi fields).
    affect: brain affect map (`/kernel.affect` payload — analyst/executor
            attention entropy, hidden norms).
    bundle: `kernel.cycle` bundle (attractor, phi_layer, metastability,
            homeostasis, desire, drift, spectral); fetched from the mesh
            when omitted.
    extra:  explicit overrides merged last (wins over derived values).
    """
    soma = soma or {}
    affect = affect or {}
    if bundle is None:
        bundle = collect_kernel_bundle()

    meta = bundle.get("metastability") or {}
    attractor = bundle.get("attractor") or {}
    phi_layer = bundle.get("phi_layer") or {}
    desire = bundle.get("desire") or {}
    drift = bundle.get("drift") or {}
    disk = soma.get("disk") or {}
    psi = soma.get("psi") or {}
    gpus = soma.get("gpus") or soma.get("gpu") or []
    if isinstance(gpus, dict):
        gpus = [gpus]

    # Extract phi_internal and phi_temporal_mi whether phi_layer is flat or keyed by model_id
    phi_int_vals = [
        _f(v.get("phi_internal"))
        for v in phi_layer.values()
        if isinstance(v, dict) and v.get("phi_internal") is not None
    ]
    phi_tmi_vals = [
        _f(v.get("phi_temporal_mi"))
        for v in phi_layer.values()
        if isinstance(v, dict) and v.get("phi_temporal_mi") is not None
    ]
    phi_internal_val = _f(phi_layer.get("phi_internal")) or (
        sum(phi_int_vals) / len(phi_int_vals) if phi_int_vals else 0.0
    )
    phi_tmi_val = _f(phi_layer.get("phi_temporal_mi")) or (
        sum(phi_tmi_vals) / len(phi_tmi_vals) if phi_tmi_vals else 0.0
    )

    # thermal: GPU temp when exposed, else PSI cpu stall as proxy [INTERP]
    temp_c = _f((gpus[0] or {}).get("temp_c") if gpus else 0.0)
    psi_cpu10 = _f(((psi.get("cpu") or {}).get("some") or {}).get("avg10"))

    # entropia soberana: média da attention_entropy dos dois brains
    entropies = [_f((affect.get(r) or {}).get("attention_entropy_mean"))
                 for r in ("analyst", "executor")]
    entropies = [e for e in entropies if e > 0.0]

    # episódios/episódios ativos do atrator (campos do attractor.features())
    state: dict[str, Any] = {
        # --- somatic pressure (schema flat do kernel) ---
        "thermal_pressure": _clip01(temp_c / 95.0) if temp_c else _clip01(psi_cpu10 / 100.0),
        "load_pressure": _clip01(_f(soma.get("load_per_core"))),
        "ram_pressure": _clip01(_f(soma.get("ram_percent")) / 100.0),
        "disk_usage_pct": _clip01(_f(disk.get("root_percent")) / 100.0),
        "swap_usage_pct": (_clip01(_f(soma.get("swap_used_gb")) / _f(soma.get("swap_total_gb")))
                           if _f(soma.get("swap_total_gb")) > 0.0 else 0.0),
        "inode_usage_pct": _clip01(_f(soma.get("inode_usage_pct"))),
        "uptime_seconds": _f(soma.get("uptime_s")),
        "energy_stability_score": _clip01(1.0 - psi_cpu10 / 100.0),

        # --- affect/MPS signals [INTERPRETAÇÃO] ---
        "entropy_sovereign": _clip01((sum(entropies) / len(entropies) / 8.0) if entropies else 0.0),
        "attractor_H_current": phi_internal_val or _f(attractor.get("H_current")),
        "attractor_H_global": phi_tmi_val or _f(attractor.get("H_global")),
        "attractor_frustration": _clip01(_f(meta.get("angst"))),
        "attractor_active_episodes": _f(attractor.get("active_episodes") or attractor.get("n_attractors")),
        "attractor_buffer_overflow_tanh": _clip01(_f(attractor.get("buffer_overflow_tanh"))),
        "epsilon_novelty": _clip01(_f(drift.get("attention_entropy_mean") or drift.get("novelty"))),
        "desire_execution_rate": _clip01(_f(desire.get("intensity"))),
        "angst_share": _clip01(_f(meta.get("angst"))),
        "angst_residual_pressure": _clip01(_f(meta.get("c_soma"))),
        "groddeck_somatic_tension": _clip01(_f(meta.get("c_soma"))),

        # --- freud10d (P2): tensão e estrutura do aparato freudiano persistente ---
        # circularidade virtuosa: freud10d -> kernel -> dunker [INTERP]
        "freud_tension": _clip01(_f((bundle.get("freud10d") or {}).get("tension")) / 10.0),
        "klein_polarization": _clip01(
            _f((((bundle.get("freud10d") or {}).get("structural") or {}).get("conflict_intensity")))
        ),
        "nasio_comocao": _clip01(abs(_f((bundle.get("freud10d") or {}).get("pleasure")))),

        # --- dendritic / MPS / phi signals para joy_base & saudade em affect.rs ---
        "winnicott_true_self": _clip01(
            _f((bundle.get("dendritic") or {}).get("contract_retention_cosine"), 0.5)
        ),
        "nasio_pain_rupture": _clip01(_f((bundle.get("dendritic") or {}).get("contract_drift"))),
        "sutura_gain": _clip01(_f((bundle.get("dendritic") or {}).get("morphology_score"))),
        "potency_gain": _clip01(_f((bundle.get("dendritic") or {}).get("eff_dim_ratio_mean")) * 4.0),
        "quantum_potency": _clip01(phi_internal_val),
        "phase_lock_score": _clip01(1.0 - _f(drift.get("attention_entropy_std"))),

        # --- activity counters (phi_meta binariza activity flags) ---
        "sovereign_daemons_active_n": int(
            _f((bundle.get("phi_meta") or {}).get("active_subsystems"))
            or len((bundle.get("phi_meta") or {}).get("elements") or [])
        ),
    }
    if extra:
        state.update(extra)
    return state
