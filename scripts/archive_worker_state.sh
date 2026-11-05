#!/usr/bin/env bash
# ============================================================================
# archive_worker_state — preservação automática para retomada de VM
#
# English: Tars the worker's runtime artifacts (state, ledgers, logs,
# code index, battery sqlites) into the mounted Drive with retention,
# so a recycled VM can resume. Before taring, every *.sqlite/*.db under
# data/, scripts/ and state/ gets PRAGMA wal_checkpoint(TRUNCATE) so no
# committed rows stay trapped in -wal/-shm sidecars; the sidecars are
# excluded from the tarball. Secret-ish patterns are excluded too.
# Designed to run as a loop daemon (default 1h) or one-shot.
#
# pt-BR: Empacota os artefatos de runtime do worker (estado, ledgers,
# logs, índice, sqlites de baterias) no Drive montado com retenção,
# para retomar após a VM reciclar. Antes do tar, todo *.sqlite/*.db em
# data/, scripts/ e state/ recebe PRAGMA wal_checkpoint(TRUNCATE) para
# que nenhuma linha commitada fique retida em -wal/-shm; os sidecars
# são excluídos do tarball. Padrões de segredo também são excluídos.
# Roda como loop daemon (default 1h) ou one-shot.
#
# Usage / Uso:
#   bash scripts/archive_worker_state.sh            # one-shot
#   bash scripts/archive_worker_state.sh --loop 3600   # loop daemon
#   bash scripts/archive_worker_state.sh --verify <archive.tar.gz>  # integrity
# Env: DRIVE_BACKUP_DIR (default /content/drive/MyDrive/omni_worker_backups)
#      BACKUP_KEEP=5   REPO=auto
#
# Provenance (RNFCI pack pattern, OW-SYN-001 D2): each archive ships a
# <name>.manifest.json (entries, boundary, prev_archive lineage, size) and
# <name>.sha256 (double hash: tarball + manifest) — restorable-verifiable.
# ============================================================================
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DRIVE_BACKUP_DIR="${DRIVE_BACKUP_DIR:-/content/drive/MyDrive/omni_worker_backups}"
KEEP="${BACKUP_KEEP:-5}"

write_provenance() {
  local tarball="$1" ts="$2" outdir="${3:-$DRIVE_BACKUP_DIR}" prev
  prev="$(ls -1t "$outdir"/omni_worker_*.tar.gz 2>/dev/null \
          | grep -v "/$(basename "$tarball")$" | head -1 | xargs -r basename)"
  python3 - "$tarball" "$ts" "$prev" "$outdir" <<'PY'
import hashlib, json, subprocess, sys, tarfile, os
tarball, ts, prev, outdir = sys.argv[1:5]
h = hashlib.sha256()
with open(tarball, "rb") as f:
    for chunk in iter(lambda: f.read(1 << 20), b""):
        h.update(chunk)
entries, top = 0, set()
with tarfile.open(tarball, "r:gz") as t:
    for m in t:
        entries += 1
        top.add(m.name.split("/", 1)[0])
mani = {
    "archive": os.path.basename(tarball),
    "created_utc": ts,
    "size_bytes": os.path.getsize(tarball),
    "entry_count": entries,
    "top_level": sorted(top),
    "sha256": h.hexdigest(),
    "prev_archive": prev or None,
    "boundary": {
        "public_safe": True,
        "secrets_excluded": ["*.env", "*token*", "*secret*", "*.pem",
                             "*.key", "*credential*", "*id_rsa*",
                             "*id_ed25519*"],
        "note": "runtime artifacts only; source history lives in git",
    },
}
mpath = os.path.join(outdir, os.path.basename(tarball).replace(
    ".tar.gz", ".manifest.json"))
with open(mpath, "w") as f:
    json.dump(mani, f, indent=2)
mh = hashlib.sha256(open(mpath, "rb").read()).hexdigest()
with open(mpath.replace(".manifest.json", ".sha256"), "w") as f:
    f.write(f"{h.hexdigest()}  {os.path.basename(tarball)}\n")
    f.write(f"{mh}  {os.path.basename(mpath)}\n")
PY
}

