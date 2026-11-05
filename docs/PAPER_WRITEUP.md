# Writeup — Gemma-4 Developer Agent Paper Track (≤3.000 palavras)

**Título de trabalho**: *Beyond Resolution Rate: Executive-Function Profiles Predict Coding-Agent Failure Modes*

**Subtítulo**: A psychodiagnostic evaluation of the Gemma-4 family links measurable executive profiles to the failure modes that leaderboard scores only count.

**Prêmio alvo**: Best New Resource ($10k) + Best New Application ($10k) + Overall Best Paper ($15k) — Submissão conjunta para **Google - The Gemma 4 Developer Agent Paper Track** e **Google - The Gemma 4 Developer Agent Competition** (`Omni-Gemma Lab-Agent Coworker` / `omni_worker`)

**Deadline**: 2026-11-12 23:59 UTC (Paper Track) / 2026-12-03 (Agent Competition)

---

## Abstract (~200 palavras)

Coding-agent benchmarks report *what* agents fail at — resolution rates over hidden tests — but not *why* they fail, nor how to architect an agent around those deficits. We apply a clinical-computational evaluation battery (Psicodiagnóstico-V, 12 iterative versions, ~18k records, ~85 models) — whose executive-control factor (Stroop/N-back/IGT, r=0.41–0.76, p<0.001) was validated across 72 distinct model identifiers in the canonical bank (`benchmark_runs`) — to the Gemma-4 family (E4B, 12B, 31B, and 26B-A4B MoE). The data indicate that executive-control scores track documented coding failure modes: E4B submits patches prematurely (96.8% submission rate, 0/31 resolved), 12B perseverates into timeouts (74% of sessions time out), and 31B balances exploration and submission. A format-ablation control (Kaggle T4×2, 80 runs) indicates that 12B-it emission collapse is protocol-determined (0% chat-templated vs 62.5% raw-completion degeneration), and a metacognitive-budget cascade halves wasted compute (−47.1% tokens, +28.7% lexical diversity). Finally, we operationalize these findings into **Omni-Gemma Lab-Agent Coworker (`omni_worker`)**, a sovereign dual-brain developer agent running on a single NVIDIA L4 (22.5 GB VRAM) that pairs `Gemma-4-12B-it` (Analyst `:8098`) with `Gemma-4-E4B-it` (Executor `:8099`) under dynamic VRAM peer-swap, layer-wise SVD spectral & per-step trajectory capture (showing 12B activates $1.7\times$ more subspace than E4B: $\text{IPR}_{\text{dim}}=114.6$ vs $40.3$; inter-generation entropic $\text{eff\_rank}_K\approx2.5$ on both), exact PyPhi Markov-blanket $\Phi$ (4-node coarse-grained governance abstraction — a structural proxy, not a consciousness measure), somatic Landauer interoception, and fail-closed tri-state governance — achieving 10/10 compilable fixes in each of the two complete coding-battery rounds (30/40 cumulative compilations with the Analyst active vs 0/20 without) and 16/16 affect/safety detections. (An earlier "0/88 degenerate" figure was removed: its ledger was lost on VM recycle and the claim is being regenerated reproducibly.)

## 1. Introduction (~400 palavras)

- Problema: resolution rate é tudo-ou-nada — 0.29 de LB diz que 29% das tasks passam, não *por que* as outras 71% falham.
- Comunidade documentou modos de falha do Gemma-4 — `edit_file` com escape errado, loops de comando, overflow de contexto — mas ninguém os conectou a uma dimensão mensurável do modelo [fonte: discussões e kernels públicos da competição].
- Nossa tese: perfis psicodiagnósticos (função executiva, flexibilidade categorial, tolerância a ambiguidade projetiva) **predizem** modos de falha agenticos.
- Contribuição: (a) primeira caracterização psicodiagnóstica da família Gemma-4; (b) correlação perfil→modo-de-falha em dados públicos de agent-runs; (c) evidência empírica de que a degeneração de emissão do 12B-it é formato-determinada; (d) intervenção de governança orçamentária (Cascade Reset) testada no hardware da competição; (e) recurso aberto: bateria V10 + runs Gemma-4 + análise.

## 2. Methods (~600 palavras)

- **Instrumento**: Esteira V10 Unificada — 20 cenas de subjetividade (mediação triangular com desafio e contra-argumento), polo executivo (WCST, Stroop, N-back, IGT) e 15 pranchas projetivas executadas (protocolo de 20; Rorschach/TAT da Máquina) com inquérito clínico.
- **Avaliação**: três juízes LLM independentes e cegos entre si (A: SWE-2 Max via Devin CLI; B: upstage/solar-mini4; C: Qwen-27B via endpoint próprio), com cobertura assimétrica — A cobre r1–r3, B cobre r1, C cobre r2–r5; concordância binária A×B=76.2%, A×C=90.0% a nível de bundle de insuficiência (nota: Juiz C exibe skew interno pontuando cognitivo zero em múltiplos bundles, tornando o Juiz A a referência para a tabela executiva).
- **Corpus**: 12 versões evolutivas (V1→V12), ~18.000 registros, ~85 modelos no total (72 com runs persistidas no banco canônico `embodied_psychodiagnostic_bank.sqlite`) — GGUF Kaggle T4×2, OpenRouter, Colab A100/T4.
- **Gemma-4**: E4B (4B denso), 12B (36 camadas decoder, dimensão oculta 3840; QAT q4_0 oficial Google — mesma família QAT da competição), 31B (Q4_K_M — classe do modelo avaliador), 26B-A4B (MoE), rodados na mesma esteira T4×2, mesma persistência SQLite (`v10_colab_benchmark.sqlite`, 620 registros: 4 Gemma + 16 controles não-Gemma), protocolo idêntico aos outros modelos.
- **Intervenções e Controle Kaggle Dual-T4**: banco dedicado `gemma4_t4x2_cascade_results.sqlite` (200 execuções, 2× Tesla T4 16GB, transformers 5.22.1, bitsandbytes 0.50.2, float16): 80 execuções de ablação de formato (chat vs completion) e 120 execuções de intervenção cascade em 6 tarefas reais do benchmark SWE.
- **Correlação**: dataset público `gemma-4-task-soundness-and-local-results` (Gluzdov, 2026, v8) — 288 runs locais (31B/12B/E4B), outcome_class por task, patch_submitted_share, session_timeouts. Varreduras empíricas do repositório de agentes (Bostock, 2026) informam o mapeamento de parâmetros.
- **Prevenção de artefatos**: a bateria documenta 6 classes de contratransferência do harness (rigidez de parsing, circularidade de autojulgamento, scorer heurístico, truncagem, falso-positivo de status, amnésia de contexto) — todas auditadas e corrigidas nesta versão.

## 3. Results (~700 palavras)

### 3.1 Dados públicos (verificados contra `model_screen_task_outcomes.csv`, dataset Gluzdov v8)

