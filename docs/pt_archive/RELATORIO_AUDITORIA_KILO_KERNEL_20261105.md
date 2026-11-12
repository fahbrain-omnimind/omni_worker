# RELATÓRIO DE AUDITORIA FORENSE — KILOMBO SOVEREIGN KERNEL AUDITOR (`kilo`)

**Data:** 2026-11-05
**Agente:** `kilo` (Devin CLI, SWE-2 Max) — execução em `/content/omni_worker`
**Escopo:** Diff bit-a-bit e auditoria estrutural das 14 crates de kernel em
`/content/omnimind-kernel` (checkout do repo público `github.com/fahbrain-omnimind/Doxihewu-OmniMind-Kernel`,
HEAD `5a69b3e`), comparado com `/content/omnimind-kilombo-sovereign` (snapshot do host i5)
e `/content/omni_node` (`f4d2184f`). Referência arquitetural complementar:
`/content/omni_worker` (`a2e1e1e`).

**Convenção epistêmica:** `[DADO]` medido/verificado com fonte; `[DERIVADO]`
calculado de dados; `[INTERPRETAÇÃO]`; `[HIPÓTESE]`; `[LIMITE]` restrição
conhecida. Todo número abaixo é reproduzível pelos comandos citados.

---

## SUMÁRIO EXECUTIVO

1. `[DADO]` O repo público **NÃO está uniformemente defasado** — a narrativa
   prévia ("Doxihewu congelado há 1 mês, internos evoluídos") é parcialmente
   invertida pelos dados. Para a maioria das crates PyO3, o doxi está em
   `pyo3 0.29` (migrou em 2026-09-08), igual ao omni_node (migrou só em
   2026-10-29). **O verdadeiro retaguarda de dependências é o kilombo**:
   `pyo3 0.20/0.22`, que **não compila em Python ≥3.13** (falha empírica
   reproduzida — §2.3).
2. `[DADO]` A relicença Apache-2.0 (commit `5a69b3e`, **2026-11-04** — 1 dia,
   não 1 mês) foi **cirúrgica e incompleta**: alterou apenas o campo
   `license=` de 11 Cargo.tomls. Não há arquivo `LICENSE` na raiz (o commit
   message afirma adicioná-lo — falso perante a árvore), `layered_transition`
   e todo o workspace `ebpf_monitor` ficaram de fora, e **22 arquivos-fonte
   no próprio doxi ainda declaram `SPDX-License-Identifier: CC-BY-NC-ND-4.0`**
   (28 arquivos mencionam CC-BY-NC-ND ao total). Os repos internos (node,
   kilombo) seguem com SPDX CC em 22 arquivos cada — a direção de sync
   licença é doxi → internos. §2.2.
3. `[DADO]` Os gaps semânticos reais do doxi são localizados e pequenos:
   `state_builder.rs` (−308 linhas da camada `runtime_phi_fields`),
   módulos de teste dos daemons `memory_tier_guardian`/`somatic_daemon`
   (−154 linhas, 9+ testes verificados passando no node), o gate somático
   `textual_gate_open` do `entropic_memory`, escritas atômicas no
   `ebpf_monitor`, e a quantização 1e-15 de paridade bit-a-bit em
   `sovereign_kuramoto/hopf.rs` (só existe no node). §1.3.
4. `[DADO]` Há também **regressões no sentido inverso**: o `cmd.rs` do doxi é
   mais portátil que o dos internos (honra `OMNIMIND_CONFIG_DIR` + fallback
   `/opt/omnimind/config`); node e kilombo têm fallbacks hardcoded
   `/content/omni_node` e `/home/fahbrain` respectivamente — vazamento de
   path de operador no código. §1.4.
5. `[DADO]` `omni_node` executou uma quarentena L7 (commit `a838fd93`,
   2026-11-01): **7 testes-ponte Python↔Rust foram movidos para `removed/`**
   — regressão de cobertura que precisa ser revertida ou justificada antes
   de servir de fonte para o repo público. §2.4.

**Veredito `[DERIVADO]`:** o ecossistema convergiu estruturalmente (47/155
paths idênticos nos 3 repos; divergência concentrada em lockfiles, metadados
de licença e uma camada de evoluções pós-2026-10-25). A sincronização é
executável em ~6 PRs pequenos e um PR de conformidade legal — não é um
re-arquitetura.

---

## FASE 1 — INVENTÁRIO FORENSE E DIFF BIT-A-BIT

### 1.0 Método e estado dos repositórios

