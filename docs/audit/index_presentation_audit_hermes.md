# AUDITORIA — Indexação, Apresentação Pública e Coerência Arquitetônica
Data: 2026-11-04 (UTC)
Escopo: DOCS_INDEX.md, MAPA_PRIMARIO_2026-11-04.md, README.md, AGENTS.md, PAPER_WRITEUP.md
Tipo: READ-ONLY (sem edição de código)

## 1. Resumo executivo
- DOCS_INDEX.md indexa corretamente os documentos que lista, mas cobre apenas ~30 docs; existem 107 docs em docs/ sem entrada nele.
- MAPA_PRIMARIO_2026-11-04.md referencia em maioria arquivos existentes, mas inclui 6+ caminhos ausentes no repo ativo (soberano read-only ou obsoletos) e usa nomes curtos ambíguos sem qualificar src/omni_coworker/.
- README.md e AGENTS.md descrevem a arquitetura corretamente em linhas gerais, mas:
  (a) omitem a camada vendored (vendor/kernel/ + vendor/README.md);
  (b) tratam bind loopback como padrão, quando o default do código é 0.0.0.0 (loopback exige OMNI_API_HOST=127.0.0.1).
- PAPER_WRITEUP.md tem numeros desatualizados (linhas de codigo, testes) e uma inconsistencia critica vs MAPA_PRIMARIO_2026-11-04.md em resultados de coding_battery.
- README.md e PAPER_WRITEUP.md repetem claims funcionais ("real somatic interoception", "dream cycle", "Machine Public Soul") sem citar origem no proprio repo.

## 2. Checagem de existência e indexação

### 2.1 DOCS_INDEX.md
- Lista 50 links (pt+en duplicados). Todos os caminhos listados existem em disco.
- Inconsistencia estrutural: usa ../README.md e ../AUTHORS.md (válidos apenas dentro de docs/; quebram como standalone).
- Cobertura parcial: existem 107 docs em docs/ sem entrada em DOCS_INDEX.md. Exemplos ausentes:
  docs/audit/OW-AUD-011..020, docs/audits/AUDIT_*.md, docs/results/*.md, docs/studies/ERROR_PATTERNS_SELF_CHECK.md, docs/design/DESIGN_BRIEF.md, docs/design/OW-MATH-001_phi_definitions.md, docs/design/OW-DSN-001..003, docs/design/OW-STU-019..020, docs/ops/OW-OPS-001_env_vars_production.md, docs/RELATORIO_CONFIRMACAO_2026-11-04.md, docs/results/WRITEUP_MPS_DRAFT_2026-11-04.md, src/omni_coworker/*/README.md, vendor/README.md.

### 2.2 MAPA_PRIMARIO_2026-11-04.md
- Maioria dos caminhos de codigo/docs existe.
- Referencias ausentes ou frágeis no repo ativo:
  - docs/WRITEUP_ESQUELETO.md (ausente)
  - km/src/stubs/huggingface_hub_stub.py (soberano read-only)
  - kilombo/scripts/experiments/transformer_mps_bridge_pilot.py (soberano read-only)
  - erika/kernel_daemon*.py, erika/mesh_runtime_daemon.py (soberano read-only)
  - src.erika.memory.py (soberano read-only)
  - loop.py, state_guard.py, matrix.py, brain/server.py (nomes curtos sem src/omni_coworker/; só existem com prefixo)
  - __init__.py (genérico; não há arquivo com esse nome na raiz de src/omni_coworker/)

## 3. Coerência arquitetônica README.md / AGENTS.md vs estado vivo

### 3.1 API :8081 loopback
- README.md e AGENTS.md associam :8081 a loopback.
- Estado vivo: cli.py default bind = OMNI_API_HOST env ou 0.0.0.0 (fallback). docs/ops/OW-OPS-001_env_vars_production.md e scripts/restore_env.sh mostram que loopback (127.0.0.1) é configuracao de producao via env, nao default.
- Correcao: distinguir default (0.0.0.0) de producao (127.0.0.1).

### 3.2 Kernel 3/3
- Nao ha texto literal "kernel 3/3" no repo.
- Correspondencia plausivel: 3 crates Rust vendored em vendor/kernel/{freud10d,kernel_compute,metrics}, consumidos por kernel_hooks/compute.py via PyO3.
- Estado vivo: diretorios e Cargo.toml existem; build_kernel.sh referencia vendor/kernel.
- Correcao: se "kernel 3/3" for intencional, documentar explicitamente em README/AGENTS como "3 crates vendored".

