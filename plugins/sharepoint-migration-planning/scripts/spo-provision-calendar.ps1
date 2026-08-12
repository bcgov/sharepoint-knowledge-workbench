<#
.SYNOPSIS
Real PnP executor for modern SPO calendar-list provisioning -- creates the
list, the list-local Start/End DateTime fields, and the modern calendar
view from a plan JSON matching sharepoint-provisioning's
calendar_provisioning.py CalendarProvisioningPlan shape.

.DESCRIPTION
calendar_provisioning.py's plan_calendar_list is pure planning -- it refuses
outright (StartEndScopeViolation) if a caller declares Start/End at
site-column scope, and a valid plan always contains exactly three steps:
list_creation (Generic List template 100, NEVER Calendar template 106),
list_local_fields (Start + End as list-local DateTime fields only), and
view_creation (a modern calendar view via ViewTypeKind=1/
ViewType2="MODERNCALENDAR"). This script is the real tenant-facing
counterpart, submitting exactly those three steps and no others.

Plan JSON shape (matches CalendarProvisioningPlan.to_dict() field names
exactly -- no augmentation needed, every field a real cmdlet sequence
requires is already present):

    {
      "outcome": "OBSERVED",
      "confirmation_token": "APPLY-3-abcdef0123456789",
      "list_creation": { "title": "City Calendar", "template": 100, "description": "" },
      "list_local_fields": [
        { "internal_name": "Start", "field_type": "DateTime" },
        { "internal_name": "End", "field_type": "DateTime" }
      ],
      "view_creation": { "title": "City Calendar", "view_type_kind": 1, "view_type2": "MODERNCALENDAR" }
    }

STRUCTURAL Start/End platform-bug guard (the real, confirmed SPO bug this
whole module exists to prevent -- see calendar_provisioning.py's module
docstring): this script never submits Start/End as site-level fields under
ANY circumstance, even if a malformed/hand-edited plan somehow contained
one. Two independent checks enforce this:

  1. `list_creation.template` MUST be 100 (Generic List). A plan carrying
     `template: 106` (Calendar template) is refused outright -- the
     platform bug's other trigger, per the module docstring ("use the
     Generic List template (100), never the Calendar template (106)").
  2. Every `list_local_fields` entry is submitted via
     `Add-PnPFieldFromXml -List <listTitle> -FieldXml <xml>` -- i.e.
     scoped to the just-created list, structurally incapable of creating a
     site column, unlike a bare `Add-PnPField` without `-List` (which would
     default to the web/site scope and reproduce the exact bug this module
     exists to prevent). This script has no code path that ever calls
     `Add-PnPField`/`Add-PnPFieldFromXml` without `-List` for a
     `list_local_fields` entry -- there is no "site column" branch to fall
     into by mistake.

Cmdlet sequence, evidenced against the source repo's modern-calendar-lib.ps1
(`New-ModernCalendarList`): New-PnPList -Title <title> -Template
GenericList (100); Add-PnPFieldFromXml -List <title> -FieldXml
"<Field Type='DateTime' ... StaticName='Start' Name='Start' />" (and the
same shape for 'End') -- list-scoped, never site-scoped; then
Invoke-PnPSPRestMethod -Method Post -Url
"/_api/web/lists/getByTitle('<title>')/views/add" with a JSON body carrying
ViewTypeKind=1/ViewType2="MODERNCALENDAR"/ViewData mapping Start to the
calendar location slots, followed by Set-PnPView -Identity <viewTitle>
-Values @{DefaultView=$true} to make it the default view.

Design note: the source repo's calendar-provisioning script also creates an
`fAllDayEvent` Boolean field, an extra summary list view, and attaches
project-specific content types -- none of that is represented in
calendar_provisioning.py's CalendarProvisioningPlan (which has exactly
three fields: list_creation, list_local_fields, view_creation), so none of
it is ported here. This script implements exactly the three-step contract
the Python plan carries, nothing more -- a caller wanting content types
attached to the resulting calendar list uses spo-provision-content-types.ps1
separately (its own `attach_content_type` step), not a hidden extra step
bolted onto this script.

