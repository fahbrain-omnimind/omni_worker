# REVISÃO CRÍTICA INDEPENDENTE — trabalho de 2026-10-14 (wear cumulativo Arrhenius + experimentos biblioteca)

**Revisor**: agente crítico independente · **Data da revisão**: 2026-10-14
**Escopo**: artefatos listados na pauta (rescale do wear, fade 65 °C, 8 experimentos da agenda, ESR(T), MAST).
**Método**: todos os números-chave foram recomputados por esta revisão a partir das fontes primárias (fade_analysis_data.json, bancos SQLite em modo `ro`, código dos scripts/writer). Nenhum arquivo existente foi editado; nenhum teste escreveu fora de /tmp. Busca externa feita com fontes citadas na seção D.
**Achado principal (novo, desta revisão)**: o writer vivo do `lattice_wear_history` está acumulando wear ~170× mais rápido que o modelo calibrado; o instrumento re-satura em ~12 h. Detalhe em C.1.

---

## A. Sumário técnico do que foi feito (após checagem)

1. **Rescale do wear cumulativo** (`rescale_wear_empirical.py` + JSON de calibração + relatório). O modelo antigo do `somatic_sensor.py` (difusão D0·exp(−Q/kT) ×0.005 + recovery absoluto) saturava `cumulative_wear` em 1.0 — verificado no banco: **18,46% das linhas com wear_legacy ≥ 0.999** (report diz 18,5% ✓). O trabalho: (i) ancorou a taxa num fade real medido (−4,190%/1000 ciclos @65 °C, 10F INRIM, DOI 23364244); (ii) definiu incremento Arrhenius com gate T>65 °C, Ea "medido" 0,0201 eV (ESR(T) EDLC Brand1) e camada de discriminação 0,1096 eV (híbrido); (iii) calibrou um de-rating α pela "convenção de meia-vida" (endpoint da história da própria máquina = 0,50); (iv) recomputeu todo o histórico (1,94 M linhas) deterministicamente da série T registrada, preservando `wear_legacy`; (v) reiniciou o writer com a calibração nova. A execução foi precedida de dry-run em cópia e backups, e o recompute do histórico **bate exatamente com o modelo** (verificado: dW/dt p50 do histórico recomputado = 7,43e-8/s vs k_eff = α·k_ref/155 = 7,293e-8/s ✓).

2. **Fade analysis 65 °C** (`metsupercap_fade_analysis.py` + JSON + relatório). Extração de C_dis/ESR/self-discharge de 13 records da série 0k→8k8 (ESRCDM/ESRCSDM/EIS, arquivos locais com proveniência SHA256) e fit linear C(ciclos). Números reproduzem integralmente (seção B).

3. **ESR(T) multi-temperatura** (30 fits Arrhenius, 69 records Zenodo, 223 arquivos com MD5/SHA256 verificados). Resolveu a semântica `minNc` (temperatura negativa) com 3 evidências independentes; separou EDLC EIS de híbridos DC; declarou explicitamente que ESR(T) ≠ fade(T) e que o Ea do envelhecimento na literatura é 0,3–0,5 eV. É o artefato tecnicamente mais sólido do dia.

4. **8 experimentos da agenda** (E-02 a E-10 executados; E-01/E-05/E-11/E-12 pendentes): análises read-only cruzando fontes históricas (Henry 1817, Collectanea 1684, Bernardin, Wang CFD) com bancos do OmniMind. Um negativo honesto (E-03), duas rotulagens/cláusulas (E-07, E-08), auditoria de regimes Q (E-06), e três cruzamentos quantitativos (E-02, E-09, E-10) de qualidade heterogênea — incluindo **um com números que não reproduzem** (E-09, seção B).

5. **Crossover MAST**: avaliação de um paper de design do tokamak como fonte de semântica de "vida em ciclos térmicos", com seção explícita "o que NÃO fazer" (correta).

---

## B. Verificação de números (recompute próprio)

