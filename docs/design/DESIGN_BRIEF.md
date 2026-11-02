<!-- doc_id: OW-DSN-000 | title: Design Brief — kernel/loop/workspace port | author: devin | requester: artifice-operator | project: omni-agent-coworker (kaggle) | date: 2026-11-02 | status: active -->

# Design Brief — Port do kernel transcendente / integration loop / shared workspace

Contexto operacional para os agentes de estudo (kilo, cline, hermes).

## Repositórios

- **Alvo (escrever propostas aqui)**: `/content/omni_worker` — pacote
  `omni-agent-coworker`, Python 3.14, src layout `src/omni_coworker/`.
  Worker standalone Kaggle: dual-brain Gemma (12B :8098 analyst +
  E4B :8099 executor, ambos nf4 via `server/erika_torch_server.py`),
  API FastAPI :8081, state_guard, swap_scheduler, code index
  all-MiniLM+faiss, crates Rust opcionais compilados via maturin
  (`kernel_hooks`).
- **Fonte (LEITURA-APENAS)**: `/content/omni_node` — node/VM completo
  (mesma linhagem, mais módulos) e `/content/omnimind-kilombo-sovereign`
  — repo primário/origem (docs canônicas, `revisao/A6_integrador/livro_vfinal*.md`,
  `docs/science/`, `docs/mapeamento_genetico_cromossomico_dodecatiade.md`).
- NÃO modificar nada em omni_node nem sovereign. NÃO commitar. NÃO dar push.

## Restrições duras do alvo

1. **CPU/RAM apenas** — os daemons de origem usavam GPU/torch; aqui a GPU
   (L4, 23GB) já carrega os dois brains nf4. Todo o port roda em CPU:
   numpy/polars/Rust. Nada de torch nos módulos novos.
2. **Rust-first quando fizer sentido** — a matriz já existe
   (`omnimind_kernel_compute`, `omnimind_metrics`, `omnimind_freud10d`,
   compilados do omni_node via `scripts/build_kernel.sh`). O desenho
   deve decidir por componente: crate Rust novo (pyo3/maturin) vs
   módulo Python puro, com justificativa (paridade de métricas,
   throughput, manutenibilidade). Não é cópia fiel — é redesign da
   arquitetura para o Kaggle; licença permite (arquitetura publicada).
3. **Feedback mínimo da máquina** — o daemon incorpora a memória de
   produção: ler `data/monitor/erika_torch_activations.jsonl` (já
   emitido pelos brains: prompt/gen tokens, layer norms, attention
   entropy), `/erika/affect`, `/soul/state` (phi/psi/sigma via Rust),
   sonda soma (`/soma/probe`). Alimentar o loop com: entrada, qualidade
   (qualia), narrativa, meaning-making.
4. **Docstrings/teoria** — reescrever de forma técnica e profissional,
   separando explicitamente em seções: **Orquestração runtime** /
   **Arquitetura** / **Princípios teóricos invocados** /
   **Analogia–homologia** (esta última marcada como interpretativa, não
   mecanística). pt-BR + EN conforme o estilo do pacote.
5. **Observação curta** — VM vive ~24h; loops com intervalo de coleta
   curto (30–120s) para produzir telemetria densa aproveitável.
6. **Preservação** — nada destrutivo; propostas em `docs/design/`
   (markdown, header doc_id estilo do repo), sem tocar em src/.

## Entregável de cada agente

Um markdown em `/content/omni_worker/docs/design/` com:

1. **Mapa do módulo fonte**: estrutura, dependências, o que é real vs
   placeholder vs morto; contratos de dados (schemas, tabelas, tópicos).
2. **O que trazer / o que cortar** — com justificativa por componente.
3. **Desenho alvo**: componentes novos em `omni_coworker` (nome do
   módulo, responsabilidade, Rust ou Python, interface pública,
   dependências internas permitidas — sem import circular).
4. **Plano faseado**: P0 (mínimo rodando CPU) → P1 → P2.
5. **Riscos/compat**: métricas históricas citadas quando relevantes;
   fontes privadas (HF `omnimind-retired-*`) se precisar de histórico.

Fontes teóricas de referência (leitura seletiva, não exaustiva):
`omnimind-kilombo-sovereign/revisao/A6_integrador/livro_vfinal_limpo_PT.md`,
`docs/science/RECONSTITUICAO_HISTORICA_DODECATIADE_20260818.md`,
`docs/mapeamento_genetico_cromossomico_dodecatiade.md`, e os READMEs/
DIRECTORY_CONTRACT.yaml encontrados junto aos módulos-fonte.
