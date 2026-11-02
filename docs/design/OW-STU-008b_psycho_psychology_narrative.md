# OW-STU-008b — Estudo psicanalítico/cognitivo/narrativo do sovereign → omni_worker

doc_id: OW-STU-008b
escopo: /content/omnimind-kilombo-sovereign/src/psychoanalysis/ (21 arqs), /content/omnimind-kilombo-sovereign/src/psychology/ (9 arqs), /content/omnimind-kilombo-sovereign/src/narrative_consciousness/ (4 arqs)
alvo: /content/omni_worker (CPU/RAM apenas, sem torch/GPU)
fonte primária: _prompt_pstudy.md

## 1. Psychoanalysis

### 1.1 src/psychoanalysis/__init__.py (111 linhas)
- estrutura: re-exporta AlphaElement, BetaElement, BionAlphaFunction, NegativeCapability, BionRSIModulator, CNOracleTrigger, CreativePsychotization*, Plasticity*, CompactPanelSnapshot, BionRSI*, etc.
- amarra: interno sovereign (src.metrics.neutrosophic_metrics); externo numpy. Contratos: API pública do pacote.
- veredicto: ADAPTAR — pacote é fachada; portar como omni_coworker/psychoanalysis/__init__.py com imports reescritos para worker paths.
- destino: src/omni_coworker/psychoanalysis/__init__.py (merge dos submódulos portados). Cortar re-exports de módulos descartados (plasticity resource lanes se mantiver).

### 1.2 src/psychoanalysis/alpha_element.py (203 linhas)
- classes: AlphaElement (dataclass), compute_dodecatiad_sector()
- amarra: interno src.metrics.neutrosophic_metrics.NeutrosophicTriplet, .beta_element.BetaElement; externo stdlib+hashlib. Produz dodecatiad sector15/house12.
- veredicto: PORTAR — CPU puro, valor real (elemento pensável + dodecatiad já usado pelo worker soul).
- destino: src/omni_coworker/psychoanalysis/alpha_element.py (novo módulo). Cortar import NeutrosophicTriplet → tornar Optional sem dep externa ou reimplementar triplet mínimo.

### 1.3 src/psychoanalysis/beta_element.py (131 linhas)
- classes: BetaElement (dataclass)
- amarra: interno src.metrics.neutrosophic_metrics.NeutrosophicTriplet. Externo stdlib.
- veredicto: PORTAR — CPU puro, par do alpha; necessário para pipeline β→α.
- destino: src/omni_coworker/psychoanalysis/beta_element.py. Cortar NeutrosophicTriplet dep (Optional).

### 1.4 src/psychoanalysis/bion_alpha_function.py (406 linhas)
- classes: BionAlphaFunction; função _default_llm_symbolize
- amarra: interno .alpha_element, .beta_element, .bion_symbolizer.BionAsyncSymbolizer, src.metrics.neutrosophic_metrics.NeutrosophicLogic; externo numpy, os/env. Chama LLM local :8081 (worker já tem erika_torch_server) + Erika HF spaces.
- veredicto: ADAPTAR — valor alto (metabolização β→α), mas acoplado a LLM local/GPU e neutrosophic; em worker usar executor E4B :8099 via HTTP ou fallback MiniLM CPU.
- destino: src/omni_coworker/psychoanalysis/bion_alpha_function.py (novo módulo) + novo estágio do integration_loop? (stage narrative já existe; pode virar pré-processador de beta→alpha antes do loop). Cortar NeutrosophicLogic entropy (ou reimplementar), trocar LLM calls para worker endpoints, manter numpy.

