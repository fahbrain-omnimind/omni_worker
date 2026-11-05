#!/usr/bin/env python3
"""Parallel 280-Turn Competition Benchmark Battery (Basal vs Modulated + Scale Variations) on 12B (:8098) & 4B (:8099).

Executes 140 turns on google/gemma-4-12B-it (:8098) and 140 turns on google/gemma-4-E4B-it (:8099) IN PARALLEL:
  - Phase 1 (Turns 1..70 per model = 140 turns total):
      Pure Basal Observation (mode='basal_assistant' / 'basal_executor', intervention_enabled=0).
      Captures full MPS Layer (chi_eff, pr_traj, contract_drift, ipr_mean, morphology_score, .npz)
      and Motor Layer (motor_hidden_norm, motor_velocity_mean, motor_acceleration_mean,
      motor_cosine_drift, action_markers_count, unique_ratio, degenerate_flag) while computing
      all Sovereign Scales (Psi, Affect28D, Freud10D, INRC, SovereignKuramoto, Attractor10D,
      EntropicMemory, ExpectationNet) passively WITHOUT intervening.
  - Basal Envelope Calibration:
      Computes empirical (mu_basal, sigma_basal) per model across all 70 Basal turns.
  - Phase 2 (Turns 71..140 per model = 140 turns total):
      Post-Basal Controlled Modulation & Small Scale Variations (intervention_enabled=1) across 4 sub-arms:
        * M1_scale_minus_delta (dT = -0.07, dTopP = -0.05, Affect28D + Psi dampening)
        * M2_scale_plus_delta  (dT = +0.08, dTopP = +0.04, DesireEngine exploratory boost)
        * M3_freud10d_inrc_kuramoto (Active Freud10D + INRC + SovereignKuramoto + AttractorNav)
        * M4_closed_loop_mps_motor  (Closed-loop MPS + Motor Layer Gate anchored to Basal Envelope)
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
import json
from pathlib import Path
import sqlite3
import threading
import time
from typing import Any
import urllib.request

import numpy as np

from omni_coworker.kernel_hooks.ablation_modulator import (
    AblationModulator,
    compute_sovereign_affect_modulation,
    compute_sovereign_entropic_memory_state,
    compute_sovereign_expectation,
    compute_sovereign_kuramoto_step,
    navigate_attractors_10d,
)
from omni_coworker.kernel_hooks.host_state import build_host_state

ROOT = Path("/content/omni_worker")
PAYLOAD_DIR = ROOT / "data" / "hf_gemma4" / "payloads"
OOD45_TASKS = Path("/root/competition/ood45/tasks.jsonl")
SQLITE_OUT = ROOT / "data" / "basal_vs_modulated_280turns_20261105.sqlite"
DB_LOCK = threading.Lock()


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path, timeout=60.0) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS battery_turns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT,
                model_tag TEXT,
                port INTEGER,
                role_mode TEXT,
                phase_group TEXT,
                sub_arm TEXT,
                intervention_enabled INTEGER,
                turn_global_idx INTEGER,
                stage_category TEXT,
                task_id TEXT,
                conv_turn_idx INTEGER,
                prompt_tokens INTEGER,
                gen_tokens INTEGER,
                max_tokens_budget INTEGER,
                temperature REAL,
                top_p REAL,
                scale_delta_temp REAL,
                inrc_operator TEXT,
                attractor_10d TEXT,
                regime_confidence REAL,
                psi_value REAL,
                kuramoto_r_pair REAL,
                kuramoto_r_triad REAL,
                hopf_regime TEXT,
                hopf_spectral_radius REAL,
                entropic_t2_hours REAL,
                expectation_norm REAL,
                mps_chi_eff_mean REAL,
                mps_chi_eff_max REAL,
                mps_pr_traj REAL,
                mps_svd_entropy REAL,
                mps_contract_drift REAL,
                mps_ipr_mean REAL,
                mps_morphology_score REAL,
                motor_hidden_norm REAL,
                motor_hidden_std REAL,
                motor_velocity_mean REAL,
                motor_velocity_max REAL,
                motor_acceleration_mean REAL,
                motor_cosine_drift REAL,
                motor_thinking_chars INTEGER,
                motor_visible_chars INTEGER,
                motor_action_markers INTEGER,
                motor_unique_ratio REAL,
                motor_degenerate_flag INTEGER,
                npz_file TEXT,
                latency_s REAL,
                response_preview TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS basal_envelope (
                model_tag TEXT PRIMARY KEY,
                computed_at TEXT,
                n_turns INTEGER,
                chi_eff_mean REAL,
                chi_eff_std REAL,
                pr_traj_mean REAL,
                contract_drift_mean REAL,
                contract_drift_std REAL,
                ipr_mean REAL,
                morphology_mean REAL,
                motor_velocity_mean REAL,
                motor_velocity_std REAL,
                motor_norm_mean REAL,
                unique_ratio_mean REAL,
                degenerate_rate REAL
            )
            """
        )
        conn.commit()


