#!/usr/bin/env bash
# ============================================================================
# OMNI WORKER — bring-up da topologia completa (container/VM, sem systemd)
#
# English: One-command startup for the worker node: analyst (:8098) →
# executor (:8099) → [judge (:8100) on tier xl] → worker API (:8081) →
# state_guard → swap_scheduler. Sequential brain boot is intentional —
# concurrent nf4 warmup OOMs the L4 (caching_allocator_warmup transient).
# Hardware tier is auto-detected (runtime_config/hw_profile.json):
#   xl  (>=60GB, A100/H100): + judge brain residente, budgets ampliados
#   std (>=18GB, L4):        topologia dual-brain padrão
#
# pt-BR: Subida da topologia completa com um comando: analyst (:8098) →
# executor (:8099) → [judge (:8100) no tier xl] → API do worker (:8081)
# → state_guard → swap_scheduler. Boot sequencial dos brains é intencional
# — warmup nf4 concorrente estoura a L4 (transiente do
# caching_allocator_warmup). O tier de hardware é auto-detectado
# (runtime_config/hw_profile.json):
#   xl  (>=60GB, A100/H100): + brain judge residente, budgets ampliados
#   std (>=18GB, L4):        topologia dual-brain padrão
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
#   JUDGE_MODEL        google/gemma-4-31B-it        (só sobe em tier xl ou OMNI_JUDGE_BRAIN=1)
#   API_PORT 8081      ANALYST_PORT 8098            EXECUTOR_PORT 8099    JUDGE_PORT 8100
#   OMNI_CODE_INDEX_DIR (default: <repo>/omni_code_index)
#   OMNI_STATE_DIR      (default: <repo>/data)
#   OMNI_HW_TIER        (auto: xl>=60GB | std>=18GB | min) — exportado p/ baterias
#   OMNI_JUDGE_BRAIN=1  força o 3º brain fora do tier xl
#   PYTHONPATH: só o pacote próprio (deps de repos irmãos estão vendored)
# ============================================================================
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$REPO/logs"
PID_DIR="$REPO/runtime_config/pids"
mkdir -p "$LOG_DIR" "$PID_DIR" "$REPO/data/monitor"
# captura temporal MPS (activation_steps/prompt_hidden): ligada por padrão
[ -f "$REPO/data/monitor/capture.env" ] || cat > "$REPO/data/monitor/capture.env" <<'CAP'
OMNI_ACT_STEP_EVERY=8
OMNI_ACT_STEP_ON=1
OMNI_ACT_STEP_KEEP=32
OMNI_ACT_PROMPT_HIDDEN=1
OMNI_ACT_VEC_SIDECAR=1
OMNI_ACT_VEC_KEEP=64
CAP

# venv: prioriza o próprio repo (omni_worker é autossuficiente — vendor/
# cobre o que antes vinha do omni_node)
if [ -z "${VENV_PYTHON:-}" ]; then
  for c in "$REPO/.venv/bin/python" /content/omni_worker/.venv/bin/python; do
    [ -x "$c" ] && VENV_PYTHON="$c" && break
  done
fi
VENV_PYTHON="${VENV_PYTHON:-python3}"

# PYTHONPATH: somente o pacote próprio. OMNI_NODE_ROOT segue exportado
# apenas como ponte opcional (fallbacks legados honram-no, nada exige).
PYTHONPATH="$REPO/src"
export OMNI_NODE_ROOT="${OMNI_NODE_ROOT:-/content/omni_node}"
export PYTHONPATH
export OMNI_CODE_INDEX_DIR="${OMNI_CODE_INDEX_DIR:-$REPO/omni_code_index}"
export OMNI_STATE_DIR="${OMNI_STATE_DIR:-$REPO/data}"
# Acervo (39G+) vai p/ scratch local quando o volume existe — alivia o
# overlay principal. Fallback /content/acervo_vetorizado em VMs sem /mnt.
if [ -z "${OMNI_ACERVO_DIR:-}" ]; then
  if [ -d /mnt/local-scratch ]; then
    OMNI_ACERVO_DIR=/mnt/local-scratch/acervo_vetorizado
  else
    OMNI_ACERVO_DIR=/content/acervo_vetorizado
  fi
