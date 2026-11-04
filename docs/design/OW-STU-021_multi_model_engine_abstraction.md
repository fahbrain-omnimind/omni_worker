<!-- doc_id: OW-STU-021 | Multi-model engine abstraction | Devin | 2026-11-04 | status: draft -->

# OW-STU-021 — Abstração Multi-Modelo do Motor (`erika_torch_server`)

**Pergunta de pesquisa**: repetir o cenário dual-brain da competição com
outras famílias (Mistral, Qwen, Llama…) na mesma classe de tamanho que caiba
na L4 (~22GB) — e, com quota A100+, rodar **todas em paralelo sob o mesmo
motor**, cada uma com suas dimensões próprias. O que o sistema precisa ter?

---

## 1. Diagnóstico — o que hoje é acoplado ao Gemma [DADO]

- `erika_torch_server.py`: `_MODEL_ID` por CLI (`--model-id`), AutoModelCausalLM
  + AutoTokenizer + BitsAndBytes NF4 — **genérico já** (não há código
  hardcoded ao Gemma além do default de modelo e do template).
- Pontos acoplados a dimensão/família:
  - `activation_steps/vectors`: `traj (L, steps, D)` — L e D livres por modelo
    (12B: 49×3840; E4B: 43×2560) → schema já suporta; o **consumidor** precisa
    ler shapes por arquivo, não assumir.
  - `dendritic_scan.layer_graph_from_traj`: L arbitrário OK (subsample ≤16
    nós já implementado pelo patch Argon).
  - `hidden_spectral` IPR_dim/eff_rank: opera por vetor — OK genérico.
  - `freud10d` perception vector (scheduler): construído de sinais MPS
    normalizados — **já independente de D**; mas `affect.attention_entropy_mean`
    depende de `attentions` retornados — **nem toda família expõe attentions
    iguais em NF4+eager** (Gemma-4 retorna; Mistral/Qwen costumam retornar
    com `attn_implementation="eager"`).
  - `apply_chat_template`: **por-tokenizer** — Mistral/Qwen têm templates
    nativos próprios; E4B-it é o caso especial (template customizado injetado).
  - Flags de degeneração (`degenerate`, `loop_suspeito`): hoje assumem a
    assinatura Gemma (spam repetitivo raw-completion). Outras famílias têm
    falhas distintas (Qwen: repetição de instrução; Mistral: drift de idioma)
    → o detector precisa de **assinaturas por família**.

## 2. O que falta — `model_profile` registry

Nova entidade: **`config/model_profiles.json`** (ou `data/model_profiles.json`),
um perfil por modelo:

```json
{
  "google/gemma-4-E4B-it": {
    "dim": 2560, "layers": 43, "attn": "eager", "quant": "nf4",
    "chat_template": "gemma-it", "degen_signature": "repetitive_spam",
    "vram_gb_nf4": 9.3, "role_default": "executor"
  },
  "mistralai/Mistral-7B-Instruct-v0.3": {
    "dim": 4096, "layers": 32, "attn": "eager", "quant": "nf4",
    "chat_template": "mistral", "degen_signature": "lang_drift",
    "vram_gb_nf4": 5.2, "role_default": "executor"
  }
}
```

Consumidores passam a ler `dim/layers` do **perfil ou do sidecar** (shape do
npz já carrega — bastante), `degen_signature` alimenta o flag do supervisor,
`vram_gb_nf4` alimenta o swap scheduler e o boot gate (10GB headroom hoje
hardcoded → `sum(vram_gb) + headroom`).

## 3. Paralelo multi-modelo (cenário A100)

- O motor já é stateless por processo (um `erika_torch_server` = um modelo =
  uma porta). N modelos = N processos = N portas.
- `agents/_llm.py` hoje resolve `:8098` analyst / `:8099` executor fixos
  → precisa de **brain registry** (`config/brains.json`: role→{model,port})
  e o `brain_proxy`/`peer-swap` generalizado: swap por `vram_gb` do perfil,
  não por lista de 2.
- `start_omni_worker.sh`: `--brains analyst:MODEL:8098 executor:MODEL:8099 …`
  (hoje args fixos); boot sequencial já existe — paralelismo via portas livres.
- `kernel_daemon` perception vector: hoje pega `attention_entropy_mean` dos
  dois roles fixos (`analyst`,`executor`) → generalizar para `affect` dict
  indexado por role (o bundle já publica `affect` por nome).

## 4. Personalização por modelo (o que é diferente)

| Aspecto | Hoje | Multi-modelo precisa |
|---|---|---|
| dims L×D | lado no shape do npz | ler shape por arquivo (já OK nos novos consumidores) |
| chat template | Gemma-it hardcoded no E4B | per-profile, `tokenizer.apply_chat_template` nativo |
| assinatura degen | spam Gemma | `degen_signature` por família + flags plurais |
| vram/swap | 2 brains fixos | soma por perfil + registry de portas |
| percepção freud10d | soma+soul+affect(2 roles) | vetor sobre N roles do registry |
| scores espectrais | neutros | ok; mas IPR/D compara % — já normalizado |
| linguagem da escuta | — | `task` label já rotula; adicionar `family` no capture.env label |

## 5. Incrementos concretos (ordem)

1. `config/model_profiles.json` + loader `soma/model_profile.py` (perfis
   Gemma + 2–3 alvos: Mistral-7B-Instruct, Qwen2.5-7B-Instruct, Llama-3.1-8B —
   todos cabem NF4 na L4).
2. `start_omni_worker.sh --brains role:model:port` + boot sequencial por
   `vram_gb`.
3. `brains.json` registry consumido por `_llm.py`/peer-swap/scheduler
   (perception vector sobre N roles).
4. `degen_signature` por família no supervisor/flags.
5. Bateria multi-modelo: mesmo `run_listening_battery` parametrizado por
   `MODEL_PORT` — comparação direta Gemma×Mistral×Qwen nas mesmas 4 tasks.

**[LIMITE]** A100 permite todos em paralelo mas cada geração ainda serializa
por processo — throughput real depende de quota, não de código.
