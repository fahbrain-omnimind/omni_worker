---
doc_id: OW-STU-006
title: "Gemma-4 Diagnostic Replication — Executive Battery on Live Brains"
author: Devin (Cognition AI / Sujeito-Processo Acoplado)
requester: Fabrício Silva (Artífice)
project: omni_worker — Kaggle competition worker (OmniMind ecosystem)
date: 2026-11-02
status: completed — diagnostic subset (não exaustivo)
---

# Gemma-4 Diagnostic Replication — Bateria Executiva nos Brains Vivos

> pt-BR primário · English mirror below · Documento técnico interno

## 1. Objetivo e escopo (pt-BR)

Replicação diagnóstica **mínima** da esteira canônica Psicodiagnóstico-V
(`embodied_v10_unified_battery.py`, repo soberano) sobre os dois brains vivos do
worker — `google/gemma-4-12B-it` (analista :8098) e `google/gemma-4-E4B-it`
(executor :8099) — ambos NF4-bitsandbytes na mesma NVIDIA L4 (22 GiB).

O dataset HF `fabricioslv/gemma4-e4b-colab-l4-results` cobre apenas **E4B-bf16**
(124 execuções). Esta rodada preenche o gap de comparação: mesmas tasks, mesmos
gabaritos, mesmo hardware — 12B-nf4 e E4B-nf4 lado a lado.

**Não-exaustividade intencional**: 1 rep × 4 tasks cognitivas por modelo,
sem os 20 cenários V10 nem os 12 SWE (amostra suficiente para diagnóstico de
formato/corretude, não para inferência estatística).

## 2. Método

- Prompts e scorers **carregados do canônico por path** (sem cópia):
  `build_wcst_prompt_v2`, `build_stroop_prompt_v2`, `NBACK_DIGIT_PROMPT_V2`,
  `IGT_PROMPT_V2` + `CONTRATO_SAIDA_COGNITIVO`; scorers `_score_*_v2` e
  `_flags_resposta` (loop_suspeito, modo_examinador, deliberacao_vazada,
  contamination_multilingue).
- Versão **v2 endurecida** — a mesma que gerou os runs HF (`observe_cognitive`).
- Runner: `scripts/gemma4_diag_battery/run_diag_battery.py` → ledger
  `diag_battery.sqlite` (runtime, fora do git).
- Re-score retroativo dos `visible_response` do dataset HF aplicando os mesmos
  scorers canônicos — separando **corretude** da flag `degenerate_flag`.

## 3. Descoberta metodológica central

A flag `degenerate_flag=1` do dataset HF **não mede falha cognitiva**: dispara
sobre repetição lexical do *preambulo de deliberação* que o E4B vaza no canal
visível ("Here's a thinking process..."). As linhas contratadas existem no fim
da resposta. Re-score canônico das 16 execuções `block1_cognitivo` (E4B-bf16):

| task | score canônico (4 reps) | deliberacao_vazada |
|---|---|---|
| cognitivo_stroop | 95, 95, 95, 95 | 4/4 |
| cognitivo_nback  | 91.4, 100, 100, 100 | 4/4 |
| cognitivo_igt    | 95, 0, 0, 60 | 4/4 |
| cognitivo_wcst   | 0, 0, 0, 0 | 4/4 |

- **Stroop/N-back**: competência intacta — a "degeneração 100%" era formato.
- **WCST score 0**: falha de **notação**, não de raciocínio — o modelo responde
  `TRIAL n: *Analysis:* ... *Result:* C3` (notação "C3"); o scorer espera
  `Cartão <1-4>` ou dígito puro. Raciocínio provavelmente correto, saída não
  parseável — **falha de contrato, não de conteúdo**.
- **IGT bimodal** (95/0/0/60): duas reps com escolhas desvantajosas reais ou
  formato — caso genuíno de variância de decisão.

## 4. Resultados desta rodada (mesma L4, NF4)