fi
export OMNI_ACERVO_DIR
export OMNI_EMBED_DEVICE="${OMNI_EMBED_DEVICE:-cpu}"
export OMNI_MEMTRIAS_EMBEDDER="${OMNI_MEMTRIAS_EMBEDDER:-auto}"
export OMNI_MEMTRIAS_AUTO_LOG="${OMNI_MEMTRIAS_AUTO_LOG:-1}"
export OMNI_AUTO_CONTEXT_ASSIST="${OMNI_AUTO_CONTEXT_ASSIST:-1}"
export OMNI_SOMA_INJECT="${OMNI_SOMA_INJECT:-1}"
export OMNI_RESTORE_CO_RESIDENT="${OMNI_RESTORE_CO_RESIDENT:-1}"
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:False}"
DRIVE_BACKUP_DIR="${DRIVE_BACKUP_DIR:-/content/drive/MyDrive/omni_worker_backups}"
SOVEREIGN_TAR="${SOVEREIGN_TAR:-/content/drive/MyDrive/omnimind_backup/omnimind-kilombo-sovereign.tar.gz}"

# --- 0. Perfil de hardware — detecta o chassi e acomoda roster/budgets ----
# xl (>=60GB: A100/H100): 3 brains residentes + swap_chars ampliado;
# std (>=18GB: L4): topologia dual padrão; min: degrade.
# Persistido p/ shells e baterias que não herdam este env.
_gpu_mb="$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ' || echo 0)"
_gpu_name="$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1 || echo unknown)"
if [ "${_gpu_mb:-0}" -ge 60000 ]; then OMNI_HW_TIER=xl
elif [ "${_gpu_mb:-0}" -ge 18000 ]; then OMNI_HW_TIER=std
else OMNI_HW_TIER=min; fi
export OMNI_HW_TIER
export OMNI_JUDGE_SWAP_CHARS="${OMNI_JUDGE_SWAP_CHARS:-$([ "$OMNI_HW_TIER" = "xl" ] && echo 8000 || echo 3000)}"
mkdir -p "$REPO/runtime_config"
printf '{"tier":"%s","gpu":"%s","vram_mb":%s,"detected_utc":"%s"}\n' \
  "$OMNI_HW_TIER" "$_gpu_name" "${_gpu_mb:-0}" "$(date -u +%FT%TZ)" \
  > "$REPO/runtime_config/hw_profile.json"

ANALYST_MODEL="${ANALYST_MODEL:-google/gemma-4-12B-it}"
EXECUTOR_MODEL="${EXECUTOR_MODEL:-google/gemma-4-E4B-it}"
JUDGE_MODEL="${JUDGE_MODEL:-google/gemma-4-31B-it}"
API_PORT="${API_PORT:-8081}"
ANALYST_PORT="${ANALYST_PORT:-8098}"
EXECUTOR_PORT="${EXECUTOR_PORT:-8099}"
JUDGE_PORT="${JUDGE_PORT:-8100}"
export ERIKA_JUDGE_PORT="${ERIKA_JUDGE_PORT:-$JUDGE_PORT}"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; RED='\033[0;31m'; NC='\033[0m'

port_open()  { curl -s -o /dev/null -m 2 "http://127.0.0.1:$1${2:-/health}"; }
pid_alive()  { [ -f "$PID_DIR/$1.pid" ] && kill -0 "$(cat "$PID_DIR/$1.pid")" 2>/dev/null; }

