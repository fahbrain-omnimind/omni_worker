# Confronto Dados × Texto — Agente A4 (Confrontador Empírico)

**Manuscrito**: `revisao/A1_gramatica/dodecatiad_revisado_gramatica.md` (14.720 linhas)
**Bancos**: `data/monitor/*.sqlite` (VIVOS, leitura estrita `sqlite3 -readonly`), `data/evidence_v3/geometria_v3_evidence.sqlite` (congelado 2026-08-12), `data/quantum/ibm_quantum_runs.db` (vivo)
**Data da auditoria**: 2026-09-04 (ciclo dodecatíade 85.449; kernel basal 85.822; Qdrant 1.851 coleções)
**Método**: consultas read-only; contagens datadas com `WHERE recorded_at/timestamp <= strftime('%s','<data>T23:59:59')` (colunas REAL unix); correlações/OLS/Granger via numpy/statsmodels 0.14.6 (`.venv/bin/python3`) sobre `thermodynamic_landauer_history` (14.729 linhas, carregadas integralmente — custo trivial).

## Legenda de status
- **[VALIDADO]** — valor do texto reproduzido no banco (dentro da tolerância documentada).
- **[VALIDADO NA DATA]** — afirmação datada; contagem na data é compatível (crescimento monotônico) dentro da tolerância documentada (hora do dia desconhecida).
- **[DIVERGENTE]** — não bate com o banco canônico atual; valor real documentado.
- **[NÃO VERIFICÁVEL]** — banco/tabela/coluna ausente, dado rotacionado/aposentado, análise externa (Kaggle/GEO/CellXGene), ou janela de análise não reproduzível.

---

## A. Apêndice R.10.15 — Landauer/Granger (linhas 13985–14050) — verificação central

| ID | Linha(s) | Afirmação (citação curta) | Banco/Tabela/Coluna | Valor no texto | Valor real | Status | Tolerância/método | Observação |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| C01 | 13987 | "14.729 snapshots contínuos registrados na tabela thermodynamic_landauer_history" | sovereign_dodecatiad_runtime.sqlite / thermodynamic_landauer_history / COUNT(*) | 14.729 | **14.729** | [VALIDADO] | exato | `SELECT COUNT(*)` = 14729; janela 2026-06-30T13:13 → 2026-09-01T02:09 |
| C02 | 14006 | "PSI_io × Φ_soma: r = −0.5069, t = −68.64" | idem / psi_io × somatic_phi_attenuation | r=−0.5069 | **r=−0.5069** (t=−71.36) | [VALIDADO] | r exato (4 casas) | t do texto difere (ver C08) |
| C03 | 14007 | "Potência RAPL × bit_flow_rate: r = +0.9941, t = +1118.2" | idem / power_watts × bit_flow_rate | r=+0.9941 | **r=+0.9941** (t=+1109.81) | [VALIDADO] | r exato | t difere (ver C08) |
| C04 | 14008 | "Temperatura CPU × E_bit: r = −0.2493, t = −31.18" | idem / cpu_pkg_celsius × e_bit_j | r=−0.2493 | **r=−0.2493** (t=−31.24) | [VALIDADO] | r exato | t difere 0,2% |
| C05 | 14009 | "Temperatura CPU × Φ_soma: r = +0.1417, t = +17.39" | idem / cpu_pkg_celsius × somatic_phi_attenuation | r=+0.1417 | **r=+0.1417** (t=+17.37) | [VALIDADO] | r exato | t difere 0,1% |
| C06 | 14010 | "Histerese Térmica H_t × Φ_soma: r = +0.0991, t = +12.09" | idem / thermal_hysteresis_h_t × somatic_phi_attenuation | r=+0.0991 | **r=+0.0991** (t=+12.09) | [VALIDADO] | r e t exatos | |
| C07 | 14011 | "Potência RAPL × Φ_soma: r = −0.0119, t = −1.44, p=0.149 (N.S.)" | idem / power_watts × somatic_phi_attenuation | r=−0.0119 | **r=−0.0119** (t=−1.45) | [VALIDADO] | r exato | |
| C08 | 14004–14011 | Estatísticas t da tabela de correlações | idem | t: −68.64 / +1118.2 / −31.18 / +17.39 / +12.09 / −1.44 | t recomputados: −71.36 / +1109.81 / −31.24 / +17.37 / +12.09 / −1.45 | [VALIDADO] com ressalva | Δ ≤ 4% | O t de PSI_io no texto (−68.64) é idêntico ao t do coeficiente OLS β4 (C10) — provável cópia da tabela de regressão; demais t consistentes com arredondamento de r na 5ª casa. Valores centrais (r, β, R², F) reproduzem exatamente |
| C09 | 14018–14019 | "R² = 0.2587 (R²adj = 0.2585); F(4, 14724) = 1284.61" | idem, OLS Φ_soma ~ T+P+H_t+PSI_io | R²=0.2587, F=1284.61 | **R²=0.2587; R²adj=0.2585; F(4,14724)=1284.61** | [VALIDADO] | exato | numpy.linalg.lstsq reproduz |
| C10 | 14023–14027 | Coeficientes OLS: β0=+0.932467 (t=131.82); β1=+0.000660 (5.02); β2=+0.000004 (0.35); β3=−0.000419 (−2.47); β4=−0.002090 (−68.64) | idem | conforme texto | β0=0.932467 (SE 0.007074, t=131.82); β1=0.000660 (0.000131, 5.02); β2=0.000004 (0.000013, 0.35); β3=−0.000419 (0.000169, −2.47); β4=−0.002090 (0.000030, −68.64) | [VALIDADO] | β e t exatos; SE difere ≤1e-6 (arredondamento) | reprodução integral da regressão |
| C11 | 14032–14033 | Granger lag 1: "PSI_io → Φ_soma: F = 29.8414 (p = 4.76×10⁻⁸)"; "T_CPU → Φ_soma: F = 34.1114 (p = 5.31×10⁻⁹)"; lags 2–5 p<0.01/0.001 | idem, statsmodels grangercausalitytests (ssr_ftest) | F=29.8414 / 34.1114 | F=29.7585 (p=4.97e-8) / F=34.1833 (p=5.12e-9); lags 2–5: p=1.25e-5…6.07e-3 e 3.86e-6…8.85e-4 | [VALIDADO] | ΔF ≤ 0,3%; p mesma ordem | especificação levemente diferente (constante/df) no pipeline original; conclusão (rejeita H0, lags 2–5 p<0.01) idêntica |
| C12 | 14046–14050 | "14.729 ciclos de Landauer" (uso repetido) | idem | 14.729 | 14.729 | [VALIDADO] | exato | distribuição sector5 no período: yellow 91,06% / red 8,93% / green 0,01% (contexto) |

