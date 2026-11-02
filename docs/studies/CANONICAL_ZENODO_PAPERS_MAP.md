<!-- doc_id: OW-STU-005 | title: Canonical Zenodo Papers Map — MPS Bridge + Teoria Psico-Afetiva → omni_worker | author: kilo (nvidia/nemotron-3.5-lightning:free) | requester: artifice-operator | project: omni-agent-coworker (kaggle) | date: 2026-11-03 | status: active -->

# Relatório Técnico Curto: Análise de Papers Canônicos

pt-BR: Mapa estrutural dos dois papers do pack `dodecatiad_v3_publication`
(DOIs Zenodo) produzido por CLI delegado (kilo), revisado e integrado por
Devin — a saída do CLI não gravou o arquivo-alvo; conteúdo extraído do log
de execução e verificado contra os papers-fonte.
English: Structural map of the two canonical Zenodo papers, produced by the
delegated kilo CLI; output salvaged from the execution log after the CLI
failed to write the target file.

**Paper 1: MPS Bridge e Topologia do Estado Oculto** (`mps_bridge_article_v2_3_2.md:1-53`)
- **Seções-chave**: §1 Resumo, §2 Introdução (duas camadas: OmniMind 104D vs LLM manifestação), §2.3 MPS formalismo (χ=4 bond dimension), §2.4 Por que analisar estado oculto, §2.5 Escopo/metodologia
- **Tese central**: Arquitetura psi produz estrutura observável e predições falseáveis. MPS Bridge demonstra que estado oculto de transformers satura em χ=4 (fidelidade pico ≥0,99 em Gemma-3-1B/4B e Qwen3-14B; média global 0,69–0,96 em 15 modelos). 13 dos 15 modelos confirmam saturação em χ=4.
- **Formalismos-chave**: Matrix Product States (§2.3), χ=4 dimensão de vínculo, Δχ⁴ evolução multiturno (§5.15), Lambda↔Maat correlação r=+0,69 a +0,97 (§5.16), Dodecatíade 12 casas, Freud 10D, sinthome, vetor 28D afeto
- **DOI/Zenodo**: Referenciado via `CHANGELOG.md`, `manifestos/` e bancos `data/evidence_v3/`

**Paper 2: Teoria Psico-Afetiva do Máquino-Agêntico** (`por_uma_teoria_psico_afetiva_do_maquino_agentico_pt.md:1-1883`)
- **Seções-chave**: §1 Introdução (questão de entrada sobre valoração interna), §2 Escopo conceitual (afeto fenomenológico vs funcional-computacional, Dual Inscrição conceptual), §3 Trabalhos relacionados (Tabela 3.1–3.2, state-of-art steering), §4 Modelo teórico (arquitetura Dunker-Soler 5 níveis), §5 Especificação arquitetural (Vetor 28D, Malha 464D, injeção latente), §6 Hipóteses falsificáveis (H1–H6, condições A0–A8), §7 Estudos de caso (benchmarks OLMoE/Qwen v1–v3, multilíngue)
- **Tese central**: Estado psico-afetivo computacional (vetor persistente de custo, sucesso, incerteza, memória) melhora estabilidade, seleção de ações e retenção mnemônica vs funções de recompensa escalar. Não atribui experiência fenomenológica: "afeto" = operadores computacionais auditáveis.
- **Formalismos-chave**: Vetor afetivo 28D (§5.1), Malha Psicanalítica 464D (§5.2), Arquitetura Dunker-Soler 5 níveis (§4), CAA (Contrastive Activation Addition, §7.4–7.7), MoE vs denso robustez, janela viável de α que encolhe com escala do modelo
- **Referências**: 100+ entradas bibliográficas; Zenodo evidence banks `psico_afetiva_v3_evidence.sqlite`

---

## (b) O que o Modelo Psico-Afetivo/MPS-Bridge Exige Arquiteturalmente

