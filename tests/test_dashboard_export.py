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
    assert data["witness"]["verified"] is True
    assert data["witness"]["last_sha256"] is not None


def test_no_simulated_values():
    res = dashboard_export.export(Path("/content/omni_worker"))
    # soul/kernel may be null (no real source wired) — never invented
    assert res["soul"] is None
    assert res["kernel"] is None
    # soma comes from real probe
    assert res["soma"]["cpu_percent"] is not None
