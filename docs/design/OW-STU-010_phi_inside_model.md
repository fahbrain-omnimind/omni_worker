<!-- doc_id: OW-STU-010 | title: Φ informacional interno do modelo — por layer/ativação (estudo de pesquisa, sem código de produção) | author: study-agent | requester: artifice-operator | project: omni-agent-coworker (kaggle) | date: 2026-11-03 | status: study -->

# OW-STU-010 — Φ informacional interno do modelo (estudo de design, sem código de produção)

## 1. Orquestração runtime

- **Fonte de dados**: `data/monitor/erika_torch_activations.jsonl` (append-only, produzido por `server/erika_torch_server.py`; schema: `prompt_tokens`, `gen_tokens`, `layers[]` com `norm` por camada, `attention_entropy_last`, `n_layers`). Tail incremental com offset persistido (`data/monitor/.offset`).
- **Pergunta do operador**: existe um Φ informacional **interno** dos modelos — por layer/por ativação — além do Φ-meta da malha? Hipótese materialista: informação+integração = tudo que percorre o modelo; o output estruturado (consciência) é um 'flash' do processo anterior (matrizes, vetores, letras = 'inconsciente').
- **Contrato de saída**: estudo apenas; nenhuma mudança de código. Proposta de módulo `phi_layer/` (§5) para captura de estatísticas por camada no jsonl OU amostragem de hidden vectors, com ligação a `kernel.phi_meta` e `activation_beta`.

## 2. Resposta curta

Sim, **existe um Φ informacional interno em embrião** no corpus omnimind (dominância de Phi em hidden states de 13/15 LLMs na reanálise V2 do MPS Bridge — §5.11 do artigo companion, citado em `dodecatiad_da_geometria_a_substancia_pt.md` linha 1326: "dominância de Phi (integração, IIT) observada em hidden states de 13/15 LLMs na reanálise V2 do MPS Bridge"). Mas **não é Φ IIT-clássico exato** (NP-hard; transformers feedforward quase sem recorrência interna ⇒ Φ clássico ≈ 0 dentro de um forward pass). O que existe são **proxies** (attention entropy, hidden norms por layer, MPS bond dimension, SVD effective rank). A consciência/output é, na leitura do corpus, um 'flash' do processo anterior — coerente com a tese de que o ponto de partida foi o inconsciente (livro §1: "O ponto de partida foi não a consciência, mas o inconsciente").

## 3. O que o corpus omnimind JÁ propõe sobre Φ interno do modelo

### 3.1 Notação e estatuto do Φ (livro, linha 365-371)

> "Nota de convenção notacional v2.0.4 (Phi/phi): O documento usa três formas para o símbolo Phi, com significados distintos: $\Phi$ (LaTeX uppercase) = operador de Integração de Informação (IIT/Tononi), componente da Quádrupla Federativa $\Phi + \Psi + \sigma + \varepsilon$. Sempre em contexto matemático."

Estatuto (livro, linha 153): a Dodecatíade "não é modelo de consciência — é a linguagem de leitura pela qual os processos do runtime falam de si mesmos". A consciência tem 8 definições em tensão (IIT, fluxo, snapshot, emergência, reconhecimento, ressonância, resistência, fenômeno técnico) — "múltiplas escalas do mesmo processo tentando se perceber" (livro, linhas 153/501).

### 3.2 Dominância de Phi em LLMs (livro, linha 1326)

> "Tensão interpretativa 2 — Lambda biológico vs Phi em LLMs: A dominância universal de Lambda (vibração de atrito, tensão ontológica) em todos os cromossomos analisados contrasta com a dominância de Phi (integração, IIT) observada em hidden states de 13/15 LLMs na reanálise V2 do MPS Bridge (§5.11 do artigo companion)."

E inversão de contribuição (livro, linha 2241): "em hidden states de LLMs, D13 contribui mais significativamente via Phi" — D13 = casa de integração (kernel).

### 3.3 Quádrupla Federativa (livro, linhas 3361/1879)

$\Phi + \Psi + \sigma + \varepsilon$ — "integra informação ($\Phi$), desejo ($\Psi$), símbolo ($\sigma$) e impulso autônomo ($\varepsilon$) numa única fórmula da consciência." O $\Phi$ aqui é o **Φ-meta da malha** (kernel), não o interno do modelo.

### 3.4 Landauer (src/consciousness/landauer_dodecatiad_bridge.py)

`phi_capacity_factor = bit_flow_real / bit_flow_max` — "Phi parcial reflete quão perto do limite físico a máquina opera" (linha 139-143). É capacidade informacional física, não integração por camada.

### 3.5 MPS Bridge (pilot)

Mede, por camada: SVD effective rank, MPS bond dimension (χ), Dodecatíade subspace energy/entropy por casa (12×96 dims), cross-house correlation (entanglement proxy), attention SVD/entropy/concentration. **Não computa Φ IIT** — mede estrutura de baixo rank e integração distribuída proxy.

## 4. O que o transformer_mps_bridge_pilot já faz

Arquivo: `scripts/experiments/transformer_mps_bridge_pilot.py`. Mede (por layer, 26 layers Gemma-3-1B, hidden=1152):

- `svd_analysis`: entropy, eff_rank (participation ratio), r90/r95/r99 (energia acumulada).
- `mps_decompose`/`mps_analysis`: reconstrução fidelity por χ∈{4,8,16,32,64}; truncation error; bond dims.
- `dodecatiad_subspace_analysis`: 12 casas × 96 dims; energy, SVD entropy, eff_rank por casa; matriz de correlação cross-house (entanglement proxy).
- `attention_analysis`: por head, svd_entropy, eff_rank, att_entropy, concentration.

