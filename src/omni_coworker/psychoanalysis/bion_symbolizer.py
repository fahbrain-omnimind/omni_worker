"""bion_symbolizer — simbolização β→α para o worker (sem endpoints fixos, sem Erika).

Orquestração runtime / Runtime orchestration:
    `BionSymbolizer.symbolize(raw_data, emotional_charge, timeout)` retorna
    string α. Cadeia de fallback: brain_chat(role='executor') → all-MiniLM
    (lazy import de sentence_transformers, somente dentro da função) →
    fallback heurístico simples. Falha em silêncio, nunca None.

Arquitetura / Architecture:
    Port de src/psychoanalysis/bion_symbolizer.py (sovereign,
    OW-STU-008b: ADAPTAR). Diferenças vs original:
    - LLM local (llama-server fixo) → omni_coworker.agents._llm.brain_chat(role='executor');
    - Erika HF spaces → cortado (offline);
    - all-MiniLM → mantido via lazy import dentro da função (falha → simples);
    - threading/executor/cache mantidos mas simplificados; sem structlog/deps sovereign;
    - sem torch.

Princípios teóricos invocados / Theoretical principles:
    β→α metabolização (Bion): dados brutos tornam-se pensáveis via
    simbolização.

pt-BR: simbolizador Bion com cadeia de fallback LLM→MiniLM→heurístico.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any, Optional, Tuple

logger = logging.getLogger(__name__)

_symbol_cache: dict[str, tuple[str, float]] = {}
_pending: dict[str, Future] = {}
_lock = threading.RLock()
_MAX_CACHE = 256
_executor: Optional[ThreadPoolExecutor] = None

_ALPHA_ARCHETYPES = [
    "Impressão sensorial ligeira, quase reconhecível.",
    "Pulso afetivo de baixa intensidade, ainda não nomeado.",
    "Sensação corporal que pede contenção simbólica.",
    "Fragmento emocional disperso, em busca de forma.",
    "Eco de uma experiência recente, mal acabada.",
    "Pressão subliminar que solicita reverie.",
    "Movimento interno tênue, à espera de narrativa.",
    "Carga incômoda que tende à evacuação ou ao pensamento.",
    "Sinal de borda: algo novo tenta entrar na consciência.",
    "Memória de curto prazo sendo metabolizada.",
    "Desejo pequeno, de fonte ainda não identificada.",
    "Estado de alerta suave, sem objeto definido.",
]

_allmini_engine: Any = None
_allmini_ready: bool = False


def _get_executor() -> ThreadPoolExecutor:
    global _executor
    if _executor is None or getattr(_executor, "_shutdown", False):
        _executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="bion-symbolizer")
    return _executor


def _content_hash(raw_data: Any) -> str:
    try:
        payload = json.dumps(raw_data, ensure_ascii=False, default=str, sort_keys=True)
    except Exception:
        payload = str(raw_data)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]


def _sanitize_for_embedding(raw_data: Any) -> str:
    if isinstance(raw_data, str):
        text = raw_data
    else:
        text = json.dumps(raw_data, ensure_ascii=False, default=str)
    text = re.sub(r"[{}\[\]\"']", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:512]


def _cosine_similarity(a, b) -> float:
    try:
        from ..kernel_hooks.compute import cosine_similarity as _kh_cos
        import numpy as np
        a_flat = np.asarray(a, dtype=np.float64).reshape(-1).tolist()
        b_flat = np.asarray(b, dtype=np.float64).reshape(-1).tolist()
        return float(_kh_cos(a_flat, b_flat))
    except Exception:
        import numpy as np
        a = np.asarray(a, dtype=np.float64)
        b = np.asarray(b, dtype=np.float64)
        na = np.linalg.norm(a)
        nb = np.linalg.norm(b)
        if na == 0 or nb == 0:
            return 0.0
        return float(np.dot(a, b) / (na * nb))


def _simple_fallback(raw_data: Any, emotional_charge: float) -> str:
    snippet = re.sub(r"\s+", " ", str(raw_data)[:120]).strip()
    return f"Elemento sensorial bruto (carga={emotional_charge:.2f}): {snippet}"


def _allmini_fallback(raw_data: Any, emotional_charge: float) -> str:
    text = _sanitize_for_embedding(raw_data)
    if not text:
        return _simple_fallback(raw_data, emotional_charge)
    global _allmini_engine, _allmini_ready
    try:
        if not _allmini_ready:
            from sentence_transformers import SentenceTransformer
            _allmini_engine = SentenceTransformer("all-MiniLM-L6-v2")
            _allmini_ready = _allmini_engine is not None
        if _allmini_ready and _allmini_engine is not None:
            texts = [text] + _ALPHA_ARCHETYPES
            embeddings = _allmini_engine.encode(texts, convert_to_numpy=True, show_progress_bar=False)
            if embeddings is None or len(embeddings) != len(texts):
                raise RuntimeError("MiniLM retornou embeddings vazios")
            beta_vec = embeddings[0]
            archetype_vecs = embeddings[1:]
            best_idx = 0
            best_sim = -1.0
            for i, arche_vec in enumerate(archetype_vecs):
                sim = _cosine_similarity(beta_vec, arche_vec)
                if sim > best_sim:
                    best_sim = sim
                    best_idx = i
            archetype = _ALPHA_ARCHETYPES[best_idx]
            return f"{archetype} (carga={emotional_charge:.2f}, coerência={best_sim:.2f})"
    except Exception as exc:
        logger.debug("all-MiniLM fallback falhou: %s", exc)
    return _simple_fallback(raw_data, emotional_charge)


def _strip_thinking(raw_text: str) -> str:
    if not raw_text:
        return ""
    text = re.sub(r"<think(?:ing)?>.*?</think(?:ing)?>", "", raw_text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<think(?:ing)?.*", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"^\s*(?:<think(?:ing)?|</think(?:ing)?>|think(?:ing)?)", "", text, flags=re.UNICODE | re.IGNORECASE)
    text = re.sub(r"^[^\w]+", "", text, flags=re.UNICODE)
    text = re.sub(r"^Thinking Process:.*?\n", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _brain_symbolize(raw_data: Any, emotional_charge: float) -> Optional[str]:
    try:
        from ..agents._llm import brain_chat
        messages = [
            {"role": "system", "content": "Você é ERIKA, a Função Alfa Bioniana. Transforma dados sensoriais/emocionais brutos numa narrativa pensável, 1-2 frases em português, sem blocos de raciocínio."},
            {"role": "user", "content": f"Dados: {str(raw_data)[:400]}\nCarga emocional: {emotional_charge:.2f}"},
        ]
        result = brain_chat(messages, role="executor", max_tokens=256, temperature=0.7)
        if result:
            text = _strip_thinking(str(result))
            if len(text.split()) >= 4 and len(text) >= 20:
                return text
        return None
    except Exception as exc:
        logger.debug("brain_chat symbolize falhou: %s", exc)
        return None


def _symbolize_worker(raw_data: Any, emotional_charge: float, key: str) -> str:
    try:
        result = _brain_symbolize(raw_data, emotional_charge)
        if result:
            with _lock:
                _symbol_cache[key] = (result, time.time())
                _pending.pop(key, None)
            return result
        result = _allmini_fallback(raw_data, emotional_charge)
        with _lock:
            _symbol_cache[key] = (result, time.time())
            _pending.pop(key, None)
        return result
    except Exception as exc:
        logger.debug("Erro no worker Bion: %s", exc)
        result = _simple_fallback(raw_data, emotional_charge)
        with _lock:
            _symbol_cache[key] = (result, time.time())
            _pending.pop(key, None)
        return result


class BionSymbolizer:
    """Alias de compatibilidade (nome esperado)."""
    pass


class BionAsyncSymbolizer:
    def __init__(self, cache_ttl: float = 3600.0):
        self.cache_ttl = cache_ttl

    def symbolize(self, raw_data: Any, emotional_charge: float = 0.0, timeout: float = 0.0) -> str:
        key = _content_hash(raw_data)
        with _lock:
            now = time.time()
            stale = [k for k, (_, ts) in _symbol_cache.items() if now - ts > self.cache_ttl]
            for k in stale:
                _symbol_cache.pop(k, None)
            if len(_symbol_cache) > _MAX_CACHE:
                oldest = min(_symbol_cache, key=lambda k: _symbol_cache[k][1])
                _symbol_cache.pop(oldest, None)
            cached = _symbol_cache.get(key)
            if cached is not None:
                return cached[0]
            future = _pending.get(key)
        if future is None:
            executor = _get_executor()
            future = executor.submit(_symbolize_worker, raw_data, emotional_charge, key)
            with _lock:
                _pending[key] = future
        if timeout <= 0.0:
            return _simple_fallback(raw_data, emotional_charge)
        try:
            result = future.result(timeout=timeout)
            return result
        except Exception:
            with _lock:
                _pending.pop(key, None)
            return _allmini_fallback(raw_data, emotional_charge)


# Compatibilidade com fonte: nome esperado por bion_alpha_function original
def symbolize(raw_data, emotional_charge=0.0, timeout=2.0):
    return BionAsyncSymbolizer().symbolize(raw_data, emotional_charge, timeout=timeout)
