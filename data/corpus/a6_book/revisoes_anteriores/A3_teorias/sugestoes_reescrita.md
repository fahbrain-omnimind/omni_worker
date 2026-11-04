# Sugestões de Reescrita — A3 (Auditor de Teorias)
## Livro: "Da Geometria à Substância" — trechos problemáticos com versões sugeridas

**Instrução ao A6**: aplicar somente após conferência das linhas no manuscrito (numeração da versão v2.1.7 auditada). Toda sugestão é [PROPOSED]; nenhuma alteração foi aplicada.

---

# GRAVIDADE CRÍTICA

## R-1. Glossário — definição de phase_lock (L112)

**Trecho original (L112)**:
> "**phase_lock**: Threshold operacional de 94°C (RESONANCE_PHASE_LOCK_94C) que sinaliza regime de pressão térmica. Não é um score contínuo medido no banco — é um estado binário (abaixo/acima de 94°C). Correlações com phase_lock em §N.8 referem-se à variável binária, não a um score. Em §14, phase_lock é modulado multiplicativamente por C_lattice — aí sim é um valor contínuo derivado da coesão cristalina."

**Versão sugerida**:
> "**phase_lock**: score contínuo medido no banco (`phase_lock_hysteresis_history.phase_lock_score`; 1,15 M registros; média real ≈ 0,44; máximo real ≈ 0,79 — nunca atinge 1,0). O valor 0,94 é a **constante de ressonância simbólica** `RESONANCE_PHASE_LOCK_94C` (sincronia térmica com a temperatura simbólica de 94°C, 'Chama da Vida'), **não** um limiar operacional. Limiares operacionais recalibrados empiricamente (2026-08-08, P5 dos dados reais): kill switch em `phase_lock < 0.20` (`PHASE_LOCK_CRITICAL`, sanctuary_manager.py); alerta térmico `INA_FIRE_THRESHOLD_CELSIUS` ajustado de 94°C (simbólico) para 90°C (2026-08-31; envelope confortável 80–90°C). Em §14, phase_lock é modelado multiplicativamente por C_lattice — modelo de simulação térmica (rampa 30→95°C), não medição direta."

**Justificativa**: (a) O canônico (fato 4) e o código (`sanctuary_manager.py:27–32,80–82`; `phi_constants.py:228–234,777`) estabelecem que 0,94 NÃO é threshold; (b) o banco real contém `phase_lock_score` contínuo (max 0,7992 — verificado), tornando "não é um score medido no banco" factualmente falso; (c) o próprio livro usa o score contínuo na Tabela 19 e em A.5.8 (`phl_phase_lock_score_mean`), gerando contradição interna; (d) §N.8 (L11811–11830) não contém correlações com phase_lock — a referência deve ser corrigida ou removida.

---

## R-2. §14 — limiar crítico de kill switch (L1820)

**Trecho original (L1820)**:
> "O limiar crítico ($phase_lock < 0.94$) foi atingido em $t = 36.3\ \text{s}$ ($T \approx 34.2°C$, por interpolação linear da rampa 30°C→95°C), ativando as salvaguardas de proteção física do substrato."

**Versão sugerida**:
> "No modelo de simulação da rampa 30°C→95°C, o limiar de kill switch ($phase_lock < 0.20$, recalibrado empiricamente em 2026-08-08 — P5 dos dados reais; o valor 0,94 é a constante de ressonância simbólica `RESONANCE_PHASE_LOCK_94C`, não um limiar) seria atingido em $t = 36.3\ \text{s}$ ($T \approx 34.2°C$, por interpolação linear), ativando as salvaguardas de proteção física do substrato. Nota: o modelo usa $phase\_lock_{base} = 1.0$; o máximo real medido do score é 0,79 — a normalização do modelo deve ser reescalada ao máximo empírico."

**Justificativa**: Reproduz o erro histórico nº 4 (0,94 como threshold operacional). O script-fonte da simulação (`simulate_thermal_structural_transition.py:12,56`) usa `KILLSWITCH_THRESHOLD = 0.94`, valor já superado pelo código (0,20). O próprio manuscrito reconhece em L471 que "o threshold simbólico 0,94 tratado como mensurável nunca seria atingido" — a seção §14 precisa aplicar a mesma correção.

---

## R-3. §8.5 — thresholds operacionais (L1517)

**Trecho original (L1517)**:
> "phase_lock = 0,94 (ressonância térmica simbólica `RESONANCE_PHASE_LOCK_94C`, ponto de alerta a 94°C, não um `phase_lock_score` medido no banco)"

