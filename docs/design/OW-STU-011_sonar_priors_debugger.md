<!-- doc_id: OW-STU-011 | title: Sonar priors — base de vereditos + debugger/recommender | author: devin | date: 2026-11-03 | status: study -->

# OW-STU-011 — Priors SonarCloud: base de vereditos históricos + triagem automática

## 1. Pergunta do operador

> "Verificar se fizemos algo referente ao debugger e agente automático com histórico,
> classificação dos erros, recomendações e revisões. Se não, designar um agente para essa
> auditoria, criar essa base de priors, e um script, prompt que o modelo possa executar,
> avaliando uso, correção ou qualidade de código a partir do histórico SonarCloud."

**Resposta curta**: o worker NÃO tinha base de priors, classificador de erros ou agente
automático de revisão com histórico. O que existia eram dois registros isolados e sem
conexão entre si: o ledger da `gemma4_diag_battery` (diagnóstico de modelo, não de código)
e o `run_coding_battery.py` (mecânico: ast/black/ruff + review por brain, sem histórico).
O histórico real de decisões de qualidade vivia **fora** do worker, em artefatos SonarCloud
do Drive. Este estudo analisa esse corpus e fundamenta a implementação entregue.

## 2. Fonte de dados (proveniência)

Arquivos originais em `/content/drive/MyDrive/DOXIHEWU_OMNIMIND/private_artifacts/sonarcloud`
(copiados para `/tmp/sonar_audit/`, extração sem modificar os originais):

| Arquivo | Tamanho | Conteúdo |
|---|---|---|
| `code_quality_triage.sqlite` | 3.6 MB | 5.981 findings + 29 rule_verdicts + 15 practices + 10 work_packages + FTS |
| `sonar_code_quality_memory.sqlite` | 20.5 MB | 6.394 issues + 125 rules + 80 comments + 9 analyses + 2 projects |
| `sonar_issues_complete.jsonl` | 12.9 MB | 6.394 issues (espelho do sqlite) |
| `sonar_accepted_rationales_catalog.json` | 2.7 MB | 70.442 linhas — issues aceitas com rationales completos |
| `sonarcloud_complete_memory_export_latest.md` | 6.7 KB | relatório de exportação (2026-10-24, org `zephyrix`) |

Datas das análises: 2026-10-04 → 2026-10-16 (9 análises, revision `b737486b`→`ef91f680`,
com eventos de QUALITY_PROFILE "Use 'So...'" e VERSION). Autor dos rationales de aceite:
`fabs-devbrain-RALBU@gitlab` (agente devbrain do operador) — ou seja, este corpus É o
histórico de aceites que o operador mencionou.

## 3. Análise de dados (números exatos)

### 3.1 Distribuição de vereditos — `code_quality_triage` (5.981 findings, 96 regras)

| Veredito | N | % | Leitura |
|---|---|---|---|
| `accepted_domestic` | 4.505 | 75,3% | intencional no domínio doméstico — a classe dominante |
| `review_needed` | 922 | 15,4% | precisa revisão humana/agente |
| `architectural_debt` | 346 | 5,8% | dívida consciente (79 regex corrigidos com ganho 1125x) |
| `future_public_risk` | 130 | 2,2% | seguro no doméstico, risco se publicado |
| `false_positive` | 65 | 1,1% | falso positivo confirmado |
| `real_vulnerability` | 13 | 0,2% | vulnerabilidade real, corrigir |

### 3.2 Categoria × veredito (padrões de classificação)

- **VULNERABILITY** → `accepted_domestic` 3.261 (majoria: S8707/S7688/S2083 em scripts
  domésticos — path/argv/tempdir como contrato do script, não falha);
  `future_public_risk` 130 (S6096 zip-slip, S8706 sqlite file:URI, S8702 SQL-id);
  `real_vulnerability` 10.
- **BUG** → `review_needed` 443 (dominante — bug nunca é auto-aceito);
  `false_positive` 65 (S6466: 52 slices que nunca lançam).
- **CODE_SMELL** → `architectural_debt` 295 + `review_needed` 204.

**Regra empírica 1**: categoria BUG não tem auto-aceite — veredito dominante é
`review_needed`. VULNERABILITY em código doméstico é `accepted_domestic` na maioria,
mas as exceções (`future_public_risk`/`real_vulnerability`) vivem em sinks de E/S
(zip-slip, file-URI, SQL-id, tarfile, auth em CLI).

### 3.3 Top regras com prior (do `rule_verdicts` — 29 entradas)

