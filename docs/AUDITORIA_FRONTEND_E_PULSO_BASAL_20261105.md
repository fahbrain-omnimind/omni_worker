# Auditoria Frontend/Dashboard + Pulso Basal de Sincronização 30 min — 2026-11-05

Escopo: `docs/index.html`, `docs/dashboard.html`, `docs/data/dashboard/latest.json`,
`scripts/dashboard_export.py`, produtores ativos (`:8098`, `:8099`, `:8081`,
`kernel_daemon`, `state_guard`, `swap_scheduler`, `archive_loop`) e a nova
rotina `scripts/pulse_dashboard_sync.sh` integrada a `scripts/start_omni_worker.sh`.

Estatuto epistêmico: **[DADO]** medido/verificado com fonte · **[DERIVADO]**
calculado de dados · **[INTERPRETAÇÃO]** leitura · **[LIMITE]** restrição.

---

## 1. Processos e produtores ativos `[DADO]` (ps aux + ss -tlnp + curl)

| Componente | Processo / Porta | Estado | Evidência |
|---|---|---|---|
| Brain analyst | `erika_torch_server google/gemma-4-12B-it :8098` | **VIVO** (PID 69858, health HTTP 200) | `ps aux`, `curl :8098/health` |
| Brain executor | `erika_torch_server google/gemma-4-E4B-it :8099` | **VIVO** (PID 69901, health HTTP 200) | `ps aux`, `curl :8099/health` |
| Worker API | `omni_coworker.cli serve :8081` | **VIVO** (PID 12962) | `/soul/state` HTTP 200; **`/health` retorna 404** — probe correto é `/soul/state` |
| kernel_daemon | in-process dentro do worker_api | **ATIVO** | `/soul/state` → `"kernel": true`; não existe processo standalone |
| state_guard | `omni_coworker.store.state_guard` | **VIVO** (PID 13029) | `ps aux` + `runtime_config/pids/state_guard.pid` |
| swap_scheduler | `omni_coworker.orchestration.swap_scheduler` | **VIVO** (PID 13031) | idem |
| archive_loop | `archive_worker_state.sh --loop 3600` | **VIVO** (PID 13033) | idem |
| pulse_sync | `scripts/pulse_dashboard_sync.sh` | **CRIADO nesta auditoria** | novo loop 1800 s |

**GPU `[DADO]`**: NVIDIA A100-SXM4-40GB (40960 MiB, ~19.9 GiB usados, 32 °C,
49 W). Tier resolvido = `std` (`runtime_config/hw_profile.json`,
`vram_mb=40960` → faixa `std ≥ 18 GB`; RAM host 89.6 GB).

**PID files desatualizados `[DADO]`**: `runtime_config/pids/brain_analyst.pid`
(PID 11838 morto) e `brain_executor.pid` (PID 12467 morto) — os brains vivos
foram iniciados em pts/2 e pts/3 fora do tracking de PID do
`start_omni_worker.sh` (provável subida manual pós-boot). **Consequência
`[LIMITE]`**: checagem de "servidores ativos" **não pode** confiar em pidfile
para os brains — a sonda correta é socket/HTTP nas portas. O exportador novo
faz probe TCP+HTTP (`:8098/:8099` → `/health`, `:8081` → `/soul/state`) e usa
pidfile apenas como evidência secundária.

**Concorrência `[LIMITE]`**: outra sessão Devin (pts/5) auditava bancos/WAL
checkpoint e `archive_worker_state.sh` em paralelo a esta auditoria — o pulso
foi desenhado para commitar **somente** `docs/data/dashboard/latest.json`
(`git add` cirúrgico), sem risco de capturar mudanças alheias.

## 2. Estado anterior de `latest.json` `[DADO]`

- Arquivo servido: `docs/data/dashboard/latest.json` (commitado, 60 KB),
  `exported_at = 2026-11-03T19:22:02Z` — **~46 h velho**; não havia nenhum
  loop de sincronização (`data/dashboard/` nem existia).
- O `main()` do exportador tinha default `--output data/dashboard/latest.json`
  (caminho gitignored por `/data/*`); a cópia em `docs/` era manual.
- Espelho `data/dashboard/latest.json` **ausente**.

### Campos reais vs fallback/estáticos `[DADO]` (auditoria campo a campo)

