"""kernel_daemon.collector — coleta incremental das fontes de produção.

Orquestração runtime / Runtime orchestration:
    Cada ciclo chama `collect_cycle()` que retorna um dict com:
      activations   — novos registros do jsonl de ativações (offset
                      persistido em `<log>.offset` para sobreviver a
                      restarts do daemon);
      affect        — GET /erika/affect por brain (timeout curto,
                      falha → None, nunca bloqueia o ciclo);
      soul          — `_compute_state()` in-process (sem self-HTTP);
      soma          — `soma.probe.probe()` in-process;
      mesh          — snapshot atual do barramento (produção dos
                      agentes/daemons já publicada).

Arquitetura / Architecture:
    O jsonl é o contrato de produção dos brains (não se toca no
    servidor); leitura é tail-incremental puro — I/O proporcional ao
    delta, não ao arquivo inteiro. Fontes HTTP são read-only e
    timeout-bounded.

pt-BR: coleta por ciclo — tail incremental do jsonl de ativações,
/erika/affect por brain, soul+soma in-process, snapshot da malha.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

ACTIVATIONS_LOG = Path(os.getenv(
    "ERIKA_ACTIVATIONS_LOG",
    "data/monitor/erika_torch_activations.jsonl",
))
_HTTP_TIMEOUT_S = 2.0


def _read_new_activations(log: Path = ACTIVATIONS_LOG) -> list[dict]:
    """Return records appended since the persisted offset."""
    off_path = log.with_suffix(log.suffix + ".offset")
    try:
        offset = int(off_path.read_text().strip())
    except Exception:  # noqa: BLE001
        offset = 0
    try:
        size = log.stat().st_size
    except OSError:
        return []
    if size < offset:  # log rotacionado/truncado — recomeça
        offset = 0
    records: list[dict] = []
    with open(log, "r", encoding="utf-8", errors="replace") as fh:
        fh.seek(offset)
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        new_offset = fh.tell()
    try:
        off_path.write_text(str(new_offset))
    except OSError:
        pass
    return records


def _http_json(url: str) -> dict | None:
    """Bounded GET; None on any failure (never blocks the cycle)."""
    try:
        import httpx
        r = httpx.get(url, timeout=_HTTP_TIMEOUT_S)
        return r.json() if r.status_code == 200 else None
    except Exception:  # noqa: BLE001
        return None


def _brain_affect(role: str) -> dict | None:
    try:
        from ..brain.server import _base_for_role
        return _http_json(f"{_base_for_role(role)}/erika/affect")
    except Exception:  # noqa: BLE001
        return None


def collect_cycle(log: Path | None = None) -> dict[str, Any]:
    """One collection pass over all production sources."""
    log = log or ACTIVATIONS_LOG
    soul = None
    try:
        from ..soul.api import _compute_state
        soul = _compute_state()
    except Exception:  # noqa: BLE001, S110
        pass
    soma = None
    try:
        from ..soma.probe import probe_recorded
        soma = probe_recorded()
    except Exception:  # noqa: BLE001, S110
        pass
    mesh = None
    try:
        from ..shared_workspace import bus
        mesh = bus.snapshot()
    except Exception:  # noqa: BLE001, S110
        pass
    return {
        "ts": time.time(),
        "activations": _read_new_activations(log or ACTIVATIONS_LOG),
        "affect": {r: _brain_affect(r) for r in ("analyst", "executor")},
        "soul": soul,
        "soma": soma,
        "mesh": mesh,
    }


def reset_offset(log: Path = ACTIVATIONS_LOG) -> None:
    """Forget the read offset (next cycle re-reads the whole log)."""
    try:
        log.with_suffix(log.suffix + ".offset").unlink()
    except OSError:
        pass
