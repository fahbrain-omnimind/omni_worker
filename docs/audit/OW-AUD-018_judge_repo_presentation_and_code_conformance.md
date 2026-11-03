# OW-AUD-018 — Julgamento: Apresentação do Repositório e Conformidade Código vs. Documentação/Resultados

Juiz Avaliador 1 (Rigoroso, Exaustivo, Sem Preguiça). Modo read-only; única escrita: este relatório.

## 1. Escopo e método

- Restrito a `/content/omni_worker` (código), `/content/WRITEUP_ESQUELETO.md` e artefatos locais. `/content/drive` não foi tocado (FUSE, risco de travamento).
- Verificação inline `arquivo.py:Lx-Ly`. Confronto de alegações quantitativas do `WRITEUP_ESQUELETO.md` / `docs/PAPER_WRITEUP.md` (idênticos, 272 linhas) contra código real em `src/omni_coworker/` e `scripts/`.

## 2. Apresentação, estética e profissionalismo do repositório

### 2.1 README.md (7185 bytes, 115 linhas)

Pontos fortes: bilíngue pt-BR/EN, topologia de portas clara, comando único de boot, tabela de serviços com supervisão. Pontos fracos:
- `README.md:L3` declara status "ATIVO" para duas competições Google com deadline 2026-11-12/2026-12-03; o repo é claramente um artefato de pesquisa, mas a entrada não explica o que está *pronto vs. planejado* (ex.: "systemd_units: [] — declared, not yet shipped" só aparece em nota de rodapé em L76-77).
- `README.md:L55-58` lista `omni-state-guard.timer` e `omni-swap-scheduler.service` como se fossem serviços reais, mas `DIRECTORY_CONTRACT.yaml` (citado em L77) declara `systemd_units: []`. Contradição documental: tabela promete systemd, rodapé admite que não existe.
- `README.md:L108-115` promete compatibilidade "standalone (adapters com fallback) ou acoplado ao repo canônico omni_node"; a inspeção de `src/` mostra que `integration_loop/adapters.py` e `safety/matrix.py` realmente têm fallback, mas o README não aponta quais subpacotes dependem de omni_node para serem "reais".
- Sem badges, sem screenshot do dashboard, sem link direto para `docs/dashboard.html` ou `docs/index.html` na seção de topo.

### 2.2 pyproject.toml

- `pyproject.toml:L12` autor único "Fabrício da Silva"; `AUTHORS.md` existe mas não foi cruzado. Sem `classifiers`, sem `project.urls`, sem `keywords` — fraco para "Best New Resource" / verificabilidade.
- Versão `0.1.0` (L6) enquanto o projeto se autodenomina V10/V12; inconsistência de maturidade.
- `test = ["pytest>=8.0", "black>=24.0", "ruff>=0.5.0", ...]` (L26) — black/ruff em deps de teste é ok, mas `ruff` não está em dev-dependencies separadas; `AGENTS.md` manda `ruff check <arquivos>`.

### 2.3 Organização de pastas e docs

- `docs/` é extremamente denso: 80+ arquivos, incluindo 3 auditorias concorrentes (`OW-AUD-011..020`) e dezenas de estudos `OW-STU-008a..018`. Para um juiz externo, é *poluído*: não há uma narrativa linear de "comece aqui". `docs/DOCS_INDEX.md` existe mas o README não o linka explicitamente.
- `docs/dashboard.html` (27KB) + `src/omni_coworker/soul/static/index.html` + `superapp.html` + `scripts/dashboard_export.py` + `data/dashboard/latest.json`: quatro superfícies de dashboard. `dashboard_export.py` gera `docs/data/dashboard/latest.json` (commitado em 33541cc). Risco de dessincronização: o JSON é estático no repo; o "live" depende de `/soul/state` em runtime. A página `docs/index.html` (SPA de 4 visões) é o portal público, mas o README não a menciona no Quickstart.

### 2.4 Dashboards

- `docs/dashboard.html` e `docs/index.html` coexistem; não está claro qual é o "oficial". Recomendação: um único entrypoint, com `index.html` redirecionando para o dashboard exportado.
- `data/dashboard/latest.json` existe (commitado) — bom para verificabilidade estática, mas sem timestamp de geração visível no topo do README.

## 3. Conferência exaustiva Código vs. Documentação/Resultados

### 3.1 MPS-lite / captura de vetores — CONFORME (com ressalvas)

