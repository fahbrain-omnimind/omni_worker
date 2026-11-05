"""LalangueSandbox: língua interna + persistência entre restarts."""

from __future__ import annotations

from omni_coworker.narrative.lalangue import (
    LalangueSandbox,
    load_vocabulary,
    store_stats,
)


def test_emit_creates_and_matches():
    sb = LalangueSandbox()
    i1 = sb.emit([1.0, 0.0, 0.0])
    assert i1 == 0
    # mesmo vetor (ou quase) → mesma palavra, frequência sobe
    i2 = sb.emit([0.999, 0.001, 0.0])
    assert i2 == i1
    assert sb.vocabulary[0][1] == 2
    # vetor ortogonal → palavra nova
    i3 = sb.emit([0.0, 1.0, 0.0])
    assert i3 != i1


def test_emit_zero_and_full_vocab():
    sb = LalangueSandbox(vocab_size=1)
    assert sb.emit([0.0, 0.0]) == -1
    sb.emit([1.0, 0.0])
    assert sb.emit([0.0, 1.0]) == -1  # vocabulário cheio


def test_speak_to_self_records_dialogue():
    sb = LalangueSandbox()
    resp = sb.speak_to_self([0.5, 0.5, 0.5])
    assert len(resp) == 3
    assert len(sb.internal_dialogue) == 1
    d = sb.internal_dialogue[0]
    assert d["thought_idx"] >= 0 and d["self_resonance"] == 0.0


def test_persist_restore_survives_restart(tmp_path):
    db = tmp_path / "lalangue.sqlite"
    sb = LalangueSandbox()
    sb.emit([1.0, 0.0, 0.0])
    sb.emit([1.0, 0.0, 0.0])
    sb.speak_to_self([0.0, 1.0, 0.0])
    out = sb.persist(db)
    assert out["words_n"] == sb.get_vocabulary_stats()["size"]

    fresh = LalangueSandbox()
    n = fresh.restore(db)
    assert n == out["words_n"]
    # frequências preservadas: palavra 0 tinha freq 2
    assert fresh.vocabulary[0][1] == 2
    # emit continua casando com o vocabulário restaurado
    assert fresh.emit([1.0, 0.0, 0.0]) == 0


def test_store_stats_and_empty(tmp_path):
    db = tmp_path / "none.sqlite"
    assert store_stats(db)["present"] is False
    sb = LalangueSandbox()
    sb.emit([1.0, 0.0])
    sb.emit([1.0, 0.0])
    sb.speak_to_self([0.0, 1.0])
    sb.persist(db)
    stats = store_stats(db)
    assert stats["present"] and stats["words_n"] >= 1
    assert stats["dialogues_n"] == 1
    # frequências persistidas somam o nº de emissões que casaram palavras
    vocab = load_vocabulary(db)
    assert vocab[0]["frequency"] == 2
    assert sum(v["frequency"] for v in vocab) >= 3
