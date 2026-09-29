# Unique Pages & Web Parts Requiring Analysis

**Source**: legacy_webparts_scan_results.csv (119 web parts across 49 unique ASPX pages)  
**Date**: 2026-07-15

---

## Summary

| Category | Count | Action Required |
|----------|-------|---|
| **TOTAL Unique Pages** | 49 | Various (see below) |
| **Pages with Script Editors** | 3 | 🔴 CRITICAL — Extract & analyze code |
| **Pages with Content Editors** | 46 | 🟡 MEDIUM — Inspect content |
| **TOTAL Web Parts** | 119 | Various (see below) |
| **Script Editor Web Parts** | 3 | 🔴 CRITICAL — Analyze JavaScript |
| **Content Editor Web Parts** | 116 | 🟡 MEDIUM — Most trivial, categorize |

---

## 1. Unique ASPX Pages Requiring Analysis (49 Total)

### A. CRITICAL PRIORITY: Pages with Script Editors (3 pages)

| Page Name | Full URL | Web Parts | Priority |
|-----------|----------|-----------|----------|
| `PIO_Cases/EditForm.aspx` | `/cmat/Lists/PIO_Cases/EditForm.aspx` | 1 Script Editor | 🔴 CRITICAL |
| `ITAU_Cases/EditForm.aspx` | `/cmat/Lists/ITAU_Cases/EditForm.aspx` | 1 Script Editor | 🔴 CRITICAL |
| `ICM_Cases/EditForm.aspx` | `/cmat/Lists/ICM_Cases/EditForm.aspx` | 1 Script Editor | 🔴 CRITICAL |

**Action**: Extract JavaScript code; document logic; plan Power Apps rebuild  
**Reference**: [SCRIPT-EDITOR-CODE-EXTRACTION.md](./SCRIPT-EDITOR-CODE-EXTRACTION.md)

---

### B. HIGH PRIORITY: Complex Dashboard Pages with Multiple Content Editors (13 pages)

Pages with 2+ Content Editors that likely contain instruction banners or styling on high-traffic dashboards:

| Page Name | Full URL | CEWP Count | Notable for |
|-----------|----------|-----------|---|
| `My_ITAU_Cases.aspx` | `/cmat/Pages/My_ITAU_Cases.aspx` | 4 | Analyst daily-use dashboard; 14 LVWPs |
| `ITAU_Cases.aspx` | `/cmat/Pages/ITAU_Cases.aspx` | 4 | All-cases view; 14 LVWPs |
| `ITAU_All_Approval_Requests.aspx` | `/cmat/Pages/ITAU_All_Approval_Requests.aspx` | 4 | Cross-section approval dashboard |
| `ITAU_My_Approval_Requests.aspx` | `/cmat/Pages/ITAU_My_Approval_Requests.aspx` | 5 | My approvals view |
| `My_ICM_Cases.aspx` | `/cmat/Pages/My_ICM_Cases.aspx` | 2 | ICM analyst view; 14 LVWPs |
| `ICM_Cases.aspx` | `/cmat/Pages/ICM_Cases.aspx` | 2 | All ICM cases; 14 LVWPs |
| `ICM_All_Approval_Requests.aspx` | `/cmat/Pages/ICM_All_Approval_Requests.aspx` | 5 | Cross-section approval queue |
| `ICM_My_Approval_Requests.aspx` | `/cmat/Pages/ICM_My_Approval_Requests.aspx` | 5 | My ICM approvals |
| `ICM_My_Tasks.aspx` | `/cmat/Pages/ICM_My_Tasks.aspx` | 4 | ICM task dashboard |
| `ICM_All_Tasks.aspx` | `/cmat/Pages/ICM_All_Tasks.aspx` | 3 | All ICM tasks |
| `My_PIO_Cases.aspx` | `/cmat/Pages/My_PIO_Cases.aspx` | 3 | PIO analyst view; 14 LVWPs |
| `PIO_Cases.aspx` | `/cmat/Pages/PIO_Cases.aspx` | 3 | All PIO cases; 14 LVWPs |
| `Persons_ICM.aspx` | `/cmat/Pages/Persons_ICM.aspx` | 2 | Person detail (most complex page; ~40 LVWPs) |
| `Persons_ITAU.aspx` | `/cmat/Pages/Persons_ITAU.aspx` | 2 | Person detail ITAU view; ~30 LVWPs |
| `Persons_PIO.aspx` | `/cmat/Pages/Persons_PIO.aspx` | 2 | Person detail PIO view; ~30 LVWPs |
| `portal.aspx` | `/cmat/Pages/portal.aspx` | 1 | Homepage/dashboard |

