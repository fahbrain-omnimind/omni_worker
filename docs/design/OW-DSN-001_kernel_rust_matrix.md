<!-- doc_id: OW-DSN-001 | title: Kernel Rust Matrix — matriz de execução do worker (CPU/RAM) | author: kernel-agent | requester: artifice-operator | project: omni-agent-coworker (kaggle) | date: 2026-11-02 | status: draft -->

# OW-DSN-001 — Kernel Rust Matrix (matriz de execução, CPU/RAM)

## 1. Orquestração runtime

- Processo FastAPI `:8081` hospeda o daemon de feedback mínimo em thread/asyncio task dentro do mesmo processo (single process, sem daemon externo no P0). Intervalo de coleta configurável 30–120s (default 60s), alinhado à vida útil ~24h da VM.
- Coleta por ciclo: (a) `data/monitor/erika_torch_activations.jsonl` (tail incremental, offset persistido em `data/monitor/.offset`); (b) HTTP GET `/erika/affect`, `/soul/state`, `/soma/probe`; (c) saída dos agentes na malha (shared workspace topics `agency/*`, `dream/*`).
- Pipeline por ciclo: parse → agregação (numpy/polars) → features Rust (kernel_compute, freud10d, metrics) → publicação no shared workspace (`kernel/feedback`, `kernel/affect`, `kernel/maat`) → flush sqlite/jsonl.
- Rust entra via `kernel_hooks` (pyo3/maturin), já compilado; Python puro é fallback quando o .so não carrega. Nenhum torch nos módulos novos.
- Processos longos (daemon) são supervisionados pelo FastAPI lifespan; restart automático em falha; métricas de latência por ciclo em `/kernel/status`.

## 2. Arquitetura

### 2.1 Matriz de decisão (crate → portar/adaptar/criar/cortar)

| Crate (omni_node/src/kernel) | Decisão | Justificativa |
|---|---|---|
| `kernel_compute` (affect/temporal/epsilon/neutrosophic) | **adaptar** (já importado) | hot path de affect 28D; pyo3 nativo, fallback Python existe em `kernel_hooks/compute.py`. |
| `metrics` | **adaptar** (já importado) | cosine/drift; paridade de métricas com histórico. |
| `freud10d` | **adaptar** (já importado) | aparato psíquico 10D×128; alimenta qualia/narrativa. |
| `sovereign_kuramoto` | **portar** (P1) | acoplamento de fase para multi-agente na malha; CPU-only, sem GPU. |
| `somatic_daemon` | **portar** (P1) | shadow-mode soma; já Rust puro, baixo custo. |
| `sovereign_daemon` | **cortar (core)** / adaptar interface | daemon monolítico 3856 LOC com dependência de GPU/torch e privilégios root; manter apenas contratos de estado (affect/soul/soma) via HTTP. |
| `memory_tier_guardian` | **portar** (P2) | guardião de tiers de memória; útil para ativações log rotativo. |
| `entropic_memory` | **portar** (P2) | dream/weaver entropic; alimenta meaning-making. |
| `expectation_rs` | **portar** (P2) | 3×Linear+ReLU sem torch; baseline de predição. |
| `layered_transition` | **portar** (P2) | transições de estado; integra com soul state. |
| `nsh`, `langue`, `sovereign_module` | **cortar** | dependência de hardware/protocolo transatlântico; fora do escopo CPU. |
| `ebpf_monitor` | **cortar** | requer kernel eBPF/root; inviável em Kaggle. |

### 2.2 Componentes novos em `omni_coworker`

