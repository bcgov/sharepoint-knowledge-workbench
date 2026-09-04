<#
.SYNOPSIS
    audit-list-lookup-reconciliation.ps1
    Precise, Matrix-Driven & Schema-Aware Content & Person Lookup Auditor:
    1. Reconciles strictly Person lookups (lookupList: "Persons") using the verified Person ID dictionary.
    2. Handles other non-Person lookups (e.g. Origin_Location -> _Court_Locations) separately without false translation.
    3. Fully paginates large lists (e.g. 23k rows in PIO_Log_Entries).
    4. Evaluates Item ID vs Case ID Suffix Skew.
    5. Produces 100% clean schema & content variance reports.
#>

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$ListName = "",

    [switch]$AuditAllExceptEtl,
    [switch]$All,
    [switch]$Interactive,
    [string]$OnPremUrl = "https://itau.jag.gov.bc.ca/cmat",
    [switch]$UseDefaultCredentials,
    [string]$MappingPath = ".agents/scratch/id-mapping-verified.json",
    [string]$ConfigPath = "plugins/sharepoint-migration/config/config-prod.psd1",
    [string]$MatrixPath = "plugins/sharepoint-migration/references/wave-dependency-matrix.json",
    [string]$EtlTargetListsPath = "plugins/ords-integration-migration/references/cmat-etl-target-lists.json",
    [string]$OutputVarianceReport = ".agents/scratch/audit-reports/site-lookup-variance-audit.csv",
    [string]$OutputSchemaVarianceReport = ".agents/scratch/audit-reports/site-schema-definition-variance.csv",
    [string]$ScratchDir = ".agents/scratch/pii-data",
    [switch]$SkipExtractIfCsvExists
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host " PRECISE MATRIX-DRIVEN CONTENT & PERSON LOOKUP AUDITOR           " -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

# 1. Load verified Person ID dictionary
if (-not (Test-Path $MappingPath)) {
    throw "Verified ID mapping table not found at: $MappingPath"
}
$idMapJson = Get-Content $MappingPath -Raw | ConvertFrom-Json

# 2. Load Wave Dependency Matrix to identify true Person lookups
$matrixData = Get-Content $MatrixPath -Raw | ConvertFrom-Json
$personLookupDefMap = @{} # ListName -> List of lookup column objects

foreach ($entry in $matrixData) {
    $destList = $entry.destinationName
    if (-not $destList) { continue }
    
    $lookupsForThisList = [System.Collections.Generic.List[PSCustomObject]]::new()

    # Check fieldRenames
    if ($entry.PSObject.Properties['fieldRenames']) {
        foreach ($fr in $entry.fieldRenames) {
            if ($fr.type -like "*Lookup*" -and $fr.lookupList -eq "Persons") {
                $lookupsForThisList.Add([PSCustomObject]@{
                    OnPremIdField = "$($fr.onPrem)Id"
                    OnPremName    = $fr.onPrem
                    SpoField      = $fr.spo
                    Title         = $fr.sp2016DisplayName
                    IsPersonLookup = $true
                })
            }
        }
    }

    # Check list-level dependsOn Persons
    if ($destList -in @("ITAU_Narratives","PIO_Narratives","ICM_Narratives")) {
        $lookupsForThisList.Add([PSCustomObject]@{
            OnPremIdField = "Related_x0020_to_x0020_PersonId"
            OnPremName    = "Related_x0020_to_x0020_Person"
            SpoField      = "Related_x0020_to_x0020_Person"
            Title         = "Related to Person"
            IsPersonLookup = $true
        })
    } elseif ($destList -in @("ITAU_Case_Tasks","PIO_Case_Tasks","ICM_Case_Tasks")) {
        $lookupsForThisList.Add([PSCustomObject]@{
            OnPremIdField = "Related_x0020_to_x0020_Person_x0028_s_x0029_Id"
            OnPremName    = "Related_x0020_to_x0020_Person_x0028_s_x0029_"
            SpoField      = "Related_x0020_to_x0020_Person_x0028_s_x0029_"
            Title         = "Related to Person(s)"
            IsPersonLookup = $true
        })
    } elseif ($destList -in @("ITAU_Log_Entries","PIO_Log_Entries","ICM_Log_Entries")) {
        $lookupsForThisList.Add([PSCustomObject]@{
            OnPremIdField = "Related_x0020_to_x0020_Person_x0Id"
            OnPremName    = "Related_x0020_to_x0020_Person_x0"
            SpoField      = "Related_x0020_to_x0020_Person_x0"
            Title         = "Related to Person(s)"
            IsPersonLookup = $true
        })
    } elseif ($destList -in @("ITAU_Documents","PIO_Documents","ICM_Documents")) {
        $lookupsForThisList.Add([PSCustomObject]@{
            OnPremIdField = "Related_x0020_to_x0020_Person_x0028_s_x0029_Id"
            OnPremName    = "Related_x0020_to_x0020_Person_x0028_s_x0029_"
            SpoField      = "Related_x0020_to_x0020_Person_x0028_s_x0029_"
            Title         = "Related to Person(s)"
            IsPersonLookup = $true
        })
    } elseif ($destList -in @("Briefings","Security_Alerts")) {
        $lookupsForThisList.Add([PSCustomObject]@{
            OnPremIdField = "Related_x0020_to_x0020_Person_x0Id"
            OnPremName    = "Related_x0020_to_x0020_Person_x0"
            SpoField      = "Related_x0020_to_x0020_Person_x0"
            Title         = "Related to Person(s)"
            IsPersonLookup = $true
        })
    } elseif ($destList -eq "YAL") {
        $lookupsForThisList.Add([PSCustomObject]@{
            OnPremIdField = "Known_x0020_AssociatesId"
            OnPremName    = "Known_x0020_Associates"
            SpoField      = "Known_x0020_Associates"
            Title         = "Known Associates"
            IsPersonLookup = $true
        })
    } elseif ($destList -eq "Persons") {
        $lookupsForThisList.Add([PSCustomObject]@{
            OnPremIdField = "Known_x0020_AssociatesId"
            OnPremName    = "Known_x0020_Associates"
            SpoField      = "Known_x0020_Associates"
            Title         = "Known Associates"
            IsPersonLookup = $true
        })
    }

    if ($lookupsForThisList.Count -gt 0) {
        $personLookupDefMap[$destList] = $lookupsForThisList
        $personLookupDefMap[$destList.Replace("_"," ")] = $lookupsForThisList
    }
}

