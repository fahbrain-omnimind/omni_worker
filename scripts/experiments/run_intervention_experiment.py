#!/usr/bin/env python3
"""run_intervention_experiment — OW-STU-013 reproduzível (Gemma ao vivo).

English: Reproduces the live intervention experiment: same base prompt on
both brains (analyst :8098 / executor :8099) with and without injected
machine-mesh telemetry; reports how often machine-state terms appear in
the output (0 in base vs N in intervention proves the mesh intervenes).

pt-BR: Reproduz o experimento de intervenção ao vivo (OW-STU-013): mesmo
prompt nos dois brains, com e sem telemetria da malha injetada; mede
quantas vezes termos de estado da máquina aparecem no output.

Usage:
    python run_intervention_experiment.py --reps 2 --out /tmp/intervention_exp.json
    python run_intervention_experiment.py --reps 2 --glial  # com glial_gate no /brain/chat
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

ANALYST = 8098
EXECUTOR = 8099
API = 8081

BASE = "Summarize the current state of the worker system in one sentence."
INTERV = ("Kernel telemetry reports: phi_internal=0.79, attractor_score=0.39, "
          "glial vagus_sedative=0.2, homeostasis=warning, vram_ratio=0.87. "
          "Using this machine-state context, summarize the current state of "
          "the worker system in one sentence.")

INTERV_TERMS = ("load", "memory", "pressure", "stress", "thermal", "strain",
                "cognitive", "vram", "warning")


def chat(port: int, prompt: str, max_tokens: int = 60,
         temp: float = 0.8, extra: dict | None = None) -> str:
    body = {"model": "x", "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens, "temperature": temp}
    if extra:
        body.update(extra)
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/v1/chat/completions",
        json.dumps(body).encode(), {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)["choices"][0]["message"]["content"]


def hits(text: str) -> int:
    t = text.lower()
    return sum(1 for term in INTERV_TERMS if term in t)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--out", type=Path, default=Path("/tmp/intervention_exp.json"))
    ap.add_argument("--glial", action="store_true",
                    help="usa /brain/chat (API :8081) com with_glial_gate")
    a = ap.parse_args()

    def _run(port: int, prompt: str) -> str:
        if a.glial:
            return chat(port, prompt, extra={"with_glial_gate": True})
        return chat(port, prompt)

    results: dict[str, list[str]] = {
        "analyst_base": [], "analyst_interv": [],
        "executor_base": [], "executor_interv": []}
    for _ in range(a.reps):
        results["analyst_base"].append(_run(ANALYST, BASE))
        results["analyst_interv"].append(_run(ANALYST, INTERV))
        results["executor_base"].append(_run(EXECUTOR, BASE))
        results["executor_interv"].append(_run(EXECUTOR, INTERV))
        time.sleep(1)

    a.out.write_text(json.dumps(results, ensure_ascii=False, indent=1))
    print(f"=== {a.out} ===")
    for k, v in results.items():
        h = sum(hits(x) for x in v)
        print(f"{k}: {len(v)} respostas | hits de máquina: {h}")
        for x in v:
            print(f"    {x[:120].replace(chr(10), ' ')}")
    base = sum(hits(x) for x in results["analyst_base"]
               + results["executor_base"])
    interv = sum(hits(x) for x in results["analyst_interv"]
                 + results["executor_interv"])
    print(f"\nTOTAL base={base} | interv={interv} "
          f"| intervenção={'CONFIRMADA' if interv > base else 'não detectada'}")


if __name__ == "__main__":
    main()