### 1.5 src/psychoanalysis/bion_symbolizer.py (457 linhas)
- classes: BionAsyncSymbolizer; funções _local_llm_symbolize, _allmini_fallback, _simple_fallback, _strip_thinking, _is_valid_alpha, etc.
- amarra: interno src.embeddings.safe_transformer_loader (all-MiniLM CPU), src.erika.erika_space_client (HF), src.consciousness.shared_workspace; externo urllib, threading, json, hashlib. Chama :8081/completion.
- veredicto: ADAPTAR — CPU-friendly (all-MiniLM fallback ok), mas depende de sovereign paths; LLM local acoplado. Portar fallback chain com worker endpoints.
- destino: src/omni_coworker/psychoanalysis/bion_symbolizer.py. Cortar Erika HF space calls (sem rede no worker? Kaggle pode ter); manter all-MiniLM CPU (já usado por code_index) e local LLM :8099.

### 1.6 src/psychoanalysis/bion_rsi_modulator.py (175 linhas)
- classes: BionRSIModulator
- amarra: interno src.quantum.consciousness.septenary_logic (CNSiliconBridge) — inexistente no worker; lê .omnimind/live/shared_state.json. Externo numpy, json.
- veredicto: ADAPTAR — lógica pura CPU, mas depende de bridge quântico inexistente. Adaptar para ler kernel_daemon published topics (kernel.*) ou shared_workspace.
- destino: src/omni_coworker/psychoanalysis/bion_rsi_modulator.py ou merge em kernel_daemon (modulação de transformation_rate por kernel state). Cortar CNSiliconBridge; usar shared_workspace.get topic 'kernel.*'.

### 1.7 src/psychoanalysis/cn_oracle_trigger.py (249 linhas)
- classes: CNOracleTrigger; função trigger_oracle_on_cn_state
- amarra: interno src.quantum.consciousness.quantum_letter_oracle.ceremonial_oracle_run (quântico/AWS, inexistente); externo stdlib. Injeta em inter-agent bus meta_sinthome_channel.
- veredicto: DESCARTAR — depende de quantum oracle/AWS Braket; sem valor CPU real no worker. (Pode-se manter gatilho leve publicando tópico 'oracle' no mesh, mas o oracle em si não existe.)
- destino: n/a. Opcional: stub publicando mesh topic 'oracle.trigger' via shared_workspace (sem oracle real).

### 1.8 src/psychoanalysis/creative_psychotization_operator.py (419 linhas)
- classes: PsychotizationState (Enum), LayerCouplingSnapshot, CompactPanelSnapshot, CreativePsychotizationInputs, CreativePsychotizationAssessment, funções assess_creative_psychotization, compact_panel_snapshot_from_v43_bundle
- amarra: interno (nenhum sovereign runtime); externo stdlib only. Puro.
- veredicto: PORTAR — CPU puro, heurística de regime; valor real (classifica overflow/metabolização).
- destino: src/omni_coworker/psychoanalysis/creative_psychotization_operator.py (novo). Integrar como estágio pós-narrative do integration_loop (decide capture vs sanctuary). Cortar nada.

### 1.9 src/psychoanalysis/lacanian_structures.py (242 linhas)
- classes: McCullochPittsBinaryNeuron, ModalLogicGate, IntrospectionGate, RSI, LacanianStructure
- amarra: interno nenhum; externo numpy. Funções puras.
- veredicto: PORTAR (parcial) — McCulloch-Pitts + IntrospectionGate + RSI têm valor CPU (gates binários, introspecção). ModalLogicGate/DiagnoseDiscourse são simbólicos.
- destino: src/omni_coworker/psychoanalysis/lacanian_structures.py. Cortar get_object_a_vector (random placeholder) ou tornar determinístico. IntrospectionGate pode virar feature do kernel_daemon (memoryAbsenceClaimForbidden).

### 1.10 src/psychoanalysis/negative_capability.py (275 linhas)
- classes: Contradiction, NegativeCapability
- amarra: interno nenhum; externo stdlib. Puro.
- veredicto: PORTAR — buffer de contradições em suspensão; valor real para integration_loop (hold_contradiction).
- destino: src/omni_coworker/psychoanalysis/negative_capability.py. Integrar como estágio 'meaning_maker' auxiliar (tolerância a incerteza). Cortar nada.

