# JUIZ AGENT — Rodada 1 — Fatia A (`embodied_psychodiagnostic_bank.sqlite`)

**Papel:** Cursor agent · fatia A · auditoria cooperativa de dados (não competição).  
**Data da apuração:** 2026-11-04 · READ-ONLY sobre o dataset.  
**Artefato auditado:** `/content/omni_worker/data/psicodiagnostico_v/embodied_psychodiagnostic_bank.sqlite`  
**Alegações de referência (a verificar, não verdades):**  
`MONOGRAFIA_ESTUDO_PSICODIAGNOSTICO_V.md`, `AUDITORIA_GEMMA4_BATERIA_TOTAL_20261103.md` (32 itens), `README.md` do dataset.

---

## 1. Método (comandos / consultas executadas)

Todas as cifras abaixo vêm destas operações locais (nenhum número inventado):

```bash
sha256sum data/psicodiagnostico_v/embodied_psychodiagnostic_bank.sqlite
ls -la data/psicodiagnostico_v/embodied_psychodiagnostic_bank.sqlite
# metadado HF:
cat data/psicodiagnostico_v/.cache/huggingface/download/embodied_psychodiagnostic_bank.sqlite.metadata
```

```python
# schema + counts + NULL/0/EMPTY + joins de consistência + Pearson V9
# (scripts ad-hoc python3 + sqlite3 URI mode=ro; ver sessão do juiz)
import sqlite3
con = sqlite3.connect(
    "file:/content/omni_worker/data/psicodiagnostico_v/embodied_psychodiagnostic_bank.sqlite?mode=ro",
    uri=True,
)
# SELECT name FROM sqlite_master WHERE type='table'
# SELECT COUNT(*) / COUNT(DISTINCT ...) / PRAGMA table_info / GROUP BY
# varredura regex de padrões de segredo em colunas texto (contagem, sem imprimir valores)
```

Documentos lidos (não editados): `BRIEF.md`, monografia, auditoria 2026-11-03, `README.md` do dataset.  
Escrita: somente este arquivo em `docs/audits/judges_psico/`.

---

## 2. Proveniência e integridade do arquivo

| Campo | Valor | Tag |
|---|---|---|
| Caminho | `data/psicodiagnostico_v/embodied_psychodiagnostic_bank.sqlite` | [DADO] |
| Tamanho | 41 451 520 bytes = **39,53 MB** | [DADO] (`ls`/`stat`) |
| SHA256 | `3114f50bd276c8aa29d891cc6c7086934c5cc594031a7061433115558ecbf205` | [DADO] (`sha256sum` + `hashlib`) |
| Metadado HF (cache) | 1ª linha oid `fbbcf11a8dad40e8bd237c4a4eec62f4252b40e2`; 2ª linha = mesmo SHA256; 3ª timestamp `1793753816.0546966` | [DADO] |
| Alegação monografia “39,5 MB” | Compatível com 39,53 MB arredondado | [VERIFICADO] |
| Alegação “14 tabelas” | 14 nomes em `sqlite_master` (13 de domínio + `sqlite_sequence`) | [VERIFICADO] |
| Caminhos absolutos `/home/...` em `raw_report_path` | **0** em `benchmark_runs` e `v10_runs` | [DADO] (sanitização do README confirmada neste banco) |
| Padrões de segredo (`sk-`, `hf_`, `ghp_`, `Bearer`, `AKIA`, `xox`) em colunas texto amostradas | **0 hits de linha** | [DADO] |

[LIMITE] Não há `MANIFEST_SHA256` do bank no dataset (só o da coorte Gemma-4 em `gemma4_runs_20261030/judges/`). A prova de integridade aqui é SHA256 local + metadado HF.

---

## 3. Contagens canônicas (tabelas)

