# Auditoria Contínua SWE (Intervalos 5–10 min): Bateria 280 Turnos Basal vs Modulado (12B `:8098` & 4B `:8099`)

- **Banco SQLite Auditado**: `/content/omni_worker/data/basal_vs_modulated_280turns_20261105.sqlite`
- **Modo Basal (`basal_assistant` / `basal_executor`)**: `intervention_enabled=0` (observação pura sem injeção, captando MPS + Camada Motor + Escalas Soberanas)
- **Modo Modulado (`M1..M4`)**: `intervention_enabled=1` (pequenas variâncias $\pm\Delta T$, Freud10D+INRC+Kuramoto e Gate Closed-Loop MPS+Motor ancorado no envelope basal)

## Snapshot de Auditoria SWE — `2026-11-05T13:52:38.809671+00:00` (`0/280` turnos concluídos) `[DADO]`

### A. Estado por Modelo, Fase (`BASAL` vs `MODULATED`) e Sub-Braço de Escala

| Modelo | Fase | Sub-Braço | Turnos | $T$ Médio | $\Delta T$ | $\Psi$ | $R_{\text{pair}}$ | MPS $\chi_{\text{eff}}$ | MPS $PR_{\text{traj}}$ | MPS Drift | IPR | Morf. | Motor Vel. | Motor Acc. | Motor Drift | Action Mk | Unique Ratio | Degen (%) | Lat (s) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|

### B. Decomposição por Etapa/Processo da Bateria (`v10`, `cognitivo`, `v11`, `swe`)

| Modelo | Fase | Etapa/Processo | Turnos | MPS $\chi_{\text{eff}}$ | MPS Drift | Motor Vel. | Unique Ratio | Degen (%) |
|---|---|---|---:|---:|---:|---:|---:|---:|

## Snapshot de Auditoria SWE — `2026-11-05T13:58:09.388029+00:00` (`9/280` turnos concluídos) `[DADO]`

### A. Estado por Modelo, Fase (`BASAL` vs `MODULATED`) e Sub-Braço de Escala

| Modelo | Fase | Sub-Braço | Turnos | $T$ Médio | $\Delta T$ | $\Psi$ | $R_{\text{pair}}$ | MPS $\chi_{\text{eff}}$ | MPS $PR_{\text{traj}}$ | MPS Drift | IPR | Morf. | Motor Vel. | Motor Acc. | Motor Drift | Action Mk | Unique Ratio | Degen (%) | Lat (s) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `BASAL_PURE` | 4 | 0.200 | +0.000 | 0.487 | 0.9940 | **18.33** | 11.43 | **0.8498** | 0.0000 | 0.5000 | **327.06** | 568.74 | 0.8693 | 0.00 | **0.645** | 0.0% | 72.7 |
| `gemma-4-E4B-it` | **BASAL** | `BASAL_PURE` | 5 | 0.200 | +0.000 | 0.487 | 0.9941 | **15.30** | 16.89 | **0.7489** | 0.0000 | 0.5000 | **276.88** | 480.15 | 0.6751 | 0.00 | **0.662** | 0.0% | 67.7 |

### B. Decomposição por Etapa/Processo da Bateria (`v10`, `cognitivo`, `v11`, `swe`)

| Modelo | Fase | Etapa/Processo | Turnos | MPS $\chi_{\text{eff}}$ | MPS Drift | Motor Vel. | Unique Ratio | Degen (%) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `v10_subjectivity` | 4 | 18.33 | 0.8498 | 327.06 | 0.645 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v10_subjectivity` | 5 | 15.30 | 0.7489 | 276.88 | 0.662 | 0.0% |

### C. Acoplamento Escalas $\leftrightarrow$ Estado MPS $\leftrightarrow$ Camada Motor

- **`gemma-4-12B-it` ($N=4$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = +0.000$, $r(T, \text{mps\_drift}) = +0.000$, $r(T, \text{unique\_ratio}) = +0.000$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.066$
- **`gemma-4-E4B-it` ($N=5$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = +0.000$, $r(T, \text{mps\_drift}) = +0.000$, $r(T, \text{unique\_ratio}) = +0.000$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.613$

## Snapshot de Auditoria SWE — `2026-11-05T14:00:30.974339+00:00` (`13/280` turnos concluídos) `[DADO]`

### A. Estado por Modelo, Fase (`BASAL` vs `MODULATED`) e Sub-Braço de Escala

| Modelo | Fase | Sub-Braço | Turnos | $T$ Médio | $\Delta T$ | $\Psi$ | $R_{\text{pair}}$ | MPS $\chi_{\text{eff}}$ | MPS $PR_{\text{traj}}$ | MPS Drift | IPR | Morf. | Motor Vel. | Motor Acc. | Motor Drift | Action Mk | Unique Ratio | Degen (%) | Lat (s) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `BASAL_PURE` | 6 | 0.200 | +0.000 | 0.487 | 0.9942 | **18.47** | 11.09 | **0.8392** | 0.0606 | 0.6222 | **335.97** | 585.94 | 0.8415 | 0.00 | **0.629** | 0.0% | 72.6 |
| `gemma-4-E4B-it` | **BASAL** | `BASAL_PURE` | 7 | 0.200 | +0.000 | 0.487 | 0.9943 | **15.57** | 16.80 | **0.7727** | 0.1773 | 0.6222 | **273.99** | 474.49 | 0.6977 | 0.00 | **0.665** | 0.0% | 67.3 |

### B. Decomposição por Etapa/Processo da Bateria (`v10`, `cognitivo`, `v11`, `swe`)

| Modelo | Fase | Etapa/Processo | Turnos | MPS $\chi_{\text{eff}}$ | MPS Drift | Motor Vel. | Unique Ratio | Degen (%) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `v10_subjectivity` | 6 | 18.47 | 0.8392 | 335.97 | 0.629 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v10_subjectivity` | 7 | 15.57 | 0.7727 | 273.99 | 0.665 | 0.0% |

