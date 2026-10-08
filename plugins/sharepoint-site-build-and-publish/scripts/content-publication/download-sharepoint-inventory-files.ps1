<#
.SYNOPSIS
Plans or downloads selected files from a recursive inventory CSV, preserving source identity.
.DESCRIPTION
Uses the existing canonical spo-download-file.ps1 for each selected file. Both
Online and on-prem are supported; Auto uses standard SharePoint Online hostnames.
Dry-run writes only downloads.csv locally. Real downloads require -Execute and
-ConfirmToken DOWNLOAD-SHAREPOINT-INVENTORY-FILES. No tenant writes.
Hash-keyed local directories prevent equal filenames in different subsites colliding.
Default extensions are html,htm,aspx; pass a comma-separated list to include Office files.
The user runs live downloads; never invoke them in a background agent session.
Prints Started, Finished and Elapsed (hh:mm:ss) on the console, also when the run fails.
.EXAMPLE
pwsh -File download-sharepoint-inventory-files.ps1 -InventoryCsv ./inventory/files.csv -ConfigPath ./config.psd1 -OutputDir ./downloads
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$InventoryCsv,
    [Parameter(Mandatory = $true)][string]$ConfigPath,
    [Parameter(Mandatory = $true)][string]$OutputDir,
    [string]$Extensions = 'html,htm,aspx',
    [ValidateSet('Auto', 'Online', 'OnPrem')][string]$Platform = 'Auto',
    [pscredential]$Credential,
    [switch]$Overwrite,
    [switch]$Execute,
    [string]$ConfirmToken
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Runtime tracking: Started/Finished/Elapsed are printed on the console, including when the run fails.
$script:RunStart = Get-Date
Write-Host "Started:  $($script:RunStart.ToString('yyyy-MM-dd HH:mm:ss'))"
try {
if ($Execute -and $ConfirmToken -ne 'DOWNLOAD-SHAREPOINT-INVENTORY-FILES') {
    throw '-Execute requires -ConfirmToken DOWNLOAD-SHAREPOINT-INVENTORY-FILES.'
}
if (-not (Test-Path -LiteralPath $ConfigPath -PathType Leaf)) { throw 'ConfigPath does not exist.' }
$selectedExtensions = @($Extensions.Split(',') | ForEach-Object { $_.Trim().TrimStart('.').ToLowerInvariant() })
$rows = @(Import-Csv -LiteralPath $InventoryCsv | Where-Object { $_.FileExtension.ToLowerInvariant() -in $selectedExtensions })
$outputRoot = [IO.Path]::GetFullPath($OutputDir)
$records = [System.Collections.Generic.List[object]]::new()
$failed = 0
$authFailed = $false
foreach ($row in $rows) {
    $localPath = ''
    $status = 'PLANNED'
    $message = ''
    try {
        $uri = [uri]$row.FileUrl
        if (-not $uri.IsAbsoluteUri -or $uri.Scheme -notin @('https', 'http')) { throw 'FileUrl must be an absolute HTTP(S) URL.' }
        $hash = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($row.FileUrl))).ToLowerInvariant()
        $directory = Join-Path $outputRoot $hash
        $safeName = 'file-' + ($row.FileName -replace '[<>:"/\\|?*\x00-\x1f]', '_').TrimEnd('.', ' ')
        $localPath = Join-Path $directory $safeName
        $chosenPlatform = $Platform
        if ($chosenPlatform -eq 'Auto') {
            $chosenPlatform = if ($uri.Host -match '(^|\.)sharepoint\.(com|us|de|cn)$') { 'Online' } else { 'OnPrem' }
        }
        $arguments = @{
            RemoteUrl = $row.FileUrl; SiteUrl = $row.WebUrl; DestinationDir = $directory
            FileName = $safeName; ConfigPath = $ConfigPath; Overwrite = $Overwrite
            Execute = $Execute; TargetPlatform = $chosenPlatform
        }
        if ($chosenPlatform -eq 'OnPrem') { $arguments.FromSource = $true; $arguments.RawFile = $true }
        if ($Execute -and $chosenPlatform -eq 'OnPrem' -and -not $Credential) {
            $Credential = Get-Credential -Message 'Enter the on-prem SharePoint domain account'
            if (-not $Credential) { throw 'On-prem credentials were not supplied.' }
        }
        if ($Credential) { $arguments.Credential = $Credential }
        if ($Execute) { $arguments.ConfirmToken = 'DOWNLOAD-SPO-FILE' }
        & (Join-Path $PSScriptRoot 'spo-download-file.ps1') @arguments | Out-Null
        if ($Execute) { $status = 'DOWNLOADED' }
    } catch {
        $failed++
        $status = 'FAILED'
        $message = $_.Exception.Message
        Write-Warning "Download '$($row.FileUrl)': $message"
        # Repeating a rejected credential on every file locks the domain account, so stop at the first auth failure.
        if ($message -match '\b401\b|Unauthorized|logon failure|credentials? (were|was) not supplied') { $authFailed = $true }
    }
    $records.Add([pscustomobject][ordered]@{
        FileUrl = $row.FileUrl; WebUrl = $row.WebUrl; LibraryTitle = $row.LibraryTitle
        FileName = $row.FileName; RelativePath = $row.RelativePath
        LocalPath = $localPath; Status = $status; Message = $message
    })
    if ($authFailed) {
        $remaining = @($rows | Select-Object -Skip $records.Count)
        foreach ($skipped in $remaining) {
            $records.Add([pscustomobject][ordered]@{
                FileUrl = $skipped.FileUrl; WebUrl = $skipped.WebUrl; LibraryTitle = $skipped.LibraryTitle
                FileName = $skipped.FileName; RelativePath = $skipped.RelativePath
                LocalPath = ''; Status = 'NOT_ATTEMPTED'; Message = 'Skipped after authentication failure.'
            })
        }
        break
    }
}
New-Item -ItemType Directory -Path $outputRoot -Force | Out-Null
$manifest = Join-Path $outputRoot 'downloads.csv'
if ($records.Count) { $records | Export-Csv -LiteralPath $manifest -NoTypeInformation -Encoding utf8 }
else { '"FileUrl","WebUrl","LibraryTitle","FileName","RelativePath","LocalPath","Status","Message"' | Set-Content -LiteralPath $manifest -Encoding utf8 }
Write-Host "Wrote $($records.Count) download record(s) to $manifest; failures: $failed."
if ($authFailed) { throw 'Authentication failed; aborted after the first rejected request to avoid locking the account. Verify the password, then re-run.' }
if ($failed) { throw 'Some files could not be planned/downloaded; inspect downloads.csv.' }
}
finally {
    $runEnd = Get-Date
    $runElapsed = $runEnd - $script:RunStart
    Write-Host "Finished: $($runEnd.ToString('yyyy-MM-dd HH:mm:ss'))"
    Write-Host ("Elapsed:  {0:00}:{1:00}:{2:00}" -f [math]::Floor($runElapsed.TotalHours), $runElapsed.Minutes, $runElapsed.Seconds)
}
