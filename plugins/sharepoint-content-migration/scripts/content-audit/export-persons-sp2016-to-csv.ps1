<#
.SYNOPSIS
    export-persons-sp2016-to-csv.ps1
    Exports Persons from SP2016 On-Prem to CSV with full natural assurance keys.
#>
[CmdletBinding()]
param(
    [string]$OnPremUrl = "https://itau.jag.gov.bc.ca/cmat",
    [switch]$UseDefaultCredentials,
    [string]$OutputDir = ".agents/scratch/pii-data"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host " EXPORTING SP2016 PERSONS TO CSV (LOCAL DIAGNOSTIC)              " -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

$headers = @{ "Accept" = "application/json;odata=verbose" }
$onPremCred = $null
if (-not $UseDefaultCredentials) {
    $onPremCred = Get-Credential -Message "On-Prem SP2016 IDIR credentials"
}

$fieldsToSelect = "ID,Title,FPS,Last_x0020_Name,First_x0020_Name,Middle_x0020_Name,Date_x0020_of_x0020_Birth,Active,Role,Risk_x0020_Level,In_x0020_Custody,Being_x0020_Monitored,Aliases"
$nextUrl = "$OnPremUrl/_api/web/lists/getbytitle('Persons')/items?`$select=$fieldsToSelect&`$top=5000"

$records = [System.Collections.Generic.List[PSCustomObject]]::new()

while ($nextUrl) {
    Write-Host "  Querying SP2016 Persons batch..." -ForegroundColor DarkGray
    try {
        if ($UseDefaultCredentials) {
            $raw = Invoke-WebRequest -Uri $nextUrl -Headers $headers -UseDefaultCredentials -ErrorAction Stop
        } else {
            $raw = Invoke-WebRequest -Uri $nextUrl -Headers $headers -Credential $onPremCred -ErrorAction Stop
        }
    } catch {
        if (-not $UseDefaultCredentials -or $null -ne $onPremCred) {
            Write-Error "Failed: $($_.Exception.Message)"
            break
        }
        Write-Warning "Default credentials failed. Prompting for IDIR..."
        $onPremCred = Get-Credential -Message "On-Prem SP2016 IDIR credentials"
        $raw = Invoke-WebRequest -Uri $nextUrl -Headers $headers -Credential $onPremCred -ErrorAction Stop
    }

    $clean = ($raw.Content -creplace '"ID"\s*:', '"__sp_ID__":') | ConvertFrom-Json
    $items = if ($clean.PSObject.Properties['d']) { $clean.d.results } else { $clean.value }

    foreach ($it in $items) {
        $idVal = if ($it.PSObject.Properties['__sp_ID__']) { $it.__sp_ID__ } else { $it.Id }
        $records.Add([PSCustomObject]@{
            ID             = [int]$idVal
            CS_Number      = [string]$it.Title
            FPS            = [string]$it.FPS
            LastName       = [string]$it.Last_x0020_Name
            FirstName      = [string]$it.First_x0020_Name
            MiddleName     = [string]$it.Middle_x0020_Name
            DateOfBirth    = [string]$it.Date_x0020_of_x0020_Birth
            Active         = [string]$it.Active
            Role           = [string]$it.Role
            RiskLevel      = [string]$it.Risk_x0020_Level
            InCustody      = [string]$it.In_x0020_Custody
            BeingMonitored = [string]$it.Being_x0020_Monitored
            Aliases        = [string]$it.Aliases
        })
    }

    $nextProp = $clean.d.PSObject.Properties['__next']
    $nextUrl = if ($nextProp) { $nextProp.Value } else { $null }
}

$csvPath = Join-Path $OutputDir "persons-sp2016-onprem.csv"
$records | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8
Write-Host "`nSuccessfully exported $($records.Count) SP2016 records to: $csvPath" -ForegroundColor Green
