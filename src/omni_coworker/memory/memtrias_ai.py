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
    Embedding default `auto`: `tardellirs/colibri-embed-ptbr` (nativo
    PT-BR, MTEB-BR 0.650, 157M params, Matryoshka 768d) tentado antes
    de `all-MiniLM-L6-v2` (`OMNI_MEMTRIAS_EMBEDDER=auto|ptbr|minilm|
    hash`; hash determinístico offline sempre funciona). Cada registro
    marca `analysis['embedder']`; recall prefere mesmo espaço vetorial
    (registros pré-tagging contam como 'hash'). Discriminação medida:
    colibri PT-BR 0.629 vs 0.229 no probe que MiniLM empatou 0.30/0.31;
    MiniLM é inglês-dominante (paráfrase EN 0.463 vs 0.024).

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

try:
    from .provenance import provenance_signature, classify_trust, quarantine_check
except Exception:  # pragma: no cover - fail-open
    def provenance_signature(content, source):  # type: ignore
        return ""
    def classify_trust(source, namespace):  # type: ignore
        return "unknown"
    def quarantine_check(content):  # type: ignore
        return {"quarantine": False, "reasons": []}

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
    if a.size != b.size:
        m = min(a.size, b.size)
        if m == 0:
            return 0.0
        a = a[:m]
        b = b[:m]
    na, nb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


_ST_MODELS: dict[str, Any] = {}
_ST_TRIED: set[str] = set()

# modelos ST suportados: spec -> HF id (ordem de tentativa no 'auto')
_ST_MODEL_IDS = {
    "ptbr": "tardellirs/colibri-embed-ptbr",      # nativo PT-BR (~600MB RAM), MTEB-BR 0.650, Matryoshka
    "minilm": "all-MiniLM-L6-v2",                  # 384d, mesmo do acervo
}
_AUTO_ORDER = ("ptbr", "minilm")


def _load_st(spec: str):
    """Carrega lazy o modelo ST do spec em RAM (CPU default); None se indisponível."""
    if spec in _ST_TRIED:
        return _ST_MODELS.get(spec)
    _ST_TRIED.add(spec)
    try:
        from sentence_transformers import SentenceTransformer
        device = os.getenv("OMNI_EMBED_DEVICE", "cpu")
        _ST_MODELS[spec] = SentenceTransformer(_ST_MODEL_IDS[spec], device=device)
    except Exception:
        _ST_MODELS[spec] = None
    return _ST_MODELS.get(spec)


def _st_embedder(spec: str) -> Callable[[str], list[float]]:
    """Retorna embedder real do modelo ST `spec` (dim nativa do modelo)."""
    def _fn(text: str) -> list[float]:
        model = _load_st(spec)
        if model is None:
            return hash_embedder(text)
        v = np.asarray(model.encode([text or ""])[0], dtype=np.float64)
        n = float(np.linalg.norm(v))
        return (v / n).tolist() if n > 0 else v.tolist()
    return _fn


def minilm_embedder(text: str, dim: int = EMBED_DIM) -> list[float]:
    """Embedder semântico real: all-MiniLM-L6-v2 (mesmo do acervo).

    Carrega lazy; fallback hash_embedder quando ST indisponível —
    nunca quebra o caminho de memória.
    """
    model = _load_st("minilm")
    if model is None:
        return hash_embedder(text, dim)
    emb = model.encode([text or ""])[0]
    v = np.asarray(emb, dtype=np.float64)
    if v.size != dim:
        out = np.zeros(dim)
        out[:min(dim, v.size)] = v[:min(dim, v.size)]
        v = out
    n = float(np.linalg.norm(v))
    return (v / n).tolist() if n > 0 else v.tolist()


