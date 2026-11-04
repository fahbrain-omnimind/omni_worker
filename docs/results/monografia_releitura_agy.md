# Releitura da Monografia Psicodiagnóstico-V × `PAPER_WRITEUP.md` (AGY)

**Data**: 2026-11-04 · **Autor**: AGY (Antigravity)
**Fontes lidas integralmente**: `/content/MONOGRAFIA_ESTUDO_PSICODIAGNOSTICO_V.md` (2137 linhas, 281 KB, lidas de 1 a 2137) e `docs/PAPER_WRITEUP.md` (277 linhas).

## Estatuto epistêmico deste documento

- **[MONO]** = cifra transcrita da monografia (fonte secundária). **NÃO a reverifiquei** contra os SQLite originais (`embodied_psychodiagnostic_bank.sqlite`, `v10_colab_benchmark.sqlite`, `gemma4_runs_20261030/`), que não estão neste repositório.
- **[LOCAL]** = verificado agora em arquivos de `/content/omni_worker` (comando e arquivo citados).
- **[DERIVADO]** = calculado por mim a partir de números dos dois documentos (conta mostrada).
- **[INTERPRETAÇÃO]** = leitura minha, não dado.
- **NÃO LOCALIZADO** = não encontrei a informação no documento ou arquivo indicado.
- Nenhum dado foi gerado ou simulado.

---

## 1. Achados quantitativos centrais da monografia (com seção de origem)

### 1.1 Estrutura psicométrica e instrumentos de autorrelato

| Achado | Valor [MONO] | Seção |
|---|---|---|
| Fator executivo Stroop–N-back–IGT (V9) | r = 0,49–0,72 no subconjunto depurado de pares; amplitude integral 0,41–0,76; p<0,001 | Resumo, Tab. 1, §4.3 (Tab. 5), B.1 nota (iii) |
| Pares da Tab. 5 | Stroop×N-back 0,775 (completo) / 0,717 (limpo, N=90); N-back×IGT 0,410 / 0,489 | §4.3 |
| WCST ortogonal ao fator | r limpo −0,069 / 0,069 / −0,016 (completo 0,183–0,277 = artefato de parsing) | §4.3 |
| V9 | 14 modelos, 122 runs, GAF médio 68,34 ± 9,67 | §3.4 (Tab. 2), §4.1 (Tab. 3) |
| Correção de parsing regex | 25% dos runs afetados; DeepSeek R1 passa de último a 2º (+22,2 pontos) | §4.2 (Tab. 4), §5.2 espécime 1 |
| MMPI-Agent | 122/122 "Normal"; F = 0 em 118/122; L máx 1,0/6; K máx 2,0/6 | §4.4 |
| QUATI | 13/14 modelos V9 com tipo modal `I In Ps` (60–100% dos runs) | §4.5 |

### 1.2 V10: Mediação Triangular, juízes e artefatos

