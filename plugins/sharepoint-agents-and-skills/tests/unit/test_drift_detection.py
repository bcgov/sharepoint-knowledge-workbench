"""
test_drift_detection.py
=========================

Tests for `drift_detection` (Phase 6 Task 8): compares the
`repository-claude` runtime's actual structural behavior against a
Task 5 common-evaluation-set case's structural expectations
(resolution success/failure per category, related-topic-cap
adherence), and flags drift. Deliberately scoped to the structural/
deterministic properties a resolver can prove -- full semantic-output
grading is a separate, larger undertaking (see Task 6's findings doc).

Includes a deliberately-introduced-drift test per the task's own
requirement ("add deliberate drift and prove detection") -- not just
happy-path coverage.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import drift_detection as dd  # noqa: E402


def _case(category, related_topic_allowance=2):
    return {
        "case_id": "TEST-01",
        "category": category,
        "related_topic_allowance": related_topic_allowance,
    }


def _result(resolved, related_count=None, error=None):
    return dd.CaseResult(resolved=resolved, related_count=related_count, error=error)


# ---------------------------------------------------------------------------
# No drift -- structural expectations met
# ---------------------------------------------------------------------------

def test_normal_case_resolved_within_cap_no_drift():
    issues = dd.detect_drift(_case("normal"), _result(resolved=True, related_count=1))
    assert issues == []


def test_negative_case_correctly_not_found_no_drift():
    issues = dd.detect_drift(_case("negative"), _result(resolved=False, error="not found"))
    assert issues == []


def test_zero_related_topics_within_cap_no_drift():
    issues = dd.detect_drift(_case("normal"), _result(resolved=True, related_count=0))
    assert issues == []


# ---------------------------------------------------------------------------
# Real drift -- structural expectations violated
# ---------------------------------------------------------------------------

def test_negative_case_unexpectedly_resolved_is_drift():
    issues = dd.detect_drift(_case("negative"), _result(resolved=True, related_count=0))
    assert any(i.code == "expected_not_found_but_resolved" for i in issues)


def test_normal_case_unexpectedly_not_found_is_drift():
    issues = dd.detect_drift(_case("normal"), _result(resolved=False, error="not found"))
    assert any(i.code == "expected_resolved_but_not_found" for i in issues)


def test_related_topic_cap_exceeded_is_drift():
    # DELIBERATE DRIFT: related_count (3) exceeds related_topic_allowance (2) --
    # this is the exact safety property Task 4's adversarial review flagged as
    # under-tested. Proves the detector actually catches a cap violation rather
    # than just asserting the happy path.
    issues = dd.detect_drift(_case("normal", related_topic_allowance=2), _result(resolved=True, related_count=3))
    assert any(i.code == "related_topic_cap_exceeded" for i in issues)
    cap_issue = next(i for i in issues if i.code == "related_topic_cap_exceeded")
    assert cap_issue.severity == "error"


def test_related_topic_cap_exceeded_by_one_still_detected():
    issues = dd.detect_drift(_case("normal", related_topic_allowance=0), _result(resolved=True, related_count=1))
    assert any(i.code == "related_topic_cap_exceeded" for i in issues)


# ---------------------------------------------------------------------------
# run_case_against_repository_claude -- real execution against real fixtures
# ---------------------------------------------------------------------------

def test_run_case_against_real_fixture(tmp_path):
    pages_dir = tmp_path / "pages"
    pages_dir.mkdir()
    (pages_dir / "topic-a--11111111.md").write_text("# Topic A\n\nBody.\n")

    case = {"primary_topic_slug": "topic-a--11111111", "category": "normal", "related_topic_allowance": 2}
    result = dd.run_case_against_repository_claude(case, pages_dir)

    assert result.resolved is True
    assert result.related_count == 0
    assert result.error is None


def test_run_case_against_missing_fixture(tmp_path):
    pages_dir = tmp_path / "pages"
    pages_dir.mkdir()

    case = {"primary_topic_slug": "does-not-exist--99999999", "category": "negative", "related_topic_allowance": 0}
    result = dd.run_case_against_repository_claude(case, pages_dir)

    assert result.resolved is False
    assert result.error is not None
