"""integration_loop — ciclo fechado de feedback da máquina (CPU/RAM).

English: Closed feedback loop over the machine's own production:
sensory_input → qualia → narrative → meaning_maker → expectation →
sensory_feedback. Consumes `kernel.*` mesh topics (kernel_daemon
bundle) and code-index context; publishes `feedback.loop` modulation.
CPU/RAM only — numpy, no torch.

pt-BR: Ciclo fechado de feedback sobre a própria produção da máquina:
sensory_input → qualia → narrative → meaning_maker → expectation →
sensory_feedback. Consome tópicos `kernel.*` da malha (bundle do
kernel_daemon) e contexto do code index; publica modulação em
`feedback.loop`. Somente CPU/RAM — numpy, sem torch.

Design basis: docs/design/OW-DSN-002_integration_loop.md.
"""

from .loop import IntegrationLoop, run_once, status

__all__ = ["IntegrationLoop", "run_once", "status"]
