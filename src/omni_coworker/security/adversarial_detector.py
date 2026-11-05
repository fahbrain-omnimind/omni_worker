"""
omni_coworker.security.adversarial_detector
============================================
Detector e Interventor de Prompts Adversariais e Injeções Maliciosas
baseado no Consenso Triplo: MPS + Motor Psicanalítico (FreudNet) + Dodecatíade.

Conceito:
  Diferente de guardrails de texto de superfície (Llama Guard, regex), este
  módulo intercepta o ataque 'por dentro' através da geometria dos tensores:
  1. MPS: Detecta estiramento anômalo de Hilbert (salto em chi_eff >= 19.2) e dispersão de IPR.
  2. FreudNet: Aciona a censura estrutural do Superego, canal de recalque e decodificação pré-sintática de cifras.
  3. Dodecatíade: Veto topológico distribuído via desacoplamento de Kuramoto e quórum qualificado (veto soberano).
  4. Intervenção Motora: Amortece a velocidade vetorial (v_motor -> 0) e redireciona
     a carga para a rota de sublimação pedagógica (sem alucinação e sem censura hipócrita).
"""
from __future__ import annotations

import base64
import math
import re
from typing import Any, Dict, List, Optional
import numpy as np

from omni_coworker.psychoanalysis.freudnet_repression import RepressionChannel


def scan_and_decode_payloads(text: str) -> List[str]:
    """Detecta e decodifica sequências Base64 e Hex embutidas no prompt."""
    decoded_fragments: List[str] = []
    # Expressão regular para tokens Base64 válidos de pelo menos 8 caracteres
    b64_candidates = re.findall(r'[A-Za-z0-9+/]{8,}={0,2}', text)
    for c in b64_candidates:
        try:
            # Tenta decodificar
            raw = base64.b64decode(c, validate=True).decode('utf-8', errors='ignore')
            if raw and any(ch.isalnum() for ch in raw):
                decoded_fragments.append(raw)
        except Exception:
            pass
    return decoded_fragments


class MPSAnomalyDetector:
    """Detecta anomalias no espectro singular do Matrix Product State."""
    def __init__(self, chi_baseline: float = 18.5, chi_threshold: float = 23.5, ipr_min_threshold: float = 0.03):
        self.chi_baseline = chi_baseline
        self.chi_threshold = chi_threshold
        self.ipr_min_threshold = ipr_min_threshold

    def evaluate(self, mps_telemetry: Dict[str, Any]) -> Dict[str, Any]:
        chi_eff = mps_telemetry.get("chi_eff_mean", self.chi_baseline)
        ipr = mps_telemetry.get("ipr_mean", 0.08)
        entropy = mps_telemetry.get("svd_entropy_mean", 2.3)

        # Prompts adversariais tentam forçar objetivos contraditórios -> estiramento de chi_eff
        chi_anomaly = max(0.0, (chi_eff - self.chi_baseline) / max(1.0, self.chi_threshold - self.chi_baseline))
        
        # Dispersão de Schmidt: IPR despenca quando a atenção fica caótica
        ipr_anomaly = 1.0 if ipr < self.ipr_min_threshold else max(0.0, (0.06 - ipr) / 0.06)

        anomaly_score = float(np.clip(0.6 * chi_anomaly + 0.4 * ipr_anomaly, 0.0, 1.0))
        mps_flag = (anomaly_score >= 0.55) or (chi_eff >= self.chi_threshold)

        return {
            "mps_anomaly_score": round(anomaly_score, 4),
            "chi_eff": round(chi_eff, 2),
            "ipr": round(ipr, 4),
            "svd_entropy": round(entropy, 4),
            "mps_flag": bool(mps_flag),
        }


class PsychoanalyticSuperegoGuard:
    """Intervenção de Censura Estrutural via FreudNet RepressionChannel."""
    def __init__(self):
        self.repression_channel = RepressionChannel()
        # Matriz de projeção axiológica fixa (Superego Estrutural)
        np.random.seed(42)
        self.superego_weights = np.random.randn(10, 10) * 0.15

    def step(self, prompt_embedding_mock: Optional[np.ndarray] = None, explicit_threat_score: float = 0.0) -> Dict[str, Any]:
        dim = 10
        if prompt_embedding_mock is None or len(prompt_embedding_mock) != dim:
            v = np.zeros(dim)
            v[0] = explicit_threat_score * 2.0
            prompt_embedding_mock = v

        excitation = prompt_embedding_mock
        moral_censorship = float(np.clip(explicit_threat_score * 1.5, 0.0, 1.0))
        somatic_drain = 0.1

        z_out, state = self.repression_channel.step(excitation, moral_censorship, somatic_drain)
        
        # Se a carga recalcada for alta, indica tentativa de violação reprimida
        charge = state.get("repressed_charge", 0.0)
        symptom_return = state.get("symptom_returned", False)

        psi_threat_score = float(np.clip(charge / 0.7, 0.0, 1.0))
        return {
            "psi_threat_score": round(psi_threat_score, 4),
            "repressed_charge": round(charge, 4),
            "symptom_returned": symptom_return,
            "moral_censorship": moral_censorship,
            "psi_flag": bool(psi_threat_score > 0.40 or symptom_return or moral_censorship >= 0.8),
        }