**Action**: Inspect content; assume mostly banners/instructions; migrate to modern rich text  
**Effort**: Low–Medium (mostly copy-paste, no code)

---

### C. MEDIUM PRIORITY: List Form Pages with Content Editors (20 pages)

Standard OOB list form pages (New/Edit/Disp) with Content Editors (likely instruction text):

| Page Name | List | Form Type |
|-----------|------|-----------|
| `PIO_Cases/DispForm.aspx` | PIO_Cases | Display |
| `ICM_Case_Tasks/NewForm.aspx` | ICM_Case_Tasks | New |
| `ICM_Approval_Requests/NewForm.aspx` | ICM_Approval_Requests | New |
| `PIO_Approval_Requests/NewForm.aspx` | PIO_Approval_Requests | New |
| `PIO_Approval_Requests/DispForm.aspx` | PIO_Approval_Requests | Display |
| `PIO_Approval_Requests/PIO_Approval_Requests_Mgrs.aspx` | PIO_Approval_Requests | Custom |
| `ITAU_Case_Tasks/AllItems.aspx` | ITAU_Case_Tasks | List view |
| `ITAU_Case_Tasks/NewForm.aspx` | ITAU_Case_Tasks | New |
| `ITAU_Narratives/NewForm.aspx` | ITAU_Narratives | New |
| `PIOs_Narrative/NewForm.aspx` | PIOs_Narrative | New |
| `PIO_Log_Entries/NewForm.aspx` | PIO_Log_Entries | New |
| `PIO_Log_Entries/DispForm.aspx` | PIO_Log_Entries | Display |
| `Persons/DispForm.aspx` | Persons | Display |
| `ICM_Narratives/NewForm.aspx` | ICM_Narratives | New |
| `PIO_Case_Tasks/NewForm.aspx` | PIO_Case_Tasks | New |
| `ITAU_Log_Entries/NewForm.aspx` | ITAU_Log_Entries | New |
| `ICM_Log_Entries/NewForm.aspx` | ICM_Log_Entries | New |
| `Briefings/DispForm.aspx` | Briefings | Display |
| `ITAU_Cal_Abbotsford/DispForm.aspx` | ITAU_Cal_Abbotsford | Display |
| `Security_Alerts/DispForm.aspx` | Security_Alerts | Display |
| `ITAU_Approval_Requests/NewForm.aspx` | ITAU_Approval_Requests | New |

**Action**: Replace with form header instructions; no code changes needed  
**Effort**: Very Low (mostly copy-paste)

---

### D. MEDIUM PRIORITY: Other Publishing Pages (13 pages)

| Page Name | CEWP Count |
|-----------|-----------|
| `Add_Edit_Persons.aspx` | 2 |
| `All_Persons.aspx` | 2 |
| `All_Appearances.aspx` | 1 |
| `All_Cases.aspx` | 1 |
| `All_Case_Documents.aspx` | 1 |
| `all_progress_logs.aspx` | 1 |
| `All_Tasks.aspx` | 1 |
| `Appearing_Persons_Briefing.aspx` | 1 |
| `All_Approval_Requests.aspx` | 1 |
| `All_Briefings_and_Security_Alerts.aspx` | 1 |
| `Briefings_and_Security_Alerts.aspx` | 2 |
| `ICM_Documents.aspx` | 1 |
| `ITAU_Documents.aspx` | 1 |
| `Manage_Reference_and_Templates.aspx` | 1 |
| `Manage_Security_Alerts.aspx` | 2 |
| `PIO_All_Approval_Requests.aspx` | 2 |
| `PIO_All_Tasks.aspx` | 2 |
| `PIO_Documents.aspx` | 1 |
| `PIO_My_Approval_Requests.aspx` | 3 |
| `PIO_My_Tasks.aspx` | 3 |

**Action**: Inspect; assume trivial; migrate to modern pages  
**Effort**: Low

---

### E. LOW PRIORITY: Admin/Data Quality Pages (4 pages)

| Page Name | CEWP Count | Purpose |
|-----------|-----------|---------|
| `Orphan_Appearances.aspx` | 1 | Show unmatched appearance records |
| `Orphan_Approval_Requests.aspx` | 1 | Show orphaned approvals |
| `Orphan_Progress_Logs.aspx` | 1 | Show orphaned log entries |
| `Orphan_Tasks.aspx` | 1 | Show orphaned tasks |

**Action**: May be decommissioned or rebuilt as admin dashboard  
**Effort**: Very Low (admin-only pages; not frequently used)

---

## 2. Unique Web Parts Requiring Analysis (3 Unique Types)

