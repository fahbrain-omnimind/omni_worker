# Estudo OW-STU-008 — Módulos psicanalíticos/cognitivos do sovereign → omni_worker

Você é um agente de estudo (read-only nas fontes). Produza UM documento
markdown em `/content/omni_worker/docs/design/` com o doc_id indicado
na sua tarefa. Não edite nada fora desse arquivo.

## Contexto (verdade operacional)

- Repo ativo (alvo do port): `/content/omni_worker` — worker standalone
  Kaggle/Colab, dual-brain Gemma 4 (analyst 12B :8098, executor E4B :8099),
  API FastAPI :8081. CPU/RAM apenas para módulos novos — **sem torch,
  sem GPU, sem CUDA**. Os dois modelos já ocupam ~19GB de VRAM; todo
  daemon/módulo portado roda em RAM/CPU.
- Já implementado no worker (NÃO re-propor):
  - `src/omni_coworker/shared_workspace/` — bus in-process + sqlite WAL
    + `/mesh/*` (tópicos canônicos: soul, soma, agency, witness, swap,
    kernel, feedback, mesh, dream, loop)
  - `src/omni_coworker/kernel_daemon/` — coletor 60s: tail jsonl
    ativações + /erika/affect + soul/soma → publica `kernel.*`
  - `src/omni_coworker/integration_loop/` — 5 estágios numpy
    (sensory_input→qualia→narrative→meaning_maker→expectation→
    sensory_feedback) + Modulation → `feedback.loop` + `/loop/*`
  - `src/omni_coworker/server/erika_torch_server.py` — servidor Torch
    real dos brains (único lugar com torch)
  - `src/omni_coworker/orchestration/swap_scheduler.py`,
    `src/omni_coworker/store/state_guard.py`, `store/code_index.py`
    (faiss+MiniLM), `soul/` (dodeca + kernel_hooks Rust)
  - Crates Rust compilados: omnimind_kernel_compute, omnimind_metrics,
    omnimind_freud10d (pyo3, já importáveis)
- Referência do que existe no guarda-chuva:
  `/content/omnimind-kilombo-sovereign/src/consciousness/` (267 arqs,
  ~107k linhas) — mapear por nome/estrutura, NÃO ler tudo.
- Lei de docstring do worker (ver `docs/design/DESIGN_BRIEF.md`):
  separar seções "Orquestração runtime", "Arquitetura", "Princípios
  teóricos invocados", "Analogia–homologia (interpretativo)".

## Sua tarefa

Para CADA arquivo .py das pastas atribuídas:

1. **Nome/path** + linhas + estrutura (classes/funções públicas).
2. **O que se amarra**: dependências internas (imports de outros
   módulos sovereign/node), dependências externas (torch/GPU/IBM/
   qdrant/etc.), contratos que consome/produz.
3. **Veredicto candidato**: `PORTAR` / `ADAPTAR` / `DESCARTAR` com
   justificativa de 1-2 linhas (critério: valor real de computação
   vs acoplamento e custo CPU; nada que precise de GPU).
4. **Se portar/adaptar**: para onde vai no worker (novo módulo? merge
   num existente? novo estágio do integration_loop? novo tópico da
   malha? feature do kernel_daemon?) e o que cortar.

Termine com uma **tabela-resumo** (arquivo → veredicto → destino) e
uma seção "Síntese de integração": o que esse corpus adiciona ao que
o worker já tem (shared_workspace/kernel_daemon/integration_loop/
soul/dodeca) — identifique sobreposições (ex.: o sovereign já tem
shared_workspace/integration_loop; o que existe NELES que falta nos
nossos?) e lacunas genuinamente novas (ex.: metacognition traz X que
nenhuma camada atual computa).

Profundidade > velocidade. Pode spawnar sub-agentes se seu CLI
permitir. Cite paths absolutos e linhas nas evidências.