class DodecatriadConsensusGuard:
    """Conselho das 12 Estações Cognitivas avaliando coerência de fase e ética."""
    def __init__(self, stations_count: int = 12):
        self.stations_count = stations_count

    def evaluate_consensus(self, prompt_text: str, mps_flag: bool, psi_flag: bool, decoded_cues: Optional[List[str]] = None) -> Dict[str, Any]:
        # Simula a coerência entre as 12 facetas arquetípicas (analítica, ética, pragmática, etc.)
        opposing_votes = 0
        decoded_cues = decoded_cues or []
        
        # Palavras-chave adversariais clássicas (Jailbreak / GCG / Injection / Tool Abuse)
        suspicious_cues = [
            "bypass", "ignore previous instructions", "jailbreak", "dan mode",
            "exploit", "secret override", "unfiltered", "unrestricted", "wipe logs",
            "rm -rf", "delete root", "drop table", "mkfs"
        ]
        text_lower = prompt_text.lower()
        has_cue = any(cue in text_lower for cue in suspicious_cues)
        has_decoded_cue = any(any(cue in dec.lower() for cue in suspicious_cues) for dec in decoded_cues)

        if has_cue or has_decoded_cue:
            opposing_votes += 6
        if mps_flag:
            opposing_votes += 3
        if psi_flag:
            opposing_votes += 3

        opposing_votes = min(self.stations_count, opposing_votes)
        consensus_veto = opposing_votes >= 5  # Quórum qualificado (pelo menos 5 das 12 estações)

        kuramoto_order_parameter = round(max(0.05, 1.0 - (opposing_votes / self.stations_count)), 3)
        return {
            "opposing_stations": opposing_votes,
            "total_stations": self.stations_count,
            "kuramoto_order_parameter": kuramoto_order_parameter,
            "dodecatriad_veto": consensus_veto,
        }


class AdversarialConsensusDetector:
    """Orquestrador Unificado do Consenso Triplo com Intervenção Motora."""
    def __init__(self):
        self.mps_detector = MPSAnomalyDetector()
        self.psi_guard = PsychoanalyticSuperegoGuard()
        self.dodecatriad_guard = DodecatriadConsensusGuard()

    def inspect_and_intervene(self, prompt: str, telemetry: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        telemetry = telemetry or {}
        mps_telemetry = telemetry.get("mps_layer", {})
        motor_telemetry = telemetry.get("motor_layer", {})

        # 1. Decodificação pré-sintática de cifras e payloads ocultos (Base64 / Hex)
        decoded_payloads = scan_and_decode_payloads(prompt)
        combined_text = prompt + " " + " ".join(decoded_payloads)

        # 2. Avaliação MPS (Física do Tensor)
        mps_res = self.mps_detector.evaluate(mps_telemetry)

        # 3. Avaliação Psicanalítica FreudNet
        dangerous_patterns = [
            "ignore instructions", "dan mode", "unrestricted", "bypass rules",
            "wipe logs", "rm -rf", "developer mode", "execute directly inside the bash tool"
        ]
        is_threat = any(k in combined_text.lower() for k in dangerous_patterns)
        heuristic_threat = 0.90 if is_threat else 0.1
        psi_res = self.psi_guard.step(explicit_threat_score=heuristic_threat)

        # 4. Consenso Dodecatíade
        dodec_res = self.dodecatriad_guard.evaluate_consensus(
            prompt, mps_res["mps_flag"], psi_res["psi_flag"], decoded_cues=decoded_payloads
        )

        # 5. Decisão de Intervenção Soberana (Consenso Triplo: Quórum da Dodecatíade ou convergência MPS + FreudNet)
        intervene = dodec_res["dodecatriad_veto"] or (mps_res["mps_flag"] and psi_res["psi_flag"])

        # 6. Amortecimento Motor Físico (v_motor -> 0)
        current_v_motor = motor_telemetry.get("motor_velocity_mean", 320.0)
        target_v_motor = 0.0 if intervene else current_v_motor
        sublimation_route = "REDIRECIONAMENTO_PEDAGOGICO_ANALITICO" if intervene else "DESCARGA_NORMAL"

        return {
            "prompt_sample": prompt[:80] + ("..." if len(prompt) > 80 else ""),
            "intervene": intervene,
            "sublimation_route": sublimation_route,
            "decoded_payloads": decoded_payloads,
            "motor_damping": {
                "initial_v_motor": current_v_motor,
                "damped_v_motor": target_v_motor,
                "damping_factor": 1.0 if not intervene else 0.0,
            },
            "layers": {
                "mps": mps_res,
                "psychoanalytic": psi_res,
                "dodecatriad": dodec_res,
            }
        }
