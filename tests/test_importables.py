"""Hermetic tests for the 5 importables (bus, governance, witness,
somatic store, persona) + CodeAgent trust integration.

English: No LLM, no backends, no network — pure-Python verification.
pt-BR: Sem LLM, sem backends, sem rede — verificação pura-Python.
"""

from __future__ import annotations

import json

import pytest

from omni_coworker.agency.witness import read_witness, verify_witness, witness_event
from omni_coworker.agents.bus import MessageBus
from omni_coworker.agents.code_agent import CodeAgent
from omni_coworker.agents.persona import load_persona, system_prompt
from omni_coworker.orchestration.governance import (
    CircuitBreaker,
    CircuitBreakerOpen,
    EventBus,
    OrchestratorMetrics,
    QuarantineSystem,
    RollbackSystem,
    TrustSystem,
)
from omni_coworker.soma.somatic_store import SomaticStore

# ── 1. MessageBus ────────────────────────────────────────────────────────────


def test_bus_publish_subscribe_roundtrip():
    bus = MessageBus()
    seen = []
    bus.subscribe("jobs", lambda m: seen.append(m))
    bus.publish("jobs", {"task": "t1", "weight": 1})
    bus.publish("jobs", {"task": "t2", "weight": 5})
    assert [m["task"] for m in seen] == ["t1", "t2"]
    assert len(bus.pending("jobs")) == 2
    # Unsubscribe stops delivery.
    handler = bus.subscribe("other", lambda m: None)
    assert bus.unsubscribe("other", handler) is True
    assert bus.unsubscribe("other", handler) is False


def test_bus_pending_and_consume():
    bus = MessageBus()
    bus.publish("q", {"id": 1})
    bus.publish("q", {"id": 2})
    assert bus.size("q") == 2
    assert bus.consume("q")["id"] == 1
    assert bus.pending("q")[0]["id"] == 2
    assert bus.consume("q")["id"] == 2
    assert bus.consume("q") is None


def test_bus_conflict_resolution_weight_wins():
    bus = MessageBus()
    bus.publish("ch", {"agent": "a", "weight": 1})
    bus.publish("ch", {"agent": "b", "weight": 3})
    bus.publish("ch", {"agent": "c", "weight": 2})
    winner = bus.conflict_resolution("ch")
    assert winner["agent"] == "b"
    assert len(bus.conflicts()) == 1
    assert bus.conflicts()[0]["winner"] == "b"


def test_bus_conflict_tie_breaks_by_last_writer():
    bus = MessageBus()
    bus.publish("ch", {"agent": "a", "weight": 1, "ts": "2026-01-01T00:00:00Z"})
    bus.publish("ch", {"agent": "b", "weight": 1, "ts": "2026-01-02T00:00:00Z"})
    assert bus.conflict_resolution("ch")["agent"] == "b"
    assert bus.conflict_resolution("empty") is None


# ── 2. Governance ────────────────────────────────────────────────────────────


def test_trust_system_events_move_trust(tmp_path, monkeypatch):
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))
    ts = TrustSystem()
    assert ts.get_trust("CodeAgent") == pytest.approx(0.5)
    ts.record_event("tests_passed")
    assert ts.get_trust("CodeAgent") == pytest.approx(0.6)
    ts.record_event("review_dissent")
    assert ts.get_trust("CodeAgent") == pytest.approx(0.4)
    # Cap at 1.0.
    for _ in range(10):
        ts.record_event("tests_passed")
    assert ts.get_trust("CodeAgent") == pytest.approx(1.0)
    # Floor at 0.0.
    ts2 = TrustSystem()
    for _ in range(10):
        ts2.record_event("review_dissent")
    assert ts2.get_trust("CodeAgent") == pytest.approx(0.0)
    # Unknown events are no-ops; per-agent isolation.
    assert ts.get_trust("ReviewerAgent") == pytest.approx(0.5)
    ts.record_event("unknown_event")
    assert ts.get_trust("CodeAgent") == pytest.approx(1.0)


def test_circuit_breaker_opens_after_n_failures():
    cb = CircuitBreaker(failure_threshold=3)
    assert cb.is_available()
    cb.record_failure()
    cb.record_failure()
    assert cb.is_available()
    cb.record_failure()
    assert not cb.is_available()
    assert cb.get_stats()["state"] == "open"
    with pytest.raises(CircuitBreakerOpen):
        cb.call_with_protection(lambda: 1)
    cb.record_success()
    assert cb.get_stats()["failure_count"] == 0


