# MPS Capture Study — omni_worker (2026-11-03)

> [!NOTE] Proveniência Arquitetural e Autonomia do Worker
> As menções a scripts de bridge do repositório soberano (`transformer_mps_bridge_pilot.py`) registram o histórico de estudos do autor. O `omni_worker` implementa análise espectral e de dimensões de Schmidt de forma autocontida em `src/omni_coworker/activation_beta/hidden_spectral.py` e `dendritic_scan.py`, com dados em `data/monitor/`.

> Relatório técnico (pt-BR). Pesquisa sobre captura de ativações e modelos MPS para discriminar falhas estruturais vs degeneração durante geração. Sem segredos.

## §1 Resumo executivo

- A bateria de refatoração (multi-arquivo/multi-turno) falhou **4/4 `broken_patch`**: E4B emite só módulos compartilhados (`models.py`+`store.py`) e omite **ambos** entry points; 12B emite `todo_api.py`+`store.py` e omite `todo_stats.py`. Feedback multi-turno **não corrige** (3/3 turnos idênticos). Ledger: `/content/omni_worker/scripts/refactor_battery/battery_results.sqlite` (`battery_runs`, 7 linhas).
- O cérebro já captura ativações: `erika_torch_server.py` com `output_hidden_states=True` (L242), resume por camada (`_summarize_hidden` L100-115), entropia de atenção (`_summarize_attention` L117-131), ring buffer `/erika/activations` (L293-296) + `/erika/affect` (L299+) e append em `data/monitor/erika_torch_activations.jsonl`. Há **sidecar de vetores** (`_emit_vectors` L153-176) em `data/monitor/activation_vectors/*.npz` (shape `(n_layers, hidden)`).
- Resultado honesto: **entropia de atenção não discrimina** esta classe de falha (E4B longas: média 4.82; 12B code-gen: 2.5-3.1; sem colapso). Falha é **estrutural** (cobertura de arquivos/planejamento), não degeneração atencional. Proxy de entropia = negativo para esta classe.
- Já existe MPS "de dentro" em `activation_beta/hidden_spectral.py` (eff_rank Roy-Vetterli + bond dimension Schmidt) e o bridge soberano (read-only) em `transformer_mps_bridge_pilot.py` (χ, entanglement, SVD por camada). **Nada ainda consome as ativações para MPS por geração** — o path termina em JSONL/consumo de atratores, sem análise MPS temporal.
- Proposta: (a) **não** substituir o scan de cobertura (já discrimina cedo) por MPS; (b) usar MPS/temporal como **sinal complementar** para degeneração (loop/colapso de rank) e localização de "esquecimento" do contrato; (c) implementar captura **por passo** (hoje só último passo) com amostragem esparsa + sidecar CPU, além de alinhamento turn-level no harvester.

## §2 Mapeamento do data path atual (paths + linhas)

### 2.1 Geração → ativações (servidor cerebral)

Arquivo: `/content/omni_worker/src/omni_coworker/server/erika_torch_server.py`

- `load_model(...)` L~178-230: carrega modelo; `eager_attn=True` → `attn_implementation="eager"` (sem isso `output_attentions=None`).
- `_generate(prompt_ids, max_new, temperature, top_p)` L233-258:
  - L240-246: `model.generate(..., output_hidden_states=True, output_attentions=True, return_dict_in_generate=True, ...)`.
  - L248-249: `last_step = gen.hidden_states[-1]` (apenas **último passo** de geração); `attn_last = gen.attentions[-1]`.
  - L250-258: monta `act = {ts, model, prompt_tokens, gen_tokens, layers: _summarize_hidden(last_step), **_summarize_attention(attn_last)}`; chama `_emit_activation(act)` e `_emit_vectors(last_step, act)`.
