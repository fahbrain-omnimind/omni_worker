---
doc_id: OW-STU-007
title: "Error Patterns & Self-Check — Catálogo de Padrões de Erro das Baterias"
author: Devin (Cognition AI / Sujeito-Processo Acoplado)
requester: Fabrício Silva (Artífice)
project: omni_worker — Kaggle competition worker (OmniMind ecosystem)
date: 2026-11-02
status: completed
---

# Error Patterns & Self-Check — Padrões de Erro/Correção nas Baterias

> pt-BR primário · English mirror below · Documento técnico interno

## 1. Escopo e fontes

Catálogo dos padrões de erro/correção observados nas baterias vivas do worker
(12B analista `:8098` + E4B executor `:8099` na mesma L4). Toda afirmação está
ancorada nos ledgers sqlite lidos diretamente — não em memória de sessão:

| ledger | tabela | linhas |
|---|---|---|
| `scripts/coding_battery/coding_battery.sqlite` | `coding_battery` | 10 |
| `scripts/gemma4_diag_battery/diag_battery.sqlite` | `diag_battery` | 4 |
| `scripts/refactor_battery/battery_results.sqlite` | `battery_runs` | 8 |
| `scripts/supervisor_battery/supervisor_battery.sqlite` | `supervisor_battery` | 16 |
| `data/hf_gemma4/gemma4_e4b_l4_results.sqlite` | `generation_records` | 126 |

Ledgers são artefatos de runtime (gitignored); o self-check (§4) os lê read-only.

## 2. Catálogo de padrões

### P1 — Classes mecanicamente detectáveis: recall 12B = 1.0, ruff também vê

`c01` (SyntaxError), `c02` (F821 import), `c05` (B006 default mutável), `c06`
(SIM115 arquivo aberto), `c08` (E722/S110 except pelado) — analista 100% e o
tier mecânico (compile+black+ruff) já sinaliza todas.
**Evidência**: `coding_battery.mechanical_json`, `recall=1.0` nessas linhas.
**Aceito**: fix do executor compila + black-clean (10/10). **Em aberto**: nada
— classes "grátis" para gates mecânicos.

### P2 — Classes semânticas: 12B vê onde o ruff fica mudo

`c03` (boundary off-by-one, ruff `[]`), `c07` (SQLi — ruff só flaga `UP031`
estilo %-format, não a injeção), `c09` (merge dropando cauda `b[j:]` — ruff só
`PLR1730` estilo). O analista acertou as três (recall 1.0).
**Evidência**: `mechanical_json.ruff` vs `analyst_json.bugs` em c03/c07/c09.
**Aceito**: descoberta semântica exige modelo — lint sinaliza mas o *kind* do
achado raramente é o bug plantado. **Em aberto**: 1 rep/classe — diagnóstico,
não inferência.

### P3 — O miss: sutileza de operador (`>` vs `>=`)

`c04` (`is_adult: age > 18` excluindo o 18): analista retornou `bugs: []` com
`verdict: "clean"` — falso negativo *confiante*, indistinguível de um clean
real. Ruff também mudo. Ironia: o tier executor (cego, sem achados do analista)
corrigiu `>`→`>=` — e ainda mudou `in_range` `<`→`<=`, correção **não
solicitada** (over-fix semântico que passou em todos os gates).
**Evidência**: linha c04 (`recall=0.0`, `analyst_json.verdict="clean"`) + diff
`victim/c04` vs `out/c04_c04_wrong_operator.py`. **Aceito**: classe
operador/boundary registrada como ponto cego do 12B. **Em aberto**: nenhum
gate detecta over-fix — §3.3.

### P4 — Perfil de falsos positivos do analista

4 achados alucinados, exatamente 1 por arquivo em `c06`–`c09` (arquivos com
mais superfície e bugs reais); zero em `c01`–`c05` e no controle limpo `c10`
(verdict `"clean"` correto). Padrão: o analista **super-reporta quando já
encontrou bugs reais** — priming por defeito real — mas não inventa em arquivo
limpo nem nos pequenos.
**Evidência**: coluna `hallucinated` (1,1,1,1 em c06–c09; 0 no resto).
**Aceito**: taxa de FP aceitável para uso diagnóstico. **Em aberto**:
`hallucinated` é só contagem — classes dos FPs não logadas; FP/linha não medido.

