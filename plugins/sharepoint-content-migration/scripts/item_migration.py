"""
item_migration.py
====================

Purpose:
    Plan and (gated) apply item-level, batched content migration with
    retry. Pure planning (``plan_item_migration``) groups a caller-supplied
    sequence of items into fixed-size batches; ``apply_item_migration``
    executes each item through a caller-injected ``executor`` (source
    item -> destination item ID), retrying a transient failure up to a
    configurable limit before recording it as failed.

    THIS IS A WRITE CAPABILITY and is gated identically to every other
    write-capable module in this workbench (``list_provisioning.py``,
    ``link_remediation.py``, ``calendar_provisioning.py``): planning is
    pure; apply is dry-run by default; a real apply requires both an
    explicitly injected ``executor`` and the plan's own confirmation token.

    Deliberately excludes: field-type-aware skip lists, per-source-schema
    lookup/calendar field renaming, and manifest/matrix-driven list
    resolution -- those are all specific to one source schema's own field
    catalog and matrix format. This module only migrates whatever
    caller-supplied ``fields`` dict each ``MigrationItem`` already carries;
    shaping the source record into that dict is the caller's job.

Layer: sharepoint-content-migration / item-level migration mechanism

Key Input Dependencies:
    - provisioning_outcomes.Outcome (reused from sharepoint-provisioning)
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence

from provisioning_outcomes import Outcome

Executor = Callable[["MigrationItem"], int]  # returns the new destination item ID


class ItemMigrationSafetyError(RuntimeError):
    """Base class for every refusal to perform an unsafe write."""


class ExecutorRequired(ItemMigrationSafetyError):
    """Raised when a real apply was requested without an injected executor."""


class ConfirmationRequired(ItemMigrationSafetyError):
    """Raised when the confirmation token is missing or does not match the plan."""


@dataclass(frozen=True)
class MigrationItem:
    """A single caller-shaped source item ready to migrate. ``fields`` is
    already in destination-field-name form -- this module has no schema
    knowledge and performs no field renaming."""

    source_id: int
    fields: Mapping[str, Any]


@dataclass(frozen=True)
class ItemMigrationPlan:
    """A complete, reviewable batching plan. Producing a plan performs no
    writes."""

    batches: tuple[tuple[MigrationItem, ...], ...]
    outcome: str = Outcome.EMPTY

    @property
    def all_items(self) -> tuple[MigrationItem, ...]:
        return tuple(item for batch in self.batches for item in batch)

    @property
    def fingerprint(self) -> str:
        digest = hashlib.sha256()
        for batch in self.batches:
            digest.update(b"batch\0")
            for item in batch:
                digest.update(str(item.source_id).encode("utf-8"))
                digest.update(b"\0")
                digest.update(repr(sorted(item.fields.items())).encode("utf-8"))
                digest.update(b"\0")
        return digest.hexdigest()[:16]

    @property
    def confirmation_token(self) -> str:
        return f"APPLY-{len(self.all_items)}-{len(self.batches)}-{self.fingerprint}"


@dataclass(frozen=True)
class ItemMigrationResult:
    """Evidence record for one apply attempt. ``migrated`` is a sequence of
    ``(source_id, dest_id)`` pairs -- the raw material for
    ``id_mapping.record_id_mapping`` -- never just a success count."""

    outcome: str
    dry_run: bool
    migrated: Sequence[tuple[int, int]] = field(default_factory=tuple)
    failed: Sequence[tuple[int, str]] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "outcome": self.outcome,
            "dry_run": self.dry_run,
            "migrated": [{"source_id": s, "dest_id": d} for s, d in self.migrated],
            "failed": [{"source_id": s, "error": e} for s, e in self.failed],
        }


def plan_item_migration(items: Sequence[MigrationItem], *, batch_size: int) -> ItemMigrationPlan:
    """Group ``items`` into fixed-size batches. Never writes anything."""
    if not items:
        return ItemMigrationPlan(batches=(), outcome=Outcome.EMPTY)

    batches = tuple(
        tuple(items[i : i + batch_size]) for i in range(0, len(items), batch_size)
    )
    return ItemMigrationPlan(batches=batches, outcome=Outcome.OBSERVED)


def _gate(plan: ItemMigrationPlan, executor: Executor | None, confirm: str | None) -> None:
    if executor is None:
        raise ExecutorRequired(
            "a real write requires an explicitly injected executor(item) -> dest_id callable; "
            "this module ships no transport and will not write autonomously"
        )
    expected = plan.confirmation_token
    if confirm != expected:
        raise ConfirmationRequired(
            f"confirmation token does not authorise this plan; expected {expected!r}"
        )


def apply_item_migration(
    plan: ItemMigrationPlan,
    *,
    executor: Executor | None = None,
    dry_run: bool = True,
    confirm: str | None = None,
    retry_attempts: int = 1,
) -> ItemMigrationResult:
    """Apply a plan. DRY RUN BY DEFAULT -- ``dry_run=False`` additionally
    requires an injected ``executor`` and ``plan.confirmation_token``. Each
    item gets ``retry_attempts`` total attempts before being recorded as
    failed -- a transient failure (e.g. a throttled request) does not lose
    the item, but a permanent failure is reported honestly, never silently
    dropped or retried forever.

    ``retry_attempts`` must be at least 1: with 0, the attempt loop never
    runs, so an item lands in neither ``migrated`` nor ``failed`` and the
    result would misreport ``OBSERVED`` with every item silently dropped --
    this is rejected outright rather than allowed to produce that result."""
    if retry_attempts < 1:
        raise ValueError(f"retry_attempts must be >= 1, got {retry_attempts}")

    items = plan.all_items

    if dry_run:
        return ItemMigrationResult(outcome=Outcome.OBSERVED if items else Outcome.EMPTY, dry_run=True)

    _gate(plan, executor, confirm)

    if not items:
        return ItemMigrationResult(outcome=Outcome.EMPTY, dry_run=False)

    migrated: list[tuple[int, int]] = []
    failed: list[tuple[int, str]] = []

    for item in items:
        last_error: Exception | None = None
        for _attempt in range(retry_attempts):
            try:
                dest_id = executor(item)  # type: ignore[misc]
            except Exception as exc:  # noqa: BLE001 -- caller-supplied sink, any error is reportable
                last_error = exc
                continue
            else:
                migrated.append((item.source_id, dest_id))
                last_error = None
                break
        if last_error is not None:
            failed.append((item.source_id, str(last_error)))

    if not migrated and failed:
        outcome = Outcome.FAILED
    elif failed:
        outcome = Outcome.PARTIAL
    else:
        outcome = Outcome.OBSERVED

    return ItemMigrationResult(
        outcome=outcome, dry_run=False, migrated=tuple(migrated), failed=tuple(failed)
    )
