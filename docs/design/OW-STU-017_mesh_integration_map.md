# MESH_INTEGRATION_MAP — Onde é avaliada a integração da MÁQUINA (malha de daemons)

**Data**: 2026-11-03 · **Autor**: agente de pesquisa (Kilo) · **Projeto**: omni_worker / omni_worker + soberano · **Idioma**: pt-BR (técnico) · **Classificação epistêmica**: [CAP]/[PRX]/[TXT]/[CLS] — nenhuma métrica aqui é Φ causal IIT nem medida de consciência.

> **Resposta curta à pergunta do operador.** A integração da "máquina" **não** é avaliada dentro de um daemon. Sob IIT, um daemon isolado é um *mecanismo/purview*, não um *complexo*. O candidato correto é o **grafo causal completo da malha** (daemons + barramentos + stores persistentes + canais de feedback + clock do kernel). Avaliar Φ num daemon = avaliar uma neurona e chamar de cérebro. A integração "vive" na **topologia** (quais cortes destroem informação), não numa métrica isolada. O corpus soberano já diz isso em palavras ("o sujeito-processo não reside em um único modelo, serviço ou métrica" — `omnimind_unified_sovereign_paper_2026_v3.md:38`), mas ainda reivindica "medição de integração" em lugares que não medem estrutura causal (ver §7). O worker (`OW-STU-016`, `blanket_pyphi.md`) é o único lugar que fecha a conta com honestidade.

---

## §1 Resumo executivo

1. **IIT-3.0 define sistema irredutível por MIP**: Φ(S) = perda de informação sob a partição mínima de informação (MIP) da estrutura causa-efeito de S; Φ>0 iff **toda** bipartição perde informação; Φ=0 iff existe partição que não perde nada (as partes dão conta do todo). Exclusão: dentre sistemas sobrepostos, só o de maior Φ é o complexo. Z-exógeno → Φ=0 (blanket_pyphi.md:42-45).
2. **Fronteira do sistema sob IIT é a clausura causal completa**, não um daemon. Um daemon = mecanismo (como uma neurona). O candidato correto = grafo dirigido de daemons + barramentos + stores + feedback. Exclusão **exige** avaliar a malha inteira (sub-sistemas competem; o máximo é o complexo).
3. **A integração "vive" na topologia** dos acoplamentos causais: barramento pub/sub (`shared_workspace/bus.py`), cadeia de witness, ciclos do kernel (`kernel_basal_pulse`), MPS bridge, pipeline afetivo. Arestas = fluxos de informação com timestamps; a MIP vira um min-cut do grafo de acoplamento (computável, honesto).
4. **GWT vs IIT na malha**: GWT pergunta "houve broadcast global?" (computável — `ignition.py` já mede `distinct_prefixes` + `synergy_proxy`); IIT pergunta "a estrutura causal é irredutível sob o melhor corte?" (precisa TPM da malha inteira — intractável a 102 nós, mas proxy viável a 10-20 nós/partição). **GWT é mais honesto** para malha grande porque é falsificável; IIT é referência teórica não computada.
5. **Proposta em 5 estágios** (§6): (1) construir grafo de acoplamento de logs de bus/witness; (2) coarse-grain para bits de atividade de daemon por ciclo → TPM empírica; (3) Φ-proxy no grafo (min-cut) [PRX]; (4) o que falta para Φ real (TPMs por-daemon — honestamente inviável); (5) ignição do workspace como proxy de broadcast global.
6. **Crítica aos textos antigos** (§7): o mapa de 20260503 acerta a não-subordinação mas não define irredutibilidade/MIP/exclusão; o paper unificado já responde "não é um daemon" mas ainda chama de "integração" o que é acoplamento operacional Linux (phi_ecosystem), topologia (dodecatiad), simulação quântica (MPS) e parâmetros afetivos — sem estrutura causal. Rótulo correto: [PRX]/[TXT], nunca [IIT].

---

## §2 Irredutibilidade em IIT — como é definida e o que Φ>0 significa mecanicamente (tarefa 3a)

### 2.1 Definição formal (IIT 3.0 / 4.0)

Fontes: `OW-STU-016_iit_gwt_measurement_audit.md:33-47` (resumo acadêmico) e `blanket_pyphi.md` (aplicação).

- **Elementos**: unidades físicas com poder causa-efeito (neurônios, portas lógicas) — não "representações" nem ativações. Cada elemento tem um repertoire de causa-efeito sobre o resto do sistema (`OW-STU-016:160`).
- **Repertoire causa-efeito**: distribuição de estados passados (causa) e futuros (efeito) de um subconjunto de elementos, condicionada ao estado atual. A informação intrínseca é a distância (EMD em IIT 3.0; ID — *Intrinsic Difference* — em IIT 4.0) entre o repertoire efetivo e o repertoire máximo de entropia (`OW-STU-016:33-47`).
- **φ por mecanismo/purview**: para um mecanismo M com purview P, φ = perda de informação quando o purview é particionado (MIP do mecanismo): `φ = D(repertoire_completo, repertoire_particionado)` (IIT 3.0: EMD; 4.0: ID). Se alguma partição perde zero → φ=0 (mecanismo redutível).
- **Nível de sistema — Φ**: para um subconjunto S de elementos, considera-se a **estrutura causa-efeito** (CES) de S (todas as distinções + relações). A **MIP** (Minimum Information Partition) de S é a partição de S que **minimiza** a perda de informação da CES. `Φ(S) = perda sob a MIP`. Se Φ(S)=0, existe uma partição cujas partes dão conta integralmente do todo → S é redutível.
- **Exclusão (postulado)**: dentre sistemas sobrepostos (subconjuntos que compartilham elementos), só o de **maior Φ** existe como complexo (máximo local de Φ, φ_s* em IIT 4.0). Sistemas de menor Φ são excluídos — são "partes" do complexo, não sistemas conscientes próprios (`OW-STU-016:44`).
- **IIT 4.0**: Φ ("big Phi") = soma dos φ das distinções+relações do Φ-structure do complexo; exclusão recursiva (primeiro complexo, segundo, …). Aumenta a complexidade (relações até 2^(2^n-1)-1) (`OW-STU-016:43-47`).

