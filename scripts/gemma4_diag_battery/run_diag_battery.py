#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gemma4_diag_battery — replicação diagnóstica mínima da esteira canônica.

English: minimal diagnostic replication of the canonical Psicodiagnóstico-V
executive battery (WCST/Stroop/N-back/IGT, v2 hardened prompts + scorers
loaded from omnimind-kilombo-sovereign). Runs each task once per live brain
(12B :8098 analyst, E4B :8099 executor) — enough to compare against the HF
E4B-L4 dataset (block1_cognitivo: 100% degenerate) and test the
quantization-inhibition hypothesis locally. Ledger → diag_battery.sqlite.
pt-BR: replicação diagnóstica mínima da esteira executiva canônica
(Psicodiagnóstico-V, prompts+scorers v2 carregados do soberano). Uma rep por
task por brain vivo — suficiente para comparar com o dataset HF E4B-L4
(cognitivo 100% degenerado) e testar localmente a hipótese
quantização→inibição. Ledger → sqlite.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sqlite3
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SRC = ROOT / "src"
for p in (str(SRC), str(ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

CANONICAL = Path(
    "/content/omnimind-kilombo-sovereign/scripts/benchmarks/"
    "embodied_v10_unified_battery.py"
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
    """Same-shape heuristic as the HF runs: token-loop degeneration."""
    lines = [l.strip() for l in (text or "").splitlines() if len(l.strip()) > 12]
    if len(lines) >= 8 and len(set(lines)) <= len(lines) // 3:
        return True
    tail = (text or "")[-400:]
    return bool(re.search(r"(.)\1{30,}", tail))


def main() -> int:
    mod = _load_canonical()
    roles = [a for a in sys.argv[1:] if a in ("analyst", "executor")] or [
        "analyst", "executor"
    ]
    try:
        from omni_coworker.agents._llm import brain_chat
    except Exception as e:
        print("brain backend unavailable:", e)
        return 1
    con = sqlite3.connect(str(DB))
    con.execute(
        """CREATE TABLE IF NOT EXISTS diag_battery (
            ts TEXT, model_role TEXT, task_id TEXT, score REAL,
            detail_json TEXT, flags_json TEXT, degenerate INTEGER,
            latency_s REAL, n_tokens INTEGER)"""
    )
    for role in roles:
        for task in _TASKS:
            prompt = _prompt(mod, task)
            t0 = time.time()
            resp = brain_chat(
                [{"role": "user", "content": prompt}],
                role=role, max_tokens=1800, temperature=0.7,
            )
            lat = time.time() - t0
            resp = resp or ""
            scorer = getattr(mod, _TASKS[task][1])
            detail = scorer(resp)
            flags = mod._flags_resposta(resp)
            con.execute(
                "INSERT INTO diag_battery VALUES (?,?,?,?,?,?,?,?,?)",
                (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), role,
                 task, detail.get("score"), json.dumps(detail)[:2000],
                 json.dumps(flags), int(_degenerate(resp)),
                 round(lat, 1), len(resp.split())),
            )
            con.commit()
            print(f"{role}/{task}: score={detail.get('score')} "
                  f"degen={_degenerate(resp)} {lat:.0f}s "
                  f"flags={flags}")
    con.close()
    print(f"ledger: {DB}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