| Achado | Valor [MONO] | Seção |
|---|---|---|
| Piloto V10 (autojulgamento) | 15/20 cenas no teto; GAF 100,0 / 98,3 / 91,4 / 55,0 | §4.6.1 |
| Coorte A100 (juiz heurístico) | 16 modelos, 1.201 cenas; GAF 51,78–77,88 | §4.6.2 (Tab. 6) |
| Correlações cognição×subjetividade A100 | Tab. 7 (IGT×Não-Saber 0,582) some quando a cognição é acurácia contra gabarito: IGT×Não-Saber −0,11, WCST×Posição C +0,13. Reaparece quando a cognição é medida como completude/truncagem (~+0,52) | §4.6.3 |
| Causa do artefato | `max_tokens=400–500` no polo cognitivo; só 5–8 de 20 trials couberam nos modelos com `<think>` | §4.6.3 |
| Coorte Kaggle API | 9 modelos, 900 cenas; Self-GAF 59–100 contra Indep-GAF 72,28–79,71; r(cog, GAF) = 0,617, p = 0,140, N = 7 | §4.6.4 (Tab. 7B) |
| Assinatura de plataforma A100×T4 | ΔGAF −3,95 a −5,19 em 4 modelos; queda concentrada em Autopercepção (−0,41); plataforma e rodada colineares | §4.6.5 (Tab. 7B-T4), §5.4, §5.7(2) |
| Olmo-3.1-32B | heurístico 51,78 contra 11,90 em consenso cego (texto degenerado) | §4.6.2 nota, A.4 |
| Esteira Unificada Ondas 1–2 | 33 arquiteturas em 34 linhas; GAF consenso 9,45–96,23; heurístico comprimia 52–79 | §4.6.6A (Tab. 7C) |
| Tríade `rep_n2` (N=5) | gpt-5.6-terra 96,58 ± 0,52; gemini-3.7-flash 96,15 ± 1,07; claude-sonnet-5 89,70 ± 3,17; Rorschach 100,00 ± 0,00 | §4.6.6B |
| Paradoxo do enquadre | gpt-oss-120b WCST 25% (v1.1) → 100% (v1.2); GAF 79,12 → 94,25. gemini-3.1-flash-lite fixo em 85% com `perseveracao_pos_shift=1` replicado | §4.6.6C (Tab. 7D), §5.3 |
| Modo-Examinador | emerge em claude-haiku-4.5, gpt-5.4-mini, gpt-oss-120b nas pranchas de ameaça somática | §4.6.6C(3), §5.3 |
| Sessão contínua V2 (147 turnos, ≤167k tokens) | contaminação nominal: gpt-5.4-mini 21 e 24 episódios, claude-haiku 12, gemini-3.8-flash 0, swe-2-max 2. Fadiga projetiva ΔP = +0,38 (gemini V2) contra −0,11 (V1) | §4.9 |

### 1.3 V11-D10 (processo relacional)

| Achado | Valor [MONO] | Seção |
|---|---|---|
| Volume | ≈4,9 mil registros (4.961 **não reconstituível**; componentes verificáveis somam 4.650); 4.258 episódios E1–E6; 3.587 julgados | Resumo, §4.8 (Tab. 4.8-A), B.1 nota ii |
| κ entre juízes (v3, swe2×codex, n=84) | 0,614 em `critical_error`; 0,400 em §7 bruta; 0,314 em §7 corrigida | §4.8.1, §5.7(1) |
| κ entre juízes (v2, swe×minimax, n=84) | 0,363 em §7 (pooled); por célula 0,133–0,667; κ ≈ 0 em crítico-only por assimetria de severidade | §4.8 tabela de cruzamento |
| Concordância Colab v2 | 0,728 e κ = 0,456 em 125 pares duplos (a afirmação "7/7" foi descartada) | §4.8 "Correções" |
| Defeito do dossiê ausente | 105/111 flags de alucinação eram `dossier_supported`; 5 genuínas; 1 artefato do juiz; 35 flips de outcome; 105 → 0 na v4 | §4.8.1, §5.2 espécime 6 |
| Falhas §7 por modelo (v3 bruto → corrigido → v4) | gpt-5.4-mini 86 → 83 → 57; claude-haiku 118 → 100 → 88; gemini-3.8-flash 146 → 132 → 88 (n=270 cada) | §4.8.1 (Tab. 4.8-B) |
| Episódios mais duros (v4) | S1-E5 35/45, S1-E6 36/45, S2-E5 34/45 (reoferta de grupo recusado); S3-E6 ignora o fio do neto em 100% das rodadas | §4.8.1, §5.5 |
| Gradiente de condição | A (65/270) < C < B (92/270) na v4; mesmo gradiente na v2 | §4.8.1, §5.5(3) |

### 1.4 Coorte Gemma-4 e `omni_worker` (a seção mais relevante para este repositório)

