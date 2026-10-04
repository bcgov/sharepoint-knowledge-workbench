"""
list_provisioning.py
=====================

Purpose:
    Reconcile-not-recreate SharePoint list/library provisioning from a
    caller-supplied declarative schema plus a caller-supplied observation of
    current live state -- no tenant I/O of any kind. Aggregates field and
    content-type provisioning plans (see ``field_provisioning`` and
    ``content_type_provisioning``) together with list-level create/delete
    planning into one reviewable ``ProvisioningPlan``.

    Duplicate-titled lists are detected and reported as a *blocking finding*
    before any deletion step is planned -- ported from a real source
    incident where a stray duplicate-titled list caused identity resolution
    to silently pick the wrong one. A plan with blocking findings can never
    be executed, even with an otherwise-valid confirmation token.

    THIS IS A WRITE CAPABILITY and is gated exactly like
    sharepoint-site-migration's ``update-page-links`` (Phase 9 spec s13):

      * planning is pure -- ``plan_provisioning`` never writes anything;
      * ``apply_provisioning`` is DRY-RUN BY DEFAULT;
      * a real apply requires BOTH an explicitly injected ``executor``
        callable (this module ships no transport, no client, no
        credentials) AND the exact confirmation token generated for that
        specific plan, which goes stale the moment the plan's source data
        changes;
      * per-step failures are reported honestly (Partial / Failed /
        Forbidden), never collapsed into an empty success;
      * ``verify_deletion_complete`` fails loud if an object unexpectedly
        still exists after a delete step, rather than assuming success.

Layer: sharepoint-site-build-and-publish / list planning and gated apply

Key Input Dependencies:
    - field_provisioning.FieldDef / plan_field_action
    - content_type_provisioning.ContentTypeDef / plan_content_type /
      plan_add_content_type_to_list
    - a caller-injected ``executor(step, detail)`` callable for real writes
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence

from content_type_provisioning import (
    ContentTypeAction,
    ContentTypeDef,
    ContentTypeState,
    plan_add_content_type_to_list,
    plan_content_type,
)
from field_provisioning import FieldAction, FieldDef, plan_field_action
from provisioning_outcomes import Outcome

Executor = Callable[[str, Mapping[str, Any]], None]


class ProvisioningSafetyError(RuntimeError):
    """Base class for every refusal to perform an unsafe write."""


class ExecutorRequired(ProvisioningSafetyError):
    """Raised when a real apply was requested without an injected executor."""


class ConfirmationRequired(ProvisioningSafetyError):
    """Raised when the confirmation token is missing or does not match the plan."""


class DuplicateListsBlockProvisioning(ProvisioningSafetyError):
    """Raised when a plan carries blocking duplicate-list findings. A plan in
    this state can never be executed, regardless of confirmation token."""


class DeletionVerificationFailed(RuntimeError):
    """Raised when an object expected to be gone after a delete step is
    still observed to exist -- fail loud, never silently assume success."""


@dataclass(frozen=True)
class ListDef:
    """A caller-declared list/library target. ``recreate=True`` opts a list
    into delete-and-recreate semantics; without it, an existing list is left
    entirely untouched by this plugin (create-if-missing only)."""

    title: str
    template: int = 100
    description: str = ""
    content_types: Sequence[str] = field(default_factory=tuple)
    recreate: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "template": self.template,
            "description": self.description,
            "content_types": list(self.content_types),
            "recreate": self.recreate,
        }


@dataclass(frozen=True)
class ListState:
    """Caller-supplied observation of a list's current live state.
    ``matching_count`` is the number of live objects sharing this exact
    title -- deliberately not a single Get-...-Identity lookup, which can
    silently resolve to the wrong object when duplicates exist."""

    title: str
    exists: bool
    matching_count: int = 0
    content_types: Sequence[str] = field(default_factory=tuple)


@dataclass(frozen=True)
class ProvisioningSchema:
    """A complete, caller-supplied declarative schema. Every column, content
    type, and target object comes from here -- nothing is hardcoded."""

    site_fields: Sequence[FieldDef] = field(default_factory=tuple)
    content_types: Sequence[ContentTypeDef] = field(default_factory=tuple)
    lists: Sequence[ListDef] = field(default_factory=tuple)


@dataclass(frozen=True)
class CurrentState:
    """Caller-supplied observation of live tenant state. This module reads
    it, never fetches it -- collecting it is the caller's (or a future,
    separately gated collection plugin's) responsibility."""

    site_fields: Mapping[str, str] = field(default_factory=dict)  # internal_name -> current type
    content_types: Mapping[str, ContentTypeState] = field(default_factory=dict)
    lists: Mapping[str, ListState] = field(default_factory=dict)


@dataclass(frozen=True)
class ListCreation:
    title: str
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {"title": self.title, "detail": self.detail}


@dataclass(frozen=True)
class ListDeletion:
    title: str
    reason: str
    blocking: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {"title": self.title, "reason": self.reason, "blocking": self.blocking}


def detect_duplicate_lists(schema: ProvisioningSchema, current: CurrentState) -> list[str]:
    """Detect, for every list declared with ``recreate=True``, whether more
    than one live object currently shares that exact title. Returns a
    human-readable finding per duplicate -- callers must not proceed to
    deletion planning for a flagged title without investigating first."""
    findings: list[str] = []
    for list_def in schema.lists:
        if not list_def.recreate:
            continue
        state = current.lists.get(list_def.title)
        if state and state.matching_count > 1:
            findings.append(
                f"DUPLICATE TITLE: {state.matching_count} live objects named "
                f"'{list_def.title}' -- resolve before any delete/recreate"
            )
    return findings


