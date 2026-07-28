"""
convert.py
==========

Orchestrates the full `convert-document` pipeline (spec Section 7.2),
through canonical package construction (validation/promotion are Tasks
10/11, NOT this module):

    DOCX
    -> pandoc extraction to staging
    -> attrs cleanup
    -> image-placement cleanup
    -> TOC cleanup
    -> table cleanup
    -> footnote cleanup
    -> legacy image conversion
    -> structural-anchor reconciliation
    -> chunking
    -> media path rewrite/copy
    -> metadata and hashes
    -> manifest
    [canonical validation      <- Task 10]
    [atomic promotion          <- Task 11]

The cleanup step order is factored into `apply_cleanup_pipeline` so it can
be unit-tested in isolation against a synthetic fixture without invoking
real pandoc (mirroring how `tests/unit/test_regression_pipeline.py` already
tests the same six modules together). `run_pandoc_extraction` is likewise
factored out as its own function so it is the only piece of this module
that shells out, keeping `convert_document`'s own logic (precondition
checks -> extraction -> cleanup -> legacy media -> reconcile/slice ->
package) readable as a single top-to-bottom sequence.
"""

import re
import subprocess
import sys
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import atomic_output  # noqa: E402
import chunking  # noqa: E402
import contracts  # noqa: E402
import dispositions  # noqa: E402
import emf_convert  # noqa: E402
import package  # noqa: E402
import plans  # noqa: E402
import validate_canonical  # noqa: E402
from pandoc_fixes.attrs import strip_pandoc_attrs  # noqa: E402
from pandoc_fixes.footnotes import clean_orphaned_footnotes  # noqa: E402
from pandoc_fixes.heading_emphasis import strip_whole_heading_emphasis  # noqa: E402
from pandoc_fixes.images import fix_glued_images  # noqa: E402
from pandoc_fixes.tables import fix_malformed_tables  # noqa: E402
from pandoc_fixes.toc import strip_raw_toc  # noqa: E402


def apply_cleanup_pipeline(markdown_text: str) -> str:
    """Apply the pandoc_fixes cleanup steps in the exact spec Section 7.2
    order: attrs -> heading-emphasis -> images -> toc -> tables ->
    footnotes. Order matters -- e.g. TOC-stripping must run after
    image-fixing so a raw Word TOC dump doesn't get misidentified/mangled
    while an image is still glued onto an adjacent heading line; running
    steps out of order can produce a different (wrong) result even though
    each step is individually correct in isolation.

    `strip_whole_heading_emphasis` runs right after `strip_pandoc_attrs`
    (both are narrow, heading/text-normalization passes) and BEFORE
    image-fixing/TOC-stripping/anchor reconciliation: it only rewrites the
    surrounding `**`/`***`/`_` markers on a heading line, never the
    heading's text content, so it cannot affect whether a later step
    recognizes a glued image or a TOC-shaped link on the same or an
    adjacent line -- but running it early keeps every downstream step
    (including chunking's post-cleanup anchor reconciliation, which keys
    off heading text) working against the final, normalized heading text
    rather than a still-decorated one.

    This is the sole place that order is encoded; `convert_document` calls
    this function rather than inlining the sequence a second time."""
    text = strip_pandoc_attrs(markdown_text)
    text = strip_whole_heading_emphasis(text)
    text = fix_glued_images(text)
    text = strip_raw_toc(text)
    text = fix_malformed_tables(text)
    text = clean_orphaned_footnotes(text)
    return text


_ABS_MEDIA_REF = re.compile(r"(!\[[^\]]*\]\()([^)]+)(\))")


