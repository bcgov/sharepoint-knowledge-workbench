"""Purpose:
    Verify document-workflow profile construction, validation, and local file-writing contracts.

Key Input Dependencies:
    - document_workflow module and psd1_writer
    - Temporary filesystem paths provided by pytest.

test_document_workflow.py
===========================

Tests for `document_workflow` (Phase 6 Task 0.17's `initialize-document-
workflow` skill): builds/validates/writes the two Layer 1b/2 profile
artifacts (`document-workflows/<DocumentId>.workflow.psd1`,
`publication-profiles/<DocumentId>.publication.psd1`) per
`docs/superpowers/specs/2026-08-02-multi-document-destination-
configuration-design.md` Sections 1 and 8. Execution boundary: ask ->
propose defaults -> validate -> display -> write -> stop. This module
never extracts documents, renders content, or connects to/modifies
SharePoint -- proven structurally (no such imports exist at all) as
well as behaviorally (writing a profile performs no I/O beyond the
profile files themselves).

Function Index:
    - test_implemented_renderer_profiles_matches_real_renderers
    - test_classify_renderer_requests_splits_supported_and_unsupported
    - test_classify_renderer_requests_preserves_order_within_each_list
    - test_build_workflow_profile_happy_path
    - test_build_workflow_profile_moves_unsupported_renderer_out_of_requested
    - test_build_workflow_profile_rejects_empty_document_id
    - test_render_workflow_psd1_produces_parseable_powershell_shape
    - test_build_publication_profile_happy_path
    - test_build_publication_profile_rejects_unsupported_renderer_in_human_publication
    - test_render_publication_profile_psd1_produces_parseable_powershell_shape
    - test_write_document_workflow_writes_both_files
    - test_write_document_workflow_refuses_silent_overwrite
    - test_module_never_imports_extraction_rendering_or_tenant_modules
"""

from pathlib import Path

import pytest

import document_workflow as dw


# ---------------------------------------------------------------------------
# Renderer-profile classification -- "only implemented profiles may appear"
# ---------------------------------------------------------------------------

# Verify that implemented renderer profiles matches real renderers.
def test_implemented_renderer_profiles_matches_real_renderers():
    # Kept in sync by hand with structured-content-rendering's actual
    # registered renderers (multipage-markdown, sharepoint-aspx) -- see
    # that plugin's renderers/protocol.py registry. This test documents
    # the sync point rather than importing cross-plugin (each plugin
    # installs standalone).
    """Verify that implemented renderer profiles matches real renderers."""
    assert dw.IMPLEMENTED_RENDERER_PROFILES == frozenset({"multipage-markdown", "sharepoint-aspx"})


# Verify that classify renderer requests splits supported and unsupported.
def test_classify_renderer_requests_splits_supported_and_unsupported():
    """Verify that classify renderer requests splits supported and unsupported."""
    supported, unsupported = dw.classify_renderer_requests(
        ["multipage-markdown", "PDF", "sharepoint-aspx", "docx"]
    )
    assert supported == ["multipage-markdown", "sharepoint-aspx"]
    assert unsupported == ["PDF", "docx"]


# Verify that classify renderer requests preserves order within each list.
def test_classify_renderer_requests_preserves_order_within_each_list():
    """Verify that classify renderer requests preserves order within each list."""
    supported, unsupported = dw.classify_renderer_requests(
        ["sharepoint-aspx", "multipage-markdown"]
    )
    assert supported == ["sharepoint-aspx", "multipage-markdown"]


# ---------------------------------------------------------------------------
# build_workflow_profile -- validates and rejects unsupported-as-executable
# ---------------------------------------------------------------------------

# Valid workflow input produces the expected workflow profile fields.
def test_build_workflow_profile_happy_path():
    """Valid workflow input produces the expected workflow profile fields."""
    profile = dw.build_workflow_profile(
        document_id="sample-manual",
        source_path="intake/sample.docx",
        source_format="docx",
        is_revision=False,
        requested_stages=["extract", "analyze", "assemble", "render"],
        requested_renderer_profiles=["multipage-markdown"],
        human_confirmation_gates={"TopicBoundaries": True, "PublicationTargets": True},
        publication_profile_path="publication-profiles/sample-manual.publication.psd1",
        agent_actions_requested=[],
        outstanding_decisions=[],
    )
    assert profile["Document"]["DocumentId"] == "sample-manual"
    assert profile["RequestedRendererProfiles"] == ["multipage-markdown"]
    assert profile["UnsupportedRequests"] == []
    assert profile["SchemaVersion"] == "1.0"


