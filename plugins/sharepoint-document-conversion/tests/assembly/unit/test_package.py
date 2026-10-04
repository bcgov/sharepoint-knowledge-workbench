"""
test_package.py
================

Tests for scripts/assembly/package.py — the canonical-content package builder
(chunk/sidecar writing, media inventory/copy/rewrite, manifest assembly).
Task 9.

Uses fabricated `StructuralAnchor` / `chunking.ChunkSlice` /
`chunking.SlicedDocument` objects directly rather than real pandoc/docx
input, since package.py's contract is "already-sliced chunk content in" ->
"canonical package on disk out" and does not itself invoke pandoc or the
cleanup pipeline. Fixture heading/product names are synthetic placeholders (e.g.
"Widget Setup", "Gadget Alpha").
"""

import json

import pytest

from canonical_schema import canonical_package as contracts
from canonical_schema import analysis_plan as plan_contracts
import package
import topic_boundary_core as topic_grouping
from chunking import ChunkSlice, SlicedDocument
from identity_core import make_chunk_id


def _anchor(path, occurrence=1, level=1):
    return plan_contracts.StructuralAnchor(
        stable_key=make_chunk_id(path, occurrence),
        heading_text=path[-1],
        heading_level=level,
        occurrence=occurrence,
        source_heading_path=list(path),
    )


def _confirmed_plan(chunk_anchors, source_sha256="b" * 64, strategy="chunked", confirmed_topic_roots=None):
    source_fp = plan_contracts.SourceFingerprint(
        path="sourcedocuments/widget.docx", sha256=source_sha256, size_bytes=123
    )
    return plan_contracts.ConversionPlan(
        schema_version=plan_contracts.CONVERSION_PLAN_SCHEMA_VERSION,
        plan_id="sha256:" + "0" * 64,
        source=source_fp,
        strategy=strategy,
        chunk_level=1,
        chunk_anchors=list(chunk_anchors),
        content_type="manual",
        template_profile="source-structure-v1",
        confirmation=plan_contracts.Confirmation(
            status="confirmed", confirmed_by="tester", confirmed_at="2026-01-01T00:00:00Z"
        ),
        confirmed_topic_roots=confirmed_topic_roots,
    )


def _slice(anchor, content):
    return ChunkSlice(anchor=anchor, start_line=0, end_line=1, content=content)


# ---------------------------------------------------------------------------
# One sidecar per chunk, no orphan sidecars
# ---------------------------------------------------------------------------

def test_one_sidecar_per_chunk_and_no_orphans(tmp_path):
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

    chunks_dir = output_dir / "chunks"
    md_files = {p.stem for p in chunks_dir.glob("*.md")}
    meta_files = {p.name[: -len(".meta.json")] for p in chunks_dir.glob("*.meta.json")}

    assert md_files == {a1.stable_key, a2.stable_key}
    assert meta_files == md_files, "every chunk must have exactly one sidecar, no orphans"


# ---------------------------------------------------------------------------
# Chunk IDs are never recomputed independently
# ---------------------------------------------------------------------------

def test_chunk_id_reused_from_anchor_stable_key_not_recomputed(tmp_path):
    anchor = _anchor(["Widget Setup"])
    plan = _confirmed_plan([anchor])
    sliced = SlicedDocument(
        preamble="", chunks=[_slice(anchor, "# Widget Setup\n\nBody.\n")]
    )
    output_dir = tmp_path / "canonical-content"
    manifest = package.build_canonical_package(
        plan, sliced, tmp_path / "raw_media", output_dir
    )
    assert manifest.chunks[0].chunk_id == anchor.stable_key
    assert (output_dir / "chunks" / f"{anchor.stable_key}.md").exists()


# ---------------------------------------------------------------------------
# Hashes, plan ID, source hash, schema version, stable ordering
# ---------------------------------------------------------------------------

