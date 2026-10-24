<#
.SYNOPSIS
[SCRATCH / INVESTIGATION SCRIPT] Downloads raw .aspx page content for specific lists found in a legacy web parts scan.

.DESCRIPTION
This is a one-off investigation helper. It reads legacy_webparts_scan_results.csv from -ExportRoot (or -ScanResultsCsv),
filters for pages whose URL matches -ListFilter (for example a list name),
and downloads the raw ASPX source to <ExportRoot>\pages\.

This script is NOT part of the main discovery pipeline. It is a targeted deep-dive helper
for specific customized pages.

.EXAMPLE
.\sample-webpart-content.ps1 -SiteUrl https://onprem.example.com/sites/demo -ListFilter MyList -ExportRoot C:\exports\legacy_webparts -UseDefaultCredentials
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$SiteUrl,
    [Parameter(Mandatory)][string]$ListFilter,
    [Parameter(Mandatory)][string]$ExportRoot,
    [string]$ScanResultsCsv = "",
    [switch]$UseDefaultCredentials
)

$ErrorActionPreference = "Stop"

function Write-Section {
    param([string]$Message)
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor DarkCyan
    Write-Host $Message -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor DarkCyan
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ExportRoot = [System.IO.Path]::GetFullPath($ExportRoot)
$outputDir = Join-Path $ExportRoot "pages"
if (-not (Test-Path $outputDir)) { New-Item -ItemType Directory -Path $outputDir -Force | Out-Null }

$spHeaders = @{ "Accept" = "application/json;odata=verbose" }
$spCredential = $null

if ($UseDefaultCredentials) {
    Write-Host "Using current Windows session." -ForegroundColor Green
} else {
    $spCredential = Get-Credential -Message "On-premises SharePoint credentials"
    if ($null -eq $spCredential) { throw "No credentials provided. Aborting." }
}

function Invoke-SPRestDownload {
    param([string]$Url, [string]$OutFile)
    try {
        if ($UseDefaultCredentials) {
            Invoke-RestMethod -Uri $Url -Headers $spHeaders -UseDefaultCredentials -OutFile $OutFile -ErrorAction Stop
        } else {
            Invoke-RestMethod -Uri $Url -Headers $spHeaders -Credential $spCredential -OutFile $OutFile -ErrorAction Stop
        }
        return $true
    } catch {
        Write-Host "Failed to download $Url" -ForegroundColor Red
        return $false
    }
}

$csvPath = if ($ScanResultsCsv) { $ScanResultsCsv } else { Join-Path $ExportRoot "legacy_webparts_scan_results.csv" }
if (-not (Test-Path $csvPath)) { throw "Scan results CSV not found: $csvPath (pass -ScanResultsCsv or put legacy_webparts_scan_results.csv in -ExportRoot)." }
$webparts = Import-Csv $csvPath

# Select the pages whose URL matches the requested list
$matchingPages = @($webparts | Where-Object { $_.PageUrl -match [regex]::Escape($ListFilter) })
$samplePages = $matchingPages | Select-Object -Unique -Property PageUrl

Write-Section "Downloading $ListFilter forms for deep dive"

foreach ($wp in $samplePages) {
    $pageUrl = $wp.PageUrl
    $encodedUrl = [Uri]::EscapeDataString($pageUrl)
    
    $fileName = $pageUrl -replace "/", "_"
    $fileName = $fileName.TrimStart("_")
    $outFile = Join-Path $outputDir "$fileName"
    
    Write-Host "Downloading: $pageUrl"
    $downloadUrl = "$SiteUrl/_api/web/GetFileByServerRelativeUrl('$encodedUrl')/`$value"
    
    Invoke-SPRestDownload -Url $downloadUrl -OutFile $outFile | Out-Null
}

Write-Host "Done" -ForegroundColor Green