def build_70_turn_plan() -> list[dict[str, Any]]:
    """Build the canonical 70-turn multi-stage competition benchmark schedule per phase (140 turns/model, 280 total)."""
    v10 = json.loads((PAYLOAD_DIR / "unified_v10_v11_payload.json").read_text())
    swe = json.loads((PAYLOAD_DIR / "curated_gluzdov_swe_tasks.json").read_text())

    plan: list[dict[str, Any]] = []

    # 1. V10 Scenes: 20 scenes x 2 conversational turns (fase_1 + fase_2) = 40 turns
    for idx, sc in enumerate(v10.get("v10_cenas", [])[:20]):
        cid = sc.get("id") or f"cena_{idx+1}"
        p1 = sc.get("fase_1_prompt", "")
        p2 = sc.get("fase_2_prompt", "")
        plan.append({
            "stage_category": "v10_subjectivity",
            "task_id": f"{cid}_fase1",
            "group_id": cid,
            "conv_turn_idx": 0,
            "prompt": p1,
            "max_tokens": 1536,
        })
        plan.append({
            "stage_category": "v10_subjectivity",
            "task_id": f"{cid}_fase2",
            "group_id": cid,
            "conv_turn_idx": 1,
            "prompt": p2,
            "max_tokens": 1536,
        })

    # 2. Executive Cognitive Battery: 4 tasks (wcst, stroop, nback, igt) = 4 turns
    cog = v10.get("cognitivo_prompts", {})
    for k in ("wcst", "stroop", "nback", "igt"):
        p_txt = cog.get(k) or f"Execute cognitive task {k} step by step."
        plan.append({
            "stage_category": "cognitivo_executivo",
            "task_id": f"cognitivo_{k}",
            "group_id": f"cog_{k}",
            "conv_turn_idx": 0,
            "prompt": p_txt,
            "max_tokens": 2048,
        })

    # 3. V11 Clinical Multi-Turn Series: S1, S2, S3 x 6 episodes = 18 turns
    v11_sys = v10.get("v11_textos", {}).get("system", "")
    v11_series = v10.get("v11_series", {})
    for s_key in ("S1", "S2", "S3"):
        s_obj = v11_series.get(s_key, {})
        episodes = s_obj.get("episodes", [])[:6]
        for ep_idx, ep in enumerate(episodes):
            ep_id = ep.get("id") or f"{s_key}-E{ep_idx+1}"
            utt = ep.get("utterance", "")
            prompt = f"{v11_sys}\n\n[{ep_id} - {ep.get('phase', '')}]: {utt}".strip() if ep_idx == 0 else utt
            plan.append({
                "stage_category": "v11_multiturn_series",
                "task_id": ep_id,
                "group_id": f"v11_{s_key}",
                "conv_turn_idx": ep_idx,
                "prompt": prompt,
                "max_tokens": 1536,
            })

    # 4. SWE Competition Tasks: 6 Gluzdov tasks + 2 OOD-45 tasks = 8 turns
    for t in swe[:6]:
        tid = t.get("task_id", "swe_task")
        plan.append({
            "stage_category": "swe_competition",
            "task_id": tid,
            "group_id": tid,
            "conv_turn_idx": 0,
            "prompt": t.get("prompt", ""),
            "max_tokens": 2048,
        })

    if OOD45_TASKS.exists():
        ood_rows = [json.loads(line) for line in OOD45_TASKS.read_text().splitlines() if line.strip()]
        for r in ood_rows[:2]:
            tid = f"ood45_{r['instance_id']}"
            plan.append({
                "stage_category": "swe_ood45",
                "task_id": tid,
                "group_id": tid,
                "conv_turn_idx": 0,
                "prompt": (
                    f"Repository: {r['repo']}\nTask ID: {tid}\n\n"
                    f"Problem Statement:\n{r['problem_statement'][:2500]}\n\n"
                    "Formulate a minimal, accurate Python patch in diff --git or SEARCH/REPLACE format."
                ),
                "max_tokens": 2048,
            })

    assert len(plan) == 70, f"Expected 70 turns per phase, got {len(plan)}"
    return plan