| Seção | Origem | Estado |
|---|---|---|
| `soul.phi/psi/sigma/epsilon/dominant_token/kernel` | `soul.api._compute_state()` live | real |
| `soul.maat` | calculado `(phi+psi+(1-eps))/3` | `[DERIVADO]` |
| `soma.*` | `soma.probe` live → fallback `somatic_probes.sqlite` (último probe) | real ou último medido |
| `kernel.cycle_count/phi_meta/s_meta/attractor_score/…` | `shared_workspace.sqlite` topics `kernel.*` | real histórico |
| `kernel.cohesion` | `phi_meta*0.92` quando ausente | **[DERIVADO]** (sintético) |
| `kernel.distinct_states` (6), `distinct_prefixes` (4), `homeo_state` ('OPTIMAL'), `producing` (true) | defaults literais | **estáticos `[LIMITE]`** |
| `kernel.regime_shift` | string fixa `'ESTÁVEL (ph < λ)'` | **hardcoded `[LIMITE]`** |
| `history.*` | últimos 24 eventos `kernel.phi_meta/metastability/attractor` | real histórico |
| `mesh` | 25 últimos eventos shared_workspace | real |
| `witness` | `data/witness.jsonl` (arquivo ausente → count 0) | real/ausente |
| `trust` | `trust_scores.json` + `trust_events.jsonl` (9569 eventos) | real |
| `battery.runs` (refactor) | `battery_results.sqlite` **0 bytes → sempre vazio** `[LIMITE]` | vazio real |
| `battery.diag_summary` | `diag_battery.sqlite` | real |
| `battery.coding_runs` | `coding_battery.sqlite` (60 linhas) | real |
| `battery.supervisor_summary` | query `FROM supervisor_runs` — **tabela inexistente** (real: `supervisor_battery`, 16 linhas) | **bug: sempre null `[DADO]`** |
| `spectral` | `activation_beta.hidden_spectral` + sidecars `state/activation_vectors` | real |
| `activations` | `data/monitor/erika_torch_activations.jsonl` | real |
| `mps_harvest` | `state/mps_harvest_12b.jsonl` | real |
| `appState.*` no index.html (phi=0.642, cpu=24.5, etc.) | literais JS exibidos quando fetch falha | **estáticos `[LIMITE]`** |

## 3. Bateria 280 Turnos — `data/basal_vs_modulated_280turns_20261105.sqlite` `[DADO]`

- `battery_turns`: **280/280** linhas; 2 chassis × 140 turnos
  (`BASAL` 70 + `MODULATED` 70 por modelo), `intervention_enabled` 0/1,
  sub-braços `BASAL_PURE`, `M1_scale_minus_delta`, `M2_scale_plus_delta`,
  `M3_freud10d_inrc_kuramoto`, `M4_closed_loop_mps_motor`; etapas
  `v10_subjectivity` (40), `cognitivo_executivo` (4), `v11_multiturn_series`
  (18), `swe_competition` (6), `swe_ood45` (2) por modelo×fase.
- `basal_envelope`: 2 linhas (uma por modelo, `n_turns=70` cada).
  12B: `chi_eff 18.330`, `ipr 0.06251`, `motor_vel 322.01`, `drift 0.8083`.
  E4B: `chi_eff 15.757`, `ipr 0.16628`, `motor_vel 256.86`, `drift 0.7814`.

### Discriminadores ROC-AUC `[DERIVADO]` (recomputado aqui por Mann-Whitney;

valores idênticos aos publicados no Ciclo 32 da auditoria contínua):

- **Chassi 12B vs E4B**: `mps_ipr_mean` **AUC = 1.000** (invertido: E4B > 12B
  em 100% dos cruzamentos; intervalos disjuntos [0.0456,0.0862] vs
  [0.1232,0.2062]) · `motor_velocity_mean` 0.977 · `mps_chi_eff_mean` 0.963 ·
  `mps_pr_traj` 0.937 (E4B) · `mps_svd_entropy` 0.832 (E4B).
- **Fase BASAL vs MODULATED intra-modelo**: todas ≈ 0.5 (`[LIMITE]` — as
  métricas dinâmicas não separam fase; o efeito da modulação é no Δ pareado,
  conforme Wilcoxon da auditoria: `v11` drift ↓ p=0.0013/0.034, `unique_ratio`
  ↑ 12B p=0.043 pooled).
- **Gate M4** (regra `drift > μ_env + 0.25σ` OU `vel < 0.85·μ_env`,
  `[DERIVADO]` recomputado): 12B 24/70 basal vs 16/70 mod; E4B 28/70 vs 27/70
  — **batem com os números publicados**. Degen: 4/4 (12B), 2/2 (E4B).

## 4. `data/swe_mps_ablation_20261105.sqlite` `[DADO]`

- `ablation_turns` 19 linhas; `ablation_summary` 4 braços B0–B3
  (4 tasks SWE cada: `cachetools_424`, `filesystem_spec_2169/2170/2183`).
- Resolve rate `[DADO]`: B0 0.75, B1 0.75, **B2 1.00, B3 1.00**.

## 5. Mudanças implementadas nesta auditoria `[DADO]`

