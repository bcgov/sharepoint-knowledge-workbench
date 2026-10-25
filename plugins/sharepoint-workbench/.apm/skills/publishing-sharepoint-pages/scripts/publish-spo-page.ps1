<#
.SYNOPSIS
Publishes one prepared modern SharePoint page package through PnP.PowerShell.

.DESCRIPTION
Reads the validated local publication package produced by
new-spo-page-publication-dry-run.ps1. By default it emits the exact tenant
operations without connecting to SharePoint. Real writes require -Execute and
the PUBLISH-SPO-PAGE confirmation token.

If a CreateOnly package's target page already exists, an interactive run asks
[O]verwrite (backup first) or [C]ancel; -Force overwrites without asking; a
non-interactive run without -Force refuses before any write. Overwrite backs up
the page first unless -ExistingPageBackupAction NoBackup.

.KEY INPUT DEPENDENCIES
- Publication package containing validated assets and page components. An
  ImageWebPart may carry ExistingImageUrl (a server-relative image already on the
  target site) instead of AssetPath; it is placed directly and needs no upload.
- -ConfigPath: config-spo-<env>.psd1 supplying Connection.SiteUrl/ClientId/TenantId
- PnP.PowerShell when executing

.OUTPUTS
- JSON execution plan, or JSON results after a gated tenant publication

.FUNCTION INDEX
Get-SpoPageIdentity, Get-SpoAssetServerRelativePath, Get-SpoImagePixelSize,
Get-SpoImageProportionalHeight, Get-SpoImageComponentUrl,
ConvertTo-SpoPageHtml,
New-SpoInlineImageHtml, Get-SpoInlineImageAlignment,
Get-SpoInlineImageTableCellWidth, ConvertTo-SpoPageInlineImages,
Test-SpoPublicationPackageAssets, Read-SpoConfiguration, Publish-SpoPage.

.EXAMPLE
pwsh -File .\plugins\sp-migration\scripts\publication\publish-spo-page.ps1 `
  -ConfigPath .\config-spo-dev.psd1 `
  -PackagePath .\page-publication-package.json

.EXAMPLE
# Republish over an existing page (backs it up first) without the prompt
pwsh -File .\plugins\sp-migration\scripts\publication\publish-spo-page.ps1 `
  -ConfigPath .\config-spo-dev.psd1 -PackagePath .\package\package.json `
  -Execute -ConfirmToken PUBLISH-SPO-PAGE -Force
#>

[CmdletBinding()]
param(
    [string]$PackagePath,
    [string]$ConfigPath,
    [switch]$Execute,
    [switch]$RecoverPartialPage,
    [switch]$UseExistingConnection,
    [switch]$LibraryMode,
    [string]$ConfirmToken,
    [ValidateSet("Backup", "NoBackup")]
    [string]$ExistingPageBackupAction = "Backup",
    [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

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

function Get-SpoPageIdentity {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string]$PageServerRelativeUrl)

    $segments = $PageServerRelativeUrl.Trim("/").Split("/")
    if ($segments.Count -lt 2 -or $segments[0] -ne "SitePages") {
        throw "Target page path must start with '/SitePages/'."
    }

    $pageName = [System.IO.Path]::GetFileNameWithoutExtension($segments[-1])
    $folder = if ($segments.Count -gt 2) {
        $segments[1..($segments.Count - 2)] -join "/"
    } else {
        ""
    }

    return [pscustomobject]@{
        Name       = $pageName
        Folder     = $folder
        CreateName = if ($folder) { "$folder/$pageName" } else { $pageName }
    }
}

function Get-SpoAssetServerRelativePath {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$SiteUrl,
        [Parameter(Mandatory = $true)][string]$AssetPath
    )

    $uri = [System.Uri]("$($SiteUrl.TrimEnd('/'))/$($AssetPath.TrimStart('/'))")
    return $uri.AbsolutePath
}

# Returns the server-relative URL an Image web part points at: an image already on the
# target site (ExistingImageUrl, no upload) or the package's uploaded asset (AssetPath).
function Get-SpoImagePixelSize {
    # Reads pixel width/height from PNG, GIF or JPEG header bytes; $null when unknown.
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][AllowEmptyCollection()][byte[]]$Bytes)

    $b = $Bytes
    if ($b.Length -ge 24 -and $b[0] -eq 0x89 -and $b[1] -eq 0x50 -and $b[2] -eq 0x4E -and $b[3] -eq 0x47) {
        $w = ([int]$b[16] -shl 24) -bor ([int]$b[17] -shl 16) -bor ([int]$b[18] -shl 8) -bor [int]$b[19]
        $h = ([int]$b[20] -shl 24) -bor ([int]$b[21] -shl 16) -bor ([int]$b[22] -shl 8) -bor [int]$b[23]
        return [pscustomobject]@{ Width = $w; Height = $h }
    }
    if ($b.Length -ge 10 -and $b[0] -eq 0x47 -and $b[1] -eq 0x49 -and $b[2] -eq 0x46) {
        return [pscustomobject]@{ Width = [int]$b[6] -bor ([int]$b[7] -shl 8); Height = [int]$b[8] -bor ([int]$b[9] -shl 8) }
    }
    if ($b.Length -ge 4 -and $b[0] -eq 0xFF -and $b[1] -eq 0xD8) {
        $i = 2
        while ($i + 9 -lt $b.Length) {
            if ($b[$i] -ne 0xFF) { $i++; continue }
            $marker = $b[$i + 1]
            if ($marker -eq 0xFF) { $i++; continue }
            if ($marker -in @(0xD8, 0x01) -or ($marker -ge 0xD0 -and $marker -le 0xD7)) { $i += 2; continue }
            $length = ([int]$b[$i + 2] -shl 8) -bor [int]$b[$i + 3]
            if ($marker -in @(0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF)) {
                $h = ([int]$b[$i + 5] -shl 8) -bor [int]$b[$i + 6]
                $w = ([int]$b[$i + 7] -shl 8) -bor [int]$b[$i + 8]
                return [pscustomobject]@{ Width = $w; Height = $h }
            }
            $i += 2 + $length
        }
    }
    return $null
}

function Get-SpoImageProportionalHeight {
    # Height that keeps the published image's aspect ratio at the given width; 0 when unknown.
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$ImageUrl,
        [Parameter(Mandatory = $true)][int]$Width
    )

    try {
        $stream = Get-PnPFile -Url $ImageUrl -AsMemoryStream -ErrorAction Stop
        $size = Get-SpoImagePixelSize -Bytes ($stream.ToArray())
    } catch {
        $size = $null
    }
    if (-not $size -or $size.Width -le 0 -or $size.Height -le 0) { return 0 }
    return [int][Math]::Round($Width * $size.Height / $size.Width)
}

function Get-SpoImageNaturalSize {
    # The published file's own pixel size; $null when unreadable.
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string]$ImageUrl)

    try {
        $stream = Get-PnPFile -Url $ImageUrl -AsMemoryStream -ErrorAction Stop
        $size = Get-SpoImagePixelSize -Bytes ($stream.ToArray())
    } catch {
        return $null
    }
    if (-not $size -or $size.Width -le 0 -or $size.Height -le 0) { return $null }
    return $size
}

function Get-SpoImageComponentUrl {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$SiteUrl,
        [Parameter(Mandatory = $true)]$Component
    )

    if ($Component.PSObject.Properties["ExistingImageUrl"] -and
        -not [string]::IsNullOrWhiteSpace([string]$Component.ExistingImageUrl)) {
        $existing = [string]$Component.ExistingImageUrl
        $sitePath = ([System.Uri]$SiteUrl).AbsolutePath.TrimEnd('/')
        if (-not $existing.StartsWith("$sitePath/", [System.StringComparison]::OrdinalIgnoreCase) -or
            $existing -match "(^|/)\.\.?(/|$)") {
            throw "ExistingImageUrl must be a server-relative path on the target site ($sitePath/...): $existing"
        }
        return $existing
    }
    return Get-SpoAssetServerRelativePath -SiteUrl $SiteUrl -AssetPath ([string]$Component.AssetPath)
}

function ConvertTo-SpoWebPartPropertyTable {
    [CmdletBinding()]
    param([AllowNull()]$InputObject)

    if ($null -eq $InputObject -or $InputObject -is [string] -or $InputObject -is [ValueType]) { return $InputObject }
    if ($InputObject -is [System.Collections.IEnumerable] -and $InputObject -isnot [System.Collections.IDictionary]) {
        return , @($InputObject | ForEach-Object { ConvertTo-SpoWebPartPropertyTable -InputObject $_ })
    }
    $table = @{}
    $pairs = if ($InputObject -is [System.Collections.IDictionary]) {
        $InputObject.GetEnumerator() | ForEach-Object { @{ Name = $_.Key; Value = $_.Value } }
    } else {
        $InputObject.PSObject.Properties | ForEach-Object { @{ Name = $_.Name; Value = $_.Value } }
    }
    foreach ($pair in $pairs) { $table[[string]$pair.Name] = ConvertTo-SpoWebPartPropertyTable -InputObject $pair.Value }
    return $table
}

function Get-SpoPageColumn {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$SectionTemplate,
        [AllowEmptyString()][string]$SourceZoneId
    )

    if ($SectionTemplate -eq "OneColumn") {
        return 1
    }
    if ($SectionTemplate -eq "TwoColumnLeft") {
        switch ($SourceZoneId) {
            "LeftZone" { return 1 }
            "RightZone" { return 2 }
        }
    }
    if ($SectionTemplate -eq "TwoColumnRight") {
        switch ($SourceZoneId) {
            "LeftZone" { return 2 }
            "RightZone" { return 1 }
        }
    }
    throw "Two-column publication requires a recognized source zone; received '$SourceZoneId' for '$SectionTemplate'."
}

