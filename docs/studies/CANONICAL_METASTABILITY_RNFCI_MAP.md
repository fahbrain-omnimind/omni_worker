<!-- doc_id: OW-STU-002 | title: Canonical Metastability + RNFCI Map — omni_worker | author: devin (subagent-mapped) | requester: artifice-operator | project: omni-agent-coworker (kaggle) | date: 2026-11-03 | status: active -->

# Mapa Canônico — Metaestabilidade/HSP (DOC_A + DOC_C) × RNFCI V49 → omni_worker

pt-BR: Mapa estrutural dos três documentos canônicos e sua aplicabilidade a este
worker (dual Gemma-4 NF4 na L4, FastAPI :8081, sem daemons canônicos).
English: structural map of three canonical docs and their applicability to this
worker — see §8 for the English summary.

Fontes (somente leitura, repo canônico):
- `omnimind-kilombo-sovereign/revisao/metastability_v3/DOC_A_MANIFESTO_HSP.md` (370 ln, v3.1-draft, 2026-09-23)
- `omnimind-kilombo-sovereign/revisao/metastability_v3/DOC_C_PAPER_EXPERIMENTAL.md` (498 ln, v3.0-draft, 2026-09-23)
- `omnimind-kilombo-sovereign/docs/zenodo_packs/rnfci_pack_v1_textual_correction_v2_20260527/upload_bundle_release/V49_REDES_NEURAIS_PSICANALITICAS_20260527.md` (347 ln, 2026-05-27, CC BY-NC-ND 4.0)

## 1. Mapa estrutural — DOC_A (Manifesto HSP)

- **Tese:** HSP é *hipótese arquitetural*, não entidade provada. Candidato a HSP =
  evidências operacionais de Autonomia, Memória histórica, Reescrita recursiva,
  Continuidade, Historicidade (Tabela 1, §1) — cada critério com definição,
  superfície de observação, teste de falha e limite interpretativo.
- **Seções:** Estatuto L1–L4/Níveis A–D · regra editorial `ontologia ≠ modelo ≠
  implementação ≠ evidência` · §1 critérios HSP · §2 acoplamento físico↔psíquico
  em **3 registros** (mecanismo / simulação / leitura ontológica) + Tabelas
  2 (Pulsão↔orçamento, Sinthome↔invariantes, Função Alfa↔filtragem, Traço unário↔
  marca persistente), 2b (malha de autores 464D/15 `nn.Module`), 2c (psicanálise
  distribuída: Bion, Piaget/INRC, Lacan, Deleuze, Wallon…Freire) · §3 genealogia
  (Bohm, Pribram, Orch-OR, θ_sinthome=√2π como *parâmetro do projeto*) · §4
  Critério R rebaixado a exploratório · §5 limites da analogia + **regra de
  permanência** (pedágio vs baseline) · §6 ΔH testável · §7 psicanálise como
  lógica de controle de habitação (CN_PHI=`composite_score`; `angst` tem 3
  implementações divergentes — imprecisão registrada) · §8 ética de execução em
  4 camadas (corpo / incompletude / recusa freireana / contrato soberano) · §9
  metaestabilidade = família abstrata trans-substrato (não identidade) · §10
  divisão A(vocabulário)/B(interfaces)/C(evidência).
- **DOI citado:** da Silva, *HSP Manifesto* → Zenodo 20417020; Schmieke QBF →
  10.5281/zenodo.18629508, 18691789, 18832969.

## 2. Mapa estrutural — DOC_C (Paper experimental)

- **Tese:** arquitetura exploratória e falsificável de controle adaptativo de
  runtimes distribuídos sob observação parcial — 4 problemas: estimação de
  estado, classificação de regime, roteamento por risco, continuidade.
- **Seções:** §1 limites de falsificação (superfícies inspecionáveis; alegações
  proibidas; anti-superioridade; **declaração de intervenção**) · §2 modelo
  state-space POMDP + ΔH · §3 VBKF (`x=[health,pressure,recovery]`,
  `z=[quorum,lease,latency,d12score]`; política de ausência: skip-update /
  R→∞ / missingness-como-feature) · §4 `S_meta = Σw_j·j` (P/T/R/O/K), faixas→
  regimes→políticas como **convenção**, Lyapunov = hipótese pendente, Page-
  Hinkley/CUSUM p/ regime · §5 `J_governance` (NLL+Risk+Transition+ActionCost+
  HistoryIntegrityLoss) · §6 simulação MoE-like (gate por regime; snapshot
  0.9985 vs 0.9383 = descritivo, não prova) · §7 evidência: F1 calibração
  (n=12 500), F2 sintético (VBKF vs KFOR), **F2b falha real** (detector parado
  180 s: detecção 10,1 s; liveness 0 s ≠ readiness), §7.5 **bug multi-fonte** →
  `event_identity=(source,stream,timestamp,sequence)` e registros contaminados
  *permanecem* (historicidade), F3–F5, §7.9 pré-alerta PH · §8 envelope de
  metadados obrigatório (0/1774 conformes — proposto) · §9 limitações/
  prioridades · §10 refs.