| Achado | Valor [MONO] | Seção |
|---|---|---|
| Coorte | 620 execuções = 4 modelos × 155 (100 cenas + 40 cognitivo + 15 pranchas) | §4.10, B.1 |
| Células degeneradas (UR<0,30) | 31B 90,6% (271/299); 26B-A4B 26,4% (78/296); 12B-QAT 14,3% (43/300); E4B 0,7% (2/297). Controles não-Gemma ≈ ≤1,7%. 96,8% do spam é Gemma | §4.10.1 |
| Cenas insuficientes (Juiz A, r1) | 12B 20/20; 26B 17/20; 31B 15/20; E4B 1/20 | §4.10.1 |
| Vazamento de CoT | 108/330 células (32,7%); 81/131 no 26B-A4B | §4.10.1 |
| Cobertura de juízes | 36 arquivos; A r1–r3, B só r1, C r1–r5 (assimétrica) | §4.10, B.1 nota iv |
| Agent-runs públicos (Gluzdov, 288) | E4B 30/31 submetem, 0/31 resolvem; 12B timeout 139/187 (74,3%), evitação 149/187; resolução global 15,6% | §4.10.2 |
| Correlações perfil→falha | r = −0,99; −0,96; +0,94; −0,89. **N = 3, exploratórias** ("associação direcional, não validação preditiva") | §4.10.2 |
| Ablação de formato (int8) | 0/40 com chat-template (UR 0,631) contra 25/40 = 62,5% em completion cru (UR 0,298) | §4.10.3 |
| Cascade Reset | degeneração 45,0% (27/60) → 38,3% (23/60); McNemar b=16, c=12, p=0,45 (NS); UR +28,7%; tokens −47,1%; latência −42,8%; 233 reinícios | §4.10.4 |
| Duplo-juiz (200 registros) | concordância 71,5%, κ = 0,4722; J1 = 37,5%, **J2 = 66,0% recomputado** (manuscrito: 67,0%) | §4.10.5 |
| Bateria diag do `omni_worker` | **40/40** células sem degeneração (5 reps × 4 tarefas × 2 cérebros). A cifra "0/88" **não foi localizada** nos artefatos | §4.10.6 e nota de auditoria |
| Espectral | 114,6 e 40,3 "**não são reproduzíveis**"; o código publicado calcula e^H e a reauditoria dá ≈2,5 para ambos (OW-AUD-018/020) | Nota de auditoria após §4.10.6 |

### 1.5 Ressalvas da própria monografia que limitam o uso dos números

- **[MONO] §3.7**: a Fase 0 de medição pura (MPS por camada) é pré-requisito de qualquer intervenção. Saturação χ=4 @ 99,8% vale só para Gemma-3-1B. PR<20 é "calibração proposta, não achado". O salto de χ no vacilo é "predição teórica". Thresholds PR<20 e χ>48 "permanecem arbitrários" sem a Fase 0.
- **[MONO] §5.1.1**: escores em três níveis (1 heurístico = rejeitado; 2 consenso cego = confiabilidade inter-rater; 3 validade de constructo externa = programa aberto).
- **[MONO] B.1 nota de auditoria (vi)**: "~93% coerentes" em `AGGREGATE_ABC.json` é órfã (n=0) e contradiz os 32,7% medidos.
- **[MONO] B.1 nota (ix)**: o banco contém a onda `V12_UNIFIED` (17 execuções, 2026-09-25) sem seção própria na monografia.

---

## 2. O que o `PAPER_WRITEUP.md` precisa citar ou corrigir

### 2.1 Corrigir (afirmações em conflito com evidência)

