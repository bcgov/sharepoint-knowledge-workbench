"""Purpose:
    Resolve configured downstream invocations to real export paths without executing them.

Key Input Dependencies:
    - DocumentId, connection, workflow-profile, and publication-profile mappings
    - <workbench_root>/sharepoint-exports/<DocumentId>/* files
    - DOWNSTREAM_INVOCATIONS registry

path_resolution.py
====================

Phase 9 Part B (`docs/superpowers/specs/2026-08-07-sharepoint-
collection-and-orchestration-design.md`) -- the `resolve-workbench-
paths` skill's logic.

**Layer:** sits *above* the two Phase 9 analysis plugins
(`sharepoint-site-assessment`, `sharepoint-site-migration`) and *below* the config
artifacts `sharepoint-workbench-setup`'s other skills already produce (connection
config, document-workflow profile, publication profile). It reads
already-parsed dicts of those three shapes for one `DocumentId`,
resolves them into the concrete export paths each downstream plugin
skill would need, and reports which are actually present on disk.

**Resolution flows downward only.** This module never imports, calls,
or subprocess-launches any of the two downstream plugins -- see
`test_module_never_imports_downstream_plugins` in this plugin's test
suite. Referencing a plugin/skill name here is always a plain string in
`DOWNSTREAM_INVOCATIONS`, never an import. That keeps `sharepoint-workbench-setup`
free of any dependency on those two plugins, preserving its own
standalone installability (verified separately by
`isolated_install_check.py`).

**Print, don't execute.** `format_invocations` renders the resolved
paths and arguments as text for a human/agent to review and run
themselves. Nothing in this module launches a subprocess or imports a
downstream module -- see the design spec's Part B, "Print-don't-execute
keeps the layer inspectable... Execution can be added later if it
proves warranted; it should not be assumed up front."

**Export path convention.** Nothing before this module defined where
collected SharePoint exports land on disk (Part A, the collection
plugin that would produce them, is explicitly out of scope -- design
only, `REQUIRES_HUMAN_DECISION`). Until a human produces exports by
hand or Part A exists, this module needs *some* concrete on-disk
location to resolve against, so it establishes the minimal one implied
by the design spec: `<workbench_root>/sharepoint-exports/<DocumentId>/
<skill-export-subdir>/<filename>`. This is a resolution convention, not
a claim that any collector produces it yet -- an absent file is
reported `UNAVAILABLE`, never fabricated.

**Scope boundary, deliberate (matches `workflow_validation.py`):**
operates on already-parsed connection/workflow-profile/publication-
profile dicts, not raw `.psd1` text. See that module's docstring for
why raw `.psd1` parsing is out of scope for this first version.

**Not a workflow engine.** `resolve_workbench_paths` performs exactly
one pass over a fixed, static registry (`DOWNSTREAM_INVOCATIONS`) --
no conditional branching on profile contents beyond `DocumentId`
matching, no state machine, no execution ordering. If a caller needs
that kind of orchestration, this module has been outgrown by design
(see the design spec's "What this deliberately does NOT do").

Function Index:
    - InvocationSpec
    - ResolvedInvocation
    - ResolvedInvocation.missing_args
    - PathResolutionResult
    - _spec_for
    - _validate_document_id
    - _resolve_invocation
    - _overall_status
    - resolve_workbench_paths
    - format_invocations
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


# ---------------------------------------------------------------------------
# Registry -- plain data. Every entry below names a downstream plugin/skill
# as a string, never an import. Filenames/arg-names are taken from each
# skill's own SKILL.md "Usage" section.
# ---------------------------------------------------------------------------

# Define a downstream plugin/skill target and the export filenames its invocation requires.
@dataclass(frozen=True)
class InvocationSpec:
    """Define a downstream plugin/skill target and the export filenames its invocation requires."""
    plugin: str
    skill: str
    export_subdir: str
    required_paths: "tuple[dict, ...]"  # each: {"arg": str, "filename": str}


DOWNSTREAM_INVOCATIONS: "tuple[InvocationSpec, ...]" = (
    InvocationSpec(
        plugin="sharepoint-site-assessment",
        skill="sharepoint-analyze-page-inventory",
        export_subdir="page-inventory",
        required_paths=(
            {"arg": "inventory_path", "filename": "page-inventory.json"},
            {"arg": "rules_path", "filename": "rules.json"},
        ),
    ),
    InvocationSpec(
        plugin="sharepoint-site-assessment",
        skill="sharepoint-analyze-webpart-behavior",
        export_subdir="webpart-code",
        required_paths=(
            {"arg": "extract_path", "filename": "webpart-content.json"},
        ),
    ),
    InvocationSpec(
        plugin="sharepoint-site-assessment",
        skill="sharepoint-analyze-site-navigation",
        export_subdir="site-navigation",
        required_paths=(
            {"arg": "navigation_path", "filename": "navigation.json"},
        ),
    ),
    InvocationSpec(
        plugin="sharepoint-site-assessment",
        skill="sharepoint-analyze-custom-forms",
        export_subdir="custom-forms",
        required_paths=(
            {"arg": "forms_path", "filename": "forms.json"},
            {"arg": "rules_path", "filename": "rules.json"},
        ),
    ),
    InvocationSpec(
        plugin="sharepoint-site-assessment",
        skill="sharepoint-analyze-permissions",
        export_subdir="permissions",
        required_paths=(
            {"arg": "permissions_path", "filename": "permissions.json"},
        ),
    ),
    InvocationSpec(
        plugin="sharepoint-site-assessment",
        skill="sharepoint-compare-schema-exports",
        export_subdir="schema",
        required_paths=(
            {"arg": "baseline_export_dir", "filename": "baseline"},
            {"arg": "candidate_export_dir", "filename": "candidate"},
        ),
    ),
    InvocationSpec(
        plugin="sharepoint-site-assessment",
        skill="sharepoint-extract-choice-columns",
        export_subdir="schema",
        required_paths=(
            {"arg": "baseline_export_dir", "filename": "baseline"},
        ),
    ),
    InvocationSpec(
        plugin="sharepoint-site-migration",
        skill="sharepoint-extract-links",
        export_subdir="links",
        required_paths=(
            {"arg": "page_path", "filename": "page.aspx"},
        ),
    ),
    InvocationSpec(
        plugin="sharepoint-site-migration",
        skill="sharepoint-update-page-links",
        export_subdir="links",
        required_paths=(
            {"arg": "rules_path", "filename": "rules.json"},
        ),
    ),
    InvocationSpec(
        plugin="sharepoint-site-migration",
        skill="sharepoint-validate-link-integrity",
        export_subdir="links",
        required_paths=(
            {"arg": "export_dir", "filename": "export"},
        ),
    ),
    InvocationSpec(
        plugin="sharepoint-site-migration",
        skill="sharepoint-analyze-classic-pages",
        export_subdir="pages",
        required_paths=(
            {"arg": "raw_html", "filename": "classic-page.raw.html"},
            {"arg": "views", "filename": "classic-page.views.json"},
            {"arg": "overrides", "filename": "classic-page.override.json"},
        ),
    ),
    InvocationSpec(
        plugin="sharepoint-site-migration",
        skill="sharepoint-plan-page-modernization",
        export_subdir="pages",
        required_paths=(
            {"arg": "classified", "filename": "classified.json"},
        ),
    ),
    InvocationSpec(
        plugin="sharepoint-site-migration",
        skill="sharepoint-create-page-preview",
        export_subdir="pages",
        required_paths=(
            {"arg": "page_folder", "filename": "destination"},
            {"arg": "chrome_folder", "filename": "site-chrome"},
        ),
    ),
)


# ---------------------------------------------------------------------------
# Resolution result shapes
# ---------------------------------------------------------------------------

# Record one downstream skill status, its existing argument paths, and missing exports.
@dataclass
class ResolvedInvocation:
    """Record one downstream skill status, its existing argument paths, and missing exports."""
    plugin: str
    skill: str
    status: str  # "AVAILABLE" | "PARTIAL" | "UNAVAILABLE"
    args: dict = field(default_factory=dict)     # arg -> resolved Path (only for present files)
    missing: "list[str]" = field(default_factory=list)  # missing filenames

    def missing_args(self) -> "list[str]":
        """The arg names whose files are missing -- never present in
        `self.args`."""
        return [
            path_entry["arg"]
            for path_entry in _spec_for(self.plugin, self.skill).required_paths
            if path_entry["filename"] in self.missing
        ]


# Summarize the resolution status and invocations for one document.
@dataclass
class PathResolutionResult:
    """Summarize the resolution status and invocations for one document."""
    document_id: str
    overall_status: str  # "PASS" | "PARTIAL" | "EMPTY"
    invocations: "list[ResolvedInvocation]" = field(default_factory=list)


# Return the registry specification for the requested plugin and skill pair.
def _spec_for(plugin: str, skill: str) -> InvocationSpec:
    """Return the registry specification for the requested plugin and skill pair."""
    for spec in DOWNSTREAM_INVOCATIONS:
        if spec.plugin == plugin and spec.skill == skill:
            return spec
    raise KeyError(f"no registry entry for {plugin}/{skill}")


def _validate_document_id(document_id: str, profile_name: str, profile: dict) -> None:
    """Reject a profile that explicitly names a different document."""
    profile_document_id = profile.get("Document", {}).get("DocumentId")
    if profile_document_id and profile_document_id != document_id:
        raise ValueError(
            f"document_id={document_id!r} does not match {profile_name}'s "
            f"Document.DocumentId={profile_document_id!r}"
        )


def _resolve_invocation(spec: InvocationSpec, export_root: Path) -> ResolvedInvocation:
    """Resolve one registry entry against the filesystem and report missing files."""
    subdir = export_root / spec.export_subdir
    args = {}
    missing = []
    for path_entry in spec.required_paths:
        candidate = subdir / path_entry["filename"]
        if candidate.exists():
            args[path_entry["arg"]] = candidate
        else:
            missing.append(path_entry["filename"])

    if not missing:
        status = "AVAILABLE"
    elif args:
        status = "PARTIAL"
    else:
        status = "UNAVAILABLE"
    return ResolvedInvocation(
        plugin=spec.plugin,
        skill=spec.skill,
        status=status,
        args=args,
        missing=missing,
    )


def _overall_status(invocations: list[ResolvedInvocation]) -> str:
    """Summarize per-invocation statuses without inventing availability."""
    if all(invocation.status == "AVAILABLE" for invocation in invocations):
        return "PASS"
    if all(invocation.status == "UNAVAILABLE" for invocation in invocations):
        return "EMPTY"
    return "PARTIAL"


# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------

def resolve_workbench_paths(
    *,
    document_id: str,
    connection: dict,
    workflow_profile: dict,
    publication_profile: dict,
    workbench_root: "Path | str",
) -> PathResolutionResult:
    """Resolve `DOWNSTREAM_INVOCATIONS` into concrete paths under
    `<workbench_root>/sharepoint-exports/<document_id>/` and check each
    referenced path against the real filesystem.

    `connection` and `publication_profile` are accepted (and their
    `DocumentId`, where present, cross-checked) per the design spec's
    call for reading connection/workflow/publication config together --
    this first version does not yet derive any per-plugin argument from
    them beyond that identity check; every resolved path comes from the
    fixed export-directory convention keyed on `document_id`.

    Honest-outcomes contract: a referenced file that does not exist is
    reported `UNAVAILABLE` and never included in `args`. Each
    invocation's own status is `AVAILABLE` (all required files present),
    `PARTIAL` (some present), or `UNAVAILABLE` (none present). The
    overall result is `PASS` (every invocation `AVAILABLE`), `EMPTY`
    (no invocation has anything present), or `PARTIAL` otherwise.
    """
    _validate_document_id(document_id, "workflow_profile", workflow_profile)
    _validate_document_id(document_id, "publication_profile", publication_profile)

    export_root = Path(workbench_root) / "sharepoint-exports" / document_id
    invocations = [_resolve_invocation(spec, export_root) for spec in DOWNSTREAM_INVOCATIONS]
    overall_status = _overall_status(invocations)

    return PathResolutionResult(
        document_id=document_id, overall_status=overall_status, invocations=invocations,
    )


# ---------------------------------------------------------------------------
# Printing -- print, don't execute
# ---------------------------------------------------------------------------

def format_invocations(result: PathResolutionResult) -> str:
    """Render `result` as human-readable text listing each downstream
    plugin/skill invocation this layer resolved, its status, and its
    resolved args (or missing filenames). This function only builds a
    string -- it never runs a subprocess or imports a downstream plugin
    module."""
    lines = [
        f"Document: {result.document_id}",
        f"Overall status: {result.overall_status}",
        "",
    ]
    for invocation in result.invocations:
        lines.append(f"[{invocation.status}] {invocation.plugin} / {invocation.skill}")
        for arg_name, resolved_path in invocation.args.items():
            lines.append(f"    {arg_name} = {resolved_path}")
        if invocation.missing:
            lines.append(f"    missing: {', '.join(invocation.missing)}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
