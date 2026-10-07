"""Purpose:
    Verify parsed connection and workflow-profile validation results.

Key Input Dependencies:
    - workflow_validation module and its config_setup/document_workflow dependencies.

test_workflow_validation.py
=============================

Tests for `workflow_validation` (Phase 6 Task 0.17's `validate-
workbench-environment` skill): validates already-built connection/
document-workflow/publication-profile dicts (the same dicts
`config_setup.py`/`document_workflow.py` build before serializing to
`.psd1` text) before they're consumed by other plugins.

Scope boundary: this module validates already-parsed Python dicts, not
raw `.psd1` file text -- parsing real PowerShell `.psd1` syntax in pure
Python is a genuinely separate undertaking (would need either a real
`.psd1` parser or a `pwsh -Command "Import-PowerShellDataFile ... |
ConvertTo-Json"` subprocess bridge), deliberately out of scope for this
first version rather than attempted half-heartedly. See
`workflow_validation.py`'s module docstring.

Function Index:
    - test_validate_connection_config_valid
    - test_validate_connection_config_missing_mandatory_fields
    - _valid_workflow_profile
    - test_validate_document_workflow_profile_valid
    - test_validate_document_workflow_profile_missing_required_key
    - test_validate_document_workflow_profile_rejects_unimplemented_renderer_in_requested
    - test_validate_document_workflow_profile_empty_document_id
    - _valid_publication_profile
    - test_validate_publication_profile_valid
    - test_validate_publication_profile_rejects_unimplemented_renderer
    - test_validate_publication_profile_missing_required_key
    - test_module_never_imports_tenant_clients
"""

import pytest

import workflow_validation as wv


# ---------------------------------------------------------------------------
# validate_connection_config -- delegates to config_setup's own checks
# ---------------------------------------------------------------------------

# A complete connection configuration produces a PASS report without issues.
def test_validate_connection_config_valid():
    """A complete connection configuration produces a PASS report without issues."""
    report = wv.validate_connection_config(
        connection={
            "SiteUrl": "https://tenant.sharepoint.com/sites/site",
            "TenantId": "tenant-id",
            "ClientId": "client-id",
            "AuthenticationMode": "Interactive",
        },
        authentication={},
    )
    assert report.status == "PASS"
    assert report.issues == []


# Missing mandatory connection fields are returned as validation issues.
def test_validate_connection_config_missing_mandatory_fields():
    """Missing mandatory connection fields are returned as validation issues."""
    report = wv.validate_connection_config(
        connection={"SiteUrl": "", "TenantId": "", "ClientId": "", "AuthenticationMode": ""},
        authentication={},
    )
    assert report.status == "FAIL"
    assert len(report.issues) == 4


# ---------------------------------------------------------------------------
# validate_document_workflow_profile
# ---------------------------------------------------------------------------

# Build a complete workflow profile accepted by the validator.
def _valid_workflow_profile():
    """Build a complete workflow profile accepted by the validator."""
    return {
        "SchemaVersion": "1.0",
        "Document": {"DocumentId": "sample-manual", "SourcePath": "intake/sample.docx", "SourceFormat": "docx", "IsRevision": False},
        "RequestedStages": ["render"],
        "RequestedRendererProfiles": ["multipage-markdown"],
        "UnsupportedRequests": [],
        "HumanConfirmationGates": {"TopicBoundaries": True},
        "PublicationProfilePath": "publication-profiles/sample-manual.publication.psd1",
        "AgentActionsRequested": [],
        "OutstandingDecisions": [],
    }


# A complete workflow profile passes structure and renderer validation.
def test_validate_document_workflow_profile_valid():
    """A complete workflow profile passes structure and renderer validation."""
    report = wv.validate_document_workflow_profile(_valid_workflow_profile())
    assert report.status == "PASS"


# A workflow profile missing a required key returns a FAIL report.
def test_validate_document_workflow_profile_missing_required_key():
    """A workflow profile missing a required key returns a FAIL report."""
    profile = _valid_workflow_profile()
    del profile["Document"]
    report = wv.validate_document_workflow_profile(profile)
    assert report.status == "FAIL"
    assert any(i.code == "missing_key" for i in report.issues)


# A workflow profile cannot mark an unsupported renderer as executable.
def test_validate_document_workflow_profile_rejects_unimplemented_renderer_in_requested():
    """A workflow profile cannot mark an unsupported renderer as executable."""
    profile = _valid_workflow_profile()
    profile["RequestedRendererProfiles"] = ["PDF"]  # should have been moved to UnsupportedRequests
    report = wv.validate_document_workflow_profile(profile)
    assert report.status == "FAIL"
    assert any(i.code == "unimplemented_renderer_in_requested" for i in report.issues)


# A blank workflow document ID produces an explicit validation issue.
def test_validate_document_workflow_profile_empty_document_id():
    """A blank workflow document ID produces an explicit validation issue."""
    profile = _valid_workflow_profile()
    profile["Document"]["DocumentId"] = ""
    report = wv.validate_document_workflow_profile(profile)
    assert report.status == "FAIL"
    assert any(i.code == "empty_document_id" for i in report.issues)


# ---------------------------------------------------------------------------
# validate_publication_profile
# ---------------------------------------------------------------------------

# Build a complete publication profile accepted by the validator.
def _valid_publication_profile():
    """Build a complete publication profile accepted by the validator."""
    return {
        "SchemaVersion": "1.0",
        "Document": {
            "DocumentId": "sample-manual", "Title": "Sample Manual", "ContentType": "Manual",
            "ContentOwner": "", "SourcePackagePath": "runs/sample-manual-v2", "PackageIdentity": "",
        },
        "HumanPublication": {
            "Enabled": True, "TargetType": "DocumentLibrary", "LibraryName": "KnowledgePublications",
            "RootFolder": "sample-manual", "TopicFolder": "topics", "MediaFolder": "media",
            "NavigationFolder": "navigation", "PublicationProfile": "multipage-markdown",
        },
        "PagePublication": {"Enabled": False},
        "AgentGrounding": {"Enabled": False},
        "Agents": [],
        "NativeSkills": [],
        "Evidence": {"OutputPath": ""},
    }


# A complete publication profile passes validation.
def test_validate_publication_profile_valid():
    """A complete publication profile passes validation."""
    report = wv.validate_publication_profile(_valid_publication_profile())
    assert report.status == "PASS"


# An enabled publication profile rejects an unimplemented renderer.
def test_validate_publication_profile_rejects_unimplemented_renderer():
    """An enabled publication profile rejects an unimplemented renderer."""
    profile = _valid_publication_profile()
    profile["HumanPublication"]["PublicationProfile"] = "PDF"
    report = wv.validate_publication_profile(profile)
    assert report.status == "FAIL"
    assert any(i.code == "unimplemented_renderer" for i in report.issues)


# A publication profile missing a required key returns a FAIL report.
def test_validate_publication_profile_missing_required_key():
    """A publication profile missing a required key returns a FAIL report."""
    profile = _valid_publication_profile()
    del profile["HumanPublication"]
    report = wv.validate_publication_profile(profile)
    assert report.status == "FAIL"
    assert any(i.code == "missing_key" for i in report.issues)


# ---------------------------------------------------------------------------
# Structural guarantee -- zero tenant I/O
# ---------------------------------------------------------------------------

# Verify that module never imports tenant clients.
def test_module_never_imports_tenant_clients():
    """Verify that module never imports tenant clients."""
    from pathlib import Path
    source = Path(wv.__file__).read_text()
    for forbidden in ("import requests", "PnPOnline", "urllib.request"):
        assert forbidden not in source
