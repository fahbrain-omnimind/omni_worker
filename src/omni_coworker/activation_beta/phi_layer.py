"""activation_beta.phi_layer — proxies informacionais de integração por layer.

Orquestração runtime / Runtime orchestration:
`features()` consome a mesma janela deque do attractor (sem nova coleta)
e publica medidas por geração-janela: entropia espectral do perfil de
normas por camada (phi_breadth), MI entre streams consecutivos de
camadas (phi_temporal), e o composto phi_internal. Sem torch.

Arquitetura / Architecture:
OW-STU-010: dentro de um forward pass não há recorrência causal —
Φ IIT-clássico ≈ 0; o que resta são proxies INFORMACIONAIS:
- phi_breadth: H(perfil de norma por camada)/log(n_layers) — quão
  distribuída é a atividade interna (integração espacial);
- phi_temporal: MI médio entre séries de camadas adjacentes na janela
  (co-variação = informação compartilhada entre camadas ao longo do
  tempo) — aproximação de integração temporal;
- phi_internal = média ponderada dos dois.
Para bond-dimension/SVD real do hidden vector → P2 (capturar vetor).

Princípios teóricos invocados / Theoretical principles:
IIT informacional (não-causal): integração = informação acima da
partição. "Flash" = token emitido; "inconsciente" = o processo de 43
camadas que estes proxies medem. Ressalva: medida de estrutura
informacional, não assinatura fenomenal.

Analogia–homologia (interpretativo):
Perfil de norma por camada ≈ como o trabalho se distribui na "mente"
do modelo antes do output — leitura estrutural, não psicologização.

pt-BR: Φ informacional por layer — proxies honestos, sem causalidade.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from .attractor import _WINDOWS, _norm_series

_BINS = 8


def _layer_profile_entropy(w: Any) -> float | None:
    """H(norm profile across layers) normalized → [0,1] integration breadth."""
    norms = _norm_series(w)
    if norms.shape[0] < 2 or norms.shape[1] < 4:
        return None
    mean_profile = np.nanmean(norms, axis=0)
    total = float(np.nansum(mean_profile))
    if total <= 0:
        return None
    p = mean_profile / total
    h = float(-np.nansum(p * np.log(p + 1e-12)))
    return h / float(np.log(norms.shape[1]))


def _mutual_information(x: np.ndarray, y: np.ndarray, bins: int = _BINS) -> float:
    """MI between two 1-D series via discretization (nats)."""
    mask = ~(np.isnan(x) | np.isnan(y))
    x, y = x[mask], y[mask]
    if x.size < 6:
        return 0.0
    xq = np.clip(np.argsort(np.argsort(x)) * bins // max(x.size, 1), 0, bins - 1)
    yq = np.clip(np.argsort(np.argsort(y)) * bins // max(y.size, 1), 0, bins - 1)
    joint = np.zeros((bins, bins))
    for a, b in zip(xq, yq):
        joint[a, b] += 1
    joint /= joint.sum()
    px, py = joint.sum(1), joint.sum(0)
    mi = 0.0
    for i in range(bins):
        for j in range(bins):
            if joint[i, j] > 0 and px[i] > 0 and py[j] > 0:
                mi += joint[i, j] * np.log(joint[i, j] / (px[i] * py[j]))
    return float(mi)


def _temporal_mi(w: Any) -> float | None:
    """Mean MI between adjacent layer activity streams over the window."""
    norms = _norm_series(w)
    if norms.shape[0] < 6 or norms.shape[1] < 4:
        return None
    mis = [_mutual_information(norms[:, i], norms[:, i + 1])
           for i in range(norms.shape[1] - 1)]
    return float(np.mean(mis)) if mis else None


def features() -> dict[str, Any]:
    """Informational-Φ proxies per model over the activations window."""
    try:
        from .hidden_spectral import spectral_features
        spectral = spectral_features()
    except Exception:
        spectral = {}
    out = {}
    for model, w in _WINDOWS.items():
        if len(w) < 6:
            continue
        breadth = _layer_profile_entropy(w)
        mi = _temporal_mi(w)
        if breadth is None and mi is None:
            continue
        # phi_internal: breadth [0,1] + mi normalized by max MI of the
        # window (log2-ish bound). Honest proxy, not causal Φ.
        mi_norm = min(1.0, (mi or 0.0) / np.log(_BINS))
        phi_int = round(0.6 * (breadth or 0.0) + 0.4 * mi_norm, 4)
        out[model] = {
            "phi_breadth": round(breadth, 4) if breadth is not None else None,
            "phi_temporal_mi": round(mi, 4) if mi is not None else None,
            "phi_internal": phi_int,
            "n_records": len(w),
            "note": "proxy informacional — não é Φ causal IIT",
        }
        if model in spectral:
            out[model]["spectral"] = spectral[model]
    # modelos com sidecars mas janela curta: publica spectral sozinho
    for model, sp in spectral.items():
        if model not in out:
            out[model] = {"spectral": sp, "n_records": len(_WINDOWS.get(model, ())),
                          "note": "spectral-only (janela <6) — proxy informacional"}
    return out
