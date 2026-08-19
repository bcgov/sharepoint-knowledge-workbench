"""
calendar_provisioning.py
=========================

Purpose:
    Plan provisioning of a working modern SharePoint Online calendar list.

    Encodes a real, validated SPO platform bug: if a calendar list's Start/
    End date fields are declared as site columns (or linked via a content
    type) before the list is created, SPO silently breaks calendar view
    rendering -- the list is created without error, but its calendar view
    never displays events correctly. There is no supported fix once this
    state exists; the list must be recreated.

    The workaround is a specific shape, not a setting: use the Generic List
    template (100), never the Calendar template (106); declare Start/End as
    list-local fields only, never as site columns or content-type-linked
    fields; and create the modern calendar view via a REST call
    (ViewTypeKind=1, ViewType2="MODERNCALENDAR") rather than relying on a
    template-provisioned view.

    ``plan_calendar_list`` makes the mistake structurally unrepresentable:
    a caller-declared ``CalendarListDef`` cannot express "Start/End as site
    columns" without the planner refusing outright (``StartEndScopeViolation``),
    and a valid plan always contains exactly the three required steps.

    THIS IS A WRITE CAPABILITY and is gated identically to
    ``list_provisioning.py`` (same three-gate contract): planning is pure;
    apply is dry-run by default; a real apply requires both an injected
    ``executor`` callable and the plan's own confirmation token.

Layer: sharepoint-provisioning / calendar planning and gated apply

Key Input Dependencies:
    - provisioning_outcomes.Outcome
    - a caller-injected ``executor(step, detail)`` callable for real writes
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence

from provisioning_outcomes import Outcome

Executor = Callable[[str, Mapping[str, Any]], None]

GENERIC_LIST_TEMPLATE = 100
CALENDAR_TEMPLATE = 106  # never used by this module -- see module docstring


class CalendarProvisioningSafetyError(RuntimeError):
    """Base class for every refusal to perform an unsafe write or plan."""


class StartEndScopeViolation(CalendarProvisioningSafetyError):
    """Raised when a caller declares Start/End at site-column scope. This is
    the exact platform-bug trigger this module exists to prevent -- refused
    at plan time, not documented as a warning."""


class ExecutorRequired(CalendarProvisioningSafetyError):
    """Raised when a real apply was requested without an injected executor."""


class ConfirmationRequired(CalendarProvisioningSafetyError):
    """Raised when the confirmation token is missing or does not match the plan."""


@dataclass(frozen=True)
class CalendarListDef:
    """A caller-declared calendar list target.

    ``start_end_site_columns`` exists only so a caller's mistaken intent can
    be detected and refused -- a correct definition never populates it.
    """

    title: str
    description: str = ""
    content_types: Sequence[str] = field(default_factory=tuple)
    start_end_site_columns: Sequence[str] = field(default_factory=tuple)


@dataclass(frozen=True)
class ListCreationStep:
    title: str
    template: int
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"title": self.title, "template": self.template, "description": self.description}


@dataclass(frozen=True)
class ListLocalFieldStep:
    internal_name: str
    field_type: str

    def to_dict(self) -> dict[str, Any]:
        return {"internal_name": self.internal_name, "field_type": self.field_type}


@dataclass(frozen=True)
class ModernViewCreationStep:
    title: str
    view_type_kind: int = 1
    view_type2: str = "MODERNCALENDAR"

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "view_type_kind": self.view_type_kind,
            "view_type2": self.view_type2,
        }


@dataclass(frozen=True)
class CalendarProvisioningPlan:
    """A complete, reviewable description of what a real apply would do.
    Producing a plan performs no writes. Always carries exactly the three
    steps the platform-bug workaround requires -- there is no partial/
    alternate shape a valid plan can take."""

    list_creation: ListCreationStep
    list_local_fields: Sequence[ListLocalFieldStep]
    view_creation: ModernViewCreationStep
    outcome: str = Outcome.OBSERVED

    def _write_items(self) -> list[tuple[str, dict[str, Any]]]:
        items: list[tuple[str, dict[str, Any]]] = [("list_creation", self.list_creation.to_dict())]
        for f in self.list_local_fields:
            items.append(("list_local_field", f.to_dict()))
        items.append(("view_creation", self.view_creation.to_dict()))
        return items

    @property
    def fingerprint(self) -> str:
        digest = hashlib.sha256()
        for step, detail in self._write_items():
            digest.update(step.encode("utf-8"))
            digest.update(b"\0")
            digest.update(repr(sorted(detail.items())).encode("utf-8"))
            digest.update(b"\0")
        return digest.hexdigest()[:16]

    @property
    def confirmation_token(self) -> str:
        return f"APPLY-{len(self._write_items())}-{self.fingerprint}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "outcome": self.outcome,
            "confirmation_token": self.confirmation_token,
            "list_creation": self.list_creation.to_dict(),
            "list_local_fields": [f.to_dict() for f in self.list_local_fields],
            "view_creation": self.view_creation.to_dict(),
        }


@dataclass(frozen=True)
class CalendarProvisioningResult:
    """Evidence record for one apply attempt."""

    outcome: str
    dry_run: bool
    executed: Sequence[tuple[str, dict[str, Any]]] = field(default_factory=tuple)
    failed: Sequence[tuple[str, str]] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "outcome": self.outcome,
            "dry_run": self.dry_run,
            "executed": [{"step": step, "detail": detail} for step, detail in self.executed],
            "failed": [{"step": step, "error": error} for step, error in self.failed],
        }


def plan_calendar_list(list_def: CalendarListDef) -> CalendarProvisioningPlan:
    """Plan provisioning of one working modern calendar list. Never writes
    anything. Refuses outright if the caller declares Start/End at
    site-column scope -- the exact trigger for the platform bug this module
    exists to prevent."""
    if list_def.start_end_site_columns:
        raise StartEndScopeViolation(
            f"'{list_def.title}': Start/End must never be declared as site columns "
            f"(got {list(list_def.start_end_site_columns)!r}) -- this silently breaks "
            "calendar view rendering in SPO. Declare them as list-local fields only."
        )

    return CalendarProvisioningPlan(
        list_creation=ListCreationStep(
            title=list_def.title,
            template=GENERIC_LIST_TEMPLATE,
            description=list_def.description,
        ),
        list_local_fields=(
            ListLocalFieldStep(internal_name="Start", field_type="DateTime"),
            ListLocalFieldStep(internal_name="End", field_type="DateTime"),
        ),
        view_creation=ModernViewCreationStep(title=list_def.title),
        outcome=Outcome.OBSERVED,
    )


def _gate(plan: CalendarProvisioningPlan, executor: Executor | None, confirm: str | None) -> None:
    if executor is None:
        raise ExecutorRequired(
            "a real write requires an explicitly injected executor(step, detail) callable; "
            "this module ships no transport and will not write autonomously"
        )
    expected = plan.confirmation_token
    if confirm != expected:
        raise ConfirmationRequired(
            f"confirmation token does not authorise this plan; expected {expected!r}"
        )


def apply_calendar_list(
    plan: CalendarProvisioningPlan,
    *,
    executor: Executor | None = None,
    dry_run: bool = True,
    confirm: str | None = None,
) -> CalendarProvisioningResult:
    """Apply a plan. DRY RUN BY DEFAULT -- ``dry_run=False`` additionally
    requires an injected ``executor`` and ``plan.confirmation_token``."""
    items = plan._write_items()

    if dry_run:
        return CalendarProvisioningResult(outcome=Outcome.OBSERVED, dry_run=True, executed=())

    _gate(plan, executor, confirm)

    executed: list[tuple[str, dict[str, Any]]] = []
    failed: list[tuple[str, str]] = []
    forbidden = False

    for step, detail in items:
        try:
            executor(step, detail)  # type: ignore[misc]
        except PermissionError as exc:
            forbidden = True
            failed.append((step, f"forbidden: {exc}"))
        except Exception as exc:  # noqa: BLE001 -- caller-supplied sink, any error is reportable
            failed.append((step, str(exc)))
        else:
            executed.append((step, detail))

    if not executed and forbidden:
        outcome = Outcome.FORBIDDEN
    elif not executed and failed:
        outcome = Outcome.FAILED
    elif failed:
        outcome = Outcome.PARTIAL
    else:
        outcome = Outcome.OBSERVED

    return CalendarProvisioningResult(
        outcome=outcome, dry_run=False, executed=tuple(executed), failed=tuple(failed)
    )
