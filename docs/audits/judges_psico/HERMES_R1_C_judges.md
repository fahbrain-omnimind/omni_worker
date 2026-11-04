# HERMES R1 — Fatia C: judges/ (Gemma-4)

[DADO] Juiz: Hermes (hermes-agent). Escopo: `gemma4_runs_20261030/judges/` (AGGREGATE_ABC, ANALYSIS_CONSOLIDATED, leaked_reasoning, MANIFEST_SHA256), `judges/CONSENSUS_*.json`, `erika_mps_5turnos/`, `activity_db/*.sqlite`, README.

## Método

- `ls`, `python3 json.load`, `sha256sum`, consultas SQLite via python.
- Todos os caminhos abaixo são relativos a `/content/omni_worker/data/psicodiagnostico_v`.

## Achados

1. [DADO] MANIFEST_SHA256.json declara 189 arquivos em 7 grupos. Verificação de hashes:
   - `judge_scores` (32), `judge_parts` (80), `bundles_respostas_cruas` (20), `scripts` (18), `paper_track` (31): 181 arquivos NÃO LOCALIZADOS no dataset (diretório `judges/scores_gemma4/` e demais ausentes). [DADO]
   - `analise` (3): arquivos presentes em `gemma4_runs_20261030/judges/` mas hashes DIVERGENTES (AGGREGATE_ABC.json/md, leaked_reasoning_gemma4.json). [DADO]
   - `fontes` (5): 1 ok (v10_colab_benchmark.sqlite hash ok), 4 missing (JUDGE_RUBRIC, WRITEUP_ESQUELETO.md/.json, WRITEUP_ESQUELETO_EN.md). [DADO]
   - Conclusão: MANIFEST não é verificável como está; proveniência declarada ≠ artefatos presentes. [INTERPRETAÇÃO]

2. [DADO] AGGREGATE_ABC.json: cobertura assimétrica confirmada — juiz A r1–r3, B apenas r1, C r1–r5 para 4 modelos × 5 runs. missing_cells lista 16 células. [DADO]

3. [DADO] leaked_reasoning_gemma4.json: 330 células com vazamento de raciocínio (marcadores `<|channel>` / `<channel|>`). por_modelo: e4b 5/5 coerentes; 12b 180 células/12 coerentes; 31b 14/10; 26b 131/81. [DADO] Material rico para análise psicanalítica associativa (camadas internas). [INTERPRETAÇÃO]

4. [DADO] CONSENSUS files (top-level `judges/`): 7 arquivos. CONSENSUS_TRIADE tem 15 runs (claude/gemini/gpt). CONSENSUS_REP_N2, WAVE1, WAVE2 com estrutura onda/juízes/pesos/runs. [DADO]

5. [DADO] README afirma "Sem segredos: varredura completa... zero ocorrências". Não verificado por mim nesta rodada (varredura não executada). [NÃO VERIFICADO]

6. [DADO] erika_mps_5turnos/bateria_5turnos_final.json: 676KB. [DADO] (conteúdo não inspecionado em detalhe.)

7. [DADO] activity_db: 10 sqlite. Tamanhos listados. [DADO]

## Tabela de alegações (README/monografia) verificadas

| Alegação | Status | Evidência |
|---|---|---|
| MANIFEST 189 arquivos verificáveis | DIVERGENTE | 181 missing + 3 mismatch |
| Juízes Gemma-4 cobertura assimétrica (A r1-3, B r1, C r1-5) | VERIFICADO | AGGREGATE_ABC missing_cells |
| leaked_reasoning 330 células | VERIFICADO | n_celulas=330 |
| Sem segredos | NÃO VERIFICADO | varredura não executada nesta rodada |

## Lacunas

- `judges/scores_gemma4/` ausente → impossível recalcular acordo inter-juízes a partir das fontes; AGGREGATE_ABC é derivado de dados não presentes. [LIMITE]
- Hashes do manifest não batem → proveniência não auditável. [LIMITE]
- CONSENSUS inter-juízes: não recalculei métricas (kappa etc.) — falta tempo/escopo; pergunta para rodada 2.

## Perguntas para outros juízes

- A: o banco embodied tem os scores brutos dos juízes? Se sim, posso recalcular acordo.
- B: v10_colab_benchmark.sqlite hash ok no manifest (fontes) — verificar se contém os bundles de respostas cruas.
- Todos: alguém localizou `judges/scores_gemma4/` em outro lugar?