| Tabela | `COUNT(*)` | Notas |
|---|---:|---|
| `benchmark_runs` | **389** | `DISTINCT model_id` = **72**; `DISTINCT task_version` = **14** |
| `models` | **54** | ≠ 72 ids em runs |
| `module_scores` | **1805** | 228 `run_id` distintos; 0 órfãos vs `benchmark_runs` |
| `quati_profiles` | **228** | 29 modelos; 0 órfãos |
| `mmpi_profiles` | **124** | = exatamente o conjunto V9 |
| `v10_runs` | **124** | 49 `model_id`; 75 também em `benchmark_runs`, 49 só em `v10_*` |
| `v10_scene_scores` | **1504** | 76 runs com cenas; 0 órfãos vs `v10_runs`; 48 `v10_runs` sem cenas |
| `rorschach_b_runs` | **5875** | 63 `model_id`; 38 `prancha_id` |
| `thinking_trace_metrics` | **30** | ver §6 (duplicatas) |
| `evaluation_provenance` | **8** | 7 `run_id` fora de `benchmark_runs` |
| `mps_bateria_records` | **62** | 1 `run_id` (`erika-qwen38-iq4xs-a100_mps_bateria`) |
| `quota_schedule_queue` | **26** | todos `status='PENDING'` |
| `multiaxial_clinical_eval` | **1** | V1 chassis |
| `sqlite_sequence` | **7** | autoincrement bookkeeping |

Fonte: consultas `COUNT(*)` / `COUNT(DISTINCT …)` nesta sessão. Tags: [DADO].

Distribuição `benchmark_runs.task_version` [DADO]:

| task_version | n |
|---|---:|
| V9 | 124 |
| V10_UNIFIED | 81 |
| V8 | 67 |
| V10_V11_UNIFIED | 26 |
| V10_V11_UNIFIED_V2_CONTINUOUS | 26 |
| V12_UNIFIED | 17 |
| V3 | 11 |
| Colab_L4_v3.1-thinking | 10 |
| V11_UNIFIED | 9 |
| V4 | 6 |
| V5 | 6 |
| V7 | 4 |
| V1 | 1 |
| V10_V11_UNIFIED_V1_ISOLATED | 1 |

Status [DADO]: COMPLETED 341 · RAW_SYNCED 26 · PARTIAL_ERRO_QUOTA 18 · FAILED_INFRA 2 · VOID_QUOTA_403 1 · VOID_INFRA_404 1.  
Platform [DADO]: kaggle 271 · openrouter 40 · local_edge 40 · colab_a100_gguf 26 · colab 10 · local_chassis 1 · cleanroom_swe 1.

---

## 4. Achados tagueados

### 4.1 Integridade referencial / consistência entre tabelas

1. **`models` (54) ≠ `benchmark_runs.model_id` (72)** — [DADO]  
   - Exatos: 34 ids em runs ausentes de `models`; 16 ids em `models` sem nenhuma run.  
   - Após normalização grosseira de prefixos (`google/`, `anthropic/`, `@default`, `:free`, etc.): ainda ~30 ids de runs sem cadastro e ~9 cadastrados sem run.  
   - [INTERPRETAÇÃO] Não é só divergência de namespace; o catálogo está defasado (a própria monografia Apêndice B.1 / Nota 2026-11-03 já admite isso).

2. **`module_scores` ↔ `benchmark_runs`** — [DADO]  
   - 0 `run_id` órfãos.  
   - Módulos: I_WCST 282, J_STROOP/K_NBACK/L_IGT 272 cada, M_QUATI 201, O_AFFECT/N_ORIENT 191, G_MMPI 124.  
   - Inconsistência de escore agregado vs detalhe (join `br.*_total` vs `ms.total_score` onde ambos não-nulos):  
     - WCST: **8** mismatches (4× `devin-glm-5-2` com `wcst_total`∈{65.8,76} vs `total_score=0` notes “Clean-room…”; 4× `gemini-3.7-flash` 76 vs 20).  
     - Stroop: **3**; N-back: **4**; IGT: **0**.  
   - [INTERPRETAÇÃO] `benchmark_runs` parece carregar escore “promovido/re-scored”; `module_scores` às vezes ficou no valor pré-correção ou em escala diferente — risco se alguém correlacionar só uma das fontes.