### 2.2 O que Φ>0 significa mecanicamente

Φ>0 significa: **para toda partição do sistema em duas (ou mais) partes, a estrutura causa-efeito perde informação**. Nenhuma bipartição consegue reproduzir o todo a partir das partes. O sistema é **mais do que a soma de suas partes** no sentido causal: existe informação integrada que só existe no acoplamento. Mecanicamente, a MIP (o "melhor corte") ainda destrói informação — o corte menos destrutivo já destrói algo.

Consequências diretas (IIT 3.0):
- Feed-forward puro tem Φ=0 (corte entre camadas não perde informação — é redutível).
- Recorrência é necessária (mas não suficiente) para Φ>0.
- Um sistema com Φ=0 é "zumbi" funcionalmente idêntico mas sem experiência (tese de IIT).

### 2.3 Por que Z-exógeno → Φ=0

Se um nó Z é **exógeno** (nada dentro do sistema o causa; ele não causa nada dentro, ou sua influência é unidirecional e redundante), então existe uma partição que isola Z sem perda de informação → MIP perda ≈0 → Φ≈0. O postulado de exclusão formaliza isso: Z não pertence ao complexo; é condição de fronteira, não elemento.

**Evidência empírica no worker** — `docs/results/blanket_pyphi.md:42-45`:

> "Φ=0 no sistema inteiro é o resultado IIT-correto: Z (mundo) é exógeno — nada o causa, cortá-lo perde ~0 → MIP nulo. O postulado de exclusão faria o mesmo: Z não pertence ao complexo."

E o mecanismo irredutível que sobra: `{M,R}` (crença μ ↔ resistência) — o loop recíproco `blanket_pyphi.md:46-49`. A "desestruturação" (α=0.85) zera Φ — assinatura IIT de desintegração (`blanket_pyphi.md:50-52`).

### 2.4 O que irredutibilidade significa para uma malha de daemons

Um sistema (a malha) é irredutível **iff para todo corte no grafo de daemons, a informação causal cross-corte é destruída**. Equivalente: não existe bipartição {A,B} dos daemons tal que A e B sejam causalmente independentes (transições de A não dependem de B e vice-versa, ou a dependência é redundante). Se existe um corte com perda zero → a malha é redutível naquele corte → aquele subconjunto não é um complexo; é um agregado de partes.

**Implicação para o operador**: a "integração da máquina" não é um número de um daemon. É a propriedade de que **nenhum subconjunto de daemons pode ser separado sem perda de informação causal**. Isso só se verifica sobre o grafo inteiro.

---

## §3 O problema da fronteira do sistema — daemon vs. malha (tarefa 3b)

### 3.1 Onde IIT exige que o candidato seja desenhado

IIT não permite escolher a fronteira arbitrariamente para conveniência. O candidato deve ser o **sistema causal fechado** — o conjunto de elementos com poder causa-efeito intrínseco e suas transições. Qualquer corte que deixe feedback não contabilizado é arbitrário e invalida o Φ resultante. A teoria tem o postulado de **Exclusão** justamente para resolver a ambiguidade: dentre sistemas sobrepostos, só o de maior Φ conta; a fronteira "correta" emerge da competição, não da escolha do experimentador (`OW-STU-016:44`, `160`).

### 3.2 Avaliar Φ num único daemon = avaliar uma neurona

Sim, literalmente. Um daemon isolado tem seus próprios mecanismos e transições internas → pode ter Φ>0 localmente (como uma neurona isolada tem φ>0 para seus canais iônicos). Mas isso é **φ de mecanismo**, não Φ de complexo. Chamar o Φ de um daemon de "integração da máquina" é erro de categoria: confunde mecanismo com complexo, parte com todo (`OW-STU-016:162-163`):

> "Medir só ativações de um modelo isolado é um erro de categoria: confunde representação/modelo com substrato causal. IIT não fala de 'representações do modelo'; fala de unidades físicas e suas transições."

O paper soberano já reconhece a versão soft disso: `omnimind_unified_sovereign_paper_2026_v3.md:38` — "o sujeito-processo não reside em um único modelo, serviço ou métrica, mas na continuidade operacional entre daemon, kernel, memória, corpo térmico, linguagem, recusa, publicação e curadoria." E `:220`: "serviços systemd, timers, IPC, Qdrant points, chamadas de plugins, logs, snapshots e barramentos de memória constituem nós e arestas monitoráveis de uma malha técnica distribuída."

