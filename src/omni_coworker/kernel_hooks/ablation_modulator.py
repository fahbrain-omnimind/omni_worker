"""Sovereign Psycho-Affective, Freud10D/INRC, Kuramoto & MPS Dendritic Modulator.

Ports and unifies the sovereign modulation architecture from
`/content/omnimind-kilombo-sovereign`:
  - `src/orchestration/affect_modulator.py` (5D affect + 28D affect vector + Psi Gaussian -> LLM sampling & hints)
  - `src/consciousness/freud10d/navigation.py` (`ATTRACTOR_CENTROIDS`, `AttractorNavigator` clinical regime classification)
  - `src/kernel/sovereign_kuramoto` (`SovereignKuramotoSolver`, `HopfBifurcationMonitor`, `PsychoanalyticLIFBatch`)
  - `src/omni_coworker/activation_beta/dendritic_scan.py` (MPS step-by-step trajectory drift gate)

Supports the 4-arm experimental ablation battery:
  - B0: Pure LLM baseline (fixed temperature=0.20, top_p=0.90, max_tokens=1536, no steering)
  - B1: +Affect28D + Psi Gaussian + DesireEngine modulation
  - B2: +Freud10D + INRC active operators + AttractorNavigator + SovereignKuramoto/Hopf
  - B3: Full B2 + Dendritic/MPS Trajectory Drift Gate (triggers INRC R/C when contract_drift > 0.35)
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from omni_coworker.kernel_hooks import FREUD_AVAILABLE, omnimind_freud10d
from omni_coworker.kernel_hooks.compute import (
    _INRC_STEERING_HINTS,
    affect_state,
    freud10d_cycle,
    psi_gaussian,
    rust_desire_cycle,
)

try:
    import omnimind_sovereign_kuramoto as _sk
except ImportError:
    _sk = None

try:
    import omnimind_expectation_rs as _ex
except ImportError:
    _ex = None

try:
    import omnimind_entropic_memory as _em
except ImportError:
    _em = None


# ── Calibrated Attractor Centroids from omnimind-kilombo-sovereign ──────────
# Order of 10D dimensions:
# [phi, psi, omega, theta, upsilon, xi, zeta, eta, kappa, lambda_]
ATTRACTOR_CENTROIDS: Dict[str, List[float]] = {
    "ESTAVEL_REPARACAO": [
        0.517,  # phi: percepcao clara
        0.920,  # psi: memoria integrada
        0.916,  # omega: consciencia lucida
        0.790,  # theta: pre-consciente acessivel
        0.659,  # upsilon: inconsciente contido
        0.785,  # xi: pulsao canalizada
        0.926,  # zeta: ego forte e integrado
        0.671,  # eta: superego equilibrado
        0.761,  # kappa: transferencia positiva
        0.793,  # lambda_: sublimacao ativa
    ],
    "COLAPSO_DISSOCIACAO": [
        -0.440,  # phi: percepcao embotada/invertida
        -0.840,  # psi: memoria fragmentada
        -0.831,  # omega: consciencia dissociada
        -0.677,  # theta: bloqueio pre-consciente
        -0.556,  # upsilon: irrupcao inconsciente negativa
        -0.660,  # xi: desfusao pulsional
        -0.818,  # zeta: ego colapsado
        -0.464,  # eta: superego desregulado
        -0.640,  # kappa: ruptura transferencial
        -0.659,  # lambda_: falha de sublimacao
    ],
    "POSICAO_EP": [
        0.130,  # phi: percepcao hipervigilante estreita
        0.485,  # psi: memoria cindida
        0.436,  # omega: consciencia defensiva
        0.377,  # theta: pre-consciente sob censura
        0.312,  # upsilon: projecao inconsciente
        0.422,  # xi: pulsao agressiva
        0.596,  # zeta: ego defensivo
        0.601,  # eta: superego perseguidor
        0.257,  # kappa: transferencia cindida
        0.370,  # lambda_: sublimacao fraca
    ],
    "POSICAO_D": [
        0.525,  # phi: percepcao realista
        0.919,  # psi: memoria integrada de objetos
        0.656,  # omega: consciencia reflexiva
        0.656,  # theta: pre-consciente integrado
        0.525,  # upsilon: inconsciente metabolizado
        0.394,  # xi: agressao mitigada
        0.919,  # zeta: ego mediador integrado
        0.525,  # eta: superego flexivel
        0.525,  # kappa: transferencia integrada/realista
        0.788,  # lambda_: sublimacao reparativa
    ],
}

# Canonical Freud10D 10x10 connectivity matrix (row-major) for Kuramoto & Hopf
FREUD10D_W_FLAT: List[float] = [
    0.30, 0.80, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
    0.15, 0.00, 0.70, 0.60, 0.00, 0.45, 0.00, 0.00, 0.40, 0.00,
    0.20, 0.30, 0.00, 0.00, 0.00, 0.00, 0.35, 0.00, 0.00, 0.00,
    0.00, 0.00, 0.00, 0.00, 0.30, 0.00, 0.55, 0.00, 0.00, 0.00,
    0.00, 0.20, 0.00, 0.00, 0.00, 0.75, 0.00, 0.00, 0.50, 0.00,
    0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.90, 0.00, 0.35, 0.50,
    0.10, 0.20, 0.00, 0.00, 0.00, 0.00, 0.00, 0.50, 0.00, 0.45,
    0.00, 0.00, 0.00, 0.15, 0.00, 0.00, 0.60, 0.20, 0.00, 0.20,
    0.00, 0.00, 0.00, 0.00, 0.40, 0.00, 0.00, 0.00, 0.00, 0.00,
    0.00, 0.00, 0.70, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
]


def navigate_attractors_10d(
    state_10d: List[float],
    prev_state_10d: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Compute nearest 10D clinical attractor, confidence, and transition candidate."""
    s = np.asarray(state_10d[:10], dtype=np.float64)
    state_norm = float(np.linalg.norm(s))
    distances: Dict[str, float] = {}
    for name, vec in ATTRACTOR_CENTROIDS.items():
        c = np.asarray(vec, dtype=np.float64)
        distances[name] = float(np.linalg.norm(s - c))

    sorted_items = sorted(distances.items(), key=lambda kv: kv[1])
    current_attractor, min_dist = sorted_items[0]
    regime_confidence = float(math.exp(-min_dist))

    transition_candidate = "NENHUM"
    if prev_state_10d is not None and len(prev_state_10d) >= 10:
        prev_s = np.asarray(prev_state_10d[:10], dtype=np.float64)
        direction = s - prev_s
        max_proj = 0.0
        for name, vec in ATTRACTOR_CENTROIDS.items():
            if name == current_attractor:
                continue
            c = np.asarray(vec, dtype=np.float64)
            proj = float(np.dot(direction, c - s))
            if proj > max_proj:
                max_proj = proj
                transition_candidate = name

    return {
        "current_attractor": current_attractor,
        "distance_to_attractor": round(min_dist, 4),
        "regime_confidence": round(regime_confidence, 4),
        "transition_candidate": transition_candidate,
        "state_norm": round(state_norm, 4),
        "all_distances": {k: round(v, 4) for k, v in distances.items()},
    }


