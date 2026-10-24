<#
.SYNOPSIS
    Read-only export of every file in a SharePoint Online document library to a CSV listing.

.DESCRIPTION
    Writes ServerRelativeUrl,SizeBytes for each file (folders excluded) so that
    library_migration_ledger.py verify (or reconcile) can confirm what is on the target.
    Makes no changes to the tenant. DEV-only: refuses a SiteUrl without 'DEV'.

.KEY INPUT DEPENDENCIES
    - -ConfigPath: config-spo-dev.psd1 (Connection.SiteUrl/ClientId/TenantId).
    - PnP.PowerShell; interactive sign-in.

.EXAMPLE
    pwsh -File plugins\sp-migration\scripts\migration\export-library-listing.ps1 `
      -ConfigPath config-spo-dev.psd1 -Library Administration -OutputPath temp\administration-admin-docs\target-listing.csv
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$ConfigPath,
    [Parameter(Mandatory = $true)][string]$Library,
    [Parameter(Mandatory = $true)][string]$OutputPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$cfg = (Import-PowerShellDataFile -LiteralPath $ConfigPath).Connection
if (-not $cfg.SiteUrl -or -not $cfg.ClientId -or -not $cfg.TenantId) { throw "Connection.SiteUrl/ClientId/TenantId missing in $ConfigPath" }
if ($cfg.SiteUrl -notmatch "DEV") { throw "Refusing non-DEV site: $($cfg.SiteUrl)" }

Connect-PnPOnline -Url $cfg.SiteUrl -ClientId $cfg.ClientId -Tenant $cfg.TenantId -Interactive
$items = Get-PnPListItem -List $Library -PageSize 500 -Fields "FileRef", "File_x0020_Size", "FSObjType"
$rows = foreach ($i in $items) {
    if ([int]$i["FSObjType"] -eq 0) {
        [pscustomobject]@{ ServerRelativeUrl = $i["FileRef"]; SizeBytes = $i["File_x0020_Size"] }
    }
}
$dir = Split-Path -Parent $OutputPath
if ($dir -and -not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
@($rows) | Export-Csv -LiteralPath $OutputPath -NoTypeInformation -Encoding UTF8
Write-Host "Wrote $(@($rows).Count) file(s) from '$Library' to $OutputPath"
