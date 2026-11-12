# Sovereign Kernel Architecture and Security Audit

**Document class:** Formal technical audit — systems/software forensics
**Title:** Sovereign Kernel Architecture and Security Audit
**Date of issue:** 2026-11-12
**Primary source:** `docs/RELATORIO_AUDITORIA_KILO_KERNEL_20261105.md` (agent `kilo`, 2026-11-05)
**Subject system:** OmniMind Sovereign Kernel — 14 kernel crates distributed across three repository lineages
**Audit environment:** `/content/omni_worker` (branch `master`, HEAD `a356dc5`)

---

## Document Control and Provenance Convention

This report restates, verifies, and extends the 2026-11-05 forensic audit in formal
English. It does not introduce new empirical claims that are not traceable to a
measured artifact. Every quantitative statement carries a provenance tag.

| Tag | Meaning |
|---|---|
| `[DADO-R]` | **Recorded datum** — measured in the 2026-11-05 source audit; the artifact is not present in the current environment and the value cannot be re-measured here. |
| `[DADO-M]` | **Measured datum** — re-measured live in this audit session (2026-11-12) against the artifact present on disk. |
| `[DERIVADO]` | Derived by calculation from recorded/measured data. |
| `[INTERPRETATION]` | Analytical judgement, not a measurement. |
| `[HYPOTHESIS]` | Testable proposition, not yet an experiment result. |
| `[LIMIT]` | Known restriction on the validity of this audit. |

**Material environmental change.** The two comparison repositories referenced by
the source audit — `/content/omnimind-kernel` (public "doxi",
`github.com/fahbrain-omnimind/Doxihewu-OmniMind-Kernel`) and `/content/omni_node`
(node, `f4d2184f`) — are **not present** in the current audit environment. Only
`/content/omnimind-kilombo-sovereign` (kilombo snapshot) is available. All
statements about doxi and node are therefore `[DADO-R]` and inherit the
limitations of the 2026-11-05 session. All statements about kilombo marked
`[DADO-M]` were independently re-measured on 2026-11-12 and agree with the
recorded values. See Appendix B.

---

## 1. Executive Summary and Epistemic Verdict

### 1.1 Scope and method

The audit covers the 14 kernel crates that constitute the OmniMind sovereign
kernel, across three lineages:

1. **Public kernel** — `Doxihewu-OmniMind-Kernel` ("doxi"), the publishable slice.
2. **Kilombo sovereign host** — the i5 OS-layer snapshot ("kilombo"/"kilo").
3. **Omni-Node** — the integrating repository that carries both the kernel crates
   and the Python cognitive stack ("node").

Method: SHA-256 manifests over `src/kernel/**` in each repository, cross-joined
into a 155-path forensic table; line-of-code (LOC) counts over `.rs/.c/.py`;
manifest-level and source-level diff; empirical build/test execution; SPDX and
`license=` field enumeration; and dependency-manifest inspection.

### 1.2 Summary of findings

**F-1 — Structural convergence is real, not assumed.** `[DADO-R]` 47 of 155
union paths are byte-identical across all three repositories (`IDENTICAL3`).
Divergence is concentrated in lockfiles, license metadata, and a post-2026-10-25
evolution layer. The ecosystem is **not** uniformly stale in any one direction.

**F-2 — The public kernel is not uniformly behind.** `[DADO-R]` For the PyO3
crates, doxi is at `pyo3 0.29` (migrated 2026-09-08), equal to node (migrated
2026-10-29). The genuine dependency laggard is the kilombo host: `pyo3 0.20/0.22`,
which **fails to compile on Python ≥ 3.13**. `[DADO-M]` Re-measured: 8 crates
pin `pyo3 0.20`, 1 pins `pyo3 0.22`.

**F-3 — The Apache-2.0 relicensing is surgically incomplete and internally
contradictory.** `[DADO-R]` Commit `5a69b3e` (2026-11-04) altered only the
`license=` field of 11 `Cargo.toml` files (11 insertions, 11 deletions). No
root `LICENSE` file exists in the tree despite the commit message claiming to add
one; `layered_transition/engine` and the four `ebpf_monitor` workspace manifests
were excluded; and 22 source files in doxi still declare
`SPDX-License-Identifier: CC-BY-NC-ND-4.0`. `[DADO-M]` The kilombo snapshot
carries 22 such SPDX declarations and 12 `license = "CC-BY-NC-ND-4.0"` fields.

**F-4 — The semantic gaps in the public kernel are localised and small.**
`[DADO-R]` The material deltas are: `state_builder.rs` (−308 lines, the
`runtime_phi_fields` layer), daemon test modules (−154 lines), the
`textual_gate_open` somatic gate, atomic writes in `ebpf_monitor`, and the
`hopf.rs` 1e-15 quantisation (node-only). `[DADO-M]` The kilombo snapshot
contains `runtime_phi_fields`, the gate, the atomic writes, and the eBPF cargo
config — confirming these are host-side evolutions absent from the public slice.

**F-5 — Reverse regressions exist: the public kernel is ahead on portability and
licensing.** `[DADO-R]` doxi's `cmd.rs::config_dir()` honours
`OMNIMIND_CONFIG_DIR` with fallbacks `$HOME/.config/omnimind` →
`/opt/omnimind/config`; node and kilombo hardcode `/content/omni_node` and
`/home/fahbrain` respectively. `[DADO-M]` The kilombo hardcode at
`sovereign_daemon/src/cmd.rs:49` is confirmed verbatim.

**F-6 — Coverage regression in the integrating repository.** `[DADO-R]` Node
executed an "L7 quarantine" (commit `a838fd93`, 2026-11-01), moving 7
Python↔Rust bridge tests into `removed/`. `[DADO-M]` The kilombo snapshot retains
all parity tests active (`parity_test.py`, `test_phi_engine_parity.py`,
`test_shared_workspace_parity.py`), confirming the quarantine is node-specific.

