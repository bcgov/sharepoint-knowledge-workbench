<#
.SYNOPSIS
    audit-list-lookup-reconciliation.ps1
    Config-driven, read-only reconciliation of lookup columns between an on-premises SharePoint source and a SharePoint Online target.
.DESCRIPTION
    1. Reconciles identity lookups (lookups whose target list is -IdentityListName, or identity_mapping.list in the audit config) through a verified source-ID -> target-ID dictionary.
    2. Fully paginates large lists on both sides.
    3. Compares each item's business-key numeric suffix with its SharePoint Online item ID (suffix skew).
    4. Writes one variance CSV row per lookup field that differs or is populated on either side.

    Nothing site-specific lives in this script. The lists to audit, their lookup columns, the business-key columns and an optional
    exclusion list come from the JSON file passed as -AuditConfigPath (see audit-config.example.json). Lookup definitions can also be
    discovered from a wave dependency matrix passed as -MatrixPath. Connection details come from -ConfigPath (a config-*.psd1 file).
#>

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$ListName = "",

    [switch]$All,
    [switch]$Interactive,
    [Parameter(Mandatory)][string]$OnPremUrl,
    [switch]$UseDefaultCredentials,
    [string]$AuditConfigPath = "audit-config.json",
    [string]$ConfigPath = "config.psd1",
    [string]$MappingPath = ".agents/scratch/id-mapping-verified.json",
    [string]$MatrixPath = "",
    [string]$IdentityListName = "",
    [string]$OutputVarianceReport = ".agents/scratch/audit-reports/site-lookup-variance-audit.csv",
    [string]$ScratchDir = ".agents/scratch/pii-data",
    [switch]$SkipExtractIfCsvExists
)

. (Join-Path $PSScriptRoot "audit-helpers.ps1")

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host " CONFIG-DRIVEN LIST LOOKUP RECONCILIATION AUDITOR              " -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

# 1. Load verified identity-list ID dictionary
if (-not (Test-Path $MappingPath)) {
    throw "Verified ID mapping table not found at: $MappingPath"
}
$idMapJson = Get-Content $MappingPath -Raw | ConvertFrom-Json

# 2. Load the audit config (lists, lookup columns, business-key columns, exclusions)
if (-not (Test-Path $AuditConfigPath)) {
    throw "Audit config not found at: $AuditConfigPath (copy audit-config.example.json and describe the lists to audit)"
}
$auditCfg = Get-Content $AuditConfigPath -Raw | ConvertFrom-Json
$keyColumns = if ($auditCfg.PSObject.Properties['key_columns'] -and $auditCfg.key_columns) { @($auditCfg.key_columns) } else { @('Title') }
if (-not $IdentityListName -and $auditCfg.PSObject.Properties['identity_mapping'] -and $auditCfg.identity_mapping.PSObject.Properties['list']) { $IdentityListName = $auditCfg.identity_mapping.list }
if (-not $IdentityListName) { Write-Warning "No identity list set (-IdentityListName or identity_mapping.list in $AuditConfigPath): lookups will not be translated." }
$excludeLists = if ($auditCfg.PSObject.Properties['exclude_lists'] -and $auditCfg.exclude_lists) { @($auditCfg.exclude_lists) } else { @() }

# Identity lookup definitions per list: ListName -> list of { OnPremIdField, OnPremName, SpoField, Title }
$identityLookupDefMap = @{}
function Add-IdentityLookup([string]$list, [string]$onPremName, [string]$spoName, [string]$title) {
    if (-not $identityLookupDefMap.ContainsKey($list)) { $identityLookupDefMap[$list] = [System.Collections.Generic.List[PSCustomObject]]::new() }
    if ($identityLookupDefMap[$list].SpoField -contains $spoName) { return }
    $identityLookupDefMap[$list].Add([PSCustomObject]@{
        OnPremIdField = "${onPremName}Id"; OnPremName = $onPremName; SpoField = $spoName; Title = $title; IsIdentityLookup = $true })
}

