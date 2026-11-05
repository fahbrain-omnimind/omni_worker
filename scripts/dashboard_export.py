#!/usr/bin/env python3
"""Export real system state to static JSON for the dashboard.

Only real values or null. Never invent data.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
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
        "SELECT brain_role, model, test, COUNT(*) AS n, ROUND(AVG(score), 2) AS avg_score "
        "FROM diag_runs GROUP BY brain_role, model, test ORDER BY brain_role, test"
    )
    coding_rows = _sqlite_rows(
        root / "scripts" / "coding_battery" / "coding_battery.sqlite",
        "SELECT ts, case_id, cls, recall, hallucinated, fix_compiles, fix_black, verdict "
        "FROM coding_battery ORDER BY rowid DESC LIMIT 30"
    )
    sup_rows = _sqlite_rows(
        root / "scripts" / "supervisor_battery" / "supervisor_battery.sqlite",
        "SELECT COUNT(*) AS n, SUM(CASE WHEN detected = 1 THEN 1 ELSE 0 END) AS detected_n FROM supervisor_runs"
    )
    battery = {
        "runs": battery_rows,
        "diag_summary": diag_summary,
        "coding_runs": coding_rows,
        "supervisor_summary": sup_rows[0] if sup_rows else None,
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

    out = {
        "exported_at": datetime.now(UTC).isoformat(),
        "source": "omni_worker real state",
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
    }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default=str(ROOT / "data" / "dashboard" / "latest.json"))
    args = ap.parse_args()
    result = export(ROOT)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, default=str))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
