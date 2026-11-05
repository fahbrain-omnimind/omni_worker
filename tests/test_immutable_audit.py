"""Tests for audit.immutable_audit (canonical sha256+fcntl chain)."""

from __future__ import annotations

import json

from omni_coworker.audit.immutable_audit import GENESIS_HASH, ImmutableAuditSystem


def _read_events(audit: ImmutableAuditSystem) -> list[dict]:
    return [json.loads(line) for line in
            audit.audit_log_file.read_text().splitlines() if line.strip()]


def test_init_writes_system_event(tmp_path):
    a = ImmutableAuditSystem(tmp_path)
    evs = _read_events(a)
    assert evs[0]["action"] == "audit_system_initialized"
    assert evs[0]["prev_hash"] == GENESIS_HASH
    assert evs[0]["current_hash"]


def test_chain_links_events(tmp_path):
    a = ImmutableAuditSystem(tmp_path)
    h1 = a.log_action("probe", {"x": 1})
    h2 = a.log_action("gate", {"y": 2})
    evs = _read_events(a)
    assert evs[1]["current_hash"] == h1
    assert evs[2]["prev_hash"] == h1
    assert evs[2]["current_hash"] == h2


def test_verify_valid_chain(tmp_path):
    a = ImmutableAuditSystem(tmp_path)
    for i in range(5):
        a.log_action(f"act_{i}", {"i": i})
    res = a.verify_chain_integrity()
    assert res["valid"] is True
    assert res["events_verified"] == 6  # init + 5
    assert res["system_restarts"] == 1


def test_verify_detects_tamper(tmp_path):
    a = ImmutableAuditSystem(tmp_path)
    a.log_action("act", {"v": 1})
    a.log_action("act2", {"v": 2})
    lines = a.audit_log_file.read_text().splitlines()
    ev = json.loads(lines[1])
    ev["details"]["v"] = 999  # adultera conteúdo
    lines[1] = json.dumps(ev, sort_keys=True)
    a.audit_log_file.write_text("\n".join(lines) + "\n")
    res = a.verify_chain_integrity()
    assert res["valid"] is False
    assert any(c.get("hash_mismatch") for c in res["corrupted"])


def test_unconscious_not_auditable(tmp_path):
    a = ImmutableAuditSystem(tmp_path)
    h = a.log_action("repressed_content_return",
                     {"component": "QuantumUnconscious"})
    assert h == "unconscious_not_auditable"
    evs = _read_events(a)
    assert len(evs) == 1  # só o init


def test_restart_break_allowed(tmp_path):
    a = ImmutableAuditSystem(tmp_path)
    a.log_action("act", {"v": 1})
    a.log_action("audit_system_initialized", {"reason": "restart"})
    res = a.verify_chain_integrity()
    assert res["valid"] is True
    assert res["system_restarts"] == 2


def test_second_instance_continues_chain(tmp_path):
    """O log (não a memória) é a fonte da verdade do prev_hash."""
    a1 = ImmutableAuditSystem(tmp_path)
    h1 = a1.log_action("act", {"v": 1})
    a2 = ImmutableAuditSystem(tmp_path)  # "outro processo" no mesmo dir
    evs = _read_events(a2)
    # o init da segunda instância ancora no hash do log — restart marcado,
    # cadeia contínua (não bifurca)
    assert evs[-1]["action"] == "audit_system_initialized"
    assert evs[-1]["prev_hash"] == h1
    h2 = a2.log_action("act", {"v": 2})
    evs = _read_events(a2)
    assert evs[-1]["current_hash"] == h2
    res = a2.verify_chain_integrity()
    assert res["valid"] is True
    assert res["system_restarts"] == 2
    assert h1 != h2


def test_genesis_reanchor_allowed_on_restart(tmp_path):
    """Init com prev=genesis no meio do log = break controlado, não fraude."""
    a = ImmutableAuditSystem(tmp_path)
    a.log_action("act", {"v": 1})
    a.log_action("audit_system_initialized", {}, category="system")
    # reescreve o prev do segundo init como genesis (sidecar perdido)
    lines = a.audit_log_file.read_text().splitlines()
    ev = json.loads(lines[-1])
    ev["prev_hash"] = GENESIS_HASH
    ev["current_hash"] = a._hash_event(
        {k: ev.get(k) for k in ("action", "category", "details",
                                "timestamp", "datetime_utc", "prev_hash")})
    lines[-1] = json.dumps(ev, sort_keys=True)
    a.audit_log_file.write_text("\n".join(lines) + "\n")
    res = a.verify_chain_integrity()
    assert res["valid"] is True
    assert res["system_restarts"] == 2