def _relativize_media_refs(markdown_text: str, staging_dir: Path) -> str:
    """Pandoc's docx reader writes ABSOLUTE filesystem paths into image
    references when `--extract-media` is given an absolute directory (this
    is pandoc's own behavior, not a defect in our cleanup pipeline) --
    e.g. `![alt](/abs/staging/raw/media/rId9.png)`. package.py's media
    handling treats any absolute reference as a rejected security/
    integrity violation (spec requirement: chunk content must never carry
    a path that could read/write outside the package), so this step
    normalizes pandoc's own absolute output back to a path relative to
    `staging_dir` (the same base directory package.py resolves refs
    against) BEFORE the cleanup pipeline or packaging ever sees it. This
    keeps package.py's rejection rule meaningful for content that
    legitimately shouldn't contain absolute/traversal paths, without
    forcing it to special-case "unless it came from pandoc".

    Uses `.absolute()`, not `.resolve()`: `.resolve()` also follows
    symlinks (e.g. macOS's `/var -> /private/var`), which would produce a
    string that no longer matches the literal path pandoc was invoked
    with (and therefore no longer matches the literal path pandoc wrote
    into its own output), causing every ref to be missed. `staging_dir`
    is made absolute the same way before being passed to pandoc in
    `run_pandoc_extraction`, so the two stay byte-for-byte comparable.
    """
    staging_dir_str = str(Path(staging_dir).absolute())

    def _replace(match: "re.Match") -> str:
        prefix, ref, suffix = match.group(1), match.group(2), match.group(3)
        if ref.startswith(("http://", "https://")):
            return match.group(0)
        if ref.startswith(staging_dir_str + "/"):
            ref = ref[len(staging_dir_str) + 1:]
        return f"{prefix}{ref}{suffix}"

    return _ABS_MEDIA_REF.sub(_replace, markdown_text)


