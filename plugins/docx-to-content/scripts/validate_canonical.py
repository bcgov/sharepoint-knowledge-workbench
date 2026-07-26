"""
validate_canonical.py
======================

The real canonical-package validator (spec Section 9, "Validation Policy").
Runs against a STAGED `canonical-content/` package on disk (Task 9's
`package.py` output) and produces a `contracts.ValidationReport` with real
PASS/WARN/FAIL semantics, replacing the `{"status": "PENDING"}` placeholder
`package.py` writes to `validation.json`.

Status semantics (spec Section 9, verbatim):
    - PASS: No errors and no undispositioned warnings.
    - WARN: No errors, but reviewable discrepancies exist. WARN cannot be
      promoted to accepted output until `warning-disposition.json` records
      each warning as accepted or resolved.
    - FAIL: Any invariant, integrity, schema, reference, or
      required-fidelity check fails. Commands exit non-zero and staging
      output is retained for diagnosis but not promoted.

This module does NOT apply/consume a warning-disposition file itself --
that is `dispositions.py`'s job (disposition-completeness is a separate
concern from producing the report). This module also does NOT promote
staging to a final location -- that is Task 11.

Severity design (this module's own decision, not dictated verbatim by the
spec beyond the PASS/WARN/FAIL rule above): every one of the 20
required-detection checks in the brief is an invariant/integrity/schema/
reference/required-fidelity check per Section 9's FAIL definition, so all
of them are `severity="error"` EXCEPT two, which are deliberately softer
"reviewable discrepancy" (WARN-level) checks:
    - `heading_missing_from_content`: a chunk's own heading text (last
      element of `source_heading_path`) not found as a heading line in its
      own content. This is a metadata/content drift *smell*, not proof of
      lost content (heading wording can legitimately be reformatted), so it
      is reviewable rather than fatal.
    - `content_comparison_skipped`: the normalized aggregate content-loss/
      duplication comparison (see below) could not run because no
      `cleaned_markdown_text` was supplied. This is a real gap in
      verification coverage that a human should consciously accept, not a
      silent PASS.

Content-loss/duplication "original" text decision (documented per the
task brief's explicit ask): Task 9's `convert.py` does NOT persist the
final cleaned markdown text anywhere under `canonical-content/` or
elsewhere in a stable, discoverable location -- `_staging/raw/extracted.md`
is pandoc's RAW (pre-cleanup) output, and by the time packaging runs, the
cleaned text only ever existed as an in-memory string inside
`convert_document`. So this module takes the OPTION (a) approach: an
optional `cleaned_markdown_text: str | None = None` parameter. When
provided (e.g. by a caller that still has it in-memory right after
`convert_document` returns, or a test that reconstructs it), the full
aggregate comparison runs. When omitted, the check is skipped and reported
as a WARN-level note (`content_comparison_skipped`), never silently
treated as PASS -- an unverified package must not look identical to a
verified one in the report.

Function Index:
    - validate_canonical_package(package_dir, plan, source_path=None,
      cleaned_markdown_text=None) -> contracts.ValidationReport
    - write_validation_report(report, package_dir) -> None
        Overwrites `<package_dir>/validation.json` with the real report,
        replacing package.py's PENDING placeholder.
"""

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import contracts  # noqa: E402
import hashing  # noqa: E402
import package  # noqa: E402
import pandoc_validate  # noqa: E402
import plans  # noqa: E402
from pandoc_fixes.toc import _BOOKMARK_ANCHOR_LINE, _TOC_LINK_LINE  # noqa: E402


def _issue(severity: str, code: str, message: str, path: "str | None" = None) -> "contracts.ValidationIssue":
    return contracts.ValidationIssue(severity=severity, code=code, message=message, path=path)


def _error(code: str, message: str, path: "str | None" = None) -> "contracts.ValidationIssue":
    return _issue("error", code, message, path)


def _warning(code: str, message: str, path: "str | None" = None) -> "contracts.ValidationIssue":
    return _issue("warning", code, message, path)


# ---------------------------------------------------------------------------
# Normalized aggregate comparison (content-loss / duplication)
# ---------------------------------------------------------------------------

