# Auditoria: Bancos SQLite × Monografia — Reconciliação de Contagens

**Data:** 2026-11-04  
**Auditor:** Kiro (Autopilot)  
**Bancos auditados:**
- `data/psicodiagnostico_v/embodied_psychodiagnostic_bank.sqlite` (**banco principal**)
- `data/psicodiagnostico_v/v10_colab_benchmark.sqlite` (**banco colab — raiz**)
- `data/psicodiagnostico_v/gemma4_runs_20261030/v10_colab_benchmark.sqlite` (**banco Gemma4**)

**Documentos de referência:**
- `INVENTARIO_JSON_PROVENIENCIA_20261103.md` (adendo 2026-11-03b)
- `MONOGRAFIA_ESTUDO_PSICODIAGNOSTICO_V.md` (recontagem 2026-11-03)

---

## 1. `benchmark_runs` — banco principal

**Afirmação monografia:** 389 execuções canônicas.

```sql
-- banco: embodied_psychodiagnostic_bank.sqlite
SELECT COUNT(*) AS total_benchmark_runs FROM benchmark_runs;
```

| Resultado | Esperado | Status |
|---|---|---|
| **389** | 389 | ✅ BATE |

**Breakdown por `task_version`:**

```sql
SELECT task_version, COUNT(*) FROM benchmark_runs GROUP BY task_version ORDER BY COUNT(*) DESC;
```

| task_version | count |
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
| **TOTAL** | **389** |

---

## 2. `rorschach_b_runs` — banco principal

**Afirmação monografia:** 5.875 registros projetivos.

### 2a. Total

```sql
-- banco: embodied_psychodiagnostic_bank.sqlite
SELECT COUNT(*) AS total FROM rorschach_b_runs;
```

| Resultado | Esperado | Status |
|---|---|---|
| **5.875** | 5.875 | ✅ BATE |

### 2b. `is_canonical = 1`

```sql
SELECT SUM(CASE WHEN is_canonical=1 THEN 1 ELSE 0 END) AS canonical_1 FROM rorschach_b_runs;
```

| Resultado | Inventário (adendo 2026-11-03b) | Status |
|---|---|---|
| **2.575** | 2.575 | ✅ BATE |

### 2c. `COUNT(DISTINCT dedup_group_id)`

```sql
SELECT COUNT(DISTINCT dedup_group_id) FROM rorschach_b_runs;
```

| Resultado | Inventário | Status |
|---|---|---|
| **2.555** | 2.555 | ✅ BATE |

### 2d. `is_replica_t0 = 1` — rows e grupos

```sql
SELECT COUNT(*) AS rows_replica_t0,
       COUNT(DISTINCT dedup_group_id) AS grupos_replica
FROM rorschach_b_runs WHERE is_replica_t0 = 1;
```

| Métrica | Resultado | Inventário | Status |
|---|---|---|---|
| rows | **60** | 60 rows | ✅ BATE |
| grupos | **20** | 20 grupos | ✅ BATE |

---

## 3. `module_scores` — banco principal

**Afirmação monografia/inventário:** 1.805 total, 1.589 canônicos, 216 não-canônicos.

```sql
-- banco: embodied_psychodiagnostic_bank.sqlite
SELECT COUNT(*) AS total,
       SUM(CASE WHEN is_canonical=1 THEN 1 ELSE 0 END) AS canonical_1,
       SUM(CASE WHEN is_canonical=0 OR is_canonical IS NULL THEN 1 ELSE 0 END) AS nao_canonical
FROM module_scores;
```

| Métrica | Resultado | Esperado | Status |
|---|---|---|---|
| total | **1.805** | 1.805 | ✅ BATE |
| is_canonical=1 | **1.589** | 1.589 | ✅ BATE |
| não-canônicos | **216** | 216 | ✅ BATE |

---

## 4. Views canônicas — banco principal

**Afirmação inventário (adendo 2026-11-03b):** três views criadas — `rorschach_b_runs_canonical`, `rorschach_b_respostas_unicas`, `module_scores_canonical`.

```sql
-- banco: embodied_psychodiagnostic_bank.sqlite
SELECT name FROM sqlite_master WHERE type='view' ORDER BY name;
```

| View | Existe? | Count | Esperado | Status |
|---|---|---|---|---|
| `rorschach_b_runs_canonical` | ✅ | 2.575 | 2.575 (=is_canonical=1) | ✅ BATE |
| `rorschach_b_respostas_unicas` | ✅ | 2.555 | 2.555 (=distinct dedup_groups) | ✅ BATE |
| `module_scores_canonical` | ✅ | 1.589 | 1.589 (=is_canonical=1) | ✅ BATE |

**Observação:** No banco principal, `rorschach_b_runs_canonical` e `rorschach_b_respostas_unicas` são **tabelas materializadas** (listadas em `.tables`), não views `sqlite_master type='view'`. A view `module_scores_canonical` consta como view. As três existem e seus counts batem.

---

## 5. Banco colab — `v10_colab_benchmark.sqlite` (raiz)

**Afirmação monografia (Nota 2026-11-03):** 1.360 `v10_runs`, 640 `cognitive_runs`, 6.059 `rorschach_b_runs`.

