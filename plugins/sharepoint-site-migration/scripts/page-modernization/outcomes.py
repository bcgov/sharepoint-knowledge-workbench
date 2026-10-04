"""
outcomes.py
===========

Purpose: shared honest partial-failure reporting vocabulary for every stage
of the page-modernization pipeline. A stage must report one of the seven
statuses below rather than collapsing a failure into an empty success.

Layer: shared utility module, imported by every other stage script in this
plugin's flat `scripts/page-modernization/` directory.
"""

from __future__ import annotations

from typing import Any

OUTCOME_STATUSES = (
    "Observed",
    "Empty",
    "Forbidden",
    "Unavailable",
    "NotSupported",
    "Partial",
    "Failed",
)

_FAILURE_STATUSES = frozenset({"Failed", "Unavailable", "Forbidden"})


class OutcomeError(ValueError):
    """Raised when an outcome dict does not conform to the shared vocabulary."""


def make_outcome(status: str, detail: str, counts: "dict[str, Any] | None" = None) -> dict:
    """Build a well-formed outcome dict. Every status other than "Observed"
    requires a non-empty `detail` -- a bare status with no explanation is
    exactly the silent-failure shape this vocabulary forbids."""
    if status not in OUTCOME_STATUSES:
        raise OutcomeError(f"status {status!r} is not part of the outcome vocabulary")
    if status != "Observed" and not detail:
        raise OutcomeError(f"status {status!r} requires a non-empty detail")
    return {"status": status, "detail": detail, "counts": counts}


def validate_outcome(outcome: dict) -> None:
    """Raise OutcomeError if `outcome` is not a well-formed outcome dict."""
    if not isinstance(outcome, dict) or "status" not in outcome:
        raise OutcomeError("outcome is missing a 'status' key")
    if outcome["status"] not in OUTCOME_STATUSES:
        raise OutcomeError(f"status {outcome['status']!r} is not part of the outcome vocabulary")


def is_failure(outcome: dict) -> bool:
    """True for Failed/Unavailable/Forbidden; False for Empty/Observed/Partial."""
    return outcome.get("status") in _FAILURE_STATUSES
