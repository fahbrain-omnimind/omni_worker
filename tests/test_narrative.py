import pytest

from omni_coworker.narrative import IdentityConstruction, LifeStory


@pytest.fixture(autouse=True)
def state_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))


def test_identity_values_and_beliefs():
    ic = IdentityConstruction()
    bid = ic.belief_network.add_belief("truth matters", 0.9, 0.8)
    snap = ic.reflect_on_identity()
    assert snap.core_values
    assert snap.dominant_beliefs == ["truth matters"]
    ic.evolve({"truth": 0.5})
    assert ic.value_system.values["truth"].importance <= 1.0
    ic.belief_network.challenge_belief(bid, "counter", 0.5)
    assert ic.belief_network.beliefs[bid].certainty < 0.9


def test_life_story_persistence(tmp_path):
    ls = LifeStory()
    ev = ls.inscribe_narrative_event({"memory_context": "failure", "task_type": "x", "current_state": "growth"})
    assert ev.original_event.startswith("original event")
    assert ls.get_current_life_narrative()
    ls2 = LifeStory()
    assert len(ls2.narrative_events) == 1
    assert ls2.detect_narrative_instability() is None


def test_resignify_and_chain():
    ls = LifeStory()
    ls.add_event("success task")
    chain = ls.resignify_past("new signifier")
    assert isinstance(chain, list)
    assert ls.construct_narrative()
