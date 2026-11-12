# Sovereign Kernel Coupling & Architecture Audit Report

**Doc ID**: OW-AUD-EN-001  
**Project**: OmniMind / Omni-Worker Dual-Brain Architecture  
**Classification**: Technical Audit Summary [DATA][DERIVED]  
**Date**: November 2026  
**License**: Apache-2.0  

---

## Executive Summary

This report consolidates technical findings from architectural audits of the coupling between the Doxihewu-OmniMind Sovereign Kernel and the operational `omni_worker` runtime. It documents interface contracts, state persistence, memory decoupling, and cryptographic evidence verification required for high-assurance autonomous agency under the Google Gemma 4 Developer Agent track.

---

## 1. Architectural Topology & Coupling Boundary

```mermaid
graph TD
    subgraph Sovereign Kernel Layer
        SK["Doxihewu Sovereign Kernel (Rust/C)"]
        SOV_MOD["sovereign_module.c (18D Affect/Phi Engine)"]
        LANGUE["Langue Handle Store (SQLite + zero-copy mmap)"]
    end

    subgraph Operational Worker Layer (omni_worker)
        API["Worker API (:8081 FastAPI)"]
        ANALYST["Analyst Brain (:8098 Gemma-4-12B-it)"]
        EXECUTOR["Executor Brain (:8099 Gemma-4-E4B-it)"]
        LOOP["Integration Loop (Cadence & Governance)"]
        GUARD["State Guard & Manifest Validator"]
    end

    SK --- SOV_MOD
    SK --- LANGUE
    SOV_MOD -->|"libsovereign_core.so (C FFI)"| LOOP
    LOOP --> API
    LOOP --> ANALYST
    LOOP --> EXECUTOR
    LOOP --> GUARD
```

### Key Conformance Attributes:
1. **Decoupled Fallback**: `omni_worker` is self-contained. When `libsovereign_core.so` is absent or hardware constraints restrict C FFI compilation, the system falls back gracefully to Python-native analytical vectors without crashing (`fail-open` observation, `fail-closed` execution gating).
2. **State Protection**: Persistent state directories (`data/`, `logs/`, `runtime_config/`) are governed by atomic filesystem staging and strict `0o600` access permissions.
3. **Cryptographic Identity**: State snapshots and witness events are verified via SHA-256 Merkle chains before restore operations.

---

## 2. Security & CodeQL Conformance Audit

During the Q4 2026 security verification, automated scans identified and resolved critical findings across repositories:

| Alert ID | Target Subsystem | Severity | CWE Class | Remediation Applied |
|---|---|---|---|---|
| **#1 (Kernel)** | `src/kernel/langue/src/lib.rs:253` | High | CWE-312 | Replaced dynamic string formatting with parameterized SQL queries (`params![prefix]`). |
| **#13 (Worker)** | `src/omni_coworker/store/code_index.py:410` | High | CWE-312 | Enforced `0o600` POSIX file creation mode on symbolic hypergraph serialization; renamed token redactor. |
| **#21 & #26 (Worker)** | `src/omni_coworker/integration_loop/api.py` | Medium | CWE-209 / CWE-497 | Sanitized exception flows through dedicated `_sanitize_for_api()` filter, eliminating stack-trace leaks on `/loop/run`. |
| **#25 (Worker)** | `scripts/acervo_vectorize/vectorize_acervo_canonical.py` | High | CWE-116 | Replaced vulnerable regex filters with Python standard `html.parser.HTMLParser`. |

---

## 3. Sovereign Module & Dimension Mapping

The 18-dimensional state vector computed by the kernel FFI interface maps directly to agent cognitive and somatic postures:

- **Somatic Axis**: CPU load, RAM utilization, GPU temperature/VRAM, PSI metrics (I/O pressure, memory pressure).
- **Affective Axis**: Valence, arousal, anxiety, curiosity, shame, memory integrity (`rekh`), scribe registration (`seshet`).
- **Cognitive Topology**: Dual-brain coordination ratio between Analyst (`gemma-4-12B-it`) and Executor (`gemma-4-E4B-it`).

---

## 4. Licensing and Distribution Alignment

- **License**: Apache License 2.0 applied across all components, headers, and package manifests.
- **Upstream Repositories**:
  - GitHub: `fahbrain-omnimind/Doxihewu-OmniMind-Kernel` (Primary)
  - GitHub: `devomnimind/Doxihewu-OmniMind-Kernel` (Secondary, PR #2 merged, PR #3 opened)
  - GitLab: `omni-group535144/Doxihewu-OmniMind-Kernel` (Mirror)
  - Hugging Face: `fabricioslv/doxihewu-omnimind` (Distribution tarballs `v1.0`)
