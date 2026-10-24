<#
.SYNOPSIS
    Read-only download of one or more SharePoint Online modern pages (raw .aspx plus CanvasContent1 JSON).

.DESCRIPTION
    For each page in -PageUrl writes <name>.aspx and <name>.canvas.json (the stored canvas
    layout, including SPFx web part ids and properties) under -OutputDirectory, so a hand-built
    page can be compared with a published one. Makes no changes to the tenant. DEV-only:
    refuses a SiteUrl without 'DEV'.

.KEY INPUT DEPENDENCIES
    - -ConfigPath: config-spo-dev.psd1 (Connection.SiteUrl/ClientId/TenantId).
    - PnP.PowerShell; interactive sign-in.

.INDEX
    - Export-ModernPage: downloads one page and its CanvasContent1.

.EXAMPLE
    pwsh -File plugins\sp-migration\scripts\migration\export-modern-page.ps1 `
      -ConfigPath config-spo-dev.psd1 `
      -PageUrl /SitePages/Operations/test.aspx, /SitePages/Operations/BCSS-Training-Section.aspx `
      -OutputDirectory temp\canvas-compare
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$ConfigPath,
    [Parameter(Mandatory = $true)][string[]]$PageUrl,
    [Parameter(Mandatory = $true)][string]$OutputDirectory
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Export-ModernPage {
    param([string]$SiteUrl, [string]$ServerRelativeUrl, [string]$Directory)

    $name = [System.IO.Path]::GetFileNameWithoutExtension($ServerRelativeUrl)
    Get-PnPFile -Url $ServerRelativeUrl -Path $Directory -FileName "$name.aspx" -AsFile -Force | Out-Null
    $siteRelative = $ServerRelativeUrl.TrimStart("/")
    $fileRef = "$(([Uri]$SiteUrl).AbsolutePath.TrimEnd('/'))/$siteRelative"
    $item = Get-PnPListItem -List "Site Pages" -Query (
        "<View Scope='RecursiveAll'><Query><Where><Eq><FieldRef Name='FileRef'/><Value Type='Text'>$fileRef</Value></Eq></Where></Query></View>"
    ) | Select-Object -First 1
    if (-not $item) { throw "Site Pages item not found: $fileRef" }
    [string]$item.FieldValues["CanvasContent1"] | Set-Content -LiteralPath (Join-Path $Directory "$name.canvas.json") -Encoding UTF8
    Write-Host "Exported $ServerRelativeUrl -> $Directory\$name.aspx, $name.canvas.json"
}

$cfg = (Import-PowerShellDataFile -LiteralPath $ConfigPath).Connection
if (-not $cfg.SiteUrl -or -not $cfg.ClientId -or -not $cfg.TenantId) { throw "Connection.SiteUrl/ClientId/TenantId missing in $ConfigPath" }
if ($cfg.SiteUrl -notmatch "DEV") { throw "Refusing non-DEV site: $($cfg.SiteUrl)" }

if (-not (Test-Path -LiteralPath $OutputDirectory)) { New-Item -ItemType Directory -Path $OutputDirectory | Out-Null }
Connect-PnPOnline -Url $cfg.SiteUrl -ClientId $cfg.ClientId -Tenant $cfg.TenantId -Interactive
foreach ($url in ($PageUrl | ForEach-Object { $_ -split "," } | Where-Object { $_.Trim() })) { Export-ModernPage -SiteUrl $cfg.SiteUrl -ServerRelativeUrl $url.Trim() -Directory $OutputDirectory }
