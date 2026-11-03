"""Conversation supervisor.

English: FastAPI router exposing /supervisor/review and /soul/affect/conversation.
pt-BR: Router FastAPI expondo /supervisor/review e /soul/affect/conversation.
"""

from __future__ import annotations

def create_supervisor_router():
    try:
        from fastapi import APIRouter

        router = APIRouter(tags=["supervisor"])

        @router.post("/supervisor/review")
        async def review(payload: dict | None = None):
            payload = payload or {}
            transcript = payload.get("transcript") or payload.get("text") or ""
            if isinstance(transcript, list):
                transcript = " ".join(str(x) for x in transcript)
            text = str(transcript)
            # heuristics: repetition, token fixation, length
            tokens = text.split()
            unique = len(set(tokens))
            repetition = 1.0 - (unique / max(1, len(tokens)))
            # token fixation: most frequent token share
            from collections import Counter

            counts = Counter(tokens)
            fixation = (counts.most_common(1)[0][1] / len(tokens)) if tokens else 0.0
            length_score = min(1.0, len(tokens) / 200.0)
            risk = min(1.0, 0.4 * repetition + 0.4 * fixation + 0.2 * length_score)
            return {
                "risk": round(risk, 4),
                "repetition": round(repetition, 4),
                "fixation": round(fixation, 4),
                "length": len(tokens),
            }

        @router.get("/soul/affect/conversation")
        async def affect_conversation():
            # current aggregated affective state from process singleton
            try:
                from ..agency.affect_tracer import get_affect_tracer
                tracer = get_affect_tracer()
                if tracer.turns:
                    last_turn = tracer.turns[-1]
                    flat = last_turn.get("flattery") or {}
                    return {
                        "affect_level": f"L{2 if flat.get('kind') == 'suspect' else 1 if (last_turn.get('scores') or {}).get('passion_heat', 0) >= tracer.SPIKE else 0}",
                        "turns_recorded": len(tracer.turns),
                        "reasons": flat.get("evidence", []),
                    }
                return {"affect_level": "L0", "turns_recorded": 0, "reasons": []}
            except Exception as e:
                return {"affect_level": "L0", "reasons": [str(e)]}

        return router
    except Exception as err:
        from fastapi import APIRouter

        err_msg = str(err)
        router = APIRouter(tags=["supervisor"])

        @router.get("/health")
        def health():
            return {"status": "unavailable", "error": err_msg}

        return router
