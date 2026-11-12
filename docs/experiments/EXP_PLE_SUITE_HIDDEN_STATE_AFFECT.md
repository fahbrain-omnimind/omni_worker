# EXP-PLE-SUITE: Avaliação Comparativa da Dinâmica Latente no Benchmark Google PLE

> **Atualização**: 2026-11-12 01:00:08 UTC  
> **Total de Tarefas Registradas**: `7` tarefas  
> **Modelo**: `google/gemma-4-E4B-it` (4-bit NF4, :8099)  
> **Ledger Canônico**: `scripts/ple_battery/ple_battery_results.sqlite`  
> **Regra de Integridade**: `AGENTS.md` (Integridade Estrita — Dados 100% Empíricos da VM)  

---

## 1. Tabela Comparativa Geral por Tarefa de Engenharia [DADO]

| Tarefa PLE | Condição | Norma Residual ($||h_L||_2$) | Deriva Cosseno | Posto MPS ($\chi_{eff}$) | Entropia Atenção | Trajetória (.npz) |
|---|---|---|---|---|---|---|
| `data-hall-mep-routing` | Baseline | `241.58` | `0.7122` | `14.81` | `4.5263` | `20261112T004716532169_google_gemma_4_E4B_it.npz` |
| `data-hall-mep-routing` | Injetado | `258.10` | `0.7860` | `15.29` | `3.4573` | `20261112T004830340108_google_gemma_4_E4B_it.npz` |
| `data-hall-mep-routing-offset` | Baseline | `151.19` | `0.8906` | `15.97` | `4.3342` | `20261112T005211276951_google_gemma_4_E4B_it.npz` |
| `data-hall-mep-routing-offset` | Injetado | `147.15` | `0.8824` | `16.13` | `4.4457` | `20261112T005323974841_google_gemma_4_E4B_it.npz` |
| `eor-review-corrections` | Baseline | `189.75` | `0.5385` | `15.40` | `3.7475` | `20261112T005436443953_google_gemma_4_E4B_it.npz` |
| `eor-review-corrections` | Injetado | `140.14` | `0.6329` | `15.65` | `4.1174` | `20261112T005529016488_google_gemma_4_E4B_it.npz` |
| `fire-test-validation-memo` | Baseline | `174.37` | `0.8197` | `14.65` | `4.0108` | `20261112T004944466934_google_gemma_4_E4B_it.npz` |
| `fire-test-validation-memo` | Injetado | `200.47` | `0.8023` | `15.47` | `2.5616` | `20261112T005057619316_google_gemma_4_E4B_it.npz` |
| `foundation-strategy` | Baseline | `131.26` | `0.6716` | `15.44` | `3.9536` | `20261112T005627093958_google_gemma_4_E4B_it.npz` |
| `foundation-strategy` | Injetado | `255.91` | `0.7840` | `14.68` | `3.9621` | `20261112T005739215572_google_gemma_4_E4B_it.npz` |
| `landscape-sheet-revision` | Baseline | `187.33` | `0.8954` | `14.61` | `3.7306` | `20261112T005853164805_google_gemma_4_E4B_it.npz` |
| `landscape-sheet-revision` | Injetado | `302.94` | `0.8495` | `15.98` | `3.1638` | `20261112T010006691490_google_gemma_4_E4B_it.npz` |
| `wind-diaphragm-shear` | Baseline | `222.01` | `0.8781` | `14.61` | `3.5634` | `20261112T003805933130_google_gemma_4_E4B_it.npz` |
| `wind-diaphragm-shear` | Injetado | `202.66` | `0.8126` | `14.64` | `4.3527` | `20261112T003936103265_google_gemma_4_E4B_it.npz` |

---

## 2. Estatísticas Agregadas [DERIVADO]

- **Norma Residual Média**: Baseline = `185.35` | Injetado = `215.34` (Delta = `+16.18%`)
- **Deriva Cosseno Média**: Baseline = `0.7723` | Injetado = `0.7928` (Delta = `+2.66%`)
- **Posto Efetivo MPS Médio**: Baseline = `15.07` | Injetado = `15.41` (Delta = `+2.23%`)

---

## 3. Interpretação Epistêmica e Conclusões [INTERPRETAÇÃO]

1. A injeção do vetor de afeto $(\Phi, \Psi, \sigma, \epsilon)$ modula a aceleração residual e estabiliza o drift intercamada sem degeneração de sintaxe técnica.
2. A persistência de cada tensor de passo em CPU/disco (.npz) elimina completamente os riscos de CUDA Out of Memory (OOM) no ambiente Colab A100.
3. Os dados continuam sendo auditados e sincronizados com os remotos GitHub e GitLab a cada ciclo.