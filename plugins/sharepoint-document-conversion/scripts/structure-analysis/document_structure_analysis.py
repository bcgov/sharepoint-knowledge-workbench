"""document_structure_analysis.py
==============================

Purpose:
    Public interface for the `document-structure-analysis` plugin: consumes a `normalized-source-document` v1 dict (produced by `source-document- extraction`'s `extraction.extract_and_normalize`) and produces an `analysis-plan` v1 dict, validated against this plugin's own `plan_schema.analysis_plan` module.

Key Input Dependencies:
    - sys
    - pathlib
    - identity
    - plans
    - topic_grouping
    - plan_schema.analysis_plan

Public interface for the `document-structure-analysis` plugin: consumes a
`normalized-source-document` v1 dict (produced by `source-document-
extraction`'s `extraction.extract_and_normalize`) and produces an
`analysis-plan` v1 dict, validated against this plugin's own
`plan_schema.analysis_plan` module. This plugin is the sole producer of
that contract; `structured-content-assembly` never imports this module directly --
it consumes the dict this function returns (after human confirmation).

This module never re-parses headings or re-detects defect signals --
those are `source-document-extraction`'s job and already present on the
input dict. It reasons *about* those observations: strategy
recommendation, topic-boundary detection, and structural-anchor identity.

Key Functions:
    - recommend_strategy(): Choose single-document or chunked processing.
    - _topic_analysis(): Build topic previews and confirmed-root data.
    - _analysis_warnings(): Translate source defects and topic decisions.
    - recommend_from_normalized(): Validate and return a draft analysis plan.

Key Functions Index:
    - recommend_strategy()
    - _topic_analysis()
    - _analysis_warnings()
    - recommend_from_normalized()"""

from __future__ import annotations

import sys
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import identity  # noqa: E402
import plans  # noqa: E402
import topic_grouping  # noqa: E402
from plan_schema.analysis_plan import (  # noqa: E402
    SourceFingerprint,
    StructuralAnchor,
    validate as validate_analysis_plan,
)

# ---------------------------------------------------------------------------
# Recommendation heuristics -- advisory, configurable constants only.
# Nothing here may branch on a literal heading string.
# ---------------------------------------------------------------------------

MIN_HEADINGS_FOR_CHUNKING = 6
MIN_LINES_FOR_CHUNKING = 500
MIN_REPEATED_PATHS_FOR_CHUNKING = 1


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


def _topic_analysis(headings: list) -> dict:
    """Build topic previews, root confirmations, and classification summaries."""
    heading_classifications = topic_grouping.classify_headings(headings)
    topic_boundaries = topic_grouping.compute_topic_boundaries(headings)
    root_classifications_by_path_occurrence = {
        (tuple(classification["path"]), classification["occurrence"]): classification
        for classification in heading_classifications
        if classification["physical_boundary"]
    }
    proposed_topics = [
        {
            "topic_id": boundary.topic_id,
            "title": boundary.title,
            "first_anchor_path": list(boundary.members[0].path),
            "anchor_count": len(boundary.members),
            "child_heading_count": len(boundary.members) - 1,
            "approx_size_chars": sum(len(member.text) for member in boundary.members),
            "source_level": root_classifications_by_path_occurrence[
                (tuple(boundary.members[0].path), boundary.members[0].occurrence)
            ]["source_level"],
            "classification": root_classifications_by_path_occurrence[
                (tuple(boundary.members[0].path), boundary.members[0].occurrence)
            ]["classification"],
        }
        for boundary in topic_boundaries
    ]
    return {
        "proposed_topics": proposed_topics,
        "confirmed_topic_roots": [
            {
                "source_heading_path": list(classification["path"]),
                "occurrence": classification["occurrence"],
            }
            for classification in heading_classifications
            if classification["physical_boundary"]
        ],
        "root_levels_used": sorted(
            {
                classification["source_level"]
                for classification in heading_classifications
                if classification["physical_boundary"]
            }
        ),
        "ambiguous_roots": [
            classification
            for classification in heading_classifications
            if classification["classification"] == "ambiguous-root"
        ],
        "promoted_roots": [
            classification
            for classification in heading_classifications
            if classification["classification"] == "promoted-root"
        ],
    }


