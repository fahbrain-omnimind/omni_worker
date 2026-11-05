"""Tests for store.code_index persistence cache (hermetic, no model)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from omni_coworker.store import code_index as ci


def _write_store(d, rows, dim=8):
    df = pd.DataFrame(rows)
    df.to_parquet(d / "chunks.parquet", index=False)
    embs = np.random.rand(len(rows), dim).astype("float32")
    try:
        import faiss

        idx = faiss.IndexFlatIP(dim)
        idx.add(embs)
        faiss.write_index(idx, str(d / "code_index.faiss"))
    except Exception:  # noqa: BLE001
        np.save(d / "embeddings.npy", embs)


@pytest.fixture(autouse=True)
def _reset_cache():
    ci._INDEX, ci._ROWS, ci._LOADED_DIR = None, [], None
    yield
    ci._INDEX, ci._ROWS, ci._LOADED_DIR = None, [], None


def test_load_missing_dir_returns_false(tmp_path):
    assert ci._load(tmp_path) is False
    assert ci._INDEX is None


def test_load_then_inplace_rebuild_reloads(tmp_path):
    _write_store(tmp_path, [{"path": "a.py", "kind": "module", "name": "a", "text": "t1"}])
    assert ci._load(tmp_path) is True
    assert [r["name"] for r in ci._ROWS] == ["a"]

    # in-place rebuild: same dir, new parquet mtime + new rows
    import os
    import time

    new = [{"path": "b.py", "kind": "module", "name": "b", "text": "t2"},
           {"path": "c.py", "kind": "module", "name": "c", "text": "t3"}]
    _write_store(tmp_path, new)
    future = time.time() + 5
    os.utime(tmp_path / "chunks.parquet", (future, future))

    assert ci._load(tmp_path) is True
    assert [r["name"] for r in ci._ROWS] == ["b", "c"]


def test_load_caches_same_stamp(tmp_path):
    _write_store(tmp_path, [{"path": "a.py", "kind": "module", "name": "a", "text": "t1"}])
    assert ci._load(tmp_path) is True
    rows_obj = ci._ROWS
    assert ci._load(tmp_path) is True
    assert ci._ROWS is rows_obj  # no reload while stamp unchanged
