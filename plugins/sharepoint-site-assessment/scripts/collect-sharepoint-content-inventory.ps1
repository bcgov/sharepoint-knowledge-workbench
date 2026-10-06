<#
.SYNOPSIS
Exports a CSV inventory of files across all libraries and descendant subsites.

.DESCRIPTION
Read-only collector for SharePoint Online (PnP.PowerShell interactive auth) or
on-premises SharePoint 2016 (REST with Windows credentials). Includes hidden and
system libraries, empty libraries, nested files, and files directly in each web's
root folder. Excludes ordinary list records/attachments, folder records, historical
versions, recycle bins, external linked content and generated list forms/views.
Scope is the starting web and its descendants, not other site collections.

Writes files.csv, libraries.csv, errors.csv and manifest.json to OutputDir.
PARTIAL/FAILED manifests are followed by a terminating error (nonzero process exit).
EMPTY means all queries succeeded but returned no files. No files are downloaded.
The user runs this script in their own terminal; never launch tenant I/O in background.

.PARAMETER Platform
Auto (default) recognizes standard sharepoint.com/us/de/cn hostnames as Online;
other hostnames use OnPrem. Override explicitly for ambiguous/custom hostnames.
Online uses PnP.PowerShell; OnPrem uses REST with NTLM/Kerberos.
.PARAMETER SiteUrl
Starting web URL, overriding config.psd1 for either platform.
.PARAMETER OutputDir
Local export directory. Existing export files are overwritten.
.PARAMETER ConfigPath
Optional explicit Workbench config.psd1 path; otherwise uses helper discovery.
.PARAMETER ClientId
Online Entra application client ID, overriding configuration.
.PARAMETER TenantId
Online tenant ID/domain, overriding configuration.
.PARAMETER Credential
OnPrem: optional explicit PSCredential. When omitted, prompts once interactively.

.EXAMPLE
pwsh -File collect-sharepoint-content-inventory.ps1 -Platform Online -SiteUrl https://tenant.sharepoint.com/sites/Example -OutputDir ./temp/content-inventory
.EXAMPLE
pwsh -File collect-sharepoint-content-inventory.ps1 -Platform OnPrem -SiteUrl https://sharepoint.example.org/sites/Example -OutputDir ./temp/content-inventory
#>
[CmdletBinding()]
param(
    [ValidateSet('Auto', 'Online', 'OnPrem')][string]$Platform = 'Auto',
    [string]$SiteUrl,
    [Parameter(Mandatory = $true)][string]$OutputDir,
    [string]$ConfigPath,
    [string]$ClientId,
    [string]$TenantId,
    [pscredential]$Credential
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot 'Get-WorkbenchConnectionConfig.ps1')
if ($ConfigPath -or -not $SiteUrl) {
    $config = Get-WorkbenchConnectionConfig -Path $ConfigPath
    if (-not $SiteUrl) { $SiteUrl = $config.SiteUrl }
    if (-not $ClientId) { $ClientId = $config.ClientId }
    if (-not $TenantId) { $TenantId = $config.TenantId }
}
$siteUri = [uri]$SiteUrl
if (-not $siteUri.IsAbsoluteUri -or $siteUri.Scheme -notin @('https', 'http')) {
    throw 'SiteUrl must be an absolute HTTP(S) URL.'
}
if ($Platform -eq 'Auto') {
    $Platform = if ($siteUri.Host -match '(^|\.)sharepoint\.(com|us|de|cn)$') { 'Online' } else { 'OnPrem' }
    Write-Host "Selected $Platform from target hostname '$($siteUri.Host)'; use -Platform to override."
}
if ($Platform -eq 'Online') {
    if (-not ($ClientId -and $TenantId)) {
        $config = Get-WorkbenchConnectionConfig -Path $ConfigPath
        if (-not $ClientId) { $ClientId = $config.ClientId }
        if (-not $TenantId) { $TenantId = $config.TenantId }
    }
    if (-not ($SiteUrl -and $ClientId -and $TenantId)) {
        throw 'Online requires SiteUrl, ClientId and TenantId through parameters or config.psd1.'
    }
} else {
    if (-not $SiteUrl) { throw 'OnPrem requires -SiteUrl.' }
    if (-not $Credential) {
        $Credential = Get-Credential -Message "Credentials for $SiteUrl"
        if (-not $Credential) { throw 'No on-prem credentials supplied.' }
    }
}
$SiteUrl = $SiteUrl.TrimEnd('/')
$sourcePath = $siteUri.AbsolutePath.TrimEnd('/')
$sourceSiteName = ''
$files = [System.Collections.Generic.List[object]]::new()
$libraries = [System.Collections.Generic.List[object]]::new()
$errors = [System.Collections.Generic.List[object]]::new()
$webs = [System.Collections.Generic.Queue[string]]::new()
$visited = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
$webs.Enqueue($SiteUrl)
$successfulWebs = 0

