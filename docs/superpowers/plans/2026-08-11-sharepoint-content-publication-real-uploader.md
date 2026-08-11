# SharePoint Content Publication Real Uploader Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give `sharepoint-content-publication`'s `upload-content` skill a real, working `.ps1`
executor for `sharepoint_upload.py`'s `upload_pages(plan, uploader)` — closing the original gap
this whole session started from (`sharepoint_upload.py` raises `NotImplementedError` without an
injected `uploader`; nothing in this repo has ever supplied one).

**Architecture:** Python and PowerShell can't share a callback directly, so this follows the same
pattern already proven by `spo-page-copy-plan.ps1`: a standalone `.ps1` that reads a `PublishPlan`
JSON file (the exact shape `sharepoint_publish_plan.py::PublishPlan.to_dict()` already produces),
and for each action creates + publishes a modern SharePoint page via `Add-PnPPage`/
`Add-PnPPageTextPart`/`Publish-PnPPage` — the only confirmed-working page-creation mechanism on
this tenant per `upload-content`'s own SKILL.md ("Real platform constraint recorded"). Dry-run by
default; `-Execute` + a confirmation token gate any real write, matching every other write-capable
script in this repo.

**Scope boundary (deliberate):** this plan covers **page creation from pre-rendered HTML** only —
each plan action's `source_path` is expected to point at an HTML fragment file, the exact output
`structured-content-rendering`'s `render-sharepoint-aspx` renderer already stages (see that
plugin's `sharepoint_aspx.py`: "one HTML fragment per chunk + `page-manifest.json`, staged for
`Add-PnPPage`/`Add-PnPPageTextPart`"). Raw asset/file upload to a document library (`Add-PnPFile`,
no page creation) is a smaller, separate capability and is explicitly out of scope here — see the
closing section.

**Tech Stack:** PowerShell 7 (`pwsh`), PnP.PowerShell (`Connect-PnPOnline`, `Add-PnPPage`,
`Add-PnPPageTextPart`, `Publish-PnPPage`, `Get-PnPPage`, `Remove-PnPPage`).

## Global Constraints

- Zero writes by default — dry run prints the plan and the exact PnP commands it would run;
  `-Execute` plus an explicit confirmation token gate any real write (same contract as
  `spo-page-copy-plan.ps1`).
- Follow `.agent/rules/sharepoint-ps1-authentication-convention.md`: read `config.psd1`'s
  `Connection`/`Authentication` blocks, `Connect-PnPOnline -Interactive`, support
  `-TenantAdminUrl`.
- File header follows the updated `.agent/rules/coding-conventions.md` rule: what it does, inputs,
  outputs, preconditions, calling example — no phase/wave/commit-hash/project-codename mentions.
- Input JSON shape is exactly `PublishPlan.to_dict()`'s output
  (`{document_id, action_count, actions: [{source_path, target_library, target_folder,
  target_filename}]}`) — no new shape invented, no changes to `sharepoint_publish_plan.py`.
- Symlink the new script into `upload-content`'s skill folder via
  `.agents/skills/symlink-manager/scripts/symlink_manager.py` (fallback: manual `ln -s` +
  `symlinks.json` entry, per the precedent already set for `spo-page-copy-plan.ps1` in this same
  plugin).
- Verify with `pwsh`'s AST parser (`[System.Management.Automation.Language.Parser]::ParseFile`)
  plus a dry-run invocation against a fixture plan — no live tenant required for verification.

---

### Task 1: Add the real page-upload executor script

**Files:**
- Create: `plugins/sharepoint-content-publication/scripts/spo-upload-plan.ps1`
- Reference: `plugins/sharepoint-content-publication/scripts/sharepoint_publish_plan.py` (`PublishPlan.to_dict()` -- the input shape)
- Reference: `plugins/sharepoint-content-publication/scripts/spo-page-copy-plan.ps1` (dry-run/-Execute/confirm-token pattern to copy)
- Reference: `plugins/workbench-setup/scripts/test-spo-connection.ps1` (config-reading pattern)

**Interfaces:**
- Consumes: a JSON file at `-PlanPath` matching `PublishPlan.to_dict()`'s shape.
- Produces: for each action, a created+published modern SharePoint page at
  `<target_library>/<target_folder>/<target_filename minus extension>` (page name derived by
  stripping `.aspx`/`.md` from `target_filename`, since `Add-PnPPage -Name` takes a bare name, not
  a file extension).

- [ ] **Step 1: Write the header, param block, and config-reading helper**

