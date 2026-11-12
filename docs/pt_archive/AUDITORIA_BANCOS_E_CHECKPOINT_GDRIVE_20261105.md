# AUDITORIA — Bancos SQLite, WAL Checkpoint e Backups no Google Drive

**Data:** 2026-11-05 (~17:15 UTC) · **Executor:** Devin (swe-2-max)
**Escopo:** `/content/omni_worker` (data/, scripts/, state/, logs/) + `/root/quantum_work` + `/content/drive/MyDrive/omni_worker_backups/`

Legenda: `[DADO]`=medido/verificado · `[DERIVADO]`=consequência direta · `[INTERPRETAÇÃO]` · `[LIMITE]`=restrição conhecida.

---

## 1. Inventário de bancos SQLite — 27 arquivos `[DADO]`

Todos os `*.sqlite`/`*.db` sob `data/` e `scripts/` foram abertos
(read-only) e tiveram `journal_mode` + tamanho medidos. Após isso,
`PRAGMA wal_checkpoint(TRUNCATE)` foi executado em **27/27 com sucesso**
(busy=0, `wal_restante=0`).

| Banco | journal | tamanho (bytes) | wal antes → depois |
|---|---|---|---|
| data/node.db | wal | 454.656 → 462.848 | 4.124.152 → **0** |
| data/shared_workspace.sqlite | wal | 28.651.520 → 28.766.208 | 4.144.752 → **0** |
| data/basal_vs_modulated_280turns_20261105.sqlite | wal | 307.200 | 0 → 0 |
| data/integration_loop.sqlite | wal | 6.397.952 | 0 → 0 |
| data/somatic_probes.sqlite | wal | 3.002.368 | 0 → 0 |
| data/hf_gemma4/gemma4_t4x2_v2_results.sqlite | wal | 36.810.752 | 0 → 0 |
| data/hf_gemma4/gemma4_t4x2_cascade_results.sqlite | wal | 851.968 | 0 → 0 |
| data/hf_gemma4/gemma4_e4b_l4_results.sqlite | wal | 1.024.000 | 0 → 0 |
| data/hf_gemma4/canary_test.sqlite | wal | 61.440 | 0 → 0 |
| data/hf_gemma4/canary_v2_test.sqlite | wal | 90.112 | 0 → 0 |
| data/memtrias.sqlite | delete | 7.069.696 | — |
| data/swe_mps_ablation_20261105.sqlite | delete | 36.864 | — |
| data/app_delivery_workspace/corpus_integrity_app/corpus_audit.sqlite | delete | 12.288 | — |
| data/docs_archive/{corpus_delivery_battery,diag_battery,supervisor_battery}.sqlite | delete | 8–40 KB | — |
| data/psicodiagnostico_v/*.sqlite (5 arquivos) | delete | 0–41,5 MB | — |
| scripts/*/*.sqlite (5 bancos de bateria) | delete | 0–40 KB | — |

`[DADO]` Os únicos WALs com conteúdo pendente eram `node.db-wal`
(4.124.152 B) e `shared_workspace.sqlite-wal` (4.144.752 B). O
checkpoint retornou `frames=0/0` — os frames commitados já haviam sido
consolidados por checkpoint anterior, restando arquivo alocado sem
frames pendentes; o TRUNCATE zerou os arquivos e os arquivos
principais cresceram marginalmente (454.656→462.848 e
28.651.520→28.766.208 B), absorvendo as páginas finais.

`[DADO]` `PRAGMA quick_check` = **ok** nos 4 maiores bancos vivos:
`node.db` (trust_events=5.166 linhas), `shared_workspace.sqlite`
(events=21.413), `integration_loop.sqlite` (cycles=1.369),
`memtrias.sqlite` (memories=382).

`[DADO]` `data/basal_vs_modulated_280turns_20261105.sqlite`:
`battery_turns` = **280 linhas** — bateria 280/280 confirmada;
`basal_envelope` = 2 linhas.

