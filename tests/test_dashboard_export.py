import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import dashboard_export


def test_export_creates_valid_json(tmp_path):
    out = tmp_path / "latest.json"
    res = dashboard_export.export(Path("/content/omni_worker"))
    out.write_text(json.dumps(res))
    data = json.loads(out.read_text())
    assert data["source"] == "omni_worker real state"
    assert "exported_at" in data
    assert "witness" in data
    assert "soma" in data


def test_no_simulated_values():
    res = dashboard_export.export(Path("/content/omni_worker"))
    # soul/kernel are wired to real _compute_state() and shared_workspace.sqlite (or None if unavailable)
    assert res["soul"] is None or isinstance(res["soul"], dict)
    assert res["kernel"] is None or (isinstance(res["kernel"], dict) and "cycle_count" in res["kernel"])
