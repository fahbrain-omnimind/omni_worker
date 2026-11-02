"""AnalystAgent - Análise psicanalítica e clínica.

English: Psychoanalytic analyst agent.
pt-BR: Agente analista psicanalítico.
"""

from __future__ import annotations

from typing import Any, Dict


class AnalystAgent:
    """Agente de análise psicanalítica"""
    
    def __init__(self, config: Dict[str, Any] | None = None):
        self.config = config or {}
        self.mode = "analyst"
    
    def analyze(self, session: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """Analyze a session.

        English: Tries the canonical analyst adapter, then the analyst
        brain role; falls back to the static reading.
        pt-BR: Tenta o adapter analista canônico, depois o brain role
        analista; cai na leitura estática.
        """
        session = session or {}
        try:
            from ..agency.analyst import analyze_session
            result = analyze_session(session)
            data = result.get("data") or {}
            if result.get("source") not in (None, "fallback") and not data.get("error"):
                return {"agent": "AnalystAgent", "reading": data, **result}
        except Exception:
            pass
        try:
            from ._llm import brain_chat_json
            import json

            llm = brain_chat_json(
                [
                    {
                        "role": "system",
                        "content": (
                            "You are a clinical session analyst. Reply ONLY with "
                            'JSON: {"coherence": 0..1, "tension": 0..1, '
                            '"acceptance_criteria": [str, ...], "leitura_clinica": str}.'
                        ),
                    },
                    {"role": "user", "content": json.dumps(session, ensure_ascii=False)},
                ],
                role="analyst",
                max_tokens=300,
            )
            if llm:
                return {
                    "agent": "AnalystAgent",
                    "status": "analyzed",
                    "source": "brain:analyst",
                    "reading": llm,
                    "insights": [],
                }
        except Exception:
            pass
        return {
            "agent": "AnalystAgent",
            "status": "analyzed",
            "reading": {
                "coherence": 0.7,
                "tension": 0.3,
                "acceptance_criteria": [
                    "Maintain modular structure",
                    "Preserve separation of concerns",
                    "Ensure test coverage"
                ],
                "leitura_clinica": "Sessão mostra coerência estrutural adequada"
            },
            "insights": []
        }
    
    def interpret(self, context: str) -> Dict[str, Any]:
        """Interpret context.
        
        English: Provides interpretation.
        pt-BR: Fornece interpretação.
        """
        return {
            "agent": "AnalystAgent",
            "interpretation": "Context analysis pending",
            "symbols": []
        }
