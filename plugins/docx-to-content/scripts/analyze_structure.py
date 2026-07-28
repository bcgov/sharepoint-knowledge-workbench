"""
analyze_structure.py
=====================

Implements the `analyze-document` skill's business logic (spec Section 7.1):
runs pandoc once against a real source `.docx` into the transitory
`analysis/raw/` folder (spec Section 6.1), analyzes the resulting markdown's
structure, and produces a draft `ConversionPlan` (never a confirmed one, and
never canonical content).

Required analysis (spec 7.1), each surfaced under `analysis-report.json`:
    - source fingerprint (sha256 + size_bytes)
    - dependency versions (pandoc)
    - heading counts by level, reconstructed heading paths, repeated paths
    - local image counts/formats
    - raw TOC evidence and known pandoc defect signals (reusing
      `pandoc_fixes.toc.strip_raw_toc`, `pandoc_fixes.images.fix_glued_images`,
      and `pandoc_fixes.attrs.strip_pandoc_attrs` detection logic rather than
      re-implementing pattern matching)
    - a single/chunked strategy recommendation driven by named, configurable
      constants -- never a branch on a literal heading string.

Function Index:
    - analyze_document(source, output_dir) -> AnalysisResult
    - detect_raw_toc(markdown_text) -> bool
    - detect_defect_signals(markdown_text) -> dict
    - parse_headings(markdown_text) -> list[dict]  (level, text, path, occurrence)
    - recommend_strategy(heading_count, repeated_path_count, line_count) -> dict
"""

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import contracts  # noqa: E402
import dependencies  # noqa: E402
import hashing  # noqa: E402
import identity  # noqa: E402
import plans  # noqa: E402
from pandoc_fixes.attrs import strip_pandoc_attrs  # noqa: E402
from pandoc_fixes.heading_emphasis import strip_whole_heading_emphasis  # noqa: E402
from pandoc_fixes.images import fix_glued_images  # noqa: E402
from pandoc_fixes.toc import _TOC_SLUG_LINE, _TOC_LINK_LINE, strip_raw_toc  # noqa: E402

# ---------------------------------------------------------------------------
# Recommendation heuristics -- advisory, configurable constants only.
# Nothing here may branch on a literal heading string (spec 7.1: "must not
# encode any pilot-document-specific heading names).
# ---------------------------------------------------------------------------

MIN_HEADINGS_FOR_CHUNKING = 6
MIN_LINES_FOR_CHUNKING = 500
MIN_REPEATED_PATHS_FOR_CHUNKING = 1

_HEADING_RE_TEMPLATE = r"^(#{{1,6}})\s+(.+?)\s*$"

import re  # noqa: E402

_HEADING_LINE = re.compile(_HEADING_RE_TEMPLATE.format(), re.MULTILINE)

_IMAGE_REF = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")


def _normalize_heading_text(text: str) -> str:
    """Apply the same whole-heading-emphasis normalization that convert-time
    cleanup applies, to a single heading's text.

    Structural anchor identity (`identity.make_chunk_id`) is computed from
    heading path text both at analysis time (this module, against RAW
    pandoc extraction) and at reconciliation time (`chunking.py`, against
    the CLEANED document, after `pandoc_fixes.heading_emphasis.
    strip_whole_heading_emphasis` has already run as part of the real
    convert pipeline). If analysis computed identity from raw, un-normalized
    text while reconciliation recomputed it from normalized text, the two
    would never match and every affected heading would fail to reconcile
    (MissingAnchorError) during a real conversion. Normalizing here, in the
    single function both `parse_headings` (analysis) and `chunking.
    parse_headings_with_lines` (reconciliation) call, guarantees both sides
    always compute identity from the same normalized text -- reconciliation
    call sites operate on already-cleaned text, so this is a no-op there.
    """
    stripped = strip_whole_heading_emphasis(f"# {text}\n")
    return stripped[2:].rstrip("\n")


@dataclass
class AnalysisResult:
    report: dict
    plan: contracts.ConversionPlan


# ---------------------------------------------------------------------------
# Heading parsing / structural paths
# ---------------------------------------------------------------------------

