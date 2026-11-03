"""activation_beta.attractor_bench — benches atratoriais executáveis (numpy).

Orquestração runtime / Runtime orchestration:
    Implementações pequenas mas REAIS de redes atratoriais usadas como
    probes do regime dinâmico do worker: `Hopfield` (Hebb clássico,
    recall síncrono, energia -1/2 s'Ws) e `RBM` (contrastive divergence
    CD-1, Bernoulli visível/oculta, Gibbs 1 passo). Benches:
    `bench_energy_perturbation` (tempo de recuperação à bacia após
    perturbação), `bench_dmn_proxy` (dwell time alternando atratores em
    dinâmica espontânea — proxy DMN de wander) e
    `bench_rbm_vs_hopfield` (A/B de recall sob ruído).

Arquitetura / Architecture:
    Itens 24/25 do OW-STU-014 — o worker não tinha lane atratorial
    executável (nem Hopfield nem RBM). Aqui ambos numpy puro, sem torch.
    NÃO é port do soberano (cuja escala é GPU/mesh); é a lane mínima
    honesta para o A/B Hopfield-vs-RBM poder ser chamado sem metáfora.

Princípios teóricos invocados / Theoretical principles:
    Atratores (Hopfield 1982; Hinton 2002): memória como bacia de
    energia — recall é descida gradiente até o padrão armazenado. DMN:
    dinâmica de repouso alterna atratores; dwell time baixo = wander
    saudável, dwell preso = colapso em uma bacia. LIMITE: redes de
    16-64 unidades são probes de regime, não modelos de escala.

pt-BR: benches atratoriais executáveis — Hopfield e RBM reais (pequenos),
    probes de energia e de dinâmica espontânea para o worker.
"""

from __future__ import annotations

from typing import Any

import numpy as np


class Hopfield:
    """Rede de Hopfield clássica (bipolar ±1, recall síncrono, energia real)."""

    def __init__(self, n: int, seed: int = 0) -> None:
        self.n = int(n)
        self.W = np.zeros((n, n))
        self._rng = np.random.default_rng(seed)
        self.patterns: list[np.ndarray] = []

    def store(self, patterns: np.ndarray) -> None:
        """Hebb: W = mean over patterns of p p' (diagonal 0)."""
        P = np.asarray(patterns, dtype=float)
        P = np.where(P > 0, 1.0, -1.0)
        for p in P:
            self.W += np.outer(p, p)
        np.fill_diagonal(self.W, 0.0)
        self.W /= len(P)
        self.patterns = [p.copy() for p in P]

    def energy(self, s: np.ndarray) -> float:
        return float(-0.5 * s @ self.W @ s)

    def recall(self, cue: np.ndarray, max_iters: int = 30) -> tuple[np.ndarray, int]:
        """Recall síncrono até estabilizar; retorna (padrão, iters)."""
        s = np.where(np.asarray(cue, dtype=float) > 0, 1.0, -1.0).copy()
        for it in range(1, max_iters + 1):
            s_new = np.where(self.W @ s >= 0.0, 1.0, -1.0)
            if np.array_equal(s_new, s):
                return s_new, it
            s = s_new
        return s, max_iters

    def recall_accuracy(self, cue: np.ndarray) -> float:
        """Overlap máximo com os padrões armazenados após recall."""
        s, _ = self.recall(cue)
        if not self.patterns:
            return 0.0
        best = max(float(np.mean(s == p)) for p in self.patterns)
        return best


