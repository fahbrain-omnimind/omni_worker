"""Somatic probe: host telemetry.

English: psutil + pynvml telemetry (CPU/GPU temp, RAM, swap, PSI) plus
virtualization detection (container / hypervisor / cloud platform).
Metrics only — no interpretation.
pt-BR: Telemetria via psutil + pynvml (temp CPU/GPU, RAM, swap, PSI) mais
detecção de virtualização (container / hypervisor / plataforma cloud).
Apenas métricas — sem interpretação.
"""

from __future__ import annotations

import os
import sys


def _gpu_probe() -> dict | None:
    """GPU telemetry snapshot.

    English: Tries pynvml first (precise per-device), falls back to
    `nvidia-smi` subprocess. Returns {"gpus": [...]} or None.
    pt-BR: Tenta pynvml primeiro (preciso por dispositivo), cai para
    subprocess `nvidia-smi`. Retorna {"gpus": [...]} ou None.
    """
    try:
        import pynvml  # type: ignore

        pynvml.nvmlInit()
        try:
            gpus = []
            for i in range(pynvml.nvmlDeviceGetCount()):
                h = pynvml.nvmlDeviceGetHandleByIndex(i)
                mem = pynvml.nvmlDeviceGetMemoryInfo(h)
                name = pynvml.nvmlDeviceGetName(h)
                g = {
                    "index": i,
                    "name": name.decode() if isinstance(name, bytes) else name,
                    "temp_c": pynvml.nvmlDeviceGetTemperature(h, pynvml.NVML_TEMPERATURE_GPU),
                    "util_percent": pynvml.nvmlDeviceGetUtilizationRates(h).gpu,
                    "vram_used_gb": round(mem.used / 1e9, 3),
                    "vram_total_gb": round(mem.total / 1e9, 3),
                }
                try:
                    g["power_w"] = round(pynvml.nvmlDeviceGetPowerUsage(h) / 1000.0, 1)
                except Exception:
                    pass
                gpus.append(g)
            return {"gpus": gpus} if gpus else None
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:
                pass
    except Exception:
        pass

    try:
        import csv
        import io
        import subprocess

        r = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,temperature.gpu,utilization.gpu,memory.used,memory.total,power.draw",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if r.returncode != 0:
            return None
        gpus = []
        for i, row in enumerate(csv.reader(io.StringIO(r.stdout.strip()))):
            if len(row) < 5:
                continue
            g = {
                "index": i,
                "name": row[0].strip(),
                "temp_c": float(row[1]),
                "util_percent": float(row[2]),
                "vram_used_gb": round(float(row[3]) / 1024.0, 3),
                "vram_total_gb": round(float(row[4]) / 1024.0, 3),
            }
            if len(row) > 5 and row[5].strip() not in ("[N/A]", "N/A"):
                try:
                    g["power_w"] = float(row[5])
                except ValueError:
                    pass
            gpus.append(g)
        return {"gpus": gpus} if gpus else None
    except Exception:
        return None


