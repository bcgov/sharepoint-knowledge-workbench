"""
test_validate_canonical.py
============================

Tests for scripts/validate_canonical.py -- the canonical-package validator
(Task 10). Builds real staged packages via `package.build_canonical_package`
(Task 9), then mutates the on-disk package/plan to trigger each of the 20
required detections in spec Section 9 / the Task 10 brief, asserting the
resulting `ValidationReport` status and issue codes.

Fixture heading/product names are synthetic placeholders (e.g. "Widget
Setup", "Gadget Alpha").
"""

import json
from pathlib import Path

import pytest

from canonical_schema import analysis_plan as contracts
import hashing
import package
import validate_canonical as vc
from chunking import ChunkSlice, SlicedDocument
from identity_core import make_chunk_id
import plan_verification


def _anchor(path, occurrence=1, level=1):
    return contracts.StructuralAnchor(
        stable_key=make_chunk_id(path, occurrence),
        heading_text=path[-1],
        heading_level=level,
        occurrence=occurrence,
        source_heading_path=list(path),
    )


def _confirmed_plan(chunk_anchors, source_sha256="b" * 64, strategy="chunked"):
    source_fp = contracts.SourceFingerprint(
        path="sourcedocuments/widget.docx", sha256=source_sha256, size_bytes=123
    )
    plan = contracts.ConversionPlan(
        schema_version=contracts.CONVERSION_PLAN_SCHEMA_VERSION,
        plan_id="",
        source=source_fp,
        strategy=strategy,
        chunk_level=1,
        chunk_anchors=list(chunk_anchors),
        content_type="manual",
        template_profile="source-structure-v1",
        confirmation=contracts.Confirmation(
            status="confirmed", confirmed_by="tester", confirmed_at="2026-01-01T00:00:00Z"
        ),
    )
    plan.plan_id = plan_verification.compute_plan_id(plan)
    return plan


def _slice(anchor, content):
    return ChunkSlice(anchor=anchor, start_line=0, end_line=1, content=content)


def _build_simple_package(tmp_path):
    """Build a minimal, fully valid two-chunk canonical package. Returns
    (plan, output_dir, a1, a2)."""
    a1 = _anchor(["Widget Setup"])
    a2 = _anchor(["Widget Configuration"])
    plan = _confirmed_plan([a1, a2])
    sliced = SlicedDocument(
        preamble="",
        chunks=[
            _slice(a1, "# Widget Setup\n\nBody one.\n"),
            _slice(a2, "# Widget Configuration\n\nBody two.\n"),
        ],
    )
    raw_media_dir = tmp_path / "raw_media"
    raw_media_dir.mkdir()
    output_dir = tmp_path / "canonical-content"
    package.build_canonical_package(plan, sliced, raw_media_dir, output_dir)
    return plan, output_dir, a1, a2


def _codes(report, code=None):
    if code is None:
        return [i.code for i in report.issues]
    return [i for i in report.issues if i.code == code]


# ---------------------------------------------------------------------------
# PASS / WARN / FAIL semantics
# ---------------------------------------------------------------------------

