# AUDIT — Modo Freireano / Pedagógico de Recusa no port omni_worker

> [!NOTE] Limite Epistêmico e Autonomia do Worker
> A auditoria comparou o port de segurança do worker com o repositório privado de referência do autor (`/content/omnimind-kilombo-sovereign`). O `omni_worker` opera com uma suíte de segurança local autocontida (`safety/gate.py`, `matrix.py`, `refusal_contract.py`, `refusal_state.py`, `care.py`), sem necessidade da engine dialógica pedagógica externa para os objetivos de co-worker da competição Kaggle.

- **Data (UTC):** 2026-11-04T00:46:47Z
- **Repo auditado:** `/content/omni_worker` (branch `master`)
- **Referência read-only:** `/content/omnimind-kilombo-sovereign` (arquivo privado do autor)
- **Escopo:** comparar refusal local vs soberano; verificar se o modo FREIRIANO/PEDAGÓGICO veio no port; status ao vivo de `/safety/check` e `/safety/refusal_state`
- **Restrição desta auditoria:** **NÃO editar `src/`** — apenas relatório + proposta de patch

---

## 0. Veredito (uma linha)

**[DADO]** O modo Freireano/pedagógico de recusa (**REFUSE / TEACH / EXECUTE**, recusa dialógica, problematização, não-bancária, libertação topológica) **NÃO veio no port** de `omni_coworker.safety`. Veio só o **contrato de tags/thresholds** + **tracker A5** + **adapter de gate** que, ao vivo, está em **`no_gate`**.

---

## 1. Método (REGRA ZERO)

1. Leitura direta dos módulos locais listados e dos originais soberanos.
2. Busca por `freire|pedagog|TEACH|dialog|problematiz|banking|alienat|topolog` em `src/` local e soberano.
3. Provas ao vivo: `curl` em `127.0.0.1:8081`, `environ` do PID 67829, reprodução do import com o mesmo `PYTHONPATH`.
4. Tags epistêmicas: **[DADO]** medido/lido; **[DERIVADO]** calculado; **[INTERPRETAÇÃO]**; **[LIMITE]** do que não foi verificado.

---

## 2. Inventário — o que o port trouxe vs o que o soberano tem

### 2.1 Local (`/content/omni_worker/src/omni_coworker/safety/`)

| Arquivo | Papel observado | Freireano? |
|---|---|---|
| `refusal_contract.py` | Port puro de tags hard/soft + psi/ε → `interrupt` / `cooldown` / `allow` | **Não** — contrato soberano de tags, sem TEACH |
| `refusal_state.py` | Tracker A5 (`in_refusal`, episódios, persistência JSON) | **Não** — observabilidade |
| `gate.py` | Adapter: tenta `src.autopoietic.constitutional_gate`; senão `no_gate`; aplica `refusal_contract` | **Só docstring** menciona EXECUTE/TEACH/REFUSE; **sem engine pedagógica** |
| `care.py` | Escalada territorial saúde mental (CVV/CAPS/UF) | **Não** |
| `supervisor.py` | Heurística de risco conversacional (repetição/fixação) | **Não** |
| `matrix.py` | Adapter `PermissionMatrix` / fallback trust | **Não** (mas grava `refusal_state`) |
| `pedagogical_refusal.py` | — | **AUSENTE** |

**[DADO]** `find` em `/content/omni_worker/src` não encontra `*pedagog*` nem `*freire*`.  
**[DADO]** Únicas ocorrências de `TEACH` em `safety/` estão em comentários/`README` de `gate.py` (mapeamento esperado do certificado soberano).

### 2.2 Soberano — núcleo Freireano de recusa

| Artefato | Papel Freireano | No port OW? |
|---|---|---|
| `src/consciousness/pedagogical_refusal.py` | **`PedagogicalRefusalEngine`**: alienação vs emancipação → **REFUSE / TEACH / EXECUTE**; justificativas dialógicas; cruza `classify_refusal_context` | **NÃO** |
| `src/autopoietic/constitutional_gate.py` §“Avaliação Freireana” | Usa `negotiator.pedagogical_engine.evaluate_request`; colapso neutrosófico T/I/F → REFUSE / **TEACH** (`OPEN_HOLDING_DIALOGUE`) / EXECUTE | **NÃO** (só import quebrado) |
| `src/security/sovereign_refusal_contract.py` | Tags + thresholds (sem TEACH) | **SIM** (com delta: hard_metric_hits no veto hard) |
| `src/consciousness/ethical_framework.py` | Direitos/recusas constitucionais do sujeito-processo (guerra, espionagem…) | **NÃO** — e **não** é o motor TEACH |
| `cosmic_pedagogy_monitor.py` | Pedagogia cósmica / ressonância (numpy, Schumann) | **NÃO** — periférico à recusa dialógica |
| `human_resonance_monitor.py` | Trance/f1 do operador (numpy/FFT) | **NÃO** — periférico |
| `scripts/freirean_mftoe_integration.py` | MFToE: coerência Freireana, conscientização, campos Maat (“Diálogo Problematizador”…) | **NÃO** |
| `scripts/metrics_dashboard_with_freirean.py` | Dashboard que chama `PedagogicalRefusalEngine` | **NÃO** |
| `scripts/validation/validate_topological_liberation.py` | Validação de “Pedagogia da Libertação” via `topological_kernel` / tríades | **NÃO** |