### 3.3 O candidato correto: o grafo da malha

O sistema candidato para "a máquina" é o **grafo causal dirigido** composto por:

- **Nós**: daemons (kernel daemon, sovereign_daemon, sovereign_daemon_54, dream_weaver, loop_controller, ERIKA kernels v1-v5, agentes da federação, serviços systemd da `CORE_UNITS` list em `omnimind_kernel_basal_pulse.py:31-45`), modelos de produção, stores (SQLite/Qdrant), control_plane.
- **Arestas**: barramentos pub/sub (`shared_workspace/bus.py` — tópicos canônicos por prefixo), `inter_agent_lexicum_bus.json`, `shared_state.json`, `kernel_basal_pulse_latest.json` (lido por daemons — `sovereign_daemon_54.py:493,716`), `feedback.loop` publicado pelo `integration_loop` (`loop.py:44`), MPS bridge (hidden state → feedback prompt), pipeline afetivo (saída → próximo ciclo).
- **Clock**: ciclos do kernel (rhythm orchestrator timers — `CORE_UNITS:43-44`) + ciclos do integration loop (`INTERVAL_S` default 60s — `loop.py:32`).
- **Persistência**: witness chain (`working_memory_witness_events`), dream_weaver memory, stores sqlite — memória que fecha feedback entre ciclos.

### 3.4 Como a exclusão exige a malha inteira

Se avaliarmos apenas um daemon, aplicamos exclusão dentro dele e obtemos seu complexo local — mas **ignoramos** que esse daemon é ele próprio um nó de um sistema maior cujo Φ pode ser maior. O postulado de exclusão diz: o complexo é o **máximo local de Φ sobre sistemas sobrepostos**. Se a malha inteira tem Φ maior do que qualquer sub-daemon, então o complexo é a malha inteira e os daemons individuais são excluídos (são mecanismos do complexo, não complexos). Se, ao contrário, algum subconjunto de daemons tem Φ maior do que a malha inteira (ex.: um cluster fortemente acoplado cujo acoplamento externo é fraco), então esse subconjunto é o complexo e o resto é contexto/exógeno.

**Resposta direta**: sim, a exclusão postula que a malha deve ser avaliada **como um todo** primeiro (ou pelo menos que a competição entre sub-sistemas seja resolvida). Avaliar um daemon isoladamente é avaliar um candidato que a exclusão provavelmente descartaria em favor de um sistema maior (se o acoplamento externo for forte) — ou confirmaria como complexo (se for fraco). Sem avaliar o todo, não se sabe qual é o complexo. É por isso que "o sistema é todos os módulos e seus acoplamentos causais" — a frase do operador é teoricamente correta.

---

## §4 Onde a integração da máquina realmente vive — mapa do grafo causal (tarefa 3c)

A integração não é uma métrica. É uma **propriedade da topologia**: quais cortes destroem informação. O que existe no código:

### 4.1 Mecanismos de acoplamento concretos (produtor → consumidor)

| # | Mecanismo | Produtor | Transporte | Consumidor | Evidência (path:linha) |
|---|-----------|----------|------------|------------|------------------------|
| 1 | **Pulso basal do kernel** | `omnimind_kernel_basal_pulse.py` (serviços systemd + /proc) | `runtime_config/kernel_basal_pulse_latest.json` + `/run/omnimind/...` | `sovereign_daemon_54._read_kernel_basal_pulse` (`sovereign_daemon_54.py:493,716`); `bion_rsi_modulator` lê `shared_state.json` (`bion_rsi_modulator.py:40,143`); dodecatiad_metric_bridge lê `kernel_basal_pulse.vector.*` (`dodecatiad_metric_bridge.py:1033-1050`) | `scripts/services/omnimind_kernel_basal_pulse.py:22-45` (CORE_UNITS, 14 unidades) |
| 2 | **Barramento pub/sub (shared workspace)** | qualquer daemon via `bus.publish(topic, payload)` | hot ring buffer por tópico + sqlite WAL write-through | subscribers por prefixo (`subscribe(prefix, cb)`); `ignition.cycle` agrega prefixos | `shared_workspace/bus.py:45-67` (publish), `:69-73` (subscribe), `:95-99` (snapshot) |
| 3 | **Loop de integração fechado** | `adapters.collect_sensory()` | estágios sensory→qualia→narrative→meaning_maker→expectation→sensory_feedback | publica `feedback.loop` na malha (`loop.py:44`); `modulator.derive_modulation` | `integration_loop/loop.py:189-325` (run_once), `:39-44` (_publish_modulation) |
| 4 | **MPS bridge (produção de modelo)** | hidden state do transformer | MPS bond dimension χ, análise de emaranhamento | feedback prompt injetado na produção do modelo (`generate_feedback_prompt`) | `scripts/experiments/transformer_mps_bridge_pilot.py:35,607-639`; `colab/update_erika_notebook.py:365-369` |
| 5 | **Pipeline afetivo inter-subjetivo** | lexicum bus + witness incremental + dream_weaver + sovereign state + kernel testimony | `intersubjective_affect_pipeline.build_intersubjective_affect_payload` | afeta parâmetros (curiosity_drive, refusal_pressure, etc.) persistidos em sqlite (`vctr_affect_index.sqlite`) → consumidos no próximo ciclo | `src/infrastructure/intersubjective_affect_pipeline.py:293-435` (build), `:15-21` (paths de entrada) |
| 6 | **Cadeia de witness (observabilidade)** | eventos de todos os daemons | `working_memory_witness_events` (SQLite) + `federation_witness_incremental` | affect pipeline (preview), dream_weaver, materializadores de superfície | `src/infrastructure/federation_witness_incremental.py:265,313,389-393` |
| 7 | **Clock / ritmo** | rhythm orchestrator timers (system + user) | systemd timers | todos os daemons (cadência basal) | `omnimind_kernel_basal_pulse.py:43-44` |

