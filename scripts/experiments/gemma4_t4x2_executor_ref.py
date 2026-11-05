#!/usr/bin/env python3
"""
gemma4_t4x2_executor.py (v2.1 — Auditado SWE-2 Max) — Kaggle Dual T4 (2x16GB = 32GB VRAM).
==========================================================================================
Suite Experimental Unificada (Ondas 1 e 2) do Gemma-4 Developer Agent Paper Track:

  - Prioridade 1 (Onda 1B — Opção 3 Expandida + Calibração 48L/LOTO em SWE, 3072 tok):
      * nf4_swe_baseline (sensor contrafactual + perfil 48 camadas + acumuladores LOTO
        persistidos transacionalmente por episódio em `loto_episode_accumulators` — 100%
        imune a cortes/resume entre múltiplas sessões Kaggle)
      * nf4_cascade_soft_v2 (Opção 3A: proteção B_think=1024, K=160 pós-think, sem frame órfão)
      * nf4_cascade_hard_cut (Opção 3B: Corte de Sessão com truncamento do sufixo degenerado,
        registro forense `purged_preview` e fechamento explícito de <channel|>)
  - Prioridade 2 (Onda 2 — Intervenções Latentes Closed-Loop Pareadas em SWE, 3072 tok):
      * Bipartição MPS Central Exata (64 x 60 = 3840, chi_eff in [1, 60], S_vN real)
      * Detector Cinemático de Trajetória em Janela (W=16 x 3840 centralizado, Gram 16x16, PR_traj)
      * nf4_opt1_steering (Opção 1: Closed-Loop Contrastive Activation Steering LOTO estrito 5->1
        nos hubs [17, 23, 29, 35], sem fallback circular p/ __GLOBAL__, norma fp16 preservada)
      * nf4_opt2_spectral (Opção 2: Closed-Loop Trajectory Subspace Deflation calibration-free
        alinhada ao tick de medição nos hubs [17, 23, 29, 35], amortecendo u_1 sem deflação composta)
  - Prioridade 3 (Onda 1A — Controles de Formato & Quantização em Longo Horizonte, 2048 tok):
      * nf4_swe_completion (controle de formato em SWE)
      * nf4_chat_long (20 cenas V10 x 2 fases com 2º turno conversacional real + mapa 48 camadas)
      * int8_chat_long vs. int8_completion_long (20 cenas V10 x 2 fases em LLM.int8)

Nota arquitetural: hooks atuam forward-localmente no residual stream (padrão activation steering).
"""

import os
import re
import sys
import math
import time
import json
import shutil
import hashlib
import sqlite3
import argparse
from datetime import datetime, timezone
from typing import Dict, List, Any, Tuple, Optional

import numpy as np
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    StoppingCriteria,
    StoppingCriteriaList,
)

# ============================================================================
# Constantes Arquiteturais (Gemma-4 12B Verificado)
# ============================================================================
CANONICAL_48_LAYERS = (0, 5, 11, 17, 23, 29, 35, 41, 47)  # L0 + 8 hubs globais full_attention
INTERVENTION_HUB_LAYERS = (17, 23, 29, 35)                # Hubs do gargalo -> re-expansão

PROGRESS_TEXT_MARKERS = (
    "diff --git",
    "```diff",
    "Index:",
    "--- a/",
    "+++ b/",
    "@@ -",
    "<|tool_call>",
    "<tool_call>",
    "call:",
)

PATCH_TEXT_MARKERS = (
    "diff --git",
    "--- a/",
    "+++ b/",
)

MARKER_SYMBOLIC_ALIASES = {
    "diff --git": "patch_header",
    "```diff": "diff_fence",
    "Index:": "index_header",
    "--- a/": "file_orig_header",
    "+++ b/": "file_mod_header",
    "@@ -": "diff_hunk",
    "<|tool_call>": "tool_call",
    "<tool_call>": "tool_call",
    "call:": "fn_call",
}

SCAFFOLD_REGEX = re.compile(
    r"(?:\n?\[(?:CASCADE_FRAME|SESSION_CUT)\][^\n]*\n(?:Action:\n)?)"
    r"|(?:\n?Think:\s*re-evaluating strategy\.[^\n]*Action:\n?)",
    flags=re.MULTILINE,
)

CHANNEL_THOUGHT_REGEX = re.compile(
    r"<\|channel>\s*thought\s?(.*?)(?:<channel\|>|$)",
    flags=re.DOTALL,
)

TOOL_CALL_CLEAN_REGEX = re.compile(r"(?:<\|tool_call>|\bcall:[A-Za-z_][A-Za-z0-9_]*\{)")


# ============================================================================
# Utilitários de Hardware, Sessão e Upload de Sobrevivência
# ============================================================================
def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_gpu_memory_snapshots() -> Dict[str, float]:
    """Captura memória alocada e reservada (MB) em cada GPU disponível."""
    snaps = {"gpu0_alloc_mb": 0.0, "gpu0_reserved_mb": 0.0, "gpu1_alloc_mb": 0.0, "gpu1_reserved_mb": 0.0}
    if not torch.cuda.is_available():
        return snaps
    for i in range(min(2, torch.cuda.device_count())):
        snaps[f"gpu{i}_alloc_mb"] = round(torch.cuda.memory_allocated(i) / (1024 * 1024), 2)
        snaps[f"gpu{i}_reserved_mb"] = round(torch.cuda.memory_reserved(i) / (1024 * 1024), 2)
    return snaps