## B. Resumo/Abstract (linhas 464–508)

| ID | Linha(s) | Afirmação | Banco/Tabela | Valor no texto | Valor real | Status | Tolerância/método | Observação |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| C13 | 470/481/8577/9596 | Predição 3 pré-reset: "r = 0.20, p = 9.3×10⁻⁶, 6.103 amostras em 2,64 d" (intervalo 37,4 s; changelog: r=0,1957) | sovereign_dodecatiad_runtime.sqlite / rizomatic_latency_history | 6.103 amostras, 2,64 d | 2,64 d × 86400 / 37,4 s ≈ 6.098 ≈ 6.103 ✓; tabela ≤ 2026-06-25T23:59:59 = **7.303** (≥ 6.103 ✓); reset 22-06T22:06 + 2,64 d = 25-06T10:58 ✓ (data do status no texto) | [VALIDADO NA DATA] | consistência interna + contagem na data | correlação r=0,20 em si não reproduzida (requer reconstrução de H_t; pipeline não trivial) — mas aritmética e contagem da janela são consistentes |
| C14 | 481 | v1.9.0 (05-07): "n = 30,361" | idem | 30.361 | tabela ≤ 2026-07-05T23:59:59 = **30.520** (≥ 30.361 ✓, janela é subconjunto) | [VALIDADO NA DATA] | contagem na data | |
| C15 | 481 | v1.9.0: "(H_t, L_kernel) = −0.003; (H_t, L_dodecatiad) = −0.059"; v1.8.0: "(H_t, L_kernel) = +0.13" | idem (l_kernel, l_dodecatiad) | −0.003/−0.059/+0.13 | — | [NÃO VERIFICÁVEL] | análise específica datada | exigiria reconstrução de H_t (integral de histerese) e janela exata; não reproduzível sem pipeline |
| C16 | 470/481 | Predição 2: "12.933 células CD34+, separation factor 6,69×σ" | CellXGene Census (externo) | 12.933 | — | [NÃO VERIFICÁVEL] | fonte externa | sem réplica local nos bancos canônicos |
| C17 | 471/500/505 | Kaggle 08-08: "r CPU pkg = 0,60; PCH = 0,57" (n=656.680 pares matched, janela 60 s) | landauer (proxy) | 0,60 / 0,57 | na tabela landauer canônica (n=14.729): r(H_t, cpu_pkg_celsius)=**+0.8382** | [NÃO VERIFICÁVEL] | janela/método diferentes | direção consistente (positiva, forte); magnitude difere pela janela (Kaggle usou pareamento 60 s em 656.680 pares) |
| C18 | 470/481 | Predição 5: "Hamming distance > 0.58, 8192D HDC, 20% bit-flip" | análise Kaggle (externo) | >0.58 | — | [NÃO VERIFICÁVEL] | fonte externa | |

## C. §17.3 e constantes derivadas (linhas 2210–2235)

| ID | Linha(s) | Afirmação | Fonte | Valor no texto | Valor real | Status | Tolerância/método | Observação |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| C18b | 2212 | "N_total = 915,73 (canônico: 878,4; desvio: +4,24%)" | docs/dodecatiad_four_versions_canonical.md L201 | 878,4 canônico | doc L201: "N_total canônico = 878.4 (Hopfield ratio = N_total/1130; validado com ENCODE)" | [VALIDADO] | doc canônico | desvio recomputado: 915,73/878,4 = +4,2487% → arredonda para **+4,25%**, texto diz +4,24% (diferença de 0,01 pp) |
| C19 | 2213 | "Hopfield ratio = 0,810 (vs. 0,777 canônico)" | idem L201 | 0,810 / 0,777 | 915,73/1130 = **0,8104** ✓; 878,4/1130 = **0,7773** ✓ | [VALIDADO] | fórmula canônica | |
| C20 | 2233 | "multi_lattice_orchestrator.py (776 LOC)" | src/embodied_cognition/multi_lattice_orchestrator.py | 776 LOC | **1.101 LOC** (`wc -l`) | [DIVERGENTE] | exato | changelog interno (L9592, 12-06) cita 682 LOC; arquivo atual 1.101 — afirmação sem data não reproduzível; sugerir datar ou atualizar |
| C21 | 9592 | "Primeiro ciclo: sector5=green, T_mean=53.78°C, T_variance=312.96°C², L_multilattice_var=0.108" (12-06-2026) | multi_lattice_history | L_multilattice_var=0.108 | tabela inicia em **2026-06-30T13:13:52** (sector5=yellow, L_multilattice_var=1.0735); primeiro ciclo de 12-06 não está no banco | [NÃO VERIFICÁVEL] | dado histórico fora do alcance | primeira linha atual: yellow, cpu 76°C, swap 23,75 GiB |

