"""Tests for list_provisioning.py -- the reconcile-a-whole-schema entry point
and the three-gate write-safety pattern (dry-run default, injected executor
required, plan-derived confirmation token). Mirrors
sharepoint-link-remediation/scripts/link_remediation.py's gate exactly."""

from __future__ import annotations

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


def _empty_schema():
    return ProvisioningSchema()


def _empty_state():
    return CurrentState()


# ---------------------------------------------------------------------------
# plan_provisioning -- basic aggregation and outcomes
# ---------------------------------------------------------------------------

def test_plan_provisioning_empty_schema_is_empty_outcome():
    plan = plan_provisioning(_empty_schema(), _empty_state())
    assert plan.outcome == Outcome.EMPTY
    assert plan.field_actions == ()
    assert plan.content_type_actions == ()
    assert plan.list_creations == ()


def test_plan_provisioning_aggregates_field_actions():
    schema = ProvisioningSchema(
        site_fields=(FieldDef(internal_name="Widget_Count", display_name="Widget Count", type="Number"),)
    )
    plan = plan_provisioning(schema, _empty_state())
    assert len(plan.field_actions) == 1
    assert plan.field_actions[0].action == "create"
    assert plan.outcome == Outcome.OBSERVED


def test_plan_provisioning_aggregates_content_type_actions():
    schema = ProvisioningSchema(
        content_types=(
            ContentTypeDef(name="Demo_Item", fields=(ContentTypeFieldSpec(field_name="Widget_Count"),)),
        )
    )
    plan = plan_provisioning(schema, _empty_state())
    steps = [a.step for a in plan.content_type_actions]
    assert "create_content_type" in steps
    assert "link_field" in steps


def test_plan_provisioning_plans_list_creation_when_missing():
    schema = ProvisioningSchema(lists=(ListDef(title="Demo_List", template=100),))
    plan = plan_provisioning(schema, _empty_state())
    assert len(plan.list_creations) == 1
    assert plan.list_creations[0].title == "Demo_List"


def test_plan_provisioning_skips_creation_when_list_already_exists():
    schema = ProvisioningSchema(lists=(ListDef(title="Demo_List"),))
    state = CurrentState(lists={"Demo_List": ListState(title="Demo_List", exists=True, matching_count=1)})
    plan = plan_provisioning(schema, state)
    assert plan.list_creations == ()


# ---------------------------------------------------------------------------
# duplicate detection -- must block before any delete step
# ---------------------------------------------------------------------------

def test_detect_duplicate_lists_flags_multiple_matches():
    state = CurrentState(lists={"Demo_List": ListState(title="Demo_List", exists=True, matching_count=2)})
    schema = ProvisioningSchema(lists=(ListDef(title="Demo_List", recreate=True),))
    findings = detect_duplicate_lists(schema, state)
    assert len(findings) == 1
    assert "Demo_List" in findings[0]
    assert "2" in findings[0]


def test_detect_duplicate_lists_silent_when_single_match():
    state = CurrentState(lists={"Demo_List": ListState(title="Demo_List", exists=True, matching_count=1)})
    schema = ProvisioningSchema(lists=(ListDef(title="Demo_List", recreate=True),))
    assert detect_duplicate_lists(schema, state) == []


def test_plan_provisioning_records_duplicate_as_blocking_finding_not_silent_skip():
    state = CurrentState(lists={"Demo_List": ListState(title="Demo_List", exists=True, matching_count=3)})
    schema = ProvisioningSchema(lists=(ListDef(title="Demo_List", recreate=True),))
    plan = plan_provisioning(schema, state)
    assert len(plan.blocking_findings) == 1
    assert plan.outcome == Outcome.FAILED
    # a duplicate blocks deletion planning outright -- no deletion step for it
    assert plan.list_deletions == ()


