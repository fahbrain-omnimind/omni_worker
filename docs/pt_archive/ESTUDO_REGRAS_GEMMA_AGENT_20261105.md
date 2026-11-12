# ESTUDO DE REGRAS — Gemma 4 Developer Agent Competition (Kaggle)

Data: 2026-11-05 · Autor: Devin (pesquisa técnica) · Repo: `omni_worker`
Fontes: `/root/competition/harness_reference/HARNESS_README.md` (692 linhas, lido
integralmente), código instalado `swegemma 0.2.11`/`adk-submission 0.2.13` em
`/root/swe_venv`, fóruns oficiais via Kaggle CLI 2.2.5, e avaliação local real em
`/root/competition/eval_e4b_run*/`.

Tags epistêmicas: **[DADO]** medido/verificado · **[DERIVADO]** conclusão lógica
dos dados · **[HIPÓTESE]** plausível mas não confirmado · **[LIMITE]** não
verificável / fora de escopo.

---

## 1. Contrato do harness [DADO]

### Modelos
- Permitidos (QAT, `qat-w4a16-ct`): `gemma-4-31b-it-qat-w4a16-ct`,
  `gemma-4-12b-it-qat-w4a16-ct`, `gemma-4-e4b-it-qat-w4a16-ct`,
  `gemma-4-e2b-it-qat-w4a16-ct`. **Exatamente um** modelo-base único por
  submissão (prefixos de provider são normalizados na validação). Múltiplos
  LoRA adapters sobre o mesmo base são permitidos.
- Contexto máximo: **32.768 tokens**; `max_output_tokens` e
  `thinking_budget` também limitados a 32.768. Scorer: vLLM 0.19.1 com
  parsers `gemma4` (tool + reasoning), `max_model_len=32768`, hardware 4×L4.
- Tempo de avaliação da competição: **12h** (nível competição, não por task).

### LoRA / adapters
- Formato: `adapters/<nome>/` com `adapter_config.json` +
  `adapter_model.safetensors`; nome `^[A-Za-z0-9][A-Za-z0-9._-]*$`;
  rank máximo **128**; agente referencia via `adapter: <nome>`.

### Tools built-in (9)
`run_command`, `read_file`, `edit_file`, `write_file`, `submit_patch`,
`get_status`, `get_code_neighbors`, `search_similar_code`,
`get_code_subgraph`. `submit_patch` e `get_status` são gratuitas;
`submit_patch` encerra o loop. `read_file`: linhas 1-indexed inclusivas,
cap 150 linhas / 10.000 chars. `edit_file`: exige `filepath`, `old_string`,
`new_string` (opcional `allow_multiple`); matching exato+flexível+regex;
rejeita arquivo vazio, `old_string` vazio ou multi-match sem flag.
Paths são relativos ao workspace e rejeitam `..`. Tools de grafo exigem
dados de grafo/embedding e podem retornar erro quando indisponíveis.

### YAML / `!include`
- `!include` resolve relativo ao diretório do YAML que inclui; `..` bloqueado.
  Prompts de `sub_agents/*.yaml` devem ficar em `sub_agents/prompts/`.

### Limites do pacote (código `swegemma`)
- Unpacked: **< 3 GiB**; extensões `.yaml .yml .md .txt .py .json .safetensors`;
  YAML ≤ 50 MB; ≤ 10.000 arquivos; ≤ 1.000 YAMLs; ≤ 1.000 skills;
  ≤ 500 agentes; profundidade de sub-agentes ≤ 50; loop máx. 500 iterações;
  instrução ≤ 1M chars (total 10M). Defaults de geração:
  `max_output_tokens 16384`, `thinking_budget 4096`.

### Sandbox / verificação
- Docker (oficial): `network_mode=none`, 4 GiB RAM, 2 vCPU, `/workspace`;
  containers separados e limpos para fase agente e fase de verificação.
  Backend `subprocess` existe para eval local (usado aqui).
- Extração do patch: `git add -N . && git diff HEAD` — **arquivos novos
  entram no patch** (risco: arquivos auxiliares vazam). Arquivos de teste e
  `pytest.ini`/`conftest.py` criados pelo harness são protegidos.
- Duas fases: (A) agente gera patch; (B) patch aplicado e `pytest` hermético,
  timeout de verificação fixo ~300s.

