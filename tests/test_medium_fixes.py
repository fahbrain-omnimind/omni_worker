"""Medium-priority fixes: manifest hash, base_url env, external unload."""



def test_manifest_hash_covers_full_file(tmp_path, monkeypatch):
    """Change past the 1MB mark must alter the manifest hash."""
    monkeypatch.setenv("OMNI_STATE_DIR", str(tmp_path))
    from omni_coworker.store import state_guard

    big = tmp_path / "big.bin"
    big.write_bytes(b"a" * 1_500_000)
    h1 = state_guard._manifest_hash()
    with big.open("r+b") as f:
        f.seek(1_400_000)
        f.write(b"CHANGED_TAIL")
    h2 = state_guard._manifest_hash()
    assert h1 != h2


def test_sanitized_env_base_url_configurable(monkeypatch):
    from omni_coworker.agents import external_cli_agent

    monkeypatch.delenv("OMNI_BRAIN_BASE_URL", raising=False)
    assert external_cli_agent.sanitized_env()["OPENAI_BASE_URL"] == \
        "http://127.0.0.1:8098"
    monkeypatch.setenv("OMNI_BRAIN_BASE_URL", "http://10.0.0.5:9000")
    assert external_cli_agent.sanitized_env()["OPENAI_BASE_URL"] == \
        "http://10.0.0.5:9000"


def test_sanitized_env_still_strips_tokens(monkeypatch):
    from omni_coworker.agents import external_cli_agent

    monkeypatch.setenv("OPENAI_API_KEY", "sk-secret")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "ak-secret")
    env = external_cli_agent.sanitized_env()
    assert "OPENAI_API_KEY" not in env and "ANTHROPIC_API_KEY" not in env


def test_swap_marks_unloaded_when_brain_unreachable(monkeypatch):
    """acts=None (brain down) -> state executor=unloaded, event recorded."""
    monkeypatch.setenv("OMNI_SWAP_EVICT_THRESHOLD", "0.99")
    from omni_coworker.orchestration import swap_scheduler as ss

    monkeypatch.setattr(ss, "_executor_activations", lambda: None)
    monkeypatch.setattr(ss, "_vram_ratio", lambda: 0.5)
    sched = ss.SwapScheduler()
    st = sched.tick()
    assert st["executor"] == "unloaded"
    assert any(e.get("evt") == "externally_unloaded" for e in st["events"])


def test_swap_loaded_when_brain_alive(monkeypatch):
    monkeypatch.setenv("OMNI_SWAP_EVICT_THRESHOLD", "0.99")
    from omni_coworker.orchestration import swap_scheduler as ss

    monkeypatch.setattr(ss, "_executor_activations", lambda: 3)
    monkeypatch.setattr(ss, "_vram_ratio", lambda: 0.5)
    sched = ss.SwapScheduler()
    st = sched.tick()
    assert st["executor"] == "loaded"
