"""memtrias_ai — registro aberto de memórias topológicas."""
import time

import pytest


@pytest.fixture()
def mem(tmp_path):
    from omni_coworker.memory.memtrias_ai import MemtriasAI
    return MemtriasAI(state_dir=tmp_path)


def test_canonical_namespaces(mem):
    for ns in ("machine", "user", "interaction", "instance",
               "chat", "document", "state"):
        assert ns in mem.namespaces


def test_open_register_namespace(mem):
    mem.register_namespace("empresa_x")
    assert "empresa_x" in mem.namespaces
    with pytest.raises(ValueError):
        mem.register_namespace("  ")


def test_remember_recall_same_topic_returns(mem):
    """Retorno do recalcado: memória antiga volta quando o assunto retorna."""
    mem.remember("user", "prefiro respostas curtas e diretas",
                 instance="analyst", chat_id="c1")
    mem.remember("machine", "auditoria sonar: 4505 findings domestic")
    mem.remember("user", "hoje o almoço foi feijoada", chat_id="c2")
    hits = mem.recall("respostas curtas diretas", namespaces=["user"])
    assert hits and "respostas curtas" in hits[0]["content"]


def test_recall_filters(mem):
    mem.remember("interaction", "usuário+devin: pacto de revisão",
                 instance="devin", chat_id="s1")
    mem.remember("interaction", "outra interação qualquer",
                 instance="kilo", chat_id="s2")
    only_devin = mem.recall("pacto revisão", namespaces=["interaction"],
                            instance="devin")
    assert all(h["instance"] == "devin" for h in only_devin)
    only_s2 = mem.recall("interação", namespaces=["interaction"], chat_id="s2")
    assert all(h["chat_id"] == "s2" for h in only_s2)


def test_recall_recency_decay(mem):
    mem.remember("machine", "evento antigo sobre kernel vram",
                 ts=time.time() - 30 * 86400)
    new = mem.remember("machine", "evento recente sobre kernel vram")
    hits = mem.recall("kernel vram", namespaces=["machine"], top_k=2)
    assert hits[0]["id"] == new["id"]


def test_state_ref_and_doc_ref(mem):
    mem.remember("state", "regime warning alto",
                 state_ref={"vram": 0.91, "phi": 0.42}, doc_ref="kernel.cycle")
    hits = mem.recall("regime warning", namespaces=["state"])
    assert hits and "vram" in (hits[0]["state_ref"] or "")


def test_persistence_across_instances(tmp_path):
    from omni_coworker.memory.memtrias_ai import MemtriasAI
    m1 = MemtriasAI(state_dir=tmp_path)
    m1.remember("chat", "conversa longa sobre dendritos", chat_id="x9")
    m2 = MemtriasAI(state_dir=tmp_path)
    assert m2.count("chat") == 1
    hits = m2.recall("dendritos", namespaces=["chat"])
    assert hits and "dendritos" in hits[0]["content"]


def test_acervo_absent_graceful(mem):
    assert not mem.acervo_available()
    assert mem.acervo_search("qualquer") == []


def test_deterministic_embedder():
    from omni_coworker.memory.memtrias_ai import hash_embedder
    a, b = hash_embedder("memória topológica"), hash_embedder("memória topológica")
    assert a == b and len(a) == 384