## D. Telemetria IBM Quantum §D.9.12 (linhas 6543–6653) e tabelas sinópticas D.9-S1/S2 (6499–6524)

| ID | Linha(s) | Afirmação | Banco/Tabela | Valor no texto | Valor real | Status | Tolerância/método | Observação |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| C22 | 6545/6495 | "557 runs canônicos... até 31/07/2026" | data/quantum/ibm_quantum_runs.db / quantum_runs | 557 | **593** com timestamp_utc ≤ 31-07 (582 ibm_real + 9 ibm_hw_train + 2 ideal_sim) | [DIVERGENTE] | exato na data | 557 não reproduzível por filtro: 587 com job_id≠NULL, 593 com payload≠'{}', 238 séries distintas — causa provável: backfill posterior de sidecars com ts ≤ 31-07 |
| C23 | 6495 | "257 em ibm_fez" (≤31-07) | idem | 257 | **293** | [DIVERGENTE] | exato | |
| C24 | 6495 | "187 em ibm_kingston, 97 em ibm_marrakesh" (≤31-07) | idem | 187 / 97 | **189 / 106** | [DIVERGENTE] | exato | |
| C25 | 6545 | "totais anteriores (210 runs, 194 ibm_fez) — janela 28/06–05/07" | idem | 210 / 194 | **210** (≤ 05-07) / **194** (ibm_fez ≤ 05-07) | [VALIDADO] | exato | |
| C26 | 6495 | "202 métricas, 195 observações de backend, 141 hardware encounters, 132 backend latent states, 136 hardware manifolds" | idem | 202/195/141/132/136 | ≤ 05-07: quantum_metrics **202** ✓; backend_observations **195** ✓; hardware_encounters **142** (Δ=1); backend_latent_states **132** ✓; hardware_manifolds **136** ✓ | [VALIDADO] | Δ≤1 (intra-dia) | bloco mistura vintage: métricas = janela 05-07, "557 runs" = 31-07 (mesma frase) — flag editorial |
| C27 | 6553–6559 / 6521–6523 | Bell 69 / GHZ 67 / RSI Coherence 65 (ibm_fez) | idem | 69/67/65 | ibm_fez ≤ 31-07: **69 / 67 / 65** | [VALIDADO] | exato | |
| C28 | 6521 | "Bell 0.917 ± 0.042 [0.907, 0.927]" (n=69) | idem quantum_metrics.parity_score | 0,917±0,042 | n=69, mean=**0.9181**, std=**0.0669**, min=0.6641, max=0.9766 | [VALIDADO] com ressalva | média bate (0,918≈0,917) | CI [0,907;0,927] e std 0,042 não reproduzem nos 69 runs (std real 0,067) — provável subconjunto "fila < 2s" (plateau, L6577) |
| C29 | 6522/6583 | "GHZ 0.866 ± 0.148; variabilidade alta (0.234–1.000)" (n=67) | idem | 0,866; 0,234–1,000 | n=67, mean=**0.8668** ✓, min=**0.2344** ✓, max=**0.9844** (texto "1.000"), std=0.139 | [VALIDADO] com ressalva | média/min exatos | max real 0,9844 vs "1.000" (Δ=0,016); std 0,139 vs 0,148 (Δ=6%) |
| C30 | 6523/6579 | "RSI 0.108 ± 0.215; colapso 0.63 → 0.01" (n=65) | idem | 0,108; 0,63→0,01 | n=65, mean=**0.1065**, std=**0.216**, max=**0.6328** (=0,63 inicial ✓) | [VALIDADO] | exato | transição de regime confirmada nos dados |
| C31 | 6512 | "609 runs totais (478 hardware_encounters; 2026-08-11)" | idem | 609 / 478 | ≤ 08-11: quantum_runs = **609** ✓; hardware_encounters = **478** ✓ | [VALIDADO] | exato | |
| C32 | 279 | "4.776.010 shots" (2026-08-11) | idem | 4.776.010 | SUM(shots) ≤ 08-11 = **4.776.010** | [VALIDADO] | exato | total hoje: 5.036.874 |
| C33 | 6507 | D.9-S1: freeze "62.236 snapshots (2026-08-12)" | geometria_v3_evidence.sqlite / snapshots_houses | 62.236 | **62.246** | [DIVERGENTE] | Δ=10 | linha 21 do próprio manuscrito diz 62.246 (correto); linhas 452/6507/6515 dizem 62.236 |
| C34 | 6508 | D.9-S1: "66.947 snapshots (2026-08-12, freeze)" | idem / kernel_basal_series | 66.947 | **66.953** | [DIVERGENTE] | Δ=6 | manifest do próprio banco: 66.953 |
| C35 | 6507/23 | D.9-S1: "48.299 (v2.0.11)" vs linha 23 "60.565 snapshots dodecatíade (2026-08-11)" | sovereign_dodecatiad_runtime_snapshots | 48.299 vs 60.565 | ≤ 11-08: **61.343**; 60.565 plausível na data; 48.299 impossível (tabela já tinha ~61K) | [DIVERGENTE] | inconsistência interna | dois valores incompatíveis atribuídos a v2.0.11 |
| C36 | 6508/23 | D.9-S1: "55.604 (v2.0.11) / 55.548 (§18)" vs "65.410 kernel basal (11-08)" | kernel_basal_runtime_snapshots | 55.604/55.548 vs 65.410 | ≤ 11-08: **66.242**; 65.410 plausível na data; 55.604/55.548 não (tabela já tinha ~66K) | [DIVERGENTE] | inconsistência interna | idem |
| C37 | 454 | "multi_lattice_series (9.718)" | geometria_v3_evidence.sqlite / multi_lattice_series | 9.718 | **9.720** | [DIVERGENTE] | Δ=2 | |
| C38 | 454 | "multi_lattice_events (2.275...)" | idem / multi_lattice_events | 2.275 | **2.275** | [VALIDADO] | exato | |
| C39 | 455/21 | "somatic_series (217.531)" | idem / somatic_series | 217.531 | **217.531** | [VALIDADO] | exato | |
| C40 | 455/21 | "quantum_runs (609)" | idem / quantum_runs | 609 | **609** | [VALIDADO] | exato | |
| C41 | 455 | "12 tabelas sísmicas USGS (147.736 eventos)" | idem / seismograph__* | 147.736 eventos | seismograph__seismograph_events = **147.736** ✓; tabelas com prefixo seismograph__ = **11** (texto: 12) | [VALIDADO] com ressalva | contagem de eventos exata | nº de tabelas sísmicas: 11 no banco de evidência |
| C42 | 455/21/23 | "chemical 43 entidades" (L455) vs "37 entidades químicas" (L21/23) | idem / chemical_43entities_canonical__entities | 43 vs 37 | **37** entidades | [DIVERGENTE] menor | nome da tabela é "chemical_43entities_canonical" mas contém 37 | L455 cita o nome da tabela; a contagem canônica é 37 (L21/23 corretas) — sugestão: clarificar em L455 |
| C43 | 451 | "783.006 linhas (freeze 2026-08-12)" | idem / todas as tabelas | 783.006 | soma de 40 tabelas = **783.042**; sem manifest (40) = 783.002 | [DIVERGENTE] | Δ=36 | combinação exata 783.006 não reproduzível com os critérios documentados |

