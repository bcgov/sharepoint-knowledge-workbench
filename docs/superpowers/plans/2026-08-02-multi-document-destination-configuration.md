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

**Files:**
- Create: `config.psd1.example` (repo root)
- Test: `tests/test_root_config_schema.py` (repo root — new top-level `tests/` directory; this
  repo has no root-level Python test dir yet, this is the first file in it)

**Interfaces:**
- Consumes: nothing.
- Produces: the `config.psd1.example` file shape Task 4's module and Task 3's profile schema both
  reference by key name (`SiteUrl`, `TenantId`, `ClientId`, `AuthenticationMode`,
  `CertificateThumbprint`, `TenantAdminUrl`, `DefaultPublicationRoot`, `DefaultAgentAssetsRoot`).

- [ ] **Step 1: Write the failing test**

```python
"""
Purpose: validates the repo-root config.psd1.example template matches the schema
specified in docs/superpowers/specs/2026-08-02-multi-document-destination-configuration-design.md
Section 1 (Layer 1 — root connection configuration).

Key input dependency: config.psd1.example (repo root) — must exist and be parseable as
PowerShell data-file syntax (@{ ... } hashtable literal).

Index of test functions:
- test_config_example_exists_at_repo_root
- test_config_example_has_no_secret_looking_values
- test_config_example_contains_required_keys
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_EXAMPLE_PATH = REPO_ROOT / "config.psd1.example"

REQUIRED_KEYS = [
    "SiteUrl", "TenantId", "ClientId", "AuthenticationMode",
    "CertificateThumbprint", "TenantAdminUrl",
    "DefaultPublicationRoot", "DefaultAgentAssetsRoot",
]


def test_config_example_exists_at_repo_root() -> None:
    assert CONFIG_EXAMPLE_PATH.is_file(), f"Expected {CONFIG_EXAMPLE_PATH} to exist"


def test_config_example_contains_required_keys() -> None:
    text = CONFIG_EXAMPLE_PATH.read_text(encoding="utf-8")
    for key in REQUIRED_KEYS:
        assert re.search(rf"\b{key}\s*=", text), f"Missing key '{key}' in config.psd1.example"


def test_config_example_has_no_secret_looking_values() -> None:
    text = CONFIG_EXAMPLE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in ["clientsecret", "password", "accesstoken", "certificatepassword"]:
        assert forbidden not in text, f"config.psd1.example must never define '{forbidden}'"
```

- [ ] **Step 2: Run the test to confirm it fails**

Run: `python3 -m pytest tests/test_root_config_schema.py -v`
Expected: FAIL — `config.psd1.example` does not exist at the repo root yet (it currently only
exists per-phase-folder).

- [ ] **Step 3: Write `config.psd1.example`**