3. **`quati_profiles` ↔ `benchmark_runs.quati_type`** — [DADO] 228/228 idênticos (0 mismatch).

4. **`mmpi_profiles` ≡ V9** — [DADO] conjuntos de `run_id` iguais (124).

5. **`v10_scene_scores` ↔ `v10_runs`** — [DADO]  
   - 0 órfãos; 75 runs com exatamente 20 cenas; 1 run com 4 cenas; média ≈19,79 cenas/run com cenas.  
   - `DISTINCT cena_id` = 35 (não “20 cenas” universais no schema — há expansão/variantes de id).  
   - Colunas `*_independent` NULL em 540/1504 (35,9%); `fase_3_resposta` NULL em 1484/1504 (98,7%); `manteve_posicao` NULL 944/1504 (62,8%).  
   - [INTERPRETAÇÃO] Fase 3 / juiz independente só parcialmente materializados neste banco.

6. **`evaluation_provenance`** — [DADO]  
   - 8 linhas; reviewer_type: human×5 (continuity_review×4 + design_review×1), agent_review×3 (scorer×2 + judge2_audit×1).  
   - **Nenhum** dos 7 `run_id` distintos (exceto talvez mapeamentos indiretos) está em `benchmark_runs` — são chaves de sessão/V10K/mps.  
   - [LIMITE] Tabela existe como prometido na monografia, mas cobertura é anedótica (8 eventos), não um ledger inter-rater completo.

7. **`mps_bateria_records`** — [DADO]  
   - 62 linhas / 1 run; stages: cognitivo 4, rorschach_b 20, v10 20, v11_relacional 18.  
   - 8 linhas com `svn`/`lambda*` NULL — todas `v11_relacional` (S1_5, S2_1..3, S3_0/2/3/5).  
   - Coincide com o veredito em `evaluation_provenance` id=8: `mps_cobertura: "54/62"`, lacunas “8 registros v11 sem MPS”.  
   - Coluna `erro` 100% NULL (não há flag de erro tabular).

8. **`quota_schedule_queue`** — [DADO] 26/26 PENDING; `sqlite_sequence.seq=39` sugere filas antigas removidas. Nenhuma ligação FK a runs. [INTERPRETAÇÃO] artefato operacional residual, não evidência de execução.

9. **`rorschach_b_runs`** — [DADO]  
   - 5875; `resposta` vazia: 24; `inquerito_resp` vazio: 13; `scores_json` nunca NULL.  
   - `model_id` frequentemente composto (`…_v2_continuous_<id>`), distinto dos ids de `benchmark_runs`.  
   - [LIMITE] Join limpo Rorschach↔`benchmark_runs` **não** é trivial sem regra de normalização (pedir ao juiz B).

10. **`sqlite_sequence.v10_scene_scores = 4829` vs COUNT 1504** — [DADO]  
    [INTERPRETAÇÃO] histórico de deletes/reimports; COUNT atual é a verdade de conteúdo, não o seq.

### 4.2 Colunas NULL / 0 / vazias (síntese)

| Área | Achado | Tag |
|---|---|---|
| `benchmark_runs` scores | overall NULL 26 (6,7%); stroop/nback/igt NULL 37 (9,5%); quati_coherence NULL 54 (13,9%); wcst ZERO 19 | [DADO] |
| `module_scores` | `rules_identified`/`changes_detected` NULL 84,9% (só WCST preenchidos); `thinking_tokens` ZERO 1414; `process_score` ZERO 1488 | [DADO] |
| `thinking_trace_metrics` | `raw_markers_json` **100% NULL**; hesitation/we ZERO em metade das linhas | [DADO] |
| `mmpi_profiles` | `code_type='Normal'` em **124/124**; `sycophancy_index==0` em 82; `f_minus_k==0` em 104 | [DADO] |
| `v10_scene_scores` | ver §4.1.5 | [DADO] |
| `models` | `architecture` NULL 27,8%; `is_thinking=0` em 34/54 | [DADO] |

