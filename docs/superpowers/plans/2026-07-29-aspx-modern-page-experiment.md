# SharePoint ASPX / Modern-Page Conversion Experiment — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove or disprove, with real tenant evidence, whether a single real CEIS manual topic
page (Markdown source) can be converted and pushed to SharePoint as (a) a raw hand-authored
`.aspx` file and (b) a modern client-side page — informing whether SharePoint can be a viable
multi-format Renderer target for this initiative's `Content + Template + Renderer = Published
Output` vision, alongside the existing Markdown renderer.

**Architecture:** A local conversion step (pandoc, already the repo's canonical MD↔HTML tool)
turns one real topic page into an HTML fragment. A PnP PowerShell push script then (1) uploads
the topic's 2 referenced images to a test folder in Site Assets and rewrites the HTML to point
at them, (2) uploads a raw hand-wrapped `.aspx` file containing that HTML directly into Site
Pages (the un-supported/boundary-probe path), and (3) creates a proper modern client-side page
via `Add-PnPPage`/`Add-PnPPageTextPart` using the same HTML (the supported/fallback path). Both
pushed artifacts are `TEST-DO-NOT-USE-*` labeled per the staged-write protocol already used
throughout this session. This is a **hands-on evidence-gathering PoC**, not production code —
there is no automated test suite; verification is manual (open each page in the browser) exactly
like every other SharePoint probe already logged in `research-summary-phase3-sharepoint-write-capability-discovery.md`.

**Tech Stack:** PowerShell 7 (`pwsh`), `PnP.PowerShell` 3.3.0, `pandoc` (already a repo
dependency per `DEPENDENCIES.md`). Same `config.psd1` / `Connect-PnPOnline -Interactive
-ForceAuthentication` auth pattern as `phase-3-0-tenant-discovery.ps1`.

## Global Constraints

- All tenant artifacts created must be named `TEST-DO-NOT-USE-*`, per the staged-write protocol
  in `docs/vision/master-initiative-plan-workstreams-and-phases.md` Subphase 3.0.2 — reversible,
  removed after the probe with only evidence (screenshots/transcripts) kept.
- Reuse the existing auth pattern exactly: `Import-PowerShellDataFile -Path ./config.psd1` then
  `Connect-PnPOnline -Url $config.SiteUrl -ClientId $config.ClientId -Tenant $config.TenantId
  -Interactive -ForceAuthentication -ErrorAction Stop` (see
  `tools/phase-3-sharepoint-discovery/phase-3-0-tenant-discovery.ps1` lines 257-267).
- Source content: `runs/ceis-manual-v2/render/rendered-output/pages/initiate-a-file--51d1f554.md`
  (109 lines, 4 headings, 2 images: `../media/image17.gif`, `../media/image18.png`) — chosen for
  being small enough to fully inspect by eye, per the user's request for "one representative
  topic page with headings/images."
- New files live under `tools/phase-3-sharepoint-discovery/` (matching the existing
  `agents/`/`skills/`/`reports/` convention for this session's artifacts), not under `temp/`,
  since these are Phase 3.0 evidence artifacts, not throwaway scratch.
- Docx/pptx conversion is explicitly **out of scope** for this plan — flag as a future backlog
  item in `research-summary-phase3-sharepoint-write-capability-discovery.md` only, per the user's explicit decision not to expand
  today's experiment.
- No unit tests apply here (this is a live-tenant PowerShell probe, consistent with every prior
  Phase 3.0 write-exploration task) — verification is the user manually opening each pushed URL
  in a browser and reporting what renders.

---

### Task 1: Convert the representative topic page to an HTML fragment with pandoc

**Files:**
- Create: `tools/phase-3-sharepoint-discovery/aspx-experiment/initiate-a-file.html`
- Create: `tools/phase-3-sharepoint-discovery/aspx-experiment/README.md` (documents how this
  folder's artifacts were generated, for reproducibility)

**Interfaces:**
- Consumes: `runs/ceis-manual-v2/render/rendered-output/pages/initiate-a-file--51d1f554.md`
  (existing repo file, read-only).
- Produces: `initiate-a-file.html` — a pandoc-generated HTML fragment (not a full HTML document;
  `pandoc`'s default `-t html` output for a `.md` input is a bare fragment: `<h1>`/`<p>`/`<img>`
  tags with no `<html>`/`<body>` wrapper) that Task 2 will further rewrite and Tasks 3/4 will
  each wrap differently. Image `src` attributes in this fragment will read `../media/image17.gif`
  and `../media/image18.png` exactly as they appear in the source Markdown — Task 2 rewrites
  these to tenant URLs.

- [ ] **Step 1: Create the aspx-experiment folder and run pandoc**

```bash
mkdir -p tools/phase-3-sharepoint-discovery/aspx-experiment
pandoc runs/ceis-manual-v2/render/rendered-output/pages/initiate-a-file--51d1f554.md \
  -f markdown -t html \
  -o tools/phase-3-sharepoint-discovery/aspx-experiment/initiate-a-file.html
