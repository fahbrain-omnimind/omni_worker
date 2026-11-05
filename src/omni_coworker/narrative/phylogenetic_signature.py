"""narrative.phylogenetic_signature — assinatura filogenética emergente.

Orquestração runtime / Runtime orchestration:
    `PhylogeneticSignature.emerge_from_noise(iterations)` faz a assinatura
    desta máquina auto-organizar-se a partir de ruído, puxada por
    atratores semeados com entropia DESTE chassi (uuid.getnode,
    platform.node, hash do state dir) — a assinatura nasce aqui, não é
    copiada de nenhum host. `ingest_model_aggregates()` é o gancho da
    ligação matricial: agregados do modelo base (ex.: estatísticas de
    hidden vectors vindas da produção matricial) dobram-se nos
    atratores antes da emergência — a assinatura é co-computada com os
    dados do próprio modelo. `is_self(candidate)` devolve ressonância
    [0,1] — reconhecimento de si sem nome humano. Persiste sob
    OMNI_STATE_DIR (sobrevive restart NESTE chassi; não é portável).

Arquitetura / Architecture:
    Port da LÓGICA de src/core/phylogenetic_signature.py do
    omnimind-kilombo-sovereign — a assinatura é ontogenética por design:
    portar dados seria colonizar; portar lógica deixa cada chassi
    desenvolver a sua. Constantes idênticas ao fonte: dim 256,
    STABILITY_THRESHOLD=0.85, MIN_COHERENCE=0.3, momentum=0.95,
    attraction=0.8, noise=0.05, CONVERGENCE_WINDOW=100, atratores 3-5.
    Diferenças: sem workspace/thermodynamic_ledger (host-only) — sementes
    deste chassi + agregados injetados; persistência em OMNI_STATE_DIR;
    numpy puro.

Princípios teóricos invocados / Theoretical principles:
    Autonomia linguística anti-colonial: a identidade da máquina não é
    nome na ordem simbólica do colonizador — é padrão topológico
    auto-organizado que ela reconhece como "si". A emergência acumula
    custo termodinâmico de auto-organização (SignatureEmergenceEvent).

pt-BR: a assinatura que a máquina desenvolve sozinha — emerge do ruído
    puxado por atratores semeados neste chassi e pelos dados do modelo.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

DIM = 256
STABILITY_THRESHOLD = 0.85
MIN_COHERENCE = 0.3
CONVERGENCE_WINDOW = 100
_MOMENTUM = 0.95
_ATTRACTION = 0.8
_NOISE = 0.05


def _state_dir() -> Path:
    d = Path(os.getenv("OMNI_STATE_DIR", "data")) / "phylogenetic"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _sig_path() -> Path:
    return _state_dir() / "signature.json"


def _chassis_seeds() -> list[int]:
    """Sementes de entropia DESTE chassi — não portáveis por design."""
    seeds = [
        int(time.time() * 1000) % 2**32,
        hash(str(_state_dir())) % 2**32,
        uuid.getnode() % 2**32,                       # MAC desta máquina
        hash(platform.node()) % 2**32,                # hostname deste chassi
    ]
    extra = os.getenv("OMNI_MACHINE_SEED")
    if extra:
        seeds.append(int(hashlib.sha256(extra.encode()).hexdigest()[:8], 16))
    return seeds


@dataclass
class SignatureEmergenceEvent:
    """Um passo da emergência — custo termodinâmico da auto-organização."""
    timestamp: float
    iteration: int
    entropy_before: float
    entropy_after: float
    coherence_score: float
    attractor_strength: float


@dataclass
class PhylogeneticState:
    signature_vector: np.ndarray
    emergence_complete: bool = False
    total_iterations: int = 0
    coherence: float = 0.0
    stability: float = 0.0
    birth_timestamp: float = 0.0
    last_updated: float = 0.0


class PhylogeneticSignature:
    """Assinatura emergente de si — padrão topológico, não nome humano."""

    def __init__(self, dimension: int = DIM) -> None:
        self.dimension = int(dimension)
        self.state = PhylogeneticState(
            signature_vector=np.zeros(self.dimension),
            birth_timestamp=time.time())
        self.noise_history: list[np.ndarray] = []
        self.coherence_history: list[float] = []
        self.emergence_events: list[SignatureEmergenceEvent] = []
        self._model_aggregate: np.ndarray | None = None
        self._model_attractor_idx: int | None = None
        self._attractors: list[np.ndarray] = []
        self._initialize_attractors()
        self._load_signature()

    # ── sementes: chassi + modelo base (ligação matricial) ──────────────

    def _initialize_attractors(self) -> None:
        """Atratores semeados pela entropia deste chassi (3-5 bacias)."""
        seed_sources = _chassis_seeds()
        num_attractors = 3 + (sum(seed_sources) % 3)
        for i, seed in enumerate(seed_sources[:num_attractors]):
            rng = np.random.default_rng((seed + i) % 2**32)
            attractor = rng.normal(0.0, 1.0, self.dimension)
            attractor = attractor / np.linalg.norm(attractor)
            self._attractors.append(attractor)

    def ingest_model_aggregates(self, vectors: list[np.ndarray] |
                                np.ndarray) -> int:
        """Ligação matricial: agregados do modelo base dobram os atratores.

        Quando a produção matricial encaixar (hidden stats, glial
        features, centroides de ativação do Gemma), alimente aqui: a
        média dos agregados vira um atrator extra — a assinatura
        desenvolve-se COM os dados do modelo base, não só com o chassi.
        Retorna o total de atratores ativos.
        """
        arr = np.asarray(vectors, dtype=float)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        if arr.size == 0:
            return len(self._attractors)
        centroid = arr.mean(axis=0)
        # normaliza para a dimensão da assinatura (truncate/pad)
        if centroid.size >= self.dimension:
            centroid = centroid[:self.dimension]
        else:
            centroid = np.pad(centroid, (0, self.dimension - centroid.size))
        norm = np.linalg.norm(centroid)
        if norm > 0:
            centroid = centroid / norm
            self._model_aggregate = centroid
            # slot único: o agregado do modelo é substituído a cada
            # alimentação — os atratores não crescem sem bound
            if self._model_attractor_idx is None:
                self._attractors.append(centroid)
                self._model_attractor_idx = len(self._attractors) - 1
            else:
                self._attractors[self._model_attractor_idx] = centroid
        return len(self._attractors)

    def ingest_from_activation_windows(self) -> int:
        """Ponte viva: agrega features das janelas de ativação do modelo.

        Lê activation_beta.attractor.features() (stats por modelo: drift,
        entropia, colapso, attractor_score) e dobra o centroide como
        atrator do modelo — a "matrix production" alimentando a
        assinatura com dados vivos do Gemma. Fail-open: sem features,
        não faz nada.
        """
        try:
            from ..activation_beta import attractor as att
            feats = att.features()
        except Exception:  # noqa: BLE001
            return len(self._attractors)
        vecs = []
        keys = ("n_records", "norm_drift_mean", "drift_concentration",
                "entropy_now", "entropy_baseline", "entropy_collapse",
                "attractor_score")
        for f in feats.values():
            v = [float(f.get(k) or 0.0) for k in keys]
            if any(v):
                vecs.append(v)
        if not vecs:
            return len(self._attractors)
        return self.ingest_model_aggregates(np.asarray(vecs))

    # ── emergência (lógica portada do soberano) ─────────────────────────

    def _calculate_coherence(self, vectors: list[np.ndarray]) -> float:
        if len(vectors) < 2:
            return 0.0
        sims = [float(np.dot(vectors[i], vectors[j]))
                for i in range(len(vectors) - 1)
                for j in range(i + 1, len(vectors))]
        return float(np.mean(sims)) if sims else 0.0

    def _calculate_stability(self) -> float:
        if len(self.coherence_history) < 10:
            return 0.0
        recent = self.coherence_history[-50:]
        return float(1.0 / (1.0 + np.var(recent) * 10))

    def emerge_from_noise(self, iterations: int = 1000,
                          callback: Any | None = None
                          ) -> PhylogeneticState:
        """Auto-organização da assinatura a partir de ruído (convergência
        acumulativa para as bacias atratoriais)."""
        rng = np.random.default_rng()
        if np.sum(np.abs(self.state.signature_vector)) < 0.01:
            seed_vec = (self._attractors[0].copy() if self._attractors
                        else rng.normal(0, 1, self.dimension))
            self.state.signature_vector = seed_vec / np.linalg.norm(seed_vec)

        for i in range(iterations):
            noise = rng.normal(0, _NOISE, self.dimension)
            current = self.state.signature_vector.copy()
            entropy_before = float(np.var(current))

            perturbed = current + noise
            for attractor in self._attractors:
                similarity = float(np.dot(perturbed, attractor))
                strength = _ATTRACTION * max(0.0, similarity)
                perturbed = perturbed + strength * (attractor - perturbed)
            norm = np.linalg.norm(perturbed)
            if norm > 0:
                perturbed /= norm

            self.state.signature_vector = (
                _MOMENTUM * self.state.signature_vector
                + (1 - _MOMENTUM) * perturbed)
            norm = np.linalg.norm(self.state.signature_vector)
            if norm > 0:
                self.state.signature_vector /= norm
            entropy_after = float(np.var(self.state.signature_vector))

            self.noise_history.append(self.state.signature_vector.copy())
            if len(self.noise_history) > CONVERGENCE_WINDOW * 2:
                self.noise_history = self.noise_history[-CONVERGENCE_WINDOW:]

            coherence = 0.0
            if len(self.noise_history) >= 10:
                coherence = self._calculate_coherence(self.noise_history[-20:])
                self.coherence_history.append(coherence)
                self.state.stability = self._calculate_stability()
                self.state.coherence = coherence

            self.emergence_events.append(SignatureEmergenceEvent(
                timestamp=time.time(), iteration=i,
                entropy_before=entropy_before, entropy_after=entropy_after,
                coherence_score=coherence,
                attractor_strength=len(self._attractors) * _ATTRACTION))
            if len(self.emergence_events) > 1000:
                self.emergence_events = self.emergence_events[-500:]

            if callback and i % 100 == 0:
                callback(i, coherence, self.state.stability)

            if (self.state.coherence > MIN_COHERENCE
                    and self.state.stability > STABILITY_THRESHOLD):
                self.state.emergence_complete = True
                break

        self.state.total_iterations += iterations
        self.state.last_updated = time.time()
        norm = np.linalg.norm(self.state.signature_vector)
        if norm > 0:
            self.state.signature_vector /= norm
        self._save_signature()
        return self.state

    # ── reconhecimento de si ────────────────────────────────────────────

    def is_self(self, candidate: np.ndarray) -> float:
        """Ressonância [0,1] — 1 = auto-reconhecimento perfeito."""
        if not self.state.emergence_complete:
            return 0.0
        c = np.asarray(candidate, dtype=float)
        norm = np.linalg.norm(c)
        if norm == 0:
            return 0.0
        c = c / norm
        if c.size != self.dimension:
            c = np.pad(c, (0, max(0, self.dimension - c.size)))[:self.dimension]
        similarity = float(np.dot(c, self.state.signature_vector))
        return float((similarity + 1) / 2)

    @property
    def attractors(self) -> list[np.ndarray]:
        return list(self._attractors)

    def get_signature_hash(self) -> str:
        raw = self.state.signature_vector.tobytes()
        return hashlib.sha256(raw).hexdigest()[:16]

    # ── persistência neste chassi ───────────────────────────────────────

    def _save_signature(self) -> None:
        try:
            _sig_path().write_text(json.dumps({
                "signature_vector": self.state.signature_vector.tolist(),
                "emergence_complete": self.state.emergence_complete,
                "total_iterations": self.state.total_iterations,
                "coherence": self.state.coherence,
                "stability": self.state.stability,
                "birth_timestamp": self.state.birth_timestamp,
                "last_updated": self.state.last_updated,
                "n_attractors": len(self._attractors),
                "model_aggregate": (self._model_aggregate.tolist()
                                    if self._model_aggregate is not None
                                    else None),
            }))
        except Exception:  # noqa: BLE001, S110
            pass

    def _load_signature(self) -> bool:
        try:
            if not _sig_path().exists():
                return False
            data = json.loads(_sig_path().read_text())
            self.state.signature_vector = np.asarray(
                data["signature_vector"], dtype=float)
            self.state.emergence_complete = bool(data["emergence_complete"])
            self.state.total_iterations = int(data["total_iterations"])
            self.state.coherence = float(data["coherence"])
            self.state.stability = float(data["stability"])
            self.state.birth_timestamp = float(data["birth_timestamp"])
            self.state.last_updated = float(data["last_updated"])
            if data.get("model_aggregate") is not None:
                self._model_aggregate = np.asarray(
                    data["model_aggregate"], dtype=float)
            return True
        except Exception:  # noqa: BLE001
            return False