function Add-InventoryError {
    param([string]$WebUrl, [string]$Stage, [string]$LibraryTitle, [string]$Message)
    if ($Platform -eq 'OnPrem' -and $Message -match '\b401\b') {
        $Message += ' Windows authentication was rejected. Rerun to prompt for the correct domain account; verify VPN access and site permissions. Browser-only sign-in may require a different authentication adapter.'
    }
    $errors.Add([pscustomobject]@{
        WebUrl = $WebUrl; Stage = $Stage; LibraryTitle = $LibraryTitle; Message = $Message
    })
    Write-Warning "$Stage at '$WebUrl' '$LibraryTitle': $Message"
}

function Get-RestRecords {
    param([string]$Url)
    # Stream each page, preserving earlier records if a later page fails.
    $nextUrl = $Url
    while ($nextUrl) {
        $request = @{
            Uri = $nextUrl; Headers = @{ Accept = 'application/json;odata=verbose' }; ErrorAction = 'Stop'
        }
        $request.Credential = $Credential
        # SP2016 may return both Id and ID: case-sensitive hashtables retain both.
        $response = (Invoke-WebRequest @request).Content | ConvertFrom-Json -AsHashtable
        $data = $response['d']
        if ($data.Contains('results')) {
            foreach ($record in $data['results']) { $record }
        } else { $data }
        $nextUrl = if ($data.Contains('__next')) { $data['__next'] } else { $null }
    }
}

function Get-ContainerType {
    param($Template)
    switch ([int]$Template) {
        109 { 'PictureLibrary' }
        119 { 'WikiPageLibrary' }
        850 { 'PublishingPageLibrary' }
        851 { 'AssetLibrary' }
        default { 'DocumentLibrary' }
    }
}

function Get-OptionalProperty {
    param($Object, [string]$Name)
    # Optional metadata is left blank rather than inventing values.
    if ($Object -is [System.Collections.IDictionary]) { return $Object[$Name] }
    if ($null -ne $Object -and $Object.PSObject.Properties[$Name]) { return $Object.$Name }
    return $null
}

function Format-InventoryDate {
    param($Value)
    if ($Value -is [datetime]) { return $Value.ToUniversalTime().ToString('o') }
    return $Value
}

function Add-FileRecord {
    param($Web, $Library, [string]$Name, [string]$Url, $Size, $Created, $Modified, $UniqueId, $ItemId, $ContentTypeId)
    $relativePath = $Url
    if ($sourcePath -and $Url.StartsWith("$sourcePath/", [StringComparison]::OrdinalIgnoreCase)) {
        $relativePath = $Url.Substring($sourcePath.Length + 1)
    } else { $relativePath = $Url.TrimStart('/') }
    $slashIndex = $relativePath.LastIndexOf('/')
    $folderPath = if ($slashIndex -ge 0) { $relativePath.Substring(0, $slashIndex) } else { '' }
    $libraryRelativePath = ''
    if ($Library) {
        $libraryRoot = $Library.RootFolder.ServerRelativeUrl.TrimEnd('/')
        if ($Url.StartsWith("$libraryRoot/", [StringComparison]::OrdinalIgnoreCase)) {
            $libraryRelativePath = $Url.Substring($libraryRoot.Length + 1)
        }
    }
    $files.Add([pscustomobject][ordered]@{
        SourceSiteName = $sourceSiteName
        SourceSiteUrl = $SiteUrl
        WebTitle = $Web.Title
        WebUrl = $Web.Url
        ContainerType = if ($Library) { Get-ContainerType (Get-OptionalProperty $Library 'BaseTemplate') } else { 'SiteRoot' }
        LibraryTitle = if ($Library) { $Library.Title } else { '' }
        LibraryId = if ($Library) { [string]$Library.Id } else { '' }
        LibraryBaseTemplate = if ($Library) { Get-OptionalProperty $Library 'BaseTemplate' } else { '' }
        RelativePath = $relativePath
        LibraryRelativePath = $libraryRelativePath
        FolderPath = $folderPath
        ServerRelativeUrl = $Url
        FileUrl = $siteUri.GetLeftPart([UriPartial]::Authority) + $Url
        FileName = $Name
        FileExtension = [IO.Path]::GetExtension($Name).TrimStart('.').ToLowerInvariant()
        UniqueId = $UniqueId
        ItemId = $ItemId
        ContentTypeId = [string]$ContentTypeId
        SizeBytes = $Size
        Created = Format-InventoryDate $Created
        Modified = Format-InventoryDate $Modified
    })
}

