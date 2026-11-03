<!-- doc_id: OW-OPS-005 | title: Recuperação pós-queda de VM (2026-11-03) | author: agy-claude | requester: artifice-operator | date: 2026-11-03 | status: operational -->

# OW-OPS-005 — Recuperação pós-queda de VM (2026-11-03)

Estatuto: **[DADO]** = verificado nesta sessão; **[LIMITE]** = restrição/lacuna conhecida; **[INTERPRETAÇÃO]** = leitura minha.

## Linha do tempo

- **[DADO]** Último commit: `1941cad` 19:46Z; `origin/master` = `HEAD` local; árvore limpa após o restore da pasta.
- **[DADO]** VM recriada; disco reiniciado. Pasta de trabalho restaurada pelo operador (~21:19Z).
- **[LIMITE]** Alterações não commitadas entre 19:46Z e a queda **não têm fonte de recuperação** (git limpo; backup só cobre artefatos de runtime). Não é possível dizer o que foi perdido: **NÃO LOCALIZADO**.

## Restauração (ordem executada)

1. **[DADO]** Backup `omni_worker_20261103T203208Z.tar.gz` (Drive `omni_worker_backups`, 1,5 GB, 297 entradas) — `archive_worker_state.sh --verify` OK (manifest + sha256).
2. **[DADO]** Extraído em staging e copiado para o repo: `data/`, `logs/`, `omni_code_index/`, `runtime_config/` (sem `pids/`) + 3 ledgers sqlite de `scripts/*_battery/`. `coding_battery.sqlite` já vinha no git.
3. **[DADO]** `pragma integrity_check` = ok nos 10 bancos. Contagens: `integration_loop` 1295 ciclos; `shared_workspace` 15539 eventos; `scars` 9; `node.db` artifacts 389; `somatic_probes` 3; ledgers: coding 50, diag 88, refactor 13, supervisor 16.
4. **[DADO]** `memtrias.sqlite`: `memories = 0` e `witness.jsonl` = 184 linhas **idênticos** nos backups 18:31Z, 19:31Z e 20:32Z → não é perda na janela coberta. **[LIMITE]** não verificado se `memories` já era 0 antes das 18:31Z (backup 16:59Z sem esses arquivos legíveis).
5. **[DADO]** Witness: 184 entradas, 0 quebras de `prev_hash`→`hash` (checagem de encadeamento; **hash não recomputado**). Última entrada 2026-11-03T03:00Z.
6. **[DADO]** Dependências reinstaladas via pip: `bitsandbytes`, `faiss-cpu`, `sentence-transformers`, `pandas`, `pyarrow`, `nvidia-ml-py`, `ruff`, `black`, `pytest-asyncio` (a VM nova só tinha torch/transformers/fastapi/uvicorn/pytest).
7. **[DADO]** `bash scripts/start_omni_worker.sh`: analyst `gemma-4-12B-it` :8098, executor `gemma-4-E4B-it` :8099, API :8081, `state_guard`, `swap_scheduler`, `archive_loop`. Modelos baixados do HF (cache vazio). VRAM ~17,2/23 GB.
8. **[DADO]** Acervo vetorizado: `fabricioslv/omnimind-acervo-vetorizado` (dataset HF), 526 arquivos / 38,3 GB → `/content/acervo_vetorizado`. API reiniciada com `OMNI_ACERVO_DIR`. `acervo_available()=True`; busca "mal-estar na civilização Freud" → 3 hits reais (obra+página) em 7,6 s.

## Testes

- **[DADO]** `PYTHONPATH=src python -m pytest tests/ -q` → **452 passed, 4 skipped** (87,7 s). Doc anterior citava "454 passed, 2 skipped" — diferença **não investigada**.
- **[DADO]** Primeira rodada falhou em `test_coding_battery` por `black` ausente (ambiente, não código); resolvido instalando `black`.

## Lacunas conhecidas / ações para próxima recuperação

- **[LIMITE]** `start_omni_worker.sh` **não** instala dependências, não restaura backup e não baixa o acervo; `OMNI_ACERVO_DIR` precisa ser exportado antes de subir a API (o script não o define). Candidato a script `scripts/bootstrap_vm.sh`.
- **[LIMITE]** Segredos (`HF_TOKEN`, etc.) não entram no backup; usar `scripts/restore_env.sh`.
- **[LIMITE]** API faz bind em `0.0.0.0:8081`; `AGENTS.md` exige loopback em produção pública.
- **[LIMITE]** `start_proc` faz append nos logs; linhas antigas restauradas (ex.: `address already in use` :8081 de execução anterior) aparecem misturadas com a sessão atual.
- **[LIMITE]** Backup horário = janela de perda de até 1 h; commits frequentes reduzem o risco para código.
