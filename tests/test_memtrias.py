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
    old = mem.remember("machine", "evento antigo sobre kernel vram",
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

    import asyncio
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