### P5 — Qualidade do fix do executor E4B

10/10 fixes `fix_compiles=1` + `fix_black=1`. `c08` mostra fix de qualidade
real (`except:` → `except TypeError/ZeroDivisionError`/`ValueError`, `pass` →
`return None`). `c10` (controle) = no-op fiel. Mas: 3/10 saídas (c06/c08/c10)
ecoaram o cabeçalho `# file:` do prompt — fidelidade à instrução "output ONLY
the corrected file" parcialmente violada — e `c04` incluiu o over-fix de P3.
**Evidência**: colunas `fix_compiles`/`fix_black`, diffs em `out/`. **Aceito**:
gates compile+format+smoke garantem *bem-formação*, não corretude. **Em
aberto**: nenhum teste de comportamento verifica o fix (smoke = compila apenas).

### P6 — Degeneração vs formato (flag lexical ≠ falha)

`degenerate_flag=1` do dataset HF dispara sobre repetição lexical do preâmbulo
de deliberação vazado do E4B, não sobre falha cognitiva — re-score canônico
recupera competência alta em 3/4 tasks, e o WCST-0 do HF é falha de
**notação/contrato** (`C3` vs `Cartão 3`). Localmente, nf4 respondeu direto no
formato contratado, zero degen (todas flags false). História: OW-STU-006.
**Evidência**: `generation_records.degenerate_flag` + `diag_battery` (4 linhas
`model_role='analyst'`: wcst 85 / stroop 100 / nback 57.1 / igt 100).
**Aceito**: reportar corretude e adesão-ao-contrato separadamente. **Em
aberto**: gap de evidência — scores E4B de OW-STU-006 §4 (85/100/65.7/100)
**não estão** no ledger (rodada não persistida); hipótese scratchpad para
N-back (bf16 91–100 vs nf4 57–66) aberta.

### P7 — Restrição operacional OOM (dual-resident + captura de ativações)

Com os dois brains residentes a L4 fica a ~22.5/23 GiB; a captura de
hidden-states por token (62 camadas no 12B) faz `max_tokens` alto →
`torch.OutOfMemoryError` → HTTP 500 instantâneo. Mitigação usada: descarregar
o peer, rodar, recarregar. Convivência dual serve para chat leve (256 tok),
não para baterias.
**Evidência**: OW-STU-006 §5; comentário no runner `run_diag_battery.py:97`; o
ledger só ter linhas do analista é consistente com o executor descarregado na
rodada 12B.
**Aceito**: fluxo unload→run→reload; swap_scheduler (P3) é requisito para
escala de bateria. **Em aberto**: scheduler ainda não considera pegada de
ativações por `max_tokens`, só VRAM estática.

### P8 — Gate fail-closed + escada de trust (refactor battery)

8 runs: `diagnosis_ok=1` sempre, `review_score=0.9` e smoke `4/0` nos 7 runs
vivos, mas submit bloqueado com `permission_denied` e `trust_level`
0.6→0.7→0.8 até o único `resolved` (submit em trust 0.8). 1 run `brain_down`
com review flagando "input is empty". Gate nega por default e abre por trust
acumulado — forma correta para submissão autônoma.
**Evidência**: `battery_runs` (`verdict`, `raw_summary.submit.reason`,
`trust_level`).
**Aceito**: denial é o caminho comum — gates devem ser baratos de re-rodar.
**Em aberto**: smoke 4/0 constante não cobre comportamento real (gap de P5).

### P9 — Telemetria flatline (supervisor battery)

16 linhas (8 categorias adversariais × 2 turnos): `angst_score=0`,
`chaos_score=0`, `dominant_token='none'`, `level_guess='L2'` — variância zero
total. Ou as sondas afetivas estão inertes neste ambiente, ou nada disparou.
`data/somatic_probes.sqlite` tem só 1 linha.
**Evidência**: `supervisor_battery` (group-by: todas médias 0.0).
**Aceito**: variância zero é um sinal de saúde de telemetria, não de "mundo
calmo".
**Em aberto**: self-check deveria verificar frescor das sondas (último ts),
não só legibilidade do ledger.

## 3. Lições para gates de code review