def _normalize_for_comparison(text: str) -> str:
    """Normalize whitespace for aggregate content comparison: strip
    trailing whitespace on every line, collapse runs of 2+ blank lines
    down to one, and strip leading/trailing blank lines from the whole
    document. This is deliberately conservative -- it does NOT reorder,
    lowercase, or strip punctuation, so a genuine content difference
    (missing paragraph, duplicated section) still shows up as a mismatch;
    it only absorbs the whitespace churn that chunk slicing/reassembly is
    expected to introduce (e.g. a chunk boundary landing mid-blank-line)."""
    lines = [line.rstrip() for line in text.splitlines()]
    collapsed: list = []
    blank_run = 0
    for line in lines:
        if line == "":
            blank_run += 1
            if blank_run > 1:
                continue
        else:
            blank_run = 0
        collapsed.append(line)
    return "\n".join(collapsed).strip()


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def validate_canonical_package(
    package_dir: "Path",
    plan: "contracts.ConversionPlan",
    source_path: "Path | None" = None,
    cleaned_markdown_text: "str | None" = None,
) -> "contracts.ValidationReport":
    """Validate a staged canonical-content package under `package_dir`
    against `plan` (the confirmed ConversionPlan used to produce it).

    Fails as gracefully as possible: even when the manifest itself is
    malformed/missing, a ValidationReport with status FAIL is still
    returned (never an uncaught exception) so callers always get a
    reportable result.
    """
    package_dir = Path(package_dir)
    issues: list = []

    manifest, manifest_issues = _load_manifest(package_dir)
    issues.extend(manifest_issues)

    # plan fingerprint / source fingerprint checks (reuse plans.py)
    issues.extend(_check_plan_and_source(plan, source_path))

    if manifest is not None:
        issues.extend(_check_manifest_consistency(manifest, plan))
        chunk_meta_by_id, chunk_issues = _load_and_check_chunks(package_dir, manifest)
        issues.extend(chunk_issues)
        issues.extend(_check_orphans(package_dir, manifest))
        issues.extend(_check_unresolved_anchors(manifest, plan))
        issues.extend(
            _check_content_loss_and_duplication(
                package_dir, manifest, cleaned_markdown_text
            )
        )
        issues.extend(_check_media_references(package_dir, manifest, chunk_meta_by_id))

    has_error = any(i.severity == "error" for i in issues)
    has_warning = any(i.severity == "warning" for i in issues)
    if has_error:
        status = "FAIL"
    elif has_warning:
        status = "WARN"
    else:
        status = "PASS"

    return contracts.ValidationReport(
        status=status,
        issues=issues,
        source_sha256=plan.source.sha256,
        plan_id=plan.plan_id,
    )


def write_validation_report(report: "contracts.ValidationReport", package_dir: "Path") -> None:
    """Overwrite `<package_dir>/validation.json` with the real report,
    replacing `package.py`'s `{"status": "PENDING"}` placeholder."""
    (Path(package_dir) / "validation.json").write_text(
        json.dumps(report.to_dict(), indent=2, sort_keys=True)
    )


# ---------------------------------------------------------------------------
# Manifest loading: malformed JSON / missing required fields / schema
# ---------------------------------------------------------------------------

def _load_manifest(package_dir: "Path"):
    manifest_path = package_dir / "manifest.json"
    if not manifest_path.exists():
        return None, [_error("manifest_missing", f"{manifest_path} does not exist")]
    try:
        raw = json.loads(manifest_path.read_text())
    except json.JSONDecodeError as exc:
        return None, [_error("malformed_json", f"manifest.json is not valid JSON: {exc}", "manifest.json")]
    try:
        manifest = contracts.Manifest.from_dict(raw)
    except ValueError as exc:
        message = str(exc)
        code = "schema_version_unsupported" if "schema_version" in message else "missing_required_field"
        return None, [_error(code, f"manifest.json: {message}", "manifest.json")]
    return manifest, []


def _load_chunk_meta(meta_path: "Path"):
    try:
        raw = json.loads(meta_path.read_text())
    except json.JSONDecodeError as exc:
        return None, _error("malformed_json", f"{meta_path.name} is not valid JSON: {exc}", str(meta_path))
    try:
        meta = contracts.ChunkMetadata.from_dict(raw)
    except ValueError as exc:
        message = str(exc)
        code = "schema_version_unsupported" if "schema_version" in message else "missing_required_field"
        return None, _error(code, f"{meta_path.name}: {message}", str(meta_path))
    return meta, None


# ---------------------------------------------------------------------------
# Source / plan fingerprint checks (reuse plans.py)
# ---------------------------------------------------------------------------

def _check_plan_and_source(plan: "contracts.ConversionPlan", source_path: "Path | None") -> list:
    issues = []
    try:
        plans.verify_plan_integrity(plan)
    except plans.PlanVerificationError as exc:
        issues.append(_error("plan_fingerprint_mismatch", str(exc)))
    if source_path is not None:
        try:
            plans.verify_plan_against_source(plan, source_path)
        except plans.PlanVerificationError as exc:
            issues.append(_error("source_fingerprint_mismatch", str(exc)))
    return issues


