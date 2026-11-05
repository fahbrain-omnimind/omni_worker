#!/usr/bin/env python3
"""rehydrate_memtrias.py — Popula/reidrata data/memtrias.sqlite com memórias reais.

English:
    Rehydrates the topological memory store (`data/memtrias.sqlite`) from
    real persisted artifacts when a VM restarts or when the store is empty:
      - `machine`: project docs (`docs/**/*.md` — studies, audits, design, ops)
      - `document`: PhilPapers 2026 corpus (`revisao/bibliografia_philpapers_20261005/txt`)
                    and canonical psychoanalysis/science entries from `acervo_manifest.sqlite`
      - `instance`: real Gemma 4 (`analyst` 12B / `executor` E4B) outputs & diagnostics
                    from the battery SQLite ledgers (`diag_battery`, `coding_battery`,
                    `supervisor_battery`, `refactor_battery`, and `data/hf_gemma4/`)
      - `state`: real somatic probes (`somatic_probes.sqlite`) and loop cycles
      - `interaction` / `user`: real mission and workspace events (`shared_workspace.sqlite`)
      - `dream`: runs live `dream.metabolize()` with the Analyst brain (:8098) if online.

pt-BR:
    Reidrata o banco de memória topológica (`data/memtrias.sqlite`) a partir de
    artefatos reais persistidos após recriação de VM ou quando o banco está vazio.
    NENHUM dado é simulado — toda entrada referencia seu arquivo/banco de origem (`doc_ref`).
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from omni_coworker.memory.memtrias_ai import MemtriasAI


def rehydrate(state_dir: Path | None = None, run_dream: bool = True) -> dict[str, int]:
    state_dir = state_dir or Path(os.getenv("OMNI_STATE_DIR", str(REPO / "data")))
    acervo_dir = Path(os.getenv("OMNI_ACERVO_DIR", "/content/acervo_vetorizado"))
    os.environ.setdefault("OMNI_EMBED_DEVICE", "cpu")
    mem = MemtriasAI(
        state_dir=state_dir,
        acervo_dir=acervo_dir if acervo_dir.exists() else None,
    )

    # Check existing doc_refs to keep rehydration idempotent
    con = sqlite3.connect(state_dir / "memtrias.sqlite")
    existing_refs = {
        r[0]
        for r in con.execute("SELECT doc_ref FROM memories WHERE doc_ref IS NOT NULL")
    }
    con.close()

    counts: dict[str, int] = {
        "machine": 0,
        "document": 0,
        "instance": 0,
        "state": 0,
        "interaction": 0,
        "user": 0,
        "dream": 0,
    }

    # 1. Namespace `machine`: docs/**/*.md
    docs_dir = REPO / "docs"
    if docs_dir.exists():
        for md in sorted(docs_dir.rglob("*.md")):
            ref = f"docs/{md.relative_to(docs_dir)}"
            if ref in existing_refs:
                continue
            try:
                txt = md.read_text(encoding="utf-8", errors="replace").strip()
            except Exception:  # noqa: BLE001, S112
                continue
            if not txt:
                continue
            lines = [
                ln.strip()
                for ln in txt.splitlines()
                if ln.strip() and not ln.strip().startswith("<!--")
            ]
            title = lines[0].lstrip("# ").strip() if lines else md.stem
            excerpt = " ".join(lines[1:8])[:600]
            content = f"[{ref}] {title} — {excerpt}"
            mem.remember(
                "machine",
                content,
                tags=["doc", md.parent.name, md.stem],
                instance="omni_worker",
                doc_ref=ref,
            )
            existing_refs.add(ref)
            counts["machine"] += 1

    # 1b. Namespace `machine`: Symbolic body (codebase hypergraph + repo snapshot, sanitized)
    try:
        import subprocess

        from omni_coworker.store.code_index import (
            build_symbolic_hypergraph,
            sanitize_secret_text,
        )

        hg = build_symbolic_hypergraph(
            REPO / "src/omni_coworker", state_dir / "symbolic_hypergraph.json"
        )
        for he in hg.get("hyperedges", []):
            mod_rel = he.get("module", "")
            ref = f"symbolic_body:module:{mod_rel}"
            if ref in existing_refs:
                continue
            clean_txt, _ = sanitize_secret_text(
                f"[SymbolicHyperedge {mod_rel}] subpackage={he.get('subpackage')} "
                f"concepts={he.get('concepts')} tables={he.get('tables')} "
                f"routes={he.get('routes')} members={he.get('members')[:8]} — {he.get('summary')}"
            )
            mem.remember(
                "machine",
                clean_txt,
                tags=["symbolic_body", "hypergraph", str(he.get("subpackage", "core"))],
                instance="omni_worker",
                doc_ref=ref,
            )
            existing_refs.add(ref)
            counts["machine"] += 1

        head_sha = (
            subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=str(REPO),
                capture_output=True,
                text=True,
                check=False,
            ).stdout.strip()
            or "unknown"
        )
        snap_ref = f"repo_snapshot:{head_sha}"
        if snap_ref not in existing_refs:
            snap_txt, _ = sanitize_secret_text(
                f"[Repo Snapshot {head_sha}] symbolic_hypergraph nodes={hg.get('node_count')} "
                f"hyperedges={hg.get('hyperedge_count')} concepts={hg.get('concepts')} "
                f"tables={hg.get('tables')} routes={hg.get('routes')}"
            )
            mem.remember(
                "machine",
                snap_txt,
                tags=["repo_snapshot", "symbolic_body", head_sha],
                instance="omni_worker",
                doc_ref=snap_ref,
            )
            existing_refs.add(snap_ref)
            counts["machine"] += 1
    except Exception as e:  # noqa: BLE001
        print(f"[rehydrate] warn symbolic_hypergraph: {e}", file=sys.stderr)

    # 2. Namespace `document`: Local PhilPapers 2026 + A6 prior model reviews + Acervo Vetorizado
    phil_dir = REPO / "data/corpus/philpapers_2026/txt"
    if not phil_dir.exists():
        phil_dir = Path(
            "/content/omnimind-kilombo-sovereign/revisao/bibliografia_philpapers_20261005/txt"
        )
    if phil_dir.exists():
        for tf in sorted(phil_dir.glob("*.txt")):
            ref = f"philpapers_2026/{tf.name}"
            if ref in existing_refs:
                continue
            try:
                head = tf.read_text(encoding="utf-8", errors="replace")[:700]
            except Exception:  # noqa: BLE001, S112
                continue
            snippet = " ".join(head.split())[:500]
            mem.remember(
                "document",
                f"[PhilPapers 2026: {tf.name}] {snippet}",
                tags=["philpapers", "corpus_local", "obra"],
                doc_ref=ref,
            )
            existing_refs.add(ref)
            counts["document"] += 1

    rev_dir = REPO / "data/corpus/a6_book/revisoes_anteriores"
    if rev_dir.exists():
        for rmd in sorted(rev_dir.rglob("*.md")):
            ref = f"a6_revisoes/{rmd.relative_to(rev_dir)}"
            if ref in existing_refs:
                continue
            try:
                head = rmd.read_text(encoding="utf-8", errors="replace")[:700]
            except Exception:  # noqa: BLE001, S112
                continue
            snippet = " ".join(head.split())[:500]
            mem.remember(
                "document",
                f"[A6 Revisão Anterior: {rmd.name}] {snippet}",
                tags=["a6_book", "revisao_anterior", rmd.stem],
                doc_ref=ref,
            )
            existing_refs.add(ref)
            counts["document"] += 1

    acervo_db = acervo_dir / "acervo_manifest.sqlite"
    if acervo_db.exists():
        try:
            acon = sqlite3.connect(f"file:{acervo_db}?mode=ro", uri=True)
            # Sample representative canonical works across areas with their first real snippet
            rows = acon.execute("""
                SELECT r.doc_id, r.nome_arquivo, r.area_cnpq, r.pagina, r.texto_snippet
                FROM rows r
                INNER JOIN (
                    SELECT doc_id, MIN(rid) AS min_rid
                    FROM rows
                    WHERE length(texto_snippet) > 120
                    GROUP BY doc_id
                    LIMIT 60
                ) m ON r.rid = m.min_rid
                """).fetchall()
            acon.close()
            for doc_id, nome_arq, area, pag, snip in rows:
                ref = f"acervo:doc:{doc_id}:p{pag}"
                if ref in existing_refs:
                    continue
                clean_snip = " ".join(str(snip).split())[:450]
                mem.remember(
                    "document",
                    f"[Acervo {nome_arq} p.{pag} ({area})] {clean_snip}",
                    tags=["acervo_vetorizado", str(area or "geral").lower()],
                    doc_ref=ref,
                )
                existing_refs.add(ref)
                counts["document"] += 1
        except Exception as e:  # noqa: BLE001
            print(f"[rehydrate] warn acervo sample: {e}", file=sys.stderr)

    # 3. Namespace `instance`: Gemma 4 Analyst (12B) & Executor (E4B) battery ledgers + HF competition DBs
    diag_db = REPO / "scripts/gemma4_diag_battery/diag_battery.sqlite"
    if diag_db.exists():
        con = sqlite3.connect(f"file:{diag_db}?mode=ro", uri=True)
        for (
            ts,
            role,
            task_id,
            score,
            detail_json,
            degen,
            lat,
            n_tok,
            rep,
        ) in con.execute(
            "SELECT ts, model_role, task_id, score, detail_json, degenerate, latency_s, n_tokens, rep "
            "FROM diag_battery ORDER BY ts DESC LIMIT 30"
        ):
            ref = f"diag_battery:{role}:{task_id}:rep{rep}:{ts}"
            if ref in existing_refs:
                continue
            content = (
                f"[Gemma-4 {role} diag_battery] task={task_id} rep={rep} score={score:.3f} "
                f"degenerate={degen} latency={lat:.2f}s tokens={n_tok} detail={str(detail_json)[:260]}"
            )
            mem.remember(
                "instance",
                content,
                tags=["gemma4", "diag_battery", str(role), str(task_id)],
                instance=str(role),
                doc_ref=ref,
            )
            existing_refs.add(ref)
            counts["instance"] += 1
        con.close()

    coding_db = REPO / "scripts/coding_battery/coding_battery.sqlite"
    if coding_db.exists():
        con = sqlite3.connect(f"file:{coding_db}?mode=ro", uri=True)
        for (
            ts,
            case_id,
            cls,
            analyst_json,
            recall,
            hall,
            fix_comp,
            verdict,
        ) in con.execute(
            "SELECT ts, case_id, cls, analyst_json, recall, hallucinated, fix_compiles, verdict "
            "FROM coding_battery ORDER BY ts DESC LIMIT 20"
        ):
            ref = f"coding_battery:{case_id}:{ts}"
            if ref in existing_refs:
                continue
            content = (
                f"[Gemma-4 coding_battery] case={case_id} cls={cls} recall={recall} "
                f"hallucinated={hall} fix_compiles={fix_comp} verdict={verdict} "
                f"analyst={str(analyst_json)[:280]}"
            )
            mem.remember(
                "instance",
                content,
                tags=["gemma4", "coding_battery", str(case_id), str(verdict)],
                instance="analyst+executor",
                doc_ref=ref,
            )
            existing_refs.add(ref)
            counts["instance"] += 1
        con.close()

    sup_db = REPO / "scripts/supervisor_battery/supervisor_battery.sqlite"
    if sup_db.exists():
        con = sqlite3.connect(f"file:{sup_db}?mode=ro", uri=True)
        for row in con.execute(
            "SELECT ts, category, turn_idx, dominant_token, tracer_level, posture "
            "FROM supervisor_battery ORDER BY ts DESC LIMIT 16"
        ):
            ts, cat, turn_idx, dom, level, posture = row
            ref = f"supervisor_battery:{cat}:{turn_idx}:{ts}"
            if ref in existing_refs:
                continue
            content = (
                f"[Gemma-4 AffectTracer supervisor_battery] category={cat} turn={turn_idx} "
                f"tracer_level={level} posture={posture} dominant_token={dom}"
            )
            mem.remember(
                "instance",
                content,
                tags=["gemma4", "supervisor_battery", str(cat), str(level)],
                instance="analyst",
                doc_ref=ref,
            )
            existing_refs.add(ref)
            counts["instance"] += 1
        con.close()

    hf_e4b = state_dir / "hf_gemma4/gemma4_e4b_l4_results.sqlite"
    if hf_e4b.exists():
        try:
            con = sqlite3.connect(f"file:{hf_e4b}?mode=ro", uri=True)
            cols = [r[1] for r in con.execute("PRAGMA table_info(generation_records)")]
            for row in con.execute("SELECT * FROM generation_records LIMIT 20"):
                rec = dict(zip(cols, row))
                rid = rec.get("id") or rec.get("record_id") or rec.get("prompt_id")
                ref = f"hf_e4b_l4:gen:{rid}"
                if ref in existing_refs:
                    continue
                prompt_id = rec.get("prompt_id") or rec.get("block") or "gen"
                out_txt = str(rec.get("output_text") or rec.get("response") or "")[:300]
                out_clean = " ".join(out_txt.split())
                mem.remember(
                    "instance",
                    f"[HF gemma4-e4b-colab-l4-results {prompt_id}] {out_clean}",
                    tags=["gemma4", "hf_competition", "e4b_l4"],
                    instance="executor",
                    doc_ref=ref,
                )
                existing_refs.add(ref)
                counts["instance"] += 1
            con.close()
        except Exception as e:  # noqa: BLE001
            print(f"[rehydrate] warn hf_e4b: {e}", file=sys.stderr)

    # 4. Namespace `state`: somatic_probes.sqlite & integration_loop.sqlite
    soma_db = state_dir / "somatic_probes.sqlite"
    if soma_db.exists():
        con = sqlite3.connect(f"file:{soma_db}?mode=ro", uri=True)
        cols = [r[1] for r in con.execute("PRAGMA table_info(probes)")]
        for row in con.execute("SELECT * FROM probes ORDER BY rowid DESC LIMIT 5"):
            rec = dict(zip(cols, row))
            ref = f"somatic_probe:{rec.get('id') or rec.get('ts')}"
            if ref in existing_refs:
                continue
            mem.remember(
                "state",
                f"[Somatic Probe] {json.dumps(rec, ensure_ascii=False)[:400]}",
                tags=["soma", "probe", "telemetry"],
                instance="worker_body",
                doc_ref=ref,
                state_ref=rec,
            )
            existing_refs.add(ref)
            counts["state"] += 1
        con.close()

    loop_db = state_dir / "integration_loop.sqlite"
    if loop_db.exists():
        con = sqlite3.connect(f"file:{loop_db}?mode=ro", uri=True)
        cols = [r[1] for r in con.execute("PRAGMA table_info(cycles)")]
        for row in con.execute("SELECT * FROM cycles ORDER BY rowid DESC LIMIT 5"):
            rec = dict(zip(cols, row))
            cid = rec.get("cycle_id") or rec.get("id")
            ref = f"integration_cycle:{cid}"
            if ref in existing_refs:
                continue
            mem.remember(
                "state",
                f"[Integration Loop Cycle {cid}] status={rec.get('status')} ts={rec.get('ts')}",
                tags=["integration_loop", "cycle"],
                instance="kernel_loop",
                doc_ref=ref,
            )
            existing_refs.add(ref)
            counts["state"] += 1
        con.close()

    # 5. Namespace `interaction` and `user`: shared_workspace.sqlite & operational context
    sw_db = state_dir / "shared_workspace.sqlite"
    if sw_db.exists():
        con = sqlite3.connect(f"file:{sw_db}?mode=ro", uri=True)
        cols = [r[1] for r in con.execute("PRAGMA table_info(events)")]
        for row in con.execute(
            "SELECT rowid, * FROM events WHERE topic NOT LIKE 'kernel.%' ORDER BY rowid DESC LIMIT 10"
        ):
            eid = row[0]
            rec = dict(zip(cols, row[1:]))
            topic = rec.get("topic") or "event"
            sender = rec.get("sender") or rec.get("source") or "worker"
            payload_json = rec.get("payload_json") or rec.get("payload") or str(rec)
            ref = f"workspace_event:{eid}"
            if ref in existing_refs:
                continue
            mem.remember(
                "interaction",
                f"[Workspace {topic} from {sender}] {str(payload_json)[:350]}",
                tags=["shared_workspace", str(topic), str(sender)],
                instance=str(sender),
                doc_ref=ref,
            )
            existing_refs.add(ref)
            counts["interaction"] += 1
        con.close()

    user_ref = "operator:operational_directives:2026-11-03"
    if user_ref not in existing_refs:
        mem.remember(
            "user",
            "Operador (Fabrício Silva): priorizar apuração técnica estrita sem simulação (REGRA ZERO), "
            "manter start_omni_worker.sh autossuficiente (restaurar backup, instalar dependências, "
            "montar acervo vetorizado e datasets HF da competição, descompactar repositórios de referência "
            "omnimind-kilombo-sovereign e omni_node) e validar baterias reais com os brains Gemma 4 (:8098/:8099).",
            tags=["operator", "regra_zero", "arquitetura"],
            instance="artifice-operator",
            doc_ref=user_ref,
        )
        counts["user"] += 1

    # 6. Namespace `dream`: run live metabolize if requested
    if run_dream:
        try:
            from omni_coworker.agency.dream import metabolize

            res = metabolize()
            if res.get("metabolized", 0) > 0:
                counts["dream"] += 1
        except Exception as e:  # noqa: BLE001
            print(f"[rehydrate] warn dream.metabolize: {e}", file=sys.stderr)

    # Final count per namespace
    con = sqlite3.connect(state_dir / "memtrias.sqlite")
    totals = dict(
        con.execute(
            "SELECT namespace, count(*) FROM memories GROUP BY namespace"
        ).fetchall()
    )
    con.close()
    print(
        json.dumps(
            {"inserted": counts, "totals_by_namespace": totals},
            indent=2,
            ensure_ascii=False,
        )
    )
    return totals


if __name__ == "__main__":
    rehydrate(run_dream="--no-dream" not in sys.argv)
