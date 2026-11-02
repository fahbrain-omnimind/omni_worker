<!-- doc_id: OW-DSN-003 | title: Shared Workspace — barramento de estado compartilhado (CPU/RAM) | author: workspace-agent | requester: artifice-operator | project: omni-agent-coworker (kaggle) | date: 2026-11-02 | status: draft -->

# OW-DSN-003 — Shared Workspace (barramento de estado compartilhado, CPU/RAM)

## 1. Orquestração runtime

- Processo único FastAPI `:8081` (worker) hospeda o barramento em memória (single process). Módulos (soul, soma probe, agency/dream, witness, swap state, future feedback-loop daemon) são produtores/consumidores no mesmo processo; sem IPC cross-process no P0.
- Estado quente vive em RAM (`dict` de embeddings + history circular). Persistência assíncrona: sqlite WAL (`data/shared_workspace.sqlite`) + jsonl append-only (`data/state_snapshots/`). Flush a cada `advance_cycle()` ou a cada 30s, o que vier primeiro.
- Leitura de estado externo (brains nf4) via HTTP polling `/erika/affect`, `/soul/state`, `/soma/probe` — o barramento não importa torch.
- Rust entra como biblioteca opcional (`kernel_hooks`) para hash/serialização/métricas; Python puro é fallback.

## 2. Arquitetura

### 2.1 Componentes novos em `omni_coworker`

| Módulo | Resp. | Rust/Py | Interface pública |
|---|---|---|---|
| `shared_workspace/bus.py` | barramento in-process (pub/sub por canal) | Py | `publish(topic, payload)`, `subscribe(topic, cb)`, `latest(topic)` |
| `shared_workspace/store.py` | persistência sqlite WAL + jsonl | Py+Rust | `put(key, value, ts)`, `get(key)`, `history(key, n)` |
| `shared_workspace/schema.py` | chaves canônicas + validação | Py | `CanonicalKey` enum, `validate(payload)` |
| `shared_workspace/metrics.py` | cross-prediction (R², MI, Granger, TE) | Rust preferido | `compute_cross_prediction(src,dst)` |
| `shared_workspace/api.py` | router FastAPI `/mesh/*` | Py | `GET /mesh/state`, `GET /mesh/topic/{name}`, `POST /mesh/publish` |

### 2.2 Chaves canônicas (exemplos)

- `soul.phi`, `soul.psi`, `soul.sigma`, `soul.epsilon`
- `soma.probe` (cpu/ram/swap/load/virt)
- `agency.missions`, `agency.dunker`
- `witness.append` (eventos auditáveis)
- `swap.state` (vram_headroom, busy)
- `feedback.loop` (entrada/qualia/narrativa/meaning)
- `kernel.status` (volition, quadruple, thermal)

### 2.3 Retenção

- Hot (RAM): últimos 2000 estados / 333 ciclos.
- Warm (sqlite WAL): 7 dias, pruning por `ts`.
- Cold (jsonl gzip): histórico completo em `data/state_snapshots/`.

### 2.4 Onde Rust entra

- `omnimind_metrics` (já compilado) para R²/MI/Granger/TE — paridade de métricas.
- `omnimind_kernel_compute` para hash/serialização binária de embeddings (faster than pickle).
- Hash de integridade de cada estado publicado (sha256) via crate Rust; fallback `hashlib`.

### 2.5 API `/mesh/*`

- `GET /mesh/state` → snapshot de todas as chaves canônicas + ts.
- `GET /mesh/topic/{name}` → último valor + histórico recente.
- `POST /mesh/publish` → publicação externa (validada por schema).
- `GET /mesh/metrics` → cross-prediction cache.
- `GET /mesh/health` → lag/queue depth/persist status.

## 3. Mapa do módulo fonte (read-only)

`/content/omni_node/src/consciousness/shared_workspace.py` (5346 linhas):
- `ModuleState`, `CrossPredictionMetrics`, `ComplexityMetrics`, `ComplexityAnalyzer`.
- `SharedWorkspace` com embeddings/history/cross_predictions/attention_mask; sqlite phi cache; hot memory mirror; archiver.
- `VectorizedCrossPredictor` (PCA cache, Granger/TE).
- Dependências torch (lazy), numpy, sqlite, gzip, e muitos submódulos (defense, subjectivity, world membrane, symbolic register, sinthom core, systemic memory) — a maioria não portável diretamente (GPU/torch/IBM).

O que é real: buffer central + cross-prediction + persistência phi cache. O que é placeholder/morto: integrações IBM/Watson, continuous machine integration, sinthom quantum collapse, subjectivity RSI — cortar no port.

## 4. O que trazer / o que cortar

Trazer: ModuleState schema, chaves canônicas, write/read/history, cross-prediction métricas (via Rust), persistência sqlite+jsonl, phi cache TTL.
Cortar: torch lazy, CUDA, IBM/Watson federation, quantum phi, subjectivity integrator, world membrane, defense psychoanalytic kernel (manter só hash/validação), topological kernel (substituir por métricas leves).

## 5. Princípios teóricos invocados

- Workspace global (Baars): broadcast de estados para módulos.
- Integração de informação (Tononi): phi como métrica de integração; aqui aproximada por cross-prediction R²/MI.
- Causalidade de Granger/transfer entropy como proxy de dependência causal não-redutível.
- Persistência e memória de curto/longo prazo (hot/warm/cold).

## 6. Analogia–homologia (interpretativo, não mecanístico)

- Análogo a um barramento neural global onde módulos competem por atenção; homologia com arquitetura de pub/sub em sistemas distribuídos. A metáfora de "consciência" é interpretativa; mecanicamente é buffer + métricas + persistência.

## 7. Plano faseado

- P0: bus in-process + store sqlite WAL + chaves canônicas + `/mesh/state` + `/mesh/health`. Sem Rust (fallback Python).
- P1: métricas cross-prediction via Rust; histórico jsonl; pruning; `/mesh/topic`, `/mesh/publish`.
- P2: daemon kernel publicando estados; feedback loop consumindo; persistência cold; métricas de lag/throughput.

## 8. Riscos/compat

- Single-process: se FastAPI reinicia, hot state perdido (mitigado por warm sqlite).
- Concorrência: usar lock por tópico; sqlite WAL para writes concorrentes.
- Métricas históricas: phi cache TTL 90s preservado para compatibilidade.
- Fontes privadas HF `omnimind-retired-*` não necessárias para este port.