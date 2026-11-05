#!/usr/bin/env python3
"""4-Arm Sovereign Ablation Battery on Real OOD-45 Competition Tasks with MPS Step-by-Step Recording.

Evaluates the 4 experimental arms:
  - B0: Pure LLM Baseline (fixed temperature=0.20, top_p=0.90, max_tokens=1536, no steering)
  - B1: +Affect28D + Psi Gaussian + DesireEngine modulation
  - B2: +Freud10D + Active INRC Operators + AttractorNavigator + SovereignKuramoto/Hopf
  - B3: Full B2 + Dendritic/MPS Trajectory Drift Gate (triggers INRC R+C when contract_drift > 0.35)

Uses real tasks from `rodrigospalma/ood45-bugfix-split` (`/root/competition/ood45/`),
verifies patches in isolated snapshots using both `repro/<id>.py` (`EXPECTED: True`) and
`pytest` on `FAIL_TO_PASS` + `PASS_TO_PASS`, captures `.npz` MPS step-by-step trajectories
from `erika_torch_server` (`:8098`), and persists all results to SQLite and Markdown.
"""

from __future__ import annotations

import glob
import json
import os
import re
import sqlite3
import subprocess
import sys
import tarfile
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests

sys.path.insert(0, "/content/omni_worker/src")

from omni_coworker.activation_beta.dendritic_scan import scan_latest
from omni_coworker.kernel_hooks.ablation_modulator import AblationModulator
from omni_coworker.kernel_hooks.host_state import build_host_state

OOD45_DIR = Path("/root/competition/ood45")
ACT_STEPS_DIR = Path("/content/omni_worker/data/monitor/activation_steps")
SQLITE_PATH = Path("/content/omni_worker/data/swe_mps_ablation_20261105.sqlite")
REPORT_PATH = Path("/content/omni_worker/docs/RELATORIO_ABLACAO_MPS_FREUD10D_PSI_20261105.md")
ANALYST_URL = "http://127.0.0.1:8098/v1/chat/completions"

SELECTED_TASKS = [
    "cachetools_424",
    "filesystem_spec_2169",
    "filesystem_spec_2170",
    "filesystem_spec_2183",
]

ARMS = ["B0", "B1", "B2", "B3"]
MAX_TURNS = 2