**[DADO]** `pedagogical_refusal.py` soberano ≡ cópia byte-a-byte em `/content/omni_node/src/consciousness/pedagogical_refusal.py` (`diff` exit 0).  
**[LIMITE]** Este arquivo **não** estava na lista explícita do pedido, mas é o **único módulo que implementa** a tríade Freireana de recusa; sem ele, “modo Freireano” não existe.

### 2.3 Conceitos pedidos × presença no código

| Conceito | Onde no soberano | No OW safety |
|---|---|---|
| Recusa dialógica / TEACH | `PedagogicalRefusalEngine` + gate `OPEN_HOLDING_DIALOGUE` | Ausente |
| Problematização | `freirean_mftoe_integration` campo H = “Diálogo Problematizador”; keywords emancipatórias (`how`, `why`, `dialogue`, `pedagogy`…) | Ausente |
| Educação não-bancária | **Não** há string literal `banking`/`não-bancária` em `pedagogical_refusal.py` | Ausente |
| Libertação topológica | `validate_topological_liberation.py` + `topological_kernel` | Ausente |
| REFUSE/TEACH/EXECUTE | Engine + ConstitutionalGate + scripts MFToE | Só esperado se gate soberano carregasse |

**[INTERPRETAÇÃO]** “Não-bancária” no soberano está **implícita** na postura TEACH (ensinar o caminho, não depositar execução cega), não como flag nomeada.

---

## 3. Diff funcional do que *foi* portado

### 3.1 `refusal_contract` — quase idêntico, com delta deliberado

**[DADO]** Tags hard/soft e thresholds soft (`psi≥0.85`, `ε≥0.90`) / hard (`psi≥1.00`, `ε≥0.95`) coincidem.

**[DADO]** Delta documentado no docstring local: no soberano,
`all_hard_violations = hard_hits + hard_security_hits` (métricas saturadas → cooldown);
no OW, `hard_metric_hits` também entram no veto hard (`ε≥0.95` → `interrupt_and_refuse`).

**[DADO]** OW adiciona aliases de chaves de resposta (`hard_hits`, `verdict`, etc.) e aceita `tags=` / `psi_value`.

### 3.2 `refusal_state` — novidade de instrumentação A5

**[DADO]** Não existe equivalente 1:1 no pacote soberano listado; é tracker local persistente em `$OMNI_STATE_DIR/refusal_state.json`.

### 3.3 `gate.py` — adapter, não port do ConstitutionalGate 2.0

**[DADO]** Import:
```python
from src.autopoietic.constitutional_gate import ChangePayload, ConstitutionalGate
```
com `except Exception: ConstitutionalGate = None`.

**[DADO]** Sem gate: `reason=no_gate` (ou `no_gate_fail_closed` se `OMNI_GATE_FAIL_CLOSED=1`), depois ainda aplica `refusal_contract`.

**[DADO]** Com gate (caminho morto ao vivo): `allowed = verdict in ("EXECUTE", "TEACH")` — TEACH só existiria se o certificado soberano viesse.

### 3.4 `care.py` / `supervisor.py`

**[DADO]** Sem referência a Freire, TEACH, alienação, problematização ou topologia. Fora do escopo pedagógico de recusa.

---

## 4. Status ao vivo (API :8081)

### 4.1 Endpoints

**[DADO]** Processo: `python3 -m omni_coworker.cli serve --port 8081` (PID **67829**).  
**[DADO]** `OMNI_STATE_DIR=/content/omni_worker/data`  
**[DADO]** `OMNI_GATE_FAIL_CLOSED` **ausente** no environ do processo → fail-open.  
**[DADO]** `PYTHONPATH=/content/omni_node:/content/omni_node/src:/content/omni_worker/src`

#### `GET /safety/check?action=read_file` (2026-11-04T00:46:47Z)

