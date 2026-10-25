<#
.SYNOPSIS
Creates a single-page Wave 1 dry-run plan for a Content Editor web part.

.DESCRIPTION
Reads one source page record and an extracted web-part content export, then
creates a local modern-page plan without contacting SharePoint or publishing.
Wave 1 accepts exactly one or more Content Editor payloads for the page and
maps each payload to an SPO text web part.

.KEY INPUT DEPENDENCIES
- Source page JSON with SiteName, ServerRelativeUrl, Url, and Title
- Web-part content JSON with PageUrl, WebPartId, WebPartTitle, optional
  WebPartCategory, and Content
- Raw SP2016 export directory containing one exportwp.aspx XML file per web part
- Optional image manifest produced by extract-page-images.ps1
- Optional -LibraryPathMapPath (inventory/library-path-map.csv) with -SourceHost: rewrites
  SP2016 links to their planned SPO location (assume-migrated link policy)
- Optional -LeadingImageWebPartIds: web parts whose leading banner image becomes an
  Image web part reusing the already-migrated image (ExistingImageUrl, no upload)
- -ConfigPath: config-spo-<env>.psd1; Connection.Environment is the target environment

.OUTPUTS
- Dry-run migration plan JSON, including per-component CleanupFindings and a
  ContentCleanup summary for the human spacing and formatting review
- LinkRewrites (Rewritten/Unmapped) for human review of every SP2016 link
- A Bootstrap accordion becomes one-column sections: an "On this page" quick-links
  section, then one native collapsible section per panel (display name = panel heading,
  collapsed by default; see docs/analysis/accordion.md). plan.Sections, plan.SectionSettings,
  plan.PageLayout = "Home" and component Section/Column are emitted only when an accordion
  is present. A leading banner image keeps its source width as ImageWidth.
- Optional -PageTitle (display title from the SP2016 <title>) adds a first TextWebPart
  (Role "PageHeader"): breadcrumb Home > -BreadcrumbSection (link via -BreadcrumbSectionUrl,
  else the containing SitePages/<SiteName>/ folder; default label SiteName; omitted for root /Pages/ pages) > title, then an <h2> title.
  Page names map en/em dashes to "-" as SPO does. Body baseline is 16px.

.FUNCTION INDEX
Remove-SpPageLegacyFontFormatting, Set-SpPageWave1BodyFontBaseline,
Remove-SpPageListItemTrailingBreaks, Remove-SpPageParagraphTrailingBreaks,
Remove-SpPageRedundantBlankLines, Set-SpPageTableCellVerticalAlignment,
Remove-SpPageInlineLayoutStyles, Set-SpPageBcDesignTokenStyles,
ConvertTo-SpPageNormalizedHtml, Get-SpPageCleanupFindings,
Get-SpPageCleanupSummary,
Replace-SpPageImageSources, Get-SpPageDefaultSourceZone,
Test-SpPageUrlMatch, Get-SpPageName, Get-SpPageHeadingAnchor,-SpPagePlainText, Get-SpPageDivEndIndex, ConvertTo-SpPageMappedLinks,-SpPageBootstrapAccordion, Get-SpPageAccordionSurroundings,-SpPageLeadingImage,
New-SpPageWave1DryRun.
#>

[CmdletBinding()]
param(
    [string]$SourcePagePath,
    [string]$WebpartContentPath,
    [string]$ImageManifestPath,
    [string]$RawExportDirectory,
    [string]$ConfigPath,
    [string]$OutputPath,
    [string]$LibraryPathMapPath,
    [string]$SourceHost,
    [string[]]$LeadingImageWebPartIds = @(),
    [ValidateSet("Native", "Spfx")][string]$AccordionOutput = "Native",
    [ValidateSet(1, 2)][int]$AccordionColumns = 2,
    [string]$HeaderText,
    [string[]]$HeaderSubtext,
    [string]$HeaderLogoUrl,
    [ValidateSet("None", "Administration")][string]$PageHeaderStyle = "None",
    [int]$PageHeaderZoneThemeIndex = 3,
    [string]$PageTitle,
    [string]$BreadcrumbSection,
    [string]$BreadcrumbSectionUrl
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

function Remove-SpPageLegacyFontFormatting {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][AllowEmptyString()][string]$Html)

    $withoutFontProperties = [regex]::Replace(
        $Html,
        '(?i)(font-family|font-size|font)\s*:\s*[^;"]*(?:;|(?=\s*["'']))',
        ""
    )
    $withoutFaceSize = [regex]::Replace(
        $withoutFontProperties,
        '(?i)\s+(face|size)\s*=\s*["''][^"'']*["'']',
        ""
    )
    # Legacy <font color> tags override the BC design-token text and link colours; unwrap them.
    return [regex]::Replace($withoutFaceSize, '(?i)</?font\b[^>]*>', '')
}

function Set-SpPageWave1BodyFontBaseline {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][AllowEmptyString()][string]$Html)

    if ([string]::IsNullOrWhiteSpace($Html)) {
        return $Html
    }
    if ($Html -match '(?is)^\s*<(?<tag>[a-z][a-z0-9]*)\b(?<attributes>[^>]*)>(?<body>.*)</\k<tag>\s*>\s*$') {
        $tag = $Matches.tag
        $attributes = $Matches.attributes
        $body = $Matches.body
        $openingTag = "<$tag$attributes>"
        if ($openingTag -notmatch '(?i)\bstyle\s*=') {
            $openingTag = $openingTag -replace '(?i)>$', ' style="font-size:16px;">'
        } elseif ($openingTag -notmatch '(?i)font-size\s*:') {
            $openingTag = $openingTag -replace '(?i)(style\s*=\s*["''])([^"'']*)', '$1font-size:16px; $2'
        }
        return $openingTag + $body + "</$tag>"
    }
    if ($Html -match '(?is)<div\b[^>]*data-sp-migration-body\s*=\s*["'']true["'']') {
        return $Html
    }
    return '<div data-sp-migration-body="true" style="font-size:16px;">' +
        $Html +
        '</div>'
}

function Remove-SpPageListItemTrailingBreaks {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][AllowEmptyString()][string]$Html)

    $withoutTrailingBreaks = [regex]::Replace(
        $Html,
        '(?is)<br\b[^>]*>[\s\u200B\uFEFF]*(?:&nbsp;[\s\u200B\uFEFF]*)*</li>',
        '</li>'
    )
    return [regex]::Replace($withoutTrailingBreaks, '(?is)</li>\s+<li>', '</li><li>')
}

function Remove-SpPageParagraphTrailingBreaks {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][AllowEmptyString()][string]$Html)

    $withoutLooseSpacer = [regex]::Replace(
        $Html,
        '(?is)<br\b[^>]*>[\s\u200B\uFEFF]*(?:(?:&nbsp;)|(?:&#160;)|<font\b[^>]*>[\s\u200B\uFEFF]*</font>)*[\s\u200B\uFEFF]*<p>[\s\u200B\uFEFF]*(?:&nbsp;|&#160;)[\s\u200B\uFEFF]*</p>',
        ''
    )
    return [regex]::Replace(
        $withoutLooseSpacer,
        '(?is)<br\b[^>]*>[\s\u200B\uFEFF]*(?:(?:&nbsp;)|(?:&#160;))[\s\u200B\uFEFF]*</p>',
        '</p>'
    )
}