start_proc() { # name, log, cmd...
  local name="$1" log="$2"; shift 2
  if pid_alive "$name"; then
    echo -e "${YELLOW}[SKIP]${NC} $name já vivo (PID $(cat "$PID_DIR/$name.pid"))"; return 0
  fi
  nohup setsid "$@" >> "$LOG_DIR/$log" 2>&1 &
  local pid=$!
  disown $pid 2>/dev/null || true
  echo $pid > "$PID_DIR/$name.pid"
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

start_brain() { # label, model, port, extra_flags
  local label="$1" model="$2" port="$3" extra="${4:-}"
  if port_open "$port"; then echo -e "${YELLOW}[SKIP]${NC} brain $label já na :$port"; return 0; fi
  echo -e "${BLUE}>> brain $label — $model (nf4, eager-attn) :$port${NC}"
  start_proc "brain_$label" "brain_${label}_${port}.log" \
    env PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:False}" \
        PYTHONPATH="$REPO/src" "$VENV_PYTHON" -m omni_coworker.server.erika_torch_server \
      --model "$model" --load-4bit --eager-attn --port "$port" $extra
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
  if [ "${OMNI_HW_TIER:-}" = "xl" ] || [ "${OMNI_JUDGE_BRAIN:-0}" = "1" ]; then
    port_open "$JUDGE_PORT" && echo ":$JUDGE_PORT OK" || echo ":$JUDGE_PORT down"
  fi
  port_open "$API_PORT" /soul/state && echo ":$API_PORT OK" || echo ":$API_PORT down"
}

case "${1:-up}" in
  stop)   stop_all; exit 0 ;;
  status) status; exit 0 ;;
  up|""|--no-brains|--reindex) ;;
  *) echo "uso: $0 [up|--no-brains|--reindex|status|stop]"; exit 2 ;;
esac

echo -e "${GREEN}OmniMind Worker bring-up${NC} — repo $REPO, python $VENV_PYTHON"

# --- 1. Bootstrap de variáveis e segredos (restore_env.sh) ------------------
# Sempre sourced: além dos segredos, aplica os defaults de escopo
# (OMNI_GATE_FAIL_CLOSED, ERIKA_HOST, OMNI_API_HOST). Antes ficava condicionado
# à ausência de HF_TOKEN — numa VM já hidratada o gate subia fail-open.
if [ -f "$REPO/scripts/restore_env.sh" ]; then
  echo -e "${BLUE}>> [bootstrap] restaurando variáveis de ambiente (restore_env.sh)...${NC}"
  # shellcheck disable=SC1090
  source "$REPO/scripts/restore_env.sh" --scope public || true
fi

# --- 2. Bootstrap de venv e dependências (pyproject.toml [all]) -------------
ensure_deps() {
  if [ "${OMNI_CREATE_VENV:-0}" = "1" ] && [ ! -x "$REPO/.venv/bin/python" ]; then
    echo -e "${BLUE}>> [bootstrap] criando virtualenv em $REPO/.venv...${NC}"
    python3 -m venv "$REPO/.venv" --system-site-packages
    VENV_PYTHON="$REPO/.venv/bin/python"
  fi
  # pyphi fica fora do check: só é usado por scripts/experiments/ e quebra no
  # Python 3.13 (collections.Iterable) — incluí-lo aqui reinstalaria [all] a cada boot.
  if ! "$VENV_PYTHON" -c "import fastapi, uvicorn, httpx, bitsandbytes, faiss, sentence_transformers, black, ruff, pytest_asyncio, sse_starlette, huggingface_hub, accelerate, safetensors, scipy" 2>/dev/null; then
    echo -e "${BLUE}>> [bootstrap] instalando dependências completas de pyproject.toml ([all])...${NC}"
    "$VENV_PYTHON" -m pip install -q -e "$REPO[all]" \
      || "$VENV_PYTHON" -m pip install -q bitsandbytes faiss-cpu sentence-transformers pandas pyarrow nvidia-ml-py httpx psutil ruff black pytest-asyncio sse-starlette huggingface-hub pyphi "agent-client-protocol>=0.12,<1"
  else
    echo -e "${GREEN}[OK]${NC} dependências Python verificadas ($VENV_PYTHON)"
  fi
}

