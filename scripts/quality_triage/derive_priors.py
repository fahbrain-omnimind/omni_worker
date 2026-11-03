#!/usr/bin/env python3
"""derive_priors — build the worker's code-quality priors base.

Reads a SonarCloud-style triage export (findings + rule_verdicts +
practices, e.g. the sovereign's code_quality_triage.sqlite) and emits a
compact `priors.sqlite`: per-rule verdict prior + dominant rationale +
suppressibility + confidence, plus the practices table.

Usage:
    python derive_priors.py --src /tmp/sonar_audit/code_quality_triage.sqlite \
        --out data/code_quality/priors.sqlite
"""

from __future__ import annotations

import argparse
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS rule_priors (
    rule TEXT PRIMARY KEY,
    total INTEGER,
    verdict TEXT,             -- dominant historical verdict
    verdict_dist TEXT,        -- json {verdict: count}
    confidence REAL,          -- dominant share of total
    batch_suppressible INTEGER,
    rationale TEXT            -- dominant rationale template
);
CREATE TABLE IF NOT EXISTS practices (
    domain TEXT, principle TEXT, detail TEXT, source TEXT
);
CREATE TABLE IF NOT EXISTS meta (
    source TEXT, findings INTEGER, derived_at TEXT
);
"""


def derive(src: Path, out: Path) -> dict:
    db = sqlite3.connect(f"file:{src}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    findings = db.execute(
        "SELECT rule, verdict, rationale FROM findings").fetchall()
    by_rule: dict[str, Counter] = defaultdict(Counter)
    rat: dict[str, Counter] = defaultdict(Counter)
    for r in findings:
        by_rule[r["rule"]][r["verdict"]] += 1
        if r["rationale"]:
            rat[r["rule"]][r["rationale"]] += 1
    suppress = {
        r["rule"]: bool(r["batch_suppressible"])
        for r in db.execute("SELECT rule, batch_suppressible FROM rule_verdicts")
    }
    practices = db.execute(
        "SELECT domain, principle, detail, source FROM practices").fetchall()
    db.close()

    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    w = sqlite3.connect(out)
    w.executescript(SCHEMA)
    import json as _json, datetime as _dt
    rows = []
    for rule, dist in by_rule.items():
        total = sum(dist.values())
        verdict, top = dist.most_common(1)[0]
        rationale = rat[rule].most_common(1)[0][0] if rat[rule] else ""
        rows.append((rule, total, verdict, _json.dumps(dict(dist)),
                     round(top / total, 4),
                     int(suppress.get(rule, False)), rationale))
    w.executemany("INSERT INTO rule_priors VALUES (?,?,?,?,?,?,?)", rows)
    w.executemany("INSERT INTO practices VALUES (?,?,?,?)",
                  [(p["domain"], p["principle"], p["detail"], p["source"])
                   for p in practices])
    w.execute("INSERT INTO meta VALUES (?,?,?)",
              (str(src), len(findings),
               _dt.datetime.now(_dt.timezone.utc).isoformat()))
    w.commit()
    w.close()
    return {"rules": len(rows), "findings": len(findings),
            "practices": len(practices)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, type=Path)
    ap.add_argument("--out", default=Path("data/code_quality/priors.sqlite"),
                    type=Path)
    a = ap.parse_args()
    print("priors:", derive(a.src, a.out))


if __name__ == "__main__":
    main()