function Remove-SpPageRedundantBlankLines {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][AllowEmptyString()][string]$Html)

    $withoutZeroWidth = $Html -replace '[\u200B\uFEFF]', ''
    $withBlockSpacing = [regex]::Replace(
        $withoutZeroWidth,
        '(?is)(?:<br\b[^>]*>[\s]*(?:&nbsp;[\s]*)*)+<(?<tag>div|p|ul|ol|table|h[1-6])(?<attrs>[^>]*)>',
        {
            param($match)
            $tag = $match.Groups["tag"].Value
            $attrs = $match.Groups["attrs"].Value
            $styleMatch = [regex]::Match(
                $attrs,
                '(?i)style\s*=\s*["''](?<value>[^"'']*)["'']'
            )
            if ($styleMatch.Success) {
                $styleValue = $styleMatch.Groups["value"].Value.TrimEnd()
                if (-not $styleValue.EndsWith(";")) {
                    $styleValue += ";"
                }
                $styleValue += " margin-top:18px;"
                $attrs = $attrs.Remove(
                    $styleMatch.Groups["value"].Index,
                    $styleMatch.Groups["value"].Length
                ).Insert(
                    $styleMatch.Groups["value"].Index,
                    $styleValue
                )
            } else {
                $attrs += ' style="margin-top:18px;"'
            }
            return "<$tag$attrs>"
        }
    )
    $withoutTrailingContainerBreak = [regex]::Replace(
        $withBlockSpacing,
        '(?is)<br\b[^>]*>[\s]*(?=</div>)',
        ''
    )
    $withoutEmptyBreakContainers = [regex]::Replace(
        $withoutTrailingContainerBreak,
        '(?is)<div\b[^>]*>[\s\u200B\uFEFF]*(?:<br\b[^>]*>[\s\u200B\uFEFF]*(?:&nbsp;[\s\u200B\uFEFF]*)*)+</div>',
        ''
    )
    # Two breaks between text are a paragraph gap in the source, so keep them; only longer runs are collapsed.
    $singleBreak = [regex]::Replace(
        $withoutEmptyBreakContainers,
        '(?is)(?:<br\b[^>]*>[\s\u200B\uFEFF]*(?:&nbsp;[\s\u200B\uFEFF]*)*){3,}',
        '<br/><br/>'
    )
    $withoutLeadingBreaks = [regex]::Replace(
        $singleBreak,
        '(?is)^[\s\u200B\uFEFF]*(?:<br\b[^>]*>[\s\u200B\uFEFF]*(?:&nbsp;[\s\u200B\uFEFF]*)*)+',
        ''
    )
    return [regex]::Replace(
        $withoutLeadingBreaks,
        '(?is)(?:<br\b[^>]*>[\s\u200B\uFEFF]*(?:&nbsp;[\s\u200B\uFEFF]*)*)+[\s\u200B\uFEFF]*$',
        ''
    )
}

function Set-SpPageTableCellVerticalAlignment {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][AllowEmptyString()][string]$Html)

    return [regex]::Replace(
        $Html,
        '(?is)<(?<tag>td|th)\b(?<attributes>[^>]*)>',
        {
            param($match)
            $attributes = $match.Groups["attributes"].Value
            if ($attributes -match '(?i)\bvalign\s*=\s*["'']?\s*(?:top|middle|bottom|baseline)\b' -or
                $attributes -match '(?i)\bvertical-align\s*:') {
                return $match.Value
            }
            $styleMatch = [regex]::Match(
                $attributes,
                '(?i)\bstyle\s*=\s*["''](?<value>[^"'']*)["'']'
            )
            if ($styleMatch.Success) {
                $styleValue = $styleMatch.Groups["value"].Value.TrimEnd()
                if (-not $styleValue.EndsWith(";")) {
                    $styleValue += ";"
                }
                $styleValue += " vertical-align: top;"
                $attributes = $attributes.Remove(
                    $styleMatch.Groups["value"].Index,
                    $styleMatch.Groups["value"].Length
                ).Insert(
                    $styleMatch.Groups["value"].Index,
                    $styleValue
                )
            } else {
                $attributes += ' style="vertical-align: top;"'
            }
            return "<$($match.Groups["tag"].Value)$attributes>"
        }
    )
}

# Example: <p style="line-height:1.6; color:#333; margin-top:18px;">Text</p>
# Result:  <p style="color:#333;">Text</p>
function Remove-SpPageInlineLayoutStyles {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][AllowEmptyString()][string]$Html)

    return [regex]::Replace(
        $Html,
        '(?is)(?<spacing>\s+)\bstyle\s*=\s*(?<quote>["''])(?<value>.*?)\k<quote>',
        {
            param($match)

            $hadTrailingSemicolon = $match.Groups["value"].Value.TrimEnd().EndsWith(";")
            $remaining = $match.Groups["value"].Value
            do {
                $previous = $remaining
                $remaining = [regex]::Replace(
                    $remaining,
                    '(?i)(?:^|;)\s*(?:line-height|margin-top)\s*:[^;]*(?:;|$)',
                    ""
                )
            } while ($remaining -ne $previous)
            $remaining = $remaining.Trim()
            $remaining = $remaining.Trim()

            if ([string]::IsNullOrWhiteSpace($remaining) -or $remaining -match '^(?:;|\s)*$') {
                return ""
            }
            if ($hadTrailingSemicolon -and -not $remaining.EndsWith(";")) {
                $remaining += ";"
            }
            return $match.Groups["spacing"].Value + 'style="' + $remaining + '"'
        }
    )
}

# Applies Modernernment design tokens (design-system-design-system colors_and_type.css) as
# inline styles, since a modern text web part cannot load external CSS or fonts.
# line-height is omitted on purpose: Remove-SpPageInlineLayoutStyles strips it.
# Example: <h2>T</h2><a href="/x">l</a>
# Result:  <div data-sp-bc-tokens="true" style="font-family:...;"><h2>T</h2><a href="/x" style="color:#255A90; text-decoration:underline;">l</a></div>
function Set-SpPageBcDesignTokenStyles {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][AllowEmptyString()][string]$Html)

    if ([string]::IsNullOrWhiteSpace($Html) -or $Html -match 'data-sp-bc-tokens\s*=') {
        return $Html
    }
    # Headings keep SPO default sizes: inline BC heading sizes rendered oversized (first DEV publish).
    $styled = [regex]::Replace(
        $Html,
        '(?is)<a(?<attrs>\s[^>]*)>',
        {
            param($m)
            $attrs = $m.Groups["attrs"].Value
            if ($attrs -match '(?is)\bstyle\s*=\s*["''][^"'']*\bcolor\s*:') {
                return $m.Value
            }
            if ($attrs -match '(?is)\bstyle\s*=\s*(["''])') {
                $attrs = [regex]::Replace($attrs, '(?is)(\bstyle\s*=\s*["''])', '${1}color:#255A90; text-decoration:underline; ', 1)
            } else {
                $attrs += ' style="color:#255A90; text-decoration:underline;"'
            }
            return "<a$attrs>"
        }
    )
    # Bootstrap panel classes have no CSS in SPO, so the legacy boxed panels lose their borders and grey header.
    $panelStyles = @{
        'panel panel-default' = 'border:1px solid #DDDDDD;border-radius:4px;margin-bottom:10px;'
        'panel-heading'       = 'background-color:#F5F5F5;border-bottom:1px solid #DDDDDD;padding:10px 15px;'
        'panel-body'          = 'padding:15px;'
    }
    foreach ($panelClass in $panelStyles.Keys) {
        $styled = [regex]::Replace(
            $styled,
            '(?is)<div\s+class="' + [regex]::Escape($panelClass) + '"(?<rest>[^>]*)>',
            {
                param($m)
                $rest = $m.Groups["rest"].Value
                $own = $panelStyles[$panelClass]
                if ($rest -match '(?is)\sstyle\s*=\s*"(?<s>[^"]*)"') {
                    $rest = [regex]::Replace($rest, '(?is)\sstyle\s*=\s*"[^"]*"', '')
                    $own += ' ' + $Matches['s']
                }
                '<div class="' + $panelClass + '" style="' + $own + '"' + $rest + '>'
            }.GetNewClosure()
        )
    }
    # SPO draws a default black table border; the source layout tables have none, so set it explicitly.
    $styled = [regex]::Replace(
        $styled,
        '(?is)<(?<tag>table|td|th)(?<attrs>(\s[^>]*)?)>',
        {
            param($m)
            $attrs = $m.Groups["attrs"].Value
            if ($attrs -match '(?is)\bborder\s*=\s*["'']?[1-9]|border\s*:') {
                return $m.Value
            }
            $own = 'border:none;'
            if ($attrs -match '(?is)\sstyle\s*=\s*"(?<s>[^"]*)"') {
                $attrs = [regex]::Replace($attrs, '(?is)\sstyle\s*=\s*"[^"]*"', '')
                $own += ' ' + $Matches['s']
            }
            # SPO ignores a style-only border:none on the table element, so also set the legacy attribute.
            if ($m.Groups["tag"].Value -ieq 'table' -and $attrs -notmatch '(?is)\sborder\s*=') { $attrs += ' border="0"' }
            '<' + $m.Groups["tag"].Value + $attrs + ' style="' + $own + '">'
        }
    )
    return '<div data-sp-bc-tokens="true" style="font-family:''BC Sans'', ''Noto Sans'', sans-serif;color:#2D2D2D;font-size:16px;">' +
        $styled + '</div>'
}