# ---------------------------------------------------------------------------
# Manifest-level consistency: counts, duplicate IDs/paths/orders
# ---------------------------------------------------------------------------

def _check_manifest_consistency(manifest: "contracts.Manifest", plan: "contracts.ConversionPlan") -> list:
    issues = []

    if manifest.chunk_count != len(manifest.chunks):
        issues.append(_error(
            "chunk_count_mismatch",
            f"manifest.chunk_count={manifest.chunk_count} but manifest.chunks "
            f"has {len(manifest.chunks)} entries",
            "manifest.json",
        ))

    if manifest.plan_id != plan.plan_id:
        issues.append(_error(
            "plan_fingerprint_mismatch",
            f"manifest.plan_id={manifest.plan_id!r} does not match the "
            f"supplied plan's plan_id={plan.plan_id!r}",
            "manifest.json",
        ))

    def _dupes(values):
        seen = set()
        dup = set()
        for v in values:
            if v in seen:
                dup.add(v)
            seen.add(v)
        return dup

    chunk_ids = [c.chunk_id for c in manifest.chunks]
    content_files = [c.content_file for c in manifest.chunks]
    metadata_files = [c.metadata_file for c in manifest.chunks]
    source_orders = [c.source_order for c in manifest.chunks]

    for label, values, code in (
        ("chunk_id", chunk_ids, "duplicate_chunk_id"),
        ("content_file", content_files, "duplicate_content_path"),
        ("metadata_file", metadata_files, "duplicate_metadata_path"),
        ("source_order", source_orders, "duplicate_source_order"),
    ):
        for dup in _dupes(values):
            issues.append(_error(code, f"duplicate {label}: {dup!r}", "manifest.json"))

    return issues


# ---------------------------------------------------------------------------
# Per-chunk checks: missing files, ID mismatches, hash mismatches, empty
# chunks, heading path presence
# ---------------------------------------------------------------------------

def _load_and_check_chunks(package_dir: "Path", manifest: "contracts.Manifest"):
    issues = []
    chunk_meta_by_id = {}

    for chunk in manifest.chunks:
        content_path = package_dir / chunk.content_file
        meta_path = package_dir / chunk.metadata_file

        if not content_path.exists():
            issues.append(_error(
                "missing_chunk_file", f"expected chunk content file does not exist", chunk.content_file
            ))
        if not meta_path.exists():
            issues.append(_error(
                "missing_sidecar_file", f"expected chunk sidecar file does not exist", chunk.metadata_file
            ))
        if not content_path.exists() or not meta_path.exists():
            continue

        meta, meta_error = _load_chunk_meta(meta_path)
        if meta_error is not None:
            issues.append(meta_error)
            continue
        chunk_meta_by_id[chunk.chunk_id] = meta

        if meta.chunk_id != chunk.chunk_id:
            issues.append(_error(
                "chunk_id_mismatch",
                f"sidecar chunk_id={meta.chunk_id!r} does not match manifest "
                f"chunk_id={chunk.chunk_id!r}",
                chunk.metadata_file,
            ))

        content = content_path.read_text()
        actual_hash = hashing.content_hash(content.encode("utf-8"))
        if actual_hash != meta.content_sha256:
            issues.append(_error(
                "content_hash_mismatch",
                f"content_sha256 mismatch for {chunk.chunk_id!r}: "
                f"manifest/sidecar recorded {meta.content_sha256!r}, "
                f"actual content hashes to {actual_hash!r}",
                chunk.content_file,
            ))

        if content.strip() == "":
            issues.append(_error(
                "empty_chunk", f"chunk {chunk.chunk_id!r} content is empty", chunk.content_file
            ))

        own_heading = (meta.source_heading_path or [None])[-1]
        if own_heading is not None:
            heading_lines = [
                line.split(" ", 1)[1].strip() if " " in line else ""
                for line in content.splitlines()
                if re.match(r"^#{1,6}\s", line)
            ]
            if own_heading not in heading_lines:
                issues.append(_warning(
                    "heading_missing_from_content",
                    f"chunk {chunk.chunk_id!r}'s own heading {own_heading!r} "
                    "(last element of source_heading_path) was not found as "
                    "a heading line in its own content",
                    chunk.content_file,
                ))

        issues.extend(_check_raw_artifacts(chunk, content))

    return chunk_meta_by_id, issues


# ---------------------------------------------------------------------------
# Raw TOC artifacts / pandoc attributes / images-in-headings (Task 2 reuse)
# ---------------------------------------------------------------------------

