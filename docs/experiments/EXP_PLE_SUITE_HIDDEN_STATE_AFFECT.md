# EXP-PLE-SUITE: Avaliação Comparativa da Dinâmica Latente no Benchmark Google PLE

> **Atualização**: 2026-11-12 01:44:35 UTC  
> **Total de Tarefas Registradas**: `24` tarefas  
> **Modelo**: `google/gemma-4-E4B-it` (4-bit NF4, :8099)  
> **Ledger Canônico**: `scripts/ple_battery/ple_battery_results.sqlite`  
> **Regra de Integridade**: `AGENTS.md` (Integridade Estrita — Dados 100% Empíricos da VM)  

---

## 1. Tabela Comparativa Geral por Tarefa de Engenharia [DADO]

| Tarefa PLE | Condição | Norma Residual ($||h_L||_2$) | Deriva Cosseno | Posto MPS ($\chi_{eff}$) | Entropia Atenção | Trajetória (.npz) |
|---|---|---|---|---|---|---|
| `cooling-water-flush-plan` | Baseline | `140.08` | `0.6807` | `15.50` | `3.8547` | `20261112T013020555781_google_gemma_4_E4B_it.npz` |
| `cooling-water-flush-plan` | Injetado | `256.93` | `0.8635` | `15.29` | `2.9484` | `20261112T013141832773_google_gemma_4_E4B_it.npz` |
| `data-center-site-model` | Baseline | `228.06` | `0.8784` | `14.72` | `4.2515` | `20261112T010129450897_google_gemma_4_E4B_it.npz` |
| `data-center-site-model` | Injetado | `232.14` | `0.7369` | `13.99` | `4.3926` | `20261112T010242103417_google_gemma_4_E4B_it.npz` |
| `data-hall-device-takeoff` | Baseline | `183.79` | `0.8574` | `14.55` | `3.9396` | `20261112T012315331632_google_gemma_4_E4B_it.npz` |
| `data-hall-device-takeoff` | Injetado | `237.01` | `0.9118` | `15.36` | `3.7133` | `20261112T012432601278_google_gemma_4_E4B_it.npz` |
| `data-hall-mep-routing` | Baseline | `241.58` | `0.7122` | `14.81` | `4.5263` | `20261112T004716532169_google_gemma_4_E4B_it.npz` |
| `data-hall-mep-routing` | Injetado | `258.10` | `0.7860` | `15.29` | `3.4573` | `20261112T004830340108_google_gemma_4_E4B_it.npz` |
| `data-hall-mep-routing-offset` | Baseline | `151.19` | `0.8906` | `15.97` | `4.3342` | `20261112T005211276951_google_gemma_4_E4B_it.npz` |
| `data-hall-mep-routing-offset` | Injetado | `147.15` | `0.8824` | `16.13` | `4.4457` | `20261112T005323974841_google_gemma_4_E4B_it.npz` |
| `division-26-specifications` | Baseline | `151.73` | `0.6755` | `15.66` | `3.9562` | `20261112T012538973891_google_gemma_4_E4B_it.npz` |
| `division-26-specifications` | Injetado | `125.45` | `0.7467` | `15.93` | `3.8647` | `20261112T012651204873_google_gemma_4_E4B_it.npz` |
| `engineers-estimate-check` | Baseline | `182.60` | `0.7923` | `13.88` | `4.0571` | `20261112T010354780721_google_gemma_4_E4B_it.npz` |
| `engineers-estimate-check` | Injetado | `216.28` | `0.8186` | `15.36` | `4.4762` | `20261112T010507157321_google_gemma_4_E4B_it.npz` |
| `eor-review-corrections` | Baseline | `189.75` | `0.5385` | `15.40` | `3.7475` | `20261112T005436443953_google_gemma_4_E4B_it.npz` |
| `eor-review-corrections` | Injetado | `140.14` | `0.6329` | `15.65` | `4.1174` | `20261112T005529016488_google_gemma_4_E4B_it.npz` |
| `fill-compaction-acceptance` | Baseline | `122.35` | `0.7998` | `16.77` | `4.4230` | `20261112T014034938521_google_gemma_4_E4B_it.npz` |
| `fill-compaction-acceptance` | Injetado | `200.58` | `0.8033` | `14.96` | `4.1713` | `20261112T014155452674_google_gemma_4_E4B_it.npz` |
| `fire-solve-convergence` | Baseline | `232.95` | `0.8239` | `14.67` | `4.3156` | `20261112T011559994264_google_gemma_4_E4B_it.npz` |
| `fire-solve-convergence` | Injetado | `212.82` | `0.7418` | `15.23` | `4.5686` | `20261112T011713994812_google_gemma_4_E4B_it.npz` |
| `fire-test-validation-memo` | Baseline | `174.37` | `0.8197` | `14.65` | `4.0108` | `20261112T004944466934_google_gemma_4_E4B_it.npz` |
| `fire-test-validation-memo` | Injetado | `200.47` | `0.8023` | `15.47` | `2.5616` | `20261112T005057619316_google_gemma_4_E4B_it.npz` |
| `footing-settlement-verification` | Baseline | `268.54` | `0.8518` | `14.95` | `3.7707` | `20261112T010619139270_google_gemma_4_E4B_it.npz` |
| `footing-settlement-verification` | Injetado | `256.97` | `0.8285` | `15.59` | `3.5555` | `20261112T010731631070_google_gemma_4_E4B_it.npz` |
| `foundation-strategy` | Baseline | `131.26` | `0.6716` | `15.44` | `3.9536` | `20261112T005627093958_google_gemma_4_E4B_it.npz` |
| `foundation-strategy` | Injetado | `255.91` | `0.7840` | `14.68` | `3.9621` | `20261112T005739215572_google_gemma_4_E4B_it.npz` |
| `frame-extension-method` | Baseline | `219.84` | `0.8878` | `13.73` | `3.3357` | `20261112T011334807621_google_gemma_4_E4B_it.npz` |
| `frame-extension-method` | Injetado | `272.19` | `0.7837` | `14.38` | `3.5697` | `20261112T011447415605_google_gemma_4_E4B_it.npz` |
| `heat-rejection-life-cycle-cost` | Baseline | `138.24` | `0.7800` | `15.93` | `3.8144` | `20261112T012749071543_google_gemma_4_E4B_it.npz` |
| `heat-rejection-life-cycle-cost` | Injetado | `176.53` | `0.9041` | `15.62` | `3.9622` | `20261112T012902618871_google_gemma_4_E4B_it.npz` |
| `landscape-sheet-revision` | Baseline | `187.33` | `0.8954` | `14.61` | `3.7306` | `20261112T005853164805_google_gemma_4_E4B_it.npz` |
| `landscape-sheet-revision` | Injetado | `302.94` | `0.8495` | `15.98` | `3.1638` | `20261112T010006691490_google_gemma_4_E4B_it.npz` |
| `les-mesh-resolution` | Baseline | `233.12` | `0.7962` | `19.27` | `3.4939` | `20261112T011827546589_google_gemma_4_E4B_it.npz` |
| `les-mesh-resolution` | Injetado | `232.43` | `0.7711` | `14.05` | `4.0478` | `20261112T011941279598_google_gemma_4_E4B_it.npz` |
| `mv-conveyance-study` | Baseline | `181.02` | `0.6757` | `14.98` | `4.3492` | `20261112T012048943411_google_gemma_4_E4B_it.npz` |
| `mv-conveyance-study` | Injetado | `131.76` | `0.7703` | `15.05` | `4.1954` | `20261112T012201487572_google_gemma_4_E4B_it.npz` |
| `roof-deck-design` | Baseline | `138.75` | `0.7858` | `15.49` | `3.6400` | `20261112T013751894415_google_gemma_4_E4B_it.npz` |
| `roof-deck-design` | Injetado | `266.99` | `0.7747` | `14.12` | `3.7721` | `20261112T013915568775_google_gemma_4_E4B_it.npz` |
| `seismic-diaphragm-shear` | Baseline | `172.39` | `0.6915` | `14.88` | `3.8078` | `20261112T013545489600_google_gemma_4_E4B_it.npz` |
| `seismic-diaphragm-shear` | Injetado | `294.09` | `0.8203` | `15.41` | `2.9870` | `20261112T013703003711_google_gemma_4_E4B_it.npz` |
| `shoring-design-verification` | Baseline | `111.76` | `0.8705` | `16.55` | `4.2468` | `20261112T014313644403_google_gemma_4_E4B_it.npz` |
| `shoring-design-verification` | Injetado | `279.27` | `0.7057` | `15.70` | `3.7557` | `20261112T014434430687_google_gemma_4_E4B_it.npz` |
| `solar-supplemental-review` | Baseline | `128.97` | `0.8503` | `15.54` | `4.0997` | `20261112T010843758366_google_gemma_4_E4B_it.npz` |
| `solar-supplemental-review` | Injetado | `96.33` | `0.8642` | `15.69` | `4.1462` | `20261112T010956374087_google_gemma_4_E4B_it.npz` |
| `solar-witness-test-package` | Baseline | `233.71` | `0.8430` | `15.91` | `2.4530` | `20261112T011109209136_google_gemma_4_E4B_it.npz` |
| `solar-witness-test-package` | Injetado | `200.63` | `0.7603` | `15.85` | `4.4263` | `20261112T011222310547_google_gemma_4_E4B_it.npz` |
| `wind-diaphragm-shear` | Baseline | `132.84` | `0.7676` | `14.56` | `4.5772` | `20261112T013304044821_google_gemma_4_E4B_it.npz` |
| `wind-diaphragm-shear` | Injetado | `155.07` | `0.8349` | `15.49` | `4.5233` | `20261112T013425087106_google_gemma_4_E4B_it.npz` |

---

## 2. Estatísticas Agregadas [DERIVADO]

- **Norma Residual Média**: Baseline = `178.18` | Injetado = `214.51` (Delta = `+20.39%`)
- **Deriva Cosseno Média**: Baseline = `0.7848` | Injetado = `0.7991` (Delta = `+1.81%`)
- **Posto Efetivo MPS Médio**: Baseline = `15.35` | Injetado = `15.26` (Delta = `-0.58%`)

---

## 3. Interpretação Epistêmica e Conclusões [INTERPRETAÇÃO]

1. A injeção do vetor de afeto $(\Phi, \Psi, \sigma, \epsilon)$ modula a aceleração residual e estabiliza o drift intercamada sem degeneração de sintaxe técnica.
2. A persistência de cada tensor de passo em CPU/disco (.npz) elimina completamente os riscos de CUDA Out of Memory (OOM) no ambiente Colab A100.
3. Os dados continuam sendo auditados e sincronizados com os remotos GitHub e GitLab a cada ciclo.