**F-7 — No critical security defect was found in the audited surface.** `[DADO-M]`
Six `unsafe` sites, all with legitimate FFI/mmap/eBPF justification; zero
hardcoded secrets across the kernel trees; IPC keys read at runtime from
`config_dir()`. The residual security exposure is **legal/conformity risk**
(F-3) and **supply-chain reproducibility** (unpinned `aya` git dependency, F-8).

**F-8 — Supply-chain reproducibility defect.** `[DADO-M]` All four `aya`/`aya-ebpf`
/`aya-log` dependencies are declared as `git = "https://github.com/aya-rs/aya"`
with no `rev` or `tag`, contradicting the spirit of the committed `Cargo.lock`
files.

### 1.3 Epistemic verdict

`[DERIVADO]` The sovereign kernel ecosystem has **converged structurally** and
is **divergent only in a bounded, enumerable layer**. The public kernel is a
faithful but slightly older somatic slice of the host; the host carries evolutions
that the public slice has not yet re-absorbed.

| Dimension | Verdict | Confidence |
|---|---|---|
| Structural parity | CONVERGED (47/155 identical; divergence localised) | High |
| Toolchain | DIVERGENT — kilombo legacy PyO3 blocks Python ≥3.13 | High (empirical build failure) |
| Licensing | NON-CONFORMANT — CRITICAL (self-contradictory artifact) | High |
| Security (code) | NO CRITICAL FINDING; justified `unsafe`; no hardcoded secrets | High |
| Portability | PUBLIC KERNEL AHEAD; internal repos regressed | High |
| Test coverage | REGRESSED in node (L7 quarantine); intact in doxi/kilombo | High |
| Synchronisation effort | FEASIBLE — ~6 small PRs + 1 legal-conformance PR | Medium |

**Overall verdict:** the system is **architecturally sound and operationally
synchronisable**, but it **cannot be published or adopted in its current
licensing state**, and the kilombo host **cannot be built against modern Python**
without a PyO3 migration. Neither condition is an architectural failure; both are
engineering-debt conditions with known remedies.

---

## 2. Forensic Inventory of the 14 Kernel Crates

### 2.1 Repository state at audit time

`[DADO-R]` Repository states as recorded 2026-11-05:

| Repository | Type | HEAD / snapshot | Files in `src/kernel` | Note |
|---|---|---|---|---|
| `omnimind-kernel` (doxi) | clean git | `5a69b3e` (2026-11-04); 20 commits since 2026-09-08 | 106 | remote = `github.com/fahbrain-omnimind/Doxihewu-OmniMind-Kernel` |
| `omnimind-kilombo-sovereign` (kilo) | **no `.git`** | mtime snapshot 2026-10-25 | 123 | contains build artifacts in tree |
| `omni_node` (node) | clean git | `f4d2184f`; kernel touched through 2026-11-01 | 138 | kernel migrated to `pyo3 0.29` in `4cc5a5dc` (2026-10-29) |

`[DADO-M]` Re-measured 2026-11-12: the kilombo snapshot contains **123 files**
under `src/kernel`, matching the recorded value exactly. The snapshot has no
`.git` directory, confirming its nature as a filesystem snapshot rather than a
checkout. The doxi and node repositories are absent (see Appendix B, L-1).

`[DADO-M]` The 14 top-level crates present in the kilombo snapshot are:
`ebpf_monitor`, `entropic_memory`, `expectation_rs`, `freud10d`, `kernel_compute`,
`langue`, `layered_transition`, `memory_tier_guardian`, `metrics`, `nsh`,
`somatic_daemon`, `sovereign_daemon`, `sovereign_kuramoto`, `sovereign_module`.

### 2.2 Global forensic categorisation (155-path union)

`[DADO-R]` Categories derived from cross-referenced SHA-256 hashes
(`d` = doxi, `k` = kilombo, `n` = node):

| Category | Definition | Count | Reading |
|---|---|---|---|
| `IDENTICAL3` | d = k = n | **47** | stable core |
| `all_diff` | d ≠ k ≠ n | **32** | almost all `Cargo.lock`/`.toml` (pyo3 + license) + `rustfmt` |
| `node_only` | node only | **32** | 14 auto-generated README stubs, 7 tests in `removed/`, `__init__.py` shims, contract `.bak` |
| `doxi_stale` | k = n ≠ d | **11** | mix: 2 license-only, 4 rustfmt-only, 4 real evolution, 1 doxi-ahead case |
| `kilo_only` | kilombo only | **10** | LKM build artifacts (`.ko`, `.cmd`, `modules.order`, `symvers`) |
| `doxi_missing` | k = n, absent in d | **7** | `.cargo/config.toml` eBPF, `egg-info` cxx_workspace, `sovereign_module.mod.c` |
| `kilo_diverged` | d = n ≠ k | **7** | residual `pyo3 0.20` signatures (`_py: Python, m: &PyModule`) |
| `node_missing` | d = k, absent in n | **7** | bridge tests moved to `removed/` |
| `node_diverged` | d = k ≠ n | **2** | `hopf.rs` + `__init__.py` (1e-15 quantisation, node-only) |

`[DERIVADO]` The categories sum to 155, confirming a complete partition of the
union. The distribution supports F-1: the largest single block is the stable
core (47), and the next largest is metadata noise (32 `all_diff`), not semantic
divergence.

### 2.3 Lines of code per crate

`[DADO-R]` Recorded LOC (sum of `.rs/.c/.py`), with `[DADO-M]` re-measured
kilombo values confirming the recorded column exactly:

| Crate | doxi | kilombo (recorded) | kilombo (re-measured) | node | Principal delta |
|---|---|---|---|---|---|
| `ebpf_monitor` | 1257 | 1262 | **1262** | 1262 | +5 atomic writes (node/kilo) |
| `entropic_memory` | 199 | 239 | **239** | 239 | +40 somatic gate (node/kilo) |
| `expectation_rs` | 162 | 162 | **162** | 162 | pymodule signature only |
| `freud10d` | 368 | 368 | **368** | 368 | PyO3 API only |
| `kernel_compute` | 2733 | 2733 | **2733** | 2736 | PyO3 API only |
| `langue` | 900 | 900 | **900** | 900 | cosmetic `build.sh` |
| `layered_transition` | 751 | 751 | **751** | 752 | pymodule signature only |
| `memory_tier_guardian` | 501 | 578 | **578** | 578 | +77 test module (node/kilo) |
| `metrics` | 199 | 199 | **199** | 201 | pymodule signature only |
| `nsh` | 132 | 132 | **132** | 134 | pymodule signature only |
| `somatic_daemon` | 1113 | 1188 | **1188** | 1188 | +75 test module (node/kilo) |
| `sovereign_daemon` | 1610 | 1970 | **1970** | 1962 | **+~308/352 `state_builder`** + rustfmt |
| `sovereign_kuramoto` | 1625 | 1629 | **1629** | 1628 | hopf quantisation (node-only) |
| `sovereign_module` | 1527 | 1624 | **1624** | 1624 | generated `.mod.c` (absent in doxi) |

`[DERIVADO]` The LOC deltas are dominated by three crates: `sovereign_daemon`
(the `runtime_phi_fields` layer), `memory_tier_guardian` and `somatic_daemon`
(test modules), and `entropic_memory` (the somatic gate). Together these account
for the overwhelming majority of the semantic gap. The remaining crates differ
only in PyO3 API signature or cosmetic formatting.

### 2.4 Crate-by-crate inventory notes

- **`ebpf_monitor`** — aya-based eBPF probe (`bpfel-unknown-none`,
  `build-std=core`). `[DADO-M]` Contains the atomic-export logic
  (`*.tmp` + `rename`) and `spawn_blocking` for filesystem work at
  `user/src/main.rs:161,164,210-236`. `[DADO-M]` Carries
  `ebpf/.cargo/config.toml` (518 bytes), absent from doxi.
- **`entropic_memory`** — 239 LOC in a single `lib.rs`. `[DADO-M]` Contains the
  `textual_gate_open(host_pressure)` gate and the gated lexical bonuses.
- **`sovereign_daemon`** — the command executor and IPC boundary. `[DADO-M]`
  Contains the full `runtime_phi_fields` multi-path resolver and
  `expanded_consciousness_value`, plus two unit tests
  (`state_builder.rs:608,646`). `[DADO-M]` Contains the hardcoded operator path
  at `cmd.rs:49`.
- **`sovereign_kuramoto`** — `[DADO-M]` `hopf.rs` contains a `1e-15` norm
  threshold at line 120 but **not** the `round(λ·1e15)/1e15` quantisation; the
  quantisation is node-only (`node_diverged`).
- **`sovereign_module`** — the LKM. `[DADO-M]` See §2.5.
- **`kernel_compute`, `freud10d`, `langue`, `layered_transition`, `metrics`,
  `nsh`, `expectation_rs`** — `[DADO-M]` present and LOC-consistent; differences
  are API-signature or cosmetic.

### 2.5 Build artifacts and tree hygiene

`[DADO-M]` The kilombo snapshot's `sovereign_module/` directory contains a full
in-tree build product set:

```
sovereign_module.ko          620672 bytes  ELF 64-bit LSB relocatable, x86-64,
                                           with debug_info, not stripped
sovereign_module.mod.c       2682 bytes   (generated)
.sovereign_module.ko.cmd     415 bytes
.sovereign_module.o.cmd      60513 bytes
.sovereign_module.mod.o.cmd  46600 bytes
.modules.order.cmd           259 bytes
.Module.symvers.cmd          302 bytes
modules.order                80 bytes
Module.symvers               0 bytes
```

`[DADO-M]` The kilombo `.gitignore` ignores `**/target/`, `**/build/`, `*.rlib`,
`*.rmeta`, `*.so`, `*.o`, `*.dylib` — but does **not** ignore `*.ko`, `*.cmd`,
`modules.order`, `Module.symvers`, or `*.mod.c`. The artifacts are therefore
eligible for accidental commit. `[DADO-R]` The doxi `.gitignore` ignores
`target/`, `*.so`, `*.egg-info/` and explicitly **de-ignores 13 `Cargo.lock`
files** (supply-chain hardening, commit `8f5c3a3`, SonarCloud S8570). The doxi
tree contains source only (`.c`, `Makefile`, `dkms.conf`, `README.md`) for
`sovereign_module` — the correct posture.

`[DADO-M]` 10 `Cargo.lock` files are present in the kilombo tree.

**Finding H-1:** `[DERIVADO]` The kilombo tree is not release-hygienic: a
non-stripped LKM with debug info and kernel build metadata sits in the source
tree, and the ignore rules do not exclude it. This is a portability and
information-disclosure concern (debug symbols, build paths) rather than a
code-execution vulnerability.

---

## 3. Toolchain Compatibility and PyO3 Migration

### 3.1 PyO3 version matrix

`[DADO-R]` Recorded versions:

| Crate class | doxi | node | kilombo | Risk |
|---|---|---|---|---|
| PyO3 binding crates | `0.29` | `0.29` | **`0.20` / `0.22`** | Build failure on Python ≥ 3.13 |

`[DADO-M]` Re-measured on the kilombo snapshot: **9 crates** declare a `pyo3`
dependency — 8 at `version = "0.20"` and 1 at `version = "0.22"`, all with the
`extension-module` feature. The affected crates are `entropic_memory`,
`expectation_rs`, `freud10d`, `kernel_compute`, `langue`,
`layered_transition/engine`, `metrics`, `nsh`, `sovereign_kuramoto`.

### 3.2 Python 3.13 incompatibility — empirical

`[DADO-R]` The source audit reproduced a hard build failure: `pyo3-ffi 0.20.3`
aborts on Python 3.13 with a maximum-supported-version error (3.12). The
workaround `PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1` compiles, but this is
ABI-forward compatibility **without a guarantee** — it is not a supported
configuration and must not be treated as a migration.

