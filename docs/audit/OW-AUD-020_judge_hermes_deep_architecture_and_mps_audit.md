# OW-AUD-020 — Auditoria Física-Matemática: Arquitetura Agêntica, Camadas do Modelo, MPS e Baterias Empíricas

Juiz Avaliador 3 (Auditoria Física-Matemática). Somente leitura de código/artefatos; sem alteração de produção.

## 1. Inventário de artefatos reais

- `data/monitor/activation_vectors/*.npz`: 128 arquivos (64 por modelo).
  - `google/gemma-4-E4B-it`: 64 arquivos, shape (43, 2560), float16.
  - `google/gemma-4-12B-it`: 64 arquivos, shape (49, 3840), float16.
- `data/monitor/activation_steps/*.npz`: 17 arquivos.
  - 12B: 11 arquivos, traj (29, 49, 3840) típico.
  - E4B: 6 arquivos, traj (36, 43, 2560) típico.
- `data/monitor/erika_torch_activations.jsonl`: 477 linhas, ~1.5MB.
- SQLite: `battery_results.sqlite` (11 runs), `coding_battery.sqlite` (34), `diag_battery.sqlite` (88), `rescore_hf_blocks.sqlite` (126), `supervisor_battery.sqlite` (16).

## 2. O que os dados reais provam matematicamente

### 2.1 Vetores ocultos por camada

- Cada sidecar captura a representação do último token (`h[:, -1, :]`) por camada, empilhada em (n_layers, hidden_dim). Isso é um proxy de estado interno, não Φ causal (OW-MATH-001).
- Variância entre 8 gerações consecutivas por camada (média sobre dims):
  - 12B (K=8, L=49, D=3840): min 0.0729, max 7.656, média 0.7897.
  - E4B (K=8, L=43, D=2560): min 0.0921, max 5.434, média 1.112.
- Norma média por camada varia fortemente (12B: 24.1–283.3; E4B: 50.6–174.9), indicando camadas com amplificação muito desigual — evidência de heterogeneidade de escala interna, não de uniformidade.

### 2.2 Espectral / MPS (hidden_spectral.py)

Execução de `spectral_features()` sobre os sidecars reais:

- `google/gemma-4-12B-it`: eff_rank_mean=2.496, spectral_entropy_mean=0.746, bond_dim_max_mean=59.76, n_layers=49, n_files=8.
- `google/gemma-4-E4B-it`: eff_rank_mean=2.516, spectral_entropy_mean=0.8387, bond_dim_max_mean=40.0, n_layers=43, n_files=8.

Interpretação matemática: effective rank ~2.5 significa que, embora a dimensão oculta seja 2560/3840, o subespaço efetivamente usado nas últimas 8 gerações tem dimensionalidade ~2.5 por camada — colapso severo. Bond dimension ~60 (12B) / 40 (E4B) indica emaranhamento/informação compartilhada não trivial entre partições do vetor, mas o corte é feito sobre um único vetor normalizado (não uma distribuição), então é uma medida estrutural, não causal.

### 2.3 Trajetória passo-a-passo

- 17 sidecars de trajetória; 16 com metadata parcial/ausente (run_id/turn/task vazios em 3 de 17; 12B em 11 arquivos quase todos sem metadata). Somente 1 E4B (stageA_full) carrega task=refactor, turn=0.
- traj shape (n_steps, n_layers, hidden); n_tokens entre 88 e 800. Amostragem a cada `OMNI_ACT_STEP_EVERY` passos + último passo.

### 2.4 Baterias empíricas

Refactor battery (`battery_results.sqlite`, 11 runs):
- Vereditos: broken_patch 7, brain_down 3, gate_blocked 1. Zero `success`.
- diagnosis_ok=1 em 10/11; review_approved=1 em 10/11; smoke_passed somente 4 em 1 run; submitted=0 em todos.
- Conclusão: o pipeline gera diagnóstico/revisão, mas não submete patch válido; falha na etapa de aplicação/smoke.

Coding battery (`coding_battery.sqlite`, 34 casos):
- Vereditos: done 20, no_analyst 14.
- fix_compiles=1 em 10/34; fix_black=1 em 10/34.
- hallucinated: 0 em 12, 1 em 8, None em 14 (sem analista).
- recall médio = 0.8889.
- Conclusão: recall alto, mas taxa de compilação do fix = 29.4% (10/34). Alucinação presente em 8/20 casos com analista.

Diag battery (`diag_battery.sqlite`, 88 linhas, 4 tasks × 2 roles × reps):
- analyst avg score 84.72 (n=44); executor avg 88.29 (n=44).
- degenerate=1 em 13/88 (14.8%).

Rescore HF blocks (`rescore_hf_blocks.sqlite`, 126): compara degenerate armazenado vs worker; campo `agree`/`agree2` permite auditoria de concordância. (Não reexecutado aqui; schema confirmado.)

Supervisor battery (`supervisor_battery.sqlite`, 16): categorias/tracer levels; não analisado em profundidade.

## 3. Insuficiências do protocolo experimental e ajustes recomendados

1. Metadados ausentes: 111/128 sidecars de vetores não têm run_id/turn/task. Sem isso, não é possível vincular vetores a tarefas específicas nem calcular métricas por tarefa. Ajuste: garantir `_capture_cfg` populado (OMNI_ACT_RUN_ID/TURN/TASK) em todas as chamadas de captura, ou gravar no record.

2. Amostragem: `_VEC_EVERY` decima chamadas (`_VEC_COUNT % _VEC_EVERY`), perdendo gerações. Para análise estatística, registrar a taxa de amostragem e o índice global.

3. Trajetória: apenas 17 arquivos, metadata quase sempre vazia; n_tokens variável (88–800) sem normalização de prompt. Ajuste: padronizar prompts/tarefas e registrar run_id/turn/task em todos.

4. Effective rank calculado sobre apenas 8 arquivos por modelo (MAX_FILES=8) e por camada com `m.shape[0] < 2` descartando. Reportar n por camada e intervalos de confiança.

5. Bond dimension: computed on a single normalized vector, not a distribution; threshold `s > s[0]*1e-3` arbitrário. Documentar e testar sensibilidade.

6. Baterias: refactor battery 0/11 sucesso; coding battery 29.4% compilação. Faltam baselines e repetições controladas; rescore mostra necessidade de concordância de degenerate.

7. Sem vinculação entre vetores e resultados de bateria (sem run_id), impossível correlacionar representação interna com sucesso/falha de tarefa.

## 4. Limitações declaradas (REGRA DE INTEGRIDADE)

- Dados são reais coletados em disco (sidecars .npz e .sqlite). Nenhum dado simulado foi gerado ou apresentado.
- Métricas são proxies (effective rank, bond dimension, norma), não Φ causal IIT.
- Não foi possível vincular vetores a tarefas individuais por falta de metadata na maioria dos sidecars.
- Não foi realizada execução de testes de código; apenas inspeção de artefatos.

## 5. Conclusão

Os dados reais sustentam: (a) colapso de dimensionalidade efetiva (~2.5) nas camadas; (b) emaranhamento estrutural não trivial (bond dim 40–60); (c) heterogeneidade de escala entre camadas; (d) baterias mostram recall alto mas baixa taxa de compilação (29.4%) e zero sucesso em refactor. O protocolo precisa de metadata completa e vinculação vetor-tarefa para claims causais.
