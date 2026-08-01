"""
validate_rendered.py
======================

Task 14 -- the render validator (spec Section 9, "Render validation must
detect") and the atomic-promotion wiring Task 13's `render_to_staging`
deliberately left undone (it stages a render but never promotes -- see its
module docstring).

Runs against a STAGED rendered-output directory (Task 13's
`render_to_staging()` output) and produces a `ValidationReport`
with the same PASS/WARN/FAIL shape `validate_canonical.py` (Task 10) uses,
for consistency across both validators.

Status semantics (this module's own decision, matching Task 10's precedent):
every one of the 9 required detections below is an invariant/integrity/
reference check with no legitimate "reviewable discrepancy" analog -- unlike
Task 10's canonical validator, which has two deliberately-WARN checks
(heading-drift smell, skipped content comparison), nothing about a broken
link, a missing page, or a stale manifest hash in a RENDERED output is ever
something a human should "accept as-is" the way a reformatted heading might
be. Every issue this module raises is therefore `severity="error"`, so
`ValidationReport.status` is always PASS or FAIL, never WARN --
`dispositions.py` is intentionally not used here; there is nothing at the
render layer that maps to its WARN-acceptance model.

Manifest-hash staleness tracking: `render_to_staging()`'s `RenderResult`
already carries `source_content_sha256` (Section 8: "renderer result
includes ... source manifest hash"), populated by
`multipage_markdown.MultipageMarkdownRenderer.render()` as
`package.manifest.source.sha256` -- the canonical package's source .docx
fingerprint. This module persists that `RenderResult` to
`<staging_dir>/render-result.json` (`write_render_result`, mirroring
`atomic_output.write_generator_info`'s persist-then-reread pattern) so a
later validation pass -- possibly run against a package that has since been
reconverted -- can compare the STAGED render's recorded hash against the
CURRENT `package.manifest.source.sha256`. A mismatch means the canonical
package was reconverted (new source fingerprint) after this render was
staged; catching that is exactly what `source_content_stale` checks for.

Path-safety reuse: broken-media/local-link and path-traversal/absolute-
reference detection reuse `path_safety.classify_reference` (a new shared
helper factored out specifically because this is the THIRD place in the
plugin needing the same "resolve a rewritten reference, reject absolute /
outside-root paths" policy -- see `path_safety.py`'s own docstring for full
reasoning and why `validate_canonical.py` was deliberately left as-is
rather than retrofitted in this task).

Function Index:
    - validate_rendered_output(rendered_dir, package) -> ValidationReport
    - write_rendered_validation_report(report, rendered_dir) -> None
        Writes `<rendered_dir>/renderer-validation.json`.
    - write_render_result(result, staging_dir) -> None
        Writes `<staging_dir>/render-result.json` (RenderResult.to_dict()).
    - render_and_promote(package, output_root, renderer=None, final_dir=None,
      plugin_version=...) -> (RenderResult, ValidationReport, promoted: bool, Path)
        Full pipeline: render_to_staging -> write render-result/generator-info
        -> validate_rendered_output -> write renderer-validation.json ->
        promote() only on PASS. Mirrors `convert.convert_and_promote`'s
        shape/naming.
"""

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

_THIS_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _THIS_DIR.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import atomic_output  # noqa: E402
import contracts  # noqa: E402
# Compatibility shim (Phase 4.5 Wave 4, retire per wave-1-decisions.json):
# ValidationIssue/ValidationReport now live in the installed
# `canonical-knowledge` package -- see
# docs/superpowers/plans/phase-4-5-evidence/wave-4-canonical-knowledge-split-decision.md.
from canonical_schema.canonical_package import ValidationIssue, ValidationReport  # noqa: E402
import path_safety  # noqa: E402
from renderers import multipage_markdown as mpm  # noqa: E402

# See scripts/package.py's _IMAGE_REF docstring for why link/alt text uses
# `(?:[^\]\\]|\\.)*` rather than a naive `[^\]]*` -- a markdown-escaped `]`
# in link/alt text otherwise terminates the character class early and the
# whole reference silently escapes this validator's broken-link check.
_LINK_REF = re.compile(r"(?<!!)\[(?:[^\]\\]|\\.)*\]\(([^)]+)\)")
_IMAGE_REF = re.compile(r"!\[(?:[^\]\\]|\\.)*\]\(([^)]+)\)")


