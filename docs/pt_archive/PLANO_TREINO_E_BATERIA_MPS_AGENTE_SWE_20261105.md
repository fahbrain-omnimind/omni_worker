# PLANO EXECUTÁVEL — Treino LoRA + Bateria MPS "por dentro" no Agente SWE (Gemma 4 Developer Agent)

**Data:** 2026-11-05 · **Autor:** Devin (Engenheiro de Treino/Interpretabilidade SWE)
**Escopo:** competição Google Gemma 4 Developer Agent (deadline 2026-12-02, paper 2026-11-12).
**Restrições deste plano:** não executa treinos longos agora; não encerra os brains `:8098`/`:8099`;
não expõe tokens/credenciais. O relatório do agente de regras
(`docs/ESTUDO_REGRAS_GEMMA_AGENT_20261105.md`) **ainda não existe** `[DADO — verificado
17:30 UTC]` — tudo que depende dele está marcado **[HIPÓTESE — depende de ESTUDO_REGRAS]**.

**Estatuto epistêmico:** `[DADO]` medido/verificado nesta VM ou em docs auditados ·
`[DERIVADO]` calculado/deduzido de dados · `[HIPÓTESE]` proposta a validar ·
`[LIMITE]` restrição conhecida · `[INTERPRETAÇÃO]` leitura causal sujeita a revisão.

---

## 0. Inventário verificado (base factual de todo o plano) `[DADO]`

| Item | Valor medido (2026-11-05 ~17:30 UTC) | Fonte |
|---|---|---|
| GPU | A100-SXM4-40GB, 40 960 MiB total, **20 569 MiB livres** | `nvidia-smi` |
| VRAM ocupada | 19 873 MiB — PID 69858 `gemma-4-12B-it` :8098 (~9,6 GB) + PID 69901 `gemma-4-E4B-it` :8099 (~10,2 GB), ambos `--load-4bit` via `erika_torch_server` | `nvidia-smi`, `ps` |
| RAM | **83 GB total / ~73 GB disponíveis** (≠ ~150 GB citado no brief — corrigindo) | `free -g` |
| Disco | `/` overlay 236 GB, **135 GB livres**; `/content/drive` montado, 129 GB livres | `df -h`, `mountpoint` |
| Stack treino | torch 2.11.0+cu130 · transformers **5.22.1** · peft 0.21.2 · accelerate 1.15.0 · bitsandbytes 0.50.2 · datasets 4.8.5 · **trl AUSENTE** | `pip list`, `import trl` → `ModuleNotFoundError` |
| Pythons | `python` 3.13.16 (env principal, serve os brains) · `python3.12` presente · `/root/swe_venv` (py3.12) já tem `swegemma-0.2.11`, `adk_submission-0.2.13`, `adk_eval_core-0.1.0`, `google_adk` | `which`, `ls site-packages` |
| HF auth | `user=fabricioslv` (whoami; token não exibido) | `hf auth whoami` |
| Kaggle quota | **GPU 15,44h restantes de 45h** — refresh **2026-11-07** · TPU 20h/20h | `kaggle quota` |
| Pesos locais | `google/gemma-4-12B-it` + `google/gemma-4-E4B-it` em `/root/.cache/huggingface` (39 GB blobs) | `du`, `ls` |
| Configs | 12B: 48 camadas, hidden 3840, GQA 16/8, vocab 262 144 (`gemma4_unified`) · E4B: 42 camadas, hidden 2560, GQA 8/2 (`gemma4`) | `config.json` no cache HF |
| Bateria existente | `data/basal_vs_modulated_280turns_20261105.sqlite` → tabela `battery_turns`, 280 linhas (70×4: 12B/E4B × BASAL/MODULATED); inclui 24 turnos `swe_competition` + 8 `swe_ood45` | `sqlite3` via Python |
| Piloto SWE+MPS | `data/swe_mps_ablation_20261105.sqlite` → `ablation_turns` (19 linhas), gerado por `scripts/experiments/run_swe_mps_ablation_battery.py` contra OOD-45 real | sqlite + script |
| OOD-45 local | `/root/competition/ood45/tasks.jsonl` = **45 tarefas** + `snapshots/*.tgz` + `repro/` + `tools/` + `wheels/` | `wc -l`, `ls` |
| Submissão atual | `/root/competition/submission/agent.yaml` → `SequentialAgent` analyst→executor→reviewer, modelo único `gemma-4-12b-it-qat-w4a16-ct`, **COMPILE OK** | `agent.yaml`, `RELATORIO_GEMMA_COMPETITION_20261105.md` |
| Telemetria reutilizável | `erika_torch_server.py::_compute_motor_and_mps_telemetry` (l.106–242): `chi_eff_mean/max`, `pr_traj`, `svd_entropy_mean`, `contract_drift`, `ipr_mean`, `morphology_score` + motor (velocity/acc/drift/norm/unique_ratio/degen_flag). Já retorna `telemetry` no JSON de `/v1/chat/completions` (l.743–749) e grava `npz` step-trajectories em `data/monitor/activation_steps/` | leitura do código |