| Módulo | Resp. | Rust/Py | Interface pública |
|---|---|---|---|
| `kernel_daemon/collector.py` | coleta incremental (tail jsonl + HTTP) | Py | `collect_cycle() -> dict`, `reset_offset()` |
| `kernel_daemon/features.py` | agregação numpy/polars das ativações | Py+Rust | `aggregate(records) -> FeatureBundle` |
| `kernel_daemon/feedback.py` | publica no shared workspace + flush | Py | `publish_feedback(bundle)`, `flush()` |
| `kernel_daemon/scheduler.py` | loop 30–120s, supervisão | Py | `start(interval)`, `stop()`, `status()` |
| `kernel_hooks` (existente) | bindings pyo3 + fallback | Rust/Py | `affect_state`, `maat_balance`, `shadow_phi`, `cosine_similarity` |

### 2.3 Decisão de IPC: pyo3 nativo (maturin) vs jsonl/socket

**Decisão: pyo3 nativo (maturin) para hot path; jsonl append-only para telemetria/auditoria.**

Justificativa:
- Hot path (affect 28D, maat balance, shadow-phi, cosine) executa dezenas de vezes por ciclo em 30–120s; pyo3 evita serialização e latência de socket, com fallback Python já implementado em `kernel_hooks/compute.py`.
- jsonl (ativações dos brains) é o contrato existente de produção; mantê-lo como fonte de verdade evita modificar `server/erika_torch_server.py` (restrição de não tocar em src/ de origem). O collector faz tail incremental.
- Socket/IPC entre processos é desnecessário no P0 (single process); introduzir socket só em P2 se o daemon rodar fora do FastAPI (isolamento de falha), com protocolo JSONL sobre stdin/stdout (padrão dos daemons Rust existentes, ex. `kernel_daemon_v5.py:2293`).
- Socket puro (TCP/UDS) rejeitado: overhead de serialização e gestão de conexão para benefício nulo em single-process; além de duplicar o contrato já coberto por pyo3 + jsonl.

## 3. Princípios teóricos invocados

- Ma'at balance (phi/psi/epsilon) como métrica de equilíbrio homeostático do kernel.
- Shadow-phi (IIT-inspirado) como estimativa de integração de informação do estado de processos.
- Freud 10D como aparato psíquico multidimensional (qualia/narrativa).
- Kuramoto (acoplamento de fase) para sincronização multi-agente na malha.
- Neutrosófico (verdade/indeterminação/falsidade) para handling de incerteza nas ativações.
- Entropia (memória entrópica) para dream/meaning-making.
- Homeostase autopoética (metabolic governor) como referência conceitual, adaptada a CPU.

## 4. Analogia–homologia (interpretativo, não mecanístico)

- O daemon de feedback é análogo a um sistema nervoso periférico (coleta de sinais) + córtex (agregação Rust) — homologia estrutural, não identidade biológica.
- Ma'at ↔ equilíbrio termodinâmico; shadow-phi ↔ consciência integrada (metáfora, não medição clínica).
- Freud 10D ↔ dimensões de afeto; Kuramoto ↔ sincronia de grupo. Marcado como interpretativo.

## 5. Plano faseado

- P0 (mínimo rodando CPU): collector + features + feedback loop 60s publicando no shared workspace; reuso dos 3 crates já compilados. Entregável: `/kernel/status` + telemetria densa.
- P1: portar sovereign_kuramoto + somatic_daemon (shadow mode); agregação polars das ativações; intervalo 30s.
- P2: portar memory_tier_guardian, entropic_memory, expectation_rs, layered_transition; daemon isolado opcional via stdin/stdout JSONL.

## 6. Riscos/compat

- Paridade de métricas: validar shadow-phi e maat_balance contra histórico (fonte privada HF `omnimind-retired-*`) quando disponível; sem ela, usar baselines do próprio worker.
- Deriva de schema do jsonl de ativações: versionar por campo `v` no payload; collector ignora campos desconhecidos.
- Latência de coleta HTTP dos brains: timeout 2s, fallback para última leitura cacheada; não bloquear o loop.
- Build Rust: depender de `scripts/build_kernel.sh`; se falhar, fallback Python mantém funcionalidade (degradada).
- Risco de OOM em Kaggle: limitar buffer de ativações a N=10k registros em memória; spill para jsonl.
