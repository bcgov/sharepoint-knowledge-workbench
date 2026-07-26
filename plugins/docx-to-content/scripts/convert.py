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

import chunking  # noqa: E402
import contracts  # noqa: E402
import emf_convert  # noqa: E402
import package  # noqa: E402
import plans  # noqa: E402
from pandoc_fixes.attrs import strip_pandoc_attrs  # noqa: E402
from pandoc_fixes.footnotes import clean_orphaned_footnotes  # noqa: E402
from pandoc_fixes.images import fix_glued_images  # noqa: E402
from pandoc_fixes.tables import fix_malformed_tables  # noqa: E402
from pandoc_fixes.toc import strip_raw_toc  # noqa: E402


def apply_cleanup_pipeline(markdown_text: str) -> str:
    """Apply the six pandoc_fixes cleanup steps in the exact spec Section
    7.2 order: attrs -> images -> toc -> tables -> footnotes. Order
    matters -- e.g. TOC-stripping must run after image-fixing so a raw
    Word TOC dump doesn't get misidentified/mangled while an image is
    still glued onto an adjacent heading line; running steps out of order
    can produce a different (wrong) result even though each step is
    individually correct in isolation. This is the sole place that order
    is encoded; `convert_document` calls this function rather than
    inlining the sequence a second time."""
    text = strip_pandoc_attrs(markdown_text)
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


def convert_document(
    source: Path,
    plan: "contracts.ConversionPlan",
    output_dir: Path,
) -> "contracts.Manifest":
    """Convert `source` (a real .docx) into a staged canonical-content
    package under `output_dir/canonical-content`, using `plan` (a
    CONFIRMED ConversionPlan) to drive chunk boundaries.

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
    output_dir = Path(output_dir)

    plans.verify_plan_against_source(plan, source)
    plans.verify_plan_integrity(plan)
    plans.require_confirmed(plan)

    staging_dir = output_dir / "_staging" / "raw"
    extracted_md_path = run_pandoc_extraction(source, staging_dir)
    media_dir = staging_dir / "media"

    text = extracted_md_path.read_text()
    text = _relativize_media_refs(text, staging_dir)
    text = apply_cleanup_pipeline(text)

    rename_map = emf_convert.convert_legacy_media(media_dir)
    for old_name, new_name in rename_map.items():
        text = text.replace(f"media/{old_name}", f"media/{new_name}")

    sliced_document = chunking.reconcile_and_slice(plan.chunk_anchors, text)

    canonical_dir = output_dir / "canonical-content"
    # `staging_dir` (not `media_dir`) is passed as the media reference base:
    # cleaned markdown refs look like "media/imageN.png", i.e. relative to
    # the raw extraction dir that CONTAINS the media/ subfolder, not
    # relative to media/ itself.
    manifest = package.build_canonical_package(
        plan, sliced_document, staging_dir, canonical_dir
    )
    return manifest