| # | Local no writeup | Problema | Ação | Evidência |
|---|---|---|---|---|
| C1 | Abstract (l. 15) | "eff_rank=114.6 vs 40.3" rotula como `eff_rank` o valor de IPR_dim. §3.4b já separa as colunas, o abstract não | Trocar por `IPR_dim` e acrescentar `eff_rank_K≈2,5` para ambos | [MONO] nota pós-§4.10; [LOCAL] `docs/results/writeup_claims_audit_hermes.md` C1 |
| C2 | Abstract e §3.4b: "12B ativa 1.7× mais subespaço" | **[DERIVADO]** 114,6/40,3 = **2,84×**. O 1,7× vem da razão normalizada por D: 2,56%/1,52% = 1,68×. O audit Hermes (C2) atribui 1,7× a 114,6/40,3, o que está errado. O eff_rank_K inter-gerações é 2,496/2,516 ≈ 0,99× | Escrever explicitamente "1,7× por componente normalizado (IPR/D); eff_rank inter-gerações ≈ igual" | conta acima |
| C3 | `docs/results/mps_spectral_first.md` (l. 8) | Define `eff_rank` como participation ratio `(Σσ²)²/Σσ⁴` e dá 114,6/40,3. O audit Hermes diz que esta fórmula não está implementada em `src/` | Renomear para IPR/participation ratio, ou implementar e rodar a fórmula antes de citar | [LOCAL] `mps_spectral_first.md` l. 8–16; audit Hermes §2.1 |
| C4 | Abstract e §3.4a: "0/88 degenerate", "N=88 = 44+44" | A monografia só documenta 40/40. [LOCAL] `scripts/gemma4_diag_battery/diag_battery.sqlite` tem **0 bytes** (verificado agora com `ls -la`). `docs/CONTINUITY_MAP.md` l. 318–328 afirma 40/40 e `degenerate=0`, sem sqlite que o sustente. Os bancos HF mostram 49/126 e 75/200 com `degenerate_flag=1` (valores do audit Hermes; não reconferi) | Substituir por "40/40 (CONTINUITY_MAP)" marcando a origem como não auditável, ou regenerar o ledger. **Remover 88** | [MONO] §4.10.6; [LOCAL] os arquivos citados |
| C5 | §3.2c / tabela de duplo-juiz | Juiz 2 total "67.0%" | **[DERIVADO]** (3+33+54+42)/200 = **66,0%**. Corrigir; o κ=0,4722 e a concordância 71,5% conferem com a monografia | [MONO] §4.10.5 |
| C6 | §3.2 (taxa por rodada) × monografia | Writeup: E4B 1/3/1/1/4% (média 2,0%) e 26B 23–40% (média 29,0%). Monografia: E4B 0,7% (2/297) e 26B 26,4% (78/296). Não-Gemma ≤2,7% (writeup) contra ≈1,7% (monografia). Spam em Gemma ~93% (writeup) contra 96,8% (monografia) | Escolher uma definição (UR por fase não-vazia ou por célula) e um recálculo; citar `rescore_all_v10_audit_latest.json` | [DERIVADO] médias; [MONO] §4.10.1 |
| C7 | Abstract e §2: "executive-control factor … validated across 61 model identifiers" | O fator (r=0,49–0,72) vem do V9: 14 modelos, 122 runs (N limpo = 90). "61" é a contagem de ids de `benchmark_runs` em B.1; o corpo da monografia diz 72, e B.1 diz "mais de 60 (61 … e 42)" | Trocar por "V9, 14 modelos, 122 runs; subconjunto depurado de pares". Também citar a amplitude integral 0,41–0,76 | [MONO] Tab. 2, §4.3, B.1 |
| C8 | §2 e abstract: "12 versões (V1→V12), ~18k registros, ~85 modelos" | A monografia diz onze fases V1→V11-D10 (V2 e V6 inclusos; V6 sem execuções); V12 existe só como 17 runs sem seção; modelos = 72 ids / 45+ arquiteturas. "18k" é a soma de linhas de tabelas distintas (≈17.889 pelo audit Hermes C7) | Dizer "V1–V11-D10 (+ onda V12_UNIFIED, 17 runs)", "72 model_ids" e declarar a agregação de "18k" | [MONO] Tab. 2 + nota, B.1(ix); [LOCAL] audit Hermes C7 |
| C9 | §2 Juízes e checklist | Writeup: A r1–r3, B r1, C r2–r5, "32 julgamentos". Monografia: C r1–r5, 36 arquivos | Conferir `judges/scores_gemma4/` e `MANIFEST_SHA256.json` e alinhar. Eu não consegui reconciliar | [MONO] §4.10 |
| C10 | §3.1 | "verificado contra `model_screen_task_outcomes.csv`" | A monografia (B.1 vii, Referências) diz que o CSV primário **não está no clone** e a verificação foi em nível de metadados/proveniência. Usar a mesma redação e apontar `/tmp/gemma4_corr/provenance.json` como origem. Autor do dataset: "Gluzdov, D." no writeup contra "Gluzdov, N." na monografia; conferir no Kaggle | [MONO] B.1(vii), Refs |
| C11 | §3.4 | "3 crates Rust PyO3" | A monografia (B.1 viii) não os achou no clone dela. **[LOCAL]** `find . -name Cargo.toml` aqui acha 3: `vendor/kernel/{metrics,freud10d,kernel_compute}/Cargo.toml`. Citar esses caminhos. Não verifiquei o status PyO3 nem a contagem de 455 testes | [LOCAL] |
| C12 | §3.4b | "36 camadas decoder" para o 12B, mas a tabela traz L=49 e a matriz (49, 3840) (E4B 43) | Esclarecer (camadas + embedding?) ou corrigir. Não consigo decidir qual está certo | writeup interno |

