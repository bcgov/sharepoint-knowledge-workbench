<#
.SYNOPSIS
    check-itau-cases-id-suffix-skew.ps1
    Counts how many ITAU_Cases in SPO and SP2016 have an Item ID that does NOT match
    the numeric suffix of the "Case ID" field (e.g. Case ID: ITAU_2026_2909 vs Item ID: 2910).
#>
param(
    [string]$ConfigPath = "plugins/sharepoint-migration/config/config-prod.psd1",
    [string]$ScratchCsvPath = ".agents/scratch/pii-data/itau-cases-onprem-lookups.csv"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host " CHECKING ITEM ID vs. CASE ID SUFFIX SKEW IN SPO & SP2016        " -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

# 1. Check SPO ITAU_Cases
$cfgHash = Import-PowerShellDataFile $ConfigPath
Import-Module PnP.PowerShell -ErrorAction Stop
Connect-PnPOnline -Url $cfgHash.SiteUrl -ClientId $cfgHash.ClientId -Tenant $cfgHash.TenantId -Interactive -ErrorAction Stop

$allSpoFields = Get-PnPField -List "ITAU_Cases" | Select-Object -ExpandProperty InternalName
$caseIdField = if ("Case_x0020_ID" -in $allSpoFields) { "Case_x0020_ID" } 
               elseif ("CaseID" -in $allSpoFields) { "CaseID" } 
               else { "Title" }

$spoItems = Get-PnPListItem -List "ITAU_Cases" -PageSize 1000 -Fields "ID","Title",$caseIdField
Write-Host "Loaded $($spoItems.Count) live rows from SPO." -ForegroundColor Green

$spoMatches = 0
$spoMismatches = 0
$spoSkewSamples = [System.Collections.Generic.List[PSCustomObject]]::new()

foreach ($it in $spoItems) {
    $itemId = [int]$it.Id
    $caseNumStr = [string]$it[$caseIdField]
    if (-not $caseNumStr) { $caseNumStr = [string]$it['Title'] }

    # Extract trailing numeric digits from Case ID (e.g. 'ITAU_2026_2909' -> 2909)
    if ($caseNumStr -match '(\d+)$') {
        $suffixInt = [int]$Matches[1]
        if ($itemId -eq $suffixInt) {
            $spoMatches++
        } else {
            $spoMismatches++
            $delta = $itemId - $suffixInt
            if ($spoSkewSamples.Count -lt 10) {
                $spoSkewSamples.Add([PSCustomObject]@{
                    SPO_Item_ID = $itemId
                    Case_Number = $caseNumStr
                    Extracted_Suffix = $suffixInt
                    Offset_Delta = $(if ($delta -gt 0) { "+$delta" } else { "$delta" })
                })
            }
        }
    } else {
        $spoMismatches++
    }
}

Write-Host "`n=================================================================" -ForegroundColor Cyan
Write-Host " SPO ITAU_Cases ID vs. SUFFIX SUMMARY                            " -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "Total SPO Items Analyzed                      : $($spoItems.Count)"
Write-Host "Cases where Item ID == Suffix (Exact Match)   : $spoMatches ($([math]::Round(($spoMatches/$spoItems.Count)*100, 2))%)" -ForegroundColor $(if ($spoMatches -gt 0) { "Green" } else { "Yellow" })
Write-Host "Cases where Item ID != Suffix (Shifted / Skew): $spoMismatches ($([math]::Round(($spoMismatches/$spoItems.Count)*100, 2))%)" -ForegroundColor $(if ($spoMismatches -gt 0) { "Yellow" } else { "Green" })

if ($spoSkewSamples.Count -gt 0) {
    Write-Host "`nSample Skewed Cases in SPO:" -ForegroundColor Yellow
    foreach ($s in $spoSkewSamples) {
        Write-Host "  * SPO Item ID: $($s.SPO_Item_ID.ToString().PadLeft(5)) | Case ID: '$($s.Case_Number)' (Suffix: $($s.Extracted_Suffix)) | Offset: $($s.Offset_Delta)"
    }
}
Write-Host "=================================================================" -ForegroundColor Cyan
