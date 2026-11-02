# agency/ — Agency Plane

**English:** Endogenous agency plane — teleology, clinical analysis, dream
metabolization, witness lineage and curiosity over the vectorized code body.
Pure-Python public surface; canonical OmniMind modules are used as optional
adapters and every function degrades to a deterministic fallback when the
canonical source or the brain backends are unavailable.

**pt-BR:** Plano de agência endógena — teleologia, análise clínica,
metabolização onírica, linhagem testemunhal e curiosidade sobre o corpo de
código vetorizado. Superfície pública pura-Python; módulos canônicos OmniMind
são usados como adapters opcionais e toda função degrada para fallback
determinístico quando a fonte canônica ou os brains estão fora.

## Files

| File | Role | Public API |
|---|---|---|
| `teleology.py` | Endogenous mission generation | `generate_missions(context)` → list of short/medium/long-term missions (`context["cpu_high"]` triggers a `maintenance` mission); `compute_omega_teleology(state)` → coherence float 0..1 from mission/goal counts |
| `analyst.py` | **Adapter** (DIRECTORY_CONTRACT) — `src.agentes.psychoanalytic_analyst` | `analyze_session(session)`, `get_insights(context)` → clinical reading + acceptance criteria |
| `dream.py` | **Adapter** — `src.cognitive.dream_weaver` + own `dream_cycle` | `metabolize(idle_seconds, context)`, `weave(context)`, `dream_cycle(out_dir, n_chunks, witness_path)` → dream record |
| `curiosity.py` | Curiosity mode over the code index | `explore(topic, out_dir, k=6, use_llm=True)` → fragments + gap/suggestion synthesis |
| `witness.py` | Append-only JSONL lineage log, sha256 hash-chain | `append_witness(path, event)`, `read_witness(path, limit)`, `witness_event(type, data, path)`, `verify_witness(path)` → `{"valid", "records", "broken_at"}` |
| `__init__.py` | Re-exports the public API above | — |

## Control flow

```
topic ─► curiosity.explore ─► store.code_index.search (MiniLM + faiss/numpy)
                            └► agents._llm.brain_chat_json(role=executor) ─► synthesis
idle ─► dream.dream_cycle ──► code_index.search (corpus sample)
                            └► agents._llm.brain_chat(role=analyst, temp=0.9) ─► dream text
                            └► witness.witness_event ─► data/witness.jsonl (hash-chained)
soma ─► teleology.generate_missions ─► /agency/missions (app.py)
```

- `analyze_session` resolves config via `OMNI_ANALYST_CONFIG`, else
  `<repo>/config/agent_psychoanalytic.yaml`; canonical analyst is used only
  when the config exists and imports cleanly.
- `dream_cycle` samples the corpus with a fixed probe query, asks the analyst
  brain for a 2–4 sentence associative weave, and always appends the record to
  the witness log — even in extractive mode.
- `verify_witness` walks `prev_hash` continuity and recomputes content hashes;
  legacy records without `hash` break the chain at their index.

## Fallbacks

| Function | Canonical path | Fallback |
|---|---|---|
| `analyze_session` | `PsychoanalyticAnalyst(config)` | Static reading (`coherence=0.7`, fixed acceptance criteria, `source="fallback"`) |
| `metabolize` | `DreamWeaver().listen_to_bus()` | Counter derived from `idle_seconds` |
| `dream_cycle` / `explore` | brain `:8098` / `:8099` via `_llm` | Extractive text / fragments only (`source="extractive"`) |
| `compute_omega_teleology` | (probes `src.consciousness.integration_loop`) | Additive coherence metric |

## Dependencies

- **Imports:** `omni_coworker.store.code_index` (sentence-transformers + faiss/numpy + pandas), `omni_coworker.agents._llm` (httpx → OpenAI-compatible `/v1/chat/completions`).
- **Optional canonical:** `src.agentes.psychoanalytic_analyst`, `src.cognitive.dream_weaver`, `src.consciousness` — all probed lazily inside try/except; absence never raises.
- **Imported by:** `omni_coworker.app` (`/agency/missions`, `/dream/cycle`, `/curiosity/explore`), `agents.analyst_agent`, `cli.py`.