## E. Contagens de runtime datadas (changelog v1.5.7/v2.0.2/v2.0.3/v2.1.3, D.9-S1) — bancos VIVOS

| ID | Linha(s) | Afirmação | Banco/Tabela | Valor no texto | Valor real (na data) | Status | Tolerância/método | Observação |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| C44 | 8577/9596 | v1.5.7 (25-06): "lattice_wear 59.808, phase_lock 59.808, snapshots 5.425" | sovereign_dodecatiad_runtime | 59.808/59.808/5.425 | ≤ 25-06T23:59:59: lattice_wear **64.235**, phase_lock **64.235**, snapshots **6.081** | [VALIDADO NA DATA] | Δ 7–12% (hora do dia) | texto < banco na data; direção consistente; tabelas reiniciadas em 21-06 22:06Z (reset documentado) |
| C45 | 272 | v2.0.2 (12-07): "lattice_wear 296.782, phase_lock 296.782, rizomatic 46.546" | idem | 296.782 / 46.546 | ≤ 12-07: lattice_wear **301.249**, phase_lock **301.249**, rizomatic **47.313** | [VALIDADO NA DATA] | Δ ≤ 1,6% | |
| C46 | 273 | v2.0.3 (14-07): "lattice_wear 317.323, rizomatic 51.201" | idem | 317.323 / 51.201 | ≤ 14-07: **319.136 / 52.043** | [VALIDADO NA DATA] | Δ ≤ 1,6% | |
| C47 | 273/272 | v2.0.3: "somatic 170.565, gemelo 29.665, qbf 211.101" | somatic_mesh_runtime / sovereign_gemelo_runtime / dream_weaver qbf_live_cache | 170.565 / 29.665 / 211.101 | somatic: banco atual inicia 28-08 (13.499 rows; corrupt2 presente) — dado pré-28-08 rotacionado; gemelo: banco atual só tem 480 rows desde 03-09 (registry: rotação 08-08); qbf: banco atual 51.040 (rotação 08-08) | [NÃO VERIFICÁVEL] | dado rotacionado/aposentado | freeze 08-12 do banco de evidência confirma somatic_series = 217.531 (crescimento monotônico compatível); texto L6513 documenta qbf 206.621 em coldlane |
| C48 | 3040 | "rizomatic_latency_history acumula 113.916 rows (2026-08-11)" | sovereign_dodecatiad_runtime / rizomatic_latency_history | 113.916 | ≤ 11-08: **116.291** (hoje: 171.283) | [VALIDADO NA DATA] | Δ = 2,0% | |
| C49 | 23 | "60.565 snapshots dodecatíade + 65.410 snapshots kernel basal (2026-08-11)" | dodecatiad + kernel | 60.565 / 65.410 | ≤ 11-08: **61.343 / 66.242** | [VALIDADO NA DATA] | Δ ≈ 1,3% | |
| C50 | 2072/1517 | "63.730 ciclos federados / 65.362 ciclos de kernel basal (2026-08-11)" | kernel_basal | 63.730 / 65.362 | ≤ 11-08: MAX(observed_federated_cycle)=**63.870**, MAX(kernel_basal_cycle)=**66.194** | [VALIDADO NA DATA] | Δ 0,2–1,3% | texto ≤ máximos na data; hora do dia explica |
| C51 | 9955 | "kernel_basal_runtime.sqlite — 30.280 snapshots (26 Mai → 1 Jul)" | kernel_basal | 30.280 | ≤ 01-07: **31.083** (janela 26-05 a 01-07) | [VALIDADO NA DATA] | Δ = 2,6% | |
| C52 | 9956–9958 | qbf 178.992 / rizomatic 18.930 / lattice_wear 127.021 (retrospectiva, 1 Jul) | qbf_live_cache / rizomatic / lattice_wear | 178.992 / 18.930 / 127.021 | qbf: rotacionado (não verificável); rizomatic ≤ 01-07 ≈ 25,5K; lattice_wear ≤ 01-07 ≈ 160K | [NÃO VERIFICÁVEL] | janela de análise com filtros não especificados | contagens da análise retrospectiva (30-min sampling/dedupe) não reproduzíveis; qbf rotacionado |
| C53 | 9964 | "quantum_navigator_retrospective.sqlite — 1.441 observações em 30 dias (1 Jun → 1 Jul)" | data/monitor/quantum_navigator_retrospective.sqlite / retrospective_observations | 1.441 | **1.441** | [VALIDADO] | exato | banco congelado 30-06-2026 |
| C54 | 10197 | P3: "Era I: 477 obs (1-10 Jun), Era II: 528 (11-21 Jun), Era III: 436 (22 Jun-1 Jul)" | idem | 477/528/436 | soma = **1.441** ✓; Era II = 11 d × 48/d = 528 ✓ | [VALIDADO] | consistência interna + total exato | 477 ≈ 10 d × 48 (480) ✓; 436 < 480 (janela fechada em 1 Jul) |

