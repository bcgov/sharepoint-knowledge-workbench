<#
.SYNOPSIS
Shared helper: resolves the Workbench SharePoint connection config from
config.psd1 into a single flat object.

.DESCRIPTION
Canonical, deduplicated copy of a function that was previously duplicated
verbatim across 11 .ps1 scripts in 3 plugins (sharepoint-site-build-and-publish,
sharepoint-site-assessment, sharepoint-site-migration). Owned by sharepoint-workbench-setup
(which already owns config.psd1 concerns) and dot-sourced by consumers, e.g.:

    . (Join-Path $PSScriptRoot "Get-WorkbenchConnectionConfig.ps1")

Supports both a flat config.psd1 shape (SiteUrl/ClientId/TenantId/
TenantAdminUrl at the top level) and a nested shape (Connection.SiteUrl/
Connection.ClientId/Connection.TenantId + Authentication.TenantAdminUrl).
Optional dictionary keys remain null under strict-mode callers; missing
Connection/Authentication sections do not invalidate a flat profile.

.PARAMETER Path
Path to config.psd1.
#>

function Get-WorkbenchConnectionConfig {
    [CmdletBinding()]
    param([Parameter(Mandatory = $false)][string]$Path)

    $resolvedPath = $null
    if ($Path) {
        if (-not (Test-Path -LiteralPath $Path)) {
            throw "Explicitly specified ConfigPath '$Path' does not exist."
        }
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
        return [pscustomobject]@{
            SiteUrl               = $null
            ClientId              = $null
            TenantId              = $null
            TenantAdminUrl        = $null
            AuthenticationMode    = "Interactive"
            CertificateThumbprint = $null
            CertificatePath       = $null
            ConfigPath            = $null
        }
    }

    $rawConfig = Import-PowerShellDataFile -LiteralPath $resolvedPath
    # Dictionary indexing tolerates optional sections/keys under strict mode.
    $cfg = if ($rawConfig['Connection']) { $rawConfig['Connection'] } else { $rawConfig }
    $auth = if ($rawConfig['Authentication']) { $rawConfig['Authentication'] } else { @{} }
    $tenantAdminUrl = if ($auth.Contains('TenantAdminUrl')) {
        $auth['TenantAdminUrl']
    } elseif ($rawConfig.Contains('TenantAdminUrl')) {
        $rawConfig['TenantAdminUrl']
    } else {
        $null
    }
    $authMode = if ($cfg['AuthenticationMode']) {
        $cfg['AuthenticationMode']
    } elseif ($rawConfig['AuthenticationMode']) {
        $rawConfig['AuthenticationMode']
    } else {
        "Interactive"
    }
    $certThumbprint = if ($auth.Contains('CertificateThumbprint')) {
        $auth['CertificateThumbprint']
    } elseif ($rawConfig.Contains('CertificateThumbprint')) {
        $rawConfig['CertificateThumbprint']
    } else {
        $null
    }
    $certPath = if ($auth.Contains('CertificatePath')) {
        $auth['CertificatePath']
    } elseif ($rawConfig.Contains('CertificatePath')) {
        $rawConfig['CertificatePath']
    } else {
        $null
    }

    [pscustomobject]@{
        SiteUrl               = $cfg['SiteUrl']
        ClientId              = $cfg['ClientId']
        TenantId              = $cfg['TenantId']
        TenantAdminUrl        = $tenantAdminUrl
        AuthenticationMode    = $authMode
        CertificateThumbprint = $certThumbprint
        CertificatePath       = $certPath
        ConfigPath            = $resolvedPath
    }
}

