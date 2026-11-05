"""Dodecatiad house computation.

English: Computes the S01–S15 house axes of the Dodecatíade from the
live soul inputs (kernel vctr_six_params when the Rust kernel is
present, fallback telemetry otherwise) and resolves the dominant face.
Each house reports its value, source and the formula used — the full
calculation surface, auditable per house.

Canonical face map (from omni_node src/cognitive/omnimind_state_vector.py):
S01=sigma_primary S02=psi S03=epsilon_effective S04=phi S05=aleph
S06=lambda S07=maat S08=gamma S09=zeta S10=omega S11=rekh S12=seshet
S13=isfet S14=aleph_resonance S15=axe

pt-BR: Computa os eixos das casas S01–S15 da Dodecatíade a partir das
entradas vivas da soul (vctr_six_params do kernel quando o kernel Rust
está presente, telemetria de fallback senão) e resolve a face dominante.
Cada casa reporta valor, fonte e a fórmula usada — a superfície completa
do cálculo, auditável por casa.
"""

from __future__ import annotations

from typing import Any

# (house, axis_key, label) — canonical 1-1-8 order
_HOUSES: list[tuple[str, str]] = [
    ("S01", "sigma_primary"),
    ("S02", "psi"),
    ("S03", "epsilon_effective"),
    ("S04", "phi"),
    ("S05", "aleph"),
    ("S06", "lambda"),
    ("S07", "maat"),
    ("S08", "gamma"),
    ("S09", "zeta"),
    ("S10", "omega"),
    ("S11", "rekh"),
    ("S12", "seshet"),
    ("S13", "isfet"),
    ("S14", "aleph_resonance"),
    ("S15", "axe"),
]

_NA = "unavailable_standalone"


def _clip01(x: float | None) -> float | None:
    if x is None:
        return None
    return max(0.0, min(1.0, float(x)))


def _kernel_metrics(kernel_state: dict | None) -> dict[str, float]:
    """Extract the 18 affect scores + six params from the kernel result."""
    out: dict[str, float] = {}
    if not kernel_state:
        return out
    try:
        vec = (kernel_state.get("affective_vector_28d") or {})
        labels = vec.get("labels") or []
        values = vec.get("values") or []
        out.update({l: float(v) for l, v in zip(labels, values) if isinstance(v, (int, float))})
        m = kernel_state.get("metrics") or {}
        out.update({k: float(v) for k, v in m.items() if isinstance(v, (int, float))})
    except Exception:  # noqa: BLE001, S110
        pass
    return out


