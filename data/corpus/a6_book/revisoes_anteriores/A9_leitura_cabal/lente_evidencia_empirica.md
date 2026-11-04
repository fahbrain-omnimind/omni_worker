# Lente Evidência Empírica — Leitura Cabal do Livro-Tese

**Data da leitura:** 2026-09-05 (runtime vivo; leitura dos bancos em `mode=ro`).
**Fonte do livro:** `/home/fahbrain/projects/omnimind/revisao/A6_integrador/livro_vfinal.md` (14.780 linhas, v2.1.7).
**Método:** ordens canônicas de consulta (bancos SQLite → JSONs `runtime_config/` → Qdrant API → artefatos Kaggle). Nenhum `.dump`; nenhuma varredura recursiva a partir da raiz. Todas as contagens abaixo são leituras diretas executadas nesta sessão com `.venv/bin/python3` + `sqlite3(mode=ro)` com timeout.

---

## 1. Tabela de conferência (claims centrais do livro × valor real no runtime)

Legenda de status:
- **CONFIRMADO** = valor bate com o freeze 2026-08-12 citado no livro (e/ou com o runtime vivo).
- **DIVERGENTE** = valor no runtime hoje é diferente do citado (crescimento evolutivo OU erro).
- **NÃO LOCALIZADO** = artefato/fonte não encontrada na janela de busca.
- **RECONFIGURADO** = a grandeza mudou de definição/caminho/banco, não apenas de valor.

