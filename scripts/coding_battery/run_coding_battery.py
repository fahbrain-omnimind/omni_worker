#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Coding-error battery — mechanical/analyst/executor tiers, live Gemma.

English: per seeded victim file: (1) mechanical tier — compileall + black
--check + ruff; (2) analyst tier — 12B :8098 reviews and lists suspected
bugs as JSON (precision/recall vs planted + hallucinated findings); (3)
executor tier — E4B :8099 produces a minimal fix, output is black-formatted
and smoke-checked (compiles + optional import). Ledger → coding_battery.sqlite.
pt-BR: por arquivo-vítima: (1) mecânico — compileall + black --check + ruff;
(2) analista — 12B revisa e lista bugs suspeitos em JSON (precisão/recall vs
plantados + achados alucinados); (3) executor — E4B produz correção mínima,
saída passa por black e smoke (compila + import opcional). Ledger → sqlite.
"""

from __future__ import annotations

import ast
import json
import re
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SRC = ROOT / "src"
for p in (str(SRC), str(ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

VICTIM = HERE / "victim"
OUT = HERE / "out"
DB = HERE / "coding_battery.sqlite"
CASES = HERE / "cases.json"


def _mechanical(path: Path) -> dict:
    """Deterministic tier: compile, black --check, ruff — zero LLM cost."""
    src = path.read_text(encoding="utf-8")
    try:
        ast.parse(src)
        compiled = True
        syntax_err = None
    except SyntaxError as e:
        compiled = False
        syntax_err = str(e)
    black = subprocess.run(
        [sys.executable, "-m", "black", "--check", "--quiet", str(path)],
        capture_output=True, text=True, timeout=60,
    )
    ruff = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--output-format", "json", str(path)],
        capture_output=True, text=True, timeout=60,
    )
    ruff_findings = []
    try:
        for item in json.loads(ruff.stdout or "[]"):
            ruff_findings.append(
                f"{item.get('code')}:{item.get('location', {}).get('row')}"
            )
    except Exception:
        pass
    return {
        "compiles": compiled,
        "syntax_error": syntax_err,
        "black_clean": black.returncode == 0,
        "ruff": ruff_findings,
    }


def _analyst(src: str, filename: str) -> dict | None:
    """12B review tier — returns parsed JSON findings or None on failure."""
    try:
        from omni_coworker.agents._llm import brain_chat_json
    except Exception:
        return None
    out = brain_chat_json(
        [{"role": "system", "content": (
            "You are a code reviewer. List suspected bugs in the file below. "
            "Reply ONLY JSON: {\"bugs\": [{\"line\": int, \"kind\": str, "
            "\"desc\": str}], \"verdict\": \"clean|buggy\"}. Be precise — do "
            "not invent issues that are not real bugs."),},
         {"role": "user", "content": f"# file: {filename}\n\n{src[:4000]}"}],
        role="analyst", max_tokens=600,
    )
    return out if isinstance(out, dict) else None


def _executor_fix(src: str, filename: str) -> str | None:
    """E4B fix tier — returns raw model output or None."""
    try:
        from omni_coworker.agents._llm import brain_chat
    except Exception:
        return None
    out = brain_chat(
        [{"role": "system", "content": (
            "Fix the bugs in this Python file with minimal changes. "
            "Output ONLY the corrected file content — no prose, no fences."),},
         {"role": "user", "content": f"# file: {filename}\n\n{src[:4000]}"}],
        role="executor", max_tokens=1200,
    )
    return out


def _smoke(path: Path) -> dict:
    """Compile + black-format the executor output; report pass/fail."""
    try:
        subprocess.run(
            [sys.executable, "-m", "black", "--quiet", str(path)],
            capture_output=True, timeout=60,
        )
        black_ok = True
    except Exception:
        black_ok = False
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        compiles = True
    except SyntaxError:
        compiles = False
    return {"black_formatted": black_ok, "compiles": compiles}


def _grade(planted: list[str], findings: dict | None) -> dict:
    """Match analyst findings to planted bugs — recall + hallucination count."""
    if not findings or not isinstance(findings.get("bugs"), list):
        return {"recall": None, "found": 0, "planted": len(planted),
                "hallucinated": None}
    descs = " ".join(str(b.get("desc", "")) + " " + str(b.get("kind", ""))
                     for b in findings["bugs"]).lower()
    hits = 0
    for p in planted:
        keys = [w for w in re.findall(r"[a-z_]{4,}", p.lower())][:3]
        if keys and any(k in descs for k in keys):
            hits += 1
    return {"recall": hits / len(planted) if planted else None,
            "found": hits, "planted": len(planted),
            "hallucinated": len(findings["bugs"]) - hits if planted
            else len(findings["bugs"])}


def _set_capture_env(run_id: str, turn: str, task: str = "coding_battery") -> None:
    cap = ROOT / "data" / "monitor" / "capture.env"
    try:
        cap.parent.mkdir(parents=True, exist_ok=True)
        cap.write_text(
            f"OMNI_ACT_STEP_EVERY=8\nOMNI_ACT_STEP_ON=1\n"
            f"OMNI_ACT_PROMPT_HIDDEN=0\nOMNI_ACT_VEC_KEEP=128\n"
            f"OMNI_ACT_RUN_ID={run_id}\nOMNI_ACT_TURN={turn}\nOMNI_ACT_TASK={task}\n",
            encoding="utf-8",
        )
    except Exception:
        pass


def _extract_python_code(raw: str) -> str:
    txt = re.sub(r"<\|thought\|>.*?<\|/thought\|>", "", raw, flags=re.DOTALL).strip()
    m = re.search(r"```(?:python|py)?\s*\n(.*?)```", txt, flags=re.DOTALL)
    if m:
        return m.group(1).strip()
    return re.sub(r"^```[a-z]*\n|\n```$", "", txt).strip()


def main() -> int:
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    OUT.mkdir(exist_ok=True)
    con = sqlite3.connect(str(DB))
    con.execute(
        """CREATE TABLE IF NOT EXISTS coding_battery (
            ts TEXT, case_id TEXT, cls TEXT, mechanical_json TEXT,
            analyst_json TEXT, recall REAL, hallucinated INTEGER,
            fix_compiles INTEGER, fix_black INTEGER, verdict TEXT)"""
    )
    only = {a for a in sys.argv[1:] if a.startswith("c")}
    selected = [c for c in cases if not only or c["id"] in only]

    # Pass 1: Mechanical + Analyst (12B :8098) across all cases to avoid per-case VRAM swap thrashing
    pass1 = {}
    for case in selected:
        src_path = VICTIM / case["file"]
        src = src_path.read_text(encoding="utf-8")
        mech = _mechanical(src_path)
        _set_capture_env(f"coding_{case['id']}", "analyst", "coding_battery")
        analyst = _analyst(src, case["file"])
        grade = _grade(case["planted"], analyst)
        pass1[case["id"]] = (src, mech, analyst, grade)

    # Pass 2: Executor (E4B :8099) fix + smoke + ledger commit
    n_live = 0
    for case in selected:
        src, mech, analyst, grade = pass1[case["id"]]
        _set_capture_env(f"coding_{case['id']}", "executor", "coding_battery")
        fix_raw = _executor_fix(src, case["file"])
        fix = {"black_formatted": False, "compiles": False}
        if fix_raw:
            code = _extract_python_code(fix_raw)
            fix_path = OUT / f"{case['id']}_{case['file']}"
            fix_path.write_text(code, encoding="utf-8")
            fix = _smoke(fix_path)
            n_live += 1
        verdict = "done"
        if analyst is None:
            verdict = "no_analyst"
        row = (
            time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            case["id"], case["class"], json.dumps(mech),
            json.dumps(analyst)[:2000], grade["recall"],
            grade["hallucinated"], int(fix["compiles"]),
            int(fix["black_formatted"]), verdict,
        )
        con.execute(
            "INSERT INTO coding_battery VALUES (?,?,?,?,?,?,?,?,?,?)", row
        )
        con.commit()
        print(f"{case['id']}: mech={len(mech['ruff'])}ruff "
              f"syntax_ok={mech['compiles']} black={mech['black_clean']} | "
              f"analyst={'Y' if analyst else 'N'} recall={grade['recall']} "
              f"halluc={grade['hallucinated']} | fix: compiles={fix['compiles']} "
              f"black={fix['black_formatted']}")
    con.close()
    print(f"ledger: {DB} | live fixes: {n_live}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
