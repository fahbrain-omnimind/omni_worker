# omni-agent-coworker (omni_worker)

**Status:** ATIVO — pacote standalone (Kaggle Gemma 4, Best New Application). Repositório privado; publicação futura Apache-2.0.

Coworker agêntico soberano: interocepção somática real, afeto derivado de tensores
(com hot-path Rust `kernel_hooks` quando compilado), teleologia endógena, governança
autopoiética (PermissionMatrix + ConstitutionalGate + prótese anti-impulsividade),
corpo simbólico vetorizado (all-MiniLM + faiss) com **dream cycle** e **curiosity mode**,
e Machine Public Soul (SSE + UI bilíngue).

## Rápido

```bash
pip install -e .          # + extras: [kernel] [brain]
omni-coworker doctor      # diagnostica kernels Rust + brains
omni-coworker serve       # ASGI em :8080 (soul, brain proxy, ops)
python -m pytest          # suíte hermética (sem LLM)
```

## Arquitetura

- `brain/` — proxy httpx role-routed (analyst/executor) p/ servidores Erika/Gemma externos
- `soma/` — telemetria host (psutil) + `somatic_store` (SQLite WAL persistido)
- `agency/` — teleology, analyst, dream (+`dream_cycle`), witness (hash-chain), curiosity
- `agents/` — Debug (read-only), Analyst, Reviewer, Code (submissão gated por trust+gate), `bus` inter-agentes, `persona`
- `orchestration/` — `AgentOrchestrator` (juízes adversariais + cascade reset) + `governance` (trust/quarantine/rollback/circuit_breaker)
- `safety/` — adapters p/ `PermissionMatrix` e `ConstitutionalGate` (fallback standalone)
- `soul/` — `/soul/state` live + SSE + UI bilíngue
- `store/` — `node_db` (SQLite WAL), `code_index` (parquet+faiss)

## Governança

Prótese executiva: diagnóstico somente-leitura; patch só via `modify_code`
(trust alimentado por evidências) + portão constitucional; 3 iterações sem
aprovação → cascade reset + SIMPLIFY.

## Compatibilidade

O pacote roda **standalone** (adapters com fallback) ou acoplado ao repo canônico
`omni_node` (usa `src.orchestration`, `src.autopoietic`, `src.agentes` reais quando
presentes no `PYTHONPATH`). Kernels Rust (`omnimind_*`) são opcionais via pip.
