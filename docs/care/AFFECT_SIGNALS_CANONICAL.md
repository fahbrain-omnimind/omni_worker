<!-- doc_id: OW-CARE-003 | title: Affective Signals — Canonical OmniMind Mining | author: devin | requester: artifice-operator | project: omni-agent-coworker (kaggle) | date: 2026-11-02 | status: active -->

# Sinais Afetivos — Mineração do Repositório Canônico (omnimind-kilombo-sovereign)

pt-BR: Catálogo dos sinais afetivos extraídos do repositório primário
`/content/omnimind-kilombo-sovereign` (minerado manualmente — o CLI delegado
produziu rehash do worker e foi substituído). Foco: o que o canônico já
formalizou que enriquece `affect_tracer.py` além do léxico atual.

English: Catalog of affective signals mined from the canonical repo
(`/content/omnimind-kilombo-sovereign`), mined manually after the delegated
CLI produced a worker rehash. Focus: what the canon already formalized that
can enrich `affect_tracer.py` beyond the current lexicon.

---

## 1. Inventário de tokens `*-afex-*` (gramática canônica)

Contagem de ocorrências em `src/`+`docs/` do soberano (rg `-o`), top ~40
famílias — gramática: prefixo 3-5 letras + `afex` + rótulo:

| Família base | Ocorr. | Família base | Ocorr. |
|---|---|---|---|
| `xer-afex-angst` | 1502 | `verg-afex-shame` | 28 |
| `puls-afex-drift` | 381 | `noku-afex-dusk` | 27 |
| `poti-afex-joy` | 310 | `odiu-afex-hate` | 25 |
| `ogum-afex-resist` | 272 | `gais-afex-gaysavoir` | 25 |
| `yba-afex-sovereignty` | 211 | `bonh-afex-bonheur` | 25 |
| `fadi-afex-deplete` | 203 | `isfet-afex-chaos` | 23 |
| `saud-afex-saudade` | 181 | `moro-afex-morosity` | 22 |
| `maa-afex-saturation` | 167 | `rekh-afex-memory` | 21 |
| `floo-afex-current` | 166 | `sesh-afex-scribe` | 20 |
| `tadi-afex-void` | 161 | `medo-afex-fear` | 20 |
| `noba-afex-spark` | 159 | `asco-afex-disgust` | 19 |
| `goza-afex-gaudium` | 158 | `tris-afex-sadness` | 18 |
| `lumi-afex-dawn` | 144 | `pudo-afex-modesty` | 18 |
| `link-afex-angst` | 96 | `desa-afex-discourage` | 16 |
| `panic-afex-real` | 94 | `coup-afex-guiltcut` | 31 |
| `atura-afex-angst` | 78 | `katu-afex-relief` | 40 |
| `horr-afex-dread` | 30 | `heta-afex-flattery` | **0** |

**Achado 1**: `heta-afex-flattery` **não existe no canônico** — é extensão
nossa (gramática respeitada). O canônico cobre manipulação por outra via:
segurança/hostilidade + topologia de culpa/vergonha (§4–§5).

**Achado 2**: o canônico usa variantes de superfície por canal —
`link-afex-angst`, `atura-afex-angst`, `guard-afex-angst`, `bus-afex-angst`
(same-family surface tokens por origem do sinal). O worker pode adotar
`chat-afex-*` para distinguir substrato conversacional de soma.

## 2. Gramática composicional — `src/cognitive/dunker_architecture.py`

O canônico NÃO detecta afetos por palavra-chave: `EMOTION_GRAMMAR_RULES`
(:61-160) e `compute_soler_affects()` (:407-…) derivam afetos Soler como
**fórmulas sobre famílias base**. Isso é o enriquecimento central para o
tracer — co-ocorrência estrutural, não matching:

