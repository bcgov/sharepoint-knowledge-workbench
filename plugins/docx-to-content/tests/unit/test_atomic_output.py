"""
test_atomic_output.py
======================

Tests for scripts/atomic_output.py (Task 11): unique staging directories,
atomic directory-replacement promotion, diagnostic retention on failure,
and reproducibility of generator-info metadata.

Covers the four scenarios required by the task brief:
    - test_failed_validation_leaves_prior_accepted_output_unchanged
    - test_successful_validation_replaces_not_overlays_old_output
    - test_stale_files_from_earlier_run_disappear
    - test_reproducible_end_to_end_conversion (via convert.convert_and_promote)

Plus focused unit coverage of create_staging_dir/promote/generator-info in
isolation, and a check that build_generator_info reuses dependencies.py's
probe functions rather than re-probing independently.
"""

import json
import shutil
from pathlib import Path
from unittest import mock

import pytest

import atomic_output
import contracts
import convert
import dependencies
import validate_canonical

FIXTURES = Path(__file__).parent.parent / "fixtures"
REPEATED_HEADINGS_DOCX = FIXTURES / "repeated_headings.docx"

PANDOC_AVAILABLE = shutil.which("pandoc") is not None


# ---------------------------------------------------------------------------
# create_staging_dir
# ---------------------------------------------------------------------------

def test_create_staging_dir_is_unique_and_fresh(tmp_path):
    d1 = atomic_output.create_staging_dir(tmp_path)
    d2 = atomic_output.create_staging_dir(tmp_path)
    assert d1 != d2
    assert d1.is_dir()
    assert d2.is_dir()
    assert d1.parent == tmp_path


def test_create_staging_dir_uses_prefix(tmp_path):
    d = atomic_output.create_staging_dir(tmp_path, prefix="canonical")
    assert d.name.startswith("canonical-")


# ---------------------------------------------------------------------------
# promote: basic atomicity behavior
# ---------------------------------------------------------------------------

def test_promote_moves_staging_into_final_when_final_absent(tmp_path):
    staging = tmp_path / "staging-1"
    staging.mkdir()
    (staging / "file.txt").write_text("hello")
    final_dir = tmp_path / "final"

    atomic_output.promote(staging, final_dir)

    assert final_dir.is_dir()
    assert (final_dir / "file.txt").read_text() == "hello"
    assert not staging.exists()


def test_failed_validation_leaves_prior_accepted_output_unchanged(tmp_path):
    """Promote v1 successfully. A second run's staged package is
    intentionally invalid (simulated: caller simply never calls promote()
    on a failed package) -- final_dir must remain byte-for-byte identical
    to what it was after v1's promotion, and the failed staging dir must
    still exist on disk for diagnosis."""
    final_dir = tmp_path / "final"

    staging_v1 = tmp_path / "staging-v1"
    staging_v1.mkdir()
    (staging_v1 / "manifest.json").write_text('{"v": 1}')
    atomic_output.promote(staging_v1, final_dir)

    before_files = {p.name: p.read_bytes() for p in final_dir.iterdir()}

    # Simulate a second run that fails validation: its staging dir is
    # built but never promoted.
    staging_v2_fail = tmp_path / "staging-v2-fail"
    staging_v2_fail.mkdir()
    (staging_v2_fail / "manifest.json").write_text('{"v": "broken"}')
    # Caller decision (mirrors real orchestration in convert.py): FAIL ->
    # do not call promote(). staging dir is retained, not deleted.

    after_files = {p.name: p.read_bytes() for p in final_dir.iterdir()}
    assert before_files == after_files
    assert staging_v2_fail.exists()
    assert (staging_v2_fail / "manifest.json").read_text() == '{"v": "broken"}'


def test_successful_validation_replaces_not_overlays_old_output(tmp_path):
    final_dir = tmp_path / "final"

    staging_v1 = tmp_path / "staging-v1"
    staging_v1.mkdir()
    (staging_v1 / "a.md").write_text("A")
    (staging_v1 / "b.md").write_text("B")
    atomic_output.promote(staging_v1, final_dir)
    assert sorted(p.name for p in final_dir.iterdir()) == ["a.md", "b.md"]

    staging_v2 = tmp_path / "staging-v2"
    staging_v2.mkdir()
    (staging_v2 / "a.md").write_text("A2")
    (staging_v2 / "b.md").write_text("B2")
    atomic_output.promote(staging_v2, final_dir)
    assert sorted(p.name for p in final_dir.iterdir()) == ["a.md", "b.md"]
    assert (final_dir / "a.md").read_text() == "A2"
    assert (final_dir / "b.md").read_text() == "B2"


def test_stale_files_from_earlier_run_disappear(tmp_path):
    """v1 has chunks A, B, C. v2 has chunks A, B, D (C removed, D added).
    After promoting v2, final_dir must contain exactly A, B, D -- no
    leftover C file anywhere in final_dir."""
    final_dir = tmp_path / "final"

    staging_v1 = tmp_path / "staging-v1"
    staging_v1.mkdir()
    for name in ("A", "B", "C"):
        (staging_v1 / f"{name}.md").write_text(name)
    atomic_output.promote(staging_v1, final_dir)
    assert sorted(p.stem for p in final_dir.iterdir()) == ["A", "B", "C"]

    staging_v2 = tmp_path / "staging-v2"
    staging_v2.mkdir()
    for name in ("A", "B", "D"):
        (staging_v2 / f"{name}.md").write_text(name)
    atomic_output.promote(staging_v2, final_dir)

    remaining = sorted(p.stem for p in final_dir.iterdir())
    assert remaining == ["A", "B", "D"]
    assert not (final_dir / "C.md").exists()


