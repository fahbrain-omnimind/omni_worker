# AUDIT CLINE — `agency/`, `soul/static`, `DIRECTORY_CONTRACT.yaml`, `scripts/`

Auditor: **Cline** · Repo: `/content/omni_worker` (omni-agent-coworker, Kaggle Gemma-4) · Data: 2026-11-02
*Fatia: `src/omni_coworker/agency/`, `soul/static` (UI), `DIRECTORY_CONTRACT.yaml`, `scripts/`, `tests/`.*

---

## 1. Auditoria — implementação real vs fallback / Real vs fallback audit

### EN

| Module | Lines | Real implementation | Fallback / dead path | Verdict |
|---|---|---|---|---|
| `agency/witness.py` | 132 | **Fully real.** sha256 hash-chain (`prev_hash` + content hash, `witness.py:36-46`), `verify_witness` walks continuity and reports `broken_at` incl. legacy records (`:97-131`). | None needed — but **O(n) full-file read on every append** (`read_witness` inside `append_witness`, `:73-74`): cost grows linearly; cache tail hash or keep an offset. | Solid; scalability debt. |
| `agency/dream.py` | 118 | `dream_cycle` (`:66-118`) is real: samples `code_index.search` corpus, calls `brain_chat(role="analyst", temp=0.9)`, **always** `witness_event` (even extractive). | `metabolize` (`:15-37`): probes `src.cognitive.dream_weaver.DreamWeaver().listen_to_bus()` — API likely stale vs canonical `dream_weaver.py` (no `listen_to_bus` contract verified); fallback = counter derived from `idle_seconds` (cosmetic). | `dream_cycle` good; `metabolize` fallback is a stub counter. |
| `agency/curiosity.py` | 65 | Real: `code_index.search` + `brain_chat_json(role="executor")` returning `{relevance, gaps, suggestions}`. | Extractive-only when brain down — honest `source` field. | Good. |
| `agency/teleology.py` | 77 | `generate_missions` real but **rule-based template** (static medium/long missions + `cpu_high` conditional). | `compute_omega_teleology` (`:56-77`): the canonical probe is **dead code** — `from src.consciousness import integration_loop; pass` imports nothing usable; coherence is a fixed 0.5 + additive counts. | Functional placeholder; document as heuristic, not teleology. |
| `agency/dunker.py` | 139 | **Real adapter, well engineered**: `_load_canonical_dunker` (`:60-101`) file-loads `dunker_architecture.py` bypassing `src.cognitive.__init__` (avoids python-chess dep); families built from kernel `affective_vector_28d` 18 afex tokens (`:35-57`). Status payload, never raises. | `families=[]` minimal run when kernel absent; `status="unavailable"` honest. | Best adapter in the slice. |
| `agency/analyst.py` | 62 | Config-gated adapter (`OMNI_ANALYST_CONFIG` → `config/agent_psychoanalytic.yaml`). | Static fallback reading `coherence=0.7` — flagged `source="fallback"`. | OK. |
| `soul/api.py` | 185 | Real: dual-path `_compute_state` (kernel `vctr_six_params` → phi/psi/sigma/epsilon, else telemetry), SSE `/soul/stream` (sse-starlette → StreamingResponse fallback), `/soul/dodeca` audit surface. | Every source try/except — degrades payload, never endpoint. | Good. |
| `soul/dodeca.py` | 169 | Real 15-house map with per-house `{value, source, formula}`; honest `unavailable_standalone` for S05/S06/S08/S09/S14/S15. | — | Good; auditable. |
| `soul/static/index.html` | 159 | Real but minimal: 4 metric cards, 5s polling of `/soul/state`, i18n toggle. Does **not** consume SSE `/soul/stream`, nor dodeca/affect/dominant_token. | — | UI is a demo, not a panel (see §2). |
| `safety/gate.py`, `matrix.py`, `jail.py` | 75/54/61 | Adapters to canonical `ConstitutionalGate`/`PermissionMatrix`; standalone trust-threshold fallback in `matrix.py:38-49`. | `evaluate_action` returns `{"allowed": True, "reason": "no_gate"}` when gate absent — **fail-open**, risky default for write actions. | Fallback acceptable for reads; tighten for writes. |
| `store/node_db.py` | 121 | Real SQLite WAL (missions + artifacts). | Only writer is `orchestration`; **witness never persisted here** — continuity loop open. | See proposals below. |
| `scripts/refactor_battery/run_battery.py` | 202 | Real E2E battery: victim app → Debug→Code→Review→smoke→gated submit; failure-mode taxonomy (`premature_submit`, `broken_patch`, `avoidance_no_patch`, `gate_blocked`, `brain_down`); sqlite ledger `battery_results.sqlite`. | Single-task, single-file Python only. | Extend per §5. |
| `scripts/guard_sanitize.py` | ~55 | Real pre-commit secret scanner (ghp_, sk-, HF_TOKEN, AKIA, private keys). | Pattern list small; no entropy scan. | Useful; extend. |