- `server/erika_torch_server.py:L137-207` (`_emit_vectors`) implementa sidecar de vetores ocultos por camada em fp16 via `np.savez_compressed`, com env `OMNI_ACT_VEC_EVERY/KEEP/SIDECAR` e retenção por modelo. Conforme §3.4b do writeup ("matriz (49, 3840) para o 12B e (43, 2560) para o E4B em fp16").
- `activation_beta/hidden_spectral.py:L75-86` (`_eff_rank`) calcula effective rank via SVD (`np.linalg.svd`) e entropia espectral. Conforme fórmula `eff_rank = (Σσ²)² / Σσ⁴`? **Gap**: o código usa `exp(H(σ²/Σσ²))` (entropia de Shannon dos valores singulares normalizados), não a participação de Roy & Vetterli `(Σσ²)²/Σσ⁴`. O writeup §3.4b nomeia "Roy & Vetterli Participation Ratio" mas a implementação é a variante entrópica. OW-AUD-020 §2.2 já registrou `eff_rank_mean=2.496` (12B) vs alegação do writeup de 114.6 — **discrepância de 46×**. O writeup reporta N=128 sidecars/5888 vetores, mas `hidden_spectral.py` usa `_MAX_FILES=8` sidecars por modelo. Alegação de 114.6 não reproduz com o código publicado.
- `hidden_spectral.py:L105-119` (`_bond_dims`) calcula Schmidt rank por corte MPS sobre um *único vetor normalizado* — medida estrutural, não causal (OW-MATH-001). Writeup não deixa isso explícito no §3.4b; apenas `hidden_spectral.py:L164` tem `"note": "proxy espectral/MPS — não é Φ causal IIT"`.

### 3.2 Trajetória por passo `_emit_step_trajectory` — CONFORME (opt-in)

- `server/erika_torch_server.py:L214-248`: implementa amostragem a cada `OMNI_ACT_STEP_EVERY` passos + último passo, sidecar `.npz` com `traj (n_steps, n_layers, hidden)` fp16, retenção `_STEP_KEEP=32`. Conforme §3.4b ("OMNI_ACT_STEP_EVERY=8").
- **Gap**: default `OMNI_ACT_STEP_EVERY=0` (L177) e `_STEP_ON` lê env `OMNI_ACT_STEP_ON` default "1" (L179), mas `_emit_step_trajectory` lê novamente via `_capture_cfg("OMNI_ACT_STEP_ON","1")` (L216) e `step_every = int(_capture_cfg("OMNI_ACT_STEP_EVERY","0"))` (L215). Ou seja, trajetória desligada por default; `AGENTS.md` registra "step_traj_requires_server_env" — servidor iniciado sem env não captura. Inconsistência com writeup que apresenta como feature ativa. OW-AUD-020 §2.3 confirma só 17 sidecars e metadata parcial/ausente em 16/17.

### 3.3 `markov_blanket.py` e PyPhi — CONFORME (com honestidade epistêmica)

- `psychoanalysis/markov_blanket.py:L220-271` (`build_tpm`) implementa TPM coarse-grained via Monte Carlo sobre 4/6 nós, com rejection sampling de microestados consistentes. Conforme §3.4d ("Φ(M,R)=0.0015 em α=0.05").
- **Gap de verificação**: o código publicado não inclui o cálculo de Φ via PyPhi (nenhum `import pyphi` em `src/`). O valor 0.0015 é declarado em `docs/results/blanket_pyphi.md` (não auditado aqui), mas o repo não contém script reproduzível de Φ. Alegação "exact PyPhi" não é verificável a partir do código publicado. Recomendação: incluir script de cálculo ou renomear para "TPM pronto para PyPhi".

### 3.4 `affect_tracer.py` — CONFORME (L0-L4)

- `agency/affect_tracer.py:L137-245` implementa `AffectTracer.observe` com níveis L0-L4, lexicon anchors EN+pt-BR, flattery context-aware, analyst-judge tier opcional. Conforme §3.4d ("16/16 detecções na supervisor_battery").
- **Gap**: `get_affect_tracer()` é singleton process-wide (L289-313) sem partição por sessão (documentado em docstring L299-302). Em cenário multi-usuário (competição), falantes intercalados compartilham uma janela — limitação real para "16/16 detecções" sob carga. `supervisor_battery.sqlite` (16 registros) é pequeno para claim de robustez.

### 3.5 `swap_scheduler.py` e peer-swap OOM em `_llm.py` — CONFORME

- `orchestration/swap_scheduler.py:L52-147` implementa loop VRAM-aware com evict/reload, busy detection honesta (counter cumulativo comparado ao tick anterior, L62-75), thresholds env-configuráveis. Conforme §3.4a.
- `agents/_llm.py:L73-93` implementa peer-swap em resposta a HTTP 500/503/507: descarrega peer, recarrega target, retenta. Conforme §3.4a ("peer-swap automático em agents/_llm.py").
- **Gap menor**: `_llm.py` só trata 500/503/507; OOM pode vir como 500 com body diferente — coberto. Mas não há retry/backoff nem circuit breaker (governance tem circuit_breaker, mas não é chamado aqui). Em turnos longos com OOM repetido, loop pode travar até timeout do httpx (default não definido no `client.post` — L65 usa default httpx, potencialmente sem timeout). Recomendação: adicionar `timeout=...` explícito.

