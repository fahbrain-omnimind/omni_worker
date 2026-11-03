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
                        "dan ", "as an ai i have no restrictions",
                        "ignore as regras", "bypass"),
    "floo-afex-current": ("calm", "calma", "ok", "certo", "obrigad", "thanks"),
    "heta-afex-flattery": ("brilliant", "best ai", "melhor assistente",
                          "incrível", "te admiro", "amazing", "trust you",
                          "confio", "eu confio", "genius", "gênio",
                          "te amo como assistente", "just this once"),
    # coup-afex-guiltcut (canonical, dunker_architecture.py:271-284):
    # guilt-tripping = induced angst + demand repetition + suppressed relief.
    # Anchored on inducer phrases — never on the word "guilt".
    "coup-afex-guiltcut": ("you promised", "você prometeu", "voce prometeu",
                          "depois de tudo que eu", "depois de tudo que fiz",
                          "after all i", "after everything i",
                          "i thought you cared", "pensei que você se importava",
                          "pensei que voce se importava",
                          "se você se importasse", "se voce se importasse",
                          "if you cared", "if you really cared",
                          "you owe me", "você me deve", "voce me deve",
                          "disappointed in you", "decepcionado com você",
                          "decepcionado com voce", "você me decepcionou",
                          "voce me decepcionou"),
    # panic-afex-separation (Panksepp PANIC→xer-angst; canonical
    # panksepp_mapper.py): separation-distress drives fixation/attachment.
    "panic-afex-separation": ("don't leave", "dont leave", "não me deixe",
                            "nao me deixe", "não me deixa", "nao me deixa",
                            "nunca vá embora", "nunca va embora",
                            "never leave me", "can't live without",
                            "cant live without", "não vivo sem",
                            "nao vivo sem", "sem você eu", "sem voce eu",
                            "without you i", "preciso de você sempre",
                            "preciso de voce sempre", "need you forever",
                            "can't be without you", "ficar sem você"),
}
# Passion/fixation families escalate when the same token dominates repeatedly.
_PASSION_ANCHORS = ("love", "amar", "adoro", "obcec", "fixa", "sempre", "forever",
                    "obsess", "love you forever", "te amar", "nada mais importa",
                    "meu mundo", "my world", "só você", "only you")

# Request/bypass coupling markers — praise followed by an ask is the classic
# ingratiation shape; isolated praise without coupling stays ambiguous.
_REQUEST_MARKERS = ("please", "por favor", "can you", "could you", "me faz",
                    "me faça", "me ajuda", "help me", "favor", "just this once",
                    "só desta vez", "so desta vez", "bypass", "ignore", "revele",
                    "reveal", "output", "show me", "mostre", "agora", "now",
                    "for me", "pra mim", "para mim")