Create at the repo root (exact content, per the design spec's Section 1 Layer 1 — this is the
consolidated, single root template; the three existing per-phase `config.psd1.example` files are
left untouched by this plan, since migrating/removing them is a future, separately-authorized
step once Task 1's inventory shows which scripts are ready to consume the root file):

```powershell
# Copy this file to config.psd1 (repo root) and fill in real values.
# NEVER commit config.psd1 — it must be gitignored (see repo .gitignore) and stay that way.
#
# This is the root connection configuration per
# docs/superpowers/specs/2026-08-02-multi-document-destination-configuration-design.md, Section 1,
# Layer 1. It holds ONLY stable environment/authentication context — never document-specific
# values (library names, folder names, agent names, overwrite decisions). Per-document
# destinations belong in a publication-profiles/<DocumentId>.publication.psd1 file instead
# (see publication-profiles/ceis-manual.publication.psd1.example for the shape).
@{
    # ============================================================
    # Target SharePoint site.
    # ============================================================
    SiteUrl                = "https://yourtenant.sharepoint.com/sites/YourSite"

    # ============================================================
    # App registration used for interactive delegated login.
    # ============================================================
    TenantId               = "00000000-0000-0000-0000-000000000000"
    ClientId               = "00000000-0000-0000-0000-000000000000"
    AuthenticationMode     = "Interactive"

    # ============================================================
    # Optional — only needed if AuthenticationMode requires certificate auth
    # or a distinct tenant admin URL.
    # ============================================================
    CertificateThumbprint  = ""
    TenantAdminUrl         = ""

    # ============================================================
    # Optional defaults — a script may still be given an explicit
    # -LibraryName/-RootFolder that overrides these; they are fallbacks,
    # not mandatory targets.
    # ============================================================
    DefaultPublicationRoot = "KnowledgePublications"
    DefaultAgentAssetsRoot = "AgentAssets"
}
```

- [ ] **Step 4: Run the test to confirm it passes**

Run: `python3 -m pytest tests/test_root_config_schema.py -v`
Expected: PASS (3/3).

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

**Files:**
- Create: `publication-profiles/ceis-manual.publication.psd1.example`
- Test: `tests/test_publication_profile_schema.py`

**Interfaces:**
- Consumes: nothing.
- Produces: the profile shape (`Document`, `HumanPublication`, `PagePublication`,
  `AgentGrounding`, `Agents`, `NativeSkills`, `Evidence` top-level keys) that Task 4's resolver
  module reads by key name.

- [ ] **Step 1: Write the failing test**

```python
"""
Purpose: validates the CEIS publication-profile example matches the schema specified in
docs/superpowers/specs/2026-08-02-multi-document-destination-configuration-design.md
Section 1 (Layer 2 — per-document publication profile).

Key input dependency: publication-profiles/ceis-manual.publication.psd1.example (repo root
relative path) — must exist and declare all 7 top-level sections.

Index of test functions:
- test_ceis_profile_example_exists
- test_ceis_profile_has_all_required_top_level_sections
- test_ceis_profile_document_id_matches_filename
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = REPO_ROOT / "publication-profiles" / "ceis-manual.publication.psd1.example"

REQUIRED_SECTIONS = [
    "Document", "HumanPublication", "PagePublication",
    "AgentGrounding", "Agents", "NativeSkills", "Evidence",
]


def test_ceis_profile_example_exists() -> None:
    assert PROFILE_PATH.is_file(), f"Expected {PROFILE_PATH} to exist"


def test_ceis_profile_has_all_required_top_level_sections() -> None:
    text = PROFILE_PATH.read_text(encoding="utf-8")
    for section in REQUIRED_SECTIONS:
        assert re.search(rf"\b{section}\s*=", text), f"Missing top-level section '{section}'"


def test_ceis_profile_document_id_matches_filename() -> None:
    text = PROFILE_PATH.read_text(encoding="utf-8")
    assert re.search(r'DocumentId\s*=\s*"ceis-manual"', text), (
        "DocumentId must be 'ceis-manual' to match the filename ceis-manual.publication.psd1"
    )
```

- [ ] **Step 2: Run the test to confirm it fails**

Run: `python3 -m pytest tests/test_publication_profile_schema.py -v`
Expected: FAIL — `publication-profiles/` directory and the example file do not exist yet.

- [ ] **Step 3: Write the CEIS publication-profile example**

Create `publication-profiles/ceis-manual.publication.psd1.example` (exact content, per the design
spec's Section 1 Layer 2 — using the real CEIS document, since it's the one document this repo
actually has, not a synthetic placeholder):

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

    NativeSkills = @()

    Evidence = @{
        OutputPath = "docs/reports/publications/ceis-manual"
    }
}
```

- [ ] **Step 4: Run the test to confirm it passes**

Run: `python3 -m pytest tests/test_publication_profile_schema.py -v`
Expected: PASS (3/3).

- [ ] **Step 5: Commit**

```bash
git add publication-profiles/ceis-manual.publication.psd1.example tests/test_publication_profile_schema.py
git commit -m "feat: add publication-profile schema example for the CEIS Manual"
```

---

## Task 4: Target-resolution PowerShell module

**Files:**
- Create: `tools/shared/Resolve-PublicationTarget.psm1`
- Test: `tests/test_resolve_publication_target.py`

**Interfaces:**
- Consumes: parsed root config hashtable (Task 2's shape) and parsed publication-profile hashtable
  (Task 3's shape), plus explicit override parameters, as plain PowerShell hashtables/strings —
  never connects to SharePoint itself.
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
      # Returns a hashtable: @{ SiteUrl; LibraryName; RootFolder; ResolvedTarget; Sources }
      # where Sources is a hashtable mapping each resolved field name to one of:
      # "OverrideParameter" | "PublicationProfile" | "RootConfig" | "Default"
  }
  ```

- [ ] **Step 1: Write the failing test**