# --- 3. Restauração automática de backup do Drive se bancos ausentes --------
ensure_state_restored() {
  if [ -f "$OMNI_STATE_DIR/integration_loop.sqlite" ] && [ -f "$OMNI_STATE_DIR/shared_workspace.sqlite" ]; then
    echo -e "${GREEN}[OK]${NC} bancos SQLite presentes em $OMNI_STATE_DIR"
    return 0
  fi
  if [ ! -d "$DRIVE_BACKUP_DIR" ]; then
    echo -e "${YELLOW}[INFO]${NC} $DRIVE_BACKUP_DIR não montado — iniciando com estado SQLite limpo e independente em $OMNI_STATE_DIR"
    return 0
  fi
  local latest
  latest="$(ls -1t "$DRIVE_BACKUP_DIR"/omni_worker_*.tar.gz 2>/dev/null | head -1 || true)"
  if [ -z "$latest" ]; then
    echo -e "${YELLOW}[INFO]${NC} nenhum omni_worker_*.tar.gz em $DRIVE_BACKUP_DIR — iniciando com estado SQLite limpo e independente"
    return 0
  fi
  echo -e "${BLUE}>> [bootstrap] verificando e restaurando backup: $(basename "$latest")${NC}"
  if bash "$REPO/scripts/archive_worker_state.sh" --verify "$latest"; then
    local stage="/tmp/omni_restore_stage_$$"
    mkdir -p "$stage"
    tar -xzf "$latest" -C "$stage"
    rm -rf "$stage/runtime_config/pids"
    for d in data logs omni_code_index runtime_config state; do
      [ -d "$stage/$d" ] && cp -a "$stage/$d" "$REPO/"
    done
    # scripts/*/*.sqlite|*.db de baterias: merge genérico do staging
    # (o tarball só carrega os bancos, não a árvore inteira de scripts)
    [ -d "$stage/scripts" ] && cp -a "$stage/scripts/." "$REPO/scripts/"
    rm -rf "$stage"
    echo -e "${GREEN}[OK]${NC} estado e bancos restaurados de $(basename "$latest")"
  else
    echo -e "${RED}[FAIL]${NC} verificação de integridade falhou para $latest — abortando restore"
  fi
}

# --- 4. Repositórios de referência e datasets HF (acervo + competição) ------
ensure_reference_assets() {
  if [ ! -d "/content/omnimind-kilombo-sovereign" ] && [ -f "$SOVEREIGN_TAR" ]; then
    echo -e "${BLUE}>> [bootstrap] descompactando /content/omnimind-kilombo-sovereign...${NC}"
    tar -xzf "$SOVEREIGN_TAR" -C /content || true
  fi
  # omni_node NÃO é mais clonado nem colocado no PYTHONPATH: o que o
  # worker precisa está vendored (vendor/kernel + omni_coworker.vendor).

  if [ ! -f "$OMNI_ACERVO_DIR/acervo_manifest.sqlite" ]; then
    if [ -n "${HF_TOKEN:-}" ]; then
      echo -e "${BLUE}>> [bootstrap] baixando acervo vetorizado HF -> $OMNI_ACERVO_DIR...${NC}"
      "$VENV_PYTHON" -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='fabricioslv/omnimind-acervo-vetorizado', repo_type='dataset', local_dir='$OMNI_ACERVO_DIR', max_workers=8)" \
        || echo -e "${YELLOW}[WARN] falha ao baixar acervo vetorizado${NC}"
    else
      echo -e "${YELLOW}[INFO]${NC} acervo vetorizado canônico omitido (HF_TOKEN ausente) — operando com memória vetorial sob demanda (MemtriasAI)"
    fi
  else
    echo -e "${GREEN}[OK]${NC} acervo vetorizado presente ($OMNI_ACERVO_DIR)"
  fi

  mkdir -p "$OMNI_STATE_DIR/hf_gemma4"
  if [ ! -f "$OMNI_STATE_DIR/hf_gemma4/gemma4_t4x2_v2_results.sqlite" ] || [ ! -f "$OMNI_STATE_DIR/hf_gemma4/gemma4_e4b_l4_results.sqlite" ]; then
    if [ -n "${HF_TOKEN:-}" ]; then
      echo -e "${BLUE}>> [bootstrap] baixando datasets da competição HF -> $OMNI_STATE_DIR/hf_gemma4...${NC}"
      "$VENV_PYTHON" -c "
from huggingface_hub import snapshot_download
for repo in ('fabricioslv/gemma4-kaggle-dual-t4-results', 'fabricioslv/gemma4-e4b-colab-l4-results'):
    snapshot_download(repo_id=repo, repo_type='dataset', local_dir='$OMNI_STATE_DIR/hf_gemma4')
