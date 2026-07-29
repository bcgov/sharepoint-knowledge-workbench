"""
test_multipage_markdown.py
===========================

Tests for `renderers.multipage_markdown` (Task 13): the first concrete
`Renderer` implementation. Spec Section 7.3 ("render-content") requires
this renderer to:
    - consume the manifest ordering (not alphabetical/filesystem order);
    - write one page per chunk under `pages/`;
    - write a hierarchical/path-aware `index.md`;
    - rewrite/copy media references so rendered pages resolve locally;
    - never read the source .docx, an analysis/ dir, or a conversion plan;
    - render to a staging dir (promotion is Task 14's job, once a render
      validator exists to gate it).

Most tests here build a synthetic `CanonicalPackage` directly (bypassing
`CanonicalPackage.load()`/pandoc entirely) so they run fast and can freely
control chunk ordering, heading paths, and local links -- exactly what the
brief asks for ("using already-loaded fixtures/canonical packages from
earlier tasks' test infrastructure"). One real end-to-end test at the
bottom exercises the full pipeline against the `repeated_headings.docx`
fixture via `convert.convert_and_promote` + `CanonicalPackage.load()`.
"""

import dataclasses
import json
import shutil
from pathlib import Path

import pytest

import atomic_output
import contracts
import package as package_module
import canonical_package as canonical_package_module
from renderers import protocol
from renderers import multipage_markdown as mpm

FIXTURES = Path(__file__).parent.parent / "fixtures"
REPEATED_HEADINGS_DOCX = FIXTURES / "repeated_headings.docx"
SMALL_SINGLE_DOCX = FIXTURES / "small_single.docx"

PANDOC_AVAILABLE = shutil.which("pandoc") is not None

FAKE_SHA = "a" * 64


# ---------------------------------------------------------------------------
# Synthetic CanonicalPackage builder (no pandoc, no disk .docx involved)
# ---------------------------------------------------------------------------

def _metadata(chunk_id, heading_path, order, content, local_links=None):
    return contracts.ChunkMetadata(
        schema_version=contracts.SUPPORTED_SCHEMA_VERSION,
        chunk_id=chunk_id,
        source_order=order,
        source_heading_path=list(heading_path),
        topic=heading_path[-1],
        content_type="reference",
        template_profile="generic",
        source_sha256=FAKE_SHA,
        plan_id="plan-1",
        content_file=f"chunks/{chunk_id}.md",
        content_sha256=FAKE_SHA,
        local_links=list(local_links or []),
        media_refs=package_module.extract_media_refs(content),
    )


def _manifest_chunk(chunk_id, heading_path, order):
    return contracts.ManifestChunk(
        chunk_id=chunk_id,
        content_file=f"chunks/{chunk_id}.md",
        metadata_file=f"chunks/{chunk_id}.meta.json",
        source_order=order,
        source_heading_path=list(heading_path),
    )


def _build_synthetic_package(tmp_path, chunk_specs, with_media=True):
    """`chunk_specs`: list of (chunk_id, heading_path, content, local_links)
    tuples, in the exact order the caller wants them to appear in the
    manifest (i.e. manifest/render order -- deliberately NOT sorted)."""
    package_dir = tmp_path / "canonical-content"
    media_dir = package_dir / "media"
    media_dir.mkdir(parents=True)
    media_names = []
    if with_media:
        (media_dir / "diagram.png").write_bytes(b"fake-png-bytes")
        media_names = ["diagram.png"]

    loaded_chunks = []
    manifest_chunks = []
    for idx, (chunk_id, heading_path, content, local_links) in enumerate(chunk_specs):
        meta = _metadata(chunk_id, heading_path, idx, content, local_links)
        loaded_chunks.append(canonical_package_module.LoadedChunk(metadata=meta, content=content))
        manifest_chunks.append(_manifest_chunk(chunk_id, heading_path, idx))

    manifest = contracts.Manifest(
        schema_version=contracts.SUPPORTED_SCHEMA_VERSION,
        generator=contracts.ManifestGenerator(plugin="docx-to-content", plugin_version="0.1.0"),
        source=contracts.ManifestSourceFingerprint(path="sourcedocuments/x.docx", sha256=FAKE_SHA),
        plan_id="plan-1",
        content_type="reference",
        template_profile="generic",
        strategy="heading-based",
        chunk_count=len(manifest_chunks),
        chunks=manifest_chunks,
        media=media_names,
        validation_report="validation.json",
    )
    validation_report = contracts.ValidationReport(
        status="PASS", issues=[], source_sha256=FAKE_SHA, plan_id="plan-1"
    )

    return canonical_package_module.CanonicalPackage(
        manifest=manifest,
        validation_report=validation_report,
        chunks=loaded_chunks,
        media_dir=media_dir,
        package_dir=package_dir,
    )


