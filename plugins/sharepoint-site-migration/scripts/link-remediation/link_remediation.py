"""
link_remediation.py
===================

Purpose:
    Rewrites legacy URLs embedded in page body content to their new locations,
    driven entirely by a caller-supplied rewrite ruleset.

    THIS IS A WRITE CAPABILITY and is gated accordingly (Phase 9 spec s13):

      * planning is pure -- ``plan_remediation`` never writes anything;
      * ``apply_remediation`` is DRY-RUN BY DEFAULT;
      * a real apply requires BOTH an explicitly injected ``writer`` callable
        (this module ships no transport, no client, no credentials) AND the
        exact confirmation token generated for that specific plan;
      * every plan retains the original content so ``rollback_remediation``
        can restore it under the same gates;
      * per-document failures are reported honestly (Partial / Failed /
        Forbidden), never collapsed into an empty success.

Layer: sharepoint-site-migration / remediation

Key Input Dependencies:
    - link_rules.RewriteRuleset (caller-supplied)
    - a caller-injected ``writer(source, content)`` callable for real writes

Usage:
    plan = plan_remediation(documents, ruleset)
    preview = apply_remediation(plan)                       # dry run, no writes
    result = apply_remediation(plan, writer=my_writer,
                               dry_run=False,
                               confirm=plan.confirmation_token)

Function Index:
    RemediationChange.to_dict, DocumentRemediation.is_changed,
    DocumentRemediation.to_dict, RemediationPlan.changed_documents,
    RemediationPlan.change_count, RemediationPlan.fingerprint,
    RemediationPlan.confirmation_token, RemediationPlan.rollback_token,
    RemediationPlan.to_dict, RemediationResult.to_dict, plan_remediation,
    _write_each, _gate, apply_remediation, rollback_remediation
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence

from link_outcomes import Outcome
from link_rules import RewriteRuleset

Writer = Callable[[str, str], None]


class RemediationSafetyError(RuntimeError):
    """Base class for every refusal to perform an unsafe write."""


class WriterRequired(RemediationSafetyError):
    """Raised when a real apply was requested without an injected writer."""


class ConfirmationRequired(RemediationSafetyError):
    """Raised when the confirmation token is missing or does not match the plan."""


@dataclass(frozen=True)
class RemediationChange:
    """One rule application against one document."""

    source: str
    rule_match: str
    rule_replacement: str

    def to_dict(self) -> dict[str, str]:
        """Serialize a rule application without including document content."""
        return {
            "source": self.source,
            "rule_match": self.rule_match,
            "rule_replacement": self.rule_replacement,
        }


@dataclass(frozen=True)
class DocumentRemediation:
    """The planned before/after state of one document."""

    source: str
    original_content: str
    remediated_content: str
    changes: Sequence[RemediationChange] = field(default_factory=tuple)

    @property
    def is_changed(self) -> bool:
        """Indicate whether one or more rules changed the document."""
        return bool(self.changes)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the document identity and applied rules."""
        return {
            "source": self.source,
            "changed": self.is_changed,
            "changes": [change.to_dict() for change in self.changes],
        }


@dataclass(frozen=True)
class RemediationPlan:
    """A complete, reviewable description of what a real apply would do.

    Producing a plan performs no writes. The plan's confirmation and rollback
    tokens are derived from its exact contents, so a token issued for one plan
    can never authorise a different (e.g. wider) one.
    """

    documents: Sequence[DocumentRemediation] = field(default_factory=tuple)
    problems: Sequence[str] = field(default_factory=tuple)
    outcome: str = Outcome.EMPTY

    @property
    def changed_documents(self) -> list[DocumentRemediation]:
        """Return only documents with a changed body."""
        return [document for document in self.documents if document.is_changed]

    @property
    def change_count(self) -> int:
        """Count documents the plan would write."""
        return len(self.changed_documents)

    @property
    def fingerprint(self) -> str:
        """Hash changed document names and content for authorization binding."""
        digest = hashlib.sha256()
        for document in self.changed_documents:
            digest.update(document.source.encode("utf-8"))
            digest.update(b"\0")
            digest.update(document.remediated_content.encode("utf-8"))
            digest.update(b"\0")
        return digest.hexdigest()[:16]

    @property
    def confirmation_token(self) -> str:
        """Create the plan-specific apply authorization token."""
        return f"APPLY-{self.change_count}-{self.fingerprint}"

    @property
    def rollback_token(self) -> str:
        """Create a distinct token for restoring this plan's original content."""
        return f"ROLLBACK-{self.change_count}-{self.fingerprint}"

    def to_dict(self) -> dict[str, Any]:
        """Serialize the full plan and both write-gate tokens."""
        return {
            "outcome": self.outcome,
            "change_count": self.change_count,
            "confirmation_token": self.confirmation_token,
            "rollback_token": self.rollback_token,
            "documents": [document.to_dict() for document in self.documents],
            "problems": list(self.problems),
        }


