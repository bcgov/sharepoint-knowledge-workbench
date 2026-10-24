<#
.SYNOPSIS
Applies a navigation ops list (from navigation_plan.py diff) to SharePoint Online native navigation.

.DESCRIPTION
Dry-run by default: prints the planned operations and needs no connection. With
-Execute and -ConfirmToken PROVISION-SPO-NAV it connects, re-reads the live tree, preflight-checks
every update/prune target (still present, same title) BEFORE any change, saves a JSON backup of the
live tree, then applies ops in order and stops at the first failure.
Supported ops: create, update (Url only), unchanged (no-op), order-drift (reported, never applied:
existing nodes cannot be reordered without recreating them), prune (only with -Prune).
Refuses a non-DEV site unless -AllowNonDev is passed by a human.

.KEY INPUT DEPENDENCIES
- PowerShell 7, PnP.PowerShell module, interactive sign-in popup (only for -Execute).
- A config-spo-<env>.psd1 with Connection = @{ SiteUrl; ClientId; TenantId }.
- ops.json produced by: python navigation_plan.py diff ...

.FUNCTION INDEX
Get-LiveSnapshot, Find-NodeById, Invoke-NavOp

.EXAMPLE
pwsh -File sync-spo-navigation.ps1 -ConfigPath .\config-spo-dev.psd1 -OpsPath .\temp\ops.json
pwsh -File sync-spo-navigation.ps1 -ConfigPath .\config-spo-dev.psd1 -OpsPath .\temp\ops.json -Execute -ConfirmToken PROVISION-SPO-NAV
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$ConfigPath,
    [Parameter(Mandatory)][string]$OpsPath,
    [ValidateSet('TopNavigationBar', 'QuickLaunch')][string]$Location = 'QuickLaunch',
    [string]$BackupPath,
    [switch]$Prune,
    [switch]$Execute,
    [string]$ConfirmToken,
    [switch]$AllowNonDev
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$requiredToken = 'PROVISION-SPO-NAV'
$linkless = 'http://linkless.header/'
$sep = [string][char]31

# Reads the live tree as plain objects.
function Get-LiveSnapshot {
    <# Returns nested {id,title,url,children} objects for the location. #>
    param([string]$Where)
    # -Tree returns display text, so children are loaded per node by Id (same as export-spo-navigation.ps1).
    function Read-LiveNode([int]$Id) {
        $n = Get-PnPNavigationNode -Id $Id
        $kids = if ($n.PSObject.Properties['Children']) { @($n.Children) } else { @() }
        [pscustomobject]@{ id = [int]$n.Id; title = [string]$n.Title; url = [string]$n.Url; children = @(foreach ($k in $kids) { Read-LiveNode -Id $k.Id }) }
    }
    @(foreach ($top in @(Get-PnPNavigationNode -Location $Where)) { Read-LiveNode -Id $top.Id })
}

# Finds a node by id anywhere in a snapshot.
function Find-NodeById {
    <# Depth-first lookup; returns $null when absent. #>
    param($Nodes, [int]$Id)
    foreach ($n in @($Nodes)) {
        if ($n.id -eq $Id) { return $n }
        $hit = Find-NodeById -Nodes $n.children -Id $Id
        if ($hit) { return $hit }
    }
    return $null
}

# Applies one op to the tenant and records ids for later ops.
function Invoke-NavOp {
    <# Executes create/update/prune; $ids maps path-key to node id. #>
    param($Op, [hashtable]$Ids, [string]$Where, [string]$SiteHost)
    $key = ($Op.path -join $sep)
    switch ($Op.op) {
        'unchanged' { $Ids[$key] = [int]$Op.id }
        'update' {
            $node = Get-PnPNavigationNode -Id $Op.id
            $node.Url = if ($Op.url) { $Op.url } else { $linkless }
            $node.Update()
            Invoke-PnPQuery
            $Ids[$key] = [int]$Op.id
        }
        'create' {
            $url = if ($Op.url) { $Op.url } else { $linkless }
            $args2 = @{ Location = $Where; Title = $Op.path[-1]; Url = $url }
            if ($Op.parentPath) { $args2.Parent = $Ids[($Op.parentPath -join $sep)] }
            if ($Op.previousPath) { $args2.PreviousNode = $Ids[($Op.previousPath -join $sep)] } else { $args2.First = $true }
            $isAbsolute = $url -match '^https?://'
            if ($isAbsolute -and ([uri]$url).Host -ne $SiteHost) { $args2.External = $true }
            if ($Op.openInNewTab) { $args2.OpenInNewTab = $true }
            try {
                $created = Add-PnPNavigationNode @args2
            } catch {
                # PnP validates same-site URLs against existing files; pages not migrated yet need the absolute URL with -External.
                if (-not $isAbsolute -and $url.StartsWith('/') -and $_.Exception.Message -match 'no such file or folder') {
                    $args2.Url = "https://$SiteHost$url"
                    $args2.External = $true
                    $created = Add-PnPNavigationNode @args2
                } else { throw }
            }
            $Ids[$key] = [int]$created.Id
        }
        'prune' { Remove-PnPNavigationNode -Identity $Op.id -Force }
    }
}