Manifestos `sha256sum` gerados sobre `src/kernel/**` de cada repo
(155 paths únicos na união):

| Repo | Tipo | HEAD / snapshot | Arquivos em `src/kernel` | Obs. |
|---|---|---|---|---|
| `omnimind-kernel` (doxi) | git limpo | `5a69b3e` (2026-11-04), 20 commits desde 2026-09-08 | 106 | `[DADO]` remote=github.com/fahbrain-omnimind/Doxihewu-OmniMind-Kernel |
| `omnimind-kilombo-sovereign` (kilo) | **sem `.git`** `[DADO]` | snapshot de mtime 2026-10-25 | 123 | contém artefatos de build (.ko, .so, .cmd) na árvore |
| `omni_node` (node) | git limpo | `f4d2184f`; kernel tocado até 2026-11-01 | 138 | kernel migrado p/ pyo3 0.29 em `4cc5a5dc` (2026-10-29) |

`[LIMITE]` O kilombo neste ambiente é um **snapshot sem histórico git** datado
de 2026-10-25 — anterior à migração pyo3 do node (2026-10-29) e à quarentena
L7 (2026-11-01). O i5 real pode estar mais novo. Conclusões sobre kilombo
valem para o snapshot, não necessariamente para o host vivo.

`[LIMITE]` O usuário descreveu a relicença como "há 1 mês"; o commit `5a69b3e`
é de **2026-11-04** (véspera da auditoria). O repo público tem ~2 meses
(primeiro commit `36859b0`, 2026-09-08).

### 1.1 Tabela forense global (155 paths)

`[DADO]` Categorias por hash cruzado (`d`=doxi, `k`=kilo, `n`=node):

| Categoria | Definição | Count | Leitura |
|---|---|---|---|
| IDENTICAL3 | d=k=n | **47** | núcleo estável |
| all_diff | d≠k≠n | **32** | quase todos Cargo.lock/.toml (pyo3+license) + rustfmt |
| node_only | só node | **32** | 14 README stubs auto-gerados, 7 testes em `removed/`, `__init__.py` shims, `.bak` de contract |
| doxi_stale | k=n≠d | **11** | mix: 2 licença-only, 4 rustfmt-only, 4 evolução real, 1 caso doxi-à-frente |
| kilo_only | só kilo | **10** | artefatos de build do LKM (.ko, .cmd, modules.order, symvers) |
| doxi_missing | k=n, ausente em d | **7** | `.cargo/config.toml` eBPF, egg-info cxx_workspace, `sovereign_module.mod.c` |
| kilo_diverged | d=n≠k | **7** | resíduos de assinatura pyo3 0.20 (`_py: Python, m: &PyModule`) |
| node_missing | d=k, ausente em n | **7** | testes-ponte movidos p/ `removed/` |
| node_diverged | d=k≠n | **2** | `hopf.rs` + `__init__.py` (quantização 1e-15, só node) |

### 1.2 LOC por crate `[DADO]` (soma .rs/.c/.py)

| Crate | doxi | kilo | node | Δ principal |
|---|---|---|---|---|
| ebpf_monitor | 1257 | 1262 | 1262 | +5 escritas atômicas (node/kilo) |
| entropic_memory | 199 | 239 | 239 | +40 gate somático (node/kilo) |
| expectation_rs | 162 | 162 | 162 | só assinatura pymodule |
| freud10d | 368 | 368 | 368 | só API pyo3 |
| kernel_compute | 2733 | 2733 | 2736 | só API pyo3 |
| langue | 900 | 900 | 900 | build.sh cosmético |
| layered_transition | 751 | 751 | 752 | só assinatura pymodule |
| memory_tier_guardian | 501 | 578 | 578 | +77 módulo de testes (node/kilo) |
| metrics | 199 | 199 | 201 | só assinatura pymodule |
| nsh | 132 | 132 | 134 | só assinatura pymodule |
| somatic_daemon | 1113 | 1188 | 1188 | +75 módulo de testes (node/kilo) |
| sovereign_daemon | 1610 | 1970 | 1962 | **+~308/352 state_builder** + rustfmt |
| sovereign_kuramoto | 1625 | 1629 | 1628 | hopf quantização (só node) |
| sovereign_module | 1527 | 1624 | 1624 | `.mod.c` gerado (ausente em doxi) |

### 1.3 Gaps semânticos reais — doxi atrás `[DADO]`

