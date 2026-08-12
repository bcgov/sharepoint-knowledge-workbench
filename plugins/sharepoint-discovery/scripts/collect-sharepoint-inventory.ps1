<#
.SYNOPSIS
Collects lists/libraries, list-field, library-file, or content-type/schema
inventory from a live SharePoint Online site via PnP.PowerShell.

.DESCRIPTION
Read-only PnP.PowerShell collector with four modes, selected via -Mode:

  Lists         Enumerates all lists/libraries on the site (title, item count,
                base type, hidden flag, content-types-enabled, unique
                permissions flag).
  ListFields    Exports a named list's field definitions. Use -FieldNames to
                restrict to specific internal names (e.g. an ID + one named
                field), or omit it to export every non-hidden field.
  LibraryFiles  Recursively inventories every file in a named document
                library (name + server-relative URL), across all sub-folders.
  ContentTypes  Exports site content-type definitions (name, id, group,
                field links), optionally filtered by -ContentTypeNameFilter
                (wildcard, e.g. "Modern_*"), plus, if -ListNames is supplied,
                each named list's own field/content-type schema.

Performs zero tenant writes -- every mode calls only Get-PnP* cmdlets.

.PARAMETER SiteUrl
Target site. Overrides config.psd1 Connection.SiteUrl.

.PARAMETER ConfigPath
Path to config.psd1. Defaults to the repository root config.psd1.

.PARAMETER ClientId
Overrides ConfigPath ClientId.

.PARAMETER TenantId
Overrides ConfigPath TenantId.

.PARAMETER TenantAdminUrl
Overrides ConfigPath Authentication.TenantAdminUrl. Not required by any mode
here (all operate within a single site), present only so this script does
not silently diverge from the repo's standard PnP auth parameter set.

.PARAMETER Mode
One of: Lists, ListFields, LibraryFiles, ContentTypes.

.PARAMETER ListName
Required for ListFields and LibraryFiles. The list/library title.

.PARAMETER FieldNames
Optional, ListFields only. Internal field names to include. Omit for all
non-hidden fields.

.PARAMETER ContentTypeNameFilter
Optional, ContentTypes only. Wildcard filter on content type Name. Defaults
to "*" (all site content types).

.PARAMETER ListNames
Optional, ContentTypes only. Also export field/content-type schema for these
named lists.

.PARAMETER OutputPath
Where to write the resulting JSON. Required.

.EXAMPLE
.\collect-sharepoint-inventory.ps1 -SiteUrl "https://tenant.sharepoint.com/sites/Test" -Mode Lists -OutputPath lists.json

.EXAMPLE
.\collect-sharepoint-inventory.ps1 -SiteUrl "https://tenant.sharepoint.com/sites/Test" -Mode ListFields -ListName "Persons" -FieldNames "Comment" -OutputPath persons-comment-fields.json

.EXAMPLE
.\collect-sharepoint-inventory.ps1 -SiteUrl "https://tenant.sharepoint.com/sites/Test" -Mode LibraryFiles -ListName "Images1" -OutputPath images1-files.json

.EXAMPLE
.\collect-sharepoint-inventory.ps1 -SiteUrl "https://tenant.sharepoint.com/sites/Test" -Mode ContentTypes -ContentTypeNameFilter "Modern_*" -ListNames "MyList" -OutputPath schema-export.json
#>

[CmdletBinding()]
param(
    [string]$SiteUrl,

    [string]$ConfigPath = (Join-Path $PSScriptRoot "..\..\..\config.psd1"),

    [string]$ClientId,

    [string]$TenantId,

    [string]$TenantAdminUrl,

    [Parameter(Mandatory = $true)]
    [ValidateSet("Lists", "ListFields", "LibraryFiles", "ContentTypes")]
    [string]$Mode,

    [string]$ListName,

    [string[]]$FieldNames,

    [string]$ContentTypeNameFilter = "*",

    [string[]]$ListNames,

    [Parameter(Mandatory = $true)]
    [string]$OutputPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "Get-WorkbenchConnectionConfig.ps1")

function Write-JsonOutput {
    param($Object, [string]$Path)
    $Object | ConvertTo-Json -Depth 10 | Set-Content -Path $Path -Encoding UTF8
}

