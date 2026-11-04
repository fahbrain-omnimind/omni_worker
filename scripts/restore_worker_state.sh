#!/usr/bin/env bash
# ============================================================================
# restore_worker_state — restaura o último backup do Drive após reciclagem
#
# English: Untars the newest omni_worker_*.tar.gz from the mounted Drive
# (data/, logs/, runtime ledgers, battery sqlites) back into the repo.
# Verify-first: checks the .sha256 manifest before extracting.
#
# pt-BR: Descompacta o omni_worker_*.tar.gz mais novo do Drive montado
# (data/, logs/, ledgers, sqlites de baterias) de volta ao repo.
# Verifica o .sha256 antes de extrair.
#
# Usage:
#   bash scripts/restore_worker_state.sh              # latest archive
#   bash scripts/restore_worker_state.sh <archive.tar.gz>
# Env: DRIVE_BACKUP_DIR (default /content/drive/MyDrive/omni_worker_backups)
# ============================================================================
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DRIVE_BACKUP_DIR="${DRIVE_BACKUP_DIR:-/content/drive/MyDrive/omni_worker_backups}"

ARCHIVE="${1:-$(ls -1t "$DRIVE_BACKUP_DIR"/omni_worker_*.tar.gz 2>/dev/null | head -1)}"
[ -n "$ARCHIVE" ] || { echo "[restore] nenhum omni_worker_*.tar.gz em $DRIVE_BACKUP_DIR"; exit 1; }
echo "[restore] archive: $ARCHIVE"

if [ -f "$ARCHIVE.sha256" ]; then
  want="$(awk '{print $1}' "$ARCHIVE.sha256" | head -1)"
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