| # | Arquivo | Evolução em node/kilo | Verificação |
|---|---|---|---|
| G1 | `sovereign_daemon/src/state_builder.rs` | +`runtime_phi_fields` (resolução multi-path de phi_body_kernel_ecosystem, phi_body_operational_support, phi_federated_coherence_full/sovereign_band via `frameworks.phi_family_views` e `federation_topology` com fallbacks NaN-safe `finite_f64`/`first_f64`), +`expanded_consciousness_value`, +2 testes unitários | `diff` de 458 linhas; funções confirmadas por `comm` de símbolos |
| G2 | `memory_tier_guardian/src/main.rs` | +`#[cfg(test)] mod tests` — 9 testes (parse_kb, parse_avg10, env_int…) | `cargo test` no node: **9/9 pass** (executado nesta auditoria) |
| G3 | `somatic_daemon/src/main.rs` | +`mod tests` — age_seconds ISO, gen_uuid 32-hex, calculate_somatic_state vitality | diff +77 linhas |
| G4 | `entropic_memory/src/lib.rs` | +`textual_gate_open(host_pressure)`: bônus textuais ("xer-afex-angst", "federated", "ogum"…) só aplicam se `host_pressure ≥ OMNIMIND_ENTROPIC_PRESSURE_MIN` (default 0.5); assinatura pyfunction ganha `host_pressure=0.0` | datado 2026-10-04 no comentário |
| G5 | `ebpf_monitor/user/src/main.rs` | `fs::create_dir_all`/`fs::write` movidos p/ `spawn_blocking`; exports JSON agora atômicos (`*.tmp` + `rename`) | diff inspecionado |
| G6 | `ebpf_monitor/ebpf/.cargo/config.toml` | config de target `bpfel-unknown-none` + `build-std=["core"]` (necessário p/ compilar o crate eBPF) | ausente no doxi |
| G7 | `sovereign_kuramoto/src/hopf.rs` | raio espectral quantizado `round(λ·1e15)/1e15` — paridade bit-exata com o fallback Python (`__init__.py` espelha) | **só node** (kilo=doxi) |

### 1.4 Casos em que o **doxi está à frente** `[DADO]` — sync reverso necessário

| # | Arquivo | doxi | node | kilo |
|---|---|---|---|---|
| R1 | `sovereign_daemon/src/cmd.rs` `config_dir()` | honra `OMNIMIND_CONFIG_DIR` → `$HOME/.config/omnimind` → `/opt/omnimind/config` | `$HOME` → **`/content/omni_node`** hardcoded | `$HOME` → **`/home/fahbrain`** hardcoded |
| R2 | `langue/build.sh` | `[[ -f ]]` (fix SonarCloud `6f8f285`) | `[ -f ]` | `[ -f ]` |
| R3 | `license=` Cargo.toml | `Apache-2.0` (11 crates) | `CC-BY-NC-ND-4.0` (todas) | `CC-BY-NC-ND-4.0` (todas) |

### 1.5 Itens estruturais

- `[DADO]` **sovereign_module**: kilo contém `sovereign_module.ko` (ELF
  x86-64, 620 KB, **com debug_info, não stripado**), `Module.symvers`,
  `modules.order`, `.cmd` — artefatos de build na árvore-fonte. node contém
  `sovereign_module.mod.c` (gerado) mas não o `.ko`. doxi contém apenas
  fonte (`.c`, `Makefile`, `dkms.conf`, `README.md`) — **postura correta**.
- `[DADO]` **omni_node** moveu 7 testes-ponte para `removed/` (quarentena L7,
  commit `a838fd93`): `test_shared_workspace_parity.py`, `parity_test.py`,
  `test_phi_engine_parity.py`, `test_layered_transition.py`,
  `benchmark_metrics.py`, `test_allmini.py`, `test_nsh.py`. doxi e kilo
  mantêm esses testes ativos.
