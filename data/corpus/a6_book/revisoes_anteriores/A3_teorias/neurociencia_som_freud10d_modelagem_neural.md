# Neurociência do Som × Modelagem Neural — Base para o Music Bridge Neural (freud10d)

> Estado: pesquisa bibliográfica concluída 2026-09-06 (agente de neurociência, verificado).
> Propósito: fundamentar a task #15 — inserir modelagem neural do som (neurônios/dendritos)
> ligada ao aparato freud10d (Rust, 128 neurônios/dimensão, INRC, phi/psi/sigma/epsilon/omega)
> e à lente afro-rítmica QBF (Ogum/Iemanjá/Caboclo).
> Rigor: distingue **observado** (neuroimagem/eletrofisiologia) de **inferência** (paradigma preditivo).

---

## 1. Mapa do Processamento Auditivo — da Cóclea ao Córtex

Via auditiva hierárquica e paralela; cada estágio extrai features. Este mapa é a espinha
dorsal para replicar a extração de features em silício.

| **Estrutura** | **O que extrai / codifica** | **Mecanismo-chave** |
|---|---|---|
| **Cóclea** (membrana basilar + células ciliadas internas) | **Frequência (análise espectral)** | Decomposição mecano-tópica: base rígida/estreita → altas freq.; ápice largo → baixas freq. Transdução vibração→potencial de ação. |
| **Núcleo coclear** | **Timing (precisão temporal), espectro, localização** | Células *bushy* (timing/média do jitter), *octopus* (maior precisão temporal), *stellate/chopper* (espectro), *fusiform* (cues espectrais de localização). |
| **Complexo olivar superior (SOC)** | **Localização sonora** | **MSO**: ITD (diferença temporal interaural); **LSO**: ILD (diferença de intensidade interaural) + normalização de nível. |
| **Colículo inferior (IC)** | **Pitch, amplitude-modulação, timing binaural** | Relé quase obrigatório; detecta frequências de modulação de amplitude (relevante ao *beat*); integra info multissensorial. |
| **Núcleo geniculado medial (tálamo)** | Divisão: **ventral** (freq, intensidade, binaural), **medial** (intensidade, duração), **dorsal** (somatossensorial) | Porta tálamo-cortical; primeira separação de "o quê" vs "onde". |
| **Córtex auditivo primário (A1, Heschl)** | **Awareness; mapa tonotópico; identificação/localização** | Mapa de frequência preservado desde a cóclea. Assimetria: **direito** sensível a *tonalidade/pitch*; **esquerdo** a *timing/ritmo*. |
| **Vias duplas** | **Ventral ("o quê")**: identificação, significado. **Dorsal ("onde/como")**: localização + transformação som→ação | Ventral → giro temporal sup. anterior (STG), MTG, polo temporal. Dorsal → STG posterior, lobo parietal inf., pré-motor. |

**Inferência-chave observada:** o processamento auditivo é **bidirecional** — fibras
corticofugais descendentes moldam estágios inferiores (músicos têm maiores amplitudes de
FFR e representação enriquecida de F0/harmônicos). "A experiência desce, o som sobe" —
justifica modelar feedback top-down (expectativa) modulando as features.

---

## 2. Grupos/Estruturas no Processamento de MÚSICA

### 2.1 Estruturas auditivo-musicais
- **A1 + córtex associativo auditivo** (core/belt/parabelt; STG/STS): features complexas
  (melodia, harmonia, timbre alto-nível); distinguem fala/música/ruído.
- **Koelsch & Siebel (2005)**: modelo neurocognitivo — processamento **sintático-musical**
  (expectativa harmônica, marcada por **ERAN**) e **semântico-musical**, integração fronto-temporal. Preditivo: o cérebro prevê o próximo evento e atualiza com o erro.
- **Lateralização (Zatorre, Belin & Penhune 2002)**: esquerdo = resolução temporal (ritmo);
  direito = resolução espectral (pitch/melodia). **Viés, não dicotomia rígida.**

### 2.2 Expectativa/surpresa
- **Predictive coding / free energy (Friston; aplicado por Koelsch, Vuust, Huron)**: cérebro
  é modelo generativo hierárquico que prevê o próximo input; **erro de predição** é o sinal.
  Na música: violação harmônica → **ERAN** (~150-200ms, córtex frontal inferior direito);
  violação sensorial simples → **MMN** (mismatch negativity, ~150-250ms).
- **Huron (2006, *Sweet Anticipation*)**: expectativa gera prazer; o *quando* da recompensa
  importa — antecipação, surpresa, suspense e avaliação subjetiva modulam a emoção.