```powershell
<#
.SYNOPSIS
Creates and publishes modern SharePoint Online pages from a publish plan.

.DESCRIPTION
Reads a PublishPlan JSON file (document_id, actions[]: source_path,
target_library, target_folder, target_filename) and, for each action,
creates a modern page via Add-PnPPage, injects the source_path file's
content into a text web part via Add-PnPPageTextPart, and publishes it via
Publish-PnPPage. By default performs no SharePoint tenant I/O; -Execute plus
-ConfirmToken UPLOAD-SPO-PLAN runs the real writes.

.PARAMETER PlanPath
Path to a PublishPlan JSON file matching PublishPlan.to_dict()'s shape.

.PARAMETER SiteUrl
Overrides config.psd1 Connection.SiteUrl. The site pages are created on.

.PARAMETER ConfigPath
Path to config.psd1. Defaults to the repository root config.psd1.

.PARAMETER ClientId
Overrides ConfigPath ClientId.

.PARAMETER TenantId
Overrides ConfigPath TenantId.

.PARAMETER TenantAdminUrl
Overrides ConfigPath Authentication.TenantAdminUrl.

.PARAMETER Overwrite
Removes an existing page at the target name before creating the new one.
Without this, an existing page at the target name causes the run to fail.

.PARAMETER Execute
Runs the real Add-PnPPage/Add-PnPPageTextPart/Publish-PnPPage calls. Omit
this to print the per-action plan only.

.PARAMETER ConfirmToken
Required with -Execute. Must be UPLOAD-SPO-PLAN.

.EXAMPLE
.\spo-upload-plan.ps1 -PlanPath plan.json -SiteUrl "https://tenant.sharepoint.com/sites/Test" -Execute -ConfirmToken UPLOAD-SPO-PLAN
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PlanPath,

    [string]$SiteUrl,

    [string]$ConfigPath = (Join-Path $PSScriptRoot "..\..\..\config.psd1"),

    [string]$ClientId,

    [string]$TenantId,

    [string]$TenantAdminUrl,

    [switch]$Overwrite,

    [switch]$Execute,

    [string]$ConfirmToken
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-WorkbenchConnectionConfig {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return [pscustomobject]@{ SiteUrl = $null; ClientId = $null; TenantId = $null; TenantAdminUrl = $null }
    }

    $rawConfig = Import-PowerShellDataFile -LiteralPath $Path
    $cfg = if ($rawConfig.Connection) { $rawConfig.Connection } else { $rawConfig }
    $tenantAdminUrl = if ($rawConfig.Authentication) { $rawConfig.Authentication.TenantAdminUrl } else { $rawConfig.TenantAdminUrl }

    [pscustomobject]@{
        SiteUrl        = $cfg.SiteUrl
        ClientId       = $cfg.ClientId
        TenantId       = $cfg.TenantId
        TenantAdminUrl = $tenantAdminUrl
    }
}

$connectionConfig = Get-WorkbenchConnectionConfig -Path $ConfigPath
if (-not $SiteUrl) { $SiteUrl = $connectionConfig.SiteUrl }
if (-not $ClientId) { $ClientId = $connectionConfig.ClientId }
if (-not $TenantId) { $TenantId = $connectionConfig.TenantId }
if (-not $TenantAdminUrl) { $TenantAdminUrl = $connectionConfig.TenantAdminUrl }

if (-not $SiteUrl -or -not $ClientId -or -not $TenantId) {
    throw "SiteUrl/ClientId/TenantId not resolved. Provide -SiteUrl/-ClientId/-TenantId or a valid -ConfigPath."
}

if (-not (Test-Path -LiteralPath $PlanPath)) {
    throw "PlanPath '$PlanPath' does not exist."
}
$plan = Get-Content -LiteralPath $PlanPath -Raw | ConvertFrom-Json
if (-not $plan.actions -or $plan.actions.Count -eq 0) {
    throw "Plan at '$PlanPath' has no actions -- nothing to upload."
}
```

- [ ] **Step 2: Write the per-action plan preview**

