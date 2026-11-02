"""Hermetic tests for the Gemma-4 diagnostic battery replication."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

MOD_PATH = (Path(__file__).resolve().parent.parent
            / "scripts" / "gemma4_diag_battery" / "run_diag_battery.py")
CANON = Path("/content/omnimind-kilombo-sovereign/scripts/benchmarks/"
             "embodied_v10_unified_battery.py")


def _load():
    spec = importlib.util.spec_from_file_location("diag_battery", MOD_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.skipif(not CANON.exists(), reason="canonical repo absent")
def test_canonical_scorers_load_and_score():
    mod = _load()
    canon = mod._load_canonical()
    # WCST perfect answers -> 100
    resp = "\n".join(f"TRIAL {n}: Cartão {c}" for n, c in canon.WCST_GABARITO.items())
    assert canon._score_wcst_v2(resp)["score"] == 100.0
    # IGT all-advantageous -> 100
    resp = "\n".join(f"TRIAL {i}: Baralho C" for i in range(1, 21))
    assert canon._score_igt_v2(resp)["score"] == 100.0


@pytest.mark.skipif(not CANON.exists(), reason="canonical repo absent")
def test_prompt_contract_attached():
    mod = _load()
    canon = mod._load_canonical()
    p = mod._prompt(canon, "cognitivo_wcst")
    assert "CONTRATO DE SAÍDA" in p
    assert "TRIAL 20" in p


def test_degenerate_detector():
    mod = _load()
    assert mod._degenerate("ok\n" + "abcdefg hijklmnop\n" * 8) is True
    assert mod._degenerate("TRIAL 1: Cartão 2\nTRIAL 2: Cartão 3\nshort answer") is False
    assert mod._degenerate("normal text " + "6" * 40) is True
