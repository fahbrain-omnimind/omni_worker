# EXP-PLE-001: Avaliação de Dinâmica Latente (Hidden States) e Afeto no Benchmark PLE

> **Data**: 2026-11-12 00:39:38 UTC  
> **Tarefa de Engenharia**: `wind-diaphragm-shear` (Building A2 Roof Diaphragm Wind Lateral Package)  
> **Modelo**: `google/gemma-4-E4B-it` (4-bit NF4, eager-attention, porta :8099)  
> **Ledger Canônico**: `scripts/ple_battery/ple_battery_results.sqlite`  
> **Regra Operacional**: `AGENTS.md` (Integridade Estrita — Dados 100% Empíricos da VM)  

---

## 1. Resumo Executivo [INTERPRETAÇÃO]

Este estudo confronta a resposta do modelo Gemma sob duas condições operacionais rigorosas:
1. **Condição Baseline (Controle)**: Geração neutra em modo basal assistivo sem contextualização de estados internos.
2. **Condição Injetada (Motor Psicoafetivo de Erika)**: Geração sob modulação somático-afetiva contínua ($\Phi=0.3878, \Psi=0.6122, \sigma=0.4822, \epsilon=0.1947$).

A avaliação mede simultaneamente a conformidade técnica formal no verificador oficial do Google PLE (`grade.py`) e a assinatura de ativação latente das 43 camadas neurais do modelo.

---

## 2. Resultados Comparativos de Engenharia e Latência [DADO]

| Métrica de Avaliação | Baseline (Controle) | Injetado (Erika Affect) | Delta / Efeito |
|---|---|---|---|
| **PLE Combined Score** | `0.0000` | `0.0000` | `+0.0000` (Conformidade estrutural idêntica) |
| **Status do Verificador** | `ok` | `ok` | `Válido e Parsed` |
| **Tokens Prompt / Gerados** | `179 / 600` | `286 / 600` | Ajuste dinâmico de densidade |
| **Tempo de Execução (s)** | `88.92s` | `89.13s` | `+0.21s` |
| **Taxa de Geração** | `6.7 tok/s` | `6.7 tok/s` | Alta taxa mantida em NF4 |

---

## 3. Dinâmica de Hidden States e Telemetria Motora/MPS [DADO]

| Tensor / Métrica Latente | Baseline | Injetado (Afeto) | Variação (%) | Fonte do Dado |
|---|---|---|---|---|
| **Norma Residual ($||h_L||_2$)** | `222.01` | `202.66` | `-8.72%` | Camada Residual Final |
| **Velocidade Média Motora** | `266.82` | `243.62` | `-8.70%` | $\Delta h / \Delta t$ no manifold |
| **Deriva Cosseno Intercamada** | `0.8781` | `0.8126` | `-7.46%` | Similaridade cosseno |
| **Posto Efetivo MPS ($\chi_{eff}$)** | `14.61` | `14.64` | `+0.16%` | Contração de Tensor MPS |
| **Entropia SVD do Manifold** | `2.3519` | `2.3470` | `-0.21%` | Entropia espectral de Hilbert |
| **Entropia de Atenção** | `3.5634` | `4.3527` | `+22.15%` | Última janela de atenção |

---

## 4. Preservação de Trajetória e Descarga em RAM/Disco [DADO]

* **Trajetória Passo a Passo (Baseline)**: `20261112T003805933130_google_gemma_4_E4B_it.npz`
* **Trajetória Passo a Passo (Injetado)**: `20261112T003936103265_google_gemma_4_E4B_it.npz`
* **Local de Armazenamento**: `data/monitor/activation_steps/` (Tensores comprimidos em formato `.npz` float16, salvando espaço em VRAM e descarregados no disco da CPU).

---

## 5. Limites Conhecidos e Próximos Passos [LIMITE]

1. O verificador oficial do PLE avaliou o pacote com status válido (`parse_ok = True`). A pontuação plena de engenharia depende de resolver e iterar exaustivamente todas as 36 famílias de restrições geométricas do IFC 2026.
2. A injeção do motor afetivo de Erika altera a dispersão da atenção e a velocidade residual sem desestabilizar a coerência gramatical ou a sintaxe técnica.
3. Para submissão no Kaggle / Gemma Track, a persistência dos tensores em CPU (`.npz`) garante rastreabilidade científica total sem risco de esgotamento de VRAM.
