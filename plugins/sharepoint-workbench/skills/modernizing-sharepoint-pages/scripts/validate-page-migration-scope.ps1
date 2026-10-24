<#
.SYNOPSIS
Validates a page-migration scope handoff produced by sp-page-inventory-agent.

.DESCRIPTION
Validates one page identity, target environment, and migration wave supplied by
the inventory agent. It never reads the inventory artifact and never contacts
SharePoint.

.KEY INPUT DEPENDENCIES
- Scope JSON returned by sp-page-inventory-agent
- Target SPO page path under /SitePages/
- Target environment: dev, test, or prod
- Migration wave: Wave-1, Wave-2, or Wave-3

.OUTPUTS
- Validated scope PSCustomObject; also written to JSON at -OutputPath when supplied.

.FUNCTION INDEX
Test-SpPageMigrationScope. Supports two parameter sets: -ScopePath/-OutputPath
(file-based CLI usage, OutputPath mandatory) and -ScopeObject/-OutputPath
(in-process usage, OutputPath optional) -- the latter lets
scripts/migration/new-spo-wave-manifest.ps1 dot-source this file and validate
every manifest page through this single shared implementation instead of a
second, independently maintained check.

.NOTE
`Test-SpPageMigrationScope` is the single shared scope-contract validator.
`scripts/migration/new-spo-wave-manifest.ps1` dot-sources this file and calls
the function directly via its `-ScopeObject` parameter set (no file I/O) so
the wave-manifest's per-page preflight (C1) enforces the exact same rules as
a standalone legacy handoff, from one implementation, not two independently
maintained copies.
#>