def run_pandoc_extraction(source: Path, staging_dir: Path) -> Path:
    """Run pandoc once against `source`, extracting markdown + media into
    `staging_dir`, and return the path to the extracted markdown file.
    The only place in this module that shells out to `pandoc`.

    `--extract-media` is given `staging_dir` itself (not a `media`
    subdirectory of it): pandoc always creates its own `media/` subfolder
    under whatever directory it's given, so passing `staging_dir/media`
    here would double-nest into `staging_dir/media/media/...` while
    markdown refs still only say `media/...`.
    """
    staging_dir = Path(staging_dir).absolute()
    staging_dir.mkdir(parents=True, exist_ok=True)
    media_dir = staging_dir / "media"
    extracted_md = staging_dir / "extracted.md"
    subprocess.run(
        [
            "pandoc",
            "-t", "markdown",
            f"--extract-media={staging_dir}",
            "--wrap=none",
            str(source),
            "-o", str(extracted_md),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    # --extract-media only creates the directory when there is at least
    # one media file; downstream steps (legacy conversion, media copy)
    # assume it always exists.
    media_dir.mkdir(parents=True, exist_ok=True)
    return extracted_md


def _run_conversion_pipeline(
    source: Path,
    plan: "contracts.ConversionPlan",
    staging_root: Path,
    canonical_dir: Path,
):
    """Shared core of `convert_document`/`convert_and_promote`: pandoc
    extraction -> cleanup -> legacy media -> reconcile/slice -> package
    build, writing the canonical package to `canonical_dir` and pandoc's
    raw extraction under `staging_root / "_staging" / "raw"`. Returns
    `(manifest, cleaned_markdown_text)` -- the cleaned text is needed by
    `validate_canonical.validate_canonical_package`'s content-loss/
    duplication check, which `convert_document` (Task 9's original,
    narrower contract) does not expose but `convert_and_promote` (Task 11)
    does.

    Preconditions (all three enforced before any pandoc/file work
    happens, reusing Task 7's plans.py so there is exactly one
    implementation of each check):
        - plans.verify_plan_against_source: source file on disk still
          matches the sha256 recorded in the plan.
        - plans.verify_plan_integrity: the plan's own plan_id still
          matches its content (not hand-tampered).
        - plans.require_confirmed: plan.confirmation.status == "confirmed".
    """
    source = Path(source)
    staging_root = Path(staging_root)
    canonical_dir = Path(canonical_dir)

    plans.verify_plan_against_source(plan, source)
    plans.verify_plan_integrity(plan)
    plans.require_confirmed(plan)

    staging_dir = staging_root / "_staging" / "raw"
    extracted_md_path = run_pandoc_extraction(source, staging_dir)
    media_dir = staging_dir / "media"

    text = extracted_md_path.read_text()
    text = _relativize_media_refs(text, staging_dir)
    text = apply_cleanup_pipeline(text)

    rename_map = emf_convert.convert_legacy_media(media_dir)
    for old_name, new_name in rename_map.items():
        text = text.replace(f"media/{old_name}", f"media/{new_name}")

    sliced_document = chunking.reconcile_and_slice(plan.chunk_anchors, text)

    # `staging_dir` (not `media_dir`) is passed as the media reference base:
    # cleaned markdown refs look like "media/imageN.png", i.e. relative to
    # the raw extraction dir that CONTAINS the media/ subfolder, not
    # relative to media/ itself.
    if plan.strategy == "grouped":
        manifest = package.build_grouped_canonical_package(
            plan, sliced_document, staging_dir, canonical_dir
        )
    else:
        manifest = package.build_canonical_package(
            plan, sliced_document, staging_dir, canonical_dir
        )
    return manifest, text


def convert_document(
    source: Path,
    plan: "contracts.ConversionPlan",
    output_dir: Path,
) -> "contracts.Manifest":
    """Convert `source` (a real .docx) into a staged canonical-content
    package under `output_dir/canonical-content`, using `plan` (a
    CONFIRMED ConversionPlan) to drive chunk boundaries.

    This is Task 9's original entry point: it writes directly to
    `output_dir/canonical-content` with no validation or promotion step
    (those are `validate_canonical.py` and `convert_and_promote` below).
    Preserved unchanged so existing callers/tests keep working; new
    callers that want the full validate-then-atomically-promote pipeline
    should use `convert_and_promote` instead.
    """
    output_dir = Path(output_dir)
    manifest, _cleaned_text = _run_conversion_pipeline(
        source, plan, output_dir, output_dir / "canonical-content"
    )
    return manifest


def convert_and_promote(
    source: Path,
    plan: "contracts.ConversionPlan",
    output_root: Path,
    final_dir: "Path | None" = None,
    disposition_path: "Path | None" = None,
    plugin_version: str = atomic_output.DEFAULT_PLUGIN_VERSION,
):
    """Full spec Section 13 pipeline: build the canonical package in a
    fresh unique staging directory under `output_root`, validate it
    there, and only promote it to `final_dir` (default
    `output_root / "canonical-content"`) if validation allows it --
    PASS outright, or WARN with every warning dispositioned via
    `disposition_path`. A FAIL (or an undispositioned WARN) leaves
    `final_dir` completely untouched and retains the staging directory
    on disk for diagnosis.

    Returns `(manifest, validation_report, promoted: bool, staging_dir)`.
    `staging_dir` here is the package directory itself (i.e. what would
    become `final_dir` on success) -- always returned so a caller can
    inspect a failed run's staged output.
    """
    source = Path(source)
    output_root = Path(output_root)
    final_dir = Path(final_dir) if final_dir is not None else output_root / "canonical-content"

    run_staging_root = atomic_output.create_staging_dir(output_root, prefix="run")
    package_staging_dir = run_staging_root / "canonical-content"

    manifest, cleaned_text = _run_conversion_pipeline(
        source, plan, run_staging_root, package_staging_dir
    )

    atomic_output.write_generator_info(package_staging_dir, plugin_version=plugin_version)

    validation_report = validate_canonical.validate_canonical_package(
        package_staging_dir, plan, source_path=source, cleaned_markdown_text=cleaned_text
    )
    validate_canonical.write_validation_report(validation_report, package_staging_dir)

    promotable = validation_report.status == "PASS"
    if validation_report.status == "WARN":
        disp_path = disposition_path or (package_staging_dir / "warning-disposition.json")
        check = dispositions.apply_disposition(validation_report, disp_path)
        promotable = check.promotable

    if promotable:
        atomic_output.promote(package_staging_dir, final_dir)
        return manifest, validation_report, True, final_dir

    return manifest, validation_report, False, package_staging_dir
