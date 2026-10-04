"""Tests for calendar_provisioning.py -- provisioning a working modern SPO
calendar list. Encodes a real, validated platform bug workaround (Start/End
as site columns or content-type-linked fields silently breaks calendar view
rendering in SPO) as planning logic, so the mistake is structurally
unrepresentable, not just documented. Mirrors list_provisioning.py's
three-gate write-safety pattern exactly (dry-run default, injected executor
required, plan-derived confirmation token)."""

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


def _valid_def():
    return CalendarListDef(title="Team Calendar")


class TestPlanCalendarList:
    def test_rejects_start_end_declared_as_site_columns(self):
        with pytest.raises(StartEndScopeViolation):
            plan_calendar_list(
                CalendarListDef(title="Team Calendar", start_end_site_columns=("Start", "End"))
            )

    def test_valid_definition_plans_generic_list_template_not_calendar_template(self):
        plan = plan_calendar_list(_valid_def())
        assert plan.list_creation.template == 100  # Generic List, never 106 (Calendar)

    def test_plan_always_includes_list_local_start_end_fields(self):
        plan = plan_calendar_list(_valid_def())
        field_names = {f.internal_name for f in plan.list_local_fields}
        assert {"Start", "End"} <= field_names

    def test_plan_always_includes_modern_view_creation_step(self):
        plan = plan_calendar_list(_valid_def())
        assert plan.view_creation.view_type_kind == 1
        assert plan.view_creation.view_type2 == "MODERNCALENDAR"

    def test_outcome_observed_for_a_real_plan(self):
        plan = plan_calendar_list(_valid_def())
        assert plan.outcome == Outcome.OBSERVED

    def test_confirmation_token_is_stable_for_identical_input(self):
        plan_a = plan_calendar_list(_valid_def())
        plan_b = plan_calendar_list(_valid_def())
        assert plan_a.confirmation_token == plan_b.confirmation_token

    def test_confirmation_token_changes_with_title(self):
        plan_a = plan_calendar_list(CalendarListDef(title="A"))
        plan_b = plan_calendar_list(CalendarListDef(title="B"))
        assert plan_a.confirmation_token != plan_b.confirmation_token


class TestApplyCalendarList:
    def test_dry_run_by_default_performs_no_writes(self):
        plan = plan_calendar_list(_valid_def())
        result = apply_calendar_list(plan)
        assert result.dry_run is True
        assert result.executed == ()

    def test_real_apply_without_executor_raises(self):
        plan = plan_calendar_list(_valid_def())
        with pytest.raises(ExecutorRequired):
            apply_calendar_list(plan, dry_run=False, executor=None, confirm=plan.confirmation_token)

    def test_real_apply_with_wrong_confirmation_token_raises(self):
        plan = plan_calendar_list(_valid_def())
        with pytest.raises(ConfirmationRequired):
            apply_calendar_list(
                plan, dry_run=False, executor=lambda step, detail: None, confirm="WRONG"
            )

    def test_real_apply_with_valid_executor_and_token_executes_all_steps(self):
        plan = plan_calendar_list(_valid_def())
        executed_steps = []

        def executor(step, detail):
            executed_steps.append(step)

        result = apply_calendar_list(
            plan, dry_run=False, executor=executor, confirm=plan.confirmation_token
        )
        assert result.outcome == Outcome.OBSERVED
        assert "list_creation" in executed_steps
        assert "list_local_field" in executed_steps
        assert "view_creation" in executed_steps

    def test_real_apply_reports_partial_on_step_failure(self):
        plan = plan_calendar_list(_valid_def())

        def executor(step, detail):
            if step == "view_creation":
                raise RuntimeError("REST call failed")

        result = apply_calendar_list(
            plan, dry_run=False, executor=executor, confirm=plan.confirmation_token
        )
        assert result.outcome == Outcome.PARTIAL
        assert any(step == "view_creation" for step, _ in result.failed)
