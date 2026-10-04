# Discovery lineage migration manifest

This manifest records what was carried forward from the originating
`sharepoint-migration` plugin and what was already represented by generalized
workbench capabilities.

## Added because missing

- `agents/sharepoint-discovery-agent.md` — adapted full-suite orchestrator.
- `references/webpart-analysis-runbook.md` — adapted web-part lineage and
  modernization handoff.
- `scripts/discovery-lineage/` — source analysis/report scripts that were not
  present in the workbench, kept together as a traceable compatibility set.

## Already represented by generalized workbench capabilities

These source capabilities were not duplicated:

| Source capability | Workbench replacement |
| --- | --- |
| ASPX page extraction | `sharepoint-collect-site-inventory` |
| Web-part scan and payload extraction | `sharepoint-analyze-webpart-behavior` |
| Web-part grouping | `sharepoint-analyze-webpart-behavior` |
| Navigation collection and analysis | `sharepoint-analyze-site-navigation` |
| Custom-form collection and analysis | `sharepoint-analyze-custom-forms` |
| Permissions collection and analysis | `sharepoint-analyze-permissions` |
| Page inventory analysis | `sharepoint-analyze-page-inventory` |
| Discovery report assembly | `sharepoint-generate-assessment-reports` |
| Schema/site-structure collection | `sharepoint-collect-site-inventory` |

## Deliberately excluded

- Source logs, caches, generated outputs, and compiled bytecode.
- Site-specific configuration files containing URLs or credentials.
- Unrelated migration, deployment, calendar, and content-audit scripts.
- Duplicate collector implementations where the workbench replacement is
  generalized and tested.

Historical reports remain evidence and must not be treated as current
inventory data or as a complete solution-mapping registry.