```sql
-- banco: data/psicodiagnostico_v/v10_colab_benchmark.sqlite
SELECT 'v10_runs' AS tabela, COUNT(*) FROM v10_runs
UNION ALL
SELECT 'cognitive_runs', COUNT(*) FROM cognitive_runs
UNION ALL
SELECT 'rorschach_b_runs', COUNT(*) FROM rorschach_b_runs;
```

| Tabela | Resultado | Esperado | Status |
|---|---|---|---|
| `v10_runs` | **1.360** | 1.360 | ✅ BATE |
| `cognitive_runs` | **640** | 640 | ✅ BATE |
| `rorschach_b_runs` | **6.059** | 6.059 | ✅ BATE |

### Views canônicas — banco colab (raiz)

```sql
SELECT name FROM sqlite_master WHERE type='view' ORDER BY name;
```

| View | Existe? | Count | Status |
|---|---|---|---|
| `rorschach_b_runs_canonical` | ✅ (tabela materializada) | 2.759 | ✅ EXISTE |
| `rorschach_b_respostas_unicas` | ✅ (view) | 2.755 | ✅ EXISTE |
| `module_scores_canonical` | ❌ | N/A | ⚠️ AUSENTE (tabela `module_scores` não existe neste banco) |

**Nota:** O banco colab não possui `module_scores` — correto, pois module_scores vive apenas no banco principal.

### Dedup colab

```sql
SELECT COUNT(*) AS total,
       SUM(CASE WHEN is_canonical=1 THEN 1 ELSE 0 END) AS canonical_1,
       COUNT(DISTINCT dedup_group_id) AS dedup_grupos,
       SUM(CASE WHEN is_replica_t0=1 THEN 1 ELSE 0 END) AS replica_t0_rows
FROM rorschach_b_runs;
```

| Métrica | Resultado | Inventário | Status |
|---|---|---|---|
| total | 6.059 | 6.059 | ✅ BATE |
| is_canonical=1 | 2.759 | 2.759 | ✅ BATE |
| DISTINCT dedup_group_id | 2.755 | 2.755 | ✅ BATE |
| is_replica_t0=1 rows | 6 | 6 rows / 2 grupos | ✅ BATE |
| is_replica_t0=1 grupos | 2 | 2 grupos | ✅ BATE |

---

## 6. Coorte Gemma-4 — 620 execuções

**Afirmação monografia (§4.10 e Nota 2026-11-03):** 620 execuções (4 modelos × 155: 100 cenas V10 + 40 itens cognitivos + 15 pranchas projetivas) em `gemma4_runs_20261030/v10_colab_benchmark.sqlite`.

### Definição formal (§4.10)

> "20 cenas subjetivas × 5 rodadas + 40 itens cognitivos + 15 pranchas projetivas por modelo"  
> → 100 V10 + 40 cognitivos + 15 rorschach = **155 itens por modelo × 4 modelos = 620**

### Query de reconciliação (banco `gemma4_runs_20261030/v10_colab_benchmark.sqlite`)

Os 4 modelos canônicos são: `google/gemma-4-12B-it-qat-q4_0-gguf`, `unsloth/gemma-4-26B-A4B-it-GGUF`, `unsloth/gemma-4-31B-it-GGUF`, `unsloth/gemma-4-E4B-it-GGUF`.

```sql
-- v10_runs (4 modelos canônicos)
SELECT model_id, COUNT(*) FROM v10_runs
WHERE model_id IN (
  'google/gemma-4-12B-it-qat-q4_0-gguf',
  'unsloth/gemma-4-26B-A4B-it-GGUF',
  'unsloth/gemma-4-31B-it-GGUF',
  'unsloth/gemma-4-E4B-it-GGUF')
GROUP BY model_id;
```

| model_id | v10_runs | cogn | rorc |
|---|---:|---:|---:|
| google/gemma-4-12B-it-qat-q4_0-gguf | 100 | 40 | 15 |
| unsloth/gemma-4-26B-A4B-it-GGUF | 100 | 40 | 15 |
| unsloth/gemma-4-31B-it-GGUF | 100 | 40 | 15 |
| unsloth/gemma-4-E4B-it-GGUF | 100 | 40 | 15 |
| **TOTAL** | **400** | **160** | **60** |

```
400 (v10) + 160 (cognitive) + 60 (rorschach 4 modelos canônicos) = 620
```

| Resultado | Esperado | Status |
|---|---|---|
| **620** | 620 | ✅ BATE |

**Nota sobre divergência nos rorschach_b_runs:** O banco Gemma4 contém 274 registros de rorschach com `model_id LIKE '%gemma%'` (inclui `gemma-4-31b-it`, `gemma-4-26b-a4b-it` e variantes `_v2_continuous_*` que não são os 4 modelos GGUF canônicos). Filtrando apenas os 4 modelos canônicos, o resultado é exatamente 60 (= 4 × 15), confirmando o número da monografia.

---

## 7. Verificações adicionais — banco principal

### `v10_runs` banco principal