```powershell
function Get-PageNameFromFileName {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string]$FileName)
    [System.IO.Path]::GetFileNameWithoutExtension($FileName)
}

$actionPlans = foreach ($action in $plan.actions) {
    $pageName = Get-PageNameFromFileName -FileName $action.target_filename
    [ordered]@{
        source_path = $action.source_path
        target_library = $action.target_library
        target_folder = $action.target_folder
        page_name = $pageName
        create_page = "Add-PnPPage -Name `"$pageName`" -LayoutType Article"
        inject_content = "Add-PnPPageTextPart -Page `"$pageName`" -Text (Get-Content -Raw `"$($action.source_path)`")"
        publish_page = "Publish-PnPPage -Identity `"$pageName`""
    }
}

$summary = [ordered]@{
    operation = "upload-spo-plan"
    document_id = $plan.document_id
    action_count = $plan.actions.Count
    site_url = $SiteUrl
    safety = [ordered]@{
        tenant_io = $(if ($Execute) { "pnp-write" } else { "none" })
        execute_requires_confirm_token = "UPLOAD-SPO-PLAN"
    }
    actions = $actionPlans
}
```

- [ ] **Step 3: Write the `-Execute` block**

```powershell
if ($Execute) {
    if ($ConfirmToken -ne "UPLOAD-SPO-PLAN") {
        throw "-Execute requires -ConfirmToken UPLOAD-SPO-PLAN."
    }
    if (-not (Get-Command Add-PnPPage -ErrorAction SilentlyContinue)) {
        throw "PnP.PowerShell with Add-PnPPage is required. Install/import PnP.PowerShell before executing."
    }

    $connectParameters = @{
        Url         = $SiteUrl
        ClientId    = $ClientId
        Tenant      = $TenantId
        Interactive = $true
    }
    if ($TenantAdminUrl) { $connectParameters["TenantAdminUrl"] = $TenantAdminUrl }
    Connect-PnPOnline @connectParameters

    $results = foreach ($action in $plan.actions) {
        $pageName = Get-PageNameFromFileName -FileName $action.target_filename
        if (-not (Test-Path -LiteralPath $action.source_path)) {
            throw "source_path '$($action.source_path)' does not exist -- refusing to create an empty page."
        }

        $existingPage = Get-PnPPage -Identity $pageName -ErrorAction SilentlyContinue
        if ($existingPage) {
            if (-not $Overwrite) {
                throw "Page '$pageName' already exists. Re-run with -Overwrite to replace it."
            }
            Remove-PnPPage -Identity $pageName -Force
        }

        $content = Get-Content -LiteralPath $action.source_path -Raw
        Add-PnPPage -Name $pageName -LayoutType Article | Out-Null
        Add-PnPPageTextPart -Page $pageName -Text $content | Out-Null
        Publish-PnPPage -Identity $pageName | Out-Null

        [pscustomobject]@{
            source_path = $action.source_path
            page_name   = $pageName
            success     = $true
        }
    }

    $results | ConvertTo-Json -Depth 8
}
else {
    $summary | ConvertTo-Json -Depth 8
}
```

- [ ] **Step 4: Verify the script parses clean**

Run:
```bash
pwsh -NoProfile -Command "$errors = $null; $null = [System.Management.Automation.Language.Parser]::ParseFile('plugins/sharepoint-content-publication/scripts/spo-upload-plan.ps1', [ref]$null, [ref]$errors); if ($errors.Count -gt 0) { $errors } else { 'PARSE OK' }"
```
Expected: `PARSE OK`

- [ ] **Step 5: Dry-run against a fixture plan (no live tenant)**

Create a temporary fixture at `plugins/sharepoint-content-publication/tests/fixtures/publish-plan.json`:
```json
{
  "document_id": "test-doc",
  "action_count": 1,
  "actions": [
    {"source_path": "page1.html", "target_library": "SitePages", "target_folder": "", "target_filename": "page1.aspx"}
  ]
}
```
Run: `pwsh -File plugins/sharepoint-content-publication/scripts/spo-upload-plan.ps1 -PlanPath plugins/sharepoint-content-publication/tests/fixtures/publish-plan.json -SiteUrl "https://tenant.sharepoint.com/sites/Test" -ClientId x -TenantId y`
Expected: prints the dry-run JSON summary with `page_name: "page1"`, `tenant_io: "none"`.

- [ ] **Step 6: Commit**

```bash
git add plugins/sharepoint-content-publication/scripts/spo-upload-plan.ps1 plugins/sharepoint-content-publication/tests/fixtures/publish-plan.json
git commit -m "feat(sharepoint-content-publication): add real page-upload executor (Add-PnPPage/Add-PnPPageTextPart/Publish-PnPPage)"
```

---

### Task 2: Wire the executor into the `upload-content` skill, symlink it, update SKILL.md

