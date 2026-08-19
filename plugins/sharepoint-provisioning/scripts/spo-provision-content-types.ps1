<#
.SYNOPSIS
Real PnP executor for content-type provisioning -- creates content types and
reconciles field links from a plan JSON matching sharepoint-provisioning's
content_type_provisioning.py plan shape (a list of ContentTypeAction steps).

.DESCRIPTION
content_type_provisioning.py's plan_content_type/plan_add_content_type_to_list
are pure planning -- they reconcile a caller-declared ContentTypeDef against
a caller-supplied ContentTypeState observation and produce an ordered list of
ContentTypeAction steps (create_content_type | link_field | hide_field |
show_field | unlink_field | attach_content_type), each carrying
`already_correct` to distinguish "nothing to do" from a real change. This
script is the real tenant-facing counterpart: it applies exactly the steps
the plan lists, in the order the plan lists them, and infers nothing locally
-- "drift is surfaced, not silently fixed" (README) means this script never
decides on its own that a field should be hidden/shown/unlinked; it only
submits whatever step the plan already computed.

Plan JSON shape (matches ContentTypeAction.to_dict() field names exactly,
plus the top-level content-type/parent/list context this script's own
contract needs since ContentTypeAction alone carries no target-object
identity beyond its human-readable `detail` string):

    {
      "confirmation_token": "APPLY-4-abcdef0123456789",
      "content_type_name": "Custom Document",
      "parent_content_type": "Document",
      "list_title": null,
      "steps": [
        { "step": "create_content_type", "detail": "create 'Custom Document' (parent 'Document')", "already_correct": false },
        { "step": "link_field", "detail": "link 'Department' to 'Custom Document'", "field_name": "Department", "already_correct": false },
        { "step": "hide_field", "detail": "set hidden=False for 'Department' on 'Custom Document' (new link)", "field_name": "Department", "hidden": false, "already_correct": false },
        { "step": "unlink_field", "detail": "unlink 'Legacy' from 'Custom Document' (no longer declared in schema)", "field_name": "Legacy", "already_correct": false }
      ]
    }

Design seam, documented honestly rather than assumed: ContentTypeAction.to_dict()
carries only `step`/`detail`/`already_correct` -- no `field_name`/`hidden`/
target content-type name of its own. Replaying a `link_field`/`hide_field`/
`show_field`/`unlink_field` step against real PnP cmdlets needs the field's
internal name and (for hide/show) the boolean hidden value, neither of
which the Python dataclass serializes. The caller producing this plan JSON
must augment each step dict with `field_name` (and `hidden` for hide_field/
show_field steps), mirroring how spo-migrate-list-items.ps1's plan augments
`MigrationItem` with `dest_id` and spo-remediate-document-content-links.ps1's
plan augments `RemediationPlan` with `remediated_content`. Steps already
marked `already_correct: true` are reported but never submitted -- they are
"nothing to do", not a real write.

Cmdlet sequence, evidenced against the source repo's wave0b-content-types.ps1:
Add-PnPContentType -Name <name> -ParentContentType <parent CT object> for
create_content_type; Add-PnPFieldToContentType -Field <name> -ContentType
<ct name> for link_field; for hide_field/show_field this script uses the CSOM
FieldLinks/Hidden path (Add-PnPFieldToContentType has no -Hidden switch, and
the source repo's own Hide-FieldOnContentTypeSafe helper was not found in the
audited scripts -- see .DESCRIPTION "Design seam" note below) via
Get-PnPContentType + the FieldLinks collection; unlink_field uses
Remove-PnPFieldFromContentType -Field <name> -ContentType <ct name>.
attach_content_type uses Add-PnPContentTypeToList -List <list> -ContentType
<ct name>.

By default performs no SharePoint tenant I/O; -Execute plus -ConfirmToken
PROVISION-SPO-CONTENT-TYPES runs the real writes.

.PARAMETER PlanPath
Path to the plan JSON file (see .DESCRIPTION for the required shape).

.PARAMETER OutputPath
If set, writes the result JSON to this path in addition to stdout.

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
Runs the real Add-PnPContentType/Add-PnPFieldToContentType/etc. calls. Omit
this to print a per-step action plan only -- no tenant I/O.

.PARAMETER ConfirmToken
Required with -Execute. Must be PROVISION-SPO-CONTENT-TYPES.

.EXAMPLE
.\spo-provision-content-types.ps1 -PlanPath plan.json -SiteUrl "https://tenant.sharepoint.com/sites/Test" -Execute -ConfirmToken PROVISION-SPO-CONTENT-TYPES
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PlanPath,

    [string]$OutputPath,

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

if (-not (Test-Path -LiteralPath $PlanPath)) {
    throw "PlanPath '$PlanPath' does not exist."
}
$plan = Get-Content -LiteralPath $PlanPath -Raw | ConvertFrom-Json

if (-not $plan.steps) {
    throw "Plan at '$PlanPath' has no steps -- nothing to provision."
}

$ctName = $plan.content_type_name

$actionableSteps = @($plan.steps | Where-Object { -not $_.already_correct })
$alreadyCorrectSteps = @($plan.steps | Where-Object { $_.already_correct })

if ($actionableSteps.Count -eq 0) {
    $emptyResult = [ordered]@{
        outcome         = "EMPTY"
        dry_run         = -not $Execute
        executed        = @()
        already_correct = @($alreadyCorrectSteps | ForEach-Object { [ordered]@{ step = $_.step; detail = $_.detail } })
        failed          = @()
    }
    $emptyJson = $emptyResult | ConvertTo-Json -Depth 8
    $emptyJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $emptyJson -Encoding UTF8 }
    return
}

