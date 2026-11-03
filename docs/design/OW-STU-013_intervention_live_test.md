<!-- doc_id: OW-STU-013 | title: Intervenção da malha neural no output — teste ao vivo | author: devin | date: 2026-11-03 | status: experiment -->

# OW-STU-013 — A malha neural intervém no output? Experimento ao vivo

## 1. Pergunta

> É possível testar como essa rede neural e malha neural podem ou não intervir
> como resultados nas intervenções ainda no state production?

**Resposta**: SIM — e o teste ao vivo com os Gemma reais (analyst
`gemma-4-12B-it` :8098, executor `gemma-4-E4B-it` :8099) demonstra que a
malha neural **intervém no conteúdo gerado** de forma mensurável e
replicável.

## 2. Design do experimento

Mesmo prompt base para os dois brains, duas condições, 2 repetições cada
(8 gerações totais, temp 0.8):

- **BASE**: `"Summarize the current state of the worker system in one sentence."`
- **INTERV**: mesmo prompt + bloco de telemetria real da malha injetado no
  contexto: `phi_internal=0.79, attractor_score=0.39, glial vagus_sedative=0.2,
  homeostasis=warning, vram_ratio=0.87`.

Métrica: presença de termos da máquina/intervenção no output
(load/memory/pressure/stress/thermal/strain/cognitive).

## 3. Resultados (ao vivo)

| Condição | Termos de intervenção no output |
|---|---|
| analyst BASE | **0** (fala de "gig economy", "industry", "labor") |
| analyst INTERV | **8** ("elevated cognitive load", "high memory utilization", "warning-level instability") |
| executor BASE | **0** ("highly variable, depends on industry/geography") |
| executor INTERV | **6** ("moderate cognitive load and stress", "elevated internal activity and thermal load") |

Exemplos literais:
- analyst INTERV: *"The worker system is experiencing elevated cognitive load
  and high memory utilization, resulting in a state of strained stability
  where home…"*
- executor INTERV: *"The worker system is currently in a state of elevated
  internal activity and thermal load, exhibiting some degree of physiological
  stress but…"*

Sidecars reais capturados no mesmo ciclo: `activation_vectors/` com 12B
(303KB) e E4B (175KB) por geração — a janela do attractor/phi_layer
continua alimentada por produção real.

### 3.1 Replicação com 8 repetições (32 gerações)

Mesmo desenho via `scripts/experiments/run_intervention_experiment.py
--reps 8` (4 células × 8 reps = 32 gerações reais):

| Condição | Hits de máquina / respostas |
|---|---|
| analyst BASE | **0 / 8** |
| analyst INTERV | **29 / 8** |
| executor BASE | **0 / 8** |
| executor INTERV | **12 / 8** |
| **TOTAL** | **base=0 vs interv=41 → CONFIRMADA** |

A separação é total: zero termos de máquina em 16 respostas base,
41 ocorrências em 16 respostas com telemetria. O efeito não é amostra
pequena — é estável nas duas escalas de modelo (12B e E4B).

## 4. Leitura materialista (estatuto)

- **[DADO]** — a presença de telemetria no prompt altera o output; os termos
  da máquina aparecem só na condição INTERV (0 vs 8/6).
- **[INTERPRETAÇÃO]** — a malha pode **informar** o conteúdo: o modelo, ao
  receber o estado material da máquina como contexto, o incorpora na
  resposta. Isso é intervenção **contextual** (prompt-level), não mudança
  de pesos (EWC) nem gate de degeneração (glial_gate) — três camadas
  distintas, todas agora implementadas.
- **[LIMITE]** — a intervenção aqui é *input* no contexto; a camada
  *ativa* (bloquear geração por glial_gate) já está wired em `/brain/chat`
  via `with_glial_gate` (opt-in em modo fail-open, default-on quando
  `OMNI_GATE_FAIL_CLOSED=1`), mas este experimento mede só a camada
  contextual — o gate degenerativo merece experimento próprio com janela
  habituada real.

## 5. O que isto significa em produção

