# omni-agent-coworker (src/omni_coworker)

## Status
ATIVO — pacote novo (Kaggle Gemma 4, Best New Application). Malha viva validada na L4.

## Descrição

Coworker agêntico com interocepção somática real, afeto derivado de tensores,
teleologia endógena, governança autopoiética e Machine Public Soul. Processo
ASGI único; roteamento por role entre dois modelos Gemma coabitando a GPU:

- `analyst`  → `google/gemma-4-12B-it`  (`:8098`, decomposição/clínica/juízes)
- `executor` → `google/gemma-4-E4B-it`  (`:8099`, tool-calling tático)

Corpo simbólico vetorizado (all-MiniLM-L6-v2 + faiss) alimenta `dream_cycle`
(sonho sobre o próprio código) e `curiosity.explore` (busca correlata).

## Arquivos / Planos

| Módulo | Papel |
|---|---|
| `app.py` | create_app() — monta soul + brain + ops (`/soma/probe`, `/agency/missions`, `/safety/check`, `/dream/cycle`, `/curiosity/explore`, `/kernel/status`) |
| `cli.py` | `serve`, `doctor`, `demo`, `soul-export`, `missions` |
| `brain/` | proxy httpx role-routed p/ erika_torch_server; affect derivation |
| `soma/probe.py` | telemetria host (psutil): cpu/ram/swap/load |
| `agency/` | teleology, analyst, dream(+dream_cycle), witness, curiosity |
| `agents/` | DebugAgent (write-lock), AnalystAgent, ReviewerAgent, CodeAgent (submit gated) |
| `orchestration/` | AgentOrchestrator — juízes adversariais + cascade reset + artifacts no node.db |
| `safety/` | matrix (PermissionMatrix), gate (ConstitutionalGate), jail |
| `soul/` | `/soul/state` live (kernel Rust 28d + soma + brain) + SSE + UI bilíngue |
| `store/` | node_db (SQLite WAL: missions + artifacts), code_index (parquet+faiss) |
| `kernel_hooks/` | bindings Rust: kernel_compute, freud10d, metrics (fallback Python) |
| `server/` | stub leve do erika_torch_server (pacote mínimo) |

## Dependências

- **Importa de**: `src.erika` (via HTTP), `src.orchestration`, `src.autopoietic`,
  `src.agentes`, `src.cognitive`, módulos Rust `omnimind_*`
- **Importado por**: `tests/omni_coworker`, CLI `omni-coworker`
- **Python**: fastapi, uvicorn, httpx, psutil, sqlite3, sentence-transformers,
  faiss-cpu (opt), pandas/pyarrow (opt)

## Governança

Prótese executiva: diagnóstico read-only; submissão de patch apenas via
`modify_code` (trust≥0.8 por testes passando) + ConstitutionalGate; 3 iterações
sem aprovação disparam cascade_reset + SIMPLIFY.