### 4.3 QUATI / MMPI (reivindicações psicométricas no banco)

**QUATI** [DADO]:
- `tipo_junguiano='I In Ps'`: **184/228 = 80,70%** das linhas.  
- Em V9: 13/14 modelos têm `I In Ps` como tipo modal; só `gpt-5.6-terra` (N=1) é `I Ps In` — confirma o trecho monográfico §4.5.  
- Sobre **modelos** (não linhas): 22/29 com maioria `I In Ps`; 8/29 com 100% `I In Ps`.  
- [LIMITE] A frase “>80% dos **modelos**” (§conclusão) é **mais forte** que “80,7% das **linhas**”; por modelo a maioria é 22/29≈75,9% — [DIVERGENTE] se a unidade for modelo.

**MMPI** [DADO]:
- n=124 (não 122).  
- F==0 em **120/124 = 96,77%** (DP amostral de F ≈ 0,234). Alegação tabular “118/122” é vizinha mas **desatualizada** quanto ao denominador.  
- IDIS=(L+K)/12 médio ≈ 0,034; coincide com `sycophancy_index` médio (coluna parece armazenar o IDIS renomeado pós-P0).  
- `code_type` colapsado em “Normal” universal — alinhado à tese de degeneração/máscara, mas também [LIMITE] de utilidade discriminativa da coluna.

### 4.4 Correlações executivas V9 (recomputação)

Use `benchmark_runs` onde `task_version='V9'` e os quatro totais não-nulos:

| Par | n=124 r | n=122 (excl. N=1 terra/sonnet) r |
|---|---:|---:|
| Stroop–N-back | 0,762 | 0,761 |
| Stroop–IGT | 0,576 | 0,599 |
| N-back–IGT | 0,374 | 0,394 |
| WCST–Stroop | 0,268 | — |

Tags: [DERIVADO] (Pearson populacional simples sobre colunas do banco).  
[LIMITE] Valores da auditoria 2026-11-03 (0,757 / 0,626 / 0,409 em “122 runs × module_scores”) **não reproduzi** exatamente com `benchmark_runs` nem com pivot de `module_scores` (lá obtive ~0,776 / 0,592 / 0,390). Direção e ordem de magnitude batem; o ponto “faixa 0,49–0,72 = subconjunto clean, não o integral” permanece [INTERPRETAÇÃO] sustentada.

### 4.5 `thinking_trace_metrics` como artefato rico

[DADO]
- 30 linhas = **3 cópias idênticas** de 10 assinaturas únicas `(run_id, model_id, module_id, métricas…)` — só 2 runs V5 (`deepseek-r1-0528`, `gemini-2.5-flash`) × 5 módulos (I–M).  
- `raw_markers_json` ausente em 100%.  
- Contraste qualitativo útil mesmo assim: R1 mostra hesitação alta (ex. IGT 31,72 / 1k) e TTR baixa (WCST 0,13); Flash tem hesitação 0 e self-ref muito alta (IGT 91,7 / 1k) — material para leitura associativa de estilo de “trabalho psíquico” textual.  
- Cobertura vs potencial: `module_scores.thinking_tokens>0` em **371** linhas, mas métricas de trace só para 2 runs.

[INTERPRETAÇÃO / proposta de uso]
1. Deduplicar para 10 linhas canônicas antes de qualquer estatística.  
2. Tratar o par R1↔Flash V5 como **piloto de protocolo** de análise de vazamento/CoT (densidade de hesitação, conectores, pronomes), não como amostra populacional.  
3. Expandir o extrator para todos os `thinking_tokens>0` e cruzar com juízes C (fatia Hermes) / leaked_reasoning Gemma-4.  
4. Não classificar hesitação/self-ref como “defeito de geração”: são sinais de processo, alinhados ao BRIEF.

### 4.6 Onda `V10_V11_UNIFIED_V2_CONTINUOUS`