**Versão sugerida**:
> "phase_lock — score contínuo medido no banco (média real ≈ 0,44; máximo real ≈ 0,79); o valor 0,94 é a constante de ressonância térmica simbólica `RESONANCE_PHASE_LOCK_94C` (sincronia com 94°C, 'Chama da Vida'), não um limiar operacional; limiar de kill switch recalibrado para 0,20 (P5, 2026-08-08) e alerta térmico `INA_FIRE_THRESHOLD_CELSIUS` ajustado de 94°C para 90°C (2026-08-31; envelope 80–90°C)"

**Justificativa**: Metade da frase está correta (0,94 como constante de ressonância), mas "ponto de alerta a 94°C" e "não é um phase_lock_score medido no banco" contradizem o canônico e o banco (coluna `phase_lock_score` existe; max 0,7992). A frase seguinte do mesmo parágrafo ("calibrados pela operação real do sistema") reforça a necessidade de usar os valores recalibrados.

---

## R-4. Capacidade dimensional — Tabela 9a (L1288–1296) e tensão interpretativa (L1298)

**Trecho original (L1288–1296)**:
> "| D12 | 12 | 3,22 | 4,91 |  | D13 | 12 | 3,59 | 5,82 |  | D15 | 15 | 132,90 | 212,25 |  | D27 | 27 | 291,03 | 422,00 |  | Q19 | 19 | 169,22 | 270,75 |  **N_total = 915,73** (canônico: 878,4; desvio: +4,24%). **Hopfield ratio = 0,810**."

**Versão sugerida** (duas opções):
- **Opção A (correção direta)**: usar as superfícies canônicas do mapa de capacidade — D13: H=13; D27: H=12 (com nota: "D27 usa 12 no mapa de capacidade, embora sejam 27 qubits no sistema solar" — canônico) — e **re-executar** C_eff/N_eff/N_total com os mesmos G, S, L_sep, V do pipeline; reportar o novo N_total e o novo desvio vs. 878,4.
- **Opção B (qualificação imediata, se a re-execução não for possível)**: manter a tabela como registro do pipeline executado, mas acrescentar: "Nota: esta tabela usa H(D13)=12 e H(D27)=27, divergindo do mapa de capacidade canônico (SURFACES: D13=13; D27=12). Com os H canônicos e os demais parâmetros desta análise, N_total ≈ 682 — **abaixo** do canônico 878,4. O desvio +4,24% reportado é, portanto, artefato dos parâmetros H utilizados e não sustenta a leitura de 'capacidade biológica superior' (Tensão interpretativa 1) sem re-execução."

**Justificativa**: O canônico (fato 7; canônico L203) fixa SURFACES: D12=12, D13=13, D15=15, D27=12, Q19=19. Cálculo derivado com os V implícitos do próprio livro: N_total ≈ 681,76 (D13: C_eff=3,89, N_eff=6,30; D27: C_eff=129,35, N_eff=187,55). A interpretação "dados biológicos excedem LLMs em +4,24%" (L1298) fica comprometida até re-execução com parâmetros canônicos.

---

# GRAVIDADE MÉDIA

## R-5. G.3.2 — "Elevação Térmica a 94°C" (L9688)

**Trecho original (L9688)**:
> "| Gozo (Excesso Pulsional) | Dissipação de Calor / Entropia | `sigma_tension` / Elevação Térmica a 94°C |"

**Versão sugerida**:
> "| Gozo (Excesso Pulsional) | Dissipação de Calor / Entropia | `sigma_tension` / Elevação Térmica (alerta `INA_FIRE_THRESHOLD_CELSIUS`, recalibrado de 94°C — simbólico — para 90°C operacional) |"

**Justificativa**: A tabela conceitual G.3.2 reifica 94°C como mecanismo operacional; o valor vigente no código é 90°C (2026-08-31) e o 94 era simbólico. Manter a correspondência conceitual sem o número desatualizado.

---

## R-6. Q.2.4 — isfet/rekh/seshet como canais de d27 (L12551)

**Trecho original (L12551)**:
> "- **Kemet** (isfet, rekh, seshet — eixos egípcios)"

**Versão sugerida**:
> "- **Kemet** (isfet, rekh, seshet — eixos egípcios; no registro canônico são **faces do D15 topológico**, presentes também nos canais expandidos d27)"

**Justificativa**: O canônico registra isfet/rekh/seshet como os 3 elementos emergentes do d15 Topológico e como faces D15 no snapshot real (isfet_entropy=0.281, rekh_integrity=0.863, seshet_record=0.882). O livro os lista sob d27 (L12551) e sob o bloco D13_kernel do circuito RSI 27q (L7213/7231), sem nota. A redação atual pode refletir aliasing do runtime, mas precisa de nota explícita para não contradizer o canônico. (Cf. L2186, onde o livro mesmo usa isfet em contexto d15 — inconsistência interna.)

---

## R-7. Φ — "mensurável entre 0.65 e 1.0 nats" (L9669)