def iter_heading_matches(markdown_text: str):
    """Low-level ATX heading walk shared by `parse_headings` (this module,
    Task 6 draft-plan analysis) and `chunking.py`'s cleaned-document heading
    index (Task 8, post-cleanup anchor reconciliation), so the path/
    occurrence computation exists in exactly one place rather than being
    copy-pasted into a second implementation.

    Yields `(match, level, text, path, occurrence)` in document order, where
    `path` is the full heading path (ancestor chain + this heading's text,
    reconstructed with a level-based stack so skipped levels -- e.g. an H1
    followed directly by an H3 -- are handled gracefully) and `occurrence`
    disambiguates two headings that share an identical full path.
    """
    stack = []  # list of (level, text)
    occurrence_counts = {}  # tuple(path) -> count seen so far

    for match in _HEADING_LINE.finditer(markdown_text):
        level = len(match.group(1))
        text = _normalize_heading_text(match.group(2).strip())
        if not text:
            continue

        while stack and stack[-1][0] >= level:
            stack.pop()
        stack.append((level, text))

        path = [t for _, t in stack]
        path_key = tuple(path)
        occurrence_counts[path_key] = occurrence_counts.get(path_key, 0) + 1
        occurrence = occurrence_counts[path_key]

        yield match, level, text, path, occurrence


def parse_headings(markdown_text: str) -> list:
    """Parse ATX headings from pandoc markdown output into an ordered list
    of dicts: {"level": int, "text": str, "path": list[str], "occurrence": int}.

    Thin wrapper over `iter_heading_matches` that drops the regex match
    object (callers needing source position -- e.g. `chunking.py` -- should
    use `iter_heading_matches` directly instead of re-parsing).
    """
    return [
        {"level": level, "text": text, "path": path, "occurrence": occurrence}
        for _match, level, text, path, occurrence in iter_heading_matches(markdown_text)
    ]


def _counts_by_level(headings: list) -> dict:
    counts = {}
    for h in headings:
        counts[h["level"]] = counts.get(h["level"], 0) + 1
    return counts


def _repeated_heading_texts(headings: list) -> dict:
    text_counts = {}
    for h in headings:
        text_counts[h["text"]] = text_counts.get(h["text"], 0) + 1
    return {text: count for text, count in text_counts.items() if count > 1}


def _repeated_paths(headings: list) -> dict:
    path_counts = {}
    for h in headings:
        key = tuple(h["path"])
        path_counts[key] = path_counts.get(key, 0) + 1
    return {path: count for path, count in path_counts.items() if count > 1}


# ---------------------------------------------------------------------------
# Image counting
# ---------------------------------------------------------------------------

def _image_stats(media_dir: Path) -> dict:
    if not media_dir.exists():
        return {"count": 0, "formats": []}
    files = [p for p in media_dir.rglob("*") if p.is_file()]
    formats = sorted({p.suffix.lstrip(".").lower() for p in files if p.suffix})
    return {"count": len(files), "formats": formats}


# ---------------------------------------------------------------------------
# Raw TOC evidence / known pandoc defect signals
# ---------------------------------------------------------------------------

def detect_raw_toc(markdown_text: str) -> bool:
    """Reuses pandoc_fixes.toc.strip_raw_toc's detection logic: if stripping
    raw-TOC field dumps changes the text, raw TOC evidence was present."""
    return strip_raw_toc(markdown_text) != markdown_text


def detect_defect_signals(markdown_text: str) -> dict:
    """Reuses pandoc_fixes.images.fix_glued_images,
    pandoc_fixes.attrs.strip_pandoc_attrs, and
    pandoc_fixes.heading_emphasis.strip_whole_heading_emphasis detection
    logic (Task 2 / Task 17A.1) rather than re-implementing pattern
    matching from scratch."""
    return {
        "raw_toc_detected": detect_raw_toc(markdown_text),
        "glued_images": fix_glued_images(markdown_text) != markdown_text,
        "pandoc_attrs": strip_pandoc_attrs(markdown_text) != markdown_text,
        "bold_wrapped_headings": strip_whole_heading_emphasis(markdown_text) != markdown_text,
    }


# ---------------------------------------------------------------------------
# Extended analysis statistics (Task 17A.1 #4) -- measured directly from the
# already-extracted markdown text; "not measured" is reported (never a
# fabricated number) if a statistic cannot be measured with reasonable
# effort using pure string/regex analysis (no re-invoking pandoc).
# ---------------------------------------------------------------------------

_TABLE_SEPARATOR_ROW = re.compile(r'^\s*\|?\s*:?-{1,}:?\s*(\|\s*:?-{1,}:?\s*)*\|?\s*$', re.MULTILINE)
_FOOTNOTE_REFERENCE = re.compile(r'\[\^([\w-]+)\](?!:)')
_FOOTNOTE_DEFINITION_LINE = re.compile(r'^\[\^([\w-]+)\]:', re.MULTILINE)
_LOCAL_LINK = re.compile(r'(?<!\!)\[[^\]]*\]\(#[^)]*\)')
_IMAGE_REFERENCE = re.compile(r'!\[[^\]]*\]\([^)]*\)')