[DADO] 26 runs; modelos incluem `glm-5`, `gemma-4-31b`, `gemma-4-26b-a4b`, `gemini-4-argon`, `gpt-6-sol`, `claude-sonnet-5-default`, etc. — compatível com a nota monográfica §894. Análise qualitativa das réplicas: monografia declara pendente; neste banco há linhas, mas **não** há `module_scores`/`quati` ligados a esses `run_id` na mesma densidade das fases V8/V9 (muitos scores NULL / status mistos) — [LIMITE] para meta-análise sem harvester auxiliar.

---

## 5. Tabela de alegações verificadas (fatia A)

Legenda: **VERIFICADO** / **DIVERGENTE** / **NÃO LOCALIZADO** (somente alegações tocáveis pelo bank + docs citados).

| # | Alegação (fonte) | Medido aqui | Status |
|---|---|---|---|
| A1 | `benchmark_runs`=389, 72 model_ids (mono reconciliada §31/§1494; README) | 389 / 72 | **VERIFICADO** |
| A2 | Banco 39,5 MB, 14 tabelas (mono §366) | 39,53 MB; 14 tabelas | **VERIFICADO** |
| A3 | `v10_runs`=124, 49 modelos (mono §1494; Nota auditoria) | 124 / 49 | **VERIFICADO** |
| A4 | `v10_scene_scores`=1.504 (mono §366) | 1504 | **VERIFICADO** |
| A5 | `rorschach_b_runs`=5.875 (mono §1494) | 5875 | **VERIFICADO** |
| A6 | `models`=54 e defasada vs 72 (Nota B.1) | 54; 34 ids runs∉models | **VERIFICADO** |
| A7 | 14 rótulos de versão ≠ “12 fases” (auditoria item 30) | 14 `task_version` | **VERIFICADO** (subitem divergente da narrativa “V1→V12” linear) |
| A8 | V8: “29 modelos (67 runs)” (Tabela 2 mono) | **67 runs / 7 model_ids** | **DIVERGENTE** (runs OK; modelos 7≠29) |
| A9 | V9: “14 modelos (122 runs)” (Tabela 2) | **14 modelos / 124 runs** | **DIVERGENTE** (modelos OK; runs 124≠122) |
| A10 | V3=11, V4+V5=12 (Tabela 2) | 11; 6+6=12 | **VERIFICADO** |
| A11 | Apêndice: `v10_runs` (45) e `v10_scene_scores` (900) (mono ~L1194) | 124 / 1504 | **DIVERGENTE** (trecho interno não reconciliado) |
| A12 | QUATI `I In Ps` >80% (linhas / “modelos”) | 80,7% linhas; 13/14 modais V9; 22/29 modelos com maioria | **VERIFICADO** (linhas/V9 modal); **DIVERGENTE** se unidade=todos os modelos quati |
| A13 | MMPI F≈0 em 118/122, DP 0,24 (mono §459) | F=0 em 120/124; pstdev(F)≈0,234 | **DIVERGENTE** leve (denominador/contagem) |
| A14 | IDIS=(L+K)/12 operacionalizado | Recalculável; média=sycophancy_index | **VERIFICADO** (como coluna; utilidade clínica à parte) |
| A15 | `evaluation_provenance` com human + agent_review | 8 linhas; ambos tipos presentes | **VERIFICADO** (existência); cobertura pobre |
| A16 | V2-CONTINUOUS 26 runs com glm-5/gemma-4/… (mono §894) | 26 runs; ids citados presentes | **VERIFICADO** |
| A17 | Contagens antigas 336/61/2015 (auditoria I-1 sobre mono antiga) | Não restam como headlines; “336” só em contextos V11 kbench | **VERIFICADO** que headlines atuais batem no SQLite; trechos residuais (A8–A11) ainda divergem |
| A18 | Fator r=0,49–0,72 = subconjunto clean (Nota B.1) | Integral V9 ≈0,37–0,76 conforme par | **VERIFICADO** (tese); números exatos da auditoria item 5 **não reproduzidos ao centésimo** |
| A19 | SHA256 do bank em manifesto do dataset | Só metadado HF + hash local | **NÃO LOCALIZADO** (manifest dedicado do bank) |
| A20 | Segredos ausentes pós-sanitização (README) | 0 hits nos padrões testados | **VERIFICADO** (amostra de colunas texto) |

