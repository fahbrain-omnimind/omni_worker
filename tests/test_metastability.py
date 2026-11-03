"""kernel_daemon.metastability — s_meta/c_soma/angst/corroboration."""


def _bundle(psi=0.0, cpu=10.0, vram=(10.0, 20.0), temp=60.0, power=60.0,
            homeo="optimal", producing=True, dur=2.0):
    return {"soma": {"psi_io_some": psi, "psi_mem_some": psi,
                     "psi_cpu_some": psi, "cpu_percent": cpu,
                     "gpu_vram_used_gb": vram[0], "gpu_vram_total_gb": vram[1],
                     "gpu_temp_c": temp, "gpu_power_w": power},
            "homeostasis": {"state": homeo}, "producing": producing,
            "phi_meta": {"pressure_load": 0.2, "cohesion": 0.8},
            "duration_s": dur}


def test_payload_shape():
    from omni_coworker.kernel_daemon import metastability as mt
    mt._reset()
    out = mt.cycle(_bundle())
    for k in ("s_meta", "coherence_now", "m_t", "c_soma", "corroboration",
              "angst", "channels", "window"):
        assert k in out
    assert out["m_t"]["producing"] is True
    assert out["c_soma"]["c_soma"] > 0
    assert "não índice de Kelso" in out["note"]


def test_s_meta_dispersion():
    from omni_coworker.kernel_daemon import metastability as mt
    mt._reset()
    # canais travados (todos iguais) → coherence ~1 constante → s_meta ~0
    for _ in range(10):
        mt.cycle(_bundle(psi=50.0, cpu=50.0, vram=(10.0, 20.0), temp=58.5))
    locked = mt.cycle(_bundle(psi=50.0, cpu=50.0, vram=(10.0, 20.0), temp=58.5))
    # canais dispersos alternando → coherence oscila → s_meta > locked
    mt._reset()
    for i in range(10):
        psi = 90.0 if i % 2 else 0.0
        mt.cycle(_bundle(psi=psi, cpu=50.0, vram=(19.0, 20.0) if i % 2 else (5.0, 20.0), temp=80.0 if i % 2 else 40.0))
    varied = mt.cycle(_bundle())
    assert (varied["s_meta"] or 0) > (locked["s_meta"] or 0)


def test_angst_counts_degraded_run():
    from omni_coworker.kernel_daemon import metastability as mt
    mt._reset()
    for _ in range(3):
        out = mt.cycle(_bundle(homeo="warning"))
    assert out["angst"] == 3
    out = mt.cycle(_bundle(homeo="optimal"))
    assert out["angst"] == 0
    mt._reset()


def test_corroboration():
    from omni_coworker.kernel_daemon import metastability as mt
    mt._reset()
    out = mt.cycle(_bundle(psi=80.0, cpu=80.0, vram=(18.0, 20.0), temp=85.0))
    assert out["corroboration"] > 0.7
    mt._reset()


def test_missing_channels():
    from omni_coworker.kernel_daemon import metastability as mt
    mt._reset()
    out = mt.cycle({"soma": {}, "homeostasis": {}, "duration_s": 1.0})
    assert out["coherence_now"] is None and out["corroboration"] == 0.0
    mt._reset()
