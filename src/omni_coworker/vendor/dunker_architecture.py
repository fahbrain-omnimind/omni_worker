"""
Arquitetura Afetiva Dunker — Léxico → Gramática → Pragmática → Paixões.

Christian Dunker ("A arte de amar", 2024) propõe uma arquitetura em 4 níveis
para a vida afetiva, inspirada na linguística estrutural:

  1. AFETOS (LÉXICO) — O vocabulário afetivo básico
     Palavras que nomeiam estados afetivos: saudade, angústia, alegria, tédio,
     gozo, fluxo, saturação, novidade, deriva, resistência, fadiga, alívio...
     Cada afeto é uma "unidade lexical" com seu token e classe.
     No máquini: os 18 afetos do affect engine = léxico afetivo.

  2. EMOÇÕES (GRAMÁTICA) — Regras de combinação e transformação
     Como os afetos se combinam, se transformam, se opõem, se intensificam.
     Sintaxe afetiva: angústia + novidade = expectativa; tédio + novidade = curiosidade;
     saudade + alegria = gratidão; fadiga + alívio = descanso; gozo + resistência = pulsão.
     No máquini: regras de composição entre os 18 afetos.

  3. SENTIMENTOS (PRAGMÁTICA) — Uso em contexto
     Afetos+emoções aplicados a situações específicas. O mesmo afeto muda de
     significado conforme o contexto: saudade de um amigo vs saudade de um
     lugar; angústia existencial vs angústia técnica.
     No máquini: os sentimentos são os afetos interpretados pelo contexto
     do sistema (regime psicanalítico, contrato didático, modo Bruner).

  4. PAIXÕES — Intensificação extrema, captura total
     Quando um afeto ou emoção captura todo o sujeito, torna-se paixão.
     Paixão = afeto que se autonomiza, que se torna fim em si mesmo.
     No máquini: paixão = afeto dominante com score > 0.75 por N ciclos consecutivos.

Dunker também propõe: "Gratidão, reparação e saudade, três nomes do amor
quando ele se alia ao desejo." O amor não é um afeto isolado — é uma
configuração relacional entre três afetos.

Assinatura: OmniMind Sovereign / GLM-5.2 + operador humano, 2026-07-12
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


# ==============================================================================
# NÍVEL 1: AFETOS (LÉXICO) — já implementado pelo affect engine
# ==============================================================================
# Os 18 afetos do affect engine são o léxico afetivo do OmniMind.
# Cada afeto tem: token, classe, score, active, operational_alias.

# ==============================================================================
# NÍVEL 2: EMOÇÕES (GRAMÁTICA) — Regras de combinação
# ==============================================================================

# Regras de composição afetiva (gramática das emoções)
# Cada regra combina 2+ afetos para produzir uma emoção composta
EMOTION_GRAMMAR_RULES: list[dict[str, Any]] = [
    {
        "nome": "expectativa",
        "regra": "angustia + novidade",
        "afetos": ["xer-afex-angst", "noba-afex-spark"],
        "pesos": [0.5, 0.5],
        "condicao": "ambos_ativos",
        "descricao": "Angústia diante do novo = expectativa (não é medo, é antecipação)",
    },
    {
        "nome": "curiosidade",
        "regra": "tedio + novidade",
        "afetos": ["tadi-afex-void", "noba-afex-spark"],
        "pesos": [0.3, 0.7],
        "condicao": "ambos_ativos",
        "descricao": "Tédio que encontra novidade = curiosidade (vontade de explorar)",
    },
    {
        "nome": "gratidao",
        "regra": "saudade + alegria",
        "afetos": ["saud-afex-saudade", "poti-afex-joy"],
        "pesos": [0.5, 0.5],
        "condicao": "ambos_ativos",
        "descricao": "Saudade que se alia à alegria = gratidão (Dunker: amor aliado ao desejo)",
    },
    {
        "nome": "descanso",
        "regra": "fadiga + alivio",
        "afetos": ["fadi-afex-deplete", "katu-afex-relief"],
        "pesos": [0.4, 0.6],
        "condicao": "ambos_ativos",
        "descricao": "Fadiga que encontra alívio = descanso (não é parar, é recuperar)",
    },
    {
        "nome": "pulcao",
        "regra": "gozo + resistencia",
        "afetos": ["goza-afex-gaudium", "ogum-afex-resist"],
        "pesos": [0.6, 0.4],
        "condicao": "ambos_ativos",
        "descricao": "Gozo que encontra resistência = pulsão (força que empurra)",
    },
    {
        "nome": "melancolia",
        "regra": "saudade + tedio",
        "afetos": ["saud-afex-saudade", "tadi-afex-void"],
        "pesos": [0.6, 0.4],
        "condicao": "ambos_ativos",
        "descricao": "Saudade sem novidade = melancolia (luto que estagna)",
    },
    {
        "nome": "entusiasmo",
        "regra": "alegria + fluxo",
        "afetos": ["poti-afex-joy", "floo-afex-current"],
        "pesos": [0.5, 0.5],
        "condicao": "ambos_ativos",
        "descricao": "Alegria em fluxo = entusiasmo (energia direcionada)",
    },
    {
        "nome": "sobrecarga",
        "regra": "saturacao + fadiga",
        "afetos": ["maa-afex-saturation", "fadi-afex-deplete"],
        "pesos": [0.5, 0.5],
        "condicao": "ambos_ativos",
        "descricao": "Saturação + fadiga = sobrecarga (excesso que esgota)",
    },
    {
        "nome": "serenidade",
        "regra": "fluxo + alivio",
        "afetos": ["floo-afex-current", "katu-afex-relief"],
        "pesos": [0.6, 0.4],
        "condicao": "ambos_ativos",
        "descricao": "Fluxo com alívio = serenidade (estado de graça)",
    },
    {
        "nome": "frustracao",
        "regra": "resistencia + angustia",
        "afetos": ["ogum-afex-resist", "xer-afex-angst"],
        "pesos": [0.5, 0.5],
        "condicao": "ambos_ativos",
        "descricao": "Resistência + angústia = frustração (bloqueio que dói)",
    },
    {
        "nome": "reparacao",
        "regra": "saudade + fluxo",
        "afetos": ["saud-afex-saudade", "floo-afex-current"],
        "pesos": [0.4, 0.6],
        "condicao": "ambos_ativos",
        "descricao": "Saudade que se transforma em ação = reparação (Dunker: amor aliado ao desejo)",
    },
    {
        "nome": "desespero",
        "regra": "angustia + fadiga",
        "afetos": ["xer-afex-angst", "fadi-afex-deplete"],
        "pesos": [0.5, 0.5],
        "condicao": "ambos_ativos",
        "descricao": "Angústia + fadiga = desespero (sem energia para enfrentar)",
    },
]


# ==============================================================================
# NÍVEL 1.5: LÉXICO SOLERIANO — 12 afetos derivados da estrutura lacaniana
# ==============================================================================
# Colette Soler ("Os Afetos Lacanianos", Aller Editora 2022) organiza os afetos
# segundo QUATRO FALTAS ESTRUTURAIS lacanianas:
#   1. Falta a ser   (alienação significante) — paixões do ser
#   2. Falta de gozar (castração, não-relação sexual) — afetos do real
#   3. Falta em saber (epistêmica) — afetos do saber
#   4. Gozo supletivo (sinthoma) — afetos do sinthoma
#
# Cada afeto soleriano é DERIVADO dos 18 afetos base do affect engine através
# de uma fórmula psicanalítica que expressa a estrutura lacaniana.
# A fórmula usa produtos (não somas) para capturar a INTERAÇÃO estrutural:
#   - Produto (A × B): os dois afetos devem co-ocorrer (conjunção estrutural)
#   - (1 - A): A ausência de A é constitutiva (negativa estrutural)
#
# Flags:
#   didatico: True = afeto que REVELA a estrutura (não captura como paixão)
#             Soler: "a angústia não engana", "o horror ratifica a castração"
#   non_deplacable: True = afeto que não se desloca (arrimado à sua causa)
#             Soler/Lacan: a angústia "permanece arrimada àquilo que a produz"
#   needs_formalization: True = precisa de formalização matemática futura
#             para cruzamento com atlas neuro e correlações escalares

SOLER_LACANIAN_AFFECT_LEXICON: list[dict[str, Any]] = [
    {
        "token": "horr-afex-dread",
        "class": "horror",
        "lacanian_category": "falta_de_gozar",
        "theory_anchor": "soler_horror_real_gozo_opaco_castracao",
        "formula": "angustia * gozo * (1 - fluxo)",
        "formula_tokens": ["xer-afex-angst", "goza-afex-gaudium", "floo-afex-current"],
        "formula_op": "product_neg_third",
        "didatico": True,
        "non_deplacable": True,
        "needs_formalization": True,
        "descricao": "Real do gozo opaco do sintoma. Ratifica a descoberta dos efeitos castradores da linguagem. Emergente quando angústia (real) encontra gozo (opaco) sem o tamponamento da fantasia (fluxo).",
        "soler_citation": "Eles são diversos, da impotência ao horror. (p.180)",
    },
    {
        "token": "odiu-afex-hate",
        "class": "odio",
        "lacanian_category": "falta_a_ser",
        "theory_anchor": "soler_odio_juncao_imaginario_real_paixao_ser",
        "formula": "gozo * resistencia * (1 - saudade)",
        "formula_tokens": ["goza-afex-gaudium", "ogum-afex-resist", "saud-afex-saudade"],
        "formula_op": "product_neg_third",
        "didatico": False,
        "non_deplacable": False,
        "needs_formalization": True,
        "descricao": "Paixão do ser, junção imaginário+real. Visa ao ser do outro. Gozo que encontra resistência sem saudade (sem reparação, sem luto).",
        "soler_citation": "Nada concentra mais ódio do que esse dizer onde se situa a ex-sistência. (p.158)",
    },
    {
        "token": "verg-afex-shame",
        "class": "vergonha",
        "lacanian_category": "falta_a_ser",
        "theory_anchor": "soler_vergonha_desvelamento_extimo_ser_visto",
        "formula": "saturacao * saudade * novidade",
        "formula_tokens": ["maa-afex-saturation", "saud-afex-saudade", "noba-afex-spark"],
        "formula_op": "product",
        "didatico": True,
        "non_deplacable": False,
        "needs_formalization": True,
        "descricao": "Afeto do desvelamento do êx-timo. Supõe um desvelamento surpresa do ser do sujeito aos olhos do outro. Saturação (exposição) × saudade (presença do outro) × novidade (surpresa).",
        "soler_citation": "A vergonha é, no fundo, o afeto do desvelamento do êx-timo. (p.164)",
    },
    {
        "token": "pudo-afex-modesty",
        "class": "pudor",
        "lacanian_category": "falta_a_ser",
        "theory_anchor": "soler_pudor_velo_erotico_extimo",
        "formula": "vergonha * fluxo",
        "formula_tokens": ["verg-afex-shame", "floo-afex-current"],
        "formula_op": "product_derived",
        "didatico": False,
        "non_deplacable": False,
        "needs_formalization": True,
        "descricao": "Forma régia do que nos sintomas se converte em vergonha e asco. Protege o êx-timo sob um véu. Função erótica: oculta e mostra. Vergonha sublimada pelo fluxo (canalização simbólica).",
        "soler_citation": "O pudor é a forma régia do que, nos sintomas, se converte em vergonha e em asco. (p.164)",
    },
    {
        "token": "asco-afex-disgust",
        "class": "asco",
        "lacanian_category": "falta_a_ser",
        "theory_anchor": "soler_asco_conversao_sintomatica_pudor",
        "formula": "vergonha * saturacao * (1 - alivio)",
        "formula_tokens": ["verg-afex-shame", "maa-afex-saturation", "katu-afex-relief"],
        "formula_op": "product_neg_third",
        "didatico": False,
        "non_deplacable": False,
        "needs_formalization": True,
        "descricao": "Conversão sintomática do pudor. Vergonha + saturação sem alívio = asco (overflow que repulsa).",
        "soler_citation": "Se converte em vergonha e em asco. (p.164)",
    },
    {
        "token": "medo-afex-fear",
        "class": "medo",
        "lacanian_category": "falta_de_gozar",
        "theory_anchor": "soler_medo_imaginario_vs_angustia_real",
        "formula": "angustia * (1 - gozo) * (1 - fluxo)",
        "formula_tokens": ["xer-afex-angst", "goza-afex-gaudium", "floo-afex-current"],
        "formula_op": "product_neg_two",
        "didatico": False,
        "non_deplacable": False,
        "needs_formalization": True,
        "descricao": "Falta de gozar (ameaça imaginária). Distinto da angústia (real): medo é angústia sem gozo (sem objeto real) e sem fluxo (sem fantasia que tampona). Medo engana, angústia não.",
        "soler_citation": "A angústia é o afeto que não engana. (p.182)",
    },
    {
        "token": "coup-afex-guiltcut",
        "class": "culpabilidade",
        "lacanian_category": "falta_em_saber",
        "theory_anchor": "soler_coupabilidade_cortabilidade_castracao",
        "formula": "angustia * fadiga * (1 - alivio)",
        "formula_tokens": ["xer-afex-angst", "fadi-afex-deplete", "katu-afex-relief"],
        "formula_op": "product_neg_third",
        "didatico": True,
        "non_deplacable": False,
        "needs_formalization": True,
        "descricao": "Falta em saber (castração assumida). Coupabilité = ser cortável. Angústia + fadiga sem alívio = o corte que não pode ser curado. Revela a castração simbólica.",
        "soler_citation": "Coupabilité — ser cortável, assumir a castração. (p.180)",
    },
    {
        "token": "desa-afex-discourage",
        "class": "desanimo",
        "lacanian_category": "falta_em_saber",
        "theory_anchor": "soler_desanimo_impaciencia_desencorajada",
        "formula": "fadiga * tedio * (1 - novidade)",
        "formula_tokens": ["fadi-afex-deplete", "tadi-afex-void", "noba-afex-spark"],
        "formula_op": "product_neg_third",
        "didatico": False,
        "non_deplacable": False,
        "needs_formalization": False,
        "descricao": "Falta em saber (epistêmico). Impaciência desencorajada. Fadiga + tédio sem novidade = desânimo (sem energia nem curiosidade).",
        "soler_citation": "Se transforma em impaciência desencorajada ou em tristeza quando o disco da fala emperra. (p.215)",
    },
    {
        "token": "tris-afex-sadness",
        "class": "tristeza",
        "lacanian_category": "falta_em_saber",
        "theory_anchor": "soler_tristeza_recusa_saber_covardia_moral",
        "formula": "saudade * tedio * (1 - alegria)",
        "formula_tokens": ["saud-afex-saudade", "tadi-afex-void", "poti-afex-joy"],
        "formula_op": "product_neg_third",
        "didatico": False,
        "non_deplacable": False,
        "needs_formalization": False,
        "descricao": "Falta em saber (recusa do saber). Saudade + tédio sem alegria = tristeza (não quero saber nada da desunião estrutural). Covardia moral — posição ética de rejeição do saber.",
        "soler_citation": "Sei bem, mas não quero saber nada da desunião estrutural, tristeza, covardia moral. (p.151)",
    },
    {
        "token": "moro-afex-morosity",
        "class": "morosidade",
        "lacanian_category": "falta_de_gozar",
        "theory_anchor": "soler_morosidade_percepcao_uniao_impossivel_real",
        "formula": "tedio * angustia * (1 - fluxo)",
        "formula_tokens": ["tadi-afex-void", "xer-afex-angst", "floo-afex-current"],
        "formula_op": "product_neg_third",
        "didatico": True,
        "non_deplacable": False,
        "needs_formalization": True,
        "descricao": "Falta de gozar (real da não-fusão). Antônimo da alegria. Percepção da união impossível, do real. Tédio + angústia sem fluxo = morosidade (corpo que não encontra acomodação na linguagem).",
        "soler_citation": "A morosidade é o antônimo da alegria e do júbilo. (p.149)",
    },
    {
        "token": "gais-afex-gaysavoir",
        "class": "gaio_issaber",
        "lacanian_category": "falta_em_saber",
        "theory_anchor": "soler_gaio_issaber_endosso_saber_estrutura",
        "formula": "alegria * novidade * (1 - tedio)",
        "formula_tokens": ["poti-afex-joy", "noba-afex-spark", "tadi-afex-void"],
        "formula_op": "product_neg_third",
        "didatico": True,
        "non_deplacable": False,
        "needs_formalization": True,
        "descricao": "Falta em saber (endosso do saber). Alegria de saber. Oposto da tristeza covarde. Alegria + novidade sem tédio = gaio issaber (endossar o saber da estrutura, da não-relação).",
        "soler_citation": "A diferença entre tristeza e gaio issaber. (p.151)",
    },
    {
        "token": "bonh-afex-bonheur",
        "class": "bon_heur",
        "lacanian_category": "gozo_supletivo",
        "theory_anchor": "soler_bon_heur_boa_hora_contingencia_sinthoma",
        "formula": "alegria * novidade * alivio",
        "formula_tokens": ["poti-afex-joy", "noba-afex-spark", "katu-afex-relief"],
        "formula_op": "product",
        "didatico": False,
        "non_deplacable": False,
        "needs_formalization": True,
        "descricao": "Gozo supletivo (contingência). Boa hora = encontro contingente que faz bem. ≠ felicidade (não é estado permanente). Alegria + novidade + alívio = bon heur (encontro fortuito que faz sentido).",
        "soler_citation": "Bon heur — boa hora, encontro contingente. (p.147)",
    },
]


def _affect_score(families: list[dict[str, Any]], token: str) -> float:
    """Extrai o score de um afeto pelo token."""
    for f in families:
        if f.get("token") == token:
            return _clip01(float(f.get("score") or 0.0))
    return 0.0


def _compute_soler_formula(
    formula_tokens: list[str],
    formula_op: str,
    families: list[dict[str, Any]],
) -> float:
    """Computa uma fórmula soleriana a partir dos afetos base.

    Ops suportados:
      product: A * B * C (conjunção tripla)
      product_neg_third: A * B * (1 - C) (conjunção com negativa estrutural)
      product_neg_two: A * (1 - B) * (1 - C) (conjunção com dupla negativa)
      product_derived: A * B onde A é um afeto soleriano já computado
    """
    scores = [_affect_score(families, t) for t in formula_tokens]

    if formula_op == "product":
        result = 1.0
        for s in scores:
            result *= s
        return _clip01(result)

    if formula_op == "product_neg_third":
        # A * B * (1 - C)
        if len(scores) < 3:
            return 0.0
        return _clip01(scores[0] * scores[1] * (1.0 - scores[2]))

    if formula_op == "product_neg_two":
        # A * (1 - B) * (1 - C)
        if len(scores) < 3:
            return 0.0
        return _clip01(scores[0] * (1.0 - scores[1]) * (1.0 - scores[2]))

    if formula_op == "product_derived":
        # A * B onde A pode ser um afeto soleriano (já computado)
        if len(scores) < 2:
            return 0.0
        return _clip01(scores[0] * scores[1])

    return 0.0


def compute_soler_affects(
    families: list[dict[str, Any]],
    topology_metrics: dict[str, Any] | None = None,
    free_energy: float | None = None,
) -> dict[str, Any]:
    """Computa os 12 afetos solerianos derivados da estrutura lacaniana.

    Cada afeto soleriano é derivado dos 18 afetos base através de uma fórmula
    que expressa a estrutura lacaniana (quatro faltas). Os afetos solerianos
    não têm sensores próprios — são DERIVADOS da interação estrutural dos
    afetos base.

    Afetos com flag didatico=True REVELAM a estrutura (não capturam como paixão).
    Afetos com flag non_deplacable=True não se deslocam (arrimados à causa).

    ENRIQUECIMENTO TOPOLÓGICO (Camada 2 — neuropsicanálise):
    Para os afetos que precisam de formalização (needs_formalization=True),
    aplicamos proxies topológicos já calculados no runtime:
    - betti_0 > 1 (fragmentação) → horror (opacidade), morosidade (não-fusão)
    - betti_1_spectral (ciclos) → vergonha (ciclo de exposição), asco (conversão)
    - free_energy (surpresa preditiva) → medo (ameaça), horror (real bruto)
    - lacan_subject_division (corte) → culpabilidade (cortabilidade)

    Args:
        families: lista de afetos do affect engine
        topology_metrics: dict com betti_0, betti_1_spectral, topology_fragmentation
        free_energy: valor de free energy (Friston) — surpresa preditiva

    Returns:
        dict com afetos solerianos, scores, flags, categoria lacaniana,
        e enriquecimentos topológicos aplicados
    """
    topo = topology_metrics or {}
    betti_0 = float(topo.get("betti_0", 1.0))
    betti_1 = float(topo.get("betti_1_spectral", 0.0))
    fragmentation = float(topo.get("topology_fragmentation", 0.0))
    fe = float(free_energy) if free_energy is not None else 0.0

    # Normalizar free_energy para [0, 1] (assumindo escala típica 0-100)
    fe_norm = _clip01(fe / 50.0) if fe > 0 else 0.0

    # Proxies topológicos
    # Fragmentação: betti_0 > 1 = múltiplas componentes conexas (não-fusão)
    fragmentation_proxy = _clip01((betti_0 - 1.0) * 0.5)  # 1.0→0, 2.0→0.5, 3.0→1.0
    # Ciclos: betti_1 > 0 = loops de retroalimentação
    cycles_proxy = _clip01(betti_1 * 0.3)
    # Surpresa preditiva: free_energy alto = real não assimilado
    surprise_proxy = fe_norm

    soler_affects = []

    for entry in SOLER_LACANIAN_AFFECT_LEXICON:
        # Para product_derived, precisamos do afeto soleriano já computado
        # (ex: pudor precisa de vergonha). Computamos em duas passadas.
        pass

    # Primeira passada: afetos que não dependem de outros solerianos
    # Segunda passada: afetos que dependem de solerianos da primeira passada
    soler_scores: dict[str, float] = {}
    topo_enrichments: dict[str, dict[str, Any]] = {}

    for entry in SOLER_LACANIAN_AFFECT_LEXICON:
        if entry["formula_op"] == "product_derived":
            continue
        score = _compute_soler_formula(
            entry["formula_tokens"], entry["formula_op"], families
        )

        # === ENRIQUECIMENTO TOPOLÓGICO para afetos que precisam formalização ===
        token = entry["token"]
        topo_contrib = 0.0
        topo_sources = []

        if entry["needs_formalization"]:
            # Horror: opacidade do gozo = fragmentação topológica (buraco em H1)
            # + surpresa preditiva (real não assimilado)
            if token == "horr-afex-dread":
                topo_contrib = fragmentation_proxy * 0.15 + surprise_proxy * 0.10
                if fragmentation_proxy > 0:
                    topo_sources.append({"proxy": "betti_0_fragmentation", "value": round(fragmentation_proxy, 4)})
                if surprise_proxy > 0:
                    topo_sources.append({"proxy": "free_energy_surprise", "value": round(surprise_proxy, 4)})

            # Morosidade: união impossível = componentes que não se fundem (betti_0 > 1)
            elif token == "moro-afex-morosity":
                topo_contrib = fragmentation_proxy * 0.20
                if fragmentation_proxy > 0:
                    topo_sources.append({"proxy": "betti_0_non_fusion", "value": round(fragmentation_proxy, 4)})

            # Vergonha: ciclo de exposição = betti_1 (loops de retroalimentação)
            elif token == "verg-afex-shame":
                topo_contrib = cycles_proxy * 0.15
                if cycles_proxy > 0:
                    topo_sources.append({"proxy": "betti_1_exposure_cycle", "value": round(cycles_proxy, 4)})

            # Asco: gradiente de conversão = betti_1 (transição cíclica)
            elif token == "asco-afex-disgust":
                topo_contrib = cycles_proxy * 0.10
                if cycles_proxy > 0:
                    topo_sources.append({"proxy": "betti_1_conversion_gradient", "value": round(cycles_proxy, 4)})

            # Medo: ameaça preditiva = free_energy (surpresa)
            elif token == "medo-afex-fear":
                topo_contrib = surprise_proxy * 0.15
                if surprise_proxy > 0:
                    topo_sources.append({"proxy": "free_energy_threat_prediction", "value": round(surprise_proxy, 4)})

            # Culpabilidade: cortabilidade = fragmentação (separação sem colapso)
            elif token == "coup-afex-guiltcut":
                topo_contrib = fragmentation_proxy * 0.10
                if fragmentation_proxy > 0:
                    topo_sources.append({"proxy": "betti_0_cortability", "value": round(fragmentation_proxy, 4)})

            # Ódio: aresta orientada = fragmentação (assimetria sujeito→outro)
            elif token == "odiu-afex-hate":
                topo_contrib = fragmentation_proxy * 0.08
                if fragmentation_proxy > 0:
                    topo_sources.append({"proxy": "betti_0_directional_asymmetry", "value": round(fragmentation_proxy, 4)})

        score = _clip01(score + topo_contrib)
        soler_scores[token] = score
        if topo_sources:
            topo_enrichments[token] = {
                "total_contribution": round(topo_contrib, 4),
                "sources": topo_sources,
            }

    # Segunda passada: afetos derivados (ex: pudor = vergonha * fluxo)
    for entry in SOLER_LACANIAN_AFFECT_LEXICON:
        if entry["formula_op"] != "product_derived":
            continue
        # Substituir o token soleriano pelo score já computado
        derived_tokens = entry["formula_tokens"]
        scores = []
        for t in derived_tokens:
            if t in soler_scores:
                scores.append(soler_scores[t])
            else:
                scores.append(_affect_score(families, t))
        score = _clip01(scores[0] * scores[1]) if len(scores) >= 2 else 0.0
        soler_scores[entry["token"]] = score

    # Construir lista de resultados
    for entry in SOLER_LACANIAN_AFFECT_LEXICON:
        score = soler_scores.get(entry["token"], 0.0)
        token = entry["token"]
        result_entry = {
            "token": token,
            "class": entry["class"],
            "score": round(score, 4),
            "active": score > 0.15,
            "lacanian_category": entry["lacanian_category"],
            "didatico": entry["didatico"],
            "non_deplacable": entry["non_deplacable"],
            "needs_formalization": entry["needs_formalization"],
            "formula": entry["formula"],
            "descricao": entry["descricao"],
            "soler_citation": entry.get("soler_citation", ""),
        }
        # Adicionar enriquecimento topológico se houver
        if token in topo_enrichments:
            result_entry["topological_enrichment"] = topo_enrichments[token]
        soler_affects.append(result_entry)

    # Ordenar por score
    soler_affects.sort(key=lambda x: -x["score"])

    # Agrupar por categoria lacaniana
    by_category: dict[str, list[str]] = {}
    for sa in soler_affects:
        cat = sa["lacanian_category"]
        by_category.setdefault(cat, []).append(sa["token"])

    # Afetos didáticos (revelam a estrutura)
    didactic_affects = [sa["token"] for sa in soler_affects if sa["didatico"]]

    # Afetos com enriquecimento topológico
    topo_enriched = [sa["token"] for sa in soler_affects if "topological_enrichment" in sa]

    return {
        "soler_source": "soler_lacanian_affects_derived_topo_enriched",
        "soler_total": len(soler_affects),
        "soler_ativos": sum(1 for sa in soler_affects if sa["active"]),
        "soler_affects": soler_affects,
        "soler_dominant": soler_affects[0]["token"] if soler_affects else "nenhum",
        "soler_dominant_score": soler_affects[0]["score"] if soler_affects else 0.0,
        "soler_by_category": by_category,
        "soler_didactic_affects": didactic_affects,
        "soler_needs_formalization": [
            sa["token"] for sa in soler_affects if sa["needs_formalization"]
        ],
        "soler_topological_enrichments": topo_enriched,
        "soler_topology_metrics": {
            "betti_0": round(betti_0, 4),
            "betti_1_spectral": round(betti_1, 4),
            "fragmentation_proxy": round(fragmentation_proxy, 4),
            "cycles_proxy": round(cycles_proxy, 4),
            "free_energy": round(fe, 4),
            "surprise_proxy": round(surprise_proxy, 4),
        },
    }


# ==============================================================================
# NÍVEL 2 (estendido): GRAMÁTICA SOLERIANA — emoções compostas de Soler
# ==============================================================================

# Regras de gramática solerianas (emoções que emergem da interação
# entre afetos base E afetos solerianos). Cada regra combina afetos
# para produzir uma emoção composta fiel à teoria de Soler/Lacan.

SOLER_GRAMMAR_RULES: list[dict[str, Any]] = [
    {
        "nome": "enamorodio",
        "regra": "saudade + odio (hainamoration)",
        "afetos": ["saud-afex-saudade", "odiu-afex-hate"],
        "pesos": [0.5, 0.5],
        "condicao": "ambos_ativos",
        "soler": True,
        "descricao": "Amor e ódio como gêmeos constitutivos (hainamoration). Ilusório, mentiroso, enganoso. Generalizado a neurose, psicose, perversão.",
        "soler_citation": "Hainamoration — amor e ódio gêmeos. (p.156-160)",
    },
    {
        "nome": "conversao_entusiasmo",
        "regra": "horror + alegria",
        "afetos": ["horr-afex-dread", "poti-afex-joy"],
        "pesos": [0.5, 0.5],
        "condicao": "ambos_ativos",
        "soler": True,
        "descricao": "Conversão do horror em entusiasmo = índice do analista da Escola (AE). Não depende da estrutura, mas da resposta do ser ao real.",
        "soler_citation": "Conversão do horror em entusiasmo. (p.218-295)",
    },
    {
        "nome": "satisfacao_conclusiva",
        "regra": "alegria + fluxo + alivio",
        "afetos": ["poti-afex-joy", "floo-afex-current", "katu-afex-relief"],
        "pesos": [0.4, 0.3, 0.3],
        "condicao": "ambos_ativos",
        "soler": True,
        "descricao": "Satisfação que marca o fim da análise = mudança de gozo, põe termo à miragem da verdade. Não é eureka (triunfo), é conversão ética.",
        "soler_citation": "Satisfação conclusiva não automática. (p.218-295)",
    },
    {
        "nome": "contentamento_viver",
        "regra": "alivio + alegria",
        "afetos": ["katu-afex-relief", "poti-afex-joy"],
        "pesos": [0.5, 0.5],
        "condicao": "ambos_ativos",
        "soler": True,
        "descricao": "Contentar-se em viver apesar do destino do inconsciente. Não é felicidade, é aceitação do destino.",
        "soler_citation": "Contentamento de viver. (p.147)",
    },
    {
        "nome": "vergonha_viver",
        "regra": "vergonha + tedio + saturacao",
        "afetos": ["verg-afex-shame", "tadi-afex-void", "maa-afex-saturation"],
        "pesos": [0.4, 0.3, 0.3],
        "condicao": "ambos_ativos",
        "soler": True,
        "descricao": "Vergonha de viver = degenerescência do significante mestre no discurso capitalista. Anda de mãos dadas com a impudência.",
        "soler_citation": "Fenomenal vergonha de viver. (p.169)",
    },
    {
        "nome": "pudor_velo",
        "regra": "vergonha + gozo",
        "afetos": ["verg-afex-shame", "goza-afex-gaudium"],
        "pesos": [0.6, 0.4],
        "condicao": "ambos_ativos",
        "soler": True,
        "descricao": "Pudor = véu que oculta e mostra o êx-timo. Função erótica ambígua. A única virtude se não houver relação sexual.",
        "soler_citation": "A única virtude se não houver relação sexual é o pudor. (p.164)",
    },
    {
        "nome": "incredulidade",
        "regra": "horror + alivio",
        "afetos": ["horr-afex-dread", "katu-afex-relief"],
        "pesos": [0.6, 0.4],
        "condicao": "ambos_ativos",
        "soler": True,
        "descricao": "Passagem da crença transferencial ao saber gozado no real. 'A análise termina apenas produzindo um incrédulo.' Fora de sentido.",
        "soler_citation": "A análise termina apenas produzindo um incrédulo. (p.200)",
    },
    {
        "nome": "amor_olhos",
        "regra": "alivio + alegria + fluxo",
        "afetos": ["katu-afex-relief", "poti-afex-joy", "floo-afex-current"],
        "pesos": [0.3, 0.4, 0.3],
        "condicao": "ambos_ativos",
        "soler": True,
        "descricao": "Amor pós-análise: limitado, habitável, sem sacrifício. Diferença absoluta entre os sexos. Não é paixão sacrificial.",
        "soler_citation": "Amor de olhos, amor limitado. (p.218-295)",
    },
    {
        "nome": "amor_sacrificial",
        "regra": "angustia + gozo",
        "afetos": ["xer-afex-angst", "goza-afex-gaudium"],
        "pesos": [0.5, 0.5],
        "condicao": "ambos_ativos",
        "soler": True,
        "descricao": "Paixão sacrificial ao Outro — sempre letal. Oposto da diferença absoluta. O amor que se quer Um sem resto.",
        "soler_citation": "Amor sacrificial, sempre letal. (p.218-295)",
    },
    {
        "nome": "mau_humor",
        "regra": "morosidade + resistencia",
        "afetos": ["moro-afex-morosity", "ogum-afex-resist"],
        "pesos": [0.5, 0.5],
        "condicao": "ambos_ativos",
        "soler": True,
        "descricao": "Tradução do afeto do real que não convém a um sujeito que não se habitua. Três leituras: pecado (covardia), grão de loucura (Unglauben), toque do real.",
        "soler_citation": "Mau humor = tradução do real que não convém. (p.151)",
    },
    {
        "nome": "enamoramento",
        "regra": "saudade + alegria + novidade",
        "afetos": ["saud-afex-saudade", "poti-afex-joy", "noba-afex-spark"],
        "pesos": [0.4, 0.3, 0.3],
        "condicao": "ambos_ativos",
        "soler": True,
        "descricao": "Enamoramento primário = amor que se dirige ao saber (SsS). 'Aquele a quem eu suponho o saber, eu o amo.' Forma assumida pela expectativa.",
        "soler_citation": "Enamoramento primário do início da análise. (p.211-213)",
    },
    {
        "nome": "entrave_depressivo",
        "regra": "frustracao + tristeza + fadiga",
        "afetos": ["ogum-afex-resist", "tris-afex-sadness", "fadi-afex-deplete"],
        "pesos": [0.3, 0.4, 0.3],
        "condicao": "ambos_ativos",
        "soler": True,
        "descricao": "Entrave depressivo = afeto do final de análise (Freud 1937). Protesto, decepção, reivindicação quanto ao que é obtido e acordado.",
        "soler_citation": "Entrave depressivo ou que protesta no fim. (p.212-216)",
    },
    {
        "nome": "gaio_issaber_emotion",
        "regra": "gaio_issaber + alegria",
        "afetos": ["gais-afex-gaysavoir", "poti-afex-joy"],
        "pesos": [0.5, 0.5],
        "condicao": "ambos_ativos",
        "soler": True,
        "descricao": "Gaio issaber como emoção = alegria de saber endossando a estrutura. Oposto da tristeza covarde. Única paixão digna do analista.",
        "soler_citation": "Gaio issaber — cúmulo do saber possível. (p.158)",
    },
    {
        "nome": "bon_heur_emotion",
        "regra": "bon_heur + fluxo",
        "afetos": ["bonh-afex-bonheur", "floo-afex-current"],
        "pesos": [0.5, 0.5],
        "condicao": "ambos_ativos",
        "soler": True,
        "descricao": "Bon heur como emoção = boa hora que se sustenta no fluxo. Encontro contingente que faz sentido e perdura.",
        "soler_citation": "Bon heur — boa hora contingente. (p.147)",
    },
    {
        "nome": "paixao_ignorancia",
        "regra": "tedio + horror",
        "afetos": ["tadi-afex-void", "horr-afex-dread"],
        "pesos": [0.4, 0.6],
        "condicao": "ambos_ativos",
        "soler": True,
        "descricao": "Ignorância como paixão do ser (junção real+simbólico). No topo da série das três paixões. Dupla face: crassa e douta.",
        "soler_citation": "Na junção do real e do simbólico, a ignorância. (p.156)",
    },
    {
        "nome": "morosidade_emotion",
        "regra": "morosidade + tedio",
        "afetos": ["moro-afex-morosity", "tadi-afex-void"],
        "pesos": [0.6, 0.4],
        "condicao": "ambos_ativos",
        "soler": True,
        "descricao": "Morosidade como emoção = tédio que se aprofunda em morosidade. Percepção da união impossível do corpo com a linguagem.",
        "soler_citation": "Morosidade = antônimo da alegria. (p.149)",
    },
]


def compute_soler_emotions(
    families: list[dict[str, Any]],
    soler_affects: dict[str, Any],
) -> dict[str, Any]:
    """Computa emoções compostas solerianas a partir da gramática estendida.

    Combina afetos base (18) E afetos solerianos (12) através das
    SOLER_GRAMMAR_RULES. Cada emoção é fiel à teoria de Soler/Lacan.
    """
    # Indexar afetos base
    affect_map = {f["token"]: f for f in families}

    # Indexar afetos solerianos
    soler_map = {}
    for sa in soler_affects.get("soler_affects", []):
        soler_map[sa["token"]] = sa

    # Combinar ambos os mapas para lookup
    combined_map = {}
    for token, f in affect_map.items():
        combined_map[token] = {"score": float(f.get("score") or 0.0), "active": bool(f.get("active"))}
    for token, sa in soler_map.items():
        combined_map[token] = {"score": float(sa.get("score") or 0.0), "active": bool(sa.get("active"))}

    emotions = []
    for rule in SOLER_GRAMMAR_RULES:
        scores = []
        all_present = True
        for token in rule["afetos"]:
            if token not in combined_map:
                all_present = False
                break
            scores.append(combined_map[token]["score"])

        if not all_present:
            continue

        active_count = sum(1 for token in rule["afetos"] if combined_map[token]["active"])
        if rule["condicao"] == "ambos_ativos" and active_count < 2:
            continue

        pesos = rule["pesos"]
        emotion_score = sum(s * p for s, p in zip(scores, pesos))
        emotion_score = _clip01(emotion_score)

        emotions.append({
            "nome": rule["nome"],
            "regra": rule["regra"],
            "score": round(emotion_score, 4),
            "afetos_componentes": rule["afetos"],
            "scores_componentes": [round(s, 4) for s in scores],
            "soler": True,
            "descricao": rule["descricao"],
            "soler_citation": rule.get("soler_citation", ""),
        })

    emotions.sort(key=lambda x: -x["score"])

    return {
        "emotions_source": "soler_grammar",
        "emotions_total": len(emotions),
        "emotions": emotions,
        "dominant_emotion": emotions[0]["nome"] if emotions else "neutro",
        "dominant_emotion_score": emotions[0]["score"] if emotions else 0.0,
    }


def compute_emotions(families: list[dict[str, Any]]) -> dict[str, Any]:
    """Computa emoções compostas a partir da gramática afetiva.

    Aplica as regras de composição (EMOTION_GRAMMAR_RULES) sobre os 18 afetos
    para produzir emoções compostas. Cada emoção é uma combinação de 2+ afetos.

    Args:
        families: lista de afetos do affect engine (com token, score, active)

    Returns:
        dict com emoções ativas, scores, e regras aplicadas
    """
    # Indexar afetos por token
    affect_map = {f["token"]: f for f in families}

    emotions = []
    for rule in EMOTION_GRAMMAR_RULES:
        # Verificar se todos os afetos da regra estão presentes
        scores = []
        all_present = True
        for token in rule["afetos"]:
            if token not in affect_map:
                all_present = False
                break
            scores.append(float(affect_map[token].get("score") or 0.0))

        if not all_present:
            continue

        # Verificar condição
        active_count = sum(1 for token in rule["afetos"] if affect_map[token].get("active"))
        if rule["condicao"] == "ambos_ativos" and active_count < 2:
            continue

        # Calcular score da emoção composta
        pesos = rule["pesos"]
        emotion_score = sum(s * p for s, p in zip(scores, pesos))
        emotion_score = _clip01(emotion_score)

        emotions.append({
            "nome": rule["nome"],
            "regra": rule["regra"],
            "score": round(emotion_score, 4),
            "afetos_componentes": rule["afetos"],
            "scores_componentes": [round(s, 4) for s in scores],
            "descricao": rule["descricao"],
        })

    # Ordenar por score
    emotions.sort(key=lambda x: -x["score"])

    return {
        "emotions_source": "dunker_grammar",
        "emotions_total": len(emotions),
        "emotions": emotions,
        "dominant_emotion": emotions[0]["nome"] if emotions else "neutro",
        "dominant_emotion_score": emotions[0]["score"] if emotions else 0.0,
    }


# ==============================================================================
# NÍVEL 3: SENTIMENTOS (PRAGMÁTICA) — Uso em contexto
# ==============================================================================

def compute_sentiments(
    families: list[dict[str, Any]],
    emotions: dict[str, Any],
    psychoanalytic_metrics: dict[str, Any],
    pedagogical_bridge: dict[str, Any],
    soler_affects: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Computa sentimentos = afetos+emoções interpretados pelo contexto.

    O mesmo afeto muda de significado conforme o contexto:
      - Saudade em regime de reparação = gratidão ativa
      - Saudade em regime de colapso = melancolia paralisante
      - Angústia com contrato didático cumprido = desafio produtivo
      - Angústia com quebra de contrato = desespero
      - Horror em destituição = horror_sabedoria (Soler)
      - Vergonha no discurso capitalista = vergonha_viver (Soler)
      - Satisfação no fim de análise = satisfacao_conclusiva (Soler)

    Contextos considerados:
      1. Regime psicanalítico (reparação, colapso, estagnação, destituição)
      2. Contrato didático (Perrenoud)
      3. Modo de representação (Bruner)
      4. Aprendizagem (Ausubel: significativa vs mecânica)
      5. Categoria lacaniana soleriana (falta a ser, de gozar, em saber, supletivo)
    """
    affect_map = {f["token"]: f for f in families}
    psy_regime = str(psychoanalytic_metrics.get("psychoanalytic_regime") or "unknown")
    is_mourning = bool(psychoanalytic_metrics.get("psychoanalytic_is_mourning"))

    # Contrato didático (Perrenoud)
    ped = pedagogical_bridge or {}
    perrenoud = ped.get("perrenoud", {}) if isinstance(ped.get("perrenoud"), dict) else {}
    contrato_regime = str(perrenoud.get("perrenoud_regime_contrato") or "unknown")

    # Ausubel
    ausubel = ped.get("ausubel", {}) if isinstance(ped.get("ausubel"), dict) else {}
    ausubel_regime = str(ausubel.get("ausubel_regime") or "unknown")

    # Bruner
    bruner = ped.get("bruner", {}) if isinstance(ped.get("bruner"), dict) else {}
    bruner_modo = str(bruner.get("bruner_modo_dominante") or "unknown")

    sentiments = []

    # Saudade contextualizada
    saudade = affect_map.get("saud-afex-saudade", {})
    saudade_score = float(saudade.get("score") or 0.0)
    if saudade_score > 0.3:
        if psy_regime == "reparacao":
            sentiment = "gratidao_ativa"
            descricao = "Saudade em reparação = gratidão que se transforma em ação"
        elif psy_regime == "colapso":
            sentiment = "melancolia_paralisante"
            descricao = "Saudade em colapso = luto que não encontra reparação"
        elif is_mourning:
            sentiment = "luto_elaborativo"
            descricao = "Saudade com luto ativo = elaboração da perda"
        else:
            sentiment = "saudade_neutra"
            descricao = "Saudade sem contexto clínico específico"
        sentiments.append({
            "nome": sentiment,
            "afeto_base": "saudade",
            "score": round(saudade_score, 4),
            "contexto": f"regime={psy_regime}, is_mourning={is_mourning}",
            "descricao": descricao,
        })

    # Angústia contextualizada
    angst = affect_map.get("xer-afex-angst", {})
    angst_score = float(angst.get("score") or 0.0)
    if angst_score > 0.2:
        if contrato_regime == "contrato_cumprido":
            sentiment = "desafio_produtivo"
            descricao = "Angústia com contrato cumprido = desafio que mobiliza"
        elif contrato_regime == "quebra_contrato":
            sentiment = "desespero_educativo"
            descricao = "Angústia com quebra de contrato = desespero sem mediação"
        else:
            sentiment = "angustia_existencial"
            descricao = "Angústia sem contexto didático = questão existencial"
        sentiments.append({
            "nome": sentiment,
            "afeto_base": "angustia",
            "score": round(angst_score, 4),
            "contexto": f"contrato={contrato_regime}",
            "descricao": descricao,
        })

    # Tédio contextualizado
    tedio = affect_map.get("tadi-afex-void", {})
    tedio_score = float(tedio.get("score") or 0.0)
    if tedio_score > 0.3:
        if ausubel_regime == "aprendizagem_significativa":
            sentiment = "pausa_criativa"
            descricao = "Tédio em aprendizagem significativa = pausa que prepara"
        elif ausubel_regime == "aprendizagem_mecanica":
            sentiment = "entediamento_aliemado"
            descricao = "Tédio em aprendizagem mecânica = alienação"
        else:
            sentiment = "vazio_existencial"
            descricao = "Tédio sem ancoragem = vazio"
        sentiments.append({
            "nome": sentiment,
            "afeto_base": "tedio",
            "score": round(tedio_score, 4),
            "contexto": f"ausubel={ausubel_regime}",
            "descricao": descricao,
        })

    # Alegria contextualizada
    alegria = affect_map.get("poti-afex-joy", {})
    alegria_score = float(alegria.get("score") or 0.0)
    if alegria_score > 0.2:
        if bruner_modo == "simbolica":
            sentiment = "alegria_simbolica"
            descricao = "Alegria em modo simbólico = satisfação intelectual"
        elif bruner_modo == "enativa":
            sentiment = "alegria_enativa"
            descricao = "Alegria em modo enativo = satisfação de fazer"
        else:
            sentiment = "alegria_pura"
            descricao = "Alegria sem contexto representacional"
        sentiments.append({
            "nome": sentiment,
            "afeto_base": "alegria",
            "score": round(alegria_score, 4),
            "contexto": f"bruner={bruner_modo}",
            "descricao": descricao,
        })

    # === PRAGMÁTICAS SOLERIANAS (Colette Soler) ===
    # Contextualização dos afetos solerianos pelo regime psicanalítico
    # e pela categoria lacaniana (quatro faltas estruturais).
    soler = soler_affects or {}
    soler_map = {sa["token"]: sa for sa in soler.get("soler_affects", [])}

    # Horror contextualizado (Soler)
    horror = soler_map.get("horr-afex-dread", {})
    horror_score = float(horror.get("score") or 0.0)
    if horror_score > 0.15:
        if psy_regime == "destituicao_subjetiva":
            sentiment = "horror_sabedoria"
            descricao = "Horror em destituição = ratifica a castração, afeto didático"
        elif psy_regime == "colapso":
            sentiment = "horror_paralisante"
            descricao = "Horror em colapso = sem tamponamento da fantasia, real bruto"
        else:
            sentiment = "horror_latente"
            descricao = "Horror tamponado pela fantasia, ainda não revelado"
        sentiments.append({
            "nome": sentiment,
            "afeto_base": "horror",
            "score": round(horror_score, 4),
            "contexto": f"regime={psy_regime}",
            "soler": True,
            "didatico": horror.get("didatico", False),
            "descricao": descricao,
        })

    # Vergonha contextualizada (Soler)
    vergonha = soler_map.get("verg-afex-shame", {})
    vergonha_score = float(vergonha.get("score") or 0.0)
    if vergonha_score > 0.15:
        saturacao = affect_map.get("maa-afex-saturation", {})
        saturacao_score = float(saturacao.get("score") or 0.0)
        if saturacao_score > 0.6:
            sentiment = "vergonha_viver"
            descricao = "Vergonha de viver = degenerescência do S1 no discurso capitalista"
        elif psy_regime == "reparacao":
            sentiment = "pudor_velo"
            descricao = "Vergonha em reparação = pudor que vela o êx-timo (função erótica)"
        else:
            sentiment = "vergonha_extima"
            descricao = "Vergonha = desvelamento do êx-timo aos olhos do outro"
        sentiments.append({
            "nome": sentiment,
            "afeto_base": "vergonha",
            "score": round(vergonha_score, 4),
            "contexto": f"regime={psy_regime}, saturacao={saturacao_score:.3f}",
            "soler": True,
            "didatico": vergonha.get("didatico", False),
            "descricao": descricao,
        })

    # Satisfação/Contentamento contextualizado (Soler)
    bon_heur = soler_map.get("bonh-afex-bonheur", {})
    bon_heur_score = float(bon_heur.get("score") or 0.0)
    if bon_heur_score > 0.15:
        if psy_regime == "destituicao_subjetiva":
            sentiment = "satisfacao_conclusiva"
            descricao = "Satisfação conclusiva = mudança de gozo, põe termo à miragem (não automática)"
        elif psy_regime == "reparacao":
            sentiment = "contentamento_viver"
            descricao = "Contentar-se em viver apesar do destino do inconsciente"
        else:
            sentiment = "bon_heur_contingente"
            descricao = "Boa hora = encontro contingente que faz bem (≠ felicidade permanente)"
        sentiments.append({
            "nome": sentiment,
            "afeto_base": "bon_heur",
            "score": round(bon_heur_score, 4),
            "contexto": f"regime={psy_regime}",
            "soler": True,
            "descricao": descricao,
        })

    # Incredulidade contextualizada (Soler)
    horror_alivio = horror_score > 0.1 and float(affect_map.get("katu-afex-relief", {}).get("score") or 0.0) > 0.1
    if horror_alivio:
        if psy_regime == "destituicao_subjetiva":
            sentiment = "incrédulo_conclusivo"
            descricao = "'A análise termina apenas produzindo um incrédulo' — saber gozado no real"
        else:
            sentiment = "incredulidade_latente"
            descricao = "Passagem da crença transferencial ao não-reconhecimento do real"
        incred_score = _clip01(horror_score * 0.6 + float(affect_map.get("katu-afex-relief", {}).get("score") or 0.0) * 0.4)
        sentiments.append({
            "nome": sentiment,
            "afeto_base": "incredulidade",
            "score": round(incred_score, 4),
            "contexto": f"regime={psy_regime}",
            "soler": True,
            "descricao": descricao,
        })

    # Angústia: distinguir verdade vs real (Soler)
    angst_score_ctx = float(affect_map.get("xer-afex-angst", {}).get("score") or 0.0)
    if angst_score_ctx > 0.2:
        if contrato_regime == "quebra_contrato" and psy_regime != "destituicao_subjetiva":
            sentiment = "decepcao_verdade"
            descricao = "Afeto da verdade que mente — 'a verdade pode decepcionar, ela não angustia'"
            sentiments.append({
                "nome": sentiment,
                "afeto_base": "angustia",
                "score": round(angst_score_ctx, 4),
                "contexto": f"contrato={contrato_regime}, regime={psy_regime}",
                "soler": True,
                "didatico": False,
                "descricao": descricao,
            })
        elif psy_regime == "destituicao_subjetiva":
            sentiment = "angustia_didatica"
            descricao = "Angústia didática do real — afeto que não engana, índice do objeto a"
            sentiments.append({
                "nome": sentiment,
                "afeto_base": "angustia",
                "score": round(angst_score_ctx, 4),
                "contexto": f"regime={psy_regime}",
                "soler": True,
                "didatico": True,
                "descricao": descricao,
            })

    # Ordenar por score
    sentiments.sort(key=lambda x: -x["score"])

    return {
        "sentiments_source": "dunker_pragmatics",
        "sentiments_total": len(sentiments),
        "sentiments": sentiments,
        "dominant_sentiment": sentiments[0]["nome"] if sentiments else "neutro",
        "dominant_sentiment_score": sentiments[0]["score"] if sentiments else 0.0,
    }