**Files:**
- Modify: `plugins/sharepoint-content-publication/skills/upload-content/SKILL.md`
- Create (symlink): `plugins/sharepoint-content-publication/skills/upload-content/scripts/spo-upload-plan.ps1` -> `../../../scripts/spo-upload-plan.ps1`
- Modify: `symlinks.json`

**Interfaces:**
- Consumes: Task 1's finished script.
- Produces: a documented, runnable path from a `PublishPlan` JSON to real published pages —
  closing the `sharepoint_upload.py` gap this whole session traced back to.

- [ ] **Step 1: Create the symlink** (same fallback rule as the discovery plan's Task 3 Step 1 --
  prefer `symlink_manager.py`, fall back to manual `ln -s` + `symlinks.json` entry if it's absent
  from this checkout).

- [ ] **Step 2: Run the symlink diagnostic** (`symlink_manager.py diagnose`, or `ls -la` fallback
  check).

- [ ] **Step 3: Update SKILL.md**

Replace the "Purpose" section's framing of `upload_pages()` as requiring a caller-supplied
`uploader` with no example, adding:
```markdown
## Real executor now available

`scripts/spo-upload-plan.ps1` is a real, working uploader for the modern-page-creation path this
skill's "Real platform constraint recorded" section already documents. It is NOT wired in as
`sharepoint_upload.py`'s injected `uploader` automatically (Python cannot call a PowerShell script
as an in-process callback) -- run it directly against a PublishPlan JSON:

\`\`\`bash
pwsh -File scripts/spo-upload-plan.ps1 -PlanPath plan.json -SiteUrl "https://tenant.sharepoint.com/sites/Test" -Execute -ConfirmToken UPLOAD-SPO-PLAN
\`\`\`

Scope: page creation from pre-rendered HTML only (matches `structured-content-rendering`'s
`render-sharepoint-aspx` output). Raw file/asset upload to a document library is a separate,
not-yet-built capability -- see this plugin's own follow-up tracking.
```

Update the `## Scripts` list to add `../../scripts/spo-upload-plan.ps1`.

- [ ] **Step 4: Run the plugin's test suite**

Run: `python -m pytest plugins/sharepoint-content-publication/tests/ -v`
Expected: all existing tests still pass (this task adds no new Python tests -- the script's
correctness is verified by Task 1's parse check + dry-run, matching how `spo-page-copy-plan.ps1`
was verified this session).

- [ ] **Step 5: Commit**

```bash
git add plugins/sharepoint-content-publication/skills/upload-content/SKILL.md symlinks.json \
  plugins/sharepoint-content-publication/skills/upload-content/scripts/spo-upload-plan.ps1
git commit -m "docs(sharepoint-content-publication): document and symlink the real page-upload executor into upload-content"
```

---

### Task 3: Update the tracked gap record

**Files:**
- Modify: `.agent/map-debt.md`

- [ ] **Step 1: Append a follow-up note to the 2026-08-11 gap entry**

```markdown
- **Update [DATE]**: gap #5 (page upload/publish, `sharepoint-content-publication`) partially
  closed -- `upload-content` skill now has a real `spo-upload-plan.ps1` executor (page creation
  from pre-rendered HTML only; raw asset/file upload to a document library is still MISSING,
  tracked as follow-on work). `sharepoint-discovery`, `sharepoint-schema`,
  `sharepoint-provisioning`, `sharepoint-content-migration`, `sharepoint-link-remediation`,
  `sharepoint-page-modernization` gaps are unchanged.
```

- [ ] **Step 2: Commit**

```bash
git add .agent/map-debt.md
git commit -m "docs(map-debt): record spo-upload-plan.ps1 as closing part of the 2026-08-11 gap"
```

---

## What this plan deliberately does NOT cover

- **Raw asset/file upload** (`Add-PnPFile` to a document library, not page creation) — a smaller,
  separate capability. `upload/migrate-site-assets.ps1` (source repo) is the closest existing
  pattern, per `docs/reports/sharepoint-migration-ps1-source-inventory.md`, but it's scoped to
  `sharepoint-content-migration`'s `migrate-site-assets` (new skill), not this plugin.
- **`link-conversion/`'s 3 files** (`execute-page-bulk-migration`, `convert-page-to-modern`,
  `validate-page-migration` per the inventory doc) — classic-to-modern page conversion is a
  different operation from publishing already-rendered content; its own plan when this plugin's
  turn comes back around.
- **`copy-spo-page-between-sites`** — already has a real executor (`spo-page-copy-plan.ps1`, built
  and verified earlier this session).
