<#
.SYNOPSIS
Rewrites a broken/relocated embedded <img> reference inside a rich-text list
field, using a FieldImageRemediationPlan produced by field_image_remediation.py.

.DESCRIPTION
Reads a FieldImageRemediationPlan JSON file matching
FieldImageRemediationPlan.to_dict()'s shape (changed_items[].source_id,
changed_items[].new_field_value, confirmation_token). `source_id` is the
list item's Id. For each changed item: Get-PnPListItem by -ListName and
-Identity, then Set-PnPListItem -Values @{<FieldName> = new_field_value}.

By default performs no SharePoint tenant I/O; -Execute plus -ConfirmToken
REMEDIATE-SPO-FIELD-IMAGES runs the real writes.

.PARAMETER PlanPath
Path to a FieldImageRemediationPlan JSON file matching
FieldImageRemediationPlan.to_dict()'s shape.

.PARAMETER ListName
The list whose items' image field is being remediated.

.PARAMETER FieldName
The internal name of the rich-text field to overwrite, e.g. "Picture".

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
Runs the real Get-PnPListItem/Set-PnPListItem calls. Omit this to print the
per-item plan only.

.PARAMETER ConfirmToken
Required with -Execute. Must be REMEDIATE-SPO-FIELD-IMAGES.

.EXAMPLE
.\spo-remediate-field-image-references.ps1 -PlanPath plan.json -ListName "Authors" -FieldName "Picture" -SiteUrl "https://tenant.sharepoint.com/sites/Test" -Execute -ConfirmToken REMEDIATE-SPO-FIELD-IMAGES
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PlanPath,

    [Parameter(Mandatory = $true)]
    [string]$ListName,

    [Parameter(Mandatory = $true)]
    [string]$FieldName,

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

if (-not (Test-Path -LiteralPath $PlanPath)) {
    throw "PlanPath '$PlanPath' does not exist."
}
$plan = Get-Content -LiteralPath $PlanPath -Raw | ConvertFrom-Json
$changedItems = @($plan.changed_items)
if ($changedItems.Count -eq 0) {
    Write-Host "No changed_items in plan -- nothing to remediate."
    return
}

if ($Execute) {
    if ($ConfirmToken -ne "REMEDIATE-SPO-FIELD-IMAGES") {
        throw "-Execute requires -ConfirmToken REMEDIATE-SPO-FIELD-IMAGES."
    }
    if (-not (Get-Command Set-PnPListItem -ErrorAction SilentlyContinue)) {
        throw "PnP.PowerShell with Set-PnPListItem is required. Install/import PnP.PowerShell before executing."
    }

    $connectParameters = @{
        Url         = $SiteUrl
        ClientId    = $ClientId
        Tenant      = $TenantId
        Interactive = $true
    }
    if ($TenantAdminUrl) { $connectParameters["TenantAdminUrl"] = $TenantAdminUrl }
    Connect-PnPOnline @connectParameters

    $results = foreach ($fix in $changedItems) {
        try {
            Set-PnPListItem -List $ListName -Identity $fix.source_id -Values @{ $FieldName = $fix.new_field_value } | Out-Null

            [pscustomobject]@{
                source_id = $fix.source_id
                success   = $true
            }
        }
        catch {
            [pscustomobject]@{
                source_id = $fix.source_id
                success   = $false
                error     = $_.Exception.Message
            }
        }
    }

    $results | ConvertTo-Json -Depth 8
}
else {
    $actionPlans = foreach ($fix in $changedItems) {
        [ordered]@{
            source_id    = $fix.source_id
            update_field = "Set-PnPListItem -List `"$ListName`" -Identity $($fix.source_id) -Values @{`"$FieldName`" = <new_field_value>}"
        }
    }

    $summary = [ordered]@{
        operation = "remediate-spo-field-image-references"
        list_name = $ListName
        field_name = $FieldName
        confirmation_token = $plan.confirmation_token
        changed_item_count = $changedItems.Count
        site_url = $SiteUrl
        safety = [ordered]@{
            tenant_io = "none"
            execute_requires_confirm_token = "REMEDIATE-SPO-FIELD-IMAGES"
        }
        actions = $actionPlans
    }

    $summary | ConvertTo-Json -Depth 8
}
