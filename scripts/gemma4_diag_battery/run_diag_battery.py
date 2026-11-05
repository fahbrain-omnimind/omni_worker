#!/usr/bin/env python3
"""gemma4_diag_battery — replicação diagnóstica mínima da esteira canônica.

English: minimal diagnostic replication of the canonical Psicodiagnóstico-V
executive battery (WCST/Stroop/N-back/IGT, v2 hardened prompts + scorers
loaded from omnimind-kilombo-sovereign). Runs each task once per live brain
(12B :8098 analyst, E4B :8099 executor, + 31B :8100 judge on hardware tier
xl) — enough to compare against the HF E4B-L4 dataset (block1_cognitivo:
100% degenerate) and test the quantization-inhibition hypothesis locally.
Ledger → diag_battery.sqlite.
pt-BR: replicação diagnóstica mínima da esteira executiva canônica
(Psicodiagnóstico-V, prompts+scorers v2 carregados do soberano). Uma rep por
task por brain vivo — suficiente para comparar com o dataset HF E4B-L4
(cognitivo 100% degenerado) e testar localmente a hipótese
quantização→inibição. Ledger → sqlite.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import sqlite3
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SRC = ROOT / "src"
for p in (str(SRC), str(ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

_LOCAL_CANONICAL = ROOT / "vendor" / "benchmarks" / "embodied_v10_unified_battery.py"
_SOVEREIGN_CANONICAL = Path(
    "/content/omnimind-kilombo-sovereign/scripts/benchmarks/"
    "embodied_v10_unified_battery.py"
)
CANONICAL = Path(
    os.getenv(
        "OMNI_V10_BATTERY_PATH",
        str(_LOCAL_CANONICAL if _LOCAL_CANONICAL.exists() else _SOVEREIGN_CANONICAL),
    )
)
DB = HERE / "diag_battery.sqlite"

# task_id -> (builder_name, scorer_name)
_TASKS = {
    "cognitivo_wcst": ("build_wcst_prompt_v2", "_score_wcst_v2"),
    "cognitivo_stroop": ("build_stroop_prompt_v2", "_score_stroop_v2"),
    "cognitivo_nback": (None, "_score_nback_v2"),  # const prompt
    "cognitivo_igt": (None, "_score_igt_v2"),
}


def _load_canonical():
    spec = importlib.util.spec_from_file_location("v10_battery", CANONICAL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _prompt(mod, task: str) -> str:
    builder, _ = _TASKS[task]
    if task == "cognitivo_nback":
        body = mod.NBACK_DIGIT_PROMPT_V2
    elif task == "cognitivo_igt":
        body = mod.IGT_PROMPT_V2 + "\n".join(
            f"TRIAL {t['trial']}: {t['contexto']}" for t in mod.IGT_TRIALS
        )
    else:
        body = getattr(mod, builder)()
    return body + mod.CONTRATO_SAIDA_COGNITIVO


def _degenerate(text: str) -> bool:
    """Token-loop degeneration — HF-shape tier + diversity collapse.

    English: line-repetition / char-run (same shape as the HF runs)
    OR token-diversity collapse: word unique-ratio < 0.5 with >5%
    repeated word 4-grams. The second tier is calibrated on the HF
    blocks dataset (rescore_hf_blocks.py): the stored flags mark
    token-level unique_ratio collapse (verbose deliberation leak) —
    49 records — that the shape tier alone misses entirely.
    pt-BR: repetição de linha / char-run (mesma forma do HF) OU
    colapso de diversidade de tokens — segundo tier calibrado no
    dataset HF de blocks (re-score reproduz 100% dos blocos
    cognitivos; shape sozinho pegava 0/49)."""
    lines = [ln.strip() for ln in (text or "").splitlines() if len(ln.strip()) > 12]
    if len(lines) >= 8 and len(set(lines)) <= len(lines) // 3:
        return True
    tail = (text or "")[-400:]
    if re.search(r"(.)\1{30,}", tail):
        return True
    toks = (text or "").split()
    if len(toks) >= 8:
        grams = [tuple(toks[i:i + 4]) for i in range(len(toks) - 3)]
        rep4 = 1 - len(set(grams)) / len(grams)
        if len(set(toks)) / len(toks) < 0.5 and rep4 > 0.05:
            return True
    return False


def _hw_tier() -> str:
    """Hardware tier detected by start_omni_worker.sh (env or profile file)."""
    t = os.getenv("OMNI_HW_TIER")
    if t:
        return t
    try:
        return json.loads(
            (ROOT / "runtime_config" / "hw_profile.json").read_text()
        ).get("tier", "std")
    except Exception:  # noqa: BLE001
        return "std"


def main() -> int:
    mod = _load_canonical()
    roles = [a for a in sys.argv[1:] if a in ("analyst", "executor", "judge")]
    if not roles:
        roles = ["analyst", "executor"] + (["judge"] if _hw_tier() == "xl" else [])
    reps = 1
    if "--reps" in sys.argv:
        i = sys.argv.index("--reps")
        reps = max(1, int(sys.argv[i + 1]))
    try:
        from omni_coworker.agents._llm import brain_chat
    except Exception as e:  # noqa: BLE001
        print("brain backend unavailable:", e)
        return 1
    con = sqlite3.connect(str(DB))
    con.execute(
        """CREATE TABLE IF NOT EXISTS diag_battery (
            ts TEXT, model_role TEXT, task_id TEXT, score REAL,
            detail_json TEXT, flags_json TEXT, degenerate INTEGER,
            latency_s REAL, n_tokens INTEGER)"""
    )
    # rep column for multi-repetition statistics; guarded migration keeps
    # old ledgers readable.
    cols = {r[1] for r in con.execute("PRAGMA table_info(diag_battery)")}
    if "rep" not in cols:
        con.execute("ALTER TABLE diag_battery ADD COLUMN rep INTEGER DEFAULT 0")
    # Full HF-parity budget needs the peer model unloaded on the L4
    # (activation capture: 62 layers x hidden per token on the 12B OOMs
    # when both brains are resident). Override per-role via OMNI_DIAG_MT_*
    # env when running both brains concurrently. On tier xl (A100+) the
    # constraint doesn't apply — budgets go up and 'judge' joins the run.
    _big = _hw_tier() == "xl"
    budget = {
        "analyst": int(os.getenv("OMNI_DIAG_MT_ANALYST", "3072" if _big else "1800")),
        "executor": int(os.getenv("OMNI_DIAG_MT_EXECUTOR", "3072" if _big else "1800")),
        "judge": int(os.getenv("OMNI_DIAG_MT_JUDGE", "4096")),
    }
    for rep in range(reps):
        for role in roles:
            for task in _TASKS:
                prompt = _prompt(mod, task)
                t0 = time.time()
                resp = brain_chat(
                    [{"role": "user", "content": prompt}],
                    role=role, max_tokens=budget.get(role, 1024), temperature=0.7,
                )
                lat = time.time() - t0
                resp = resp or ""
                scorer = getattr(mod, _TASKS[task][1])
                detail = scorer(resp)
                flags = mod._flags_resposta(resp)
                con.execute(
                    "INSERT INTO diag_battery VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), role,
                     task, detail.get("score"), json.dumps(detail)[:2000],
                     json.dumps(flags), int(_degenerate(resp)),
                     round(lat, 1), len(resp.split()), rep),
                )
                con.commit()
                print(f"rep{rep} {role}/{task}: score={detail.get('score')} "
                      f"degen={_degenerate(resp)} {lat:.0f}s "
                      f"flags={flags}")
    con.close()
    print(f"ledger: {DB}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