verify_archive() {
  local tarball="$1" base want got mpath
  base="$(basename "$tarball")"
  mpath="$(dirname "$tarball")/${base%.tar.gz}.manifest.json"
  want="$(awk 'NR==1{print $1}' "$(dirname "$tarball")/${base%.tar.gz}.sha256" 2>/dev/null)"
  [ -n "$want" ] || { echo "[verify] sem sha256 sidecar para $base"; return 1; }
  got="$(sha256sum "$tarball" | awk '{print $1}')"
  if [ "$got" = "$want" ] && [ -s "$mpath" ]; then
    echo "[verify] OK $base (manifest + sha256)"; return 0
  fi
  echo "[verify] FALHA $base"; return 1
}

checkpoint_sqlite() {
  # Consolidate WAL into the main db file so the tarball carries 100%
  # of committed state (nothing left in -wal/-shm sidecars). Best-effort:
  # a busy db logs a warning but never aborts the archive.
  python3 - "$REPO" <<'PY'
import os, sqlite3, sys
repo = sys.argv[1]
found = []
for root in ("data", "scripts", "state"):
    base = os.path.join(repo, root)
    if not os.path.isdir(base):
        continue
    for dirpath, _, files in os.walk(base):
        for f in files:
            if f.endswith((".sqlite", ".db")):
                found.append(os.path.join(dirpath, f))
for p in sorted(set(found)):
    rel = os.path.relpath(p, repo)
    try:
        con = sqlite3.connect(p, timeout=15)
        con.execute("PRAGMA busy_timeout=15000")
        busy, log, ckpt = con.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
        con.close()
        wal = p + "-wal"
        wal_sz = os.path.getsize(wal) if os.path.exists(wal) else 0
        tag = "ok" if busy == 0 else "BUSY(parcial)"
        print(f"[checkpoint] {tag} frames={ckpt}/{log} wal_restante={wal_sz} {rel}")
    except Exception as e:
        print(f"[checkpoint] FALHA {rel}: {e}")
PY
}

archive_once() {
  local target_dir="$DRIVE_BACKUP_DIR"
  if [ ! -d "$target_dir" ] && ! mkdir -p "$target_dir" 2>/dev/null; then
    target_dir="$REPO/data/backups"
    mkdir -p "$target_dir" 2>/dev/null || {
      echo "[archive] destino indisponível ($target_dir) — skip"; return 1; }
    echo "[archive] fallback para diretório local: $target_dir"
  fi
  local ts name
  ts="$(date -u +%Y%m%dT%H%M%SZ)"
  name="omni_worker_${ts}.tar.gz"
  checkpoint_sqlite
  # runtime artifacts the git history does NOT cover; secrets + sqlite
  # transient sidecars excluded (state já consolidado via checkpoint)
  local members=(data logs omni_code_index runtime_config)
  [ -d "$REPO/state" ] && members+=(state)
  local db
  for db in "$REPO"/scripts/*/*.sqlite "$REPO"/scripts/*/*.db; do
    [ -e "$db" ] && members+=("${db#"$REPO"/}")
  done
  tar -czf "$target_dir/.$name.tmp" \
    --exclude='*.env' --exclude='*token*' --exclude='*secret*' \
    --exclude='*.pem' --exclude='*.key' --exclude='*credential*' \
    --exclude='*id_rsa*' --exclude='*id_ed25519*' \
    --exclude='*-wal' --exclude='*-shm' --exclude='*-journal' \
    -C "$REPO" \
    --ignore-failed-read \
    "${members[@]}" \
    2>/dev/null
  if [ -s "$target_dir/.$name.tmp" ]; then
    mv "$target_dir/.$name.tmp" "$target_dir/$name"
    write_provenance "$target_dir/$name" "$ts" "$target_dir"
    echo "[archive] $name ($(du -h "$target_dir/$name" | cut -f1)) +manifest +sha256"
    ls -1t "$target_dir"/omni_worker_*.tar.gz | tail -n +$((KEEP+1)) | while read -r old; do
      rm -f "$old" "${old%.tar.gz}.manifest.json" "${old%.tar.gz}.sha256"
    done
    return 0
  fi
  rm -f "$target_dir/.$name.tmp"
  echo "[archive] tar vazio — nada a preservar"; return 1
}

case "${1:-}" in
  --loop)
    iv="${2:-3600}"
    echo "[archive] loop ${iv}s → $DRIVE_BACKUP_DIR (keep $KEEP)"
    while true; do archive_once; sleep "$iv"; done ;;
  --verify)
    verify_archive "${2:?uso: --verify <archive.tar.gz>}" ;;
  *) archive_once ;;
esac
