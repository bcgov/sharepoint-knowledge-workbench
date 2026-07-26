"""
plans.py
========

Draft `ConversionPlan` construction (spec Section 6.2 / 7.1). This module
turns the structural analysis produced by `analyze_structure.py` into a
`contracts.ConversionPlan` with `confirmation.status == "draft"` — it never
promotes a plan to "confirmed" (that is Task 7's `confirm` command) and
never writes canonical content.

Function Index:
    - build_draft_plan(source_fingerprint, strategy, chunk_level,
                        chunk_anchors, content_type, template_profile,
                        analysis_warnings) -> contracts.ConversionPlan
"""

import sys
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import contracts  # noqa: E402
import hashing  # noqa: E402

DEFAULT_CONTENT_TYPE = "manual"
DEFAULT_TEMPLATE_PROFILE = "source-structure-v1"


def build_draft_plan(
    source_fingerprint: "contracts.SourceFingerprint",
    strategy: str,
    chunk_level: int,
    chunk_anchors: list,
    content_type: str = DEFAULT_CONTENT_TYPE,
    template_profile: str = DEFAULT_TEMPLATE_PROFILE,
    analysis_warnings: "list | None" = None,
) -> "contracts.ConversionPlan":
    """Build a draft ConversionPlan (confirmation.status == "draft").

    `plan_id` is computed from normalized plan content (excluding the
    `plan_id` field itself and the `confirmed_at` timestamp), via
    `hashing.compute_plan_id`, matching the spec's "plan_id is calculated
    from normalized plan content excluding the plan_id field itself" rule.
    """
    plan = contracts.ConversionPlan(
        schema_version=contracts.SUPPORTED_SCHEMA_VERSION,
        plan_id="",
        source=source_fingerprint,
        strategy=strategy,
        chunk_level=chunk_level,
        chunk_anchors=list(chunk_anchors),
        content_type=content_type,
        template_profile=template_profile,
        confirmation=contracts.Confirmation(
            status="draft",
            confirmed_by="",
            confirmed_at="",
        ),
        analysis_warnings=list(analysis_warnings or []),
    )
    plan.plan_id = hashing.compute_plan_id(plan)
    return plan
