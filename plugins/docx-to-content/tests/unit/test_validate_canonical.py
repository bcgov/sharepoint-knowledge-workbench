"""
test_validate_canonical.py
============================

Tests for scripts/validate_canonical.py -- the canonical-package validator
(Task 10). Builds real staged packages via `package.build_canonical_package`
(Task 9), then mutates the on-disk package/plan to trigger each of the 20
required detections in spec Section 9 / the Task 10 brief, asserting the
resulting `ValidationReport` status and issue codes.

Fixture heading/product names are invented placeholders (e.g. "Widget
Setup", "Gadget Alpha") -- no real CEIS manual content appears here.
"""

import json

import pytest

import contracts
import hashing
import package
import validate_canonical as vc
from chunking import ChunkSlice, SlicedDocument
from identity import make_chunk_id
from plans import build_draft_plan, confirm_plan


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
    draft = build_draft_plan(
        source_fingerprint=source_fp,
        strategy=strategy,
        chunk_level=1,
        chunk_anchors=chunk_anchors,
    )
    return confirm_plan(draft, confirmed_by="tester")


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
    assert report.status == "WARN"
    assert "content_comparison_skipped" in _codes(report)


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
    report = vc.validate_canonical_package(output_dir, plan)
    assert report.status == "WARN"
    matches = _codes(report, "heading_missing_from_content")
    assert len(matches) == 1
    assert matches[0].severity == "warning"


# ---------------------------------------------------------------------------
# Content loss/duplication using normalized aggregate comparison
# ---------------------------------------------------------------------------

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