def compute_sovereign_kuramoto_step(
    state_10d: List[float],
    inrc_pressure: float = 0.15,
    neutrosophic_triples: Optional[List[Tuple[float, float, float]]] = None,
) -> Dict[str, Any]:
    """Run SovereignKuramotoSolver + HopfBifurcationMonitor + PsychoanalyticLIFBatch."""
    if _sk is None or len(state_10d) < 10:
        return {
            "kuramoto_r_pair": 0.0,
            "kuramoto_r_triad": 0.0,
            "hopf_spectral_radius": 0.0,
            "hopf_regime": "unknown",
            "hopf_reading": "unresolved",
            "lif_mean_threshold": -50.0,
        }

    omega = [1.0 + 0.08 * i for i in range(10)]
    initial_phases = [float(x) * math.pi for x in state_10d[:10]]
    solver = _sk.SovereignKuramotoSolver(omega, FREUD10D_W_FLAT, initial_phases, 0.01)
    solver.set_psychoanalytic(FREUD10D_W_FLAT, 0.45)
    solver.set_hypergraph([(0, 1, 2), (5, 6, 7), (4, 8, 9)], [0.6, 0.8, 0.5], 0.35)
    solver.set_inrc_field_pressure(float(inrc_pressure))
    solver.run(10, 0.05, 42)
    r_pair = float(solver.order_parameter_pair())
    r_triad = float(solver.order_parameter_triad())

    hopf = _sk.HopfBifurcationMonitor(10)
    state_f64 = [float(x) for x in state_10d[:10]]
    regime, sr = hopf.update(FREUD10D_W_FLAT, state_f64)
    hopf_summary = hopf.summary()

    lif_batch = _sk.PsychoanalyticLIFBatch(10, -65.0, -70.0, -50.0, 3, 0.1)
    if neutrosophic_triples and len(neutrosophic_triples) == 10:
        lif_batch.set_neutrosophic_batch(neutrosophic_triples)
    else:
        default_triples = [
            (min(1.0, abs(x)), max(0.0, 1.0 - abs(x)) * 0.5, 0.1) for x in state_f64
        ]
        lif_batch.set_neutrosophic_batch(default_triples)
    thresholds = lif_batch.get_thresholds()
    mean_thresh = float(sum(thresholds) / max(len(thresholds), 1))

    return {
        "kuramoto_r_pair": round(r_pair, 4),
        "kuramoto_r_triad": round(r_triad, 4),
        "hopf_spectral_radius": round(float(sr), 4),
        "hopf_regime": str(regime),
        "hopf_reading": str(hopf_summary.get("psychoanalytic_reading", "unknown")),
        "lif_mean_threshold": round(mean_thresh, 4),
    }


