"""Acceptance tests for corpus_integrity_app."""

import sqlite3
from pathlib import Path

import cli
import scanner

PHIL_TXT = Path(__file__).resolve().parents[3] / "data/corpus/philpapers_2026/txt"


def test_md5_and_duplicate_detection(tmp_path):
    a, b = tmp_path / "a.txt", tmp_path / "b.txt"
    a.write_text("identical", encoding="utf-8")
    b.write_text("identical", encoding="utf-8")
    dups = scanner.detect_duplicates([str(a), str(b)])
    assert len(dups) == 1 and dups[0][2] == scanner.compute_md5(str(a))


def test_manifest_anomaly_detection():
    f30 = PHIL_TXT / "30_Beckmann_manuscript_WorldModelingInTransformers.txt"
    res = scanner.verify_manifest_entry(
        str(f30), "Beckmann", "World Modeling in Transformers"
    )
    assert res["anomaly"] is True and res["author_match"] is False


def test_tabular_tail_and_epistemic_tags():
    sample = "[DADO] medido\n[PRX] proxy\n[DADO] 2\n10 20 30 40\n11 22 33 44\n"
    tags = scanner.count_epistemic_tags(sample)
    assert tags["[DADO]"] == 2 and tags["[PRX]"] == 1
    assert 0.2 <= scanner.tabular_tail_ratio(sample) <= 0.8


def test_sqlite_cli_persistence(tmp_path):
    db = tmp_path / "audit.sqlite"
    recs = [{"file": "30_Beckmann.txt", "anomaly": 1, "md5": "abc", "dado_count": 3}]
    assert cli.save_audit_sqlite(str(db), recs) == 1
    rows = (
        sqlite3.connect(str(db))
        .execute("SELECT file, anomaly FROM audit_records")
        .fetchall()
    )
    assert rows == [("30_Beckmann.txt", 1)]