### `eval_config.yaml`
- `max_time_minutes`: wall-clock da sessão (default 60). `max_tool_calls`:
  **compartilhado pelo SequentialAgent inteiro e pelos nudge-restarts**.
  `max_turns`: budget de turnos LLM. `timeout_seconds`: por comando, não
  sessão. Nudges de continuação: até 3 antes de declarar não-submissão.

---

## 2. Auditoria da submissão (`/root/competition/submission`) [DADO]

Estrutura: `agent.yaml` (SequentialAgent `omni_pipeline`) → `analyst` →
`executor` → `reviewer`; prompts via `!include sub_agents/prompts/*.md`;
`eval_config.yaml`; `README.md`. Somente `.yaml`/`.md`, ~12,5 KB unpacked,
zip ~9 KB — muito abaixo de qualquer limite. Sem adapters.

| Item | Resultado |
|---|---|
| Modelo único | ✅ `gemma-4-12b-it-qat-w4a16-ct` em todos os 3 agentes |
| Modelo permitido | ✅ está na lista QAT |
| `!include` paths | ✅ `sub_agents/prompts/*.md`, sem `..` |
| Tools | ✅ todas as 9 declarações ∈ registry; `submit_patch` só no reviewer |
| `generate_content_config` | ✅ temps 0.1/0.2/0.0 ≥ 0; outputs 8k/16k/8k e thinking 4096 ≤ 32768 |
| `SequentialAgent` root | ✅ sem `model`/`instruction` (correto) |
| `eval_config` | ✅ chaves reconhecidas (45min/100calls/200turns/300s) |
| Compilação declarativa | ✅ testada anteriormente com sucesso |

**Falha de configuração encontrada empiricamente (ver §5):**
`executor.max_output_tokens=16384` implica que, no contexto de 32768 do
scorer, o executor só tem **~16k tokens de headroom de input** — e a sessão
é compartilhada entre os três sub-agentes (o histórico do analyst, incluindo
dumps de arquivos, entra no prompt do executor). Medimos overflow já com
input ≥ 16.385 tokens em contexto de 24.576. [DERIVADO] o mesmo teto pode
estourar no scorer quando a análise acumular > ~16k tokens antes/durante o
executor — risco real, não teórico.

---

## 3. Fóruns oficiais (Kaggle CLI, `competitions topics`) [DADO/LIMITE]

Dump em `/root/competition/forum_dump_20261105.txt` (20 tópicos, JSON
completo). Destaques:

- **Destilação de LLMs externos** (tópico 742807): resposta do organizador é
  **condicional** — depende dos termos de licença do modelo professor e das
  regras da competição. Não é permissão irrestrita nem proibição categórica.
  [DERIVADO] destilação é zona cinzenta: exigir compliance de licença.
- **LoRA e score zero** (755677, 755611): há relato comunitário de score
  **não-zero** com LoRA → zero não prova ban universal. Falhas relatadas
  apontam timeout/empacotamento/compatibilidade de backend. [LIMITE] não
  encontramos confirmação oficial de que todos os bugs de LoRA foram
  corrigidos.
- **"Where 76% of a 300-second agent budget goes"** (755291): auditoria
  comunitária mostra decodificação dominada por re-leitura de arquivos,
  truncamento de 150 linhas e spikes de prefill — motiva prompts que evitam
  re-reads e payloads grandes.
- **Bug de serialização `edit_file`** (756051): modelo emite `edit_file` sem
  `old_string` repetidamente — problema do modelo/parser, reportado.
- **Loop infinito em argumento array** (753973): parser de tool pode travar
  em argumento do tipo array — risco de timeout/estouro de budget.
- **Enviar tasks públicas a provider hospedado** (755542): suporte
  comunitário, mas **sem decisão oficial autoritativa** localizada no dump.
  [LIMITE] tratar como risco de regra.
- **Fila/pending** (747519, 756044): atrasos ~33h+, limites de pending
  bloqueiam novas submissões; "Notebook Timeout" reportado. [DERIVADO] a
  janela de 12h + fila significa que cada submissão pode ocupar > 1 dia.
- Outros: falhas de ambiente em tasks públicas (unsolvable por ambiente),
  bugs de compactação, duplicação de contexto — riscos externos à submissão.

---

## 4. Submissões existentes (CLI) [DADO/LIMITE]

- `kaggle competitions submissions gemma-4-developer-agent` → **"No
  submissions found"**.
