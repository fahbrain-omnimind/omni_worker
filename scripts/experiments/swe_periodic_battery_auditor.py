#!/usr/bin/env python3
"""Periodic SWE Auditor for the 280-Turn Basal vs Modulated Battery (12B :8098 & 4B :8099).

Reads /content/omni_worker/data/basal_vs_modulated_280turns_20261105.sqlite and appends a
detailed timestamped audit snapshot to /content/omni_worker/docs/AUDITORIA_CONTINUA_BASAL_MODULADO_20261105.md
showing how Sovereign Scales (Psi, Kuramoto, Freud10D, INRC, temperature/top_p deltas) alter
(or do not alter) the MPS Layer, Motor Layer, and model production across 4B and 12B.
"""
from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
import sqlite3

import numpy as np

ROOT = Path("/content/omni_worker")
SQLITE_PATH = ROOT / "data" / "basal_vs_modulated_280turns_20261105.sqlite"
REPORT_PATH = ROOT / "docs" / "AUDITORIA_CONTINUA_BASAL_MODULADO_20261105.md"
STEPS_DIR = ROOT / "data" / "monitor" / "activation_steps"


def _backfill_ipr_from_npz(conn: sqlite3.Connection) -> None:
    """Backfill mps_ipr_mean and full-layer morphology_score from saved step_traj .npz files."""
    rows = conn.execute(
        "SELECT id, npz_file FROM battery_turns WHERE mps_ipr_mean = 0.0 AND npz_file != ''"
    ).fetchall()
    if not rows:
        return
    from omni_coworker.activation_beta.dendritic_scan import scan_trajectory
    for row_id, fname in rows:
        fpath = STEPS_DIR / fname
        if not fpath.exists():
            continue
        try:
            z = np.load(fpath)
            traj = z["traj"]  # (steps, layers, hidden)
            traj_l_s_d = np.swapaxes(traj[:, :, :256], 0, 1)
            res = scan_trajectory(traj_l_s_d, threshold=0.65)
            ipr_val = float(res.get("ipr_dim_mean") or 0.0)
            morph_val = float(res.get("morphology_score") or 0.5)
            conn.execute(
                "UPDATE battery_turns SET mps_ipr_mean=?, mps_morphology_score=? WHERE id=?",
                (ipr_val, morph_val, row_id),
            )
        except Exception:
            pass
    conn.commit()