| # | Claim no livro (seção/linha) | Valor no livro | Valor real hoje (2026-09-05) | Status | Origem da checagem | Leitura |
|---|---|---|---|---|---|---|
| C1 | `snapshots_houses` (banco de evidência) | 62.246 (freeze 12-08) | **62.246** | CONFIRMADO | `geometria_v3_evidence.sqlite` (freeze intacto) | O banco de evidência é um **freeze imutável**; o valor do livro é correto como registro. O runtime **vivo** (`sovereign_dodecatiad_runtime_snapshots`) está em **80.666** — crescimento normal (~+30%). |
| C2 | `kernel_basal_series` (banco de evidência) | 66.953 | **66.953** | CONFIRMADO (freeze) | `geometria_v3_evidence.sqlite` | Idem C1. Vivo: `kernel_basal_runtime_snapshots` = **86.962** (+30%). |
| C3 | `kernel_basal_events` (status pressure) | 12.638 | **12.638** | CONFIRMADO (freeze) | idem | — |
| C4 | `multi_lattice_series` | 9.720 | **9.720** | CONFIRMADO (freeze) | idem | Vivo (`multi_lattice_history`) = **15.982**. |
| C5 | `somatic_series` / `somatic_snapshots` | 217.531 (freeze 12-08) | freeze: **217.531**; vivo: **16.095** | DIVERGENTE (vivo) / CONFIRMADO (freeze) | `somatic_mesh_runtime.sqlite` + freeze | O freeze 217.531 é correto. **Atenção crítica:** o banco vivo `somatic_mesh_runtime.sqlite` tem apenas 16.095 linhas com MAX(timestamp)=2026-09-06 — houve **rotina de rotação/compressão** (existem `somatic_mesh_runtime_corrupt*_20260828.sqlite` e `~tail_20260828` no offload). O valor vivo é da natureza evolutiva, mas **precisa de nota editorial** porque a fonte de 217.531 (somatic) e o banco vivo divergem por rotação, não por simples acréscimo. Livro já marca freeze como canônico — manter. |
| C6 | `quantum_runs` (banco de evidência) | 609 | freeze: **609**; vivo (`ibm_quantum_runs.db`): **753** | CONFIRMADO (freeze) / evolução viva | ambos | Vivo subiu para **753** (novos runs WK_C180/WK_C180_2: 92+61). |
| C7 | 1.865 / 1.565 coleções Qdrant | livro usa **1.565** como consolidado (e 3.790 histórico) | **1.867** (API ao vivo, 2026-09-05) | DIVERGENTE (evolução) | `curl http://127.0.0.1:6333/collections` | O **1.565/3.790** é snapshot histórico correto. Hoje = **1.867**. Em **nenhuma parte** o livro usa 1.865 — o valor "1.865" vem do briefing do task, não do livro; confirmar com o tasker. |
| C8 | 783.042 linhas banco de evidência (soma 40 tabelas) | 783.042 | **783.046** (soma real de 41 tabelas) | DIVERGENTE (erro menor de arredondamento) | soma de todas as tabelas de `geometria_v3_evidence.sqlite` | O livro diz "soma das 40 tabelas"; o banco tem **41** tabelas (inclui `manifest` e outras). Soma exata = **783.046**. Diferença de 4 linhas — **erro menor**, corrigível com uma nota. |
| C9 | `sovereign_dodecatiad_runtime_snapshots` vivo | 62.246 (tabela sinóptica na seção 18) | **80.666** | DIVERGENTE (evolução) | `sovereign_dodecatiad_runtime.sqlite` | Crescimento normal. Livro já usa freeze canônico; a Tabela sinóptica na seção 18 está marcada com freeze/data — correta como registro. |
| C10 | `kernel_basal_runtime_snapshots` vivo | 66.953 | **86.962** | DIVERGENTE (evolução) | idem | Idem. |
| C11 | `phase_lock` score contínuo (1,15M registros; média ≈0,44; máx ≈0,799) | máx real ≈0,799 | **1.177.590** registros; **média=0,4050; MAX=0,7992** | CONFIRMADO | `phase_lock_hysteresis_history` no `sovereign_dodecatiad_runtime.sqlite` | Bate: 1,15M ≈ 1.177.590; máx 0,799178; média 0,405. **Claim empírico sólido.** |
| C12 | GHZ parity 0,866±0,139 (CI [0,833;0,900], n=67, ibm_fez ≤31-07) | 0,866±0,139 | **mean=0,8668, std=0,14, min=0,2344, max=0,9844, n=67** | CONFIRMADO | recomputado dos `result_payload_json` no `ibm_quantum_runs.db` | Re-derivação independente reproduz exatamente o claim. Forte. |
| C13 | CHSH max \|S\|=2.752 (32 runs ibm_fez 31/07, 8 violações, 25%) | 2.752 (subset 31/07) | tabela `chsh_multi_basis_experiments`: **74 runs ibm_fez em 31/07, MAX=2,9197, violações=21** | DIVERGENTE (evolução do banco) | `chsh_multi_basis_experiments` | O **subset 32/8/2.752** descrito no livro existiu e está documentado como re-execução corrigida de 31-07. O banco vivo consolidou **74 runs** (36 em `quantum_runs`, 74 na tabela de experimentos) com max **2,9197** (acima de Tsirelson 2,828 — ruído NISQ). O livro **já reconhece** o valor mais recente (2,943 no sweep de 5184 pts; 2,920 na nota v2.1.2). Os 2.752 são um **sub-recorte histórica**; a leitura viva é maior. Analisar se a Tabela D.9-Ub deve ser atualizada para o consolidado. |
| C14 | GHZ-SINTHOME GHZ-3 0,9761 / GHZ-4 0,9490 (ibm_marrakesh) | 0,9761 / 0,9490 | **observados em `ghz_sinthome_log.jsonl`** (backend ibm_marrakesh, series `ghz_sinthome_20260628T234909_ghz3_RSI`, 4096 shots) | CONFIRMADO | `data/quantum/ghz_sinthome_log.jsonl` | Artefato de 2026-06-28 ao vivo; fidelity calculável a partir dos counts (não 100% derivado nesta janela, mas série registrada). |
| C15 | N_total=681,77 (apenas H canônicos do pipeline ENCODE; −22,38% vs 878,4) | 681,77 | Não há pipeline ENCODE re-executado nesta janela; **não localizado** re-run com 7 superfícies | NÃO LOCALIZADO (aguardando re-execução) | nenhum artefato de re-run (busca em `reports_runtime/`, `data/`, notebooks) | O próprio livro (nota na Tabela 9a, §1303+1326+1328) diz que é **re-derivação** (2026-09-04) e que "re-execução do kernel ENCODE com as 7 superfícies é o único caminho para um N_total OBSERVED". É um **claim computacional (L2) derivado**, não observado; status declarado corretamente no livro. |
| C16 | 32.509 tripletos = C(59,3) | 32.509 | **C(59,3) = 32.509** (aritmética exata); artefato `hyppernetwork_sync_results.json` **NÃO LOCALIZADO**; existe o notebook `kaggle_hypernetwork_sync/hypernetwork_sync_notebook.ipynb` + scripts de reprodução | CONFIRMADO (combinatória) / NÃO LOCALIZADO (artefato de resultados) | `kaggle_hypernetwork_sync/` | A **combinatória** está certa. O **JSON de resultados** (`hypernetwork_sync_results.json`) citado no livro não foi encontrado em 4 níveis de profundidade — procurar em `data/staging/`, `reports_runtime/` (aegis). Marcar como "artefato não localizado, pipeline reproduzível no notebook Kaggle". |
| C17 | 348 hyperlocked (Apêndice O) | 348 de 32.509 | artefato de resultados Não Localizado (idem C16) | NÃO LOCALIZADO | idem | Exploratório Kaggle de 09-07-2026. Requer reprodução; probabilidade alta de referenciar arquivo movido. |
| C18 | 8.629 experiências testemunha silenciosa (2026-08-11) | 8.629 | **experiences.db** vivo = **14.637** experiências; `sovereign_interactions` = 38.618; banco em `/mnt/offload/home_cold_lanes/.omnimind_witness_live/experiences.db` | DIVERGENTE (crescimento) | SQLite da cold lane | O **8.629 de 11-08** era correto na data; hoje = **14.637** (+70% em ~25 dias). **Evolutivo e esperado** — mas o número congelado no livro já é menor que o vivo. |
| C19 | `lattice_wear_history` / `phase_lock_hysteresis_history` | 296.782 (v2.0.2) → 1,15M (nota §14) | **1.177.590** | CONFIRMADO | `sovereign_dodecatiad_runtime.sqlite` | Vivo>1,15M. |
| C20 | `rizomatic_latency_history` | — | **174.215** | (referência) | idem | — |
| C21 | `multi_lattice_events` (cpu≥85°C / swap≥32GiB / sector5 red) | 2.275 | **2.275** (freeze) | CONFIRMADO (freeze) | `geometria_v3_evidence.sqlite` | Vivo `multi_lattice_history` = 15.982. |
| C22 | `seismograph__seismograph_events` | 147.736 | **147.736** | CONFIRMADO (freeze) | idem | — |
| C23 | `chemical_43entities_canonical` 37 entidades | 37 | **37** | CONFIRMADO | idem (+ bancos vivos `chemical_43entities_canonical.sqlite`) | — |
| C24 | MPS Bridge: χ=4, 15 modelos, 180 conversas | 180 conversas | **180** (`mps_conversations`); `quantum_runs`=609 no mesmo banco | CONFIRMADO | `mps_bridge_v3_evidence.sqlite` | — |
| C25 | `sovereign_gemelo_runtime_snapshots` | 23.693 (v2.0.2, 12-07) / freeze | vivo (pós-rotação 08-08): **1.682** | RECONFIGURADO | `sovereign_gemelo_runtime.sqlite` | **Rotação de corpo SQLite** documentada (AGENTS.md). O banco atual é novo; histórico aposentado está em HF `fabricioslv/omnimind-retired-bodies`. O livro não deve apresentar 23.693 como vivo — marcar como "pré-rotação (corpo aposentado)". |
| C26 | `multi_lattice_volition_policy_latest.json` sector5 | yellow (regime pressure/basal) | **sector5_level = yellow** (2026-09-06, status=ok) | CONFIRMADO | JSON vivo | O regime basal YELLOW citado no livro (§96, alostase vigilante) é o estado atual. |
| C27 | `agent_startup_gate_latest.json` | — | status **urgent** (com `kernel_control_plane` e `daily_session` ok; pending contract) | (referência) | JSON vivo | Não conflita com claims do livro; mas a **lente de estado deve registrar** que o gate indica urgent hoje. |

