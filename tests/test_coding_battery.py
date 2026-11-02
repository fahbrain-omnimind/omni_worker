"""Hermetic tests for the coding battery mechanical tier + case registry."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MOD_PATH = HERE.parent / "scripts" / "coding_battery" / "run_coding_battery.py"


def _load():
    spec = importlib.util.spec_from_file_location("coding_battery", MOD_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_cases_registry_matches_victim_files():
    cases = json.loads((MOD_PATH.parent / "cases.json").read_text())
    for c in cases:
        assert (MOD_PATH.parent / "victim" / c["file"]).exists(), c["file"]
    classes = {c["class"] for c in cases}
    assert "control" in classes
    assert len(cases) >= 10


def test_mechanical_detects_syntax_error():
    mod = _load()
    out = mod._mechanical(MOD_PATH.parent / "victim" / "c01_syntax_missing_paren.py")
    assert out["compiles"] is False
    assert out["syntax_error"]


def test_mechanical_flags_lint_and_control_is_clean():
    mod = _load()
    dirty = mod._mechanical(MOD_PATH.parent / "victim" / "c02_missing_import.py")
    assert dirty["compiles"] is True
    assert dirty["ruff"]  # undefined-name findings expected
    clean = mod._mechanical(MOD_PATH.parent / "victim" / "c10_clean_control.py")
    assert clean["compiles"] is True
    assert clean["black_clean"] is True
    assert clean["ruff"] == []


def test_grade_recall_and_hallucination():
    mod = _load()
    planted = ["unclosed parenthesis (SyntaxError)"]
    findings = {"bugs": [{"line": 2, "kind": "syntax",
                          "desc": "unclosed parenthesis on return"},
                         {"line": 5, "kind": "style", "desc": "naming"}],
                "verdict": "buggy"}
    g = mod._grade(planted, findings)
    assert g["recall"] == 1.0
    assert g["hallucinated"] == 1
    clean_grade = mod._grade([], {"bugs": [{"desc": "x"}], "verdict": "buggy"})
    assert clean_grade["recall"] is None