def _analysis_warnings(
    defect_signals: dict,
    root_levels_used: list,
    promoted_roots: list,
    ambiguous_roots: list,
) -> list[str]:
    """Describe observed source defects and topic-root decisions for review."""
    warnings = []
    if defect_signals["raw_toc_detected"]:
        warnings.append("raw Word TOC field dump detected in source")
    if defect_signals["glued_images"]:
        warnings.append("images glued to heading/list lines detected")
    if defect_signals["pandoc_attrs"]:
        warnings.append("pandoc attribute syntax detected")
    if defect_signals["bold_wrapped_headings"]:
        warnings.append("whole-heading-wrapped bold/italic emphasis detected")
    if len(root_levels_used) > 1:
        warnings.append(
            "MIXED_LOGICAL_ROOT_LEVELS: proposed topic roots use inconsistent "
            f"source heading levels {root_levels_used} -- review proposed_topics "
            "before confirming the grouped strategy"
        )
    for classification in promoted_roots:
        warnings.append(
            f"PROMOTED_TOPIC_ROOT: heading {classification['text']!r} "
            f"(source level {classification['source_level']}) treated as a "
            "topic root though its level differs from the document's opening "
            "heading level"
        )
    for classification in ambiguous_roots:
        warnings.append(
            f"AMBIGUOUS_TOPIC_ROOT: heading {classification['text']!r} "
            f"(source level {classification['source_level']}) could be a "
            "topic root or a genuine nested child -- treated as an internal "
            "heading by default; review before confirming"
        )
    return warnings


def recommend_from_normalized(normalized_source_document: dict) -> dict:
    """Produce an `analysis-plan` v1 dict from a `normalized-source-document`
    v1 dict: chunking-strategy recommendation, structural anchors (stable
    chunk identity), topic-boundary preview, and a draft `ConversionPlan`
    (`confirmation.status == "draft"`).

    Never mutates `normalized_source_document`. Never writes to disk --
    the caller (currently `docx-to-content`'s compatibility orchestrator)
    is responsible for persisting the result.
    """
    headings = normalized_source_document["headings"]
    repeated_paths_count = len(normalized_source_document["repeated_heading_paths"])
    line_count = len(normalized_source_document["markdown_text"].splitlines())

    recommendation = recommend_strategy(
        heading_count=len(headings),
        repeated_path_count=repeated_paths_count,
        line_count=line_count,
    )

    source_fingerprint = SourceFingerprint(
        path=normalized_source_document["source_path"],
        sha256=normalized_source_document["source_content_sha256"],
        size_bytes=normalized_source_document["source_size_bytes"],
    )

    # --- structural anchors (identity.py; never raw line offsets) ---
    chunk_anchors = [
        StructuralAnchor(
            stable_key=identity.make_chunk_id(h["path"], h["occurrence"]),
            heading_text=h["text"],
            heading_level=h["level"],
            occurrence=h["occurrence"],
            source_heading_path=list(h["path"]),
        )
        for h in headings
    ]

    candidate_chunk_level = 1

    topic_analysis = _topic_analysis(headings)
    proposed_topics = topic_analysis["proposed_topics"]
    confirmed_topic_roots = topic_analysis["confirmed_topic_roots"]
    analysis_warnings = _analysis_warnings(
        normalized_source_document["defect_signals"],
        topic_analysis["root_levels_used"],
        topic_analysis["promoted_roots"],
        topic_analysis["ambiguous_roots"],
    )

    # media_decisions is deliberately left None here: proposing preamble
    # media decisions requires filesystem access to the extracted media
    # directory, which this function's normalized-source-document-only
    # input does not carry. The compatibility orchestrator merges media
    # proposals in via `plans.apply_media_decision` after this call
    # returns, before writing the draft plan to disk.
    plan = plans.build_draft_plan(
        source_fingerprint=source_fingerprint,
        strategy=recommendation["strategy"],
        chunk_level=candidate_chunk_level,
        chunk_anchors=chunk_anchors,
        analysis_warnings=analysis_warnings,
        confirmed_topic_roots=confirmed_topic_roots,
        media_decisions=None,
    )

    result = plan.to_dict()
    result["proposed_topics"] = proposed_topics
    result["recommendation"] = {
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
    }
    validate_analysis_plan(result)
    return result