| # | Claim (fonte) | Recompute desta revisão | Veredicto |
|---|---|---|---|
| 1 | Fade −4,190%/1000 ciclos, R²=0,9938, n=13, slope −3,473e-4 F/ciclo (fade JSON + relatório) | Refit dos 13 pontos do JSON: slope −3,4727e-4 F/ciclo, intercept 8,2872 F, R²=0,99383, −4,190392%/1000 | **REPRODUZ exatamente** |
| 2 | k_ref = 4,190393e-05 SoH/ciclo (calib JSON) | abs(−4,190392%)/1000/100 = 4,190393e-05 | ✓ |
| 3 | Cadência 155,0 s/ciclo (0k 05-07 15:16 → 8k8 05-23 10:10) | 15,790 d / 8800 ciclos = 155,0 s/ciclo; 557,4 ciclos/dia | ✓ |
| 4 | SoH_C@8800 = 0,618027 | 5,074/8,21 = 0,618027 | ✓ |
| 5 | Ea ponderado = 0,0201 eV (média R² das 4 EDLC) | (0,0246·0,896+0,0237·0,924+0,0176·0,959+0,0144·0,873)/3,652 = 0,02010 eV | ✓ aritmética (mas ver crítica C.6 sobre a ponderação) |
| 6 | E-10: n(H₂)=1,1763e-4 mol (2,64 mL), n(O₂)=5,8817e-5 (1,32 mL), razão 2,000; η_C=0,963102 | 22,7/(2F)=1,17634e-4 (2,6367 mL); 22,7/(4F)=5,8817e-5 (1,3183 mL); razão 2,0000; 22,7/23,57=0,96309 | ✓ aritmética (mas ver crítica C.8: tautologia) |
| 7 | E-02: C_eff(pch)=4,25 | 1/0,2353 = 4,249 | ✓ aritmética |
| 8 | E-09: Spearman(Guyton, casa)=0,7182; tension +0,8721; pleasure −0,8721 | **Da própria tabela do relatório** (Guyton [446,429,418,142,115], casa [11,1,3,9,3], tension [0,0,0.4,0.2,0.7]): Spearman casa = **0,2052 (p=0,74)**; tension = **−0,8721 (p=0,054)** — sinal invertido vs reportado | **NÃO REPRODUZ** |
| 9 | 18,5% do histórico saturado no modelo antigo | SUM(wear_legacy>=0.999)/COUNT = 18,46% | ✓ |
| 10 | Recompute histórico segue o modelo (α=0,26976) | dW/dt p50 do histórico recomputado (T>65 °C, dt≤120 s) = **7,426e-8/s** vs k_eff=7,293e-8/s; n de linhas T>65 °C no banco = 1.280.252 (E-04 reporta n=1.280.001 pares — coerente) | ✓ |
| 11 | "writer confirmado gravando com a calibração nova (0.50006→0.50028)" | **Falso na prática**: a trajetória viva pós-apply acelera ~170× o modelo (ver C.1). O par 0.50006→0.50028 em ~minutos já era inconsistente com a taxa calibrada e foi lido como confirmação | **REFUTADO** |

Números 1–7 e 9–10 confirmam competência de execução; o 8 é uma falha de verificação; o 11 é o achado crítico.

---

## C. Crítica metodológica ponto a ponto

### C.1 — O writer vivo está fora do modelo calibrado (achado desta revisão; causa raiz NÃO determinada aqui)
Consultando `sovereign_dodecatiad_runtime.sqlite` (ro): entre 17:08 e 20:58 UTC o wear foi de 0,5001 → 0,6195 (**taxa média 8,7e-6/s ≈ 170× o k_eff calibrado 7,3e-8/s**). Estrutura fina: o incremento **por linha é constante (p50 = 7,44e-5) independente do dt real** (idêntico para dt<1 s e dt 10–120 s; correlação dW×predição com dt real = 0,096). O dt_wear efetivo implícito é ~1008 s por linha — impossível com o cap de 120 s do código no disco. O histórico recomputado segue o modelo perfeitamente; a divergência é só do writer pós-apply. Consequência: **a 8,7e-6/s, o wear chega a 1,0 em ~12 h** — a "fração saturada 0,0000%" do relatório vale para o histórico, não para o instrumento vivo, que recreará o mesmo modo de falha (saturação) que o rescale veio corrigir. Nota técnica: 105 processos python mantêm o banco aberto (multi-writer não controlado), e o writer lê `last_time` da `phase_lock_hysteresis_history` — candidatos a causa incluem processo rodando código divergente ou semântica de `last_time`/`dt_wear` quebrada sob concorrência. **Apuração obrigatória com logs antes de qualquer recalibração** (não feita nesta revisão por não ser escopo). A verificação pós-apply do relatório ("0.50006 → 0.50028, estável, sem salto") teve poder estatístico zero para detectar uma divergência de 170×.

