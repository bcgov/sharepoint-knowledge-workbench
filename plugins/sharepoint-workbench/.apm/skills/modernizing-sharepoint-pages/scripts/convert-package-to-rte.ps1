<#
.SYNOPSIS
Rewrites the Text web part HTML of a publication package into markup the modern page
text editor keeps on edit (offline; reads and writes local files only).

.DESCRIPTION
The modern Text web part editor drops inline styles and wrapper divs when a person edits
the part. This script (1) turns the BC alert and callout boxes into tables, the only
box-like element the editor keeps, then (2) runs PnP.Framework HtmlTransformator, which
maps colours, sizes and table styles to editor classes. See
references/text-web-part-html-sanitization.md. The input package is never modified.

.KEY INPUT DEPENDENCIES
- PnP.PowerShell module (PnP.Framework.Modernization.Transform.HtmlTransformator)
- A package.json from new-spo-page-publication-dry-run.ps1

.USAGE
pwsh -File plugins\sp-migration\scripts\publication\convert-package-to-rte.ps1 `
  -PackagePath temp\operations-policy-manual\package.json `
  -OutputPath temp\operations-policy-manual\package-rte.json

.FUNCTION INDEX
Find-SpRteMatchingDivEnd, ConvertTo-SpRteBoxTables, ConvertTo-SpRteNormalizedHtml, ConvertTo-SpRteHtml.
#>
[CmdletBinding()]
param(
    [string]$PackagePath,
    [string]$OutputPath,
    [switch]$LibraryMode
)

$ErrorActionPreference = "Stop"

# Returns the index just after the </div> that closes the <div> opening at $StartIndex.
function Find-SpRteMatchingDivEnd {
    param([string]$Html, [int]$StartIndex)
    $depth = 0
    foreach ($m in [regex]::Matches($Html.Substring($StartIndex), '(?i)<(/?)div\b[^>]*>')) {
        if ($m.Groups[1].Value -eq '/') { $depth-- } else { $depth++ }
        if ($depth -eq 0) { return $StartIndex + $m.Index + $m.Length }
    }
    throw "Unbalanced <div> in package HTML."
}

# Alert (#fef1d8) and callout (#faf9f8) -> full-width, one-cell editor-native tables (markup captured from the tenant editor).
function ConvertTo-SpRteBoxTables {
    param([Parameter(Mandatory)][AllowEmptyString()][string]$Html)
    $openPattern = '(?i)<div\b[^>]*background-color:\s*#(?<c>fef1d8|faf9f8)[^>]*>'
    $alertHead = 'background-color:rgb(248, 187, 71);border:1px solid rgb(248, 187, 71);color:rgb(45, 45, 45);'
    $fills = @{
        fef1d8 = 'background-color:rgb(254, 241, 216);border:1px solid rgb(248, 187, 71);color:rgb(45, 45, 45);'
        faf9f8 = 'background-color:rgb(250, 249, 248);border-left:6px solid rgb(1, 51, 102);color:rgb(45, 45, 45);'
    }
    while ($true) {
        $open = [regex]::Match($Html, $openPattern)
        if (-not $open.Success) { break }
        $end = Find-SpRteMatchingDivEnd -Html $Html -StartIndex $open.Index
        $inner = $Html.Substring($open.Index + $open.Length, $end - $open.Index - $open.Length - '</div>'.Length).Trim()
        $head = ''
        if ($open.Groups['c'].Value -ieq 'fef1d8') {
            $title = [regex]::Match($inner, '(?is)^\s*<div\b[^>]*>(?<t>.*?)</div>(?<rest>.*)$')
            if ($title.Success) {
                $head = '<thead><tr><th class="lightBackground" style="' + $alertHead + '" scope="col"><strong>' + $title.Groups['t'].Value.Trim() + '</strong></th></tr></thead>'
                $inner = $title.Groups['rest'].Value.Trim()
            }
        }
        $inner = [regex]::Replace($inner, '(?is)<div\b[^>]*>(.*?)</div>', '<p>$1</p>')
        $table = '<figure class="table tableCenterAlign canvasRteResponsiveTable" title="Table"><table class="simpleTableStyleNeutral customCells ck-table-resized"><colgroup><col style="width:100%;"></colgroup>' + $head + '<tbody><tr><td class="lightBackground" style="' + $fills[$open.Groups['c'].Value.ToLower()] + '">' + $inner + '</td></tr></tbody></table></figure>'
        $Html = $Html.Substring(0, $open.Index) + $table + $Html.Substring($end)
    }
    return $Html
}

