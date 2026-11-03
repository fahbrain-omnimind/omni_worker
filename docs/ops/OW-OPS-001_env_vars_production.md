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
- Escopo `public`: `OMNI_GATE_FAIL_CLOSED=1` + `ERIKA_HOST=127.0.0.1`;
- Escopo `domestic`: gate fail-open (laboratório);
- Fail-open: sem token, segue com defaults de código.

## 4. O que NÃO deve existir em produção

- `0.0.0.0` bind sem `HOST`/`CORS_ALLOWED` via env (prática do corpus: security#2);
- `shell=True` com input interpolado (prática security#1);
- `/tmp` world-writable para filas/estado sensível (prática security#4);
- tokens/segredos commitados no repo público (GitHub e GitLab são PUBLIC);
- `OMNI_GATE_FAIL_CLOSED=0` em serviço exposto (gate aberto = fail-open);
- endpoints HTTP vivos sem auth mínimo (prática security#5 — CSRF em loopback).

## 5. Como criar/alterar (manual, se necessário)

GitHub: `gh secret set HF_TOKEN --repo fahbrain-omnimind/omni_worker`
GitLab: Settings → CI/CD → Variables → key `HF_TOKEN`, masked+protected;
ou API: `POST /projects/fahbrain-omnimind%2Fomni_worker/variables`.

---

Nota de proveniência: valores de segredo **nunca** entram em commits, logs ou
mensagens. O inventário acima é [DADO] (varredura do código); as regras de
produção são [DERIVADO] das práticas OW-STU-011 §3.6.