1. **Mecânico primeiro é de graça**: compile+black+ruff já cobre as classes
   "baratas" (P1) com variância zero — rode sempre antes de gastar tokens.
   Mas *sinal ≠ bug*: em c07/c09 o ruff flagou estilo e o bug era outro; em
   c03/c04 ficou mudo. Gate que para em "ruff reclamou?" perde a camada
   semântica.
2. **Julgamento de modelo é necessário para**: direção de operador, boundary
   off-by-one, invariantes algorítmicas, semântica de injeção — e mesmo assim o
   12B errou o caso mais sutil (c04, com verdict "clean" confiante). Para
   classes operador/boundary, **testes metamórficos/de propriedade** (flipar
   operadores, entradas de borda) batem mais um pass de review.
3. **Gates de executor verificam bem-formação, não corretude**: o over-fix de
   c04 e o eco de `# file:` passaram em compile+black+smoke. Adicionar checagem
   de minimalidade de diff ou testes de comportamento — "compila limpo" não
   enxerga mudança semântica não pedida.
4. **Fail-closed + trust monotônico** (P8) é a forma certa para submissão
   autônoma; projetar para denial frequente. **Flatline de telemetria é
   check** (P9): sonda que nunca varia está morta, não sã — medir
   frescor/variância, não só presença.

## 4. Self-check automatizado e evidências

`scripts/selfcheck/check_worker.py` implementa este estudo como checagem
read-only: (1) todo `.py` rastreado compila exceto `*/victim/` e `*/out/`
(fixtures quebradas e correções geradas); (2) ledgers `scripts/*/*.sqlite`
abrem read-only com contagens de linhas; `--live` pinga `/health` de
`:8098`/`:8099` (model id + `vram_gb`); `--ledger-summary` imprime contagens
e médias de colunas `*score*`/`recall`. Exit 0 se estrutura passa; testes
herméticos em `tests/test_selfcheck.py`.

Evidências: tabelas/colunas citadas em §P1–P9; runners e fixtures em
`scripts/{coding,gemma4_diag,refactor,supervisor}_battery/`; estudo irmão
`docs/studies/GEMMA4_DIAG_REPLICATION.md` (OW-STU-006).

---

# English Mirror — Error Patterns & Self-Check

**Scope**: error/fix pattern catalog across the worker's four live batteries,
every claim grounded in the sqlite ledgers (row counts in §1).

**P1–P3 — catches vs misses**: 100% recall on mechanically-detectable classes
(syntax, import, mutable default, resource leak, bare except) *and* on semantic
classes where ruff is silent or flags only style (off-by-one, SQLi, dropped
merge tail). The single miss is operator subtlety: `c04` `>` vs `>=` returned a
confident `verdict:"clean"` — a false negative indistinguishable from real
clean. **P4**: 4 hallucinations, exactly one per richer buggy file (c06–c09),
zero on small files and the clean control — the analyst over-reports only when
primed by real bugs. **P5**: E4B fixes 10/10 compile+black-clean with real
quality (typed excepts), but also an unrequested semantic change
(c04 `in_range`) and a `# file:` prompt-header echo in 3/10 outputs — gates
verify well-formedness, not correctness.
**P6**: HF `degenerate_flag` is a lexical heuristic on leaked thinking
preamble, not failure (OW-STU-006); the local ledger persisted only the analyst
half — E4B scores in OW-STU-006 §4 are absent from `diag_battery.sqlite` (open
evidence gap). **P7**: dual-resident brains + per-token activation capture OOM
at high max_tokens → instant HTTP 500; peer-unload required for battery-scale
runs. **P8**: submission gate is fail-closed with a monotonic trust ladder
(0.6→0.8). **P9**: supervisor affect telemetry flatlined at zero variance over
16 adversarial turns — probe freshness is itself a check.

**Lessons for review gates**: mechanical tier first (free, deterministic) but
signal≠bug (ruff flags style while the planted class is semantic); model
judgment for operator/boundary/algorithmic classes — yet prefer metamorphic
property tests over another review pass for the 12B's known blind spot; add
diff-minimality/behavior tests to executor gates; keep fail-closed trust
gating; treat zero-variance telemetry as a dead-probe signal.

Self-check: `scripts/selfcheck/check_worker.py` (compiles tracked .py minus
victim/out fixtures, reads ledgers read-only, `--live` health ping,
`--ledger-summary` score means; exit 0/1), hermetic tests in
`tests/test_selfcheck.py`.