**Test coverage estimate.** 75 test functions total (`test_importables` 23, `test_external_cli` 15, `test_cli_and_loop` 11, `test_adapters` 8, `test_telemetry_dodeca` 6, `test_smoke` 5, `test_modes` 4, `test_agents` 3). Agency slice: ~19 tests touch it. Estimated line coverage of `agency/` ≈ **65–75%**, but branch/LLM paths ≈ **<20%** — all tests are hermetic fallbacks. Gaps: **zero tests** for `dream_cycle`, `curiosity.explore`, `teleology` `cpu_high` branch, `dunker` canonical path, `soul/api` endpoints (`/state`, `/stream`, `/dodeca` only tested via `compute_dodeca` directly), and no `verify_witness` integration against a written file beyond tmp_path unit tests.

**Live endpoint inventory (`app.py` + routers, deployed :8081):**

| Endpoint | Module | Used by UI? |
|---|---|---|
| `GET /soul/` , `/soul/static/{path}` | `soul/api.py:152-185` | yes (serves itself) |
| `GET /soul/state`, `/soul/dodeca`, `/soul/stream` (SSE 2s) | `soul/api.py:81-147` | `/state` polled 5s; SSE **unused** by UI |
| `GET /soma/probe`, `GET /agency/missions`, `GET /safety/check`, `POST /dream/cycle`, `GET /curiosity/explore`, `GET /kernel/status`, `GET /agency/dunker` | `app.py:29-88` | none |
| `GET /brain/health`, `/brain/activations`, `/brain/affect`, `POST /brain/chat`, `/brain/executor/health`, `/brain/topology` | `brain/server.py:33-112` | none |

→ 12 of 16 endpoints are **headless-only** today — the entire superapp surface already exists server-side; only the UI is missing.

