"""Additional tests for omni_coworker adapters.

English: Tests for agency, brain, soma integrations.
pt-BR: Testes para agency, brain, integrações soma.
"""

from omni_coworker import agency, brain, soma, safety, store


def test_agency_teleology():
    missions = agency.generate_missions({"cpu_high": True})
    assert isinstance(missions, list)
    omega = agency.compute_omega_teleology({"missions": missions})
    assert 0.0 <= omega <= 1.0


def test_agency_analyst():
    result = agency.analyze_session({"id": "test"})
    assert isinstance(result, dict)
    assert "status" in result


def test_agency_dream():
    result = agency.metabolize(120.0)
    assert isinstance(result, dict)
    assert "metabolized" in result


def test_agency_witness(tmp_path):
    path = tmp_path / "w.jsonl"
    agency.witness_event("test", {"x": 1}, path=str(path))
    events = agency.read_witness(path)
    assert len(events) == 1


def test_brain_affect():
    aff = brain.derive_affect()
    assert all(k in aff for k in ["phi", "psi", "sigma", "epsilon"])


def test_soma_probe():
    p = soma.probe()
    assert "cpu_percent" in p
    assert "ram_used_gb" in p


def test_safety_checks():
    assert safety.is_command_safe("ls -la")
    assert not safety.is_command_safe("rm -rf /")
    assert safety.validate_path("/content/test.txt")
    assert not safety.validate_path("/etc/passwd")


def test_node_db_extended(tmp_path):
    db = store.NodeDB(str(tmp_path / "n.db"))
    db.init()
    rid = db.add_mission("test spec")
    assert rid >= 1
    m = db.get_mission(rid)
    assert m["spec"] == "test spec"
    missions = db.list_missions()
    assert len(missions) >= 1