class RBM:
    """Restricted Boltzmann Machine mínima — CD-1 real (Hinton 2002)."""

    def __init__(self, n_visible: int, n_hidden: int, seed: int = 0) -> None:
        self.n_v = int(n_visible)
        self.n_h = int(n_hidden)
        rng = np.random.default_rng(seed)
        self.W = rng.normal(0.0, 0.1, (self.n_v, self.n_h))
        self.b_v = np.zeros(self.n_v)
        self.b_h = np.zeros(self.n_h)
        self._rng = rng

    def _sigmoid(self, x: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-np.clip(x, -30.0, 30.0)))

    def hidden_probs(self, v: np.ndarray) -> np.ndarray:
        return self._sigmoid(v @ self.W + self.b_h)

    def visible_probs(self, h: np.ndarray) -> np.ndarray:
        return self._sigmoid(h @ self.W.T + self.b_v)

    def _sample(self, p: np.ndarray) -> np.ndarray:
        return (self._rng.random(p.shape) < p).astype(float)

    def gibbs_step(self, v: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Um passo Gibbs: v→h→v'. Retorna (h_sample, v')."""
        h = self._sample(self.hidden_probs(v))
        v1 = self._sample(self.visible_probs(h))
        return h, v1

    def train_step(self, v: np.ndarray, lr: float = 0.1) -> float:
        """CD-1: ΔW ∝ <vh>data - <vh>model. Retorna erro de reconstrução."""
        v = np.asarray(v, dtype=float)
        ph_data = self.hidden_probs(v)
        h_sample = self._sample(ph_data)
        v_recon_p = self.visible_probs(h_sample)
        v_recon = self._sample(v_recon_p)
        ph_recon = self.hidden_probs(v_recon)
        self.W += lr * (np.outer(v, ph_data) - np.outer(v_recon, ph_recon))
        self.b_v += lr * (v - v_recon)
        self.b_h += lr * (ph_data - ph_recon)
        return float(np.mean((v - v_recon_p) ** 2))

    def free_energy(self, v: np.ndarray) -> float:
        """F(v) = -b_v·v - Σ softplus(b_h + vW)."""
        v = np.asarray(v, dtype=float)
        hidden_term = np.sum(np.logaddexp(0.0, v @ self.W + self.b_h))
        return float(-v @ self.b_v - hidden_term)

    def reconstruct(self, cue: np.ndarray, steps: int = 3) -> np.ndarray:
        """cue → alterna h/v `steps` vezes → reconstrução probabilística."""
        v = np.asarray(cue, dtype=float)
        for _ in range(steps):
            h_p = self.hidden_probs(v)
            v = self.visible_probs(self._sample(h_p))
        return v


def bench_energy_perturbation(
    hopfield: Hopfield, n_trials: int = 20, flip_frac: float = 0.3,
) -> dict[str, Any]:
    """Perturba padrões armazenados e mede recuperação à bacia."""
    rng = np.random.default_rng(1)
    recover_iters, accuracies = [], []
    for p in hopfield.patterns:
        for _ in range(n_trials // max(len(hopfield.patterns), 1)):
            cue = p.copy()
            flips = rng.choice(hopfield.n,
                               int(hopfield.n * flip_frac), replace=False)
            cue[flips] *= -1
            _, iters = hopfield.recall(cue)
            recover_iters.append(iters)
            accuracies.append(hopfield.recall_accuracy(cue))
    return {"n_trials": len(recover_iters),
            "mean_recovery_iters": float(np.mean(recover_iters)),
            "mean_recall_accuracy": float(np.mean(accuracies)),
            "flip_frac": flip_frac}


def bench_dmn_proxy(
    hopfield: Hopfield, n_steps: int = 200, noise: float = 0.15,
    seed: int = 2,
) -> dict[str, Any]:
    """Dinâmica espontânea: estado salta entre bacias sob ruído.

    Proxy DMN: conta trocas de atrator dominante e dwell time médio.
    Wander saudável → várias trocas; colapso → dwell ≈ n_steps.
    """
    rng = np.random.default_rng(seed)
    if not hopfield.patterns:
        return {"switches": 0, "mean_dwell": 0.0, "dominant": []}
    s = hopfield.patterns[0].copy()
    dwells, cur_dwell, dominant = [], 0, -1
    for _ in range(n_steps):
        s = np.where(hopfield.W @ s +
                     rng.normal(0, noise * hopfield.n ** 0.5, hopfield.n)
                     >= 0, 1.0, -1.0)
        dists = [int(np.sum(s != p)) for p in hopfield.patterns]
        dom = int(np.argmin(dists))
        if dom == dominant:
            cur_dwell += 1
        else:
            if dominant >= 0:
                dwells.append(cur_dwell)
            dominant, cur_dwell = dom, 1
    dwells.append(cur_dwell)
    return {"switches": max(len(dwells) - 1, 0),
            "mean_dwell": float(np.mean(dwells)),
            "dominant": dominant,
            "n_steps": n_steps}


def bench_rbm_vs_hopfield(
    n: int = 32, n_patterns: int = 4, epochs: int = 60,
    flip_frac: float = 0.3, seed: int = 3,
) -> dict[str, Any]:
    """A/B real: Hopfield vs RBM-CD1 no mesmo recall sob ruído.

    Mede overlap médio do recall com o padrão-âncora de cada cue.
    """
    rng = np.random.default_rng(seed)
    patterns = rng.choice([-1.0, 1.0], size=(n_patterns, n))

    hop = Hopfield(n, seed=seed)
    hop.store(patterns)

    rbm = RBM(n, n_hidden=max(8, n_patterns * 2), seed=seed)
    data01 = (patterns + 1.0) / 2.0
    for _ in range(epochs):
        for v in data01:
            rbm.train_step(v, lr=0.1)

    hop_acc, rbm_acc = [], []
    for p in patterns:
        cue = p.copy()
        flips = rng.choice(n, int(n * flip_frac), replace=False)
        cue[flips] *= -1
        hop_acc.append(float(np.mean(hop.recall(cue)[0] == p)))
        recon = rbm.reconstruct((cue + 1.0) / 2.0, steps=3)
        rbm_out = np.where(recon >= 0.5, 1.0, -1.0)
        rbm_acc.append(float(np.mean(rbm_out == p)))
    return {"hopfield_mean_overlap": float(np.mean(hop_acc)),
            "rbm_mean_overlap": float(np.mean(rbm_acc)),
            "epochs": epochs, "flip_frac": flip_frac, "n": n}
