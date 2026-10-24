<#
.SYNOPSIS
    export-list-content-pairs.ps1 (list content audit, discovery step 1)
    Populates paired CSV datasets of CURRENT list content from both the on-premises SharePoint source
    and SharePoint Online, to enable downstream deep variance analysis and content-migration
    auditing (analyze-all-variances.py / analyze-lookup-variances.py):
      - .agents/scratch/pii-data/<ListName>-sp2016-onprem.csv
      - .agents/scratch/pii-data/<ListName>-spo-prod.csv
    Zero in-memory comparison logic — purely robust, paginated data extraction.
    The lists to export come from the "lists" (minus "exclude_lists") of the audit config passed as -AuditConfigPath, or from -ListName.
    The "sp2016"/"spo-prod" parts of the file names are fixed labels (source / target) that the analyzers look for.
#>

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$ListName = "",

    [switch]$All,
    [switch]$Interactive,
    [ValidateSet("Both", "SPO", "SP2016")]
    [string]$Source = "Both",
    [switch]$SPOOnly,
    [switch]$SP2016Only,
    [Parameter(Mandatory)][string]$OnPremUrl,
    [string]$AuditConfigPath = "audit-config.json",
    [switch]$UseDefaultCredentials,
    [string]$ConfigPath = "config.psd1",
    [string]$ScratchDir = ".agents/scratch/pii-data",
    [string]$StartFrom = "",
    [switch]$SkipExtractIfCsvExists
)

if ($SPOOnly) { $Source = "SPO" }
if ($SP2016Only) { $Source = "SP2016" }

. (Join-Path $PSScriptRoot "audit-helpers.ps1")

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host " LIST CONTENT EXTRACTION ENGINE (DISCOVERY STEP 1)               " -ForegroundColor Cyan
Write-Host " Target Source: $Source | Default: Both                          " -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

# 1. Setup Connections & Directories
if (-not (Test-Path $ScratchDir)) { New-Item -ItemType Directory -Path $ScratchDir -Force | Out-Null }
$headers = @{ "Accept" = "application/json;odata=verbose" }

if ($Source -in @("Both", "SP2016")) {
    $onPremCred = $null
    if (-not $UseDefaultCredentials) {
        $onPremCred = Get-Credential -Message "On-premises SharePoint credentials"
    }
}

if ($Source -in @("Both", "SPO")) {
    $cfgHash = Import-PowerShellDataFile $ConfigPath
    Import-Module PnP.PowerShell -ErrorAction Stop
    Connect-PnPOnline -Url $cfgHash.SiteUrl -ClientId $cfgHash.ClientId -Tenant $cfgHash.TenantId -Interactive -ErrorAction Stop
}

# 2. Scope: the audit config's lists (minus exclusions); a -ListName that is not in the config is exported as given
$businessLists = @()
if (Test-Path $AuditConfigPath) {
    $auditCfg = Get-Content $AuditConfigPath -Raw | ConvertFrom-Json
    $cfgLists = if ($auditCfg.PSObject.Properties['lists'] -and $auditCfg.lists) { @($auditCfg.lists) }
                elseif ($auditCfg.PSObject.Properties['lookups']) { @($auditCfg.lookups.PSObject.Properties.Name) } else { @() }
    $excluded = if ($auditCfg.PSObject.Properties['exclude_lists'] -and $auditCfg.exclude_lists) { @($auditCfg.exclude_lists) } else { @() }
    $businessLists = @($cfgLists | Where-Object { $_ -notin $excluded } | Sort-Object -Unique)
}
if ($businessLists.Count -eq 0 -and [string]::IsNullOrWhiteSpace($ListName)) {
    throw "No lists to export: pass -ListName or set 'lists' in $AuditConfigPath (see audit-config.example.json)."
}

