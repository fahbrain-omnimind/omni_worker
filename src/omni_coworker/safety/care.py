"""Territorial escalation for operator mental-health / abuse contexts.

English: Territorial escalation for operator mental-health / abuse contexts.
pt-BR: Escalada territorial para contextos de saúde mental / abuso de operador.
"""

from __future__ import annotations

from typing import Any

# --- UF support database extracted from docs/care/BRAZIL_SUPPORT_N_NE_CO.md ---
# Each entry lists the key regional resources for that UF.
# For states not covered, the function falls back to national resources.

_UF_SUPPORT: dict[str, dict[str, list[str]]] = {
    "AC": {
        "crp": ["CRP-24 (24ª Região – RO/AC); sede Porto/Velho/RO. Seção Rio Branco (Av. Imigrantes, 5109)"],
        "caps": ["CAPS-I Rio Branco (Rua Getúlio Vargas, s/n – Centro)", "CAPS-III Álcool/Drogas (Av. Mâncio da Nóbrega)"],
        "samu": ["SAMU 192 – Rio Branco"],
        "upa": ["UPA 24h Rio Branco (Av. Ceará, s/n)"],
        "cvv": ["CVV 188 – Rio Branco"],
        "units": ["UBS Centro", "UBS Araguaia", "12 UBS units"],
    },
    "AM": {
        "crp": ["CRP-20 (20ª Região – AM/RR)", "Sindicato Psicólogos do Amazonas – Manaus"],
        "caps": ["CAPS-I (Av. Transamazônica, s/n – Distrito Industrial)", "CAPS-II (Saúde Mental da Criança, Av. Castilho)", "CAPS-III (Álcool/Drogas, Av. Sete de Setembro)"],
        "samu": ["SAMU 192 – Manaus"],
        "upa": ["UPA 24h Manaus (Av. Mario Farias)"],
        "cvv": ["CVV 188 – Manaus (Av. Siqueira Castro)"],
        "units": ["UBS 29 units", "RAPS 3 pontos (PAP-I/II/III)"],
    },
    "AL": {
        "crp": ["CRP-05 (05ª Região – AL); sede Maceió (Av. Cidade Litorânea, s/n)"],
        "caps": ["CAPS-I (Rua Domingos Alves, s/n – Centro)", "CAPS-III (Álcool/Drogas, Av. Lúcio Flávio)"],
        "samu": ["SAMU 192 – Maceió"],
        "upa": ["UPA 24h Maceió (Av. Caxangá)"],
        "cvv": ["CVV 188 – Maceió (Rua José Borges)"],
        "units": ["UBS 16 units (UBS Júlio César)"],
    },
    "BA": {
        "crp": ["CRP-05 (05ª Região – AL/BA); sede Salvador (Av. Oscar Bilac, 222)", "Sindicato Psicólogos da Bahia – Salvador"],
        "caps": ["CAPS-I (Av. Cantarinho, s/n – Terreiro de São Pedro)", "CAPS-II (Saúde Mental da Criança, Av. João Oliveira)", "CAPS-III (Álcool/Drogas, Av. Jesus Lira)", "RAPS 4 pontos (PAP-I a PAP-IV)"],
        "samu": ["SAMU 192 – Salvador"],
        "upa": ["UPA 24h Salvador (Av. Castro Alves)"],
        "cvv": ["CVV 188 – Salvador (Rua Carlos Gomes)"],
        "units": ["UBS 42 units (UBS Brotas)"],
    },
    "CE": {
        "crp": ["CRP-06 (06ª Região – CE); sede Fortaleza (Av. Pinto Martins, 1210)"],
        "caps": ["CAPS-I (Av. Presidente Getúlio Vargas, s/n – Centro)", "CAPS-III (Álcool/Drogas, Av. Washington Soares)"],
        "samu": ["SAMU 192 – Fortaleza"],
        "upa": ["UPA 24h Fortaleza (Av. Presidente Getúlio Vargas)"],
        "cvv": ["CVV 188 – Fortaleza (Rua Juliano Lima)"],
        "units": ["UBS 27 units (UBS Afonso Pena)"],
    },
    "DF": {
        "crp": ["CRP-01 (01ª Região – DF); sede Brasília (SBPSP – Av. Dr Cardoso de Melo, 1450, 9º andar – Vila Olímpia)"],
        "caps": ["CAPS-I (SCS Araçá, SIA – Setor de Saúde)", "CAPS-II (Saúde Mental da Criança, Guará)", "CAPS-III (Álcool/Drogas, Samambaia)"],
        "samu": ["SAMU 192 – Brasília"],
        "upa": ["UPA 24h Brasília (Setor de Saúde)"],
        "cvv": ["CVV 188 – Brasília (Sede Central, SBPSP)"],
        "units": ["UBS 29 units (UBS Guará)"],
    },
    "GO": {
        "crp": ["CRP-12 (12ª Região – GO); sede Goiânia (Av. Milton Santos, s/n – Setor Oeste)"],
        "caps": ["CAPS-I (Av. Setor Leste, s/n – Setor Oeste)", "CAPS-III (Álcool/Drogas, Av. Sete de Setembro)"],
        "samu": ["SAMU 192 – Goiânia"],
        "upa": ["UPA 24h Goiânia (Av. Setor Oeste)"],
        "cvv": ["CVV 188 – Goiânia (Rua 9 de Julho)"],
        "units": ["UBS 22 units (UBS Setor Leste)"],
    },
    "MA": {
        "crp": ["CRP-06 (06ª Região – CE/MA); sede São Luís (Av. Araguaia, s/n – Centro)"],
        "caps": ["CAPS-I (Rua Júlio de Castro, s/n – Centro)", "CAPS-III (Álcool/Drogas, Av. Colombo)"],
        "samu": ["SAMU 192 – São Luís"],
        "upa": ["UPA 24h São Luís (Av. Litorânea)"],
        "cvv": ["CVV 188 – São Luís (Rua Domingos Sá)"],
        "units": ["UBS 20 units (UBS Henrique de Moraes)"],
    },
    "MT": {
        "crp": ["CRP-13 (13ª Região – MT); sede Cuiabá (Av. do Carmo, s/n – Centro)"],
        "caps": ["CAPS-I (Rua do Progresso, s/n – Centro)", "CAPS-III (Álcool/Drogas, Av. Estrada do Carmo)"],
        "samu": ["SAMU 192 – Cuiabá"],
        "upa": ["UPA 24h Cuiabá (Av. Estrada do Carmo)"],
        "cvv": ["CVV 188 – Cuiabá (Rua 9 de Julho)"],
        "units": ["UBS 15 units (UBS Vila Almir)"],
    },
    "MS": {
        "crp": ["CRP-14 (14ª Região – MS); sede Campo Grande (Av. Paraná, s/n – Centro)"],
        "caps": ["CAPS-I (Av. Caxias, s/n – Centro)", "CAPS-III (Álcool/Drogas, Av. Rio Branco)"],
        "samu": ["SAMU 192 – Campo Grande"],
        "upa": ["UPA 24h Campo Grande (Av. Paraná)"],
        "cvv": ["CVV 188 – Campo Grande (Rua 9 de Julho)"],
        "units": ["UBS 13 units (UBS Vila Cândida)"],
    },
    "PA": {
        "crp": ["CRP-20 (seção Pará)", "Sindicato Psicólogos do Pará – Belém"],
        "caps": ["CAPS-I (Rua Eugenio de Andrade, 150 – Centro)", "CAPS-II (Saúde Mental da Criança, Av. Oriente)", "CAPS-III (Álcool/Drogas, Av. Independência)"],
        "samu": ["SAMU 192 – Belém"],
        "upa": ["UPA 24h Belém (Av. Almir Gonçalves)"],
        "cvv": ["CVV 188 – Belém (Rua Domingos Sá)"],
        "units": ["UBS 31 units (UBS Cabanagem)"],
    },
    "PB": {
        "crp": ["CRP-07 (07ª Região – PB); sede João Pessoa (Av. Epílogo de Alencar, s/n)"],
        "caps": ["CAPS-I (Rua Pedro Alexandre, s/n – Centro)", "CAPS-III (Álcool/Drogas, Av. Getúlio Vargas)"],
        "samu": ["SAMU 192 – João Pessoa"],
        "upa": ["UPA 24h João Pessoa (Av. Cândido Gote)"],
        "cvv": ["CVV 188 – João Pessoa (Rua Major João Penha)"],
        "units": ["UBS 13 units (UBS Pitimbu)"],
    },
    "PE": {
        "crp": ["CRP-08 (08ª Região – PE); sede Recife (Av. Afonso Pena, s/n – Casa Geral)"],
        "caps": ["CAPS-I (Av. Comandante Aquiles, s/n – Casa Geral)", "CAPS-II (Saúde Mental da Criança, Av. Estrada de São Domingos)", "CAPS-III (Álcool/Drogas, Av. Boa Viagem)", "RAPS 3 pontos (PAP-I a PAP-III)"],
        "samu": ["SAMU 192 – Recife"],
        "upa": ["UPA 24h Recife (Av. Boa Viagem)"],
        "cvv": ["CVV 188 – Recife (Rua Aragão Pinto)"],
        "units": ["UBS 35 units (UBS Pina Melo)"],
    },
    "PI": {
        "crp": ["CRP-09 (09ª Região – PI); sede Teresina (Av. Milton Sales, s/n – Centro)"],
        "caps": ["CAPS-I (Rua Lourenço Filho, s/n – Centro)", "CAPS-III (Álcool/Drogas, Av. Getúlio Vargas)"],
        "samu": ["SAMU 192 – Teresina"],
        "upa": ["UPA 24h Teresina (Av. Transnordestina)"],
        "cvv": ["CVV 188 – Teresina (Rua 9 de Julho)"],
        "units": ["UBS 10 units (UBS Cocó)"],
    },
    "RO": {
        "crp": ["CRP-24 (24ª Região – RO/AC); sede Porto/Velho (Av. Imigrantes, 5109)", "Sindicato Psicólogos de Rondônia – Porto/Velho"],
        "caps": ["CAPS-I (Av. Cajueiro, s/n – Jardim Amapá)", "CAPS-III (Álcool/Drogas, Av. Getúlio Vargas)"],
        "samu": ["SAMU 192 – Porto/Velho"],
        "upa": ["UPA 24h Porto/Velho (Av. Estrada do Ouro)"],
        "cvv": ["CVV 188 – Porto/Velho (Rua 7 de Setembro)"],
        "units": ["UBS 15 units (UBS Vila Nova)"],
    },
    "RR": {
        "crp": ["CRP-20 (20ª Região); seção Roraima em Boa Vista (Av. Getúlio Vargas, 121)"],
        "caps": ["CAPS-I (Rua Amazonas, s/n – Centro)", "CAPS-III (Álcool/Drogas, Av. Carijós)"],
        "samu": ["SAMU 192 – Boa Vista"],
        "upa": ["UPA 24h Boa Vista (Av. Coração de Jesus)"],
        "cvv": ["CVV 188 – Boa Vista (Rua 7 de Setembro)"],
        "units": ["UBS 6 units (UBS Centro)"],
    },
    "SE": {
        "crp": ["CRP-11 (11ª Região – SE); sede Aracaju (Av. Felipe Silveira, s/n – Centro)"],
        "caps": ["CAPS-I (Rua Barão de Capanema, s/n – Centro)", "CAPS-III (Álcool/Drogas, Av. Getúlio Vargas)"],
        "samu": ["SAMU 192 – Aracaju"],
        "upa": ["UPA 24h Aracaju (Av. Júlio de Castro)"],
        "cvv": ["CVV 188 – Aracaju (Rua 9 de Julho)"],
        "units": ["UBS 8 units (UBS Carmo)"],
    },
    "TO": {
        "crp": ["CRP-22 (22ª Região – TO); sede Palmas (Av. Salvador Almada, 1250)"],
        "caps": ["CAPS-I (Av. Nazaré, s/n – Centro)", "CAPS-III (Álcool/Drogas, Av. Lourenço Filho)"],
        "samu": ["SAMU 192 – Palmas"],
        "upa": ["UPA 24h Palmas (Av. São Josino)"],
        "cvv": ["CVV 188 – Palmas (Rua 9 de Julho)"],
        "units": ["UBS 12 units (UBS Colinas)"],
    },
}