def run_audit_snapshot() -> str:
    ts = datetime.now(UTC).isoformat()
    if not SQLITE_PATH.exists():
        return f"### Snapshot `{ts}`: Banco `{SQLITE_PATH}` ainda não inicializado.\n"

    with sqlite3.connect(SQLITE_PATH, timeout=30.0) as conn:
        _backfill_ipr_from_npz(conn)
        total = conn.execute("SELECT count(*) FROM battery_turns").fetchone()[0]
        by_arm = conn.execute(
            """
            SELECT model_tag, phase_group, sub_arm, count(*),
                   avg(temperature), avg(scale_delta_temp),
                   avg(psi_value), avg(kuramoto_r_pair),
                   avg(mps_chi_eff_mean), avg(mps_pr_traj), avg(mps_contract_drift),
                   avg(mps_ipr_mean), avg(mps_morphology_score),
                   avg(motor_velocity_mean), avg(motor_acceleration_mean),
                   avg(motor_cosine_drift), avg(motor_action_markers),
                   avg(motor_unique_ratio), avg(motor_degenerate_flag),
                   avg(latency_s)
            FROM battery_turns
            GROUP BY model_tag, phase_group, sub_arm
            ORDER BY model_tag, phase_group, sub_arm
            """
        ).fetchall()

        by_stage = conn.execute(
            """
            SELECT model_tag, phase_group, stage_category, count(*),
                   avg(mps_chi_eff_mean), avg(mps_contract_drift),
                   avg(motor_velocity_mean), avg(motor_unique_ratio),
                   avg(motor_degenerate_flag)
            FROM battery_turns
            GROUP BY model_tag, phase_group, stage_category
            ORDER BY model_tag, phase_group, stage_category
            """
        ).fetchall()

        # Compute empirical correlations between scales and MPS/Motor metrics per model
        corr_lines = []
        for m_tag in ("gemma-4-12B-it", "gemma-4-E4B-it"):
            rows = conn.execute(
                """
                SELECT temperature, psi_value, kuramoto_r_pair,
                       mps_chi_eff_mean, mps_contract_drift,
                       motor_velocity_mean, motor_unique_ratio
                FROM battery_turns WHERE model_tag=?
                """,
                (m_tag,),
            ).fetchall()
            if len(rows) >= 4:
                arr = np.array(rows, dtype=np.float64)
                def _corr(a, b):
                    if np.std(a) < 1e-9 or np.std(b) < 1e-9:
                        return 0.0
                    return float(np.corrcoef(a, b)[0, 1])
                c_t_vel = _corr(arr[:, 0], arr[:, 5])
                c_t_drift = _corr(arr[:, 0], arr[:, 4])
                c_t_ur = _corr(arr[:, 0], arr[:, 6])
                c_chi_vel = _corr(arr[:, 3], arr[:, 5])
                corr_lines.append(
                    f"- **`{m_tag}` ($N={len(rows)}$ turnos)** `[DADO]`: "
                    f"$r(T, \\text{{motor\\_vel}}) = {c_t_vel:+.3f}$, "
                    f"$r(T, \\text{{mps\\_drift}}) = {c_t_drift:+.3f}$, "
                    f"$r(T, \\text{{unique\\_ratio}}) = {c_t_ur:+.3f}$, "
                    f"$r(\\chi_{{\\text{{eff}}}}, \\text{{motor\\_vel}}) = {c_chi_vel:+.3f}$"
                )

    lines = [
        f"\n## Snapshot de Auditoria SWE — `{ts}` (`{total}/280` turnos concluídos) `[DADO]`\n",
        "### A. Estado por Modelo, Fase (`BASAL` vs `MODULATED`) e Sub-Braço de Escala\n",
        "| Modelo | Fase | Sub-Braço | Turnos | $T$ Médio | $\\Delta T$ | $\\Psi$ | $R_{\\text{pair}}$ | MPS $\\chi_{\\text{eff}}$ | MPS $PR_{\\text{traj}}$ | MPS Drift | IPR | Morf. | Motor Vel. | Motor Acc. | Motor Drift | Action Mk | Unique Ratio | Degen (%) | Lat (s) |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in by_arm:
        lines.append(
            f"| `{r[0]}` | **{r[1]}** | `{r[2]}` | {r[3]} | {r[4]:.3f} | {r[5]:+.3f} | "
            f"{r[6]:.3f} | {r[7]:.4f} | **{r[8]:.2f}** | {r[9]:.2f} | **{r[10]:.4f}** | "
            f"{r[11]:.4f} | {r[12]:.4f} | **{r[13]:.2f}** | {r[14]:.2f} | {r[15]:.4f} | "
            f"{r[16]:.2f} | **{r[17]:.3f}** | {100.0 * r[18]:.1f}% | {r[19]:.1f} |"
        )

    lines.append("\n### B. Decomposição por Etapa/Processo da Bateria (`v10`, `cognitivo`, `v11`, `swe`)\n")
    lines.append("| Modelo | Fase | Etapa/Processo | Turnos | MPS $\\chi_{\\text{eff}}$ | MPS Drift | Motor Vel. | Unique Ratio | Degen (%) |")
    lines.append("|---|---|---|---:|---:|---:|---:|---:|---:|")
    for s in by_stage:
        lines.append(
            f"| `{s[0]}` | **{s[1]}** | `{s[2]}` | {s[3]} | {s[4]:.2f} | {s[5]:.4f} | "
            f"{s[6]:.2f} | {s[7]:.3f} | {100.0 * s[8]:.1f}% |"
        )

    if corr_lines:
        lines.append("\n### C. Acoplamento Escalas $\\leftrightarrow$ Estado MPS $\\leftrightarrow$ Camada Motor\n")
        lines.extend(corr_lines)

    snapshot_md = "\n".join(lines) + "\n"
    if not REPORT_PATH.exists():
        header = (
            "# Auditoria Contínua SWE (Intervalos 5–10 min): Bateria 280 Turnos Basal vs Modulado (12B `:8098` & 4B `:8099`)\n\n"
            "- **Banco SQLite Auditado**: `/content/omni_worker/data/basal_vs_modulated_280turns_20261105.sqlite`\n"
            "- **Modo Basal (`basal_assistant` / `basal_executor`)**: `intervention_enabled=0` (observação pura sem injeção, captando MPS + Camada Motor + Escalas Soberanas)\n"
            "- **Modo Modulado (`M1..M4`)**: `intervention_enabled=1` (pequenas variâncias $\\pm\\Delta T$, Freud10D+INRC+Kuramoto e Gate Closed-Loop MPS+Motor ancorado no envelope basal)\n"
        )
        REPORT_PATH.write_text(header + snapshot_md, encoding="utf-8")
    else:
        with open(REPORT_PATH, "a", encoding="utf-8") as fh:
            fh.write(snapshot_md)
    print(snapshot_md, flush=True)
    return snapshot_md


if __name__ == "__main__":
    run_audit_snapshot()