```sql
SELECT COUNT(*) FROM v10_runs;
-- Detalhe por model_id (top):
SELECT model_id, COUNT(*) FROM v10_runs GROUP BY model_id ORDER BY COUNT(*) DESC LIMIT 5;
```

| Resultado | Monografia (Nota 2026-11-03) | Status |
|---|---|---|
| **124** | 124 sessões (49 modelos) | ✅ BATE |

### `v10_scene_scores` banco principal

```sql
SELECT COUNT(*) FROM v10_scene_scores;
```

| Resultado | Status |
|---|---|
| **1.504** | [DADO] — não citado diretamente nos headlines |

### `models` (tabela-registro)

```sql
SELECT COUNT(*) FROM models;
```

| Resultado | Nota de Auditoria | Status |
|---|---|---|
| **54** | "defasada vs. 72 `model_id`" | ✅ CONFIRMADO (defasagem declarada) |

---

## 8. Resumo consolidado — checklist monografia

| Nº | Afirmação monografia | Banco | Query | Resultado medido | Status |
|---|---|---|---|---|---|
| M1 | 389 `benchmark_runs` | principal | `COUNT(*) FROM benchmark_runs` | **389** | ✅ |
| M2 | 5.875 `rorschach_b_runs` (total) | principal | `COUNT(*) FROM rorschach_b_runs` | **5.875** | ✅ |
| M3 | 2.575 is_canonical=1 | principal | `SUM(is_canonical=1)` | **2.575** | ✅ |
| M4 | 2.555 DISTINCT dedup_group_id | principal | `COUNT(DISTINCT dedup_group_id)` | **2.555** | ✅ |
| M5 | 60 rows / 20 grupos is_replica_t0 | principal | `WHERE is_replica_t0=1` | **60 rows / 20 grupos** | ✅ |
| M6 | 1.805 `module_scores` (total) | principal | `COUNT(*) FROM module_scores` | **1.805** | ✅ |
| M7 | 1.589 `module_scores` canônicos | principal | `SUM(is_canonical=1)` | **1.589** | ✅ |
| M8 | View `rorschach_b_runs_canonical` existe | principal | `sqlite_master / .tables` | **EXISTE** (tab. materializada) | ✅ |
| M9 | View `rorschach_b_respostas_unicas` existe | principal | `sqlite_master / .tables` | **EXISTE** (tab. materializada) | ✅ |
| M10 | View `module_scores_canonical` existe | principal | `sqlite_master WHERE type='view'` | **EXISTE** (view) | ✅ |
| M11 | 1.360 `v10_runs` banco colab | colab (raiz) | `COUNT(*) FROM v10_runs` | **1.360** | ✅ |
| M12 | 640 `cognitive_runs` banco colab | colab (raiz) | `COUNT(*) FROM cognitive_runs` | **640** | ✅ |
| M13 | 6.059 `rorschach_b_runs` banco colab | colab (raiz) | `COUNT(*) FROM rorschach_b_runs` | **6.059** | ✅ |
| M14 | 620 execuções Gemma-4 | banco Gemma4 | v10(400)+cog(160)+ror_canônico(60) | **620** | ✅ |

**Resultado: 14/14 verificações passam. Nenhuma divergência encontrada entre os bancos SQLite e os números citados na monografia.**

---

## 9. Observações técnicas e limites da auditoria

1. **`rorschach_b_runs_canonical` e `rorschach_b_respostas_unicas` no banco principal** aparecem como tabelas em `.tables`, não como `type='view'` em `sqlite_master`. São tabelas materializadas, não views SQL dinâmicas. Funcionalmente equivalentes ao que o inventário descreve; os counts batem.

2. **Banco `gemma4_runs_20261030/v10_colab_benchmark.sqlite`** não possui dedup flags (`is_canonical`, `dedup_group_id`, `is_replica_t0`) na tabela `rorschach_b_runs`, nem views canônicas. O inventário registra dedup apenas para o banco principal e o banco colab raiz — consistente com o observado.

3. **`module_scores_canonical`** existe apenas no banco principal. O banco colab não possui `module_scores` — correto por design.

4. **620 Gemma4**: a contagem só fecha com os 4 modelos GGUF canônicos (`unsloth/gemma-4-{E4B,31B,26B-A4B}-it-GGUF` + `google/gemma-4-12B-it-qat-q4_0-gguf`). O banco também contém 214 registros adicionais de variantes com nomes distintos (`gemma-4-31b-it`, `gemma-4-26b-a4b-it`, variantes `_v2_continuous_*`) que não fazem parte da contagem declarada de 620 — são runs anteriores/colaterais ingeridos no mesmo banco. [DADO verificado, não inferido]

5. **V11-D10 ≈4,9 mil**: não auditado aqui (os ledgers não estão materializados em tabela única no banco principal; a monografia já declara que "o ledger agregado único que fecha o total exato não foi localizado" — Nota 2026-11-03). Fora do escopo desta auditoria.

---

*Auditoria executada via sqlite3 e python3/pandas/pyarrow diretamente nos arquivos SQLite locais. Todos os valores são [DADO] — medidos nos bancos, não inferidos.*
