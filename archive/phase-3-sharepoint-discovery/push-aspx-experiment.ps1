<#
.SYNOPSIS
    Phase 3.0 experiment: convert one real CEIS manual topic page (already rendered to
    Markdown by the docx-to-content plugin) to HTML via pandoc, then push it to SharePoint
    two ways — (1) as a raw hand-authored .aspx file (unsupported boundary probe) and (2) as
    a proper modern client-side page (supported route) — to test whether SharePoint can be a
    viable multi-format Renderer target.

    All tenant artifacts are TEST-DO-NOT-USE- labeled and removable per the staged-write
    protocol (docs/vision/master-initiative-plan-workstreams-and-phases.md, Subphase 3.0.2).
#>

[CmdletBinding()]
param(
    [string]$ConfigPath = (Join-Path $PSScriptRoot "config.psd1")
)

$ErrorActionPreference = "Stop"

$htmlFragmentPath = Join-Path $PSScriptRoot "aspx-experiment/initiate-a-file.html"
$image17Path = Join-Path $PSScriptRoot "../../runs/ceis-manual-v2/render/rendered-output/media/image17.gif"
$image18Path = Join-Path $PSScriptRoot "../../runs/ceis-manual-v2/render/rendered-output/media/image18.png"

foreach ($required in @($htmlFragmentPath, $image17Path, $image18Path)) {
    if (-not (Test-Path $required)) {
        Write-Error "Required input not found: $required. Run the pandoc conversion step first."
        exit 1
    }
}

if (-not (Test-Path $ConfigPath)) {
    Write-Error "Config file not found: $ConfigPath. Copy config.psd1.example to config.psd1 and fill in ClientId/TenantId/SiteUrl before running this script."
    exit 1
}

Write-Host "Loading configuration from $ConfigPath..." -ForegroundColor Cyan
$config = Import-PowerShellDataFile -Path $ConfigPath

foreach ($required in @("ClientId", "TenantId", "SiteUrl")) {
    if (-not $config.ContainsKey($required) -or [string]::IsNullOrWhiteSpace($config[$required])) {
        Write-Error "config.psd1 is missing a value for '$required'. This script cannot connect without it."
        exit 1
    }
}

Write-Host "Connecting to SPO at $($config.SiteUrl) (interactive delegated login — a browser window will open)..." -ForegroundColor Cyan
Connect-PnPOnline -Url $config.SiteUrl -ClientId $config.ClientId -Tenant $config.TenantId -Interactive -ForceAuthentication -ErrorAction Stop
Write-Host "Connected successfully!" -ForegroundColor Green

# --- 1. Upload the two referenced images to a test folder in Site Assets ---

$siteAssetsTestFolder = "SiteAssets/TEST-DO-NOT-USE-aspx-experiment"

Write-Host "Ensuring test folder exists: $siteAssetsTestFolder" -ForegroundColor Cyan
Resolve-PnPFolder -SiteRelativePath $siteAssetsTestFolder | Out-Null

Write-Host "Uploading image17.gif and image18.png..." -ForegroundColor Cyan
Add-PnPFile -Path $image17Path -Folder $siteAssetsTestFolder | Out-Null
Add-PnPFile -Path $image18Path -Folder $siteAssetsTestFolder | Out-Null

$web = Get-PnPWeb
$image17AbsoluteUrl = "$($web.Url)/$siteAssetsTestFolder/image17.gif"
$image18AbsoluteUrl = "$($web.Url)/$siteAssetsTestFolder/image18.png"

Write-Host "Uploaded image17 to: $image17AbsoluteUrl" -ForegroundColor Green
Write-Host "Uploaded image18 to: $image18AbsoluteUrl" -ForegroundColor Green

# --- 2. Load the pandoc HTML fragment and rewrite image paths to tenant URLs ---

Write-Host "Rewriting HTML image paths to tenant URLs..." -ForegroundColor Cyan
$rawHtml = Get-Content -Path $htmlFragmentPath -Raw
$rewrittenHtml = $rawHtml `
    -replace '\.\./media/image17\.gif', $image17AbsoluteUrl `
    -replace '\.\./media/image18\.png', $image18AbsoluteUrl

if ($rewrittenHtml -match [regex]::Escape('../media/')) {
    Write-Error "Rewrite incomplete — '../media/' still present in `$rewrittenHtml. Check the image filenames match exactly."
    exit 1
}

Write-Host "Rewrite complete. First 300 chars of rewritten HTML:" -ForegroundColor Cyan
Write-Host $rewrittenHtml.Substring(0, [Math]::Min(300, $rewrittenHtml.Length))

# --- 3. Push the raw hand-authored .aspx file directly to Site Pages (boundary probe) ---

$aspxShell = @"
<%@ Page Language="C#" %>
<html>
<head><title>TEST-DO-NOT-USE raw aspx probe</title></head>
<body>
$rewrittenHtml
</body>
</html>
"@

$rawAspxLocalPath = Join-Path $PSScriptRoot "aspx-experiment/raw-page.aspx"
Set-Content -Path $rawAspxLocalPath -Value $aspxShell -Encoding UTF8
Write-Host "Wrote raw ASPX shell to $rawAspxLocalPath" -ForegroundColor Cyan

Write-Host "Uploading raw .aspx file to Site Pages (boundary probe — may or may not render as a page)..." -ForegroundColor Cyan
Add-PnPFile -Path $rawAspxLocalPath -Folder "Site Pages" -NewFileName "TEST-DO-NOT-USE-raw-initiate-a-file.aspx" | Out-Null

$rawAspxUrl = "$($web.Url)/SitePages/TEST-DO-NOT-USE-raw-initiate-a-file.aspx"
Write-Host ""
Write-Host "=== RAW ASPX PROBE PUSHED ===" -ForegroundColor Yellow
Write-Host "Open this URL in your browser and report what you see:" -ForegroundColor Yellow
Write-Host $rawAspxUrl -ForegroundColor Yellow
Write-Host "(Does it render as a page? Download as a raw file? Show an error? Show SharePoint's ""this is an old page"" banner?)" -ForegroundColor Yellow
Write-Host ""

# --- 4. Push the same content as a proper modern client-side page (supported route) ---

Write-Host "Creating modern client-side page via Add-PnPPage..." -ForegroundColor Cyan
$modernPage = Add-PnPPage -Name "TEST-DO-NOT-USE-modern-initiate-a-file" -LayoutType Article -Publish:$false

Add-PnPPageTextPart -Page $modernPage -Text $rewrittenHtml

Write-Host "Publishing modern page..." -ForegroundColor Cyan
Set-PnPPage -Identity $modernPage -Publish

$modernPageUrl = "$($web.Url)/SitePages/TEST-DO-NOT-USE-modern-initiate-a-file.aspx"
Write-Host ""
Write-Host "=== MODERN PAGE PUSHED ===" -ForegroundColor Yellow
Write-Host "Open this URL in your browser and report what you see:" -ForegroundColor Yellow
Write-Host $modernPageUrl -ForegroundColor Yellow
Write-Host "(Do headings, tables, and both images render correctly inside the Text web part?)" -ForegroundColor Yellow
Write-Host ""

Write-Host "=== SUMMARY ===" -ForegroundColor Cyan
Write-Host "Raw ASPX probe:   $rawAspxUrl"
Write-Host "Modern page:      $modernPageUrl"