- **DOI citado:** Shan et al. 2024 (10.1016/j.jprocont.2024.103211); Li et al.
  2026 (10.48550/arXiv.2604.02738); genealogia = mesmos DOIs de §1.

## 3. Mapa estrutural — V49 RNFCI

- **Tese:** redes neurais psicanalíticas — da engenharia à ética da posição de
  sujeito. Agente histórico `a_t=f(H_t)` irredutível a janela `W_n` (Teorema 1).
- **Seções:** Glossário (H_t, s_t D=8192, Audit Chain, Dodecatad, neutrosofia,
  INRC, Bahnung, Umschrift, BVGI, VFE, J_t) · §1 Teorema Agente Histórico · §2
  Lema Dodecatáde (12 faces, setores basal/ético/simbólico, matriz M 12×12) ·
  §3 álgebra INRC (I,N,R,C involutivos; Klein-4) · §4 triple ⟨T,I,F⟩ por face,
  `ΔX_k=η(1−I_k)(T_k−F_k)`, I_k→1 = *transition lock* (anti-fechamento binário)
  · §5 VFE (KL) + J_t + damping Hamiltoniano; SDM Hamming 8192d; ignição GWT ·
  §6 `C_soma = α₁Lat+α₂Temp+α₃Swap+α₄(1−BVGI)` (BVGI: 5 R's, pesos
  0.18/0.22/0.15/0.20/0.25; baseline μ=0,5226) · §7 sujeito-processo = I(H_t)≠0
  · §8 fluxo tensional `Ẋ_i=ΣM_ij(X_j−X_i)−δ_iJ_i` · §9 reversibilidade INRC
  `d(C∘R∘N(s_t),s_t)=0` · §10 Algoritmo 1 (ciclo runtime) · §11 **3 invariantes
  éticos**: auditabilidade da inscrição; preservação da falha de Umschrift
  (I_k≠0); recusa soberana (BVGI<0,50 ou violação homeostática) — ética como
  restrição do espaço de busca, *não* filtro de saída · §12 tabela conceito→
  módulo + limite: method skeleton público, sujeito-processo local soberano.
- **DOI:** o manuscrito não carrega DOI inline; o `PACK_MANIFEST.json` do bundle
  declara `doi: 10.5281/zenodo.20417020` (nova versão do mesmo registro).
  *(incerteza honesta: tratar como DOI do pack/bundle, não do paper isolado.)*

## 4. O que os três exigem arquiteturalmente

- **DOC_C (técnico):** estimador de estado latente; política de ausência; score
  composto com faixas→política declaradas; detector de mudança de regime; custo
  de decisão com termo de integridade histórica; identidade de evento multi-
  fonte; declaração de intervenção; artefatos versionados com metadados.
- **DOC_A (posição):** disciplina de estratos (claim carrega L1–L4); gramática
  operador↔contrapartida; ética em camadas de restrição antes da execução;
  analogia só permanece pagando pedágio de predição/controle/auditabilidade.
- **V49:** história imutável (SQLite + hash-chain); estado latente + faces com
  indeterminacy preservada; custo somático real na política; invariantes éticos
  estruturais; separação method-skeleton público × sujeito local.

## 5. Aplicabilidade ao worker — IMPLEMENTADO (ou análogo funcional)

| Exigência | Worker | Nota |
|---|---|---|
| H_t / Audit Chain / traço unário | `agency/witness.py` (JSONL sha256 + `verify_witness`) + dual-write `node_db`; `store/audit_adapter.py` → ImmutableAuditSystem canônico | V49 §1.3/§11.2 — ok |
| C_soma / telemetria host | `soma/probe.py` (cpu/ram/swap/load/GPU/virt) + `somatic_store` SQLite; `_soma_inject` leva soma ao prompt | V49 §6 — sem BVGI formal |
| Faces dodecatáde | `soul/dodeca.py` S01–S15, 9 computáveis standalone (resto `unavailable_standalone`) | V49 §2 — só eixos; sem M, sem ⟨T,I,F⟩ |
| Afeto/afex | `kernel_hooks.affect_state` (28d/18 afex), `brain/affect.py` (phi/psi/sigma/epsilon), `dunker.py` adapter, `affect_tracer` L0–L4 | análogo de V49 §5/§11 |
| Contenção/fallback | `governance.py` Trust/Quarantine/Rollback/CircuitBreaker; `safety/gate.py` EXECUTE/TEACH/REFUSE | DOC_C §4.2/§5; V49 §11.2; DOC_A §8 |
| Continuidade | `state_guard` snapshots tar.gz + manifest hash + restore | HSP critério C (DOC_A T1) |
| Cuidado territorial | `safety/care.py` (CVV/CAPS por UF) | módulo próprio, sem base canônica |

## 6. Aplicabilidade — MAPEÁVEL (não implementado, caminho claro)