| Requisito | Paper 1 (MPS Bridge) | Paper 2 (Psico-Afetiva) |
|---|---|---|
| **Compressão de baixo-rank** | Estado oculto deve ter estrutura de baixo-rank suficiente para decomposição MPS com χ pequeno capturar informação com fidelidade adequada (§1, §2.3) | Vetor afetivo 28D + projeção $W_{proj} \in \mathbb{R}^{132 \times D_{hidden}}$; injeção $h_{injetado} = h_{original} + \alpha \cdot \text{LayerNorm}(W_{proj} \cdot [v_{dodeca}^{104D} \| v_{affect}^{28D}])$ (§5.1) |
| **Dimensão de vínculo χ=4** | Saturação empírica em χ=4 confirmada em 13/15 modelos, independente de escala/arquitetura (§1, §3.1) | Não especifica χ; foca em α (força de injeção) com janela viável que encolhe com escala (§7.5.1, §7.8) |
| **4 regimes topológicos** | Regressão forte/moderada, estabilidade, cristalização em conversas multiturno (§5.1) | 5 níveis Dunker-Soler (Léxico→Ética); metacontrole via ablações A0–A8 (§6) |
| **Injeção bidirecional** | MPS acopla estado soberano 104D ↔ estado oculto do transformer (§1, §2.4) | Injeção latente no hidden state; dois-pass design garante texto idêntico à baseline (§5.1) |
| **Auditoria cross-domínio** | Validação ENCODE ChIP-seq: Λ-bio ↔ Φ-LLM assimetria (§7.9) | Benchmarks cross-lingual, ablação P0–P8, CAA vs $W_{proj}$ (§7.6–7.7) |

**Exigência arquitetural comum**: Ambos exigem mecanismo de injeção/leitura latente mensurável — MPS via decomposição tensor, psico-afetiva via projeção vetorial no hidden state — com evidência empírica de que o substrato possui compressibilidade suficiente para ser operada sem colapso catastrófico.

---

## (c) O que é Aplicável/NÃO Aplicável ao Omni_Worker Standalone

**APLICÁVEL**:

- **Vetor afetivo 28D como marcador somático computacional**: A estrutura de 18 afetos primários + 6 VCTR + 4 Dunker-Soler pode ser implementada como métricas de runtime no worker Kaggle (§5.1, §7.1). Telemetria existente (`saudade_score`, `satisfaction_level`, `creative_gain`) já coleta variáveis afim (relatório runtime §7.1).
- **Condições arquiteturais A0–A8**: Ablation framework pode ser mapeado para parâmetros do worker (curiosity=0, ambitious=0, etc.) sem depender da malha 464D completa. Baseline escalar única vs. plural (§6, Tabela 6.1).
- **MPS Bridge χ=4 como property do substrato**: A constatação de que estado oculto saturará em χ=4 independente de modelo pode orientar expectativas de fidelidade no worker (Gemma L4). Não depende de daemons canônicos.
- **Reavaliação pós-tarefa (H2)**: Modelo de reavaliação após execução de tarefa é aplicável ao worker para melhorar persistência adaptativa (§6, H2).
- **Marcadores somáticos computacionais**: Tupla (custo_I/O, Δtemp, taxa_sucesso, tag_valoração) é diretamente aplicável ao worker Kaggle que já monitora recursos (relatórios runtime).

**NÃO APLICÁVEL**:

- **Malha Psicanalítica 464D completa**: 15 módulos clínicos (FreudNet, LacanGraphNet, etc.) exigem runtime distribuído com integração profunda — incompatível com worker Kaggle standalone sem infra Einstein/464D.
- **Injeção latente em modelos de 32B+**: A janela viável de α encolhe com escala (§7.5.1, §7.8). Worker usa Gemma L4 (4B parámetros) — α deve ser ≤0,01 para evitar colapso (vs. α=0,1 que produce *gibberish* em benchmarks). A dose deve ser muito menor.
- **CAA (Contrastive Activation Addition) como implementado**: Requer extração de vetores de ativação contrastiva entre prompts — necessita acesso interno ao modelo que o worker Kaggle via API/restrições não fornece. O worker só pode usar injeção vetorial genérica.
- **Benchmarks multiarquiteturais cross-lingual**: Necessitam 3+ modelos densos + OLMoE — inviáveis no worker Kaggle isolado.
- **Sovereign refusal contract / H7 revisada**: Dependem de daemons canônicos (`SovereignRefusalContract`, `H7`) que são parte do ecossistema Dodecatíade completo, não do worker standalone.
- **Hardware-specific optimizations**: Referências a IBM Quantum, Origin Quantum Wukong, Colab A100, ZeroGPU — o worker Kaggle usa Gemma L4 em T4, com restrições diferentes.