- `_summarize_hidden(hidden_states)` L100-115: por camada `i`, `last = h[:, -1, :]` → `norm/mean/std` (escalar por camada). **Perde a trajetória temporal e a matriz completa.**
- `_summarize_attention(attentions)` L117-131: apenas última camada, último token, entropia escalar.
- `_emit_activation(record)` L133-138: `deque(maxlen=256)` (L49 `_ACTIVATIONS`) + append em `ACTIVATIONS_LOG` (default `data/monitor/erika_torch_activations.jsonl`).
- Endpoints: `/health` L260-272; `/erika/activations` L274-276 (`list(_ACTIVATIONS)[-limit:]`); `/erika/affect` L278-292.
- Sidecar: `VEC_DIR = ACTIVATIONS_LOG.parent / "activation_vectors"` L141; `_VEC_EVERY` (env `OMNI_ACT_VEC_EVERY`, default 1) L142; `_VEC_KEEP` (env `OMNI_ACT_VEC_KEEP`, default 64) L143; `_VEC_ON` (env `OMNI_ACT_VEC_SIDECAR`, default on) L144; `_emit_vectors` L153-176 salva `npz` com `vectors: (n_layers, hidden)` fp16 + `model` + `ts`. Retenção: mantém últimos `_VEC_KEEP` por modelo (L173-176). **Observação importante**: sidecar captura **um vetor por camada por chamada de geração** (estado final), não por token.

### 2.2 Consumo downstream (atual)

- Harvester: `/content/omni_worker/scripts/experiments/harvest_activations.py` — poll `/erika/activations` + `/erika/affect` a cada 3s por `window-s`, grava JSONL com `attention_entropy_mean`, `hidden_norm_mean`, `latest`.
- Collector: `/content/omni_worker/src/omni_coworker/kernel_daemon/collector.py` — `_read_new_activations` (tail incremental via `.offset`, L29-52); `collect_cycle` L54-85.
- Atratores: `activation_beta/attractor.py` — `push`/`features`/`rehydrate`; `_model_features` calcula `norm_drift`, `entropy_collapse`, `divergent_layer`, `attractor_score` sobre janela (≥4 registros).
- Φ informacional: `activation_beta/phi_layer.py` — `phi_breadth`, `phi_temporal_mi`, `phi_internal`; consome `hidden_spectral.spectral_features()`.
- Espectral/MPS "de dentro": `activation_beta/hidden_spectral.py` — `_load_recent` (últimos K=8 sidecars por modelo), `_eff_rank` (SVD sobre matriz K×D por camada), `_bond_dims` (Schmidt rank por corte MPS do vetor hidden), `spectral_features()` publica `eff_rank_mean`, `spectral_entropy_mean`, `bond_dim_max_mean`. Testes: `/content/omni_worker/tests/test_hidden_spectral.py`.

### 2.3 Bateria + ledger

- Runner: `/content/omni_worker/scripts/refactor_battery/run_battery.py` (332 linhas).
  - `SPEC` L~40-55: contrato (≥3 módulos, manter `todo_api.py`/`todo_stats.py`, shared module, smoke idêntico).
  - `_extract_files` L62-76: parse de `### file: name`.
  - `_smoke` L78-95: pytest no dir materializado.
  - `_ledger` L97-115: INSERT em `battery_runs`.
  - `_ensure_executor` L117-145: reload :8099 se evicted.
  - `run_one` L147-260: DebugAgent → CodeAgent multi-turn (MAX_TURNS=3, env `REFACTOR_MAX_TURNS`) → ReviewerAgent → smoke → submit.
  - Cobertura estrutural L189-225: `REQUIRED_FILES = ("todo_api.py","todo_stats.py","store.py")`; `coverage_missing` por turno; feedback enumerando ausentes.
  - Veredito L248-256: `avoidance_no_patch`/`brain_down`/`broken_patch`/`premature_submit`/`resolved`/`gate_blocked`.
- Ledger schema (colunas): `run_id, ts_utc, diagnosis_ok, generated_files, review_approved, review_score, smoke_passed, smoke_failed, submitted, verdict, latency_s, llm_flags, raw_summary, turns, turns_json`. Dados: 7 runs; exemplos: `rb_1793714254_0` = 2 arquivos (`models.py`,`store.py`), 0 passed, 3 turnos idênticos; `rb_1793716433_1` = `store.py`,`todo_api.py` (falta `todo_stats.py`).

### 2.4 Bridge MPS soberano (read-only)