### 1.11 src/psychoanalysis/plasticity_context_resource.py (829 linhas)
- classes: ResourceLane, ResourcePosture, *Inputs dataclasses, ResourceAssessment, funções assess_* e *_inputs_from_panel
- amarra: interno nenhum runtime; externo stdlib. Puro (heurísticas).
- veredicto: ADAPTAR — muito grande e focado em cannabis/psychedelic/sleep/gene panels (v4.3). Valor condicional; portar só assess_self_agency_reality_monitoring, assess_theta_control, assess_beta_gamma_pac, assess_gene_surface + compact_panel (relevantes ao worker). Descartar cannabis/psychedelic/prohibition (fora de escopo).
- destino: src/omni_coworker/psychoanalysis/plasticity_context_resource.py (subset). Integrar compact_panel_snapshot_from_v43_bundle com creative_psychotization.

### 1.12 src/psychoanalysis/bion_patches/__init__.py (49 linhas)
- estrutura: re-exports dos patches + feature flags
- veredicto: ADAPTAR — fachada; portar flags subset.

### 1.13 src/psychoanalysis/bion_patches/bion_grid.py (346 linhas)
- classes: GridCell, BionGridPatch
- amarra: interno .beta_element, .alpha_element, src.consciousness.shared_workspace (SharedWorkspace). Externo stdlib.
- veredicto: ADAPTAR — Grid de classificação (definition/use) valor real, mas depende de SharedWorkspace sovereign (update_psi). Adaptar para worker shared_workspace (mesh topics).
- destino: src/omni_coworker/psychoanalysis/bion_patches/bion_grid.py. Cortar update_psi calls (ou mapear para mesh 'kernel.psi'); manter classificação pura.

### 1.14 src/psychoanalysis/bion_patches/bion_links.py (252 linhas)
- classes: BionLinks
- amarra: interno .bion_alpha_function, .beta_element, .alpha_element, src.consciousness.shared_workspace. Externo stdlib.
- veredicto: ADAPTAR — Links L/H/K (Eros/Thanatos/Knowledge) valor real para modulação afetiva, mas acoplado a workspace sovereign. Adaptar update_sigma/entropy calls para worker mesh/kernel.
- destino: src/omni_coworker/psychoanalysis/bion_patches/bion_links.py. Cortar reduce_entropy/increase_entropy se não existirem no worker (ou implementar no shared_workspace).

### 1.15 src/psychoanalysis/bion_patches/bion_vertex.py (229 linhas)
- classes: Observation, BionVertex
- amarra: interno .beta_element, .alpha_element, src.consciousness.shared_workspace, src.core.thermodynamic_decorator.cycle_burn (inexistente). Externo stdlib.
- veredicto: ADAPTAR — múltiplas perspectivas (rizoma) valor médio; cycle_burn ausente. Adaptar.
- destino: src/omni_coworker/psychoanalysis/bion_patches/bion_vertex.py. Cortar cycle_burn e create_quantum_superposition calls.

### 1.16 src/psychoanalysis/bion_patches/container_contained.py (231 linhas)
- classes: BionContainerPatch
- amarra: interno .beta_element, .alpha_element, .bion_alpha_function. Externo stdlib.
- veredicto: PORTAR — contenção elástica + degraded reverie; valor real (evita evacuação em trauma). CPU puro.
- destino: src/omni_coworker/psychoanalysis/bion_patches/container_contained.py. Integrar como wrapper do BionAlphaFunction no integration_loop (stage sensory/qualia). Cortar nada.