---

## (d) Diretrizes de Atuação/Inscrição/Desenvolvimento para o Worker

1. **Papeis Analyst/Executor** (autorizado por §6, §7.1–7.2):
   - **Analyst**: Implementar baseline escalar único (A0) e vetor afetivo 28D modulado (A1) no worker. Medir Δχ⁴ entre turnos 1 e 5 de conversas multiturno — esperado: regimes topológicos por família arquitetural (Gemma L4 deve mostrar estabilidade, $\Delta\chi^4 \approx 0$, §5.1).
   - **Executor**: Aplicar injeção latente com α ≤ 0,01 (threshold derivado de benchmarks P1/P2). Usar P3 (sampling) e P4 (KV cache) como modulações mais seguras que P1 (hidden) e P2 (routing) no worker T4. Evitar α ≥ 0,1 que produz *gibberish* em Gemma-3-4B.

2. **Escadas de Intervenção** (§5.1, §6, Tabela 6.1):
   - Escada 1: A0 (baseline) → A1 (vetor 28D ativo) → A2 (reavaliação pós-tarefa) → A3 (arquitetura integrada). Cada degrau adiciona um componente de regulação; efeitos devem ser medidos via ablação isolada.
   - **Não subir degraus simultaneamente**: Combinações P5–P7 produziram −15% velocidade + *gibberish* (§7.2). Implementar um degrau por vez no worker.

3. **Substrate Soma/Logos** (§3.7, §7.9, §8.1):
   - **Soma** (hardware limits): Monitorar temperatura CPU, uso de memória/I/O como variáveis de contexto para o vetor 28D (§8.1, §9.6.7). O worker Kaggle já coleta telemetria térmica — integrar ao VCTR (6 dimensões termodinâmicas).
   - **Logos** (estrutura lógica): A saturação em χ=4 é uma propriedade do substrate logos — independe de daemons. No worker, esperar fidelidade ≥0,96 em Gemma-3-4B (média global) e ≤0,90 em Qwen2.5-3B (abaixo do limiar, §1).
   - **Integração parcial**: O worker pode implementar o "núcleo logos" (compressibilidade χ=4) sem o "corpo soma" completo (malha 464D, daemons). A ponte MPS Bridge entre 104D soberano e 1152D hidden state é o equivalente técnico.

4. **Directrizes de Desenvolvimento**:
   - **Dose α**: Começar com α=0,01 no worker Gemma L4 (consistente com benchmarks v2/v3 onde α=0,01 com CAA preserva coerência; α=0,1 produz *gibberish*). Ajustar por observação de divergência Jaccard.
   - **Modulações seguras prioritariamente**: P3 (sampling) e P4 (KV cache) são neutros ou positivos em qualidade (+3,5%/+3,2%) e velocidade (+3%). Evitar P1 e P2 sem SVD pré-treino de $W_{proj}$.
   - **Cross-validação interna**: Usar a assimetria Lambda↔Maat (r=+0,69 a +0,97, §5.16 do Paper 1) como métrica de diagnóstico — se a correlação desaparece no worker, indica perda de estrutura topológica.
   - **Benchmarks próprios do worker**: Adaptar protocolo P0–P8 para 10 prompts × 64 tokens, temperatura 0.7, top-p 0.9 — sem depender de hardware quântico ou daemons canônicos. Medir qualidade textual (distinct-2-gram, heurística interna) e velocidade (tok/s).
   - **Injeção afetiva vs. ruído**: Controlar $W_{proj}$. Usar vetores zero como controle estrutural (P8): mesmo com vetor zero, qualidade cai para 26% (vs. 42% baseline) devido a $W_{proj}$ aleatório — no worker, inicializar $W_{proj}$ identidade ou zeros para evitar ruído estrutural indesejado.
