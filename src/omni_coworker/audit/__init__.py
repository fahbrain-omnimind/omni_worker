"""audit — worker-owned immutable audit chain (canonical port).

English: Canonical `ImmutableAuditSystem` semantics at worker scale:
sha256 hash chain (prev_hash → current_hash over sorted JSON), fcntl
inter-process lock on a sidecar file, last-hash read from the log tail
(source of truth), restart-tolerant verification, and the
UNCONSCIOUS_COMPONENTS guard — the unconscious is not auditable.
pt-BR: Semântica canônica do `ImmutableAuditSystem` em escala worker:
cadeia sha256 (prev_hash → current_hash sobre JSON ordenado), lock
inter-processos fcntl em arquivo sidecar, último hash lido do fim do
log (fonte da verdade), verificação tolerante a restarts, e a guarda
UNCONSCIOUS_COMPONENTS — o inconsciente não é auditável.
"""

from .immutable_audit import ImmutableAuditSystem

__all__ = ["ImmutableAuditSystem"]