def test_hashes_plan_id_source_hash_schema_version_and_ordering(tmp_path):
    a1 = _anchor(["Alpha"])
    a2 = _anchor(["Beta"])
    a3 = _anchor(["Gamma"])
    plan = _confirmed_plan([a1, a2, a3], source_sha256="c" * 64)
    sliced = SlicedDocument(
        preamble="",
        chunks=[
            _slice(a1, "# Alpha\n\none\n"),
            _slice(a2, "# Beta\n\ntwo\n"),
            _slice(a3, "# Gamma\n\nthree\n"),
        ],
    )
    output_dir = tmp_path / "canonical-content"
    manifest = package.build_canonical_package(
        plan, sliced, tmp_path / "raw_media", output_dir
    )

    assert manifest.schema_version == contracts.MANIFEST_SCHEMA_VERSION
    assert manifest.plan_id == plan.plan_id
    assert manifest.source.sha256 == "c" * 64

    # Stable ordering: matches chunk_anchors order, not filesystem order.
    assert [c.chunk_id for c in manifest.chunks] == [
        a1.stable_key, a2.stable_key, a3.stable_key,
    ]
    assert [c.source_order for c in manifest.chunks] == [0, 1, 2]

    for idx, chunk in enumerate(manifest.chunks):
        meta_path = output_dir / chunk.metadata_file
        meta = contracts.ChunkMetadata.from_dict(json.loads(meta_path.read_text()))
        assert meta.schema_version == contracts.CHUNK_METADATA_SCHEMA_VERSION
        assert meta.plan_id == plan.plan_id
        assert meta.source_sha256 == "c" * 64
        assert meta.source_order == idx

        content_path = output_dir / chunk.content_file
        import hashing
        expected = hashing.content_hash(content_path.read_text().encode("utf-8"))
        assert meta.content_sha256 == expected


def test_manifest_ordering_independent_of_filesystem_listing_order(tmp_path):
    # Chunk IDs chosen so that lexicographic filesystem order (Alpha before
    # Zeta) is the REVERSE of the plan's declared chunk_anchors order, to
    # prove ordering is not derived from glob()/listdir() results.
    a_last = _anchor(["Alpha Last In Plan"])
    a_first = _anchor(["Zeta First In Plan"])
    plan = _confirmed_plan([a_first, a_last])
    sliced = SlicedDocument(
        preamble="",
        chunks=[
            _slice(a_first, "# Zeta\n\nfirst\n"),
            _slice(a_last, "# Alpha\n\nlast\n"),
        ],
    )
    output_dir = tmp_path / "canonical-content"
    manifest = package.build_canonical_package(
        plan, sliced, tmp_path / "raw_media", output_dir
    )
    assert [c.chunk_id for c in manifest.chunks] == [a_first.stable_key, a_last.stable_key]


# ---------------------------------------------------------------------------
# Media: copied once, multi-chunk references
# ---------------------------------------------------------------------------

def test_media_copied_once_and_referenced_from_multiple_chunks(tmp_path):
    a1 = _anchor(["Alpha"])
    a2 = _anchor(["Beta"])
    plan = _confirmed_plan([a1, a2])
    raw_media_dir = tmp_path / "raw_media"
    (raw_media_dir / "media").mkdir(parents=True)
    (raw_media_dir / "media" / "image1.png").write_bytes(b"shared-bytes")

    sliced = SlicedDocument(
        preamble="",
        chunks=[
            _slice(a1, "# Alpha\n\n![diagram](media/image1.png)\n"),
            _slice(a2, "# Beta\n\nSame image again: ![diagram](media/image1.png)\n"),
        ],
    )
    output_dir = tmp_path / "canonical-content"
    manifest = package.build_canonical_package(plan, sliced, raw_media_dir, output_dir)

    media_files = list((output_dir / "media").iterdir())
    assert len(media_files) == 1
    assert manifest.media == ["image1.png"]

    for chunk in manifest.chunks:
        content = (output_dir / chunk.content_file).read_text()
        assert "../media/image1.png" in content


# ---------------------------------------------------------------------------
# Media: duplicate names, different content -> disambiguated
# ---------------------------------------------------------------------------

