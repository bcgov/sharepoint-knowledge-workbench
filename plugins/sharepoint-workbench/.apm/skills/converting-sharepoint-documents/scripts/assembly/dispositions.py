"""dispositions.py
================

Purpose:
    Warning-disposition mechanism for a `contracts.ValidationReport` produced by `validate_canonical.py` (spec Section 9): "WARN cannot be promoted to accepted output until `warning-disposition.json` records each warning as accepted or resolved."

Key Input Dependencies:
    - json
    - sys
    - dataclasses
    - pathlib
    - canonical_schema

Warning-disposition mechanism for a `contracts.ValidationReport` produced by
`validate_canonical.py` (spec Section 9): "WARN cannot be promoted to
accepted output until `warning-disposition.json` records each warning as
accepted or resolved."

This module does NOT do promotion itself (Task 11's job) -- it only answers
"is every warning in this report accounted for by a disposition record?"
and returns enough information for a promotion step to make that decision.

Disposition file format (`warning-disposition.json`), this module's own
design decision (not spec-mandated verbatim):

    {
      "dispositions": {
        "<code>|<path>": {
          "status": "accepted" | "resolved",
          "note": "free-text explanation",
          "by": "who decided this",
          "at": "ISO-8601 timestamp"
        },
        ...
      }
    }

Key shape decision: `disposition_key(issue) = f"{issue.code}|{issue.path or ''}"`.
A warning is identified by its (code, path) pair rather than a bare index,
because:
    - it survives issue-list reordering across validator runs (an index
      would silently point at the wrong warning if new issues were
      inserted/removed upstream), and
    - (code, path) is exactly the granularity a human reviewer disposes at
      ("I've reviewed the heading-drift warning on chunk X's content
      file"), whereas a single global index carries no meaning on its own.
If two warnings share the same (code, path) (e.g. a future check that can
emit more than one distinct warning against the same file/code), a single
disposition entry covers all of them -- this module does not currently
need finer-grained identity than that, and callers needing to distinguish
same-code/same-path warnings can extend the key later.

Function Index:
    - disposition_key(issue: contracts.ValidationIssue) -> str
    - load_dispositions(path: Path) -> dict[str, dict]
        Reads and parses `warning-disposition.json`. Returns {} if the file
        does not exist (an absent file is "no dispositions recorded", not
        an error). Raises DispositionError on malformed JSON, a missing
        top-level "dispositions" key, or an entry whose "status" is not
        "accepted"/"resolved".
    - apply_disposition(validation_report, disposition_path) -> PromotionCheck
        The brief's required function: checks EVERY warning in
        `validation_report` has a matching disposition entry. Returns a
        `PromotionCheck` (promotable: bool, undispositioned: list[
        contracts.ValidationIssue]). A report with status "FAIL" is never
        promotable regardless of dispositions (dispositions only ever
        cover WARN-level reviewable discrepancies, never errors).

Key Functions Index:
    - disposition_key()
    - load_dispositions()
    - apply_disposition()"""

import json
import sys
from dataclasses import dataclass
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from canonical_schema import canonical_package as contracts  # noqa: E402

_VALID_STATUSES = {"accepted", "resolved"}


class DispositionError(Exception):
    """A warning-disposition.json file exists but is malformed: invalid
    JSON, missing the top-level "dispositions" key, or an entry with a
    "status" other than "accepted"/"resolved"."""


@dataclass
class PromotionCheck:
    promotable: bool
    undispositioned: list  # list[contracts.ValidationIssue]


def disposition_key(issue: "contracts.ValidationIssue") -> str:
    """Stable identity for a warning: its code plus the path it points at
    (empty string if the issue carries no path). See module docstring for
    why (code, path) was chosen over a bare list index."""
    return f"{issue.code}|{issue.path or ''}"


def load_dispositions(path: "Path") -> dict:
    """Load `warning-disposition.json` from `path`. Returns {} (no
    dispositions recorded) if the file does not exist -- a missing file is
    a legitimate, common state (no warnings have been reviewed yet), not a
    malformed one. Raises DispositionError for a file that exists but is
    unreadable as valid disposition data."""
    path = Path(path)
    if not path.exists():
        return {}

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DispositionError(f"{path} is not valid JSON: {exc}") from exc

    if not isinstance(raw, dict) or "dispositions" not in raw:
        raise DispositionError(
            f"{path} is missing the top-level 'dispositions' object"
        )

    entries = raw["dispositions"]
    if not isinstance(entries, dict):
        raise DispositionError(f"{path}: 'dispositions' must be an object")

    for key, entry in entries.items():
        if not isinstance(entry, dict) or entry.get("status") not in _VALID_STATUSES:
            raise DispositionError(
                f"{path}: disposition entry {key!r} must have a 'status' "
                f"of 'accepted' or 'resolved' (got {entry!r})"
            )

    return entries


def apply_disposition(
    validation_report: "contracts.ValidationReport", disposition_path: "Path"
) -> "PromotionCheck":
    """Check every WARN-level issue in `validation_report` against the
    disposition file at `disposition_path`. A report is `promotable` only
    if:
        - it has no "error"-severity issues (FAIL always blocks, no
          disposition can override an error), AND
        - every "warning"-severity issue has a matching entry in the
          disposition file (status "accepted" or "resolved").

    Missing/incomplete dispositions do not raise -- they are reported via
    `PromotionCheck.undispositioned` so a caller (e.g. Task 11's promotion
    step, or a test) can present exactly which warnings still need review,
    rather than getting an opaque exception. `DispositionError` from a
    malformed disposition FILE (as opposed to an incomplete one) still
    propagates -- that is a data-integrity problem the caller must fix,
    not a "some warnings are unreviewed" state.
    """
    has_error = any(i.severity == "error" for i in validation_report.issues)
    dispositions = load_dispositions(disposition_path)

    warnings = [i for i in validation_report.issues if i.severity == "warning"]
    undispositioned = [
        w for w in warnings if disposition_key(w) not in dispositions
    ]

    promotable = (not has_error) and (not undispositioned)
    return PromotionCheck(promotable=promotable, undispositioned=undispositioned)

