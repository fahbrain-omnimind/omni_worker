<!-- doc_id: OW-STU-009 | title: Ativações como β-elements — hidden-state stats → metabolização α (design study, CPU/RAM) | author: study-agent | requester: artifice-operator | project: omni-agent-coworker (kaggle) | date: 2026-11-02 | status: study -->

# OW-STU-009 — Ativações como β-elements (estudo de design, sem código de produção)

## 1. Orquestração runtime

- **Fonte de dados**: `data/monitor/erika_torch_activations.jsonl` (append-only, produzido por `server/erika_torch_server.py` a cada geração; schema: `prompt_tokens`, `gen_tokens`, `layers[]` com `norm` por camada, `attention_entropy_last`, `n_layers`). Tail incremental com offset persistido (`data/monitor/.offset`), já usado por DSN-001 collector.
- **Cadência**: análise em janelas deslizantes sobre o jsonl (default janela=64 gerações, step=16) executada pelo loop de integração (DSN-002, 30–120s) ou por gatilho de evento (`dream/*`, `agency/*`). Sem torch/GPU no caminho de análise.
- **Contrato de saída**: features de atrator + BetaElement → metabolização α via `integration_loop.bion_bridge.metabolize` → publicação no barramento (`mesh`, `dream`, `loop`) e persistência sqlite WAL.
- **Processo único** FastAPI `:8081`; sem daemon externo no P0. GPU permanece saturada pelo brain — análise é CPU/RAM only.

## 2. Perguntas arquiteturais respondidas

### Q1 — Ativações brutas podem ser β-elements?
**Sim**, sob enquadramento operacional. Os registros por geração (`hidden_states` stats, entropia de atenção, normas por layer) são material não-pensável no sentido Bion: experiência numérica bruta, pré-simbólica, com carga emocional derivável (drift de norma, colapso de entropia). O `BetaElement.raw_data` já é string digest (ver `bion_bridge._digest`); ativações viram um digest estruturado por geração/janela. A carga emocional (`emotional_charge`) mapeia para features de atrator normalizadas [0,1] (ver §3). Não é experiência fenomenal — é verbalização operacional do estado da máquina (mesma ressalva de `bion_bridge`).

### Q2 — "As camadas hidden retornarem sobre si" sem vs com torch
- **Sem torch (P0/P1, recomendado)**: sumários estatísticos e janelas sobre o jsonl. Derivar por camada: média/variância de `norm`, drift entre gerações consecutivas, entropia de atenção rolante, repetição de token (n-gram overlap entre prompts/gen), camada divergente (argmax de |norm_t - norm_{t-1}|). Tudo numpy/polars, O(N·L) CPU, sem modelo vivo. Retrieval = consulta sqlite/jsonl por janela temporal.
- **Com modelo vivo (P2, opcional)**: o brain consulta sua própria ativação passada via retrieval (RAG sobre `erika_torch_activations.jsonl` ou índice faiss). O modelo escolhe material a reter/modificar (self-training/planejamento) — mas isso exige torch no caminho do brain, não do daemon. Daemon continua só observação; o brain decide consumo. Risco: feedback loop pode amplificar degeneração → mitigar com gate de atrator (§3) e `negative_capability`.

### Q3 — Ponte proposta
```
activation_records (jsonl)
  → features de atrator (numpy, CPU):
      norm_drift[layer] = |norm_t - norm_{t-1}|
      entropy_collapse   = 1 - (H_t / H_baseline)  (clamped)
      token_repetition   = n-gram repeat ratio prompt↔gen
      divergent_layer    = argmax layer drift
      attractor_score    = weighted combo (weights config)
  → BetaElement(raw_data=digest, emotional_charge=attractor_score, source="activations.window")
  → bion_bridge.metabolize(ctx, arousal=attractor_score)
  → AlphaElement: alpha_content (narrativa simbólica), symbolic_potential
  → consumidores:
      dream_weaver/agency: meaning_score boost, topic_hint = divergent_layer
      narrative.life_story: append α como evento de "insight"
      modulação do loop: swap_threshold_delta, curiosity_boost
      futuro self-training: reter/modificar material com attractor_score alto (gated)
```

### Q4 — Onde a análise vive
- **P0**: novo módulo `activation_beta/` (Python puro, numpy) consumido pelo `integration_loop` (estágio opcional `activation_beta` após `sensory_input`) e pelo `kernel_daemon` (features). Não no daemon monolítico; não em `agency/dream` (esses consomem).
- **P1**: `activation_beta/` publica em tópicos `mesh`, `dream`, `loop`; dream_weaver lê.
- **Trade-offs**: 53GB RAM livres → janelas de 64–256 gerações (~MB) trivial; GPU saturada → proibir torch no caminho de análise; latência por janela < 50ms CPU. Rodar análise em thread do FastAPI lifespan (não bloquear ciclo de 25s).

### Q5 — Formato de proposta
Módulos, interfaces, tópicos, persistência, fases, riscos, não-fazer (ver §5–§8).

## 3. Features de atrator (especificação)