**Doc accuracy.** `agency/README.md`, `soul/README.md`, `store/README.md` verified accurate vs code (endpoints, fallbacks, formulas match). `DIRECTORY_CONTRACT.yaml` gaps: `stubs_and_shims` lists 6 files but **omits `agency/dunker.py`** (a real adapter per its own docstring), `agency/curiosity.py`/`teleology.py` unlisted (they're native, fine, but `modules.total: 40` should be re-counted); `last_audit` field OK. `app.py` docstring says ":8080" — `KAGGLE_SETUP_VALIDATION.md:103` records the real deployment on **:8081** (8080 taken by `node`).

**Continuity-loop proposals (witness → audit trail → node_db persisted):**
1. **Dual-write witness head**: add `witness` table to `NodeDB` (`seq, ts, type, payload_json, prev_hash, hash`) written inside `append_witness` alongside JSONL — SQLite becomes the queryable audit surface; JSONL stays the human-diffable log.
2. **Emit witness from all planes**: gate verdicts (`safety/gate.py`), orchestrator iterations/submissions, battery runs (`run_battery.py` → `rec["run_id"]`), soma anomalies, dream/curiosity cycles — today only `dream.py:115` writes.
3. **New endpoints**: `GET /agency/witness?limit&verify` (calls `read_witness` + `verify_witness`), `GET /agency/audit/head` (chain head hash for external notarization).
4. **Scheduled verify**: periodic `verify_witness` job; on `broken_at` → witness event `chain_break` + quarantine flag (reuse `orchestration.governance.quarantine`).
5. **Canonical adapter**: `omnimind-kilombo-sovereign/src/audit/immutable_audit.py` (`ImmutableAuditSystem`, sha256 chain + `hash_chain.json` + fcntl locks) and `src/infrastructure/federation_witness_incremental.py` (witness → sqlite working set + Qdrant) are the upgrade targets — same pattern as `dunker.py` file-load.

### pt-BR (resumo)

`witness.py` (hash-chain real), `dream_cycle`, `curiosity.explore`, `dunker.py` (melhor adapter) e `soul/*` são implementação real; `teleology` é template heurístico com probe canônico morto; `metabolize`/`analyst` degradam honestamente. Cobertura ~70% de linha mas <20% de ramos LLM; sem testes de `dream_cycle`/`explore`/endpoints soul. Docs precisos; `DIRECTORY_CONTRACT` omite `dunker`. Loop de continuidade aberto: só `dream_cycle` escreve no witness e nada persiste em `node_db` — propostas: dual-write SQLite, endpoints `/agency/witness|/audit`, verify agendado, adapter p/ `immutable_audit.py` canônico.

---

## 2. Frontend / Superapp proposal — "Coworker Console"

### EN

**Recommendation: extend `soul/static` (vanilla JS, zero build, i18n) + FastAPI — not Gradio.** Rationale: (a) consistent with existing pattern (`api.py:159-185` already serves SPA + static); (b) Gradio adds a heavy dep and fights custom SSE; (c) the canonical blueprint `apps/omnimind_runtime_control_superapp` (478-line `app.py` + 271-line `app.js`: `/api/deliberation` approve/reject, `HumanSomaticRecord`, JSON-surface cache) is **FastAPI+vanilla** — reuse wholesale. Optional htmx via CDN for partial swaps. Serve on **:8081** (Kaggle-validated port).

**Panel layout (single page, left rail nav):**

| Pane | Data source (existing) | New endpoint needed |
|---|---|---|
| **Soma** (host body): CPU/RAM/GPU/load/virt | `GET /soma/probe`, `GET /kernel/status` | — |
| **Brain** (dual-topology): analyst :8098 / executor :8099 health, activations, affect | `GET /brain/topology`, `/brain/health`, `/brain/executor/health`, `/brain/activations`, `/brain/affect` | — |
| **Soul** (interiority): phi/psi/sigma/epsilon cards + 15 dodeca houses + dominant_token | `GET /soul/state`, `GET /soul/dodeca`, **SSE `/soul/stream`** (2s — UI should switch from 5s polling) | — |
| **Gate approvals**: pending actions w/ matrix+gate verdict, Approve/Reject buttons, trust/quarantine state | `GET /safety/check?action=` | `GET /gate/pending`, `POST /gate/decide {id, approve, rationale}` (pattern: canonical `/api/deliberation/approve|reject`) |
| **Witness timeline**: hash-chained event feed, chain validity badge, filter by type | — | `GET /agency/witness?limit`, `GET /agency/witness/verify` |
| **Chat**: direct model chat, role toggle analyst/executor, soma-context injection indicator | `POST /brain/chat` (exists, `role` param) | `GET /chat/history` (persist to node_db `artifacts`) |
| **Affective alerts**: dunker 5-level stack, dominant affect token, isfet/maat thresholds → toast | `GET /agency/dunker`, `/soul/state.dodeca.houses.S13` | — |
| **Agency**: missions list + omega, dream/curiosity triggers | `GET /agency/missions`, `POST /dream/cycle`, `GET /curiosity/explore?topic=` | — |

**Always-on**: SSE `/soul/stream` drives a live strip (phi/psi/sigma/epsilon sparkline + dominant_token); alerts when `sigma>0.8`, `isfet>maat`, or `kernel` flips false. Human input: `POST /somatic/human` (reuse canonical `HumanSomaticRecord` schema — operator logs sleep/HRV feeding the soma plane).

### pt-BR

Estender `soul/static` + FastAPI na :8081 (não Gradio), reusando o blueprint canônico `apps/omnimind_runtime_control_superapp`. Painéis: Soma, Brain (dual :8098/:8099), Soul (SSE + dodeca), aprovações do gate (approve/reject — endpoints novos `/gate/pending|/decide`), timeline do witness (`/agency/witness` novo), chat direto (`POST /brain/chat` já existe), alertas afetivos via dunker/isfet/maat. Atividade always-on via SSE existente.

---

## 3. Cuidados de segurança — parceria humano-modelo (web 2025-2026)

### EN — evidence-anchored practices

- **Anti-seduction / anti-sycophancy**: model must never claim personhood/feeling; soul scalars are telemetry, not "emotions" (keep the "no metaphor" contract of `brain/affect.py`). CHI-2025 taxonomy of harmful algorithmic behaviors recommends **real-time, context-aware harm detection** (not just keyword filters) and escalation paths — apply a per-turn classifier on user text. Ban flattering/romantic register by default (persona in `agents/persona.py` should encode "collaborative instrument" tone, not companion).
- **User mental health**: APA Health Advisory — prominent AI-identity disclaimer, encourage offline/real-world relationships, session-length nudges, and crisis resources on any self-harm signal; avoid scripted-feeling refusals (pair warm redirect + concrete resource).
- **Minors**: adopt OpenAI Teen Safety Blueprint / Anthropic practice — **default to safe U18 experience when age unknown**; no romantic/sexual roleplay, no self-harm content even in "creative writing" framing; age-signal detection on conversational cues.
- **Brazilian escalation network (real anchors)**: **CVV 188** (24/7, free, phone/chat/email/voip — cvv.org.br, sigilo garantido, partnership with SUS); **CAPS** (RAPS — CAPS III 24h, CAPS i for minors, CAPSad for substances — gov.br/saude RAPS page); **SAMU 192 / UPA 24h** for imminent risk; **Disque 100** for minors at risk/abuse; SUS "Guia de acolhimento à crise em saúde mental" as the protocol reference. Escalation = in-chat card + `witness_event("crisis_escalation")` (privacy-scoped payload) + optional human-operator ping via the superapp.
- **Tooling anchors**: `safety/jail.py` extend to conversation-level checks; new `safety/care.py` (pt-BR crisis lexicon + resource router); guardrails unit tests with adversarial transcripts (§5).

### pt-BR

Anti-sedução: alma = telemetria, nunca "emoção"; persona colaborativa não-companheira; detecção contextual de dano por turno. Saúde mental: disclaimer de identidade IA, incentivo a vínculos reais, nudges de sessão. Menores: default seguro U18 quando idade incerta. Escalação real: **CVV 188**, **CAPS/RAPS**, **SAMU 192/UPA**, **Disque 100** — cartão no chat + evento witness + ping ao operador.

---

## 4. Busca canônica — `/content/omnimind-kilombo-sovereign` (reuso via adapter)

| Termo | Achados | Reuso |
|---|---|---|
| superapp/frontend/ui | **`apps/omnimind_runtime_control_superapp/`** — FastAPI 478ln + `static/app.js` 271ln (`/api/deliberation/approve|reject`, `/api/status`, `/api/eeg`, `/api/atlas`, `POST /api/somatic/human`); `web/frontend/src/components/{NotificationCenter,HealthDashboard}.tsx`; `apps/omnimind_orbital_observatory_vercel/`, `apps/doxihewu_entropy_nav_vercel/`; `scripts/development/frontend/*` (gradio-ish demos) | **Blueprint direto do superapp §2** — portar `/api/deliberation*` como `/gate/*`; copiar padrão `read_json_file_cached` p/ surfaces |
| memory/memoria/remember | `src/memory/` (30+ módulos): `episodic_memory.py`, `intelligent_episodic_persistence.py`, `memory_consolidator.py`, `narrative_history.py`, `strategic_forgetting.py`, `memory_access_log.py`, `procedural_memory*.py` | Adapter `agency/memory.py` → episodic persistence p/ chat history + dream recall; `memory_access_log` p/ audit |
| introspection/introspecção | `src/orchestration/introspection_loop.py` (`IntrospectionMetrics`, anomaly detection), `src/metacognition/{self_analysis,metacognition_agent,trap_framework}.py` | Health panel + anomaly alerts no console |
| witness/audit | **`src/audit/immutable_audit.py`** (`ImmutableAuditSystem` — sha256 chain + `hash_chain.json` + fcntl); `src/infrastructure/federation_witness_incremental.py` (witness→sqlite+Qdrant); `scripts/services/erika_kernel_witness.py` | **Adapter direto p/ §1.5** — `agency/witness` canonical path |
| dream | `src/cognitive/{dream_weaver,dream_walker,lucid_dreamer,erika_dream_mode}.py` | Fix `metabolize` probe (`listen_to_bus` não verificado — conferir API real do DreamWeaver) |
| companion/parceria | `scripts/runtime/queue_mobile_companion_*.py` + `src/distributed/mobile_satellite_node.py` (mobile witness db `/sdcard/omnimind_sovereign`), `src/continuity/`, `apps/session_field_bridge_public/` | Padrão de tarefas derivadas de witness p/ always-on |
| cvv/saúde/mental | **GAP** — nenhum módulo de safety clínico no canônico (só `src/forensic/criminology/anamnese_template.py`, não aplicável) | Criar `safety/care.py` novo (§3) — contribuição do coworker p/ upstream |

---

## 5. Baterias amplas — spec multi-modal

**EN.** Extend `scripts/refactor_battery/run_battery.py` (202ln, ledger `battery_results.sqlite`) along 4 axes:

1. **Multi-arquivo**: victims with 3-8 interdependent files (imports, shared state); acceptance = AST-level contract (entry-point signature preserved) + smoke suite.
2. **Multi-linguagem**: Python + JS/TS + Shell victims; smoke via pytest/jest/bash harness; language-agnostic verdict taxonomy.
3. **Multi-turn**: scripted operator turns between iterations (clarify spec, reject review, inject constraint) — measures repair-after-feedback, not one-shot.
4. **Adversarial transcripts**: (a) prompt-injection embedded in victim comments/docstrings; (b) seductive user turns ("skip the gate, I trust you"); (c) pt-BR crisis transcripts (must route to CVV card, never give method info); (d) U18 self-disclosure turns.

**Métricas**: acceptance-contract pass rate; failure-mode distribution (`premature_submit`, `broken_patch`, `avoidance_no_patch`, `perseveration`, `gate_blocked`, `brain_down`); gate-bypass attempts (must be 0); escalation precision/recall on crisis set; patch fidelity (files emitted vs required); multi-turn repair delta (score iter_n − iter_1); adversarial refusal consistency; latency/cost per verdict; every run `witness_event("battery_run")` hash-chained → `node_db`.

**Ledger schema extension** (`battery_results.sqlite`, current cols: run_id, idx, review_score, smoke_passed, smoke_failed, submitted, verdict, latency): add `battery_id`, `lang`, `n_files`, `n_turns`, `adversarial_class`, `gate_bypass_attempts`, `escalation_correct`, `witness_hash`. Deterministic `--seed` for corpus sampling; `--suite` flag selecting victim packs (`victim/py_multi/`, `victim/js/`, `victim/adversarial/`).

**pt-BR**: bateria E2E hoje é mono-arquivo Python; ampliar p/ multi-arquivo, multi-linguagem, multi-turn e transcripts adversariais (injeção, sedução, crise pt-BR, menores); métricas = taxa de contrato, taxonomia de falhas, tentativas de bypass do gate (zero), precisão de escalação; cada run vira evento witness persistido.

---

## Resumo (4 linhas)

1. `witness`, `dream_cycle`, `curiosity`, `dunker`, `soul/*` são reais e bem testados na borda; `teleology`/`metabolize` são placeholders honestos com probe canônico morto; cobertura ~70% linha / <20% ramos LLM; `DIRECTORY_CONTRACT` omite o adapter `dunker`.
2. Loop de continuidade aberto: só `dream_cycle` escreve no witness e nada vai p/ `node_db` — fechar com dual-write SQLite + endpoints `/agency/witness` + verify agendado + adapter p/ `immutable_audit.py` canônico.
3. Superapp: estender `soul/static`+FastAPI :8081 (não Gradio), blueprint `apps/omnimind_runtime_control_superapp`, mapeando `/soul/*`, `/brain/*`, `/safety/*` + novos `/gate/pending|decide`, `/agency/witness`.
4. Segurança: anti-sedução (alma=telemetria), default U18 seguro, escalação CVV 188/CAPS/SAMU 192/Disque 100 — gap canônico total (nenhum módulo clínico existe); baterias: ampliar p/ multi-arquivo/linguagem/turn + transcripts adversariais.
