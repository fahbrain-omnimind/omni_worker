# OW-AUD-019 — Mapa de execução (agy)

Fonte: `docs/audit/OW-AUD-019_judge_kaggle_competition_and_sota_comparison.md` (33 linhas, lido integralmente).
Método: leitura do código/docs no HEAD `95ee5e1`. Nenhum arquivo de código foi alterado. Este é o único arquivo criado.
`W` = `docs/PAPER_WRITEUP.md`.

Estado informado pelo usuário e **não reverificado** por mim: API fail-closed, kernel 3/3, freud10d+dendritic, writeup corrigido, Apache-2.0, framing detector, G7+G9. Só verifiquei a licença (`LICENSE:2`, `README.md:3`).

## Achados críticos (verificados)

1. **[DADO]** O writeup está **muito acima de 3000 palavras**. `wc -w` dá 5990 no arquivo todo e 5497 até o "Checklist". O limite do Kaggle é ≤3000. É o bloqueio nº 1 para a submissão. O checklist em `W:254` continua `[ ]`.
2. **[DADO]** O número de testes diverge. `W:180` diz "455 testes". `pytest --collect-only` coletou **469**. Isso só coletou, não rodou a suíte.
3. **[DADO]** O "0/88 degeneração" que o OW-AUD-019 cita em §4.3 **já foi removido** do abstract (`W:15`, "ledger lost on VM recycle"). Não deve ser reintroduzido.
4. **[DADO]** O prazo do Paper Track é 12/11/2026 23:59 UTC. Hoje é 04/11, restam 8 dias. O Paper Track e a Main competition (02/12) são deadlines distintos.

## Mapa item a item

### §1 — Fatos das competições (informativo, sem ação direta)
O conteúdo é externo e não verificável no código. **[LIMITE]** Não revalidei as afirmações externas (arXiv 2606.13705, números Qwen vs Gemma, model card). A única ação derivada é a conferência das citações no writeup (ver R5).

### §2 — Gaps SOTA

| # | Gap | Status | Evidência | Proposta |
|---|---|---|---|---|
| 2a | N maior que 3 e baseline de prompt/scaffold | **PARCIAL** | O N=3 está rotulado como exploratório (`W:171`, `W:228`). A comparação com a comunidade existe só em texto (`W:236`). Não há baseline de scaffold nem N>3 (`W:252`: 26B-A4B ausente dos agent-runs). | Ver R1. |
| 2b | Intervenção de pesos, probes/SAE, método explícito | **PARCIAL** | Roy & Vetterli citado em `W:238`. rank~1 basal e fid≡1.0 declarados em `W:228`. O `grep` por "probe/SAE" não achou comparação em `src`/`scripts`/`W`. Não há neuron surgery. | O neuron surgery fica **fora de escopo** (o posicionamento em `W:237` já o diferencia). Ver R6 para o texto do método. |
| 2c | Efeito binário NS, escala e ablação de K | **PARCIAL** | O McNemar p≈0.45 e o Wilson 95% estão reportados (`W:155`, `W:228`). O K=30 é descrito como sensível demais (`W:228`), mas não há ablação de K. | Ver R7. |
| 2d | Comparar com outros proxies de consciência | **PENDENTE** | PyPhi e GWT-lite estão em `W:215`. Não há comparação com information bottleneck ou causal emergence. | Ver R8 (o mais barato é uma frase de escopo, não um experimento). |

### §3 — Gaps do writeup

