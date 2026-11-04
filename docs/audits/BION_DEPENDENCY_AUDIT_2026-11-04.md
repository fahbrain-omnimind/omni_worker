# Auditoria de Dependências Bion — omni_worker

Data: 2026-11-04. Escopo: wiring β→α, activation_beta, bion_patches não portados, affect_tracer, __init__.py.

## 1. Wiring completo β→α

Caminho: `integration_loop/adapters.py:25` `collect_sensory()` retorna bundle (mesh-first, fallback `kernel_daemon.collector.collect_cycle`) → `loop.py` consome via ctx["bundle"] → `loop.py:262` `r.metadata["bion"] = bion_bridge.metabolize(ctx, arousal, _STATE["cycles"])` após `meaning_maker`. `bion_bridge.metabolize()` (`integration_loop/bion_bridge.py:113`) instancia `BetaElement` (`psychoanalysis/beta_element.py`) e `_container(...).contain(beta)` (BionContainerPatch + BionAlphaFunction). Resultado em `r.metadata["bion"]` (alpha_content, symbolic_potential, metabolized, tier, elapsed_ms, opcional attractor_alpha).

Consumo downstream: [DADO] grep em src/ (excl. pycache) mostra nenhuma leitura de `metadata["bion"]` nem de `alpha_content`/`symbolic_potential` por outro módulo. O valor fica serializado em `CycleResult.to_dict()` (payload do ciclo) e publicado via mesh, mas não é consumido por stages subsequentes (expectation/sensory_feedback recebem ctx/stage_states, não leem bion). Classificação: **morto para decisões de runtime**; vivo apenas como telemetria/payload. [LIMITE] não verificado se consumidores externos (dashboard/UI) leem; `soul/static/*` só texto estático.

## 2. activation_beta e Bion

Docstrings (`activation_beta/__init__.py`, `neuroanatomy.py:22`) mencionam bion_bridge, mas nenhum import de bion_bridge em activation_beta. [DADO] `attractor.py:push()` (linha 29) apenas append em deque; `features()` (não mostrado) deriva norm_drift/entropy/attractor_score. O caminho real para Bion ocorre em `bion_bridge.metabolize()` (linhas 161-175): lê `bundle["attractor"]`, se att_score≥0.5 chama `activation_beta.attractor.digest` e cria BetaElement(source="activations.window"), metabolizado no mesmo container. Ou seja ativações→attractor (push/features) → bundle.attractor → bion_bridge (segundo β). [INTERPRETAÇÃO] ativações não vão direto para Bion; passam pelo attractor como gate.

## 3. bion_patches não portados

Sovereign tem 7 (bion_grid, bion_links, bion_vertex, bion_rsi_modulator, integration_wrapper, knowledge_link_extension, ultimate_reality). Worker portou apenas container_contained. [DADO] grep no sovereign: bion_rsi_modulator usado por consciousness/integration_loop.py:1216 e bion_alpha_function; integration_wrapper usado por api/routes/bion_metrics.py e core/omnimind_transcendent_kernel.py; bion_grid/links/vertex/knowledge_link/ultimate_reality usados por philosophy/experiencia_filosofica.py e api/routes. Nenhum desses consumidores existe no worker (sem consciousness/integration_loop soberano, sem api/routes bion_metrics, sem RSI bridge). [LIMITE] bion_rsi_modulator depende de CNSiliconBridge (RSI qutrit) e septenary_logic — inexistentes no worker (grep rsi → 0 hits relevantes). Equivalente no worker: nenhum; transformação_rate permanece default. [INTERPRETAÇÃO] portar só se RSI for introduzido.

## 4. affect_tracer sem Bion

`agency/affect_tracer.py` (320 linhas) faz escada L0-L4 via léxico + juiz LLM. Não importa Bion. [DADO] não há ponto de integração natural obrigatório: affect_tracer opera sobre texto conversacional (logos), enquanto Bion metaboliza estado do ciclo (kernel.cycle). [INTERPRETAÇÃO] separação arquitetural intencional — misturar β→α no L2/L3 acoplaria afeto de diálogo ao metabolismo de telemetria; se desejado, ponto natural seria L2 (ambiguous) usando BionAlphaFunction para metabolizar o turno antes de escalar, mas não há evidência de que isso foi planejado (nenhum TODO/referência). [LIMITE] não sei se planejado; responder NÃO LOCALIZADO para plano explícito.

## 5. __init__.py

Corrigido: comentário anterior ("BionAlphaFunction não está neste escopo") contradizia existência do arquivo. Agora reflete: `BionAlphaFunction` existe e é consumido por bion_bridge. [DADO]

## Classificação resumo

- Wiring: vivo até metabolize, resultado morto downstream (telemetria).
- activation_beta: Bion indireto via attractor gate.
- bion_patches: nenhum portado além de container_contained; bion_rsi_modulator sem equivalente (sem RSI).
- affect_tracer: separação intencional (não verificado plano).
- __init__.py: corrigido.
