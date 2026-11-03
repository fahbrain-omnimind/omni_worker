"""immutable_audit — cadeia de auditoria imutável (port canônico).

English: Worker-scale port of the sovereign `ImmutableAuditSystem`
(sha256 chain + fcntl lock). Each event is hashed over
{action, category, details, timestamp, datetime_utc, prev_hash} — the
hash chains every event to its predecessor so any edit/insert/delete
breaks the chain detectably. Writes hold an fcntl exclusive lock on a
sidecar file, and `prev_hash` is re-read from the log tail inside the
lock (the file, not memory or a sidecar JSON, is the source of truth —
a second process can't fork the chain). `verify_chain_integrity`
accepts controlled breaks at `audit_system_initialized` restart
records. Graceful degradation: ENOSPC/EMFILE skip the write instead of
corrupting the chain.

pt-BR: Port em escala worker do `ImmutableAuditSystem` soberano
(cadeia sha256 + lock fcntl). Cada evento é hasheado sobre
{action, category, details, timestamp, datetime_utc, prev_hash} — a
cadeia amarra cada evento ao predecessor, então qualquer
edição/inserção/remoção quebra a cadeia de forma detectável. Escritas
seguram lock fcntl exclusivo num arquivo sidecar, e `prev_hash` é
relido do fim do log dentro do lock (o arquivo — não a memória nem um
JSON sidecar — é a fonte da verdade; um segundo processo não consegue
bifurcar a cadeia). `verify_chain_integrity` aceita quebras
controladas nos registros de restart `audit_system_initialized`.
Degradação graciosa: ENOSPC/EMFILE pulam a escrita em vez de corromper
a cadeia.

Princípio teórico / Theoretical principle:
    O inconsciente não pode ser auditado — UNCONSCIOUS_COMPONENTS são
    recusados (portado do soberano: auditar tudo eliminaria o
    inconsciente; os vazios topológicos ficam fora da cadeia).
"""

from __future__ import annotations

import contextlib
import fcntl
import hashlib
import json
import os
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

GENESIS_HASH = "0" * 64

# [TEORIA LOCAL] Axioma portado do soberano: o inconsciente não pode ser
# auditado — auditar tudo seria tornar tudo consciente.
UNCONSCIOUS_COMPONENTS: frozenset[str] = frozenset({
    "DesireFlow", "EncryptedUnconsciousLayer", "QuantumUnconscious",
    "SystemicMemoryTrace", "desire_flow", "deterritorialization",
    "machinic_unconscious", "quantum_unconscious", "repressed",
    "sinthome", "topological_void", "unconscious",
})