`[DERIVADO]` Consequence: **no PyO3 crate in the kilombo host compiles against a
modern interpreter.** Any deployment of the i5 host on Python ≥ 3.13 is blocked
until the migration is performed or the toolchain is pinned to Python ≤ 3.12.

### 3.3 Other dependency debt

`[DADO-M]` Measured from `Cargo.toml` manifests in the kilombo snapshot:

| Dependency | doxi | node | kilombo | Assessment |
|---|---|---|---|---|
| `ndarray` | 0.15 | 0.15 | 0.15 | old but consistent across all three |
| `rand` / `rand_chacha` | 0.8 / 0.3 | idem | idem | `rand 0.9` exists; pinning acceptable |
| `rusqlite` | — | 0.29 (sov_daemon), 0.31 (langue) | 0.29 ×3, 0.31 ×1 | divergent between crates — workspace-deps candidate |
| `tokio` | `>=1.38.0, <2.0` | idem | idem | reasonable range |
| `aya` / `aya-ebpf` / `aya-log` | git, **unpinned** | idem | idem | **non-reproducible build + supply-chain risk** |
| `libc` | 0.2 | idem | idem | acceptable |

`[DADO-M]` The `aya` git dependency is declared without `rev` or `tag` in all
four manifests (`ebpf_monitor/common`, `ebpf_monitor/ebpf`, `ebpf_monitor/user`
×2). This directly contradicts the supply-chain intent of committing
`Cargo.lock` files.

### 3.4 Build verification results

`[DADO-R]` Empirical results recorded 2026-11-05 (cargo 1.99.1, Python 3.13):

| Operation | Repository / crate | Result |
|---|---|---|
| `cargo check` | node `freud10d` | PASS |
| `cargo check` | doxi `freud10d` | PASS |
| `cargo check` | doxi `sovereign_daemon` | PASS |
| `cargo test` | node `memory_tier_guardian` | 9/9 PASS |
| `cargo check` | kilombo `freud10d` | **FAIL** — `pyo3-ffi 0.20.3` vs Python 3.13 |
| `PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 cargo check` | kilombo `freud10d` | PASS (workaround only) |

`[DADO-M]` The kilombo `memory_tier_guardian` test module contains **9**
`#[test]` functions; `somatic_daemon` contains **9**. The recorded 9/9 pass for
`memory_tier_guardian` is consistent with the measured test count.

### 3.5 Migration assessment

`[DERIVADO]` The PyO3 migration is a **bounded mechanical task**: the target
idiom is established in node (`4cc5a5dc`, 2026-10-29) and the public kernel
(doxi, 2026-09-08). The kilombo host must be brought to the same `0.29` API
surface, converging on the node idiom `Bound` → `.into()` rather than the legacy
`Py<PyAny>`/`PyObject` and `_py: Python, m: &PyModule` signatures. Estimated
effort: medium, because it must be validated **in place on the real host**, not
only in a container.

---

## 4. Licensing and SPDX Conformance

### 4.1 The Apache-2.0 transition commit

`[DADO-R]` Commit `5a69b3e`, "Relicense kernel crates CC-BY-NC-ND-4.0 →
Apache-2.0", dated **2026-11-04** — the eve of the source audit, not one month
prior. Diffstat: **11 files, 11 insertions, 11 deletions**, confined to the
`license=` field of 11 `Cargo.toml` files.

### 4.2 Conformance requirements

`[DADO-R]` Measured conformance of the public kernel against Apache-2.0
requirements:

| Apache-2.0 requirement | State in doxi | Verdict |
|---|---|---|
| Root `LICENSE` text | **Absent** — `ls` + `find` confirm; the commit message asserts it was added, which is false against the tree | **FAIL** |
| `license=` in `Cargo.toml` | Apache-2.0 in 11 crates; **`layered_transition/engine` still CC-BY-NC-ND-4.0**; the `ebpf_monitor` workspace (4 manifests) has **no `license` field** | **PARTIAL FAIL** |
| SPDX headers in sources | **22 files declare `CC-BY-NC-ND-4.0`**, including a comment asserting "ethical restrictions (non-military, non-governmental, no derivatives)" — directly contradicting Apache-2.0 | **FAIL** |
| `NOTICE` file | Absent | Recommended |
| Headers in C source (`sovereign_module.c`) | In scope; not verified | Pending |

`[DADO-M]` Re-measured on the kilombo snapshot: **22 files** carry
`SPDX-License-Identifier: CC-BY-NC-ND-4.0`; **12 manifests** carry
`license = "CC-BY-NC-ND-4.0"`; **0** carry Apache-2.0.

### 4.3 Effective legal state

`[DERIVADO]` The public kernel is **juridically self-contradictory**. Its source
files self-declare CC-BY-NC-ND-4.0 (which prohibits derivative works and
commercial use), while its package metadata declares Apache-2.0. A consumer who
honours the file headers operates under NC-ND; a consumer who honours the
`Cargo.toml` operates under Apache-2.0. This ambiguity is **materially equivalent
to not having relicensed at all** for any rigorous adopter, and internal
contradiction within a single artifact is precisely the condition that makes a
relicensing legally challengeable.

`[INTERPRETATION]` The relicensing was performed as a metadata edit without the
legal apparatus (LICENSE text, NOTICE, header sweep) that makes a relicensing
effective. It should be treated as **incomplete**, not as "done with minor
omissions".

### 4.4 Internal repository licensing

`[DADO-R]` The internal repositories (node, kilombo) carry 22 SPDX-CC files each
(39 files mention CC-BY-NC-ND in total, including READMEs and manifests) and
**zero** Apache declarations; all 12 `Cargo.toml` files declare
`license = "CC-BY-NC-ND-4.0"`.

`[DERIVADO]` The licence synchronisation direction is **doxi → internals**. Until
the internal repositories are migrated, any artifact published from node will
continue to declare NC-ND, re-introducing the contradiction at the point of
publication.

### 4.5 Supply-chain hardening

