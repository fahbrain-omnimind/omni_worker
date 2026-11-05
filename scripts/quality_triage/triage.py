#!/usr/bin/env python3
"""triage — classify code findings against the historical priors base.

Pipeline per finding:
  1. rule match → prior verdict + confidence >= AUTO_THRESHOLD
     → auto-verdict with the dominant historical rationale;
  2. severity BLOCKER/CRITICAL in non-vendored code → always flag REVIEW
     (priors never suppress gate-level severity);
  3. otherwise → escalate to the analyst brain (role='analyst') with a
     prompt carrying prior_verdict + rationale + snippet, or fall back to
     a heuristic verdict when brains are unavailable.

Input format: one finding per JSON line —
  {"rule": "S1244", "file": "src/x.py", "line": 12, "severity": "MINOR",
   "message": "...", "category": "code_smell"}

Writes verdicts to the findings table of the priors DB (upsert by
rule+file+line) so today's decisions become tomorrow's priors.

pt-BR: triagem de achados contra a base histórica — auto-veredicto por
prior, escalada ao analista quando a confiança é baixa.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

PRIORS_DB = Path(__file__).resolve().parents[2] / "data" / "code_quality" / "priors.sqlite"
AUTO_THRESHOLD = 0.90          # confiança mínima para auto-veredicto
GATE_SEVERITIES = {"BLOCKER", "CRITICAL"}
VENDORED_MARKERS = ("vendor/", "third_party/", "node_modules/", ".venv/")

REVIEW_PROMPT = """Você é o revisor de qualidade do worker. Classifique o achado.

Histórico da regra no projeto: {history}
Regra: {rule} | Severidade: {severity} | Arquivo: {file}:{line}
Mensagem: {message}
Trecho: {snippet}

