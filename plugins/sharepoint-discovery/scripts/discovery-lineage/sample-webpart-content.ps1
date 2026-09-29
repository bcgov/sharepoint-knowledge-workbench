<#
.SYNOPSIS
[SCRATCH / INVESTIGATION SCRIPT] Downloads raw .aspx page content for specific lists found in a legacy web parts scan.

.DESCRIPTION
This is a one-off investigation helper. It reads legacy_webparts_scan_results.csv,
filters for pages matching a specific list (currently hardcoded to PIO_Cases),
and downloads the raw ASPX source to 01_source_sharepoint\raw_exports\legacy_webparts\pages\.

This script is NOT part of the main discovery pipeline. It was used for a targeted
deep-dive into specific customized pages. If you need to generalise it, add a -ListFilter
parameter and replace the hardcoded path references.

.EXAMPLE
.\sample-webpart-content.ps1 -UseDefaultCredentials
#>
[CmdletBinding()]
param(
    [string]$SiteUrl = "https://itau.test.jag.gov.bc.ca/cmat",
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
$ProjectRoot = Resolve-Path (Join-Path $scriptDir "..\..") | Select-Object -ExpandProperty Path
$outputDir = Join-Path $ProjectRoot "01_source_sharepoint\raw_exports\legacy_webparts\pages"
if (-not (Test-Path $outputDir)) { New-Item -ItemType Directory -Path $outputDir -Force | Out-Null }

$spHeaders = @{ "Accept" = "application/json;odata=verbose" }
$spCredential = $null

if ($UseDefaultCredentials) {
    Write-Host "Using current Windows session." -ForegroundColor Green
} else {
    $spCredential = Get-Credential -Message "IDIR credentials"
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

$csvPath = Join-Path $ProjectRoot "01_source_sharepoint\raw_exports\legacy_webparts\legacy_webparts_scan_results.csv"
$webparts = Import-Csv $csvPath

# Select PIO_Cases and some Calendar forms
$pioForms = @($webparts | Where-Object { $_.PageUrl -match "PIO_Cases" })
$samplePages = $pioForms | Select-Object -Unique -Property PageUrl

Write-Section "Downloading PIO_Cases forms for deep dive"

foreach ($wp in $samplePages) {
    $pageUrl = $wp.PageUrl
    $encodedUrl = [Uri]::EscapeDataString($pageUrl)
    
    $fileName = $pageUrl -replace "/", "_"
    $fileName = $fileName.TrimStart("_cmat_")
    $outFile = Join-Path $outputDir "$fileName"
    
    Write-Host "Downloading: $pageUrl"
    $downloadUrl = "$SiteUrl/_api/web/GetFileByServerRelativeUrl('$encodedUrl')/`$value"
    
    Invoke-SPRestDownload -Url $downloadUrl -OutFile $outFile | Out-Null
}

Write-Host "Done" -ForegroundColor Green