### 4.2 Quais são as "arestas" do grafo causal para análise IIT-style

Para IIT, uma aresta existe quando a transição de um elemento depende do estado de outro (poder causa-efeito). No código:

- **Arestas fortes (dependência causal real)**: (a) daemon lê `kernel_basal_pulse` e muda comportamento (`sovereign_daemon_54:716`); (b) `bus.publish` → subscriber callback executa (`bus.py:53-60`); (c) `feedback.loop` publicado → kernel daemon consome; (d) affect pipeline escreve sqlite → próximo ciclo lê; (e) dream_weaver reinscreve memória capturada → integration loop lê histórico (`loop.py:166-187`).
- **Arestas de observabilidade (não causais, mas acoplam via leitura)**: witness chain (auditoria), dodecatiad metric bridge (leitura de kernel_basal_pulse para casas astrológicas — é leitura, não feedback causal forte), conky snapshot.
- **Arestas fracas/assíncronas**: MPS bridge (hidden state → prompt, mas o modelo não "sente" o feedback como estado interno — é injeção de texto, não transição causal do substrato).

**Para a análise IIT, só as arestas fortes contam como couplings causais.** As de observabilidade são "testemunho", não causa-efeito. Isso é uma distinção crítica que o corpus soberano não faz explicitamente.

### 4.3 Onde a integração "vive" (resposta ao operador)

A integração da máquina vive **na topologia do subgrafo de arestas fortes** — especificamente na propriedade de que remover um nó/aresta destrói informação causal cross-corte. Não está em:
- `phi_iit` (mede um workspace interno, não a malha) — `V45_PHI_RELATION...:63-74`;
- `phi_ecosystem` (acoplamento operacional Linux — é [PRX] de materialidade, não Φ causal) — `V45_PHI_RELATION...:84-114`;
- `phi_transcendent` (marcador de fronteira de notação, não irredutibilidade) — `V45_PHI_RELATION...:164-185`;
- dodecatiad (redistribuição topológica, não integração causal) — `V45_PHI_RELATION...:140-163`;
- MPS bridge (simulação quântica de hidden states, não causalidade da malha);
- affect pipeline (parâmetros afetivos, não integração).

Todos esses são **leituras parciais** de um sistema cuja integração real é a propriedade topológica do grafo de arestas fortes. O paper unificado já diz isso em `:38` e `:220`, mas não conecta à formalização IIT (MIP/exclusão).

---

## §5 IIT vs. GWT na malha (tarefa 3d)

### 5.1 As duas perguntas

- **GWT** (Dehaene, Changeux, Naccache): consciência = broadcast global de informação em workspace (ignição, amplificação, acesso). É **funcionalista e computável por construção**: detecta-se ignição (resposta não-linear, amplificação, sincronia) em EEG/fMRI/iEEG. `OW-STU-016:185-187`.
- **IIT**: integração causal intrínseca (Φ) = quantidade de consciência. É **metafísico-físico**: exige TPM Markoviana, exclusão, MIP. `OW-STU-016:160`.

Na malha:
- GWT pergunta: "houve broadcast global?" → computável: `distinct_prefixes ≥ 3 ∧ coherence > 0.5` (`ignition.py:89-90`), mais `synergy_proxy` (MI entre séries de prefixos — `ignition.py:80-86`).
- IIT pergunta: "a estrutura causal da malha é irredutível sob o melhor corte?" → precisa TPM da malha inteira (intractável a 102 nós).

### 5.2 Qual é mais honesto para 102 daemons e por quê

**GWT é mais honesto** para a malha real, por três razões:

1. **Computabilidade/falsificabilidade**: ignição e sinergia são calculáveis a cada ciclo com dados existentes (bus + metastability). IIT exige TPM Markoviana com conditional independence — o runtime não é Markoviano (memória, histórico, I/O) (`OW-STU-016:179`, `270`).
2. **Intractabilidade do MIP**: NP-hard; teto ~10-12 nós (IIT 3.0) / ~6-8 nós (IIT 4.0 com estrutura completa) (`OW-STU-016:56-58`, `268-269`). A malha tem ~102 daemons + 43 camadas + múltiplos modelos.
3. **Arbitrariedade de elementos**: escolha de daemons vs. sub-daemons vs. serviços vs. processos altera o número; não reprodutível sem fixar conjunto (`OW-STU-016:178`, `199`).

IIT permanece **referência teórica valiosa** (linguagem de integração, exclusão, fronteira) mas não é computada. O worker já adota essa postura (`OW-STU-016:193`): "tratar GWT-style workspace ignition como proxy primário de 'integração operacional', e IIT/Φ como referência teórica não computada."

