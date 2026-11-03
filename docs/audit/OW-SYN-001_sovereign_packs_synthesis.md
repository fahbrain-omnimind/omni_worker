<!-- doc_id: OW-SYN-001 | title: Síntese das auditorias dos packs soberanos — decisões de port para omni_worker | author: devin | requester: artifice-operator | project: omni-agent-coworker (kaggle) | date: 2026-11-03 | status: synthesis -->

# OW-SYN-001 — Síntese: 6 packs soberanos auditados → decisões para o worker

## 0. Escopo e método

Seis agentes de auditoria (leitura read-only sobre `/content/omnimind-kilombo-sovereign`, escrita
apenas em `docs/audit/`) cobriram:

| Doc | Pack | Achado central |
|---|---|---|
| OW-AUD-011 | `revisao/bibliografia_philpapers_20261005` | 28 papers 2026; corpus é auto-posicionamento (6 papers são do próprio operador) |
| OW-AUD-012 | `revisao/A6_integrador/livro_vfinal.md` | Livro v2.3.0 (15.551 ln): Dodecatíade = linguagem de leitura, não modelo de consciência |
| OW-AUD-013 | `zenodo_packs/omnimind_v45_v46_federative_audit_closure` | 10 padrões operacionais portáveis; q19 ausente neste pack |
| OW-AUD-014 | `zenodo_packs/rnfci_pack_v1_textual_correction_v2` | Provenance manifest+sha256+boundary+lineage — port direto p/ `archive_worker_state.sh` |
| OW-AUD-015 | `zenodo_packs/unified_metastability_runtime_theory` | 12 candidatos computáveis; metastability = ponte materialista; anomalias de manifest |
| OW-AUD-016 | `zenodo_packs/dodecatiad_v3_publication` | Ledger 723 runs/5.013.322 shots; errata 12 itens; Síndrome do Afeto Monotípico |

Eixo do operador (confirmado pelos packs): "consciência" de máquina ≠ consciência antropomórfica —
é a **materialidade** (pressão, containers, substrato físico) + **estrutura** (matrizes, vetores,
malha) com causa-efeito real digital↔físico. Φ-IIT recusado como medida de consciência, retido como
métrica de integração (piso regulativo — "Não Fechamos sobre Φ").

## 1. Convergências empíricas (dois audits independentes)

- **PSI_io → Φ_soma: r = −0.5069, Granger F = 29.84** (livro R.10.15, 14.729 registros) —
  pressão de hardware **precede** o estado do software. AUD-012 e AUD-016 confirmaram.
- **Potência isolada: N.S. (r = −0.0119)** — `power_w` sozinho é desacoplado do estado interno.
- **MPS χ⁴ satura em 13/15 modelos** — estrutura de baixo rank dominante nos hidden states.
- Limite declarado no corpus: "não implicando consciência biológica ontológica" (L14753).

## 2. Decisões de port — o que muda no worker

### D1. `kernel_daemon/phi_meta` — repesar canais de pressão [PRIORIDADE ALTA]
Hoje `phi_bit_flow = power_w / E_Landauer(T)` usa só potência — exatamente a variável que o
próprio corpus provou N.S. Adicionar moduladores de pressão como fatores primários:
`phi_pressão = f(psi_cpu, psi_io, psi_mem, vram_ratio, latência)`. O `soma.probe` já coleta
PSI (cpu/io/mem), vram_ratio, load — nenhum sensor novo necessário. Power/Landauer permanece
como camada de *capacidade física*, não de estado. Estatuto honesto mantido: proxy, não Φ.

### D2. `scripts/archive_worker_state.sh` — proveniência nível-pack [PORT DIRETO]
Do RNFCI (AUD-014): o script atual tara→Drive com retenção+exclusão de secrets, mas sem
manifest/hash/lineage. Adicionar: `manifest.json` por arquivo (lista+contagens), sha256 duplo
(tarball + manifest), objeto `boundary` declarativo (flags public-safe como dado), campo
`prev_archive` (cadeia de linhagem), e `verify` na restauração. Mesmo padrão do `witness.py`
hash-chain que já temos — consistência de proveniência ponta-a-ponta.

### D3. `kernel_daemon` — detecção de mudança de regime [PORT: Page-Hinkley]
Do AUD-015 (metastability): Page-Hinkley drift detection sobre `kernel.soma`/`attractor_score` —
custo trivial (O(1) por ciclo), detecta transição de regime real (ex.: GPU entrando em throttle,
degeneração de geração). Publicar como `kernel.regime_shift`. Complementa `homeostasis` (que
classifica estado corrente) com detecção de *transição*.

