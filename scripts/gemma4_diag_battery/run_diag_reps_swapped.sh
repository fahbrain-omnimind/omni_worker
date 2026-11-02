#!/usr/bin/env bash
# ============================================================================
# diag battery with peer-swap — N reps per task per brain, full budget.
#
# English: The L4 can't hold both nf4 brains + 1800-token activation
# capture (doc: 8 MiB free → OOM on the 12B). So we run each role with
# the peer EVICTED via /erika/unload|reload (real endpoints on the
# ported erika_torch_server): analyst reps → swap → executor reps →
# restore dual residency.
#
# pt-BR: A L4 não comporta os dois brains nf4 + captura de ativações de
# 1800 tokens (doc: 8 MiB livres → OOM no 12B). Rodamos cada role com o
# peer DESPEJADO via /erika/unload|reload (endpoints reais do
# erika_torch_server portado): reps do analyst → swap → reps do
# executor → restaura residência dupla.
#
# Usage / Uso:
#   bash scripts/gemma4_diag_battery/run_diag_reps_swapped.sh [REPS]
# Env: API_PORT=8081 ANALYST_PORT=8098 EXECUTOR_PORT=8099 REPS=5
#      VENV_PYTHON=/content/omni_node/.venv/bin/python
# ============================================================================
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV_PYTHON="${VENV_PYTHON:-/content/omni_node/.venv/bin/python}"
API_PORT="${API_PORT:-8081}"
ANALYST_PORT="${ANALYST_PORT:-8098}"
EXECUTOR_PORT="${EXECUTOR_PORT:-8099}"
REPS="${1:-${REPS:-5}}"
export PYTHONPATH="/content/omni_node:/content/omni_node/src:$REPO/src"

post() { curl -s -m "${3:-300}" -X POST "http://127.0.0.1:$1$2"; }
healthy() { curl -s -m 3 "http://127.0.0.1:$1/health" | grep -q '"model_loaded":true'; }

echo "== diag battery — $REPS reps × 4 tasks × 2 roles (peer-swap)"

echo "-- unload executor :$EXECUTOR_PORT"
post "$EXECUTOR_PORT" /erika/unload; echo
"$VENV_PYTHON" "$REPO/scripts/gemma4_diag_battery/run_diag_battery.py" analyst --reps "$REPS" || {
  echo "!! analyst run falhou — restaurando"; }

echo "-- reload executor + unload analyst"
post "$EXECUTOR_PORT" /erika/reload; echo
post "$ANALYST_PORT" /erika/unload; echo
"$VENV_PYTHON" "$REPO/scripts/gemma4_diag_battery/run_diag_battery.py" executor --reps "$REPS" || {
  echo "!! executor run falhou — restaurando"; }

echo "-- reload analyst (dual residency restore)"
post "$ANALYST_PORT" /erika/reload; echo
sleep 5
for p in "$ANALYST_PORT" "$EXECUTOR_PORT"; do
  healthy "$p" && echo ":$p model_loaded OK" || echo ":$p NÃO saudável — verificar"
done
echo "== done — ledger: $REPO/scripts/gemma4_diag_battery/diag_battery.sqlite"