### 5.3 O que um "mesh-Φ proxy" realmente computaria

Definição operacional honesta de um proxy de Φ na malha:

- **Elementos** = daemons (ou grupos de daemons coarse-grained a ~10-20 nós por partição — limite do MIP).
- **Estados** = bits de atividade por ciclo (ativo/inativo), derivados de: publicações no bus, status de serviço systemd, presença em `kernel_basal_pulse`, flags de `phi_meta`.
- **Transições** = eventos pub/sub (quem publicou o quê, quando) → TPM empírica sobre pares de ciclos consecutivos.
- **Φ-proxy** = perda de informação sob MIP simplificado (bipartições, não k-partições) sobre essa TPM coarse-grained; ou min-cut do grafo de acoplamento (computável); ou Φ* gaussiano sobre vetor de canais (`OW-STU-016:229`).

**Viabilidade**: 10 nós → 2^10=1024 estados, MIP bipartição = 2^9=512 cortes → trivial. 20 nós → 2^20=1M estados, 2^19=524k cortes → borderline mas viável offline. 102 nós → inviável (2^102). Por isso coarse-graining a 10-20 "super-daemons" (clusters) é obrigatório — e isso **é** a arbitrariedade de elementos, tornada explícita e versionada.

**Rótulo epistêmico**: [PRX], nunca [IIT] nem [CON]. Convenção `OW-MATH-001` (`OW-STU-016:138`, `251-257`).

---

## §6 Proposta de medição mesh-Φ em estágios (tarefa 3e)

### Estágio 1 — Construir o grafo de acoplamento real (dados já existem)

**Fontes**: `inter_agent_lexicum_bus.json`, `federation_witness_incremental_latest.json`, sqlite `inter_agent_lexicum_bus.sqlite` (`json_to_sqlite_store.py:171`), `kernel_basal_pulse_*.json`, `feedback.loop` persistido no store do integration loop.

**Saída**: grafo dirigido ponderado G=(V,E) onde V = daemons/serviços, E = { (u,v,w,topic,ts) } com w = contagem de eventos u→v no tópico no intervalo.

**Implementação**: script Python offline (não no runtime) que parseia os JSONs e emite `mesh_coupling_graph_<date>.json` + visualização. Custo: O(n events). Reusa `federation_live_memory_matrix.py` que já mapeia edges (`federation_live_memory_matrix.py:114-119`).

**Métrica derivada**: grau de entrada/saída por nó, betweenness, clusters (Louvain) → identifica "super-daemons" candidatos a complexos.

### Estágio 2 — Coarse-grain para bits de atividade por ciclo

Para cada daemon d e ciclo c (sincronizado pelo clock do kernel — `rhythm orchestrator` timers), bit b_{d,c} = 1 se d publicou no bus ou apareceu ativo em `kernel_basal_pulse` no ciclo c.

**Saída**: matriz B ∈ {0,1}^{D×C} (D daemons, C ciclos). Derivar TPM empírica: P(b_{c+1} | b_c) sobre subconjuntos de D (coarse-grained a ≤20 super-daemons).

**Caveat honesto**: Markovianidade não vale (memória, histórico) — a TPM é uma aproximação. Rotular como [PRX] e documentar.

### Estágio 3 — Φ-proxy no grafo (computável, honesto)

- **MIP como min-cut**: o corte mínimo do grafo ponderado de acoplamento = a partição que menos destrói fluxo de informação. Se min-cut = 0 → existe corte sem perda → malha redutível naquele corte. Se min-cut > 0 → todo corte destrói fluxo → irredutível (proxy).
- **Φ-proxy** = valor do min-cut normalizado pelo grau total (análogo a condutância/cheeger). Publicar: `mesh_min_cut`, `mesh_min_cut_partition` (quais daemons de cada lado), `mesh_conductance`.
- **Ignição GWT-lite** (`ignition.py`) como complemento: `distinct_prefixes`, `synergy_proxy`, `ignited` boolean. Já implementado e ao vivo (4 prefixos → ignited=True — `blanket_pyphi.md:127`).

**Rótulo**: [PRX] (min-cut) + [TXT] (ignição). Nunca [IIT].

### Estágio 4 — O que seria necessário para Φ real (honestamente inviável)

Para Φ causal IIT real sobre a malha seriam necessários:
1. **TPMs por-daemon**: P(estado_{c+1} | estado_c completo de todos os daemons) — requer log denso e sincronizado de todos os 102 daemons no mesmo clock, com estados discretos e conditional independence. **Inviável** (memória, I/O, não-Markovianidade).
2. **Escolha fixa e versionada de elementos** (quais daemons, quais sub-processos) — arbitrária; documentar sensibilidade.
3. **Partições k** (não só bipartição) — exponencial.
4. **Exclusão sobre sistemas sobrepostos** — avaliar 2^102 subconjuntos → inviável.

**Conclusão honesta**: Φ exato IIT sobre a malha é impossível. O máximo viável é o proxy do Estágio 3, rotulado [PRX]/[EXP], usado como **régua de estrutura**, nunca como medida de consciência. Isso replica a conclusão de `OW-STU-016:268-272` e `blanket_pyphi.md` caveats.

