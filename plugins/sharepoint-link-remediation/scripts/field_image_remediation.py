"""
field_image_remediation.py
=============================

Purpose:
    Inventory-verified remediation of an embedded ``<img>`` reference
    inside a rich-text list field (e.g. a "Picture or Description" column),
    distinct from both ``link_remediation.py`` (blind rule-based rewrite of
    page-body links) and ``document_link_remediation.py`` (Office/PDF file
    content): a rewrite is proposed for an item's embedded image reference
    ONLY when the referenced filename is confirmed present in a real
    document-library inventory -- never a blind regex guess. An item whose
    referenced file is genuinely absent, or whose ``<img>`` tag has no
    ``src`` at all (an empty broken-image placeholder), is classified and
    reported, never silently rewritten or dropped.

    This is the field-content-migration counterpart to a library move/
    rename: content authored under one library path (e.g. a legacy
    publishing-images library) still resolves correctly after the files
    move to a new library, PROVIDED the embedded reference is rewritten to
    match -- but only for files that actually made the move. Rewriting
    blindly (as ``link_remediation.py`` does for page bodies, where the
    target is assumed to always exist post-migration) would silently
    "fix" a reference to a file that was never migrated, hiding a real
    data-loss problem behind an apparently successful rewrite.

    THIS IS A WRITE CAPABILITY and is gated identically to every other
    write-capable module in this plugin: planning is pure; apply is
    dry-run by default; a real apply requires both an explicitly injected
    ``executor`` and the plan's own confirmation token.

Layer: sharepoint-link-remediation / field-content remediation

Key Input Dependencies:
    - link_outcomes.Outcome (shared honest-outcome vocabulary)
    - link_rules.RewriteRuleset (caller-supplied path-segment rewrite rule)
    - a caller-injected ``executor(source_id, new_field_value)`` callable
      for real writes
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

from link_outcomes import Outcome
from link_rules import RewriteRuleset
from urllib.parse import unquote

Executor = Callable[[str, str], None]

_IMG_SRC_PATTERN = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)
_IMG_TAG_PATTERN = re.compile(r"<img[^>]*>", re.IGNORECASE)


class FieldImageRemediationSafetyError(RuntimeError):
    """Base class for every refusal to perform an unsafe write."""


class ExecutorRequired(FieldImageRemediationSafetyError):
    """Raised when a real apply was requested without an injected executor."""


class ConfirmationRequired(FieldImageRemediationSafetyError):
    """Raised when the confirmation token is missing or does not match the plan."""


@dataclass(frozen=True)
class ImageReferenceClassification:
    """The classification of one item's embedded image reference.

    ``status`` is one of:
      - ``"no_img_tag"``   -- the field has no ``<img>`` tag at all
      - ``"img_no_src"``   -- an ``<img>`` tag with no ``src`` attribute
                              (an empty broken-image placeholder -- no path
                              to fix, distinct from a genuinely missing file)
      - ``"matched"``      -- the referenced filename exists in the
                              inventory (fix = rewrite the path segment)
      - ``"missing"``      -- the referenced filename does not exist
                              anywhere in the inventory (genuinely absent)
    """

    status: str
    original_src: str = ""
    extracted_filename: str = ""
    matched_relative_url: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "status": self.status,
            "original_src": self.original_src,
            "extracted_filename": self.extracted_filename,
            "matched_relative_url": self.matched_relative_url,
        }


def _extract_img_src(field_value: str) -> str | None:
    match = _IMG_SRC_PATTERN.search(field_value)
    return match.group(1) if match else None


def _has_img_tag(field_value: str) -> bool:
    return bool(_IMG_TAG_PATTERN.search(field_value))


def _extract_filename(src: str) -> str:
    return unquote(src).rsplit("/", 1)[-1]


def classify_field_images(
    items: Mapping[str, str], *, inventory: Mapping[str, str]
) -> dict[str, ImageReferenceClassification]:
    """Classify every item's embedded image reference against ``inventory``
    (a filename-lowercased-to-RelativeUrl lookup, e.g. produced by a
    document-library export). Pure -- no I/O."""
    classifications: dict[str, ImageReferenceClassification] = {}

    for source_id, field_value in items.items():
        src = _extract_img_src(field_value or "")

        if src is None:
            status = "img_no_src" if _has_img_tag(field_value or "") else "no_img_tag"
            classifications[source_id] = ImageReferenceClassification(status=status)
            continue

        filename = _extract_filename(src)
        matched_url = inventory.get(filename.lower())
        classifications[source_id] = ImageReferenceClassification(
            status="matched" if matched_url else "missing",
            original_src=src,
            extracted_filename=filename,
            matched_relative_url=matched_url or "",
        )

    return classifications


@dataclass(frozen=True)
class FieldImageFix:
    """One proposed field-value rewrite for a confirmed-matched item."""

    source_id: str
    original_field_value: str
    new_field_value: str

    def to_dict(self) -> dict[str, str]:
        return {
            "source_id": self.source_id,
            "original_field_value": self.original_field_value,
            "new_field_value": self.new_field_value,
        }


@dataclass(frozen=True)
class FieldImageRemediationPlan:
    """A complete, reviewable description of what a real apply would do.
    ``classifications`` covers every item, including ones with no proposed
    fix -- never drop a missing/broken item from the record just because
    there is nothing to write."""

    classifications: Mapping[str, ImageReferenceClassification] = field(default_factory=dict)
    changed_items: tuple[FieldImageFix, ...] = ()
    outcome: str = Outcome.EMPTY

    @property
    def change_count(self) -> int:
        return len(self.changed_items)

    @property
    def fingerprint(self) -> str:
        digest = hashlib.sha256()
        for fix in self.changed_items:
            digest.update(fix.source_id.encode("utf-8"))
            digest.update(b"\0")
            digest.update(fix.new_field_value.encode("utf-8"))
            digest.update(b"\0")
        return digest.hexdigest()[:16]

    @property
    def confirmation_token(self) -> str:
        return f"APPLY-{self.change_count}-{self.fingerprint}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "outcome": self.outcome,
            "change_count": self.change_count,
            "confirmation_token": self.confirmation_token,
            "classifications": {k: v.to_dict() for k, v in self.classifications.items()},
            "changed_items": [f.to_dict() for f in self.changed_items],
        }


@dataclass(frozen=True)
class FieldImageRemediationResult:
    """Evidence record for one apply attempt."""

    outcome: str
    dry_run: bool
    applied: tuple[str, ...] = ()
    failed: tuple[tuple[str, str], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "outcome": self.outcome,
            "dry_run": self.dry_run,
            "applied": list(self.applied),
            "failed": [{"source_id": s, "error": e} for s, e in self.failed],
        }


def plan_field_image_remediation(
    items: Mapping[str, str], *, inventory: Mapping[str, str], ruleset: RewriteRuleset
) -> FieldImageRemediationPlan:
    """Classify every item, then propose a rewrite ONLY for items
    classified ``matched`` -- ``missing`` and ``img_no_src`` items are
    recorded in ``classifications`` but never get a proposed fix. Never
    writes anything."""
    if not items:
        return FieldImageRemediationPlan(classifications={}, changed_items=(), outcome=Outcome.EMPTY)

    classifications = classify_field_images(items, inventory=inventory)

    fixes: list[FieldImageFix] = []
    for source_id, classification in classifications.items():
        if classification.status != "matched":
            continue
        original_value = items[source_id]
        new_value, applied_rules = ruleset.apply(original_value)
        if applied_rules:
            fixes.append(
                FieldImageFix(
                    source_id=source_id, original_field_value=original_value, new_field_value=new_value
                )
            )

    outcome = Outcome.OBSERVED if fixes else Outcome.EMPTY
    return FieldImageRemediationPlan(
        classifications=classifications, changed_items=tuple(fixes), outcome=outcome
    )


def _gate(plan: FieldImageRemediationPlan, executor: Executor | None, confirm: str | None) -> None:
    if executor is None:
        raise ExecutorRequired(
            "a real write requires an explicitly injected executor(source_id, new_field_value) "
            "callable; this module ships no transport and will not write autonomously"
        )
    expected = plan.confirmation_token
    if confirm != expected:
        raise ConfirmationRequired(
            f"confirmation token does not authorise this plan; expected {expected!r}"
        )


def apply_field_image_remediation(
    plan: FieldImageRemediationPlan,
    *,
    executor: Executor | None = None,
    dry_run: bool = True,
    confirm: str | None = None,
) -> FieldImageRemediationResult:
    """Apply a plan. DRY RUN BY DEFAULT -- ``dry_run=False`` additionally
    requires an injected ``executor`` and ``plan.confirmation_token``. Only
    confirmed-matched items with a proposed fix are ever sent to the
    executor."""
    if dry_run:
        return FieldImageRemediationResult(
            outcome=Outcome.OBSERVED if plan.changed_items else Outcome.EMPTY, dry_run=True
        )

    _gate(plan, executor, confirm)

    if not plan.changed_items:
        return FieldImageRemediationResult(outcome=Outcome.EMPTY, dry_run=False)

    applied: list[str] = []
    failed: list[tuple[str, str]] = []

    for fix in plan.changed_items:
        try:
            executor(fix.source_id, fix.new_field_value)  # type: ignore[misc]
        except Exception as exc:  # noqa: BLE001 -- caller-supplied sink, any error is reportable
            failed.append((fix.source_id, str(exc)))
        else:
            applied.append(fix.source_id)

    if not applied and failed:
        outcome = Outcome.FAILED
    elif failed:
        outcome = Outcome.PARTIAL
    else:
        outcome = Outcome.OBSERVED

    return FieldImageRemediationResult(
        outcome=outcome, dry_run=False, applied=tuple(applied), failed=tuple(failed)
    )
