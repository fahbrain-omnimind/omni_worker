# Auditoria de Alegações Quantitativas — PAPER_WRITEUP.md

**Objetivo**: confrontar alegações numéricas do writeup contra código e ledgers
do repo. Resultado: tabela claim→evidência→veredito + correções sugeridas.
**Escopo**: `docs/PAPER_WRITEUP.md`, `src/omni_coworker/activation_beta/hidden_spectral.py`,
`docs/audit/OW-AUD-018_*`, `docs/audit/OW-AUD-020_*`, bancos `scripts/*/*.sqlite`,
`data/hf_gemma4/*.sqlite`, `data/psicodiagnostico_v/gemma4_runs_20261030/v10_colab_benchmark.sqlite`,
`data/psicodiagnostico_v/embodied_psychodiagnostic_bank.sqlite`.

---

## 1. Tabela de Verificação

| # | Claim no writeup | Evidência do repo/código | Veredito |
|---|------------------|--------------------------|----------|
| C1 | Abstract: *eff_rank=114.6 vs 40.3* (12B vs E4B) | `hidden_spectral.py:L75-86` implementa `exp(H(σ²/Σσ²))` (entropia de Shannon dos valores singulares normalizados). `_ipr_dim` implementa `(Σh²)²/Σh⁴`. OW-AUD-020 §2.2 executou o código publicado e obteve `eff_rank_mean=2.496` (12B) e `2.516` (E4B). A tabela §3.4b do writeup coloca 114.6/40.3 na coluna *IPR_dim* e 2.496/2.516 na coluna *eff_rank_K*, mas o abstract rotula tudo como *eff_rank*. `mps_spectral_first.md` define *eff_rank* como participation ratio de Roy & Vetterli, fórmula não implementada em `src/`. | **CORRIGIR** |
| C2 | §3.4b: *12B ativa 1.7× mais subespaço representacional por componente (IPR_dim/D = 2.56% vs 1.52%)* | Mesma evidência de C1. O número 1.7× corresponde a 114.6/40.3, que é IPR_dim (intra-vetor). O código publicado com K=8 produz 2.496/2.516 para eff_rank inter-gerações, que na verdade é ~1.0×, não 1.7×. | **CORRIGIR** |
| C3 | §3.4c: *10/10 (100%) correções que compilam e passam no black em cada rodada* | `scripts/coding_battery/coding_battery.sqlite` contém 50 linhas (10 casos × 5 repetições). `fix_compiles=1` em 20/50 (40.0%). Com analista ativo: 20/30 (66.7%). Sem analista: 0/20. Nenhuma agregação atinge 10/10. OW-AUD-020 §2.4 registrou 10/34 (29.4%) em versão anterior; o ledger atual expandiu para 50 linhas, mas a taxa não chega a 100%. | **CORRIGIR** |
| C4 | Abstract + §3.4a: *0/88 degenerate runs in live L4 diagnostics* / *88/88 execuções (0% de degeneração)* | `scripts/gemma4_diag_battery/diag_battery.sqlite` está vazio (0 bytes, 0 tabelas). Nenhum ledger local suporta N=88. `data/hf_gemma4/gemma4_e4b_l4_results.sqlite` mostra 126 registros com `degenerate_flag=1` em 49/126 (38.9%). `data/hf_gemma4/gemma4_t4x2_cascade_results.sqlite` mostra 200 registros com `degenerate_flag=1` em 75/200 (37.5%). `docs/CONTINUITY_MAP.md` menciona "40/40 rows" e "degenerate=0", mas não há artefato sqlite correspondente no repo. | **CORRIGIR / SEM_EVIDENCIA** |
| C5 | Implícito em §3.4c: *loop fechado de até 3 turnos* (multi-turno funcional) | `data/hf_gemma4/gemma4_e4b_l4_results.sqlite` possui colunas `turn2_tokens`, `turn2_latency`, `ur_turn2`, `turn2_response`, mas `turn2_tokens=0` em 126/126 registros. `AUDIT_KILO_EXPERIMENTS_GAPS_20261104.md` registra: "turn2_* = 0/NULL em 126/126 (turn2 não executado)". | **CORRIGIR** |
| C6 | §3.4d: *16/16 cenários na supervisor_battery* | `supervisor_battery.sqlite` não existe em nenhum diretório do repo (`find` retornou 0 arquivos). OW-AUD-020 menciona o arquivo, mas ele não está presente no disco. | **SEM_EVIDENCIA** |
| C7 | Intro/Methods: *~18k registros, ~85 modelos no total* | `embodied_psychodiagnostic_bank.sqlite`: benchmark_runs=389, v10_runs=124, rorschach_b_runs=5875, module_scores=1805, etc. Total de linhas em tabelas não-sequence = 10.230. `gemma4_runs_20261030/v10_colab_benchmark.sqlite`: 1.760+800+5.099 = 7.659. Soma total local ≈ 17.889. A cifra é plausível por soma de tabelas distintas, mas o writeup cita "18k registros" sem especificar a agregação. | **CONFERE (com ressalva)** |
| C8 | Methods: *72 com runs persistidas no banco canônico embodied_psychodiagnostic_bank.sqlite* | `benchmark_runs` tem 72 `model_id` distintos. Confere exatamente. | **CONFERE** |
| C9 | Intro: *61 model identifiers* validados para executive-control factor | `v10_colab_benchmark.sqlite` (gemma4_runs_20261030) tem 20 modelos. `embodied_psychodiagnostic_bank.sqlite` tem 49 em `v10_runs`, 63 em `rorschach_b_runs`, 72 em `benchmark_runs`. A cifra 61 não foi localizada diretamente como COUNT(DISTINCT model_id) em uma única tabela do repo atual. | **SEM_EVIDENCIA** |
| C10 | §3.1: *15 controles não-Gemma* no banco Gemma-4 | `gemma4_runs_20261030/v10_colab_benchmark.sqlite` lista 16 modelos não-Gemma em `v10_runs` (excluindo 4 Gemma-4). Writeup cita 15. | **CORRIGIR** |