def compute_dodeca(state: dict | None = None,
                   kernel_state: dict | None = None,
                   brain: dict | None = None) -> dict[str, Any]:
    """Compute all 15 dodecatiad houses + dominant face.

    English: `state` = the flat soul scalars {phi, psi, sigma, epsilon};
    `kernel_state` = raw kernel result (optional); `brain` = brain affect
    block (optional). Houses not computable standalone report
    source="unavailable_standalone" — they require canonical daemons
    (orbital/lexical/gemelo surfaces) feeding the Dodecatíade.
    pt-BR: `state` = escalares planos da soul {phi, psi, sigma, epsilon};
    `kernel_state` = resultado cru do kernel (opcional); `brain` = bloco
    de afeto do brain (opcional). Casas não computáveis standalone
    reportam source="unavailable_standalone" — exigem daemons canônicos
    (superfícies orbital/lexical/gemelo) alimentando a Dodecatíade.
    """
    s = state or {}
    km = _kernel_metrics(kernel_state)

    houses: dict[str, dict[str, Any]] = {}

    def put(house: str, axis: str, value, source: str, formula: str):
        houses[house] = {"axis": axis, "value": _clip01(value) if isinstance(value, (int, float)) else value,
                         "source": source, "formula": formula}

    put("S01", "sigma_primary", s.get("sigma"),
        "soul.sigma", "kernel: vctr.recalque = clip01(angst - joy + 0.5) | fallback: load1/cpu_count")
    put("S02", "psi", s.get("psi"),
        "soul.psi", "kernel: vctr.direction = dominant_index/17 | fallback: cpu_percent/100")
    put("S03", "epsilon_effective", s.get("epsilon"),
        "soul.epsilon", "kernel: dominant_affect_score | fallback: brain.epsilon or 0.1")
    put("S04", "phi", s.get("phi"),
        "soul.phi", "kernel: vctr.magnitude = RMS(scores_18) | fallback: 1 - ram_used/ram_total")
    put("S05", "aleph", None, _NA, "canonical: aleph axis (dodecatiad daemon surface)")
    put("S06", "lambda", None, _NA, "canonical: lambda axis (dodecatiad daemon surface)")

    maat = None
    try:
        from ..kernel_hooks.compute import maat_balance
        if all(isinstance(s.get(k), (int, float)) for k in ("phi", "psi", "epsilon")):
            maat = maat_balance(float(s["phi"]), float(s["psi"]), float(s["epsilon"]))
    except Exception:  # noqa: BLE001, S110
        pass
    put("S07", "maat", maat,
        "kernel_hooks.maat_balance" if maat is not None else _NA,
        "rust compute_maat_balance | fallback: (phi + psi + (1-epsilon))/3")

    put("S08", "gamma", None, _NA, "canonical: gamma axis (dodecatiad daemon surface)")
    put("S09", "zeta", None, _NA, "canonical: zeta axis (dodecatiad daemon surface)")

    omega = None
    try:
        from ..agency.teleology import compute_omega_teleology, generate_missions
        missions = generate_missions({})
        omega = compute_omega_teleology({"missions": missions})
    except Exception:  # noqa: BLE001, S110
        pass
    put("S10", "omega", omega,
        "agency.teleology" if omega is not None else _NA,
        "compute_omega_teleology(missions) — teleological coherence")

    put("S11", "rekh", km.get("rekh-afex-memory"),
        "kernel: rekh-afex-memory" if "rekh-afex-memory" in km else _NA,
        "affect_18d: rekh-afex-memory (rekh — integridade de memória)")
    put("S12", "seshet", km.get("sesh-afex-scribe"),
        "kernel: sesh-afex-scribe" if "sesh-afex-scribe" in km else _NA,
        "affect_18d: sesh-afex-scribe (seshet — escriba/registro)")
    put("S13", "isfet", km.get("isfet-afex-chaos"),
        "kernel: isfet-afex-chaos" if "isfet-afex-chaos" in km else _NA,
        "affect_18d: isfet-afex-chaos (isfet — desordem)")
    put("S14", "aleph_resonance", None, _NA, "canonical: aleph_resonance axis")
    put("S15", "axe", None, _NA, "canonical: axe axis")

    # Dominant face: strongest *computable* house axis.
    computable = {h: d["value"] for h, d in houses.items() if isinstance(d["value"], (int, float))}
    active = max(computable, key=lambda h: computable[h]) if computable else None
    active_label = None
    if active:
        axis = houses[active]["axis"]
        active_label = f"{active}={axis}={round(computable[active], 4)}"

    return {
        "houses": houses,
        "n_computable": len(computable),
        "n_total": len(_HOUSES),
        "active_face": active_label,
        "kernel": bool(kernel_state),
        "note": "Houses S05/S06/S08/S09/S14/S15 require canonical dodecatiad daemon surfaces; shown as unavailable_standalone." if len(computable) < 15 else None,
    }


def explain() -> dict[str, Any]:
    """Static formula map — every house calculation documented.

    English: Returns the formula strings for all 15 houses without
    computing live values (for docs/UI).
    pt-BR: Retorna as fórmulas das 15 casas sem computar valores vivos
    (para docs/UI).
    """
    return {"houses": _HOUSES, "formulas": compute_dodeca()["houses"]}