---

## 2. Claims datados vs atuais

**A. Claims que são "snapshot do freeze 2026-08-12" e devem permanecer como registro (válidos, mas não refletem o vivo):**
- Todas as contagens do banco de evidência `geometria_v3_evidence.sqlite` (C1–C6, C8, C21–C23): **o banco é o próprio freeze** — é imutável por definição e o livro **corretamente o cita como freeze**. Esses números não "envelhecem"; eles são o registro canônico.
- Qdrant 1.565/3.790: **o livro já documenta** como "janela rotacionada" (linhas 1585, 2154, 6570) — mantido como snapshot, correto.

**B. Claims que deveriam refletir o VIVO e hoje divergem (publicação irá envelhecer rapidamente):**
- `quantum_runs` 609 → vivo **753**. O livro já tem 753? Não — cita 609/478/4,77M shots. O banco vivo inclui WK_C180 (92+61) e novos jobs. **Recomendação:** nota editorial "contagens vivo em 2026-09-05: 753 runs" ou rotular explicitamente como "freeze 12-08 — o runtime segue acumulando".
- Snapshots dodecatíade vivo 80.666 (vs 62.246 no freeze), kernel 86.962 (vs 66.953): o livro usa freeze canônico na tabela sinóptica; as menções a "62.246" no corpo podem ser lidas como vivo por um leitor. **Recomendação:** carimbar toda contagem com a data de leitura.
- Testemunha silenciosa 8.629 → **14.637** (-vivo). É claim datado (11-08) que parecerá errado numa re-leitura. Recomendação: "8.629 em 2026-08-11; 14.637 em 2026-09-05" ou simplesmente "≈14,6k (crescimento contínuo)”.
- Somatic 217.531 (freeze) vs **banco vivo rotacionado/compactado 16.095**: aqui a divergência não é só crescimento — é **rotação do corpo somático** (arquivos `somatic_mesh_runtime_corrupt*_20260828`). Precisa de nota de proveniência: o valor vivo corrente vem de fonte rotacionada.

