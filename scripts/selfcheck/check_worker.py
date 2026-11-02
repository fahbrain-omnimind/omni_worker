#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_worker — structural self-check for the omni_worker repo.

English: read-only repo-health verification, safe to run anywhere.
Checks: (1) every checkable .py file compiles — anything under */victim/
or */out/ is skipped (seeded victims are intentionally buggy, out/ holds
model-generated fixes); tracked files come from `git ls-files` with an
rglob fallback outside git worktrees; (2) sqlite ledgers under
scripts/*/ open read-only and report per-table row counts. Optional
flags: --live pings the brain servers (:8098 analyst / :8099 executor)
and reports model id + vram_gb; --ledger-summary prints per-table row
counts, distinct task-id counts and score-column means. Prints one
compact PASS/FAIL line per structural check; exit code 0 when all pass,
1 otherwise. Live-server failures are warnings, never structural.
pt-BR: verificação read-only da saúde do repo, segura em qualquer
ambiente. Checa: (1) todo .py verificável compila — qualquer coisa sob
*/victim/ ou */out/ é ignorada (vítimas semeadas são quebradas de
propósito, out/ guarda correções geradas por modelo); arquivos rastreados
vêm de `git ls-files` com fallback rglob fora de worktrees git; (2)
ledgers sqlite sob scripts/*/ abrem read-only e reportam contagens por
tabela. Flags: --live pinga os servidores brain (:8098 analista /
:8099 executor) e reporta model id + vram_gb; --ledger-summary imprime
contagens, task-ids distintos e médias de colunas de score. Uma linha
compacta PASS/FAIL por checagem; exit 0 se tudo passa, 1 caso contrário.
Falhas nos servidores vivos são avisos, nunca estruturais.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

BRAIN_URLS = {
    "analyst": "http://127.0.0.1:8098",
    "executor": "http://127.0.0.1:8099",
}

# .py under these path parts is never structurally checked: seeded
# victims are intentionally broken, out/ holds generated fixes.
SKIP_DIRS = {"victim", "out", "__pycache__", ".git", ".venv", "node_modules"}

# column-name hints for --ledger-summary
SCORE_HINT = "score"
EXTRA_MEAN_COLS = {"recall"}
TASK_COLS = ("task_id", "case_id", "category", "model_role")


def _git_tracked_py(root: Path) -> list[Path] | None:
    """git ls-files '*.py' under root; None when git/repo is unavailable."""
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z", "--", "*.py"],
            capture_output=True,
            timeout=30,
        )
    except Exception:
        return None
    if out.returncode != 0:
        return None
    return [
        root / rel for rel in out.stdout.decode("utf-8", "replace").split("\0") if rel
    ]


def iter_checkable_py(root: Path) -> list[Path]:
    """All checkable .py files: git-tracked when possible, else rglob —
    minus anything under a SKIP_DIRS path part."""
    files = _git_tracked_py(root)
    if files is None:
        files = sorted(p for p in root.rglob("*.py") if p.is_file())
    checkable = []
    for p in files:
        try:
            parts = p.resolve().relative_to(root.resolve()).parts
        except (ValueError, OSError):
            continue
        if set(parts[:-1]) & SKIP_DIRS:
            continue
        checkable.append(p)
    return checkable


def compile_failures(
    root: Path, files: list[Path] | None = None
) -> list[tuple[str, str]]:
    """(relpath, error) for each checkable .py that fails compile()."""
    failures = []
    for p in files if files is not None else iter_checkable_py(root):
        try:
            rel = str(p.resolve().relative_to(root.resolve()))
        except (ValueError, OSError):
            rel = str(p)
        try:
            src = p.read_text(encoding="utf-8", errors="replace")
            compile(src, str(p), "exec")
        except SyntaxError as e:
            failures.append((rel, f"{e.msg} (line {e.lineno})"))
        except OSError as e:
            failures.append((rel, f"unreadable: {e}"))
    return failures


def _connect_ro(path: Path) -> sqlite3.Connection:
    """Open a sqlite file read-only (URI mode=ro); never writes/journals."""
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)


def scan_ledgers(scripts_dir: Path) -> list[dict]:
    """Read-only scan of scripts/*/*.sqlite ledgers + table row counts."""
    reports = []
    for db in sorted(scripts_dir.glob("*/*.sqlite")):
        rep = {"path": db, "ok": False, "tables": {}, "error": None}
        try:
            con = _connect_ro(db)
            names = [
                r[0]
                for r in con.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            ]
            for t in names:
                rep["tables"][t] = con.execute(
                    f'SELECT COUNT(*) FROM "{t}"'
                ).fetchone()[0]
            con.close()
            rep["ok"] = True
        except Exception as e:
            rep["error"] = str(e)
        reports.append(rep)
    return reports


def ledger_summary(path: Path) -> dict:
    """Per-table {rows, tasks?, means{score-ish col: avg}} for one ledger."""
    summary = {}
    con = _connect_ro(path)
    tables = [
        r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")
    ]
    for t in tables:
        cols = [c[1] for c in con.execute(f'PRAGMA table_info("{t}")')]
        entry = {"rows": con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]}
        for tc in TASK_COLS:
            if tc in cols:
                entry["tasks"] = con.execute(
                    f'SELECT COUNT(DISTINCT "{tc}") FROM "{t}"'
                ).fetchone()[0]
                break
        means = {}
        for c in cols:
            if SCORE_HINT in c or c in EXTRA_MEAN_COLS:
                mean = con.execute(
                    f'SELECT AVG("{c}") FROM "{t}" '
                    f'WHERE typeof("{c}") IN ("integer", "real")'
                ).fetchone()[0]
                if mean is not None:
                    means[c] = round(mean, 3)
        if means:
            entry["means"] = means
        summary[t] = entry
    con.close()
    return summary


def ping_health(base_url: str, timeout: float = 5.0) -> dict | None:
    """GET <base>/health → parsed dict, or None when unreachable."""
    try:
        with urllib.request.urlopen(
            base_url.rstrip("/") + "/health", timeout=timeout
        ) as resp:
            data = json.loads(resp.read().decode("utf-8", "replace"))
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _line(status: str, msg: str) -> None:
    print(f"[{status}] {msg}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="check_worker",
        description="Read-only structural self-check for omni_worker.",
    )
    ap.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="repo root (default: the repo containing this file)",
    )
    ap.add_argument(
        "--live",
        action="store_true",
        help="also ping brain /health on :8098 (analyst) and :8099 (executor)",
    )
    ap.add_argument(
        "--ledger-summary",
        action="store_true",
        help="print per-ledger task counts and score-column means",
    )
    args = ap.parse_args(argv)
    root = args.root.resolve()
    failures = 0

    # check 1 — every checkable .py compiles
    files = iter_checkable_py(root)
    bad = compile_failures(root, files)
    if bad:
        failures += 1
        _line("FAIL", f"compile: {len(bad)}/{len(files)} files broken")
        for rel, err in bad[:10]:
            print(f"       {rel}: {err}")
    else:
        _line(
            "PASS",
            f"compile: {len(files)} files compile " "(victim/out fixtures excluded)",
        )

    # check 2 — ledgers under scripts/*/ readable
    reports = scan_ledgers(root / "scripts")
    bad_ledgers = [r for r in reports if not r["ok"]]
    if bad_ledgers:
        failures += 1
        _line(
            "FAIL",
            f"ledgers: {len(bad_ledgers)}/{len(reports)} unreadable",
        )
        for r in bad_ledgers:
            print(f"       {r['path']}: {r['error']}")
    elif reports:
        _line("PASS", f"ledgers: {len(reports)} readable")
    else:
        _line("PASS", "ledgers: none found under scripts/*/ (runtime artifacts)")
    for r in reports:
        if r["ok"]:
            tables = ", ".join(f"{t}={n}" for t, n in r["tables"].items())
            rel = r["path"].relative_to(root)
            print(f"       {rel}: {tables}")

    # optional --live: brain /health (warnings only, never structural)
    if args.live:
        for role, base in BRAIN_URLS.items():
            health = ping_health(base)
            if health is None:
                _line("WARN", f"live: {role} {base} unreachable")
            else:
                _line(
                    "INFO",
                    f"live: {role} {base} model={health.get('model')} "
                    f"vram_gb={health.get('vram_gb')}",
                )

    # optional --ledger-summary: task counts + score means per ledger
    if args.ledger_summary:
        for r in reports:
            if not r["ok"]:
                continue
            rel = r["path"].relative_to(root)
            print(f"  summary {rel}:")
            for table, info in ledger_summary(r["path"]).items():
                bits = [f"rows={info['rows']}"]
                if info.get("tasks") is not None:
                    bits.append(f"tasks={info['tasks']}")
                for col, m in (info.get("means") or {}).items():
                    bits.append(f"mean({col})={m}")
                print(f"       {table}: {' '.join(bits)}")

    _line(
        "PASS" if failures == 0 else "FAIL",
        f"overall: {failures} structural check(s) failed",
    )
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