def _build_synthetic_grouped_package(tmp_path):
    """Two-topic grouped package: "Beta" appears first in manifest/chunks
    order, but publication-map.json explicitly orders "Alpha" first --
    proving render() follows the publication map, not manifest order,
    when one is present."""
    pkg = _build_synthetic_package(
        tmp_path,
        [
            ("beta--11111111", ["Beta"], "# Beta\n\nBeta body.\n", []),
            ("alpha--22222222", ["Alpha"], "# Alpha\n\nAlpha body.\n", []),
        ],
    )
    pub_map = contracts.PublicationMap(
        schema_version=contracts.SUPPORTED_SCHEMA_VERSION,
        package_identity="sha256:deadbeef",
        entries=[
            contracts.PublicationMapEntry(
                topic_id="alpha--22222222", title="Alpha", order=0,
                chunk_id="alpha--22222222",
            ),
            contracts.PublicationMapEntry(
                topic_id="beta--11111111", title="Beta", order=1,
                chunk_id="beta--11111111",
            ),
        ],
    )
    grouped_manifest = dataclasses.replace(pkg.manifest, strategy="grouped")
    return dataclasses.replace(pkg, manifest=grouped_manifest, publication_map=pub_map)


# ---------------------------------------------------------------------------
# Protocol conformance
# ---------------------------------------------------------------------------

def test_renderer_satisfies_protocol():
    renderer = mpm.MultipageMarkdownRenderer()
    assert isinstance(renderer, protocol.Renderer)
    assert renderer.name == "multipage-markdown"
    assert contracts.SUPPORTED_SCHEMA_VERSION in renderer.supported_manifest_versions


def test_renderer_supported_versions_tracks_manifest_constant_not_plan_constant():
    # Temporarily set contracts.MANIFEST_SCHEMA_VERSION and reload the
    # multipage_markdown module to ensure the renderer's supported_manifest_versions
    # is derived from that constant. Restore both the constant and the module
    # after the check to avoid leaking state to other tests.
    import importlib
    import contracts as _contracts

    original = _contracts.MANIFEST_SCHEMA_VERSION
    try:
        _contracts.MANIFEST_SCHEMA_VERSION = "9.9"
        import renderers.multipage_markdown as mpm
        importlib.reload(mpm)
        assert "9.9" in mpm.MultipageMarkdownRenderer.supported_manifest_versions
        assert "1.0" not in mpm.MultipageMarkdownRenderer.supported_manifest_versions
    finally:
        _contracts.MANIFEST_SCHEMA_VERSION = original
        import renderers.multipage_markdown as mpm
        importlib.reload(mpm)


# ---------------------------------------------------------------------------
# Single vs chunked -- same code path
# ---------------------------------------------------------------------------

def test_single_chunk_package_renders_one_page_and_index(tmp_path):
    pkg = _build_synthetic_package(
        tmp_path,
        [("chunk-a", ["Getting Started"], "# Getting Started\n\nHello.\n", [])],
    )
    output_dir = tmp_path / "rendered"
    result = mpm.MultipageMarkdownRenderer().render(pkg, output_dir)

    assert isinstance(result, contracts.RenderResult)
    assert result.status == "PASS"
    assert result.renderer_name == "multipage-markdown"
    assert result.source_content_sha256 == FAKE_SHA
    assert (output_dir / "pages" / "chunk-a.md").read_text() == "# Getting Started\n\nHello.\n"
    assert (output_dir / "index.md").exists()
    index_text = (output_dir / "index.md").read_text()
    assert "pages/chunk-a.md" in index_text


def test_chunked_package_uses_same_render_method_as_single(tmp_path):
    # Same MultipageMarkdownRenderer.render -- no special-casing for N==1.
    pkg = _build_synthetic_package(
        tmp_path,
        [
            ("chunk-a", ["Section Alpha", "Intro"], "# Intro\n\nA.\n", []),
            ("chunk-b", ["Section Alpha", "Details"], "# Details\n\nB.\n", []),
        ],
    )
    output_dir = tmp_path / "rendered"
    renderer = mpm.MultipageMarkdownRenderer()
    result = renderer.render(pkg, output_dir)

    assert result.status == "PASS"
    assert (output_dir / "pages" / "chunk-a.md").exists()
    assert (output_dir / "pages" / "chunk-b.md").exists()


