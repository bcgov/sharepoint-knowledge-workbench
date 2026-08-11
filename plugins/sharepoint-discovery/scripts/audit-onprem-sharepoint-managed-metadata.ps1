<#
.SYNOPSIS
Audits a legacy on-premises SharePoint 2016 site (and optionally a parent
site) for Managed Metadata (Taxonomy) usage -- term group/term-set discovery
via CSOM TaxonomySession plus every list/library and site column bound to a
Taxonomy field -- via NTLM/Kerberos REST + CSOM.

.DESCRIPTION
On-prem SharePoint (unlike modern SPO) has no Entra app-registration path in
general use here, so this script authenticates via NTLM/Kerberos --
Invoke-RestMethod with -UseDefaultCredentials or an explicit -Credential --
not Connect-PnPOnline. This is a deliberate divergence from this repo's
standard PnP.PowerShell auth convention, required because the target is
on-prem SP2016.

Performs three checks:

  1. List/library column scan on -SiteUrl (and -ParentSiteUrl, if supplied)
     via REST: enumerates non-hidden, non-system lists/libraries and flags
     fields whose TypeAsString is TaxonomyField or TaxonomyFieldTypeMulti.
  2. Site column scan on the same site(s), same field-type filter.
  3. Term group/term-set lookup via CSOM TaxonomySession, resolving
     -TermGroupName against the term store reachable from -SiteUrl. Falls
     back to the site collection's local term group if no global match is
     found. A CSOM assembly/version failure is recorded as a non-fatal
     finding (Error field), not thrown.

Never silently produces empty/fake results: failed REST calls emit
Write-Warning and the affected record set is empty, not fabricated.

.PARAMETER SiteUrl
The on-prem SP2016 site to audit. Required (no hardcoded default).

.PARAMETER ParentSiteUrl
Optional parent/root site to also audit (e.g. when -SiteUrl is a subsite).
Omit to audit -SiteUrl only.

.PARAMETER ListName
Optional list name to restrict the list/library column scan to. Omit to
scan every non-hidden, non-system list/library.

.PARAMETER TermGroupName
The Term Group to look up via CSOM. Defaults to "" (skips the term-group
lookup) unless supplied.

.PARAMETER UseDefaultCredentials
Use the current Windows session (Kerberos/NTLM pass-through). Requires VPN /
domain-joined. Without this switch, a credential prompt is shown.

.PARAMETER OutputPath
Where to write the resulting JSON. Required.

.EXAMPLE
.\audit-onprem-sharepoint-managed-metadata.ps1 -SiteUrl "https://sp2016.example.org/sites/Legacy" -TermGroupName "Enterprise Taxonomy" -OutputPath managed-metadata-audit.json -UseDefaultCredentials

.EXAMPLE
.\audit-onprem-sharepoint-managed-metadata.ps1 -SiteUrl "https://sp2016.example.org/subsite" -ParentSiteUrl "https://sp2016.example.org" -OutputPath managed-metadata-audit.json
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$SiteUrl,

    [string]$ParentSiteUrl,

    [string]$ListName,

    [string]$TermGroupName = "",

    [switch]$UseDefaultCredentials,

    [Parameter(Mandatory = $true)]
    [string]$OutputPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$script:spHeaders    = @{ "Accept" = "application/json;odata=verbose" }
$script:spCredential = $null
$script:spUseDefault = [bool]$UseDefaultCredentials

if (-not $script:spUseDefault) {
    $script:spCredential = Get-Credential -Message "Credentials for $SiteUrl"
}

function Invoke-SPRest {
    param([string]$Url)
    try {
        if ($script:spUseDefault) {
            return Invoke-RestMethod -Uri $Url -Headers $script:spHeaders -UseDefaultCredentials -ErrorAction Stop
        }
        return Invoke-RestMethod -Uri $Url -Headers $script:spHeaders -Credential $script:spCredential -ErrorAction Stop
    } catch {
        Write-Warning "REST call failed: $Url - $($_.Exception.Message)"
        return $null
    }
}

function Get-SPRestAll {
    param([string]$Url)
    $all = @()
    $nextUrl = $Url
    while ($nextUrl) {
        $result = Invoke-SPRest -Url $nextUrl
        if ($null -eq $result) { break }
        $items = $result.d.results
        if ($items) { $all += $items }
        $nextProp = $result.d.PSObject.Properties['__next']
        $nextUrl = if ($nextProp) { $nextProp.Value } else { $null }
    }
    return , $all
}