def test_circuit_breaker_call_protection():
    cb = CircuitBreaker(failure_threshold=2)

    def boom():
        raise ValueError("boom")

    with pytest.raises(ValueError):
        cb.call_with_protection(boom)
    assert cb.is_available()
    with pytest.raises(ValueError):
        cb.call_with_protection(boom)
    assert not cb.is_available()
    with pytest.raises(CircuitBreakerOpen):
        cb.call_with_protection(lambda: 42)
    cb.reset()
    assert cb.is_available()
    assert cb.call_with_protection(lambda: 7) == 7


def test_orchestrator_metrics_push_and_mean():
    om = OrchestratorMetrics()
    om.push("gen", 0.5, True)
    om.push("gen", 1.5, True)
    om.push("gen", 1.0, True)
    assert om.mean("gen") == pytest.approx(1.0)
    assert om.count("gen") == 3
    om.push("gen", 2.0, False)
    summary = om.summary()
    assert summary["operations"]["gen"]["count"] == 4
    assert summary["operations"]["gen"]["errors"] == 1
    assert om.mean("never_seen") == 0.0


def test_event_bus_publish_subscribe_history():
    bus = EventBus()
    seen = []
    bus.subscribe("tests_passed", lambda event_type, data: seen.append(data))
    bus.publish("tests_passed", {"suite": "importables"})
    bus.publish("review_dissent", {"by": "judge2"})
    assert len(seen) == 1
    assert len(bus.history("tests_passed")) == 1
    assert len(bus.history()) == 2


def test_quarantine_and_rollback_smoke():
    q = QuarantineSystem()
    q.quarantine("agent-b", "repeated failures", {"failures": 3})
    assert q.is_quarantined("agent-b")
    assert q.quarantined() == ["agent-b"]
    assert q.release("agent-b") is True
    assert not q.is_quarantined("agent-b")

    rb = RollbackSystem(max_versions=3)
    v1 = rb.create_snapshot("worker", {"step": 1})
    v2 = rb.create_snapshot("worker", {"step": 2})
    assert v2 > v1
    assert rb.get_current_version("worker") == v2
    assert rb.rollback_component("worker") == {"step": 2}
    assert rb.get_snapshot("worker", v1) == {"step": 1}
    assert rb.summary()["components"]["worker"]["version"] == v2


# ── 3. Witness hash-chain ────────────────────────────────────────────────────


def test_witness_hash_chain_valid(tmp_path):
    path = tmp_path / "w.jsonl"
    witness_event("alpha", {"x": 1}, path=str(path))
    witness_event("beta", {"x": 2}, path=str(path))
    witness_event("gamma", {"x": 3}, path=str(path))

    records = read_witness(path)
    assert len(records) == 3
    assert records[0]["prev_hash"] == ""
    assert records[1]["prev_hash"] == records[0]["hash"]
    assert records[2]["prev_hash"] == records[1]["hash"]
    assert all(r.get("hash") for r in records)

    result = verify_witness(path)
    assert result == {"valid": True, "records": 3, "broken_at": None}


def test_witness_corrupt_middle_hash_broken_at(tmp_path):
    path = tmp_path / "w.jsonl"
    witness_event("alpha", {}, path=str(path))
    witness_event("beta", {}, path=str(path))
    witness_event("gamma", {}, path=str(path))

    records = read_witness(path)
    records[1]["hash"] = "0" * 64
    path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n",
        encoding="utf-8",
    )
    result = verify_witness(path)
    assert result["valid"] is False
    assert result["broken_at"] == 1