def test_duplicate_media_names_different_content_disambiguated(tmp_path):
    a1 = _anchor(["Alpha"])
    a2 = _anchor(["Beta"])
    plan = _confirmed_plan([a1, a2])

    # Two different subdirectories both extracted a file named image1.png,
    # but with genuinely different bytes (pandoc numbers media sequentially
    # per extraction run, so this collision is realistic across re-runs).
    raw_media_dir = tmp_path / "raw_media"
    sub_a = raw_media_dir / "runA"
    sub_b = raw_media_dir / "runB"
    sub_a.mkdir(parents=True)
    sub_b.mkdir(parents=True)
    (sub_a / "image1.png").write_bytes(b"content-A")
    (sub_b / "image1.png").write_bytes(b"content-B-different")

    sliced = SlicedDocument(
        preamble="",
        chunks=[
            _slice(a1, "# Alpha\n\n![a](runA/image1.png)\n"),
            _slice(a2, "# Beta\n\n![b](runB/image1.png)\n"),
        ],
    )
    output_dir = tmp_path / "canonical-content"
    package.build_canonical_package(plan, sliced, raw_media_dir, output_dir)

    media_files = sorted(p.name for p in (output_dir / "media").iterdir())
    assert len(media_files) == 2
    assert "image1.png" in media_files
    # second collision gets a distinguishing suffix, not silently overwritten
    disambiguated = [n for n in media_files if n != "image1.png"][0]
    assert disambiguated.startswith("image1-") and disambiguated.endswith(".png")

    content_a = (output_dir / "chunks" / f"{a1.stable_key}.md").read_text()
    content_b = (output_dir / "chunks" / f"{a2.stable_key}.md").read_text()
    assert "image1.png" in content_a
    assert disambiguated in content_b or "image1.png" in content_b
    assert content_a != content_b

    bytes_a = (output_dir / "media" / "image1.png").read_bytes()
    bytes_b_name = [n for n in media_files if n != "image1.png"][0]
    bytes_b = (output_dir / "media" / bytes_b_name).read_bytes()
    assert {bytes_a, bytes_b} == {b"content-A", b"content-B-different"}


# ---------------------------------------------------------------------------
# Media: relative path rewriting scheme
# ---------------------------------------------------------------------------

def test_relative_path_rewriting_scheme(tmp_path):
    anchor = _anchor(["Alpha"])
    plan = _confirmed_plan([anchor])
    raw_media_dir = tmp_path / "raw_media"
    (raw_media_dir / "media").mkdir(parents=True)
    (raw_media_dir / "media" / "diagram.png").write_bytes(b"bytes")

    sliced = SlicedDocument(
        preamble="",
        chunks=[_slice(anchor, "# Alpha\n\n![d](media/diagram.png)\n")],
    )
    output_dir = tmp_path / "canonical-content"
    package.build_canonical_package(plan, sliced, raw_media_dir, output_dir)

    content = (output_dir / "chunks" / f"{anchor.stable_key}.md").read_text()
    # Before: "media/diagram.png" (relative to the raw extraction dir).
    # After: "../media/diagram.png" (relative to chunks/<id>.md, since
    # chunks/ and media/ are sibling directories under canonical-content/).
    assert "![d](../media/diagram.png)" in content


# ---------------------------------------------------------------------------
# Media: URL-encoded paths and spaces
# ---------------------------------------------------------------------------

def test_url_encoded_and_space_containing_media_refs(tmp_path):
    anchor = _anchor(["Alpha"])
    plan = _confirmed_plan([anchor])
    raw_media_dir = tmp_path / "raw_media"
    (raw_media_dir / "media").mkdir(parents=True)
    (raw_media_dir / "media" / "image 1.png").write_bytes(b"bytes")

    sliced = SlicedDocument(
        preamble="",
        chunks=[_slice(anchor, "# Alpha\n\n![a](media/image%201.png)\n")],
    )
    output_dir = tmp_path / "canonical-content"
    package.build_canonical_package(plan, sliced, raw_media_dir, output_dir)

    assert (output_dir / "media" / "image 1.png").exists()
    content = (output_dir / "chunks" / f"{anchor.stable_key}.md").read_text()
    # Rewritten reference is encoded exactly once (no "%2520" double-encoding).
    assert "%2520" not in content
    assert "../media/image%201.png" in content


def test_alt_text_with_escaped_brackets_still_recognized_as_media_ref(tmp_path):
    """Regression test: alt text containing a markdown-escaped `]`
    (e.g. from Word captions with brackets which pandoc escapes as `\\[...\\]`)
    must not cause the alt-text regex class to stop matching early. The whole
    image reference must be recognized, copied into media/, and rewritten."""
    anchor = _anchor(["Alpha"])
    plan = _confirmed_plan([anchor])
    raw_media_dir = tmp_path / "raw_media"
    (raw_media_dir / "media").mkdir(parents=True)
    (raw_media_dir / "media" / "diagram.png").write_bytes(b"bytes")

    content_with_escaped_brackets = (
        "# Alpha\n\n"
        "![NOTE -- see Form 1 \\[Terminating a Sample Item\\], "
        "unless otherwise directed.](media/diagram.png)\n"
    )
    sliced = SlicedDocument(
        preamble="",
        chunks=[_slice(anchor, content_with_escaped_brackets)],
    )
    output_dir = tmp_path / "canonical-content"
    package.build_canonical_package(plan, sliced, raw_media_dir, output_dir)

    assert (output_dir / "media" / "diagram.png").exists()
    content = (output_dir / "chunks" / f"{anchor.stable_key}.md").read_text()
    assert "../media/diagram.png" in content
    assert "media/diagram.png)" not in content.replace("../media/diagram.png)", "")


