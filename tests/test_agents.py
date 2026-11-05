"""Tests for agents.

English: Tests for DebugAgent, AnalystAgent, ReviewerAgent.
pt-BR: Testes para agentes.
"""

from omni_coworker import AnalystAgent, DebugAgent, ReviewerAgent


def test_debug_agent():
    agent = DebugAgent()
    result = agent.diagnose("test error")
    assert result["agent"] == "DebugAgent"
    assert result["can_fix"] == False


def test_analyst_agent():
    agent = AnalystAgent()
    result = agent.analyze({"id": "test"})
    assert result["agent"] == "AnalystAgent"
    assert "reading" in result


def test_reviewer_agent():
    agent = ReviewerAgent()
    result = agent.review("print('hello')")
    assert result["agent"] == "ReviewerAgent"
    assert "approved" in result