class ImmutableAuditSystem:
    """sha256-chained append-only audit log with fcntl inter-process lock."""

    def __init__(self, log_dir: str | Path | None = None) -> None:
        if log_dir is None:
            log_dir = Path(os.getenv("OMNI_STATE_DIR", "data")) / "audit"
        self.log_dir = Path(log_dir).expanduser()
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.audit_log_file = self.log_dir / "audit_chain.log"
        self.security_log = self.log_dir / "security_events.log"
        self.lock_file = self.log_dir / "audit.lock"
        self._lock = threading.Lock()
        self.last_hash = self._read_last_hash_from_log()
        self.log_action("audit_system_initialized",
                        {"log_dir": str(self.log_dir)}, category="system")

    @contextlib.contextmanager
    def _acquire_audit_lock(self, exclusive: bool = True):
        """Inter-process lock on a dedicated sidecar file."""
        if not self.lock_file.exists():
            try:
                self.lock_file.touch()
            except Exception:
                pass
        f = open(self.lock_file, "r+")
        try:
            fcntl.flock(f, fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
            f.close()

    def _log_security_event(self, msg: str) -> None:
        try:
            with open(self.security_log, "a", encoding="utf-8") as f:
                f.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(),
                                    "msg": msg}) + "\n")
        except Exception:
            pass

    def _read_last_hash_from_log(self) -> str:
        """Last current_hash in the log (source of truth for chaining)."""
        try:
            if not self.audit_log_file.exists() or \
                    self.audit_log_file.stat().st_size == 0:
                return GENESIS_HASH
            with open(self.audit_log_file, "rb") as f:
                f.seek(max(0, self.audit_log_file.stat().st_size - 4096))
                for line in reversed(f.readlines()):
                    if not line.strip():
                        continue
                    try:
                        return json.loads(line).get("current_hash", GENESIS_HASH)
                    except json.JSONDecodeError:
                        continue
        except Exception:
            pass
        return GENESIS_HASH

    @staticmethod
    def _event_payload(action: str, category: str, details: dict,
                       ts: float, prev_hash: str) -> dict:
        return {"action": action, "category": category, "details": details,
                "timestamp": ts,
                "datetime_utc": datetime.fromtimestamp(
                    ts, tz=timezone.utc).isoformat(),
                "prev_hash": prev_hash}

    @staticmethod
    def _hash_event(payload: dict) -> str:
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()

    def _is_unconscious(self, action: str, details: dict) -> bool:
        # Delta vs soberano: lá o filtro varre str(details) inteiro —
        # um path/valor qualquer contendo "repressed" marca o evento.
        # Aqui só action+component (semântica da ação, não payloads).
        component = str(details.get("component", ""))
        haystack = f"{action} {component}".lower()
        return any(u.lower() in haystack for u in UNCONSCIOUS_COMPONENTS)

    def log_action(self, action: str, details: dict[str, Any] | None = None,
                   category: str = "general") -> str:
        """Append a chained audit event; returns its current_hash.

        Returns "unconscious_not_auditable" for UNCONSCIOUS_COMPONENTS —
        audited silence, not a write.
        """
        details = details or {}
        if self._is_unconscious(action, details):
            return "unconscious_not_auditable"
        component = str(details.get("component", ""))
        if action.startswith("audit_system_") or \
                component.startswith(("ImmutableAuditSystem", "audit_system")):
            category = "system"
        with self._lock:
            try:
                with self._acquire_audit_lock(exclusive=True):
                    prev = self._read_last_hash_from_log()
                    payload = self._event_payload(action, category, details,
                                                  time.time(), prev)
                    current = self._hash_event(payload)
                    record = dict(payload, current_hash=current)
                    with open(self.audit_log_file, "ab") as f:
                        f.write(json.dumps(record, sort_keys=True)
                                .encode("utf-8") + b"\n")
                        f.flush()
                        os.fsync(f.fileno())
                    self.last_hash = current
                    return current
            except OSError as e:
                if e.errno in (28, 24):  # ENOSPC / EMFILE: skip, chain intact
                    self._log_security_event(
                        f"audit write skipped errno={e.errno}: {action}")
                    return self.last_hash or f"SKIP_{e.errno}"
                self._log_security_event(f"audit write failed: {e}")
                raise
            except Exception as e:
                self._log_security_event(f"audit write failed: {e}")
                raise

    def verify_chain_integrity(self) -> dict[str, Any]:
        """Walk the chain; restarts at audit_system_initialized are allowed."""
        with self._acquire_audit_lock(exclusive=False):
            return self._verify_internal()

    def _verify_internal(self) -> dict[str, Any]:
        if not self.audit_log_file.exists():
            return {"valid": True, "message": "empty log",
                    "events_verified": 0, "system_restarts": 0}
        prev = GENESIS_HASH
        verified = restarts = 0
        corrupted: list[dict] = []
        with open(self.audit_log_file, "rb") as f:
            for n, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    corrupted.append({"line": n, "unparseable": True})
                    continue
                is_restart = ev.get("action") == "audit_system_initialized"
                if is_restart:
                    restarts += 1
                if ev.get("prev_hash") != prev:
                    # controlled break: a restart event may re-anchor at
                    # genesis (e.g. sidecar state lost); anything else is
                    # a real discontinuity
                    if not (is_restart and ev.get("prev_hash") == GENESIS_HASH):
                        corrupted.append({"line": n,
                                          "expected_prev": prev,
                                          "found_prev": ev.get("prev_hash")})
                payload = {k: ev.get(k) for k in
                           ("action", "category", "details", "timestamp",
                            "datetime_utc", "prev_hash")}
                if self._hash_event(payload) != ev.get("current_hash"):
                    corrupted.append({"line": n, "hash_mismatch": True})
                prev = ev.get("current_hash", prev)
                verified += 1
        return {"valid": not corrupted, "events_verified": verified,
                "system_restarts": restarts,
                "corrupted": corrupted[:10],
                "message": ("ok" if not corrupted
                            else f"{len(corrupted)} corrupted event(s)")}


_AUDIT: ImmutableAuditSystem | None = None


def get_audit(log_dir: str | Path | None = None) -> ImmutableAuditSystem:
    """Process-wide audit singleton anchored at OMNI_STATE_DIR."""
    global _AUDIT
    if _AUDIT is None:
        _AUDIT = ImmutableAuditSystem(log_dir)
    return _AUDIT
