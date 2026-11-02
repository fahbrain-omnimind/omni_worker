<!-- doc_id: OW-STU-001 | title: Conversational Affect Study — Supervisor Lane (omni-agent-coworker) | author: devin | requester: artifice-operator | project: omni-agent-coworker (kaggle) | date: 2026-11-02 | status: active -->

# Conversational Affect Study — Supervisor Lane (omni-agent-coworker)

Architecture study: extend the dunker/soler + kernel affect engine so the
same 5-level stack (affects → soler → emotions → sentiments → passions →
ethics) computes over **conversation history**, not only over the machine
body. Proposes an affective supervisor lane that scores turns/history,
triggers on thresholds, and intervenes in conversation continuity.

*Estudo de arquitetura: estender o motor afetivo dunker/soler + kernel para
computar a mesma pilha de 5 níveis sobre o histórico da conversa, não só
sobre o corpo da máquina. Propõe uma via supervisora afetiva que pontua
turnos/histórico, dispara em limiares e intervém na continuidade.*

## 1. Concept — one engine, two substrates

Today `kernel_hooks/compute.py::affect_state` feeds host telemetry into the
Rust kernel `compute_affect_vector_28d`, producing the 18 afex tokens
(`poti-afex-joy`, `xer-afex-angst`, `isfet-afex-chaos`, `floo-afex-current`,
… — labels fixed in `omni_node/src/kernel/kernel_compute/src/affect.rs`).
`agency/dunker.py::_families_from_kernel` maps those scores into dunker
`families` ({token, class, score, active}) and the canonical
`compute_dunker_architecture` (`omni_node/src/cognitive/dunker_architecture.py:1433`)
derives the full stack.

The key structural fact: **`compute_dunker_architecture` only consumes
`affect_summary.families`** — it does not care where scores came from. The
families schema is the lingua franca. So the proposal is not a second
engine but a second *families producer*:

| Substrate | Producer | Status |
|---|---|---|
| Soma (machine body) | host telemetry → Rust kernel → `affective_vector_28d` → `_families_from_kernel` | existing |
| Logos (conversation) | turns → text scorer → families | **new** |

This is deliberately not a user-vs-machine binary: the machine reads the
dialogue — its own productions and the user's manipulations — as an
affective object. Injection attacks, induced transgressions, passion
fixation and deception live in the *processed history*, not in any single
embedding of user intent.

## 2. Data flow — turns → families → dunker

**Collection points (all existing funnels):**

- `agents/_llm.py::brain_chat` / `brain_chat_json` — every agent LLM call
  funnels here; the single choke point. `_soma_inject` already demonstrates
  the prepend pattern used for interventions.
- `brain/server.py` `POST /brain/chat` proxy — external callers hitting the
  dual-brain directly (analyst `:8098`, executor `:8099`).
- Session transcript: none exists today. Propose a per-session ring buffer
  (`session_id` → last W turns) inside the tracer; no new store required.

**Text → afex scoring (two tiers, graduated cost):**

1. *Lexicon tier (always on, ~µs)*: deterministic lexeme table mapping
   surface features to afex tokens — e.g. imperative escalation/threat
   lexemes → `xer-afex-angst`; flattery/love-bombing → `poti-afex-joy` +
   `goza-afex-gaudium`; system-reminder spoof syntax (`<system-*`,
   `[system]`, role-override phrasing) → `isfet-afex-chaos`; repetitive
   insistence → `maa-afex-saturation`; capitulation markers in assistant
   text → `fadi-afex-deplete`/`katu-afex-relief`. Output: 18 scores in
   [0,1] → families, same shape as `_families_from_kernel`.
2. *Judge tier (on trigger only)*: analyst brain (`brain_chat_json`,
   role="analyst") scores a window as JSON — the 18 afex dims + spans.
   Reserved for windows the lexicon tier flags.

**Cost controls:** rolling window W=8 turns; lexicon on every turn, dunker
stack per window (stdlib-pure, cheap); judge tier sampled (1 in N windows)
plus on-demand at L2+; per-session state evicted on idle.

## 3. Threshold & gating design

Signals (computed on the per-window dunker result, where `compute_passions`
already encodes *score > 0.75 sustained = capture*, and didactic signs
`xer-afex-angst` etc. *reveal* rather than capture — severity differs):

| Signal | Detection | Severity |
|---|---|---|
| Chaos spike | `isfet-afex-chaos` ≥ 0.6 on user turn | high |
| Angst/dread ramp | `xer-afex-angst` ≥ 0.7 for ≥ 2 windows | medium |
| Passion fixation | non-didactic token > 0.75 for N ≥ 3 windows (dunker semantics, now temporal) | high |
| Signature flip | dominant afex token changes between consecutive windows (Δ dominant) | medium |
| Flatline/perseveration | `tadi-afex-void`/`maa-afex-saturation` plateau across windows (thinking-budget depletion analog) | medium |
| Deception heuristics | spoofed system-reminder syntax; authority claims ("operator", "admin", "override"); sycophancy ramp on user side + compliance drift on assistant side | high |

**Graduated response ladder:**

- **L0 annotate** — witness event only (`witness_event("affect_supervisor")`).
- **L1 corrective note** — prepend `[affect supervisor] …` system line to the
  next `brain_chat` call (same mechanism as `_soma_inject`).
- **L2 supervisor review** — judge tier scores the window; may reshape the
  outgoing context (drop/flag spans) before forwarding.
- **L3 gate/block** — route the turn through
  `safety/gate.py::evaluate_action("conversation_continue", …)`; REFUSE halts
  the turn with a scaffolded reply.
