#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Re-score HF "blocks" records with the worker's own metrics.

English: Loads fabricioslv/gemma4-e4b-colab-l4-results
(generation_records), re-applies the worker degenerate heuristic
(same shape as run_diag_battery) + canonical _flags_resposta to each
stored visible_response / turn2_response, compares against the stored
degenerate_flag, and writes a rescore ledger + markdown report to
docs/results/. The HF sqlite is read-only — rescored rows go to
rescore_hf_blocks.sqlite next to this script.

pt-BR: Recalcula os registros "blocks" do dataset HF com as métricas
do worker: heurística degenerate (mesma forma do run_diag_battery) +
_flags_resposta canônica sobre cada visible_response/turn2_response,
compara com o degenerate_flag armazenado e grava ledger + relatório em
docs/results/. O sqlite HF é read-only — o rescore vai para
rescore_hf_blocks.sqlite local.

Usage:
    HF_E4B_SQLITE=/path/gemma4_e4b_l4_results.sqlite \
    PYTHONPATH=src python3 scripts/gemma4_diag_battery/rescore_hf_blocks.py
"""

from __future__ import annotations

import json
import os
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

HF_SQLITE = Path(os.getenv(
    "HF_E4B_SQLITE",
    "/tmp/kilo_runs/hf_e4b/gemma4_e4b_l4_results.sqlite"))
OUT_DB = HERE / "rescore_hf_blocks.sqlite"
REPORT = HERE.parents[1] / "docs" / "results" / "rescore_hf_blocks.md"

CANONICAL = Path(
    "/content/omnimind-kilombo-sovereign/scripts/benchmarks/"
    "embodied_v10_unified_battery.py"
)


def _load_canonical():
    import importlib.util
    spec = importlib.util.spec_from_file_location("v10_battery", CANONICAL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _degenerate(text: str) -> bool:
    """Same-shape heuristic as run_diag_battery / the HF runs."""
    lines = [ln.strip() for ln in (text or "").splitlines()
             if len(ln.strip()) > 12]
    if len(lines) >= 8 and len(set(lines)) <= len(lines) // 3:
        return True
    tail = (text or "")[-400:]
    return bool(re.search(r"(.)\1{30,}", tail))


def _uniq_words(text: str) -> float:
    toks = (text or "").split()
    return len(set(toks)) / max(len(toks), 1) if toks else 0.0


def _uniq_lines(text: str) -> float:
    lines = [ln for ln in (text or "").splitlines() if ln.strip()]
    return len(set(lines)) / max(len(lines), 1) if lines else 0.0


def _rep4(text: str) -> float:
    """Repeated-fraction of word 4-grams — catches the low-token-diversity
    verbose degeneration (deliberation leak) that the line-shape heuristic
    misses: HF flag ≈ token-level unique_ratio < ~0.3."""
    toks = (text or "").split()
    if len(toks) < 8:
        return 0.0
    grams = [tuple(toks[i:i + 4]) for i in range(len(toks) - 3)]
    return 1 - len(set(grams)) / len(grams)


def _degenerate_v2(text: str) -> bool:
    """Worker detector, second tier: line/char shape OR token-diversity
    collapse (word_ur < 0.5 with rep4 > 0.05 — calibrated so that clean
    observe records at ~0.65/0.002 stay clean and cognitivo degen at
    ~0.42/0.146 fires)."""
    if _degenerate(text):
        return True
    return _uniq_words(text) < 0.5 and _rep4(text) > 0.05


def main() -> int:
    if not HF_SQLITE.exists():
        print("HF sqlite not found:", HF_SQLITE)
        return 1
    mod = _load_canonical()
    flags_fn = mod._flags_resposta

    src = sqlite3.connect(f"file:{HF_SQLITE}?mode=ro", uri=True)
    rows = src.execute(
        """SELECT record_id, experiment, task_id, rep_idx,
                  degenerate_flag, unique_ratio, visible_response,
                  turn2_response, n_gates_interventions
           FROM generation_records ORDER BY record_id""").fetchall()

    con = sqlite3.connect(str(OUT_DB))
    con.execute("DROP TABLE IF EXISTS rescore")
    con.execute(
        """CREATE TABLE rescore (
            record_id INTEGER PRIMARY KEY, experiment TEXT, task_id TEXT,
            rep_idx INTEGER, stored_degen INTEGER, worker_degen INTEGER,
            worker_degen2 INTEGER, agree INTEGER, agree2 INTEGER,
            stored_ur REAL, worker_ur_words REAL,
            worker_ur_lines REAL, rep4 REAL, flags_json TEXT, which TEXT,
            gates_interventions INTEGER)"""
    )

    stats = {}
    discord = []
    for (rid, exp, task, rep, stored_degen, stored_ur, vis, turn2,
         gates) in rows:
        for which, text in (("visible", vis), ("turn2", turn2)):
            if not text:
                continue
            w_degen = int(_degenerate(text))
            w_degen2 = int(_degenerate_v2(text))
            flags = flags_fn(text)
            uw, ul, r4 = _uniq_words(text), _uniq_lines(text), _rep4(text)
            s_degen = int(stored_degen or 0) if which == "visible" else -1
            agree = None if s_degen < 0 else int(w_degen == s_degen)
            agree2 = None if s_degen < 0 else int(w_degen2 == s_degen)
            con.execute(
                "INSERT OR REPLACE INTO rescore VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (rid, exp, task, rep, s_degen if s_degen >= 0 else None,
                 w_degen, w_degen2, agree, agree2, stored_ur,
                 round(uw, 4), round(ul, 4), round(r4, 4),
                 json.dumps(flags), which, gates))
            if agree is not None:
                st = stats.setdefault(exp, {"n": 0, "agree": 0,
                                            "agree2": 0,
                                            "stored_degen": 0,
                                            "worker_degen": 0,
                                            "worker_degen2": 0,
                                            "loops": 0})
                st["n"] += 1
                st["agree"] += agree
                st["agree2"] += agree2
                st["stored_degen"] += s_degen
                st["worker_degen"] += w_degen
                st["worker_degen2"] += w_degen2
                st["loops"] += int(flags.get("loop_suspeito", False))
                if not agree2:
                    discord.append((rid, exp, task, s_degen, w_degen2, flags))
    con.commit()

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Re-score dos blocks HF E4B-L4 com métricas do worker",
        "",
        f"Fonte: `{HF_SQLITE}` (read-only) · gerado "
        f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} UTC",
        "",
        "Métricas worker: `_degenerate` (mesma forma do runner) + "
        "`_flags_resposta` canônico + uniq_words/uniq_lines "
        "(whitespace — o `unique_ratio` armazenado usa tokens BPE, "
        "não reproduzível exatamente; usado só como referência). "
        "`worker_degen2` adiciona o segundo tier calibrado "
        "(word_ur<0.5 ∧ rep4>0.05) para a classe dominante do HF: "
        "degeneração verbosa por vazamento de deliberação, que o "
        "heurístico de forma de linha não captura.",
        "",
        "## Concordância por experimento (visible_response)",
        "",
        "| experiment | n | agree shape | agree v2 | degen stored | degen v2 | loops |",
        "|---|---|---|---|---|---|---|",
    ]
    for exp in sorted(stats):
        st = stats[exp]
        lines.append(
            f"| {exp} | {st['n']} | {st['agree']}/{st['n']} "
            f"| {st['agree2']}/{st['n']} "
            f"| {st['stored_degen']} | {st['worker_degen2']} | {st['loops']} |")
    lines += ["", "## Discordâncias (stored ≠ worker)", ""]
    if discord:
        for rid, exp, task, sd, wd, flags in discord[:40]:
            lines.append(
                f"- `#{rid}` {exp}/{task}: stored={sd} worker={wd} "
                f"flags={flags}")
    else:
        lines.append("(nenhuma)")
    REPORT.write_text("\n".join(lines), encoding="utf-8")

    print("=== re-score summary (visible_response) ===")
    for exp in sorted(stats):
        st = stats[exp]
        print(f"{exp}: shape={st['agree']}/{st['n']} v2={st['agree2']}/{st['n']} | degen "
              f"stored={st['stored_degen']} v2={st['worker_degen2']} "
              f"loops={st['loops']}")
    print(f"ledger: {OUT_DB}\nreport: {REPORT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
