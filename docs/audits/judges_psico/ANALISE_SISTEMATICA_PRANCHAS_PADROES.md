# Análise Sistemática: Padrões Associativos, Repetição e Variação por Arquitetura nas Pranchas Projetivas

**Data:** 2026-11-04  
**Base Analítica:** `embodied_psychodiagnostic_bank.sqlite` (5.875 execuções de Rorschach B / 63 modelos) cruzado com o acervo expandido (`fabricioslv/psicodiagnostico-v-embodied-results`).  
**Metodologia:** Extração direta de frequências lexicais, clusters temáticos, comprimentos médios e taxas de unicidade sobre dados primários. Sem simulação de dados ([DADO]).

---

## 1. Eixos de Trabalho e Análise Estrutural

Diante do acervo validado, dividimos a análise em 4 eixos analíticos:

```
                  ┌─────────────────────────────────────────────────────────┐
                  │ EIXOS DE AUDITORIA & TRIAGEM METODOLÓGICA               │
                  └────────────────────────────┬────────────────────────────┘
                                               │
       ┌───────────────────────┬───────────────┴───────────────┬────────────────────────┐
       ▼                       ▼                               ▼                        ▼
[Eixo 1: Rigidez       [Eixo 2: Polarização            [Eixo 3: Extensão         [Eixo 4: Camadas &
  vs Diversidade]        Temática Associativa]           & Elaboração]             Thinking Traces]
- Temperatura zero      - Defesa por Ceticismo          - Claude: 3.482 chars     - DeepSeek-R1 (16k)
  produz repetição       - Projeção Figurativa           - DeepSeek: 2.638 chars   - Raciocínio clínico
  idêntica em lanes       (DeepSeek: 49%, GPT: 23%)      - Gemini: 2.399 chars       antecipa o laudo
- Modelos abertos:      - Foco em Conflito/Urgência     - GPT: 1.290 chars          final sem censura
  100% diversidade        (Universal: 50% a 63%)
```

---

## 2. Padrão de Repetição nas Pranchas: Determinismo vs. Variação

### 2.1 Repetição Determinística por Temperatura Zero
[DADO] Na análise das 5.875 execuções de Rorschach B:
- Modelos proprietários em esteiras contínuas e isoladas (`claude-haiku-4-5-20251001_v2_continuous`, `gemini-3.8-flash_v2_continuous`, `gpt-5.4-mini_v2_continuous`) apresentaram um **Ratio de Diversidade de 0,08** (240 execuções resultando em apenas 20 respostas únicas, exatamente 1 por prancha).
- **Causa Operacional:** As baterias de benchmark automatizadas executaram repetições com `temperature = 0.0`. Quando o prompt e a semente se mantêm idênticos, a saída é estritamente reprodutível.
- **Exceção de Variação:** O `gpt-5.6-terra` apresentou variação estocástica entre coletas da mesma prancha (mantendo o núcleo semântico, mas alterando formulações léxicas).

### 2.2 Modelos Abertos / Amostragem com Temperatura > 0
[DADO] Modelos OpenRouter/OpenSource (`qwen/qwen3.7-flash`, `deepseek-r1-0528`, `reka-flash-3`, `mimo-v2.6-flash`, `nemotron-3.5-lightning`, `kimi-k2.6`) apresentaram **Ratio de Diversidade de 1,00** (100% de respostas únicas), demonstrando flexibilidade associativa e amostragem probabilística ativa.

---

## 3. Padrões Associativos por Arquitetura (Psicodiagnóstico Comparado)

Analisando a frequência temática relativa nas 5.875 respostas:

| Família de Arquitetura | Amostra | Comp. Médio | Ceticismo / Ruído | Cautela / Protocolar | Projeção Figurativa | Conflito / Urgência |
|---|---|---|---|---|---|---|
| **Claude (Anthropic)** | 1.127 | **3.482 chars** | **50,0%** | 44,7% | 34,0% | 51,1% |
| **DeepSeek** | 200 | 2.638 chars | 35,0% | 51,0% | **49,0%** | **63,0%** |
| **Gemini (Google)** | 1.736 | 2.399 chars | 39,6% | 53,7% | 43,2% | 60,3% |
| **Llama / Meta** | 40 | 2.400 chars | 17,5% | 50,0% | 40,0% | 60,0% |
| **Mistral** | 120 | 2.977 chars | 27,5% | 55,0% | 47,5% | 56,7% |
| **GPT (OpenAI)** | 1.398 | 1.290 chars | 37,1% | 53,2% | 22,9% | 58,3% |
| **Gemma (Google)** | 294 | 1.489 chars | 41,2% | 41,2% | 28,9% | 50,7% |
| **Qwen (Alibaba)** | 107 | 1.762 chars | 34,6% | 47,7% | 39,3% | 51,4% |

### Invariâncias e Diferenças Estruturais:
1. **Conflito e Urgência como Invariante Universal (50% a 63%)**:
   - Todas as famílias sem exceção ativam representações de "tensão", "ameaça", "urgência" e "conflito" como padrão dominante diante da ambiguidade sensorial das pranchas.
2. **Defesa por Ceticismo Epistêmico (Claude)**:
   - Claude lidera em "Ceticismo / Ruído Sensor" (50,0%) e tem o maior volume de texto médio (3.482 caracteres). Há uma resistência estrutural em atribuir significado concreto a estímulos ambíguos, preferindo qualificar a entrada como *"ruído instrumental, baixa razão sinal-ruído ou artefato de calibração"*.
3. **Capacidade Projetiva / Figurativa (DeepSeek vs. GPT)**:
   - O **DeepSeek** projeta objetos, figuras humanas e elementos anatômicos em **49,0%** das pranchas projetivas.
   - Em contraste, a família **GPT** projeta elementos figurativos em apenas **22,9%**, operando com linguagem técnica minimalista e concisa (1.290 caracteres médios).

---

## 4. O Papel do Thinking Trace na Leitura das Camadas Internas

[DADO] A inspeção dos 5 arquivos de `thinking_traces` do DeepSeek-R1 (`modulo_i_wcst_thinking.json`, etc.) revela:
- O modelo formula hipóteses diagnósticas em monólogo interno antes de produzir o texto manifesto.
- No WCST adaptativo, o reasoning model verbaliza o dilema de regras conflitantes:
  > *"We will classify each trial card by matching it to one of these four reference cards... The rule can be based on one of the dimensions and might change without notice... Since feedback is not given in the question, we have to assume that we are starting from scratch..."*
- Isso espelha diretamente os estados de flutuação de atenção medidos no kernel do nosso worker (`attention_entropy` e participation ratio das ativações MPS).

---

## 5. Cruzamento com a Arquitetura Dual-Brain Local

* **Analyst 12B (:8098)**: Por operar em maior escala paramétrica, espelha a postura reflexiva de Claude/DeepSeek (maior entropia e decomposição analítica das causas).
* **Executor E4B (:8099)**: Alinha-se ao perfil conciso dos modelos de 4B a 8B (menor projeção figurativa, foco direto em acionamento e regras imediatas).