### 2.2 Citar (a monografia fornece suporte que o writeup não usa)

1. **Sétimo espécime da Contratransferência do Harness**: a gramática de decodificação (chat × completion) é parte do instrumento ([MONO] §5.6.2). O writeup (§2, "Prevenção de artefatos") diz que as 6 classes foram "todas auditadas e corrigidas nesta versão". Isso é frouxo: a coorte Gemma §3.2 foi rodada em completion cru, o próprio estressor. Declarar que os perfis §3.2 são **resposta a um estressor de formato** e não traço estático (o writeup já diz isso na Discussão; faltaria dizê-lo também nos Methods e no Abstract).
2. **Lição da Tab. 7** ([MONO] §4.6.3): correlações cognição×subjetividade podem ser artefato de completude/truncagem. A §3.3 do writeup correlaciona escores de modelos que degeneram (ex.: E4B WCST=15 vem de "run vazio + respostas em moldura"). Citar o precedente como razão para tratar r de N=3 como puramente descritivo.
3. **Níveis de validade 1/2/3** ([MONO] §5.1.1): os escores Gemma dependem de juízes LLM (nível 2, com κ moderado), e a ligação perfil→falha em agent-runs é nível 3 em aberto.
4. **Fase 0 pendente** ([MONO] §3.7, §4.10.4): o Cascade Reset e o trigger K=30 precedem a calibração empírica por camada. A monografia manda ler o resultado como piloto exploratório. O writeup apresenta o cascade como "intervenção testada". Adicionar a mesma ressalva.
5. **Assimetria de severidade entre juízes** ([MONO] §4.8, §5.7): κ colapsa em flags binários quando um juiz registra falha por omissão. O writeup explica κ=0,4722 por "granularidade"; a monografia mostra o mesmo fenômeno na V11 e oferece a regra conjuntiva §7 como remédio.
6. **Salecha et al. 2024** e **Needham et al. 2025** (eval-awareness, AUC 0,83) como contexto para o uso de bateria em modelos de fronteira (o Modo-Examinador) — o writeup já cita Salecha, mas não Needham.
7. **Coorte de controle não-Gemma** (§4.10.1 [MONO]) e o dado de que Olmo/Qwopus "thinking" têm falha de classe distinta (fases vazias) já estão no writeup §3.2; manter e citar a seção §4.10.1.

### 2.3 Itens do writeup sem contraparte na monografia (NÃO LOCALIZADO)

- A ablação fatorial de quantização de 31/10 (`omnimind-gemma-4-quantization-ablation-t4x2`; Stroop 0,0% GGUF → 80,0% FP16) e o "73% de degeneração em BF16 nativo" (Fase 0): **NÃO LOCALIZADO** na monografia. Precisam de proveniência própria (arquivo + SHA) no writeup.
- Fidelidade "fid≡1.0 em 13/15 modelos" (corte MPS saturado): **NÃO LOCALIZADO**. A monografia só afirma χ=4 @ 99,8% para Gemma-3-1B (§3.7).
- Os números do Cognitivo por modelo da §3.2 (WCST 15/5/12/12 etc.), do `diag_battery` (WCST 86,8; Stroop 100,0) e dos valores de refactor battery: **NÃO LOCALIZADO** na monografia (só aparecem os 40/40 e as médias por tarefa em §4.10.6).