$query = @'
<View Scope="RecursiveAll"><ViewFields><FieldRef Name="ID"/><FieldRef Name="ContentTypeId"/><FieldRef Name="FileLeafRef"/><FieldRef Name="FileRef"/><FieldRef Name="File_x0020_Size"/><FieldRef Name="Created"/><FieldRef Name="Modified"/><FieldRef Name="UniqueId"/><FieldRef Name="FSObjType"/></ViewFields><RowLimit Paged="TRUE">500</RowLimit></View>
'@

while ($webs.Count -gt 0) {
    $webUrl = $webs.Dequeue().TrimEnd('/')
    if (-not $visited.Add($webUrl)) { continue }
    Write-Host "Collecting files at $webUrl"
    $connection = $null
    try {
        if ($Platform -eq 'Online') {
            $connection = Connect-PnPOnline -Url $webUrl -ClientId $ClientId -Tenant $TenantId -Interactive -ReturnConnection
            $web = Get-PnPWeb -Includes Title, Url, RootFolder -Connection $connection
        } else { $web = Get-RestRecords -Url "$webUrl/_api/web?`$select=Title,Url" }
        $successfulWebs++
        if ($webUrl -eq $SiteUrl) { $sourceSiteName = $web.Title }
    } catch {
        Add-InventoryError $webUrl 'Web' '' $_.Exception.Message
        continue
    }

    try {
        if ($Platform -eq 'Online') {
            Get-PnPSubWeb -Includes Url -Connection $connection | ForEach-Object { $webs.Enqueue($_.Url) }
        } else {
            Get-RestRecords -Url "$webUrl/_api/web/webs?`$select=Title,Url" | ForEach-Object { $webs.Enqueue($_.Url) }
        }
    } catch { Add-InventoryError $webUrl 'Subsites' '' $_.Exception.Message }

    # Includes files such as default.aspx stored outside document libraries.
    try {
        $rootFiles = if ($Platform -eq 'Online') {
            Get-PnPProperty -ClientObject $web.RootFolder -Property Files -Connection $connection
        } else {
            Get-RestRecords -Url "$webUrl/_api/web/RootFolder/Files?`$select=Name,ServerRelativeUrl,Length,TimeCreated,TimeLastModified,UniqueId"
        }
        foreach ($file in $rootFiles) {
            Add-FileRecord $web $null $file.Name $file.ServerRelativeUrl $file.Length $file.TimeCreated $file.TimeLastModified (Get-OptionalProperty $file 'UniqueId')
        }
    } catch { Add-InventoryError $webUrl 'RootFiles' '' $_.Exception.Message }

    try {
        $getLibraries = {
            if ($Platform -eq 'Online') {
                Get-PnPList -Includes BaseType, BaseTemplate, Hidden, RootFolder -Connection $connection
            } else {
                Get-RestRecords -Url "$webUrl/_api/web/lists?`$select=Id,Title,BaseType,BaseTemplate,Hidden,RootFolder/ServerRelativeUrl&`$expand=RootFolder"
            }
        }
        & $getLibraries | ForEach-Object {
            $library = $_
            if ([string]$library.BaseType -notin @('1', 'DocumentLibrary')) { return }
            $startCount = $files.Count
            $libraryStatus = 'COMPLETE'
            try {
                if ($Platform -eq 'Online') {
                    Get-PnPListItem -List $library.Id -Query $query -PageSize 500 -Connection $connection | ForEach-Object {
                        if ([string]$_.FileSystemObjectType -in @('0', 'File')) {
                            $fields = $_.FieldValues
                            Add-FileRecord $web $library $fields['FileLeafRef'] $fields['FileRef'] $fields['File_x0020_Size'] $fields['Created'] $fields['Modified'] $fields['UniqueId'] $fields['ID'] $fields['ContentTypeId']
                        }
                    }
                } else {
                    $itemsUrl = "$webUrl/_api/web/lists(guid'$($library.Id)')/items?`$select=Id,ContentTypeId,FileLeafRef,FileRef,FSObjType,Created,Modified,File/Length,File/UniqueId&`$expand=File&`$top=500"
                    Get-RestRecords -Url $itemsUrl | ForEach-Object {
                        if ($_.FSObjType -eq 0) {
                            Add-FileRecord $web $library $_.FileLeafRef $_.FileRef $_.File.Length $_.Created $_.Modified (Get-OptionalProperty $_.File 'UniqueId') (Get-OptionalProperty $_ 'Id') (Get-OptionalProperty $_ 'ContentTypeId')
                        }
                    }
                }
            } catch {
                $libraryStatus = 'PARTIAL'
                Add-InventoryError $webUrl 'LibraryFiles' $library.Title $_.Exception.Message
            }
            $libraries.Add([pscustomobject][ordered]@{
                SourceSiteName = $sourceSiteName; SourceSiteUrl = $SiteUrl
                WebTitle = $web.Title; WebUrl = $web.Url
                ContainerType = Get-ContainerType (Get-OptionalProperty $library 'BaseTemplate')
                LibraryTitle = $library.Title; LibraryId = [string]$library.Id
                LibraryBaseTemplate = Get-OptionalProperty $library 'BaseTemplate'
                LibraryRootUrl = $library.RootFolder.ServerRelativeUrl
                Hidden = $library.Hidden; FileCount = $files.Count - $startCount; Status = $libraryStatus
            })
        }
    } catch { Add-InventoryError $webUrl 'Libraries' '' $_.Exception.Message }
    if ($connection) {
        try { Disconnect-PnPOnline -Connection $connection }
        catch { Add-InventoryError $webUrl 'Disconnect' '' $_.Exception.Message }
    }
}