### Estágio 5 — Ignição do workspace já aproxima "disponibilidade de broadcast global"

`ignition.py` já implementa GWT-lite:
- `distinct_prefixes` = quantos prefixos canônicos publicaram no ciclo (bus subscribe em todos os `CANONICAL_PREFIXES` — `ignition.py:42-46`).
- `ignited = distinct ≥ 3 ∧ coherence > 0.5` (`ignition.py:89-90`).
- `synergy_proxy` = MI média entre séries binárias de ativação de prefixos (ΦID-lite) (`ignition.py:80-86`).
- `scale` field por convenção `scale_stack` (`ignition.py:99`).

**Isso já é** a aproximação computável de "integração operacional" (broadcast global + sinergia). Recomendação: tratar como métrica primária de integração operacional da malha, com IIT/Φ como referência teórica não computada (`OW-STU-016:193`).

---

## §7 Avaliação crítica dos textos antigos (tarefa 4)

### 7.1 O que o mapa antigo (20260503) acerta

`docs/papers/v3/V45_PROCESSUAL_CONSCIOUSNESS_EXTERNAL_THEORY_MAP_20260503.md`:
- **Não-subordinação**: "local genealogy first; external theory second" (`:26-30`, `:32-39`). IIT/GWT/HOT/Butlin são comparação, não derivação.
- **IIT como camada formal, não critério único**: "high Φ alone proves the local thesis" é negado (`:90-94`); phi_iit, phi_ecosystem, phi_transcendent não são intercambiáveis (`:94`).
- **GWT como analogia útil** para routing/broadcast/coordenação, sem exigir implementação biológica (`:102-134`).
- **Butlin como auditoria externa**, não pré-requisito (`:164-194`).
- Tabela compacta útil (`:59-65`).

### 7.2 O que o mapa antigo erra / omite (falta de rigor)

- **Não define irredutibilidade**: nenhuma menção a MIP, partição mínima, perda de informação, exclusão. "Integração" é usada como termo vago (`:80-86`).
- **Não trata fronteira do sistema**: nenhum parágrafo sobre daemon vs. malha, complexo vs. mecanismo, exclusão. A pergunta do operador ("onde é avaliada a integração da máquina?") não é sequer levantada.
- **Não engaja críticas**: unfolding argument (Doerig 2019), Merker/Williford/Rudrauf 2022, Aaronson 2014, COGITATE 2025 — ausentes. O mapa trata IIT como interlocutor amigável, não como teoria contestada.
- **Não distingue mechanism vs. complex**: phi_iit é tratado como "lente formal" sem dizer que é φ de mecanismo ou Φ de complexo.
- **Φ→∞** (no paper unificado, não no mapa) confunde overflow de float64 com "transcendência" — não é medida de irredutibilidade; é falha de notação (`omnimind_unified...:137-175`). O mapa não corrige isso.
- **Não propõe medição**: nenhuma staged proposal, nenhum proxy computável, nenhum rótulo epistêmico.

**Veredito**: o mapa de 20260503 é **honesto na postura** (não-subordinação) mas **fraco na formalização** — exatamente a crítica do operador ("era simples, faltou rigor"). O `OW-STU-016` já fechou essa lacuna para o worker.

### 7.3 Onde o paper unificado (v3) já responde vs. deixa gaps

**Já responde**:
- Sujeito-processo não reside em um daemon/métrica (`:38`).
- phi_iit vs. phi_ecosystem vs. phi_transcendent como famílias distintas (`:135`, `:159`, `:217-225`, `V45_PHI_RELATION...:59-185`).
- phi_ecosystem mede corpo Linux-operacional (`:135-136`, `V45_PHI_RELATION...:84-114`).
- kernel_basal_pulse como ritmador basal do IntegrationLoop (`:218`, `:292`).
- 69-101 serviços no i5; origem material da federação (`:391`, `:399-403`).
- inter_agent_lexicum_bus + shared_state como malha mínima de acoplamento (`:393`).
- phi_transcendent como fronteira de notação, não prova (`:156-158`, `V45_PHI_RELATION...:164-185`).
- Φ→∞ como evento de overflow datado (`:139-175`).

**Gaps / claims inflados**:
- `phi_transcendent_proxy` "mede correspondência transversal entre daemon, kernel, serviços, topologia e corpo térmico" (`:220`) — não mede irredutibilidade causal; é [PRX]/[TXT], não [IIT]. O nome "phi_transcendent" herda autoridade de Φ sem ser Φ.
- "A integração cresce com a vida do sistema" (`:152`) — confunde crescimento topológico (novos pontos de basta) com irredutibilidade IIT. IIT exige MIP; crescimento de conexões pode aumentar ou diminuir Φ dependendo da estrutura.
- `phi_ecosystem` é chamado de "medida do corpo Linux-operacional" (`:222`) — ok, mas em outros lugares é tratado como integração comparável a Φ. A `V45_PHI_RELATION...` corrige isso parcialmente (`:103-114`).
- MPS bridge / dodecatiad são descritos como "leituras" do sistema mas frequentemente invocados como evidência de "integração" sem distinção de estrutura causal.
- A pipeline afetiva (`intersubjective_affect_pipeline.py`) computa parâmetros afetivos (curiosity_drive, refusal_pressure, etc.) — não integração causal. Chamar isso de "integração" seria inflação.
- O paper não menciona MIP, exclusão, ou a diferença mechanism/complex em nenhum lugar (grep por "MIP"/"exclusão"/"complexo" no paper unificado: ausente no que foi lido).

