"""
path_resolution.py
====================

Phase 9 Part B (`docs/superpowers/specs/2026-08-07-sharepoint-
collection-and-orchestration-design.md`) -- the `resolve-workbench-
paths` skill's logic.

**Layer:** sits *above* the four Phase 9 analysis plugins
(`sharepoint-discovery`, `sharepoint-schema`, `sharepoint-link-
remediation`, `sharepoint-page-modernization`) and *below* the config
artifacts `workbench-setup`'s other skills already produce (connection
config, document-workflow profile, publication profile). It reads
already-parsed dicts of those three shapes for one `DocumentId`,
resolves them into the concrete export paths each downstream plugin
skill would need, and reports which are actually present on disk.

**Resolution flows downward only.** This module never imports, calls,
or subprocess-launches any of the four downstream plugins -- see
`test_module_never_imports_downstream_plugins` in this plugin's test
suite. Referencing a plugin/skill name here is always a plain string in
`DOWNSTREAM_INVOCATIONS`, never an import. That keeps `workbench-setup`
free of any dependency on those four plugins, preserving its own
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
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


# ---------------------------------------------------------------------------
# Registry -- plain data. Every entry below names a downstream plugin/skill
# as a string, never an import. Filenames/arg-names are taken from each
# skill's own SKILL.md "Usage" section.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class InvocationSpec:
    plugin: str
    skill: str
    export_subdir: str
    required_paths: "tuple[dict, ...]"  # each: {"arg": str, "filename": str}


DOWNSTREAM_INVOCATIONS: "tuple[InvocationSpec, ...]" = (
    InvocationSpec(
        plugin="sharepoint-discovery",
        skill="analyze-page-inventory",
        export_subdir="page-inventory",
        required_paths=(
            {"arg": "inventory_path", "filename": "page-inventory.json"},
            {"arg": "rules_path", "filename": "rules.json"},
        ),
    ),
    InvocationSpec(
        plugin="sharepoint-discovery",
        skill="analyze-webpart-code",
        export_subdir="webpart-code",
        required_paths=(
            {"arg": "extract_path", "filename": "webpart-content.json"},
        ),
    ),
    InvocationSpec(
        plugin="sharepoint-discovery",
        skill="analyze-site-navigation",
        export_subdir="site-navigation",
        required_paths=(
            {"arg": "navigation_path", "filename": "navigation.json"},
        ),
    ),
    InvocationSpec(
        plugin="sharepoint-discovery",
        skill="analyze-custom-forms",
        export_subdir="custom-forms",
        required_paths=(
            {"arg": "forms_path", "filename": "forms.json"},
            {"arg": "rules_path", "filename": "rules.json"},
        ),
    ),
    InvocationSpec(
        plugin="sharepoint-discovery",
        skill="analyze-permissions",
        export_subdir="permissions",
        required_paths=(
            {"arg": "permissions_path", "filename": "permissions.json"},
        ),
    ),
    InvocationSpec(
        plugin="sharepoint-schema",
        skill="audit-schema",
        export_subdir="schema",
        required_paths=(
            {"arg": "baseline_export_dir", "filename": "baseline"},
            {"arg": "candidate_export_dir", "filename": "candidate"},
        ),
    ),
    InvocationSpec(
        plugin="sharepoint-schema",
        skill="extract-choice-fields",
        export_subdir="schema",
        required_paths=(
            {"arg": "baseline_export_dir", "filename": "baseline"},
        ),
    ),
    InvocationSpec(
        plugin="sharepoint-link-remediation",
        skill="extract-links",
        export_subdir="links",
        required_paths=(
            {"arg": "page_path", "filename": "page.aspx"},
        ),
    ),
    InvocationSpec(
        plugin="sharepoint-link-remediation",
        skill="remediate-links",
        export_subdir="links",
        required_paths=(
            {"arg": "rules_path", "filename": "rules.json"},
        ),
    ),
    InvocationSpec(
        plugin="sharepoint-link-remediation",
        skill="validate-link-integrity",
        export_subdir="links",
        required_paths=(
            {"arg": "export_dir", "filename": "export"},
        ),
    ),
    InvocationSpec(
        plugin="sharepoint-page-modernization",
        skill="analyze-aspx-pages",
        export_subdir="pages",
        required_paths=(
            {"arg": "raw_html", "filename": "classic-page.raw.html"},
            {"arg": "views", "filename": "classic-page.views.json"},
            {"arg": "overrides", "filename": "classic-page.override.json"},
        ),
    ),
    InvocationSpec(
        plugin="sharepoint-page-modernization",
        skill="convert-aspx-pages",
        export_subdir="pages",
        required_paths=(
            {"arg": "classified", "filename": "classified.json"},
        ),
    ),
    InvocationSpec(
        plugin="sharepoint-page-modernization",
        skill="compose-page-preview",
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

@dataclass
class ResolvedInvocation:
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


@dataclass
class PathResolutionResult:
    document_id: str
    overall_status: str  # "PASS" | "PARTIAL" | "EMPTY"
    invocations: "list[ResolvedInvocation]" = field(default_factory=list)


def _spec_for(plugin: str, skill: str) -> InvocationSpec:
    for spec in DOWNSTREAM_INVOCATIONS:
        if spec.plugin == plugin and spec.skill == skill:
            return spec
    raise KeyError(f"no registry entry for {plugin}/{skill}")


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
    workflow_document_id = workflow_profile.get("Document", {}).get("DocumentId")
    if workflow_document_id and workflow_document_id != document_id:
        raise ValueError(
            f"document_id={document_id!r} does not match workflow_profile's "
            f"Document.DocumentId={workflow_document_id!r}"
        )
    publication_document_id = publication_profile.get("Document", {}).get("DocumentId")
    if publication_document_id and publication_document_id != document_id:
        raise ValueError(
            f"document_id={document_id!r} does not match publication_profile's "
            f"Document.DocumentId={publication_document_id!r}"
        )

    export_root = Path(workbench_root) / "sharepoint-exports" / document_id

    invocations = []
    for spec in DOWNSTREAM_INVOCATIONS:
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

        invocations.append(ResolvedInvocation(
            plugin=spec.plugin, skill=spec.skill, status=status, args=args, missing=missing,
        ))

    if all(inv.status == "AVAILABLE" for inv in invocations):
        overall_status = "PASS"
    elif all(inv.status == "UNAVAILABLE" for inv in invocations):
        overall_status = "EMPTY"
    else:
        overall_status = "PARTIAL"

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
