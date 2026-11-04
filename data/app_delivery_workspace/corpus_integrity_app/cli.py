"""SQLite persistence and CLI runner for corpus_integrity_app."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import scanner

KNOWN_MANIFEST = {
    "30_Beckmann_manuscript_WorldModelingInTransformers.txt": (
        "Beckmann",
        "World Modeling in Transformers",
    ),
    "52_Shahmoradi_2026_IsStructuralRepresentation.txt": (
        "Shahmoradi",
        "Is structural representation analog representation",
    ),
    "001_anil-k-seth_2026_conscious-artificial-intelligence-and-biolog.txt": (
        "Seth",
        "Conscious artificial intelligence and biological naturalism",
    ),
}


def save_audit_sqlite(db_file: str, records: list[dict[str, Any]]) -> int:
    with sqlite3.connect(db_file) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS audit_records ("
            "file TEXT PRIMARY KEY, anomaly INTEGER, md5 TEXT, dado_count INTEGER)"
        )
        conn.executemany(
            "INSERT OR REPLACE INTO audit_records (file, anomaly, md5, dado_count) "
            "VALUES (?, ?, ?, ?)",
            [
                (
                    str(r.get("file", "")),
                    int(r.get("anomaly", 0)),
                    str(r.get("md5", "")),
                    int(r.get("dado_count", 0)),
                )
                for r in records
            ],
        )
    return len(records)


def run_corpus_scan(phil_dir: str, a6_book: str, db_file: str) -> dict[str, Any]:
    txt_files = sorted(str(p) for p in Path(phil_dir).glob("*.txt"))
    dups = scanner.detect_duplicates(txt_files)
    dup_set = {p for a, b, _ in dups for p in (a, b)}
    records: list[dict[str, Any]] = []
    for fpath in txt_files + ([a6_book] if Path(a6_book).exists() else []):
        p = Path(fpath)
        text = p.read_text(encoding="utf-8", errors="replace")
        tags = scanner.count_epistemic_tags(text)
        tab = scanner.tabular_tail_ratio(text)
        exp = KNOWN_MANIFEST.get(p.name)
        ver = scanner.verify_manifest_entry(fpath, *exp) if exp else {"anomaly": False}
        anom = int(ver["anomaly"] or (fpath in dup_set) or tab > 0.5)
        records.append(
            {
                "file": p.name,
                "anomaly": anom,
                "md5": scanner.compute_md5(fpath),
                "dado_count": tags["[DADO]"],
            }
        )
    save_audit_sqlite(db_file, records)
    return {
        "files_scanned": len(records),
        "duplicates_found": len(dups),
        "anomalies_flagged": sum(r["anomaly"] for r in records),
    }