[CmdletBinding()]
param(
    # Named distinctly from the internal function's -ScopePath/-OutputPath so that
    # dot-sourcing this file (e.g. from scripts/migration/new-spo-wave-manifest.ps1,
    # see C1) cannot clobber a caller's own same-named variables: PowerShell binds
    # a dot-sourced script's top-level param() block in the CALLER's scope, and an
    # unsupplied arg resets the variable there even though the bottom invocation
    # guard below is skipped.
    [string]$CliScopePath,
    [string]$CliOutputPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Test-SpPageMigrationScope {
    [CmdletBinding(DefaultParameterSetName = "Path")]
    param(
        [Parameter(Mandatory = $true, ParameterSetName = "Path")][string]$ScopePath,
        [Parameter(Mandatory = $true, ParameterSetName = "Object")]$ScopeObject,
        [Parameter(ParameterSetName = "Path")]
        [Parameter(ParameterSetName = "Object")]
        [string]$OutputPath
    )

    if ($PSCmdlet.ParameterSetName -eq "Path") {
        if (-not (Test-Path -LiteralPath $ScopePath -PathType Leaf)) {
            throw "Migration scope file was not found: $ScopePath"
        }
        $scope = Get-Content -LiteralPath $ScopePath -Raw | ConvertFrom-Json
    } else {
        $scope = $ScopeObject
    }
    if ($scope -is [System.Array]) {
        throw "Migration scope must contain exactly one page object."
    }

    foreach ($field in @("SiteName", "ServerRelativeUrl", "TargetPageServerRelativeUrl", "Layout", "TargetEnvironment", "Wave")) {
        $property = $scope.PSObject.Properties[$field]
        if ($null -eq $property -or [string]::IsNullOrWhiteSpace([string]$property.Value)) {
            throw "Migration scope is missing required field '$field'."
        }
    }

    if ([string]$scope.TargetEnvironment -notin @("dev", "test", "prod")) {
        throw "Migration scope TargetEnvironment must be dev, test, or prod."
    }
    if ([string]$scope.Wave -notin @("Wave-1", "Wave-2", "Wave-3")) {
        throw "Migration scope Wave must be Wave-1, Wave-2, or Wave-3."
    }
    if (-not [string]$scope.ServerRelativeUrl.StartsWith("/")) {
        throw "Migration scope ServerRelativeUrl must start with '/'."
    }
    if (-not [string]$scope.TargetPageServerRelativeUrl.StartsWith("/SitePages/")) {
        throw "Migration scope TargetPageServerRelativeUrl must start with '/SitePages/'."
    }
    $pageIdProperty = $scope.PSObject.Properties["PageId"]
    $waveIdProperty = $scope.PSObject.Properties["WaveId"]
    if (($null -ne $pageIdProperty) -ne ($null -ne $waveIdProperty)) {
        throw "Migration scope must provide both PageId and WaveId when either is present."
    }
    if ($pageIdProperty -and
        ([string]::IsNullOrWhiteSpace([string]$pageIdProperty.Value) -or
            [string]::IsNullOrWhiteSpace([string]$waveIdProperty.Value))) {
        throw "Migration scope PageId and WaveId must be non-empty."
    }
    $targetSiteUrl = ""
    if ($scope.PSObject.Properties["TargetSiteUrl"]) {
        $targetSiteUri = $null
        $targetSiteUrl = [string]$scope.TargetSiteUrl
        if (-not [uri]::TryCreate($targetSiteUrl, [System.UriKind]::Absolute, [ref]$targetSiteUri) -or
            $targetSiteUri.Scheme -notin @("http", "https")) {
            throw "Migration scope TargetSiteUrl must be an absolute HTTP(S) URL."
        }
        $targetSiteUrl = $targetSiteUrl.TrimEnd("/")
    }
    $sourceLeaf = [System.IO.Path]::GetFileName([string]$scope.ServerRelativeUrl)
    if ([string]::IsNullOrWhiteSpace($sourceLeaf) -or
        [System.IO.Path]::GetExtension($sourceLeaf).ToLowerInvariant() -ne ".aspx") {
        throw "Migration scope ServerRelativeUrl must identify an .aspx source page."
    }
    # SPO saves en/em dashes in page file names as "-" (matches Get-SpPageName in the plan builder).
    $expectedLeaf = ([System.IO.Path]::GetFileNameWithoutExtension($sourceLeaf) -replace "[\u2013\u2014]", "-") + ".aspx"
    $expectedTarget = if ([string]$scope.SiteName -eq "Main") {
        "/SitePages/$expectedLeaf"
    } else {
        "/SitePages/$([string]$scope.SiteName)/$expectedLeaf"
    }
    if ([string]$scope.TargetPageServerRelativeUrl -ne $expectedTarget) {
        throw "Migration scope target '$($scope.TargetPageServerRelativeUrl)' does not match the site-folder convention; expected '$expectedTarget'."
    }

    $title = if ($scope.PSObject.Properties["Title"]) {
        [string]$scope.Title
    } else {
        ""
    }
    $url = if ($scope.PSObject.Properties["Url"]) {
        [string]$scope.Url
    } else {
        ""
    }
    $validated = [ordered]@{
        SiteName = [string]$scope.SiteName
        ServerRelativeUrl = [string]$scope.ServerRelativeUrl
        TargetPageServerRelativeUrl = [string]$scope.TargetPageServerRelativeUrl
        Title = $title
        Url = $url
        Layout = [string]$scope.Layout
        TargetEnvironment = [string]$scope.TargetEnvironment
        Wave = [string]$scope.Wave
    }
    if ($pageIdProperty) {
        $validated.PageId = [string]$pageIdProperty.Value
        $validated.WaveId = [string]$waveIdProperty.Value
    }
    if ($scope.PSObject.Properties["TargetSiteUrl"]) {
        $validated.TargetSiteUrl = $targetSiteUrl
    }

    if (-not [string]::IsNullOrWhiteSpace($OutputPath)) {
        $parent = Split-Path -Parent $OutputPath
        if (-not (Test-Path -LiteralPath $parent -PathType Container)) {
            New-Item -ItemType Directory -Path $parent -Force | Out-Null
        }
        $validated | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
    }
    return [pscustomobject]$validated
}

if ($MyInvocation.InvocationName -ne ".") {
    if ([string]::IsNullOrWhiteSpace($CliScopePath) -or
        [string]::IsNullOrWhiteSpace($CliOutputPath)) {
        throw "ScopePath and OutputPath are required."
    }
    Test-SpPageMigrationScope -ScopePath $CliScopePath -OutputPath $CliOutputPath
}
