import pytest

from omni_coworker.soul import api


def test_static_files_serves_allowlisted_file(tmp_path, monkeypatch):
    static_dir = tmp_path / "static"
    static_dir.mkdir()
    asset = static_dir / "app.js"
    asset.write_text("asset", encoding="utf-8")
    monkeypatch.setattr(api, "STATIC_DIR", static_dir)
    monkeypatch.setattr(api, "STATIC_FILE_PATHS", {"app.js": asset})

    response = api.static_files("app.js")

    assert response.path == str(asset)


def test_static_files_rejects_unknown_file(tmp_path, monkeypatch):
    static_dir = tmp_path / "static"
    static_dir.mkdir()
    monkeypatch.setattr(api, "STATIC_DIR", static_dir)
    monkeypatch.setattr(api, "STATIC_FILE_PATHS", {"app.js": static_dir / "app.js"})

    assert api.static_files("../../etc/passwd") == {"error": "not found"}


def test_static_files_rejects_symlink_outside_static_dir(tmp_path, monkeypatch):
    static_dir = tmp_path / "static"
    static_dir.mkdir()
    outside_file = tmp_path / "secret.txt"
    outside_file.write_text("secret", encoding="utf-8")
    asset = static_dir / "app.js"
    try:
        asset.symlink_to(outside_file)
    except OSError:
        pytest.skip("symlinks are not supported")
    monkeypatch.setattr(api, "STATIC_DIR", static_dir)
    monkeypatch.setattr(api, "STATIC_FILE_PATHS", {"app.js": asset})

    assert api.static_files("app.js") == {"error": "not found"}
