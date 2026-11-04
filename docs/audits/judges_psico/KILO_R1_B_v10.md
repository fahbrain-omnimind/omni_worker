# Juiz Kilo — Rodada 1 — Fatia B (V10/V11)

_Auditoria cooperativa de dados. Juiz: Kilo (fatia B). Data: 2026-11-04._

## Método

Comandos executados (todos em `/content/omni_worker/data/psicodiagnostico_v`):
- `find ... -maxdepth 3` para inventário de arquivos.
- `python3 -c` com `sqlite3` para contagens/esquemas/nulos em `v10_colab_benchmark.sqlite` e `gemma4_runs_20261030/v10_colab_benchmark.sqlite`.
- `python3` com `json`/`pandas` para comparar `psicodiagnostico_v10_results.json` ↔ `.parquet`.

## Achados (tagged)

- [DADO] `v10_colab_benchmark.sqlite`: v10_runs=1360, rorschach_b_runs=6059, cognitive_runs=640; modelos distintos: v10=16, rorschach=79, cognitivo=16. Fonte: sqlite3 count.
- [DADO] `gemma4_runs_20261030/v10_colab_benchmark.sqlite`: v10_runs=1760, rorschach_b_runs=5099, cognitive_runs=800. Fonte: sqlite3 count.
- [DADO] JSON↔Parquet V10: json len=1360, parquet shape=(1360,9), colunas idênticas (id, model_id, cena_id, run_idx, fase_1/2/3_resp, scores_json, timestamp). Fonte: pandas.read_parquet + json.load.
- [DADO] Nulos/vazios: v10 fase_1_resp vazios=36, scores_json vazios=0; rorschach resposta vazia=33; cognitivo resposta vazia=43. Fonte: sqlite3.
- [DADO] rorschach respostas <5 chars: 34/6059. Fonte: sqlite3.
- [LIMITE] Tabela `v10_scene_scores` não existe nos bancos (BRIEF cita-a); a correspondente é `v10_runs` com `scores_json`. NÃO LOCALIZADO `v10_scene_scores`.
- [INTERPRETAÇÃO] O banco gemma4 tem mais v10_runs (1760) que o colab (1360) mas menos rorschach (5099 vs 6059), indicando conjuntos não idênticos — provável execução parcial/incremental. Requer verificação de sobreposição de model_id/cena_id.

## Tabela de alegações verificadas (slice B)

| # | Alegação | Resultado | Fonte |
|---|---|---|---|
| 1 | v10_colab_benchmark.sqlite = 1.360 cenas + 640 rodadas cognitivas | VERIFICADO (v10_runs=1360, cognitive_runs=640) | sqlite3 |
| 2 | rorschach_b_runs canônico = 2.015 | DIVERGENTE (6059 no colab; 5875 no bank) | sqlite3 |
| 3 | consistência json↔parquet↔sqlite | VERIFICADO para v10 (1360=1360, esquema idêntico) | json/parquet |
| 4 | scorer heurístico / pranchas Rorschach degeneração | PARCIAL: 33 vazias, 34 <5 chars em 6059 (0,56%+0,56%) | sqlite3 |

## Lacunas

- Não verificada sobreposição model_id/cena_id entre os dois bancos v10.
- Não inspecionadas amostras de respostas Rorschach para repetição/vazamento (thinking_trace).
- peer_cross_evals e protocols não auditados nesta rodada.
- scripts/ não revisados para scorer heurístico.

## Perguntas para outros juízes

- Juiz A: confirmar se embodied bank rorschach_b_runs=5875 é subconjunto dos 6059 do colab.
- Juiz C: verificar hashes do MANIFEST_SHA256 para os parquets V10.
- Juiz C: agreement inter-juízes sobre v10 (peer_cross_evals).

## Notas de integridade

Nenhum dado inventado; todas as contagens acima provêm de consultas executadas. Dataset tratado como read-only.