"""
plans.py
========

Draft `ConversionPlan` construction (spec Section 6.2 / 7.1), plus (Task 7)
explicit confirmation and the plan/source verification checks that later
`convert`/`run` steps use as a precondition.

Function Index:
    - build_draft_plan(source_fingerprint, strategy, chunk_level,
                        chunk_anchors, content_type, template_profile,
                        analysis_warnings) -> contracts.ConversionPlan
    - confirm_plan(draft_plan, confirmed_by) -> contracts.ConversionPlan
        Builds a NEW confirmed ConversionPlan from a draft; never mutates
        the draft object passed in.
    - verify_plan_against_source(plan, source_path) -> None
    - verify_plan_integrity(plan) -> None
    - require_confirmed(plan) -> None
        These three plus `PlanVerificationError` are re-exported here from
        `plan_verification_core.py` (the single canonical implementation,
        also consumed cross-plugin by `canonical-knowledge` via a managed
        symlink) so existing callers of `plans.verify_plan_against_source`
        etc. are unaffected. See
        docs/superpowers/plans/phase-4-5-evidence/wave-9-duplication-remediation-report.md.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from plan_schema import analysis_plan as contracts  # noqa: E402
import plan_hashing as hashing  # noqa: E402
from plan_verification_core import (  # noqa: E402,F401
    PlanVerificationError,
    verify_plan_against_source,
    verify_plan_integrity,
    require_confirmed,
)

DEFAULT_CONTENT_TYPE = "manual"
DEFAULT_TEMPLATE_PROFILE = "source-structure-v1"
DEFAULT_CONFIRMED_BY = "user-or-supervising-agent"



def build_draft_plan(
    source_fingerprint: "contracts.SourceFingerprint",
    strategy: str,
    chunk_level: int,
    chunk_anchors: list,
    content_type: str = DEFAULT_CONTENT_TYPE,
    template_profile: str = DEFAULT_TEMPLATE_PROFILE,
    analysis_warnings: "list | None" = None,
    confirmed_topic_roots: "list | None" = None,
    media_decisions: "list | None" = None,
) -> "contracts.ConversionPlan":
    """Build a draft ConversionPlan (confirmation.status == "draft").

    `plan_id` is computed from normalized plan content (excluding the
    `plan_id` field itself and the `confirmed_at` timestamp), via
    `hashing.compute_plan_id`, matching the spec's "plan_id is calculated
    from normalized plan content excluding the plan_id field itself" rule.
    """
    plan = contracts.ConversionPlan(
        schema_version=contracts.CONVERSION_PLAN_SCHEMA_VERSION,
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
        confirmed_topic_roots=(
            list(confirmed_topic_roots) if confirmed_topic_roots is not None else None
        ),
        media_decisions=list(media_decisions) if media_decisions is not None else None,
    )
    plan.plan_id = hashing.compute_plan_id(plan)
    return plan


# ---------------------------------------------------------------------------
# Confirmation (Task 7)
# ---------------------------------------------------------------------------

def confirm_plan(
    draft_plan: "contracts.ConversionPlan",
    confirmed_by: str = DEFAULT_CONFIRMED_BY,
) -> "contracts.ConversionPlan":
    """Build a NEW confirmed ConversionPlan from `draft_plan`.

    Never mutates `draft_plan` in place: a fresh `contracts.ConversionPlan`
    is constructed with `confirmation.status` set to "confirmed",
    `confirmation.confirmed_by` set to `confirmed_by`, and
    `confirmation.confirmed_at` set to the current UTC time in ISO-8601.
    `plan_id` is then recomputed over this finalized content via
    `hashing.compute_plan_id` (which itself excludes `plan_id` and
    `confirmation.confirmed_at` from the hash input).
    """
    confirmed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    confirmed = contracts.ConversionPlan(
        schema_version=draft_plan.schema_version,
        plan_id="",
        source=draft_plan.source,
        strategy=draft_plan.strategy,
        chunk_level=draft_plan.chunk_level,
        chunk_anchors=list(draft_plan.chunk_anchors),
        content_type=draft_plan.content_type,
        template_profile=draft_plan.template_profile,
        confirmation=contracts.Confirmation(
            status="confirmed",
            confirmed_by=confirmed_by,
            confirmed_at=confirmed_at,
        ),
        analysis_warnings=list(draft_plan.analysis_warnings),
        confirmed_topic_roots=(
            list(draft_plan.confirmed_topic_roots)
            if draft_plan.confirmed_topic_roots is not None
            else None
        ),
        media_decisions=(
            list(draft_plan.media_decisions) if draft_plan.media_decisions is not None else None
        ),
    )
    confirmed.plan_id = hashing.compute_plan_id(confirmed)
    return confirmed


# ---------------------------------------------------------------------------
# Media-decision override (Task 18 general media-disposition mechanism)
# ---------------------------------------------------------------------------

def apply_media_decision(
    draft_plan: "contracts.ConversionPlan",
    source_media_id: str,
    classification: str,
    disposition: str,
    reason: str,
    decision_authority: str = "human-confirmed",
    canonical_inclusion: bool = False,
    publication_inclusion: bool = False,
    derived_asset_allowed: bool = False,
    requires_alt_text: "bool | None" = False,
) -> "contracts.ConversionPlan":
    """Return a NEW draft plan with the proposed media-decision record for
    `source_media_id` replaced by a human-confirmed one (classification/
    disposition/reason/decision_authority and the inclusion/derived-asset
    flags). Never mutates `draft_plan`. Raises `ValueError` if
    `source_media_id` isn't among `draft_plan.media_decisions` (nothing to
    override) or if the plan is already confirmed (overrides belong on the
    draft, before `confirm_plan`).
    """
    if draft_plan.confirmation.status != "draft":
        raise ValueError(
            "apply_media_decision requires a draft plan; the media decision "
            "must be recorded before confirm_plan, not after"
        )
    existing = list(draft_plan.media_decisions or [])
    matched = False
    updated = []
    for record in existing:
        if record["source_media_id"] == source_media_id:
            matched = True
            updated.append(
                {
                    **record,
                    "classification": classification,
                    "disposition": disposition,
                    "reason": reason,
                    "decision_authority": decision_authority,
                    "canonical_inclusion": canonical_inclusion,
                    "publication_inclusion": publication_inclusion,
                    "derived_asset_allowed": derived_asset_allowed,
                    "requires_alt_text": requires_alt_text,
                }
            )
        else:
            updated.append(record)
    if not matched:
        raise ValueError(
            f"no proposed media decision found for {source_media_id!r} on this "
            "draft plan"
        )

    new_draft = contracts.ConversionPlan(
        schema_version=draft_plan.schema_version,
        plan_id="",
        source=draft_plan.source,
        strategy=draft_plan.strategy,
        chunk_level=draft_plan.chunk_level,
        chunk_anchors=list(draft_plan.chunk_anchors),
        content_type=draft_plan.content_type,
        template_profile=draft_plan.template_profile,
        confirmation=contracts.Confirmation(status="draft", confirmed_by="", confirmed_at=""),
        analysis_warnings=list(draft_plan.analysis_warnings),
        confirmed_topic_roots=(
            list(draft_plan.confirmed_topic_roots)
            if draft_plan.confirmed_topic_roots is not None
            else None
        ),
        media_decisions=updated,
    )
    new_draft.plan_id = hashing.compute_plan_id(new_draft)
    return new_draft


# ---------------------------------------------------------------------------
# Verification (Task 7): used by later convert/run preconditions.
# PlanVerificationError/verify_plan_against_source/verify_plan_integrity/
# require_confirmed now live in plan_verification_core.py (the single
# canonical implementation, imported above) -- this used to be their home
# directly; see the module docstring and
# docs/superpowers/plans/phase-4-5-evidence/wave-9-duplication-remediation-report.md.
# ---------------------------------------------------------------------------
