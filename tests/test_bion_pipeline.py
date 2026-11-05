from datetime import datetime

from omni_coworker.psychoanalysis.alpha_element import AlphaElement
from omni_coworker.psychoanalysis.beta_element import BetaElement
from omni_coworker.psychoanalysis.bion_alpha_function import BionAlphaFunction


def test_transform_basic():
    beta = BetaElement(raw_data="hello world", timestamp=datetime.now(), emotional_charge=0.2, source="sensor")
    f = BionAlphaFunction(use_llm_symbolizer=False)
    alpha = f.transform(beta)
    assert isinstance(alpha, AlphaElement)
    assert alpha.content == "hello world"


def test_transform_mock_brain_chat(monkeypatch):
    import omni_coworker.agents._llm as llm
    monkeypatch.setattr(llm, "brain_chat", lambda *a, **k: "alpha simbolico pensavel para teste")
    # shared executor (2 workers) can be saturated by real brain calls from
    # earlier tests when brains are live — give the pending future room.
    monkeypatch.setenv("OMNI_WORKER_BION_SYMBOL_TIMEOUT", "30")
    beta = BetaElement(raw_data="raw", timestamp=datetime.now(), emotional_charge=0.1, source="sensor")
    f = BionAlphaFunction(use_llm_symbolizer=True)
    alpha = f.transform(beta)
    assert alpha is not None
    assert "alpha simbolico" in alpha.content


def test_batch_and_stats():
    betas = [BetaElement(raw_data=i, timestamp=datetime.now(), emotional_charge=0.1) for i in range(3)]
    f = BionAlphaFunction(use_llm_symbolizer=False, transformation_rate=0.7)
    alphas = f.transform_batch(betas)
    assert len(alphas) == 3
    stats = f.get_statistics()
    assert stats["total_processed"] == 3


def test_traumatic_high_charge():
    beta = BetaElement(raw_data="x", timestamp=datetime.now(), emotional_charge=0.95, source="sensor")
    f = BionAlphaFunction(transformation_rate=0.5, tolerance_threshold=0.8, use_llm_symbolizer=False)
    # low rate -> not processable
    assert f.transform(beta) is None
