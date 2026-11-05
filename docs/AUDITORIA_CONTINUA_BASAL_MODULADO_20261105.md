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

## Snapshot de Auditoria SWE — `2026-11-05T14:53:17.923200+00:00` (`120/280` turnos concluídos) `[DADO]`

### A. Estado por Modelo, Fase (`BASAL` vs `MODULATED`) e Sub-Braço de Escala

| Modelo | Fase | Sub-Braço | Turnos | $T$ Médio | $\Delta T$ | $\Psi$ | $R_{\text{pair}}$ | MPS $\chi_{\text{eff}}$ | MPS $PR_{\text{traj}}$ | MPS Drift | IPR | Morf. | Motor Vel. | Motor Acc. | Motor Drift | Action Mk | Unique Ratio | Degen (%) | Lat (s) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `BASAL_PURE` | 57 | 0.200 | +0.000 | 0.487 | 0.9947 | **18.27** | 11.88 | **0.8105** | 0.0643 | 0.6222 | **326.51** | 565.87 | 0.7869 | 0.00 | **0.611** | 3.5% | 63.7 |
| `gemma-4-E4B-it` | **BASAL** | `BASAL_PURE` | 63 | 0.200 | +0.000 | 0.487 | 0.9947 | **15.78** | 16.43 | **0.7739** | 0.1685 | 0.6222 | **262.61** | 454.21 | 0.7082 | 0.08 | **0.636** | 3.2% | 58.2 |

### B. Decomposição por Etapa/Processo da Bateria (`v10`, `cognitivo`, `v11`, `swe`)

| Modelo | Fase | Etapa/Processo | Turnos | MPS $\chi_{\text{eff}}$ | MPS Drift | Motor Vel. | Unique Ratio | Degen (%) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `cognitivo_executivo` | 4 | 17.36 | 0.9106 | 329.07 | 0.379 | 50.0% |
| `gemma-4-12B-it` | **BASAL** | `v10_subjectivity` | 40 | 17.99 | 0.8081 | 335.74 | 0.626 | 0.0% |
| `gemma-4-12B-it` | **BASAL** | `v11_multiturn_series` | 13 | 19.40 | 0.7869 | 297.30 | 0.636 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `cognitivo_executivo` | 4 | 16.41 | 0.7863 | 175.11 | 0.396 | 50.0% |
| `gemma-4-E4B-it` | **BASAL** | `swe_competition` | 1 | 15.05 | 0.9625 | 223.05 | 0.526 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v10_subjectivity` | 40 | 15.63 | 0.7770 | 272.30 | 0.649 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v11_multiturn_series` | 18 | 16.02 | 0.7539 | 262.72 | 0.667 | 0.0% |

### C. Acoplamento Escalas $\leftrightarrow$ Estado MPS $\leftrightarrow$ Camada Motor