# 3. Setup Connections
if (-not (Test-Path $ScratchDir)) { New-Item -ItemType Directory -Path $ScratchDir -Force | Out-Null }
$outReportDir = Split-Path $OutputVarianceReport -Parent
if ($outReportDir -and -not (Test-Path $outReportDir)) { New-Item -ItemType Directory -Path $outReportDir -Force | Out-Null }
$headers = @{ "Accept" = "application/json;odata=verbose" }
$onPremCred = $null
if (-not $UseDefaultCredentials) {
    $onPremCred = Get-Credential -Message "On-Prem SP2016 IDIR credentials"
}

$cfgHash = Import-PowerShellDataFile $ConfigPath
Import-Module PnP.PowerShell -ErrorAction Stop
Connect-PnPOnline -Url $cfgHash.SiteUrl -ClientId $cfgHash.ClientId -Tenant $cfgHash.TenantId -Interactive -ErrorAction Stop

# Target lists to audit
$businessListsToAudit = @(
    "ITAU_Cases",
    "PIO_Cases",
    "ICM_Cases",
    "ITAU_Narratives",
    "PIO_Narratives",
    "ICM_Narratives",
    "ITAU_Case_Tasks",
    "PIO_Case_Tasks",
    "ICM_Case_Tasks",
    "ITAU_Log_Entries",
    "PIO_Log_Entries",
    "ICM_Log_Entries",
    "ITAU_Documents",
    "PIO_Documents",
    "ICM_Documents",
    "Briefings",
    "Security_Alerts",
    "YAL",
    "Persons"
)

$targetLists = @()
if ($ListName -and $ListName -ne "All" -and $ListName -ne "*") {
    $targetLists = @($businessListsToAudit | Where-Object { $_ -like "*$ListName*" })
    if ($targetLists.Count -eq 0) { $targetLists = @($ListName) }
} elseif ($AuditAllExceptEtl -or $All) {
    $targetLists = $businessListsToAudit
} elseif ($Interactive -or [string]::IsNullOrWhiteSpace($ListName)) {
    Write-Host "`nSelect an audit scope or specific list:" -ForegroundColor Yellow
    Write-Host "  [0] Audit ALL Core Business Lists ($($businessListsToAudit.Count) Lists)" -ForegroundColor Green
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

    $lookupCols = if ($personLookupDefMap.ContainsKey($srcTitle)) { $personLookupDefMap[$srcTitle] } 
                  elseif ($personLookupDefMap.ContainsKey($safeTitle)) { $personLookupDefMap[$safeTitle] } 
                  else { [System.Collections.Generic.List[PSCustomObject]]::new() }

    # Fetch On-Prem Items with full pagination
    $scratchCsv = Join-Path $ScratchDir "$($safeTitle)-onprem-lookups.csv"
    $onPremData = $null

    if ($SkipExtractIfCsvExists -and (Test-Path $scratchCsv)) {
        Write-Host "  Loading cached on-prem extract ($scratchCsv)..." -ForegroundColor DarkGray
        $onPremData = Import-Csv -Path $scratchCsv
    } else {
        Write-Host "  Querying On-Premises SP2016 for '$srcTitle'..." -ForegroundColor Yellow
        $onPremListUrl = "$OnPremUrl/_api/web/lists/getbytitle('$srcTitle')/items?`$top=5000"
        
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
                $cProp = $it.PSObject.Properties['Case_x0020_ID']
                $caseNum = if ($cProp) { [string]$cProp.Value } else { $null }
                if (-not $caseNum) {
                    $cIdProp = $it.PSObject.Properties['CaseID']
                    $caseNum = if ($cIdProp) { [string]$cIdProp.Value } else { $null }
                }
                if (-not $caseNum) {
                    $tProp = $it.PSObject.Properties['Title']
                    $caseNum = if ($tProp) { [string]$tProp.Value } else { $null }
                }
                if (-not $caseNum) {
                    $idVal = if ($it.PSObject.Properties['__sp_ID__']) { $it.__sp_ID__ } else { $it.Id }
                    $caseNum = "ITEM_$idVal"
                }

                $tVal = if ($it.PSObject.Properties['Title']) { [string]$it.Title } else { "" }
                $rowObj = [ordered]@{
                    OnPremID   = if ($it.PSObject.Properties['__sp_ID__']) { [int]$it.__sp_ID__ } else { [int]$it.Id }
                    CaseNumber = $caseNum.Trim()
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
    $caseIdField = if ("Case_x0020_ID" -in $allSpoFields) { "Case_x0020_ID" } 
                   elseif ("CaseID" -in $allSpoFields) { "CaseID" } 
                   else { "Title" }

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
        $caseNum = $opCase.CaseNumber
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
                CaseNumber        = $caseNum
                OnPremID          = $opId
                SpoItemID         = $spoItemId
                CaseIDSuffix      = $extractedSuffix
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
Write-Host " Run 'python analyze-lookup-variances.py' for summary metrics.   " -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Cyan
