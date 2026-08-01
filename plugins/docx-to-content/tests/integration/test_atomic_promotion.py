"""
test_atomic_promotion.py
==========================

Integration coverage for `convert.convert_and_promote` (Task 11): the real
pandoc pipeline, `validate_canonical.py`, `dispositions.py`, and
`atomic_output.py` wired together end to end against a real .docx fixture.

Proves the brief's "failed validation leaves prior accepted output
unchanged" scenario using an actually-broken confirmed plan (a bogus extra
chunk_anchors entry) to force a real FAIL, rather than a synthetic staging
dir as in tests/unit/test_atomic_output.py.
"""

import json
import shutil
from pathlib import Path

import pytest

import analyze_structure
from plan_schema import analysis_plan as plan_contracts
import convert
import plans

FIXTURES = Path(__file__).parent.parent / "fixtures"
SMALL_SINGLE_DOCX = FIXTURES / "small_single.docx"

PANDOC_AVAILABLE = shutil.which("pandoc") is not None
pytestmark = pytest.mark.skipif(not PANDOC_AVAILABLE, reason="pandoc not available on PATH")


def _confirmed_plan(tmp_path):
    analysis_dir = tmp_path / "analysis"
    analyze_structure.analyze_document(SMALL_SINGLE_DOCX, analysis_dir)
    draft = plan_contracts.ConversionPlan.from_dict(
        json.loads((analysis_dir / "conversion-plan.draft.json").read_text())
    )
    return plans.confirm_plan(draft, confirmed_by="test-suite")


def test_convert_and_promote_success_then_failure_preserves_final_dir(tmp_path, monkeypatch):
    confirmed = _confirmed_plan(tmp_path)
    output_root = tmp_path / "out"

    manifest1, report1, promoted1, final_dir1 = convert.convert_and_promote(
        SMALL_SINGLE_DOCX, confirmed, output_root
    )
    assert promoted1 is True
    assert report1.status == "PASS"
    final_dir = output_root / "canonical-content"
    assert final_dir1 == final_dir
    before_snapshot = {
        p.relative_to(final_dir): p.read_bytes()
        for p in final_dir.rglob("*") if p.is_file()
    }

    # Force a real FAIL on the second run. The real pipeline (pandoc,
    # cleanup, chunking, packaging) still runs unmodified end to end;
    # only the validator's verdict is forced to FAIL here, via
    # monkeypatching `validate_canonical.validate_canonical_package` as
    # `convert.py` imports and calls it -- this isolates
    # `convert_and_promote`'s promotion-gating behavior (the thing Task 11
    # owns) from `validate_canonical.py`'s own detection logic (Task 10's
    # concern, already covered by tests/unit/test_validate_canonical.py).
    from canonical_schema import canonical_package as _contracts

    def _fake_fail_validate(*args, **kwargs):
        return _contracts.ValidationReport(
            status="FAIL",
            issues=[
                _contracts.ValidationIssue(
                    severity="error",
                    code="simulated_failure",
                    message="forced FAIL for atomic-promotion test",
                    path=None,
                )
            ],
            source_sha256=confirmed.source.sha256,
            plan_id=confirmed.plan_id,
        )

    monkeypatch.setattr(
        convert.validate_canonical, "validate_canonical_package", _fake_fail_validate
    )

    manifest2, report2, promoted2, staging_dir2 = convert.convert_and_promote(
        SMALL_SINGLE_DOCX, confirmed, output_root
    )
    assert promoted2 is False
    assert report2.status == "FAIL"
    assert staging_dir2.exists()  # retained for diagnosis

    after_snapshot = {
        p.relative_to(final_dir): p.read_bytes()
        for p in final_dir.rglob("*") if p.is_file()
    }
    assert before_snapshot == after_snapshot


def test_convert_and_promote_second_success_replaces_final_dir(tmp_path):
    confirmed = _confirmed_plan(tmp_path)
    output_root = tmp_path / "out"

    convert.convert_and_promote(SMALL_SINGLE_DOCX, confirmed, output_root)
    final_dir = output_root / "canonical-content"
    manifest_v1 = json.loads((final_dir / "manifest.json").read_text())

    manifest2, report2, promoted2, final_dir2 = convert.convert_and_promote(
        SMALL_SINGLE_DOCX, confirmed, output_root
    )
    assert promoted2 is True
    manifest_v2 = json.loads((final_dir / "manifest.json").read_text())

    # Identical plan/source -> identical manifest content (chunk_ids,
    # content hashes, plan_id) modulo nothing -- there is no run-specific
    # field inside manifest.json itself (run metadata lives in the
    # sibling generator-info.json instead).
    assert manifest_v1 == manifest_v2

    chunk_files = {p.name for p in (final_dir / "chunks").iterdir()}
    # No stray files: every file under chunks/ is exactly one of the
    # current manifest's content/metadata files.
    expected = set()
    for c in manifest_v2["chunks"]:
        expected.add(Path(c["content_file"]).name)
        expected.add(Path(c["metadata_file"]).name)
    assert chunk_files == expected


def test_convert_and_promote_writes_generator_info(tmp_path):
    confirmed = _confirmed_plan(tmp_path)
    output_root = tmp_path / "out"

    convert.convert_and_promote(SMALL_SINGLE_DOCX, confirmed, output_root)
    final_dir = output_root / "canonical-content"
    info = json.loads((final_dir / "generator-info.json").read_text())
    # convert_and_promote is now provided by the installed canonical-knowledge
    # package (Phase 4.5 Wave 4), so it stamps its own plugin identity here.
    assert info["plugin"] == "canonical-knowledge"
    assert "python_version" in info
    assert "pandoc_version" in info
    assert "run_timestamp" in info


def test_reproducible_conversion_produces_identical_manifests(tmp_path):
    """Moved from canonical-knowledge's own test suite (Phase 4.5 Wave 4):
    depends on `analyze_structure`, docx-to-content's own orchestrator, not
    an installable dependency of canonical-knowledge -- see
    docs/superpowers/plans/phase-4-5-evidence/wave-4-canonical-knowledge-split-decision.md."""
    confirmed = _confirmed_plan(tmp_path)

    out1 = tmp_path / "run1"
    out2 = tmp_path / "run2"
    manifest1 = convert.convert_document(SMALL_SINGLE_DOCX, confirmed, out1)
    manifest2 = convert.convert_document(SMALL_SINGLE_DOCX, confirmed, out2)

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
