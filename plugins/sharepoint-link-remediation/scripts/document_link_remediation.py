"""
document_link_remediation.py
==============================

Purpose:
    Rewrites legacy URLs embedded INSIDE Office documents (docx/xlsx/pptx)
    and PDFs stored in a document library -- distinct from
    ``link_remediation.py``, which only rewrites URLs in page/HTML body
    content. A page can be fully converted to modern SPO and still link out
    to a Word document whose own embedded hyperlinks still point at the
    old classic site.

    docx/xlsx/pptx are plain ZIP archives of XML parts (the Office Open XML
    format) -- this module rewrites them using only the standard library
    (``zipfile`` + the same ``RewriteRuleset`` text substitution
    ``link_remediation.py`` already uses), with no dependency on
    python-docx/openpyxl/python-pptx. PDF hyperlink rewriting genuinely
    requires a real PDF parser this module does not ship; a PDF document is
    reported ``Outcome.NOT_SUPPORTED`` unless the caller injects a
    ``pdf_handler(content: bytes, ruleset) -> (bytes, applied_rules)``
    callable -- honest non-coverage, never a silent no-op mistaken for
    success.

    THIS IS A WRITE CAPABILITY and is gated identically to
    ``link_remediation.py`` (same three-gate contract): planning is pure;
    apply is dry-run by default; a real apply requires both an injected
    ``executor`` callable and the plan's own confirmation token.

Layer: sharepoint-link-remediation / document-content remediation

Key Input Dependencies:
    - link_outcomes.Outcome (shared honest-outcome vocabulary)
    - link_rules.RewriteRuleset (caller-supplied)
    - a caller-injected ``executor(source, content: bytes)`` callable for real writes
    - an optional caller-injected ``pdf_handler`` for PDF support
"""

from __future__ import annotations

import hashlib
import io
import zipfile
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence

from link_outcomes import Outcome
from link_rules import RewriteRule, RewriteRuleset

Executor = Callable[[str, bytes], None]
PdfHandler = Callable[[bytes, RewriteRuleset], "tuple[bytes, list[RewriteRule]]"]

_OOXML_FORMATS = {
    "docx": "word/",
    "xlsx": "xl/",
    "pptx": "ppt/",
}

# Parts worth scanning for rewritable URLs: relationship files (hyperlinks,
# external references) and the main content XML parts. Scanning every part
# in the archive would also rewrite binary media -- restrict to XML/rels.
_REWRITABLE_SUFFIXES = (".rels", ".xml")


class DocumentRemediationSafetyError(RuntimeError):
    """Base class for every refusal to perform an unsafe write."""


class ExecutorRequired(DocumentRemediationSafetyError):
    """Raised when a real apply was requested without an injected executor."""


class ConfirmationRequired(DocumentRemediationSafetyError):
    """Raised when the confirmation token is missing or does not match the plan."""


def detect_document_format(content: bytes) -> str:
    """Detect a document's format from its actual bytes, never from a
    filename extension (a mismatched or missing extension must not cause a
    misdetection). Returns one of ``"docx"``, ``"xlsx"``, ``"pptx"``,
    ``"pdf"``, or ``"unknown"``."""
    if content.startswith(b"%PDF"):
        return "pdf"

    if content[:2] == b"PK":
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as zf:
                names = zf.namelist()
        except zipfile.BadZipFile:
            return "unknown"
        for fmt, marker in _OOXML_FORMATS.items():
            if any(name.startswith(marker) for name in names):
                return fmt

    return "unknown"


@dataclass(frozen=True)
class DocumentRemediation:
    """The planned before/after state of one document."""

    source: str
    format: str
    original_content: bytes
    remediated_content: bytes
    changes: Sequence[str] = field(default_factory=tuple)
    outcome: str = Outcome.EMPTY

    @property
    def is_changed(self) -> bool:
        return bool(self.changes)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "format": self.format,
            "changed": self.is_changed,
            "changes": list(self.changes),
            "outcome": self.outcome,
        }


@dataclass(frozen=True)
class DocumentRemediationPlan:
    """A complete, reviewable description of what a real apply would do.
    Producing a plan performs no writes."""

    documents: Sequence[DocumentRemediation] = field(default_factory=tuple)
    outcome: str = Outcome.EMPTY

    @property
    def changed_documents(self) -> list[DocumentRemediation]:
        return [d for d in self.documents if d.is_changed]

    @property
    def change_count(self) -> int:
        return len(self.changed_documents)

    @property
    def fingerprint(self) -> str:
        digest = hashlib.sha256()
        for document in self.changed_documents:
            digest.update(document.source.encode("utf-8"))
            digest.update(b"\0")
            digest.update(document.remediated_content)
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
            "documents": [d.to_dict() for d in self.documents],
        }


