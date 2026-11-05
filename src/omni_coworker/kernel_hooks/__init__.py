"""Kernel hooks for Rust crates.

English: Optional bindings to compiled Rust kernel modules.
pt-BR: Bindings opcionais para módulos de kernel Rust compilados.
"""

from __future__ import annotations

try:
    import omnimind_kernel_compute  # type: ignore
    KERNEL_AVAILABLE = True
except Exception:  # noqa: BLE001
    omnimind_kernel_compute = None  # type: ignore
    KERNEL_AVAILABLE = False

try:
    import omnimind_freud10d  # type: ignore
    FREUD_AVAILABLE = True
except Exception:  # noqa: BLE001
    omnimind_freud10d = None  # type: ignore
    FREUD_AVAILABLE = False

try:
    import omnimind_metrics  # type: ignore
    METRICS_AVAILABLE = True
except Exception:  # noqa: BLE001
    omnimind_metrics = None  # type: ignore
    METRICS_AVAILABLE = False

__all__ = [
    "FREUD_AVAILABLE",
    "KERNEL_AVAILABLE",
    "METRICS_AVAILABLE",
    "omnimind_freud10d",
    "omnimind_kernel_compute",
    "omnimind_metrics",
]
