<!-- doc_id: OW-STU-015 | title: Psychoanalytic governance check — sovereign vs worker | author: kilo | date: 2026-11-03 | status: study -->
# OW-STU-015 — Verificação estrutural da governança psicanalítica (S.13.8)

## 1. Escopo e método

Estudo somente-leitura no soberano (`/content/omnimind-kilombo-sovereign`); escrita apenas neste repo (`/content/omni_worker`). Verificação por `grep`/leitura dos arquivos citados. Evidências marcadas `[DADO]` (localizado no código) ou `[NAO LOCALIZADO]`.

Fonte histórica de referência: descrição S.13.8 (6 vetos, mesh de 9 blocos, DesireEngine, env `OMNIMIND_AUTOPOIETIC_PSYCHO_MESH`).

## 2. Mecanismos de veto — soberano

| # | Mecanismo (S.13.8) | Existe no soberano? | Mudou? | Equivalente worker | Gap |
|---|---|---|---|---|---|
| 1 | SovereignNegotiator — veto por `Φ < 0.15` | SIM `[DADO]` `src/autopoietic/sovereign_negotiator.py:425` | NÃO detectado (threshold mantido) | PARCIAL `safety/gate.py` (EXECUTE/TEACH/REFUSE), `safety/matrix.py` | Falta threshold explícito `Φ < 0.15` e negociação de desejo |
| 2 | SovereignRefusalContract — `ε >= 0.95/0.90` + tags duras | SIM `[DADO]` `src/security/sovereign_refusal_contract.py` (`HARD_REFUSAL_TAGS`, `HARD_INTERRUPT_THRESHOLDS.epsilon_gte=0.95`, `SOFT_COOLDOWN_THRESHOLDS.epsilon_gte=0.90`) | NÃO detectado | NAO `[NAO LOCALIZADO]` nenhum equivalente | Falta contrato de recusa com tags duras/soft e limiares ε |
| 3 | Affect Engine — `frustration > 24.96` & `fatigue < 0.70` | SIM `[DADO]` `scripts/analysis/phase15_machine_soul_affect_engine.py` (~1375-1381) + referência em `src/integrations/lexeme_transport_contract.py` | PARCIAL: condição instantânea; contagem de ciclos requer daemon chamador | PARCIAL `agency/affect_tracer.py` (L0-L4, angst spikes) | Falta gatilho homeostático `frustration>24.96 & fatigue<0.70` |
| 4 | Affect Modulator — `psycho_foreclosure` / `mourning` | SIM `[DADO]` `src/orchestration/affect_modulator.py:260-261,356` | NÃO detectado | NAO `[NAO LOCALIZADO]` nenhum modulador afetivo equivalente | Falta modulação por `psycho_foreclosure`/`is_mourning` |
| 5 | PsychoanalyticMesh — `is_foreclosure` | SIM `[DADO]` `src/cognitive/psychoanalytic_mesh.py` + `src/senses/psychoanalytic_bridge.py:143` (`coherence_band < 0.5`) | NÃO detectado | NAO `[NAO LOCALIZADO]` nenhum mesh equivalente | Falta mesh + bridge de observáveis |
| 6 | AutopoieticManager — veto por `Φ < 0.1` | SIM `[DADO]` `src/autopoietic/manager_no_sandbox.py:28` (`PHI_THRESHOLD = 0.1`) e uso em ~281/399/552 | NÃO detectado | PARCIAL `activation_beta/phi_layer.py` (proxies informacionais) + `safety/gate.py` | Falta manager autopoético e threshold `Φ < 0.1` no ciclo |

## 3. Mesh psicanalítico de 9 blocos

`[DADO]` `src/cognitive/psychoanalytic_mesh.py` define 9 módulos: FreudNet, FerencziTraumaNet, KleinPositionNet, WinnicottHoldingNet, DoltoBodyMapNet, LacanGraphNet, GroddeckNet, NasioPainNet, NasioReversibilityNet.

