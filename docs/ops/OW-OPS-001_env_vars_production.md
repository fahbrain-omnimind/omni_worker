# OW-OPS-001 — Variáveis fixas e modo de produção

<!-- doc_id: OW-OPS-001 | title: env vars fixas + bootstrap pós-recriação | author: devin | date: 2026-11-03 | status: operational -->

## 1. Inventário (auditado em 2026-11-03)

Varredura de `os.getenv` em `src/` — 25 variáveis. Classificação:

| Variável | Default em código | Fixa? | Segredo? | Nota |
|---|---|---|---|---|
| `HF_TOKEN` | — | **SIM (fixa)** | **SIM** | modelos gated (Gemma 4 12B/E4B) |
| `OMNI_STATE_DIR` | `data` | fixa (start script) | não | caminho de estado |
| `OMNI_CODE_INDEX_DIR` | fallback repo | fixa (start script) | não | índice FAISS |
| `OMNI_GATE_FAIL_CLOSED` | — (fail-open) | **fixa em produção** | não | `1` = gate fechado |
| `ERIKA_HOST` | `127.0.0.1` | — | não | bind (produção: loopback) |
| `OMNI_API_HOST` | `0.0.0.0` | `127.0.0.1` (escopo public) | não | bind da worker API (`serve --host` sobrescreve) |
| `ERIKA_PORT`/`ERIKA_EXECUTOR_PORT` | `8098`/`8099` | — | não | brains |
| `API_PORT` | `8081` | — | não | worker API |
| `OMNI_SWAP_EVICT/RELOAD/MAX_UNLOADED` | `0.9/0.75/30` | — | não | swap scheduler |
| `OMNI_KERNEL_DAEMON_INTERVAL_S` | `60` | — | não | daemon |
| `OMNI_LOOP_INTERVAL_S`/`TIMEOUT_S` | `60/25` | — | não | integration loop |
| `OMNI_SOMA_INJECT` | `1` | — | não | telemetria |
| `OMNI_ACT_VEC_DIR` | — | — | não | sidecars (default derivado) |
| `OMNI_GATE_DB` | `/tmp/...` | — | não | gate db |
| `OMNI_MODES_STATE`, `OMNI_ORCHESTRATOR_DIR` | `/tmp/...` | — | não | estados voláteis |
| `OMNI_ANALYST_CONFIG`, `OMNI_NODE_ROOT` | — | — | não | opcionais |
| `OMNI_MEMTRIAS_EMBEDDER` | `auto` | — | não | `auto`/`ptbr`/`minilm`/`hash` — auto tenta `colibri-embed-ptbr` (nativo PT-BR, MTEB-BR 0.650) depois MiniLM-L6; hash offline sempre funciona |
| `OMNI_ACERVO_DIR` | — | — | não | dir do acervo vetorizado (read-only, interno) |
| `OMNI_MACHINE_SEED` | — | — | não | semente extra de chassi p/ PhylogeneticSignature |
| `OMNI_V10_BATTERY_PATH` | `vendor/benchmarks/...` | — | não | caminho da bateria V10 (autossuficiente, fallback soberano) |
| `BACKUP_DIR` | `data/backups` | — | não | diretório de backup local (fallback se Drive ausente) |
| `KAGGLE_*`/`COLAB_*` | — | plataforma | — | fornecidas pelo host |

**Conclusão**: apenas `HF_TOKEN` é um segredo obrigatório; `OMNI_GATE_FAIL_CLOSED`
deve ser fixada conforme escopo (produção `1`, laboratório `0`). Todas as demais
têm default seguro em código ou no start script.

## 2. Onde estão fixadas (2026-11-03)

| Plataforma | Variável | Tipo | Valor |
|---|---|---|---|
| GitHub (`fahbrain-omnimind/omni_worker`) | `HF_TOKEN` | Actions secret | token HF (write-only — não legível via API) |
| GitLab (mesmo projeto) | `HF_TOKEN` | CI/CD variable, `masked=true`, `protected=true` | token HF (legível via API c/ token c/ scope api) |

**GitHub é write-only**: secrets não são legíveis de volta — por isso o bootstrap
usa o **GitLab** como fonte primária de restauração.

## 3. Bootstrap pós-recriação de VM

`scripts/restore_env.sh` (só ler, nunca commitado com token):

```bash
source scripts/restore_env.sh public   # ou: domestic
bash scripts/start_omni_worker.sh
```

- Busca variáveis fixas via API do GitLab (token: `GITLAB_TOKEN` env ou
  `/content/gitlab.txt`);
- Restaura `HF_TOKEN` (mascarado), defaults `OMNI_STATE_DIR`/`OMNI_CODE_INDEX_DIR`;
- Escopo `public`: `OMNI_GATE_FAIL_CLOSED=1` + `ERIKA_HOST=127.0.0.1` +
  `OMNI_API_HOST=127.0.0.1` (API loopback; `serve --host`/`OMNI_API_HOST`
  sobrescreve);
- Escopo `domestic`: gate fail-open (laboratório);
- Fail-open: sem token, segue com defaults de código.

## 4. O que NÃO deve existir em produção

- `0.0.0.0` bind sem `HOST`/`CORS_ALLOWED` via env (prática do corpus: security#2);
- `shell=True` com input interpolado (prática security#1);
- `/tmp` world-writable para filas/estado sensível (prática security#4);
- tokens/segredos commitados no repo público (GitHub e GitLab são PUBLIC);
- `OMNI_GATE_FAIL_CLOSED=0` em serviço exposto (gate aberto = fail-open);
- endpoints HTTP vivos sem auth mínimo (prática security#5 — CSRF em loopback).

## 5. Dependências de sistema (bring-up)

| Dep | Quem provê | Fallback |
|---|---|---|
| `cargo`/`rustc` >= 1.85 | `ensure_kernel` instala rustup stable minimal (`OMNI_KERNEL_AUTO_RUSTUP=0` desativa) | kernel Rust opcional — sem ele, `kernel_hooks` usa fallback Python e `/agency/dunker` fica sem `affective_vector_28d` |
| `python3-dev` headers | imagem base (pyo3 precisa de `Python.h`) | idem |
| fontes dos crates | `vendor/kernel/` (vendored, Apache-2.0 — upstream PR#1 merged 2026-11-04) → `OMNI_KERNEL_SRC` → clone público | — |
| `dunker_architecture.py` | `omni_coworker/vendor/` (vendored) → `OMNI_NODE_ROOT` legado | endpoint retorna `status: unavailable` |

## 6. Como criar/alterar (manual, se necessário)

GitHub: `gh secret set HF_TOKEN --repo fahbrain-omnimind/omni_worker`
GitLab: Settings → CI/CD → Variables → key `HF_TOKEN`, masked+protected;
ou API: `POST /projects/omni-group535144%2Fomni_worker/variables`.

---

Nota de proveniência: valores de segredo **nunca** entram em commits, logs ou
mensagens. O inventário acima é [DADO] (varredura do código); as regras de
produção são [DERIVADO] das práticas OW-STU-011 §3.6.
## Security posture — Dependabot dismissals

- **Alert #2 (torch `jit.script` memory corruption, low)** — dismissed
  `not_used` 2026-11-04: zero `torch.jit`/TorchScript call sites in
  `src/` ou `scripts/` (server usa `from_pretrained`+`generate`).
  ⚠️ Se alguém introduzir TorchScript/jit.script no futuro, reabrir a
  avaliação — o vetor passa a ser alcançável.
