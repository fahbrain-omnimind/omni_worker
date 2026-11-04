"""Forensic scanner for bibliographic and manuscript integrity."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

EPISTEMIC_TAGS = (
    "[DADO]",
    "[DERIVADO]",
    "[INTERPRETAÇÃO]",
    "[LIMITE]",
    "[PRX]",
    "[CAP]",
    "[TXT]",
    "[CLS]",
    "[EXP]",
)


def compute_md5(path: str) -> str:
    try:
        return hashlib.md5(Path(path).read_bytes()).hexdigest()
    except OSError:
        return ""


def detect_duplicates(paths: list[str]) -> list[tuple[str, str, str]]:
    by_md5: dict[str, list[str]] = {}
    for p in paths:
        h = compute_md5(p)
        if h:
            by_md5.setdefault(h, []).append(p)
    return [
        (group[i], group[j], h)
        for h, group in by_md5.items()
        for i in range(len(group))
        for j in range(i + 1, len(group))
    ]


def verify_manifest_entry(
    path: str, expected_author: str, expected_title: str
) -> dict[str, bool]:
    try:
        header = Path(path).read_text(encoding="utf-8", errors="replace")[:2500].lower()
    except OSError:
        return {"author_match": False, "title_match": False, "anomaly": True}
    a_toks = [
        t.lower() for t in re.split(r"[^a-zA-ZÀ-ÿ]+", expected_author) if len(t) >= 3
    ]
    t_toks = [
        t.lower() for t in re.split(r"[^a-zA-Z0-9À-ÿ]+", expected_title) if len(t) >= 4
    ]
    a_ok = bool(a_toks) and any(t in header for t in a_toks)
    t_ok = bool(t_toks) and (sum(1 for t in t_toks if t in header) / len(t_toks)) >= 0.6
    return {"author_match": a_ok, "title_match": t_ok, "anomaly": not (a_ok and t_ok)}


def count_epistemic_tags(text: str) -> dict[str, int]:
    return {tag: (text.count(tag) if text else 0) for tag in EPISTEMIC_TAGS}


def tabular_tail_ratio(text: str) -> float:
    lines = [ln.split() for ln in (text or "").splitlines() if ln.strip()]
    if not lines:
        return 0.0
    num_re = re.compile(r"[-+]?\d+([.,]\d+)?([eE][-+]?\d+)?%?")
    tab = sum(
        1
        for toks in lines
        if len(toks) >= 3
        and sum(1 for t in toks if num_re.fullmatch(t)) >= len(toks) / 2
    )
    return round(tab / len(lines), 4)