function ConvertTo-SpPageNormalizedHtml {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][AllowEmptyString()][string]$Html)

    $normalized = $Html -replace "`r`n?", "`n"
    $normalized = [regex]::Replace($normalized, "(?s)<!--.*?-->", "")
    $normalized = [regex]::Replace($normalized, ">\s+<", "> <")
    $normalized = Remove-SpPageListItemTrailingBreaks -Html $normalized
    $normalized = Remove-SpPageParagraphTrailingBreaks -Html $normalized
    $normalized = Remove-SpPageRedundantBlankLines -Html $normalized
    $normalized = Set-SpPageTableCellVerticalAlignment -Html $normalized
    $normalized = Remove-SpPageInlineLayoutStyles -Html $normalized
    $normalized = [regex]::Replace($normalized, '(?is)<br\s*/>', '<br/>')
    $withoutLegacyFormatting = (Remove-SpPageLegacyFontFormatting -Html $normalized).Trim()
    return $withoutLegacyFormatting
}

function Get-SpPageCleanupFindings {
    # Reports dirty SP2016 Content Editor markup left after normalization.
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][AllowEmptyString()][string]$Html)

    $checks = [ordered]@{
        LegacyFontTag = '(?i)<font\b[^>]*>'
        OfficeMarkup = '(?i)<o:p\b[^>]*>|\bclass\s*=\s*"[^"]*\bMso\w+'
        SharePointRteClass = '(?i)\bclass\s*=\s*"[^"]*\bms-rte[\w-]*'
        EmptyInlineElement = '(?i)<(span|font|strong|em|b|i)\b[^>]*>\s*</\1>'
        StackedBlankParagraphs = '(?i)(?:<p\b[^>]*>\s*(?:&nbsp;|&#160;|\u00a0|<br\s*/?>|\s)*</p>\s*){2,}'
        NbspSpacingRun = '(?i)(?:&nbsp;|&#160;|\u00a0){3,}'
    }
    foreach ($code in $checks.Keys) {
        $hits = [regex]::Matches($Html, $checks[$code])
        if ($hits.Count -gt 0) {
            $example = $hits[0].Value
            if ($example.Length -gt 80) { $example = $example.Substring(0, 80) }
            [pscustomobject]@{ Code = $code; Count = $hits.Count; Example = $example }
        }
    }
}

function Get-SpPageCleanupSummary {
    # Totals component cleanup findings; spacing review is always human.
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][AllowEmptyCollection()][object[]]$Components)

    $count = 0
    foreach ($component in $Components) {
        $count += @($component.CleanupFindings).Count
    }
    return [pscustomobject][ordered]@{
        Clean = ($count -eq 0)
        FindingCount = $count
        RequiresHumanSpacingReview = $true
        Guidance = "Compare spacing with the SP2016 page; clear any remaining formatting by hand."
    }
}

function Replace-SpPageImageSources {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$Html,
        [Parameter(Mandatory = $true)][object[]]$Images
    )

    $result = $Html
    foreach ($image in $Images) {
        $destination = [string]$image.DestinationRelativePath
        $sourceUrl = [string]$image.SourceUrl
        $sourcePath = ([Uri]$image.SourceUrl).AbsolutePath
        $result = $result.Replace($sourceUrl, $destination)
        $result = $result.Replace($sourcePath, $destination)
        $result = $result.Replace(
            [System.Net.WebUtility]::HtmlEncode($sourceUrl),
            $destination
        )
        $result = $result.Replace(
            [System.Net.WebUtility]::HtmlEncode($sourcePath),
            $destination
        )
    }
    return $result
}

function Get-SpPageDefaultSourceZone {
    [CmdletBinding()]
    param([AllowEmptyString()][string]$Layout)

    switch ($Layout) {
        "Two-Third-Right" { return "RightZone" }
        "Two-Third-Left" { return "LeftZone" }
        "One-Third-Right" { return "LeftZone" }
        default { return "" }
    }
}

function Test-SpPageUrlMatch {
    [CmdletBinding()]
    param(
        [AllowEmptyString()][string]$WebPartPageUrl,
        [AllowEmptyString()][string]$PageUrl,
        [Parameter(Mandatory = $true)][string]$ServerRelativeUrl
    )

    if ([string]::IsNullOrWhiteSpace($WebPartPageUrl)) {
        return $false
    }
    if ($WebPartPageUrl -eq $PageUrl -or $WebPartPageUrl -eq $ServerRelativeUrl) {
        return $true
    }

    $webPartUri = $null
    if ([Uri]::TryCreate($WebPartPageUrl, [UriKind]::Absolute, [ref]$webPartUri)) {
        return $webPartUri.AbsolutePath -eq $ServerRelativeUrl
    }
    return $false
}

function Get-SpPageName {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)]$Page)

    $name = if (-not [string]::IsNullOrWhiteSpace([string]$Page.Title)) {
        [string]$Page.Title
    } else {
        [System.IO.Path]::GetFileNameWithoutExtension((Split-Path -Path ([string]$Page.ServerRelativeUrl) -Leaf))
    }
    # SPO saves en/em dashes in a page file name as "-" (Bill-C-78 published as Bill-C-78---...).
    return $name -replace "[\u2013\u2014]", "-"
}

# Converts heading text to the anchor SPO generates for H1-H3 headings
# (lowercase, punctuation dropped, spaces to hyphens). Confirm on the published page.
function Get-SpPageHeadingAnchor {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][AllowEmptyString()][string]$Heading)

    $text = [System.Net.WebUtility]::HtmlDecode($Heading) -replace "[\u200B\uFEFF]", ""
    $text = $text.Replace([char]0x00A0, " ").ToLowerInvariant()
    $text = $text -replace "[^\p{L}\p{Nd}\s-]", ""
    $text = ($text.Trim() -replace "\s+", "-") -replace "-+", "-"
    return $text.Trim("-")
}

# Returns heading text without tags, entities, non-breaking or zero-width spaces.
function Get-SpPagePlainText {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][AllowEmptyString()][string]$Html)

    $text = [System.Net.WebUtility]::HtmlDecode(($Html -replace "<[^>]+>", " "))
    $text = ($text -replace "[\u200B\uFEFF]", "").Replace([char]0x00A0, " ")
    return ($text -replace "\s+", " ").Trim()
}

# Returns the index just after the closing tag of the <div> that starts at StartIndex,
# counting nested divs; -1 when the markup is unbalanced.
function Get-SpPageDivEndIndex {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$Html,
        [Parameter(Mandatory = $true)][int]$StartIndex
    )

    $depth = 0
    foreach ($match in [regex]::Matches($Html.Substring($StartIndex), "(?i)<div\b[^>]*>|</div\s*>")) {
        if ($match.Value.StartsWith("</")) { $depth-- } else { $depth++ }
        if ($depth -eq 0) { return $StartIndex + $match.Index + $match.Length }
    }
    return -1
}

