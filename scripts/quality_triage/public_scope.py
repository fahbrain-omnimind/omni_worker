#!/usr/bin/env python3
"""public scope — reclassify domestic priors under professional/public mode.

The historical corpus verdicts are DOMESTIC: 75% accepted_domestic reflects
a lab machine with high Linux control (transpatch, disk symlinks, sudo
rituals, LAN IPs). Public/professional deployment flips those assumptions:
what the lab accepts as "intentional" becomes a public-risk finding.

Every flip carries a TRAIL: prior verdict (domestic) → public rule →
explanatory rationale → practice reference. The reclassification is
deterministic and auditable — models (free CLIs) can cross-check the
mapping tables below via `crosscheck.py`.

pt-BR: camada pública sobre priors domésticos — reclassificação
determinística com trilha explicativa.
"""

from __future__ import annotations

from dataclasses import dataclass

# rule → (public verdict, reason, practice)
# Sources: OW-STU-011 §3.3/§3.6 (rule_verdicts + practices do corpus).
PUBLIC_FLIPS: dict[str, tuple[str, str, str]] = {
    "S8707": ("future_public_risk",
              "path como interface de script vindo de parse_args é aceitável "
              "no doméstico; em app pública exige validação de input (allowlist)",
              "security: validar input externo antes de usar em I/O"),
    "S7688": ("future_public_risk",
              "ritual sudo em .sh é intencional no lab; serviço público exige "
              "dropping de privilégios e execução sem sudo",
              "security: mínimos privilégios em runtime"),
    "S2083": ("future_public_risk",
              "write_text de artefato interno OK no lab; exposto publicamente "
              "é path traversal — validar e permitir apenas diretórios canônicos",
              "security: paths de escrita restritos e validados"),
    "S5443": ("future_public_risk",
              "/tmp world-writable é contrato do lab; público exige dir 0700 "
              "e ownership check",
              "security: filas/estado fora de world-writable"),
    "S2245": ("future_public_risk",
              "PRNG não-cripto em simulador é intencional; produção pública "
              "que exponha IDs/tokens exige secrets/random criptográfico",
              "security: PRNG só em não-exposição"),
    "S8705": ("future_public_risk",
              "argv→subprocess list-form é padrão doméstico; serviço público "
              "que aceita input externo exige shlex.quote + allowlist",
              "security: shell=True só com pipeline list-form"),
    "S5332": ("future_public_risk",
              "http:// + IPs internos são localhost de daemons do lab; "
              "produção exige TLS e bind configurável por env",
              "security: bind/CORS configuráveis por env"),
    "S1313": ("future_public_risk",
              "IPs LAN intencionais no lab; expostos, vazam topologia — "
              "externalizar via env/config",
              "architecture: separação doméstico vs oficial"),
    "S8706": ("real_vulnerability",
              "sqlite file:URI com #/? injeta parâmetro — já era risco no "
              "lab; em público é vulnerabilidade real, urllib.parse",
              "security: validar IPs/paths com parsers reais"),
    "S6096": ("real_vulnerability",
              "tarfile de origem externa (HF/Zenodo) sem filter='data' é "
              "zip-slip — vulnerabilidade real em qualquer escopo",
              "security: zip-slip filter='data'"),
    "S8702": ("real_vulnerability",
              "identificadores SQL em f-string de --table/--limit — "
              "injeção real quando exposto",
              "security: parâmetros, nunca interpolação"),
    "S5145": ("future_public_risk",
              "campos de request no logger forjam linhas — sanitizar \\n\\r",
              "security: sanitizar campos de request antes de log"),
    "S6350": ("real_vulnerability",
              "endpoints sem auth que disparam CLIs (gemini/codex exec) — "
              "CSRF-viável no browser do operador; público é crítico",
              "security: endpoints HTTP ativos exigem auth mínimo"),
    "S8786": ("architectural_debt",
              "regex super-linear segue dívida consciente — mas em serviço "
              "público o adversarial time é contrato, não exceção",
              "regex: medir antes de reescrever"),
    "S1244": ("review_needed",
              "float equality em enable-gates era intencional; em API pública "
              "epsilon explícito evita ambiguidade de contrato",
              "architecture: contrato explícito em superfície pública"),
    "S6466": ("false_positive",
              "slices que nunca lançam seguem false positive — sem mudança",
              "persistence: manter veredito histórico"),
}

PUBLIC_PRACTICES = (
    "security: shell=True só com pipeline list-form (shlex.quote)",
    "security: bind/CORS configuráveis por env (0.0.0.0 só doméstico)",
    "security: validar IPs com ipaddress.ip_address() em sinks",
    "security: filas de segurança em dir 0700 + ownership check",
    "security: endpoints HTTP ativos exigem auth mínimo",
    "security: sanitizar campos de request antes de log (S5145)",
    "async: subprocess/requests/sleep em corrotinas → asyncio.to_thread",
    "async: guardar referências de create_task (S7502)",
    "regex: medir antes de reescrever (t(2n)/t(n)>2.5 ou >20ms adversarial)",
    "regex: seeds explícitas para reprodutibilidade (S6709)",
    "persistence: escrita atômica com lock para JSON canônico",
    "persistence: retorno bool em helpers de persistência",
    "architecture: separação doméstico vs oficial é princípio permanente",
    "architecture: classe de veredicto antes de corrigir (rationale preservado)",
)


@dataclass
class Trail:
    rule: str
    domestic_verdict: str
    public_verdict: str
    reason: str
    practice: str
    flips: bool


def reclassify(rule: str, domestic_verdict: str) -> Trail:
    """Public-mode reclassification with provenance trail."""
    flip = PUBLIC_FLIPS.get(rule)
    if flip:
        pub, reason, practice = flip
        return Trail(rule, domestic_verdict, pub, reason, practice,
                     flips=pub != domestic_verdict)
    return Trail(rule, domestic_verdict, domestic_verdict,
                 "sem reclassificação pública definida no mapeamento atual",
                 "", flips=False)


def apply_to_prior(rule: str, prior: dict | None) -> dict:
    """Merge a prior row with its public trail (for triage --scope public)."""
    dom = (prior or {}).get("verdict") or "unknown"
    tr = reclassify(rule, dom)
    out = dict(prior or {})
    out.update({
        "rule": rule,
        "domestic_verdict": dom,
        "public_verdict": tr.public_verdict,
        "public_reason": tr.reason,
        "public_practice": tr.practice,
        "flips": tr.flips,
    })
    return out