| Item | Status | Evidência |
|---|---|---|
| (i) dual-brain, peer-swap, chat-template | **EXECUTADA** | `W:182` (§3.4a), abstract `W:15`. |
| (ii) captura espectral e trajetória por passo (`OMNI_ACT_STEP_EVERY=8`) | **EXECUTADA** | `W:189` (§3.4b). Código: `src/omni_coworker/server/erika_torch_server.py:181` e `:219`. O default no código é `"0"`. O "=8" depende de env, e eu não verifiquei onde o 8 é definido (`scripts/start_omni_worker.sh` apareceu no grep, não li). |
| (iii) refatoração multi-turno e `coverage_missing` | **EXECUTADA** | `scripts/refactor_battery/run_battery.py:243,259,272`. Writeup: `W:209` e `W:235`. |
| (iv) supervisão afetiva L0–L4 (16/16) | **EXECUTADA** | `W:213` (§3.4d); `scripts/supervisor_battery`. O 16/16 é afirmação do writeup. Não reexecutei a bateria. |
| Posicionamento competitivo | **EXECUTADA** | `W:231` (§5), com scaffold/capacity em `W:236` e neuron surgery em `W:237`. |
| Claim "Best New Application" | **EXECUTADA** | `W:7` e `W:178`. |
| Limitações de generalização mais fortes | **EXECUTADA** | `W:228` cobre N=3, κ=0.4722, janela ~120 tokens, cascade subpotente. |

### §4 — Críticas do revisor

| # | Crítica | Status | Evidência e lacuna |
|---|---|---|---|
| 1 | Correlação N=3: bootstrap/permutation, N maior | **PARCIAL** | Rotulada como exploratória (`W:171`, `W:176`: "artefato de 3 pontos"). O `grep` por bootstrap/permutation em `scripts`/`src`/`W`/`docs/results` não achou nada. **Bootstrap/permutação com N=3 é matematicamente vazio**: só existem 6 permutações, então o menor p exato é 1/3 em teste bilateral. A mitigação honesta é reportar como "descritivo" (já feito), não calcular IC. N maior só vem de R1. |
| 2 | Degeneração é artefato de protocolo | **PARCIAL** | A ablação 0% vs 62.5% está no abstract (`W:15`). Wilson aparece no pilot cascade (`W:155`). Falta confirmar IC e tamanho de efeito para 0% vs 62.5% e a ablação formato-casada na quantização (§3.2b). Não li §3.2c por inteiro. |
| 3 | Sem score SWE-bench | **PARCIAL** | Métricas internas existem (`W:15`: 30/30 compile, 16/16 afeto). Falta uma frase explícita "aplicação/supervisão, não leaderboard". Contagem de testes errada (achado 2). |
| 4 | IIT overreach | **PARCIAL** | Φ=0 e GWT-lite honestos, PyPhi 1.2.0 citado (`W:215`). **Disclaimer explícito de escopo**: o `grep` por disclaimer não achou. |
| 5 | Novelty vs neuron surgery | **EXECUTADA** | `W:237` cita arXiv:2606.13705 e diferencia. |
| 6 | Proveniência (sqlite, SHA256, seeds) e links públicos | **PARCIAL** | SHA256 de juízes (`W:251`) e do dataset de terceiros (`W:260`). **O SHA256 está em `/tmp/gemma4_corr/provenance.json`, local e volátil.** Links públicos do próprio recurso: ausentes (`W:253`). |

### §5 — Recomendações

| Recomendação | Status | Evidência |
|---|---|---|
| Finalizar writeup ≤3000 palavras (3.4a–d) | **PENDENTE** | 5497 palavras (achado 1). As seções 3.4a–d existem (`W:182–213`), assim como "Competitive Positioning" (`W:231`). O "Reproducibility" é só a lista curta de `W:241`. |
| Dataset público (V10 + runs + análise) | **PENDENTE** | `W:243` é a intenção e `W:253` está `[ ]`. Não achei metadados de dataset (`dataset-metadata.json`). O grep foi limitado a `scripts` e `docs`. |
| Submeter antes de 12/11; arXiv opcional | **PENDENTE** | `W:255` e `W:256` estão `[ ]`. |
| Manter git read-only | **N/A** | Esta execução não alterou código. |

## Propostas para PENDENTE/PARCIAL

**R1 — Cortar o writeup para ≤3000 palavras (prioridade P0, bloqueante)**
- Alvo: `docs/PAPER_WRITEUP.md`. Criar uma cópia de submissão, por exemplo `docs/PAPER_WRITEUP_SUBMIT.md`, e manter o original como versão longa.
- Mudança: mover o detalhe de §3.4a–d, §3.2e e "Dados já verificados" para um apêndice ou para o repositório. Manter na versão curta o abstract, o §3.2c, o §3.2d, o §3.3 e a limitação em um bloco.
- Risco: cortar uma evidência que a rubrica de Verifiability exige. Mitigação: deixar link para o doc longo e para o commit. Confirmar o método de contagem do Kaggle, porque tabelas e código podem contar diferente.