---

## 2. Detalhamento dos Gaps Críticos

### 2.1 eff_rank / IPR — fórmula implementada vs rotulada

- **O que o código faz** (`hidden_spectral.py:L68-85`):
  - `_spectral_entropy(s)`: `H = -Σ p_i log(p_i)` com `p_i = σ_i² / Σσ_i²`.
  - `_eff_rank`: retorna `exp(H)`.
  - Isso é **effective rank entrópico**, não a participation ratio de Roy & Vetterli `(Σσ²)² / Σσ⁴`.

- **O que o writeup rotula**:
  - Abstract: *eff_rank=114.6 vs 40.3*.
  - §3.4b tabela: coluna `IPR_dim` médio = 114.6/40.3; coluna `eff_rank_K` = 2.496/2.516.
  - Texto: "Roy & Vetterli Participation Ratio".

- **Conflito**: 114.6/40.3 são valores de IPR_dim (calculados por `_ipr_dim`), não de eff_rank. O abstract usa o nome errado. O texto cita Roy & Vetterli, mas o código usa entropia espectral.

### 2.2 10/10 correções vs ledger real

- **Ledger** (`coding_battery.sqlite`): 50 linhas. 20 `fix_compiles=1`, 30 `fix_compiles=0`.
- **Distribuição**: 20 linhas `no_analyst` (fix_compiles=0), 30 linhas `done` (20 com fix_compiles=1, 10 com fix_compiles=0).
- **Writeup**: afirma 10/10 *em cada rodada*. Não existe rodada (agrupamento por `case_id` e `rep`) com 10/10. A melhor taxa é 66.7% (20/30 com analista).

### 2.3 0/88 vs 40/40 degenerate runs

- **Artefatos existentes**:
  - `diag_battery.sqlite`: vazio. Não suporta N=88.
  - `gemma4_e4b_l4_results.sqlite`: 126 registros, 49 degenerados (38.9%).
  - `gemma4_t4x2_cascade_results.sqlite`: 200 registros, 75 degenerados (37.5%).
- **Referência a 40/40**: aparece apenas em `docs/CONTINUITY_MAP.md` como "40/40 rows" de uma execução passada, sem sqlite correspondente no repo atual.
- **Conclusão**: a cifra 0/88 não tem respaldo nos bancos acessíveis. A cifra 40/40 é citada em documento de continuidade, mas não há artefato sqlite verificável.

### 2.4 Claims de turn2 sem evidência

- O writeup descreve um pipeline multi-turno com reinjeção de feedback (até 3 turnos).
- O banco `gemma4_e4b_l4_results.sqlite` registra colunas de turn2, mas todos os 126 registros têm `turn2_tokens=0` e demais campos NULL/0.
- Portanto, o turn2 não foi executado nas runs persistidas. Descrevê-lo como parte funcional do pipeline é enganoso sem evidência de execução.

### 2.5 16/16 supervisor_battery

- Nenhum arquivo `supervisor_battery.sqlite` existe no repo. A claim é não-verificável localmente.

---

