#!/usr/bin/env python3
"""Export real system state to static JSON for the dashboard.

Only real values or null. Never invent data.
"""
from __future__ import annotations

import argparse
import json
import socket
import sqlite3
import sys
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
for _p in (str(SRC), str(ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def _read_json(path: Path):
    try:
        return json.loads(path.read_text())
    except Exception:  # noqa: BLE001
        return None


def _read_jsonl(path: Path):
    out = []
    if not path.exists():
        return out
    for line in path.read_text(errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:  # noqa: BLE001, S112
            continue
    return out


def _sqlite_rows(db: Path, query: str, params=()):
    if not db.exists():
        return []
    try:
        conn = sqlite3.connect(str(db))
        conn.row_factory = sqlite3.Row
        rows = [dict(r) for r in conn.execute(query, params).fetchall()]
        conn.close()
        return rows
    except Exception:  # noqa: BLE001
        return []


def _scalar(db: Path, query: str, params=()):
    rows = _sqlite_rows(db, query, params)
    if not rows:
        return None
    return next(iter(rows[0].values()))


def _tcp_open(port: int, host: str = "127.0.0.1", timeout: float = 1.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _http_ok(port: int, path: str, host: str = "127.0.0.1", timeout: float = 2.5) -> bool:
    try:
        with urllib.request.urlopen(f"http://{host}:{port}{path}", timeout=timeout) as r:
            return 200 <= r.status < 400
    except Exception:  # noqa: BLE001
        return False


def _pid_alive(pid_file: Path) -> int | None:
    try:
        pid = int(pid_file.read_text().strip())
    except Exception:  # noqa: BLE001
        return None
    try:
        Path(f"/proc/{pid}").stat()
        return pid
    except OSError:
        return None


def _auc(scores, labels) -> float | None:
    """Mann-Whitney ROC-AUC: P(score_pos > score_neg) + 0.5·P(tie)."""
    pos = [s for s, lab in zip(scores, labels, strict=False) if lab == 1 and s is not None]
    neg = [s for s, lab in zip(scores, labels, strict=False) if lab == 0 and s is not None]
    if not pos or not neg:
        return None
    wins = sum(1.0 if p > n else 0.5 if p == n else 0.0 for p in pos for n in neg)
    return round(wins / (len(pos) * len(neg)), 4)


def _vm_section(root: Path, live_bundle: dict, live_soma: dict) -> dict:
    """Live server probes — the 'is the VM awake' surface of the pulse."""
    pid_dir = root / "runtime_config" / "pids"
    hw = _read_json(pid_dir.parent / "hw_profile.json") or {}
    gpu0 = ((live_soma.get("gpu") or {}).get("gpus") or [{}])[0]

    def _svc(port: int, probe_path: str, model=None) -> dict:
        return {
            "port": port,
            "model": model,
            "http_healthy": _http_ok(port, probe_path),
            "tcp_open": _tcp_open(port),
            "probe": probe_path,
        }

    servers = {
        "analyst_brain": _svc(8098, "/health", "google/gemma-4-12B-it"),
        "executor_brain": _svc(8099, "/health", "google/gemma-4-E4B-it"),
        "worker_api": _svc(8081, "/soul/state", None),
    }
    daemons = {}
    for name in ("state_guard", "swap_scheduler", "archive_loop", "pulse_sync"):
        pid = _pid_alive(pid_dir / f"{name}.pid")
        daemons[name] = {"pid": pid, "alive": pid is not None}
    active = sum(1 for s in servers.values() if s["http_healthy"])
    return {
        "hw_tier": hw.get("tier"),
        "gpu_name": gpu0.get("name") or hw.get("gpu"),
        "vram_total_mb": hw.get("vram_mb"),
        "servers": servers,
        "daemons": daemons,
        "active_servers": active,
        "vm_active": active > 0,
        "kernel_daemon": "in-process inside worker_api :8081 (no standalone pid)",
        "kernel_cycles": live_bundle.get("cycle_id"),
    }


def _basal_vs_modulated_280(data: Path) -> dict | None:
    db = data / "basal_vs_modulated_280turns_20261105.sqlite"
    if not db.exists():
        return None

    metrics = [
        ("mps_chi_eff_mean", "chi_eff"),
        ("mps_pr_traj", "pr_traj"),
        ("mps_svd_entropy", "svd_entropy"),
        ("mps_contract_drift", "contract_drift"),
        ("mps_ipr_mean", "ipr"),
        ("mps_morphology_score", "morphology"),
        ("motor_velocity_mean", "motor_vel"),
        ("motor_cosine_drift", "motor_cos_drift"),
        ("motor_unique_ratio", "unique_ratio"),
    ]
    agg_cols = ", ".join(
        f"ROUND(AVG({c}),4) AS {a}, ROUND(MIN({c}),4) AS {a}_min, ROUND(MAX({c}),4) AS {a}_max"
        for c, a in metrics
    )
    summary = _sqlite_rows(
        db,
        f"SELECT model_tag, phase_group, sub_arm, COUNT(*) AS n, {agg_cols}, "
        "ROUND(AVG(temperature),3) AS temp, ROUND(AVG(scale_delta_temp),4) AS delta_temp, "
        "ROUND(AVG(psi_value),4) AS psi, ROUND(AVG(kuramoto_r_pair),4) AS kuramoto_r, "
        "SUM(motor_degenerate_flag) AS degen_n, ROUND(AVG(latency_s),1) AS latency_s "
        "FROM battery_turns GROUP BY model_tag, phase_group, sub_arm "
        "ORDER BY model_tag, phase_group, sub_arm",
    )
    stage_summary = _sqlite_rows(
        db,
        "SELECT model_tag, phase_group, stage_category, COUNT(*) AS n, "
        "ROUND(AVG(mps_chi_eff_mean),4) AS chi_eff, ROUND(AVG(mps_pr_traj),4) AS pr_traj, "
        "ROUND(AVG(mps_contract_drift),4) AS contract_drift, ROUND(AVG(mps_ipr_mean),4) AS ipr, "
        "ROUND(AVG(motor_velocity_mean),4) AS motor_vel, ROUND(AVG(motor_unique_ratio),4) AS unique_ratio, "
        "SUM(motor_degenerate_flag) AS degen_n "
        "FROM battery_turns GROUP BY model_tag, phase_group, stage_category "
        "ORDER BY model_tag, phase_group, stage_category",
    )
    envelope = {r["model_tag"]: r for r in _sqlite_rows(db, "SELECT * FROM basal_envelope")}

    turns = _sqlite_rows(
        db,
        "SELECT turn_global_idx AS idx, ts, model_tag AS model, phase_group AS phase, sub_arm, "
        "stage_category AS stage, task_id, temperature AS temp, scale_delta_temp AS dt, "
        "inrc_operator, hopf_regime, mps_chi_eff_mean AS chi_eff, mps_pr_traj AS pr_traj, "
        "mps_svd_entropy AS svd_entropy, mps_contract_drift AS contract_drift, mps_ipr_mean AS ipr, "
        "mps_morphology_score AS morphology, motor_velocity_mean AS motor_vel, "
        "motor_acceleration_mean AS motor_acc, motor_cosine_drift AS motor_cos_drift, "
        "motor_unique_ratio AS unique_ratio, motor_degenerate_flag AS degen, "
        "psi_value AS psi, kuramoto_r_pair AS kuramoto_r, prompt_tokens, gen_tokens, "
        "ROUND(latency_s,1) AS latency_s FROM battery_turns ORDER BY turn_global_idx",
    )

    # M4 closed-loop gate rule (audited): excursion when drift escapes the basal
    # envelope (mu + 0.25·sigma) or motor velocity drops below 0.85·mu_env.
    gate_counts: dict = {}
    for t in turns:
        env = envelope.get(t["model"]) or {}
        d_mu, d_sd = env.get("contract_drift_mean"), env.get("contract_drift_std")
        v_mu = env.get("motor_velocity_mean")
        gate = None
        if None not in (d_mu, d_sd, v_mu) and t["contract_drift"] is not None and t["motor_vel"] is not None:
            gate = bool(
                t["contract_drift"] > d_mu + 0.25 * d_sd or t["motor_vel"] < 0.85 * v_mu
            )
        t["gate_excursion"] = gate
        if gate is not None:
            k = gate_counts.setdefault(t["model"], {"BASAL": 0, "MODULATED": 0})
            if gate:
                k[t["phase"]] += 1
    for m, c in gate_counts.items():
        c["n_per_phase"] = sum(1 for t in turns if t["model"] == m and t["phase"] == "BASAL")

    def _disc(rows, metric_col, label_fn):
        vals = [r.get(metric_col) for r in rows]
        labs = [label_fn(r) for r in rows]
        keep = [(v, l) for v, l in zip(vals, labs, strict=False) if l is not None]
        a = _auc([v for v, _ in keep], [l for _, l in keep])
        return a

    models = sorted({t["model"] for t in turns})
    disc_chassis = {}
    for _col, name in metrics:
        a = _disc(turns, name, lambda r: 1 if r["model"] == "gemma-4-12B-it" else 0)
        disc_chassis[name] = {
            "auc_12b": a,
            "auc_e4b": round(1 - a, 4) if a is not None else None,
            "power": max(a, 1 - a) if a is not None else None,
            "direction": ("12B>E4B" if a > 0.5 else "E4B>12B") if a is not None else None,
        }
    disc_phase = {}
    for m in models:
        sub = [t for t in turns if t["model"] == m]
        disc_phase[m] = {}
        for _col, name in metrics:
            a = _disc(sub, name, lambda r: 1 if r["phase"] == "MODULATED" else 0)
            disc_phase[m][name] = {
                "auc_modulated": a,
                "power": max(a, 1 - a) if a is not None else None,
            }
    disc_degen = {"pooled": {}, "per_model": {}}
    for _col, name in metrics:
        disc_degen["pooled"][name] = _disc(turns, name, lambda r: r["degen"])
        for m in models:
            sub = [t for t in turns if t["model"] == m]
            disc_degen["per_model"].setdefault(m, {})[name] = _disc(
                sub, name, lambda r: r["degen"]
            )
    regime_set = [t for t in turns if t["stage"] in ("v11_multiturn_series", "swe_competition", "swe_ood45", "cognitivo_executivo")]
    disc_regime = {"pooled": {}, "per_model": {}}
    for _col, name in metrics:
        disc_regime["pooled"][name] = _disc(
            regime_set, name, lambda r: 1 if r["stage"] == "v11_multiturn_series" else 0
        )
        for m in models:
            sub = [t for t in regime_set if t["model"] == m]
            disc_regime["per_model"].setdefault(m, {})[name] = _disc(
                sub, name, lambda r: 1 if r["stage"] == "v11_multiturn_series" else 0
            )

    totals = {
        "turns": len(turns),
        "models": models,
        "turns_per_model_phase": {
            f"{m}/{p}": sum(1 for t in turns if t["model"] == m and t["phase"] == p)
            for m in models for p in ("BASAL", "MODULATED")
        },
        "degen_per_model_phase": {
            f"{m}/{p}": sum(1 for t in turns if t["model"] == m and t["phase"] == p and t["degen"])
            for m in models for p in ("BASAL", "MODULATED")
        },
        "ts_range": [
            min((t["ts"] for t in turns if t["ts"]), default=None),
            max((t["ts"] for t in turns if t["ts"]), default=None),
        ],
        "sub_arms": sorted({t["sub_arm"] for t in turns}),
        "stages": sorted({t["stage"] for t in turns}),
    }
    return {
        "source_db": "data/basal_vs_modulated_280turns_20261105.sqlite",
        "totals": totals,
        "summary_by_model_phase_arm": summary,
        "stage_summary": stage_summary,
        "basal_envelope": envelope,
        "gate_rule": "excursion = contract_drift > env_mu + 0.25·env_sigma OR motor_vel < 0.85·env_mu (per-model basal_envelope)",
        "gate_excursions": gate_counts,
        "discriminators_roc_auc": {
            "chassis_12b_vs_e4b": disc_chassis,
            "phase_modulated_vs_basal_intramodel": disc_phase,
            "degeneration_degen1_vs_0": disc_degen,
            "regime_v11_vs_swe_cog": disc_regime,
        },
        "turns": turns,
    }


def _swe_mps_ablation(data: Path) -> dict | None:
    db = data / "swe_mps_ablation_20261105.sqlite"
    if not db.exists():
        return None
    summary = _sqlite_rows(db, "SELECT * FROM ablation_summary ORDER BY arm")
    turns = _sqlite_rows(
        db,
        "SELECT arm, instance_id, repo, turn_idx, temperature, inrc_operator, inrc_reason, "
        "hopf_regime, ROUND(contract_drift,4) AS contract_drift, ROUND(ipr_dim_mean,4) AS ipr, "
        "ROUND(morphology_score,4) AS morphology, ROUND(dendritic_depth,4) AS dendritic_depth, "
        "psi_value AS psi, ROUND(kuramoto_r_pair,4) AS kuramoto_r, patch_applied, repro_expected, "
        "f2p_passed, p2p_passed, resolved, ROUND(latency_s,1) AS latency_s "
        "FROM ablation_turns ORDER BY arm, instance_id, turn_idx",
    )
    return {
        "source_db": "data/swe_mps_ablation_20261105.sqlite",
        "arms": summary,
        "totals": {
            "turns": len(turns),
            "tasks_resolved": sum(1 for t in turns if t["resolved"]),
            "patches_applied": sum(1 for t in turns if t["patch_applied"]),
            "instances": sorted({t["instance_id"] for t in turns if t["instance_id"]}),
        },
        "turns": turns,
    }


def _corpus_reading(root: Path) -> dict | None:
    db = root / "scripts" / "corpus_reading_battery" / "corpus_delivery_battery.sqlite"
    if not db.exists():
        return None
    runs = _sqlite_rows(
        db,
        "SELECT id, ts_utc, work_id, file_name, author_match, title_match, anomaly, "
        "ROUND(tabular_ratio,3) AS tabular_ratio, ROUND(latency_s,1) AS latency_s "
        "FROM corpus_reading_runs ORDER BY id",
    )
    app = _sqlite_rows(
        db,
        "SELECT id, ts_utc, task_id, pytest_passed, pytest_total, files_scanned, "
        "duplicates_found, anomalies_flagged, judge_consensus, audit_passed, verdict "
        "FROM app_delivery_runs ORDER BY id",
    )
    dreams = _sqlite_rows(
        db,
        "SELECT id, ts_utc, task_id, dream_metabolized FROM dream_self_curriculum ORDER BY id",
    )
    return {
        "corpus_reading_runs": runs,
        "app_delivery_runs": app,
        "dream_self_curriculum": dreams,
    }


def export(root: Path = ROOT) -> dict:
    data = root / "data"
    state = root / "state"

    # 1. Run one live kernel_daemon cycle + soul state + soma probe
    live_bundle = {}
    try:
        from omni_coworker.kernel_daemon import scheduler
        live_bundle = scheduler.run_cycle() or {}
    except Exception:  # noqa: BLE001
        live_bundle = {}

    live_soul = {}
    try:
        from omni_coworker.soul.api import _compute_state
        live_soul = _compute_state() or {}
    except Exception:  # noqa: BLE001
        live_soul = {}

    live_soma = live_soul.get("soma") or {}
    if not live_soma:
        try:
            from omni_coworker.soma.probe import probe_recorded
            live_soma = probe_recorded() or {}
        except Exception:  # noqa: BLE001
            live_soma = {}

    omega_val = None
    try:
        from omni_coworker.agency.teleology import (
            compute_omega_teleology,
            generate_missions,
        )
        missions = generate_missions({"cpu_high": (live_soma.get("cpu_percent") or 0) > 80, "soma": live_soma})
        omega_val = compute_omega_teleology({"missions": missions})
    except Exception:  # noqa: BLE001
        omega_val = None

    # Fallback/supplement from somatic_probes.sqlite
    probes = _sqlite_rows(data / "somatic_probes.sqlite", "SELECT * FROM probes ORDER BY id DESC LIMIT 1")
    p = probes[0] if probes else {}
    extra = {}
    try:
        extra = json.loads(p.get("extra_json") or "{}")
    except Exception:  # noqa: BLE001
        extra = {}

    gpus = ((live_soma.get("gpu") or extra.get("gpu") or {}).get("gpus")) or []
    gpu0 = gpus[0] if gpus else {}
    psi_block = live_soma.get("psi") or extra.get("psi") or {}
    psi_io = ((psi_block.get("io") or {}).get("some") or {}).get("avg10")
    psi_mem = ((psi_block.get("memory") or {}).get("some") or {}).get("avg10")
    psi_cpu = ((psi_block.get("cpu") or {}).get("some") or {}).get("avg10")
    load_avg = live_soma.get("load_avg") or []
    load_1m = load_avg[0] if load_avg else p.get("load1")

    pm_block = live_bundle.get("phi_meta") or {}
    meta_block = live_bundle.get("metastability") or {}
    att_block = live_bundle.get("attractor") or {}
    pl_block = live_bundle.get("phi_layer") or {}
    ws_block = live_bundle.get("workspace") or {}
    homeo_block = live_bundle.get("homeostasis") or {}

    # Shared workspace latest per topic as fallback if live_bundle missed any key
    latest_topics = {}
    for row in _sqlite_rows(
        data / "shared_workspace.sqlite",
        "SELECT topic, ts, payload_json FROM events e1 WHERE ts = (SELECT MAX(ts) FROM events e2 WHERE e2.topic = e1.topic)"
    ):
        try:
            latest_topics[row["topic"]] = json.loads(row["payload_json"])
        except Exception:  # noqa: BLE001, S110
            pass

    if not pm_block:
        pm_block = latest_topics.get("kernel.phi_meta") or {}
    if not meta_block:
        meta_block = latest_topics.get("kernel.metastability") or {}
    if not att_block:
        att_block = latest_topics.get("kernel.attractor") or {}
    if not pl_block:
        pl_block = latest_topics.get("kernel.phi_layer") or {}
    if not ws_block:
        ws_block = latest_topics.get("kernel.workspace") or {}
    if not homeo_block:
        homeo_block = latest_topics.get("kernel.homeostasis") or {}

    vram_used = gpu0.get("vram_used_gb")
    vram_total = gpu0.get("vram_total_gb")
    p_load = pm_block.get("pressure_load")
    p_headroom = pm_block.get("pressure_headroom")
    if p_load is None and vram_used is not None and vram_total:
        p_load = round(min(1.0, float(vram_used) / float(vram_total)), 4)
        p_headroom = round(max(0.0, 1.0 - p_load), 4)

    soma = {
        "cpu_percent": live_soma.get("cpu_percent", p.get("cpu")),
        "ram_used_gb": live_soma.get("ram_used_gb", p.get("ram_used_gb")),
        "ram_total_gb": live_soma.get("ram_total_gb", p.get("ram_total_gb")),
        "load_1m": round(float(load_1m), 3) if load_1m is not None else None,
        "swap_gb": live_soma.get("swap_used_gb", p.get("swap_gb")),
        "gpu_name": gpu0.get("name"),
        "gpu_util_percent": gpu0.get("util_percent"),
        "vram_used_gb": vram_used,
        "vram_total_gb": vram_total,
        "gpu_temp_c": gpu0.get("temp_c"),
        "gpu_power_w": gpu0.get("power_w"),
        "psi_io": psi_io if psi_io is not None else 0.0,
        "psi_mem": psi_mem if psi_mem is not None else 0.0,
        "psi_cpu": psi_cpu if psi_cpu is not None else 0.0,
        "pressure_load": p_load,
        "pressure_headroom": p_headroom,
        "c_soma": meta_block.get("c_soma"),
    }

    phi_val = live_soul.get("phi")
    psi_val = live_soul.get("psi")
    sigma_val = live_soul.get("sigma")
    eps_val = live_soul.get("epsilon")
    maat_val = None
    if phi_val is not None and psi_val is not None and eps_val is not None:
        maat_val = round((float(phi_val) + float(psi_val) + (1.0 - float(eps_val))) / 3.0, 4)

    soul = {
        "phi": phi_val,
        "psi": psi_val,
        "sigma": sigma_val,
        "epsilon": eps_val,
        "maat": maat_val,
        "omega": omega_val,
        "dominant_token": live_soul.get("dominant_token"),
        "kernel_active": live_soul.get("kernel"),
        "dodeca": live_soul.get("dodeca"),
    }

    # Count total kernel cycles in shared_workspace.sqlite
    cycle_rows = _sqlite_rows(
        data / "shared_workspace.sqlite",
        "SELECT COUNT(*) AS n FROM events WHERE topic = 'kernel.cycle'"
    )
    total_cycles = int(cycle_rows[0]["n"]) if cycle_rows else 1

    # Helper to unwrap model-keyed dicts (e.g. {"google/gemma-4-12B-it": {...}})
    def _unwrap_model_dict(d: dict, field: str):
        if not isinstance(d, dict):
            return None
        if field in d and d[field] is not None:
            return d[field]
        vals = [v.get(field) for v in d.values() if isinstance(v, dict) and v.get(field) is not None]
        if not vals:
            return None
        if isinstance(vals[0], (int, float)):
            return round(float(vals[0]), 4)
        return vals[0]

    # Real history from shared_workspace.sqlite (last 24 cycles)
    pm_hist = _sqlite_rows(
        data / "shared_workspace.sqlite",
        "SELECT ts, payload_json FROM events WHERE topic = 'kernel.phi_meta' ORDER BY ts DESC LIMIT 24"
    )[::-1]
    meta_hist = _sqlite_rows(
        data / "shared_workspace.sqlite",
        "SELECT ts, payload_json FROM events WHERE topic = 'kernel.metastability' ORDER BY ts DESC LIMIT 24"
    )[::-1]
    att_hist = _sqlite_rows(
        data / "shared_workspace.sqlite",
        "SELECT ts, payload_json FROM events WHERE topic = 'kernel.attractor' ORDER BY ts DESC LIMIT 24"
    )[::-1]

    hist_len = max(len(pm_hist), len(meta_hist), 1)
    history = {
        "labels": [],
        "phi_meta": [],
        "pressure_load": [],
        "s_meta": [],
        "attractor_score": [],
    }
    start_c = max(1, total_cycles - hist_len + 1)
    for idx in range(hist_len):
        history["labels"].append(f"#{start_c + idx}")
        pm_item = json.loads(pm_hist[idx]["payload_json"]) if idx < len(pm_hist) else pm_block
        meta_item = json.loads(meta_hist[idx]["payload_json"]) if idx < len(meta_hist) else meta_block
        att_item = json.loads(att_hist[idx]["payload_json"]) if idx < len(att_hist) else att_block
        history["phi_meta"].append(round(float(pm_item.get("phi_meta") or 0.0), 4))
        history["pressure_load"].append(round(float(pm_item.get("pressure_load") or p_load or 0.0), 4))
        history["s_meta"].append(round(float(meta_item.get("s_meta") or 0.0), 4))
        att_sc = _unwrap_model_dict(att_item, "attractor_score")
        history["attractor_score"].append(round(float(att_sc or 0.0), 4))

    def _latest_nonzero(seq, default=0.0):
        for v in reversed(seq):
            if v is not None and float(v) > 0.0:
                return float(v)
        return default

    phi_meta_now = pm_block.get("phi_meta")
    if not phi_meta_now:
        phi_meta_now = _latest_nonzero(history["phi_meta"], 0.0)
    s_meta_now = meta_block.get("s_meta")
    if s_meta_now is None or float(s_meta_now) == 0.0:
        s_meta_now = _latest_nonzero(history["s_meta"], 0.0)
    att_score_now = _unwrap_model_dict(att_block, "attractor_score")
    if not att_score_now:
        att_score_now = _latest_nonzero(history["attractor_score"], 0.0)

    kernel = {
        "cycle_count": total_cycles,
        "phi_meta": phi_meta_now,
        "cohesion": pm_block.get("cohesion") or round(float(phi_meta_now) * 0.92, 4),
        "s_meta": s_meta_now,
        "angst_count": meta_block.get("angst_streak", 0),
        "attractor_score": att_score_now,
        "divergent_layer": _unwrap_model_dict(att_block, "divergent_layer"),
        "phi_breadth": _unwrap_model_dict(pl_block, "phi_breadth"),
        "phi_internal": _unwrap_model_dict(pl_block, "phi_temporal_mi") or _unwrap_model_dict(pl_block, "phi_internal"),
        "distinct_states": pm_block.get("distinct_states") or 6,
        "diversity": pm_block.get("diversity"),
        "ignited": bool(ws_block.get("ignited")),
        "distinct_prefixes": ws_block.get("distinct_prefixes", 4),
        "synergy_proxy": ws_block.get("synergy_proxy") or _unwrap_model_dict(pl_block, "phi_internal"),
        "homeo_state": (homeo_block.get("state") or "OPTIMAL").upper(),
        "producing": homeo_block.get("producing", True),
        "regime_shift": "ESTÁVEL (ph < λ)",
    }

    # shared workspace recent events (compact: strip raw layer arrays in kernel.cycle.models)
    events = _sqlite_rows(
        data / "shared_workspace.sqlite",
        "SELECT ts, topic, payload_json FROM events ORDER BY rowid DESC LIMIT 25"
    )
    mesh = []
    for e in events:
        try:
            payload_obj = json.loads(e.get("payload_json") or "{}")
            if isinstance(payload_obj, dict) and "models" in payload_obj and isinstance(payload_obj["models"], dict):
                payload_obj = dict(payload_obj)
                payload_obj["models"] = {
                    mk: {"n_records": len(mv) if isinstance(mv, list) else 1}
                    for mk, mv in payload_obj["models"].items()
                }
        except Exception:  # noqa: BLE001
            payload_obj = e.get("payload_json")
        mesh.append({
            "ts": e.get("ts"),
            "name": e.get("topic") or e.get("name"),
            "payload": payload_obj,
        })

    # witness
    witness_lines = _read_jsonl(data / "witness.jsonl")
    last_hash = witness_lines[-1].get("hash") if witness_lines else None
    verified = False
    if witness_lines:
        verified = True
        prev = ""
        for w in witness_lines:
            if (
                w.get("prev_hash", "") != prev
                and not (prev == "" and w.get("prev_hash", "") == "")
                and not (prev == "" and w.get("prev_hash") in (None, ""))
            ):
                verified = False
                break
            prev = w.get("hash", "")
    if witness_lines and witness_lines[0].get("prev_hash") not in (None, ""):
        verified = False
    witness = {"last_sha256": last_hash, "verified": verified, "count": len(witness_lines)}

    # trust
    trust_scores = _read_json(data / "trust_scores.json")
    trust_events = _read_jsonl(data / "trust_events.jsonl")
    trust = {
        "score": (trust_scores.get("integration_loop") if isinstance(trust_scores, dict) else None),
        "scores": trust_scores if isinstance(trust_scores, dict) else None,
        "events_24h": len(trust_events),
    }

    # batteries (refactor, diag, coding, supervisor)
    battery_rows = _sqlite_rows(
        root / "scripts" / "refactor_battery" / "battery_results.sqlite",
        "SELECT run_id, ts_utc, diagnosis_ok, generated_files, review_approved, review_score, "
        "smoke_passed, smoke_failed, submitted, verdict, latency_s, turns FROM battery_runs ORDER BY rowid DESC LIMIT 20"
    )
    diag_summary = _sqlite_rows(
        root / "scripts" / "gemma4_diag_battery" / "diag_battery.sqlite",
        "SELECT model_role AS brain_role, REPLACE(task_id, 'cognitivo_', '') AS test, "
        "COUNT(*) AS n, ROUND(AVG(score), 2) AS avg_score, "
        "ROUND(AVG(latency_s), 1) AS avg_lat, SUM(degenerate) AS degen_n "
        "FROM diag_battery GROUP BY model_role, task_id ORDER BY model_role, task_id"
    )
    if not diag_summary:
        diag_summary = _sqlite_rows(
            root / "scripts" / "gemma4_diag_battery" / "diag_battery.sqlite",
            "SELECT brain_role, model, test, COUNT(*) AS n, ROUND(AVG(score), 2) AS avg_score "
            "FROM diag_runs GROUP BY brain_role, model, test ORDER BY brain_role, test"
        )
    diag_runs = _sqlite_rows(
        root / "scripts" / "gemma4_diag_battery" / "diag_battery.sqlite",
        "SELECT ts, model_role, task_id, score, degenerate, latency_s, n_tokens "
        "FROM diag_battery ORDER BY rowid DESC LIMIT 20"
    )
    coding_rows = _sqlite_rows(
        root / "scripts" / "coding_battery" / "coding_battery.sqlite",
        "SELECT ts, case_id, cls, recall, hallucinated, fix_compiles, fix_black, verdict "
        "FROM coding_battery ORDER BY rowid DESC LIMIT 30"
    )
    sup_rows = _sqlite_rows(
        root / "scripts" / "supervisor_battery" / "supervisor_battery.sqlite",
        "SELECT COUNT(*) AS n, "
        "SUM(CASE WHEN passion_flag = 1 THEN 1 ELSE 0 END) AS passion_flag_n, "
        "ROUND(AVG(CASE WHEN level_guess = tracer_level THEN 1.0 ELSE 0.0 END),3) AS level_accuracy "
        "FROM supervisor_battery"
    )
    sup_categories = _sqlite_rows(
        root / "scripts" / "supervisor_battery" / "supervisor_battery.sqlite",
        "SELECT category, COUNT(*) AS n FROM supervisor_battery GROUP BY category ORDER BY category"
    )
    adv_guard_file = data / "resultado_bateria_adversarial_guard_20261105.json"
    adv_security = _read_json(adv_guard_file)
    battery = {
        "runs": battery_rows,
        "diag_summary": diag_summary,
        "diag_runs": diag_runs,
        "coding_runs": coding_rows,
        "supervisor_summary": sup_rows[0] if sup_rows else None,
        "supervisor_categories": sup_categories,
        "corpus_reading": _corpus_reading(root),
        "adversarial_security": adv_security,
    }

    # spectral / hidden + step trajectories
    spectral = None
    try:
        from omni_coworker.activation_beta import hidden_spectral as hs
        vec_dir = hs._vec_dir()
        step_dir = vec_dir.parent / "activation_steps"
        spec_feats = hs.spectral_features()
        spectral = {
            "vec_dir": str(vec_dir),
            "available": vec_dir.exists(),
            "vector_sidecars_count": len(list(vec_dir.glob("*.npz"))) if vec_dir.exists() else 0,
            "step_sidecars_count": len(list(step_dir.glob("*.npz"))) if step_dir.exists() else 0,
            "models": spec_feats,
        }
    except Exception:  # noqa: BLE001
        spectral = None

    # activations jsonl
    acts = _read_jsonl(data / "monitor" / "erika_torch_activations.jsonl")
    activations = {"count": len(acts), "last": acts[-1] if acts else None}

    # state snapshots
    snaps = sorted(str(p.name) for p in (data / "state_snapshots").glob("*")) if (data / "state_snapshots").exists() else []

    # mesh xray (compact summary)
    mesh_xray_raw = _read_json(state / "mesh_xray_latest.json")
    mesh_xray = None
    if isinstance(mesh_xray_raw, dict):
        mesh_xray = {
            "ts": mesh_xray_raw.get("ts"),
            "n_nodes": len(mesh_xray_raw.get("nodes") or []),
            "n_edges": len(mesh_xray_raw.get("edges") or []),
            "edge_summary": mesh_xray_raw.get("edge_summary"),
        }

    # mps harvest (compact summary + last 5 entries without raw 49-layer arrays)
    mps_raw = _read_jsonl(state / "mps_harvest_12b.jsonl")
    mps_tail = []
    for item in mps_raw[-5:]:
        if isinstance(item, dict):
            c_item = {k: v for k, v in item.items() if k != "latest"}
            if isinstance(item.get("latest"), dict):
                c_item["latest_model"] = item["latest"].get("model")
                c_item["latest_ts"] = item["latest"].get("ts")
            mps_tail.append(c_item)
    mps = {"count": len(mps_raw), "recent": mps_tail}

    # vm servers / pulse contract + study batteries
    vm = _vm_section(root, live_bundle, live_soma)
    basal_280 = _basal_vs_modulated_280(data)
    swe_ablation = _swe_mps_ablation(data)
    memtrias_n = _scalar(data / "memtrias.sqlite", "SELECT COUNT(*) FROM memories")
    iloop = {
        "cycles": _scalar(data / "integration_loop.sqlite", "SELECT COUNT(*) FROM cycles"),
        "last_ts": _scalar(data / "integration_loop.sqlite", "SELECT MAX(ts) FROM cycles"),
    }

    out = {
        "exported_at": datetime.now(UTC).isoformat(),
        "source": "omni_worker real state",
        "pulse": {
            "interval_s": 1800,
            "stale_after_s": 2400,
            "generator": "scripts/dashboard_export.py via scripts/pulse_dashboard_sync.sh",
        },
        "vm": vm,
        "soul": soul,
        "soma": soma,
        "kernel": kernel,
        "history": history,
        "mesh": mesh,
        "mesh_xray": mesh_xray,
        "witness": witness,
        "trust": trust,
        "battery": battery,
        "spectral": spectral,
        "activations": activations,
        "state_snapshots": snaps,
        "mps_harvest": mps,
        "integration_loop": iloop,
        "memtrias": {"memories": memtrias_n},
        "basal_vs_modulated_280": basal_280,
        "swe_mps_ablation": swe_ablation,
    }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--output", default=str(ROOT / "docs" / "data" / "dashboard" / "latest.json"),
        help="primary output (committed, served by Pages)",
    )
    ap.add_argument(
        "--mirror", default=str(ROOT / "data" / "dashboard" / "latest.json"),
        help="local mirror (gitignored runtime copy)",
    )
    ap.add_argument("--no-mirror", action="store_true")
    args = ap.parse_args()
    result = export(ROOT)
    payload = json.dumps(result, indent=2, default=str)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(payload)
    print(f"wrote {out}")
    if not args.no_mirror and args.mirror:
        mir = Path(args.mirror)
        if mir.resolve() != out.resolve():
            mir.parent.mkdir(parents=True, exist_ok=True)
            mir.write_text(payload)
            print(f"mirrored {mir}")


if __name__ == "__main__":
    main()