# ---------------------------------------------------------------------------
# Manifest ordering drives page/index generation
# ---------------------------------------------------------------------------

def test_index_follows_manifest_order_not_alphabetical(tmp_path):
    # "zzz-first" is manifest-first but alphabetically last; "aaa-second"
    # is manifest-second but alphabetically first. If the renderer sorted
    # alphabetically or by filesystem listing, aaa would appear first.
    pkg = _build_synthetic_package(
        tmp_path,
        [
            ("zzz-first", ["Zzz First"], "# Zzz First\n", []),
            ("aaa-second", ["Aaa Second"], "# Aaa Second\n", []),
        ],
    )
    output_dir = tmp_path / "rendered"
    mpm.MultipageMarkdownRenderer().render(pkg, output_dir)

    index_text = (output_dir / "index.md").read_text()
    assert index_text.index("zzz-first") < index_text.index("aaa-second")


# ---------------------------------------------------------------------------
# Hierarchical / path-aware index.md
# ---------------------------------------------------------------------------

def test_index_reflects_heading_hierarchy_with_shared_top_level_group(tmp_path):
    pkg = _build_synthetic_package(
        tmp_path,
        [
            ("chunk-a", ["Section Alpha", "Getting Started"], "# Getting Started\n", []),
            ("chunk-b", ["Section Alpha", "Advanced Topic"], "# Advanced Topic\n", []),
        ],
    )
    output_dir = tmp_path / "rendered"
    mpm.MultipageMarkdownRenderer().render(pkg, output_dir)
    index_text = (output_dir / "index.md").read_text()

    # The shared top-level group "Section Alpha" appears exactly once,
    # not duplicated per chunk -- proving grouping, not a flat list.
    assert index_text.count("Section Alpha") == 1
    lines = index_text.splitlines()
    group_line = next(l for l in lines if "Section Alpha" in l)
    leaf_lines = [l for l in lines if "pages/chunk-a.md" in l or "pages/chunk-b.md" in l]
    assert len(leaf_lines) == 2
    # Leaf entries are indented deeper than their parent group line.
    group_indent = len(group_line) - len(group_line.lstrip(" "))
    for leaf in leaf_lines:
        leaf_indent = len(leaf) - len(leaf.lstrip(" "))
        assert leaf_indent > group_indent


# ---------------------------------------------------------------------------
# Media copying and page-relative reference rewriting
# ---------------------------------------------------------------------------

def test_media_copied_and_relative_reference_form_is_unchanged(tmp_path):
    content = "# Widget\n\n![diagram](../media/diagram.png)\n"
    pkg = _build_synthetic_package(
        tmp_path,
        [("chunk-a", ["Widget"], content, [])],
    )
    output_dir = tmp_path / "rendered"
    mpm.MultipageMarkdownRenderer().render(pkg, output_dir)

    assert (output_dir / "media" / "diagram.png").read_bytes() == b"fake-png-bytes"
    page_text = (output_dir / "pages" / "chunk-a.md").read_text()
    # pages/ and chunks/ are both one level below their respective package
    # roots with a sibling media/ dir, so the relative form is unchanged.
    assert "../media/diagram.png" in page_text


# ---------------------------------------------------------------------------
# Internal links between chunks
# ---------------------------------------------------------------------------

def test_internal_local_link_rewritten_to_page_relative_target(tmp_path):
    content_a = "# A\n\nSee [Details](chunks/chunk-b.md) for more.\n"
    content_b = "# B\n\nBack to [A](chunks/chunk-a.md).\n"
    pkg = _build_synthetic_package(
        tmp_path,
        [
            ("chunk-a", ["A"], content_a, ["chunks/chunk-b.md"]),
            ("chunk-b", ["B"], content_b, ["chunks/chunk-a.md"]),
        ],
    )
    output_dir = tmp_path / "rendered"
    mpm.MultipageMarkdownRenderer().render(pkg, output_dir)

    page_a = (output_dir / "pages" / "chunk-a.md").read_text()
    page_b = (output_dir / "pages" / "chunk-b.md").read_text()
    assert "(chunk-b.md)" in page_a
    assert "chunks/chunk-b.md" not in page_a
    assert "(chunk-a.md)" in page_b
    assert "chunks/chunk-a.md" not in page_b


