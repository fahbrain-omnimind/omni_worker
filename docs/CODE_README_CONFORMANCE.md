<!-- doc_id: OW-OPS-003 | title: Code ↔ README Conformance Study — omni_worker (2026-11-02) | author: devin | requester: artifice-operator | project: omni-agent-coworker (kaggle) | date: 2026-11-02 | status: active -->

# Code ↔ README Conformance Study — omni_worker

pt-BR: Estudo de conformidade entre os 12 READMEs do repo e o código
(rotas FastAPI, APIs públicas, env vars, flags CLI, contratos de
adapter). Toda afirmação documental foi conferida contra
`src/omni_coworker/**` em 2026-11-02; esta rodada reescreveu todos os
READMEs bilíngues (pt-BR primário) e corrigiu as divergências abaixo.

English: Conformance study between the repo's 12 READMEs and the code
(FastAPI routes, public APIs, env vars, CLI flags, adapter contracts).
Every documentary claim was checked against `src/omni_coworker/**` on
2026-11-02; this pass rewrote all READMEs bilingual (pt-BR primary) and
fixed the divergences below.

## 1. Divergências encontradas e corrigidas / Discrepancies found & fixed

| # | README | Afirmação anterior | Código real | Fix |
|---|---|---|---|---|
| 1 | `soma/README.md` | `GET /soma/probe → probe_with_brain()` | `app.py:34-38` chama `probe_recorded()` | corrigido |
| 2 | `src/omni_coworker/README.md` | lista de ops omitia rotas | `app.py` expõe também `/safety/care` (:60), `/agency/dunker` (:89), `/agency/witness` (:102) | rotas listadas |
| 3 | `brain/README.md` | endpoints sem swap | `server.py:45-65` define `POST /brain/unload|reload` | adicionados |
| 4 | `safety/README.md` | `care.py` ausente; só `no_gate` fail-open | `gate.py:55-57` lê `OMNI_GATE_FAIL_CLOSED`; `care.py::escalate` existe e serve `/safety/care` | arquivo + env documentados |
| 5 | `agency/README.md` | `dunker.py` e `affect_tracer.py` ausentes | ambos existem; dunker servido em `/agency/dunker` | tabela atualizada |
| 6 | `store/README.md` | `state_guard.py` e `audit_adapter.py` ausentes | ambos existem (`__main__` no state_guard) | tabela + seções novas |
| 7 | `orchestration/README.md` | `swap_scheduler.py` ausente | `swap_scheduler.py:47-112` (tick/loop/`__main__`) | seção nova |
| 8 | `README.md` raiz | `serve` "ASGI em :8080" | deploy real `--port 8081` (8080 tomada por `node` — `docs/KAGGLE_SETUP_VALIDATION.md:103`); default argparse 8080 (`cli.py:172`) | runtime doc + quickstart |
| 9 | `soma/README.md` | `probe()` sem `gpu`/`virt` | `probe.py:182-183` retorna ambos sempre | assinatura corrigida |
| 10 | `store/README.md` (nova seção) | — | `audit_adapter.py:43-49` `audit_verify()` só verifica a witness local, não a cadeia canônica | comportamento real descrito |
| 11 | todos | EN-only ou EN-primeiro | política: pt-BR primário, English segundo | 12 arquivos reescritos |

## 2. Lacunas de cobertura / Coverage gaps

- `DIRECTORY_CONTRACT.yaml` desatualizado: `modules.total: 40` vs **49**
  arquivos reais; `stubs_and_shims` omite `agency/dunker.py` (adapter real,
  confirmado por `dunker.py:1-19`); `with_main` omite `swap_scheduler.py:105`
  e `state_guard.py:131` (ambos com `__main__`); `systemd_units: []` — units
  declaradas no README raiz mas não entregues.
- `scripts/` sem README próprio: `build_kernel.sh`, `guard_sanitize.py`,
  `refactor_battery/run_battery.py`, `supervisor_battery/run_supervisor_battery.py`.
- `tests/` (suite hermética, `pytest.ini_options.testpaths`) não tem mapa —
  só menções dispersas.
- `agency/affect_tracer`, `agency/dunker`, `orchestration/swap_scheduler`,
  `store/state_guard`, `store/audit_adapter`, `safety/care` não são
  re-exportados nos `__init__.py` — importáveis como submódulos (documentado).