By default performs no SharePoint tenant I/O; -Execute plus -ConfirmToken
PROVISION-SPO-CALENDAR runs the real writes.

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
Runs the real New-PnPList/Add-PnPFieldFromXml/Invoke-PnPSPRestMethod calls.
Omit this to print the action plan only -- no tenant I/O.

.PARAMETER ConfirmToken
Required with -Execute. Must be PROVISION-SPO-CALENDAR.

.EXAMPLE
.\spo-provision-calendar.ps1 -PlanPath plan.json -SiteUrl "https://tenant.sharepoint.com/sites/Test" -Execute -ConfirmToken PROVISION-SPO-CALENDAR
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

if (-not $plan.list_creation -or -not $plan.list_local_fields -or -not $plan.view_creation) {
    throw "Plan at '$PlanPath' is missing one of list_creation/list_local_fields/view_creation -- not a valid CalendarProvisioningPlan."
}

# STRUCTURAL guard 1: Generic List template (100) only -- never Calendar
# template (106). This is the other half of the real SPO platform bug
# calendar_provisioning.py exists to prevent.
$template = [int]$plan.list_creation.template
if ($template -ne 100) {
    throw "REFUSED: list_creation.template must be 100 (Generic List), got $template. Template 106 (Calendar) reproduces the confirmed SPO calendar-view platform bug -- see calendar_provisioning.py's module docstring."
}

# STRUCTURAL guard 2: every list-local field must have a non-empty
# internal_name and is only ever submitted list-scoped (-List <title>) --
# there is no code path in this script that submits a list_local_fields
# entry as a site column.
foreach ($localField in $plan.list_local_fields) {
    if (-not $localField.internal_name) {
        throw "REFUSED: a list_local_fields entry has no internal_name -- refusing rather than guessing."
    }
}

$listTitle = $plan.list_creation.title

