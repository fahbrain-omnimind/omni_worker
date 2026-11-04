#!/usr/bin/env python3
"""run_freud10d_battery_replay — detector basal do Vacilo sobre ativações/sidecars.

Orquestração runtime / Runtime orchestration:
    Reproduz trajetórias de geração `(L, steps, D)` (`activation_steps/*.npz`)
    ou séries de normas de camadas (`activation_vectors/*.npz` / JSONL)
    através do aparato psíquico `FreudianPsychicApparatus` (numpy puro ou
    crate `omnimind_freud10d` quando compilado) para extrair:
      - `pleasure_early_max`: pico de alívio de tensão (Δtension < 0) no
        primeiro terço da geração (hipótese P4: spike cedo = submissão
        prematura em modelos táticos como E4B);
      - `tension_plateau_ratio`: fração de passos nos dois terços finais
        com tensão sustentada alta e baixa descarga de prazer (hipótese P4:
        plateau = perseveração / ruminação em modelos analíticos como 12B);
      - `vacilo_regime`: classificação estrutural [CLS/EXP] entre
        `premature_closure_risk`, `perseveration_plateau_risk` e `balanced`.

Regra de integridade (AGENTS.md):
    NUNCA gera nem salva resultados sintéticos como se fossem execuções reais.
    Se nenhum sidecar `.npz` for encontrado no diretório alvo, retorna
    `status="NÃO LOCALIZADO"` com contagem 0.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from omni_coworker.psychoanalysis.freudian_apparatus_numpy import FreudianPsychicApparatus


def analyze_trajectory_vacilo(arr: np.ndarray, seed: int = 42) -> dict[str, Any]:
    """Run FreudianPsychicApparatus over a trajectory and compute Vacilo metrics."""
    a = np.asarray(arr, dtype=np.float64)
    if a.ndim == 3:
        # (L, steps, D) -> sequence of step summaries across layers (steps, L)
        steps_seq = np.linalg.norm(a, axis=-1).T  # shape (steps, L)
    elif a.ndim == 2:
        # (L, D) -> treat layers as sequential depth steps of summary norms/slices
        steps_seq = a[:, : min(32, a.shape[1])]
    else:
        steps_seq = a.reshape(1, -1)

    n_steps = steps_seq.shape[0]
    app = FreudianPsychicApparatus(
        n_id=16, n_ego=32, n_superego=8, input_dim=steps_seq.shape[1], seed=seed
    )

    tensions: list[float] = []
    pleasure_deltas: list[float] = []
    prev_pleasure = 0.0

    for t in range(n_steps):
        vec = steps_seq[t]
        norm = float(np.linalg.norm(vec))
        vec_norm = vec / norm if norm > 1e-12 else vec
        res = app.forward(vec_norm)
        tensions.append(float(res["tension"]))
        p_now = float(res["pleasure"])
        pleasure_deltas.append(max(0.0, p_now - prev_pleasure))
        prev_pleasure = p_now

    early_cut = max(1, n_steps // 3)
    early_pleasures = pleasure_deltas[:early_cut]
    late_tensions = tensions[early_cut:] if n_steps > 1 else tensions

    pleasure_early_max = float(max(early_pleasures)) if early_pleasures else 0.0
    tension_mean = float(np.mean(tensions)) if tensions else 0.0
    tension_std_late = float(np.std(late_tensions)) if len(late_tensions) > 1 else 0.0
    plateau_ratio = float(
        np.mean([1.0 if t >= 0.85 * tension_mean else 0.0 for t in late_tensions])
    ) if late_tensions and tension_mean > 0 else 0.0

    if pleasure_early_max > 0.35 and (late_tensions and late_tensions[-1] < 0.75 * tensions[0]):
        regime = "premature_closure_risk"
    elif plateau_ratio >= 0.75 and pleasure_early_max < 0.15:
        regime = "perseveration_plateau_risk"
    else:
        regime = "balanced"

    return {
        "n_steps": int(n_steps),
        "pleasure_early_max": round(pleasure_early_max, 4),
        "tension_mean": round(tension_mean, 4),
        "tension_std_late": round(tension_std_late, 4),
        "tension_plateau_ratio": round(plateau_ratio, 4),
        "total_pleasure": round(float(app.pleasure), 4),
        "total_unpleasure": round(float(app.unpleasure), 4),
        "vacilo_regime": regime,
        "scale": "freud10d/numpy trajectory replay [PRX/EXP]",
    }


def replay_directory(steps_dir: Path) -> dict[str, Any]:
    """Replay all .npz sidecars in `steps_dir` without fabricating data."""
    if not steps_dir.is_dir():
        return {"status": "NÃO LOCALIZADO", "dir": str(steps_dir), "n_files": 0, "records": []}
    files = sorted(steps_dir.glob("*.npz"))
    if not files:
        return {"status": "NÃO LOCALIZADO", "dir": str(steps_dir), "n_files": 0, "records": []}
    records = []
    for f in files:
        try:
            z = np.load(f)
            arr = z["trajectory"] if "trajectory" in z else z["vectors"]
            metrics = analyze_trajectory_vacilo(arr)
            records.append({"file": f.name, **metrics})
        except Exception as e:
            records.append({"file": f.name, "error": str(e)})
    return {"status": "DADO", "dir": str(steps_dir), "n_files": len(files), "records": records}


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay Freud10D Vacilo detector over sidecars.")
    parser.add_argument("--dir", type=Path, default=Path("data/monitor/activation_steps"))
    args = parser.parse_args()
    res = replay_directory(args.dir)
    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
