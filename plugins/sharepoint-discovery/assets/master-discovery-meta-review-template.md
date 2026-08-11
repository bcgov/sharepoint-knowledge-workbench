# Master Discovery Meta-Review & Modernization Readiness Catalog — {{SITE_NAME}}

> **Generated:** {{DATE}}  
> **Target Site:** {{SITE_NAME}}  
> **Source Site URL:** `{{SITE_URL}}`  
> **Total ASPX Pages Downloaded:** {{TOTAL_PAGES}}  
> **Total Web Part Instances Discovered:** {{TOTAL_WPS}}  
> **Unique Web Part Functional Groups:** {{UNIQUE_WP_GROUPS}}  
> **Flagged Legacy Links Across 7 Surfaces:** {{FLAGGED_LINKS}}  
> **Site Collection Groups & Principals:** {{TOTAL_GROUPS}}  
> **Custom Form Overrides:** {{CUSTOM_FORMS}}  
> **Global & Quick Launch Navigation Nodes:** {{TOTAL_NAV_NODES}}  

---

## 1. Executive Summary & Site Complexity Profile

This document provides the consolidated **Master Discovery Meta-Review Pass** synthesizing all 13 technical discovery domains for **{{SITE_NAME}}**.

### Site Modernization Complexity Assessment: **{{COMPLEXITY_RATING}}**

- 🟢 **OOB Standard Pages**: {{OOB_PAGES}} pages require simple layout translation.
- 🟡 **Custom Layout / Web Part Canvas Pages**: {{CUSTOM_PAGES}} pages require modern canvas layout reconstruction.
- 🔴 **Complex Script / SPFx Candidates**: {{SPFX_CANDIDATES}} custom code groups require SPFx web part or Application Customizer development.

---

## 2. Consolidated 13-Domain Technical Discovery Summary Matrix

| Domain # | Discovery Domain Area | Target Output Deliverable | Findings & Key Metrics | Risk Level | Target SPO Architectural Replacement |
|---|---|---|---|---|---|
| **1** | **ASPX Page Inventory** | `aspx-page-summary.md` | {{TOTAL_PAGES}} pages across {{SUBWEB_COUNT}} subwebs | 🟢 Low | Modern Canvas Pages |
| **2** | **Live Web Part Scan** | `legacy_webparts_scan_results.csv` | {{TOTAL_WPS}} DB-stored web part GUIDs | 🟡 Medium | Modern Page Canvas |
| **3** | **Web Part Content Extraction**| `webpart_content_extract.json` | 100% payload extraction verified | 🟢 Low | Standard & SPFx Web Parts |
| **4** | **Web Part Pre-Clustering** | `webpart-code-groups.json` | {{UNIQUE_WP_GROUPS}} functional code groups | 🟡 Medium | Consolidated SPFx / Text WPs |
| **5** | **Deep Web Part Catalog** | `ALL-UNIQUE-WEBPART-CODE-FOR-REVIEW.md` | Deep architectural reviews complete | 🔴 High | Custom SPFx Solutions |
| **6** | **Standard Report Suite** | `<SITE>-MODERNIZATION-VARIANCE-ANALYSIS.md` | 7 core discovery reports compiled | 🟢 Low | Strategic Migration Roadmap |
| **7** | **Site Navigation & Chrome** | `SITE-NAVIGATION-CHROME-SUMMARY.md` | {{TOTAL_NAV_NODES}} navigation nodes | 🟢 Low | SPO Hub & Left Navigation |
| **8** | **Custom Form Overrides** | `CUSTOM-FORMS-INVENTORY-REPORT.md` | {{CUSTOM_FORMS}} custom form overrides | 🟢 Low | Standard SPO Modern Lists |
| **9** | **Dual-Layer ASPX Layouts** | `aspx-content-plan.md` | Layer 1 DOM + Layer 2 Zones mapped | 🟡 Medium | Modern Section Layouts |
| **10** | **Security & Permissions** | `SPO-GROUP-PROVISIONING-CHECKLIST.md` | {{TOTAL_GROUPS}} groups/principals cataloged | 🔴 High | Entra ID Security Groups |
| **11** | **Legacy Link Surfaces** | `ALL-UNIQUE-LINKS-FOR-REVIEW.md` | {{FLAGGED_LINKS}} legacy links flagged | 🔴 High | Automated URL Rewriting |
| **12** | **Custom List Forms** | `CUSTOM-FORMS-INVENTORY-REPORT.md` | {{CUSTOM_FORMS_COMPAT_NOTE}} | 🟢 Low | Native SPO List Views |
| **13** | **Navigation Architecture** | `SITE-NAVIGATION-CHROME-SUMMARY.md` | Master page chrome references mapped | 🟢 Low | Modern Site Header/Footer |

---

## 3. High-Risk Architectural Vulnerabilities & Mitigation Strategy

### A. Individual User Account ACE Direct Assignments
- ⚠️ **Issue**: {{DIRECT_USER_ACE_COUNT}} individual user accounts hold direct permissions across subwebs.
- 💡 **Mitigation**: Do NOT replicate direct user ACEs in SPO. Encapsulate into Entra ID M365 security groups.

### B. Legacy On-Premises Absolute Hostname Hardcoding
- ⚠️ **Issue**: {{HARDCODED_URL_COUNT}} absolute page URLs hardcode the on-prem hostname.
- 💡 **Mitigation**: Run this repo's link-remediation tooling (see `sharepoint-link-remediation` plugin) during publishing waves to auto-rewrite hostnames to the target SPO tenant URLs.

---

## 4. Final Handoff Readiness Checklist for Migration Waves

- [ ] **Page Sources Downloaded**: {{TOTAL_PAGES}} ASPX pages ready for page layout parsing.
- [ ] **Web Parts Inventory Verified**: Inventory drift between scan and extraction confirmed/resolved.
- [ ] **Security Checklist Formulated**: Entra ID group mapping matrix ready for Wave 0 provisioning.
- [ ] **Link Rewriting Rules Established**: Hostname replacement matrix ready for publishing automation.