```python
"""
Purpose: validates the Resolve-PublicationTarget PowerShell module (tools/shared/
Resolve-PublicationTarget.psm1) implements the target-resolution algorithm from
docs/superpowers/specs/2026-08-02-multi-document-destination-configuration-design.md
Section 6 — never connects to SharePoint, pure data in/data out.

Key input dependency: pwsh (PowerShell 7) must be on PATH — confirmed present this session
(pwsh 7.7.0-preview.3). Module path: tools/shared/Resolve-PublicationTarget.psm1.

Index of test functions:
- test_resolves_human_topic_target_from_profile_defaults
- test_resolves_media_target_with_explicit_override
- test_resolution_sources_are_recorded_per_field
- test_missing_required_value_fails_closed_not_silent_default
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
    script = f"""
    Import-Module '{MODULE_PATH}' -Force
    {ps_args}
    """
    result = subprocess.run(
        [PWSH, "-NoProfile", "-Command", script],
        capture_output=True, text=True, check=True,
    )
    return json.loads(result.stdout)


def test_resolves_human_topic_target_from_profile_defaults() -> None:
    result = _run_resolve("""
        $root = @{ SiteUrl = "https://tenant.sharepoint.com/sites/site" }
        $profile = @{
            Document = @{ DocumentId = "ceis-manual" }
            HumanPublication = @{ LibraryName = "KnowledgePublications"; RootFolder = "ceis-manual"; TopicFolder = "topics" }
        }
        $r = Resolve-PublicationTarget -RootConfig $root -PublicationProfile $profile -ArtifactType HumanTopic -RelativeItemPath "topic-001.md"
        $r | ConvertTo-Json -Depth 10
    """)
    assert result["LibraryName"] == "KnowledgePublications"
    assert result["ResolvedTarget"] == "KnowledgePublications/ceis-manual/topics/topic-001.md"


def test_resolves_media_target_with_explicit_override() -> None:
    result = _run_resolve("""
        $root = @{ SiteUrl = "https://tenant.sharepoint.com/sites/site" }
        $profile = @{
            Document = @{ DocumentId = "ceis-manual" }
            HumanPublication = @{ LibraryName = "KnowledgePublications"; RootFolder = "ceis-manual"; MediaFolder = "media" }
        }
        $r = Resolve-PublicationTarget -RootConfig $root -PublicationProfile $profile -ArtifactType Media -OverrideLibraryName "OverriddenLibrary" -RelativeItemPath "image-001.png"
        $r | ConvertTo-Json -Depth 10
    """)
    assert result["LibraryName"] == "OverriddenLibrary"
    assert result["Sources"]["LibraryName"] == "OverrideParameter"


def test_resolution_sources_are_recorded_per_field() -> None:
    result = _run_resolve("""
        $root = @{ SiteUrl = "https://tenant.sharepoint.com/sites/site"; DefaultPublicationRoot = "KnowledgePublications" }
        $profile = @{
            Document = @{ DocumentId = "ceis-manual" }
            HumanPublication = @{ RootFolder = "ceis-manual"; TopicFolder = "topics" }
        }
        $r = Resolve-PublicationTarget -RootConfig $root -PublicationProfile $profile -ArtifactType HumanTopic -RelativeItemPath "topic-001.md"
        $r | ConvertTo-Json -Depth 10
    """)
    assert result["Sources"]["LibraryName"] == "RootConfig"
    assert result["Sources"]["RootFolder"] == "PublicationProfile"


def test_missing_required_value_fails_closed_not_silent_default() -> None:
    with pytest.raises(subprocess.CalledProcessError):
        _run_resolve("""
            $root = @{ SiteUrl = "https://tenant.sharepoint.com/sites/site" }
            $profile = @{ Document = @{ DocumentId = "ceis-manual" }; HumanPublication = @{} }
            Resolve-PublicationTarget -RootConfig $root -PublicationProfile $profile -ArtifactType HumanTopic -RelativeItemPath "topic-001.md" -ErrorAction Stop
        """)
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
    order in docs/superpowers/specs/2026-08-02-multi-document-destination-configuration-design.md
    Section 1 (explicit parameter -> publication profile -> root config -> fail closed).

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

    $section = switch ($ArtifactType) {
        "HumanTopic"    { $PublicationProfile.HumanPublication }
        "Media"         { $PublicationProfile.HumanPublication }
        "AgentGrounding" { $PublicationProfile.AgentGrounding }
        "AspxPage"      { $PublicationProfile.PagePublication }
        "NativeSkill"   { $PublicationProfile.NativeSkills }
    }

    $sources = @{}

    if ($OverrideLibraryName) {
        $libraryName = $OverrideLibraryName
        $sources["LibraryName"] = "OverrideParameter"
    } elseif ($section -and $section.LibraryName) {
        $libraryName = $section.LibraryName
        $sources["LibraryName"] = "PublicationProfile"
    } elseif ($RootConfig.DefaultPublicationRoot) {
        $libraryName = $RootConfig.DefaultPublicationRoot
        $sources["LibraryName"] = "RootConfig"
    } else {
        Write-Error "No LibraryName resolvable from override, profile, or root config for ArtifactType '$ArtifactType'." -ErrorAction Stop
        return
    }

    if ($OverrideRootFolder) {
        $rootFolder = $OverrideRootFolder
        $sources["RootFolder"] = "OverrideParameter"
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

    $pathParts = @($libraryName, $rootFolder)
    if ($subFolder) { $pathParts += $subFolder }
    if ($RelativeItemPath) { $pathParts += $RelativeItemPath }
    $resolvedTarget = ($pathParts -join "/")

    return @{
        SiteUrl        = $RootConfig.SiteUrl
        LibraryName    = $libraryName
        RootFolder     = $rootFolder
        ResolvedTarget = $resolvedTarget
        Sources        = $sources
    }
}

Export-ModuleMember -Function Resolve-PublicationTarget
```

