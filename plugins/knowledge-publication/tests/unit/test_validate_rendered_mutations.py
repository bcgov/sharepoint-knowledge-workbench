"""
test_validate_rendered_mutations.py
======================================

Layer-3 mutation suite (Phase 2, spec Section 5.1): validate_rendered_output
must be proven to catch corruption in the staged rendered-output directory
-- an omitted-but-linked page, a page whose index link is wrong, and a
validation report whose lineage fields don't match the package it claims
to describe (the general form of the image239 lesson: a report that lies
about what it checked).
"""

import json

import pytest

from renderers import validate_rendered
from test_validate_rendered import _build_synthetic_package, _staged_render


TWO_CHUNK_SPECS = [
    ("chunk-a", ["A"], "# A\n\nSee [B](chunks/chunk-b.md).\n", ["chunks/chunk-b.md"]),
    ("chunk-b", ["B"], "# B\n\n![diagram](../media/diagram.png)\n", []),
]


def test_index_omitting_an_existing_page_is_detected(tmp_path):
    """Neither existing check catches this: _check_index_links only checks
    links that ARE present in index.md for brokenness, and
    _check_page_completeness only checks that every chunk has a page and
    every page has a chunk -- neither checks that index.md actually links
    every page that exists. This is a real gap this task closes with a new
    check, _check_index_completeness (added to validate_rendered.py in
    Step 3 below), not a hypothetical one."""
    pkg = _build_synthetic_package(tmp_path, TWO_CHUNK_SPECS)
    _, rendered_dir = _staged_render(tmp_path, pkg)
    index_path = rendered_dir / "index.md"
    pages_dir = rendered_dir / "pages"
    existing_page_stems = {p.stem for p in pages_dir.glob("*.md")}
    assert existing_page_stems, "fixture must have produced at least one page"

    # Remove every line in index.md that links to one specific existing
    # page, leaving that page still present on disk but unlinked.
    target_stem = sorted(existing_page_stems)[0]
    lines = index_path.read_text().splitlines()
    kept = [l for l in lines if f"pages/{target_stem}.md" not in l]
    index_path.write_text("\n".join(kept))

    report = validate_rendered.validate_rendered_output(rendered_dir, pkg)

    assert report.status == "FAIL"
    assert any(i.code == "page_not_linked_from_index" for i in report.issues)


def test_source_content_staleness_is_detected(tmp_path):
    # Round-3 review (GPT 5.6 blocking #7) caught that an earlier draft
    # named this test "wrong_manifest_version_claim" while it actually
    # mutates source_content_sha256 -- a source-staleness case, not a
    # renderer manifest-version-compatibility case. Renamed to match what
    # it actually tests; the real manifest-version-compatibility case is
    # test_renderer_rejects_unsupported_manifest_version below.
    pkg = _build_synthetic_package(tmp_path, TWO_CHUNK_SPECS)
    _, rendered_dir = _staged_render(tmp_path, pkg)
    render_result_path = rendered_dir / "render-result.json"
    data = json.loads(render_result_path.read_text())
    data["source_content_sha256"] = "f" * 64
    render_result_path.write_text(json.dumps(data))

    report = validate_rendered.validate_rendered_output(rendered_dir, pkg)

    assert report.status == "FAIL"
    assert any(i.code == "source_content_stale" for i in report.issues)


def test_renderer_rejects_unsupported_manifest_version(tmp_path):
    """The actual 'wrong manifest version' case: protocol.dispatch_render
    must refuse to render a package whose manifest.schema_version is not
    in the renderer's own supported_manifest_versions -- this is a
    dispatch-time check (renderers/protocol.py), not a rendered-output
    validation check, so it's tested at the dispatch layer directly."""
    import dataclasses

    from renderers import protocol
    from renderers.multipage_markdown import MultipageMarkdownRenderer

    pkg = _build_synthetic_package(tmp_path, TWO_CHUNK_SPECS)
    unsupported_manifest = dataclasses.replace(pkg.manifest, schema_version="9.9")
    unsupported_package = dataclasses.replace(pkg, manifest=unsupported_manifest)

    with pytest.raises(protocol.UnsupportedManifestVersionError):
        protocol.dispatch_render(MultipageMarkdownRenderer(), unsupported_package, tmp_path / "out")