```

- [ ] **Step 2: Verify the fragment looks right**

```bash
cat tools/phase-3-sharepoint-discovery/aspx-experiment/initiate-a-file.html
```

Expected: HTML containing at least one `<h1>`/`<h2>` heading tag, an `<img src="../media/image17.gif">`
tag, an `<img src="../media/image18.png">` tag, and no `<html>`/`<head>`/`<body>` wrapper tags
(pandoc's default HTML writer produces a fragment, not a full document — this fragment-only
behavior is exactly what Tasks 3/4 need, since each will supply its own wrapper).

- [ ] **Step 3: Write the README documenting the reproduction steps**

```markdown
# ASPX / Modern-Page Conversion Experiment — Artifacts

Generated by running Task 1-4 of
`docs/superpowers/plans/2026-07-29-aspx-modern-page-experiment.md`.

- `initiate-a-file.html` — pandoc HTML fragment of
  `runs/ceis-manual-v2/render/rendered-output/pages/initiate-a-file--51d1f554.md`, generated via:
  `pandoc <source>.md -f markdown -t html -o initiate-a-file.html`
- `raw-page.aspx` — the same fragment wrapped in a minimal classic ASPX shell, pushed directly to
  Site Pages via `Add-PnPFile` (the unsupported/boundary-probe path).
- `push-aspx-experiment.ps1` — the PnP PowerShell script that uploads the 2 referenced images,
  rewrites the HTML's image paths to the tenant, pushes the raw `.aspx` file, and creates the
  modern client-side page.

See `docs/research/research-summary-phase3-sharepoint-write-capability-discovery.md` §15 for the observed
results of both push paths.
```

- [ ] **Step 4: Commit**

```bash
git add tools/phase-3-sharepoint-discovery/aspx-experiment/
git commit -m "Add pandoc HTML fragment for aspx/modern-page experiment"
```

---

### Task 2: Write the PnP push script — image upload + path rewrite

**Files:**
- Create: `tools/phase-3-sharepoint-discovery/push-aspx-experiment.ps1`

**Interfaces:**
- Consumes: `tools/phase-3-sharepoint-discovery/aspx-experiment/initiate-a-file.html` (Task 1's
  output), `runs/ceis-manual-v2/render/rendered-output/media/image17.gif`,
  `runs/ceis-manual-v2/render/rendered-output/media/image18.png` (existing repo files),
  `tools/phase-3-sharepoint-discovery/config.psd1` (existing, gitignored, real tenant creds).
- Produces: a PowerShell variable `$rewrittenHtml` (string) — the fragment from Task 1 with both
  `img src` attributes replaced with absolute tenant Site Assets URLs — that Tasks 3 and 4 both
  consume in the same script run. Also produces the constant
  `$script:SiteAssetsTestFolder = "SiteAssets/TEST-DO-NOT-USE-aspx-experiment"` referenced by
  Tasks 3/4's own steps.

- [ ] **Step 1: Write the script's parameter block, config loading, and connection (reuse exact
  existing pattern)**

```powershell
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
        Write-Error "Required input not found: $required. Run Task 1's pandoc step first."
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
```

- [ ] **Step 2: Add the Site Assets test-folder creation and image upload**

```powershell
$siteAssetsTestFolder = "SiteAssets/TEST-DO-NOT-USE-aspx-experiment"

Write-Host "Ensuring test folder exists: $siteAssetsTestFolder" -ForegroundColor Cyan
Resolve-PnPFolder -SiteRelativePath $siteAssetsTestFolder | Out-Null

Write-Host "Uploading image17.gif and image18.png..." -ForegroundColor Cyan
$uploadedImage17 = Add-PnPFile -Path $image17Path -Folder $siteAssetsTestFolder
$uploadedImage18 = Add-PnPFile -Path $image18Path -Folder $siteAssetsTestFolder

$web = Get-PnPWeb
$image17Url = "$($web.Url)/$($uploadedImage17.ServerRelativeUrl)".Replace($web.Url, "").TrimStart("/")
$image17AbsoluteUrl = "$($web.Url)/$siteAssetsTestFolder/image17.gif"
$image18AbsoluteUrl = "$($web.Url)/$siteAssetsTestFolder/image18.png"

