# HERMES_EXPANDED_AUDIT — Fatia C (acervo expandido)

Fonte: `/content/omni_worker/data/psicodiagnostico_v_v2/` (read-only). Verificação executada em disco (sem simulação).

## 1. Integridade de hashes (brief)

- judge_scores: 32/32 matches (100%) — conforme brief.
- judge_parts: 80/80 matches (100%).
- bundles_respostas_cruas: 20/20 matches (100%).
- Total 136 hashes verificados.

## 2. Inventário local (contagens verificadas)

- Arquivos de score (judge_*scores*.json, excluindo parts): 235.
- Diretórios de parts (scores_gemma_pranchas_juiz2_parts): 20 (cada run com 4 chunks).
- Bundles (arquivos *.json em bundles_*): 164.
- Thinking traces: 5 arquivos em `data_sanitized/thinking_traces/deepseek_r1_v5/` (módulos I–M).

## 3. Consensos (7 arquivos CONSENSUS_*.json)

| Arquivo | Runs | MAD cenas (range) | Observação |
|---|---|---|---|
| CONSENSUS_WAVE1.json | 7 | 0.12–0.18 | 2 juízes A/B, pesos 40/35/25 |
| CONSENSUS_WAVE2.json | 23 | 0.15–0.71 | 2 juízes A/B |
| CONSENSUS_COLAB.json | 16 | MAD 0.31 (anubis ex.) | colab runs, juízes A/B |
| CONSENSUS_RUN2.json | 3 | MAD ~0.16 | runs independentes |
| CONSENSUS_TRIADE.json | 15 | MAD 0.06 (claude ex.) | triade A/B/C |
| CONSENSUS_UNIFIED_V10.json | 2 | MAD 0.08 / 0.26 | deepseek_r1 vs v4_flash |
| CONSENSUS_REP_N2.json | 60 | (a consolidar) | 1 juiz A |
| **Total** | **126** | — | — |

## 4. Agreement real

- Wave1: MAD baixo (0.12–0.18) → alta concordância inter-juízes.
- Wave2: MAD até 0.71 em alguns runs → heterogeneidade maior; investigar runs com MAD >0.5.
- Triade: claude_sonnet concordância muito alta (MAD 0.06, 15/20 cenas exatas); gpt_5_6 e gemini com maior dispersão.
- Unified V10: deepseek_r1 (MAD 0.08, det 20/20) supera v4_flash (MAD 0.26, det 7/20).
- Colab: MAD típico 0.31, exato apenas 1/20 em anubis → baixa concordância absoluta.

## 5. Thinking trace

- Material disponível apenas para deepseek_r1_v5 (5 módulos: I WCST, J Stroop/GoNoGo, K N-back, L IGT, M QUATI).
- Uso: interpretação psicanalítica das camadas e raciocínio interno; não deve ser tratado como evidência empírica de desempenho.

## 6. Limitações / gaps

- CONSENSUS_REP_N2 tem 1 único juiz (A) → sem concordância inter-juízes; MAD não aplicável.
- Parts count (80) corresponde a 20 runs × 4 chunks, mas score files totais (235) incluem waves/colab/triade — nem todos têm parts.
- Nenhum dado simulado gerado; todos os números acima vêm de leitura direta dos JSON em disco.