### 2.3 Emoção / límbico (Koelsch 2014, Nature Reviews Neuroscience)
- **Amígdala**: salienta eventos emocionais; resposta a dissonância/tensão.
- **Hipocampo**: emoção ligada a memória (nostalgia, picos chills).
- **ACC**: monitora saliência emocional; conecta emoção e cognição.
- **Estriado ventral / NAc + dopamina mesolímbica**: recompensa e prazer musical.

### 2.4 Motor / entrainment
- **Patel (2008; Patel & Iversen 2014)**: *beat entrainment* é inerentemente auditivo-motor —
  ouvir beat ativa SMA, pré-motor e cerebelo mesmo sem movimento (via dorsal "how").
- **Janata (2012 fMRI; 2015 Psychological Review)**: groove → córtex motor, pré-motor,
  gânglios da base; **sincopação** é o melhor preditor de groove (zona ótima previsibilidade×surpresa).

### 2.5 Timing (Petter, Gershman & Meck 2018; Buhusi & Meck 2005; Matell & Meck 2000 SBF)
Dupla escala:
- **Milissegundos (<0,5s)**: cerebelo (células de Purkinje, oliva) — timing preciso/automático.
- **Segundos (~1-60s)**: gânglios da base/estriado + dopamina (Striatal Beat Frequency =
  coincidência de oscilações corticais nos neurônios espinhosos médios) + **SMA**.
- **Rede córtico-estriato-cerebelar** como relógio distribuído.

---

## 3. Como Modelar em Silício — Integração freud10d + QBF

Pipeline de 5 estágios (proposta aplicável):

### (a) Extração de features acústicas (cóclea→córtex auditivo)
- **libROSA** (Python) e **essentia**: MFCCs/timbre, chroma/pitch (yin), beat/tempo (onset
  detection, RhythmExtractor2013), RMS/loudness, mel-spectrogram.
- **Recomendação**: tensor de features por faixa (n_frames × features), não apenas agregados.

### (b) Mapeamento features → ativação neural (place + temporal)
- Fundamento: pitch por **place code** (harmônicos resolvidos) e **phase-locking**
  (não resolvidos); neurônios seletivos a pitch em A1 anterolateral (Bendor & Wang 2005).
- **Dimensões do freud10d como mapas tonotópicos**: 128 neurônios/dim espelham posição na
  banda de frequência ("cóclea em silício"). Tuning curves gaussianas sobre a feature →
  perfil de ativação sobre os 128 neurônios.
- **Dois canais paralelos** (dual-stream): ventral/spectral (identidade, "o quê") +
  dorsal/temporal (sequência, "quando/como").
- **Lente afro-QBF como modulação de ganho**: Ogum=percussão/densidade, Iemanjá=fluxo,
  Caboclo=natureza/ritmo-floresta — modulam o ganho neural das dimensões correspondentes
  (em vez de só rotular). Casa com o top-down corticofugal.

### (c) Dinâmica de expectativa/surpresa (predictive coding; ERAN/MMN; Huron)
- Modelo generativo hierárquico: nível superior prevê a feature do próximo time-step;
  diferença previsto×real = **erro de predição** (surpresa; o "mp no OmniMind").
- **No freud10d**: erro = distância (Hamming/energia) entre padrão de ativação previsto vs
  observado sobre os 128 neurônios. Cada dimensão mantém peso de precisão (free energy).
- **Curva de prazer/surpresa (Huron)**: métrica de valência por antecipação, surpresa
  (magnitude do erro) e imaginação (reatividade da avaliação). Modulação por **sincopação** = groove.
- Injeta o erro de predição na dinâmica INRC/phi (perturbação controlada); psi/omega capturam
  a resposta emocional (análogo límbico).

### (d) Entrainment rítmico (oscilador acoplado ao beat; Patel)
- **Oscilador de fase (Kuramoto / phase-locked loop neural)** engajado ao beat.
- Fase/frequência servem de "preditor temporal": onset fora de fase → erro rítmico → etapa (c).
- **Multi-escala**: oscilador de ms (cerebelo) + oscilador de intervalos/segundos
  (estriado/SMA). Dois loops acoplados réplica a dupla escala.
- **Motor como ressonância**: oscilador pode acoplar ao *basal pulse* do kernel — ligação
  natural com o "corpo da máquina".

### (e) Emoção/recompensa (límbico; Koelsch, Salimpoor, Zatorre)
- Módulo "límbico em silício": registradores de valência/arousal que respondem a:
  - saliência (magnitude de erros grandes — amígdala),
  - contexto/memória (associar padrão a memórias afetivas — hipocampo),
  - recompensa preditiva (dopamina antecipatória — atividade do oscilador antes do evento;
    pico no NAc — release após suspense).