Vereditos possíveis: accepted_domestic | review_needed | architectural_debt | false_positive | real_vulnerability | future_public_risk
Responda em UMA linha JSON: {{"verdict": "...", "confidence": 0.0-1.0, "rationale": "uma frase técnica"}}"""


def load_priors(db_path: Path) -> dict:
    db = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    rows = db.execute(
        "SELECT rule, verdict, confidence, batch_suppressible, rationale,"
        " total, verdict_dist FROM rule_priors").fetchall()
    db.close()
    return {r[0]: {"verdict": r[1], "confidence": r[2],
                  "suppressible": bool(r[3]), "rationale": r[4],
                  "total": r[5], "dist": r[6]} for r in rows}


def _is_vendored(path: str) -> bool:
    return any(m in path for m in VENDORED_MARKERS)


def classify(finding: dict, priors: dict, scope: str = "domestic") -> dict:
    """Return {verdict, confidence, rationale, via} for one finding."""
    rule, sev, path = (finding.get("rule") or "",
                       (finding.get("severity") or "").upper(),
                       finding.get("file") or "")
    p = priors.get(rule)
    # scope público: reclassifica o prior doméstico com trilha explicativa
    if scope == "public":
        import public_scope
        if p:
            p = public_scope.apply_to_prior(rule, p)
            if p["flips"]:
                return {"verdict": p["public_verdict"],
                        "confidence": p["confidence"],
                        "rationale": f"{p['public_reason']} — "
                                     f"[prior doméstico: {p['domestic_verdict']}]",
                        "via": "public_scope"}
        else:
            p = {"verdict": None, "confidence": 0.0,
                 "suppressible": False, "rationale": "",
                 "total": 0, "dist": "{}"}
            p = public_scope.apply_to_prior(rule, p)
            if p["flips"]:
                return {"verdict": p["public_verdict"], "confidence": 0.0,
                        "rationale": p["public_reason"], "via": "public_scope"}
    # gate: severidade alta em código próprio nunca é auto-suprimida
    if sev in GATE_SEVERITIES and not _is_vendored(path):
        return {"verdict": "review_needed", "confidence": 1.0,
                "rationale": f"severity {sev} gate — sem auto-supressão",
                "via": "gate"}
    if p and p["confidence"] >= AUTO_THRESHOLD and p["suppressible"]:
        return {"verdict": p["verdict"], "confidence": p["confidence"],
                "rationale": p["rationale"] or f"prior {p['verdict']} n={p['total']}",
                "via": "prior"}
    return {"verdict": "escalate", "confidence": p["confidence"] if p else 0.0,
            "rationale": "", "via": "prior" if p else "unknown_rule"}


def llm_review(finding: dict, prior: dict | None) -> dict:
    """Escalate to analyst brain; heuristic fallback when unavailable."""
    hist = (f"{prior['verdict']} (n={prior['total']}, conf={prior['confidence']})"
            if prior else "regra desconhecida no histórico")
    prompt = REVIEW_PROMPT.format(
        history=hist, rule=finding.get("rule"),
        severity=finding.get("severity", "?"),
        file=f"{finding.get('file')}:{finding.get('line')}",
        message=finding.get("message", "")[:200],
        snippet=finding.get("snippet", "")[:300])
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
        from omni_coworker.agents._llm import brain_chat
        out = brain_chat([{"role": "user", "content": prompt}],
                         role="analyst", max_tokens=160, temperature=0.2)
        text = str(out or "").strip()
        start = text.find("{")
        if start >= 0:
            end = text.rfind("}") + 1
            d = json.loads(text[start:end])
            if d.get("verdict"):
                d["via"] = "llm"
                return d
    except Exception:  # noqa: BLE001, S110
        pass
    return {"verdict": "review_needed", "confidence": 0.5,
            "rationale": "llm indisponível — revisão humana", "via": "fallback"}


def record(db_path: Path, finding: dict, result: dict) -> None:
    db = sqlite3.connect(db_path)
    db.execute("""CREATE TABLE IF NOT EXISTS findings (
        rule TEXT, file TEXT, line INTEGER, severity TEXT,
        verdict TEXT, confidence REAL, via TEXT, rationale TEXT,
        ts TEXT DEFAULT (datetime('now')),
        PRIMARY KEY (rule, file, line))""")
    db.execute("""INSERT OR REPLACE INTO findings
        (rule,file,line,severity,verdict,confidence,via,rationale)
        VALUES (?,?,?,?,?,?,?,?)""",
               (finding.get("rule"), finding.get("file"),
                finding.get("line"), finding.get("severity"),
                result["verdict"], result.get("confidence"),
                result["via"], result.get("rationale", "")))
    db.commit()
    db.close()


def run(findings_path: Path, db_path: Path, use_llm: bool = True,
        scope: str = "domestic") -> dict:
    priors = load_priors(db_path)
    stats = {"auto": 0, "llm": 0, "fallback": 0, "gate": 0, "total": 0,
             "public_scope": 0}
    with findings_path.open() as fh:
        for line in fh:
            if not line.strip():
                continue
            f = json.loads(line)
            r = classify(f, priors, scope)
            if r["verdict"] == "escalate":
                r = llm_review(f, priors.get(f.get("rule"))) if use_llm else {
                    "verdict": "review_needed", "confidence": 0.0,
                    "via": "fallback", "rationale": "llm desligado"}
            stats[r["via"]] = stats.get(r["via"], 0) + 1
            stats["total"] += 1
            record(db_path, f, r)
    return stats


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--findings", required=True, type=Path,
                    help="jsonl com um achado por linha")
    ap.add_argument("--db", default=PRIORS_DB, type=Path)
    ap.add_argument("--no-llm", action="store_true")
    ap.add_argument("--scope", default="domestic",
                    choices=("domestic", "public"),
                    help="public reclassifica priors domésticos com trilha")
    a = ap.parse_args()
    print(json.dumps(run(a.findings, a.db, not a.no_llm, a.scope), indent=1))


if __name__ == "__main__":
    main()
