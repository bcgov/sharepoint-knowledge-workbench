<#
.SYNOPSIS
Real PnP executor for provisioning Managed Metadata Term Groups, Term Sets, and Terms.

.DESCRIPTION
Same dry-run-by-default / -Execute + -ConfirmToken / Get-WorkbenchConnectionConfig.ps1
pattern as every other spo-provision-*.ps1 script in this plugin -- see that
script's own docstring for the full safety-gate rationale, not repeated here.

Plan JSON shape:

    {
      "confirmation_token": "UPDATE-2-abcdef0123456789",
      "actions": [
        {
          "internal_name": "ClientMatterNumber",
          "display_name": "Client Matter Number",
          "description": "Updated per 2026-08-18 schema review",
          "required": false,
          "choices": []
        }
      ]
    }

.PARAMETER PlanPath
Path to the plan JSON described above.

.PARAMETER Execute
Runs the real Set-PnPField call. Omit this to print a dry-run action summary
and take no tenant action.

.PARAMETER ConfirmToken
Must equal PROVISION-SPO-TERM-SET when -Execute is passed. Refused otherwise.

.PARAMETER SiteUrl
.PARAMETER ClientId
.PARAMETER TenantId
.PARAMETER TenantAdminUrl
.PARAMETER ConfigPath
Connection parameters -- resolved via Get-WorkbenchConnectionConfig.ps1 when
-ConfigPath is given and the explicit parameters are omitted.

.PARAMETER OutputPath
Optional path to also write the JSON result to.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PlanPath,

    [switch]$Execute,

    [string]$ConfirmToken,

    [string]$SiteUrl,
    [string]$ClientId,
    [string]$TenantId,
    [string]$TenantAdminUrl,
    [string]$ConfigPath = (Join-Path $PSScriptRoot "..\..\..\config.psd1"),

    [string]$OutputPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "Get-WorkbenchConnectionConfig.ps1")

$connectionConfig = Get-WorkbenchConnectionConfig -Path $ConfigPath
if (-not $SiteUrl) { $SiteUrl = $connectionConfig.SiteUrl }
if (-not $ClientId) { $ClientId = $connectionConfig.ClientId }
if (-not $TenantId) { $TenantId = $connectionConfig.TenantId }
if (-not $TenantAdminUrl) { $TenantAdminUrl = $connectionConfig.TenantAdminUrl }

if (-not (Test-Path -LiteralPath $PlanPath)) {
    throw "Plan file not found at '$PlanPath'."
}
$plan = Get-Content -LiteralPath $PlanPath -Raw | ConvertFrom-Json

if (-not $plan.actions -or $plan.actions.Count -eq 0) {
    $emptyResult = [ordered]@{
        outcome = "EMPTY"
        dry_run = -not $Execute
        updated = @()
        skipped = @()
        failed  = @()
    }
    $emptyJson = $emptyResult | ConvertTo-Json -Depth 8
    $emptyJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $emptyJson -Encoding UTF8 }
    return
}

if ($Execute) {
    if ($ConfirmToken -ne "PROVISION-SPO-TERM-SET") {
        throw "-Execute requires -ConfirmToken PROVISION-SPO-TERM-SET."
    }
    if (-not $SiteUrl -or -not $ClientId -or -not $TenantId) {
        throw "SiteUrl/ClientId/TenantId not resolved. Provide -SiteUrl/-ClientId/-TenantId or a valid -ConfigPath."
    }
    if (-not (Get-Command Set-PnPField -ErrorAction SilentlyContinue)) {
        throw "PnP.PowerShell with Set-PnPField is required. Install/import PnP.PowerShell before executing."
    }

    $connectParameters = @{
        Url         = $SiteUrl
        ClientId    = $ClientId
        Tenant      = $TenantId
        Interactive = $true
    }
    if ($TenantAdminUrl) { $connectParameters["TenantAdminUrl"] = $TenantAdminUrl }
    Connect-PnPOnline @connectParameters

    $updated = @()
    $failed = @()

    foreach ($action in $plan.actions) {
        try {
            New-PnPTermGroup -Name $action.group_name -ErrorAction SilentlyContinue | Out-Null
            New-PnPTermSet -GroupName $action.group_name -Name $action.term_set_name -ErrorAction SilentlyContinue | Out-Null
            if ($action.terms) { foreach ($t in $action.terms) { New-PnPTerm -TermSet $action.term_set_name -TermGroup $action.group_name -Name $t -ErrorAction SilentlyContinue | Out-Null } }
            $updated += [ordered]@{ term_set_name = $action.term_set_name }
        }
        catch {
            $failed += [ordered]@{ term_set_name = $action.term_set_name; group_name = $action.group_name; error = $_.Exception.Message }
        }
    }

    $outcome = if ($updated.Count -eq 0 -and $failed.Count -gt 0) { "FAILED" }
        elseif ($failed.Count -gt 0) { "PARTIAL" }
        else { "OBSERVED" }

    $result = [ordered]@{
        outcome = $outcome
        dry_run = $false
        updated = $updated
        skipped = @()
        failed  = $failed
    }
    $resultJson = $result | ConvertTo-Json -Depth 8
    $resultJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $resultJson -Encoding UTF8 }
}
else {
    $actionPlans = foreach ($action in $plan.actions) {
        $groupName = if ($action.PSObject.Properties.Name -contains 'group_name') { $action.group_name } else { $null }
        $termSetName = if ($action.PSObject.Properties.Name -contains 'term_set_name') { $action.term_set_name } else { $null }
        [ordered]@{
            group_name    = $groupName
            term_set_name = $termSetName
            action        = "New-PnPTermSet -GroupName `"$groupName`" -Name `"$termSetName`""
        }
    }
    $summary = [ordered]@{
        operation           = "provision-spo-term-set"
        confirmation_token  = $plan.confirmation_token
        provision_count     = $plan.actions.Count
        site_url            = $SiteUrl
        safety              = [ordered]@{
            tenant_io                      = "none"
            execute_requires_confirm_token = "PROVISION-SPO-TERM-SET"
        }
        planned_actions     = $actionPlans
    }
    $summaryJson = $summary | ConvertTo-Json -Depth 8
    $summaryJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $summaryJson -Encoding UTF8 }
}