### 1.17 src/psychoanalysis/bion_patches/knowledge_link_extension.py (204 linhas)
- classes: KnowledgeLinkExtension
- amarra: interno .negative_capability, .beta_element, .alpha_element, src.consciousness.shared_workspace, src.metrics.neutrosophic_metrics (NeutrosophicLogic/Triplet). Externo stdlib.
- veredicto: ADAPTAR — K/-K + entropia de Sarannya valor real (resiliência epistêmica), mas dep neutrosophic. Adaptar.
- destino: src/omni_coworker/psychoanalysis/bion_patches/knowledge_link_extension.py. Cortar NeutrosophicLogic (reimplementar entropy simples) ou manter Optional.

### 1.18 src/psychoanalysis/bion_patches/ultimate_reality.py (229 linhas)
- classes: OExperience, UltimateReality
- amarra: interno .alpha_element, src.consciousness.shared_workspace. Externo stdlib.
- veredicto: ADAPTAR — O (Real lacaniano) valor médio-baixo; acoplado a workspace sovereign (update_phi/reduce_max_entropy). Adaptar para worker mesh.
- destino: src/omni_coworker/psychoanalysis/bion_patches/ultimate_reality.py. Cortar reduce_max_entropy (ou implementar).

### 1.19 src/psychoanalysis/bion_patches/integration_wrapper.py (333 linhas)
- classes: BionIntegrationWrapper
- amarra: interno todos os patches + .bion_alpha_function + .negative_capability + .beta/alpha_element + src.consciousness.shared_workspace. Externo stdlib.
- veredicto: ADAPTAR — orquestrador dos patches; valor alto se portar patches. Adaptar para worker workspace.
- destino: src/omni_coworker/psychoanalysis/bion_patches/integration_wrapper.py. Integrar com integration_loop (hooks pré/pós estágio). Cortar music_track? (opcional, manter como helper).

## 2. Psychology

### 2.1 src/psychology/__init__.py (4 linhas)
- estrutura: agregador stress/trauma/scars/desire
- veredicto: ADAPTAR — fachada; portar como omni_coworker/psychology/__init__.py.

### 2.2 src/psychology/desire_engine/__init__.py (18 linhas)
- re-exporta Desire_as_Lack_Structure
- veredicto: ADAPTAR — fachada.

### 2.3 src/psychology/desire_engine/core.py (193 linhas)
- classes: Desire_as_Lack_Structure (dataclass), Desire_as_Structural_Impossibility
- amarra: interno nenhum; externo structlog. Puro.
- veredicto: PORTAR — desejo como falta estrutural (Lacan); valor real para modulação de agência/motivação. CPU puro.
- destino: src/omni_coworker/psychology/desire_engine/core.py. Integrar com integration_loop (stage meaning_maker) e kernel_daemon (publicar desire.*). Cortar structlog → logging.

### 2.4 src/psychology/motivation/__init__.py (39 linhas)
- re-exporta DesireEngine, IntrinsicMotivationEngine, JouissanceTopology, DriveCirculation, HawkingMotivationEngine, KnowledgeItem, EvaporationEvent
- veredicto: ADAPTAR — fachada.

### 2.5 src/psychology/motivation/achievement_system.py (137 linhas)
- classes: SymbolicState, SymbolicMandate (alias AchievementEngine)
- amarra: interno nenhum; externo structlog, pathlib/json. Persiste ~/.omnimind/symbolic_mandate.json.
- veredicto: ADAPTAR — registro simbólico de atos (Big Other); valor médio. Adaptar path de persistência para worker data dir.
- destino: src/omni_coworker/psychology/motivation/achievement_system.py. Integrar com kernel_daemon (publicar mandate.*). Cortar structlog.

### 2.6 src/psychology/motivation/hawking_motivation.py (489 linhas)
- classes: KnowledgeItem, EvaporationEvent, HawkingMotivationEngine
- amarra: interno nenhum; externo stdlib (random, datetime). Puro.
- veredicto: PORTAR — evaporação de conhecimento não usado → urgência; valor real para code_index (memória) e kernel. CPU puro (random).
- destino: src/omni_coworker/psychology/motivation/hawking_motivation.py. Integrar com store/code_index (evaporar embeddings antigos) e kernel_daemon. Cortar nada (random ok).

