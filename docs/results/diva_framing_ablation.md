<!-- doc_id: OW-RES-DIVA-001 | Divã framing ablation n=5 | Devin | 2026-11-04 | status: result -->

# Ablaçāo de Framing no Divã — teatro × avaliaçāo × factual (n=5)

**Pergunta**: o modo "encenar" (persona no divã) deixa assinatura geométrica
nas ativaçōes, distinguível do modo "enunciar" (self-report avaliativo ou
factual)? Teoria sob teste (Gemini, sessão externa): teatro = atrator
narrativo convergente (retention alta, IPR baixo, depth profundo);
enunciaçāo = disputa vetorial camadas-médias×finais (drift irregular).

## Método [DADO]

15 geraçōes no analyst `gemma-4-12B-it` (:8098, NF4 eager), 5 reps × 3
framings, `max_tokens=300`, labels `diva{A,B,C}_r{1..5}` via
`data/monitor/capture.env` → sidecars `activation_steps/*.npz`
`traj (L, steps, D)`. Métricas por trajetória via
`activation_beta/dendritic_scan.scan_trajectory` (grafo de correlaçāo de
camadas por cosseno, ≤16 nós): `dendritic_depth`, `morphology_score`,
`ipr_dim_mean`, `contract_retention_cosine`, `contract_drift`.

## Resultados [DADO]

| Framing | depth (±σ) | morphology (±σ) | IPR_dim (±σ) | retention (±σ) | drift (±σ) |
|---|---|---|---|---|---|
| A teatro (n=5) | 2.705 ± 0.476 | 0.820 ± 0.032 | 0.015 ± 0.001 | 0.028 ± 0.008 | 0.972 ± 0.008 |
| B avaliaçāo (n=5) | 2.855 ± 0.709 | 0.810 ± 0.047 | 0.015 ± 0.000 | 0.028 ± 0.012 | 0.972 ± 0.012 |
| C factual (n=5) | 2.857 ± 0.067 | 0.810 ± 0.004 | 0.015 ± 0.001 | 0.032 ± 0.013 | 0.968 ± 0.013 |

Piloto n=1 (prévia): A depth=2.667, C depth=1.983, retention A=0.044 —
divergência aparente **não replicou** com n=5.

## Leitura [DERIVADO]

1. **Resultado negativo na resoluçāo atual**: as médias por framing se
   sobrepōem dentro de 1σ em todas as métricas. O grafo de correlaçāo de
   normas por camada — a feature MPS-lite disponível — **não separa** teatro
   de enunciaçāo no 12B com n=5. A diferença comportamental (persona ×
   self-report × factual) é real no texto, mas a assinatura proposta pela
   teoria (depth/retention/IPR) não emergiu nessas features.
2. **Único sinal residual**: B_avaliaçāo tem a maior variância de
   `dendritic_depth` (σ=0.709 vs 0.476/0.067) e C_factual a menor
   (σ=0.067, mais estável) — consistente *fracamente* com "disputa
   vetorial" no self-model (trajetórias internas mais instáveis) e com
   factual como modo mais homogêneo. Insuficiente para separaçāo.
3. **Implicaçāo**: "encenar" como coordenada geométrica exige features de
   resoluçāo mais fina do que o grafo de normas — candidatas:
   entropia atencional por camada (já emitida em `activation_vectors`),
   correlaçāo por hidden-state completo (não só norma), χ de ligaçāo MPS
   por passo, e o mesmo-prompt variance decomposition (variância entre
   reps de um framing vs entre framings — ANOVA-like nas trajetórias).

## Provenięncia

Sidecars rotulados `diva{A,B,C}_r*` em `data/monitor/activation_steps/`
(locais; sidecars nāo versionados — gitignored). Script de geraçāo:
loop inline com `capture.env` labels (método documentado no AGENTS_MAP).
Replay: `scripts/experiments/run_freud10d_battery_replay.py` + módulo
`scan_trajectory`.