if (-not (Test-Path -LiteralPath $ConfigPath)) { throw "Config not found: $ConfigPath" }
if (-not (Test-Path -LiteralPath $OpsPath)) { throw "Ops file not found: $OpsPath" }
$connection = (Import-PowerShellDataFile -LiteralPath $ConfigPath).Connection
if ($connection.SiteUrl -notmatch 'DEV' -and -not $AllowNonDev) {
    throw "Refusing non-DEV site '$($connection.SiteUrl)'. A human must pass -AllowNonDev."
}
if ($Execute -and $ConfirmToken -ne $requiredToken) { throw "-Execute requires -ConfirmToken $requiredToken" }

$plan = Get-Content -LiteralPath $OpsPath -Raw -Encoding utf8 | ConvertFrom-Json
$ops = @($plan.ops | Where-Object { $_.op -ne 'prune' -or $Prune })
$skippedPrune = @($plan.ops | Where-Object { $_.op -eq 'prune' }).Count - @($ops | Where-Object { $_.op -eq 'prune' }).Count
$started = Get-Date
[Console]::Error.WriteLine("Started: $started  Site: $($connection.SiteUrl)  Mode: $(if ($Execute) { 'EXECUTE' } else { 'DRY-RUN' })")

if (-not $Execute) {
    foreach ($op in $ops) { [Console]::Error.WriteLine(('{0,-11} {1}' -f $op.op, ($op.path -join ' > '))) }
    if ($skippedPrune -gt 0) { [Console]::Error.WriteLine("$skippedPrune prune op(s) not shown: pass -Prune to include them.") }
    $counts = [ordered]@{}
    foreach ($group in ($ops | Group-Object op)) { $counts[$group.Name] = $group.Count }
    [ordered]@{ mode = 'dry-run'; siteUrl = $connection.SiteUrl; counts = $counts; pruneSkipped = $skippedPrune } | ConvertTo-Json -Depth 5
    return
}

Connect-PnPOnline -Url $connection.SiteUrl -ClientId $connection.ClientId -Tenant $connection.TenantId -Interactive
$live = Get-LiveSnapshot -Where $Location

# Preflight: every update/prune target must still exist with the expected title; nothing is changed if not.
foreach ($op in ($ops | Where-Object { $_.op -in 'update', 'prune' })) {
    $node = Find-NodeById -Nodes $live -Id ([int]$op.id)
    if (-not $node -or $node.title -ne $op.path[-1]) {
        throw "Preflight failed: node $($op.id) '$($op.path -join ' > ')' no longer matches live navigation. Re-run export + diff."
    }
}

if (-not $BackupPath) { $BackupPath = Join-Path ([System.IO.Path]::GetTempPath()) ("nav-backup-{0:yyyyMMdd-HHmmss}.json" -f $started) }
@{ siteUrl = $connection.SiteUrl; location = $Location; nodes = $live } | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $BackupPath -Encoding utf8
[Console]::Error.WriteLine("Backup: $BackupPath")

$siteHost = ([uri]$connection.SiteUrl).Host
$ids = @{}
$results = @()
foreach ($op in $ops) {
    if ($op.op -eq 'order-drift') { $results += [pscustomobject]@{ op = $op.op; path = ($op.path -join ' > '); status = 'reported' }; continue }
    try {
        Invoke-NavOp -Op $op -Ids $ids -Where $Location -SiteHost $siteHost
        [Console]::Error.WriteLine(('{0,-11} ok  {1}' -f $op.op, ($op.path -join ' > ')))
        $results += [pscustomobject]@{ op = $op.op; path = ($op.path -join ' > '); status = 'ok' }
    } catch {
        $results += [pscustomobject]@{ op = $op.op; path = ($op.path -join ' > '); status = 'failed'; error = $_.Exception.Message }
        $results | ConvertTo-Json -Depth 5
        [Console]::Error.WriteLine("Stopped at first failure. Restore reference: $BackupPath")
        exit 1
    }
}
$results | ConvertTo-Json -Depth 5
$finished = Get-Date
[Console]::Error.WriteLine("Finished: $finished  Elapsed: $([int]($finished - $started).TotalSeconds)s")
