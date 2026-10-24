<#
.SYNOPSIS
    Converts a downloaded classic ASPX page into clean design-system styled HTML.
.DESCRIPTION
    Converts one local ASPX file to a separate HTML file, removes known legacy
    presentation artifacts, rejects common active markup, and protects existing output.
.INPUTS
    -SourcePath: Existing local ASPX file.
    -OutputPath: Optional output file path; defaults to a sibling .html file.
    -Overwrite: Explicitly permits replacing an existing output file.
.OUTPUTS
    Writes one UTF-8 HTML file and reports its path.
.NOTES
    Key input dependencies: PowerShell 7 and a local ASPX source file.
    This is not a general-purpose HTML sanitizer.
.EXAMPLE
    pwsh -File .\scripts\convert-aspx-to-html.ps1 -SourcePath .\page.aspx -OutputPath .\page.html
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$SourcePath,

    [Parameter(Mandatory = $false)]
    [string]$OutputPath,

    [Parameter(Mandatory = $false)]
    [switch]$Overwrite
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $SourcePath -PathType Leaf)) {
    throw "Source file not found or not a file: $SourcePath"
}

$resolvedSource = (Resolve-Path -LiteralPath $SourcePath).Path
if (-not $OutputPath) {
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($resolvedSource)
    $dir = [System.IO.Path]::GetDirectoryName($resolvedSource)
    $OutputPath = Join-Path $dir "$baseName.html"
}