def compute_statistics(markdown_text: str) -> dict:
    """Measure extended statistics directly from already-extracted
    markdown text: table count (by counting separator rows), footnote
    reference/definition counts, local document link count, total image
    reference count, and generated-TOC-entries-detected. Each of these is
    reliably measurable with plain regex analysis over the text pandoc
    already produced, so none fall back to "not measured" here -- that
    literal is reserved for a statistic this function cannot compute (none
    currently), per the "where feasible" requirement.
    """
    table_count = len(_TABLE_SEPARATOR_ROW.findall(markdown_text))
    footnote_reference_count = len(
        [m for m in _FOOTNOTE_REFERENCE.finditer(markdown_text)]
    )
    footnote_definition_count = len(_FOOTNOTE_DEFINITION_LINE.findall(markdown_text))
    local_link_count = len(_LOCAL_LINK.findall(markdown_text))
    image_reference_count = len(_IMAGE_REFERENCE.findall(markdown_text))

    toc_bookmark_entries = len(_TOC_LINK_LINE.findall(markdown_text))
    toc_slug_entries = len(_TOC_SLUG_LINE.findall(markdown_text))
    generated_toc_entries_detected = toc_bookmark_entries + toc_slug_entries

    return {
        "table_count": table_count,
        "footnote_reference_count": footnote_reference_count,
        "footnote_definition_count": footnote_definition_count,
        "local_link_count": local_link_count,
        "image_reference_count": image_reference_count,
        "generated_toc_entries_detected": generated_toc_entries_detected,
    }


# ---------------------------------------------------------------------------
# Recommendation
# ---------------------------------------------------------------------------

def recommend_strategy(heading_count: int, repeated_path_count: int, line_count: int) -> dict:
    """Recommend "single" or "chunked" using only the named constants above
    -- no literal heading text is ever inspected here (source-agnostic)."""
    reasons = []
    chunked = False

    if heading_count >= MIN_HEADINGS_FOR_CHUNKING:
        chunked = True
        reasons.append(
            f"heading count ({heading_count}) meets/exceeds "
            f"MIN_HEADINGS_FOR_CHUNKING ({MIN_HEADINGS_FOR_CHUNKING})"
        )
    if repeated_path_count >= MIN_REPEATED_PATHS_FOR_CHUNKING:
        chunked = True
        reasons.append(
            f"{repeated_path_count} repeated heading path(s) detected "
            f"(>= MIN_REPEATED_PATHS_FOR_CHUNKING={MIN_REPEATED_PATHS_FOR_CHUNKING})"
        )
    if line_count >= MIN_LINES_FOR_CHUNKING:
        chunked = True
        reasons.append(
            f"line count ({line_count}) meets/exceeds "
            f"MIN_LINES_FOR_CHUNKING ({MIN_LINES_FOR_CHUNKING})"
        )

    if not chunked:
        reasons.append(
            f"heading count ({heading_count}) below MIN_HEADINGS_FOR_CHUNKING "
            f"({MIN_HEADINGS_FOR_CHUNKING}), no repeated heading paths, and "
            f"line count ({line_count}) below MIN_LINES_FOR_CHUNKING "
            f"({MIN_LINES_FOR_CHUNKING})"
        )

    return {"strategy": "chunked" if chunked else "single", "reasons": reasons}


# ---------------------------------------------------------------------------
# Pandoc invocation into the transitory raw/ folder
# ---------------------------------------------------------------------------