**R2 — Dataset público Best New Resource (P0)**
- Alvo: novo diretório `release/kaggle_dataset/` com `dataset-metadata.json`, a bateria V10, os sqlite exportados em CSV, os scripts de correlação e um `MANIFEST.sha256`. Os 2 sqlite citados em `W:264` são `embodied_psychodiagnostic_bank.sqlite` e `v10_colab_benchmark.sqlite`.
- Risco: vazar secrets ou dados de terceiros. Licenciar os dados do Gluzdov (CC BY 4.0, `W:260`) só por referência e não redistribuir. Varrer o conteúdo por tokens antes de publicar. A publicação exige credencial Kaggle do usuário (ação sua).

**R3 — Corrigir contagem de testes (P1, trivial)**
- Alvo: `W:180`. Rodar `pytest` completo, não só collect, e escrever o número realmente aprovado (469 coletados). Risco: baixo.

**R4 — Sentença de escopo "aplicação, não leaderboard" (P1)**
- Alvo: `W:178` ou §4. Uma frase dizendo que não há score SWE-bench e que as métricas são internas. Risco: nenhum.

**R5 — Verificar citações externas (P1)**
- Alvo: `W:235–237`. Checar arXiv:2606.13705 e os números da comunidade na fonte. Risco: citar dado externo não confirmado. Se a fonte não abrir: "NÃO LOCALIZADO", e remover ou marcar como não verificado.

**R6 — Método do eff_rank e limitações (P2)**
- Alvo: `W:189–207`. Definir participation ratio (Roy & Vetterli) numa linha e remeter a rank~1 basal e fid≡1.0 (`W:228`). Risco: baixo.

**R7 — Ablação do threshold K (P2, experimento)**
- Alvo: `scripts/experiments/run_intervention_experiment.py` (K=30 não foi localizado pelo grep, então o parâmetro precisa ser confirmado antes). Varrer K e relatar com Wilson, McNemar e tamanho de efeito.
- Risco: custo de GPU (T4×2 no Kaggle). Resultado pode continuar NS, e então reportar como tal. Só entra no paper se terminar a tempo. Caso contrário, manter em limitações.

**R8 — Disclaimers IIT e proxies (P2)**
- Alvo: `W:215`. Acrescentar: Φ é do blanket de 4–6 nós, não do modelo, não prova consciência, e outros proxies (information bottleneck, causal emergence) **não foram avaliados**. Risco: nenhum, só reduz o claim.

**R9 — Reprodutibilidade e proveniência persistente (P1)**
- Alvo: `W:241` e `W:260`. Copiar `/tmp/gemma4_corr/provenance.json` para dentro do repo (por exemplo `docs/data/`), porque `/tmp` é volátil. Acrescentar seeds, SHA256 e comandos de reprodução. Verificar o arquivo antes de copiar. Se já sumiu: "NÃO LOCALIZADO", e regenerar a partir do dataset v8.
- Risco: o hash não bater com o dataset atual (versão v8).

**R10 — Submissão (P0, ação sua)**
- O submit explícito e os links sem login (`W:255–256`) exigem sua conta Kaggle. Prazo: 12/11/2026 23:59 UTC. Sugestão de ordem: R1 → R3/R4/R8 → R2/R9 → R10, com R5 em paralelo e R7 só se sobrar tempo.

## Limites desta apuração
- Não executei a suíte de testes nem baterias, só `--collect-only`.
- Não li o writeup inteiro linha a linha, só as seções citadas. Os status "PARCIAL" de §4.2 dependem de §3.2c, que não li por completo.
- Greps negativos (bootstrap, probe/SAE, disclaimer, K=30, dataset-metadata) cobrem só `src`, `scripts`, `docs` e `W`. Não cobrem `data/`, `/content/drive` (proibido) nem outros repos.
