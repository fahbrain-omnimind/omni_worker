"""soma.probe full telemetry + pluggable custom probes."""
import sys

import omni_coworker.soma.probe  # noqa: F401  (module, not the fn)

probe_mod = sys.modules["omni_coworker.soma.probe"]


def test_probe_full_fields():
    p = probe_mod.probe()
    for k in ("cpu_percent", "ram_used_gb", "ram_percent", "disk", "net",
              "psi", "procs", "load_per_core", "uptime_s", "custom", "virt"):
        assert k in p, k
    assert isinstance(p["custom"], dict)
    assert p["ram_percent"] >= 0
    assert p["cpu_count"] >= 1


def test_custom_probe_loaded(tmp_path, monkeypatch):
    (tmp_path / "mysensor.py").write_text(
        "def probe():\n    return {'reading': 42}\n")
    monkeypatch.setenv("OMNI_PROBES_DIR", str(tmp_path))
    monkeypatch.setattr(probe_mod, "_CUSTOM_PROBES", None)
    p = probe_mod.probe()
    assert p["custom"].get("mysensor") == {"reading": 42}
    monkeypatch.setattr(probe_mod, "_CUSTOM_PROBES", None)


def test_custom_probe_error_isolated(tmp_path, monkeypatch):
    (tmp_path / "bad.py").write_text(
        "def probe():\n    raise RuntimeError('boom')\n")
    monkeypatch.setenv("OMNI_PROBES_DIR", str(tmp_path))
    monkeypatch.setattr(probe_mod, "_CUSTOM_PROBES", None)
    p = probe_mod.probe()
    assert "error" in (p["custom"].get("bad") or {})
    monkeypatch.setattr(probe_mod, "_CUSTOM_PROBES", None)