if ($Execute) {
    if ($ConfirmToken -ne "PROVISION-SPO-CALENDAR") {
        throw "-Execute requires -ConfirmToken PROVISION-SPO-CALENDAR."
    }
    if (-not $SiteUrl -or -not $ClientId -or -not $TenantId) {
        throw "SiteUrl/ClientId/TenantId not resolved. Provide -SiteUrl/-ClientId/-TenantId or a valid -ConfigPath."
    }
    if (-not (Get-Command New-PnPList -ErrorAction SilentlyContinue) -or
        -not (Get-Command Add-PnPFieldFromXml -ErrorAction SilentlyContinue) -or
        -not (Get-Command Invoke-PnPSPRestMethod -ErrorAction SilentlyContinue)) {
        throw "PnP.PowerShell with New-PnPList/Add-PnPFieldFromXml/Invoke-PnPSPRestMethod is required. Install/import PnP.PowerShell before executing."
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

    try {
        New-PnPList -Title $listTitle -Template 100 -ErrorAction Stop | Out-Null
        if ($plan.list_creation.description) {
            Set-PnPList -Identity $listTitle -Description $plan.list_creation.description -ErrorAction Stop | Out-Null
        }
        $executed += [ordered]@{ step = "list_creation"; detail = "created '$listTitle' (template 100)" }
    }
    catch {
        $failed += [ordered]@{ step = "list_creation"; error = $_.Exception.Message }
    }

    if ($failed.Count -eq 0) {
        foreach ($localField in $plan.list_local_fields) {
            try {
                $safeDisplay = $localField.internal_name -replace "&", "&amp;" -replace "'", "&apos;"
                # List-scoped (-List $listTitle) -- structurally cannot become a site column.
                $xml = "<Field Type='$($localField.field_type)' DisplayName='$safeDisplay' Required='FALSE' Format='DateTime' FriendlyDisplayFormat='Disabled' StaticName='$($localField.internal_name)' Name='$($localField.internal_name)' />"
                Add-PnPFieldFromXml -List $listTitle -FieldXml $xml -ErrorAction Stop | Out-Null
                $executed += [ordered]@{ step = "list_local_field"; detail = "created list-local field '$($localField.internal_name)' on '$listTitle'" }
            }
            catch {
                $failed += [ordered]@{ step = "list_local_field"; detail = $localField.internal_name; error = $_.Exception.Message }
            }
        }
    }

    if ($failed.Count -eq 0) {
        try {
            $viewTitle = $plan.view_creation.title
            $startField = ($plan.list_local_fields | Where-Object { $_.internal_name -match "^(?i)start$" } | Select-Object -First 1).internal_name
            if (-not $startField) { $startField = "Start" }
            $existingCalendarView = Get-PnPView -List $listTitle -ErrorAction SilentlyContinue | Where-Object { $_.Title -eq $viewTitle }
            if ($existingCalendarView) {
                Remove-PnPView -List $listTitle -Identity $viewTitle -Force -ErrorAction Stop | Out-Null
            }
            $viewPayload = @"
{
"parameters": {
    "Title": "$viewTitle",
    "ViewTypeKind": $($plan.view_creation.view_type_kind),
    "ViewType2": "$($plan.view_creation.view_type2)",
    "RowLimit": 0,
    "ViewFields": [ "$startField", "Title" ],
    "ViewData": "<FieldRef Name='Title' Type='CalendarMonthTitle' /><FieldRef Name='$startField' Type='CalendarMonthLocation' />"
}
}
"@
            Invoke-PnPSPRestMethod -Method Post -Url "/_api/web/lists/getByTitle('$listTitle')/views/add" -Content $viewPayload | Out-Null
            Set-PnPView -List $listTitle -Identity $viewTitle -Values @{DefaultView = $true } -ErrorAction Stop | Out-Null
            $executed += [ordered]@{ step = "view_creation"; detail = "created modern calendar view '$viewTitle' and set as default" }
        }
        catch {
            $failed += [ordered]@{ step = "view_creation"; error = $_.Exception.Message }
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
        outcome  = $outcome
        dry_run  = $false
        executed = $executed
        failed   = $failed
    }

    $resultJson = $result | ConvertTo-Json -Depth 8
    $resultJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $resultJson -Encoding UTF8 }
}
else {
    $actionPlans = @(
        [ordered]@{ step = "list_creation"; action = "New-PnPList -Title `"$listTitle`" -Template 100" }
    )
    foreach ($localField in $plan.list_local_fields) {
        $actionPlans += [ordered]@{ step = "list_local_field"; action = "Add-PnPFieldFromXml -List `"$listTitle`" -FieldXml <list-scoped DateTime XML for '$($localField.internal_name)'>" }
    }
    $actionPlans += [ordered]@{ step = "view_creation"; action = "Invoke-PnPSPRestMethod POST /_api/web/lists/getByTitle('$listTitle')/views/add (ViewTypeKind=$($plan.view_creation.view_type_kind), ViewType2=$($plan.view_creation.view_type2)) + Set-PnPView -Values @{DefaultView=`$true}" }

    $summary = [ordered]@{
        operation = "provision-spo-calendar"
        confirmation_token = $plan.confirmation_token
        list_title = $listTitle
        site_url = $SiteUrl
        safety = [ordered]@{
            tenant_io = "none"
            execute_requires_confirm_token = "PROVISION-SPO-CALENDAR"
            start_end_guard = "template forced to 100 (refuses 106); Start/End fields always submitted -List scoped, never as site columns"
        }
        actions = $actionPlans
    }

    $summaryJson = $summary | ConvertTo-Json -Depth 8
    $summaryJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $summaryJson -Encoding UTF8 }
}
