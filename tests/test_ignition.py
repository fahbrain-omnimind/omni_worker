"""Tests for kernel_daemon.ignition (GWT-lite broadcast texture)."""

from omni_coworker.kernel_daemon import ignition
from omni_coworker.shared_workspace import bus


def test_ignition_counts_distinct_prefixes():
    ignition._reset()
    ignition.cycle({})  # registers bus hook
    bus.publish("soul.phi", {"v": 1})
    bus.publish("soma.probe", {"psi": 0.5})
    bus.publish("kernel.phi_meta", {"phi_meta": 1.0})
    bus.publish("witness.append", {"e": "x"})
    out = ignition.cycle({"metastability": {"coherence_t": 0.7}})
    assert out["distinct_prefixes"] == 4
    assert set(out["prefixes"]) == {"kernel", "soma", "soul", "witness"}
    assert out["ignited"] is True
    assert out["scale"].startswith("prefix-count")


def test_ignition_respects_coherence_gate():
    ignition._reset()
    ignition.cycle({})
    for p in ("soul", "soma", "kernel", "agency"):
        bus.publish(f"{p}.x", {"v": 1})
    out = ignition.cycle({"metastability": {"coherence_t": 0.2}})
    assert out["distinct_prefixes"] == 4
    assert out["ignited"] is False  # coherent gate blocks


def test_synergy_grows_with_correlated_series():
    ignition._reset()
    ignition.cycle({})
    for _ in range(12):
        bus.publish("soul.x", {"v": 1})
        bus.publish("soma.x", {"v": 1})
        ignition.cycle({})
        ignition.cycle({})  # soul+soma OFF together → correlated
    out = ignition.cycle({})
    assert out["synergy_proxy"] > 0.0