$resolvedOutput = [System.IO.Path]::GetFullPath($OutputPath)
if (Test-Path -LiteralPath $OutputPath -PathType Container) {
    throw "Output path is a directory: $OutputPath"
}
if (Test-Path -LiteralPath $OutputPath -PathType Leaf) {
    $resolvedOutput = (Resolve-Path -LiteralPath $OutputPath).Path
}
if ($resolvedOutput.Equals($resolvedSource, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Output path must not resolve to the source file: $resolvedSource"
}
if ((Test-Path -LiteralPath $OutputPath -PathType Leaf) -and -not $Overwrite) {
    throw "Output file already exists. Use -Overwrite to replace it: $resolvedOutput"
}

$rawContent = Get-Content -LiteralPath $resolvedSource -Raw -Encoding UTF8
$baseName = [System.IO.Path]::GetFileNameWithoutExtension($resolvedSource)

# Extract title
$pageTitle = $baseName -replace "[-_]", " "
if ($rawContent -match '<title>([^<]+)</title>') {
    $pageTitle = $Matches[1].Trim()
}

# Clean ASPX markup
$body = $rawContent
$body = [System.Text.RegularExpressions.Regex]::Replace($body, '<%@.*?%>', '', [System.Text.RegularExpressions.RegexOptions]::Singleline)
$body = [System.Text.RegularExpressions.Regex]::Replace($body, '<%--.*?--%>', '', [System.Text.RegularExpressions.RegexOptions]::Singleline)
$body = [System.Text.RegularExpressions.Regex]::Replace($body, '<script[^>]*src=[^>]*WebResource[^>]*>.*?</script>', '', [System.Text.RegularExpressions.RegexOptions]::Singleline)

# Strip MS Office XML conditional comments
$body = [System.Text.RegularExpressions.Regex]::Replace($body, '<!--\[if.*?<!\[endif\]-->', '', [System.Text.RegularExpressions.RegexOptions]::Singleline)

if ($body -match '(?si)<body[^>]*>(.*?)</body>') {
    $body = $Matches[1]
}

# Clean legacy layout markup: spacer images and font wrappers
$body = [System.Text.RegularExpressions.Regex]::Replace($body, '<img[^>]*spacer\.gif[^>]*>', '', [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
$body = [System.Text.RegularExpressions.Regex]::Replace($body, '</?font[^>]*>', '', [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)

# Remove redundant duplicated title in body if already extracted into header
$escapedTitle = [System.Text.RegularExpressions.Regex]::Escape($pageTitle)
$body = [System.Text.RegularExpressions.Regex]::Replace($body, "(?si)<p[^>]*>\s*(?:<b[^>]*>)?\s*(?:<!--.*?-->)?\s*$escapedTitle\s*(?:</b>)?\s*</p>", "")

# Clean up empty anchor tags (e.g. <a name="top"></a>)
$body = [System.Text.RegularExpressions.Regex]::Replace($body, '(?i)<a\s+name="top"\s*>\s*</a>', '')

# Clean up empty table cells and empty rows left behind by spacer removal
$body = [System.Text.RegularExpressions.Regex]::Replace($body, '(?si)<td[^>]*>(&nbsp;|\s)*</td>', '')
$body = [System.Text.RegularExpressions.Regex]::Replace($body, '(?si)<tr[^>]*>\s*</tr>', '')

# If a table has only 1 row and 1 cell remaining, unwrap it to clean semantic HTML
$body = [System.Text.RegularExpressions.Regex]::Replace($body, '(?si)<table[^>]*>\s*<tr[^>]*>\s*<td[^>]*>(.*?)</td>\s*</tr>\s*</table>', '$1')
$body = [System.Text.RegularExpressions.Regex]::Replace($body, '(?si)<table[^>]*>\s*<tr[^>]*>\s*<td[^>]*>(.*?)</td>\s*</tr>\s*</table>', '$1')

$activeMarkupPatterns = @(
    '<\s*(script|iframe|frame|object|embed)\b',
    '<[^>]*\bon[a-z][a-z0-9:_-]*\s*=',
    '<[^>]*\bsrcdoc\s*=',
    '\b(?:href|src|action|formaction|xlink:href)\s*=\s*(?:["'']\s*)?javascript\s*:'
)
foreach ($pattern in $activeMarkupPatterns) {
    if ([System.Text.RegularExpressions.Regex]::IsMatch(
        $body,
        $pattern,
        [System.Text.RegularExpressions.RegexOptions]::IgnoreCase -bor [System.Text.RegularExpressions.RegexOptions]::Singleline
    )) {
        throw "Unsupported active HTML detected; no output was written."
    }
}

$html = @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>$pageTitle</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 24px;
            background-color: #f3f4f6;
            color: #1f2937;
            line-height: 1.6;
        }
        .container {
            max-width: 960px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 8px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
            overflow: hidden;
            border-top: 5px solid #003366;
        }
        header {
            background-color: #003366;
            color: #ffffff;
            padding: 20px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        header h1 {
            margin: 0;
            font-size: 1.4rem;
            font-weight: 600;
        }
        .badge {
            background-color: #fcba19;
            color: #003366;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: bold;
        }
        .content {
            padding: 32px;
        }
        .source-meta {
            font-size: 0.85rem;
            color: #6b7280;
            margin-bottom: 24px;
            padding-bottom: 12px;
            border-bottom: 1px solid #e5e7eb;
        }
        .legacy-body {
            font-size: 1rem;
            color: #2d3748;
        }
        .legacy-body p {
            margin-bottom: 16px;
        }
        .legacy-body a {
            color: #1a5a96;
            text-decoration: underline;
        }
        .legacy-body a:hover {
            color: #003366;
        }
        /* Neutralize legacy layout tables */
        table {
            border-collapse: collapse;
            max-width: 100%;
            margin: 16px 0;
        }
        td, th {
            padding: 6px 10px;
            vertical-align: top;
            border: none;
        }
        /* Style only actual data tables with headers or explicit borders */
        table:has(th), table[border]:not([border="0"]), table.data-table {
            width: 100%;
            border: 1px solid #d1d5db;
        }
        table:has(th) th, table[border]:not([border="0"]) th, table.data-table th,
        table:has(th) td, table[border]:not([border="0"]) td, table.data-table td {
            border: 1px solid #d1d5db;
            padding: 8px 12px;
            text-align: left;
        }
        table:has(th) th, table[border]:not([border="0"]) th, table.data-table th {
            background-color: #f9fafb;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>$pageTitle</h1>
            <span class="badge">Legacy Archived Document</span>
        </header>
        <div class="content">
            <div class="source-meta">
                <strong>Source File:</strong> $([System.IO.Path]::GetFileName($resolvedSource))<br>
                <strong>Converted:</strong> $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
            </div>
            <div class="legacy-body">
                $body
            </div>
        </div>
    </div>
</body>
</html>
"@

Set-Content -LiteralPath $resolvedOutput -Value $html -Encoding UTF8
Write-Host "Converted: $resolvedSource -> $resolvedOutput" -ForegroundColor Green
