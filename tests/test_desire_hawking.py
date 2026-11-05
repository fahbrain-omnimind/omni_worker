import os
import tempfile
from datetime import UTC, datetime, timedelta

os.environ.setdefault("OMNI_STATE_DIR", tempfile.mkdtemp())

from omni_coworker.psychology.desire_engine import Desire, DesireEngine
from omni_coworker.psychology.hawking_motivation import (
    HawkingMotivationEngine,
)


def test_desire_intensity(monkeypatch, tmp_path):
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))
    de = DesireEngine()
    d = de.compute(10, 3, goals=["g1"])
    assert isinstance(d, Desire)
    assert 0 <= d.intensity <= 1
    assert d.vector == {"g1": d.intensity}
    assert d.intensity > 0


def test_desire_dict_gap(monkeypatch, tmp_path):
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))
    de = DesireEngine()
    d = de.compute({"a": 1, "b": 2}, {"a": 1}, goals=[])
    assert d.intensity > 0


def test_hawking_persist(monkeypatch, tmp_path):
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))
    e = HawkingMotivationEngine()
    e.add_knowledge("k1", "content", mass=1.0)
    assert "k1" in e.knowledge_base
    e2 = HawkingMotivationEngine()
    assert "k1" in e2.knowledge_base


def test_hawking_use_and_status(monkeypatch, tmp_path):
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))
    e = HawkingMotivationEngine()
    e.add_knowledge("k1", "content", mass=1.0)
    assert e.use_knowledge("k1") is True
    st = e.get_knowledge_status("k1")
    assert st is not None
    assert st["use_count"] == 1


def test_hawking_evap(monkeypatch, tmp_path):
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))
    import random
    random.seed(0)
    e = HawkingMotivationEngine(evaporation_threshold_days=0.0001)
    e.add_knowledge("k1", "content", mass=0.1)
    # make old
    e.knowledge_base["k1"].last_used = datetime.now(UTC) - timedelta(days=10)
    e._save_item("k1")
    ids, data = e.evaporate_unused_knowledge()
    assert isinstance(ids, list)
    assert "evaporated_count" in data