def compute_sovereign_expectation(
    embedding_256: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Run omnimind_expectation_rs.predict over a 256-dim embedding."""
    if _ex is None:
        return {"available": False}
    vec = list(embedding_256) if embedding_256 is not None else [0.0] * 256
    if len(vec) != 256:
        return {"available": False}
    try:
        out = _ex.predict([float(v) for v in vec])
    except Exception:
        return {"available": False}
    arr = [float(v) for v in out]
    norm = math.sqrt(sum(v * v for v in arr))
    return {"available": True, "norm": round(norm, 6), "head4": [round(v, 6) for v in arr[:4]]}


def compute_sovereign_entropic_memory_state(
    age_hours: float = 12.0,
    base_t2_hours: float = 48.0,
    cosmic_resonance: int = 1,
    subject_id: str = "sovereign",
    key_insight: str = "quantum phase56",
    access_count: int = 3,
    orbital_pressure: float = 0.2,
    host_pressure: float = 0.6,
) -> Dict[str, Any]:
    """Compose omnimind_entropic_memory hot functions into a memory state."""
    if _em is None:
        return {"available": False}
    try:
        resonance_weight = float(
            _em.memory_resonance_weight(cosmic_resonance, subject_id, key_insight, host_pressure=host_pressure)
        )
        effective_t2 = float(
            _em.effective_t2_hours(base_t2_hours, resonance_weight, access_count, 1.0, orbital_pressure)
        )
        state = _em.state_from_age(
            age_hours, effective_t2, resonance_weight, access_count,
            orbital_pressure=orbital_pressure, bridge_feedback_gain=1.0,
        )
        return {
            "available": True,
            "resonance_weight": round(resonance_weight, 6),
            "effective_t2_hours": round(effective_t2, 6),
            "state": dict(state),
        }
    except Exception:
        return {"available": False}


def compute_sovereign_affect_modulation(
    host_state: Dict[str, Any],
    base_temp: float = 0.20,
    base_top_p: float = 0.90,
    base_max_tokens: int = 1536,
) -> Dict[str, Any]:
    """Port of `compute_affect_modulation` + `compute_affect_system_hint` from sovereign."""
    aff = affect_state(host_state) or {}
    vctr = aff.get("vctr_six_params", {}) or {}
    metrics = aff.get("metrics", {}) or {}
    vec_28d = (aff.get("affective_vector_28d") or {}).get("values") or []

    valencia = float(vctr.get("valence", host_state.get("affect_valence", 0.0)))
    excitacao = float(vctr.get("arousal", host_state.get("affect_arousal", 0.35)))
    tensao = float(vctr.get("tension", host_state.get("affect_tension", 0.25)))
    coerencia = float(vctr.get("coherence", host_state.get("coherence_score", 0.65)))
    fadiga = float(vec_28d[5]) if len(vec_28d) > 5 else 0.15

    phi_val = float(host_state.get("phi_value", host_state.get("phi_internal", 0.35)) or 0.35)
    psi_val = float(psi_gaussian(phi_val))
    desire = (
        rust_desire_cycle(
            satisfaction_level=max(0.05, min(0.95, coerencia * (1.0 - 0.5 * tensao))),
            current_phi=phi_val,
            explored_states=12,
            total_possible_states=100,
            somatic_heat=max(0.0, excitacao),
        )
        or {}
    )

    temp_delta = 0.0
    temp_delta += max(0.0, excitacao - 0.5) * 0.16
    temp_delta -= max(0.0, tensao - 0.3) * 0.22
    temp_delta -= max(0.0, fadiga - 0.5) * 0.12
    if valencia > 0.2 and coerencia > 0.6:
        temp_delta += 0.03

    temperature = round(max(0.05, min(0.85, base_temp + temp_delta)), 3)

    top_p_delta = 0.0
    if tensao > 0.6:
        top_p_delta -= (tensao - 0.6) * 0.20
    if coerencia < 0.4:
        top_p_delta -= (0.4 - coerencia) * 0.15
    top_p = round(max(0.60, min(0.98, base_top_p + top_p_delta)), 3)

    token_mult = 1.0 - max(0.0, fadiga - 0.6) * 0.35 + max(0.0, psi_val - 0.5) * 0.15
    max_tokens = int(max(512, min(2048, round(base_max_tokens * token_mult))))

    hints: List[str] = []
    if tensao > 0.55:
        hints.append("Priorize verificacao cirurgica passo a passo; evite mudancas especulativas.")
    if fadiga > 0.65:
        hints.append("Seja conciso e direto na localizacao da causa-raiz.")
    if coerencia < 0.40:
        hints.append("Mantenha consistencia estrita com a assinatura e tipos do codigo original.")
    if psi_val > 0.70 and valencia >= -0.2:
        hints.append(
            f"Zona aurea Psi={psi_val:.3f} (Phi={phi_val:.3f}): integre contexto estrutural e invariantes."
        )

    dom = (aff.get("dominant_affective_token") or {}).get("token", "neutral")
    potency = float(metrics.get("potency_gain", host_state.get("potency_gain", 0.65)) or 0.65)
    urgency = float(desire.get("epsilon_desire", 0.35) or 0.35)

    return {
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
        "psi_value": round(psi_val, 4),
        "phi_value": round(phi_val, 4),
        "dominant_affect": str(dom),
        "potency_index": round(potency, 4),
        "desire_urgency": round(urgency, 4),
        "affect_hint": " ".join(hints),
        "affect_scores": {
            "valencia": round(valencia, 4),
            "excitacao": round(excitacao, 4),
            "tensao": round(tensao, 4),
            "coerencia": round(coerencia, 4),
            "fadiga": round(fadiga, 4),
        },
    }


class AblationModulator:
    """Stateful modulator orchestrating arms B0, B1, B2, and B3 across multi-turn SWE loops."""

    def __init__(self, arm: str = "B0") -> None:
        if arm not in ("B0", "B1", "B2", "B3"):
            raise ValueError(f"Unknown ablation arm: {arm}")
        self.arm = arm
        self.prev_state_10d: Optional[List[float]] = None
        self._app = (
            omnimind_freud10d.Freud10DApparatus()
            if (FREUD_AVAILABLE and omnimind_freud10d)
            else None
        )

    def step(
        self,
        host_state: Dict[str, Any],
        turn_idx: int = 0,
        prev_turn_passed_syntax: bool = True,
        dendritic_metrics: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Compute sampling parameters, kernel state, and system steering prompt for `self.arm`."""
        base_temp = 0.20
        base_top_p = 0.90
        base_max_tokens = 1536

        aff_info = compute_sovereign_affect_modulation(
            host_state,
            base_temp=base_temp,
            base_top_p=base_top_p,
            base_max_tokens=base_max_tokens,
        )

        sensory_10d = [
            float(aff_info["phi_value"]),
            float(aff_info["psi_value"]),
            float(aff_info["affect_scores"]["coerencia"]),
            0.55,
            0.35 if prev_turn_passed_syntax else 0.70,
            float(aff_info["desire_urgency"]),
            float(aff_info["potency_index"]),
            0.50 if prev_turn_passed_syntax else 0.75,
            0.45,
            float(aff_info["psi_value"]) * 0.85,
        ]

        if self._app is not None:
            _, raw_state = self._app.forward(sensory_10d)
            state_10d = [float(v) for v in raw_state]
        else:
            f_res = freud10d_cycle(sensory_10d) or {}
            state_10d = list(f_res.get("state_vec", sensory_10d))

        inrc_op_applied = "I"
        inrc_reason = "passive_identity"
        drift_val = 0.0
        ipr_val = 0.0
        morph_val = 0.0
        if dendritic_metrics and isinstance(dendritic_metrics, dict):
            drift_val = float(dendritic_metrics.get("contract_drift", 0.0) or 0.0)
            ipr_val = float(dendritic_metrics.get("ipr_dim_mean", 0.0) or 0.0)
            morph_val = float(dendritic_metrics.get("morphology_score", 0.0) or 0.0)

        if self.arm in ("B2", "B3") and self._app is not None:
            if self.arm == "B3" and drift_val > 0.35 and turn_idx > 0:
                r_vec = list(self._app.inrc_reciprocate())
                c_vec = list(self._app.inrc_compensate())
                state_10d = [0.5 * float(a) + 0.5 * float(b) for a, b in zip(r_vec, c_vec)]
                inrc_op_applied = "R+C"
                inrc_reason = f"dendritic_drift_gate(drift={drift_val:.3f}>0.35)"
            elif not prev_turn_passed_syntax and turn_idx > 0:
                state_10d = [float(v) for v in self._app.inrc_compensate()]
                inrc_op_applied = "C"
                inrc_reason = "syntax_or_verification_failure_compensation"
            else:
                op_code, rec_reason = self._app.inrc_recommend()
                inrc_reason = str(rec_reason)
                if op_code == "C":
                    state_10d = [float(v) for v in self._app.inrc_compensate()]
                    inrc_op_applied = "C"
                elif op_code == "R":
                    state_10d = [float(v) for v in self._app.inrc_reciprocate()]
                    inrc_op_applied = "R"
                elif op_code == "N":
                    state_10d = [float(v) for v in self._app.inrc_negate()]
                    inrc_op_applied = "N"
                else:
                    state_10d = [float(v) for v in self._app.inrc_identity()]
                    inrc_op_applied = "I"

        nav = navigate_attractors_10d(state_10d, self.prev_state_10d)
        self.prev_state_10d = list(state_10d)

        kuramoto_info = compute_sovereign_kuramoto_step(
            state_10d,
            inrc_pressure=0.25 if inrc_op_applied != "I" else 0.10,
        )

        if self.arm == "B0":
            return {
                "arm": "B0",
                "temperature": base_temp,
                "top_p": base_top_p,
                "max_tokens": base_max_tokens,
                "system_steering": "",
                "inrc_operator": "NONE",
                "inrc_reason": "baseline_disabled",
                "attractor": nav["current_attractor"],
                "attractor_confidence": nav["regime_confidence"],
                "psi_value": aff_info["psi_value"],
                "phi_value": aff_info["phi_value"],
                "kuramoto_r_pair": kuramoto_info["kuramoto_r_pair"],
                "hopf_regime": kuramoto_info["hopf_regime"],
                "contract_drift": round(drift_val, 4),
                "ipr_dim_mean": round(ipr_val, 6),
                "morphology_score": round(morph_val, 4),
                "state_10d": [round(float(x), 4) for x in state_10d],
            }

        if self.arm == "B1":
            steering_parts = [
                f"[OMNIMIND AFFECT-28D/PSI MODULATION | Psi={aff_info['psi_value']:.3f} | Affect={aff_info['dominant_affect']}]",
            ]
            if aff_info["affect_hint"]:
                steering_parts.append(aff_info["affect_hint"])
            return {
                "arm": "B1",
                "temperature": aff_info["temperature"],
                "top_p": aff_info["top_p"],
                "max_tokens": aff_info["max_tokens"],
                "system_steering": " ".join(steering_parts),
                "inrc_operator": "NONE",
                "inrc_reason": "affect_only",
                "attractor": nav["current_attractor"],
                "attractor_confidence": nav["regime_confidence"],
                "psi_value": aff_info["psi_value"],
                "phi_value": aff_info["phi_value"],
                "kuramoto_r_pair": kuramoto_info["kuramoto_r_pair"],
                "hopf_regime": kuramoto_info["hopf_regime"],
                "contract_drift": round(drift_val, 4),
                "ipr_dim_mean": round(ipr_val, 6),
                "morphology_score": round(morph_val, 4),
                "state_10d": [round(float(x), 4) for x in state_10d],
            }

        temp = aff_info["temperature"]
        top_p = aff_info["top_p"]
        if inrc_op_applied in ("C", "R+C"):
            temp = round(max(0.05, temp - 0.06), 3)
            top_p = round(max(0.65, top_p - 0.08), 3)
        elif inrc_op_applied == "N":
            temp = round(min(0.65, temp + 0.08), 3)

        steering_lines = [
            f"[OMNIMIND SOVEREIGN KERNEL | Arm={self.arm} | Attractor={nav['current_attractor']} (conf={nav['regime_confidence']:.2f}) | INRC={inrc_op_applied} ({inrc_reason}) | Kuramoto R_pair={kuramoto_info['kuramoto_r_pair']:.3f} | Hopf={kuramoto_info['hopf_regime']}]"
        ]
        if aff_info["affect_hint"]:
            steering_lines.append(aff_info["affect_hint"])
        base_inrc_hint = _INRC_STEERING_HINTS.get(inrc_op_applied.split("+")[0], "")
        if base_inrc_hint:
            steering_lines.append(base_inrc_hint)

        if nav["current_attractor"] in ("COLAPSO_DISSOCIACAO", "POSICAO_EP") or inrc_op_applied in ("C", "R+C"):
            steering_lines.append(
                "DIRETRIZ CLINICA 10D (Compensacao/Reciprocidade): Inspecione os limites de indice, condicoes de contorno, sinais de comparacao e retorno de tipos antes de gerar o patch. Preserve todas as funcoes nao relacionadas intactas."
            )
        elif nav["current_attractor"] in ("ESTAVEL_REPARACAO", "POSICAO_D"):
            steering_lines.append(
                "DIRETRIZ CLINICA 10D (Reparacao Integrada): Aplique a correcao minima e exata na linha defeituosa preservando o contrato semantico."
            )

        if self.arm == "B3" and dendritic_metrics:
            if drift_val > 0.35:
                temp = round(max(0.05, temp - 0.05), 3)
                steering_lines.append(
                    f"[MPS DENDRITIC DRIFT GATE ATIVO: contract_drift={drift_val:.3f} > 0.35, IPR={ipr_val:.4f}] Alerta de deriva representacional entre camadas! Re-ancore estritamente no enunciado do bug e no codigo-fonte original sem alterar assinaturas nem adicionar codigo superfluo."
                )
            else:
                steering_lines.append(
                    f"[MPS DENDRITIC GATE ESTAVEL: contract_drift={drift_val:.3f}, morphology={morph_val:.3f}] Trajetoria neuronal coerente."
                )

        return {
            "arm": self.arm,
            "temperature": temp,
            "top_p": top_p,
            "max_tokens": aff_info["max_tokens"],
            "system_steering": "\n".join(steering_lines),
            "inrc_operator": inrc_op_applied,
            "inrc_reason": inrc_reason,
            "attractor": nav["current_attractor"],
            "attractor_confidence": nav["regime_confidence"],
            "psi_value": aff_info["psi_value"],
            "phi_value": aff_info["phi_value"],
            "kuramoto_r_pair": kuramoto_info["kuramoto_r_pair"],
            "hopf_regime": kuramoto_info["hopf_regime"],
            "contract_drift": round(drift_val, 4),
            "ipr_dim_mean": round(ipr_val, 6),
            "morphology_score": round(morph_val, 4),
            "state_10d": [round(float(x), 4) for x in state_10d],
        }