# ---------------------------------------------------------------------------
# Media: reject absolute paths and .. traversal
# ---------------------------------------------------------------------------

def test_absolute_media_path_rejected(tmp_path):
    anchor = _anchor(["Alpha"])
    plan = _confirmed_plan([anchor])
    raw_media_dir = tmp_path / "raw_media"
    raw_media_dir.mkdir()

    sliced = SlicedDocument(
        preamble="",
        chunks=[_slice(anchor, "# Alpha\n\n![a](/etc/passwd)\n")],
    )
    output_dir = tmp_path / "canonical-content"
    with pytest.raises(package.MediaPathViolation):
        package.build_canonical_package(plan, sliced, raw_media_dir, output_dir)


def test_dotdot_traversal_media_path_rejected(tmp_path):
    anchor = _anchor(["Alpha"])
    plan = _confirmed_plan([anchor])
    raw_media_dir = tmp_path / "sub" / "raw_media"
    raw_media_dir.mkdir(parents=True)
    (tmp_path / "secret.txt").write_bytes(b"top secret")

    sliced = SlicedDocument(
        preamble="",
        chunks=[_slice(anchor, "# Alpha\n\n![a](../secret.txt)\n")],
    )
    output_dir = tmp_path / "canonical-content"
    with pytest.raises(package.MediaPathViolation):
        package.build_canonical_package(plan, sliced, raw_media_dir, output_dir)


def test_windows_drive_letter_absolute_path_rejected(tmp_path):
    anchor = _anchor(["Alpha"])
    plan = _confirmed_plan([anchor])
    raw_media_dir = tmp_path / "raw_media"
    raw_media_dir.mkdir()

    sliced = SlicedDocument(
        preamble="",
        chunks=[_slice(anchor, r"# Alpha\n\n![a](C:\Windows\System32\secret.png)\n")],
    )
    output_dir = tmp_path / "canonical-content"
    with pytest.raises(package.MediaPathViolation):
        package.build_canonical_package(plan, sliced, raw_media_dir, output_dir)


def test_windows_unc_path_rejected(tmp_path):
    anchor = _anchor(["Alpha"])
    plan = _confirmed_plan([anchor])
    raw_media_dir = tmp_path / "raw_media"
    raw_media_dir.mkdir()

    sliced = SlicedDocument(
        preamble="",
        chunks=[_slice(anchor, r"# Alpha\n\n![a](\\server\share\secret.png)\n")],
    )
    output_dir = tmp_path / "canonical-content"
    with pytest.raises(package.MediaPathViolation):
        package.build_canonical_package(plan, sliced, raw_media_dir, output_dir)


def test_windows_backslash_traversal_rejected(tmp_path):
    anchor = _anchor(["Alpha"])
    plan = _confirmed_plan([anchor])
    raw_media_dir = tmp_path / "sub" / "raw_media"
    raw_media_dir.mkdir(parents=True)

    sliced = SlicedDocument(
        preamble="",
        chunks=[_slice(anchor, r"# Alpha\n\n![a](..\..\secret.png)\n")],
    )
    output_dir = tmp_path / "canonical-content"
    with pytest.raises(package.MediaPathViolation):
        package.build_canonical_package(plan, sliced, raw_media_dir, output_dir)


# ---------------------------------------------------------------------------
# Media: unsupported legacy media remaining after conversion
# ---------------------------------------------------------------------------

def test_unconverted_legacy_media_remaining_is_rejected(tmp_path):
    anchor = _anchor(["Alpha"])
    plan = _confirmed_plan([anchor])
    raw_media_dir = tmp_path / "raw_media"
    raw_media_dir.mkdir()
    # Simulate emf_convert.convert_legacy_media having failed to convert
    # (or never having run): the .emf file is still on disk and still
    # referenced -- this must be surfaced, not silently packaged.
    (raw_media_dir / "legacy1.emf").write_bytes(b"not-a-real-emf-but-present")

    sliced = SlicedDocument(
        preamble="",
        chunks=[_slice(anchor, "# Alpha\n\n![d](media/legacy1.emf)\n")],
    )
    output_dir = tmp_path / "canonical-content"
    with pytest.raises(package.UnsupportedLegacyMediaError):
        package.build_canonical_package(plan, sliced, raw_media_dir, output_dir)