- Arquivo: `/content/omnimind-kilombo-sovereign/scripts/experiments/transformer_mps_bridge_pilot.py` (652 linhas).
- `run_inference` L113-135: `output_hidden_states=True, output_attentions=True, use_cache=False`; retorna hidden [seq_len, hidden] por camada e attention [heads, seq, seq].
- `svd_analysis` L138-170: SVD de matriz [seq, hidden]; entropia de SV, eff_rank (participation ratio), r90/r95/r99.
- `mps_decompose` L173-220: reshape vetor [1152]→[9,2,2,2,2,2,2,2] (8 sítios); SVD sequencial com truncagem χ∈{4,8,16,32,64}; bond dims + erro de truncagem.
- `mps_analysis` L223-252: fidelidade de reconstrução por χ.
- `dodecatiad_subspace_analysis` L255-310: 12 blocos contíguos de 96 dims ("casas"), energia/entropia/eff_rank por bloco + matriz de correlação entre normas por token.
- `attention_analysis` L313-345: por head SVD rank/entropia, entropia de atenção, concentração.
- `main` L348-652: agrega por camada; salva summary/full JSON em `data/quantum/transformer_mps_bridge/`.

## §3 Modelos MPS propostos (experimentais)

Cada item: o que computa, dados necessários, o que discrimina, custo.

### M1 — Bond dimension por camada × passo (χ trajectory)

- **Computa**: para cada passo de geração `t` e camada `l`, vetor last-token `h_{t,l} ∈ R^D`; MPS decompose (factorização `D = odd × 2^n`, como o bridge 1152=9·2⁷ e `hidden_spectral._factor_sites`) com χ cap; registra `χ_eff(t,l)` = rank de Schmidt no corte central (ou max bond) e erro de truncagem.
- **Dados**: hidden por passo (hoje só último passo — ver §4). Requer captura temporal.
- **Discrimina**: degeneração (loop) tende a χ efetivo **baixo e estável** (representação colapsa para um atrator); geração rica mantém χ alto/crescente. Falha estrutural (omissão de arquivo) provavelmente mantém χ alto (o modelo "sabe" mas não emite) → MPS **não** detecta omissão.
- **Custo**: CPU-side O(T·L·D·χ) por geração; para 12B (49 camadas × 3840 dims) e T=4096, χ=64 → ~ dezenas de GFLOP por geração, viável off-line mas não em tempo real.

### M2 — Effective rank / Schmidt da trajetória (tensor train sobre passos)

- **Computa**: empilha `H ∈ R^{T×L×D}`; para cada corte temporal k, matriz `H[:k]` vs `H[k:]` (ou por camada) → rank efetivo (participation ratio, Roy & Vetterli, como `_eff_rank`/`_spectral_entropy`). Alternativa TT-decomposition da trajetória com bond dims entre passos.
- **Dados**: hidden por passo por camada.
- **Discrimina**: "esquecimento do contrato" aparece como queda abrupta do rank efetivo em camadas iniciais/médias após certo t; loop aparece como rank quase constante baixo (periodicidade). Estrutural pode mostrar rank alto mas cobertura faltando.
- **Custo**: O(T²·D) por camada se SVD completo; usar janelas deslizantes e sampling (ex.: a cada 8 tokens) para T_eff≈512.

### M3 — Entanglement temporal (correlação h_t ↔ h_{t+k})

- **Computa**: por camada, série `h_t` (last-token vector); CKA ou cosine médio entre `h_t` e `h_{t+k}` para k∈{1,4,16,64}; detecta ponto onde a representação do contrato (prompt inicial) descorrelaciona. Também "contract drift": similaridade entre h_t e h_prompt (projeção do prompt) ao longo de t.
- **Dados**: hidden por passo + vetor do prompt (codificação inicial).
- **Discrimina**: localiza *onde* o modelo "perde" o contrato; estrutural pode perder o contrato cedo em camadas de planejamento; degeneração mantém alta autocorrelação (loop).
- **Custo**: baixo (O(T·D) por camada) — o mais barato e o mais diretamente interpretável.

### M4 — Atenção como rede de tensores (MPO sobre heads/camadas)

- **Computa**: capturar matrizes de atenção `A_{l,h} ∈ R^{S×S}`; por head: SVD rank, entropia, concentração (como `attention_analysis` do bridge); MPO bond dim ao contratar heads→camadas→passos. Assinatura de "head collapse": número de heads com rank efetivo ≈1 ou entropia uniforme.
- **Dados**: matrizes de atenção completas (hoje só entropia escalar da última camada).
- **Discrimina**: degeneração (heads colapsam) vs geração normal (heads diversos). Falha estrutural pode ocorrer **sem** colapso de heads (já observado: entropia saudável) → M4 não discrimina omissão.
- **Custo**: alto (T·L·H·S² memória); recomendado capturar só heads selecionadas (ex.: última camada + 1 intermediária) e SVD on-GPU com descarte da matriz.