def _virt_probe() -> dict:
    """Detect virtualization / container / cloud platform.

    English: container flag (/.dockerenv, cgroup), hypervisor flag
    (/proc/cpuinfo), DMI vendor/product match (KVM, QEMU, VMware, Xen,
    Hyper-V, GCE, EC2), systemd-detect-virt, and platform hints
    (KAGGLE_*, COLAB_*, /content).
    pt-BR: flag de container (/.dockerenv, cgroup), flag de hypervisor
    (/proc/cpuinfo), casamento DMI vendor/product (KVM, QEMU, VMware, Xen,
    Hyper-V, GCE, EC2), systemd-detect-virt, e pistas de plataforma
    (KAGGLE_*, COLAB_*, /content).
    """
    from pathlib import Path

    info: dict = {"container": False, "vm": None, "hypervisor_flag": False, "platform": "metal"}

    try:
        cgroup = Path("/proc/1/cgroup").read_text(encoding="utf-8", errors="ignore")
        info["container"] = (
            Path("/.dockerenv").exists()
            or Path("/run/.containerenv").exists()
            or any(s in cgroup for s in ("docker", "kubepods", "containerd", "podman"))
        )
    except Exception:
        info["container"] = Path("/.dockerenv").exists()

    try:
        info["hypervisor_flag"] = "hypervisor" in Path("/proc/cpuinfo").read_text(
            encoding="utf-8", errors="ignore"
        )
    except Exception:
        pass

    hypervisors = {
        "kvm": "kvm", "qemu": "qemu", "virtualbox": "virtualbox",
        "vmware": "vmware", "xen": "xen", "hyper-v": "hyper-v", "microsoft corporation": "hyper-v",
        "google compute engine": "gce", "google": "gce", "amazon ec2": "ec2",
        "amazon": "ec2", "digitalocean": "digitalocean", "openstack": "openstack",
    }
    try:
        dmi = ""
        for f in ("sys_vendor", "product_name", "board_vendor"):
            p = Path(f"/sys/class/dmi/id/{f}")
            if p.exists():
                dmi += " " + p.read_text(encoding="utf-8", errors="ignore").strip().lower()
        for key, name in hypervisors.items():
            if key in dmi:
                info["vm"] = name
                break
        if info["vm"] is None and info["hypervisor_flag"]:
            info["vm"] = "unknown"
    except Exception:
        pass

    if os.getenv("KAGGLE_KERNEL_RUN_TYPE") or os.getenv("KAGGLE_DATA_PROXY_URL") or Path("/kaggle").exists():
        info["platform"] = "kaggle"
    elif os.getenv("COLAB_RELEASE_TAG") or os.getenv("COLAB_GPU") or "google.colab" in sys.modules:
        info["platform"] = "colab"
    elif Path("/content").exists() and (info["container"] or info["vm"]):
        info["platform"] = "colab-family"
    elif info["vm"]:
        info["platform"] = "cloud-vm"
    elif info["container"]:
        info["platform"] = "container"

    return info


def probe() -> dict:
    """Return host telemetry snapshot.

    English: CPU, memory, swap, load; GPU block when available;
    virtualization block always present.
    pt-BR: CPU, memória, swap, carga; bloco GPU quando disponível;
    bloco de virtualização sempre presente.
    """
    import psutil

    vm = psutil.virtual_memory()
    return {
        "cpu_percent": psutil.cpu_percent(interval=0.0),
        "ram_used_gb": round(vm.used / 1e9, 3),
        "ram_total_gb": round(vm.total / 1e9, 3),
        "swap_used_gb": round(psutil.swap_memory().used / 1e9, 3),
        "load_avg": os.getloadavg() if hasattr(os, "getloadavg") else None,
        "gpu": _gpu_probe(),
        "virt": _virt_probe(),
    }


def soma_context_line() -> str | None:
    """Compact one-line somatic context for LLM injection.

    English: Renders the live machine state as a short bracketed line
    (cpu/ram/load/gpu/vram/virt) suitable for a system preamble —
    brings the machine's live body to the model itself.
    pt-BR: Renderiza o estado vivo da máquina em uma linha curta
    (cpu/ram/load/gpu/vram/virt) para preâmbulo de sistema — traz o
    corpo vivo da máquina para o próprio modelo.
    """
    try:
        p = probe()
        parts = [
            f"cpu={p.get('cpu_percent')}%",
            f"ram={p.get('ram_used_gb')}/{p.get('ram_total_gb')}GB",
        ]
        la = p.get("load_avg") or []
        if la:
            parts.append(f"load={la[0]:.2f}")
        gpus = (p.get("gpu") or {}).get("gpus") or []
        if gpus:
            g = gpus[0]
            parts.append(
                f"gpu0={g.get('name')} {g.get('temp_c')}C util={g.get('util_percent')}% "
                f"vram={g.get('vram_used_gb')}/{g.get('vram_total_gb')}GB"
            )
        v = p.get("virt") or {}
        tags = [t for t in ("container" if v.get("container") else "", v.get("vm") or "") if t]
        parts.append(f"virt={'+'.join(tags) if tags else 'metal'} platform={v.get('platform')}")
        return " ".join(parts)
    except Exception:
        return None


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
