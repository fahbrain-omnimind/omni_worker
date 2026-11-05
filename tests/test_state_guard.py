"""Tests for store.state_guard (snapshot/retention/restore)."""

from __future__ import annotations

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
    kept = list(sg._snapshot_dir().glob("state_*.tar.gz"))
    assert len(kept) <= sg.N_SNAPSHOTS


def test_restore_roundtrip(tmp_path, monkeypatch):
    root = _fresh_root(tmp_path, monkeypatch)
    (root / "witness.jsonl").write_text("content-a\n")
    snap = sg.snapshot()
    (root / "witness.jsonl").write_text("content-b\n")
    out = sg.restore(snap["path"])
    assert out["restored"] is True
    assert out["verified"] is True
    assert out["manifest_sha256"]
    # "content-a" era linha não-JSON (legada): o evento state_restore é
    # anexado à cadeia restaurada, então o arquivo cresce em vez de ser
    # byte-idêntico ao original
    text = (root / "witness.jsonl").read_text()
    assert text.startswith("content-a\n")
    assert "state_restore" in text


def _retar_with_mutation(snapshot_path: str, mutate) -> Path:
    """Re-empacota um snapshot aplicando `mutate(staged_dir)` antes do tar."""
    import tarfile
    import tempfile

    sp = Path(tempfile.mkdtemp())
    with tarfile.open(snapshot_path, "r:gz") as tf:
        tf.extractall(sp, filter="data")
    mutate(sp)
    tampered = Path(snapshot_path).parent / "tampered.tar.gz"
    with tarfile.open(tampered, "w:gz") as tf:
        for p in sorted(sp.rglob("*")):
            if p.is_file():
                tf.add(p, arcname=str(p.relative_to(sp)))
    return tampered


def test_restore_refuses_tampered_content(tmp_path, monkeypatch):
    """Manifest hash divergente → fail-closed, estado vivo intacto."""
    root = _fresh_root(tmp_path, monkeypatch)
    snap = sg.snapshot()
    before = (root / "node.db").read_bytes()

    def _mutate(sp):
        (sp / "node.db").write_bytes(b"tampered" * 50)

    bad = _retar_with_mutation(snap["path"], _mutate)
    out = sg.restore(bad)
    assert out["restored"] is False
    assert out["reason"] == "manifest_hash_mismatch"
    assert (root / "node.db").read_bytes() == before  # nunca tocou o vivo


def test_restore_refuses_broken_witness(tmp_path, monkeypatch):
    """Witness embutido com cadeia quebrada → recusado (manifest honesto)."""
    import json as _json

    root = _fresh_root(tmp_path, monkeypatch)
    (root / "witness.jsonl").write_text(
        _json.dumps({"type": "x", "prev_hash": "", "hash": "bogus"}) + "\n")
    snap = sg.snapshot()  # manifest hash cobre o witness quebrado tal qual
    out = sg.restore(snap["path"])
    assert out["restored"] is False
    assert out["reason"] == "witness_chain_broken"


def test_restore_witness_valid_chain(tmp_path, monkeypatch):
    """Snapshot com witness válido → restore verificado + evento anexado."""
    root = _fresh_root(tmp_path, monkeypatch)
    from omni_coworker.agency.witness import verify_witness, witness_event
    witness_event("seed", {"n": 1})
    snap = sg.snapshot()
    witness_event("post", {"n": 2})
    out = sg.restore(snap["path"])
    assert out["restored"] is True and out["verified"] is True
    assert out["witness"]["valid"] is True
    res = verify_witness(root / "witness.jsonl")
    assert res["valid"] is True  # cadeia restaurada + state_restore coerente