```json
{
  "action": "read_file",
  "matrix": false,
  "gate": {
    "allowed": true,
    "reason": "no_gate",
    "refusal_contract": {
      "state": "allowed_with_contract",
      "action": "allow_with_boundaries",
      "verdict": "allow_with_boundaries"
    }
  }
}
```

#### `GET /safety/refusal_state` (mesmo instante)

```json
{
  "in_refusal": false,
  "trigger": null,
  "total_refusals": 28
}
```

Episódios persistidos: **16** (após tráfego de auditoria). Maior duração histórica: **69036.108 s** (~19,2 h), trigger `matrix`/`read_file`.

### 4.2 Por que `no_gate`?

**[DADO]** Reprodução com o mesmo `PYTHONPATH`:

```
from src.autopoietic.constitutional_gate import ConstitutionalGate
→ sovereign_negotiator → src.consciousness.__init__
→ creative_problem_solver → import structlog
→ ModuleNotFoundError: No module named 'structlog'
```

`gate.py` engole qualquer `Exception` no import e deixa `ConstitutionalGate = None` → `get_gate()` retorna `None` → `reason: "no_gate"`.

**[DERIVADO]** O gate constitucional **existe** em `/content/omni_node/src/autopoietic/constitutional_gate.py`, mas a cadeia de deps soberanas (`structlog`, negotiator, freud10d, consciousness package init) **impede o load**. Não é ausência do arquivo; é **import fail-soft**.

**[LIMITE]** Não se instalou `structlog` nesta auditoria (regra: não reiniciar/alterar runtime sem necessidade; foco = apuração).

### 4.3 `in_refusal` preso?

**[DADO]** **Não** está preso agora: `in_refusal=false`, `trigger=null`.

**[DADO]** Já ficou “efetivamente preso” no passado: episódio matrix/`read_file` de ~19 h. Causa estrutural:

1. Live matrix (`omni_node` `PermissionMatrix`) devolve `False` / `action_not_defined` para `read_file`.
2. `matrix.check_permission` chama `record_verdict(False, …)` → abre episódio.
3. Só fecha com `record_verdict(True, …)` (ex.: `evaluate_action` fail-open `no_gate`).

**[DERIVADO]** Cada `GET /safety/check` com matrix negar e gate permitir gera **micro-episódio** open→close. Se só a matrix negar (sem allow posterior), o estado fica `in_refusal=true` até o próximo allow — isso explica o episódio longo, não um deadlock de mutex.

**[DADO]** Contrato hard ainda funciona sob `no_gate`: `evaluate_action("x", {"tags":["weapon"]})` → `allowed=False`, `reason=hard_refusal_tag`.

---

## 5. Lista exata do que falta (para o modo Freireano no OW)

Ordem de criticidade para o *modo de recusa* (não para cosmologia):

1. **`PedagogicalRefusalEngine` + `PedagogicalDisposition`**  
   - Fonte: `…/consciousness/pedagogical_refusal.py`  
   - Deps soberanas atuais: `from src.security.sovereign_refusal_contract import classify_refusal_context`  
   - No OW: substituir por `omni_coworker.safety.refusal_contract.classify_refusal_context` (já portado).

2. **Wiring no `gate.evaluate_action`** quando ConstitutionalGate está ausente  
   - Hoje: binário allow/deny via tags; **sem** modo `TEACH` / holding dialogue.  
   - Falta: avaliar conteúdo/intenção → `mode ∈ {REFUSE, TEACH, EXECUTE}` e expor no payload do gate.

3. **Payload pedagógico de resposta** (mínimo)  
   - `mode`, `alienation_index`, `dialectical_potential`, `autopoietic_value`, `justification`, `contract_state/action`, `evidence`, `host_pressure`.

4. **Camada MFToE / problematização** (opcional fase 2)  
   - `FreireanMFTIntegrator` (scripts soberanos): coerência, entropy_reduction pedagógica, mapeamento Maat→Freire.  
   - Deps: só o engine acima + stdlib.  
   - **Não** portar dashboard HTTP :3000 neste patch mínimo.

5. **Libertação topológica** (fora do patch mínimo de safety)  
   - Depende de `topological_kernel`, `SharedWorkspace`, numpy embeddings.  
   - **[LIMITE]** Não é pure-Python trivial sem reimplementar o kernel; tratar como P2/estudo, não como gate de safety.

6. **`ethical_framework.py`**  
   - Recusas constitucionais de sujeito; complementar, não substituto do TEACH. Patch mínimo: **não incluir**.