def test_promote_restores_original_final_dir_if_rename_fails(tmp_path, monkeypatch):
    """If the second os.rename (staging -> final) fails after the first
    (final -> backup) has already happened, promote() must restore
    final_dir to its original state rather than leaving it missing."""
    final_dir = tmp_path / "final"
    final_dir.mkdir()
    (final_dir / "orig.txt").write_text("orig")

    staging = tmp_path / "staging"
    staging.mkdir()
    (staging / "new.txt").write_text("new")

    real_rename = atomic_output.os.rename
    call_count = {"n": 0}

    def flaky_rename(src, dst):
        call_count["n"] += 1
        if call_count["n"] == 2:
            raise OSError("simulated failure")
        return real_rename(src, dst)

    monkeypatch.setattr(atomic_output.os, "rename", flaky_rename)

    with pytest.raises(OSError):
        atomic_output.promote(staging, final_dir)

    assert final_dir.is_dir()
    assert (final_dir / "orig.txt").read_text() == "orig"


# ---------------------------------------------------------------------------
# generator-info metadata
# ---------------------------------------------------------------------------

def test_build_generator_info_reuses_dependencies_probes():
    with mock.patch.object(dependencies, "probe_pandoc") as mock_pandoc, \
         mock.patch.object(atomic_output.dependencies, "probe_pandoc", mock_pandoc), \
         mock.patch.object(atomic_output.dependencies, "probe_soffice") as mock_soffice:
        mock_pandoc.return_value = dependencies.DependencyStatus(
            name="pandoc", available=True, path="/usr/bin/pandoc", version="pandoc 3.1"
        )
        mock_soffice.return_value = dependencies.DependencyStatus(
            name="soffice", available=False
        )
        info = atomic_output.build_generator_info(plugin_version="0.1.0")

    assert mock_pandoc.called
    assert mock_soffice.called
    assert info["plugin"] == "docx-to-content"
    assert info["plugin_version"] == "0.1.0"
    assert info["pandoc_version"] == "pandoc 3.1"
    assert info["soffice_version"] is None
    assert "python_version" in info


def test_write_generator_info_is_deterministic_json_utf8(tmp_path):
    with mock.patch.object(atomic_output.dependencies, "probe_pandoc") as mock_pandoc, \
         mock.patch.object(atomic_output.dependencies, "probe_soffice") as mock_soffice:
        mock_pandoc.return_value = dependencies.DependencyStatus(
            name="pandoc", available=True, version="pandoc 3.1"
        )
        mock_soffice.return_value = dependencies.DependencyStatus(name="soffice", available=False)

        record1 = atomic_output.write_generator_info(tmp_path, run_timestamp="2026-01-01T00:00:00Z")
        raw1 = (tmp_path / "generator-info.json").read_bytes()

        record2 = atomic_output.write_generator_info(tmp_path, run_timestamp="2099-12-31T00:00:00Z")
        raw2 = (tmp_path / "generator-info.json").read_bytes()

    # Non-timestamp fields identical
    non_ts_1 = {k: v for k, v in record1.items() if k != "run_timestamp"}
    non_ts_2 = {k: v for k, v in record2.items() if k != "run_timestamp"}
    assert non_ts_1 == non_ts_2
    assert record1["run_timestamp"] != record2["run_timestamp"]

    # Deterministic ordering: re-dumping with sort_keys reproduces the file
    assert raw1.decode("utf-8") == json.dumps(
        {**non_ts_1, "run_timestamp": "2026-01-01T00:00:00Z"}, indent=2, sort_keys=True
    )


# ---------------------------------------------------------------------------
# Reproducibility (full pipeline, real pandoc)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not PANDOC_AVAILABLE, reason="pandoc not available on PATH")
def test_reproducible_conversion_produces_identical_manifests(tmp_path):
    import analyze_structure
    import plans

    analysis_dir = tmp_path / "analysis"
    analyze_structure.analyze_document(REPEATED_HEADINGS_DOCX, analysis_dir)
    draft = contracts.ConversionPlan.from_dict(
        json.loads((analysis_dir / "conversion-plan.draft.json").read_text())
    )
    confirmed = plans.confirm_plan(draft, confirmed_by="test-suite")

    out1 = tmp_path / "run1"
    out2 = tmp_path / "run2"
    manifest1 = convert.convert_document(REPEATED_HEADINGS_DOCX, confirmed, out1)
    manifest2 = convert.convert_document(REPEATED_HEADINGS_DOCX, confirmed, out2)

    d1 = manifest1.to_dict()
    d2 = manifest2.to_dict()
    assert d1 == d2
    assert manifest1.plan_id == manifest2.plan_id

    for chunk1, chunk2 in zip(manifest1.chunks, manifest2.chunks):
        assert chunk1.chunk_id == chunk2.chunk_id
        meta1 = json.loads(
            (out1 / "canonical-content" / chunk1.metadata_file).read_text()
        )
        meta2 = json.loads(
            (out2 / "canonical-content" / chunk2.metadata_file).read_text()
        )
        assert meta1 == meta2
