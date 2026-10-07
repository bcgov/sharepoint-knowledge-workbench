"""Purpose:
    Build, validate, render, and write document-workflow and publication-profile data.

Key Input Dependencies:
    - Caller-provided document and publication profile values
    - psd1_writer.render_document
    - IMPLEMENTED_RENDERER_PROFILES

document_workflow.py
======================

Phase 6 Task 0.17 -- the `initialize-document-workflow` skill's logic.
Builds, validates, and writes the two Layer 1b/2 profile artifacts per
`docs/superpowers/specs/2026-08-02-multi-document-destination-
configuration-design.md` Section 1 (Layer 1b, Layer 2) and Section 8:

    document-workflows/<DocumentId>.workflow.psd1       -- what processing
                                                             should occur
    publication-profiles/<DocumentId>.publication.psd1  -- where each
                                                             resulting
                                                             artifact should
                                                             be published

Execution boundary (design spec Section 8, "first version"): ask ->
propose defaults -> validate -> display resolved configuration -> write
profile files -> stop. The "ask"/"propose"/"display" steps are the
calling skill's/agent's job (SKILL.md instructions) -- this module is
the pure, testable core: it takes already-collected answers, validates
them, and produces the two artifacts. It never extracts documents,
confirms topic boundaries, renders content, or connects to/modifies
SharePoint -- there is no import here that could do any of those
things (see `test_module_never_imports_extraction_rendering_or_tenant_
modules`), and `write_document_workflow`'s only I/O is writing the two
profile files themselves.

Renderer-profile allowlist: `IMPLEMENTED_RENDERER_PROFILES` is kept in
hand-sync with `structured-content-rendering`'s actual registered
renderers (`multipage-markdown`, `sharepoint-aspx`) -- see that
plugin's `renderers/protocol.py` registry. Not imported cross-plugin
(each plugin installs standalone, per this repo's architecture); update
this constant by hand when a new renderer is added there.

Function Index:
    - DocumentWorkflowError
    - classify_renderer_requests
    - _require_non_empty
    - build_workflow_profile
    - build_publication_profile
    - render_workflow_psd1
    - render_publication_profile_psd1
    - write_document_workflow
"""

from pathlib import Path

from psd1_writer import render_document

IMPLEMENTED_RENDERER_PROFILES = frozenset({"multipage-markdown", "sharepoint-aspx"})

SCHEMA_VERSION = "1.0"


class DocumentWorkflowError(Exception):
    """Raised for any validation failure while building or writing a
    document-workflow or publication profile."""


def classify_renderer_requests(requested: list) -> "tuple[list, list]":
    """Split `requested` renderer-profile names into `(supported,
    unsupported)`, preserving each list's relative order. A name is
    "supported" only if it is in `IMPLEMENTED_RENDERER_PROFILES` --
    everything else is recorded as unsupported, never silently treated
    as executable (design spec Section 8)."""
    supported = [name for name in requested if name in IMPLEMENTED_RENDERER_PROFILES]
    unsupported = [name for name in requested if name not in IMPLEMENTED_RENDERER_PROFILES]
    return supported, unsupported


# Reject a blank or whitespace-only value for the named required field.
def _require_non_empty(value: str, field_name: str) -> None:
    """Reject a blank or whitespace-only value for the named required field."""
    if not value or not value.strip():
        raise DocumentWorkflowError(f"{field_name} must be a non-empty string")


# ---------------------------------------------------------------------------
# document-workflows/<DocumentId>.workflow.psd1 (Layer 1b)
# ---------------------------------------------------------------------------

def build_workflow_profile(
    *,
    document_id: str,
    source_path: str,
    source_format: str,
    is_revision: bool,
    requested_stages: list,
    requested_renderer_profiles: list,
    human_confirmation_gates: dict,
    publication_profile_path: str,
    agent_actions_requested: list,
    outstanding_decisions: list,
) -> dict:
    """Build and validate a document-workflow profile dict (Layer 1b
    schema). Only implemented renderer profiles are ever placed in
    `RequestedRendererProfiles`; anything else moves to
    `UnsupportedRequests` instead of being dropped."""
    _require_non_empty(document_id, "document_id")
    _require_non_empty(source_path, "source_path")
    _require_non_empty(source_format, "source_format")

    supported, unsupported = classify_renderer_requests(requested_renderer_profiles)

    return {
        "SchemaVersion": SCHEMA_VERSION,
        "Document": {
            "DocumentId": document_id,
            "SourcePath": source_path,
            "SourceFormat": source_format,
            "IsRevision": bool(is_revision),
        },
        "RequestedStages": list(requested_stages),
        "RequestedRendererProfiles": supported,
        "UnsupportedRequests": unsupported,
        "HumanConfirmationGates": dict(human_confirmation_gates),
        "PublicationProfilePath": publication_profile_path,
        "AgentActionsRequested": list(agent_actions_requested),
        "OutstandingDecisions": list(outstanding_decisions),
    }