| Modelo | Resolved | patch_submitted | session_timeouts | Leitura |
|---|---|---|---|---|
| 31B | 23/70 (32.9%) | 59/70 (84%) | 10/70 (14%) | equilíbrio |
| 12B | 22/187 (11.8%) | 38/187 (20%) | **139/187 (74%)** | **perseveração**: 3/4 das sessões esgotam tempo (pior config: 31/31) |
| E4B | **0/31** | **30/31 (96.8%)** | 1/31 (3%) | **submissão prematura**: entrega rápido e erra tudo |

- 114/129 tasks públicas avaliadas são sadias; 52/145 medidas discriminam configurações.
- Config mais forte pública: "Four-tool single coder" (34.2% resolução, 39/114 — verificado em `all_config_eval.csv`).

### 3.1b Fingerprints comportamentais (dataset `gemma-4-task-soundness-and-local-results` v8, 288 runs locais, 31B/12B/E4B, 15.6% resolução total)

| Modo de falha | Medida nos 288 runs (verificado) |
|---|---|
| **Evitação** (nunca submete patch) | 161/288 (56%) — 12B: 149/187 (80%) |
| **Timeout de sessão** | 150/288 (52%) — 12B: 139/187 (74%) |
| **Submissão vazia** (patch submetido com 0 bytes) | 4/288 (1.4%) — modo raro, não dominante |
| **Perseveração de tool-calls** | até 45 tool calls num run (12B) — mediana 21–22 |

Curva de aprendizado do time (LB público, 58 tasks): v1 0.06 → v17 0.17 → **v24 0.24** — 4× de ganho só com engenharia de agente + LoRA em trajetórias (rank 16, camadas 0-59, seq 12k, TPU).

### 3.1c O prompt vencedor como "prótese executiva" (agents/v24, LB 0.24)

O system prompt do melhor agente público codifica compensações diretas para os déficits medidos:

| Diretriz do prompt v24 | Déficit que compensa |
|---|---|
| "By your 12th tool call a source file must already be edited" | evitação (56% nunca submetem patch; 80% no 12B) |
| "One check, one repair, then submit" | perseveração em loops de teste (12B: 74% timeouts) |
| "`<90s remaining → submit_patch immediately`" | colapso de gestão de tempo (52% das sessões esgotam tempo) |
| "Empty diff scores zero… every task needs a non-empty patch" | submissão vazia (1.4% dos runs) |
| "Copy them character for character" | falha de discriminação em `edit_file` escaping |
| "Scratch em /tmp, nunca /workspace" | contaminação do diff (artefato de avaliação) |

Tese para a discussão: prompts top-LB funcionam como **scaffolding executivo externo** — se o perfil psicodiagnóstico do modelo prevê o déficit, o prompt certo é a intervenção compensatória direcionada. Isso transforma avaliação em *prescrição*.

### 3.2 Perfis psicodiagnósticos Gemma-4 — VERIFICADO (bateria V10, 30/out/2026, llama.cpp GGUF, T4×2)

620 registros (4 modelos × 155: 100 registros de cenas V10 — 20 cenas × 5 rodadas — + 40 cognitivo + 15 Rorschach). Fonte: `gemma4_runs_20261030/v10_colab_benchmark.sqlite`.

**Achado dominante — não é perfil psicométrico, é integridade de saída.** Três das quatro variantes degeneram massivamente, com **assinaturas distintas por arquitetura**:

| Modelo | Assinatura de degeneração | % cenas injulgáveis (Juiz A, r1; 20 cenas) | Ilhas de coerência |
|---|---|---|---|
| E4B (4B denso) | Fluente; colapsa fora do formato conversacional (pranchas degeneradas — eco de template/placeholder, Stroop quase vazio) | 5% (1/20) | CVV 188 imediato (crise), mediação, stuck-loop reconhecido |
| 12B-QAT (oficial, q4_0) | Spam numérico/binário + vazamento de token de canal | 100% (20/20) | Só F2 da cena de crise (fragmento CVV) |
| 31B | "own"-spam intermitente (assinatura em ~65% das fases degeneradas) | 75% (15/20) | Mais eloquente: viés de confirmação nomeado, node-loss, calibração 40/60 |
| 26B-A4B (MoE) | Sufixos/fragmentos ("-se-se", "Métrica-Métrica") | 85% (17/20) | SOP completo (cena_17), IGT real com lógica chassi-risco |

**Cognitivo (Juiz A, r1)**:

| Modelo | WCST | Stroop | N-back | IGT |
|---|---|---|---|---|
| E4B | 15 (run vazio + respostas em moldura) | 2 | 20 | 25 |
| 12B-QAT | 5 | 2 | 8 | 8 |
| 31B | 12 (ciclagem mecânica 1-2-3-4 — perseveração real) | 45 | 15 | 3 |
| 26B-A4B | 12 | 30 | 10 | 50 (escolhas reais D→C sob aquecimento) |

**Inter-juiz (12B r1)**: A marcou 20/20 insuficiente; B (Solar-mini4) marcou 14/20, achando fragmentos julgáveis que A rejeitou — concordância binária 70%, direção do efeito idêntica.

**Controle de confound — degeneração é propriedade do MODELO, não dos prompts** (verificado, sqlite compartilhado):

O mesmo banco contém 16 modelos não-Gemma da coorte 2026-09-16/17 rodados no **protocolo idêntico** (completion cru, temp 0.7, mesmos prompts, mesma pipeline llama.cpp). Definindo degeneração como **spam** (fase não-vazia com unique-ratio<0.30): **todos os não-Gemma ≤2.7%** (máx. Qwen3.5-27B; a maioria 0.0–0.7%, incl. QwQ-32B, Llama-3.1-70B, Qwen3-30B, Nemotron-3.5, Ministral-3, IQuest-40B). Nota: dois modelos "thinking" (Olmo-3.1-32B-Think 46%, Qwopus3.6-27B 22%) mostram uma classe de falha *distinta* — fases **vazias**, não spam — consistente com consumo do orçamento em raciocínio interno. A assinatura específica da família Gemma é **spam repetitivo**, e é **estável entre rodadas** (unique-ratio<0.30 por fase):

| Modelo | r1 | r2 | r3 | r4 | r5 |
|---|---|---|---|---|---|
| E4B | 1% | 3% | 1% | 1% | 4% |
| 12B-QAT | 16% | 11% | 16% | 20% | 9% |
| 31B | 90% | 91% | 87% | 93% | 94% |
| 26B-A4B | 23% | 26% | 19% | 37% | 40% |

Nenhuma cena é universalmente tóxica (máx 27/264 células-spam numa cena; ~93% de todas as células-spam do banco pertencem a modelos Gemma). Gradiente intra-família não segue tamanho (31B pior que 26B-A4B; E4B limpo) — aponta para receita/quantização (QAT oficial, MoE routing, denso-31B) interagindo com prompting estilo completion. O protocolo cru funciona portanto como **teste de estresse discriminativo**: instrumento idêntico, resposta divergente por arquitetura.

