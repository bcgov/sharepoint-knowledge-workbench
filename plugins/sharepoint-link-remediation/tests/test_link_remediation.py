"""
test_link_remediation.py
========================

Purpose:
    Contract and *write-safety* tests for ``link_remediation``. Remediation
    rewrites content, so spec section 13 applies: dry-run by default, explicit
    confirmation, injected writer (no built-in transport), rollback,
    partial-failure reporting, and evidence. These tests are the enforcement
    mechanism for that boundary -- weakening them weakens the safety gate.

Layer: sharepoint-link-remediation / tests
"""

from pathlib import Path

import pytest

from link_outcomes import Outcome
from link_remediation import (
    ConfirmationRequired,
    RemediationPlan,
    WriterRequired,
    apply_remediation,
    plan_remediation,
    rollback_remediation,
)
from link_rules import load_ruleset

FIXTURES = Path(__file__).resolve().parent / "fixtures"

DOCUMENTS = {
    "page-a": '<a href="/Pages/team.aspx">team</a>',
    "page-b": '<a href="http://legacy.example.internal/Pages/overview.aspx">o</a>',
    "page-clean": '<a href="/SitePages/already-modern.aspx">m</a>',
}


@pytest.fixture()
def ruleset():
    return load_ruleset(FIXTURES / "rewrite-rules.json")


class RecordingWriter:
    """Test double for the *injected* write boundary -- not a mock of any
    internal code path, only of the caller-supplied tenant/storage sink."""

    def __init__(self, fail_for=()):
        self.writes = []
        self.fail_for = set(fail_for)

    def __call__(self, source, content):
        if source in self.fail_for:
            raise RuntimeError(f"write rejected for {source}")
        self.writes.append((source, content))


# --------------------------------------------------------------------------
# Planning -- pure, never writes
# --------------------------------------------------------------------------


def test_plan_remediation_reports_every_change_without_writing(ruleset):
    plan = plan_remediation(DOCUMENTS, ruleset)

    assert isinstance(plan, RemediationPlan)
    assert plan.outcome == Outcome.OBSERVED
    changed = {doc.source for doc in plan.documents if doc.changes}
    assert changed == {"page-a", "page-b"}
    assert plan.change_count == 2


def test_plan_remediation_preserves_original_content_for_rollback(ruleset):
    plan = plan_remediation(DOCUMENTS, ruleset)
    page_a = next(doc for doc in plan.documents if doc.source == "page-a")

    assert page_a.original_content == DOCUMENTS["page-a"]
    assert page_a.remediated_content == '<a href="/SitePages/team.aspx">team</a>'


def test_plan_remediation_on_clean_documents_is_empty(ruleset):
    plan = plan_remediation({"page-clean": DOCUMENTS["page-clean"]}, ruleset)

    assert plan.outcome == Outcome.EMPTY
    assert plan.change_count == 0


def test_plan_remediation_with_no_documents_is_empty(ruleset):
    assert plan_remediation({}, ruleset).outcome == Outcome.EMPTY


def test_plan_remediation_records_empty_document_bodies_as_problems(ruleset):
    plan = plan_remediation({"page-a": DOCUMENTS["page-a"], "page-null": ""}, ruleset)

    assert plan.outcome == Outcome.PARTIAL
    assert any("page-null" in problem for problem in plan.problems)


# --------------------------------------------------------------------------
# Write safety -- dry-run default, confirmation, injected writer
# --------------------------------------------------------------------------


def test_apply_is_dry_run_by_default_and_writes_nothing(ruleset):
    plan = plan_remediation(DOCUMENTS, ruleset)
    writer = RecordingWriter()

    result = apply_remediation(plan, writer=writer)

    assert result.dry_run is True
    assert result.outcome == Outcome.OBSERVED
    assert writer.writes == []
    assert result.applied == []
    assert sorted(result.would_change) == ["page-a", "page-b"]


def test_apply_without_a_writer_refuses_to_write(ruleset):
    plan = plan_remediation(DOCUMENTS, ruleset)

    with pytest.raises(WriterRequired):
        apply_remediation(plan, dry_run=False, confirm=plan.confirmation_token)


def test_apply_without_confirmation_refuses_to_write(ruleset):
    plan = plan_remediation(DOCUMENTS, ruleset)
    writer = RecordingWriter()

    with pytest.raises(ConfirmationRequired):
        apply_remediation(plan, writer=writer, dry_run=False)

    assert writer.writes == []


def test_apply_with_the_wrong_confirmation_token_refuses_to_write(ruleset):
    plan = plan_remediation(DOCUMENTS, ruleset)
    writer = RecordingWriter()

    with pytest.raises(ConfirmationRequired):
        apply_remediation(plan, writer=writer, dry_run=False, confirm="yes")

    assert writer.writes == []


def test_confirmation_token_is_bound_to_the_exact_plan_scope(ruleset):
    small = plan_remediation({"page-a": DOCUMENTS["page-a"]}, ruleset)
    large = plan_remediation(DOCUMENTS, ruleset)

    assert small.confirmation_token != large.confirmation_token

    with pytest.raises(ConfirmationRequired):
        apply_remediation(large, writer=RecordingWriter(), dry_run=False, confirm=small.confirmation_token)


