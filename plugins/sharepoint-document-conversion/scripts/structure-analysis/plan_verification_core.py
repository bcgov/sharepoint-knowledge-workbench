"""plan_verification_core.py
============================

Purpose:
    Confirmed-plan verification and plan-ID computation -- the single canonical implementation, shared by `document-structure-analysis` (via `plans.py`, which handles draft/confirm/media-decision workflows and delegates verification here) and `structured-content-assembly` (via a managed cross-plugin symlink at this exact module name -- `structured-content-assembly` consumes a *confirmed* plan dict and must verify it without depending on `document-structure-analysis`'s implementation package).

Key Input Dependencies:
    - hashlib
    - json
    - pathlib
    - typing

Confirmed-plan verification and plan-ID computation -- the single
canonical implementation, shared by `document-structure-analysis` (via `plans.py`,
which handles draft/confirm/media-decision workflows and delegates
verification here) and `structured-content-assembly` (via a managed cross-plugin
symlink at this exact module name -- `structured-content-assembly` consumes a
*confirmed* plan dict and must verify it without depending on
`document-structure-analysis`'s implementation package). See
docs/superpowers/plans/phase-4-5-evidence/wave-9-duplication-remediation-report.md.

Deliberately untyped (duck-typed) rather than importing either plugin's
own `ConversionPlan` schema class: every function here only reads
`.source.sha256`, `.confirmation.status`, `.plan_id`, and calls
`.to_dict()` -- it never constructs or validates a plan, so it does not
need either plugin's schema module as a runtime or even type-hint-only
dependency. This keeps this module genuinely self-contained (stdlib-only)
so it can be symlinked into another plugin without pulling in a second
cross-plugin dependency.

Function Index:
    - compute_plan_id(plan) -> str
        The single canonical implementation of plan-ID computation
        (`sha256:`-prefixed content hash over normalized plan content,
        excluding `plan_id` itself and `confirmation.confirmed_at`).
        `document-structure-analysis`'s own `plan_hashing.compute_plan_id` is a
        thin re-export of this function, used by `plans.py`'s
        `build_draft_plan`/`confirm_plan`/`apply_media_decision`.
    - verify_plan_against_source(plan, source_path) -> None
        Raises PlanVerificationError if the source file on disk right now
        doesn't match the sha256 recorded in `plan.source` at confirm time.
    - verify_plan_integrity(plan) -> None
        Raises PlanVerificationError if recomputing plan_id over the
        plan's current content doesn't match the stored plan_id (detects
        hand-tampering of a confirmed plan JSON file after it was written).
    - require_confirmed(plan) -> None
        Raises PlanVerificationError unless confirmation.status ==
        "confirmed".

Key Functions Index:
    - _canonical_json_bytes()
    - _content_hash()
    - compute_plan_id()
    - verify_plan_against_source()
    - verify_plan_integrity()
    - require_confirmed()"""

import hashlib
import json
from pathlib import Path
from typing import Any


class PlanVerificationError(Exception):
    """Raised by confirm/verify checks: an unconfirmed plan, a source file
    that no longer matches its recorded fingerprint, or a confirmed plan
    whose content was hand-tampered after it was written."""


# Encode a plan mapping as deterministic UTF-8 JSON bytes for fingerprint calculation.
def _canonical_json_bytes(payload: Any) -> bytes:
    """Encode a plan mapping as deterministic UTF-8 JSON bytes for fingerprint calculation."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


# Compute the SHA-256 digest of the supplied source content.
def _content_hash(data: bytes) -> str:
    """Compute the SHA-256 digest of the supplied source content."""
    return hashlib.sha256(data).hexdigest()


def compute_plan_id(plan) -> str:
    """Compute a `sha256:`-prefixed content hash for a confirmed-plan-like
    object (anything with a `.to_dict()` matching the `ConversionPlan`
    wire shape).

    Excludes:
    - the `plan_id` field itself (it cannot depend on its own value), and
    - `confirmation.confirmed_at` (a timestamp; per spec, timestamps must
      not alter content hashes).

    All other fields, including `confirmation.status` and
    `confirmation.confirmed_by`, participate in the hash.
    """
    data = plan.to_dict()
    data.pop("plan_id", None)
    confirmation = data.get("confirmation")
    if isinstance(confirmation, dict):
        confirmation = dict(confirmation)
        confirmation.pop("confirmed_at", None)
        data["confirmation"] = confirmation
    digest = _content_hash(_canonical_json_bytes(data))
    return f"sha256:{digest}"


def verify_plan_against_source(plan, source_path: Path) -> None:
    """Re-fingerprint the source file as it exists on disk right now and
    compare its sha256 against `plan.source.sha256` (the fingerprint
    recorded at confirmation time). Raises PlanVerificationError on any
    mismatch -- this is how a modified/swapped source file after
    confirmation gets rejected before a stale plan is used to convert it."""
    current_sha256 = _content_hash(Path(source_path).read_bytes())
    if current_sha256 != plan.source.sha256:
        raise PlanVerificationError(
            f"source file {source_path} does not match the fingerprint "
            f"recorded in the plan (expected sha256={plan.source.sha256}, "
            f"got sha256={current_sha256}); the source was modified after "
            "confirmation -- re-run analyze/confirm against the current file"
        )


def verify_plan_integrity(plan) -> None:
    """Recompute plan_id over the plan's current content and compare
    against the plan_id field stored on the plan. Raises
    PlanVerificationError if they don't match -- this detects hand-editing
    of a confirmed plan JSON file after it was written (e.g. a tampered
    chunk_anchors entry) while the stored plan_id was left untouched."""
    recomputed = compute_plan_id(plan)
    if recomputed != plan.plan_id:
        raise PlanVerificationError(
            f"plan_id mismatch: stored plan_id={plan.plan_id!r} does not "
            f"match recomputed plan_id={recomputed!r}; the plan content was "
            "modified after confirmation without regenerating plan_id "
            "(tampering or manual edit)"
        )


def require_confirmed(plan) -> None:
    """Raise PlanVerificationError unless `plan.confirmation.status ==
    "confirmed"`."""
    if plan.confirmation.status != "confirmed":
        raise PlanVerificationError(
            f"plan is not confirmed (confirmation.status="
            f"{plan.confirmation.status!r}); run the `confirm` command "
            "first"
        )
