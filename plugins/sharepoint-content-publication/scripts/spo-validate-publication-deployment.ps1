<#
.SYNOPSIS
Read-only post-deployment validation: confirms a PublishPlan's targets
actually exist on the live tenant, matching this plugin's honestly-recorded
"post-deployment validation not yet built" gap.

.DESCRIPTION
Reads a PublishPlan JSON file (document_id, actions[]: source_path,
target_library, target_folder, target_filename) and, for each action,
confirms the target page (Get-PnPPage, for a SitePages target) or file
(Get-PnPFile, for a document-library target) actually exists on the tenant.
Always real tenant I/O when run (read-only, no confirmation token required
-- there is nothing to confirm, this script never writes).

.PARAMETER PlanPath
Path to a PublishPlan JSON file matching PublishPlan.to_dict()'s shape.

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

.EXAMPLE
.\spo-validate-publication-deployment.ps1 -PlanPath plan.json -SiteUrl "https://tenant.sharepoint.com/sites/Test"
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PlanPath,

    [string]$SiteUrl,

    [string]$ConfigPath = (Join-Path $PSScriptRoot "..\..\..\config.psd1"),

    [string]$ClientId,

    [string]$TenantId,

    [string]$TenantAdminUrl
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "Get-WorkbenchConnectionConfig.ps1")

function Get-PublishTargetKind {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string]$TargetLibrary)
    if ($TargetLibrary -eq "SitePages") { return "page" }
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
    throw "Plan at '$PlanPath' has no actions -- nothing to validate."
}

if (-not (Get-Command Get-PnPPage -ErrorAction SilentlyContinue) -or -not (Get-Command Get-PnPFile -ErrorAction SilentlyContinue)) {
    throw "PnP.PowerShell with Get-PnPPage/Get-PnPFile is required. Install/import PnP.PowerShell before running this validator."
}

$connectParameters = @{
    Url         = $SiteUrl
    ClientId    = $ClientId
    Tenant      = $TenantId
    Interactive = $true
}
if ($TenantAdminUrl) { $connectParameters["TenantAdminUrl"] = $TenantAdminUrl }
Connect-PnPOnline @connectParameters

$findings = foreach ($action in $plan.actions) {
    $kind = Get-PublishTargetKind -TargetLibrary $action.target_library

    if ($kind -eq "page") {
        $pageName = [System.IO.Path]::GetFileNameWithoutExtension($action.target_filename)
        $found = Get-PnPPage -Identity $pageName -ErrorAction SilentlyContinue
        [pscustomobject]@{
            target_filename = $action.target_filename
            kind            = $kind
            outcome         = $(if ($found) { "OBSERVED" } else { "EMPTY" })
            detail          = $(if ($found) { "Page '$pageName' present." } else { "Page '$pageName' not found on tenant." })
        }
    }
    else {
        $targetFolder = "$($action.target_library)/$($action.target_folder)".TrimEnd("/").Replace("//", "/")
        $targetUrl = "$targetFolder/$($action.target_filename)"
        $found = Get-PnPFile -Url $targetUrl -ErrorAction SilentlyContinue
        [pscustomobject]@{
            target_filename = $action.target_filename
            kind            = $kind
            outcome         = $(if ($found) { "OBSERVED" } else { "EMPTY" })
            detail          = $(if ($found) { "File '$targetUrl' present." } else { "File '$targetUrl' not found on tenant." })
        }
    }
}

$missingCount = @($findings | Where-Object { $_.outcome -eq "EMPTY" }).Count

[ordered]@{
    operation      = "validate-publication-deployment"
    document_id    = $plan.document_id
    site_url       = $SiteUrl
    action_count   = $plan.actions.Count
    missing_count  = $missingCount
    status         = $(if ($missingCount -eq 0) { "PASS" } else { "FAIL" })
    findings       = $findings
} | ConvertTo-Json -Depth 8
