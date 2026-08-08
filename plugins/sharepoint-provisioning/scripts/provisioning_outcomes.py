"""
provisioning_outcomes.py
=========================

Purpose:
    The single honest-reporting vocabulary shared by every module in this
    plugin. Every planning/apply operation reports exactly one of these
    outcomes; an operation that could not do its job never reports success
    with empty results.

Layer: sharepoint-provisioning / shared vocabulary

Key Input Dependencies:
    - none (standard library only)
"""

from __future__ import annotations


class Outcome:
    """Reporting vocabulary. String values are the serialised evidence form."""

    OBSERVED = "Observed"
    """The operation ran fully and its results are complete."""

    EMPTY = "Empty"
    """The operation ran fully and there was legitimately nothing to report."""

    FORBIDDEN = "Forbidden"
    """The caller's identity/action was refused. Not a pass, not an empty result."""

    UNAVAILABLE = "Unavailable"
    """A required input schema or dependency could not be found/read."""

    NOT_SUPPORTED = "NotSupported"
    """The requested check/operation is outside this capability's contract."""

    PARTIAL = "Partial"
    """Some units succeeded/resolved and some did not. Both sets are reported."""

    FAILED = "Failed"
    """No unit succeeded, or a blocking finding prevents proceeding."""

    ALL = (OBSERVED, EMPTY, FORBIDDEN, UNAVAILABLE, NOT_SUPPORTED, PARTIAL, FAILED)


def summarise(succeeded: int, failed: int, *, empty_is_empty: bool = True) -> str:
    """Reduce a succeeded/failed tally to a single outcome."""
    if succeeded == 0 and failed == 0:
        return Outcome.EMPTY if empty_is_empty else Outcome.OBSERVED
    if failed == 0:
        return Outcome.OBSERVED
    if succeeded == 0:
        return Outcome.FAILED
    return Outcome.PARTIAL
