# Audit: Kilo Experiments Gaps — 2026-11-04

## Status
Concluído (primeira passagem).

## Escopo
Bancos SQLite (`data/**/*.sqlite`, `scripts/**/*.sqlite`), scripts de experimentos (`scripts/experiments`, `scripts/*_battery`), daemons (`src/omni_coworker/kernel_daemon`), `docs/studies/GEMMA4_BATTERY_INVENTORY.md`, alinhamento com `docs/PENDING_ROADMAP.md`.

## Método
[DADO] Inspeção de schema/contagens via `python /tmp/audit_sqlite.py` (sqlite3). Daemons listados por glob. Nenhum dado simulado.

## Achados — bancos com colunas zeradas/NULL/vazias

### data/somatic_probes.sqlite
- [DADO] `swap_gb` = 0 em 9/9 (100%); `cpu`=0 em 2/9. [INTERPRETAÇÃO] coleta de swap não funcional ou sempre zero (VM sem swap) — confirmar ambiente antes de usar como métrica.

### data/memtrias.sqlite
- [DADO] `forgotten`=0 em 455/455; `instance` NULL em 108; `doc_ref` NULL em 8. [INTERPRETAÇÃO] flag de esquecimento nunca acionado (poda inerte) — alinhar a `dream.metabolize`.

### data/shared_workspace.sqlite
- [DADO] `provenance_json` NULL em 9421/18218 (51.7%). [INTERPRETAÇÃO] eventos sem proveniência → quebra de cadeia de evidência (AUDIT imutável).

### data/hf_gemma4/gemma4_e4b_l4_results.sqlite
- [DADO] `thinking_trace` vazia em 126/126; `tool_calls_n`=0, `progress_events_n`=0 em 103/126; `thinking_tokens`=0, `thought_closed`=0 em 126/126; `n_gates_interventions`=0 em 124/126; `turn2_*`=0/NULL em 126/126 (turn2 não executado). [LIMITE] dataset HF só cobre turn1; claims de turn2 no writeup sem evidência.

### data/hf_gemma4/gemma4_t4x2_cascade_results.sqlite
- [DADO] `thinking_trace` NULL em 200/200; `tool_calls_n` NULL em 200/200; `progress_events_n`=0 em 80/200; `cascade_events` com `last_progress_marker`/`context_ref`/`frame_text` vazios em 1435/1668 (restart_idx=0). [INTERPRETAÇÃO] eventos de cascade sem payload de progresso — reprodutibilidade limitada.

### data/hf_gemma4/gemma4_t4x2_v2_results.sqlite
- [DADO] `steering_source` NULL em 205/205; `n_hook_interventions`=0 em 205/205; `hook_fired_count`=0 em 1620/1620 (latent_layer_metrics); `loto_episode_accumulators.neg_n`=0 em 417/540. [INTERPRETAÇÃO] steering/calibração não disparou nos runs v2 — verificar se hooks estavam habilitados.

### data/hf_gemma4/canary_v2_test.sqlite
- [DADO] `visible_response` vazia em 2/2; `ur_visible` NULL em 2/2; `steering_source` NULL em 2/2; `hook_fired_count`=0 em 36/36; `memory_snapshots.record_id` NULL em 2/2. [INTERPRETAÇÃO] canary v2 incompleto/abortado.

### scripts/coding_battery/coding_battery.sqlite
- [DADO] `recall` NULL em 23/50; `hallucinated` NULL em 20/50; `fix_compiles`=0 em 30/50; `fix_black`=0 em 30/50. [INTERPRETAÇÃO] metade dos casos sem fix compilável — alinhar a P4 (coding battery em execução).

### scripts/refactor_battery/battery_results.sqlite
- [DADO] `smoke_passed`=0 e `smoke_failed`=0 em 12/13; `submitted`=0 em 13/13; `turns`=0 em 1/13; `turns_json` NULL em 1/13. [INTERPRETAÇÃO] smoke não rodou na maioria dos runs (bug de harness documentado no roadmap — sys.path).

### scripts/supervisor_battery/supervisor_battery.sqlite
- [DADO] `passion_flag`=0, `angst_score`=0, `chaos_score`=0 em 16/16; `tracer_level`/`posture` NULL em 8/16; `judge_intent`/`judge_recommend` NULL em 13/16. [INTERPRETAÇÃO] métricas de afeto não persistidas para metade dos turnos (instância fresh por turno).

### scripts/corpus_reading_battery/corpus_delivery_battery.sqlite
- [DADO] `author_match`=0 em 4/10; `anomaly`=0 em 6/10; `tabular_ratio`=0 em 8/10; `layer_mps_metrics_json` NULL em 5/10. [INTERPRETAÇÃO] cobertura parcial de métricas por run.

### data/code_quality/priors.sqlite
- [DADO] `batch_suppressible`=0 em 85/96; `confidence`=0 em 3/6 (findings). [INTERPRETAÇÃO] priors conservadores — verificar se suppressível deve ser booleano.

### data/app_delivery_workspace/.../corpus_audit.sqlite
- [DADO] `anomaly`=0 em 27/30; `dado_count`=0 e `tabular_ratio`=0 em 30/30. [INTERPRETAÇÃO] colunas não preenchidas pelo scanner (possível schema mismatch).

## Serviços dormentes
- [DADO] `kernel_daemon` presente (`ignition`, `phi_meta`, `metastability`, `scheduler`, `feedback`, `collector`, `features`, `homeostasis`, `regime`, `api`). [INTERPRETAÇÃO] não verificado se estão wired em app.py; roadmap cita ignition/phi_meta implementados. Recomendação: auditar wiring (grep) — fora do escopo de edição src/.

## Propostas (alinhadas a PENDING_ROADMAP)
1. Completar canary v2 e popular `ur_visible`, `steering_source`, `hook_fired_count` (P4).
2. Re-rodar coding_battery para preencher recall/hallucinated (P4).
3. Fix harness smoke path (refactor_battery) — já documentado; re-rodar.
4. Persistir proveniência em shared_workspace (P1 witness).
5. Reconciliar schema corpus_audit (dado_count/tabular_ratio) com scanner.
6. Auditar wiring dos daemons em app.py (sem editar src/ nesta passagem).

## Limites
- [LIMITE] Sem execução de testes (apenas leitura de bancos). Nenhum dado simulado.