if ($Mode -in @("ListFields", "LibraryFiles") -and -not $ListName) {
    throw "-ListName is required for -Mode $Mode."
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
    switch ($Mode) {
        "Lists" {
            # Source: export-sharepoint-inventory.ps1 / export-sharepoint-inventory-custom.ps1
            # (non-on-prem-specific value: list/library enumeration with counts).
            $lists = Get-PnPList -Includes ItemCount, Hidden, BaseType, ContentTypesEnabled, HasUniqueRoleAssignments
            $records = foreach ($l in $lists) {
                [pscustomobject]@{
                    Title                    = $l.Title
                    ItemCount                = $l.ItemCount
                    IsLibrary                = ($l.BaseType -eq "DocumentLibrary")
                    Hidden                   = $l.Hidden
                    ContentTypesEnabled      = $l.ContentTypesEnabled
                    HasUniqueRoleAssignments = $l.HasUniqueRoleAssignments
                }
            }
            Write-JsonOutput -Object @($records) -Path $OutputPath
            Write-Host "Wrote $($records.Count) list/library record(s) to $OutputPath" -ForegroundColor Green
        }

        "ListFields" {
            # Source: export-persons-picture-description.ps1, generalized from the
            # hardcoded "Persons"/"Comment" list+field to -ListName/-FieldNames.
            $allFields = Get-PnPField -List $ListName
            $selected = if ($FieldNames) {
                $allFields | Where-Object { $FieldNames -contains $_.InternalName }
            } else {
                $allFields | Where-Object { -not $_.Hidden }
            }
            $records = foreach ($f in $selected) {
                [pscustomobject]@{
                    InternalName = $f.InternalName
                    Title        = $f.Title
                    TypeAsString = $f.TypeAsString
                    Hidden       = $f.Hidden
                    Required     = $f.Required
                }
            }
            Write-JsonOutput -Object @($records) -Path $OutputPath
            Write-Host "Wrote $($records.Count) field record(s) for list '$ListName' to $OutputPath" -ForegroundColor Green
        }

        "LibraryFiles" {
            # Source: export-images-library-inventory.ps1, generalized from the
            # hardcoded "Images1" library to -ListName.
            $items = @(Get-PnPListItem -List $ListName -PageSize 500)
            $files = @($items | Where-Object { $_.FileSystemObjectType -eq "File" })
            $records = foreach ($file in $files) {
                [pscustomobject]@{
                    FileName    = $file.FieldValues["FileLeafRef"]
                    RelativeUrl = $file.FieldValues["FileRef"]
                }
            }
            Write-JsonOutput -Object @($records) -Path $OutputPath
            Write-Host "Wrote $($records.Count) file record(s) for library '$ListName' to $OutputPath" -ForegroundColor Green
        }

        "ContentTypes" {
            # Source: discover-sandbox-definitions.ps1, generalized from the
            # hardcoded Sandbox/NTT site URLs and "Modern_*"/"*Appearances*"/named-list
            # filters to -SiteUrl/-ContentTypeNameFilter/-ListNames.
            $siteCts = Get-PnPContentType | Where-Object { $_.Name -like $ContentTypeNameFilter }
            $ctDefinitions = foreach ($ct in $siteCts) {
                try {
                    $detailedCt = Get-PnPContentType -Identity $ct.Name
                    $fieldLinks = Get-PnPProperty -ClientObject $detailedCt -Property FieldLinks
                    $fieldsList = foreach ($fl in $fieldLinks) {
                        [pscustomobject]@{ Name = $fl.Name; Id = $fl.Id }
                    }
                    [pscustomobject]@{
                        Name        = $ct.Name
                        Id          = $ct.Id.ToString()
                        Group       = $ct.Group
                        Description = $ct.Description
                        Fields      = @($fieldsList)
                    }
                } catch {
                    Write-Warning "Could not retrieve content type $($ct.Name): $($_.Exception.Message)"
                }
            }

            $listDefinitions = foreach ($listTitle in $ListNames) {
                try {
                    $list = Get-PnPList -Identity $listTitle -ErrorAction Stop
                    $fields = Get-PnPField -List $list
                    $listCts = Get-PnPContentType -List $list

                    $fieldsList = foreach ($f in $fields) {
                        if (-not $f.Hidden) {
                            [pscustomobject]@{ Title = $f.Title; InternalName = $f.InternalName; Type = $f.TypeAsString }
                        }
                    }
                    $listCtList = foreach ($ct in $listCts) {
                        [pscustomobject]@{ Name = $ct.Name; Id = $ct.Id.ToString() }
                    }

                    [pscustomobject]@{
                        Title        = $list.Title
                        BaseType     = $list.BaseType.ToString()
                        ContentTypes = @($listCtList)
                        Fields       = @($fieldsList)
                    }
                } catch {
                    Write-Warning "Could not fetch list $listTitle : $($_.Exception.Message)"
                }
            }

            $result = [pscustomobject]@{
                SiteContentTypes = @($ctDefinitions)
                Lists            = @($listDefinitions)
            }
            Write-JsonOutput -Object $result -Path $OutputPath
            Write-Host "Wrote $(@($ctDefinitions).Count) content type(s) and $(@($listDefinitions).Count) list schema(s) to $OutputPath" -ForegroundColor Green
        }
    }
} finally {
    Disconnect-PnPOnline -ErrorAction SilentlyContinue
}
