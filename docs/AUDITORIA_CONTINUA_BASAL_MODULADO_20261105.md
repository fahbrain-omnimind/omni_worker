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
