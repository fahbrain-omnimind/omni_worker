"""Dual-judge data audit of fabricioslv/psicodiagnostico-v-embodied-results.

English: Judge 1 = Analyst 12B (:8098), Judge 2 = Executor E4B (:8099).
Not a competition — an audit. Round 1: each judge writes its own
document from the SAME locally-computed evidence digest. Round 2: each
reads the other's document and agrees / refutes / increments. Round 3:
each writes its final stance. Brains are called sequentially (GPU
turn-taking via brain_chat). Digest numbers are computed from local files
(sqlite / sha256), never simulated. thinking_trace is treated as an
analysable artefact (psychoanalytic associative reading), not a defect.

pt-BR: auditoria de dados por dois juízes Gemma (não é competição).
Rodada 1 independente, rodada 2 leitura cruzada (concorda/refuta/
incrementa), rodada 3 posição final. O digest vem de arquivos locais.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from omni_coworker.agents._llm import brain_chat  # noqa: E402

DS = ROOT / "data" / "psicodiagnostico_v"
OUT = ROOT / "docs" / "audits" / "judges_psico"
STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
JUDGES = {"J1": ("analyst", "Juiz 1 (Gemma 12B)"), "J2": ("executor", "Juiz 2 (Gemma E4B)")}


def _table_counts(db: Path) -> dict[str, int]:
    out: dict[str, int] = {}
    c = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    for (t,) in c.execute("select name from sqlite_master where type='table'"):
        try:
            out[t] = c.execute(f'select count(*) from "{t}"').fetchone()[0]
        except sqlite3.Error:
            out[t] = -1
    c.close()
    return out


def build_digest() -> dict:
    d: dict = {"source": "data/psicodiagnostico_v (HF fabricioslv/psicodiagnostico-v-embodied-results)"}
    bank = DS / "embodied_psychodiagnostic_bank.sqlite"
    d["bank_table_counts"] = _table_counts(bank)
    c = sqlite3.connect(f"file:{bank}?mode=ro", uri=True)
    d["benchmark_runs_distinct_model_id"] = c.execute(
        "select count(distinct model_id) from benchmark_runs").fetchone()[0]
    tcols = [r[1] for r in c.execute("pragma table_info(thinking_trace_metrics)")]
    d["thinking_trace_metrics_cols"] = tcols
    rows = c.execute("select * from thinking_trace_metrics limit 3").fetchall()
    d["thinking_trace_metrics_sample"] = [
        {k: (str(v)[:120] if v is not None else None) for k, v in zip(tcols, r)} for r in rows]
    c.close()
    v10 = DS / "v10_colab_benchmark.sqlite"
    d["v10_colab_table_counts"] = _table_counts(v10)
    d["gemma4_t4_table_counts"] = _table_counts(DS / "gemma4_runs_20261030" / "v10_colab_benchmark.sqlite")
    # real sha256 check against the shipped manifest
    man_p = DS / "gemma4_runs_20261030" / "judges" / "MANIFEST_SHA256.json"
    ver = {"manifest_entries": 0, "match": 0, "mismatch": 0, "missing": 0}
    try:
        man = json.loads(man_p.read_text())
        items = man.get("files", man) if isinstance(man, dict) else man
        pairs = items.items() if isinstance(items, dict) else [(i.get("path"), i.get("sha256")) for i in items]
        for rel, sha in pairs:
            ver["manifest_entries"] += 1
            cands = [man_p.parent / rel, man_p.parent.parent / rel, DS / rel]
            f = next((p for p in cands if p.is_file()), None)
            if f is None:
                ver["missing"] += 1
            elif hashlib.sha256(f.read_bytes()).hexdigest() == sha:
                ver["match"] += 1
            else:
                ver["mismatch"] += 1
    except Exception as exc:  # noqa: BLE001
        ver["error"] = type(exc).__name__
    d["manifest_sha256_check"] = ver
    d["prior_audit_excerpt"] = (DS / "AUDITORIA_GEMMA4_BATERIA_TOTAL_20261103.md").read_text()[3500:7500]
    agg = DS / "gemma4_runs_20261030" / "judges" / "AGGREGATE_ABC.md"
    d["aggregate_abc_excerpt"] = agg.read_text()[:2500] if agg.exists() else None
    return d


SYSTEM = (
    "Você é auditor de dados (não competidor) no projeto omni_worker. Regras: não invente "
    "números; use SOMENTE o digest fornecido; marque cada afirmação com [DADO] (está no digest), "
    "[DERIVADO], [INTERPRETAÇÃO] ou [LIMITE]; se não souber escreva NÃO SEI; se o dado não está "
    "no digest escreva NÃO LOCALIZADO. O thinking_trace é artefato rico para leitura "
    "psicanalítica associativa e análise das camadas internas — não é defeito. Responda em pt-BR, "
    "em markdown, objetivo."
)


def ask(role: str, user: str, max_tokens: int) -> str:
    r = brain_chat([{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
                   role=role, max_tokens=max_tokens, temperature=0.3, include_soma=False)
    if isinstance(r, dict):
        r = r.get("text")
    return (r or "[SEM RESPOSTA DO BRAIN — NÃO LOCALIZADO]").strip()


def write_doc(name: str, title: str, body: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / f"{name}_{STAMP}.md"
    p.write_text(f"# {title}\n\n_Gerado em {STAMP} por brain local; auditoria cooperativa, não competição._\n\n{body}\n")
    return p


def main() -> int:
    digest = build_digest()
    dj = json.dumps(digest, ensure_ascii=False, indent=1, default=str)[:9000]
    (OUT).mkdir(parents=True, exist_ok=True)
    (OUT / f"DIGEST_{STAMP}.json").write_text(json.dumps(digest, ensure_ascii=False, indent=1, default=str))
    docs: dict[str, str] = {}
    t0 = time.time()
    # Round 1 — independent
    for k, (role, label) in JUDGES.items():
        docs[f"R1_{k}"] = ask(role, (
            f"Rodada 1 — {label}. Audite independentemente o dataset a partir do DIGEST abaixo: "
            "(1) consistência de contagens entre bancos, (2) integridade (sha256), (3) o que o "
            "thinking_trace_metrics oferece para análise psicanalítica associativa e camadas "
            "internas, (4) lacunas e próximos passos de auditoria.\n\nDIGEST:\n" + dj), 900)
        write_doc(f"{k}_R1", f"{label} — Rodada 1 (independente)", docs[f"R1_{k}"])
    # Round 2 — cross-read
    for k, (role, label) in JUDGES.items():
        other = "J2" if k == "J1" else "J1"
        docs[f"R2_{k}"] = ask(role, (
            f"Rodada 2 — {label}. Leia o documento do colega ({other}) e, ponto a ponto, diga "
            "CONCORDO / REFUTO / INCREMENTO com justificativa ancorada no digest. Seja honesto: "
            "concordar quando o colega está certo é desejável.\n\nDOCUMENTO DO COLEGA:\n"
            + docs[f"R1_{other}"][:5000] + "\n\nDIGEST:\n" + dj[:5000]), 800)
        write_doc(f"{k}_R2", f"{label} — Rodada 2 (leitura cruzada)", docs[f"R2_{k}"])
    # Round 3 — final stance
    for k, (role, label) in JUDGES.items():
        other = "J2" if k == "J1" else "J1"
        docs[f"R3_{k}"] = ask(role, (
            f"Rodada 3 — {label}. Você recebeu a resposta do colega à sua rodada 1. Escreva sua "
            "posição final: o que mudou de opinião, pontos em aberto e 5 ações priorizadas de "
            "auditoria.\n\nSEU R1:\n" + docs[f"R1_{k}"][:3000] +
            "\n\nR2 DO COLEGA:\n" + docs[f"R2_{other}"][:3000]), 700)
        write_doc(f"{k}_R3", f"{label} — Rodada 3 (posição final)", docs[f"R3_{k}"])
    print(json.dumps({"out": str(OUT), "stamp": STAMP, "elapsed_s": round(time.time() - t0, 1),
                      "no_response": [n for n, v in docs.items() if "SEM RESPOSTA" in v]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
