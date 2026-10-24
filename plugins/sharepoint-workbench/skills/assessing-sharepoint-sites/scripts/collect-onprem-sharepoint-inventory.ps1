<#
.SYNOPSIS
Collects a full site inventory (or a fast item/storage count summary) from a
legacy on-premises SharePoint 2016 site via REST + Windows-credential auth.

.DESCRIPTION
On-prem SharePoint (unlike modern SPO) has no Entra app-registration path in
general use here, so this script authenticates via NTLM/Kerberos --
Invoke-RestMethod with -UseDefaultCredentials or an explicit -Credential --
not Connect-PnPOnline. This is a deliberate divergence from this repo's
standard PnP.PowerShell auth convention, required because the target is
on-prem SP2016.

Two modes:

  Full inventory (default). Recursively crawls the site and every sub-web,
  exporting per-web site columns, content types, permissions, workflows,
  master pages, and per-list/library fields, content types, views,
  permissions, workflows, form-customization detection, and (for wiki-page
  libraries) a page scan that flags legacy Content Editor / Script Editor
  web parts. Writes one JSON/CSV pair per artifact under raw_exports/<web
  key>/..., plus cross-site summary files and a customization audit under
  raw_exports/summary/.

  -QuickCountsOnly. Skips the full crawl and web recursion; queries only the
  root site's lists/libraries for item counts and (for libraries) storage
  size, plus site-collection storage usage. Writes a single CSV. Use this
  for a fast size/scope estimate before committing to a full crawl.

Never silently produces empty/fake success: failed REST calls emit
Write-Warning and the affected record set is empty, not fabricated.

.PARAMETER SiteUrl
The on-prem SP2016 site to crawl. Required (no hardcoded default).

.PARAMETER OutputDir
Directory to write outputs under. Required for full-inventory mode (creates
raw_exports/ beneath it). For -QuickCountsOnly, the file to write the
summary CSV to.

.PARAMETER UseDefaultCredentials
Use the current Windows session (Kerberos/NTLM pass-through). Requires VPN /
domain-joined. Without this switch, a credential dialog/prompt is shown.

.PARAMETER IncludeHidden
Include hidden lists/libraries in the crawl.

.PARAMETER IncludeSystemLists
Include built-in system lists (Site Assets, Style Library, etc.) in the crawl.

.PARAMETER IncludeBuiltinFields
Include hidden/built-in fields in field exports (default: user-visible fields only).

.PARAMETER SkipPermissions
Skip role-assignment (permissions) collection.

.PARAMETER QuickCountsOnly
Run the fast item/storage count summary instead of the full crawl.

.EXAMPLE
.\collect-onprem-sharepoint-inventory.ps1 -SiteUrl "https://sp2016.example.org/sites/Legacy" -OutputDir .\inventory -UseDefaultCredentials

.EXAMPLE
.\collect-onprem-sharepoint-inventory.ps1 -SiteUrl "https://sp2016.example.org/sites/Legacy" -OutputDir .\quick-counts.csv -QuickCountsOnly -UseDefaultCredentials
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$SiteUrl,

    [Parameter(Mandatory = $true)]
    [string]$OutputDir,

    [switch]$UseDefaultCredentials,
    [switch]$IncludeHidden,
    [switch]$IncludeSystemLists,
    [switch]$IncludeBuiltinFields,
    [switch]$SkipPermissions,
    [switch]$QuickCountsOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# ─────────────────────────────────────────────
# Output helpers
# ─────────────────────────────────────────────

function Ensure-Directory {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { New-Item -ItemType Directory -Path $Path -Force | Out-Null }
}

function Get-SafeName {
    param([string]$Name)
    if ([string]::IsNullOrWhiteSpace($Name)) { return "_blank" }
    $invalid = [System.IO.Path]::GetInvalidFileNameChars()
    $safe = $Name
    foreach ($char in $invalid) { $safe = $safe.Replace($char, "_") }
    $safe = $safe -replace '\s+', '_' -replace '_{2,}', '_'
    $safe = $safe.Trim('_')
    if ($safe.Length -gt 120) { $safe = $safe.Substring(0, 120) }
    return $safe
}

function Write-JsonFile {
    param($Object, [string]$Path)
    $json = $Object | ConvertTo-Json -Depth 20
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $json, $utf8NoBom)
}

function Write-CsvFile {
    param($Object, [string]$Path)
    if ($null -eq $Object -or @($Object).Count -eq 0) {
        @() | Export-Csv -Path $Path -NoTypeInformation -Encoding UTF8
        return
    }
    @($Object) | Export-Csv -Path $Path -NoTypeInformation -Encoding UTF8
}

function Get-RelativeWebKey {
    param([string]$WebUrl)
    $rel = ([Uri]$WebUrl).AbsolutePath.Trim('/')
    if ([string]::IsNullOrWhiteSpace($rel)) { return "root" }
    return (Get-SafeName $rel)
}

function Get-SystemListTitleSet {
    return @(
        "Access Requests", "App Packages", "appdata", "appfiles", "Composed Looks",
        "Content and Structure Reports", "Content type publishing error log", "Converted Forms",
        "Device Channels", "Form Templates", "List Template Gallery", "Long Running Operation Status",
        "Maintenance Log Library", "MicroFeed", "Relationships List", "Reusable Content", "Site Assets",
        "Site Collection Documents", "Site Collection Images", "Site Pages", "Solution Gallery",
        "Style Library", "TaxonomyHiddenList", "Theme Gallery", "Translation Packages",
        "User Information List", "Web Part Gallery", "wfpub", "Workflow History", "Workflow Tasks"
    )
}

# ─────────────────────────────────────────────
# Auth + REST
# ─────────────────────────────────────────────

$script:spHeaders    = @{ "Accept" = "application/json;odata=verbose" }
$script:spCredential = $null
$script:spUseDefault = [bool]$UseDefaultCredentials