$script:systemTitles = @(
    "Access Requests", "App Packages", "appdata", "appfiles", "Composed Looks",
    "Content and Structure Reports", "Content type publishing error log", "Converted Forms",
    "Device Channels", "List Template Gallery", "Long Running Operation Status",
    "Maintenance Log Library", "MicroFeed", "Relationships List", "Reusable Content", "Site Assets",
    "Site Collection Documents", "Site Collection Images", "Site Pages", "Solution Gallery",
    "Style Library", "TaxonomyHiddenList", "Theme Gallery", "Translation Packages",
    "User Information List", "Web Part Gallery", "wfpub", "Workflow History", "Workflow Tasks"
)

function Get-SiteManagedMetadata {
    <#
    Scans one web's lists/libraries (or a single -ListName, if supplied) and
    site columns for Taxonomy-typed fields. Returns a
    { WebTitle, ListColumns, SiteColumns } record, or $null if the site
    could not be reached.
    #>
    param([string]$TargetUrl)

    Write-Host "`nConnecting to $TargetUrl ..." -ForegroundColor DarkGray
    $testResult = Invoke-SPRest -Url "$TargetUrl/_api/web?`$select=Title"
    if ($null -eq $testResult) {
        Write-Warning "Could not connect to $TargetUrl. Skipping."
        return $null
    }
    $webTitle = $testResult.d.Title
    Write-Host "Connected successfully to web: $webTitle" -ForegroundColor Green

    # Determine which list(s) to check
    $listsToCheck = @()
    if (-not [string]::IsNullOrWhiteSpace($ListName)) {
        $listsToCheck += [pscustomobject]@{ Title = $ListName; BaseType = 1 }
    } else {
        $listsUrl = "$TargetUrl/_api/web/lists?`$select=Title,BaseType,Hidden"
        $allLists = Get-SPRestAll -Url $listsUrl
        if ($allLists.Count -eq 1 -and $allLists[0] -is [System.Array]) { $allLists = $allLists[0] }
        foreach ($l in $allLists) {
            if (-not ($l.Hidden -eq $true -or $l.Hidden -eq "true") -and ($script:systemTitles -notcontains $l.Title)) {
                $listsToCheck += $l
            }
        }
    }

    $listColumnResults = @()
    foreach ($list in $listsToCheck) {
        $listType = if ($list.BaseType -eq 1 -or $list.BaseType -eq "1") { "Library" } else { "List" }
        $encodedTitle = [Uri]::EscapeDataString($list.Title).Replace("'", "''")
        $fields = Get-SPRestAll -Url "$TargetUrl/_api/web/lists/getbytitle('$encodedTitle')/fields"
        if ($fields.Count -eq 1 -and $fields[0] -is [System.Array]) { $fields = $fields[0] }
        if ($fields.Count -eq 0) { continue }

        $metadataFields = @($fields | Where-Object { $_.TypeAsString -eq "TaxonomyField" -or $_.TypeAsString -eq "TaxonomyFieldTypeMulti" })
        foreach ($f in $metadataFields) {
            $listColumnResults += [pscustomobject]@{
                Web          = $webTitle
                WebUrl       = $TargetUrl
                ListName     = $list.Title
                ListType     = $listType
                ColumnTitle  = $f.Title
                InternalName = $f.InternalName
                FieldType    = $f.TypeAsString
                Hidden       = $f.Hidden
            }
        }
    }

    $siteColumnResults = @()
    $fields = Get-SPRestAll -Url "$TargetUrl/_api/web/fields"
    if ($fields.Count -eq 1 -and $fields[0] -is [System.Array]) { $fields = $fields[0] }
    $metadataFields = @($fields | Where-Object { $_.TypeAsString -eq "TaxonomyField" -or $_.TypeAsString -eq "TaxonomyFieldTypeMulti" })
    foreach ($f in $metadataFields) {
        $siteColumnResults += [pscustomobject]@{
            Web          = $webTitle
            WebUrl       = $TargetUrl
            ColumnTitle  = $f.Title
            InternalName = $f.InternalName
            FieldType    = $f.TypeAsString
            Group        = $f.Group
            Hidden       = $f.Hidden
        }
    }

    return [pscustomobject]@{
        WebUrl      = $TargetUrl
        WebTitle    = $webTitle
        ListColumns = @($listColumnResults)
        SiteColumns = @($siteColumnResults)
    }
}