- `kaggle competitions submissions gemma-4-developer-agent-paper` → **"No
  submissions found"**.
- Conta autenticada com `userHasEntered=True` nos dois slugs.
- **[LIMITE]** Não existe comando documentado no CLI para listar
  writeups/hackathon submissions do paper track (`submissions`,
  `team-submissions`, `pages`, `topics` não cobrem writeups). "No
  submissions found" no paper track **não prova** ausência de writeup —
  writeups podem residir em outra superfície (página de discussão/artigo do
  Kaggle) fora da API de submissions. Não contornamos autenticação.

---

## 5. Avaliação local REAL — Gemma E4B QAT no OOD45 [DADO]

Infraestrutura reconstruída do zero (o venv não tinha vLLM):
- Instalado `vllm 0.19.1` do wheelhouse; stack alinhado ao scorer
  (`transformers 5.13.1`, `tokenizers 0.22.2`, `google-adk 1.36.1`,
  `litellm 1.83.14` — dois conflitos de versão resolvidos:
  `AmbiguousGlobalPerLayerAttributeError` com transformers 5.22 e
  `CacheableResult` com litellm 1.108/mcp 1.30).
- Checkpoint E4B QAT (11,5 GB, multimodal) servido text-only via
  `--hf-overrides Gemma4ForCausalLM`, parsers `gemma4`,
  `--gpu-memory-utilization 0.30` (≤ 0.30 conforme exigido), `enforce_eager`,
  `max_num_batched_tokens 2048`, `max_model_len` 24576 (único que coube —
  KV cache 2,65 GiB ≈ 28.9k tokens). Brains :8098/:8099 intactos.
- Driver `/root/competition/run_ood_eval.py` (usa `ood45_harness` com
  `wheels_dir` por repo, `--sandbox subprocess`), submissão variante
  `/root/competition/submission_e4b` (única diferença: modelo E4B;
  na run5 também `max_output_tokens` 4096 nos 3 agentes, marcado como
  variante reduzida — NÃO é a submissão oficial).

### Resultados (subconjunto de 2 tasks; NÃO representa o OOD45 inteiro)

| Run | ctx | task | resultado | duração | modo de falha |
|---|---|---|---|---|---|
| run2 | 8192 | apprise_1747 | 0/1 | 9,9s | ContextWindowExceeded (8192 out + ≥8.193 in > 8192) — infra |
| run2 | 8192 | feast_6859 | 0/1 | 20s | idem |
| run3 | 16384 | apprise_1747 | 0/1 | 255s | ContextWindowExceeded (16.384 out + ≥8.193 in > 16384) — config |
| run4 | 24576 | apprise_1747 | 0/1 | 204s | ContextWindowExceeded (8.192 out + ≥16.385 in > 24576) — config |
| run5* | 24576 | apprise_1747 | 0/1 | 477s | pipeline completo, **0 tool calls de edição**, sem `submit_patch`, nudges esgotados; reviewer alucinou "verificado" |
| run5* | 24576 | feast_6859 | 0/1 | 1.236s | executor fez ~10× `edit_file` reais — **todas FileEditError `old_string not found`**; reviewer alucinou write_file bem-sucedido; sem `submit_patch` |

\* run5 = variante com `max_output_tokens` 4096 (necessário p/ caber no ctx local).

**pass@1 / resolution rate: 0/2 (0%)** no subconjunto medido — resultado
honesto, com artefatos em `/root/competition/eval_e4b_run*/`.

### Modos de falha medidos
1. **[DADO] Estouro de contexto estrutural**: `max_output_tokens` alto +
   sessão compartilhada → cada LLM-call exige `input + max_out ≤ max_len`;
   com output 16.384 o executor fica com ≤16k de input no scorer — o analyst
   sozinho já enche isso lendo arquivos. **[DERIVADO] no scorer (32k) a
   mesma arquitetura pode falhar identicamente** assim que o histórico
   passar de ~16k tokens.
2. **[DADO] Conclusão prematura/alucinação de verificação** (E4B): reviewer
   declara "fix implementado e verificado" sem `edit_file`/`submit_patch` —
   confirma o comentário no `agent.yaml` sobre E4B submeter cedo; aqui ele
   "conclui" cedo sem patch.
