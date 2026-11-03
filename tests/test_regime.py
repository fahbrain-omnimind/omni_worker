"""Page-Hinkley regime shift detection — kernel_daemon.regime."""


def _bundle(cpu=10.0, temp=70.0, vram_used=10.0, vram_total=20.0,
            attractor=None, ts=1000.0):
    return {"ts": ts,
            "soma": {"cpu_percent": cpu, "gpu_temp_c": temp,
                     "gpu_vram_used_gb": vram_used,
                     "gpu_vram_total_gb": vram_total},
            "attractor": attractor or {}}


def test_step_change_fires():
    from omni_coworker.kernel_daemon import regime
    regime._reset()
    events = []
    # baseline: 20 ciclos estáveis
    for i in range(20):
        out = regime.cycle(_bundle(cpu=10.0, ts=1000.0 + i))
        events += out["events"]
    assert not events
    # step: cpu salta para 90
    fired = False
    for i in range(15):
        out = regime.cycle(_bundle(cpu=90.0, ts=2000.0 + i))
        events += out["events"]
        if out["events"]:
            fired = True
            ev = out["events"][0]
    assert fired
    assert ev["signal"] == "cpu_percent"
    assert ev["ph_stat"] > 0 and ev["mean_before"] < ev["value"]


def test_stationary_no_alarm():
    from omni_coworker.kernel_daemon import regime
    regime._reset()
    import math
    events = []
    for i in range(40):
        cpu = 20.0 + 2.0 * math.sin(i)  # oscilação pequena e reversível
        out = regime.cycle(_bundle(cpu=cpu, ts=3000.0 + i))
        events += out["events"]
    assert not events
    assert "cpu_percent" in out["tracked"]


def test_attractor_signal_tracked():
    from omni_coworker.kernel_daemon import regime
    regime._reset()
    att = {"m1": {"attractor_score": 0.2}}
    out = regime.cycle(_bundle(attractor=att, ts=4000.0))
    assert "attractor:m1" in out["tracked"]
    regime._reset()


def test_missing_channels_tolerated():
    from omni_coworker.kernel_daemon import regime
    regime._reset()
    out = regime.cycle({"ts": 1.0, "soma": {}, "attractor": {}})
    assert out["events"] == []
    regime._reset()