def test_pass_on_a_clean_package_with_cleaned_markdown_supplied(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    cleaned = "# Widget Setup\n\nBody one.\n\n# Widget Configuration\n\nBody two.\n"
    report = vc.validate_canonical_package(
        output_dir, plan, cleaned_markdown_text=cleaned
    )
    assert report.status == "PASS", report.issues
    assert report.issues == []


def test_warn_when_cleaned_markdown_not_supplied(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    report = vc.validate_canonical_package(output_dir, plan)
    # For real producer-path packages (manifest.generator.plugin=="docx-to-content"),
    # omitting cleaned_markdown_text is now an ERROR per Task 7.
    assert report.status == "FAIL"
    assert any(i.code == "content_comparison_skipped" and i.severity == "error" for i in report.issues)


def test_fail_when_manifest_missing(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    (output_dir / "manifest.json").unlink()
    report = vc.validate_canonical_package(output_dir, plan)
    assert report.status == "FAIL"
    assert "manifest_missing" in _codes(report)


def test_report_carries_source_sha256_and_plan_id(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    report = vc.validate_canonical_package(output_dir, plan)
    assert report.source_sha256 == plan.source.sha256
    assert report.plan_id == plan.plan_id


# ---------------------------------------------------------------------------
# Malformed JSON / missing required fields / unsupported schema version
# ---------------------------------------------------------------------------

def test_fail_on_malformed_manifest_json(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    (output_dir / "manifest.json").write_text("{not valid json")
    report = vc.validate_canonical_package(output_dir, plan)
    assert report.status == "FAIL"
    assert "malformed_json" in _codes(report)


def test_fail_on_manifest_missing_required_field(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    data = json.loads((output_dir / "manifest.json").read_text())
    del data["chunk_count"]
    (output_dir / "manifest.json").write_text(json.dumps(data))
    report = vc.validate_canonical_package(output_dir, plan)
    assert report.status == "FAIL"
    assert "missing_required_field" in _codes(report)


def test_fail_on_unsupported_manifest_schema_version(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    data = json.loads((output_dir / "manifest.json").read_text())
    data["schema_version"] = "99.9"
    (output_dir / "manifest.json").write_text(json.dumps(data))
    report = vc.validate_canonical_package(output_dir, plan)
    assert report.status == "FAIL"
    assert "schema_version_unsupported" in _codes(report)


def test_fail_on_malformed_sidecar_json(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    meta_path = output_dir / "chunks" / f"{a1.stable_key}.meta.json"
    meta_path.write_text("{broken")
    report = vc.validate_canonical_package(output_dir, plan)
    assert report.status == "FAIL"
    assert "malformed_json" in _codes(report)


# ---------------------------------------------------------------------------
# Source / plan fingerprint mismatch
# ---------------------------------------------------------------------------

def test_fail_on_plan_fingerprint_mismatch_tampered_plan(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    tampered = contracts.ConversionPlan.from_dict(plan.to_dict())
    tampered.strategy = "single"  # mutate content without recomputing plan_id
    report = vc.validate_canonical_package(output_dir, tampered)
    assert report.status == "FAIL"
    assert "plan_fingerprint_mismatch" in _codes(report)


def test_fail_on_source_fingerprint_mismatch(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    source_file = tmp_path / "widget.docx"
    source_file.write_bytes(b"different bytes than the plan's recorded sha256")
    report = vc.validate_canonical_package(output_dir, plan, source_path=source_file)
    assert report.status == "FAIL"
    assert "source_fingerprint_mismatch" in _codes(report)


# ---------------------------------------------------------------------------
# Manifest chunk_count mismatch
# ---------------------------------------------------------------------------

def test_fail_on_chunk_count_mismatch(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    data = json.loads((output_dir / "manifest.json").read_text())
    data["chunk_count"] = 999
    (output_dir / "manifest.json").write_text(json.dumps(data))
    report = vc.validate_canonical_package(output_dir, plan)
    assert report.status == "FAIL"
    assert "chunk_count_mismatch" in _codes(report)


# ---------------------------------------------------------------------------
# Duplicate chunk IDs / content paths / metadata paths / source orders
# ---------------------------------------------------------------------------

def test_fail_on_duplicate_chunk_id(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    data = json.loads((output_dir / "manifest.json").read_text())
    data["chunks"][1]["chunk_id"] = data["chunks"][0]["chunk_id"]
    (output_dir / "manifest.json").write_text(json.dumps(data))
    report = vc.validate_canonical_package(output_dir, plan)
    assert report.status == "FAIL"
    assert "duplicate_chunk_id" in _codes(report)


def test_fail_on_duplicate_content_path(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    data = json.loads((output_dir / "manifest.json").read_text())
    data["chunks"][1]["content_file"] = data["chunks"][0]["content_file"]
    (output_dir / "manifest.json").write_text(json.dumps(data))
    report = vc.validate_canonical_package(output_dir, plan)
    assert "duplicate_content_path" in _codes(report)


def test_fail_on_duplicate_metadata_path(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    data = json.loads((output_dir / "manifest.json").read_text())
    data["chunks"][1]["metadata_file"] = data["chunks"][0]["metadata_file"]
    (output_dir / "manifest.json").write_text(json.dumps(data))
    report = vc.validate_canonical_package(output_dir, plan)
    assert "duplicate_metadata_path" in _codes(report)


def test_fail_on_duplicate_source_order(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    data = json.loads((output_dir / "manifest.json").read_text())
    data["chunks"][1]["source_order"] = data["chunks"][0]["source_order"]
    (output_dir / "manifest.json").write_text(json.dumps(data))
    report = vc.validate_canonical_package(output_dir, plan)
    assert "duplicate_source_order" in _codes(report)


# ---------------------------------------------------------------------------
# Missing expected chunks/sidecars, orphan chunks/sidecars/media
# ---------------------------------------------------------------------------

def test_fail_on_missing_chunk_content_file(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    (output_dir / "chunks" / f"{a1.stable_key}.md").unlink()
    report = vc.validate_canonical_package(output_dir, plan)
    assert report.status == "FAIL"
    assert "missing_chunk_file" in _codes(report)


def test_fail_on_missing_sidecar_file(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    (output_dir / "chunks" / f"{a1.stable_key}.meta.json").unlink()
    report = vc.validate_canonical_package(output_dir, plan)
    assert report.status == "FAIL"
    assert "missing_sidecar_file" in _codes(report)


def test_fail_on_orphan_chunk_file(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    (output_dir / "chunks" / "unknown-chunk.md").write_text("# Orphan\n")
    report = vc.validate_canonical_package(output_dir, plan)
    assert report.status == "FAIL"
    assert "orphan_chunk_file" in _codes(report)


def test_fail_on_orphan_sidecar_file(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    (output_dir / "chunks" / "unknown-chunk.meta.json").write_text("{}")
    report = vc.validate_canonical_package(output_dir, plan)
    assert report.status == "FAIL"
    assert "orphan_sidecar_file" in _codes(report)


def test_fail_on_orphan_media_file(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    (output_dir / "media").mkdir(exist_ok=True)
    (output_dir / "media" / "unreferenced.png").write_bytes(b"bytes")
    report = vc.validate_canonical_package(output_dir, plan)
    assert report.status == "FAIL"
    assert "orphan_media_file" in _codes(report)


# ---------------------------------------------------------------------------
# Mismatched IDs between manifest and sidecars
# ---------------------------------------------------------------------------

def test_fail_on_chunk_id_mismatch_between_manifest_and_sidecar(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    meta_path = output_dir / "chunks" / f"{a1.stable_key}.meta.json"
    meta = json.loads(meta_path.read_text())
    meta["chunk_id"] = "totally-different-id"
    meta_path.write_text(json.dumps(meta))
    report = vc.validate_canonical_package(output_dir, plan)
    assert report.status == "FAIL"
    assert "chunk_id_mismatch" in _codes(report)


# ---------------------------------------------------------------------------
# Mismatched content hashes
# ---------------------------------------------------------------------------

def test_fail_on_content_hash_mismatch(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    content_path = output_dir / "chunks" / f"{a1.stable_key}.md"
    content_path.write_text("# Widget Setup\n\nTampered body!\n")
    report = vc.validate_canonical_package(output_dir, plan)
    assert report.status == "FAIL"
    assert "content_hash_mismatch" in _codes(report)


def test_chunk_sidecar_plan_id_mismatch_is_detected(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    meta_path = output_dir / "chunks" / f"{a1.stable_key}.meta.json"
    meta_data = json.loads(meta_path.read_text())
    meta_data["plan_id"] = "sha256:" + "0" * 64
    meta_path.write_text(json.dumps(meta_data))

    report = vc.validate_canonical_package(output_dir, plan)

    assert report.status == "FAIL"
    assert any(i.code == "chunk_plan_id_mismatch" for i in report.issues)


def test_chunk_sidecar_source_sha256_mismatch_is_detected(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    meta_path = output_dir / "chunks" / f"{a1.stable_key}.meta.json"
    meta_data = json.loads(meta_path.read_text())
    meta_data["source_sha256"] = "f" * 64
    meta_path.write_text(json.dumps(meta_data))

    report = vc.validate_canonical_package(output_dir, plan)

    assert report.status == "FAIL"
    assert any(i.code == "chunk_source_sha256_mismatch" for i in report.issues)


# ---------------------------------------------------------------------------
# Empty chunks
# ---------------------------------------------------------------------------

def test_fail_on_empty_chunk(tmp_path):
    a1 = _anchor(["Widget Setup"])
    plan = _confirmed_plan([a1])
    sliced = SlicedDocument(preamble="", chunks=[_slice(a1, "   \n")])
    output_dir = tmp_path / "canonical-content"
    package.build_canonical_package(plan, sliced, tmp_path / "raw_media", output_dir)
    report = vc.validate_canonical_package(output_dir, plan)
    assert report.status == "FAIL"
    assert "empty_chunk" in _codes(report)


# ---------------------------------------------------------------------------
# Heading path missing from chunk content (WARN-level)
# ---------------------------------------------------------------------------

def test_warn_on_heading_missing_from_chunk_content(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    content_path = output_dir / "chunks" / f"{a1.stable_key}.md"
    content_path.write_text("Body one, but the heading line got dropped.\n")
    # Recompute + fix the stored hash so this test isolates the heading
    # check from the (separately-tested) content-hash-mismatch check.
    meta_path = output_dir / "chunks" / f"{a1.stable_key}.meta.json"
    meta = json.loads(meta_path.read_text())
    meta["content_sha256"] = hashing.content_hash(content_path.read_text().encode("utf-8"))
    meta_path.write_text(json.dumps(meta))
    # Supply cleaned_markdown_text so the content-comparison check runs and
    # does not produce an error that would mask this heading-level warning.
    cleaned = "\n".join(
        (output_dir / "chunks" / f"{a.stable_key}.md").read_text()
        for a in (a1, a2)
    )
    report = vc.validate_canonical_package(output_dir, plan, cleaned_markdown_text=cleaned)
    assert report.status == "WARN"
    matches = _codes(report, "heading_missing_from_content")
    assert len(matches) == 1
    assert matches[0].severity == "warning"


# ---------------------------------------------------------------------------
# Content loss/duplication using normalized aggregate comparison
# ---------------------------------------------------------------------------


def _build_minimal_valid_package(tmp_path, generator_plugin: str = "docx-to-content", with_media: bool = False, strategy: str = "chunked", chunk_count: int = 1, validated: bool = False):
    """Build a minimal, fully valid canonical package for tests.
    Returns the package directory Path. Writes the plan used to build to
    tmp_path / "plan.json" so `_load_plan_used_to_build` can retrieve it.

    Backwards compatible with the prior single-arg form. New kwargs:
    - with_media: if True, include a media file under raw_media/media and
      reference it from the first chunk.
    - strategy: passed to the confirmed plan ("chunked" or "grouped").
    - chunk_count: number of distinct chunks to create (>=1).
    - validated: if True, run the real validator and write a PASS validation.json
      (replacing the default PENDING placeholder written by package builders).
    """
    # Build anchors and sliced document with chunk_count distinct chunks
    anchors = []
    chunks = []
    for i in range(chunk_count):
        name = "Minimal" if chunk_count == 1 else f"Minimal {i+1}"
        a = _anchor([name])
        anchors.append(a)
        content = f"# {name}\n\nBody {i+1}.\n"
        # If requested, include a media reference in the first chunk
        if with_media and i == 0:
            content += "\n![diagram](media/diagram.png)\n"
        chunks.append(_slice(a, content))

    plan = _confirmed_plan(anchors, strategy=strategy)
    sliced = SlicedDocument(preamble="", chunks=chunks)
    raw_media_dir = tmp_path / "raw_media"
    # create raw_media and optional media file
    raw_media_dir.mkdir()
    if with_media:
        (raw_media_dir / "media").mkdir(parents=True, exist_ok=True)
        (raw_media_dir / "media" / "diagram.png").write_bytes(b"fake-png-bytes")

    output_dir = tmp_path / "canonical-content"
    # Use grouped vs chunked builder depending on strategy
    if strategy == "grouped":
        package.build_grouped_canonical_package(plan, sliced, raw_media_dir, output_dir)
    else:
        package.build_canonical_package(plan, sliced, raw_media_dir, output_dir)

    if generator_plugin != "docx-to-content":
        data = json.loads((output_dir / "manifest.json").read_text())
        data["generator"]["plugin"] = generator_plugin
        (output_dir / "manifest.json").write_text(json.dumps(data))

    # Persist the plan used so tests can re-load it
    (tmp_path / "plan.json").write_text(json.dumps(plan.to_dict(), indent=2))

    # Optionally write a real PASS validation.json using the real validator
    if validated:
        try:
            # Reconstruct a cleaned_markdown_text from the staged chunk files
            # so the aggregate content-loss/duplication check can run and not
            # fail due to missing cleaned text (producer-path packages treat
            # that as an error). Use manifest order (source_order) to
            # reconstruct a canonical aggregate.
            manifest = json.loads((output_dir / "manifest.json").read_text())
            ordered = sorted(manifest.get("chunks", []), key=lambda c: c.get("source_order", 0))
            cleaned = "\n".join((output_dir / c["content_file"]).read_text() for c in ordered)
            report = vc.validate_canonical_package(output_dir, plan, cleaned_markdown_text=cleaned)
            vc.write_validation_report(report, output_dir)
        except Exception:
            # Tests that request a pre-validated package expect a simple
            # PASS report to be written; let exceptions surface to the
            # caller rather than masking them here.
            raise

    return output_dir


def _load_plan_used_to_build(package_dir):
    tmp_path = Path(package_dir).parent
    data = json.loads((tmp_path / "plan.json").read_text())
    return contracts.ConversionPlan.from_dict(data)


def test_producer_path_content_comparison_skip_is_now_an_error(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path)  # generator.plugin == "docx-to-content"
    plan = _load_plan_used_to_build(package_dir)
    # cleaned_markdown_text omitted -- this package's own manifest records
    # generator.plugin == "docx-to-content", so it's a producer-path
    # package regardless of what any caller might wish were true.
    report = vc.validate_canonical_package(package_dir, plan)

    assert report.status == "FAIL"
    assert any(
        i.code == "content_comparison_skipped" and i.severity == "error"
        for i in report.issues
    )


def test_fixture_provenance_content_comparison_skip_is_not_an_error(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, generator_plugin="hand-authored-fixture")
    plan = _load_plan_used_to_build(package_dir)
    report = vc.validate_canonical_package(package_dir, plan)

    assert report.status != "FAIL" or not any(
        i.code == "content_comparison_skipped" for i in report.issues
    )

def test_fail_on_content_loss_detected_by_aggregate_comparison(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    cleaned = (
        "# Widget Setup\n\nBody one.\n\n"
        "# Widget Configuration\n\nBody two.\n\n"
        "# A Section That Got Lost\n\nThis paragraph never made it into any chunk.\n"
    )
    report = vc.validate_canonical_package(
        output_dir, plan, cleaned_markdown_text=cleaned
    )
    assert report.status == "FAIL"
    assert "content_loss_or_duplication" in _codes(report)


def test_fail_on_content_duplication_detected_by_aggregate_comparison(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    # cleaned text is only the first chunk's content -- reconstructed
    # aggregate (both chunks) has extra content relative to "original".
    cleaned = "# Widget Setup\n\nBody one.\n"
    report = vc.validate_canonical_package(
        output_dir, plan, cleaned_markdown_text=cleaned
    )
    assert report.status == "FAIL"
    assert "content_loss_or_duplication" in _codes(report)


def test_pass_when_aggregate_matches_after_whitespace_normalization(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    # Extra trailing whitespace / blank-line churn that normalization
    # should absorb without flagging content loss.
    cleaned = "# Widget Setup   \n\n\n\nBody one.\n\n# Widget Configuration\n\nBody two.\n\n\n"
    report = vc.validate_canonical_package(
        output_dir, plan, cleaned_markdown_text=cleaned
    )
    assert "content_loss_or_duplication" not in _codes(report)


def test_pass_on_clean_package_with_image_despite_media_path_rewrite(tmp_path):
    """Regression test (Task 10b): `package.build_canonical_package` (via
    `rewrite_media_and_copy`) rewrites every staged chunk's media
    reference from `media/<file>` to `../media/<file>` (chunks/ and
    media/ are sibling dirs). `cleaned_markdown_text` is the PRE-rewrite
    text and still says `media/<file>`. Before the Task 10b fix, the
    aggregate comparison in `_check_content_loss_and_duplication` compared
    these two forms verbatim and always FAILed on any document containing
    an image, even though no real content was lost or duplicated."""
    a1 = _anchor(["Widget Setup"])
    plan = _confirmed_plan([a1])
    sliced = SlicedDocument(
        preamble="",
        chunks=[_slice(a1, "# Widget Setup\n\nBody one.\n\n![a diagram](media/diagram.png)\n")],
    )
    raw_media_dir = tmp_path / "raw_media"
    (raw_media_dir / "media").mkdir(parents=True)
    (raw_media_dir / "media" / "diagram.png").write_bytes(b"fake-png-bytes")
    output_dir = tmp_path / "canonical-content"
    package.build_canonical_package(plan, sliced, raw_media_dir, output_dir)

    # cleaned_markdown_text is the pre-rewrite text: still `media/...`,
    # not `../media/...` like the staged chunk now contains.
    cleaned = "# Widget Setup\n\nBody one.\n\n![a diagram](media/diagram.png)\n"
    report = vc.validate_canonical_package(
        output_dir, plan, cleaned_markdown_text=cleaned
    )
    assert "content_loss_or_duplication" not in _codes(report)
    assert report.status == "PASS", report.issues


def test_fail_on_real_content_loss_still_detected_when_image_present(tmp_path):
    """The Task 10b fix must not weaken real content-loss detection: an
    actually-missing paragraph must still FAIL even when an image
    reference (with its expected path-prefix rewrite) is also present."""
    a1 = _anchor(["Widget Setup"])
    plan = _confirmed_plan([a1])
    sliced = SlicedDocument(
        preamble="",
        chunks=[_slice(a1, "# Widget Setup\n\nBody one.\n\n![a diagram](media/diagram.png)\n")],
    )
    raw_media_dir = tmp_path / "raw_media"
    (raw_media_dir / "media").mkdir(parents=True)
    (raw_media_dir / "media" / "diagram.png").write_bytes(b"fake-png-bytes")
    output_dir = tmp_path / "canonical-content"
    package.build_canonical_package(plan, sliced, raw_media_dir, output_dir)

    # cleaned_markdown_text has an extra paragraph that never made it
    # into the staged chunk -- a genuine content loss, not just a media
    # path difference.
    cleaned = (
        "# Widget Setup\n\nBody one.\n\n![a diagram](media/diagram.png)\n\n"
        "This paragraph was lost during chunking.\n"
    )
    report = vc.validate_canonical_package(
        output_dir, plan, cleaned_markdown_text=cleaned
    )
    assert report.status == "FAIL"
    assert "content_loss_or_duplication" in _codes(report)


def test_fail_on_real_content_duplication_still_detected_when_image_present(tmp_path):
    """The Task 10b fix must not weaken real duplication detection: an
    actually-duplicated paragraph in the staged chunks must still FAIL
    even when an image reference (with its expected path-prefix rewrite)
    is also present."""
    a1 = _anchor(["Widget Setup"])
    plan = _confirmed_plan([a1])
    sliced = SlicedDocument(
        preamble="",
        chunks=[
            _slice(
                a1,
                "# Widget Setup\n\nBody one.\n\n![a diagram](media/diagram.png)\n\n"
                "Body one.\n",  # duplicated paragraph
            )
        ],
    )
    raw_media_dir = tmp_path / "raw_media"
    (raw_media_dir / "media").mkdir(parents=True)
    (raw_media_dir / "media" / "diagram.png").write_bytes(b"fake-png-bytes")
    output_dir = tmp_path / "canonical-content"
    package.build_canonical_package(plan, sliced, raw_media_dir, output_dir)

    cleaned = "# Widget Setup\n\nBody one.\n\n![a diagram](media/diagram.png)\n"
    report = vc.validate_canonical_package(
        output_dir, plan, cleaned_markdown_text=cleaned
    )
    assert report.status == "FAIL"
    assert "content_loss_or_duplication" in _codes(report)


# ---------------------------------------------------------------------------
# Unresolved structural anchors
# ---------------------------------------------------------------------------

def test_fail_on_unresolved_structural_anchor_manifest_chunk_not_in_plan(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    data = json.loads((output_dir / "manifest.json").read_text())
    data["chunks"][0]["chunk_id"] = "chunk-id-not-in-plan-anchors"
    (output_dir / "manifest.json").write_text(json.dumps(data))
    # Rename the sidecar/content files to match, and fix chunk_id inside
    # the sidecar, so this test isolates the anchor check from missing-
    # file/mismatch checks.
    old_content = output_dir / "chunks" / f"{a1.stable_key}.md"
    old_meta = output_dir / "chunks" / f"{a1.stable_key}.meta.json"
    new_content = output_dir / "chunks" / "chunk-id-not-in-plan-anchors.md"
    new_meta = output_dir / "chunks" / "chunk-id-not-in-plan-anchors.meta.json"
    new_content.write_text(old_content.read_text())
    meta = json.loads(old_meta.read_text())
    meta["chunk_id"] = "chunk-id-not-in-plan-anchors"
    new_meta.write_text(json.dumps(meta))
    old_content.unlink()
    old_meta.unlink()
    data["chunks"][0]["content_file"] = "chunks/chunk-id-not-in-plan-anchors.md"
    data["chunks"][0]["metadata_file"] = "chunks/chunk-id-not-in-plan-anchors.meta.json"
    (output_dir / "manifest.json").write_text(json.dumps(data))

    report = vc.validate_canonical_package(output_dir, plan)
    assert report.status == "FAIL"
    assert "unresolved_structural_anchor" in _codes(report)


# ---------------------------------------------------------------------------
# Raw TOC artifacts
# ---------------------------------------------------------------------------

def test_fail_on_raw_toc_artifact_in_chunk_content(tmp_path):
    a1 = _anchor(["Widget Setup"])
    plan = _confirmed_plan([a1])
    content = "# Widget Setup\n\n[Introduction](#_Toc123456)\n\nBody.\n"
    sliced = SlicedDocument(preamble="", chunks=[_slice(a1, content)])
    output_dir = tmp_path / "canonical-content"
    package.build_canonical_package(plan, sliced, tmp_path / "raw_media", output_dir)
    report = vc.validate_canonical_package(output_dir, plan)
    assert report.status == "FAIL"
    assert "raw_toc_artifact" in _codes(report)


# ---------------------------------------------------------------------------
# Pandoc attributes
# ---------------------------------------------------------------------------

def test_fail_on_leftover_pandoc_attribute_artifact(tmp_path):
    a1 = _anchor(["Widget Setup"])
    plan = _confirmed_plan([a1])
    content = "# Widget Setup\n\nSome text {.underline} remains.\n"
    sliced = SlicedDocument(preamble="", chunks=[_slice(a1, content)])
    output_dir = tmp_path / "canonical-content"
    package.build_canonical_package(plan, sliced, tmp_path / "raw_media", output_dir)
    report = vc.validate_canonical_package(output_dir, plan)
    assert report.status == "FAIL"
    assert "pandoc_attribute_artifact" in _codes(report)


# ---------------------------------------------------------------------------
# Images embedded in headings
# ---------------------------------------------------------------------------

def test_fail_on_image_embedded_in_heading(tmp_path):
    a1 = _anchor(["Widget Setup"])
    plan = _confirmed_plan([a1])
    raw_media_dir = tmp_path / "raw_media"
    (raw_media_dir / "media").mkdir(parents=True)
    (raw_media_dir / "media" / "icon.png").write_bytes(b"bytes")
    content = "# Widget Setup ![icon](media/icon.png)\n\nBody.\n"
    sliced = SlicedDocument(preamble="", chunks=[_slice(a1, content)])
    output_dir = tmp_path / "canonical-content"
    package.build_canonical_package(plan, sliced, raw_media_dir, output_dir)
    report = vc.validate_canonical_package(output_dir, plan)
    assert report.status == "FAIL"
    assert "image_in_heading" in _codes(report)


# ---------------------------------------------------------------------------
# Unsupported legacy media (post-packaging second pass)
# ---------------------------------------------------------------------------

def test_fail_on_unsupported_legacy_media_reference_in_staged_content(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    (output_dir / "media").mkdir(exist_ok=True)
    (output_dir / "media" / "legacy.emf").write_bytes(b"not-a-real-emf")
    content_path = output_dir / "chunks" / f"{a1.stable_key}.md"
    new_content = "# Widget Setup\n\n![diagram](../media/legacy.emf)\n"
    content_path.write_text(new_content)
    meta_path = output_dir / "chunks" / f"{a1.stable_key}.meta.json"
    meta = json.loads(meta_path.read_text())
    meta["content_sha256"] = hashing.content_hash(new_content.encode("utf-8"))
    meta_path.write_text(json.dumps(meta))
    data = json.loads((output_dir / "manifest.json").read_text())
    data["media"].append("legacy.emf")
    (output_dir / "manifest.json").write_text(json.dumps(data))

    report = vc.validate_canonical_package(output_dir, plan)
    assert report.status == "FAIL"
    assert "unsupported_legacy_media" in _codes(report)


# ---------------------------------------------------------------------------
# Broken local document links
# ---------------------------------------------------------------------------

def test_fail_on_broken_local_document_link(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    meta_path = output_dir / "chunks" / f"{a1.stable_key}.meta.json"
    meta = json.loads(meta_path.read_text())
    meta["local_links"] = ["chunks/does-not-exist-chunk.md"]
    meta_path.write_text(json.dumps(meta))
    report = vc.validate_canonical_package(output_dir, plan)
    assert report.status == "FAIL"
    assert "broken_local_link" in _codes(report)


def test_pass_local_link_to_a_known_chunk_id(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    meta_path = output_dir / "chunks" / f"{a1.stable_key}.meta.json"
    meta = json.loads(meta_path.read_text())
    meta["local_links"] = [f"chunks/{a2.stable_key}.md"]
    meta_path.write_text(json.dumps(meta))
    report = vc.validate_canonical_package(output_dir, plan)
    assert "broken_local_link" not in _codes(report)


# ---------------------------------------------------------------------------
# Broken media references
# ---------------------------------------------------------------------------

def test_fail_on_broken_media_reference(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    content_path = output_dir / "chunks" / f"{a1.stable_key}.md"
    new_content = "# Widget Setup\n\n![missing](../media/does-not-exist.png)\n"
    content_path.write_text(new_content)
    meta_path = output_dir / "chunks" / f"{a1.stable_key}.meta.json"
    meta = json.loads(meta_path.read_text())
    meta["content_sha256"] = hashing.content_hash(new_content.encode("utf-8"))
    meta_path.write_text(json.dumps(meta))
    report = vc.validate_canonical_package(output_dir, plan)
    assert report.status == "FAIL"
    assert "broken_media_reference" in _codes(report)


# ---------------------------------------------------------------------------
# Path traversal / absolute-path references (second pass on staged content)
# ---------------------------------------------------------------------------

def test_fail_on_path_traversal_reference_in_staged_content(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    content_path = output_dir / "chunks" / f"{a1.stable_key}.md"
    new_content = "# Widget Setup\n\n![escape](../../etc/passwd)\n"
    content_path.write_text(new_content)
    meta_path = output_dir / "chunks" / f"{a1.stable_key}.meta.json"
    meta = json.loads(meta_path.read_text())
    meta["content_sha256"] = hashing.content_hash(new_content.encode("utf-8"))
    meta_path.write_text(json.dumps(meta))
    report = vc.validate_canonical_package(output_dir, plan)
    assert report.status == "FAIL"
    assert "path_traversal_or_absolute_reference" in _codes(report)


def test_fail_on_absolute_path_reference_in_staged_content(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    content_path = output_dir / "chunks" / f"{a1.stable_key}.md"
    new_content = "# Widget Setup\n\n![escape](/etc/passwd)\n"
    content_path.write_text(new_content)
    meta_path = output_dir / "chunks" / f"{a1.stable_key}.meta.json"
    meta = json.loads(meta_path.read_text())
    meta["content_sha256"] = hashing.content_hash(new_content.encode("utf-8"))
    meta_path.write_text(json.dumps(meta))
    report = vc.validate_canonical_package(output_dir, plan)
    assert report.status == "FAIL"
    assert "path_traversal_or_absolute_reference" in _codes(report)


# ---------------------------------------------------------------------------
# write_validation_report
# ---------------------------------------------------------------------------

def test_write_validation_report_overwrites_placeholder(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    placeholder = json.loads((output_dir / "validation.json").read_text())
    assert placeholder["status"] == "PENDING"

    report = vc.validate_canonical_package(output_dir, plan)
    vc.write_validation_report(report, output_dir)

    written = json.loads((output_dir / "validation.json").read_text())
    assert written["status"] == report.status
    assert written["status"] != "PENDING"


# ---------------------------------------------------------------------------
# Grouped-package validation (Task 17-topic-grouping, Task 7)
# ---------------------------------------------------------------------------

def _build_grouped_package(tmp_path):
    file_access = _anchor(["File Access"], level=1)
    how_to_seal = _anchor(["File Access", "How to Seal a File"], level=2)
    overview = _anchor(["Overview"], level=1)
    plan = _confirmed_plan([file_access, how_to_seal, overview], strategy="grouped")
    sliced = SlicedDocument(
        preamble="",
        chunks=[
            _slice(file_access, "# File Access\n\nIntro to file access.\n"),
            _slice(how_to_seal, "## How to Seal a File\n\nSteps to seal a file.\n"),
            _slice(overview, "# Overview\n\nOverview body.\n"),
        ],
    )
    raw_media_dir = tmp_path / "raw_media"
    raw_media_dir.mkdir()
    output_dir = tmp_path / "canonical-content"
    package.build_grouped_canonical_package(plan, sliced, raw_media_dir, output_dir)
    return plan, output_dir


def _grouped_cleaned_markdown():
    return (
        "# File Access\n\nIntro to file access.\n\n"
        "## How to Seal a File\n\nSteps to seal a file.\n\n"
        "# Overview\n\nOverview body.\n"
    )


def test_validate_grouped_package_passes_when_every_anchor_assigned_once(tmp_path):
    plan, output_dir = _build_grouped_package(tmp_path)
    report = vc.validate_canonical_package(
        output_dir, plan, cleaned_markdown_text=_grouped_cleaned_markdown()
    )
    assert report.status == "PASS", report.issues


def test_validate_grouped_package_fails_when_an_anchor_is_missing(tmp_path):
    plan, output_dir = _build_grouped_package(tmp_path)
    meta_path = next((output_dir / "chunks").glob("*.meta.json"))
    meta = json.loads(meta_path.read_text())
    if meta.get("anchors"):
        meta["anchors"].pop()
        content_path = output_dir / meta["content_file"]
        meta["content_sha256"] = hashing.content_hash(
            content_path.read_text().encode("utf-8")
        )
        meta_path.write_text(json.dumps(meta))
    report = vc.validate_canonical_package(output_dir, plan)
    assert report.status == "FAIL"
    assert "unassigned_structural_anchor" in _codes(report)


def test_validate_grouped_package_fails_when_an_anchor_is_duplicated_across_topics(tmp_path):
    plan, output_dir = _build_grouped_package(tmp_path)
    meta_paths = sorted((output_dir / "chunks").glob("*.meta.json"))
    metas = [json.loads(p.read_text()) for p in meta_paths]
    first_with_anchors = next(m for m in metas if m.get("anchors"))
    other = next(m for m in metas if m is not first_with_anchors)
    other["anchors"].append(first_with_anchors["anchors"][0])
    for path, meta in zip(meta_paths, metas):
        path.write_text(json.dumps(meta))
    report = vc.validate_canonical_package(output_dir, plan)
    assert report.status == "FAIL"
    assert "duplicate_structural_anchor_assignment" in _codes(report)


def test_validate_grouped_package_fails_when_publication_map_missing(tmp_path):
    plan, output_dir = _build_grouped_package(tmp_path)
    (output_dir / "publication-map.json").unlink()
    report = vc.validate_canonical_package(output_dir, plan)
    assert report.status == "FAIL"
    assert "missing_publication_map" in _codes(report)


def test_validate_grouped_package_fails_when_publication_map_order_has_gap(tmp_path):
    plan, output_dir = _build_grouped_package(tmp_path)
    pub_map_path = output_dir / "publication-map.json"
    data = json.loads(pub_map_path.read_text())
    data["entries"][1]["order"] = 5
    pub_map_path.write_text(json.dumps(data))
    report = vc.validate_canonical_package(output_dir, plan)
    assert report.status == "FAIL"
    assert "publication_map_order_invalid" in _codes(report)


def test_malformed_publication_map_is_a_controlled_validation_error(tmp_path):
    plan, output_dir = _build_grouped_package(tmp_path)
    (output_dir / "publication-map.json").write_text("{not valid json")

    report = vc.validate_canonical_package(output_dir, plan)

    assert report.status == "FAIL"
    assert any(i.code == "malformed_publication_map" for i in report.issues)


def test_unexpected_publication_map_on_non_grouped_package_is_rejected(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    (output_dir / "publication-map.json").write_text(json.dumps({
        "schema_version": "1.0",
        "package_identity": "sha256:" + "a" * 64,
        "entries": [],
    }))

    report = vc.validate_canonical_package(output_dir, plan)

    assert report.status == "FAIL"
    assert any(i.code == "unexpected_publication_map" for i in report.issues)


def test_publication_map_chunk_id_diverging_from_topic_id_is_detected(tmp_path):
    plan, output_dir = _build_grouped_package(tmp_path)
    pub_map_path = output_dir / "publication-map.json"
    data = json.loads(pub_map_path.read_text())
    # Deliberately break the chunk_id/topic_id equality the real producer
    # currently maintains -- chunk_id now points at a chunk that does not
    # exist in the manifest at all, proving the validator checks chunk_id
    # itself rather than trusting topic_id as a stand-in for it.
    data["entries"][0]["chunk_id"] = "nonexistent-chunk-id"
    pub_map_path.write_text(json.dumps(data))

    report = vc.validate_canonical_package(output_dir, plan)

    assert report.status == "FAIL"
    assert any(i.code == "publication_map_chunk_mismatch" for i in report.issues)


def test_validate_ungrouped_package_unaffected_by_new_grouped_checks(tmp_path):
    plan, output_dir, a1, a2 = _build_simple_package(tmp_path)
    cleaned = "# Widget Setup\n\nBody one.\n\n# Widget Configuration\n\nBody two.\n"
    report = vc.validate_canonical_package(
        output_dir, plan, cleaned_markdown_text=cleaned
    )
    assert report.status == "PASS", report.issues


# ---------------------------------------------------------------------------
# Media-decision reconciliation (Task 18 general media-disposition
# mechanism): a pending ("requires-human-review") media decision blocks;
# a human-confirmed omission does not.
# ---------------------------------------------------------------------------

def _plan_with_media_decision(record):
    source_fp = contracts.SourceFingerprint(
        path="sourcedocuments/widget.docx", sha256="b" * 64, size_bytes=123
    )
    plan = contracts.ConversionPlan(
        schema_version=contracts.CONVERSION_PLAN_SCHEMA_VERSION,
        plan_id="",
        source=source_fp,
        strategy="grouped",
        chunk_level=1,
        chunk_anchors=[],
        content_type="manual",
        template_profile="source-structure-v1",
        confirmation=contracts.Confirmation(
            status="confirmed", confirmed_by="tester", confirmed_at="2026-01-01T00:00:00Z"
        ),
        media_decisions=[record],
    )
    plan.plan_id = plan_verification.compute_plan_id(plan)
    return plan


def test_pending_media_decision_is_blocking():
    plan = _plan_with_media_decision({
        "source_media_id": "image1.png",
        "classification": "requires-human-review",
        "disposition": "requires-human-decision",
    })
    issues = vc._check_media_decisions(plan)
    assert any(i.code == "unclassified_media" for i in issues)


def test_reviewed_media_omission_is_not_blocking():
    plan = _plan_with_media_decision({
        "source_media_id": "image1.png",
        "classification": "obsolete-source-layout-artifact",
        "disposition": "omit-as-reviewed-artifact",
        "decision_authority": "human-confirmed",
    })
    issues = vc._check_media_decisions(plan)
    assert issues == []


def test_no_media_decisions_is_not_blocking():
    source_fp = contracts.SourceFingerprint(
        path="sourcedocuments/widget.docx", sha256="b" * 64, size_bytes=123
    )
    plan = contracts.ConversionPlan(
        schema_version=contracts.CONVERSION_PLAN_SCHEMA_VERSION,
        plan_id="",
        source=source_fp,
        strategy="grouped",
        chunk_level=1,
        chunk_anchors=[],
        content_type="manual",
        template_profile="source-structure-v1",
        confirmation=contracts.Confirmation(
            status="confirmed", confirmed_by="tester", confirmed_at="2026-01-01T00:00:00Z"
        ),
    )
    plan.plan_id = plan_verification.compute_plan_id(plan)
    assert vc._check_media_decisions(plan) == []


# ---------------------------------------------------------------------------
# Preamble-aware content-loss comparison (Task 18): package builders never
# copy SlicedDocument.preamble into any chunk (chunking.py's documented
# design), so the content-loss/duplication comparison must be made against
# preamble-stripped cleaned text, not the full cleaned document -- a real
# pilot document's non-empty preamble (title page/TOC) would otherwise
# always FAIL this check for content that was deliberately excluded from
# canonical chunks, not actually lost.
# ---------------------------------------------------------------------------

def test_content_loss_check_passes_when_compared_against_preamble_stripped_text(tmp_path):
    a1 = _anchor(["Widget Setup"])
    plan = _confirmed_plan([a1])
    preamble = "**Widget Manual**\n\n**Version 1.0**\n\n"
    sliced = SlicedDocument(preamble=preamble, chunks=[_slice(a1, "# Widget Setup\n\nBody one.\n")])
    output_dir = tmp_path / "canonical-content"
    package.build_canonical_package(plan, sliced, tmp_path / "raw_media", output_dir)

    full_cleaned_text = preamble + "# Widget Setup\n\nBody one.\n"
    text_without_preamble = full_cleaned_text[len(preamble):]

    # Mirrors the pre-fix bug: comparing against the FULL cleaned text
    # (preamble included) reports content loss for content that was never
    # meant to be in any chunk.
    report_with_preamble = vc.validate_canonical_package(
        output_dir, plan, cleaned_markdown_text=full_cleaned_text
    )
    assert "content_loss_or_duplication" in _codes(report_with_preamble)

    # The fix: compare against preamble-stripped text instead.
    report_without_preamble = vc.validate_canonical_package(
        output_dir, plan, cleaned_markdown_text=text_without_preamble
    )
    assert "content_loss_or_duplication" not in _codes(report_without_preamble)
