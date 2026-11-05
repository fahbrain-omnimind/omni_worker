#!/usr/bin/env python3
"""harvest_activations — coleta assinaturas de atenção/hidden durante um run.

English: polls /erika/activations + /erika/affect on a brain while a
battery/task runs, writing per-sample MPS-lite features to JSONL.
Features: attention entropy, per-layer hidden norm/mean/std — the raw
material for early-failure detection (attention collapse) without raw
hidden states (server exposes summaries only). [PRX] — not MPS bond
dimension (that lives in the sovereign bridge, needs raw states).

pt-BR: polls /erika/activations + /erika/affect durante uma tarefa,
gravando features MPS-lite por amostra em JSONL. [PRX] — não é bond
dimension (isso vive na ponte soberana, precisa de hidden cru).

Uso: python3 scripts/experiments/harvest_activations.py \
        --port 8099 --out state/mps_harvest.jsonl --window-s 600
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.request
from pathlib import Path


def _get(url: str) -> dict | None:
    try:
        with urllib.request.urlopen(url, timeout=4) as r:
            return json.loads(r.read())
    except Exception:  # noqa: BLE001
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8099)
    ap.add_argument("--out", default="state/mps_harvest.jsonl")
    ap.add_argument("--window-s", type=int, default=600)
    args = ap.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    base = f"http://127.0.0.1:{args.port}"
    t0 = time.time()
    n = 0
    while time.time() - t0 < args.window_s:
        act = _get(f"{base}/erika/activations")
        aff = _get(f"{base}/erika/affect")
        if act or aff:
            sample = {
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "port": args.port,
                "n_activations": len(act) if act else 0,
                "attention_entropy_mean": (aff or {}).get("attention_entropy_mean"),
                "hidden_norm_mean": (aff or {}).get("hidden_norm_mean"),
                "latest": act[-1] if act else None,
            }
            with out.open("a") as fh:
                fh.write(json.dumps(sample, ensure_ascii=False) + "\n")
            n += 1
        time.sleep(3)
    print(f"harvest done: {n} samples → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())