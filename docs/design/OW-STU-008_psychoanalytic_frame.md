# OW-STU-008a — Módulos metacognition/ e lacanian/ do sovereign → omni_worker

> [!NOTE] Proveniência Arquitetural e Portabilidade
> As referências a `/content/omnimind-kilombo-sovereign` documentam a auditoria técnica do repositório privado de referência do autor, realizada durante o design de portabilidade. No `omni_worker`, os componentes portados para `src/omni_coworker/psychoanalysis/`, `kernel_daemon/homeostasis.py` e `governance.py` são 100% autônomos e funcionam sem qualquer dependência de arquivos externos ou privados.

**Doc ID:** OW-STU-008a  
**Alvo:** Portabilidade para `/content/omni_worker` (CPU/RAM apenas, sem torch/GPU/CUDA)  
**Fontes analisadas (referência privada do autor):** `/content/omnimind-kilombo-sovereign/src/metacognition/` (20 .py, ~7100 linhas), `/content/omnimind-kilombo-sovereign/src/lacanian/` (11 .py, ~3955 linhas)  
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


---


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