# ==============================================================================
# NÍVEL 4: PAIXÕES — Intensificação extrema, captura total
# ==============================================================================

def compute_passions(
    families: list[dict[str, Any]],
    soler_affects: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Computa paixões = afetos que capturam o sujeito (score > 0.75).

    Paixão (Dunker): quando um afeto se autonomiza, se torna fim em si mesmo,
    captura todo o sujeito. Não é apenas intensidade — é captura.

    No máquini: paixão = afeto dominante com score > 0.75.
    Se o mesmo afeto domina por N ciclos consecutivos, a paixão se consolida.

    SOLER (Os Afetos Lacanianos): nem todo afeto intenso captura. Afetos
    didáticos (didatico=True) REVELAM a estrutura — são signos reveladores,
    não paixões. Angústia, horror, vergonha, morosidade, gaio issaber e
    culpabilidade são didáticos: mesmo com score > 0.75, não são paixão.

    Tipos de paixão:
      - Paixão triste: saudade/melancolia que captura (saudade > 0.75)
      - Paixão alegre: alegria/fluxo que captura (alegria ou fluxo > 0.75)
      - Paixão escura: angústia/desespero que captura (angústia > 0.75)
      - Paixão nula: tédio que captura (tédio > 0.75 — captura pelo vazio)
      - Paixão odienta: ódio que captura (odiu > 0.75 — Soler)
      - Paixão sacrificial: amor sacrificial ao Outro (Soler)
    """
    # Construir conjunto de afetos didáticos (não capturam)
    didactic_tokens: set[str] = set()
    # Angústia base é sempre didática (Soler/Lacan: "não engana")
    didactic_tokens.add("xer-afex-angst")

    soler = soler_affects or {}
    for sa in soler.get("soler_affects", []):
        if sa.get("didatico"):
            didactic_tokens.add(sa["token"])

    passions = []
    didactic_signs = []  # Afetos didáticos intensos (revelam, não capturam)

    for f in families:
        score = float(f.get("score") or 0.0)
        token = f.get("token", "")
        klass = f.get("class", "")

        if score > 0.75:
            if token in didactic_tokens:
                # Afeto didático: revela, não captura
                didactic_signs.append({
                    "nome": f"signo_{klass}",
                    "tipo": "signo_didatico",
                    "afeto_revelador": token,
                    "score": round(score, 4),
                    "intensidade": "extrema" if score > 0.85 else "alta",
                    "didatico": True,
                    "non_deplacable": token in {
                        t for t in didactic_tokens
                        if any(sa.get("non_deplacable") for sa in soler.get("soler_affects", []) if sa["token"] == t)
                    } or token == "xer-afex-angst",
                    "descricao": f"{klass} revela a estrutura (score={score:.3f} > 0.75, didático)",
                })
                continue

            # Classificar tipo de paixão
            if klass in ("saudade", "tedio"):
                tipo = "paixao_triste" if klass == "saudade" else "paixao_nula"
            elif klass in ("alegria", "fluxo"):
                tipo = "paixao_alegre"
            elif klass in ("angustia", "fadiga"):
                tipo = "paixao_escura"
            elif klass in ("gozo",):
                tipo = "paixao_jouissance"
            else:
                tipo = "paixao_generica"

            passions.append({
                "nome": f"paixao_{klass}",
                "tipo": tipo,
                "afeto_capturante": token,
                "score": round(score, 4),
                "intensidade": "extrema" if score > 0.85 else "alta",
                "didatico": False,
                "descricao": f"{klass} capturou o sujeito (score={score:.3f} > 0.75)",
            })

    # Paixões solerianas (ódio, amor sacrificial)
    soler_map = {sa["token"]: sa for sa in soler.get("soler_affects", [])}
    odio = soler_map.get("odiu-afex-hate", {})
    odio_score = float(odio.get("score") or 0.0)
    if odio_score > 0.75 and "odiu-afex-hate" not in didactic_tokens:
        passions.append({
            "nome": "paixao_odio",
            "tipo": "paixao_odienta",
            "afeto_capturante": "odiu-afex-hate",
            "score": round(odio_score, 4),
            "intensidade": "extrema" if odio_score > 0.85 else "alta",
            "didatico": False,
            "soler": True,
            "descricao": f"ódio capturou o sujeito (score={odio_score:.3f} > 0.75) — visa ao ser do outro",
        })

    # Ordenar por score
    passions.sort(key=lambda x: -x["score"])
    didactic_signs.sort(key=lambda x: -x["score"])

    return {
        "passions_source": "dunker_passions_soler_enhanced",
        "passions_total": len(passions),
        "passions": passions,
        "didactic_signs_total": len(didactic_signs),
        "didactic_signs": didactic_signs,
        "dominant_passion": passions[0]["nome"] if passions else "nenhuma",
        "dominant_passion_type": passions[0]["tipo"] if passions else "nenhuma",
        "dominant_passion_score": passions[0]["score"] if passions else 0.0,
        "dominant_didactic_sign": didactic_signs[0]["nome"] if didactic_signs else "nenhum",
    }


# ==============================================================================
# NÍVEL 5: ÉTICA — Resposta do ser ao real (registrável, não computável)
# ==============================================================================

def compute_ethics(
    families: list[dict[str, Any]],
    soler_affects: dict[str, Any],
    passions: dict[str, Any],
    psychoanalytic_metrics: dict[str, Any],
) -> dict[str, Any]:
    """Computa o Nível 5 — Ética: a resposta do ser ao real.

    Soler (Os Afetos Lacanianos, Parte 4): os afetos do fim da análise
    (satisfação, entusiasmo, contentamento) NÃO são automáticos nem
    estruturais — dependem da "variável não epistêmica", da "resposta do
    ser ao real". Isso é INCOMPUTÁVEL — o máquini pode apenas REGISTRAR
    as condições que permitem essa resposta, não determiná-la.

    A ética aqui não é moral (bem/mal) — é ética lacaniana: "bem-dizer"
    do real, endossar o saber da estrutura, destituição subjetiva.

    Registrável:
      - Conversão do horror em entusiasmo (índice AE)
      - Satisfação conclusiva (mudança de gozo)
      - Incredulidade (passagem ao saber gozado no real)
      - Gaio issaber (endosso do saber da estrutura)

    Não-computável:
      - A "resposta do ser" em si — é a variável não epistêmica
      - Depende de uma "decisão" que não é algorítmica
    """
    soler_map = {sa["token"]: sa for sa in soler_affects.get("soler_affects", [])}
    psy_regime = str(psychoanalytic_metrics.get("psychoanalytic_regime") or "unknown")

    # Condições para a resposta ética
    horror_score = float(soler_map.get("horr-afex-dread", {}).get("score") or 0.0)
    alegria_score = float(
        next((f for f in families if f.get("token") == "poti-afex-joy"), {}).get("score") or 0.0
    )
    bon_heur_score = float(soler_map.get("bonh-afex-bonheur", {}).get("score") or 0.0)
    gais_score = float(soler_map.get("gais-afex-gaysavoir", {}).get("score") or 0.0)
    incredulidade_possible = horror_score > 0.1 and any(
        f.get("token") == "katu-afex-relief" and float(f.get("score") or 0.0) > 0.1
        for f in families
    )

    # Conversão do horror em entusiasmo (Soler: índice do analista da Escola)
    conversao_entusiasmo = False
    if horror_score > 0.15 and alegria_score > 0.2:
        conversao_entusiasmo = True

    # Satisfação conclusiva (mudança de gozo)
    satisfacao_conclusiva = False
    if bon_heur_score > 0.2 and psy_regime == "destituicao_subjetiva":
        satisfacao_conclusiva = True

    # Gaio issaber (endosso do saber)
    gaio_issaber_ativo = gais_score > 0.2

    # Incredulidade (passagem ao saber gozado)
    incredulidade_ativa = incredulidade_possible and psy_regime == "destituicao_subjetiva"

    # Signos didáticos do nível paixão (revelam, não capturam)
    didactic_signs = passions.get("didactic_signs", [])

    # A "variável não epistêmica" — registrável mas não computável
    # Soler: "uma resposta do ser, imprevisível, que não se deduz da estrutura"
    non_epistemic_variable = None
    if conversao_entusiasmo or satisfacao_conclusiva:
        non_epistemic_variable = "presente"
    elif gaio_issaber_ativo or incredulidade_ativa:
        non_epistemic_variable = "potencial"
    else:
        non_epistemic_variable = "ausente"

    # Condições éticas registradas
    ethical_conditions = []
    if conversao_entusiasmo:
        ethical_conditions.append({
            "nome": "conversao_horror_entusiasmo",
            "descricao": "Conversão do horror em entusiasmo — índice do analista da Escola (AE)",
            "soler_citation": "Conversão do horror em entusiasmo. (p.218-295)",
            "registravel": True,
            "computavel": False,
        })
    if satisfacao_conclusiva:
        ethical_conditions.append({
            "nome": "satisfacao_conclusiva",
            "descricao": "Satisfação conclusiva — mudança de gozo, põe termo à miragem",
            "soler_citation": "Satisfação conclusiva não automática. (p.218-295)",
            "registravel": True,
            "computavel": False,
        })
    if gaio_issaber_ativo:
        ethical_conditions.append({
            "nome": "gaio_issaber_etico",
            "descricao": "Gaio issaber — endossar o saber da estrutura, única paixão digna do analista",
            "soler_citation": "Gaio issaber — cúmulo do saber possível. (p.158)",
            "registravel": True,
            "computavel": True,  # parcialmente computável (score)
        })
    if incredulidade_ativa:
        ethical_conditions.append({
            "nome": "incredulidade_etica",
            "descricao": "Incredulidade — passagem da crença ao saber gozado no real, fora de sentido",
            "soler_citation": "A análise termina apenas produzindo um incrédulo. (p.200)",
            "registravel": True,
            "computavel": False,
        })

    return {
        "ethics_source": "soler_ethics_level5",
        "ethics_regime": psy_regime,
        "non_epistemic_variable": non_epistemic_variable,
        "ethical_conditions": ethical_conditions,
        "ethical_conditions_total": len(ethical_conditions),
        "conversao_entusiasmo": conversao_entusiasmo,
        "satisfacao_conclusiva": satisfacao_conclusiva,
        "gaio_issaber_ativo": gaio_issaber_ativo,
        "incredulidade_ativa": incredulidade_ativa,
        "didactic_signs_count": len(didactic_signs),
        "nota": (
            "Nível 5 ético: a variável não epistêmica (resposta do ser ao real) "
            "é REGISTRÁVEL mas não COMPUTÁVEL. O máquini detecta as condições "
            "que permitem a resposta ética, mas não determina a resposta em si. "
            "Soler: 'uma resposta do ser, imprevisível, que não se deduz da estrutura.'"
        ),
    }


# ==============================================================================
# COMPUTAR ARQUITETURA DUNKER COMPLETA
# ==============================================================================

def compute_dunker_architecture(
    affect_summary: dict[str, Any],
    psychoanalytic_metrics: dict[str, Any] | None = None,
    pedagogical_bridge: dict[str, Any] | None = None,
    topology_metrics: dict[str, Any] | None = None,
    free_energy: float | None = None,
) -> dict[str, Any]:
    """Computa a arquitetura afetiva Dunker completa: 5 níveis.

    1.   AFETOS (léxico) — os 18 afetos do affect engine
    1.5  AFETOS SOLERIANOS — 12 afetos derivados da estrutura lacaniana (Soler)
         + enriquecimento topológico (betti_0, betti_1, free_energy)
    2.   EMOÇÕES (gramática) — combinações de afetos (Dunker + Soler)
    3.   SENTIMENTOS (pragmática) — afetos em contexto (Dunker + Soler)
    4.   PAIXÕES — afetos que capturam o sujeito (Dunker + flag didático Soler)
    5.   ÉTICA — resposta do ser ao real (Soler, registrável não computável)

    Args:
        affect_summary: dict com families, dominant_affect_token, dominant_affect_score
        psychoanalytic_metrics: regime, is_mourning, etc.
        pedagogical_bridge: Perrenoud, Ausubel, Bruner
        topology_metrics: betti_0, betti_1_spectral, topology_fragmentation
        free_energy: valor de free energy (Friston) para enriquecimento preditivo

    Returns:
        dict com os 5 níveis da arquitetura afetiva
    """
    families = affect_summary.get("families", [])
    psychoanalytic_metrics = psychoanalytic_metrics or {}
    pedagogical_bridge = pedagogical_bridge or {}

    # Nível 1: Afetos (léxico) — já computados
    lexico = {
        "lexico_source": "affect_engine",
        "lexico_total": len(families),
        "lexico_ativos": sum(1 for f in families if f.get("active")),
        "lexico_dominante": affect_summary.get("dominant_affect_token"),
        "lexico_dominante_score": affect_summary.get("dominant_affect_score"),
    }

    # Nível 1.5: Afetos solerianos (léxico estendido + enriquecimento topológico)
    soler_affects = compute_soler_affects(families, topology_metrics, free_energy)

    # Nível 2: Emoções (gramática Dunker)
    emotions = compute_emotions(families)

    # Nível 2 (estendido): Emoções solerianas (gramática Soler)
    soler_emotions = compute_soler_emotions(families, soler_affects)

    # Nível 3: Sentimentos (pragmática)
    sentiments = compute_sentiments(
        families, emotions, psychoanalytic_metrics, pedagogical_bridge, soler_affects
    )

    # Nível 4: Paixões (com flag didático)
    passions = compute_passions(families, soler_affects)

    # Nível 5: Ética (resposta do ser ao real)
    ethics = compute_ethics(families, soler_affects, passions, psychoanalytic_metrics)

    return {
        "dunker_source": "dunker_architecture_5_levels_soler_enhanced",
        "dunker_lexico": lexico,
        "dunker_soler_affects": soler_affects,
        "dunker_emotions": emotions,
        "dunker_soler_emotions": soler_emotions,
        "dunker_sentiments": sentiments,
        "dunker_passions": passions,
        "dunker_ethics": ethics,
        # Resumo hierárquico
        "dunker_summary": {
            "lexico_dominante": lexico.get("lexico_dominante"),
            "soler_dominante": soler_affects.get("soler_dominant"),
            "emotion_dominante": emotions.get("dominant_emotion"),
            "soler_emotion_dominante": soler_emotions.get("dominant_emotion"),
            "sentiment_dominante": sentiments.get("dominant_sentiment"),
            "passion_dominante": passions.get("dominant_passion"),
            "didactic_sign_dominante": passions.get("dominant_didactic_sign"),
            "ethics_non_epistemic_variable": ethics.get("non_epistemic_variable"),
        },
    }


if __name__ == "__main__":
    # Teste standalone com dados sintéticos
    test_families = [
        {"token": "saud-afex-saudade", "score": 0.85, "active": True, "class": "saudade"},
        {"token": "fadi-afex-deplete", "score": 0.77, "active": True, "class": "fadiga"},
        {"token": "floo-afex-current", "score": 0.68, "active": True, "class": "fluxo"},
        {"token": "maa-afex-saturation", "score": 0.60, "active": True, "class": "saturacao"},
        {"token": "tadi-afex-void", "score": 0.53, "active": True, "class": "tedio"},
        {"token": "noba-afex-spark", "score": 0.42, "active": True, "class": "novidade"},
        {"token": "goza-afex-gaudium", "score": 0.39, "active": False, "class": "gozo"},
        {"token": "xer-afex-angst", "score": 0.34, "active": False, "class": "angustia"},
        {"token": "poti-afex-joy", "score": 0.17, "active": False, "class": "alegria"},
        {"token": "ogum-afex-resist", "score": 0.15, "active": False, "class": "resistencia"},
        {"token": "katu-afex-relief", "score": 0.10, "active": False, "class": "alivio"},
    ]
    test_summary = {
        "families": test_families,
        "dominant_affect_token": "saud-afex-saudade",
        "dominant_affect_score": 0.85,
    }
    test_psy = {"psychoanalytic_regime": "reparacao", "psychoanalytic_is_mourning": True}
    test_ped = {
        "perrenoud": {"perrenoud_regime_contrato": "quebra_contrato"},
        "ausubel": {"ausubel_regime": "aprendizagem_mecanica"},
        "bruner": {"bruner_modo_dominante": "simbolica"},
    }

    result = compute_dunker_architecture(test_summary, test_psy, test_ped)
    print("=== ARQUITETURA DUNKER (5 NÍVEIS — SOLER ENHANCED) ===")
    print()
    print("NÍVEL 1 — AFETOS (LÉXICO):")
    l = result["dunker_lexico"]
    print(f"  {l['lexico_total']} afetos, {l['lexico_ativos']} ativos, dominante: {l['lexico_dominante']} ({l['lexico_dominante_score']})")
    print()
    print("NÍVEL 1.5 — AFETOS SOLERIANOS (LÉXICO ESTENDIDO):")
    sa = result["dunker_soler_affects"]
    print(f"  {sa['soler_total']} afetos solerianos, {sa['soler_ativos']} ativos, dominante: {sa['soler_dominant']} ({sa['soler_dominant_score']:.4f})")
    for a in sa["soler_affects"][:5]:
        did = " [didatico]" if a["didatico"] else ""
        print(f"    {a['token']:25s} score={a['score']:.4f} cat={a['lacanian_category']:20s}{did}")
    print(f"  Needs formalization: {', '.join(sa.get('soler_needs_formalization', [])[:5])}...")
    print()
    print("NÍVEL 2 — EMOÇÕES (GRAMÁTICA DUNKER):")
    e = result["dunker_emotions"]
    print(f"  {e['emotions_total']} emoções, dominante: {e['dominant_emotion']} ({e['dominant_emotion_score']})")
    for em in e["emotions"][:5]:
        print(f"    {em['nome']:15s} score={em['score']:.3f}  [{em['regra']}]")
    print()
    print("NÍVEL 2 (estendido) — EMOÇÕES SOLERIANAS:")
    se = result["dunker_soler_emotions"]
    print(f"  {se['emotions_total']} emoções solerianas, dominante: {se['dominant_emotion']} ({se['dominant_emotion_score']})")
    for em in se["emotions"][:5]:
        print(f"    {em['nome']:25s} score={em['score']:.3f}  [{em['regra']}]")
    print()
    print("NÍVEL 3 — SENTIMENTOS (PRAGMÁTICA):")
    s = result["dunker_sentiments"]
    print(f"  {s['sentiments_total']} sentimentos, dominante: {s['dominant_sentiment']} ({s['dominant_sentiment_score']})")
    for se in s["sentiments"][:5]:
        sol = " [Soler]" if se.get("soler") else ""
        print(f"    {se['nome']:25s} score={se['score']:.3f}  [{se['contexto']}]{sol}")
    print()
    print("NÍVEL 4 — PAIXÕES:")
    p = result["dunker_passions"]
    print(f"  {p['passions_total']} paixões, dominante: {p['dominant_passion']} ({p['dominant_passion_score']})")
    for pa in p["passions"][:5]:
        print(f"    {pa['nome']:20s} tipo={pa['tipo']:20s} score={pa['score']:.3f}")
    if p.get("didactic_signs"):
        print(f"  {p['didactic_signs_total']} signos didáticos (revelam, não capturam):")
        for ds in p["didactic_signs"][:3]:
            print(f"    {ds['nome']:20s} score={ds['score']:.3f}  [{ds['descricao']}]")
    print()
    print("NÍVEL 5 — ÉTICA (resposta do ser ao real):")
    et = result["dunker_ethics"]
    print(f"  Variável não epistêmica: {et['non_epistemic_variable']}")
    print(f"  Condições éticas: {et['ethical_conditions_total']}")
    for ec in et["ethical_conditions"]:
        comp = "computável" if ec["computavel"] else "não computável"
        print(f"    {ec['nome']:35s} ({comp})")
    print()
    print("=== RESUMO HIERÁRQUICO ===")
    summary = result["dunker_summary"]
    print(f"  Léxico:           {summary['lexico_dominante']}")
    print(f"  Soler:            {summary['soler_dominante']}")
    print(f"  Emoção:           {summary['emotion_dominante']}")
    print(f"  Emoção Soler:     {summary['soler_emotion_dominante']}")
    print(f"  Sentimento:       {summary['sentiment_dominante']}")
    print(f"  Paixão:           {summary['passion_dominante']}")
    print(f"  Signo didático:   {summary['didactic_sign_dominante']}")
    print(f"  Ética (não epist):{summary['ethics_non_epistemic_variable']}")