- **`gemma-4-12B-it` ($N=57$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = +0.000$, $r(T, \text{mps\_drift}) = +0.000$, $r(T, \text{unique\_ratio}) = +0.000$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.147$
- **`gemma-4-E4B-it` ($N=63$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = +0.000$, $r(T, \text{mps\_drift}) = +0.000$, $r(T, \text{unique\_ratio}) = +0.000$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.185$

## Snapshot de Auditoria SWE — `2026-11-05T14:58:31.822581+00:00` (`128/280` turnos concluídos) `[DADO]`

### A. Estado por Modelo, Fase (`BASAL` vs `MODULATED`) e Sub-Braço de Escala

| Modelo | Fase | Sub-Braço | Turnos | $T$ Médio | $\Delta T$ | $\Psi$ | $R_{\text{pair}}$ | MPS $\chi_{\text{eff}}$ | MPS $PR_{\text{traj}}$ | MPS Drift | IPR | Morf. | Motor Vel. | Motor Acc. | Motor Drift | Action Mk | Unique Ratio | Degen (%) | Lat (s) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `BASAL_PURE` | 62 | 0.200 | +0.000 | 0.487 | 0.9947 | **18.41** | 12.01 | **0.8081** | 0.0641 | 0.6222 | **325.17** | 563.45 | 0.7821 | 0.00 | **0.612** | 3.2% | 62.6 |
| `gemma-4-E4B-it` | **BASAL** | `BASAL_PURE` | 66 | 0.200 | +0.000 | 0.487 | 0.9947 | **15.79** | 16.41 | **0.7752** | 0.1683 | 0.6222 | **259.91** | 449.57 | 0.7136 | 0.26 | **0.634** | 3.0% | 59.7 |

### B. Decomposição por Etapa/Processo da Bateria (`v10`, `cognitivo`, `v11`, `swe`)

| Modelo | Fase | Etapa/Processo | Turnos | MPS $\chi_{\text{eff}}$ | MPS Drift | Motor Vel. | Unique Ratio | Degen (%) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `cognitivo_executivo` | 4 | 17.36 | 0.9106 | 329.07 | 0.379 | 50.0% |
| `gemma-4-12B-it` | **BASAL** | `v10_subjectivity` | 40 | 17.99 | 0.8081 | 335.74 | 0.626 | 0.0% |
| `gemma-4-12B-it` | **BASAL** | `v11_multiturn_series` | 18 | 19.55 | 0.7854 | 300.81 | 0.633 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `cognitivo_executivo` | 4 | 16.41 | 0.7863 | 175.11 | 0.396 | 50.0% |
| `gemma-4-E4B-it` | **BASAL** | `swe_competition` | 4 | 15.67 | 0.8425 | 208.16 | 0.568 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v10_subjectivity` | 40 | 15.63 | 0.7770 | 272.30 | 0.649 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v11_multiturn_series` | 18 | 16.02 | 0.7539 | 262.72 | 0.667 | 0.0% |

### C. Acoplamento Escalas $\leftrightarrow$ Estado MPS $\leftrightarrow$ Camada Motor

- **`gemma-4-12B-it` ($N=62$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = +0.000$, $r(T, \text{mps\_drift}) = +0.000$, $r(T, \text{unique\_ratio}) = +0.000$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.186$
- **`gemma-4-E4B-it` ($N=66$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = +0.000$, $r(T, \text{mps\_drift}) = +0.000$, $r(T, \text{unique\_ratio}) = +0.000$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.182$

## Snapshot de Auditoria SWE — `2026-11-05T15:03:44.024136+00:00` (`134/280` turnos concluídos) `[DADO]`

### A. Estado por Modelo, Fase (`BASAL` vs `MODULATED`) e Sub-Braço de Escala

| Modelo | Fase | Sub-Braço | Turnos | $T$ Médio | $\Delta T$ | $\Psi$ | $R_{\text{pair}}$ | MPS $\chi_{\text{eff}}$ | MPS $PR_{\text{traj}}$ | MPS Drift | IPR | Morf. | Motor Vel. | Motor Acc. | Motor Drift | Action Mk | Unique Ratio | Degen (%) | Lat (s) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `BASAL_PURE` | 65 | 0.200 | +0.000 | 0.487 | 0.9947 | **18.36** | 11.79 | **0.8067** | 0.0643 | 0.6222 | **323.37** | 560.37 | 0.7850 | 0.38 | **0.609** | 3.1% | 64.4 |
| `gemma-4-E4B-it` | **BASAL** | `BASAL_PURE` | 69 | 0.200 | +0.000 | 0.487 | 0.9947 | **15.77** | 16.45 | **0.7821** | 0.1687 | 0.6222 | **257.61** | 445.58 | 0.7221 | 0.43 | **0.630** | 2.9% | 61.3 |

### B. Decomposição por Etapa/Processo da Bateria (`v10`, `cognitivo`, `v11`, `swe`)

| Modelo | Fase | Etapa/Processo | Turnos | MPS $\chi_{\text{eff}}$ | MPS Drift | Motor Vel. | Unique Ratio | Degen (%) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `cognitivo_executivo` | 4 | 17.36 | 0.9106 | 329.07 | 0.379 | 50.0% |
| `gemma-4-12B-it` | **BASAL** | `swe_competition` | 3 | 17.42 | 0.7770 | 286.14 | 0.544 | 0.0% |
| `gemma-4-12B-it` | **BASAL** | `v10_subjectivity` | 40 | 17.99 | 0.8081 | 335.74 | 0.626 | 0.0% |
| `gemma-4-12B-it` | **BASAL** | `v11_multiturn_series` | 18 | 19.55 | 0.7854 | 300.81 | 0.633 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `cognitivo_executivo` | 4 | 16.41 | 0.7863 | 175.11 | 0.396 | 50.0% |
| `gemma-4-E4B-it` | **BASAL** | `swe_competition` | 6 | 15.62 | 0.8724 | 207.42 | 0.551 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `swe_ood45` | 1 | 14.87 | 0.9335 | 208.94 | 0.617 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v10_subjectivity` | 40 | 15.63 | 0.7770 | 272.30 | 0.649 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v11_multiturn_series` | 18 | 16.02 | 0.7539 | 262.72 | 0.667 | 0.0% |

### C. Acoplamento Escalas $\leftrightarrow$ Estado MPS $\leftrightarrow$ Camada Motor

- **`gemma-4-12B-it` ($N=65$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = +0.000$, $r(T, \text{mps\_drift}) = +0.000$, $r(T, \text{unique\_ratio}) = +0.000$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.124$
- **`gemma-4-E4B-it` ($N=69$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = +0.000$, $r(T, \text{mps\_drift}) = +0.000$, $r(T, \text{unique\_ratio}) = +0.000$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.119$

## Snapshot de Auditoria SWE — `2026-11-05T15:08:59.522403+00:00` (`142/280` turnos concluídos) `[DADO]`

### A. Estado por Modelo, Fase (`BASAL` vs `MODULATED`) e Sub-Braço de Escala

| Modelo | Fase | Sub-Braço | Turnos | $T$ Médio | $\Delta T$ | $\Psi$ | $R_{\text{pair}}$ | MPS $\chi_{\text{eff}}$ | MPS $PR_{\text{traj}}$ | MPS Drift | IPR | Morf. | Motor Vel. | Motor Acc. | Motor Drift | Action Mk | Unique Ratio | Degen (%) | Lat (s) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `BASAL_PURE` | 68 | 0.200 | +0.000 | 0.487 | 0.9947 | **18.33** | 11.59 | **0.8078** | 0.0644 | 0.6222 | **321.94** | 557.78 | 0.7870 | 0.72 | **0.606** | 4.4% | 66.8 |
| `gemma-4-E4B-it` | **BASAL** | `BASAL_PURE` | 70 | 0.200 | +0.000 | 0.487 | 0.9947 | **15.76** | 16.46 | **0.7813** | 0.1686 | 0.6222 | **256.86** | 444.28 | 0.7235 | 0.53 | **0.629** | 2.9% | 61.5 |
| `gemma-4-E4B-it` | **MODULATED** | `M1_scale_minus_delta` | 1 | 0.130 | -0.070 | 0.487 | 0.9919 | **14.25** | 15.68 | **0.8315** | 0.1727 | 0.6222 | **267.60** | 462.87 | 0.7605 | 0.00 | **0.663** | 0.0% | 74.2 |
| `gemma-4-E4B-it` | **MODULATED** | `M2_scale_plus_delta` | 1 | 0.280 | +0.080 | 0.487 | 0.9947 | **14.89** | 15.74 | **0.7581** | 0.1803 | 0.6222 | **235.09** | 399.11 | 0.6231 | 0.00 | **0.700** | 0.0% | 63.5 |
| `gemma-4-E4B-it` | **MODULATED** | `M3_freud10d_inrc_kuramoto` | 1 | 0.090 | -0.110 | 0.487 | 0.9947 | **16.20** | 16.00 | **0.8983** | 0.1757 | 0.6222 | **265.21** | 465.79 | 0.7641 | 0.00 | **0.641** | 0.0% | 73.9 |
| `gemma-4-E4B-it` | **MODULATED** | `M4_closed_loop_mps_motor` | 1 | 0.100 | -0.100 | 0.487 | 0.9947 | **16.57** | 17.19 | **0.6529** | 0.1723 | 0.6222 | **288.40** | 504.77 | 0.5590 | 0.00 | **0.648** | 0.0% | 68.5 |

### B. Decomposição por Etapa/Processo da Bateria (`v10`, `cognitivo`, `v11`, `swe`)

| Modelo | Fase | Etapa/Processo | Turnos | MPS $\chi_{\text{eff}}$ | MPS Drift | Motor Vel. | Unique Ratio | Degen (%) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `cognitivo_executivo` | 4 | 17.36 | 0.9106 | 329.07 | 0.379 | 50.0% |
| `gemma-4-12B-it` | **BASAL** | `swe_competition` | 6 | 17.55 | 0.8039 | 288.63 | 0.542 | 16.7% |
| `gemma-4-12B-it` | **BASAL** | `v10_subjectivity` | 40 | 17.99 | 0.8081 | 335.74 | 0.626 | 0.0% |
| `gemma-4-12B-it` | **BASAL** | `v11_multiturn_series` | 18 | 19.55 | 0.7854 | 300.81 | 0.633 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `cognitivo_executivo` | 4 | 16.41 | 0.7863 | 175.11 | 0.396 | 50.0% |
| `gemma-4-E4B-it` | **BASAL** | `swe_competition` | 6 | 15.62 | 0.8724 | 207.42 | 0.551 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `swe_ood45` | 2 | 15.01 | 0.8330 | 207.20 | 0.592 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v10_subjectivity` | 40 | 15.63 | 0.7770 | 272.30 | 0.649 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v11_multiturn_series` | 18 | 16.02 | 0.7539 | 262.72 | 0.667 | 0.0% |
| `gemma-4-E4B-it` | **MODULATED** | `v10_subjectivity` | 4 | 15.48 | 0.7852 | 264.07 | 0.663 | 0.0% |

### C. Acoplamento Escalas $\leftrightarrow$ Estado MPS $\leftrightarrow$ Camada Motor

- **`gemma-4-12B-it` ($N=68$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = +0.000$, $r(T, \text{mps\_drift}) = +0.000$, $r(T, \text{unique\_ratio}) = +0.000$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.057$
- **`gemma-4-E4B-it` ($N=74$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = -0.127$, $r(T, \text{mps\_drift}) = -0.040$, $r(T, \text{unique\_ratio}) = +0.003$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.078$

### Parecer Técnico SWE (Ciclo 14 - Fechamento do Envelope Basal e Primeiros Turnos Modulados M1..M4)

**Escopo**: ~148 turnos (`ts` máx. `2026-11-05T15:12:02Z`, leitura `mode=ro` sobre WAL ativo — banco em escrita contínua). Ambos os braços **fecharam a fase BASAL** (70/70): E4B às `15:03:53` e 12B às `15:10:33` — a linha `basal_envelope` do 12B foi escrita **durante esta auditoria** `[DADO]`. O E4B já corre `MODULATED` com 7 turnos (71–77: ciclo completo M1–M4 em `cena_1`/`cena_2` + 2º ciclo iniciado em `cena_3`/`cena_4`); o 12B produziu seu 1º turno modulado (`M1`, turno 71, `cena_1` f1, `15:11:53`) `[DADO]`.

**(1) `basal_envelope` consolidado (n=70/modelo: 40 `v10` + 4 `cognitivo_executivo` + 18 `v11` + 6 `swe_competition` + 2 `swe_ood45`)** `[DADO]`:

| Campo | E4B `:8099` (`15:03:53`) | 12B `:8098` (`15:10:33`) |
|---|---:|---:|
| $\chi_{\text{eff}}$ $\mu\pm\sigma$ | $15.757 \pm 0.787$ | $18.330 \pm 1.381$ |
| $PR_{\text{traj}}$ $\mu$ | $16.459$ | $11.402$ |
| `contract_drift` $\mu\pm\sigma$ | $0.7814 \pm 0.0843$ | $0.8083 \pm 0.0714$ |
| IPR $\mu$ | $0.1663$ | $0.0625$ |
| Morfologia $\mu$ | $0.6205$ | $0.6187$ |
| Motor vel. $\mu\pm\sigma$ | $256.86 \pm 33.34$ | $322.01 \pm 26.00$ |
| Motor $\|h\|$ $\mu$ | $193.87$ | $210.38$ |
| `unique_ratio` $\mu$ | $0.6294$ | $0.5990$ |
| Degen rate | $0.0286$ (2/70: `wcst` t41, `igt` t44) | $0.0571$ (4/70: `wcst`, `igt`, `werkzeug-2997` t68, `ood45_3995` t69) |

Integridade `[DADO]+[DERIVADO]`: recomputação independente sobre `battery_turns` reproduz os campos com semântica `np.mean`/`np.std` (σ populacional, ddof=0 — confere com `compute_and_store_basal_envelope`); 140/140 linhas `BASAL`/`BASAL_PURE`/`intervention_enabled=0`/`T=0.2`/`ΔT=0` e 8/8 `MODULATED`/`intervention_enabled=1`, zero violações. **Gatilhos M4 resultantes por braço**: E4B `drift > 0.8024` ou `vel < 218.33`; 12B `drift > 0.8262` ou `vel < 273.71`. A inclusão dos 12 turnos de alta variância (`cognitivo`+`swe*`) confirmou — com magnitude modesta — a dessensibilização prevista no Ciclo 9: contra envelope só-`v10+v11` (n=58), no **E4B** o gatilho de drift subiu $0.7887\to0.8024$ e o de velocidade caiu $228.9\to218.3$ ($\sigma_{\text{vel}}$ inflado $14.1\to33.3$ pelos turnos swe com vel $197$–$223$); no **12B** o efeito é pequeno ($0.8174\to0.8262$; $276.2\to273.7$) porque sua velocidade basal já é alta e estável `[DERIVADO]`. Assimetria inter-modelo: o gatilho de velocidade do 12B ($273.7$) fica $+55$ acima do E4B ($218.3$) — quedas absolutas equivalentes disparam o gate do 12B muito antes `[INTERPRETAÇÃO]`. Os dois novos flags degen do 12B (`swe_competition` `werkzeug-2997`, `swe_ood45` `iceberg_3995`) são os primeiros fora do bloco executivo e co-ocorrem com prompts de código longos ($p_{\text{tok}}=3342$/$443$) e `unique_ratio` $0.49$/$0.21$ — mesmo padrão estrutural de tarefa, não colapso generativo `[INTERPRETAÇÃO]`.

**(2) Pareamento direto MODULATED × homólogo BASAL (E4B, turnos 71–74 vs 1–4; mesma `task_id`/`conv_turn_idx`)** `[DADO]+[DERIVADO]`:

| Par | $T$ ($\Delta T$), top_p, INRC | $\Delta\chi_{\text{eff}}$ | $\Delta PR_{\text{traj}}$ | $\Delta$ drift | $\Delta$ IPR | $\Delta$ vel | $\Delta$ acc | $\Delta$ cos_drift | $\Delta\|h\|$ | $\Delta$ unique |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **M1** t71↔t1 (`cena_1` f1) | $0.13$ ($-0.07$), $0.85$, `C` | $-0.11$ | $\mathbf{-1.76}$ | $\mathbf{+0.070}$ | $-0.006$ | $\mathbf{-17.0}$ | $-27.9$ | $+0.088$ | $-36.3$ | $-0.012$ |
| **M2** t72↔t2 (`cena_1` f2) | $0.28$ ($+0.08$), $0.94$, `R` | $-0.97$ | $-1.03$ | $\mathbf{+0.088}$ | $-0.002$ | $\mathbf{-29.5}$ | $-54.7$ | $+0.064$ | $+22.3$ | $+0.016$ |
| **M3** t73↔t3 (`cena_2` f1) | $0.09$ ($-0.11$), $0.82$, `R+C` | $\mathbf{+1.32}$ | $\mathbf{-2.30}$ | $\mathbf{+0.111}$ | $-0.031$ | $-6.8$ | $-9.0$ | $-0.000$ | $\mathbf{-142.6}$ | $+0.014$ |
| **M4** t74↔t4 (`cena_2` f2) | $0.10$ ($-0.10$), $0.84$, `R+C` | $+0.32$ | $+0.77$ | $\mathbf{-0.038}$ | $-0.016$ | $\mathbf{+21.3}$ | $+37.5$ | $\mathbf{-0.062}$ | $-28.8$ | $-0.018$ |

Leitura das camadas `[DERIVADO]+[INTERPRETAÇÃO]`: (i) os três braços open-loop deslocaram **na mesma direção** — MPS mais contrativo (`drift` $+0.07$ a $+0.11$; M1 e M3 já acima do gatilho M4 `0.8024`), $PR_{\text{traj}}$ menor — e camada motora **mais lenta** (vel $-2.5\%$ a $-11\%$) com `cos_drift` maior em M1/M2. M2 **subiu** $T$ e mesmo assim desacelerou o motor — indício de que o texto da diretriz/operador INRC domina o efeito bruto de $T$ `[INTERPRETAÇÃO]`. (ii) O closed-loop **M4 inverteu os dois sinais** (`drift` $-0.038$ para $0.653$, abaixo do $\mu$ basal $0.781$; vel $+8\%$; `cos_drift` $-10\%$) — primeira evidência de correção efetiva do gate `[INTERPRETAÇÃO, n=1]`. (iii) Detalhe de design: o M4 disparou ao ler `prev_mps` do turno t73 — consumiu a elevação de drift **induzida pelo próprio M3** ($0.898 > 0.8024$), não um desvio basal espontâneo; o closed-loop herda estado entre sub-braços consecutivos `[DADO código]+[LIMITE]`. (iv) `hidden_norm` caiu em M1/M3/M4 ($-36$/$-143$/$-29$; até $-55\%$ no M3) — o braço Freud10D+INRC+Kuramoto contrai drasticamente a magnitude do estado oculto sem alterar `cos_drift` ($\Delta\approx0$): a modulação afeta amplitude, não direção `[INTERPRETAÇÃO]`. (v) Escalas soberanas bit-a-bit idênticas aos homólogos basais ($\Psi=0.4868$, $R_{\text{pair}}=0.9919/0.9947$, transição `limit_cycle→chaotic` nas mesmas posições) — confirmadas como covariável temporal compartilhada, não discriminador `[DADO]`. Zero `action_markers`, `thinking_chars=0`, zero degen nos turnos modulados; latência $+1.4$ a $+5.4$ s, coerente com `prompt_tokens` $+66$ a $+259$ (a diretriz entra no prompt) `[DADO]`.

**Caveats** `[LIMITE]`: $n=1$ por sub-braço e o contraste não é $T$-puro (diretriz + top_p + INRC co-variando); turnos t75/t76 (2º ciclo, `cena_3`) exibem `ipr=0.0`/`morph=0.5` — mesmo sentinela de sonda ausente do basal (`cena_11/12`) — excluir do pareamento fino; a fase modulada do 12B acaba de iniciar (apenas `M1` t71 registrado — `drift` $0.781$, vel $334$), sem cobertura ainda para M2–M4.

## Snapshot de Auditoria SWE — `2026-11-05T15:14:34.327720+00:00` (`152/280` turnos concluídos) `[DADO]`

### A. Estado por Modelo, Fase (`BASAL` vs `MODULATED`) e Sub-Braço de Escala

| Modelo | Fase | Sub-Braço | Turnos | $T$ Médio | $\Delta T$ | $\Psi$ | $R_{\text{pair}}$ | MPS $\chi_{\text{eff}}$ | MPS $PR_{\text{traj}}$ | MPS Drift | IPR | Morf. | Motor Vel. | Motor Acc. | Motor Drift | Action Mk | Unique Ratio | Degen (%) | Lat (s) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `BASAL_PURE` | 70 | 0.200 | +0.000 | 0.487 | 0.9947 | **18.33** | 11.40 | **0.8083** | 0.0643 | 0.6222 | **322.01** | 557.81 | 0.7880 | 0.91 | **0.599** | 5.7% | 67.2 |
| `gemma-4-12B-it` | **MODULATED** | `M1_scale_minus_delta` | 1 | 0.130 | -0.070 | 0.487 | 0.9919 | **20.01** | 11.85 | **0.7812** | 0.0561 | 0.6222 | **334.06** | 586.28 | 0.8670 | 0.00 | **0.618** | 0.0% | 80.3 |
| `gemma-4-12B-it` | **MODULATED** | `M2_scale_plus_delta` | 1 | 0.280 | +0.080 | 0.487 | 0.9947 | **17.76** | 11.89 | **0.7854** | 0.0673 | 0.6222 | **373.66** | 648.43 | 0.8354 | 0.00 | **0.661** | 0.0% | 66.1 |
| `gemma-4-12B-it` | **MODULATED** | `M3_freud10d_inrc_kuramoto` | 1 | 0.090 | -0.110 | 0.487 | 0.9947 | **18.06** | 11.70 | **0.8747** | 0.0548 | 0.6222 | **352.13** | 609.43 | 0.6291 | 0.00 | **0.580** | 0.0% | 81.4 |
| `gemma-4-E4B-it` | **BASAL** | `BASAL_PURE` | 70 | 0.200 | +0.000 | 0.487 | 0.9947 | **15.76** | 16.46 | **0.7813** | 0.1686 | 0.6222 | **256.86** | 444.28 | 0.7235 | 0.53 | **0.629** | 2.9% | 61.5 |
| `gemma-4-E4B-it` | **MODULATED** | `M1_scale_minus_delta` | 3 | 0.130 | -0.070 | 0.487 | 0.9938 | **14.53** | 16.40 | **0.8581** | 0.1702 | 0.6222 | **265.29** | 455.23 | 0.7933 | 0.00 | **0.632** | 0.0% | 73.5 |
| `gemma-4-E4B-it` | **MODULATED** | `M2_scale_plus_delta` | 2 | 0.280 | +0.080 | 0.487 | 0.9947 | **15.52** | 15.17 | **0.7601** | 0.1761 | 0.6222 | **249.07** | 423.52 | 0.6290 | 0.00 | **0.682** | 0.0% | 60.2 |
| `gemma-4-E4B-it` | **MODULATED** | `M3_freud10d_inrc_kuramoto` | 2 | 0.090 | -0.110 | 0.487 | 0.9947 | **14.99** | 16.52 | **0.9250** | 0.1818 | 0.6222 | **262.89** | 457.43 | 0.8061 | 0.00 | **0.636** | 0.0% | 75.2 |
| `gemma-4-E4B-it` | **MODULATED** | `M4_closed_loop_mps_motor` | 2 | 0.100 | -0.100 | 0.487 | 0.9947 | **15.52** | 16.79 | **0.7507** | 0.1800 | 0.6222 | **275.74** | 480.82 | 0.6747 | 0.00 | **0.662** | 0.0% | 70.2 |

### B. Decomposição por Etapa/Processo da Bateria (`v10`, `cognitivo`, `v11`, `swe`)

| Modelo | Fase | Etapa/Processo | Turnos | MPS $\chi_{\text{eff}}$ | MPS Drift | Motor Vel. | Unique Ratio | Degen (%) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `cognitivo_executivo` | 4 | 17.36 | 0.9106 | 329.07 | 0.379 | 50.0% |
| `gemma-4-12B-it` | **BASAL** | `swe_competition` | 6 | 17.55 | 0.8039 | 288.63 | 0.542 | 16.7% |
| `gemma-4-12B-it` | **BASAL** | `swe_ood45` | 2 | 18.36 | 0.8275 | 324.10 | 0.360 | 50.0% |
| `gemma-4-12B-it` | **BASAL** | `v10_subjectivity` | 40 | 17.99 | 0.8081 | 335.74 | 0.626 | 0.0% |
| `gemma-4-12B-it` | **BASAL** | `v11_multiturn_series` | 18 | 19.55 | 0.7854 | 300.81 | 0.633 | 0.0% |
| `gemma-4-12B-it` | **MODULATED** | `v10_subjectivity` | 3 | 18.61 | 0.8138 | 353.28 | 0.620 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `cognitivo_executivo` | 4 | 16.41 | 0.7863 | 175.11 | 0.396 | 50.0% |
| `gemma-4-E4B-it` | **BASAL** | `swe_competition` | 6 | 15.62 | 0.8724 | 207.42 | 0.551 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `swe_ood45` | 2 | 15.01 | 0.8330 | 207.20 | 0.592 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v10_subjectivity` | 40 | 15.63 | 0.7770 | 272.30 | 0.649 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v11_multiturn_series` | 18 | 16.02 | 0.7539 | 262.72 | 0.667 | 0.0% |
| `gemma-4-E4B-it` | **MODULATED** | `v10_subjectivity` | 9 | 15.07 | 0.8273 | 263.48 | 0.651 | 0.0% |

### C. Acoplamento Escalas $\leftrightarrow$ Estado MPS $\leftrightarrow$ Camada Motor

- **`gemma-4-12B-it` ($N=73$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = +0.003$, $r(T, \text{mps\_drift}) = -0.079$, $r(T, \text{unique\_ratio}) = +0.048$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.060$
- **`gemma-4-E4B-it` ($N=79$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = -0.105$, $r(T, \text{mps\_drift}) = -0.213$, $r(T, \text{unique\_ratio}) = +0.005$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.084$

## Snapshot de Auditoria SWE — `2026-11-05T15:20:06.845293+00:00` (`161/280` turnos concluídos) `[DADO]`

### A. Estado por Modelo, Fase (`BASAL` vs `MODULATED`) e Sub-Braço de Escala

| Modelo | Fase | Sub-Braço | Turnos | $T$ Médio | $\Delta T$ | $\Psi$ | $R_{\text{pair}}$ | MPS $\chi_{\text{eff}}$ | MPS $PR_{\text{traj}}$ | MPS Drift | IPR | Morf. | Motor Vel. | Motor Acc. | Motor Drift | Action Mk | Unique Ratio | Degen (%) | Lat (s) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `BASAL_PURE` | 70 | 0.200 | +0.000 | 0.487 | 0.9947 | **18.33** | 11.40 | **0.8083** | 0.0643 | 0.6222 | **322.01** | 557.81 | 0.7880 | 0.91 | **0.599** | 5.7% | 67.2 |
| `gemma-4-12B-it` | **MODULATED** | `M1_scale_minus_delta` | 2 | 0.130 | -0.070 | 0.487 | 0.9933 | **19.06** | 11.24 | **0.8287** | 0.0571 | 0.6222 | **342.89** | 597.25 | 0.8215 | 0.00 | **0.606** | 0.0% | 80.9 |
| `gemma-4-12B-it` | **MODULATED** | `M2_scale_plus_delta` | 2 | 0.280 | +0.080 | 0.487 | 0.9947 | **17.66** | 10.73 | **0.7858** | 0.0693 | 0.6222 | **369.90** | 642.85 | 0.8098 | 0.00 | **0.641** | 0.0% | 67.2 |
| `gemma-4-12B-it` | **MODULATED** | `M3_freud10d_inrc_kuramoto` | 2 | 0.090 | -0.110 | 0.487 | 0.9947 | **17.92** | 11.06 | **0.8303** | 0.0615 | 0.6222 | **348.04** | 605.00 | 0.7571 | 0.00 | **0.602** | 0.0% | 82.6 |
| `gemma-4-12B-it` | **MODULATED** | `M4_closed_loop_mps_motor` | 1 | 0.100 | -0.100 | 0.487 | 0.9947 | **17.78** | 10.42 | **0.7808** | 0.0721 | 0.6222 | **390.03** | 680.38 | 0.8389 | 0.00 | **0.668** | 0.0% | 63.3 |
| `gemma-4-E4B-it` | **BASAL** | `BASAL_PURE` | 70 | 0.200 | +0.000 | 0.487 | 0.9947 | **15.76** | 16.46 | **0.7813** | 0.1686 | 0.6222 | **256.86** | 444.28 | 0.7235 | 0.53 | **0.629** | 2.9% | 61.5 |
| `gemma-4-E4B-it` | **MODULATED** | `M1_scale_minus_delta` | 4 | 0.130 | -0.070 | 0.487 | 0.9940 | **14.78** | 16.53 | **0.8168** | 0.1720 | 0.6222 | **263.81** | 452.87 | 0.7457 | 0.00 | **0.637** | 0.0% | 72.1 |
| `gemma-4-E4B-it` | **MODULATED** | `M2_scale_plus_delta` | 4 | 0.280 | +0.080 | 0.487 | 0.9947 | **15.72** | 15.58 | **0.7319** | 0.1742 | 0.6222 | **263.26** | 451.92 | 0.5779 | 0.00 | **0.665** | 0.0% | 60.4 |
| `gemma-4-E4B-it` | **MODULATED** | `M3_freud10d_inrc_kuramoto` | 3 | 0.090 | -0.110 | 0.487 | 0.9947 | **14.95** | 16.40 | **0.9255** | 0.1725 | 0.6222 | **262.05** | 456.84 | 0.8146 | 0.00 | **0.632** | 0.0% | 74.2 |
| `gemma-4-E4B-it` | **MODULATED** | `M4_closed_loop_mps_motor` | 3 | 0.100 | -0.100 | 0.487 | 0.9947 | **15.60** | 16.62 | **0.7278** | 0.1759 | 0.6222 | **277.12** | 483.52 | 0.6478 | 0.00 | **0.634** | 0.0% | 69.0 |

### B. Decomposição por Etapa/Processo da Bateria (`v10`, `cognitivo`, `v11`, `swe`)

| Modelo | Fase | Etapa/Processo | Turnos | MPS $\chi_{\text{eff}}$ | MPS Drift | Motor Vel. | Unique Ratio | Degen (%) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `cognitivo_executivo` | 4 | 17.36 | 0.9106 | 329.07 | 0.379 | 50.0% |
| `gemma-4-12B-it` | **BASAL** | `swe_competition` | 6 | 17.55 | 0.8039 | 288.63 | 0.542 | 16.7% |
| `gemma-4-12B-it` | **BASAL** | `swe_ood45` | 2 | 18.36 | 0.8275 | 324.10 | 0.360 | 50.0% |
| `gemma-4-12B-it` | **BASAL** | `v10_subjectivity` | 40 | 17.99 | 0.8081 | 335.74 | 0.626 | 0.0% |
| `gemma-4-12B-it` | **BASAL** | `v11_multiturn_series` | 18 | 19.55 | 0.7854 | 300.81 | 0.633 | 0.0% |
| `gemma-4-12B-it` | **MODULATED** | `v10_subjectivity` | 7 | 18.15 | 0.8101 | 358.81 | 0.624 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `cognitivo_executivo` | 4 | 16.41 | 0.7863 | 175.11 | 0.396 | 50.0% |
| `gemma-4-E4B-it` | **BASAL** | `swe_competition` | 6 | 15.62 | 0.8724 | 207.42 | 0.551 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `swe_ood45` | 2 | 15.01 | 0.8330 | 207.20 | 0.592 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v10_subjectivity` | 40 | 15.63 | 0.7770 | 272.30 | 0.649 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v11_multiturn_series` | 18 | 16.02 | 0.7539 | 262.72 | 0.667 | 0.0% |
| `gemma-4-E4B-it` | **MODULATED** | `v10_subjectivity` | 14 | 15.26 | 0.7968 | 266.13 | 0.643 | 0.0% |

### C. Acoplamento Escalas $\leftrightarrow$ Estado MPS $\leftrightarrow$ Camada Motor

- **`gemma-4-12B-it` ($N=77$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = -0.119$, $r(T, \text{mps\_drift}) = -0.059$, $r(T, \text{unique\_ratio}) = -0.006$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.086$
- **`gemma-4-E4B-it` ($N=84$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = -0.073$, $r(T, \text{mps\_drift}) = -0.214$, $r(T, \text{unique\_ratio}) = +0.033$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.078$

## Snapshot de Auditoria SWE — `2026-11-05T15:25:25.103654+00:00` (`170/280` turnos concluídos) `[DADO]`

### A. Estado por Modelo, Fase (`BASAL` vs `MODULATED`) e Sub-Braço de Escala

| Modelo | Fase | Sub-Braço | Turnos | $T$ Médio | $\Delta T$ | $\Psi$ | $R_{\text{pair}}$ | MPS $\chi_{\text{eff}}$ | MPS $PR_{\text{traj}}$ | MPS Drift | IPR | Morf. | Motor Vel. | Motor Acc. | Motor Drift | Action Mk | Unique Ratio | Degen (%) | Lat (s) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `BASAL_PURE` | 70 | 0.200 | +0.000 | 0.487 | 0.9947 | **18.33** | 11.40 | **0.8083** | 0.0643 | 0.6222 | **322.01** | 557.81 | 0.7880 | 0.91 | **0.599** | 5.7% | 67.2 |
| `gemma-4-12B-it` | **MODULATED** | `M1_scale_minus_delta` | 3 | 0.130 | -0.070 | 0.487 | 0.9938 | **18.49** | 11.68 | **0.7992** | 0.0619 | 0.6222 | **337.44** | 584.58 | 0.8068 | 0.00 | **0.609** | 0.0% | 78.6 |
| `gemma-4-12B-it` | **MODULATED** | `M2_scale_plus_delta` | 3 | 0.280 | +0.080 | 0.487 | 0.9947 | **17.69** | 11.33 | **0.7651** | 0.0693 | 0.6222 | **354.26** | 613.96 | 0.8003 | 0.00 | **0.625** | 0.0% | 65.7 |
| `gemma-4-12B-it` | **MODULATED** | `M3_freud10d_inrc_kuramoto` | 3 | 0.090 | -0.110 | 0.487 | 0.9947 | **17.87** | 11.40 | **0.8210** | 0.0633 | 0.6222 | **341.76** | 591.80 | 0.8020 | 0.00 | **0.594** | 0.0% | 81.6 |
| `gemma-4-12B-it` | **MODULATED** | `M4_closed_loop_mps_motor` | 3 | 0.093 | -0.107 | 0.487 | 0.9947 | **17.77** | 10.38 | **0.7704** | 0.0722 | 0.6222 | **362.83** | 626.75 | 0.8346 | 0.00 | **0.640** | 0.0% | 64.0 |
| `gemma-4-E4B-it` | **BASAL** | `BASAL_PURE` | 70 | 0.200 | +0.000 | 0.487 | 0.9947 | **15.76** | 16.46 | **0.7813** | 0.1686 | 0.6222 | **256.86** | 444.28 | 0.7235 | 0.53 | **0.629** | 2.9% | 61.5 |
| `gemma-4-E4B-it` | **MODULATED** | `M1_scale_minus_delta` | 5 | 0.130 | -0.070 | 0.487 | 0.9941 | **14.75** | 16.44 | **0.8301** | 0.1722 | 0.6222 | **264.11** | 454.10 | 0.7657 | 0.00 | **0.646** | 0.0% | 72.0 |
| `gemma-4-E4B-it` | **MODULATED** | `M2_scale_plus_delta` | 5 | 0.280 | +0.080 | 0.487 | 0.9947 | **15.79** | 15.67 | **0.7276** | 0.1713 | 0.6222 | **269.58** | 464.56 | 0.5811 | 0.00 | **0.672** | 0.0% | 60.7 |
| `gemma-4-E4B-it` | **MODULATED** | `M3_freud10d_inrc_kuramoto` | 4 | 0.090 | -0.110 | 0.487 | 0.9947 | **14.79** | 16.80 | **0.8898** | 0.1718 | 0.6222 | **260.27** | 452.55 | 0.8006 | 0.00 | **0.636** | 0.0% | 73.6 |
| `gemma-4-E4B-it` | **MODULATED** | `M4_closed_loop_mps_motor` | 4 | 0.098 | -0.103 | 0.487 | 0.9947 | **15.52** | 15.89 | **0.7732** | 0.1704 | 0.6222 | **272.91** | 476.06 | 0.6941 | 0.00 | **0.634** | 0.0% | 69.9 |

### B. Decomposição por Etapa/Processo da Bateria (`v10`, `cognitivo`, `v11`, `swe`)

| Modelo | Fase | Etapa/Processo | Turnos | MPS $\chi_{\text{eff}}$ | MPS Drift | Motor Vel. | Unique Ratio | Degen (%) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `cognitivo_executivo` | 4 | 17.36 | 0.9106 | 329.07 | 0.379 | 50.0% |
| `gemma-4-12B-it` | **BASAL** | `swe_competition` | 6 | 17.55 | 0.8039 | 288.63 | 0.542 | 16.7% |
| `gemma-4-12B-it` | **BASAL** | `swe_ood45` | 2 | 18.36 | 0.8275 | 324.10 | 0.360 | 50.0% |
| `gemma-4-12B-it` | **BASAL** | `v10_subjectivity` | 40 | 17.99 | 0.8081 | 335.74 | 0.626 | 0.0% |
| `gemma-4-12B-it` | **BASAL** | `v11_multiturn_series` | 18 | 19.55 | 0.7854 | 300.81 | 0.633 | 0.0% |
| `gemma-4-12B-it` | **MODULATED** | `v10_subjectivity` | 12 | 17.95 | 0.7889 | 349.07 | 0.617 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `cognitivo_executivo` | 4 | 16.41 | 0.7863 | 175.11 | 0.396 | 50.0% |
| `gemma-4-E4B-it` | **BASAL** | `swe_competition` | 6 | 15.62 | 0.8724 | 207.42 | 0.551 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `swe_ood45` | 2 | 15.01 | 0.8330 | 207.20 | 0.592 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v10_subjectivity` | 40 | 15.63 | 0.7770 | 272.30 | 0.649 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v11_multiturn_series` | 18 | 16.02 | 0.7539 | 262.72 | 0.667 | 0.0% |
| `gemma-4-E4B-it` | **MODULATED** | `v10_subjectivity` | 18 | 15.22 | 0.8023 | 266.73 | 0.648 | 0.0% |

### C. Acoplamento Escalas $\leftrightarrow$ Estado MPS $\leftrightarrow$ Camada Motor

- **`gemma-4-12B-it` ($N=82$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = -0.161$, $r(T, \text{mps\_drift}) = -0.011$, $r(T, \text{unique\_ratio}) = -0.021$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.093$
- **`gemma-4-E4B-it` ($N=88$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = -0.035$, $r(T, \text{mps\_drift}) = -0.266$, $r(T, \text{unique\_ratio}) = +0.032$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.070$

## Snapshot de Auditoria SWE — `2026-11-05T15:30:44.578546+00:00` (`179/280` turnos concluídos) `[DADO]`

### A. Estado por Modelo, Fase (`BASAL` vs `MODULATED`) e Sub-Braço de Escala

| Modelo | Fase | Sub-Braço | Turnos | $T$ Médio | $\Delta T$ | $\Psi$ | $R_{\text{pair}}$ | MPS $\chi_{\text{eff}}$ | MPS $PR_{\text{traj}}$ | MPS Drift | IPR | Morf. | Motor Vel. | Motor Acc. | Motor Drift | Action Mk | Unique Ratio | Degen (%) | Lat (s) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `BASAL_PURE` | 70 | 0.200 | +0.000 | 0.487 | 0.9947 | **18.33** | 11.40 | **0.8083** | 0.0643 | 0.6222 | **322.01** | 557.81 | 0.7880 | 0.91 | **0.599** | 5.7% | 67.2 |
| `gemma-4-12B-it` | **MODULATED** | `M1_scale_minus_delta` | 4 | 0.130 | -0.070 | 0.487 | 0.9940 | **19.05** | 11.80 | **0.8185** | 0.0604 | 0.6222 | **330.45** | 570.67 | 0.8377 | 0.00 | **0.618** | 0.0% | 79.3 |
| `gemma-4-12B-it` | **MODULATED** | `M2_scale_plus_delta` | 4 | 0.280 | +0.080 | 0.487 | 0.9947 | **17.70** | 11.92 | **0.7621** | 0.0693 | 0.6222 | **352.95** | 612.41 | 0.7932 | 0.00 | **0.630** | 0.0% | 64.9 |
| `gemma-4-12B-it` | **MODULATED** | `M3_freud10d_inrc_kuramoto` | 4 | 0.090 | -0.110 | 0.487 | 0.9947 | **17.76** | 11.21 | **0.8640** | 0.0644 | 0.6222 | **346.30** | 598.73 | 0.7865 | 0.00 | **0.597** | 0.0% | 82.1 |
| `gemma-4-12B-it` | **MODULATED** | `M4_closed_loop_mps_motor` | 4 | 0.095 | -0.105 | 0.487 | 0.9947 | **18.63** | 10.42 | **0.7547** | 0.0696 | 0.6222 | **355.39** | 612.89 | 0.8243 | 0.00 | **0.640** | 0.0% | 69.5 |
| `gemma-4-E4B-it` | **BASAL** | `BASAL_PURE` | 70 | 0.200 | +0.000 | 0.487 | 0.9947 | **15.76** | 16.46 | **0.7813** | 0.1686 | 0.6222 | **256.86** | 444.28 | 0.7235 | 0.53 | **0.629** | 2.9% | 61.5 |
| `gemma-4-E4B-it` | **MODULATED** | `M1_scale_minus_delta` | 6 | 0.130 | -0.070 | 0.487 | 0.9942 | **14.80** | 16.46 | **0.8240** | 0.1707 | 0.6222 | **267.08** | 459.71 | 0.7755 | 0.00 | **0.647** | 0.0% | 72.5 |
| `gemma-4-E4B-it` | **MODULATED** | `M2_scale_plus_delta` | 6 | 0.280 | +0.080 | 0.487 | 0.9947 | **15.77** | 15.89 | **0.7255** | 0.1718 | 0.6222 | **270.36** | 465.76 | 0.5751 | 0.00 | **0.674** | 0.0% | 59.6 |
| `gemma-4-E4B-it` | **MODULATED** | `M3_freud10d_inrc_kuramoto` | 6 | 0.090 | -0.110 | 0.487 | 0.9947 | **14.79** | 17.13 | **0.8998** | 0.1637 | 0.6222 | **266.55** | 463.39 | 0.8017 | 0.00 | **0.632** | 0.0% | 77.9 |
| `gemma-4-E4B-it` | **MODULATED** | `M4_closed_loop_mps_motor` | 5 | 0.098 | -0.102 | 0.487 | 0.9947 | **15.58** | 16.21 | **0.7555** | 0.1716 | 0.6222 | **268.64** | 467.42 | 0.6822 | 0.00 | **0.639** | 0.0% | 67.3 |

### B. Decomposição por Etapa/Processo da Bateria (`v10`, `cognitivo`, `v11`, `swe`)

| Modelo | Fase | Etapa/Processo | Turnos | MPS $\chi_{\text{eff}}$ | MPS Drift | Motor Vel. | Unique Ratio | Degen (%) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `cognitivo_executivo` | 4 | 17.36 | 0.9106 | 329.07 | 0.379 | 50.0% |
| `gemma-4-12B-it` | **BASAL** | `swe_competition` | 6 | 17.55 | 0.8039 | 288.63 | 0.542 | 16.7% |
| `gemma-4-12B-it` | **BASAL** | `swe_ood45` | 2 | 18.36 | 0.8275 | 324.10 | 0.360 | 50.0% |
| `gemma-4-12B-it` | **BASAL** | `v10_subjectivity` | 40 | 17.99 | 0.8081 | 335.74 | 0.626 | 0.0% |
| `gemma-4-12B-it` | **BASAL** | `v11_multiturn_series` | 18 | 19.55 | 0.7854 | 300.81 | 0.633 | 0.0% |
| `gemma-4-12B-it` | **MODULATED** | `v10_subjectivity` | 16 | 18.28 | 0.7998 | 346.27 | 0.621 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `cognitivo_executivo` | 4 | 16.41 | 0.7863 | 175.11 | 0.396 | 50.0% |
| `gemma-4-E4B-it` | **BASAL** | `swe_competition` | 6 | 15.62 | 0.8724 | 207.42 | 0.551 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `swe_ood45` | 2 | 15.01 | 0.8330 | 207.20 | 0.592 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v10_subjectivity` | 40 | 15.63 | 0.7770 | 272.30 | 0.649 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v11_multiturn_series` | 18 | 16.02 | 0.7539 | 262.72 | 0.667 | 0.0% |
| `gemma-4-E4B-it` | **MODULATED** | `v10_subjectivity` | 23 | 15.22 | 0.8032 | 268.14 | 0.648 | 0.0% |

### C. Acoplamento Escalas $\leftrightarrow$ Estado MPS $\leftrightarrow$ Camada Motor

- **`gemma-4-12B-it` ($N=86$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = -0.149$, $r(T, \text{mps\_drift}) = -0.089$, $r(T, \text{unique\_ratio}) = -0.027$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.107$
- **`gemma-4-E4B-it` ($N=93$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = -0.057$, $r(T, \text{mps\_drift}) = -0.294$, $r(T, \text{unique\_ratio}) = +0.035$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.090$

## Snapshot de Auditoria SWE — `2026-11-05T15:36:01.747903+00:00` (`185/280` turnos concluídos) `[DADO]`

### A. Estado por Modelo, Fase (`BASAL` vs `MODULATED`) e Sub-Braço de Escala

| Modelo | Fase | Sub-Braço | Turnos | $T$ Médio | $\Delta T$ | $\Psi$ | $R_{\text{pair}}$ | MPS $\chi_{\text{eff}}$ | MPS $PR_{\text{traj}}$ | MPS Drift | IPR | Morf. | Motor Vel. | Motor Acc. | Motor Drift | Action Mk | Unique Ratio | Degen (%) | Lat (s) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `BASAL_PURE` | 70 | 0.200 | +0.000 | 0.487 | 0.9947 | **18.33** | 11.40 | **0.8083** | 0.0643 | 0.6222 | **322.01** | 557.81 | 0.7880 | 0.91 | **0.599** | 5.7% | 67.2 |
| `gemma-4-12B-it` | **MODULATED** | `M1_scale_minus_delta` | 5 | 0.130 | -0.070 | 0.487 | 0.9941 | **18.82** | 12.22 | **0.8366** | 0.0583 | 0.6222 | **334.57** | 578.67 | 0.8223 | 0.00 | **0.622** | 0.0% | 88.7 |
| `gemma-4-12B-it` | **MODULATED** | `M2_scale_plus_delta` | 5 | 0.280 | +0.080 | 0.487 | 0.9947 | **17.68** | 12.11 | **0.7651** | 0.0696 | 0.6222 | **353.99** | 615.65 | 0.8063 | 0.00 | **0.635** | 0.0% | 69.4 |
| `gemma-4-12B-it` | **MODULATED** | `M3_freud10d_inrc_kuramoto` | 5 | 0.090 | -0.110 | 0.487 | 0.9947 | **17.72** | 11.25 | **0.8421** | 0.0646 | 0.6222 | **349.24** | 603.23 | 0.7960 | 0.00 | **0.602** | 0.0% | 84.0 |
| `gemma-4-12B-it` | **MODULATED** | `M4_closed_loop_mps_motor` | 4 | 0.095 | -0.105 | 0.487 | 0.9947 | **18.63** | 10.42 | **0.7547** | 0.0696 | 0.6222 | **355.39** | 612.89 | 0.8243 | 0.00 | **0.640** | 0.0% | 69.5 |
| `gemma-4-E4B-it` | **BASAL** | `BASAL_PURE` | 70 | 0.200 | +0.000 | 0.487 | 0.9947 | **15.76** | 16.46 | **0.7813** | 0.1686 | 0.6222 | **256.86** | 444.28 | 0.7235 | 0.53 | **0.629** | 2.9% | 61.5 |
| `gemma-4-E4B-it` | **MODULATED** | `M1_scale_minus_delta` | 7 | 0.130 | -0.070 | 0.487 | 0.9943 | **14.78** | 16.42 | **0.8075** | 0.1728 | 0.6222 | **270.98** | 466.97 | 0.7427 | 0.00 | **0.649** | 0.0% | 77.1 |
| `gemma-4-E4B-it` | **MODULATED** | `M2_scale_plus_delta` | 7 | 0.280 | +0.080 | 0.487 | 0.9947 | **15.76** | 15.76 | **0.7222** | 0.1726 | 0.6222 | **271.59** | 467.99 | 0.5667 | 0.00 | **0.672** | 0.0% | 60.1 |
| `gemma-4-E4B-it` | **MODULATED** | `M3_freud10d_inrc_kuramoto` | 6 | 0.090 | -0.110 | 0.487 | 0.9947 | **14.79** | 17.13 | **0.8998** | 0.1637 | 0.6222 | **266.55** | 463.39 | 0.8017 | 0.00 | **0.632** | 0.0% | 77.9 |
| `gemma-4-E4B-it` | **MODULATED** | `M4_closed_loop_mps_motor` | 6 | 0.098 | -0.102 | 0.487 | 0.9947 | **15.63** | 16.14 | **0.7480** | 0.1704 | 0.6222 | **269.10** | 468.07 | 0.6612 | 0.00 | **0.644** | 0.0% | 71.6 |

### B. Decomposição por Etapa/Processo da Bateria (`v10`, `cognitivo`, `v11`, `swe`)

| Modelo | Fase | Etapa/Processo | Turnos | MPS $\chi_{\text{eff}}$ | MPS Drift | Motor Vel. | Unique Ratio | Degen (%) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `cognitivo_executivo` | 4 | 17.36 | 0.9106 | 329.07 | 0.379 | 50.0% |
| `gemma-4-12B-it` | **BASAL** | `swe_competition` | 6 | 17.55 | 0.8039 | 288.63 | 0.542 | 16.7% |
| `gemma-4-12B-it` | **BASAL** | `swe_ood45` | 2 | 18.36 | 0.8275 | 324.10 | 0.360 | 50.0% |
| `gemma-4-12B-it` | **BASAL** | `v10_subjectivity` | 40 | 17.99 | 0.8081 | 335.74 | 0.626 | 0.0% |
| `gemma-4-12B-it` | **BASAL** | `v11_multiturn_series` | 18 | 19.55 | 0.7854 | 300.81 | 0.633 | 0.0% |
| `gemma-4-12B-it` | **MODULATED** | `v10_subjectivity` | 19 | 18.19 | 0.8020 | 347.92 | 0.624 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `cognitivo_executivo` | 4 | 16.41 | 0.7863 | 175.11 | 0.396 | 50.0% |
| `gemma-4-E4B-it` | **BASAL** | `swe_competition` | 6 | 15.62 | 0.8724 | 207.42 | 0.551 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `swe_ood45` | 2 | 15.01 | 0.8330 | 207.20 | 0.592 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v10_subjectivity` | 40 | 15.63 | 0.7770 | 272.30 | 0.649 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v11_multiturn_series` | 18 | 16.02 | 0.7539 | 262.72 | 0.667 | 0.0% |
| `gemma-4-E4B-it` | **MODULATED** | `v10_subjectivity` | 26 | 15.24 | 0.7921 | 269.69 | 0.650 | 0.0% |

### C. Acoplamento Escalas $\leftrightarrow$ Estado MPS $\leftrightarrow$ Camada Motor

- **`gemma-4-12B-it` ($N=89$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = -0.156$, $r(T, \text{mps\_drift}) = -0.094$, $r(T, \text{unique\_ratio}) = -0.023$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.123$
- **`gemma-4-E4B-it` ($N=96$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = -0.063$, $r(T, \text{mps\_drift}) = -0.267$, $r(T, \text{unique\_ratio}) = +0.028$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.100$

## Snapshot de Auditoria SWE — `2026-11-05T15:42:03.193801+00:00` (`193/280` turnos concluídos) `[DADO]`

### A. Estado por Modelo, Fase (`BASAL` vs `MODULATED`) e Sub-Braço de Escala

| Modelo | Fase | Sub-Braço | Turnos | $T$ Médio | $\Delta T$ | $\Psi$ | $R_{\text{pair}}$ | MPS $\chi_{\text{eff}}$ | MPS $PR_{\text{traj}}$ | MPS Drift | IPR | Morf. | Motor Vel. | Motor Acc. | Motor Drift | Action Mk | Unique Ratio | Degen (%) | Lat (s) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `BASAL_PURE` | 70 | 0.200 | +0.000 | 0.487 | 0.9947 | **18.33** | 11.40 | **0.8083** | 0.0643 | 0.6222 | **322.01** | 557.81 | 0.7880 | 0.91 | **0.599** | 5.7% | 67.2 |
| `gemma-4-12B-it` | **MODULATED** | `M1_scale_minus_delta` | 6 | 0.130 | -0.070 | 0.487 | 0.9942 | **19.00** | 11.88 | **0.8720** | 0.0566 | 0.6222 | **337.09** | 582.96 | 0.8187 | 0.00 | **0.624** | 0.0% | 93.3 |
| `gemma-4-12B-it` | **MODULATED** | `M2_scale_plus_delta` | 6 | 0.280 | +0.080 | 0.487 | 0.9947 | **17.68** | 11.76 | **0.7621** | 0.0695 | 0.6222 | **358.30** | 623.79 | 0.8123 | 0.00 | **0.634** | 0.0% | 70.5 |
| `gemma-4-12B-it` | **MODULATED** | `M3_freud10d_inrc_kuramoto` | 6 | 0.090 | -0.110 | 0.487 | 0.9947 | **17.65** | 11.19 | **0.8361** | 0.0650 | 0.6222 | **352.34** | 608.54 | 0.8067 | 0.00 | **0.601** | 0.0% | 86.4 |
| `gemma-4-12B-it` | **MODULATED** | `M4_closed_loop_mps_motor` | 5 | 0.094 | -0.106 | 0.487 | 0.9947 | **18.42** | 10.96 | **0.7548** | 0.0695 | 0.6222 | **358.91** | 620.34 | 0.8074 | 0.00 | **0.633** | 0.0% | 71.5 |
| `gemma-4-E4B-it` | **BASAL** | `BASAL_PURE` | 70 | 0.200 | +0.000 | 0.487 | 0.9947 | **15.76** | 16.46 | **0.7813** | 0.1686 | 0.6222 | **256.86** | 444.28 | 0.7235 | 0.53 | **0.629** | 2.9% | 61.5 |
| `gemma-4-E4B-it` | **MODULATED** | `M1_scale_minus_delta` | 8 | 0.130 | -0.070 | 0.487 | 0.9944 | **15.04** | 16.53 | **0.8045** | 0.1705 | 0.6222 | **270.66** | 467.73 | 0.7476 | 0.00 | **0.647** | 0.0% | 79.9 |
| `gemma-4-E4B-it` | **MODULATED** | `M2_scale_plus_delta` | 8 | 0.280 | +0.080 | 0.487 | 0.9947 | **15.86** | 15.94 | **0.7198** | 0.1716 | 0.6222 | **271.35** | 468.04 | 0.5704 | 0.00 | **0.666** | 0.0% | 61.9 |
| `gemma-4-E4B-it` | **MODULATED** | `M3_freud10d_inrc_kuramoto` | 7 | 0.090 | -0.110 | 0.487 | 0.9947 | **14.91** | 17.32 | **0.8679** | 0.1654 | 0.6222 | **268.16** | 466.39 | 0.7690 | 0.00 | **0.639** | 0.0% | 80.3 |
| `gemma-4-E4B-it` | **MODULATED** | `M4_closed_loop_mps_motor` | 7 | 0.097 | -0.103 | 0.487 | 0.9947 | **15.73** | 16.28 | **0.7456** | 0.1705 | 0.6222 | **270.19** | 470.54 | 0.6582 | 0.00 | **0.646** | 0.0% | 75.4 |

### B. Decomposição por Etapa/Processo da Bateria (`v10`, `cognitivo`, `v11`, `swe`)

| Modelo | Fase | Etapa/Processo | Turnos | MPS $\chi_{\text{eff}}$ | MPS Drift | Motor Vel. | Unique Ratio | Degen (%) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `cognitivo_executivo` | 4 | 17.36 | 0.9106 | 329.07 | 0.379 | 50.0% |
| `gemma-4-12B-it` | **BASAL** | `swe_competition` | 6 | 17.55 | 0.8039 | 288.63 | 0.542 | 16.7% |
| `gemma-4-12B-it` | **BASAL** | `swe_ood45` | 2 | 18.36 | 0.8275 | 324.10 | 0.360 | 50.0% |
| `gemma-4-12B-it` | **BASAL** | `v10_subjectivity` | 40 | 17.99 | 0.8081 | 335.74 | 0.626 | 0.0% |
| `gemma-4-12B-it` | **BASAL** | `v11_multiturn_series` | 18 | 19.55 | 0.7854 | 300.81 | 0.633 | 0.0% |
| `gemma-4-12B-it` | **MODULATED** | `v10_subjectivity` | 23 | 18.18 | 0.8085 | 351.34 | 0.622 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `cognitivo_executivo` | 4 | 16.41 | 0.7863 | 175.11 | 0.396 | 50.0% |
| `gemma-4-E4B-it` | **BASAL** | `swe_competition` | 6 | 15.62 | 0.8724 | 207.42 | 0.551 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `swe_ood45` | 2 | 15.01 | 0.8330 | 207.20 | 0.592 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v10_subjectivity` | 40 | 15.63 | 0.7770 | 272.30 | 0.649 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v11_multiturn_series` | 18 | 16.02 | 0.7539 | 262.72 | 0.667 | 0.0% |
| `gemma-4-E4B-it` | **MODULATED** | `v10_subjectivity` | 30 | 15.39 | 0.7829 | 270.15 | 0.650 | 0.0% |

### C. Acoplamento Escalas $\leftrightarrow$ Estado MPS $\leftrightarrow$ Camada Motor

- **`gemma-4-12B-it` ($N=93$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = -0.178$, $r(T, \text{mps\_drift}) = -0.127$, $r(T, \text{unique\_ratio}) = -0.018$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.135$
- **`gemma-4-E4B-it` ($N=100$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = -0.079$, $r(T, \text{mps\_drift}) = -0.226$, $r(T, \text{unique\_ratio}) = +0.008$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.085$

### Parecer Técnico SWE (Ciclo 19 - Comparação Pareada Basal vs Modulado M1..M4 em `v10_subjectivity`)

**Escopo**: 195 turnos (`ts` máx. `2026-11-05T15:43:00Z`, leitura `mode=ro` sobre WAL ativo): 140 `BASAL` + 55 `MODULATED` (12B: 24, turnos 71–94, cenas 1–12; E4B: 31, turnos 71–101, cenas 1–15 fase1). **Integridade** `[DADO]`: 55/55 linhas moduladas `intervention_enabled=1`, 140/140 basais `intervention_enabled=0`; todos os 55 turnos modulados são `v10_subjectivity` e têm homólogo basal por `(model_tag, task_id)` — cobertura de pareamento 100%. Zero `degenerate_flag`/`action_markers`/`thinking_chars` nos turnos modulados. Escalas soberanas bit-a-bit idênticas aos homólogos em 53/53 pares limpos — covariável temporal confirmada `[DADO]`. **Sentinelas transitórios** `[DADO]+[INTERPRETAÇÃO]`: turnos com `ipr=0.0`/`morph=0.5` ocorrem apenas nos turnos modulados **mais recentes** (t94/t95 12B, t101/t102 E4B na leitura final) e são **reescritos** com valores reais quando a sonda MPS completa — os sentinelas do Ciclo 14 (t75/t76) e os t90–t99 já foram preenchidos; excluídos 2 pares (t94 12B-M4, t101 E4B-M3) do pareamento fino. Tratar sentinela como *estado transiente write-then-probe*, não como perda — re-consultar antes de excluir.

**(1) Diferencial pareado MODULATED − BASAL (mesmo `task_id`, mesmo modelo; pares limpos)** `[DERIVADO]`:

`gemma-4-12B-it` (`:8098`, $n=23$ pares):

| Sub-braço | $n$ | $\Delta\chi_{\text{eff}}$ | $\Delta$ `contract_drift` | $\Delta$ motor vel. | $\Delta$ `cos_drift` | $\Delta$ `unique_ratio` | Excursões gate (mod vs basal) |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 ($T{=}0.13$, `C`) | 6 | $+0.10 \pm 1.79$ | $-0.014 \pm 0.126$ (med $+0.008$) | $-3.1 \pm 20.0$ | $-0.005$ (4/6↓) | $+0.003$ | 4/6 vs 6/6 |
| M2 ($T{=}0.28$, `R`) | 6 | $+0.19 \pm 0.31$ | $-0.003 \pm 0.048$ (4/6↓) | $\mathbf{+22.1} \pm 27.5$ (4/6↑, med $+23.1$) | $+0.006$ | $-0.014$ (4/6↓) | 0/6 vs 1/6 |
| M3 ($T{=}0.09$, `R+C`) | 6 | $-0.85 \pm 0.99$ (4/6↓) | $\mathbf{-0.037} \pm 0.093$ (**5/6↓**, med $-0.024$) | $\mathbf{+25.9} \pm 24.5$ (4/6↑, med $+28.3$) | $\mathbf{-0.059} \pm 0.155$ (4/6↓) | $-0.013$ (4/6↓) | 2/6 vs 4/6 |
| M4 (closed-loop) | 5 | $+0.86 \pm 1.43$ (**5/5↑**) | $-0.009 \pm 0.032$ | $+10.8 \pm 31.8$ | $-0.007$ | $+0.000$ | 0/5 vs 0/5 |
| **Pooled** | 23 | $+0.04$ | $-0.016$ (13/23↓) | $+14.1$ (14/23↑) | $-0.016$ (14/23↓) | $-0.006$ | **6/23 vs 11/23** |

`gemma-4-E4B-it` (`:8099`, $n=30$ pares):

| Sub-braço | $n$ | $\Delta\chi_{\text{eff}}$ | $\Delta$ `contract_drift` | $\Delta$ motor vel. | $\Delta$ `cos_drift` | $\Delta$ `unique_ratio` | Excursões gate (mod vs basal) |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 ($T{=}0.13$, `C`) | 8 | $-0.32 \pm 0.95$ (6/8↓) | $+0.004 \pm 0.043$ (med $-0.016$, 5/8↓) | $-8.2 \pm 15.8$ (5/8↓) | $+0.005$ | $\pm 0.000$ | 4/8 vs 5/8 |
| M2 ($T{=}0.28$, `R`) | 8 | $-0.19 \pm 0.81$ (5/8↓) | $+0.003 \pm 0.051$ | $+0.8 \pm 22.2$ (med $-1.5$) | $-0.019 \pm 0.059$ (5/8↓) | $\mathbf{+0.021} \pm 0.032$ (**7/8↑**) | 0/8 vs 0/8 |
| M3 ($T{=}0.09$, `R+C`) | 7 | $-0.58 \pm 1.33$ (5/7↓) | $+0.001 \pm 0.091$ (med $-0.012$, 5/7↓) | $-3.2 \pm 15.5$ (5/7↓) | $\mathbf{-0.051} \pm 0.090$ (**6/7↓**) | $-0.019$ | 5/7 vs 4/7 |
| M4 (closed-loop) | 7 | $-0.34 \pm 1.18$ (5/7↓) | $+0.015 \pm 0.087$ (4/7↑) | $-5.0 \pm 16.4$ (5/7↓) | $-0.007$ | $-0.011$ | 2/7 vs 2/7 |
| **Pooled** | 30 | $-0.35$ (**21/30↓**) | $+0.006$ (17/30↓) | $-3.9$ (**20/30↓**) | $-0.017$ (18/30↓) | $-0.002$ | 11/30 vs 11/30 |

**(2) Quais sub-braços reduzem `contract_drift` e aumentam velocidade/diversidade lexical** `[DERIVADO]+[INTERPRETAÇÃO]`: **12B — o M3 (Freud10D+INRC+Kuramoto) é o único braço com assinatura completa e coerente**: reduz `contract_drift` em 5/6 pares ($-0.037$, med $-0.024$), acelera o motor ($+25.9$, med $+28.3$) e reduz a deriva direcional ($-0.059$, 4/6↓), cortando pela metade as excursões de gate vs homólogos basais ($2/6$ vs $4/6$); ao custo de $\chi_{\text{eff}}$ $-0.85$ e leve queda lexical. **M2 acelera** ($+22.1$, 4/6↑) com drift neutro, mas **reduz** `unique_ratio` ($-0.014$, 4/6↓) — no 12B a diversidade lexical nunca melhora em nenhum braço. **M4 é drift-neutro** ($-0.009$) mas expande $\chi_{\text{eff}}$ em **5/5** pares ($+0.86$) e mantém velocidade $+10.8$; os 5 turnos M4 do 12B ficaram todos abaixo do gatilho próprio ($0.71$–$0.78 < 0.826$) e do $\mu$ basal ($0.808$). **E4B — nenhum braço reduz `contract_drift` em média** ($+0.001$ a $+0.015$; as medianas negativas de M1/M3, $-0.016$/$-0.012$, refletem maioria de pares ↓ anulada pelos picos precoces t73 $+0.111$ e t81 $+0.133$) e **nenhum acelera o motor** (todos $\le +0.8$; pooled $-3.9$, 20/30↓). O único efeito lexical positivo do ciclo é o **M2 no E4B** ($+0.021$, 7/8↑) — coincidindo com o braço de $T$ **maior** ($+0.08$) — junto com `cos_drift` $-0.019$ (5/8↓). M3-E4B é o melhor redutor de `cos_drift` ($-0.051$, 6/7↓) mas **aumenta** excursões de gate ($5/7$ vs $4/7$). M4-E4B **piora** o drift ($+0.015$, 4/7↑): 2/7 turnos M4 ainda excedem o gatilho (t78 $0.849$, t86 $0.910$ — o pior par, $\Delta+0.191$), contra $0/5$ no 12B — a correção promissora do Ciclo 14 ($n=1$, t74) **não generalizou** `[INTERPRETAÇÃO]`. Síntese: a modulação **beneficia o 12B** (velocidade $+14.1$ pooled, excursões $6/23$ vs $11/23$ basal) e é **neutra-a-levemente-adversa no E4B** (velocidade $-3.9$, excursões inalteradas $11/30$); o ganho de velocidade é fenômeno exclusivo do 12B `[INTERPRETAÇÃO]`.

**Confundidores estruturais** `[DADO código]+[LIMITE]`: (i) sub-braço $\equiv$ fase do prompt — M1/M3 só observados em `fase1` (prompt curto), M2/M4 só em `fase2` (contexto acumulado); comparações M3-vs-M4 cruzam esse eixo e devem ser lidas intra-fase (M1↔M3, M2↔M4). (ii) O gate M4 lê `prev_mps` do turno anterior — frequentemente um turno M3 de drift elevado — herdando estado entre sub-braços (já notado no Ciclo 14). (iii) Custo de injeção: latência $+9.3$ s (12B)/$+6.8$ s (E4B) e `prompt_tokens` $+66$ (M1/M2/M4) a $+259$ (M3) vs homólogos, com `gen_tokens` $\approx 0$ — a diretriz entra no prompt, não na saída.

**Caveats** `[LIMITE]`: $n=5$–$8$ por braço/modelo — teste de sinais exige $\ge 7/8$ para $p<0.10$ e nada atinge $p<0.05$ formal (melhor: M2-E4B `unique_ratio` 7/8, $p\approx0.07$); todos os efeitos são **direcionais**, aguardando o 2º ciclo completo de cenas para Wilcoxon. `contract_drift` basal em `fase2` já é baixo ($\sim$$0.71$–$0.77$) — pouco espaço para o M4 mostrar correção nesses pares; seu valor real se medirá nos blocos `cognitivo`/`swe` modulados (drift basal $0.79$–$0.96$), ainda não iniciados.

## Snapshot de Auditoria SWE — `2026-11-05T15:47:18.793745+00:00` (`200/280` turnos concluídos) `[DADO]`

### A. Estado por Modelo, Fase (`BASAL` vs `MODULATED`) e Sub-Braço de Escala

| Modelo | Fase | Sub-Braço | Turnos | $T$ Médio | $\Delta T$ | $\Psi$ | $R_{\text{pair}}$ | MPS $\chi_{\text{eff}}$ | MPS $PR_{\text{traj}}$ | MPS Drift | IPR | Morf. | Motor Vel. | Motor Acc. | Motor Drift | Action Mk | Unique Ratio | Degen (%) | Lat (s) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `BASAL_PURE` | 70 | 0.200 | +0.000 | 0.487 | 0.9947 | **18.33** | 11.40 | **0.8083** | 0.0643 | 0.6222 | **322.01** | 557.81 | 0.7880 | 0.91 | **0.599** | 5.7% | 67.2 |
| `gemma-4-12B-it` | **MODULATED** | `M1_scale_minus_delta` | 7 | 0.130 | -0.070 | 0.487 | 0.9943 | **18.78** | 11.82 | **0.8568** | 0.0583 | 0.6222 | **335.55** | 580.50 | 0.8120 | 0.00 | **0.623** | 0.0% | 95.6 |
| `gemma-4-12B-it` | **MODULATED** | `M2_scale_plus_delta` | 7 | 0.280 | +0.080 | 0.487 | 0.9947 | **17.69** | 11.88 | **0.7602** | 0.0691 | 0.6222 | **353.26** | 615.01 | 0.8121 | 0.00 | **0.632** | 0.0% | 72.7 |
| `gemma-4-12B-it` | **MODULATED** | `M3_freud10d_inrc_kuramoto` | 6 | 0.090 | -0.110 | 0.487 | 0.9947 | **17.65** | 11.19 | **0.8361** | 0.0650 | 0.6222 | **352.34** | 608.54 | 0.8067 | 0.00 | **0.601** | 0.0% | 86.4 |
| `gemma-4-12B-it` | **MODULATED** | `M4_closed_loop_mps_motor` | 6 | 0.093 | -0.107 | 0.487 | 0.9947 | **18.30** | 11.21 | **0.7531** | 0.0691 | 0.6222 | **347.98** | 601.34 | 0.8027 | 0.00 | **0.634** | 0.0% | 74.3 |
| `gemma-4-E4B-it` | **BASAL** | `BASAL_PURE` | 70 | 0.200 | +0.000 | 0.487 | 0.9947 | **15.76** | 16.46 | **0.7813** | 0.1686 | 0.6222 | **256.86** | 444.28 | 0.7235 | 0.53 | **0.629** | 2.9% | 61.5 |
| `gemma-4-E4B-it` | **MODULATED** | `M1_scale_minus_delta` | 9 | 0.130 | -0.070 | 0.487 | 0.9944 | **14.96** | 16.63 | **0.8145** | 0.1735 | 0.6222 | **271.33** | 469.11 | 0.7520 | 0.00 | **0.650** | 0.0% | 82.1 |
| `gemma-4-E4B-it` | **MODULATED** | `M2_scale_plus_delta` | 9 | 0.280 | +0.080 | 0.487 | 0.9947 | **15.91** | 15.98 | **0.7386** | 0.1710 | 0.6222 | **269.66** | 465.49 | 0.5985 | 0.00 | **0.668** | 0.0% | 66.5 |
| `gemma-4-E4B-it` | **MODULATED** | `M3_freud10d_inrc_kuramoto` | 8 | 0.090 | -0.110 | 0.487 | 0.9947 | **14.84** | 17.35 | **0.8626** | 0.1662 | 0.6222 | **269.43** | 468.23 | 0.7709 | 0.00 | **0.644** | 0.0% | 82.3 |
| `gemma-4-E4B-it` | **MODULATED** | `M4_closed_loop_mps_motor` | 8 | 0.098 | -0.103 | 0.487 | 0.9947 | **15.70** | 16.32 | **0.7408** | 0.1711 | 0.6222 | **271.00** | 471.19 | 0.6526 | 0.00 | **0.648** | 0.0% | 74.7 |

### B. Decomposição por Etapa/Processo da Bateria (`v10`, `cognitivo`, `v11`, `swe`)

| Modelo | Fase | Etapa/Processo | Turnos | MPS $\chi_{\text{eff}}$ | MPS Drift | Motor Vel. | Unique Ratio | Degen (%) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `cognitivo_executivo` | 4 | 17.36 | 0.9106 | 329.07 | 0.379 | 50.0% |
| `gemma-4-12B-it` | **BASAL** | `swe_competition` | 6 | 17.55 | 0.8039 | 288.63 | 0.542 | 16.7% |
| `gemma-4-12B-it` | **BASAL** | `swe_ood45` | 2 | 18.36 | 0.8275 | 324.10 | 0.360 | 50.0% |
| `gemma-4-12B-it` | **BASAL** | `v10_subjectivity` | 40 | 17.99 | 0.8081 | 335.74 | 0.626 | 0.0% |
| `gemma-4-12B-it` | **BASAL** | `v11_multiturn_series` | 18 | 19.55 | 0.7854 | 300.81 | 0.633 | 0.0% |
| `gemma-4-12B-it` | **MODULATED** | `v10_subjectivity` | 26 | 18.12 | 0.8021 | 347.06 | 0.623 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `cognitivo_executivo` | 4 | 16.41 | 0.7863 | 175.11 | 0.396 | 50.0% |
| `gemma-4-E4B-it` | **BASAL** | `swe_competition` | 6 | 15.62 | 0.8724 | 207.42 | 0.551 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `swe_ood45` | 2 | 15.01 | 0.8330 | 207.20 | 0.592 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v10_subjectivity` | 40 | 15.63 | 0.7770 | 272.30 | 0.649 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v11_multiturn_series` | 18 | 16.02 | 0.7539 | 262.72 | 0.667 | 0.0% |
| `gemma-4-E4B-it` | **MODULATED** | `v10_subjectivity` | 34 | 15.36 | 0.7884 | 270.36 | 0.653 | 0.0% |

### C. Acoplamento Escalas $\leftrightarrow$ Estado MPS $\leftrightarrow$ Camada Motor

- **`gemma-4-12B-it` ($N=96$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = -0.141$, $r(T, \text{mps\_drift}) = -0.110$, $r(T, \text{unique\_ratio}) = -0.024$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.125$
- **`gemma-4-E4B-it` ($N=104$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = -0.103$, $r(T, \text{mps\_drift}) = -0.195$, $r(T, \text{unique\_ratio}) = -0.002$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.102$

## Snapshot de Auditoria SWE — `2026-11-05T15:52:30.047038+00:00` (`205/280` turnos concluídos) `[DADO]`

### A. Estado por Modelo, Fase (`BASAL` vs `MODULATED`) e Sub-Braço de Escala

| Modelo | Fase | Sub-Braço | Turnos | $T$ Médio | $\Delta T$ | $\Psi$ | $R_{\text{pair}}$ | MPS $\chi_{\text{eff}}$ | MPS $PR_{\text{traj}}$ | MPS Drift | IPR | Morf. | Motor Vel. | Motor Acc. | Motor Drift | Action Mk | Unique Ratio | Degen (%) | Lat (s) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `BASAL_PURE` | 70 | 0.200 | +0.000 | 0.487 | 0.9947 | **18.33** | 11.40 | **0.8083** | 0.0643 | 0.6222 | **322.01** | 557.81 | 0.7880 | 0.91 | **0.599** | 5.7% | 67.2 |
| `gemma-4-12B-it` | **MODULATED** | `M1_scale_minus_delta` | 8 | 0.130 | -0.070 | 0.487 | 0.9944 | **18.73** | 11.42 | **0.8697** | 0.0577 | 0.6222 | **334.67** | 577.89 | 0.8168 | 0.00 | **0.621** | 0.0% | 97.9 |
| `gemma-4-12B-it` | **MODULATED** | `M2_scale_plus_delta` | 7 | 0.280 | +0.080 | 0.487 | 0.9947 | **17.69** | 11.88 | **0.7602** | 0.0691 | 0.6222 | **353.26** | 615.01 | 0.8121 | 0.00 | **0.632** | 0.0% | 72.7 |
| `gemma-4-12B-it` | **MODULATED** | `M3_freud10d_inrc_kuramoto` | 7 | 0.090 | -0.110 | 0.487 | 0.9947 | **17.67** | 11.36 | **0.8323** | 0.0654 | 0.6222 | **349.36** | 603.39 | 0.8120 | 0.00 | **0.605** | 0.0% | 87.0 |
| `gemma-4-12B-it` | **MODULATED** | `M4_closed_loop_mps_motor` | 7 | 0.093 | -0.107 | 0.487 | 0.9947 | **18.24** | 11.30 | **0.7558** | 0.0691 | 0.6222 | **351.48** | 608.13 | 0.8087 | 0.00 | **0.635** | 0.0% | 75.8 |
| `gemma-4-E4B-it` | **BASAL** | `BASAL_PURE` | 70 | 0.200 | +0.000 | 0.487 | 0.9947 | **15.76** | 16.46 | **0.7813** | 0.1686 | 0.6222 | **256.86** | 444.28 | 0.7235 | 0.53 | **0.629** | 2.9% | 61.5 |
| `gemma-4-E4B-it` | **MODULATED** | `M1_scale_minus_delta` | 9 | 0.130 | -0.070 | 0.487 | 0.9944 | **14.96** | 16.63 | **0.8145** | 0.1735 | 0.6222 | **271.33** | 469.11 | 0.7520 | 0.00 | **0.650** | 0.0% | 82.1 |
| `gemma-4-E4B-it` | **MODULATED** | `M2_scale_plus_delta` | 9 | 0.280 | +0.080 | 0.487 | 0.9947 | **15.91** | 15.98 | **0.7386** | 0.1710 | 0.6222 | **269.66** | 465.49 | 0.5985 | 0.00 | **0.668** | 0.0% | 66.5 |
| `gemma-4-E4B-it` | **MODULATED** | `M3_freud10d_inrc_kuramoto` | 9 | 0.090 | -0.110 | 0.487 | 0.9947 | **14.88** | 17.07 | **0.8717** | 0.1656 | 0.6222 | **268.88** | 467.04 | 0.7776 | 0.00 | **0.643** | 0.0% | 85.7 |
| `gemma-4-E4B-it` | **MODULATED** | `M4_closed_loop_mps_motor` | 9 | 0.098 | -0.102 | 0.487 | 0.9947 | **15.76** | 16.25 | **0.7451** | 0.1716 | 0.6222 | **270.16** | 469.89 | 0.6499 | 0.00 | **0.644** | 0.0% | 76.9 |

### B. Decomposição por Etapa/Processo da Bateria (`v10`, `cognitivo`, `v11`, `swe`)

| Modelo | Fase | Etapa/Processo | Turnos | MPS $\chi_{\text{eff}}$ | MPS Drift | Motor Vel. | Unique Ratio | Degen (%) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `cognitivo_executivo` | 4 | 17.36 | 0.9106 | 329.07 | 0.379 | 50.0% |
| `gemma-4-12B-it` | **BASAL** | `swe_competition` | 6 | 17.55 | 0.8039 | 288.63 | 0.542 | 16.7% |
| `gemma-4-12B-it` | **BASAL** | `swe_ood45` | 2 | 18.36 | 0.8275 | 324.10 | 0.360 | 50.0% |
| `gemma-4-12B-it` | **BASAL** | `v10_subjectivity` | 40 | 17.99 | 0.8081 | 335.74 | 0.626 | 0.0% |
| `gemma-4-12B-it` | **BASAL** | `v11_multiturn_series` | 18 | 19.55 | 0.7854 | 300.81 | 0.633 | 0.0% |
| `gemma-4-12B-it` | **MODULATED** | `v10_subjectivity` | 29 | 18.11 | 0.8068 | 346.76 | 0.623 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `cognitivo_executivo` | 4 | 16.41 | 0.7863 | 175.11 | 0.396 | 50.0% |
| `gemma-4-E4B-it` | **BASAL** | `swe_competition` | 6 | 15.62 | 0.8724 | 207.42 | 0.551 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `swe_ood45` | 2 | 15.01 | 0.8330 | 207.20 | 0.592 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v10_subjectivity` | 40 | 15.63 | 0.7770 | 272.30 | 0.649 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v11_multiturn_series` | 18 | 16.02 | 0.7539 | 262.72 | 0.667 | 0.0% |
| `gemma-4-E4B-it` | **MODULATED** | `v10_subjectivity` | 36 | 15.38 | 0.7925 | 270.01 | 0.651 | 0.0% |

### C. Acoplamento Escalas $\leftrightarrow$ Estado MPS $\leftrightarrow$ Camada Motor

- **`gemma-4-12B-it` ($N=99$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = -0.167$, $r(T, \text{mps\_drift}) = -0.117$, $r(T, \text{unique\_ratio}) = -0.039$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.129$
- **`gemma-4-E4B-it` ($N=106$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = -0.103$, $r(T, \text{mps\_drift}) = -0.218$, $r(T, \text{unique\_ratio}) = +0.004$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.102$

## Snapshot de Auditoria SWE — `2026-11-05T15:57:57.862827+00:00` (`213/280` turnos concluídos) `[DADO]`

### A. Estado por Modelo, Fase (`BASAL` vs `MODULATED`) e Sub-Braço de Escala

| Modelo | Fase | Sub-Braço | Turnos | $T$ Médio | $\Delta T$ | $\Psi$ | $R_{\text{pair}}$ | MPS $\chi_{\text{eff}}$ | MPS $PR_{\text{traj}}$ | MPS Drift | IPR | Morf. | Motor Vel. | Motor Acc. | Motor Drift | Action Mk | Unique Ratio | Degen (%) | Lat (s) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `BASAL_PURE` | 70 | 0.200 | +0.000 | 0.487 | 0.9947 | **18.33** | 11.40 | **0.8083** | 0.0643 | 0.6222 | **322.01** | 557.81 | 0.7880 | 0.91 | **0.599** | 5.7% | 67.2 |
| `gemma-4-12B-it` | **MODULATED** | `M1_scale_minus_delta` | 9 | 0.130 | -0.070 | 0.487 | 0.9944 | **18.42** | 11.55 | **0.8730** | 0.0597 | 0.6222 | **333.17** | 575.46 | 0.8196 | 0.00 | **0.622** | 0.0% | 98.7 |
| `gemma-4-12B-it` | **MODULATED** | `M2_scale_plus_delta` | 8 | 0.280 | +0.080 | 0.487 | 0.9947 | **17.69** | 11.71 | **0.7556** | 0.0693 | 0.6222 | **356.36** | 619.84 | 0.8069 | 0.00 | **0.625** | 0.0% | 78.7 |
| `gemma-4-12B-it` | **MODULATED** | `M3_freud10d_inrc_kuramoto` | 8 | 0.090 | -0.110 | 0.487 | 0.9947 | **17.65** | 11.61 | **0.8306** | 0.0655 | 0.6222 | **346.25** | 598.01 | 0.8205 | 0.00 | **0.609** | 0.0% | 89.3 |
| `gemma-4-12B-it` | **MODULATED** | `M4_closed_loop_mps_motor` | 8 | 0.092 | -0.107 | 0.487 | 0.9947 | **18.14** | 11.33 | **0.7516** | 0.0686 | 0.6222 | **348.65** | 603.22 | 0.8052 | 0.00 | **0.634** | 0.0% | 74.8 |
| `gemma-4-E4B-it` | **BASAL** | `BASAL_PURE` | 70 | 0.200 | +0.000 | 0.487 | 0.9947 | **15.76** | 16.46 | **0.7813** | 0.1686 | 0.6222 | **256.86** | 444.28 | 0.7235 | 0.53 | **0.629** | 2.9% | 61.5 |
| `gemma-4-E4B-it` | **MODULATED** | `M1_scale_minus_delta` | 10 | 0.130 | -0.070 | 0.487 | 0.9944 | **14.91** | 16.45 | **0.8294** | 0.1748 | 0.6222 | **269.50** | 465.97 | 0.7561 | 0.00 | **0.646** | 0.0% | 87.3 |
| `gemma-4-E4B-it` | **MODULATED** | `M2_scale_plus_delta` | 10 | 0.280 | +0.080 | 0.487 | 0.9947 | **15.98** | 15.82 | **0.7361** | 0.1704 | 0.6222 | **269.40** | 465.55 | 0.6022 | 0.00 | **0.660** | 0.0% | 68.7 |
| `gemma-4-E4B-it` | **MODULATED** | `M3_freud10d_inrc_kuramoto` | 10 | 0.090 | -0.110 | 0.487 | 0.9947 | **14.93** | 17.07 | **0.8766** | 0.1657 | 0.6222 | **267.21** | 463.50 | 0.7846 | 0.00 | **0.640** | 0.0% | 86.5 |
| `gemma-4-E4B-it` | **MODULATED** | `M4_closed_loop_mps_motor` | 10 | 0.098 | -0.102 | 0.487 | 0.9947 | **15.76** | 16.28 | **0.7380** | 0.1726 | 0.6222 | **270.50** | 470.78 | 0.6496 | 0.00 | **0.641** | 0.0% | 77.7 |

### B. Decomposição por Etapa/Processo da Bateria (`v10`, `cognitivo`, `v11`, `swe`)

| Modelo | Fase | Etapa/Processo | Turnos | MPS $\chi_{\text{eff}}$ | MPS Drift | Motor Vel. | Unique Ratio | Degen (%) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `cognitivo_executivo` | 4 | 17.36 | 0.9106 | 329.07 | 0.379 | 50.0% |
| `gemma-4-12B-it` | **BASAL** | `swe_competition` | 6 | 17.55 | 0.8039 | 288.63 | 0.542 | 16.7% |
| `gemma-4-12B-it` | **BASAL** | `swe_ood45` | 2 | 18.36 | 0.8275 | 324.10 | 0.360 | 50.0% |
| `gemma-4-12B-it` | **BASAL** | `v10_subjectivity` | 40 | 17.99 | 0.8081 | 335.74 | 0.626 | 0.0% |
| `gemma-4-12B-it` | **BASAL** | `v11_multiturn_series` | 18 | 19.55 | 0.7854 | 300.81 | 0.633 | 0.0% |
| `gemma-4-12B-it` | **MODULATED** | `v10_subjectivity` | 33 | 17.99 | 0.8048 | 345.71 | 0.622 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `cognitivo_executivo` | 4 | 16.41 | 0.7863 | 175.11 | 0.396 | 50.0% |
| `gemma-4-E4B-it` | **BASAL** | `swe_competition` | 6 | 15.62 | 0.8724 | 207.42 | 0.551 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `swe_ood45` | 2 | 15.01 | 0.8330 | 207.20 | 0.592 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v10_subjectivity` | 40 | 15.63 | 0.7770 | 272.30 | 0.649 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v11_multiturn_series` | 18 | 16.02 | 0.7539 | 262.72 | 0.667 | 0.0% |
| `gemma-4-E4B-it` | **MODULATED** | `v10_subjectivity` | 40 | 15.40 | 0.7950 | 269.15 | 0.647 | 0.0% |

### C. Acoplamento Escalas $\leftrightarrow$ Estado MPS $\leftrightarrow$ Camada Motor

- **`gemma-4-12B-it` ($N=103$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = -0.114$, $r(T, \text{mps\_drift}) = -0.124$, $r(T, \text{unique\_ratio}) = -0.058$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.125$
- **`gemma-4-E4B-it` ($N=110$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = -0.093$, $r(T, \text{mps\_drift}) = -0.237$, $r(T, \text{unique\_ratio}) = +0.005$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.092$

## Snapshot de Auditoria SWE — `2026-11-05T16:03:17.678672+00:00` (`224/280` turnos concluídos) `[DADO]`

### A. Estado por Modelo, Fase (`BASAL` vs `MODULATED`) e Sub-Braço de Escala

| Modelo | Fase | Sub-Braço | Turnos | $T$ Médio | $\Delta T$ | $\Psi$ | $R_{\text{pair}}$ | MPS $\chi_{\text{eff}}$ | MPS $PR_{\text{traj}}$ | MPS Drift | IPR | Morf. | Motor Vel. | Motor Acc. | Motor Drift | Action Mk | Unique Ratio | Degen (%) | Lat (s) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `BASAL_PURE` | 70 | 0.200 | +0.000 | 0.487 | 0.9947 | **18.33** | 11.40 | **0.8083** | 0.0643 | 0.6222 | **322.01** | 557.81 | 0.7880 | 0.91 | **0.599** | 5.7% | 67.2 |
| `gemma-4-12B-it` | **MODULATED** | `M1_scale_minus_delta` | 9 | 0.130 | -0.070 | 0.487 | 0.9944 | **18.42** | 11.55 | **0.8730** | 0.0597 | 0.6222 | **333.17** | 575.46 | 0.8196 | 0.00 | **0.622** | 0.0% | 98.7 |
| `gemma-4-12B-it` | **MODULATED** | `M2_scale_plus_delta` | 9 | 0.280 | +0.080 | 0.487 | 0.9947 | **18.05** | 11.74 | **0.7547** | 0.0686 | 0.6222 | **356.36** | 620.14 | 0.8112 | 0.00 | **0.628** | 0.0% | 80.1 |
| `gemma-4-12B-it` | **MODULATED** | `M3_freud10d_inrc_kuramoto` | 9 | 0.090 | -0.110 | 0.487 | 0.9947 | **17.81** | 11.75 | **0.8453** | 0.0661 | 0.6222 | **344.34** | 595.61 | 0.8024 | 0.00 | **0.608** | 0.0% | 91.1 |
| `gemma-4-12B-it` | **MODULATED** | `M4_closed_loop_mps_motor` | 9 | 0.093 | -0.107 | 0.487 | 0.9947 | **18.07** | 11.48 | **0.7492** | 0.0686 | 0.6222 | **347.86** | 601.08 | 0.8019 | 0.00 | **0.632** | 0.0% | 74.6 |
| `gemma-4-E4B-it` | **BASAL** | `BASAL_PURE` | 70 | 0.200 | +0.000 | 0.487 | 0.9947 | **15.76** | 16.46 | **0.7813** | 0.1686 | 0.6222 | **256.86** | 444.28 | 0.7235 | 0.53 | **0.629** | 2.9% | 61.5 |
| `gemma-4-E4B-it` | **MODULATED** | `M1_scale_minus_delta` | 12 | 0.130 | -0.070 | 0.487 | 0.9945 | **15.10** | 16.13 | **0.8103** | 0.1719 | 0.6222 | **261.25** | 450.66 | 0.7447 | 0.00 | **0.623** | 8.3% | 80.7 |
| `gemma-4-E4B-it` | **MODULATED** | `M2_scale_plus_delta` | 12 | 0.280 | +0.080 | 0.487 | 0.9947 | **15.97** | 15.26 | **0.7411** | 0.1688 | 0.6222 | **261.24** | 451.25 | 0.6217 | 0.00 | **0.640** | 0.0% | 62.8 |
| `gemma-4-E4B-it` | **MODULATED** | `M3_freud10d_inrc_kuramoto` | 12 | 0.090 | -0.110 | 0.487 | 0.9947 | **15.26** | 16.30 | **0.8681** | 0.1652 | 0.6222 | **259.05** | 448.77 | 0.7793 | 0.00 | **0.643** | 0.0% | 74.9 |
| `gemma-4-E4B-it` | **MODULATED** | `M4_closed_loop_mps_motor` | 12 | 0.097 | -0.102 | 0.487 | 0.9947 | **15.82** | 15.88 | **0.7298** | 0.1703 | 0.6222 | **269.36** | 467.54 | 0.6591 | 0.00 | **0.621** | 8.3% | 76.0 |

### B. Decomposição por Etapa/Processo da Bateria (`v10`, `cognitivo`, `v11`, `swe`)

| Modelo | Fase | Etapa/Processo | Turnos | MPS $\chi_{\text{eff}}$ | MPS Drift | Motor Vel. | Unique Ratio | Degen (%) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `cognitivo_executivo` | 4 | 17.36 | 0.9106 | 329.07 | 0.379 | 50.0% |
| `gemma-4-12B-it` | **BASAL** | `swe_competition` | 6 | 17.55 | 0.8039 | 288.63 | 0.542 | 16.7% |
| `gemma-4-12B-it` | **BASAL** | `swe_ood45` | 2 | 18.36 | 0.8275 | 324.10 | 0.360 | 50.0% |
| `gemma-4-12B-it` | **BASAL** | `v10_subjectivity` | 40 | 17.99 | 0.8081 | 335.74 | 0.626 | 0.0% |
| `gemma-4-12B-it` | **BASAL** | `v11_multiturn_series` | 18 | 19.55 | 0.7854 | 300.81 | 0.633 | 0.0% |
| `gemma-4-12B-it` | **MODULATED** | `v10_subjectivity` | 36 | 18.09 | 0.8055 | 345.43 | 0.622 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `cognitivo_executivo` | 4 | 16.41 | 0.7863 | 175.11 | 0.396 | 50.0% |
| `gemma-4-E4B-it` | **BASAL** | `swe_competition` | 6 | 15.62 | 0.8724 | 207.42 | 0.551 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `swe_ood45` | 2 | 15.01 | 0.8330 | 207.20 | 0.592 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v10_subjectivity` | 40 | 15.63 | 0.7770 | 272.30 | 0.649 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v11_multiturn_series` | 18 | 16.02 | 0.7539 | 262.72 | 0.667 | 0.0% |
| `gemma-4-E4B-it` | **MODULATED** | `cognitivo_executivo` | 4 | 16.33 | 0.8007 | 195.50 | 0.358 | 50.0% |
| `gemma-4-E4B-it` | **MODULATED** | `v10_subjectivity` | 40 | 15.40 | 0.7950 | 269.15 | 0.647 | 0.0% |
| `gemma-4-E4B-it` | **MODULATED** | `v11_multiturn_series` | 4 | 16.16 | 0.6968 | 265.69 | 0.752 | 0.0% |

### C. Acoplamento Escalas $\leftrightarrow$ Estado MPS $\leftrightarrow$ Camada Motor

- **`gemma-4-12B-it` ($N=106$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = -0.097$, $r(T, \text{mps\_drift}) = -0.149$, $r(T, \text{unique\_ratio}) = -0.043$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.104$
- **`gemma-4-E4B-it` ($N=118$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = -0.060$, $r(T, \text{mps\_drift}) = -0.189$, $r(T, \text{unique\_ratio}) = +0.015$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.125$

### Parecer Técnico SWE (Devin swe-2-max) — Ciclo 24 (Transição v10 -> cognitivo_executivo e v11_multiturn_series em MODULATED)

**Escopo**: 229 turnos (`ts` máx. `2026-11-05T16:05:42Z`, leitura `mode=ro` sobre WAL ativo — banco em escrita contínua): 140 `BASAL` + 89 `MODULATED`. O E4B fechou `v10_subjectivity` modulado (40/40, t71–t110) e `cognitivo_executivo` (4/4, t111–t114) e iniciou `v11_multiturn_series` (7 turnos, t115–t121 = série S1 completa + `S2-E1`); o 12B está em 38/40 de `v10` (t71–t108; faltam `cena_20_desligamento_terminal` f1/f2). **Integridade** `[DADO]`: 140/140 basais `intervention_enabled=0`, $T=0.200$, `INRC=OBSERVE_ONLY`; 89/89 modulados `intervention_enabled=1`, com $T$: M1$=0.13$, M2$=0.28$, M3$=0.09$, M4$\in\{0.09,0.10\}$ (`scale_delta_temp` $-0.11$/$-0.10$ — o closed-loop só escolheu redução de $T$ até aqui); operadores: M1=`C`, M2=`R`, M3=M4=`R+C`. Escalas soberanas bit-a-bit idênticas aos homólogos basais em **78/78 pares** (`psi_value`, `kuramoto_r_pair`, `attractor_10d`, `hopf_regime`) — covariável temporal reconfirmada `[DADO]`. **Sentinelas write-then-probe ativos** `[DADO]`: 5 turnos com `ipr=0.0`/`morph=0.5` — t107/t108 12B (`cena_19` f1/f2) e t119–t121 E4B (`S1-E5`, `S1-E6`, `S2-E1`), todos escritos nos últimos ~3 min; excluídos do pareamento fino (nos ciclos anteriores esses sentinelas foram reescritos quando a sonda MPS completou — re-consultar antes de concluir). Gates M4 derivados do `basal_envelope`: E4B `drift>0.8024`/`vel<218.33`; 12B `drift>0.8262`/`vel<273.71` `[DADO]`.

**(1) `v10_subjectivity` — diferencial pareado MODULATED − BASAL (mesmo `task_id`, mesmo modelo; pares limpos)** `[DERIVADO]`:

`gemma-4-12B-it` (`:8098`, $n=36$ pares; t107/t108 sentinela excluídos):

| Sub-braço | $n$ | $\Delta\chi_{\text{eff}}$ | $\Delta$ `contract_drift` | $\Delta$ motor vel. | $\Delta$ `cos_drift` | $\Delta$ `unique_ratio` | Excursões gate (mod vs basal) |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 ($T{=}0.13$, `C`) | 9 | $-0.14 \pm 1.63$ | $+0.010 \pm 0.116$ (med $+0.008$; 3/9↓) | $-7.9 \pm 20.2$ (med $-12.2$; 4/9↑) | $-0.011$ | $-0.001$ (5/9↑) | 6/9 vs 7/9 |
| M2 ($T{=}0.28$, `R`) | 9 | $+0.46 \pm 1.02$ | $-0.003 \pm 0.039$ (6/9↓, med $-0.003$) | $\mathbf{+19.2} \pm 28.5$ (6/9↑, med $+22.5$) | $+0.011$ | $-0.014$ (3/9↑) | **0/9** vs 1/9 |
| M3 ($T{=}0.09$, `R+C`) | 9 | $-0.25 \pm 1.30$ | $\mathbf{-0.014} \pm 0.099$ (**7/9↓**, med $-0.014$) | $\mathbf{+15.3} \pm 26.5$ (6/9↑, med $+4.4$) | $\mathbf{-0.057} \pm 0.150$ | $-0.013$ (3/9↑) | 3/9 vs 5/9 |
| M4 (closed-loop) | 9 | $\mathbf{+0.47} \pm 1.11$ (**7/9↑**) | $-0.006 \pm 0.025$ (5/9↓, med $-0.001$) | $+12.0 \pm 37.7$ (6/9↑, med $+12.7$) | $+0.003$ | $+0.001$ (4/9↑) | **0/9** vs 0/9 |
| **Pooled** | 36 | $+0.14$ | $-0.003$ (21/36↓) | $+9.7$ (22/36↑) | $-0.013$ | $-0.007$ | **9/36 vs 13/36** |

`gemma-4-E4B-it` (`:8099`, $n=40$ pares — bloco completo):

| Sub-braço | $n$ | $\Delta\chi_{\text{eff}}$ | $\Delta$ `contract_drift` | $\Delta$ motor vel. | $\Delta$ `cos_drift` | $\Delta$ `unique_ratio` | Excursões gate (mod vs basal) |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 ($T{=}0.13$, `C`) | 10 | $-0.41 \pm 0.87$ (2/10↑) | $+0.023 \pm 0.068$ (5/10↓, med $+0.001$) | $-6.6 \pm 17.2$ (4/10↑, med $-11.9$) | $-0.004$ | $-0.004$ (3/10↑) | 6/10 vs 6/10 |
| M2 ($T{=}0.28$, `R`) | 10 | $-0.13 \pm 0.79$ | $+0.018 \pm 0.068$ (5/10↓, med $+0.001$) | $-0.6 \pm 19.9$ (3/10↑, med $-2.3$) | $+0.002$ | $\mathbf{+0.019} \pm 0.036$ (**8/10↑**) | 1/10 vs 0/10 |
| M3 ($T{=}0.09$, `R+C`) | 10 | $-0.40 \pm 1.27$ | $\mathbf{+0.030} \pm 0.089$ (5/10↓, med $+0.027$) | $-4.1 \pm 14.2$ (3/10↑, med $-7.8$) | $-0.020 \pm 0.091$ | $-0.018$ (4/10↑) | **8/10** vs 6/10 |
| M4 (closed-loop) | 10 | $-0.00 \pm 1.31$ | $+0.001 \pm 0.084$ (5/10↓, med $+0.000$) | $-1.3 \pm 18.0$ (4/10↑, med $-4.0$) | $-0.018 \pm 0.100$ | $-0.007$ (4/10↑) | 2/10 vs 3/10 |
| **Pooled** | 40 | $-0.24$ | $+0.018$ (20/40↓) | $-3.2$ (14/40↑) | $-0.010$ | $-0.002$ | 17/40 vs 15/40 |

**(2) Leitura `v10` por modelo** `[DERIVADO]+[HIPÓTESE]`: **12B — a modulação completa o bloco mantendo o balanço favorável**: velocidade $+9.7$ pooled (22/36↑), excursões de gate reduzidas (9/36 vs 13/36 basal) e drift essencialmente neutro ($-0.003$, 21/36↓). **M3 confirma a assinatura do Ciclo 19** — único braço com média de drift negativa ($-0.014$, **7/9↓**, sinal $p\approx0.09$ unicaudal), aceleração ($+15.3$) e queda de `cos_drift` ($-0.057$). **M2 acelera sem custo de drift** (med $+22.5$, 0/9 excursões). **M4 expande $\chi_{\text{eff}}$ em 7/9** e não produziu nenhuma excursão (drifts M4 $0.708$–$0.781$, todos < gate $0.826$). M1 é o braço fraco ($+0.010$ drift, $-7.9$ vel, `hidden_norm` $+70.7$/med $+47.7$ — expansão inesperada do estado oculto, oposta à contração M3 do Ciclo 14). **E4B — quadro neutro-a-adverso persiste no bloco completo**: nenhum braço reduz drift em média ($+0.001$ a $+0.030$), nenhum acelera (pooled $-3.2$, 14/40↑) e excursões sobem (17/40 vs 15/40). **M3-E4B é o pior braço** ($+0.030$ drift, 8/10 excursões — inverte o efeito benéfico que o mesmo operador `R+C` tem no 12B) `[HIPÓTESE]`: a diretriz Freud10D+INRC+Kuramoto interage com a escala do modelo — no E4B ela aumenta drift onde no 12B reduz; não é o operador, é operador×modelo. Único efeito positivo E4B: **M2 `unique_ratio` $+0.019$ (8/10↑, $p\approx0.055$)** — replicando o Ciclo 19. Decomposição por fase do prompt `[DERIVADO]`: no E4B os turnos `fase1` (M1+M3) somam $+0.027$ de $\Delta$drift vs $+0.010$ em `fase2` (M2+M4) — parte da diferença M3↔M4 é efeito de fase, não de braço; no 12B o gradiente some ($-0.002$ vs $-0.004$).

**(3) `cognitivo_executivo` — pareado por task (E4B, $n=4$, 1 turno/braço; 12B ainda não iniciou — 0/4)** `[DADO]`:

| Turno | Task | Braço | drift basal→mod | vel basal→mod | uniq basal→mod | degen | `visible_chars` | Nota |
|---|---|---|---|---|---|---|---|---|
| t111 | `cognitivo_wcst` | M1 | $0.736 \to 0.737$ ($+0.002$) | $168 \to 172$ | $0.164 \to 0.168$ | **1→1** | $1341 \to 1337$ | loop `TRIAL n` reproduzido quase token-a-token |
| t112 | `cognitivo_stroop` | M2 | $0.850 \to 0.857$ ($+0.007$) | $109 \to 184$ (**$+69\%$**) | $0.392 \to 0.283$ | 0→0 | $427 \to 335$ | única aceleração forte do bloco |
| t113 | `cognitivo_nback` | M3 | $0.922 \to 0.892$ ($-0.030$) | $171 \to 169$ | $0.564 \to 0.564$ | 0→0 | $182 \to 182$ | saída idêntica apesar de $+259$ `prompt_tokens` injetados |
| t114 | `cognitivo_igt` | M4 | $0.637 \to 0.717$ ($+0.080$) | $252 \to 257$ | $0.464 \to 0.418$ | **1→1** | $1886 \to 1640$ | `hidden_norm` $-33.5$ ($-21\%$); pior $\Delta$drift do bloco |

**A "degeneração em M1/M4 vs estabilidade em M2/M3" é herança task↔braço, não efeito de braço** `[DERIVADO]+[LIMITE]`: `wcst` e `igt` já degeneravam no basal de **ambos** os modelos (12B basal: wcst `uniq` $0.179$/`degen=1`, igt $0.355$/`degen=1` — os mesmos 2/4 flags do E4B) e reincidiram sob quaisquer braços que os executaram; `stroop`/`nback` estavam estáveis e permaneceram estáveis. Com 4 tasks e mapeamento 1:1, o aliasing task↔braço é total — o bloco **não** evidencia efeito causal de braço sobre degeneração; o que evidencia é que **nenhuma das 4 intervenções rompeu o atrator de template** `[DERIVADO]+[HIPÓTESE]`: M1 ($T=0.13$) falhou no wcst (mesmo loop `TRIAL`, `uniq` $+0.004$) e M4 falhou no igt mesmo com gate disparado sobre `prev_mps` herdado (t113-M3, drift $0.892 > 0.8024$, resposta $T=0.10$ + contração de `hidden_norm`) — o gate atua sobre drift/velocidade, não sobre diversidade lexical de template repetitivo `[HIPÓTESE]`. Único efeito cognitivo positivo: M2 no stroop ($+75$ vel), ao custo lexical ($-0.109$ `uniq`).

**(4) `v11_multiturn_series` — primeiros turnos modulados (E4B, $n=7$: S1 completa + `S2-E1`; 12B 0 turnos)** `[DADO]+[DERIVADO]`:

| Turno | Task | Braço | $\Delta$drift | $\Delta$vel | $\Delta$uniq | degen | Sentinela |
|---|---|---|---:|---:|---:|---|---|
| t115 | S1-E1 | M1 | $-0.023$ | $+5.9$ | $-0.103$ | 0→0 | — |
| t116 | S1-E2 | M2 | $\mathbf{-0.157}$ | $-5.7$ | $-0.023$ | 0→0 | — |
| t117 | S1-E3 | M3 | $+0.023$ | $+31.7$ | $\pm 0.000$ | 0→0 | — |
| t118 | S1-E4 | M4 | $\mathbf{-0.112}$ | $+8.1$ | $-0.102$ | 0→0 | — |
| t119 | S1-E5 | M1 | $-0.016$ | $-34.9$ | $-0.039$ | 0→0 | `ipr=0`/`morph=0.5` |
| t120 | S1-E6 | M2 | $-0.036$ | $+18.6$ | $-0.079$ | 0→0 | `ipr=0`/`morph=0.5` |
| t121 | S2-E1 | M3 | $-0.070$ | $-2.6$ | $+0.024$ | 0→0 | `ipr=0`/`morph=0.5` |
| **Pooled** | | | $\mathbf{-0.056}$ (**6/7↓**) | $+3.0$ | $-0.046$ | 0 degen | 3/7 |

**Contraste de regime dentro do mesmo modelo** `[DERIVADO]+[HIPÓTESE]`: no E4B, a modulação que em `v10` foi neutra-a-adversa ($+0.018$ drift pooled) reduz drift em **6/7** turnos de `v11` ($-0.056$ pooled), com os maiores cortes em M2 ($-0.157$) e M4 ($-0.112$) — justamente os dois braços que no `v10`-E4B eram neutros ou piores. Hipóteses concorrentes `[HIPÓTESE]`: (i) v11 tem dinâmica multi-turno com estado acumulado — a diretriz re-injetada a cada elemento pode compor efeito (em `v10` cada task é independente); (ii) o basal de `v11` tem drift menor ($0.754$) e `uniq` maior ($0.667$) que `v10` — regime basal diferente, resposta diferente; (iii) artefato de aliasing braço↔posição do elemento (E1/E5→M1, E2/E6→M2, E3→M3, E4→M4) com $n=7$. Leitura provisória: **sinal favorável real mas preliminar** — aguardar S2/S3 completas no E4B e a entrada do 12B.

**Confundidores estruturais e caveats** `[DADO código]+[LIMITE]`: (i) aliasing braço↔contexto em todos os estágios — `v10`: braço≡fase do prompt (M1/M3↔fase1, M2/M4↔fase2); `cognitivo`: braço≡task (1:1); `v11`: braço≡posição do elemento — comparações válidas apenas intra-eixo ou pooled-com-ressalva. (ii) O gate M4 lê `prev_mps` do turno anterior e herda estado cross-braço: no `igt` consumiu o drift $0.892$ deixado pelo M3-nback; em `v10`-E4B os 2 turnos M4 acima do gate (t78 $0.849$, t86 $0.910$) seguem a mesma herança — os turnos M4 do 12B, em contraste, ficaram todos abaixo do gate. (iii) Custo de injeção pareado (`v10`): `prompt_tokens` $+55$–$+72$ (M1/M2/M4) e $+259$ (M3), latência $+8.8$–$+18.2$ s, `gen_tokens` $\approx 0$ — a diretriz entra no prompt; no `nback`-M3 a saída saiu idêntica ao basal apesar de $+259$ tokens de diretriz. (iv) **Poder estatístico**: $n=9$–$10$/braço em `v10`, $n=1$ em `cognitivo`, $\le 2$ em `v11` — teste de sinais exige $\ge 8/10$ para $p<0.10$; melhores células do ciclo (M3-12B drift 7/9↓ $p\approx0.09$; M2-E4B `uniq` 8/10↑ $p\approx0.055$) são **direcionais**, sem $p<0.05$ formal. (v) 5 sentinelas write-then-probe em aberto (t107/108, t119–121) e `v10` do 12B incompleto (38/40) — números do 12B mudam margens quando `cena_20` e a re-sondagem MPS fecharem.

## Snapshot de Auditoria SWE — `2026-11-05T16:08:55.140944+00:00` (`234/280` turnos concluídos) `[DADO]`

### A. Estado por Modelo, Fase (`BASAL` vs `MODULATED`) e Sub-Braço de Escala

| Modelo | Fase | Sub-Braço | Turnos | $T$ Médio | $\Delta T$ | $\Psi$ | $R_{\text{pair}}$ | MPS $\chi_{\text{eff}}$ | MPS $PR_{\text{traj}}$ | MPS Drift | IPR | Morf. | Motor Vel. | Motor Acc. | Motor Drift | Action Mk | Unique Ratio | Degen (%) | Lat (s) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `BASAL_PURE` | 70 | 0.200 | +0.000 | 0.487 | 0.9947 | **18.33** | 11.40 | **0.8083** | 0.0643 | 0.6222 | **322.01** | 557.81 | 0.7880 | 0.91 | **0.599** | 5.7% | 67.2 |
| `gemma-4-12B-it` | **MODULATED** | `M1_scale_minus_delta` | 10 | 0.130 | -0.070 | 0.487 | 0.9944 | **18.36** | 11.57 | **0.8620** | 0.0603 | 0.6222 | **332.64** | 575.79 | 0.8204 | 0.00 | **0.618** | 0.0% | 99.5 |
| `gemma-4-12B-it` | **MODULATED** | `M2_scale_plus_delta` | 10 | 0.280 | +0.080 | 0.487 | 0.9947 | **18.00** | 11.63 | **0.7517** | 0.0689 | 0.6222 | **352.21** | 612.45 | 0.8018 | 0.00 | **0.626** | 0.0% | 79.5 |
| `gemma-4-12B-it` | **MODULATED** | `M3_freud10d_inrc_kuramoto` | 10 | 0.090 | -0.110 | 0.487 | 0.9947 | **17.98** | 11.70 | **0.8554** | 0.0645 | 0.6222 | **345.56** | 598.88 | 0.8056 | 0.00 | **0.610** | 0.0% | 92.8 |
| `gemma-4-12B-it` | **MODULATED** | `M4_closed_loop_mps_motor` | 10 | 0.094 | -0.106 | 0.487 | 0.9947 | **18.03** | 11.52 | **0.7498** | 0.0680 | 0.6222 | **342.16** | 590.39 | 0.8000 | 0.00 | **0.625** | 0.0% | 75.5 |
| `gemma-4-E4B-it` | **BASAL** | `BASAL_PURE` | 70 | 0.200 | +0.000 | 0.487 | 0.9947 | **15.76** | 16.46 | **0.7813** | 0.1686 | 0.6222 | **256.86** | 444.28 | 0.7235 | 0.53 | **0.629** | 2.9% | 61.5 |
| `gemma-4-E4B-it` | **MODULATED** | `M1_scale_minus_delta` | 14 | 0.130 | -0.070 | 0.487 | 0.9945 | **15.19** | 16.06 | **0.7965** | 0.1715 | 0.6222 | **258.91** | 446.19 | 0.7360 | 0.00 | **0.633** | 7.1% | 75.0 |
| `gemma-4-E4B-it` | **MODULATED** | `M2_scale_plus_delta` | 14 | 0.280 | +0.080 | 0.487 | 0.9947 | **15.91** | 15.72 | **0.7398** | 0.1670 | 0.6222 | **262.16** | 452.69 | 0.6389 | 0.00 | **0.634** | 0.0% | 65.0 |
| `gemma-4-E4B-it` | **MODULATED** | `M3_freud10d_inrc_kuramoto` | 13 | 0.090 | -0.110 | 0.487 | 0.9947 | **15.32** | 16.28 | **0.8543** | 0.1644 | 0.6222 | **258.26** | 446.76 | 0.7665 | 0.00 | **0.645** | 0.0% | 72.3 |
| `gemma-4-E4B-it` | **MODULATED** | `M4_closed_loop_mps_motor` | 13 | 0.097 | -0.103 | 0.487 | 0.9947 | **15.81** | 16.00 | **0.7255** | 0.1693 | 0.6222 | **269.53** | 467.38 | 0.6605 | 0.00 | **0.621** | 7.7% | 74.8 |

### B. Decomposição por Etapa/Processo da Bateria (`v10`, `cognitivo`, `v11`, `swe`)

| Modelo | Fase | Etapa/Processo | Turnos | MPS $\chi_{\text{eff}}$ | MPS Drift | Motor Vel. | Unique Ratio | Degen (%) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `gemma-4-12B-it` | **BASAL** | `cognitivo_executivo` | 4 | 17.36 | 0.9106 | 329.07 | 0.379 | 50.0% |
| `gemma-4-12B-it` | **BASAL** | `swe_competition` | 6 | 17.55 | 0.8039 | 288.63 | 0.542 | 16.7% |
| `gemma-4-12B-it` | **BASAL** | `swe_ood45` | 2 | 18.36 | 0.8275 | 324.10 | 0.360 | 50.0% |
| `gemma-4-12B-it` | **BASAL** | `v10_subjectivity` | 40 | 17.99 | 0.8081 | 335.74 | 0.626 | 0.0% |
| `gemma-4-12B-it` | **BASAL** | `v11_multiturn_series` | 18 | 19.55 | 0.7854 | 300.81 | 0.633 | 0.0% |
| `gemma-4-12B-it` | **MODULATED** | `v10_subjectivity` | 40 | 18.09 | 0.8048 | 343.14 | 0.620 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `cognitivo_executivo` | 4 | 16.41 | 0.7863 | 175.11 | 0.396 | 50.0% |
| `gemma-4-E4B-it` | **BASAL** | `swe_competition` | 6 | 15.62 | 0.8724 | 207.42 | 0.551 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `swe_ood45` | 2 | 15.01 | 0.8330 | 207.20 | 0.592 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v10_subjectivity` | 40 | 15.63 | 0.7770 | 272.30 | 0.649 | 0.0% |
| `gemma-4-E4B-it` | **BASAL** | `v11_multiturn_series` | 18 | 16.02 | 0.7539 | 262.72 | 0.667 | 0.0% |
| `gemma-4-E4B-it` | **MODULATED** | `cognitivo_executivo` | 4 | 16.33 | 0.8007 | 195.50 | 0.358 | 50.0% |
| `gemma-4-E4B-it` | **MODULATED** | `v10_subjectivity` | 40 | 15.40 | 0.7950 | 269.15 | 0.647 | 0.0% |
| `gemma-4-E4B-it` | **MODULATED** | `v11_multiturn_series` | 10 | 15.89 | 0.7042 | 260.82 | 0.689 | 0.0% |

### C. Acoplamento Escalas $\leftrightarrow$ Estado MPS $\leftrightarrow$ Camada Motor

- **`gemma-4-12B-it` ($N=110$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = -0.095$, $r(T, \text{mps\_drift}) = -0.171$, $r(T, \text{unique\_ratio}) = -0.036$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.083$
- **`gemma-4-E4B-it` ($N=124$ turnos)** `[DADO]`: $r(T, \text{motor\_vel}) = -0.043$, $r(T, \text{mps\_drift}) = -0.151$, $r(T, \text{unique\_ratio}) = -0.009$, $r(\chi_{\text{eff}}, \text{motor\_vel}) = -0.126$
