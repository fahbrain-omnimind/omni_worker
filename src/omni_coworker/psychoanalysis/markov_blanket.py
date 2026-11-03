"""markov_blanket.py — Poincaré Markov blanket + PyPhi-ready TPM.

English: faithful port of the sovereign's clinical Markov blanket
dynamics (poincare_markov_blanket.py + simulate_prior_conflict_hyperbolic.py,
livro §19/B§9). Belief μ evolves on the Poincaré disk via Möbius addition,
modulated by resistance r, permeability, transference axis τ, under a
therapeutic-ambiguity gain α.

The blanket supplies what PyPhi needs and generic telemetry lacks:
PRINCIPLED elements (FEP partition: internal {M,R,T} vs external {Z}
coupled through sensory error + active prediction channels) and a real
transition structure. The 4 causal nodes → 16 states → coarse-grained
TPM (Monte Carlo over consistent microstates) → exact Φ within PyPhi's
~10-node ceiling. This is the only scale at which IIT is computable
here — the blanket boundary, not the whole runtime.

pt-BR: port fiel da dinâmica do Markov blanket soberano. O blanket dá
elementos principiados (partição FEP) + estrutura de transição — o
requisito do PyPhi que telemetria genérica não tem. TPM coarse-grained
via Monte Carlo; Φ exato factível a 4 nós.

Labels (OW-MATH-001): the TPM is [PRX-data]; Φ computed by PyPhi on it
is [EXP] — a real IIT-3.0 computation over a coarse-grained abstraction
of the blanket dynamics, never a consciousness measure of the worker.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

# Node order — the blanket's minimal causal organs.
NODES = ("Z", "M", "R", "T")

# Sovereign constants (simulate_prior_conflict_hyperbolic.py —
# DO NOT tune: they reproduce the livro §19/B§9 simulation).
TARGET = np.array([0.6, 0.4])          # prior_target
ETA = 0.25                            # base learning rate
DECAY = 0.88                          # resistance decay λ
RHO = 0.15                            # resistance gain ρ
ETA_TRANS = 0.08                      # transference learning rate
TAU0 = np.array([0.8, -0.2])          # initial transference axis
Z_FLIP_P = 0.03                       # P(world-regime flip)/step (~t=30 shift, Markovized)
NOISE_STD = 0.03                      # sovereign noise magnitude (Markov-safe stochastic)

# Binarization thresholds — the sovereign's own classification constants.
Z_THRESH = 0.3    # z[0] regime split (early [0.1,-0.1] vs late [0.62,0.38])
M_THRESH = 0.3    # dH(mu, target) — "Nova crença estabilizada" criterion
R_THRESH = 0.4    # "Resistance" criterion
E_THRESH = 0.3    # "Symptomatic regression" error criterion (observable)


def mobius_add(u: np.ndarray, v: np.ndarray) -> np.ndarray:
    """Möbius addition in the Poincaré disk (|x|<1)."""
    u = np.asarray(u, dtype=float)
    v = np.asarray(v, dtype=float)
    uv = float(np.dot(u, v))
    uu = float(np.dot(u, u))
    vv = float(np.dot(v, v))
    num = (1 + 2 * uv + vv) * u + (1 - uu) * v
    den = 1 + 2 * uv + uu * vv
    return num / max(den, 1e-12)


def hyperbolic_dist(u: np.ndarray, v: np.ndarray) -> float:
    """Poincaré disk distance."""
    u = np.asarray(u, dtype=float)
    v = np.asarray(v, dtype=float)
    diff = u - v
    num = 2.0 * float(np.dot(diff, diff))
    den = (1.0 - float(np.dot(u, u))) * (1.0 - float(np.dot(v, v)))
    arg = 1.0 + num / max(den, 1e-12)
    return float(np.arccosh(max(1.0, arg)))


@dataclass
class BlanketState:
    """Continuous microstate of the clinical blanket."""
    mu: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0]))
    r: float = 0.0
    tau: np.ndarray = field(default_factory=lambda: TAU0.copy())


def blanket_step(state: BlanketState, z: np.ndarray, alpha: float,
                 noise: np.ndarray, rng: np.random.Generator) -> tuple[BlanketState, dict]:
    """One dynamics step — sovereign-faithful.

    English: observation → prediction error → Möbius belief update →
    transference/resistance/permeability. Returns new state + observables.
    z flips regime with probability Z_FLIP_P (Markov version of the
    deterministic t=30 shift in the sovereign sim).
    """
    z = np.asarray(z, dtype=float)
    if rng.random() < Z_FLIP_P:
        z = np.array([0.62, 0.38]) if z[0] <= Z_THRESH else np.array([0.1, -0.1])

    y = z + noise
    y_hat = state.mu * (1.0 - 0.25 * state.r)
    error = y - y_hat
    error_mag = float(np.linalg.norm(error))

    mu_norm_sq = float(np.dot(state.mu, state.mu))
    error_l1 = error + state.tau * (1.0 - mu_norm_sq)
    tau_next = state.tau + ETA_TRANS * error_l1
    m = float(np.linalg.norm(tau_next))
    if m > 0.0:
        state.tau = (tau_next / m) * 0.8

    if alpha > 0.7:
        permeability = 0.1 + 0.8 * abs(math.sin(rng.random() * math.pi))
    else:
        permeability = 0.5 * (1.0 - alpha) + 0.4 * (1.0 - state.r)
    permeability = max(0.05, min(0.95, permeability))

    gain = 1.0 / (1.0 + state.r * 1.8) * (1.0 - alpha * 0.6)
    state.mu = mobius_add(state.mu, ETA * gain * error)

    phi_res = max(0.0, float(np.dot(error, state.tau))) ** 2
    state.r = max(0.0, min(1.0, DECAY * state.r + RHO * phi_res))

    observ = {
        "error": error, "error_mag": error_mag,
        "permeability": permeability, "gain": gain,
        "dH": hyperbolic_dist(state.mu, TARGET),
    }
    return state, observ


def binarize(z: np.ndarray, state: BlanketState, observ: dict) -> tuple:
    """Continuous microstate → 4 node bits (Z, M, R, T).

    English: the coarse-graining map — each bit is a sovereign-defined
    clinical threshold, not an arbitrary discretization.
    """
    return (
        int(z[0] > Z_THRESH),
        int(observ["dH"] <= M_THRESH),
        int(state.r >= R_THRESH),
        int(state.tau[0] > 0.0),
    )


def _sample_consistent(bits: tuple, rng: np.random.Generator,
                       max_tries: int = 4000) -> tuple:
    """Rejection-sample a continuous (z, mu, r, tau) matching node bits."""
    zb, mb, rb, tb = bits
    for _ in range(max_tries):
        if zb:
            z = np.array([0.62, 0.38]) + rng.normal(0, 0.05, 2)
            if z[0] <= Z_THRESH:
                continue
        else:
            z = np.array([0.1, -0.1]) + rng.normal(0, 0.05, 2)
            if z[0] > Z_THRESH:
                continue
        while True:
            mu = rng.uniform(-0.9, 0.9, 2)
            if np.dot(mu, mu) < 0.9 ** 2:
                break
        st = BlanketState(mu=mu,
                          r=float(rng.uniform(R_THRESH, 1.0) if rb
                                  else rng.uniform(0.0, R_THRESH)))
        th = rng.uniform(0, 2 * math.pi)
        tau = np.array([math.cos(th), math.sin(th)]) * 0.8
        if (tau[0] > 0.0) != bool(tb):
            continue
        # M bit depends on dH of the *post-step* mu; approximate with the
        # pre-step distance — close enough for coarse-graining, and the
        # honest alternative (pre-imaging the map) costs orders more.
        if (hyperbolic_dist(mu, TARGET) <= M_THRESH) != bool(mb):
            continue
        st.tau = tau
        return z, st
    raise RuntimeError(f"no consistent microstate for bits {bits}")


def build_tpm(alpha: float, k: int = 600, seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """Coarse-grained TPM over the 4 blanket nodes via Monte Carlo.

    English: for each of the 16 binary states, sample K consistent
    microstates, run one sovereign-faithful step (with noise + z-flip),
    count next binary states → joint TPM (16×16). Also returns the
    state-by-node marginals PyPhi's sbn format would use.

    pt-BR: para cada estado binário, K microestados consistentes → um
    passo da dinâmica soberana → TPM conjunta 16×16 + marginais s×n.
    """
    rng = np.random.default_rng(seed)
    n = len(NODES)
    joint = np.zeros((2 ** n, 2 ** n))
    for s_idx in range(2 ** n):
        bits = tuple((s_idx >> (n - 1 - i)) & 1 for i in range(n))
        counts = np.zeros(2 ** n)
        tried = 0
        for _ in range(k):
            try:
                z, st = _sample_consistent(bits, rng)
            except RuntimeError:
                tried += 1
                if tried > 3:
                    break
                continue
            noise = rng.normal(0, NOISE_STD, 2)
            st2, obs = blanket_step(st, z, alpha, noise, rng)
            nxt = binarize(z, st2, obs)
            n_idx = sum(b << (n - 1 - i) for i, b in enumerate(nxt))
            counts[n_idx] += 1
        total = counts.sum()
        joint[s_idx] = counts / total if total > 0 else 0.0
    # state-by-node marginals: sbn[s][j] = P(node j ON at t+1 | s)
    sbn = np.zeros((2 ** n, n))
    for s_idx in range(2 ** n):
        for j in range(n):
            sbn[s_idx, j] = sum(joint[s_idx, ns] for ns in range(2 ** n)
                                if (ns >> (n - 1 - j)) & 1)
    return joint, sbn


def connectivity_matrix() -> np.ndarray:
    """Directed effective connectivity at node grain (from→to).

    English: Z drives everything through the error channel; M persists
    and drives ŷ→error→{R,T}; R modulates gain + distorts ŷ → {M,R,T};
    T feeds resistance (φ=⟨e,τ⟩) and persists. No arrows into Z (world).
    """
    # order Z M R T; cm[i][j] = i → j
    return np.array([
        [1, 1, 1, 1],   # Z → Z,M,R,T (via sensory error channel)
        [0, 1, 1, 1],   # M → M,R,T (prediction → error)
        [0, 1, 1, 1],   # R → M,R,T (gain + distortion)
        [0, 0, 1, 1],   # T → R,T (resistance alignment + persistence)
    ], dtype=float)