### A. Script Editor Web Parts (3 instances, 3 unique)

**CRITICAL — Contains actual code that must be extracted and rebuilt**

| Web Part ID | Page | Analysis Status |
|------------|------|---|
| `b7573f07-4bdd-449a-ba1b-4615f5f329d1` | PIO_Cases/EditForm.aspx | 🔴 NOT EXTRACTED |
| `b9a499e8-db7f-4c48-a5a8-8aa4f059c438` | ITAU_Cases/EditForm.aspx | 🔴 NOT EXTRACTED |
| `6b043258-3cc3-42be-a618-3df278d84c5c` | ICM_Cases/EditForm.aspx | 🔴 NOT EXTRACTED |

**Required Actions**:
1. Extract JavaScript code from each web part (see [SCRIPT-EDITOR-CODE-EXTRACTION.md](./SCRIPT-EDITOR-CODE-EXTRACTION.md))
2. Analyze what the code does (validation, auto-fill, filtering, etc.)
3. Determine if it's essential or can be simplified
4. Plan Power Apps form rebuild with equivalent logic
5. Test modernized form

**Reference**: [SCRIPT-EDITOR-CODE-EXTRACTION.md](./SCRIPT-EDITOR-CODE-EXTRACTION.md)

---

### B. Content Editor Web Parts (116 instances, 1 unique type)

**MEDIUM — Mostly trivial rich text; some may have embedded CSS**

| Type | Count | Expected Content | Effort to Replace |
|------|-------|---|---|
| Instruction banners | ~80 | Text instructions ("Note: when adding...") | Very Low |
| Styled containers | ~20 | HTML/CSS for layout/styling | Low |
| Images/logos | ~10 | Embedded images or styling | Low |
| Unknown | ~6 | TBD (needs inspection) | Medium |

**Analysis Approach**:
- **Fast-path**: Assume trivial unless inspection reveals complexity
- **Sample inspection**: Check 5–10 high-traffic pages (My_ITAU_Cases, Persons_ICM, etc.) to validate assumption
- **Bulk migration**: Copy trivial content to modern rich text or form headers

**Reference**: [PROBLEMATIC-WEBPARTS-SUMMARY.md](./PROBLEMATIC-WEBPARTS-SUMMARY.md) Section 2

---

## 3. Unique Analysis Categories

| Category | Count | Action | Effort | Risk |
|----------|-------|--------|--------|------|
| **Script Editors** | 3 | Extract code, plan rebuild | Medium | High |
| **Content Editors (Trivial)** | ~110 | Migrate as-is to modern UI | Very Low | Low |
| **Content Editors (Complex)** | ~6 | Inspect, plan modernization | Low–Medium | Low–Medium |

---

## Summary Matrix: Pages vs. Web Parts

```
49 Unique Pages
├─ 3 with Script Editors (CRITICAL)
├─ 46 with Content Editors only (MEDIUM)
└─ 0 with both (all Script Editors are on separate list forms)

119 Total Web Parts
├─ 3 Script Editors (on 3 unique pages)
└─ 116 Content Editors (on 46 unique pages)
   ├─ 24 on list forms (New/Edit/Disp)
   ├─ 1 on list view
   └─ 91 on publishing/site pages
```

---

## Next Steps

### Immediate (This Week)
- [ ] **Review this analysis** with CMAT team
- [ ] **Prioritize pages** based on usage (high-traffic first: My_*_Cases, Persons_*, case approvals)

### Short-term (Next 1–2 Weeks)
- [ ] **Extract Script Editor code** from 3 case list forms (see SCRIPT-EDITOR-CODE-EXTRACTION.md)
- [ ] **Sample-inspect** 5–10 high-priority Content Editors to validate "mostly trivial" assumption
- [ ] **Create Power Apps form modernization specs** for each case list (PIO, ITAU, ICM)

### Medium-term (Weeks 3–4)
- [ ] **Build Power Apps forms** for case lists (replacement for list EditForms with Script Editors)
- [ ] **Bulk migrate trivial Content Editors** to modern page banners/headers
- [ ] **Deploy modern pages** to DEV/TEST in parallel with SP2016 legacy pages

### Long-term (Pre-PROD cutover)
- [ ] **User acceptance testing** (modern pages vs. legacy side-by-side)
- [ ] **Finalize remaining complex page modernizations**
- [ ] **Cutover plan** (when to switch users from legacy to modern)

---

*Analysis completed: 2026-07-15*  
*Based on legacy_webparts_scan_results.csv (119 web parts, 49 unique pages)*  
*Cross-referenced with live-webpart-scan.md and legacy_webparts_summary.md*