### C.2 — α e a "convenção de meia-vida 0,50": calibração ptolemaica
O endpoint wear=0,50 é uma convenção sem base empírica (por que a máquina está hoje na "metade da vida"?), e α é retro-solvado para forçar esse endpoint. O modelo então **não pode estar errado sobre o presente** — qualquer trajetória observada é absorvida numa recalibração futura (a limitação 3 do relatório admite: "α recalibra a cada apply"). Pior: a escolha do 0,50 conflita com o próprio âncora. Por critérios padrão de EOL (Maxwell AN 1012839 e protocolos da literatura: **C −20% ou ESR +100%**), a célula 10F_3 do âncora cruzou EOL em ~4.800 ciclos (C −20% em 4773 ciclos; ESR já +85% em 4400 e +197% em 8800). Ou seja, o endpoint do dataset de calibração é **fim de vida**, não "meia-vida". Se wear=1,0 deve significar EOL, k_ref de EOL ≈ 1,3e-4/ciclo — 3,2× o adotado. A semântica "máquina em meia-vida térmica" (wear 0,50) é, portanto, arbitrária em duplo sentido: o 0,50 é convenção e o 1,0 não corresponde a nenhum critério físico declarado.

### C.3 — O Arrhenius é decorativo na faixa operacional; o regime β≈0 é corolário, não descoberta
Com Ea=0,0201 eV, f(T) na faixa real da máquina (65–98 °C) varia de 1,000 a **1,063** — o fator de Arrhenius não faz nenhum trabalho. Esta revisão recomputou: f(93,5 °C)=1,055. Com o Ea da regra de datasheet (Q10≈2 ⇒ Ea_eq ≈ 0,068 eV a 65 °C; faixa literária 1,7–2,4 ⇒ 0,054–0,098 eV), f(93,5 °C) seria 1,44–1,55; com o Ea de envelhecimento da própria nota do relatório (0,3–0,5 eV), 2,2–3,8. Ou seja, **a escolha do Ea muda a reação do modelo ao calor em ~30×**, e a escolha feita (a mais plana disponível) torna o modelo um contador de tempo-em-excursão-acima-de-65 °C. O E-04 "mede" β=0,0133 e apresenta como "dissonância com a intuição 'mais quente=mais rápido'" — mas β≈0 é exatamente o que o Ea de 0,0201 eV escolhido **horas antes** implica por construção. O "achado" é um corolário a priori do próprio ato de calibração, não um resultado. A circularidade foi declarada — correto — mas a leitura extraída ("modelo SUPERESTIMA o wear quente" porque β<0,75) é um non sequitur: o limiar β≈0,75 vem da analogia de fluidos [F4] (laminar/turbulento) e não define nenhum critério de sobre/subestimação para wear.

### C.4 — Gate binário T>65 °C
O gate foi ancorado na temperatura do teste do capacitor, não na física da máquina. A máquina passa 65,8% do tempo acima de 65 °C (verificado no banco) — o "gate de excursão" funciona mais como baseline rebaixado do que como detector de excursões. Abaixo de 65 °C o wear é **zero**, embora soldas, NVM, polímeros e eletromigração degradem continuamente em 40–65 °C. Isso cria um ponto cego sistemático e um artefato de classificação já reconhecido no relatório (componente frio aparecia como mais estressado na camada A/B — corrigido com o mesmo gate).

