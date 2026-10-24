<#
.SYNOPSIS
Downloads image assets referenced by extracted SP2016 page web-part HTML.

.DESCRIPTION
Reads the existing webpart-content.json shape, resolves image sources using
browser page URL semantics, downloads image bytes read-only into a local output
directory, and writes an asset manifest for later SPO publication.

.KEY INPUT DEPENDENCIES
- Web-part content JSON with PageUrl and Content fields
- Source SP2016 page URL or page-relative URL
- Target SPO page path used for the SiteAssets/SitePages folder
- -ConfigPath: config-spo-<env>.psd1; SourcePageUrl must be on its Source.SiteUrl host
  and Source.ReadOnly must be $true
- SP2016 credentials: prompts via Get-Credential by default (or pass -Credential);
  -UseDefaultCredentials opts in to Windows integrated auth

.OUTPUTS
- Downloaded image files under the requested output directory
- JSON asset manifest with future SiteAssets/SitePages destinations

.FUNCTION INDEX
Get-SpImageRequestCredentials, Get-SpPageAssetFolderPath, Get-SpPageImageReferences, Save-SpPageImageAssets,
Read-SpoConfiguration.
#>

[CmdletBinding()]
param(
    [string]$WebpartContentPath,
    [string]$SourcePageUrl,
    [string]$TargetPageServerRelativeUrl,
    [string]$OutputDir,
    [string]$ManifestPath,
    [string]$ConfigPath,
    [switch]$UseDefaultCredentials,
    [pscredential]$Credential
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Returns the credential fields for Invoke-WebRequest. Integrated auth is opt-in only;
# otherwise an explicit credential is used, prompting once when none was supplied.
function Get-SpImageRequestCredentials {
    [CmdletBinding()]
    param(
        [switch]$UseDefaultCredentials,
        [pscredential]$Credential
    )
    if ($UseDefaultCredentials) {
        return @{ UseDefaultCredentials = $true }
    }
    if ($null -eq $Credential) {
        $Credential = Get-Credential -Message "Credentials for SP2016 request"
    }
    return @{ Credential = $Credential }
}

# Reads the environment configuration file named by -ConfigPath (config-spo-<env>.psd1).
# Identical in every sp-migration script so each installed skill stays self-contained.
function Read-SpoConfiguration {
    <#
    Returns Path, Environment, SiteUrl, ClientId, TenantId (from Connection.*) and
    Source (the SP2016 Source block, or $null). Throws when -ConfigPath is missing,
    the file does not exist, or a name listed in -Require is empty in Connection.
    #>
    [CmdletBinding()]
    param(
        [AllowEmptyString()][string]$Path,
        [string[]]$Require = @()
    )

    if ([string]::IsNullOrWhiteSpace($Path)) {
        throw "-ConfigPath is required: pass the config-spo-<env>.psd1 file for the environment."
    }
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "-ConfigPath file not found: $Path"
    }

    $raw = Import-PowerShellDataFile -LiteralPath $Path
    $connection = if ($raw.ContainsKey("Connection")) { $raw.Connection } else { @{} }
    foreach ($name in $Require) {
        if (-not $connection.ContainsKey($name) -or [string]::IsNullOrWhiteSpace([string]$connection[$name])) {
            throw "Configuration is missing Connection.${name}: $Path"
        }
    }
    $environment = [string]$connection["Environment"]
    if (-not [string]::IsNullOrWhiteSpace($environment) -and $environment -notin @("dev", "test", "prod")) {
        throw "Connection.Environment must be dev, test, or prod: $Path"
    }

    return [pscustomobject]@{
        Path        = $Path
        Environment = $environment
        SiteUrl     = [string]$connection["SiteUrl"]
        ClientId    = [string]$connection["ClientId"]
        TenantId    = [string]$connection["TenantId"]
        Source      = if ($raw.ContainsKey("Source")) { $raw.Source } else { $null }
    }
}

