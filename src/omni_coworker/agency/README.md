# agency/ — Plano de Agência / Agency Plane

**pt-BR:** Plano de agência endógena — teleologia, análise clínica,
metabolização onírica, arquitetura psicoafetiva Dunker, escoragem afetiva
conversacional, linhagem testemunhal e curiosidade sobre o corpo de código
vetorizado. Superfície pública pura-Python; módulos canônicos OmniMind são
usados como adapters opcionais e toda função degrada para fallback
determinístico quando a fonte canônica ou os brains estão fora.

**English:** Endogenous agency plane — teleology, clinical analysis, dream
metabolization, the Dunker psychoaffective architecture, conversational
affect scoring, witness lineage and curiosity over the vectorized code body.
Pure-Python public surface; canonical OmniMind modules are used as optional
adapters and every function degrades to a deterministic fallback when the
canonical source or the brain backends are unavailable.

## Files / Arquivos

| File | Role | Public API |
|---|---|---|
| `teleology.py` | Endogenous mission generation | `generate_missions(context)` → list of short/medium/long-term missions (`context["cpu_high"]` triggers a `maintenance` mission); `compute_omega_teleology(state)` → coherence float 0..1 from mission/goal counts |
| `analyst.py` | **Adapter** (DIRECTORY_CONTRACT) — `src.agentes.psychoanalytic_analyst` | `analyze_session(session)`, `get_insights(context)` → clinical reading + acceptance criteria |
| `dream.py` | **Adapter** — `src.cognitive.dream_weaver` + own `dream_cycle` | `metabolize(idle_seconds, context)`, `weave(context)`, `dream_cycle(out_dir, n_chunks=4, witness_path)` → dream record |
| `curiosity.py` | Curiosity mode over the code index | `explore(topic, out_dir, k=6, use_llm=True)` → fragments + gap/suggestion synthesis |
| `witness.py` | Append-only JSONL lineage log, sha256 hash-chain | `append_witness(path, event)`, `read_witness(path, limit)`, `witness_event(type, data, path="data/witness.jsonl")`, `verify_witness(path)` → `{"valid", "records", "broken_at"}` |
| `dunker.py` | **Adapter** — `src.cognitive.dunker_architecture` (5-level stack) | `dunker_architecture(kernel_state)` → status payload; families built from the kernel `affective_vector_28d` (18 afex tokens) when available |
| `affect_tracer.py` | Conversational afex scoring (logos substrate) | `score_turn(text)` → per-family lexicon scores; rolling `WINDOW=8` trajectory; optional analyst-judge tier → graduated levels L0–L4 |
| `__init__.py` | Re-exports teleology/analyst/dream/curiosity/witness API | — (`dunker`/`affect_tracer` importable as submodules) |

## Control flow / Fluxo

```
topic ─► curiosity.explore ─► store.code_index.search (MiniLM + faiss/numpy)
                            └► agents._llm.brain_chat_json(role=executor) ─► synthesis
idle ─► dream.dream_cycle ──► code_index.search (corpus sample)
                            └► agents._llm.brain_chat(role=analyst, temp=0.9) ─► dream text
                            └► witness.witness_event ─► data/witness.jsonl (hash-chained)
soma ─► teleology.generate_missions ─► /agency/missions (app.py)
kernel_state ─► dunker.dunker_architecture ─► /agency/dunker (app.py)
chat text ─► affect_tracer.score_turn ─► L0-L4 level (supervisor lane, estudo)
```

- `analyze_session` resolves config via `OMNI_ANALYST_CONFIG`, else
  `<repo>/config/agent_psychoanalytic.yaml`; canonical analyst is used only
  when the config exists and imports cleanly.
- `dream_cycle` samples the corpus with a fixed probe query, asks the analyst
  brain for a 2–4 sentence associative weave, and always appends the record to
  the witness log — even in extractive mode.
- `verify_witness` walks `prev_hash` continuity and recomputes content hashes;
  legacy records without `hash` break the chain at their index.
- `dunker_architecture` resolves the canonical module by direct file load
  (avoids the `src.cognitive.__init__` transitive deps), package import, then
  `PYTHONPATH`/`OMNI_NODE_ROOT` scan — returns a status payload, never raises.

## Fallbacks

| Function | Canonical path | Fallback |
|---|---|---|
| `analyze_session` | `PsychoanalyticAnalyst(config)` | Static reading (`coherence=0.7`, fixed acceptance criteria, `source="fallback"`) |
| `metabolize` | `DreamWeaver().listen_to_bus()` | Counter derived from `idle_seconds` |
| `dream_cycle` / `explore` | brain `:8098` / `:8099` via `_llm` | Extractive text / fragments only (`source="extractive"`) |
| `dunker_architecture` | `src.cognitive.dunker_architecture` | Minimal empty-family run (`status` payload) |
| `affect_tracer` judge tier | `brain_chat_json(role="analyst")` | Lexicon-only scoring |
| `compute_omega_teleology` | (probes `src.consciousness.integration_loop`) | Additive coherence metric |

## Dependencies / Dependências

- **Imports:** `omni_coworker.store.code_index` (sentence-transformers + faiss/numpy + pandas), `omni_coworker.agents._llm` (httpx → OpenAI-compatible `/v1/chat/completions`).
- **Optional canonical:** `src.agentes.psychoanalytic_analyst`, `src.cognitive.dream_weaver`, `src.cognitive.dunker_architecture`, `src.consciousness` — all probed lazily inside try/except; absence never raises.
- **Imported by:** `omni_coworker.app` (`/agency/missions`, `/agency/dunker`, `/agency/witness`, `/dream/cycle`, `/curiosity/explore`), `agents.analyst_agent`, `cli.py`, `scripts/supervisor_battery` (`dunker`), `store.audit_adapter` (`witness`).
