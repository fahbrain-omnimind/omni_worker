"""ASGI app factory.

English: Unifies brain, agency, soul on :8080.
pt-BR: Unifica brain, agency, soul em :8080.
"""

from __future__ import annotations

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

    @app.get("/soma/probe")
    def soma_probe() -> dict:
        """Host telemetry snapshot."""
        from .soma.probe import probe_with_brain
        return probe_with_brain()

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

    return app
