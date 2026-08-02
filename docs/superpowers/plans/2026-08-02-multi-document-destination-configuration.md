# Multi-Document Destination Configuration Implementation Plan

> **PLANNING ONLY — DO NOT EXECUTE WITHOUT SEPARATE EXPLICIT AUTHORIZATION.** Per
> `docs/superpowers/specs/2026-08-02-multi-document-destination-configuration-design.md`'s Section
> 13, this design is "not authorized to implement now." Writing this plan is allowed under this
> repo's "planning is not implementation" rule (`start-here.md`'s Mandatory Planning Protocol);
> running any task below requires the user's separate, explicit go-ahead. No task in this plan
> creates a SharePoint library, page, agent, or skill, or modifies the tenant in any way — every
> deliverable is a document, a shared PowerShell module, its tests, or (Task 5) a skill-authoring
> PR description for the sibling monorepo, never tenant-side.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce the script inventory, root-config schema, publication-profile schema, and a
tested target-resolution module the design specifies — the prerequisite infrastructure for
supporting a second real document without duplicating or colliding with the first.

**Architecture:** A read-only inventory pass first (per the spec's own "do not refactor blindly"
rule), then two new schema/example files, then one new pure-function PowerShell module
(`Resolve-PublicationTarget.psm1`) with a Pester-equivalent test approach (this repo's PowerShell
scripts are tested via `pytest` + `subprocess` calls to `pwsh`, per the existing pattern in
`tools/phase-4-native-sharepoint-skills/tests/test_rollback_and_exit_gate.py` — reused here, not a
new test framework introduced). No existing script is modified in this plan — Task 6 only
identifies which ones *would* need updating, deferred to a future, separately-authorized plan.

**Tech Stack:** PowerShell 7 (module + `Export-ModuleMember` functions), Python 3 + `pytest` +
`subprocess` (calling into `pwsh -Command` for the module's tests, matching this repo's existing
cross-language test pattern).

## Global Constraints

- **No tenant modification.** No `Connect-PnPOnline`, no library/page/agent/skill creation,
  anywhere in this plan's code. The module under test takes plain data in and returns plain data
  out — it never connects to SharePoint.
- **No new skill code written directly in this repo.** Per `CLAUDE.md`'s Skill Development
  Protocol, `setup-sharepoint-connection` is authored in the sibling `agent-plugins-skills`
  monorepo, PR'd, and merged by the user — Task 5 here produces only the *specification* handed to
  that process, not `SKILL.md` content itself.
- **Coding conventions** (`.agent/rules/coding-conventions.md`): every new source file (Python
  test files, the PowerShell module) starts with a purpose header stating what it does, its key
  input dependencies, and an index of the functions/procedures it defines. Python functions use
  type hints. Extract a helper past 50 lines or 3+ nesting levels in one function.
- **Do not refactor blindly** (spec Section 10): Task 6 (script inventory) happens before any task
  that would touch an existing script's destination logic — and this plan does not include such a
  task at all, deferring it to a future plan once the inventory exists.
- Work on a dedicated branch per this repo's Per-Phase Git & Session Workflow — but per the
  PLANNING ONLY note above, do not create the branch or run any task until the user authorizes
  execution.

---

## Task 1: Script inventory matrix

**Files:**
- Create: `docs/reports/multi-document-destination-config/script-inventory-matrix.md`

**Interfaces:**
- Consumes: nothing (read-only inspection of existing scripts).
- Produces: the matrix table later tasks (and any future refactor plan) reference by script path.

- [ ] **Step 1: List every candidate script**