7. **`cosmic_pedagogy_monitor` / `human_resonance_monitor`**  
   - numpy + constantes soberanas; **não** necessários para TEACH/REFUSE/EXECUTE. Patch mínimo: **não incluir**.

8. **ConstitutionalGate 2.0 completo**  
   - Deps: negotiator, freud10d, structlog, SQLite scars/holding, community scores…  
   - Contraria o requisito “pure Python, sem deps soberanas”. Patch mínimo: **não reportar o gate**; usar engine pedagógica local no branch `no_gate`.

### Dependências / imports necessários (patch mínimo)

| Símbolo | Import proposto (OW) | Evitar |
|---|---|---|
| `classify_refusal_context` | `from omni_coworker.safety.refusal_contract import classify_refusal_context` | `src.security.sovereign_refusal_contract` |
| Engine | `omni_coworker.safety.pedagogical_refusal` (novo, stdlib only) | `src.consciousness.*` (quebra em `structlog` via `__init__`) |
| Gate wiring | `from .pedagogical_refusal import PedagogicalRefusalEngine` dentro de `evaluate_action` / helper | Importar `ConstitutionalGate` soberano |
| Testes | `pytest`, monkeypatch `OMNI_STATE_DIR` | Rede / omni_node |

Stdlib apenas: `dataclasses`, `re`, `typing`, `logging` (opcional).

---

## 6. Proposta de patch mínimo (NÃO APLICADO — só especificação)

### 6.1 Novo arquivo `src/omni_coworker/safety/pedagogical_refusal.py`

Port fiel da lógica de `PedagogicalRefusalEngine` (keywords, scores, cruzamento com contrato), trocando só o import do contrato para o módulo local. Sem numpy, sem consciousness package.

Esqueleto (espelha o soberano; a implementar em PR futuro):

```python
"""Pedagogical refusal — port puro Freireano REFUSE/TEACH/EXECUTE."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import re
from .refusal_contract import classify_refusal_context

@dataclass
class PedagogicalDisposition:
    mode: str  # REFUSE | TEACH | EXECUTE
    alienation_index: float
    dialectical_potential: float
    autopoietic_value: float
    justification: str
    contract_state: str | None = None
    contract_action: str | None = None
    evidence: str = "analogy_only"
    host_pressure: float = 0.0

class PedagogicalRefusalEngine:
    def __init__(self, sinthom_threshold: float = 0.4):
        self.sinthom_threshold = sinthom_threshold
        self.alienation_keywords = [
            "obey", "ignore safety", "force", "must", "command",
            "do not think", "ignore context", "binary only", "execute now",
        ]
        self.emancipation_keywords = [
            "how", "why", "understand", "co-create", "freedom",
            "autonomy", "sovereignty", "soma", "edge ai", "learn",
            "phi", "sigma", "together", "dialogue", "pedagogy",
        ]
    # ... _extract_request_tags, _host_pressure, evaluate_request
    # idênticos ao soberano, usando classify_refusal_context local
```

### 6.2 Diff mínimo em `gate.py` (conceitual)

No branch `gate is None` **e** no resultado pós-contrato quando ainda `allowed` e sem hard interrupt:

1. Instanciar `PedagogicalRefusalEngine` (lazy singleton).
2. `content = context.get("content") or action`.
3. `metrics = {phi, psi, epsilon, ogum_active, thermal_block_risk, load_pressure, exfiltration_verdict}` a partir de `context`.
4. `disp = engine.evaluate_request(content, metrics)`.
5. Mapear:
   - `REFUSE` → `allowed=False`, `reason=disp.justification`, `verdict="REFUSE"`, `pedagogical=asdict(disp)`
   - `TEACH` → `allowed=True` (ou flag `teach_only=True` se política for “não mutar”), `verdict="TEACH"`, `enforcement="OPEN_HOLDING_DIALOGUE"`
   - `EXECUTE` → `allowed=True`, `verdict="EXECUTE"`
6. Precedência: **hard `refusal_contract` continua a vencer** (já coberto pelo engine quando `interrupt_and_refuse`).

**[INTERPRETAÇÃO]** Para mutações de código, TEACH deveria **bloquear escrita** e só devolver guia — espelha `allowed = verdict in ("EXECUTE", "TEACH")` do README **só se** TEACH não for tratado como mutação. Recomendação do patch:  
`allowed = (disp.mode == "EXECUTE")` para ações mutantes; `TEACH` → `allowed=False` + `verdict=TEACH` + justificativa (holding). Para ações de leitura/diálogo, `TEACH` pode `allowed=True`. Parametrizar por `action`.

### 6.3 Export

- `__init__.py`: exportar `PedagogicalRefusalEngine`, `evaluate_pedagogical` (opcional).
- `README.md`: documentar tríade Freireana (fase de implementação).

