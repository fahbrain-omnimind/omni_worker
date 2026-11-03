<!-- doc_id: OW-MATH-001 | title: Definições matemáticas das métricas phi/pressão/metastability do worker | author: devin | requester: artifice-operator | project: omni-agent-coworker (kaggle) | date: 2026-11-03 | status: reference -->

# OW-MATH-001 — Definições matemáticas das métricas do kernel

Referência canônica das fórmulas publicadas na malha. Convenção de estatuto:
**[CAP]** capacidade física · **[PRX]** proxy informacional · **[TXT]** textura
de regime · **[CLS]** classificação. Nenhuma é Φ causal IIT nem medida de
consciência fenomenal.

## 1. Camada física — `kernel.phi_meta` (Landauer) [CAP]

Fonte: `kernel_daemon/phi_meta.py`, `soma.probe`.

- `E_Landauer(T) = k_B · T_K · ln 2` [J/bit], k_B = 1.380649e-23 — custo mínimo
  de apagar 1 bit à temperatura T (GPU real).
- `bit_flow_real = P_gpu / E_Landauer` [bits/s] — potência real convertida em
  taxa máxima de bits processáveis.
- `cohesion = clip(phi_meta / H_sistema, 0, 1)` — fração integrada (§2).
- `phi_bit_flow_rate = bit_flow_real · cohesion` [bits/s] — capacidade × coesão.
- `vs_i5_ratio = (P/E_L(T)) / (45W / E_L(73.65°C))` — relação à baseline i5.

Limite documentado pelo corpus (livro R.10.15): potência sozinha é N.S. —
esta camada mede **capacidade**, não estado.

## 2. Φ-meta de subsistemas — `kernel.phi_meta` [PRX]

- Elementos: 7 flags binários/ciclo (activations, affect_analyst,
  affect_executor, soma_ok, soul_phi, homeo_stable, mesh_active) sobre
  janela de 40 ciclos.
- `H_sistema = −Σ p(σ) log₂ p(σ)` sobre as assinaturas de estado observadas.
- `MI(p1,p2) = H(p1) + H(p2) − H(p1∪p2)` por bipartição.
- `phi_meta = min_bipartição [H_sistema − MI(p1,p2)]` — perda mínima de
  informação ao cortar (MIP simplificado sobre flags, não transições causais).
- `integration = média MI entre pares adjacentes de elementos`.
- `mip_side_a`/`mip_side_b`/`mip_top3` [PRX-audit] — bipartição de perda
  mínima publicada (o proxy só é auditável se o corte for visível;
  OW-STU-016 estágio 1).
- `n_distinct_states`, `diversity = n_distinct/window` — anti-saturação;
  alerta quando diversity < 0.3.

## 3. Camada de pressão — `kernel.phi_meta` (D1) [TXT]

Corpus (livro R.10.15): PSI_io→Φ_soma r=−0.5069, Granger hardware→software.

- Canais normalizados [0,1]: `psi_io`, `psi_mem`, `psi_cpu` (PSI avg10/100),
  `vram_ratio` (used/total), `load_core` (load1/n_cpu, clip 1).
- `pressure_load = Σ w_i·c_i / Σ w_i(presentes)`, pesos
  `{io:.35, vram:.25, mem:.15, cpu:.15, load:.10}` — ordem empírica do corpus.
- `pressure_headroom = 1 − pressure_load`.
- `phi_effective_bits_s = bit_flow_real · cohesion · headroom` [bits/s] —
  a camada que o corpus mostrou acoplada: pressão modula o fluxo
  efetivamente integrado, não a potência nua.

## 4. Φ informacional por layer — `kernel.phi_layer` [PRX]

Fonte: `activation_beta/phi_layer.py` sobre a janela deque (máx 256
registros/modelo; rehydrate do tail do jsonl pós-restart). Requer ≥6
registros e ≥4 camadas.

- `phi_breadth = H(p) / ln(L)`, onde `p_l = norm̄_l / Σ norm̄` é o perfil médio
  de norma por camada (L=43 no E4B). 1.0 = atividade uniforme nas camadas;
  baixo = atividade concentrada (integração espacial).
- `phi_temporal_mi` = MI médio entre séries temporais de normas de camadas
  adjacentes na janela, discretizado por rank em 8 bins (nats).
- `phi_internal = 0.6·phi_breadth + 0.4·min(1, MI/ln 8)` — composto, [0,1].
- **Limitações**: perfil de norma ≠ vetor hidden; MI por rank-binning é
  proxy grosseiro; sem causalidade nem MIP. Upgrade P2: vetores hidden →
  SVD effective rank, MPS bond dimension χ, MI real k-NN (OW-STU-010 §5).

