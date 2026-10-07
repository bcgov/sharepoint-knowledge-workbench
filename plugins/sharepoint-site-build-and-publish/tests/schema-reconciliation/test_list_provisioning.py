"""Tests for list_provisioning.py -- the reconcile-a-whole-schema entry point
and the three-gate write-safety pattern (dry-run default, injected executor
required, plan-derived confirmation token). Mirrors
sharepoint-site-migration/scripts/link_remediation.py's gate exactly.
Purpose:
    Verify schema aggregation, duplicate-list blocking, dry-run defaults, and guarded execution.

Key Input Dependencies:
    - list_provisioning, related field/content-type planners, and injected executor fixtures.

Function Index:
    _empty_schema, _empty_state, test_plan_provisioning_empty_schema_is_empty_outcome, test_plan_provisioning_aggregates_field_actions, test_plan_provisioning_aggregates_content_type_actions, test_plan_provisioning_plans_list_creation_when_missing, test_plan_provisioning_skips_creation_when_list_already_exists, test_detect_duplicate_lists_flags_multiple_matches, test_detect_duplicate_lists_silent_when_single_match, test_plan_provisioning_records_duplicate_as_blocking_finding_not_silent_skip, test_plan_provisioning_plans_deletion_for_recreate_list_with_no_duplicate, _writable_plan, test_apply_provisioning_dry_run_by_default_writes_nothing, test_apply_provisioning_missing_executor_raises, test_apply_provisioning_stale_or_missing_token_raises, test_apply_provisioning_token_goes_stale_when_plan_source_data_changes, test_apply_provisioning_real_executor_with_valid_token_executes, test_apply_provisioning_partial_when_executor_fails_some_steps, test_apply_provisioning_forbidden_when_executor_raises_permission_error, test_apply_provisioning_blocking_findings_refuse_execution_even_with_valid_token, test_apply_provisioning_empty_plan_is_empty_outcome_even_with_real_executor, test_verify_deletion_complete_passes_when_gone, test_verify_deletion_complete_fails_loud_when_still_present, test_list_creation_serialization_preserves_template_and_metadata, test_recreate_list_executes_deletion_before_creation, test_recreate_list_skips_creation_if_deletion_fails
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "schema-reconciliation"))

import pytest

from field_provisioning import FieldDef
from content_type_provisioning import ContentTypeDef, ContentTypeFieldSpec, ContentTypeState
from list_provisioning import (
    ConfirmationRequired,
    CurrentState,
    DeletionVerificationFailed,
    DuplicateListsBlockProvisioning,
    ExecutorRequired,
    ListDef,
    ListState,
    ProvisioningSchema,
    apply_provisioning,
    detect_duplicate_lists,
    plan_provisioning,
    verify_deletion_complete,
)
from provisioning_outcomes import Outcome


# Create an empty provisioning schema for outcome and safety-gate tests.
def _empty_schema():
    """Create an empty provisioning schema for outcome and safety-gate tests."""
    return ProvisioningSchema()


# Create an empty caller-supplied observation of SharePoint state.
def _empty_state():
    """Create an empty caller-supplied observation of SharePoint state."""
    return CurrentState()


# ---------------------------------------------------------------------------
# plan_provisioning -- basic aggregation and outcomes
# ---------------------------------------------------------------------------

# Verify the contract that plan provisioning empty schema is empty outcome.
def test_plan_provisioning_empty_schema_is_empty_outcome():
    """Verify the contract that plan provisioning empty schema is empty outcome."""
    plan = plan_provisioning(_empty_schema(), _empty_state())
    assert plan.outcome == Outcome.EMPTY
    assert plan.field_actions == ()
    assert plan.content_type_actions == ()
    assert plan.list_creations == ()


# Verify the contract that plan provisioning aggregates field actions.
def test_plan_provisioning_aggregates_field_actions():
    """Verify the contract that plan provisioning aggregates field actions."""
    schema = ProvisioningSchema(
        site_fields=(FieldDef(internal_name="Widget_Count", display_name="Widget Count", type="Number"),)
    )
    plan = plan_provisioning(schema, _empty_state())
    assert len(plan.field_actions) == 1
    assert plan.field_actions[0].action == "create"
    assert plan.outcome == Outcome.OBSERVED


# Verify the contract that plan provisioning aggregates content type actions.
def test_plan_provisioning_aggregates_content_type_actions():
    """Verify the contract that plan provisioning aggregates content type actions."""
    schema = ProvisioningSchema(
        content_types=(
            ContentTypeDef(name="Demo_Item", fields=(ContentTypeFieldSpec(field_name="Widget_Count"),)),
        )
    )
    plan = plan_provisioning(schema, _empty_state())
    steps = [a.step for a in plan.content_type_actions]
    assert "create_content_type" in steps
    assert "link_field" in steps


# Verify the contract that plan provisioning plans list creation when missing.
def test_plan_provisioning_plans_list_creation_when_missing():
    """Verify the contract that plan provisioning plans list creation when missing."""
    schema = ProvisioningSchema(lists=(ListDef(title="Demo_List", template=100),))
    plan = plan_provisioning(schema, _empty_state())
    assert len(plan.list_creations) == 1
    assert plan.list_creations[0].title == "Demo_List"


# Verify the contract that plan provisioning skips creation when list already exists.
def test_plan_provisioning_skips_creation_when_list_already_exists():
    """Verify the contract that plan provisioning skips creation when list already exists."""
    schema = ProvisioningSchema(lists=(ListDef(title="Demo_List"),))
    state = CurrentState(lists={"Demo_List": ListState(title="Demo_List", exists=True, matching_count=1)})
    plan = plan_provisioning(schema, state)
    assert plan.list_creations == ()


# ---------------------------------------------------------------------------
# duplicate detection -- must block before any delete step
# ---------------------------------------------------------------------------

# Verify the contract that detect duplicate lists flags multiple matches.
def test_detect_duplicate_lists_flags_multiple_matches():
    """Verify the contract that detect duplicate lists flags multiple matches."""
    state = CurrentState(lists={"Demo_List": ListState(title="Demo_List", exists=True, matching_count=2)})
    schema = ProvisioningSchema(lists=(ListDef(title="Demo_List", recreate=True),))
    findings = detect_duplicate_lists(schema, state)
    assert len(findings) == 1
    assert "Demo_List" in findings[0]
    assert "2" in findings[0]


# Verify the contract that detect duplicate lists silent when single match.
def test_detect_duplicate_lists_silent_when_single_match():
    """Verify the contract that detect duplicate lists silent when single match."""
    state = CurrentState(lists={"Demo_List": ListState(title="Demo_List", exists=True, matching_count=1)})
    schema = ProvisioningSchema(lists=(ListDef(title="Demo_List", recreate=True),))
    assert detect_duplicate_lists(schema, state) == []


# Verify the contract that plan provisioning records duplicate as blocking finding not silent skip.
def test_plan_provisioning_records_duplicate_as_blocking_finding_not_silent_skip():
    """Verify the contract that plan provisioning records duplicate as blocking finding not silent skip."""
    state = CurrentState(lists={"Demo_List": ListState(title="Demo_List", exists=True, matching_count=3)})
    schema = ProvisioningSchema(lists=(ListDef(title="Demo_List", recreate=True),))
    plan = plan_provisioning(schema, state)
    assert len(plan.blocking_findings) == 1
    assert plan.outcome == Outcome.FAILED
    # a duplicate blocks deletion planning outright -- no deletion step for it
    assert plan.list_deletions == ()


# Verify the contract that plan provisioning plans deletion for recreate list with no duplicate.
def test_plan_provisioning_plans_deletion_for_recreate_list_with_no_duplicate():
    """Verify the contract that plan provisioning plans deletion for recreate list with no duplicate."""
    state = CurrentState(lists={"Demo_List": ListState(title="Demo_List", exists=True, matching_count=1)})
    schema = ProvisioningSchema(lists=(ListDef(title="Demo_List", recreate=True),))
    plan = plan_provisioning(schema, state)
    assert len(plan.list_deletions) == 1
    assert plan.list_deletions[0].blocking is False
    assert plan.blocking_findings == ()


# ---------------------------------------------------------------------------
# three-gate write safety -- dry-run / missing-executor / stale-token / valid-execute
# ---------------------------------------------------------------------------

# Build a plan containing field and list writes for apply-gate tests.
def _writable_plan():
    """Build a plan containing field and list writes for apply-gate tests."""
    schema = ProvisioningSchema(
        site_fields=(FieldDef(internal_name="Widget_Count", display_name="Widget Count", type="Number"),),
        lists=(ListDef(title="Demo_List"),),
    )
    return plan_provisioning(schema, _empty_state())


# Verify the contract that apply provisioning dry run by default writes nothing.
def test_apply_provisioning_dry_run_by_default_writes_nothing():
    """Verify the contract that apply provisioning dry run by default writes nothing."""
    plan = _writable_plan()
    calls = []
    result = apply_provisioning(plan, executor=lambda step, detail: calls.append((step, detail)))
    assert result.dry_run is True
    assert calls == []
    assert result.outcome == Outcome.OBSERVED


# Verify the contract that apply provisioning missing executor raises.
def test_apply_provisioning_missing_executor_raises():
    """Verify the contract that apply provisioning missing executor raises."""
    plan = _writable_plan()
    with pytest.raises(ExecutorRequired):
        apply_provisioning(plan, dry_run=False, confirm=plan.confirmation_token)


# Verify the contract that apply provisioning stale or missing token raises.
def test_apply_provisioning_stale_or_missing_token_raises():
    """Verify the contract that apply provisioning stale or missing token raises."""
    plan = _writable_plan()
    with pytest.raises(ConfirmationRequired):
        apply_provisioning(
            plan, executor=lambda step, detail: None, dry_run=False, confirm="not-the-real-token"
        )
    with pytest.raises(ConfirmationRequired):
        apply_provisioning(plan, executor=lambda step, detail: None, dry_run=False, confirm=None)


# Verify the contract that apply provisioning token goes stale when plan source data changes.
def test_apply_provisioning_token_goes_stale_when_plan_source_data_changes():
    """Verify the contract that apply provisioning token goes stale when plan source data changes."""
    schema = ProvisioningSchema(site_fields=(FieldDef(internal_name="A", display_name="A", type="Text"),))
    plan_one = plan_provisioning(schema, _empty_state())
    schema_changed = ProvisioningSchema(
        site_fields=(FieldDef(internal_name="A", display_name="A", type="Text"),
                     FieldDef(internal_name="B", display_name="B", type="Text"))
    )
    plan_two = plan_provisioning(schema_changed, _empty_state())
    assert plan_one.confirmation_token != plan_two.confirmation_token
    with pytest.raises(ConfirmationRequired):
        apply_provisioning(
            plan_two, executor=lambda step, detail: None, dry_run=False, confirm=plan_one.confirmation_token
        )


# Verify the contract that apply provisioning real executor with valid token executes.
def test_apply_provisioning_real_executor_with_valid_token_executes():
    """Verify the contract that apply provisioning real executor with valid token executes."""
    plan = _writable_plan()
    calls = []
    result = apply_provisioning(
        plan,
        executor=lambda step, detail: calls.append((step, detail)),
        dry_run=False,
        confirm=plan.confirmation_token,
    )
    assert result.dry_run is False
    assert len(calls) > 0
    assert result.outcome == Outcome.OBSERVED
    assert len(result.executed) == len(calls)


# Verify the contract that apply provisioning partial when executor fails some steps.
def test_apply_provisioning_partial_when_executor_fails_some_steps():
    """Verify the contract that apply provisioning partial when executor fails some steps."""
    plan = _writable_plan()

    # Simulate an executor failure on a selected step to test partial apply reporting.
    def flaky(step, detail):
        """Simulate an executor failure on a selected step to test partial apply reporting."""
        if step == "field":
            raise RuntimeError("boom")

    result = apply_provisioning(plan, executor=flaky, dry_run=False, confirm=plan.confirmation_token)
    assert result.outcome == Outcome.PARTIAL
    assert len(result.failed) >= 1


# Verify the contract that apply provisioning forbidden when executor raises permission error.
def test_apply_provisioning_forbidden_when_executor_raises_permission_error():
    """Verify the contract that apply provisioning forbidden when executor raises permission error."""
    plan = _writable_plan()

    # Simulate an authorization failure to test the forbidden apply outcome.
    def forbidden(step, detail):
        """Simulate an authorization failure to test the forbidden apply outcome."""
        raise PermissionError("no access")

    result = apply_provisioning(plan, executor=forbidden, dry_run=False, confirm=plan.confirmation_token)
    assert result.outcome == Outcome.FORBIDDEN


# Verify the contract that apply provisioning blocking findings refuse execution even with valid token.
def test_apply_provisioning_blocking_findings_refuse_execution_even_with_valid_token():
    """Verify the contract that apply provisioning blocking findings refuse execution even with valid token."""
    state = CurrentState(lists={"Demo_List": ListState(title="Demo_List", exists=True, matching_count=2)})
    schema = ProvisioningSchema(lists=(ListDef(title="Demo_List", recreate=True),))
    plan = plan_provisioning(schema, state)
    with pytest.raises(DuplicateListsBlockProvisioning):
        apply_provisioning(
            plan, executor=lambda step, detail: None, dry_run=False, confirm=plan.confirmation_token
        )


# Verify the contract that apply provisioning empty plan is empty outcome even with real executor.
def test_apply_provisioning_empty_plan_is_empty_outcome_even_with_real_executor():
    """Verify the contract that apply provisioning empty plan is empty outcome even with real executor."""
    plan = plan_provisioning(_empty_schema(), _empty_state())
    result = apply_provisioning(
        plan, executor=lambda step, detail: None, dry_run=False, confirm=plan.confirmation_token
    )
    assert result.outcome == Outcome.EMPTY


# ---------------------------------------------------------------------------
# fail-loud verification after a delete step
# ---------------------------------------------------------------------------

# Verify the contract that verify deletion complete passes when gone.
def test_verify_deletion_complete_passes_when_gone():
    """Verify the contract that verify deletion complete passes when gone."""
    verify_deletion_complete("Demo_List", still_exists=False)  # must not raise


# Verify the contract that verify deletion complete fails loud when still present.
def test_verify_deletion_complete_fails_loud_when_still_present():
    """Verify the contract that verify deletion complete fails loud when still present."""
    with pytest.raises(DeletionVerificationFailed):
        verify_deletion_complete("Demo_List", still_exists=True)


# Verify the contract that list creation serialization preserves template and metadata.
def test_list_creation_serialization_preserves_template_and_metadata():
    """Verify the contract that list creation serialization preserves template and metadata."""
    schema = ProvisioningSchema(
        lists=(ListDef(title="DocLib", template=101, description="Library", content_types=("CustomDoc",)),)
    )
    plan = plan_provisioning(schema, _empty_state())
    assert len(plan.list_creations) == 1
    creation = plan.list_creations[0]
    assert creation.template == 101
    assert creation.description == "Library"
    assert creation.content_types == ("CustomDoc",)

    payload = plan.to_dict()
    found = [c for c in payload["list_creations"] if c["title"] == "DocLib"]
    assert len(found) == 1
    assert found[0]["template"] == 101
    assert found[0]["description"] == "Library"
    assert found[0]["content_types"] == ["CustomDoc"]


# Verify the contract that recreate list executes deletion before creation.
def test_recreate_list_executes_deletion_before_creation():
    """Verify the contract that recreate list executes deletion before creation."""
    state = CurrentState(lists={"Demo_List": ListState(title="Demo_List", exists=True)})
    schema = ProvisioningSchema(lists=(ListDef(title="Demo_List", recreate=True),))
    plan = plan_provisioning(schema, state)

    calls = []
    # Capture or simulate the caller-injected operation used by the test case.
    def executor(step, detail):
        """Capture or simulate the caller-injected operation used by the test case."""
        calls.append((step, detail["title"]))

    result = apply_provisioning(plan, executor=executor, dry_run=False, confirm=plan.confirmation_token)
    assert result.outcome == Outcome.OBSERVED
    assert calls == [("list_deletion", "Demo_List"), ("list_creation", "Demo_List")]


# Verify the contract that recreate list skips creation if deletion fails.
def test_recreate_list_skips_creation_if_deletion_fails():
    """Verify the contract that recreate list skips creation if deletion fails."""
    state = CurrentState(lists={"Demo_List": ListState(title="Demo_List", exists=True)})
    schema = ProvisioningSchema(lists=(ListDef(title="Demo_List", recreate=True),))
    plan = plan_provisioning(schema, state)

    calls = []
    # Capture or simulate the caller-injected operation used by the test case.
    def executor(step, detail):
        """Capture or simulate the caller-injected operation used by the test case."""
        calls.append(step)
        if step == "list_deletion":
            raise RuntimeError("delete failed")

    result = apply_provisioning(plan, executor=executor, dry_run=False, confirm=plan.confirmation_token)
    assert result.outcome == Outcome.FAILED
    assert calls == ["list_deletion"]
    assert any("skipped creation" in err for _, err in result.failed)