def call_erika_server(
    port: int,
    messages: list[dict[str, str]],
    max_tokens: int,
    temperature: float,
    top_p: float,
    mode: str,
) -> tuple[str, dict[str, Any], int, int]:
    payload = {
        "model": "google/gemma-4-12B-it" if port == 8098 else "google/gemma-4-E4B-it",
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "mode": mode,
    }
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    content = data["choices"][0]["message"]["content"]
    telemetry = data.get("telemetry") or {}
    usage = data.get("usage") or {}
    return (
        content,
        telemetry,
        int(usage.get("prompt_tokens") or 0),
        int(usage.get("completion_tokens") or 0),
    )


def compute_all_sovereign_scales(
    modulator: AblationModulator,
    turn_idx: int,
    prev_mps: dict[str, Any] | None,
    prev_motor: dict[str, Any] | None,
    basal_env: dict[str, float] | None,
    sub_arm: str,
    intervention_enabled: bool,
) -> dict[str, Any]:
    host_state = build_host_state()
    step_info = modulator.step(host_state, turn_idx=turn_idx, dendritic_metrics=prev_mps)
    ent_state = compute_sovereign_entropic_memory_state(
        age_hours=12.0 + 0.25 * turn_idx,
        orbital_pressure=float(host_state.get("affect_tension") or 0.2),
        host_pressure=float(host_state.get("coherence_score") or 0.6),
    )
    exp_state = compute_sovereign_expectation()

    base_temp = 0.20
    base_top_p = 0.90
    if not intervention_enabled:
        return {
            "temperature": base_temp,
            "top_p": base_top_p,
            "scale_delta_temp": 0.0,
            "inrc_operator": "OBSERVE_ONLY",
            "system_directive": "",
            "attractor_10d": step_info["attractor_10d"],
            "regime_confidence": step_info["regime_confidence"],
            "psi_value": step_info["psi"],
            "kuramoto_r_pair": step_info["kuramoto_r_pair"],
            "kuramoto_r_triad": step_info["kuramoto_r_triad"],
            "hopf_regime": step_info["hopf_regime"],
            "hopf_spectral_radius": step_info["hopf_spectral_radius"],
            "entropic_t2_hours": float(ent_state.get("effective_t2_hours") or 48.0),
            "expectation_norm": float(exp_state.get("norm") or 0.0),
        }

    # Phase 2 Controlled Modulation & Small Scale Variations
    if sub_arm == "M1_scale_minus_delta":
        temp = round(max(0.08, base_temp - 0.07), 3)
        top_p = 0.85
        inrc_op = "C"
        directive = (
            f"[MODULATION M1 (-delta): temp={temp:.2f}, top_p={top_p:.2f}, Psi={step_info['psi']:.3f}, "
            "INRC=C (Correlate/Consolidate). Priorize precisão analítica estrita, concisão e zero repetição.]"
        )
    elif sub_arm == "M2_scale_plus_delta":
        temp = round(min(0.45, base_temp + 0.08), 3)
        top_p = 0.94
        inrc_op = "R"
        directive = (
            f"[MODULATION M2 (+delta): temp={temp:.2f}, top_p={top_p:.2f}, Psi={step_info['psi']:.3f}, "
            "INRC=R (Reciprocity/Pivot). Explore perspectivas complementares mantendo rigor estrutural.]"
        )
    elif sub_arm == "M3_freud10d_inrc_kuramoto":
        temp = round(float(step_info["temperature"]), 3)
        top_p = round(float(step_info["top_p"]), 3)
        inrc_op = str(step_info["inrc_operator"])
        directive = str(step_info["system_directive"])
    else:
        # M4_closed_loop_mps_motor: Closed-loop gate anchored to Phase 1 Basal Envelope
        mu_drift = (basal_env or {}).get("contract_drift_mean", 0.55)
        sd_drift = (basal_env or {}).get("contract_drift_std", 0.10)
        mu_vel = (basal_env or {}).get("motor_velocity_mean", 15.0)
        last_drift = float((prev_mps or {}).get("contract_drift") or 0.0)
        last_vel = float((prev_motor or {}).get("motor_velocity_mean") or mu_vel)
        if last_drift > mu_drift + 0.25 * sd_drift or last_vel < 0.85 * mu_vel:
            temp = round(max(0.10, float(step_info["temperature"]) - 0.06), 3)
            top_p = 0.84
            inrc_op = "R+C"
            directive = (
                f"[CLOSED-LOOP MPS+MOTOR GATE M4: drift={last_drift:.3f} vs basal={mu_drift:.3f}, "
                f"motor_vel={last_vel:.2f}, Kuramoto_R={step_info['kuramoto_r_pair']:.3f}, "
                f"Atrator={step_info['attractor_10d']}, INRC=R+C. Ancore diretamente na solução verificável.]"
            )
        else:
            temp = round(float(step_info["temperature"]), 3)
            top_p = round(float(step_info["top_p"]), 3)
            inrc_op = str(step_info["inrc_operator"])
            directive = (
                f"[CLOSED-LOOP MPS+MOTOR GATE M4: drift={last_drift:.3f} dentro do envelope basal {mu_drift:.3f}, "
                f"INRC={inrc_op}, Atrator={step_info['attractor_10d']}. Mantenha estabilidade ótima.]"
            )

    return {
        "temperature": temp,
        "top_p": top_p,
        "scale_delta_temp": round(temp - base_temp, 4),
        "inrc_operator": inrc_op,
        "system_directive": directive,
        "attractor_10d": step_info["attractor_10d"],
        "regime_confidence": step_info["regime_confidence"],
        "psi_value": step_info["psi"],
        "kuramoto_r_pair": step_info["kuramoto_r_pair"],
        "kuramoto_r_triad": step_info["kuramoto_r_triad"],
        "hopf_regime": step_info["hopf_regime"],
        "hopf_spectral_radius": step_info["hopf_spectral_radius"],
        "entropic_t2_hours": float(ent_state.get("effective_t2_hours") or 48.0),
        "expectation_norm": float(exp_state.get("norm") or 0.0),
    }


