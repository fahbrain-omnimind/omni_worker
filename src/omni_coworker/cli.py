"""CLI entrypoint.

English: serve, demo, doctor, soul-export, missions.
pt-BR: serve, demo, doctor, soul-export, missions.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def serve(port: int = 8080) -> int:
    """Start server.

    English: Start uvicorn server.
    pt-BR: Inicia servidor uvicorn.
    """
    try:
        import uvicorn
        from .app import create_app
        app = create_app()
        uvicorn.run(app, host="0.0.0.0", port=port)
    except Exception as e:
        print(f"Error starting server: {e}")
        return 1
    return 0


def doctor() -> int:
    """Run diagnostics.

    English: Check dependencies, Rust kernel modules and brain server
    topology (analyst/executor health). Always exits 0 — it reports,
    never fails.
    pt-BR: Verifica dependências, módulos do kernel Rust e a topologia
    dos servidores brain (saúde analista/executor). Sempre sai 0 —
    reporta, nunca falha.
    """
    checks: list[tuple[str, str]] = []

    for mod in ("fastapi", "torch", "httpx", "psutil", "pydantic"):
        try:
            imported = __import__(mod)
            checks.append((mod, getattr(imported, "__version__", "ok")))
        except Exception as e:
            checks.append((mod, f"ERROR: {e}"))

    try:
        from .kernel_hooks.compute import kernel_status
        for name, ok in kernel_status().items():
            checks.append((f"kernel.{name}", "available" if ok else "unavailable"))
    except Exception as e:
        checks.append(("kernel", f"ERROR: {e}"))

    from .brain import server as brain_server
    for role, base in (
        ("analyst", brain_server.ERIKA_BASE_URL),
        ("executor", brain_server.EXECUTOR_BASE_URL),
    ):
        try:
            import httpx
            resp = httpx.get(f"{base}/health", timeout=3.0)
            data = resp.json()
            checks.append((
                f"brain.{role}",
                "up model={model} vram_gb={vram} ({base})".format(
                    model=data.get("model", "?"),
                    vram=data.get("vram_gb", "?"),
                    base=base,
                ),
            ))
        except Exception:
            checks.append((f"brain.{role}", f"down ({base})"))

    for name, value in checks:
        print(f"{name}: {value}")
    return 0


def demo(task: str = "hello") -> int:
    """Run a lean pipeline.

    English: DebugAgent diagnoses, CodeAgent generates, ReviewerAgent
    reviews; prints a JSON summary. Works without LLM backends
    (agents already fall back cleanly).
    pt-BR: DebugAgent diagnostica, CodeAgent gera, ReviewerAgent revisa;
    imprime resumo JSON. Funciona sem backends de LLM (os agentes já
    têm fallback limpo).
    """
    from .agents.debug_agent import DebugAgent
    from .agents.code_agent import CodeAgent
    from .agents.reviewer_agent import ReviewerAgent

    diagnosis = DebugAgent().diagnose(task)
    generated = CodeAgent().generate(task, context={"diagnosis": diagnosis.get("diagnosis")})
    review = ReviewerAgent().review(generated.get("code") or "")

    summary = {
        "task": task,
        "diagnosis": diagnosis.get("diagnosis"),
        "suggestions": diagnosis.get("suggestions"),
        "code": (generated.get("code") or "")[:2000],
        "review": {
            "approved": review.get("approved"),
            "score": review.get("score"),
            "issues": review.get("issues"),
        },
        "llm": {
            "debug": bool(diagnosis.get("llm")),
            "code": bool(generated.get("llm")),
            "review": bool(review.get("llm")),
        },
    }
    print(json.dumps(summary, indent=2, default=str))
    return 0


def soul_export(out: str | None = None) -> int:
    """Export the soul state as JSON.

    English: Computes /soul/state locally (no server needed) and prints
    it; optionally writes to --out.
    pt-BR: Computa /soul/state localmente (sem servidor) e imprime;
    opcionalmente grava em --out.
    """
    from .soul.api import _compute_state

    state = _compute_state()
    text = json.dumps(state, indent=2, default=str)
    if out:
        Path(out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


def missions() -> int:
    """List teleology missions.

    English: Same payload as GET /agency/missions, computed via internal
    functions (no HTTP).
    pt-BR: Mesmo payload de GET /agency/missions, computado via funções
    internas (sem HTTP).
    """
    from .agency.teleology import compute_omega_teleology, generate_missions
    from .soma.probe import probe

    soma = probe()
    generated = generate_missions({
        "cpu_high": (soma.get("cpu_percent") or 0) > 80,
        "soma": soma,
    })
    payload = {
        "missions": generated,
        "omega": compute_omega_teleology({"missions": generated}),
    }
    print(json.dumps(payload, indent=2, default=str))
    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI main.

    English: argparse subparsers for serve/doctor/demo/soul-export/missions.
    pt-BR: subparsers argparse para serve/doctor/demo/soul-export/missions.
    """
    parser = argparse.ArgumentParser(prog="omni-coworker")
    sub = parser.add_subparsers(dest="command")

    p_serve = sub.add_parser("serve", help="Run the FastAPI app via uvicorn")
    p_serve.add_argument("--port", type=int, default=8080)
    p_serve.set_defaults(func=lambda a: serve(a.port))

    p_doctor = sub.add_parser("doctor", help="Diagnostics: deps, kernel, brain topology")
    p_doctor.set_defaults(func=lambda a: doctor())

    p_demo = sub.add_parser("demo", help="Run a lean Debug->Code->Review pipeline")
    p_demo.add_argument("--task", default="hello")
    p_demo.set_defaults(func=lambda a: demo(a.task))

    p_soul = sub.add_parser("soul-export", help="Print /soul/state as JSON")
    p_soul.add_argument("--out", default=None)
    p_soul.set_defaults(func=lambda a: soul_export(a.out))

    p_missions = sub.add_parser("missions", help="Print teleology missions as JSON")
    p_missions.set_defaults(func=lambda a: missions())

    args = parser.parse_args(argv)
    func = getattr(args, "func", None)
    if func is None:
        parser.print_help()
        return 0
    return int(func(args) or 0)


if __name__ == "__main__":
    import sys
    sys.exit(main())