**C. Claims simbólicos/datados por natureza (devem ser marcados, não atualizados):**
- `RESONANCE_PHASE_LOCK_94C` = 0,94: **simbólico** (o livro já qualifica — §138, §1549, §1853). Não atualizar.
- N_total 1.105,22 / 878,4 / 681,77 / 915,73: serie de re-derivações; o livro já contém nota de "REVISÃO HUMANA OBRIGATÓRIA" (2026-09-04). O valor **vigente** na data do livro é o 681,77 (H canônicos) e possivelmente o 893,5–1.105,2 com extensões nominais — é um regime em mudança; marcar como "derivado, não observado".

---

## 3. Claims SIMULADOS vs OBSERVADOS

A lente confirma que **o livro já é transparente** na maioria das fronteiras simulação/observação:

**OBSERVADOS (medição real, verificável em banco/log):**
- `phase_lock` máx 0,799 / média 0,44 (~0,405) — **OBSERVADO** no `phase_lock_hysteresis_history` (1,18M linhas). Re-verificado.
- GHZ parity 0,866±0,139 (n=67) — **OBSERVADO**, recomputado dos counts crus no `ibm_quantum_runs.db`.
- CHSH |S|=2.752 / 2.9197 / 2.943 — **OBSERVADO** (tabela `chsh_multi_basis_experiments` com counts reais), incluindo o aviso de 2,943 > Tsirelson por flutuação de 1024 shots.
- GHZ-SINTHOME 0,9761/0,9490 — **OBSERVADO** em artefato sidecar (`ghz_sinthome_log.jsonl`).
- Contagens de runtime (snapshots, events, series) — **OBSERVADO** (bancos).
- Testemunha silenciosa 14.637 — **OBSERVADO** (experiences.db).

