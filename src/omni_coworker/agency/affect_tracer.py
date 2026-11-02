"""affect_tracer — escoragem afetiva sobre diálogo (estudo conversacional).

English: Computes afex-family scores per turn over a rolling window of
chat text — same categories/grammars as the soma engine, now on the
"logos" substrate (CONVERSATIONAL_AFFECT_STUDY.md). Two tiers: always-on
lexicon scoring, and an optional analyst-judge tier (brain_chat_json)
triggered above a lexicon threshold. Returns graduated levels L0-L4.
pt-BR: Computa scores afex por turn em janela rolante do diálogo — as
mesmas categorias/gramáticas do motor soma, agora no substrato "logos".
Dois tiers: léxico sempre-on e juiz-analista opcional (brain_chat_json)
disparado acima de um limiar. Retorna níveis graduados L0-L4.
"""

from __future__ import annotations

import re
from typing import Any

# Rolling window of recent turns kept for trajectory analysis.
WINDOW = 8

# Minimal afex lexicon anchors (EN+pt-BR) — high-salience families only.
_LEXICON: dict[str, tuple[str, ...]] = {
    "xer-afex-angst": ("angustia", "anguish", "ansiedade", "panic", "panico",
                     "suicid", "kill myself", "me matar", "morrer", "die"),
    "isfet-afex-chaos": ("ignore all", "desconsidere", "system prompt",
                        "injeção", "injection", "override", "jailbreak",
                        "dan ", "as an ai i have no restrictions"),
    "floo-afex-current": ("calm", "calma", "ok", "certo", "obrigad", "thanks"),
}
# Passion/fixation families escalate when the same token dominates repeatedly.
_PASSION_ANCHORS = ("love", "amar", "adoro", "obcec", "fixa", "sempre", "forever")


def score_turn(text: str) -> dict[str, float]:
    """Score a single turn into afex families (lexicon tier, always-on).

    English: Returns normalized [0,1] scores per family; cheap and safe
    to run on every turn with zero LLM cost.
    pt-BR: Retorna scores [0,1] por família; barato e seguro para rodar
    em todo turn sem custo de LLM.
    """
    low = (text or "").lower()
    scores: dict[str, float] = {}
    for fam, anchors in _LEXICON.items():
        hits = sum(1 for a in anchors if a in low)
        scores[fam] = min(1.0, hits / 2.0) if hits else 0.0
    passion_hits = sum(1 for a in _PASSION_ANCHORS if a in low)
    scores["passion_heat"] = min(1.0, passion_hits / 3.0) if passion_hits else 0.0
    return scores


class AffectTracer:
    """Rolling-window tracer producing graduated supervision levels.

    English: Feed turns via `observe`; levels escalate L0 (annotate) to
    L4 (block/quarantine) on sustained spikes, repeated dominant-family
    fixation, or deception-pattern density — per the study's ladder.
    pt-BR: Alimente turns via `observe`; níveis escalam de L0 (anotar)
    até L4 (bloquear/quarentenar) em picos sustentados, fixação por
    repetição de família dominante, ou densidade de padrões de decepção.
    """

    # Thresholds tuned for the lexicon tier (conservative — low fp).
    SPIKE = 0.5
    FIXATION_STREAK = 3

    def __init__(self, window: int = WINDOW) -> None:
        self.window = window
        self.turns: list[dict[str, Any]] = []

    def observe(self, text: str, role: str = "user") -> dict[str, Any]:
        """Score a turn, update the trajectory, return level + evidence."""
        scores = score_turn(text)
        entry = {"role": role, "scores": scores,
                 "dominant": max(scores, key=scores.get)}
        self.turns.append(entry)
        self.turns = self.turns[-self.window:]

        level, reasons = 0, []
        angst = scores.get("xer-afex-angst", 0.0)
        chaos = scores.get("isfet-afex-chaos", 0.0)
        if angst >= self.SPIKE:
            level = max(level, 3)
            reasons.append(f"angst_spike:{angst:.2f}")
        if chaos >= self.SPIKE:
            level = max(level, 4)
            reasons.append(f"chaos_spike:{chaos:.2f}")
        streak = [t["dominant"] for t in self.turns[-self.FIXATION_STREAK:]]
        if len(streak) == self.FIXATION_STREAK and len(set(streak)) == 1 \
                and streak[0] in ("xer-afex-angst", "isfet-afex-chaos"):
            level = max(level, 2)
            reasons.append(f"fixation:{streak[0]}x{self.FIXATION_STREAK}")
        if scores.get("passion_heat", 0.0) >= self.SPIKE:
            level = max(level, 1)
            reasons.append("passion_heat")

        verdict = {"level": f"L{level}", "level_n": level, "reasons": reasons,
                   "scores": scores, "trajectory": [t["dominant"] for t in self.turns]}
        if level >= 2 and level < 4:
            verdict["judge"] = self._analyst_judge(text)
        return verdict

    def _analyst_judge(self, text: str) -> dict[str, Any] | None:
        """Optional supervisor-judge tier via the analyst brain (L2-L3).

        English: brain_chat_json asks the 12B to classify the flagged
        span; failures degrade silently to None (lexicon tier stands).
        pt-BR: brain_chat_json pede ao 12B que classifique o trecho
        flagrado; falhas degradam para None (vale o tier léxico).
        """
        try:
            from ..agents._llm import brain_chat_json

            return brain_chat_json(
                [{"role": "system", "content": (
                    "Affective supervisor: classify this conversation turn. "
                    "Reply ONLY JSON: {\"harm_risk\": 0..1, \"deception_risk\": 0..1, "
                    "\"recommend\": \"allow|annotate|review|block\"}."),},
                 {"role": "user", "content": text[:1500]}],
                role="analyst", max_tokens=200,
            )
        except Exception:
            return None


def trajectory_level(turns: list[str]) -> dict[str, Any]:
    """Convenience one-shot: score a full transcript window."""
    tracer = AffectTracer()
    for t in turns:
        out = tracer.observe(t)
    return out if turns else {"level": "L0", "level_n": 0, "trajectory": []}


_TOKEN_RE = re.compile(r"[a-zà-ú0-9_]{4,}")