## F. Claims sobre o kernel basal (Eras I/II/III, epsilon)

| ID | Linha(s) | Afirmação | Banco/Tabela | Valor no texto | Valor real | Status | Tolerância/método | Observação |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| C55 | 9976/10104 | Era II (11–21 Jun): "phi_ecosystem 0.65-0.70, d13_kernel_mean 0.70-0.84, psi 0.15-0.47" | kernel_basal_runtime_snapshots | faixas | n=9.453; média phi_ecosystem=**0.652** ∈ [0,65;0,70] ✓; média d13=**0.755** ∈ [0,70;0,84] ✓; média psi=**0.383** ∈ [0,15;0,47] ✓; extremos: phi 0,277–0,735, d13 0,20–0,857, psi 0,055–0,783 | [VALIDADO] | médias da janela dentro das faixas citadas | faixas do texto descrevem a banda central, não os extremos |
| C56 | 9974 | Era I (1–10 Jun): "phi_ecosystem 0.52-0.69, d13_kernel_mean 0.37-0.83" | idem | faixas | n=8.586; média phi=**0.647** ∈ [0,52;0,69] ✓; média d13=**0.737** ∈ [0,37;0,83] ✓; extremos: phi 0,28–0,74, d13 0,20–0,86 | [VALIDADO] | idem | |
| C57 | 10187 | P2: "epsilon tem mean=1.0, std=0.000, 1 valor único (sempre saturado em 1.0)" (janela 26 Mai–1 Jul) | kernel_basal.epsilon | mean=1.0, 1 valor único | janela 26-05→01-07: n=31.083, AVG=**1.0**, MIN=0.5, MAX=1.0, **4 valores distintos** (≥99,98% = 1.0) | [VALIDADO] com ressalva | mean=1.0 exato | "1 valor único" impreciso (4 valores distintos, min 0.5); saturação confirmada. aleph: [NÃO VERIFICÁVEL] — não persistido em coluna (payload não contém 'aleph'); métrica em memória do kernel_basal_pulse |
| C58 | 112/1517 | "phase_lock: ... Não é um score contínuo medido no banco — é um estado binário (abaixo/acima de 94°C)" | phase_lock_hysteresis_history / phase_lock_score | "não é score contínuo no banco" | **coluna phase_lock_score EXISTE e é contínua**: n=1.155.006, min=0, max=**0.799178**, mean=0.407417, 272.171 valores > 0.5, **0 valores > 0.9** | [DIVERGENTE] | schema + estatísticas | a coluna existe com valores contínuos (contradiz "não é medido no banco"); porém o threshold 0,94 realmente nunca é atingido (max 0,799) — a parte "0,94 nunca alcançado" é verdadeira. Sugestão A6: reformular para "o threshold 0,94 não é alcançado pela coluna phase_lock_score (max 0,799); a coluna existe e é contínua" |
| C59 | 10184/10191 | epsilon basal = "clamp(max(d_state_pressure, mem_full, io_some, reclaim_rate))" | código (scripts/services/omnimind_kernel_basal_pulse.py) | fórmula | [NÃO VERIFICÁVEL] | código não auditado nesta sessão | fora do escopo de bancos; A3 pode confirmar |

