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
        Raises PlanVerificationError if the source file on disk right now
        doesn't match the sha256 recorded in `plan.source` at confirm time.
    - verify_plan_integrity(plan) -> None
        Raises PlanVerificationError if recomputing plan_id over the
        plan's current content doesn't match the stored plan_id (detects
        hand-tampering of a confirmed plan JSON file after it was written).
    - require_confirmed(plan) -> None
        Raises PlanVerificationError unless confirmation.status ==
        "confirmed". Lower-level counterpart to cli.py's
        `_require_confirmed_plan` (which loads from a file path and maps to
        an exit code); this one operates on an already-loaded
        ConversionPlan for non-CLI callers (e.g. Task 9's convert pipeline
        calling directly into plans.py).
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import contracts  # noqa: E402
import hashing  # noqa: E402

DEFAULT_CONTENT_TYPE = "manual"
DEFAULT_TEMPLATE_PROFILE = "source-structure-v1"
DEFAULT_CONFIRMED_BY = "user-or-supervising-agent"


class PlanVerificationError(Exception):
    """Raised by confirm/verify checks: an unconfirmed plan, a source file
    that no longer matches its recorded fingerprint, or a confirmed plan
    whose content was hand-tampered after it was written."""


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
    )
    confirmed.plan_id = hashing.compute_plan_id(confirmed)
    return confirmed


# ---------------------------------------------------------------------------
# Verification (Task 7): used by later convert/run preconditions
# ---------------------------------------------------------------------------

def verify_plan_against_source(plan: "contracts.ConversionPlan", source_path: Path) -> None:
    """Re-fingerprint the source file as it exists on disk right now and
    compare its sha256 against `plan.source.sha256` (the fingerprint
    recorded at confirmation time). Raises PlanVerificationError on any
    mismatch -- this is how a modified/swapped source file after
    confirmation gets rejected before a stale plan is used to convert it."""
    current_sha256 = hashing.content_hash(Path(source_path).read_bytes())
    if current_sha256 != plan.source.sha256:
        raise PlanVerificationError(
            f"source file {source_path} does not match the fingerprint "
            f"recorded in the plan (expected sha256={plan.source.sha256}, "
            f"got sha256={current_sha256}); the source was modified after "
            "confirmation -- re-run analyze/confirm against the current file"
        )


def verify_plan_integrity(plan: "contracts.ConversionPlan") -> None:
    """Recompute plan_id over the plan's current content (same exclusion
    rules as hashing.compute_plan_id) and compare against the plan_id
    field stored on the plan. Raises PlanVerificationError if they don't
    match -- this detects hand-editing of a confirmed plan JSON file after
    it was written (e.g. a tampered chunk_anchors entry) while the stored
    plan_id was left untouched."""
    recomputed = hashing.compute_plan_id(plan)
    if recomputed != plan.plan_id:
        raise PlanVerificationError(
            f"plan_id mismatch: stored plan_id={plan.plan_id!r} does not "
            f"match recomputed plan_id={recomputed!r}; the plan content was "
            "modified after confirmation without regenerating plan_id "
            "(tampering or manual edit)"
        )


def require_confirmed(plan: "contracts.ConversionPlan") -> None:
    """Raise PlanVerificationError unless `plan.confirmation.status ==
    "confirmed"`. Lower-level, file-independent counterpart to
    `cli.py`'s `_require_confirmed_plan` (which loads a plan from a file
    path and maps this same check to CLI exit code 4); this version is for
    callers that already hold a loaded ConversionPlan object directly
    (e.g. Task 9's convert pipeline) so the "is this plan confirmed" rule
    has exactly one implementation, not two independently-maintained ones.
    """
    if plan.confirmation.status != "confirmed":
        raise PlanVerificationError(
            f"plan is not confirmed (confirmation.status="
            f"{plan.confirmation.status!r}); run the `confirm` command "
            "first"
        )