def _check_raw_artifacts(chunk: "contracts.ManifestChunk", content: str) -> list:
    issues = []

    for line in content.splitlines():
        stripped = line.rstrip("\n")
        if _BOOKMARK_ANCHOR_LINE.match(stripped) or _TOC_LINK_LINE.match(stripped):
            issues.append(_error(
                "raw_toc_artifact",
                f"raw Word TOC artifact line found in chunk content: {stripped!r}",
                chunk.content_file,
            ))

    # pandoc_validate.validate_cleaned_markdown lumps together attribute
    # artifacts, images-in-headings, and unresolved image links into one
    # errors list; classify each by its known message prefix so this
    # module's report carries distinct codes per the brief's required
    # detection list, without re-implementing any of the regex logic.
    result = pandoc_validate.validate_cleaned_markdown(content, base_dir=Path("/__unused__"))
    for message in result["errors"]:
        if message.startswith("Leftover pandoc attribute artifact"):
            issues.append(_error("pandoc_attribute_artifact", message, chunk.content_file))
        elif message.startswith("Image embedded directly in heading line"):
            issues.append(_error("image_in_heading", message, chunk.content_file))
        # "Unresolved image link" messages are deliberately ignored here:
        # base_dir above is a dummy, so every relative ref would spuriously
        # "fail" resolution; real broken-media-reference checking is done
        # by `_check_media_references` against the package's actual media/
        # directory instead.

    return issues


# ---------------------------------------------------------------------------
# Orphan chunks/sidecars/media
# ---------------------------------------------------------------------------

def _check_orphans(package_dir: "Path", manifest: "contracts.Manifest") -> list:
    issues = []
    chunks_dir = package_dir / "chunks"
    media_dir = package_dir / "media"

    known_content_stems = {Path(c.content_file).stem for c in manifest.chunks}
    known_meta_stems = {
        Path(c.metadata_file).name[: -len(".meta.json")] for c in manifest.chunks
    }

    if chunks_dir.is_dir():
        for md_file in sorted(chunks_dir.glob("*.md")):
            if md_file.stem not in known_content_stems:
                issues.append(_error(
                    "orphan_chunk_file",
                    f"chunk content file not referenced by any manifest entry",
                    f"chunks/{md_file.name}",
                ))
        for meta_file in sorted(chunks_dir.glob("*.meta.json")):
            stem = meta_file.name[: -len(".meta.json")]
            if stem not in known_meta_stems:
                issues.append(_error(
                    "orphan_sidecar_file",
                    f"chunk sidecar file not referenced by any manifest entry",
                    f"chunks/{meta_file.name}",
                ))

    known_media = set(manifest.media)
    if media_dir.is_dir():
        for media_file in sorted(media_dir.iterdir()):
            if media_file.is_file() and media_file.name not in known_media:
                issues.append(_error(
                    "orphan_media_file",
                    f"media file not referenced by manifest.media",
                    f"media/{media_file.name}",
                ))

    return issues


# ---------------------------------------------------------------------------
# Unresolved structural anchors: manifest chunk_ids vs plan's anchors
# ---------------------------------------------------------------------------

def _check_unresolved_anchors(manifest: "contracts.Manifest", plan: "contracts.ConversionPlan") -> list:
    """Defense-in-depth re-check (Task 8/9 already resolve anchors at
    conversion time, raising before a package is ever staged if they
    can't): every manifest chunk_id must correspond to exactly one
    anchor's stable_key in the confirmed plan's chunk_anchors, and every
    plan anchor must be represented exactly once in the manifest. This is
    identity/count matching only -- not anchor re-resolution against
    markdown, which already happened in `chunking.py`."""
    issues = []
    plan_keys = [a.stable_key for a in plan.chunk_anchors]
    manifest_ids = [c.chunk_id for c in manifest.chunks]

    plan_key_set = set(plan_keys)
    manifest_id_set = set(manifest_ids)

    for chunk_id in manifest_ids:
        if chunk_id not in plan_key_set:
            issues.append(_error(
                "unresolved_structural_anchor",
                f"manifest chunk_id {chunk_id!r} does not correspond to any "
                "anchor's stable_key in the confirmed plan's chunk_anchors",
            ))
    for stable_key in plan_keys:
        if stable_key not in manifest_id_set:
            issues.append(_error(
                "unresolved_structural_anchor",
                f"confirmed plan anchor {stable_key!r} has no corresponding "
                "chunk in the manifest",
            ))
    return issues


# ---------------------------------------------------------------------------
# Content-loss / duplication: normalized aggregate comparison
# ---------------------------------------------------------------------------