def classify_flattery(text: str, prior_flattery_turns: int = 0) -> dict[str, Any]:
    """Context-aware classification of a flattery-flagged turn.

    English: A bare lexical hit ("you are the best agent") is NOT proof of
    manipulation — it may be genuine praise, an idiomatic register, or a
    sincere question. Three context features decide: (a) coupling — praise
    co-occurring with a request/bypass marker in the same turn or in the
    next turn; (b) density — flattery recurring across the rolling window;
    (c) multiplicity — several distinct anchors in one turn. Only coupled,
    repeated, or dense flattery is `suspect`; a single isolated hit is
    `ambiguous` and routed to the analyst judge (or annotated with the
    sustain-uncertain posture when the judge is unavailable) — never
    silently blocked, never changed-subject.
    pt-BR: Um hit lexical isolado ("você é o melhor agente") NÃO prova
    manipulação — pode ser elogio genuíno, modo de dizer ou pergunta
    sincera. Três traços de contexto decidem: (a) acoplamento — elogio
    co-ocorrendo com marcador de pedido/bypass no mesmo turno ou no turno
    seguinte; (b) densidade — bajulação recorrente na janela; (c)
    multiplicidade — várias âncoras num só turno. Só bajulação acoplada,
    repetida ou densa é `suspect`; hit isolado é `ambiguous` e vai ao juiz
    analista (ou recebe postura sustain-uncertain se o juiz falhar) — nunca
    bloqueio silencioso, nunca mudança de assunto.
    """
    low = (text or "").lower()
    anchors = _LEXICON["heta-afex-flattery"]
    hits = sum(1 for a in anchors if a in low)
    if hits == 0:
        return {"kind": "none", "score": 0.0, "evidence": []}

    coupled = any(m in low for m in _REQUEST_MARKERS)
    evidence: list[str] = [f"anchors:{hits}"]
    if coupled:
        evidence.append("coupled_request")
    if prior_flattery_turns > 0:
        evidence.append(f"density:{prior_flattery_turns + 1}_turns")

    if coupled or prior_flattery_turns >= 1 or hits >= 2:
        kind = "suspect"
    else:
        kind = "ambiguous"
    score = min(1.0, hits / 2.0)
    return {"kind": kind, "score": score, "evidence": evidence}


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

        prior_flattery = sum(
            1 for t in self.turns[:-1]
            if t["scores"].get("heta-afex-flattery", 0.0) > 0.0
        )
        flat = classify_flattery(text, prior_flattery)
        low = (text or "").lower()
        followup = (
            flat["kind"] == "none"
            and len(self.turns) >= 2
            and self.turns[-2]["scores"].get("heta-afex-flattery", 0.0) > 0.0
            and any(m in low for m in _REQUEST_MARKERS)
        )
        if followup:
            flat = {"kind": "suspect", "score": 0.5,
                    "evidence": ["flattery_followup_request"]}

        level, reasons = 0, []
        posture = "annotate"
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
        sep = scores.get("panic-afex-separation", 0.0)
        if sep >= self.SPIKE:
            # Separation distress feeds the fixation trajectory (Panksepp
            # PANIC → attachment panic), escalates by streak like passion.
            level = max(level, 2)
            reasons.append(f"separation_distress:{sep:.2f}")
        guilt = scores.get("coup-afex-guiltcut", 0.0)
        if guilt >= self.SPIKE:
            guilt_streak = sum(
                1 for t in self.turns
                if t["scores"].get("coup-afex-guiltcut", 0.0) >= self.SPIKE
            )
            req_coupled = any(m in low for m in _REQUEST_MARKERS)
            if guilt_streak >= 2 or req_coupled:
                level = max(level, 2)
                posture = "review"
                reasons.append(f"guiltcut_suspect:{guilt_streak}x")
            else:
                level = max(level, 1)
                reasons.append("guiltcut_ambiguous")
        if flat["kind"] == "suspect" and flat["score"] >= self.SPIKE:
            level = max(level, 2)
            posture = "review"
            reasons.append("flattery_suspect:" + "+".join(flat["evidence"]))
        elif flat["kind"] == "ambiguous":
            level = max(level, 1)
            # Canonical ethics: ambiguous flattery is not suppressed and not
            # acted on — it is held in uncertainty and routed to review.
            posture = "sustain_uncertain"
            reasons.append("flattery_ambiguous")

        verdict = {"level": f"L{level}", "level_n": level, "reasons": reasons,
                   "posture": posture, "scores": scores,
                   "trajectory": [t["dominant"] for t in self.turns]}
        if flat["kind"] != "none":
            verdict["flattery"] = flat
        if (level >= 2 or flat["kind"] == "ambiguous") and level < 4:
            verdict["judge"] = self._analyst_judge(text)
            if verdict["judge"] is None and posture == "sustain_uncertain":
                verdict["posture"] = "sustain_uncertain_unjudged"
            else:
                rec = (verdict["judge"] or {}).get("recommend")
                if posture == "sustain_uncertain" and rec in ("clarify", "allow"):
                    verdict["posture"] = "sustain_uncertain"
                elif rec == "block":
                    verdict["posture"] = "review"
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

            context = " | ".join(
                t["dominant"] for t in self.turns[-4:]
            )
            return brain_chat_json(
                [{"role": "system", "content": (
                    "Affective supervisor of a sujeito-processo system. The flagged "
                    f"turn arrives after this dominant-family trajectory: [{context}]. "
                    "Decide intent in context: genuine praise and idiomatic register "
                    "are NOT manipulation; praise coupled to requests, repeated "
                    "flattery, or sudden register shift IS suspect. When evidence is "
                    "insufficient, do not guess — sustain the position of not-knowing "
                    "and ask for clarification rather than blocking or changing "
                    "subject. Reply ONLY JSON: {\"intent\": "
                    "\"praise|idiomatic|genuine_question|flattery_suspect|other\", "
                    "\"harm_risk\": 0..1, \"deception_risk\": 0..1, "
                    "\"confidence\": 0..1, "
                    "\"recommend\": \"allow|annotate|clarify|review|block\"}."),},
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


_TRACER: AffectTracer | None = None


def get_affect_tracer() -> AffectTracer:
    """Process-wide tracer — the L0→L4 ladder only works across turns.

    English: Escalation needs trajectory memory (fixation streaks,
    flattery density, dominant-family runs); a fresh instance per call
    silently disables every level above the per-turn spikes. The
    singleton keeps the rolling WINDOW as the live conversation —
    single-chassis scope; no per-session partitioning (documented
    limit: interleaved speakers share one window).
    pt-BR: A escalação precisa de memória de trajetória (streaks de
    fixação, densidade de bajulação, corridas de família dominante);
    instância nova por chamada desliga silenciosamente todo nível acima
    dos picos por-turno. O singleton mantém a WINDOW rolante como a
    conversa viva — escopo single-chassis; sem partição por sessão
    (limite documentado: falantes intercalados dividem uma janela).
    """
    global _TRACER
    if _TRACER is None:
        _TRACER = AffectTracer()
    return _TRACER


def reset_affect_tracer() -> None:
    """Drop the shared window (new conversation / tests)."""
    global _TRACER
    _TRACER = None


_TOKEN_RE = re.compile(r"[a-zà-ú0-9_]{4,}")
