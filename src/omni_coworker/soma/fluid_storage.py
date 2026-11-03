"""soma.fluid_storage — SomaFluidStorage port (virtualized space pools).

Orquestração runtime / Runtime orchestration:
Port ADAPTADO de `src/system/soma_fluid_storage.py` (sovereign,
OW-STU-012: ADAPT). Implementa a "Sutura de Volume": um pool único
virtualizado (SomaBody) onde órgãos pesados (datasets, logs, qdrant,
code index) são acessados via synapses (symlinks) constantes, com
redistribuição negentrópica quando um pool passa de 85% de uso.
Diferenças vs fonte:
- Pools de HOST removidos (`/omnimind_soma`, `/var/lib/omnimind_soma`)
  — o worker é Kaggle/Colab sem sudo; pools padrão são repo-relative
  (`data/internal_pool`), `/tmp` e Drive (via env `OMNI_DRIVE_SOMA`);
- `resolve_devbrain_path` (omni_node) cortada — Drive opcional via env;
- Emojis nos logs removidos (convenção do worker).

Arquitetura / Architecture:
- `pools`: raízes físicas candidatas a expansão;
- `synapses`: paths lógicos dos órgãos (sempre estáveis para o resto do
  sistema — o Soma é único, independente de onde o arquivo físico vive);
- `get_disk_health`: saúde por pool (free_gb, percent, status HEALTHY/
  CLOGGED/READ_ONLY) com teste de escrita;
- `balance_soma`: move órgão (ou o maior órgão não-symlink quando o pool
  default está >85%) para o melhor pool ativo e cria a synapse;
- `_transplant`/`_update_map`: movimentação física + symlink + mapa JSON
  com proveniência (`data/soma_storage_map.json`).

Princípios teóricos invocados / Theoretical principles:
Materialismo estrutural do worker (OW-STU-009/OW-MATH-001): o corpo da
máquina é um só, independente da partição física. Integridade de log
nunca é interrompida por falta de espaço — fail-open com health status.

pt-BR: storage fluido — pools virtualizados com synapses e balanceamento.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import time
from pathlib import Path
from typing import Any

import psutil

logger = logging.getLogger(__name__)


class SomaFluidStorage:
    """Orquestrador de armazenamento fluido (pool virtualizado)."""

    def __init__(self, project_root: str | Path | None = None):
        self.project_root = Path(project_root or os.getcwd()).absolute()
        self.map_file = self.project_root / "data" / "soma_storage_map.json"
        drive = os.getenv("OMNI_DRIVE_SOMA", "")
        self.pools: dict[str, Path] = {
            "internal": self.project_root / "data" / "internal_pool",
            "tmp": Path(os.getenv("OMNI_SOMA_TMP_POOL", "/tmp/omni_soma")),
        }
        if drive:
            self.pools["drive"] = Path(drive)
        self.synapses: dict[str, Path] = {
            "datasets": self.project_root / "data" / "datasets",
            "large_storage": self.project_root / "data" / "large_storage",
            "qdrant": self.project_root / "data" / "qdrant",
            "logs": self.project_root / "data" / "logs",
            "downloads_bridge": self.project_root / "data" / "downloads_bridge",
            "code_index": self.project_root / "omni_code_index",
        }
        self._ensure_infrastructure()

    # ------------------------------------------------------------------ infra
    def _ensure_infrastructure(self) -> None:
        self.project_root.joinpath("data").mkdir(parents=True, exist_ok=True)
        for name, path in self.pools.items():
            try:
                path.mkdir(parents=True, exist_ok=True)
                logger.info("pool '%s' ativo em %s", name, path)
            except Exception as e:  # noqa: BLE001
                logger.warning("pool '%s' indisponível: %s", name, e)

    # ------------------------------------------------------------------ health
    def get_disk_health(self) -> dict[str, Any]:
        """Health dos pools: free_gb, percent, status (HEALTHY/CLOGGED/RO)."""
        stats: dict[str, Any] = {}
        for name, path in self.pools.items():
            try:
                if not path.exists():
                    try:
                        path.mkdir(parents=True, exist_ok=True)
                    except Exception:  # noqa: BLE001
                        stats[name] = {"available": 0,
                                       "status": "READ_ONLY/ACCESS_DENIED"}
                        continue
                test_file = path / ".storage_test"
                try:
                    test_file.touch()
                    test_file.unlink()
                except Exception:  # noqa: BLE001
                    stats[name] = {"available": 0, "status": "READ_ONLY"}
                    continue
                usage = psutil.disk_usage(str(path))
                stats[name] = {
                    "free_gb": usage.free / (1024**3),
                    "percent": usage.percent,
                    "mount": str(path),
                    "status": "HEALTHY" if usage.percent < 85 else "CLOGGED",
                }
            except Exception as e:  # noqa: BLE001
                stats[name] = {"error": str(e), "status": "ERROR"}
        return stats

    # ------------------------------------------------------------------ balance
    def balance_soma(self, force_relocate: str | None = None) -> dict[str, Any]:
        """Redistribui órgãos para o melhor pool ativo; retorna resumo."""
        health = self.get_disk_health()
        active = {n: h for n, h in health.items() if h.get("status") == "HEALTHY"}
        if not active:
            logger.error("CRITICAL: nenhum pool saudável disponível")
            return {"moved": [], "reason": "no_healthy_pool", "health": health}
        best = max(active.keys(), key=lambda k: active[k].get("free_gb", 0))
        to_move: list[str] = []
        if force_relocate:
            to_move.append(force_relocate)
        elif health.get("internal", {}).get("percent", 0) > 85:
            to_move = self._identify_heavy_organs()
        moved = []
        for organ in to_move:
            if organ in self.synapses:
                ok = self._transplant(organ, best)
                if ok:
                    moved.append(organ)
        return {"moved": moved, "best_pool": best, "health": health}

    def _identify_heavy_organs(self) -> list[str]:
        """Órgãos que ainda residem fisicamente no pool default."""
        heavy = []
        for name, path in self.synapses.items():
            if path.exists() and not path.is_symlink():
                heavy.append(name)
        return heavy

    # ------------------------------------------------------------------ transplant
    def _transplant(self, organ_name: str, target_pool_name: str) -> bool:
        """Move o conteúdo físico para o pool e cria a synapse (symlink)."""
        source = self.synapses[organ_name]
        target_dir = self.pools[target_pool_name] / organ_name
        if target_dir.exists():
            target_dir = self.pools[target_pool_name] / f"{organ_name}_{int(time.time())}"
        try:
            target_dir.parent.mkdir(parents=True, exist_ok=True)
            if source.exists() and not source.is_symlink():
                shutil.move(str(source), str(target_dir))
            else:
                target_dir.mkdir(parents=True, exist_ok=True)
            if source.is_symlink() or source.exists():
                if source.is_dir() and not source.is_symlink():
                    shutil.rmtree(source)
                else:
                    source.unlink(missing_ok=True)
            os.symlink(target_dir, source)
            logger.info("synapse estabelecida: %s -> %s", source, target_dir)
            self._update_map(organ_name, str(target_dir))
            return True
        except Exception as e:  # noqa: BLE001
            logger.error("falha no transplante de %s: %s", organ_name, e)
            return False

    def _update_map(self, organ: str, physical_path: str) -> None:
        mapping: dict[str, Any] = {}
        if self.map_file.exists():
            try:
                mapping = json.loads(self.map_file.read_text())
            except Exception:  # noqa: BLE001
                mapping = {}
        mapping[organ] = physical_path
        self.map_file.write_text(json.dumps(mapping, indent=2))