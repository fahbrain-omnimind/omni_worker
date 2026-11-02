"""ReviewerAgent - Revisão e validação.

English: Code review and validation agent.
pt-BR: Agente de revisão e validação de código.
"""

from __future__ import annotations

from typing import Any, Dict, List


class ReviewerAgent:
    """Agente de revisão de código"""
    
    def __init__(self, config: Dict[str, Any] | None = None):
        self.config = config or {}
        self.mode = "reviewer"
    
    def review(self, code: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """Review code.
        
        English: Reviews code for quality, style, security.
        pt-BR: Revisa código quanto à qualidade, estilo, segurança.
        """
        issues = []
        suggestions = []
        
        # Basic checks
        if "TODO" in code or "FIXME" in code:
            issues.append({"type": "todo", "severity": "low", "message": "TODO/FIXME found"})
        if "print(" in code and not code.strip().startswith('#'):
            suggestions.append("Consider using logging instead of print()")

        llm_verdict = None
        try:
            from ._llm import brain_chat_json
            from .persona import system_prompt

            llm_verdict = brain_chat_json(
                [
                    {
                        "role": "system",
                        "content": (
                            system_prompt("reviewer")
                            + "\n\n"
                            + "You are a strict code reviewer. Reply ONLY with JSON: "
                            '{"approved": bool, "issues": [{"severity": "low|medium|high", '
                            '"message": str}], "suggestions": [str], "score": 0..1}.'
                        ),
                    },
                    {"role": "user", "content": f"Review this code:\n```\n{code[:4000]}\n```"},
                ],
                role="analyst",
                max_tokens=300,
            )
        except Exception:
            llm_verdict = None

        if llm_verdict:
            issues.extend(llm_verdict.get("issues") or [])
            suggestions.extend(llm_verdict.get("suggestions") or [])
            approved = bool(llm_verdict.get("approved")) and not any(
                i.get("severity") == "high" for i in issues
            )
            score = float(llm_verdict.get("score", 0.9))
        else:
            approved = not any(i.get("severity") == "high" for i in issues)
            score = 0.9

        return {
            "agent": "ReviewerAgent",
            "approved": approved,
            "issues": issues,
            "suggestions": suggestions,
            "score": score,
            "llm": bool(llm_verdict),
        }
    
    def validate_tests(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate test results.
        
        English: Checks if tests meet coverage requirements.
        pt-BR: Verifica se testes atendem requisitos de cobertura.
        """
        passed = test_results.get("passed", 0)
        failed = test_results.get("failed", 0)
        total = passed + failed
        coverage = test_results.get("coverage", 0.0)
        
        return {
            "agent": "ReviewerAgent",
            "valid": failed == 0 and coverage >= 0.8,
            "passed": passed,
            "failed": failed,
            "coverage": coverage,
            "recommendation": "approve" if failed == 0 else "request_changes"
        }
