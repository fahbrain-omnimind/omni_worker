# omni-agent-coworker (src/omni_coworker)

## Status

ATIVO — pacote novo (Kaggle Gemma 4, Best New Application). Malha viva validada
na L4. / ACTIVE — new package; live mesh validated on the L4.

## Descrição / Description

pt-BR: Coworker agêntico com interocepção somática real, afeto derivado de
tensores, teleologia endógena, governança autopoiética e Machine Public Soul.
Processo ASGI único; roteamento por role entre dois modelos Gemma coabitando a
GPU:

- `analyst`  → `google/gemma-4-12B-it`  (`:8098`, decomposição/clínica/juízes)
- `executor` → `google/gemma-4-E4B-it`  (`:8099`, tool-calling tático)

Corpo simbólico vetorizado (all-MiniLM-L6-v2 + faiss) alimenta `dream_cycle`
(sonho sobre o próprio código) e `curiosity.explore` (busca correlata).

English: Agentic coworker with real somatic interoception, tensor-derived
affect, endogenous teleology, autopoietic governance and a Machine Public
Soul. Single ASGI process; role routing between two Gemma models sharing
the GPU (same table above). The vectorized symbolic body
(all-MiniLM-L6-v2 + faiss) feeds `dream_cycle` (dreaming over its own
code) and `curiosity.explore` (correlated search).

## Runtime & Services / Runtime e Serviços

pt-BR: `create_app()` sobe via `omni-coworker serve --port 8081` (8080 ocupada
pelo `node` neste ambiente; default argparse = 8080). Os dois brains rodam
**NF4-residentes na mesma NVIDIA L4, sem CPU offload** (`--load-4bit
--eager-attn` no `erika_torch_server` canônico do omni_node) — fora deste
pacote, alcançados via `brain/` proxy. Container sem systemd: os loops
auxiliares rodam standalone — `store.state_guard` (snapshots 6h),
`orchestration.swap_scheduler` (600s), sonda soma via `GET /soma/probe`,
witness JSONL e `scripts/supervisor_battery`. Num host com systemd seriam
units/timer (ver README raiz, tabela Runtime).

English: `create_app()` is served via `omni-coworker serve --port 8081`
(8080 is taken by `node` in this env; argparse default = 8080). Both brains
run **NF4-resident on the same NVIDIA L4, no CPU offload** (canonical
omni_node `erika_torch_server --load-4bit --eager-attn`) — external to this
package, reached through the `brain/` proxy. No systemd in this container:
auxiliary loops run standalone — `store.state_guard` (6h snapshots),
`orchestration.swap_scheduler` (600s), soma probe via `GET /soma/probe`,
the witness JSONL and `scripts/supervisor_battery`. On a systemd host they
would be services/timers (see root README, Runtime table).

## Arquivos / Files

| Módulo | Papel / Role |
|---|---|
| `app.py` | `create_app()` — monta soul + brain routers + ops (`/soma/probe`, `/agency/missions`, `/agency/dunker`, `/agency/witness`, `/safety/check`, `/safety/care`, `/dream/cycle`, `/curiosity/explore`, `/kernel/status`) |
| `cli.py` | `serve`, `doctor`, `demo`, `soul-export`, `missions` (entrypoint `omni-coworker`) |
| `brain/` | proxy httpx role-routed p/ erika_torch_server (`/brain/*` incl. `unload`/`reload`); affect derivation |
| `soma/probe.py` | telemetria host (psutil): cpu/ram/swap/load + gpu (pynvml/nvidia-smi) + virt |
| `agency/` | teleology, analyst, dream(+dream_cycle), dunker, affect_tracer, witness, curiosity |
| `agents/` | DebugAgent (write-lock), AnalystAgent, ReviewerAgent, CodeAgent (submit gated) |
| `orchestration/` | AgentOrchestrator — juízes adversariais + cascade reset + artifacts no node.db; `swap_scheduler` (evict/reload por VRAM) |
| `safety/` | matrix (PermissionMatrix), gate (ConstitutionalGate, `OMNI_GATE_FAIL_CLOSED`), jail, care (territorial) |
| `soul/` | `/soul/state` live (kernel Rust 28d + soma + brain) + `/soul/dodeca` + SSE + UI bilíngue |
| `store/` | node_db (SQLite WAL: missions + artifacts), code_index (parquet+faiss), state_guard (snapshots tar.gz), audit_adapter |
| `kernel_hooks/` | bindings Rust: kernel_compute, freud10d, metrics (fallback Python) |
| `server/` | stub leve do erika_torch_server (pacote mínimo) |

## Dependências / Dependencies

- **Importa de / Imports from**: `src.erika` (via HTTP), `src.orchestration`,
  `src.autopoietic`, `src.agentes`, `src.cognitive`, módulos Rust `omnimind_*`
- **Importado por / Imported by**: `tests/`, CLI `omni-coworker`
- **Python**: fastapi, uvicorn, httpx, psutil, sqlite3, sentence-transformers,
  faiss-cpu (opt), pandas/pyarrow (opt)

## Governança / Governance

Prótese executiva: diagnóstico read-only; submissão de patch apenas via
`modify_code` (trust≥0.8 por testes passando) + ConstitutionalGate; 3 iterações
sem aprovação disparam cascade_reset + SIMPLIFY.

English: Executive prosthesis: read-only diagnosis; patch submission only via
`modify_code` (trust≥0.8 earned by passing tests) + ConstitutionalGate; 3
iterations without approval trigger cascade_reset + SIMPLIFY.