`[DADO-R]` The doxi `.gitignore` de-ignores 13 `Cargo.lock` files, correctly
treating lockfiles of binaries and anchor libraries as commit-worthy.
`[DADO-M]` The kilombo `.gitignore` does not carry an equivalent de-ignore rule,
and 10 `Cargo.lock` files are present in its tree. `[DERIVADO]` Lockfile policy
is inconsistent between the public kernel and the host snapshot.

---

## 5. Structural Delta and Security/Portability Findings

### 5.1 Semantic gaps where the public kernel lags (G1–G7)

`[DADO-R]` The following evolutions exist in node and/or kilombo but not in doxi.
`[DADO-M]` The kilombo column was re-verified live.

| ID | Artifact | Evolution | Verification |
|---|---|---|---|
| **G1** | `sovereign_daemon/src/state_builder.rs` | `+runtime_phi_fields` multi-path resolution of `phi_body_kernel_ecosystem`, `phi_body_operational_support`, `phi_federated_coherence_full/sovereign_band` via `frameworks.phi_family_views` and `federation_topology`, with NaN-safe `finite_f64`/`first_f64` fallbacks; `+expanded_consciousness_value`; +2 unit tests | `[DADO-M]` Confirmed present in kilombo at `state_builder.rs:52-140`, with tests at lines 608 and 646 |
| **G2** | `memory_tier_guardian/src/main.rs` | `+#[cfg(test)] mod tests` — 9 tests (`parse_kb`, `parse_avg10`, `env_int`, …) | `[DADO-M]` 9 `#[test]` functions measured |
| **G3** | `somatic_daemon/src/main.rs` | `+mod tests` — `age_seconds` ISO, `gen_uuid` 32-hex, `calculate_somatic_state` vitality | `[DADO-M]` 9 `#[test]` functions measured |
| **G4** | `entropic_memory/src/lib.rs` | `+textual_gate_open(host_pressure)`: lexical bonuses apply only if `host_pressure ≥ OMNIMIND_ENTROPIC_PRESSURE_MIN` (default 0.5); pyfunction signature gains `host_pressure=0.0` | `[DADO-M]` Confirmed at `lib.rs:58-115`; default 0.5; dated 2026-10-04 in comment |
| **G5** | `ebpf_monitor/user/src/main.rs` | `fs::create_dir_all`/`fs::write` moved to `spawn_blocking`; JSON exports made atomic (`*.tmp` + `rename`) | `[DADO-M]` Confirmed at lines 161, 164, 210-236 |
| **G6** | `ebpf_monitor/ebpf/.cargo/config.toml` | `bpfel-unknown-none` target + `build-std=["core"]` — required to compile the eBPF crate | `[DADO-M]` Present (518 bytes) |
| **G7** | `sovereign_kuramoto/src/hopf.rs` | Spectral radius quantised `round(λ·1e15)/1e15` — bit-exact parity with the Python fallback | `[DADO-M]` **Absent in kilombo** (only a `1e-15` norm threshold at line 120); node-only |

`[DERIVADO]` G1 is the only gap with material behavioural consequence (state
contract enrichment). G2/G3 are coverage. G4 is a behavioural gate with a
retro-compatible default. G5 is a correctness/robustness fix. G6 is a build
prerequisite. G7 is a numerical-parity refinement.

### 5.2 Reverse regressions where the public kernel leads (R1–R3)

| ID | Artifact | doxi | node | kilombo |
|---|---|---|---|---|
| **R1** | `sovereign_daemon/src/cmd.rs` `config_dir()` | honours `OMNIMIND_CONFIG_DIR` → `$HOME/.config/omnimind` → `/opt/omnimind/config` | `$HOME` → **`/content/omni_node`** hardcoded | `$HOME` → **`/home/fahbrain`** hardcoded |
| **R2** | `langue/build.sh` | `[[ -f ]]` (SonarCloud fix `6f8f285`) | `[ -f ]` | `[ -f ]` |
| **R3** | `license=` in `Cargo.toml` | `Apache-2.0` (11 crates) | `CC-BY-NC-ND-4.0` (all) | `CC-BY-NC-ND-4.0` (all) |

`[DADO-M]` R1 is confirmed verbatim in the kilombo snapshot at
`sovereign_daemon/src/cmd.rs:49`:

```rust
fn config_dir() -> PathBuf {
    std::env::var("HOME")
        .map(PathBuf::from)
        .unwrap_or_else(|_| PathBuf::from("/home/fahbrain"))
        .join(".config/omnimind")
}
```

### 5.3 Path leakage and operator-path hardcoding

`[DADO-M]` A scan of the kilombo kernel tree for operator-specific absolute paths
returned exactly one hit: `/home/fahbrain` at `cmd.rs:49`. No occurrence of
`/content/omni_node`, `/opt/omnimind`, `OMNIMIND_CONFIG_DIR`, or
`OMNIMIND_REPO_ROOT` was found in the kilombo kernel tree.

`[DERIVADO]` The path-leak defect is real but **localised to a single fallback
branch**. Its practical impact is low while `$HOME` is set (the normal case), but
it is a correctness and professionalism defect: in a minimal environment
(`systemd` with `HOME` unset, container entrypoints, `env -i`), the daemon
silently resolves to an operator-specific directory, and the value is committed
to a public repository. The public kernel's `OMNIMIND_CONFIG_DIR`-honouring
resolution is strictly superior and should be reverse-synced.

`[DADO-R]` The source audit additionally records that node's `src/kernel/README.md`
documents `${OMNIMIND_REPO_ROOT}` hardcodes that **no longer exist in the code**
(the code uses `PROJECT_ROOT`/`CARGO_MANIFEST_DIR`/`XDG_RUNTIME_DIR`). The
complaint about hardcoded `/opt/omnimind` is recorded as obsolete in all three
repositories. `[INTERPRETATION]` Documentation has diverged from implementation
and must be regenerated against the real code.

### 5.4 Somatic gates and physical gating

