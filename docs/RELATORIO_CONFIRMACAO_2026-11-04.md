<!-- doc_id: OW-MAP-002 | title: Relatório de Confirmação — Bion + Rescore HF | date: 2026-11-04 | author: kiro | status: active -->

# Relatório de Confirmação — Bion & Rescore HF 108 blocks

> Todas as afirmações abaixo verificadas diretamente em arquivo/código/sqlite.
> Nenhuma inferência sem evidência.

---

## 1. BION — O que está implementado vs. o que não está

### Pergunta: "O Bion não foi implementado em outros módulos?"

**Resposta verificada: PARCIALMENTE INCORRETO** — Bion está implementado,
portado e wired. O `__init__.py` da `psychoanalysis/` continha uma nota
enganosa dizendo que `BionAlphaFunction` "não está neste escopo", mas o
arquivo `bion_alpha_function.py` **existe e é importável**.

#### [DADO] O que existe e funciona

| Arquivo | O que implementa | Importável? |
|---------|-----------------|-------------|
| `psychoanalysis/bion_alpha_function.py` | `BionAlphaFunction` — β→α transform com symbolizer, history, rates | ✅ SIM |
| `psychoanalysis/bion_symbolizer.py` | `BionAsyncSymbolizer` — symbolizer CPU (sem torch/LLM) | ✅ SIM |
| `psychoanalysis/bion_patches/container_contained.py` | `BionContainerPatch` — contenção container-contained com degraded reverie | ✅ SIM |
| `psychoanalysis/beta_element.py` | `BetaElement`, `NeutrosophicTriplet` (mínimo) | ✅ SIM |
| `psychoanalysis/alpha_element.py` | `AlphaElement`, `compute_dodecatiad_sector` | ✅ SIM |
| `psychoanalysis/negative_capability.py` | `NegativeCapability`, `Contradiction` | ✅ SIM |
| `psychoanalysis/creative_psychotization_operator.py` | `assess_creative_psychotization`, regimes | ✅ SIM |
| `psychoanalysis/freudian_apparatus_numpy.py` | Aparelho freudiano numpy | ✅ SIM |
| `psychoanalysis/freudnet_repression.py` | FreudNet repressão | ✅ SIM |
| `psychoanalysis/markov_blanket.py` | Blanket PyPhi (IIT real 4-6 nós) | ✅ SIM |
| `psychoanalysis/plasticity_resource.py` | Plasticidade | ✅ SIM |
| `psychoanalysis/defense_mechanisms.py` | Mecanismos de defesa | ✅ SIM |
| `integration_loop/bion_bridge.py` | Adapter β→α para o ciclo de integração | ✅ SIM |

**Wire real verificado**: `integration_loop/loop.py:262` chama
`bion_bridge.metabolize(...)` — Bion está **no caminho de produção** do
integration loop.

#### [DADO] O que a nota do __init__ dizia vs. realidade

A linha `psychoanalysis/__init__.py:21`:
> "`BionAlphaFunction` não está neste escopo: `BionContainerPatch` opera
> por duck typing sobre `transform`"

Isso é **errado como descrição do estado atual**: `bion_alpha_function.py`
existe e é importável. A nota era verdadeira durante a implementação
parcial (antes de o arquivo ser criado) e nunca foi atualizada.
`BionAlphaFunction` não está no `__all__` do `__init__.py` — mas o
arquivo existe e `bion_bridge.py` a importa diretamente.

#### [DADO] O que NÃO foi portado do soberano (gap real)

Comparando `omnimind-kilombo-sovereign/src/psychoanalysis/` com
`omni_worker/src/omni_coworker/psychoanalysis/`:

| Arquivo soberano | No worker? | Observação |
|-----------------|-----------|-----------|
| `bion_rsi_modulator.py` | ❌ NÃO | RSI modulator Bioniano — não portado |
| `bion_patches/bion_grid.py` | ❌ NÃO | Grade Bion — não portada |
| `bion_patches/bion_links.py` | ❌ NÃO | Links Bion (K, L, H) — não portados |
| `bion_patches/bion_vertex.py` | ❌ NÃO | Vértice Bion — não portado |
| `bion_patches/integration_wrapper.py` | ❌ NÃO | Wrapper de integração — não portado |
| `bion_patches/knowledge_link_extension.py` | ❌ NÃO | Extensão links K — não portada |
| `bion_patches/ultimate_reality.py` | ❌ NÃO | "O" (realidade última Bion) — não portado |
| `author_state_lens.py` | ❌ NÃO | Lente de estado do autor — não portada |
| `big_other_interview.py` | ❌ NÃO | Grande Outro entrevista — não portado |
| `cn_oracle_trigger.py` | ❌ NÃO | Oráculo CN trigger — não portado |
| `lacanian_structures.py` | ❌ NÃO | Estruturas Lacanianas (separado de discourse_discovery) — não portado |
| `plasticity_context_resource.py` | ❌ NÃO | Plasticidade contextual — não portada (worker tem `plasticity_resource.py` diferente) |

#### [DADO] Onde Bion NÃO é usado (mas poderia/deveria)

| Módulo | Status Bion | Observação |
|--------|------------|-----------|
| `agency/affect_tracer.py` | ❌ sem Bion | Escada afetiva L0-L4 léxica — não usa β→α |
| `agents/analyst_agent.py` | ❌ sem Bion | Agente analista sem pipeline Bion |
| `orchestration/agent_orchestrator.py` | ❌ sem Bion | Sem metabolização β→α nas deliberações |
| `soul/` | referência HTML | Menciona Bion na UI (`bionStateText`) mas consome do integration_loop via API |
| `activation_beta/` | menção em docstring | `__init__.py` e `neuroanatomy.py` **mencionam** `bion_bridge` mas não importam |
| `kernel_daemon/collector.py` | ❌ sem Bion | Coleta ativações mas não passa por β→α |

**Conclusão sobre Bion**: o módulo está portado e vivo no `integration_loop`.
O gap real são os 12 arquivos de `bion_patches/` não portados (grid, links,
vertex, RSI modulator, etc.) e a ausência de wire nos agentes/affect_tracer.

---

## 2. RESCORE DOS 108 HF BLOCKS — Estado real

### Pergunta: "O rescore dos 108 HF não foi feito?"

**Resposta verificada: JÁ FOI FEITO** — mas o artefato sqlite foi
perdido (gitignored). O relatório sobreviveu. Precisão exata abaixo.

#### [DADO] O que foi rescored

O script `scripts/gemma4_diag_battery/rescore_hf_blocks.py` rodou em
**2026-11-03T11:37:12Z** (timestamp do relatório gerado). Cobriu
**todos os 126 generation_records** do sqlite HF:

| experiment | n records | rescored? | resultado |
|-----------|-----------|----------|-----------|
| block1_cognitivo | 16 | ✅ SIM | agree_v2=16/16 (100%) |
| block1_observe | 20 | ✅ SIM | agree_v2=20/20 (100%) |
| block1_pranchas | 20 | ✅ SIM | agree_v2=20/20 (100%) |
| block1_v10 | 20 | ✅ SIM | agree_v2=20/20 (100%) |
| block2_intervene | 48 | ✅ SIM | agree_v2=22/48 (46%) — discordâncias documentadas |
| canary | 2 | ✅ SIM | agree_v2=2/2 (100%) |

**Total: 126 records rescored** (não 108 — o mapa antigo excluía os
cognitivos já feitos; o script cobriu tudo).

#### [DADO] O que o artefato de saída revelou

- `rescore_hf_blocks.sqlite`: **AUSENTE** (gitignored, não commitado — foi
  gerado localmente e perdido na reinicialização da VM). Confirmado via
  `ls scripts/gemma4_diag_battery/rescore_hf_blocks.sqlite` → não existe.
