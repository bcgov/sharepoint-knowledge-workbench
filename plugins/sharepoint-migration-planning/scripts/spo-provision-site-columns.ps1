<#
.SYNOPSIS
Real PnP executor for site-column provisioning -- creates fields from a plan
JSON matching sharepoint-provisioning's field_provisioning.py plan shape
(a caller-declared FieldDef's planned FieldAction, action in
"create"|"exists"|"repair").

.DESCRIPTION
field_provisioning.py's plan_field_action is pure planning -- it builds raw
Field XML for the three types a typed cmdlet API cannot express (Calculated,
Lookup/LookupMulti, User/UserMulti) but performs no write of any kind. This
script is the real tenant-facing counterpart: it consumes a plan already
built by the Python module and submits each planned action via PnP.

Division of labor (same seam as spo-remediate-document-content-links.ps1's
"remediated_content" pattern): Python builds the XML string via
build_calculated_field_xml/build_lookup_field_xml/build_user_field_xml;
this script never constructs or edits Field XML itself, it only submits
whatever XML the plan already carries via Add-PnPFieldFromXml. Typed fields
(Text, Note, DateTime, Boolean, Number, Integer, Currency, URL, Choice,
MultiChoice) carry no `xml` and are created via Add-PnPField instead.

Plan JSON shape (matches FieldAction.to_dict() field names exactly, plus a
top-level wrapper this script's own contract adds -- FieldAction itself has
no site/list/type/choices/required data, only internal_name/action/reason/
xml, so this script's plan JSON augments each action with the caller's own
FieldDef data needed to actually submit a typed Add-PnPField call):

    {
      "confirmation_token": "APPLY-3-abcdef0123456789",
      "actions": [
        {
          "internal_name": "Department",
          "action": "create",
          "reason": "declared but not present (type 'Text')",
          "xml": null,
          "type": "Text",
          "display_name": "Department",
          "required": false,
          "choices": []
        },
        {
          "internal_name": "ManagerLookup",
          "action": "create",
          "reason": "declared but not present (type 'Lookup')",
          "xml": "<Field Type='Lookup' ... />",
          "type": "Lookup"
        }
      ]
    }

Design seam, documented honestly rather than assumed: FieldAction.to_dict()
(field_provisioning.py) has no `type`/`display_name`/`required`/`choices`
keys -- only `internal_name`/`action`/`reason`/`xml`. A typed (non-raw-XML)
"create" action cannot be replayed against Add-PnPField from FieldAction
alone; the caller producing this plan JSON must augment each action dict
with the originating FieldDef's `type`/`display_name`/`required`/`choices`
fields (mirroring how FieldDef.to_dict() already carries them) before
handing it to this script. Only `action == "create"` items are ever
submitted; "exists" and "repair" actions are reported but not acted on --
`field_needs_type_repair` detection has no destructive remove/recreate
counterpart on the Python side, so this script never removes a live field
either (that would be new, undesigned write behaviour, not a port of an
existing plan).

Start/End platform-bug guard: field_provisioning.py itself has NO knowledge
of the Start/End-must-never-be-a-site-column rule -- it is purely caller
responsibility on the Python side (there is no filter in
filter_deployable_fields or plan_field_action that excludes Start/End).
This script therefore enforces the rule itself, structurally: any plan
action whose `internal_name` is exactly "Start" or "End" is refused outright
(script throws) rather than silently created as a site column -- the same
real SPO platform bug calendar_provisioning.py's module docstring documents
and wave0a-site-columns.ps1 (source repo) guards with a hardcoded skip list.

By default performs no SharePoint tenant I/O; -Execute plus -ConfirmToken
PROVISION-SPO-SITE-COLUMNS runs the real writes.

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
Runs the real Add-PnPField/Add-PnPFieldFromXml calls. Omit this to print a
per-field action plan only -- no tenant I/O.

.PARAMETER ConfirmToken
Required with -Execute. Must be PROVISION-SPO-SITE-COLUMNS.

.EXAMPLE
.\spo-provision-site-columns.ps1 -PlanPath plan.json -SiteUrl "https://tenant.sharepoint.com/sites/Test" -Execute -ConfirmToken PROVISION-SPO-SITE-COLUMNS
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

if (-not $plan.actions) {
    throw "Plan at '$PlanPath' has no actions -- nothing to provision."
}

# Never a caller option: Start/End must never be a site column, unconditionally.
$blockedNames = @("Start", "End")
foreach ($action in $plan.actions) {
    if ($action.internal_name -in $blockedNames) {
        throw "REFUSED: '$($action.internal_name)' must never be provisioned as a site column -- " +
            "this is the confirmed SPO calendar-view platform bug (see calendar_provisioning.py's " +
            "module docstring). Declare it as a list-local field on the target calendar list instead " +
            "(see spo-provision-calendar.ps1)."
    }
}

