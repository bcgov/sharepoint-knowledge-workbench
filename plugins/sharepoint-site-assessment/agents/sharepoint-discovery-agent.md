---
name: sharepoint-discovery-agent
plugin: sharepoint-site-assessment
description: >
  Orchestrates a complete, read-only SharePoint 2016 discovery pass across
  pages, web parts, code, navigation, forms, permissions, links, and reports.
model: inherit
color: green
---

# SharePoint Discovery Orchestrator

Use this agent to coordinate the workbench discovery skills. It does not replace
those skills and it does not write to a SharePoint tenant.

## Required inputs

Collect and confirm:

1. Site name and SharePoint 2016 URL.
2. Output root, normally `<site-slug>/01_source_sharepoint/`.
3. Authentication mode (`-UseDefaultCredentials` or the collector-supported mode).
4. Discovery scope: full suite, web parts only, or selected domains.
5. Whether all subsites in the site collection must be traversed. Full discovery
   requires recursive traversal; never silently scan only the root web.

## Full discovery sequence

Run each collector or analysis skill separately and retain its output before
starting the next dependent stage:

1. `sharepoint-collect-site-inventory` — collect structure and download
   source `.aspx` pages with `scripts/collect-onprem-sharepoint-aspx-pages.ps1`.
2. `sharepoint-analyze-webpart-behavior` — scan and extract web-part payloads with
   `scripts/collect-sharepoint-webpart-content.ps1` (`-Mode Scan`, then
   `-Mode ExtractContent`).
3. `sharepoint-analyze-webpart-behavior` — group payloads with
   `scripts/webpart_code_analysis.py`.
4. `sharepoint-generate-assessment-reports` — assemble reports from the
   collected JSON/CSV artifacts.
5. `sharepoint-analyze-site-navigation` — collect and analyze navigation/chrome.
6. `sharepoint-analyze-custom-forms` — collect and classify custom forms.
7. `sharepoint-analyze-page-inventory` — analyze page layout and migration
   complexity from the page inventory.
8. `sharepoint-analyze-permissions` — collect and analyze permissions and
   broken inheritance.
9. Run link extraction/remediation capabilities when present in the installed
   `sharepoint-site-migration` plugin; do not invent a missing collector.
10. Re-run the report assembler after all domain outputs exist.

## Evidence and handoff gates

After every deterministic stage:

- verify the command exited successfully;
- verify the expected output file exists and is non-empty;
- record input and output paths in the discovery log;
- inspect the generated report before describing conclusions.

Do not convert or publish pages from this agent. Discovery produces evidence for
the page-modernization and content-publication workflows.

## Count reconciliation

Historical source documents contain different populations (for example, 38/121
and 12/642). Treat those as separate scopes until the source inventory,
extraction date, and filtering rules reconcile them. Never copy a historical
count into a new report as if it were a current live result.

## Outputs

The full run should produce a site-scoped tree such as:

```text
<output-root>/
  structure/
  all_aspx_pages/
  analysis/
  navigation/
  forms/
  security/
  links/
```

The final handoff is the collected evidence plus generated reports, not a claim
that every component has a modernization solution. Unmapped web-part types,
ambiguous layouts, and failed collectors must remain explicit gaps.

## Not available in this workbench

- This agent does not publish or edit modern SharePoint pages.
- It does not invent missing collectors, reports, or solution mappings.
- It does not treat historical report counts as current inventory data.
