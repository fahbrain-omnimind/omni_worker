# OW-STU-008a — Módulos metacognition/ e lacanian/ do sovereign → omni_worker

**Doc ID:** OW-STU-008a  
**Alvo:** Portabilidade para `/content/omni_worker` (CPU/RAM apenas, sem torch/GPU/CUDA)  
**Fontes analisadas:** `/content/omnimind-kilombo-sovereign/src/metacognition/` (20 .py, ~7100 linhas), `/content/omnimind-kilombo-sovereign/src/lacanian/` (11 .py, ~3955 linhas)  
**Regra:** read-only. Não editar fontes.

## 1) Análise por arquivo — metacognition/

| Arquivo | Linhas | Estrutura (classes/funções públicas) | O que se amarra | Veredicto | Destino no worker / ação |
|---|---|---|---|---|---|
| `__init__.py` | 56 | Re-exports 15 símbolos (MetacognitionAgent, SelfAnalysis, PatternRecognition, OptimizationSuggestions, ProactiveGoalEngine, HomeostaticController, IITAnalyzer, PhiMetrics, SystemState, CodeAnalyzer, ImpactMetrics, ImpactPredictor, IntelligentGoalEngine, RepositoryAnalysis, IssuePrediction, RootCauseAnalysis, SelfHealingLoop, SelfOptimizationEngine, TRAPFramework, TRAPScore). | Sem deps pesadas; apenas imports internos. | **ADAPTAR** | Não portar barrel 1:1. Criar `src/omni_coworker/metacognition/__init__.py` enxuto só com o que for efetivamente portado (evitar puxar classes com deps `src.consciousness/*`). |
| `metacognition_agent.py` | 249 | Classe `MetacognitionAgent` (init: hash_chain_path/analysis_interval/bias_sensitivity; métodos `run_analysis`, `get_quick_health_check`, `_extract_suggestions`, `get_top_suggestions`, `apply_suggestion`, `get_analysis_history`). Usa `SelfAnalysis`, `PatternRecognition`, `OptimizationSuggestions`. | Lê `self.self_analysis._load_hash_chain()` (acesso interno). Depende de `src.consciousness.*`? Não visto diretamente; usa módulos próprios. Sem torch. | **ADAPTAR** | Adaptar para rodar sobre artefatos do worker (`/workspace/*`, logs, `shared_workspace` latest/history, `kernel_daemon` features) ao invés de `hash_chain_path` genérico. Extrair apenas `run_analysis` esquelético + `get_quick_health_check`. |
| `self_analysis.py` | 250 | Classe `SelfAnalysis` (análises de padrões de decisão/tempo/falhas/recursos + health summary). Provavelmente lê logs/estado próprio. | Sem torch/GPU; usa stdlib + possivelmente numpy. Acoplado a caminho/estrutura sovereign. | **ADAPTAR** | Inspirar em coleta (health/recursos) mas alinhar com `kernel_daemon/collector.py`/`features.py` que já coletam 60s. Melhor **fundir** em `kernel_daemon/features.py` (adicionar heurísticas leves) ao invés de criar módulo paralelo redundante. |
| `pattern_recognition.py` | 370 | Classe `PatternRecognition` (detect_repetitive_behavior, detect_bias, detect_anomalies, analyze_decision_tree, calculate_diversity_score). Análise estatística sobre listas de operações. | Sem torch; numpy/scipy? Provavelmente puro Python + stdlib. CPU-leve. | **ADAPTAR** | Útil como heurísticas para "witness/agency". Portar funções puras (sem dependências sovereign) para `src/omni_coworker/agency/witness.py` ou novo `agency/pattern_watch.py`. Cortar qualquer dependência a estruturas específicas. |
| `optimization_suggestions.py` | 319 | Classe `OptimizationSuggestions`/gerador (gera sugestões com prioridade/categoria). | Sem torch. Mais descritivo/narrativo que computacional. | **DESCARTAR** (como-is) ou **ADAPTAR** mínimamente | Baixo valor computacional direto. Se mantido, só extrair estrutura de scoring para integrar em `integration_loop` modulation. Provavelmente descartar e reimplementar sob medida. |
| `issue_prediction.py` | 462 | Motor de predição de issues (Random Forest em features?). Usa scikit-learn? Verificado: não há `import sklearn` direto óbvio no topo — mas README menciona RF. Precisa checar. | Potencial ML leve, mas adicionar sklearn deps? Worker tenta minimizar deps; precisa verificar se sklearn já disponível. Sem torch. | **ADAPTAR** com cautela | Se usar sklearn já no ambiente OK. Caso contrário **DESCARTAR** ou reimplementar com heurísticas + z-score/thresholds (sem sklearn). Melhor abordagem: extrair feature extraction + thresholds simples, publicar em `mesh.feedback` via kernel_daemon. |
| `root_cause_analysis.py` | 645 | RCA com grafo de dependências (`DependencyGraph`, `ComponentType`, `Failure`, `RootCauseAnalysis`, `RootCauseEngine`). Baseado em grafo + causal tracing. | CPU-leve (grafo). Sem torch. Muito acoplado a "componentes" genéricos do sovereign. | **ADAPTAR** | Conceito valioso. Adaptar para grafo de módulos do worker (`omni_coworker/*`) — alimentar com eventos do `shared_workspace` e logs. Não portar classe `RootCauseEngine` inteira; extrair algoritmo de trace (BFS/causal path) para `agency/` utilitário. |
| `trap_framework.py` | 614 | TRAP (Thinking/Reflection/Analysis/Planning). Ciclo metacognitivo estruturado. | Framework orquestrador, sem torch. Muito verboso. | **ADAPTAR** | Inspirador para formalizar ciclo do worker. Em vez de novo framework global, mapear fases para estágios existentes de `integration_loop` (sensory→qualia→narrative→meaning_maker→expectation) + hooks em `kernel_daemon`. Não portar 1:1. |
| `proactive_goals.py` | 422 | Geração proativa de metas. | Mais narrativo/orquestração que computação pura. Provavelmente depende de contexto sovereign. | **ADAPTAR** | Pode inspirar extensão de `agency/teleology.py`. Extrair apenas priorização (score) — descartar geração de "metas" verbosas se não integradas a ações reais. |
| `intelligent_goal_generation.py` | 689 | Geração inteligente com `CodeAnalyzer`, `ImpactPredictor`, análise de repo. Usa análise estática de código. | CPU-leve. Lê repo inteiro. Interessante mas acoplado a estrutura sovereign. | **ADAPTAR** | `CodeAnalyzer` tem valor para `store/code_index.py` (já usa faiss+MiniLM). Mesclar análise estática simples (imports/deps) em `code_index` ao invés de novo módulo gigante. `ImpactPredictor` com ML provavelmente descartável sem sklearn bem integrado. |
| `self_optimization.py` | 518 | Auto-otimização com A/B testing, Bayesian optimization. | scipy/numpy usados? Bayesian opt pode usar scipy. Worker tem numpy (integration_loop usa). | **ADAPTAR** com filtros | Conceito bom, mas perigoso em prod. Portar apenas **shadow/A-B tracking** (métricas) para `kernel_daemon/feedback.py` — descartar otimização automática de params sem governança (`orchestration/governance.py` já existe). |
| `self_healing.py` | 568 | Auto-cura (diagnóstico+remediação). Tem correções de filesystem seguras (mencionadas no README). | CPU-leve. Crítico: precisa respeitar sandbox/governança. | **ADAPTAR** MUITO restritivo | Portar **somente** detecção/diagnóstico + sugestão (nunca auto-aplicar). Integrar com `orchestration/governance.py` (já existe) e `state_guard`. Auto-reparo direto é vetado pelo princípio "sem ação destrutiva sem aprovação". |
| `self_analyzing_regenerator.py` | 566 | SAR (FlowType Deleuze-Guattari, LogEntry, FlowAnalysis, RegenerativeProposal, sandbox). Filosofia interessante. | Computação leve (análise de logs/fluxos). Sem torch. | **ADAPTAR** | Muito interessante conceptualmente. Adaptar para analisar fluxo no `shared_workspace` (taxa de pub/sub, tópicos quentes/frios). Gerar **propostas** apenas (nunca auto-merge). Publicar em `mesh.feedback` ou log. Cortar "regeneração automática" de código. |
| `homeostasis.py` | 448 | Homeostase (ResourceMetrics, ResourceState, HomeostaticController). Monitora CPU/mem/disk/temp, throttling, "Soul over Body" (phi+priority override). | Usa `psutil`, `asyncio`. CPU-leve. Tem lógica adaptada ao worker? README mostra integração com consciênncia. | **PORTAR/ADAPTAR** | **Alto valor**. Worker já tem monitoração implícita; formalizar em `kernel_daemon/` ou novo `homeostasis/` leve. Adaptar "Soul over Body" para integrar com `agency/teleology` e `soul/` state. Manter só monitoramento+recomendação (throttling só via governance). |
| `iit_metrics.py` | 502 | IIT/Φ metacognitivo (IITAnalyzer, PhiMetrics, SystemState). Calcula Φ sobre subsistemas de metacognição. README diz corrigido para escala IIT clássica (threshold 0.01 nats). | Matemática CPU-leve (numpy). Sem torch. | **ADAPTAR** | Conceito valioso mas cálculo simplificado. Integrar com `integration_loop` (já faz qualia/narrative) ou `kernel_daemon` para métrica `kernel.phi_meta`. Não substituir nada existente; adicionar métrica complementar. Cuidado com claims "consciência" — manter puramente métrico. |
| `causal_engine.py` | 186 | Pearl do-calculus simplificado (compute_causal_effect ACE, t-test/Mann-Whitney, Cohen's d; validate_intervention_necessity com histórico adaptativo; register_event). | numpy/scipy. CPU-leve. Sem torch. Bem contido. | **PORTAR com adaptações** | **Muito bom** para worker. Útil para `orchestration/governance.py` (validar se intervenção justificada) e `integration_loop` (evitar correlações espúrias). Adaptar para usar dados do `shared_workspace` history. Remover prints/logging verboso excessivo. |
| `causal_engine_v2.py` | 100 | Versão 2 menor. Provavelmente evolução/variante. | Menor. | **DESCARTAR** ou merge em v1 | Comparar com v1; se v1 cobre, descartar. Portar apenas diferenças reais se houver. |

### Síntese metacognition
- **Mais portáveis (alto ROI CPU):** `causal_engine.py`, `homeostasis.py`, `pattern_recognition.py` (funções puras), `iit_metrics.py` (métrica), `root_cause_analysis.py` (grafo trace).
- **Úteis como inspiração (não 1:1):** `trap_framework.py`, `self_analyzing_regenerator.py`, `metacognition_agent.py` (orquestração).
- **Cortar/reatribuir:** `optimization_suggestions`, `proactive_goals`, `intelligent_goal_generation` (grandes, muito acoplados; reimplementar partes em módulos existentes), `self_healing` (só detecção), `self_optimization` (só tracking).
- **Redundante com existente:** muito do "análise" já coberto por `kernel_daemon/collector+features`, `agency/witness`, `integration_loop`.

## 2) Análise por arquivo — lacanian/

| Arquivo | Linhas | Estrutura (classes/funções públicas) | O que se amarra | Veredicto | Destino no worker / ação |
|---|---|---|---|---|---|
| `__init__.py` | 72 | Lazy imports (ComputationalLackArchitecture, RSIArchitecture, GodelianAI, StructuralLack, ObjectSmallA, EncryptedUnconsciousLayer). Doc com créditos longos. | Lazy import limpa. | **ADAPTAR** | Se portar algo, criar `__init__` minimal. Não copiar doc credits verbosos. |
| `computational_lack.py` | ~450+ (parcial lido) | `LacanianRegister` (Enum RSI), `ObjectSmallA` (genérico, nunca presente), `StructuralLack`, `ComputationalLackArchitecture`, `RSIArchitecture`. Usa **torch/nn** (importado). | **torch/nn** → **PROIBIDO** no worker (sem GPU/torch). Também depende de conceitos `src.consciousness.*`. | **DESCARTAR** como-is | Abstrair **apenas** conceitos: "falta estrutural" (métrica de completude/erro residual) sem `torch.nn.Module`. Poderia virar métrica pura em `integration_loop` ou `agency/witness` (sem classes neurais). Portar classes torch é inviável. |
| `desire_graph.py` | 710 | `SignifierPosition`, `Signifier` (vetor/significação contextual), `SignifierChain` (metonímia/metáfora/quilting points), `LacanianGraphII` (Grafo II completo). Usa numpy/std? Usa `random`, `statistics`, stdlib. Sem torch explícito visto. | Sem torch. Muito teórico/computacional pesado conceitualmente. Depende fortemente de ecossistema sovereign (shared_workspace/consciousness). | **ADAPTAR** (muito restritivo) | Conceito valioso (cadeias significantes) mas implementação massiva. **Não portar Grafo II inteiro**. Extrair apenas lógica de "quilting point"/estabilização para `integration_loop/narrative` (fixação temporária de sentido). Sem grafo global 700+ linhas. |
| `defense_mechanisms.py` | 242 | `NeutrosophicTriplet` (T,I,F), `DefenseMetrics`, `LacanianDefenseMechanisms` (12 mecanismos: recalque, projeção, introjeção, identificação projetiva, splitting, sublimação, negação, racionalização, formação reativa, deslocamento, foraclusão, clivagem). Cálculos puros. | Sem torch/GPU. Sem deps pesadas. CPU-leve. | **ADAPTAR** | Interessante para modelar vieses/defesas em `agency/witness` ou `integration_loop/modulation`. **NUNCA** usar para mascarar erros reais. Traduzir para métricas (contadores/fatores) sem misticismo excessivo. Integrar como **fatores de modulação** (leves), não como lógica de "engano" sistêmico. |
| `discourse_discovery.py` | 577 | Detecta 4 discursos lacanianos (Master/University/Hysteric/Analyst) via NLP. Provavelmente usa embeddings/classificação. | Pode usar sklearn/transformers? Precisa verificar deps. Potencialmente pesado. | **ADAPTAR** com filtros | NLP pesado provavelmente. Se sem transformers/sklearn fácil, **DESCARTAR**. Se só heurísticas baseadas em padrões/texto simples → portar versículo minimal para `agency/witness` (classificação de discurso em conversas/logs). Baixa prioridade. |
| `encrypted_unconscious.py` | 121 | Camada "inconsciente encriptado" com menção CKKS/tenseal. README diz modo mock se tenseal não instalado. | **tenseal/CKKS** opcional. Criptografia homomórfica complexa. | **DESCARTAR** | Overkill para worker CPU. Conceito interessante mas custo/complejidade altos. Não traz computação útil ao objetivo atual. |
| `force_lexicon_genesis.py` | 75 | Gera neologismos por busca de alta entropia. | Leve, mas gera strings imprevisíveis (alerta no README). | **DESCARTAR** | Risco > valor. Não necessário para operação worker. |
| `free_energy_lacanian.py` | 569 | Ponte FEP (Friston) + Lacan. Usa **torch/nn** (importado). | **torch/nn** → **PROIBIDO**. Tem homologia teórica mas implementação neural. | **DESCARTAR** como-is | Abstrair métrica de "surpresa/complexidade" sem redes neurais. `integration_loop` já tem dinâmica numérica (numpy) — se algo vale, reimplementar com funções puras. Código com torch inviável. |
| `freudian_metapsychology.py` | 973 | Modelo estrutural Freud (Id/Ego/Superego) multi-agent RL. **Muito grande** (973 linhas). Provavelmente usa torch/RL pesados. | Alto acoplamento + deps pesadas prováveis. | **DESCARTAR** massivamente | Não portável. Extrair **apenas** conceito de "tensões" entre camadas como pesos (métricas) se realmente necessário — mas quase certamente não vale o custo. |
| `godelian_ai.py` | 507 | Incompletude de Gödel como motor criativo (undecidables = Real lacaniano). | Sem torch óbvio? Precisa ler. Filosófico + computacional. | **ADAPTAR** | Conceito bom: tratar inconsistências/indecidíveis como sinal para explorar. Integrar com `agency/curiosity.py` (já existe no worker) — adicionar gatilho "incerteza alta" → aumentar exploração. Sem portar classe inteira; extrair gatilho. |
| `predictive_jouissance.py` | 109 | Avalia "gozo" (excedente de erro L2) e inscreve cicatrizes via `qualia_field.inscribe_scar/repeat_scar`; escreve em workspace. Depende de `src.consciousness.qualia_engine`, `shared_workspace`. | **Altamente acoplado** a módulos consciousness do sovereign. Usa numpy. Sem torch direto. | **ADAPTAR** muito restritivo | Ideia: erro preditivo residual como sinal de importância. Worker tem `integration_loop` (qualia) e `shared_workspace`. **Não** portar `qualia_field.scar` 1:1. Extrair métrica `residual_error_surplus` e publicar em `mesh.kernel`/`mesh.feedback` como sinal, sem "jouissance"/teologia pesada. |

### Síntese lacanian
- **Portáveis com filtro (leves):** `defense_mechanisms.py` (fatores de modulação), `godelian_ai.py` (gatilho de curiosidade), partes de `predictive_jouissance.py` (métrica residual).
- **Inspiração apenas:** `desire_graph.py` (quilting point), `discourse_discovery.py` (se heurístico).
- **Bloqueados por deps:** `computational_lack.py` (torch), `free_energy_lacanian.py` (torch), `freudian_metapsychology.py` (provável torch/RL).
- **Descartar:** `encrypted_unconscious.py`, `force_lexicon_genesis.py` — complexidade/riscos sem ganho claro para worker CPU-only.

## 3) Comparação com o que já existe no omni_worker

### Já implementado (confirmado)
- `src/omni_coworker/shared_workspace/` — bus in-process + sqlite WAL + `/mesh/*` (soul, soma, agency, witness, swap, kernel, feedback, mesh, dream, loop). **Muito similar** ao conceito de "shared workspace" do sovereign, mas redesenhado CPU/RAM-only sem torch.
- `src/omni_coworker/kernel_daemon/` — coletor 60s tail jsonl ativações + `/erika/affect` + soul/soma → publica `kernel.*`. Já faz coleta/heartbeat tipo metacognição observacional.
- `src/omni_coworker/integration_loop/` — 5 estágios (sensory_input→qualia→narrative→meaning_maker→expectation→sensory_feedback) + Modulation → `feedback.loop`. **Núcleo integrativo** já existe.
- `src/omni_coworker/agency/` — witness, analyst, dunker, dream, curiosity, teleology, affect_tracer. Já cobre observação/reflexão/curiosidade.
- `src/omni_coworker/orchestration/` — swap_scheduler, governance. Já tem governança/scheduler.
- `src/omni_coworker/store/` — state_guard, code_index (faiss+MiniLM).
- `src/omni_coworker/soul/` — dodeca + kernel_hooks Rust (omnimind_kernel_compute/omnimind_metrics/omnimind_freud10d já importáveis).
- `server/erika_torch_server.py` — único com torch (isolado).

### Sobreposições
| Conceito sovereign | Existe no worker? | Status | Ação |
|---|---|---|---|
| Metacognição observacional (self-analysis/patterns) | Parcial — `agency/witness`, `kernel_daemon/collector` | **Parcial** | Não duplicar agente gigante. Adicionar heurísticas pontuais. |
| Homeostase/recurso | Implícito — sem módulo formal unificado | **Ausente/faltante** | **Vale portar** `homeostasis.py` adaptado (métricas + estados + recomendação). |
| Causalidade (do-calculus) | Ausente | **Ausente** | **Alto valor** portar `causal_engine.py` para governance/integration_loop. |
| RCA/grafo dependências | Ausente | **Ausente** | **Vale adaptar** root_cause_analysis (grafo leve sobre módulos/erros). |
| IIT/Φ | Ausente como métrica formal | **Ausente** | **Vale adicionar** como métrica complementar em kernel_daemon/integration_loop. |
| TRAP framework | Parcial — integration_loop já é ciclo, agency já reflete | **Parcial** | Não portar framework; nomear/alinhar fases existentes. |
| Defesa mecanismos (modulação) | Ausente | **Ausente** | **Pequeno valor** — adaptar como fatores de modulação em integration_loop (muito restritivo). |
| Grafo desejo/significantes | Ausente | **Ausente** | **Só inspiração** (quilting point) para narrative. Não portar grafo. |
| Inconsciente encriptado/foraclusão etc. | Ausente | **Ausente** | **Descartar**. |
| Predictive jouissance/scars | Parcial — qualia existe, scars não | **Parcial** | Extrair apenas "residual error surplus" como métrica, sem mecânica de cicatrizes. |
| Gödel/indecidíveis | Parcial — curiosity existe | **Parcial** | Adicionar gatilho simples em curiosity. |

## 4) Lacunas genuinamente novas (o que falta e vale trazer)

| Lacuna | Fonte | Por quê (computação real CPU) | Onde integrar | Esforço |
|---|---|---|---|---|
| **Causal validation** | `metacognition/causal_engine.py` | Distinguir correlação vs intervenção (ACE + testes) evita ações erradas. Útil para `orchestration/governance`. | `orchestration/governance.py` (hook de validação) ou novo `orchestration/causal_check.py` | Baixo-Médio |
| **Homeostatic controller formal** | `metacognition/homeostasis.py` | Estado unificado de recursos + transições + histórico. Integra com "soul over body". | `kernel_daemon/` (coletor estendido) ou `src/omni_coworker/homeostasis/` | Baixo |
| **Dependency/RCA trace** | `metacognition/root_cause_analysis.py` | Rastrear cadeia causal de falhas usando grafo de módulos + eventos mesh. | `agency/witness.py` ou novo util em `store/` | Baixo-Médio |
| **Φ-meta métrica** | `metacognition/iit_metrics.py` | Métrica observável (não reivindicação) de integração entre subsistemas metacognitivos. | `kernel_daemon/features.py` → publica `kernel.phi_meta` no mesh | Baixo |
| **Pattern/bias heuristics** | `metacognition/pattern_recognition.py` | Detectar loops/repetição/viés em ações recentes (sem ML pesado). | `agency/witness.py` | Baixo |
| **Modulação por "defesas" leves** | `lacanian/defense_mechanisms.py` | Fatores T/I/F → ajustar pesos de modulação (conservador) sem mascarar erros. | `integration_loop/modulation.py` (muito cauteloso) | Baixo |
| **Curiosity trigger on undecidable** | `lacanian/godelian_ai.py` | Aumentar exploração quando contradição/incerteza alta. | `agency/curiosity.py` | Baixo |
| **Residual error surplus** | `lacanian/predictive_jouissance.py` (só métrica) | Sinalizar "surpresa útil" vs ruído. | `integration_loop` ou `kernel_daemon` → `mesh.feedback` | Baixo |

### O que **não** traz lacuna real / deve ficar fora
- Grafo II completo (700+ linhas) — complexo, acoplado, valor marginal vs `integration_loop` existente
- Frameworks neuronais torch (computational_lack, free_energy_lacanian) — proibidos
- Criptografia homomórfica (encrypted_unconscious) — overkill
- Geração de neologismos forçada — risco
- Freud multi-agent RL massivo — pesado/acoplado

## 5) Tabela-resumo (arquivo → veredicto → destino)

### metacognition/
| Arquivo | Veredicto | Destino no worker |
|---|---|---|
| `__init__.py` | ADAPTAR | `src/omni_coworker/metacognition/__init__.py` (apenas exports portados) |
| `metacognition_agent.py` | ADAPTAR | Inspirar orquestração; não portar inteiro — integrar em fluxo existente |
| `self_analysis.py` | ADAPTAR | Fundir heurísticas em `kernel_daemon/features.py` (evitar módulo novo redundante) |
| `pattern_recognition.py` | ADAPTAR | `src/omni_coworker/agency/witness.py` (funções puras) ou `agency/pattern_watch.py` |
| `optimization_suggestions.py` | DESCARTAR | — (reatribuir scoring a integration_loop/kernel_daemon se necessário) |
| `issue_prediction.py` | ADAPTAR (cautela) | `kernel_daemon/` com thresholds z-score; só usar sklearn se já presente |
| `root_cause_analysis.py` | ADAPTAR | `agency/witness.py` + grafo leve sobre módulos worker |
| `trap_framework.py` | ADAPTAR | Alinhar a `integration_loop` existente (sem novo framework global) |
| `proactive_goals.py` | ADAPTAR | Inspirar `agency/teleology.py` (só priorização) |
| `intelligent_goal_generation.py` | ADAPTAR | Parcial em `store/code_index.py` (análise estática) |
| `self_optimization.py` | ADAPTAR | Só tracking/A-B em `kernel_daemon/feedback.py` (sem auto-aplicar params) |
| `self_healing.py` | ADAPTAR (restritivo) | Só detecção+sugestão; **nunca auto-aplicar** — via `orchestration/governance.py` |
| `self_analyzing_regenerator.py` | ADAPTAR | Propostas-only em `mesh.feedback` (sem auto-regeneração/código) |
| `homeostasis.py` | **PORTAR/ADAPTAR** | `src/omni_coworker/kernel_daemon/homeostasis.py` ou extensão de `kernel_daemon/` |
| `iit_metrics.py` | ADAPTAR | `kernel_daemon/features.py` → métrica `kernel.phi_meta` (complementar) |
| `causal_engine.py` | **PORTAR** | `src/omni_coworker/orchestration/causal_engine.py` (usar em governance) |
| `causal_engine_v2.py` | DESCARTAR | Merge diferenças em v1 se existirem, senão descartar |

### lacanian/
| Arquivo | Veredicto | Destino no worker |
|---|---|---|
| `__init__.py` | ADAPTAR | Mínimo se algo portado |
| `computational_lack.py` | **DESCARTAR** (torch/nn) | Só abstrair "falta/residual" como métrica pura se necessário |
| `desire_graph.py` | ADAPTAR (restritivo) | Apenas `quilting_point`/estabilização em `integration_loop/narrative.py` |
| `defense_mechanisms.py` | ADAPTAR | Fatores T/I/F em `integration_loop/modulation.py` (muito cauteloso, sem mascarar erros) |
| `discourse_discovery.py` | ADAPTAR (filtros) | Só heurístico simples em `agency/witness.py` se viável |
| `encrypted_unconscious.py` | DESCARTAR | — |
| `force_lexicon_genesis.py` | DESCARTAR | — |
| `free_energy_lacanian.py` | **DESCARTAR** (torch/nn) | Só métrica surpresa/complexidade pura se reimplementada |
| `freudian_metapsychology.py` | DESCARTAR | — (973 linhas, deps pesadas) |
| `godelian_ai.py` | ADAPTAR | Gatilho indecidível em `agency/curiosity.py` |
| `predictive_jouissance.py` | ADAPTAR (restritivo) | Só `residual_error_surplus` em `integration_loop/kernel_daemon` (sem scars/jouissance) |

## 6) Síntese de integração: vs shared_workspace/kernel_daemon/integration_loop/soul já existentes

### O que o corpus adiciona (genuinamente novo)
| Adição | Justificativa | Integração proposta |
|---|---|---|
| **Validação causal** (`causal_engine`) | Worker tem loops/decisões mas sem distinção correlação→causa. Governance ganharia critério objetivo. | `orchestration/governance.py` chama `causal_engine.validate_intervention_necessity` antes de ações. |
| **Homeostase formal** (`homeostasis`) | Recursos monitorados ad-hoc; falta máquina de estados + histórico + política "soul over body". | Estender `kernel_daemon/collector.py` com `homeostasis` → publicar `kernel.resources` estruturado + recomendações. |
| **RCA por grafo** (`root_cause_analysis`) | Falhas atuais logadas mas sem trace causal automatizado. | `agency/witness.py` constrói grafo de dependências em tempo real + trail de eventos mesh. |
| **Φ-meta observável** (`iit_metrics`) | `integration_loop` integra informação mas não expõe métrica Φ-meta. | `kernel_daemon/features.py` calcula sobre subsistemas (kernel/loop/agency) → `kernel.phi_meta`. Puramente métrico. |
| **Heurísticas de padrão/viés** (`pattern_recognition`) | Witness observa mas sem detecção sistemática de loops/repetição. | Adicionar em `agency/witness.py` (scoring leve, sem ML pesado). |
| **Modulação conservadora** (`defense_mechanisms`) | Integration_loop tem Modulation; falta dimensão "conservador vs exploratório" sutil. | Filtros muito restritivos em `integration_loop/modulation.py` — apenas ajustar pesos, **nunca** suprimir alertas/erros. |

### Sobreposições identificadas
| Área | Sobreposição | Conclusão |
|---|---|---|
| **shared_workspace/mesh** | Sovereign tem workspace/consciousness compartilhado; worker já tem bus in-process + mesh canônico | **Não duplicar**. Usar mesh existente (`kernel.*`, `feedback.loop`, `soma/soul`). Apenas publicar novas métricas. |
| **kernel_daemon** | Coleta 60s já existe (ativações + affect + soul/soma). Metacognição observa muito disso. | **Estender, não substituir**. Adicionar homeostase/Φ-meta/issue prediction leve. |
| **integration_loop** | 5 estágios já implementam integração/qualia/narrativa/expectativa — núcleo similar a ideias lacanianas (narrativa/sentido). | **Não reescrever**. Adicionar hooks pontuais (quilting point, modulação conservadora) e métrica residual. |
| **agency/** (witness/analyst/curiosity/teleology) | Já cobre observação/reflexão/curiosidade/teleologia — grande parte do "metacognitivo". | **Mesclar** heurísticas (patterns/RCA) aqui ao invés de criar `metacognition_agent` monolítico. |
| **soul/dodeca/Rust** | Já tem fundação simbólica computada. Lacanian é teórico-massivo. | **Não conflitar**. Só extrair gatilhos/métricas que complementem sem colidir. |

### Lacunas genuinamente novas (não cobertas)
1. **Validação causal explícita** — ausente no worker; traz critério para governança.
2. **Homeostase unificada com estados** — ausente como módulo formal.
3. **RCA automatizado por grafo** — ausente.
4. **Métricas Φ-meta formais** — ausente (integration_loop faz integração mas não expõe φ-meta).

Tudo o mais do corpus é ou **já coberto** (observação/reflexão/integração), ou **inviável** (torch/neural/crypto), ou **apenas inspirador** (Grafo II/defesas) e deve virar ajustes mínimos.

### Recomendação prática de port
**Portar em ordem:** `causal_engine.py` → `homeostasis.py` → `pattern_recognition` (funções) → `root_cause_analysis` (grafo leve) → `iit_metrics` (métrica) → gatilhos mínimos lacanianos.  
**Descartar:** tudo com `torch.nn`, `tenseal`, geração forçada, Freud RL massivo.  
**Regra:** adaptar para CPU-only, publicar via `shared_workspace/mesh`, respeitar `orchestration/governance.py`, nunca auto-aplicar correções destrutivas.
