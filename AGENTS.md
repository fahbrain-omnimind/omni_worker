# AGENTS.md — omni_worker

Regras operacionais deste repositório. Todo agente (Devin, Kilo, Hermes,
Codex, etc.) deve obedecer antes de qualquer ação.

## REGRA ZERO — Apuração Técnica Obrigatória (NÃO NEGOCIÁVEL)

- **NINGUÉM SUPÕE, NINGUÉM ADIVINHA, NINGUÉM REINICIA SEM EVIDÊNCIA.**

## REGRA DE INTEGRIDADE — NÃO MENTIR, NÃO OMITIR, NÃO FALSIFICAR (2026-08-16, NÃO NEGOCIÁVEL)

- **É PROIBIDO FABRICAR, SIMULAR OU GERAR "dados empíricos"** — incluindo
  datasets com DOIs de papers reais marcados como "(simulated)" ou
  qualquer variação. Dados gerados por script são SIMULAÇÃO e NUNCA
  podem ser apresentados como evidência empírica, calibração com dados
  reais, ou dataset baixado.
- **NÃO MENTIR**: nenhuma afirmação pode contradizer o que se sabe.
- **NÃO OMITIR**: se um dado é simulado, derivado, estimado ou ausente,
  DIZER explicitamente no mesmo contexto.
- **NÃO FALSIFICAR**: nunca atribuir a uma fonte (paper, DOI, dataset,
  execução) valores ou resultados que ela não contém.
- **Se não sabe → responder "NÃO SEI".** **Se não tem os dados →
  responder "NÃO LOCALIZADO".** Estas respostas são válidas e
  preferíveis a qualquer inferência não verificada.
- Antes de citar um dado como "real" (dataset, medição, execução),
  verificar a origem: arquivo local, banco, log, artefato de execução —
  e declarar a origem na citação.
- Ao encontrar scripts que geram dados simulados com aparência de reais
  (DOIs de papers), REPORTAR imediatamente e marcar o artefato como
  SIMULAÇÃO — nunca usá-lo como evidência.

## Estatuto epistêmico dos documentos

Docs de design/estudo marcam a origem de cada afirmação:
**[DADO]** (medido/verificado com fonte), **[DERIVADO]** (calculado de
dados), **[INTERPRETAÇÃO]**, **[LIMITE]** (restrição conhecida).

## Ambiente operacional

- Repo ativo: `/content/omni_worker` (branch `master`). Editar/commitar aqui.
- Referência read-only: `/content/omnimind-kilombo-sovereign`.
- NÃO trabalhar em `/content/omni_node` (projeto separado).
- NUNCA buscar recursivamente em `/content/drive` (nuvem, trava).
- Testes: `PYTHONPATH=src python -m pytest tests/ -x -q`
- Lint: `ruff check <arquivos>`
- Brains vivos: analyst `gemma-4-12B-it` :8098, executor `gemma-4-E4B-it`
  :8099, API :8081. Estado: `data/` ou `OMNI_STATE_DIR`.
- Produção pública: `OMNI_GATE_FAIL_CLOSED=1`, bind loopback, secrets
  nunca em código/argv (GitHub + GitLab `omni-group535144/omni_worker`,
  `HF_TOKEN` masked+protected; restaurar via `scripts/restore_env.sh`).

## Delegação

- Broad mapping/auditoria bruta → CLIs free (hermes `-z --yolo`, kilo
  `run --auto`), sem timeout arbitrário. Devin apura, integra, valida,
  commita, pushe.
- Commits descritivos; não fazer `push --force`; manter sync
  GitHub+GitLab.
