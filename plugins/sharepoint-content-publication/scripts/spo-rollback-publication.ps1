<#
.SYNOPSIS
Executes a RollbackPlan -- removes the SPO pages or library files a prior
publish action created.

.DESCRIPTION
Reads a RollbackPlan JSON file (document_id, actions[]: target_url, reason)
and, for each action, removes the target: Remove-PnPPage for a SitePages
target, Remove-PnPFile for a document-library target (distinguished by
whether target_url's first path segment is "SitePages"). By default
performs no SharePoint tenant I/O; -Execute plus -ConfirmToken
ROLLBACK-SPO-PLAN runs the real deletions.

.PARAMETER PlanPath
Path to a RollbackPlan JSON file matching RollbackPlan.to_dict()'s shape
(as built by sharepoint_publish_plan.py's build_rollback_plan).

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
Runs the real Remove-PnPPage / Remove-PnPFile calls. Omit this to print
the per-action plan only.

.PARAMETER ConfirmToken
Required with -Execute. Must be ROLLBACK-SPO-PLAN.

.EXAMPLE
.\spo-rollback-publication.ps1 -PlanPath rollback.json -SiteUrl "https://tenant.sharepoint.com/sites/Test" -Execute -ConfirmToken ROLLBACK-SPO-PLAN
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PlanPath,

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

function Get-RollbackTargetKind {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string]$TargetUrl)
    $firstSegment = $TargetUrl.TrimStart("/").Split("/")[0]
    if ($firstSegment -eq "SitePages") { return "page" }
    return "file"
}

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
if (-not $plan.actions -or $plan.actions.Count -eq 0) {
    throw "Plan at '$PlanPath' has no actions -- nothing to roll back."
}

if ($Execute) {
    if ($ConfirmToken -ne "ROLLBACK-SPO-PLAN") {
        throw "-Execute requires -ConfirmToken ROLLBACK-SPO-PLAN."
    }
    if (-not (Get-Command Remove-PnPPage -ErrorAction SilentlyContinue) -or -not (Get-Command Remove-PnPFile -ErrorAction SilentlyContinue)) {
        throw "PnP.PowerShell with Remove-PnPPage/Remove-PnPFile is required. Install/import PnP.PowerShell before executing."
    }

    $connectParameters = @{
        Url         = $SiteUrl
        ClientId    = $ClientId
        Tenant      = $TenantId
        Interactive = $true
    }
    if ($TenantAdminUrl) { $connectParameters["TenantAdminUrl"] = $TenantAdminUrl }
    Connect-PnPOnline @connectParameters

    $results = foreach ($action in $plan.actions) {
        $kind = Get-RollbackTargetKind -TargetUrl $action.target_url

        if ($kind -eq "page") {
            $pageName = [System.IO.Path]::GetFileNameWithoutExtension(($action.target_url -split "/")[-1])
            $existingPage = Get-PnPPage -Identity $pageName -ErrorAction SilentlyContinue
            if (-not $existingPage) {
                [pscustomobject]@{
                    target_url = $action.target_url
                    kind       = $kind
                    outcome    = "EMPTY"
                    detail     = "Page '$pageName' not found -- nothing to remove."
                }
                continue
            }
            Remove-PnPPage -Identity $pageName -Force
            $stillThere = Get-PnPPage -Identity $pageName -ErrorAction SilentlyContinue
            if ($stillThere) {
                throw "Removal verification failed: page '$pageName' still present after Remove-PnPPage."
            }
        }
        else {
            $existingFile = Get-PnPFile -Url $action.target_url -ErrorAction SilentlyContinue
            if (-not $existingFile) {
                [pscustomobject]@{
                    target_url = $action.target_url
                    kind       = $kind
                    outcome    = "EMPTY"
                    detail     = "File '$($action.target_url)' not found -- nothing to remove."
                }
                continue
            }
            Remove-PnPFile -ServerRelativeUrl $action.target_url -Force
            $stillThere = Get-PnPFile -Url $action.target_url -ErrorAction SilentlyContinue
            if ($stillThere) {
                throw "Removal verification failed: file '$($action.target_url)' still present after Remove-PnPFile."
            }
        }

        [pscustomobject]@{
            target_url = $action.target_url
            kind       = $kind
            outcome    = "OBSERVED"
            detail     = "Removed and verified absent."
        }
    }

    $results | ConvertTo-Json -Depth 8
}
else {
    $actionPlans = foreach ($action in $plan.actions) {
        $kind = Get-RollbackTargetKind -TargetUrl $action.target_url
        [ordered]@{
            target_url = $action.target_url
            reason = $action.reason
            kind = $kind
            remove = $(if ($kind -eq "page") {
                $pageName = [System.IO.Path]::GetFileNameWithoutExtension(($action.target_url -split "/")[-1])
                "Remove-PnPPage -Identity `"$pageName`" -Force"
            } else {
                "Remove-PnPFile -ServerRelativeUrl `"$($action.target_url)`" -Force"
            })
        }
    }

    $summary = [ordered]@{
        operation = "rollback-spo-plan"
        document_id = $plan.document_id
        action_count = $plan.actions.Count
        site_url = $SiteUrl
        safety = [ordered]@{
            tenant_io = "none"
            execute_requires_confirm_token = "ROLLBACK-SPO-PLAN"
        }
        actions = $actionPlans
    }

    $summary | ConvertTo-Json -Depth 8
}