@dataclass(frozen=True)
class RemediationResult:
    """Evidence record for one apply or rollback attempt."""

    outcome: str
    dry_run: bool
    applied: Sequence[str] = field(default_factory=list)
    failed: Sequence[tuple[str, str]] = field(default_factory=list)
    skipped: Sequence[str] = field(default_factory=list)
    would_change: Sequence[str] = field(default_factory=list)
    changes: Sequence[RemediationChange] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        """Serialize apply or rollback results and per-document failures."""
        return {
            "outcome": self.outcome,
            "dry_run": self.dry_run,
            "applied": list(self.applied),
            "failed": [{"source": source, "error": error} for source, error in self.failed],
            "skipped": list(self.skipped),
            "would_change": list(self.would_change),
            "changes": [change.to_dict() for change in self.changes],
        }


def plan_remediation(documents: Mapping[str, str], ruleset: RewriteRuleset) -> RemediationPlan:
    """Compute, without writing anything, what remediation would change.

    ``documents`` maps a caller-defined document identifier (page name, item id,
    file path -- this module does not care) to its current body content.
    """
    planned: list[DocumentRemediation] = []
    problems: list[str] = []

    for source, content in documents.items():
        if not content:
            problems.append(f"no content to scan: {source}")
            continue
        remediated, applied_rules = ruleset.apply(content)
        changes = tuple(
            RemediationChange(source=source, rule_match=rule.match, rule_replacement=rule.replacement)
            for rule in applied_rules
        )
        planned.append(
            DocumentRemediation(
                source=source,
                original_content=content,
                remediated_content=remediated,
                changes=changes,
            )
        )

    changed = any(document.is_changed for document in planned)
    if problems and planned:
        outcome = Outcome.PARTIAL
    elif problems:
        outcome = Outcome.FAILED
    elif changed:
        outcome = Outcome.OBSERVED
    else:
        outcome = Outcome.EMPTY

    return RemediationPlan(documents=tuple(planned), problems=tuple(problems), outcome=outcome)


def _write_each(
    targets: Sequence[tuple[str, str]],
    writer: Writer,
    *,
    changes: Sequence[RemediationChange],
    skipped: Sequence[str],
) -> RemediationResult:
    """Write targets independently and classify partial or complete failures."""
    applied: list[str] = []
    failed: list[tuple[str, str]] = []
    forbidden = False

    for source, content in targets:
        try:
            writer(source, content)
        except PermissionError as exc:
            forbidden = True
            failed.append((source, f"forbidden: {exc}"))
        except Exception as exc:  # noqa: BLE001 -- caller-supplied sink, any error is reportable
            failed.append((source, str(exc)))
        else:
            applied.append(source)

    if not applied and forbidden:
        outcome = Outcome.FORBIDDEN
    elif not applied and failed:
        outcome = Outcome.FAILED
    elif failed:
        outcome = Outcome.PARTIAL
    else:
        outcome = Outcome.OBSERVED

    return RemediationResult(
        outcome=outcome,
        dry_run=False,
        applied=list(applied),
        failed=list(failed),
        skipped=list(skipped),
        changes=tuple(changes),
    )


def _gate(plan: RemediationPlan, writer: Writer | None, confirm: str | None, expected: str) -> None:
    """Require an injected writer and the expected plan-bound token."""
    if writer is None:
        raise WriterRequired(
            "a real write requires an explicitly injected writer(source, content) callable; "
            "this module ships no transport and will not write autonomously"
        )
    if confirm != expected:
        raise ConfirmationRequired(
            f"confirmation token does not authorise this plan; expected {expected!r}"
        )


def apply_remediation(
    plan: RemediationPlan,
    *,
    writer: Writer | None = None,
    dry_run: bool = True,
    confirm: str | None = None,
) -> RemediationResult:
    """Apply a plan. DRY RUN BY DEFAULT -- ``dry_run=False`` additionally
    requires an injected ``writer`` and ``plan.confirmation_token``."""
    changed = plan.changed_documents
    unchanged = tuple(document.source for document in plan.documents if not document.is_changed)
    all_changes = tuple(change for document in changed for change in document.changes)

    if dry_run:
        return RemediationResult(
            outcome=Outcome.OBSERVED if changed else Outcome.EMPTY,
            dry_run=True,
            skipped=unchanged,
            would_change=tuple(document.source for document in changed),
            changes=all_changes,
        )

    _gate(plan, writer, confirm, plan.confirmation_token)

    if not changed:
        return RemediationResult(outcome=Outcome.EMPTY, dry_run=False, skipped=unchanged)

    return _write_each(
        [(document.source, document.remediated_content) for document in changed],
        writer,
        changes=all_changes,
        skipped=unchanged,
    )


def rollback_remediation(
    plan: RemediationPlan,
    *,
    writer: Writer | None = None,
    confirm: str | None = None,
) -> RemediationResult:
    """Restore every document this plan changed to its original content.
    Requires an injected writer and ``plan.rollback_token`` -- the apply token
    is deliberately not accepted."""
    changed = plan.changed_documents
    unchanged = tuple(document.source for document in plan.documents if not document.is_changed)

    _gate(plan, writer, confirm, plan.rollback_token)

    if not changed:
        return RemediationResult(outcome=Outcome.EMPTY, dry_run=False, skipped=unchanged)

    return _write_each(
        [(document.source, document.original_content) for document in changed],
        writer,
        changes=(),
        skipped=unchanged,
    )