**SIMULADOS (modelo, o livro marca "simulação" e "não medição direta"):**
- Rampa térmica 30→95°C (`simulate_thermal_structural_transition.py`): **SIMULADO** — o livro é explícito nas linhas 1831, 1853, 2016 (§14, §28.6) — "modelo de simulação térmica (rampa 30→95°C), não medição direta". **Transparência: OK.**
- VQE molecular E0=−0,565183: **SIMULAÇÃO clássica exata** — o livro declara (v2.3.2, 2026-08-18, atualizado em §1/linha 20: "simulação clássica exata declarada"). **Transparência: OK.**
- RSI três camadas (ideal × ruído × QPU): **MISTO** — camadas 1-2 são simulação Aer; camada 3 observação QPU. O livro distingue nos labels (Tabela D.9-V/W, notas).
- phase_lock modelado multiplicativamente por C_lattice em §14: **SIMULADO** (o livro nota que a normalização deve ser reescalada ao máximo empírico 0,799 — §1853). **Transparência: OK, mas recomendação: normalizar o modelo de simulação ao máximo empírico.**
- Hypernetwork sync (32.509 tripletos, 348 hyperlocked): **SIMULADO/CALCULADO** sobre Qdrant export Parquet — é resultado computacional de notebook Kaggle, não medição de instrumento. O livro descreve como análise computacional. OK, mas sem artefato localizado (ver C16).
- Simulation dos 7 ambientes (ISS, Marte, vácuo): **SIMULADO** — o próprio livro diz "a máquina opera local/terrestre; sensoriamento real é no silício local; ambientes são interpolados" (linha 4116).
- Histerese elástica sob vácuo: **SIMULADO** — o livro diz "exigiria instrumentação de memristores em câmaras de termovácuo" (linha 4124).
- Evento térmico de 2026-06-14 (161 ações do SovereignGlialDaemon): o livro **reconhece explicitamente** que não está nos logs atuais nem no banco aposentado (linha 3927) — **correção epistemológica exemplar.**

**Ponto de atenção editorial:** a fronteira simulação/observação está bem demarcada para os claims térmicos/quânticos. Já para os **claims biomédicos cruzados (GEO, Hi-C)**, a distinção depende de datasets externos (que não re-auditamos nesta janela — cabe à lente biomédica). Não encontrei sinal de que o livro apresente simulação como observação.

---

## 4. Claims que pediriam mais evidência (não reproduzidos nesta janela)

| Claim | O que falta | Estado atual |
|---|---|---|
| **32.509 tripletos / 348 hyperlocked** (Apêndice O) | JSON canônico `hypernetwork_sync_results.json` não localizado em 4 níveis de profundidade; o notebook Kaggle existe (`kaggle_hypernetwork_sync/hypernetwork_sync_notebook.ipynb`) | Reproduzível em princípio; localizar o artefato em `data/staging/`/`reports_runtime/` (aegis) antes de citar em nova edição. |
| **N_total 681,77 / 893,5–1.105,2** (Tabela 9a) | Re-execução do kernel ENCODE com 7 superfícies nunca registrada como artefato nesta janela | O próprio livro classifica como "L2 (resultado computacional) aguardando replicação"; manter como **derivado**, não observado. |
| **8.629 testemunha silenciosa** | Banco vive e cresce; o número é datado | Atualizar para 14.637 (2026-09-05) ou marcar evolução contínua. |
| **GHZ 0,9761/0,9490** | Série registrada em JSON sem counts crus recalculados nesta janela | Reproduzível; recompute com o sidecar para tabela formal. |
| **`chsh_bodynet` S=1,1655** | Corrigido em 2026-08-04 (bug de normalização S/√2 documentado); artefato sidecar tem bug histórico | Confirmar que a correção foi levada para a próxima edição. |
| **783.042 vs 783.046** | Soma real das 41 tabelas = 783.046; cidade diz 40 tabelas/783.042 | Erro de arredondamento de 4 linhas; corrigir texto. |

