"""Tests for store.state_guard (snapshot/retention/restore)."""

from __future__ import annotations

import os
from pathlib import Path

from omni_coworker.store import state_guard as sg


def _fresh_root(tmp_path, monkeypatch):
    root = tmp_path / "data"
    root.mkdir()
    (root / "witness.jsonl").write_text("line1\n")
    (root / "node.db").write_bytes(b"x" * 100)
    monkeypatch.setenv("OMNI_STATE_DIR", str(root))
    return root


def test_snapshot_skips_when_unchanged(tmp_path, monkeypatch):
    _fresh_root(tmp_path, monkeypatch)
    a = sg.snapshot()
    assert a["created"] is True
    b = sg.snapshot()
    assert b["skipped"] is True
    assert b["path"] == a["path"]


def test_snapshot_force_creates_new(tmp_path, monkeypatch):
    _fresh_root(tmp_path, monkeypatch)
    a = sg.snapshot()
    b = sg.snapshot(force=True)
    assert b["created"] is True and b["path"] != a["path"]


def test_retention_prunes_to_three(tmp_path, monkeypatch):
    root = _fresh_root(tmp_path, monkeypatch)
    for i in range(5):
        (root / "witness.jsonl").write_text(f"line{i}\n")
        sg.snapshot()
    kept = list(sg._snapshot_dir().glob("state_*.tar.zst"))
    assert len(kept) <= sg.N_SNAPSHOTS


def test_restore_roundtrip(tmp_path, monkeypatch):
    root = _fresh_root(tmp_path, monkeypatch)
    (root / "witness.jsonl").write_text("content-a\n")
    snap = sg.snapshot()
    (root / "witness.jsonl").write_text("content-b\n")
    out = sg.restore(snap["path"])
    assert out["restored"] is True
    assert (root / "witness.jsonl").read_text() == "content-a\n"