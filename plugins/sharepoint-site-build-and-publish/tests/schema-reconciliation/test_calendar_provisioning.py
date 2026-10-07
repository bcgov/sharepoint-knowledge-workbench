"""Tests for calendar_provisioning.py -- provisioning a working modern SPO
calendar list. Encodes a real, validated platform bug workaround (Start/End
as site columns or content-type-linked fields silently breaks calendar view
rendering in SPO) as planning logic, so the mistake is structurally
unrepresentable, not just documented. Mirrors list_provisioning.py's
three-gate write-safety pattern exactly (dry-run default, injected executor
required, plan-derived confirmation token).
Purpose:
    Verify calendar-list planning protects the modern calendar workaround and gates writes.

Key Input Dependencies:
    - calendar_provisioning planner and injected executor fixtures; no live SharePoint connection.

Function Index:
    _valid_def, TestPlanCalendarList.test_rejects_start_end_declared_as_site_columns, TestPlanCalendarList.test_valid_definition_plans_generic_list_template_not_calendar_template, TestPlanCalendarList.test_plan_always_includes_list_local_start_end_fields, TestPlanCalendarList.test_plan_always_includes_modern_view_creation_step, TestPlanCalendarList.test_outcome_observed_for_a_real_plan, TestPlanCalendarList.test_confirmation_token_is_stable_for_identical_input, TestPlanCalendarList.test_confirmation_token_changes_with_title, TestApplyCalendarList.test_dry_run_by_default_performs_no_writes, TestApplyCalendarList.test_real_apply_without_executor_raises, TestApplyCalendarList.test_real_apply_with_wrong_confirmation_token_raises, TestApplyCalendarList.test_real_apply_with_valid_executor_and_token_executes_all_steps, TestApplyCalendarList.test_real_apply_reports_partial_on_step_failure
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "schema-reconciliation"))

import pytest

from calendar_provisioning import (
    CalendarListDef,
    ConfirmationRequired,
    ExecutorRequired,
    StartEndScopeViolation,
    apply_calendar_list,
    plan_calendar_list,
)
from provisioning_outcomes import Outcome


# Create a valid caller-declared calendar-list definition for planning tests.
def _valid_def():
    """Create a valid caller-declared calendar-list definition for planning tests."""
    return CalendarListDef(title="Team Calendar")


class TestPlanCalendarList:
    # Verify the contract that rejects start end declared as site columns.
    def test_rejects_start_end_declared_as_site_columns(self):
        """Verify the contract that rejects start end declared as site columns."""
        with pytest.raises(StartEndScopeViolation):
            plan_calendar_list(
                CalendarListDef(title="Team Calendar", start_end_site_columns=("Start", "End"))
            )

    # Verify the contract that valid definition plans generic list template not calendar template.
    def test_valid_definition_plans_generic_list_template_not_calendar_template(self):
        """Verify the contract that valid definition plans generic list template not calendar template."""
        plan = plan_calendar_list(_valid_def())
        assert plan.list_creation.template == 100  # Generic List, never 106 (Calendar)

    # Verify the contract that plan always includes list local start end fields.
    def test_plan_always_includes_list_local_start_end_fields(self):
        """Verify the contract that plan always includes list local start end fields."""
        plan = plan_calendar_list(_valid_def())
        field_names = {f.internal_name for f in plan.list_local_fields}
        assert {"Start", "End"} <= field_names

    # Verify the contract that plan always includes modern view creation step.
    def test_plan_always_includes_modern_view_creation_step(self):
        """Verify the contract that plan always includes modern view creation step."""
        plan = plan_calendar_list(_valid_def())
        assert plan.view_creation.view_type_kind == 1
        assert plan.view_creation.view_type2 == "MODERNCALENDAR"

    # Verify the contract that outcome observed for a real plan.
    def test_outcome_observed_for_a_real_plan(self):
        """Verify the contract that outcome observed for a real plan."""
        plan = plan_calendar_list(_valid_def())
        assert plan.outcome == Outcome.OBSERVED

    # Verify the contract that confirmation token is stable for identical input.
    def test_confirmation_token_is_stable_for_identical_input(self):
        """Verify the contract that confirmation token is stable for identical input."""
        plan_a = plan_calendar_list(_valid_def())
        plan_b = plan_calendar_list(_valid_def())
        assert plan_a.confirmation_token == plan_b.confirmation_token

    # Verify the contract that confirmation token changes with title.
    def test_confirmation_token_changes_with_title(self):
        """Verify the contract that confirmation token changes with title."""
        plan_a = plan_calendar_list(CalendarListDef(title="A"))
        plan_b = plan_calendar_list(CalendarListDef(title="B"))
        assert plan_a.confirmation_token != plan_b.confirmation_token


class TestApplyCalendarList:
    # Verify the contract that dry run by default performs no writes.
    def test_dry_run_by_default_performs_no_writes(self):
        """Verify the contract that dry run by default performs no writes."""
        plan = plan_calendar_list(_valid_def())
        result = apply_calendar_list(plan)
        assert result.dry_run is True
        assert result.executed == ()

    # Verify the contract that real apply without executor raises.
    def test_real_apply_without_executor_raises(self):
        """Verify the contract that real apply without executor raises."""
        plan = plan_calendar_list(_valid_def())
        with pytest.raises(ExecutorRequired):
            apply_calendar_list(plan, dry_run=False, executor=None, confirm=plan.confirmation_token)

    # Verify the contract that real apply with wrong confirmation token raises.
    def test_real_apply_with_wrong_confirmation_token_raises(self):
        """Verify the contract that real apply with wrong confirmation token raises."""
        plan = plan_calendar_list(_valid_def())
        with pytest.raises(ConfirmationRequired):
            apply_calendar_list(
                plan, dry_run=False, executor=lambda step, detail: None, confirm="WRONG"
            )

    # Verify the contract that real apply with valid executor and token executes all steps.
    def test_real_apply_with_valid_executor_and_token_executes_all_steps(self):
        """Verify the contract that real apply with valid executor and token executes all steps."""
        plan = plan_calendar_list(_valid_def())
        executed_steps = []

        # Capture or simulate the caller-injected operation used by the test case.
        def executor(step, detail):
            """Capture or simulate the caller-injected operation used by the test case."""
            executed_steps.append(step)

        result = apply_calendar_list(
            plan, dry_run=False, executor=executor, confirm=plan.confirmation_token
        )
        assert result.outcome == Outcome.OBSERVED
        assert "list_creation" in executed_steps
        assert "list_local_field" in executed_steps
        assert "view_creation" in executed_steps

    # Verify the contract that real apply reports partial on step failure.
    def test_real_apply_reports_partial_on_step_failure(self):
        """Verify the contract that real apply reports partial on step failure."""
        plan = plan_calendar_list(_valid_def())

        # Capture or simulate the caller-injected operation used by the test case.
        def executor(step, detail):
            """Capture or simulate the caller-injected operation used by the test case."""
            if step == "view_creation":
                raise RuntimeError("REST call failed")

        result = apply_calendar_list(
            plan, dry_run=False, executor=executor, confirm=plan.confirmation_token
        )
        assert result.outcome == Outcome.PARTIAL
        assert any(step == "view_creation" for step, _ in result.failed)