function ConvertTo-SpoPageHtml {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$Html,
        [Parameter(Mandatory = $true)][string]$SiteUrl,
        [string]$PageServerRelativeUrl
    )

    # Page-relative image and link sources (../Library/...) become server-relative so they resolve
    # correctly on whichever site (DEV/TEST/PROD) the package is published to.
    if (-not [string]::IsNullOrWhiteSpace($PageServerRelativeUrl)) {
        $pageUri = [Uri]("https://host" + $PageServerRelativeUrl)
        $Html = [regex]::Replace(
            $Html,
            '(?i)(?<prefix>\b(?:src|href)\s*=\s*["''])(?<path>\.\.?/[^"'']+)(?<suffix>["''])',
            {
                param($match)
                $target = [Uri]::new($pageUri, $match.Groups["path"].Value)
                # AbsolutePath alone drops "?MessageID=71"; keep the query string and fragment.
                $resolved = $target.AbsolutePath + $target.Query + $target.Fragment
                $match.Groups["prefix"].Value + $resolved + $match.Groups["suffix"].Value
            }
        )
    }

    # Ensure document links (.pdf, .docx, .xlsx, etc.) and external links have target="_blank"
    $Html = [regex]::Replace(
        $Html,
        '(?is)<a\b(?<attrs>[^>]*)>',
        {
            param($m)
            $attrs = $m.Groups["attrs"].Value
            $hrefM = [regex]::Match($attrs, '(?i)\bhref\s*=\s*["''](?<href>[^"'']+)["'']')
            if ($hrefM.Success) {
                $href = $hrefM.Groups["href"].Value
                $isDoc = $href -match '(?i)\.(pdf|docx?|xlsx?|pptx?)$'
                $isExternal = $href -match '^https?://'
                if (($isDoc -or $isExternal) -and $attrs -notmatch '(?i)\btarget\s*=') {
                    $attrs += ' target="_blank"'
                }
            }
            return "<a$attrs>"
        }
    )
    return [regex]::Replace(
        $Html,
        '(?i)(?<prefix>\bsrc\s*=\s*["''])(?<path>SiteAssets/[^"'']+)(?<suffix>["''])',
        {
            param($match)
            $match.Groups["prefix"].Value +
                (Get-SpoAssetServerRelativePath -SiteUrl $SiteUrl -AssetPath $match.Groups["path"].Value) +
                $match.Groups["suffix"].Value
        }
    )
}

function Get-SpoTitleBannerTemplate {
    # Canvas shapes of the title banner live in assets/title-banner-canvas.json (copied from the
    # hand-built DEV Administration/Accessibility-Resources page), not in this script.
    [CmdletBinding()]
    param()

    $candidates = @(
        (Join-Path $PSScriptRoot "..\..\assets\title-banner-canvas.json"),
        (Join-Path $PSScriptRoot "..\assets\title-banner-canvas.json")
    )
    $path = $candidates | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } | Select-Object -First 1
    if (-not $path) {
        throw "Title banner template was not found; looked in: $($candidates -join '; ')"
    }
    return Get-Content -LiteralPath $path -Raw -Encoding UTF8 | ConvertFrom-Json
}

function ConvertTo-SpoCanvasAttributeValue {
    # Encodes an object the way SharePoint stores it in a canvas attribute (data-sp-controldata).
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)]$InputObject)

    $json = ConvertTo-Json -InputObject $InputObject -Compress -Depth 12
    $json = $json.Replace('\u003c', '<').Replace('\u003e', '>').Replace('\u0026', '&').Replace('\u0027', "'")
    return $json.Replace('&', '&amp;').Replace('"', '&quot;').Replace('<', '&lt;').Replace('>', '&gt;').
        Replace('{', '&#123;').Replace('}', '&#125;').Replace(':', '&#58;')
}

function Split-SpoCanvasControls {
    # Splits a canvas string into the text before the first control, each control, and the closing div.
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][AllowEmptyString()][string]$Content)

    $starts = @([regex]::Matches($Content, [regex]::Escape('<div data-sp-canvascontrol=""')) | ForEach-Object { $_.Index })
    if ($starts.Count -eq 0) {
        return [pscustomobject]@{ Prefix = $Content; Controls = @(); Suffix = "" }
    }
    $suffixMatch = [regex]::Match($Content, '</div>\s*$')
    $end = if ($suffixMatch.Success) { $suffixMatch.Index } else { $Content.Length }
    $controls = for ($i = 0; $i -lt $starts.Count; $i++) {
        $to = if ($i + 1 -lt $starts.Count) { $starts[$i + 1] } else { $end }
        $Content.Substring($starts[$i], $to - $starts[$i])
    }
    return [pscustomobject]@{
        Prefix   = $Content.Substring(0, $starts[0])
        Controls = @($controls)
        Suffix   = $Content.Substring($end)
    }
}

function ConvertTo-SpoCanvasWithTitleBanner {
    # Moves the page title into the title-zone Banner web part (the model the web team's hand-built
    # Administration pages use) so the title zone can carry a theme colour, which PnP cannot set.
    # Body zones move down one, the old Title Region is removed from LayoutWebpartsContent.
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$CanvasContent,
        [AllowEmptyString()][string]$LayoutWebpartsContent = "",
        [Parameter(Mandatory = $true)][string]$Title,
        [int]$ZoneThemeIndex = 3,
        [string]$LayoutType = "NoImage",
        [string]$TextAlignment = "Left",
        [bool]$ShowPublishDate = $true
    )

    $template = Get-SpoTitleBannerTemplate
    $unchanged = [pscustomobject]@{ CanvasContent = $CanvasContent; LayoutWebpartsContent = $LayoutWebpartsContent; BannerZoneId = "" }
    if ($CanvasContent.Contains("&quot;webPartId&quot;&#58;&quot;$($template.bannerWebPartId)&quot;")) {
        return $unchanged
    }

    $zoneId = [guid]::NewGuid().ToString()
    $controlId = [guid]::NewGuid().ToString()
    $bannerControl = $template.bannerControl
    $controlData = $bannerControl.controlData
    $controlData.position.zoneId = $zoneId
    $controlData.id = $controlId
    $webPartData = $bannerControl.webPartData
    $webPartData.instanceId = $controlId
    $props = $webPartData.properties
    $props.title = $Title
    $props.layoutType = $LayoutType
    $props.textAlignment = $TextAlignment
    $props.showPublishDate = $ShowPublishDate
    $props.htmlTitle = ([string]$template.titleHtml).Replace("{title}", [System.Net.WebUtility]::HtmlEncode($Title))

    $bannerHtml = '<div data-sp-canvascontrol="" data-sp-canvasdataversion="' + $bannerControl.canvasDataVersion +
        '" data-sp-controldata="' + (ConvertTo-SpoCanvasAttributeValue -InputObject $controlData) +
        '"><div data-sp-webpart="" data-sp-webpartdataversion="' + $bannerControl.webPartDataVersion +
        '" data-sp-webpartdata="' + (ConvertTo-SpoCanvasAttributeValue -InputObject $webPartData) +
        '"><div data-sp-componentid="' + $bannerControl.componentId + '"></div><div data-sp-htmlproperties=""></div></div></div>'

    $theme = $template.zoneThemeControl
    $zoneTheme = [pscustomobject]@{ lightIndex = $ZoneThemeIndex; darkIndex = $ZoneThemeIndex }
    $theme.webPartData.properties.zoneThemeIndex | Add-Member -NotePropertyName $zoneId -NotePropertyValue $zoneTheme
    $zoneThemeHtml = '<div data-sp-canvascontrol="" data-sp-canvasdataversion="' + $theme.canvasDataVersion +
        '" data-sp-controldata="' + (ConvertTo-SpoCanvasAttributeValue -InputObject $theme.controlData) +
        '"><div data-sp-webpart="" data-sp-webpartdataversion="' + $theme.webPartDataVersion +
        '" data-sp-webpartdata="' + (ConvertTo-SpoCanvasAttributeValue -InputObject $theme.webPartData) +
        '"><div data-sp-componentid=""></div><div data-sp-htmlproperties=""></div></div></div>'

    $parts = Split-SpoCanvasControls -Content $CanvasContent
    $shifted = foreach ($control in $parts.Controls) {
        [regex]::Replace($control, '(&quot;zoneIndex&quot;&#58;)(\d+)', [System.Text.RegularExpressions.MatchEvaluator]{
            param($m)
            $m.Groups[1].Value + ([int]$m.Groups[2].Value + 1)
        })
    }
    $newCanvas = $parts.Prefix + $bannerHtml + (@($shifted) -join "") + $zoneThemeHtml + $parts.Suffix

    $layoutParts = Split-SpoCanvasControls -Content $LayoutWebpartsContent
    $titleRegion = "&quot;title&quot;&#58;&quot;$($template.titleRegionTitle)&quot;"
    $keptLayout = @($layoutParts.Controls | Where-Object { -not $_.Contains($titleRegion) })
    $newLayout = if ($layoutParts.Controls.Count -eq 0) {
        $LayoutWebpartsContent
    } elseif ($keptLayout.Count -eq 0) {
        "<div></div>"
    } else {
        $layoutParts.Prefix + ($keptLayout -join "") + $layoutParts.Suffix
    }

    return [pscustomobject]@{ CanvasContent = $newCanvas; LayoutWebpartsContent = $newLayout; BannerZoneId = $zoneId }
}