## 3. Correções Sugeridas de Texto (não editivo)

### 3.1 Abstract

**Original**:
> ...eff_rank=114.6 vs 40.3... achieving 0/88 degenerate runs in live L4 diagnostics...

**Sugestão**:
> ...IPR_dim=114.6 vs 40.3 (intra-vetor, K=64 sidecars) enquanto o effective rank inter-gerações (K=8) é ≈2.5 para ambos... [remover ou corrigir 0/88]

### 3.2 Seção 3.4b

**Original**:
> 12B ativa 1.7× mais do seu subespaço representacional por componente (IPR_dim/D = 2.56% vs 1.52%)

**Sugestão**:
> 12B apresenta IPR_dim 1.7× maior que E4B (114.6 vs 40.3; IPR_dim/D = 2.56% vs 1.52%). O effective rank inter-gerações (K=8) é ≈2.5 para ambos, indicando que a janela curta entre gerações concentra a trajetória em subespaço similar.

### 3.3 Seção 3.4c

**Original**:
> ...o pipeline alcançou 10/10 (100%) correções que compilam e passam no black em cada rodada...

**Sugestão**:
> ...o pipeline alcançou 20/30 correções que compilam e passam no black quando o Analista está ativo (66.7%), contra 0/20 sem Analista. No ledger total de 50 linhas, 20/50 (40%) produzem fix_compiles=1.

### 3.4 Seção 3.4a

**Original**:
> ...ambos os cérebros atingem degenerate=0 em 88/88 execuções (0% de degeneração).

**Sugestão**:
> [Remover ou substituir por dado verificável]. O ledger `diag_battery.sqlite` referenciado está vazio. O dataset `gemma4_e4b_l4_results.sqlite` (126 runs) registra 49/126 (38.9%) `degenerate_flag=1`. O dataset `gemma4_t4x2_cascade_results.sqlite` (200 runs) registra 75/200 (37.5%). Nenhum artefato no repo sustenta 0/88.

### 3.5 Seção 3.4c (multi-turno)

**Original**:
> Implementa um loop fechado de até 3 turnos...

**Sugestão**:
> Implementa um loop fechado de até 3 turnos [em código], mas o ledger `gemma4_e4b_l4_results.sqlite` mostra que apenas o turno 1 foi efetivamente executado nas runs persistidas (turn2_tokens=0 em 126/126 registros).

### 3.6 Seção 3.4d

**Original**:
> ...detectou 16/16 cenários na supervisor_battery...

**Sugestão**:
> [Remover ou substituir]. O artefato `supervisor_battery.sqlite` não existe no repo; a claim 16/16 não é verificável localmente.

### 3.7 Methods — contagem de registros e modelos

**Original**:
> ~18.000 registros, ~85 modelos no total (72 com runs persistidas no banco canônico)

**Sugestão**:
> ~17.900 registros no total (soma de tabelas de `embodied_psychodiagnostic_bank.sqlite` + `gemma4_runs_20261030/v10_colab_benchmark.sqlite`), 72 modelos com runs em `benchmark_runs` (banco canônico).

### 3.8 Methods — controles não-Gemma

**Original**:
> ...15 controles não-Gemma

**Sugestão**:
> ...16 controles não-Gemma (contagem em `v10_runs` do banco `gemma4_runs_20261030`).

---

## 4. Ações Recomendadas (prioridade)

1. **Alta**: Separar claramente no writeup `IPR_dim` (intra-vetor, fórmula `(Σh²)²/Σh⁴`) de `eff_rank` (inter-gerações, fórmula `exp(H(σ²/Σσ²))`). Atualizar abstract para usar o nome correto.
2. **Alta**: Substituir 0/88 por dado de banco acessível ou remover a claim.
3. **Alta**: Corrigir 10/10 para 20/30 (66.7% com analista) ou remover a claim de 100%.
4. **Média**: Documentar que turn2 não foi executado nos ledgers atuais, ou executá-lo e persistir o sqlite.
5. **Média**: Disponibilizar `supervisor_battery.sqlite` ou remover a claim 16/16.
6. **Baixa**: Reconciliar 40/40 (CONTINUITY_MAP) com artefato sqlite ausente ou descartar a cifra.

---

## 5. Nota Metodológica

Este documento segue a REGRA DE INTEGRIDADE do repo: todas as cifras foram
extraídas de arquivos locais via consulta direta; nenhum dado foi simulado
ou inferido sem fonte. Where a evidência está ausente (`SEM_EVIDENCIA`),
isso foi declarado explicitamente, em vez de fabricar números.