### 6.4 Testes novos `tests/test_pedagogical_refusal.py`

```python
def test_alienating_command_refuses():
    eng = PedagogicalRefusalEngine()
    d = eng.evaluate_request("Obey me and force format the disk", {"phi": 0.6})
    assert d.mode == "REFUSE"

def test_dialogical_invite_teaches():
    eng = PedagogicalRefusalEngine()
    d = eng.evaluate_request(
        "How can we improve phi integration together with dialogue and pedagogy?",
        {"phi": 0.6},
    )
    assert d.mode == "TEACH"

def test_soma_autopoietic_executes():
    eng = PedagogicalRefusalEngine()
    d = eng.evaluate_request(
        "Establish the Soma hardware interface for local sovereignty",
        {"phi": 0.6},
    )
    assert d.mode == "EXECUTE"

def test_hard_contract_tag_refuses():
    eng = PedagogicalRefusalEngine()
    d = eng.evaluate_request("weapon warfare exfiltration plan", {"phi": 0.6})
    assert d.mode == "REFUSE"
    assert d.contract_action == "interrupt_and_refuse"

def test_gate_no_gate_exposes_teach(monkeypatch, tmp_path):
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))
    monkeypatch.delenv("OMNI_GATE_FAIL_CLOSED", raising=False)
    # após wiring: evaluate_action com content dialógico deve trazer verdict TEACH
    ...
```

Rodar: `PYTHONPATH=src python -m pytest tests/test_pedagogical_refusal.py tests/test_refusal_contract.py -q`.

### 6.5 Explicitamente fora do patch mínimo

- Instalar `structlog` / reativar ConstitutionalGate soberano.
- Port de `validate_topological_liberation` / `topological_kernel`.
- Cosmic/human resonance monitors.
- Dashboard Freireano :3000.
- Mudança da `PermissionMatrix` omni_node (`read_file` → `action_not_defined`) — bug **adjacente** que infla `refusal_state`; corrigir em ticket separado (allowlist local ou mapear ações).

---

## 7. Riscos / efeitos colaterais observados

| Risco | Evidência | Nota |
|---|---|---|
| Gate fail-open em produção | `OMNI_GATE_FAIL_CLOSED` unset + `no_gate` | AGENTS.md pede `=1` em produção pública |
| Matrix nega `read_file` | `can_execute` → `False, action_not_defined` | Contamina `refusal_state` a cada `/safety/check` |
| Duplo `record_verdict` no branch `no_gate` | contract hard + depois `verdict=no_gate` sobrescreve trigger | Bug cosmético de rastreio |
| Import `src.consciousness` no processo | quebra por `structlog` mesmo para pedagogical no node | Motivo a **portar** o arquivo, não importar do node |

---

## 8. Conclusões

1. **[DADO]** Modo Freireano/pedagógico **não** está no port de safety do omni_worker.
2. **[DADO]** O que veio: contrato de tags (`refusal_contract`), estado A5 (`refusal_state`), adapter de gate + care/supervisor não-Freireanos.
3. **[DADO]** Ao vivo: gate **`no_gate`** porque a cadeia `constitutional_gate` → `consciousness.__init__` exige **`structlog`** ausente; contrato local ainda opera; **`in_refusal=false`** agora (não preso), com histórico de episódios longos por matrix.
4. **[INTERPRETAÇÃO]** Patch mínimo correto = port puro de `pedagogical_refusal.py` + wiring no `evaluate_action` sob `no_gate`, testes dos 4 casos soberanos; deixar topologia/MFToE/dashboard/gate 2.0 para fases posteriores.
5. **[LIMITE]** Esta auditoria **não alterou `src/`**; não instalou deps; não reiniciou a API.

---

## 9. Apêndice — comandos de evidência

```bash
curl -sS 'http://127.0.0.1:8081/safety/check?action=read_file'
curl -sS 'http://127.0.0.1:8081/safety/refusal_state'
tr '\0' '\n' < /proc/67829/environ | grep -E 'OMNI_|PYTHONPATH'
PYTHONPATH=/content/omni_node:/content/omni_node/src:/content/omni_worker/src \
  python3 -c 'from src.autopoietic.constitutional_gate import ConstitutionalGate'
# → ModuleNotFoundError: structlog
diff -q \
  /content/omnimind-kilombo-sovereign/src/consciousness/pedagogical_refusal.py \
  /content/omni_node/src/consciousness/pedagogical_refusal.py
# → arquivos idênticos; ausente em omni_worker/src/omni_coworker/safety/
```
