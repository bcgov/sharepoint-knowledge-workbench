"""test_drift_detection.py
=========================

Purpose:
    Tests for `drift_detection` (Phase 6 Task 8): compares the `repository-claude` runtime's actual structural behavior against a Task 5 common-evaluation-set case's structural expectations (resolution success/failure per category, related-topic-cap adherence), and flags drift.

Key Input Dependencies:
    - pytest and the plugin-local tests in this namespace
    - sys
    - pathlib
    - drift_detection

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

Key Functions Index:
    - _case()
    - _result()
    - test_normal_case_resolved_within_cap_no_drift()
    - test_negative_case_correctly_not_found_no_drift()
    - test_zero_related_topics_within_cap_no_drift()
    - test_negative_case_unexpectedly_resolved_is_drift()
    - test_normal_case_unexpectedly_not_found_is_drift()
    - test_related_topic_cap_exceeded_is_drift()
    - test_related_topic_cap_exceeded_by_one_still_detected()
    - test_run_case_against_real_fixture()
    - test_run_case_against_missing_fixture()"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts" / "editorial-review"))

import drift_detection as dd  # noqa: E402


# Build an editorial evaluation case with its supplied topic and expected content.
def _case(category, related_topic_allowance=2):
    """Build an editorial evaluation case with its supplied topic and expected content."""
    return {
        "case_id": "TEST-01",
        "category": category,
        "related_topic_allowance": related_topic_allowance,
    }


# Build an editorial review result from the requested findings and status.
def _result(resolved, related_count=None, error=None):
    """Build an editorial review result from the requested findings and status."""
    return dd.CaseResult(resolved=resolved, related_count=related_count, error=error)


# ---------------------------------------------------------------------------
# No drift -- structural expectations met
# ---------------------------------------------------------------------------

def test_normal_case_resolved_within_cap_no_drift():
    """Verify normal case resolved within cap no drift."""
    issues = dd.detect_drift(_case("normal"), _result(resolved=True, related_count=1))
    assert issues == []


# Verify negative case correctly not found no drift.
def test_negative_case_correctly_not_found_no_drift():
    """Verify negative case correctly not found no drift."""
    issues = dd.detect_drift(_case("negative"), _result(resolved=False, error="not found"))
    assert issues == []


# Verify zero related topics within cap no drift.
def test_zero_related_topics_within_cap_no_drift():
    """Verify zero related topics within cap no drift."""
    issues = dd.detect_drift(_case("normal"), _result(resolved=True, related_count=0))
    assert issues == []


# ---------------------------------------------------------------------------
# Real drift -- structural expectations violated
# ---------------------------------------------------------------------------

def test_negative_case_unexpectedly_resolved_is_drift():
    """Verify negative case unexpectedly resolved is drift."""
    issues = dd.detect_drift(_case("negative"), _result(resolved=True, related_count=0))
    assert any(i.code == "expected_not_found_but_resolved" for i in issues)


# Verify normal case unexpectedly not found is drift.
def test_normal_case_unexpectedly_not_found_is_drift():
    """Verify normal case unexpectedly not found is drift."""
    issues = dd.detect_drift(_case("normal"), _result(resolved=False, error="not found"))
    assert any(i.code == "expected_resolved_but_not_found" for i in issues)


# Verify related topic cap exceeded is drift.
def test_related_topic_cap_exceeded_is_drift():
    # DELIBERATE DRIFT: related_count (3) exceeds related_topic_allowance (2) --
    # this is the exact safety property Task 4's adversarial review flagged as
    # under-tested. Proves the detector actually catches a cap violation rather
    # than just asserting the happy path.
    """Verify related topic cap exceeded is drift."""
    issues = dd.detect_drift(_case("normal", related_topic_allowance=2), _result(resolved=True, related_count=3))
    assert any(i.code == "related_topic_cap_exceeded" for i in issues)
    cap_issue = next(i for i in issues if i.code == "related_topic_cap_exceeded")
    assert cap_issue.severity == "error"


# Verify related topic cap exceeded by one still detected.
def test_related_topic_cap_exceeded_by_one_still_detected():
    """Verify related topic cap exceeded by one still detected."""
    issues = dd.detect_drift(_case("normal", related_topic_allowance=0), _result(resolved=True, related_count=1))
    assert any(i.code == "related_topic_cap_exceeded" for i in issues)


# ---------------------------------------------------------------------------
# run_case_against_repository_claude -- real execution against real fixtures
# ---------------------------------------------------------------------------

def test_run_case_against_real_fixture(tmp_path):
    """Verify run case against real fixture."""
    pages_dir = tmp_path / "pages"
    pages_dir.mkdir()
    (pages_dir / "topic-a--11111111.md").write_text("# Topic A\n\nBody.\n")

    case = {"primary_topic_slug": "topic-a--11111111", "category": "normal", "related_topic_allowance": 2}
    result = dd.run_case_against_repository_claude(case, pages_dir)

    assert result.resolved is True
    assert result.related_count == 0
    assert result.error is None


# Verify run case against missing fixture.
def test_run_case_against_missing_fixture(tmp_path):
    """Verify run case against missing fixture."""
    pages_dir = tmp_path / "pages"
    pages_dir.mkdir()

    case = {"primary_topic_slug": "does-not-exist--99999999", "category": "negative", "related_topic_allowance": 0}
    result = dd.run_case_against_repository_claude(case, pages_dir)

    assert result.resolved is False
    assert result.error is not None
