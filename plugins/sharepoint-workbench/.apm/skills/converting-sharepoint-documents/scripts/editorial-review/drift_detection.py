"""drift_detection.py
====================

Purpose:
    Phase 6 Task 8 -- compares the `repository-claude` runtime's actual structural behavior for a Task 5 common-evaluation-set case against that case's structural expectations, and flags drift.

Key Input Dependencies:
    - sys
    - dataclasses
    - pathlib
    - review_manual_topics

Phase 6 Task 8 -- compares the `repository-claude` runtime's actual
structural behavior for a Task 5 common-evaluation-set case against
that case's structural expectations, and flags drift.

Deliberately scoped to the structural/deterministic properties a
resolver can prove without a live model-graded run: whether primary-
topic resolution succeeded/failed as the case's `category` implies
(a `negative` case should fail to resolve; every other category
should resolve), and whether the related-topic cap
(`related_topic_allowance`) was respected. Full semantic-output
grading (does the review text actually satisfy
`expected_semantic_behaviours`) is a separate, larger undertaking --
see `docs/superpowers/plans/phase-6-tasks-1-12-evidence/
task-6-baseline-evaluation-findings.md`'s open items.

Key Functions Index:
    - run_case_against_repository_claude()
    - detect_drift()"""

import sys
from dataclasses import dataclass
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import review_manual_topics as rmt  # noqa: E402

# Categories whose primary topic is expected to fail resolution.
_EXPECTED_NOT_FOUND_CATEGORIES = frozenset({"negative"})


@dataclass
class CaseResult:
    resolved: bool
    related_count: "int | None" = None
    error: "str | None" = None


@dataclass
class DriftIssue:
    severity: str
    code: str
    message: str


def run_case_against_repository_claude(case: dict, pages_dir: "Path | str") -> "CaseResult":
    """Run `case` (a Task 5 common-evaluation-set case dict) against the
    real `repository-claude` deterministic resolver, over `pages_dir`
    (a directory of rendered `.md` topic pages). Returns a `CaseResult`
    -- never raises; resolution failures are captured in the result."""
    pages_dir = Path(pages_dir)
    slug = case.get("primary_topic_slug") or case["primary_topic"]
    try:
        resolved = rmt.resolve_topic(pages_dir, slug)
        return CaseResult(resolved=True, related_count=len(resolved.related))
    except rmt.TopicNotFoundError as exc:
        return CaseResult(resolved=False, error=str(exc))
    except rmt.TooManyRelatedTopicsError as exc:
        return CaseResult(resolved=True, error=str(exc))


def detect_drift(case: dict, result: "CaseResult") -> list:
    """Compare `result` (from `run_case_against_repository_claude`, or
    an equivalent structural summary of a native-runtime run) against
    `case`'s structural expectations. Returns a list of `DriftIssue`
    (empty means no structural drift detected)."""
    issues = []
    category = case.get("category")

    expected_not_found = category in _EXPECTED_NOT_FOUND_CATEGORIES
    if expected_not_found and result.resolved:
        issues.append(DriftIssue(
            severity="error",
            code="expected_not_found_but_resolved",
            message=f"case category {category!r} expects the primary topic to NOT resolve, "
                    "but it resolved",
        ))
    elif not expected_not_found and not result.resolved:
        issues.append(DriftIssue(
            severity="error",
            code="expected_resolved_but_not_found",
            message=f"case category {category!r} expects the primary topic to resolve, "
                    f"but it did not (error: {result.error!r})",
        ))

    allowance = case.get("related_topic_allowance")
    if result.related_count is not None and allowance is not None and result.related_count > allowance:
        issues.append(DriftIssue(
            severity="error",
            code="related_topic_cap_exceeded",
            message=f"related_count={result.related_count} exceeds "
                    f"related_topic_allowance={allowance}",
        ))

    return issues
