"""kernel_daemon — daemon de feedback mínimo da máquina (CPU/RAM).

English: Minimal machine-feedback daemon: collects brain activation
telemetry (jsonl tail), affect, soul and soma state plus the agents'
mesh production, aggregates a feature bundle per cycle and publishes
canonical `kernel.*` topics on the shared workspace. CPU/RAM only —
no torch; Rust kernels used via kernel_hooks when present.

pt-BR: Daemon de feedback mínimo da máquina: coleta telemetria de
ativações dos brains (tail jsonl), afeto, estado soul e soma, e a
produção dos agentes na malha, agrega um bundle de features por ciclo
e publica tópicos canônicos `kernel.*` no shared workspace. Somente
CPU/RAM — sem torch; kernels Rust via kernel_hooks quando presentes.

See docs/design/OW-DSN-001_kernel_rust_matrix.md (design basis).
"""

from .collector import collect_cycle
from .scheduler import KernelDaemon, status

__all__ = ["KernelDaemon", "collect_cycle", "status"]
