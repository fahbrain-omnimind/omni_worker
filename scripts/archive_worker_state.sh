#!/usr/bin/env bash
# ============================================================================
# archive_worker_state — preservação automática para retomada de VM
#
# English: Tars the worker's runtime artifacts (state, ledgers, logs,
# code index) into the mounted Drive with retention, so a recycled VM
# can resume. Secret-ish patterns are excluded before archiving.
# Designed to run as a loop daemon (default 1h) or one-shot.
#
# pt-BR: Empacota os artefatos de runtime do worker (estado, ledgers,
# logs, índice) no Drive montado com retenção, para retomar após a VM
# reciclar. Padrões de segredo são excluídos antes de empacotar.
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
  local tarball="$1" ts="$2" prev
  prev="$(ls -1t "$DRIVE_BACKUP_DIR"/omni_worker_*.tar.gz 2>/dev/null \
          | grep -v "/$(basename "$tarball")$" | head -1 | xargs -r basename)"
  python3 - "$tarball" "$ts" "$prev" "$DRIVE_BACKUP_DIR" <<'PY'
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

archive_once() {
  [ -d "$DRIVE_BACKUP_DIR" ] || mkdir -p "$DRIVE_BACKUP_DIR" || {
    echo "[archive] drive indisponível ($DRIVE_BACKUP_DIR) — skip"; return 1; }
  local ts name
  ts="$(date -u +%Y%m%dT%H%M%SZ)"
  name="omni_worker_${ts}.tar.gz"
  # runtime artifacts the git history does NOT cover; secrets excluded
  tar -czf "$DRIVE_BACKUP_DIR/.$name.tmp" \
    --exclude='*.env' --exclude='*token*' --exclude='*secret*' \
    --exclude='*.pem' --exclude='*.key' --exclude='*credential*' \
    --exclude='*id_rsa*' --exclude='*id_ed25519*' \
    -C "$REPO" \
    data logs omni_code_index \
    scripts/gemma4_diag_battery/diag_battery.sqlite \
    scripts/coding_battery/coding_battery.sqlite \
    scripts/supervisor_battery/supervisor_battery.sqlite \
    scripts/refactor_battery/refactor_battery.sqlite \
    2>/dev/null
  if [ -s "$DRIVE_BACKUP_DIR/.$name.tmp" ]; then
    mv "$DRIVE_BACKUP_DIR/.$name.tmp" "$DRIVE_BACKUP_DIR/$name"
    write_provenance "$DRIVE_BACKUP_DIR/$name" "$ts"
    echo "[archive] $name ($(du -h "$DRIVE_BACKUP_DIR/$name" | cut -f1)) +manifest +sha256"
    ls -1t "$DRIVE_BACKUP_DIR"/omni_worker_*.tar.gz | tail -n +$((KEEP+1)) | while read -r old; do
      rm -f "$old" "${old%.tar.gz}.manifest.json" "${old%.tar.gz}.sha256"
    done
    return 0
  fi
  rm -f "$DRIVE_BACKUP_DIR/.$name.tmp"
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