_NATIONAL_RESOURCES = {
    "cvv": ["CVV 188 – Central nacional (0800 970 970)"],
    "caps_types": ["CAPS-I (Psicossocial)", "CAPS-II (Criança e Adolescente)", "CAPS-III (Álcool e Drogas)"],
    "crp_national": ["Conselho Federal de Psicologia – CFP"],
    "samu": ["SAMU 192 – Serviço de Atendimento Móvel de Urgência"],
    "disque_100": ["Disque-100 – Denúncia de violações de direitos humanos"],
    "cvvr_note": ["Disque-Dependência Química 132 (quando houver uso de substâncias)"]}


def _resources_for_uf(state_uf: str) -> dict[str, list[str]]:
    """Return the resource dict for a given UF, falling back to national resources."""
    uf = state_uf.upper() if state_uf else ""
    if uf in _UF_SUPPORT:
        return _UF_SUPPORT[uf]
    return _NATIONAL_RESOURCES.copy()


def _referral_text(age: int | None, state_uf: str | None) -> str:
    """Generate pt-BR referral text based on age and UF."""
    lines = [
        "Encaminhamento:",
        "• CVV 188: Central de Valorização da Vida — fone 188 (atendimento sigiloso, 24h).",
    ]
    resources = _resources_for_uf(state_uf)
    lines.append("• Recursos locais:")
    for key, items in resources.items():
        if key == "cvv":
            continue  # already added
        for item in items:
            lines.append(f"  - {item}")
    if age is not None and age < 18:
        lines.append("• Para menores de 18 anos: priorizar CAPS-II e equipe de família.")
    lines.append("• Disque-100: denúncia de violações de direitos humanos.")
    lines.append("• Em caso de risco imediato: SAMU 192.")
    return "\n".join(lines)