- `soul/dodeca.py` casas S05/S06/S08/S09/S14/S15 → `unavailable_standalone`
  (`dodeca.py:44`): exigem superfícies canônicas ausentes neste pacote.
- `POST /brain/unload|reload` inútil contra o stub upstream — o stub
  (`server/erika_torch_server.py`) não implementa `/erika/unload|reload`;
  erro upstream vira `{"status": "error"}` (documentado).
- Endpoints propostos e ainda inexistentes: `/gate/pending`, `/gate/decide`,
  `/supervisor/review`, `/soul/affect/conversation`
  (`docs/audits/AUDIT_CLINE.md:79`, `CONVERSATIONAL_AFFECT_STUDY.md:140`).

## 3. Oportunidades de evolução / Evolution opportunities

Loop de continuidade/supervisão (o que falta para fechar o ciclo):

1. **Snapshots não cobrem o node.db** — `state_guard.py:29` ancora em
   `OMNI_STATE_DIR` (default `data/`), mas o orchestrator persiste artefatos
   em `OMNI_ORCHESTRATOR_DIR` (default `/tmp/omni_coworker_orch`,
   `agent_orchestrator.py:19`) → fora do snapshot. Alinhar defaults ou
   adicionar paths extras ao manifest.
2. **Busy detection do swap é monotônica** — `swap_scheduler.py:41-43`
   testa `activations_buffered > 0`, contador cumulativo no deque: após o
   primeiro uso o executor fica "ativo" para sempre → evict nunca dispara.
   Comparar delta entre checks ou usar timestamp da última activation.
3. **Witness fora do state root** — `app.py:107` hardcodeia
   `data/witness.jsonl`; `witness.py:96` default idem. Sob `OMNI_STATE_DIR`
   custom, a cadeia fica fora dos snapshots do state_guard.
4. **`_manifest_hash` trunca arquivos** — `state_guard.py:47` lê só 1MB por
   arquivo: mudanças após o primeiro MB (sqlite grandes) não alteram o hash
   → snapshots podados erram "nada mudou".
5. **Falha de gate é permanente** — `gate.py:39-41`: `_GATE_FAILED` jamais
   reseta; um init ruim desliga o gate pelo resto do processo.
6. **Mount do brain router engole erro** — `app.py:29-32` `except: pass`
   esconde falha de montagem; logar motivo.
7. **Sonda soma só on-demand** — `probe_recorded` roda apenas via HTTP
   (`app.py:34-38`); sem job periódico, `somatic_probes.sqlite` fica
   esparsa — o "soma probe timer" da tabela Runtime não existe como loop.
8. **Supervisor lane desconectado** — `affect_tracer` scoreia L0-L4 mas
   nada o chama no caminho de `/brain/chat` (`server.py:94-103` passa
   direto); wire P2 do roadmap.
9. **ACP/shell base env hardcoded** — `external_cli_agent.py:52`
   `OPENAI_BASE_URL=http://127.0.0.1:8098` ignora `ERIKA_PORT`.
10. **`cpu_percent(interval=0.0)`** — `probe.py:177` retorna 0.0 na primeira
    chamada do processo (semântica psutil); telemetria do primeiro hit é
    fria.

Refinamentos menores: `cli.py:14` sem flag `--host` (fixa `0.0.0.0`);
`state_guard.py:25` `N_SNAPSHOTS=3` hardcoded; `audit_adapter.py:20-28`
refaz `sys.path.insert` + scan de bases a cada chamada; `agents/modes.py`
persiste mode em `/tmp` (volátil) — candidatos a env/const.

## 4. Superfície API/contrato / API & contract surface

App única `create_app()` (`app.py:17`), deploy `:8081`.

**soma / agency / safety / kernel (rotas diretas em `app.py`)**

| Route | Método | Handler real |
|---|---|---|
| `/soma/probe` | GET | `soma.probe.probe_recorded()` — persiste sqlite |
| `/agency/missions` | GET | `teleology.generate_missions` + `compute_omega_teleology` |
| `/agency/dunker` | GET | `dunker.dunker_architecture(kernel_state?)` |
| `/agency/witness` | GET | `read_witness` + `verify_witness` em `data/witness.jsonl` |
| `/safety/check?action=` | GET | `matrix.check_permission` + `gate.evaluate_action` |
| `/safety/care?reason=&state_uf=&age=` | GET | `care.escalate` → `{level, resources, referral_text}` |
| `/dream/cycle` | POST | `agency.dream.dream_cycle()` |
| `/curiosity/explore?topic=&k=` | GET | `agency.curiosity.explore` |
| `/kernel/status` | GET | `kernel_hooks.compute.kernel_status` |