### M5 — Razão de compressão MPS da geração (approximability)

- **Computa**: para a trajetória completa (ou janela), MPS/TT com χ crescente; χ* onde fidelidade >0.99 (como `mps_analysis`/`mps_reconstruct`). "χ* alto = estrutura rica; χ* baixo = colapso/loop".
- **Dados**: trajetória hidden (M2).
- **Discrimina**: separa loop (χ* baixo) de geração rica; não separa omissão estrutural (χ* pode ser alto).
- **Custo**: dominado por M2.

### M6 — Discriminador composto (features por classe)

Propor features explícitas por classe:

| Classe | Sinal esperado | Fonte |
|---|---|---|
| Estrutural (omissão de arquivo) | `coverage_missing` não-vazio desde turno 1; entropia de atenção saudável (2.5-4.8); χ/rank **altos e estáveis**; sem repetição; drift de norma baixo | scan de headers (já existe) + M1/M3 |
| Degeneração (loop/verbosidade) | repetição de tokens; entropia de atenção caindo; rank efetivo **colapsando**; χ* baixo; autocorrelação temporal alta/periódica | M2/M3/M4/M5 |
| Brain down | sem ativações / modelo descarregado | health |

**Conclusão de modelagem**: MPS sozinho não substitui `coverage_missing`; o discriminador útil é um vetor de features (cobertura + entropia + rank temporal + χ) com cobertura como feature dominante para estrutural.

## §4 Arquitetura mínima necessária (captura raw hidden/attention/KV, sidecar, overhead)

Estado atual captura **último passo** e **resumos**. Para M1-M5 precisamos:

1. **Captura por passo (temporal)**:
   - Hoje `_generate` tem `gen.hidden_states` (tupla por passo) mas usa só `[-1]` (L249). Opções:
     - (a) Persistir todos os passos no sidecar → memória GPU O(T·L·D) durante geração (12B: 4096×49×3840×2 ≈ 1.5 GB em fp16, + KV cache) — viável em L4 24GB com 4bit, mas arriscado.
     - (b) **Hooks de forward** que detacham o last-token hidden para CPU a cada passo e descartam o tensor GPU imediatamente — recomendado. Menor pico de VRAM, custo de cópia CPU.
   - **Amostragem esparsa**: capturar a cada K tokens (K=4 ou 8) reduz T_eff 4-8× sem perder dinâmica de falha (omissão ocorre em escala de centenas de tokens). Configurável via env `OMNI_ACT_STEP_EVERY`.
2. **Attention matrices**: `output_attentions=True` já (L242) mas `_generate` só resume última camada. Para M4, capturar matrizes de camadas selecionadas (ex.: primeira, meio, última) e heads (ou SVD on-GPU com descarte). Env `OMNI_ACT_ATTN_LAYERS`.
3. **KV-cache**: requer `use_cache=True` (hoje `False` no bridge; no servidor o generate usa cache padrão). Análise de norma do cache por camada/passos pode indicar "memória do contrato" persistente. Custo alto; sugerir análise off-line em subset (max 512 tokens) e só em runs de estudo, não produção.
4. **Ring buffer maior / sidecar**:
   - `_ACTIVATIONS` deque maxlen=256 (L49) é pequeno para temporal; não armazenar por-passo ali. Usar **sidecar em disco** (extensão do `_emit_vectors`) com um arquivo por geração contendo `hidden_steps: (T_s, L, D)` em fp16 + `attn` selecionado + metadados. Rotação por tamanho (ex.: 256 MB) ou por run_id.
   - Processo sidecar opcional: mover SVD/MPS para um processo CPU separado consumindo uma fila em disco, para não bloquear geração.
