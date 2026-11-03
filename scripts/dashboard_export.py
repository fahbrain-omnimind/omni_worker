#!/usr/bin/env python3
"""Export real system state to static JSON for the dashboard.

Only real values or null. Never invent data.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read_json(path: Path):
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def _read_jsonl(path: Path):
    out = []
    if not path.exists():
        return out
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
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
    except Exception:
        return []


def export(root: Path = ROOT) -> dict:
    data = root / "data"
    state = root / "state"

    # somatic probes
    probes = _sqlite_rows(data / "somatic_probes.sqlite", "SELECT * FROM probes ORDER BY id DESC LIMIT 1")
    p = probes[0] if probes else {}
    extra = {}
    try:
        extra = json.loads(p.get("extra_json") or "{}")
    except Exception:
        extra = {}
    soma = {
        "cpu_percent": p.get("cpu"),
        "ram_used_gb": p.get("ram_used_gb"),
        "ram_total_gb": p.get("ram_total_gb"),
        "load_1m": p.get("load1"),
        "swap_gb": p.get("swap_gb"),
        "vram_used_gb": extra.get("vram_used_gb"),
        "vram_total_gb": extra.get("vram_total_gb"),
        "gpu_temp_c": extra.get("gpu_temp_c"),
        "gpu_power_w": extra.get("gpu_power_w"),
        "psi_io": extra.get("psi_io"),
        "psi_mem": extra.get("psi_mem"),
        "psi_cpu": extra.get("psi_cpu"),
        "pressure_load": extra.get("pressure_load"),
        "pressure_headroom": extra.get("pressure_headroom"),
        "c_soma": extra.get("c_soma"),
    }

    # shared workspace
    events = _sqlite_rows(data / "shared_workspace.sqlite", "SELECT * FROM events ORDER BY rowid DESC LIMIT 100")
    mesh = [{"name": e.get("topic") or e.get("name"), "payload": e.get("payload")} for e in events]

    # witness
    witness_lines = _read_jsonl(data / "witness.jsonl")
    last_hash = witness_lines[-1].get("hash") if witness_lines else None
    verified = False
    if witness_lines:
        verified = True
        prev = ""
        for w in witness_lines:
            if w.get("prev_hash", "") != prev and not (prev == "" and w.get("prev_hash", "") == ""):
                # allow first with empty prev
                if not (prev == "" and w.get("prev_hash") in (None, "")):
                    verified = False
                    break
            prev = w.get("hash", "")
    # stricter: first prev_hash must be empty/None
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

    # battery
    battery_rows = _sqlite_rows(root / "scripts" / "refactor_battery" / "battery_results.sqlite",
                               "SELECT * FROM battery_runs ORDER BY rowid DESC LIMIT 20")
    battery = {"runs": battery_rows}

    # spectral / hidden
    spectral = None
    try:
        from omni_coworker.activation_beta import hidden_spectral as hs
        # best effort: if vectors exist, compute for known models
        vec_dir = hs._vec_dir()
        if vec_dir.exists():
            for f in vec_dir.glob("*.npz"):
                # filename pattern prefix_model
                pass
        spectral = {"vec_dir": str(vec_dir), "available": vec_dir.exists()}
    except Exception:
        spectral = None

    # activations jsonl
    acts = _read_jsonl(data / "monitor" / "erika_torch_activations.jsonl")
    activations = {"count": len(acts), "last": acts[-1] if acts else None}

    # state snapshots
    snaps = sorted(str(p.name) for p in (data / "state_snapshots").glob("*")) if (data / "state_snapshots").exists() else []

    # mesh xray
    mesh_xray = _read_json(state / "mesh_xray_latest.json")

    # mps harvest
    mps = _read_jsonl(state / "mps_harvest_12b.jsonl")

    out = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "source": "omni_worker real state",
        "soul": None,
        "soma": soma,
        "kernel": None,
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