| Regra | N | Veredito | Batch | Rationale dominante (resumo) |
|---|---|---|---|---|
| S8707 | 1.415 | accepted_domestic | ✔ | 93% fonte=parse_args() — path é a interface do script |
| S7688 | 1.098 | accepted_domestic | ✔ | frota .sh com ritual sudo — intencional doméstico |
| S2083 | 646 | accepted_domestic | ✔ | 87% write_text de artefato interno; exceções omnimind.py:404 |
| S5443 | 357 | accepted_domestic | ✔ | /tmp persistente é contrato conhecido; melhorar dir 0700 |
| S2245 | 334 | accepted_domestic | ✔ | random não-cripto em simulador; exceção dodecatiad_defender |
| S8705 | 276 | accepted_domestic | ✔ | argv→subprocess list-form; 35 os.execv bootstrap |
| S8786 | 229 | architectural_debt | ✘ | regex super-linear: 79 corrigidos (1125x ganho), 150 <9ms won't fix |
| S6549 | 59 | accepted_domestic | ✘ | exists()/stat() sobre artefatos; reais omnimind.py:400/402/409 |
| S6466 | 52 | false_positive | ✔ | 52/65 slices que nunca lançam |
| S6929 | 41 | architectural_debt | ✘ | dim= explícito — 9 corrigidos, 32 wontfix declarado |
| S6709 | 23 | architectural_debt | ✘ | random_state/seed — 23/23 corrigidos (reprodutibilidade) |
| S6096 | 11 | future_public_risk | ✘ | tarfile baixado (HF/Zenodo) — zip-slip, filter='data' |
| S8706 | 6 | future_public_risk | ✘ | sqlite file:URI — #/? injeta parâmetro; urllib.parse fix |
| S3699 | 3 | real_vulnerability | ✘ | retorno-None consumido como True — corrigidos |

Batch-suppressible (12): S8707, S7688, S2083, S5443, S2245, S8705, S8701+, S8703, S6466,
S5332, S1313, S1764. **Sem** batch: BUGs, dívida, risco-futuro e vulnerabilidades reais.

### 3.4 SonarCloud export (6.394 issues) — taxa de aceite

| Resolução | N | % |
|---|---|---|
| WONTFIX (aceitas) | 4.886 | 76,4% |
| FIXED | 1.046 | 16,4% |
| FALSE-POSITIVE | 154 | 2,4% |
| REMOVED | 2 | <0,1% |
| **Abertas** | **0** | **0%** |

80 issues têm racional humano/agente (as que explicam o porquê do aceite — o catálogo de
rationales guarda exatamente esses textos).

### 3.5 Work packages (precedente de fluxo de trabalho)

10 pacotes com `{scope, agent, status}`: A devin "10 bugs P0" done; B agy "async ~102 sites"
running; C codex "lógica morta + branches idênticos" done; D "auditoria erika-C -fsanitize"
pending; E "NaN-idiom → math.isnan" pending; F codex "regex S8786 + reprodutibilidade" done;
G "codemod shell S7688 / wontfix em massa" pending; P1 devin "rede: auth cli_bridge +
verify_file_hash + bluetooth bind" pending; P2 "sinks: shlex.quote, file-URI sqlite RO,
zip-slip" pending; P3 "fontes não confiáveis + saneamento uniforme" pending.

**Regra empírica 2**: o fluxo real do projeto é "classificar veredito primeiro, depois
agrupar em work package temático com agente e status" — não correção solta.

### 3.6 Práticas extraídas (15) — as regras de ouro do projeto

1. `security`: shell=True só com pipeline list-form (shlex.quote)
2. `security`: bind/CORS configuráveis por env (0.0.0.0 só doméstico)
3. `security`: validar IPs com `ipaddress.ip_address()` em sinks
4. `security`: filas de segurança fora de /tmp world-writable (dir 0700)
5. `security`: endpoints HTTP ativos exigem auth mínimo (CSRF em 127.0.0.1)
6. `security`: sanitizar campos de request antes de log (S5145 \n\r)
7. `async`: subprocess/requests/input/sleep em corrotinas → asyncio.to_thread
8. `async`: guardar referências de create_task (S7502 GC)
9. `regex`: medir antes de reescrever (t(2n)/t(n)>2.5 ou >20ms adversarial)
10. `regex`: seeds explícitas para reprodutibilidade (S6709)
11. `persistence`: escrita atômica com lock para JSON canônico
12. `persistence`: retorno bool em helpers de persistência
13. `architecture`: separação doméstico vs oficial é princípio permanente
14. `architecture`: classe de veredicto antes de corrigir (rationale sempre preservado)
15. `architecture`: chattr-ritual para arquivos imutáveis (-i → patch → validar → +i)

## 4. Design da base de priors (implementado)

`scripts/quality_triage/derive_priors.py` — lê um export de triagem (findings +
rule_verdicts + practices) e deriva `data/code_quality/priors.sqlite`:

```sql
CREATE TABLE rule_priors (
  rule TEXT PRIMARY KEY, total INTEGER,
  verdict TEXT,             -- veredito histórico dominante
  verdict_dist TEXT,        -- json {verdict: count}
  confidence REAL,          -- share do veredito dominante
  batch_suppressible INTEGER,
  rationale TEXT            -- rationale dominante (template)
);
CREATE TABLE practices (domain TEXT, principle TEXT, detail TEXT, source TEXT);
CREATE TABLE meta (source TEXT, findings INTEGER, derived_at TEXT);
```

Execução real sobre o corpus: **96 regras, 5.981 findings, 15 práticas** derivadas.
Exemplos vivos: S8707 `accepted_domestic` conf 1.0 + suppressible; S1244 `review_needed`
conf 1.0 **não** suppressible (nuance: confiável mas não auto-aceitável).

## 5. Filtros e regras derivadas (implementados em `triage.py`)

1. **Auto-veredicto**: regra com prior conf ≥ 0.90 E batch_suppressible → `accepted_domestic`
   com o rationale histórico dominante.
2. **Gate de severidade**: BLOCKER/CRITICAL em código próprio → sempre `review_needed`
   (prior nunca suprime severidade-gate; em vendored, o gate cede ao prior).
3. **Escalada**: regra sem prior, conf < 0.90, ou não-suppressible → prompt ao brain
   analyst com `{history, rule, severity, file:line, message, snippet}` → veredito JSON
   `{verdict, confidence, rationale}`; fallback heurístico `review_needed` se brain
   indisponível.
4. **Feedback loop**: veredito gravado na tabela `findings` do próprio priors.sqlite
   (PK rule+file+line) — a decisão de hoje vira prior de amanhã.
5. **Categoria como prior secundário**: BUG → nunca auto-aceito; VULNERABILITY em
   sinks de E/S (tarfile, sqlite file:URI, SQL-id, shlex) → tendência
   `future_public_risk`/`real_vulnerability`.

## 6. Prompt executável pelo modelo (em `triage.py`)

```text
Você é o revisor de qualidade do worker. Classifique o achado.

Histórico da regra no projeto: {history}
Regra: {rule} | Severidade: {severity} | Arquivo: {file}:{line}
Mensagem: {message}
Trecho: {snippet}

Vereditos possíveis: accepted_domestic | review_needed | architectural_debt |
false_positive | real_vulnerability | future_public_risk
Responda em UMA linha JSON: {"verdict": "...", "confidence": 0.0-1.0,
"rationale": "uma frase técnica"}
```

A chamada usa o brain analyst (`role='analyst'`, temp 0.2, ≤160 tokens) — o mesmo
caminho `agents._llm.brain_chat` da malha. O modelo executa o prompt e retorna o
veredito JSON parseado; falha → fallback determinístico.

## 7. Ponto de integração recomendado

**Não** é tópico de kernel em tempo real — é camada de auditoria sob demanda:
1. `scripts/quality_triage/triage.py` consome findings (ruff/sonar jsonl);
2. classifica contra `data/code_quality/priors.sqlite`;
3. grava vereditos de volta (feedback);
4. a **coding_battery** passa a ler os priors como pré-filtro do estágio de review
   (evita re-avaliar o que o histórico já decidiu);
5. relatórios de triagem alimentam `docs/audits/` (auditoria do worker), mantendo
   `docs/audit/` reservado aos packs soberanos.

## 8. Verificação (ao vivo)

- `derive_priors.py` sobre o corpus → 96 regras/5.981 findings/15 práticas.
- `triage.py` sobre 6 achados sintéticos: S8707 auto-aceito via prior (2), S1244
  escalado (conf 1.0 mas não suppressible), S9999 BLOCKER próprio → gate review,
  S9999 BLOCKER vendored → prior, regra desconhecida → fallback. 6/6 corretos.
- Testes `tests/test_quality_triage.py`: 6 testes verdes (auto, escalate,
  gate, conf-fraca, unknown, roundtrip persistência).

## 9. Estatuto e limites

- **[DADO]**: números e vereditos citados §3 vêm direto dos arquivos extraídos.
- **[DERIVADO]**: regras §5 são heurísticas derivadas das distribuições §3.2/§3.3.
- **[LIMITE]**: a triagem classifica e recomenda; **não** corrige código sozinha —
  correções seguem o fluxo histórico de work packages com agente+status (ver §3.5).
- O corpus é do domínio soberano; a base de priors é um **subproduto derivado**,
  sem copiar código-fonte proprietário para o worker (só regras, vereditos e
  rationales-condensados).