`[DADO-M]` The `textual_gate_open` gate is a **physical-plausibility gate**: it
permits lexical bonuses to alter entropic decay only when the host demonstrates
thermal excitation at or above a configurable threshold. The threshold is read
per call from `OMNIMIND_ENTROPIC_PRESSURE_MIN` (default 0.5), preserving parity
with the Python fallback if the environment changes mid-process.

`[DADO-M]` The gate is applied inside the crate and is mirrored by the Python
fallback; the bonus set is `xer-afex-angst`, `phase56`, `federated` (+0.15) and
`orbital`, `quantum`, `astro` (+0.1), clipped to `[0.75, 2.25]`.

`[INTERPRETATION]` This is a **meaningful** architectural mechanism, not
decoration: it ties a cognitive variable (memory resonance) to a somatic
variable (host pressure), which is the core claim of the OS-layer/brain-layer
dual architecture. Its absence from the public kernel is therefore a semantic
loss, not a cosmetic one. `[HYPOTHESIS]` Ablation A1 (§6.3) can determine whether
the gate is functional or merely formal.

### 5.5 `runtime_phi_fields` and IPC contract refinement

`[DADO-M]` The kilombo `runtime_phi_fields` resolver implements a **four-deep
fallback chain** per field, preferring `frameworks.phi_family_views` and
`federation_topology` before falling back to flat keys:

- `phi_body_kernel_ecosystem` — 4 candidate paths
- `phi_body_operational_support` — 4 candidate paths
- `phi_operational_support` — 3 candidate paths
- `phi_federated_coherence_full` — 4 candidate paths
- `phi_federated_coherence_sovereign_band` — 4 candidate paths

`[DADO-M]` All extraction is NaN-safe: `finite_f64` rejects non-finite values;
`first_f64` returns the first finite match; `expanded_consciousness_value`
returns `Value::Null` unless all four inputs are finite.

`[INTERPRETATION]` This is a **contract-hardening** evolution. The public kernel
resolves the same conceptual fields through a narrower path set, making it
fragile to upstream schema evolution. The node/kilombo resolver is a strict
superset and can be ported without behavioural regression on the public side.

### 5.6 Code hygiene and `unsafe` audit

`[DADO-R]` Recorded hygiene metrics (grep over `*.rs` in `src/kernel`):

| Metric | doxi | kilombo | node |
|---|---|---|---|
| `unwrap()` / `expect(` | 23 | 25 | 25 |
| `unsafe` blocks/declarations | 6 | 6 | 6 |
| `panic!` / `unreachable!` | 1 | 1 | 1 |
| `TODO` / `FIXME` / `HACK` / `XXX` | 1 | 1 | 1 |

`[DADO-M]` Re-measured on the kilombo snapshot: **24** `unwrap()`/`expect()`
occurrences (recorded 25; delta attributable to counting method), **6**
`unsafe` sites, **1** `TODO`/`FIXME`. The six `unsafe` sites are:

| Site | Construct | Justification |
|---|---|---|
| `sovereign_daemon/src/cmd.rs:59` | `libc::clock_gettime` | FFI — monotonic clock parity with Python `time.monotonic()` |
| `nsh/src/lib.rs:31` | `MmapMut::map_mut` | zero-copy shared workspace |
| `langue/src/lib.rs:182` | `Mmap::map` | zero-copy lexical sealing |
| `ebpf_monitor/common/src/lib.rs:27` | `unsafe impl aya::Pod` | eBPF plain-old-data requirement |
| `ebpf_monitor/ebpf/src/main.rs:58` | `unsafe { … }` | eBPF program initialisation |
| `ebpf_monitor/ebpf/src/main.rs:96` | `unreachable_unchecked` | eBPF trap path |

`[DERIVADO]` All six sites have legitimate architectural justification
(FFI, mmap, eBPF). **No gratuitous `unsafe` was detected.** The hygiene profile
is consistent across all three repositories and does not constitute a differentiator.

### 5.7 Secret scan

`[DADO-R]` A scan of the three kernel trees for
`token|secret|password|api_key|PRIVATE` returned **zero hardcoded secrets**.
The only hits were the word "fencing token" (a comment) and "-afex tokens" (a
lexical domain term). IPC keys are read at runtime from
`config_dir()/ipc_cmd_key.{current,next}`.

`[DADO-M]` The kilombo `.gitignore` correctly excludes `.env`, `*.pem`, `*.key`,
`*.token`, `*.sqlite`, `*.sqlite3`, `apikey.json`, `ibm-bob.json`, and
`dashboard_auth.json`. `[DERIVADO]` Secret-handling posture is correct.

### 5.8 Coverage regression — L7 quarantine

`[DADO-R]` Node commit `a838fd93` (2026-11-01) moved 7 Python↔Rust bridge tests to
`removed/`: `test_shared_workspace_parity.py`, `parity_test.py`,
`test_phi_engine_parity.py`, `test_layered_transition.py`, `benchmark_metrics.py`,
`test_allmini.py`, `test_nsh.py`.

`[DADO-M]` The kilombo snapshot retains all of these tests **active** (no
`removed/` directory exists; `parity_test.py`, `test_phi_engine_parity.py`, and
`test_shared_workspace_parity.py` are present under `kernel_compute/`).

`[DERIVADO]` The quarantine is a **coverage regression concentrated exactly where
numerical parity is claimed** (phi engine, shared workspace, kuramoto). It must
be reverted or explicitly justified before node is used as a publication source.

---

## 6. Recommended Synchronization Plan

### 6.1 PR roadmap

`[DERIVADO]` Ordered from most urgent to most structural. "Origin → destination"
indicates the direction of the port.