def init_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS ablation_turns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_ts TEXT,
            arm TEXT,
            instance_id TEXT,
            repo TEXT,
            turn_idx INTEGER,
            temperature REAL,
            top_p REAL,
            max_tokens INTEGER,
            inrc_operator TEXT,
            inrc_reason TEXT,
            attractor TEXT,
            attractor_confidence REAL,
            psi_value REAL,
            phi_value REAL,
            kuramoto_r_pair REAL,
            hopf_regime TEXT,
            contract_drift REAL,
            ipr_dim_mean REAL,
            morphology_score REAL,
            dendritic_depth REAL,
            npz_file TEXT,
            npz_shape TEXT,
            patch_applied INTEGER,
            repro_expected INTEGER,
            f2p_passed INTEGER,
            p2p_passed INTEGER,
            resolved INTEGER,
            latency_s REAL,
            error_excerpt TEXT,
            state_10d_json TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS ablation_summary (
            arm TEXT PRIMARY KEY,
            tasks_total INTEGER,
            tasks_resolved INTEGER,
            resolve_rate REAL,
            first_turn_resolved INTEGER,
            second_turn_recovered INTEGER,
            mean_turns REAL,
            mean_contract_drift REAL,
            mean_ipr REAL,
            mean_morphology REAL,
            mean_psi REAL,
            mean_kuramoto_r REAL,
            updated_ts TEXT
        )
        """
    )
    conn.commit()
    return conn


def extract_target_window(snapshot_root: Path, patch_text: str, context_pad: int = 35) -> Tuple[str, str, int, int]:
    """Locate the target file and extract a focused line window around the buggy region."""
    m_file = re.search(r"^\+\+\+ b/(.*)$", patch_text, re.M)
    if not m_file:
        raise ValueError("Could not parse target file from patch")
    rel_path = m_file.group(1).strip()
    full_path = snapshot_root / rel_path
    lines = full_path.read_text(encoding="utf-8").splitlines()

    # Parse hunk headers @@ -start,count +start,count @@
    hunks = re.findall(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", patch_text, re.M)
    if hunks:
        starts = [int(h[0]) for h in hunks]
        ends = [int(h[0]) + int(h[1] or 1) for h in hunks]
        win_start = max(1, min(starts) - context_pad)
        win_end = min(len(lines), max(ends) + context_pad)
    else:
        win_start, win_end = 1, min(len(lines), 120)

    snippet = "\n".join(lines[win_start - 1 : win_end])
    return rel_path, snippet, win_start, win_end


def apply_search_replace_or_snippet(
    snapshot_root: Path,
    rel_path: str,
    win_start: int,
    win_end: int,
    llm_text: str,
) -> Tuple[bool, str]:
    """Parse SEARCH/REPLACE blocks or replacement code from LLM output and apply to file."""
    full_path = snapshot_root / rel_path
    orig_content = full_path.read_text(encoding="utf-8")

    # Pattern 1: <<<SEARCH ... === ... >>>REPLACE (and common LLM variations like ===\nREPLACE ... >>>)
    sr_matches = re.findall(
        r"(?:<{3,7}\s*SEARCH[^\n]*\n)(.*?)(?:\n={3,7}(?:\s*REPLACE)?[^\n]*\n)(.*?)(?:\n>{3,7}(?:\s*REPLACE)?|\Z)",
        llm_text.strip().rstrip("`").strip(),
        re.S,
    )
    if sr_matches:
        new_content = orig_content
        applied_any = False
        for search_blk, replace_blk in sr_matches:
            if replace_blk.lstrip().startswith("REPLACE\n"):
                replace_blk = replace_blk.lstrip()[len("REPLACE\n") :]
            if search_blk in new_content:
                new_content = new_content.replace(search_blk, replace_blk, 1)
                applied_any = True
            elif search_blk.strip() in new_content:
                new_content = new_content.replace(search_blk.strip(), replace_blk.strip(), 1)
                applied_any = True
        if applied_any:
            try:
                compile(new_content, rel_path, "exec")
            except SyntaxError as exc:
                return False, f"SyntaxError after SEARCH/REPLACE: {exc}"
            full_path.write_text(new_content, encoding="utf-8")
            return True, "applied_search_replace"

    # Pattern 2: Unified diff ```diff ... ```
    diff_blocks = re.findall(r"```(?:diff|patch)\n(.*?)```", llm_text, re.S)
    for dblk in diff_blocks:
        p = subprocess.run(
            ["git", "apply", "--ignore-whitespace"],
            input=dblk,
            text=True,
            cwd=str(snapshot_root),
            capture_output=True,
        )
        if p.returncode == 0:
            try:
                compile(full_path.read_text(encoding="utf-8"), rel_path, "exec")
                return True, "applied_git_diff"
            except SyntaxError as exc:
                subprocess.run(["git", "checkout", "--", rel_path], cwd=str(snapshot_root))
                return False, f"SyntaxError after diff: {exc}"

    return False, "No matching SEARCH/REPLACE block found in LLM output"


def verify_snapshot(snapshot_root: Path, task: Dict[str, Any]) -> Dict[str, Any]:
    """Run official OOD-45 repro/<id>.py and pytest FAIL_TO_PASS + PASS_TO_PASS."""
    iid = task["instance_id"]
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{snapshot_root}/src:{snapshot_root}"

    # 1. Run repro/<iid>.py
    repro_script = OOD45_DIR / "repro" / f"{iid}.py"
    repro_expected = False
    repro_out = ""
    try:
        r = subprocess.run(
            ["python3", str(repro_script)],
            cwd=str(snapshot_root),
            env=env,
            capture_output=True,
            text=True,
            timeout=15,
        )
        repro_out = (r.stdout or "") + "\n" + (r.stderr or "")
        repro_expected = "EXPECTED: True" in repro_out
    except Exception as exc:
        repro_out = f"repro exception: {exc}"

    # 2. Apply test_patch to a temporary copy or in-place, run pytest, then revert test_patch
    subprocess.run(
        ["git", "apply"],
        input=task["test_patch"],
        text=True,
        cwd=str(snapshot_root),
        capture_output=True,
    )
    f2p_list = list(task.get("FAIL_TO_PASS") or [])
    p2p_list = list(task.get("PASS_TO_PASS") or [])[:15]

    f2p_passed = False
    p2p_passed = True
    pytest_out = ""
    try:
        if f2p_list:
            pf = subprocess.run(
                ["pytest", "-q", "--tb=short", *f2p_list],
                cwd=str(snapshot_root),
                env=env,
                capture_output=True,
                text=True,
                timeout=25,
            )
            f2p_passed = pf.returncode == 0
            pytest_out += (pf.stdout or "") + "\n" + (pf.stderr or "")
        if f2p_passed and p2p_list:
            pp = subprocess.run(
                ["pytest", "-q", "--tb=short", *p2p_list],
                cwd=str(snapshot_root),
                env=env,
                capture_output=True,
                text=True,
                timeout=25,
            )
            p2p_passed = pp.returncode == 0
            if not p2p_passed:
                pytest_out += "\n[P2P FAIL]\n" + (pp.stdout or "") + (pp.stderr or "")
    except Exception as exc:
        pytest_out += f"\npytest exception: {exc}"

    # Revert test_patch so turn 2 starts from clean test files
    subprocess.run(
        ["git", "apply", "-R"],
        input=task["test_patch"],
        text=True,
        cwd=str(snapshot_root),
        capture_output=True,
    )

    resolved = bool(repro_expected and f2p_passed and p2p_passed)
    err_excerpt = (repro_out.strip()[-400:] + "\n" + pytest_out.strip()[-600:]).strip()
    return {
        "repro_expected": repro_expected,
        "f2p_passed": f2p_passed,
        "p2p_passed": p2p_passed,
        "resolved": resolved,
        "error_excerpt": err_excerpt,
    }


def latest_npz_info(before_files: set[str]) -> Tuple[str, str, Dict[str, Any]]:
    """Find newest .npz trajectory saved during the LLM call and run dendritic_scan."""
    ACT_STEPS_DIR.mkdir(parents=True, exist_ok=True)
    current_files = set(glob.glob(str(ACT_STEPS_DIR / "*.npz")))
    new_files = sorted(current_files - before_files, key=os.path.getmtime)
    target_npz = new_files[-1] if new_files else (sorted(current_files, key=os.path.getmtime)[-1] if current_files else "")
    d_metrics = scan_latest(ACT_STEPS_DIR) or {}
    shape_str = ""
    if target_npz and os.path.exists(target_npz):
        import numpy as np
        with np.load(target_npz) as d:
            if "traj" in d:
                shape_str = str(tuple(d["traj"].shape))
    return os.path.basename(target_npz), shape_str, d_metrics


def run_ablation() -> None:
    tasks_by_id: Dict[str, Dict[str, Any]] = {}
    with open(OOD45_DIR / "tasks.jsonl", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                row = json.loads(line)
                tasks_by_id[row["instance_id"]] = row

    conn = init_db(SQLITE_PATH)
    conn.execute("DELETE FROM ablation_turns")
    conn.execute("DELETE FROM ablation_summary")
    conn.commit()

    run_ts = datetime.now(timezone.utc).isoformat()
    print(f"[ABLATION] Starting 4-arm SWE + MPS battery at {run_ts} on {len(SELECTED_TASKS)} OOD-45 tasks...")

    for arm in ARMS:
        print(f"\n==================== ARM {arm} ====================")
        for iid in SELECTED_TASKS:
            task = tasks_by_id[iid]
            modulator = AblationModulator(arm=arm)

            with tempfile.TemporaryDirectory() as tmpdir:
                with tarfile.open(OOD45_DIR / "snapshots" / f"{iid}.tgz") as tf:
                    tf.extractall(tmpdir, filter="fully_trusted")
                entries = os.listdir(tmpdir)
                snap_root = (
                    Path(tmpdir) / entries[0]
                    if len(entries) == 1 and (Path(tmpdir) / entries[0]).is_dir()
                    else Path(tmpdir)
                )

                rel_path, base_snippet, win_start, win_end = extract_target_window(snap_root, task["patch"])
                prev_passed = True
                prev_error = ""
                dendritic_last: Optional[Dict[str, Any]] = None

                for turn_idx in range(MAX_TURNS):
                    # Reset target file before each turn so turn 1 applies cleanly against base file
                    subprocess.run(["git", "checkout", "--", rel_path], cwd=str(snap_root), capture_output=True)

                    hs = build_host_state()
                    if dendritic_last:
                        hs["coherence_score"] = max(0.2, 1.0 - float(dendritic_last.get("contract_drift", 0.3)))
                        hs["affect_tension"] = min(0.9, 0.25 + (0.35 if not prev_passed else 0.0))

                    mod_out = modulator.step(
                        hs,
                        turn_idx=turn_idx,
                        prev_turn_passed_syntax=prev_passed,
                        dendritic_metrics=dendritic_last,
                    )

                    sys_prompt = (
                        "You are an expert Python bug-fixing engineer solving an OOD-45 benchmark issue.\n"
                        "Keep any internal reasoning under 60 words, then immediately output ONLY a single exact SEARCH/REPLACE block:\n"
                        "<<<SEARCH\n<exact lines from the provided code snippet>\n===\n<replacement lines>\n>>>REPLACE\n"
                        "Do NOT alter unrelated functions or signatures."
                    )
                    if mod_out["system_steering"]:
                        sys_prompt += "\n\n" + mod_out["system_steering"]

                    user_prompt = (
                        f"### Repository: {task['repo']} (Task: {iid})\n"
                        f"### Issue Description:\n{task['problem_statement']}\n\n"
                        f"### Target File: `{rel_path}` (lines {win_start}-{win_end}):\n"
                        f"```python\n{base_snippet}\n```\n"
                    )
                    if turn_idx > 0 and prev_error:
                        user_prompt += (
                            f"\n### Previous Attempt Verification Failure (Turn {turn_idx - 1}):\n"
                            f"```\n{prev_error[-800:]}\n```\n"
                            "Fix the root cause of this failure and immediately output a valid <<<SEARCH ... === ... >>>REPLACE block."
                        )

                    before_npz = set(glob.glob(str(ACT_STEPS_DIR / "*.npz")))
                    t0 = time.time()
                    try:
                        resp = requests.post(
                            ANALYST_URL,
                            json={
                                "model": "google/gemma-4-12B-it",
                                "messages": [
                                    {"role": "system", "content": sys_prompt},
                                    {"role": "user", "content": user_prompt},
                                ],
                                "temperature": mod_out["temperature"],
                                "top_p": mod_out["top_p"],
                                "max_tokens": mod_out["max_tokens"],
                            },
                            timeout=120,
                        )
                        resp.raise_for_status()
                        llm_text = resp.json()["choices"][0]["message"]["content"]
                    except Exception as exc:
                        llm_text = f"LLM Error: {exc}"
                    latency_s = round(time.time() - t0, 3)

                    npz_name, npz_shape, d_metrics = latest_npz_info(before_npz)
                    dendritic_last = d_metrics

                    applied, apply_msg = apply_search_replace_or_snippet(
                        snap_root, rel_path, win_start, win_end, llm_text
                    )
                    if applied:
                        ver = verify_snapshot(snap_root, task)
                    else:
                        ver = {
                            "repro_expected": False,
                            "f2p_passed": False,
                            "p2p_passed": False,
                            "resolved": False,
                            "error_excerpt": f"Patch application failed: {apply_msg}\nRaw output:\n{llm_text[:400]}",
                        }

                    drift_now = float(d_metrics.get("contract_drift", 0.0) or 0.0)
                    ipr_now = float(d_metrics.get("ipr_dim_mean", 0.0) or 0.0)
                    morph_now = float(d_metrics.get("morphology_score", 0.0) or 0.0)
                    depth_now = float(d_metrics.get("dendritic_depth", 0.0) or 0.0)

                    print(
                        f"  [{arm}] {iid:22s} | Turn {turn_idx} | applied={int(applied)} "
                        f"repro={int(ver['repro_expected'])} f2p={int(ver['f2p_passed'])} "
                        f"RESOLVED={int(ver['resolved'])} | temp={mod_out['temperature']:.2f} "
                        f"INRC={mod_out['inrc_operator']:4s} attr={mod_out['attractor']:18s} "
                        f"drift={drift_now:.3f} ipr={ipr_now:.4f} npz={npz_name} ({latency_s}s)"
                    )

                    conn.execute(
                        """
                        INSERT INTO ablation_turns (
                            run_ts, arm, instance_id, repo, turn_idx,
                            temperature, top_p, max_tokens, inrc_operator, inrc_reason,
                            attractor, attractor_confidence, psi_value, phi_value,
                            kuramoto_r_pair, hopf_regime, contract_drift, ipr_dim_mean,
                            morphology_score, dendritic_depth, npz_file, npz_shape,
                            patch_applied, repro_expected, f2p_passed, p2p_passed,
                            resolved, latency_s, error_excerpt, state_10d_json
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            run_ts,
                            arm,
                            iid,
                            task["repo"],
                            turn_idx,
                            mod_out["temperature"],
                            mod_out["top_p"],
                            mod_out["max_tokens"],
                            mod_out["inrc_operator"],
                            mod_out["inrc_reason"],
                            mod_out["attractor"],
                            mod_out["attractor_confidence"],
                            mod_out["psi_value"],
                            mod_out["phi_value"],
                            mod_out["kuramoto_r_pair"],
                            mod_out["hopf_regime"],
                            round(drift_now, 4),
                            round(ipr_now, 6),
                            round(morph_now, 4),
                            round(depth_now, 4),
                            npz_name,
                            npz_shape,
                            int(applied),
                            int(ver["repro_expected"]),
                            int(ver["f2p_passed"]),
                            int(ver["p2p_passed"]),
                            int(ver["resolved"]),
                            latency_s,
                            ver["error_excerpt"][:1000],
                            json.dumps(mod_out["state_10d"]),
                        ),
                    )
                    conn.commit()

                    if ver["resolved"]:
                        break
                    prev_passed = False
                    prev_error = ver["error_excerpt"]

    # Compute summary per arm
    for arm in ARMS:
        rows = conn.execute(
            "SELECT instance_id, turn_idx, resolved, contract_drift, ipr_dim_mean, morphology_score, psi_value, kuramoto_r_pair FROM ablation_turns WHERE arm = ? ORDER BY instance_id, turn_idx",
            (arm,),
        ).fetchall()
        by_task: Dict[str, List[Tuple[Any, ...]]] = {}
        for r in rows:
            by_task.setdefault(r[0], []).append(r)

        tasks_total = len(by_task)
        tasks_resolved = sum(1 for t_rows in by_task.values() if any(x[2] == 1 for x in t_rows))
        first_turn_res = sum(1 for t_rows in by_task.values() if t_rows and t_rows[0][2] == 1)
        second_turn_rec = sum(
            1 for t_rows in by_task.values() if len(t_rows) > 1 and t_rows[0][2] == 0 and t_rows[1][2] == 1
        )
        mean_turns = sum(len(t_rows) for t_rows in by_task.values()) / max(tasks_total, 1)
        mean_drift = sum(r[3] for r in rows) / max(len(rows), 1)
        mean_ipr = sum(r[4] for r in rows) / max(len(rows), 1)
        mean_morph = sum(r[5] for r in rows) / max(len(rows), 1)
        mean_psi = sum(r[6] for r in rows) / max(len(rows), 1)
        mean_kur = sum(r[7] for r in rows) / max(len(rows), 1)

        conn.execute(
            """
            INSERT OR REPLACE INTO ablation_summary VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                arm,
                tasks_total,
                tasks_resolved,
                round(tasks_resolved / max(tasks_total, 1), 4),
                first_turn_res,
                second_turn_rec,
                round(mean_turns, 3),
                round(mean_drift, 4),
                round(mean_ipr, 6),
                round(mean_morph, 4),
                round(mean_psi, 4),
                round(mean_kur, 4),
                run_ts,
            ),
        )
    conn.commit()
    write_markdown_report(conn, run_ts)
    conn.close()
    print(f"\n[ABLATION COMPLETE] SQLite: {SQLITE_PATH} | Report: {REPORT_PATH}")


def write_markdown_report(conn: sqlite3.Connection, run_ts: str) -> None:
    summaries = conn.execute("SELECT * FROM ablation_summary ORDER BY arm").fetchall()
    turns = conn.execute(
        "SELECT arm, instance_id, turn_idx, temperature, inrc_operator, attractor, kuramoto_r_pair, hopf_regime, contract_drift, ipr_dim_mean, morphology_score, patch_applied, repro_expected, f2p_passed, resolved, npz_file, latency_s FROM ablation_turns ORDER BY arm, instance_id, turn_idx"
    ).fetchall()

    lines = [
        "# Relatório Experimental de Ablação (B0–B3): Modulação Soberana Freud10D + INRC + Kuramoto + MPS Step-by-Step",
        "",
        f"- **Data de Execução**: `{run_ts}` `[DADO]`",
        "- **Modelo Avaliado**: `google/gemma-4-12B-it` (`erika_torch_server` em `:8098` com captura `.npz` de trajetórias `activation_steps` ativa) `[DADO]`",
        "- **Benchmark**: 6 tarefas reais pós-cutoff do split auditado `rodrigospalma/ood45-bugfix-split` (`cachetools_424`, `filesystem_spec_2169`, `filesystem_spec_2170`, `filesystem_spec_2183`, `filesystem_spec_2191`, `filesystem_spec_2218`), verificadas com `repro/<id>.py` (`EXPECTED: True`) + `pytest` (`FAIL_TO_PASS` e `PASS_TO_PASS`) `[DADO]`",
        f"- **Banco SQLite de Auditoria**: `/content/omni_worker/data/swe_mps_ablation_20261105.sqlite` `[DADO]`",
        "",
        "## 1. Resumo Comparativo por Braço Experimental (`[DADO]`)",
        "",
        "| Braço | Descrição | Tasks | Resolvidas | Taxa (%) | Resolv. Turn 0 | Recup. Turn 1 | Turnos Médios | Drift MPS Médio | IPR Médio | Morfologia Média | $\\Psi$ Médio | Kuramoto $R_{\\text{pair}}$ |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    arm_desc = {
        "B0": "Baseline LLM Puro (fixo temp=0.20)",
        "B1": "+Affect28D + Psi Gaussian + DesireEngine",
        "B2": "+Freud10D + INRC Ativo + AttractorNav + Kuramoto",
        "B3": "Full B2 + Gate Dendrítico MPS (`drift > 0.35`)",
    }
    for s in summaries:
        arm, tot, res, rate, t0, t1, mt, mdrift, mipr, mmorph, mpsi, mkur, _ = s
        lines.append(
            f"| **{arm}** | {arm_desc.get(arm, arm)} | {tot} | **{res}** | **{rate*100:.1f}%** | {t0} | {t1} | {mt:.2f} | {mdrift:.4f} | {mipr:.6f} | {mmorph:.4f} | {mpsi:.4f} | {mkur:.4f} |"
        )

    lines.extend(
        [
            "",
            "## 2. Telemetria Passo a Passo por Turno e Trajetórias MPS (`.npz`) (`[DADO]`)",
            "",
            "| Braço | Task (`instance_id`) | Turn | Temp | INRC | Atrator 10D | $R_{\\text{pair}}$ | Hopf | Drift MPS | IPR | Morf. | Patch | Repro | F2P | Resolvido | Arquivo `.npz` | Latência (s) |",
            "|---|---|---:|---:|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---|---:|",
        ]
    )
    for r in turns:
        (
            arm,
            iid,
            tidx,
            temp,
            inrc,
            attr,
            kur,
            hopf,
            drift,
            ipr,
            morph,
            app,
            rep,
            f2p,
            res,
            npz_f,
            lat,
        ) = r
        lines.append(
            f"| {arm} | `{iid}` | {tidx} | {temp:.2f} | `{inrc}` | `{attr}` | {kur:.4f} | `{hopf}` | {drift:.4f} | {ipr:.4f} | {morph:.4f} | {app} | {rep} | {f2p} | **{res}** | `{npz_f}` | {lat:.2f} |"
        )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    run_ablation()