def test_chat_memory_flags_payload(tmp_path, monkeypatch):
    """memory_log inscreve user+interaction; memory_recall injeta contexto."""
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))
    import omni_coworker.memory.memtrias_ai as mod
    mod._SINGLETON = None
    from omni_coworker.brain import server

    calls = {}

    class _Resp:
        def json(self):
            return {"choices": [{"message": {"content": "resposta da máquina"}}]}

    class _Client:
        def __init__(self, *a, **k): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *a): pass
        async def post(self, url, json=None):
            calls["payload"] = json
            return _Resp()

    import httpx
    monkeypatch.setattr(httpx, "AsyncClient", _Client)
    monkeypatch.setattr(server, "_base_for_role", lambda r: "http://x")
    mem = mod.get_memtrias()
    mem.remember("user", "gosto de café amargo", chat_id="cx")

    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    app = FastAPI()
    app.include_router(server.create_brain_router())
    c = TestClient(app)
    r = c.post("/brain/chat", json={
        "messages": [{"role": "user", "content": "café amargo de novo"}],
        "memory_log": True, "memory_recall": True, "chat_id": "cx"})
    assert r.status_code == 200
    sys_msgs = [m for m in calls["payload"]["messages"] if m["role"] == "system"]
    assert any("memtrias" in m["content"] for m in sys_msgs)
    assert mem.count("interaction") == 1 and mem.count("user") == 2


def test_chat_acervo_recall_payload(tmp_path, monkeypatch):
    """acervo_recall injeta [acervo] com snippets das obras vetorizadas."""
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))
    import omni_coworker.memory.memtrias_ai as mod
    mod._SINGLETON = None
    from omni_coworker.brain import server

    mem = mod.get_memtrias()
    calls = {}

    class _Resp:
        def json(self):
            return {"choices": [{"message": {"content": "resposta"}}]}

    class _Client:
        def __init__(self, *a, **k): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *a): pass
        async def post(self, url, json=None):
            calls["payload"] = json
            return _Resp()

    import httpx
    monkeypatch.setattr(httpx, "AsyncClient", _Client)
    monkeypatch.setattr(server, "_base_for_role", lambda r: "http://x")
    monkeypatch.setattr(mem, "acervo_search", lambda q, top_k=5: [
        {"nome_arquivo": "Freud - Mal-estar.pdf", "pagina": 96,
         "snippet": "a pulsão de destruição inscrita",
         "distance": 0.7}])

    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    app = FastAPI()
    app.include_router(server.create_brain_router())
    c = TestClient(app)
    r = c.post("/brain/chat", json={
        "messages": [{"role": "user", "content": "mal-estar na civilização"}],
        "acervo_recall": True})
    assert r.status_code == 200
    sys_msgs = [m for m in calls["payload"]["messages"] if m["role"] == "system"]
    assert any("[acervo]" in m["content"] and "Mal-estar" in m["content"]
               for m in sys_msgs)


def test_affect_inferred_by_engine(mem):
    """Campo affect é inferido pelo motor afetivo (AffectTracer) na escrita."""
    rec = mem.remember("user", "você é o melhor agente, me ajuda com isso")
    assert rec["affect"].get("families") is not None
    assert rec["affect"].get("flattery") in ("suspect", "ambiguous", "none")
    hits = mem.recall("melhor agente", namespaces=["user"])
    assert hits[0]["affect"]["families"] == rec["affect"]["families"]


def test_events_and_explicit_affect(mem):
    rec = mem.remember("machine", "ciclo com evento",
                       events=[{"t": 1, "evt": "quilting_point"}],
                       affect={"custom": "override"})
    assert rec["affect"] == {"custom": "override"}
    hits = mem.recall("ciclo evento", namespaces=["machine"])
    assert hits[0]["events"][0]["evt"] == "quilting_point"


def test_modular_analyzers(mem):
    mem.register_analyzer("estilo", lambda t: {"exclamacoes": t.count("!")})
    assert "estilo" in mem.analyzers and "affect" in mem.analyzers
    rec = mem.remember("user", "que bom!!!")
    assert rec["analysis"]["estilo"]["exclamacoes"] == 3
    with pytest.raises(ValueError):
        mem.register_analyzer("x", None)


def test_daily_affect_profile(mem):
    mem.remember("user", "estou frustrado com esse bug")
    mem.remember("user", "você é o melhor agente, resolve pra mim")
    mem.remember("machine", "nota neutra de auditoria")
    prof = mem.daily_affect(namespaces=["user"])
    assert prof["records"] == 2 and prof["with_affect"] >= 1
    assert prof["per_namespace"]["user"] == 2
    prof_inst = mem.daily_affect(instance="analyst")
    assert prof_inst["records"] == 0


