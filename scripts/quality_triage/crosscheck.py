#!/usr/bin/env python3
"""crosscheck — free-CLI model loop: map + cross-validate public rules.

Delegates to hermes/kilo/cline (free models) instead of spawning internal
agents at scale (avoids model rate limits). Each CLI independently maps
the public-scope rules; then each CLI cross-checks the others' mappings;
results are merged into a report with agreement/conflict rows.

Usage:
    python crosscheck.py --rules S8707,S7688,S2083,S8706,S6096 \
        --scope public --out /tmp/crosscheck_report.json
    python crosscheck.py --list-clis

Design:
- Deterministic driver; CLIs are subprocesses (timeout, best-effort).
- Each mapper gets: rule table (public_scope.PUBLIC_FLIPS) + prompt to
  produce JSON verdicts + reasons.
- Cross phase: each CLI reviews the merged map and flags disagreements.
- Report: per-rule {consensus, disagreements, sources}.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import public_scope

CLIS = {
    "hermes": ["hermes", "-z", "{prompt}", "--yolo"],
    "kilo": ["kilo", "run", "{prompt}", "--auto"],
}
# cline removido: modelo free em rate limit diário (429) — re-add se
# provider livre voltar; crosscheck roda com 2 CLIs ou mais quando houver.

MAP_PROMPT = """Você é auditor de qualidade pública. Classifique cada regra do
mapeamento abaixo conforme risco se o código for EXPOSTO publicamente
(web service / pacote público), não no laboratório doméstico.

Regras (regra -> veredito doméstico atual):
{rules_json}

Responda SOMENTE com JSON:
{{"Sxxxx": {{"public_verdict": "future_public_risk|real_vulnerability|review_needed|accepted_domestic|false_positive|architectural_debt", "reason": "frase curta"}}, ...}}
Se discordar do mapeamento proposto, inclua "disagree": true e o porquê no reason."""

CROSS_PROMPT = """Aqui está o mapeamento consolidado de outra auditoria sobre
reclassificação pública de regras de código:

{merged_json}

Revise cada entrada. Para cada uma, diga CONCORDO ou DISCORDO (com motivo).
Responda SOMENTE com JSON:
{{"agreements": ["Sxxxx", ...], "disagreements": {{"Sxxxx": "motivo"}}}}"""


def _run_cli(cli: str, prompt: str) -> str:
    import os
    timeout = os.getenv("OMNI_CROSSCHECK_TIMEOUT_S")
    timeout = float(timeout) if timeout else None
    try:
        cmd = [c.format(prompt=prompt) if "{prompt}" in c else c for c in CLIS[cli]]
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
        return p.stdout.strip()[-4000:]
    except Exception as e:  # noqa: BLE001 — best-effort
        return f"__CLI_ERROR__ {e}"


def _extract_json(text: str) -> dict | None:
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        return json.loads(text[start:end + 1])
    except Exception:  # noqa: BLE001
        return None


def map_phase(rules: list[str]) -> dict[str, dict]:
    table = {r: public_scope.PUBLIC_FLIPS.get(r, ("no_flip", "", ""))[0]
             for r in rules}
    # table: rule -> domestic-or-public flip verdict for context
    prompt = MAP_PROMPT.format(rules_json=json.dumps(table, indent=1))
    out = {}
    for cli in CLIS:
        raw = _run_cli(cli, prompt)
        parsed = _extract_json(raw)
        out[cli] = {"raw_tail": raw[:300], "parsed": parsed or {}}
    return out


def cross_phase(merged: dict) -> dict[str, dict]:
    prompt = CROSS_PROMPT.format(merged_json=json.dumps(merged, indent=1))
    out = {}
    for cli in CLIS:
        raw = _run_cli(cli, prompt)
        out[cli] = {"parsed": _extract_json(raw) or {}, "raw_tail": raw[:300]}
    return out


def consensus(maps: dict[str, dict], rules: list[str]) -> dict[str, dict]:
    votes: dict[str, dict] = {}
    for cli, m in maps.items():
        for rule, val in (m.get("parsed") or {}).items():
            if isinstance(val, dict) and "public_verdict" in val:
                votes.setdefault(rule, {})[cli] = val["public_verdict"]
    out = {}
    for rule in rules:
        v = votes.get(rule, {})
        from collections import Counter
        cnt = Counter(v.values())
        out[rule] = {"votes": dict(v), "consensus": cnt.most_common(1)[0][0]
                     if cnt else None, "conflict": len(cnt) > 1}
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rules", required=True,
                    help="comma-separated rule ids")
    ap.add_argument("--out", default="/tmp/crosscheck_report.json", type=Path)
    ap.add_argument("--list-clis", action="store_true")
    a = ap.parse_args()
    if a.list_clis:
        print("\n".join(CLIS))
        return
    rules = [r.strip() for r in a.rules.split(",") if r.strip()]
    t0 = time.time()
    maps = map_phase(rules)
    merged = {r: {cli: (m.get("parsed") or {}).get(r) for cli, m in maps.items()}
              for r in rules}
    crossed = cross_phase(merged)
    cons = consensus(maps, rules)
    report = {"rules": rules, "map_phase": maps, "cross_phase": crossed,
              "consensus": cons, "elapsed_s": round(time.time() - t0, 1),
              "note": "crosscheck por CLIs free — veredito final é decisão do operador"}
    a.out.write_text(json.dumps(report, indent=1, ensure_ascii=False))
    print(json.dumps(cons, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()