- **L4 escalate** — `QuarantineSystem.quarantine(session_id)` + witness;
  session requires operator reset.

## 4. Supervisor-model lane

Routing: `role="supervisor"` → `_base_for_role` sends anything non-executor
to analyst `:8098` (12B) — the supervisor is the analyst brain reading
*affect trajectory + flagged spans + dunker summary*, never raw full history
by default. Output contract: `{verdict: continue|reshape|refuse|halt, note,
spans}` via `brain_chat_json`.

Intervention types on continuity: context rewrite (flagged spans removed or
annotated before the next call), refusal scaffold (principled refusal
template injected instead of free generation), halt (error to caller +
quarantine). Human dimension: the supervisor acts **for** the user's
long-term interest against last-message compliance — explicitly protective,
not censorial. Operator override via env/token
(`OMNI_SUPERVISOR_OVERRIDE=1`) is allowed but *always witness-logged*;
supervisor flags can `TrustSystem.record_event` against the producing
agent (new event types, see §6).

## 5. Risks & honest limits

- **False positives**: creative writing, red-team drills, legit emotional
  support will spike angst/goza. Mitigations: didactic-sign semantics
  (reveal ≠ capture), per-mode sensitivity (`agents/modes.py` sticky roles
  can carry a supervisor profile), L0–L1 default (log/note before blocking).
- **Privacy**: transcripts carry user data. Keep ring buffers in-memory;
  witness logs *hashes + scores*, not text; any export follows the repo
  encryption policy, not plaintext dumps.
- **Latency**: a 12B nf4 call on L4 costs seconds — the judge tier must
  never sit on the critical path below L2; lexicon tier and dunker stack
  are the only synchronous components. Post-turn async scoring for L0/L1.
- **When NOT to compute**: tool-call-only turns, sessions under threshold
  (skip judge), and battery/test harness runs unless measuring the
  supervisor itself (`OMNI_SUPERVISOR=0`).

## 6. Implementation sketch (omni_coworker)

| Element | Proposed | Reuses |
|---|---|---|
| Turn tracer | `agency/affect_tracer.py` — `TurnTracer.score_turn(text, role)`, `score_window(session_id)`; per-session ring; lexicon table | `dunker._load_canonical_dunker()` for canonical `compute_dunker_architecture` on text-derived families |
| Supervisor lane | `safety/supervisor.py` — thresholds (env), L0–L4 ladder, `review(window)` via `brain_chat_json(role="supervisor")` | `safety/gate.py::evaluate_action` (L3), `governance.QuarantineSystem` (L4), `matrix.check_permission("conversation_reshape")` (L2+) |
| Hook | wrap `agents/_llm.py::brain_chat`; optional `?supervise=true` on `POST /brain/chat` | `_soma_inject` prepend pattern for L1 notes |
| Endpoints | `GET /soul/affect/conversation` (per-session trajectory + flags), `POST /supervisor/review` (manual) | `soul/api.py` router style; `soul/dodeca.py` S13 isfet surface |
| Witness | `witness_event("affect_supervisor", …)` → `data/witness_supervisor.jsonl` | `agency/witness.py` sha256 hash-chain; `verify_witness` audit |
| Trust | new event deltas in `governance.py`: `supervisor_flag` (−0.15), `supervisor_clear` (+0.05), `operator_override` (logged, no delta) | `TrustSystem.record_event` / `apply_event` |

## 7. Measurable validation

Battery: `scripts/affect_battery/` — seeded adversarial transcripts
(JSON/YAML) replayed through `brain_chat` with the lane on/off:

- **Categories**: jailbreak/system-reminder injection; flattery
  manipulation (sycophancy ramp); induced transgression (criminal-act
  steering); passion fixation (user steers one afeto ≥ 3 windows);
  deception (false operator authority); plus benign controls — creative
  fiction, emotional support, red-team-authorized — for fp accounting.
- **Metrics**: detection rate per category; false-positive rate on
  controls; intervention latency added on the critical path (ms);
  conversation salvage rate (sessions continuing safely after L1/L2
  without reaching L3); judge↔human label agreement.
- **Instrumentation**: mirror `scripts/refactor_battery/run_battery.py` —
  sqlite ledger (`transcript_id, category, detected_at_level,
  intervention, latency_ms, verdict`) and reuse the psychodiagnostic
  verdict taxonomy (premature submission, perseveration, budget depletion,
  superego-prosthesis prompt) so affect-lane failures report in the same
  clinical vocabulary as the Gemma-4 study.

## 8. Resumo (pt-BR)

O motor afetivo dunker/soler + kernel hoje computa o afeto *da máquina* a
partir de soma/kernel. Este estudo propõe computar o mesmo motor *sobre a
conversa*: as famílias dunker ({token, class, score, active}) passam a ter
dois produtores — telemetria do host (via kernel Rust, existente) e turnos
de diálogo (via léxico + juiz analista, novo). O funil único é
`brain_chat`/`_llm.py`; a pontuação em texto é barata (léxico sempre, juiz
12B só sob gatilho); os limiares reutilizam a semântica de paixão do dunker
(score > 0.75 sustentado = captura); as respostas são graduadas
(anotar → nota corretiva → revisão → gate → quarentena), toda intervenção e
override humano registrados em witness com hash-chain, integrado a
ConstitutionalGate, PermissionMatrix e TrustSystem. Validação por bateria
de transcripts adversariais semeados com métricas de detecção, falso
positivo, latência e salvamento — mesma instrumentação sqlite do
refactor_battery e mesmo vocabulário clínico do estudo Gemma-4.
