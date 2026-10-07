"""
test_discovery_inputs.py

Purpose:
    Contract and safety tests for the shared discovery input loader. Exercises the
    honest-status vocabulary required by the Phase 9 spec (§13): a discovery step must
    report Observed / Empty / Forbidden / Unavailable / NotSupported / Partial / Failed
    and must never collapse a failure into an empty success.

Layer: plugins/sharepoint-site-assessment -- tests

Notes:
    Per `.agent/rules/test-driven-development.md` ("Critical Runtime Paths -- No Mocking
    Allowed"), path resolution and file parsing are exercised against a real filesystem
    (tmp_path), not mocked.

Key Input Dependencies:
    - pytest, the plugin module under test, and temporary JSON fixtures created by the test cases.

Function index:
    - test_status_vocabulary_is_exactly_the_specified_seven
    - test_missing_file_is_unavailable_not_empty_success
    - test_malformed_json_is_failed_not_empty_success
    - test_empty_collection_is_empty_and_distinguishable_from_observed
    - test_populated_collection_is_observed
    - test_unreadable_file_is_forbidden_not_failed
    - test_partial_outcome_records_what_was_missing
    - test_outcome_to_dict_is_json_serializable
    - test_require_output_dir_creates_real_directory
    - test_require_output_dir_rejects_empty_path
"""

import json
import os
import stat

import pytest

from discovery_inputs import (
    DiscoveryOutcome,
    DiscoveryStatus,
    load_json_input,
    require_output_dir,
)


# Status vocabulary is exactly the specified seven.
def test_status_vocabulary_is_exactly_the_specified_seven():
    """Status vocabulary is exactly the specified seven."""
    assert {s.value for s in DiscoveryStatus} == {
        "Observed",
        "Empty",
        "Forbidden",
        "Unavailable",
        "NotSupported",
        "Partial",
        "Failed",
    }


# Missing file is unavailable not empty success.
def test_missing_file_is_unavailable_not_empty_success(tmp_path):
    """Missing file is unavailable not empty success."""
    outcome = load_json_input(tmp_path / "absent.json", domain="pages")
    assert outcome.status is DiscoveryStatus.UNAVAILABLE
    assert outcome.data is None
    assert "absent.json" in outcome.detail
    assert not outcome.ok


# Malformed json is failed not empty success.
def test_malformed_json_is_failed_not_empty_success(tmp_path):
    """Malformed json is failed not empty success."""
    p = tmp_path / "bad.json"
    p.write_text("{ not json", encoding="utf-8")
    outcome = load_json_input(p, domain="pages")
    assert outcome.status is DiscoveryStatus.FAILED
    assert outcome.data is None
    assert not outcome.ok


# Empty collection is empty and distinguishable from observed.
def test_empty_collection_is_empty_and_distinguishable_from_observed(tmp_path):
    """Empty collection is empty and distinguishable from observed."""
    p = tmp_path / "empty.json"
    p.write_text("[]", encoding="utf-8")
    outcome = load_json_input(p, domain="pages")
    assert outcome.status is DiscoveryStatus.EMPTY
    assert outcome.data == []
    # Empty is a legitimate observation, so it is ok -- but it is NOT "Observed".
    assert outcome.ok
    assert outcome.status is not DiscoveryStatus.OBSERVED


# Populated collection is observed.
def test_populated_collection_is_observed(tmp_path):
    """Populated collection is observed."""
    p = tmp_path / "ok.json"
    p.write_text(json.dumps([{"FileName": "default.aspx"}]), encoding="utf-8")
    outcome = load_json_input(p, domain="pages")
    assert outcome.status is DiscoveryStatus.OBSERVED
    assert outcome.data == [{"FileName": "default.aspx"}]


# Unreadable file is forbidden not failed.
@pytest.mark.skipif(
    not hasattr(os, "geteuid") or os.geteuid() == 0,
    reason="Windows or root bypasses POSIX file permissions",
)
def test_unreadable_file_is_forbidden_not_failed(tmp_path):
    """Unreadable file is forbidden not failed."""
    p = tmp_path / "locked.json"
    p.write_text("[]", encoding="utf-8")
    p.chmod(stat.S_IWUSR)  # write-only: no read permission
    try:
        outcome = load_json_input(p, domain="permissions")
        assert outcome.status is DiscoveryStatus.FORBIDDEN
        assert outcome.data is None
        assert not outcome.ok
    finally:
        p.chmod(stat.S_IRUSR | stat.S_IWUSR)


# Partial outcome records what was missing.
def test_partial_outcome_records_what_was_missing():
    """Partial outcome records what was missing."""
    outcome = DiscoveryOutcome.partial("navigation", "QuickLaunch unavailable", data={"TopNav": []})
    assert outcome.status is DiscoveryStatus.PARTIAL
    assert outcome.ok
    assert "QuickLaunch" in outcome.detail


# Outcome to dict is json serializable.
def test_outcome_to_dict_is_json_serializable():
    """Outcome to dict is json serializable."""
    outcome = DiscoveryOutcome.observed("forms", "3 forms", data=[1, 2, 3])
    json.dumps(outcome.to_dict())


# Require output dir creates real directory.
def test_require_output_dir_creates_real_directory(tmp_path):
    """Require output dir creates real directory."""
    target = tmp_path / "nested" / "out"
    resolved = require_output_dir(target)
    assert resolved.is_dir()
    assert resolved == target.resolve()


# Require output dir rejects empty path.
def test_require_output_dir_rejects_empty_path():
    """Require output dir rejects empty path."""
    with pytest.raises(ValueError):
        require_output_dir("")
