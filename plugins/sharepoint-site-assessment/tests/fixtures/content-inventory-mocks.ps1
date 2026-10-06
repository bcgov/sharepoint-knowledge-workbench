<# Mock tenant adapters for the content collector; no network or credentials are used. #>
param([string]$Collector, [string]$OutputDir, [string]$Platform, [string]$Scenario,
      [string]$TargetUrl = 'https://example.test/sites/root', [string]$ConfigPath, [switch]$ConfigOnly)
$ErrorActionPreference = 'Stop'
$root = $TargetUrl
$documentId = '11111111-1111-1111-1111-111111111111'
$assetId = '22222222-2222-2222-2222-222222222222'
$emptyId = '33333333-3333-3333-3333-333333333333'
$ordinaryId = '44444444-4444-4444-4444-444444444444'

function Mock-Web($url) {
    $title = if ($url -eq $root) { 'Root' } elseif ($url -like '*/grandchild') { 'Grandchild' } else { 'Child' }
    [pscustomobject]@{ Url = $url; Title = $title }
}
function Mock-Libraries($url) {
    if ($Scenario -eq 'empty') { return }
    $path = ([uri]$url).AbsolutePath
    [pscustomobject]@{ Id = $documentId; Title = 'Documents'; BaseType = 1; BaseTemplate = 101; Hidden = $false; RootFolder = [pscustomobject]@{ ServerRelativeUrl = "$path/Documents" } }
    if ($url -eq $root) {
        [pscustomobject]@{ Id = $assetId; Title = 'Site Assets'; BaseType = 1; BaseTemplate = 851; Hidden = $true; RootFolder = [pscustomobject]@{ ServerRelativeUrl = "$path/SiteAssets" } }
        [pscustomobject]@{ Id = $emptyId; Title = 'Empty'; BaseType = 1; BaseTemplate = 109; Hidden = $false; RootFolder = [pscustomobject]@{ ServerRelativeUrl = "$path/Empty" } }
    }
    [pscustomobject]@{ Id = $ordinaryId; Title = 'Tasks'; BaseType = 0; Hidden = $false; RootFolder = [pscustomobject]@{ ServerRelativeUrl = "$path/Lists/Tasks" } }
}
function Mock-Files($url, $id) {
    if ($id -eq $ordinaryId) { throw 'ordinary list records must not be queried' }
    if ($Scenario -eq 'library-denied' -and $url -eq $root -and $id -eq $assetId) { throw 'library denied' }
    if ($id -eq $emptyId) { return }
    $path = ([uri]$url).AbsolutePath
    $name = if ($id -eq $assetId) { 'logo.svg' } elseif ($url -eq $root) { 'manual.docx' } elseif ($url -like '*/grandchild') { 'news.aspx' } else { 'photo.PNG' }
    $folder = if ($id -eq $assetId) { 'SiteAssets' } elseif ($url -eq $root) { 'Documents' } else { 'Documents/deep' }
    [pscustomobject]@{ FileLeafRef = $name; FileRef = "$path/$folder/$name"; FSObjType = 0; File_x0020_Size = '20'; Created = '2026-01-01T00:00:00Z'; Modified = '2026-02-01T00:00:00Z'; File = [pscustomobject]@{ Length = '20' } }
}
function Mock-Children($url) {
    if ($Scenario -eq 'empty') { return }
    if ($Scenario -eq 'subsites-denied' -and $url -eq "$root/child") { throw 'subsites denied' }
    if ($url -eq $root) { Mock-Web "$root/child" }
    elseif ($url -eq "$root/child") { Mock-Web "$root/child/grandchild" }
}
function Mock-RootFiles($url) {
    if ($Scenario -ne 'empty' -and $url -eq $root) {
        [pscustomobject]@{ Name = 'default.aspx'; ServerRelativeUrl = '/sites/root/default.aspx'; Length = 10; TimeCreated = '2026-01-01T00:00:00Z'; TimeLastModified = '2026-02-01T00:00:00Z' }
    }
}
function Connect-PnPOnline {
    [CmdletBinding()] param($Url, $ClientId, $Tenant, [switch]$Interactive, [switch]$ReturnConnection)
    [pscustomobject]@{ Url = $Url }
}
function Disconnect-PnPOnline { [CmdletBinding()] param($Connection) }
function Get-PnPWeb {
    [CmdletBinding()] param($Connection, $Includes)
    $web = Mock-Web $Connection.Url
    $web | Add-Member RootFolder ([pscustomobject]@{ Url = $Connection.Url })
    $web
}
function Get-PnPSubWeb { [CmdletBinding()] param($Connection, $Includes); Mock-Children $Connection.Url }
function Get-PnPList { [CmdletBinding()] param($Connection, $Includes); Mock-Libraries $Connection.Url }
function Get-PnPListItem {
    [CmdletBinding()] param($List, $Query, $PageSize, $Connection)
    if ($Query -notmatch 'RecursiveAll') { throw 'nested files require RecursiveAll' }
    foreach ($record in @(Mock-Files $Connection.Url $List)) {
        [pscustomobject]@{ FileSystemObjectType = 'File'; FieldValues = @{
            FileLeafRef = $record.FileLeafRef; FileRef = $record.FileRef; File_x0020_Size = $record.File_x0020_Size
            Created = $record.Created; Modified = $record.Modified
        } }
    }
    [pscustomobject]@{ FileSystemObjectType = 'Folder'; FieldValues = @{ FileLeafRef = 'folder' } }
}
function Get-PnPProperty {
    [CmdletBinding()] param($ClientObject, $Property, $Connection)
    Mock-RootFiles $ClientObject.Url
}
function Invoke-RestMethod {
    [CmdletBinding()] param($Uri, $Headers, [switch]$UseDefaultCredentials, $Credential)
    $webUrl, $endpoint = ([string]$Uri) -split '/_api/', 2
    if ($endpoint -eq 'web?$select=Title,Url') { return [pscustomobject]@{ d = (Mock-Web $webUrl) } }
    if ($endpoint -like 'web/webs*') { $records = @(Mock-Children $webUrl) }
    elseif ($endpoint.StartsWith('web/lists?')) { $records = @(Mock-Libraries $webUrl) }
    elseif ($endpoint -like 'web/RootFolder/Files*') { $records = @(Mock-RootFiles $webUrl) }
    elseif ($endpoint -like 'web/lists(guid*') {
        if ($endpoint -notmatch "guid'([^']+)'") { throw "bad library URL: $Uri" }
        $id = $matches[1]
        if ($endpoint -like '*page=2*') {
            if ($Scenario -eq 'page-denied' -and $webUrl -eq $root) { throw 'later page denied' }
            return [pscustomobject]@{ d = [pscustomobject]@{ results = @() } }
        }
        $records = @(Mock-Files $webUrl $id)
        return [pscustomobject]@{ d = [pscustomobject]@{ results = $records; __next = "$Uri&page=2" } }
    } else { throw "Unexpected REST request: $Uri" }
    # Paginate child webs and library discovery too, not just file results.
    if ($endpoint -like '*page=2*') { return [pscustomobject]@{ d = [pscustomobject]@{ results = @() } } }
    [pscustomobject]@{ d = [pscustomobject]@{ results = $records; __next = "$Uri&page=2" } }
}
function Invoke-WebRequest {
    [CmdletBinding()] param($Uri, $Headers, [switch]$UseDefaultCredentials, $Credential)
    if ($Scenario -eq 'unauthorized') { throw 'Response status code does not indicate success: 401 (Unauthorized).' }
    $response = Invoke-RestMethod -Uri $Uri -Headers $Headers -UseDefaultCredentials:$UseDefaultCredentials -Credential $Credential
    [pscustomobject]@{ Content = ($response | ConvertTo-Json -Depth 10 -Compress) }
}
try {
    $parameters = @{ Platform = $Platform; OutputDir = $OutputDir; Credential = [pscredential]::new('mock', (ConvertTo-SecureString 'mock' -AsPlainText -Force)) }
    if (-not $ConfigOnly) { $parameters.SiteUrl = $root }
    if ($ConfigPath) { $parameters.ConfigPath = $ConfigPath }
    else { $parameters.ClientId = 'mock-client'; $parameters.TenantId = 'mock-tenant' }
    & $Collector @parameters
} catch { Write-Error $_ -ErrorAction Continue; exit 1 }