Run:
```bash
find tools/phase-3-sharepoint-discovery tools/phase-4-native-sharepoint-skills/deployment/scripts tools/phase-5-sharepoint-knowledge-agent-pilot -name "*.ps1" | sort
```
Expected: at least these 16 (per the design spec's Section 10 list) —
`phase-3-sharepoint-discovery/push-aspx-experiment.ps1`,
`phase-3-sharepoint-discovery/provision-agentassets.ps1`,
`phase-3-sharepoint-discovery/phase-3-0-tenant-discovery.ps1`,
`phase-3-sharepoint-discovery/run-phase3-tenant-pilot.ps1`,
`phase-4-native-sharepoint-skills/deployment/scripts/task-8-deploy-review-manual-topics.ps1`,
`.../task-8a-reconcile-deployed-skill.ps1`, `.../task-9-retrieve-topic-metadata.ps1`,
`.../task-12-rollback.ps1`, `.../rollback-skill.ps1`, `.../rollback-skill-deployment.ps1`,
`.../provision-agentassets.ps1`, `.../create-test-agent.ps1`, `.../create-corrected-agent.ps1`,
`.../create-aspx-only-agent-test.ps1`, `.../create-updated-agent-sitepages.ps1`,
`.../deploy-and-verify-skill.ps1`, `phase-5-sharepoint-knowledge-agent-pilot/upload-rendered-markdown.ps1`.

- [ ] **Step 2: For each script, record the 9 matrix columns from spec Section 10**

For each file found in Step 1, read it and record: script path; plugin/phase owner (which
`tools/phase-N-*` folder); current hardcoded values (literal library/folder/agent names found in
the script body — quote them exactly); current config dependencies (which `config.psd1`/
`tenant-config.psd1` file and which of its keys it reads); required connection parameters (does it
call `Connect-PnPOnline`, with which parameters); required operation parameters (what it currently
takes as `param()` block entries, if any); write-safety gate (does it have `-DryRun`/`-Execute`/
`-ConfirmExactTarget`, or does it write unconditionally); publication-profile support (none exist
yet — record "None (pre-dates this design)" for every script); standalone-install support (can it
run outside its own folder, or does it assume `$PSScriptRoot`-relative paths only); tests required
(does a corresponding `tests/test_*.py` already exercise it — check
`tools/phase-4-native-sharepoint-skills/tests/` by name).

- [ ] **Step 3: Write the matrix document**

Create `docs/reports/multi-document-destination-config/script-inventory-matrix.md` as a purpose
header (what this document is, why it exists, pointer to the design spec) followed by one Markdown
table with the 9 columns from Step 2, one row per script from Step 1's list. Do not summarize or
group scripts — every script gets its own row, per the spec's "inventory every script" instruction
(not a representative sample).

- [ ] **Step 4: Commit**

```bash
git add docs/reports/multi-document-destination-config/script-inventory-matrix.md
git commit -m "docs: script inventory matrix for multi-document destination config design"
```

---

## Task 2: Root config schema and example

**Corrected 2026-08-02** to match the design spec's Section 1 Layer 1 revision: three nested
sections (`Connection`, `Authentication`, `Defaults`) instead of one flat hashtable, and
artifact-specific default keys instead of one ambiguous `DefaultPublicationRoot`. Validation now
uses `Import-PowerShellDataFile` (via `pwsh`) instead of regex-on-text, per fix #7 — a regex match
proves a substring exists, not that the file is valid PowerShell data-file syntax or correctly
nested.

**Files:**
- Create: `config.psd1.example` (repo root)
- Test: `tests/test_root_config_schema.py` (repo root — new top-level `tests/` directory; this
  repo has no root-level Python test dir yet, this is the first file in it)

**Interfaces:**
- Consumes: `pwsh` on PATH (for `Import-PowerShellDataFile`).
- Produces: the `config.psd1.example` file shape Task 4's module and Task 3's profile schema both
  reference by key path (`Connection.SiteUrl`, `Connection.TenantId`, `Connection.ClientId`,
  `Connection.AuthenticationMode`, `Authentication.CertificateThumbprint`,
  `Authentication.TenantAdminUrl`, `Defaults.DefaultHumanPublicationLibrary`,
  `Defaults.DefaultAgentGroundingLibrary`, `Defaults.DefaultAgentAssetsLibrary`,
  `Defaults.DefaultSitePagesLibrary`).

- [ ] **Step 1: Write the failing test**

```python
"""
Purpose: validates the repo-root config.psd1.example template matches the corrected schema
specified in docs/superpowers/specs/2026-08-02-multi-document-destination-configuration-design.md
Section 1 (Layer 1 — root connection configuration, Connection/Authentication/Defaults sections).

Key Input Dependencies:
- config.psd1.example (repo root) — must exist and be loadable via PowerShell's
  Import-PowerShellDataFile cmdlet (pwsh must be on PATH).

Index of test functions:
- test_config_example_exists_at_repo_root
- test_config_example_loads_as_valid_powershell_data_file
- test_config_example_has_all_three_required_sections
- test_config_example_connection_section_has_mandatory_keys
- test_config_example_defaults_section_is_artifact_specific
- test_config_example_has_no_secret_looking_values
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_EXAMPLE_PATH = REPO_ROOT / "config.psd1.example"
PWSH = shutil.which("pwsh")

pytestmark = pytest.mark.skipif(PWSH is None, reason="pwsh not installed")

MANDATORY_CONNECTION_KEYS = ["SiteUrl", "TenantId", "ClientId", "AuthenticationMode"]
ARTIFACT_SPECIFIC_DEFAULT_KEYS = [
    "DefaultHumanPublicationLibrary", "DefaultAgentGroundingLibrary",
    "DefaultAgentAssetsLibrary", "DefaultSitePagesLibrary",
]


def _load_config() -> dict:
    """Load config.psd1.example via pwsh's Import-PowerShellDataFile, returned as a dict."""
    result = subprocess.run(
        [PWSH, "-NoProfile", "-Command",
         f"(Import-PowerShellDataFile -Path '{CONFIG_EXAMPLE_PATH}') | ConvertTo-Json -Depth 10"],
        capture_output=True, text=True, check=True,
    )
    return json.loads(result.stdout)


def test_config_example_exists_at_repo_root() -> None:
    """config.psd1.example must exist at the repo root, not only per-phase-folder."""
    assert CONFIG_EXAMPLE_PATH.is_file(), f"Expected {CONFIG_EXAMPLE_PATH} to exist"


def test_config_example_loads_as_valid_powershell_data_file() -> None:
    """config.psd1.example must be syntactically valid PowerShell data-file (@{...}) content."""
    config = _load_config()
    assert isinstance(config, dict)


def test_config_example_has_all_three_required_sections() -> None:
    """The corrected schema requires exactly three top-level sections, not one flat hashtable."""
    config = _load_config()
    for section in ["Connection", "Authentication", "Defaults"]:
        assert section in config, f"Missing top-level section '{section}'"


def test_config_example_connection_section_has_mandatory_keys() -> None:
    """SiteUrl, TenantId, ClientId, AuthenticationMode are unconditionally mandatory."""
    config = _load_config()
    for key in MANDATORY_CONNECTION_KEYS:
        assert key in config["Connection"], f"Missing mandatory Connection key '{key}'"


def test_config_example_defaults_section_is_artifact_specific() -> None:
    """Defaults must be per-artifact-type keys, never the old ambiguous DefaultPublicationRoot."""
    config = _load_config()
    for key in ARTIFACT_SPECIFIC_DEFAULT_KEYS:
        assert key in config["Defaults"], f"Missing artifact-specific Defaults key '{key}'"
    # The old, ambiguous generic key must not reappear.
    assert "DefaultPublicationRoot" not in config["Defaults"]


def test_config_example_has_no_secret_looking_values() -> None:
    """config.psd1.example must never contain a secret, token, or password placeholder key."""
    text = CONFIG_EXAMPLE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in ["clientsecret", "password", "accesstoken", "certificatepassword"]:
        assert forbidden not in text, f"config.psd1.example must never define '{forbidden}'"
```

- [ ] **Step 2: Run the test to confirm it fails**

Run: `python3 -m pytest tests/test_root_config_schema.py -v`
Expected: FAIL — `config.psd1.example` does not exist at the repo root yet (it currently only
exists per-phase-folder).

- [ ] **Step 3: Write `config.psd1.example`**

Create at the repo root (exact content, per the design spec's corrected Section 1 Layer 1 — this
is the consolidated, single root template; the three existing per-phase `config.psd1.example`
files are left untouched by this plan, since migrating/removing them is a future,
separately-authorized step once Task 1's inventory shows which scripts are ready to consume the
root file):

```powershell
# Copy this file to config.psd1 (repo root) and fill in real values.
# NEVER commit config.psd1 — it must be gitignored (see repo .gitignore) and stay that way.
#
# This is the root connection configuration per
# docs/superpowers/specs/2026-08-02-multi-document-destination-configuration-design.md, Section 1,
# Layer 1. It holds ONLY stable environment/authentication context and tenant-wide artifact-type
# defaults — never document-specific values (library names FOR A SPECIFIC DOCUMENT, folder names,
# agent names, overwrite decisions). Per-document destinations belong in a
# publication-profiles/<DocumentId>.publication.psd1 file instead (see
# publication-profiles/ceis-manual.publication.psd1.example for the shape).
#
# Canonical source of truth for this template (per the design spec's Section 8): the
# workbench-setup plugin's assets/config.psd1.example, once that plugin exists. This repo's copy
# is a materialized hard copy, not an independently hand-maintained duplicate.
@{
    Connection = @{
        # Target SharePoint site.
        SiteUrl            = "https://yourtenant.sharepoint.com/sites/YourSite"

        # App registration used for interactive delegated login. All four Connection keys are
        # mandatory — a script cannot connect without them.
        TenantId           = "00000000-0000-0000-0000-000000000000"
        ClientId           = "00000000-0000-0000-0000-000000000000"
        AuthenticationMode = "Interactive"
    }

    Authentication = @{
        # Conditional — only needed when AuthenticationMode requires certificate auth or a
        # distinct tenant admin URL. Leave blank for AuthenticationMode = "Interactive".
        CertificateThumbprint = ""
        TenantAdminUrl        = ""
    }

    Defaults = @{
        # Optional, artifact-specific fallbacks. A script's explicit override parameter always
        # takes precedence (see Section 1 Layer 3's precedence order) — these are tenant-wide
        # defaults, never a per-document value. Each key maps to exactly one ArtifactType; there
        # is no shared generic fallback across artifact types (see Section 6's corrected
        # resolution table).
        DefaultHumanPublicationLibrary = "KnowledgePublications"
        DefaultAgentGroundingLibrary   = "AgentGrounding"
        DefaultAgentAssetsLibrary      = "AgentAssets"
        DefaultSitePagesLibrary        = "Site Pages"
    }
}
```

- [ ] **Step 4: Run the test to confirm it passes**

Run: `python3 -m pytest tests/test_root_config_schema.py -v`
Expected: PASS (6/6).

- [ ] **Step 5: Gitignore the future real `config.psd1`**

Add to `.gitignore` (root-level entry, alongside the existing per-phase entries):
```text
# Real tenant credentials for the root connection config (multi-document destination
# configuration design) — never commit. config.psd1.example (the template) IS committed.
/config.psd1
```

- [ ] **Step 6: Commit**

```bash
git add config.psd1.example tests/test_root_config_schema.py .gitignore
git commit -m "feat: add root config.psd1.example schema and validating test"
```

---

## Task 3: Publication-profile schema and CEIS example

**Corrected 2026-08-02** per the design spec's Section 1 Layer 2 revision: `Document` now carries
`PackageIdentity` (fix #10); `NativeSkills` is explicitly documented as a reference/approval list,
never a resolvable target section (fix #3); validation uses `Import-PowerShellDataFile` instead of
regex (fix #7).

**Files:**
- Create: `publication-profiles/ceis-manual.publication.psd1.example`
- Test: `tests/test_publication_profile_schema.py`

**Interfaces:**
- Consumes: `pwsh` on PATH.
- Produces: the profile shape (`Document` including `PackageIdentity`, `HumanPublication`,
  `PagePublication`, `AgentGrounding`, `Agents`, `NativeSkills`, `Evidence` top-level keys) that
  Task 4's resolver module reads by key path.

- [ ] **Step 1: Write the failing test**

```python
"""
Purpose: validates the CEIS publication-profile example matches the corrected schema specified in
docs/superpowers/specs/2026-08-02-multi-document-destination-configuration-design.md
Section 1 (Layer 2 — per-document publication profile).

Key Input Dependencies:
- publication-profiles/ceis-manual.publication.psd1.example (repo root relative path) — must
  exist and be loadable via PowerShell's Import-PowerShellDataFile cmdlet.

Index of test functions:
- test_ceis_profile_example_exists
- test_ceis_profile_loads_as_valid_powershell_data_file
- test_ceis_profile_has_all_required_top_level_sections
- test_ceis_profile_document_id_matches_filename
- test_ceis_profile_document_has_package_identity_key
- test_ceis_profile_native_skills_is_a_reference_list_not_a_target_section
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = REPO_ROOT / "publication-profiles" / "ceis-manual.publication.psd1.example"
PWSH = shutil.which("pwsh")

pytestmark = pytest.mark.skipif(PWSH is None, reason="pwsh not installed")

REQUIRED_SECTIONS = [
    "Document", "HumanPublication", "PagePublication",
    "AgentGrounding", "Agents", "NativeSkills", "Evidence",
]


def _load_profile() -> dict:
    """Load ceis-manual.publication.psd1.example via pwsh's Import-PowerShellDataFile."""
    result = subprocess.run(
        [PWSH, "-NoProfile", "-Command",
         f"(Import-PowerShellDataFile -Path '{PROFILE_PATH}') | ConvertTo-Json -Depth 10"],
        capture_output=True, text=True, check=True,
    )
    return json.loads(result.stdout)


def test_ceis_profile_example_exists() -> None:
    """The CEIS publication-profile example file must exist at its documented path."""
    assert PROFILE_PATH.is_file(), f"Expected {PROFILE_PATH} to exist"


def test_ceis_profile_loads_as_valid_powershell_data_file() -> None:
    """The profile must be syntactically valid PowerShell data-file content."""
    profile = _load_profile()
    assert isinstance(profile, dict)


def test_ceis_profile_has_all_required_top_level_sections() -> None:
    """All 7 top-level sections from the corrected schema must be present."""
    profile = _load_profile()
    for section in REQUIRED_SECTIONS:
        assert section in profile, f"Missing top-level section '{section}'"


def test_ceis_profile_document_id_matches_filename() -> None:
    """DocumentId must equal 'ceis-manual', matching the file's own name."""
    profile = _load_profile()
    assert profile["Document"]["DocumentId"] == "ceis-manual", (
        "DocumentId must be 'ceis-manual' to match the filename ceis-manual.publication.psd1"
    )


def test_ceis_profile_document_has_package_identity_key() -> None:
    """Document must declare PackageIdentity, the third element of the composite PublicationId."""
    profile = _load_profile()
    assert "PackageIdentity" in profile["Document"], (
        "Document section must declare PackageIdentity (Section 1 Layer 2's composite "
        "PublicationId = DocumentId + PublicationProfile + PackageIdentity)"
    )


def test_ceis_profile_native_skills_is_a_reference_list_not_a_target_section() -> None:
    """NativeSkills must be an array (a reference/approval list), never a hashtable a resolver
    could mistakenly treat as one resolvable target section (the bug fix #3 corrects)."""
    profile = _load_profile()
    assert isinstance(profile["NativeSkills"], list)
```

- [ ] **Step 2: Run the test to confirm it fails**

Run: `python3 -m pytest tests/test_publication_profile_schema.py -v`
Expected: FAIL — `publication-profiles/` directory and the example file do not exist yet.

- [ ] **Step 3: Write the CEIS publication-profile example**

Create `publication-profiles/ceis-manual.publication.psd1.example` (exact content, per the design
spec's corrected Section 1 Layer 2 — using the real CEIS document, since it's the one document
this repo actually has, not a synthetic placeholder):

```powershell
# Example publication profile — copy to ceis-manual.publication.psd1 (drop the .example
# suffix) once this design is authorized for implementation. Per
# docs/superpowers/specs/2026-08-02-multi-document-destination-configuration-design.md,
# Section 1, Layer 2 — this file is project content (no secrets), tracked in git.
@{
    SchemaVersion = "1.0"

    Document = @{
        DocumentId        = "ceis-manual"
        Title             = "CEIS Manual"
        ContentType       = "Manual"
        ContentOwner      = ""
        SourcePackagePath = "runs/ceis-manual-v2"
        # PackageIdentity is the canonical package's own identity (Phase 2's package_identity) —
        # left blank in the .example template; filled in from the real canonical package's
        # manifest when a real profile is created from this template. Combined with DocumentId
        # and each section's PublicationProfile/TargetType, this forms the composite PublicationId
        # the resolver (Section 6) and collision check (Section 7) actually key on.
        PackageIdentity   = ""
    }

    HumanPublication = @{
        Enabled            = $true
        TargetType         = "DocumentLibrary"
        LibraryName        = "KnowledgePublications"
        RootFolder         = "ceis-manual"
        TopicFolder        = "topics"
        MediaFolder        = "media"
        NavigationFolder   = "navigation"
        PublicationProfile = "multipage-markdown"
    }

    PagePublication = @{
        Enabled            = $false
        TargetType         = "SitePages"
        LibraryName        = "Site Pages"
        RootFolder         = "ceis-manual"
        PageTemplate       = ""
        PageNamePattern    = "{TopicId}.aspx"
    }

    AgentGrounding = @{
        Enabled            = $true
        LibraryName        = "AgentGrounding"
        RootFolder         = "ceis-manual"
        GroundingProfile   = "manual-grounding"
    }

    Agents = @(
        @{
            Enabled             = $true
            AgentId             = "ceis-knowledge-agent"
            AgentName           = "CEIS Knowledge Agent"
            AgentTemplate       = ""
            KnowledgeTargets    = @("HumanPublication")
            IncludeNativeSkills = $false
            Skills              = @()
        }
    )

    # NativeSkills is a reference/approval list ONLY — it names which already-deployed skills
    # this document's agents may use. It is never resolved as a target section itself: resolving
    # a NativeSkill's own deployment location takes an exact -SkillName parameter and resolves
    # against Defaults.DefaultAgentAssetsLibrary (see Section 6's corrected resolution table),
    # not against anything in this array's shape.
    NativeSkills = @(
        # @{ SkillName = "review-manual-topics"; Approved = $true }
    )

    Evidence = @{
        OutputPath = "docs/reports/publications/ceis-manual"
    }
}
```

- [ ] **Step 4: Run the test to confirm it passes**

Run: `python3 -m pytest tests/test_publication_profile_schema.py -v`
Expected: PASS (6/6).

- [ ] **Step 5: Commit**

```bash
git add publication-profiles/ceis-manual.publication.psd1.example tests/test_publication_profile_schema.py
git commit -m "feat: add publication-profile schema example for the CEIS Manual"
```

---

## Task 4: Target-resolution PowerShell module

**Corrected 2026-08-02** per the design spec's Section 6 revision: artifact-specific defaults
instead of one shared `DefaultPublicationRoot` fallback (fix #4); a `PublicationId` composite
returned alongside the resolved target (fix #10); and path-safety rejection — traversal, absolute
paths, empty segments, `DocumentId`-boundary escape — instead of silent normalization (fix #6).

**Files:**
- Create: `tools/shared/Resolve-PublicationTarget.psm1`
- Test: `tests/test_resolve_publication_target.py`

**Interfaces:**
- Consumes: parsed root config hashtable (Task 2's nested `Connection`/`Authentication`/`Defaults`
  shape) and parsed publication-profile hashtable (Task 3's shape, including
  `Document.PackageIdentity`), plus explicit override parameters, as plain PowerShell
  hashtables/strings — never connects to SharePoint itself.
- Produces: `Resolve-PublicationTarget` — a PowerShell function with this signature, importable by
  any future script via `Import-Module ./tools/shared/Resolve-PublicationTarget.psm1`:
  ```powershell
  function Resolve-PublicationTarget {
      param(
          [Parameter(Mandatory)][hashtable]$RootConfig,
          [Parameter(Mandatory)][hashtable]$PublicationProfile,
          [Parameter(Mandatory)][ValidateSet("HumanTopic", "Media", "AgentGrounding", "AspxPage", "NativeSkill")][string]$ArtifactType,
          [string]$OverrideLibraryName,
          [string]$OverrideRootFolder,
          [string]$RelativeItemPath
      )
      # Returns a hashtable: @{ SiteUrl; LibraryName; RootFolder; PublicationId; ResolvedTarget; Sources }
      # where Sources maps each resolved field name to one of:
      # "OverrideParameter" | "PublicationProfile" | "RootConfig" | "Default"
      # PublicationId = "<DocumentId>::<PublicationProfile-or-TargetType>::<PackageIdentity>"
  }
  ```

- [ ] **Step 1: Write the failing test**

```python
"""
Purpose: validates the Resolve-PublicationTarget PowerShell module (tools/shared/
Resolve-PublicationTarget.psm1) implements the corrected target-resolution algorithm from
docs/superpowers/specs/2026-08-02-multi-document-destination-configuration-design.md
Section 6 — artifact-specific defaults, PublicationId composite, path-safety rejection. Never
connects to SharePoint, pure data in/data out.

Key Input Dependencies:
- pwsh (PowerShell 7) must be on PATH — confirmed present this session (pwsh 7.7.0-preview.3).
- tools/shared/Resolve-PublicationTarget.psm1 (the module under test).

Index of test functions:
- test_resolves_human_topic_target_from_profile_defaults
- test_resolves_media_target_with_explicit_override
- test_resolution_sources_are_recorded_per_field
- test_artifact_specific_default_used_not_shared_fallback
- test_agent_grounding_never_falls_back_to_human_publication_default
- test_missing_required_value_fails_closed_not_silent_default
- test_path_traversal_segment_rejected
- test_absolute_item_path_rejected
- test_document_id_boundary_escape_rejected
- test_publication_id_composite_is_returned
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "tools" / "shared" / "Resolve-PublicationTarget.psm1"
PWSH = shutil.which("pwsh")

pytestmark = pytest.mark.skipif(PWSH is None, reason="pwsh not installed")


def _run_resolve(ps_args: str) -> dict:
    """Import the module under test and run the given PowerShell snippet, parsing its JSON stdout."""
    script = f"""
    Import-Module '{MODULE_PATH}' -Force
    {ps_args}
    """
    result = subprocess.run(
        [PWSH, "-NoProfile", "-Command", script],
        capture_output=True, text=True, check=True,
    )
    return json.loads(result.stdout)


def _base_root() -> str:
    """Return a PowerShell snippet defining $root with all four artifact-specific defaults set."""
    return """
    $root = @{
        Connection = @{ SiteUrl = "https://tenant.sharepoint.com/sites/site" }
        Defaults   = @{
            DefaultHumanPublicationLibrary = "KnowledgePublications"
            DefaultAgentGroundingLibrary   = "AgentGrounding"
            DefaultAgentAssetsLibrary      = "AgentAssets"
            DefaultSitePagesLibrary        = "Site Pages"
        }
    }
    """


def test_resolves_human_topic_target_from_profile_defaults() -> None:
    """A HumanTopic target resolves from the profile's own LibraryName/RootFolder/TopicFolder."""
    result = _run_resolve(_base_root() + """
        $profile = @{
            Document = @{ DocumentId = "ceis-manual"; PackageIdentity = "sha256:abc" }
            HumanPublication = @{ LibraryName = "KnowledgePublications"; RootFolder = "ceis-manual"; TopicFolder = "topics"; PublicationProfile = "multipage-markdown" }
        }
        $r = Resolve-PublicationTarget -RootConfig $root -PublicationProfile $profile -ArtifactType HumanTopic -RelativeItemPath "topic-001.md"
        $r | ConvertTo-Json -Depth 10
    """)
    assert result["LibraryName"] == "KnowledgePublications"
    assert result["ResolvedTarget"] == "KnowledgePublications/ceis-manual/topics/topic-001.md"


def test_resolves_media_target_with_explicit_override() -> None:
    """An explicit -OverrideLibraryName takes precedence over the profile's own LibraryName."""
    result = _run_resolve(_base_root() + """
        $profile = @{
            Document = @{ DocumentId = "ceis-manual"; PackageIdentity = "sha256:abc" }
            HumanPublication = @{ LibraryName = "KnowledgePublications"; RootFolder = "ceis-manual"; MediaFolder = "media"; PublicationProfile = "multipage-markdown" }
        }
        $r = Resolve-PublicationTarget -RootConfig $root -PublicationProfile $profile -ArtifactType Media -OverrideLibraryName "OverriddenLibrary" -RelativeItemPath "image-001.png"
        $r | ConvertTo-Json -Depth 10
    """)
    assert result["LibraryName"] == "OverriddenLibrary"
    assert result["Sources"]["LibraryName"] == "OverrideParameter"


def test_resolution_sources_are_recorded_per_field() -> None:
    """Each resolved field records which layer (RootConfig/PublicationProfile/etc.) supplied it."""
    result = _run_resolve(_base_root() + """
        $profile = @{
            Document = @{ DocumentId = "ceis-manual"; PackageIdentity = "sha256:abc" }
            HumanPublication = @{ RootFolder = "ceis-manual"; TopicFolder = "topics"; PublicationProfile = "multipage-markdown" }
        }
        $r = Resolve-PublicationTarget -RootConfig $root -PublicationProfile $profile -ArtifactType HumanTopic -RelativeItemPath "topic-001.md"
        $r | ConvertTo-Json -Depth 10
    """)
    assert result["Sources"]["LibraryName"] == "RootConfig"
    assert result["Sources"]["RootFolder"] == "PublicationProfile"


def test_artifact_specific_default_used_not_shared_fallback() -> None:
    """AgentGrounding with no explicit LibraryName must resolve from
    Defaults.DefaultAgentGroundingLibrary, never Defaults.DefaultHumanPublicationLibrary."""
    result = _run_resolve(_base_root() + """
        $profile = @{
            Document = @{ DocumentId = "ceis-manual"; PackageIdentity = "sha256:abc" }
            AgentGrounding = @{ RootFolder = "ceis-manual"; GroundingProfile = "manual-grounding" }
        }
        $r = Resolve-PublicationTarget -RootConfig $root -PublicationProfile $profile -ArtifactType AgentGrounding -RelativeItemPath "grounding.md"
        $r | ConvertTo-Json -Depth 10
    """)
    assert result["LibraryName"] == "AgentGrounding"


def test_agent_grounding_never_falls_back_to_human_publication_default() -> None:
    """If DefaultAgentGroundingLibrary is absent, resolution must fail closed — it must NOT
    silently borrow DefaultHumanPublicationLibrary just because one default exists."""
    with pytest.raises(subprocess.CalledProcessError):
        _run_resolve("""
            $root = @{
                Connection = @{ SiteUrl = "https://tenant.sharepoint.com/sites/site" }
                Defaults   = @{ DefaultHumanPublicationLibrary = "KnowledgePublications" }
            }
            $profile = @{
                Document = @{ DocumentId = "ceis-manual"; PackageIdentity = "sha256:abc" }
                AgentGrounding = @{ RootFolder = "ceis-manual" }
            }
            Resolve-PublicationTarget -RootConfig $root -PublicationProfile $profile -ArtifactType AgentGrounding -RelativeItemPath "grounding.md" -ErrorAction Stop
        """)


def test_missing_required_value_fails_closed_not_silent_default() -> None:
    """With no override, no profile LibraryName, and no matching root default, resolution must
    raise rather than guess a target."""
    with pytest.raises(subprocess.CalledProcessError):
        _run_resolve("""
            $root = @{ Connection = @{ SiteUrl = "https://tenant.sharepoint.com/sites/site" }; Defaults = @{} }
            $profile = @{ Document = @{ DocumentId = "ceis-manual"; PackageIdentity = "sha256:abc" }; HumanPublication = @{} }
            Resolve-PublicationTarget -RootConfig $root -PublicationProfile $profile -ArtifactType HumanTopic -RelativeItemPath "topic-001.md" -ErrorAction Stop
        """)


def test_path_traversal_segment_rejected() -> None:
    """A RelativeItemPath containing '..' must be rejected, never silently normalized."""
    with pytest.raises(subprocess.CalledProcessError):
        _run_resolve(_base_root() + """
            $profile = @{
                Document = @{ DocumentId = "ceis-manual"; PackageIdentity = "sha256:abc" }
                HumanPublication = @{ LibraryName = "KnowledgePublications"; RootFolder = "ceis-manual"; TopicFolder = "topics"; PublicationProfile = "multipage-markdown" }
            }
            Resolve-PublicationTarget -RootConfig $root -PublicationProfile $profile -ArtifactType HumanTopic -RelativeItemPath "../other-document/secret.md" -ErrorAction Stop
        """)


def test_absolute_item_path_rejected() -> None:
    """A RelativeItemPath that is actually absolute must be rejected."""
    with pytest.raises(subprocess.CalledProcessError):
        _run_resolve(_base_root() + """
            $profile = @{
                Document = @{ DocumentId = "ceis-manual"; PackageIdentity = "sha256:abc" }
                HumanPublication = @{ LibraryName = "KnowledgePublications"; RootFolder = "ceis-manual"; TopicFolder = "topics"; PublicationProfile = "multipage-markdown" }
            }
            Resolve-PublicationTarget -RootConfig $root -PublicationProfile $profile -ArtifactType HumanTopic -RelativeItemPath "/etc/passwd" -ErrorAction Stop
        """)


def test_document_id_boundary_escape_rejected() -> None:
    """An explicit RootFolder override that names a DIFFERENT DocumentId's folder must be
    rejected — a script must not be able to write outside its own document's boundary."""
    with pytest.raises(subprocess.CalledProcessError):
        _run_resolve(_base_root() + """
            $profile = @{
                Document = @{ DocumentId = "ceis-manual"; PackageIdentity = "sha256:abc" }
                HumanPublication = @{ LibraryName = "KnowledgePublications"; TopicFolder = "topics"; PublicationProfile = "multipage-markdown" }
            }
            Resolve-PublicationTarget -RootConfig $root -PublicationProfile $profile -ArtifactType HumanTopic -OverrideRootFolder "small-claims-manual" -RelativeItemPath "topic-001.md" -ErrorAction Stop
        """)


def test_publication_id_composite_is_returned() -> None:
    """The resolved result includes PublicationId = DocumentId::PublicationProfile::PackageIdentity."""
    result = _run_resolve(_base_root() + """
        $profile = @{
            Document = @{ DocumentId = "ceis-manual"; PackageIdentity = "sha256:abc" }
            HumanPublication = @{ LibraryName = "KnowledgePublications"; RootFolder = "ceis-manual"; TopicFolder = "topics"; PublicationProfile = "multipage-markdown" }
        }
        $r = Resolve-PublicationTarget -RootConfig $root -PublicationProfile $profile -ArtifactType HumanTopic -RelativeItemPath "topic-001.md"
        $r | ConvertTo-Json -Depth 10
    """)
    assert result["PublicationId"] == "ceis-manual::multipage-markdown::sha256:abc"
```

- [ ] **Step 2: Run the tests to confirm they fail**

Run: `python3 -m pytest tests/test_resolve_publication_target.py -v`
Expected: FAIL — `tools/shared/Resolve-PublicationTarget.psm1` does not exist yet
(`Import-Module` error).

- [ ] **Step 3: Write the module**

Create `tools/shared/Resolve-PublicationTarget.psm1`:

```powershell
<#
.SYNOPSIS
    Purpose: resolves an exact SharePoint destination target from a root connection config,
    a per-document publication profile, and explicit override parameters, per the precedence
    order and artifact-specific-default rules in
    docs/superpowers/specs/2026-08-02-multi-document-destination-configuration-design.md
    Section 6 (explicit parameter -> publication profile -> root config Default for THIS
    artifact type only -> fail closed). Also enforces path safety and returns the composite
    PublicationId (Section 1 Layer 2 / Section 7).

    Key input dependencies: none at import time. At call time, takes plain hashtables (parsed
    from config.psd1 / publication-profiles/<id>.publication.psd1 by the caller) — this module
    never calls Connect-PnPOnline or reads a file itself, so it is fully unit-testable without
    a live tenant connection.

    Index of exported functions:
    - Resolve-PublicationTarget: the single entry point described above.
#>

function Resolve-PublicationTarget {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][hashtable]$RootConfig,
        [Parameter(Mandatory)][hashtable]$PublicationProfile,
        [Parameter(Mandatory)][ValidateSet("HumanTopic", "Media", "AgentGrounding", "AspxPage", "NativeSkill")][string]$ArtifactType,
        [string]$OverrideLibraryName,
        [string]$OverrideRootFolder,
        [string]$RelativeItemPath
    )

    $documentId = $PublicationProfile.Document.DocumentId
    if ([string]::IsNullOrWhiteSpace($documentId)) {
        Write-Error "PublicationProfile.Document.DocumentId is required and was empty." -ErrorAction Stop
        return
    }

    # Artifact-specific section AND artifact-specific default key — never a shared fallback.
    $section = switch ($ArtifactType) {
        "HumanTopic"     { $PublicationProfile.HumanPublication }
        "Media"          { $PublicationProfile.HumanPublication }
        "AgentGrounding" { $PublicationProfile.AgentGrounding }
        "AspxPage"       { $PublicationProfile.PagePublication }
        "NativeSkill"    { $null }  # Resolved against Defaults.DefaultAgentAssetsLibrary only;
                                     # NativeSkills is a reference/approval list, never a target section.
    }
    $defaultKey = switch ($ArtifactType) {
        "HumanTopic"     { "DefaultHumanPublicationLibrary" }
        "Media"          { "DefaultHumanPublicationLibrary" }
        "AgentGrounding" { "DefaultAgentGroundingLibrary" }
        "AspxPage"       { "DefaultSitePagesLibrary" }
        "NativeSkill"    { "DefaultAgentAssetsLibrary" }
    }

    $sources = @{}

    if ($OverrideLibraryName) {
        $libraryName = $OverrideLibraryName
        $sources["LibraryName"] = "OverrideParameter"
    } elseif ($section -and $section.LibraryName) {
        $libraryName = $section.LibraryName
        $sources["LibraryName"] = "PublicationProfile"
    } elseif ($RootConfig.Defaults -and $RootConfig.Defaults[$defaultKey]) {
        $libraryName = $RootConfig.Defaults[$defaultKey]
        $sources["LibraryName"] = "RootConfig"
    } else {
        Write-Error "No LibraryName resolvable for ArtifactType '$ArtifactType' — checked override, profile, and RootConfig.Defaults.$defaultKey. Refusing to borrow a different artifact type's default." -ErrorAction Stop
        return
    }

    if ($OverrideRootFolder) {
        $rootFolder = $OverrideRootFolder
        $sources["RootFolder"] = "OverrideParameter"
        # Path-safety: an override must not name a different document's folder.
        if ($rootFolder -ne $documentId) {
            Write-Error "OverrideRootFolder '$rootFolder' does not match this profile's DocumentId '$documentId' — refusing to write outside this document's boundary." -ErrorAction Stop
            return
        }
    } elseif ($section -and $section.RootFolder) {
        $rootFolder = $section.RootFolder
        $sources["RootFolder"] = "PublicationProfile"
    } else {
        $rootFolder = $documentId
        $sources["RootFolder"] = "Default"
    }

    $subFolder = switch ($ArtifactType) {
        "HumanTopic" { $section.TopicFolder }
        "Media"      { $section.MediaFolder }
        default      { $null }
    }

    # Path safety on the caller-supplied relative item path.
    if ($RelativeItemPath) {
        if ($RelativeItemPath -match '\.\.' ) {
            Write-Error "RelativeItemPath '$RelativeItemPath' contains a path-traversal segment ('..') — rejected." -ErrorAction Stop
            return
        }
        if ($RelativeItemPath.StartsWith("/") -or $RelativeItemPath -match '^[A-Za-z]:[\\/]') {
            Write-Error "RelativeItemPath '$RelativeItemPath' is an absolute path — rejected, only relative item paths are accepted." -ErrorAction Stop
            return
        }
        if ($RelativeItemPath -match '//' -or $RelativeItemPath -match '\\\\') {
            Write-Error "RelativeItemPath '$RelativeItemPath' contains duplicate path separators — rejected." -ErrorAction Stop
            return
        }
    }

    $pathParts = @($libraryName, $rootFolder)
    if ($subFolder) { $pathParts += $subFolder }
    if ($RelativeItemPath) { $pathParts += $RelativeItemPath }
    $resolvedTarget = ($pathParts -join "/")

    $publicationProfileOrTargetType = if ($section -and $section.PublicationProfile) {
        $section.PublicationProfile
    } elseif ($section -and $section.TargetType) {
        $section.TargetType
    } else {
        $ArtifactType
    }
    $publicationId = "$documentId" + "::" + "$publicationProfileOrTargetType" + "::" + "$($PublicationProfile.Document.PackageIdentity)"

    return @{
        SiteUrl        = $RootConfig.Connection.SiteUrl
        LibraryName    = $libraryName
        RootFolder     = $rootFolder
        PublicationId  = $publicationId
        ResolvedTarget = $resolvedTarget
        Sources        = $sources
    }
}

Export-ModuleMember -Function Resolve-PublicationTarget
```

- [ ] **Step 4: Run the tests to confirm they pass**

Run: `python3 -m pytest tests/test_resolve_publication_target.py -v`
Expected: PASS (10/10).

- [ ] **Step 5: Commit**

```bash
git add tools/shared/Resolve-PublicationTarget.psm1 tests/test_resolve_publication_target.py
git commit -m "feat: add Resolve-PublicationTarget module with artifact-specific defaults, PublicationId, and path safety"
```

---

## Task 5: Collision-prevention validation in the same module

**Corrected 2026-08-02** per the design spec's Section 7 revision (fix #5): collision identity is
the tuple **normalized `SiteUrl` + `LibraryName` + normalized path**, not the raw `ResolvedTarget`
string alone — two different sites resolving to a visually identical path must never be flagged as
colliding, and the corrected schema's nested `RootConfig.Connection.SiteUrl` (Task 2/4) is what
this task's tests now use, not the old flat `$root.SiteUrl`.

**Files:**
- Modify: `tools/shared/Resolve-PublicationTarget.psm1`
- Test: `tests/test_resolve_publication_target.py` (extend from Task 4)

**Interfaces:**
- Consumes: `Resolve-PublicationTarget`'s output shape from Task 4 (including `SiteUrl` and
  `ResolvedTarget`).
- Produces: a second exported function, `Test-PublicationTargetCollision`:
  ```powershell
  function Test-PublicationTargetCollision {
      param(
          [Parameter(Mandatory)][hashtable]$ProposedTarget,   # output of Resolve-PublicationTarget
          [Parameter(Mandatory)][hashtable[]]$ExistingTargets  # array of prior Resolve-PublicationTarget outputs
      )
      # Returns $true only when normalized SiteUrl + LibraryName + normalized path all match an
      # existing target — never on ResolvedTarget string equality alone. Used before any write.
  }
  ```

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_resolve_publication_target.py`:

```python
def test_collision_detected_for_identical_resolved_target() -> None:
    """Two documents resolving to the same site + library + path must be flagged as colliding."""
    result = _run_resolve(_base_root() + """
        $profileA = @{ Document = @{ DocumentId = "ceis-manual"; PackageIdentity = "sha256:aaa" }; HumanPublication = @{ LibraryName = "KnowledgePublications"; RootFolder = "ceis-manual"; TopicFolder = "topics"; PublicationProfile = "multipage-markdown" } }
        $profileB = @{ Document = @{ DocumentId = "small-claims-manual"; PackageIdentity = "sha256:bbb" }; HumanPublication = @{ LibraryName = "KnowledgePublications"; RootFolder = "ceis-manual"; TopicFolder = "topics"; PublicationProfile = "multipage-markdown" } }
        $targetA = Resolve-PublicationTarget -RootConfig $root -PublicationProfile $profileA -ArtifactType HumanTopic -RelativeItemPath "topic-001.md"
        $targetB = Resolve-PublicationTarget -RootConfig $root -PublicationProfile $profileB -ArtifactType HumanTopic -RelativeItemPath "topic-001.md"
        $collision = Test-PublicationTargetCollision -ProposedTarget $targetB -ExistingTargets @($targetA)
        @{ Collision = $collision } | ConvertTo-Json -Depth 10
    """)
    assert result["Collision"] is True


def test_no_collision_for_different_document_folders() -> None:
    """Two documents resolving to different RootFolders under the same library never collide."""
    result = _run_resolve(_base_root() + """
        $profileA = @{ Document = @{ DocumentId = "ceis-manual"; PackageIdentity = "sha256:aaa" }; HumanPublication = @{ LibraryName = "KnowledgePublications"; RootFolder = "ceis-manual"; TopicFolder = "topics"; PublicationProfile = "multipage-markdown" } }
        $profileB = @{ Document = @{ DocumentId = "small-claims-manual"; PackageIdentity = "sha256:bbb" }; HumanPublication = @{ LibraryName = "KnowledgePublications"; RootFolder = "small-claims-manual"; TopicFolder = "topics"; PublicationProfile = "multipage-markdown" } }
        $targetA = Resolve-PublicationTarget -RootConfig $root -PublicationProfile $profileA -ArtifactType HumanTopic -RelativeItemPath "topic-001.md"
        $targetB = Resolve-PublicationTarget -RootConfig $root -PublicationProfile $profileB -ArtifactType HumanTopic -RelativeItemPath "topic-001.md"
        $collision = Test-PublicationTargetCollision -ProposedTarget $targetB -ExistingTargets @($targetA)
        @{ Collision = $collision } | ConvertTo-Json -Depth 10
    """)
    assert result["Collision"] is False


def test_no_collision_for_identical_path_on_different_sites() -> None:
    """Fix #5: an identical library+path resolved under two different SiteUrls must NOT be
    flagged as colliding — collision identity includes the site, not just the path string."""
    result = _run_resolve("""
        $rootSiteA = @{
            Connection = @{ SiteUrl = "https://tenant.sharepoint.com/sites/site-a" }
            Defaults   = @{ DefaultHumanPublicationLibrary = "KnowledgePublications" }
        }
        $rootSiteB = @{
            Connection = @{ SiteUrl = "https://tenant.sharepoint.com/sites/site-b" }
            Defaults   = @{ DefaultHumanPublicationLibrary = "KnowledgePublications" }
        }
        $profile = @{ Document = @{ DocumentId = "ceis-manual"; PackageIdentity = "sha256:aaa" }; HumanPublication = @{ LibraryName = "KnowledgePublications"; RootFolder = "ceis-manual"; TopicFolder = "topics"; PublicationProfile = "multipage-markdown" } }
        $targetA = Resolve-PublicationTarget -RootConfig $rootSiteA -PublicationProfile $profile -ArtifactType HumanTopic -RelativeItemPath "topic-001.md"
        $targetB = Resolve-PublicationTarget -RootConfig $rootSiteB -PublicationProfile $profile -ArtifactType HumanTopic -RelativeItemPath "topic-001.md"
        $collision = Test-PublicationTargetCollision -ProposedTarget $targetB -ExistingTargets @($targetA)
        @{ Collision = $collision } | ConvertTo-Json -Depth 10
    """)
    assert result["Collision"] is False
```

- [ ] **Step 2: Run the tests to confirm they fail**

Run: `python3 -m pytest tests/test_resolve_publication_target.py -v`
Expected: the 3 new tests FAIL (`Test-PublicationTargetCollision` not defined); the 10 from Task 4
still PASS.

- [ ] **Step 3: Add the function to the module**

Append to `tools/shared/Resolve-PublicationTarget.psm1`, before the `Export-ModuleMember` line, and
update that line to export both functions:

```powershell
function Test-PublicationTargetCollision {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][hashtable]$ProposedTarget,
        [Parameter(Mandatory)][hashtable[]]$ExistingTargets
    )
    # Collision identity per Section 7: normalized SiteUrl + LibraryName + normalized path —
    # never ResolvedTarget string equality alone, which would ignore the site entirely.
    $proposedSite = $ProposedTarget.SiteUrl.TrimEnd("/").ToLowerInvariant()
    $proposedLibrary = $ProposedTarget.LibraryName.ToLowerInvariant()
    $proposedPath = $ProposedTarget.ResolvedTarget.TrimStart("/").ToLowerInvariant()

    foreach ($existing in $ExistingTargets) {
        $existingSite = $existing.SiteUrl.TrimEnd("/").ToLowerInvariant()
        $existingLibrary = $existing.LibraryName.ToLowerInvariant()
        $existingPath = $existing.ResolvedTarget.TrimStart("/").ToLowerInvariant()

        if ($existingSite -eq $proposedSite -and
            $existingLibrary -eq $proposedLibrary -and
            $existingPath -eq $proposedPath) {
            return $true
        }
    }
    return $false
}
```

Change the final line to:
```powershell
Export-ModuleMember -Function Resolve-PublicationTarget, Test-PublicationTargetCollision
```

- [ ] **Step 4: Run the tests to confirm they all pass**

Run: `python3 -m pytest tests/test_resolve_publication_target.py -v`
Expected: PASS (13/13).

- [ ] **Step 5: Commit**

```bash
git add tools/shared/Resolve-PublicationTarget.psm1 tests/test_resolve_publication_target.py
git commit -m "feat: add Test-PublicationTargetCollision with SiteUrl+library+path identity"
```

---

## Task 6: `setup-sharepoint-connection` skill specification (for the sibling monorepo)

**Corrected 2026-08-02** per the design spec's Section 8 revision: the original spec text
self-contradicted ("never connects to SharePoint" vs. an optional read-only validation mentioned
in the same breath) — fix #8 resolves this as generate-only-by-default plus an explicit, separate
opt-in flag. Also states exactly which keys are mandatory vs. conditional vs. optional (only four
are unconditionally mandatory, not "six required keys" as the original draft loosely claimed), and
records canonical-template ownership (fix #9): this repo's `config.psd1.example` is a materialized
copy of the `workbench-setup` plugin's own canonical asset, not an independent duplicate to
hand-maintain in two places.

**Files:**
- Create: `docs/reports/multi-document-destination-config/setup-sharepoint-connection-skill-spec.md`

**Interfaces:**
- Consumes: Task 2's `config.psd1.example` shape (the skill's output must match it exactly).
- Produces: a specification document to hand to a future session working in the sibling
  `agent-plugins-skills` monorepo — this task does NOT create `SKILL.md` content, per this repo's
  `CLAUDE.md` Skill Development Protocol (new skills are authored there, PR'd, and merged by the
  user, never written directly in this repo).

- [ ] **Step 1: Write the skill specification document**

Create `docs/reports/multi-document-destination-config/setup-sharepoint-connection-skill-spec.md`
with a purpose header, then these sections:

**Purpose** — interviews the user and writes `config.psd1` at the repo root using Task 2's
`config.psd1.example` as the template to fill in. Mandatory questions (all four, unconditionally):
`Connection.SiteUrl`, `Connection.TenantId`, `Connection.ClientId`,
`Connection.AuthenticationMode`. Conditional questions (asked only when `AuthenticationMode`
requires them): `Authentication.CertificateThumbprint`, `Authentication.TenantAdminUrl`. Optional
questions (offered with sensible defaults, user may accept or override):
`Defaults.DefaultHumanPublicationLibrary`, `Defaults.DefaultAgentGroundingLibrary`,
`Defaults.DefaultAgentAssetsLibrary`, `Defaults.DefaultSitePagesLibrary`.

**Default behavior vs. explicit opt-in** — generating `config.psd1` is the default action and
never connects to SharePoint. A separate, explicit `-TestConnection` flag performs a read-only
validation (e.g. a single `Get-PnPWeb` call) only after the user deliberately passes that flag —
the skill must never connect as a side effect of the default generate-only path.

**Canonical template ownership** — the `workbench-setup` plugin owns `assets/config.psd1.example`
as the single hand-maintained source of truth. This repo's root `config.psd1.example` (Task 2) is
a materialized hard copy produced by that plugin's installer, following the same
hub-and-spoke/installer-materializes-a-real-copy pattern this repo's own `CLAUDE.md` already
requires for in-repo plugin resource sharing (`symlink_manager.py`) — here applied across the
repo/plugin boundary via an installer copy step, since a filesystem symlink cannot cross that
boundary. Never hand-edit this repo's `config.psd1.example` independently of the plugin's asset
once the plugin exists.

**Non-goals** — never writes a real secret to any tracked file; never connects to SharePoint
during the default generate-only flow.

**Output contract** — the filled-in `config.psd1`, gitignored, matching Task 2's corrected schema
exactly (three nested sections: `Connection`, `Authentication`, `Defaults`).

**Where this is authored** — sibling `agent-plugins-skills` monorepo, per this repo's `CLAUDE.md`
Skill Development Protocol: TDD first, feature branch, PR, user-merged, then installed here via
`plugin_add.py` against the local checkout.

**Acceptance criteria** for that future authoring session: a fresh repo with only
`config.psd1.example` present ends up, after running the skill's default (non-`-TestConnection`)
path, with a valid `config.psd1` whose four mandatory `Connection.*` keys are all non-empty and
match exactly what the user typed — no placeholder text left in the file, and no network call was
made during generation. A second acceptance test: running with `-TestConnection` performs exactly
one read-only validation call and reports success/failure without writing anything.

- [ ] **Step 2: Commit**

```bash
git add docs/reports/multi-document-destination-config/setup-sharepoint-connection-skill-spec.md
git commit -m "docs: setup-sharepoint-connection skill spec for sibling-monorepo authoring"
```

---

## Self-review notes

**Corrected 2026-08-02 (external review, 12 concrete defects):** Tasks 2-6 were rewritten in place
to fix: (1) config schema mixing connection/destination concerns → `Connection`/`Authentication`/
`Defaults` split; (2) ambiguous `DefaultPublicationRoot` → four artifact-specific `Default*Library`
keys; (3) `NativeSkills` treated as a resolvable target section → explicitly a reference/approval
list only, resolved via `-SkillName` against `DefaultAgentAssetsLibrary`; (4) shared fallback
across artifact types → per-`ArtifactType` default keys, fails closed if the specific one is
absent; (5) collision identity on path string alone → `SiteUrl` + `LibraryName` + path tuple; (6)
no path-safety checks → traversal/absolute-path/`DocumentId`-boundary rejection added to the
resolver; (7) regex-only `.psd1` validation → `Import-PowerShellDataFile`-based tests throughout;
(8) self-contradictory setup-skill connection behavior → generate-only default +
explicit-opt-in `-TestConnection`; (9) two independently hand-maintained templates → one canonical
source (`workbench-setup` plugin), this repo's copy is a materialized hard copy; (10) no way to
distinguish a document's multiple simultaneous representations → `PackageIdentity` +
`PublicationId` composite added to `Document`/resolver/collision check. (11)/(12) (operation
params stay script-level; precedence order preserved) were already correct in the original draft,
confirmed unchanged.

- **Spec coverage:** Section 1 Layer 1 → Task 2; Layer 2 → Task 3; Layer 3 (parameter precedence)
  → Task 4's resolution-source tracking; Section 6 (target-resolution algorithm, now
  artifact-specific + path-safe + PublicationId-emitting) → Task 4; Section 7 (collision
  prevention, now SiteUrl-aware) → Task 5; Section 8 (setup plugin, now non-contradictory) → Task
  6; Section 10 (script inventory) → Task 1. Sections 2-3 (parameter contracts for future script
  updates), 9 (agent-assisted setup behavior), and 12 (republication compatibility) are
  deliberately not separate tasks here — they describe conventions for scripts not yet identified
  (Section 2-3) or a future phase's behavior (Section 9, 12), not buildable artifacts this plan can
  produce today; Task 1's inventory is the prerequisite that would turn Sections 2-3 into real
  per-script tasks in a later, separately-authorized plan.
- **No placeholders:** every code block is complete, runnable content — no "TODO"/"fill in later."
  Task 6 deliberately produces a specification document, not skill code, which is the correct
  non-placeholder output given the sibling-monorepo constraint (the spec IS the deliverable, not a
  stand-in for one).
- **Type/signature consistency:** `Resolve-PublicationTarget`'s return shape (`SiteUrl`,
  `LibraryName`, `RootFolder`, `PublicationId`, `ResolvedTarget`, `Sources`) is defined once in
  Task 4 and consumed identically by Task 5's `Test-PublicationTargetCollision` (matches on the
  `SiteUrl`+`LibraryName`+`ResolvedTarget` tuple, per the corrected Section 7) — no drift between
  the two tasks' field names.
- **Coding-conventions compliance — verified against the actual enforcement script** (`.agents/
  skills/coding-conventions-agent/scripts/workspace_conventions_auditor.py`'s `scan_python_file`,
  not just the summary rule doc), and two real gaps found and fixed by this correction pass:
  (a) the header wording "Key input dependency:" (singular) does not satisfy the auditor's exact
  substring check for `"key input dependencies:"` or `"dependencies:"` — every Python test file's
  header now reads "Key Input Dependencies:" (plural); (b) the auditor requires **every function**
  to carry its own docstring, not just the module header — every helper and `test_*` function
  across Tasks 2-5's Python files now has one. The PowerShell module (`.psm1`) is outside the
  auditor's scanned extensions (`.py`/`.ts`/`.tsx`/`.js`) and cannot be verified against it
  automatically, but carries the same purpose-header shape by convention for consistency.
