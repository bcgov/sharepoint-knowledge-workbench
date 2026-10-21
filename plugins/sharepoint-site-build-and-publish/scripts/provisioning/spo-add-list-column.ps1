<#
.SYNOPSIS
Real PnP executor for list-scoped column creation -- Add-PnPField against a plan JSON.

.DESCRIPTION
Same dry-run-by-default / -Execute + -ConfirmToken / Get-WorkbenchConnectionConfig.ps1
pattern as every other spo-provision-*.ps1 script in this plugin -- see that
script's own docstring for the full safety-gate rationale, not repeated here.

Plan JSON shape:

    {
      "confirmation_token": "ADD-2-abcdef0123456789",
      "actions": [
        {
          "list_title": "Forms",
          "internal_name": "SIZAFormNumber",
          "display_name": "Form Number",
          "type": "Text",
          "add_to_default_view": true,
          "choices": []
        },
        {
          "list_title": "Forms",
          "internal_name": "SIZAFormType",
          "display_name": "Form Type",
          "type": "Lookup",
          "lookup_list": "Form Types",
          "lookup_field": "Title"
        }
      ]
    }

`type`, `add_to_default_view` and `choices` are optional (default Text, false, none).
A `Lookup` action resolves `lookup_list` (by title) to its GUID and submits field XML via
Add-PnPFieldFromXml -List; `lookup_field` defaults to Title. The lookup list must already
exist, and a Lookup column is not added to the default view.

.PARAMETER PlanPath
Path to the plan JSON described above.

.PARAMETER Execute
Runs the real Add-PnPField / Add-PnPFieldFromXml calls. Omit this to print a dry-run action summary
and take no tenant action.

.PARAMETER ConfirmToken
Must equal ADD-SPO-LIST-COLUMN when -Execute is passed. Refused otherwise.

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
    if ($ConfirmToken -ne "ADD-SPO-LIST-COLUMN") {
        throw "-Execute requires -ConfirmToken ADD-SPO-LIST-COLUMN."
    }
    if (-not $SiteUrl -or -not $ClientId -or -not $TenantId) {
        throw "SiteUrl/ClientId/TenantId not resolved. Provide -SiteUrl/-ClientId/-TenantId or a valid -ConfigPath."
    }
    if (-not (Get-Command Add-PnPField -ErrorAction SilentlyContinue)) {
        throw "PnP.PowerShell with Add-PnPField is required. Install/import PnP.PowerShell before executing."
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
            $names = $action.PSObject.Properties.Name
            $type = if ($names -contains 'type') { [string]$action.type } else { "Text" }
            if ($type -eq "Lookup") {
                if (-not ($names -contains 'lookup_list') -or [string]::IsNullOrWhiteSpace([string]$action.lookup_list)) {
                    throw "Lookup column '$($action.internal_name)' needs a lookup_list in the plan."
                }
                $lookupList = Get-PnPList -Identity $action.lookup_list -ErrorAction Stop
                $showField = if ($names -contains 'lookup_field' -and $action.lookup_field) { [string]$action.lookup_field } else { "Title" }
                $xmlName = [System.Security.SecurityElement]::Escape([string]$action.internal_name)
                $xmlDisplay = [System.Security.SecurityElement]::Escape([string]$action.display_name)
                $xmlShow = [System.Security.SecurityElement]::Escape($showField)
                $fieldXml = "<Field Type=""Lookup"" Name=""$xmlName"" StaticName=""$xmlName"" DisplayName=""$xmlDisplay"" List=""{$($lookupList.Id)}"" ShowField=""$xmlShow"" />"
                Add-PnPFieldFromXml -List $action.list_title -FieldXml $fieldXml -ErrorAction Stop | Out-Null
            }
            else {
                $addToView = ($names -contains 'add_to_default_view') -and [bool]$action.add_to_default_view
                $fieldParams = @{ List = $action.list_title; DisplayName = $action.display_name; InternalName = $action.internal_name; Type = $type; AddToDefaultView = $addToView; ErrorAction = "Stop" }
                if (($names -contains 'choices') -and $action.choices) { $fieldParams["Choices"] = $action.choices }
                Add-PnPField @fieldParams | Out-Null
            }
            $updated += [ordered]@{ internal_name = $action.internal_name }
        }
        catch {
            $failed += [ordered]@{ list_title = $action.list_title; internal_name = $action.internal_name; error = $_.Exception.Message }
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
        $listTitle = if ($action.PSObject.Properties.Name -contains 'list_title') { $action.list_title } else { $null }
        $internalName = if ($action.PSObject.Properties.Name -contains 'internal_name') { $action.internal_name } else { $null }
        $displayName = if ($action.PSObject.Properties.Name -contains 'display_name') { $action.display_name } else { $internalName }
        $type = if ($action.PSObject.Properties.Name -contains 'type') { $action.type } else { "Text" }
        $lookupList = if ($action.PSObject.Properties.Name -contains 'lookup_list') { $action.lookup_list } else { $null }
        [ordered]@{
            list_title    = $listTitle
            internal_name = $internalName
            action        = if ($type -eq "Lookup") {
                "Add-PnPFieldFromXml -List `"$listTitle`" (Lookup `"$internalName`" -> list `"$lookupList`")"
            }
            else {
                "Add-PnPField -List `"$listTitle`" -Type $type -InternalName `"$internalName`" -DisplayName `"$displayName`""
            }
        }
    }
    $summary = [ordered]@{
        operation           = "add-spo-list-columns"
        confirmation_token  = $plan.confirmation_token
        add_count           = $plan.actions.Count
        site_url            = $SiteUrl
        safety              = [ordered]@{
            tenant_io                      = "none"
            execute_requires_confirm_token = "ADD-SPO-LIST-COLUMN"
        }
        planned_actions     = $actionPlans
    }
    $summaryJson = $summary | ConvertTo-Json -Depth 8
    $summaryJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $summaryJson -Encoding UTF8 }
}
