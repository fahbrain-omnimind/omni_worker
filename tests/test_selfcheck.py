"""Hermetic tests for scripts/selfcheck/check_worker.py.

English: exercises the check functions on temp dirs only — no live
brains, no git worktree, no canonical repo required. The live-server
path is gated behind OMNI_SELFCHECK_LIVE=1.
pt-BR: exercita as funções de checagem só em dirs temporários — sem
brains vivos, sem worktree git, sem repo canônico. O caminho de servidor
vivo fica atrás de OMNI_SELFCHECK_LIVE=1.
"""

from __future__ import annotations

import importlib.util
import os
import sqlite3
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
MOD_PATH = HERE.parent / "scripts" / "selfcheck" / "check_worker.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_worker", MOD_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_compile_check_skips_victim_and_out(tmp_path):
    """Broken .py under */victim/ and */out/ must not be checked."""
    mod = _load()
    _write(tmp_path / "pkg" / "ok.py", "x = 1\n")
    _write(tmp_path / "scripts" / "b" / "victim" / "bad.py", "def broken(:\n")
    _write(tmp_path / "scripts" / "b" / "out" / "gen.py", "def also_broken(:\n")
    checked = [str(p) for p in mod.iter_checkable_py(tmp_path)]
    assert checked == [str(tmp_path / "pkg" / "ok.py")]
    assert mod.compile_failures(tmp_path) == []


def test_compile_check_flags_broken_file(tmp_path):
    """A broken .py outside the skipped dirs is reported by relpath."""
    mod = _load()
    _write(tmp_path / "pkg" / "ok.py", "x = 1\n")
    _write(tmp_path / "pkg" / "broken.py", "def broken(:\n")
    failures = mod.compile_failures(tmp_path)
    assert len(failures) == 1
    assert "broken.py" in failures[0][0]
    assert "line" in failures[0][1]


def test_ledger_scan_counts_rows_and_flags_unreadable(tmp_path):
    """Real sqlite → ok + row counts + score means; bogus file → not ok."""
    mod = _load()
    scripts = tmp_path / "scripts" / "fake"
    scripts.mkdir(parents=True)
    con = sqlite3.connect(scripts / "good.sqlite")
    con.execute("CREATE TABLE t (task_id TEXT, score REAL)")
    con.executemany(
        "INSERT INTO t VALUES (?, ?)",
        [("a", 1.0), ("b", 0.5), ("b", None)],
    )
    con.commit()
    con.close()
    (scripts / "bad.sqlite").write_bytes(b"not a sqlite file")

    reports = mod.scan_ledgers(tmp_path / "scripts")
    by_name = {r["path"].name: r for r in reports}
    assert by_name["good.sqlite"]["ok"] is True
    assert by_name["good.sqlite"]["tables"]["t"] == 3
    assert by_name["bad.sqlite"]["ok"] is False
    assert by_name["bad.sqlite"]["error"]

    summary = mod.ledger_summary(scripts / "good.sqlite")
    assert summary["t"]["rows"] == 3
    assert summary["t"]["tasks"] == 2
    assert summary["t"]["means"]["score"] == 0.75


@pytest.mark.skipif(
    os.getenv("OMNI_SELFCHECK_LIVE") != "1",
    reason="live brains required (set OMNI_SELFCHECK_LIVE=1)",
)
def test_live_health_reports_model_and_vram():
    mod = _load()
    health = mod.ping_health(mod.BRAIN_URLS["analyst"])
    assert health is not None
    assert "model" in health