def test_missing_media_file_is_rejected(tmp_path):
    anchor = _anchor(["Alpha"])
    plan = _confirmed_plan([anchor])
    raw_media_dir = tmp_path / "raw_media"
    raw_media_dir.mkdir()

    sliced = SlicedDocument(
        preamble="",
        chunks=[_slice(anchor, "# Alpha\n\n![d](media/does-not-exist.png)\n")],
    )
    output_dir = tmp_path / "canonical-content"
    with pytest.raises(package.UnsupportedLegacyMediaError):
        package.build_canonical_package(plan, sliced, raw_media_dir, output_dir)


# ---------------------------------------------------------------------------
# build_grouped_canonical_package (Task 17-topic-grouping, Task 5)
# ---------------------------------------------------------------------------

def _two_topic_sliced_document():
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
    return plan, sliced


def test_build_grouped_canonical_package_produces_one_file_per_topic(tmp_path):
    plan, sliced = _two_topic_sliced_document()
    manifest = package.build_grouped_canonical_package(
        plan, sliced, raw_media_dir=tmp_path / "raw_media", output_dir=tmp_path / "out"
    )
    assert manifest.strategy == "grouped"
    assert manifest.chunk_count == 2
    assert {c.source_heading_path[0] for c in manifest.chunks} == {"File Access", "Overview"}


def test_grouped_topic_content_preserves_all_anchor_content_losslessly(tmp_path):
    plan, sliced = _two_topic_sliced_document()
    manifest = package.build_grouped_canonical_package(
        plan, sliced, raw_media_dir=tmp_path / "raw_media", output_dir=tmp_path / "out"
    )
    file_access_chunk = next(
        c for c in manifest.chunks if c.source_heading_path == ["File Access"]
    )
    combined = (tmp_path / "out" / file_access_chunk.content_file).read_text()
    for chunk_slice in sliced.chunks:
        if chunk_slice.anchor.source_heading_path[0] == "File Access":
            assert chunk_slice.content.strip() in combined


def test_grouped_chunk_metadata_lists_every_folded_anchor(tmp_path):
    plan, sliced = _two_topic_sliced_document()
    manifest = package.build_grouped_canonical_package(
        plan, sliced, raw_media_dir=tmp_path / "raw_media", output_dir=tmp_path / "out"
    )
    file_access_chunk = next(
        c for c in manifest.chunks if c.source_heading_path == ["File Access"]
    )
    meta = contracts.ChunkMetadata.from_dict(
        json.loads((tmp_path / "out" / file_access_chunk.metadata_file).read_text())
    )
    anchor_keys = {a["stable_key"] for a in meta.anchors}
    expected_keys = {
        s.anchor.stable_key for s in sliced.chunks
        if s.anchor.source_heading_path[0] == "File Access"
    }
    assert anchor_keys == expected_keys


def test_grouped_package_writes_publication_map(tmp_path):
    plan, sliced = _two_topic_sliced_document()
    package.build_grouped_canonical_package(
        plan, sliced, raw_media_dir=tmp_path / "raw_media", output_dir=tmp_path / "out"
    )
    pub_map_path = tmp_path / "out" / "publication-map.json"
    assert pub_map_path.exists()
    data = json.loads(pub_map_path.read_text())
    assert len(data["entries"]) == 2
    assert data["entries"][0]["order"] == 0


def test_grouped_package_identity_is_not_double_prefixed(tmp_path):
    anchor = _anchor(["Alpha"], level=1)
    plan = _confirmed_plan([anchor], strategy="grouped")
    raw_media_dir = tmp_path / "raw_media"
    raw_media_dir.mkdir()
    sliced = SlicedDocument(
        preamble="", chunks=[_slice(anchor, "# Alpha\n\nBody text.\n")]
    )
    output_dir = tmp_path / "canonical-content"
    package.build_grouped_canonical_package(plan, sliced, raw_media_dir, output_dir)

    pub_map_data = json.loads((output_dir / "publication-map.json").read_text())
    manifest_data = json.loads((output_dir / "manifest.json").read_text())
    assert pub_map_data["package_identity"] == manifest_data["plan_id"]
    assert not pub_map_data["package_identity"].startswith("sha256:sha256:")


