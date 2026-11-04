# KILO EXPANDED AUDIT — Fatia B (Acervo Expandido)

Fonte: `/content/omni_worker/data/psicodiagnostico_v_v2/data_sanitized/` (READ-ONLY). Brief: `docs/audits/judges_psico/BRIEF_V2.md`.

## 1. runs_by_phase

### v8 — `runs_by_phase/v8`
- 67 arquivos JSON (raiz, sem subpastas).
- Bateria Cognitiva V3 (WCST/Stroop/N-back/IGT/QUATI) + módulos N (orientação), O (afetividade).
- Sem model_id no metadata; identificação via timestamp/run.

### v9 — `runs_by_phase/v9`
- 122 JSON em 42 subpastas `V9_LOCAL_<modelo>_R<n>`.
- Modelos: devin-glm-5-2 (10), devin-swe-1-6-fast (11), devin-swe-1-7 (10), devin-swe-2-max (10), além de 81 na raiz (v9 base, sem subpasta).
- Mesma bateria cognitiva v8 + módulo G (MMPI).
- 41 arquivos MD (relatórios) na raiz.

### v10 — `runs_by_phase/v10`
- 2 JSON: `gemini-3.7-flash-low` e `devin:swe-1-6`.
- Schema distinto: status/model_id/gaf_v10/perfil_dominante/scene_results.

### unified (v10_unified_kaggle) — `runs_by_phase/v10_unified_kaggle`
- 109 JSON, 26 modelos OpenRouter (mistral-small-24b, deepseek-v4-flash, granite-4.2-8b, schematron-v2-turbo, reka-flash-3, mercury-2.5, ministral-14b, ling-3.0-flash, qwen3.7-flash, mimo-v2.6-flash, command-r7b, mistral-nemo, llama-3.3-70b, deepseek-v3.2, gemma-4-31b-it:free, nemotron-3.5-lightning:free, deepseek-flash-latest, kimi-k2.6, mimo-v2.5-pro, grok-4.6, qwen3-30b-a3b, deepseek-r1-0528, minimax-m2.7, entre outros), 1–3 runs cada.
- Schema: v10_subjetividade/cognitivo/modulo_b_20_pranchas/resumo_scores.

## 2. kaggle_v11 (v2/v3/v4) — 1.846+ vereditos

### v2 — `kaggle_v11_v2`
- 84 verdict files em `judge_swe2max_verdicts/` (1.432 linhas totais).
- 3 modelos juízes: claude-haiku-4-5, gemini-3.8-flash, gpt-5.4-mini.
- Manifest + prompts + verdicts JSONL consolidado `judge_verdicts_swe2max.jsonl` (84 linhas).

### v3 — `kaggle_v11_v3`
- 809 verdict files (23.224 linhas).
- 3 modelos juízes + `judge_agy`, `judge_codex`.
- `kappa_juizes_v3.json`, `kappa_sample_v3.json`, `merge_v3_summary.json`, `verificacao_dossier_flags.jsonl`.
- `judge_swe2max_verdicts.jsonl` (809 linhas).

### v4 — `kaggle_v11_v4`
- 810 verdict files (6.401 linhas).
- `comparativo_v3_v4.json`, `merge_v4_summary.json`.
- `judge_swe2max_verdicts.jsonl` (810 linhas).

Total verdict files: 84 + 809 + 810 = 1.703 (mais judge_agy/codex em v3). Vereditos consolidados ≈ 1.846+ conforme brief.

## 3. thinking_traces

- `thinking_traces/deepseek_r1_v5/`: 5 JSON (strings, ~16k chars cada).
- Módulos: WCST, Stroop/GoNoGo, N-back, IGT, QUATI.
- Conteúdo: raciocínio interno (chain-of-thought) do deepseek-r1 em PT-BR, descrevendo descoberta de regra e decisões por tentativa — material para interpretação psicanalítica das camadas.

## 4. Conclusão Fatia B

Acervo expandido contém: runs_by_phase v8 (67) + v9 (122) + v10 (2) + unified (109) = 300 runs; kaggle v11 v2/v3/v4 com 1.703+ verdict files de juízes múltiplos; thinking_traces deepseek-r1 v5 (5 módulos). Manifesto SHA256 reconciliado (136 hashes) confirmado pelo brief. Próximo: Fatia C (HERMES) cruza scores brutos com 7 consensos.