# Rewrites href/src values that point at SP2016 content to their planned SPO location from
# inventory/library-path-map.csv (assume-migrated link policy). Longest prefix wins.
# Pages under /SitePages/ keep .aspx; library .aspx/.htm files become .html.
# Returns Html plus Links (Rewritten/Unmapped); external, mailto and #anchor links are untouched.
function ConvertTo-SpPageMappedLinks {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$Html,
        [Parameter(Mandatory = $true)][object[]]$PathMap,
        [AllowEmptyString()][string]$PageUrl,
        [Parameter(Mandatory = $true)][string]$SourceHost,
        [string]$TargetSitePath,
        [string]$RelativeBase
    )

    $sourceHostName = ($SourceHost -replace "^[a-z]+://", "").Trim("/")
    $rows = @($PathMap | Sort-Object { ([string]$_.source_prefix).Length } -Descending)
    $links = [System.Collections.Generic.List[object]]::new()
    $evaluator = {
        param($match)
        $raw = $match.Groups["value"].Value
        $value = [System.Net.WebUtility]::HtmlDecode($raw).Trim()
        if ($value -eq "" -or $value -match "^(#|mailto:|tel:|javascript:|data:)" -or $value -match "^/sites/") {
            return $match.Value
        }
        $uri = $null
        if ([Uri]::TryCreate($value, [UriKind]::Absolute, [ref]$uri) -and $uri.Scheme -in @("http", "https")) {
            if ($uri.Host -ne $sourceHostName) { return $match.Value }
            $value = $uri.PathAndQuery + $uri.Fragment
        } elseif (-not $value.StartsWith("/")) {
            if ([string]::IsNullOrWhiteSpace($PageUrl)) { return $match.Value }
            $resolved = $null
            if ([Uri]::TryCreate([Uri]$PageUrl, $value, [ref]$resolved)) {
                $value = $resolved.PathAndQuery + $resolved.Fragment
            } else {
                $links.Add([pscustomobject]@{ Source = $raw; Target = $raw; Status = "Unmapped"; MapStatus = "MalformedUri" })
                return $match.Value
            }
        }
        $suffixIndex = $value.IndexOfAny([char[]]@("?", "#"))
        $path = if ($suffixIndex -ge 0) { $value.Substring(0, $suffixIndex) } else { $value }
        $suffix = if ($suffixIndex -ge 0) { $value.Substring($suffixIndex) } else { "" }
        $decoded = [Uri]::UnescapeDataString($path)
        $row = $rows | Where-Object {
            $decoded.StartsWith([string]$_.source_prefix, [System.StringComparison]::OrdinalIgnoreCase)
        } | Select-Object -First 1
        if (-not $row) {
            $links.Add([pscustomobject]@{ Source = $raw; Target = $raw; Status = "Unmapped"; MapStatus = "" })
            return $match.Value
        }
        $target = [string]$row.dest_prefix + $decoded.Substring(([string]$row.source_prefix).Length)
        if (-not [string]::IsNullOrWhiteSpace($TargetSitePath)) {
            $target = $target -replace "^/sites/[^/]+", $TargetSitePath.TrimEnd("/")
        }
        if ($target -notmatch "(?i)/SitePages/" -and $target -match "(?i)\.(aspx|htm)$") {
            $target = $target -replace "(?i)\.(aspx|htm)$", ".html"
        }
        # Page-relative form keeps the same package valid on DEV, TEST and PROD (no site prefix).
        $sitePrefix = $TargetSitePath.TrimEnd("/") + "/"
        if (-not [string]::IsNullOrWhiteSpace($RelativeBase) -and
            $target.StartsWith($sitePrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
            $target = $RelativeBase + $target.Substring($sitePrefix.Length)
        }
        $encoded = (($target -split "/") | ForEach-Object { if ($_ -eq "..") { $_ } else { [Uri]::EscapeDataString($_) } }) -join "/"
        $encoded += [System.Net.WebUtility]::HtmlEncode($suffix)
        $links.Add([pscustomobject]@{
            Source = $raw; Target = $encoded; Status = "Rewritten"; MapStatus = [string]$row.status
        })
        return $match.Groups["prefix"].Value + $encoded + $match.Groups["quote"].Value
    }
    $result = [regex]::Replace(
        $Html,
        '(?i)(?<prefix>\b(?:href|src)\s*=\s*(?<quote>["'']))(?<value>[^"'']*)\k<quote>',
        $evaluator
    )
    return [pscustomobject]@{ Html = $result; Links = @($links) }
}

# Splits a Bootstrap accordion (panel-group/panel-collapse) into one item per panel with
# its plain heading text and inner panel-body HTML. Returns nothing for other markup.
function Split-SpPageBootstrapAccordion {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][AllowEmptyString()][string]$Html)

    # Always-open Bootstrap panel boxes have no data-toggle; only a real accordion does.
    if ($Html -notmatch "(?i)\bpanel-group\b" -or $Html -notmatch '(?i)\b(?:panel-)?collapse\b' -or $Html -notmatch '(?i)data-toggle\s*=\s*["'']collapse') {
        return
    }
    $titlePattern = '(?is)<(?<tag>h\d|div|span)\b[^>]*class\s*=\s*["''][^"'']*\bpanel-title\b[^"'']*["''][^>]*>(?<title>.*?)</\k<tag>\s*>'
    $titles = [regex]::Matches($Html, $titlePattern)
    if ($titles.Count -eq 0) {
        # Some pages put the heading in panel-heading (h4 > a) with no panel-title element.
        $titles = [regex]::Matches($Html, '(?is)<(?<tag>div)\b[^>]*class\s*=\s*["''][^"'']*\bpanel-heading\b[^"'']*["''][^>]*>(?<title>.*?)</\k<tag>\s*>')
    }
    foreach ($title in $titles) {
        $afterTitle = $title.Index + $title.Length
        $collapseMatch = [regex]::Match(
            $Html.Substring($afterTitle),
            '(?i)<div\b[^>]*class\s*=\s*["''][^"'']*\b(?:panel-)?collapse\b[^"'']*["''][^>]*>'
        )
        if (-not $collapseMatch.Success) { continue }
        $collapseStart = $afterTitle + $collapseMatch.Index
        $collapseEnd = Get-SpPageDivEndIndex -Html $Html -StartIndex $collapseStart
        if ($collapseEnd -lt 0) { throw "Accordion panel is not balanced near: $(Get-SpPagePlainText -Html $title.Value)" }
        $collapseInner = $Html.Substring($collapseStart + $collapseMatch.Length, $collapseEnd - ($collapseStart + $collapseMatch.Length))
        $closeCollapse = $collapseInner.LastIndexOf("</", [System.StringComparison]::Ordinal)
        if ($closeCollapse -ge 0) { $collapseInner = $collapseInner.Substring(0, $closeCollapse) }
        $bodyHtml = $collapseInner.Trim()
        $bodyMatch = [regex]::Match($collapseInner, '(?is)^\s*<div\b[^>]*class\s*=\s*["''][^"'']*\bpanel-body\b[^"'']*["''][^>]*>')
        if ($bodyMatch.Success) {
            $bStart = $bodyMatch.Index
            $bEnd = Get-SpPageDivEndIndex -Html $collapseInner -StartIndex $bStart
            if ($bEnd -lt 0) { throw "Accordion panel body is not balanced near: $(Get-SpPagePlainText -Html $title.Value)" }
            $bClose = $collapseInner.LastIndexOf("</", $bEnd - 1, [System.StringComparison]::Ordinal)
            $bodyHtml = $collapseInner.Substring($bStart + $bodyMatch.Length, $bClose - ($bStart + $bodyMatch.Length)).Trim()
        }
        # Text after the heading link (e.g. a red "NEW!" span) becomes the badge; a panel-collapse
        # with the Bootstrap "in" class is open by default.
        $titleHtml = [string]$title.Groups["title"].Value
        $anchor = [regex]::Match($titleHtml, '(?is)<a\b[^>]*>(?<text>.*?)</a\s*>(?<rest>.*)$')
        $headingHtml = if ($anchor.Success) { $anchor.Groups["text"].Value } else { $titleHtml }
        $badge = if ($anchor.Success) { Get-SpPagePlainText -Html $anchor.Groups["rest"].Value } else { "" }
        $collapseTag = $collapseMatch.Value
        [pscustomobject]@{
            Heading = Get-SpPagePlainText -Html $headingHtml
            Badge = $badge
            DefaultOpen = ($collapseTag -match '(?i)class\s*=\s*["''][^"'']*\b(?:panel-)?collapse\b[^"'']*\bin\b')
            BodyHtml = $bodyHtml
        }
    }
}

# Replaces the legacy yellow "important notice" box (#ffff9e background) with a BC Design System
# warning InlineAlert (tokens inlined: surface #fef1d8, border #f8bb47, radius 4px, padding 1rem 1.5rem).
# The text before the first <br/> becomes the bold title. Example:
# <div style="background-color:#ffff9e"><strong>NOTICE:</strong><br/><br/>Text</div>
function ConvertTo-SpPageBcAlert {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][AllowEmptyString()][string]$Html)

    # Legacy black-bordered box (one inner div) becomes a BC Callout, light grey theme (surface #faf9f8,
    # 4px left border #013366, radius 4px 0 0 4px, padding 1rem 1.5rem, text #474543).
    $infoPattern = '(?is)<div\b[^>]*border\s*:\s*2px\s+solid\s+#000000[^>]*>\s*<div\b[^>]*>(?<inner>(?:(?!<div\b).)*?)</div\s*>\s*</div\s*>'
    $Html = [regex]::Replace($Html, $infoPattern, {
        param($m)
        $inner = ($m.Groups["inner"].Value -replace "[\u200B\uFEFF]", "") -replace '\s+', ' '
        '<div style="background-color:#faf9f8; border-left:4px solid #013366; border-radius:4px 0 0 4px; padding:1rem 1.5rem; margin-bottom:1rem; color:#474543;"><div>' + $inner.Trim() + '</div></div>'
    })

    $pattern = '(?is)<div\b[^>]*background-color\s*:\s*#ffff9e[^>]*>(?<inner>(?:(?!<div\b).)*?)</div\s*>'
    return [regex]::Replace($Html, $pattern, {
        param($m)
        $inner = $m.Groups["inner"].Value -replace "[\u200B\uFEFF]", ""
        $split = [regex]::Match($inner, '(?is)^(?<title>.*?)(?:<br\s*/?>\s*)+(?<body>.*)$')
        $titleHtml = if ($split.Success) { $split.Groups["title"].Value } else { "" }
        $bodyHtml = if ($split.Success) { $split.Groups["body"].Value.Trim() } else { $inner.Trim() }
        $titleText = [System.Net.WebUtility]::HtmlEncode((Get-SpPagePlainText -Html $titleHtml))
        $out = '<div style="background-color:#fef1d8; border:1px solid #f8bb47; border-radius:4px; padding:1rem 1.5rem; margin-bottom:1rem; color:#2D2D2D;">'
        if ($titleText) { $out += '<div style="margin:0 0 0.5rem 0; font-weight:700;">' + $titleText + '</div>' }
        $out + '<div>' + $bodyHtml + '</div></div>'
    })
}

