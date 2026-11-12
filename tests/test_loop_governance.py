"""Tests for per-iteration governance wire in integration_loop.loop."""

from __future__ import annotations

import pytest

import omni_coworker.integration_loop.loop as loop_mod
import omni_coworker.orchestration.governance as gov_mod


@pytest.fixture
def _gov_env(tmp_path, monkeypatch):
    """Estado isolado: OMNI_STATE_DIR novo + resets dos singletons."""
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))
    loop_mod._GOV = None
    gov_mod._SHARED_TRUST = None
    yield tmp_path
    loop_mod._GOV = None
    gov_mod._SHARED_TRUST = None


def _bundle():
    """Bundle no schema real de collect_sensory (models = dict de stats)."""
    return {
        "models": {"analyst": {"prompt_tokens_mean": 12.0,
                               "gen_tokens_mean": 30.0,
                               "gen_tokens_max": 64.0,
                               "attention_entropy_mean": 1.1,
                               "hidden_norm_mean": 9.5,
                               "hidden_norm_std": 0.4,
                               "last_layer_norm_mean": 8.9,
                               "n_records": 24}},
        "soma": {"cpu_percent": 22.0, "gpu_vram_used_gb": 9.1,
                 "gpu_util_percent": 35.0},
        "soul": {"phi": 0.5, "psi": 0.4, "sigma": 0.3, "epsilon": 0.2},
        "affect": {},
        "mesh_topics": ["kernel"],
    }


def test_cycle_carries_governance_summary(_gov_env):
    out = loop_mod.run_once(_bundle())
    g = out["governance"]
    assert g is not None
    assert g["quarantined"] == []
    # todos os estágios passaram sob breaker — registrados no resumo
    assert "sensory_input" in g["breakers"]
    assert "meaning_maker" in g["breakers"]
    assert out["status"] in ("ok", "partial")


def test_eventbus_feeds_trust(_gov_env):
    """Ciclo ok → loop.cycle.completed alimenta o TrustSystem compartilhado."""
    loop_mod.run_once(_bundle())
    trust = gov_mod.get_trust_system()
    # integration_loop recebeu +0.01 do evento de ciclo
    assert trust.get_trust("integration_loop") > gov_mod.TrustSystem.DEFAULT_TRUST
    # estágios ok acumularam evidência própria
    assert trust.get_trust("stage.sensory_input") > \
        gov_mod.TrustSystem.DEFAULT_TRUST


def test_failing_stage_quarantined_and_skipped(_gov_env, monkeypatch):
    """Estágio falhando cronicamente: breaker abre → quarentena → skip
    permanente + witness — e o ciclo continua 'partial', não 'error'."""
    from omni_coworker.integration_loop import stages

    monkeypatch.setattr(
        stages, "meaning_maker",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    for _ in range(3):
        out = loop_mod.run_once(_bundle())
    assert out["status"] == "partial"
    mm = out["stage_states"]["meaning_maker"]
    assert mm["metadata"]["skipped"] in ("boom", "RuntimeError", "circuit_open",
                                         "quarantined")
    gov = loop_mod._GOV
    assert "stage.meaning_maker" in gov["quarantine"].quarantined()
    # 4º ciclo: skip vem da quarentena (não nem tenta)
    out = loop_mod.run_once(_bundle())
    assert out["stage_states"]["meaning_maker"]["metadata"]["skipped"] == \
        "quarantined"
    # confiança do estágio caiu com falha+quarentena
    trust = gov_mod.get_trust_system()
    assert trust.get_trust("stage.meaning_maker") < \
        gov_mod.TrustSystem.DEFAULT_TRUST
    # witness registrou o evento de quarentena
    from omni_coworker.agency.witness import read_witness
    types = [e.get("type") for e in read_witness()]
    assert "stage_quarantined" in types


def test_one_failure_keeps_other_stages(_gov_env, monkeypatch):
    """Uma falha isolada de qualia não derruba os demais estágios."""
    from omni_coworker.integration_loop import stages

    monkeypatch.setattr(
        stages, "qualia",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("qualia boom")))
    out = loop_mod.run_once(_bundle())
    assert out["status"] == "partial"
    assert out["stage_states"]["qualia"]["metadata"]["skipped"] in (
        "qualia boom", "RuntimeError"
    )
    # narrative + meaning_maker ainda correram (independentes de qualia)
    assert out["stage_states"]["narrative"]["embedding"]
    assert out["stage_states"]["meaning_maker"].get("metadata") is not None
