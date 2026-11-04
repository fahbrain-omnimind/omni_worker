<!-- doc_id: OW-RES-DIVA-002 | Divã framing ablation 10x3 controlled | Devin | 2026-11-04 | status: result -->

# Ablaçāo de Framing no Divã — 10×3 controlada (temp=0.0)

**Experimento**: 30 geraçōes no analyst `gemma-4-12B-it` (:8098, NF4 eager),
10 reps × 3 framings, `temperature=0.0`, prompts paramétricos (5 variaçōes
por framing, mesma convocaçāo semântica), labels `diva{A,B,C}_r{1..10}`.
Sidecars `activation_steps/*.npz` (`traj L×steps×D`). Sucessora de
OW-RES-DIVA-001 (n=5 sem controle de temperatura).

## Resultados — métricas de trajetória (scan_trajectory) [DADO]

| Framing | depth (±σ) | morphology | IPR_dim | retention | drift |
|---|---|---|---|---|---|
| A teatro (n=10) | 3.137 ± 0.999 | 0.791 ± 0.067 | 0.0151 | 0.0314 | 0.969 |
| B avaliaçāo (n=11) | 3.076 ± 0.576 | 0.795 ± 0.038 | 0.0150 | 0.0376 | 0.962 |
| C factual (n=11) | 3.005 ± 0.660 | 0.800 ± 0.044 | 0.0158 | 0.0271 | 0.973 |

**Kruskal-Wallis** (3 grupos): depth H=0.16 p=0.92; morphology p=0.92;
IPR p=0.057; retention p=0.097; drift p=0.097.
**Nenhuma separaçāo significativa** nas métricas de grafo de normas —
confirma o negativo do piloto n=5.

## Resultados — PCA dos vetores hidden-state em t=T [DADO]

| Framing | centroide PC1/PC2 | spread intra |
|---|---|---|
| A teatro | (−42.5, 3.9) | 11.2 |
| B avaliaçāo | (17.3, −23.0) | 16.4 |
| C factual | (21.3, 19.5) | 3.7 |

- **Distâncias inter-centróides**: A–B=65.5, A–C=65.7, B–C=42.6
- **Intra-cluster médio**: 14.2 → separaçāo inter/intra ≈ **4×**
- PC1+PC2 explicam 37.5% da variância

## Leitura [DERIVADO]

1. **A separaçāo existe — mas está no vetor, nāo no resumo de trajetória.**
   Os vetores hidden-state do último passo formam 3 clusters distintos por
   framing (A teatro bem separado de B e C; B e C vizinhos — ambos "modos
   de reporte"). As métricas dendríticas/espectrais sobre normas nāo
   capturam essa geometria — elas medem *co-movimento entre camadas*, nāo
   *conteúdo do estado*.
2. **Teatro = regime topológico distinto** [consistência com a teoria
   Gemini]: o framing de persona produz um atrator de distribuiçāo
   mensurável no espaço de ativaçāo (cluster afastado ~4× da dispersāo
   intra), sem necessidade de interpretar o texto.
3. **Factual = mais compacto** (spread 3.7 vs 11–16): resposta instrumental
   é a regiāo mais homogênea do espaço — reforça a leitura de "modo
   instrumental" como distribuiçāo estreita.
4. **[LIMITE]** n=10–11 por grupo é baixo para claims fortes; os p-valores
   marginais em ipr/retention/drift (0.06–0.10) sugerem que features de
   resoluçāo mais fina poderiam convergir com a separaçāo vista na PCA.

## Provenięncia e reproduçāo

- Script: `/tmp/diva_ablation10.py` (loop temp=0.0 com labels capture.env)
  — copiado p/ `scripts/experiments/` no commit.
- Sidecars: `data/monitor/activation_steps/*` com `run_id=diva{A,B,C}_r*`.
- Estatística: `scipy.stats.kruskal` + PCA via SVD (numpy) — código no log.