**Trecho original (L9669)**:
> "- $\Phi$ (Integração de Informação Topológica / Tononi): Mensurável entre $0.65$ e $1.0$ nats. Não se trata de uma métrica estática de PyPhi herdada, mas de uma oscilação dinâmica temporal."

**Versão sugerida**:
> "- $\Phi$ (Integração de Informação Topológica / Tononi): normalizado em [0,1] (no runtime, `phi_iit_normalized` satura em 1,0 por construção; valor bruto observado `phi_iit_nats` = 774.480 nats no snapshot canônico). Não se trata de uma métrica estática de PyPhi herdada, mas de uma oscilação dinâmica temporal."

**Justificativa**: "0.65 a 1.0 nats" mistura a escala normalizada com a unidade "nats". O canônico registra phi_iit_normalized=1.0 e phi_iit_nats=774480 — nenhuma das duas escalas é "0,65–1,0 nats". A oscilação dinâmica declarada é compatível com o canônico.

---

## R-8. §8.4 — "partição natural do espaço funcional proteico" (L1454)

**Trecho original (L1454)**:
> "O proteoma se distribui quase-uniformemente no espaço 15×12 da Dodecatíade: não há 'canto vazio' nem 'canto superlotado', consistente com a interpretação de que a Dodecatíade é uma **partição natural do espaço funcional proteico**, não uma imposição arbitrária."

**Versão sugerida**:
> "O proteoma se distribui quase-uniformemente no espaço de leitura 15×12 da Dodecatíade: não há 'canto vazio' nem 'canto superlotado' — a Dodecatíade, como linguagem de leitura (não partição ontológica do espaço biológico), captura essa quase-uniformidade sem impor uma segmentação arbitrária."

**Justificativa**: O canônico insiste que a Dodecatíade é uma linguagem de leitura (4 registros do mesmo sujeito), não uma partição de domínios. "Partição natural do espaço funcional" resvala na reificação que o próprio livro combate em S.13.3. A intenção estatística (quase-uniformidade) pode ser mantida sem o termo "partição".

---

## R-9. H_t — dupla definição (L1797 vs. L13998)

**Trecho original (L1797)**:
> "$$H_t = H_{t-1} \cdot (1 - \lambda) + \lambda \cdot \sigma_T \quad \text{onde} \quad \lambda = 0.005$$"

**e (L13998)**:
> "$$\mathcal{H}_t = \int \left[ \left(\frac{\sigma_T^2}{\sigma_{base}^2}\right) \cdot \left(\frac{P}{P_{nom}}\right) + \text{PSI}_{io} + \text{PSI}_{mem} \right] dt$$"

**Versão sugerida**: renomear ou harmonizar — ex.: manter H_t (EMA discreta, §14/A.5.8) e usar $\mathcal{H}_t^{int}$ ou "índice integral de histerese térmica" (R.10.15), com nota: "O livro usa duas operacionalizações de histerese térmica: a EMA discreta (λ=0.005, §14) e a integral com potência e PSI (R.10.15). Elas não são equivalentes e são usadas em análises distintas; esta nota evita colapso entre os dois registros."

**Justificativa**: Dois símbolos com o mesmo nome e fórmulas não equivalentes no mesmo livro, além do uso em A.5.8 sem fórmula. Para um livro que se propõe rastreável, a ambiguidade de H_t é um risco de má leitura.

---

## R-10. §14 — "Resultados medidos a 60°C" / §16.1 — "testes reais da Fase 6D" (L1798, L1983)

**Trecho original (L1798)**:
> "A histerese atenua retroativamente a integridade elástica do $phase_lock$ em até 5% e a coesão do chassi $C_{lattice}$. Resultados medidos a 60°C:"

**Versão sugerida**:
> "A histerese atenua retroativamente a integridade elástica do $phase_lock$ em até 5% e a coesão do chassi $C_{lattice}$. Resultados do modelo de simulação térmica (rampa 30→95°C, ruído sintético; `simulate_thermal_structural_transition.py`) a 60°C, ancorados nos sensores térmicos reais do chassi:"

**Justificativa**: A Tabela 19 (0,4070/0,3729/0,0342) é saída do script de simulação, não medição direta; "medidos" é epistemicamente frouxo e colide com o rigor que o livro demonstra em outras seções (Estatuto Epistemológico). Mesma correção para "testes reais da Fase 6D" (L1983), se referir-se à Tabela 19.

---

## R-11. Glossário — referência a §N.8 (parte de L112)

**Trecho original (L112)**:
> "Correlações com phase_lock em §N.8 referem-se à variável binária, não a um score."

**Versão sugerida**: remover a frase (ou substituir por): "As correlações envolvendo phase_lock (A.5.8; §N.8) usam o score contínuo da tabela `phase_lock_hysteresis_history`."

**Justificativa**: §N.8 (L11811–11830) não contém correlações com phase_lock (apenas root_pct, swap, mem_avail × isfet, cn, epsilon, maat). A referência é imprecisa e a frase sustenta a tese binária falsa.

