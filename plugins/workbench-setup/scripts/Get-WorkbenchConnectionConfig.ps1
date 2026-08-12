<#
.SYNOPSIS
Shared helper: resolves the Workbench SharePoint connection config from
config.psd1 into a single flat object.

.DESCRIPTION
Canonical, deduplicated copy of a function that was previously duplicated
verbatim across 11 .ps1 scripts in 3 plugins (sharepoint-content-publication,
sharepoint-discovery, sharepoint-link-remediation). Owned by workbench-setup
(which already owns config.psd1 concerns) and dot-sourced by consumers, e.g.:

    . (Join-Path $PSScriptRoot "Get-WorkbenchConnectionConfig.ps1")

Supports both a flat config.psd1 shape (SiteUrl/ClientId/TenantId/
TenantAdminUrl at the top level) and a nested shape (Connection.SiteUrl/
Connection.ClientId/Connection.TenantId + Authentication.TenantAdminUrl).

.PARAMETER Path
Path to config.psd1.
#>

function Get-WorkbenchConnectionConfig {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return [pscustomobject]@{ SiteUrl = $null; ClientId = $null; TenantId = $null; TenantAdminUrl = $null }
    }

    $rawConfig = Import-PowerShellDataFile -LiteralPath $Path
    $cfg = if ($rawConfig.Connection) { $rawConfig.Connection } else { $rawConfig }
    $tenantAdminUrl = if ($rawConfig.Authentication) { $rawConfig.Authentication.TenantAdminUrl } else { $rawConfig.TenantAdminUrl }

    [pscustomobject]@{
        SiteUrl        = $cfg.SiteUrl
        ClientId       = $cfg.ClientId
        TenantId       = $cfg.TenantId
        TenantAdminUrl = $tenantAdminUrl
    }
}
