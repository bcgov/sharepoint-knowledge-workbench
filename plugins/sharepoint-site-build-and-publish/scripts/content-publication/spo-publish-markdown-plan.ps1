<#
.SYNOPSIS
Uploads rendered Markdown/media files to a SharePoint document library from
a PublishPlan.

.DESCRIPTION
Reads a PublishPlan JSON file (document_id, actions[]: source_path,
target_library, target_folder, target_filename) and, for each action,
verifies the target library, resolves and verifies the target folder
(creating missing nested folders), then uploads via Add-PnPFile. Uses
checkout/checkin (Set-PnPFileCheckedOut / Set-PnPFileCheckedIn
-CheckinType MajorCheckIn) around any overwrite of an existing file. By
default performs no SharePoint tenant I/O; -Execute plus -ConfirmToken
PUBLISH-SPO-MARKDOWN runs the real writes.

.PARAMETER PlanPath
Path to a PublishPlan JSON file matching PublishPlan.to_dict()'s shape
(as built by sharepoint_publish_plan.py's build_markdown_publish_plan).

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
Verifies the target library, creates and confirms missing target folders,
and runs the real Add-PnPFile / checkout-checkin calls. Omit this to print
the per-action plan only.

.PARAMETER ConfirmToken
Required with -Execute. Must be PUBLISH-SPO-MARKDOWN.

.EXAMPLE
.\spo-publish-markdown-plan.ps1 -PlanPath plan.json -SiteUrl "https://tenant.sharepoint.com/sites/Test" -Execute -ConfirmToken PUBLISH-SPO-MARKDOWN
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
    throw "Plan at '$PlanPath' has no actions -- nothing to publish."
}

if ($Execute) {
    if ($ConfirmToken -ne "PUBLISH-SPO-MARKDOWN") {
        throw "-Execute requires -ConfirmToken PUBLISH-SPO-MARKDOWN."
    }
    $requiredCommands = @("Get-PnPList", "Resolve-PnPFolder", "Get-PnPFolder", "Add-PnPFile")
    $missingCommands = @($requiredCommands | Where-Object {
        -not (Get-Command $_ -ErrorAction SilentlyContinue)
    })
    if ($missingCommands.Count -gt 0) {
        throw "PnP.PowerShell commands are required before execution: $($missingCommands -join ', '). Install/import PnP.PowerShell before executing."
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
        if (-not (Test-Path -LiteralPath $action.source_path)) {
            throw "source_path '$($action.source_path)' does not exist -- refusing to upload nothing."
        }

        $targetFolder = "$($action.target_library)/$($action.target_folder)".TrimEnd("/").Replace("//", "/")
        $targetServerRelativeUrl = "$targetFolder/$($action.target_filename)"

        try {
            $targetLibrary = Get-PnPList -Identity $action.target_library -ErrorAction Stop
        }
        catch {
            throw "Unable to verify target document library '$($action.target_library)' before upload; no file was uploaded. If the library is missing, create it with the SharePoint document-library skill and rerun. Details: $($_.Exception.Message)"
        }
        if (-not $targetLibrary) {
            throw "Target document library '$($action.target_library)' could not be confirmed; no file was uploaded. If the library is missing, create it with the SharePoint document-library skill and rerun."
        }

        if (-not [string]::IsNullOrWhiteSpace([string]$action.target_folder)) {
            try {
                Resolve-PnPFolder -SiteRelativePath $targetFolder -ErrorAction Stop | Out-Null
                $resolvedFolder = Get-PnPFolder -Url $targetFolder -ErrorAction Stop
            }
            catch {
                throw "Unable to ensure and verify target folder '$targetFolder' before upload; no file was uploaded. Details: $($_.Exception.Message)"
            }
            if (-not $resolvedFolder) {
                throw "Target folder '$targetFolder' could not be confirmed after resolution; no file was uploaded."
            }
        }

        $existingFile = Get-PnPFile -Url $targetServerRelativeUrl -ErrorAction SilentlyContinue
        if ($existingFile) {
            Set-PnPFileCheckedOut -Url $targetServerRelativeUrl
        }

        Add-PnPFile -Path $action.source_path -Folder $targetFolder -NewFileName $action.target_filename | Out-Null

        if ($existingFile) {
            Set-PnPFileCheckedIn -Url $targetServerRelativeUrl -CheckinType MajorCheckIn
        }

        [pscustomobject]@{
            source_path          = $action.source_path
            target_url           = $targetServerRelativeUrl
            target_folder_verified = $true
            overwrote            = [bool]$existingFile
            success              = $true
        }
    }

    $results | ConvertTo-Json -Depth 8
}
else {
    $actionPlans = foreach ($action in $plan.actions) {
        $targetFolder = "$($action.target_library)/$($action.target_folder)".TrimEnd("/").Replace("//", "/")
        [ordered]@{
            source_path = $action.source_path
            target_folder = $targetFolder
            target_filename = $action.target_filename
            verify_library = "Get-PnPList -Identity `"$($action.target_library)`""
            resolve_target_folder = if ([string]::IsNullOrWhiteSpace([string]$action.target_folder)) {
                "Target document library root"
            }
            else {
                "Resolve-PnPFolder -SiteRelativePath `"$targetFolder`""
            }
            verify_target_folder = if ([string]::IsNullOrWhiteSpace([string]$action.target_folder)) {
                "Get-PnPList -Identity `"$($action.target_library)`""
            }
            else {
                "Get-PnPFolder -Url `"$targetFolder`""
            }
            checkout_if_exists = "Set-PnPFileCheckedOut -Url `"$targetFolder/$($action.target_filename)`""
            upload = "Add-PnPFile -Path `"$($action.source_path)`" -Folder `"$targetFolder`" -NewFileName `"$($action.target_filename)`""
            checkin_if_existed = "Set-PnPFileCheckedIn -Url `"$targetFolder/$($action.target_filename)`" -CheckinType MajorCheckIn"
        }
    }

    $summary = [ordered]@{
        operation = "publish-spo-markdown"
        document_id = $plan.document_id
        action_count = $plan.actions.Count
        site_url = $SiteUrl
        safety = [ordered]@{
            tenant_io = "none"
            execute_requires_confirm_token = "PUBLISH-SPO-MARKDOWN"
        }
        actions = $actionPlans
    }

    $summary | ConvertTo-Json -Depth 8
}