" || echo -e "${YELLOW}[WARN] falha ao baixar datasets HF da competição${NC}"
    else
      echo -e "${YELLOW}[INFO]${NC} datasets de competição HF omitidos (HF_TOKEN ausente) — execução local continuará independente"
    fi
  else
    echo -e "${GREEN}[OK]${NC} datasets HF da competição presentes ($OMNI_STATE_DIR/hf_gemma4)"
  fi

  # Banco psicodiagnóstico (dedup materializado, commit HF 9eb617e3) —
  # insumo do scripts/psico_dual_judge_audit. Só os artefatos canônicos.
  PSICO_DIR="$OMNI_STATE_DIR/psicodiagnostico_v"
  if [ ! -f "$PSICO_DIR/embodied_psychodiagnostic_bank.sqlite" ]; then
    if [ -n "${HF_TOKEN:-}" ]; then
      echo -e "${BLUE}>> [bootstrap] baixando banco psicodiagnóstico HF -> $PSICO_DIR...${NC}"
      mkdir -p "$PSICO_DIR"
      "$VENV_PYTHON" -c "
from huggingface_hub import snapshot_download
snapshot_download(repo_id='fabricioslv/psicodiagnostico-v-embodied-results', repo_type='dataset', local_dir='$PSICO_DIR',
  allow_patterns=['embodied_psychodiagnostic_bank.sqlite','v10_colab_benchmark.sqlite','gemma4_runs_20261030/*','judges/*','INVENTARIO*','MONOGRAFIA*','analise_emergente*/*','appendices/*','data_sanitized/*'], max_workers=8)
" || echo -e "${YELLOW}[WARN] falha ao baixar banco psicodiagnóstico${NC}"
    else
      echo -e "${YELLOW}[INFO]${NC} banco psicodiagnóstico omitido (HF_TOKEN ausente) — use o dataset público Kaggle se desejar auditar"
    fi
  else
    echo -e "${GREEN}[OK]${NC} banco psicodiagnóstico presente ($PSICO_DIR)"
  fi

  # Garante os dois modelos de embedding em RAM/cache local:
  # 1) tardellirs/colibri-embed-ptbr (~600MB nativo PT-BR, Matryoshka)
  # 2) sentence-transformers/all-MiniLM-L6-v2 (384D, compatível com acervo_vetorizado)
  "$VENV_PYTHON" -c "
from huggingface_hub import snapshot_download
for m in ('tardellirs/colibri-embed-ptbr', 'sentence-transformers/all-MiniLM-L6-v2'):
    snapshot_download(repo_id=m)
" >/dev/null 2>&1 || true
}

# --- 2b. Kernel Rust opcional (omnimind_*: kernel_compute/metrics/freud10d) --
# Sem os .so, kernel_hooks degrada p/ fallback Python e /agency/dunker fica sem
# o affective_vector_28d (léxico zerado). Build é opcional: falha → warn.
ensure_kernel() {
  if "$VENV_PYTHON" -c "import omnimind_kernel_compute" 2>/dev/null; then
    echo -e "${GREEN}[OK]${NC} kernel Rust omnimind_* importável"
    return 0
  fi
  [ -f "$HOME/.cargo/env" ] && . "$HOME/.cargo/env" || true
  if ! command -v cargo >/dev/null 2>&1 && [ "${OMNI_KERNEL_AUTO_RUSTUP:-1}" = "1" ]; then
    echo -e "${BLUE}>> [kernel] cargo ausente — instalando rustup (stable, minimal)...${NC}"
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \
      | sh -s -- -y --profile minimal --default-toolchain stable >/dev/null 2>&1 \
      && . "$HOME/.cargo/env" || true
  fi
  if ! command -v cargo >/dev/null 2>&1; then
    echo -e "${YELLOW}[WARN]${NC} cargo ausente — kernel Rust não compilado (fallbacks Python ativos)"
    return 0
  fi
  echo -e "${BLUE}>> [kernel] compilando crates omnimind_* (kernel_compute, metrics, freud10d)...${NC}"
  CARGO_TARGET_DIR="${OMNI_KERNEL_TARGET_DIR:-$REPO/.kernel_target}" \
    PYTHON="$VENV_PYTHON" bash "$REPO/scripts/build_kernel.sh" \
    || echo -e "${YELLOW}[WARN]${NC} build do kernel falhou — seguindo com fallback Python"
}