def _error(code: str, message: str, path: "str | None" = None) -> "ValidationIssue":
    return ValidationIssue(severity="error", code=code, message=message, path=path)


# ---------------------------------------------------------------------------
# render-result.json / renderer-validation.json persistence
# ---------------------------------------------------------------------------

def write_render_result(result: "contracts.RenderResult", staging_dir: Path) -> None:
    """Persist `result` (the `RenderResult` `render_to_staging()` returned)
    into the staged render directory as `render-result.json`, so a later
    validation pass -- possibly run in a separate process/invocation -- can
    recover the source manifest hash this render was produced from, without
    needing the in-memory `RenderResult` object still around."""
    (Path(staging_dir) / "render-result.json").write_text(
        json.dumps(result.to_dict(), indent=2, sort_keys=True)
    )


def write_rendered_validation_report(report: "ValidationReport", rendered_dir: Path) -> None:
    """Write `<rendered_dir>/renderer-validation.json` -- this validator's
    own output report (detection #1's "missing ... output report" refers to
    THIS file's existence being unnecessary as a validation PRECONDITION,
    since producing it is what validation itself does)."""
    (Path(rendered_dir) / "renderer-validation.json").write_text(
        json.dumps(report.to_dict(), indent=2, sort_keys=True)
    )


# ---------------------------------------------------------------------------
# 1. index.md / pages/ existence
# ---------------------------------------------------------------------------

def _check_index_and_pages_exist(rendered_dir: Path) -> list:
    issues = []
    if not (rendered_dir / "index.md").exists():
        issues.append(_error("missing_index", "index.md does not exist", "index.md"))
    if not (rendered_dir / "pages").is_dir():
        issues.append(_error("missing_pages_dir", "pages/ directory does not exist", "pages"))
    return issues


# ---------------------------------------------------------------------------
# 2. Broken index links
# ---------------------------------------------------------------------------

def _check_index_links(rendered_dir: Path) -> list:
    index_path = rendered_dir / "index.md"
    if not index_path.exists():
        return []
    issues = []
    text = index_path.read_text()
    for match in _LINK_REF.finditer(text):
        raw_target = match.group(1).strip()
        if raw_target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        target = unquote(raw_target)
        if not target.startswith("pages/"):
            continue
        resolved = rendered_dir / target
        if not resolved.exists():
            issues.append(_error(
                "broken_index_link",
                f"index.md links to {raw_target!r}, which does not exist",
                "index.md",
            ))
    return issues


# ---------------------------------------------------------------------------
# New: index completeness (Task 12)
# ---------------------------------------------------------------------------

def _check_index_completeness(rendered_dir: Path) -> list:
    """index.md must link every page that actually exists under pages/ --
    _check_index_links only catches links that ARE present and broken, not
    an existing page index.md silently fails to mention at all."""
    index_path = rendered_dir / "index.md"
    pages_dir = rendered_dir / "pages"
    if not index_path.exists() or not pages_dir.is_dir():
        return []

    index_text = index_path.read_text()
    linked_stems = set()
    for match in _LINK_REF.finditer(index_text):
        raw_target = match.group(1).strip()
        if raw_target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        target = unquote(raw_target)
        if target.startswith("pages/"):
            linked_stems.add(Path(target).stem)

    issues = []
    for page_path in sorted(pages_dir.glob("*.md")):
        if page_path.stem not in linked_stems:
            issues.append(_error(
                "page_not_linked_from_index",
                f"pages/{page_path.name} exists but index.md does not link it",
                "index.md",
            ))
    return issues


# ---------------------------------------------------------------------------
# 3 & 4. Missing / orphan pages, page count mismatch
# ---------------------------------------------------------------------------