function New-SpoInlineImageHtml {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$ImageUrl,
        [Parameter(Mandatory = $true)][string]$WebId,
        [Parameter(Mandatory = $true)][string]$SiteId,
        [Parameter(Mandatory = $true)][string]$ListId,
        [Parameter(Mandatory = $true)][string]$UniqueId,
        [int]$Width = 0,
        [int]$Height = 0,
        [int]$WidthPercentage = 100,
        [ValidateSet("Left", "Center", "Right")][string]$Alignment = "Left",
        [string]$AlternativeText = "",
        [string]$Caption = "",
        [string]$LinkUrl = ""
    )

    return '<div class="imagePlugin" style="background-color:transparent;position:relative;" data-alignment="' +
        $Alignment + '" data-imageurl="' +
        $ImageUrl + '" data-uploading="0" data-height="' + $Height + '" data-width="' + $Width +
        '" data-imagenaturalheight="' + $Height + '" data-imagenaturalwidth="' + $Width +
        '" data-widthpercentage="' + $WidthPercentage + '" data-webid="' + $WebId +
        '" data-siteid="' + $SiteId + '" data-listid="' + $ListId + '" data-uniqueid="' + $UniqueId +
        '" data-isoverlaytextenabled="false" data-captiontext="' + $Caption +
        '" data-alttext="' + $AlternativeText + '" data-linkurl="' + $LinkUrl + '"></div>'
}

function Get-SpoInlineImageAlignment {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$Html,
        [Parameter(Mandatory = $true)][int]$ImageIndex
    )

    $prefix = $Html.Substring(0, $ImageIndex)
    $openElements = [System.Collections.Generic.List[object]]::new()
    $alignment = "Left"
    $tagMatches = [regex]::Matches(
        $prefix,
        '(?is)</?(?<tag>div|td|th|p|li|center)\b(?<attributes>[^>]*)>'
    )

    foreach ($tagMatch in $tagMatches) {
        $tag = $tagMatch.Groups["tag"].Value.ToLowerInvariant()
        if ($tagMatch.Value -match '(?is)^</') {
            for ($index = $openElements.Count - 1; $index -ge 0; $index--) {
                if ($openElements[$index].Tag -eq $tag) {
                    $openElements.RemoveAt($index)
                    break
                }
            }
            continue
        }
        if ($tagMatch.Value -match '(?is)/\s*>$') {
            continue
        }
        $openElements.Add([pscustomobject]@{
            Tag        = $tag
            Attributes = $tagMatch.Groups["attributes"].Value
        })
    }

    foreach ($element in $openElements) {
        $candidate = $null
        if ($element.Tag -eq "center") {
            $candidate = "Center"
        } else {
            $styleMatch = [regex]::Match(
                $element.Attributes,
                '(?i)\btext-align\s*:\s*(?<value>left|center|right)\b'
            )
            if (-not $styleMatch.Success) {
                $styleMatch = [regex]::Match(
                    $element.Attributes,
                    '(?i)\balign\s*=\s*["'']?\s*(?<value>left|center|right)\b'
                )
            }
            if ($styleMatch.Success) {
                $candidate = [cultureinfo]::InvariantCulture.TextInfo.ToTitleCase(
                    $styleMatch.Groups["value"].Value.ToLowerInvariant()
                )
            }
        }
        if ($candidate) {
            $alignment = $candidate
        }
    }

    return $alignment
}

function Get-SpoInlineImageDimensions {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$ImageTag,
        [string]$ImagePath
    )

    $styleMatch = [regex]::Match($ImageTag, '(?i)\bstyle\s*=\s*["'']([^"'']*)["'']')
    $style = if ($styleMatch.Success) { $styleMatch.Groups[1].Value } else { "" }
    $getDimension = {
        param([string]$Name)
        $match = [regex]::Match($style, "(?i)\b$Name\s*:\s*(\d+)\s*px")
        if (-not $match.Success) {
            $match = [regex]::Match($ImageTag, "(?i)\b$Name\s*=\s*['""]?(\d+)(?:px)?['""]?")
        }
        if ($match.Success) { return [int]$match.Groups[1].Value }
        return 0
    }

    $width = & $getDimension "width"
    $height = & $getDimension "height"
    $intrinsicWidth = 0
    $intrinsicHeight = 0
    if (-not [string]::IsNullOrWhiteSpace($ImagePath) -and
        (Test-Path -LiteralPath $ImagePath -PathType Leaf)) {
        # Header-byte read keeps this cross-platform (System.Drawing/GDI+ is Windows only).
        $pixelSize = Get-SpoImagePixelSize -Bytes ([System.IO.File]::ReadAllBytes($ImagePath))
        if ($pixelSize) {
            $intrinsicWidth = $pixelSize.Width
            $intrinsicHeight = $pixelSize.Height
        }
    }
    if ($width -eq 0 -and $height -eq 0) {
        $width = $intrinsicWidth
        $height = $intrinsicHeight
    } elseif ($width -eq 0 -and $height -gt 0 -and $intrinsicHeight -gt 0) {
        $width = [int][math]::Round($height * $intrinsicWidth / $intrinsicHeight)
    } elseif ($height -eq 0 -and $width -gt 0 -and $intrinsicWidth -gt 0) {
        $height = [int][math]::Round($width * $intrinsicHeight / $intrinsicWidth)
    }

    return [pscustomobject]@{
        Width  = $width
        Height = $height
    }
}

function Get-SpoInlineImageSizing {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$ImageTag,
        [string]$ImagePath,
        [Parameter(Mandatory = $true)][int]$ContainingWidth
    )

    $dimensions = Get-SpoInlineImageDimensions `
        -ImageTag $ImageTag `
        -ImagePath $ImagePath
    if ($ContainingWidth -le 0 -or $dimensions.Width -le 0 -or $dimensions.Height -le 0) {
        throw "Image sizing requires positive image and containing dimensions."
    }

    if ($dimensions.Width -le $ContainingWidth) {
        $width = $dimensions.Width
        $mode = "IntrinsicSize"
    } else {
        $width = $ContainingWidth
        $mode = "FitContainer"
    }
    $height = [int][math]::Round(
        $width * $dimensions.Height / $dimensions.Width
    )
    $widthPercentage = [int][math]::Round(
        [math]::Min(100, ($width / $ContainingWidth) * 100)
    )

    return [pscustomobject]@{
        Width           = $width
        Height          = $height
        WidthPercentage = $widthPercentage
        Mode            = $mode
    }
}

# Example: a 200px image in a 25% table cell with a 1271px page base.
# Result: a 318px containing width for percentage sizing.
function Get-SpoInlineImageTableCellWidth {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$Html,
        [Parameter(Mandatory = $true)][int]$ImageIndex,
        [Parameter(Mandatory = $true)][int]$BaseWidth
    )

    $prefix = $Html.Substring(0, $ImageIndex)
    $cellStarts = @([regex]::Matches($prefix, '(?is)<(?:td|th)\b[^>]*>'))
    $cellEnds = @([regex]::Matches($prefix, '(?is)</(?:td|th)\s*>'))
    if ($cellStarts.Count -eq 0 -or
        ($cellEnds.Count -gt 0 -and $cellStarts[-1].Index -le $cellEnds[-1].Index)) {
        return 0
    }

    $cellStart = $cellStarts[-1].Index
    $tableStarts = @([regex]::Matches($prefix, '(?is)<table\b[^>]*>'))
    $tableEnds = @([regex]::Matches($prefix, '(?is)</table\s*>'))
    $tableStart = -1
    foreach ($table in $tableStarts) {
        if ($tableEnds.Count -eq 0 -or $table.Index -gt $tableEnds[-1].Index) {
            $tableStart = $table.Index
        }
    }
    if ($tableStart -lt 0) {
        return 0
    }

    $tablePrefix = $Html.Substring($tableStart, $ImageIndex - $tableStart)
    $colgroups = @([regex]::Matches(
        $tablePrefix,
        '(?is)<colgroup\b[^>]*>(?<content>.*?)</colgroup\s*>'
    ))
    if ($colgroups.Count -eq 0) {
        return 0
    }

    $columnWidths = @(
        foreach ($column in [regex]::Matches(
            $colgroups[-1].Groups["content"].Value,
            '(?is)<col\b(?<attributes>[^>]*)>'
        )) {
            $widthMatch = [regex]::Match(
                $column.Groups["attributes"].Value,
                '(?i)\bwidth\s*:\s*(\d+(?:\.\d+)?)\s*%'
            )
            if (-not $widthMatch.Success) {
                $widthMatch = [regex]::Match(
                    $column.Groups["attributes"].Value,
                    '(?i)\bwidth\s*=\s*["''](\d+(?:\.\d+)?)\s*%["'']'
                )
            }
            if ($widthMatch.Success) {
                [double]$widthMatch.Groups[1].Value
            } else {
                0
            }
        }
    )
    if ($columnWidths.Count -eq 0 -or ($columnWidths | Measure-Object -Sum).Sum -le 0) {
        return 0
    }

    $rowStarts = @([regex]::Matches($prefix, '(?is)<tr\b[^>]*>'))
    if ($rowStarts.Count -eq 0) {
        return 0
    }
    $rowStart = $rowStarts[-1].Index
    $rowPrefix = $Html.Substring($rowStart, $cellStart - $rowStart)
    $columnStart = 0
    foreach ($cell in [regex]::Matches($rowPrefix, '(?is)<(?:td|th)\b(?<attributes>[^>]*)>')) {
        $spanMatch = [regex]::Match(
            $cell.Groups["attributes"].Value,
            '(?i)\bcolspan\s*=\s*["'']?(\d+)'
        )
        $columnStart += if ($spanMatch.Success) {
            [int]$spanMatch.Groups[1].Value
        } else {
            1
        }
    }

    $currentSpanMatch = [regex]::Match(
        $cellStarts[-1].Value,
        '(?i)\bcolspan\s*=\s*["'']?(\d+)'
    )
    $currentSpan = if ($currentSpanMatch.Success) {
        [int]$currentSpanMatch.Groups[1].Value
    } else {
        1
    }
    if ($columnStart -ge $columnWidths.Count) {
        return 0
    }

    $columnEnd = [math]::Min($columnStart + $currentSpan, $columnWidths.Count)
    $columnPercentage = 0
    for ($index = $columnStart; $index -lt $columnEnd; $index++) {
        $columnPercentage += $columnWidths[$index]
    }
    if ($columnPercentage -le 0) {
        return 0
    }
    return [int][math]::Round($BaseWidth * $columnPercentage / 100)
}