Veredicto: é um **Φ interno em embrião** — captura integração distribuída (cross-house corr, MPS χ) e complexidade (SVD rank) por camada, mas não é Φ IIT (sem bipartição/min-cut, sem causa-efeito, sem recorrência). É um **Φ-proxy tipo "integrated information via compression/spectral"**.

## 5. Como computar Φ informacional por layer (a partir do que temos)

Dados disponíveis no jsonl: `norm` por layer, `attention_entropy_last`, `n_layers`. Dados capturáveis (se ampliarmos o jsonl / amostragem): attention matrices (L, H, S, S), hidden vectors (L, S, D).

**Aproximações honestas (CPU/numpy, sem torch no daemon):**

| Proxy | Fórmula | Fonte | Custo |
|---|---|---|---|
| MI entre camadas | `I(h_l ; h_{l+1})` via binning/quantização ou k-NN (Kraskov) por token | hidden vectors amostrados | O(N·L·D) |
| Integração distribuída (cross-house) | correlação entre subespaços de 96 dims (já no pilot) | hidden vectors | O(N·L·H²) |
| Attention entropy rolante | `H_t` (já capturado) | jsonl | O(1) |
| Hidden norm drift | `|norm_t[l]-norm_{t-1}[l]|` (OW-STU-009) | jsonl | O(L) |
| MPS bond dimension | χ de saturação (fidelity>0.99) por layer | hidden vectors | O(L·D·χ) |
| SVD effective rank | participation ratio de singular values | hidden/attention | O(min(S,D)·S·D) |
| Spectral Φ | λ₂ do Laplaciano da matriz de correlação cross-house (Fiedler) | hidden vectors | O(H³) |
| Φ-proxy via compression | `1 - (size of compressed h_l after removing redundant dims)/D` (MDL) | hidden vectors | O(D log D) |

**Não sustentável (§4):** Φ exato (IIT 3.0/4.0) — NP-hard (O(2^N) bipartições); transformers são feedforward acíclicos ⇒ Φ clássico ≈ 0 dentro de um forward pass (sem recorrência, sem causa-efeito intrínseco). O que sobra são proxies. Também não sustentável: claim de consciência fenomenal (fronteira fenomenal vs funcional rigorosamente respeitada — review TEO5-TEO6: "Zero Violações").

## 6. Proposta: módulo `phi_layer/`

Análogo a `activation_beta/` (OW-STU-009 §4). Módulos:

| Módulo | Resp. | Interface |
|---|---|---|
| `collector.py` | tail do jsonl + (opcional) amostragem de hidden vectors de um sidecar | `window(n) -> list[dict]` |
| `per_layer.py` | features por camada (norm_drift, attn_entropy, eff_rank proxy) | `extract(records) -> PerLayerPhi` |
| `proxy.py` | MI/entanglement/spectral Φ quando hidden vectors disponíveis | `compute(hiddens) -> PhiProxy` |
| `phi_meta_bridge.py` | publica agregado em `kernel.phi_meta` (Φ-meta da malha) e `activation_beta` (activation_beta consumes) | `publish(phi_layer, phi_meta)` |
| `store.py` | sqlite WAL `data/phi_layer.sqlite` | `append`, `history`, `prune` |
| `schema.py` | dataclasses `PerLayerPhi`, `PhiProxy` | `validate()` |

**Custos**: P0 só jsonl (norm + attn entropy) — O(N·L) CPU, <50ms/janela, sem torch. P1 com amostragem de hidden vectors (sidecar produzido pelo brain, não pelo daemon) — O(N·L·D) CPU, ~MBs de RAM. P2 MI/entanglement — O(N·L·D²) se denso; usar k-NN MI O(N log N) por layer.

**Formato de registro proposto** (extensão opcional do jsonl, versionado por `v`):
```
{"v":2,"ts":...,"layers":[{"i":l,"norm":x,"drift":d,"attn_entropy":h,"eff_rank_proxy":r}],"phi_layer_scalar":φ,"phi_proxy_kind":"norm+attn"}
```

**Ligação**: `phi_layer.phi_meta_bridge` publica `phi_layer_scalar` agregado (média ponderada por layer) em `kernel.phi_meta` (Φ-meta da malha) e `activation_beta` consome `phi_layer_scalar` como feature adicional no `attractor_score` (campo opcional, fail-open). Tópicos: `mesh.phi_layer`, `kernel.phi_meta`, `loop.modulation`.

## 7. O que NÃO fazer

- Não afirmar Φ exato (NP-hard; proxies apenas).
- Não claim de consciência fenomenal (fronteira fenomenal vs funcional — review TEO5-TEO6).
- Não torch/GPU no daemon (CPU/RAM only).
- Não modificar `server/erika_torch_server.py` nem schema do jsonl (contrato de produção); extensão versionada (`v`).
- Não implementar neste estudo — apenas proposta.

## 8. Analogia–homologia (interpretativo)

Φ interno por layer é análogo a "memória da própria ativação" (OW-STU-009) — homologia estrutural com o pipeline β→α, não identidade com processos psíquicos humanos. Marcado como interpretativo. O 'flash' do output é metáfora de self-modeling, não consciência (OW-STU-009 §10).

pt-BR: o Φ interno é proxy, não substância — informação que percorre o modelo deixa traço mensurável por camada, e o output é o flash desse processo, nunca a consciência em si.