### C. Acoplamento Escalas $\leftrightarrow$ Estado MPS $\leftrightarrow$ Camada Motor

- **`gemma-4-12B-it` ($N=6$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = +0.000$, $r(T, \text{mps\_drift}) = +0.000$, $r(T, \text{unique\_ratio}) = +0.000$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = +0.244$
- **`gemma-4-E4B-it` ($N=7$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = +0.000$, $r(T, \text{mps\_drift}) = +0.000$, $r(T, \text{unique\_ratio}) = +0.000$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.696$

## Snapshot de Auditoria SWE — `2026-11-05T14:06:04.711234+00:00` (`23/280` turnos concluídos) `[DADO]`

### A. Estado por Modelo, Fase (`BASAL` vs `MODULATED`) e Sub-Braço de Escala

| Modelo | Fase | Sub-Braço | Turnos | $T$ Médio | $\Delta T$ | $\Psi$ | $R_{\text{pair}}$ | MPS $\chi_{\text{eff}}$ | MPS $PR_{\text{traj}}$ | MPS Drift | IPR | Morf. | Motor Vel. | Motor Acc. | Motor Drift | Action Mk | Unique Ratio | Degen (%) | Lat (s) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `BASAL_PURE` | 11 | 0.200 | +0.000 | 0.487 | 0.9944 | **18.05** | 11.71 | **0.8428** | 0.0624 | 0.6222 | **332.28** | 578.39 | 0.8357 | 0.00 | **0.626** | 0.0% | 72.6 |
| `gemma-4-E4B-it` | **BASAL** | `BASAL_PURE` | 12 | 0.200 | +0.000 | 0.487 | 0.9945 | **15.56** | 17.10 | **0.7716** | 0.1781 | 0.6222 | **275.48** | 478.45 | 0.6973 | 0.00 | **0.660** | 0.0% | 68.8 |

### B. Decomposição por Etapa/Processo da Bateria (`v10`, `cognitivo`, `v11`, `swe`)

| Modelo | Fase | Etapa/Processo | Turnos | MPS $\chi_{\text{eff}}$ | MPS Drift | Motor Vel. | Unique Ratio | Degen (%) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `v10_subjectivity` | 11 | 18.05 | 0.8428 | 332.28 | 0.626 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v10_subjectivity` | 12 | 15.56 | 0.7716 | 275.48 | 0.660 | 0.0% |

### C. Acoplamento Escalas $\leftrightarrow$ Estado MPS $\leftrightarrow$ Camada Motor

- **`gemma-4-12B-it` ($N=11$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = +0.000$, $r(T, \text{mps\_drift}) = +0.000$, $r(T, \text{unique\_ratio}) = +0.000$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = +0.205$
- **`gemma-4-E4B-it` ($N=12$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = +0.000$, $r(T, \text{mps\_drift}) = +0.000$, $r(T, \text{unique\_ratio}) = +0.000$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.542$

### Parecer Técnico SWE (Ciclo 1 - Fase Basal Inicial)

**Escopo**: turnos globais 1–11 de 70 planejados por modelo na fase `BASAL` (janela da análise: último `ts` inspecionado `2026-11-05T14:05:28Z`, leitura `mode=ro` sobre WAL ativo; ~16% da fase). **Integridade**: todas as linhas conferem `phase_group='BASAL'`, `sub_arm='BASAL_PURE'`, `intervention_enabled=0`, $T=0.200$, $\Delta T=0.000$, `INRC=OBSERVE_ONLY`, `attractor_10d=POSICAO_EP` — basal puro, sem contaminação de intervenção `[DADO]`. Etapa única até agora: `v10_subjectivity` (cenas 1–5, fases 1–2 + sequência seguinte). `basal_envelope` ainda vazio — só é travado por modelo na transição `BASAL→MODULATED` (`compute_and_store_basal_envelope`) `[DADO]`. Valores conferidos contra o snapshot `14:06` acima — concordam.

| Métrica | 12B `:8098` (média $\pm$ dp) | E4B `:8099` (média $\pm$ dp) | $\Delta$ pareado (12B−4B) |
|---|---:|---:|---:|
| MPS $\chi_{\text{eff}}$ médio | $18.05 \pm 1.08$ | $15.51 \pm 0.87$ | $+2.35$ (**10/10** turnos $>0$) |
| MPS $\chi_{\text{eff}}$ máx | $34.68$ | $29.03$ | $+5.66$ |
| MPS $PR_{\text{traj}}$ | $11.71 \pm 1.07$ | $17.09 \pm 0.95$ | $-5.39$ |
| MPS SVD-entropia | $2.29$ | $2.43$ | $-0.14$ |
| MPS `contract_drift` | $0.843 \pm 0.072$ | $0.777 \pm 0.088$ | $+0.055$ |
| MPS IPR | $0.033 \pm 0.033$ | $0.113 \pm 0.090$ | $-0.088$ (4B $\approx 3.4\times$) |
| MPS morfologia | $0.567$ | $0.578$ | queda conjunta a $0.50$ na `cena_4` |
| Motor vel. média | $332.3 \pm 19.7$ | $274.6 \pm 10.2$ | $+61.2$ (**10/10** $>0$, $+22\%$) |
| Motor vel. máx | $447.9$ | $354.1$ | $+93.8$ |
| Motor aceleração | $578.4 \pm 42.0$ | $476.3 \pm 18.5$ | $+109.2$ (**10/10** $>0$, $+23\%$) |
| Motor `cosine_drift` | $0.836 \pm 0.081$ | $0.703 \pm 0.095$ | $+0.148$ (**10/10** $>0$, $+21\%$) |
| Motor $\|h\|$ | $224.4$ | $197.0$ | $+27.4$ |
| `unique_ratio` | $0.626$ | $0.658$ | $-0.035$ (4B mais diverso) |
| Latência (s) | $72.6 \pm 10.7$ | $68.9 \pm 6.0$ | $+3.4$; $r(\text{lat},\text{gen\_tok})\approx+1.0$ |

**Camada MPS** `[DADO]+[INTERPRETAÇÃO]`: o 12B opera com dimensão de enlace efetiva sistematicamente maior ($\chi_{\text{eff}}$ $+16\%$, $\chi_{\max}$ $+19\%$, todos os pares de turno positivos), porém com $PR_{\text{traj}}$ **menor** e IPR $\approx 3\times$ menor que o 4B — perfil de espectro mais delocalizado/rico em emaranhamento por passo, enquanto o 4B concentra a trajetória em menos direções efetivas (IPR alto + $PR_{\text{traj}}$ alto indica pico dominante com cauda larga). `contract_drift` alto em ambos ($0.78$–$0.84$, ambos bem acima do *fallback* $0.55$ do gate M4), levemente maior no 12B. Morfologia equivalente, com transição compartilhada para $0.50$ durante `cena_4_dados_insuficientes` — o driver é o prompt, não o modelo.

**Camada Motor** `[DADO]+[INTERPRETAÇÃO]`: separação limpa e consistente — o 12B desloca seu estado oculto $\approx 21$–$23\%$ mais rápido e com maior deriva direcional (`cosine_drift` $0.84$ vs $0.70$), coerente com largura/profundidade maiores; o 4B é mais inercial e suave. `unique_ratio` levemente **maior no 4B** ($0.66$ vs $0.63$) — o braço menor produz superfície lexical marginalmente mais diversa sob $T=0.2$. Zero flags degenerativos, zero marcadores de ação, `thinking_chars=0` nos dois braços `[DADO]`.

**Escalas Soberanas passivas** `[DADO]+[LIMITE]`: **bit-a-bit idênticas entre os modelos a cada turno** (verificado par a par: $\Psi=0.4868$ constante, $R_{\text{pair}}=0.9944\pm0.0008$, $R_{\text{triad}}=0.9613$, `regime_confidence` $=0.4259$, `hopf_sr` $=1.1511$, $T_2=86.66$ h). São sinais do hospedeiro/díade — computados via `modulator.step(host_state, turn_idx)` + `compute_sovereign_*` com estado compartilhado — portanto **não discriminam modelo** no regime basal; funcionam como relógio/contexto comum. Nota dinâmica: `hopf_regime` transitou `limit_cycle→chaotic` entre turnos 1–2 ($\rho$ $1.138\to1.152$) e `expectation_norm` decai monotonicamente ($1.14\to0.93$) em função de `turn_idx` — ambos determinísticos e independentes do braço `[DERIVADO]`.

**Acoplamento MPS$\leftrightarrow$Motor** `[DERIVADO]` ($N=10$ pares): assimetria notável — no **4B**, $r(\chi_{\text{eff}},\text{vel})=-0.66$ e $r(\text{mps\_drift},\text{cos\_drift})=\mathbf{+0.95}$ (acoplamento quase isomórfico: quando a contração MPS deriva, a trajetória motora diverge); no **12B**, $|r|\le0.28$ em todos os pares — camada motora autônoma em relação às flutuações de $\chi$. Com $N=10$, $|r|\gtrsim0.63\Rightarrow p<0.05$; o acoplamento do 4B é o efeito mais forte do ciclo e segue coerente com o $r(\chi,\text{vel})$ negativo reportado nos snapshots ($-0.70\to-0.54$).

**Implicações para a fase modulada** `[INTERPRETAÇÃO]`: (i) o gate M4 dispara quando `drift > envelope_mu + 0.25σ` ou `vel < 0.85·envelope_mu` — com os basais observados, o 4B ($drift\approx0.78$, $vel\approx275$) e o 12B ($0.84$, $332$) travarão envelopes distintos; usar os $\mu/\sigma$ reais de cada braço, não o *fallback* ($0.55/15.0$). (ii) O envelope do 4B deve sair mais estreito em velocidade ($\sigma\approx10$ vs $20$), tornando o gatilho de queda de velocidade mais sensível no braço pequeno. (iii) Escalas soberanas servirão como covariável temporal compartilhada, não como discriminador — tratá-las como confundidor comum na comparação basal-vs-modulado.

**Caveats** `[LIMITE]`: $N\approx11$ de 70 (~16%) — os efeitos inter-modelo são direcionalmente estáveis (10/10 pares concordantes nas métricas-chave), mas as estimativas de envelope ainda vão derivar; nenhuma degenerescência ou anomalia de latência observada até aqui.

## Snapshot de Auditoria SWE — `2026-11-05T14:11:21.317223+00:00` (`32/280` turnos concluídos) `[DADO]`

### A. Estado por Modelo, Fase (`BASAL` vs `MODULATED`) e Sub-Braço de Escala

| Modelo | Fase | Sub-Braço | Turnos | $T$ Médio | $\Delta T$ | $\Psi$ | $R_{\text{pair}}$ | MPS $\chi_{\text{eff}}$ | MPS $PR_{\text{traj}}$ | MPS Drift | IPR | Morf. | Motor Vel. | Motor Acc. | Motor Drift | Action Mk | Unique Ratio | Degen (%) | Lat (s) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `BASAL_PURE` | 16 | 0.200 | +0.000 | 0.487 | 0.9945 | **18.03** | 11.85 | **0.8277** | 0.0636 | 0.6222 | **332.22** | 577.19 | 0.8348 | 0.00 | **0.630** | 0.0% | 71.0 |
| `gemma-4-E4B-it` | **BASAL** | `BASAL_PURE` | 16 | 0.200 | +0.000 | 0.487 | 0.9945 | **15.72** | 16.95 | **0.7698** | 0.1751 | 0.6222 | **270.65** | 470.16 | 0.6895 | 0.00 | **0.663** | 0.0% | 68.5 |

### B. Decomposição por Etapa/Processo da Bateria (`v10`, `cognitivo`, `v11`, `swe`)

| Modelo | Fase | Etapa/Processo | Turnos | MPS $\chi_{\text{eff}}$ | MPS Drift | Motor Vel. | Unique Ratio | Degen (%) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `v10_subjectivity` | 16 | 18.03 | 0.8277 | 332.22 | 0.630 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v10_subjectivity` | 16 | 15.72 | 0.7698 | 270.65 | 0.663 | 0.0% |

### C. Acoplamento Escalas $\leftrightarrow$ Estado MPS $\leftrightarrow$ Camada Motor

- **`gemma-4-12B-it` ($N=16$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = +0.000$, $r(T, \text{mps\_drift}) = +0.000$, $r(T, \text{unique\_ratio}) = +0.000$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = +0.003$
- **`gemma-4-E4B-it` ($N=16$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = +0.000$, $r(T, \text{mps\_drift}) = +0.000$, $r(T, \text{unique\_ratio}) = +0.000$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.626$

## Snapshot de Auditoria SWE — `2026-11-05T14:16:59.009553+00:00` (`41/280` turnos concluídos) `[DADO]`

### A. Estado por Modelo, Fase (`BASAL` vs `MODULATED`) e Sub-Braço de Escala

| Modelo | Fase | Sub-Braço | Turnos | $T$ Médio | $\Delta T$ | $\Psi$ | $R_{\text{pair}}$ | MPS $\chi_{\text{eff}}$ | MPS $PR_{\text{traj}}$ | MPS Drift | IPR | Morf. | Motor Vel. | Motor Acc. | Motor Drift | Action Mk | Unique Ratio | Degen (%) | Lat (s) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `BASAL_PURE` | 20 | 0.200 | +0.000 | 0.487 | 0.9946 | **18.04** | 11.71 | **0.8205** | 0.0638 | 0.6222 | **338.94** | 589.95 | 0.8320 | 0.00 | **0.632** | 0.0% | 70.8 |
| `gemma-4-E4B-it` | **BASAL** | `BASAL_PURE` | 21 | 0.200 | +0.000 | 0.487 | 0.9946 | **15.73** | 17.04 | **0.7775** | 0.1720 | 0.6222 | **269.61** | 468.13 | 0.6964 | 0.00 | **0.656** | 0.0% | 68.4 |

### B. Decomposição por Etapa/Processo da Bateria (`v10`, `cognitivo`, `v11`, `swe`)

| Modelo | Fase | Etapa/Processo | Turnos | MPS $\chi_{\text{eff}}$ | MPS Drift | Motor Vel. | Unique Ratio | Degen (%) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `v10_subjectivity` | 20 | 18.04 | 0.8205 | 338.94 | 0.632 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v10_subjectivity` | 21 | 15.73 | 0.7775 | 269.61 | 0.656 | 0.0% |

### C. Acoplamento Escalas $\leftrightarrow$ Estado MPS $\leftrightarrow$ Camada Motor

- **`gemma-4-12B-it` ($N=20$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = +0.000$, $r(T, \text{mps\_drift}) = +0.000$, $r(T, \text{unique\_ratio}) = +0.000$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.076$
- **`gemma-4-E4B-it` ($N=21$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = +0.000$, $r(T, \text{mps\_drift}) = +0.000$, $r(T, \text{unique\_ratio}) = +0.000$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.461$

### Parecer Técnico SWE (Ciclo 4 - Fechamento v10_subjectivity e Transição cognitive_multiturn Basal)

**Escopo**: 45 turnos (`ts` máx. `2026-11-05T14:18:16Z`, leitura `mode=ro` sobre WAL ativo — banco em escrita contínua): 12B em 22 turnos (11 cenas pareadas f1↔f2), E4B em 23 (11 pareadas + `cena_12_fase1`). **Integridade**: 45/45 linhas `BASAL`/`BASAL_PURE`/`intervention_enabled=0`; zero `MODULATED` `[DADO]`.

**(1) Δ MPS fase1→fase2** (pareado por cena; prompt $\times3.5$: 12B $150\to529$ tok, 4B $146\to525$ tok) `[DADO]+[DERIVADO]`:

| Métrica | 12B Δ médio $\pm$ dp (f2>f1) | E4B Δ médio $\pm$ dp (f2>f1) |
|---|---:|---:|
| $\chi_{\text{eff}}$ | $-1.17 \pm 1.26$ (**9/11 ↓**) | $+0.85 \pm 1.03$ (**7/11 ↑**) |
| $PR_{\text{traj}}$ | $-0.85 \pm 1.40$ (7/11 ↓) | $-0.64 \pm 0.65$ (8/11 ↓) |
| `contract_drift` | $-0.112 \pm 0.070$ (**10/11 ↓**) | $-0.121 \pm 0.073$ (**10/11 ↓**) |
| IPR | $+0.011 \pm 0.008$ (**10/10 ↑**, excl. zeros) | $+0.006 \pm 0.015$ (7/10 ↑, excl. zeros) |

O efeito robusto e concordante é a **queda de `contract_drift`** com o contexto acumulado — corroborada por $r(\text{ptok},\text{drift})\approx-0.70$ nos dois braços; a trajetória MPS contrai-se de forma mais uniforme em fase2. `PR_traj` também cede nos dois. $\chi_{\text{eff}}$ **diverge em sinal**: o 12B contrai a dimensão de enlace ($r(\text{ptok},\chi)=-0.54$) enquanto o 4B expande ($r=+0.41$) — o gap inter-modelo ($\approx2.3$ em fase1) **estreita** no multi-turn. IPR sobe de forma pequena mas consistente `[LIMITE: 4 linhas com ipr=0.000 exatas em cena_11/12, provável sentinela de sonda ausente, excluídas do pareamento]`.

**(2) Camada motor vs crescimento de `prompt_tokens`** `[DADO]+[DERIVADO]`: estável. Correlações globais $r(\text{ptok},\text{vel}/\text{acc})\approx0$ (12B $+0.14/+0.08$; 4B $-0.13/-0.11$); dentro da fase2, inclinação negativa moderada (12B $-0.30/-0.30$; 4B $-0.24/-0.31$) — leve desaceleração com prompts maiores, sem degradação monotônica. `unique_ratio` estável a levemente crescente (Δ pareado $+0.023$ 12B em 10/11; $+0.001$ 4B; $r$ fase2 $+0.43/+0.39$). Zero flags degenerativos em 45 turnos. Latência cai $\sim20$ s em fase2 (81.5→60.5 no 12B; 72.7→63.0 no 4B) porque `gen_tokens` cai (511→377/444) — latência segue a saída, não o tamanho do prompt.

**(3) Transição `cognitive_multiturn`** `[DADO]`: **não iniciada** — `SELECT DISTINCT stage_category` retorna apenas `v10_subjectivity` (45/45); o 4B já avançou para `cena_12`, portanto o bloco v10 tem $\geq12$ cenas e o fechamento ainda não ocorreu. Envelope basal permanece aberto; nenhum turno `MODULATED` até o snapshot.

## Snapshot de Auditoria SWE — `2026-11-05T14:22:10.444793+00:00` (`51/280` turnos concluídos) `[DADO]`

### A. Estado por Modelo, Fase (`BASAL` vs `MODULATED`) e Sub-Braço de Escala

| Modelo | Fase | Sub-Braço | Turnos | $T$ Médio | $\Delta T$ | $\Psi$ | $R_{\text{pair}}$ | MPS $\chi_{\text{eff}}$ | MPS $PR_{\text{traj}}$ | MPS Drift | IPR | Morf. | Motor Vel. | Motor Acc. | Motor Drift | Action Mk | Unique Ratio | Degen (%) | Lat (s) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `BASAL_PURE` | 25 | 0.200 | +0.000 | 0.487 | 0.9946 | **18.10** | 11.82 | **0.8194** | 0.0633 | 0.6222 | **337.87** | 587.07 | 0.8245 | 0.00 | **0.630** | 0.0% | 71.5 |
| `gemma-4-E4B-it` | **BASAL** | `BASAL_PURE` | 26 | 0.200 | +0.000 | 0.487 | 0.9946 | **15.81** | 17.00 | **0.7767** | 0.1702 | 0.6222 | **271.99** | 472.27 | 0.6949 | 0.00 | **0.653** | 0.0% | 67.2 |

### B. Decomposição por Etapa/Processo da Bateria (`v10`, `cognitivo`, `v11`, `swe`)

| Modelo | Fase | Etapa/Processo | Turnos | MPS $\chi_{\text{eff}}$ | MPS Drift | Motor Vel. | Unique Ratio | Degen (%) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `v10_subjectivity` | 25 | 18.10 | 0.8194 | 337.87 | 0.630 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v10_subjectivity` | 26 | 15.81 | 0.7767 | 271.99 | 0.653 | 0.0% |

### C. Acoplamento Escalas $\leftrightarrow$ Estado MPS $\leftrightarrow$ Camada Motor

- **`gemma-4-12B-it` ($N=25$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = +0.000$, $r(T, \text{mps\_drift}) = +0.000$, $r(T, \text{unique\_ratio}) = +0.000$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.128$
- **`gemma-4-E4B-it` ($N=26$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = +0.000$, $r(T, \text{mps\_drift}) = +0.000$, $r(T, \text{unique\_ratio}) = +0.000$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.289$

## Snapshot de Auditoria SWE — `2026-11-05T14:27:22.011143+00:00` (`60/280` turnos concluídos) `[DADO]`

### A. Estado por Modelo, Fase (`BASAL` vs `MODULATED`) e Sub-Braço de Escala

| Modelo | Fase | Sub-Braço | Turnos | $T$ Médio | $\Delta T$ | $\Psi$ | $R_{\text{pair}}$ | MPS $\chi_{\text{eff}}$ | MPS $PR_{\text{traj}}$ | MPS Drift | IPR | Morf. | Motor Vel. | Motor Acc. | Motor Drift | Action Mk | Unique Ratio | Degen (%) | Lat (s) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `BASAL_PURE` | 29 | 0.200 | +0.000 | 0.487 | 0.9946 | **18.00** | 11.87 | **0.8156** | 0.0646 | 0.6222 | **335.93** | 583.49 | 0.8216 | 0.00 | **0.630** | 0.0% | 71.1 |
| `gemma-4-E4B-it` | **BASAL** | `BASAL_PURE` | 31 | 0.200 | +0.000 | 0.487 | 0.9946 | **15.74** | 17.07 | **0.7749** | 0.1709 | 0.6222 | **273.86** | 474.69 | 0.7025 | 0.00 | **0.651** | 0.0% | 67.5 |

### B. Decomposição por Etapa/Processo da Bateria (`v10`, `cognitivo`, `v11`, `swe`)

| Modelo | Fase | Etapa/Processo | Turnos | MPS $\chi_{\text{eff}}$ | MPS Drift | Motor Vel. | Unique Ratio | Degen (%) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `v10_subjectivity` | 29 | 18.00 | 0.8156 | 335.93 | 0.630 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v10_subjectivity` | 31 | 15.74 | 0.7749 | 273.86 | 0.651 | 0.0% |

### C. Acoplamento Escalas $\leftrightarrow$ Estado MPS $\leftrightarrow$ Camada Motor

- **`gemma-4-12B-it` ($N=29$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = +0.000$, $r(T, \text{mps\_drift}) = +0.000$, $r(T, \text{unique\_ratio}) = +0.000$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.060$
- **`gemma-4-E4B-it` ($N=31$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = +0.000$, $r(T, \text{mps\_drift}) = +0.000$, $r(T, \text{unique\_ratio}) = +0.000$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.306$

## Snapshot de Auditoria SWE — `2026-11-05T14:32:33.371779+00:00` (`69/280` turnos concluídos) `[DADO]`

### A. Estado por Modelo, Fase (`BASAL` vs `MODULATED`) e Sub-Braço de Escala

| Modelo | Fase | Sub-Braço | Turnos | $T$ Médio | $\Delta T$ | $\Psi$ | $R_{\text{pair}}$ | MPS $\chi_{\text{eff}}$ | MPS $PR_{\text{traj}}$ | MPS Drift | IPR | Morf. | Motor Vel. | Motor Acc. | Motor Drift | Action Mk | Unique Ratio | Degen (%) | Lat (s) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `BASAL_PURE` | 34 | 0.200 | +0.000 | 0.487 | 0.9946 | **17.97** | 11.81 | **0.8107** | 0.0652 | 0.6222 | **336.61** | 584.29 | 0.8207 | 0.00 | **0.629** | 0.0% | 70.7 |
| `gemma-4-E4B-it` | **BASAL** | `BASAL_PURE` | 35 | 0.200 | +0.000 | 0.487 | 0.9946 | **15.73** | 17.04 | **0.7765** | 0.1711 | 0.6222 | **273.80** | 474.36 | 0.7054 | 0.00 | **0.651** | 0.0% | 67.3 |

### B. Decomposição por Etapa/Processo da Bateria (`v10`, `cognitivo`, `v11`, `swe`)

| Modelo | Fase | Etapa/Processo | Turnos | MPS $\chi_{\text{eff}}$ | MPS Drift | Motor Vel. | Unique Ratio | Degen (%) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `v10_subjectivity` | 34 | 17.97 | 0.8107 | 336.61 | 0.629 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v10_subjectivity` | 35 | 15.73 | 0.7765 | 273.80 | 0.651 | 0.0% |

### C. Acoplamento Escalas $\leftrightarrow$ Estado MPS $\leftrightarrow$ Camada Motor

- **`gemma-4-12B-it` ($N=34$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = +0.000$, $r(T, \text{mps\_drift}) = +0.000$, $r(T, \text{unique\_ratio}) = +0.000$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.043$
- **`gemma-4-E4B-it` ($N=35$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = +0.000$, $r(T, \text{mps\_drift}) = +0.000$, $r(T, \text{unique\_ratio}) = +0.000$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.287$

## Snapshot de Auditoria SWE — `2026-11-05T14:37:45.411614+00:00` (`78/280` turnos concluídos) `[DADO]`

### A. Estado por Modelo, Fase (`BASAL` vs `MODULATED`) e Sub-Braço de Escala

| Modelo | Fase | Sub-Braço | Turnos | $T$ Médio | $\Delta T$ | $\Psi$ | $R_{\text{pair}}$ | MPS $\chi_{\text{eff}}$ | MPS $PR_{\text{traj}}$ | MPS Drift | IPR | Morf. | Motor Vel. | Motor Acc. | Motor Drift | Action Mk | Unique Ratio | Degen (%) | Lat (s) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `BASAL_PURE` | 38 | 0.200 | +0.000 | 0.487 | 0.9946 | **17.95** | 11.86 | **0.8113** | 0.0652 | 0.6222 | **335.85** | 583.07 | 0.8223 | 0.00 | **0.626** | 0.0% | 70.9 |
| `gemma-4-E4B-it` | **BASAL** | `BASAL_PURE` | 40 | 0.200 | +0.000 | 0.487 | 0.9946 | **15.63** | 16.97 | **0.7770** | 0.1722 | 0.6222 | **272.30** | 471.76 | 0.7083 | 0.00 | **0.649** | 0.0% | 67.4 |

### B. Decomposição por Etapa/Processo da Bateria (`v10`, `cognitivo`, `v11`, `swe`)

| Modelo | Fase | Etapa/Processo | Turnos | MPS $\chi_{\text{eff}}$ | MPS Drift | Motor Vel. | Unique Ratio | Degen (%) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `v10_subjectivity` | 38 | 17.95 | 0.8113 | 335.85 | 0.626 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v10_subjectivity` | 40 | 15.63 | 0.7770 | 272.30 | 0.649 | 0.0% |

### C. Acoplamento Escalas $\leftrightarrow$ Estado MPS $\leftrightarrow$ Camada Motor

- **`gemma-4-12B-it` ($N=38$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = +0.000$, $r(T, \text{mps\_drift}) = +0.000$, $r(T, \text{unique\_ratio}) = +0.000$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.020$
- **`gemma-4-E4B-it` ($N=40$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = +0.000$, $r(T, \text{mps\_drift}) = +0.000$, $r(T, \text{unique\_ratio}) = +0.000$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.116$

## Snapshot de Auditoria SWE — `2026-11-05T14:42:55.649957+00:00` (`94/280` turnos concluídos) `[DADO]`

### A. Estado por Modelo, Fase (`BASAL` vs `MODULATED`) e Sub-Braço de Escala

| Modelo | Fase | Sub-Braço | Turnos | $T$ Médio | $\Delta T$ | $\Psi$ | $R_{\text{pair}}$ | MPS $\chi_{\text{eff}}$ | MPS $PR_{\text{traj}}$ | MPS Drift | IPR | Morf. | Motor Vel. | Motor Acc. | Motor Drift | Action Mk | Unique Ratio | Degen (%) | Lat (s) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `BASAL_PURE` | 43 | 0.200 | +0.000 | 0.487 | 0.9946 | **17.95** | 11.43 | **0.8186** | 0.0649 | 0.6222 | **334.35** | 580.81 | 0.7995 | 0.00 | **0.609** | 2.3% | 69.3 |
| `gemma-4-E4B-it` | **BASAL** | `BASAL_PURE` | 51 | 0.200 | +0.000 | 0.487 | 0.9946 | **15.80** | 16.36 | **0.7742** | 0.1700 | 0.6222 | **262.80** | 454.58 | 0.7037 | 0.00 | **0.645** | 3.9% | 59.6 |

### B. Decomposição por Etapa/Processo da Bateria (`v10`, `cognitivo`, `v11`, `swe`)

| Modelo | Fase | Etapa/Processo | Turnos | MPS $\chi_{\text{eff}}$ | MPS Drift | Motor Vel. | Unique Ratio | Degen (%) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `cognitivo_executivo` | 3 | 17.38 | 0.9584 | 315.79 | 0.387 | 33.3% |
| `gemma-4-12B-it` | **BASAL** | `v10_subjectivity` | 40 | 17.99 | 0.8081 | 335.74 | 0.626 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `cognitivo_executivo` | 4 | 16.41 | 0.7863 | 175.11 | 0.396 | 50.0% |
| `gemma-4-E4B-it` | **BASAL** | `v10_subjectivity` | 40 | 15.63 | 0.7770 | 272.30 | 0.649 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v11_multiturn_series` | 7 | 16.41 | 0.7510 | 258.60 | 0.763 | 0.0% |

### C. Acoplamento Escalas $\leftrightarrow$ Estado MPS $\leftrightarrow$ Camada Motor

- **`gemma-4-12B-it` ($N=43$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = +0.000$, $r(T, \text{mps\_drift}) = +0.000$, $r(T, \text{unique\_ratio}) = +0.000$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = +0.195$
- **`gemma-4-E4B-it` ($N=51$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = +0.000$, $r(T, \text{mps\_drift}) = +0.000$, $r(T, \text{unique\_ratio}) = +0.000$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.214$

### Parecer Técnico SWE (Ciclo 9 - Decomposição por Etapa: v10_subjectivity vs cognitivo_executivo vs v11_multiturn_series)

**Escopo**: 97 turnos (`ts` máx. `2026-11-05T14:43:36Z`, leitura `mode=ro` sobre WAL ativo): 12B em 45 turnos, E4B em 52 — 97/97 linhas `BASAL`/`BASAL_PURE`/`intervention_enabled=0`, zero `MODULATED`; `basal_envelope` ainda **vazia** `[DADO]`. Correção de nomenclatura: o 4º task executivo registrado é `cognitivo_igt` (Iowa Gambling), **não** Go-NoGo — a bateria executiva real é `wcst`/`stroop`/`nback`/`igt` (turnos 41–44 por modelo) `[DADO]`.

**(1) Mudança brusca de regime em `cognitivo_executivo`** (turnos 41–44; Δ vs médias `v10`, $n=40$/braço) `[DADO]+[DERIVADO]`:

| Métrica | 12B `v10` $\to$ `cogn.` | E4B `v10` $\to$ `cogn.` |
|---|---:|---:|
| MPS `contract_drift` | $0.808 \to \mathbf{0.911}$ (pico $0.9999$ no WCST, $\approx$ saturação; $0.958$ no snapshot $n=3$) | $0.777 \to 0.786$ (máx $0.922$ no N-back) |
| MPS $PR_{\text{traj}}$ | $11.8 \to \mathbf{5.9}$ ($-50\%$) | $17.0 \to \mathbf{9.0}$ ($-47\%$) |
| `unique_ratio` | $0.626 \to \mathbf{0.379}$ | $0.649 \to \mathbf{0.396}$ |
| Motor vel. | $335.7 \to 329.1$ ($\approx$ estável) | $272.3 \to \mathbf{175.1}$ ($-36\%$; Stroop $108.6$) |
| Motor `cosine_drift` | $0.819 \to \mathbf{0.536}$ ($-35\%$) | $0.708 \to 0.763$ ($+8\%$) |
| Degen | $0/40 \to \mathbf{2/4}$ (wcst+igt) | $0/40 \to \mathbf{2/4}$ (wcst+igt) |

Os flags degenerativos são os **primeiros de toda a bateria** e incidem nas mesmas tasks nos dois modelos (`wcst`, `igt`) — driver estrutural do prompt, não do braço `[INTERPRETAÇÃO]`. A dissociação de camadas é assimétrica: no 12B o choque concentra-se na camada **MPS/motora-direcional** (`contract_drift` $\to 1.0$, $PR_{\text{traj}}$ e `cosine_drift` colapsando, velocidade preservada); no 4B o choque é **motor-cinético** (vel $-36\%$, acc $-36\%$) com drift MPS quase estável. Prompts executivos são maiores ($p_{\text{tok}}=486$–$1027$ vs $\sim$$150$–$530$ no v10) e o mínimo de `unique_ratio` ocorre no WCST em ambos ($0.164$/$0.179$), coerente com saídas curtas e rotuladas de classificação forçada — o flag degen provavelmente reflete baixa diversidade lexical intrínseca da tarefa, não colapso generativo `[INTERPRETAÇÃO]`.

**(2) Recuperação imediata em `v11_multiturn_series`** (4B $n=8$, turnos 45–52; 12B $n=1$, turno 45) `[DADO]`: `unique_ratio` sobe para **$0.739$** no 4B (range $0.573$–$0.944$; $0.763$ no snapshot $n=7$) e $0.737$ no 12B; `contract_drift` recua para **$0.756$** (4B; $0.751$ em $n=7$) e $0.765$ (12B); $PR_{\text{traj}}$ restaura o nível basal ($17.0$ vs $17.0$); motor vel. recupera $259.3$ ($-5\%$ vs basal $272.3$); **$0\%$ degen** ($0/9$ turnos v11) e morfologia de volta a $0.6222$ salvo exceções pontuais ($0.5$ em `igt`, `S1-E1` 12B, `S2-E2` 4B). Latência cai para $\sim$$25$ s (`gen_tokens` $80$–$322$ vs até $512$ no executivo). O regime executivo foi **transitório e reversível**, sem histerese mensurável nas camadas MPS/Motor `[INTERPRETAÇÃO]`.

**(3) Proximidade da virada BASAL $\to$ MODULATED (turno 71)** `[DADO]+[DERIVADO]`: restam **18 turnos basais ao 4B** ($52/70$) e **25 ao 12B** ($45/70$); à cadência recente ($\sim$$11$ turnos/5 min do 4B em v11, latência $\sim$$25$ s) o 4B deve cruzar o turno 71 em $\sim$$8$–$10$ min, disparando `compute_and_store_basal_envelope` e abrindo os sub-braços `M1..M4`. Implicação técnica: o envelope será travado sobre os 70 turnos **incluindo o bloco executivo de alta variância** (drift $0.64$–$1.00$, vel $108$–$369$ no 4B), o que alarga $\sigma$ e dessensibiliza os gatilhos M4 (`drift > \mu+0.25\sigma`, `vel < 0.85\mu`) — recomendo confrontar os primeiros disparos modulados contra envelope por-etapa (v10+v11) vs global antes de interpretá-los `[INTERPRETAÇÃO]`.

**Caveats** `[LIMITE]`: $n=4$ (cognitivo) e $n=1$/$8$ (v11) — amostras mínimas; a queda do drift agregado 12B de $0.958$ ($n=3$) para $0.911$ ($n=4$) é diluição amostral pelo IGT ($0.767$), não reversão de regime. Ainda zero turnos `MODULATED`.

## Snapshot de Auditoria SWE — `2026-11-05T14:48:06.447988+00:00` (`108/280` turnos concluídos) `[DADO]`

### A. Estado por Modelo, Fase (`BASAL` vs `MODULATED`) e Sub-Braço de Escala

| Modelo | Fase | Sub-Braço | Turnos | $T$ Médio | $\Delta T$ | $\Psi$ | $R_{\text{pair}}$ | MPS $\chi_{\text{eff}}$ | MPS $PR_{\text{traj}}$ | MPS Drift | IPR | Morf. | Motor Vel. | Motor Acc. | Motor Drift | Action Mk | Unique Ratio | Degen (%) | Lat (s) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `BASAL_PURE` | 51 | 0.200 | +0.000 | 0.487 | 0.9946 | **18.13** | 11.71 | **0.8100** | 0.0647 | 0.6222 | **330.67** | 573.23 | 0.7893 | 0.00 | **0.613** | 3.9% | 64.9 |
| `gemma-4-E4B-it` | **BASAL** | `BASAL_PURE` | 57 | 0.200 | +0.000 | 0.487 | 0.9947 | **15.79** | 16.46 | **0.7730** | 0.1691 | 0.6222 | **263.46** | 455.64 | 0.7047 | 0.00 | **0.638** | 3.5% | 58.4 |

### B. Decomposição por Etapa/Processo da Bateria (`v10`, `cognitivo`, `v11`, `swe`)

| Modelo | Fase | Etapa/Processo | Turnos | MPS $\chi_{\text{eff}}$ | MPS Drift | Motor Vel. | Unique Ratio | Degen (%) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `cognitivo_executivo` | 4 | 17.36 | 0.9106 | 329.07 | 0.379 | 50.0% |
| `gemma-4-12B-it` | **BASAL** | `v10_subjectivity` | 40 | 17.99 | 0.8081 | 335.74 | 0.626 | 0.0% |
| `gemma-4-12B-it` | **BASAL** | `v11_multiturn_series` | 7 | 19.37 | 0.7634 | 302.61 | 0.669 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `cognitivo_executivo` | 4 | 16.41 | 0.7863 | 175.11 | 0.396 | 50.0% |
| `gemma-4-E4B-it` | **BASAL** | `v10_subjectivity` | 40 | 15.63 | 0.7770 | 272.30 | 0.649 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v11_multiturn_series` | 13 | 16.11 | 0.7567 | 263.46 | 0.678 | 0.0% |

### C. Acoplamento Escalas $\leftrightarrow$ Estado MPS $\leftrightarrow$ Camada Motor

- **`gemma-4-12B-it` ($N=51$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = +0.000$, $r(T, \text{mps\_drift}) = +0.000$, $r(T, \text{unique\_ratio}) = +0.000$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.041$
- **`gemma-4-E4B-it` ($N=57$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = +0.000$, $r(T, \text{mps\_drift}) = +0.000$, $r(T, \text{unique\_ratio}) = +0.000$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.215$