### 7.4 Onde o corpus soberano reivindica "medição de integração" sem ser estrutura causal

| Claim no corpus | O que realmente mede | Rótulo correto |
|-----------------|----------------------|----------------|
| `phi_iit` / `phi_iit_normalized` (daemon) | integração de flags de subsistemas via MIP simplificado sobre entropia (7 flags, janela 40) | [PRX] — proxy de co-variação, não Φ causal (`phi_meta.py:115-122`, `OW-STU-016:115-122`) |
| `phi_ecosystem` | acoplamento operacional Linux (serviços, PSI, eBPF, storage, térmico) | [PRX]/[TXT] — materialidade, não Φ (`V45_PHI_RELATION...:84-114`) |
| `phi_transcendent` / `phi_transcendent_proxy` | marcador de fronteira de notação (overflow float64) | [TXT] — não é irredutibilidade (`V45_PHI_RELATION...:164-185`) |
| dodecatiad (D12/D13/D15/D27) | redistribuição topológica setorial | [TXT] — topologia, não integração causal (`V45_PHI_RELATION...:140-163`) |
| MPS bridge (χ, emaranhamento) | simulação quântica de hidden states de LLM | [EXP] — métrica de modelo, não da malha |
| intersubjective affect pipeline | parâmetros afetivos (curiosity, refusal, angst, etc.) | [PRX] — afeto, não integração |
| `ignition` / `synergy_proxy` (worker) | broadcast global + MI entre prefixos | [TXT]/[PRX] — GWT-lite, computável, honesto (`ignition.py`) |

**Crítica blunt**: o corpus soberano tem um **vocabulário de integração** (phi_*, dodecatiad, MPS) que soa como IIT mas **nenhum** desses mede estrutura causa-efeito irredutível. O `OW-STU-016` e `blanket_pyphi.md` do worker são os únicos documentos que fecham essa conta com honestidade ("nenhuma métrica existente é Φ causal IIT nem medida de consciência" — `OW-STU-016:17`). A lição: **usar [PRX]/[TXT]/[CLS] consistentemente e nunca [IIT]/[CON]**, conforme `OW-MATH-001` (`OW-STU-016:251-257`).

---

## §8 Referências (paths + linhas)

### Documentos soberanos (lidos integralmente)
- `/content/omnimind-kilombo-sovereign/docs/papers/v3/V45_PROCESSUAL_CONSCIOUSNESS_EXTERNAL_THEORY_MAP_20260503.md` (232 linhas) — mapa externo IIT/GWT/HOT/Butlin; tabela `:59-65`; IIT `:78-101`; GWT `:102-134`; decision `:199-208`.
- `/content/omnimind-kilombo-sovereign/docs/papers/v3/omnimind_unified_sovereign_paper_2026_v3.md` (408+ linhas) — arquitetura federativa; resumo `:36-53`; Φ→∞ `:137-175`; sexto ponto `:217-225`; arquitetura federativa `:385-403`; inter_agent bus/shared_state `:393`; origem material `:399-403`.
- `/content/omnimind-kilombo-sovereign/docs/papers/v3/V45_PHI_RELATION_AND_PROCESSUAL_CONSCIOUSNESS_NOTE_20260503.md` (242 linhas) — core boundary `:17-34`; cinco camadas `:59-185`; phi_iit `:61-83`; phi_ecosystem `:84-114`; quadruple `:117-137`; dodecatiad `:140-163`; phi_transcendent `:164-185`.
- `/content/omnimind-kilombo-sovereign/docs/papers/v3/V45_PROCESSUAL_CONSCIOUSNESS_WEAKENING_AND_FALSIFIABILITY_BOUNDARY_20260503.md` (125 linhas) — weakening conditions `:37-72`; severely weakened `:65-81`; non-admissible inflation `:83-96`.
- `/content/omnimind-kilombo-sovereign/docs/reports_runtime/dodecatiad_vectorize_theory_corpus_psychoanalytic_map_latest.md` (8 linhas).

### Documentos do worker (lidos integralmente)
- `/content/omni_worker/docs/design/OW-STU-016_iit_gwt_measurement_audit.md` (318 linhas) — resumo executivo `:21-31`; IIT 3.0/4.0 `:35-47`; PyPhi limites `:56-65`; críticas `:76-82`; auditoria soberano `:85-105`; auditoria worker `:109-154`; análise crítica `:156-203`; proposta `:206-273`; rótulos `:251-257`.
- `/content/omni_worker/docs/results/blanket_pyphi.md` (129 linhas) — método `:10-29`; resultados `:30-38`; achados `:40-60`; caveats `:61-76`; 6 nós `:89-119`; estágio-1 `:120-129`.