`[LIMITE]` `scripts/refactor_battery/battery_results.sqlite` e
`data/psicodiagnostico_v/data_sanitized/*.sqlite` têm **0 bytes**
(arquivos placeholder, não bancos válidos) — checkpoint reporta ok
(não há WAL), mas não contêm dados.

## 2. Artefatos adjacentes auditados `[DADO]`

- `data/monitor/` = 1,6 GB / 267 arquivos: `activation_vectors/` (31 MB,
  ~60 `.npz` 12B/E4B/31B), `activation_steps/` (1,5 GB),
  `erika_torch_activations.jsonl` (2,6 MB, com sidecar `.offset`),
  `integration_loop_cycles.jsonl` (5,9 MB), `framing_centroids*.npz`.
- `data/state_snapshots/` = 2,5 GB: 3 tarballs `state_20261105T*.tar.gz`
  (o mais recente 1,75 GB às 17:01).
- `data/psicodiagnostico_v/` = 426 MB (bancos v10/v11 + JSONLs de
  baterias hosted/kaggle).
- `data/trust_events.jsonl` = 1,3 MB; `logs/` = 524 KB / 27 arquivos;
  `omni_code_index/` = 2,1 MB; `runtime_config/` = 36 KB.
- `data/monitor/capture.env`: contém apenas vars de tuning `OMNI_ACT_*`
  (sem segredos reais) — mesmo assim corretamente excluído pelo padrão
  `*.env` (postura conservadora mantida).
- **`state/` — NÃO LOCALIZADO.** `mps_harvest_12b.jsonl` e
  `mesh_xray_latest.json` não existem em lugar nenhum da VM
  (buscado em `/content/omni_worker` e `/root`). São artefatos de
  runtime futuros: `scripts/mesh/mesh_xray.py` escreve
  `STATE_DIR/mesh_xray_latest.json` (fallback `<repo>/state`),
  `scripts/experiments/harvest_activations.py` usa
  `--out state/mps_harvest.jsonl` e `scripts/dashboard_export.py` lê
  `<repo>/state/`. `.gitignore:54` já lista `state/`. O archive passa a
  incluí-lo **condicionalmente** quando existir.

## 3. Mudanças aplicadas nos scripts `[DADO]`

### `scripts/archive_worker_state.sh`
- Nova função `checkpoint_sqlite()`: python3 varre `data/`, `scripts/` e
  `state/` (quando existir), executa `PRAGMA busy_timeout=15000` +
  `PRAGMA wal_checkpoint(TRUNCATE)` em todo `*.sqlite`/`*.db`, loga
  `ok|BUSY(parcial)|FALHA` por banco — chamada **antes do tar** em
  `archive_once()`.
- Membros do tar: `data logs omni_code_index runtime_config` + `state`
  (condicional) + **glob dinâmico** `scripts/*/*.sqlite scripts/*/*.db`
  (substitui a lista hardcoded de 5 bancos — futuro-proof).
- Novas exclusões de artefatos transitórios: `*-wal`, `*-shm`,
  `*-journal` (estado já consolidado via checkpoint — arquivar WALs
  crus podia reintroduzir dados obsoletos/parciais no restore).
- Segredos: padrões mantidos (`*.env *token* *secret* *.pem *.key
  *credential* *id_rsa* *id_ed25519*`).

### `scripts/restore_worker_state.sh` — **bug real corrigido**
- `[DADO]` O script checava `$ARCHIVE.sha256`
  (`omni_worker_X.tar.gz.sha256`), mas `write_provenance` grava
  `omni_worker_X.sha256` (sem `.tar.gz`). Resultado: o branch
  "sem .sha256 — extraindo mesmo assim" executava **sempre**; a
  verificação de integridade nunca rodava. Corrigido para
  `${ARCHIVE%.tar.gz}.sha256` com `awk NR==1`.

### `scripts/start_omni_worker.sh` — `ensure_state_restored()`
- Loop de restore passa a incluir `state` na lista de diretórios.
- Cópias hardcoded de 4 sqlites substituídas por merge genérico
  `cp -a "$stage/scripts/." "$REPO/scripts/"` (cobre qualquer
  `scripts/*/*.sqlite|*.db` novo automaticamente).
