"""
sharepoint_reconcile.py
=========================

Purpose:
Diffs an UploadPackage (expected state, scripts/content-publication/sharepoint_package.py)
against ActualLibraryState evidence captured from the real SharePoint
library. Phase 3.0 confirmed CSV export as the only currently-available
evidence-capture mechanism (docs/superpowers/specs/phase-3-tenant-capability-report.md);
a future Graph/PnP-based reader is explicitly left open by resolved
decision #10 in docs/superpowers/specs/phase-3-unresolved-decisions.md
but is not required for this pilot. Phase 3 plan Task 3.3.1.

Key Input Dependencies:
    - UploadPackage entries as the expected publication state
    - caller-captured CSV rows as observed SharePoint state
    - standard-library csv, dataclasses, and pathlib

Function Index:
    ReconciliationIssue.to_dict, ReconciliationReport.to_dict,
    load_actual_state_from_csv, reconcile, _reconcile_entry,
    _find_unexpected_items
"""

import csv
from dataclasses import dataclass
from pathlib import Path

_COMPARED_FIELDS = (
    "title", "package_identity", "publication_order",
    "topic_content_sha256", "source_document_sha256",
)


@dataclass
class ActualLibraryItem:
    topic_id: str
    title: str
    package_identity: str
    publication_order: int
    topic_content_sha256: str
    source_document_sha256: str


@dataclass
class ReconciliationIssue:
    severity: str
    code: str
    message: str
    topic_id: str = None

    def to_dict(self) -> dict:
        """Serialize one discrepancy for a reconciliation report."""
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "topic_id": self.topic_id,
        }


@dataclass
class ReconciliationReport:
    status: str  # "MATCH" | "MISMATCH"
    issues: list  # list[ReconciliationIssue]
    package_identity: str

    def to_dict(self) -> dict:
        """Serialize the overall match status and all reconciliation issues."""
        return {
            "status": self.status,
            "issues": [i.to_dict() for i in self.issues],
            "package_identity": self.package_identity,
        }


# Load the operator's actual-library evidence CSV into typed records.
def load_actual_state_from_csv(csv_path: Path) -> list:
    """Parse the required actual-state columns into library-item records."""
    csv_path = Path(csv_path)
    items = []
    with csv_path.open(newline="") as fh:
        for row in csv.DictReader(fh):
            items.append(ActualLibraryItem(
                topic_id=row["TopicId"],
                title=row["Title"],
                package_identity=row["PackageIdentity"],
                publication_order=int(row["PublicationOrder"]),
                topic_content_sha256=row["TopicContentSHA256"],
                source_document_sha256=row["SourceDocumentSHA256"],
            ))
    return items


# Compare expected topics and fields with actual library observations.
def reconcile(pkg, actual_items: list) -> ReconciliationReport:
    """Compare package topics with observed library rows and report every drift."""
    issues = []

    actual_by_id = {}
    for item in actual_items:
        actual_by_id.setdefault(item.topic_id, []).append(item)

    expected_ids = {e.topic_id for e in pkg.entries}
    for entry in pkg.entries:
        issues.extend(_reconcile_entry(entry, actual_by_id.get(entry.topic_id, [])))
    issues.extend(_find_unexpected_items(expected_ids, actual_by_id))

    status = "MISMATCH" if issues else "MATCH"
    return ReconciliationReport(status=status, issues=issues,
                                 package_identity=pkg.package_identity)


# Report whether one package topic is missing, duplicated, or drifted.
def _reconcile_entry(entry, matches: list[ActualLibraryItem]) -> list[ReconciliationIssue]:
    """Report a missing, duplicated, or field-drifted library match for one topic."""
    if not matches:
        return [ReconciliationIssue(
            "error", "MISSING_IN_LIBRARY",
            f"topic {entry.topic_id!r} is in the upload package but "
            "not found in the library",
            topic_id=entry.topic_id,
        )]
    if len(matches) > 1:
        return [ReconciliationIssue(
            "error", "DUPLICATE_IN_LIBRARY",
            f"topic {entry.topic_id!r} appears {len(matches)} times "
            "in the library (expected exactly once)",
            topic_id=entry.topic_id,
        )]
    actual = matches[0]
    expected_values = {
        "title": entry.title,
        "package_identity": entry.package_identity,
        "publication_order": entry.order,
        "topic_content_sha256": entry.topic_content_sha256,
        "source_document_sha256": entry.source_document_sha256,
    }
    issues = []
    for field_name in _COMPARED_FIELDS:
        expected_value = expected_values[field_name]
        actual_value = getattr(actual, field_name)
        if expected_value != actual_value:
            issues.append(ReconciliationIssue(
                "error", "FIELD_MISMATCH",
                f"topic {entry.topic_id!r}: {field_name} expected "
                f"{expected_value!r}, library has {actual_value!r}",
                topic_id=entry.topic_id,
            ))
    return issues


def _find_unexpected_items(
    expected_ids: set[str], actual_by_id: dict[str, list[ActualLibraryItem]]
) -> list[ReconciliationIssue]:
    """Report observed library topics absent from the upload package."""
    return [
        ReconciliationIssue(
            "error", "UNEXPECTED_IN_LIBRARY",
            f"library has topic {topic_id!r} not present in the upload package",
            topic_id=topic_id,
        )
        for topic_id in actual_by_id
        if topic_id not in expected_ids
    ]
