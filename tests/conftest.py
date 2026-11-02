"""Test bootstrap for omni_worker (standalone).

English: Adds src/ to sys.path so `omni_coworker` imports without install.
pt-BR: Adiciona src/ ao sys.path para importar `omni_coworker` sem instalar.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))