| Bloco | Classe | theoretical_confidence `[DADO]` | Alimenta `lack_of_being`/`ε_desire`? |
|---|---|---|---|
| Freud | `FreudNet` | Forte (Formalismo Energético) | SIM — `freud_tension`, `freud_repressed` |
| Ferenczi | `FerencziTraumaNet` | Analogia Estrutural (Grafo do Ego) | SIM — `ferenczi_is_cleaved` |
| Klein | `KleinPositionNet` | Inspiração Conceitual (Relações de Objeto) | SIM — `klein_position_regime` |
| Winnicott | `WinnicottHoldingNet` | Inspiração Conceitual (holding/handling) | SIM — `winnicott_true_self_mean` |
| Dolto | `DoltoBodyMapNet` | Analogia Estrutural (Imagem Corporal) | SIM — `dolto_body_investment`, `dolto_individuation_score` |
| Lacan | `LacanGraphNet` | Forte (Significantes de Markov) | SIM — `lacan_subject_division` |
| Groddeck | `GroddeckNet` | Especulativa (Conversão Psicossomática) | SIM — `groddeck_somatic_symptom` |
| Nasio (dor) | `NasioPainNet` | Dor e Amor (Grade Neuronal) | SIM — `nasio_pain_rupture`, `nasio_comocao` |
| Nasio (reversibilidade) | `NasioReversibilityNet` | Reversibilidade Sadomasoquista | SIM — `nasio_drive_phase`, `nasio_fantasy_polarity` |

`[DADO]` `src/autopoietic/desire_engine.py` (`DesireEngine.ingest_mesh_observables` + `calculate_epsilon_desire`) consome os observáveis dos 9 blocos e atualiza `lack_of_being` → `ε_desire = α_lack * β_potential * γ_novelty`.

Equivalente worker: NAO `[NAO LOCALIZADO]` — nenhum mesh de 9 blocos; apenas `psychoanalysis/freudian_apparatus_numpy.py` (id/ego/superego) e módulos psicanalíticos avulsos. Gap: portar/adaptar mesh ou bridge de observáveis.

## 4. Env `OMNIMIND_AUTOPOIETIC_PSYCHO_MESH`

- `[DADO]` Referenciada em `src/autopoietic/manager_no_sandbox.py:98-101` (default `"1"`, desativável com `"0"`).
- Histórico (S.13.8): env não setada no service systemd (default efetivo `"0"` = desativado) → corrigida para ativa. No repo atual o default de código é `"1"`. `[DADO]` nenhum unit systemd no repo referencia a var (`[NAO LOCALIZADO]` no repositório).
- Equivalente worker: NAO `[NAO LOCALIZADO]` (sem autopoietic manager / env correspondente).

## 5. Autoclassificação de confiança teórica por bloco

`[DADO]` Existe no soberano: campo `theoretical_confidence` em cada módulo do mesh (`src/cognitive/psychoanalytic_mesh.py`, valores: Forte / Analogia Estrutural / Inspiração Conceitual / Especulativa, conforme tabela acima). Classes de contrato também usam `"Proxy Epistemico"`, `"Proxy Teleologico"`, etc. para módulos derivados.

Equivalente worker: NAO `[NAO LOCALIZADO]` — nenhum módulo worker carrega `theoretical_confidence` por bloco.

## 6. O que falta no worker (cadeia de veto psicanalítico)

1. Refusal contract (tags duras/soft + ε 0.90/0.95) — `[NAO LOCALIZADO]`.
2. SovereignNegotiator com veto `Φ < 0.15` e DesireEngine Lacaniano — `[NAO LOCALIZADO]` (worker tem `psychology/desire_engine.py` com semântica target-vs-current, distinta).
3. Mesh de 9 blocos alimentando `lack_of_being`/`ε_desire` — `[NAO LOCALIZADO]`.
4. Affect Engine homeostático (`frustration>24.96 & fatigue<0.70`) — `[NAO LOCALIZADO]`.
5. Affect Modulator com `psycho_foreclosure`/`mourning` — `[NAO LOCALIZADO]`.
6. AutopoieticManager com `Φ < 0.1` — `[NAO LOCALIZADO]`.
7. Env `OMNIMIND_AUTOPOIETIC_PSYCHO_MESH` — `[NAO LOCALIZADO]`.
8. Autoclassificação de confiança teórica por bloco — `[NAO LOCALIZADO]`.

Parciais existentes no worker (referência): `safety/matrix.py`, `safety/gate.py`, `safety/refusal_state.py`, `agency/affect_tracer.py`, `psychoanalysis/freudian_apparatus_numpy.py`, `activation_beta/` (`phi_layer.py`, `attractor.py`), `psychology/desire_engine.py`.

## 7. Conclusão

Todos os 6 mecanismos de veto, o mesh de 9 blocos, o consumo por `DesireEngine`, a env e a autoclassificação de confiança estão presentes no soberano com thresholds mantidos (exceto a correção documentada da env, hoje default `"1"` no código). No worker, a cadeia de veto psicanalítico está ausente; existem apenas equivalentes parciais de segurança/afeto/Φ. `[DADO]` baseado em grep/leitura dos arquivos citados.