Write-Host "Uploaded image17 to: $image17AbsoluteUrl" -ForegroundColor Green
Write-Host "Uploaded image18 to: $image18AbsoluteUrl" -ForegroundColor Green
```

- [ ] **Step 3: Add the HTML fragment load + image-path rewrite**

```powershell
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
```

- [ ] **Step 4: Manually run the script up to this point and verify no errors**

Run: `pwsh tools/phase-3-sharepoint-discovery/push-aspx-experiment.ps1` (Tasks 3/4's code isn't
written yet, so the script will end after Step 3's output — that's expected at this point in the
plan.)

Expected: connects successfully, uploads both images without error, prints the rewritten HTML
snippet with `https://bcgov.sharepoint.com/...` URLs in place of `../media/...` paths, and no
`../media/` substring remains.

- [ ] **Step 5: Commit**

```bash
git add tools/phase-3-sharepoint-discovery/push-aspx-experiment.ps1
git commit -m "Add PnP script: image upload + HTML path rewrite for aspx experiment"
```

---

### Task 3: Push the raw `.aspx` boundary probe

**Files:**
- Modify: `tools/phase-3-sharepoint-discovery/push-aspx-experiment.ps1` (append to the file
  created in Task 2)
- Create: `tools/phase-3-sharepoint-discovery/aspx-experiment/raw-page.aspx` (the wrapped shell,
  saved locally before upload, for inspection/reproducibility)

**Interfaces:**
- Consumes: `$rewrittenHtml` (string, from Task 2 Step 3).
- Produces: a pushed SharePoint file at `Site Pages/TEST-DO-NOT-USE-raw-initiate-a-file.aspx`,
  and prints its full URL to the console for the user to open in a browser.

- [ ] **Step 1: Write the raw ASPX shell locally**

```powershell
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
```

- [ ] **Step 2: Upload it directly to Site Pages via Add-PnPFile**

```powershell
Write-Host "Uploading raw .aspx file to Site Pages (boundary probe — may or may not render as a page)..." -ForegroundColor Cyan
$uploadedAspx = Add-PnPFile -Path $rawAspxLocalPath -Folder "Site Pages" -NewFileName "TEST-DO-NOT-USE-raw-initiate-a-file.aspx"

$rawAspxUrl = "$($web.Url)/SitePages/TEST-DO-NOT-USE-raw-initiate-a-file.aspx"
Write-Host ""
Write-Host "=== RAW ASPX PROBE PUSHED ===" -ForegroundColor Yellow
Write-Host "Open this URL in your browser and report what you see:" -ForegroundColor Yellow
Write-Host $rawAspxUrl -ForegroundColor Yellow
Write-Host "(Does it render as a page? Download as a raw file? Show an error? Show SharePoint's ""this is an old page"" banner?)" -ForegroundColor Yellow
Write-Host ""
```

- [ ] **Step 3: Run the script and open the printed URL in a browser**

Run: `pwsh tools/phase-3-sharepoint-discovery/push-aspx-experiment.ps1`

Expected: the script prints a `TEST-DO-NOT-USE-raw-initiate-a-file.aspx` URL under `Site Pages`
with no PowerShell errors. Open that URL in a browser and note the actual behavior (this
observation is the evidence for Task 5's findings write-up — there is no "correct" expected
result here, since this is exactly the thing being tested).

- [ ] **Step 4: Commit**

```bash
git add tools/phase-3-sharepoint-discovery/push-aspx-experiment.ps1 tools/phase-3-sharepoint-discovery/aspx-experiment/raw-page.aspx
git commit -m "Add raw .aspx boundary-probe push to aspx experiment script"
```

---

### Task 4: Push the supported modern client-side page

**Files:**
- Modify: `tools/phase-3-sharepoint-discovery/push-aspx-experiment.ps1` (append to the file from
  Tasks 2/3)

**Interfaces:**
- Consumes: `$rewrittenHtml` (string, from Task 2 Step 3), `$web` (from Task 2 Step 2).
- Produces: a pushed, published SharePoint modern page at
  `Site Pages/TEST-DO-NOT-USE-modern-initiate-a-file.aspx` (yes, modern pages are also physically
  `.aspx` files under the hood — the distinction under test is *authoring method*: raw file
  upload in Task 3 vs. the client-side-page API here), printed URL for the user to open.

- [ ] **Step 1: Create the modern page and add the HTML as a Text web part**

```powershell
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
Write-Host "(Do headings and both images render correctly inside the Text web part?)" -ForegroundColor Yellow
Write-Host ""
```

- [ ] **Step 2: Run the full script end-to-end**

Run: `pwsh tools/phase-3-sharepoint-discovery/push-aspx-experiment.ps1`