def test_apply_with_confirmation_and_writer_writes_only_changed_documents(ruleset):
    plan = plan_remediation(DOCUMENTS, ruleset)
    writer = RecordingWriter()

    result = apply_remediation(plan, writer=writer, dry_run=False, confirm=plan.confirmation_token)

    assert result.dry_run is False
    assert result.outcome == Outcome.OBSERVED
    assert sorted(source for source, _ in writer.writes) == ["page-a", "page-b"]
    assert dict(writer.writes)["page-a"] == '<a href="/SitePages/team.aspx">team</a>'
    assert result.skipped == ["page-clean"]


def test_apply_on_an_empty_plan_never_calls_the_writer(ruleset):
    plan = plan_remediation({"page-clean": DOCUMENTS["page-clean"]}, ruleset)
    writer = RecordingWriter()

    result = apply_remediation(plan, writer=writer, dry_run=False, confirm=plan.confirmation_token)

    assert result.outcome == Outcome.EMPTY
    assert writer.writes == []


# --------------------------------------------------------------------------
# Honest partial-failure reporting
# --------------------------------------------------------------------------


def test_a_failing_write_is_reported_as_partial_not_success(ruleset):
    plan = plan_remediation(DOCUMENTS, ruleset)
    writer = RecordingWriter(fail_for={"page-b"})

    result = apply_remediation(plan, writer=writer, dry_run=False, confirm=plan.confirmation_token)

    assert result.outcome == Outcome.PARTIAL
    assert result.applied == ["page-a"]
    assert [source for source, _ in result.failed] == ["page-b"]


def test_all_writes_failing_is_reported_as_failed(ruleset):
    plan = plan_remediation(DOCUMENTS, ruleset)
    writer = RecordingWriter(fail_for={"page-a", "page-b"})

    result = apply_remediation(plan, writer=writer, dry_run=False, confirm=plan.confirmation_token)

    assert result.outcome == Outcome.FAILED
    assert result.applied == []


def test_a_permission_denial_is_reported_as_forbidden(ruleset):
    class ForbiddingWriter:
        def __call__(self, source, content):
            raise PermissionError("insufficient privileges")

    plan = plan_remediation(DOCUMENTS, ruleset)
    result = apply_remediation(plan, writer=ForbiddingWriter(), dry_run=False, confirm=plan.confirmation_token)

    assert result.outcome == Outcome.FORBIDDEN
    assert result.applied == []


def test_result_is_json_serialisable_evidence(ruleset):
    import json

    plan = plan_remediation(DOCUMENTS, ruleset)
    writer = RecordingWriter()
    result = apply_remediation(plan, writer=writer)
    payload = json.loads(json.dumps(result.to_dict()))

    assert payload["dry_run"] is True
    assert payload["outcome"] == "Observed"
    assert payload["changes"]


# --------------------------------------------------------------------------
# Rollback
# --------------------------------------------------------------------------


def test_rollback_restores_original_content_under_the_same_gates(ruleset):
    plan = plan_remediation(DOCUMENTS, ruleset)
    writer = RecordingWriter()
    apply_remediation(plan, writer=writer, dry_run=False, confirm=plan.confirmation_token)
    writer.writes.clear()

    result = rollback_remediation(plan, writer=writer, confirm=plan.rollback_token)

    assert result.outcome == Outcome.OBSERVED
    assert dict(writer.writes)["page-a"] == DOCUMENTS["page-a"]
    assert dict(writer.writes)["page-b"] == DOCUMENTS["page-b"]


def test_rollback_without_confirmation_refuses_to_write(ruleset):
    plan = plan_remediation(DOCUMENTS, ruleset)
    writer = RecordingWriter()

    with pytest.raises(ConfirmationRequired):
        rollback_remediation(plan, writer=writer)

    assert writer.writes == []


def test_rollback_token_differs_from_apply_token(ruleset):
    plan = plan_remediation(DOCUMENTS, ruleset)

    assert plan.rollback_token != plan.confirmation_token

    with pytest.raises(ConfirmationRequired):
        rollback_remediation(plan, writer=RecordingWriter(), confirm=plan.confirmation_token)


# --------------------------------------------------------------------------
# Genericity / independence
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "literal",
    ["jag.gov.bc.ca", "bcgov.sharepoint.com", "AG-CSB", "AG-BCPS", "CrownNet", "MediaInfo",
     "JUSTIN", "CEIS", "ORDS", "courthouse", "ITAU", "PIO", "ICM"],
)
def test_module_source_contains_no_project_literals(literal):
    source = (Path(__file__).resolve().parents[1] / "scripts" / "link_remediation.py").read_text()

    assert literal.lower() not in source.lower()


def test_module_ships_no_live_transport_or_default_urls():
    source = (Path(__file__).resolve().parents[1] / "scripts" / "link_remediation.py").read_text()

    assert "http://" not in source
    assert "https://" not in source
    for forbidden in ("import requests", "urllib.request", "subprocess", "Connect-PnPOnline"):
        assert forbidden not in source
