"""Tests for ARGON_WORKER_MAP P4/5d, P6, and P7 implementations."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from omni_coworker.activation_beta.dendritic_scan import (
    ipr_dim,
    scan_trajectory,
)
from omni_coworker.integration_loop.quilting import detect_quilting_point
from omni_coworker.kernel_hooks.compute import cosine_similarity
from omni_coworker.memory.memtrias_ai import _cosine as mem_cos
from omni_coworker.narrative.lalangue import _cosine as lalangue_cos
from omni_coworker.orchestration.governance import QuarantineSystem, TrustSystem
from omni_coworker.psychoanalysis.bion_symbolizer import _cosine_similarity as bion_cos
from omni_coworker.store.node_db import NodeDB


def test_p6_cosine_similarity_wired_consumers():
    v1 = [1.0, 0.0, 0.0, 1.0]
    v2 = [1.0, 0.0, 0.0, 1.0]
    v3 = [0.0, 1.0, 1.0, 0.0]

    assert abs(cosine_similarity(v1, v2) - 1.0) < 1e-6
    assert abs(bion_cos(v1, v2) - 1.0) < 1e-6
    assert abs(lalangue_cos([0.70710678, 0.70710678], [0.70710678, 0.70710678]) - 1.0) < 1e-5
    assert abs(mem_cos(np.array(v1), np.array(v3))) < 1e-6

    embs = [
        [0.9, 0.1, 0.0],
        [0.91, 0.09, 0.0],
        [0.905, 0.095, 0.0],
        [0.908, 0.092, 0.0],
    ]
    qp = detect_quilting_point(embs, ["t1", "t1", "t1", "t1"])
    assert qp is not None
    assert qp["fixed_topic"] == "t1"
    assert "mean_cosine" in qp
    assert qp["mean_cosine"] > 0.99


def test_p7_node_db_governance_persistence(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))

    ts = TrustSystem()
    after = ts.record_event("tests_passed", agent="CodeAgent")
    assert abs(after - 0.6) < 1e-6

    qs = QuarantineSystem()
    qs.quarantine("stage.qualia", "circuit_open", {"failures": 3})

    # Verify SQLite node.db directly
    db = NodeDB(str(tmp_path / "node.db"))
    scores = db.get_trust_scores()
    assert abs(scores["CodeAgent"] - 0.6) < 1e-6
    events = db.list_trust_events()
    assert len(events) == 1
    assert events[0]["event"] == "tests_passed"

    q_recs = db.get_quarantine_records()
    assert "stage.qualia" in q_recs
    assert q_recs["stage.qualia"]["reason"] == "circuit_open"

    # Remove JSON files and verify fallback reload from node.db
    for jf in tmp_path.glob("*.json"):
        jf.unlink()

    ts2 = TrustSystem()
    assert abs(ts2.get_trust("CodeAgent") - 0.6) < 1e-6

    qs2 = QuarantineSystem()
    assert qs2.is_quarantined("stage.qualia")
    qs2.release("stage.qualia")
    assert not db.get_quarantine_records()


def test_p4_dendritic_scan_and_vacilo_replay(tmp_path: Path):
    rng = np.random.default_rng(11)
    # 3D trajectory (L=8, steps=6, D=32)
    traj = rng.normal(0.0, 1.0, size=(8, 6, 32))
    res = scan_trajectory(traj, threshold=0.15)
    assert res["n_graph_nodes"] == 8
    assert res["dendritic_depth"] >= 0.0
    assert 0.0 <= res["morphology_score"] <= 1.0
    assert res["contract_retention_cosine"] is not None
    assert res["contract_drift"] is not None

    ipr, eff_r = ipr_dim(np.ones(16))
    assert abs(ipr - (1.0 / 16.0)) < 1e-5
    assert abs(eff_r - 1.0) < 1e-5

    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "run_freud10d_battery_replay",
        str(Path(__file__).resolve().parents[1] / "scripts/experiments/run_freud10d_battery_replay.py"),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    vac = mod.analyze_trajectory_vacilo(traj)
    assert vac["n_steps"] == 6
    assert vac["vacilo_regime"] in (
        "premature_closure_risk",
        "perseveration_plateau_risk",
        "balanced",
    )
    empty_rep = mod.replay_directory(tmp_path / "nonexistent")
    assert empty_rep["status"] == "NÃO LOCALIZADO"
