# omni_worker — Gemma-4 Developer Agent Competition submission scaffold

Declarative ADK submission (`swegemma` harness). **No Python code** — YAML only.
Verified against `adk_submission-0.2.13` + `swegemma-0.2.11` (competition wheelhouse)
and `HARNESS_README.md` (2026-10-13).

## Design

```
SequentialAgent(omni_pipeline)
├── code_analyst    (LlmAgent, 12B, temp 0.1)  — read-only + code-intel tools → analysis_report
├── patch_executor  (LlmAgent, 12B, temp 0.2)  — edit/write/run → implementation_notes
└── patch_reviewer  (LlmAgent, 12B, temp 0.0)  — tests + sole submit_patch → review_verdict
```

- **Single base**: `gemma-4-12b-it-qat-w4a16-ct` — required by the Single-Model Rule
  (all LlmAgents must share exactly one alias from `ALLOWED_MODEL_NAMES`).
  E4B's premature-submit failure is fatal here; 12B's perseveration is bounded by
  budgets + the 3-nudge mechanism. Chat template is native to the harness.
- **Verification gate**: only `patch_reviewer` holds `submit_patch` — the paper's
  "executive prosthesis" (verify-before-act) enforced *structurally*.
- **Handoffs**: `output_key` → `session.state` templating (`{analysis_report?}`,
  `{implementation_notes?}`).

## Harness contract gotchas (verified in adk_submission-0.2.13 source)

1. **`!include` resolves relative to the INCLUDING file's directory**, sandboxed to
   the submission root — NOT root-relative, and `..` is blocked. Prompts used by
   `sub_agents/*.yaml` therefore live at `sub_agents/prompts/*.md`. A root-level
   `prompts/` dir is only reachable from `agent.yaml` itself.
2. **`{var}` templating raises `KeyError` when the session-state var is absent**
   (`instructions_utils.py` → "Context variable not found"). `hints` only exists
   when `task.hints_text` is non-empty; upstream `output_key`s only exist if the
   upstream agent emitted a final text response. All non-guaranteed vars use the
   optional suffix `{var?}` (renders as empty string).
3. **`config_path` (sub_agents / agent_tool) tries including-file-dir first, then
   root** — `sub_agents/analyst.yaml` from root resolves correctly either way.
4. **A nudge restarts the WHOLE SequentialAgent** — if the Reviewer blocks
   (no `submit_patch`), the harness nudges the root and the full pipeline re-runs
   on the already-edited tree. The Analyst prompt detects this via `git status`/
   `git diff` non-empty and plans a correction instead of the original fix.
5. **Unsubmitted diffs are still scored** — on timeout/budget/3-nudge exhaustion,
   the harness falls back to `git add -N . && git diff HEAD`; a BLOCKED review does
   not prevent the current diff from going to Phase 2 (same binary score).
6. **`git add -N .` before `git diff HEAD`** in the Reviewer — otherwise new
   files created by `write_file` never appear in the diff being inspected.
7. **Scratch files under `/workspace` end up in the patch** — repro scripts go to
   `/tmp` (executor + reviewer prompts enforce this).
8. **Protected files are stripped anyway** (`test_*.py`, `tests/`, `conftest.py`,
   `pytest.ini`, `pyproject.toml`, ...) — but the Reviewer still rejects diffs
   touching them since they signal a wrong approach.
9. **Tool names must match the registry exactly**: `run_command`, `read_file`,
   `write_file`, `edit_file`, `submit_patch`, `get_status`, `get_code_neighbors`,
   `search_similar_code`, `get_code_subgraph` (graph tools return errors when no
   `data/graphs|embeddings/<repo>` files exist — prompts say "when available").
10. **`eval_config.yaml`** maps `evaluation.{max_time_minutes,max_tool_calls,
    max_turns,timeout_seconds}` onto `EvalConfig` — `timeout_seconds` is the
    PER-COMMAND timeout (default 300), not the session wall-clock.
    `verification_timeout_seconds` is fixed at 300 on the scorer.

## Local iteration

```bash
swegemma eval \
  --tasks tasks.jsonl --snapshots-dir snapshots \
  --submission-dir competition/submission \
  --results-dir results/run_01 --sandbox subprocess \
  --task-id <instance_id>  # single task for debugging
```

On a single L4 use `gemma-4-12b-it-qat-w4a16-ct` or `gemma-4-e4b-it-qat-w4a16-ct`
locally (bf16 aliases exist for CLI-only eval); official scoring always uses the
QAT models on 4×L4.

## Variants to try

1. `agent_e4b.yaml` — same pipeline on e4b (faster/cheaper; watch premature-submit
   risk — the gate mitigates).
2. Multi-LoRA: `adapters/analyst_lora/` + `adapters/executor_lora/` on one base
   (rank ≤128, <3GiB total).
3. `LoopAgent` wrapper instead of SequentialAgent for iterative fix cycles within
   one turn (note: a nudge on SequentialAgent already re-runs the whole pipeline;
   LoopAgent iterates sub-agents within a single run_async instead).
4. `include_contents: "none"` on executor/reviewer — drops upstream event
   history (analyst's raw tool transcript) from their context; handoff then
   relies solely on the `{...?}` templated reports. Cuts tokens, loses redundancy.
5. `agent_tool` refactor — wrap the analyst as an AgentTool of the executor
   (`skip_summarization: true`) to isolate exploration context (best practice #4).
