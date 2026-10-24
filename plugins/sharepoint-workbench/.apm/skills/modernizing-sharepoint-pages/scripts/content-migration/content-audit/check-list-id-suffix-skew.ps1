<#
.SYNOPSIS
    check-list-id-suffix-skew.ps1
    Counts how many items of one SharePoint Online list have an item ID that does NOT match the numeric suffix of their
    business key (for example key 'ABC_2026_2909' vs item ID 2910). Read-only.
.PARAMETER ListName
    The list to check.
.PARAMETER KeyColumns
    Business-key columns tried in order; the first one that exists on the list is used. Default: Title.
.PARAMETER ConfigPath
    Connection config (a config-*.psd1 file with SiteUrl, ClientId and TenantId).
#>
param(
    [Parameter(Mandatory)][string]$ListName,
    [string[]]$KeyColumns = @("Title"),
    [string]$ConfigPath = "config.psd1"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host " CHECKING ITEM ID vs. BUSINESS-KEY SUFFIX SKEW                    " -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

# 1. Check the live SharePoint Online list
$cfgHash = Import-PowerShellDataFile $ConfigPath
Import-Module PnP.PowerShell -ErrorAction Stop
Connect-PnPOnline -Url $cfgHash.SiteUrl -ClientId $cfgHash.ClientId -Tenant $cfgHash.TenantId -Interactive -ErrorAction Stop

$allSpoFields = Get-PnPField -List $ListName | Select-Object -ExpandProperty InternalName
$keyField = @($KeyColumns | Where-Object { $_ -in $allSpoFields })[0]
if (-not $keyField) { $keyField = "Title" }

$spoItems = Get-PnPListItem -List $ListName -PageSize 1000 -Fields "ID","Title",$keyField
Write-Host "Loaded $($spoItems.Count) live rows from SPO." -ForegroundColor Green

$spoMatches = 0
$spoMismatches = 0
$spoSkewSamples = [System.Collections.Generic.List[PSCustomObject]]::new()

foreach ($it in $spoItems) {
    $itemId = [int]$it.Id
    $keyStr = [string]$it[$keyField]
    if (-not $keyStr) { $keyStr = [string]$it['Title'] }

    # Extract trailing numeric digits from the business key (e.g. 'ABC_2026_2909' -> 2909)
    if ($keyStr -match '(\d+)$') {
        $suffixInt = [int]$Matches[1]
        if ($itemId -eq $suffixInt) {
            $spoMatches++
        } else {
            $spoMismatches++
            $delta = $itemId - $suffixInt
            if ($spoSkewSamples.Count -lt 10) {
                $spoSkewSamples.Add([PSCustomObject]@{
                    SPO_Item_ID = $itemId
                    Business_Key = $keyStr
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
Write-Host " SPO LIST ID vs. SUFFIX SUMMARY: $ListName                        " -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "Total SPO Items Analyzed                      : $($spoItems.Count)"
Write-Host "Items where Item ID == Suffix (Exact Match)   : $spoMatches ($([math]::Round(($spoMatches/$spoItems.Count)*100, 2))%)" -ForegroundColor $(if ($spoMatches -gt 0) { "Green" } else { "Yellow" })
Write-Host "Items where Item ID != Suffix (Shifted / Skew): $spoMismatches ($([math]::Round(($spoMismatches/$spoItems.Count)*100, 2))%)" -ForegroundColor $(if ($spoMismatches -gt 0) { "Yellow" } else { "Green" })

if ($spoSkewSamples.Count -gt 0) {
    Write-Host "`nSample skewed items in SPO:" -ForegroundColor Yellow
    foreach ($s in $spoSkewSamples) {
        Write-Host "  * SPO Item ID: $($s.SPO_Item_ID.ToString().PadLeft(5)) | Key: '$($s.Business_Key)' (Suffix: $($s.Extracted_Suffix)) | Offset: $($s.Offset_Delta)"
    }
}
Write-Host "=================================================================" -ForegroundColor Cyan
