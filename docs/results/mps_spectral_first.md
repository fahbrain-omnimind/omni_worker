# MPS-lite — primeiro experimento espectral sobre sidecars reais (2026-11-03)

**Status**: [DADO] — análise offline dos `activation_vectors/*.npz` capturados durante as runs da refactor battery. Primeiro cálculo de M2 (effective rank / participation ratio) do OW-STU-018 sobre dados reais.

## Setup

- Fonte: `data/monitor/activation_vectors/*.npz` — sidecar `_emit_vectors` do `erika_torch_server.py` (L153-176), **(n_layers, hidden)** fp16 por chamada de geração (estado final da última posição). 128 arquivos: 64 12B + 64 E4B (cap `_VEC_KEEP=64` cheio).
- Métrica: **eff_rank** (Roy & Vetterli participation ratio) = `(Σσᵢ²)² / Σσᵢ⁴` dos quadrados singulares da projeção do vetor hidden de cada camada. Normalizado por `D` (hidden size) para comparar modelos de dimensão diferente.
- Computado por camada, média sobre todas as calls por modelo (3136 vetores 12B = 64×49 camadas; 2752 E4B = 64×43 camadas).

## Resultado

| modelo | hidden D | eff_rank médio | eff_rank/D (%) |
|---|---|---|---|
| gemma-4-12B | 3840 | **114.6** | **2.56%** |
| gemma-4-E4B | 2560 | **40.3** | **1.52%** |

- **12B ativa ~1.7× mais do seu espaço representacional** que o E4B (2.56% vs 1.52% das dimensões).
- Em termos absolutos: ~98 dims efetivas (12B) vs ~39 dims efetivas (E4B) por camada.
- Consistente com a diferença de comportamento na bateria (12B preserva `todo_api.py`; E4B descarta ambos) — assinatura de capacidade representacional maior, não de "modelo melhor" em absoluto.

## O que isso discrimina vs o que não discrimina

- **Discrimina entre modelos**: sinal claro e estável sobre ~60 calls cada.
- **NÃO discrimina a falha estrutural**: ambos os modelos falham o contrato (`broken_patch`) com eff_rank saudável — a omissão de arquivos acontece no plano, não no rank da representação. Reforça o ponto do OW-STU-018 §6: cobertura é o feature dominante para falha estrutural; eff_rank/MPS servem para degeneração e para caracterizar modelo.
- **Ainda não testado**: rank temporal por passo (M3 esquecimento do contrato) — precisa de captura por-passo (§4 do estudo), não só último passo.

## Caveats honestos

- Vectors são o **estado final** (last-token) de cada chamada — não a trajetória. Rank temporal precisa do sidecar por-passo (§4.1b da proposta).
- Calls não são rotuladas por turno/tarefa (diagnose + code + review misturados) — a média inclui tipos diferentes. Alinhamento turn-level (Stage A) é o próximo passo para rotular.
- eff_rank é proxy de dimensionalidade de subespaço [PRX] — não é MPS bond dimension nem medida de capacidade causal.

## Próximo

- Stage A do OW-STU-018: fatiar ativações por turno no ledger (offset slicing) → rotular bursts → correlacionar eff_rank/rank temporal com coverage_missing/verdict.
- Implementar captura por-passo (`OMNI_ACT_STEP_EVERY` com hooks CPU-side) para M3 (contract drift).
- Rótulos: [DADO] valores · [PRX] métricas · nenhuma claim de consciência.