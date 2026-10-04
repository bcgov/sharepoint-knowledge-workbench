"""
test_outcomes.py
================

Contract tests for the honest partial-failure reporting vocabulary
(Phase 9 plan Task 13): every stage must report one of
Observed / Empty / Forbidden / Unavailable / NotSupported / Partial / Failed
rather than collapsing a failure into an empty success.
"""

import pytest

import outcomes


def test_vocabulary_is_exactly_the_seven_required_statuses():
    assert set(outcomes.OUTCOME_STATUSES) == {
        "Observed",
        "Empty",
        "Forbidden",
        "Unavailable",
        "NotSupported",
        "Partial",
        "Failed",
    }


def test_make_outcome_returns_status_detail_and_counts():
    out = outcomes.make_outcome("Observed", "3 zones detected", counts={"zones": 3})
    assert out["status"] == "Observed"
    assert out["detail"] == "3 zones detected"
    assert out["counts"] == {"zones": 3}


def test_make_outcome_rejects_a_status_outside_the_vocabulary():
    with pytest.raises(outcomes.OutcomeError):
        outcomes.make_outcome("Success", "not part of the vocabulary")


def test_make_outcome_requires_a_detail_for_every_non_observed_status():
    """A bare 'Empty' with no explanation is exactly the silent-failure shape this forbids."""
    for status in ("Empty", "Forbidden", "Unavailable", "NotSupported", "Partial", "Failed"):
        with pytest.raises(outcomes.OutcomeError):
            outcomes.make_outcome(status, "")


def test_validate_outcome_rejects_a_missing_status():
    with pytest.raises(outcomes.OutcomeError):
        outcomes.validate_outcome({"detail": "no status key"})


def test_validate_outcome_accepts_a_well_formed_outcome():
    outcomes.validate_outcome(outcomes.make_outcome("Empty", "no zones detected"))


def test_is_failure_distinguishes_real_failure_from_honest_emptiness():
    assert outcomes.is_failure(outcomes.make_outcome("Failed", "input unreadable")) is True
    assert outcomes.is_failure(outcomes.make_outcome("Unavailable", "source absent")) is True
    assert outcomes.is_failure(outcomes.make_outcome("Forbidden", "no permission")) is True
    assert outcomes.is_failure(outcomes.make_outcome("Empty", "nothing detected")) is False
    assert outcomes.is_failure(outcomes.make_outcome("Observed", "ok")) is False
    assert outcomes.is_failure(outcomes.make_outcome("Partial", "some zones skipped")) is False