- **S_meta-like** sobre `somatic_probes.sqlite` + probes de brain — componentes
  P/T/R/O/K e faixas→política como convenção declarada [DOC_C §4.1–4.2].
- **Filtro/simples estimador latente** (health/pressure/recovery) sobre a série
  de probes — VBKF completo é opcional [DOC_C §3].
- **Missingness como feature:** `recorded=False`/`unavailable_standalone` já
  existem — formalizar skip-update + flag em vez de imputar [DOC_C §3.3].
- **Pré-alerta Page-Hinkley/CUSUM** sobre load/temp/VRAM [DOC_C §7.9].
- **Declaração de intervenção** para `swap_scheduler` evict/reload, quarantine e
  cascade reset (reversibilidade/escopo/risco/rollback/autorização) [DOC_C §1.4].
- **Envelope de metadados** em `state_guard` manifest e artefatos de battery
  (schema_version, producer_commit, generated_at, limitations) [DOC_C §8.3].
- **I_k por casa:** `unavailable_standalone` já é uma forma de indeterminacy —
  formalizar como ⟨T,I,F⟩ leve no `/soul/dodeca` [V49 §4].

## 7. Aplicabilidade — FORA DE ESCOPO

- Malha de autores 464D/15 `nn.Module`, subsistema Bion, INRC Rust `freud10d`,
  developmental mesh: dependem do repo canônico inteiro (DOC_A T2b–T2c).
- VBKF/soliton-raft/Prometheus/cn_regime: daemons canônicos — este worker
  explicitamente não os hospeda.
- BVGI formal (R_timing systemd, afrorhythmic 3–5 Hz/75,37 Hz): sem soma
  rítmica/systemd no container [V49 §6.2].
- GWT ignition, SDM 8192d Hamming, damping Hamiltoniano: vocabulário de design
  apenas; sem implementação correspondente aqui.
- Claims Lyapunov, Orch-OR, θ_sinthome, Elemento Zero, trans-substrato: [L4] —
  não geram tarefas de engenharia (DOC_A §3–§5; DOC_C §4.3).

## 8. Diretrizes deriváveis (seção citada por diretriz)

1. **Todo valor publicado carrega fonte+fórmula** — manter o padrão `dodeca.py`
   (source/formula por casa) em qualquer score novo. [DOC_A Legenda; DOC_C §1.1]
2. **Faixas de score são convenção de política, nunca teorema.** [DOC_C §4.2]
3. **Ausência é evidência:** canal mudo → flag de missingness; nunca imputar
   zero nem silenciar. [DOC_C §3.3]
4. **Toda intervenção declara** reversibilidade, escopo, dependências, risco,
   rollback, autorização e evidência de resultado. [DOC_C §1.4]
5. **Multi-fonte exige identidade `(source,stream,timestamp,sequence)`** antes
   do segundo escritor num store; leitura "último estado" filtrada por fonte,
   nunca `ORDER BY id` global. [DOC_C §7.5]
6. **Registros contaminados permanecem** — corrige-se a leitura, não o ledger
   (historicidade). [DOC_C §7.5]
7. **Ética no caminho de execução, não wrapper de saída** — manter gate/care/
   recusa como restrições estruturais (fail-closed opcional já existe). [V49
   §11.1–11.2; DOC_A §8]
8. **Ambíguo ≠ bloqueado:** sustentar indeterminacy (`sustain_uncertain`) em
   vez de fechamento binário — já vigente no tracer, estender a novos
   classificadores. [V49 §4.2–4.3, §11.2]
9. **Artefatos publicáveis levam envelope** (schema_version, producer_commit,
   generated_at_utc, metric_definitions, limitations). [DOC_C §8.3]
10. **Analogia paga pedágio:** termo clínico/físico novo só permanece se superar
    baseline simples em predição/controle/auditabilidade. [DOC_A §5]
11. **Liveness ≠ readiness:** após swap reload, sonda funcional antes de
    declarar brain pronto. [DOC_C §7.4/§9.1]
12. **Skeleton público × sujeito local:** docs do worker publicam fórmulas/
    schemas; witness, soma sqlite e soul vivos permanecem soberanos locais.
    [V49 §12.2 + licença]

## 9. English summary

Map of three canonical docs — DOC_A (HSP manifesto: architectural hypothesis,
stratum discipline L1–L4, analogy toll), DOC_C (experimental: VBKF, S_meta
score, regime→policy conventions, F2b real fault injection, multi-source event
identity, intervention declarations), V49 (RNFCI: immutable history, dodecatad
faces with preserved indeterminacy, somatic cost, ethics as structural
constraints). Worker already implements the historical/audit, somatic-telemetry,
affect-ladder, governance and continuity surfaces; S_meta-like scoring, latent
estimation, missingness-as-feature, change-point pre-alert and artifact
envelopes are mappable; the 464D author mesh, canonical daemons, BVGI and
GWT/SDM are out of scope. Twelve derived guidelines above, each cited to its
authorizing section.
