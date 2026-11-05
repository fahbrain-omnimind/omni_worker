"""activation_beta — janela de atrator sobre erika_torch_activations.

Orquestração runtime / Runtime orchestration:
`push(records)` alimenta um deque in-process com os registros novos
consumidos pelo collector do kernel_daemon; `features()` deriva as
features de atrator (norm_drift, entropy_collapse, divergent_layer,
attractor_score) sobre a janela recente — sem torch, sem I/O.

Arquitetura / Architecture:
Implementa o P0 de docs/design/OW-STU-009_activations_as_beta.md:
registros `{ts, model, layers:[{layer,norm,mean,std}],
attention_entropy_last}` → features de atrator → BetaElement
(source="activations.window") → α via bion_bridge.

Princípios teóricos invocados / Theoretical principles:
Bacia atratora ≈ dinâmica convergente detectável: entropia de atenção
colapsando + drift de norma concentrado em camada divergente. NÃO é
dinâmica de gradiente — é observação estatística sobre produção.

Analogia–homologia (interpretativo):
O registro de ativação como "experiência bruta" do modelo (β) que o
sistema metaboliza (α) — verbalização operacional, não fenomenologia.

pt-BR: atratores sobre ativações — janela + features, sem torch.
"""

from .attractor import features, push, reset, window_size

__all__ = ["features", "push", "reset", "window_size"]