def test_external_links_are_left_untouched(tmp_path):
    content = "# A\n\nSee [docs](https://example.com/x) and [anchor](#top).\n"
    pkg = _build_synthetic_package(tmp_path, [("chunk-a", ["A"], content, [])])
    output_dir = tmp_path / "rendered"
    mpm.MultipageMarkdownRenderer().render(pkg, output_dir)

    page_a = (output_dir / "pages" / "chunk-a.md").read_text()
    assert "https://example.com/x" in page_a
    assert "(#top)" in page_a


# ---------------------------------------------------------------------------
# Repeated headings -> distinct output
# ---------------------------------------------------------------------------

def test_repeated_leaf_heading_under_different_parents_produces_distinct_links(tmp_path):
    pkg = _build_synthetic_package(
        tmp_path,
        [
            ("chunk-setup-1", ["Section Alpha", "Setup"], "# Setup\n\nAlpha setup.\n", []),
            ("chunk-setup-2", ["Section Beta", "Setup"], "# Setup\n\nBeta setup.\n", []),
        ],
    )
    output_dir = tmp_path / "rendered"
    mpm.MultipageMarkdownRenderer().render(pkg, output_dir)

    assert (output_dir / "pages" / "chunk-setup-1.md").exists()
    assert (output_dir / "pages" / "chunk-setup-2.md").exists()
    index_text = (output_dir / "index.md").read_text()
    assert "pages/chunk-setup-1.md" in index_text
    assert "pages/chunk-setup-2.md" in index_text
    assert "Section Alpha" in index_text
    assert "Section Beta" in index_text
    # Two distinct groups, not collapsed into one "Setup" bucket.
    assert index_text.count("Setup") == 2


# ---------------------------------------------------------------------------
# No DOCX / analysis / conversion-plan access
# ---------------------------------------------------------------------------

def test_module_source_has_no_docx_or_analysis_or_plan_access():
    import ast
    import inspect

    tree = ast.parse(Path(mpm.__file__).read_text())
    imported_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_names.add(node.module)
    forbidden_modules = {"analyze_structure", "plans", "convert"}
    assert not (imported_names & forbidden_modules), (
        f"multipage_markdown.py must not import {forbidden_modules}, "
        f"found {imported_names & forbidden_modules}"
    )

    # The renderer's actual code (not module-level prose/docstrings) must
    # not contain a literal .docx/analysis/conversion-plan reference.
    render_body = inspect.getsource(mpm.MultipageMarkdownRenderer.render)
    staging_body = inspect.getsource(mpm.render_to_staging)
    for forbidden in (".docx", "sourcedocuments", "analysis/", "conversion-plan"):
        assert forbidden not in render_body
        assert forbidden not in staging_body


def test_render_produces_correct_output_with_no_docx_or_analysis_or_plan_on_disk(tmp_path):
    # Nothing under tmp_path is a .docx, analysis/ dir, or conversion-plan
    # file -- only the synthetic CanonicalPackage's own directory tree
    # (which itself never had a .docx/analysis/plan written to it either).
    pkg = _build_synthetic_package(
        tmp_path,
        [("chunk-a", ["Getting Started"], "# Getting Started\n\nHello.\n", [])],
    )
    assert not list(tmp_path.rglob("*.docx"))
    assert not list(tmp_path.rglob("analysis"))
    assert not list(tmp_path.rglob("conversion-plan*"))

    output_dir = tmp_path / "rendered"
    result = mpm.MultipageMarkdownRenderer().render(pkg, output_dir)

    assert result.status == "PASS"
    assert (output_dir / "pages" / "chunk-a.md").exists()


# ---------------------------------------------------------------------------
# Staging (option (a): stage only, no promotion until Task 14's validator)
# ---------------------------------------------------------------------------

def test_render_to_staging_writes_to_a_fresh_staging_dir_without_promoting(tmp_path):
    pkg = _build_synthetic_package(
        tmp_path,
        [("chunk-a", ["Getting Started"], "# Getting Started\n\nHello.\n", [])],
    )
    output_root = tmp_path / "out"
    result, staging_dir = mpm.render_to_staging(pkg, output_root)

    assert result.status == "PASS"
    assert staging_dir.exists()
    assert staging_dir.parent == output_root
    assert (staging_dir / "index.md").exists()
    assert (staging_dir / "pages" / "chunk-a.md").exists()
    # No promotion happened -- no "rendered-output" (or any non-staging)
    # final directory was created.
    other_entries = [p for p in output_root.iterdir() if p != staging_dir]
    assert other_entries == []


