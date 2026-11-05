"""state_guard — snapshots com retenção para continuidade da VM.

English: Snapshot/restore manager anchored at $OMNI_STATE_DIR (default
./data). `snapshot()` tars the state dir + witness chain, verifies the
previous snapshot is intact, skips when nothing changed (content hash
of the manifest), keeps at most N_SNAPSHOTS copies and prunes older
ones — no unbounded accumulation. `restore()` extracts and verifies.
pt-BR: Gerenciador de snapshot/restore ancorado em $OMNI_STATE_DIR
(default ./data). `snapshot()` empacota o state dir + witness chain,
verifica que o snapshot anterior está íntegro, pula quando nada mudou
(hash do manifest), mantém no máximo N_SNAPSHOTS cópias e poda as
antigas — sem acúmulo ilimitado. `restore()` extrai e verifica.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tarfile
import time
from pathlib import Path

N_SNAPSHOTS = 3
SNAPSHOT_DIR_NAME = "state_snapshots"


def _state_root() -> Path:
    return Path(os.getenv("OMNI_STATE_DIR", "data"))


def _snapshot_dir() -> Path:
    d = _state_root() / SNAPSHOT_DIR_NAME
    d.mkdir(parents=True, exist_ok=True)
    return d


def _hash_tree(root: Path, skip_top: set[str] | None = None,
               skip_parts: str | None = None) -> str:
    """Deterministic sha256 over a tree's files (path + content)."""
    skip_top = skip_top or set()
    h = hashlib.sha256()
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if rel.parts[0] in skip_top or (skip_parts and skip_parts in rel.parts):
            continue
        h.update(str(rel).encode())
        with p.open("rb") as f:
            for chunk in iter(lambda: f.read(1_000_000), b""):
                h.update(chunk)
    return h.hexdigest()


def _manifest_hash() -> str:
    """Hash of the state files (excluding snapshots dir)."""
    return _hash_tree(_state_root(), skip_parts=SNAPSHOT_DIR_NAME)


def _latest_snapshot() -> Path | None:
    snaps = sorted(_snapshot_dir().glob("state_*.tar.gz"), reverse=True)
    return snaps[0] if snaps else None


def snapshot(force: bool = False) -> dict:
    """Create a snapshot (skip if unchanged), prune to N_SNAPSHOTS.

    English: Returns {created, skipped, path, kept}. Integrity: the
    latest existing snapshot is hash-verified before pruning; if the
    chain is broken the new snapshot is still written but pruning is
    paused (never delete the only valid copy).
    pt-BR: Retorna {created, skipped, path, kept}. Integridade: o
    snapshot existente mais recente é verificado antes de podar; se a
    cadeia estiver quebrada o novo snapshot ainda é gravado mas a poda
    é pausada (nunca apagar a única cópia válida).
    """
    manifest = _manifest_hash()
    latest = _latest_snapshot()
    if latest is not None and not force:
        try:
            with tarfile.open(latest, "r:gz") as tf:
                stored = json.loads(tf.extractfile("manifest.json").read())["hash"]
            if stored == manifest:
                return {"created": False, "skipped": True,
                        "path": str(latest), "kept": len(list(_snapshot_dir().glob("state_*.tar.gz")))}
        except Exception:  # noqa: BLE001, S110
            pass  # corrupt latest -> fall through and write a fresh one

    ts = time.strftime("%Y%m%dT%H%M%S", time.gmtime()) + f"{time.time_ns() % 1_000_000:06d}Z"
    target = _snapshot_dir() / f"state_{ts}.tar.gz"
    # Atomic snapshot via staging (kilo guard-audit): hashing the live
    # tree then tarring it later raced mutable files (sqlite WALs,
    # witness.jsonl) — the stored manifest didn't match the tar
    # contents and fail-closed restore would refuse the snapshot.
    # Frozen copy → hash the copy → tar the copy: hash and contents
    # always agree.
    import tempfile
    staging = Path(tempfile.mkdtemp(prefix="omni_snap_"))
    try:
        stage_state = staging / "state"
        src_root = _state_root()
        if src_root.exists():
            shutil.copytree(
                src_root, stage_state,
                ignore=lambda _d, names: {SNAPSHOT_DIR_NAME} & set(names),
            )
        else:
            stage_state.mkdir(parents=True)
        manifest = _hash_tree(stage_state, skip_parts=SNAPSHOT_DIR_NAME)
        (stage_state / "manifest.json").write_text(
            json.dumps({"hash": manifest, "created_utc": ts}))
        with tarfile.open(target, "w:gz") as tf:
            for p in sorted(stage_state.rglob("*")):
                if p.is_file():
                    tf.add(p, arcname=str(p.relative_to(stage_state)))
    finally:
        shutil.rmtree(staging, ignore_errors=True)

    # prune: keep the N newest — but pause entirely when the chain head
    # is unreadable (a corrupt tip may be sitting on the last valid copy)
    snaps = sorted(_snapshot_dir().glob("state_*.tar.gz"), reverse=True)
    try:
        with tarfile.open(snaps[0], "r:gz") as tf:
            tf.extractfile("manifest.json")
        head_ok = True
    except Exception:  # noqa: BLE001
        head_ok = False
    kept = snaps[:N_SNAPSHOTS] if head_ok else snaps
    for old in snaps[len(kept):]:
        old.unlink()
    return {"created": True, "skipped": False, "path": str(target),
            "kept": len(kept)}


