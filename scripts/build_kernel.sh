#!/usr/bin/env bash
# Build the optional Rust kernel modules (omnimind_*.so) for omni-agent-coworker.
#
# English: The kernel crates are NOT pip-installable (no Python packaging
# upstream). This script builds them with cargo and installs the cdylib
# .so files into the active interpreter's site-packages so
# `import omnimind_kernel_compute / omnimind_metrics / omnimind_freud10d`
# resolve (kernel_hooks auto-detects them; package works without them).
#
# pt-BR: Os crates do kernel NÃO são instaláveis via pip (sem packaging
# Python upstream). Este script compila com cargo e instala os .so cdylib
# no site-packages do interpretador ativo para que os imports
# omnimind_* resolvam (kernel_hooks auto-detecta; o pacote funciona sem).
#
# Source priority / prioridade de fonte:
#   1. $OMNI_KERNEL_SRC (dir contendo os crates, ex.: omni_node/src/kernel)
#   2. /content/omni_node/src/kernel (repo canônico local, quando montado)
#   3. clone --depth 1 do repo público Doxihewu-OmniMind-Kernel -> /tmp
#
# Requires / requer: rustup/cargo stable >=1.85, python dev headers.
# License note / nota de licença: os crates são CC-BY-NC-ND-4.0 — build
# local opcional; nada de código kernel é redistribuído no pacote.

set -euo pipefail

CRATES="${OMNI_KERNEL_CRATES:-kernel_compute metrics freud10d}"
SRC="${OMNI_KERNEL_SRC:-}"
PYBIN="${PYTHON:-python3}"
# CARGO_TARGET_DIR redireciona os artefatos de build para fora do repo
# fonte (omni_node é projeto separado / read-only no fluxo do worker).
TARGET_DIR="${CARGO_TARGET_DIR:-}"

if [ -z "$SRC" ]; then
  if [ -d "/content/omni_node/src/kernel" ]; then
    SRC=/content/omni_node/src/kernel
  else
    CLONE=/tmp/doxi_kernel
    if [ ! -d "$CLONE" ]; then
      git clone --depth 1 https://github.com/devomnimind/Doxihewu-OmniMind-Kernel.git "$CLONE"
    fi
    SRC="$CLONE/src/kernel"
  fi
fi

SITE=$($PYBIN -c "import site; print(site.getsitepackages()[0])")
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1

for c in $CRATES; do
  echo "==> build $c"
  (cd "$SRC/$c" && cargo build --release)
  RELEASE_DIR="${TARGET_DIR:-$SRC/$c/target}/release"
  cp "$RELEASE_DIR/libomnimind_${c}.so" "$SITE/omnimind_${c}.so"
done

echo "==> installed crates: $CRATES -> $SITE"
$PYBIN - <<'EOF'
try:
    import omnimind_kernel_compute, omnimind_metrics, omnimind_freud10d
    print("ok: omnimind_* modules import")
except Exception as e:
    print("import check failed:", e)
EOF