# Unwraps links that point back to the page being migrated; the text stays, the link is dropped.
function Remove-SpPageSelfLinks {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$Html,
        [Parameter(Mandatory = $true)][string]$PageServerRelativeUrl
    )

    $removed = [System.Collections.Generic.List[string]]::new()
    $self = [System.Uri]::UnescapeDataString($PageServerRelativeUrl).TrimEnd("/")
    $result = [regex]::Replace($Html, '(?is)<a\b(?<attrs>[^>]*)>(?<text>.*?)</a\s*>', {
        param($m)
        $href = [regex]::Match($m.Groups["attrs"].Value, '(?i)\bhref\s*=\s*["''](?<v>[^"'']*)["'']')
        if (-not $href.Success) { return $m.Value }
        $path = [System.Uri]::UnescapeDataString(($href.Groups["v"].Value -replace '^(?i)https?://[^/]+', "" -replace '[?#].*$', "")).TrimEnd("/")
        if ($path -ieq $self) {
            $removed.Add($href.Groups["v"].Value)
            return $m.Groups["text"].Value
        }
        return $m.Value
    })
    return [pscustomobject]@{ Html = $result; Removed = @($removed) }
}

# Converts nested Bootstrap collapse sections (<a data-toggle="collapse" data-target="#id"> plus
# <div class="collapse" id="id">) into native <details><summary> so they stay collapsible in SPO
# without Bootstrap JavaScript. Sections whose target div cannot be found are left untouched.
function ConvertTo-SpPageNativeCollapse {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][AllowEmptyString()][string]$Html)

    $pattern = '(?is)(?:<(?<wt>h\d|p)\b[^>]*>\s*)?<a\b(?<attrs>[^>]*\bdata-toggle\s*=\s*["'']collapse["''][^>]*)>(?<title>.*?)</a\s*>(?:\s*</\k<wt>\s*>)?'
    $searchFrom = 0
    while ($searchFrom -lt $Html.Length) {
        $m = [regex]::Match($Html.Substring($searchFrom), $pattern)
        if (-not $m.Success) { break }
        $matchStart = $searchFrom + $m.Index
        $matchEnd = $matchStart + $m.Length
        $target = [regex]::Match($m.Groups["attrs"].Value, '(?i)\b(?:data-target|href)\s*=\s*["'']#([^"'']+)["'']')
        $div = if ($target.Success) {
            [regex]::Match($Html.Substring($matchEnd), '(?i)<div\b[^>]*\bid\s*=\s*["'']' + [regex]::Escape($target.Groups[1].Value) + '["''][^>]*>')
        } else { $null }
        if (-not $div -or -not $div.Success) { $searchFrom = $matchEnd; continue }
        $divStart = $matchEnd + $div.Index
        $divEnd = Get-SpPageDivEndIndex -Html $Html -StartIndex $divStart
        if ($divEnd -lt 0) { $searchFrom = $matchEnd; continue }
        $inner = $Html.Substring($divStart + $div.Length, $divEnd - ($divStart + $div.Length) - 6)
        $summary = [System.Net.WebUtility]::HtmlEncode((Get-SpPagePlainText -Html $m.Groups["title"].Value))
        $details = "<details><summary>$summary</summary>$inner</details>"
        $Html = $Html.Substring(0, $matchStart) + $details + $Html.Substring($divEnd)
        $searchFrom = $matchStart + ("<details><summary>$summary</summary>").Length
    }
    return $Html
}

# Returns the HTML before and after the accordion's panel-group container.
function Get-SpPageAccordionSurroundings {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string]$Html)

    $group = [regex]::Match($Html, '(?i)<div\b[^>]*class\s*=\s*["''][^"'']*\bpanel-group\b[^"'']*["''][^>]*>')
    if (-not $group.Success) { return [pscustomobject]@{ Before = ""; After = "" } }
    $end = Get-SpPageDivEndIndex -Html $Html -StartIndex $group.Index
    if ($end -lt 0) { throw "Accordion panel-group container is not balanced." }
    return [pscustomobject]@{ Before = $Html.Substring(0, $group.Index).Trim(); After = $Html.Substring($end).Trim() }
}

# Splits a leading block that contains only one image (plus span/br/nbsp wrappers) from the
# rest of the HTML. Returns the decoded image URL, alt text and remaining HTML, or $null.
function Split-SpPageLeadingImage {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][AllowEmptyString()][string]$Html)

    $trimmed = $Html.TrimStart()
    $blockEnd = -1
    if ($trimmed -match "^(?i)<div\b") {
        $blockEnd = Get-SpPageDivEndIndex -Html $trimmed -StartIndex 0
    } elseif ($trimmed -match "^(?is)<p\b.*?</p\s*>") {
        $blockEnd = $Matches[0].Length
    } elseif ($trimmed -match "^(?i)<img\b[^>]*>") {
        $blockEnd = $Matches[0].Length
    }
    if ($blockEnd -lt 0) { return $null }
    $block = $trimmed.Substring(0, $blockEnd)
    $images = [regex]::Matches($block, "(?i)<img\b[^>]*>")
    if ($images.Count -ne 1) { return $null }
    $leftover = [regex]::Replace($block, "(?i)</?(div|span|p|br|img)\b[^>]*>", "")
    if ((Get-SpPagePlainText -Html $leftover) -ne "") { return $null }
    $imgTag = $images[0].Value
    $src = if ($imgTag -match '(?i)\bsrc\s*=\s*["'']([^"'']*)["'']') { $Matches[1] } else { "" }
    $alt = if ($imgTag -match '(?i)\balt\s*=\s*["'']([^"'']*)["'']') { $Matches[1] } else { "" }
    if ([string]::IsNullOrWhiteSpace($src)) { return $null }
    $width = 0
    if ($imgTag -match '(?i)\bstyle\s*=\s*["''][^"'']*\bwidth\s*:\s*(\d+)px') { $width = [int]$Matches[1] }
    elseif ($imgTag -match '(?i)\bwidth\s*=\s*["'']?(\d+)') { $width = [int]$Matches[1] }

    $remaining = ($trimmed.Substring($blockEnd) -replace "^(\s|&#160;|&nbsp;)+", "").Trim()
    if ($remaining -ne "" -and -not $remaining.StartsWith("<")) {
        $blockTag = [regex]::Match($remaining, "(?i)<(p|div|h\d|ul|ol|table)\b")
        $textEnd = if ($blockTag.Success) { $blockTag.Index } else { $remaining.Length }
        $remaining = "<p>" + $remaining.Substring(0, $textEnd).Trim() + "</p>" + $remaining.Substring($textEnd)
    }
    return [pscustomobject]@{
        ImageUrl = [Uri]::UnescapeDataString([System.Net.WebUtility]::HtmlDecode($src))
        AltText = [System.Net.WebUtility]::HtmlDecode($alt)
        Width = $width
        RemainingHtml = $remaining
    }
}

function Get-SpPagePlacementFromRawExport {
    <#
    .SYNOPSIS
    Reads authoritative zone placement from an SP2016 exportwp.aspx XML file.
    #>
    param(
        [Parameter(Mandatory = $true)][string]$RawExportDirectory,
        [Parameter(Mandatory = $true)][string]$WebPartId
    )

    $rawFile = Get-ChildItem -LiteralPath $RawExportDirectory -File -Filter "*_$WebPartId.xml" |
        Select-Object -First 1
    if (-not $rawFile) {
        throw "Raw SP2016 export XML was not found for web part '$WebPartId' in '$RawExportDirectory'."
    }

    $rawXml = [System.Xml.XmlDocument]::new()
    $rawXml.Load($rawFile.FullName)
    $zoneNode = $rawXml.SelectSingleNode(
        "/*[local-name()='WebPart']/*[local-name()='ZoneID']"
    )
    $partOrderNode = $rawXml.SelectSingleNode(
        "/*[local-name()='WebPart']/*[local-name()='PartOrder']"
    )
    if (-not $zoneNode -or [string]::IsNullOrWhiteSpace($zoneNode.InnerText)) {
        throw "Raw SP2016 export XML is missing ZoneID for web part '$WebPartId'."
    }

    return [pscustomobject]@{
        ZoneID = [string]$zoneNode.InnerText
        PartOrder = if ($partOrderNode) { [int]$partOrderNode.InnerText } else { 0 }
    }
}

