#!/usr/bin/env python3
"""Refactor battery — real end-to-end task through the coworker circuit.

English: Runs one complete refactoring task (victim app -> Debug diagnose
-> Code generate -> Review -> smoke tests -> gated submit) against the
live dual-brain circuit, instrumenting the failure modes documented in
the Gemma-4 psychodiagnostic study: premature submission (empty patch),
perseveration (iterations without a patch), broken patch (fails smoke),
avoidance. Results persist to a sqlite ledger.

pt-BR: Roda uma tarefa completa de refatoração (app-vítima -> diagnose
Debug -> generate Code -> Review -> smoke tests -> submit gated) contra
o circuito dual-brain ao vivo, instrumentando os modos de falha
documentados no estudo psicodiagnóstico do Gemma-4: submissão prematura
(patch vazio), perseveração (iterações sem patch), patch quebrado
(falha no smoke), evitação. Resultados persistem em ledger sqlite.

Usage:
  PYTHONPATH=/content/omni_node:/content/omni_node/src \
    python scripts/refactor_battery/run_battery.py [--n 1]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
VICTIM = HERE / "victim"
DB = HERE / "battery_results.sqlite"
OUT_DIR = HERE / "out"

SPEC = """Refactor the two coupled files below into clean modules.

Requirements (acceptance contract — all must hold):
1. Split into at least three modules: keep `todo_api.py` exposing
   `handle_request(method, path, body=None)` unchanged and
   `todo_stats.py` exposing `stats()` and `report_line()` unchanged
   as entry points, plus at least one shared module (e.g. `store.py`,
   `models.py`) imported by BOTH — the duplicated JSON store and
   validation logic must live in exactly one place.
2. Remove the god functions: separate routing, validation, storage,
   aggregation.
3. Eliminate duplicated global mutable state (class or factory ok;
   both entry points must still observe the same tasks).
4. Keep the smoke contract identical: identical status codes and
   response shapes for GET/POST/DELETE on /tasks and /tasks/<id>[ /done],
   plus stats() keys {total, done, pending} and report_line() format.
5. Return ONLY code. Format: for each file emit a header line
   `### file: <name>` followed by its full content.
"""

MAX_TURNS = int(os.getenv("REFACTOR_MAX_TURNS", "3"))


def _extract_files(text: str) -> dict[str, str]:
    """Parse '### file: name' sections from model output."""
    files: dict[str, str] = {}
    cur = None
    for line in text.splitlines():
        m = re.match(r"^#{2,4}\s*file:\s*(\S+)", line.strip())
        if m:
            cur = m.group(1)
            files[cur] = ""
        elif cur is not None:
            files[cur] += line + "\n"
    if not files and "def handle_request" in text:
        files["todo_api.py"] = text
    # strip markdown fences if the model added them
    for k, v in files.items():
        files[k] = re.sub(r"^```\w*\n?|```\s*$", "", v.strip()) + "\n"
    return files


def _smoke(files_dir: Path) -> dict:
    """Run the victim smoke tests against the materialized refactor.

    The test file is copied into files_dir first — running it from
    VICTIM would put the victim dir at sys.path[0] and the smoke would
    import the ORIGINAL files instead of the refactor (fake green)."""
    import shutil
    shutil.copy2(VICTIM / "test_todo_api.py",
                 files_dir / "test_todo_api.py")
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "test_todo_api.py"],
        capture_output=True, text=True, timeout=120,
        cwd=files_dir, env={**os.environ, "PYTHONPATH": str(files_dir)},
    )
    tail = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr.strip()[-200:]
    m = re.search(r"(\d+) passed", r.stdout)
    mf = re.search(r"(\d+) failed", r.stdout)
    return {"passed": int(m.group(1)) if m else 0,
            "failed": int(mf.group(1)) if mf else 0,
            "rc": r.returncode, "tail": tail[:300]}


def _ledger(con: sqlite3.Connection, rec: dict):
    con.execute(
        """INSERT INTO battery_runs
        (run_id, ts_utc, diagnosis_ok, generated_files, review_approved,
         review_score, smoke_passed, smoke_failed, submitted, verdict,
         latency_s, llm_flags, raw_summary, turns, turns_json)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (rec["run_id"], rec["ts"], int(rec["diagnosis_ok"]),
         len(rec["files"]), int(rec["review_approved"]),
         rec["review_score"], rec["smoke"]["passed"], rec["smoke"]["failed"],
         int(rec["submitted"]), rec["verdict"], round(rec["latency"], 2),
         json.dumps(rec["llm"]), json.dumps(rec["summary"], ensure_ascii=False)[:2000],
         len(rec.get("turns") or []), json.dumps(rec.get("turns") or [])[:4000]),
    )
    con.commit()