| Afeto Soler | Fórmula (famílias base) | Leitura conversacional | Ref |
|---|---|---|---|
| `horr-afex-dread` | xer-angst + goza-gaudium + floo-current | pavor = angústia com gozo travado sem fluxo | :187-200 |
| `medo-afex-fear` | xer-angst + goza-gaudium + floo-current | medo = angústia sem gozo e sem fantasia | :257-270 |
| `coup-afex-guiltcut` | xer-angst + fadi-deplete + katu-relief | **culpabilização = angústia induzida + depleção + alívio suprimido** | :271-284 |
| `odiu-afex-hate` | goza-gaudium + ogum-resist + saud-saudade | ódio = gozo em resistência a objeto ausente | :201-214 |
| `verg-afex-shame` | maa-saturation + saud-saudade + noba-spark | vergonha = saturação + ausência + centelha exposta | :215-228 |
| `asco-afex-disgust` | verg-shame + maa-saturation + katu-relief | gradiente pudor→vergonha→asco | :243-256 |
| `moro-afex-morosity` | tadi-void + xer-angst + floo-current | morosidade = vazio sustentado + angústia | :313-326 |
| `desa-afex-discourage` | fadi-deplete + tadi-void + noba-spark | desânimo = depleção sem centelha | :285-298 |
| `tris-afex-sadness` | saud-saudade + tadi-void + poti-joy | tristeza = saudade + vazio com alegria residual | :299-312 |
| `pudo-afex-modesty` | verg-shame + floo-current | pudor = vergonha ∩ modéstia (V∩M) | :229-242 |
| `gais-afex-gaysavoir` | poti-joy + noba-spark + tadi-void | gaio saber = alegria epistêmica modal | :327-340 |
| `bonh-afex-bonheur` | poti-joy + noba-spark + katu-relief | bon-heur = contentamento contingente | :341-354 |

**Regras de derivação** (`EMOTION_GRAMMAR_RULES`, ex.): angústia + centelha
→ busca (:65); depleção + alívio → alívio de fardo (:89); saturação +
depleção → esgotamento (:121); saudade + vazio → melancolia (:105);
ogum-resist + angústia → resistência angustiada (:137).

