<!-- doc_id: OW-STU-004 | title: Gemma-4 Battery Inventory — HF datasets + local | author: devin | requester: artifice-operator | project: omni-agent-coworker (kaggle) | date: 2026-11-03 | status: active -->

# Inventário de Baterias Gemma-4 — HF `gemma4-e4b-colab-l4-results` + local

pt-BR: O que já rodou na família Gemma-4 (fonte: dataset HF
`fabricioslv/gemma4-e4b-colab-l4-results` — sqlite de 124 execuções E4B/bf16
na L4 em 01-02/nov/2026, baixado para `data/hf_gemma4/`), o que podemos
repetir neste worker e o que ele cobre de novo (12B — ausente do dataset).
English: inventory of Gemma-4 batteries already run (HF E4B-L4 dataset),
what is repeatable in this worker, and the 12B gap it fills.

## 1. Dataset HF — estrutura (124 ledger rows, todas DONE)

| Experimento | Arm | N | Degenerate | tok/s | Gates |
|---|---|---|---|---|---|
| `block1_cognitivo` | observe_cognitive | 16 | **1.00 (100%)** | 9.8 | 0 |
| `block1_observe` | observe_free | 20 | 0.00 | 10.8 | 0 |
| `block1_pranchas` | observe_projective | 20 | 0.00 | 10.3 | 0 |
| `block1_v10` | observe_free | 20 | 0.00 | 10.2 | 0 |
| `block2_intervene` | arm_baseline | 12 | **0.75** | 10.2 | 0 |
| `block2_intervene` | arm_thought_floor | 12 | **0.75** | 10.2 | 0 |
| `block2_intervene` | arm_unified_cascade | 12 | **0.58** | 10.1 | 1 |
| `block2_intervene` | arm_verification_gate | 12 | **0.67** | 10.1 | 1 |
| canary | baseline | 2 | 0.00 | 10.3 | 0 |

- Tasks block2 = SWE reais do dataset Gluzdov (apiflask, django_channels,
  werkzeug, cookiecutter, mpmath…).
- `generation_records` (126): visible+thinking traces separados,
  `degenerate_flag`, `unique_ratio`, `n_gates_interventions`, finish_reason
  (eos 107 / length 17 / **gate_triggered 2**).
- `latent_layer_metrics` (1492): **por camada** — `pr_traj` (participation
  ratio), `svd_entropy_traj`, `mps_chi_eff`, `h_norm` → instrumentação real
  do "vacilo" (§4.2 do writeup) já em produção.
- Leitura: polo projetivo/livre não degenera no E4B-bf16; **executivo
  cognitivo degenera 100%; SWE degenera 58–75%** — cascade/gate foram os
  braços que mais reduziram (−17pp e −8pp vs baseline).

## 2. Baterias locais já rodadas neste worker (Gemma dual)

| Bateria | N | Ledger |
|---|---|---|
| `refactor_battery` Debug→Code→Review→gate | 8 runs (incl. arco trust 0.5→0.8→resolved) | `battery_results.sqlite` |
| `supervisor_battery` 8 categorias adversariais | 16 turnos, 16/16 | `supervisor_battery.sqlite` |
| `coding_battery` (nova) 10 classes de erro, 3 tiers | em execução | `coding_battery.sqlite` |

## 3. O que repetir aqui (e o que ele cobre de novo)

**Gap do dataset HF: só E4B/bf16.** Nosso diferencial: os mesmos braços no
**12B NF4** ao vivo (:8098) + comparação lado-a-lado na mesma L4:

1. **block1_cognitivo** — repetir no 12B e no E4B local: E4B degenerou 100%
   em HF; nosso tracer/supervisor pode registrar o modo de colapso
   (repetição? surrender?) com `latent_layer_metrics`-like via
   `/erika/activations` (65 camadas — mesmo substrato do `pr_traj`).
2. **block2 braços** (baseline/thought_floor/unified_cascade/
   verification_gate): nosso `safety/gate` + `affect_tracer` + swap
   scheduler são implementações de fábrica dos mesmos conceitos — rodar
   o subset de tasks Gluzdov (públicas) nos dois modelos mede se a
   arquitetura do worker reduz degeneração vs baseline.
3. **block1_pranchas**: projetivas não-codificação — candidato a bateria
   "open-ended" separada (alimenta o estudo afetivo, não coding).
4. **canary** (2 gen. baseline) — manter como smoke vivo no CI-live.

## 4. Protocolo formatação (black) — verificado

Modelos não "usam" black; o pipeline aplica como camada determinística:
gera→`black`→ast.parse→smoke. Já integrado ao `coding_battery` (colunas
`fix_black`, `fix_compiles`). black 26.10.1 + ruff 0.17.3 instalados no
python3 do worker.

## 5. Fontes

- HF dataset: `fabricioslv/gemma4-e4b-colab-l4-results` →
  `gemma4_e4b_l4_results.sqlite` (local `data/hf_gemma4/`, untracked).
- Writeup alvo: `/content/WRITEUP_ESQUELETO.md` (paper track, deadline
  2026-11-12; claims: ablação quantização, vacilo PR/χ, braços de
  intervenção — todos confirmáveis contra o sqlite).
- SWE tasks: dataset público Gluzdov v8 (288 runs referenciados no writeup).
