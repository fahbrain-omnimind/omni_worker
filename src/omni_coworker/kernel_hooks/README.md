# kernel_hooks/ — optional Rust (pyo3) hot-paths with Python fallbacks

English: `kernel_hooks` binds to the compiled Rust kernel crates
(`omnimind_*`, provenance `src.kernel.*` in the canonical omni_node
repo — 9 pyo3 crates). Every function degrades to a pure-Python
implementation (or `None`) when the crates are not installed, so the
package stays fully standalone.

pt-BR: `kernel_hooks` faz bind aos crates Rust compilados
(`omnimind_*`, proveniência `src.kernel.*` no repo canônico omni_node
— 9 crates pyo3). Toda função degrada para implementação Python pura
(ou `None`) quando os crates não estão instalados, mantendo o pacote
totalmente standalone.

## Files

| File | Role | Key API |
|---|---|---|
| `__init__.py` | Optional imports + flags | `KERNEL_AVAILABLE`, `FREUD_AVAILABLE`, `METRICS_AVAILABLE`; module refs `omnimind_kernel_compute`, `omnimind_freud10d`, `omnimind_metrics` (`None` when absent) |
| `compute.py` | Compute wrappers | `affect_state`, `maat_balance`, `shadow_phi`, `cosine_similarity`, `kernel_status` |

## Functions and fallbacks (`compute.py`)

| Function | Rust path | Python fallback |
|---|---|---|
| `affect_state(host_state)` | `omnimind_kernel_compute.compute_affect_vector_28d` → `{affective_vector_28d, vctr_six_params, metrics, dominant_*}` | `None` (no kernel → callers use the heuristic path) |
| `maat_balance(phi_anchor, psi, epsilon)` | `compute_maat_balance` | `clamp01((phi + psi + (1 - epsilon)) / 3)` |
| `shadow_phi(total_processes, …8 factors)` | `calculate_shadow_phi` | `log1p(total_processes) * structural_factor`, clamped ≥ 0 |
| `cosine_similarity(a, b)` | `omnimind_metrics.cosine_similarity` | pure-Python dot/norm |
| `kernel_status()` | — | `{"kernel_compute", "freud10d", "metrics"}` availability flags |

Note: `omnimind_freud10d` is imported and flagged but currently has no
wrapper in `compute.py` — reserved for future hot-paths.

## Consumers

- `soul/api.py::_compute_state` — when `affect_state()` returns a
  kernel result, `/soul/state` maps `vctr_six_params`
  (`magnitude→phi`, `direction→psi`, `recalque→sigma`,
  `dominant_affect_score→epsilon`, `dominant_affect_token`) and marks
  `"kernel": true`; otherwise the soma-derived heuristic runs.
- `app.py` — `GET /kernel/status` → `kernel_status()`.
- `cli.py doctor` — reports each module as `available`/`unavailable`.

## Installation & fallback behavior

- The `omnimind_*` wheels come from the canonical omni_node build
  (pyo3/maturin); they are **not** pip dependencies of this package.
  `pip install -e .[kernel]` installs the *vector* stack
  (faiss/sentence-transformers/pandas/pyarrow), not the Rust crates.
- Import failures are caught per-module in `__init__.py`; call-site
  errors are caught per-call in `compute.py` — a broken crate never
  crashes the package, it just loses the hot path.
