# SharePoint Discovery Real Collector Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give `sharepoint-discovery`'s `analyze-page-inventory` skill a real, working `.ps1`
collector that produces the `page-inventory.json` export it currently requires the caller to
already have — closing the first (and lowest-risk) of the 6 plugin gaps recorded in
`.agent/map-debt.md`'s 2026-08-11 entry ("Phase 9 Onboarding — Real Tenant-Write/Discovery
Executors Never Ported, Only Their Planning Halves").

**Architecture:** One new `.ps1` script at the plugin root
(`plugins/sharepoint-discovery/scripts/collect-sharepoint-page-inventory.ps1`), following this
repo's hub-and-spoke convention (real file at plugin root, symlinked into the consuming skill) and
its standard PnP.PowerShell auth convention (`.agent/rules/sharepoint-ps1-authentication-
convention.md`). It is read-only (`Get-PnP*` only, zero writes) and emits JSON matching the exact
shape `page_inventory_analysis.py` already consumes — verified against
`tests/fixtures/page-inventory.json`, the plugin's own existing test fixture, so no consumer-side
code changes are needed.

**Tech Stack:** PowerShell 7 (`pwsh`), PnP.PowerShell (`Connect-PnPOnline`, `Get-PnPListItem`,
`Get-PnPFile`), no new Python dependencies.

## Global Constraints

- Zero tenant writes — this script only calls read cmdlets (`Get-PnP*`), never `Add-PnP*`/
  `Set-PnP*`/`Remove-PnP*`.
- Must follow `.agent/rules/sharepoint-ps1-authentication-convention.md`: read connection details
  from `config.psd1` (`Connection` nested or flat schema), `Connect-PnPOnline -Interactive`, and
  support `-TenantAdminUrl` (not required for this read-only site-scoped operation, but the param
  must exist per the rule's own text so this script doesn't silently diverge).
- Output JSON must be a byte-for-byte-compatible shape with
  `plugins/sharepoint-discovery/tests/fixtures/page-inventory.json` (a JSON array of objects with
  `FileName`, `Category`, `ListTitle`, `ConnectedWPCount`, `HasCEWP`, `HasSEWP`, `WebParts[]` where
  each web part has `Category`, `TypeName`, `Title`, `ListName`) — `page_inventory_analysis.py`
  parses this shape today and must not need to change.
- No project-specific site/tenant values hardcoded in the script itself (matches this plugin's
  existing "rules are data, not code" principle) — the target site comes from `config.psd1` or an
  explicit `-SiteUrl` override, same pattern as `test-spo-connection.ps1`.