def _check_page_completeness(rendered_dir: Path, package) -> list:
    pages_dir = rendered_dir / "pages"
    if not pages_dir.is_dir():
        return []

    issues = []
    known_ids = {chunk.metadata.chunk_id for chunk in package.chunks}
    page_files = {p.stem: p for p in pages_dir.glob("*.md")}

    for chunk_id in known_ids:
        if chunk_id not in page_files:
            issues.append(_error(
                "missing_page",
                f"expected rendered page for chunk {chunk_id!r} does not exist",
                f"pages/{chunk_id}.md",
            ))

    for stem in sorted(page_files):
        if stem not in known_ids:
            issues.append(_error(
                "orphan_page",
                f"rendered page {stem!r} does not correspond to any chunk "
                "in the source canonical package",
                f"pages/{stem}.md",
            ))

    if len(page_files) != package.manifest.chunk_count:
        issues.append(_error(
            "page_count_mismatch",
            f"pages/ contains {len(page_files)} file(s) but the manifest "
            f"chunk_count is {package.manifest.chunk_count}",
            "pages",
        ))

    return issues


# ---------------------------------------------------------------------------
# 5 & 6. Broken local links / media references, path traversal / absolute
# ---------------------------------------------------------------------------

def _check_page_references(rendered_dir: Path, package) -> list:
    pages_dir = rendered_dir / "pages"
    if not pages_dir.is_dir():
        return []

    issues = []
    known_ids = {chunk.metadata.chunk_id for chunk in package.chunks}

    for page_path in sorted(pages_dir.glob("*.md")):
        content = page_path.read_text()
        rel_path = f"pages/{page_path.name}"

        # Media references (image syntax) -- must resolve under this
        # render's OWN media/ dir, never the canonical package's.
        for match in _IMAGE_REF.finditer(content):
            raw_ref = match.group(1).strip()
            kind, detail = path_safety.classify_reference(raw_ref, pages_dir, rendered_dir)
            if kind == "external":
                continue
            if kind == "violation":
                issues.append(_error(
                    "path_traversal_or_absolute_reference",
                    f"media reference {raw_ref!r} in {rel_path} is "
                    f"{'an absolute path' if detail == path_safety.VIOLATION_ABSOLUTE else 'a path-traversal outside the rendered output'}",
                    rel_path,
                ))
                continue
            resolved = detail
            media_dir = (rendered_dir / "media").resolve()
            if media_dir not in resolved.parents or not resolved.exists():
                issues.append(_error(
                    "broken_media_reference",
                    f"media reference {raw_ref!r} in {rel_path} does not "
                    "resolve to an existing file under this render's media/",
                    rel_path,
                ))

        # Local page-to-page links (non-image, page-relative "<chunk_id>.md")
        for match in _LINK_REF.finditer(content):
            raw_target = match.group(1).strip()
            if raw_target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            decoded = unquote(raw_target)
            if not decoded.endswith(".md"):
                continue

            kind, detail = path_safety.classify_reference(raw_target, pages_dir, rendered_dir)
            if kind == "violation":
                issues.append(_error(
                    "path_traversal_or_absolute_reference",
                    f"local link {raw_target!r} in {rel_path} is "
                    f"{'an absolute path' if detail == path_safety.VIOLATION_ABSOLUTE else 'a path-traversal outside the rendered output'}",
                    rel_path,
                ))
                continue

            target_chunk_id = Path(decoded).stem
            resolved = detail
            if target_chunk_id not in known_ids or not resolved.exists():
                issues.append(_error(
                    "broken_local_link",
                    f"local link {raw_target!r} in {rel_path} does not "
                    "resolve to a known rendered page",
                    rel_path,
                ))

    return issues


# ---------------------------------------------------------------------------
# 8. Manifest hash mismatch
# ---------------------------------------------------------------------------

