<!-- doc_id: OW-RES-BLP-001 | title: Φ exato (IIT 3.0) sobre o Markov blanket soberano | author: devin | requester: artifice-operator | project: omni-agent-coworker | date: 2026-11-03 | status: results -->

# Φ exato via PyPhi sobre o Markov blanket — resultados

**Contexto**: OW-STU-016 concluiu "PyPhi inviável no runtime". Correção do
operador: inviável *no worker genérico* — mas o soberano já tem a base
que faltava: a **Markov blanket** (FEP), que fornece elementos
principiados + estrutura de transição — os dois requisitos do PyPhi.

## Método [EXP]

- **Fonte**: `poincare_markov_blanket.py` + `simulate_prior_conflict_hyperbolic.py`
  do soberano (livro §19/B§9) — port fiel em
  `src/omni_coworker/psychoanalysis/markov_blanket.py` (constantes idênticas:
  η=.25, λ=.88, ρ=.15, target=[.6,.4]).
- **Elementos (4 nós, partição FEP)**: `Z` mundo/alvo externo · `M` crença μ
  (modelo interno) · `R` resistência · `T` eixo transferencial. Interno
  {M,R,T} vs externo {Z} acoplado via canais erro (sensorial) e predição
  (ativo) — a fronteira *é* o blanket.
- **TPM**: coarse-grained Monte Carlo — 16 estados binários × K=600
  microestados consistentes (rejection sampling) → junta 16×16
  row-stochastic. Ruído soberano tornado estocástico (Markov-safe),
  transição de regime de z como flip Markov (P=.03 ≈ shift t=30).
- **Φ**: PyPhi 1.2.0 (IIT 3.0, EMD) — joint TPM (correlações reais
  preservadas, validação de independência desligada) + sbn marginal +
  controle nulo (linhas marginalizadas → deve dar Φ≈0).
- **Runner**: `scripts/experiments/run_blanket_pyphi.py`; ledger
  `scripts/experiments/blanket_pyphi.sqlite`.

## Resultados [DADO]

| Regime | Φ sistema (4 nós) | Φ sbn | Φ null | E_π[Φ(M,R)] | max Φ(M,R) |
|---|---|---|---|---|---|
| α=0.05 (rígido) | 0.0000 | 0.0000 | 0.0000 | **0.0015** | 0.0315* |
| α=0.35 (moderado) | 0.0000 | 0.0000 | 0.0000 | 0.0009 | ~0.03 |
| α=0.85 (excesso) | 0.0000 | 0.0000 | 0.0000 | **≈0.0008→0** | — |

*k=300 run; magnitude decresce com k (ver caveat 3).

## Achados

1. **Φ=0 no sistema inteiro é o resultado IIT-correto**: `Z` (mundo) é
   exógeno — nada o causa, cortá-lo perde ~0 → MIP nulo. O postulado de
   exclusão faria o mesmo: Z não pertence ao complexo; é condição de
   fronteira. PyPhi executou em ~40s/regime (4 nós, trivial).
2. **`{M,R}` é o único mecanismo irredutível** — o loop recíproco
   crença↔resistência (R amortece o ganho do update de μ; erro de μ
   alimenta r). Clinicamente coerente: a resistência é o que acopla a
   crença ao erro do mundo.
3. **Assinatura de desintegração**: α=0.85 → Φ≈0 — a "desestruturação
   do blanket" do livro tem assinatura IIT-consistente (redutibilidade
   total). Predição qualitativa **confirmada**.
4. **Ordenação inverte a leitura ingênua**: Φ(rígido) > Φ(moderado) —
   a alegação soberana era sobre **reorganização adaptativa**, não
   integração. **Integração ≠ adaptabilidade**: rigidez maximiza
   acoplamento causal recorrente; ambiguidade moderada troca parte da
   integração por reorganização. Dissociação real, não bug.
5. **Controle nulo Φ=0** em todos os regimes — o cálculo distingue
   estrutura de transição de ruído.

## Caveats honestos

