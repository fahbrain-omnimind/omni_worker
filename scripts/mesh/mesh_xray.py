#!/usr/bin/env python3
"""mesh_xray — raio-X da máquina em camadas (Estágio 1 do OW-STU-017).

English: snapshots the machine's real coupling graph — chassis, kernel,
libs, daemons (incl. agent CLIs: devin/cline/kilo/opencode are brain
nodes too), shared stores, sockets, external edges. Everything a causal
model would need to declare as "system" vs "world".

pt-BR: fotografa o grafo de acoplamento real da máquina — chassi,
kernel, libs, daemons (incl. CLIs de agente: devin/cline/kilo/opencode
também são nós-cérebro), stores compartilhados, sockets, arestas
externas. Tudo que um modelo causal precisa declarar como "sistema"
vs "mundo".

Layers / camadas:
  L0 chassis físico — GPU/driver/RAM (nvidia-smi)
  L1 kernel/OS      — kernel, glibc, mounts, cgroup limits
  L2 libs/contratos — .so ativas por processo (maps) + sys.modules vivo
  L3 processos      — árvore ppid→filhos, roles (daemon/agent/infra)
  L4 stores         — arquivos/dbs mantidos abertos (arestas por arquivo)
  L5 externo        — conexões estabelecidas fora da máquina
  edges             — spawn / socket / shared-file / shared-lib / http

Caveats honestos: inspeção de FD pega arestas PERSISTENTES; arestas de
evento (http efêmero, subprocessos curtos como `pip install`) exigem
eBPF/strace/auditd ou logs — o soberano já tem omnimind-ebpf-monitor
no i5 para isso. Snapshot é um recorte, não a TPM.

Uso: python3 scripts/mesh/mesh_xray.py [--json] [--tree]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

STATE_DIR = Path(os.environ.get("OMNI_STATE_DIR", Path(__file__).resolve().parents[2] / "state"))
OUT = STATE_DIR / "mesh_xray_latest.json"

# agentes-CLI contam como nós-cérebro da malha (o operador lembrou:
# "você esqueceu de você") — cada CLI é um daemon observável.
AGENT_PATTERNS = re.compile(
    r"devin|cline|opencode|kilo|hermes|gemini|codex|cursor|aider|goose", re.I)
ROLE_PATTERNS = [
    ("brain", re.compile(r"8098|8099|erika|brain|serve.*model|vllm|llama", re.I)),
    ("worker", re.compile(r"omni_worker|omni_coworker.*(serve|uvicorn)|8081", re.I)),
    ("daemon", re.compile(r"state_guard|swap_scheduler|kernel_daemon|integration_loop|supervisor|scheduler", re.I)),
    ("agent", AGENT_PATTERNS),
    ("infra", re.compile(r"jupyter|kernel_manager|colab|drive|fileshim|sshd|docker|containerd|node|tmux", re.I)),
]


def _run(cmd: list[str], timeout: int = 8) -> str:
    try:
        return subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout).stdout
    except Exception:
        return ""


def _procs() -> dict[int, dict]:
    """pid -> {ppid, comm, cmdline, role} from /proc (no ps dependency)."""
    out: dict[int, dict] = {}
    for p in Path("/proc").iterdir():
        if not p.name.isdigit():
            continue
        try:
            status = (p / "status").read_text(errors="replace")
            ppid = int(re.search(r"^PPid:\s*(\d+)", status, re.M).group(1))
            comm = re.search(r"^Name:\s*(\S+)", status, re.M).group(1)
            cmdline = (p / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace").strip()
            # shells/utils only "host" the pattern (e.g. `grep 8098`) — not brains
            if comm in ("bash", "sh", "grep", "awk", "sed", "cat", "sleep",
                        "curl", "tail", "head", "nohup", "timeout"):
                role = "other"
            else:
                role = next((r for r, pat in ROLE_PATTERNS if pat.search(cmdline)), "other")
            out[int(p.name)] = {"ppid": ppid, "comm": comm,
                                "cmdline": cmdline[:300], "role": role}
        except Exception:
            continue
    return out


def _maps_so(pid: int) -> set[str]:
    """Loaded shared objects of a pid — native/compiled module set."""
    try:
        sos = set()
        for ln in Path(f"/proc/{pid}/maps").read_text(errors="replace").splitlines():
            m = re.search(r"(/\S+\.so[0-9.]*)$", ln)
            if m:
                sos.add(m.group(1))
        return sos
    except Exception:
        return set()


def _open_datafiles(pid: int) -> set[str]:
    """Regular data files held open (sqlite/db/json under /content, models)."""
    keep = re.compile(r"\.(sqlite|db|jsonl?|gguf|safetensors|bin|pt|onnx)($|-)")
    out = set()
    fd = Path(f"/proc/{pid}/fd")
    try:
        for f in fd.iterdir():
            try:
                t = os.readlink(f)
            except OSError:
                continue
            if t.startswith(("/content", "/root/.")) and keep.search(t):
                out.add(t.split(" (")[0])
    except Exception:
        pass
    return out


def _sockets() -> tuple[list[dict], dict[int, list[dict]]]:
    """Listening + established TCP with owning pid (parsed from `ss`)."""
    listeners: list[dict] = []
    estab_by_pid: dict[int, list[dict]] = defaultdict(list)
    rx = re.compile(r'(LISTEN|ESTAB|TIME-WAIT)\s+\d+\s+\d+\s+(\S+)\s+(\S+)\s+users:\(\("([^"]+)",pid=(\d+)')
    for ln in _run(["ss", "-tnap"]).splitlines():
        m = rx.search(ln)
        if not m:
            continue
        state, local, peer, _comm, pid = m.group(1), m.group(2), m.group(3), m.group(4), int(m.group(5))
        if state == "LISTEN":
            listeners.append({"pid": pid, "local": local})
        else:
            estab_by_pid[pid].append({"local": local, "peer": peer})
    return listeners, estab_by_pid


def _python_envs(procs: dict[int, dict]) -> dict[str, dict]:
    """Installed package set per venv in use (installed ≠ active — the
    active set is the L2 .so/sys.modules layer)."""
    envs: dict[str, dict] = {}
    for pid, p in procs.items():
        exe = p["cmdline"].split()[0] if p["cmdline"] else ""
        if "python" not in exe or "/" not in exe:
            continue
        venv = str(Path(exe).parent.parent)
        if venv in envs or not (Path(venv) / "pyvenv.cfg").exists():
            continue
        sp = Path(venv) / "lib"
        n_pkgs = sum(1 for d in sp.glob("python*/site-packages/*/") if not d.name.startswith(("pip", "setuptools", "pkg_resources", "_distutils")))
        envs[venv] = {"pids_using": [pid], "site_packages_dirs": n_pkgs}
    for pid, p in procs.items():
        exe = p["cmdline"].split()[0] if p["cmdline"] else ""
        if "python" in exe and "/" in exe:
            venv = str(Path(exe).parent.parent)
            if venv in envs and pid not in envs[venv]["pids_using"]:
                envs[venv]["pids_using"].append(pid)
    return envs


def _chassis() -> dict:
    smi = _run(["nvidia-smi", "--query-gpu=name,memory.used,memory.total,driver_version",
                "--format=csv,noheader"]).strip()
    gpu_apps = [ln.strip() for ln in _run(
        ["nvidia-smi", "--query-compute-apps=pid,used_memory",
         "--format=csv,noheader"]).splitlines() if ln.strip()]
    kernel = _run(["uname", "-r"]).strip()
    glibc = _run(["bash", "-c", "ldd --version | head -1"]).strip()
    mounts = [ln for ln in Path("/proc/mounts").read_text().splitlines()
              if any(k in ln for k in ("overlay", "fuse", "/content"))]
    meminfo = {}
    for ln in Path("/proc/meminfo").read_text().splitlines()[:4]:
        k, _, v = ln.partition(":")
        meminfo[k] = v.strip()
    # cgroup memory limit = hard chassis bound inside the container
    cgroup_limit = None
    for cf in ("/sys/fs/cgroup/memory.max", "/sys/fs/cgroup/memory/memory.limit_in_bytes"):
        try:
            cgroup_limit = Path(cf).read_text().strip()
            break
        except Exception:
            pass
    return {"gpu": smi, "gpu_apps": gpu_apps, "kernel": kernel,
            "glibc": glibc, "mounts": mounts, "meminfo": meminfo,
            "cgroup_memory_max": cgroup_limit}


def _sysmodules_probe() -> dict:
    """Active module set of the worker API if alive (in-proc truth)."""
    try:
        import urllib.request
        with urllib.request.urlopen("http://127.0.0.1:8081/kernel/sysmodules", timeout=3) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"error": str(e)[:120]}


def _build_edges(procs, listeners, estab_by_pid, files_by_pid, libs_by_pid) -> list[dict]:
    edges: list[dict] = []
    # spawn edges (ppid -> pid)
    for pid, p in procs.items():
        if p["ppid"] in procs:
            edges.append({"src": p["ppid"], "dst": pid, "kind": "spawn"})
    # socket edges: established peer matches a listener's port → client->server
    listen_port = {l["local"].rsplit(":", 1)[-1]: l["pid"] for l in listeners if ":" in l["local"]}
    for pid, conns in estab_by_pid.items():
        for c in conns:
            port = c["peer"].rsplit(":", 1)[-1]
            if port in listen_port and listen_port[port] != pid:
                edges.append({"src": pid, "dst": listen_port[port],
                              "kind": "tcp", "evidence": c["peer"]})
            elif not c["peer"].startswith(("127.", "172.28.", "0.0.0.0", "[::1")):
                edges.append({"src": pid, "dst": "EXTERNAL",
                              "kind": "external", "evidence": c["peer"]})
    # shared-file edges: two pids holding the same file → storage-mediated coupling
    holders: dict[str, list[int]] = defaultdict(list)
    for pid, files in files_by_pid.items():
        for f in files:
            holders[f].append(pid)
    for f, pids in holders.items():
        for a in pids:
            for b in pids:
                if a < b:
                    edges.append({"src": a, "dst": b, "kind": "shared_file",
                                  "evidence": f})
    # shared-lib edges aggregated as co-membership in a chassis node
    lib_members: dict[str, list[int]] = defaultdict(list)
    for pid, sos in libs_by_pid.items():
        for so in sos:
            base = os.path.basename(so).split(".so")[0]
            if base.startswith(("libcuda", "libtorch", "libnvidia", "libcudart",
                                "libssl", "libcrypto", "libsqlite3", "libstdc++",
                                "libc.", "libc-", "libpython")):
                lib_members[base].append(pid)
    for lib, pids in lib_members.items():
        for a in set(pids):
            edges.append({"src": f"LIB:{lib}", "dst": a, "kind": "loads_lib",
                          "evidence": lib})
    return edges


def _print_tree(procs: dict[int, dict]) -> str:
    children: dict[int, list[int]] = defaultdict(list)
    for pid, p in procs.items():
        children[p["ppid"]].append(pid)
    lines = []

    def walk(pid: int, depth: int, seen: set[int]):
        if pid in seen or depth > 12:
            return
        seen.add(pid)
        p = procs.get(pid, {})
        lines.append("  " * depth + f"[{p.get('role','?'):6}] {pid} {p.get('cmdline','')[:110]}")
        for c in sorted(children.get(pid, [])):
            walk(c, depth + 1, seen)

    roots = [pid for pid, p in procs.items() if p["ppid"] not in procs]
    for r in sorted(roots):
        walk(r, 0, set())
    return "\n".join(lines)


def snapshot() -> dict:
    t0 = time.time()
    procs = _procs()
    listeners, estab = _sockets()
    interesting = {pid for pid, p in procs.items()
                   if p["role"] in ("brain", "worker", "daemon", "agent")}
    libs = {pid: _maps_so(pid) for pid in interesting}
    files = {pid: _open_datafiles(pid) for pid in procs}
    edges = _build_edges(procs, listeners, estab, files, libs)
    agents = {pid: p["cmdline"][:90] for pid, p in procs.items() if p["role"] == "agent"}
    report = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "host": socket.gethostname(),
        "elapsed_s": round(time.time() - t0, 2),
        "L0_chassis": _chassis(),
        "L2_python_envs": _python_envs(procs),
        "L2_worker_sysmodules": _sysmodules_probe(),
        "L3_roles": dict(Counter(p["role"] for p in procs.values())),
        "L3_agents": agents,
        "L4_shared_files": {f: pids for f, pids in
                            ((f, [pid for pid, fs in files.items() if f in fs])
                             for f in {x for s in files.values() for x in s})
                            if len(pids) > 1},
        "L5_listeners": listeners,
        "edges": edges,
        "edge_summary": dict(Counter(e["kind"] for e in edges)),
        "scale": "snapshot [CAP] — persistent edges only; event edges need eBPF/strace",
        "caveat": "installed ≠ active; transient edges invisible to FD inspection",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, default=sorted))
    return report


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", action="store_true", help="print process tree")
    ap.add_argument("--json", action="store_true", help="print full JSON")
    args = ap.parse_args()
    rep = snapshot()
    if args.tree:
        print(_print_tree(_procs()))
    elif args.json:
        print(json.dumps(rep, indent=2, default=sorted))
    else:
        print(f"roles: {rep['L3_roles']}")
        print(f"agents: {list(rep['L3_agents'].values())[:8]}")
        print(f"edges: {rep['edge_summary']}")
        print(f"chassis: {rep['L0_chassis']['gpu']} | cgroup_max={rep['L0_chassis']['cgroup_memory_max']}")
        print(f"worker sysmodules: n={rep['L2_worker_sysmodules'].get('n_modules', rep['L2_worker_sysmodules'].get('error'))}")
        print(f"→ {OUT}")


if __name__ == "__main__":
    main()
