"""omni-agent-coworker package (Kaggle Gemma 4 Best New Application).

English: Sovereign agentic coworker with somatic interoception, affect from tensors,
teleology, autopoietic governance, and Machine Public Soul.

pt-BR: Coworker agêntico soberano com interocepção somática, afeto derivado de
tensores, teleologia, governança autopoiética e Machine Public Soul.
"""

__version__ = "0.1.0"
__all__ = [
    "AnalystAgent",
    "CodeAgent",
    "DebugAgent",
    "ReviewerAgent",
    "agency",
    "agents",
    "app",
    "brain",
    "cli",
    "kernel_hooks",
    "orchestration",
    "safety",
    "server",
    "soma",
    "soul",
    "store",
]

from . import agents
from .agents.analyst_agent import AnalystAgent
from .agents.code_agent import CodeAgent
from .agents.debug_agent import DebugAgent
from .agents.reviewer_agent import ReviewerAgent