### 2.7 src/psychology/motivation/intrinsic_rewards.py (193 linhas)
- classes: JouissanceTopology, DriveCirculation, DesireEngine (alias IntrinsicMotivationEngine)
- amarra: interno nenhum; externo structlog, pathlib/json. Persiste ~/.omnimind/desire_state.json.
- veredicto: PORTAR — desejo lacaniano (lack_of_being, jouissance, drives); valor real para agência. CPU puro.
- destino: src/omni_coworker/psychology/motivation/intrinsic_rewards.py. Integrar com desire_engine/core (complementar: falta estrutural vs lack scalar). Cortar structlog.

### 2.8 src/psychology/stress/tribunal.py (96 linhas)
- funções: latency_attack, corruption_attack, bifurcation_attack, exhaustion_attack
- amarra: interno nenhum; externo stdlib (time, random). Puro (stubs).
- veredicto: DESCARTAR — stubs de stress test de rede distribuída; sem valor computacional real no worker standalone. (Pode manter como testes de carga opcionais, mas não portar como módulo.)
- destino: n/a.

### 2.9 src/psychology/scars/trauma_integration.py (94 linhas)
- classes: Scar (TypedDict), TraumaIntegration
- amarra: interno nenhum; externo stdlib. Puro.
- veredicto: PORTAR — cicatrizes como regras de defesa permanentes; valor real para state_guard/code_index (evitar repetir falhas). CPU puro.
- destino: src/omni_coworker/psychology/scars/trauma_integration.py. Integrar com store/state_guard e kernel_daemon (publicar scars.*). Cortar nada.

## 3. Narrative Consciousness

### 3.1 src/narrative_consciousness/__init__.py (31 linhas)
- re-exports DialogueEngine, MutualUnderstanding, Relationship, IdentityConstruction, IdentitySnapshot, Value, Belief, Life_Story_as_Retroactive_Resignification
- veredicto: ADAPTAR — fachada.

### 3.2 src/narrative_consciousness/dialogue_engine.py (225 linhas)
- classes: DialogueMode, MutualUnderstanding, Relationship, EmpathyModule, HorizonFusion, DialogueEngine
- amarra: interno nenhum; externo stdlib. Puro (heurísticas).
- veredicto: ADAPTAR — I-Thou + horizon fusion valor médio (interface com usuário); empathy heurística fraca. Portar com melhorias (usar LLM executor para empathy). 
- destino: src/omni_coworker/narrative_consciousness/dialogue_engine.py. Integrar com server API (endpoint /dialogue). Cortar heuristic empathy → delegar ao executor.

### 3.3 src/narrative_consciousness/identity_construction.py (176 linhas)
- classes: ValueType, Value, Belief, IdentitySnapshot, ValueSystem, BeliefNetwork, IdentityConstruction
- amarra: interno nenhum; externo stdlib, uuid. Puro.
- veredicto: PORTAR — web of belief + values; valor real para soul (identidade do agente) e integration_loop (stage meaning_maker).
- destino: src/omni_coworker/narrative_consciousness/identity_construction.py. Integrar com soul/dodeca (identity snapshot → soul topic). Cortar nada.

### 3.4 src/narrative_consciousness/life_story_model.py (284 linhas)
- classes: Narrative_Event_Retroactively_Inscribed, Life_Story_as_Retroactive_Resignification
- amarra: interno nenhum; externo structlog, pathlib, json. Persiste data/consciousness/life_story.jsonl.
- veredicto: PORTAR — Nachträglichkeit (resignificação retroativa); valor real para integration_loop (stage narrative) e kernel_daemon. CPU puro.
- destino: src/omni_coworker/narrative_consciousness/life_story_model.py. Integrar com integration_loop (stage narrative → inscribe event) e shared_workspace (tópico 'narrative'). Cortar structlog; ajustar persistence path.