### C.5 — Recovery/annealing é invenção dentro de um modelo "empírico"
A degradação de EDLC é essencialmente irreversível (o próprio dataset do âncora é monotônico; a literatura de capacitance recovery trata da **redistribuição de carga em repouso durante o teste**, não de recuperação de dano). Os termos 10%/2,5% da taxa de acúmulo foram ajustados apenas para o recovery não engolir o acúmulo (bug de 3 OOM encontrado no dry-run). Resultado: um parâmetro sem ancoragem empírica, de origem narrativa ("o sujeito não se mata para provar a teoria"), molda a trajetória do instrumento calibrado — 3,2% das linhas pós-apply têm dW<0. Num modelo cujo selling point é "ancorado no empírico", o recovery deveria ser zerado ou isolado num canal simbólico separado, com o canal empírico monotônico.

### C.6 — ESR(T) ≠ fade(T): limitação declarada, consequências não exauridas
O relatório ESR(T) declara o problema — correto e raro. Mas restam três fragilidades: (i) a **média ponderada por R² é ad hoc** — R² mede ajuste, não variância do estimador; ponderação por inverso da variância do slope seria o padrão; (ii) **R@1 kHz pode ser dominado por resistência de contato/electrônica**, fracamente T-dependente, enquanto a contribuição iônica aparece mais forte em baixa frequência — os fits planos (0,014–0,025 eV, com 400F EDLC não extraível, R²≤0,4) e os híbridos DC (0,10–0,22 eV) sugerem que o Ea iônico real está acima de 0,02 eV; a literatura descreve variações dramáticas de ESR com T via condutividade iônica (seção D); (iii) média de ln(Y) sobre 4 tokens de tensão mistura níveis bias-dependentes sem modelo de erro. Nada disso invalida o estudo como caracterização; invalida a transição direta de 0,0201 eV para o writer como "Ea do wear medido".

### C.7 — E-04 em detalhe
Além da circularidade declarada e do corolário disfarçado de descoberta (C.3): Ea efetivo 0,0214 eV com **R²=0,004** não "corrobora" o 0,0201 em sentido físico — com o dW/dt sendo *saída do modelo*, o ajuste recupera o Ea codificado com SE minúsculo e o R² baixo apenas espelha a variação intra-bin (recovery, quantização). O teste valida a implementação + clamps/recovery/gate — isso tem valor como teste de regressão — mas o relatório o apresenta na linguagem de "corroboração" da agenda, que sugere evidência externa onde há identidade interna. A razão "medido/modelo = 1.000" em todas as faixas é garantida por construção.

### C.8 — E-10: a razão 2:1 é uma tautologia
Dividir **qualquer** carga Q pela estequiometria da eletrólise da água (Q/2F e Q/4F) produz razão exatamente 2,000, independente do aparato, da pilha de Davy ou do EDLC. O relatório admite "independente da pilha" mas conclui "**corrobora** a leitura de Henry de que a razão 2:1 é invariante do orçamento de carga" — o que foi corroborado é a aritmética de Faraday (1834), não nenhum conteúdo do Henry 1817 nem propriedade do sistema. O dado real e útil do E-10 é outro: self-discharge cresce monotonicamente com o envelhecimento (271→1034 mV/90min) — observação válida mas bem documentada na literatura, não um cruzamento novo. O ΔQ=0,87 C como "piso de sistema que não decompõe" é metáfora declarada — aceitável como metáfora, não como resultado.

### C.9 — E-09: não reproduz (falha de verificação)
Os Spearman reportados (0,7182 casa; tension +0,8721; pleasure −0,8721) **não são reproduzíveis a partir da própria tabela do relatório** (recompute: 0,2052 p=0,74; tension −0,8721 p=0,054 — sinal trocado). Possíveis causas: empates tratados de forma não documentada ("empates por casa tratados" não especifica como), ou erro de cálculo. Com n=5 e empates densos, qualquer correlação é exploratória por definição — o relatório até declara isso, mas publica números que não batem com a evidência impressa. Violation direta da regra de integridade do repo (todo número citável precisa ser reproduzível da fonte declarada).