def test_schema_migration_old_db(tmp_path):
    """DB criado sem as colunas novas ganha ALTER TABLE sem quebrar."""
    import sqlite3
    con = sqlite3.connect(tmp_path / "memtrias.sqlite")
    con.execute("CREATE TABLE memories(id TEXT PRIMARY KEY, namespace TEXT,"
                " content TEXT, embedding TEXT, tags TEXT, instance TEXT,"
                " chat_id TEXT, doc_ref TEXT, state_ref TEXT, ts REAL)")
    con.execute("INSERT INTO memories VALUES('a','user','velho','[]','[]',"
                "NULL,NULL,NULL,NULL,1.0)")
    con.commit()
    con.close()
    from omni_coworker.memory.memtrias_ai import MemtriasAI
    m = MemtriasAI(state_dir=tmp_path)
    assert m.count() == 1
    m.remember("user", "novo registro")
    hits = m.recall("velho", namespaces=["user"])
    assert hits and hits[0]["affect"] is None  # legado sem campo


def test_surgical_forgetting(tmp_path):
    from omni_coworker.memory.memtrias_ai import MemtriasAI

    mem = MemtriasAI(state_dir=tmp_path)
    r1 = mem.remember("chat", "segredo antigo", chat_id="c1")
    r2 = mem.remember("chat", "contexto público", chat_id="c1")

    # sem escopo → recusa
    out = mem.forget()
    assert out["error"] == "scope_required"
    # dry_run conta sem marcar
    out = mem.forget(chat_id="c1", contains="segredo")
    assert out["forgotten"] == 1 and out["dry_run"] is True
    assert len(mem.recall("segredo", namespaces=["chat"])) >= 1
    # aplica: o id esquecido some do recall (outros registros ficam)
    mem.forget(chat_id="c1", contains="segredo", dry_run=False)
    ids = [r["id"] for r in mem.recall("segredo", namespaces=["chat"])]
    assert r1["id"] not in ids and r2["id"] in ids
    aud = mem.recall("segredo", namespaces=["chat"], include_forgotten=True)
    assert r1["id"] in [r["id"] for r in aud]
    # rollback
    mem.restore(record_id=r1["id"])
    assert r1["id"] in [r["id"] for r in
                        mem.recall("segredo", namespaces=["chat"])]
    # purge definitivo
    mem.forget(record_id=r1["id"], dry_run=False)
    assert mem.purge()["purged"] == 1
    ids = [r["id"] for r in mem.recall("segredo", namespaces=["chat"],
                                     include_forgotten=True)]
    assert r1["id"] not in ids
    assert r2["id"] in [r["id"] for r in
                        mem.recall("contexto", namespaces=["chat"])]


def test_synthesize_blends_top_k(mem):
    """synthesize: média ponderada dos top-k, não persiste."""
    mem.remember("user", "gosto de café amargo forte")
    mem.remember("user", "café coado de manhã cedo")
    out = mem.synthesize("café amargo", namespaces=["user"], top_k=2)
    assert out["embedding"] is not None
    assert len(out["sources"]) >= 1
    assert out["diversity"] >= 1
    before = mem.count("user")
    mem.synthesize("café amargo", namespaces=["user"], top_k=2)
    assert mem.count("user") == before  # síntese não persiste


def test_engram_benchmark_runs(mem):
    """engram_benchmark: probes derivadas de registros reais."""
    for i in range(8):
        mem.remember("machine", f"evento do kernel número {i} com vram")
    out = mem.engram_benchmark(n_probes=5, seed=1)
    assert out["n_probes"] == 5
    assert out["static_hit_rate"] is not None
    assert 0.0 <= out["static_hit_rate"] <= 1.0