def _pick_embedder(spec: str | None) -> tuple[Callable[[str], list[float]], str]:
    """Resolve embedder + nome honesto para marcação por registro.

    spec: 'ptbr' | 'minilm' | 'hash' | 'auto' (default) | None.
    'ptbr'/'minilm' → tenta o ST correspondente (marca o spec se
    carregar, 'hash' senão); 'auto' tenta ptbr→minilm (PT-BR é a língua
    de deploy); 'hash' → força hashing-trick.
    """
    spec = (spec or os.getenv("OMNI_MEMTRIAS_EMBEDDER") or "auto").lower()
    if spec == "hash":
        return hash_embedder, "hash"
    if spec in _ST_MODEL_IDS:
        if _load_st(spec) is not None:
            return _st_embedder(spec), spec
        return hash_embedder, "hash"  # pedido mas indisponível
    if spec == "auto":
        for s in _AUTO_ORDER:
            if _load_st(s) is not None:
                return _st_embedder(s), s
    return hash_embedder, "hash"


def _affect_analyzer(text: str) -> dict[str, Any]:
    """Motor afetivo léxico (AffectTracer): famílias afex + flattery."""
    try:
        from ..agency.affect_tracer import classify_flattery, score_turn

        fams = score_turn(text or "")
        flat = classify_flattery(text or "")
        active = {k: round(v, 4) for k, v in fams.items() if v > 0}
        return {"families": active, "flattery": flat.get("kind"),
                "flattery_score": flat.get("score")}
    except Exception:
        return {"families": {}, "flattery": "none", "flattery_score": 0.0}


