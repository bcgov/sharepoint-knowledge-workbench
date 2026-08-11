<#
.SYNOPSIS
Audits a live SharePoint Online site for Managed Metadata (Taxonomy) usage --
term group/term-set discovery plus every list/library and site column bound
to a Taxonomy field -- via PnP.PowerShell.

.DESCRIPTION
Read-only PnP.PowerShell audit. Performs two checks against the connected
site:

  1. Term group/term-set lookup. Resolves -TermGroupName via
     Get-PnPTermGroup / Get-PnPTermSet and records each term set's name, id,
     and description. If the group cannot be found, this is recorded as a
     non-fatal finding rather than a thrown error.

  2. Managed Metadata column scan. Enumerates every non-hidden, non-system
     list/library on the site and every site column, flagging fields whose
     TypeAsString is TaxonomyField or TaxonomyFieldTypeMulti.

Performs zero tenant writes -- every operation calls only Get-PnP* cmdlets.
Never silently produces empty/fake results: a failed term-group lookup is
recorded with an Error field, not fabricated.

.PARAMETER SiteUrl
Target site. Overrides config.psd1 Connection.SiteUrl.

.PARAMETER ConfigPath
Path to config.psd1. Defaults to the repository root config.psd1.

.PARAMETER ClientId
Overrides ConfigPath ClientId.

.PARAMETER TenantId
Overrides ConfigPath TenantId.

.PARAMETER TenantAdminUrl
Overrides ConfigPath Authentication.TenantAdminUrl. Not required for this
script's read operations (all operate within a single site), present only so
this script does not silently diverge from the repo's standard PnP auth
parameter set.

.PARAMETER TermGroupName
The Term Group to look up. Defaults to "" (skips the term-group lookup and
reports only the column scan) unless supplied.

.PARAMETER OutputPath
Where to write the resulting JSON. Required.

.EXAMPLE
.\audit-sharepoint-managed-metadata.ps1 -SiteUrl "https://tenant.sharepoint.com/sites/Test" -TermGroupName "Enterprise Taxonomy" -OutputPath managed-metadata-audit.json
#>

[CmdletBinding()]
param(
    [string]$SiteUrl,

    [string]$ConfigPath = (Join-Path $PSScriptRoot "..\..\..\config.psd1"),

    [string]$ClientId,

    [string]$TenantId,

    [string]$TenantAdminUrl,

    [string]$TermGroupName = "",

    [Parameter(Mandatory = $true)]
    [string]$OutputPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$script:systemTitles = @(
    "Access Requests", "App Packages", "appdata", "appfiles", "Composed Looks",
    "Content and Structure Reports", "Content type publishing error log", "Converted Forms",
    "Device Channels", "List Template Gallery", "Long Running Operation Status",
    "Maintenance Log Library", "MicroFeed", "Relationships List", "Reusable Content", "Site Assets",
    "Site Collection Documents", "Site Collection Images", "Site Pages", "Solution Gallery",
    "Style Library", "TaxonomyHiddenList", "Theme Gallery", "Translation Packages",
    "User Information List", "Web Part Gallery", "wfpub", "Workflow History", "Workflow Tasks"
)

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

function Write-JsonOutput {
    param($Object, [string]$Path)
    $Object | ConvertTo-Json -Depth 10 | Set-Content -Path $Path -Encoding UTF8
}

$connectionConfig = Get-WorkbenchConnectionConfig -Path $ConfigPath
if (-not $SiteUrl) { $SiteUrl = $connectionConfig.SiteUrl }
if (-not $ClientId) { $ClientId = $connectionConfig.ClientId }
if (-not $TenantId) { $TenantId = $connectionConfig.TenantId }
if (-not $TenantAdminUrl) { $TenantAdminUrl = $connectionConfig.TenantAdminUrl }

if (-not $SiteUrl -or -not $ClientId -or -not $TenantId) {
    throw "SiteUrl/ClientId/TenantId not resolved. Provide -SiteUrl/-ClientId/-TenantId or a valid -ConfigPath."
}

$connectParameters = @{
    Url         = $SiteUrl
    ClientId    = $ClientId
    Tenant      = $TenantId
    Interactive = $true
}
if ($TenantAdminUrl) { $connectParameters["TenantAdminUrl"] = $TenantAdminUrl }
Connect-PnPOnline @connectParameters

try {
    $web = Get-PnPWeb

    # 1. Term group / term set lookup
    $termGroupResult = [pscustomobject]@{
        TermGroupName = $TermGroupName
        Found         = $false
        TermSets      = @()
        Error         = $null
    }
    if (-not [string]::IsNullOrWhiteSpace($TermGroupName)) {
        try {
            $group = Get-PnPTermGroup -Identity $TermGroupName -ErrorAction Stop
            $termGroupResult.Found = $true
            $termSets = Get-PnPTermSet -TermGroup $TermGroupName
            $termGroupResult.TermSets = @(foreach ($ts in $termSets) {
                    [pscustomobject]@{ Name = $ts.Name; Id = $ts.Id.ToString(); Description = $ts.Description }
                })
        } catch {
            $termGroupResult.Error = $_.Exception.Message
        }
    }

    # 2. Managed Metadata columns across non-hidden, non-system lists/libraries
    $lists = Get-PnPList
    $listColumnResults = @()
    foreach ($list in $lists) {
        if ($list.Hidden -or ($script:systemTitles -contains $list.Title)) { continue }

        $fields = Get-PnPField -List $list
        $metadataFields = @($fields | Where-Object { $_.TypeAsString -in @("TaxonomyField", "TaxonomyFieldTypeMulti") })
        if ($metadataFields.Count -eq 0) { continue }

        $listType = if ($list.BaseType -eq "DocumentLibrary" -or $list.BaseType -eq 1) { "Library" } else { "List" }
        foreach ($f in $metadataFields) {
            $listColumnResults += [pscustomobject]@{
                ListTitle    = $list.Title
                ListType     = $listType
                ColumnTitle  = $f.Title
                InternalName = $f.InternalName
                FieldType    = $f.TypeAsString
                Hidden       = $f.Hidden
            }
        }
    }

    # 3. Managed Metadata site columns
    $siteFields = Get-PnPField
    $siteColumnResults = @()
    $metadataSiteFields = @($siteFields | Where-Object { $_.TypeAsString -in @("TaxonomyField", "TaxonomyFieldTypeMulti") })
    foreach ($f in $metadataSiteFields) {
        $siteColumnResults += [pscustomobject]@{
            ColumnTitle  = $f.Title
            InternalName = $f.InternalName
            FieldType    = $f.TypeAsString
            Group        = $f.Group
            Hidden       = $f.Hidden
        }
    }

    $result = [pscustomobject]@{
        GeneratedOn         = (Get-Date).ToString("s")
        SiteUrl             = $SiteUrl
        WebTitle            = $web.Title
        TermGroup           = $termGroupResult
        ListColumns         = @($listColumnResults)
        ListColumnCount     = $listColumnResults.Count
        SiteColumns         = @($siteColumnResults)
        SiteColumnCount     = $siteColumnResults.Count
        AnyManagedMetadata  = ($listColumnResults.Count -gt 0 -or $siteColumnResults.Count -gt 0)
    }

    Write-JsonOutput -Object $result -Path $OutputPath
    Write-Host "Wrote managed metadata audit ($($listColumnResults.Count) list column(s), $($siteColumnResults.Count) site column(s)) to $OutputPath" -ForegroundColor Green
} finally {
    Disconnect-PnPOnline -ErrorAction SilentlyContinue
}