# ---------------------------------------------------------------------------
# publication-profiles/<DocumentId>.publication.psd1 (Layer 2)
# ---------------------------------------------------------------------------

def build_publication_profile(
    *,
    document_id: str,
    title: str,
    content_type: str,
    content_owner: str,
    source_package_path: str,
    package_identity: str,
    human_publication: dict,
    page_publication: "dict | None" = None,
    agent_grounding: "dict | None" = None,
    agents: "list | None" = None,
    native_skills: "list | None" = None,
    evidence_output_path: str = "",
) -> dict:
    """Build and validate a publication profile dict (Layer 2 schema).
    `human_publication["PublicationProfile"]`, if set and the section is
    enabled, must be an implemented renderer profile."""
    _require_non_empty(document_id, "document_id")

    if human_publication.get("Enabled") and human_publication.get("PublicationProfile") not in IMPLEMENTED_RENDERER_PROFILES:
        raise DocumentWorkflowError(
            f"HumanPublication.PublicationProfile "
            f"{human_publication.get('PublicationProfile')!r} is not an implemented renderer "
            f"profile ({sorted(IMPLEMENTED_RENDERER_PROFILES)})"
        )

    return {
        "SchemaVersion": SCHEMA_VERSION,
        "Document": {
            "DocumentId": document_id,
            "Title": title,
            "ContentType": content_type,
            "ContentOwner": content_owner,
            "SourcePackagePath": source_package_path,
            "PackageIdentity": package_identity,
        },
        "HumanPublication": dict(human_publication),
        "PagePublication": dict(page_publication or {"Enabled": False}),
        "AgentGrounding": dict(agent_grounding or {"Enabled": False}),
        "Agents": list(agents or []),
        "NativeSkills": list(native_skills or []),
        "Evidence": {"OutputPath": evidence_output_path},
    }


# ---------------------------------------------------------------------------
# PowerShell hashtable (.psd1) text rendering -- see psd1_writer.py
# ---------------------------------------------------------------------------

def render_workflow_psd1(profile: dict) -> str:
    """Render a document-workflow profile dict to PowerShell hashtable
    (`.psd1`) text."""
    return render_document(profile)


def render_publication_profile_psd1(profile: dict) -> str:
    """Render a publication profile dict to PowerShell hashtable
    (`.psd1`) text."""
    return render_document(profile)


# ---------------------------------------------------------------------------
# write_document_workflow -- the "write profile files -> stop" step
# ---------------------------------------------------------------------------

def write_document_workflow(
    root: "Path | str",
    document_id: str,
    workflow_profile: dict,
    publication_profile: dict,
    *,
    overwrite: bool = False,
) -> "tuple[Path, Path]":
    """Write both profile files under `root` (`document-workflows/
    <document_id>.workflow.psd1`, `publication-profiles/<document_id>.
    publication.psd1`). Refuses to silently overwrite an existing file
    unless `overwrite=True` is explicitly passed -- collision safety per
    design spec Section 7's "overwrite behavior is explicit, never
    implicit" rule. Returns `(workflow_path, publication_path)`."""
    root = Path(root)
    workflow_path = root / "document-workflows" / f"{document_id}.workflow.psd1"
    publication_path = root / "publication-profiles" / f"{document_id}.publication.psd1"

    if not overwrite:
        for path in (workflow_path, publication_path):
            if path.exists():
                raise DocumentWorkflowError(
                    f"{path} already exists -- pass overwrite=True to replace it explicitly"
                )

    workflow_path.parent.mkdir(parents=True, exist_ok=True)
    publication_path.parent.mkdir(parents=True, exist_ok=True)
    workflow_path.write_text(render_workflow_psd1(workflow_profile))
    publication_path.write_text(render_publication_profile_psd1(publication_profile))
    return workflow_path, publication_path
