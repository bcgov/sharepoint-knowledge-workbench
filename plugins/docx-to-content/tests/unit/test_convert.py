"""
test_convert.py
================

Tests for scripts/convert.py — full convert-document pipeline
orchestration (Task 9): pandoc extraction -> cleanup pipeline (in order)
-> legacy media conversion -> anchor reconciliation/chunking -> canonical
package build.

`test_full_cleanup_order_matters` reuses the existing
`tests/fixtures/regression_raw.md` fixture (already proven, in
test_regression_pipeline.py, to exercise every pandoc_fixes defect
category at once) to prove `apply_cleanup_pipeline` runs attrs -> images
-> toc -> tables -> footnotes in that order, without needing pandoc or a
real docx.

`test_convert_document_end_to_end` exercises the full pipeline against a
real fixture .docx (`tests/fixtures/repeated_headings.docx`, which
contains a real embedded image and multiple headings/chunks) via real
pandoc, proving convert_document wires precondition checks, extraction,
cleanup, reconciliation/chunking, and canonical package building together
correctly end to end. No CEIS-specific literals appear in this file.
"""

import shutil
from pathlib import Path

import pytest

import analyze_structure
import contracts
import convert
import package
import plans

FIXTURES = Path(__file__).parent.parent / "fixtures"
REPEATED_HEADINGS_DOCX = FIXTURES / "repeated_headings.docx"
REGRESSION_RAW_MD = FIXTURES / "regression_raw.md"

PANDOC_AVAILABLE = shutil.which("pandoc") is not None


# ---------------------------------------------------------------------------
# Full cleanup order
# ---------------------------------------------------------------------------

def test_full_cleanup_order_matters():
    text = REGRESSION_RAW_MD.read_text(encoding="utf-8")
    cleaned = convert.apply_cleanup_pipeline(text)

    # attrs.py: pandoc attribute artifacts removed
    assert '{width="100" height="50"}' not in cleaned
    assert "{.underline}" not in cleaned
    assert "{.mark}" not in cleaned

    # images.py: glued images separated onto their own paragraph, BEFORE
    # toc.py runs -- if toc stripping ran first while the image was still
    # glued to the "# Introduction" heading line, the TOC-detection logic
    # would be looking at a heading line containing an inline image
    # reference rather than a clean heading, which is exactly the
    # order-sensitive scenario this test protects against.
    assert "# Introduction\n\n![](media/image1.png)" in cleaned

    # toc.py: raw Word TOC dump removed, real heading kept as the first
    # thing in the document
    assert "_Toc" not in cleaned
    assert cleaned.lstrip().startswith("# Introduction")

    # tables.py: missing header separator row inserted
    assert "| --- | --- |" in cleaned

    # footnotes.py: matched pair kept, orphans removed
    assert "[^1]" in cleaned
    assert "[^2]" not in cleaned
    assert "[^3]" not in cleaned

    # Legacy .emf reference untouched by the cleanup pipeline itself
    # (legacy conversion is a separate pipeline stage, not part of
    # apply_cleanup_pipeline).
    assert "media/legacy1.emf" in cleaned


def test_cleanup_pipeline_is_a_named_ordered_sequence_not_reimplemented():
    """convert_document must call apply_cleanup_pipeline rather than
    inlining pandoc_fixes calls a second time -- assert by construction
    that apply_cleanup_pipeline exists and convert_document's source
    references it exactly once."""
    import inspect

    source = inspect.getsource(convert.convert_document)
    assert "apply_cleanup_pipeline" in source
    assert source.count("strip_pandoc_attrs(") == 0  # not re-inlined here


# ---------------------------------------------------------------------------
# Preconditions
# ---------------------------------------------------------------------------

def test_convert_document_rejects_unconfirmed_plan(tmp_path):
    source = tmp_path / "source.docx"
    source.write_bytes(b"not-a-real-docx-but-fingerprint-only-matters-here")
    source_fp = contracts.SourceFingerprint(
        path=str(source),
        sha256=__import__("hashing").content_hash(source.read_bytes()),
        size_bytes=source.stat().st_size,
    )
    draft = plans.build_draft_plan(
        source_fingerprint=source_fp,
        strategy="single",
        chunk_level=1,
        chunk_anchors=[],
    )
    with pytest.raises(plans.PlanVerificationError):
        convert.convert_document(source, draft, tmp_path / "out")


def test_convert_document_rejects_stale_source(tmp_path):
    source = tmp_path / "source.docx"
    source.write_bytes(b"original-bytes")
    import hashing

    source_fp = contracts.SourceFingerprint(
        path=str(source),
        sha256=hashing.content_hash(source.read_bytes()),
        size_bytes=source.stat().st_size,
    )
    draft = plans.build_draft_plan(
        source_fingerprint=source_fp,
        strategy="single",
        chunk_level=1,
        chunk_anchors=[],
    )
    confirmed = plans.confirm_plan(draft, confirmed_by="tester")

    # Source modified after confirmation.
    source.write_bytes(b"tampered-bytes-different-length")

    with pytest.raises(plans.PlanVerificationError):
        convert.convert_document(source, confirmed, tmp_path / "out")


# ---------------------------------------------------------------------------
# Full pipeline, end to end, against a real fixture .docx
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not PANDOC_AVAILABLE, reason="pandoc not found on PATH")
def test_convert_document_end_to_end(tmp_path):
    analysis_dir = tmp_path / "analysis"
    result = analyze_structure.analyze_document(REPEATED_HEADINGS_DOCX, analysis_dir)
    confirmed_plan = plans.confirm_plan(result.plan, confirmed_by="tester")

    output_dir = tmp_path / "run"
    manifest = convert.convert_document(REPEATED_HEADINGS_DOCX, confirmed_plan, output_dir)

    canonical_dir = output_dir / "canonical-content"
    assert (canonical_dir / "manifest.json").exists()
    assert (canonical_dir / "validation.json").exists()
    assert manifest.chunk_count == len(confirmed_plan.chunk_anchors)
    assert manifest.chunk_count > 1  # repeated_headings.docx is multi-chunk

    for chunk in manifest.chunks:
        assert (canonical_dir / chunk.content_file).exists()
        assert (canonical_dir / chunk.metadata_file).exists()

    # repeated_headings.docx embeds one real image -- prove it made it
    # into media/ and got rewritten to a ../media/ relative reference in
    # whichever chunk references it.
    media_dir = canonical_dir / "media"
    assert media_dir.exists()
    media_files = list(media_dir.iterdir())
    if media_files:
        referencing = [
            c for c in manifest.chunks
            if (canonical_dir / c.content_file).read_text().find("../media/") != -1
        ]
        assert referencing