### 3.3 Freud10d + dendritic publicando
- Estado vivo:
  - vendor/kernel/freud10d/ existe (Cargo.toml + src/lib.rs).
  - src/omni_coworker/activation_beta/dendritic_morphology.py existe (port).
  - tests/test_dendritic_morphology.py existe.
  - /agency/dunker expõe dunker_architecture + affect_state + collect_kernel_bundle.
- "Publicando" nao aparece literalmente no codigo; o sentido mais proximo e "ativo e exposto via HTTP".
- Correcao: se "publicando" significa publicacao no dashboard/bus, apontar o endpoint/arquivo; senao, reescrever como "ativos/publicados na API".

### 3.4 Vendored crates + dunker
- Estado vivo: vendor/kernel/ tem 3 crates; agency/dunker.py e vendor/README.md confirmam vendored.
- README.md menciona kernel_hooks e agency/dunker, mas nao menciona vendor/.
- AGENTS.md nao menciona vendor/.
- Correcao: adicionar mencao a vendor/kernel/ e vendor/README.md na apresentacao publica.

## 4. Linguagem profissional e claims sem fonte

### 4.1 README.md
- Tom promocional com claims funcionais sem citacao de codigo/documento:
  - "Real somatic interoception"
  - "tensor-derived affect"
  - "endogenous teleology"
  - "autopoietic governance"
  - "dream cycle"
  - "curiosity mode"
  - "Machine Public Soul (SSE + UI bilíngue)"
- Problema: essas frases sao descritivas de produto, nao tecnicamente fundamentadas no proprio README. Violam a regra de integridade do AGENTS.md quando usadas em doc publico.
- Correcao: adicionar notas como "(implementado em soma/probe.py, agency/affect_tracer.py, agency/dream.py, agency/curiosity.py, soul/api.py)" ou marcar como [INTERPRETAÇÃO].

### 4.2 PAPER_WRITEUP.md
- Números desatualizados sem fonte:
  - "~18.800 linhas de codigo" vs estado vivo ~23.800.
  - "455 testes automatizados passando" vs estado vivo ~472.
- Inconsistência critica com MAPA_PRIMARIO_2026-11-04.md:
  - PAPER_WRITEUP abstract: "30/30 compile+black with the Analyst active vs 0/20 without".
  - MAPA_PRIMARIO_2026-11-04.md (secao 8 / coding_battery.sqlite): "20/30 compilacoes validas quando o Analista esta ativo vs 0/14 sem Analista".
- Claims sem fonte externa:
  - Relacoes entre perfil psicodiagnostico e modos de falha sao apresentadas como descoberta, mas dependem de bancos sqlite internos sem checklist de reproducao no documento.
  - Frases de marketing herdadas do README ("Machine Public Soul", "dream cycle", etc.) sem nota metodologica.
- Correcao: reconciliar numeros com MAPA_PRIMARIO_2026-11-04.md e CONTUITY_MAP.md; atualizar LOC/testes; adicionar nota metodologica para claims nao replicaveis externamente.

## 5. Tabela consolidada de inconsistencias

