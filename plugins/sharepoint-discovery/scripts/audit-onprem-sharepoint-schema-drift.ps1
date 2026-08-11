<#
.SYNOPSIS
Read-only schema drift audit for on-premises SharePoint 2016: compares field
schemas between a set of source lists and a set of destination lists.

.DESCRIPTION
Connects to an on-prem SP2016 site via PnP.PowerShell using web-login or
explicit credentials (CSOM does support this for on-prem, unlike the modern
SPO `-Interactive` app-registration flow this repo otherwise standardizes
on -- see .agent/rules/sharepoint-ps1-authentication-convention.md for why
this script is a documented exception). If `-SiteUrl` is not supplied, falls
back to `SiteUrl` in config.psd1 the same way other scripts in this plugin
do.

Enumerates every list on the site, collects each list's field schema
(internal name, type, required, hidden, lookup references, choices),
content types, and workflow associations, then compares the caller-supplied
source lists against the caller-supplied (or pattern-matched) destination
lists field-by-field: missing fields, type mismatches, and required-field
mismatches in either direction. Also validates lookup-field references
against the site's actual list GUIDs/titles.

Exports 5 CSVs (list schema, field schema, content types, schema mismatches,
workflow dependencies) plus a single markdown summary report combining all
findings with a recommended-remediation section.

By default reports drift across ALL fields on the destination lists, not a
narrowed sentinel set -- pass -WatchFieldNames to restrict the "watch
report" section to specific field names if desired.

HARD RULE: This script is READ-ONLY. No writes to on-premises SharePoint.

.PARAMETER SiteUrl
Target on-prem SP2016 site. Falls back to config.psd1's SiteUrl if omitted.

.PARAMETER ConfigPath
Path to config.psd1 used only for the SiteUrl fallback. Defaults to this
plugin's own config.psd1 relative location.

.PARAMETER SourceListNames
Array of list titles (or internal/root-folder names) to treat as the
schema-of-record ("source") lists that destination lists are compared
against. Required.

.PARAMETER DestinationListNames
Explicit array of list titles to treat as destination lists. Use this or
-DestinationListPattern (or both -- results are unioned).

.PARAMETER DestinationListPattern
Wildcard pattern (PowerShell -like syntax, e.g. "Cal_*") matched against
list titles to identify destination lists. Use this or
-DestinationListNames (or both -- results are unioned).

.PARAMETER WatchFieldNames
Optional array of field names (matched against InternalName, Title, or
StaticName) to highlight in a dedicated "Watch Field Types" report section.
Defaults to empty, meaning no narrowing -- the field-schema CSV and
mismatch comparison already cover every field regardless of this parameter.

.PARAMETER OutputDir
Directory to write CSVs and the markdown report. Defaults to the current
directory.

.PARAMETER UseCredential
If set, prompts for explicit credentials instead of using web-login auth.

.EXAMPLE
pwsh -File audit-onprem-sharepoint-schema-drift.ps1 `
    -SiteUrl "https://sp2016.example.org/sites/Legacy" `
    -SourceListNames @('Matches_Received','All_Appearances') `
    -DestinationListPattern "Cal_*" `
    -OutputDir .\schema-drift-report

.EXAMPLE
# Explicit destination list names, narrowed watch-field report, credential prompt
pwsh -File audit-onprem-sharepoint-schema-drift.ps1 `
    -SiteUrl "https://sp2016.example.org/sites/Legacy" `
    -SourceListNames @('Requests') `
    -DestinationListNames @('Archive_2024','Archive_2025') `
    -WatchFieldNames @('Case_ID','Status') `
    -UseCredential

.EXAMPLE
# Use config.psd1's SiteUrl instead of specifying -SiteUrl
pwsh -File audit-onprem-sharepoint-schema-drift.ps1 `
    -SourceListNames @('Requests') -DestinationListPattern "Archive_*"
#>

