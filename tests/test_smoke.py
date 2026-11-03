"""Smoke tests for omni_coworker scaffold.

English: Hermetic CPU-only smoke tests.
pt-BR: Testes smoke herméticos apenas CPU.
"""

from omni_coworker.app import create_app
from omni_coworker.safety.jail import is_safe
from omni_coworker.brain.affect import derive_affect
from omni_coworker.soma.probe import probe
from omni_coworker.store.node_db import NodeDB


def test_app_create():
    app = create_app()
    assert app is not None


def test_sysmodules_endpoint():
    from fastapi.testclient import TestClient
    c = TestClient(create_app())
    d = c.get("/kernel/sysmodules").json()
    assert d["n_modules"] > 50
    assert "omni_coworker" in d["top_packages"]
    assert d["scale"].startswith("sys.modules")


def test_mesh_xray_snapshot(tmp_path, monkeypatch):
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location(
        "mesh_xray", Path(__file__).resolve().parents[1] / "scripts/mesh/mesh_xray.py")
    mx = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mx)
    monkeypatch.setattr(mx, "OUT", tmp_path / "x.json")
    rep = mx.snapshot()
    assert rep["L3_roles"]["infra"] >= 1
    assert any(e["kind"] == "spawn" for e in rep["edges"])
    assert "kernel" in rep["L0_chassis"]


def test_jail():
    assert is_safe("pytest -q")
    assert not is_safe("rm -rf /")


def test_affect():
    assert derive_affect()["phi"] == 0.0


def test_probe():
    p = probe()
    assert "cpu_percent" in p


def test_node_db(tmp_path):
    db = NodeDB(str(tmp_path / "n.db"))
    db.init()
    rid = db.add_mission("spec")
    assert rid >= 1