function New-SpPageWave1DryRun {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$SourcePagePath,
        [Parameter(Mandatory = $true)][string]$WebpartContentPath,
        [string]$ImageManifestPath,
        [Parameter(Mandatory = $true)][string]$RawExportDirectory,
        [Parameter(Mandatory = $true)][ValidateSet("dev", "test", "prod")][string]$TargetEnvironment,
        [Parameter(Mandatory = $true)][string]$OutputPath,
        [string]$LibraryPathMapPath,
        [string]$SourceHost,
        [string]$TargetSitePath,
        [string[]]$LeadingImageWebPartIds = @(),
        [ValidateSet("Native", "Spfx")][string]$AccordionOutput = "Native",
        [ValidateSet(1, 2)][int]$AccordionColumns = 2,
        [string]$HeaderText,
        [string[]]$HeaderSubtext,
        [string]$HeaderLogoUrl,
        [ValidateSet("None", "Administration")][string]$PageHeaderStyle = "None",
        [int]$PageHeaderZoneThemeIndex = 3,
        [string]$PageTitle,
        [string]$BreadcrumbSection,
        [string]$BreadcrumbSectionUrl
    )

    $useSpfx = $AccordionOutput -eq "Spfx"
    $hasHeader = $useSpfx -and -not [string]::IsNullOrWhiteSpace($HeaderText)
    $hasTitleBanner = $PageHeaderStyle -eq "Administration"
    if ($hasTitleBanner) {
        if ([string]::IsNullOrWhiteSpace($PageTitle)) {
            throw "-PageHeaderStyle Administration needs -PageTitle: the banner shows it."
        }
        if (-not [string]::IsNullOrWhiteSpace($HeaderText)) {
            throw "-PageHeaderStyle Administration and the Operations band (-HeaderText) are mutually exclusive."
        }
    }
    $spfxComponentId = "7a54e5d6-ff9d-4d4e-ac49-655e8948d60c"
    foreach ($path in @($SourcePagePath, $WebpartContentPath)) {
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
            throw "Migration input file was not found: $path"
        }
        if (-not [string]::IsNullOrWhiteSpace($RawExportDirectory) -and
            -not (Test-Path -LiteralPath $RawExportDirectory -PathType Container)) {
            throw "Raw SP2016 export directory was not found: $RawExportDirectory"
        }
    }

    $page = Get-Content -LiteralPath $SourcePagePath -Raw | ConvertFrom-Json
    foreach ($field in @("SiteName", "ServerRelativeUrl")) {
        if ([string]::IsNullOrWhiteSpace([string]$page.$field)) {
            throw "Source page is missing required field '$field'."
        }
    }

    $pageUrl = [string]$page.Url
    $webparts = @(Get-Content -LiteralPath $WebpartContentPath -Raw | ConvertFrom-Json)
    $pageWebparts = @($webparts | Where-Object {
        Test-SpPageUrlMatch `
            -WebPartPageUrl ([string]$_.PageUrl) `
            -PageUrl $pageUrl `
            -ServerRelativeUrl ([string]$page.ServerRelativeUrl)
    })
    $imagesByWebPart = @{}
    if (-not [string]::IsNullOrWhiteSpace($ImageManifestPath)) {
        if (-not (Test-Path -LiteralPath $ImageManifestPath -PathType Leaf)) {
            throw "Image manifest file was not found: $ImageManifestPath"
        }
        foreach ($image in @(Get-Content -LiteralPath $ImageManifestPath -Raw | ConvertFrom-Json)) {
            if ($null -eq $image -or -not $image.PSObject.Properties["SourceWebPartId"]) {
                continue
            }
            if (-not $imagesByWebPart.ContainsKey([string]$image.SourceWebPartId)) {
                $imagesByWebPart[[string]$image.SourceWebPartId] = [System.Collections.Generic.List[object]]::new()
            }
            $imagesByWebPart[[string]$image.SourceWebPartId].Add($image)
        }
    }
    # The collector emits one shared export for the wave; isolate this page
    # before turning its web parts into migration components.
    $contentEditors = @($pageWebparts)
    if ($contentEditors.Count -eq 0) {
        throw "Wave-1 requires at least one Content Editor web part for '$($page.ServerRelativeUrl)'."
    }

    $pathMap = @()
    if (-not [string]::IsNullOrWhiteSpace($LibraryPathMapPath)) {
        if (-not (Test-Path -LiteralPath $LibraryPathMapPath -PathType Leaf)) {
            throw "Library path map was not found: $LibraryPathMapPath"
        }
        if ([string]::IsNullOrWhiteSpace($SourceHost)) {
            throw "-SourceHost is required with -LibraryPathMapPath."
        }
        $pathMap = @(Import-Csv -LiteralPath $LibraryPathMapPath)
    }
    $pageLayout = if ($page.PSObject.Properties["Layout"]) { [string]$page.Layout } else { "" }
    $components = [System.Collections.Generic.List[object]]::new()
    $linkRewrites = [System.Collections.Generic.List[object]]::new()
    $droppedImages = [System.Collections.Generic.List[object]]::new()
    $section = 0
    $lastWasAccordion = $false
    $lastWasSpfx = $false
    $fullWidthSections = @{}
    $hasAccordion = $false
    $sectionSettings = [System.Collections.Generic.List[object]]::new()
    $spfxBodySection = if ($hasHeader) { 2 } else { 1 }
    if ($hasHeader) {
        # Native header band: logo left, editable heading right, strong emphasis (navy).
        $sectionSettings.Add([ordered]@{ Section = 1; Emphasis = 3 })
        if (-not [string]::IsNullOrWhiteSpace($HeaderLogoUrl)) {
            $components.Add([ordered]@{
                OutputType = "ImageWebPart"; ExistingImageUrl = $HeaderLogoUrl; AltText = "BC Operations Service logo"
                Role = "HeaderLogo"; Section = 1; Column = 1; CleanupFindings = @()
            })
        }
        $components.Add([ordered]@{
            OutputType = "TextWebPart"; Html = (& {
                # Native headings as the page editor saves them on the hand-built DEV BCSSS page: Titles 1-2 are H2, Title 3 is H3 in brand gold.
                $titles = @($HeaderText) + @($HeaderSubtext | Where-Object { $_ })
                $out = ""
                for ($i = 0; $i -lt $titles.Count; $i++) {
                    $line = [System.Net.WebUtility]::HtmlEncode($titles[$i])
                    $out += if ($i -eq 2) { '<h3 class="headingSpacingAbove headingSpacingBelow"><span class="fontColorBrand2">' + $line + '</span></h3>' } else { '<h2 class="headingSpacingAbove headingSpacingBelow">' + $line + '</h2>' }
                }
                $out
            })
            Role = "HeaderText"; Section = 1; Column = 2; CleanupFindings = @()
        })
    }

    if (-not [string]::IsNullOrWhiteSpace($PageTitle)) {
        # Breadcrumb + title (mirrors the SP2016 breadcrumb and H1). Home and the section link only
        # when the target exists; unknown levels stay plain text (bc-design-system-page-chrome.md).
        $encode = { param([string]$Value) [System.Net.WebUtility]::HtmlEncode($Value) }
        $homeUrl = if ($TargetSitePath) { $TargetSitePath } else { "/" }
        $sectionLabel = if ($BreadcrumbSection) { $BreadcrumbSection } else { [string]$page.SiteName }
        # Root-site pages (/Pages/...) have no section level: Home > title.
        $isRootPage = -not $BreadcrumbSection -and ([string]$page.ServerRelativeUrl) -match '^/Pages/'
        # No landing page given: link the section to its containing SitePages folder (path-map convention).
        $sectionUrl = if ($BreadcrumbSectionUrl) { $BreadcrumbSectionUrl }
            elseif ($TargetSitePath -and $page.SiteName -and [string]$page.SiteName -ne "Main") { "$($TargetSitePath.TrimEnd('/'))/SitePages/$($page.SiteName)/" }
        $sectionHtml = if ($sectionUrl) { "<a href=`"$(& $encode $sectionUrl)`">$(& $encode $sectionLabel)</a>" } else { & $encode $sectionLabel }
        $sectionCrumb = if ($isRootPage) { "" } else { "$sectionHtml &gt; " }
        $components.Add([ordered]@{
            OutputType = "TextWebPart"; Role = "PageHeader"; Section = $spfxBodySection; Column = 1; CleanupFindings = @()
            Html = "<p><a href=`"$(& $encode $homeUrl)`">Home</a> &gt; $sectionCrumb<strong>$(& $encode $PageTitle)</strong></p>" +
                $(if ($hasHeader -or $hasTitleBanner) { "" } else { "<h2>$(& $encode $PageTitle)</h2>" })
        })
    }

    # Keep source order: zone, then PartOrder from the raw export.
    if (-not [string]::IsNullOrWhiteSpace($RawExportDirectory)) {
        $contentEditors = @($contentEditors | Sort-Object -Property @{ Expression = {
            $placement = Get-SpPagePlacementFromRawExport -RawExportDirectory $RawExportDirectory -WebPartId ([string]$_.WebPartId)
            if ($placement) { [int]$placement.PartOrder } else { 0 }
        } })
    }
    foreach ($webpart in $contentEditors) {
        $webpartId = [string]$webpart.WebPartId
        $rawPlacement = if (-not [string]::IsNullOrWhiteSpace($RawExportDirectory)) {
            Get-SpPagePlacementFromRawExport -RawExportDirectory $RawExportDirectory -WebPartId $webpartId
        }
        $sourceZoneId = if ($rawPlacement) {
            [string]$rawPlacement.ZoneID
        } elseif ($webpart.PSObject.Properties["ZoneID"]) {
            [string]$webpart.ZoneID
        } elseif ($webpart.PSObject.Properties["ZoneId"]) {
            [string]$webpart.ZoneId
        } else {
            ""
        }
        if ([string]::IsNullOrWhiteSpace($sourceZoneId)) {
            throw "Source ZoneID metadata is required for web part '$webpartId' on '$($page.ServerRelativeUrl)'."
        }
        $sourcePartOrder = if ($rawPlacement) {
            [int]$rawPlacement.PartOrder
        } elseif ($webpart.PSObject.Properties["PartOrder"]) {
            [int]$webpart.PartOrder
        } else {
            0
        }
        $webpartImages = @(
            if ($imagesByWebPart.ContainsKey($webpartId)) { @($imagesByWebPart[$webpartId]) } else { @() }
        )
        # Normalize, swap manifest images, rewrite links. Returns the cleaned HTML fragment.
        $prepare = {
            param([string]$Fragment)
            $html = ConvertTo-SpPageNormalizedHtml -Html $Fragment
            $selfLinks = Remove-SpPageSelfLinks -Html $html -PageServerRelativeUrl ([string]$page.ServerRelativeUrl)
            $html = $selfLinks.Html
            foreach ($removedHref in @($selfLinks.Removed)) {
                $linkRewrites.Add([pscustomobject]@{
                    Source = $removedHref; Target = ""; Status = "SelfLinkUnwrapped"; MapStatus = "self"; SourceWebPartId = $webpartId
                })
            }
            if ($webpartImages.Count -gt 0) {
                $html = Replace-SpPageImageSources -Html $html -Images $webpartImages
                $html = $html -replace "><", "> <"
                $html = ConvertTo-SpPageNormalizedHtml -Html $html
            }
            if ($pathMap.Count -gt 0) {
                $mapped = ConvertTo-SpPageMappedLinks -Html $html -PathMap $pathMap -PageUrl $pageUrl `
                    -SourceHost $SourceHost -TargetSitePath $TargetSitePath `
                    -RelativeBase $(if ($TargetSitePath) { if ([string]$page.SiteName -eq "Main") { "../" } else { "../../" } } else { "" })
                foreach ($link in @($mapped.Links)) {
                    $link | Add-Member -NotePropertyName SourceWebPartId -NotePropertyValue $webpartId
                    $linkRewrites.Add($link)
                }
                $html = $mapped.Html
            }
            $dropped = [regex]::Matches($html, '(?i)<img\b[^>]*\bsrc\s*=\s*["'']data:[^>]*>')
            if ($dropped.Count -gt 0) {
                foreach ($d in $dropped) {
                    $altM = [regex]::Match($d.Value, '(?i)\balt\s*=\s*["'']([^"'']*)')
                    $droppedImages.Add([pscustomobject]@{ SourceWebPartId = $webpartId; Reason = "Embedded base64 image cannot be published inline; add it manually"; Alt = $altM.Groups[1].Value })
                }
                $html = [regex]::Replace($html, '(?i)<img\b[^>]*\bsrc\s*=\s*["'']data:[^>]*>', "")
            }
            return $html
        }
        $newComponent = {
            param([string]$OutputType, [string]$Html, [int]$Section)
            [ordered]@{
                SourceWebPartId = $webpartId
                SourceWebPartTitle = [string]$webpart.WebPartTitle
                SourceZoneId = $sourceZoneId
                SourcePartOrder = $sourcePartOrder
                OutputType = $OutputType
                Html = $Html
                Section = $Section
                Column = 1
                CleanupFindings = @(if ($OutputType -eq "TextWebPart") { Get-SpPageCleanupFindings -Html $Html })
            }
        }

        $content = [string]$webpart.Content
        $panels = @(Split-SpPageBootstrapAccordion -Html $content)
        $pieces = [System.Collections.Generic.List[object]]::new()
        if ($panels.Count -gt 0) {
            $hasAccordion = $true
            $around = Get-SpPageAccordionSurroundings -Html $content
            if ($around.Before) { $pieces.Add([pscustomobject]@{ Accordion = $false; Html = $around.Before; Raw = $true }) }
            if ($useSpfx) {
                $index = 0
                $spfxPanels = @(foreach ($panel in $panels) {
                    $index++
                    $spfxPanel = [ordered]@{ id = "panel-$index"; title = [string]$panel.Heading; buttonLabel = [string]$panel.Heading
                        html = (ConvertTo-SpPageNativeCollapse -Html (& $prepare $panel.BodyHtml)) }
                    if ($panel.Badge) { $spfxPanel["badge"] = [string]$panel.Badge }
                    if ($panel.DefaultOpen) { $spfxPanel["defaultOpen"] = $true }
                    $spfxPanel
                })
                $pieces.Add([pscustomobject]@{ Accordion = $false; Spfx = $true; Panels = $spfxPanels; Html = ""; Raw = $false })
            } else {
                $quick = "<h2>On this page</h2><ul>" + (($panels | ForEach-Object {
                    $heading = [System.Net.WebUtility]::HtmlEncode($_.Heading)
                    "<li><a href=`"#$(Get-SpPageHeadingAnchor -Heading $_.Heading)`">$heading</a></li>"
                }) -join "") + "</ul>"
                $pieces.Add([pscustomobject]@{ Accordion = $true; Html = $quick; Raw = $false })
                foreach ($panel in $panels) {
                    $pieces.Add([pscustomobject]@{
                        Accordion = $true; Html = (& $prepare $panel.BodyHtml); Raw = $false; Heading = $panel.Heading
                    })
                }
            }
            if ($around.After) { $pieces.Add([pscustomobject]@{ Accordion = $false; Html = $around.After; Raw = $true }) }
        } else {
            $wpTitle = [string]$webpart.WebPartTitle
            $body = $content
            if (-not [string]::IsNullOrWhiteSpace($wpTitle) -and
                $wpTitle -notin @("Content Editor", "ContentEditorWebPart") -and
                $body -notmatch '(?is)^\s*(<[^>]+>)*\s*<h[1-3]') {
                $body = "<h3>$([System.Net.WebUtility]::HtmlEncode($wpTitle))</h3>" + $body
            }
            $pieces.Add([pscustomobject]@{ Accordion = $false; Html = $body; Raw = $true })
        }

        $isFirstPiece = $true
        foreach ($piece in $pieces) {
            $html = if ($piece.Raw) { & $prepare $piece.Html } else { $piece.Html }
            $isSpfxPiece = $piece.PSObject.Properties["Spfx"] -ne $null
            if ($useSpfx) {
                # Text parts cannot sit in a full-width section, so the accordion gets its own section.
                if ($section -lt $spfxBodySection) { $section = $spfxBodySection }
                elseif ($isSpfxPiece -or $lastWasSpfx) { $section++ }
                if ($isSpfxPiece) { $fullWidthSections[$section] = $true }
                $lastWasSpfx = $isSpfxPiece
            } elseif ($piece.Accordion -or $section -eq 0 -or $lastWasAccordion) { $section++ }
            $lastWasAccordion = $piece.Accordion
            if ($piece.PSObject.Properties["Spfx"]) {
                $components.Add([ordered]@{
                    SourceWebPartId = $webpartId
                    SourceWebPartTitle = [string]$webpart.WebPartTitle
                    SourceZoneId = $sourceZoneId
                    SourcePartOrder = $sourcePartOrder
                    OutputType = "SpfxWebPart"
                    ComponentId = $spfxComponentId
                    Properties = [ordered]@{
                        panels = @($piece.Panels);                         showButtons = $true; startExpanded = $false; allowMultiple = $true; columns = $(if (@($piece.Panels).Count -gt 1) { $AccordionColumns } else { 1 })
                    }
                    Section = $section
                    Column = 1
                    CleanupFindings = @()
                })
                $isFirstPiece = $false
                continue
            }
            if ($piece.PSObject.Properties["Heading"]) {
                # Native collapsible section, collapsed by default (owner decision 2026-10-16; docs/analysis/accordion.md).
                $sectionSettings.Add([ordered]@{
                    Section = $section; Collapsible = $true; IsExpanded = $false; DisplayName = [string]$piece.Heading
                })
            }
            if ($isFirstPiece -and $webpartId -in @($LeadingImageWebPartIds)) {
                $lead = Split-SpPageLeadingImage -Html $html
                if (-not $lead) { throw "Web part '$webpartId' does not start with a single image block." }
                if ($useSpfx -or $hasTitleBanner) {
                    # The native header or the page title banner replaces the banner image.
                    $html = $lead.RemainingHtml
                } else {
                    if (-not $lead.ImageUrl.StartsWith("/sites/", [System.StringComparison]::OrdinalIgnoreCase)) {
                        throw "Leading image '$($lead.ImageUrl)' was not mapped to an SPO site path."
                    }
                    $image = & $newComponent "ImageWebPart" "" $section
                    $image.Remove("Html")
                    $image["ExistingImageUrl"] = $lead.ImageUrl
                    $image["AltText"] = $lead.AltText
                    if ($lead.Width -gt 0) { $image["ImageWidth"] = $lead.Width }
                    $image["Role"] = "Banner"
                    $components.Add($image)
                    $html = $lead.RemainingHtml
                }
            }
            $isFirstPiece = $false
            if ([string]::IsNullOrWhiteSpace($html)) { continue }
            $components.Add((& $newComponent "TextWebPart" (Set-SpPageBcDesignTokenStyles -Html (ConvertTo-SpPageBcAlert -Html $html)) $section))
        }
    }
    if ($hasAccordion -and -not $useSpfx -and $pageLayout -notin @("", "One-Column")) {
        throw "Accordion sections need a One-Column page layout; source layout is '$pageLayout'."
    }
    $plan = [ordered]@{
        Mode = "DryRun"
        Wave = $(if ($page.PSObject.Properties["Migration Plan"] -and -not [string]::IsNullOrWhiteSpace([string]$page."Migration Plan")) { [string]$page."Migration Plan" } else { "Wave-1" })
        TargetEnvironment = $TargetEnvironment
        Source = [ordered]@{
            SiteName = [string]$page.SiteName
            ServerRelativeUrl = [string]$page.ServerRelativeUrl
            Url = $pageUrl
        }
        PageName = Get-SpPageName -Page $page
        WouldPublish = $false
        ImageAssets = @(
            foreach ($images in $imagesByWebPart.Values) {
                foreach ($image in $images) {
                    [ordered]@{
                        SourceWebPartId = [string]$image.SourceWebPartId
                        SourceUrl = [string]$image.SourceUrl
                        AssetPath = [string]$image.DestinationRelativePath
                        AssetFileName = [string]$image.OutputFileName
                    }
                }
            }
        )
        Components = @($components)
        ContentCleanup = Get-SpPageCleanupSummary -Components @($components)
        LinkRewrites = @($linkRewrites)
        DroppedImages = @($droppedImages)
    }
    $isTwoColumnLayout = ($pageLayout -in @("One-Third-Right", "Two-Third-Left")) -or `
        (@($components | Where-Object { ($_.Contains("SourceZoneId") -and $_["SourceZoneId"] -eq "RightZone") -or ($_.PSObject.Properties["SourceZoneId"] -and $_.SourceZoneId -eq "RightZone") }).Count -gt 0)

    if ($isTwoColumnLayout) {
        $bodySection = if ($hasHeader) { 3 } elseif (-not [string]::IsNullOrWhiteSpace($PageTitle)) { 2 } else { 1 }
        foreach ($component in $components) {
            $role = if ($component.Contains("Role")) { [string]$component["Role"] } elseif ($component.PSObject.Properties["Role"]) { [string]$component.Role } else { "" }
            if ($role -in @("HeaderLogo", "HeaderText", "PageHeader")) {
                if ($hasHeader -and $role -eq "HeaderText") {
                    $component["Section"] = 1; $component["Column"] = 2
                } elseif ($hasHeader -and $role -eq "PageHeader") {
                    $component["Section"] = 2; $component["Column"] = 1
                } else {
                    $component["Section"] = 1; $component["Column"] = 1
                }
                continue
            }
            $zone = if ($component.Contains("SourceZoneId")) { [string]$component["SourceZoneId"] } elseif ($component.PSObject.Properties["SourceZoneId"]) { [string]$component.SourceZoneId } else { "" }
            $component["Section"] = $bodySection
            $component["Column"] = if ($zone -eq "RightZone") { 2 } else { 1 }
        }
        $plan["Sections"] = if ($bodySection -eq 3) { @("TwoColumnRight", "OneColumn", "TwoColumnLeft") } elseif ($bodySection -eq 2) { @("OneColumn", "TwoColumnLeft") } else { @("TwoColumnLeft") }
        if ($hasHeader) { $plan["SectionSettings"] = @($sectionSettings) }
        $plan["PageLayout"] = "Home"
    } elseif ($hasAccordion -or $hasHeader) {
        $plan["Sections"] = @(1..$section | ForEach-Object {
            # Header band is one-third left (logo) / two-thirds right (title), as built by hand in TEST.
            if ($hasHeader -and $_ -eq 1) { "TwoColumnRight" } elseif ($false) { "OneColumnFullWidth" } else { "OneColumn" }
        })
        $plan["SectionSettings"] = @($sectionSettings)
        # Home has no title area; the page shows its own banner image instead.
        $plan["PageLayout"] = "Home"
    } else {
        foreach ($component in $components) { $component.Remove("Section"); $component.Remove("Column") }
    }
    if ($hasTitleBanner) {
        # Administration playbook: a Banner web part in the page title area (white text on #65799e), as built
        # by hand on DEV Administration/Accessibility-Resources. ZoneThemeIndex 3 is the value stored there.
        $plan["PageLayout"] = "Article"
        $plan["PageHeader"] = [ordered]@{
            Style = "Administration"
            Title = $PageTitle
            LayoutType = "NoImage"
            TextAlignment = "Left"
            ShowPublishDate = $true
            ShowAuthor = $false
            ZoneThemeIndex = $PageHeaderZoneThemeIndex
        }
    }
    $parent = Split-Path -Parent $OutputPath
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    $plan | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
    return [pscustomobject]$plan
}

if ($MyInvocation.InvocationName -ne ".") {
    $spoConfig = Read-SpoConfiguration -Path $ConfigPath -Require @("Environment")
    if ([string]::IsNullOrWhiteSpace($SourcePagePath) -or
        [string]::IsNullOrWhiteSpace($WebpartContentPath) -or
        [string]::IsNullOrWhiteSpace($OutputPath)) {
        throw "SourcePagePath, WebpartContentPath, and OutputPath are required."
    }
    New-SpPageWave1DryRun `
        -SourcePagePath $SourcePagePath `
        -WebpartContentPath $WebpartContentPath `
        -ImageManifestPath $ImageManifestPath `
        -RawExportDirectory $RawExportDirectory `
        -TargetEnvironment $spoConfig.Environment `
        -OutputPath $OutputPath `
        -LibraryPathMapPath $LibraryPathMapPath `
        -SourceHost $SourceHost `
        -TargetSitePath $(if ($spoConfig.SiteUrl) { ([Uri][string]$spoConfig.SiteUrl).AbsolutePath.TrimEnd("/") } else { "" }) `
        -LeadingImageWebPartIds $LeadingImageWebPartIds `
        -AccordionOutput $AccordionOutput `
        -AccordionColumns $AccordionColumns `
        -HeaderText $HeaderText `
        -HeaderSubtext $HeaderSubtext `
        -HeaderLogoUrl $HeaderLogoUrl `
        -PageHeaderStyle $PageHeaderStyle `
        -PageHeaderZoneThemeIndex $PageHeaderZoneThemeIndex `
        -PageTitle $PageTitle `
        -BreadcrumbSection $BreadcrumbSection `
        -BreadcrumbSectionUrl $BreadcrumbSectionUrl
}
