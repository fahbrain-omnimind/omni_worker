"""ASGI app factory.

English: Unifies brain, agency, soul on :8080.
pt-BR: Unifica brain, agency, soul em :8080.
"""

from __future__ import annotations

from typing import Optional

from fastapi import FastAPI

from .soul.api import router as soul_router
from .brain.server import create_brain_router


def create_app() -> FastAPI:
    """Create the ASGI app.
    
    English: Mounts sub-routers.
    pt-BR: Monta sub-routers.
    """
    app = FastAPI(
        title="omni-agent-coworker",
        description="Sovereign agentic coworker - Machine Public Soul",
        version="0.1.0"
    )
    app.include_router(soul_router)
    try:
        app.include_router(create_brain_router())
    except Exception:
        pass
    try:
        from .safety.supervisor import create_supervisor_router
        app.include_router(create_supervisor_router())
    except Exception:
        pass
    try:
        from .shared_workspace.api import router as mesh_router
        app.include_router(mesh_router)
    except Exception:
        pass
    try:
        from .kernel_daemon.api import router as kernel_router
        app.include_router(kernel_router)

        from .kernel_daemon.scheduler import KernelDaemon
        _daemon = KernelDaemon()

        @app.on_event("startup")
        async def _kernel_daemon_start() -> None:
            _daemon.start()

        @app.on_event("shutdown")
        async def _kernel_daemon_stop() -> None:
            await _daemon.stop()
    except Exception:
        pass
    try:
        from .integration_loop.api import router as loop_router
        app.include_router(loop_router)

        from .integration_loop.loop import IntegrationLoop
        _loop = IntegrationLoop()

        @app.on_event("startup")
        async def _integration_loop_start() -> None:
            _loop.start()

        @app.on_event("shutdown")
        async def _integration_loop_stop() -> None:
            await _loop.stop()
    except Exception:
        pass

    @app.get("/soma/probe")
    def soma_probe() -> dict:
        """Host telemetry snapshot (persisted to somatic store)."""
        from .soma.probe import probe_recorded
        return probe_recorded()

    @app.get("/agency/missions")
    def agency_missions() -> dict:
        """Teleology missions generated from current host pressure."""
        from .agency.teleology import compute_omega_teleology, generate_missions
        from .soma.probe import probe
        soma = probe()
        missions = generate_missions({"cpu_high": (soma.get("cpu_percent") or 0) > 80, "soma": soma})
        return {"missions": missions, "omega": compute_omega_teleology({"missions": missions})}

    @app.get("/safety/check")
    def safety_check(action: str = "read_file") -> dict:
        """Evaluate an action through permission matrix + constitutional gate."""
        from .safety.gate import evaluate_action
        from .safety.matrix import check_permission
        return {
            "action": action,
            "matrix": check_permission(action),
            "gate": evaluate_action(action),
        }

    @app.get("/safety/refusal_state")
    def safety_refusal_state() -> dict:
        """Current refusal episode state + transitions (A5)."""
        from .safety.refusal_state import current_state
        return current_state()

    @app.get("/safety/care")
    def safety_care(reason: str, state_uf: Optional[str] = None, age: Optional[int] = None) -> dict:
        """Escalate a mental-health / abuse concern through the territorial care path.
        
        English: Escalate a mental-health / abuse concern through the territorial care path.
        pt-BR: Escalar uma preocupação de saúde mental / abuso pelo caminho de cuidado territorial.
        """
        from .safety.care import escalate
        result = escalate(reason, state_uf=state_uf, age=age)
        return result

    @app.post("/dream/cycle")
    def dream_cycle() -> dict:
        """Run a dream cycle over the vectorized code corpus."""
        from .agency.dream import dream_cycle as _cycle
        return _cycle()

    @app.get("/curiosity/explore")
    def curiosity_explore(topic: str, k: int = 6) -> dict:
        """Explore a topic against the code index (curiosity mode)."""
        from .agency.curiosity import explore
        return explore(topic, k=k)

    @app.get("/kernel/status")
    def kernel_status() -> dict:
        """Rust kernel modules availability."""
        from .kernel_hooks.compute import kernel_status as _status
        return _status()

    @app.get("/kernel/sysmodules")
    def kernel_sysmodules() -> dict:
        """Active Python module set inside this live process (sys.modules).

        English: which modules are actually loaded — the activation set,
        not pip freeze (installed ≠ active). Mesh x-ray L2 layer.
        pt-BR: módulos realmente carregados — conjunto de ativação, não
        pip freeze (instalado ≠ ativo). Camada L2 do raio-X da malha.
        """
        import collections
        import sys
        pkgs: dict[str, int] = collections.Counter()
        natives: list[str] = []
        for name, mod in sys.modules.items():
            pkgs[name.split(".")[0]] += 1
            f = getattr(mod, "__file__", None) or ""
            spec = getattr(mod, "__spec__", None)
            builtin = spec is not None and spec.origin == "built-in"
            if f.endswith((".so", ".pyd")) or builtin:
                natives.append(name)
        top = pkgs.most_common(40)
        return {
            "pid": __import__("os").getpid(),
            "n_modules": len(sys.modules),
            "top_packages": dict(top),
            "native_modules": sorted(natives),
            "scale": "sys.modules count [CAP]",
        }

    @app.get("/agency/dunker")
    def agency_dunker() -> dict:
        """Dunker/Soler 5-level psychoaffective architecture (canonical adapter)."""
        from .agency.dunker import dunker_architecture
        from .kernel_hooks.compute import affect_state
        from .soma.probe import probe
        kernel_state = None
        try:
            kernel_state = affect_state({"soma": probe()})
        except Exception:
            pass
        return dunker_architecture(kernel_state=kernel_state)

    @app.get("/agency/witness")
    def agency_witness() -> dict:
        """Witness hash-chain: last entries + integrity verification."""
        from .agency.witness import read_witness, verify_witness

        chain = read_witness(limit=20)
        return {"entries": chain, "verify": verify_witness()}

    return app