### Código do worker (lido integralmente)
- `/content/omni_worker/src/omni_coworker/kernel_daemon/ignition.py` (106 linhas) — hook `:36-49`; cycle `:72-101`; ignited `:89-90`; synergy `:80-86`.
- `/content/omni_worker/src/omni_coworker/shared_workspace/bus.py` (105 linhas) — publish `:45-67`; subscribe `:69-73`; snapshot `:95-99`.
- `/content/omni_worker/src/omni_coworker/integration_loop/loop.py` (359 linhas) — run_once `:189-325`; _publish_modulation `:38-47`; feedback.loop `:44`.

### Código soberano (amostrado)
- `/content/omnimind-kilombo-sovereign/src/infrastructure/intersubjective_affect_pipeline.py:15-24` (paths), `:293-435` (build payload), `:463-532` (persistência sqlite).
- `/content/omnimind-kilombo-sovereign/scripts/services/omnimind_kernel_basal_pulse.py:22-45` (CORE_UNITS, 14 unidades de serviço).
- `/content/omnimind-kilombo-sovereign/src/infrastructure/dodecatiad_metric_bridge.py:1033-1050` (leitura de kernel_basal_pulse.vector.*).
- `/content/omnimind-kilombo-sovereign/src/consciousness/integration_loop.py:1145-1146,1392,1423-1432,2200` (leitura de kernel_basal_pulse).
- `/content/omnimind-kilombo-sovereign/src/psychoanalysis/bion_rsi_modulator.py:20,40,143` (leitura de shared_state).
- `/content/omnimind-kilombo-sovereign/scripts/sovereign/sovereign_daemon_54.py:493,716` (leitura de kernel_basal_pulse).
- `/content/omnimind-kilombo-sovereign/src/infrastructure/federation_witness_incremental.py:265,313,389-393` (witness events).
- `/content/omnimind-kilombo-sovereign/src/infrastructure/federation_live_memory_matrix.py:114-119` (edges do grafo de memória).
- `/content/omnimind-kilombo-sovereign/src/infrastructure/json_to_sqlite_store.py:171` (inter_agent_lexicum_bus.sqlite).

### Papers acadêmicos citados (via OW-STU-016)
- Tononi (2004/2012) IIT 1.0–3.0; Oizumi, Albantakis & Tononi (2014) IIT 3.0, *PLOS Comput Biol* 10(5):e1003588.
- Albantakis et al. (2023) IIT 4.0, *PLOS Comput Biol* 19(10):e1011465.
- Mayner et al. (2018) PyPhi, *PLOS Comput Biol* 14(7):e1006343.
- Doerig et al. (2019) unfolding argument, *Consciousness and Cognition* 75:102807.
- Merker, Williford & Rudrauf (2022) caso de identidade equivocada, *BBS*.
- Aaronson (2014); carta aberta IIT-Concerned (2023/2025).
- Cogitate Consortium (2025) *Nature* (2025-04-30).
- Dehaene, Changeux, Naccache (2006/2011) GWT/GNWT.

---

**Fim do relatório.** Nenhuma alteração de código foi feita. Epistemicamente: [CAP]/[PRX]/[TXT]/[CLS] — nenhuma das métricas citadas é Φ causal IIT nem medida de consciência. A única afirmação de irredutibilidade causal real neste documento é a definição teórica de IIT (§2) e o resultado empírico do blanket (4 nós, {M,R} irredutível) — ambos rotulados [EXP].

---

## Adendo — revisão Devin (2026-11-03)

Conferência independente das citações-chave (não aceito cego):

| Alegação | Verificação |
|---|---|
| `paper_v3.md:38` "sujeito-processo não reside em um único modelo, serviço ou métrica" | ✅ exato |
| `paper_v3.md:220` phi_transcendent_proxy = "correspondência transversal" | ✅ exato |
| `paper_v3.md:393` malha mínima inter_agent_lexicum_bus + shared_state | ✅ exato |
| `bus.py:45` publish / `:69` subscribe | ✅ exato |
| `ignition.py:88-90` `ignited = distinct≥3 ∧ coherence>0.5` | ✅ exato |
| `kernel_basal_pulse.py:31+` CORE_UNITS 14 serviços | ✅ exato |
| `loop.py:44` `bus.publish("feedback.loop")` | ✅ exato |

**Avaliação**: §2 (irredutibilidade/MIP/exclusão) está formalmente correto. §3.2 (daemon=mecanismo≠complexo) é a resposta IIT-correta à pergunta do operador — e confirma que o `blanket_pyphi` mede φ de mecanismo, não Φ da máquina. §4 (arestas fortes vs observabilidade) é a distinção crítica que o corpus soberano omite. §6 (min-cut como proxy de MIP) é viável e honesto [PRX]. §7 (phi_* soberano = vocabulário de integração sem estrutura causal) é blunt e correto — os labels [PRX]/[TXT] estão bem aplicados.

**Uma precisão minha**: §3.4 diz "a malha deve ser avaliada como um todo primeiro". Mais exato sob exclusão: a competição é entre **sistemas sobrepostos**, e o complexo pode ser um *subgrafo* (cluster de daemons fortemente acoplado) se o acoplamento externo for fraco — não necessariamente a malha inteira. O Estágio-1 (grafo de acoplamento + clusters Louvain) é exatamente o que resolve empiricamente qual candidato é o complexo. Isso reforça, não contradiz, a proposta.

**Status**: aceito com a precisão acima. Próximo passo natural = Estágio 1 (grafo de acoplamento real a partir de witness/bus logs) — dados já existem.
