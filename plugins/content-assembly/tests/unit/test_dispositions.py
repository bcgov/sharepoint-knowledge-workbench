"""
test_dispositions.py
=====================

Tests for scripts/dispositions.py -- the warning-disposition completeness
mechanism (Task 10). Verifies the brief's required failing-test scenario:
"WARN blocks promotion without a complete disposition file", plus the
disposition file format, malformed-file handling, and FAIL-always-blocks
behavior.

Fixture data is synthetic (contracts.ValidationReport/ValidationIssue
constructed directly).
"""

import json

import pytest

from canonical_schema import canonical_package as contracts
import dispositions as disp


def _report(issues, status="WARN"):
    return contracts.ValidationReport(
        status=status, issues=issues, source_sha256="a" * 64, plan_id="sha256:" + "b" * 64
    )


def _warning(code="heading_missing_from_content", path="chunks/x.md"):
    return contracts.ValidationIssue(severity="warning", code=code, message="msg", path=path)


def _error(code="content_hash_mismatch", path="chunks/x.md"):
    return contracts.ValidationIssue(severity="error", code=code, message="msg", path=path)


# ---------------------------------------------------------------------------
# disposition_key
# ---------------------------------------------------------------------------

def test_disposition_key_combines_code_and_path():
    issue = _warning(code="heading_missing_from_content", path="chunks/abc.md")
    assert disp.disposition_key(issue) == "heading_missing_from_content|chunks/abc.md"


def test_disposition_key_handles_missing_path():
    issue = contracts.ValidationIssue(severity="warning", code="content_comparison_skipped", message="m", path=None)
    assert disp.disposition_key(issue) == "content_comparison_skipped|"


# ---------------------------------------------------------------------------
# WARN blocks promotion without a complete disposition file (brief's
# required failing test)
# ---------------------------------------------------------------------------

def test_warn_blocks_promotion_without_any_disposition_file(tmp_path):
    report = _report([_warning()])
    result = disp.apply_disposition(report, tmp_path / "warning-disposition.json")
    assert result.promotable is False
    assert len(result.undispositioned) == 1


def test_warn_blocks_promotion_with_incomplete_disposition_file(tmp_path):
    w1 = _warning(code="heading_missing_from_content", path="chunks/a.md")
    w2 = _warning(code="content_comparison_skipped", path=None)
    report = _report([w1, w2])

    disposition_path = tmp_path / "warning-disposition.json"
    disposition_path.write_text(json.dumps({
        "dispositions": {
            disp.disposition_key(w1): {
                "status": "accepted",
                "note": "reviewed, acceptable",
                "by": "tester",
                "at": "2026-07-26T00:00:00Z",
            }
        }
    }))

    result = disp.apply_disposition(report, disposition_path)
    assert result.promotable is False
    assert [disp.disposition_key(w) for w in result.undispositioned] == [disp.disposition_key(w2)]


def test_warn_promotable_with_complete_disposition_file(tmp_path):
    w1 = _warning(code="heading_missing_from_content", path="chunks/a.md")
    w2 = _warning(code="content_comparison_skipped", path=None)
    report = _report([w1, w2])

    disposition_path = tmp_path / "warning-disposition.json"
    disposition_path.write_text(json.dumps({
        "dispositions": {
            disp.disposition_key(w1): {
                "status": "accepted", "note": "n", "by": "tester", "at": "2026-07-26T00:00:00Z",
            },
            disp.disposition_key(w2): {
                "status": "resolved", "note": "n2", "by": "tester", "at": "2026-07-26T00:00:00Z",
            },
        }
    }))

    result = disp.apply_disposition(report, disposition_path)
    assert result.promotable is True
    assert result.undispositioned == []


# ---------------------------------------------------------------------------
# FAIL always blocks, dispositions cannot override errors
# ---------------------------------------------------------------------------

def test_fail_never_promotable_even_with_dispositions_covering_warnings(tmp_path):
    w1 = _warning()
    e1 = _error()
    report = _report([w1, e1], status="FAIL")

    disposition_path = tmp_path / "warning-disposition.json"
    disposition_path.write_text(json.dumps({
        "dispositions": {
            disp.disposition_key(w1): {
                "status": "accepted", "note": "n", "by": "tester", "at": "2026-07-26T00:00:00Z",
            }
        }
    }))

    result = disp.apply_disposition(report, disposition_path)
    assert result.promotable is False


def test_pass_with_no_warnings_is_promotable_without_any_disposition_file(tmp_path):
    report = _report([], status="PASS")
    result = disp.apply_disposition(report, tmp_path / "warning-disposition.json")
    assert result.promotable is True
    assert result.undispositioned == []


# ---------------------------------------------------------------------------
# load_dispositions: malformed file handling
# ---------------------------------------------------------------------------

def test_load_dispositions_missing_file_returns_empty_dict(tmp_path):
    assert disp.load_dispositions(tmp_path / "nope.json") == {}


def test_load_dispositions_raises_on_malformed_json(tmp_path):
    path = tmp_path / "warning-disposition.json"
    path.write_text("{not valid json")
    with pytest.raises(disp.DispositionError):
        disp.load_dispositions(path)


def test_load_dispositions_raises_on_missing_top_level_key(tmp_path):
    path = tmp_path / "warning-disposition.json"
    path.write_text(json.dumps({"not_dispositions": {}}))
    with pytest.raises(disp.DispositionError):
        disp.load_dispositions(path)


def test_load_dispositions_raises_on_invalid_status_value(tmp_path):
    path = tmp_path / "warning-disposition.json"
    path.write_text(json.dumps({
        "dispositions": {
            "some_code|some_path": {"status": "ignored_forever", "note": "n", "by": "x", "at": "t"}
        }
    }))
    with pytest.raises(disp.DispositionError):
        disp.load_dispositions(path)