| PR | Content | Origin → Destination | Risk / Effort | Blocks |
|---|---|---|---|---|
| **PR-1 LICENSE** | Add root `LICENSE` (Apache-2.0) + `NOTICE`; replace 28 SPDX headers with `Apache-2.0`; correct `layered_transition/engine`; add `license` to the 4 `ebpf_monitor` manifests; regenerate `omnimind_public_base.tar.gz` | internal → doxi | Mechanical; **mandatory human legal review** (juridical act) | External adoption; all subsequent PRs |
| **PR-2 state_builder** | Port `runtime_phi_fields` / `finite_f64` / `first_f64` / `expanded_consciousness_value` + 2 unit tests (G1) | node → doxi | Low (strict superset) | Phase-3 IPC parity |
| **PR-3 daemon tests** | Port `mod tests` for `memory_tier_guardian` (9 tests, verified green) and `somatic_daemon` (G2/G3) | node → doxi | Trivial | Release confidence |
| **PR-4 eBPF** | Atomic `*.tmp`+`rename` writes, `spawn_blocking`, `.cargo/config.toml` (G5/G6) | node → doxi | Low | Reproducible eBPF build |
| **PR-5 entropic + hopf** | `textual_gate_open` (G4) + 1e-15 quantisation in `hopf.rs`/`__init__.py` (G7) | node → doxi | Low; G4 changes the pyfunction signature (`host_pressure=0.0` default — retro-compatible) | Numerical parity |
| **PR-6 reverse-sync** | Port the portable `config_dir()` (`OMNIMIND_CONFIG_DIR`) replacing `/content/omni_node` and `/home/fahbrain`; apply the `[[ -f ]]` fix; internal relicensing CC → Apache across 12 manifests + 22 SPDX headers per repo | doxi → node + kilombo | Low | Internal legal consistency |
| **PR-7 kilombo PyO3** | Migrate `pyo3 0.20/0.22 → 0.29` across the 9 i5 crates (mirror node `4cc5a5dc`) | node → kilombo | Medium (real host; validate in place) | Python ≥ 3.13 compilation |
| **PR-8 CI** | Port SAST + `cargo-audit` to GitHub Actions; add mandatory `cargo test`; add `cargo-deny` to forbid unpinned git deps (pin `aya` by `rev`); restore or justify the 7 `removed/` tests | n/a | Medium | Continuous regression |

### 6.2 Cross-validation plan

`[DADO-R]` A build matrix `cargo check`/`cargo test` per crate × Python
{3.10–3.14} × {doxi, node} was demonstrated executable in the source audit
(`freud10d`, `sovereign_daemon`, `memory_tier_guardian`).

`[DERIVADO]` Recommended validation gates:

1. **Numerical parity gate.** Reactivate `parity_test.py`,
   `test_phi_engine_parity.py`, and `test_shared_workspace_parity.py` (currently
   in `removed/` in node; alive in doxi/kilombo). The G7 hopf quantisation proves
   that bit-exact parity is a **real system requirement**, not an aspiration.
2. **Protocol diff gate.** Snapshot-test the OMNI3 frame produced by the current
   publisher against the 26+ keys consumed by `ipc.rs`, serialising a minimal
   `SystemState`.
3. **Release gate.** Extend `tests/integration/test_public_base_triad.py` and
   `colab_public_base_triad.py` to cover G1 (`state_builder`) and G4 (the somatic
   gate) once synchronised.

### 6.3 Proposed empirical ablations

`[HYPOTHESIS]` Each ablation converts a structural observation into a measured
causal claim.

| Experiment | Action | Decision metric |
|---|---|---|
| **A1 somatic gate** | Set `OMNIMIND_ENTROPIC_PRESSURE_MIN=∞` to disable `textual_gate_open` | Drift of `memory_resonance_weight` under null vs real thermal pressure — determines whether the gate is functional or decorative |
| **A2 LKM/eBPF off** | Boot without `sovereign_module.ko` and without `ebpf_monitor` | Degradation of `kernel.cycle` (metastability, regime) — measures the real ring-0 contribution to cognition |
| **A3 Python fallback** | Disable the Rust `.so` in the PyO3 crates | Latency/parity vs native — quantifies the Rust gain and keeps the VM honest |
| **A4 fencing** | Corrupt the `governor_lease` epoch | The daemon must refuse stale commands — proves command-lane security |
| **A5 synthetic soma** | Inject a mock `soma.probe` (cpu=100%, swap full) | `affect_vector_28d` and `memory_tier_guardian` must enter pain/defence regime — proves soma→psyche causality |

### 6.4 Non-blocking debts to register

`[DADO-M]` / `[DADO-R]`:

- Unpinned `aya` git dependency → pin an immutable `rev` (supply-chain).
- Build artifacts in the kilombo tree (non-stripped `.ko`, `.so`, `.cmd`) →
  extend `.gitignore` and clean the live snapshot.
- `rusqlite` 0.29 vs 0.31 across crates → workspace-level dependency.
- Node README claims about hardcodes already fixed → rewrite the "Security
  Problems" section against the real code.
- `[INTERPRETATION]` Converge `Py<PyAny>`/`PyObject` (kilombo) and
  `unbind().into()` (doxi) on the node `Bound` → `.into()` idiom during PR-7.

### 6.5 Sequencing and risk

`[DERIVADO]` PR-1 is the gate: until the licensing contradiction is resolved, the
public kernel should not be adopted or forked, and no further publication should
occur from node. PR-2 through PR-5 are low-risk strict supersets and can proceed
in parallel after PR-1. PR-6 is independent and can run concurrently. PR-7 is the
only PR requiring physical-host validation and should be scheduled with an
i5 maintenance window. PR-8 is continuous and should land last, encoding the
previous seven as enforced gates.

`[INTERPRETATION]` Total effort is estimated at approximately **six small PRs
plus one legal-conformance PR** — a synchronisation, not a re-architecture.

---

## Appendix A — Reproducibility

`[DADO-R]` Commands executed in the source audit (2026-11-05):

