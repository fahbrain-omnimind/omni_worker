"""Tests for shared_workspace bus/store/schema (hermetic, tmp stores)."""

from __future__ import annotations

import pytest

from omni_coworker.shared_workspace import bus, schema, store


@pytest.fixture(autouse=True)
def _fresh(tmp_path, monkeypatch):
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))
    store._reset()
    bus._reset()
    yield
    bus._reset()
    store._reset()


def test_validate_rejects_noncanonical():
    with pytest.raises(ValueError):
        schema.validate("nonsense.topic", {})
    with pytest.raises(TypeError):
        schema.validate("soul.phi", object())


def test_publish_latest_history(tmp_path):
    evt = bus.publish("soul.phi", {"v": 0.27})
    assert evt["topic"] == "soul.phi"
    assert bus.latest("soul.phi")["payload"]["v"] == 0.27
    bus.publish("soul.phi", {"v": 0.30})
    assert len(bus.history("soul.phi", 10)) == 2
    assert bus.topics() == ["soul.phi"]


def test_subscribe_by_prefix():
    got = []
    bus.subscribe("soul", lambda t, e: got.append(t))
    bus.publish("soul.psi", {"v": 1})
    bus.publish("swap.state", {"v": 2})
    assert got == ["soul.psi"]


def test_bad_subscriber_isolated():
    bus.subscribe("kernel", lambda t, e: 1 / 0)
    evt = bus.publish("kernel.status", {"ok": True})
    assert evt["payload"]["ok"] is True


def test_write_through_to_sqlite(tmp_path):
    bus.publish("soma.probe", {"cpu": 12.5})
    rows = store.history("soma.probe", 5)
    assert len(rows) == 1 and rows[0]["payload"]["cpu"] == 12.5
    assert "soma.probe" in store.latest_per_topic()


def test_prune_retention():
    store.put(1.0, "soul.phi", {"v": 0})
    store.put(2.0, "soul.phi", {"v": 1})
    assert store.prune(older_than=1.5) == 1
    assert [r["payload"]["v"] for r in store.history("soul.phi", 10)] == [1]


def test_mesh_endpoints(tmp_path):
    from fastapi.testclient import TestClient
    from omni_coworker.app import create_app

    c = TestClient(create_app())
    r = c.post("/mesh/publish", json={"topic": "feedback.loop", "payload": {"meaning": 0.9}})
    assert r.status_code == 200 and r.json()["topic"] == "feedback.loop"
    r = c.get("/mesh/state")
    assert "feedback.loop" in r.json()["state"]
    r = c.post("/mesh/publish", json={"topic": "bad.topic", "payload": {}})
    assert r.status_code >= 400
