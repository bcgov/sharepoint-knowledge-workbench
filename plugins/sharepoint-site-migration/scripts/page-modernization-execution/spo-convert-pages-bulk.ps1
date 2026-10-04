<#
.SYNOPSIS
Bulk-converts every classic page in a library to modern SharePoint pages, one
subprocess per page, with a resumable manifest and post-run validation.

.DESCRIPTION
Enumerates every page in -SourceLibrary, then invokes
spo-convert-page-to-modern.ps1 once per page as an isolated subprocess (a
crash, timeout, or auth failure on one page is captured as a failed row, not
a stopped run). Appends one row per page to -ManifestPath as it goes, so an
interrupted run preserves all completed results; -ResumeFromManifest skips
pages already recorded as Succeeded. Applies a throttle delay between pages.
After all pages are processed, calls spo-validate-page-conversion.ps1 against
the manifest, unless -SkipValidation is set.

Each subprocess opens its own interactive PnP.PowerShell connection --
expect one browser MFA prompt per page unless PnP.PowerShell has cached the
session token.

.PARAMETER SourceLibrary
Library containing the classic source pages. Required.

.PARAMETER TargetLibrary
Library the converted modern pages land in. Defaults to "Site Pages".

.PARAMETER FieldMapping
Path to a JSON field-mapping file, passed through to each conversion
subprocess. Optional.

.PARAMETER LiteralFieldValues
Path to a JSON literal-field-values file, passed through to each conversion
subprocess. Optional.

.PARAMETER PageName
Optional. Process only this one page (by filename) instead of the whole
library -- use for a single-page test run before a full bulk run.

.PARAMETER ManifestPath
Path to the run manifest CSV. Defaults to .\run-manifest.csv. Appended to if
it already exists.

.PARAMETER ResumeFromManifest
Skip pages already recorded as Succeeded in an existing manifest.

.PARAMETER ThrottleDelaySeconds
Delay between pages to avoid SharePoint Online rate limiting. Defaults to 2.

.PARAMETER SkipValidation
Skip the post-run call to spo-validate-page-conversion.ps1.

.PARAMETER WorkerScript
Path to spo-convert-page-to-modern.ps1. Defaults to the copy in this same
scripts folder.

.PARAMETER ValidationScript
Path to spo-validate-page-conversion.ps1. Defaults to the copy in this same
scripts folder.

.PARAMETER SiteUrl
Overrides config.psd1 Connection.SiteUrl.

.PARAMETER ConfigPath
Path to config.psd1. Defaults to the repository root config.psd1.

.PARAMETER ClientId
Overrides ConfigPath ClientId.

.PARAMETER TenantId
Overrides ConfigPath TenantId.

.PARAMETER TenantAdminUrl
Overrides ConfigPath Authentication.TenantAdminUrl.

.PARAMETER Execute
Runs the real subprocess conversions. Omit this to print the page list and
plan only -- no subprocesses are spawned.

.PARAMETER ConfirmToken
Required with -Execute. Must be CONVERT-SPO-PAGES-BULK.

.EXAMPLE
.\spo-convert-pages-bulk.ps1 -SourceLibrary "ClassicPages" -FieldMapping field-mapping.json -Execute -ConfirmToken CONVERT-SPO-PAGES-BULK
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$SourceLibrary,

    [string]$TargetLibrary = "Site Pages",

    [string]$FieldMapping,

    [string]$LiteralFieldValues,

    [string]$PageName,

    [string]$ManifestPath = ".\run-manifest.csv",

    [switch]$ResumeFromManifest,

    [int]$ThrottleDelaySeconds = 2,

    [switch]$SkipValidation,

    [string]$WorkerScript = (Join-Path $PSScriptRoot "spo-convert-page-to-modern.ps1"),

    [string]$ValidationScript = (Join-Path $PSScriptRoot "spo-validate-page-conversion.ps1"),

    [string]$SiteUrl,

    [string]$ConfigPath = (Join-Path $PSScriptRoot "..\..\..\config.psd1"),

    [string]$ClientId,

    [string]$TenantId,

    [string]$TenantAdminUrl,

    [switch]$Execute,

    [string]$ConfirmToken
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "Get-WorkbenchConnectionConfig.ps1")

$connectionConfig = Get-WorkbenchConnectionConfig -Path $ConfigPath
if (-not $SiteUrl) { $SiteUrl = $connectionConfig.SiteUrl }
if (-not $ClientId) { $ClientId = $connectionConfig.ClientId }
if (-not $TenantId) { $TenantId = $connectionConfig.TenantId }
if (-not $TenantAdminUrl) { $TenantAdminUrl = $connectionConfig.TenantAdminUrl }

if (-not $SiteUrl -or -not $ClientId -or -not $TenantId) {
    throw "SiteUrl/ClientId/TenantId not resolved. Provide -SiteUrl/-ClientId/-TenantId or a valid -ConfigPath."
}
if (-not (Test-Path -LiteralPath $WorkerScript)) { throw "Worker script not found at '$WorkerScript'." }
if (-not $SkipValidation -and -not (Test-Path -LiteralPath $ValidationScript)) {
    throw "Validation script not found at '$ValidationScript'. Use -SkipValidation to skip it."
}

if (-not $Execute) {
    [ordered]@{
        operation = "convert-pages-bulk"
        site_url = $SiteUrl
        source_library = $SourceLibrary
        target_library = $TargetLibrary
        page_name_filter = $PageName
        manifest_path = $ManifestPath
        worker_script = $WorkerScript
        validation_script = $(if ($SkipValidation) { $null } else { $ValidationScript })
        safety = [ordered]@{
            tenant_io = "none"
            execute_requires_confirm_token = "CONVERT-SPO-PAGES-BULK"
        }
    } | ConvertTo-Json -Depth 8
    return
}

