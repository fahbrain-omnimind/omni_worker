# Port Task — sovereign → omni_worker (CPU/RAM only)

Você é um agente de desenvolvimento com escopo restrito. Leia a fonte,
escreva o módulo adaptado + testes no worker, rode seus testes.
Sua tarefa define APENAS os arquivos que você pode criar/editar —
não toque em mais nada do repo.

## Regras duras

- Trabalhe SOMENTE nos arquivos listados na sua tarefa (+ seu arquivo
  de teste em `tests/`). Não edite `app.py`, módulos compartilhados,
  nem nada fora do seu escopo — conflitos com trabalho paralelo.
- CPU/RAM apenas: **sem torch, sem GPU, sem CUDA**. numpy/psutil/
  stdlib OK. LLM calls → `omni_coworker.agents._llm.brain_chat[_json]`
  (roles analyst/executor) ou fallback heurístico.
- Persistência quando houver estado: sqlite WAL em
  `Path(os.getenv("OMNI_STATE_DIR","data"))` — padrão dos outros
  módulos (ver `shared_workspace/store.py`, `psychology/scars.py`).
- Malha: publicar eventos via `shared_workspace.bus.publish(topic,
  payload)` com tópico canônico (soul, soma, agency, witness, swap,
  kernel, feedback, mesh, dream, loop) — opcional, fail-open.
- Docstring de módulo NO padrão do worker (ver
  `kernel_daemon/homeostasis.py`): seções "Orquestração runtime /
  Runtime orchestration:", "Arquitetura / Architecture:" (aqui cita
  a fonte portada + diferenças vs original), "Princípios teóricos
  invocados / Theoretical principles:", opcional "Analogia–homologia
  (interpretativo)", e linha pt-BR final.
- Testes herméticos em `tests/test_<seu>.py`: monkeypatch
  `OMNI_STATE_DIR` para tmp_path; sem rede, sem GPU, sem modelos.
  Rode: `/content/omni_node/.venv/bin/python -m pytest
  tests/test_<seu>.py -q` com `PYTHONPATH=/content/omni_worker/src`
  e cwd `/content/omni_worker`. TODOS devem passar.
- Não commite — o revisor (Devin) valida e commita.
- Python 3.14, type hints modernos, estilo compacto do pacote.

## Contexto

- Worker: `/content/omni_worker` (repo ativo), src em `src/omni_coworker/`.
- Fontes: `/content/omnimind-kilombo-sovereign/src/...` (ler, não editar).
- Venv: `/content/omni_node/.venv/bin/python`.
- Estudos de referência com veredictos por arquivo:
  `docs/design/OW-STU-008a_metacognition_lacanian.md` e
  `docs/design/OW-STU-008b_psycho_psychology_narrative.md` — siga-os.
