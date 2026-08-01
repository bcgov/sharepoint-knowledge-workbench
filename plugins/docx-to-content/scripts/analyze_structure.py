"""
analyze_structure.py
=====================

Implements the `analyze-document` skill's business logic (spec Section 7.1)
as the **compatibility orchestrator** (Phase 4.5): composes the now-
installed `source-document-extraction` and `knowledge-analysis` packages
in sequence, then merges in the preamble-media-disposition proposal (still
local to this plugin -- `media_disposition.py` is `canonical-knowledge`-
domain, unmoved until Wave 4) and writes both output files, matching the
analysis package layout in spec 6.1. Produces a draft `ConversionPlan`
(never a confirmed one, and never canonical content).

Function Index:
    - analyze_document(source, output_dir) -> AnalysisResult
"""

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import media_disposition  # noqa: E402

# Compatibility shim (Phase 4.5, retire per wave-1-decisions.json): this
# orchestrator composes the installed source-document-extraction and
# knowledge-analysis packages -- see
# docs/superpowers/plans/phase-4-5-evidence/wave-2-flat-scripts-correction.md
# and wave-3-analysis-plan-split-decision.md. Requires both to be
# `pip install -e`'d into whatever environment runs this plugin's tests --
# a transition-only dependency, removed in Wave 7/8.
import dependencies  # noqa: E402
from extraction import extract_and_normalize  # noqa: E402
from analysis import recommend_from_normalized  # noqa: E402
from plan_schema import analysis_plan as contracts  # noqa: E402
import plan_hashing  # noqa: E402

# Used only to locate the first heading's start position for preamble
# slicing below -- the real heading-walk logic lives in
# source-document-extraction's heading_parsing / knowledge-analysis's
# recommend_from_normalized.
_HEADING_LINE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)


@dataclass
class AnalysisResult:
    report: dict
    plan: "contracts.ConversionPlan"


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

    # --- source-document-extraction: pandoc + source-level observations ---
    normalized = extract_and_normalize(source, output_dir)
    markdown_text = normalized["markdown_text"]
    raw_dir = output_dir / "raw"

    # --- preamble media disposition proposal (still local to this plugin;
    # canonical-knowledge domain, unmoved until Wave 4) ---
    first_heading_match = next(iter(_HEADING_LINE.finditer(markdown_text)), None)
    preamble_text = markdown_text[: first_heading_match.start()] if first_heading_match else markdown_text
    proposed_media_decisions = media_disposition.propose_media_decisions(
        preamble_text, raw_dir / "media"
    )

    # --- knowledge-analysis: strategy recommendation, topic-boundary
    # preview, structural anchors, draft plan (media_decisions=None) ---
    analysis_plan_dict = recommend_from_normalized(normalized)
    plan = contracts.ConversionPlan.from_dict(analysis_plan_dict)

    # --- merge the media proposal into the plan (recompute plan_id) ---
    analysis_warnings = list(plan.analysis_warnings)
    if proposed_media_decisions:
        analysis_warnings.append(
            f"MEDIA_REQUIRES_REVIEW: {len(proposed_media_decisions)} preamble media "
            "item(s) require classification/disposition review before confirming "
            "(see proposed_preamble_media)"
        )
        plan = contracts.ConversionPlan(
            schema_version=plan.schema_version,
            plan_id="",
            source=plan.source,
            strategy=plan.strategy,
            chunk_level=plan.chunk_level,
            chunk_anchors=plan.chunk_anchors,
            content_type=plan.content_type,
            template_profile=plan.template_profile,
            confirmation=plan.confirmation,
            analysis_warnings=analysis_warnings,
            confirmed_topic_roots=plan.confirmed_topic_roots,
            media_decisions=proposed_media_decisions,
        )
        plan.plan_id = plan_hashing.compute_plan_id(plan)

    report = {
        "source": {
            "path": normalized["source_path"],
            "sha256": normalized["source_content_sha256"],
            "size_bytes": normalized["source_size_bytes"],
        },
        "dependencies": normalized["dependencies"],
        "raw": {
            "markdown_path": str((raw_dir / "extracted.md").relative_to(output_dir)),
            "media_path": str((raw_dir / "media").relative_to(output_dir)),
            "transitory": True,
            "note": "raw/ is disposable working output from a single pandoc "
                    "pass; it is not part of the canonical content package "
                    "and must not be treated as a permanent artifact.",
        },
        "headings": {
            "counts_by_level": normalized["heading_counts_by_level"],
            "total": len(normalized["headings"]),
            "paths": [h["path"] for h in normalized["headings"]],
            "repeated_heading_texts": normalized["repeated_heading_texts"],
            "repeated_heading_paths": normalized["repeated_heading_paths"],
        },
        "proposed_topics": analysis_plan_dict["proposed_topics"],
        "proposed_preamble_media": proposed_media_decisions,
        "images": normalized["images"],
        "defect_signals": normalized["defect_signals"],
        "statistics": normalized["statistics"],
        "recommendation": analysis_plan_dict["recommendation"],
    }

    (output_dir / "analysis-report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True)
    )
    (output_dir / "conversion-plan.draft.json").write_text(
        json.dumps(plan.to_dict(), indent=2, sort_keys=True)
    )

    return AnalysisResult(report=report, plan=plan)