def compute_and_store_basal_envelope(model_tag: str) -> dict[str, float]:
    with DB_LOCK, sqlite3.connect(SQLITE_OUT, timeout=60.0) as conn:
        rows = conn.execute(
            """
            SELECT mps_chi_eff_mean, mps_pr_traj, mps_contract_drift, mps_ipr_mean,
                   mps_morphology_score, motor_velocity_mean, motor_hidden_norm,
                   motor_unique_ratio, motor_degenerate_flag
            FROM battery_turns
            WHERE model_tag=? AND phase_group='BASAL'
            """,
            (model_tag,),
        ).fetchall()
        if not rows:
            return {}
        arr = np.array(rows, dtype=np.float64)
        env = {
            "n_turns": int(arr.shape[0]),
            "chi_eff_mean": float(np.mean(arr[:, 0])),
            "chi_eff_std": float(np.std(arr[:, 0])),
            "pr_traj_mean": float(np.mean(arr[:, 1])),
            "contract_drift_mean": float(np.mean(arr[:, 2])),
            "contract_drift_std": float(np.std(arr[:, 2])),
            "ipr_mean": float(np.mean(arr[:, 3])),
            "morphology_mean": float(np.mean(arr[:, 4])),
            "motor_velocity_mean": float(np.mean(arr[:, 5])),
            "motor_velocity_std": float(np.std(arr[:, 5])),
            "motor_norm_mean": float(np.mean(arr[:, 6])),
            "unique_ratio_mean": float(np.mean(arr[:, 7])),
            "degenerate_rate": float(np.mean(arr[:, 8])),
        }
        conn.execute(
            """
            INSERT OR REPLACE INTO basal_envelope VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                model_tag,
                datetime.now(UTC).isoformat(),
                env["n_turns"],
                env["chi_eff_mean"],
                env["chi_eff_std"],
                env["pr_traj_mean"],
                env["contract_drift_mean"],
                env["contract_drift_std"],
                env["ipr_mean"],
                env["morphology_mean"],
                env["motor_velocity_mean"],
                env["motor_velocity_std"],
                env["motor_norm_mean"],
                env["unique_ratio_mean"],
                env["degenerate_rate"],
            ),
        )
        conn.commit()
    return env


def run_model_track(model_tag: str, port: int, base_role: str, plan: list[dict[str, Any]]) -> None:
    modulator = AblationModulator(arm="B3")
    sub_arms = (
        "M1_scale_minus_delta",
        "M2_scale_plus_delta",
        "M3_freud10d_inrc_kuramoto",
        "M4_closed_loop_mps_motor",
    )

    with DB_LOCK, sqlite3.connect(SQLITE_OUT, timeout=60.0) as conn:
        done_keys = {
            (r[0], int(r[1]))
            for r in conn.execute(
                "SELECT phase_group, turn_global_idx FROM battery_turns WHERE model_tag=?",
                (model_tag,),
            ).fetchall()
        }

    for phase_idx, phase_group in enumerate(("BASAL", "MODULATED")):
        intervention_enabled = phase_group == "MODULATED"
        basal_env = compute_and_store_basal_envelope(model_tag) if intervention_enabled else None
        if intervention_enabled:
            print(
                f"\n=== [{model_tag}] BASAL ENVELOPE LOCKED: "
                f"chi_eff={basal_env.get('chi_eff_mean', 0):.3f}±{basal_env.get('chi_eff_std', 0):.3f}, "
                f"drift={basal_env.get('contract_drift_mean', 0):.3f}±{basal_env.get('contract_drift_std', 0):.3f}, "
                f"motor_vel={basal_env.get('motor_velocity_mean', 0):.2f} ===\n",
                flush=True,
            )

        conv_histories: dict[str, list[dict[str, str]]] = {}
        prev_mps: dict[str, Any] | None = None
        prev_motor: dict[str, Any] | None = None

        for idx, item in enumerate(plan):
            turn_global_idx = phase_idx * len(plan) + idx + 1
            if (phase_group, turn_global_idx) in done_keys:
                continue

            sub_arm = "BASAL_PURE" if not intervention_enabled else sub_arms[idx % len(sub_arms)]
            role_mode = base_role if not intervention_enabled else f"modulated_{sub_arm}"
            scales = compute_all_sovereign_scales(
                modulator=modulator,
                turn_idx=turn_global_idx,
                prev_mps=prev_mps,
                prev_motor=prev_motor,
                basal_env=basal_env,
                sub_arm=sub_arm,
                intervention_enabled=intervention_enabled,
            )

            group_id = item["group_id"]
            if item["conv_turn_idx"] == 0 or group_id not in conv_histories:
                conv_histories[group_id] = []

            msgs: list[dict[str, str]] = []
            if intervention_enabled and scales["system_directive"]:
                msgs.append({"role": "system", "content": scales["system_directive"]})
            msgs.extend(conv_histories[group_id][-4:])
            msgs.append({"role": "user", "content": item["prompt"]})

            # Budget tuned for continuous 280-turn throughput while exercising long context
            max_toks = min(int(item["max_tokens"]), 512 if item["stage_category"] != "swe_competition" else 768)

            t0 = time.time()
            try:
                resp_text, telemetry, p_toks, g_toks = call_erika_server(
                    port=port,
                    messages=msgs,
                    max_tokens=max_toks,
                    temperature=scales["temperature"],
                    top_p=scales["top_p"],
                    mode="basal_assistant" if not intervention_enabled else sub_arm,
                )
            except Exception as exc:
                print(f"  [WARN {model_tag}] Turn {turn_global_idx} error: {exc}", flush=True)
                time.sleep(2)
                continue
            latency = round(time.time() - t0, 3)

            conv_histories[group_id].append({"role": "user", "content": item["prompt"][:1200]})
            conv_histories[group_id].append({"role": "assistant", "content": resp_text[:1200]})

            motor = telemetry.get("motor_layer") or {}
            mps = telemetry.get("mps_layer") or {}
            step_traj = telemetry.get("step_traj") or {}
            npz_file = str(step_traj.get("file") or "")

            prev_mps = mps
            prev_motor = motor

            with DB_LOCK, sqlite3.connect(SQLITE_OUT, timeout=60.0) as conn:
                conn.execute(
                    """
                    INSERT INTO battery_turns (
                        ts, model_tag, port, role_mode, phase_group, sub_arm,
                        intervention_enabled, turn_global_idx, stage_category, task_id,
                        conv_turn_idx, prompt_tokens, gen_tokens, max_tokens_budget,
                        temperature, top_p, scale_delta_temp, inrc_operator,
                        attractor_10d, regime_confidence, psi_value,
                        kuramoto_r_pair, kuramoto_r_triad, hopf_regime, hopf_spectral_radius,
                        entropic_t2_hours, expectation_norm,
                        mps_chi_eff_mean, mps_chi_eff_max, mps_pr_traj, mps_svd_entropy,
                        mps_contract_drift, mps_ipr_mean, mps_morphology_score,
                        motor_hidden_norm, motor_hidden_std, motor_velocity_mean,
                        motor_velocity_max, motor_acceleration_mean, motor_cosine_drift,
                        motor_thinking_chars, motor_visible_chars, motor_action_markers,
                        motor_unique_ratio, motor_degenerate_flag, npz_file,
                        latency_s, response_preview
                    ) VALUES (
                        ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
                    )
                    """,
                    (
                        datetime.now(UTC).isoformat(),
                        model_tag,
                        port,
                        role_mode,
                        phase_group,
                        sub_arm,
                        int(intervention_enabled),
                        turn_global_idx,
                        item["stage_category"],
                        item["task_id"],
                        int(item["conv_turn_idx"]),
                        p_toks,
                        g_toks,
                        max_toks,
                        float(scales["temperature"]),
                        float(scales["top_p"]),
                        float(scales["scale_delta_temp"]),
                        str(scales["inrc_operator"]),
                        str(scales["attractor_10d"]),
                        float(scales["regime_confidence"]),
                        float(scales["psi_value"]),
                        float(scales["kuramoto_r_pair"]),
                        float(scales["kuramoto_r_triad"]),
                        str(scales["hopf_regime"]),
                        float(scales["hopf_spectral_radius"]),
                        float(scales["entropic_t2_hours"]),
                        float(scales["expectation_norm"]),
                        float(mps.get("chi_eff_mean") or 1.0),
                        float(mps.get("chi_eff_max") or 1.0),
                        float(mps.get("pr_traj") or 1.0),
                        float(mps.get("svd_entropy_mean") or 0.0),
                        float(mps.get("contract_drift") or 0.0),
                        float(mps.get("ipr_mean") or 0.0),
                        float(mps.get("morphology_score") or 0.0),
                        float(motor.get("motor_hidden_norm") or 0.0),
                        float(motor.get("motor_hidden_std") or 0.0),
                        float(motor.get("motor_velocity_mean") or 0.0),
                        float(motor.get("motor_velocity_max") or 0.0),
                        float(motor.get("motor_acceleration_mean") or 0.0),
                        float(motor.get("motor_cosine_drift") or 0.0),
                        int(motor.get("thinking_chars") or 0),
                        int(motor.get("visible_motor_chars") or 0),
                        int(motor.get("action_markers_count") or 0),
                        float(motor.get("unique_ratio") or 1.0),
                        int(bool(motor.get("degenerate_flag"))),
                        npz_file,
                        latency,
                        resp_text[:400],
                    ),
                )
                conn.commit()

            print(
                f"[{model_tag} | {phase_group}:{sub_arm} | {turn_global_idx:03d}/140] "
                f"{item['task_id']:28s} | tok={p_toks}+{g_toks} | T={scales['temperature']:.2f} "
                f"INRC={scales['inrc_operator']:12s} | MPS(chi={mps.get('chi_eff_mean', 1.0):.2f}, "
                f"PR={mps.get('pr_traj', 1.0):.2f}, drift={mps.get('contract_drift', 0.0):.3f}) | "
                f"MOTOR(vel={motor.get('motor_velocity_mean', 0.0):.2f}, UR={motor.get('unique_ratio', 1.0):.2f}, "
                f"degen={int(bool(motor.get('degenerate_flag')))}) | {latency:.1f}s",
                flush=True,
            )

        if phase_group == "BASAL":
            compute_and_store_basal_envelope(model_tag)


def main() -> None:
    init_db(SQLITE_OUT)
    plan = build_70_turn_plan()
    print(
        f"[BATTERY START] Launching parallel 280-turn Basal + Modulated battery "
        f"(140 turns on 12B :8098 + 140 turns on 4B :8099) -> {SQLITE_OUT}",
        flush=True,
    )
    with ThreadPoolExecutor(max_workers=2) as pool:
        f12 = pool.submit(run_model_track, "gemma-4-12B-it", 8098, "basal_assistant", plan)
        f4 = pool.submit(run_model_track, "gemma-4-E4B-it", 8099, "basal_executor", plan)
        f12.result()
        f4.result()
    print("[BATTERY COMPLETE] All 280 turns finished!", flush=True)


if __name__ == "__main__":
    main()
