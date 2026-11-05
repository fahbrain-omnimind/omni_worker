"""quality_triage — priors classification, gate, escalation."""

import json
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]
                     / "scripts" / "quality_triage"))
import triage


@pytest.fixture()
def priors_db(tmp_path):
    db = sqlite3.connect(tmp_path / "priors.sqlite")
    db.executescript("""
    CREATE TABLE rule_priors (rule TEXT PRIMARY KEY, total INTEGER,
        verdict TEXT, verdict_dist TEXT, confidence REAL,
        batch_suppressible INTEGER, rationale TEXT);
    INSERT INTO rule_priors VALUES
      ('S8707', 100, 'accepted_domestic', '{}', 1.0, 1, 'intencional'),
      ('S1244', 50, 'review_needed', '{}', 1.0, 0, 'revisar caso'),
      ('SWEAK', 40, 'accepted_domestic', '{}', 0.6, 1, 'fraco');
    """)
    db.commit()
    db.close()
    return tmp_path / "priors.sqlite"


def test_auto_verdict_suppressible(priors_db):
    p = triage.load_priors(priors_db)
    r = triage.classify({"rule": "S8707", "file": "src/x.py",
                         "severity": "MINOR"}, p)
    assert r["verdict"] == "accepted_domestic" and r["via"] == "prior"


def test_confident_but_not_suppressible_escalates(priors_db):
    p = triage.load_priors(priors_db)
    r = triage.classify({"rule": "S1244", "file": "src/x.py",
                         "severity": "MAJOR"}, p)
    assert r["verdict"] == "escalate"


def test_severity_gate_never_suppressed(priors_db):
    p = triage.load_priors(priors_db)
    r = triage.classify({"rule": "S8707", "file": "src/x.py",
                         "severity": "BLOCKER"}, p)
    assert r["verdict"] == "review_needed" and r["via"] == "gate"
    # mas em código vendored, o gate cede ao prior
    r2 = triage.classify({"rule": "S8707", "file": "vendor/x.py",
                          "severity": "BLOCKER"}, p)
    assert r2["verdict"] == "accepted_domestic"


def test_weak_confidence_escalates(priors_db):
    p = triage.load_priors(priors_db)
    r = triage.classify({"rule": "SWEAK", "file": "src/x.py",
                         "severity": "MINOR"}, p)
    assert r["verdict"] == "escalate" and r["confidence"] == 0.6


def test_unknown_rule_escalates(priors_db):
    r = triage.classify({"rule": "NEW1", "file": "a.py",
                         "severity": "MINOR"}, triage.load_priors(priors_db))
    assert r["verdict"] == "escalate" and r["via"] == "unknown_rule"


def test_record_roundtrip(priors_db, tmp_path):
    fp = tmp_path / "f.jsonl"
    fp.write_text(json.dumps({"rule": "S8707", "file": "a.py", "line": 1,
                              "severity": "MINOR"}) + "\n")
    stats = triage.run(fp, priors_db, use_llm=False)
    assert stats["prior"] == 1
    row = sqlite3.connect(priors_db).execute(
        "select verdict from findings where rule='S8707'").fetchone()
    assert row[0] == "accepted_domestic"


def test_public_scope_flips_domestic(priors_db):
    # S8707 tem prior accepted_domestic suppressible; em escopo público
    # o mesmo achado vira future_public_risk com trilha explicativa.
    p = triage.load_priors(priors_db)
    r = triage.classify({"rule": "S8707", "file": "src/x.py",
                         "severity": "MINOR"}, p, scope="public")
    assert r["verdict"] == "future_public_risk"
    assert r["via"] == "public_scope"
    assert "prior doméstico: accepted_domestic" in r["rationale"]


def test_public_scope_no_flip_still_uses_prior(priors_db):
    # regra sem flip no mapeamento público segue o fluxo normal
    p = triage.load_priors(priors_db)
    r = triage.classify({"rule": "SWEAK", "file": "src/x.py",
                         "severity": "MINOR"}, p, scope="public")
    assert r["verdict"] == "escalate"  # conf 0.6 < threshold