if ($ConfirmToken -ne "CONVERT-SPO-PAGES-BULK") {
    throw "-Execute requires -ConfirmToken CONVERT-SPO-PAGES-BULK."
}
if (-not (Get-Command Connect-PnPOnline -ErrorAction SilentlyContinue)) {
    throw "PnP.PowerShell is required. Install/import PnP.PowerShell before executing."
}

$alreadySucceeded = @{}
if ($ResumeFromManifest -and (Test-Path -LiteralPath $ManifestPath)) {
    Import-Csv -LiteralPath $ManifestPath | Where-Object { $_.Status -eq "Succeeded" } |
        ForEach-Object { $alreadySucceeded[$_.PageName] = $true }
    Write-Host "Resume mode: $($alreadySucceeded.Count) page(s) already succeeded -- will skip." -ForegroundColor Yellow
}
if (-not (Test-Path -LiteralPath $ManifestPath)) {
    "PageName,Status,StartedAt,CompletedAt,DurationSeconds,Error" | Out-File -FilePath $ManifestPath -Encoding utf8
}

$connectParameters = @{
    Url         = $SiteUrl
    ClientId    = $ClientId
    Tenant      = $TenantId
    Interactive = $true
}
if ($TenantAdminUrl) { $connectParameters["TenantAdminUrl"] = $TenantAdminUrl }
Connect-PnPOnline @connectParameters

$pages = Get-PnPListItem -List $SourceLibrary -PageSize 2000 -Fields @("FileRef", "FileLeafRef")
if ($PageName) {
    $pages = $pages | Where-Object { $_.FieldValues["FileLeafRef"] -eq $PageName }
    if (-not $pages) { throw "No page named '$PageName' found in '$SourceLibrary'." }
}
Disconnect-PnPOnline -ErrorAction SilentlyContinue

$stats = @{ Succeeded = 0; Failed = 0; Skipped = 0 }
$counter = 0
$total = @($pages).Count

foreach ($page in $pages) {
    $currentPageName = $page.FieldValues["FileLeafRef"]
    $counter++

    if ($alreadySucceeded.ContainsKey($currentPageName)) {
        Write-Host "[$counter/$total] SKIP $currentPageName (already succeeded)" -ForegroundColor DarkGray
        $stats.Skipped++
        continue
    }

    $startedAt = Get-Date
    $workerArgs = @(
        "-NonInteractive", "-File", $WorkerScript,
        "-PageName", $currentPageName,
        "-SourceLibrary", $SourceLibrary,
        "-TargetLibrary", $TargetLibrary,
        "-SiteUrl", $SiteUrl, "-ClientId", $ClientId, "-TenantId", $TenantId,
        "-Execute", "-ConfirmToken", "CONVERT-SPO-PAGE"
    )
    if ($FieldMapping) { $workerArgs += @("-FieldMapping", $FieldMapping) }
    if ($LiteralFieldValues) { $workerArgs += @("-LiteralFieldValues", $LiteralFieldValues) }
    if ($TenantAdminUrl) { $workerArgs += @("-TenantAdminUrl", $TenantAdminUrl) }

    $stderr = $null
    $exitCode = 0
    try {
        $output = & pwsh @workerArgs 2>&1
        $exitCode = $LASTEXITCODE
        $stderr = ($output | Where-Object { $_ -is [System.Management.Automation.ErrorRecord] } |
            Select-Object -First 1 | ForEach-Object { $_.Exception.Message }) -join ""
    }
    catch {
        $exitCode = 1
        $stderr = $_.Exception.Message
    }

    $completedAt = Get-Date
    $durationSeconds = [math]::Round(($completedAt - $startedAt).TotalSeconds, 1)
    $status = if ($exitCode -eq 0) { "Succeeded" } else { "Failed" }

    if ($status -eq "Succeeded") {
        Write-Host "[$counter/$total] OK   $currentPageName (${durationSeconds}s)" -ForegroundColor Green
        $stats.Succeeded++
    } else {
        Write-Warning "[$counter/$total] FAIL $currentPageName (${durationSeconds}s) -- $stderr"
        $stats.Failed++
    }

    $errorText = if ($stderr) { $stderr -replace '"', "'" -replace "`r`n|`n", " " } else { "" }
    "$currentPageName,$status,$($startedAt.ToString('o')),$($completedAt.ToString('o')),$durationSeconds,`"$errorText`"" |
        Out-File -FilePath $ManifestPath -Append -Encoding utf8

    if ($counter -lt $total) { Start-Sleep -Seconds $ThrottleDelaySeconds }
}

Write-Host ""
Write-Host "Succeeded: $($stats.Succeeded)  Failed: $($stats.Failed)  Skipped: $($stats.Skipped)  Total: $total"

if (-not $SkipValidation) {
    Write-Host ""
    Write-Host "Running validation..." -ForegroundColor Cyan
    $validateArgs = @(
        "-NonInteractive", "-File", $ValidationScript,
        "-ManifestPath", $ManifestPath, "-TargetLibrary", $TargetLibrary,
        "-ReportPath", ([System.IO.Path]::ChangeExtension($ManifestPath, $null) + "test-report.csv"),
        "-SiteUrl", $SiteUrl, "-ClientId", $ClientId, "-TenantId", $TenantId
    )
    if ($FieldMapping) { $validateArgs += @("-FieldMapping", $FieldMapping) }
    if ($LiteralFieldValues) { $validateArgs += @("-LiteralFieldValues", $LiteralFieldValues) }
    if ($TenantAdminUrl) { $validateArgs += @("-TenantAdminUrl", $TenantAdminUrl) }
    & pwsh @validateArgs
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Validation reported failures -- check the test report."
        exit 1
    }
}