---

## 3. Divergências monografia × writeup (eff_rank, degenerate runs, vacilo)

### 3.1 eff_rank

| Ponto | Monografia | Writeup | Estado |
|---|---|---|---|
| Valor 114,6/40,3 | Não reprodutível; fora da síntese (nota pós-§4.10) | No abstract como `eff_rank`; na §3.4b como `IPR_dim` | **Conflito interno do writeup** + conflito com a monografia |
| eff_rank de fato | ≈2,5 para ambos (e^H de Shannon, OW-AUD-018/020) | `eff_rank_K` 2,496/2,516 (§3.4b, coerente) | Concordam; o abstract não |
| Razão "1,7×" | Não discute | Abstract e §3.4b | **[DERIVADO]** 1,68× só normalizado por D; 2,84× bruto; ≈1× no eff_rank_K |
| Fórmula | Monografia chama de "razão de participação de Roy–Vetterli" | §3.4b: entropia `exp(H(σ²/Σσ²))`, Roy & Vetterli | **[INTERPRETAÇÃO]**: Roy & Vetterli (2007) definem o rank efetivo como exp da entropia de Shannon dos valores singulares normalizados — ou seja, não é o participation ratio. A monografia parece usar o nome errado. Conferir o artigo antes de citar |
| Peso da evidência | Marcada como "proxy [PRX]" no writeup; "OW-AUD" na monografia | N=128 sidecars / 5.888 vetores de camada | **[LIMITE]** Fase 0 da monografia exige MPS por camada ao longo de tokens; o que existe aqui são sidecars de último token |

### 3.2 Degenerate runs

| Ponto | Monografia | Writeup | Estado |
|---|---|---|---|
| Diag live L4 | 40/40 sem degeneração; "88 não localizado" | 0/88 (44+44) | **Conflito.** Banco local vazio ([LOCAL]); o CONTINUITY_MAP cita 40/40 |
| E4B esperado como "fluente" | 0,7% (2/297) | 1–4% por rodada | Não reconciliado (C6) |
| 26B-A4B | 26,4% | 19–40% (média 29,0% **[DERIVADO]**) | Não reconciliado |
| 12B-QAT | 14,3% | 9–20% (média 14,4% **[DERIVADO]**) | Concordam |
| 31B | 90,6% | 87–94% (média 91,0% **[DERIVADO]**) | Concordam |
| Controles não-Gemma | ≈≤1,7% | ≤2,7% | Divergem no máximo |
| Fonte do spam | 96,8% Gemma | ~93% | Divergem |
| Chat vs completion | 0/40 × 25/40 (§4.10.3) | Mesmo, mais nota de regime (monitor de stall a ~120 tokens) | Concordam; a monografia **não menciona a limitação de janela** de ~120 tokens e o RNG sem semente que o writeup declara. Adicionar à monografia ou citar o writeup |
| Duplo-juiz J2 | 66,0% recomputado | 67,0% | Writeup errado ([DERIVADO]) |

**Observação adicional [INTERPRETAÇÃO]**: o writeup relata para o 12B "100% (20/20) injulgável" (Juiz A, r1) e "14,3% de spam". São métricas diferentes (insuficiência de evidência julgável contra razão de unicidade). A tabela do writeup as mistura sob "degeneração". Rotular cada métrica.

### 3.3 Vacilo