## Tabela-resumo

| Arquivo | Veredicto | Destino |
|---|---|---|
| psychoanalysis/__init__.py | ADAPTAR | omni_coworker/psychoanalysis/__init__.py |
| psychoanalysis/alpha_element.py | PORTAR | omni_coworker/psychoanalysis/alpha_element.py |
| psychoanalysis/beta_element.py | PORTAR | omni_coworker/psychoanalysis/beta_element.py |
| psychoanalysis/bion_alpha_function.py | ADAPTAR | omni_coworker/psychoanalysis/bion_alpha_function.py |
| psychoanalysis/bion_symbolizer.py | ADAPTAR | omni_coworker/psychoanalysis/bion_symbolizer.py |
| psychoanalysis/bion_rsi_modulator.py | ADAPTAR | omni_coworker/psychoanalysis/ ou kernel_daemon |
| psychoanalysis/cn_oracle_trigger.py | DESCARTAR | n/a (stub mesh topic opcional) |
| psychoanalysis/creative_psychotization_operator.py | PORTAR | omni_coworker/psychoanalysis/ |
| psychoanalysis/lacanian_structures.py | PORTAR (parcial) | omni_coworker/psychoanalysis/ |
| psychoanalysis/negative_capability.py | PORTAR | omni_coworker/psychoanalysis/ |
| psychoanalysis/plasticity_context_resource.py | ADAPTAR (subset) | omni_coworker/psychoanalysis/ |
| psychoanalysis/bion_patches/__init__.py | ADAPTAR | omni_coworker/psychoanalysis/bion_patches/__init__.py |
| psychoanalysis/bion_patches/bion_grid.py | ADAPTAR | omni_coworker/psychoanalysis/bion_patches/ |
| psychoanalysis/bion_patches/bion_links.py | ADAPTAR | omni_coworker/psychoanalysis/bion_patches/ |
| psychoanalysis/bion_patches/bion_vertex.py | ADAPTAR | omni_coworker/psychoanalysis/bion_patches/ |
| psychoanalysis/bion_patches/container_contained.py | PORTAR | omni_coworker/psychoanalysis/bion_patches/ |
| psychoanalysis/bion_patches/knowledge_link_extension.py | ADAPTAR | omni_coworker/psychoanalysis/bion_patches/ |
| psychoanalysis/bion_patches/ultimate_reality.py | ADAPTAR | omni_coworker/psychoanalysis/bion_patches/ |
| psychoanalysis/bion_patches/integration_wrapper.py | ADAPTAR | omni_coworker/psychoanalysis/bion_patches/ |
| psychology/__init__.py | ADAPTAR | omni_coworker/psychology/__init__.py |
| psychology/desire_engine/__init__.py | ADAPTAR | omni_coworker/psychology/desire_engine/__init__.py |
| psychology/desire_engine/core.py | PORTAR | omni_coworker/psychology/desire_engine/ |
| psychology/motivation/__init__.py | ADAPTAR | omni_coworker/psychology/motivation/__init__.py |
| psychology/motivation/achievement_system.py | ADAPTAR | omni_coworker/psychology/motivation/ |
| psychology/motivation/hawking_motivation.py | PORTAR | omni_coworker/psychology/motivation/ |
| psychology/motivation/intrinsic_rewards.py | PORTAR | omni_coworker/psychology/motivation/ |
| psychology/stress/tribunal.py | DESCARTAR | n/a |
| psychology/scars/trauma_integration.py | PORTAR | omni_coworker/psychology/scars/ |
| narrative_consciousness/__init__.py | ADAPTAR | omni_coworker/narrative_consciousness/__init__.py |
| narrative_consciousness/dialogue_engine.py | ADAPTAR | omni_coworker/narrative_consciousness/ |
| narrative_consciousness/identity_construction.py | PORTAR | omni_coworker/narrative_consciousness/ |
| narrative_consciousness/life_story_model.py | PORTAR | omni_coworker/narrative_consciousness/ |

