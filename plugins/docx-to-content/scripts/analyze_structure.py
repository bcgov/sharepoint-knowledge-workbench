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
      `pandoc.toc.strip_raw_toc`, `pandoc.images.fix_glued_images`,
      and `pandoc.attrs.strip_pandoc_attrs` detection logic rather than
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
import re
import sys
from dataclasses import dataclass
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import contracts  # noqa: E402
import hashing  # noqa: E402
import identity  # noqa: E402
import media_disposition  # noqa: E402
import plans  # noqa: E402
import topic_grouping  # noqa: E402

# Compatibility shim (Phase 4.5 Wave 2, retire per wave-1-decisions.json):
# these functions now live in the installed `source-document-extraction`
# package (flat `scripts/` layout, bare module names -- see
# docs/superpowers/plans/phase-4-5-evidence/wave-2-flat-scripts-correction.md)
# -- per the approved split
# (docs/superpowers/plans/phase-4-5-evidence/wave-1-analyze-structure-split-decision.md),
# every source-level *observation* function moved there. Imported here, not
# duplicated, so `docx-to-content` keeps working during the migration.
# Requires `source-document-extraction` to be `pip install -e`'d into
# whatever environment runs this plugin's tests -- a transition-only
# dependency, removed in Wave 7/8. Bare names resolve directly from the
# installed distribution since this plugin no longer ships same-named
# shim files of its own to shadow them.
import dependencies  # noqa: E402
from extraction import _run_pandoc_raw  # noqa: E402
from heading_parsing import (  # noqa: E402
    _counts_by_level,
    _image_stats,
    _normalize_heading_text,
    _repeated_heading_texts,
    _repeated_paths,
    compute_statistics,
    detect_defect_signals,
    detect_raw_toc,
    iter_heading_matches,
    parse_headings,
)

# ---------------------------------------------------------------------------
# Recommendation heuristics -- advisory, configurable constants only.
# Nothing here may branch on a literal heading string (spec 7.1: "must not
# encode any pilot-document-specific heading names).
# ---------------------------------------------------------------------------

MIN_HEADINGS_FOR_CHUNKING = 6
MIN_LINES_FOR_CHUNKING = 500
MIN_REPEATED_PATHS_FOR_CHUNKING = 1

# Used only to locate the first heading's start position for preamble
# slicing below -- the real heading-walk logic lives in
# source_document_extraction.heading_parsing.
_HEADING_LINE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)


@dataclass
class AnalysisResult:
    report: dict
    plan: contracts.ConversionPlan


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

    # --- preamble media disposition proposal (Task 18 general media
    # classification/disposition mechanism) ---
    first_heading_match = next(iter(_HEADING_LINE.finditer(markdown_text)), None)
    preamble_text = markdown_text[: first_heading_match.start()] if first_heading_match else markdown_text
    proposed_media_decisions = media_disposition.propose_media_decisions(
        preamble_text, raw_dir / "media"
    )

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

    # --- proposed topic-grouping preview (Task 17-topic-grouping, refined
    # by Task 18's mixed-level logical-root detection) ---
    heading_classifications = topic_grouping.classify_headings(headings)
    topic_boundaries = topic_grouping.compute_topic_boundaries(headings)
    root_classifications_by_path_occurrence = {
        (tuple(c["path"]), c["occurrence"]): c
        for c in heading_classifications
        if c["physical_boundary"]
    }
    proposed_topics = [
        {
            "topic_id": boundary.topic_id,
            "title": boundary.title,
            "first_anchor_path": list(boundary.members[0].path),
            "anchor_count": len(boundary.members),
            "child_heading_count": len(boundary.members) - 1,
            # Cheap heading-text-only size proxy at analysis time -- real
            # chunk-body sizes aren't known until cleaned markdown is
            # sliced in convert; this previews relative topic weight only.
            "approx_size_chars": sum(len(m.text) for m in boundary.members),
            "source_level": root_classifications_by_path_occurrence[
                (tuple(boundary.members[0].path), boundary.members[0].occurrence)
            ]["source_level"],
            "classification": root_classifications_by_path_occurrence[
                (tuple(boundary.members[0].path), boundary.members[0].occurrence)
            ]["classification"],
        }
        for boundary in topic_boundaries
    ]
    confirmed_topic_roots = [
        {"source_heading_path": list(c["path"]), "occurrence": c["occurrence"]}
        for c in heading_classifications
        if c["physical_boundary"]
    ]
    root_levels_used = sorted({c["source_level"] for c in heading_classifications if c["physical_boundary"]})
    ambiguous_roots = [c for c in heading_classifications if c["classification"] == "ambiguous-root"]
    promoted_roots = [c for c in heading_classifications if c["classification"] == "promoted-root"]

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
        "proposed_topics": proposed_topics,
        "proposed_preamble_media": proposed_media_decisions,
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
    if len(root_levels_used) > 1:
        analysis_warnings.append(
            "MIXED_LOGICAL_ROOT_LEVELS: proposed topic roots use inconsistent "
            f"source heading levels {root_levels_used} -- review proposed_topics "
            "before confirming the grouped strategy"
        )
    for c in promoted_roots:
        analysis_warnings.append(
            f"PROMOTED_TOPIC_ROOT: heading {c['text']!r} (source level {c['source_level']}) "
            "treated as a topic root though its level differs from the document's "
            "opening heading level"
        )
    for c in ambiguous_roots:
        analysis_warnings.append(
            f"AMBIGUOUS_TOPIC_ROOT: heading {c['text']!r} (source level {c['source_level']}) "
            "could be a topic root or a genuine nested child -- treated as an internal "
            "heading by default; review before confirming"
        )
    if proposed_media_decisions:
        analysis_warnings.append(
            f"MEDIA_REQUIRES_REVIEW: {len(proposed_media_decisions)} preamble media "
            "item(s) require classification/disposition review before confirming "
            "(see proposed_preamble_media)"
        )

    plan = plans.build_draft_plan(
        source_fingerprint=source_fingerprint,
        strategy=recommendation["strategy"],
        chunk_level=candidate_chunk_level,
        chunk_anchors=chunk_anchors,
        analysis_warnings=analysis_warnings,
        confirmed_topic_roots=confirmed_topic_roots,
        media_decisions=proposed_media_decisions or None,
    )

    (output_dir / "analysis-report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True)
    )
    (output_dir / "conversion-plan.draft.json").write_text(
        json.dumps(plan.to_dict(), indent=2, sort_keys=True)
    )

    return AnalysisResult(report=report, plan=plan)
