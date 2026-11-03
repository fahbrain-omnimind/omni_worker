"""freudian_apparatus_numpy — aparato psíquico freudiano em numpy puro.

Orquestração runtime / Runtime orchestration:
Port numpy-puro de `src/consciousness/freudian_neural_apparatus.py` do
sovereign (OW-STU-012: SKIP no daemon por torch → versão numpy). Sem
torch/structlog: logging padrão. Três camadas (id, ego, superego) com
fluxo id→ego→superego, neurônios com soma W·x+b, ativação (tanh/sigmoid)
e plasticidade hebbiana leve. Alimenta o worker (CPU/RAM) sem GPU.

Arquitetura / Architecture:
- `FreudianNeuron`: neurônio denso com pesos, bias, ativação e plasticidade.
- `FreudianNeuralLayer`: camada de n neurônios, forward numpy, ruído opcional.
- `FreudianPsychicApparatus`: 3 camadas (id/ego/superego) + projeções
  id→ego e ego→superego; `forward(x)` retorna dict com ativações.
- `to_numpy`: helper de conversão (ndarray/tensor/list/dict).

Princípios teóricos invocados / Theoretical principles:
Freud (1895/1900/1923) + neuropsicanálise preditiva; id/ego/superego
como camadas neurais com dinâmicas de tensão, prazer/desprazer e defesa.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import numpy as np

logger = logging.getLogger(__name__)

_ACTIVATIONS = ("tanh", "sigmoid", "relu", "identity")


def _as_array(x: Any) -> np.ndarray:
    try:
        import torch  # type: ignore

        if isinstance(x, torch.Tensor):
            return x.detach().cpu().numpy().astype(float)
    except Exception:
        pass
    if isinstance(x, dict):
        return {k: _as_array(v) for k, v in x.items()}  # type: ignore
    if isinstance(x, (list, tuple)):
        return np.asarray(x, dtype=float)
    if isinstance(x, np.ndarray):
        return np.asarray(x, dtype=float)
    return np.asarray(x, dtype=float)


def to_numpy(x: Any = None) -> Any:
    """Helper de conversão para numpy (suporta tensor/list/dict/None)."""
    if x is None:
        return None
    if isinstance(x, dict):
        return {k: to_numpy(v) for k, v in x.items()}
    try:
        import torch  # type: ignore

        if isinstance(x, torch.Tensor):
            return x.detach().cpu().numpy()
    except Exception:
        pass
    if isinstance(x, np.ndarray):
        return np.asarray(x)
    try:
        return np.asarray(x)
    except Exception:
        return x


def _activate(name: str, x: np.ndarray) -> np.ndarray:
    name = (name or "tanh").lower()
    if name == "sigmoid":
        return 1.0 / (1.0 + np.exp(-np.clip(x, -30.0, 30.0)))
    if name == "relu":
        return np.maximum(0.0, x)
    if name == "identity":
        return x
    return np.tanh(x)


def _kw(kwargs: dict, *names: str, default: Any = None) -> Any:
    for n in names:
        if n in kwargs and kwargs[n] is not None:
            return kwargs.pop(n)
    return default


def _align(a: np.ndarray, n: int) -> np.ndarray:
    a = np.asarray(a, dtype=float).reshape(-1)
    if a.size == n:
        return a
    if a.size > n:
        return a[:n]
    out = np.zeros(n, dtype=float)
    out[: a.size] = a
    return out


class FreudianNeuron:
    """Neurônio freudiano denso (W·x + b, ativação, plasticidade hebbiana)."""

    def __init__(
        self,
        n_inputs: Optional[int] = None,
        activation: str = "tanh",
        seed: Optional[int] = None,
        weights: Any = None,
        bias: Any = None,
        neuron_id: Optional[str] = None,
        neuron_type: Optional[str] = None,
        **kwargs,
    ) -> None:
        if n_inputs is None:
            n_inputs = _kw(kwargs, "input_dim", "in_features", "input_size",
                           "n_inputs", "features", default=1)
        if n_inputs is None:
            n_inputs = 1
        self.n_inputs = int(n_inputs) if n_inputs is not None else 1
        self.activation = _kw(kwargs, "activation", default=activation) or activation
        self.seed = 0 if seed is None else int(seed)
        self.neuron_id = neuron_id
        self.neuron_type = neuron_type
        self.rng = np.random.default_rng(self.seed)
        if weights is None:
            self.weights = None
        else:
            self.weights = np.asarray(weights, dtype=float).reshape(-1)
            self.n_inputs = int(self.weights.size)
        if bias is None:
            self.bias = 0.0
        else:
            self.bias = float(np.asarray(bias).reshape(-1)[0]) if np.asarray(bias).size else 0.0
        # compat fields (sovereign)
        self.cathexis = 0.0
        self.barrier_resistance = 1.0
        self.facilitation = 0.0
        self._initialized = self.weights is not None

    def _ensure(self, x: np.ndarray) -> None:
        if self.weights is None or self.weights.size != x.size:
            rng = np.random.default_rng(self.seed)
            self.n_inputs = int(x.size)
            self.weights = rng.normal(0.0, 0.1, size=self.n_inputs)
            self.bias = 0.0
            self._initialized = True

    def forward(self, x: Any) -> float:
        x = np.asarray(x, dtype=float).reshape(-1)
        self._ensure(x)
        x = _align(x, self.weights.size)
        s = float(np.dot(self.weights, x) + self.bias)
        out = _activate(self.activation, np.asarray([s]))[0]
        self.cathexis = float(out)
        return float(out)

    __call__ = forward

    def plasticity(self, pre: Any, post: Any, lr: float = 0.01) -> None:
        self.hebbian_update(pre, post, lr=lr)

    def hebbian_update(self, pre: Any, post: Any, lr: float = 0.01) -> None:
        pre = np.asarray(pre, dtype=float).reshape(-1)
        post_scalar = float(np.asarray(post, dtype=float).reshape(-1)[0]) if np.asarray(post).size else 0.0
        if self.weights is None:
            self._ensure(pre)
        pre = _align(pre, self.weights.size)
        self.weights = self.weights + float(lr) * post_scalar * pre
        self.bias = self.bias + float(lr) * post_scalar
        self.facilitation = self.facilitation + 0.1 * abs(post_scalar)

    def hebbian(self, *a, **k) -> None:
        self.hebbian_update(*a, **k)

    def to_numpy(self) -> np.ndarray:
        if self.weights is None:
            return np.asarray([], dtype=float)
        return np.asarray(self.weights, dtype=float)


class FreudianNeuralLayer:
    """Camada com n neurônios, forward numpy, ruído opcional."""

    def __init__(
        self,
        n_neurons: Optional[int] = None,
        input_dim: Optional[int] = None,
        activation: str = "tanh",
        noise: float = 0.0,
        seed: Optional[int] = None,
        **kwargs,
    ) -> None:
        if n_neurons is None:
            n_neurons = _kw(kwargs, "n", "size", "units", "num_neurons",
                            "out_features", "output_dim", "n_neurons", default=4)
        if n_neurons is None:
            n_neurons = 4
        self.n_neurons = int(n_neurons)
        if input_dim is None:
            input_dim = _kw(kwargs, "input_dim", "input_size", "in_features",
                            "input_features", "n_inputs", "features", default=None)
        self.input_dim = None if input_dim is None else int(input_dim)
        self.activation = _kw(kwargs, "activation", default=activation) or activation
        self.noise = float(_kw(kwargs, "noise", "noise_std", "noise_level", default=noise))
        if self.noise is None:
            self.noise = 0.0
        self.seed = 0 if seed is None else int(seed)
        self.rng = np.random.default_rng(self.seed)
        self.weights: Optional[np.ndarray] = None
        self.bias: Optional[np.ndarray] = None
        self.neurons: list = []
        if self.input_dim is not None:
            self._init_weights(self.input_dim)
        else:
            self.neurons = [FreudianNeuron(None, activation=self.activation,
                                           seed=self.seed + i) for i in range(self.n_neurons)]

    def _init_weights(self, input_dim: int) -> None:
        input_dim = int(input_dim)
        self.input_dim = input_dim
        rng = np.random.default_rng(self.seed)
        self.weights = rng.normal(0.0, 0.1, size=(self.n_neurons, input_dim))
        self.bias = np.zeros(self.n_neurons, dtype=float)
        self.neurons = [
            FreudianNeuron(input_dim, activation=self.activation, seed=self.seed + i,
                           weights=self.weights[i].copy(), bias=self.bias[i])
            for i in range(self.n_neurons)
        ]

    def _ensure(self, x: np.ndarray) -> None:
        if self.weights is None:
            self._init_weights(x.size)

    def forward(self, x: Any, noise: Optional[float] = None, **kwargs) -> np.ndarray:
        x = np.asarray(x, dtype=float).reshape(-1)
        self._ensure(x)
        x = _align(x, self.weights.shape[1])
        out = self.weights @ x + self.bias
        out = _activate(self.activation, out)
        ns = self.noise if noise is None else float(noise)
        if kwargs.get("noise_std") is not None:
            ns = float(kwargs["noise_std"])
        if ns and ns > 0:
            out = out + self.rng.normal(0.0, ns, size=out.shape)
        # sync neurons
        for i, n in enumerate(self.neurons):
            n.weights = self.weights[i].copy()
            n.bias = float(self.bias[i])
        return np.asarray(out, dtype=float)

    __call__ = forward

    def hebbian_update(self, pre: Any, post: Any, lr: float = 0.01) -> None:
        pre = np.asarray(pre, dtype=float).reshape(-1)
        post = np.asarray(post, dtype=float).reshape(-1)
        if self.weights is None:
            self._ensure(pre)
        pre = _align(pre, self.weights.shape[1])
        post = _align(post, self.weights.shape[0])
        self.weights = self.weights + float(lr) * np.outer(post, pre)
        self.bias = self.bias + float(lr) * post
        for n in self.neurons:
            pass

    def hebbian(self, *a, **k) -> None:
        self.hebbian_update(*a, **k)

    def plasticity(self, *a, **k) -> None:
        self.hebbian_update(*a, **k)

    def to_numpy(self) -> np.ndarray:
        if self.weights is None:
            return np.asarray([], dtype=float)
        return np.asarray(self.weights, dtype=float)


class FreudianPsychicApparatus:
    """Aparato psíquico: camadas id→ego→superego (numpy puro)."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        n_id = _kw(kwargs, "n_id", "id_neurons", "id_size", "id_dim",
                    "id_units", "num_id", "n_neurons_id", default=None)
        n_ego = _kw(kwargs, "n_ego", "ego_neurons", "ego_size", "ego_dim",
                    "ego_units", "num_ego", "n_neurons_ego", default=None)
        n_sup = _kw(kwargs, "n_superego", "superego_neurons", "superego_size",
                    "superego_dim", "superego_units", "num_superego",
                    "n_neurons_superego", "n_sup", default=None)
        input_dim = _kw(kwargs, "input_dim", "input_size", "in_features",
                        "input_features", "n_inputs", "features", "input", default=None)
        seed = _kw(kwargs, "seed", "random_seed", "rng_seed", default=0)
        if seed is None:
            seed = 0
        self.seed = int(seed)
        noise = _kw(kwargs, "noise", "noise_std", "noise_level", default=0.0)
        if noise is None:
            noise = 0.0
        self.noise = float(noise)
        activation = _kw(kwargs, "activation", default="tanh") or "tanh"

        pos = list(args)
        if n_id is None and pos:
            n_id = pos.pop(0)
        if n_ego is None and pos:
            n_ego = pos.pop(0)
        if n_sup is None and pos:
            n_sup = pos.pop(0)
        if input_dim is None and pos:
            input_dim = pos.pop(0)

        if n_id is None:
            n_id = 16
        if n_ego is None:
            n_ego = 32
        if n_sup is None:
            n_sup = 8
        self.n_id = int(n_id)
        self.n_ego = int(n_ego)
        self.n_superego = int(n_sup)
        if input_dim is not None:
            input_dim = int(input_dim)
        self.input_dim = input_dim

        self.id_layer = FreudianNeuralLayer(self.n_id, input_dim=self.input_dim,
                                            activation=activation, noise=self.noise,
                                            seed=self.seed)
        self.ego_layer = FreudianNeuralLayer(self.n_ego, input_dim=self.n_id,
                                             activation=activation, noise=self.noise,
                                             seed=self.seed + 1)
        self.superego_layer = FreudianNeuralLayer(self.n_superego,
                                                  input_dim=self.n_ego,
                                                  activation=activation,
                                                  noise=self.noise,
                                                  seed=self.seed + 2)
        # aliases
        self.id = self.id_layer
        self.ego = self.ego_layer
        self.superego = self.superego_layer
        self.layers = {"id": self.id_layer, "ego": self.ego_layer,
                       "superego": self.superego_layer}

        r2 = np.random.default_rng(self.seed + 10)
        self.W_id_ego = r2.normal(0.0, 0.1, size=(self.n_ego, self.n_id))
        self.b_id_ego = np.zeros(self.n_ego, dtype=float)
        r3 = np.random.default_rng(self.seed + 20)
        self.W_ego_superego = r3.normal(0.0, 0.1, size=(self.n_superego, self.n_ego))
        self.b_ego_superego = np.zeros(self.n_superego, dtype=float)

        self.tension = 0.0
        self.pleasure = 0.0
        self.unpleasure = 0.0
        self._prev_tension = 0.0
        self.last_output: Optional[Dict[str, Any]] = None
        self.activation = activation
        logger.info("FreudianPsychicApparatus numpy inicializado (id=%d, ego=%d, superego=%d)",
                    self.n_id, self.n_ego, self.n_superego)

    def _forward_one(self, x: np.ndarray, noise: Optional[float] = None) -> Dict[str, Any]:
        x = np.asarray(x, dtype=float).reshape(-1)
        id_act = self.id_layer.forward(x, noise=noise)
        ego_input = self.W_id_ego @ id_act + self.b_id_ego
        ego_act = self.ego_layer.forward(ego_input, noise=noise)
        sup_input = self.W_ego_superego @ ego_act + self.b_ego_superego
        sup_act = self.superego_layer.forward(sup_input, noise=noise)

        id_arr = np.asarray(id_act, dtype=float)
        ego_arr = np.asarray(ego_act, dtype=float)
        sup_arr = np.asarray(sup_act, dtype=float)

        self.tension = float(np.sum(np.abs(ego_arr)))
        delta = self.tension - self._prev_tension
        if delta < 0:
            self.pleasure += abs(delta)
        else:
            self.unpleasure += delta
        self._prev_tension = self.tension

        result: Dict[str, Any] = {
            "id": id_arr,
            "ego": ego_arr,
            "superego": sup_arr,
            "id_layer": id_arr,
            "ego_layer": ego_arr,
            "superego_layer": sup_arr,
            "id_activation": id_arr,
            "ego_activation": ego_arr,
            "superego_activation": sup_arr,
            "output": sup_arr,
            "activations": {"id": id_arr, "ego": ego_arr, "superego": sup_arr},
            "tension": self.tension,
            "pleasure": self.pleasure,
            "unpleasure": self.unpleasure,
            "state": {"tension": self.tension, "pleasure": self.pleasure,
                      "unpleasure": self.unpleasure},
        }
        self.last_output = result
        return result

    def forward(self, x: Any, noise: Optional[float] = None, **kwargs) -> Any:
        if noise is None and kwargs.get("noise") is not None:
            noise = kwargs.get("noise")
        x_arr = np.asarray(x, dtype=float)
        if x_arr.ndim <= 1:
            return self._forward_one(x_arr, noise=noise)
        out_list = [self._forward_one(row, noise=noise) for row in x_arr]
        combined: Dict[str, Any] = {}
        for key in out_list[0]:
            vals = [o[key] for o in out_list]
            if isinstance(vals[0], np.ndarray):
                combined[key] = np.stack(vals)
            elif isinstance(vals[0], dict):
                combined[key] = {k: np.stack([o[key][k] for o in out_list])
                                 for k in vals[0]}
            else:
                combined[key] = vals
        self.last_output = combined
        return combined

    __call__ = forward

    def learn_association(self, perception: Any, target: Any, lr: float = 0.01) -> None:
        try:
            self.id_layer.forward(perception)
        except Exception:
            pass
        # hebbian-ish update on id layer
        try:
            self.id_layer.hebbian_update(perception, self.last_output["id"] if self.last_output else perception, lr=lr)
        except Exception:
            pass

    def defense_mechanism(self, threatening: Any) -> np.ndarray:
        t = np.asarray(threatening, dtype=float).reshape(-1)
        out = t.copy()
        idx = np.where(t > 0.8)[0]
        out[idx] *= 0.3
        return out

    def wish_fulfillment(self, wish: Any) -> np.ndarray:
        w = np.asarray(wish, dtype=float).reshape(-1)
        # regress to id space roughly
        res = self.forward(w)
        return np.asarray(res["superego"], dtype=float)

    def get_psychic_metrics(self) -> Dict[str, float]:
        return {
            "tension": self.tension,
            "pleasure": self.pleasure,
            "unpleasure": self.unpleasure,
            "pleasure_balance": self.pleasure - self.unpleasure,
            "id_facilitation": float(np.mean(self.id_layer.weights)) if self.id_layer.weights is not None else 0.0,
        }

    def to_numpy(self, x: Any = None) -> Any:
        if x is None:
            x = self.last_output
        return to_numpy(x)


# backward-compat aliases for sovereign-style names
FreudianApparatus = FreudianPsychicApparatus
FreudianLayer = FreudianNeuralLayer
FreudianApparatusNumpy = FreudianPsychicApparatus
