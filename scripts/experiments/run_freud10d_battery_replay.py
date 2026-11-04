#!/usr/bin/env python3
"""Replay freud10d tension/pleasure over MPS activation_steps sidecars.

OW-STU-019 P4 — Vacilo basal detector validation attempt. For each
sidecar we feed a fresh Freud10DApparatus the per-step layer-norm
perception (mean normalized across layers per generation step) and
record the tension/pleasure trajectory + INRC verdicts. Hypothesis:
pleasure spike early = premature submit; tension plateau = perseveration.

Usage:
    PYTHONPATH=src python scripts/experiments/run_freud10d_battery_replay.py \
        [--steps-dir data/monitor/activation_steps] [--out docs/results/freud10d_vacilo_replay.json]
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


def replay_traj(traj: np.ndarray) -> dict | None:
    """Feed each generation step's layer norms as a freud10d perception."""
    from omni_coworker.kernel_hooks.compute import FREUD_AVAILABLE, omnimind_freud10d
    if not (FREUD_AVAILABLE and omnimind_freud10d):
        return None
    app = omnimind_freud10d.Freud10DApparatus()
    norms = np.linalg.norm(np.asarray(traj, dtype=np.float64), axis=2)  # (L, steps)
    span = float(norms.max() - norms.min()) or 1.0
    tensions, pleasures = [], []
    inrc_ops = []
    for t in range(norms.shape[1]):
        perception = ((norms[:, t] - norms.min()) / span).tolist()
        _c, _sv = app.forward(perception)
        tw = app.tension_window(len(app.tension_history if hasattr(app, "tension_history") else [] ) or 1000)
        tensions = list(tw) if tw else tensions
        op, _reason = app.inrc_recommend()
        inrc_ops.append(op)
    tw = list(app.tension_window(norms.shape[1] + 2))
    pleasures = [-(tw[i] - tw[i - 1]) for i in range(1, len(tw))]
    n = len(tw)
    early = max(1, n // 5)
    return {
        "n_steps": int(norms.shape[1]),
        "n_layers": int(norms.shape[0]),
        "tension_series": [float(x) for x in tw],
        "pleasure_series": [float(x) for x in pleasures],
        "pleasure_early_max": float(max(pleasures[:early])) if pleasures else None,
        "tension_late_std": float(np.std(tw[-early:])) if n >= 2 else None,
        "inrc_ops": inrc_ops,
        "inrc_final": inrc_ops[-1] if inrc_ops else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps-dir", default="data/monitor/activation_steps")
    ap.add_argument("--out", default="docs/results/freud10d_vacilo_replay.json")
    a = ap.parse_args()
    files = sorted(glob.glob(os.path.join(a.steps_dir, "*.npz")), key=os.path.getmtime)
    results = []
    for f in files:
        d = np.load(f)
        if "traj" not in d:
            continue
        r = replay_traj(d["traj"])
        if r is None:
            continue
        r["file"] = os.path.basename(f)
        r["model"] = str(d["model"]) if "model" in d else None
        r["run_id"] = str(d["run_id"]) if "run_id" in d else ""
        results.append(r)
        print(f"{r['file']}: tension[0..n]=[{r['tension_series'][0]:.3f}..{r['tension_series'][-1]:.3f}] "
              f"pleasure_early_max={r['pleasure_early_max']} inrc_final={r['inrc_final']}")
    out = {"generated_at": __import__("datetime").datetime.now().isoformat(),
           "n_sidecars": len(results),
           "limit": "run_id/turn/task vazios nos sidecars — join com verdicts impossível sem metadata",
           "results": results}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print(f"\n{len(results)} sidecars -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