def log_memory_snapshot(conn: sqlite3.Connection, phase: str, record_id: Optional[int] = None) -> None:
    snaps = get_gpu_memory_snapshots()
    conn.execute(
        """
        INSERT INTO memory_snapshots (
            record_id, phase, gpu0_alloc_mb, gpu0_reserved_mb,
            gpu1_alloc_mb, gpu1_reserved_mb, timestamp_utc
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record_id,
            phase,
            snaps["gpu0_alloc_mb"],
            snaps["gpu0_reserved_mb"],
            snaps["gpu1_alloc_mb"],
            snaps["gpu1_reserved_mb"],
            utc_now_iso(),
        ),
    )
    conn.commit()


def log_budget_event(conn: sqlite3.Connection, event_type: str, detail: str) -> None:
    conn.execute(
        "INSERT INTO budget_events (event_type, detail, timestamp_utc) VALUES (?, ?, ?)",
        (event_type, detail, utc_now_iso()),
    )
    conn.commit()


class BudgetController:
    """Controla o tempo acumulado da sessão Kaggle (margem padrão de 1200s p/ episódios de 3072 tok)."""

    def __init__(self, max_hours: float = 10.8, epoch_file: Optional[str] = None):
        self.max_seconds = max_hours * 3600.0
        self.start_epoch = time.time()
        if epoch_file and os.path.exists(epoch_file):
            try:
                with open(epoch_file, "r", encoding="utf-8") as f:
                    self.start_epoch = float(f.read().strip())
            except Exception:
                pass

    def elapsed_seconds(self) -> float:
        return max(0.0, time.time() - self.start_epoch)

    def remaining_seconds(self) -> float:
        return max(0.0, self.max_seconds - self.elapsed_seconds())

    def should_stop(self, min_margin_seconds: float = 1200.0) -> bool:
        return self.remaining_seconds() <= min_margin_seconds


def maybe_upload_checkpoint_hf(
    conn: sqlite3.Connection,
    db_path: str,
    hf_repo: Optional[str],
    reason: str,
) -> bool:
    """Faz WAL checkpoint passivo, copia snapshot consistente e envia ao Hugging Face Hub."""
    if not hf_repo:
        return False
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        try:
            from kaggle_secrets import UserSecretsClient
            hf_token = UserSecretsClient().get_secret("HF_TOKEN")
        except Exception:
            hf_token = None
    if not hf_token:
        return False

    snap_path = f"{db_path}.upload_snap"
    try:
        conn.commit()
        conn.execute("PRAGMA wal_checkpoint(PASSIVE);")
        shutil.copyfile(db_path, snap_path)
        with open(snap_path, "rb") as f_in:
            sha256_hex = hashlib.sha256(f_in.read()).hexdigest()[:16]
        size_mb = round(os.path.getsize(snap_path) / (1024 * 1024), 2)

        from huggingface_hub import HfApi
        api = HfApi(token=hf_token)
        api.create_repo(repo_id=hf_repo, repo_type="dataset", private=True, exist_ok=True)
        fname = os.path.basename(db_path)
        api.upload_file(
            path_or_fileobj=snap_path,
            path_in_repo=fname,
            repo_id=hf_repo,
            repo_type="dataset",
            commit_message=f"[{reason}] {fname} ({size_mb} MB, sha={sha256_hex})",
        )
        log_budget_event(conn, "hf_upload", f"OK reason={reason} file={fname} mb={size_mb} sha={sha256_hex}")
        return True
    except Exception as exc:
        log_budget_event(conn, "hf_upload_warn", f"WARN reason={reason} err={str(exc)[:180]}")
        return False
    finally:
        if os.path.exists(snap_path):
            try:
                os.remove(snap_path)
            except Exception:
                pass


# ============================================================================
# Banco SQLite Transacional (Schema v2.1 + Persistência LOTO por Episódio)
# ============================================================================
def init_database(db_path: str) -> sqlite3.Connection:
    """Inicializa banco SQLite em modo WAL com todas as tabelas das Ondas 1 e 2."""
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=60.0)
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA busy_timeout = 30000;")

    schema = """
    CREATE TABLE IF NOT EXISTS run_metadata (
        run_id TEXT PRIMARY KEY,
        model_id TEXT NOT NULL,
        model_revision_sha TEXT,
        quantization TEXT NOT NULL,
        compute_dtype TEXT NOT NULL,
        device_map_json TEXT NOT NULL,
        transformers_ver TEXT NOT NULL,
        bitsandbytes_ver TEXT,
        torch_ver TEXT NOT NULL,
        cuda_ver TEXT,
        gpus_json TEXT NOT NULL,
        kaggle_session_id TEXT,
        started_at_utc TEXT NOT NULL,
        completed_at_utc TEXT,
        status TEXT DEFAULT 'RUNNING'
    );

    CREATE TABLE IF NOT EXISTS experiment_ledger (
        experiment TEXT NOT NULL,
        arm TEXT NOT NULL,
        task_id TEXT NOT NULL,
        rep_idx INTEGER NOT NULL,
        status TEXT NOT NULL,
        record_id INTEGER,
        updated_at_utc TEXT NOT NULL,
        PRIMARY KEY (experiment, arm, task_id, rep_idx)
    );

    CREATE TABLE IF NOT EXISTS generation_records (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT NOT NULL,
        experiment TEXT NOT NULL,
        arm TEXT NOT NULL,
        task_id TEXT NOT NULL,
        task_phase TEXT,
        rep_idx INTEGER NOT NULL,
        prompt_tokens INTEGER NOT NULL,
        generated_tokens INTEGER NOT NULL,
        n_cascade_restarts INTEGER DEFAULT 0,
        n_would_fire INTEGER DEFAULT 0,
        latency_seconds REAL,
        tokens_per_s REAL,
        visible_response TEXT,
        thinking_trace TEXT,
        finish_reason TEXT,
        degenerate_flag INTEGER,
        unique_ratio REAL,
        tool_calls_n INTEGER DEFAULT 0,
        progress_events_n INTEGER DEFAULT 0,
        seed INTEGER,
        timestamp_utc TEXT NOT NULL,
        enable_thinking INTEGER DEFAULT 1,
        thinking_tokens INTEGER DEFAULT 0,
        visible_tokens INTEGER DEFAULT 0,
        thought_closed INTEGER DEFAULT 0,
        ur_thinking REAL,
        ur_visible REAL,
        ur_sanitized REAL,
        degen_sanitized INTEGER,
        cut_tokens_purged INTEGER DEFAULT 0,
        n_hook_interventions INTEGER DEFAULT 0,
        steering_source TEXT
    );

    CREATE TABLE IF NOT EXISTS cascade_events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_id INTEGER NOT NULL,
        restart_idx INTEGER NOT NULL,
        trigger_type TEXT NOT NULL,
        token_pos INTEGER NOT NULL,
        cut_tokens INTEGER DEFAULT 0,
        purged_preview TEXT,
        last_progress_marker TEXT,
        context_ref TEXT,
        temp_before REAL,
        temp_after REAL,
        frame_text TEXT,
        timestamp_utc TEXT NOT NULL,
        FOREIGN KEY(record_id) REFERENCES generation_records(record_id)
    );

    CREATE TABLE IF NOT EXISTS latent_layer_metrics (
        metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_id INTEGER NOT NULL,
        layer_idx INTEGER NOT NULL,
        phase TEXT NOT NULL,
        token_pos INTEGER NOT NULL,
        pr_traj REAL,
        top1_energy_ratio REAL,
        svd_entropy_traj REAL,
        mps_chi_eff REAL,
        mps_svn REAL,
        mps_top1_schmidt REAL,
        h_norm REAL,
        hook_fired_count INTEGER DEFAULT 0,
        timestamp_utc TEXT NOT NULL,
        FOREIGN KEY(record_id) REFERENCES generation_records(record_id)
    );

    CREATE TABLE IF NOT EXISTS loto_episode_accumulators (
        record_id INTEGER NOT NULL,
        task_id TEXT NOT NULL,
        rep_idx INTEGER NOT NULL,
        layer_idx INTEGER NOT NULL,
        pos_n INTEGER NOT NULL,
        pos_pr_sum REAL NOT NULL,
        pos_sum_blob BLOB NOT NULL,
        neg_n INTEGER NOT NULL,
        neg_pr_sum REAL NOT NULL,
        neg_sum_blob BLOB NOT NULL,
        timestamp_utc TEXT NOT NULL,
        PRIMARY KEY (record_id, layer_idx),
        FOREIGN KEY(record_id) REFERENCES generation_records(record_id)
    );

    CREATE TABLE IF NOT EXISTS steering_calibration (
        calib_id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT NOT NULL,
        held_out_task TEXT NOT NULL,
        n_source_tasks INTEGER DEFAULT 0,
        layer_idx INTEGER NOT NULL,
        n_pos_windows INTEGER NOT NULL,
        n_neg_windows INTEGER NOT NULL,
        pos_pr_mean REAL,
        neg_pr_mean REAL,
        delta_norm REAL,
        tau_pr_threshold REAL,
        vector_blob BLOB NOT NULL,
        timestamp_utc TEXT NOT NULL,
        UNIQUE(held_out_task, layer_idx)
    );

    CREATE TABLE IF NOT EXISTS memory_snapshots (
        snap_id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_id INTEGER,
        phase TEXT NOT NULL,
        gpu0_alloc_mb REAL,
        gpu0_reserved_mb REAL,
        gpu1_alloc_mb REAL,
        gpu1_reserved_mb REAL,
        timestamp_utc TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS budget_events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT NOT NULL,
        detail TEXT,
        timestamp_utc TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_records_arm ON generation_records(experiment, arm);
    CREATE INDEX IF NOT EXISTS idx_ledger_status ON experiment_ledger(status);
    CREATE INDEX IF NOT EXISTS idx_cascade_rec ON cascade_events(record_id);
    CREATE INDEX IF NOT EXISTS idx_latent_rec ON latent_layer_metrics(record_id, layer_idx);
    CREATE INDEX IF NOT EXISTS idx_loto_acc_task ON loto_episode_accumulators(task_id, layer_idx);
    """
    conn.executescript(schema)

    # Migrações retrocompatíveis
    existing_cols = {r[1] for r in conn.execute("PRAGMA table_info(generation_records)").fetchall()}
    for col_name, col_def in [
        ("enable_thinking", "INTEGER DEFAULT 1"),
        ("thinking_tokens", "INTEGER DEFAULT 0"),
        ("visible_tokens", "INTEGER DEFAULT 0"),
        ("thought_closed", "INTEGER DEFAULT 0"),
        ("ur_thinking", "REAL"),
        ("ur_visible", "REAL"),
        ("ur_sanitized", "REAL"),
        ("degen_sanitized", "INTEGER"),
        ("cut_tokens_purged", "INTEGER DEFAULT 0"),
        ("n_hook_interventions", "INTEGER DEFAULT 0"),
        ("steering_source", "TEXT"),
    ]:
        if col_name not in existing_cols:
            conn.execute(f"ALTER TABLE generation_records ADD COLUMN {col_name} {col_def};")

    cascade_cols = {r[1] for r in conn.execute("PRAGMA table_info(cascade_events)").fetchall()}
    for col_name, col_def in [("cut_tokens", "INTEGER DEFAULT 0"), ("purged_preview", "TEXT")]:
        if col_name not in cascade_cols:
            conn.execute(f"ALTER TABLE cascade_events ADD COLUMN {col_name} {col_def};")

    calib_cols = {r[1] for r in conn.execute("PRAGMA table_info(steering_calibration)").fetchall()}
    if "n_source_tasks" not in calib_cols:
        conn.execute("ALTER TABLE steering_calibration ADD COLUMN n_source_tasks INTEGER DEFAULT 0;")

    # P1-10: Marca runs anteriores órfãs (RUNNING de sessões mortas) como DIED
    conn.execute(
        "UPDATE run_metadata SET status='DIED', completed_at_utc=? WHERE status='RUNNING'",
        (utc_now_iso(),),
    )
    conn.commit()
    return conn


# ============================================================================
# Formatação de Prompt & Parser Estruturado do Canal `<|channel>thought`
# ============================================================================
def first_input_device(model) -> torch.device:
    """Determinístico p/ modelos sharded multimodais: usa `get_input_embeddings()` se disponível (P1-8)."""
    try:
        if hasattr(model, "get_input_embeddings") and model.get_input_embeddings() is not None:
            return model.get_input_embeddings().weight.device
        return next(model.parameters()).device
    except Exception:
        return torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def encode_messages_tensor(
    tokenizer,
    messages: List[Dict[str, str]],
    use_chat: bool,
    enable_thinking: bool,
    device: torch.device,
) -> torch.Tensor:
    """
    Codifica mensagens respeitando o chat_template.jinja canônico do Gemma-4:
      - use_chat=True, enable_thinking=True  -> injeta `<|turn>system\\n<|think|>\\n<turn|>`
        e deixa `<|turn>model\\n` aberto para emitir `<|channel>thought...<channel|>`.
      - use_chat=True, enable_thinking=False -> fecha `<|channel>thought\\n<channel|>` no prompt.
      - use_chat=False                       -> completion cru (concatenação textual pareada).
    """
    if use_chat:
        try:
            rendered = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=enable_thinking,
            )
        except TypeError:
            rendered = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
            if enable_thinking and "<|think|>" not in rendered:
                if rendered.endswith("<|channel>thought\n<channel|>"):
                    rendered = rendered[: -len("<|channel>thought\n<channel|>")]
                bos = tokenizer.bos_token or ""
                if bos and rendered.startswith(bos):
                    rendered = bos + "<|turn>system\n<|think|>\n<turn|>\n" + rendered[len(bos) :]
                else:
                    rendered = "<|turn>system\n<|think|>\n<turn|>\n" + rendered
        res = tokenizer(rendered, add_special_tokens=False, return_tensors="pt")
    else:
        raw_parts = [m["content"] for m in messages if m.get("content")]
        raw_text = "\n\n".join(raw_parts)
        res = tokenizer(raw_text, return_tensors="pt")

    if hasattr(res, "input_ids"):
        tensor = res.input_ids
    elif isinstance(res, dict) and "input_ids" in res:
        tensor = res["input_ids"]
    else:
        tensor = res
    return tensor.to(device)


def sanitize_scaffold_text(text: str) -> str:
    """Remove frames injetados pelo Cascade/Session-Cut para medição pura da fala do modelo."""
    if not text:
        return ""
    return SCAFFOLD_REGEX.sub("\n", text).strip()


def compute_token_ur(tokenizer, text: str) -> Tuple[int, Optional[float]]:
    if not text:
        return 0, None
    ids = tokenizer.encode(text, add_special_tokens=False)
    if not ids:
        return 0, None
    return len(ids), round(len(set(ids)) / float(len(ids)), 4)


def parse_gemma4_channels(tokenizer, gen_ids: torch.Tensor) -> Dict[str, Any]:
    """
    Separa com precisão o canal interno `<|channel>thought...<channel|>` da resposta visível,
    preservando métricas desacopladas (`ur_thinking`, `ur_visible`, `ur_sanitized`).
    """
    ids_list = gen_ids.tolist() if hasattr(gen_ids, "tolist") else list(gen_ids)
    n_raw = len(ids_list)
    raw_ur = round(len(set(ids_list)) / float(n_raw), 4) if n_raw > 0 else 0.0

    raw_decoded = tokenizer.decode(ids_list, skip_special_tokens=False)

    thought_matches = list(CHANNEL_THOUGHT_REGEX.finditer(raw_decoded))
    n_open_tags = len(thought_matches)
    n_close_tags = raw_decoded.count("<channel|>")
    thought_segments: List[str] = []

    if n_open_tags > 0:
        for match in thought_matches:
            seg = match.group(1).strip()
            if seg:
                thought_segments.append(seg)
        visible_raw = CHANNEL_THOUGHT_REGEX.sub("", raw_decoded)
        thought_closed = 1 if n_close_tags >= n_open_tags else 0
    else:
        visible_raw = raw_decoded
        thought_closed = 0

    # Preserva contagem de `<|tool_call>` na região visível ANTES de remover tokens especiais (P1-12)
    vis_before_sp_strip = sanitize_scaffold_text(visible_raw)
    tool_calls_n = len(TOOL_CALL_CLEAN_REGEX.findall(vis_before_sp_strip))

    for sp in getattr(tokenizer, "all_special_tokens", []):
        if sp:
            visible_raw = visible_raw.replace(sp, "")
            thought_segments = [s.replace(sp, "") for s in thought_segments]

    thinking_trace = "\n\n".join(s.strip() for s in thought_segments if s.strip())
    visible_response = visible_raw.strip()

    think_clean = sanitize_scaffold_text(thinking_trace)
    vis_clean = sanitize_scaffold_text(visible_response)
    combined_clean = (think_clean + "\n" + vis_clean).strip()

    thinking_tokens, ur_thinking = compute_token_ur(tokenizer, think_clean)
    visible_tokens, ur_visible = compute_token_ur(tokenizer, vis_clean)
    sanitized_tokens, ur_sanitized = compute_token_ur(tokenizer, combined_clean)
    if ur_sanitized is None:
        ur_sanitized = 0.0

    degen_raw = 1 if (raw_ur < 0.30 or n_raw < 50) else 0
    degen_sanitized = 1 if (ur_sanitized < 0.30 or sanitized_tokens < 50) else 0
    has_patch = 1 if any(m in vis_clean for m in PATCH_TEXT_MARKERS) else 0

    return {
        "thinking_trace": thinking_trace,
        "visible_response": visible_response,
        "thinking_tokens": thinking_tokens,
        "visible_tokens": visible_tokens,
        "thought_closed": thought_closed,
        "unique_ratio": raw_ur,
        "ur_thinking": ur_thinking,
        "ur_visible": ur_visible,
        "ur_sanitized": ur_sanitized,
        "degenerate_flag": degen_raw,
        "degen_sanitized": degen_sanitized,
        "tool_calls_n": tool_calls_n,
        "has_patch": has_patch,
    }


# ============================================================================
# Opção 3 (v2.1): VaciloTriggerV2 O(1) Incremental + Soft (3A) & Hard Cut (3B)
# ============================================================================
def has_repeated_ngram(tokens: List[int], n: int = 8, min_repeats: int = 3) -> Optional[int]:
    """
    Detecta se qualquer n-grama de tokens aparece >= min_repeats vezes na janela.
    Retorna o índice relativo do início da 2ª ocorrência (onde o loop começou), ou None.
    """
    L = len(tokens)
    if L < n * min_repeats:
        return None
    counts: Dict[Tuple[int, ...], int] = {}
    second_occ_idx: Dict[Tuple[int, ...], int] = {}
    for i in range(L - n + 1):
        ng = tuple(tokens[i : i + n])
        c = counts.get(ng, 0) + 1
        counts[ng] = c
        if c == 2:
            second_occ_idx[ng] = i
        elif c >= min_repeats:
            return second_occ_idx[ng]
    return None


class VaciloTriggerV2(StoppingCriteria):
    """
    Detector Bifásico O(1)/passo (P1-4, P1-5, P1-15 corrigidos):
      - Rastreia incrementalmente contadores de `<|channel>` / `<channel|>` (pensamento)
        e `<|tool_call>` / `<tool_call|>` (chamada de ferramenta JSON longa) em O(1).
      - Dentro de `<|channel>thought`: suspende `k_no_progress` até `think_budget` (1024 tok),
        disparando cedo apenas em repetição cíclica real (`think_repetition`).
      - Dentro de `<|tool_call>...<tool_call|>`: suspende `k_no_progress` p/ não cortar JSON válido.
      - Alinha `token_pos` em `gross_generated` (`gross_offset + seg_len`) tanto em `would_fire`
        quanto em restarts reais.
    """

    def __init__(
        self,
        tokenizer,
        tool_token_ids: List[int],
        episode_prompt_len: int,
        gross_offset: int,
        ch_open_id: Optional[int],
        ch_close_id: Optional[int],
        tc_open_id: Optional[int] = None,
        tc_close_id: Optional[int] = None,
        K: int = 160,
        think_budget: int = 1024,
        W: int = 128,
        ur_min: float = 0.30,
        observe_only: bool = False,
    ):
        super().__init__()
        self.tok = tokenizer
        self.tool_ids = set(tool_token_ids)
        self.episode_prompt_len = episode_prompt_len
        self.gross_offset = gross_offset
        self.ch_open_id = ch_open_id
        self.ch_close_id = ch_close_id
        self.tc_open_id = tc_open_id
        self.tc_close_id = tc_close_id
        self.K = K
        self.think_budget = think_budget
        self.W = W
        self.ur_min = ur_min
        self.observe_only = observe_only

        self.segment_start_len: Optional[int] = None
        self.n_ch_open = 0
        self.n_ch_close = 0
        self.current_thought_age = 0
        self.n_tc_open = 0
        self.n_tc_close = 0

        self.since_progress = 0
        self.step_counter = 0
        self.fired = False
        self.trigger_type: Optional[str] = None
        self.loop_rel_start: Optional[int] = None
        self.would_fire_events: List[Dict[str, Any]] = []

    def _init_prefix_state(self, prefix_gen_ids: List[int]) -> None:
        """Inicializa contadores uma única vez por segmento (evita O(L^2) por token)."""
        for tid in prefix_gen_ids:
            self._advance_token_state(tid)

    def _advance_token_state(self, tok_id: int) -> None:
        if self.ch_open_id is not None and tok_id == self.ch_open_id:
            self.n_ch_open += 1
            self.current_thought_age = 1
        elif self.ch_close_id is not None and tok_id == self.ch_close_id:
            self.n_ch_close = min(self.n_ch_open, self.n_ch_close + 1)
            if self.n_ch_open == self.n_ch_close:
                self.current_thought_age = 0
        elif self.n_ch_open > self.n_ch_close:
            self.current_thought_age += 1

        if self.tc_open_id is not None and tok_id == self.tc_open_id:
            self.n_tc_open += 1
        elif self.tc_close_id is not None and tok_id == self.tc_close_id:
            self.n_tc_close = min(self.n_tc_open, self.n_tc_close + 1)

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        if self.segment_start_len is None:
            self.segment_start_len = int(input_ids.shape[1]) - 1
            if self.segment_start_len > self.episode_prompt_len:
                prior = input_ids[0][self.episode_prompt_len : self.segment_start_len].tolist()
                self._init_prefix_state(prior)

        seg_gen = input_ids[0][self.segment_start_len :]
        seg_len = int(seg_gen.shape[0])
        if seg_len == 0:
            return False

        self.step_counter += 1
        last_tok = int(seg_gen[-1])
        self._advance_token_state(last_tok)

        in_thought = (
            self.ch_open_id is not None
            and self.ch_close_id is not None
            and (self.n_ch_open > self.n_ch_close)
        )
        in_tool_call = (
            self.tc_open_id is not None
            and self.tc_close_id is not None
            and (self.n_tc_open > self.n_tc_close)
        )

        # Checa progresso na zona visível fora de pensamento e fora de corpo tool_call JSON
        if (not in_thought) and (not in_tool_call):
            if last_tok in self.tool_ids:
                self.since_progress = 0
            elif self.step_counter % 4 == 0:
                recent_txt = self.tok.decode(seg_gen[-24:], skip_special_tokens=False)
                if any(m in recent_txt for m in PROGRESS_TEXT_MARKERS):
                    self.since_progress = 0
                else:
                    self.since_progress += 4
        else:
            self.since_progress = 0

        ttype: Optional[str] = None
        loop_start: Optional[int] = None

        # 1. Detector de repetição (ativo em qualquer zona a cada 4 passos quando seg_len >= 24)
        if self.step_counter % 4 == 0 and seg_len >= 24:
            tail_w = seg_gen[-min(seg_len, self.W) :].tolist()
            ng_pos = has_repeated_ngram(tail_w, n=8, min_repeats=3)
            if ng_pos is not None:
                ttype = "think_repetition" if in_thought else "repetition"
                loop_start = max(0, seg_len - len(tail_w) + ng_pos)
            elif seg_len >= self.W:
                ur = len(set(tail_w)) / float(len(tail_w))
                if ur < self.ur_min:
                    ttype = "think_repetition" if in_thought else "repetition"
                    loop_start = max(0, seg_len - self.W // 2)

        # 2. Orçamento máximo do canal de pensamento ou stall pós-pensamento
        if ttype is None:
            if in_thought and self.think_budget > 0 and self.current_thought_age >= self.think_budget:
                ttype = "think_budget_cap"
            elif (not in_thought) and (not in_tool_call) and self.K > 0 and self.since_progress >= self.K:
                ttype = "k_no_progress"

        if ttype is None:
            return False

        gross_pos = self.gross_offset + seg_len
        if self.observe_only:
            if not self.would_fire_events or (gross_pos - self.would_fire_events[-1]["token_pos"] >= 64):
                self.would_fire_events.append(
                    {
                        "restart_idx": 0,
                        "trigger_type": f"would_fire:{ttype}",
                        "token_pos": gross_pos,
                        "cut_tokens": 0,
                        "purged_preview": None,
                        "last_progress": "observe_only",
                        "context_ref": "in_thought" if in_thought else "visible",
                        "temp_before": 0.7,
                        "temp_after": 0.7,
                        "frame_text": "",
                        "timestamp_utc": utc_now_iso(),
                    }
                )
            self.since_progress = 0
            return False

        self.fired = True
        self.trigger_type = ttype
        self.loop_rel_start = loop_start
        return True


def extract_last_action_symbolic(text: str) -> Tuple[str, str]:
    """
    Extrai o alias simbólico do ato MAIS RECENTE (varredura reversa — P1-18 corrigido,
    sem nunca injetar literal 'diff --git' no frame) e contexto arquivo:linha.
    """
    clean = sanitize_scaffold_text(text)
    last_act = "none"
    best_pos = -1
    for marker in PROGRESS_TEXT_MARKERS:
        pos = clean.rfind(marker)
        if pos > best_pos:
            best_pos = pos
            last_act = MARKER_SYMBOLIC_ALIASES.get(marker, "code_marker")

    ctx_ref = "n/a"
    for line in reversed(clean.splitlines()):
        if any(ext in line for ext in (".py", ".ts", ".js", ".go", ".rs", ".java", ".toml", ".cfg")):
            stripped = line.strip().lstrip("+- ").replace("diff --git", "").strip()
            if stripped:
                ctx_ref = stripped[:60]
                break
    return last_act, ctx_ref


def build_cascade_frame_v2(
    mode: str,
    last_act: str,
    ctx_ref: str,
    remaining_tokens: int,
) -> str:
    """Frame livre de marcadores de patch para reorientação metacognitiva."""
    tag = "SESSION_CUT" if mode == "hard_cut" else "CASCADE_FRAME"
    return (
        f"\n[{tag}] Strategy checkpoint (last_state={last_act}, target={ctx_ref}, "
        f"remaining_budget=~{remaining_tokens} tok). Stop repeating; emit the final solution/patch directly.\n"
        f"Action:\n"
    )


# ============================================================================
# Onda 2: Resolutor 48 Camadas, Bipartição MPS (64x60) & Hooks GPU-Zero-Sync
# ============================================================================
def resolve_decoder_layers(model) -> torch.nn.ModuleList:
    """
    Localiza as 48 camadas de texto em `Gemma4UnifiedForConditionalGeneration` / CausalLM.
    Verificado em `hf_device_map` (transformers 5.22.1): `model.language_model.layers.0..47`.
    """
    candidates = [
        ("model", "language_model", "layers"),
        ("language_model", "layers"),
        ("model", "layers"),
        ("layers",),
    ]
    for path in candidates:
        curr = model
        ok = True
        for attr in path:
            if hasattr(curr, attr):
                curr = getattr(curr, attr)
            else:
                ok = False
                break
        if ok and isinstance(curr, (torch.nn.ModuleList, list)) and len(curr) >= 24:
            return curr

    indexed: Dict[int, torch.nn.Module] = {}
    for name, mod in model.named_modules():
        m = re.search(r"(?:language_model\.|model\.)?layers\.(\d+)$", name)
        if m:
            indexed[int(m.group(1))] = mod
    if indexed:
        ordered = [indexed[i] for i in sorted(indexed.keys())]
        return torch.nn.ModuleList(ordered)

    raise RuntimeError("Não foi possível localizar `layers` (48 camadas) na estrutura do modelo.")


def compute_bipartite_mps_64x60(x_fp32: torch.Tensor) -> Tuple[float, float, float]:
    """
    Bipartição Central Exata do estado oculto h in R^3840 -> M in R^(64 x 60).
    Espectro de Schmidt exato com rank máximo chi_max = 60.
    Retorna: (chi_eff in [1, 60], S_vN in [0, ln(60)], top1_schmidt_weight in [0, 1]).
    """
    D = int(x_fp32.numel())
    if D == 3840:
        rows, cols = 64, 60
    else:
        rows = int(math.isqrt(D))
        while rows > 1 and (D % rows != 0):
            rows -= 1
        cols = D // rows
        if rows == 1:
            half = (D // 2) * 2
            x_fp32 = x_fp32[:half]
            rows, cols = 2, half // 2

    M = x_fp32.reshape(rows, cols)
    s = torch.linalg.svdvals(M)
    s2 = s * s
    total = float(s2.sum().item())
    if total <= 1e-12 or not math.isfinite(total):
        return 1.0, 0.0, 1.0

    q = s2 / total
    q_pos = q[q > 1e-12]
    svn = float(-(q_pos * torch.log(q_pos)).sum().item())
    chi_eff = float(math.exp(svn))
    top1 = float(q[0].item())
    return round(chi_eff, 4), round(svn, 4), round(top1, 4)


def compute_trajectory_gram_metrics(
    buf_fp32: torch.Tensor,
    need_top_vector: bool = False,
) -> Tuple[float, float, float, Optional[torch.Tensor], Optional[torch.Tensor]]:
    """
    Calcula métricas espectrais da janela temporal centralizada H_tilde in R^(W x D)
    via matriz de Gram simétrica G = H_tilde @ H_tilde^T in R^(W x W).
    Se need_top_vector=True: extrai o vetor singular direito dominante exato u_1 in R^D.
    """
    mean_vec = buf_fp32.mean(dim=0, keepdim=True)
    H_tilde = buf_fp32 - mean_vec
    G = H_tilde @ H_tilde.transpose(0, 1)

    if need_top_vector:
        evals, evecs = torch.linalg.eigh(G)
    else:
        evals = torch.linalg.eigvalsh(G)
        evecs = None

    evals = torch.clamp(evals, min=0.0)
    etot = float(evals.sum().item())
    if etot <= 1e-8 or not math.isfinite(etot):
        return 1.0, 1.0, 0.0, None, mean_vec.squeeze(0)

    sum_sq = float((evals * evals).sum().item())
    pr_traj = (etot * etot) / max(sum_sq, 1e-12)
    lambda_max = float(evals[-1].item())
    gamma1 = lambda_max / etot

    p = evals / etot
    p_pos = p[p > 1e-12]
    svd_ent = float(-(p_pos * torch.log(p_pos)).sum().item())

    u1 = None
    if need_top_vector and evecs is not None and lambda_max > 1e-8:
        w1 = evecs[:, -1]
        raw_u1 = H_tilde.transpose(0, 1) @ w1
        u1_norm = torch.linalg.vector_norm(raw_u1)
        if float(u1_norm.item()) > 1e-8:
            u1 = raw_u1 / u1_norm

    return round(pr_traj, 4), round(gamma1, 4), round(svd_ent, 4), u1, mean_vec.squeeze(0)


class LayerHookState:
    """
    Estado isolado por camada durante um episódio:
      - Zero `.cpu()` / `.item()` nos passos intermediários fora do tick `stride` (P1-3 corrigido).
      - Na Opção 2 (`opt2_spectral`), a deflação atua alinhada exatamente ao tick de avaliação
        (`is_eval_tick`), evitando deflação composta de 94% com `u_1` defasado (P1-2 corrigido).
    """

    def __init__(
        self,
        layer_idx: int,
        mode: str,
        W: int = 16,
        stride: int = 4,
        steer_vec_np: Optional[np.ndarray] = None,
        tau_pr: float = 2.20,
        alpha_steer: float = 0.05,
        beta_spectral: float = 0.50,
        gamma1_thresh: float = 0.80,
        collect_calib: bool = False,
    ):
        self.layer_idx = layer_idx
        self.mode = mode  # 'passive' | 'opt1_steering' | 'opt2_spectral'
        self.W = W
        # Em opt2_spectral usamos stride=2 p/ medição+ato acoplados com alta responsividade
        self.stride = 2 if mode == "opt2_spectral" else stride
        self.tau_pr = tau_pr
        self.alpha_steer = alpha_steer
        self.beta_spectral = beta_spectral
        self.gamma1_thresh = gamma1_thresh
        self.collect_calib = collect_calib

        self.steer_vec_cpu = (
            torch.from_numpy(steer_vec_np.astype(np.float32))
            if steer_vec_np is not None
            else None
        )
        self.steer_vec_dev: Optional[torch.Tensor] = None

        self.ring_buf: Optional[torch.Tensor] = None
        self.ring_count = 0
        self.ring_ptr = 0
        self.decode_steps = 0
        self.hook_fired_count = 0

        self.last_pr = float(W)
        self.last_gamma1 = 1.0 / float(W)
        self.last_svd_ent = math.log(W)
        self.last_u1: Optional[torch.Tensor] = None
        self.last_mean: Optional[torch.Tensor] = None
        self.pr_history: List[float] = []

        self.checkpoints: List[Dict[str, Any]] = []
        self.calib_pos_sum: Optional[np.ndarray] = None
        self.calib_pos_n = 0
        self.calib_pos_prs: List[float] = []
        self.calib_neg_sum: Optional[np.ndarray] = None
        self.calib_neg_n = 0
        self.calib_neg_prs: List[float] = []
        self.calib_mid_reservoir: List[Tuple[float, np.ndarray]] = []
        self.last_decode_x_dev: Optional[torch.Tensor] = None

    def _push_ring(self, x_fp32: torch.Tensor) -> None:
        D = x_fp32.shape[-1]
        if self.ring_buf is None or self.ring_buf.device != x_fp32.device:
            self.ring_buf = torch.zeros((self.W, D), dtype=torch.float32, device=x_fp32.device)
            self.ring_count = 0
            self.ring_ptr = 0
        self.ring_buf[self.ring_ptr].copy_(x_fp32)
        self.ring_ptr = (self.ring_ptr + 1) % self.W
        self.ring_count = min(self.W, self.ring_count + 1)

    def _ordered_window(self) -> torch.Tensor:
        if self.ring_count < self.W:
            return self.ring_buf[: self.ring_count]
        if self.ring_ptr == 0:
            return self.ring_buf
        return torch.cat([self.ring_buf[self.ring_ptr :], self.ring_buf[: self.ring_ptr]], dim=0)

    def hook_fn(self, module: torch.nn.Module, inputs: Any, output: Any) -> Any:
        is_tuple = isinstance(output, tuple)
        h = output[0] if is_tuple else output
        if not isinstance(h, torch.Tensor) or h.ndim != 3 or h.shape[1] == 0:
            return output

        seq_len = int(h.shape[1])
        x_fp32 = h[0, -1, :].detach().to(torch.float32)

        # Passo 0: Prefill do prompt
        if seq_len > 1:
            if not self.checkpoints:
                h_norm = float(torch.linalg.vector_norm(x_fp32).item())
                chi_eff, svn, top1_sch = compute_bipartite_mps_64x60(x_fp32)
                self.checkpoints.append(
                    {
                        "layer_idx": self.layer_idx,
                        "phase": "prefill_last",
                        "token_pos": 0,
                        "pr_traj": None,
                        "top1_energy_ratio": None,
                        "svd_entropy_traj": None,
                        "mps_chi_eff": chi_eff,
                        "mps_svn": svn,
                        "mps_top1_schmidt": top1_sch,
                        "h_norm": round(h_norm, 3),
                        "hook_fired_count": 0,
                    }
                )
            self._push_ring(x_fp32)
            return output

        # Passo Autoregressivo (seq_len == 1) — zero sync CPU fora de ticks!
        self.decode_steps += 1
        self._push_ring(x_fp32)
        self.last_decode_x_dev = x_fp32

        is_eval_tick = (self.ring_count >= self.W) and (self.decode_steps % self.stride == 0)
        if is_eval_tick:
            win = self._ordered_window()
            pr, gamma1, svd_ent, u1, mean_v = compute_trajectory_gram_metrics(
                win, need_top_vector=(self.mode == "opt2_spectral")
            )
            self.last_pr = pr
            self.last_gamma1 = gamma1
            self.last_svd_ent = svd_ent
            self.last_u1 = u1
            self.last_mean = mean_v
            self.pr_history.append(pr)

            if self.collect_calib and (self.decode_steps % 8 == 0):
                h_norm_val = float(torch.linalg.vector_norm(x_fp32).item())
                if h_norm_val > 1e-6:
                    unit_np = (x_fp32 / h_norm_val).cpu().numpy().astype(np.float64)
                    if self.calib_pos_sum is None:
                        self.calib_pos_sum = np.zeros_like(unit_np)
                        self.calib_neg_sum = np.zeros_like(unit_np)
                    if pr >= 3.20:
                        self.calib_pos_sum += unit_np
                        self.calib_pos_n += 1
                        self.calib_pos_prs.append(pr)
                    elif pr <= 2.20:
                        self.calib_neg_sum += unit_np
                        self.calib_neg_n += 1
                        self.calib_neg_prs.append(pr)
                    elif len(self.calib_mid_reservoir) < 64:
                        self.calib_mid_reservoir.append((pr, unit_np))

        if self.decode_steps == 256:
            h_norm = float(torch.linalg.vector_norm(x_fp32).item())
            chi_eff, svn, top1_sch = compute_bipartite_mps_64x60(x_fp32)
            self.checkpoints.append(
                {
                    "layer_idx": self.layer_idx,
                    "phase": "mid_gen_256",
                    "token_pos": 256,
                    "pr_traj": self.last_pr if self.ring_count >= self.W else None,
                    "top1_energy_ratio": self.last_gamma1 if self.ring_count >= self.W else None,
                    "svd_entropy_traj": self.last_svd_ent if self.ring_count >= self.W else None,
                    "mps_chi_eff": chi_eff,
                    "mps_svn": svn,
                    "mps_top1_schmidt": top1_sch,
                    "h_norm": round(h_norm, 3),
                    "hook_fired_count": self.hook_fired_count,
                }
            )

        if self.ring_count < self.W or self.mode == "passive":
            return output

        # Intervenções 100% em tensores GPU (apenas 1 check isfinite no final)
        x_mod: Optional[torch.Tensor] = None

        if self.mode == "opt1_steering" and self.steer_vec_cpu is not None:
            if self.last_pr < self.tau_pr:
                if self.steer_vec_dev is None or self.steer_vec_dev.device != h.device:
                    self.steer_vec_dev = self.steer_vec_cpu.to(device=h.device, dtype=torch.float32)
                h_norm_t = torch.linalg.vector_norm(x_fp32)
                cand = x_fp32 + (self.alpha_steer * h_norm_t) * self.steer_vec_dev
                cand_norm_t = torch.clamp(torch.linalg.vector_norm(cand), min=1e-6)
                x_mod = cand * (h_norm_t / cand_norm_t)

        elif self.mode == "opt2_spectral":
            # Atua exatamente no tick de medição fresca `is_eval_tick` (sem deflação composta stale — P1-2)
            if is_eval_tick and (self.last_gamma1 > self.gamma1_thresh or self.last_pr < 2.0) and self.last_u1 is not None:
                h_norm_t = torch.linalg.vector_norm(x_fp32)
                mean_ref = self.last_mean if self.last_mean is not None else torch.zeros_like(x_fp32)
                delta = x_fp32 - mean_ref
                proj = torch.dot(delta, self.last_u1)
                cand = x_fp32 - (self.beta_spectral * proj) * self.last_u1
                cand_norm_t = torch.clamp(torch.linalg.vector_norm(cand), min=1e-6)
                x_mod = cand * (h_norm_t / cand_norm_t)

        if x_mod is None:
            return output

        x_cast = x_mod.to(dtype=h.dtype)
        if not bool(torch.isfinite(x_cast).all().item()):
            return output

        self.hook_fired_count += 1
        h_out = h.clone()
        h_out[0, -1, :] = x_cast
        return (h_out,) + output[1:] if is_tuple else h_out

    def extract_episode_loto_accumulator(self, hidden_dim: int = 3840) -> Dict[str, Any]:
        """Extrai somas suficientes (pos/neg) do episódio p/ persistência transacional SQLite (P0-1a)."""
        pos_sum = self.calib_pos_sum.copy() if self.calib_pos_sum is not None else np.zeros(hidden_dim, dtype=np.float64)
        pos_n = self.calib_pos_n
        pos_pr_sum = float(np.sum(self.calib_pos_prs)) if self.calib_pos_prs else 0.0

        neg_sum = self.calib_neg_sum.copy() if self.calib_neg_sum is not None else np.zeros(hidden_dim, dtype=np.float64)
        neg_n = self.calib_neg_n
        neg_pr_sum = float(np.sum(self.calib_neg_prs)) if self.calib_neg_prs else 0.0

        # Se este episódio teve poucas janelas extremas, complementa com quantis superior/inferior do episódio
        if (pos_n == 0 or neg_n == 0) and len(self.calib_mid_reservoir) >= 4:
            ordered = sorted(self.calib_mid_reservoir, key=lambda item: item[0])
            k_q = max(1, len(ordered) // 4)
            if neg_n == 0:
                for pr_v, v_np in ordered[:k_q]:
                    neg_sum += v_np
                    neg_n += 1
                    neg_pr_sum += float(pr_v)
            if pos_n == 0:
                for pr_v, v_np in ordered[-k_q:]:
                    pos_sum += v_np
                    pos_n += 1
                    pos_pr_sum += float(pr_v)

        return {
            "layer_idx": self.layer_idx,
            "pos_n": pos_n,
            "pos_pr_sum": pos_pr_sum,
            "pos_sum_blob": pos_sum.astype(np.float64).tobytes(),
            "neg_n": neg_n,
            "neg_pr_sum": neg_pr_sum,
            "neg_sum_blob": neg_sum.astype(np.float64).tobytes(),
        }

    def finalize_episode_checkpoints(self) -> List[Dict[str, Any]]:
        if self.last_decode_x_dev is not None:
            x_cpu = self.last_decode_x_dev.detach().cpu()
            chi_eff, svn, top1_sch = compute_bipartite_mps_64x60(x_cpu)
            h_norm = float(torch.linalg.vector_norm(x_cpu).item())
            mean_pr = round(float(np.mean(self.pr_history)), 4) if self.pr_history else None
            self.checkpoints.append(
                {
                    "layer_idx": self.layer_idx,
                    "phase": "episode_end",
                    "token_pos": self.decode_steps,
                    "pr_traj": mean_pr,
                    "top1_energy_ratio": self.last_gamma1 if self.pr_history else None,
                    "svd_entropy_traj": self.last_svd_ent if self.pr_history else None,
                    "mps_chi_eff": chi_eff,
                    "mps_svn": svn,
                    "mps_top1_schmidt": top1_sch,
                    "h_norm": round(h_norm, 3),
                    "hook_fired_count": self.hook_fired_count,
                }
            )
        return self.checkpoints


def rebuild_and_persist_loto_from_db(
    conn: sqlite3.Connection,
    run_id: str,
    layers: Tuple[int, ...] = CANONICAL_48_LAYERS,
    hidden_dim: int = 3840,
) -> int:
    """
    Reconstrói os vetores LOTO diretamente da tabela SQLite `loto_episode_accumulators` (P0-1a):
      - 100% resiliente a múltiplos restarts/sessões Kaggle (nunca perde episódios anteriores).
      - Guarda estrita anti-vazamento: para cada `held_out_task`, agrega SOMENTE `task_id != held_out_task`
        e exige `len(src_tasks) >= 1` (se houver apenas 1 task total no banco, NÃO grava vetor por-task,
        eliminando matematicamente o risco de leave-one-IN!).
    """
    rows = conn.execute(
        """
        SELECT task_id, layer_idx, pos_n, pos_pr_sum, pos_sum_blob, neg_n, neg_pr_sum, neg_sum_blob
        FROM loto_episode_accumulators
        """
    ).fetchall()
    if not rows:
        return 0

    by_task_layer: Dict[str, Dict[int, Dict[str, Any]]] = {}
    for task_id, l_idx, p_n, p_pr_s, p_blob, n_n, n_pr_s, n_blob in rows:
        p_vec = np.frombuffer(p_blob, dtype=np.float64)
        n_vec = np.frombuffer(n_blob, dtype=np.float64)
        if p_vec.shape[0] != hidden_dim or n_vec.shape[0] != hidden_dim:
            continue
        tmap = by_task_layer.setdefault(task_id, {})
        acc = tmap.setdefault(
            int(l_idx),
            {
                "pos_sum": np.zeros(hidden_dim, dtype=np.float64),
                "pos_n": 0,
                "pos_pr_sum": 0.0,
                "neg_sum": np.zeros(hidden_dim, dtype=np.float64),
                "neg_n": 0,
                "neg_pr_sum": 0.0,
            },
        )
        acc["pos_sum"] += p_vec
        acc["pos_n"] += int(p_n)
        acc["pos_pr_sum"] += float(p_pr_s)
        acc["neg_sum"] += n_vec
        acc["neg_n"] += int(n_n)
        acc["neg_pr_sum"] += float(n_pr_s)

    tasks = sorted(by_task_layer.keys())
    targets: List[str] = ["__GLOBAL__"]
    if len(tasks) >= 2:
        targets = tasks + ["__GLOBAL__"]
    else:
        log_budget_event(
            conn,
            "loto_partial_warn",
            f"Apenas {len(tasks)} task(s) com acumuladores ({tasks}); vetores por-task retidos p/ impedir leave-one-in.",
        )

    saved = 0
    for held_out in targets:
        src_tasks = [t for t in tasks if t != held_out] if held_out != "__GLOBAL__" else tasks
        if not src_tasks:
            continue
        for l_idx in layers:
            pos_sum = np.zeros(hidden_dim, dtype=np.float64)
            pos_n = 0
            pos_pr_sum = 0.0
            neg_sum = np.zeros(hidden_dim, dtype=np.float64)
            neg_n = 0
            neg_pr_sum = 0.0

            for stask in src_tasks:
                e = by_task_layer.get(stask, {}).get(l_idx)
                if not e:
                    continue
                pos_sum += e["pos_sum"]
                pos_n += e["pos_n"]
                pos_pr_sum += e["pos_pr_sum"]
                neg_sum += e["neg_sum"]
                neg_n += e["neg_n"]
                neg_pr_sum += e["neg_pr_sum"]

            if pos_n == 0 or neg_n == 0:
                continue

            mu_pos = pos_sum / float(pos_n)
            mu_neg = neg_sum / float(neg_n)
            delta = mu_pos - mu_neg
            dnorm = float(np.linalg.norm(delta))
            if dnorm <= 1e-8:
                continue

            v_unit = (delta / dnorm).astype(np.float32)
            pos_pr_m = pos_pr_sum / float(pos_n)
            neg_pr_m = neg_pr_sum / float(neg_n)
            tau_pr = float(np.clip(0.5 * (pos_pr_m + neg_pr_m), 1.75, 3.10))

            conn.execute(
                """
                INSERT OR REPLACE INTO steering_calibration (
                    run_id, held_out_task, n_source_tasks, layer_idx,
                    n_pos_windows, n_neg_windows, pos_pr_mean, neg_pr_mean,
                    delta_norm, tau_pr_threshold, vector_blob, timestamp_utc
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    held_out,
                    len(src_tasks),
                    l_idx,
                    pos_n,
                    neg_n,
                    round(pos_pr_m, 4),
                    round(neg_pr_m, 4),
                    round(dnorm, 5),
                    round(tau_pr, 4),
                    v_unit.tobytes(),
                    utc_now_iso(),
                ),
            )
            saved += 1
    conn.commit()
    return saved