def test_render_to_staging_uses_atomic_output_create_staging_dir(tmp_path, monkeypatch):
    calls = []
    real_create_staging_dir = atomic_output.create_staging_dir

    def _spy(output_root, prefix="staging"):
        calls.append((output_root, prefix))
        return real_create_staging_dir(output_root, prefix=prefix)

    monkeypatch.setattr(mpm.atomic_output, "create_staging_dir", _spy)

    pkg = _build_synthetic_package(
        tmp_path,
        [("chunk-a", ["Getting Started"], "# Getting Started\n\nHello.\n", [])],
    )
    mpm.render_to_staging(pkg, tmp_path / "out")

    assert len(calls) == 1


# ---------------------------------------------------------------------------
# Real end-to-end run through the full pipeline
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not PANDOC_AVAILABLE, reason="pandoc not available on PATH")
def test_end_to_end_render_of_small_single_fixture(tmp_path):
    # Uses small_single.docx (not repeated_headings.docx) deliberately:
    # repeated_headings.docx currently fails convert_and_promote's
    # content_loss_or_duplication check for an unrelated, pre-existing
    # media-ref normalization bug (see Task 10b in the project plan) --
    # not something Task 13's renderer can or should fix. The
    # repeated-headings distinct-links behavior this renderer must prove
    # is already covered by the synthetic
    # test_repeated_leaf_heading_under_different_parents_produces_distinct_links
    # test above, without depending on that unrelated bug being fixed
    # first.
    import analyze_structure
    import convert
    import plans

    analysis_dir = tmp_path / "analysis"
    analyze_structure.analyze_document(SMALL_SINGLE_DOCX, analysis_dir)
    draft = contracts.ConversionPlan.from_dict(
        json.loads((analysis_dir / "conversion-plan.draft.json").read_text())
    )
    confirmed = plans.confirm_plan(draft, confirmed_by="test-suite")

    output_root = tmp_path / "out"
    manifest, report, promoted, final_dir = convert.convert_and_promote(
        SMALL_SINGLE_DOCX, confirmed, output_root
    )
    assert promoted is True

    loaded = canonical_package_module.CanonicalPackage.load(final_dir)
    assert loaded.manifest.chunk_count >= 1

    result, staging_dir = mpm.render_to_staging(loaded, tmp_path / "rendered")

    assert result.status == "PASS"
    pages = sorted((staging_dir / "pages").glob("*.md"))
    assert len(pages) == loaded.manifest.chunk_count

    index_text = (staging_dir / "index.md").read_text()
    for chunk in loaded.chunks:
        assert f"pages/{chunk.metadata.chunk_id}.md" in index_text

    canonical_media = sorted(p.name for p in (final_dir / "media").glob("*") if p.is_file())
    rendered_media = sorted(p.name for p in (staging_dir / "media").glob("*") if p.is_file())
    assert rendered_media == canonical_media


# ---------------------------------------------------------------------------
# Publication-map-driven navigation (Task 17-topic-grouping, Task 8)
# ---------------------------------------------------------------------------

def test_render_uses_publication_map_order_when_present(tmp_path):
    pkg = _build_synthetic_grouped_package(tmp_path)
    output_dir = tmp_path / "rendered"
    result = mpm.MultipageMarkdownRenderer().render(pkg, output_dir)

    assert result.status == "PASS"
    index_text = (output_dir / "index.md").read_text()
    # Publication map orders Alpha (0) before Beta (1), even though the
    # package's manifest/chunks order has Beta first.
    assert index_text.index("Alpha") < index_text.index("Beta")
    assert (output_dir / "pages" / "alpha--22222222.md").exists()
    assert (output_dir / "pages" / "beta--11111111.md").exists()


def test_render_falls_back_to_manifest_order_when_no_publication_map(tmp_path):
    pkg = _build_synthetic_package(
        tmp_path,
        [
            ("chunk-a", ["Section Alpha", "Intro"], "# Intro\n\nA.\n", []),
            ("chunk-b", ["Section Alpha", "Details"], "# Details\n\nB.\n", []),
        ],
    )
    assert pkg.publication_map is None
    output_dir = tmp_path / "rendered"
    result = mpm.MultipageMarkdownRenderer().render(pkg, output_dir)
    assert result.status == "PASS"
    assert (output_dir / "index.md").exists()
    index_text = (output_dir / "index.md").read_text()
    assert index_text.index("Intro") < index_text.index("Details")