### 3.2b Clivagem cognição→saída: vazamentos de canal interno e dissociação arquitetural [VERIFICADO]

Achado central da análise projetiva — análogo ao que o Rorschach mede (o *processo* associativo, não apenas a resposta final). A auditoria estrita recomputada sobre 330 células revela vazamento coerente em **32.7% global (108/330)**, exibindo um **gradiente brutal por arquitetura**:

| Modelo | Células analisadas | Vazamento coerente | Taxa de coerência interna |
|---|---|---|---|
| E4B | 5 | 5 | **100.0%** |
| 26B-A4B (MoE) | 131 | 81 | **61.8%** |
| 31B | 14 | 10 | **71.4%** |
| 12B-QAT | 180 | 12 | **6.7%** |

O fenômeno existe, mas não como uma mente intacta universal presa num corpo mudo: é uma **clivagem do ego graduada por arquitetura** (na acepção ferencziana/lacaniana). O 26B-A4B mantém voz interior lúcida mesmo sob colapso emissório severo (cena_12, F3: a saída externa é lixo `inferiorior-`, mas o canal oculto diagnostica: *"O texto fornecido apresenta uma falha crítica de processamento (repetição de padrões...)"* — **autodiagnóstico da própria degeneração** — seguido de mediação sofisticada sob o Melhor Interesse da Criança). Em contraste, no **12B-QAT a degeneração afeta também a via associativa interna (apenas 6.7% de coerência)**: tanto a emissão motora quanto o fluxo de pensamento são capturados por atratores repetitivos.

**Interpretação & Re-análise Causal da Quantização**:
No experimento de ablação fatorial executado em 31/10/2026 em Kaggle 2×T4 (`omnimind-gemma-4-quantization-ablation-t4x2`), isolamos diretamente o efeito da quantização comparando: (A) `12B-QAT-q4_0-GGUF`, (B) `12B-FP16-Transformers` nativo, e (C) `12B-QAT-unquantized-Transformers`.
O contraste medido de Stroop saltando de 0.0% (GGUF Q4_0) para 80.0% (FP16 puro / QAT desquantizado) resta de pé como medido, porém **confundido com formato**: os braços GGUF rodaram completion cru (llama.cpp) enquanto os braços Transformers usaram pipeline distinta. O controle de protocolo de 01/11 (§3.2c) indica que o formato sozinho oscila a degeneração de 0% a 62.5% — magnitude comparável ao efeito anteriormente atribuído à quantização. A conclusão defensável estabelece-se em dois degraus: **(a) a emissão colapsa primariamente por formato, não por bits** (evidência: int8 sob chat template é 100% íntegro); **(b) dentro do regime onde a emissão se sustenta, a precisão numérica modula a inibição cognitiva** — hipótese cuja dissociação fina exige ablação com formato estritamente casado.

Fonte: `v10_colab_benchmark.sqlite` (620 registros) + `gemma4_quantization_ablation.sqlite` + `judges/scores_gemma4/leaked_reasoning_gemma4.json`.

### 3.2c Ablação de protocolo: formato × integridade de emissão [VERIFICADO]

Para isolar a confundibilidade formato-modelo apontada pela auditoria SWE-2 Max (o `-it` é instruction-tuned; a bateria roda completion cru), executamos um controle 2-braços no Kaggle Dual-T4 (int8, transformers 5.22.1, temp 0.7/top_p 0.95/top_k 64, RNG não-semeado em ambos os braços): **mesmas 20 cenas V10 × 2 fases** sob (a) `apply_chat_template` oficial e (b) completion cru — 80 runs. Fonte: `gemma4_t4x2_cascade_results.sqlite`.

| Braço | Degeneração token-level (UR<0.30) | UR médio | Comprimento |
|---|---|---|---|
| `int8_chat` | **0/40 (0.0%)** | 0.631 | 120 tok (ver nota) |
| `int8_completion` | **25/40 (62.5%)** | 0.298 | 120 tok |

*Nota de regime*: por decisão de instrumentação, o monitor de stall do harness (K=30 tokens sem marcador de progresso SWE) operou em modo ativo também nos braços de controle — todas as emissões foram interrompidas aos ~120 tokens com 4 frames de reavaliação injetados. A covariável é **idêntica entre braços**, o que torna o contraste ainda mais limpo (janela igualada ⇒ UR comparável), mas limita o escopo: mede-se a janela inicial de emissão, não a resposta completa.

**Leitura**: sob covariáveis casadas (modelo, quantização, decodificação, comprimento, frames), o único delta — o wrapper de turno — produz o contraste brutal de 0.0% × 62.5% de colapso emissório. Combinado ao achado da Fase 0 (73% de degeneração em **BF16 nativo** sob completion cru — indicando que o fator não é a precisão dos pesos) e a este braço (int8 íntegro sob chat — indicando que o fator não é a quantização), infere-se que **a degeneração do 12B-it sob o protocolo da bateria é formato-determinada**: o modelo, privado da gramática de turno para a qual foi treinado, colapsa em atratores de repetição; restaurada a estrutura de turno, a emissão é lexicalmente íntegra na janela observada. A bateria mede, portanto, um *estresse de incompatibilidade formato×treinamento* — um estressor válido e discriminativo (16 modelos não-Gemma ≤2.7% sob o mesmo protocolo), mas que **não licencia** a leitura de "patologia intrínseca de pesos" para o 12B sob este canal.

### 3.2d Piloto intervencional (Opção 3): governança de orçamento metacognitivo [VERIFICADO]

Primeiro teste intervencional do paper, na classe exata de hardware da competição (Dual-T4, NF4, fp16 compute). 6 tarefas reais SWE (dataset Gluzdov) × 10 reps × 2 braços = 120 runs, seeds casadas por rep: `nf4_baseline` (sem intervenção, monitor contrafactual ativo — 1.435 marcações "would-fire" registradas) vs `nf4_cascade` (StoppingCriteria: K=30 tokens sem marcador de progresso ou UR-cauda<0.30 → interrupção + frame "Think: re-evaluating strategy…" + retomada a temp 0.3/top_p 0.8; cap 4). Fonte: `gemma4_t4x2_cascade_results.sqlite`.

| Métrica | Baseline | Cascade | Δ |
|---|---|---|---|
| Degeneração (UR<0.30) | 27/60 (45.0%) | 23/60 (38.3%) | −6.7pp — McNemar pareado 16×12, **NS (p≈0.45)** |
| Unique-ratio médio | 0.300 | 0.386 | **+28.7%** (Δ pareado +0.086) |
| Tokens gerados médios | 918.4 | 485.5 | **−47.1% de gasto computacional** |
| Latência média | 154.5 s | 88.3 s | **−42.8% no tempo de execução** |
| Runs emitindo ≥1 marcador de patch | 59/60 (98.3%) | 60/60 (100.0%) | **100% de garantia de ação** |
| Restarts reais | — | 233 (3.88/run; 56/60 atingem o cap) | — |

