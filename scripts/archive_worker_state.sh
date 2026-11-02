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
# Env: DRIVE_BACKUP_DIR (default /content/drive/MyDrive/omni_worker_backups)
#      BACKUP_KEEP=5   REPO=auto
# ============================================================================
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DRIVE_BACKUP_DIR="${DRIVE_BACKUP_DIR:-/content/drive/MyDrive/omni_worker_backups}"
KEEP="${BACKUP_KEEP:-5}"

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
    echo "[archive] $name ($(du -h "$DRIVE_BACKUP_DIR/$name" | cut -f1))"
    ls -1t "$DRIVE_BACKUP_DIR"/omni_worker_*.tar.gz | tail -n +$((KEEP+1)) | xargs -r rm -f
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
  *) archive_once ;;
esac