# Unsupported renderer requests are recorded as unsupported, not executable.
def test_build_workflow_profile_moves_unsupported_renderer_out_of_requested():
    """Unsupported renderer requests are recorded as unsupported, not executable."""
    profile = dw.build_workflow_profile(
        document_id="sample-manual",
        source_path="intake/sample.docx",
        source_format="docx",
        is_revision=False,
        requested_stages=["render"],
        requested_renderer_profiles=["multipage-markdown", "PDF"],
        human_confirmation_gates={"TopicBoundaries": True, "PublicationTargets": True},
        publication_profile_path="publication-profiles/sample-manual.publication.psd1",
        agent_actions_requested=[],
        outstanding_decisions=[],
    )
    assert profile["RequestedRendererProfiles"] == ["multipage-markdown"]
    assert profile["UnsupportedRequests"] == ["PDF"]


# Workflow profile construction rejects a blank document ID.
def test_build_workflow_profile_rejects_empty_document_id():
    """Workflow profile construction rejects a blank document ID."""
    with pytest.raises(dw.DocumentWorkflowError):
        dw.build_workflow_profile(
            document_id="",
            source_path="intake/sample.docx",
            source_format="docx",
            is_revision=False,
            requested_stages=["render"],
            requested_renderer_profiles=[],
            human_confirmation_gates={},
            publication_profile_path="publication-profiles/x.publication.psd1",
            agent_actions_requested=[],
            outstanding_decisions=[],
        )


# ---------------------------------------------------------------------------
# render_workflow_psd1 -- PowerShell hashtable text generation
# ---------------------------------------------------------------------------

# Verify that render workflow psd1 produces parseable powershell shape.
def test_render_workflow_psd1_produces_parseable_powershell_shape():
    """Verify that render workflow psd1 produces parseable powershell shape."""
    profile = dw.build_workflow_profile(
        document_id="sample-manual",
        source_path="intake/sample.docx",
        source_format="docx",
        is_revision=False,
        requested_stages=["render"],
        requested_renderer_profiles=["multipage-markdown"],
        human_confirmation_gates={"TopicBoundaries": True},
        publication_profile_path="publication-profiles/sample-manual.publication.psd1",
        agent_actions_requested=[],
        outstanding_decisions=["confirm topic grouping"],
    )
    text = dw.render_workflow_psd1(profile)
    assert text.strip().startswith("@{")
    assert text.strip().endswith("}")
    assert 'DocumentId   = "sample-manual"' in text or 'DocumentId = "sample-manual"' in text
    assert '"multipage-markdown"' in text
    assert "$true" in text  # PowerShell boolean literal, not Python True
    assert "confirm topic grouping" in text


# ---------------------------------------------------------------------------
# build_publication_profile / render_publication_profile_psd1
# ---------------------------------------------------------------------------

# Valid publication input produces the expected Layer 2 profile.
def test_build_publication_profile_happy_path():
    """Valid publication input produces the expected Layer 2 profile."""
    profile = dw.build_publication_profile(
        document_id="sample-manual",
        title="Sample Manual",
        content_type="Manual",
        content_owner="",
        source_package_path="runs/sample-manual-v2",
        package_identity="",
        human_publication={
            "Enabled": True, "TargetType": "DocumentLibrary",
            "LibraryName": "KnowledgePublications", "RootFolder": "sample-manual",
            "TopicFolder": "topics", "MediaFolder": "media",
            "NavigationFolder": "navigation", "PublicationProfile": "multipage-markdown",
        },
    )
    assert profile["Document"]["DocumentId"] == "sample-manual"
    assert profile["HumanPublication"]["Enabled"] is True


# An enabled publication profile rejects an unsupported renderer.
def test_build_publication_profile_rejects_unsupported_renderer_in_human_publication():
    """An enabled publication profile rejects an unsupported renderer."""
    with pytest.raises(dw.DocumentWorkflowError):
        dw.build_publication_profile(
            document_id="sample-manual",
            title="Sample Manual",
            content_type="Manual",
            content_owner="",
            source_package_path="runs/sample-manual-v2",
            package_identity="",
            human_publication={
                "Enabled": True, "TargetType": "DocumentLibrary",
                "LibraryName": "KnowledgePublications", "RootFolder": "sample-manual",
                "TopicFolder": "topics", "MediaFolder": "media",
                "NavigationFolder": "navigation", "PublicationProfile": "PDF",
            },
        )


