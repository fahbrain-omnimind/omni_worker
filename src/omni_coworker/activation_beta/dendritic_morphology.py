"""activation_beta.dendritic_morphology — dendritic graph morphology (port).

Orquestração runtime / Runtime orchestration:
Port ADAPTADO de `src/consciousness/freud10d/dendritic_morphology.py`
(sovereign, OW-STU-012: ADAPT). Numpy puro (daemon CPU-only). Aplica a
tese de Giseli de Sousa (Hertfordshire, 2012 — menor profundidade média
da árvore dendrítica ⇒ melhor reconhecimento de padrões) ao grafo de
conectividade W entre as 10 dimensões psíquicas do worker (Φ→Ψ→Ω→Θ→Υ→Ξ→Ζ→Η→Κ→Λ
— as mesmas dimensões de `neuroanatomy.py`). `load_worker_weight_matrix`
reconstrói a conectividade freudiana canônica (fallback idêntico ao do
sovereign, sem depender do Freud10DSystem ausente aqui).

Arquitetura / Architecture:
- `dendritic_depth(W)`: caminho médio mais curto entre dimensões (BFS);
- `morphology_score(W)`: 1 − depth/9 (0..1, maior = melhor);
- `prune_deep_connections(W, n_shortcuts)`: atalhos AO LONGO do eixo
  funcional (correção INC-1 do sovereign: atalhos aleatórios destroem a
  estrutura — saltos de comprimento 2/3 no fluxo perceptual);
- `evolve_morphology(...)`: EA restrito ao fluxo funcional (nunca conecta
  dimensões rivais), otimizando 0.6·morphology + 0.4·recognition;
- `_snr_discrimination(W)`: dinâmica tanh(Wx+u) separando 2 atratores —
  morfologias melhores separam mais;
- `compare_depth_vs_recognition(W)`: experimento original/podada/evoluída.

Princípios teóricos invocados / Theoretical principles:
Giseli de Sousa, "Optimization of Neuronal Morphologies for Pattern
Recognition" (PhD, Hertfordshire, 2012; JCN 2015): profundidade média da
árvore dendrítica é anti-correlacionada com reconhecimento; assimetria
não correlaciona. Aplicado ao aparelho psíquico: um psiquismo "raso"
(dimensões diretamente conectadas) discrimina melhor entre estados.

Analogia–homologia (interpretativo):
W é o grafo de conectividade dos SUBSISTEMAS do worker — leitura
estrutural da topologia psíquica, não afirmação biológica.

pt-BR: morfologia dendrítica do grafo psíquico — profundidade, poda
funcional e evolução restrita ao eixo.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np

_N = 10
_MAX_DEPTH = float(_N - 1)


def dendritic_depth(W: np.ndarray) -> float:
    """Mean shortest-path depth of the connectivity graph (BFS)."""
    n = W.shape[0]
    adj = (W > 0.01).astype(float)
    np.fill_diagonal(adj, 0.0)
    total, count = 0.0, 0
    for s in range(n):
        dist = np.full(n, -1)
        dist[s] = 0
        queue = [s]
        while queue:
            u = queue.pop(0)
            for v in range(n):
                if adj[u, v] > 0 and dist[v] < 0:
                    dist[v] = dist[u] + 1
                    queue.append(v)
        for v in range(n):
            if v != s and dist[v] > 0:
                total += dist[v]
                count += 1
    return total / max(1, count)


def morphology_score(W: np.ndarray) -> float:
    """1 − normalized depth (0..1, higher = better morphology)."""
    return float(max(0.0, 1.0 - dendritic_depth(W) / _MAX_DEPTH))


def _functional_pairs(n: int) -> list[tuple[int, int]]:
    """Allowed pairs: functional axis (i→i+1) + functional jumps (i→i+2/3)."""
    pairs = set()
    for i in range(n - 1):
        pairs.add((i, i + 1))
    for i in range(n - 2):
        pairs.add((i, i + 2))
    for i in range(n - 3):
        pairs.add((i, i + 3))
    return sorted(pairs)


def prune_deep_connections(W: np.ndarray, n_shortcuts: int = 3,
                           seed: int = 42) -> np.ndarray:
    """Add functional shortcuts along the perceptual axis (INC-1 fixed)."""
    W2 = W.copy()
    n = W.shape[0]
    added = 0
    for jump in (2, 3):
        for idx in range(0, n - jump, 2):
            if added >= n_shortcuts:
                break
            i, j = idx, idx + jump
            if W2[i, j] < 0.01:
                W2[i, j] = 0.35
                added += 1
        if added >= n_shortcuts:
            break
    return W2


def evolve_morphology(
    W0: np.ndarray,
    n_generations: int = 20,
    pop_size: int = 12,
    seed: int = 7,
    recognition_fn: Callable[[np.ndarray], float] | None = None,
) -> dict[str, Any]:
    """EA restricted to the functional flow (never connects rival dims)."""
    rng = np.random.default_rng(seed)
    n = W0.shape[0]
    allowed_list = _functional_pairs(n)

    def _mutate(W: np.ndarray) -> np.ndarray:
        Wm = W.copy()
        for _ in range(int(rng.integers(1, 4))):
            i, j = allowed_list[int(rng.integers(0, len(allowed_list)))]
            if rng.random() < 0.5:
                Wm[i, j] = float(np.clip(Wm[i, j] + rng.normal(0, 0.15), 0.0, 1.0))
            else:
                Wm[i, j] = float(np.clip(Wm[i, j] + rng.random() * 0.3, 0.0, 1.0))
        if rng.random() < 0.2:
            for i in range(n):
                for j in range(n):
                    if (i, j) not in allowed_list and Wm[i, j] < 0.15:
                        Wm[i, j] = 0.0
        return Wm

    pop = [W0.copy()]
    for _ in range(pop_size - 1):
        pop.append(_mutate(W0))

    history: list[dict[str, Any]] = []
    for gen in range(n_generations):
        scores = []
        for W in pop:
            ms = morphology_score(W)
            rec = recognition_fn(W) if recognition_fn else 0.5
            scores.append(0.6 * ms + 0.4 * rec)
        order = np.argsort(scores)[::-1]
        pop = [pop[i] for i in order[: pop_size // 2]]
        history.append({"gen": gen, "best_score": float(scores[order[0]])})
        while len(pop) < pop_size:
            parent = pop[int(rng.integers(0, len(pop)))]
            pop.append(_mutate(parent))

    best = pop[0]
    return {
        "best_W": best,
        "best_morphology_score": float(morphology_score(best)),
        "best_depth": float(dendritic_depth(best)),
        "history": history,
    }


def _snr_discrimination(W: np.ndarray, n_steps: int = 30, seed: int = 0) -> float:
    """Discrimination SNR between two attractors under tanh dynamics."""
    rng = np.random.default_rng(seed)
    n = W.shape[0]
    attractor_A = np.zeros(n)
    attractor_A[0] = 0.9
    attractor_A[1] = 0.7
    attractor_B = np.zeros(n)
    attractor_B[5] = 0.9
    attractor_B[6] = 0.7

    def _run(x0: np.ndarray) -> np.ndarray:
        x = x0.copy()
        for _ in range(n_steps):
            x = np.tanh(W @ x + 0.05 * rng.standard_normal(n))
        return x

    sep_total = 0.0
    for s in range(5):
        rng2 = np.random.default_rng(seed + s)
        xA = _run(attractor_A + 0.1 * rng2.standard_normal(n))
        xB = _run(attractor_B + 0.1 * rng2.standard_normal(n))
        sep_total += float(np.linalg.norm(xA - xB))
    return sep_total / 5.0


def compare_depth_vs_recognition(W_base: np.ndarray) -> dict[str, Any]:
    """Central experiment: depth × SNR for original/pruned/evolved."""
    results: list[dict[str, Any]] = [
        {"morphology": "original", "depth": float(dendritic_depth(W_base)),
         "snr": float(_snr_discrimination(W_base))},
    ]
    for k in (1, 2, 3, 5):
        Wp = prune_deep_connections(W_base, n_shortcuts=k, seed=42 + k)
        results.append({"morphology": f"pruned_{k}",
                        "depth": float(dendritic_depth(Wp)),
                        "snr": float(_snr_discrimination(Wp))})
    evo = evolve_morphology(W_base, n_generations=15, pop_size=10, seed=7)
    results.append({"morphology": "evolved",
                    "depth": float(evo["best_depth"]),
                    "snr": float(_snr_discrimination(evo["best_W"]))})
    return {"results": results, "evolved_score": evo["best_morphology_score"]}


def load_worker_weight_matrix() -> np.ndarray:
    """Canonical Freudian connectivity W (10×10) for the worker.

    English: Same fallback as the sovereign's dendritic module — the
    worker has no Freud10DSystem, so the canonical Freudian chain is
    rebuilt here (Id→Ego 0.9, etc.). Shared with neuroanatomy dims order.
    pt-BR: Reconstrói a conectividade freudiana canônica (fallback do
    sovereign) — sem dependência do Freud10DSystem ausente no worker.
    """
    n = _N
    W = np.zeros((n, n))
    W[0, 1] = 0.8   # Phi → Psi
    W[1, 2] = 0.7   # Psi → Omega
    W[1, 3] = 0.6   # Psi → Theta
    W[3, 4] = 0.3   # Theta → Upsilon
    W[4, 1] = 0.2   # Upsilon → Psi
    W[1, 5] = 0.45  # Psi → Xi
    W[4, 5] = 0.75  # Upsilon → Xi (Id)
    W[3, 6] = 0.55  # Theta → Zeta
    W[5, 6] = 0.9   # Xi → Zeta (Id→Ego, pulsão→realidade)
    W[6, 7] = 0.5   # Zeta → Eta (Ego→Superego)
    W[7, 1] = 0.4   # Eta → Psi (Superego vigia memória)
    W[6, 8] = 0.6   # Zeta → Kappa (transferência)
    W[8, 9] = 0.5   # Kappa → Lambda (sublimação)
    W[9, 0] = 0.3   # Lambda → Phi (sublimação realimenta percepção)
    np.fill_diagonal(W, 0.2)
    return W