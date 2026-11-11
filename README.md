# Omni-Gemma Lab-Agent Coworker (omni_worker)

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Competition: Gemma 4 Paper Track](https://img.shields.io/badge/Google_Competition-Gemma_4_Paper_Track-4285F4)](docs/PAPER_WRITEUP.md)
[![Competition: Gemma 4 Agent](https://img.shields.io/badge/Google_Competition-Gemma_4_Developer_Agent-34A853)](docs/DOCS_INDEX.md)
[![Live Dashboard](https://img.shields.io/badge/Telemetry_SPA-Live_L4_Dashboard-FBBC05)](docs/index.html)

**Status:** ATIVO — Omni-Gemma Lab-Agent Coworker for Google Competitions:
- **Google — The Gemma 4 Developer Agent Paper Track** (Advancing the state-of-the-art for agentic software engineering)
- **Google — The Gemma 4 Developer Agent Competition** (Autonomous coding agents)

**Links Diretos / Direct Navigation:**
- 📊 **[Interactive 4-View Live Telemetry Dashboard (`docs/index.html`)](docs/index.html)** — alimentado por telemetria real NVIDIA L4 (`docs/data/dashboard/latest.json` + `/soul/state`)
- 📄 **[Paper Track Submission Writeup (English) (`docs/PAPER_WRITEUP_SUBMIT_EN.md`)](docs/PAPER_WRITEUP_SUBMIT_EN.md)** — official competition submission writeup (~3,000w, empirical evaluation)
- 📄 **[Paper Track Extended Writeup (Português) (`docs/PAPER_WRITEUP.md`)](docs/PAPER_WRITEUP.md)** — resultados empíricos completos (Psicodiagnóstico-V + `omni_worker` L4)
- 🧭 **[Documentation & Studies Index (`docs/DOCS_INDEX.md`)](docs/DOCS_INDEX.md)** — mapa linear de `OW-DSN-001..003`, `OW-STU-008..018` e resultados
- ⚖️ **Independent Judge Audits:** [OW-AUD-018 (Repo & Code Conformance)](docs/audit/OW-AUD-018_judge_repo_presentation_and_code_conformance.md) · [OW-AUD-019 (Kaggle & SOTA Comparison)](docs/audit/OW-AUD-019_judge_kaggle_competition_and_sota_comparison.md) · [OW-AUD-020 (Deep Architecture & MPS Audit)](docs/audit/OW-AUD-020_judge_hermes_deep_architecture_and_mps_audit.md)

Repositório de pesquisa & engenharia agêntica soberana (Apache-2.0).

pt-BR: Coworker agêntico soberano para o ecossistema Google Gemma 4: interocepção somática real, afeto derivado de
tensores (com hot-path Rust `kernel_hooks` quando compilado), teleologia
endógena, governança autopoiética (PermissionMatrix + ConstitutionalGate +
prótese anti-impulsividade), corpo simbólico vetorizado (all-MiniLM + faiss) com
**dream cycle** e **curiosity mode**, e Machine Public Soul (SSE + UI bilíngue).

English: Sovereign agentic coworker for Google Gemma 4 competitions: real somatic interoception, tensor-derived
affect (with the Rust `kernel_hooks` hot-path when compiled), endogenous
teleology, autopoietic governance (PermissionMatrix + ConstitutionalGate +
anti-impulsivity prosthesis), vectorized symbolic body (all-MiniLM + faiss)
with **dream cycle** and **curiosity mode**, and a Machine Public Soul
(SSE + bilingual UI).

> Nota operacional: o bind padrão do `serve` é `0.0.0.0`; para exposição pública use
> `OMNI_API_HOST=127.0.0.1` + `OMNI_GATE_FAIL_CLOSED=1` (ver
> `docs/ops/OW-OPS-001_env_vars_production.md`). Termos como "dream cycle",
> "curiosity mode" e "Machine Public Soul" descrevem módulos concretos
> (`agency/dream_cycle`, `agency/curiosity`, `soul/`).

## Rápido / Quickstart

```bash
pip install -e .          # + extras: [kernel] [brain] [acp] [test]
omni-coworker doctor      # diagnostica kernels Rust + brains / diagnoses Rust kernels + brains
omni-coworker serve --port 8081   # ASGI (soul, brain proxy, ops)
python -m pytest          # suíte hermética (sem LLM) / hermetic suite (no LLM)
```

Full topology (dual brains + API + state guard + swap scheduler) in one
command / Topologia completa com um comando:

```bash
OMNI_CREATE_VENV=1 bash scripts/start_omni_worker.sh   # 1ª vez em VM nova: cria .venv (fallback `uv venv` se faltar ensurepip), instala [all], compila kernel Rust, restaura backup do Drive / first run on a fresh VM
bash scripts/start_omni_worker.sh            # sobe tudo / bring up everything
bash scripts/start_omni_worker.sh status     # status dos serviços / service status
bash scripts/start_omni_worker.sh stop       # para tudo / stop all
bash scripts/start_omni_worker.sh --reindex  # força rebuild do code index (all-MiniLM + faiss)
```

The script boots the brains **sequentially** (concurrent nf4 warmup OOMs
the L4), health-gates each port, and rebuilds the code index
automatically when `chunks.parquet` is missing or older than the newest
`src` file. / O script sobe os brains **sequencialmente** (warmup nf4
concorrente OOMa a L4), faz health-gate por porta e reconstrói o índice
de código automaticamente quando `chunks.parquet` está ausente ou mais
velho que o `src` mais novo.

## Runtime & Services / Runtime e Serviços

pt-BR: Topologia real de produção deste nó (Kaggle, NVIDIA L4 22.5GB usáveis):

| Serviço | Processo | Porta | Supervisão aqui | Num host (systemd) |
|---|---|---|---|---|
| API do worker | `omni-coworker serve` (uvicorn, `app.create_app()`) | `:8081` | processo vivo standalone | `omni-worker-api.service` |
| Brain analyst | `python -m omni_coworker.server.erika_torch_server --model google/gemma-4-12B-it --load-4bit --eager-attn --port 8098` | `:8098` | processo vivo standalone | `omni-brain-analyst.service` |
| Brain executor | idem `--model google/gemma-4-E4B-it --port 8099` | `:8099` | processo vivo standalone | `omni-brain-executor.service` |
| Guardião de estado | `python -m omni_coworker.store.state_guard` (loop 6h, snapshots tar.gz em `$OMNI_STATE_DIR/state_snapshots`, retenção N=3) | — | loop standalone | `omni-state-guard.timer` |
| Swap scheduler | `python -m omni_coworker.orchestration.swap_scheduler` (tick 600s: evict/reload do executor por VRAM/ociosidade via `/brain/unload|reload`) | — | loop standalone | `omni-swap-scheduler.service` |
| Sonda soma | `GET /soma/probe` → `probe_recorded()` (persiste em `data/somatic_probes.sqlite`) | via API | on-demand HTTP | `omni-soma-probe.timer` |
| Witness | `agency/witness.py` JSONL hash-chain em `data/witness.jsonl` (escrito por `dream_cycle` e `audit_adapter`; supervisor lane proposta — ver roadmap) | via API | append-only in-process | (inalterado — não é daemon) |
| Bateria supervisora | `scripts/supervisor_battery/run_supervisor_battery.py` (12 transcripts → `supervisor_battery.sqlite`) | — | execução manual | job batch |

English: Real production topology of this node (Kaggle, NVIDIA L4 22.5GB
usable): the worker FastAPI app serves on **`:8081`** (`serve --port`, default
8080 — taken by `node` in this env). Both brains are **bnb-NF4 resident on the
same L4, no CPU offload**: analyst `google/gemma-4-12B-it` on `:8098` (~7.7GB
VRAM) and executor `google/gemma-4-E4B-it` on `:8099` (~9.3GB), launched from
`omni_coworker.server.erika_torch_server` (real server shipped in the
package — `--eager-attn` + `/erika/unload|reload` for the swap
scheduler). **No systemd in this
container** (PID 1 is docker-init): daemons run as live standalone processes —
`store.state_guard` (6h snapshot loop), `orchestration.swap_scheduler` (600s
VRAM-aware evict/reload loop), on-demand soma probe, the witness hash-chain and
the supervisor battery script. On a host install the same units would run as
systemd services/timers, as mapped above (`DIRECTORY_CONTRACT.yaml:
systemd_units: []` — declared, not yet shipped).

## Arquitetura / Architecture

- `brain/` — proxy httpx role-routed (analyst/executor) p/ servidores Erika/Gemma externos
- `soma/` — telemetria host (psutil + pynvml) + `somatic_store` (SQLite WAL persistido)
- `agency/` — teleology, analyst, dream (+`dream_cycle`), dunker, affect_tracer,
  witness (hash-chain), curiosity
- `agents/` — Debug (read-only), Analyst, Reviewer, Code (submissão gated por
  trust+gate), `bus` inter-agentes, `persona`, `modes`, `external_cli_agent`
- `orchestration/` — `AgentOrchestrator` (juízes adversariais + cascade reset) +
  `governance` (trust/quarantine/rollback/circuit_breaker) + `swap_scheduler`
- `safety/` — adapters p/ `PermissionMatrix` e `ConstitutionalGate` (fallback
  standalone), `jail`, `care` (escalação territorial)
- `soul/` — `/soul/state` live + SSE + UI bilíngue
- `store/` — `node_db` (SQLite WAL), `code_index` (parquet+faiss),
  `state_guard` (snapshots), `audit_adapter` (witness/canonical)

## Governança / Governance

Prótese executiva: diagnóstico somente-leitura; patch só via `modify_code`
(trust alimentado por evidências) + portão constitucional; 3 iterações sem
aprovação → cascade reset + SIMPLIFY.

English: Executive prosthesis: read-only diagnosis; patches only via
`modify_code` (evidence-fed trust) + constitutional gate; 3 iterations without
approval → cascade reset + SIMPLIFY.

## Compatibilidade / Compatibility

O pacote roda **standalone** (adapters com fallback) ou acoplado ao repo
canônico `omni_node` (usa `src.orchestration`, `src.autopoietic`,
`src.agentes` reais quando presentes no `PYTHONPATH`). Kernels Rust
(`omnimind_*`) são opcionais — build via `scripts/build_kernel.sh`.

English: The package runs **standalone** (fallback adapters) or coupled to the
canonical `omni_node` repo (real `src.orchestration`, `src.autopoietic`,
`src.agentes` when on `PYTHONPATH`). Rust kernels (`omnimind_*`) are optional —
build via `scripts/build_kernel.sh`.