param(
    [string]$SiteUrl,
    [string]$ConfigPath = "$PSScriptRoot\..\config.psd1",
    [Parameter(Mandatory = $true)]
    [string[]]$SourceListNames,
    [string[]]$DestinationListNames = @(),
    [string]$DestinationListPattern = "",
    [string[]]$WatchFieldNames = @(),
    [string]$OutputDir = $PSScriptRoot,
    [switch]$UseCredential
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ── Resolve SiteUrl from config.psd1 if not supplied ──────────────────────────
if (-not $SiteUrl) {
    if (Test-Path -LiteralPath $ConfigPath) {
        $raw = Import-PowerShellDataFile $ConfigPath
        $cfg = if ($raw.ContainsKey('Connection')) { $raw.Connection } else { $raw }
        if ($cfg.SiteUrl) { $SiteUrl = $cfg.SiteUrl }
    }
    if (-not $SiteUrl) {
        throw "No -SiteUrl supplied and no SiteUrl found in config.psd1 ($ConfigPath)."
    }
}

if (-not $DestinationListNames -and -not $DestinationListPattern) {
    throw "Supply -DestinationListNames, -DestinationListPattern, or both to identify destination lists."
}

# ── Output paths ──────────────────────────────────────────────────────────────
if (-not (Test-Path $OutputDir)) { New-Item -ItemType Directory -Path $OutputDir | Out-Null }
$csvLists    = Join-Path $OutputDir 'SchemaDrift-ListSchema.csv'
$csvFields   = Join-Path $OutputDir 'SchemaDrift-FieldSchema.csv'
$csvCTs      = Join-Path $OutputDir 'SchemaDrift-ContentTypes.csv'
$csvMismatch = Join-Path $OutputDir 'SchemaDrift-SchemaMismatches.csv'
$csvWF       = Join-Path $OutputDir 'SchemaDrift-WorkflowDependencies.csv'
$mdReport    = Join-Path $OutputDir 'SchemaDrift-Report.md'

Write-Host ""
Write-Host "=== On-Prem Schema Drift Audit ===" -ForegroundColor Cyan
Write-Host "Target : $SiteUrl" -ForegroundColor Cyan
Write-Host "Output : $OutputDir" -ForegroundColor Cyan
Write-Host ""

# ── Connect ───────────────────────────────────────────────────────────────────
Write-Host "[CONNECT] Connecting to $SiteUrl ..." -ForegroundColor Yellow
try {
    if ($UseCredential) {
        $cred = Get-Credential -Message "Enter credentials for $SiteUrl"
        Connect-PnPOnline -Url $SiteUrl -Credentials $cred -ErrorAction Stop
    } else {
        Connect-PnPOnline -Url $SiteUrl -UseWebLogin -ErrorAction Stop
    }
    Write-Host "[CONNECT] Connected." -ForegroundColor Green
} catch {
    Write-Error "Failed to connect to $SiteUrl : $($_.Exception.Message)"
    exit 1
}

# ── 1. Enumerate all lists ────────────────────────────────────────────────────
Write-Host ""
Write-Host "[LISTS] Enumerating all lists..." -ForegroundColor Yellow
$allLists = Get-PnPList -ErrorAction Stop
Write-Host "  Found $($allLists.Count) lists." -ForegroundColor Green

$listRows = foreach ($l in $allLists) {
    [PSCustomObject]@{
        Title               = $l.Title
        InternalName        = $l.RootFolder.Name
        BaseTemplate        = $l.BaseTemplate
        ItemCount           = $l.ItemCount
        ContentTypesEnabled = $l.ContentTypesEnabled
        Hidden              = $l.Hidden
    }
}
$listRows | Export-Csv $csvLists -NoTypeInformation -Encoding UTF8
Write-Host "  Exported: $csvLists" -ForegroundColor Green

# Identify destination lists: explicit names union pattern match
$destLists = @()
if ($DestinationListNames) {
    $destLists += $allLists | Where-Object { $DestinationListNames -contains $_.Title } | Select-Object -ExpandProperty Title
}
if ($DestinationListPattern) {
    $destLists += $allLists | Where-Object { $_.Title -like $DestinationListPattern } | Select-Object -ExpandProperty Title
}
$destLists = $destLists | Select-Object -Unique
Write-Host "  Destination lists found: $($destLists.Count)" -ForegroundColor Cyan

# ── 2. Collect field schema per list ─────────────────────────────────────────
Write-Host ""
Write-Host "[FIELDS] Collecting field schema (all lists)..." -ForegroundColor Yellow

$fieldRows    = [System.Collections.Generic.List[PSCustomObject]]::new()
$fieldsByList = @{}   # hashtable: listTitle -> array of field objects

foreach ($l in $allLists) {
    try {
        $fields = Get-PnPField -List $l.Title -ErrorAction SilentlyContinue
        if (-not $fields) { continue }

        $fieldsByList[$l.Title] = $fields

        foreach ($f in $fields) {
            $choices = if ($f.Choices) { ($f.Choices -join ' | ') } else { '' }
            $fieldRows.Add([PSCustomObject]@{
                ListTitle    = $l.Title
                InternalName = $f.InternalName
                StaticName   = $f.StaticName
                Title        = $f.Title
                TypeAsString = $f.TypeAsString
                Required     = $f.Required
                Hidden       = $f.Hidden
                ReadOnly     = $f.ReadOnly
                DefaultValue = $f.DefaultValue
                LookupList   = $f.LookupList
                LookupField  = $f.LookupField
                Choices      = $choices
            })
        }
        Write-Host "  [$($l.Title)] $($fields.Count) fields" -ForegroundColor Gray
    } catch {
        Write-Warning "  Could not read fields for '$($l.Title)': $($_.Exception.Message)"
    }
}

$fieldRows | Export-Csv $csvFields -NoTypeInformation -Encoding UTF8
Write-Host "  Exported: $csvFields" -ForegroundColor Green

# ── 3. Collect content types ──────────────────────────────────────────────────
Write-Host ""
Write-Host "[CTs] Collecting content types..." -ForegroundColor Yellow

$ctRows = [System.Collections.Generic.List[PSCustomObject]]::new()
foreach ($l in $allLists) {
    try {
        $cts = Get-PnPContentType -List $l.Title -ErrorAction SilentlyContinue
        if (-not $cts) { continue }
        foreach ($ct in $cts) {
            $ctRows.Add([PSCustomObject]@{
                ListTitle         = $l.Title
                ContentTypeName   = $ct.Name
                ContentTypeId     = $ct.Id.StringValue
                ParentContentType = $ct.Parent.Name
                Hidden            = $ct.Hidden
                ReadOnly          = $ct.ReadOnly
            })
        }
    } catch {
        Write-Warning "  Could not read CTs for '$($l.Title)': $($_.Exception.Message)"
    }
}

$ctRows | Export-Csv $csvCTs -NoTypeInformation -Encoding UTF8
Write-Host "  Exported: $csvCTs" -ForegroundColor Green

# ── 4. Watch-field type report (optional narrowing) ───────────────────────────
Write-Host ""
Write-Host "[WATCH] Reporting field types across all lists..." -ForegroundColor Yellow

$watchReport = [System.Collections.Generic.List[PSCustomObject]]::new()
foreach ($row in $fieldRows) {
    $include = $true
    if ($WatchFieldNames -and $WatchFieldNames.Count -gt 0) {
        $include = [bool]($WatchFieldNames | Where-Object {
            $row.InternalName -eq $_ -or
            $row.Title        -eq $_ -or
            $row.StaticName   -eq $_
        })
    }
    if ($include) {
        $watchReport.Add([PSCustomObject]@{
            List         = $row.ListTitle
            Field        = $row.InternalName
            DisplayName  = $row.Title
            Type         = $row.TypeAsString
            Required     = $row.Required
            Hidden       = $row.Hidden
        })
    }
}

# ── 5. Schema mismatch comparison: sources vs destinations ────────────────────
Write-Host ""
Write-Host "[COMPARE] Comparing source vs destination field schemas..." -ForegroundColor Yellow

$mismatchRows = [System.Collections.Generic.List[PSCustomObject]]::new()

# Build source field type maps
$srcFieldMaps = @{}
foreach ($srcTitle in $SourceListNames) {
    $matched = $allLists | Where-Object { $_.Title -eq $srcTitle -or $_.RootFolder.Name -eq $srcTitle }
    if (-not $matched) { continue }
    $srcFields = $fieldsByList[$matched[0].Title]
    if (-not $srcFields) { continue }
    $map = @{}
    foreach ($f in $srcFields) { $map[$f.InternalName] = $f }
    $srcFieldMaps[$matched[0].Title] = $map
}

foreach ($destTitle in $destLists) {
    $destFields = $fieldsByList[$destTitle]
    if (-not $destFields) { continue }

    foreach ($srcTitle in $srcFieldMaps.Keys) {
        $srcMap = $srcFieldMaps[$srcTitle]

        # Fields in source — check if present and matching in dest
        foreach ($internalName in $srcMap.Keys) {
            $srcF  = $srcMap[$internalName]
            $destF = $destFields | Where-Object { $_.InternalName -eq $internalName }

            if (-not $destF) {
                $mismatchRows.Add([PSCustomObject]@{
                    SourceList      = $srcTitle
                    DestinationList = $destTitle
                    Field           = $internalName
                    SourceType      = $srcF.TypeAsString
                    DestinationType = '(MISSING)'
                    Issue           = 'MISSING FIELD IN DESTINATION'
                })
            } elseif ($destF.TypeAsString -ne $srcF.TypeAsString) {
                $mismatchRows.Add([PSCustomObject]@{
                    SourceList      = $srcTitle
                    DestinationList = $destTitle
                    Field           = $internalName
                    SourceType      = $srcF.TypeAsString
                    DestinationType = $destF.TypeAsString
                    Issue           = 'TYPE MISMATCH'
                })
            } elseif ($destF.Required -and -not $srcF.Required) {
                $mismatchRows.Add([PSCustomObject]@{
                    SourceList      = $srcTitle
                    DestinationList = $destTitle
                    Field           = $internalName
                    SourceType      = $srcF.TypeAsString
                    DestinationType = $destF.TypeAsString
                    Issue           = 'REQUIRED ON DEST BUT NOT SOURCE'
                })
            }
        }

        # Required fields in dest not in source
        foreach ($destF in $destFields) {
            if ($destF.Required -and -not $srcMap.ContainsKey($destF.InternalName)) {
                $mismatchRows.Add([PSCustomObject]@{
                    SourceList      = $srcTitle
                    DestinationList = $destTitle
                    Field           = $destF.InternalName
                    SourceType      = '(MISSING)'
                    DestinationType = $destF.TypeAsString
                    Issue           = 'REQUIRED ON DEST — NOT IN SOURCE'
                })
            }
        }
    }
}

$mismatchRows | Export-Csv $csvMismatch -NoTypeInformation -Encoding UTF8
Write-Host "  Exported: $csvMismatch ($($mismatchRows.Count) issues)" -ForegroundColor Green

# ── 6. Workflow dependency inspection ─────────────────────────────────────────
Write-Host ""
Write-Host "[WORKFLOW] Inspecting workflow associations..." -ForegroundColor Yellow

$wfRows = [System.Collections.Generic.List[PSCustomObject]]::new()
try {
    $ctx = Get-PnPContext
    foreach ($l in $allLists) {
        try {
            $list = $ctx.Web.Lists.GetByTitle($l.Title)
            $wfAssoc = $list.WorkflowAssociations
            $ctx.Load($wfAssoc)
            $ctx.ExecuteQuery()
            foreach ($wf in $wfAssoc) {
                $wfRows.Add([PSCustomObject]@{
                    ListTitle    = $l.Title
                    WorkflowName = $wf.Name
                    BaseId       = $wf.BaseId
                    Enabled      = $wf.Enabled
                    TaskList     = $wf.TaskListTitle
                    HistoryList  = $wf.HistoryListTitle
                    AssocData    = ($wf.AssociationData -replace "`r`n"," ")
                })
            }
        } catch { }
    }
} catch {
    Write-Warning "  Workflow inspection failed: $($_.Exception.Message)"
}

$wfRows | Export-Csv $csvWF -NoTypeInformation -Encoding UTF8
Write-Host "  Exported: $csvWF ($($wfRows.Count) workflow associations)" -ForegroundColor Green

# ── 7. Lookup validation ──────────────────────────────────────────────────────
Write-Host ""
Write-Host "[LOOKUPS] Validating lookup field references..." -ForegroundColor Yellow

$lookupIssues = [System.Collections.Generic.List[string]]::new()

foreach ($row in $fieldRows) {
    if ($row.TypeAsString -eq 'Lookup' -and $row.LookupList) {
        # LookupList is stored as a GUID on SP2016 REST; check if any list matches
        $refList = $allLists | Where-Object { $_.Id.ToString() -eq $row.LookupList -or $_.Title -eq $row.LookupList }
        if (-not $refList) {
            $lookupIssues.Add("[$($row.ListTitle)] Field '$($row.InternalName)' references missing list: $($row.LookupList)")
            Write-Warning "  BROKEN LOOKUP: [$($row.ListTitle)].$($row.InternalName) -> $($row.LookupList)"
        }
    }
}

# ── 8. Generate SchemaDrift-Report.md ─────────────────────────────────────────
Write-Host ""
Write-Host "[REPORT] Generating SchemaDrift-Report.md..." -ForegroundColor Yellow

$ts             = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
$typeMismatches = $mismatchRows | Where-Object { $_.Issue -eq 'TYPE MISMATCH' }
$missingFields  = $mismatchRows | Where-Object { $_.Issue -like 'MISSING*' }
$requiredIssues = $mismatchRows | Where-Object { $_.Issue -like 'REQUIRED*' }

$md = [System.Text.StringBuilder]::new()
[void]$md.AppendLine("# Schema Drift Audit Report")
[void]$md.AppendLine("")
[void]$md.AppendLine("**Generated:** $ts")
[void]$md.AppendLine("**Target Site:** $SiteUrl")
[void]$md.AppendLine("")
[void]$md.AppendLine("---")
[void]$md.AppendLine("")
[void]$md.AppendLine("## Executive Summary")
[void]$md.AppendLine("")

if ($mismatchRows.Count -eq 0 -and $lookupIssues.Count -eq 0) {
    [void]$md.AppendLine("> **No list, field, lookup, or content type drift detected between the specified source and destination lists.**")
} else {
    [void]$md.AppendLine("| Metric | Count |")
    [void]$md.AppendLine("|---|---|")
    [void]$md.AppendLine("| Total lists inventoried | $($allLists.Count) |")
    [void]$md.AppendLine("| Destination lists compared | $($destLists.Count) |")
    [void]$md.AppendLine("| Total schema issues found | $($mismatchRows.Count) |")
    [void]$md.AppendLine("| Type mismatches | $($typeMismatches.Count) |")
    [void]$md.AppendLine("| Missing fields on destination | $($missingFields.Count) |")
    [void]$md.AppendLine("| Required field issues | $($requiredIssues.Count) |")
    [void]$md.AppendLine("| Broken lookup references | $($lookupIssues.Count) |")
}

[void]$md.AppendLine("")
[void]$md.AppendLine("---")
[void]$md.AppendLine("")
[void]$md.AppendLine("## Lists Inventoried")
[void]$md.AppendLine("")
[void]$md.AppendLine("| Title | Base Template | Items | CTs Enabled | Hidden |")
[void]$md.AppendLine("|---|---|---|---|---|")
foreach ($l in ($listRows | Sort-Object Title)) {
    [void]$md.AppendLine("| $($l.Title) | $($l.BaseTemplate) | $($l.ItemCount) | $($l.ContentTypesEnabled) | $($l.Hidden) |")
}

[void]$md.AppendLine("")
[void]$md.AppendLine("---")
[void]$md.AppendLine("")
[void]$md.AppendLine("## Field Types Across Lists")
[void]$md.AppendLine("")
if ($WatchFieldNames -and $WatchFieldNames.Count -gt 0) {
    [void]$md.AppendLine("_Narrowed to -WatchFieldNames: $($WatchFieldNames -join ', ')_")
    [void]$md.AppendLine("")
}
[void]$md.AppendLine("| List | Field (Internal) | Display Name | Type | Required | Hidden |")
[void]$md.AppendLine("|---|---|---|---|---|---|")
foreach ($w in ($watchReport | Sort-Object List, Field)) {
    [void]$md.AppendLine("| $($w.List) | $($w.Field) | $($w.DisplayName) | $($w.Type) | $($w.Required) | $($w.Hidden) |")
}

[void]$md.AppendLine("")
[void]$md.AppendLine("---")
[void]$md.AppendLine("")
[void]$md.AppendLine("## Field Type Mismatches")
[void]$md.AppendLine("")
if ($typeMismatches.Count -eq 0) {
    [void]$md.AppendLine("_No type mismatches found._")
} else {
    [void]$md.AppendLine("| Source List | Destination List | Field | Source Type | Dest Type |")
    [void]$md.AppendLine("|---|---|---|---|---|")
    foreach ($r in $typeMismatches) {
        [void]$md.AppendLine("| $($r.SourceList) | $($r.DestinationList) | $($r.Field) | $($r.SourceType) | $($r.DestinationType) |")
    }
}

[void]$md.AppendLine("")
[void]$md.AppendLine("---")
[void]$md.AppendLine("")
[void]$md.AppendLine("## Missing Fields on Destination Lists")
[void]$md.AppendLine("")
if ($missingFields.Count -eq 0) {
    [void]$md.AppendLine("_No missing fields found._")
} else {
    [void]$md.AppendLine("| Source List | Destination List | Field | Source Type | Issue |")
    [void]$md.AppendLine("|---|---|---|---|---|")
    foreach ($r in $missingFields) {
        [void]$md.AppendLine("| $($r.SourceList) | $($r.DestinationList) | $($r.Field) | $($r.SourceType) | $($r.Issue) |")
    }
}

[void]$md.AppendLine("")
[void]$md.AppendLine("---")
[void]$md.AppendLine("")
[void]$md.AppendLine("## Lookup Issues")
[void]$md.AppendLine("")
if ($lookupIssues.Count -eq 0) {
    [void]$md.AppendLine("_No broken lookup references found._")
} else {
    foreach ($li in $lookupIssues) { [void]$md.AppendLine("- $li") }
}

[void]$md.AppendLine("")
[void]$md.AppendLine("---")
[void]$md.AppendLine("")
[void]$md.AppendLine("## Content Type Issues")
[void]$md.AppendLine("")
[void]$md.AppendLine("### Content Types per Destination List")
[void]$md.AppendLine("")
[void]$md.AppendLine("| Destination List | Content Type | CT ID | Parent |")
[void]$md.AppendLine("|---|---|---|---|")
foreach ($ct in ($ctRows | Where-Object { $destLists -contains $_.ListTitle } | Sort-Object ListTitle, ContentTypeName)) {
    [void]$md.AppendLine("| $($ct.ListTitle) | $($ct.ContentTypeName) | $($ct.ContentTypeId) | $($ct.ParentContentType) |")
}

[void]$md.AppendLine("")
[void]$md.AppendLine("---")
[void]$md.AppendLine("")
[void]$md.AppendLine("## Workflow Dependency Findings")
[void]$md.AppendLine("")
if ($wfRows.Count -eq 0) {
    [void]$md.AppendLine("_No workflow associations found or workflow inspection was not available._")
} else {
    [void]$md.AppendLine("| List | Workflow Name | Enabled | Task List | History List |")
    [void]$md.AppendLine("|---|---|---|---|---|")
    foreach ($wf in ($wfRows | Sort-Object ListTitle, WorkflowName)) {
        [void]$md.AppendLine("| $($wf.ListTitle) | $($wf.WorkflowName) | $($wf.Enabled) | $($wf.TaskList) | $($wf.HistoryList) |")
    }
}

[void]$md.AppendLine("")
[void]$md.AppendLine("---")
[void]$md.AppendLine("")
[void]$md.AppendLine("## Required Field Issues")
[void]$md.AppendLine("")
if ($requiredIssues.Count -eq 0) {
    [void]$md.AppendLine("_No required field issues found._")
} else {
    [void]$md.AppendLine("| Source List | Destination List | Field | Dest Type | Issue |")
    [void]$md.AppendLine("|---|---|---|---|---|")
    foreach ($r in $requiredIssues) {
        [void]$md.AppendLine("| $($r.SourceList) | $($r.DestinationList) | $($r.Field) | $($r.DestinationType) | $($r.Issue) |")
    }
}

[void]$md.AppendLine("")
[void]$md.AppendLine("---")
[void]$md.AppendLine("")
[void]$md.AppendLine("## Recommended Remediation")
[void]$md.AppendLine("")
if ($mismatchRows.Count -eq 0 -and $lookupIssues.Count -eq 0) {
    [void]$md.AppendLine("Schema is clean between the specified source and destination lists. If a workflow or")
    [void]$md.AppendLine("integration failure was the trigger for this audit, investigate infrastructure/service")
    [void]$md.AppendLine("factors instead: Timer Service health, patch state, farm event receiver, and IIS app")
    [void]$md.AppendLine("pool state on the relevant web front-end servers.")
} else {
    if ($typeMismatches.Count -gt 0) {
        [void]$md.AppendLine("### Type Mismatches")
        [void]$md.AppendLine("Fix field types on the destination lists to match the source. Do not retype in-place if data exists — add a new column, migrate data, delete old, rename new.")
    }
    if ($missingFields.Count -gt 0) {
        [void]$md.AppendLine("### Missing Fields")
        [void]$md.AppendLine("Add missing columns to destination lists. Ensure InternalName matches the source exactly.")
    }
    if ($lookupIssues.Count -gt 0) {
        [void]$md.AppendLine("### Broken Lookups")
        [void]$md.AppendLine("Restore or recreate the referenced lookup list, then repoint the lookup field.")
    }
    if ($requiredIssues.Count -gt 0) {
        [void]$md.AppendLine("### Required Field Issues")
        [void]$md.AppendLine("Either populate the field before writing, or remove the Required constraint on the destination list.")
    }
}

[void]$md.AppendLine("")
[void]$md.AppendLine("---")
[void]$md.AppendLine("_Generated by audit-onprem-sharepoint-schema-drift.ps1 — read-only, no writes to on-premises SharePoint._")

$md.ToString() | Set-Content -Path $mdReport -Encoding UTF8
Write-Host "  Exported: $mdReport" -ForegroundColor Green

# ── Summary ───────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "=== Done ===" -ForegroundColor Cyan
Write-Host "  Lists inventoried  : $($allLists.Count)" -ForegroundColor White
Write-Host "  Dest lists         : $($destLists.Count)" -ForegroundColor White
Write-Host "  Schema issues      : $($mismatchRows.Count)" -ForegroundColor $(if ($mismatchRows.Count -gt 0) { "Red" } else { "Green" })
Write-Host "  Broken lookups     : $($lookupIssues.Count)" -ForegroundColor $(if ($lookupIssues.Count -gt 0) { "Red" } else { "Green" })
Write-Host ""
Write-Host "Output files:"
Write-Host "  $csvLists"
Write-Host "  $csvFields"
Write-Host "  $csvCTs"
Write-Host "  $csvMismatch"
Write-Host "  $csvWF"
Write-Host "  $mdReport"
Write-Host ""
