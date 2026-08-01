import os

import pytest

from knowledge_workbench_runtime.atomic_output import create_staging_dir, promote


def test_create_staging_dir_creates_unique_directory(tmp_path):
    d1 = create_staging_dir(tmp_path)
    d2 = create_staging_dir(tmp_path)
    assert d1.exists() and d2.exists()
    assert d1 != d2


def test_create_staging_dir_never_overlays_existing_directory(tmp_path):
    d1 = create_staging_dir(tmp_path, prefix="staging")
    (d1 / "marker.txt").write_text("present")
    d2 = create_staging_dir(tmp_path, prefix="staging")
    # d2 must be a distinct, empty directory — never the same path as d1
    assert d2 != d1
    assert not (d2 / "marker.txt").exists()


def test_promote_moves_staging_content_into_final_dir(tmp_path):
    staging = create_staging_dir(tmp_path)
    (staging / "output.txt").write_text("hello")
    final_dir = tmp_path / "final"

    promote(staging, final_dir)

    assert (final_dir / "output.txt").read_text() == "hello"
    assert not staging.exists()


def test_promote_fully_replaces_existing_final_dir_not_merges(tmp_path):
    final_dir = tmp_path / "final"
    final_dir.mkdir()
    (final_dir / "old.txt").write_text("stale")

    staging = create_staging_dir(tmp_path)
    (staging / "new.txt").write_text("fresh")

    promote(staging, final_dir)

    assert (final_dir / "new.txt").read_text() == "fresh"
    assert not (final_dir / "old.txt").exists()


def test_promote_restores_final_dir_on_failure(tmp_path, monkeypatch):
    final_dir = tmp_path / "final"
    final_dir.mkdir()
    (final_dir / "old.txt").write_text("stale")

    staging = create_staging_dir(tmp_path)
    (staging / "new.txt").write_text("fresh")

    real_rename = os.rename
    call_count = {"n": 0}

    def flaky_rename(src, dst):
        call_count["n"] += 1
        # First call is the "back up existing final_dir" rename — let it succeed.
        # Second call is "promote staging into final_dir" — force it to fail.
        if call_count["n"] == 2:
            raise OSError("simulated cross-device rename failure")
        return real_rename(src, dst)

    monkeypatch.setattr(os, "rename", flaky_rename)

    with pytest.raises(OSError):
        promote(staging, final_dir)

    # final_dir must be restored to exactly its pre-call state
    assert (final_dir / "old.txt").read_text() == "stale"
    assert not (final_dir / "new.txt").exists()