function Get-SpoInlineImageContainingWidth {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$Html,
        [Parameter(Mandatory = $true)][int]$ImageIndex,
        [int]$BaseWidth = 1271
    )

    $tableWidth = Get-SpoInlineImageTableCellWidth `
        -Html $Html `
        -ImageIndex $ImageIndex `
        -BaseWidth $BaseWidth
    if ($tableWidth -gt 0) {
        return $tableWidth
    }

    $prefix = $Html.Substring(0, $ImageIndex)
    $cellStarts = @([regex]::Matches($prefix, '(?is)<td\b[^>]*>'))
    $cellEnds = @([regex]::Matches($prefix, '(?is)</td\s*>'))
    $lastCellStart = if ($cellStarts.Count -gt 0) {
        $cellStarts[-1].Index
    } else {
        -1
    }
    $lastCellEnd = if ($cellEnds.Count -gt 0) {
        $cellEnds[-1].Index
    } else {
        -1
    }
    if ($lastCellStart -le $lastCellEnd) {
        return $BaseWidth
    }

    $cellTag = $cellStarts[-1].Value
    $widthMatch = [regex]::Match(
        $cellTag,
        '(?i)\bwidth\s*:\s*(\d+(?:\.\d+)?)\s*%'
    )
    if (-not $widthMatch.Success) {
        $widthMatch = [regex]::Match(
            $cellTag,
            '(?i)\bwidth\s*=\s*["''](\d+(?:\.\d+)?)\s*%["'']'
        )
    }
    if ($widthMatch.Success) {
        return [int][math]::Round(
            $BaseWidth * [double]$widthMatch.Groups[1].Value / 100
        )
    }
    # A cell sized in pixels (the editor-safe converter output) is its own containing width.
    $pixelMatch = [regex]::Match($cellTag, '(?i)\bwidth\s*:\s*(\d+(?:\.\d+)?)\s*px')
    if ($pixelMatch.Success) {
        return [int][math]::Min($BaseWidth, [math]::Round([double]$pixelMatch.Groups[1].Value))
    }
    return $BaseWidth
}

function Get-SpoSectionColumnWidth {
    # Pixel width of a section column, used as the base for inline-image sizing.
    [CmdletBinding()]
    param(
        [string]$SectionTemplate,
        [int]$Column = 1,
        [int]$FullWidth = 1271
    )

    $fraction = switch ($SectionTemplate) {
        "TwoColumn"      { 1 / 2 }
        "ThreeColumn"    { 1 / 3 }
        "TwoColumnLeft"  { if ($Column -eq 1) { 2 / 3 } else { 1 / 3 } }
        "TwoColumnRight" { if ($Column -eq 1) { 1 / 3 } else { 2 / 3 } }
        default          { 1 }
    }
    return [int][math]::Round($FullWidth * $fraction)
}

function ConvertTo-SpoPageInlineImages {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$Html,
        [Parameter(Mandatory = $true)][string]$SiteUrl,
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][object[]]$ImageMetadata,
        [int]$BaseWidth = 1271
    )

    $replaceImage = {
        param($tag, $linkUrl, $imageIndex, $currentHtml)
        $srcMatch = [regex]::Match($tag, '(?i)\bsrc\s*=\s*["'']([^"'']+)["'']')
        if (-not $srcMatch.Success) {
            throw "Image tag has no src attribute and cannot be converted to a SharePoint inline image."
        }

        $sourcePath = $srcMatch.Groups[1].Value
        $asset = @($ImageMetadata | Where-Object {
            ($_.PSObject.Properties["AssetPath"] -and $_.AssetPath -eq $sourcePath) -or
            ($_.PSObject.Properties["ServerRelativeUrl"] -and $_.ServerRelativeUrl -eq $sourcePath) -or
            ($_.PSObject.Properties["UploadPath"] -and $_.UploadPath -eq $sourcePath) -or
            ($_.PSObject.Properties["SourceUrl"] -and
                ([Uri]$_.SourceUrl).AbsolutePath -eq $sourcePath)
        }) | Select-Object -First 1
        if (-not $asset) {
            throw "No uploaded asset metadata matched image source: $sourcePath"
        }

        $containerWidth = Get-SpoInlineImageContainingWidth `
            -Html $currentHtml `
            -ImageIndex $imageIndex `
            -BaseWidth $BaseWidth
        $sizing = Get-SpoInlineImageSizing `
            -ImageTag $tag `
            -ImagePath $(if ($asset.PSObject.Properties["LocalPath"]) {
                [string]$asset.LocalPath
            } else {
                ""
            }) `
            -ContainingWidth $containerWidth
        $alignment = Get-SpoInlineImageAlignment `
            -Html $currentHtml `
            -ImageIndex $imageIndex
        $altMatch = [regex]::Match($tag, '(?i)\balt\s*=\s*["'']([^"'']*)["'']')
        $alt = if ($altMatch.Success) { $altMatch.Groups[1].Value } else { "" }
        return New-SpoInlineImageHtml `
            -ImageUrl ([string]$asset.ServerRelativeUrl) `
            -WebId ([string]$asset.WebId) `
            -SiteId ([string]$asset.SiteId) `
            -ListId ([string]$asset.ListId) `
            -UniqueId ([string]$asset.UniqueId) `
            -Width $sizing.Width `
            -Height $sizing.Height `
            -WidthPercentage $sizing.WidthPercentage `
            -Alignment $alignment `
            -AlternativeText $alt `
            -LinkUrl $linkUrl
    }

    $normalized = [regex]::Replace($Html, '(?is)<a\b(?<attributes>[^>]*)>\s*(?<image><img\b[^>]*>)\s*</a>', {
        param($match)
        $hrefMatch = [regex]::Match($match.Groups["attributes"].Value, '(?i)\bhref\s*=\s*["'']([^"'']*)["'']')
        $linkUrl = if ($hrefMatch.Success) { $hrefMatch.Groups[1].Value } else { "" }
        return & $replaceImage `
            $match.Groups["image"].Value `
            $linkUrl `
            $match.Groups["image"].Index `
            $Html
    })
    return [regex]::Replace($normalized, '(?is)<img\b[^>]*>', {
        param($match)
        return & $replaceImage $match.Value "" $match.Index $normalized
    })
}

function Test-SpoPublicationPackageAssets {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)]$Package)

    $assets = if ($null -eq $Package.Assets) { @() } else { @($Package.Assets) }
    $uploadPaths = @{}
    foreach ($asset in $assets) {
        if ($null -eq $asset -or
            [string]::IsNullOrWhiteSpace([string]$asset.LocalPath) -or
            [string]::IsNullOrWhiteSpace([string]$asset.UploadPath)) {
            throw "Every publication asset requires LocalPath and UploadPath."
        }
        $uploadPath = [string]$asset.UploadPath
        if ($uploadPath -notmatch "^/SiteAssets/" -or $uploadPath -match "(^|/)\.\.?(/|$)") {
            throw "Publication asset UploadPath must be a safe path under /SiteAssets/: $uploadPath"
        }
        if ($uploadPaths.ContainsKey($uploadPath)) {
            throw "Publication package contains duplicate asset UploadPath: $uploadPath"
        }
        $uploadPaths[$uploadPath] = $true
        if (-not (Test-Path -LiteralPath ([string]$asset.LocalPath) -PathType Leaf)) {
            throw "Local publication asset was not found: $($asset.LocalPath)"
        }
    }
    foreach ($component in @($Package.Components)) {
        if ([string]$component.OutputType -notin @("TextWebPart", "ImageWebPart", "SpfxWebPart")) {
            throw "Unsupported publication component type: $($component.OutputType)"
        }
        if ([string]$component.OutputType -eq "SpfxWebPart" -and
            [string]::IsNullOrWhiteSpace([string]$component.ComponentId)) {
            throw "SpfxWebPart component requires a ComponentId."
        }
        $usesExistingImage = $component.PSObject.Properties["ExistingImageUrl"] -and
            -not [string]::IsNullOrWhiteSpace([string]$component.ExistingImageUrl)
        if ([string]$component.OutputType -eq "ImageWebPart" -and -not $usesExistingImage -and
            [string]$component.AssetPath -notin @($assets | ForEach-Object { [string]$_.AssetPath })) {
            throw "Image publication component has no matching local asset: $($component.AssetPath)"
        }
    }
}

