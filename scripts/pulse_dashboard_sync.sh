#!/usr/bin/env bash
# ============================================================================
# pulse_dashboard_sync.sh — Pulso Basal de Sincronização do Dashboard (30 min)
#
# English: Basal pulse that keeps the public dashboard alive. Each beat:
#   1) runs scripts/dashboard_export.py → docs/data/dashboard/latest.json
#      (+ local mirror data/dashboard/latest.json)
#   2) when the VM is active (any of :8081/:8098/:8099 answering HTTP),
#      commits docs/data/dashboard/latest.json (and ONLY that file) and pushes
#      to origin (GitHub) and the gitlab remote (GitLab omni-group535144).
#   The GitLab token is read from GITLAB_TOKEN or /content/gitlab.txt and fed
#   to git through a credential.helper that expands the ENV VAR inside the
#   credential subprocess — the token never appears in argv, remote config,
#   files or logs.
#
# pt-BR: Pulso basal que mantém o dashboard público vivo. A cada batida:
#   exporta → commit cirúrgico → push origin+gitlab (token nunca exposto).
#
# Usage / Uso:
#   bash scripts/pulse_dashboard_sync.sh --once          # uma batida
#   bash scripts/pulse_dashboard_sync.sh --loop [secs]   # loop (default 1800)
#   bash scripts/pulse_dashboard_sync.sh --once --no-push  # exporta sem git
# ============================================================================
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCS_JSON_REL="docs/data/dashboard/latest.json"
GITLAB_PROJECT="omni-group535144/omni_worker"
GITLAB_URL="https://gitlab.com/${GITLAB_PROJECT}.git"
LOG_PREFIX="[pulse]"

# venv: mesma detecção do start_omni_worker.sh
if [ -z "${VENV_PYTHON:-}" ]; then
  for c in "$REPO/.venv/bin/python" /content/omni_worker/.venv/bin/python; do
    [ -x "$c" ] && VENV_PYTHON="$c" && break
  done
fi
VENV_PYTHON="${VENV_PYTHON:-python3}"

MODE="once"
INTERVAL="${PULSE_INTERVAL_S:-1800}"
DO_PUSH=1
case "${1:---once}" in
  --once) MODE="once" ;;
  --loop) MODE="loop"; [ -n "${2:-}" ] && INTERVAL="$2" ;;
  *) echo "uso: $0 [--once | --loop [secs]] [--no-push]"; exit 2 ;;
esac
for arg in "$@"; do [ "$arg" = "--no-push" ] && DO_PUSH=0; done

echo "$LOG_PREFIX repo=$REPO python=$VENV_PYTHON mode=$MODE interval=${INTERVAL}s push=$DO_PUSH"

vm_active() {
  curl -sf -m 2 -o /dev/null "http://127.0.0.1:8098/health"     && return 0
  curl -sf -m 2 -o /dev/null "http://127.0.0.1:8099/health"     && return 0
  curl -sf -m 2 -o /dev/null "http://127.0.0.1:8081/soul/state" && return 0
  return 1
}

gitlab_token() {
  if [ -n "${GITLAB_TOKEN:-}" ]; then printf '%s' "$GITLAB_TOKEN"; return 0; fi
  [ -f /content/gitlab.txt ] || return 1
  local t
  t="$(sed -n 's/^glab_token=//p' /content/gitlab.txt | head -1 | tr -d '[:space:]')"
  [ -z "$t" ] && t="$(head -1 /content/gitlab.txt | tr -d '[:space:]')"
  printf '%s' "$t"
}

push_remotes() {
  cd "$REPO" || return 1
  git push origin HEAD:master 2>&1 | sed 's/^/  [origin] /' || \
    echo "$LOG_PREFIX WARN: push origin falhou (sem rede/auth) — próxima batida tenta de novo"

  local tok; tok="$(gitlab_token || true)"
  if [ -z "$tok" ]; then
    echo "$LOG_PREFIX WARN: GITLAB_TOKEN/gitlab.txt ausente — push gitlab pulado (fail-open)"
    return 0
  fi
  git remote get-url gitlab >/dev/null 2>&1 || git remote add gitlab "$GITLAB_URL"
  # credential.helper expande $GITLAB_TOKEN DENTRO do subprocesso de credencial:
  # argv, remote -v, config e logs nunca carregam o token.
  GITLAB_TOKEN="$tok" git \
    -c "credential.helper=!f() { echo username=oauth2; echo \"password=\$GITLAB_TOKEN\"; }; f" \
    push gitlab HEAD:master 2>&1 \
      | sed -E 's/(glpat-|oauth2:|password=)[^ &]*/\1***/g; s/^/  [gitlab] /' \
    || echo "$LOG_PREFIX WARN: push gitlab falhou — próxima batida tenta de novo"
}

beat() {
  local ts; ts="$(date -u +%FT%TZ)"
  echo "$LOG_PREFIX beat $ts — exportando latest.json..."
  PYTHONPATH="$REPO/src" "$VENV_PYTHON" "$REPO/scripts/dashboard_export.py" || {
    echo "$LOG_PREFIX ERROR: dashboard_export.py falhou"; return 1; }

  if [ "$DO_PUSH" -eq 0 ]; then
    echo "$LOG_PREFIX --no-push: exportação concluída (git pulado)"
    return 0
  fi
  if ! vm_active; then
    echo "$LOG_PREFIX VM inativa (nenhum :8081/:8098/:8099 saudável) — latest.json atualizado localmente, commit/push adiados"
    return 0
  fi

  cd "$REPO" || return 1
  git add -- "$DOCS_JSON_REL"
  if git diff --cached --quiet -- "$DOCS_JSON_REL"; then
    echo "$LOG_PREFIX latest.json sem alteração — nada a commitar"
  else
    git -c user.name="omni-pulse" -c user.email="omni-pulse@omni-worker.local" \
      commit -q -m "chore(pulse): dashboard latest.json sync $(date -u +%FT%TZ)" \
      && echo "$LOG_PREFIX commit: $DOCS_JSON_REL"
  fi
  push_remotes
}

case "$MODE" in
  once)
    beat
    ;;
  loop)
    echo "$LOG_PREFIX loop ativo — batida a cada ${INTERVAL}s (Ctrl+C p/ parar)"
    while true; do
      beat || true
      sleep "$INTERVAL"
    done
    ;;
esac