$targetLists = @()
if ($ListName -and $ListName -ne "All" -and $ListName -ne "*") {
    $targetLists = @($businessLists | Where-Object { $_ -like "*$ListName*" })
    if ($targetLists.Count -eq 0) { $targetLists = @($ListName) }
} elseif ($All) {
    $targetLists = $businessLists
} elseif ($Interactive -or [string]::IsNullOrWhiteSpace($ListName)) {
    Write-Host "`nSelect an audit scope or specific list:" -ForegroundColor Yellow
    Write-Host "  [0] Export ALL configured lists ($($businessLists.Count) Lists)" -ForegroundColor Green
    for ($i = 0; $i -lt $businessLists.Count; $i++) {
        Write-Host "  [$($i+1)] $($businessLists[$i])"
    }
    $choice = Read-Host "`nEnter selection (0-$($businessLists.Count)) [Default: 0 - ALL]"
    if ([string]::IsNullOrWhiteSpace($choice) -or $choice -eq "0") {
        $targetLists = $businessLists
    } else {
        $idx = [int]$choice - 1
        if ($idx -ge 0 -and $idx -lt $businessLists.Count) {
            $targetLists = @($businessLists[$idx])
        } else {
            $targetLists = $businessLists
        }
    }
} else {
    $targetLists = $businessLists
}

if ($StartFrom) {
    $startIndex = -1
    for ($i = 0; $i -lt $targetLists.Count; $i++) {
        if ($targetLists[$i] -like "*$StartFrom*") { $startIndex = $i; break }
    }
    if ($startIndex -ge 0) {
        $targetLists = @($targetLists[$startIndex..($targetLists.Count - 1)])
        Write-Host "`nResuming from '$StartFrom' -> $($targetLists.Count) list(s) remaining." -ForegroundColor Magenta
    }
}

Write-Host "`nTarget Scope: $($targetLists.Count) list(s) to export: $($targetLists -join ', ')" -ForegroundColor Cyan