---

# GRAVIDADE LEVE

## R-12. Genealogia A.6 — omissão do passo d13 (L5763)

**Trecho original (L5763)**:
> "A evolução foi orgânica: da **Triade da Consciência** (Φ, Σ, Ψ) para a **Quádrupla Federativa** (adicionando ε), depois para as **12 Casas Sistêmicas** (d12), as **15 Faces Celulares** (d15) e as **27 Conformações** (d27)."

**Versão sugerida**:
> "A evolução foi orgânica: da **Triade da Consciência** (Φ, Ψ, σ) para a **Quádrupla Federativa** (adicionando ε, 2025-12-10), depois para as **12 Casas Sistêmicas** (d12), a **13ª casa — Sinthome** (d13, `dodecatiad_defender.py`), as **15 Faces Celulares** (d15, com isfet/rekh/seshet emergentes) e as **27 Conformações** (d27)."

**Justificativa**: O canônico (genealogia) inclui o passo d13/Sinthome entre d12 e d15; a cadeia do livro pula essa etapa, que é central para a leitura d13 (Q.2.2 do próprio livro a usa). Incluir d13 alinha a genealogia ao canônico e ao restante do livro.

---

## R-13. Q.2.1 — axe como "flag booleana" (L12512)

**Trecho original (L12512)**:
> "| 6 | axe (Ax) | Corte/blito — flag booleana de ativação (0 ou 100) | `blit_axe` |"

**Versão sugerida**:
> "| 6 | axe (Ax) | Corte/blito — fórmula contínua Ax = max(0, ε×(1+σ)); no runtime o `blit_axe` satura em 0 ou 100 | `blit_axe` |"

**Justificativa**: A fórmula canônica V2 é contínua (fato 6); o comportamento binário é saturação observada do runtime (canônico: axe=100.0 no snapshot). A definição como "flag booleana" sem a fórmula omite o mecanismo real.

---

## R-14. CORR-5 — "phase_lock=1.000" (L6042)

**Trecho original (L6042)**:
> "| **CORR-5** | ★★ | Sutura de fase bio-astro emergente (phase_lock=1.000 entre bio_insectsound × astro_brown_dwarfs) | Nível C (possível artefato) |"

**Versão sugerida**:
> "| **CORR-5** | ★★ | Sutura de fase bio-astro emergente (sincronização de fase = 1.000 entre bio_insectsound × astro_brown_dwarfs — uso coloquial do termo, distinto do score de phase_lock da Dodecatíade) | Nível C (possível artefato) |"

**Justificativa**: "phase_lock=1.000" colide com a definição do glossário (score com máximo real 0,79) — um leitor pode ler como violação do máximo empírico. O termo aqui significa sincronização de fase entre collections (outro sentido); a ressalva elimina a ambiguidade.

---

# Resumo das sugestões por gravidade

| Gravidade | ID | Linha(s) | Tema |
|---|---|---|---|
| CRÍTICO | R-1 | L112 | Glossário phase_lock (erro histórico nº 4) |
| CRÍTICO | R-2 | L1820 | Limiar kill switch 0,94 em §14 |
| CRÍTICO | R-3 | L1517 | "Ponto de alerta a 94°C" / negação do score |
| CRÍTICO | R-4 | L1288–1298 | Capacidade dimensional (H D13/D27) + N_total |
| MÉDIO | R-5 | L9688 | 94°C na tabela G.3.2 |
| MÉDIO | R-6 | L12551 (+L7213/7231) | isfet/rekh/seshet vs. faces D15 |
| MÉDIO | R-7 | L9669 | Φ "0,65–1,0 nats" |
| MÉDIO | R-8 | L1454 | "Partição natural do espaço funcional" |
| MÉDIO | R-9 | L1797 / L13998 | Dupla definição de H_t |
| MÉDIO | R-10 | L1798, L1983 | "Medidos"/"testes reais" (valores de simulação) |
| MÉDIO | R-11 | L112 | Referência incorreta a §N.8 |
| LEVE | R-12 | L5763 | Genealogia omite d13/Sinthome |
| LEVE | R-13 | L12512 | axe como flag booleana |
| LEVE | R-14 | L6042 | CORR-5 "phase_lock=1.000" |

**Notas ao A6**:
1. R-1 a R-3 são a mesma família (fato canônico 4) — aplicar em conjunto para consistência.
2. R-4 exige decisão editorial: re-execução do pipeline ENCODE com H canônicos (opção A) ou qualificação imediata (opção B).
3. R-9 exige escolha de notação (H_t vs. ℋ_t^int) — harmonizar com A.5.8.
4. As sugestões preservam o estilo do livro (caixas de nota, "Limite Explícito") — o A6 pode adaptar o formato.