function Get-SpPageAssetFolderPath {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$TargetPageServerRelativeUrl
    )

    $segments = $TargetPageServerRelativeUrl.Trim("/").Split("/")
    if ($segments.Count -lt 2 -or $segments[0] -ne "SitePages") {
        throw "Target page path must be under '/SitePages/'."
    }
    $pageName = [System.IO.Path]::GetFileNameWithoutExtension($segments[-1])
    if ([string]::IsNullOrWhiteSpace($pageName)) {
        throw "Target page path does not contain a page name."
    }
    $folderSegments = [System.Collections.Generic.List[string]]::new()
    $folderSegments.Add("SiteAssets")
    $folderSegments.Add("SitePages")
    if ($segments.Count -gt 2) {
        foreach ($segment in $segments[1..($segments.Count - 2)]) {
            $folderSegments.Add($segment)
        }
    }
    $folderSegments.Add($pageName)
    return ($folderSegments -join "/")
}

function Get-SpPageImageReferences {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$Html,
        [Parameter(Mandatory = $true)][string]$PageUrl,
        [Parameter(Mandatory = $true)][string]$TargetPageServerRelativeUrl
    )

    $assetFolder = Get-SpPageAssetFolderPath -TargetPageServerRelativeUrl $TargetPageServerRelativeUrl
    $pageUri = [Uri]$PageUrl
    $matches = [regex]::Matches($Html, '(?is)<img\b[^>]*?\bsrc\s*=\s*["'']([^"'']+)["'']')
    foreach ($match in $matches) {
        $source = [System.Net.WebUtility]::HtmlDecode(
            [string]$match.Groups[1].Value
        )
        if ([string]::IsNullOrWhiteSpace($source) -or $source -match '^(?i:data:|#)') {
            continue
        }

        $sourceUri = [Uri]::new($pageUri, $source)
        $leaf = [System.IO.Path]::GetFileName($sourceUri.AbsolutePath)
        if ([string]::IsNullOrWhiteSpace($leaf) -or $leaf -notmatch '(?i)\.(png|jpe?g|gif|svg|webp|bmp|tiff?)$') {
            continue
        }

        $safeLeaf = [regex]::Replace([Uri]::UnescapeDataString($leaf), '[^A-Za-z0-9._-]', '_')
        $sha256 = [Security.Cryptography.SHA256]::Create()
        try {
            $hashBytes = $sha256.ComputeHash(
                [Text.Encoding]::UTF8.GetBytes($sourceUri.AbsoluteUri)
            )
        } finally {
            $sha256.Dispose()
        }
        $hash = ([BitConverter]::ToString($hashBytes) -replace '-', '').ToLowerInvariant()
        $numericPrefix = (([Convert]::ToUInt64($hash.Substring(0, 15), 16) % 9000000000) + 1000000000)
        [pscustomobject][ordered]@{
            SourceUrl = $sourceUri.AbsoluteUri
            OutputFileName = "$numericPrefix-$safeLeaf"
            DestinationRelativePath = "$assetFolder/$numericPrefix-$safeLeaf"
            OutputType = "ImageWebPart"
        }
    }
}

