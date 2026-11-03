# Refactor battery multi-arquivo/multi-turn — resultados live (2026-11-03)

**Status**: [DADO] — 2 reps reais, 3 turnos cada, executor E4B (`gemma-4-E4B-it`), Ledger `scripts/refactor_battery/battery_results.sqlite`.

## Veredito

| rep | verdict | files gerados | smoke | review (heurística) | turns | latency |
|---|---|---|---|---|---|---|
| 1 (`rb_1793714254_0`) | **broken_patch** | `models.py`, `store.py` | rc=1 (import error, 0.05s) | approved 0.9 | 3 | 408.6s |
| 2 (`rb_1793714897_0`) | **broken_patch** | `models.py`, `store.py` | rc=1 (import error, 0.05s) | approved 0.9 | 3 | 410.9s |

## Achado reprodutível

**O modelo gera apenas os módulos compartilhados e descarta os entry points.**

- O contrato exige: `todo_api.py` (handle_request) e `todo_stats.py` (stats/report_line) **preservados** + módulo compartilhado novo.
- 2/2 reps: o modelo produz só `models.py` + `store.py` — as APIs públicas somem → `test_todo_api.py` (que importa `todo_api`) falha em 0.05s.
- **Feedback multi-turn não corrige**: 3/3 turnos idênticos, mesma saída, mesmo smoke rc=1. O modelo repete o erro em modo local — não é ruído de amostragem, é padrão de comportamento com este spec (multi-arquivo: "split" é interpretado como "reescreva para só os novos módulos").
- O harness **não aceita**: break exige `smoke.passed>0 ∧ failed=0 ∧ approved` — a heurística aprova (0.9) mas o contrato segura. `verdict=broken_patch` honesto.
- `llm.review:false`: analista estava evictado (contenção de VRAM — ver abaixo) → review heurístico registrado com flag explícita.

## Correções de infraestrutura feitas no caminho

1. **Bug real — crash multi-turn**: a limpeza do out dir entre turnos fazia `name.unlink()` em `__pycache__/` (criado pelo pytest do turn 1) → `IsADirectoryError` matava o run no turn 2. Fix: `rmtree` para dirs (`run_battery.py`).
2. **OOM de co-residência (causa dos runs anteriores)**: analista 12B (10.2GB) + executor E4B (11.5GB) + embeddings (332MB) ≈ 22GB numa L4 de 23GB — cabe estático, **estoura durante geração** (dequant bitsandbytes precisa de scratch; 54MiB com 2.8MiB livres → OOM → `code:false`). O swap_scheduler existe exatamente para isso. Fix operacional: evictar o analista durante a bateria. **Dual residency = modo de repouso, não de geração.**
3. **`_ensure_executor`**: guard auto-curativo na bateria — se o scheduler evictar o executor entre turnos, recarrega e espera (`/erika/reload` + poll `/health`, padrão do `run_diag_reps_swapped.sh`).
4. **Runner ignora `REFACTOR_N` env** — é `--n` (argparse). Documentado aqui.

## Nota honesta

- 2 reps com o mesmo resultado = padrão, não anedota; mas N=2 é pequeno.
- O test contract não distingue "modelo perdeu os arquivos" de "extração perdeu" — `_extract_files` achou os mesmos 2 arquivos nas 2 reps; se o modelo tivesse emitido os entry points com outro header, teriam aparecido. A evidência do log do brain (saída crua) é necessária para fechar a distinção — pendente.
- Próximo natural: adicionar ao feedback do turn os **nomes obrigatórios dos arquivos** de forma explícita (o spec já os lista; o modelo ainda assim os pula — investigar se prompt-shaping resolve ou se é limite real do E4B).

## Rótulos

[DADO] resultados · [PRX] métricas de harness · nenhuma claim de consciência.