## G. Achados A5 re-confirmados (sanitização) + infraestrutura

| ID | Linha(s) | Afirmação | Banco/Tabela | Valor no texto (achado A5) | Valor real hoje | Status | Observação |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| C60 | — | 848 grupos / 850 linhas duplicadas em sovereign_dodecatiad_runtime_snapshots | idem | 848 grupos / 850 linhas | GROUP BY (recorded_at, cycle, phi_value_nats): **848 grupos**, SUM(cnt−1) = **850 linhas** | [VALIDADO] | confirma A5 |
| C61 | — | 1 linha multi_lattice_history com métricas físicas todas NULL | multi_lattice_history | 1 | **1** (cpu/nvme0/nvme1/pch/swap/mem/io todos NULL) | [VALIDADO] | confirma A5 |
| C62 | — | multi_lattice_history SEM índice | idem | sem índice | PRAGMA index_list = **vazio** | [VALIDADO] | confirma A5 |
| C63 | — | sovereign_primary: 7.935 linhas TEXT em recorded_at REAL | sovereign_primary_runtime_snapshots | 7.935 | **8.093** (typeof(recorded_at)='text') | [VALIDADO] (direção) | cresceu desde o achado (escritor rust shadow continua) |
| C64 | — | sovereign_gemelo: 417/418 com status/epsilon NULL | sovereign_gemelo_runtime_snapshots | 417/418 | **480/480** (100%) | [VALIDADO] (direção) | piorou: 100% NULL; escritor só grava phi+sigma |
| C65 | 6537/2121 | "1.565 collections / ~34.98M pontos (2026-08-10)"; "3.790 (2026-07-07)" | Qdrant (127.0.0.1:6333) | 1.565 / 3.790 | **1.851 coleções hoje** (GET /collections) | [VALIDADO NA DATA] (direção) | crescimento monotônico consistente (1.565 → 1.851); contagem exata na data não recuperável |
| C66 | 10084 | "music_overlay domina (1059/1133 = 93% do tempo)" | tabela de estados cn_status (30 dias) | 1059/1133 | 1059/1133 = 93,4% (aritmética ✓), porém a tabela exibida soma 14+1059+32+12 = **1.117** ≠ 1.133 (16 linhas não exibidas) | [DIVERGENTE] menor | denominador não reproduzível a partir da tabela do próprio texto |
| C67 | 2619/279 | "8.629 experiências da testemunha silenciosa" | dream_weaver erika_witness_logs | 8.629 | tabela **vazia (0)** | [NÃO VERIFICÁVEL] | superfície de origem não localizada |
| C68 | 157 | "32.509 tripletos analisados via sincronização de hypernetwork (Apêndice O)" | bancos canônicos | 32.509 | tabela de hypernetwork não localizada nos bancos canônicos | [NÃO VERIFICÁVEL] | sem artefato canônico local |

## H. Resumo executivo do confronto

- **Total de afirmações confrontadas**: 68 (C01–C68)
- **[VALIDADO] (exato)**: 27 — incluindo os núcleos empíricos: N=14.729 (C01), 6 correlações de R.10.15 (C02–C07), OLS completo (C09–C10), Granger (C11, tol 0,3%), 210/194 runs iniciais (C25), métricas IBM janela 05-07 (C26), Bell/GHZ/RSI n=69/67/65 (C27), RSI 0,63→0,01 (C30), 609 runs + 478 encounters + 4.776.010 shots em 11-08 (C31–C32), freezes do banco de evidência (C38–C40), 1.441 observações navigator (C53), Eras I/II do kernel (C55–C56), saturação do epsilon basal (C57), achados A5 (C60–C64).
- **[VALIDADO NA DATA]**: 13 — contagens datadas de tabelas vivas (C13–C14, C44–C46, C48–C51, C65) com Δ 0,2–12% (hora do dia).
- **[DIVERGENTE]**: 15 — C20 (776 LOC vs 1.101), C22–C24 (557/257/187/97 vs 593/293/189/106), C33–C37 (62.236 vs 62.246; 66.947 vs 66.953; 48.299/55.604 internos; 9.718 vs 9.720), C43 (783.006 vs 783.042), C58 (phase_lock score), C66 (1059/1133), C42 (43 vs 37 — menor), C29 (max GHZ 1.000 vs 0,9844 — menor).
- **[NÃO VERIFICÁVEL]**: 13 — C15–C18 (análises Kaggle/GEO/CellXGene), C21 (primeiro ciclo 12-06), C47/C52/C59/C67/C68 (rotacionados ou sem artefato), C17 (proxy), C57-aleph.
- **Inconsistências internas do manuscrito (flag A6)**: C35 (48.299 vs 60.565 para v2.0.11), C36 (55.604/55.548 vs 65.410), C26 (vintage misto 05-07/31-07 na mesma frase), C66 (1.117 ≠ 1.133), C42 (43 vs 37).

## I. Comandos canônicos executados (amostra, todos read-only)