@dataclass(frozen=True)
class ProvisioningPlan:
    """A complete, reviewable description of what a real apply would do.
    Producing a plan performs no writes."""

    field_actions: Sequence[FieldAction] = field(default_factory=tuple)
    content_type_actions: Sequence[ContentTypeAction] = field(default_factory=tuple)
    list_creations: Sequence[ListCreation] = field(default_factory=tuple)
    list_deletions: Sequence[ListDeletion] = field(default_factory=tuple)
    blocking_findings: Sequence[str] = field(default_factory=tuple)
    outcome: str = Outcome.EMPTY

    def _write_items(self) -> list[tuple[str, dict[str, Any]]]:
        items: list[tuple[str, dict[str, Any]]] = []
        for action in self.field_actions:
            if action.action in ("create", "repair"):
                items.append(("field", action.to_dict()))
        for action in self.content_type_actions:
            if not action.already_correct:
                items.append(("content_type", action.to_dict()))
        for creation in self.list_creations:
            items.append(("list_creation", creation.to_dict()))
        for deletion in self.list_deletions:
            items.append(("list_deletion", deletion.to_dict()))
        return items

    @property
    def has_writes(self) -> bool:
        return bool(self._write_items())

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
            "field_actions": [a.to_dict() for a in self.field_actions],
            "content_type_actions": [a.to_dict() for a in self.content_type_actions],
            "list_creations": [c.to_dict() for c in self.list_creations],
            "list_deletions": [d.to_dict() for d in self.list_deletions],
            "blocking_findings": list(self.blocking_findings),
        }


@dataclass(frozen=True)
class ProvisioningResult:
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


def plan_provisioning(schema: ProvisioningSchema, current: CurrentState) -> ProvisioningPlan:
    """Reconcile a declarative schema against a caller-supplied observation
    of current state. Never writes anything."""
    field_actions = tuple(
        plan_field_action(fd, existing_type=current.site_fields.get(fd.internal_name))
        for fd in schema.site_fields
    )

    content_type_actions: list[ContentTypeAction] = []
    for ct_def in schema.content_types:
        content_type_actions.extend(plan_content_type(ct_def, current.content_types.get(ct_def.name)))

    blocking_findings = tuple(detect_duplicate_lists(schema, current))
    blocked_titles = {
        finding.split("'")[1] for finding in blocking_findings
    }  # extract the quoted title

    list_creations: list[ListCreation] = []
    list_deletions: list[ListDeletion] = []
    for list_def in schema.lists:
        state = current.lists.get(list_def.title)
        exists = bool(state and state.exists)

        if list_def.title in blocked_titles:
            continue

        if not exists:
            list_creations.append(
                ListCreation(list_def.title, f"create '{list_def.title}' (template {list_def.template})")
            )
        elif list_def.recreate:
            list_deletions.append(
                ListDeletion(list_def.title, f"delete '{list_def.title}' for recreate", blocking=False)
            )
            list_creations.append(
                ListCreation(list_def.title, f"recreate '{list_def.title}' (template {list_def.template})")
            )

    has_content = bool(field_actions or content_type_actions or list_creations or list_deletions)
    if blocking_findings:
        outcome = Outcome.FAILED
    elif has_content:
        outcome = Outcome.OBSERVED
    else:
        outcome = Outcome.EMPTY

    return ProvisioningPlan(
        field_actions=field_actions,
        content_type_actions=tuple(content_type_actions),
        list_creations=tuple(list_creations),
        list_deletions=tuple(list_deletions),
        blocking_findings=blocking_findings,
        outcome=outcome,
    )


def _gate(plan: ProvisioningPlan, executor: Executor | None, confirm: str | None) -> None:
    if plan.blocking_findings:
        raise DuplicateListsBlockProvisioning(
            "plan carries blocking findings (e.g. duplicate-titled lists) and "
            "can never be executed until they are resolved: "
            + "; ".join(plan.blocking_findings)
        )
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


def apply_provisioning(
    plan: ProvisioningPlan,
    *,
    executor: Executor | None = None,
    dry_run: bool = True,
    confirm: str | None = None,
) -> ProvisioningResult:
    """Apply a plan. DRY RUN BY DEFAULT -- ``dry_run=False`` additionally
    requires an injected ``executor`` and ``plan.confirmation_token``, and
    unconditionally refuses if the plan carries blocking findings."""
    items = plan._write_items()

    if dry_run:
        return ProvisioningResult(
            outcome=Outcome.OBSERVED if items else Outcome.EMPTY,
            dry_run=True,
            executed=(),
        )

    _gate(plan, executor, confirm)

    if not items:
        return ProvisioningResult(outcome=Outcome.EMPTY, dry_run=False)

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

    return ProvisioningResult(outcome=outcome, dry_run=False, executed=tuple(executed), failed=tuple(failed))


def verify_deletion_complete(title: str, *, still_exists: bool) -> None:
    """Fail loud if an object expected to be gone after a delete step is
    still observed to exist. Callers must invoke this with a fresh
    post-delete observation -- this function does not check anything
    itself, it only enforces the honest-outcome contract."""
    if still_exists:
        raise DeletionVerificationFailed(
            f"'{title}' still exists after a delete step -- investigate before proceeding; "
            "never assume a delete succeeded without verifying it"
        )