def test_grouped_publication_map_chunk_id_is_not_a_path(tmp_path):
    anchor = _anchor(["Alpha"], level=1)
    plan = _confirmed_plan([anchor], strategy="grouped")
    raw_media_dir = tmp_path / "raw_media"
    raw_media_dir.mkdir()
    sliced = SlicedDocument(
        preamble="", chunks=[_slice(anchor, "# Alpha\n\nBody text.\n")]
    )
    output_dir = tmp_path / "canonical-content"
    package.build_grouped_canonical_package(plan, sliced, raw_media_dir, output_dir)

    pub_map_data = json.loads((output_dir / "publication-map.json").read_text())
    entry = pub_map_data["entries"][0]
    # chunk_id must be the real chunk identifier, never a "chunks/....md" path.
    assert not entry["chunk_id"].startswith("chunks/")
    assert not entry["chunk_id"].endswith(".md")
    assert entry["chunk_id"] == entry["topic_id"]  # equal-in-practice for the grouped producer today
    assert "parent_topic_id" not in entry


def test_grouped_every_anchor_assigned_exactly_once(tmp_path):
    plan, sliced = _two_topic_sliced_document()
    manifest = package.build_grouped_canonical_package(
        plan, sliced, raw_media_dir=tmp_path / "raw_media", output_dir=tmp_path / "out"
    )
    all_anchor_keys = []
    for chunk in manifest.chunks:
        meta = contracts.ChunkMetadata.from_dict(
            json.loads((tmp_path / "out" / chunk.metadata_file).read_text())
        )
        all_anchor_keys.extend(a["stable_key"] for a in meta.anchors)
    source_keys = [s.anchor.stable_key for s in sliced.chunks]
    assert sorted(all_anchor_keys) == sorted(source_keys)
    assert len(all_anchor_keys) == len(set(all_anchor_keys))


# ---------------------------------------------------------------------------
# Confirmed topic-root set consumption (Task 18 mixed-level logical-root
# detection): convert must use the plan's confirmed_topic_roots as-is,
# not independently recompute grouping from heading levels.
# ---------------------------------------------------------------------------

def test_grouped_package_uses_confirmed_topic_roots_for_mixed_level_document(tmp_path):
    # A "File Access" (Heading 2) / "How to Seal a File" (Heading 3) /
    # "Overview" (Heading 1) sequence: the default heuristic alone would
    # treat "How to Seal a File" (level 2) as a child (2 > current root 1
    # once "Overview" -- wait, order here is File Access first). What
    # matters is that the *confirmed* root set, not a level==1-only
    # assumption, decides which headings are roots.
    file_access = _anchor(["File Access"], level=2)
    how_to_seal = _anchor(["File Access", "How to Seal a File"], level=3)
    overview = _anchor(["Overview"], level=1)
    confirmed_topic_roots = [
        {"source_heading_path": ["File Access"], "occurrence": 1},
        {"source_heading_path": ["Overview"], "occurrence": 1},
    ]
    plan = _confirmed_plan(
        [file_access, how_to_seal, overview],
        strategy="grouped",
        confirmed_topic_roots=confirmed_topic_roots,
    )
    sliced = SlicedDocument(
        preamble="",
        chunks=[
            _slice(file_access, "## File Access\n\nIntro to file access.\n"),
            _slice(how_to_seal, "### How to Seal a File\n\nSteps to seal a file.\n"),
            _slice(overview, "# Overview\n\nOverview body.\n"),
        ],
    )
    manifest = package.build_grouped_canonical_package(
        plan, sliced, raw_media_dir=tmp_path / "raw_media", output_dir=tmp_path / "out"
    )
    assert manifest.chunk_count == 2
    assert {c.source_heading_path[0] for c in manifest.chunks} == {"File Access", "Overview"}


def test_grouped_package_raises_when_confirmed_roots_no_longer_reconcile(tmp_path):
    # A confirmed root set referencing a heading path/occurrence that no
    # longer exists in the current headings must fail loudly, not
    # silently fall back to recomputing a (possibly different) heuristic.
    file_access = _anchor(["File Access"], level=1)
    confirmed_topic_roots = [
        {"source_heading_path": ["Some Other Heading"], "occurrence": 1},
    ]
    plan = _confirmed_plan(
        [file_access], strategy="grouped", confirmed_topic_roots=confirmed_topic_roots
    )
    sliced = SlicedDocument(
        preamble="",
        chunks=[_slice(file_access, "# File Access\n\nIntro.\n")],
    )
    with pytest.raises(topic_grouping.UnassignableHeadingError):
        package.build_grouped_canonical_package(
            plan, sliced, raw_media_dir=tmp_path / "raw_media", output_dir=tmp_path / "out"
        )
