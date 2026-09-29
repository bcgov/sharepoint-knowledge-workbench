# Script Editor Code Extraction — Critical Pages Requiring Analysis

**Goal**: Extract and document the JavaScript code from 3 Script Editor web parts on case list edit forms  
**Scope**: SP2016 CMAT (Test or Prod)  
**Status**: Pending extraction — code not yet analyzed

> **UPDATE (2026-07-15)**: A script now exists to do this automatically —
> `plugins/sharepoint-migration/scripts/page-migration/extract-webpart-content.ps1`.
> It reads `legacy_webparts_scan_results.csv`, re-queries the live Web Part Manager API
> for every page/WebPartId pair, and pulls the full untruncated `Content` property for
> all 119 CEWP/SEWP web parts (including the 3 Script Editors below). Run it instead of
> the manual Option A/B/C approaches documented here — those are kept below for reference
> only. See [PROBLEMATIC-WEBPARTS-SUMMARY.md](./PROBLEMATIC-WEBPARTS-SUMMARY.md) → "Tooling"
> section for full usage and output details.

---

## Critical Script Editors (3 Total)

All 3 Script Editors are on **case list EditForm.aspx** pages. These are form customizations that contain custom JavaScript logic.

### Page 1: PIO_Cases/EditForm.aspx
- **Web Part Title**: Script Editor
- **Web Part ID**: `b7573f07-4bdd-449a-ba1b-4615f5f329d1`
- **URL**: `https://itau.test.jag.gov.bc.ca/cmat/Lists/PIO_Cases/EditForm.aspx`
- **Status**: 🔴 Code NOT YET EXTRACTED

### Page 2: ITAU_Cases/EditForm.aspx
- **Web Part Title**: Script Editor
- **Web Part ID**: `b9a499e8-db7f-4c48-a5a8-8aa4f059c438`
- **URL**: `https://itau.test.jag.gov.bc.ca/cmat/Lists/ITAU_Cases/EditForm.aspx`
- **Status**: 🔴 Code NOT YET EXTRACTED

### Page 3: ICM_Cases/EditForm.aspx
- **Web Part Title**: Script Editor
- **Web Part ID**: `6b043258-3cc3-42be-a618-3df278d84c5c`
- **URL**: `https://itau.test.jag.gov.bc.ca/cmat/Lists/ICM_Cases/EditForm.aspx`
- **Status**: 🔴 Code NOT YET EXTRACTED

---

## How to Extract Script Editor Code

### Option A: Manual Inspection (Quick, one-time)

1. **Connect to SP2016 Test** (VPN required)
2. **Navigate to the page**, e.g., `https://itau.test.jag.gov.bc.ca/cmat/Lists/PIO_Cases/EditForm.aspx`
3. **Edit the page** (Site Actions → Edit Page, or if using modern: Edit in classic mode)
4. **Click on the Script Editor web part**
5. **Select "Edit in Web Part"** or **right-click → Web Part Properties**
6. **In the "Content" field**: Copy the entire JavaScript code
7. **Paste into a text file** named `script-editor-{list-name}.js` for later analysis
8. **Document what it does** (validation, auto-fill, filtering, etc.)

### Option B: Automated Extraction (PowerShell)

Use PnP.PowerShell to extract all web part properties including content:

```powershell
# Connect to SP2016 site
$siteUrl = "https://itau.test.jag.gov.bc.ca/cmat"
Connect-PnPOnline -Url $siteUrl -UseWebLogin

# Define target pages
$pages = @(
    "Lists/PIO_Cases/EditForm.aspx",
    "Lists/ITAU_Cases/EditForm.aspx",
    "Lists/ICM_Cases/EditForm.aspx"
)

# Extract Script Editor web parts
foreach ($page in $pages) {
    Write-Host "Extracting from: $page" -ForegroundColor Cyan
    
    $file = Get-PnPFile -Url "/cmat/$page" -AsListItem
    $webparts = Get-PnPWebPart -ServerRelativeUrl "/cmat/$page"
    
    foreach ($wp in $webparts | Where-Object { $_.WebPart.TypeName -eq "Microsoft.SharePoint.WebPartPages.ScriptEditorWebPart" }) {
        Write-Host "  Script Editor: $($wp.Title)" -ForegroundColor Yellow
        Write-Host "  ID: $($wp.Id)"
        Write-Host "  Properties XML:" -ForegroundColor Green
        
        # Extract the 'Content' property
        $wpProperties = $wp.WebPart.Properties
        if ($wpProperties -and $wpProperties.Content) {
            Write-Host $wpProperties.Content
            
            # Save to file
            $outputFile = "script-editor-$(($page -split '/')[1]).js"
            $wpProperties.Content | Out-File $outputFile -Encoding UTF8
            Write-Host "  Saved to: $outputFile"
        }
    }
}
```