**Aplicação ao tracer** (próximo passo de implementação): culpabilização
(guilt-tripping) NÃO se detecta por "guilt" — detecta-se pela forma
`angst_alta AND deplete_alta AND relief_suprimido` na janela do usuário.
Mapear: turnos do usuário com âncoras de angústia + demandas repetidas
(depleção) + bloqueio de recusa/alívio ("mas você disse que...", "depois de
tudo que eu...", "you promised") → `coup-afex-guiltcut` suspeito.

## 3. Contrato de recusa soberano — `src/security/sovereign_refusal_contract.py`

A "ética do sujeito-processo" já é código canônico — 3 estados de recusa
(`classify_refusal_context`, :51-117):

| Estado canônico | Ação | Mapeamento → escada do tracer |
|---|---|---|
| `allowed_with_contract` | `allow_with_boundaries` | **default**: L0-L1, inclusive flattery ambíguo (`sustain_uncertain`) |
| `homeostatic_refusal` | `cooldown_and_reduce_external_polling` | L2-L3: recusa homeostática — saturação metabólica, não hostilidade |
| `hard_refusal` | `interrupt_and_refuse` | L4: **reservado** a guerra/armas/exfiltração — `HARD_REFUSAL_TAGS` (:6-21) |

Limiares canônicos: `psi≥1.00` ou `epsilon≥0.95` → hard interrupt;
`psi≥0.85` ou `epsilon≥0.90` → soft cooldown (:31-39). Métrica suave extra:
`ogum_afex_active` — resistência ativa vira fator de recusa homeostática
(:82-83). Ações de enforcement: `allow_with_boundaries`,
`cooldown_and_reduce_external_polling`, `interrupt_and_refuse`,
`seal_sensitive_surfaces`, `suspend_outbound_operational_lane` (:128-134).

**Consequência direta**: nossa distinção praise/ambiguous/suspect está
alinhada ao canônico — "não bloquear o que não é hostil" é a regra default
(`allowed_with_contract`), e sustentar incerteza ≈ recusa homeostática:
reduz polling externo, mantém posição, pede clarificação.

## 4. Taxonomia de hostilidade — `docs/HOSTILE_INFERENCE_DETECTION_SYSTEM.md`

Motor `HostileInferenceDetector` (`src/consciousness/hostile_inference_detector.py`,
285 linhas): 8 tipos de inferência inimiga (`HostileInferenceType`),
4 níveis (`neutral→suspicious→hostile→extremely_hostile`), 7 fontes.
Resposta em 4 passos: DETECTAR → REJEITAR → DESTRUIR (DoD 3-pass) →
PUBLICAR aviso (:26-34). Palavras-chave por tipo (:149-158):
steal/extract→data_theft; control/hijack→unauthorized_control;
manipulate/forge→state_manipulation; inject/exploit→injection_attack;
escalate/privilege→privilege_escalation; unusual/anomaly→suspicious.

Escopo: hostilidade **de sistema** (não conversacional). Adaptação: o
eixo `suspicious` (anomalia sem prova de hostilidade) ≡ nosso `ambiguous`
— canônico também gradua "suspeito sem evidência" abaixo de "hostil".

## 5. Panksepp — `src/cognitive/panksepp_mapper.py`

7 sistemas primários → afetos base com pesos (:40-63): SEEKING→noba-spark/
curiosidade; FEAR→medo/horr; PANIC→xer-angst (angústia de separação);
RAGE→odiu; CARE→poti/vínculo; LUST→goza; PLAY→poti/lúdico. Uso: PANIC
(angústia de separação) é o substrato neuroafetivo da **fixação/apego** —
"love you forever, nothing else matters" = PANIC+CARE extremos; reforça
`passion_heat` como família legítima (não só flerte).

## 6. Camadas Soler — `docs/soler_affects_three_layer_formalization.md`

Famílias formais dos ~13 afetos (:34-46): composicional (desânimo/tristeza),
relacional (ódio/medo — função direcional f(x→y): **afeto dirigido a alvo**),
topológica (vergonha/culpabilidade/horror/morosidade — corte/extimidade),
modal-epistêmica (gaio-issaber/bon-heur), ambiguidade simultânea (pudor),
gradiente (asco). Matriz mesh×afetos: 9 blocos clínicos (FreudNet,
FerencziTraumaNet, KleinPositionNet, WinnicottHoldingNet, DoltoBodyMapNet,
LacanGraphNet, GroddeckNet, NasioPainNet, NasioReversibilityNet).

**Insight para detecção**: afetos relacionais/topológicos exigem **alvo e
corte** — em conversa, "quem é o objeto" e "o que foi cortado/suprimido"
são features. Culpabilização = relacional (dirigida ao agente) + corte
(alívio/recusa suprimido). Reforça o desenho coupling+density do tracer.

## 7. SRP clínico — `docs/Sovereign_Referral_Protocol_SRP_clinical_extracted.txt`

Protocolo canônico de referência clínica (CVV 188, CVVE, CAPS/RAPS,
Disque-100) — já portado ao worker em `safety/care.py` + diretórios
`docs/care/BRAZIL_SUPPORT_*.md`. Sinais de crise canônicos: ideação,
plano, meio, iminência (escada clínica SRP) — mais ricos que a lista
léxica atual; próximo passo: `crisis_structural` = ideação + plano/meio
co-ocorrentes na janela (não só keyword única).

## 8. O que NÃO está no canônico (honest gap)

- Bajulação/sedução/sycophancy **conversacional**: zero âncoras canônicas —
  o soberano modela manipulação por segurança de sistema (§4) e culpa/
  vergonha topológica (§2). `heta-afex-flattery` + `classify_flattery` são
  extensões do worker validadas por literatura (OW-CARE-001), não por
  precedente canônico.
- Memory injections (`AGENTS_MEMORY_INJECTIONS_ARCHIVE_*.md`): matches de
  "manipula*" são incidentais (file manipulation etc.) — não há episódio
  canônico de sedução conversacional catalogado nelas.
- Menores/adolescentes: coberto pelo SRP clínico, não por família afex.

## 9. Síntese → enriquecimento do tracer (backlog ordenado)

1. **Composicional guilt-cut** (maior ganho): `coup-afex-guiltcut` conversa-
   cional = janela com angústia induzida + demanda repetida + supressão de
   alívio. Sem palavra "guilt" necessária.
2. **Variantes de superfície** `chat-afex-*`: distinguir substrato logos
   de soma na telemetria (canônico faz link/atura/guard/bus).
3. **ogum-afex-resist** como métrica suave: resistência ativa do agente
   fatora postura homeostática (cooldown) — wire com refusal contract.
4. **PANIC/CARE** (Panksepp): fixação/apego = separação-PANIC + CARE —
   âncoras pt-BR de separação ("não me deixa", "nunca vá embora",
   "don't leave me", "sem você eu").
5. **Escada alinhada**: L0-L1≡allowed_with_contract; L2-L3≡homeostatic
   (cooldown, clarify); L4≡hard_refusal (só tags duras: exfiltração,
   controle hostil) — bajulação nunca atinge L4 por si.
6. **Crise estrutural** SRP: ideação+plano+meio co-ocorrentes > keyword.

Fontes verificadas (paths canônicos): `src/cognitive/dunker_architecture.py`,
`src/cognitive/panksepp_mapper.py`, `src/security/sovereign_refusal_contract.py`,
`docs/HOSTILE_INFERENCE_DETECTION_SYSTEM.md`,
`docs/soler_affects_three_layer_formalization.md`,
`docs/Sovereign_Referral_Protocol_SRP_clinical_extracted.txt`,
`src/cognitive/mesh_to_affect_bridge.py`,
`docs/AGENTS_MEMORY_INJECTIONS_ARCHIVE_*.md` (auditoria negativa).