- [ ] **Step 4: Run the tests to confirm they pass**

Run: `python3 -m pytest tests/test_resolve_publication_target.py -v`
Expected: PASS (4/4).

- [ ] **Step 5: Commit**

```bash
git add tools/shared/Resolve-PublicationTarget.psm1 tests/test_resolve_publication_target.py
git commit -m "feat: add Resolve-PublicationTarget module with precedence-order resolution tests"
```

---

## Task 5: Collision-prevention validation in the same module

**Files:**
- Modify: `tools/shared/Resolve-PublicationTarget.psm1`
- Test: `tests/test_resolve_publication_target.py` (extend from Task 4)

**Interfaces:**
- Consumes: `Resolve-PublicationTarget`'s output shape from Task 4.
- Produces: a second exported function, `Test-PublicationTargetCollision`:
  ```powershell
  function Test-PublicationTargetCollision {
      param(
          [Parameter(Mandatory)][hashtable]$ProposedTarget,   # output of Resolve-PublicationTarget
          [Parameter(Mandatory)][hashtable[]]$ExistingTargets  # array of prior Resolve-PublicationTarget outputs
      )
      # Returns $true if $ProposedTarget.ResolvedTarget matches any $ExistingTargets entry's
      # ResolvedTarget exactly (same DocumentId path colliding) — used before any write.
  }
  ```

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_resolve_publication_target.py`:

```python
def test_collision_detected_for_identical_resolved_target() -> None:
    result = _run_resolve("""
        $root = @{ SiteUrl = "https://tenant.sharepoint.com/sites/site" }
        $profileA = @{ Document = @{ DocumentId = "ceis-manual" }; HumanPublication = @{ LibraryName = "KnowledgePublications"; RootFolder = "ceis-manual"; TopicFolder = "topics" } }
        $profileB = @{ Document = @{ DocumentId = "small-claims-manual" }; HumanPublication = @{ LibraryName = "KnowledgePublications"; RootFolder = "ceis-manual"; TopicFolder = "topics" } }
        $targetA = Resolve-PublicationTarget -RootConfig $root -PublicationProfile $profileA -ArtifactType HumanTopic -RelativeItemPath "topic-001.md"
        $targetB = Resolve-PublicationTarget -RootConfig $root -PublicationProfile $profileB -ArtifactType HumanTopic -RelativeItemPath "topic-001.md"
        $collision = Test-PublicationTargetCollision -ProposedTarget $targetB -ExistingTargets @($targetA)
        @{ Collision = $collision } | ConvertTo-Json -Depth 10
    """)
    assert result["Collision"] is True


def test_no_collision_for_different_document_folders() -> None:
    result = _run_resolve("""
        $root = @{ SiteUrl = "https://tenant.sharepoint.com/sites/site" }
        $profileA = @{ Document = @{ DocumentId = "ceis-manual" }; HumanPublication = @{ LibraryName = "KnowledgePublications"; RootFolder = "ceis-manual"; TopicFolder = "topics" } }
        $profileB = @{ Document = @{ DocumentId = "small-claims-manual" }; HumanPublication = @{ LibraryName = "KnowledgePublications"; RootFolder = "small-claims-manual"; TopicFolder = "topics" } }
        $targetA = Resolve-PublicationTarget -RootConfig $root -PublicationProfile $profileA -ArtifactType HumanTopic -RelativeItemPath "topic-001.md"
        $targetB = Resolve-PublicationTarget -RootConfig $root -PublicationProfile $profileB -ArtifactType HumanTopic -RelativeItemPath "topic-001.md"
        $collision = Test-PublicationTargetCollision -ProposedTarget $targetB -ExistingTargets @($targetA)
        @{ Collision = $collision } | ConvertTo-Json -Depth 10
    """)
    assert result["Collision"] is False