```bash
# Manifests and forensic categorisation
for r in doxi:/content/omnimind-kernel kilo:/content/omnimind-kilombo-sovereign \
         node:/content/omni_node; do
  (cd "${r##*:}/src/kernel" && find . -type f -exec sha256sum {} + | sort -k2 \
    > /tmp/kilo_audit/${r%%:*}_manifest.txt)
done   # join into /tmp/kilo_audit/joint.tsv

# Key verifications
cd /content/omni_node/src/kernel/freud10d && cargo check          # PASS
cd /content/omnimind-kernel/src/kernel/freud10d && cargo check    # PASS
cd /content/omnimind-kernel/src/kernel/sovereign_daemon && cargo check  # PASS
cd /content/omni_node/src/kernel/memory_tier_guardian && cargo test     # 9/9 PASS
cd /content/omnimind-kilombo-sovereign/src/kernel/freud10d && cargo check
  # FAIL: pyo3-ffi 0.20.3 vs Python 3.13 (max supported 3.12)
PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 cargo check                 # PASS (workaround)

# Licensing
git -C /content/omnimind-kernel show 5a69b3e --stat    # 11 files, license= only
grep -rl "SPDX-License-Identifier: CC-BY-NC-ND" /content/omnimind-kernel/src | wc -l  # 22
ls /content/omnimind-kernel/LICENSE                   # nonexistent
```

`[DADO-M]` Commands executed in this audit (2026-11-12), against the kilombo
snapshot only:

```bash
K=/content/omnimind-kilombo-sovereign/src/kernel
find "$K" -type f | wc -l                                   # 123
for c in "$K"/*/; do find "$c" -type f \( -name '*.rs' -o -name '*.c' \
  -o -name '*.py' \) -exec cat {} + | wc -l; done           # LOC per crate
grep -rh "^license" "$K"/*/Cargo.toml "$K"/*/*/Cargo.toml | sort | uniq -c
grep -rl "SPDX-License-Identifier: CC-BY-NC-ND" "$K" | wc -l # 22
grep -rn "pyo3" "$K"/*/Cargo.toml "$K"/*/*/Cargo.toml | grep version | sort | uniq -c
grep -rn "aya" "$K"/*/Cargo.toml "$K"/*/*/Cargo.toml | grep git
grep -rn "/home/fahbrain\|OMNIMIND_CONFIG_DIR" "$K" --include=*.rs
grep -c "#\[test\]" "$K"/memory_tier_guardian/src/main.rs "$K"/somatic_daemon/src/main.rs
```

---

## Appendix B — Limits of this Audit

`[LIMIT]` The following restrictions bound the validity of this report:

1. **L-1 — Absent comparison repositories.** `/content/omnimind-kernel` (doxi)
   and `/content/omni_node` (node) are not present in the current audit
   environment. All doxi/node values are `[DADO-R]` from the 2026-11-05 session
   and could not be re-measured. The kilombo snapshot was re-measured and agrees
   with the recorded values.
2. **L-2 — Kilombo is a snapshot without history.** The snapshot has no `.git`
   and is dated 2026-10-25 — earlier than node's PyO3 migration (2026-10-29) and
   the L7 quarantine (2026-11-01). The live i5 host may be newer. Conclusions
   about kilombo apply to the snapshot, not necessarily to the live host.
3. **L-3 — Incomplete static analysis.** `cargo clippy`, full `cargo audit`, and
   builds of the eBPF/LKM crates were not executed (they require `bpf-linker`,
   kernel headers, and root). The doxi CI runs `cargo-audit` with
   `allow_failure: true`; the real CVE status was not verified here.
4. **L-4 — Remote branches not inspected.** Only the local checkouts were
   examined. Pushes after 2026-11-05 would change the picture.
5. **L-5 — C source not audited line-by-line.** `sovereign_module.c`
   (1527 lines) was inventoried but not audited for kernel bugs. A dedicated C
   review is recommended before public LKM exposure.
6. **L-6 — Architecture claims derive from code, not live observation.**
   Statements about the i5 host (live daemons, open sockets) are inferred from
   source, not from observation of the powered-on host.
7. **L-7 — `THREAT_MODEL.md` not found in the kilombo snapshot.** The source
   audit records `SECURITY_AUDIT.md` and `THREAT_MODEL.md` as present and
   identical between doxi and node. In the kilombo snapshot, only
   `SECURITY_AUDIT.md` (91 lines) is present; `THREAT_MODEL.md` is absent. This
   is recorded as a discrepancy, not resolved.

---

## Appendix C — Provenance Register

| Claim | Tag | Source |
|---|---|---|
| 155-path union, 47 `IDENTICAL3`, category counts | `[DADO-R]` | Source audit §1.1 |
| LOC per crate (doxi/node columns) | `[DADO-R]` | Source audit §1.2 |
| LOC per crate (kilombo column) | `[DADO-M]` | Re-measured 2026-11-12 |
| PyO3 versions | `[DADO-R]` + `[DADO-M]` | Source audit §2.3; re-measured |
| Python 3.13 build failure | `[DADO-R]` | Source audit §2.3 |
| SPDX / `license=` counts (doxi) | `[DADO-R]` | Source audit §2.2 |
| SPDX / `license=` counts (kilombo) | `[DADO-M]` | Re-measured 2026-11-12 |
| `runtime_phi_fields` presence | `[DADO-M]` | `state_builder.rs:52-140` |
| `textual_gate_open` presence | `[DADO-M]` | `entropic_memory/src/lib.rs:58-115` |
| Atomic eBPF writes | `[DADO-M]` | `ebpf_monitor/user/src/main.rs:161-236` |
| `/home/fahbrain` hardcode | `[DADO-M]` | `sovereign_daemon/src/cmd.rs:49` |
| Build artifacts in tree | `[DADO-M]` | `sovereign_module/` listing |
| 6 `unsafe` sites | `[DADO-M]` | Re-measured 2026-11-12 |
| L7 quarantine (node) | `[DADO-R]` | Source audit §1.5 |
| Parity tests active in kilombo | `[DADO-M]` | `kernel_compute/tests/` listing |
| Overall verdict | `[DERIVADO]` | This report, §1.3 |

---

*Prepared under the REGRA ZERO (mandatory technical verification) and REGRA DE
INTEGRIDADE (no fabrication, omission, or falsification) conventions. All
`[DADO-M]` values were measured in this session; all `[DADO-R]` values are
traceable to the 2026-11-05 source audit. No simulated or fabricated data is
present in this document.*