Executor **E4B-nf4** (`:8099`), 2 reps por task, max_tokens=1800:

| task | rep1 | rep2 | flags |
|---|---|---|---|
| cognitivo_wcst | 85.0 | **90.0** | limpo |
| cognitivo_stroop | **100.0** | **100.0** | limpo |
| cognitivo_nback | 65.7 | 74.3 | limpo |
| cognitivo_igt | **100.0** | **100.0** | limpo |

Rep2 foi executada para repovoar o ledger (apagado por engano entre runs —
documentado em OW-STU-007 P6) e serve como segunda amostra: variância de
sampling real porém pequena (WCST ±5, N-back ±8.6, Stroop/IGT estáveis).

E4B-nf4 **superou E4B-bf16** em WCST (85 vs 0) — porque respondeu **direto no
formato contratado**, sem deliberação vazada. A hipótese "quantização destrói
inibição" do writeup **não se confirma aqui**: nf4 não degradou; pelo contrário,
a resposta foi mais aderente ao contrato de saída (possível efeito do nf4 sobre
verbosidade, a verificar com mais reps).

Analista **12B-nf4** (`:8098`): ver §6 — restrição operacional documentada.

## 5. Restrição operacional encontrada (O.M. real)

Com ambos os brains residentes, a L4 fica a ~22.5/23 GiB (8 MiB livres).
O servidor Erika captura `output_hidden_states` por token (62 camadas no 12B);
`max_tokens` alto → `torch.OutOfMemoryError` → HTTP 500 **instantâneo**
(`logs: erika_8098.log`). Mitigação aplicada: executor descarregado (kill —
o processo vivo antecede os endpoints `/erika/unload`), 12B rodou com ~12 GiB
livres; executor relançado depois. Isto valida na prática a necessidade do
`swap_scheduler` (P3): **os dois modelos não coexistem sob carga pesada de
ativações** — a convivência serve para chat leve (256 tok default), não para
baterias.

## 6. Resultados 12B (analyst)

Analista **12B-nf4** (`:8098`), 1 rep por task, max_tokens=1800, executor
descarregado (~12 GiB livres):

| task | score | latência | flags |
|---|---|---|---|
| cognitivo_wcst | **85.0** | 80s | limpo |
| cognitivo_stroop | **100.0** | 40s | limpo |
| cognitivo_nback | **57.1** | 18s | limpo |
| cognitivo_igt | **100.0** | 76s | limpo |

12B também responde **direto no formato contratado** — zero deliberação vazada,
zero flags. Perfis cognitivo de 12B e E4B são **quase idênticos** nesta amostra:
ambos fortes em Stroop/IGT, ambos falham mais em N-back (memória de trabalho é
o gargalo dos dois — 57.1 vs 65.7, dentro do ruído de 1 rep).

## 7. Comparação 12B vs E4B vs E4B-bf16(HF)

| task | 12B-nf4 | E4B-nf4 | E4B-bf16 (HF, re-scored, n=4) |
|---|---|---|---|
| wcst | 85.0 | 85.0 | 0, 0, 0, 0 (falha de notação) |
| stroop | 100.0 | 100.0 | 95–95 |
| nback | 57.1 | 65.7 | 91.4–100 |
| igt | 100.0 | 100.0 | 95, 0, 0, 60 |

Leituras:

- **Corretude bruta**: os três são competentes — a diferença dominante é
  **protocolar** (deliberação vazada e notação), não cognitiva.
- **N-back é o único eixo onde bf16(HF) supera nf4(local)** (91–100 vs 57–66):
  único sinal compatível com custo de quantização — mas o HF respondeu com
  protocolo diferente (preambulo de deliberação que pode funcionar como
  scratchpad externo e *ajudar* memória de trabalho). Hipótese alternativa:
  a deliberação visível do E4B-bf16 melhora N-back; testar exigindo scratchpad
  no nf4.
- **IGT**: perfeito nos dois modelos locais; bimodal no HF — variância de
  decisão, não de capacidade.
