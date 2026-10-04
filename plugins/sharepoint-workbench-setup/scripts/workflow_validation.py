"""
workflow_validation.py
========================

Phase 6 Task 0.17 -- the `validate-sharepoint-connection` skill's
logic. Validates already-built connection/document-workflow/
publication-profile dicts (the same in-memory shape `config_setup.py`/
`document_workflow.py` build before serializing to `.psd1` text) before
they're consumed by other plugins.

**Scope boundary, deliberate:** this module validates already-PARSED
Python dicts, not raw `.psd1` file text. Parsing real PowerShell
`.psd1` hashtable syntax in pure Python is a genuinely separate
undertaking -- correctly handling nested hashtables, arrays, PowerShell
comments, and boolean/string literal syntax is not a quick regex job.
Rather than ship a fragile, half-correct custom parser, this first
version's boundary is: callers that have an on-disk `.psd1` file must
parse it themselves (e.g. via a `pwsh -Command "Import-
PowerShellDataFile <path> | ConvertTo-Json"` subprocess bridge -- the
same cross-language pattern already used elsewhere in this repo, e.g.
`tools/phase-4-native-sharepoint-skills/tests/test_rollback_and_exit_
gate.py`) before calling into this module. A future, separately-scoped
version may add that bridge directly; not attempted here.

Every issue is `severity="error"` -- status is always `PASS` or `FAIL`,
matching this repo's other validators' convention (e.g.
`structured-content-rendering`'s `renderers/validate_rendered.py`).
"""

from dataclasses import dataclass, field

from config_setup import validate_connection_answers
from document_workflow import IMPLEMENTED_RENDERER_PROFILES


@dataclass
class ValidationIssue:
    severity: str
    code: str
    message: str


@dataclass
class ValidationReport:
    status: str
    issues: list = field(default_factory=list)


def _error(code: str, message: str) -> "ValidationIssue":
    return ValidationIssue(severity="error", code=code, message=message)


def _report(issues: list) -> "ValidationReport":
    return ValidationReport(status="FAIL" if issues else "PASS", issues=issues)


def _check_required_keys(data: dict, required: "tuple[str, ...]") -> list:
    issues = []
    for key in required:
        if key not in data:
            issues.append(_error("missing_key", f"required key {key!r} is missing"))
    return issues


# ---------------------------------------------------------------------------
# Connection config
# ---------------------------------------------------------------------------

def validate_connection_config(connection: dict, authentication: dict) -> "ValidationReport":
    """Validate a Layer 1 connection-config dict. Delegates to
    `config_setup.validate_connection_answers` (the single source of
    truth for these rules) and adapts its `ConfigIssue` list to this
    module's `ValidationReport` shape."""
    config_issues = validate_connection_answers(connection, authentication)
    issues = [_error(issue.code, issue.message) for issue in config_issues]
    return _report(issues)


# ---------------------------------------------------------------------------
# Document-workflow profile
# ---------------------------------------------------------------------------

_WORKFLOW_REQUIRED_KEYS = (
    "SchemaVersion", "Document", "RequestedStages", "RequestedRendererProfiles",
    "UnsupportedRequests", "HumanConfirmationGates", "PublicationProfilePath",
    "AgentActionsRequested", "OutstandingDecisions",
)


def validate_document_workflow_profile(profile: dict) -> "ValidationReport":
    """Validate a document-workflow profile dict (Layer 1b schema)."""
    issues = _check_required_keys(profile, _WORKFLOW_REQUIRED_KEYS)
    if issues:
        return _report(issues)

    document_id = profile.get("Document", {}).get("DocumentId", "")
    if not document_id or not document_id.strip():
        issues.append(_error("empty_document_id", "Document.DocumentId must be non-empty"))

    for name in profile.get("RequestedRendererProfiles", []):
        if name not in IMPLEMENTED_RENDERER_PROFILES:
            issues.append(_error(
                "unimplemented_renderer_in_requested",
                f"RequestedRendererProfiles contains {name!r}, which is not an implemented "
                f"renderer profile ({sorted(IMPLEMENTED_RENDERER_PROFILES)}) -- it must be in "
                "UnsupportedRequests instead",
            ))

    return _report(issues)


# ---------------------------------------------------------------------------
# Publication profile
# ---------------------------------------------------------------------------

_PUBLICATION_REQUIRED_KEYS = (
    "SchemaVersion", "Document", "HumanPublication", "PagePublication",
    "AgentGrounding", "Agents", "NativeSkills", "Evidence",
)


def validate_publication_profile(profile: dict) -> "ValidationReport":
    """Validate a publication profile dict (Layer 2 schema)."""
    issues = _check_required_keys(profile, _PUBLICATION_REQUIRED_KEYS)
    if issues:
        return _report(issues)

    human_publication = profile.get("HumanPublication", {})
    if human_publication.get("Enabled") and human_publication.get("PublicationProfile") not in IMPLEMENTED_RENDERER_PROFILES:
        issues.append(_error(
            "unimplemented_renderer",
            f"HumanPublication.PublicationProfile "
            f"{human_publication.get('PublicationProfile')!r} is not an implemented renderer "
            f"profile ({sorted(IMPLEMENTED_RENDERER_PROFILES)})",
        ))

    return _report(issues)