1. `scripts/dashboard_export.py`:
   - Novo `vm`/`servers`: probe TCP+HTTP de `:8081` (`/soul/state`), `:8098`,
     `:8099`, pidfiles (`state_guard`, `swap_scheduler`, `archive_loop`),
     `kernel_daemon` (in-process), `hw_profile`, GPU; `active_servers` e
     `vm_active` derivados.
   - Novo `pulse`: `{interval_s: 1800, stale_after_s: 2400}` — contrato do
     indicador do frontend.
   - Novo `basal_vs_modulated_280`: totais, agregados modelo×fase×sub-braço,
     decomposição por `stage_category`, `basal_envelope`, `discriminators`
     (AUC chassi/fase/degen/regime), `gate_rule` + contagens, e série
     `turns` (280 pontos, sem `response_preview` — não-sensível e compacto).
   - Novo `swe_mps_ablation`: `ablation_summary` + turnos.
   - `battery`: corrigido `supervisor_summary` (`supervisor_runs` →
     `supervisor_battery`, com taxa `passion_flag` e acurácia `level_guess`
     vs `tracer_level`); adicionada `corpus_reading` (corpus_delivery_battery
     + app_delivery + dream_self_curriculum).
   - Escreve **simultaneamente** `docs/data/dashboard/latest.json`
     (commitado, Pages) e `data/dashboard/latest.json` (espelho local,
     gitignored) — flags `--output`/`--mirror`/`--no-mirror`.
2. `docs/index.html`: indicador global de **Pulso Basal** na barra superior +
   cartão detalhado no topo de *Supervisão* — `exported_at ≤ 40 min` E
   `vm.active_servers > 0` → **'VM ATIVA / PULSO BASAL ONLINE (Sync 30m)'**;
   `> 40 min` ou fetch impossível → **'SERVIDOR OFF / VM INATIVA — Modo
   Histórico Consolidado'** (gráficos/tabelas históricas permanecem).
   Nova seção **Bateria 280 Turnos** em *Pesquisas & Docs*: envelopes basais,
   tabela fase×sub-braço, decomposição por etapa, chips de discriminadores
   AUC, gráficos IPR-por-turno (separação de chassi) e métricas fase×modelo.
3. `docs/dashboard.html`: convertido de redirect mudo para **página de status
   leve** (pulso, servidores, métricas-chave, resumo 280) com link ao
   `index.html` canônico.
4. `scripts/pulse_dashboard_sync.sh` (novo, `+x`): `--once` e `--loop
   [intervalo]` (default 1800 s); exporta → commit cirúrgico de
   `docs/data/dashboard/latest.json` (só se alterado) → push `origin`
   (GitHub, via credential helper já configurado) + `gitlab`
   (`gitlab.com/omni-group535144/omni_worker`, token lido de
   `/content/gitlab.txt` via `GIT_ASKPASS`/credential helper — **o token
   nunca entra em argv, URL, remote config ou log**). Só commita/pusha quando
   a VM está ativa (probe dos servidores). Integrado ao
   `start_omni_worker.sh` via `start_proc pulse_sync … --loop
   ${PULSE_INTERVAL_S:-1800}`.

## 6. Execução verificada `[DADO]` (2026-11-05T17:13Z)

- `bash scripts/pulse_dashboard_sync.sh --once` executado: exportou
  `docs/data/dashboard/latest.json` (356 KB, `exported_at` fresco) + espelho
  `data/dashboard/latest.json`, detectou VM ativa (3/3 servidores), commitou
  cirurgicamente só `latest.json` e pushou **origin** (GitHub
  `fahbrain-omnimind/omni_worker`) e **gitlab**
  (`gitlab.com/omni-group535144/omni_worker`, remote adicionado sem token na
  URL; auth via `credential.helper` expandindo `$GITLAB_TOKEN` no subprocesso
  de credencial — token ausente de argv/config/log).
- Commits: `ef0ce05` (feat dev) → `0fe9707` + `919aad4` (chore pulse) — todos
  em `master` nos dois remotos.
- Loop basal ativo: `runtime_config/pids/pulse_sync.pid` = 134892
  (`--loop 1800`, log `logs/pulse_sync.log`); próximos boots sobem via
  `start_omni_worker.sh` (`OMNI_PULSE_SYNC=0` desliga).
- Verificações: `node --check` nos dois scripts JS, smoke `updatePulseStatus`/
  `render280Section` com snapshot real (ONLINE/STALE/NO-SNAP + seção 280),
  `ruff check` limpo, `python -m compileall` OK, `http.server` local servindo
  index/dashboard/latest.json 200.
- AUCs exportados conferem 1:1 com o Ciclo 32 da auditoria contínua
  (`ipr` power=1.000, `motor_vel` 0.977, `chi_eff` 0.963, `pr_traj` 0.937;
  degen `pr_traj` pooled 0.067→0.933 invertido; regime `pr_traj` 0.785 pooled,
  0.991 intra-12B, `motor_vel` 0.946 intra-E4B).

## 7. Limites residuais `[LIMITE]`

- `appState.*` continua com defaults literais quando `latest.json` está
  inacessível — agora explicitamente sinalizado pelo badge OFF; não são
  dados reais.
- `battery.runs` (refactor) continuará vazio enquanto `battery_results.sqlite`
  for 0 bytes — dado ausente real, não bug do exportador.
- O loop do pulso só publica enquanto a VM estiver ligada — após shutdown, o
  `exported_at` estagna e o frontend degrada sozinho ao modo histórico
  (> 40 min), que é exatamente o comportamento especificado.
- Push GitLab depende de `/content/gitlab.txt` existir na VM; ausência →
  `origin` ainda é publicado (warn, fail-open) `[DADO código]`.