function Get-TermGroupAudit {
    <#
    Resolves -TermGroupName via CSOM TaxonomySession against -SiteUrl. Falls
    back to the site collection's local term group. Returns a
    { TermGroupName, Found, TermSets, Error } record; never throws.
    #>
    param([string]$TargetUrl, [string]$GroupName)

    $auditResult = [pscustomobject]@{
        TermGroupName = $GroupName
        Found         = $false
        TermSets      = @()
        Error         = $null
    }
    if ([string]::IsNullOrWhiteSpace($GroupName)) { return $auditResult }

    try {
        [System.Reflection.Assembly]::LoadWithPartialName("Microsoft.SharePoint.Client") | Out-Null
        [System.Reflection.Assembly]::LoadWithPartialName("Microsoft.SharePoint.Client.Runtime") | Out-Null
        [System.Reflection.Assembly]::LoadWithPartialName("Microsoft.SharePoint.Client.Taxonomy") | Out-Null
        Import-Module PnP.PowerShell -ErrorAction SilentlyContinue | Out-Null

        $ctx = New-Object Microsoft.SharePoint.Client.ClientContext($TargetUrl)
        if ($script:spUseDefault) {
            $ctx.Credentials = [System.Net.CredentialCache]::DefaultCredentials
        } else {
            $ctx.Credentials = $script:spCredential
        }

        $taxSession = [Microsoft.SharePoint.Client.Taxonomy.TaxonomySession]::GetTaxonomySession($ctx)
        $termStores = $taxSession.TermStores
        $ctx.Load($termStores)
        $ctx.ExecuteQuery()

        if ($termStores.Count -eq 0) {
            $auditResult.Error = "No Term Store accessible via CSOM."
            return $auditResult
        }

        $ts = $termStores[0]
        $groups = $ts.Groups
        $ctx.Load($groups)
        $ctx.ExecuteQuery()

        $matchingGroup = $groups | Where-Object { $_.Name -eq $GroupName -or $_.Name -like "*$GroupName*" }

        if ($null -eq $matchingGroup) {
            try {
                $siteObj = $ctx.Site
                $ctx.Load($siteObj)
                $ctx.ExecuteQuery()
                $localGroup = $ts.GetSiteCollectionGroup($siteObj)
                $ctx.Load($localGroup)
                $ctx.ExecuteQuery()
                if ($localGroup.Name -match $GroupName) { $matchingGroup = $localGroup }
            } catch {
                # Silent fallback if site collection group retrieval fails
            }
        }

        if ($null -eq $matchingGroup) {
            $auditResult.Error = "Term Group '$GroupName' not found in this Term Store."
            return $auditResult
        }

        $auditResult.Found = $true
        $termSets = $matchingGroup.TermSets
        $ctx.Load($termSets)
        $ctx.ExecuteQuery()
        $auditResult.TermSets = @(foreach ($tsItem in $termSets) {
                [pscustomobject]@{ Name = $tsItem.Name; Id = $tsItem.Id.ToString(); Description = $tsItem.Description }
            })
    } catch {
        $auditResult.Error = "Could not query Taxonomy Term Store via CSOM: $($_.Exception.Message)"
    }
    return $auditResult
}

function Write-JsonOutput {
    param($Object, [string]$Path)
    $Object | ConvertTo-Json -Depth 10 | Set-Content -Path $Path -Encoding UTF8
}

$sitesAudited = @()
$primary = Get-SiteManagedMetadata -TargetUrl $SiteUrl
if ($primary) { $sitesAudited += $primary }

if (-not [string]::IsNullOrWhiteSpace($ParentSiteUrl)) {
    $parent = Get-SiteManagedMetadata -TargetUrl $ParentSiteUrl
    if ($parent) { $sitesAudited += $parent }
}

$termGroupResult = Get-TermGroupAudit -TargetUrl $SiteUrl -GroupName $TermGroupName

$allListColumns = @($sitesAudited | ForEach-Object { $_.ListColumns })
$allSiteColumns = @($sitesAudited | ForEach-Object { $_.SiteColumns })

$result = [pscustomobject]@{
    GeneratedOn        = (Get-Date).ToString("s")
    SiteUrl            = $SiteUrl
    ParentSiteUrl      = $ParentSiteUrl
    Sites              = @($sitesAudited)
    TermGroup          = $termGroupResult
    ListColumns        = $allListColumns
    ListColumnCount    = $allListColumns.Count
    SiteColumns        = $allSiteColumns
    SiteColumnCount    = $allSiteColumns.Count
    AnyManagedMetadata = ($allListColumns.Count -gt 0 -or $allSiteColumns.Count -gt 0)
}

Write-JsonOutput -Object $result -Path $OutputPath
Write-Host "Wrote managed metadata audit ($($allListColumns.Count) list column(s), $($allSiteColumns.Count) site column(s)) to $OutputPath" -ForegroundColor Green