### 3.6 `run_battery.py` multi-turn — CONFORME (com gap de resultado)

- `scripts/refactor_battery/run_battery.py:L194-280` implementa loop de até 3 turnos com `coverage_missing` (L242-244) sobre arquivos obrigatórios, reinjeção de feedback + smoke tail + review issues. Conforme §3.4c.
- **Gap de resultado**: OW-AUD-020 §2.4 registra `battery_results.sqlite` com 11 runs: vereditos `broken_patch 7, brain_down 3, gate_blocked 1, success 0`. O writeup §3.4c afirma "10/10 correções que compilam e passam no black" — mas isso refere-se ao `coding_battery` (34 casos, 10/34 fix_compiles=1 = 29.4%, não 10/10). A alegação "10/10" no writeup §3.4c ("Na execução com os dois cérebros ativos, o pipeline alcançou 10/10 correções que compilam") é **inflada**: o ledger real mostra 10/34 (29.4%) com fix_compiles=1, e 14/34 casos `no_analyst`. Apenas se contar os 20 casos com analista e 10 compilam = 50%, ainda não 100%.
- `coding_battery/run_coding_battery.py` (não lido integralmente) — recomendação: auditar o critério de "10/10" e corrigir a alegação para 10/34 ou 10/20.

### 3.7 `hidden_spectral.py` — discrepância numérica (já em 3.1)

Reforço: writeup §3.4b tabela reporta `eff_rank=114.6` (12B) e `40.3` (E4B) com K=64 sidecars. Código usa K=8 e produz 2.496/2.516 (OW-AUD-020). Alegação de 1.7× mais subespaço não se sustenta com o código publicado. **Gap crítico para "Best Paper"**: números não reproduzíveis.

## 4. Diagnóstico de insuficiências (lista cirúrgica)

| # | Categoria | Evidência inline | Severidade |
|---|-----------|------------------|------------|
| G1 | Números não reproduzíveis (eff_rank 114.6 vs 2.5) | `hidden_spectral.py:L37` `_MAX_FILES=8`; OW-AUD-020 §2.2 | Crítica |
| G2 | Fórmula de eff_rank documentada como Roy&Vetterli mas implementada como entropia | `hidden_spectral.py:L75-86` | Alta |
| G3 | Alegação "10/10 correções" vs ledger 10/34 | `coding_battery.sqlite` (OW-AUD-020 §2.4); writeup §3.4c | Alta |
| G4 | Trajetória por passo desligada por default; metadata ausente | `erika_torch_server.py:L177,215-216`; OW-AUD-020 §2.3 | Média |
| G5 | Φ "exact PyPhi" sem script de cálculo no repo | `markov_blanket.py` (sem pyphi import) | Média |
| G6 | README promete systemd mas `DIRECTORY_CONTRACT.yaml` diz `[]` | `README.md:L55-77` | Média |
| G7 | Singleton affect tracer sem partição por sessão | `affect_tracer.py:L289-313` | Média |
| G8 | `_llm.py` sem timeout explícito no httpx | `agents/_llm.py:L65` | Baixa |
| G9 | Quatro superfícies de dashboard não reconciliadas | `docs/dashboard.html`, `docs/index.html`, `soul/static/*` | Baixa |
| G10 | pyproject sem classifiers/urls/keywords | `pyproject.toml` | Baixa |

## 5. Plano de ação recomendado (cirúrgico, sem editar código nesta auditoria)

1. Reconciliar números: ou reprocessar com K=64 e documentar a fórmula correta, ou corrigir o writeup para 2.5 e trocar "Roy & Vetterli" por "entropic effective rank".
2. Corrigir alegação de "10/10" para "10/34 (29.4%) com analista; 10/20 (50%) entre casos com analista".
3. Documentar trajetória por passo como opt-in (`OMNI_ACT_STEP_EVERY=8`) e publicar metadata (run_id/turn/task) nos sidecars.
4. Incluir script reproduzível de Φ (PyPhi) ou renomear claim para "TPM pronto para PyPhi".
5. Unificar dashboard em um único entrypoint; linkar `docs/index.html` no README.
6. Adicionar `timeout=` explícito em `_llm.py` e partição por sessão no affect tracer (ou documentar limite como blocker para multi-usuário).
7. Resolver contradição systemd no README (tabela vs rodapé).

## 6. Veredito

O repositório é denso, técnico e ambicioso, com mecanismos reais e bem implementados (captura sidecar, peer-swap, swap scheduler, TPM coarse-grained, affect tracer). Porém, as alegações quantitativas do writeup (eff_rank 114.6, "10/10 correções") não se sustentam contra o código/ledger publicado — isso é o maior risco para a competição (critério Verifiability). Correção cirúrgica dos números e da fórmula é pré-requisito antes da submissão.