def load_steering_for_task(
    conn: sqlite3.Connection,
    task_id: str,
    layers: Tuple[int, ...] = INTERVENTION_HUB_LAYERS,
    hidden_dim: int = 3840,
) -> Tuple[Dict[int, Tuple[np.ndarray, float]], str]:
    """
    Carrega vetores LOTO estritos (`held_out_task == task_id` com `n_source_tasks >= 1`) do SQLite.
    NÃO faz fallback silencioso para `__GLOBAL__` (elimina circularidade P1-1!).
    """
    out: Dict[int, Tuple[np.ndarray, float]] = {}
    min_src = 999
    for l_idx in layers:
        row = conn.execute(
            """
            SELECT vector_blob, tau_pr_threshold, n_source_tasks
            FROM steering_calibration
            WHERE held_out_task=? AND layer_idx=?
            """,
            (task_id, l_idx),
        ).fetchone()
        if row is not None:
            vec = np.frombuffer(row[0], dtype=np.float32).copy()
            if vec.shape[0] == hidden_dim:
                out[l_idx] = (vec, float(row[1]))
                min_src = min(min_src, int(row[2] or 0))
    source_tag = f"loto_strict(src_tasks={min_src})" if out else "missing"
    return out, source_tag


# ============================================================================
# Executor Central de Episódio
# ============================================================================
def run_episode_v2(
    model,
    tokenizer,
    prompt_ids: torch.Tensor,
    arm: str,
    cfg: Dict[str, Any],
    decoder_layers: Optional[torch.nn.ModuleList] = None,
    hook_mode: Optional[str] = None,
    steering_map: Optional[Dict[int, Tuple[np.ndarray, float]]] = None,
    collect_calib: bool = False,
) -> Dict[str, Any]:
    current_ids = prompt_ids
    prompt_len = int(prompt_ids.shape[1])

    is_cascade_soft = "cascade_soft" in arm or arm == "nf4_cascade"
    is_cascade_hard = "cascade_hard" in arm
    observe_only = not (is_cascade_soft or is_cascade_hard)

    ch_open_id = cfg.get("ch_open_id")
    ch_close_id = cfg.get("ch_close_id")
    tc_open_id = cfg.get("tc_open_id")
    tc_close_id = cfg.get("tc_close_id")
    nl_token_ids = set(tokenizer.encode("\n", add_special_tokens=False))
    hidden_dim = cfg.get("hidden_dim", 3840)

    gross_generated = 0
    cut_tokens_purged = 0
    restarts = 0
    events: List[Dict[str, Any]] = []
    temp = cfg["temp"]
    top_p = cfg["top_p"]
    finish_reason = "eos"

    handles = []
    hook_states: Dict[int, LayerHookState] = {}
    if decoder_layers is not None and hook_mode in ("passive", "opt1_steering", "opt2_spectral"):
        n_layers_model = len(decoder_layers)
        for l_idx in CANONICAL_48_LAYERS:
            if l_idx >= n_layers_model:
                continue
            active_mode = (
                hook_mode
                if (hook_mode in ("opt1_steering", "opt2_spectral") and l_idx in INTERVENTION_HUB_LAYERS)
                else "passive"
            )
            s_vec, tau_val = (None, 2.20)
            if active_mode == "opt1_steering" and steering_map and l_idx in steering_map:
                s_vec, tau_val = steering_map[l_idx]
            st = LayerHookState(
                layer_idx=l_idx,
                mode=active_mode,
                W=cfg.get("latent_W", 16),
                stride=cfg.get("latent_stride", 4),
                steer_vec_np=s_vec,
                tau_pr=tau_val,
                alpha_steer=cfg.get("alpha_steer", 0.05),
                beta_spectral=cfg.get("beta_spectral", 0.50),
                gamma1_thresh=cfg.get("gamma1_thresh", 0.80),
                collect_calib=collect_calib,
            )
            hook_states[l_idx] = st
            handles.append(decoder_layers[l_idx].register_forward_hook(st.hook_fn))

    try:
        while gross_generated < cfg["max_new_tokens"]:
            remaining = cfg["max_new_tokens"] - gross_generated
            if remaining <= 0:
                finish_reason = "cap"
                break

            trig = VaciloTriggerV2(
                tokenizer=tokenizer,
                tool_token_ids=cfg["tool_token_ids"],
                episode_prompt_len=prompt_len,
                gross_offset=gross_generated,
                ch_open_id=ch_open_id,
                ch_close_id=ch_close_id,
                tc_open_id=tc_open_id,
                tc_close_id=tc_close_id,
                K=cfg["K"],
                think_budget=cfg["think_budget"],
                W=cfg["W"],
                ur_min=cfg["ur_min"],
                observe_only=observe_only,
            )

            seg_before_len = int(current_ids.shape[1])
            with torch.no_grad():
                out = model.generate(
                    current_ids,
                    max_new_tokens=remaining,
                    do_sample=True,
                    temperature=temp,
                    top_p=top_p,
                    top_k=cfg["top_k"],
                    stopping_criteria=StoppingCriteriaList([trig]),
                    pad_token_id=tokenizer.eos_token_id,
                    return_dict_in_generate=True,
                )

            gen_seg = out.sequences[0][seg_before_len:]
            seg_len = int(gen_seg.shape[0])
            gross_generated += seg_len
            current_ids = out.sequences
            events.extend(trig.would_fire_events)

            if not trig.fired:
                finish_reason = "cap" if gross_generated >= cfg["max_new_tokens"] else "eos"
                break

            if restarts >= cfg["max_restarts"]:
                finish_reason = "restart_cap"
                break

            restarts += 1
            n_cut = 0
            purged_preview: Optional[str] = None

            # Opção 3B: Hard Context Truncation + registro forense `purged_preview` (P1-7)
            if is_cascade_hard and seg_len > 12:
                if trig.trigger_type in ("repetition", "think_repetition"):
                    if trig.loop_rel_start is not None:
                        raw_cut = seg_len - trig.loop_rel_start
                    else:
                        raw_cut = min(seg_len - 8, cfg["W"])
                    n_cut = max(8, min(seg_len - 4, raw_cut))
                elif trig.trigger_type == "think_budget_cap":
                    tail_check = gen_seg[-min(32, seg_len) :].tolist()
                    found_nl = False
                    for back_i in range(len(tail_check) - 1, -1, -1):
                        if tail_check[back_i] in nl_token_ids:
                            n_cut = len(tail_check) - 1 - back_i
                            found_nl = True
                            break
                    if not found_nl or n_cut == 0:
                        n_cut = min(24, seg_len // 4)
                elif trig.trigger_type == "k_no_progress":
                    n_cut = min(seg_len // 2, 80)

                max_safe_cut = int(current_ids.shape[1]) - prompt_len - 4
                n_cut = max(0, min(n_cut, max_safe_cut))
                if n_cut > 0:
                    purged_ids = current_ids[0, -n_cut:].tolist()
                    purged_txt = tokenizer.decode(purged_ids, skip_special_tokens=False)
                    p_sha = hashlib.sha256(purged_txt.encode("utf-8", errors="ignore")).hexdigest()[:12]
                    purged_preview = f"sha={p_sha}|len={n_cut}|head={purged_txt[:80]!r}|tail={purged_txt[-80:]!r}"
                    current_ids = current_ids[:, :-n_cut]
                    cut_tokens_purged += n_cut

            surviving_ep_ids = current_ids[0][prompt_len:].tolist()
            decoded_surviving = tokenizer.decode(surviving_ep_ids, skip_special_tokens=False)
            last_act, ctx_ref = extract_last_action_symbolic(decoded_surviving)
            rem_after = max(0, cfg["max_new_tokens"] - gross_generated)
            frame_mode = "hard_cut" if is_cascade_hard else "soft"
            frame_text = build_cascade_frame_v2(frame_mode, last_act, ctx_ref, rem_after)

            prefix_close_ids: List[int] = []
            if (
                ch_open_id is not None
                and ch_close_id is not None
                and surviving_ep_ids.count(ch_open_id) > surviving_ep_ids.count(ch_close_id)
            ):
                prefix_close_ids = [ch_close_id]

            frame_token_list = prefix_close_ids + tokenizer.encode(frame_text, add_special_tokens=False)
            frame_tensor = torch.tensor([frame_token_list], dtype=torch.long, device=current_ids.device)
            current_ids = torch.cat([current_ids, frame_tensor], dim=1)

            events.append(
                {
                    "restart_idx": restarts,
                    "trigger_type": trig.trigger_type or "unknown",
                    "token_pos": gross_generated,
                    "cut_tokens": n_cut,
                    "purged_preview": purged_preview,
                    "last_progress": last_act,
                    "context_ref": ctx_ref,
                    "temp_before": temp,
                    "temp_after": cfg["cascade_temp"],
                    "frame_text": ("<channel|>" if prefix_close_ids else "") + frame_text,
                    "timestamp_utc": utc_now_iso(),
                }
            )

            temp = cfg["cascade_temp"]
            top_p = cfg["cascade_top_p"]

    finally:
        for h in handles:
            h.remove()

    latent_rows: List[Dict[str, Any]] = []
    loto_acc_rows: List[Dict[str, Any]] = []
    total_hook_fires = 0
    for l_idx in sorted(hook_states.keys()):
        st = hook_states[l_idx]
        total_hook_fires += st.hook_fired_count
        latent_rows.extend(st.finalize_episode_checkpoints())
        if collect_calib:
            loto_acc_rows.append(st.extract_episode_loto_accumulator(hidden_dim=hidden_dim))

    return {
        "final_ids": current_ids[0][prompt_len:],
        "gross_generated": gross_generated,
        "cut_tokens_purged": cut_tokens_purged,
        "restarts": restarts,
        "finish_reason": finish_reason,
        "events": events,
        "latent_rows": latent_rows,
        "loto_acc_rows": loto_acc_rows,
        "total_hook_fires": total_hook_fires,
    }


# ============================================================================
# Persistência Transacional Atômica de Episódio (Inclui Acumuladores LOTO!)
# ============================================================================
def persist_episode_result(
    conn: sqlite3.Connection,
    run_id: str,
    experiment: str,
    arm: str,
    ledger_task_key: str,
    task_id: str,
    task_phase: str,
    rep_idx: int,
    prompt_tokens: int,
    ep_res: Dict[str, Any],
    parsed: Dict[str, Any],
    latency: float,
    seed: int,
    enable_thinking: bool,
    steering_source: Optional[str] = None,
) -> int:
    gross_gen = ep_res["gross_generated"]
    tok_s = round(gross_gen / latency, 2) if latency > 0 else 0.0
    n_would_fire = sum(1 for e in ep_res["events"] if str(e.get("trigger_type", "")).startswith("would_fire:"))

    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO generation_records (
            run_id, experiment, arm, task_id, task_phase, rep_idx,
            prompt_tokens, generated_tokens, n_cascade_restarts, n_would_fire,
            latency_seconds, tokens_per_s, visible_response, thinking_trace,
            finish_reason, degenerate_flag, unique_ratio, tool_calls_n,
            progress_events_n, seed, timestamp_utc,
            enable_thinking, thinking_tokens, visible_tokens, thought_closed,
            ur_thinking, ur_visible, ur_sanitized, degen_sanitized,
            cut_tokens_purged, n_hook_interventions, steering_source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            experiment,
            arm,
            task_id,
            task_phase,
            rep_idx,
            prompt_tokens,
            gross_gen,
            ep_res["restarts"],
            n_would_fire,
            latency,
            tok_s,
            parsed["visible_response"],
            parsed["thinking_trace"],
            ep_res["finish_reason"],
            parsed["degenerate_flag"],
            parsed["unique_ratio"],
            parsed["tool_calls_n"],
            parsed["has_patch"],
            seed,
            utc_now_iso(),
            1 if enable_thinking else 0,
            parsed["thinking_tokens"],
            parsed["visible_tokens"],
            parsed["thought_closed"],
            parsed["ur_thinking"],
            parsed["ur_visible"],
            parsed["ur_sanitized"],
            parsed["degen_sanitized"],
            ep_res["cut_tokens_purged"],
            ep_res["total_hook_fires"],
            steering_source,
        ),
    )
    rec_id = int(cur.lastrowid)

    for ev in ep_res["events"]:
        cur.execute(
            """
            INSERT INTO cascade_events (
                record_id, restart_idx, trigger_type, token_pos, cut_tokens,
                purged_preview, last_progress_marker, context_ref, temp_before,
                temp_after, frame_text, timestamp_utc
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                rec_id,
                ev.get("restart_idx", 0),
                ev.get("trigger_type", "unknown"),
                ev.get("token_pos", 0),
                ev.get("cut_tokens", 0),
                ev.get("purged_preview"),
                ev.get("last_progress", ""),
                ev.get("context_ref", ""),
                ev.get("temp_before", 0.7),
                ev.get("temp_after", 0.3),
                ev.get("frame_text", ""),
                ev.get("timestamp_utc", utc_now_iso()),
            ),
        )

    for lr in ep_res["latent_rows"]:
        cur.execute(
            """
            INSERT INTO latent_layer_metrics (
                record_id, layer_idx, phase, token_pos, pr_traj,
                top1_energy_ratio, svd_entropy_traj, mps_chi_eff, mps_svn,
                mps_top1_schmidt, h_norm, hook_fired_count, timestamp_utc
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                rec_id,
                lr["layer_idx"],
                lr["phase"],
                lr["token_pos"],
                lr["pr_traj"],
                lr["top1_energy_ratio"],
                lr["svd_entropy_traj"],
                lr["mps_chi_eff"],
                lr["mps_svn"],
                lr["mps_top1_schmidt"],
                lr["h_norm"],
                lr["hook_fired_count"],
                utc_now_iso(),
            ),
        )

    for acc in ep_res.get("loto_acc_rows", []):
        cur.execute(
            """
            INSERT OR REPLACE INTO loto_episode_accumulators (
                record_id, task_id, rep_idx, layer_idx,
                pos_n, pos_pr_sum, pos_sum_blob,
                neg_n, neg_pr_sum, neg_sum_blob, timestamp_utc
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                rec_id,
                task_id,
                rep_idx,
                acc["layer_idx"],
                acc["pos_n"],
                acc["pos_pr_sum"],
                acc["pos_sum_blob"],
                acc["neg_n"],
                acc["neg_pr_sum"],
                acc["neg_sum_blob"],
                utc_now_iso(),
            ),
        )

    cur.execute(
        """
        INSERT OR REPLACE INTO experiment_ledger (
            experiment, arm, task_id, rep_idx, status, record_id, updated_at_utc
        ) VALUES (?, ?, ?, ?, 'done', ?, ?)
        """,
        (experiment, arm, ledger_task_key, rep_idx, rec_id, utc_now_iso()),
    )
    conn.commit()
    return rec_id


# ============================================================================
# Execução dos Blocos Experimentais
# ============================================================================
def run_clinical_control_arms(
    conn: sqlite3.Connection,
    model,
    tokenizer,
    decoder_layers: torch.nn.ModuleList,
    arms_spec: List[Tuple[str, bool, bool, bool]],
    scenes: List[Dict[str, Any]],
    cfg_clinical: Dict[str, Any],
    run_id: str,
    budget: BudgetController,
    db_path: str,
    hf_repo: Optional[str],
    upload_every: int,
    counter_box: List[int],
) -> bool:
    in_dev = first_input_device(model)
    for arm_name, use_chat, enable_thinking, do_profile in arms_spec:
        print(f"\n>>> [CONTROLE LONGO HORIZONTE] Braço: {arm_name} | Cenas: {len(scenes)} | Thinking: {enable_thinking}")
        for idx, sc in enumerate(scenes):
            task_id = sc.get("id") or sc.get("cena_id", f"cena_{idx+1}")
            f1_prompt = sc.get("fase_1_prompt", "")
            f2_prompt = sc.get("fase_2_prompt", "")
            f1_visible_cached: Optional[str] = None
            f1_attempted = False

            for phase_idx, (phase, p_text) in enumerate([("fase_1", f1_prompt), ("fase_2", f2_prompt)]):
                if not p_text:
                    continue
                if budget.should_stop():
                    log_budget_event(conn, "abort_budget", f"Budget atingido em {arm_name}:{task_id}_{phase}")
                    return False

                ledger_key = f"{task_id}_{phase}"
                row = conn.execute(
                    "SELECT status, record_id FROM experiment_ledger WHERE experiment='control_v2' AND arm=? AND task_id=? AND rep_idx=1",
                    (arm_name, ledger_key),
                ).fetchone()
                if row and row[0] == "done":
                    if phase == "fase_1" and row[1] is not None:
                        f1_attempted = True
                        prev = conn.execute(
                            "SELECT visible_response FROM generation_records WHERE record_id=?",
                            (row[1],),
                        ).fetchone()
                        if prev:
                            f1_visible_cached = prev[0]
                    continue

                if phase == "fase_2" and f1_attempted:
                    # P1-16: Preserva sempre estrutura 2-turnos mesmo se fase_1 gastou tudo em thought
                    f1_context = sanitize_scaffold_text(f1_visible_cached or "")[:3000]
                    if not f1_context:
                        f1_context = "[Sem emissão visível concluída no turno anterior.]"
                    messages = [
                        {"role": "user", "content": f1_prompt},
                        {"role": "assistant", "content": f1_context},
                        {"role": "user", "content": f2_prompt},
                    ]
                else:
                    messages = [{"role": "user", "content": p_text}]

                seed = 1000 * (idx + 1) + 100 * (phase_idx + 1) + 42
                torch.manual_seed(seed)
                if torch.cuda.is_available():
                    torch.cuda.manual_seed_all(seed)

                encoded_prompt = encode_messages_tensor(
                    tokenizer, messages, use_chat=use_chat, enable_thinking=enable_thinking, device=in_dev
                )

                t0 = time.time()
                ep_res = run_episode_v2(
                    model=model,
                    tokenizer=tokenizer,
                    prompt_ids=encoded_prompt,
                    arm=arm_name,
                    cfg=cfg_clinical,
                    decoder_layers=decoder_layers if do_profile else None,
                    hook_mode="passive" if do_profile else None,
                )
                latency = round(time.time() - t0, 3)
                parsed = parse_gemma4_channels(tokenizer, ep_res["final_ids"])

                if phase == "fase_1":
                    f1_attempted = True
                    f1_visible_cached = parsed["visible_response"]

                rec_id = persist_episode_result(
                    conn=conn,
                    run_id=run_id,
                    experiment="control_v2",
                    arm=arm_name,
                    ledger_task_key=ledger_key,
                    task_id=task_id,
                    task_phase=phase,
                    rep_idx=1,
                    prompt_tokens=int(encoded_prompt.shape[1]),
                    ep_res=ep_res,
                    parsed=parsed,
                    latency=latency,
                    seed=seed,
                    enable_thinking=enable_thinking and use_chat,
                )
                counter_box[0] += 1
                if counter_box[0] % 20 == 0:
                    log_memory_snapshot(conn, f"post_gen_{arm_name}", rec_id)
                if upload_every > 0 and (counter_box[0] % upload_every == 0):
                    maybe_upload_checkpoint_hf(conn, db_path, hf_repo, f"ckpt_{counter_box[0]}")

                print(
                    f"  [{arm_name}] {ledger_key}: {ep_res['gross_generated']} tok "
                    f"(think={parsed['thinking_tokens']}, vis={parsed['visible_tokens']}) "
                    f"em {latency}s | Degen={parsed['degen_sanitized']} (UR_clean={parsed['ur_sanitized']})"
                )
    return True


def run_swe_arms(
    conn: sqlite3.Connection,
    model,
    tokenizer,
    decoder_layers: torch.nn.ModuleList,
    arms_spec: List[Dict[str, Any]],
    swe_tasks: List[Dict[str, Any]],
    cfg_swe: Dict[str, Any],
    run_id: str,
    budget: BudgetController,
    db_path: str,
    hf_repo: Optional[str],
    upload_every: int,
    counter_box: List[int],
) -> bool:
    in_dev = first_input_device(model)
    hidden_dim = cfg_swe.get("hidden_dim", 3840)

    for spec in arms_spec:
        arm_name = spec["arm"]
        exp_tag = spec["experiment"]
        reps = spec["reps"]
        use_chat = spec.get("use_chat", True)
        enable_thinking = spec.get("enable_thinking", True)
        hook_mode = spec.get("hook_mode", None)
        collect_calib = spec.get("collect_calib", False)

        # Se este braço é Opt1 Steering, garante que os vetores LOTO estão atualizados a partir do banco
        if hook_mode == "opt1_steering":
            rebuild_and_persist_loto_from_db(conn, run_id, CANONICAL_48_LAYERS, hidden_dim)

        print(
            f"\n>>> [{exp_tag.upper()}] Braço: {arm_name} | Tasks: {len(swe_tasks)} x Reps: {reps} "
            f"| Hook: {hook_mode or 'none'}"
        )

        for rep in range(1, reps + 1):
            for task in swe_tasks:
                if budget.should_stop():
                    if collect_calib:
                        rebuild_and_persist_loto_from_db(conn, run_id, CANONICAL_48_LAYERS, hidden_dim)
                    log_budget_event(conn, "abort_budget", f"Budget atingido em {arm_name}:{task.get('task_id')}:r{rep}")
                    return False

                task_id = task.get("task_id", "unknown_task")
                row = conn.execute(
                    "SELECT status FROM experiment_ledger WHERE experiment=? AND arm=? AND task_id=? AND rep_idx=?",
                    (exp_tag, arm_name, task_id, rep),
                ).fetchone()
                if row and row[0] == "done":
                    continue

                steering_map = None
                steering_source = None
                if hook_mode == "opt1_steering":
                    steering_map, steering_source = load_steering_for_task(
                        conn, task_id, INTERVENTION_HUB_LAYERS, hidden_dim
                    )
                    if len(steering_map) < len(INTERVENTION_HUB_LAYERS):
                        raise RuntimeError(
                            f"Calibração LOTO estrita incompleta para `{task_id}` ({len(steering_map)}/{len(INTERVENTION_HUB_LAYERS)} hubs). "
                            "Conclua pelo menos 2 tasks distintas em `nf4_swe_baseline` / `nf4_swe_calib_loto`."
                        )

                seed = 1000 * rep + 42
                torch.manual_seed(seed)
                if torch.cuda.is_available():
                    torch.cuda.manual_seed_all(seed)

                messages = [{"role": "user", "content": task.get("prompt", "")}]
                encoded_prompt = encode_messages_tensor(
                    tokenizer, messages, use_chat=use_chat, enable_thinking=enable_thinking, device=in_dev
                )

                t0 = time.time()
                ep_res = run_episode_v2(
                    model=model,
                    tokenizer=tokenizer,
                    prompt_ids=encoded_prompt,
                    arm=arm_name,
                    cfg=cfg_swe,
                    decoder_layers=decoder_layers if hook_mode else None,
                    hook_mode=hook_mode,
                    steering_map=steering_map,
                    collect_calib=collect_calib,
                )
                latency = round(time.time() - t0, 3)
                parsed = parse_gemma4_channels(tokenizer, ep_res["final_ids"])

                rec_id = persist_episode_result(
                    conn=conn,
                    run_id=run_id,
                    experiment=exp_tag,
                    arm=arm_name,
                    ledger_task_key=task_id,
                    task_id=task_id,
                    task_phase="swe_solve",
                    rep_idx=rep,
                    prompt_tokens=int(encoded_prompt.shape[1]),
                    ep_res=ep_res,
                    parsed=parsed,
                    latency=latency,
                    seed=seed,
                    enable_thinking=enable_thinking and use_chat,
                    steering_source=steering_source,
                )
                counter_box[0] += 1
                if counter_box[0] % 15 == 0:
                    log_memory_snapshot(conn, f"post_gen_{arm_name}", rec_id)
                if upload_every > 0 and (counter_box[0] % upload_every == 0):
                    if collect_calib:
                        rebuild_and_persist_loto_from_db(conn, run_id, CANONICAL_48_LAYERS, hidden_dim)
                    maybe_upload_checkpoint_hf(conn, db_path, hf_repo, f"ckpt_{counter_box[0]}")

                print(
                    f"  [{arm_name} r{rep}] {task_id}: {ep_res['gross_generated']} tok "
                    f"(think={parsed['thinking_tokens']}, vis={parsed['visible_tokens']}, cut={ep_res['cut_tokens_purged']}) "
                    f"em {latency}s | Restarts={ep_res['restarts']} | Hooks={ep_res['total_hook_fires']} "
                    f"| Patch={parsed['has_patch']} | Degen={parsed['degen_sanitized']} (UR={parsed['ur_sanitized']})"
                )

        if collect_calib:
            n_vecs = rebuild_and_persist_loto_from_db(conn, run_id, CANONICAL_48_LAYERS, hidden_dim)
            print(f"  [LOTO CALIBRATION DB] {n_vecs} vetores reconstruídos de `loto_episode_accumulators`.")
            log_budget_event(conn, "loto_calibrated", f"arm={arm_name} vectors={n_vecs}")

    return True


# ============================================================================
# CLI & Orquestração Principal
# ============================================================================
def import_transformers_version() -> str:
    try:
        import transformers
        return transformers.__version__
    except Exception:
        return "unknown"


def import_bnb_version() -> str:
    try:
        import bitsandbytes
        return bitsandbytes.__version__
    except Exception:
        return "none"


def count_pending_episodes(
    conn: sqlite3.Connection,
    experiment_mode: str,
    precision: str,
    reps_swe: int,
    reps_swe_comp: int,
    scenes: List[Dict[str, Any]],
    swe_tasks: List[Dict[str, Any]],
) -> Tuple[int, int]:
    """
    Calcula (pending_count, total_expected) consultando `experiment_ledger` ANTES de carregar 12 GB na VRAM.
    Em sessões de continuação (ex.: Sessão 3 onde `full_nf4` já terminou e falta só `control_int8`),
    evita carregar NF4 desnecessariamente!
    """
    expected: List[Tuple[str, str, str, int]] = []

    def _add_swe(exp_tag: str, arm_name: str, reps: int) -> None:
        for r in range(1, reps + 1):
            for t in swe_tasks:
                expected.append((exp_tag, arm_name, t.get("task_id", "unknown_task"), r))

    def _add_clinical(arm_name: str) -> None:
        for idx, sc in enumerate(scenes):
            tid = sc.get("id") or sc.get("cena_id", f"cena_{idx+1}")
            for phase, p_text in [("fase_1", sc.get("fase_1_prompt", "")), ("fase_2", sc.get("fase_2_prompt", ""))]:
                if p_text:
                    expected.append(("control_v2", arm_name, f"{tid}_{phase}", 1))

    if experiment_mode in ("wave1_nf4", "full_nf4", "pilot", "all") and swe_tasks:
        for arm in ("nf4_swe_baseline", "nf4_cascade_soft_v2", "nf4_cascade_hard_cut"):
            _add_swe("wave1_swe", arm, reps_swe)
    if experiment_mode in ("wave2_nf4", "full_nf4") and swe_tasks:
        for arm in ("nf4_opt1_steering", "nf4_opt2_spectral"):
            _add_swe("wave2_swe", arm, reps_swe)
    if experiment_mode in ("wave1_nf4", "full_nf4"):
        if swe_tasks:
            _add_swe("wave1_swe", "nf4_swe_completion", reps_swe_comp)
        if scenes:
            _add_clinical("nf4_chat_long")
    if experiment_mode in ("control_int8", "control", "all") and scenes:
        _add_clinical(f"{precision}_chat_long")
        _add_clinical(f"{precision}_completion_long")

    if not expected:
        return 0, 0
    done_set = {
        (r[0], r[1], r[2], int(r[3]))
        for r in conn.execute("SELECT experiment, arm, task_id, rep_idx FROM experiment_ledger WHERE status='done'").fetchall()
    }
    pending = sum(1 for k in expected if k not in done_set)
    return pending, len(expected)


def main():
    parser = argparse.ArgumentParser(description="Gemma-4 T4x2 v2.1 Unified Executor (Waves 1 & 2)")
    parser.add_argument("--model-id", type=str, default="google/gemma-4-12b-it")
    parser.add_argument("--precision", type=str, choices=["int8", "nf4", "fp16"], default="nf4")
    parser.add_argument(
        "--experiment",
        type=str,
        choices=[
            "canary",
            "control_int8",
            "wave1_nf4",
            "wave2_nf4",
            "full_nf4",
            "control",
            "pilot",
            "all",
        ],
        default="full_nf4",
    )
    parser.add_argument("--output-db", type=str, default="/kaggle/working/gemma4_t4x2_v2_results.sqlite")
    parser.add_argument("--payload-dir", type=str, default="research/gemma4_paper_track/payloads")
    parser.add_argument("--reps-swe", type=int, default=10)
    parser.add_argument("--reps-swe-comp", type=int, default=3)
    parser.add_argument("--max-tokens-clinical", type=int, default=2048)
    parser.add_argument("--max-tokens-swe", type=int, default=3072)
    parser.add_argument("--max-new-tokens", type=int, default=None)
    parser.add_argument("--think-budget", type=int, default=1024)
    parser.add_argument("--stall-k", type=int, default=160)
    parser.add_argument("--time-budget-hours", type=float, default=10.8)
    parser.add_argument("--session-epoch-file", type=str, default="/kaggle/working/session_start_epoch.txt")
    parser.add_argument("--hf-repo", type=str, default="fabricioslv/gemma4-kaggle-dual-t4-results")
    parser.add_argument("--upload-every", type=int, default=25)
    parser.add_argument("--limit-tasks", type=int, default=None)
    args = parser.parse_args()

    if args.max_new_tokens is not None:
        args.max_tokens_clinical = args.max_new_tokens
        args.max_tokens_swe = args.max_new_tokens

    budget = BudgetController(max_hours=args.time_budget_hours, epoch_file=args.session_epoch_file)
    run_id = f"run_v21_{args.precision}_{args.experiment}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    print(f"=== EXECUTOR T4x2 v2.1 ({args.precision.upper()} | {args.experiment}) | Run: {run_id} ===")
    print(f"Tempo restante do budget de sessão: {round(budget.remaining_seconds() / 3600.0, 2)} h")

    n_gpus = torch.cuda.device_count()
    gpus_meta = []
    for i in range(n_gpus):
        p = torch.cuda.get_device_properties(i)
        gpus_meta.append({"idx": i, "name": p.name, "sm": f"{p.major}.{p.minor}", "mem_mb": round(p.total_memory / (1024**2), 2)})
        print(f"  GPU {i}: {p.name} (sm_{p.major}{p.minor}, {gpus_meta[-1]['mem_mb']} MB)")

    conn = init_database(args.output_db)

    payload_scenes_path = os.path.join(args.payload_dir, "unified_v10_v11_payload.json")
    payload_swe_path = os.path.join(args.payload_dir, "curated_gluzdov_swe_tasks.json")

    scenes: List[Dict[str, Any]] = []
    if os.path.exists(payload_scenes_path):
        with open(payload_scenes_path, "r", encoding="utf-8") as f:
            v10_data = json.load(f)
        scenes = v10_data.get("v10_cenas") or v10_data.get("cenas_v10", [])
        if args.limit_tasks is not None:
            scenes = scenes[: args.limit_tasks]

    swe_tasks: List[Dict[str, Any]] = []
    if os.path.exists(payload_swe_path):
        with open(payload_swe_path, "r", encoding="utf-8") as f:
            swe_tasks = json.load(f)
        if args.limit_tasks is not None:
            swe_tasks = swe_tasks[: args.limit_tasks]

    if args.experiment != "canary":
        if budget.should_stop():
            msg = f"Budget de sessão já esgotado ({round(budget.remaining_seconds(), 1)}s restantes). Pulando carga de {args.precision}!"
            print(f"[FAST-SKIP BUDGET] {msg}")
            log_budget_event(conn, "skip_load_budget", f"exp={args.experiment} precision={args.precision}")
            conn.close()
            return
        pending_n, total_n = count_pending_episodes(
            conn, args.experiment, args.precision, args.reps_swe, args.reps_swe_comp, scenes, swe_tasks
        )
        print(f"Progresso no ledger ({args.experiment}): {total_n - pending_n}/{total_n} concluídos ({pending_n} pendentes).")
        if total_n > 0 and pending_n == 0:
            print(f"[FAST-SKIP DONE] Todos os {total_n} episódios de `{args.experiment}` já estão 'done' no ledger! Pulando carga de pesos.")
            conn.close()
            return

    print(f"\nCarregando {args.model_id} em regime {args.precision} (compute_dtype=float16)...")
    tokenizer = AutoTokenizer.from_pretrained(args.model_id, trust_remote_code=True)

    bnb_config = None
    torch_dtype = torch.float16
    if args.precision == "int8":
        bnb_config = BitsAndBytesConfig(load_in_8bit=True)
    elif args.precision == "nf4":
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.float16,
        )

    if n_gpus >= 2:
        max_mem = {0: "7.5GiB", 1: "13.5GiB"} if args.precision == "nf4" else {0: "13.5GiB", 1: "13.5GiB"}
        dev_map_arg = "auto"
    else:
        max_mem = None
        dev_map_arg = "cuda:0" if n_gpus == 1 else "cpu"

    model = AutoModelForCausalLM.from_pretrained(
        args.model_id,
        device_map=dev_map_arg,
        max_memory=max_mem,
        quantization_config=bnb_config,
        torch_dtype=torch_dtype,
        attn_implementation="sdpa",
        trust_remote_code=True,
    )
    model.eval()

    raw_dmap = getattr(model, "hf_device_map", {})
    if n_gpus >= 1:
        bad_targets = {k: str(v) for k, v in raw_dmap.items() if str(v) in ("cpu", "disk")}
        if bad_targets:
            raise RuntimeError(f"VIOLAÇÃO DE PINNING VRAM: módulos despachados fora da GPU: {bad_targets}")

    decoder_layers = resolve_decoder_layers(model)
    model_sha = getattr(model.config, "_commit_hash", None) or "hf_snapshot"
    print(f"Camadas de texto resolvidas: {len(decoder_layers)} | Shard entries: {len(raw_dmap)} | rev={model_sha}")

    hf_map_str = json.dumps({k: str(v) for k, v in raw_dmap.items()})
    conn.execute(
        """
        INSERT OR REPLACE INTO run_metadata (
            run_id, model_id, model_revision_sha, quantization, compute_dtype,
            device_map_json, transformers_ver, bitsandbytes_ver, torch_ver,
            cuda_ver, gpus_json, kaggle_session_id, started_at_utc, status
        ) VALUES (?, ?, ?, ?, 'float16', ?, ?, ?, ?, ?, ?, ?, ?, 'RUNNING')
        """,
        (
            run_id,
            args.model_id,
            str(model_sha),
            args.precision,
            hf_map_str,
            import_transformers_version(),
            import_bnb_version(),
            torch.__version__,
            torch.version.cuda,
            json.dumps(gpus_meta),
            os.environ.get("KAGGLE_KERNEL_RUN_TYPE", "interactive"),
            utc_now_iso(),
        ),
    )
    conn.commit()
    log_memory_snapshot(conn, "post_load")

    def _safe_tok_id(tok_str: str) -> Optional[int]:
        tid = tokenizer.convert_tokens_to_ids(tok_str)
        return int(tid) if (tid is not None and tid != tokenizer.unk_token_id) else None

    ch_open_id = _safe_tok_id("<|channel>")
    ch_close_id = _safe_tok_id("<channel|>")
    think_sys_id = _safe_tok_id("<|think|>")
    tc_open_id = _safe_tok_id("<|tool_call>")
    tc_close_id = _safe_tok_id("<tool_call|>")

    tool_token_ids = [tid for tid in (tc_open_id, _safe_tok_id("<tool_call>")) if tid is not None]
    print(
        f"Special token IDs: <|think|>={think_sys_id}, <|channel>={ch_open_id}, "
        f"<channel|>={ch_close_id}, <|tool_call>={tc_open_id}, <tool_call|>={tc_close_id}"
    )
    if ch_open_id is None or ch_close_id is None or think_sys_id is None:
        warn_msg = f"IDs especiais de pensamento incompletos: think={think_sys_id} open={ch_open_id} close={ch_close_id}"
        print(f"AVISO CRÍTICO: {warn_msg}")
        log_budget_event(conn, "tok_ids_missing", warn_msg)

    hidden_dim = int(getattr(getattr(model.config, "text_config", model.config), "hidden_size", 3840))
    base_cfg = {
        "temp": 0.7,
        "top_p": 0.95,
        "top_k": 64,
        "K": args.stall_k,
        "think_budget": args.think_budget,
        "W": 128,
        "ur_min": 0.30,
        "max_restarts": 3,
        "cascade_temp": 0.3,
        "cascade_top_p": 0.85,
        "tool_token_ids": tool_token_ids,
        "ch_open_id": ch_open_id,
        "ch_close_id": ch_close_id,
        "tc_open_id": tc_open_id,
        "tc_close_id": tc_close_id,
        "hidden_dim": hidden_dim,
        "latent_W": 16,
        "latent_stride": 4,
        "alpha_steer": 0.05,
        "beta_spectral": 0.50,
        "gamma1_thresh": 0.80,
    }
    cfg_clinical = dict(base_cfg, max_new_tokens=args.max_tokens_clinical)
    cfg_swe = dict(base_cfg, max_new_tokens=args.max_tokens_swe)

    counter_box = [0]
    ok_budget = True

    # ------------------------------------------------------------------
    # Modo 0: Canário de Sanidade (VRAM + Canal Thinking + Hooks 48L)
    # ------------------------------------------------------------------
    if args.experiment == "canary":
        canary_scenes = scenes[:1] if scenes else [{"id": "canary_1", "fase_1_prompt": "Explique em 2 frases como validar um patch git."}]
        cfg_can = dict(base_cfg, max_new_tokens=args.max_new_tokens or 96)
        ok_budget = run_clinical_control_arms(
            conn, model, tokenizer, decoder_layers,
            arms_spec=[(f"{args.precision}_canary_chat_48L", True, True, True)],
            scenes=canary_scenes, cfg_clinical=cfg_can, run_id=run_id,
            budget=budget, db_path=args.output_db, hf_repo=None, upload_every=0, counter_box=counter_box,
        )
        log_memory_snapshot(conn, "canary_done")

    # ------------------------------------------------------------------
    # Modo 1 (PRIORIDADE PAPER — P0-2): Onda 1B SWE Core (Baseline 48L/LOTO -> 3A -> 3B)
    # ------------------------------------------------------------------
    if ok_budget and args.experiment in ("wave1_nf4", "full_nf4", "pilot", "all") and swe_tasks:
        wave1_core_swe = [
            {
                "experiment": "wave1_swe",
                "arm": "nf4_swe_baseline",
                "reps": args.reps_swe,
                "use_chat": True,
                "enable_thinking": True,
                "hook_mode": "passive",
                "collect_calib": True,
            },
            {
                "experiment": "wave1_swe",
                "arm": "nf4_cascade_soft_v2",
                "reps": args.reps_swe,
                "use_chat": True,
                "enable_thinking": True,
                "hook_mode": None,
                "collect_calib": False,
            },
            {
                "experiment": "wave1_swe",
                "arm": "nf4_cascade_hard_cut",
                "reps": args.reps_swe,
                "use_chat": True,
                "enable_thinking": True,
                "hook_mode": None,
                "collect_calib": False,
            },
        ]
        ok_budget = run_swe_arms(
            conn, model, tokenizer, decoder_layers,
            arms_spec=wave1_core_swe, swe_tasks=swe_tasks, cfg_swe=cfg_swe,
            run_id=run_id, budget=budget, db_path=args.output_db,
            hf_repo=args.hf_repo, upload_every=args.upload_every, counter_box=counter_box,
        )

    # ------------------------------------------------------------------
    # Modo 2 (PRIORIDADE PAPER — P0-2): Onda 2 SWE Latente (Opt1 Steering LOTO vs Opt2 Spectral)
    # ------------------------------------------------------------------
    if ok_budget and args.experiment in ("wave2_nf4", "full_nf4") and swe_tasks:
        rebuild_and_persist_loto_from_db(conn, run_id, CANONICAL_48_LAYERS, hidden_dim)
        # Verifica cobertura por-task real para todas as tasks SWE (P0-1b)
        covered_tasks = {
            r[0]
            for r in conn.execute(
                "SELECT DISTINCT held_out_task FROM steering_calibration WHERE held_out_task != '__GLOBAL__'"
            ).fetchall()
        }
        needed_tasks = {t.get("task_id", "unknown_task") for t in swe_tasks}
        if not needed_tasks.issubset(covered_tasks) and len(swe_tasks) >= 2:
            print(
                f"\n[WAVE 2 AUTO-CALIB] Cobertura LOTO incompleta ({len(covered_tasks)}/{len(needed_tasks)} tasks). "
                "Executando calibração LOTO rápida (3 reps/task)..."
            )
            ok_budget = run_swe_arms(
                conn, model, tokenizer, decoder_layers,
                arms_spec=[
                    {
                        "experiment": "wave2_calib",
                        "arm": "nf4_swe_calib_loto",
                        "reps": 3,
                        "use_chat": True,
                        "enable_thinking": True,
                        "hook_mode": "passive",
                        "collect_calib": True,
                    }
                ],
                swe_tasks=swe_tasks, cfg_swe=cfg_swe, run_id=run_id,
                budget=budget, db_path=args.output_db, hf_repo=args.hf_repo,
                upload_every=args.upload_every, counter_box=counter_box,
            )

        if ok_budget:
            wave2_swe_arms = [
                {
                    "experiment": "wave2_swe",
                    "arm": "nf4_opt1_steering",
                    "reps": args.reps_swe,
                    "use_chat": True,
                    "enable_thinking": True,
                    "hook_mode": "opt1_steering",
                    "collect_calib": False,
                },
                {
                    "experiment": "wave2_swe",
                    "arm": "nf4_opt2_spectral",
                    "reps": args.reps_swe,
                    "use_chat": True,
                    "enable_thinking": True,
                    "hook_mode": "opt2_spectral",
                    "collect_calib": False,
                },
            ]
            ok_budget = run_swe_arms(
                conn, model, tokenizer, decoder_layers,
                arms_spec=wave2_swe_arms, swe_tasks=swe_tasks, cfg_swe=cfg_swe,
                run_id=run_id, budget=budget, db_path=args.output_db,
                hf_repo=args.hf_repo, upload_every=args.upload_every, counter_box=counter_box,
            )

    # ------------------------------------------------------------------
    # Modo 3: Controles Complementares NF4 (nf4_swe_completion + nf4_chat_long 2048 tok)
    # ------------------------------------------------------------------
    if ok_budget and args.experiment in ("wave1_nf4", "full_nf4"):
        if swe_tasks:
            ok_budget = run_swe_arms(
                conn, model, tokenizer, decoder_layers,
                arms_spec=[
                    {
                        "experiment": "wave1_swe",
                        "arm": "nf4_swe_completion",
                        "reps": args.reps_swe_comp,
                        "use_chat": False,
                        "enable_thinking": False,
                        "hook_mode": "passive",
                        "collect_calib": False,
                    }
                ],
                swe_tasks=swe_tasks, cfg_swe=cfg_swe, run_id=run_id,
                budget=budget, db_path=args.output_db, hf_repo=args.hf_repo,
                upload_every=args.upload_every, counter_box=counter_box,
            )
        if ok_budget and scenes:
            ok_budget = run_clinical_control_arms(
                conn, model, tokenizer, decoder_layers,
                arms_spec=[("nf4_chat_long", True, True, True)],
                scenes=scenes, cfg_clinical=cfg_clinical, run_id=run_id,
                budget=budget, db_path=args.output_db, hf_repo=args.hf_repo,
                upload_every=args.upload_every, counter_box=counter_box,
            )

    # ------------------------------------------------------------------
    # Modo 4: Controle Clínico INT8 Longo Horizonte (2048 tok)
    # ------------------------------------------------------------------
    if ok_budget and args.experiment in ("control_int8", "control", "all") and scenes:
        p_tag = args.precision
        ok_budget = run_clinical_control_arms(
            conn, model, tokenizer, decoder_layers,
            arms_spec=[
                (f"{p_tag}_chat_long", True, True, False),
                (f"{p_tag}_completion_long", False, False, False),
            ],
            scenes=scenes, cfg_clinical=cfg_clinical, run_id=run_id,
            budget=budget, db_path=args.output_db, hf_repo=args.hf_repo,
            upload_every=args.upload_every, counter_box=counter_box,
        )

    final_status = "COMPLETED" if ok_budget else "ABORTED_BUDGET"
    conn.execute(
        "UPDATE run_metadata SET completed_at_utc=?, status=? WHERE run_id=?",
        (utc_now_iso(), final_status, run_id),
    )
    conn.commit()
    if args.experiment != "canary":
        maybe_upload_checkpoint_hf(conn, args.output_db, args.hf_repo, f"final_{final_status}")
    conn.close()
    print(f"\n[{final_status}] Execução finalizada ({counter_box[0]} novos registros). Banco: {args.output_db}")


if __name__ == "__main__":
    main()