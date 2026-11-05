"""psychoanalysis.freudnet_repression — canal de retorno do recalcado (numpy).

Orquestração runtime / Runtime orchestration:
    `RepressionChannel.step(excitation, moral_censorship, somatic_drain)`
    mantém um vetor tensional z: a excitação entra, a parcela censurada
    (recalque) é desviada para `repressed_charge`/`repressed_content`
    (EMA), e quando a carga reprimida ultrapassa o limiar com histerese,
    parte dela retorna ao vetor z como formação sintomática — deslocada
    (roll de 7 posições) e distorcida (sin × 2.5), nunca o conteúdo
    literal. Função de estado puro, sem I/O, sem torch.

Arquitetura / Architecture:
    Port numpy de src/cognitive/psychoanalytic_mesh.py (FreudNet,
    linhas ~67-178) do omnimind-kilombo-sovereign — canal de retorno do
    recalcado registrado como pendência 16 do OW-STU-014. Constantes
    idênticas ao fonte: threshold=0.7 (descarga), return_threshold=0.5,
    return_rate=0.3, return_hysteresis=0.15, displacement_shift=7,
    EMA 0.9/0.1. Diferenças vs original: sem torch/batch (vetor 1-D),
    `superego_projection` (nn.Linear treinável) virou matriz fixa
    semeada — a censura é estrutural, não aprendida; lane externa de
    reinjecção pulsional não portada (governança host-only, mesma
    decisão documentada no fonte).

Princípios teóricos invocados / Theoretical principles:
    Retorno do recalcado (Freud, 1915): a carga reprimida não se
    dissolve — ultrapassado o limiar, retorna como sintoma. O sintoma é
    formação de compromisso: deslocado na cadeia representacional e
    distorcido por condensação não-linear. A histerese impede oscilação
    liga/desliga da trava return_active.

pt-BR: o recalcado volta — carga reprimida retorna ao estado tensional
    como sintoma deslocado/distorcido quando o limiar é ultrapassado.
"""

from __future__ import annotations

from typing import Any

import numpy as np


class RepressionChannel:
    """Canal de retorno do recalcado (FreudNet, escala worker, numpy)."""

    def __init__(self, latent_dim: int = 64, threshold: float = 0.7,
                 return_threshold: float = 0.5, return_rate: float = 0.3,
                 return_hysteresis: float = 0.15,
                 displacement_shift: int = 7, seed: int = 0) -> None:
        self.latent_dim = int(latent_dim)
        self.threshold = float(threshold)
        self.return_threshold = float(return_threshold)
        self.return_rate = float(return_rate)
        self.return_hysteresis = float(return_hysteresis)
        self.displacement_shift = int(displacement_shift)
        rng = np.random.default_rng(seed)
        self._W_superego = rng.normal(
            0.0, 1.0 / np.sqrt(self.latent_dim),
            size=(self.latent_dim, self.latent_dim))
        self._b_superego = np.zeros(self.latent_dim)
        self.reset_state()

    def reset_state(self) -> None:
        self.z = np.zeros(self.latent_dim)
        self.repressed_charge = 0.0
        self.repressed_content = np.zeros(self.latent_dim)
        self.return_active = False
        self.return_events = 0
        self.symptom_formation = 0.0

    def step(self, excitation: np.ndarray,
             moral_censorship: float = 0.5,
             somatic_symptom_drain: float = 0.0,
             ) -> tuple[np.ndarray, dict[str, Any]]:
        """Um passo da dinâmica tensional + retorno do recalcado."""
        warnings: list[str] = []
        exc = np.asarray(excitation, dtype=float).reshape(-1)
        if exc.size != self.latent_dim:
            exc = np.resize(exc, self.latent_dim)
        if np.isnan(exc).any():
            warnings.append("Excitation contains NaNs")
            exc = np.nan_to_num(exc)

        # Censura do Superego (matriz fixa semeada) + máscara repressiva
        censorship = _sigmoid(self._W_superego @ self.z + self._b_superego)
        censorship = censorship * float(moral_censorship)
        repressive_mask = _sigmoid(np.abs(exc) - self.threshold)
        recalque = repressive_mask * exc * censorship

        self.repressed_charge = (self.repressed_charge * 0.9
                                 + float(np.mean(np.abs(recalque))))
        self.repressed_content = (self.repressed_content * 0.9
                                  + recalque * 0.1)

        self.z = np.tanh(self.z + exc - recalque)

        # Descargas homeostáticas (motora + dreno psicossomático)
        discharge = np.zeros_like(self.z)
        idx = np.abs(self.z) > self.threshold
        discharge[idx] = self.z[idx] * 0.5
        drain = self.z * float(somatic_symptom_drain) * 0.3
        self.z = self.z - discharge - drain

        # Trava de retorno com histerese
        if self.return_active:
            if self.repressed_charge <= (self.return_threshold
                                         - self.return_hysteresis):
                self.return_active = False
                warnings.append("Return-of-the-repressed exhausted - hysteresis rearmed")
        elif self.repressed_charge > self.return_threshold:
            self.return_active = True
            warnings.append("Repressed charge exceeded return threshold - symptom formation!")

        symptom = np.zeros_like(self.z)
        if self.return_active and self.repressed_charge > 0.0:
            return_mass = min(self.return_rate * self.repressed_charge,
                              self.repressed_charge)
            displaced = np.roll(self.repressed_content,
                                shift=self.displacement_shift, axis=-1)
            symptom = np.sin(displaced * 2.5) * return_mass
            self.z = np.tanh(self.z + symptom)
            self.repressed_charge = max(0.0, self.repressed_charge - return_mass)
            self.return_events += 1

        self.symptom_formation = float(np.mean(np.abs(symptom)))
        loss_local = float(np.mean(np.abs(self.z)))
        return self.z.copy(), {
            "z_state": self.z.copy(),
            "repressed_charge": self.repressed_charge,
            "return_active": self.return_active,
            "return_events": self.return_events,
            "symptom_formation": self.symptom_formation,
            "tension_loss": loss_local,
            "regime": "colapso" if loss_local > 0.8 else "estavel",
            "warnings": warnings,
        }


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30.0, 30.0)))