# 2a. Lookups declared in the audit config: { "<list>": { "<spoColumn>": ["<onPremColumn>", "<targetList>"] } }
if ($auditCfg.PSObject.Properties['lookups']) {
    foreach ($listProp in $auditCfg.lookups.PSObject.Properties) {
        foreach ($colProp in $listProp.Value.PSObject.Properties) {
            $onPremName, $targetList = @($colProp.Value)
            if ($targetList -eq $IdentityListName) { Add-IdentityLookup $listProp.Name $onPremName $colProp.Name $colProp.Name }
        }
    }
}

# 2b. Optional: lookups discovered from a wave dependency matrix (entries with destinationName and fieldRenames)
if ($MatrixPath -and (Test-Path $MatrixPath)) {
    foreach ($entry in (Get-Content $MatrixPath -Raw | ConvertFrom-Json)) {
        if (-not $entry.destinationName -or -not $entry.PSObject.Properties['fieldRenames']) { continue }
        foreach ($fr in $entry.fieldRenames) {
            if ($fr.type -like "*Lookup*" -and $fr.lookupList -eq $IdentityListName) {
                $title = if ($fr.PSObject.Properties['sp2016DisplayName'] -and $fr.sp2016DisplayName) { $fr.sp2016DisplayName } else { $fr.spo }
                Add-IdentityLookup $entry.destinationName $fr.onPrem $fr.spo $title
            }
        }
    }
}
foreach ($k in @($identityLookupDefMap.Keys)) { $identityLookupDefMap[$k.Replace("_"," ")] = $identityLookupDefMap[$k] }

# 3. Setup Connections
if (-not (Test-Path $ScratchDir)) { New-Item -ItemType Directory -Path $ScratchDir -Force | Out-Null }
$outReportDir = Split-Path $OutputVarianceReport -Parent
if ($outReportDir -and -not (Test-Path $outReportDir)) { New-Item -ItemType Directory -Path $outReportDir -Force | Out-Null }
$headers = @{ "Accept" = "application/json;odata=verbose" }
$onPremCred = $null
if (-not $UseDefaultCredentials) {
    $onPremCred = Get-Credential -Message "On-premises SharePoint credentials"
}

$cfgHash = Import-PowerShellDataFile $ConfigPath
Import-Module PnP.PowerShell -ErrorAction Stop
Connect-PnPOnline -Url $cfgHash.SiteUrl -ClientId $cfgHash.ClientId -Tenant $cfgHash.TenantId -Interactive -ErrorAction Stop

# Target lists to audit: the config's "lists", else every list that has a configured lookup; minus exclusions
$businessListsToAudit = @(
    $(if ($auditCfg.PSObject.Properties['lists'] -and $auditCfg.lists) { @($auditCfg.lists) } else { @($identityLookupDefMap.Keys | Where-Object { $_ -notmatch ' ' }) }) |
        Where-Object { $_ -notin $excludeLists } | Sort-Object -Unique
)
if ($businessListsToAudit.Count -eq 0) { throw "No lists to audit: set 'lists' (or 'lookups') in $AuditConfigPath." }

$targetLists = @()
if ($ListName -and $ListName -ne "All" -and $ListName -ne "*") {
    $targetLists = @($businessListsToAudit | Where-Object { $_ -like "*$ListName*" })
    if ($targetLists.Count -eq 0) { $targetLists = @($ListName) }
} elseif ($All) {
    $targetLists = $businessListsToAudit
} elseif ($Interactive -or [string]::IsNullOrWhiteSpace($ListName)) {
    Write-Host "`nSelect an audit scope or specific list:" -ForegroundColor Yellow
    Write-Host "  [0] Audit ALL configured lists ($($businessListsToAudit.Count) Lists)" -ForegroundColor Green
    for ($i = 0; $i -lt $businessListsToAudit.Count; $i++) {
        Write-Host "  [$($i+1)] $($businessListsToAudit[$i])"
    }
    $choice = Read-Host "`nEnter selection (0-$($businessListsToAudit.Count)) [Default: 0 - ALL]"
    if ([string]::IsNullOrWhiteSpace($choice) -or $choice -eq "0") {
        $targetLists = $businessListsToAudit
    } else {
        $idx = [int]$choice - 1
        if ($idx -ge 0 -and $idx -lt $businessListsToAudit.Count) {
            $targetLists = @($businessListsToAudit[$idx])
        } else {
            $targetLists = $businessListsToAudit
        }
    }
} else {
    $targetLists = $businessListsToAudit
}