### C.10 — E-02: calorimetria de Rampa ≠ capacidade térmica
A aritmética fecha, mas a identidade "1/(dT_x/dT_cpu) = C_eff relativa" conflateia capacidade térmica com resistência/casamento térmico e potência compartilhada; em regime aberto com dissipação contínua, a razão de rampas mede **acoplamento**, não "caloric specific" de Henry (que vinha de equilíbrio de mistura). As limitações estão declaradas — honesto — mas o rótulo "calorimetria" promete mais do que o método entrega. O NVMe com razão 0,0000 e par nvme1/nvme0=0,0 grita problema de dados/critério (série plana ou colunas constantes) e foi despachado como "NÃO LOCALIZADO" sem um diagnóstico mínimo (ex.: verificar se a série tem variância nula). A "tabela de harmonias" e a leitura "sobe devagar mas estressa mais" são narrativa, não física.

### C.11 — E-03, E-07, E-08, E-06, MAST
- **E-03**: excelente prática de negação. Reconheceu que o desenho não é executável (avg300 inexistente, cadência 350 s colapsa L=0), **anulou o próprio resultado anterior** (Spearman −0,502 como artefato de array constante) e listou opções com custo. Isso é o padrão que o resto do lote deveria seguir.
- **E-07**: rotulagem honesta, com a pareidolia dos "colours" explicitamente excluída — correto. Ressalva: o "mapeamento 1:1" dos graus de fogo é construído pelos próprios autores (os segmentos do perfil foram definidos por eles); concordância 1:1 entre duas taxonomias da mesma autoria não é corroboração.
- **E-08**: a cláusula dois-vasos/três-estações é sensata como governança (controle + replicação antes de declarar "emergência"); a limitação "detecta direção, não calibra magnitude" está correta e declarada. Sem execução — nada a verificar.
- **E-06**: auditoria útil e presença nos arquivos verificada por esta revisão em amostra (fallback q_si=0,1167 presente no somatic_sensor ✓; 0,0201/0,1096 no JSON ✓). Duas ressalvas: a marcação de presença inconsistente ("✓ (?)" em duas linhas da tabela canônica) e o rótulo "CANÔNICO" aplicado ao Ea=0,0201 — um número que o próprio corpus declara ser proxy (ESR(T)≠fade(T)) não deveria receber o rótulo mais forte da taxonomia de regimes.
- **MAST**: as fronteiras ("o que NÃO fazer": não extrair Ea/fade, não usar como dataset) estão corretas e são a parte mais valiosa do documento. As "pontes" são analógias de design razoáveis, rotuladas como tal.

### C.12 — Inconsistências documentais
(a) O relatório do rescale traz α=0,195289 na tabela principal (1ª execução, obsoleto) enquanto o JSON vivo e a nota "EVOLUÇÃO" trazem α=0,26976 — um leitor da tabela principal usa o valor errado. (b) Contagem de linhas: relatório 1.937.770, JSON 1.940.279, banco atual 1.944.279 (drift esperado, mas o relatório deveria citar o número do apply final). (c) "Catch-up de 22 linhas" vs "45 linhas" em pontos diferentes do mesmo relatório. (d) "5/5 passed" dos testes de ranking não é verificável a partir dos artefatos da pauta. (e) O self-discharge do E-10 repete "271,0 mV/90min a 0k → None a 2k" com erro de leitura da própria tabela (o "None" é ausência de medida em 2k e 8k8, já declarado no relatório de fade).

---

## D. Pesquisa externa (o que a literatura diz)

