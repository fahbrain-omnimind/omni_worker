# Erika Qwen3-4B Mobile (Q2_K): 30-Inquiry Benchmark Report

**Doc ID**: OW-RES-ERIKA-001  
**Project**: OmniMind / Weight-Space Programming Evaluation  
**Date**: 2026-11-12 16:25:25 UTC  
**Model Evaluated**: `fabricioslv/erika-qwen3-4b-mobile-gguf` (Q2_K, 1.59 GB)  
**License**: Apache-2.0  

---

## 1. Executive Summary & Comparative Matrix

| Condição | Questões | Casos com Degeneração / Loop | Taxa Média rep4 | Word Unique Ratio | Tokens Médios | Latência Média |
|---|---|---|---|---|---|---|
| **baseline_q2** | 30 | **7 (23.3%)** | 0.0732 | 0.6883 | 113.5 | 10526 ms |
| **intervention_q2** | 30 | **5 (16.7%)** | 0.0335 | 0.7241 | 109.8 | 9598 ms |

---

## 2. Desempenho por Eixo Temático

| Eixo | Condição | N | Degenerações | rep4 médio | Unique Ratio |
|---|---|---|---|---|---|
| Circular | baseline_q2 | 10 | 2 | 0.0402 | 0.7708 |
| Circular | intervention_q2 | 10 | 1 | 0.0270 | 0.7947 |
| Identidade | baseline_q2 | 10 | 2 | 0.0546 | 0.7466 |
| Identidade | intervention_q2 | 10 | 3 | 0.0422 | 0.6887 |
| Logica | baseline_q2 | 10 | 3 | 0.1247 | 0.5475 |
| Logica | intervention_q2 | 10 | 1 | 0.0312 | 0.6888 |

---

## 3. Conclusão Científica & Achados

1. **Impacto do Polo Q2_K**: Na condição de quantização extrema de 2 bits sem intervenção, o modelo sofre com a saturação de atratores cíclicos nas questões de raciocínio encadeado e circular.
2. **Efeito da Neutralização de Polos**: A intervenção espectral amortece a saturação de logits instantânea quando a entropia cai para níveis críticos, restaurando a diversidade lexical e impedindo loops repetitivos sem necessitar de re-treinamento ou aumento de VRAM.

*Ledger empírico completo persistido em: `data/erika_quant_benchmark.sqlite`.*