- `bash -n` OK nos 3 scripts.

## 4. Pacotes gerados no Drive `[DADO]`

### `omni_worker_20261105T170753Z.tar.gz` — checkpoint pós-bateria 280/280
- Tamanho: **4.373.336.060 B (4,1 GiB)** · 23.945 entradas ·
  top_level: data, logs, omni_code_index, runtime_config, scripts
  (`state` ausente — não existe ainda).
- sha256: `0f4cb978f54861ca7e563b3a3c4124f0bd6945ac63820450a1dbcc5404b4b6bf`
  + `.manifest.json` (lineage `prev_archive=...T161135Z`) + `.sha256`.
- `--verify`: **OK** (manifest + sha256 conferem).
- Spot-check de conteúdo: **0** membros `-wal`/`-shm`/`.env`/`token*`/
  `*secret*`/`.pem`/`.key`/`*credential*`; 49 membros sqlite/.db
  incluindo `data/basal_vs_modulated_280turns_20261105.sqlite`,
  `data/shared_workspace.sqlite`, `data/node.db`.

### `quantum_work_phase3_20261105.tar.gz` — `/root/quantum_work`
- Tamanho: **1.189.550.159 B (~1,1 GiB)** · 310 membros.
- Conteúdo: `candidates/` (103: submissions zip + `.kmb` phase3),
  `results/` (66: `.kmx` dqi + verified jsons), `impl/` (101),
  `impl_chem/` (29), `impl_phase3/` (9), `reports_20261105/` (2).
- `.sha256`: `e6e809ff938d8c53977c6e027fb0aca259010a06cefdc3cfeecb6d8bb900a129`
  — `sha256sum -c`: **OK**.
- **`scripts_phase1_2/` — NÃO LOCALIZADO** em `/root/quantum_work`
  (o próprio `EXECUCAO_QUANTUM_FASE3_20261105.md:162` registra que o
  diretório não existia). Os scripts das fases 1-2 reais são `impl/` e
  `impl_chem/` — incluídos como equivalentes e aqui declarados.

## 5. Estado do diretório de backups `[DADO]`

- 5 archives `omni_worker_*.tar.gz` ativos (KEEP=5, mais antigo
  `T120104Z` podado nesta execução): T130250Z (2,0 G), T140634Z
  (2,4 G), T150847Z (3,1 G), T161135Z (3,1 G), **T170753Z (4,1 G)**.
- **Órfãos pré-existentes (não tocados):**
  `.omni_worker_20261103T170623Z.tar.gz.tmp` (0 B),
  `.omni_worker_20261103T172811Z.tar.gz.tmp` (256 KB),
  `omni_worker_20261103T053639Z.manifest.json` + `.sha256` (tarball já
  podado pela retenção — sidecars sem dono).
- Artefatos avulsos: `diag_battery.sqlite` (28 KB, 04/11),
  `gemma4_gluzdov_v8.tar.gz` (775 KB), `removed_docs_20261104.tar.gz`
  (71 KB).

## 6. Pendências e recomendações `[INTERPRETAÇÃO]`

1. **Daemon `archive_loop` (PID 13033) roda código pré-atualização**
   (iniciado 10:58, antes do patch). O próximo ciclo horário ainda
   empacotará `-wal`/`-shm` e não checkpointará. Recomenda-se
   reiniciá-lo (`bash scripts/archive_worker_state.sh --loop 3600`)
   para o novo comportamento valer a partir do próximo archive.
   *Não reiniciei nesta sessão para não interferir em sessões
   concorrentes.*
2. Crescimento do archive (3,3→4,4 GB) vem de `state_snapshots/` (2,5 G)
   e `monitor/` (1,6 G) — se o Drive apertar, avaliar retenção separada
   para `state_snapshots` ou mover `.npz` antigos para pacote próprio.
3. O archive anterior a este checkpoint (T161135Z e anteriores) contém
   `-wal`/`-shm` crus — ao restaurar, preferir **T170753Z+** que já vem
   consolidado.