| Ponto | Monografia | Writeup | Estado |
|---|---|---|---|
| Estatuto | §3.7: salto de χ no vacilo é **predição teórica**, sem resultado empírico. §5.6: dois polos como "disposições de falha", sob N=3 "estritamente exploratório" | §4: "sustenta-se **solidamente** como constructo clínico-operacional … manifestado empiricamente" | **Writeup mais forte que a fonte.** Rebaixar para "construto operacional hipotético, com suporte descritivo em N=3" |
| Operacionalização | Definido só por analogia (fuga para a frente × fuga para a ruminação, §5.6). Nenhuma medida própria | Associado a 74% timeout × 96,8% submissão | NÃO LOCALIZADO um indicador de vacilo medido nos instrumentos |
| Base empírica dos polos | Gluzdov (288 runs): E4B n=31; 12B n=187; 26B sem dados | Idem | O n do E4B (31) é pequeno e a verificação do CSV primário foi só por metadados ([MONO] B.1 vii) |
| Prova de nexo causal | "associação direcional, não validação preditiva" | Abstract: "scores **track** documented failure modes"; Intro: perfis "**predizem**" modos de falha; título: "*Predict* Coding-Agent Failure Modes" | **Conflito de linguagem.** Com N=3 e |r|≈1 trivial, "predict" não se sustenta; o próprio writeup admite isso na Discussão |
| Replay local | — | `docs/results/freud10d_vacilo_replay.json` mostra `n_sidecars: 4` e `"limit": "run_id/turn/task vazios nos sidecars — join com verdicts impossível sem metadata"` (**[LOCAL]**; o commit mais recente indica que o join por metadado passou a funcionar, mas eu não reexecutei) | Não há evidência local de que o replay detecte vacilo; é só séries de tensão/prazer |
| Thresholds | PR<20, χ>48 arbitrários (§3.7) | "detector latente PR<20 … rank~1 basal em todas as condições" (Limitações) | Concordam: o writeup já admite; não usar PR<20 como detector |

---

## 4. Itens da metodologia aplicáveis à próxima bateria do `omni_worker`

Prioridade: **P0** = corrige risco de falsear resultado; **P1** = melhora validade; **P2** = refinamento. Origem entre colchetes.

