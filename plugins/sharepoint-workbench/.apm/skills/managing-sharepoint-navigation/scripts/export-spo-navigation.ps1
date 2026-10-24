<#
.SYNOPSIS
Read-only export of the live SharePoint Online navigation (tree view or JSON snapshot).

.DESCRIPTION
Connects with the Connection block of -ConfigPath, reads the navigation tree with
Get-PnPNavigationNode -Tree and either prints an indented tree or emits a snapshot JSON
({siteUrl, location, topNav|quickLaunch: [{id,title,url,children}]}). The snapshot feeds
navigation_plan.py (diff / to-workbook). It never modifies the site, needs no token, and
status lines go to stderr so stdout stays clean for redirection.

.KEY INPUT DEPENDENCIES
- PowerShell 7, PnP.PowerShell module, interactive sign-in popup.
- A config-spo-<env>.psd1 with Connection = @{ SiteUrl; ClientId; TenantId }.

.FUNCTION INDEX
ConvertTo-Snapshot, Write-Tree

.EXAMPLE
pwsh -File export-spo-navigation.ps1 -ConfigPath .\config-spo-dev.psd1
pwsh -File export-spo-navigation.ps1 -ConfigPath .\config-spo-dev.psd1 -Format Json -OutputPath .\temp\nav-live.json
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$ConfigPath,
    [ValidateSet('TopNavigationBar', 'QuickLaunch')][string]$Location = 'QuickLaunch',
    [ValidateSet('Tree', 'Json')][string]$Format = 'Tree',
    [string]$OutputPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Converts PnP navigation nodes (with Children) into plain snapshot objects.
function ConvertTo-Snapshot {
    <# Recursively maps nodes to {id,title,url,children}. #>
    param($Nodes)
    @(foreach ($node in @($Nodes)) {
        [ordered]@{
            id       = [int]$node.Id
            title    = [string]$node.Title
            url      = [string]$node.Url
            children = @(if ($node.PSObject.Properties['Children']) { ConvertTo-Snapshot -Nodes $node.Children })
        }
    })
}

# Loads one node by Id and recurses into its Children.
function Read-Node {
    <# Returns {id,title,url,children} for the node and its descendants. #>
    param([int]$Id)
    $node = Get-PnPNavigationNode -Id $Id
    $kids = if ($node.PSObject.Properties['Children']) { @($node.Children) } else { @() }
    [ordered]@{
        id       = [int]$node.Id
        title    = [string]$node.Title
        url      = [string]$node.Url
        children = @(foreach ($k in $kids) { Read-Node -Id $k.Id })
    }
}

# Prints an indented tree to stdout.
function Write-Tree {
    <# Writes one line per node, indented by depth. #>
    param($Nodes, [int]$Depth = 0)
    foreach ($node in $Nodes) {
        Write-Output ('{0}{1}  [{2}]  {3}' -f ('  ' * $Depth), $node.title, $node.id, $node.url)
        Write-Tree -Nodes $node.children -Depth ($Depth + 1)
    }
}

if (-not (Test-Path -LiteralPath $ConfigPath)) { throw "Config not found: $ConfigPath" }
$connection = (Import-PowerShellDataFile -LiteralPath $ConfigPath).Connection
$started = Get-Date
[Console]::Error.WriteLine("Started: $started  Site: $($connection.SiteUrl)  Location: $Location")

Connect-PnPOnline -Url $connection.SiteUrl -ClientId $connection.ClientId -Tenant $connection.TenantId -Interactive
$flat = @(Get-PnPNavigationNode -Location $Location)
[Console]::Error.WriteLine("Top-level nodes found in ${Location}: $($flat.Count)")
if ($flat.Count -eq 0) {
    $other = if ($Location -eq 'QuickLaunch') { 'TopNavigationBar' } else { 'QuickLaunch' }
    $otherCount = @(Get-PnPNavigationNode -Location $other).Count
    [Console]::Error.WriteLine("No nodes in $Location ($other has $otherCount); try -Location $other.")
}
# -Tree only returns display text, so children are loaded per node by Id.
$nodes = @(foreach ($n in $flat) { Read-Node -Id $n.Id })
$key = if ($Location -eq 'QuickLaunch') { 'quickLaunch' } else { 'topNav' }
$snapshot = [ordered]@{ siteUrl = $connection.SiteUrl; location = $Location; $key = $nodes }

if ($Format -eq 'Json') {
    $json = $snapshot | ConvertTo-Json -Depth 20
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $json -Encoding utf8 } else { $json }
} else {
    $text = Write-Tree -Nodes $nodes
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $text -Encoding utf8 } else { $text }
}

$finished = Get-Date
[Console]::Error.WriteLine("Finished: $finished  Elapsed: $([int]($finished - $started).TotalSeconds)s  Top-level nodes: $(@($nodes).Count)")

