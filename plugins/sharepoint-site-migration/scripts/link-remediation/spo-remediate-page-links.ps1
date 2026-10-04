<#
.SYNOPSIS
Rewrites legacy URLs embedded in modern SharePoint page body content
(CanvasContent1) using a RemediationPlan produced by link_remediation.py.

.DESCRIPTION
Reads a RemediationPlan JSON file matching RemediationPlan.to_dict()'s shape
(documents[].source, documents[].changed, documents[].changes[],
confirmation_token). For each changed document, resolves the item by its
server-relative path (the plan's `source` field) in -TargetLibrary via
Get-PnPListItem, then rewrites -TargetField (default CanvasContent1) with the
document's already-remediated content via Set-PnPListItem.

The Python planning module (link_remediation.py) only ever computes the
*text* of the remediated content -- it does not ship the new content back out
through RemediationPlan.to_dict() (that method reports only
source/changed/changes, to keep the plan JSON small and diffable). This
script therefore expects the plan JSON to carry the remediated body text
directly on each changed document as `remediated_content`, e.g. produced by:

    plan = plan_remediation(documents, ruleset)
    payload = plan.to_dict()
    for doc, planned in zip(payload["documents"], plan.documents):
        if planned.is_changed:
            doc["remediated_content"] = planned.remediated_content
    json.dump(payload, open("plan.json", "w"))

By default performs no SharePoint tenant I/O; -Execute plus -ConfirmToken
REMEDIATE-SPO-LINKS runs the real writes.

.PARAMETER PlanPath
Path to a RemediationPlan JSON file (see .DESCRIPTION for the required
`remediated_content` augmentation on each changed document).

.PARAMETER TargetLibrary
The document/page library the plan's `source` paths live in, e.g.
"Site Pages".

.PARAMETER TargetField
The list-item field to overwrite with the remediated content. Defaults to
CanvasContent1, the modern-page body field.

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
per-document plan only.

.PARAMETER ConfirmToken
Required with -Execute. Must be REMEDIATE-SPO-LINKS.

.EXAMPLE
.\spo-remediate-page-links.ps1 -PlanPath plan.json -TargetLibrary "Site Pages" -SiteUrl "https://tenant.sharepoint.com/sites/Test" -Execute -ConfirmToken REMEDIATE-SPO-LINKS
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PlanPath,

    [Parameter(Mandatory = $true)]
    [string]$TargetLibrary,

    [string]$TargetField = "CanvasContent1",

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
if (-not $plan.documents) {
    throw "Plan at '$PlanPath' has no documents -- nothing to remediate."
}

$changedDocuments = @($plan.documents | Where-Object { $_.changed })
if ($changedDocuments.Count -eq 0) {
    Write-Host "No changed documents in plan -- nothing to remediate."
    return
}

if ($Execute) {
    if ($ConfirmToken -ne "REMEDIATE-SPO-LINKS") {
        throw "-Execute requires -ConfirmToken REMEDIATE-SPO-LINKS."
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

    $results = foreach ($document in $changedDocuments) {
        if (-not (Get-Member -InputObject $document -Name "remediated_content") -or [string]::IsNullOrEmpty($document.remediated_content)) {
            throw "Document '$($document.source)' is marked changed but has no 'remediated_content' -- see .DESCRIPTION for the required plan augmentation."
        }

        try {
            $escapedPath = $document.source -replace "'", "''"
            $item = Get-PnPListItem -List $TargetLibrary -Query "<View><Query><Where><Eq><FieldRef Name='FileRef'/><Value Type='Text'>$escapedPath</Value></Eq></Where></Query></View>" -PageSize 1
            if (-not $item) {
                throw "No item found in '$TargetLibrary' with FileRef '$($document.source)'."
            }

            Set-PnPListItem -List $TargetLibrary -Identity $item.Id -Values @{ $TargetField = $document.remediated_content } | Out-Null

            [pscustomobject]@{
                source  = $document.source
                item_id = $item.Id
                success = $true
            }
        }
        catch {
            [pscustomobject]@{
                source  = $document.source
                success = $false
                error   = $_.Exception.Message
            }
        }
    }

    $results | ConvertTo-Json -Depth 8
}
else {
    $actionPlans = foreach ($document in $changedDocuments) {
        [ordered]@{
            source        = $document.source
            change_count  = @($document.changes).Count
            find_item     = "Get-PnPListItem -List `"$TargetLibrary`" -Query `"<View><Query><Where><Eq><FieldRef Name='FileRef'/><Value Type='Text'>$($document.source)</Value></Eq></Where></Query></View>`""
            update_field  = "Set-PnPListItem -List `"$TargetLibrary`" -Identity <item.Id> -Values @{`"$TargetField`" = <remediated_content>}"
        }
    }

    $summary = [ordered]@{
        operation = "remediate-spo-links"
        target_library = $TargetLibrary
        target_field = $TargetField
        confirmation_token = $plan.confirmation_token
        changed_document_count = $changedDocuments.Count
        site_url = $SiteUrl
        safety = [ordered]@{
            tenant_io = "none"
            execute_requires_confirm_token = "REMEDIATE-SPO-LINKS"
        }
        actions = $actionPlans
    }

    $summary | ConvertTo-Json -Depth 8
}
