<#
.SYNOPSIS
    Registers, previews, verifies or removes an SPFx Application Customizer as a
    site- or web-scoped custom action.

.DESCRIPTION
    Creates or updates a ClientSideExtension.ApplicationCustomizer custom action so the
    extension runs on every page of one site (Scope Web) or site collection (Scope Site).
    Needed when the package was deployed with skipFeatureDeployment (the extension is not
    activated by installing the app). Dry-run by default: nothing is written unless
    -Execute and -ConfirmToken REGISTER-SPO-APPCUSTOMIZER are both supplied. -Remove
    deletes every matching action (idempotent); it never touches the package or the app.
    After a write the action is re-queried and printed, so success is proven, not assumed.

    Key Input Dependencies:
      - PnP.PowerShell 3.x and a config .psd1 (SiteUrl, ClientId, TenantId) or overrides.
      - The extension manifest id (GUID) from src/extensions/<name>/*.manifest.json.

    Function Index:
      - Get-MatchingAction : finds actions by Name or ClientSideComponentId.

.EXAMPLE
    pwsh -File scripts/register-application-customizer.ps1 `
      -Name "CustomNavigation" -Title "Custom Navigation" `
      -ComponentId "00000000-0000-0000-0000-000000000000" -ConfigPath ".\config-spo-dev.psd1"

.EXAMPLE
    pwsh -File scripts/register-application-customizer.ps1 `
      -Name "CustomNavigation" -ComponentId "00000000-0000-0000-0000-000000000000" `
      -ConfigPath ".\config-spo-dev.psd1" -Execute -ConfirmToken REGISTER-SPO-APPCUSTOMIZER

.EXAMPLE
    pwsh -File scripts/register-application-customizer.ps1 `
      -Name "CustomNavigation" -ComponentId "00000000-0000-0000-0000-000000000000" `
      -ConfigPath ".\config-spo-dev.psd1" -Remove -Execute -ConfirmToken REGISTER-SPO-APPCUSTOMIZER
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Name,
    [string]$Title = $Name,
    [Parameter(Mandatory)][guid]$ComponentId,
    [string]$ComponentProperties = '{}',
    [ValidateRange(0, 65536)][int]$Sequence = 10,
    [ValidateSet('Web', 'Site')][string]$Scope = 'Web',
    [string]$ConfigPath = '',
    [string]$SiteUrl = '',
    [string]$ClientId = '',
    [string]$TenantId = '',
    [switch]$Remove,
    [switch]$Execute,
    [string]$ConfirmToken = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$requiredToken = 'REGISTER-SPO-APPCUSTOMIZER'
$location = 'ClientSideExtension.ApplicationCustomizer'

if ($ConfigPath) {
    $resolvedConfigPath = (Resolve-Path -LiteralPath $ConfigPath -ErrorAction Stop).Path
    $config = Import-PowerShellDataFile -LiteralPath $resolvedConfigPath
    if (-not $SiteUrl -and $config.SiteUrl) { $SiteUrl = $config.SiteUrl }
    if (-not $ClientId -and $config.ClientId) { $ClientId = $config.ClientId }
    if (-not $TenantId -and $config.TenantId) { $TenantId = $config.TenantId }
}

foreach ($requiredValue in @(
    @{ Name = 'SiteUrl'; Value = $SiteUrl },
    @{ Name = 'ClientId'; Value = $ClientId },
    @{ Name = 'TenantId'; Value = $TenantId }
)) {
    if ([string]::IsNullOrWhiteSpace([string]$requiredValue.Value)) {
        throw "$($requiredValue.Name) is required directly or through -ConfigPath."
    }
}

if ($Execute -and $ConfirmToken -ne $requiredToken) {
    throw "Live writes require -Execute and -ConfirmToken $requiredToken."
}

try {
    $null = $ComponentProperties | ConvertFrom-Json -ErrorAction Stop
}
catch {
    throw "-ComponentProperties must be valid JSON: $($_.Exception.Message)"
}

$componentIdText = $ComponentId.ToString()

# Finds actions at this scope that match by stable name or by component id.
function Get-MatchingAction {
    param([string]$ActionName, [string]$ActionComponentId, [string]$ActionScope)
    @(Get-PnPCustomAction -Scope $ActionScope | Where-Object {
        $_.Name -eq $ActionName -or
        ($null -ne $_.ClientSideComponentId -and $_.ClientSideComponentId.ToString() -eq $ActionComponentId)
    })
}

try {
    Connect-PnPOnline -Url $SiteUrl -ClientId $ClientId -Tenant $TenantId -Interactive

    $matches = Get-MatchingAction -ActionName $Name -ActionComponentId $componentIdText -ActionScope $Scope
    $mode = if ($Execute) { 'EXECUTE' } else { 'DRY-RUN' }
    Write-Host "Mode: $mode  Site: $SiteUrl  Scope: $Scope  Matches: $($matches.Count)" -ForegroundColor Cyan

    if ($Remove) {
        if ($matches.Count -eq 0) {
            Write-Host 'No matching Application Customizer action exists.' -ForegroundColor Yellow
            return
        }
        if (-not $Execute) {
            Write-Host "Would remove $($matches.Count) action(s). Add -Execute -ConfirmToken $requiredToken to apply." -ForegroundColor Yellow
            return
        }
        foreach ($action in $matches) {
            Remove-PnPCustomAction -Identity $action.Id -Scope $Scope -Force
        }
        $remaining = Get-MatchingAction -ActionName $Name -ActionComponentId $componentIdText -ActionScope $Scope
        Write-Host "Removed $($matches.Count) action(s); $($remaining.Count) remain." -ForegroundColor Green
        return
    }

    if ($matches.Count -gt 1) {
        throw "Found $($matches.Count) actions matching Name '$Name' or ComponentId '$componentIdText'. Remove duplicates with -Remove first."
    }

    $operation = if ($matches.Count -eq 1) { 'update' } else { 'create' }
    if (-not $Execute) {
        Write-Host "Would $operation '$Title' ($componentIdText) at $location, sequence $Sequence. Add -Execute -ConfirmToken $requiredToken to apply." -ForegroundColor Yellow
        return
    }

    if ($operation -eq 'create') {
        Add-PnPCustomAction -Name $Name -Title $Title -Location $location -Sequence $Sequence `
            -ClientSideComponentId $componentIdText -ClientSideComponentProperties $ComponentProperties -Scope $Scope | Out-Null
    }
    else {
        Set-PnPCustomAction -Identity $matches[0].Id -Scope $Scope -Title $Title -Sequence $Sequence `
            -ClientSideComponentId $componentIdText -ClientSideComponentProperties $ComponentProperties | Out-Null
    }

    $verified = Get-MatchingAction -ActionName $Name -ActionComponentId $componentIdText -ActionScope $Scope
    if ($verified.Count -ne 1) {
        throw "Verification failed: expected exactly 1 matching action after $operation, found $($verified.Count)."
    }
    Write-Host "Verified: $operation OK. Name=$($verified[0].Name) ComponentId=$($verified[0].ClientSideComponentId) Location=$($verified[0].Location) Sequence=$($verified[0].Sequence)" -ForegroundColor Green
}
finally {
    Disconnect-PnPOnline -ErrorAction SilentlyContinue
}