Write-Host "`nTarget Scope: $($targetLists.Count) list(s) to audit: $($targetLists -join ', ')" -ForegroundColor Cyan

$allContentVariances = [System.Collections.Generic.List[PSCustomObject]]::new()
$allSchemaVariances = [System.Collections.Generic.List[PSCustomObject]]::new()

foreach ($srcTitle in $targetLists) {
    $safeTitle = $srcTitle.Replace(" ", "_")
    Write-Host "`n=================================================================" -ForegroundColor DarkCyan
    Write-Host " AUDITING LIST: $srcTitle                                        " -ForegroundColor DarkCyan
    Write-Host "=================================================================" -ForegroundColor DarkCyan

    $lookupCols = if ($identityLookupDefMap.ContainsKey($srcTitle)) { $identityLookupDefMap[$srcTitle] } 
                  elseif ($identityLookupDefMap.ContainsKey($safeTitle)) { $identityLookupDefMap[$safeTitle] } 
                  else { [System.Collections.Generic.List[PSCustomObject]]::new() }

    # Fetch On-Prem Items with full pagination
    $scratchCsv = Join-Path $ScratchDir "$($safeTitle)-onprem-lookups.csv"
    $onPremData = $null

    if ($SkipExtractIfCsvExists -and (Test-Path $scratchCsv)) {
        Write-Host "  Loading cached on-prem extract ($scratchCsv)..." -ForegroundColor DarkGray
        $onPremData = Import-Csv -Path $scratchCsv
    } else {
        Write-Host "  Querying on-premises SharePoint for '$srcTitle'..." -ForegroundColor Yellow
        $onPremListUrl = "$OnPremUrl/_api/web/lists/getbytitle('$(ConvertTo-ODataListTitle $srcTitle)')/items?`$top=5000"
        
        $extractedRows = [System.Collections.Generic.List[PSCustomObject]]::new()
        $nextUrl = $onPremListUrl

        while ($nextUrl) {
            try {
                $raw = if ($UseDefaultCredentials) {
                    Invoke-WebRequest -Uri $nextUrl -Headers $headers -UseDefaultCredentials -ErrorAction Stop
                } else {
                    Invoke-WebRequest -Uri $nextUrl -Headers $headers -Credential $onPremCred -ErrorAction Stop
                }
            } catch {
                Write-Warning "  Could not query on-prem list '$srcTitle': $($_.Exception.Message)"
                break
            }

            $clean = ($raw.Content -creplace '"ID"\s*:', '"__sp_ID__":') | ConvertFrom-Json
            $items = if ($clean.PSObject.Properties['d']) { $clean.d.results } else { $clean.value }

            foreach ($it in $items) {
                $caseNum = $null
                foreach ($kc in $keyColumns) {
                    $kProp = $it.PSObject.Properties[$kc]
                    if ($kProp -and $kProp.Value) { $caseNum = [string]$kProp.Value; break }
                }
                if (-not $caseNum) {
                    $idVal = if ($it.PSObject.Properties['__sp_ID__']) { $it.__sp_ID__ } else { $it.Id }
                    $caseNum = "ITEM_$idVal"
                }

                $tVal = if ($it.PSObject.Properties['Title']) { [string]$it.Title } else { "" }
                $rowObj = [ordered]@{
                    OnPremID   = if ($it.PSObject.Properties['__sp_ID__']) { [int]$it.__sp_ID__ } else { [int]$it.Id }
                    BusinessKey = $caseNum.Trim()
                    Title      = $tVal
                }

                foreach ($f in $lookupCols) {
                    $propName = $f.OnPremIdField
                    $valObj = $it.PSObject.Properties[$propName]
                    $val = if ($valObj) { $valObj.Value } else { $null }

                    $idList = [System.Collections.Generic.List[int]]::new()
                    if ($null -ne $val) {
                        if ($val -is [int]) {
                            $idList.Add($val)
                        } elseif ($val.PSObject.Properties['results']) {
                            foreach ($r in $val.results) {
                                if ($r -match '^\d+$') { $idList.Add([int]$r) }
                            }
                        } elseif ([string]$val -match '^\d+$') {
                            $idList.Add([int]$val)
                        }
                    }
                    $rowObj[$f.SpoField] = ($idList -join ',')
                }
                $extractedRows.Add([PSCustomObject]$rowObj)
            }

            $nextProp = $clean.d.PSObject.Properties['__next']
            $nextUrl = if ($nextProp) { $nextProp.Value } else { $null }
        }

        $extractedRows | Export-Csv -Path $scratchCsv -NoTypeInformation -Encoding UTF8
        $onPremData = $extractedRows
        Write-Host "  Retrieved $($extractedRows.Count) rows from on-prem." -ForegroundColor Green
    }

    # Query SPO Target
    $spoList = Get-PnPList -Identity $srcTitle -ErrorAction SilentlyContinue
    if (-not $spoList) { $spoList = Get-PnPList -Identity $safeTitle -ErrorAction SilentlyContinue }
    if (-not $spoList) {
        Write-Warning "  List '$srcTitle' not found on SPO site. Skipping."
        continue
    }

    $allSpoFields = Get-PnPField -List $spoList.Title | Select-Object -ExpandProperty InternalName
    $caseIdField = @($keyColumns | Where-Object { $_ -in $allSpoFields })[0]
    if (-not $caseIdField) { $caseIdField = "Title" }

    $spoQueryFields = @("ID","Title") + @($lookupCols.SpoField | Where-Object { $_ -in $allSpoFields })
    if ($caseIdField -notin $spoQueryFields) { $spoQueryFields += $caseIdField }

    Write-Host "  Querying Live SPO for '$($spoList.Title)'..." -ForegroundColor Yellow
    $spoItems = @(Get-PnPListItem -List $spoList.Title -PageSize 2000 -Fields $spoQueryFields)
    Write-Host "  Retrieved $($spoItems.Count) rows from live SPO." -ForegroundColor Green

    $spoByCaseKey = @{}
    foreach ($it in $spoItems) {
        $cVal = [string]$it[$caseIdField]
        if (-not $cVal) { $cVal = [string]$it['Title'] }
        if ($cVal) {
            $spoByCaseKey[$cVal.Trim().ToUpper()] = $it
        }
    }

    # Compare content & lookups
    foreach ($opCase in $onPremData) {
        $caseNum = $opCase.BusinessKey
        $cKey = $caseNum.ToUpper()
        $opId = [int]$opCase.OnPremID

        $spoItem = if ($spoByCaseKey.ContainsKey($cKey)) { $spoByCaseKey[$cKey] } else { $null }
        if ($null -eq $spoItem) {
            # Skip items that only exist on-prem (e.g. newly created on-prem records not yet migrated to SPO)
            continue
        }
        $spoItemId = [string]$spoItem.Id

        # Suffix Skew
        $extractedSuffix = ""
        $isSuffixMatched = "NO_DIGITS"
        $idOffset = ""

        if ($caseNum -match '(\d+)$') {
            $suffixInt = [int]$Matches[1]
            $extractedSuffix = [string]$suffixInt
            if ($spoItemId -ne "NOT_IN_SPO") {
                $spoIntId = [int]$spoItemId
                if ($spoIntId -eq $suffixInt) {
                    $isSuffixMatched = "MATCH"
                    $idOffset = "0"
                } else {
                    $isSuffixMatched = "SKEWED"
                    $delta = $spoIntId - $suffixInt
                    $idOffset = $(if ($delta -gt 0) { "+$delta" } else { "$delta" })
                }
            }
        }

        foreach ($f in $lookupCols) {
            $spoField = $f.SpoField
            $title = $f.Title
            $rawOnPrem = [string]$opCase.$spoField

            $expectedSpoIds = [System.Collections.Generic.List[int]]::new()
            if (-not [string]::IsNullOrWhiteSpace($rawOnPrem)) {
                $opIds = $rawOnPrem -split '[,;\s]+' | Where-Object { $_ -match '^\d+$' }
                foreach ($oldId in $opIds) {
                    if ($idMapJson.PSObject.Properties[$oldId]) {
                        $expectedSpoIds.Add([int]$idMapJson.$oldId)
                    }
                }
            }

            $actualSpoIds = [System.Collections.Generic.List[int]]::new()
            if ($null -ne $spoItem -and $spoField -in $allSpoFields) {
                $val = $spoItem[$spoField]
                if ($null -ne $val -and "" -ne $val) {
                    if ($val -is [Microsoft.SharePoint.Client.FieldLookupValue]) {
                        $actualSpoIds.Add($val.LookupId)
                    } elseif ($val -is [System.Collections.IEnumerable] -and $val -isnot [string]) {
                        foreach ($sub in $val) {
                            if ($sub -is [Microsoft.SharePoint.Client.FieldLookupValue]) { $actualSpoIds.Add($sub.LookupId) }
                            elseif ($sub.PSObject.Properties['LookupId']) { $actualSpoIds.Add([int]$sub.LookupId) }
                            elseif ($sub -is [int]) { $actualSpoIds.Add($sub) }
                        }
                    } elseif ($val.PSObject.Properties['LookupId']) {
                        $actualSpoIds.Add([int]$val.LookupId)
                    }
                }
            }

            if ($expectedSpoIds.Count -eq 0 -and $actualSpoIds.Count -eq 0) {
                continue
            }

            $expSet = [System.Collections.Generic.HashSet[int]]::new($expectedSpoIds)
            $actSet = [System.Collections.Generic.HashSet[int]]::new($actualSpoIds)

            $matches = [System.Collections.Generic.HashSet[int]]::new($expSet)
            $matches.IntersectWith($actSet)

            $missing = [System.Collections.Generic.HashSet[int]]::new($expSet)
            $missing.ExceptWith($actSet)

            $extra = [System.Collections.Generic.HashSet[int]]::new($actSet)
            $extra.ExceptWith($expSet)

            $status = if ($expSet.SetEquals($actSet)) {
                "MATCH"
            } elseif ($actSet.Count -eq 0 -and $expSet.Count -gt 0) {
                "MISSING_IN_SPO"
            } elseif ($matches.Count -eq 0 -and $actSet.Count -gt 0) {
                "FALSE_MATCH"
            } else {
                "PARTIAL_MATCH"
            }

            $allContentVariances.Add([PSCustomObject]@{
                ListName          = $srcTitle
                BusinessKey       = $caseNum
                OnPremID          = $opId
                SpoItemID         = $spoItemId
                KeySuffix         = $extractedSuffix
                SuffixMatchStatus = $isSuffixMatched
                IDOffsetDelta     = $idOffset
                FieldTitle        = $title
                InternalField     = $spoField
                OnPremSourceIDs   = $rawOnPrem
                ExpectedSpoIDs    = ($expectedSpoIds -join ',')
                ActualSpoIDs      = ($actualSpoIds -join ',')
                Status            = $status
                MatchedCount      = $matches.Count
                MissingCount      = $missing.Count
                ExtraOrWrongCount = $extra.Count
            })
        }
    }
}

# Export Clean Variance Report
$allContentVariances | Export-Csv -Path $OutputVarianceReport -NoTypeInformation -Encoding UTF8
Write-Host "`n=================================================================" -ForegroundColor Cyan
Write-Host " AUDIT COMPLETE ACROSS $($targetLists.Count) BUSINESS LIST(S)   " -ForegroundColor Cyan
Write-Host " Content Variance Report : $OutputVarianceReport                 " -ForegroundColor Green
Write-Host " Run 'python analyze-lookup-variances.py' for summary metrics." -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Cyan
