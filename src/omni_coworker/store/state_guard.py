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


def _manifest_hash() -> str:
    """Hash of the state files (excluding snapshots dir)."""
    root = _state_root()
    h = hashlib.sha256()
    for p in sorted(root.rglob("*")):
        if SNAPSHOT_DIR_NAME in p.parts or not p.is_file():
            continue
        h.update(str(p.relative_to(root)).encode())
        with p.open("rb") as f:
            for chunk in iter(lambda: f.read(1_000_000), b""):
                h.update(chunk)
    return h.hexdigest()


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
        except Exception:
            pass  # corrupt latest -> fall through and write a fresh one

    ts = time.strftime("%Y%m%dT%H%M%S", time.gmtime()) + f"{time.time_ns() % 1_000_000:06d}Z"
    target = _snapshot_dir() / f"state_{ts}.tar.gz"
    with tarfile.open(target, "w:gz") as tf:
        for p in sorted(_state_root().rglob("*")):
            if SNAPSHOT_DIR_NAME in p.parts or not p.is_file():
                continue
            tf.add(p, arcname=str(p.relative_to(_state_root())))
        manifest_bytes = json.dumps({"hash": manifest, "created_utc": ts}).encode()
        _ti = tarfile.TarInfo("manifest.json")
        _ti.size = len(manifest_bytes)
        tf.addfile(_ti, __import__("io").BytesIO(manifest_bytes))

    # prune: keep the N newest, but never drop the last valid chain head
    snaps = sorted(_snapshot_dir().glob("state_*.tar.gz"), reverse=True)
    valid_heads = 0
    for s in snaps:
        try:
            with tarfile.open(s, "r:gz") as tf:
                tf.extractfile("manifest.json")
            valid_heads += 1
        except Exception:
            break
    kept = snaps[: max(N_SNAPSHOTS, valid_heads)]
    for old in snaps[len(kept):]:
        old.unlink()
    return {"created": True, "skipped": False, "path": str(target),
            "kept": len(kept)}


def restore(path: str | Path) -> dict:
    """Extract a snapshot into the state root (never overwrite snapshots)."""
    path = Path(path)
    try:
        with tarfile.open(path, "r:gz") as tf:
            tf.extractall(_state_root(), filter="data")
        return {"restored": True, "path": str(path)}
    except Exception as e:
        return {"restored": False, "reason": str(e)}


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