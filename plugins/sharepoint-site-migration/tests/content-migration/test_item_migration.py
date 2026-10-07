"""Tests for item_migration.py -- item-level batched content migration with
retry, gated by the same three-gate write-safety contract used everywhere
else in this workbench (dry-run default, injected executor, plan-derived
confirmation token).

Purpose: Tests for item_migration.py -- item-level batched content migration with retry, gated by the same three-gate write-safety contract used everywhere else in this workbench (dry-run default, injected executor, plan-derived confirmation token).
Key Input Dependencies: item_migration, provisioning_outcomes.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "content-migration"))

import pytest

from item_migration import (
    ConfirmationRequired,
    ExecutorRequired,
    MigrationItem,
    apply_item_migration,
    plan_item_migration,
)
from provisioning_outcomes import Outcome


def _items(n: int) -> tuple[MigrationItem, ...]:
    """Test helper: items."""
    return tuple(MigrationItem(source_id=i, fields={"Title": f"Item {i}"}) for i in range(n))


class TestPlanItemMigration:
    def test_empty_items_is_empty_outcome(self):
        """Verify empty items is empty outcome."""
        plan = plan_item_migration((), batch_size=100)
        assert plan.outcome == Outcome.EMPTY
        assert plan.batches == ()

    def test_batches_items_by_batch_size(self):
        """Verify batches items by batch size."""
        plan = plan_item_migration(_items(5), batch_size=2)
        assert [len(b) for b in plan.batches] == [2, 2, 1]

    def test_single_batch_when_batch_size_exceeds_item_count(self):
        """Verify single batch when batch size exceeds item count."""
        plan = plan_item_migration(_items(3), batch_size=100)
        assert len(plan.batches) == 1
        assert len(plan.batches[0]) == 3

    def test_outcome_observed_for_nonempty_plan(self):
        """Verify outcome observed for nonempty plan."""
        plan = plan_item_migration(_items(1), batch_size=10)
        assert plan.outcome == Outcome.OBSERVED

    def test_confirmation_token_stable_for_identical_input(self):
        """Verify confirmation token stable for identical input."""
        plan_a = plan_item_migration(_items(3), batch_size=2)
        plan_b = plan_item_migration(_items(3), batch_size=2)
        assert plan_a.confirmation_token == plan_b.confirmation_token

    def test_confirmation_token_changes_with_batch_size(self):
        """Verify confirmation token changes with batch size."""
        plan_a = plan_item_migration(_items(3), batch_size=1)
        plan_b = plan_item_migration(_items(3), batch_size=3)
        assert plan_a.confirmation_token != plan_b.confirmation_token


class TestApplyItemMigration:
    def test_dry_run_by_default_performs_no_writes(self):
        """Verify dry run by default performs no writes."""
        plan = plan_item_migration(_items(3), batch_size=2)
        result = apply_item_migration(plan)
        assert result.dry_run is True
        assert result.migrated == ()

    def test_real_apply_without_executor_raises(self):
        """Verify real apply without executor raises."""
        plan = plan_item_migration(_items(1), batch_size=10)
        with pytest.raises(ExecutorRequired):
            apply_item_migration(plan, dry_run=False, executor=None, confirm=plan.confirmation_token)

    def test_real_apply_with_wrong_token_raises(self):
        """Verify real apply with wrong token raises."""
        plan = plan_item_migration(_items(1), batch_size=10)
        with pytest.raises(ConfirmationRequired):
            apply_item_migration(plan, dry_run=False, executor=lambda item: 100, confirm="WRONG")

    def test_real_apply_migrates_every_item_and_reports_source_to_dest_ids(self):
        """Verify real apply migrates every item and reports source to dest ids."""
        plan = plan_item_migration(_items(3), batch_size=2)

        def executor(item: MigrationItem) -> int:
            """Test double for executor used by the enclosing test."""
            return item.source_id + 1000  # fake dest id

        result = apply_item_migration(plan, dry_run=False, executor=executor, confirm=plan.confirmation_token)
        assert result.outcome == Outcome.OBSERVED
        assert dict(result.migrated) == {0: 1000, 1: 1001, 2: 1002}
        assert result.failed == ()

    def test_transient_failure_is_retried_up_to_the_limit(self):
        """Verify transient failure is retried up to the limit."""
        plan = plan_item_migration(_items(1), batch_size=10)
        attempts = {"count": 0}

        def flaky_executor(item: MigrationItem) -> int:
            """Test double for flaky executor used by the enclosing test."""
            attempts["count"] += 1
            if attempts["count"] < 3:
                raise RuntimeError("throttled")
            return 500

        result = apply_item_migration(
            plan, dry_run=False, executor=flaky_executor, confirm=plan.confirmation_token, retry_attempts=3
        )
        assert result.outcome == Outcome.OBSERVED
        assert dict(result.migrated) == {0: 500}
        assert attempts["count"] == 3

    def test_exhausting_retries_reports_partial_not_a_crash(self):
        """Verify exhausting retries reports partial not a crash."""
        plan = plan_item_migration(_items(2), batch_size=10)

        def always_fails(item: MigrationItem) -> int:
            """Test double for always fails used by the enclosing test."""
            raise RuntimeError("permanent failure")

        result = apply_item_migration(
            plan, dry_run=False, executor=always_fails, confirm=plan.confirmation_token, retry_attempts=2
        )
        assert result.outcome == Outcome.FAILED
        assert result.migrated == ()
        assert {source_id for source_id, _ in result.failed} == {0, 1}

    def test_partial_success_across_items_is_reported_as_partial(self):
        """Verify partial success across items is reported as partial."""
        plan = plan_item_migration(_items(2), batch_size=10)

        def executor(item: MigrationItem) -> int:
            """Test double for executor used by the enclosing test."""
            if item.source_id == 1:
                raise RuntimeError("permanent failure")
            return 900

        result = apply_item_migration(
            plan, dry_run=False, executor=executor, confirm=plan.confirmation_token, retry_attempts=1
        )
        assert result.outcome == Outcome.PARTIAL
        assert dict(result.migrated) == {0: 900}
        assert any(source_id == 1 for source_id, _ in result.failed)

    def test_retry_attempts_zero_is_rejected_not_silently_dropping_every_item(self):
        """External review finding: retry_attempts=0 makes `range(retry_attempts)`
        never execute, so every item lands in neither migrated nor failed and
        the function falls through to OBSERVED -- silent, complete data loss
        reported as success. Must raise instead of running."""
        plan = plan_item_migration(_items(2), batch_size=10)
        with pytest.raises(ValueError, match="retry_attempts"):
            apply_item_migration(
                plan, dry_run=False, executor=lambda item: 1,
                confirm=plan.confirmation_token, retry_attempts=0,
            )

    def test_retry_attempts_negative_is_rejected(self):
        """Verify retry attempts negative is rejected."""
        plan = plan_item_migration(_items(1), batch_size=10)
        with pytest.raises(ValueError, match="retry_attempts"):
            apply_item_migration(
                plan, dry_run=False, executor=lambda item: 1,
                confirm=plan.confirmation_token, retry_attempts=-1,
            )

    def test_batch_size_zero_is_rejected(self):
        """Verify batch size zero is rejected."""
        with pytest.raises(ValueError, match="batch_size"):
            plan_item_migration(_items(2), batch_size=0)

    def test_batch_size_negative_is_rejected(self):
        """Verify batch size negative is rejected."""
        with pytest.raises(ValueError, match="batch_size"):
            plan_item_migration(_items(2), batch_size=-5)

