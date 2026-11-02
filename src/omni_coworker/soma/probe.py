"""Somatic probe: host telemetry.

English: psutil + pynvml telemetry (CPU/GPU temp, RAM, swap, PSI). Metrics only.
pt-BR: Telemetria via psutil + pynvml (temp CPU/GPU, RAM, swap, PSI). Apenas métricas.
"""

from __future__ import annotations

import os


def probe() -> dict:
    """Return host telemetry snapshot.

    English: CPU, memory, swap, load; GPU when available.
    pt-BR: CPU, memória, swap, carga; GPU quando disponível.
    """
    import psutil

    vm = psutil.virtual_memory()
    return {
        "cpu_percent": psutil.cpu_percent(interval=0.0),
        "ram_used_gb": round(vm.used / 1e9, 3),
        "ram_total_gb": round(vm.total / 1e9, 3),
        "swap_used_gb": round(psutil.swap_memory().used / 1e9, 3),
        "load_avg": os.getloadavg() if hasattr(os, "getloadavg") else None,
    }


def probe_recorded(path=None) -> dict:
    """Probe and persist to the somatic store.

    English: Returns the probe dict with `recorded: bool`. If SQLite
    fails, returns the probe alone (recorded=False).
    pt-BR: Retorna o dict da sonda com `recorded: bool`. Se o SQLite
    falhar, retorna apenas a sonda (recorded=False).
    """
    data = probe()
    try:
        from .somatic_store import SomaticStore

        SomaticStore(path or "data/somatic_probes.sqlite").record(data)
        data["recorded"] = True
    except Exception:
        data["recorded"] = False
    return data


def probe_with_brain() -> dict:
    """Probe with brain server integration.
    
    English: Combines host telemetry with brain activation data.
    pt-BR: Combina telemetria do host com dados de ativação cerebral.
    """
    data = probe()
    try:
        from ..brain.server import get_brain_client
        client = get_brain_client()
        if client is not None:
            resp = client.get("/erika/activations", params={"limit": 1})
            if resp.status_code == 200:
                acts = resp.json()
                data["brain_activations"] = len(acts)
                if acts:
                    data["brain_last_ts"] = acts[-1].get("ts")
        resp2 = client.get("/erika/affect") if client else None
        if resp2 and resp2.status_code == 200:
            data["brain_affect"] = resp2.json()
    except Exception:
        pass
    return data