# Projects one PnP page component to the small set of scalar fields needed to recreate its
# layout. Nested objects are reduced to their Order, never serialised, because the raw
# component graph is deep and heavily linked.
function ConvertTo-SpoBackupComponent {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)]$Component)

    $scalar = {
        param($Value)
        if ($null -eq $Value) { return $null }
        if ($Value -is [string] -or $Value -is [ValueType]) { return $Value }
        return [string]$Value
    }
    $read = { param($Name) if ($Component.PSObject.Properties[$Name]) { & $scalar $Component.$Name } }
    $order = {
        param($Name)
        $nested = if ($Component.PSObject.Properties[$Name]) { $Component.$Name } else { $null }
        if ($nested -is [ValueType]) { return $nested }
        if ($nested -and $nested.PSObject.Properties["Order"]) { & $scalar $nested.Order }
    }

    return [ordered]@{
        Type         = $Component.GetType().Name
        InstanceId   = & $read "InstanceId"
        Order        = & $read "Order"
        Title        = & $read "Title"
        Text         = & $read "Text"
        WebPartId    = & $read "WebPartId"
        ControlType  = & $read "ControlType"
        PropertiesJson = & $read "PropertiesJson"
        Section      = & $order "Section"
        Column       = & $order "Column"
    }
}

# Fails the backup (and therefore the overwrite) instead of letting one slow step run unbounded.
# It can only act between steps; it cannot interrupt a single call that never returns.
function Assert-SpoBackupWithinDeadline {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][System.Diagnostics.Stopwatch]$Stopwatch,
        [Parameter(Mandatory = $true)][string]$Step,
        [int]$MaxSeconds = 120
    )

    if ($Stopwatch.Elapsed.TotalSeconds -gt $MaxSeconds) {
        throw "Backup exceeded $MaxSeconds seconds after step '$Step'; aborting before any destructive change."
    }
}

# Common full-recovery backup function shared by every overwrite path.
# Captures the existing page's raw .aspx, its page-component layout, the
# Site Pages list item metadata, its permission state (inherited vs. unique
# role assignments), and any already-published referenced assets the
# incoming package would also upload. Fails closed: any capture failure
# throws before the caller is allowed to delete the existing page.
function Backup-SpoExistingPage {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$SiteUrl,
        [Parameter(Mandatory = $true)][string]$PageServerRelativeUrl,
        [Parameter(Mandatory = $true)][string]$PageCreateName,
        [object[]]$PackageAssets = @(),
        [string]$BackupRoot
    )

    $pageFileName = [System.IO.Path]::GetFileName($PageServerRelativeUrl)
    $timestamp = (Get-Date -AsUTC).ToString("yyyyMMddTHHmmssfffZ")
    $backupId = "$([System.IO.Path]::GetFileNameWithoutExtension($pageFileName))-$timestamp"
    $root = if ([string]::IsNullOrWhiteSpace($BackupRoot)) {
        Join-Path (Join-Path (Join-Path (Get-Location).Path "temp") "page-migration-backups") $backupId
    } else {
        Join-Path $BackupRoot $backupId
    }
    New-Item -ItemType Directory -Path $root -Force | Out-Null
    $assetsDir = Join-Path $root "assets"
    $backupClock = [System.Diagnostics.Stopwatch]::StartNew()

    try {
        # 1. Raw page file.
        Get-PnPFile -Url $PageServerRelativeUrl -Path $root -FileName "page.aspx" -AsFile -Force -ErrorAction Stop | Out-Null
        Assert-SpoBackupWithinDeadline -Stopwatch $backupClock -Step "raw page file"
        # 2. Page component layout. Raw PnP component objects are deep, heavily linked graphs;
        # serialising them with a large -Depth stalls at 100% CPU, so only the fields needed to
        # recreate the layout are saved. The raw page.aspx above remains the full-fidelity copy.
        $pageObject = Get-PnPPage -Identity $PageCreateName -ErrorAction Stop
        $components = @(Get-PnPPageComponent -Page $PageCreateName -ErrorAction Stop)
        [ordered]@{
            PageServerRelativeUrl = $PageServerRelativeUrl
            Components            = @($components | ForEach-Object { ConvertTo-SpoBackupComponent -Component $_ })
        } | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $root "page-components.json") -Encoding UTF8
        Assert-SpoBackupWithinDeadline -Stopwatch $backupClock -Step "component layout"

        # 3. Site Pages list item metadata + permission state. The query must be recursive (a
        # library query otherwise sees only the root folder) and match the full FileRef, since
        # the same filename can exist in several SitePages subfolders.
        $pageFileRef = Get-SpoAssetServerRelativePath -SiteUrl $SiteUrl -AssetPath $PageServerRelativeUrl
        $listItem = Get-PnPListItem -List "Site Pages" -Query (
            "<View Scope='RecursiveAll'><Query><Where><Eq><FieldRef Name='FileRef'/><Value Type='Text'>$pageFileRef</Value></Eq></Where></Query></View>"
        ) -ErrorAction Stop | Select-Object -First 1
        if (-not $listItem) {
            throw "Backup could not locate the Site Pages list item for: $PageServerRelativeUrl"
        }
        $hasUniqueRoleAssignments = [bool]$listItem.FieldValues["HasUniqueRoleAssignments"]
        $roleAssignments = if ($hasUniqueRoleAssignments -and (Get-Command Invoke-PnPSPRestMethod -ErrorAction SilentlyContinue)) {
            try {
                Invoke-PnPSPRestMethod -Method Get -Url (
                    "/_api/web/lists/getbytitle('Site Pages')/items($($listItem.Id))/roleassignments?`$expand=Member,RoleDefinitionBindings"
                ) -ErrorAction Stop
            } catch {
                throw "Backup could not capture unique permission role assignments: $($_.Exception.Message)"
            }
        } else {
            $null
        }
        [ordered]@{
            ListItemId               = $listItem.Id
            FieldValues               = $listItem.FieldValues
            HasUniqueRoleAssignments = $hasUniqueRoleAssignments
            RoleAssignments          = $roleAssignments
        } | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $root "list-item-metadata.json") -Encoding UTF8
        Assert-SpoBackupWithinDeadline -Stopwatch $backupClock -Step "list item metadata"

        # 4. Already-published referenced assets the incoming package would also replace.
        $assetManifest = [System.Collections.Generic.List[object]]::new()
        # $null (no assets) must not iterate once as @($null) does.
        $PackageAssets = @($PackageAssets | Where-Object { $null -ne $_ })
        if ($PackageAssets.Count -gt 0) {
            New-Item -ItemType Directory -Path $assetsDir -Force | Out-Null
        }
        foreach ($asset in $PackageAssets) {
            $uploadPath = Get-SpoAssetServerRelativePath -SiteUrl $SiteUrl -AssetPath ([string]$asset.UploadPath)
            $existingAsset = $null
            try {
                $existingAsset = Get-PnPFile -Url $uploadPath -ErrorAction Stop
            } catch {
                if ($_.Exception.Message -notmatch "404|not found|does not exist") {
                    throw "Backup could not determine whether referenced asset exists: $uploadPath -- $($_.Exception.Message)"
                }
            }
            if ($existingAsset) {
                $assetFileName = [System.IO.Path]::GetFileName($uploadPath)
                Get-PnPFile -Url $uploadPath -Path $assetsDir -FileName $assetFileName -AsFile -Force -ErrorAction Stop | Out-Null
                $assetManifest.Add([ordered]@{
                    UploadPath = $uploadPath
                    BackupPath = (Join-Path $assetsDir $assetFileName)
                })
            }
        }

        $manifest = [ordered]@{
            BackupId               = $backupId
            PageServerRelativeUrl  = $PageServerRelativeUrl
            CapturedAtUtc          = (Get-Date -AsUTC).ToString("o")
            Scope                  = "full_recovery"
            PageAsposePath         = Join-Path $root "page.aspx"
            PageComponentsPath     = Join-Path $root "page-components.json"
            ListItemMetadataPath   = Join-Path $root "list-item-metadata.json"
            ReferencedAssets       = @($assetManifest)
        }
        $manifest | ConvertTo-Json -Depth 15 | Set-Content -LiteralPath (Join-Path $root "manifest.json") -Encoding UTF8
        return [pscustomobject]$manifest
    } catch {
        throw "Full-recovery backup of existing page failed; overwrite aborted before any destructive change: $($_.Exception.Message)"
    }
}