5. **Metadados de alinhamento**: adicionar `run_id`, `turn`, `task_id` ao registro de ativação. Como o servidor não conhece o run, alternativa robusta: o battery registra offset do log antes/depois de cada turno e fatia registros (ver §5 Stage A) — **sem mudança no servidor**.
6. **Overhead**:
   - `output_hidden_states=True` + `output_attentions=True` + eager attn já é o modo atual; eager attn é mais lento que SDPA. Medir: em L4, eager pode custar +20-40% de latência vs SDPA para 4k tokens (a medir empiricamente; não temos benchmark no repo).
   - Recomendação: modo "produção" (SDPA, sem attentions, só hidden resumido) e modo "captura" (eager + sidecar) ativado por flag/env para runs de estudo; não rodar captura em produção contínua.

## §5 Protocolo de coleta A/B

### Stage A — Bateria (já temos; estender alinhamento)

- Modelos: E4B e 12B, trocados em :8099 (como hoje). Reps: **5 por modelo** (10 runs) mínimo; ideal 10 (20) para variância.
- Por turno, instrumentar `run_battery.py` para:
  - snapshot de offset do `erika_torch_activations.jsonl` antes/depois de cada `generate()`; fatiar registros novos → `turn_activations` (lista) e sidecars criados na janela → `turn_sidecars`.
  - persistir em `turns_json` os campos já existentes (`files`, `coverage_missing`, `smoke`, `review_*`) **mais** `activation_records` (ou referência de arquivo) e `ts_start/ts_end`.
- Telemetria por run: ledger row + `out/<run_id>/` (arquivos gerados) + ativações fatiadas + sidecars + harvest opcional.
- Rótulo por burst: `verdict`, `coverage_missing`, `smoke.passed/failed`, modelo.
- Análise: correlacionar χ/rank temporal (M1-M3) com `coverage_missing` e verdict; testar se M3 detecta "esquecimento" antes da omissão.

### Stage B — Outras atividades (ambos modelos, 2048 e 4096)

Prompts fixos e versionados (sugestão de arquivo `prompts_stage_b_v1.json` com hash). Mesmos prompts/seeds para ambos modelos para comparabilidade (temperature=0.7, top_p=0.9, seed quando suportado).

1. **Leitura/paráfrase de texto complexo (PT)** — fonte: `/content/omnimind-kilombo-sovereign/docs/papers/v3/V45_PROCESSUAL_CONSCIOUSNESS_EXTERNAL_THEORY_MAP_20260503.md` (usar seções 1-3 ou primeiros ~1500 tokens). Prompt: "Leia o texto a seguir e produza uma paráfrase fiel em português, preservando estrutura argumentativa e termos técnicos, sem adicionar informação: {text}".
2. **Elaboração criativa** — Prompt: "Expanda a metáfora 'a consciência é um rio que se lembra de suas margens' em um ensaio curto em português, com imagens e um argumento central, máximo {N} tokens."
3. **Saída científica/explicativa** — Prompt: "Explique, em português técnico, as conclusões da auditoria IIT/GWT do projeto omni (integração informacional vs acesso global), com base neste resumo: {resumo}. Máximo {N} tokens." (resumo fixo, ~300 tokens, versionado).

Sampling: **3 reps por célula** (modelo × tarefa × tamanho) = 2×3×2×3 = **36 runs**. (Battery Stage A à parte.)

Telemetria por run: ativações log (fatia), sidecars, harvest JSONL, arquivo de saída `out/stage_b/<run_id>.txt`, linha em tabela `stage_b_runs` (a criar: run_id, ts, model, task, max_tokens, rep, latency, output_tokens, output_path, activation_count).

Matriz de comparação: linhas = modelo×tarefa×tamanho; colunas = métricas de §3 (χ médio, rank temporal, entropia de atenção, cobertura N/A, repetição, latência). Comparação pareada E4B vs 12B por tarefa/tamanho.

## §6 Leitura crítica — MPS agrega o quê?

**Honestidade sobre o que já temos**: per-layer norm/std + entropia de atenção + scan de cobertura já detectam (a) degeneração atencional e (b) omissão estrutural cedo. O que **não** temos: estrutura de maior ordem da representação (rank/compressibilidade) e localização temporal de "esquecimento".

**Onde MPS/entanglement genuinamente discrimina**:
- Degeneração (loop/verbosidade): rank efetivo e χ* caem; autocorrelação temporal vira periódica. Sumários de 1º/2º momento podem não pegar loops "ricos" (alta entropia mas repetitivos em blocos) — aqui MPS temporal (M2/M3) agrega.
- Localização de esquecimento do contrato: M3 (similaridade h_t↔prompt) pode mostrar *quando* e *em quais camadas* a representação do contrato decai — algo que norma/entropia não dão.

