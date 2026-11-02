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