# Drops the bare token wrapper div (the editor keeps no layout divs) and maps <i>/<b> to <em>/<strong>.
function ConvertTo-SpRteNormalizedHtml {
    param([Parameter(Mandatory)][AllowEmptyString()][string]$Html)
    $open = [regex]::Match($Html, '(?i)<div\b[^>]*data-sp-bc-tokens[^>]*>')
    while ($open.Success) {
        $end = Find-SpRteMatchingDivEnd -Html $Html -StartIndex $open.Index
        $inner = $Html.Substring($open.Index + $open.Length, $end - $open.Index - $open.Length - '</div>'.Length)
        $Html = $Html.Substring(0, $open.Index) + $inner + $Html.Substring($end)
        $open = [regex]::Match($Html, '(?i)<div\b[^>]*data-sp-bc-tokens[^>]*>')
    }
    $Html = $Html -replace '(?i)<(/?)i(?=[\s>])', '<$1em' -replace '(?i)<(/?)b(?=[\s>])', '<$1strong'
    $Html = [regex]::Replace($Html, '(?i)(<a\b[^>]*?)\s+style="[^"]*"', '$1')
    return $Html
}

# Boxes to tables, normalise, then PnP HtmlTransformator (requires PnP.PowerShell to be importable).
function ConvertTo-SpRteHtml {
    param([Parameter(Mandatory)][AllowEmptyString()][string]$Html)
    if (-not ('PnP.Framework.Modernization.Transform.HtmlTransformator' -as [type])) {
        Import-Module PnP.PowerShell -ErrorAction Stop
    }
    $transformator = [PnP.Framework.Modernization.Transform.HtmlTransformator]::new($null)
    $prepared = ConvertTo-SpRteNormalizedHtml -Html (ConvertTo-SpRteBoxTables -Html $Html)
    # Box figures are already editor-native; hide them from the transformer, which would rewrite them.
    $boxes = [System.Collections.Generic.List[string]]::new()
    $prepared = [regex]::Replace($prepared, '(?is)<figure class="table .*?</figure>', {
        param($m)
        $boxes.Add($m.Value)
        '<p>SPBOXTOKEN' + ($boxes.Count - 1) + 'END</p>'
    })
    $out = $transformator.Transform($prepared, $false)
    for ($i = 0; $i -lt $boxes.Count; $i++) {
        $out = [regex]::Replace($out, '(?is)(<span>)?<p>\s*SPBOXTOKEN' + $i + 'END\s*</p>(</span>)?', [System.Text.RegularExpressions.MatchEvaluator]{ param($m) $boxes[$i] })
    }
    return ConvertTo-SpRteTrimmedHtml -Html $out
}

# Removes empty paragraphs and <br> at the very start and end of a Text web part; each adds a blank line of padding in the editor.
function ConvertTo-SpRteTrimmedHtml {
    param([Parameter(Mandatory)][AllowEmptyString()][string]$Html)
    $blank = '(?:\s|&nbsp;|<br\s*/?>)*'
    $emptyPara = '(?:<span>)?<p[^>]*>' + $blank + '</p>(?:</span>)?'
    $Html = [regex]::Replace($Html, '(?is)^(?:\s|' + $emptyPara + ')+', '')
    $Html = [regex]::Replace($Html, '(?is)(?:\s|' + $emptyPara + ')+$', '')
    $Html = [regex]::Replace($Html, '(?is)(?:<br\s*/?>|\s)+(</p>(?:</span>)?)$', '$1')
    return $Html
}

# The Operations header band title is already editor-native (H2/H3 with spacing classes); the transformer would shift its heading level.
function Test-SpRteComponentNeedsTransform {
    param([Parameter(Mandatory)]$Component)
    $role = if ($Component.PSObject.Properties['Role']) { [string]$Component.Role } else { '' }
    return $Component.OutputType -eq 'TextWebPart' -and
        -not [string]::IsNullOrWhiteSpace([string]$Component.Html) -and
        $role -ne 'HeaderText'
}

if (-not $LibraryMode) {
    if ([string]::IsNullOrWhiteSpace($PackagePath) -or [string]::IsNullOrWhiteSpace($OutputPath)) {
        throw "-PackagePath and -OutputPath are required."
    }
    $package = Get-Content -LiteralPath $PackagePath -Raw -Encoding UTF8 | ConvertFrom-Json
    $count = 0
    foreach ($component in $package.Components) {
        if (Test-SpRteComponentNeedsTransform -Component $component) {
            $component.Html = ConvertTo-SpRteHtml -Html ([string]$component.Html)
            $count++
        }
    }
    $package | ConvertTo-Json -Depth 50 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
    Write-Host "Transformed $count text web part(s) -> $OutputPath"
}