- `docs/results/rescore_hf_blocks.md`: **PRESENTE** — relatório completo
  com tabela de concordância e 26 discordâncias listadas.

#### [DADO] Principal achado do rescore

- **`block1_cognitivo`**: heurístico de shape de linhas concordou 0/16 com
  o HF; scorer v2 (word_ur<0.5 ∧ rep4>0.05) concordou 16/16. **Conclusão**:
  o flag armazenado no HF captura degeneração verbosa por word-level unique
  ratio, não shape de linhas — o heurístico original do worker era cego.
- **`block2_intervene`**: 33 records marcados como degen no HF; scorer v2
  só confirma 7. Divergência de 26 = mistura semântica de gates (degen=1
  ↔ gates=0 em 33 casos) com degeneração real. Documentado com 26
  discordâncias individuais em `rescore_hf_blocks.md`.

#### [LIMITE] O que ainda falta

O rescore cobriu as **métricas** (degen heuristic v1/v2, unique_ratio,
flags). O que **não** foi feito:
1. Rescore com **scorer canônico de tarefa** (corretude da resposta para
   as cenas/pranchas/SWE) — isso requer reexecução dos brains ou scorer
   por tarefa específica.
2. Réplica local nf4 dos braços `block2_intervene` (12 tarefas × 4 braços
   com os brains vivos) — payloads existem, run não executado.
3. O sqlite de output foi perdido — `rescore_hf_blocks.sqlite` precisa
   ser regenerado para alimentar o writeup com evidência persistida.

---

## 3. PROMPTS PARA HERMES / KILO

Os prompts abaixo estão prontos para serem passados diretamente.

### Prompt Hermes (auditoria profunda de dependências Bion)

```
TAREFA: Auditoria de dependências Bion no omni_worker

Repositório: /content/omni_worker (branch master)
Referência: /content/omnimind-kilombo-sovereign (read-only)

Mapa base: docs/MAPA_PRIMARIO_2026-11-04.md e docs/RELATORIO_CONFIRMACAO_2026-11-04.md

PERGUNTAS A RESPONDER (com evidência de código — paths:linhas):

1. WIRING COMPLETO: trace o caminho completo de uma chamada β→α no
   integration_loop: desde `adapters.collect_sensory()` até
   `bion_bridge.metabolize()` até `loop.py`. O resultado do metabolize
   vai para onde? É consumido por algum outro módulo ou fica em
   `r.metadata["bion"]` sem consumidor?

2. GAPS DE WIRE: O `activation_beta/` menciona bion_bridge nas docstrings
   mas não importa. Verificar se deveria: `attractor.py` constrói
   `BetaElement`? Qual é o data path real de ativações → β → α?

3. BION_PATCHES NÃO PORTADOS: Os 7 arquivos ausentes
   (bion_grid, bion_links, bion_vertex, bion_rsi_modulator,
   integration_wrapper, knowledge_link_extension, ultimate_reality)
   são usados por algum módulo do worker? Algum deles é necessário
   para completar o pipeline β→α real?

4. AFFECT_TRACER SEM BION: `agency/affect_tracer.py` faz a escada L0-L4
   sem nenhum conceito Bion. Deveria passar por β→α para detectar
   projeção/identificação projetiva (Bion) além do léxico? Ou é
   intencional?

5. SOBERANO: Em `/content/omnimind-kilombo-sovereign/src/psychoanalysis/`,
   `bion_rsi_modulator.py` lê `shared_state.json`. Qual é o papel
   desse módulo no soberano e há equivalente no worker?

Formato de saída: relatório markdown em /content/omni_worker/docs/audits/
nomeado BION_DEPENDENCY_AUDIT_2026-11-04.md, com seções por pergunta,
paths:linhas verificados, classificação epistêmica [DADO]/[LIMITE].
```

### Prompt Kilo (estudo profundo rescore HF + writeup)

