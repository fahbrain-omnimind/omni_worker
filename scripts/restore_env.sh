#!/usr/bin/env bash
# ============================================================================
# restore_env.sh — bootstrap de variáveis fixas para VM recriada
#
# English: After a VM recreation (Colab/Kaggle), env vars and CI secrets are
# gone. This script re-fetches the FIXED variables from GitLab/GitHub
# (created manually or by Devin) and exports them for the current shell, so
# `start_omni_worker.sh` can pick them up.
#
# pt-BR: Após recriação da VM, env vars e segredos somem. Este script
# rebusca as variáveis FIXAS no GitLab/GitHub (mascaradas/protegidas) e as
# exporta para a shell atual, para o `start_omni_worker.sh` consumir.
#
# Usage:
#   source scripts/restore_env.sh --scope public
#   bash scripts/start_omni_worker.sh
#
# Requisitos (não commitados — segredo local):
#   GITLAB_TOKEN   (Personal Access Token c/ api scope)
#   GH_TOKEN       (opcional — só se quiser sync do GitHub)
# Preferência: GitLab primeiro (variáveis masked+protected legíveis via API).
# ============================================================================
set -uo pipefail

SCOPE="${1:-public}"
SCOPE="${SCOPE#--scope=}"; SCOPE="${SCOPE#--scope}"   # aceita --scope public, --scope=public ou public
SCOPE="${SCOPE:-public}"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[restore_env] escopo='${SCOPE}'"

# --- 1. GitLab: rebusca variáveis fixas via API ---------------------------
if [ -n "${GITLAB_TOKEN:-}" ] || [ -f /content/gitlab.txt ]; then
  GITLAB_TOKEN="${GITLAB_TOKEN:-$(python3 -c "print(open('/content/gitlab.txt').read().strip().split('=',1)[1].strip())" 2>/dev/null || true)}"
  if [ -n "$GITLAB_TOKEN" ]; then
    echo "[restore_env] GitLab: rebuscando variáveis fixas..."
    _vars="$(curl -s --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
      "https://gitlab.com/api/v4/projects/omni-group535144%2Fomni_worker/variables")"
    if [ -n "$_vars" ]; then
      echo "$_vars" | python3 - <<'PYEOF'
import json, os, sys
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)  # sem variáveis ou resposta não-JSON — fail-open
for v in data:
    k, val = v.get("key"), v.get("value")
    if k and val is not None and k != "HF_TOKEN":
        os.environ[k] = val  # só no processo filho; HF_TOKEN vai via CLI HF
        print(f"  -> {k} restaurado (masked={v.get('masked')})")
PYEOF
      if echo "$_vars" | grep -q '"HF_TOKEN"'; then
        export HF_TOKEN="$(echo "$_vars" | python3 -c "
import json,sys
d=json.load(sys.stdin)
print(next(v['value'] for v in d if v['key']=='HF_TOKEN'))" 2>/dev/null || true)"
        [ -n "${HF_TOKEN:-}" ] && echo "  -> HF_TOKEN restaurado (mascarado)"
      fi
    fi
  fi
else
  echo "[restore_env] sem GITLAB_TOKEN — pule variáveis GitLab (FAIL-OPEN)"
fi

# --- 2. GitHub: (opcional) ------------------------------------------------
if [ -n "${GH_TOKEN:-}" ]; then
  echo "[restore_env] GitHub: GH_TOKEN presente, mas secrets são write-only —"
  echo "[restore_env] variáveis GitHub não são legíveis via API. Use GitLab."
fi

# --- 3. Defaults de produção por escopo -----------------------------------
if [ "$SCOPE" = "public" ]; then
  export OMNI_GATE_FAIL_CLOSED="${OMNI_GATE_FAIL_CLOSED:-1}"   # gate fechado em produção
  export ERIKA_HOST="${ERIKA_HOST:-127.0.0.1}"                 # bind local apenas
  echo "[restore_env] escopo public: OMNI_GATE_FAIL_CLOSED=1, ERIKA_HOST=127.0.0.1"
else
  export OMNI_GATE_FAIL_CLOSED="${OMNI_GATE_FAIL_CLOSED:-0}"   # laboratório: fail-open
  echo "[restore_env] escopo domestic: OMNI_GATE_FAIL_CLOSED=0 (fail-open)"
fi

export OMNI_STATE_DIR="${OMNI_STATE_DIR:-$REPO/data}"
export OMNI_CODE_INDEX_DIR="${OMNI_CODE_INDEX_DIR:-$REPO/omni_code_index}"
echo "[restore_env] OMNI_STATE_DIR=$OMNI_STATE_DIR"
echo "[restore_env] OMNI_CODE_INDEX_DIR=$OMNI_CODE_INDEX_DIR"
echo "[restore_env] done."