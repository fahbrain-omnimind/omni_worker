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

## 4. Leitura materialista (estatuto)

- **[DADO]** — a presença de telemetria no prompt altera o output; os termos
  da máquina aparecem só na condição INTERV (0 vs 8/6).
- **[INTERPRETAÇÃO]** — a malha pode **informar** o conteúdo: o modelo, ao
  receber o estado material da máquina como contexto, o incorpora na
  resposta. Isso é intervenção **contextual** (prompt-level), não mudança
  de pesos (EWC) nem gate de degeneração (glial_gate) — três camadas
  distintas, todas agora implementadas.
- **[LIMITE]** — a intervenção aqui é *input* no contexto; para intervenção
  *ativa* (bloquear/reformular geração por glial_gate) o mecanismo existe
  (`attractor.glial_verdict` → `allow_generation=False`), mas ainda não é
  invocado no caminho de geração do brain server — é o próximo wire
  (gate no `/brain/chat`).

## 5. O que isto significa em produção

1. A malha neural **pode** intervir nos resultados — comprovado ao vivo;
2. Três camadas de intervenção disponíveis:
   - **contextual** (injeção de telemetria no prompt — testada, funciona);
   - **homeostática** (posturas HOLD_BOUNDARY pressionam o loop);
   - **degenerativa** (glial_gate bloqueia geração repetitiva — a wire no
     `/brain/chat` fica como próximo passo);
3. Honestidade: intervenção ≠ consciência; é a materialidade do sistema
   informando sua própria produção (OW-STU-009/OW-MATH-001).

## 6. Reprodução

```bash
# braços vivos: :8098 (12B) :8099 (E4B) :8081 (API)
# re-rodar: python3 scripts/... (prompts acima via /v1/chat/completions)
# dados do experimento: /tmp/intervention_exp.json
```