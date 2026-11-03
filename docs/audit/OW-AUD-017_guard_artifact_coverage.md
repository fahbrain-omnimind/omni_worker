# Guard/State Audit Report — omni_worker (READ-ONLY)

Generated: 2026-11-03. Repo: /content/omni_worker. OMNI_STATE_DIR env unset → default `data/` (evidence: `env | grep OMNI_STATE_DIR` empty; `src/omni_coworker/store/state_guard.py:29-31`, `scripts/start_omni_worker.sh:51`, `scripts/restore_env.sh:81`).

## 1. Artefato → produzido? → arquivado? → no pack?

| Artefato (path) | Produzido? | Arquivado? (archive_worker_state.sh) | No pack? |
|---|---|---|---|
| data/node.db | sim | sim (data/) | não |
| data/memtrias.sqlite | sim | sim | não |
| data/witness.jsonl (184 records) | sim | sim | não |
| data/audit/audit_chain.log | não (dir ausente) | n/a | não |
| approval_queue.jsonl | não (ausente) | n/a | não |
| scripts/*_battery/*_battery.sqlite (4) | sim | sim | não |
| data/monitor/internal_vocabulary.sqlite (lalangue) | não | n/a | não |
| data/phylogenetic/signature.json | não | n/a | não |
| data/metabolize_state.json (dream watermark) | não | n/a | não |
| data/trust_scores.json, trust_events.jsonl | sim | sim | não |
| data/integration_loop.sqlite + modulation.json | sim | sim | não |
| data/shared_workspace.sqlite (+wal/shm) | sim | sim | não |
| data/scars.sqlite | sim | sim | não |
| data/somatic_probes.sqlite (+wal/shm) | sim | sim | não |
| data/code_quality/priors.sqlite | sim | sim | não |
| data/cli_circuit_breaker.json | sim | sim | não |
| data/quarantine.json, quarantine_records.json | sim | sim | não |
| data/refusal_state.json | sim | sim | não |
| data/monitor/erika_torch_activations.jsonl (+offset) | sim | sim | não |
| data/monitor/activation_vectors/*.npz | sim | sim | não |
| data/state_snapshots/*.tar.gz (3) | sim | sim (data/) | não |
| logs/* | sim | sim | não |
| omni_code_index/* | sim | sim | não |
| runtime_config/pids/* | sim | não | sim |
| /tmp/omni_modes_state.json | sim | não | sim |

## 2. Gaps (path + evidência)

1. Snapshot mais recente falha verificação de manifest (fail-closed restore recusaria).
   - `data/state_snapshots/state_20261103T034851713474Z.tar.gz` (28,492,046 bytes): stored hash `37a89d963e9d...`, recomputado `0df9e0583e43...` (mismatch). Witness chain do snapshot válido (184 records).
   - Causa provável: `_manifest_hash()` calculado antes do `tar` (state_guard.py:52-84) enquanto arquivos mutáveis (sqlite WAL, activation_vectors) mudaram entre hash e empacotamento.
2. Nenhum restore testado em produção.
   - `data/witness.jsonl`: 0 eventos `state_restore`; `logs/state_guard.log`: 0 bytes.
3. Proveniência dos archives no Drive ausente.
   - `/content/drive/MyDrive/omni_worker_backups/`: 5 tar.gz, 0 `*.manifest.json`/`*.sha256` (script promete em `archive_worker_state.sh:write_provenance`). `--verify` retorna "sem sha256 sidecar".
4. Artefatos de runtime não cobertos pelo archive script.
   - `runtime_config/pids/*` (4 arquivos) e `/tmp/omni_modes_state.json` não estão em `data logs omni_code_index` nem nos 4 sqlite listados (`archive_worker_state.sh:archive_once`).
5. state_guard não é atômico (hash→tar race) — snapshot pode ser inconsistente.
6. Nenhum artefato corrompido/vazio em data/ (`find data -type f -size 0` = 0). Snapshots antigos (2) válidos.

## 3. Secrets

- Nenhum `.env`, `*token*`, `*secret*`, `*.pem`, `*.key`, `*credential*`, ssh keys no repo (find). 
- grep de padrões de alto sinal (ghp_, sk-, AIza, BEGIN KEY, HF_TOKEN=, AKIA) em data/logs/omni_code_index: sem hits.
- Tarballs do Drive: nenhum nome de entrada bate com padrões sensíveis.
- Exclusões do archive script presentes: `--exclude='*.env' ...` (archive_worker_state.sh) e boundary manifest lista 8 padrões.

## 4. Recomendações concretas

- Tornar snapshot atômico: calcular hash sobre o tar gerado (ou copiar state para staging antes de hash) em `state_guard.snapshot()`.
- Adicionar `runtime_config/` (e modos externos) ao archive script ou mover pids para `data/runtime_config/`.
- Investigar por que `write_provenance` não grava sidecars (manual funciona); adicionar check pós-archive e falhar se ausentes.
- Registrar restore de teste (ex.: cron/state_guard) e anexar evento `state_restore` (já suportado por `restore()`).
- Opcional: excluir `monitor/activation_vectors/*.npz` do archive para reduzir 68MB (não essencial para resume).
- Manter N_SNAPSHOTS=3 (atual) ou aumentar se VM recicla com frequência.

## 5. Excluídos por cautela

- Qualquer arquivo matching `*.env`, `*token*`, `*secret*`, `*.pem`, `*.key`, `*credential*`, `*id_rsa*`, `*id_ed25519*`.
- `/content/gitlab.txt`, HF_TOKEN e demais segredos (não presentes no repo; nunca incluídos).
- `/tmp` reports de auditoria/experimentos (não são runtime state).
- `__pycache__`, `.git`, `.venv`, `*.db-wal` soltos.
- Arquivos de origem incerta foram omitidos do pack (ex.: logs de terceiros).

## Pack

`/tmp/kilo_runs/gdrive_pack.tar.gz` (1,137 bytes) contém `MANIFEST.json` + `runtime_config/pids/*` + `tmp/omni_modes_state.json`, com sha256/tamanho por entrada. Verificado.

---

## Resolução (Devin, 2026-11-03)

- **Bug 1 (snapshot race) — CORRIGIDO**: `state_guard.snapshot()` agora faz
  staging (copytree) → hash do staging → tar do staging. Hash e conteúdo
  sempre consistentes; restore fail-closed verificado end-to-end.
- **Bug 2 (ledger errado no tar) — CORRIGIDO**: archive listava
  `refactor_battery.sqlite`; o ledger real é `battery_results.sqlite`
  (nunca era arquivado — o `2>/dev/null` escondia o erro). Agora com
  `--ignore-failed-read` explícito.
- **Gap 3 (runtime_config) — CORRIGIDO**: adicionado ao tar do archive.
- **Sidecars ausentes no Drive**: `write_provenance` está correto no código
  atual — os 5 archives sem sidecar são anteriores à função. `--verify`
  falhará neles (esperado: sem sha256 para conferir).
- **Pendente legítimo**: nenhum `state_restore` testado em produção
  (witness 0 eventos) — restore verificado só em teste hermético.
