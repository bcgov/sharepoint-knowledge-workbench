<#
.SYNOPSIS
    backfill-itau-cases-person-lookups.ps1
    High-efficiency, 2-phase Person Lookup reconciler for ITAU_Cases:
    Phase 1: Single bulk read from SP2016 -> extracts Case ID + all 8 on-prem Person Lookup arrays -> saves to CSV.
    Phase 2: Translates on-prem Person IDs via id-mapping-verified.json -> builds single consolidated update hashtable per Case -> writes to SPO via PnP Batching (100 items per HTTP POST).
#>

[CmdletBinding()]
param(
    [string]$OnPremUrl = "https://itau.jag.gov.bc.ca/cmat",
    [switch]$UseDefaultCredentials,
    [string]$MappingPath = ".agents/scratch/id-mapping-verified.json",
    [string]$ConfigPath = "plugins/sharepoint-migration/config/config-prod.psd1",
    [string]$ScratchCsvPath = ".agents/scratch/pii-data/itau-cases-onprem-lookups.csv",
    [int]$BatchSize = 100,
    [int]$Limit = 0, # 0 = all items
    [switch]$DryRun,
    [switch]$SkipExtractIfCsvExists
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host " HIGH-EFFICIENCY BULK RECONCILER: ITAU_Cases PERSON LOOKUPS      " -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

# 1. Load verified dictionary
if (-not (Test-Path $MappingPath)) {
    throw "Verified ID mapping table not found at: $MappingPath`nPlease run analyze-persons-mapping-assurance.py first."
}
$idMapJson = Get-Content $MappingPath -Raw | ConvertFrom-Json
Write-Host "Loaded verified ID dictionary from $MappingPath." -ForegroundColor Green

# -----------------------------------------------------------------------------
# PHASE 1: Single Bulk Read from SP2016 On-Prem -> Extract to CSV
# -----------------------------------------------------------------------------
$fieldsToQuery = @(
    @{ OnPremIdField = "subject_x0028_s_x0029__x0020__x0Id";  SpoField = "Subjects_Accused";        Title = "Subject (Accused)" },
    @{ OnPremIdField = "subject_x0028_s_x0029__x0020__x00Id"; SpoField = "Subjects_Victim_Witness"; Title = "Subject (Victim/Witness)" },
    @{ OnPremIdField = "subject_x0028_s_x0029__x0020__x01Id"; SpoField = "Subjects_Gov_Employee";   Title = "Subject (Gov Employee)" },
    @{ OnPremIdField = "subject_x0028_s_x0029__x0020__x02Id"; SpoField = "Subjects_Other";          Title = "Subject (Other)" },
    @{ OnPremIdField = "affected_x0020__x002d__x0020_CroId";  SpoField = "Affected_Crown";          Title = "Affected (Crown)" },
    @{ OnPremIdField = "affected_x0020__x002d__x0020_JudId";  SpoField = "Affected_Judiciary";      Title = "Affected (Judiciary)" },
    @{ OnPremIdField = "affected_x0020__x002d__x0020_GovId";  SpoField = "Affected_Gov_Employee";   Title = "Affected (Gov Employee)" },
    @{ OnPremIdField = "affected_x0020__x002d__x0020_OthId";  SpoField = "Affected_Other";          Title = "Affected (Other)" }
)

$csvDir = Split-Path $ScratchCsvPath -Parent
if (-not (Test-Path $csvDir)) { New-Item -ItemType Directory -Path $csvDir -Force | Out-Null }

if ($SkipExtractIfCsvExists -and (Test-Path $ScratchCsvPath)) {
    Write-Host "`n[Phase 1] Using existing SP2016 extract CSV ($ScratchCsvPath)..." -ForegroundColor Yellow
} else {
    Write-Host "`n[Phase 1] Single Bulk Read: Querying all ITAU_Cases from SP2016 ($OnPremUrl)..." -ForegroundColor Yellow

    $headers = @{ "Accept" = "application/json;odata=verbose" }
    $onPremCred = $null
    if (-not $UseDefaultCredentials) {
        $onPremCred = Get-Credential -Message "On-Prem SP2016 IDIR credentials"
    }

    $selectCols = "ID,Title," + (($fieldsToQuery.OnPremIdField) -join ',')
    $nextUrl = "$OnPremUrl/_api/web/lists/getbytitle('ITAU_Cases')/items?`$select=$selectCols&`$top=5000"

    $extractedRows = [System.Collections.Generic.List[PSCustomObject]]::new()

    while ($nextUrl) {
        Write-Host "  Querying on-prem ITAU_Cases batch..." -ForegroundColor DarkGray
        try {
            $raw = if ($UseDefaultCredentials) {
                Invoke-WebRequest -Uri $nextUrl -Headers $headers -UseDefaultCredentials -ErrorAction Stop
            } else {
                Invoke-WebRequest -Uri $nextUrl -Headers $headers -Credential $onPremCred -ErrorAction Stop
            }
        } catch {
            if (-not $UseDefaultCredentials -or $null -ne $onPremCred) {
                throw "Failed to fetch on-prem ITAU_Cases: $($_.Exception.Message)"
            }
            Write-Warning "Default credentials failed. Prompting for IDIR..."
            $onPremCred = Get-Credential -Message "On-Prem SP2016 IDIR credentials"
            $raw = Invoke-WebRequest -Uri $nextUrl -Headers $headers -Credential $onPremCred -ErrorAction Stop
        }

        $clean = ($raw.Content -creplace '"ID"\s*:', '"__sp_ID__":') | ConvertFrom-Json
        $items = if ($clean.PSObject.Properties['d']) { $clean.d.results } else { $clean.value }

        foreach ($it in $items) {
            $caseId = if ($it.PSObject.Properties['__sp_ID__']) { $it.__sp_ID__ } else { $it.Id }
            $rowObj = [ordered]@{
                CaseID = [int]$caseId
                Title  = [string]$it.Title
            }

            foreach ($f in $fieldsToQuery) {
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

    $extractedRows | Export-Csv -Path $ScratchCsvPath -NoTypeInformation -Encoding UTF8
    Write-Host "Extracted $($extractedRows.Count) ITAU_Cases rows from SP2016 to: $ScratchCsvPath" -ForegroundColor Green
}

# -----------------------------------------------------------------------------
# PHASE 2: In-Memory Translation & PnP Batch Update to SPO
# -----------------------------------------------------------------------------
Write-Host "`n[Phase 2] Loading extract CSV and building consolidated updates..." -ForegroundColor Yellow

$casesData = Import-Csv -Path $ScratchCsvPath
Write-Host "Loaded $($casesData.Count) cases from extract CSV." -ForegroundColor DarkGray

$pendingUpdates = [System.Collections.Generic.List[PSCustomObject]]::new()
$totalLookupsToUpdate = 0

foreach ($row in $casesData) {
    $caseId = [int]$row.CaseID
    $updateValues = @{}
    $hasAnyLookup = $false

    foreach ($f in $fieldsToQuery) {
        $spoField = $f.SpoField
        $rawOnPremIds = [string]$row.$spoField

        if (-not [string]::IsNullOrWhiteSpace($rawOnPremIds)) {
            $oldIds = $rawOnPremIds -split '[,;\s]+' | Where-Object { $_ -match '^\d+$' }
            $translatedSpoIds = [System.Collections.Generic.List[int]]::new()

            foreach ($oldId in $oldIds) {
                if ($idMapJson.PSObject.Properties[$oldId]) {
                    $newSpoId = [int]$idMapJson.$oldId
                    $translatedSpoIds.Add($newSpoId)
                } else {
                    Write-Warning "Case #$caseId ($spoField): On-prem Person ID $oldId not found in dictionary."
                }
            }

            if ($translatedSpoIds.Count -gt 0) {
                $updateValues[$spoField] = [int[]]$translatedSpoIds.ToArray()
                $hasAnyLookup = $true
                $totalLookupsToUpdate += $translatedSpoIds.Count
            }
        }
    }

    if ($hasAnyLookup) {
        $pendingUpdates.Add([PSCustomObject]@{
            CaseId = $caseId
            Values = $updateValues
        })
    }

    if ($Limit -gt 0 -and $pendingUpdates.Count -ge $Limit) {
        Write-Host "Reached limit of $Limit cases with lookups. Stopping build." -ForegroundColor Yellow
        break
    }
}

Write-Host "Found $($pendingUpdates.Count) cases that have Person lookups (Total lookup pointers: $totalLookupsToUpdate)." -ForegroundColor Green

if ($pendingUpdates.Count -eq 0) {
    Write-Host "No cases require updates. Exiting." -ForegroundColor Green
    return
}

# Connect to SPO
Write-Host "`nConnecting to SharePoint Online..." -ForegroundColor Yellow
$cfgHash = Import-PowerShellDataFile $ConfigPath
Import-Module PnP.PowerShell -ErrorAction Stop
Connect-PnPOnline -Url $cfgHash.SiteUrl -ClientId $cfgHash.ClientId -Tenant $cfgHash.TenantId -Interactive -ErrorAction Stop

if ($DryRun) {
    Write-Host "`n[DRY RUN] Sample consolidated updates (First 3 cases):" -ForegroundColor Yellow
    foreach ($sample in ($pendingUpdates | Select-Object -First 3)) {
        Write-Host "  Case #${sample.CaseId}:" -ForegroundColor Cyan
        foreach ($k in $sample.Values.Keys) {
            Write-Host "    * $k = $(($sample.Values[$k] -join ', '))"
        }
    }
    Write-Host "`n[DRY RUN] Preview complete. No updates were sent to SPO." -ForegroundColor Yellow
    return
}

# Execute in PnP Batches of $BatchSize (100 cases per HTTP POST)
Write-Host "`nExecuting PnP Batch Updates (Batch size: $BatchSize cases per request)..." -ForegroundColor Yellow

$totalBatches = [math]::Ceiling($pendingUpdates.Count / $BatchSize)
$currentBatchNum = 0
$processedCount = 0

for ($i = 0; $i -lt $pendingUpdates.Count; $i += $BatchSize) {
    $currentBatchNum++
    $chunk = $pendingUpdates[$i..[math]::Min($i + $BatchSize - 1, $pendingUpdates.Count - 1)]
    
    Write-Host "  Processing Batch $currentBatchNum of $totalBatches ($($chunk.Count) cases)..." -ForegroundColor DarkGray
    $batch = New-PnPBatch

    foreach ($item in $chunk) {
        Set-PnPListItem -List "ITAU_Cases" -Identity $item.CaseId -Values $item.Values -Batch $batch | Out-Null
    }

    try {
        Invoke-PnPBatch -Batch $batch -ErrorAction Stop
        $processedCount += $chunk.Count
    } catch {
        Write-Error "Error executing batch $currentBatchNum: $($_.Exception.Message)"
    }
}

Write-Host "`n=================================================================" -ForegroundColor Cyan
Write-Host " RECONCILIATION SUMMARY FOR ITAU_Cases                           " -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "Total Cases with Person Lookups Updated : $processedCount / $($pendingUpdates.Count)" -ForegroundColor Green
Write-Host "Total Person Pointers Restored          : $totalLookupsToUpdate" -ForegroundColor Green
Write-Host "Lookups per Case Updated in Single Call : Up to 8 columns at once" -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Cyan