class MemtriasAI:
    """Registro aberto de memórias topológicas por namespace."""

    def __init__(self, state_dir: Path | str | None = None,
                 embedder: Callable[[str], list[float]] | None = None,
                 acervo_dir: Path | str | None = None) -> None:
        self._dir = Path(state_dir) if state_dir else _state_dir()
        self._dir.mkdir(parents=True, exist_ok=True)
        if embedder is not None:
            self._embedder, self._embedder_name = embedder, "custom"
        else:
            self._embedder, self._embedder_name = _pick_embedder(None)
        self._namespaces: set[str] = set(CANONICAL_NAMESPACES)
        self._acervo_dir = Path(acervo_dir or os.getenv("OMNI_ACERVO_DIR", "")) \
            if (acervo_dir or os.getenv("OMNI_ACERVO_DIR")) else None
        self._analyzers: dict[str, Callable[[str], dict[str, Any]]] = {}
        self.register_analyzer("affect", _affect_analyzer)
        con = sqlite3.connect(self._dir / _DB, timeout=10)
        con.execute(
            "CREATE TABLE IF NOT EXISTS memories("
            "id TEXT PRIMARY KEY, namespace TEXT, content TEXT,"
            " embedding TEXT, tags TEXT, instance TEXT, chat_id TEXT,"
            " doc_ref TEXT, state_ref TEXT, affect TEXT, events TEXT,"
            " analysis TEXT, ts REAL)")
        cols = {r[1] for r in con.execute("PRAGMA table_info(memories)")}
        for col in ("affect", "events", "analysis"):
            if col not in cols:
                con.execute(f"ALTER TABLE memories ADD COLUMN {col} TEXT")
        if "forgotten" not in cols:
            con.execute(
                "ALTER TABLE memories ADD COLUMN forgotten INTEGER DEFAULT 0")
        con.execute(
            "CREATE INDEX IF NOT EXISTS idx_mem_ns ON memories(namespace, ts)")
        con.commit()
        con.close()

    # ── analisadores modulares (registro aberto) ─────────────────────────

    def register_analyzer(self, name: str,
                          fn: Callable[[str], dict[str, Any]]) -> str:
        """Pluga classificador: fn(texto) -> dict gravado em analysis[name]."""
        name = (name or "").strip().lower()
        if not name or not callable(fn):
            raise ValueError("analyzer precisa de nome + callable")
        self._analyzers[name] = fn
        return name

    @property
    def analyzers(self) -> list[str]:
        return sorted(self._analyzers)

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
                 affect: dict[str, Any] | None = None,
                 events: list[dict[str, Any]] | None = None,
                 ts: float | None = None) -> dict[str, Any]:
        """Inscreve memória: embute conteúdo + roda analisadores + persiste.

        `affect` explícito sobrescreve o inferido pelo motor afetivo;
        `events` guarda eventos associados (kernel, ciclo, auditoria).
        """
        ns = (namespace or "").strip().lower()
        if ns not in self._namespaces:
            self.register_namespace(ns)
        if not chat_id:
            chat_id = os.getenv("OMNI_DEFAULT_CHAT_ID", "omni-session")
        if state_ref is None:
            state_ref = {"tag": "auto", "ts": time.time() if ts is None else ts}
        # MINJA provenance guard (fail-open)
        try:
            q = quarantine_check(content)
        except Exception:
            q = {"quarantine": False, "reasons": ["guard_error"]}
        try:
            src_marker = doc_ref if doc_ref else instance
            tc = classify_trust(src_marker, ns)
            sig = provenance_signature(content, src_marker)
        except Exception:
            tc = "unknown"
            sig = ""
        quarantined = bool(q.get("quarantine"))
        provenance = {
            "signature": sig,
            "trust_class": tc,
            "quarantine": quarantined,
            "reasons": list(q.get("reasons") or []),
        }
        tags = list(tags or [])
        if quarantined and "quarantined" not in tags:
            tags = tags + ["quarantined"]
        emb = self._embedder(content or "")
        analysis: dict[str, Any] = {"embedder": self._embedder_name}
        for name, fn in self._analyzers.items():
            try:
                analysis[name] = fn(content or "")
            except Exception:
                analysis[name] = {"error": "analyzer_failed"}
        analysis["provenance"] = provenance
        inferred = analysis.get("affect") or {}
        rec = {
            "id": uuid.uuid4().hex[:16],
            "namespace": ns,
            "content": content or "",
            "tags": tags,
            "instance": instance,
            "chat_id": chat_id,
            "doc_ref": doc_ref,
            "state_ref": state_ref if isinstance(state_ref, str) or state_ref is None
                        else json.dumps(state_ref, default=str),
            "affect": affect if affect is not None else inferred,
            "events": events or [],
            "analysis": analysis,
            "provenance": provenance,
            "ts": float(ts or time.time()),
        }
        con = sqlite3.connect(self._dir / _DB, timeout=10)
        con.execute(
            "INSERT INTO memories(id,namespace,content,embedding,tags,"
            "instance,chat_id,doc_ref,state_ref,affect,events,analysis,ts)"
            " VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (rec["id"], ns, rec["content"], json.dumps(emb),
             json.dumps(rec["tags"]), instance, chat_id, doc_ref,
             rec["state_ref"], json.dumps(rec["affect"], default=str),
             json.dumps(rec["events"], default=str),
             json.dumps(analysis, default=str), rec["ts"]))
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
               recency_halflife_s: float | None = 86400.0,
               include_quarantined: bool = False,
               include_forgotten: bool = False) -> list[dict[str, Any]]:
        """Retrieval topológico: cosine(query) + filtros + recency decay.

        O "retorno do recalcado": o que foi inscrito volta quando a
        consulta o reconvoca — por proximidade vetorial e metadados.
        Registros esquecidos (tombstone) ficam fora salvo auditoria.
        """
        q = np.asarray(self._embedder(query or ""), dtype=np.float64)
        sql = "SELECT id,namespace,content,embedding,tags,instance,chat_id," \
              "doc_ref,state_ref,affect,events,analysis,ts" \
              " FROM memories WHERE 1=1"
        args: list[Any] = []
        if not include_forgotten:
            sql += " AND COALESCE(forgotten,0)=0"
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
        for (mid, ns, content, embj, tags, inst, cid, dref, sref,
             affect, events, analysis, ts) in rows:
            tlist = json.loads(tags or "[]")
            if (not include_quarantined) and "quarantined" in (tlist or []):
                continue
            emb = np.asarray(json.loads(embj), dtype=np.float64)
            score = _cosine(q, emb)
            if recency_halflife_s and ts:
                age = max(0.0, now - float(ts))
                score *= 0.5 + 0.5 * math.pow(0.5, age / recency_halflife_s)
            scored.append({"id": mid, "namespace": ns, "content": content,
                           "score": round(score, 6), "tags": json.loads(tags or "[]"),
                           "instance": inst, "chat_id": cid, "doc_ref": dref,
                           "state_ref": sref,
                           "affect": json.loads(affect or "null"),
                           "events": json.loads(events or "[]"),
                           "analysis": json.loads(analysis or "{}"),
                           "ts": ts})
        # espaços vetoriais diferentes não se comparam: prefere registros
        # do mesmo embedder. Registros sem marca são pré-tagging → foram
        # escritos pelo hash_embedder (único que existia) → "hash".
        # Cai para todos quando não há nenhum mesmo-embedder.
        same = [r for r in scored
                if ((r["analysis"] or {}).get("embedder") or "hash")
                == self._embedder_name]
        if same:
            scored = same
        scored.sort(key=lambda r: r["score"], reverse=True)
        return scored[:top_k]

    # ── engram: síntese dinâmica vs recuperação estática ────────────────

    def synthesize(self, query: str, *,
                   namespaces: list[str] | None = None,
                   top_k: int = 4) -> dict[str, Any]:
        """Síntese dinâmica: reconstrói uma "memória" misturando os top-k.

        Recuperação estática devolve o traço inscrito verbatim; a síntese
        reconstrói — embedding = média ponderada (por score) dos top hits,
        conteúdo = concatenação das fontes. Não persiste: é a memória
        reconstruída do engrama, não um novo traço.
        """
        hits = self.recall(query, namespaces=namespaces, top_k=top_k)
        if not hits:
            return {"query": query, "sources": [], "embedding": None,
                    "content": None, "diversity": 0}
        embs = []
        weights = []
        con = sqlite3.connect(self._dir / _DB, timeout=10)
        for h in hits:
            row = con.execute("SELECT embedding FROM memories WHERE id=?",
                              (h["id"],)).fetchone()
            if row and row[0]:
                embs.append(np.asarray(json.loads(row[0]), dtype=np.float64))
                weights.append(max(h["score"], 1e-6))
        con.close()
        blend = None
        if embs:
            w = np.asarray(weights) / sum(weights)
            blend = np.average(np.stack(embs), axis=0, weights=w)
        ns_set = {h["namespace"] for h in hits}
        return {"query": query,
                "sources": [{"id": h["id"], "namespace": h["namespace"],
                             "score": h["score"]} for h in hits],
                "embedding": blend.tolist() if blend is not None else None,
                "content": " || ".join(h["content"][:120] for h in hits),
                "diversity": len(ns_set)}

    def engram_benchmark(self, n_probes: int = 20, *,
                         seed: int = 0) -> dict[str, Any]:
        """Benchmark de alocação: recuperação estática vs síntese dinâmica.

        Probes derivadas de registros reais (substring do conteúdo):
        - estática: top-1 do recall retorna o registro-fonte? (hit rate,
          score médio)
        - síntese: cosine da mistura top-k vs probe + diversidade de fontes
        """
        con = sqlite3.connect(self._dir / _DB, timeout=10)
        rows = con.execute(
            "SELECT id, content FROM memories"
            " WHERE COALESCE(forgotten,0)=0"
            " AND content NOT NULL AND length(content)>=12"
            " ORDER BY ts DESC LIMIT 500").fetchall()
        con.close()
        if not rows:
            return {"n_probes": 0, "note": "sem registros para sondar"}
        rng = np.random.default_rng(seed)
        idx = rng.choice(len(rows), size=min(n_probes, len(rows)),
                         replace=False)
        probes = [(rows[i][0], rows[i][1]) for i in idx]
        static_hits, static_scores, syn_scores, syn_div = [], [], [], []
        for src_id, content in probes:
            probe = content[:max(12, len(content) // 2)]
            rec = self.recall(probe, top_k=1)
            if rec:
                static_hits.append(1 if rec[0]["id"] == src_id else 0)
                static_scores.append(rec[0]["score"])
            syn = self.synthesize(probe, top_k=4)
            if syn["embedding"] is not None:
                q = np.asarray(self._embedder(probe), dtype=np.float64)
                syn_scores.append(_cosine(q, np.asarray(syn["embedding"])))
                syn_div.append(syn["diversity"])
        return {
            "n_probes": len(probes),
            "static_hit_rate": (round(float(np.mean(static_hits)), 4)
                                if static_hits else None),
            "static_mean_score": (round(float(np.mean(static_scores)), 4)
                                  if static_scores else None),
            "synthesis_mean_score": (round(float(np.mean(syn_scores)), 4)
                                     if syn_scores else None),
            "synthesis_mean_diversity": (round(float(np.mean(syn_div)), 2)
                                        if syn_div else None),
            "note": ("estática = traço verbatim; síntese = reconstrução "
                     "dinâmica dos top-k (não persiste)")}

    # ── leitura afetiva do dia (motor afetivo) ───────────────────────────

    def daily_affect(self, day_ts: float | None = None, *,
                     instance: str | None = None,
                     namespaces: list[str] | None = None) -> dict[str, Any]:
        """Perfil afetivo do dia: agrega o campo affect dos registros.

        O "estado afetivo lido no dia pelo motor afetivo" — dominância de
        famílias afex, contagem de flattery, volume por namespace.
        """
        day = time.localtime(day_ts or time.time())
        start = time.mktime((day.tm_year, day.tm_mon, day.tm_mday,
                            0, 0, 0, 0, 0, -1))
        end = start + 86400
        sql = "SELECT namespace,affect FROM memories WHERE ts>=? AND ts<?"
        args: list[Any] = [start, end]
        if instance:
            sql += " AND instance=?"
            args.append(instance)
        if namespaces:
            sql += f" AND namespace IN ({','.join('?' * len(namespaces))})"
            args += [n.lower() for n in namespaces]
        con = sqlite3.connect(self._dir / _DB, timeout=10)
        rows = con.execute(sql, args).fetchall()
        con.close()
        fams: dict[str, float] = {}
        flattery: dict[str, int] = {}
        per_ns: dict[str, int] = {}
        n_aff = 0
        for ns, affj in rows:
            per_ns[ns] = per_ns.get(ns, 0) + 1
            aff = json.loads(affj or "{}") or {}
            if not aff:
                continue
            n_aff += 1
            for k, v in (aff.get("families") or {}).items():
                fams[k] = fams.get(k, 0.0) + float(v)
            kind = aff.get("flattery")
            if kind:
                flattery[kind] = flattery.get(kind, 0) + 1
        dominant = max(fams.items(), key=lambda kv: kv[1])[0] if fams else None
        return {"records": len(rows), "with_affect": n_aff,
                "dominant_family": dominant,
                "family_sums": {k: round(v, 4) for k, v in fams.items()},
                "flattery_counts": flattery, "per_namespace": per_ns,
                "day": time.strftime("%Y-%m-%d", day)}

    # ── esquecimento cirúrgico (tombstone + rollback + purge) ────────────

    @staticmethod
    def _forget_where(record_id=None, namespace=None, chat_id=None,
                      doc_ref=None, contains=None, before_ts=None):
        sql = " WHERE 1=1"
        args: list[Any] = []
        if record_id:
            sql += " AND id=?"
            args.append(record_id)
        if namespace:
            sql += " AND namespace=?"
            args.append(namespace.lower())
        if chat_id:
            sql += " AND chat_id=?"
            args.append(chat_id)
        if doc_ref:
            sql += " AND doc_ref=?"
            args.append(doc_ref)
        if contains:
            sql += " AND content LIKE ?"
            args.append(f"%{contains}%")
        if before_ts:
            sql += " AND ts<?"
            args.append(float(before_ts))
        return sql, args

    def forget(self, *, record_id=None, namespace=None, chat_id=None,
               doc_ref=None, contains=None, before_ts=None,
               dry_run=True) -> dict[str, Any]:
        """Esquecimento cirúrgico: tombstone escopado por id/ns/chat/doc.

        English: marks records forgotten=1 — excluded from recall;
        restore() rolls back; purge() hard-deletes tombstoned rows.
        Sem escopo algum, recusa (proteção contra amnésia total).
        pt-BR: esquecimento exato com rollback; dry_run só conta.
        """
        if not any([record_id, namespace, chat_id, doc_ref,
                    contains, before_ts]):
            return {"forgotten": 0, "error": "scope_required",
                    "dry_run": dry_run}
        where, args = self._forget_where(record_id, namespace, chat_id,
                                         doc_ref, contains, before_ts)
        con = sqlite3.connect(self._dir / _DB, timeout=10)
        n_target = con.execute(
            f"SELECT COUNT(*) FROM memories{where} AND COALESCE(forgotten,0)=0",
            args).fetchone()[0]
        if not dry_run and n_target:
            con.execute(
                f"UPDATE memories SET forgotten=1{where}"
                " AND COALESCE(forgotten,0)=0", args)
            con.commit()
        con.close()
        return {"forgotten": int(n_target), "dry_run": dry_run}

    def restore(self, *, record_id=None, namespace=None, chat_id=None,
                doc_ref=None, contains=None, before_ts=None) -> dict[str, Any]:
        """Rollback do esquecimento: desmarca tombstones no escopo."""
        where, args = self._forget_where(record_id, namespace, chat_id,
                                         doc_ref, contains, before_ts)
        where += " AND COALESCE(forgotten,0)=1"
        con = sqlite3.connect(self._dir / _DB, timeout=10)
        cur = con.execute(f"UPDATE memories SET forgotten=0{where}", args)
        con.commit()
        con.close()
        return {"restored": int(cur.rowcount)}

    def purge(self) -> dict[str, Any]:
        """Apaga definitivamente os registros tombstoned (sem rollback)."""
        con = sqlite3.connect(self._dir / _DB, timeout=10)
        cur = con.execute(
            "DELETE FROM memories WHERE COALESCE(forgotten,0)=1")
        con.commit()
        con.close()
        return {"purged": int(cur.rowcount)}

    def records_since(self, ts: float, *, limit: int = 50,
                      exclude_namespaces: tuple[str, ...] = ("dream",)
                      ) -> list[dict[str, Any]]:
        """Registros não-esquecidos com ts > marca (integração incremental)."""
        con = sqlite3.connect(self._dir / _DB, timeout=10)
        sql = ("SELECT id, namespace, content, ts FROM memories"
               " WHERE ts > ? AND COALESCE(forgotten,0)=0")
        args: tuple = (float(ts),)
        if exclude_namespaces:
            excl = ",".join("?" for _ in exclude_namespaces)
            sql += f" AND namespace NOT IN ({excl})"
            args += tuple(exclude_namespaces)
        rows = con.execute(f"{sql} ORDER BY ts ASC LIMIT ?",
                           (*args, int(limit))).fetchall()
        con.close()
        return [{"id": r[0], "namespace": r[1], "content": r[2], "ts": r[3]}
                for r in rows]

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

    def _acervo_faiss_search(self, query: str, top_k: int) -> list[dict[str, Any]]:
        """Recuperação vetorial real: MiniLM-L6-v2 → faiss → manifest rows."""
        try:
            import faiss
        except Exception:
            return []
        try:
            if not hasattr(self, "_acervo_idx"):
                self._acervo_idx = faiss.read_index(
                    str(self._acervo_dir / "acervo_index.faiss"))
            model = _load_st("minilm")
            if model is None:
                return []
            q = model.encode([query or ""])
            _d, idxs = self._acervo_idx.search(q, top_k)
            con = sqlite3.connect(
                f"file:{self._acervo_dir / 'acervo_manifest.sqlite'}?mode=ro",
                uri=True, timeout=10)
            out = []
            for rid, dist in zip(idxs[0], _d[0]):
                row = con.execute(
                    "SELECT doc_id, nome_arquivo, pagina, texto_snippet"
                    " FROM rows WHERE rid=?", (int(rid),)).fetchone()
                if row:
                    out.append({"doc_id": row[0], "nome_arquivo": row[1],
                                "pagina": row[2], "snippet": row[3],
                                "distance": float(dist)})
            con.close()
            return out
        except Exception:
            return []

    def acervo_search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Recuperação de obras do acervo (read-only, uso interno).

        Vetorial (faiss + MiniLM-L6-v2) quando disponível; fallback
        lexical no manifest. O acervo contém material de licença —
        nunca escreve nele e seus snippets não são publicáveis.
        """
        if not self.acervo_available():
            return []
        hits = self._acervo_faiss_search(query, top_k)
        if hits:
            return hits
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