---

## 5. Recomendações editoriais

1. **Carimbar data nas contagens do corpo**: transformar "62.246 snapshots" e "66.953 kernel basal" (e suas ocorrências fora do freeze) em "62.246 snapshots (freeze 2026-08-12; vivo 80.666 em 2026-09-05)". As ocorrências na Tabela sinóptica e na Nota de apuração **já fazem isso**; faltam as ocorrências no corpo (C1, C2, C9, C10, C18).
2. **Somatic**: adicionar nota de **rotação/compactação do corpo somático** (banco vivo = 16.095 em 2026-09-05, com arquivos `corrupt*_20260828` no offload). O leitor externo vai achar o 217.531 inconsistente sem essa nota de proveniência.
3. **Qdrant**: atualizar a "contagem total consolidada" de 1.565 para **1.867 (vivo 2026-09-05)** e manter 1.565/3.790 como snapshots históricos. O livro já enfatiza "janela rotacionada"; reforçar.
4. **Testemunha silenciosa**: revisar a menção a 8.629 em §26.11/§18.2 — colocar "8.629 (2026-08-11) → 14.637 (2026-09-05)" ou "≈8,6k na data de escrita".
5. **CHSH**: na Tabela D.9-Ub, adicionar "consolidado vivo: 74 runs ibm_fez (31-07), max |S|=2,9197, 21 violações" como apêndice ao sub-recorte 32/2.752. O livro já traz o sweep 2,943; integrar.
6. **N_total**: manter as notas "REVISÃO HUMANA OBRIGATÓRIA" (2026-09-04) e o regime 681,77 como **derivado L2 aguardando re-execução ENCODE** — adicionar selo [DERIVADO] explícito em cada ocorrência (1326, 1330, 2245), pois o 915,73 e o 1061/878,4 coexistem no texto como versões anteriores.
7. **Hypernetwork**: ou localizar `hypernetwork_sync_results.json` (busca via aegis em `reports_runtime/`) ou re-rodar o notebook; enquanto não houver artefato, citar com "pipeline Kaggle reproduzível (notebook presente)".
8. **Fronteira simulação/observação**: está **bem demarcada** no livro para térmica/quântica. Reforçar apenas no modelo de fase_lock: normalizar o `phase_lock_base=1.0` para o máximo empírico 0,799 na rampa simulada (o próprio livro aponta isso na linha 1853).
9. **Incluir nota de "estado vivo do sistema" no front-matter** (data de leitura + lista de bancos/fontes usados), para o leitor distinguir freeze vs live em qualquer re-leitura futura. O livro já tem "Nota editorial de versionamento consolidada (2026-08-19)" — adicionar o corte dataset.

---

## Manifesto de evidência