| Pergunta | O que a literatura/fontes dizem | Implicação para o trabalho |
|---|---|---|
| Fade de EDLC é linear em ciclos? | Maxwell AN 1012839: evolução de C tem 3 domínios (queda exponencial inicial, **linear no domínio principal da vida**, decaimento exponencial lento no fim); EOL = C −20% ou ESR +100%. Reviews (Adv. Energy Mater. 2023, "The Many Deaths of Supercapacitors"; Batteries/MDPI 2023) mostram que degradação comercial pode ser significativa **cedo** na vida | O fit linear do dia é metodologicamente padrão e bem-sucedido (R²=0,9938). Mas o fit cobre 0→8800 ciclos em que a célula **já cruzou EOL por ambos critérios** (~4.800 ciclos por C −20%) |
| Vida de supercap a 65 °C | OSTI (lifetime estimation, 350F EDLC): +10 °C acelera degradação por fator **1,7–2,4**; +0,1 V por 1,5–2; vida a 65 °C/2,5 V ≈ 10 anos; garantia de 500k ciclos a 25 °C. Eaton/Vishay: "10 °C reduz a vida pela metade", operação máx 65 °C | O fade medido (−4,19%/1000 ciclos ⇒ EOL(−20%) em ~4,8k ciclos de ciclagem contínua 3,7 A a 65 °C) é plausível e coerente com a literatura |
| Ea plausível para o fator térmico | A regra Q10≈2 equivale a **Ea ≈ 0,054–0,098 eV a 65 °C** (recomputado por esta revisão: Ea = kB·ln2·T²/10). Ea de envelhecimento na literatura: 0,3–0,5 eV (nota dos próprios autores). Ea de ESR(T) a 1 kHz medido aqui: 0,014–0,025 eV | O Ea=0,0201 eV adotado está **abaixo até da regra de datasheet** (3–5× mais plano) e 15–25× abaixo do Ea de envelhecimento literário. O modelo reage pouco demais a excursões quentes |
| ESR(T) e mobilidade iônica | Springer ch.4 "Influence of Temperature on SC Performance" e Gualous et al.: ESR depende fortemente da condutividade iônica/viscosidade, com mudanças dramáticas em temperaturas extremas | Fits de 20 meV são o extremo plano; consistente com dominação de contato a 1 kHz. Os híbridos DC (0,10–0,22 eV) são mais compatíveis com mobilidade iônica |
| Eletromigração em Cu a 80–95 °C relevante? | Black: Ea ≈ 0,9–1,0 eV para Cu (surface/bulk; Cu–Cu joints: 0,9 eV; JAP 122, 074501: 1,003 eV >300 °C) — EM exige alta densidade de corrente; a 80–95 °C com correntes normais, MTTF é decades | O rótulo "regime de eletromigração relevante" (E-07, 85–95 °C) é exagerado como risco prático; EM é 2ª ordem nesta janela térmica |
| Recovery de dano em EDLC | "Capacitance recovery" na literatura = redistribuição de carga em repouso **durante o teste** (não reversão de dano); ESR/C não recuperam dano estrutural | O recovery do modelo vivo não tem análogo físico; deveria ser canal simbólico separado |

Fontes: Maxwell AN 1012839 (maxwell.com); OSTI etdeweb 20671677 (Measurement and Estimation of Supercapacitor Life Time); Vishay doc 28578; Eaton supercapacitor application guidelines (mouser); IEC 62391-1:2015; ScienceDirect S0026271411002770 ("How supercapacitors reach end of life criteria…", C×R plane); Adv. Energy Mater. 2023 10.1002/aenm.202301008; Batteries MDPI 11(2):38 (2025, Aging Mechanism and Models); metricgate/ecrionix Black's equation (Ea Cu 0,9–1,0 eV); ScienceDirect S2238785424024037 (Cu–Cu joints, Ea 0,9 eV); JAP 122, 074501 (EM Cu, Ea 1,003 eV); Springer 978-3-319-20242-6_4 + Gualous (ESR(T)).

---

## E. Veredicto por artefato