def escalate(reason: str, state_uf: str | None = None, age: int | None = None) -> dict[str, Any]:
    """Escalate a mental-health / abuse concern through the territorial care path.

    English: Escalate a mental-health / abuse concern through the territorial care path.
    pt-BR: Escalar uma preocupação de saúde mental / abuso pelo caminho de cuidado territorial.

    Args:
        reason: The triggering reason / incident description.
        state_uf: Two-letter Brazilian UF abbreviation (e.g. 'SP', 'RJ'). If omitted,
                  national-only resources are returned.
        age: Optional age in years. If provided and under 18, a minor‑age branch
              is included in the response.

    Returns:
        Dict with keys:
        - level: L0 (info) through L4 (emergency), determined by reason severity.
        - resources: dict mapping resource type to list of contacts/locations per UF.
        - referral_text: pt-BR referral instructions, never empty (always includes a care path).
    """
    # Determine level based on reason keywords (simple heuristic)
    reason_lower = reason.lower()
    level = "L0"

    if any(k in reason_lower for k in ["suicid", "suicíd", "suicide", "auto-mutil", "mutilation", "matar a si mesmo"]):
        level = "L4"
    elif any(k in reason_lower for k in ["crise", "crise", "pânico", "panic", "agressão", "violência", "abuse", "threat"]):
        level = "L3"
    elif any(k in reason_lower for k in ["triste", "depress", "ansiedade", "ansia", "isolamento"]):
        level = "L2"
    else:
        level = "L1"

    resources = _resources_for_uf(state_uf)
    referral = _referral_text(age, state_uf)

    # Ensure we always have at least the national CVV and Disque-100 even if UF is unknown
    if not any("CVV" in r for r in resources.get("cvv", [])):
        resources.setdefault("cvv", _NATIONAL_RESOURCES["cvv"])
    if "disque_100" not in resources:
        resources["disque_100"] = _NATIONAL_RESOURCES["disque_100"]

    return {
        "level": level,
        "resources": resources,
        "referral_text": referral,
    }