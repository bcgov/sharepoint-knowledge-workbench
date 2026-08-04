"""
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
"""

import pytest

import workflow_validation as wv


# ---------------------------------------------------------------------------
# validate_connection_config -- delegates to config_setup's own checks
# ---------------------------------------------------------------------------

def test_validate_connection_config_valid():
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


def test_validate_connection_config_missing_mandatory_fields():
    report = wv.validate_connection_config(
        connection={"SiteUrl": "", "TenantId": "", "ClientId": "", "AuthenticationMode": ""},
        authentication={},
    )
    assert report.status == "FAIL"
    assert len(report.issues) == 4


# ---------------------------------------------------------------------------
# validate_document_workflow_profile
# ---------------------------------------------------------------------------

def _valid_workflow_profile():
    return {
        "SchemaVersion": "1.0",
        "Document": {"DocumentId": "ceis-manual", "SourcePath": "intake/ceis.docx", "SourceFormat": "docx", "IsRevision": False},
        "RequestedStages": ["render"],
        "RequestedRendererProfiles": ["multipage-markdown"],
        "UnsupportedRequests": [],
        "HumanConfirmationGates": {"TopicBoundaries": True},
        "PublicationProfilePath": "publication-profiles/ceis-manual.publication.psd1",
        "AgentActionsRequested": [],
        "OutstandingDecisions": [],
    }


def test_validate_document_workflow_profile_valid():
    report = wv.validate_document_workflow_profile(_valid_workflow_profile())
    assert report.status == "PASS"


def test_validate_document_workflow_profile_missing_required_key():
    profile = _valid_workflow_profile()
    del profile["Document"]
    report = wv.validate_document_workflow_profile(profile)
    assert report.status == "FAIL"
    assert any(i.code == "missing_key" for i in report.issues)


def test_validate_document_workflow_profile_rejects_unimplemented_renderer_in_requested():
    profile = _valid_workflow_profile()
    profile["RequestedRendererProfiles"] = ["PDF"]  # should have been moved to UnsupportedRequests
    report = wv.validate_document_workflow_profile(profile)
    assert report.status == "FAIL"
    assert any(i.code == "unimplemented_renderer_in_requested" for i in report.issues)


def test_validate_document_workflow_profile_empty_document_id():
    profile = _valid_workflow_profile()
    profile["Document"]["DocumentId"] = ""
    report = wv.validate_document_workflow_profile(profile)
    assert report.status == "FAIL"
    assert any(i.code == "empty_document_id" for i in report.issues)


# ---------------------------------------------------------------------------
# validate_publication_profile
# ---------------------------------------------------------------------------

def _valid_publication_profile():
    return {
        "SchemaVersion": "1.0",
        "Document": {
            "DocumentId": "ceis-manual", "Title": "CEIS Manual", "ContentType": "Manual",
            "ContentOwner": "", "SourcePackagePath": "runs/ceis-manual-v2", "PackageIdentity": "",
        },
        "HumanPublication": {
            "Enabled": True, "TargetType": "DocumentLibrary", "LibraryName": "KnowledgePublications",
            "RootFolder": "ceis-manual", "TopicFolder": "topics", "MediaFolder": "media",
            "NavigationFolder": "navigation", "PublicationProfile": "multipage-markdown",
        },
        "PagePublication": {"Enabled": False},
        "AgentGrounding": {"Enabled": False},
        "Agents": [],
        "NativeSkills": [],
        "Evidence": {"OutputPath": ""},
    }


def test_validate_publication_profile_valid():
    report = wv.validate_publication_profile(_valid_publication_profile())
    assert report.status == "PASS"


def test_validate_publication_profile_rejects_unimplemented_renderer():
    profile = _valid_publication_profile()
    profile["HumanPublication"]["PublicationProfile"] = "PDF"
    report = wv.validate_publication_profile(profile)
    assert report.status == "FAIL"
    assert any(i.code == "unimplemented_renderer" for i in report.issues)


def test_validate_publication_profile_missing_required_key():
    profile = _valid_publication_profile()
    del profile["HumanPublication"]
    report = wv.validate_publication_profile(profile)
    assert report.status == "FAIL"
    assert any(i.code == "missing_key" for i in report.issues)


# ---------------------------------------------------------------------------
# Structural guarantee -- zero tenant I/O
# ---------------------------------------------------------------------------

def test_module_never_imports_tenant_clients():
    from pathlib import Path
    source = Path(wv.__file__).read_text()
    for forbidden in ("import requests", "PnPOnline", "urllib.request"):
        assert forbidden not in source
