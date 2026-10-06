param([string]$Collector, [string]$OutputDir)
$ErrorActionPreference = 'Stop'
function Connect-PnPOnline { [CmdletBinding()] param($Url, $ClientId, $Tenant, [switch]$Interactive, [switch]$ReturnConnection); [pscustomobject]@{ Url=$Url } }
function Disconnect-PnPOnline { [CmdletBinding()] param($Connection) }
function Get-PnPField { [CmdletBinding()] param($List, $Connection); [pscustomobject]@{InternalName='CanvasContent1'}; [pscustomobject]@{InternalName='LayoutWebpartsContent'} }
function Get-PnPListItem {
    [CmdletBinding()] param($List, $Id, $Fields, $Connection)
    [pscustomobject]@{ FieldValues = @{ CanvasContent1='<a href="/docs/guide.pdf">Guide</a>'; LayoutWebpartsContent='[{"properties":{"imageUrl":"/assets/banner.png"}}]' } }
}
New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
@'
"FileUrl","WebUrl","LibraryTitle","LibraryId","ItemId","FileExtension"
"https://tenant.sharepoint.com/sites/root/SitePages/news.aspx","https://tenant.sharepoint.com/sites/root","Site Pages","11111111-1111-1111-1111-111111111111","1","aspx"
'@ | Set-Content -LiteralPath (Join-Path $OutputDir 'input.csv')
& $Collector -InventoryCsv (Join-Path $OutputDir 'input.csv') -OutputDir $OutputDir -ClientId 'mock' -TenantId 'mock'