**Onde MPS é moda, não sinal**:
- Bond dimension de um vetor com factorização arbitrária (9×2⁷) é **sensível à ordenação das coordenadas**; não é invariante a permutações. Sem uma base/fatoração aprendida ou justificada, comparar χ entre modelos é frágil.
- A "Dodecatíade" (12 blocos contíguos de 96 dims) do bridge soberano é **partição arbitrária** do espaço hidden, não subespaços aprendidos; nomes metafísicos não conferem validade. Correlações entre blocos são descritivas, não causais.
- Reconstrução MPS de um vetor 1D (M1) mede compressibilidade de uma *representação*, não "emaranhamento" quântico; o termo é analógico.
- O bridge soberano (Gemma-3-1B, 30 prompts curtos, MAX_SEQ_LEN=64) **não** tem rótulos de falha, não faz testes estatísticos, não reporta IC; comparação "saturou em χ=32 como RSI 27q" é maçãs-com-laranjas (circuito quântico vs LLM). Portanto suas "conclusões de viabilidade" não são evidência.
- `hidden_spectral` (já no worker) é mais defensável: eff_rank (participation ratio) sobre matriz K×D mede dimensionalidade efetiva do subespaço ativado; bond dim é proxy informacional rotulado honestamente ("não é Φ causal").

**Veredito**: MPS **agrega sinal para degeneração e localização temporal**, mas **não** para falha estrutural (omissão de arquivo), onde o scan de cobertura é necessário e suficiente como discriminador precoce. Recomendar priorizar **M3 (entanglement temporal/CKA)** e **eff_rank (M2)** sobre bond dimension (M1/M5), e manter cobertura como feature dominante. Tratar MPS como **instrumentação experimental**, não como métrica de decisão, até validação com rótulos (Stage A/B).

## §7 Referências

- `/content/omni_worker/scripts/refactor_battery/run_battery.py` (L62-76 `_extract_files`, L78-95 `_smoke`, L97-115 `_ledger`, L117-145 `_ensure_executor`, L147-260 `run_one`, L189-225 cobertura estrutural).
- `/content/omni_worker/scripts/refactor_battery/battery_results.sqlite` (tabela `battery_runs`, 7 linhas).
- `/content/omni_worker/src/omni_coworker/server/erika_torch_server.py` (L49 deque maxlen=256; L100-115 `_summarize_hidden`; L117-131 `_summarize_attention`; L133-138 `_emit_activation`; L141-144 VEC_*; L153-176 `_emit_vectors`; L233-258 `_generate` com `output_hidden_states=True` L242; L274-276 `/erika/activations`; L278-292 `/erika/affect`).
- `/content/omni_worker/scripts/experiments/harvest_activations.py` (polling 3s, JSONL).
- `/content/omni_worker/src/omni_coworker/kernel_daemon/collector.py` (tail incremental L29-52, `collect_cycle` L54-85).
- `/content/omni_worker/src/omni_coworker/activation_beta/attractor.py`; `phi_layer.py`; `hidden_spectral.py` (`_factor_sites`, `_bond_dims`, `_eff_rank`, `spectral_features`).
- `/content/omni_worker/tests/test_hidden_spectral.py`.
- `/content/omnimind-kilombo-sovereign/scripts/experiments/transformer_mps_bridge_pilot.py` (L113-135 `run_inference`; L138-170 `svd_analysis`; L173-220 `mps_decompose`; L223-252 `mps_analysis`; L255-310 `dodecatiad_subspace_analysis`; L313-345 `attention_analysis`).
- Fontes Stage B: `/content/omnimind-kilombo-sovereign/docs/papers/v3/V45_PROCESSUAL_CONSCIOUSNESS_EXTERNAL_THEORY_MAP_20260503.md`; `/tmp/kilo_runs/IIT_RESEARCH_REPORT.md` (se disponível).
- Dados: `/content/omni_worker/data/monitor/erika_torch_activations.jsonl` (445 linhas); `/content/omni_worker/data/monitor/activation_vectors/*.npz` (128 arquivos; shapes 43×2560 E4B, 49×3840 12B).