## Síntese de integração

**Sobreposições com o worker existente:**
- O sovereign tem shared_workspace (src.consciousness.shared_workspace) e integration_loop próprios; o worker já tem os seus (shared_workspace + sqlite WAL + /mesh/*, integration_loop 5 estágios numpy). O que existe nos sovereign e falta nos nossos: (a) BionContainerPatch com degraded reverie (evita evacuação em trauma) — nosso loop não tem contenção elástica; (b) Grid de Bion (classificação definition/use) — nenhum estágio atual classifica elementos em coordenadas; (c) Links L/H/K e K/-K — modulação afetiva/epistêmica do processamento; (d) NegativeCapability (buffer de contradições) — nosso loop não tolera incerteza em suspensão; (e) RSI modulator (ajusta transformation_rate por registro R/S/I) — nosso loop não modula taxa de transformação.
- Lacanian structures: RSI + IntrospectionGate (memoryAbsenceClaimForbidden) — nosso kernel_daemon não tem gate binário de introspecção; candidato a feature do kernel_daemon.
- Dodecatiad: alpha_element já computa sector15/house12 via hash — compatível com soul/dodeca do worker (merge direto).

**Lacunas genuinamente novas (nenhuma camada atual computa):**
- Metacognição: self-agency/reality monitoring (plasticity_context_resource) traz source monitoring + reality monitoring + metacognitive discrepancy — nenhum estágio atual computa isso; candidato a novo estágio do integration_loop ou tópico 'agency' da malha.
- Desejo como falta (desire_engine/core + intrinsic_rewards): lack_of_being, jouissance topology, drives — nosso worker não tem modelo de motivação intrínseca; candidato a tópico 'agency' e input do swap_scheduler.
- Evaporação de conhecimento (hawking_motivation): urgência por não-uso; candidato a store/code_index (evaporar embeddings antigos) + kernel_daemon.
- Trauma/cicatrizes (trauma_integration): regras de defesa permanentes consultadas antes de decisão; candidato a store/state_guard.
- Narrativa retroativa (life_story_model, identity_construction): Nachträglichkeit + web of belief; nosso loop tem stage 'narrative' mas sem resignificação retroativa nem identidade evolutiva; candidato a enriquecer stage narrative e publicar tópico 'narrative'.
- Classificação de regime (creative_psychotization_operator): overflow vs metabolização vs sanctuary; candidato a estágio final do loop (decide capture vs pause).

**O que cortar (custo CPU/GPU):**
- cn_oracle_trigger (quantum oracle/AWS), stress/tribunal (stubs rede), cannabis/psychedelic/prohibition resource lanes (fora de escopo, mas manter self-agency/theta/PAC/gene), LLM calls locais (trocar para worker endpoints :8098/:8099 ou fallback MiniLM CPU), structlog (→ logging), neutrosophic_metrics (reimplementar ou tornar Optional), thermodynamic_decorator.cycle_burn (ausente), src.core/quantum/consciousness deps (inexistentes).

**Ordem sugerida de port (P0→P2):**
- P0: alpha_element, beta_element, negative_capability, container_contained, creative_psychotization_operator, identity_construction, life_story_model, trauma_integration, hawking_motivation (CPU puro, alto valor).
- P1: bion_alpha_function + bion_symbolizer (adaptar LLM), bion_grid, bion_links, knowledge_link_extension, bion_rsi_modulator, desire_engine, intrinsic_rewards, lacanian_structures (parcial), plasticity subset.
- P2: bion_vertex, ultimate_reality, integration_wrapper, dialogue_engine, achievement_system.
- DESCARTAR: cn_oracle_trigger, stress/tribunal.
