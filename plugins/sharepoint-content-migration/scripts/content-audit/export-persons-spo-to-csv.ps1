<#
.SYNOPSIS
    export-persons-spo-to-csv.ps1
    Exports Persons from SPO PROD to CSV with full natural assurance keys.
#>
[CmdletBinding()]
param(
    [string]$ConfigPath = "plugins/sharepoint-migration/config/config-prod.psd1",
    [string]$OutputDir = ".agents/scratch/pii-data"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host " EXPORTING SPO PERSONS TO CSV (LOCAL DIAGNOSTIC)                 " -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

$cfgHash = Import-PowerShellDataFile $ConfigPath
Import-Module PnP.PowerShell -ErrorAction Stop
Connect-PnPOnline -Url $cfgHash.SiteUrl -ClientId $cfgHash.ClientId -Tenant $cfgHash.TenantId -Interactive -ErrorAction Stop

$fields = @(
    "ID",
    "Title",
    "FPS",
    "Last_x0020_Name",
    "First_x0020_Name",
    "Middle_x0020_Name",
    "Date_x0020_of_x0020_Birth",
    "Active",
    "Role",
    "Risk_x0020_Level",
    "In_x0020_Custody",
    "Being_x0020_Monitored",
    "Aliases",
    "FullName_DOB_Active_Lookup",
    "Active_x0020_Persons"
)

Write-Host "Querying all SPO Persons items with assurance fields..." -ForegroundColor Yellow
$items = Get-PnPListItem -List "Persons" -PageSize 2000 -Fields $fields

$records = [System.Collections.Generic.List[PSCustomObject]]::new()
foreach ($it in $items) {
    $records.Add([PSCustomObject]@{
        ID                         = [int]$it.Id
        CS_Number                  = [string]$it['Title']
        FPS                        = [string]$it['FPS']
        LastName                   = [string]$it['Last_x0020_Name']
        FirstName                  = [string]$it['First_x0020_Name']
        MiddleName                 = [string]$it['Middle_x0020_Name']
        DateOfBirth                = [string]$it['Date_x0020_of_x0020_Birth']
        Active                     = [string]$it['Active']
        Role                       = [string]$it['Role']
        RiskLevel                  = [string]$it['Risk_x0020_Level']
        InCustody                  = [string]$it['In_x0020_Custody']
        BeingMonitored             = [string]$it['Being_x0020_Monitored']
        Aliases                    = [string]$it['Aliases']
        FullName_DOB_Active_Lookup = [string]$it['FullName_DOB_Active_Lookup']
        Active_Persons             = [string]$it['Active_x0020_Persons']
    })
}

$csvPath = Join-Path $OutputDir "persons-spo-prod.csv"
$records | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8
Write-Host "`nSuccessfully exported $($records.Count) SPO records to: $csvPath" -ForegroundColor Green