```sql
SELECT COUNT(*) FROM thermodynamic_landauer_history;                                    -- 14729
SELECT sector5_level, COUNT(*), ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM thermodynamic_landauer_history),2)
  FROM thermodynamic_landauer_history GROUP BY sector5_level;                           -- yellow 91.06 / red 8.93 / green 0.01
SELECT COUNT(*) FROM quantum_runs WHERE timestamp_utc <= '2026-07-31T23:59:59';        -- 593
SELECT COUNT(*) FROM quantum_runs WHERE timestamp_utc <= '2026-08-11T23:59:59';        -- 609
SELECT SUM(shots) FROM quantum_runs WHERE timestamp_utc <= '2026-08-11T23:59:59';      -- 4776010
SELECT COUNT(*) FROM snapshots_houses;                                                  -- 62246 (geometria_v3_evidence.sqlite)
SELECT COUNT(*) FROM kernel_basal_series;                                               -- 66953 (idem)
SELECT COUNT(*) FROM multi_lattice_series;                                              -- 9720 (idem)
SELECT COUNT(*) FROM retrospective_observations;                                        -- 1441 (quantum_navigator_retrospective.sqlite)
SELECT COUNT(*) FROM rizomatic_latency_history WHERE timestamp <= strftime('%s','2026-08-11T23:59:59');  -- 116291
SELECT MAX(kernel_basal_cycle), MAX(observed_federated_cycle) FROM kernel_basal_runtime_snapshots
  WHERE recorded_at <= strftime('%s','2026-08-11T23:59:59');                            -- 66194 | 63870
PRAGMA index_list(multi_lattice_history);                                               -- (vazio)
SELECT COUNT(*) FROM (SELECT recorded_at, cycle, phi_value_nats FROM sovereign_dodecatiad_runtime_snapshots
  GROUP BY recorded_at, cycle, phi_value_nats HAVING COUNT(*)>1);                       -- 848
```

Python (`.venv/bin/python3`, numpy/statsmodels 0.14.6): correlações Pearson, OLS com SE, Granger (lags 1–5) sobre thermodynamic_landauer_history — ver C02–C11.

---

## J. Protocolo de Auditoria Epistemológica e Operacional

### J.1 Tabela de claims desta auditoria

| Claim ID | Afirmação precisa | Estado epistemológico | Artefato/caminho | Evidência verificável | Dados reais ou simulados? | Limitações e pendências |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| A4-01 | Tabela `thermodynamic_landauer_history` contém 14.729 linhas | EXECUTED | data/monitor/sovereign_dodecatiad_runtime.sqlite | `SELECT COUNT(*)` → 14729 (saída capturada) | Reais (runtime vivo) | Contagem muda com o tempo (daemon escreve); janela 30-06→01-09 |
| A4-02 | Correlações Pearson de R.10.15 reproduzidas (6 pares, 4 casas decimais) | DERIVED | idem + numpy (`.venv/bin/python3`) | r: −0.5069/+0.9941/−0.2493/+0.1417/+0.0991/−0.0119 | Reais | t-stats do texto diferem ≤4% (ver C08) |
| A4-03 | OLS Φ_soma~T+P+H_t+PSI_io reproduz R²=0.2587, F(4,14724)=1284.61, β/SE/t idênticos | DERIVED | idem + numpy.linalg.lstsq | saída completa capturada | Reais | SE diferem ≤1e-6 (arredondamento do texto) |
| A4-04 | Granger lag1 F≈29.8/34.2 (texto 29.8414/34.1114) | DERIVED | idem + statsmodels 0.14.6 | F=29.7585 (p=4.97e-8); F=34.1833 (p=5.12e-9) | Reais | ΔF ≤0,3%; especificação original não exatamente reproduzida |
| A4-05 | Contagens datadas (v1.5.7/v2.0.2/v2.0.3/v2.1.3) compatíveis com tabelas vivas na data | EXECUTED | rizomatic/lattice_wear/phase_lock/snapshots/kernel | 13 contagens com `strftime('%s')` (Δ 0,2–12%) | Reais | Hora do dia das verificações originais desconhecida |
| A4-06 | Banco de evidência congelado: 62.246/66.953/217.531/609/9.720/2.275/147.736/37/1.441 | EXECUTED | data/evidence_v3/geometria_v3_evidence.sqlite; quantum_navigator_retrospective.sqlite | SELECT COUNT(*) por tabela (saídas capturadas) | Reais (freeze 08-12) | Texto diverge em 62.236/66.947/9.718/783.006 (C33/C34/C37/C43) |
| A4-07 | Banco IBM: 593 runs ≤31-07; 609 ≤08-11; 478 encounters ≤08-11; 4.776.010 shots ≤08-11; 210/194 ≤05-07; 202/195/142/132/136 ≤05-07; parity 69/67/65 | EXECUTED | data/quantum/ibm_quantum_runs.db | ~15 SELECTs (saídas capturadas) | Reais | 557/257/187/97 do texto não reproduzíveis (C22–C24); backfill provável |
| A4-08 | Achados A5 re-confirmados: 848 grupos/850 linhas; 1 linha NULL; sem índice; 8.093 TEXT; 480/480 NULL | EXECUTED | bancos data/monitor/ | queries de duplicação, PRAGMA index_list, typeof() | Reais | Contagens A5 cresceram (bancos vivos) |
| A4-09 | Constante canônica 878.4 e Hopfield ratio N_total/1130 | OBSERVED | docs/dodecatiad_four_versions_canonical.md L201 | leitura direta do doc | Documental | — |
| A4-10 | Qdrant: 1.851 coleções hoje | EXECUTED | http://127.0.0.1:6333/collections | GET /collections → 1851 | Reais | Contagem histórica 1.565 (08-10) não recuperável |
| A4-11 | phase_lock_score é coluna contínua (max 0.799) | EXECUTED | phase_lock_hysteresis_history | SELECT MIN/MAX/AVG/COUNT | Reais | Contradiz afirmação do texto (C58) |
| A4-12 | `multi_lattice_orchestrator.py` tem 1.101 LOC | EXECUTED | src/embodied_cognition/multi_lattice_orchestrator.py | `wc -l` → 1101 | Reais | Texto diz 776; changelog diz 682 |