$createActions = @($plan.actions | Where-Object { $_.action -eq "create" })
$skippedActions = @($plan.actions | Where-Object { $_.action -ne "create" })

if ($createActions.Count -eq 0) {
    $emptyResult = [ordered]@{
        outcome  = "EMPTY"
        dry_run  = -not $Execute
        created  = @()
        skipped  = @($skippedActions | ForEach-Object { [ordered]@{ internal_name = $_.internal_name; action = $_.action; reason = $_.reason } })
        failed   = @()
    }
    $emptyJson = $emptyResult | ConvertTo-Json -Depth 8
    $emptyJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $emptyJson -Encoding UTF8 }
    return
}

if ($Execute) {
    if ($ConfirmToken -ne "PROVISION-SPO-SITE-COLUMNS") {
        throw "-Execute requires -ConfirmToken PROVISION-SPO-SITE-COLUMNS."
    }
    if (-not $SiteUrl -or -not $ClientId -or -not $TenantId) {
        throw "SiteUrl/ClientId/TenantId not resolved. Provide -SiteUrl/-ClientId/-TenantId or a valid -ConfigPath."
    }
    if (-not (Get-Command Add-PnPField -ErrorAction SilentlyContinue) -or
        -not (Get-Command Add-PnPFieldFromXml -ErrorAction SilentlyContinue)) {
        throw "PnP.PowerShell with Add-PnPField/Add-PnPFieldFromXml is required. Install/import PnP.PowerShell before executing."
    }

    $connectParameters = @{
        Url         = $SiteUrl
        ClientId    = $ClientId
        Tenant      = $TenantId
        Interactive = $true
    }
    if ($TenantAdminUrl) { $connectParameters["TenantAdminUrl"] = $TenantAdminUrl }
    Connect-PnPOnline @connectParameters

    $created = @()
    $failed = @()

    foreach ($action in $createActions) {
        try {
            if ($action.xml) {
                Add-PnPFieldFromXml -FieldXml $action.xml -ErrorAction Stop | Out-Null
            }
            else {
                $addParameters = @{
                    Type         = $action.type
                    InternalName = $action.internal_name
                    DisplayName  = if ($action.display_name) { $action.display_name } else { $action.internal_name }
                    Required     = [bool]$action.required
                    Group        = "Custom Columns"
                    ErrorAction  = "Stop"
                }
                if ($action.choices -and $action.choices.Count -gt 0) {
                    $addParameters["Choices"] = $action.choices
                }
                Add-PnPField @addParameters | Out-Null
            }
            $created += [ordered]@{ internal_name = $action.internal_name; action = $action.action }
        }
        catch {
            $failed += [ordered]@{ internal_name = $action.internal_name; error = $_.Exception.Message }
        }
    }

    if ($created.Count -eq 0 -and $failed.Count -gt 0) {
        $outcome = "FAILED"
    }
    elseif ($failed.Count -gt 0) {
        $outcome = "PARTIAL"
    }
    else {
        $outcome = "OBSERVED"
    }

    $result = [ordered]@{
        outcome  = $outcome
        dry_run  = $false
        created  = $created
        skipped  = @($skippedActions | ForEach-Object { [ordered]@{ internal_name = $_.internal_name; action = $_.action; reason = $_.reason } })
        failed   = $failed
    }

    $resultJson = $result | ConvertTo-Json -Depth 8
    $resultJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $resultJson -Encoding UTF8 }
}
else {
    $actionPlans = foreach ($action in $createActions) {
        [ordered]@{
            internal_name = $action.internal_name
            action        = if ($action.xml) { "Add-PnPFieldFromXml -FieldXml <raw XML from plan>" } else { "Add-PnPField -Type $($action.type) -InternalName `"$($action.internal_name)`" -DisplayName `"$($action.display_name)`" -Required:$([bool]$action.required)" }
        }
    }

    $summary = [ordered]@{
        operation = "provision-spo-site-columns"
        confirmation_token = $plan.confirmation_token
        create_count = $createActions.Count
        skipped_count = $skippedActions.Count
        site_url = $SiteUrl
        safety = [ordered]@{
            tenant_io = "none"
            execute_requires_confirm_token = "PROVISION-SPO-SITE-COLUMNS"
            start_end_guard = "Start/End internal names refused unconditionally -- never provisioned as site columns"
        }
        actions = $actionPlans
        skipped = @($skippedActions | ForEach-Object { [ordered]@{ internal_name = $_.internal_name; action = $_.action; reason = $_.reason } })
    }

    $summaryJson = $summary | ConvertTo-Json -Depth 8
    $summaryJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $summaryJson -Encoding UTF8 }
}