function Write-InventoryCsv {
    param($Records, [string[]]$Columns, [string]$Path)
    if ($Records.Count -gt 0) {
        $Records | Select-Object -Property $Columns | Export-Csv -LiteralPath $Path -NoTypeInformation -Encoding utf8
    } else {
        # Keep the schema readable even for an empty export.
        ('"' + ($Columns -join '","') + '"') | Set-Content -LiteralPath $Path -Encoding utf8
    }
}
New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
Write-InventoryCsv $files @('SourceSiteName', 'SourceSiteUrl', 'WebTitle', 'WebUrl', 'ContainerType', 'LibraryTitle', 'LibraryId', 'LibraryBaseTemplate', 'RelativePath', 'LibraryRelativePath', 'FolderPath', 'ServerRelativeUrl', 'FileUrl', 'FileName', 'FileExtension', 'UniqueId', 'ItemId', 'ContentTypeId', 'SizeBytes', 'Created', 'Modified') (Join-Path $OutputDir 'files.csv')
Write-InventoryCsv $libraries @('SourceSiteName', 'SourceSiteUrl', 'WebTitle', 'WebUrl', 'ContainerType', 'LibraryTitle', 'LibraryId', 'LibraryBaseTemplate', 'LibraryRootUrl', 'Hidden', 'FileCount', 'Status') (Join-Path $OutputDir 'libraries.csv')
Write-InventoryCsv $errors @('WebUrl', 'Stage', 'LibraryTitle', 'Message') (Join-Path $OutputDir 'errors.csv')
$status = if ($successfulWebs -eq 0) { 'FAILED' } elseif ($errors.Count -gt 0) { 'PARTIAL' } elseif ($files.Count -eq 0) { 'EMPTY' } else { 'COMPLETE' }
[pscustomobject]@{
    GeneratedOn = [datetime]::UtcNow.ToString('o'); SourceSiteUrl = $SiteUrl; Platform = $Platform
    Status = $status; WebCount = $successfulWebs; AttemptedWebCount = $visited.Count
    LibraryCount = $libraries.Count; FileCount = $files.Count; ErrorCount = $errors.Count
    Scope = 'Starting web and descendant subsites; all libraries (including hidden/system) and direct web-root files'
    Exclusions = @('Ordinary list records and attachments', 'Folder records', 'Historical versions and recycle bins', 'External linked content', 'Generated list forms/views', 'Files outside libraries below web-root folders')
} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $OutputDir 'manifest.json') -Encoding utf8
Write-Host "Wrote $($files.Count) files and $($libraries.Count) libraries to $OutputDir ($status)."
if ($status -in @('PARTIAL', 'FAILED')) { throw "Inventory is $status. See errors.csv and manifest.json in '$OutputDir'." }
