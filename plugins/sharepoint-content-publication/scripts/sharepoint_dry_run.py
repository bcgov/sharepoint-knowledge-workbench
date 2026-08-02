"""
sharepoint_dry_run.py
=======================

Pre-upload validator for a Phase 3 UploadPackage (scripts/sharepoint_package.py).
Runs entirely offline -- no SharePoint tenant I/O -- so it can gate a
human upload before any tenant write happens. See
docs/superpowers/specs/phase-3-governed-sharepoint-knowledge-pilot-spec.md
Section 9. Phase 3 plan Task 3.2.2.
"""

from dataclasses import dataclass, field

TITLE_MAX_LENGTH = 255


@dataclass
class DryRunIssue:
    severity: str  # always "error" -- dry-run has no warning tier
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
class DryRunReport:
    status: str  # "PASS" | "FAIL"
    issues: list  # list[DryRunIssue]
    package_identity: str

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "issues": [i.to_dict() for i in self.issues],
            "package_identity": self.package_identity,
        }


def validate_upload_package(pkg) -> DryRunReport:
    issues = []

    if not pkg.entries:
        issues.append(DryRunIssue("error", "EMPTY_PACKAGE",
                                   "UploadPackage has no entries"))
        return DryRunReport(status="FAIL", issues=issues,
                             package_identity=pkg.package_identity)

    seen_orders = {}
    seen_topic_ids = {}
    for entry in pkg.entries:
        if not entry.title:
            issues.append(DryRunIssue("error", "EMPTY_TITLE",
                                       f"topic {entry.topic_id!r} has an empty title",
                                       topic_id=entry.topic_id))
        elif len(entry.title) > TITLE_MAX_LENGTH:
            issues.append(DryRunIssue(
                "error", "TITLE_TOO_LONG",
                f"topic {entry.topic_id!r} title is {len(entry.title)} chars "
                f"(max {TITLE_MAX_LENGTH})",
                topic_id=entry.topic_id,
            ))

        if entry.order in seen_orders:
            issues.append(DryRunIssue(
                "error", "DUPLICATE_ORDER",
                f"order {entry.order} used by both "
                f"{seen_orders[entry.order]!r} and {entry.topic_id!r}",
                topic_id=entry.topic_id,
            ))
        else:
            seen_orders[entry.order] = entry.topic_id

        if entry.topic_id in seen_topic_ids:
            issues.append(DryRunIssue(
                "error", "DUPLICATE_TOPIC_ID",
                f"topic_id {entry.topic_id!r} appears more than once",
                topic_id=entry.topic_id,
            ))
        else:
            seen_topic_ids[entry.topic_id] = True

        content_path = pkg.root_dir / entry.content_path
        if not content_path.exists():
            issues.append(DryRunIssue(
                "error", "MISSING_CONTENT_FILE",
                f"topic {entry.topic_id!r}: {content_path} does not exist",
                topic_id=entry.topic_id,
            ))

    status = "FAIL" if issues else "PASS"
    return DryRunReport(status=status, issues=issues,
                         package_identity=pkg.package_identity)
