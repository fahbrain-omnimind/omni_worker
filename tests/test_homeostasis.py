"""Tests for kernel_daemon.homeostasis (ported resource state machine)."""

from __future__ import annotations

import pytest

from omni_coworker.kernel_daemon.homeostasis import (
    HomeostaticController,
    TaskPriority,
)


@pytest.fixture
def ctl():
    return HomeostaticController()


def _soma(cpu=10, ram=30, disk=20, vram_used=5, vram_total=23):
    return {"cpu_percent": cpu, "ram_percent": ram,
            "disk": {"percent": disk},
            "gpu": {"gpus": [{"vram_used_gb": vram_used,
                              "vram_total_gb": vram_total}]}}


def test_state_machine_levels(ctl):
    assert ctl.regulate(_soma(cpu=10))["state"] == "optimal"
    assert ctl.regulate(_soma(cpu=65))["state"] == "good"
    assert ctl.regulate(_soma(cpu=85))["state"] == "warning"
    assert ctl.regulate(_soma(cpu=92))["state"] == "critical"
    assert ctl.regulate(_soma(cpu=97))["state"] == "emergency"


def test_vram_counts_as_resource(ctl):
    out = ctl.regulate(_soma(vram_used=21.5, vram_total=23))
    assert out["state"] == "critical"  # 93.5% vram
    assert out["metrics"]["vram_percent"] > 90


def test_emergency_throttles_and_recovers(ctl):
    ctl.regulate(_soma(cpu=97))
    assert ctl._throttled is True
    out = ctl.regulate(_soma(cpu=10))
    assert out["action"] == "throttle_released" and ctl._throttled is False


def test_sublimation_override(ctl):
    ctl.update_consciousness_state(0.5, TaskPriority.CRITICAL)
    out = ctl.regulate(_soma(cpu=97))
    assert out["action"] == "sublimated_override"
    assert ctl._throttled is False


def test_should_execute_task_gates(ctl):
    ctl.regulate(_soma(cpu=97))  # emergency
    assert ctl.should_execute_task(TaskPriority.CRITICAL) is True
    assert ctl.should_execute_task(TaskPriority.LOW) is False
    ctl.regulate(_soma(cpu=85))  # warning
    assert ctl.should_execute_task(TaskPriority.BACKGROUND) is False
    assert ctl.should_execute_task(TaskPriority.MEDIUM) is True


def test_kernel_cycle_publishes_homeostasis(tmp_path, monkeypatch):
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))
    from omni_coworker.kernel_daemon import collector, scheduler
    from omni_coworker.shared_workspace import bus, store
    store._reset(); bus._reset()
    log = tmp_path / "act.jsonl"; log.write_text("")
    monkeypatch.setattr(collector, "ACTIVATIONS_LOG", log)
    scheduler.run_cycle()
    ev = bus.latest("kernel.homeostasis")
    assert ev is not None and "state" in ev["payload"]
    bus._reset(); store._reset()


def test_phi_meta_window(tmp_path, monkeypatch):
    from omni_coworker.kernel_daemon import phi_meta
    phi_meta._reset()
    # independent flags → low phi; correlated flags → higher phi
    bundle = {"models": {"m": {"n_records": 2}},
              "affect": {"analyst": {"e": 1}, "executor": None},
              "soma": {"cpu_percent": 10,
                      "gpu": {"gpus": [{"power_w": 33.7, "temp_c": 71.0}]}},
              "soul": {"phi": 0.5},
              "homeostasis": {"state": "good"}, "mesh_topics": ["kernel.cycle"]}
    out = None
    for _ in range(6):
        out = phi_meta.update(bundle)
    assert out["phi_meta"] >= 0 and out["window"] == 6
    assert "activations" in out["elements"]
    # bit/Landauer layer: real power → real bit flow + integrated rate
    assert float(out["bit_flow_real_bits_s"]) > 0
    assert float(out["phi_bit_flow_rate_bits_s"]) >= 0
    assert out["vs_i5_ratio"] is not None and out["vs_i5_ratio"] > 0
    # pressure layer: no channels present → headroom 1, effective == rate
    assert out["pressure_load"] == 0.0
    assert float(out["phi_effective_bits_s"]) == float(
        out["phi_bit_flow_rate_bits_s"])
    # alternating states → more entropy/complexity
    phi_meta._reset()
    for i in range(6):
        b = dict(bundle); b["affect"] = {"analyst": {"e": 1} if i % 2 else None}
        out = phi_meta.update(b)
    assert out["complexity"] > 0
    phi_meta._reset()


def test_phi_meta_pressure_channels():
    """Pressure channels modulate effective bits; io weighted heaviest."""
    from omni_coworker.kernel_daemon import phi_meta
    phi_meta._reset()
    soma = {"cpu_percent": 10, "gpu_power_w": 33.7, "gpu_temp_c": 71.0,
            "psi_io_some": 50.0, "psi_mem_some": 10.0, "psi_cpu_some": 5.0,
            "load_per_core": 0.5,
            "gpu_vram_used_gb": 16.0, "gpu_vram_total_gb": 20.0}
    bundle = {"models": {"m": {"n_records": 2}},
              "affect": {"analyst": {"e": 1}}, "soma": soma,
              "soul": {"phi": 0.5}, "homeostasis": {"state": "good"},
              "mesh_topics": ["kernel.cycle"]}
    out = None
    for i in range(6):
        b = dict(bundle)
        b["affect"] = {"analyst": {"e": 1} if i % 2 else None}
        out = phi_meta.update(b)
    ch = out["pressure_channels"]
    assert ch["psi_io"] == 0.5 and ch["vram_ratio"] == 0.8
    assert ch["load_core"] == 0.5
    # weighted: .35*.5 + .25*.8 + .15*.1 + .15*.05 + .10*.5 = .4475
    assert out["pressure_load"] == 0.4475
    assert out["pressure_headroom"] == 0.5525
    assert float(out["phi_bit_flow_rate_bits_s"]) > 0
    assert float(out["phi_effective_bits_s"]) < float(
        out["phi_bit_flow_rate_bits_s"])
    # missing channels → weights renormalize over present ones
    phi_meta._reset()
    b2 = dict(bundle); b2["soma"] = {"cpu_percent": 10,
                                    "psi_io_some": 100.0}
    for _ in range(6):
        out = phi_meta.update(b2)
    assert out["pressure_load"] == 1.0 and out["pressure_headroom"] == 0.0
    assert float(out["phi_effective_bits_s"]) == 0.0
    phi_meta._reset()