def test_plan_provisioning_plans_deletion_for_recreate_list_with_no_duplicate():
    state = CurrentState(lists={"Demo_List": ListState(title="Demo_List", exists=True, matching_count=1)})
    schema = ProvisioningSchema(lists=(ListDef(title="Demo_List", recreate=True),))
    plan = plan_provisioning(schema, state)
    assert len(plan.list_deletions) == 1
    assert plan.list_deletions[0].blocking is False
    assert plan.blocking_findings == ()


# ---------------------------------------------------------------------------
# three-gate write safety -- dry-run / missing-executor / stale-token / valid-execute
# ---------------------------------------------------------------------------

def _writable_plan():
    schema = ProvisioningSchema(
        site_fields=(FieldDef(internal_name="Widget_Count", display_name="Widget Count", type="Number"),),
        lists=(ListDef(title="Demo_List"),),
    )
    return plan_provisioning(schema, _empty_state())


def test_apply_provisioning_dry_run_by_default_writes_nothing():
    plan = _writable_plan()
    calls = []
    result = apply_provisioning(plan, executor=lambda step, detail: calls.append((step, detail)))
    assert result.dry_run is True
    assert calls == []
    assert result.outcome == Outcome.OBSERVED


def test_apply_provisioning_missing_executor_raises():
    plan = _writable_plan()
    with pytest.raises(ExecutorRequired):
        apply_provisioning(plan, dry_run=False, confirm=plan.confirmation_token)


def test_apply_provisioning_stale_or_missing_token_raises():
    plan = _writable_plan()
    with pytest.raises(ConfirmationRequired):
        apply_provisioning(
            plan, executor=lambda step, detail: None, dry_run=False, confirm="not-the-real-token"
        )
    with pytest.raises(ConfirmationRequired):
        apply_provisioning(plan, executor=lambda step, detail: None, dry_run=False, confirm=None)


def test_apply_provisioning_token_goes_stale_when_plan_source_data_changes():
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


def test_apply_provisioning_real_executor_with_valid_token_executes():
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


def test_apply_provisioning_partial_when_executor_fails_some_steps():
    plan = _writable_plan()

    def flaky(step, detail):
        if step == "field":
            raise RuntimeError("boom")

    result = apply_provisioning(plan, executor=flaky, dry_run=False, confirm=plan.confirmation_token)
    assert result.outcome == Outcome.PARTIAL
    assert len(result.failed) >= 1


def test_apply_provisioning_forbidden_when_executor_raises_permission_error():
    plan = _writable_plan()

    def forbidden(step, detail):
        raise PermissionError("no access")

    result = apply_provisioning(plan, executor=forbidden, dry_run=False, confirm=plan.confirmation_token)
    assert result.outcome == Outcome.FORBIDDEN


def test_apply_provisioning_blocking_findings_refuse_execution_even_with_valid_token():
    state = CurrentState(lists={"Demo_List": ListState(title="Demo_List", exists=True, matching_count=2)})
    schema = ProvisioningSchema(lists=(ListDef(title="Demo_List", recreate=True),))
    plan = plan_provisioning(schema, state)
    with pytest.raises(DuplicateListsBlockProvisioning):
        apply_provisioning(
            plan, executor=lambda step, detail: None, dry_run=False, confirm=plan.confirmation_token
        )


def test_apply_provisioning_empty_plan_is_empty_outcome_even_with_real_executor():
    plan = plan_provisioning(_empty_schema(), _empty_state())
    result = apply_provisioning(
        plan, executor=lambda step, detail: None, dry_run=False, confirm=plan.confirmation_token
    )
    assert result.outcome == Outcome.EMPTY


# ---------------------------------------------------------------------------
# fail-loud verification after a delete step
# ---------------------------------------------------------------------------

def test_verify_deletion_complete_passes_when_gone():
    verify_deletion_complete("Demo_List", still_exists=False)  # must not raise


def test_verify_deletion_complete_fails_loud_when_still_present():
    with pytest.raises(DeletionVerificationFailed):
        verify_deletion_complete("Demo_List", still_exists=True)