def _check_source_content_staleness(rendered_dir: Path, package) -> list:
    result_path = rendered_dir / "render-result.json"
    if not result_path.exists():
        return [_error(
            "missing_render_result",
            "render-result.json does not exist -- cannot verify which "
            "canonical package this render was produced from",
            "render-result.json",
        )]

    try:
        recorded = contracts.RenderResult.from_dict(json.loads(result_path.read_text()))
    except (ValueError, json.JSONDecodeError) as exc:
        return [_error(
            "malformed_render_result",
            f"render-result.json failed schema validation: {exc}",
            "render-result.json",
        )]

    current_hash = package.manifest.source.sha256
    if recorded.source_content_sha256 != current_hash:
        return [_error(
            "source_content_stale",
            f"render-result.json records source_content_sha256="
            f"{recorded.source_content_sha256!r}, but the supplied canonical "
            f"package's current source content hash is {current_hash!r} -- "
            "the canonical package was reconverted after this render was "
            "staged",
            "render-result.json",
        )]
    return []


# ---------------------------------------------------------------------------
# 9. Rendered page content not traceable to a chunk ID
# ---------------------------------------------------------------------------

def _check_page_traceability(rendered_dir: Path, package) -> list:
    pages_dir = rendered_dir / "pages"
    if not pages_dir.is_dir():
        return []

    issues = []
    known_ids = {chunk.metadata.chunk_id for chunk in package.chunks}

    for chunk in package.chunks:
        page_path = pages_dir / f"{chunk.metadata.chunk_id}.md"
        if not page_path.exists():
            continue  # already reported by _check_page_completeness
        expected = mpm._rewrite_local_links(chunk.content, known_ids)
        actual = page_path.read_text()
        if actual != expected:
            issues.append(_error(
                "page_content_not_traceable",
                f"pages/{chunk.metadata.chunk_id}.md content does not match "
                "the source chunk's content (post local-link rewrite) -- "
                "not traceable back to its chunk ID",
                f"pages/{chunk.metadata.chunk_id}.md",
            ))

    return issues


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def validate_rendered_output(rendered_dir: Path, package) -> "ValidationReport":
    """Validate a staged rendered-output directory under `rendered_dir`
    (Task 13's `render_to_staging()` output) against `package` (the
    `CanonicalPackage` it was rendered from). Returns a
    `ValidationReport` -- always PASS or FAIL (see module
    docstring for why WARN does not apply at the render layer)."""
    rendered_dir = Path(rendered_dir)
    issues = []

    issues.extend(_check_index_and_pages_exist(rendered_dir))
    issues.extend(_check_index_links(rendered_dir))
    issues.extend(_check_index_completeness(rendered_dir))
    issues.extend(_check_page_completeness(rendered_dir, package))
    issues.extend(_check_page_references(rendered_dir, package))
    issues.extend(_check_source_content_staleness(rendered_dir, package))
    issues.extend(_check_page_traceability(rendered_dir, package))

    status = "FAIL" if issues else "PASS"

    return ValidationReport(
        status=status,
        issues=issues,
        source_sha256=package.manifest.source.sha256,
        plan_id=package.manifest.plan_id,
    )


# ---------------------------------------------------------------------------
# render_and_promote: full stage -> validate -> promote pipeline
# ---------------------------------------------------------------------------

def render_and_promote(
    package,
    output_root: Path,
    renderer=None,
    final_dir: "Path | None" = None,
    plugin_version: str = atomic_output.DEFAULT_PLUGIN_VERSION,
):
    """Render `package` into a fresh staging directory, validate it there,
    and promote it to `final_dir` (default `output_root / "rendered-output"`)
    only if validation status is PASS. Mirrors `convert.convert_and_promote`'s
    shape: `(RenderResult, ValidationReport, promoted: bool, Path)`, where
    the returned `Path` is `final_dir` on success or the retained staging
    dir on failure (for diagnosis, never deleted)."""
    output_root = Path(output_root)
    final_dir = Path(final_dir) if final_dir is not None else output_root / "rendered-output"

    result, staging_dir = mpm.render_to_staging(package, output_root, renderer=renderer)
    atomic_output.write_generator_info(staging_dir, plugin_version=plugin_version)
    write_render_result(result, staging_dir)

    report = validate_rendered_output(staging_dir, package)
    write_rendered_validation_report(report, staging_dir)

    if report.status == "PASS":
        atomic_output.promote(staging_dir, final_dir)
        return result, report, True, final_dir

    return result, report, False, staging_dir