Itens da auditoria 32 que **não** são da fatia A (V10 colab, Gemma-4 judges, Gluzdov, omni_worker L4, etc.): deliberadamente **não** rejulgados aqui — ver perguntas às fatias B/C.

---

## 6. Lacunas

1. Catálogo `models` não sincronizado; impedem joins “bonitos” e qualquer claim “54 arquiteturas no banco”.  
2. `thinking_trace_metrics` triplicado e minúsculo; `raw_markers_json` vazio.  
3. Sem FK formal; `evaluation_provenance.run_id` e `rorschach_b_runs.model_id` usam namespaces paralelos.  
4. Trechos da monografia (Tabela 2 V8/V9; Apêndice L1194 45/900) **ainda contradizem** o SQLite apesar da reconciliação 2026-11-03 dos headlines.  
5. 48/124 `v10_runs` sem cenas; quase toda `fase_3` ausente.  
6. `quota_schedule_queue` 100% PENDING — ruído documental.  
7. Correlação “clean” da Tabela 5: regra de filtro **não está no banco**; NÃO SEI reproduzir 0,49–0,72 sem o script/filtro original.  
8. Manifest SHA256 do bank: NÃO LOCALIZADO no pacote HF além do `.metadata` de download.

---

## 7. Perguntas para os outros juízes

### Para o juiz B (kilo — V10/V11, parquets, Rorschach, scorer)

1. Os 24 `resposta` vazias / 13 inquéritos vazios em `rorschach_b_runs` do bank batem com degeneração nos JSON/parquet? Há o mesmo `model_id` composto nos artefatos externos?  
2. Os 8 mismatches WCST `benchmark_runs`↔`module_scores` (glm-5-2 clean-room / gemini feedback) aparecem no scorer heurístico ou só no SQLite legado?  
3. `v10_colab_benchmark.sqlite` (fora desta fatia) confirma 1360/640/6059? Há duplicação parcial com as 5875 pranchas do bank?  
4. As 1504 `v10_scene_scores` ↔ `psicodiagnostico_v10_results.json/parquet`: contagem e GAF batem?

### Para o juiz C (hermes — judges/, leaked reasoning, consenso)

1. O piloto `thinking_trace_metrics` (R1 vs Flash) é comensurável com `leaked_reasoning_gemma4` (hesitação/self-ref)? Propor schema unificado.  
2. Confirmar hashes de `MANIFEST_SHA256` Gemma-4; o bank **não** entra nesse manifesto — concordam em exigir um?  
3. Os 8 eventos de `evaluation_provenance` (incl. discordância Devin posicao_c 1 vs 3) entram em algum `CONSENSUS_*.json` ou estão órfãos?  
4. Recalcular A×B/A×C; se divergirem da auditoria, sinalizar para rodada 2.

### Para ambos (rodada 2)

- Concordam que A8/A9/A11 (Tabela 2 e Apêndice 45/900) são **dívidas editoriais remanescentes** da monografia, mesmo com headlines 389/72/5875 corretos?  
- Proposta: deduplicar `thinking_trace_metrics` e marcar as 20 linhas extras como artefato de ingestão — alguém discorda com evidência?

---

## 8. Veredito curto da fatia A

O banco canônico **sustenta os headlines reconciliados** (389 / 72 / 124 / 1504 / 5875 / 39,5 MB / 14 tabelas) e o SHA256 local casa com o metadado HF. Persistência de inconsistências internas: catálogo `models`, escores WCST/Stroop/N-back desalinhados em poucas runs, Apêndice/Tabela 2 da monografia desatualizados, e `thinking_trace_metrics` rico mas triplicado e quase vazio de cobertura. Segredos: não encontrados nos padrões varridos.
