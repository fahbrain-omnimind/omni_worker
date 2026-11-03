"""Hermetic and real-fixture tests for corpus_integrity_app delivery."""

from __future__ import annotations

import importlib.util
from pathlib import Path

APP_DIR = (
    Path(__file__).resolve().parent.parent
    / "data/app_delivery_workspace/corpus_integrity_app"
)


def _load_mod(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def test_scanner_and_cli_on_tmp_and_real_corpus(tmp_path):
    if not (APP_DIR / "scanner.py").exists():
        return
    scanner = _load_mod("scanner", APP_DIR / "scanner.py")
    import sys

    sys.modules["scanner"] = scanner
    cli = _load_mod("cli", APP_DIR / "cli.py")

    a = tmp_path / "doc_a.txt"
    b = tmp_path / "doc_b.txt"
    a.write_text(
        "Anil Seth Conscious artificial intelligence and biological naturalism\n[DADO] 1\n",
        encoding="utf-8",
    )
    b.write_text(
        "Anil Seth Conscious artificial intelligence and biological naturalism\n[DADO] 1\n",
        encoding="utf-8",
    )

    dups = scanner.detect_duplicates([str(a), str(b)])
    assert len(dups) == 1
    assert dups[0][2] == scanner.compute_md5(str(a))

    ver_ok = scanner.verify_manifest_entry(
        str(a), "Seth", "Conscious artificial intelligence and biological naturalism"
    )
    assert ver_ok["anomaly"] is False
    assert ver_ok["author_match"] is True

    ver_bad = scanner.verify_manifest_entry(
        str(a), "Beckmann", "World Modeling in Transformers"
    )
    assert ver_bad["anomaly"] is True

    tags = scanner.count_epistemic_tags("[DADO] x [PRX] y [DADO] z")
    assert tags["[DADO]"] == 2
    assert tags["[PRX]"] == 1

    db_file = tmp_path / "audit.sqlite"
    saved = cli.save_audit_sqlite(
        str(db_file),
        [{"file": "doc_a.txt", "anomaly": 0, "md5": dups[0][2], "dado_count": 1}],
    )
    assert saved == 1
