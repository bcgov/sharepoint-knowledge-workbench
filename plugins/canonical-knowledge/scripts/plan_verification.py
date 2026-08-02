"""
plan_verification.py
=====================

Plan/source verification checks that `convert.py` uses as a precondition
before building a canonical package. Duplicated from knowledge-analysis's
`plans.py` (Phase 4.5 Wave 4) rather than imported cross-plugin: per the
dependency-boundary rule (spec Section 11), a real domain plugin never
imports another domain plugin's implementation package. See
docs/superpowers/plans/phase-4-5-evidence/wave-4-canonical-knowledge-split-decision.md.

Only the three verification functions convert.py actually calls are
duplicated here (plus their shared error type and a local compute_plan_id,
since this plugin does not need draft/confirm plan construction).
"""

from pathlib import Path

from canonical_schema import analysis_plan as contracts
import hashing


class PlanVerificationError(Exception):
    """Raised by verify checks: a source file that no longer matches its
    recorded fingerprint, or a confirmed plan whose content was
    hand-tampered after it was written."""


def _compute_plan_id(plan: "contracts.ConversionPlan") -> str:
    data = plan.to_dict()
    data.pop("plan_id", None)
    confirmation = data.get("confirmation")
    if isinstance(confirmation, dict):
        confirmation = dict(confirmation)
        confirmation.pop("confirmed_at", None)
        data["confirmation"] = confirmation
    digest = hashing.content_hash(hashing.canonical_json_bytes(data))
    return f"sha256:{digest}"


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
    rules as knowledge-analysis's plan_hashing.compute_plan_id) and compare
    against the plan_id field stored on the plan. Raises
    PlanVerificationError if they don't match -- this detects hand-editing
    of a confirmed plan JSON file after it was written (e.g. a tampered
    chunk_anchors entry) while the stored plan_id was left untouched."""
    recomputed = _compute_plan_id(plan)
    if recomputed != plan.plan_id:
        raise PlanVerificationError(
            f"plan_id mismatch: stored plan_id={plan.plan_id!r} does not "
            f"match recomputed plan_id={recomputed!r}; the plan content was "
            "modified after confirmation without regenerating plan_id "
            "(tampering or manual edit)"
        )


def require_confirmed(plan: "contracts.ConversionPlan") -> None:
    """Raise PlanVerificationError unless `plan.confirmation.status ==
    "confirmed"`."""
    if plan.confirmation.status != "confirmed":
        raise PlanVerificationError(
            f"plan is not confirmed (confirmation.status="
            f"{plan.confirmation.status!r}); run the `confirm` command "
            "first"
        )