### Option C: Direct REST API Call

Query the SharePoint REST API directly:

```powershell
# For each page, call the Web Part Manager API
$pageUrl = "/cmat/Lists/PIO_Cases/EditForm.aspx"
$restUrl = "https://itau.test.jag.gov.bc.ca/cmat/_api/web/GetFileByServerRelativeUrl('$pageUrl')/GetLimitedWebPartManager(scope=1)/WebParts?`$expand=WebPart"

Invoke-RestMethod -Uri $restUrl -UseDefaultCredentials -Headers @{ "Accept" = "application/json" }
```

The response will include the full web part XML with the JavaScript code embedded.

---

## What to Look For in Script Editor Code

Once extracted, analyze each Script Editor for:

### 1. **Type of Logic**
- [ ] Form validation (checking field values, preventing save)
- [ ] Auto-fill / cascading dropdowns
- [ ] Field show/hide based on conditions
- [ ] External API calls (AJAX to REST endpoints)
- [ ] Custom event handlers
- [ ] UI styling/CSS injection

### 2. **Dependencies**
- [ ] Uses jQuery? (If so, which version?)
- [ ] Uses external libraries? (moment.js, d3, etc.)
- [ ] Calls ORDS endpoints?
- [ ] Calls other SharePoint lists?
- [ ] Hard-coded values or configuration?

### 3. **Complexity**
- **Simple** (< 50 lines): Validation, show/hide logic → Can rebuild in Power Apps
- **Medium** (50–200 lines): Cascading dropdowns, auto-fill → Can rebuild in Power Apps + Power Fx
- **Complex** (> 200 lines): Custom data transformations, external integrations → Requires SPFx custom form customizer

---

## Modernization Path

Once code is extracted and analyzed:

### **Power Apps Form** (Recommended for most cases)
- Rebuild form in Power Apps with same fields + layout
- Replicate validation using Power Fx formulas
- Replicate auto-fill using gallery controls or lookup fields
- Deploy as modern list form replacement
- **Effort**: Small–Medium (1–3 days per form)
- **Risk**: Low

### **Modern SharePoint Form + Power Automate** (Alternative)
- Use OOB modern list form
- Recreate conditional visibility using modern form customizations (if supported)
- Use Power Automate for complex logic (if needed)
- **Effort**: Medium (2–5 days)
- **Risk**: Medium (limited customization options)

### **SPFx Custom Form Customizer** (If complex logic required)
- Build custom React component for form
- Full control over JavaScript and styling
- **Effort**: Large (5–10 days)
- **Risk**: Medium (custom code, maintenance burden)

---

## Extraction Checklist

- [ ] **PIO_Cases/EditForm.aspx** — Extract code, document logic, classify complexity
- [ ] **ITAU_Cases/EditForm.aspx** — Extract code, document logic, classify complexity
- [ ] **ICM_Cases/EditForm.aspx** — Extract code, document logic, classify complexity
- [ ] **Create per-form modernization plan** based on complexity
- [ ] **Update ASPX-MODERNIZATION-STRATEGY.md** with findings

---

## Next Steps

1. **Choose extraction method** (Manual / PowerShell / REST API)
2. **Run extraction against SP2016 Test** (safer than Prod initially)
3. **Document code + complexity** for each Script Editor
4. **Create modernization specs** for each form
5. **Prioritize Power Apps rebuilds** by complexity

---

*Document created: 2026-07-15*  
*Ready for code extraction when VPN/access available*
