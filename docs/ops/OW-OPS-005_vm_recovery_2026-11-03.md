<!-- doc_id: OW-OPS-005 | title: Recuperação pós-queda de VM, Bootstrap Completo e Bateria de Obras (2026-11-03) | author: antigravity-claude | requester: artifice-operator | date: 2026-11-03 | status: operational -->

# OW-OPS-005 — Recuperação pós-queda de VM, Bootstrap Completo e Bateria de Obras (2026-11-03)

Estatuto: **[DADO]** = verificado nesta sessão; **[LIMITE]** = restrição conhecida.

## 1. Linha do tempo e recuperação do trabalho da janela 19:46–20:32Z

- **[DADO]** Último commit antes da queda: `1941cad` (19:46Z).
- **[DADO]** Backup automático do Drive: `omni_worker_20261103T203208Z.tar.gz` (20:32Z, 1,5 GB, 297 entradas) — verificado com `archive_worker_state.sh --verify` (manifest + sha256 OK).
- **[DADO]** Dentro do backup das 20:32Z foi localizado `data/app_delivery_workspace/corpus_integrity_app/` (criado entre 20:23Z e 20:26Z), contendo a suíte de aceitação completa `test_corpus_app.py` (59 linhas) e os arquivos parciais `spec_contract.json` e `scanner.py` da bateria de leitura de obras e entrega de aplicativo que estava em desenvolvimento no momento da queda.

## 2. Repositórios de referência e Datasets Hugging Face restaurados

> **[PROVENIÊNCIA / PORTABILIDADE]**: Os artefatos e repositórios listados abaixo pertencem ao acervo histórico privado e aos pontos de salvamento do autor no Google Drive/Hugging Face, utilizados especificamente para hidratação e continuidade neste ambiente de desenvolvimento (Colab). O repositório público `omni_worker` foi arquitetado de forma autossuficiente e hermética: terceiros podem clonar e executar a suíte de testes e o servidor standalone sem acesso a esses caminhos privados, operando com bancos de dados SQLite gerados sob demanda.

1. **[DADO]** `/content/omnimind-kilombo-sovereign` (1,4 GB, read-only): descompactado de `/content/drive/MyDrive/omnimind_backup/omnimind-kilombo-sovereign.tar.gz` — inclui `/content/omnimind-kilombo-sovereign/revisao/bibliografia_philpapers_20261005/txt/` (29 textos) e `revisao/A6_integrador/livro_vfinal.md` (15.551 linhas).
2. **[DADO]** `/content/omni_node` (read-only): clonado de `https://github.com/fahbrain-omnimind/omni_node.git` (`HEAD f4d2184f`).
3. **[DADO]** Acervo vetorizado (`/content/acervo_vetorizado`, 526 arquivos, 38,3 GB): baixado de `fabricioslv/omnimind-acervo-vetorizado` (`acervo_index.faiss` 4,34 GB + `acervo_manifest.sqlite` 779 MB, 2.402.192 vetores 384D `all-MiniLM-L6-v2`).
4. **[DADO]** Datasets privados da competição em `data/hf_gemma4/` (todos `PRAGMA integrity_check = ok`):
   - De `fabricioslv/gemma4-kaggle-dual-t4-results`:
     - `canary_test.sqlite` (60 KB, 4 `generation_records`)
     - `canary_v2_test.sqlite` (88 KB, 2 `generation_records`, 36 `latent_layer_metrics`)
     - `gemma4_t4x2_cascade_results.sqlite` (832 KB, 200 `experiment_ledger`, 200 `generation_records`, 1668 `cascade_events`)
     - `gemma4_t4x2_v2_results.sqlite` (36 MB, 205 `experiment_ledger`, 205 `generation_records`, 2440 `cascade_events`, 1620 `latent_layer_metrics`, 540 `loto_episode_accumulators`, 62 `steering_calibration`)
   - De `fabricioslv/gemma4-e4b-colab-l4-results`:
     - `gemma4_e4b_l4_results.sqlite` (1,0 MB, 124 `experiment_ledger`, 126 `generation_records`, 1492 `latent_layer_metrics`)

## 3. Requerimentos (`pyproject.toml`) e Bootstrap no Instalador (`scripts/start_omni_worker.sh`)

- **[DADO]** `pyproject.toml`: adicionadas as dependências reais verificadas por varredura AST do código (`sse-starlette>=2.0`, `huggingface-hub>=0.23` em `dependencies`; `pytest-asyncio>=0.23`, `pyphi>=1.2` em `test`; e grupo unificado `[all]`).
- **[DADO]** `scripts/start_omni_worker.sh` atualizado para executar o ciclo completo na ordem correta ao subir a VM:
  1. `restore_env.sh --scope public` se `HF_TOKEN` ausente;
  2. `ensure_deps`: configura `.venv` (se `OMNI_CREATE_VENV=1`) e instala `pyproject.toml[all]` caso falte qualquer pacote;
  3. `ensure_state_restored`: se os bancos em `data/` não existirem, localiza o backup mais recente em `/content/drive/MyDrive/omni_worker_backups`, verifica `manifest + sha256` e restaura `data/`, `logs/`, `omni_code_index/`, `runtime_config/` e os `.sqlite` das 5 baterias;
  4. `ensure_reference_assets`: garante `/content/omnimind-kilombo-sovereign`, `/content/omni_node`, `/content/acervo_vetorizado` e `data/hf_gemma4/`;
  5. Sobe sequencialmente `brain_analyst` (`:8098`), `brain_executor` (`:8099`), `worker_api` (`:8081` com `OMNI_ACERVO_DIR` e `OMNI_MEMTRIAS_AUTO_LOG=1`), `state_guard`, `swap_scheduler` e `archive_loop`;
  6. `rehydrate_memtrias.py`: se `data/memtrias.sqlite` estiver com `0` memórias, reidrata todos os namespaces canônicos e tece o sonho inicial (`dream.metabolize()`).

## 4. Memória Topológica (`data/memtrias.sqlite`)

- **[DADO]** Diagnosticada a causa de `memories = 0` no backup anterior: `/brain/chat` tinha `memory_log=False` por default e não havia rotina de ingestão dos artefatos locais após recriação.
- **[DADO]** Criado e executado `scripts/rehydrate_memtrias.py` com embeddings reais `all-MiniLM-L6-v2` (384D) e ligado `OMNI_MEMTRIAS_AUTO_LOG=1` em `src/omni_coworker/brain/server.py`.
- **[DADO]** Estado verificado de `data/memtrias.sqlite`: **264 memórias reais** nos 7 namespaces (`document`: 89, `instance`: 92, `machine`: 56, `interaction`: 14, `state`: 11, `user`: 1, `dream`: 1).

## 5. Bateria de Leitura de Obras & Entrega de Aplicativo (`corpus_integrity_app`)

- **[DADO]** Completados `spec_contract.json`, `scanner.py` e `cli.py` em `data/app_delivery_workspace/corpus_integrity_app/`.
- **[DADO]** `pytest data/app_delivery_workspace/corpus_integrity_app/test_corpus_app.py` → **4/4 passed** sobre as fixtures reais do PhilPapers 2026 (`24_Desmond` ↔ `255_hugh-desmond` MD5 `5cb0975024fd759fce9a97e0d25be8f7` e anomalia `30_Beckmann` = *MetaOthello*).
- **[DADO]** Criado e executado `scripts/corpus_reading_battery/run_corpus_delivery_battery.py` (relatório em `docs/results/corpus_delivery_battery.md` e ledger em `scripts/corpus_reading_battery/corpus_delivery_battery.sqlite`).