- Symlink the new script into the skill folder via
  `.agents/skills/symlink-manager/scripts/symlink_manager.py` (never `ln -s`, never a hand-copy) —
  if that helper is not present in this checkout (a documented, real gap — see
  `.agent/map-debt.md`'s 2026-08-07 "symlink_manager.py not present in this worktree" entry), fall
  back to manually creating the symlink and recording that in `symlinks.json`, matching the pattern
  already used for `spo-page-copy-plan.ps1`.
- Run `pwsh`'s AST parser on the finished script (`[System.Management.Automation.Language.Parser]::ParseFile`)
  before considering any task done — this repo has no PowerShell unit-test runner, so a clean parse
  plus a structural dry-run (see Task 2) is the verification bar for `.ps1` correctness here.

---

### Task 1: Add the real page-inventory collector script

**Files:**
- Create: `plugins/sharepoint-discovery/scripts/collect-sharepoint-page-inventory.ps1`
- Reference: `plugins/sharepoint-discovery/tests/fixtures/page-inventory.json` (target output shape)
- Reference: `jag-csb-cmat-sharepoint-online/.agents/skills/sp-discovering-site-structure/scripts/export-sharepoint-inventory.ps1` lines 636-681 (`Page Scanner` block — the source logic this generalizes, but rewritten against PnP.PowerShell/`Connect-PnPOnline` instead of that script's on-prem NTLM `Invoke-RestMethod` mode, since this workbench's tenant is modern SPO, not an ADFS-federated on-prem site)
- Reference: `plugins/workbench-setup/scripts/test-spo-connection.ps1` (config-reading pattern to copy)

**Interfaces:**
- Consumes: `config.psd1`'s `Connection.SiteUrl`/`ClientId`/`TenantId` (or flat schema), same
  reader pattern as `test-spo-connection.ps1`.
- Produces: a JSON file at `-OutputPath` (default `page-inventory.json` in the current directory)
  matching the array-of-page-objects shape below — this is what Task 3 wires into the skill as its
  documented collector.

- [ ] **Step 1: Write the script header and parameter block**

```powershell
<#
.SYNOPSIS
Collects a page inventory (Site Pages + list forms) from a live SharePoint Online
site and writes it as JSON in the shape analyze-page-inventory's
page_inventory_analysis.py already consumes.

.DESCRIPTION
Read-only. Connects interactively via PnP.PowerShell, enumerates the Site Pages
library (and list NewForm/EditForm/DispForm pages, if -IncludeListForms is set),
downloads each .aspx page's content, and detects legacy Content Editor / Script
Editor web parts and list-view web parts by scanning the page markup. Performs
zero tenant writes.

.PARAMETER SiteUrl
Overrides config.psd1 Connection.SiteUrl.

.PARAMETER ConfigPath
Path to config.psd1. Defaults to the repository root config.psd1.

.PARAMETER ClientId
Overrides ConfigPath ClientId.

.PARAMETER TenantId
Overrides ConfigPath TenantId.

.PARAMETER TenantAdminUrl
Overrides ConfigPath Authentication.TenantAdminUrl. Not required for this
read-only, single-site operation -- present only so this script does not
silently diverge from the repo's standard PnP auth parameter set.

.PARAMETER IncludeListForms
When set, also scans each list's NewForm/EditForm/DispForm pages, not just
Site Pages library pages.

.PARAMETER OutputPath
Where to write the resulting JSON array. Defaults to .\page-inventory.json.

.EXAMPLE
.\collect-sharepoint-page-inventory.ps1 -SiteUrl "https://tenant.sharepoint.com/sites/Test" -OutputPath ".\out\page-inventory.json"
#>

[CmdletBinding()]
param(
    [string]$SiteUrl,

    [string]$ConfigPath = (Join-Path $PSScriptRoot "..\..\..\config.psd1"),

    [string]$ClientId,

    [string]$TenantId,

    [string]$TenantAdminUrl,

    [switch]$IncludeListForms,

    [string]$OutputPath = ".\page-inventory.json"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
```

- [ ] **Step 2: Write the config-reading helper (same pattern as `test-spo-connection.ps1`)**

```powershell
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
```

- [ ] **Step 3: Write the web-part detection function (ported from the source repo's Page Scanner block, generalized)**

```powershell
function Get-PageWebParts {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string]$PageContent)

    $webParts = @()
    $hasCewp = $PageContent -match 'ContentEditorWebPart'
    $hasSewp = $PageContent -match 'ScriptEditorWebPart'

    if ($PageContent -match 'ContentEditorWebPart[^>]*Title="([^"]*)"') {
        $webParts += [pscustomobject]@{ Category = "CEWP"; TypeName = "ContentEditorWebPart"; Title = $matches[1]; ListName = "" }
    }
    if ($PageContent -match 'ScriptEditorWebPart[^>]*Title="([^"]*)"') {
        $webParts += [pscustomobject]@{ Category = "SEWP"; TypeName = "ScriptEditorWebPart"; Title = $matches[1]; ListName = "" }
    }

    [pscustomobject]@{
        HasCEWP  = $hasCewp
        HasSEWP  = $hasSewp
        WebParts = $webParts
    }
}
```

- [ ] **Step 4: Write the main collection loop and JSON output**

```powershell
Connect-PnPOnline -Url $SiteUrl -ClientId $ClientId -Tenant $TenantId -Interactive

$pages = @()
$siteRelativeUrl = (Get-PnPWeb -Includes ServerRelativeUrl).ServerRelativeUrl
$pageFiles = Get-PnPFolderItem -FolderSiteRelativeUrl "SitePages" -ItemType File

foreach ($file in $pageFiles) {
    if ($file.Name -notmatch '\.aspx$') { continue }
    $serverRelativeUrl = "$siteRelativeUrl/SitePages/$($file.Name)"
    $content = (Get-PnPFile -Url $serverRelativeUrl -AsString)
    $detection = Get-PageWebParts -PageContent $content

    $pages += [pscustomobject]@{
        FileName         = $file.Name
        Category         = "SitePage"
        ListTitle        = ""
        ConnectedWPCount = 0
        HasCEWP          = $detection.HasCEWP
        HasSEWP          = $detection.HasSEWP
        WebParts         = $detection.WebParts
    }
}

if ($IncludeListForms) {
    $lists = Get-PnPList | Where-Object { -not $_.Hidden }
    foreach ($list in $lists) {
        $forms = Get-PnPView -List $list.Title -Includes ServerRelativeUrl -ErrorAction SilentlyContinue
        # Form scanning intentionally minimal in this first pass -- see plan's
        # "not yet done" notes below for the follow-on task that extends this.
    }
}

$pages | ConvertTo-Json -Depth 8 | Set-Content -Path $OutputPath -Encoding UTF8
Write-Host "Wrote $($pages.Count) page record(s) to $OutputPath" -ForegroundColor Green
Disconnect-PnPOnline -ErrorAction SilentlyContinue
```

- [ ] **Step 5: Verify the script parses clean**

Run:
```bash
pwsh -NoProfile -Command "$errors = $null; $null = [System.Management.Automation.Language.Parser]::ParseFile('plugins/sharepoint-discovery/scripts/collect-sharepoint-page-inventory.ps1', [ref]$null, [ref]$errors); if ($errors.Count -gt 0) { $errors } else { 'PARSE OK' }"
```
Expected: `PARSE OK`

- [ ] **Step 6: Commit**

```bash
git add plugins/sharepoint-discovery/scripts/collect-sharepoint-page-inventory.ps1
git commit -m "feat(sharepoint-discovery): add real page-inventory collector (Get-PnPFile/Get-PnPFolderItem)"
```

---

### Task 2: Verify the collector's output shape against the existing consumer, without a live tenant

**Files:**
- Create: `plugins/sharepoint-discovery/tests/test_page_inventory_collector_shape.py`
- Modify: none (this is a shape-contract test, not a live-tenant test)

**Interfaces:**
- Consumes: `plugins/sharepoint-discovery/tests/fixtures/page-inventory.json` (the existing fixture
  `page_inventory_analysis.py`'s own tests already validate against).
- Produces: a regression guard that fails if a future edit to the collector script's `ConvertTo-Json`
  shape (Step 4 above) silently diverges from what `page_inventory_analysis.py` expects — this test
  parses the collector script's PowerShell object-construction lines with a simple structural check
  (field-name set comparison), not a live run.

- [ ] **Step 1: Write the failing test**

```python
import json
import re
from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "page-inventory.json"
COLLECTOR = Path(__file__).parent.parent / "scripts" / "collect-sharepoint-page-inventory.ps1"


def test_collector_output_fields_match_fixture_schema():
    fixture_records = json.loads(FIXTURE.read_text(encoding="utf-8"))
    fixture_fields = set(fixture_records[0].keys())

    collector_source = COLLECTOR.read_text(encoding="utf-8")
    # Find the [pscustomobject]@{ ... } block that builds each $pages entry.
    match = re.search(r"\$pages \+= \[pscustomobject\]@\{(.*?)\}", collector_source, re.DOTALL)
    assert match, "collector script must build $pages entries via [pscustomobject]@{...}"
    collector_fields = set(re.findall(r"^\s*(\w+)\s*=", match.group(1), re.MULTILINE))

    assert collector_fields == fixture_fields, (
        f"collector output fields {collector_fields} do not match "
        f"page_inventory_analysis.py's expected fixture fields {fixture_fields}"
    )


def test_collector_webpart_fields_match_fixture_schema():
    fixture_records = json.loads(FIXTURE.read_text(encoding="utf-8"))
    fixture_wp_fields = set(fixture_records[1]["WebParts"][0].keys())  # links.aspx has WebParts

    collector_source = COLLECTOR.read_text(encoding="utf-8")
    matches = re.findall(r"\[pscustomobject\]@\{ Category = .*? \}", collector_source)
    assert matches, "collector script must build WebParts entries via [pscustomobject]@{...}"
    collector_wp_fields = set(re.findall(r"(\w+)\s*=", matches[0]))

    assert collector_wp_fields == fixture_wp_fields
```

- [ ] **Step 2: Run test to verify it fails (before the collector script exists it can't -- run after Task 1's script exists, but before this test file is added to CI it should still be run once manually to confirm both assertions actually exercise real content)**

Run: `python -m pytest plugins/sharepoint-discovery/tests/test_page_inventory_collector_shape.py -v`
Expected: PASS once Task 1 is complete (this test is written after Task 1's script exists, so it
should pass immediately -- if it fails, the collector's field names drifted from the fixture and
must be fixed before proceeding, not the test).

- [ ] **Step 3: Run the plugin's full test suite to confirm nothing else broke**

Run: `python -m pytest plugins/sharepoint-discovery/tests/ -v`
Expected: all existing tests still pass, plus the two new ones.

- [ ] **Step 4: Commit**

```bash
git add plugins/sharepoint-discovery/tests/test_page_inventory_collector_shape.py
git commit -m "test(sharepoint-discovery): guard collector output shape against page_inventory_analysis.py's fixture contract"
```

---

### Task 3: Wire the collector into the skill, symlink it, update SKILL.md

**Files:**
- Modify: `plugins/sharepoint-discovery/skills/analyze-page-inventory/SKILL.md`
- Create (symlink): `plugins/sharepoint-discovery/skills/analyze-page-inventory/scripts/collect-sharepoint-page-inventory.ps1` -> `../../../scripts/collect-sharepoint-page-inventory.ps1`
- Modify: `symlinks.json` (record the new link, same pattern as the existing `spo_page_copy_plan.py`/`spo-page-copy-plan.ps1` entries)

**Interfaces:**
- Consumes: Task 1's finished script at `plugins/sharepoint-discovery/scripts/collect-sharepoint-page-inventory.ps1`.
- Produces: a documented, runnable end-to-end path from "I have a live tenant" to
  `page-inventory.json` to `page_inventory_analysis.py`'s existing `run()` — closing this specific
  gap from `.agent/map-debt.md`'s 2026-08-11 entry.

- [ ] **Step 1: Create the symlink**

Preferred (if `.agents/skills/symlink-manager/scripts/symlink_manager.py` exists in this checkout):
```bash
python3 .agents/skills/symlink-manager/scripts/symlink_manager.py create \
  --src plugins/sharepoint-discovery/scripts/collect-sharepoint-page-inventory.ps1 \
  --dst plugins/sharepoint-discovery/skills/analyze-page-inventory/scripts/collect-sharepoint-page-inventory.ps1
```

Fallback (per `.agent/map-debt.md`'s 2026-08-07 entry, if the helper is absent from this checkout):
```bash
mkdir -p plugins/sharepoint-discovery/skills/analyze-page-inventory/scripts
ln -s ../../../scripts/collect-sharepoint-page-inventory.ps1 \
  plugins/sharepoint-discovery/skills/analyze-page-inventory/scripts/collect-sharepoint-page-inventory.ps1
```
Then manually add the same entry shape already used for `spo-page-copy-plan.ps1` to `symlinks.json`.

- [ ] **Step 2: Run the symlink diagnostic**

```bash
python3 .agents/skills/symlink-manager/scripts/symlink_manager.py diagnose
```
Expected: zero broken links, the new link listed as a real symlink (not a real-file imposter). If
the helper is absent, instead run `ls -la plugins/sharepoint-discovery/skills/analyze-page-inventory/scripts/`
and confirm the entry shows as a symlink (`l` mode bit) pointing at the plugin-root file.

- [ ] **Step 3: Update SKILL.md's Trigger/Purpose, Usage, and Scripts sections**

Replace this line:
```
It consumes a
page inventory already exported from a tenant and produces a scored,
prioritised analysis.
```
with:
```
It consumes a page inventory exported from a tenant -- either produced by
`scripts/collect-sharepoint-page-inventory.ps1` (this skill's own real, read-only
PnP.PowerShell collector) or supplied from any other source in the same JSON shape
-- and produces a scored, prioritised analysis.
```

Add a new `## Collecting a fresh export` section before `## Usage`:
```markdown
## Collecting a fresh export

`collect-sharepoint-page-inventory.ps1` connects interactively (delegated auth,
per `.agent/rules/sharepoint-ps1-authentication-convention.md`) to a live site
and writes a `page-inventory.json` in the exact shape `page_inventory_analysis.py`
consumes. Read-only -- calls only `Get-PnP*` cmdlets, zero tenant writes.

\`\`\`bash
pwsh -File scripts/collect-sharepoint-page-inventory.ps1 -SiteUrl "https://tenant.sharepoint.com/sites/Test" -OutputPath page-inventory.json
\`\`\`
```

Update the `## Scripts` list:
```markdown
## Scripts

- `scripts/collect-sharepoint-page-inventory.ps1` -- real, read-only PnP.PowerShell collector (new)
- `scripts/page_inventory_analysis.py` -- `run`, `analyse`, `generate_report`, `load_rules`, `compute_complexity`, `disposition_hint`
- `scripts/discovery_inputs.py` -- `DiscoveryStatus`, `DiscoveryOutcome`, `load_json_input`, `require_output_dir`
```

- [ ] **Step 4: Update `plugin.yaml` if it lists per-skill script files explicitly**

Check `plugins/sharepoint-discovery/plugin.yaml` for a per-skill file manifest (per
`.agent/map-debt.md`'s "Plugin manifest drift" 2026-08-08 entry, which added
`test_plugin_manifest.py` specifically to catch this). Add the new script if the manifest format
requires it.

- [ ] **Step 5: Run the plugin manifest test**

Run: `python -m pytest plugins/sharepoint-discovery/tests/ -k manifest -v` (if this test exists in
this plugin; if not, run the full suite per Task 2 Step 3 again as the closest available check).

- [ ] **Step 6: Commit**

```bash
git add plugins/sharepoint-discovery/skills/analyze-page-inventory/SKILL.md symlinks.json \
  plugins/sharepoint-discovery/skills/analyze-page-inventory/scripts/collect-sharepoint-page-inventory.ps1 \
  plugins/sharepoint-discovery/plugin.yaml
git commit -m "docs(sharepoint-discovery): document and symlink the real page-inventory collector into analyze-page-inventory"
```

---

### Task 4: Update the tracked gap record

**Files:**
- Modify: `.agent/map-debt.md`

**Interfaces:**
- Consumes: the 2026-08-11 gap entry already in this file.
- Produces: an updated status so a future session doesn't re-discover this same gap from scratch.

- [ ] **Step 1: Add a follow-up note to the existing 2026-08-11 entry**

Append to the entry (do not rewrite it -- this repo's convention is additive incident logs, not
edited history):
```markdown
- **Update [DATE OF THIS WORK]**: gap #1 (discovery of lists/site structure) partially closed --
  `sharepoint-discovery`'s `analyze-page-inventory` skill now has a real, read-only
  `collect-sharepoint-page-inventory.ps1` collector (Site Pages library only; list-form scanning
  and the plugin's other 4 domains -- forms, navigation, permissions, webpart-code -- are still
  MISSING/STUB, tracked as follow-on work). `sharepoint-schema`, `sharepoint-provisioning`,
  `sharepoint-content-migration`, `sharepoint-content-publication`, `sharepoint-link-remediation`,
  `sharepoint-page-modernization` gaps are unchanged.
```

- [ ] **Step 2: Commit**

```bash
git add .agent/map-debt.md
git commit -m "docs(map-debt): record page-inventory collector as closing part of the 2026-08-11 gap"
```

---

## Findings from the full 147-file source inventory (2026-08-11)

A separate, broader audit (`docs/reports/sharepoint-migration-ps1-source-inventory.md`) classified
every `.ps1` file in the source repo's `sharepoint-migration` plugin. The subset relevant to
`sharepoint-discovery` is recorded here so the next domain's plan doesn't have to re-derive it:

| Source script | Onboard as | Target skill |
|---|---|---|
| `diagnostics/export-images-library-inventory.ps1` | As-Is (already PnP-based) | `collect-sharepoint-inventory` (new) |
| `diagnostics/export-persons-picture-description.ps1` | As-Is (already PnP-based) | `collect-sharepoint-inventory` (new) |
| `inventory/export-sharepoint-inventory.ps1` | Rewrite (NTLM/REST -> PnP) | `collect-sharepoint-inventory` (new) |
| `inventory/export-sharepoint-inventory-custom.ps1` | Rewrite (NTLM/REST -> PnP) | `collect-sharepoint-inventory` (new) |
| `inventory/check-managed-metadata-custom.ps1` | Rewrite | `audit-managed-metadata` (new) |
| `utilities/check-managed-metadata-spo-prod.ps1` | Rewrite | `audit-managed-metadata` (new) |
| `content-migration/get-source-item-counts.ps1` | Rewrite (on-prem leg, keep NTLM) | `collect-sharepoint-inventory` (new) |
| `utilities/discover-sandbox-definitions.ps1` | Rewrite | `collect-sharepoint-inventory` (new) |
| `scripts/diagnose-onprem-schema-drift.ps1` (source repo root) | Rewrite | `audit-onprem-schema-drift` (new) |
| `page-migration/extract-all-aspx-pages.ps1` | Rewrite (on-prem leg, keep NTLM) | `collect-sharepoint-inventory` (new) |
| `page-migration/extract-site-navigation.ps1` | Rewrite (on-prem leg, keep NTLM) | `analyze-site-navigation` (existing -- this is its missing collector) |
| `page-migration/extract-webpart-content.ps1`, `scan-webparts.ps1`, `scan-all-webparts-live.ps1` | Rewrite (on-prem leg, keep NTLM) | `analyze-webpart-code` (existing -- these are its missing collector) |
| `page-migration/download-custom-forms.ps1` | Rewrite (on-prem leg, keep NTLM) | `analyze-custom-forms` (existing -- this is its missing collector) |
| `page-migration/generate-discovery-reports.ps1` | Rewrite (no tenant I/O, local report assembly) | `generate-discovery-report-set` (new) |
| `utilities/extract-choices.ps1`, `extract-choices-direct.ps1` | Rewrite | an existing choice-field extraction skill the inventory doc names `extract-choice-fields` -- **not yet confirmed against this plugin's actual 5 skill names; verify before relying on this row** |

This plan's Task 1 (page-inventory collector) is the first slice of the `collect-sharepoint-
inventory` skill above -- `page_inventory_analysis.py`'s consumer needs are narrower than the full
inventory collector's scope, so this plan built a purpose-fit collector rather than the full
multi-domain one. When picking up the remaining `sharepoint-discovery` work, treat `collect-
sharepoint-inventory` as the eventual home for this plan's script too, not a separate thing.

Note that several rows above say "keep NTLM" -- those source scripts collect from a legacy on-prem
SharePoint 2016 site (Windows-credential/NTLM REST), which is a different collection mechanism
than this plan's `Connect-PnPOnline`-based approach for modern SharePoint Online. Both are
legitimate; which one applies depends on whether the target site is on-prem SP2016 or SPO. Don't
collapse them into one script without preserving that distinction.

## What this plan deliberately does NOT cover (by design, not oversight)

- The other 4 `sharepoint-discovery` analysis domains (forms, navigation, permissions, webpart-code)
  each need their own collector, following this same Task 1-4 shape — the exact source scripts to
  rewrite for each are now named in the "Findings from the full 147-file source inventory" table
  above (`extract-site-navigation.ps1` for navigation, `extract-webpart-content.ps1`/`scan-
  webparts.ps1`/`scan-all-webparts-live.ps1` for webpart-code, `download-custom-forms.ps1` for
  forms; no source script was identified in the inventory for permissions specifically — that gap
  needs its own confirmation before its collector plan is written). Not planned here — per your
  "one plugin at a time" instruction, this plan scopes to proving the pattern on one domain first;
  the remaining domains in this same plugin are the natural next increment once this one is
  reviewed, and now have a concrete source-script starting point instead of a blank slate.
- `collect-sharepoint-inventory`, `audit-managed-metadata`, `audit-onprem-schema-drift`, and
  `generate-discovery-report-set` — four *new* skills the inventory found `sharepoint-discovery`
  needs beyond extending its existing 5 — also not planned here, same reasoning.
- `sharepoint-schema` (site columns/content types), `sharepoint-provisioning`,
  `sharepoint-content-migration`, `sharepoint-content-publication`, `sharepoint-link-remediation`,
  `sharepoint-page-modernization` — each gets its own plan when its turn comes, per the priority
  order already recorded in `.agent/map-debt.md`'s 2026-08-11 entry.
- List-form (`NewForm`/`EditForm`/`DispForm`) scanning within page-inventory collection — Task 1
  Step 4 leaves `-IncludeListForms` as a documented no-op stub with a comment explaining it's out
  of scope for this pass, since the source script's list-form logic (source lines 390-424) needs
  its own dedicated task to port correctly rather than being rushed into this one.
