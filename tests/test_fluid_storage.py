"""SomaFluidStorage port — virtualized pools with synapses/balance."""
from pathlib import Path

from omni_coworker.soma.fluid_storage import SomaFluidStorage


def test_pools_and_synapses_created(tmp_path):
    s = SomaFluidStorage(project_root=tmp_path)
    assert s.pools["internal"] == tmp_path / "data" / "internal_pool"
    assert s.pools["internal"].is_dir()
    assert s.synapses["code_index"] == tmp_path / "omni_code_index"
    assert s.synapses["logs"] == tmp_path / "data" / "logs"


def test_disk_health_healthy_status(tmp_path):
    s = SomaFluidStorage(project_root=tmp_path)
    h = s.get_disk_health()
    assert "internal" in h
    assert h["internal"]["status"] in ("HEALTHY", "CLOGGED")
    assert h["internal"]["free_gb"] > 0


def test_balance_creates_synapse_for_heavy_organ(tmp_path):
    s = SomaFluidStorage(project_root=tmp_path)
    # cria conteúdo físico no órgão logs (não é symlink ainda)
    logs = s.synapses["logs"]
    logs.mkdir(parents=True, exist_ok=True)
    (logs / "x.log").write_text("data")
    res = s.balance_soma(force_relocate="logs")
    assert res["moved"] == ["logs"]
    assert logs.is_symlink()
    assert s.map_file.exists()
    assert s.synapses["logs"].is_symlink()


def test_balance_no_healthy_pool_fail_open(tmp_path):
    s = SomaFluidStorage(project_root=tmp_path)
    # aponta todos os pools para caminho inacessível
    s.pools = {"internal": Path("/proc/1/nonexistent_pool")}
    res = s.balance_soma()
    assert res["moved"] == []
    assert res["reason"] == "no_healthy_pool"


def test_transplant_keeps_organs_readable_through_synapse(tmp_path):
    s = SomaFluidStorage(project_root=tmp_path)
    datasets = s.synapses["datasets"]
    datasets.mkdir(parents=True, exist_ok=True)
    (datasets / "a.parquet").write_text("x")
    s.balance_soma(force_relocate="datasets")
    # o path lógico continua funcionando (Soma é único)
    assert (s.synapses["datasets"] / "a.parquet").read_text() == "x"