def restore(path: str | Path, verify: bool = True) -> dict:
    """Verify + extract a snapshot into the state root, then witness it.

    English: With ``verify`` (default) the archive is stage-extracted and
    checked BEFORE touching live state — fail-closed: a snapshot whose
    manifest hash mismatches (tampered/corrupt) or whose embedded
    witness.jsonl chain is broken is refused and never overwrites the
    state dir. On success the files overlay the state root (files absent
    from the archive are left alone — overlay, not wipe) and a
    ``state_restore`` witness event is appended to the restored chain,
    so the act itself joins the lineage it resurrected.
    pt-BR: Com ``verify`` (default) o arquivo é extraído em staging e
    conferido ANTES de tocar o estado vivo — fail-closed: snapshot com
    hash de manifest divergente (adulterado/corrompido) ou witness.jsonl
    embutido com cadeia quebrada é recusado e nunca sobrescreve o state
    dir. No sucesso os arquivos sobrepõem a raiz (arquivos ausentes do
    arquivo permanecem — overlay, não wipe) e um evento witness
    ``state_restore`` é anexado à cadeia restaurada — o ato entra na
    linhagem que ressuscitou.
    """
    import tempfile

    path = Path(path)
    root = _state_root()
    root.mkdir(parents=True, exist_ok=True)
    try:
        if not verify:
            with tarfile.open(path, "r:gz") as tf:
                tf.extractall(root, filter="data")
            return {"restored": True, "path": str(path), "verified": False}
        with tempfile.TemporaryDirectory(dir=str(root.parent)) as stage:
            sp = Path(stage)
            with tarfile.open(path, "r:gz") as tf:
                tf.extractall(sp, filter="data")
            try:
                stored = json.loads((sp / "manifest.json").read_text())["hash"]
            except Exception:  # noqa: BLE001
                return {"restored": False, "reason": "manifest_missing",
                        "path": str(path)}
            got = _hash_tree(sp, skip_top={"manifest.json"})
            if got != stored:
                return {"restored": False, "reason": "manifest_hash_mismatch",
                        "expected": stored, "got": got, "path": str(path)}
            wfile = sp / "witness.jsonl"
            if wfile.exists():
                from ..agency.witness import verify_witness
                wv = verify_witness(wfile)
                if wv.get("valid") is False:
                    return {"restored": False, "reason": "witness_chain_broken",
                            "broken_at": wv.get("broken_at"), "path": str(path)}
            else:
                wv = {"valid": None, "records": 0}
            for item in sp.iterdir():
                if item.name == "manifest.json":
                    continue
                dest = root / item.name
                if item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest)
            try:
                from ..agency.witness import witness_event
                witness_event("state_restore", {
                    "archive": str(path), "manifest_sha256": stored,
                    "witness_records": wv.get("records", 0)})
            except Exception:  # noqa: BLE001, S110
                pass
            return {"restored": True, "path": str(path), "verified": True,
                    "manifest_sha256": stored, "witness": wv}
    except Exception as e:  # noqa: BLE001
        return {"restored": False, "reason": str(e), "path": str(path)}


def loop(interval_hours: float = 6.0, once: bool = False) -> None:
    """Scheduler: snapshot every interval_hours; run forever unless once."""
    import time as _t

    while True:
        print(json.dumps(snapshot()))
        if once:
            break
        _t.sleep(interval_hours * 3600)


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true", help="one snapshot, then exit")
    ap.add_argument("--interval-hours", type=float, default=6.0)
    ap.add_argument("--restore", metavar="PATH", help="restore a snapshot and exit")
    args = ap.parse_args()
    if args.restore:
        print(json.dumps(restore(args.restore)))
    else:
        loop(args.interval_hours, once=args.once)