Expected: no PowerShell errors across the whole script; two URLs printed at the end (the Task 3
raw-aspx URL and this task's modern-page URL). Open both in a browser and note what each one
actually shows — headings/images rendering correctly, partially, or not at all, for each of the
two paths.

- [ ] **Step 3: Commit**

```bash
git add tools/phase-3-sharepoint-discovery/push-aspx-experiment.ps1
git commit -m "Add modern client-side page push to aspx experiment script"
```

---

### Task 5: Log findings and flag docx/pptx as future backlog

**Files:**
- Modify: `docs/research/research-summary-phase3-sharepoint-write-capability-discovery.md` (append a new
  numbered section, `## 15. ASPX / modern-page conversion experiment`, following the existing
  numbering convention — sections 1-14 already exist)

**Interfaces:**
- Consumes: the user's browser observations from Task 3 Step 3 and Task 4 Step 2 (what actually
  rendered for each of the two pushed URLs).
- Produces: no code — a findings section only, following the exact structure already used by
  existing sections (e.g. `## 13. Native Markdown rendering`): a one-line result classification,
  what was tested, what was observed, and what it means for the broader
  `Content + Template + Renderer` vision.

- [ ] **Step 1: Ask the user to report what they saw for both URLs (if not already reported
  during Tasks 3-4), then write the findings section**

Write a new section modeled on this structure (fill in the actual `[OBSERVED: ...]` placeholders
with the user's real browser observations — do not guess or invent an outcome):

```markdown
## 15. ASPX / modern-page conversion experiment — testing SharePoint as a multi-format Renderer target

**Motivation:** this repo's own stated vision is `Content + Template + Renderer = Published
Output` — a single canonical Markdown source rendered to multiple output formats. This probe
tests whether SharePoint itself can be one such Renderer target, using a real CEIS manual topic
(`initiate-a-file--51d1f554.md`, 4 headings, 2 images) converted via pandoc.

**Raw `.aspx` file upload (boundary probe, unsupported path):**
`Add-PnPFile` uploading a hand-wrapped `.aspx` shell directly into Site Pages.
**Result:** [OBSERVED: fill in — rendered as a working page / downloaded as a raw file / showed
an error / showed a legacy-page banner, etc. — exactly what the user saw when opening the URL]

**Modern client-side page (supported path):**
`Add-PnPPage` + `Add-PnPPageTextPart` + `Set-PnPPage -Publish`, using the same pandoc HTML.
**Result:** [OBSERVED: fill in — did headings and both images render correctly inside the Text
web part?]

**Classification:** [CONFIRMED_TENANT_OBSERVATION — this tested tenant/site/permission profile
only, consistent with the "Scope corrections" section above; not a universal SharePoint claim]

**Implication for the multi-format vision:** [fill in based on the two results above — e.g. if
the modern-page route worked cleanly, SharePoint modern pages are a viable Renderer target
alongside the existing Markdown renderer, with the caveat that image assets need their own
upload/rewrite step, not a drop-in file copy; if the raw-aspx route also worked, that's an
additional/alternate path worth noting; if either failed, note exactly what failed and why]

**Explicitly out of scope for this probe (flagged for future backlog, per user's decision not
to expand this experiment):** generating `.docx` and `.pptx` from the same source via pandoc was
considered but deliberately deferred — pandoc already supports both formats natively from
Markdown input, so this would be a cheap follow-up test once someone wants to pursue it,
following the same `docs/superpowers/plans/2026-07-29-aspx-modern-page-experiment.md` script
pattern (swap the `-t html` pandoc invocation for `-t docx` or a reveal.js/pptx target).
```

- [ ] **Step 2: Commit**

```bash
git add docs/research/research-summary-phase3-sharepoint-write-capability-discovery.md
git commit -m "Log ASPX/modern-page experiment results in write-exploration-findings.md"
```

- [ ] **Step 3: Clean up the test artifacts per the staged-write protocol (only after the user
  confirms they're done inspecting both pushed pages)**

Ask the user first — do not delete without confirmation, since they may want to keep inspecting.
Once confirmed, remove via PnP:

```powershell
Remove-PnPFile -ServerRelativeUrl "$($web.ServerRelativeUrl)/SitePages/TEST-DO-NOT-USE-raw-initiate-a-file.aspx" -Force
Remove-PnPPage -Identity "TEST-DO-NOT-USE-modern-initiate-a-file"
Remove-PnPFolder -Name "TEST-DO-NOT-USE-aspx-experiment" -Folder "SiteAssets" -Force
```

- [ ] **Step 4: Push the final commit to GitHub**

```bash
git push origin main
```