function Invoke-SPRest {
    param([string]$Url)
    try {
        if ($script:spUseDefault) {
            return Invoke-RestMethod -Uri $Url -Headers $script:spHeaders -UseDefaultCredentials -ErrorAction Stop
        }
        if ($null -eq $script:spCredential) {
            $script:spCredential = Get-Credential -Message "Credentials for $SiteUrl"
        }
        return Invoke-RestMethod -Uri $Url -Headers $script:spHeaders -Credential $script:spCredential -ErrorAction Stop
    } catch {
        Write-Warning "REST call failed: $Url — $($_.Exception.Message)"
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

function Download-SPFile {
    param([string]$WebUrl, [string]$ServerRelativeUrl, [string]$LocalPath)
    try {
        $encodedUrl = [Uri]::EscapeDataString($ServerRelativeUrl.Replace("'", "''"))
        $fileUrl = "$WebUrl/_api/web/GetFileByServerRelativeUrl('$encodedUrl')/`$value"
        if ($script:spUseDefault) {
            Invoke-RestMethod -Uri $fileUrl -Headers $script:spHeaders -UseDefaultCredentials -OutFile $LocalPath -ErrorAction Stop
        } else {
            Invoke-RestMethod -Uri $fileUrl -Headers $script:spHeaders -Credential $script:spCredential -OutFile $LocalPath -ErrorAction Stop
        }
        return $true
    } catch {
        Write-Warning "Failed to download file '$ServerRelativeUrl': $($_.Exception.Message)"
        return $false
    }
}

# ─────────────────────────────────────────────
# Record builders
# ─────────────────────────────────────────────

function Get-FieldRecords {
    param($Fields, [string]$WebUrl, [string]$ParentType, [string]$ParentTitle = "")
    $records = @()
    foreach ($f in $Fields) {
        if (-not $IncludeBuiltinFields -and $f.Hidden) { continue }
        $lookupList      = if ($f.PSObject.Properties['LookupList'])      { $f.LookupList }      else { $null }
        $lookupField     = if ($f.PSObject.Properties['LookupField'])     { $f.LookupField }     else { $null }
        $customFormatter = if ($f.PSObject.Properties['CustomFormatter']) { $f.CustomFormatter } else { $null }
        $records += [PSCustomObject]@{
            WebUrl              = $WebUrl
            ParentType          = $ParentType
            ParentTitle         = $ParentTitle
            InternalName        = $f.InternalName
            Title               = $f.Title
            TypeAsString        = $f.TypeAsString
            Group               = $f.Group
            Hidden              = $f.Hidden
            ReadOnlyField       = $f.ReadOnlyField
            Required            = $f.Required
            EnforceUniqueValues = $f.EnforceUniqueValues
            Indexed             = $f.Indexed
            Sealed              = $f.Sealed
            StaticName          = $f.StaticName
            DefaultValue        = $f.DefaultValue
            Description         = $f.Description
            LookupList          = $lookupList
            LookupField         = $lookupField
            CustomFormatter     = $customFormatter
        }
    }
    return , $records
}

function Get-ContentTypeRecords {
    param($ContentTypes, [string]$WebUrl, [string]$ParentType, [string]$ParentTitle = "")
    $records = @()
    foreach ($ct in $ContentTypes) {
        $records += [PSCustomObject]@{
            WebUrl      = $WebUrl
            ParentType  = $ParentType
            ParentTitle = $ParentTitle
            Name        = $ct.Name
            StringId    = $ct.StringId
            Group       = $ct.Group
            Description = $ct.Description
            Hidden      = $ct.Hidden
            ReadOnly    = $ct.ReadOnly
            Sealed      = $ct.Sealed
        }
    }
    return , $records
}

function Get-ViewRecords {
    param($Views, [string]$WebUrl, [string]$ListTitle, [string]$OdataListTitle)
    $records = @()
    foreach ($v in $Views) {
        $viewFields = ""
        try {
            $vfResult = Invoke-SPRest -Url "$WebUrl/_api/web/lists/getbytitle('$OdataListTitle')/views(guid'$($v.Id)')/viewfields"
            if ($vfResult -and $vfResult.d.Items.results) { $viewFields = ($vfResult.d.Items.results -join "; ") }
        } catch {}
        $records += [PSCustomObject]@{
            WebUrl            = $WebUrl
            ListTitle         = $ListTitle
            Title             = $v.Title
            ServerRelativeUrl = $v.ServerRelativeUrl
            DefaultView       = $v.DefaultView
            Hidden            = $v.Hidden
            Paged             = $v.Paged
            RowLimit          = $v.RowLimit
            ViewQuery         = $v.ViewQuery
            ViewFields        = $viewFields
        }
    }
    return , $records
}

function Get-PermissionRecords {
    param([string]$WebUrl, [string]$ObjectType, [string]$ObjectTitle, [string]$ListTitle = "")
    $records = @()
    if ($SkipPermissions) { return , $records }
    try {
        if ($ListTitle) {
            $encodedTitle = [Uri]::EscapeDataString($ListTitle.Replace("'", "''"))
            $raUrl = "$WebUrl/_api/web/lists/getbytitle('$encodedTitle')/roleassignments?`$expand=Member,RoleDefinitionBindings"
        } else {
            $raUrl = "$WebUrl/_api/web/roleassignments?`$expand=Member,RoleDefinitionBindings"
        }
        $raResult = Invoke-SPRest -Url $raUrl
        if ($null -eq $raResult) { return , $records }
        foreach ($ra in $raResult.d.results) {
            $roles = ($ra.RoleDefinitionBindings.results | ForEach-Object { $_.Name }) -join "; "
            $records += [PSCustomObject]@{
                WebUrl           = $WebUrl
                ObjectType       = $ObjectType
                ObjectTitle      = $ObjectTitle
                PrincipalTitle   = $ra.Member.Title
                PrincipalLogin   = $ra.Member.LoginName
                PrincipalType    = $ra.Member.PrincipalType
                PermissionLevels = $roles
            }
        }
    } catch {
        Write-Warning "Could not get permissions for $ObjectType '$ObjectTitle': $($_.Exception.Message)"
    }
    return , $records
}

function Get-WorkflowRecords {
    param([string]$WebUrl, [string]$ParentType, [string]$ParentTitle = "", [string]$ListTitle = "")
    $records = @()
    try {
        if ($ListTitle) {
            $encodedTitle = [Uri]::EscapeDataString($ListTitle.Replace("'", "''"))
            $wfUrl = "$WebUrl/_api/web/lists/getbytitle('$encodedTitle')/WorkflowAssociations"
        } else {
            $wfUrl = "$WebUrl/_api/web/WorkflowAssociations"
        }
        $wfResult = Invoke-SPRest -Url $wfUrl
        if ($null -eq $wfResult) { return , $records }
        foreach ($wf in $wfResult.d.results) {
            $records += [PSCustomObject]@{
                WebUrl          = $WebUrl
                ParentType      = $ParentType
                ParentTitle     = $ParentTitle
                Name            = $wf.Name
                Id              = $wf.Id
                InternalName    = $wf.InternalName
                AllowManual     = $wf.AllowManual
                AutoStartCreate = $wf.AutoStartCreate
                AutoStartChange = $wf.AutoStartChange
                Description     = $wf.Description
            }
        }
    } catch {
        Write-Warning "Could not get workflows for $ParentType '$ParentTitle': $($_.Exception.Message)"
    }
    return , $records
}

function Get-ListFormRecords {
    <#
    Returns the New/Edit/Display form URLs for a list and flags any that appear
    customized (server-relative URL does not match the standard NewForm.aspx /
    EditForm.aspx / DispForm.aspx pattern) -- detects InfoPath/custom-ASPX form
    replacements.
    #>
    param([string]$WebUrl, [string]$ListTitle)
    $records = @()
    try {
        $encodedTitle = [Uri]::EscapeDataString($ListTitle.Replace("'", "''"))
        $result = Invoke-SPRest -Url "$WebUrl/_api/web/lists/getbytitle('$encodedTitle')/forms"
        if ($null -eq $result) { return , $records }
        foreach ($form in $result.d.results) {
            $formTypeName = switch ($form.FormType) {
                1 { "DisplayForm" } 2 { "EditForm" } 3 { "NewForm" } default { "Other($($form.FormType))" }
            }
            $isCustomized = ($form.ServerRelativeUrl -notmatch '/(New|Edit|Disp)Form\.aspx(\?.*)?$')
            $records += [PSCustomObject]@{
                WebUrl            = $WebUrl
                ListTitle         = $ListTitle
                FormType          = $formTypeName
                ServerRelativeUrl = $form.ServerRelativeUrl
                IsCustomized      = $isCustomized
            }
        }
    } catch {
        Write-Warning "Could not get forms for '$ListTitle': $($_.Exception.Message)"
    }
    return , $records
}

function Get-ListStorageBytes {
    param([string]$WebUrl, [string]$ListTitle, [string]$RootFolderServerRelativeUrl, [string]$EncodedListTitle)
    $sizeInBytes = [int64]0
    try {
        $encodedRelUrl = [Uri]::EscapeDataString($RootFolderServerRelativeUrl.Replace("'", "''"))
        $metricsResult = Invoke-SPRest -Url "$WebUrl/_api/web/GetFolderByServerRelativeUrl('$encodedRelUrl')?`$select=StorageMetrics&`$expand=StorageMetrics"
        if ($metricsResult -and $metricsResult.d.StorageMetrics) {
            $sizeInBytes = [int64]($metricsResult.d.StorageMetrics.TotalSize ?? $metricsResult.d.StorageMetrics.TotalFileStreamSize ?? 0)
        }
    } catch {
        Write-Warning "Could not get storage metrics for list '$ListTitle': $($_.Exception.Message)"
    }
    return $sizeInBytes
}

# ─────────────────────────────────────────────
# Per-web crawl
# ─────────────────────────────────────────────

function Get-WebInventory {
    param([string]$WebUrl, [string]$WebTitle, [string]$RawBaseFolder)

    $webKey = Get-RelativeWebKey -WebUrl $WebUrl
    Write-Host "Processing web: $WebUrl" -ForegroundColor Green

    $webRawRoot         = Join-Path $RawBaseFolder $webKey
    $siteColumnsFolder  = Join-Path $webRawRoot "site_columns"
    $contentTypesFolder = Join-Path $webRawRoot "content_types"
    $viewsFolder        = Join-Path $webRawRoot "views"
    $permissionsFolder  = Join-Path $webRawRoot "permissions"
    $workflowsFolder    = Join-Path $webRawRoot "workflows"
    $masterPagesFolder  = Join-Path $webRawRoot "master_pages"
    $rawFolder          = Join-Path $webRawRoot "raw_exports"
    $listsFolder        = Join-Path $webRawRoot "lists"
    $libsFolder         = Join-Path $webRawRoot "document_libraries"

    foreach ($folder in @($webRawRoot, $siteColumnsFolder, $contentTypesFolder, $viewsFolder, $permissionsFolder,
            $workflowsFolder, $masterPagesFolder, $rawFolder, $listsFolder, $libsFolder)) {
        Ensure-Directory $folder
    }

    # Site columns
    $rawFields = Get-SPRestAll -Url "$WebUrl/_api/web/fields"
    $siteColumnRecords = Get-FieldRecords -Fields $rawFields -WebUrl $WebUrl -ParentType "Web" -ParentTitle $WebTitle
    Write-CsvFile  -Object $siteColumnRecords -Path (Join-Path $siteColumnsFolder "site_columns.csv")
    Write-JsonFile -Object $siteColumnRecords -Path (Join-Path $siteColumnsFolder "site_columns.json")

    # Web content types
    $rawCts = Get-SPRestAll -Url "$WebUrl/_api/web/contenttypes"
    $webCtRecords = Get-ContentTypeRecords -ContentTypes $rawCts -WebUrl $WebUrl -ParentType "Web" -ParentTitle $WebTitle
    Write-CsvFile  -Object $webCtRecords -Path (Join-Path $contentTypesFolder "content_types.csv")
    Write-JsonFile -Object $webCtRecords -Path (Join-Path $contentTypesFolder "content_types.json")

    # Web permissions
    $webPermissionRecords = Get-PermissionRecords -WebUrl $WebUrl -ObjectType "Web" -ObjectTitle $WebTitle
    if (-not $SkipPermissions) {
        Write-CsvFile  -Object $webPermissionRecords -Path (Join-Path $permissionsFolder "web_permissions.csv")
        Write-JsonFile -Object $webPermissionRecords -Path (Join-Path $permissionsFolder "web_permissions.json")
    }

    # Web workflows
    $webWorkflowRecords = Get-WorkflowRecords -WebUrl $WebUrl -ParentType "Web" -ParentTitle $WebTitle
    Write-CsvFile  -Object $webWorkflowRecords -Path (Join-Path $workflowsFolder "web_workflows.csv")
    Write-JsonFile -Object $webWorkflowRecords -Path (Join-Path $workflowsFolder "web_workflows.json")

    # Master pages discovery + download
    $webInfo = Invoke-SPRest -Url "$WebUrl/_api/web?`$select=MasterUrl,CustomMasterUrl,ServerRelativeUrl,HasUniqueRoleAssignments,Description,LastItemModifiedDate"
    if ($webInfo) {
        $masterRecord = [PSCustomObject]@{ WebUrl = $WebUrl; MasterUrl = $webInfo.d.MasterUrl; CustomMasterUrl = $webInfo.d.CustomMasterUrl }
        Write-JsonFile -Object $masterRecord -Path (Join-Path $masterPagesFolder "web_master_pages.json")
        Write-CsvFile  -Object @($masterRecord) -Path (Join-Path $masterPagesFolder "web_master_pages.csv")

        $galleryRelPath = "$($webInfo.d.ServerRelativeUrl.TrimEnd('/'))/_catalogs/masterpage"
        $encodedGallery = [Uri]::EscapeDataString($galleryRelPath.Replace("'", "''"))
        $galleryFiles = Get-SPRestAll -Url "$WebUrl/_api/web/GetFolderByServerRelativeUrl('$encodedGallery')/Files"
        foreach ($file in $galleryFiles) {
            if ($file.Name -match '\.(master|html|css|js)$') {
                Download-SPFile -WebUrl $WebUrl -ServerRelativeUrl $file.ServerRelativeUrl -LocalPath (Join-Path $masterPagesFolder $file.Name) | Out-Null
            }
        }

        # Legacy SP2010 workflow publication files (wfpub)
        try {
            $wfpubRelPath = "$($webInfo.d.ServerRelativeUrl.TrimEnd('/'))/wfpub"
            $encodedWfpub = [Uri]::EscapeDataString($wfpubRelPath.Replace("'", "''"))
            $wfFolders = Get-SPRestAll -Url "$WebUrl/_api/web/GetFolderByServerRelativeUrl('$encodedWfpub')/Folders"
            foreach ($folder in $wfFolders) {
                $wfLocalFolder = Join-Path $workflowsFolder (Get-SafeName $folder.Name)
                Ensure-Directory $wfLocalFolder
                $wfFiles = Get-SPRestAll -Url "$WebUrl/_api/web/GetFolderByServerRelativeUrl('$([Uri]::EscapeDataString($folder.ServerRelativeUrl.Replace("'", "''")))')/Files"
                foreach ($file in $wfFiles) {
                    Download-SPFile -WebUrl $WebUrl -ServerRelativeUrl $file.ServerRelativeUrl -LocalPath (Join-Path $wfLocalFolder $file.Name) | Out-Null
                }
            }
        } catch {
            Write-Warning "Could not read wfpub workflows folder: $($_.Exception.Message)"
        }
    }

    # Lists and libraries
    $listsUrl = "$WebUrl/_api/web/lists?" +
    "`$select=Title,Hidden,BaseType,BaseTemplate,ItemCount,EnableVersioning," +
    "EnableMinorVersions,ForceCheckout,DefaultViewUrl,HasUniqueRoleAssignments," +
    "ContentTypesEnabled,ClientSideComponentId,ClientSideComponentProperties," +
    "RootFolder/ServerRelativeUrl&`$expand=RootFolder"
    $rawLists = Get-SPRestAll -Url $listsUrl

    $systemTitles = Get-SystemListTitleSet
    if (-not $IncludeHidden) { $rawLists = $rawLists | Where-Object { -not $_.Hidden } }
    if (-not $IncludeSystemLists) { $rawLists = $rawLists | Where-Object { $systemTitles -notcontains $_.Title } }

    $listInventory        = @()
    $allPermissionRecords = @()
    $allViewRecordsForWeb = @()
    $allFormRecordsForWeb = @()
    $allWikiPagesForWeb   = @()
    $allLegacyWebParts    = @()

    foreach ($list in $rawLists) {
        $isLibrary  = ($list.BaseType -eq 1)
        $objectType = if ($isLibrary) { "Library" } else { "List" }
        $categoryFolder = if ($isLibrary) { $libsFolder } else { $listsFolder }
        $listFolder = Join-Path $categoryFolder (Get-SafeName $list.Title)
        Ensure-Directory $listFolder

        $encodedTitle = [Uri]::EscapeDataString($list.Title.Replace("'", "''"))

        $rawListFields = Get-SPRestAll -Url "$WebUrl/_api/web/lists/getbytitle('$encodedTitle')/fields"
        $fieldRecords  = Get-FieldRecords -Fields $rawListFields -WebUrl $WebUrl -ParentType $objectType -ParentTitle $list.Title

        $rawListCts = Get-SPRestAll -Url "$WebUrl/_api/web/lists/getbytitle('$encodedTitle')/contenttypes"
        $ctRecords  = Get-ContentTypeRecords -ContentTypes $rawListCts -WebUrl $WebUrl -ParentType $objectType -ParentTitle $list.Title

        $rawViews    = Get-SPRestAll -Url "$WebUrl/_api/web/lists/getbytitle('$encodedTitle')/views"
        $viewRecords = Get-ViewRecords -Views $rawViews -WebUrl $WebUrl -ListTitle $list.Title -OdataListTitle $encodedTitle
        $allViewRecordsForWeb += $viewRecords

        $listPermissionRecords = Get-PermissionRecords -WebUrl $WebUrl -ObjectType $objectType -ObjectTitle $list.Title -ListTitle $list.Title
        $allPermissionRecords += $listPermissionRecords

        $listWorkflowRecords = Get-WorkflowRecords -WebUrl $WebUrl -ParentType $objectType -ParentTitle $list.Title -ListTitle $list.Title

        $sizeInBytes = [int64]0
        if ($isLibrary) {
            $sizeInBytes = Get-ListStorageBytes -WebUrl $WebUrl -ListTitle $list.Title -RootFolderServerRelativeUrl $list.RootFolder.ServerRelativeUrl -EncodedListTitle $encodedTitle
        }

        $spfxId    = if ($list.PSObject.Properties['ClientSideComponentId'])         { $list.ClientSideComponentId }         else { $null }
        $spfxProps = if ($list.PSObject.Properties['ClientSideComponentProperties']) { $list.ClientSideComponentProperties } else { $null }

        $listRecord = [PSCustomObject]@{
            WebUrl                        = $WebUrl
            WebTitle                      = $WebTitle
            WebKey                        = $webKey
            Title                         = $list.Title
            Hidden                        = $list.Hidden
            BaseType                      = $list.BaseType
            BaseTemplate                  = $list.BaseTemplate
            IsLibrary                     = $isLibrary
            ItemCount                     = $list.ItemCount
            SizeInBytes                   = $sizeInBytes
            SizeInMB                      = [math]::Round($sizeInBytes / 1MB, 2)
            SizeInGB                      = [math]::Round($sizeInBytes / 1GB, 4)
            EnableVersioning              = $list.EnableVersioning
            EnableMinorVersions           = $list.EnableMinorVersions
            ForceCheckout                 = $list.ForceCheckout
            ContentTypesEnabled           = $list.ContentTypesEnabled
            DefaultViewUrl                = $list.DefaultViewUrl
            RootFolderServerRelative      = $list.RootFolder.ServerRelativeUrl
            HasUniqueRoleAssignments      = $list.HasUniqueRoleAssignments
            ClientSideComponentId         = $spfxId
            ClientSideComponentProperties = $spfxProps
            HasSPFxCustomizer             = (-not [string]::IsNullOrWhiteSpace($spfxId) -and $spfxId -ne '00000000-0000-0000-0000-000000000000')
        }
        $listInventory += $listRecord
        $listSafe = Get-SafeName $list.Title

        Write-JsonFile -Object $listRecord    -Path (Join-Path $listFolder "definition.json")
        Write-CsvFile  -Object @($listRecord) -Path (Join-Path $listFolder "definition.csv")
        Write-JsonFile -Object $fieldRecords  -Path (Join-Path $listFolder "fields.json")
        Write-CsvFile  -Object $fieldRecords  -Path (Join-Path $listFolder "fields.csv")
        Write-JsonFile -Object $ctRecords     -Path (Join-Path $listFolder "content_types.json")
        Write-CsvFile  -Object $ctRecords     -Path (Join-Path $listFolder "content_types.csv")
        Write-JsonFile -Object $viewRecords   -Path (Join-Path $listFolder "views.json")
        Write-CsvFile  -Object $viewRecords   -Path (Join-Path $listFolder "views.csv")
        Write-CsvFile  -Object $viewRecords   -Path (Join-Path $viewsFolder "$listSafe.views.csv")
        Write-JsonFile -Object $viewRecords   -Path (Join-Path $viewsFolder "$listSafe.views.json")

        if (-not $SkipPermissions) {
            Write-JsonFile -Object $listPermissionRecords -Path (Join-Path $listFolder "permissions.json")
            Write-CsvFile  -Object $listPermissionRecords -Path (Join-Path $listFolder "permissions.csv")
            Write-CsvFile  -Object $listPermissionRecords -Path (Join-Path $permissionsFolder "$listSafe.permissions.csv")
            Write-JsonFile -Object $listPermissionRecords -Path (Join-Path $permissionsFolder "$listSafe.permissions.json")
        }

        Write-CsvFile  -Object $listWorkflowRecords -Path (Join-Path $listFolder "workflows.csv")
        Write-JsonFile -Object $listWorkflowRecords -Path (Join-Path $listFolder "workflows.json")

        $listFormRecords = Get-ListFormRecords -WebUrl $WebUrl -ListTitle $list.Title
        $allFormRecordsForWeb += $listFormRecords
        Write-JsonFile -Object $listFormRecords -Path (Join-Path $listFolder "forms.json")
        Write-CsvFile  -Object $listFormRecords -Path (Join-Path $listFolder "forms.csv")

        # Wiki/page scan: flags legacy Content Editor / Script Editor web parts.
        # Matches BaseTemplate 119 (Wiki Page Library) or the common Pages/Site Pages titles.
        $wikiPageRecords      = @()
        $legacyWebPartRecords = @()
        $isWikiLib = ($list.BaseTemplate -eq 119 -or $list.Title -eq "Pages" -or $list.Title -eq "Site Pages")
        if ($isWikiLib) {
            Write-Host "  - Scanning wiki library '$($list.Title)' ($($list.ItemCount) items)..." -ForegroundColor DarkGray
            try {
                $encodedPages = [Uri]::EscapeDataString($list.RootFolder.ServerRelativeUrl.Replace("'", "''"))
                $pageFiles = Get-SPRestAll -Url "$WebUrl/_api/web/GetFolderByServerRelativeUrl('$encodedPages')/Files"
                foreach ($file in $pageFiles) {
                    if ($file.Name -notmatch '\.aspx$') { continue }
                    $hasCewp = $false; $hasSewp = $false
                    try {
                        $encodedFileUrl = [Uri]::EscapeDataString($file.ServerRelativeUrl.Replace("'", "''"))
                        $fileContentUrl = "$WebUrl/_api/web/GetFileByServerRelativeUrl('$encodedFileUrl')/`$value"
                        $pageContent = if ($script:spUseDefault) {
                            Invoke-RestMethod -Uri $fileContentUrl -UseDefaultCredentials -Headers $script:spHeaders -ErrorAction Stop
                        } else {
                            Invoke-RestMethod -Uri $fileContentUrl -Credential $script:spCredential -Headers $script:spHeaders -ErrorAction Stop
                        }
                        $hasCewp = ($pageContent -match 'ContentEditorWebPart')
                        $hasSewp = ($pageContent -match 'ScriptEditorWebPart')
                    } catch {
                        Write-Warning "    Could not read page '$($file.Name)': $($_.Exception.Message)"
                    }
                    $wikiPageRecords += [PSCustomObject]@{
                        WebUrl = $WebUrl; LibraryTitle = $list.Title; BaseTemplate = $list.BaseTemplate
                        FileName = $file.Name; ServerRelativeUrl = $file.ServerRelativeUrl
                        HasContentEditor = $hasCewp; HasScriptEditor = $hasSewp; IsCustomized = ($hasCewp -or $hasSewp)
                    }
                    if ($hasCewp -or $hasSewp) {
                        $legacyWebPartRecords += [PSCustomObject]@{
                            WebUrl = $WebUrl; LibraryTitle = $list.Title; FileName = $file.Name
                            ServerRelativeUrl = $file.ServerRelativeUrl; HasContentEditor = $hasCewp; HasScriptEditor = $hasSewp
                        }
                    }
                }
                if ($wikiPageRecords.Count -gt 0) {
                    Write-CsvFile  -Object $wikiPageRecords -Path (Join-Path $listFolder "wiki_pages.csv")
                    Write-JsonFile -Object $wikiPageRecords -Path (Join-Path $listFolder "wiki_pages.json")
                }
                if ($legacyWebPartRecords.Count -gt 0) {
                    Write-CsvFile  -Object $legacyWebPartRecords -Path (Join-Path $listFolder "legacy_webparts.csv")
                    Write-JsonFile -Object $legacyWebPartRecords -Path (Join-Path $listFolder "legacy_webparts.json")
                }
            } catch {
                Write-Warning "Could not scan wiki library '$($list.Title)': $($_.Exception.Message)"
            }
        }
        $allWikiPagesForWeb += $wikiPageRecords
        $allLegacyWebParts  += $legacyWebPartRecords

        $customFormattedFields = @($fieldRecords | Where-Object { -not [string]::IsNullOrWhiteSpace($_.CustomFormatter) })
        Write-JsonFile -Object ([PSCustomObject]@{
                Definition            = $listRecord
                Fields                = $fieldRecords
                ContentTypes          = $ctRecords
                Views                 = $viewRecords
                Permissions           = $listPermissionRecords
                Workflows             = $listWorkflowRecords
                Forms                 = $listFormRecords
                CustomFormattedFields = $customFormattedFields
            }) -Path (Join-Path $rawFolder ("{0}.full.json" -f $listSafe))

        $hasCustomForm = @($listFormRecords | Where-Object { $_.IsCustomized }).Count -gt 0
        if ($hasCustomForm -or $listRecord.HasSPFxCustomizer -or $customFormattedFields.Count -gt 0) {
            Write-Host ("  + $($list.Title) - CUSTOMIZATION DETECTED: CustomForm=$hasCustomForm SPFx=$($listRecord.HasSPFxCustomizer) JsonFormat=$($customFormattedFields.Count -gt 0)") -ForegroundColor Yellow
        } else {
            Write-Host ("  + {0} ({1} fields, {2} views)" -f $list.Title, @($fieldRecords).Count, @($viewRecords).Count) -ForegroundColor DarkGray
        }
    }

    return [PSCustomObject]@{
        WebRecord         = [PSCustomObject]@{
            WebUrl = $WebUrl; WebTitle = $WebTitle; WebKey = $webKey
            HasUniquePermissions = if ($webInfo) { [bool]$webInfo.d.HasUniqueRoleAssignments } else { $false }
            Description = if ($webInfo -and $webInfo.d.Description) { $webInfo.d.Description } else { '' }
            LastModified = if ($webInfo) { $webInfo.d.LastItemModifiedDate } else { '' }
        }
        SiteColumns       = $siteColumnRecords
        WebContentTypes   = $webCtRecords
        WebPermissions    = $webPermissionRecords
        ListsAndLibraries = $listInventory
        ViewRecords       = $allViewRecordsForWeb
        PermissionRecords = $allPermissionRecords
        FormRecords       = $allFormRecordsForWeb
        WikiPages         = $allWikiPagesForWeb
        LegacyWebParts    = $allLegacyWebParts
    }
}

function Get-AllSubWebs {
    param([string]$WebUrl)
    $subWebs = @()
    $result = Invoke-SPRest -Url "$WebUrl/_api/web/webs?`$select=Title,Url,ServerRelativeUrl"
    if ($null -eq $result) { return , $subWebs }
    foreach ($sw in $result.d.results) {
        $swUrl = $sw.Url.TrimEnd('/')
        $subWebs += [PSCustomObject]@{ Url = $swUrl; Title = $sw.Title }
        $subWebs += Get-AllSubWebs -WebUrl $swUrl
    }
    return , $subWebs
}

# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

Write-Host "Testing connection to $SiteUrl ..." -ForegroundColor DarkGray
$testResult = Invoke-SPRest -Url "$SiteUrl/_api/web?`$select=Title,Url,ServerRelativeUrl"
if ($null -eq $testResult) { throw "Could not connect to $SiteUrl" }
$rootTitle = $testResult.d.Title
$rootUrl   = $SiteUrl.TrimEnd('/')
Write-Host "Connected: $rootTitle" -ForegroundColor Green

if ($QuickCountsOnly) {
    # Source: get-source-item-counts.ps1 — fast item/storage count summary, root site only.
    Write-Host "`n=== Quick Item/Storage Counts: $SiteUrl ===" -ForegroundColor Cyan

    $siteStorageResult = Invoke-SPRest -Url "$SiteUrl/_api/site?`$select=Usage"
    $siteCollectionGB = if ($siteStorageResult -and $siteStorageResult.d.Usage) { [math]::Round($siteStorageResult.d.Usage.Storage / 1GB, 3) } else { $null }

    $listsUrl = "$SiteUrl/_api/web/lists?`$select=Title,BaseType,Hidden,ItemCount,RootFolder/ServerRelativeUrl&`$expand=RootFolder"
    $result = Invoke-SPRest -Url $listsUrl
    if (-not $result) { throw "Could not enumerate lists on $SiteUrl" }

    $systemTitles = Get-SystemListTitleSet
    $rows = @()
    foreach ($list in ($result.d.results | Where-Object { -not $_.Hidden -and $systemTitles -notcontains $_.Title })) {
        $isLibrary = ($list.BaseType -eq 1)
        $sizeBytes = if ($isLibrary) { Get-ListStorageBytes -WebUrl $SiteUrl -ListTitle $list.Title -RootFolderServerRelativeUrl $list.RootFolder.ServerRelativeUrl } else { [int64]0 }
        $rows += [PSCustomObject]@{
            Type      = if ($isLibrary) { "Library" } else { "List" }
            Title     = $list.Title
            ItemCount = [int]$list.ItemCount
            SizeGB    = if ($isLibrary) { [math]::Round($sizeBytes / 1GB, 3) } else { $null }
            SizeBytes = if ($isLibrary) { $sizeBytes } else { $null }
        }
    }
    $rows = $rows | Sort-Object Type, Title

    $outDir = Split-Path $OutputDir -Parent
    if ($outDir -and -not (Test-Path $outDir)) { Ensure-Directory $outDir }
    Write-CsvFile -Object $rows -Path $OutputDir

    $lists = @($rows | Where-Object { $_.Type -eq 'List' })
    $libs  = @($rows | Where-Object { $_.Type -eq 'Library' })
    Write-Host "  Lists: $($lists.Count) (total items: $(($lists | Measure-Object -Property ItemCount -Sum).Sum))" -ForegroundColor Green
    Write-Host "  Libraries: $($libs.Count) (total items: $(($libs | Measure-Object -Property ItemCount -Sum).Sum), total size: $([math]::Round(($libs | Measure-Object -Property SizeGB -Sum).Sum, 3)) GB)" -ForegroundColor Green
    if ($siteCollectionGB) { Write-Host "  Site collection storage: $siteCollectionGB GB" -ForegroundColor Green }
    Write-Host "  Written to: $OutputDir" -ForegroundColor DarkGray
    return
}

# Full crawl. Source: export-sharepoint-inventory.ps1 / export-sharepoint-inventory-custom.ps1.
$rawBase       = Join-Path $OutputDir "raw_exports"
$summaryFolder = Join-Path $rawBase "summary"
Ensure-Directory $rawBase
Ensure-Directory $summaryFolder

Write-Host "`nDiscovering webs..." -ForegroundColor Cyan
$allWebs = @([PSCustomObject]@{ Url = $rootUrl; Title = $rootTitle })
try { $allWebs += Get-AllSubWebs -WebUrl $rootUrl } catch { Write-Warning "Could not enumerate sub-webs: $_. Continuing with root only." }
Write-Host ("Found {0} web(s)." -f $allWebs.Count) -ForegroundColor Green

$allWebRecords = @(); $allListRecords = @(); $allViewRecords = @(); $allPermissionRecords = @()
$allSiteColumnRecords = @(); $allContentTypeRecords = @(); $allFormRecords = @()
$allWikiPageRecords = @(); $allLegacyWebPartRecords = @()

foreach ($web in $allWebs) {
    $bundle = Get-WebInventory -WebUrl $web.Url -WebTitle $web.Title -RawBaseFolder $rawBase
    $allWebRecords           += $bundle.WebRecord
    $allListRecords          += $bundle.ListsAndLibraries
    $allViewRecords          += $bundle.ViewRecords
    $allPermissionRecords    += $bundle.PermissionRecords
    $allSiteColumnRecords    += $bundle.SiteColumns
    $allContentTypeRecords   += $bundle.WebContentTypes
    $allFormRecords          += $bundle.FormRecords
    $allWikiPageRecords      += $bundle.WikiPages
    $allLegacyWebPartRecords += $bundle.LegacyWebParts
}

Write-Host "`nWriting summary files..." -ForegroundColor Cyan
Write-CsvFile  -Object $allWebRecords         -Path (Join-Path $summaryFolder "webs.csv")
Write-JsonFile -Object $allWebRecords         -Path (Join-Path $summaryFolder "webs.json")
Write-CsvFile  -Object $allListRecords        -Path (Join-Path $summaryFolder "lists_and_libraries.csv")
Write-JsonFile -Object $allListRecords        -Path (Join-Path $summaryFolder "lists_and_libraries.json")
Write-CsvFile  -Object $allViewRecords        -Path (Join-Path $summaryFolder "all_views.csv")
Write-JsonFile -Object $allViewRecords        -Path (Join-Path $summaryFolder "all_views.json")
Write-CsvFile  -Object $allSiteColumnRecords  -Path (Join-Path $summaryFolder "all_site_columns.csv")
Write-JsonFile -Object $allSiteColumnRecords  -Path (Join-Path $summaryFolder "all_site_columns.json")
Write-CsvFile  -Object $allContentTypeRecords -Path (Join-Path $summaryFolder "all_web_content_types.csv")
Write-JsonFile -Object $allContentTypeRecords -Path (Join-Path $summaryFolder "all_web_content_types.json")
if (-not $SkipPermissions) {
    Write-CsvFile  -Object $allPermissionRecords -Path (Join-Path $summaryFolder "all_permissions.csv")
    Write-JsonFile -Object $allPermissionRecords -Path (Join-Path $summaryFolder "all_permissions.json")
}

# Customization audit — aggregates signals of non-standard forms/customizations.
$listsWithSPFx        = @($allListRecords      | Where-Object { $_.HasSPFxCustomizer })
$listsWithCustomForms = @($allFormRecords      | Where-Object { $_.IsCustomized })
$fieldsWithJsonFmt    = @($allSiteColumnRecords | Where-Object { -not [string]::IsNullOrWhiteSpace($_.CustomFormatter) })
$infoPathLibraries    = @($allListRecords      | Where-Object { $_.Title -eq 'Form Templates' })

$customizationAudit = [PSCustomObject]@{
    GeneratedOn                        = (Get-Date).ToString("s")
    ListsWithCustomFormUrls            = $listsWithCustomForms
    ListsWithCustomFormUrlsCount       = $listsWithCustomForms.Count
    ListsWithSPFxCustomizer            = $listsWithSPFx
    ListsWithSPFxCustomizerCount       = $listsWithSPFx.Count
    SiteColumnsWithJsonFormatting      = $fieldsWithJsonFmt
    SiteColumnsWithJsonFormattingCount = $fieldsWithJsonFmt.Count
    InfoPathFormTemplateLibraries      = $infoPathLibraries
    InfoPathLibraryCount               = $infoPathLibraries.Count
    TotalWikiPages                     = $allWikiPageRecords.Count
    WikiPagesWithLegacyWebParts        = $allLegacyWebPartRecords
    WikiPagesWithLegacyWebPartsCount   = $allLegacyWebPartRecords.Count
    AnyCustomizationDetected           = ($listsWithSPFx.Count -gt 0 -or $listsWithCustomForms.Count -gt 0 -or $fieldsWithJsonFmt.Count -gt 0 -or $infoPathLibraries.Count -gt 0 -or $allLegacyWebPartRecords.Count -gt 0)
}
Write-JsonFile -Object $customizationAudit -Path (Join-Path $summaryFolder "customization_audit.json")
Write-CsvFile  -Object $listsWithCustomForms -Path (Join-Path $summaryFolder "lists_with_custom_forms.csv")
Write-CsvFile  -Object $allWikiPageRecords -Path (Join-Path $summaryFolder "all_wiki_pages.csv")
Write-JsonFile -Object $allWikiPageRecords -Path (Join-Path $summaryFolder "all_wiki_pages.json")
Write-CsvFile  -Object $allLegacyWebPartRecords -Path (Join-Path $summaryFolder "all_legacy_webparts.csv")
Write-JsonFile -Object $allLegacyWebPartRecords -Path (Join-Path $summaryFolder "all_legacy_webparts.json")

# Subsite summary
$webSummaryRecords = @()
foreach ($wr in $allWebRecords) {
    $webLists = @($allListRecords | Where-Object { $_.WebKey -eq $wr.WebKey })
    $webWiki  = @($allWikiPageRecords | Where-Object { $_.WebUrl -eq $wr.WebUrl })
    $webItems = if ($webLists.Count -gt 0) { [int]($webLists | Measure-Object -Property ItemCount -Sum).Sum } else { 0 }
    $webSummaryRecords += [PSCustomObject]@{
        IsRootWeb            = ($wr.WebUrl.TrimEnd('/') -eq $rootUrl)
        WebKey               = $wr.WebKey
        WebTitle             = $wr.WebTitle
        WebUrl               = $wr.WebUrl
        HasUniquePermissions = $wr.HasUniquePermissions
        Description          = $wr.Description
        ListCount            = $webLists.Count
        TotalItems           = $webItems
        WikiPageCount        = $webWiki.Count
        LastModified         = $wr.LastModified
    }
}
Write-CsvFile  -Object $webSummaryRecords -Path (Join-Path $summaryFolder "subsite_summary.csv")
Write-JsonFile -Object $webSummaryRecords -Path (Join-Path $summaryFolder "subsite_summary.json")

$manifest = [PSCustomObject]@{
    GeneratedOn           = (Get-Date).ToString("s")
    SiteUrl               = $SiteUrl
    OutputRoot            = $rawBase
    WebCount              = $allWebRecords.Count
    ListAndLibraryCount   = $allListRecords.Count
    ViewCount             = $allViewRecords.Count
    PermissionRecordCount = if ($SkipPermissions) { 0 } else { $allPermissionRecords.Count }
    SiteColumnCount       = $allSiteColumnRecords.Count
    WebContentTypeCount   = $allContentTypeRecords.Count
    TotalWikiPages        = $allWikiPageRecords.Count
}
Write-JsonFile -Object $manifest -Path (Join-Path $rawBase "manifest.json")

Write-Host "`nExport complete. Summary: $summaryFolder" -ForegroundColor Green