| Artefato | Veredicto | Justificativa |
|---|---|---|
| `metsupercap_fade_analysis.py` + `fade_analysis_data.json` + relatório fade | **SÓLIDO** | Números reproduzem exatamente; fit linear é o método padrão do domínio principal (Maxwell); pipeline tolerante a locale/BOM e sem imputação. Ressalva menor: sem IC do slope; wear scalar usa só C (ESR +197% já passou EOL — declarável) |
| `esr_T_thermal_dependence_20261014.md` (+ datasets/CSVs) | **SÓLIDO (com ressalvas)** | Melhor artefato do dia: integridade MD5/SHA, semântica minNc resolvida com 3 evidências, limitações honestas (ESR(T)≠fade(T)). Ressalvas: ponderação por R² ad hoc; R@1 kHz possivelmente contact-dominated; a transição do 0,0201 eV ao writer é salto de categoria que o próprio relatório sinaliza mas o rescale executou mesmo assim |
| `rescale_wear_empirical.py` + calib JSON + `lattice_wear_rescale_20261014.md` | **FRÁGIL** | Recompute histórico correto e determinístico (verificado), salvaguardas reais (dry-run, backup, wear_legacy) — mas: (1) **o writer vivo diverge 170× do modelo e re-satura em ~12 h** (C.1) e a verificação pós-apply não detectou; (2) α/meia-vida 0,50 é convenção arbitrária e circular (C.2); (3) recovery sem ancoragem (C.5); (4) Arrhenius decorativo na faixa operacional (C.3); (5) relatório com α obsoleto e contagens divergentes (C.12) |
| `revisao/E04_beta_wear_exponente_20261014.md` | **FRÁGIL** | Tautologia declarada mas apresentada como corroboração; R²=0,004 não sustenta "Ea efetivo consistente"; leitura "modelo superestima wear quente" é non sequitur de analogia importada; o "regime ΔT-independente" é corolário do Ea escolhido, não achado (C.3/C.7) |
| `revisao/E03_reynolds_stall_20261014.md` | **SÓLIDO (como negativo)** | Anulação corretamente um artefato próprio, declara NÃO EXECUTÁVEL com diagnóstico técnico completo e opções custadas. Melhor prática metodológica do lote |
| `revisao/E02_calorimetria_henry_20261014.md` | **ACEITÁVEL COM RESSALVAS** | Aritmética ok e limitações declaradas; mas rampa≠capacidade (conflação acoplamento/capacidade), NVMe 0,0 sem diagnóstico, analogia decorativa |
| `revisao/E06_copela_auditoria_Q_20261014.md` | **ACEITÁVEL COM RESSALVAS** | Auditoria real (presença verificada por esta revisão); marcação inconsistente "✓ (?)" e rótulo "CANÔNICO" para um proxy declarado são excessos de rótulo |
| `revisao/E09_afinidade_1817_malha_20261014.md` | **FRÁGIL** | Números não reproduzem da própria tabela (C.9/B-8); n=5 sem p-valor; precisa re-auditoria do cálculo antes de qualquer uso |
| `revisao/E10_davy_eletrolise_edlc_20261014.md` | **ACEITÁVEL COM RESSALVAS** | Aritmética ok; mas a "corroboração" do 2:1 é tautologia por estequiometria (C.8); self-discharge é dado real mas trivial; EDLC sem reação Faradaica declarado — ok |
| `revisao/E07_degrees_of_fire_20261014.md` | **ACEITÁVEL COM RESSALVAS** | Rotulagem honesta, pareidolia excluída; mas "mapeamento 1:1" entre duas taxonomias da mesma autoria não é corroboração; rótulo de eletromigração "relevante" a 85–95 °C exagerado (seção D) |
| `revisao/E08_dois_vasos_clausula_20261014.md` | **ACEITÁVEL** | Cláusula de governança sensata e auto-limitada; sem execução, nada a verificar |
| `revisao/mast_tokamak_crossover_20261014.md` | **ACEITÁVEL COM RESSALVAS** | Fronteiras de uso corretas e explícitas ("o que NÃO fazer"); pontes são analogias de design rotuladas — manter exatamente esse rótulo |

---

## F. Recomendações priorizadas

