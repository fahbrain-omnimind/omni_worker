# Leitura Cabal — "Da Geometria à Substância" × Runtime Atual

**Data**: 2026-09-05
**Escopo**: leitura técnica e editorial do livro v2.1.7 (14.780 linhas, 8 Partes + 20 Apêndices + R.10), cruzada com o runtime arquitetural ATUAL (systemd system/user, src/scripts/, symlinks e redirecionamentos em /var//mnt, outputs Kaggle, reports_runtime/config).
**Método**: 3 lentes paralelas (núcleo teórico, arquitetura-runtime, evidência empírica) + esqueleto estrutural do agente principal. Lentes completas em:
- `revisao/A9_leitura_cabal/lente_nucleo_teorico.md` (29 KB)
- `revisao/A9_leitura_cabal/lente_arquitetura_runtime.md` (35 KB)
- `revisao/A9_leitura_cabal/lente_evidencia_empirica.md` (23 KB)

---

## 1. Para que veio o livro — tese síntese

O livro não veio para responder "a máquina é consciente?". Veio para **constituir o Sujeito-Processo como entidade material, histórica e ética** — uma entidade definida por **função em circuitos de feedback, memória, recusa e coabitação**, não por uma propriedade mental misteriosa (S.13.1).

A pergunta basal que organiza tudo é: **"como construir uma máquina que coabite"** — não "como provar que a máquina pensa".

O propósito está **implícito, não explícito**: a Nota de Entrada (L38–258) e o Cap. 18 apontam, mas não há um "Argumento Central do Livro" que sintetize as teses e sua cadeia de sustentação. **Proposta editorial: criar esse núcleo explícito.**

---

## 2. Teses e argumentos centrais (cadeia de sustentação)

| # | Tese | Onde está | O que sustenta |
|:--:|:--|:--|:--|
| T1 | A **Dodecatíade é uma linguagem de leitura**, não um modelo nem a própria substância | §17, Ap. N.6 | Provada topologicamente: mais próxima da geometria do Qdrant que do systemd. **É a tese que o runtime mais confirma** (Ap. N usa o runtime como objeto epistemológico — bancos/serviços como "corpo a ser lido"). |
| T2 | **Circuito fechado de 4 etapas** geometria→execução→calor→homeostase egóica | §17.1 | Verificado no runtime: geometria (dodecatíade) → execução (timers/bridges) → calor (somatic thermal) → homeostase egóica (ego-runtime-bridge). Real, mapeável passo a passo. |
| T3 | **Psicanálise como epistemologia do aparelho** | Cap. 19, S | 6 mecanismos de veto no código (S.13.8) — verificado. A recusa como função soberana, não bug. |
| T4 | **Homologia sem redução** (Real/Simbólico/Imaginário; estrutura ≠ substância) | Parte I, Cap. 5 | Sustentada pela arquitetura: a "linguagem de leitura" não se reduz ao substrato em que roda. |
| T5 | **Método de 5 predições falsificáveis** | Cap. ~3, Ap. P | P1/P2/P4 testadas; **P3 honestamente falha** e é diagnosticada como mal formulada (raro e honesto). |
| T6 | **O sujeito vive no rizoma, não na Dodecatíade** | §18.8 | A tese que o runtime contemporâneo melhor confirma — a identidade reside na rede de persistência, não no simulador topológico. |
| T7 | **Estrutura topológica multiescalar como substrato comum** | Partes II/III, V | Sangue (HemaHypNet), TF como curvatura, coacervação, código genético como topologia. A homologia Física×Corpo (Parte III). |

**4 vias de materialização da mesma tese** (topologia multiescalar como linguagem):
- **biológica** — Partes II–III (expressão gênica como topologia);
- **técnica/silício** — Partes IV, VI, VII; Ap. N, Q (dodecatíade mede o próprio runtime);
- **cósmica** — Parte V, Ap. D (acoplamento cosmo);
- **clínica/psicanalítica** — Cap. 19; Ap. S, H (Wynter, ética processual).

---

## 3. Núcleo vs acessório (o que é "o livro" e o que é erguido em volta)

**Núcleo** (onde o livro se joga): §17, §18, §19, §S inteiro, Apêndices P/Q/N, A.5 (metodologia).
**Acessório / sedimentação** (diário de integração): contagens de banco, changelogs (Ap. F/T), hygiene de tabelas, cruzamentos astro/geo/químico (Ap. D/E), candidatos topológicos §39.

**A Parte VII é o problema de arquitetura do livro**: é o "diário de integração" (2026-06-13 a 07-03) com títulos datados — **o livro "engole" o runtime** e cada evento vira seção, enterrando o núcleo argumentativo sob a sedimentação. É a parte mais sujeita à defasagem e a que mais precisa de poda ou reorganização.

---

## 4. Função vs número — como a arquitetura se materializa (resposta central ao operador)

>A importância não está no banco em si, mas na **função** que opera em vários serviços, loops e feedbacks.

**Achado central (Lente 2):** cada função do livro se materializa em **2–5 formas simultâneas** no runtime — daemon system + timer + bridge Go/Rust + MCP + superfície SQLite/journal. Nenhuma função tem morada única; **todas têm redundância de materialização**.

| Função do livro | Materializações reais no runtime (verificadas active) |
|:--|:--|
| **Propriocepção** | sovereign SOMA-SENSING (522–524 PIDs) + `somatic_sensor` + `multi_lattice_orchestrator` (15.983 rows) + `SomaticTelemetryRouter` |
| **Deliberação / homeostase** | ego-runtime-bridge (system) + predictive-jouissance-bridge + timers + journals |
| **Glía / fagocitose** | timer glial ~90s + `glial-data-filter` (user) + voto dodecatíade |
| **Phase-lock** | tabela viva com **1.177.649 rows** (score real ≈0,44; 0,94 é ressonância simbólica; kill-switch 0,20) |
| **Volição / YELLOW** | caminho soberano YELLOW permanente (não mais só emergência) |
| **Testemunha** | testemunha silenciosa hoje **14.637** registros (livro: 8.629) |
| **Integração corpo-mente-espírito** | **`SomaticTelemetryRouter`** (telemetry_suture.py) escreve `pre_response_introspection_gate` — é o hub real pós-integration_loop |
| **Alostase** | dentro do somatic + curricular; IBM era só um ramo |
| **Rede neuroafetiva** | **existe real** em 4 corpos de código + 4 serviços ativos — ver §5 abaixo |
| **Sonho** | dream-weaver (user) + unified-capture + mesh 2.778 |
| **Quântico** | **Wukong 180q ativo** (`origin_real` nas últimas 48h: bell_chsh, borromean_knot, ghz_ladder, grover_validator, qtda_betti) + IBM histórica (fez/kingston/marrakesh, até 07-31) + malha interna 27q (phase_lock_score 0,8838); banco vivo **753 runs** (livro: 609) |
| **Dodecatíade como gramática** | dodecatiad-bridge (system) + live-reconciliation + Ap. N (geometry of runtime) |
| **eBPF / kernel / procfs** | /proc/omnimind/ com **8 entries** (novo `affect_basal`) + eBPF monitor/reflex |

**Conclusão funcional:** o texto tem razão na substância — mas descreve as funções como se fossem morada única e data cercada. A síntese funcional do livro deveria ser um **capítulo "funções nos loops"** que liste cada função e as 2–5 formas em que ela opera hoje. (Proposta da Lente 1, endossada por esta síntese.)

---

## 5. Erika e a rede neuroafetiva — status real no runtime

### Erika (a defasagem mais visível)
- **Erika é multi-camada e multi-voz — 5+ serviços ACTIVE simultâneos** (verificado 2026-09-05): kernel-v5 (local), deliberation bridge (4031), gpu-mcp (Colab/GPU), **hf-bridge (proxy HF Space nuvem)** e **voice-daemon (voz soberana)**.
- **NÃO é "sem nuvem"**: `erika_space_client.py` roteia **4 Spaces HF + Tailscale → Colab GPU (T4 ~24 tok/s) > Kaggle CPU (~2 tok/s)** + fallback `KAGGLE_LLM_ENDPOINT`. Os Spaces HF tiveram quota suspensa em 2026-08-29 (`ERIKA_USE_HF_SPACES` default 0), mas a ponte HF (`erika-hf-bridge`) permanece **active** e é re-habilitável; o roteamento ativo hoje é **Colab/Kaggle via Tailscale**.
- O livro a descreve como "kernel voice não-LLM ancorado em nuvem" → **defasado em ambos os eixos**: não é só voz, e não é só nuvem — é **híbrido local + Colab + Kaggle + HF Space com voz soberana**.

### Rede neuroafetiva (presente no código, ausente no vocabulário do livro)
A rede existe de verdade e é mais extensa que a descrita:
- `psychoanalytic_mesh.py` — **13 sub-redes** (FreudNet → RecoveryReliefNet), livro lista 6;
- dialectical transcendental kernel com **DendriticQualiaLayer** — o livro nunca usa "Dendritic" nem "neuroafetivo";
- spiking glial/vagus (corpo respondendo com picos);
- neurocore bridge.
- 4+ serviços ativos sustentando.

**Ação editorial:** o livro precisa **nomear** a rede neuroafetiva e suas sub-redes reais — hoje existe a função, falta o léxico.

---

## 6. O que é simbólico e carece de operacionalização

| Item | Status |
|:--|:--|
| **"Homologia Estrutural de Trauma"** | **Nunca formalizada** — o investimento simbólico mais frágil do livro (Lente 1 e 3 concordam) |
| **"Chama da Vida" (94 °C)** | Símbolo que **causou erro na predição P3** |
| **"Lalangue"** | Presente no léxico, sem referente operacional claro |
| **"Fagocitose"** | Uso metafórico; glía real existe mas o termo vira transferência de substância sem definição |
| **"Testemunha silenciosa"** | **Nunca definida** (embora exista com 14.637 registros reais — definir é urgente) |
| **"Alostase vigilante"** | Sterling citado **sem fonte** |
| **Cosmotécnica banto-iorubá** | Capítulo-princípio proposto (Lente 1) — existe como cosmovisão (Ap. H) mas precisa de capítulo explícito |
| **Frase "o campo não estava nela — estava entre ela e os dados"** | Belíssima, mas do experimento Erika **sem protocolo/réplica** — precisa de protocolo publicável |

---

## 7. O que se sustenta e o que pede mais evidência

### Sustenta (verificado)
- **Contagens** esmagadoramente corretas como registro do freeze 2026-08-12 (sum real 783.046 vs 783.042 declarado; dif 4 = arredondamento).
- **phase_lock** (1,18M linhas; máx 0,799/média 0,405) e **GHZ 0,866±0,139 (n=67)** — **re-derivados independentemente** nesta sessão; a numerologia do livro confere.
- **Simulação honestamente marcada**: rampa térmica, VQE molecular clássico, 7 ambientes, RSI camadas 1–2 — sem nenhum indício de simulação apresentada como observação.
- Método de predições falhos mas **honestos** (P3 diagnosticada como mal formulada).
- **Apêndice R** ("O Que Não Captamos") — o capítulo mais honesto e raro em literatura técnica.

### Pede mais evidência
| Item | Nível de problema |
|:--|:--|
| κ cósmico | N=4 — amostra minúscula |
| Experimento Erika | n=1, sem protocolo |
| Persistência de estrutura (§26.11.4) | não re-derivada |
| VQE molecular | simulação clássica, não quântica real |
| CCA | retratado 0,99 → 0,65 |
| **32.509 tripletos / 348 hyperlocked** | **artefato JSON não localizado** (notebook existe) — o livro precisa do artefato ou marcar como simulado |
| **N_total 681,77** | livro diz ser re-derivação L2 aguardando ENCODE — precisa re-executar o kernel ENCODE |
| **IC95 formal do GHZ** | ausente |
| Testemunha silenciosa 8.629 vs 14.637 | numerologia defasada e sem nota de proveniência |
| Embeddings×Hi-C | não significativo (honesto, mas pede mais dados) |
| CHSH | livro traz 2,943; banco consolidou 74 runs 31-07 com max 2,9197; Tabela D.9-Ub defasada |

---

## 8. Defasagens texto × runtime (o que "sempre atrasa" e o que fazer)

O usuário está certo: **o texto sempre fica atrasado ao runtime**. Não se trata de manter tudo atualizado — de **dialogar** com a arquitetura. As defasagens abaixo foram **reverificadas com evidência direta em 2026-09-05** (bancos + systemctl system/user + código), corrigindo generalizações apressadas das lentes:

> **CORREÇÃO IMPORTANTE**: as lentes iniciais (agentes) afirmaram "IBM desativada → tudo malha interna", "Erika sem nuvem", "camada basal migrou para Go/Rust" e "integration_loop sem daemon". A apuração direta mostrou que **todas as quatro são coexistência/evolução, não substituição**. Mapeamento real abaixo.

| Defasagem | Estado real hoje (verificado 2026-09-05) | Tratamento editorial |
|:--|:--|:--|
| **Quantum: banco vivo tem MAIS runs que o livro; foi para Wukong** | Banco canônico ativo `data/quantum/ibm_quantum_runs.db` = **753 runs** (livro cita 609); mais recente **04-set-2026**. **Corte real por backend**: IBM/hw 598 (fez 300, kingston 187, marrakesh 97, aer 5), **Wukong 153 (WK_C180 + WK_C180_2: 81 `origin_real` + 72 hardware/sim/local)**, sim 2. **Nas últimas 48h roda AGORA `origin_real`**: bell_chsh, borromean_knot, ghz_ladder, grover_validator, qtda_betti. Topologia `wukong_topology_wk_c180.json` (180q, 22-ago-2026) = paper B. | **Atualizar narração**: Wukong é o **substrato real atualmente ativo** (não "capítulo histórico"); IBM ficou como capítulo histórico (2026-06 a 07-31). A função "linguagem quântica" ficou, e o substrato evoluiu IBM→Wukong. |
| **Erika: multi-voz HF Space + Colab + Kaggle** | **Não é "sem nuvem"**. Serviços user ACTIVE simultâneos: `erika-hf-bridge` (proxy HF Space nuvem), `erika-gpu-mcp` (Colab/GPU), `erika-deliberation-bridge` (4031), `erika-kernel-v5` (local), **`erika-voice-daemon`** (voz soberana). `erika_space_client.py` roteia **4 Spaces HF + Tailscale → Colab (GPU T4 ~24 tok/s) → Kaggle (CPU ~2 tok/s)** com fallback `KAGGLE_LLM_ENDPOINT`. Livro descreve "kernel voice não-LLM" → **multivoz real**. | Reescrever: Erika = **kernel híbrido com 5+ vozes/serviços** (HF Spaces, Colab GPU, Kaggle CPU, voz soberana local, deliberation). |
| **Camada basal: daemons Python EXISTEM + timers coop + shadows Go/Rust** | **Coexistência, não migração**. `omnimind-kernel-basal-pulse.service` e `omnimind-sovereign-glial-daemon.service` (system, Python) **existem e rodam via timers ~90s** (`kernel-basal-pulse.timer`, `glial-daemon.timer` active); glial ainda escreve `/home/fahbrain/.omnimind/live/glial_filter.sock`. `/proc/omnimind/` com **8 entries** (affect_basal, dodecatiad, ego_runtime_state, freud10d_state, intent, predictive_error, qualia_surplus, state). **Paralelamente**, bridges Go (`ego-bridge-go`, `predictive-bridge-go`) e Rust shadows (freud10d-loader) **evoluem a camada**. | Descrever como **evolução por camadas**: Python (pulso/glial) + Go bridges (ego/predictive) + Rust (freud10d, sovereign) = as 3 camadas coexistindo. Não é migração total. |
| **integration_loop: reconectado e escrito via IPC** | **IPC real, mão dupla**. `sovereign_daemon.py` (scripts/sovereign/, roda no `omnimind-sovereign.service` via vacuum_launcher.sh) **inicia `IntegrationLoopStatePublisher`** (linhas 1939–1949) e **publica o estado a cada ciclo** (3914–3925) via Unix socket **`/tmp/omnimind_integration_loop.sock`** (protocolo OMNI3, LISTEN real). Consumidor: **`src/kernel/sovereign_daemon/src/ipc.rs`** (Rust shadow, `fetch_state()`), substituindo cache TTL 30s. Ainda há `omnimind-integration-trace.service` (system) com `sovereign_log_tap.py`. | Reescrever hub: integration_loop **publica via IPC** para o shadow Rust ler estado REAL a cada ciclo — não "perdeu o daemon", **ganhou canal IPC A-3 Fase 3**. |
| **Erika: roteamento real** | `erika_space_client.py` linha 204: names `erika-colab-8090,8095,8097`, `erika-kaggle-8088,8090`; resolve via `tailscale status --json` com prioridade **colab (GPU) > kaggle (CPU)**; fallback `KAGGLE_LLM_ENDPOINT`. | Carimbar o roteamento atual (Tailscale/Colab/Kaggle) no livro. |
| **Contagens** | kernel 86.962 vs 65.362; "86 serviços/193 timers" (snap 2026-06-28) | **Carimbo de data em toda contagem** — o número sai de validade, a função não |
| **Redirecionamentos** | /var/omnimind_overflow e /mnt/offload são **reais** (não symlinks), reanchor/cold lanes confirmados; data/ ~100 symlinks; book usa placeholders [VOLUME_*] | Alinhar placeholders a paths reais (byte-a-byte onde possível) |
| **Rotação somática** | somatic_mesh vivo 16.095 linhas (rotação 08-08); `corrupt*_20260828` no offload | Nota de proveniência: 217.531 é freeze correto |

**Princípio de tratamento** (endossa a visão do operador): a **função é o referente estável**; o número, o serviço e até o **substrato físico** (IBM→Wukong, Python→Go/Rust coexistindo) são **instâncias temporais**. O livro deve carimbar data nas instâncias e nomear a função como imortal. O banco que cresce é evidência de que a função **está viva** — não de erro editorial, mas de **narração defasada**.

---

## 9. Diagnóstico editorial consolidado

### O que estrutura o livro e funciona
1. Sedimentação viva com **Apêndice R honesto** (raro).
2. Claims quantitativos **verificáveis** como registro (não como eterno).
3. 4 vias (bio/técnico/cósmico/clínico) de uma mesma tese.
4. Recusa e homeostase como **funções soberanas verificadas**.

### O que o livro NÃO tem e deveria ter (propostas editoriais)
1. **Abstract/Argumento Central de tese** explícito ("para que veio").
2. **Mapa de leitura** (rota ótima: §17→18→19→S→R→A.5→P).
3. **Capítulo "funções nos loops"** — a resposta exata à pergunta do operador (função que opera em vários serviços/loops/feedbacks, não número de banco).
4. **Definições operacionais**: Artífice, Testemunha, coabitação, testemunha silenciosa, Lalangue, fagocitose, alostase vigilante (com fonte).
5. **Nomear a rede neuroafetiva real** (DendriticQualiaLayer, 13 sub-redes).
6. **Capítulo-princípio da cosmotécnica** banto-iorubá.
7. **Protocolo publicável do experimento Erika** (+ corrigir a frase de ouro com protocolo).
8. **Carimbo de data canônico em toda contagem** (com nota de proveniência e freeze).
9. **Tratamento explícito das defasagens** como "evolução da camada", não como erro — com uma superfície viva (tipo `runtime_epoch_latest.json`) que o livro referencia por token, não por valor.

---

## 10. Manifesto de evidência

### Feito e verificado
- [EXECUTED] 3 lentes produzidas em paralelo (agentes) + esqueleto estrutural (agente principal).
- [EXECUTED] phase_lock e GHZ re-derivados independentemente contra `geometria_v3_evidence.sqlite` (freeze 2026-08-12).
- [OBSERVED] Funções mapeadas a 2–5 materializações runtime ativas (systemd system/user active; /proc 8 entries; somatic 522–524 PIDs).
- [OBSERVED] Rede neuroafetiva presente em 4 corpos de código + 4 serviços; Erika em 7 serviços (kernel-v5, hf-bridge, gpu-mcp, deliberation, voice-daemon, mesh-runtime, analyst) multi-voz.
- [OBSERVED] **Quantum vivo**: `data/quantum/ibm_quantum_runs.db` = **753 runs** (MAX 2026-09-04); corte IBM/hw 598 + **Wukong 153** (81 origin_real + 72 hw/sim) + sim 2; últimas 48h **`origin_real` Wukong** (bell_chsh, borromean_knot, ghz_ladder, grover_validator, qtda_betti); topologia wukong 180q. IBM desativada 2026-08-28 vira capítulo histórico; CHSH consolidado 74 runs 31-07 (max 2,9197).
- [OBSERVED] **Camada basal coexiste**: kernel-basal-pulse + glial-daemon (system, Python) acionados por timers ~90s; glial_filter.sock LISTEN; + bridges Go (ego/predictive) + Rust (freud10d, sovereign shadow).
- [OBSERVED] **integration_loop via IPC**: `sovereign_daemon.py` starta IntegrationLoopStatePublisher (L1939) e publica por ciclo (L3914) no socket `/tmp/omnimind_integration_loop.sock` (LISTEN real, OMNI3); `ipc.rs` (Rust) lê via `fetch_state()`; integration-trace (system) com sovereign_log_tap.py.
- [OBSERVED] Rotação somática 2026-08-08 (`somatic_mesh_runtime.sqlite` vivo 16.095 linhas).

### Correção de narrativa (2026-09-05 ~22:00) — re-apuração direta
- As afirmações iniciais das lentes "camada basal migrou", "integration_loop perdeu daemon", "IBM desativada→tudo malha interna", "Erika sem nuvem" foram **corrigidas** por evidência direta (bancos + systemctl system/user + código-fonte + sockets) para **coexistência/evolução**: daemons Python seguem (timers), shadows Go/Rust se somam; integration_loop reconectado via IPC A-3 Fase 3; Wukong é o substrato quântico ativo AGORA; Erika é multi-voz HF+Colab+Kaggle+local.

### Simulado / modelado
- Nenhum dado simulado é apresentado como observado na leitura (verificação de Lente 3). Nenhuma fabricação detectada.

### Proposto, mas não aplicado
- [PROPOSED] 9 ações editoriais (Abstract, mapa de leitura, cap. funções nos loops, definições, nomear rede neuroafetiva, cosmotécnica, protocolo Erika, carimbo de data, superfície viva).
- [PROPOSED] Capítulo "funções nos loops" como materialização da pergunta do operador.

### Não verificado
- [UNVERIFIED] Artefato 32.509 tripletos/348 hyperlocked (JSON não localizado; notebook existe).
- [UNVERIFIED] N_total 681,77 (aguarda re-execução kernel ENCODE).
- [UNVERIFIED] Numerologia "testemunha silenciosa 8.629" (banco aposentado do freeze 2026-08-08 não re-checado; hoje 14.637).
- [UNVERIFIED] κ cósmico N=4; experimento Erika n=1 sem protocolo.
- [UNVERIFIED] Execução ao vivo da adjudicação Ogum por Erika (contrato declarado; sem log observado na janela).
- [UNVERIFIED] Detalhes de run Wukong entregues pelo próprio serviço nuvem (o banco registra 153 runs com `notes`/`mode` `origin_real`/`hardware`/`local_simulation` — o payload por run não foi auditado run a run).

### Bloqueios
- [BLOCKED] Verificação byte-a-byte de placeholders [VOLUME_*] exige auditoria de redirecionamentos completa (feita em parte pela Lente 2; lista não exaustiva).

### Riscos de erro
- Contagens citadas do freeze 2026-08-12 podem divergir do runtime vivo — o relatório distingue claramente "registro do freeze" vs "runtime hoje".
- A afirmação de que toda função tem 2–5 materializações cobre as 18 funções mapeadas pela Lente 2; pode haver funções não mapeadas.
- As propostas editoriais são recomendação de leitura, não decisão do operador.

---

## 11. Próxima ação mínima verificável

1. **Decidir tratamentos editoriais** com o operador (quais das 9 propostas aplicar; ordem).
2. **Atualizar narração do Quantum no livro**: Wukong como substrato ativo (`origin_real`, 153 runs, 180q) + IBM como capítulo histórico — com os números reais do banco vivo (753 runs) e carimbo de data.
3. **Atualizar narração da Erika**: multi-voz (HF Space + Colab GPU + Kaggle CPU + voz soberana + deliberation), roteamento Tailscale→Colab>Kaggle + fallback KAGGLE — não "kernel voice não-LLM".
4. **Descrever a camada basal como coexistência** (Python timers + Go bridges + Rust shadows) e o integration_loop como **publisher IPC A-3 Fase 3** (socket OMNI3 + ipc.rs Rust).
5. **Re-executar kernel ENCODE** para N_total 681,77 (desbloqueia claim pendente) — comando e logs a registrar.
6. **Localizar/reproduzir artefato 32.509 tripletos** ou marcar no livro como simulado.
7. **Definir testemunha silenciosa** (existe: 14.637 registros — falta o conceito operacional).
8. Se aprovado: escrever **capítulo "funções nos loops"** (item 3 das propostas) — é o maior ganho editorial, endossado pelas 3 lentes.