```
TAREFA: Estudo de Rescore HF blocks + preparação do writeup

Repositório: /content/omni_worker (branch master)
Referência: /content/omnimind-kilombo-sovereign (read-only)

Mapa base: docs/MAPA_PRIMARIO_2026-11-04.md
Relatório: docs/RELATORIO_CONFIRMACAO_2026-11-04.md
Relatório existente: docs/results/rescore_hf_blocks.md (gerado 2026-11-03)
Script: scripts/gemma4_diag_battery/rescore_hf_blocks.py

SITUAÇÃO:
- rescore_hf_blocks.py já rodou (2026-11-03T11:37:12Z) cobrindo 126 records
- O .sqlite de output foi perdido (gitignored)
- O .md de relatório sobreviveu (docs/results/rescore_hf_blocks.md)
- O HF sqlite está em data/hf_gemma4/gemma4_e4b_l4_results.sqlite (presente)

TAREFAS:

1. REGENERAR O SQLITE: Rodar
   HF_E4B_SQLITE=data/hf_gemma4/gemma4_e4b_l4_results.sqlite \
   PYTHONPATH=src python3 scripts/gemma4_diag_battery/rescore_hf_blocks.py
   Verificar se roda sem erros. Se falhar, diagnosticar e corrigir.
   Output esperado: scripts/gemma4_diag_battery/rescore_hf_blocks.sqlite
   + atualização de docs/results/rescore_hf_blocks.md

2. ANÁLISE PROFUNDA block2_intervene: 26 discordâncias (stored=1/worker=0)
   — classificar cada uma: é degeneração real (semantica) ou gate semântico
   (gates=0 porque o modelo recusou/simplificou)? Existe padrão por braço
   (baseline vs thought_floor vs unified_cascade vs verification_gate)?
   Qual braço tem maior taxa de degen real vs gate?

3. ANÁLISE latent_layer_metrics: O sqlite HF tem 1492 linhas de
   latent_layer_metrics (pr_traj, svd_entropy, mps_chi_eff, h_norm por
   camada). Fazer análise descritiva:
   - mps_chi_eff varia por experiment? Por braço?
   - Correlação entre mps_chi_eff baixo e degenerate_flag=1?
   - Camadas com maior variância de h_norm (onde o modelo "trabalha mais")?
   Esta análise alimenta a seção MPS do writeup.

4. WRITEUP: Preencher docs/WRITEUP_ESQUELETO.md (se existir) ou criar
   docs/results/WRITEUP_DRAFT_2026-11-04.md com:
   - Seção "Ablação quantização": NF4 vs BF16, resultado da diag_battery
     (wcst/stroop/nback/igt por modelo), evidência do diag_battery.sqlite
   - Seção "MPS e ativações": bond_dim, eff_rank da hidden_spectral;
     mps_chi_eff do dataset HF; limitação de captura só último passo
   - Seção "block2_intervene": resultados do ponto 2 acima
   Cada claim com fonte [DADO] e path verificado.

Formato: relatório + dados em docs/results/. Sqlite em scripts/gemma4_diag_battery/.
REGRA: sem dados simulados. Se falhar, reportar o erro exato.
```

---

## 4. SUMÁRIO EXECUTIVO PARA O OPERADOR

| Pergunta | Resposta verificada | Evidência |
|----------|--------------------|---------:|
| Bion implementado nos módulos? | **SIM** — portado e wired no integration_loop. Gaps: 7 arquivos bion_patches não portados, affect_tracer sem Bion | código verificado |
| BionAlphaFunction não está no escopo? | **ERRADO** — arquivo existe, importável, usado por bion_bridge | `import` testado ao vivo |
| Rescore 108 HF foi feito? | **SIM** — cobriu 126 records em 2026-11-03. Relatório existe. SQLite perdido (precisa regenerar) | `rescore_hf_blocks.md` presente |
| O que ainda falta no rescore? | Scorer de corretude por tarefa (cenas/SWE), réplica local nf4 block2, sqlite regenerado | [LIMITE] |
| Hermes/Kilo podem trabalhar? | **SIM** — prompts acima estão prontos | — |