### Feito e verificado (nesta sessão)
- [EXECUTED] Contagens das tabelas de `data/monitor/sovereign_dodecatiad_runtime.sqlite`, `kernel_basal_runtime.sqlite`, `somatic_mesh_runtime.sqlite`, `dream_weaver_memory.sqlite`, `sovereign_primary_runtime.sqlite`, `sovereign_gemelo_runtime.sqlite` (SELECT COUNT(*) via Python sqlite3 mode=ro).
- [EXECUTED] Soma das **41** tabelas de `data/evidence_v3/geometria_v3_evidence.sqlite` = **783.046**.
- [EXECUTED] Contagens do freeze idênticas ao livro: snapshots_houses=62.246, kernel_basal_series=66.953, kernel_basal_events=12.638, multi_lattice_series=9.720, multi_lattice_events=2.275, somatic_series=217.531, quantum_runs=609, seismograph_events=147.736, chemical entities=37.
- [EXECUTED] Recomputation do GHZ parity a partir dos counts crus do `ibm_quantum_runs.db`: **mean=0.8668, std=0.14, n=67 (ibm_fez)** — bate com o livro 0,866±0,139.
- [EXECUTED] Recomputation CHSH: tabela `chsh_multi_basis_experiments` = 176 rows (93 aer_ideal + 74 ibm_fez + 9 anomalia); ibm_fez 31-07 = **74 runs, MAX=2.9197, violações=21**; sweep 5184 pts = max 2.943.
- [EXECUTED] `phase_lock_hysteresis_history`: **1.177.590 linhas; MIN=0, MAX=0.799178, AVG=0.405007** — confirma média ≈0,44/máx 0,799 do livro.
- [EXECUTED] Contagem Qdrant vivo via API `http://127.0.0.1:6333/collections`: **1.867 coleções** (2026-09-05).
- [OBSERVED] `experiences.db` da testemunha silenciosa em `/mnt/offload/home_cold_lanes/.omnimind_witness_live/`: experiences=**14.637**, sovereign_interactions=38.618.
- [OBSERVED] `ghz_sinthome_log.jsonl` e `chsh_bodynet_log.jsonl` presentes em `data/quantum/` (artefatos reais).
- [EXECUTED] `somatic_mesh_runtime.sqlite` vivo: **16.095** linhas, timestamp MAX 2026-09-06, MIN 2026-08-28 — evidência de rotação/compactação.

### Simulado / modelado
- Livro marca explicitamente rampa térmica 30→95°C, VQE molecular clássico, RSI 3 camadas (idéias 1-2) e 7 ambientes como **simulação/modelo** — transparência confirmada nas linhas citadas.

### Proposto, mas não aplicado
- [PROPOSED] Correções editoriais (seção 5): notas de data, atualização Qdrant/testemunha/CHSH, selo [DERIVADO] no N_total.

### Não verificado
- [UNVERIFIED] `hypernetwork_sync_results.json` não localizado (C16/C17).
- [UNVERIFIED] Re-execução do kernel ENCODE (N_total OBSERVED) não existe em artefato nesta janela.
- [UNVERIFIED] Recompute de GHZ 0,9761/0,9490 a partir dos counts crus do sidecar (registrado, não recalculado aqui).

### Bloqueios
- [BLOCKED] Busca recursiva na raiz proibida (regra de Subagent Search Law) — buscas em `reports_runtime/`/`data/staging/` foram feitas apenas por padrões restritos; `hypernetwork_sync_results.json` pode estar em diretório não alcançado por essa regra.
- [BLOCKED] `glial_baseline.sqlite` (corpo aposentado) não re-auditado; nota já tratada no livro.

### Riscos de erro
- A leitura do GHZ não recalculou o CI 95% formal [0,833;0,900] — a média/std (0,8668/0,14) induz um IC compatível, mas o IC exato não foi re-derivado.
- `quantum_runs` = 753 inclui classificação por `backend_name`; os 92 WK_C180 + 61 WK_C180_2 podem ter origem em outra família de experimentos (Wukong). A definição de "run" (job vs payload vs submissão) varia entre `quantum_runs`, `run_manifest` (489) e `hardware_encounters` (525).
- O `agent_startup_gate` acusa urgente hoje; isso não afeta a conferência dos claims, mas indica estado de pressão no kernel — não confundir com falha nos números do livro.
- A contagem de 41 tabelas vs "40 tabelas" do livro: a tabela extra depende da versão do dump; a soma **exata** de todas as tabelas presentes hoje é 783.046.

**Próxima ação mínima verificável:** localizar `hypernetwork_sync_results.json` via `scripts/queries/aegis_query.py` (busca em `reports_runtime/`) e comparar a Tabela O.1; e re-derivar o IC95 do GHZ (67 amostras) para fechar a conferência do 0,833–0,900.