```

- [ ] **Step 2: Run the tests to confirm they fail**

Run: `python3 -m pytest tests/test_resolve_publication_target.py -v`
Expected: the 2 new tests FAIL (`Test-PublicationTargetCollision` not defined); the 4 from Task 4
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
    foreach ($existing in $ExistingTargets) {
        if ($existing.ResolvedTarget -eq $ProposedTarget.ResolvedTarget) {
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
Expected: PASS (6/6).

- [ ] **Step 5: Commit**

```bash
git add tools/shared/Resolve-PublicationTarget.psm1 tests/test_resolve_publication_target.py
git commit -m "feat: add Test-PublicationTargetCollision to Resolve-PublicationTarget module"
```

---

## Task 6: `setup-sharepoint-connection` skill specification (for the sibling monorepo)

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
with a purpose header, then these sections: **Purpose** (interviews the user for `SiteUrl`,
`ClientId`, `TenantId`, `AuthenticationMode`, optional `CertificateThumbprint`, optional
`DefaultPublicationRoot`/`DefaultAgentAssetsRoot`; writes the answers into `config.psd1` at the
repo root using Task 2's `config.psd1.example` as the template to fill in); **Non-goals** (never
writes a real secret to any tracked file; never connects to SharePoint itself — this skill only
produces the local config file, per the design spec's Section 8); **Output contract** (the
filled-in `config.psd1`, gitignored, matching Task 2's schema exactly — same key names, same
optional-vs-required fields); **Where this is authored** (state explicitly: sibling
`agent-plugins-skills` monorepo, per this repo's `CLAUDE.md` Skill Development Protocol — TDD
first, feature branch, PR, user-merged, then installed here via `plugin_add.py` against the local
checkout); **Acceptance criteria** for that future authoring session (a fresh repo with only
`config.psd1.example` present ends up, after running the skill, with a valid `config.psd1` whose
6 required keys are all non-empty and whose values were the exact ones the user typed — no
placeholder text left in the file).

- [ ] **Step 2: Commit**

```bash
git add docs/reports/multi-document-destination-config/setup-sharepoint-connection-skill-spec.md
git commit -m "docs: setup-sharepoint-connection skill spec for sibling-monorepo authoring"
```

---

## Self-review notes

- **Spec coverage:** Section 1 Layer 1 → Task 2; Layer 2 → Task 3; Layer 3 (parameter precedence)
  → Task 4's resolution-source tracking; Section 6 (target-resolution algorithm) → Task 4; Section
  7 (collision prevention) → Task 5; Section 8 (setup plugin) → Task 6; Section 10 (script
  inventory) → Task 1. Sections 2-3 (parameter contracts for future script updates), 9
  (agent-assisted setup behavior), and 12 (republication compatibility) are deliberately not
  separate tasks here — they describe conventions for scripts not yet identified (Section 2-3) or
  a future phase's behavior (Section 9, 12), not buildable artifacts this plan can produce today;
  Task 1's inventory is the prerequisite that would turn Sections 2-3 into real per-script tasks in
  a later, separately-authorized plan.
- **No placeholders:** every code block is complete, runnable content — no "TODO"/"fill in later."
  Task 6 deliberately produces a specification document, not skill code, which is the correct
  non-placeholder output given the sibling-monorepo constraint (the spec IS the deliverable, not a
  stand-in for one).
- **Type/signature consistency:** `Resolve-PublicationTarget`'s return shape (`SiteUrl`,
  `LibraryName`, `RootFolder`, `ResolvedTarget`, `Sources`) is defined once in Task 4 and consumed
  identically by Task 5's `Test-PublicationTargetCollision` (matches on `.ResolvedTarget`) — no
  drift between the two tasks' field names.
- **Coding-conventions compliance:** every new Python test file and the PowerShell module carry a
  purpose header stating what the file does, its key input dependencies, and an index of the
  functions/tests it defines, per `.agent/rules/coding-conventions.md`'s non-negotiables — applied
  here even though that rule's glob is Python/TS/JS/C#-specific and doesn't literally list `.ps1`,
  since the same discoverability rationale applies to a shared module future scripts will import.
