"""Tests for agency.dream.metabolize (real memory integration)."""

from __future__ import annotations

import json

import omni_coworker.memory.memtrias_ai as mem_mod
from omni_coworker.agency import dream


def _fresh(tmp_path, monkeypatch):
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))
    mem_mod._SINGLETON = None
    return mem_mod.get_memtrias()


def test_metabolize_integrates_new_records(tmp_path, monkeypatch):
    mem = _fresh(tmp_path, monkeypatch)
    mem.remember("user", "pediu revisão do gate")
    mem.remember("machine", "ciclo kernel regime stable")
    out = dream.metabolize(idle_seconds=120)
    assert out["metabolized"] == 2
    # brain analista pode estar online nesta VM — as duas fontes são
    # legítimas; o que importa é que um digest real foi produzido
    assert out["source"] in ("brain:analyst", "extractive")
    assert out["dream_id"]
    # a memória dream carrega os ids metabolizados
    hits = mem.recall("revisão gate", namespaces=["dream"], top_k=3)
    assert hits
    ev = hits[0]["events"][0]
    assert ev["type"] == "metabolize" and ev["source_count"] == 2


def test_metabolize_zero_when_nothing_new(tmp_path, monkeypatch):
    mem = _fresh(tmp_path, monkeypatch)
    mem.remember("user", "nada")
    dream.metabolize()
    out = dream.metabolize()
    assert out["metabolized"] == 0
    assert out["reason"] == "no_new_records"


def test_metabolize_mark_persists_and_excludes_dream(tmp_path, monkeypatch):
    mem = _fresh(tmp_path, monkeypatch)
    mem.remember("user", "primeiro resíduo")
    dream.metabolize()
    # dream records não são re-metabolizados (mark + namespace exclude)
    mark = json.loads((tmp_path / "metabolize_state.json").read_text())
    assert mark["last_ts"] > 0
    out = dream.metabolize()
    assert out["metabolized"] == 0
    assert mem.count("dream") == 1  # só um dream, não acumulou eco


def test_records_since_respects_mark(tmp_path, monkeypatch):
    mem = _fresh(tmp_path, monkeypatch)
    import time
    old = mem.remember("user", "velho", ts=time.time() - 100)
    new = mem.remember("user", "novo")
    recs = mem.records_since(time.time() - 50)
    ids = {r["id"] for r in recs}
    assert new["id"] in ids and old["id"] not in ids
    # dream namespace excluído por default
    mem.remember("dream", "sonho anterior")
    recs2 = mem.records_since(0)
    assert all(r["namespace"] != "dream" for r in recs2)