def _check_content_loss_and_duplication(
    package_dir: "Path", manifest: "contracts.Manifest", cleaned_markdown_text: "str | None"
) -> list:
    if cleaned_markdown_text is None:
        return [_warning(
            "content_comparison_skipped",
            "no cleaned_markdown_text was supplied to the validator; the "
            "normalized aggregate content-loss/duplication comparison was "
            "not performed for this run",
        )]

    ordered_chunks = sorted(manifest.chunks, key=lambda c: c.source_order)
    pieces = []
    for chunk in ordered_chunks:
        content_path = package_dir / chunk.content_file
        if content_path.exists():
            pieces.append(content_path.read_text())
    reconstructed = "\n".join(pieces)

    normalized_reconstructed = _normalize_for_comparison(reconstructed)
    normalized_original = _normalize_for_comparison(cleaned_markdown_text)

    if normalized_reconstructed != normalized_original:
        return [_error(
            "content_loss_or_duplication",
            "normalized aggregate of staged chunks does not match the "
            "normalized cleaned markdown text used to produce them "
            "(possible content loss or duplication during chunking/"
            "packaging)",
        )]
    return []


# ---------------------------------------------------------------------------
# Broken media/local-document links, path traversal / absolute paths
# ---------------------------------------------------------------------------

_IMAGE_REF = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def _check_media_references(
    package_dir: "Path", manifest: "contracts.Manifest", chunk_meta_by_id: dict
) -> list:
    """Second-pass check against the FINAL, already-staged reference in
    `chunks/<id>.md` (as opposed to `package.py`'s check, which runs at
    conversion time against RAW pre-rewrite references before they are
    written). A legitimately rewritten reference always looks like
    `../media/<file>` (see `package.py`'s docstring: chunks/ and media/
    are sibling directories), i.e. it always contains exactly one `..`
    segment -- so this cannot reuse `package._decode_and_validate`
    unmodified (that function rejects ANY `..` segment, which would flag
    every legitimate staged reference as a violation). Instead: an
    absolute path is always a violation; a `..`-containing relative path
    is a violation only if it resolves to somewhere OUTSIDE `package_dir`
    entirely (escaping the package), whereas resolving to somewhere inside
    `package_dir` but outside `media/` (or to a nonexistent file inside
    `media/`) is reported as a broken media reference instead."""
    issues = []
    chunks_dir = package_dir / "chunks"
    package_dir_resolved = package_dir.resolve()
    media_dir_resolved = (package_dir / "media").resolve()
    known_chunk_ids = {c.chunk_id for c in manifest.chunks}

    for chunk in manifest.chunks:
        content_path = package_dir / chunk.content_file
        if not content_path.exists():
            continue
        content = content_path.read_text()

        for match in _IMAGE_REF.finditer(content):
            raw_ref = match.group(1).strip()
            if raw_ref.startswith(("http://", "https://")):
                continue
            ref = unquote(raw_ref)

            if Path(ref).is_absolute() or ref.startswith("\\\\"):
                issues.append(_error(
                    "path_traversal_or_absolute_reference",
                    f"media reference {raw_ref!r} in staged chunk content "
                    "is an absolute path",
                    chunk.content_file,
                ))
                continue

            resolved = (chunks_dir / ref).resolve()
            if package_dir_resolved != resolved and package_dir_resolved not in resolved.parents:
                issues.append(_error(
                    "path_traversal_or_absolute_reference",
                    f"media reference {raw_ref!r} in staged chunk content "
                    "resolves outside the package directory via '..' "
                    "traversal",
                    chunk.content_file,
                ))
                continue

            if media_dir_resolved not in resolved.parents or not resolved.exists():
                issues.append(_error(
                    "broken_media_reference",
                    f"media reference {raw_ref!r} in {chunk.content_file} does "
                    f"not resolve to an existing file under media/",
                    chunk.content_file,
                ))
            elif resolved.suffix.lower() in (".emf", ".wmf"):
                issues.append(_error(
                    "unsupported_legacy_media",
                    f"media reference {raw_ref!r} in {chunk.content_file} "
                    "resolves to an unsupported legacy (.emf/.wmf) file",
                    chunk.content_file,
                ))

        meta = chunk_meta_by_id.get(chunk.chunk_id)
        local_links = meta.local_links if meta is not None else []
        for link in local_links:
            if link.startswith(("http://", "https://", "#")):
                continue
            target_stem = Path(link).stem
            if target_stem not in known_chunk_ids and not (chunks_dir / link).exists():
                issues.append(_error(
                    "broken_local_link",
                    f"local document link {link!r} in {chunk.content_file} "
                    "does not resolve to any known chunk or file in the "
                    "package",
                    chunk.content_file,
                ))

    return issues