@dataclass(frozen=True)
class DocumentRemediationResult:
    """Evidence record for one apply attempt."""

    outcome: str
    dry_run: bool
    applied: Sequence[str] = field(default_factory=tuple)
    failed: Sequence[tuple[str, str]] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "outcome": self.outcome,
            "dry_run": self.dry_run,
            "applied": list(self.applied),
            "failed": [{"source": source, "error": error} for source, error in self.failed],
        }


def _rewrite_ooxml(content: bytes, ruleset: RewriteRuleset) -> tuple[bytes, list[str]]:
    """Rewrite every rewritable XML/rels part of a docx/xlsx/pptx archive
    against ``ruleset``, preserving every other part byte-for-byte."""
    changes: list[str] = []
    output = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(content)) as src, zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename.endswith(_REWRITABLE_SUFFIXES):
                text = data.decode("utf-8")
                rewritten, applied = ruleset.apply(text)
                if applied:
                    changes.append(f"{item.filename}: {', '.join(r.description or r.match for r in applied)}")
                    data = rewritten.encode("utf-8")
            dst.writestr(item, data)
    return output.getvalue(), changes


def plan_document_link_remediation(
    documents: Mapping[str, bytes], ruleset: RewriteRuleset, *, pdf_handler: PdfHandler | None = None
) -> DocumentRemediationPlan:
    """Detect each document's format and plan its remediation. Never
    writes anything. A PDF without an injected ``pdf_handler`` is reported
    ``Outcome.NOT_SUPPORTED`` -- never silently skipped and never attempted
    with a format-inappropriate text substitution."""
    if not documents:
        return DocumentRemediationPlan(documents=(), outcome=Outcome.EMPTY)

    planned: list[DocumentRemediation] = []
    any_not_supported = False

    for source, content in documents.items():
        fmt = detect_document_format(content)

        if fmt in _OOXML_FORMATS:
            remediated, changes = _rewrite_ooxml(content, ruleset)
            planned.append(
                DocumentRemediation(
                    source=source, format=fmt, original_content=content,
                    remediated_content=remediated, changes=tuple(changes),
                    outcome=Outcome.OBSERVED if changes else Outcome.EMPTY,
                )
            )
        elif fmt == "pdf" and pdf_handler is not None:
            remediated, applied_rules = pdf_handler(content, ruleset)
            changes = [r.description or r.match for r in applied_rules]
            planned.append(
                DocumentRemediation(
                    source=source, format=fmt, original_content=content,
                    remediated_content=remediated, changes=tuple(changes),
                    outcome=Outcome.OBSERVED if changes else Outcome.EMPTY,
                )
            )
        else:
            any_not_supported = True
            planned.append(
                DocumentRemediation(
                    source=source, format=fmt, original_content=content,
                    remediated_content=content, changes=(), outcome=Outcome.NOT_SUPPORTED,
                )
            )

    if any_not_supported:
        outcome = Outcome.NOT_SUPPORTED
    elif any(d.is_changed for d in planned):
        outcome = Outcome.OBSERVED
    else:
        outcome = Outcome.EMPTY

    return DocumentRemediationPlan(documents=tuple(planned), outcome=outcome)


def _gate(plan: DocumentRemediationPlan, executor: Executor | None, confirm: str | None) -> None:
    if executor is None:
        raise ExecutorRequired(
            "a real write requires an explicitly injected executor(source, content) callable; "
            "this module ships no transport and will not write autonomously"
        )
    expected = plan.confirmation_token
    if confirm != expected:
        raise ConfirmationRequired(
            f"confirmation token does not authorise this plan; expected {expected!r}"
        )


def apply_document_link_remediation(
    plan: DocumentRemediationPlan,
    *,
    executor: Executor | None = None,
    dry_run: bool = True,
    confirm: str | None = None,
) -> DocumentRemediationResult:
    """Apply a plan. DRY RUN BY DEFAULT -- ``dry_run=False`` additionally
    requires an injected ``executor`` and ``plan.confirmation_token``. Only
    changed documents are written; unchanged and `NOT_SUPPORTED` documents
    are never sent to the executor."""
    changed = plan.changed_documents

    if dry_run:
        return DocumentRemediationResult(
            outcome=Outcome.OBSERVED if changed else Outcome.EMPTY, dry_run=True
        )

    _gate(plan, executor, confirm)

    if not changed:
        return DocumentRemediationResult(outcome=Outcome.EMPTY, dry_run=False)

    applied: list[str] = []
    failed: list[tuple[str, str]] = []

    for document in changed:
        try:
            executor(document.source, document.remediated_content)  # type: ignore[misc]
        except Exception as exc:  # noqa: BLE001 -- caller-supplied sink, any error is reportable
            failed.append((document.source, str(exc)))
        else:
            applied.append(document.source)

    if not applied and failed:
        outcome = Outcome.FAILED
    elif failed:
        outcome = Outcome.PARTIAL
    else:
        outcome = Outcome.OBSERVED

    return DocumentRemediationResult(
        outcome=outcome, dry_run=False, applied=tuple(applied), failed=tuple(failed)
    )
