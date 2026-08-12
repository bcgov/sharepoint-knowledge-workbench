<#
.SYNOPSIS
Uploads pre-computed remediated Office document content (docx/xlsx/pptx)
back to a SharePoint document library, replacing the original file, with
explicit checkout/checkin around the write.

.DESCRIPTION
Reads a DocumentRemediationPlan JSON file matching
DocumentRemediationPlan.to_dict()'s shape (documents[].source,
documents[].format, documents[].changed, documents[].changes[],
confirmation_token).

DESIGN SEAM -- read before use: document_link_remediation.py's
DocumentRemediation.to_dict() reports only source/format/changed/changes; it
deliberately does NOT serialize the remediated file bytes into JSON (bytes
are not JSON-safe, and embedding a whole rewritten Office file inline would
make the plan file enormous). The actual OOXML zipfile/XML-part rewrite is
Python-only logic (see _rewrite_ooxml in document_link_remediation.py) --
this PowerShell script has no equivalent and does not attempt to reimplement
an OOXML rewriter. The realistic division of labor is: the Python side
computes plan_document_link_remediation(...), writes each changed document's
already-remediated bytes to a local temp file, and augments the plan JSON
with a `remediated_content_path` field (an absolute local path) on each
changed document, e.g.:

    import tempfile, json
    from link_rules import load_ruleset
    from document_link_remediation import plan_document_link_remediation

    plan = plan_document_link_remediation(documents, load_ruleset("rules.json"))
    payload = plan.to_dict()
    for doc_dict, doc in zip(payload["documents"], plan.documents):
        if doc.is_changed:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix="." + doc.format)
            tmp.write(doc.remediated_content)
            tmp.close()
            doc_dict["remediated_content_path"] = tmp.name
    json.dump(payload, open("plan.json", "w"))

This script's job starts from that augmented plan: for each changed
document, it checks out the target file, uploads the new content from
`remediated_content_path`, then checks it back in. It does not perform any
OOXML rewriting itself.

By default performs no SharePoint tenant I/O; -Execute plus -ConfirmToken
REMEDIATE-SPO-DOCUMENT-LINKS runs the real writes.

.PARAMETER PlanPath
Path to a DocumentRemediationPlan JSON file, augmented with
`remediated_content_path` on each changed document (see .DESCRIPTION).

.PARAMETER TargetLibrary
The document library the plan's `source` paths live in.

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

.PARAMETER CheckinComment
Comment recorded on the check-in. Defaults to a generic remediation note.

.PARAMETER Execute
Runs the real Set-PnPFileCheckedOut/Add-PnPFile/Set-PnPFileCheckedIn calls.
Omit this to print the per-document plan only.

.PARAMETER ConfirmToken
Required with -Execute. Must be REMEDIATE-SPO-DOCUMENT-LINKS.

.EXAMPLE
.\spo-remediate-document-content-links.ps1 -PlanPath plan.json -TargetLibrary "Shared Documents" -SiteUrl "https://tenant.sharepoint.com/sites/Test" -Execute -ConfirmToken REMEDIATE-SPO-DOCUMENT-LINKS
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PlanPath,

    [Parameter(Mandatory = $true)]
    [string]$TargetLibrary,

    [string]$SiteUrl,

    [string]$ConfigPath = (Join-Path $PSScriptRoot "..\..\..\config.psd1"),

    [string]$ClientId,

    [string]$TenantId,

    [string]$TenantAdminUrl,

    [string]$CheckinComment = "Automated link remediation (sharepoint-link-remediation)",

    [switch]$Execute,

    [string]$ConfirmToken
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-WorkbenchConnectionConfig {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return [pscustomobject]@{ SiteUrl = $null; ClientId = $null; TenantId = $null; TenantAdminUrl = $null }
    }

    $rawConfig = Import-PowerShellDataFile -LiteralPath $Path
    $cfg = if ($rawConfig.Connection) { $rawConfig.Connection } else { $rawConfig }
    $tenantAdminUrl = if ($rawConfig.Authentication) { $rawConfig.Authentication.TenantAdminUrl } else { $rawConfig.TenantAdminUrl }

    [pscustomobject]@{
        SiteUrl        = $cfg.SiteUrl
        ClientId       = $cfg.ClientId
        TenantId       = $cfg.TenantId
        TenantAdminUrl = $tenantAdminUrl
    }
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
if (-not $plan.documents) {
    throw "Plan at '$PlanPath' has no documents -- nothing to remediate."
}

$changedDocuments = @($plan.documents | Where-Object { $_.changed })
if ($changedDocuments.Count -eq 0) {
    Write-Host "No changed documents in plan -- nothing to remediate."
    return
}

if ($Execute) {
    if ($ConfirmToken -ne "REMEDIATE-SPO-DOCUMENT-LINKS") {
        throw "-Execute requires -ConfirmToken REMEDIATE-SPO-DOCUMENT-LINKS."
    }
    foreach ($cmdlet in @("Set-PnPFileCheckedOut", "Add-PnPFile", "Set-PnPFileCheckedIn")) {
        if (-not (Get-Command $cmdlet -ErrorAction SilentlyContinue)) {
            throw "PnP.PowerShell with $cmdlet is required. Install/import PnP.PowerShell before executing."
        }
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
        if (-not (Get-Member -InputObject $document -Name "remediated_content_path") -or [string]::IsNullOrEmpty($document.remediated_content_path)) {
            throw "Document '$($document.source)' is marked changed but has no 'remediated_content_path' -- see .DESCRIPTION for the required plan augmentation."
        }
        if (-not (Test-Path -LiteralPath $document.remediated_content_path)) {
            throw "remediated_content_path '$($document.remediated_content_path)' for '$($document.source)' does not exist."
        }

        try {
            $folder = [System.IO.Path]::GetDirectoryName($document.source) -replace "\\", "/"
            $fileName = [System.IO.Path]::GetFileName($document.source)

            Set-PnPFileCheckedOut -Url $document.source | Out-Null
            Add-PnPFile -Path $document.remediated_content_path -Folder $folder -NewFileName $fileName | Out-Null
            Set-PnPFileCheckedIn -Url $document.source -CheckinType MajorCheckIn -Comment $CheckinComment | Out-Null

            [pscustomobject]@{
                source  = $document.source
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
            source          = $document.source
            format          = $document.format
            change_count    = @($document.changes).Count
            checkout        = "Set-PnPFileCheckedOut -Url `"$($document.source)`""
            upload          = "Add-PnPFile -Path <remediated_content_path> -Folder `"$([System.IO.Path]::GetDirectoryName($document.source) -replace '\\','/')`" -NewFileName `"$([System.IO.Path]::GetFileName($document.source))`""
            checkin         = "Set-PnPFileCheckedIn -Url `"$($document.source)`" -CheckinType MajorCheckIn -Comment `"$CheckinComment`""
        }
    }

    $summary = [ordered]@{
        operation = "remediate-spo-document-content-links"
        target_library = $TargetLibrary
        confirmation_token = $plan.confirmation_token
        changed_document_count = $changedDocuments.Count
        site_url = $SiteUrl
        design_seam = "remediated_content_path must be pre-populated by the Python plan_document_link_remediation caller -- this script performs no OOXML rewriting itself; see .DESCRIPTION."
        safety = [ordered]@{
            tenant_io = "none"
            execute_requires_confirm_token = "REMEDIATE-SPO-DOCUMENT-LINKS"
        }
        actions = $actionPlans
    }

    $summary | ConvertTo-Json -Depth 8
}