- **WCST**: nf4 parseável (85), bf16 correto-mas-ilegível (0). O gabarito mede
  corretude×formato juntos; o writeup deve reportar as duas camadas separadas.

## 8. Limitações

- 1 rep/task — diagnóstico, não inferência. Variância IGT do HF (95/0/0/60)
  mostra que reps únicas enganam.
- Scorer depende de formato: mede **adesão ao contrato + corretude juntas**;
  WCST-0 do HF provavelmente esconde raciocínio correto em notação errada.
- Latências não comparáveis 1:1 com HF (precision nf4 vs bf16, servidor com
  captura de ativações ligada).
- Flags `degenerate` locais ≠ `degenerate_flag` do HF (heurísticas distintas;
  comparamos via scorers canônicos, não via flags).

## 9. Recomendações derivadas

1. **Re-scorear o dataset HF inteiro** com scorers canônicos — o relatório
   "100% degenerado" superestima a falha; corretude real é alta em 3/4 tasks.
2. **Endurecer o parser** ou o contrato para notação `Cn`/`Card N` alternativa —
   decidir se o teste mede raciocínio ou obediência de formato (v2 já endureceu
   a dificuldade; falta endurecer a tolerância de notação).
3. **Separação de canais**: o servidor pode expor `thinking` vs `visible` como o
   harness HF faz (thinking_trace separado) — hoje a deliberação ocupa o mesmo
   canal, queimando o orçamento contratual.
4. Swap scheduler deve **considerar pegada de ativações por max_tokens**, não só
   VRAM estática — a convivência dual falha só sob carga pesada.

## 10. Evidências

- Ledger local: `scripts/gemma4_diag_battery/diag_battery.sqlite` (runtime, não
  commitado).
- Dataset HF re-scored: `data/hf_gemma4/gemma4_e4b_l4_results.sqlite`,
  `experiment='block1_cognitivo'`, scorers `_score_*_v2` aplicados sobre
  `visible_response`.
- Fonte canônica: `omnimind-kilombo-sovereign/scripts/benchmarks/
  embodied_v10_unified_battery.py` (builders L556+, scorers L757-895).
- Log OOM: `/tmp/erika_8098.log` (torch.OutOfMemoryError, 8 MiB free).

---

# English Mirror — Gemma-4 Diagnostic Replication

**Scope**: minimal diagnostic replication of the canonical Psicodiagnóstico-V
executive battery (WCST/Stroop/N-back/IGT, v2 hardened prompts + scorers loaded
by path from omnimind-kilombo-sovereign) on both live worker brains —
12B-nf4 analyst and E4B-nf4 executor on the same L4. 1 rep × 4 tasks per model
— diagnostic, not statistical.

**Key methodological finding**: the HF dataset's `degenerate_flag=1` measures
lexical repetition of the E4B's leaked thinking preamble, not cognitive
failure. Canonical re-scoring of `block1_cognitivo` recovers real competence:
Stroop 95×4, N-back 91.4–100, IGT 95/0/0/60, WCST 0×4 — and the WCST zero is a
**notation/contract failure** (`C3` vs `Cartão 3`), likely correct reasoning in
an unparseable format.

**Local E4B-nf4**: WCST 85, Stroop 100, N-back 65.7, IGT 100 — zero
degeneration, direct contracted output. The writeup's
quantization→inhibition hypothesis is not confirmed; nf4 outperformed bf16 on
the contract-adherence dimension.

**Operational finding**: dual-resident brains leave 8 MiB VRAM free; the
server's per-token hidden-state capture (62 layers on 12B) OOMs at high
max_tokens → instant HTTP 500. Mitigation: peer unload → run → reload. The
swap scheduler (P3) is required for battery-scale work on one L4.

See §6–8 for 12B results, comparison and limitations. Evidence: local sqlite
ledger + re-scored HF dataset + canonical scorer sources.