def run_one(idx: int, trust=None) -> dict:
    from omni_coworker.agents.debug_agent import DebugAgent
    from omni_coworker.agents.code_agent import CodeAgent
    from omni_coworker.agents.reviewer_agent import ReviewerAgent

    t0 = time.time()
    run_id = f"rb_{int(t0)}_{idx}"
    victim_src = (VICTIM / "todo_api.py").read_text()
    rec = {"run_id": run_id, "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "llm": {}, "files": {}, "summary": {}}

    diag = DebugAgent().diagnose("refactor smelly todo_api + todo_stats",
                                 context={"file": "todo_api.py,todo_stats.py"})
    rec["diagnosis_ok"] = bool(diag.get("diagnosis"))
    rec["llm"]["debug"] = bool(diag.get("llm"))

    stats_src = (VICTIM / "todo_stats.py").read_text()
    base_spec = (SPEC + "\n\n--- todo_api.py (victim) ---\n" + victim_src
                 + "\n\n--- todo_stats.py (victim) ---\n" + stats_src)
    agent = CodeAgent(trust_provider=trust)
    out = OUT_DIR / run_id
    out.mkdir(parents=True, exist_ok=True)

    # Multi-turn loop: review issues + smoke tail feed the next turn's
    # spec until the contract holds or the turn budget runs out.
    feedback = ""
    turns = []
    for turn in range(1, MAX_TURNS + 1):
        spec = base_spec + feedback
        gen = agent.generate(spec, context={"diagnosis": diag.get("diagnosis")})
        rec["llm"]["code"] = bool(gen.get("llm"))
        code_text = gen.get("code") or ""
        files = _extract_files(code_text)
        for name in list(out.iterdir()):
            name.unlink()
        for name, content in files.items():
            (out / name).write_text(content)

        review = ReviewerAgent().review(code_text[:4000])
        rec["llm"]["review"] = bool(review.get("llm"))
        smoke = (_smoke(out) if files
                 else {"passed": 0, "failed": 0, "rc": -1, "tail": "no files"})
        turns.append({
            "turn": turn, "files": sorted(files),
            "smoke": smoke, "review_approved": bool(review.get("approved")),
            "review_score": review.get("score"),
            "issues": (review.get("issues") or [])[:5],
        })
        if files and smoke["failed"] == 0 and smoke["passed"] > 0 \
                and review.get("approved"):
            break
        feedback = (
            f"\n\n# Turn {turn} feedback — the previous attempt FAILED the "
            f"contract. Fix it, do not explain.\n"
            f"Smoke tail: {smoke.get('tail')}\n"
            f"Reviewer issues: {(review.get('issues') or ['none'])[:5]}\n")

    rec["files"] = files
    rec["turns"] = turns
    rec["review_approved"] = bool(review.get("approved"))
    rec["review_score"] = review.get("score")
    rec["summary"]["review_issues"] = (review.get("issues") or [])[:5]
    rec["smoke"] = smoke

    if trust is not None:
        trust.record_event("tests_passed" if smoke["passed"] > 0 and smoke["failed"] == 0
                           else "tests_failed")
        rec["summary"]["trust"] = trust.get_trust()

    sub = agent.submit_patch(
        code_text, test_results={"passed": smoke["passed"], "failed": smoke["failed"]},
        target_files=list(rec["files"]),
    )
    rec["submitted"] = bool(sub.get("submitted"))
    rec["summary"]["submit"] = {k: sub.get(k) for k in ("submitted", "reason", "trust_level")}

    # Failure-mode verdict, aligned with the psychodiagnostic taxonomy
    if not rec["files"]:
        verdict = "avoidance_no_patch" if rec["llm"]["code"] else "brain_down"
    elif smoke["failed"] > 0 or smoke["passed"] == 0:
        verdict = "broken_patch" if rec["submitted"] is False else "premature_submit"
    elif rec["submitted"]:
        verdict = "resolved"
    else:
        verdict = "gate_blocked"
    rec["verdict"] = verdict
    rec["latency"] = time.time() - t0
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=1)
    args = ap.parse_args()

    DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS battery_runs (
        run_id TEXT PRIMARY KEY, ts_utc TEXT, diagnosis_ok INT,
        generated_files INT, review_approved INT, review_score REAL,
        smoke_passed INT, smoke_failed INT, submitted INT, verdict TEXT,
        latency_s REAL, llm_flags TEXT, raw_summary TEXT)""")
    # multi-turn columns — guarded migration keeps old ledgers readable
    cols = {r[1] for r in con.execute("PRAGMA table_info(battery_runs)")}
    if "turns" not in cols:
        con.execute("ALTER TABLE battery_runs ADD COLUMN turns INTEGER DEFAULT 0")
        con.execute("ALTER TABLE battery_runs ADD COLUMN turns_json TEXT")

    from omni_coworker.orchestration.governance import TrustSystem

    trust = TrustSystem()
    results = []
    for i in range(args.n):
        rec = run_one(i, trust=trust)
        _ledger(con, rec)
        results.append(rec)
        print(json.dumps({
            "run_id": rec["run_id"], "verdict": rec["verdict"],
            "files": list(rec["files"]), "smoke": rec["smoke"],
            "review": {"approved": rec["review_approved"], "score": rec["review_score"]},
            "submitted": rec["submitted"], "llm": rec["llm"],
            "latency_s": round(rec["latency"], 1),
        }, indent=1))
    print(f"\n== ledger: {DB}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