function Publish-SpoPage {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$PackagePath,
        [Parameter(Mandatory = $true)][string]$SiteUrl,
        [string]$ClientId,
        [string]$TenantId,
        [switch]$Execute,
        [switch]$RecoverPartialPage,
        [switch]$UseExistingConnection,
        [string]$ConfirmToken,
        [ValidateSet("Backup", "NoBackup")]
        [string]$ExistingPageBackupAction = "Backup",
        [string]$BackupRoot,
        # Overwrite (with backup) an existing page even though the package is CreateOnly.
        [switch]$Force,
        # Asks the operator what to do when a CreateOnly target already exists; receives the
        # page URL and returns "Overwrite" or "Cancel". Null means non-interactive: refuse.
        [scriptblock]$ExistingPagePrompt
    )

    if (-not (Test-Path -LiteralPath $PackagePath -PathType Leaf)) {
        throw "Publication package was not found: $PackagePath"
    }
    if ([string]::IsNullOrWhiteSpace($SiteUrl)) {
        throw "SiteUrl is required."
    }

    $package = Get-Content -LiteralPath $PackagePath -Raw | ConvertFrom-Json
    if ($package.WouldPublish -ne $false -or [string]$package.Mode -ne "DryRun") {
        throw "Only a non-publishing preparation package may be executed."
    }
    $pageMode = [string]$package.Target.PageMode
    if ($pageMode -notin @("CreateOnly", "OverwriteExisting")) {
        throw "Unsupported publication page mode: $pageMode"
    }
    Test-SpoPublicationPackageAssets -Package $package
    # @(...) wraps the whole expression: an if statement unrolls an empty array to $null.
    $packageAssets = @($package.Assets | Where-Object { $null -ne $_ })

    $identity = Get-SpoPageIdentity -PageServerRelativeUrl ([string]$package.Target.PageServerRelativeUrl)
    $actions = [System.Collections.Generic.List[object]]::new()

    foreach ($asset in $packageAssets) {
        $targetPath = [string]$asset.UploadPath
        $targetFolder = $targetPath.Substring(0, $targetPath.LastIndexOf("/"))
        $actions.Add([ordered]@{
            Action       = "UploadAsset"
            LocalPath    = [string]$asset.LocalPath
            TargetFolder = $targetFolder
            TargetPath   = $targetPath
        })
    }

    $willBackupExistingPage = ($pageMode -eq "OverwriteExisting") -and
        ($ExistingPageBackupAction -eq "Backup") -and
        (-not $RecoverPartialPage)
    if ($willBackupExistingPage) {
        $actions.Add([ordered]@{
            Action = "BackupExistingPage"
            Path   = [string]$package.Target.PageServerRelativeUrl
            Scope  = "full_recovery"
        })
    }

    $actions.Add([ordered]@{
        Action     = if ($pageMode -eq "OverwriteExisting") { "OverwritePage" } else { "CreatePage" }
        Name       = $identity.Name
        CreateName = $identity.CreateName
        Path       = [string]$package.Target.PageServerRelativeUrl
        SectionTemplate = if ($package.Target.PSObject.Properties["SectionTemplate"]) {
            [string]$package.Target.SectionTemplate
        } else {
            "OneColumn"
        }
        CommentsEnabled = $false
    })

    $pageFullServerUrl = ([System.Uri]$SiteUrl).AbsolutePath.TrimEnd("/") + "/" + ([string]$package.Target.PageServerRelativeUrl).TrimStart("/")
    foreach ($component in @($package.Components)) {
        if ([string]$component.OutputType -eq "TextWebPart") {
            $actions.Add([ordered]@{
                Action = "AddTextWebPart"
                Html   = ConvertTo-SpoPageHtml -Html ([string]$component.Html) -SiteUrl $SiteUrl -PageServerRelativeUrl $pageFullServerUrl
            })
        } elseif ([string]$component.OutputType -eq "ImageWebPart") {
            $actions.Add([ordered]@{
                Action    = "AddImageWebPart"
                ImageUrl  = Get-SpoImageComponentUrl -SiteUrl $SiteUrl -Component $component
            })
        } elseif ([string]$component.OutputType -eq "SpfxWebPart") {
            $actions.Add([ordered]@{
                Action      = "AddSpfxWebPart"
                ComponentId = [string]$component.ComponentId
            })
        } else {
        }
    }

    $summary = [ordered]@{
        Operation = "publish-spo-page"
        DryRun    = -not $Execute
        Target    = [ordered]@{
            SiteUrl                   = $SiteUrl
            PageServerRelativeUrl     = [string]$package.Target.PageServerRelativeUrl
        }
        Safety    = [ordered]@{
            TenantIo    = if ($Execute) { "enabled" } else { "none" }
            ConfirmToken = "PUBLISH-SPO-PAGE"
            ExistingPageBehavior = if ($pageMode -eq "OverwriteExisting") {
                "ReplaceExistingPageDuringPublication"
            } else {
                "RefuseBeforeUpload"
            }
            ExistingPageBackup = if ($pageMode -ne "OverwriteExisting" -or $RecoverPartialPage) {
                "NotApplicable"
            } elseif ($ExistingPageBackupAction -eq "Backup") {
                "BackupBeforeOverwrite"
            } else {
                "OverwriteWithoutBackup"
            }
            CommentsEnabled = $false
        }
        Actions   = @($actions)
    }

    if (-not $Execute) {
        return [pscustomobject]$summary
    }

    if ($ConfirmToken -ne "PUBLISH-SPO-PAGE") {
        throw "-Execute requires -ConfirmToken PUBLISH-SPO-PAGE."
    }
    if (-not $UseExistingConnection -and
        ([string]::IsNullOrWhiteSpace($ClientId) -or [string]::IsNullOrWhiteSpace($TenantId))) {
        throw "-Execute requires ClientId and TenantId."
    }
    $requiredCommands = @(
        "Connect-PnPOnline",
        "Add-PnPFile",
        "Resolve-PnPFolder",
        "Add-PnPPage",
        "Add-PnPPageSection",
        "Add-PnPPageTextPart",
        "Add-PnPPageImageWebPart",
        "Remove-PnPPage",
        "Set-PnPPage",
        "Get-PnPFile",
        "Get-PnPPage",
        "Get-PnPPageComponent",
        "Get-PnPListItem",
        "Get-PnPWeb",
        "Get-PnPSite",
        "Get-PnPList"
    )
    if (@($package.Components | Where-Object { [string]$_.OutputType -eq "SpfxWebPart" }).Count -gt 0) {
        $requiredCommands += "Add-PnPPageWebPart"
    }
    if ($package.Target.PSObject.Properties["PageHeader"]) {
        $requiredCommands += "Set-PnPListItem"
    }
    foreach ($commandName in $requiredCommands) {
        if (-not (Get-Command $commandName -ErrorAction SilentlyContinue)) {
            throw "PnP.PowerShell command is required: $commandName"
        }
    }

    if (-not $UseExistingConnection) {
        Connect-PnPOnline -Url $SiteUrl -ClientId $ClientId -Tenant $TenantId -Interactive
    }

    try {
        $existingPage = Get-PnPFile -Url ([string]$package.Target.PageServerRelativeUrl) -ErrorAction Stop
    } catch {
        if ($_.Exception.Message -notmatch "404|not found|does not exist") {
            throw "Unable to determine whether the target page exists: $($_.Exception.Message)"
        }
        $existingPage = $null
    }
    if ($existingPage -and $pageMode -eq "CreateOnly" -and -not $RecoverPartialPage) {
        $pageUrl = [string]$package.Target.PageServerRelativeUrl
        if ($Force) {
            $pageMode = "OverwriteExisting"
        } elseif ($ExistingPagePrompt) {
            $answer = [string](& $ExistingPagePrompt $pageUrl)
            if ($answer -ne "Overwrite") {
                throw "Publication cancelled by operator; existing page left unchanged: $pageUrl"
            }
            $pageMode = "OverwriteExisting"
        } else {
            throw "Target page already exists; CreateOnly publication refused before upload: $pageUrl (rerun with -Force to back up and overwrite)"
        }
        $summary.Safety.ExistingPageBehavior = "ReplaceExistingPageDuringPublication"
        $summary.Safety.ExistingPageBackup = if ($ExistingPageBackupAction -eq "Backup") { "BackupBeforeOverwrite" } else { "OverwriteWithoutBackup" }
    }
    if ($RecoverPartialPage -and -not $existingPage) {
        throw "Partial-page recovery requires an existing target page."
    }
    # Images already in this site's libraries (not uploaded by the package) are resolved BEFORE any
    # page is removed or created, so a missing image fails the run without leaving a partial page.
    $existingImageMetadata = @()
    # Full server-relative page URL (web prefix + web-relative target) for resolving ../ image sources.
    $pageFullServerUrl = ([System.Uri]$SiteUrl).AbsolutePath.TrimEnd("/") + "/" + ([string]$package.Target.PageServerRelativeUrl).TrimStart("/")
    $packageUploadPaths = @($packageAssets | ForEach-Object {
        Get-SpoAssetServerRelativePath -SiteUrl $SiteUrl -AssetPath ([string]$_.UploadPath)
    })
    $preWebPrefix = ([System.Uri]$SiteUrl).AbsolutePath.TrimEnd("/")
    $preWebId = $null
    $preSiteId = $null
    $seenExisting = @{}
    # Find the repo's shared ledgers by walking up from this script, then load them once.
    $ledgerRows = @()
    $walk = $PSScriptRoot
    while ($walk -and -not (Test-Path -LiteralPath (Join-Path $walk "inventory\ledgers"))) {
        $walk = Split-Path -Parent $walk
    }
    if ($walk) {
        foreach ($ledgerFile in Get-ChildItem -LiteralPath (Join-Path $walk "inventory\ledgers") -Filter ledger.csv -Recurse -File) {
            $ledgerRows += @(Import-Csv -LiteralPath $ledgerFile.FullName)
        }
    }
    foreach ($component in @($package.Components)) {
        if ([string]$component.OutputType -ne "TextWebPart") { continue }
        foreach ($imgMatch in [regex]::Matches((ConvertTo-SpoPageHtml -Html ([string]$component.Html) -SiteUrl $SiteUrl -PageServerRelativeUrl $pageFullServerUrl), '(?i)<img\b[^>]*\bsrc\s*=\s*["'']([^"'']+)["'']')) {
            $src = $imgMatch.Groups[1].Value
            if ($src -notmatch '^/' -or -not $src.StartsWith("$preWebPrefix/", [StringComparison]::OrdinalIgnoreCase)) { continue }
            $decoded = [System.Uri]::UnescapeDataString($src)
            if ($seenExisting.ContainsKey($decoded) -or $packageUploadPaths -contains $src -or $packageUploadPaths -contains $decoded) { continue }
            $seenExisting[$decoded] = $true
            if (-not $preWebId) {
                $preWebId = [string](Get-PnPWeb -Includes Id -ErrorAction Stop).Id
                $preSiteId = [string](Get-PnPSite -Includes Id -ErrorAction Stop).Id
            }
            $existingItem = $null
            try {
                $existingItem = Get-PnPFile -Url $decoded -AsListItem -ErrorAction Stop
            } catch {
                throw "Image $src is not in the package and was not found in the target site: $($_.Exception.Message)"
            }
            $existingList = Get-PnPProperty -ClientObject $existingItem -Property ParentList -ErrorAction Stop
            # The HTML carries no width/height for these images, so read the pixel size from the local
            # download recorded in the migration ledgers; fetch a temp copy from the site only if none exists.
            $webRelative = $decoded.Substring($preWebPrefix.Length).TrimStart("/")
            $localImage = ""
            if ($ledgerRows) {
                $ledgerHit = $ledgerRows | Where-Object {
                    "$($_.TargetLibrary)/$($_.TargetFolder)/$($_.TargetFilename)" -ieq $webRelative -and
                    $_.LocalPath -and (Test-Path -LiteralPath $_.LocalPath -PathType Leaf)
                } | Select-Object -First 1
                if ($ledgerHit) { $localImage = [string]$ledgerHit.LocalPath }
            }
            if (-not $localImage) {
                $sizeProbeDir = Join-Path ([System.IO.Path]::GetTempPath()) "spo-image-size-probe"
                New-Item -ItemType Directory -Path $sizeProbeDir -Force | Out-Null
                $probeName = [guid]::NewGuid().ToString("N") + [System.IO.Path]::GetExtension($decoded)
                Get-PnPFile -Url $decoded -Path $sizeProbeDir -FileName $probeName -AsFile -Force -ErrorAction Stop
                $localImage = Join-Path $sizeProbeDir $probeName
            }
            $existingImageMetadata += [pscustomobject]@{
                AssetPath         = $src
                UploadPath        = $src
                SourceUrl         = ""
                LocalPath         = $localImage
                ServerRelativeUrl = $src
                WebId             = $preWebId
                SiteId            = $preSiteId
                ListId            = [string]$existingList.Id
                UniqueId          = [string]$existingItem.FieldValues["UniqueId"]
            }
        }
    }
    $backupManifest = $null
    if ($existingPage -and $pageMode -eq "OverwriteExisting" -and -not $RecoverPartialPage) {
        if ($ExistingPageBackupAction -eq "Backup") {
            Write-Verbose "Backing up existing page before overwrite: $($package.Target.PageServerRelativeUrl)"
            $backupManifest = Backup-SpoExistingPage `
                -SiteUrl $SiteUrl `
                -PageServerRelativeUrl ([string]$package.Target.PageServerRelativeUrl) `
                -PageCreateName $identity.CreateName `
                -PackageAssets $packageAssets `
                -BackupRoot $BackupRoot
        }
        Remove-PnPPage -Identity $identity.CreateName -Force -ErrorAction Stop
        $existingPage = $null
    }

    # PnP rejects a bare /SiteAssets/... path on a subsite or /sites/<name> web; every tenant
    # call must use the full server-relative path that includes the web's own prefix.
    # Add-PnPFile cannot create a missing folder chain (DEV returns "Access denied."), so the
    # folder is ensured first via Resolve-PnPFolder, which takes a web-relative path.
    $webPrefix = ([System.Uri]$SiteUrl).AbsolutePath.TrimEnd("/")
    foreach ($asset in $packageAssets) {
        $targetPath = Get-SpoAssetServerRelativePath -SiteUrl $SiteUrl -AssetPath ([string]$asset.UploadPath)
        $targetFolder = $targetPath.Substring(0, $targetPath.LastIndexOf("/"))
        $siteRelativeFolder = $targetFolder.Substring($webPrefix.Length).TrimStart("/")
        Resolve-PnPFolder -SiteRelativePath $siteRelativeFolder -ErrorAction Stop | Out-Null
        Add-PnPFile -Path $asset.LocalPath -Folder $targetFolder `
            -NewFileName ([System.IO.Path]::GetFileName($targetPath)) -ErrorAction Stop | Out-Null
    }
    $webId = [string](Get-PnPWeb -Includes Id -ErrorAction Stop).Id
    $siteId = [string](Get-PnPSite -Includes Id -ErrorAction Stop).Id
    $siteAssetsListId = [string](Get-PnPList -Identity "Site Assets" -Includes Id -ErrorAction Stop).Id
    $inlineImageMetadata = @(
        foreach ($asset in $packageAssets) {
        $assetServerPath = Get-SpoAssetServerRelativePath -SiteUrl $SiteUrl -AssetPath ([string]$asset.UploadPath)
        $item = Get-PnPFile -Url $assetServerPath -AsListItem -ErrorAction Stop
        [pscustomobject]@{
            AssetPath          = if ($asset.PSObject.Properties["AssetPath"]) {
                [string]$asset.AssetPath
            } else {
                [string]$asset.UploadPath
            }
            UploadPath         = [string]$asset.UploadPath
            SourceUrl          = if ($asset.PSObject.Properties["SourceUrl"]) {
                [string]$asset.SourceUrl
            } else {
                ""
            }
            LocalPath          = [string]$asset.LocalPath
            ServerRelativeUrl  = Get-SpoAssetServerRelativePath -SiteUrl $SiteUrl -AssetPath ([string]$asset.UploadPath)
            WebId              = $webId
            SiteId             = $siteId
            ListId             = $siteAssetsListId
            UniqueId           = [string]$item.FieldValues["UniqueId"]
        }
        }
    )

    $inlineImageMetadata = @($inlineImageMetadata) + @($existingImageMetadata)

    if ($RecoverPartialPage) {
        $existingComponents = @(Get-PnPPageComponent -Page $identity.CreateName -ErrorAction Stop)
        if ($existingComponents.Count -ne 1) {
            throw "Partial-page recovery requires exactly one existing component; found $($existingComponents.Count)."
        }
        $page = $identity.CreateName
    } else {
        $pageLayout = if ($package.Target.PSObject.Properties["PageLayout"] -and
            -not [string]::IsNullOrWhiteSpace([string]$package.Target.PageLayout)) {
            [string]$package.Target.PageLayout
        } else {
            "Article"
        }
        Add-PnPPage -Name $identity.CreateName -LayoutType $pageLayout -CommentsEnabled:$false -ErrorAction Stop | Out-Null
        $pageIdentity = "$($identity.CreateName).aspx"
        $page = Get-PnPPage -Identity $pageIdentity -ErrorAction Stop
        $sectionTemplate = if ($package.Target.PSObject.Properties["SectionTemplate"]) {
            [string]$package.Target.SectionTemplate
        } else {
            "OneColumn"
        }
        $sectionTemplates = if ($package.Target.PSObject.Properties["Sections"]) {
            @($package.Target.Sections | ForEach-Object { [string]$_ })
        } else {
            @($sectionTemplate)
        }
        $sectionSettings = if ($package.Target.PSObject.Properties["SectionSettings"]) {
            @($package.Target.SectionSettings)
        } else {
            @()
        }
        $sectionOrder = 1
        foreach ($template in $sectionTemplates) {
            $setting = $sectionSettings | Where-Object { [int]$_.Section -eq $sectionOrder } | Select-Object -First 1
                $emphasisArgs = @{}
                if ($setting -and $setting.PSObject.Properties["Emphasis"]) { $emphasisArgs["ZoneEmphasis"] = [int]$setting.Emphasis }
                if ($setting -and $setting.PSObject.Properties["Collapsible"] -and [bool]$setting.Collapsible -and [bool]$setting.IsExpanded) {
                    # Native collapsible section, expanded by default (docs/analysis/accordion.md).
                    Add-PnPPageSection -Page $page -SectionTemplate $template -Order $sectionOrder -Collapsible -IsExpanded `
                        -DisplayName ([string]$setting.DisplayName) -ErrorAction Stop | Out-Null
                } elseif ($setting -and $setting.PSObject.Properties["Collapsible"] -and [bool]$setting.Collapsible) {
                    Add-PnPPageSection -Page $page -SectionTemplate $template -Order $sectionOrder -Collapsible `
                        -DisplayName ([string]$setting.DisplayName) -ErrorAction Stop | Out-Null
                } elseif ($emphasisArgs.ContainsKey("ZoneEmphasis")) {
                    Add-PnPPageSection -Page $page -SectionTemplate $template -Order $sectionOrder -ZoneEmphasis $emphasisArgs["ZoneEmphasis"] -ErrorAction Stop | Out-Null
                } else {
                    Add-PnPPageSection -Page $page -SectionTemplate $template -Order $sectionOrder -ErrorAction Stop | Out-Null
                }
            $sectionOrder++
        }
    }

    $columnOrders = @{}
    $componentsToAdd = if ($RecoverPartialPage) {
        @($package.Components | Select-Object -Skip 1)
    } else {
        @($package.Components)
    }
    foreach ($component in $componentsToAdd) {
        $sectionTemplate = if ($package.Target.PSObject.Properties["SectionTemplate"]) {
            [string]$package.Target.SectionTemplate
        } else {
            "OneColumn"
        }
        $sectionNumber = if ($component.PSObject.Properties["Section"]) { [int]$component.Section } else { 1 }
        $sourceZoneId = if ($component.PSObject.Properties["SourceZoneId"]) {
            [string]$component.SourceZoneId
        } else {
            ""
        }
        $column = if ($component.PSObject.Properties["Column"]) {
            [int]$component.Column
        } else {
            Get-SpoPageColumn `
                -SectionTemplate $sectionTemplate `
                -SourceZoneId $sourceZoneId
        }
        $orderKey = "$sectionNumber/$column"
        $componentOrder = if ($columnOrders.ContainsKey($orderKey)) { $columnOrders[$orderKey] } else { 1 }
        $columnOrders[$orderKey] = $componentOrder + 1
        if ([string]$component.OutputType -eq "TextWebPart") {
            $columnTemplate = if ($package.Target.PSObject.Properties["Sections"] -and
                @($package.Target.Sections).Count -ge $sectionNumber) {
                [string]@($package.Target.Sections)[$sectionNumber - 1]
            } else {
                $sectionTemplate
            }
            $textHtml = ConvertTo-SpoPageInlineImages `
                -Html (ConvertTo-SpoPageHtml -Html ([string]$component.Html) -SiteUrl $SiteUrl -PageServerRelativeUrl $pageFullServerUrl) `
                -SiteUrl $SiteUrl `
                -ImageMetadata $inlineImageMetadata `
                -BaseWidth (Get-SpoSectionColumnWidth -SectionTemplate $columnTemplate -Column $column)
            Add-PnPPageTextPart -Page $page -Text $textHtml -Section $sectionNumber -Column $column -Order $componentOrder `
                -ErrorAction Stop | Out-Null
        } elseif ([string]$component.OutputType -eq "SpfxWebPart") {
            $available = @(Get-PnPPageComponent -Page $page -ListAvailable -ErrorAction Stop)
            $spfxComponent = $available | Where-Object {
                ([string]$_.Id).Trim('{', '}') -ieq ([string]$component.ComponentId).Trim('{', '}')
            } | Select-Object -First 1
            if (-not $spfxComponent) {
                throw "SPFx component $($component.ComponentId) is not available on the target site. Deploy the .sppkg to the App Catalog (and install it on the site) before publishing."
            }
            Add-PnPPageWebPart -Page $page -Component $spfxComponent `
                -WebPartProperties (ConvertTo-SpoWebPartPropertyTable -InputObject $component.Properties) `
                -Section $sectionNumber -Column $column -Order $componentOrder -ErrorAction Stop | Out-Null
        } else {
            $imageUrl = Get-SpoImageComponentUrl -SiteUrl $SiteUrl -Component $component
            if ($component.PSObject.Properties["ImageWidth"] -and [int]$component.ImageWidth -gt 0) {
                # Width alone lets SPO choose a height and stretch the image; send the matching height.
                $imageWidth = [int]$component.ImageWidth
                $imageHeight = Get-SpoImageProportionalHeight -ImageUrl $imageUrl -Width $imageWidth
                if ($imageHeight -gt 0) {
                    Add-PnPPageImageWebPart -Page $page -ImageUrl $imageUrl -Section $sectionNumber -Column $column -Order $componentOrder `
                        -ImageWidth $imageWidth -ImageHeight $imageHeight -ErrorAction Stop | Out-Null
                } else {
                    Write-Warning "Image size unreadable for $imageUrl; publishing without a fixed size to avoid distortion."
                    Add-PnPPageImageWebPart -Page $page -ImageUrl $imageUrl -Section $sectionNumber -Column $column -Order $componentOrder `
                        -ErrorAction Stop | Out-Null
                }
            } else {
                # With no size, PnP stores a 150x150 box, which squashes any non-square file; send the file's own size.
                $natural = Get-SpoImageNaturalSize -ImageUrl $imageUrl
                if ($natural) {
                    Add-PnPPageImageWebPart -Page $page -ImageUrl $imageUrl -Section $sectionNumber -Column $column -Order $componentOrder `
                        -ImageWidth $natural.Width -ImageHeight $natural.Height -ErrorAction Stop | Out-Null
                } else {
                    Write-Warning "Image size unreadable for $imageUrl; publishing without a fixed size (SPO defaults to 150x150 and may distort it)."
                    Add-PnPPageImageWebPart -Page $page -ImageUrl $imageUrl -Section $sectionNumber -Column $column -Order $componentOrder `
                        -ErrorAction Stop | Out-Null
                }
            }
        }
    }
    $pageTitle = if ($package.Target.PSObject.Properties["PageTitle"]) { [string]$package.Target.PageTitle } else { "" }
    $pageHeader = if ($package.Target.PSObject.Properties["PageHeader"]) { $package.Target.PageHeader } else { $null }
    $headerArgs = @{}
    if ($pageHeader) {
        # Title-area Banner web part (Administration playbook): Plain layout, publish date shown.
        $headerArgs["HeaderType"] = "PageTitleWebPart"
        $headerArgs["HeaderLayoutType"] = [string]$pageHeader.LayoutType
        $headerArgs["ShowPublishDate"] = [bool]$pageHeader.ShowPublishDate
    }
    if (-not [string]::IsNullOrWhiteSpace($pageTitle)) {
        Set-PnPPage -Identity $identity.CreateName -Title $pageTitle -CommentsEnabled:$false @headerArgs -Publish -ErrorAction Stop | Out-Null
    } else {
        Set-PnPPage -Identity $identity.CreateName -CommentsEnabled:$false @headerArgs -Publish -ErrorAction Stop | Out-Null
    }
    if ($pageHeader) {
        # PnP cannot set the title zone colour: convert the saved canvas to the Banner web part model.
        # SystemUpdate keeps the page published (no new version, no draft).
        $pageFileRef = Get-SpoAssetServerRelativePath -SiteUrl $SiteUrl -AssetPath ([string]$package.Target.PageServerRelativeUrl)
        $pageItem = Get-PnPListItem -List "Site Pages" -Query (
            "<View Scope='RecursiveAll'><Query><Where><Eq><FieldRef Name='FileRef'/><Value Type='Text'>$pageFileRef</Value></Eq></Where></Query></View>"
        ) -ErrorAction Stop | Select-Object -First 1
        if (-not $pageItem) {
            throw "Title banner step could not locate the Site Pages item for: $($package.Target.PageServerRelativeUrl)"
        }
        $bannerTitle = if (-not [string]::IsNullOrWhiteSpace([string]$pageHeader.Title)) { [string]$pageHeader.Title } else { $pageTitle }
        $converted = ConvertTo-SpoCanvasWithTitleBanner `
            -CanvasContent ([string]$pageItem.FieldValues["CanvasContent1"]) `
            -LayoutWebpartsContent ([string]$pageItem.FieldValues["LayoutWebpartsContent"]) `
            -Title $bannerTitle -ZoneThemeIndex ([int]$pageHeader.ZoneThemeIndex) `
            -LayoutType ([string]$pageHeader.LayoutType) -TextAlignment ([string]$pageHeader.TextAlignment) `
            -ShowPublishDate ([bool]$pageHeader.ShowPublishDate)
        Set-PnPListItem -List "Site Pages" -Identity $pageItem.Id -UpdateType SystemUpdate -Values @{
            CanvasContent1        = $converted.CanvasContent
            LayoutWebpartsContent = $converted.LayoutWebpartsContent
        } -ErrorAction Stop | Out-Null
    }

    $verifiedAssets = foreach ($asset in $packageAssets) {
        $verified = Get-PnPFile `
            -Url (Get-SpoAssetServerRelativePath -SiteUrl $SiteUrl -AssetPath ([string]$asset.UploadPath)) `
            -ErrorAction SilentlyContinue
        if (-not $verified) {
            throw "Published asset could not be verified: $($asset.UploadPath)"
        }
        [string]$asset.UploadPath
    }
    $verifiedPage = Get-PnPPage -Identity $identity.CreateName -ErrorAction SilentlyContinue
    if (-not $verifiedPage) {
        throw "Published page could not be verified: $($package.Target.PageServerRelativeUrl)"
    }

    $summary.DryRun = $false
    $summary.Safety.TenantIo = "completed"
    $summary.Validation = [ordered]@{
        Page  = [string]$package.Target.PageServerRelativeUrl
        Assets = @($verifiedAssets)
        Backup = $backupManifest
    }
    return [pscustomobject]$summary
}

if (-not $LibraryMode -and $MyInvocation.InvocationName -ne ".") {
    $spoConfig = Read-SpoConfiguration -Path $ConfigPath -Require @("SiteUrl", "ClientId", "TenantId")
    if ([string]::IsNullOrWhiteSpace($PackagePath)) {
        throw "PackagePath is required."
    }
    $existingPagePrompt = $null
    if (-not $Force -and -not [Console]::IsInputRedirected -and [Environment]::UserInteractive) {
        $existingPagePrompt = {
            param($PageUrl)
            $reply = Read-Host "Target page already exists: $PageUrl. [O]verwrite (backup first) or [C]ancel"
            if ($reply -match '^(o|overwrite)$') { "Overwrite" } else { "Cancel" }
        }
    }
    Publish-SpoPage `
        -PackagePath $PackagePath `
        -SiteUrl $spoConfig.SiteUrl `
        -ClientId $spoConfig.ClientId `
        -TenantId $spoConfig.TenantId `
        -Execute:$Execute `
        -RecoverPartialPage:$RecoverPartialPage `
        -UseExistingConnection:$UseExistingConnection `
        -ConfirmToken $ConfirmToken `
        -ExistingPageBackupAction $ExistingPageBackupAction `
        -Force:$Force `
        -ExistingPagePrompt $existingPagePrompt
}