function Save-SpPageImageAssets {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$WebpartContentPath,
        [Parameter(Mandatory = $true)][string]$SourcePageUrl,
        [Parameter(Mandatory = $true)][string]$TargetPageServerRelativeUrl,
        [Parameter(Mandatory = $true)][string]$OutputDir,
        [Parameter(Mandatory = $true)][string]$ManifestPath,
        [switch]$UseDefaultCredentials,
        [pscredential]$Credential
    )

    if (-not (Test-Path -LiteralPath $WebpartContentPath -PathType Leaf)) {
        throw "Web-part content file was not found: $WebpartContentPath"
    }
    $webparts = @(Get-Content -LiteralPath $WebpartContentPath -Raw | ConvertFrom-Json)
    $pageUri = [Uri]$SourcePageUrl
    $pageWebparts = @($webparts | Where-Object {
        $webpartUrl = [string]$_.PageUrl
        if ([string]::IsNullOrWhiteSpace($webpartUrl)) {
            return $false
        }
        try {
            ([Uri]::new($pageUri, $webpartUrl)).AbsolutePath -eq $pageUri.AbsolutePath
        } catch {
            throw "Invalid web-part PageUrl '$webpartUrl' in $WebpartContentPath."
        }
    })
    $references = [System.Collections.Generic.List[object]]::new()
    foreach ($webpart in $pageWebparts) {
        $pageUrl = if ([string]::IsNullOrWhiteSpace([string]$webpart.PageUrl)) {
            $SourcePageUrl
        } else {
            [Uri]::new([Uri]$SourcePageUrl, [string]$webpart.PageUrl).AbsoluteUri
        }
        foreach ($reference in @(Get-SpPageImageReferences `
            -Html ([string]$webpart.Content) `
            -PageUrl $pageUrl `
            -TargetPageServerRelativeUrl $TargetPageServerRelativeUrl)) {
            if (-not @($references | Where-Object SourceUrl -eq $reference.SourceUrl)) {
                $references.Add([pscustomobject][ordered]@{
                    SourceWebPartId = [string]$webpart.WebPartId
                    SourceUrl = $reference.SourceUrl
                    OutputFileName = $reference.OutputFileName
                    DestinationRelativePath = $reference.DestinationRelativePath
                    OutputType = $reference.OutputType
                })
            }
        }
    }

    if (-not (Test-Path -LiteralPath $OutputDir -PathType Container)) {
        New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    }
    $auth = if ($references.Count -gt 0) {
        Get-SpImageRequestCredentials -UseDefaultCredentials:$UseDefaultCredentials -Credential $Credential
    } else {
        @{}
    }
    foreach ($reference in $references) {
        $destination = Join-Path $OutputDir $reference.OutputFileName
        $request = @{ Uri = $reference.SourceUrl; OutFile = $destination; ErrorAction = "Stop" }
        foreach ($key in $auth.Keys) { $request[$key] = $auth[$key] }
        Invoke-WebRequest @request
        if (-not (Test-Path -LiteralPath $destination -PathType Leaf)) {
            throw "Image download did not produce an output file: $destination"
        }
    }

    $parent = Split-Path -Parent $ManifestPath
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    $manifestJson = if ($references.Count -eq 0) {
        "[]"
    } else {
        @($references) | ConvertTo-Json -Depth 6
    }
    $manifestJson | Set-Content -LiteralPath $ManifestPath -Encoding UTF8
    return @($references)
}

if ($MyInvocation.InvocationName -ne ".") {
    $spoConfig = Read-SpoConfiguration -Path $ConfigPath
    if ($null -eq $spoConfig.Source -or [string]::IsNullOrWhiteSpace([string]$spoConfig.Source.SiteUrl)) {
        throw "Blocking configuration failure: Source.SiteUrl is missing in $($spoConfig.Path)."
    }
    if ($spoConfig.Source.ReadOnly -ne $true) {
        throw "Blocking configuration failure: Source.ReadOnly must explicitly be `$true."
    }
    if (-not [string]::IsNullOrWhiteSpace($SourcePageUrl) -and
        ([Uri]$SourcePageUrl).Host -ne ([Uri][string]$spoConfig.Source.SiteUrl).Host) {
        throw "SourcePageUrl host must match Source.SiteUrl ($($spoConfig.Source.SiteUrl))."
    }
    if ([string]::IsNullOrWhiteSpace($WebpartContentPath) -or
        [string]::IsNullOrWhiteSpace($SourcePageUrl) -or
    [string]::IsNullOrWhiteSpace($TargetPageServerRelativeUrl) -or
    [string]::IsNullOrWhiteSpace($OutputDir) -or
        [string]::IsNullOrWhiteSpace($ManifestPath)) {
        throw "WebpartContentPath, SourcePageUrl, OutputDir, and ManifestPath are required."
    }
    Save-SpPageImageAssets `
        -WebpartContentPath $WebpartContentPath `
        -SourcePageUrl $SourcePageUrl `
        -TargetPageServerRelativeUrl $TargetPageServerRelativeUrl `
        -OutputDir $OutputDir `
        -ManifestPath $ManifestPath `
        -UseDefaultCredentials:$UseDefaultCredentials `
        -Credential $Credential
}
