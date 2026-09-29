# Master Web Part Code Review Catalog — {{SITE_NAME}}

> **Generated:** {{DATE}}  
> **Target Site:** {{SITE_NAME}}  
> **Total Web Parts Analyzed:** {{TOTAL_INSTANCE_COUNT}}  
> **Unique Functional Code Groups:** {{UNIQUE_GROUP_COUNT}}  

---

## Executive Summary of Code Analysis Pass

This document provides a deep architectural and behavioral code analysis for every unique custom web part group discovered on the **{{SITE_NAME}}** site.

Groups were established by clustering identical inline JavaScript logic, external helper script references (`<script src="...">`), CSS styling, and HTML markup. Each group is analyzed below for business behavior, presentation vs. access enforcement, and modern SPO replacement path.

---

## Master Group Analysis Catalog

<!-- Repeat the block below for each unique functional group (Group 1 to Group N) -->

## Group {{GROUP_INDEX}} — {{GROUP_NAME}} ({{INSTANCE_COUNT}} instances)

**Representative Page:** `{{REPRESENTATIVE_PAGE_URL}}` (WebPartId `{{REPRESENTATIVE_WEBPART_ID}}`)  
**All Affected Pages:**
{{AFFECTED_PAGES_LIST}}

### Code / Content Snippet
```html
{{CODE_SNIPPET}}
```

### Modernization Assessment
- **Business behavior:** {{BUSINESS_BEHAVIOR_DESCRIPTION}}
- **Text web part sufficient:** {{TEXT_WEBPART_SUFFICIENT_YES_NO}}
- **Recommended modern replacement:** {{RECOMMENDED_MODERN_REPLACEMENT}}
- **MVP decision:** {{MVP_DECISION_SIMPLIFY_PORT_DROP}}
- **SPFx candidate:** {{SPFX_CANDIDATE_YES_NO_CONDITIONAL}}
- **Validation required:** {{VALIDATION_REQUIRED_QUESTION}}

### Modernization Behaviour Analysis

#### User-visible effect
{{USER_VISIBLE_EFFECT}}

#### Business intent
{{BUSINESS_INTENT}}

#### Actual enforcement level
{{ACTUAL_ENFORCEMENT_LEVEL}}

#### Modern SharePoint Online approach
{{MODERN_SPO_APPROACH}}

#### SPFx assessment
{{SPFX_ASSESSMENT}}

#### Modern Script Editor (PnP SPFx) Evaluation
{{MODERN_SCRIPT_EDITOR_EVALUATION}}

#### Migration note
{{MIGRATION_NOTE}}

---