if ($Execute) {
    if ($ConfirmToken -ne "PROVISION-SPO-CONTENT-TYPES") {
        throw "-Execute requires -ConfirmToken PROVISION-SPO-CONTENT-TYPES."
    }
    if (-not $SiteUrl -or -not $ClientId -or -not $TenantId) {
        throw "SiteUrl/ClientId/TenantId not resolved. Provide -SiteUrl/-ClientId/-TenantId or a valid -ConfigPath."
    }
    if (-not (Get-Command Add-PnPContentType -ErrorAction SilentlyContinue) -or
        -not (Get-Command Add-PnPFieldToContentType -ErrorAction SilentlyContinue)) {
        throw "PnP.PowerShell with Add-PnPContentType/Add-PnPFieldToContentType is required. Install/import PnP.PowerShell before executing."
    }

    $connectParameters = @{
        Url         = $SiteUrl
        ClientId    = $ClientId
        Tenant      = $TenantId
        Interactive = $true
    }
    if ($TenantAdminUrl) { $connectParameters["TenantAdminUrl"] = $TenantAdminUrl }
    Connect-PnPOnline @connectParameters

    $executed = @()
    $failed = @()

    foreach ($step in $actionableSteps) {
        try {
            switch ($step.step) {
                "create_content_type" {
                    $parentCt = Get-PnPContentType -Identity $plan.parent_content_type -ErrorAction Stop
                    Add-PnPContentType -Name $ctName -ParentContentType $parentCt -Group "Custom Content Types" -ErrorAction Stop | Out-Null
                }
                "link_field" {
                    Add-PnPFieldToContentType -Field $step.field_name -ContentType $ctName -ErrorAction Stop | Out-Null
                }
                "hide_field" {
                    $ct = Get-PnPContentType -Identity $ctName -ErrorAction Stop
                    $fieldLink = $ct.FieldLinks | Where-Object { $_.Name -eq $step.field_name }
                    if (-not $fieldLink) { throw "field link '$($step.field_name)' not found on content type '$ctName'" }
                    $fieldLink.Hidden = $true
                    $ct.Update($false)
                    Invoke-PnPQuery
                }
                "show_field" {
                    $ct = Get-PnPContentType -Identity $ctName -ErrorAction Stop
                    $fieldLink = $ct.FieldLinks | Where-Object { $_.Name -eq $step.field_name }
                    if (-not $fieldLink) { throw "field link '$($step.field_name)' not found on content type '$ctName'" }
                    $fieldLink.Hidden = $false
                    $ct.Update($false)
                    Invoke-PnPQuery
                }
                "unlink_field" {
                    Remove-PnPFieldFromContentType -Field $step.field_name -ContentType $ctName -ErrorAction Stop | Out-Null
                }
                "attach_content_type" {
                    if (-not $plan.list_title) { throw "attach_content_type step requires plan.list_title" }
                    Add-PnPContentTypeToList -List $plan.list_title -ContentType $ctName -ErrorAction Stop | Out-Null
                }
                default {
                    throw "unrecognised step '$($step.step)'"
                }
            }
            $executed += [ordered]@{ step = $step.step; detail = $step.detail }
        }
        catch {
            $failed += [ordered]@{ step = $step.step; detail = $step.detail; error = $_.Exception.Message }
        }
    }

    if ($executed.Count -eq 0 -and $failed.Count -gt 0) {
        $outcome = "FAILED"
    }
    elseif ($failed.Count -gt 0) {
        $outcome = "PARTIAL"
    }
    else {
        $outcome = "OBSERVED"
    }

    $result = [ordered]@{
        outcome         = $outcome
        dry_run         = $false
        executed        = $executed
        already_correct = @($alreadyCorrectSteps | ForEach-Object { [ordered]@{ step = $_.step; detail = $_.detail } })
        failed          = $failed
    }

    $resultJson = $result | ConvertTo-Json -Depth 8
    $resultJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $resultJson -Encoding UTF8 }
}
else {
    $actionPlans = foreach ($step in $actionableSteps) {
        $cmdlet = switch ($step.step) {
            "create_content_type" { "Add-PnPContentType -Name `"$ctName`" -ParentContentType `"$($plan.parent_content_type)`"" }
            "link_field" { "Add-PnPFieldToContentType -Field `"$($step.field_name)`" -ContentType `"$ctName`"" }
            "hide_field" { "Get-PnPContentType/FieldLinks[`"$($step.field_name)`"].Hidden = `$true; Update" }
            "show_field" { "Get-PnPContentType/FieldLinks[`"$($step.field_name)`"].Hidden = `$false; Update" }
            "unlink_field" { "Remove-PnPFieldFromContentType -Field `"$($step.field_name)`" -ContentType `"$ctName`"" }
            "attach_content_type" { "Add-PnPContentTypeToList -List `"$($plan.list_title)`" -ContentType `"$ctName`"" }
            default { "UNRECOGNISED STEP: $($step.step)" }
        }
        [ordered]@{ step = $step.step; detail = $step.detail; action = $cmdlet }
    }

    $summary = [ordered]@{
        operation = "provision-spo-content-types"
        confirmation_token = $plan.confirmation_token
        content_type_name = $ctName
        actionable_count = $actionableSteps.Count
        already_correct_count = $alreadyCorrectSteps.Count
        site_url = $SiteUrl
        safety = [ordered]@{
            tenant_io = "none"
            execute_requires_confirm_token = "PROVISION-SPO-CONTENT-TYPES"
        }
        actions = $actionPlans
        already_correct = @($alreadyCorrectSteps | ForEach-Object { [ordered]@{ step = $_.step; detail = $_.detail } })
    }

    $summaryJson = $summary | ConvertTo-Json -Depth 8
    $summaryJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $summaryJson -Encoding UTF8 }
}