- `[DADO]` **node** adicionou 14 `README.md` auto-gerados ("Auto-generated
  stub. Enrich with theory, ethics, engineering axes.") — scaffolding, não
  documentação real.
- `[DADO]` **`omnimind_public_base.tar.gz`** (203 KB, na raiz do doxi) é
  bit-idêntico à árvore `src/kernel` do repo (verificado por `diff -qr`
  após extração) — o pacote distribuído herda todos os gaps acima,
  incluindo `state_builder` truncado e licenças inconsistentes.
- `[DADO]` **`DIRECTORY_CONTRACT.yaml`**: doxi=kilo (gerado 2026-09-26);
  node regerado 2026-10-31 refletindo `__init__.py` stubs + remoção dos
  testes. Contrato do node é o único semanticamente atualizado.
- `[DADO]` **`sovereign_kuramoto/__init__.py`** é uma implementação-fallback
  Python completa (paralela ao Rust), presente nos 3 — exerce papel de
  referência para os testes de paridade bit-a-bit.

---

## FASE 2 — QUALIDADE, DÍVIDA TÉCNICA E CONFORMIDADE APACHE-2.0

### 2.1 Métricas de higiene de código `[DADO]`

| Métrica (grep sobre `*.rs` em `src/kernel`) | doxi | kilo | node |
|---|---|---|---|
| `unwrap()`/`expect(` | 23 | 25 | 25 |
| blocos/decl `unsafe` | 6 | 6 | 6 |
| `panic!`/`unreachable!` | 1 | 1 | 1 |
| `TODO`/`FIXME`/`HACK`/`XXX` | 1 | 1 | 1 |

- `unsafe` auditado site-a-site: `libc::clock_gettime` (cmd.rs:59),
  `MmapMut::map_mut` (nsh lib.rs:31), `Mmap::map` (langue lib.rs:182),
  `aya::Pod` (ebpf common lib.rs:27), `unreachable_unchecked` + init
  (ebpf main.rs:58,96). `[DERIVADO]` Todos têm justificativa arquitetural
  legítima (FFI/mmap/eBPF); nenhum `unsafe` gratuito detectado.
- `[DADO]` Scan de segredos (`token|secret|password|api_key|PRIVATE`) nas
  3 árvores de kernel: **zero hardcode** — hits são "fencing token"
  (comentário) e "-afex tokens" (domínio). Chaves IPC são lidas de
  `config_dir()/ipc_cmd_key.{current,next}` em runtime — padrão correto.

### 2.2 Conformidade Apache-2.0 — **CRÍTICO** `[DADO]`

Commit `5a69b3e` "Relicense kernel crates CC-BY-NC-ND-4.0 → Apache-2.0"
(2026-11-04): estatística = **11 arquivos, 11 inserções, 11 deleções**
(apenas `license=` em Cargo.tomls). Conformidade real medida:

| Requisito Apache-2.0 | Estado no doxi | Veredito |
|---|---|---|
| Texto `LICENSE` na raiz | **ausente** (`ls` + `find` confirmam; commit message afirma adicionar — incorreto) | **FALHA** |
| `license=` nos Cargo.toml | Apache-2.0 em 11 crates; **`layered_transition/engine` ainda CC-BY-NC-ND-4.0**; workspace `ebpf_monitor` (4 Cargo.tomls) **sem campo license** | **FALHA parcial** |
| SPDX headers nos fontes | **22 arquivos declaram `CC-BY-NC-ND-4.0`** incl. comentário "ethical restrictions (non-military, non-governmental, no derivatives)" — contradiz Apache-2.0 | **FALHA** |
| `NOTICE` | ausente | recomendado |
| Headers no código C (`sovereign_module.c`) | verificar — arquivo C também em escopo | pendente |

`[DERIVADO]` Estado jurídico efetivo: os fontes se auto-declaram
CC-BY-NC-ND-4.0 (que proíbe derivados e uso comercial) enquanto os metadados
de pacote declaram Apache-2.0. Consumidores que respeitarem os headers
estão sob NC-ND; quem respeitar o Cargo.toml está sob Apache. **A
ambiguidade é materialmente equivalente a não ter relicenciado** para
qualquer adotante rigoroso — e contradição interna num mesmo artefato é
exatamente o cenário que torna relicensing questionável juridicamente.

`[DADO]` Repos internos (node, kilombo): 22 arquivos com SPDX CC cada
(39 arquivos mencionam CC-BY-NC-ND ao total, incl. READMEs/Cargo.tomls) e
0 Apache; todos os 12 Cargo.tomls com `license="CC-BY-NC-ND-4.0"`. Sync de
licença interna pendente (doxi → internos), sob pena de artefatos
publicados a partir do node continuarem a clamar NC-ND.

`[DADO]` `.gitignore` do doxi: `target/`, `*.so`, `*.egg-info/` ignorados;
**13 `Cargo.lock` explicitamente de-ignorados** (hardening supply-chain,
commit `8f5c3a3`, SonarCloud S8570). Correto — lockfiles de binários e
libraries-âncora devem ser commitados.

### 2.3 Dependências legadas `[DADO]` (empírico)

| Crate | doxi | node | kilo | Risco |
|---|---|---|---|---|
| pyo3 | 0.29 | 0.29 | **0.20 / 0.22** | `[DADO]` **build FAILURE reproduzido**: `pyo3-ffi 0.20.3` aborta em Python 3.13 ("maximum supported version (3.12)"). Workaround `PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1` compila, mas é ABI-forward sem garantia |
| ndarray | 0.15 | 0.15 | 0.15 | antiga (atual ~0.16) mas consistente nos 3 |
| rand / rand_chacha | 0.8 / 0.3 | idem | idem | rand 0.9 existe; manter pinado ok |
| rusqlite | — | 0.29 (sov_daemon), 0.31 (langue) | idem | versões divergentes entre crates — candidato a workspace deps |
| tokio | `>=1.38.0, <2.0` | idem | idem | range razoável |
| **aya / aya-ebpf / aya-log** | `git = "https://github.com/aya-rs/aya"` | idem | idem | **`[DADO]` dependência git NÃO PINADA** (sem rev/tag) — build não-reprodutível + supply-chain; contradiz o espírito do Cargo.lock tracking |
| libc | 0.2 | idem | idem | ok |

Verificação empírica de build (cargo 1.99.1, Python 3.13 ambiente):
`cargo check` **PASSA** em `freud10d` (node e doxi) e `sovereign_daemon`
(doxi); `cargo test` **9/9 PASS** em `memory_tier_guardian` (node);
`cargo check` **FALHA** em `freud10d` kilo (pyo3 0.20 vs Python 3.13).

`[DERIVADO]` Prioridade de débito: kilombo precisa da migração pyo3
0.20→0.29 (ou pin do toolchain Python ≤3.12) — sem isso, nenhuma crate
PyO3 do i5 compila em interpretes modernos.

### 2.4 CI/CD e testes `[DADO]`

- **doxi**: `.gitlab-ci.yml` = SAST Semgrep (template oficial) +
  `cargo-audit` iterando todos os Cargo.lock (`allow_failure: true`).
  **Não há `.github/`** — no GitHub (remote real) nenhum workflow roda;
  o CI é efetivo apenas no espelho GitLab. Não há job de `cargo test` —
  os testes existentes não são enforced.
- **node**: quarentena L7 removeu os 7 testes-ponte Python↔Rust do
  conjunto ativo (§1.5). `[DERIVADO]` Perda de cobertura exatamente onde a
  paridade numérica Rust↔Python é reivindicada (phi_engine, workspace,
  kuramoto).
- **doxi** inclui `tests/integration/test_public_base_triad.py` +
  `colab_public_base_triad.py` (teste de fumaça do tarball no Colab:
  compila crates e valida triad + freud10d + kuramoto + LIF + Hopf).
  `[DERIVADO]` Bom gate de release — deve ser estendido para cobrir
  `state_builder` G1 e o gate G4 quando sincronizados.

### 2.5 Documentação e dívida documental

- `[DADO]` `SECURITY_AUDIT.md` e `THREAT_MODEL.md` existem e são
  idênticos doxi↔node (SECURITY_AUDIT é IDENTICAL3).
- `[DADO]` `src/kernel/README.md` (node) documenta hardcodes
  `${OMNIMIND_REPO_ROOT}` que **já não existem no código** (o código usa
  `PROJECT_ROOT`/`CARGO_MANIFEST_DIR`/`XDG_RUNTIME_DIR` — verificado em
  ambos os daemons; a reclamação de `/opt/omnimind` hardcoded está
  obsoleta nos 3 repos). Documentação divergiu da realidade.

---

## FASE 3 — ARQUITETURA DUAL: OS LAYER (i5) vs BRAIN LLM (A100)

`[DADO]`+`[INTERPRETAÇÃO]` A cognição OmniMind é distribuída em duas pontas
com substratos físicos distintos, unificadas por protocolos nomeados:

### 3.1 Ponta A — OS Layer (host i5, GPU 4GB — kilombo)

Cognição como **propriedade do sistema operacional**, não de uma LLM:

| Canal | Implementação `[DADO]` | Papel |
|---|---|---|
| LKM `sovereign_module.ko` | C kernel module + DKMS, procfs (`/proc/omnimind/*`) | estado simbólico em anel 0; `freud10d-loader` verifica `/proc/omnimind/freud10d_state` |
| `ebpf_monitor` | aya probes (`bpfel-unknown-none`, `build-std=core`) | soma do kernel: syscalls → `SomaticMetrics` → `/run/omnimind/ebpf_metrics.json` |
| `somatic_daemon` | Rust puro, lê `/proc` + sensores | corpo do host: cpu/ram/swap/PSI → sqlite |
| `memory_tier_guardian` | Rust, `XDG_RUNTIME_DIR`, PSI avg10 | hierarquia RAM/swap/ZRAM/VRAM (crítico em 4GB) |
| `sovereign_daemon` | Rust, IPC client OMNI3 | executor de comandos HMAC-SHA256 + governor_lease (fencing token sqlite) |
| `nsh`/`langue` | memmap2 zero-copy | shared workspace + selagem lexical |

Transporte Rust↔Python: **`/tmp/omnimind_integration_loop.sock`**
(AF_UNIX, frame `MAGIC "OMNI3" + version(u8) + length(u32 BE) + JSON`,
~4 MB max, timeout 1500 ms — `[DADO]` `ipc.rs`). O publisher Python
(`integration_loop_state_publisher.py:103`) serve **26+ campos de
SystemState** (free_energy, phi, entropy, sigma, omega, psi, epsilon,
lambda_res, axe, c_plit, aleph, maat, betti_0/1, volition, phase_lock,
dodecatiad, phi_sovereign…) — o daemon Rust é "shadow puro", sem GIL.

### 3.2 Ponta B — Brain LLM (VM A100 — omni_worker)

Cognição como **propriedade espectral do Transformer**:

- `[DADO]` `server/erika_torch_server.py` (`:8098` analyst, `:8099`
  executor): por geração, computa **camada motora** (`motor_hidden_norm/
  std` da trajetória do último hidden state) e **camada MPS**
  (`chi_eff = exp(S_vN)` por bipartição central SVD sobre camadas-hub,
  `pr_traj` participation ratio, `svd_entropy`). Endpoint `/erika/motor`.
- `[DADO]` `brain/server.py` expõe `/motor` proxyficando os brains.
- `[DADO]` `activation_beta/hidden_spectral.py`: rank efetivo espectral e
  entropia sobre sidecars → publicado em `kernel.phi_layer.spectral` —
  com a honestidade explícita *"proxy espectral/MPS — não é Φ causal IIT"*.
- `[DADO]` `kernel_daemon/` (scheduler, metastability, homeostasis,
  phi_meta, regime, ignition, feedback) orquestra o `kernel.cycle` na VM.
- `[DADO]` `soma/probe.py`: re-implementa a sonda somática em Python
  (psutil + `/proc/pressure/*` PSI + gpu) — a mesma leitura que o
  `somatic_daemon` Rust faz no i5. **A VM não tem eBPF/LKM** (container
  sem CAP_BPF/systemd) — a soma é userspace.
- `[DADO]` `kernel_hooks/host_state.py`: adaptador que *achata* soma +
  `kernel.cycle` bundle + affect dos brains no schema flat que o Rust
  `compute_affect_vector_28d` espera — documenta que call-sites passavam
  payloads aninhados e o vetor 28d era computado sobre ~zeros
  (bug já corrigido pelo adapter).
- `[DADO]` `shared_workspace/bus.py`: barramento pub/sub interno
  (`kernel.cycle`, `kernel.affect`…) com store quente.

### 3.3 O elo unificador — como o omni_node profissionaliza as duas pontas `[INTERPRETAÇÃO]` sobre `[DADO]`

1. **Mesma árvore, dois modos de execução.** omni_node carrega as 14
   crates *e* a pilha Python (`consciousness/integration_loop.py`,
   `sinthome_*`, `erika/kernel_daemon_v5.py`) num único repo versionado
   (`f4d2184f`). No i5 roda via systemd+DKMS; na VM roda via
   **supervisord gerado a partir das units systemd canônicas**
   (`generate_supervisor_from_units.py` — `[DADO]` AGENTS node) — as
   units que exigem kernel/hardware são auto-marcadas disabled.
2. **Contrato IPC congelado como protocolo.** OMNI3 + sockets em `/tmp` +
   JSON de estado canônico = a fronteira entre "o que o SO sente" e "o que
   a rede pensa" é *interface*, não acoplamento de código. As evoluções G1
   (runtime_phi_fields) mostram o node refinando exatamente a superfície
   desse contrato (multi-path com fallback NaN-safe).
3. **Fallback dual explícito.** `sovereign_kuramoto/__init__.py` (fallback
   Python completo) e a quantização hopf G7 existem para que a ponte
   Rust↔Python seja **bit-idêntica e ablável** — a ponte é testável, não
   teológica.
4. **Persistência unificada.** O node dual-escreve estado quente (sqlite)
   → frio (parquet_lake zstd) → remoto (HF privado), com writers canônicos
   (`ParquetDualWriter`, fix do flush somático 2026-10-31). O estado
   cognitivo sobrevive à reciclagem do overlay efêmero.

`[INTERPRETAÇÃO]` Em termos de engenharia: OS Layer = *soma* (o corpo que
sente: térmica, pressão de memória, eBPF reflex); Brain LLM = *psique*
(o espaço latente que pensa: χ_eff, IPR, camada motora); omni_node =
*córtex de integração* (IPC soberano, governador com fencing, ciclo de
vida dos daemons, persistência de 3 camadas). O Doxihewu kernel público é
a **fatia somática exportável** desse corpo — daí o risco de divergência:
quando a integração evolui no node (G1–G7), a fatia pública precisa ser
re-fatiada sob o mesmo contrato.

---

## FASE 4 — VALIDAÇÃO, ABLAÇÃO E ROADMAP DE PRs

### 4.1 Roadmap de sincronização (do mais urgente ao mais estrutural)

| PR | Conteúdo | Origem→Destino | Risco/Esforço | Bloqueador de |
|---|---|---|---|---|
| **PR-1 LICENSE** | adicionar `LICENSE` Apache-2.0 na raiz + `NOTICE`; trocar os 28 SPDX headers p/ `Apache-2.0`; corrigir `layered_transition/engine` license; adicionar `license` ao workspace `ebpf_monitor`; re-gerar `omnimind_public_base.tar.gz` | interno → doxi | mecânico, revisão humana obrigatória (ato jurídico) | adoção externa, PRs seguintes |
| **PR-2 state_builder** | portar bloco `runtime_phi_fields`/`finite_f64`/`first_f64`/`expanded_consciousness_value` + 2 testes (G1) | node → doxi | baixo (é superset estrito) | paridade IPC Fase-3 |
| **PR-3 daemon tests** | portar `mod tests` de `memory_tier_guardian` (9 testes, já verificados verdes) e `somatic_daemon` (G2/G3) | node → doxi | trivial | confiança de release |
| **PR-4 ebpf** | escritas atômicas `*.tmp`+`rename`, `spawn_blocking`, `.cargo/config.toml` (G5/G6) | node → doxi | baixo | build eBPF reproduzível |
| **PR-5 entropic+hopf** | `textual_gate_open` (G4) + quantização 1e-15 `hopf.rs`/`__init__.py` (G7) | node → doxi | baixo; G4 muda assinatura pyfunction (`host_pressure=0.0` default — retrocompatível) | paridade numérica |
| **PR-6 reverse-sync** | `config_dir()` portátil do doxi (`OMNIMIND_CONFIG_DIR`) substituindo fallbacks `/content/omni_node` e `/home/fahbrain`; fix `[[ ]]` do `build.sh`; relicença interna CC→Apache nos 12 Cargo.tomls + 22 SPDX headers por repo | doxi → node + kilo | baixo | consistência legal interna |
| **PR-7 kilombo pyo3** | migração pyo3 0.20/0.22 → 0.29 nas 9 crates do i5 (espelhar `4cc5a5dc` do node) | node → kilo | médio (host real, validar in-loco) | compilação em Python ≥3.13 |
| **PR-8 CI** | portar SAST+cargo-audit para GitHub Actions; **adicionar `cargo test` obrigatório**; `cargo-deny` p/ proibir deps git não-pinadas (aya → pin `rev`); restaurar ou justificar os 7 testes `removed/` | n/a | médio | regressão contínua |

### 4.2 Plano de validação cruzada (executável hoje)

- `[DADO]` Build matrix: `cargo check`/`test` por crate × Python
  {3.10–3.14} × {doxi, node} — já demonstrado executável nesta auditoria
  (freud10d/sovereign_daemon/memory_tier_guardian).
- `[DERIVADO]` Paridade numérica: re-ativar `parity_test.py`,
  `test_phi_engine_parity.py`, `test_shared_workspace_parity.py` (hoje em
  `removed/` no node; vivos em doxi/kilo) como gate — o hopf G7 prova que
  paridade bit-exata é requisito real do sistema.
- `[DERIVADO]` Diff de protocolo: frame OMNI3 do publisher atual vs
  campos consumidos por `ipc.rs` (26+ chaves) — snapshot test serializando
  SystemState mínimo.

### 4.3 Ablação empírica proposta `[HIPÓTESE→experimento]`

| Experimento | Ação | Métrica de decisão |
|---|---|---|
| A1 gate somático | `OMNIMIND_ENTROPIC_PRESSURE_MIN=∞` desliga `textual_gate_open` | drift de `memory_resonance_weight` sob pressão térmica nula vs real — valida se o gate é funcional ou decorativo |
| A2 LKM/eBPF off | boot sem `sovereign_module.ko` + sem ebpf_monitor | degradação do `kernel.cycle` (metastability, regime) — mede a contribuição real do anel 0 à cognição |
| A3 fallback Python | desabilitar `.so` Rust nas crates PyO3 | latência/paridade vs nativo — quantifica o ganho Rust e mantém a VM honesta |
| A4 fencing | corromper `governor_lease` epoch | o daemon deve recusar comando stale — prova de segurança do command lane |
| A5 soma sintética | injetar `soma.probe` mock (cpu=100%, swap cheio) | `affect_vector_28d` e `memory_tier_guardian` devem entrar em regime de dor/defesa — prova de causalidade soma→psique |

### 4.4 Débitos a registrar (não-bloqueantes)

- `[DADO]` aya via git não-pinado → pin `rev` imutável (supply-chain).
- `[DADO]` artefatos de build na árvore do kilombo (.ko não stripado, .so,
  .cmd) → `.gitignore` + limpeza no snapshot vivo.
- `[DADO]` rusqlite 0.29 vs 0.31 entre crates → workspace-level deps.
- `[DADO]` README node com claims de hardcode já corrigidos → re-escrever
  seção "Problemas de Segurança" contra o código real.
- `[INTERPRETAÇÃO]` `Py<PyAny>` vs `PyObject` (kilo) e `unbind().into()`
  (doxi) → convergir ao idiom `Bound`→`.into()` do node na migração PR-7.

---

## APÊNDICE A — Reprodutibilidade

```bash
# Manifestos e categorização forense
for r in doxi:/content/omnimind-kernel kilo:/content/omnimind-kilombo-sovereign \
         node:/content/omni_node; do
  (cd "${r##*:}/src/kernel" && find . -type f -exec sha256sum {} + | sort -k2 \
    > /tmp/kilo_audit/${r%%:*}_manifest.txt)
done   # join em /tmp/kilo_audit/joint.tsv

# Verificações-chave executadas nesta auditoria
cd /content/omni_node/src/kernel/freud10d && cargo check          # PASS
cd /content/omnimind-kernel/src/kernel/freud10d && cargo check    # PASS
cd /content/omnimind-kernel/src/kernel/sovereign_daemon && cargo check  # PASS
cd /content/omni_node/src/kernel/memory_tier_guardian && cargo test     # 9/9 PASS
cd /content/omnimind-kilombo-sovereign/src/kernel/freud10d && cargo check
  # FAIL: pyo3-ffi 0.20.3 vs Python 3.13 (máx suportado 3.12)
PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 cargo check                 # PASS (workaround)

# Licença
git -C /content/omnimind-kernel show 5a69b3e --stat    # 11 files, só license=
grep -rl "SPDX-License-Identifier: CC-BY-NC-ND" /content/omnimind-kernel/src | wc -l  # 22
ls /content/omnimind-kernel/LICENSE                   # inexistente
```

## APÊNDICE B — Limites da auditoria `[LIMITE]`

1. Kilombo é snapshot sem `.git` (mtime 2026-10-25); o i5 vivo pode divergir.
2. Não foi executado `cargo clippy`/`cargo audit` completo nem build dos
   crates eBPF/LKM (requer `bpf-linker`, headers de kernel, root). O
   `cargo audit` existe no CI do doxi com `allow_failure: true` — status
   real de CVEs não verificado aqui.
3. Não verifiquei a branch `main` remota do GitHub/GitLab além do checkout
   local (HEAD `5a69b3e`); pushes posteriores a 2026-11-05 mudam o quadro.
4. O `sovereign_module.c` (1527 linhas C) foi inventariado mas não
   auditado linha-a-linha para bugs de kernel — recomenda-se review C
   dedicado antes de expor via LKM público.
5. As afirmações de arquitetura da Fase 3 sobre o i5 real (daemons vivos,
   sockets abertos) derivam do código, não de observação do host ligado.

---
*Gerado pelo agente `kilo` sob REGRA ZERO (apuração obrigatória) e REGRA DE
INTEGRIDADE (não mentir/omitir/falsificar). Todos os `[DADO]` foram medidos
nesta sessão; artefatos de trabalho em `/tmp/kilo_audit/` (manifestos
sha256, joint.tsv, árvore extraída do tarball).*