**soul router (`soul/api.py`, prefixo `/soul`)**

| Route | Método | Conteúdo |
|---|---|---|
| `/soul/state` | GET | `{phi,psi,sigma,epsilon,kernel,soma,brain,dodeca}` |
| `/soul/dodeca` | GET | casas S01–S15 com value/source/formula |
| `/soul/stream` | GET | SSE 2.0s (sse-starlette → StreamingResponse fallback) |
| `/soul/` | GET | UI HTML bilíngue |
| `/soul/static/{path}` | GET | assets (i18n json, index.html) |

**brain router (`brain/server.py`, prefixo `/brain`)**

| Route | Método | Upstream |
|---|---|---|
| `/brain/health` | GET | analyst `/health` |
| `/brain/activations?limit=` | GET | analyst `/erika/activations` |
| `/brain/affect` | GET | analyst `/erika/affect` |
| `/brain/executor/health` | GET | executor `/health` |
| `/brain/topology` | GET | ambos roles up/down |
| `/brain/chat?role=` | POST | role-routed `/v1/chat/completions` |
| `/brain/unload?role=` | POST | role-routed `/erika/unload` (default executor) |
| `/brain/reload?role=` | POST | role-routed `/erika/reload` (default executor) |

**stub `server/erika_torch_server.py`** (superfície mínima):
`GET /health`, `GET /erika/activations`, `GET /erika/affect`,
`POST /v1/chat/completions`, `POST /v1/completions` (503 sem `_MODEL`).
Sem `/erika/unload|reload`.

**CLI (`cli.py`)**: `serve [--port]`, `doctor`, `demo [--task]`,
`soul-export [--out]`, `missions`. **__main__ auxiliares**:
`swap_scheduler [--interval-s|--once]`, `state_guard
[--once|--interval-hours|--restore]`, `agent_orchestrator`, stub server.

**Env vars lidas no código** (todas): `ERIKA_HOST/PORT`,
`ERIKA_EXECUTOR_PORT`, `ERIKA_ACTIVATIONS_LOG`, `OMNI_STATE_DIR`,
`OMNI_CODE_INDEX_DIR`, `OMNI_ORCHESTRATOR_DIR`, `OMNI_GATE_DB`,
`OMNI_GATE_FAIL_CLOSED`, `OMNI_SOMA_INJECT`, `OMNI_SWAP_EVICT_THRESHOLD`,
`OMNI_SWAP_RELOAD_THRESHOLD`, `OMNI_SWAP_MAX_UNLOADED_MIN`,
`OMNI_ANALYST_CONFIG`, `OMNI_NODE_ROOT`, `OMNI_AGENTS_CONFIG_DIR`,
`OMNI_MODES_STATE`, `OMNI_EXTERNAL_CLI_WORKDIR`, `OMNI_CLI_<NAME>`,
`KAGGLE_*`/`COLAB_*` (virt probe), `OMNI_KERNEL_SRC/OMNI_KERNEL_CRATES`
(build_kernel.sh).

## English summary

All 12 READMEs were rewritten bilingual (pt-BR first) and corrected: 11
concrete discrepancies fixed (stale route lists, wrong function names,
missing modules/files, wrong port). Gaps: `DIRECTORY_CONTRACT.yaml`
under-counts modules (40 vs 49) and misses dunker + 2 `__main__` blocks;
`scripts/` and `tests/` undocumented; several modules unexported from
`__init__`; stub lacks swap endpoints; proposed supervisor/gate endpoints
unimplemented. Top continuity-loop findings: orchestrator `node.db` lives
outside `OMNI_STATE_DIR` (snapshots miss it), swap busy-detection is
monotonic (evict can starve), witness path ignores `OMNI_STATE_DIR`,
manifest hash truncates at 1MB/file, gate failure latches permanently,
soma probe has no periodic loop, affect_tracer is unwired into
`/brain/chat`. Full route inventory + env-var surface in §4.
