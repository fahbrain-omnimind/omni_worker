"""DebugAgent - Diagnóstico e debug.

English: Debug agent for diagnosis and troubleshooting (read-only).
pt-BR: Agente de debug para diagnóstico e solução de problemas (somente leitura).
"""

from __future__ import annotations

from typing import Any, Dict


class DebugAgent:
    """Agente especializado em diagnóstico e debugging"""
    
    def __init__(self, config: Dict[str, Any] | None = None):
        self.config = config or {}
        self.mode = "debug"
        self.allowed_commands = ["ls", "cat", "grep", "find", "python3 -m pytest", "git status"]
    
    def diagnose(self, issue: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """Diagnose an issue.

        English: Calls the executor brain for a read-only diagnosis;
        falls back to a stub payload when the backend is down.
        pt-BR: Chama o brain executor para diagnóstico somente-leitura;
        cai em payload stub quando o backend está fora.
        """
        context = context or {}
        from ._llm import brain_chat_json

        llm = brain_chat_json(
            [
                {
                    "role": "system",
                    "content": (
                        "You are a read-only diagnostic agent. You may NOT edit "
                        "files or apply fixes. Analyze the issue and reply ONLY "
                        'with JSON: {"diagnosis": str, "root_cause": str, '
                        '"suggestions": [str, ...]}.'
                    ),
                },
                {"role": "user", "content": f"Issue: {issue}\nContext: {context}"},
            ],
            role="executor",
            max_tokens=300,
        ) or {}
        return {
            "agent": "DebugAgent",
            "issue": issue,
            "diagnosis": llm.get("diagnosis", "Analysis pending"),
            "suggestions": list(llm.get("suggestions") or []),
            "root_cause": llm.get("root_cause"),
            "can_fix": False,
            "llm": bool(llm),
            "note": "Read-only agent - delegate fixes to CodeAgent",
        }
    
    def analyze_logs(self, logs: str) -> Dict[str, Any]:
        """Analyze logs for errors.
        
        English: Scans logs for patterns.
        pt-BR: Examina logs em busca de padrões.
        """
        errors = []
        for line in logs.split('\n'):
            if any(err in line.lower() for err in ['error', 'exception', 'traceback', 'failed']):
                errors.append(line.strip())
        return {
            "agent": "DebugAgent",
            "errors_found": len(errors),
            "errors": errors[:10]
        }
    
    def suggest_fix(self, diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest fix for diagnosis.
        
        English: Provides fix suggestions.
        pt-BR: Fornece sugestões de correção.
        """
        return {
            "agent": "DebugAgent",
            "suggestions": diagnosis.get("suggestions", []),
            "priority": "medium"
        }