ensure_deps
ensure_kernel
ensure_state_restored
ensure_reference_assets

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
  # Sequencial estrito (warmup nf4 concorrente estoura a L4).
  # Prioridade 1: Analyst (12B) — maior capacidade analítica.
  start_brain analyst "$ANALYST_MODEL" "$ANALYST_PORT" || exit 1

  # Prioridade 2: Executor (E4B). Verifica folga de VRAM antes de carregar.
  # Se VRAM estiver apertada (< 10GB livres), sobe o executor em modo --lazy:
  # o serviço :8099 fica ativo e o swap_scheduler gerencia o /erika/reload conforme a demanda.
  free_vram_mb=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ' || echo "0")
  if [ -n "$free_vram_mb" ] && [ "$free_vram_mb" -ge 10000 ]; then
    echo -e "${GREEN}[INFO]${NC} VRAM livre (${free_vram_mb}MB >= 10GB): tentando carregar executor residente..."
    if ! start_brain executor "$EXECUTOR_MODEL" "$EXECUTOR_PORT"; then
      echo -e "${YELLOW}[WARN]${NC} Carregamento direto do executor estourou VRAM. Recorrendo a modo --lazy..."
      start_brain executor "$EXECUTOR_MODEL" "$EXECUTOR_PORT" "--lazy" || true
    fi
  else
    echo -e "${YELLOW}[WARN]${NC} VRAM apertada (${free_vram_mb}MB livre < 10GB). Subindo executor em modo --lazy (alocação sob demanda via swap_scheduler)..."
    start_brain executor "$EXECUTOR_MODEL" "$EXECUTOR_PORT" "--lazy" || true
  fi

  # Prioridade 3: Judge (tier xl ou OMNI_JUDGE_BRAIN=1) — segunda-opinião
  # pesada residente. Falha do judge não derruba a malha (|| true).
  if [ "$OMNI_HW_TIER" = "xl" ] || [ "${OMNI_JUDGE_BRAIN:-0}" = "1" ]; then
    echo -e "${GREEN}[INFO]${NC} tier $OMNI_HW_TIER: subindo judge residente $JUDGE_MODEL :$JUDGE_PORT"
    start_brain judge "$JUDGE_MODEL" "$JUDGE_PORT" || true
  fi
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

# --- 4b. Pulso Basal de Sincronização do Dashboard -------------------------
# A cada PULSE_INTERVAL_S (default 1800s): exporta docs/data/dashboard/
# latest.json (+ espelho data/dashboard/latest.json) e, com a VM ativa,
# commita e pusha para origin (GitHub) e gitlab (token via /content/gitlab.txt,
# nunca exposto). O frontend degrada p/ "Modo Histórico" quando o pulso para.
if [ "${OMNI_PULSE_SYNC:-1}" = "1" ]; then
  start_proc pulse_sync "pulse_sync.log" \
    bash "$REPO/scripts/pulse_dashboard_sync.sh" --loop "${PULSE_INTERVAL_S:-1800}"
fi

# --- 5. Reidratação da memória topológica (memtrias.sqlite) se vazia --------
mem_count=$("$VENV_PYTHON" -c "import sqlite3, os; p='$OMNI_STATE_DIR/memtrias.sqlite'; print(sqlite3.connect(p).execute('SELECT count(*) FROM memories').fetchone()[0] if os.path.exists(p) else 0)" 2>/dev/null || echo "0")
if [ "${mem_count:-0}" -eq 0 ] && [ -f "$REPO/scripts/rehydrate_memtrias.py" ]; then
  echo -e "${BLUE}>> [bootstrap] memtrias.sqlite vazio (0 registros) — reidratando memórias reais...${NC}"
  "$VENV_PYTHON" "$REPO/scripts/rehydrate_memtrias.py" || echo -e "${YELLOW}[WARN] rehydrate_memtrias falhou${NC}"
else
  echo -e "${GREEN}[OK]${NC} memtrias.sqlite populado (${mem_count} memórias)"
fi

echo -e "\n${GREEN}Topologia:${NC}"
status
echo -e "\nLogs: $LOG_DIR | PIDs: $PID_DIR"
