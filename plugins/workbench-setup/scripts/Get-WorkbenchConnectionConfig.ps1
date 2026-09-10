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
    param([Parameter(Mandatory = $false)][string]$Path)

    $resolvedPath = $null
    if ($Path -and (Test-Path -LiteralPath $Path)) {
        $resolvedPath = (Resolve-Path -LiteralPath $Path).Path
    } else {
        $candidates = @(
            "$PWD\config.psd1",
            "$PSScriptRoot\..\..\..\..\config.psd1",
            "$PSScriptRoot\..\..\..\config.psd1",
            "$PSScriptRoot\..\..\config.psd1",
            "$PSScriptRoot\..\config.psd1",
            "$PSScriptRoot\config.psd1"
        )
        foreach ($cand in $candidates) {
            if (Test-Path -LiteralPath $cand) {
                $resolvedPath = (Resolve-Path -LiteralPath $cand).Path
                break
            }
        }
    }

    if (-not $resolvedPath -or -not (Test-Path -LiteralPath $resolvedPath)) {
        return [pscustomobject]@{ SiteUrl = $null; ClientId = $null; TenantId = $null; TenantAdminUrl = $null; ConfigPath = $null }
    }

    $rawConfig = Import-PowerShellDataFile -LiteralPath $resolvedPath
    $cfg = if ($rawConfig.Connection) { $rawConfig.Connection } else { $rawConfig }
    $tenantAdminUrl = if ($rawConfig.Authentication -and $rawConfig.Authentication.Contains('TenantAdminUrl')) {
        $rawConfig.Authentication['TenantAdminUrl']
    } elseif ($rawConfig.Contains('TenantAdminUrl')) {
        $rawConfig['TenantAdminUrl']
    } else {
        $null
    }

    [pscustomobject]@{
        SiteUrl        = $cfg.SiteUrl
        ClientId       = $cfg.ClientId
        TenantId       = $cfg.TenantId
        TenantAdminUrl = $tenantAdminUrl
        ConfigPath     = $resolvedPath
    }
}