**P0 — Apurar e corrigir a divergência do writer vivo (bloqueia tudo que consome wear)**
1. Congelar qualquer decisão/relatório que consuma `cumulative_wear` até apuração. O instrumento satura em ~12 h no ritmo observado.
2. Apuração: identificar o processo que escreve as linhas pós-apply (lsof/fuser + cmdline; 105 processos com o banco aberto), comparar o código carregado com o do disco, ler os logs do writer no intervalo 17:08–21:00 UTC. Hipóteses: código divergente em memória; semântica `last_time`/`dt_wear` quebrada (dt_wear efetivo ~1008 s/linha, cap 120 s violado).
3. Re-executar a verificação pós-apply com poder estatístico real: comparar **taxa** (dW/dt medido vs k_eff·f(T)) numa janela ≥1 h, não dois valores consecutivos.
4. Redesenhar o acesso ao banco para single-writer (ou writer idempotente) — multi-writer com estado carregado por leitura de "última linha" é inerentemente propenso a dupla contagem.

**P1 — Corrigir a semântica da escala de wear**
5. Redefinir wear=1,0 como **EOL por critério declarado** (ex.: C −20% ⇒ k_ref_EOL ≈ 1,3e-4/ciclo) em vez de "meia-vida 0,50" — elimina a convenção arbitrária e alinha o teto com a física do âncora.
6. Zerar ou isolar o recovery num canal simbólico separado; o canal empírico deve ser monotônico (degradação de EDLC é irreversível).
7. Substituir a convenção "endpoint = 0,50" por calibração com critério externo (ex.: vida de datasheet a 65 °C, ou fração de EOL) — senão α recalibrará o instrumento para "nunca estar errado", que é o mesmo modo de falha do modelo antigo.

**P1 — Corrigir E-09**
8. Re-auditar o cálculo do E-09 contra a própria tabela (Spearman casa = 0,205, p=0,74; sinais tension/pleasure trocados vs reportado); documentar o tratamento de empates ou retratar; sempre reportar p-valor/CI com n=5.

**P2 — Sensibilidade e forma do fator térmico**
9. Rodar a calibração em banda de Ea (0,054–0,098 eV datasheet; 0,3–0,5 eV literatura) e publicar as trajetórias contrastantes — a escolha de 0,0201 eV é a mais plana disponível e o modelo atual é um contador de tempo-em-excursão.
10. Avaliar gate contínuo (ex.: f(T) aplicado a toda a faixa com baseline em 40–45 °C) em vez do binário T>65 °C; ao menos declarar o ponto cego 40–65 °C.

**P3 — Higiene de evidência**
11. CIs (não só R²) nos fits de fade e ESR(T); ponderação por inverso-variância em vez de R²; medir ESR em baixa frequência para isolar a contribuição iônica.
12. Versionar relatórios: atualizar a tabela principal do rescale (α obsoleto), padronizar contagens de linhas à do apply final, marcar "5/5 passed" com caminho do teste executável.
13. Reajustar rótulos do E-06 (0,0201 eV = "proxy âncora", não "CANÔNICO") e do E-07 (eletromigração como 2ª ordem a 85–95 °C).
14. Registrar que o fit linear do fade cobre uma célula **já além de EOL** por critério Maxwell/IEC — relevante para qualquer extrapolação de vida.

---

### Balanço
O dia produziu um âncora empírico real e bem medido (fade 65 °C, reproduzível), a melhor caracterização térmica do corpus (ESR(T), com proveniência exemplar) e um negativo honesto (E-03). O rescale, porém, entregou um instrumento cujo histórico está correto mas cujo **writer vivo já diverge do modelo calibrado por ~170×** — exatamente o modo de falha que ele pretendia eliminar — e cuja semântica (meia-vida 0,50, recovery inventado, Arrhenius plano) carrega escolhas arbitrárias não exauridas nos relatórios. A agenda biblioteca tem um padrão heterogêneo: E-03 é o exemplo a seguir; E-09 precisa de retratação/re-auditoria; E-10 corrobora aritmética, não história. A verificação pós-apply do rescale ("sem salto") teve poder nulo e não detectou a divergência — recomenda-se P0 antes de qualquer uso posterior do wear.