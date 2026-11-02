"""Tests for GPU/VM telemetry, soma->model injection, dodeca, dunker.

English: Hermetic — exercises adapters without requiring GPU, Rust
kernel, canonical repo or brain backends.
pt-BR: Hermético — exercita adaptadores sem exigir GPU, kernel Rust,
repo canônico ou backends brain.
"""

from omni_coworker.soma.probe import probe, soma_context_line
from omni_coworker.soul import dodeca as soul_dodeca
from omni_coworker.agency import dunker as agency_dunker


def test_probe_has_virt_block():
    p = probe()
    assert "virt" in p
    assert "container" in p["virt"]
    assert "platform" in p["virt"]
    assert "gpu" in p  # None on GPU-less hosts — key must exist


def test_soma_context_line_shape():
    line = soma_context_line()
    # line may be None only if probe itself fails — normally a string
    if line is not None:
        assert "cpu=" in line
        assert "virt=" in line


def test_soma_inject_disabled_env(monkeypatch):
    monkeypatch.setenv("OMNI_SOMA_INJECT", "0")
    from omni_coworker.agents import _llm

    msgs = [{"role": "user", "content": "hi"}]
    assert _llm._soma_inject(msgs) == msgs


def test_dodeca_all_houses_present():
    d = soul_dodeca.compute_dodeca({"phi": 0.5, "psi": 0.2, "sigma": 0.1, "epsilon": 0.1})
    assert d["n_total"] == 15
    for h in ("S01", "S04", "S07", "S10", "S15"):
        assert h in d["houses"]
        assert "formula" in d["houses"][h]
    assert d["active_face"] is not None


def test_dodeca_kernel_families_populate_faces():
    fake_kernel = {
        "affective_vector_28d": {
            "labels": ["xer-afex-angst", "rekh-afex-memory", "isfet-afex-chaos"],
            "values": [0.5, 0.9, 0.3],
        }
    }
    d = soul_dodeca.compute_dodeca({}, kernel_state=fake_kernel)
    assert d["houses"]["S11"]["value"] == 0.9
    assert d["houses"]["S13"]["value"] == 0.3


def test_dunker_adapter_returns_payload():
    d = agency_dunker.dunker_architecture(kernel_state=None)
    assert isinstance(d, dict)
    assert d.get("status") in ("ok", "unavailable", "error")
    assert d.get("families_used") == 0