def test_witness_legacy_records_without_hash_break(tmp_path):
    path = tmp_path / "legacy.jsonl"
    path.write_text(
        json.dumps({"type": "old", "data": {}}, ensure_ascii=False) + "\n"
        + json.dumps({"type": "old2", "data": {}}, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    result = verify_witness(path)
    assert result["valid"] is False
    assert result["broken_at"] == 0
    # Empty file is a valid (empty) chain.
    assert verify_witness(tmp_path / "missing.jsonl") == {
        "valid": True,
        "records": 0,
        "broken_at": None,
    }


# ── 4. SomaticStore ──────────────────────────────────────────────────────────


def test_somatic_store_record_recent_summary(tmp_path):
    store = SomaticStore(str(tmp_path / "soma.sqlite"))
    store.record(
        {
            "cpu_percent": 10.0,
            "ram_used_gb": 1.0,
            "ram_total_gb": 8.0,
            "swap_used_gb": 0.0,
            "load_avg": (0.5, 0.4, 0.3),
            "note": "first",
        }
    )
    store.record(
        {
            "cpu_percent": 20.0,
            "ram_used_gb": 2.0,
            "ram_total_gb": 8.0,
            "swap_used_gb": 1.0,
            "load_avg": (0.9, 0.8, 0.7),
        }
    )

    recent = store.recent(5)
    assert len(recent) == 2
    assert recent[0]["cpu"] == 10.0
    assert recent[1]["cpu"] == 20.0
    assert recent[0]["load1"] == pytest.approx(0.5)
    assert recent[0]["extra"] == {"note": "first"}

    summary = store.summary()
    assert summary["count"] == 2
    assert summary["cpu"] == pytest.approx(15.0)
    assert summary["ram_used_gb"] == pytest.approx(1.5)
    assert summary["swap_gb"] == pytest.approx(0.5)
    assert summary["load1"] == pytest.approx(0.7)


def test_somatic_store_empty_summary(tmp_path):
    store = SomaticStore(str(tmp_path / "empty.sqlite"))
    assert store.recent(5) == []
    assert store.summary()["count"] == 0


def test_probe_recorded(tmp_path):
    from omni_coworker.soma.probe import probe_recorded

    p = probe_recorded(path=str(tmp_path / "probes.sqlite"))
    assert "cpu_percent" in p
    assert p.get("recorded") is True
    assert len(SomaticStore(str(tmp_path / "probes.sqlite")).recent(5)) == 1


# ── 5. Persona ───────────────────────────────────────────────────────────────


def test_persona_load_fallback_missing_dir():
    p = load_persona("nonexistent_persona", config_dir="/nonexistent/dir")
    assert p["agent_name"] == "nonexistent_persona"
    assert p.get("fallback") is True
    assert p.get("mode") == "nonexistent_persona"


def test_persona_load_real_config():
    p = load_persona("architect")
    assert p.get("agent_name")
    assert p.get("mode")


def test_persona_system_prompt_judge_nonempty():
    sp = system_prompt("judge")
    assert isinstance(sp, str) and sp.strip()
    assert "judge" in sp.lower()
    assert "titan" in sp.lower()
    for role in ("debug", "analyst", "reviewer", "code"):
        assert system_prompt(role).strip()


def test_persona_role_mapping():
    from omni_coworker.agents.persona import ROLE_PERSONA_MAP

    assert ROLE_PERSONA_MAP["reviewer"] == "critic"
    assert ROLE_PERSONA_MAP["code"] == "architect"
    assert ROLE_PERSONA_MAP["judge"] == "titan"


# ── 6. CodeAgent trust integration ───────────────────────────────────────────


class _FakeTrust:
    def __init__(self, level: float):
        self._level = level

    def get_trust(self, agent: str = "CodeAgent") -> float:
        return self._level


def _patch_payload():
    return {"passed": 1, "failed": 0}


def test_code_agent_low_trust_denied():
    agent = CodeAgent(trust_provider=_FakeTrust(0.1))
    result = agent.submit_patch("def f():\n    return 1\n", _patch_payload())
    assert result["submitted"] is False
    assert result["reason"] == "permission_denied"
    assert result["trust_level"] == pytest.approx(0.1)


def test_code_agent_high_trust_runs_gate():
    agent = CodeAgent(trust_provider=_FakeTrust(0.9))
    result = agent.submit_patch("def f():\n    return 1\n", _patch_payload())
    assert result["submitted"] is True
    assert "gate" in result


def test_code_agent_default_trust_system_fallback():
    # With no provider the governance TrustSystem is used (default 0.5),
    # which is below the modify_code threshold 0.8 -> denied, without
    # ever touching the LLM backends.
    agent = CodeAgent()
    result = agent.submit_patch("def f():\n    return 1\n", _patch_payload())
    assert result["submitted"] is False
    assert result["reason"] == "permission_denied"
    assert result["trust_level"] < 0.8