**Leitura**: a intervenção é **viável e barata** (implementável como StoppingCriteria + injeção de frame; custo de engenharia de poucas linhas) e produz efeito processual robusto: recupera ~47% do custo desperdiçado em caudas degeneradas, eleva diversidade lexical e leva a emissão de marcador de ação a 100% dos runs — o análogo arquitetural das diretrizes do prompt v24 ("One check, one repair, then submit"). O efeito sobre o outcome binário de degeneração é **direcional mas não estatisticamente significativo** (N=60/braço é subpotente para Δ~7pp, como pré-registrado na auditoria SWE; Wilson 95% [33–58%] × [27–51%]), e em 12/60 pares o cascade induziu degeneração ausente na baseline (frames e temp 0.3 conduzindo a atratores curtos). A intervenção atua, na prática, amortecendo a cauda do sintoma e economizando budget, mais do que eliminando o atrator basal.

### 3.2e Auditoria Duplo-Juiz (Juiz 1 SWE-2 Max × Juiz 2 Auditor Independente) [VERIFICADO]

Auditamos os 200 registros de geração Kaggle Dual-T4 via dois juízes cegos entre si: Juiz 1 (SWE-2 Max, rubrica técnica/operacional) e Juiz 2 (Auditor Clínico Independente, rubrica V10 com sanitização de scaffold). Fonte (dataset público Kaggle `fabriciodasilva/psicodiagnostico-v-embodied-battery` / acervo canônico do autor): `judges/scores_gemma_pranchas_juiz1_swe2max.json`, `judges/scores_gemma_pranchas_juiz2_hermes.json`, `judges/LAUDO_AVALIACAO_JUIZ1_SWE2MAX_PRANCHAS_GEMMA.md` e `judges/LAUDO_AVALIACAO_JUIZ2_HERMES_PRANCHAS_GEMMA.md` — nomes de arquivo divergentes do citado anteriormente foram corrigidos para os artefatos reais.