def test_page_content_diverging_from_source_chunk_is_detected(tmp_path):
    pkg = _build_synthetic_package(tmp_path, TWO_CHUNK_SPECS)
    _, rendered_dir = _staged_render(tmp_path, pkg)
    page_path = next((rendered_dir / "pages").glob("*.md"))
    page_path.write_text(page_path.read_text() + "\ntampered after render\n")

    report = validate_rendered.validate_rendered_output(rendered_dir, pkg)

    assert report.status == "FAIL"
    assert any(i.code == "page_content_not_traceable" for i in report.issues)


# Adversarial cases added in Step 4

def test_index_completeness_survives_escaped_bracket_in_link_text(tmp_path):
    pkg = _build_synthetic_package(tmp_path, TWO_CHUNK_SPECS)
    _, rendered_dir = _staged_render(tmp_path, pkg)
    index_path = rendered_dir / "index.md"
    pages_dir = rendered_dir / "pages"
    target_stem = sorted(p.stem for p in pages_dir.glob("*.md"))[0]

    lines = index_path.read_text().splitlines()
    rewritten = []
    for line in lines:
        if f"pages/{target_stem}.md" in line:
            rewritten.append(f"- [Section \\[One\\]](pages/{target_stem}.md)")
        else:
            rewritten.append(line)
    index_path.write_text("\n".join(rewritten))

    report = validate_rendered.validate_rendered_output(rendered_dir, pkg)

    assert not any(i.code == "page_not_linked_from_index" for i in report.issues), (
        "escaped bracket in link text must not cause a correctly-linked "
        "page to be reported as unlinked"
    )


def test_index_completeness_survives_url_encoded_page_filename(tmp_path):
    pkg = _build_synthetic_package(tmp_path, TWO_CHUNK_SPECS)
    _, rendered_dir = _staged_render(tmp_path, pkg)
    index_path = rendered_dir / "index.md"
    pages_dir = rendered_dir / "pages"
    target_stem = sorted(p.stem for p in pages_dir.glob("*.md"))[0]

    lines = index_path.read_text().splitlines()
    rewritten = []
    for line in lines:
        if f"pages/{target_stem}.md" in line:
            from urllib.parse import quote
            rewritten.append(f"- [Section One](pages/{quote(target_stem)}.md)")
        else:
            rewritten.append(line)
    index_path.write_text("\n".join(rewritten))

    report = validate_rendered.validate_rendered_output(rendered_dir, pkg)

    assert not any(i.code == "page_not_linked_from_index" for i in report.issues)


def test_index_completeness_detects_duplicate_link_while_another_page_is_omitted(tmp_path):
    pkg = _build_synthetic_package(tmp_path, TWO_CHUNK_SPECS)
    _, rendered_dir = _staged_render(tmp_path, pkg)
    pages_dir = rendered_dir / "pages"
    stems = sorted(p.stem for p in pages_dir.glob("*.md"))
    assert len(stems) >= 2, "fixture must produce at least 2 pages for this test to mean anything"
    first_stem, second_stem = stems[0], stems[1]

    index_path = rendered_dir / "index.md"
    lines = index_path.read_text().splitlines()
    rewritten = [l for l in lines if f"pages/{second_stem}.md" not in l]
    rewritten.append(f"- [Duplicate]({f'pages/{first_stem}.md'})")
    index_path.write_text("\n".join(rewritten))

    report = validate_rendered.validate_rendered_output(rendered_dir, pkg)

    assert report.status == "FAIL"
    assert any(
        i.code == "page_not_linked_from_index" and second_stem in i.message
        for i in report.issues
    )
