<#
.SYNOPSIS
    Registers or removes a list-scoped SPFx ListView Command Set.

.DESCRIPTION
    Creates or updates a ClientSideExtension.ListViewCommandSet.CommandBar custom action
    on one SharePoint list or document library. Use -Remove for idempotent rollback.

.EXAMPLE
    pwsh -File scripts/register-listview-command-set.ps1 `
      -ListName "Documents" `
      -Name "CustomUploaderCommandSet" `
      -Title "Custom Upload" `
      -ComponentId "85e7a62e-b444-438c-810d-ce4e35b4801a" `
      -ConfigPath ".\config-test.psd1"

.EXAMPLE
    pwsh -File scripts/register-listview-command-set.ps1 `
      -ListName "Documents" `
      -Name "CustomUploaderCommandSet" `
      -ComponentId "85e7a62e-b444-438c-810d-ce4e35b4801a" `
      -ConfigPath ".\config-test.psd1" `
      -Remove
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)][string]$ListName,
    [Parameter(Mandatory)][string]$Name,
    [string]$Title = $Name,
    [Parameter(Mandatory)][guid]$ComponentId,
    [string]$ComponentProperties = '{}',
    [ValidateRange(0, 65536)][int]$Sequence = 10,
    [string]$ConfigPath = '',
    [string]$SiteUrl = '',
    [string]$ClientId = '',
    [string]$TenantId = '',
    [switch]$Remove
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

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

$componentIdText = $ComponentId.ToString()
$location = 'ClientSideExtension.ListViewCommandSet.CommandBar'

try {
    Connect-PnPOnline -Url $SiteUrl -ClientId $ClientId -Tenant $TenantId -Interactive

    $list = Get-PnPList -Identity $ListName -Includes Title, UserCustomActions
    Get-PnPProperty -ClientObject $list -Property UserCustomActions | Out-Null

    $matches = @($list.UserCustomActions | Where-Object {
        $_.Name -eq $Name -or
        ($null -ne $_.ClientSideComponentId -and $_.ClientSideComponentId.ToString() -eq $componentIdText)
    })

    if ($Remove) {
        if ($matches.Count -eq 0) {
            Write-Host "No matching list custom action exists on '$($list.Title)'." -ForegroundColor Yellow
            return
        }

        if ($PSCmdlet.ShouldProcess($list.Title, "Remove $($matches.Count) matching ListView Command Set action(s)")) {
            foreach ($action in $matches) {
                $action.DeleteObject()
            }
            Invoke-PnPQuery
            Write-Host "Removed $($matches.Count) matching list custom action(s) from '$($list.Title)'." -ForegroundColor Green
        }
        return
    }

    if ($matches.Count -gt 1) {
        throw "Found $($matches.Count) actions matching Name '$Name' or ComponentId '$componentIdText'. Remove duplicates with -Remove before registering."
    }

    if ($PSCmdlet.ShouldProcess($list.Title, "Register ListView Command Set '$Title'")) {
        $action = $matches | Select-Object -First 1
        $operation = 'Updated'
        if ($null -eq $action) {
            $action = $list.UserCustomActions.Add()
            $operation = 'Created'
        }

        $action.Name = $Name
        $action.Title = $Title
        $action.Location = $location
        $action.Sequence = $Sequence
        $action.ClientSideComponentId = $componentIdText
        $action.ClientSideComponentProperties = $ComponentProperties
        $action.Update()
        Invoke-PnPQuery

        Write-Host "$operation ListView Command Set '$Title' on '$($list.Title)'." -ForegroundColor Green
        Write-Host "  ComponentId : $componentIdText" -ForegroundColor DarkGray
        Write-Host "  Sequence    : $Sequence" -ForegroundColor DarkGray
    }
}
finally {
    Disconnect-PnPOnline -ErrorAction SilentlyContinue
}