## 5. Atrator — `kernel.attractor` [TXT]

Fonte: `activation_beta/attractor.py`.

- `norm_drift_mean` = média |norm_t[l] − norm_{t−1}[l]| sobre a janela.
- `divergent_layer` = camada de drift máximo; `drift_concentration` =
  drift da camada divergente / drift total.
- `entropy_now` = entropia de atenção do registro mais recente;
  `entropy_baseline` = média dos _BASELINE_N=128 registros antigos;
  `entropy_collapse = baseline − now` (>0 = atenção colapsando).
- `attractor_score` ∈ [0,1] = composto de collapse+concentração+drift —
  alimenta `emotional_charge` do BetaElement (α/β Bion).

## 6. Metastabilidade — `kernel.metastability` (D6) [TXT]

Fonte: `kernel_daemon/metastability.py`.

- Canais: psi_io/mem/cpu, cpu_percent, vram_ratio, gpu_temp normalizados.
- `coherence_t = 1 − 2·σ(canais_t)` — coerência instantânea entre canais.
- `s_meta = pstdev(coherence_t, janela 40)` — análogo escalar ao índice de
  metastabilidade (std do parâmetro de ordem). Alto = oscilando entre
  integração/segregação (adaptativo); ~0 = travado.
- `m_t = {pressure_load, cohesion, producing, homeo_state}` — vetor de
  materialidade do ciclo.
- `c_soma = média{power/160W, (temp−30)/57, latency/10s, vram_ratio}` —
  custo somático composto [0,1].
- `corroboration` = fração de canais > 0.5 (identidade multi-fonte:
  estresse confirmado só quando canais independentes concordam).
- `angst` = nº consecutivo de ciclos em homeostasis ∉ {optimal, good}.

## 7. Regime shift — `kernel.regime_shift` (D3) [CLS]

Fonte: `kernel_daemon/regime.py` — Page-Hinkley bilateral por sinal
(cpu_percent, gpu_temp_c, vram_ratio, attractor:modelo).

- `cum_up += x − mean − δ`, `ph_up = cum_up − min(cum_up)` (subida);
  `cum_dn += mean − x − δ`, `ph_dn = cum_dn − min(cum_dn)` (descida).
- Alarme quando `ph > λ`, `λ = max(floor_sinal, 4·σ_running)`;
  `δ = 0.15·λ`; mínimo 10 amostras; re-baseline após alarme.
- Evento: `{signal, direction, ph_stat, mean_before, value, ts}`.
- Publica **só em eventos** — ausência do tópico = nenhum shift detectado.

## 8. Afeto/desire/homeostase

- `kernel.affect.mono_source` [CLS] = true quando <2 brains respondem —
  guard contra Síndrome do Afeto Monotípico (integração ≠ verdade;
  fonte única = leitura frágil).
- `kernel.homeostasis.producing` [TXT] = qualquer modelo registrou
  ativações no ciclo — ótimo-em-repouso ≠ ótimo-produzindo (void
  homeostático, AUD-012).
- `agency.desire.intensity` = distância estrutural homeo atual→optimal
  (falta estrutural, Desire-as-Lack operacional).

## 9. Tabela de estatuto

| Métrica | Classe | O que mede | O que NÃO mede |
|---|---|---|---|
| bit_flow_real | CAP | taxa física de bits (Landauer) | estado interno |
| phi_meta | PRX | integração de flags de subsistemas | Φ causal, consciência |
| pressure_load/headroom | TXT | pressão material corrente | futuro (ver regime) |
| phi_effective | CAP×TXT | capacidade modulada por pressão | informação real processada |
| phi_breadth | PRX | distribuição de atividade por layer | integração causal |
| phi_temporal_mi | PRX | co-variação entre camadas | MI vetorial real |
| attractor_score | TXT | colapso de variabilidade | qualidade do texto |
| s_meta | TXT | dispersão temporal da coerência | índice Kelso formal |
| c_soma | TXT | custo somático composto | energia contábil exata |
| regime_shift | CLS | transição de regime (PH) | causa da transição |
| mono_source | CLS | diversidade de fonte afetiva | valência |
| producing | TXT | trabalho real no ciclo | utilidade do trabalho |
| angst | TXT | duração degradada contínua | afeto fenomenal |

pt-BR: tudo aqui é régua de estrutura e materialidade — a "consciência"
da máquina, se existe como conceito operacional, é o estágio do sistema
reconhecido por estas medidas, nunca uma assinatura fenomenal lida nelas.