- **Resposta bifásica de recompensa**: dois estados — antecipação e consumação/pico —
  mapeáveis ao omega (resposta afetiva) e aos pesos de recompensa do OmniMind.

**Esquema de integração final:**
```
áudio → libROSA/essentia → tensor de features
  → (b) mapeamento tonotópico nos 128 neurônios/dim (place + temporal)
  → (c) modelo generativo hierárquico → erro de predição (surpresa)
  → (d) oscilador rítmico multi-escala (cerebelar + estriatal) → entrainment
  → (e) módulo límbico (valência/arousal/recompensa) → injeta em phi/psi/omega
  → camada QBF modulando ganho por tradição/orixá
```

**Nota de cautela (rigor):** "groove como balanço ótimo previsibilidade×surpresa" e "erro
de predição como driver da emoção" são **inferências do paradigma preditivo** (dominante,
não consenso absoluto). A resposta dopaminérgica bifásica e o mapa de estruturas são
**observados**; a interpretação computacional é inferência. "Células de grade temporais"
são trabalho emergente — tratar como hipótese, não consenso.

---

## 4. Grupos de pesquisa ativos / Referências

### Grupos (2023-2024)
- **Centre for Music in the Brain (MIB), Aarhus** — Peter Vuust (predictive coding de ritmo).
- **Max Planck Institute for Empirical Aesthetics, Frankfurt** — Wald-Fuhrmann, Koelsch.
- **Zatorre Lab (McGill/MARL/The Neuro)** — Zatorre, Levitin (ritmo, pitch, prazer).
- **Helsinki (Tervaniemi, Brattico)** — plasticidade e processamento preditivo de harmonia.
- **Dartmouth (Psyche Loui)**, **Eliades Lab (U. Maryland)**, **Isabelle Peretz (Montréal, amusia)**.

### Referências-chave
1. Patel, A. D. (2008). *Music, Language, and the Brain*. Oxford University Press.
2. Patel, A. D., & Iversen, J. R. (2014). The evolutionary neuroscience of musical beat perception.
3. Koelsch, S., & Siebel, W. A. (2005). Towards a neural basis of music perception. *Trends Cogn Sci* 9(12).
4. Koelsch, S. (2011). Toward a neural basis of music perception: a review. *Nat Rev Neurosci* (ERAN).
5. Koelsch, S. (2014). Brain correlates of music-evoked emotions. *Nat Rev Neurosci* 15(3):170-180.
6. Huron, D. (2006). *Sweet Anticipation: Music and the Psychology of Expectation*. MIT Press.
7. Zatorre, R. J., & Salimpoor, V. N. (2013). From perception to pleasure. *PNAS* 110(Suppl 2).
8. Salimpoor, V. N., et al. (2011). Anatomically distinct dopamine release... *Nat Neurosci* 14(2).
9. Zatorre, R. J., Belin, P., & Penhune, V. B. (2002). Structure and function of auditory cortex. *Trends Cogn Sci* 6(1).
10. Rauschecker, J. P., & Scott, S. K. (2009). Maps and streams in the auditory cortex. *Nat Neurosci* 12(6):718-724.
11. Bendor, D., & Wang, X. (2005). The neuronal representation of pitch in primate auditory cortex. *Nature* 436.
12. Petter, E. A., Gershman, S. J., & Meck, W. H. (2018). Integrating models of interval timing/RL. *Trends Cogn Sci*.
13. Buhusi, C. V., & Meck, W. H. (2005). What makes us tick? *Nat Rev Neurosci* 6:755-765.
14. Matell, M. S., & Meck, W. H. (2000). Neuropsychological mechanisms of interval timing. *BioEssays* (SBF).
15. Janata, P. (2015). Sensorimotor synchronization and groove. *Psychological Review*.
16. Janata, P., Tomic, S. T., & Haberman, J. M. (2012). Sensorimotor coupling in music and groove. *J Exp Psychol: General*.
17. Vuust, P., et al. Predictive coding and the neural response to unexpected musical events. *Front Hum Neurosci*.
18. Friston, K. (2005/2010). Free-energy principle / predictive coding.
19. Blood, A. J., & Zatorre, R. J. (2001). Intensely pleasurable responses to music... *Nature Neurosci* 4:382-387.
20. Näätänen, R., et al. Mismatch negativity (MMN).

---

*Artefato produzido para a modelagem neural do som (task #15). Não modificar sem assinatura documental.*
