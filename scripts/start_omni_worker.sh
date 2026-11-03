#!/usr/bin/env bash
# ============================================================================
# OMNI WORKER — bring-up da topologia completa (container/VM, sem systemd)
#
# English: One-command startup for the dual-brain worker node: analyst
# (:8098) → executor (:8099) → worker API (:8081) → state_guard →
# swap_scheduler. Sequential brain boot is intentional — concurrent nf4
# warmup OOMs the L4 (caching_allocator_warmup transient).
#
# pt-BR: Subida da topologia completa com um comando: analyst (:8098) →
# executor (:8099) → API do worker (:8081) → state_guard →
# swap_scheduler. Boot sequencial dos brains é intencional — warmup nf4
# concorrente estoura a L4 (transiente do caching_allocator_warmup).
#
# Usage / Uso:
#   bash scripts/start_omni_worker.sh           # sobe tudo
#   bash scripts/start_omni_worker.sh --no-brains   # só API + loops
#   bash scripts/start_omni_worker.sh --reindex     # força rebuild do code index
#   bash scripts/start_omni_worker.sh status    # status dos serviços
#   bash scripts/start_omni_worker.sh stop      # para tudo
#
# Env overrides / variáveis:
#   VENV_PYTHON        (default: auto-detect .venv siblings/omni_node)
#   ANALYST_MODEL      google/gemma-4-12B-it        EXECUTOR_MODEL  google/gemma-4-E4B-it
#   API_PORT 8081      ANALYST_PORT 8098            EXECUTOR_PORT 8099
#   OMNI_CODE_INDEX_DIR (default: <repo>/omni_code_index)
#   OMNI_STATE_DIR      (default: <repo>/data)
#   PYTHONPATH extra via OMNI_NODE_ROOT (default /content/omni_node, se existir)
# ============================================================================
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$REPO/logs"
PID_DIR="$REPO/runtime_config/pids"
mkdir -p "$LOG_DIR" "$PID_DIR" "$REPO/data/monitor"

# venv: prioriza o compartilhado documentado (omni_node), cai no local
if [ -z "${VENV_PYTHON:-}" ]; then
  for c in /content/omni_node/.venv/bin/python "$REPO/.venv/bin/python" /content/omni_worker/.venv/bin/python; do
    [ -x "$c" ] && VENV_PYTHON="$c" && break
  done
fi
VENV_PYTHON="${VENV_PYTHON:-python3}"

# PYTHONPATH: pacote próprio + acoplamento canônico opcional (omni_node)
PYTHONPATH="$REPO/src"
OMNI_NODE_ROOT="${OMNI_NODE_ROOT:-/content/omni_node}"
[ -d "$OMNI_NODE_ROOT/src" ] && PYTHONPATH="$OMNI_NODE_ROOT:$OMNI_NODE_ROOT/src:$PYTHONPATH"
export PYTHONPATH
export OMNI_CODE_INDEX_DIR="${OMNI_CODE_INDEX_DIR:-$REPO/omni_code_index}"
export OMNI_STATE_DIR="${OMNI_STATE_DIR:-$REPO/data}"

ANALYST_MODEL="${ANALYST_MODEL:-google/gemma-4-12B-it}"
EXECUTOR_MODEL="${EXECUTOR_MODEL:-google/gemma-4-E4B-it}"
API_PORT="${API_PORT:-8081}"
ANALYST_PORT="${ANALYST_PORT:-8098}"
EXECUTOR_PORT="${EXECUTOR_PORT:-8099}"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; RED='\033[0;31m'; NC='\033[0m'

port_open()  { curl -s -o /dev/null -m 2 "http://127.0.0.1:$1${2:-/health}"; }
pid_alive()  { [ -f "$PID_DIR/$1.pid" ] && kill -0 "$(cat "$PID_DIR/$1.pid")" 2>/dev/null; }

start_proc() { # name, log, cmd...
  local name="$1" log="$2"; shift 2
  if pid_alive "$name"; then
    echo -e "${YELLOW}[SKIP]${NC} $name já vivo (PID $(cat "$PID_DIR/$name.pid"))"; return 0
  fi
  nohup "$@" >> "$LOG_DIR/$log" 2>&1 &
  echo $! > "$PID_DIR/$name.pid"
  echo -e "${BLUE}[START]${NC} $name (PID $(cat "$PID_DIR/$name.pid"), log $log)"
}