# Verify that render publication profile psd1 produces parseable powershell shape.
def test_render_publication_profile_psd1_produces_parseable_powershell_shape():
    """Verify that render publication profile psd1 produces parseable powershell shape."""
    profile = dw.build_publication_profile(
        document_id="sample-manual",
        title="Sample Manual",
        content_type="Manual",
        content_owner="",
        source_package_path="runs/sample-manual-v2",
        package_identity="",
        human_publication={
            "Enabled": True, "TargetType": "DocumentLibrary",
            "LibraryName": "KnowledgePublications", "RootFolder": "sample-manual",
            "TopicFolder": "topics", "MediaFolder": "media",
            "NavigationFolder": "navigation", "PublicationProfile": "multipage-markdown",
        },
    )
    text = dw.render_publication_profile_psd1(profile)
    assert text.strip().startswith("@{")
    assert '"KnowledgePublications"' in text


# ---------------------------------------------------------------------------
# write_document_workflow -- execution boundary + collision safety
# ---------------------------------------------------------------------------

# Verify that write document workflow writes both files.
def test_write_document_workflow_writes_both_files(tmp_path):
    """Verify that write document workflow writes both files."""
    workflow = dw.build_workflow_profile(
        document_id="sample-manual", source_path="intake/sample.docx", source_format="docx",
        is_revision=False, requested_stages=["render"],
        requested_renderer_profiles=["multipage-markdown"],
        human_confirmation_gates={}, publication_profile_path="publication-profiles/sample-manual.publication.psd1",
        agent_actions_requested=[], outstanding_decisions=[],
    )
    publication = dw.build_publication_profile(
        document_id="sample-manual", title="Sample Manual", content_type="Manual",
        content_owner="", source_package_path="runs/sample-manual-v2", package_identity="",
        human_publication={
            "Enabled": True, "TargetType": "DocumentLibrary", "LibraryName": "KnowledgePublications",
            "RootFolder": "sample-manual", "TopicFolder": "topics", "MediaFolder": "media",
            "NavigationFolder": "navigation", "PublicationProfile": "multipage-markdown",
        },
    )
    workflow_path, publication_path = dw.write_document_workflow(tmp_path, "sample-manual", workflow, publication)

    assert workflow_path == tmp_path / "document-workflows" / "sample-manual.workflow.psd1"
    assert publication_path == tmp_path / "publication-profiles" / "sample-manual.publication.psd1"
    assert workflow_path.exists()
    assert publication_path.exists()


# Verify that write document workflow refuses silent overwrite.
def test_write_document_workflow_refuses_silent_overwrite(tmp_path):
    """Verify that write document workflow refuses silent overwrite."""
    workflow = dw.build_workflow_profile(
        document_id="sample-manual", source_path="intake/sample.docx", source_format="docx",
        is_revision=False, requested_stages=["render"], requested_renderer_profiles=[],
        human_confirmation_gates={}, publication_profile_path="publication-profiles/sample-manual.publication.psd1",
        agent_actions_requested=[], outstanding_decisions=[],
    )
    publication = dw.build_publication_profile(
        document_id="sample-manual", title="Sample Manual", content_type="Manual",
        content_owner="", source_package_path="runs/sample-manual-v2", package_identity="",
        human_publication={
            "Enabled": False, "TargetType": "DocumentLibrary", "LibraryName": "KnowledgePublications",
            "RootFolder": "sample-manual", "TopicFolder": "topics", "MediaFolder": "media",
            "NavigationFolder": "navigation", "PublicationProfile": "multipage-markdown",
        },
    )
    dw.write_document_workflow(tmp_path, "sample-manual", workflow, publication)

    with pytest.raises(dw.DocumentWorkflowError):
        dw.write_document_workflow(tmp_path, "sample-manual", workflow, publication)

    # Explicit overwrite=True is allowed.
    dw.write_document_workflow(tmp_path, "sample-manual", workflow, publication, overwrite=True)


# ---------------------------------------------------------------------------
# Structural guarantee -- zero extraction/rendering/tenant-I/O imports
# ---------------------------------------------------------------------------

# Verify that module never imports extraction rendering or tenant modules.
def test_module_never_imports_extraction_rendering_or_tenant_modules():
    """Verify that module never imports extraction rendering or tenant modules."""
    source = Path(dw.__file__).read_text()
    for forbidden in (
        "import pandoc", "import extraction", "import multipage_markdown",
        "import sharepoint_aspx", "PnPOnline", "Connect-PnP", "requests.",
    ):
        assert forbidden not in source