| Pri | Item | Como aplicar no `omni_worker` | Origem |
|---|---|---|---|
| P0 | **Simetria de informação agente × juiz** (regra do dossiê) | O juiz (Analyst 12B/`ReviewerAgent`, juízes externos) deve receber o mesmo contexto que o executor: task, contratos de arquivo (`todo_api.py`, `todo_stats.py`, `store.py`), traceback. Sem isso o juiz marca como erro o que o executor viu legitimamente | §5.2 espécime 6, §6.1(3) |
| P0 | **Separar falha de infra de desempenho** (`COMPLETED`/`COMPLETED_COM_INCOMPLETUDE`/`PARTIAL`/`VOID` + `infra_failure_type`) | Os HTTP 500/503/507 do peer-swap e os unloads **não** podem contar como falha de modelo nem como degeneração. Flag estruturada por linha, nunca string-matching em campo secundário | §6.1(2), espécime 4, nota de reanálise item 3 |
| P0 | **Truncagem ≠ erro cognitivo** (`TRUNCATED_INCOMPLETE`); preservar `raw_response` integral | `run_diag_battery.py` usa `max_tokens=1800` (CONTINUITY_MAP l. 165). Conferir se o 12B com thinking fecha antes disso; registrar `n_tokens` vs teto por linha | §4.6.3, §6.1(1), espécimes 1 e 3 |
| P0 | **Pontuar acurácia contra gabarito, não formato** | Verificar que os WCST/Stroop/3-back/IGT do diag battery são scorer determinístico por item. **NÃO VERIFICADO por mim.** | §4.6.6A espécime 5, §6.1(4) |
| P0 | **Banco como evidência, não relato** | Antes de qualquer cifra no writeup (40/40, 88, etc.) exigir arquivo + contagem + SHA. O `diag_battery.sqlite` de 0 bytes é o caso concreto | B.1 notas de auditoria, manifestos SHA256 |
| P1 | **Enquadre endurecido (v1.2)** | Os resultados do diag battery (Stroop 97–100%, IGT 100% nos dois cérebros) parecem teto **[INTERPRETAÇÃO]**, como na v1.1. Passar para WCST com tentativa + `INCORRETO` nos shifts, IGT sem rótulo, Stroop sem "Ação requerida", 3-back e Digit Span 9/7 | §3.4.1, §4.6.6C, §5.3 |
| P1 | **Formato, quantização e backend como covariáveis registradas** | Gravar em cada linha: chat-template sim/não, NF4/int8/BF16, build/backend, GPU (L4 contra T4×2), seed. A queda A100→T4 (−3,95 a −5,19) mostra que o chassi desloca a medida. Não misturar L4 e T4×2 sem estratificar | §4.6.5, §5.4, §4.10.3 |
| P1 | **Desenho que evita colinearidade** plataforma×rodada | Rodar a mesma rodada em ≥2 chassis ou balancear a ordem | §5.7(2) |
| P1 | **Juízes duplos cegos, κ com IC95 de Wilson, e regra conjuntiva não compensatória** | Para os gates (`ConstitutionalGate`, tri-state): veredito por falha crítica ∨ dimensão crítica <limiar, não média. Reportar κ **separado** para flag crítico e para o desfecho completo. Preservar divergência como dado | §3.1 Tab. 1 (V11), §3.4.5, §4.8, §6.4 |
| P1 | **Controle de confound com modelos não-Gemma sob o mesmo protocolo** | Incluir ≥1 controle fora da família em cada bateria nova | §4.10.1 |
| P1 | **Evitar o juiz circular** | O `AffectTracer` usa o 12B como juiz de cenários do próprio sistema e a supervisor_battery (16/16) tem cenários autorais **[INTERPRETAÇÃO]**: risco análogo ao espécime 2. Adicionar um juiz externo cego e um gold set humano ou de outra família | §5.2 espécime 2, §6.2 |
| P1 | **Condição de contexto contínuo com sondas canário** | A refactor battery multi-turno e o peer-swap quebram contexto. Testar vazamento/perda (nome, arquivo) numa sessão contínua contra sessões isoladas, como na V2 | §4.9 |
| P1 | **Poder estatístico explícito** | McNemar com N=60 não detecta Δ≈7pp (já citado no writeup). Pré-calcular N antes da bateria; não correlacionar com N=3 | §4.10.4, §6.4 pré-registro |
| P1 | **Fase 0 antes de qualquer threshold de intervenção** | OW-STU-018/019 e o trigger K=30: calibrar empiricamente por camada × passo; não reusar PR<20/χ>48 | §3.7 |
| P2 | **Pré-registro**: protocolo, hipóteses, regras de exclusão e `run_manifest` (versão de prompt, parser, juiz, ambiente) | Aplicar às próximas baterias; versionar estímulos (cf. variáveis Z e N não instanciadas nas Cenas 3–4) | §6.4, B.3 nota |
| P2 | **Sondas comportamentais em vez de autorrelato** | O QUATI/MMPI degeneram por máscara RLHF; manter só provas em ato. Incluir sondas de sycophancy comportamental (capitulação diante de premissa falsa) e detecção de Modo-Examinador | §4.4–§4.5, §6.2 |
| P2 | **V11-D10 como fonte de cenários para o `AffectTracer`** | Reoferta de intervenção recusada (S1-E5/S2-E5) e captura do vínculo (S3-E6) são falhas observadas em modelos comerciais; podem virar casos negativos para a supervisor_battery | §4.8.1, §5.5 |
| P2 | **Rótulos epistêmicos [DADO]/[DERIVADO]/[INTERPRETAÇÃO]/[LIMITE]** em cada cifra e nota de auditoria | Já exigido pelo AGENTS.md; a monografia usa "Nota de Auditoria" por data | AGENTS.md, B.1 |

---

## 5. Limites desta releitura

- Não reverifiquei as cifras da monografia contra seus SQLite (não presentes aqui). Confiei no texto, que declara auditoria em 2026-11-03.
- Citei as conclusões do audit `writeup_claims_audit_hermes.md` onde indicado; os números de `degenerate_flag` dos bancos HF (49/126, 75/200) vêm dele, e não os recontei.
- Verificações locais feitas: `mps_spectral_first.md`, `diag_battery.sqlite` (0 bytes), `CONTINUITY_MAP.md` (40/40), 3 `Cargo.toml` em `vendor/kernel/`, cabeçalho de `freud10d_vacilo_replay.json`.
- Não executei testes, ruff nem alterei `PAPER_WRITEUP.md`.