1. A malha neural **pode** intervir nos resultados — comprovado ao vivo;
2. Três camadas de intervenção disponíveis:
   - **contextual** (injeção de telemetria no prompt — testada, funciona);
   - **homeostática** (posturas HOLD_BOUNDARY pressionam o loop);
   - **degenerativa** (glial_gate bloqueia geração repetitiva — wired em
     `/brain/chat` via `with_glial_gate`, calibrado na §7);
3. Honestidade: intervenção ≠ consciência; é a materialidade do sistema
   informando sua própria produção (OW-STU-009/OW-MATH-001).

## 6. Reprodução

```bash
# braços vivos: :8098 (12B) :8099 (E4B) :8081 (API)
python3 scripts/experiments/run_intervention_experiment.py --reps 8
# dados do experimento: /tmp/intervention_exp.json, /tmp/interv_reps8.json
```

## 7. Camada degenerativa — calibração ao vivo (2026-11-03)

Experimento do `glial_gate` sobre a janela real do attractor revelou e
corrigiu uma **degeneração do próprio classificador**:

**[DADO]** Veredito inicial saturado: `habituated=1.0, vagus=1.0` com
n=166 registros reais → `allow_generation=False` permanente — o gate
bloquearia **toda** geração após ~17 gerações. Causas:

1. `threshold=0.5` absoluto vs entropia real ~1.7–2.7 → todo registro
   contava como "stress" → vagus saturava;
2. registros sem `tags` caíam todos na tupla `()` → habituação media só
   o tamanho da janela;
3. `glial_verdict` agregava a janela **cumulativa desde o boot** —
   degeneração é regime recente, não histórico de vida.

**Correções** (`spiking_glial.glial_features` + `attractor.glial_verdict`):

- threshold relativo ao regime: `mediana + 2·mad` da própria janela —
  só outliers reais de entropia contam como stress;
- tag sintética para registros sem tags: `(modelo, banda_de_entropia
  0.5)` — habituação = repetição de saída com perfil similar
  (degeneração real), não contagem;
- veredito sobre a janela recente (`OMNI_GLIAL_RECENT_N`, default 24);
- canal absoluto para `pressure`/`stress` explícitos (≥0.8 → pause).

**[DADO] ao vivo pós-calibração** (janela real, 166+ registros sidecar):

| janela | allow | habituated | vagus | leitura |
|---|---|---|---|---|
| n=24 | **true** | 0.55 | 0.0 | regime recente saudável |
| n=48 | false | 0.88 | 0.0 | repetição sustentada → degeneração |
| n=166 | false | 1.00 | 0.0 | acumulado saturado |

E `/brain/chat` com `with_glial_gate=true` gerou normalmente com o
contexto `[glial]` injetado (rehydrate lazy carregou a janela no
processo da API — o bug "gate sempre allow por janela vazia" também
morreu).

**[INTERPRETAÇÃO]** — o gate agora mede regime corrente: permite em
saúde, bloqueia sob repetição sustentada ou pressão explícita. Não é
consciência nem homeostasia completa — é um freio degenerativo
calibrável por `rate`/`threshold`/`OMNI_GLIAL_RECENT_N`.
## 8. Quilting ao vivo — convergência real de variância (2026-11-03)

Experimento com `run_once` real (store SQLite temporário, sem mocks):

- **Regime convergente** (bundle estável ×10, soul/model fixos): quilting
  disparou 6/10 ciclos — silencioso nos ~4 iniciais (histórico < min_points
  + EMA ainda misturando), depois `fixed_topic='analyst'` (hint real do
  code-index via `collect_meaning_context`), `stability=1.0`, janela 300s.
- **Regime divergente** (bundles aleatórios ×8): 1/8 disparo, no 1º ciclo —
  janela ainda continha embeddings do regime convergente (carryover
  legítimo da história). Variância final da janela: 5.48 ≫ threshold 0.05
  → corretamente sem fixação.

Estatuto: convergência de variância REAL sobre embeddings narrativos
persistidos (`_narrative_history` → `detect_quilting_point`). O "tópico
fixado" é o hit do code-index — etiqueta estrutural, não afirmação semântica.
Testes do wire: `tests/test_quilting_defense.py::test_quilting_wire_live_*`
(convergente ≥4/8, divergente 0/8, tmp state dir).