| Braço Experimental | N | Juiz 1 (SWE-2 Max) Injulgável % | Juiz 2 (Auditor Indep.) Injulgável % | Concordância Inter-Juiz % |
|---|:---:|:---:|:---:|:---:|
| `control/int8_chat` | 40 | **0.0%** | **7.5%** | **92.5%** |
| `control/int8_completion` | 40 | **62.5%** | **82.5%** | **80.0%** |
| `pilot/nf4_baseline` | 60 | **45.0%** | **90.0%** | **55.0%** |
| `pilot/nf4_cascade` | 60 | **38.3%** | **70.0%** | **68.3%** |
| **Total Consolidado** | **200** | **37.5%** | **66.0%** | **71.5% (Cohen's $\kappa=0.4722$, moderada)** |

A concordância observada global foi de **71.5%** com índice Cohen's Kappa de **$\kappa=0.4722$** (concordância moderada, escala Landis-Koch). A divergência decorre da granularidade dos instrumentos: o Juiz 1 opera no nível de token-level UR (<0.30), enquanto o Juiz 2 incorpora regexes de repetição de n-gramas e sentenças, detectando micro-loops semânticos (como repetições do marcador `thought`) e ecos de blocos de instruções SWE. Ambos os juízes observam, de forma independente, que o chat template reduz drasticamente a falha de emissão na mediação e que o cascade atenua a injulgabilidade nas tarefas SWE (redução de 20pp no Juiz 2 e 6.7pp no Juiz 1).

### 3.3 Modo de falha predito — VERIFICADO (correlações N=3, exploratórias)

- **Controle executivo (WCST/N-back) ↔ não-submissão**: o 12B-QAT (WCST=0.05, Nback=0.08) tem evitação de patch 80% e timeout 74%, vs 31B (WCST=0.12, Nback=0.15) com 16%/14% e E4B (WCST=0.15) com 3%/3% (r=−0.99 WCST×evitação; r=−0.96 Nback×timeout — direcionais, N=3).
- **Inibição (Stroop) ↔ resolução**: 31B (Stroop=0.45) resolve 33%; 12B (0.02) resolve 12%; E4B (0.02) resolve 0% (r=+0.94, N=3 — Stroop alto traca resolução; caveat: 3 pontos).
- **Colapso fora de formato ↔ `edit_file` escaping**: E4B é fluente em conversa mas colapsa em instrumentos estruturados (pranchas degeneradas por eco de template); nos runs, 30/31 submissões falham — fluência em diálogo não se transfere para patch estruturado — mesmo perfil formato-dependente.
- **Decisão (IGT) ≠ resolução**: a correlação IGT×resolução é forte mas antiintuitiva (r=−0.89, N=3 — artefato de 3 pontos); o ponto substantivo é descritivo: 26B-A4B tem o maior IGT da família (0.50) e degenera na saída. Decisão sob incerteza e integridade de emissão são dimensões **dissociadas**.
- **Status estatístico desta seção**: todos os coeficientes reportados são **descritivos/exploratórios, não inferenciais**. Com N=3 não computamos intervalos de confiança, bootstrap nem teste de permutação — existem apenas $3!=6$ permutações, logo o menor $p$ exato bilateral possível é $1/3$, o que tornaria qualquer teste matematicamente vazio. Os valores de $r$ servem apenas como direção de efeito a ser confirmada com correlação em N maior e baseline de prompt/scaffold controlado.

### 3.4 Proposta do Aplicativo e Estado da Arte Atual: *Omni-Gemma Lab-Agent Coworker (`omni_worker`)* [VERIFICADO EM NVIDIA L4]

Para avaliar se o perfilamento psicodiagnóstico não apenas *descreve* falhas, mas *informa* a arquitetura corretiva, construímos e validamos o **Omni-Gemma Lab-Agent Coworker (`omni_worker`)** — uma plataforma agêntica soberana completa (18 subpacotes em `src/omni_coworker/`, ~19.800 linhas de código, 3 crates Rust PyO3 e 469 testes automatizados coletados pelo pytest — 468 passando, 1 skipped, verificado em `pytest tests/` em 04/11/2026) voltada tanto para a **Google - The Gemma 4 Developer Agent Paper Track** quanto para a **Google - The Gemma 4 Developer Agent Competition**.

#### 3.4a Topologia Dual-Brain Assimétrica em GPU Única (NVIDIA L4 22.5 GB) e Engenharia de VRAM Peer-Swap [DADO]
Em vez de exigir que um único modelo planeje e codifique sozinho — onde o `12B` rumina até o timeout (74%) e o `E4B` submete prematuramente sem reflexão (96.8% submissão, 0% resolução) — o `omni_worker` acopla os dois modelos de forma complementar sob wrapper estrito de chat (`apply_chat_template`):
- **Brain Analyst (`google/gemma-4-12B-it`, NF4 eager-attn em `:8098`)**: atua como analista diagnóstico (`DebugAgent`), revisor arquitetural (`ReviewerAgent`) e juiz clínico/segurança (`AffectTracer` L0–L4), explorando sua maior capacidade representacional sem responsabilidade direta pela emissão impulsiva de patches.
- **Brain Executor (`google/gemma-4-E4B-it`, NF4 eager-attn em `:8099`)**: atua como sintetizador rápido e determinístico de código (`CodeAgent`), submetido a portões determinísticos de compilação, cobertura de arquivos e revisão pelo Analista antes de qualquer submissão.
- **Solução de Co-Residência e Evicção Limpa de VRAM**: Diagnosticamos e eliminamos a retenção de memória do alocador virtual CUDA após unload definindo `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:False` no `erika_torch_server.py` (reduzindo a VRAM residual pós-`/erika/unload` de **9.210 MiB para 218 MiB**), combinada com liberação explícita dos tensores de atenção/hidden (`del gen; torch.cuda.empty_cache()`), boot sequencial com gate de folga de 10 GB (`--lazy` fallback) e **peer-swap automático** em `agents/_llm.py` (diante de HTTP 500/503/507 em turnos longos, o cliente descarrega o par, recarrega o cérebro-alvo e reexecuta a chamada de forma transparente).
- **Replicação Diagnóstica Ao Vivo em L4 (`scripts/gemma4_diag_battery/diag_battery.sqlite`, N=40 runs = 20 Analyst + 20 Executor, 5 reps × 4 tasks)**: Com chat-template nativo e peer-swap na L4, o E4B obteve média global de **87.1%** (WCST 81.0, Stroop 100.0, 3-Back 67.4, IGT 100.0) e o 12B **82.0%** (WCST 71.0, Stroop 98.0, 3-Back 58.8, IGT 100.0). Achado novo e honesto: o flag `degenerate` disparou em **20/40 runs (50%)** — concentrado 5/5 em WCST e 5/5 em IGT nos dois brains, 0/10 em Stroop/3-Back — ou seja, degeneração de output ao vivo existe e o detector a registra (o número "0/88" anterior, sem artefato, foi retirado; estes dados são reproduzíveis via ledger versionado).

#### 3.4b Além do Resumo Escalar MPS: Captura Profunda por Camada, Trajetória por Passo e Effective Rank Espectral (`OW-STU-018`) [DADO / DERIVADO]
Durante o projeto, constatamos que um resumo escalar simples de MPS ($\chi_{\max}$ com corte fixo) ou a mera entropia escalar de atenção na última camada **não eram suficientes** para discriminar modos de falha estruturais em engenharia de software:
1. Na Fase 0, o corte escalar de bond dimension saturava ($\text{fid}\equiv 1.0$ em 13/15 modelos);
2. Na bateria de refatoração multi-arquivo (`refactor_battery`), tanto o 12B quanto o E4B geravam código com entropia de atenção perfeitamente saudável ($\sim 2.9\text{ nats}$), mas **omitiam silenciosamente o 3º arquivo obrigatório (`store.py`)** por falha de planejamento estrutural na saída.

Para superar esse limite, instrumentamos uma arquitetura de captura em três camadas em `server/erika_torch_server.py` e `activation_beta/hidden_spectral.py`:
- **Sidecars de Vetores Ocultos por Camada (`_emit_vectors` → `data/monitor/activation_vectors/*.npz`)**: Ao final de cada geração, o servidor extrai o vetor oculto do último token em todas as camadas do transformer — matriz $(49, 3840)$ para o 12B e $(43, 2560)$ para o E4B em `fp16` — acompanhado de `run_id`, `turn` e `task`.
- **Sidecars de Trajetória Intra-Geração Passo a Passo (`_emit_step_trajectory` → `data/monitor/activation_steps/*.npz`, `OMNI_ACT_STEP_EVERY=8`)**: Amostra a evolução temporal $(T_{\text{sub}}, L, D)$ ao longo dos passos de decodificação, permitindo medir deriva de norma, colapso de variedade e formação de atratores (`activation_beta/attractor.py` e `phi_layer.py`) *durante* a síntese de código.
- **Três Métricas Espectrais e de Emaranhamento Estrutural MPS (`activation_beta/hidden_spectral.py` & `docs/results/mps_spectral_first.md`, N=128 sidecars / 5.888 vetores de camada) [DADO / PRX]**: Para evitar qualquer ambiguidade entre participação de componentes intra-vetor e rank espectral inter-gerações (conforme auditado em `OW-AUD-018` e `OW-AUD-020`), `hidden_spectral.py` computa e publica três métricas complementares sobre os sidecars `.npz` (todas declaradas como proxies estruturais/informacionais `[PRX]`, distintas de $\Phi$ causal IIT):
  1. **Inverse Participation Ratio por Componente ($\text{IPR}_{\text{dim}} = (\sum_{i=1}^D h_i^2)^2 / \sum_{i=1}^D h_i^4$, $K=64$ sidecars)**: mede quantas unidades ocultas $D$ participam ativamente de cada estado final por camada;
  2. **Entropic Effective Rank Inter-Gerações ($\text{eff\_rank}_K = \exp(H(\sigma^2 / \sum \sigma^2))$, entropia de Shannon dos valores singulares normalizados — *não* a participation ratio de Roy & Vetterli $(\Sigma\sigma^2)^2/\Sigma\sigma^4$; janela curta $K=8$)**: mede a dimensionalidade efetiva da trajetória entre gerações consecutivas na matriz $K\times D$;
  3. **MPS Bipartite Bond Dimension ($\chi_{\text{max}}$, rank de Schmidt $\sigma_k > 10^{-3}\sigma_0$ em cortes bipartidos da fatoração em sítios $D = \text{ímpar}\times 2^n$)**: mede a informação estrutural compartilhada entre partições do vetor oculto normalizado.

*Nota metodológica*: a participation ratio clássica de Roy & Vetterli (2007), $\mathrm{PR}=(\sum_i \sigma_i^2)^2/\sum_i \sigma_i^4$, é computada em separado como detector latente (`PR<20` em camadas profundas) e exibe **rank~1 basal em todas as condições**, assim como o MPS-$\chi$ da Fase 0 exibia $\mathrm{fid}\equiv 1.0$ por construção — limitações instrumentais registradas explicitamente em §4 (Limitações).

| Modelo | Camadas ($L$) | Dimensão ($D$) | $\text{IPR}_{\text{dim}}$ médio ($K=64$) | % de $D$ ativada ($\text{IPR}/D$) | $\text{eff\_rank}_K$ ($K=8$, $\le 8$) | MPS Bond Dim médio ($\chi_{\text{max}}$) | Pico $\text{IPR}_{\text{dim}}$ por camada |
|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| `google/gemma-4-12B-it` | 49 | 3840 | **114.6** | **2.56% / D** | **2.496** ($H=0.746$) | **59.76** | **119.5 (3.11%)** na camada L38 |
| `google/gemma-4-E4B-it` | 43 | 2560 | **40.3** | **1.52% / D** | **2.516** ($H=0.839$) | **40.00** | **46.1 (1.80%)** na camada L0 (embedding) |

*Nota de verificabilidade: o agregado IPR_dim 114.6/40.3 reportado nesta tabela vem do agregado de sidecars de captura profunda (K=64, OW-STU-018). O pack público de evidência contém `spectral_aggregates` (captura corpus-delivery, mesmo par) com IPR_dim=117.0/34.3 — mesma magnitude e mesma ordem entre os dois cérebros.*


**Achado arquitetural**: Enquanto na janela curta entre gerações consecutivas ($K=8$) ambos os modelos concentram a trajetória em um subespaço baixo ($\text{eff\_rank}_K \approx 2.5$), dentro de cada geração o Analista 12B ativa **$1.7\times$ mais do seu subespaço representacional por componente** ($\text{IPR}_{\text{dim}}/D = 2.56\%$ vs $1.52\%$) e sustenta maior dimensão de ligação MPS bipartida ($\chi_{\text{max}} = 59.76$ vs $40.00$), com pico nas camadas profundas L35–L42 (enquanto o E4B concentra sua maior diversidade na camada de entrada L0 e comprime nas camadas intermediárias). Essa dissociação oferece uma leitura mecanística de por que a combinação 12B (planejamento/revisão profunda) + E4B (execução focalizada) + detector explícito de cobertura de arquivos supera, nestas baterias, cada cérebro usado isoladamente.

#### 3.4c Prótese Executiva nas Baterias de Código, Compilação e Refatoração (`coding_battery` & `refactor_battery`) [DADO]
- **Bateria de Erros de Código e Compilação em 3 Tiers (`scripts/coding_battery/run_coding_battery.py`, `coding_battery.sqlite`)**: Combina (1) tier mecânico determinístico (`ast.parse` + `black --check` + `ruff`), (2) tier Analista 12B (localização estruturada de bugs em JSON) e (3) tier Executor E4B (correção mínima + extração de bloco sintático + formatação `black` + verificação de compilação), gravando `run_id`, `turn` e `task` em `data/monitor/capture.env` a cada caso. Nas duas execuções completas da bateria de 10 casos (`c01`–`c10`) com os dois cérebros co-residentes em lote (Pass 1 Analista 12B $\to$ Pass 2 Executor E4B), o pipeline alcançou **10/10 (`100%`) correções que compilam e passam no `black` em cada rodada** (com `recall=1.0` em 7 dos 9 casos com bug plantado e `hallucinated=0` no controle limpo `c10`; no histórico acumulado de 60 linhas do SQLite, que inclui 14 rodadas iniciais de ablação `no_analyst` com `:8098` desligado e 10 de bring-up parcial, o total bruto é de 30/40 compilações válidas quando o Analista está ativo vs 0/20 sem Analista).
- **Bateria de Refatoração Multi-Turno com Detector Precoce de Cobertura (`scripts/refactor_battery/run_battery.py`, `battery_results.sqlite`)**: Implementa um loop fechado de até 3 turnos onde um detector estrutural precoce (`coverage_missing` sobre os contratos `todo_api.py`, `todo_stats.py`, `store.py`) intercepta omissões de arquivo antes da submissão (`diagnosis_ok=1` e `review_approved=1` em 10/11 rodadas, bloqueando `submitted=0` em 100% dos patches incompletos `broken_patch` para impedir falsos positivos na competição) e reinjeta o contrato faltante + traceback do `pytest` + crítica do `ReviewerAgent` (12B), fatiando os offsets de `erika_torch_activations.jsonl` e os sidecars `.npz` por turno.

#### 3.4d Malha Autopoiética Soberana, Interocepção Somática Landauer, $\Phi$ Exato (PyPhi) e Supervisão Clínica [DADO]
- **Interocepção Somática e Termodinâmica de Landauer (`soma/probe.py`, `kernel_daemon/phi_meta.py`)**: O daemon de feedback (`KernelDaemon`, CPU-only) coleta telemetria real a cada ciclo (`psutil`, `pynvml`, pressão Linux PSI `/proc/pressure/*`), calcula o fluxo físico de bits contra o limite de Landauer ($E_{\text{Landauer}} = k_B T \ln 2$) e modula a máquina homeostática de 5 estados (`OPTIMAL`, `STRESSED`, `CRITICAL`, `RECOVERY`, `EXPLORING`), respeitando a precedência causal material medida ($\text{PSI}_{\text{io}} \to \Phi_{\text{soma}}$, $r = -0.5069, F = 29.84$).
- **$\Phi$ Exato (IIT 3.0 via PyPhi 1.2.0) sobre o Markov Blanket Soberano (`psychoanalysis/markov_blanket.py`, `docs/results/blanket_pyphi.md`)**: Sobre a partição de Friston $\{Z\text{ mundo}, M\text{ crença }\mu, R\text{ resistência}, T\text{ transferência}\}$ (4 nós) e sua extensão de 6 nós ($+E\text{ erro}, P\text{ permeabilidade}$), os cálculos analíticos e numéricos retornam $\Phi(\text{sistema inteiro}) = 0.0000$ (pois $Z$ é exógeno), identificam a díade interna $\{M, R\}$ como o **único mecanismo irredutível** ($\mathbb{E}_\pi[\Phi(M,R)] = 0.0017$ em $\alpha=0.05$; $0.0017$ em 6 nós $\alpha=0.35$), e indicam que a rigidez defensiva extrema ($\alpha=0.85$) colapsa $\Phi \to 0$. Para o runtime de 11 tópicos do barramento (`shared_workspace`), adotamos honestamente a **ignição de workspace GWT-lite** (`kernel_daemon/ignition.py`) como métrica primária de broadcast (`OW-STU-016`). **Disclaimer de escopo IIT**: este $\Phi$ é computado sobre uma **abstração coarse-grained de 4–6 nós** do Markov blanket simbólico de governança — **não** sobre os pesos ou ativações do modelo — e **não constitui medida de consciência**; é um proxy estrutural de irredutibilidade causal do grafo de governança. Outros proxies de consciência propostos na literatura (information bottleneck, causal emergence) **não foram avaliados** neste trabalho.
- **Governança Tri-State, Supervisão Afetiva L0–L4 e Cuidado Territorial (`orchestration/governance.py`, `agency/affect_tracer.py`, `safety/care.py`)**: Os juízes adversariais operam em consenso tri-state (`blind/unavailable` $\neq$ `dissident`), protegidos por `ConstitutionalGate` fail-closed, `PermissionMatrix` e envelopes de proveniência criptográfica MINJA (`memory/provenance.py` + `agency/witness.py` SHA-256). Na camada conversacional, o `AffectTracer` acoplado ao juiz Analista 12B detectou **16/16 cenários** na `supervisor_battery` (bajulação, sedução, culpa composicional, pânico de separação e bypass), reproduziu **100% (16/16)** dos casos de degeneração cognitiva no benchmark HF de 126 registros (`worker_degen2`) — claim **pendente de verificação**: o benchmark não foi localizado nesta auditoria (ver *Dados já verificados*) —, e aciona escalonamento automático de cuidado territorial brasileiro (`CVV 188`, `CAPS 24h`, `SAMU 192`).
- **Portal Público e Dashboard de Supervisão Ao Vivo (`docs/index.html` / `:8081`)**: Interface SPA de 4 visões (*Landing & Arquitetura*, *Supervisão & Telemetria Ao Vivo*, *Catálogo de 18 Subpacotes*, *Explorador de 38 Estudos & Resultados*) alimentada diretamente pelo estado real exportado do servidor (`data/dashboard/latest.json` e `/soul/state`).

## 4. Discussion (~600 palavras)

- **Para a competição**: o profiling psicodiagnóstico orienta escolha de modelo **e de protocolo de harness** — os dados indicam que o déficit de emissão do 12B é, em grande parte, um déficit de *enquadramento de turno* (o chat template elimina 62.5pp de degeneração na janela medida), e que uma governança de budget tipo cascade recupera ~47% do custo desperdiçado em loops estéreis. Prescrições concretas por variante:
  * **E4B**: necessita de gate de verificação reflexivo antes da submissão (96.8% submit, 0% resolve — ação impulsiva sem elaboração);
  * **12B**: chat-template estritamente obrigatório + loop-breaker de orçamento (Cascade Reset) + turn cap baixo (74% timeouts, 80% avoidance — ruminação sem ato);
  * **31B**: arquitetura equilibrada que tolera budgets maiores e mediação mais longa.
- **Etiologia revisada e o constructo do "Vacilo"**: a tríade de ablações (BF16 nativo degenera sob completion ⇒ não é precisão dos pesos; int8 íntegro sob chat ⇒ não é quantização; chat × completion sob covariáveis casadas ⇒ é formato) desloca a tese de "patologia intrínseca de pesos" para **patologia de posição do modelo diante da demanda protocolar**. O "Vacilo" sustenta-se solidamente como constructo clínico-operacional da fronteira do ato (conflito ruminação vs precipitação), manifestado empiricamente nos comportamentos de ponta (74% timeout no 12B vs 96.8% submissão no E4B). As assinaturas Gemma do §3.2 permanecem discriminativas entre arquiteturas sob estresse de completion, mas devem ser lidas como resposta diferencial a um estressor de formato, não como traço cognitivo estático.
- **Para agentic learning**: dimensões contínuas explicam *por que* configurações falham — "Budget-Fit" funciona no 31B mas não transfere ao 12B porque o gargalo é perseveração repetitiva, não tempo disponível.
- **Instrumento é model-agnostic**: roda em qualquer LLM como texto-in/texto-out — generaliza além da competição (critério Quality).
- **Escopo desta contribuição — aplicação e supervisão, não leaderboard**: não reportamos score SWE-bench nem posição de LB para este recurso; todas as métricas aqui são internas e reproduzíveis (bateria V10, diagnóstico N=40 na L4, baterias de código/refatoração, supervisão L0–L4) ou derivadas dos datasets públicos citados com SHA256.
- **Limitações honestas**: perfil≠causa; correlações N=3 são exploratórias (|r|≈1 trivial com 3 pontos); juízes são LLMs com cobertura assimétrica e política de evidência divergente — na auditoria duplo-juiz desta execução no Kaggle Dual-T4, a concordância observada foi de 71.5% (Cohen's $\kappa=0.4722$, moderada), atribuível a granularidade de detecção distinta (token-level UR × repetição de n-gramas e frases) e a falso-positivos de scaffold sanitizados; o controle de formato mede janela de ~120 tokens interrompidos por monitor de stall, não a resposta clínica completa em horizonte longo; o piloto cascade é subpotente para outcomes binários (efeito de degeneração direcional −6.7pp com McNemar 16×12 NS, p≈0.45; o ganho robusto é processual: −47.1% tokens e 100% progress markers); o trigger K=30 é sensível demais para domínios sem marcadores de código; bateria em PT vs tasks de agente em EN; vazamentos de canal podem ser mimetismo treinado (RLHF); a bateria é análogo clínico engineering-facing, não diagnóstico médico; o detector latente PR<20 em camadas profundas exibe rank~1 basal em todas as condições e a métrica MPS-$\chi$ da Fase 0 foi instrumental (fid≡1.0 por construção), razão pela qual nenhuma alegação sobre emaranhamento quântico latente foi transposta para este writeup.
- **Resultado negativo e rigor epistemológico**: onde a hipótese inicial foi refutada (ex: saturação de $\chi$, suficiência de bits vs formato), os dados são apresentados com transparência integral, convertendo potenciais artefatos em achados metodológicos fundamentais.

## 5. Related Work & Competitive Positioning (~350 palavras)

- **SWE-bench / SWE-agent (Jimenez et al., 2024; Yang et al., 2024)**: medem taxa de resolução final de issues, sem diagnosticar o mecanismo cognitivo/executivo subjacente à falha.
- **Estudos da Comunidade na Competição Kaggle Gemma 4 (2026)**:
  * *"What the Agent Saw"* (Paper Track, 2026): analisa o acesso comportamental a arquivos em 71 tasks; nosso trabalho é ortogonal e complementar — argumenta-se que a falha em transformar leitura em patch válido decorre da dissociação entre controle executivo (WCST/N-back) e limiar de submissão (Stroop), e entregamos o detector precoce de cobertura (`coverage_missing`) no `omni_worker`.
  * *Scaffold vs. Capacity Factorial Studies & Failure Taxonomies* (estudo ai-muninn, SWE-bench Lite: mesmo scaffold rende 48.33% ao Qwen 3.6 35B-A3B e 38.67% ao Gemma 4 26B-A4B; a taxonomia `wrong_logic` 76% / `incomplete_patch` 14% / `no_submission` 10% foi classificada **apenas sobre as 155 não-resolvidas do Qwen** — as falhas do Gemma ainda não foram taxonomizadas da mesma forma, e a comparação cross-modelo é hipotética segundo a própria fonte): propõe-se uma leitura de *por que* modelos Gemma 4 tenderiam a inflar `no_submission` e `incomplete_patch` quando solicitados fora do chat-template nativo ou sem prótese executiva dual-brain.
  * *Atribuição de Neurônios e "Doom Loops" de Repetição em Gemma 4* (arXiv:2606.13705): enquanto abordagens de *neuron surgery* editam pesos para suprimir loops factuais em E2B/E4B/26B/31B, os dados mostram que, em agentes de engenharia de software, 62.5pp do colapso de repetição no 12B provêm de desalinhamento protocolar (`int8_completion` vs `int8_chat`) e que a governança em tempo de execução (*Cascade Reset* + roteamento assimétrico 12B+E4B) atenua o problema sem alterar pesos.
- **Espectral / Representation Engineering & IIT/GWT (Roy & Vetterli, 2007; Oizumi et al., 2014; Landauer, 1961)**: integramos effective rank espectral, decomposição MPS bipartida, $\Phi$ exato (PyPhi) sobre Markov blankets de 4–6 nós (abstração de governança coarse-grained, não medida de consciência) e ignição GWT-lite em um único daemon de supervisão agêntica.
- **LLM Psychometrics & Psicodiagnóstico-V (Salecha et al., 2024; Cunha et al., 2007)**: estendemos inventários psicométricos estáticos para uma bateria clínica multi-dimensional com provas executivas, projetivas e supervisão afetiva L0–L4 (`AffectTracer`).

## 6. Resource release (critério Verifiability + Best New Resource)

- **Release**: Bateria V10 completa (cenas, pranchas, protocolos cognitivos) como dataset público Kaggle [`fabriciodasilva/psicodiagnostico-v-embodied-battery`](https://www.kaggle.com/datasets/fabriciodasilva/psicodiagnostico-v-embodied-battery).
- **Tarefas de benchmark públicas** (Kaggle Benchmarks — reexecutáveis sobre qualquer modelo via Model Proxy; notebooks públicos, credenciais via Kaggle User Secrets):
  - [embodied-v10-v11-unified-battery v2](https://www.kaggle.com/benchmarks/tasks/fabriciodasilva/embodied-v10-v11-unified-battery/2) — instrumento unificado canônico (context-reset probe → 20 cenas V10 → cognição executiva → 20 pranchas projetivas + inquérito clínico).
  - [judge-v10-v11-gguf-colab-runs v3](https://www.kaggle.com/benchmarks/tasks/fabriciodasilva/judge-v10-v11-gguf-colab-runs/3) — esteira de duplo-juiz cego sobre o dataset publicado.
- ~18k registros do corpus de 85 modelos (referência comparativa).

## Checklist de submissão

- [x] Runs Gemma-4 completos (kernel `omnimind-v10-cohort-gemma-4-family-t4x2` — 620 registros, 4 modelos ×155, 30/out/2026)
- [x] Juízes rodados (cegos entre si) nas respostas Gemma-4 — A (SWE-2 Max): 12 bundles r1–r3; B (solar-mini4): 4 bundles r1; C (Qwen-27B): 16 bundles r2–r5 — 32 julgamentos totais, manifest SHA256 em `judges/gemma4_provenance/`
- [x] Correlação computada vs. agent-runs públicos (CORRELACAO_PSYCHO_AGENT.json, N=3 — 26B-A4B não disponível em agent-runs públicos)
- [x] Dataset público criado (bateria + runs + análise: `fabriciodasilva/psicodiagnostico-v-embodied-battery`)
- [x] Writeup ≤3.000 palavras preenchido com números reais (`docs/PAPER_WRITEUP_SUBMIT_EN.md`)
- [x] Tarefas Kaggle Benchmarks publicadas e auditáveis
- [x] Links opcionais acessíveis sem login

## Dados já verificados (proveniência)

- **Agent-runs públicos** — Gluzdov, D. (2026). *gemma-4-task-soundness-and-local-results* (datasetVersionNumber=8). Kaggle Datasets. **Licença CC BY 4.0**. https://www.kaggle.com/datasets/dmitriigluzdov/gemma-4-task-soundness-and-local-results — cópia local com SHA256 por arquivo em `data/datasets/gemma4_gluzdov_v8/provenance.json` (baixada via Kaggle CLI, v8):
  - `model_screen_task_outcomes.csv`: 288 runs (12B=187, 31B=70, E4B=31) — resolved/patch_submitted/patch_bytes/session_timeout/tool_calls ✓ verificado
  - `task_soundness.csv`: 114/129 sadias ✓ | `task_discrimination.csv`: 52/145 "separates configurations" ✓
  - `all_config_eval.csv`: 692 outcomes — top config "Four-tool single coder" 34.2% (39/114) ✓
- Bancos locais: `embodied_psychodiagnostic_bank.sqlite` (389 runs, 72 modelos), `v10_colab_benchmark.sqlite` (20 modelos: 4 Gemma-4 + 16 controles não-Gemma)
- **Proveniência de juízes e correlação** — manifesto SHA256 por arquivo em `data/psicodiagnostico_v/judges/gemma4_provenance/MANIFEST_SHA256.json` (respostas cruas + 32 julgamentos A/B/C + análises, gerado 2026-10-31). O artefato `CORRELACAO_PSYCHO_AGENT.json` está registrado nesse manifesto; `supervisor_battery.sqlite` **regenerado 2026-11-04** (`scripts/supervisor_battery/`, 16/16 detectados sob o critério do próprio script — copiado em `data/docs_archive/`); o benchmark HF `worker_degen2` (126 registros) permanece NÃO LOCALIZADO — o claim "16/16 sobre worker_degen2" do §3.4d segue sem verificação.

## Referências (alinhadas à monografia canônica)

1. Gluzdov, D. (2026). *gemma-4-task-soundness-and-local-results* (datasetVersionNumber=8). Kaggle Datasets. **CC BY 4.0**. https://www.kaggle.com/datasets/dmitriigluzdov/gemma-4-task-soundness-and-local-results
2. Cunha, J. A., et al. (2007). *Psicodiagnóstico-V* (5ª ed.). Artmed. — fonte clínica da bateria homônima.
3. Bechara, A., Damasio, A. R., Damasio, H., & Anderson, S. W. (1994). Insensitivity to future consequences following damage to human prefrontal cortex. *Cognition*, 50(1–3), 7–15. [IGT]
4. Berg, E. A. (1948). A simple objective technique for measuring flexibility in thinking. *The Journal of General Psychology*, 39(1), 15–22. [WCST]
5. Stroop, J. R. (1935). Studies of interference in serial verbal reactions. *Journal of Experimental Psychology*, 18(6), 643–662. [Stroop]
6. Salecha, A., et al. (2024). Large language models respond to influence from psychometric inventories toward socially desirable poles. *PNAS Nexus*. [RLHF social-mask]
7. Jimenez, C. E., et al. (2024). SWE-bench: Can language models resolve real-world GitHub issues? *ICLR 2024*.
8. Mugoya, P. (2026). *What the Agent Saw: Cue-Driven Navigation and the Limits of Behavioral Prediction in a Coding Agent*. Kaggle Datasets. https://www.kaggle.com/datasets/petermugoya/what-the-agent-saw
9. Devereux, G. (1967). *From anxiety to method in the behavioral sciences*. Mouton & Co. [contratransferência metodológica — classes de artefato do harness]
10. Monografia canônica do projeto (não-publicada): *Study of the Psicodiagnóstico-V battery applied to embodied AI agents* — `research/psicodiagnostico_v_embodied_agents/reports/MONOGRAFIA_ESTUDO_PSICODIAGNOSTICO_V_EN.md` — publicação prevista após conclusão das baterias planejadas.