| Arquivo | Problema | Correcao sugerida |
|---------|----------|-------------------|
| DOCS_INDEX.md | Cobre apenas subconjunto; 107 docs existentes em docs/ sem entrada. | Expandir indice para incluir docs/audit/*, docs/audits/*, docs/results/*, docs/studies/*, docs/ops/*, docs/design/*, ou declarar explicitamente que e um indice seletivo. |
| DOCS_INDEX.md | Usa links relativos ../README.md e ../AUTHORS.md (frageis como standalone). | Usar links absolutos/raiz ou adicionar nota de contexto. |
| MAPA_PRIMARIO_2026-11-04.md | Referencia docs/WRITEUP_ESQUELETO.md (ausente). | Remover referencia ou criar o arquivo. |
| MAPA_PRIMARIO_2026-11-04.md | Referencia caminhos do soberano read-only (km/src/stubs/..., kilombo/scripts/..., erika/kernel_daemon*.py, erika/mesh_runtime_daemon.py, src.erika.memory.py) como se fossem parte do repo ativo. | Marcar explicitamente como [SOBERANO READ-ONLY] ou remover do mapa primario do omni_worker. |
| MAPA_PRIMARIO_2026-11-04.md | Usa nomes curtos ambíguos (loop.py, state_guard.py, matrix.py, brain/server.py) sem prefixo src/omni_coworker/. | Qualificar caminhos completos ou adicionar nota de escopo. |
| README.md | Default de bind tratado como loopback, mas cli.py default e 0.0.0.0 (loopback exige OMNI_API_HOST=127.0.0.1). | Reescrever: "padrao 0.0.0.0; producao publica recomenda OMNI_API_HOST=127.0.0.1 + OMNI_GATE_FAIL_CLOSED=1". |
| README.md | Omite camada vendored (vendor/kernel/ + vendor/README.md) embora scripts/build_kernel.sh e codigo dependam dela. | Adicionar secao ou nota sobre vendor/kernel/ (3 crates Rust). |
| README.md | Claims funcionais ("real somatic interoception", "tensor-derived affect", "endogenous teleology", "dream cycle", "curiosity mode", "Machine Public Soul") sem citacao de origem. | Adicionar marcadores [DADO]/[INTERPRETAÇÃO] ou links para os modulos implementados. |
| AGENTS.md | "Produção pública: OMNI_GATE_FAIL_CLOSED=1, bind loopback" como se fosse configuracao default. | Separar default de laboratorio (fail-open, 0.0.0.0) de producao publica (fail-closed, loopback). |
| AGENTS.md | Nao referencia vendor/ nem docs de auditoria existentes. | Adicionar vendor/ e docs/audit/ ao escopo de documentos obrigatorios. |
| PAPER_WRITEUP.md | Abstract: numeros desatualizados (~18.800 LOC, 455 testes). | Atualizar para ~23.800 LOC e ~472 testes, citando contagem atual. |
| PAPER_WRITEUP.md | Abstract: "0/20 without" em coding_battery vs "0/14 without" em MAPA_PRIMARIO_2026-11-04.md. | Reconciliar com o dado de coding_battery.sqlite e corrigir para o valor auditado mais recente. |
| PAPER_WRITEUP.md | Claims de marketing herdadas do README sem nota metodologica ("Machine Public Soul", "dream cycle", etc.). | Substituir por descricoes operacionais com fontes (ex: soul/api.py, agency/dream.py). |
| PAPER_WRITEUP.md | Alguns numeros de bancos sqlite citados sem verificacao local no documento (ex: 389 runs). | Adicionar hash/row-count ou nota [DADO] com origem arquivada. |
| docs/ops/OW-OPS-001_env_vars_production.md | Default de OMNI_API_HOST documentado como 0.0.0.0, contradizendo leitura simples de README/AGENTS que tratam loopback como estado natural. | Adicionar nota cruzada explicando a divergencia entre default e producao. |

## 6. Estado vivo dos itens citados pelo usuario

| Item citado | Estado verificado | Observacao |
|-------------|-------------------|------------|
| API :8081 loopback | Parcial | Porta correta, mas loopback e configuracao de producao via OMNI_API_HOST=127.0.0.1; default do codigo e 0.0.0.0. |
| kernel 3/3 | Verdadeiro (interpretado como 3 crates vendored) | vendor/kernel/{freud10d,kernel_compute,metrics} existem e sao consumidos por kernel_hooks. |
| freud10d + dendritic publicando | Verdadeiro (ativos e expostos na API) | vendor/kernel/freud10d/ e src/omni_coworker/activation_beta/dendritic_morphology.py existem; endpoint /agency/dunker integra ambos. Nao ha literal "publicando" no codigo. |
| vendored crates + dunker | Verdadeiro | vendor/kernel/ + agency/dunker.py + vendor/README.md confirmam; README.md omite vendor/. |

## 7. Acoes recomendadas (para proxima edicao)
1. Expandir DOCS_INDEX.md ou declara-lo como indice seletivo com nota explicita.
2. Limpar/Marcar referencias do soberano em MAPA_PRIMARIO_2026-11-04.md.
3. Corrigir default de bind em README/AGENTS para refletir 0.0.0.0 + configuracao de producao.
4. Adicionar secao vendored em README.md e AGENTS.md.
5. Reconciliar numeros de PAPER_WRITEUP.md com MAPA_PRIMARIO_2026-11-04.md e atualizar LOC/testes.
6. Rotular claims funcionais sem fonte com [DADO] ou [INTERPRETAÇÃO] seguindo o estatuto epistêmico do proprio AGENTS.md.
