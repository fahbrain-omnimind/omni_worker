"""CodeAgent - Geração e submissão de código com portão.

English: Code agent that produces patches via the executor brain and
submits them only through the permission matrix + constitutional gate
(anti-impulsivity prosthesis: no submission without passing tests).
pt-BR: Agente de código que produz patches via brain executor e submete
somente através da matriz de permissões + portão constitucional
(prótese anti-impulsividade: sem submissão sem testes passando).
"""

from __future__ import annotations

from typing import Any


class CodeAgent:
    """Code generation agent with gated submission."""

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        trust_provider: Any | None = None,
    ):
        self.config = config or {}
        self.mode = "code"
        # Injected trust source (duck-typed: get_trust(agent=...) -> float).
        # Defaults to the governance TrustSystem; 0.9 if unavailable.
        self.trust_provider = trust_provider

    def _trust_level(self) -> float:
        """Resolve the agent's current trust level.

        English: Uses the injected trust_provider, else the governance
        TrustSystem; falls back to 0.9 when no provider is usable.
        pt-BR: Usa o trust_provider injetado, senão o TrustSystem de
        governança; cai em 0.9 quando nenhum provider é utilizável.
        """
        try:
            provider = self.trust_provider
            if provider is None:
                from ..orchestration.governance import get_trust_system

                provider = get_trust_system()
            return float(provider.get_trust(agent="CodeAgent"))
        except Exception:  # noqa: BLE001
            return 0.9

    def generate(self, spec: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Generate code for a spec via the executor brain.

        English: Executor role produces the patch; falls back to empty.
        pt-BR: Role executor produz o patch; cai em vazio.
        """
        from ._llm import brain_chat

        context = context or {}
        code = brain_chat(
            [
                {
                    "role": "system",
                    "content": (
                        "You are a surgical code agent. Produce only the code "
                        "for the spec below — no prose, no markdown fences."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Spec: {spec}\nContext: {context}",
                },
            ],
            role="executor",
            max_tokens=800,
            temperature=0.3,
        )
        return {"agent": "CodeAgent", "code": code or "", "llm": bool(code)}

    def submit_patch(
        self,
        code: str,
        test_results: dict[str, Any] | None = None,
        target_files: list[str] | None = None,
    ) -> dict[str, Any]:
        """Submit a patch through the safety plane.

        English: Refuses empty diffs and submissions without passing
        tests; runs permission matrix + constitutional gate.
        pt-BR: Recusa diffs vazios e submissões sem testes passando;
        executa matriz de permissões + portão constitucional.
        """
        from ..safety.gate import evaluate_action
        from ..safety.matrix import check_permission

        if not code.strip():
            return {"agent": "CodeAgent", "submitted": False, "reason": "empty_diff"}

        tests = test_results or {}
        if tests and tests.get("failed", 0) > 0:
            return {
                "agent": "CodeAgent",
                "submitted": False,
                "reason": "tests_failing",
                "failed": tests.get("failed"),
            }
        if test_results is not None and tests.get("passed", 0) <= 0:
            return {
                "agent": "CodeAgent",
                "submitted": False,
                "reason": "no_tests_passed",
            }

        # modify_code exige trust>=0.8 na matriz — testes passando + revisão
        # prévia são a evidência que eleva a confiança do agente (TrustSystem).
        trust_level = self._trust_level()
        if not check_permission("modify_code", {"trust_level": trust_level}):
            return {
                "agent": "CodeAgent",
                "submitted": False,
                "reason": "permission_denied",
                "trust_level": trust_level,
            }

        verdict = evaluate_action(
            "submit_patch",
            {
                "proponent": "CodeAgent",
                "target_files": target_files or [],
                "content": code[:4000],
            },
        )
        return {
            "agent": "CodeAgent",
            "submitted": bool(verdict.get("allowed")),
            "gate": verdict,
        }