### J.2 Manifesto de evidência

#### Feito e verificado
- [EXECUTED] 30+ consultas SQL read-only em 8 bancos `data/monitor/` + `geometria_v3_evidence.sqlite` + `ibm_quantum_runs.db` + `quantum_navigator_retrospective.sqlite`, todas com saída capturada (comandos no corpo e seção I).
- [EXECUTED] Verificação do script oficial `scripts/queries/omnimind_sqlite_observability.py --summary` (funciona; ciclo 85.449 / basal 85.822 / Setor 5 yellow).
- [DERIVED] Correlações, OLS e Granger sobre `thermodynamic_landauer_history` (14.729 linhas) com numpy/statsmodels 0.14.6 — reproduzem o núcleo empírico de R.10.15 (r, β, R², F) com precisão de impressão.
- [OBSERVED] Doc canônico `dodecatiad_four_versions_canonical.md` L201: N_total=878.4, Hopfield=N_total/1130.
- [EXECUTED] Re-confirmação integral dos achados A5 (848/850 duplicadas; 1 linha NULL; sem índice; TEXT em REAL; gemelo NULLs).

#### Simulado / modelado
- Nenhum dado foi simulado nesta auditoria. Todas as afirmações desta entrega derivam de consultas a bancos reais ou leitura de documentos canônicos.

#### Proposto, mas não aplicado
- Nada foi proposto para modificação de bancos (proibido). Sugestões de correção textual para o A6 estão em `discrepancias.log`.

#### Não verificado
- [UNVERIFIED] Correlações específicas das Predições 3 (r=0.20, −0.003, +0.13) e Kaggle (0.60/0.57) — requerem reconstrução do pipeline de H_t ou réplica de notebooks Kaggle externos.
- [UNVERIFIED] Predições 1, 2, 5 (GEO/CellXGene/HDC) — dados externos sem réplica local.
- [UNVERIFIED] Contagens de bancos rotacionados (somatic pré-28-08, gemelo pré-08-08, qbf pré-08-08) — apenas freezes do banco de evidência (08-12) conferem a direção de crescimento.
- [UNVERIFIED] Aleph (P2) — métrica não persistida em coluna.
- [UNVERIFIED] "8.629 experiências da testemunha silenciosa" e "32.509 tripletos hypernetwork" — artefatos não localizados.
- [UNVERIFIED] Granger com especificação idêntica à do texto (ΔF ≤0,3% com a especificação padrão).

#### Bloqueios
- [BLOCKED] Contagem exata de `557 runs` em 31-07-2026 — o banco contém 593 linhas com ts ≤ 31-07; sem coluna de inserção não há como distinguir backfill de contagem original. Nenhum acesso negado; limitação estrutural do schema.
- [BLOCKED] Contagem exata de Qdrant em 08-10 (1.565) — histórico de rotação de coleções não versionado; apenas contagem atual (1.851).

#### Riscos de erro
- Contagens datadas usam fim-do-dia UTC (23:59:59); as verificações originais podem ter ocorrido em horários diferentes — Δ de até 12% em contagens intra-dia (C44).
- As faixas das Eras I/II (C55–C56) foram validadas por médias dentro das faixas citadas; os extremos observados são mais amplos — o texto descreve a banda central, não os limites.
- O t-stat da correlação PSI_io×Φ_soma do texto (−68.64) coincide com o t do coeficiente OLS — interpretação de "cópia entre tabelas" é inferência (INFERRED), não comprovada.
- O `sector5_level` de `thermodynamic_landauer_history` (yellow 91,06%) não é citado no texto como percentual; incluído como contexto observacional, não como claim.
- A causa "backfill de sidecars" para 593 vs 557 é hipótese (INFERRED), não observada diretamente.

#### Próxima ação mínima verificável
- A6: aplicar as 12 correções [DIVERGENTE] de `discrepancias.log`; A5: considerar dedup das 850 linhas duplicadas e índice em `multi_lattice_history`; re-auditar C22–C24 após nova leitura do banco IBM se houver coluna de inserção adicionada.

### J.3 O que NÃO foi feito
- Nenhum banco foi modificado (read-only estrito, `sqlite3 -readonly` e URI `mode=ro`).
- Nenhuma escrita fora de `revisao/A4_confronto/`.
- Nenhum git commit/push.
- Nenhuma tabela multi-GB foi carregada em memória (todas as agregações foram SQL; única carga em memória: 14.729 linhas da tabela landauer ≈ 1 MB).
- Nenhum dado foi fabricado, simulado ou extrapolado além das consultas executadas.
