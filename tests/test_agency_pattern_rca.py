import os
import tempfile

from omni_coworker.agency.pattern_watch import (
    detect_anomalies,
    detect_bias,
    detect_repetitive_behavior,
    diversity_score,
)
from omni_coworker.agency.rca import RCA, register_failure, trace_root_cause


def test_repetitive():
    ops = [{"tool_name": "a"}, {"tool_name": "b"}, {"tool_name": "a"}, {"tool_name": "b"}, {"tool_name": "a"}, {"tool_name": "b"}]
    r = detect_repetitive_behavior(ops)
    assert r["patterns"]
    assert r["patterns"][0]["sequence"] == ["a", "b"]


def test_bias():
    ops = [{"tool_name": "x"}] * 8 + [{"tool_name": "y"}] * 2
    r = detect_bias(ops, sensitivity=0.7)
    assert any(b["name"] == "x" for b in r["biases"])


def test_anomalies():
    ops = [{"tool_name": "t", "duration": 1, "success": True} for _ in range(5)] + [{"tool_name": "t", "duration": 100, "success": True}]
    r = detect_anomalies(ops)
    assert r["total_anomalies"] >= 1


def test_diversity():
    ops = [{"tool_name": "a"}, {"tool_name": "b"}, {"tool_name": "c"}]
    r = diversity_score(ops)
    assert r["diversity_score"] > 0
    assert r["unique_tools"] == 3


def test_rca_trace():
    rca = RCA()
    rca.add_component("api", ["db", "cache"])
    rca.add_component("db", [])
    rca.add_component("cache", [])
    fid = rca.register_failure("api", "timeout", 1)
    path = rca.trace_root_cause(fid)
    assert path[0] == "api"
    assert "db" in path or "cache" in path


def test_rca_module_level():
    os.environ["OMNI_STATE_DIR"] = tempfile.mkdtemp()
    fid = register_failure("worker", "crash", 2)
    path = trace_root_cause(fid)
    assert path and path[0] == "worker"