3. **[DADO] `edit_file` `old_string not found` em loop**: 10 falhas
   consecutivas no feast_6859 (o modelo suspeitou de escape de `\` e
   indentação) — mesmo sintoma dos tópicos oficiais; o agente não tem
   estratégia de fallback (`write_file` reescrevendo o arquivo, por ex.).
4. **[DADO] Ambiente**: `pytest` ausente no sandbox do apprise (relato do
   próprio agente) — falhas de ambiente em tasks públicas também foram
   reportadas nos fóruns.
5. Infra local: `--cpu-offload-gb` incompatível com vLLM 0.19.1
   (assert `uva.cpu_offload_gb == 0` na reinit do input batch) — não usar.

---

## 6. Permitido / proibido / arriscado

**Permitido [DADO]:** os 4 modelos QAT; um base model; múltiplos LoRA
(rank ≤128) sobre o mesmo base; tools built-in; `!include` sem `..`;
declarative YAML; budgets configuráveis em `eval_config.yaml`.

**Proibido/imposto pelo contrato [DADO]:** mais de um modelo-base; paths
`..`; editar arquivos protegidos (testes/harness); rede no sandbox oficial;
exceder 3 GiB/32k ctx/12h.

**Zona cinzenta [DERIVADO/LIMITE]:** destilação (depende de licença do
teacher); enviar tasks públicas a provider hospedado (sem decisão oficial);
LoRA funciona mas com falhas reportadas não confirmadas como resolvidas.

---

## 7. Recomendações de ajuste na submissão

1. **[DERIVADO] Reduzir `max_output_tokens` do executor** (16.384 → ~8.192 ou
   6.144): libera ~8k de headroom de input no ctx 32k e reduz o risco de
   ContextWindowExceeded medido na §5. Custo: respostas de edição mais
   curtas — mitigável pedindo edits incrementais no prompt.
2. **[DERIVADO] Isolar contexto por sub-agente** (ou encurtar histórico):
   a sessão compartilhada vaza os dumps do analyst para o executor/reviewer.
   Opções: instruir o analyst a emitir relatório compacto sem blocos de
   código grandes; considerar transferência explícita via `output_key` com
   contexto isolado (AgentTool/`skip_summarization`) se o harness suportar.
3. **[DERIVADO] Prompt do executor com fallback explícito de edição**:
   "se `edit_file` falhar 2× com `old_string not found`, re-ler o trecho exato
   com `read_file` e, persistindo, reescrever o arquivo com `write_file`" —
   ataca o loop de FileEditError medido (10 falhas seguidas).
4. **[DERIVADO] Prompt do reviewer endurecido**: exigir `run_command` de
   teste real e `get_status`/diff antes de `submit_patch`; proibir concluir
   "verificado" sem saída de teste observada — combate a alucinação de
   conclusão medida.
5. **[DERIVADO] Prompts: evitar re-reads** — guardar conteúdo já lido, usar
   `start_line`/`end_line` explícitos (auditoria do fórum: re-leitura domina
   o budget de decode).
6. **[HIPÓTESE] Manter 12B como base**: E4B confirmou o modo de falha de
   conclusão prematura (0 patches reais em 2 tasks); 31B pode estourar a
   janela/VRAM do scorer. [LIMITE] não medimos 12B localmente (não coube).
7. **[DERIVADO] Cuidado com arquivos novos**: `git add -N` inclui untracked
   no patch — instruir o executor a não criar arquivos auxiliares
   (scratch, logs) no workspace.
8. **[DERIVADO] LoRA só após baseline medido**: com evidência comunitária de
   score-zero e bugs de backend, só treinar/adicionar adapter depois de um
   baseline estável e com validação de empacotamento local.
9. **[DERIVADO] Não enviar nada sem baseline E2E**: primeiro objetivo é um
   run que produza `submit_patch` real com patch não-vazio; hoje temos 0.

---

## 8. Lacunas honestas

- [LIMITE] Não avaliamos o modelo 12B declarado (VRAM) — resultados são
  E4B; [DERIVADO] modos de falha 1, 3 e 4 são agnósticos de modelo, o 2 é
  provavelmente pior no E4B.
- [LIMITE] Subconjunto de 2/45 tasks; budgets reduzidos na run5.
- [LIMITE] Scorer usa 4×L4/32k/docker — local foi A100/24.5k/subprocess.
- [LIMITE] Paper track: impossível listar writeups via CLI documentada.
