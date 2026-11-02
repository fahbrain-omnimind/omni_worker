"""omni-agent-coworker package (Kaggle Gemma 4 Best New Application).

English: Sovereign agentic coworker with somatic interoception, affect from tensors,
teleology, autopoietic governance, and Machine Public Soul.

pt-BR: Coworker agêntico soberano com interocepção somática, afeto derivado de
tensores, teleologia, governança autopoiética e Machine Public Soul.
"""

__version__ = "0.1.0"
__all__ = ["app", "cli", "brain", "soma", "agency", "safety", "soul", "store", "kernel_hooks", "agents", "orchestration", "server"]

from . import agents  # noqa: E402
from .agents.debug_agent import DebugAgent  # noqa: E402
from .agents.analyst_agent import AnalystAgent  # noqa: E402
from .agents.reviewer_agent import ReviewerAgent  # noqa: E402
from .agents.code_agent import CodeAgent  # noqa: E402