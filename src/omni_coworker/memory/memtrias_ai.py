"""memory.memtrias_ai — memória topológica aberta (retorno do recalcado).

Orquestração runtime / Runtime orchestration:
    `MemtriasAI` é o registro aberto de memórias da instância: separa
    conteúdo por namespaces canônicos (machine, user, interaction,
    instance, chat, document, state) e aceita namespaces novos em
    runtime. `remember` embute + persiste; `recall` faz retrieval
    topológico (cosine sobre vetores) com filtros por namespace,
    instância, chat e estado da máquina — é o mecanismo do "retorno do
    recalcado": quando um assunto volta, as memórias antigas voltam com
    ele, por medida topológica + metadados organizados.
    Função pura + sqlite local; sem torch; acervo externo é bridge
    read-only opcional (OMNI_ACERVO_DIR).

Arquitetura / Architecture:
    Conceito: a máquina lê suas próprias produções (docs, auditorias,
    conversas, estados) e as guarda topologicamente; o ciclo consulta.
    Namespaces canônicos:
      - machine:     memórias que a máquina/instância produziu
                     (docs, auditorias, decisões, resumos).
      - user:        falas do usuário, preferências, estilos mapeados.
      - interaction: o saber entre ESTE usuário e ESTA instância
                     (vínculo, histórico conjunto).
      - instance:    por instância de modelo/agente (analyst, executor,
                     devin, kilo...) — instância x.
      - chat:        por sessão/conversa — chat x (o cache de megas de
                     conversa que volta quando o contexto retorna).
      - document:    documentos associados (acervo vetorizado, livros;
                     bridge read-only, uso interno/privado).
      - state:       estado da máquina associado à memória (regime,
                     vram, phi, attractor no momento da escrita).
    Embedding default: hashing-trick determinístico 384d (mesma
    dimensionalidade do acervo vetorizado 384D); pluggable via
    `embedder=` (ex.: sentence-transformers quando disponível).

Princípios teóricos invocados / Theoretical principles:
    Retorno do recalcado (Freud): o que foi registrado retorna quando o
    contexto o reconvoca — aqui, retrieval por proximidade topológica
    + recency decay, não por índice simbólico. A memória não é cache
    descartável: é inscrição que o próprio ciclo consulta.

pt-BR: registro aberto de memórias por namespace; embedding
determinístico; retrieval topológico com filtros; acervo externo
opcional read-only.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any, Callable

import numpy as np

EMBED_DIM = 384  # mesma dimensão do acervo vetorizado (384D)

CANONICAL_NAMESPACES = (
    "machine", "user", "interaction", "instance",
    "chat", "document", "state",
)

_DB = "memtrias.sqlite"


def _state_dir() -> Path:
    return Path(os.getenv("OMNI_STATE_DIR", "data"))


def hash_embedder(text: str, dim: int = EMBED_DIM) -> list[float]:
    """Deterministic hashing-trick embedder (offline, no deps).

    Cada token vira ±1 numa dim via sha256; média + L2-normaliza.
    Mesmo texto → mesmo vetor; não é semântico como MiniLM, mas dá
    proximidade topológica por vocabulário compartilhado.
    """
    vec = np.zeros(dim, dtype=np.float64)
    for tok in (text or "").lower().split():
        h = hashlib.sha256(tok.encode("utf-8")).digest()
        idx = int.from_bytes(h[:4], "little") % dim
        sign = 1.0 if h[4] & 1 else -1.0
        vec[idx] += sign
    n = float(np.linalg.norm(vec))
    return (vec / n).tolist() if n > 0 else vec.tolist()


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


class MemtriasAI:
    """Registro aberto de memórias topológicas por namespace."""

    def __init__(self, state_dir: Path | str | None = None,
                 embedder: Callable[[str], list[float]] | None = None,
                 acervo_dir: Path | str | None = None) -> None:
        self._dir = Path(state_dir) if state_dir else _state_dir()
        self._dir.mkdir(parents=True, exist_ok=True)
        self._embedder = embedder or hash_embedder
        self._namespaces: set[str] = set(CANONICAL_NAMESPACES)
        self._acervo_dir = Path(acervo_dir or os.getenv("OMNI_ACERVO_DIR", "")) \
            if (acervo_dir or os.getenv("OMNI_ACERVO_DIR")) else None
        con = sqlite3.connect(self._dir / _DB, timeout=10)
        con.execute(
            "CREATE TABLE IF NOT EXISTS memories("
            "id TEXT PRIMARY KEY, namespace TEXT, content TEXT,"
            " embedding TEXT, tags TEXT, instance TEXT, chat_id TEXT,"
            " doc_ref TEXT, state_ref TEXT, ts REAL)")
        con.execute(
            "CREATE INDEX IF NOT EXISTS idx_mem_ns ON memories(namespace, ts)")
        con.commit()
        con.close()

    # ── namespaces abertos ───────────────────────────────────────────────

    def register_namespace(self, name: str) -> str:
        """Adiciona namespace novo (classe aberta — usuário programa sua biblioteca)."""
        name = (name or "").strip().lower()
        if not name:
            raise ValueError("namespace vazio")
        self._namespaces.add(name)
        return name

    @property
    def namespaces(self) -> list[str]:
        return sorted(self._namespaces)

    # ── escrita ──────────────────────────────────────────────────────────

    def remember(self, namespace: str, content: str, *,
                 tags: list[str] | None = None,
                 instance: str | None = None,
                 chat_id: str | None = None,
                 doc_ref: str | None = None,
                 state_ref: dict[str, Any] | str | None = None,
                 ts: float | None = None) -> dict[str, Any]:
        """Inscreve memória: embute conteúdo + persiste com metadados."""
        ns = (namespace or "").strip().lower()
        if ns not in self._namespaces:
            self.register_namespace(ns)
        emb = self._embedder(content or "")
        rec = {
            "id": uuid.uuid4().hex[:16],
            "namespace": ns,
            "content": content or "",
            "tags": tags or [],
            "instance": instance,
            "chat_id": chat_id,
            "doc_ref": doc_ref,
            "state_ref": state_ref if isinstance(state_ref, str) or state_ref is None
                        else json.dumps(state_ref, default=str),
            "ts": float(ts or time.time()),
        }
        con = sqlite3.connect(self._dir / _DB, timeout=10)
        con.execute(
            "INSERT INTO memories(id,namespace,content,embedding,tags,"
            "instance,chat_id,doc_ref,state_ref,ts) VALUES(?,?,?,?,?,?,?,?,?,?)",
            (rec["id"], ns, rec["content"], json.dumps(emb),
             json.dumps(rec["tags"]), instance, chat_id, doc_ref,
             rec["state_ref"], rec["ts"]))
        con.commit()
        con.close()
        rec["dim"] = len(emb)
        return rec

    # ── leitura / retorno do recalcado ───────────────────────────────────

    def recall(self, query: str, *,
               namespaces: list[str] | None = None,
               top_k: int = 5,
               instance: str | None = None,
               chat_id: str | None = None,
               recency_halflife_s: float | None = 86400.0) -> list[dict[str, Any]]:
        """Retrieval topológico: cosine(query) + filtros + recency decay.

        O "retorno do recalcado": o que foi inscrito volta quando a
        consulta o reconvoca — por proximidade vetorial e metadados.
        """
        q = np.asarray(self._embedder(query or ""), dtype=np.float64)
        sql = "SELECT id,namespace,content,embedding,tags,instance,chat_id," \
              "doc_ref,state_ref,ts FROM memories WHERE 1=1"
        args: list[Any] = []
        if namespaces:
            sql += f" AND namespace IN ({','.join('?' * len(namespaces))})"
            args += [n.lower() for n in namespaces]
        if instance:
            sql += " AND instance=?"
            args.append(instance)
        if chat_id:
            sql += " AND chat_id=?"
            args.append(chat_id)
        con = sqlite3.connect(self._dir / _DB, timeout=10)
        rows = con.execute(sql, args).fetchall()
        con.close()
        now = time.time()
        scored = []
        for (mid, ns, content, embj, tags, inst, cid, dref, sref, ts) in rows:
            emb = np.asarray(json.loads(embj), dtype=np.float64)
            score = _cosine(q, emb)
            if recency_halflife_s and ts:
                age = max(0.0, now - float(ts))
                score *= 0.5 + 0.5 * math.pow(0.5, age / recency_halflife_s)
            scored.append({"id": mid, "namespace": ns, "content": content,
                           "score": round(score, 6), "tags": json.loads(tags or "[]"),
                           "instance": inst, "chat_id": cid, "doc_ref": dref,
                           "state_ref": sref, "ts": ts})
        scored.sort(key=lambda r: r["score"], reverse=True)
        return scored[:top_k]

    def count(self, namespace: str | None = None) -> int:
        sql = "SELECT COUNT(*) FROM memories"
        args: tuple = ()
        if namespace:
            sql += " WHERE namespace=?"
            args = (namespace.lower(),)
        con = sqlite3.connect(self._dir / _DB, timeout=10)
        n = con.execute(sql, args).fetchone()[0]
        con.close()
        return int(n)

    # ── acervo externo (document namespace, read-only) ───────────────────

    def acervo_available(self) -> bool:
        return bool(self._acervo_dir
                    and (self._acervo_dir / "acervo_manifest.sqlite").exists())

    def acervo_search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Busca lexical no catálogo do acervo (manifest sqlite, read-only).

        Uso interno/privado — o acervo contém material de licença e não é
        publicável; a bridge nunca escreve nele.
        """
        if not self.acervo_available():
            return []
        try:
            con = sqlite3.connect(
                f"file:{self._acervo_dir / 'acervo_manifest.sqlite'}?mode=ro",
                uri=True, timeout=10)
            tables = [r[0] for r in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")]
            table = next((t for t in tables
                          if "catalogo" in t or "doc" in t or "chunk" in t),
                         tables[0] if tables else None)
            if not table:
                con.close()
                return []
            cols = [r[1] for r in con.execute(f"PRAGMA table_info({table})")]
            text_cols = [c for c in cols
                         if any(k in c.lower() for k in
                                ("titulo", "texto", "content", "nome", "chunk"))]
            if not text_cols:
                con.close()
                return []
            where = " OR ".join(f"{c} LIKE ?" for c in text_cols)
            rows = con.execute(
                f"SELECT * FROM {table} WHERE {where} LIMIT ?",
                tuple([f"%{query}%"] * len(text_cols)) + (top_k,)).fetchall()
            con.close()
            return [dict(zip(cols, r)) for r in rows]
        except Exception:
            return []


_SINGLETON: MemtriasAI | None = None


def get_memtrias() -> MemtriasAI:
    global _SINGLETON
    if _SINGLETON is None:
        _SINGLETON = MemtriasAI()
    return _SINGLETON