# 3. Export Loop (Pure Extraction)
foreach ($srcTitle in $targetLists) {
    $safeTitle = $srcTitle.Replace(" ", "_")
    Write-Host "`n=================================================================" -ForegroundColor DarkCyan
    Write-Host " EXPORTING LIST DATA PAIR: $srcTitle                             " -ForegroundColor DarkCyan
    Write-Host "=================================================================" -ForegroundColor DarkCyan

    $onPremCsv = Join-Path $ScratchDir "$($safeTitle)-sp2016-onprem.csv"
    $spoCsv = Join-Path $ScratchDir "$($safeTitle)-spo-prod.csv"

    # --- A. On-premises source export ---
    $legacyOnPremCsv = Join-Path $ScratchDir "$($safeTitle)-full-onprem.csv"
    if ($Source -notin @("Both", "SP2016")) {
        Write-Host "  [Source: $Source] Skipping source extraction." -ForegroundColor DarkGray
    } elseif ($SkipExtractIfCsvExists -and (Test-Path $onPremCsv)) {
        Write-Host "  Using existing On-Prem extract: $onPremCsv" -ForegroundColor DarkGray
    } elseif ($SkipExtractIfCsvExists -and (Test-Path $legacyOnPremCsv)) {
        Copy-Item -Path $legacyOnPremCsv -Destination $onPremCsv -Force
        Write-Host "  Using cached On-Prem extract: $onPremCsv" -ForegroundColor DarkGray
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
                $rowObj = [ordered]@{}
                $currentId = if ($it.PSObject.Properties['__sp_ID__']) { [int]$it.__sp_ID__ } else { [int]$it.Id }
                $rowObj["ID"] = [string]$currentId

                foreach ($p in $it.PSObject.Properties) {
                    if ($p.Name -like '__*' -or $p.Name -like 'OData_*' -or $p.Name -eq '__sp_ID__') { continue }
                    $val = $p.Value
                    if ($null -eq $val) {
                        $rowObj[$p.Name] = ""
                    } elseif ($val.PSObject.Properties['results']) {
                        $rowObj[$p.Name] = ($val.results | ForEach-Object { [string]$_ }) -join ';'
                    } elseif ($val.PSObject.Properties['LookupId']) {
                        $rowObj[$p.Name] = [string]$val.LookupId
                    } elseif ($val.PSObject.Properties['Id']) {
                        $rowObj[$p.Name] = [string]$val.Id
                    } else {
                        $rowObj[$p.Name] = [string]$val
                    }
                }
                $extractedRows.Add([PSCustomObject]$rowObj)
            }
            $nextProp = $clean.d.PSObject.Properties['__next']
            $nextUrl = if ($nextProp) { $nextProp.Value } else { $null }
        }

        $extractedRows | Export-Csv -Path $onPremCsv -NoTypeInformation -Encoding UTF8
        Write-Host "  Saved $($extractedRows.Count) rows -> $onPremCsv" -ForegroundColor Green
    }

    # --- B. SharePoint Online Export ---
    if ($Source -notin @("Both", "SPO")) {
        Write-Host "  [Source: $Source] Skipping SPO extraction." -ForegroundColor DarkGray
    } elseif ($SkipExtractIfCsvExists -and (Test-Path $spoCsv)) {
        Write-Host "  Using existing SPO extract: $spoCsv" -ForegroundColor DarkGray
    } else {
        Write-Host "  Querying Live SPO for '$srcTitle'..." -ForegroundColor Yellow
        $spoList = Get-PnPList -Identity $srcTitle -ErrorAction SilentlyContinue
        if (-not $spoList) { $spoList = Get-PnPList -Identity $safeTitle -ErrorAction SilentlyContinue }
        if (-not $spoList) {
            Write-Warning "  List '$srcTitle' not found on SPO site. Skipping."
            continue
        }

        $spoItems = @(Get-PnPListItem -List $spoList.Title -PageSize 2000)
        $spoSavedRows = [System.Collections.Generic.List[PSCustomObject]]::new()

        foreach ($it in $spoItems) {
            $rObj = [ordered]@{}
            $rObj["ID"] = [string]$it.Id
            foreach ($k in $it.FieldValues.Keys) {
                if ($k -like '_*' -or $k -eq 'ID') { continue }
                $val = $it.FieldValues[$k]
                if ($null -eq $val) {
                    $rObj[$k] = ""
                } elseif ($val -is [Microsoft.SharePoint.Client.FieldLookupValue]) {
                    $rObj[$k] = [string]$val.LookupId
                } elseif ($val -is [Microsoft.SharePoint.Client.FieldUserValue]) {
                    $rObj[$k] = [string]$val.LookupId
                } elseif ($val -is [System.Collections.IEnumerable] -and $val -isnot [string]) {
                    $parts = @()
                    foreach ($sub in $val) {
                        if ($sub -is [Microsoft.SharePoint.Client.FieldLookupValue]) { $parts += [string]$sub.LookupId }
                        elseif ($sub -is [Microsoft.SharePoint.Client.FieldUserValue]) { $parts += [string]$sub.LookupId }
                        elseif ($sub.PSObject.Properties['LookupId']) { $parts += [string]$sub.LookupId }
                        else { $parts += [string]$sub }
                    }
                    $rObj[$k] = $parts -join ';'
                } else {
                    $rObj[$k] = [string]$val
                }
            }
            $spoSavedRows.Add([PSCustomObject]$rObj)
        }

        $spoSavedRows | Export-Csv -Path $spoCsv -NoTypeInformation -Encoding UTF8
        Write-Host "  Saved $($spoSavedRows.Count) rows -> $spoCsv" -ForegroundColor Green
    }
}

Write-Host "`n=================================================================" -ForegroundColor Cyan
Write-Host " DATA EXTRACTION COMPLETE                                        " -ForegroundColor Cyan
Write-Host " Raw paired CSVs saved in: $ScratchDir                           " -ForegroundColor Green
Write-Host " Analysis outputs will be saved to: .agents\scratch\audit-reports\" -ForegroundColor Yellow
Write-Host " Now run: python analyze-lookup-variances.py                     " -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Cyan