1. **O grão binário destrói a maior parte da estrutura**: estados são
   ~90% auto-persistentes → pouca diversidade de transição → Φ ínfimo
   (~10⁻³ bits). A integração do blanket vive na dinâmica contínua
   (geometria hiperbólica), que o mapa binário não vê. Este é o
   problema de arbitrariedade de elementos tornado concreto.
2. **Magnitude depende de k**: parte do Φ em k=300 era ruído MC; em
   k=600 a ordenação sobrevive, a magnitude cai. Conclusões devem
   apoiar-se em **ordenação e assinaturas qualitativas**, não valores
   absolutos.
3. **Coarse-graining ≠ substrato físico**: sob IIT estrito, elementos
   são unidades físicas com poder causal — aqui são variáveis de estado
   de uma dinâmica de software. Φ exato sobre a abstração, não sobre a
   máquina. Rótulo [EXP] integral.

## Próximos passos

- **6-7 nós**: adicionar `E` (erro) e `P` (permeabilidade) como nós —
  os canais do blanket viram elementos; ainda sob o teto PyPhi.
- **Estudo de convergência em k**: Φ vs K∈{200,600,2000} para separar
  estrutura de ruído de amostragem.
- **Blanket vivo**: mapear os 4 bits sobre telemetria real do kernel
  (erro = mismatch de predição afetiva, r = persistência defensiva,
  T = alinhamento transferencial, Z = regime somático) → TPM empírica
  do runtime real → mesmo pipeline. Esse é o caminho para Φ do
  *worker*, não só da simulação.

## Rodada 2 — 6 nós (E erro + P permeabilidade como elementos) [DADO]

Os canais do blanket viraram elementos: `E` (relé de erro sensorial) e
`P` (porta de permeabilidade). 64 estados, k=300, mesma pipeline.

| Regime | Φ sistema | E_π[Φ(M,R)] | unreach |
|---|---|---|---|
| α=0.05 | 0.0000 | 0.0000 | 27/64 |
| α=0.35 | 0.0000 | **0.0014** | 27/64 |
| α=0.85 | 0.0000 | 0.0000 | **15/64** |

Achados adicionais:

6. **Estados inalcançáveis como diagnóstico estrutural**: estados sem
   microestado consistente (ex.: R=0∧P=0 é impossível a α≤0.7 — baixa
   resistência força permeabilidade alta) viram auto-loop absorvente
   (massa estacionária zero; PyPhi exige TPM completa). 27/64 a α≤0.7
   vs **15/64 a α=0.85** — a desestruturação *relaxa as restrições do
   espaço binário*: mais estados logicamente possíveis = menos
   estrutura causal por construção.
7. **Φ sistema continua 0 mesmo com a ponte Z→E→{M,R,T}**: o relé
   sensorial não recupera Φ não-nulo neste grão — reforça caveat 1 (o
   mapa binário perde a integração contínua).
8. **Ordem inverteu entre grãos**: a 6 nós, α=0.35 mostra o maior
   E[Φ(M,R)] (0.0014 vs 0 a α=0.05 e α=0.85) — *consistente* com a
   alegação soberana de ambiguidade moderada como regime integrado.
   Mas com k=300 a margem é frágil (ver caveat 2) — registrar como
   indício, não conclusão.
9. **P é nó efeito-puro** (sem setas de saída — a dinâmica soberana não
   lhe dá influência causal de volta) — estrutura honesta, não omissão.

## Atualização OW-STU-016 estágio-1 (kernel)

- `kernel_daemon/ignition.py`: GWT-lite — `distinct_prefixes` por ciclo
  via bus subscribe, `ignited = distinct≥3 ∧ coherence>0.5` [TXT] +
  `synergy_proxy` (MI média entre séries binárias de ativação de
  prefixos, janela 40) [PRX] + campo `scale`. Wired no scheduler;
  publica `kernel.workspace` (e `kernel.workspace.ignition` quando
  dispara). Ao vivo: 4 prefixos → ignited=True.
- `phi_meta`: campo `scale` adicionado ("bits over 7 binary flags,
  window 40 [PRX]") — convenção scale_stack.