def _run_pandoc_raw(source: Path, raw_dir: Path) -> Path:
    raw_dir.mkdir(parents=True, exist_ok=True)
    media_dir = raw_dir / "media"
    extracted_md = raw_dir / "extracted.md"
    subprocess.run(
        [
            "pandoc",
            "-t", "markdown",
            f"--extract-media={media_dir}",
            "--wrap=none",
            str(source),
            "-o", str(extracted_md),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    # extract-media only creates the directory if there is at least one
    # media file; the analysis package layout (spec 6.1) always includes
    # raw/media, so ensure it exists even for image-free documents.
    media_dir.mkdir(parents=True, exist_ok=True)
    return extracted_md


# ---------------------------------------------------------------------------
# Top-level entry point
# ---------------------------------------------------------------------------

def analyze_document(source, output_dir) -> AnalysisResult:
    """Analyze a real source .docx and produce a draft ConversionPlan plus
    an analysis report, writing both (and the transitory raw/ pandoc output)
    under `output_dir`, matching the analysis package layout in spec 6.1:

        analysis/
          analysis-report.json
          conversion-plan.draft.json
          raw/
            extracted.md
            media/

    Never writes a `canonical-content/` folder and never promotes the plan
    beyond `confirmation.status == "draft"`.
    """
    source = Path(source)
    output_dir = Path(output_dir)

    if not source.exists() or not source.is_file():
        raise FileNotFoundError(f"source file not found: {source}")

    pandoc_status = dependencies.probe_pandoc()
    if not pandoc_status.available:
        raise dependencies.MissingDependencyError("pandoc")

    output_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = output_dir / "raw"
    extracted_md_path = _run_pandoc_raw(source, raw_dir)
    markdown_text = extracted_md_path.read_text()

    # --- fingerprint ---
    sha256 = hashing.content_hash(source.read_bytes())
    size_bytes = source.stat().st_size
    source_fingerprint = contracts.SourceFingerprint(
        path=str(source), sha256=sha256, size_bytes=size_bytes,
    )

    # --- headings ---
    headings = parse_headings(markdown_text)
    counts_by_level = _counts_by_level(headings)
    repeated_paths = _repeated_paths(headings)
    repeated_heading_texts = _repeated_heading_texts(headings)

    # --- images ---
    image_stats = _image_stats(raw_dir / "media")

    # --- defect signals ---
    defect_signals = detect_defect_signals(markdown_text)

    # --- extended statistics (Task 17A.1 #4) ---
    statistics = compute_statistics(markdown_text)

    # --- recommendation ---
    line_count = len(markdown_text.splitlines())
    recommendation = recommend_strategy(
        heading_count=len(headings),
        repeated_path_count=len(repeated_paths),
        line_count=line_count,
    )

    # --- structural anchors (identity.py; never raw line offsets) ---
    chunk_anchors = [
        contracts.StructuralAnchor(
            stable_key=identity.make_chunk_id(h["path"], h["occurrence"]),
            heading_text=h["text"],
            heading_level=h["level"],
            occurrence=h["occurrence"],
            source_heading_path=list(h["path"]),
        )
        for h in headings
    ]

    candidate_chunk_level = 1

    report = {
        "source": source_fingerprint.to_dict(),
        "dependencies": {
            "pandoc": {
                "available": pandoc_status.available,
                "version": pandoc_status.version,
                "path": pandoc_status.path,
            },
        },
        "raw": {
            "markdown_path": str(extracted_md_path.relative_to(output_dir)),
            "media_path": str((raw_dir / "media").relative_to(output_dir)),
            "transitory": True,
            "note": "raw/ is disposable working output from a single pandoc "
                    "pass; it is not part of the canonical content package "
                    "and must not be treated as a permanent artifact.",
        },
        "headings": {
            "counts_by_level": counts_by_level,
            "total": len(headings),
            "paths": [h["path"] for h in headings],
            "repeated_heading_texts": repeated_heading_texts,
            "repeated_heading_paths": [list(p) for p in repeated_paths.keys()],
        },
        "images": image_stats,
        "defect_signals": defect_signals,
        "statistics": statistics,
        "recommendation": {
            "strategy": recommendation["strategy"],
            "reasons": recommendation["reasons"],
            "candidate_chunk_level": candidate_chunk_level,
            "chunk_level_note": (
                "chunk_level/strategy are ADVISORY recommendations only. "
                "chunk_anchors -- not chunk_level -- determine the actual "
                "physical chunk boundaries used at convert time; every "
                "heading becomes a chunk_anchor regardless of chunk_level's "
                "value."
            ),
        },
    }

    analysis_warnings = []
    if defect_signals["raw_toc_detected"]:
        analysis_warnings.append("raw Word TOC field dump detected in source")
    if defect_signals["glued_images"]:
        analysis_warnings.append("images glued to heading/list lines detected")
    if defect_signals["pandoc_attrs"]:
        analysis_warnings.append("pandoc attribute syntax detected")
    if defect_signals["bold_wrapped_headings"]:
        analysis_warnings.append("whole-heading-wrapped bold/italic emphasis detected")

    plan = plans.build_draft_plan(
        source_fingerprint=source_fingerprint,
        strategy=recommendation["strategy"],
        chunk_level=candidate_chunk_level,
        chunk_anchors=chunk_anchors,
        analysis_warnings=analysis_warnings,
    )

    (output_dir / "analysis-report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True)
    )
    (output_dir / "conversion-plan.draft.json").write_text(
        json.dumps(plan.to_dict(), indent=2, sort_keys=True)
    )

    return AnalysisResult(report=report, plan=plan)