wait_health() { # port, label, proc_name, timeout_s, probe_path
  local port="$1" label="$2" proc="$3" t="${4:-600}" probe="${5:-/health}" s=0
  while [ $s -lt "$t" ]; do
    port_open "$port" "$probe" && echo -e "${GREEN}[OK]${NC} $label saudável na :$port" && return 0
    sleep 5; s=$((s+5))
    pid_alive "$proc" || { echo -e "${RED}[FAIL]${NC} $label morreu — ver log"; return 1; }
  done
  echo -e "${RED}[FAIL]${NC} timeout $label :$port"; return 1
}

start_brain() { # label, model, port
  local label="$1" model="$2" port="$3"
  if port_open "$port"; then echo -e "${YELLOW}[SKIP]${NC} brain $label já na :$port"; return 0; fi
  echo -e "${BLUE}>> brain $label — $model (nf4, eager-attn) :$port${NC}"
  start_proc "brain_$label" "brain_${label}_${port}.log" \
    env PYTHONPATH="$REPO/src" "$VENV_PYTHON" -m omni_coworker.server.erika_torch_server \
      --model "$model" --load-4bit --eager-attn --port "$port"
  wait_health "$port" "$label" "brain_$label" 600
}

stop_all() {
  for p in "$PID_DIR"/*.pid; do
    [ -e "$p" ] || continue
    kill "$(cat "$p")" 2>/dev/null && echo "stopped $(basename "$p" .pid)"
    rm -f "$p"
  done
}

status() {
  for p in "$PID_DIR"/*.pid; do
    [ -e "$p" ] || continue
    n="$(basename "$p" .pid)"
    kill -0 "$(cat "$p")" 2>/dev/null && echo "$n RUNNING (PID $(cat "$p"))" || echo "$n dead"
  done
  for port in "$ANALYST_PORT" "$EXECUTOR_PORT"; do
    port_open "$port" && echo ":$port OK" || echo ":$port down"
  done
  port_open "$API_PORT" /soul/state && echo ":$API_PORT OK" || echo ":$API_PORT down"
}

case "${1:-up}" in
  stop)   stop_all; exit 0 ;;
  status) status; exit 0 ;;
  up|""|--no-brains|--reindex) ;;
  *) echo "uso: $0 [up|--no-brains|--reindex|status|stop]"; exit 2 ;;
esac

echo -e "${GREEN}OmniMind Worker bring-up${NC} — repo $REPO, python $VENV_PYTHON"

# Code index (symbolic body): só reconstrói se ausente ou se chamado explicitamente com --reindex.
# Se já existe índice válido, reutiliza imediatamente no startup para nunca atrasar os brains.
index_missing() {
  local mani="$OMNI_CODE_INDEX_DIR/chunks.parquet"
  [ ! -f "$mani" ]
}

if [ "${1:-}" = "--reindex" ] || index_missing; then
  echo -e "${BLUE}>> code index build → $OMNI_CODE_INDEX_DIR${NC}"
  # CPU-only: rebuild com brains residentes não pode disputar VRAM
  CUDA_VISIBLE_DEVICES="" "$VENV_PYTHON" -c "from omni_coworker.store import code_index; \
    print(code_index.build_index('$REPO/src/omni_coworker', code_index.index_dir()))" \
    || echo -e "${YELLOW}[WARN] index build falhou (dream/curiosity degradam p/ fallback)${NC}"
else
  echo -e "${GREEN}[OK]${NC} code index preservado/reutilizado ($OMNI_CODE_INDEX_DIR) — use --reindex para forçar"
fi

if [ "${1:-up}" != "--no-brains" ]; then
  # sequencial de propósito: warmup nf4 concorrente OOMa a L4
  start_brain analyst "$ANALYST_MODEL" "$ANALYST_PORT" || exit 1
  start_brain executor "$EXECUTOR_MODEL" "$EXECUTOR_PORT" || exit 1
fi

if ! port_open "$API_PORT" /soul/state; then
  start_proc worker_api "worker_api_${API_PORT}.log" \
    "$VENV_PYTHON" -m omni_coworker.cli serve --port "$API_PORT"
  wait_health "$API_PORT" worker_api worker_api 90 /soul/state || true
else
  echo -e "${YELLOW}[SKIP]${NC} API já na :$API_PORT"
fi

start_proc state_guard "state_guard.log" \
  "$VENV_PYTHON" -m omni_coworker.store.state_guard
start_proc swap_scheduler "swap_scheduler.log" \
  "$VENV_PYTHON" -m omni_coworker.orchestration.swap_scheduler
start_proc archive_loop "archive_loop.log" \
  bash "$REPO/scripts/archive_worker_state.sh" --loop "${ARCHIVE_INTERVAL_S:-3600}"

echo -e "\n${GREEN}Topologia:${NC}"
status
echo -e "\nLogs: $LOG_DIR | PIDs: $PID_DIR"