| Feature | Fórmula (CPU) | Range | Semântica β |
|---|---|---|---|
| `norm_drift[l]` | `abs(norm_t[l]-norm_{t-1}[l])` rolante | [0,∞) | desestabilização de camada |
| `entropy_collapse` | `1 - H_t/H_baseline` clamped [0,1] | [0,1] | colapso de atenção (bacia atratora) |
| `token_repetition` | n-gram repeat ratio | [0,1] | degeneração de geração |
| `divergent_layer` | `argmax_l norm_drift[l]` | int | camada "pensando demais" |
| `attractor_score` | `0.4*entropy_collapse + 0.3*token_repetition + 0.3*norm(norm_drift)` | [0,1] | carga emocional β |

`H_baseline` = média rolante (janela 128) de `attention_entropy_last`.

## 4. Módulos propostos (`src/omni_coworker/activation_beta/`)

| Módulo | Resp. | Interface pública |
|---|---|---|
| `collector.py` | tail incremental do jsonl + janela deslizante | `window(n=64) -> list[dict]`, `reset_offset()` |
| `features.py` | features de atrator numpy/polars | `extract(records) -> AttractorFeatures` |
| `beta_bridge.py` | records → BetaElement (digest + charge) | `to_beta(records, features) -> BetaElement` |
| `metabolize.py` | orquestra β→α via bion_bridge | `run(records) -> dict` (alpha_content, symbolic_potential, unmetabolized) |
| `publish.py` | publica no barramento + persiste | `publish(features, alpha)`, `flush()` |
| `store.py` | sqlite WAL `data/activation_beta.sqlite` | `append(ts, payload)`, `history(n)`, `prune()` |
| `schema.py` | dataclasses `AttractorFeatures`, validação | `validate()` |

## 5. Tópicos de malha (OW-DSN-003)

- `mesh.activation_beta` — features brutas por janela (consumido por dream_weaver, narrative).
- `dream.attractor` — atrator detectado (consumido por agency para meaning-making).
- `loop.modulation` — já existente; activation_beta adiciona `attractor_score` ao `Modulation` (campo novo, opcional).
- `kernel.feedback` — já existente; features agregadas.

## 6. Persistência

- Hot: ring buffer RAM (últimas 32 janelas `AttractorFeatures`).
- Warm: sqlite WAL `data/activation_beta.sqlite`, tabela `windows(ts, window_id, features_json, alpha_json)`, retenção 7 dias, pruning por `ts`.
- Cold: jsonl `data/monitor/activation_beta_windows.jsonl` (P2 gzip rotativo).
- Offset do tail: reuso `data/monitor/.offset` (não duplicar).

## 7. Fases

- **P0**: `collector.py` + `features.py` + `schema.py` + consumo pelo `integration_loop` (sensory_input enriquecido). Sem metabolização LLM. CPU-only. Entregável: `/loop/status` mostra `attractor_score` rolante.
- **P1**: `beta_bridge.py` + `metabolize.py` + `publish.py` + `store.py`. Metabolização α via bion_bridge (gate LLM por `_should_llm`). Consumidores dream_weaver/agency/narrative. Intervalo 60s.
- **P2**: retrieval pelo brain (modelo consulta ativação passada via faiss), self-training gated, jsonl gzip, daemon isolado opcional (stdin/stdout JSONL).

## 8. Riscos / compat

- Schema drift do jsonl: versionar por campo `v`; collector ignora campos desconhecidos; falhar suave (fail-open).
- Amplificação de degeneração: se `attractor_score` alto alimentar self-training sem gate, o modelo pode colapsar. Mitigar: gate `attractor_score < 0.85` para retenção; `negative_capability` para β não-metabolizável; scars para padrões repetidos.
- Latência: janela de 64 × 65 layers ≈ 4k floats; numpy < 50ms. Não bloquear ciclo de 25s — rodar em thread/asyncio task.
- OOM: limitar janela ≤ 256; spill para jsonl. 53GB livres é confortável.
- Paridade: validar features contra `/erika/activations` agregado (mesma fonte).

## 9. O que NÃO fazer

- **Não portar análise pesada GPU**: sem torch/CUDA no caminho de análise; numpy/Rust only. O brain (torch) permanece isolado em `erika_torch_server.py` (não tocar).
- **Não alimentar gradientes de volta**: somente observação. Nenhum `backward()`/`optimizer.step()` a partir de activation_beta. Self-training (P2) é decisão do brain, não do daemon, e sempre gated.
- **Não modificar** `server/erika_torch_server.py` nem o schema do jsonl (contrato de produção).
- **Não criar** novo processo/daemon no P0; reuso FastAPI lifespan.
- **Não afirmar** consciência/qualia: marcar como interpretativo/análogo (DSN-001/002 §4/§6).
- **Não implementar** neste estudo — apenas proposta. Implementação em port task separado.

## 10. Analogia–homologia (interpretativo)

Ativações como β-elements é análogo a "experiência bruta não-metabolizada" (Bion) — homologia estrutural com o pipeline β→α existente, não identidade com processos psíquicos humanos. Marcado como interpretativo. A "memória da própria ativação" do modelo (P2) é metáfora de self-modeling, não consciência.

pt-BR: ativação vira beta, beta vira alpha, alpha alimenta sonho e narrativa — observação, nunca intervenção no modelo.
