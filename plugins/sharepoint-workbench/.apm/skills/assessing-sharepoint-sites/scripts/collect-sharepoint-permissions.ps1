<#
.SYNOPSIS
Collects role assignments (permissions) for a site and its lists/libraries
from a live SharePoint site, in the flat JSON shape analyze-permissions'
permissions_analysis.py already consumes.

.DESCRIPTION
Read-only. Connects via Windows-credential/NTLM REST (works against both
legacy on-premises SharePoint 2016 and modern SharePoint Online, since both
expose the same _api/web/roleassignments REST surface). Queries the site's
own role assignments, then each non-hidden list/library's role assignments
where HasUniqueRoleAssignments is true (lists that still inherit the site's
permissions are not separately reported -- they have nothing of their own to
audit). Performs zero tenant writes.

Output is a flat JSON array of {webUrl, principalTitle, permissionLevels,
objectTitle | listName} records -- the exact shape
plugins/sharepoint-site-assessment/tests/fixtures/permissions-flat.json already
demonstrates and permissions_analysis.py's analyse() already accepts.

.PARAMETER SiteUrl
Target site. Required.

.PARAMETER OutputPath
Where to write the resulting JSON array. Required.

.PARAMETER UseDefaultCredentials
Use the current Windows session (Kerberos/NTLM) instead of a credential
prompt.

.EXAMPLE
.\collect-sharepoint-permissions.ps1 -SiteUrl "https://tenant.example.com/sites/Team" -OutputPath permissions.json -UseDefaultCredentials
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$SiteUrl,

    [Parameter(Mandatory = $true)]
    [string]$OutputPath,

    [switch]$UseDefaultCredentials
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$script:headers = @{ "Accept" = "application/json;odata=verbose" }
$script:credential = $null

if (-not $UseDefaultCredentials) {
    $script:credential = Get-Credential -Message "Credentials for $SiteUrl"
    if (-not $script:credential) { throw "No credentials provided." }
}

function Invoke-SPRest {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string]$Url)
    try {
        if ($UseDefaultCredentials) {
            return Invoke-RestMethod -Uri $Url -Headers $script:headers -UseDefaultCredentials -ErrorAction Stop
        }
        return Invoke-RestMethod -Uri $Url -Headers $script:headers -Credential $script:credential -ErrorAction Stop
    }
    catch {
        Write-Warning "REST call failed: $Url -- $($_.Exception.Message)"
        return $null
    }
}

function Get-PermissionRecords {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$WebUrl,
        [string]$ObjectTitle,
        [string]$ListTitle
    )
    $records = @()
    $raUrl = if ($ListTitle) {
        $encodedTitle = [Uri]::EscapeDataString($ListTitle.Replace("'", "''"))
        "$WebUrl/_api/web/lists/getbytitle('$encodedTitle')/roleassignments?`$expand=Member,RoleDefinitionBindings"
    } else {
        "$WebUrl/_api/web/roleassignments?`$expand=Member,RoleDefinitionBindings"
    }
    $result = Invoke-SPRest -Url $raUrl
    if ($null -eq $result) { return , $records }

    foreach ($ra in $result.d.results) {
        $roles = ($ra.RoleDefinitionBindings.results | ForEach-Object { $_.Name }) -join "; "
        $record = [ordered]@{
            webUrl           = $WebUrl
            principalTitle   = $ra.Member.Title
            permissionLevels = $roles
        }
        if ($ListTitle) { $record["listName"] = $ListTitle } else { $record["objectTitle"] = $ObjectTitle }
        $records += [pscustomobject]$record
    }
    return , $records
}

Write-Host "Collecting permissions for $SiteUrl ..." -ForegroundColor Cyan

$allRecords = @()
$allRecords += Get-PermissionRecords -WebUrl $SiteUrl -ObjectTitle "Site"

$listsUrl = "$SiteUrl/_api/web/lists?`$select=Title,Hidden,HasUniqueRoleAssignments"
$listsResult = Invoke-SPRest -Url $listsUrl
if ($listsResult) {
    foreach ($list in $listsResult.d.results) {
        if ($list.Hidden -or -not $list.HasUniqueRoleAssignments) { continue }
        Write-Host "  Unique permissions on: $($list.Title)" -ForegroundColor DarkGray
        $allRecords += Get-PermissionRecords -WebUrl $SiteUrl -ListTitle $list.Title
    }
}

$allRecords | ConvertTo-Json -Depth 8 | Set-Content -Path $OutputPath -Encoding UTF8
Write-Host "Wrote $($allRecords.Count) permission record(s) to $OutputPath" -ForegroundColor Green