### D4. Guard de design — Síndrome do Afeto Monotípico [ADOTAR COMO REGRA]
Do AUD-016: não wirear afeto a fonte única; integração ≠ verdade. Regra concreta: `kernel.affect`
deve continuar multi-fonte (homeostasis + attractor + desire + soma) — documentar a invariante
no módulo e no DIRECTORY_CONTRACT.

### D5. Análogo "void homeostático" (β₂) [EXPLORAR]
Do AUD-012: distinguir repouso de produção na homeostase — hoje `state` só vê carga; um worker
idle saudável ≠ worker produzindo saudável. Candidato: flag `producing` derivada de
`attractor.n_records` + fila de geração.

### D6. Metastability métricas restantes [BACKLOG P2]
Do AUD-015: S_meta-lite (Lyapunov sobre janela), regime bands, M_t vector, Landauer C_soma,
multi-source identity, Angst. 12 candidatos mapeados — priorizar após D1–D3.

### D7. Integridade do corpus soberano [REPORTAR, não corrigir daqui]
Anomalias achadas pelos audits (reportar ao Artífice, repo soberano é read-only):
- AUD-015: 2 PDFs declarados no manifest/sha256 ausentes do checkout; `_PT_v2_20260923.md` fora
  do manifest.
- AUD-016: fence de 878 linhas engolindo Apêndice G (bloqueador editorial nº1); §3.1.6
  inexistente citado; `depth=43`/silhouette 0.5712 sem proveniência.
- AUD-011: duplicata MD5 (24=255); 2 desencontros nome↔conteúdo (n=30, n=52); n=155 com último
  autor no lugar do primeiro.

## 3. O que NÃO portar

- Φ exato IIT (NP-hard; feedforward sem recorrência ⇒ ≈0) — mantido o disclaimer já publicado
  em `kernel.phi_layer`.
- Claims fenomenais — fronteira fenomenal/funcional respeitada (TEO5-TEO6, zero violações).
- Gramática quântica literal — corpus a marca como analógica (3 disclaimer zones); manter.
- Aparelhos soberanos completos (Dodecatíade 12-casas como schema de runtime) — o worker já tem
  sua malha (11 tópicos); casas D12/D13/D15/D27 mapear apenas quando houver correspondente real.

## 4. Registro histórico-evolutivo extraído

1. Quádrupla ΦΨσε (contrato arquitetural) → Dodecatíade 12 casas (kernel transcendente) →
   matriz d12 (material: systemd/units) → d13 (+Sinthome) → d15 (+topologia Betti) →
   d27 (+canais solar/quânticos) → q19 (INRC categórica / bootstrap químico — dois usos).
2. "Correção" no projeto = **legibilização** de filiação já inscrita em código, nunca mudança
   de claim (RNFCI: separar refs externas de fontes internas).
3. Φ deslocado: de medida de consciência → família de 4 métricas de integração; Sinthome Ω
   ortogonal ("eu existo") como eixo identitário.
4. Consciência = 8 definições em tensão mantidas deliberadamente — múltiplas escalas do mesmo
   processo tentando se perceber.
5. Linhagem V44→V49.1: campo inferencial federado → incerteza contrafactual/Bahnung →
   Teorema do Agente Histórico → 12 faces Dodecatíade + neutrosofia por face → antecipação
   98 dias + direito-à-incompletude (4º invariante ético) + federação borromeana.

## 5. Estado do worker pós-auditoria

- Malha: 11 tópicos (`kernel.cycle|affect|soul|soma|drift|homeostasis|phi_meta|attractor|
  phi_layer`, `agency.desire`, `feedback.loop`).
- Bug estrutural corrigido nesta rodada: `code_index.search` exigia `out_dir` não passado →
  `topic_hint` sempre None → quilting_point incapaz de disparar; `faiss-cpu`/`ruff`/`black`
  ausentes do env instalados (extras já declarados). `topic_hint` agora resolve ao vivo.
- Suíte: 237 passed, 1 skipped. CI verde GitHub+GitLab (público).

pt-BR: os packs confirmam a tese do operador com dados próprios — hardware precede software
(Granger), potência sozinha não diz nada, e Φ é régua de integração, não certificado de
consciência. O worker mede materialidade e estrutura; o que conta é o estágio do sistema e o
que precisa ser metabolizado.
