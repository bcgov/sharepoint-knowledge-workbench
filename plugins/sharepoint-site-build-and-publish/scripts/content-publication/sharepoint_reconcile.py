"""
sharepoint_reconcile.py
=========================

Diffs an UploadPackage (expected state, scripts/content-publication/sharepoint_package.py)
against ActualLibraryState evidence captured from the real SharePoint
library. Phase 3.0 confirmed CSV export as the only currently-available
evidence-capture mechanism (docs/superpowers/specs/phase-3-tenant-capability-report.md);
a future Graph/PnP-based reader is explicitly left open by resolved
decision #10 in docs/superpowers/specs/phase-3-unresolved-decisions.md
but is not required for this pilot. Phase 3 plan Task 3.3.1.
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
        return {
            "status": self.status,
            "issues": [i.to_dict() for i in self.issues],
            "package_identity": self.package_identity,
        }


def load_actual_state_from_csv(csv_path: Path) -> list:
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


def reconcile(pkg, actual_items: list) -> ReconciliationReport:
    issues = []

    actual_by_id = {}
    for item in actual_items:
        actual_by_id.setdefault(item.topic_id, []).append(item)

    expected_ids = {e.topic_id for e in pkg.entries}

    for entry in pkg.entries:
        matches = actual_by_id.get(entry.topic_id, [])
        if not matches:
            issues.append(ReconciliationIssue(
                "error", "MISSING_IN_LIBRARY",
                f"topic {entry.topic_id!r} is in the upload package but "
                "not found in the library",
                topic_id=entry.topic_id,
            ))
            continue
        if len(matches) > 1:
            issues.append(ReconciliationIssue(
                "error", "DUPLICATE_IN_LIBRARY",
                f"topic {entry.topic_id!r} appears {len(matches)} times "
                "in the library (expected exactly once)",
                topic_id=entry.topic_id,
            ))
            continue

        actual = matches[0]
        expected_values = {
            "title": entry.title,
            "package_identity": entry.package_identity,
            "publication_order": entry.order,
            "topic_content_sha256": entry.topic_content_sha256,
            "source_document_sha256": entry.source_document_sha256,
        }
        for field_name in _COMPARED_FIELDS:
            expected_val = expected_values[field_name]
            actual_val = getattr(actual, field_name)
            if expected_val != actual_val:
                issues.append(ReconciliationIssue(
                    "error", "FIELD_MISMATCH",
                    f"topic {entry.topic_id!r}: {field_name} expected "
                    f"{expected_val!r}, library has {actual_val!r}",
                    topic_id=entry.topic_id,
                ))

    for topic_id in actual_by_id:
        if topic_id not in expected_ids:
            issues.append(ReconciliationIssue(
                "error", "UNEXPECTED_IN_LIBRARY",
                f"library has topic {topic_id!r} not present in the "
                "upload package",
                topic_id=topic_id,
            ))

    status = "MISMATCH" if issues else "MATCH"
    return ReconciliationReport(status=status, issues=issues,
                                 package_identity=pkg.package_identity)
