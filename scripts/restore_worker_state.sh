#!/usr/bin/env bash
# ============================================================================
# restore_worker_state — restaura o último backup do Drive após reciclagem
#
# English: Untars the newest omni_worker_*.tar.gz from the mounted Drive
# (data/, logs/, state/, runtime ledgers, battery sqlites) back into the
# repo. Verify-first: checks the .sha256 sidecar before extracting.
# Archives are already WAL-consolidated (archive_worker_state runs
# PRAGMA wal_checkpoint(TRUNCATE) before taring).
#
# pt-BR: Descompacta o omni_worker_*.tar.gz mais novo do Drive montado
# (data/, logs/, state/, ledgers, sqlites de baterias) de volta ao repo.
# Verifica o sidecar .sha256 antes de extrair. Os archives já vêm com
# WAL consolidado (archive_worker_state roda PRAGMA
# wal_checkpoint(TRUNCATE) antes de empacotar).
#
# Usage:
#   bash scripts/restore_worker_state.sh              # latest archive
#   bash scripts/restore_worker_state.sh <archive.tar.gz>
# Env: DRIVE_BACKUP_DIR (default /content/drive/MyDrive/omni_worker_backups)
# ============================================================================
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DRIVE_BACKUP_DIR="${DRIVE_BACKUP_DIR:-/content/drive/MyDrive/omni_worker_backups}"
BACKUP_DIR="${BACKUP_DIR:-$DRIVE_BACKUP_DIR}"
if [ ! -d "$BACKUP_DIR" ] && [ -d "$REPO/data/backups" ]; then
  BACKUP_DIR="$REPO/data/backups"
fi

ARCHIVE="${1:-$(ls -1t "$BACKUP_DIR"/omni_worker_*.tar.gz 2>/dev/null | head -1 || true)}"
[ -n "$ARCHIVE" ] || { echo "[restore] nenhum omni_worker_*.tar.gz em $BACKUP_DIR (operação com estado limpo/novo)"; exit 0; }
echo "[restore] archive: $ARCHIVE"

SHA_FILE="${ARCHIVE%.tar.gz}.sha256"
if [ -f "$SHA_FILE" ]; then
  want="$(awk 'NR==1{print $1}' "$SHA_FILE")"
  got="$(sha256sum "$ARCHIVE" | awk '{print $1}')"
  if [ "$want" != "$got" ]; then
    echo "[restore] SHA256 MISMATCH — abortando (integridade falhou)"
    exit 2
  fi
  echo "[restore] sha256 ok"
else
  echo "[restore] sem .sha256 — extraindo mesmo assim (cuidado)"
fi

tar xzf "$ARCHIVE" -C "$REPO"
echo "[restore] extraído em $REPO (data/, logs/, ledgers, sqlites)"