**Fatos do harness que condicionam o desenho** `[DADO — HARNESS_README.md + RELATORIO]`:
scorer oficial = 4×L4, vLLM `tensor_parallel=4`, `max_model_len=32768`,
`tool_call_parser="gemma4"`, `reasoning_parser="gemma4"`; modelo base único por
submissão (`ALLOWED_MODEL_NAMES`, só variantes **QAT w4a16**); multi-LoRA permitido
(`adapters/<name>/`, `max_lora_rank≤128`, `.safetensors`); submissão < 3 GiB;
`swegemma eval --sandbox subprocess` é o caminho local; o harness conecta em
`LiteLlm(model="openai/<model>", api_base="http://127.0.0.1:8000/v1")` e **admite
anexar a um endpoint já ativo** ("fallback LiteLlm num_retries=3 when attaching to
an already-active endpoint") — é o gancho do nosso backend instrumentado.

---

## A. Capacidade de treino

### A.1 O que cabe nesta VM `[DERIVADO]` (memória estimada, calibrar com microbench §A.4)

Contas: base 4-bit NF4 ≈ 0,55–0,65 GB/B-param; bf16 ≈ 2 GB/B-param; LoRA r=16–64
bf16 sobre todas as projeções lineares ≈ 0,05–0,4 GB + otimizador `paged_adamw_8bit`
≈ 2×adapter; ativações com `gradient_checkpointing` ≈ 1,5–4 GB a seq 4096/batch 1.

| Config | VRAM estimada | Cabe nos 20,5 GB livres (brains vivos)? | Cabe sozinha nos 40 GB? |
|---|---|---|---|
| **E4B QLoRA** (4bit, r≤64, seq 4096) | ~6–10 GB | **Sim, com folga** | trivial |
| **E4B LoRA bf16** (pesos ~8,6 GB) | ~12–16 GB | Sim, apertado | trivial |
| **12B QLoRA** (4bit, r≤64, seq 2048–4096, grad-ckpt) | ~13–18 GB | **Borderline** — seq≤2048 ok; 4096 arrisca OOM | **Sim, confortável** |
| **12B LoRA bf16** (pesos ~24–25 GB) | ~30–36 GB | **Não** | Sim, apertado (seq≤4096) |
| **31B** qualquer fine-tune | >40 GB | Não | Não — fora de escopo |

**Restrição operacional** `[LIMITE]`: os brains :8098/:8099 não podem ser derrubados
por este plano. Portanto: (i) treino **E4B QLoRA e 12B QLoRA seq≤2048–4096 cabem na
VRAM livre com os brains vivos**; (ii) 12B LoRA bf16 ou seq>4096 exigem **janela de
manutenção negociada com Fabricio** ou execução no Kaggle/Colab.

**Atenção — mismatch de artefato** `[LIMITE]+[HIPÓTESE]`: o scorer serve variantes
**QAT w4a16 `-ct`**, mas o treino local roda sobre os checkpoints HF `gemma-4-*-it`
(bf16/4bit-bnb). Um adapter treinado em pesos HF e servido sobre pesos QAT-INT4 pode
sofrer shift de distribuição — é exatamente a classe de problema do "bug de LoRA"
sob investigação pelo outro agente. Mitigação: validar o adapter no backend local
4-bit **e** num sweep Kaggle com o scorer real antes de apostar nele
`[HIPÓTESE — depende de ESTUDO_REGRAS]`.

### A.2 Ambiente de treino `[DADO]+[HIPÓTESE]`

- `trl` **não está instalado** `[DADO]`. Criar venv dedicado para não perturbar o env
  que serve os brains:
  ```bash
  python3 -m venv /content/omni_worker/.venv-train
  /content/omni_worker/.venv-train/bin/pip install \
    "transformers==5.22.1" "peft==0.21.2" "accelerate==1.15.0" \
    "bitsandbytes==0.50.2" "datasets==4.8.5" "trl" "flash-attn"  # pin das versões já validadas
  ```
  `[HIPÓTESE]` Se `trl` exigir downgrade de `transformers/peft`, usar `Trainer` puro
  do transformers (SFT manual com `DataCollatorForCompletionOnlyLM`-like) — zero
  dependência nova.

### A.3 Kaggle / Colab retomável `[DADO]+[HIPÓTESE]`

- **Quota** `[DADO]`: GPU **15,44h** até refresh **2026-11-07** → depois volta a 45h.
  TPU 20h intactas (stack TPU-JAX fora do pipeline atual → não contar). Sessões
  Kaggle ≤ ~9–12h/execução `[LIMITE]` → todo treino >6h precisa de checkpoint externo.
- **Receita retomável** `[HIPÓTESE]` (padrão já usado em `VM_SETUP.md` com HF dataset):
  1. Notebook Kaggle com wheelhouse + pacote `fabricioslv/gemma4-dev-agent-competition`
     anexados; `HF_TOKEN` via Kaggle Secrets (nunca em código).
  2. `TrainingArguments(save_steps=100, save_total_limit=3)`; a cada save,
     `huggingface_hub.upload_folder(..., repo_id="fabricioslv/gemma4-train-ckpt",
     repo_type="dataset")` em thread de fundo — ponto de retomada ≤100 steps.
  3. Retomada: `trainer.train(resume_from_checkpoint=<último do HF>)`; notebook
     versionado com `output` descartável — estado real vive no HF dataset.
  4. Colab: `drive.mount('/content/drive')` + `save_dir=/content/drive/MyDrive/gemma4_ckpt`
     como espelho secundário; HF continua sendo a fonte de verdade (Drive é cache).
- **Regra**: um run = um `run_id`; checkpoints nomeados `ckpt/<run_id>/step_N`.

### A.4 Throughput — medir antes de prometer `[DERIVADO]+[HIPÓTESE]`

Estimativas a priori (A100-40GB, QLoRA, grad-ckpt, ga=8, seq 4096) — **ordens de
grandeza, não compromisso** `[DERIVADO]`:

| Config | tok/s estimado | tokens/h | Exemplos/h (média ~4k tok) |
|---|---|---|---|
| E4B QLoRA | 4–10k | ~15–35M | ~4–9k |
| 12B QLoRA | 1,5–4k | ~5–15M | ~1,5–4k |
| Kaggle T4×2 (fp16, sem bf16 nativo) | ~3–8× mais lento | — | usar p/ eval, não p/ treino principal `[INTERPRETAÇÃO]` |

**Script a criar:** `scripts/mps_swe/bench_qlora.py` — 60 steps reais por config
(12B/E4B × seq 2048/4096), mede tok/s, VRAM pico e estabilidade com brains vivos.
30 min de GPU resolvem todas as incertezas da tabela. `[HIPÓTESE]`

**Capacidade planejada** `[DERIVADO]`: alvo LoRA-SFT = 2–5k trajetórias verificadas
× ~4k tok ≈ **8–20M tokens/época** → 1–2 épocas em **~2–6h na A100 local** (12B QLoRA,
brains vivos, seq 2048) ou ~1–2 sessões Kaggle. Volume não é gargalo; **qualidade do
filtro é** (§B.3).

---

## B. Dados de treino permitidos

### B.1 Matriz de fontes `[HIPÓTESE — depende de ESTUDO_REGRAS em todos os itens]`

| Fonte | O que é | Status legal | Observação |
|---|---|---|---|
| **Trajetórias próprias (rejection sampling)** | Rodar nosso agente (BASE) em OOD-45 + tasks derivadas, verificar com testes do próprio repo (repro + F2P + P2P do harness), SFT só nas que passam | `[HIPÓTESE]` — auto-distilação do próprio modelo permitido normalmente; aguardar regras | Já temos toda a infra: `run_swe_mps_ablation_battery.py::verify_snapshot` faz verificação hermética real |
| SWE-Gym (~2,4k trajetórias verificadas) | trajetórias OpenHands/public | `[HIPÓTESE]` | Licença + regra de dados externos da competição pendentes |
| SWE-smith (~50k tasks sintéticas) | tasks geradas c/ testes | `[HIPÓTESE]` | Idem; útil p/ escalar rejection sampling próprio |
| `scottweeden/gemma-4-developer-agent-tool-lora-kit` (Kaggle) | kit oficial-adjacente p/ tool-use LoRA | `[HIPÓTESE]` provável OK (publicado p/ a competição) | Já citado no RELATORIO §6 |
| Destilação de teacher externo (Gemini/Claude/GPT) | — | `[HIPÓTESE]` **assumir PROIBIDO até prova contrária** | Não planejar em cima; se ESTUDO_REGRAS liberar, vira upside |

**Decisão de segurança epistêmica**: até o ESTUDO_REGRAS sair, o plano executável usa
**apenas trajetórias próprias verificadas por teste** (rejection sampling), que é a
fonte de menor risco legal e já produz telemetria MPS de graça durante a geração.

### B.2 Pipeline de geração (scripts a criar)

- `scripts/mps_swe/gen_trajectory_data.py` — para cada task (OOD-45 + fontes
  liberadas): executa o agente BASE no loop instrumentado (§C), verifica patch no
  snapshot isolado (reuso de `verify_snapshot`), e grava `sft_candidates` no SQLite
  com `resolved`, `n_turns`, `n_tool_calls`, telemetria por turno. Critério de ouro:
  `resolved=1 AND patch mínimo AND zero edição em arquivos protegidos`.
- `scripts/mps_swe/build_sft_dataset.py` — converte turnos verificados p/ formato de
  chat Gemma 4 (tags de canal/thought e `tool_call` no formato nativo do parser
  `gemma4` do vLLM — o dataset tem que ensinar o modelo a emitir o formato que o
  scorer parseia, não o nosso formato interno) `[DERIVADO]`. Máscara de loss só em
  tokens assistant (`train_on_prompt=False`).

### B.3 Filtro opcional de trajetórias via sinais MPS `[HIPÓTESE]`

**Evidência de base** `[DADO — AUDITORIA_CONTINUA §(3b)]`: na bateria de 280 turnos,
`degenerate_flag=1` co-ocorre com **colapso de `mps_pr_traj`** — AUC pooled 0,067
(≡ 0,933 invertido), mediana 7,75 vs 14,64; todos os 12 turnos degen com
`PR_traj ≤ 11,64`. IPR separa chassi deterministicamente (AUC=1,000 invertido).

**Proposta** `[HIPÓTESE — braço de ablação pré-registrado, não filtro default]`:
- `dataset_full`: todas as trajetórias `resolved=1`.
- `dataset_mpsfilt`: `resolved=1` **e** nenhum turno com `pr_traj < P10_basal` do
  respectivo chassi/fase (limiar calculado do envelope BASAL do próprio modelo, não
  constante global — o envelope muda por chassi `[DADO]`) **e** `degenerate_flag=0`
  em todos os turnos.
- Hipótese testável: filtrar turnos com trajetória MPS colapsada remove exemplos
  onde o modelo "acertou por template" (perseveração que coincidiu com o fix),
  melhorando generalização. **Risco declarado**: pode só reduzir N sem efeito —
  por isso é braço B da ablação, não o default. Custo: re-treino de 1 config.

---

## C. Desenho da bateria MPS "por dentro" no agente SWE

### C.1 Arquitetura do backend instrumentado

**Fato-chave** `[DADO]`: a telemetria MPS já existe e já sai no HTTP —
`/v1/chat/completions` retorna `telemetry.{motor_layer, mps_layer, step_traj}`
(l.743–749 do `erika_torch_server.py`) e `_emit_step_trajectory` grava `.npz` por
geração. O que falta para o loop de agente SWE é **tool-calling nativo**: o harness
fala OpenAI `tools`/`tool_calls` e o modelo emite a tag especial de tool-call do
Gemma 4 (a que o `tool_call_parser="gemma4"` do vLLM decodifica).

**Duas rotas, em ordem de fidelidade:**

**Rota 1 (primária) — shim OpenAI-compatível instrumentado** `[HIPÓTESE — spike 1–2 dias]`:
`scripts/mps_swe/mps_shim_server.py`, FastAPI em `127.0.0.1:8000` que:
1. Recebe `POST /v1/chat/completions` com `tools`, `messages` (incl. `tool` results)
   exatamente como o LiteLlm do harness envia.
2. Renderiza o prompt no chat-template Gemma 4, gera via HF transformers
   `generate(..., output_hidden_states=True)` (reuso direto de `_generate` +
   `_compute_motor_and_mps_telemetry` do `erika_torch_server`).
3. Parseia a tag de tool-call do Gemma 4 no texto gerado → responde no formato
   OpenAI (`message.tool_calls`, `finish_reason="tool_calls"`); repassa `thought`
   conforme `reasoning_parser` espera.
4. Persiste telemetria + request-id por chamada no SQLite (schema §C.3).
5. Aceita `model="openai/<adapter_name>"` → aplica/desaplica adapter PEFT
   (`model.set_adapter`) para comparar BASE vs LORA **no mesmo processo**.

O harness roda **inalterado**: `swegemma eval --sandbox subprocess ...` contra a
submissão real (`/root/competition/submission`), anexando ao endpoint ativo —
ou seja, medimos o loop *de verdade* (nudges, budgets, SequentialAgent, as 9 tools).
`[HIPÓTESE]` risco: o adapter `LiteLlm` pode exigir campos extras da resposta
(`logprobs`, headers); mitigação = spike curto + fallback Rota 2.

**Rota 2 (fallback) — mini-loop próprio**: estender
`scripts/experiments/run_swe_mps_ablation_battery.py` para multi-turno com as 9
ferramentas (subprocess no snapshot extraído, mesmas truncagens: 5k chars stdout,
150 linhas/10k chars read_file, timeout 300s) e o prompt-template do harness
(`build_agent_prompt`, 7 seções). `[LIMITE]` divergência do harness real — só usar
se a Rota 1 falhar no spike.

### C.2 Desenho experimental

| Eixo | Valores |
|---|---|
| Braços | **BASE**: `gemma-4-12B-it` HF 4-bit, sem adapter, BASAL puro (sem modulação, sem steering — `inrc_operator=None`, T fixa 0,2/top_p 0,9) · **LORA**: idem + adapter treinado (§B) |
| Tarefas | OOD-45 completo (45) — piloto: 5 tasks já usadas no piloto de ablação |
| Modulação | **BASAL puro primeiro** — nenhum braço modulado nesta bateria; MPS é sensor, não atuador |
| Variável por turno | `agent_role` (analyst/executor/reviewer — inferido do evento ADK ou da ordem) · `phase` = próxima tool chamada (`read_file`, `edit_file`, `write_file`, `run_command`, `get_status`, `submit_patch`, graph-tools, `none`) |
| Covariável | `resolved` (Fase-2 hermética) — **só covariável**, nunca endpoint primário |

Ordem fixa e pareada: mesma task, mesma seed-base, BASE→LORA na mesma sessão do
shim (mesmo processo/pesos) para controlar deriva de servidor.

### C.3 SQLite — `data/mps_swe_agent_battery_<AAAAMMDD>.sqlite`

Superset de `battery_turns` (compatível com tooling existente) + campos de agente:

```sql
CREATE TABLE agent_turns (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT NOT NULL,            -- ex: mps2026w46_base_v1
  arm TEXT NOT NULL,               -- BASE | LORA
  model_tag TEXT NOT NULL,         -- gemma-4-12B-it
  weight_variant TEXT NOT NULL,    -- hf-4bit | hf-bf16 | qat-w4a16
  adapter_name TEXT,               -- NULL no braço BASE
  instance_id TEXT NOT NULL, repo TEXT,
  task_turn_idx INTEGER,           -- índice da chamada LLM dentro da task
  agent_role TEXT,                 -- analyst|executor|reviewer|root
  tool_call_name TEXT,             -- tool prevista nesta resposta (ou 'none')
  tool_call_ok INTEGER,            -- parse + execução ok
  nudge INTEGER DEFAULT 0,         -- turno foi nudge de continuação?
  prompt_tokens INTEGER, gen_tokens INTEGER,
  temperature REAL, top_p REAL, latency_s REAL,
  mps_chi_eff_mean REAL, mps_chi_eff_max REAL, mps_pr_traj REAL,
  mps_svd_entropy REAL, mps_contract_drift REAL, mps_ipr_mean REAL,
  mps_morphology_score REAL,
  motor_hidden_norm REAL, motor_velocity_mean REAL, motor_velocity_max REAL,
  motor_acceleration_mean REAL, motor_cosine_drift REAL,
  motor_thinking_chars INTEGER, motor_unique_ratio REAL,
  motor_degenerate_flag INTEGER, motor_action_markers INTEGER,
  npz_file TEXT, response_preview TEXT, error_class TEXT
);
CREATE TABLE task_runs (
  run_id TEXT, arm TEXT, instance_id TEXT, resolved INTEGER,
  n_turns INTEGER, n_tool_calls INTEGER, n_nudges INTEGER,
  patch_bytes INTEGER, wall_s REAL,
  fail_class TEXT,                  -- localization|implementation|gating|budget|harness
  PRIMARY KEY (run_id, arm, instance_id)
);
CREATE TABLE sft_candidates (...);  -- §B.2
CREATE TABLE train_runs (...);      -- run_id, config JSON, dataset, ckpt paths, metrics
```

### C.4 Memória de hidden-states `[DERIVADO]+[LIMITE]`

`generate(output_hidden_states=True)` retém (n_layers+1) × `[1,1,hidden]` por passo:
12B ≈ 49×3840×2 B ≈ **0,38 MB/token** → 4 096 tok ≈ 1,5 GB, 16k tok ≈ 6 GB. Com o
shim em 4-bit na VRAM livre, capar `max_output_tokens` do shim em **4 096** (coerente
com o `thinking_budget` 4 096 do scorer e já suficiente p/ tool-calls) — turns que
excederem são exatamente os que o nudge de truncação trata. `[LIMITE]`

### C.5 Poder estatístico honesto `[DERIVADO]`

- **Unidade de análise primária**: task × braço (agregado = mediana dos turnos por
  fase). n = **45 pares** (tasks casadas BASE↔LORA) → **Wilcoxon signed-rank**:
  menor efeito detectável dz ≈ **0,43** (α=0,05 bicaudal, poder 0,80). Efeitos
  menores serão reportados com CI, sem alegação de significância.
- **Turn-level** (~1–3k turnos/braço): autocorrelação intra-task viola iid → usar só
  descritivamente + modelo misto com intercepto aleatório por task; nunca contar
  turno como unidade independente nos testes.
- **resolved**: 45 tasks → CI95 ±~13–15 p.p. em Δ taxa de resolução →
  **declaradamente subdimensionado**; entra como covariável/estratificador
  (ex.: ΔPR_traj condicionado a resolved=0 vs 1), não como endpoint.
- Métricas primárias pré-registradas: `mps_pr_traj`, `mps_chi_eff_mean`,
  `motor_velocity_mean`; secundárias: restantes MPS/motor. Correção **BH-FDR**
  dentro da família secundária. Bootstrap hierárquico (reamostrar tasks) para CIs.
- Ancoragem na evidência prévia: chassi se separa por IPR (AUC=1,000) e degen por
  `PR_traj` (AUC≈0,93 invertida) — se BASE-vs-LORA produzir |Δ| menores que o efeito
  chassi/degen, o poder real será limitado; reportar tamanhos de efeito, não só p.

### C.6 Scripts a criar (consolidado)

| Path | Papel |
|---|---|
| `scripts/mps_swe/mps_shim_server.py` | §C.1 Rota 1 — endpoint :8000 OpenAI+tools com telemetria |
| `scripts/mps_swe/run_agent_battery.py` | driver: sobe shim → `swegemma eval` por task → coleta → sqlite |
| `scripts/mps_swe/tag_turn_phases.py` | pós-processa `agent_turns`: `agent_role`, `phase`, `nudge`, `fail_class` |
| `scripts/mps_swe/analyze_battery.py` | estatística §C.5 → `docs/RELATORIO_MPS_AGENTE_SWE_<data>.md` |
| `scripts/mps_swe/bench_qlora.py` | §A.4 microbench |
| `scripts/mps_swe/gen_trajectory_data.py` | §B.2 rejection sampling |
| `scripts/mps_swe/build_sft_dataset.py` | §B.2 dataset chat-format |
| `scripts/mps_swe/train_lora.py` | SFT (transformers Trainer + peft; resume checkpoint→HF) |
| `scripts/mps_swe/export_adapter.py` | valida + empacota `adapters/<name>/` (<3 GiB, `.safetensors`) |

---

## D. Cronograma — 4 semanas até 2026-12-02

Hoje = 2026-11-05 (qui). Paper = 2026-11-12. Refresh quota Kaggle = 2026-11-07.

| Semana | Marco | Entregas | Dependências |
|---|---|---|---|
| **S1** (05–12 nov) | Infra + piloto BASAL | `bench_qlora.py` rodado (números reais em §A.4) · shim spike Rota 1 (3 tasks fumando) · venv-train criado · piloto MPS-agente 5 tasks BASE → **insumo do paper (12 nov)** · lida ESTUDO_REGRAS quando sair | **ESTUDO_REGRAS pendente** `[LIMITE]` |
| **S2** (12–19 nov) | Bateria BASE completa + dados | OOD-45 × BASE rodado (bateria MPS por turno) · `gen_trajectory_data` ≥2k trajetórias verificadas · dataset_full + dataset_mpsfilt congelados · LoRA smoke r=16 E4B e 12B (sanity loss↓, adapter salva/carrega) | quota Kaggle refrescada 11-07 |
| **S3** (19–26 nov) | LoRA v1 + bateria LORA | treino 12B-QLoRA r=32 (dataset_full) · bateria MPS LORA pareada (45 tasks) · `analyze_battery.py` → relatório comparativo BASE-vs-LORA · eval Kaggle do adapter no scorer real (valida transferência HF→QAT) | bug-LoRA resolvido no ESTUDO_REGRAS |
| **S4** (26 nov–02 dez) | Consolidação + submissão | variantes (rank/dataset) se houver sinal · sweep final OOD-45 do candidato · `export_adapter` + zip <3 GiB + compile-gate + **submissão final** · relatório MPS final anexado ao paper-2 | folga ≥2 dias p/ re-submit |

### Riscos `[LIMITE]+[HIPÓTESE]`

| Risco | Prob. | Mitigação |
|---|---|---|
| ESTUDO_REGRAS atrasa/proíbe fontes de dados | média | fallback já é o default: só trajetórias próprias verificadas |
| Bug de LoRA (adapter não transfere p/ QAT) | média | S3 valida no scorer real antes de iterar; BASE-puro segue como submissão fallback |
| Shim OpenAI incompatível c/ LiteLlm do harness | baixa-média | Rota 2 (mini-loop) + spike na S1 |
| 12B-QLoRA OOM com brains vivos | média | seq 2048, batch 1, `paged_adamw_8bit`; ou janela negociada c/ Fabricio |
| Hidden-states inflam VRAM em turns longos | baixa | cap 4 096 gen-tokens (§C.4) |
| Quota Kaggle insuficiente p/ eval+treino | média | prioridade: eval no Kaggle, treino na A100 local; TPU não conta |
| Turn-level pseudo-replicação infla "significância" | — | já mitigado no desenho (§C.5): análise em nível de task |
| Paper 11-12 sem dados de agente SWE | baixa | piloto 5-task na S1; senão, paper usa bateria 280-turns já consolidada |

---

## E. O que este plano NÃO faz (declarado)

- Não treina nada agora; não derruba :8098/:8099; não expõe `HF_TOKEN`/Kaggle key.
- Não afirma que LoRA melhora resolução — a bateria mede **estrutura interna (MPS)**
  e trata `resolved` como covariável.
- Não assume legalidade de nenhum dado externo antes do ESTUDO_REGRAS.
- Não promete os números de throughput da tabela A.4 antes do microbench.