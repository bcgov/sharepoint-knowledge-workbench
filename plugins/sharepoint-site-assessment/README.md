# sharepoint-site-assessment

Collection and analysis of classic/modern SharePoint site inventories:
per-page migration complexity scoring, functional grouping of web-part code,
site navigation depth analysis, custom-form classification, and permissions
auditing -- each backed by a real, read-only PnP.PowerShell (modern SPO) or
NTLM/REST (legacy on-prem SP2016) collector, plus a real managed-metadata
auditor, on-prem schema-drift diagnostic, and discovery report-set generator.

**Read-only, but not zero tenant I/O.** The Python analysis modules
(`*_analysis.py`) make no writes and no network access -- they read an
export you already have. The `.ps1` collectors (`collect-*.ps1`,
`audit-*.ps1`, `generate-*.ps1`) do connect to a live site to produce that
export, but only ever call `Get-PnP*` cmdlets or REST GETs -- zero tenant
writes anywhere in this plugin.

```
plugins/sharepoint-site-assessment/
├── scripts/
│   ├── discovery_inputs.py                        # shared DiscoveryStatus/DiscoveryOutcome vocabulary
│   ├── page_inventory_analysis.py / webpart_code_analysis.py / navigation_analysis.py /
│   │   forms_analysis.py / permissions_analysis.py  # read-only analysis of an export
│   ├── collect-sharepoint-page-inventory.ps1        # Site Pages inventory (modern SPO)
│   ├── collect-sharepoint-inventory.ps1             # lists/libraries/content-types (modern SPO, multi-mode)
│   ├── collect-onprem-sharepoint-inventory.ps1      # full crawl or quick counts (on-prem SP2016)
│   ├── collect-onprem-sharepoint-aspx-pages.ps1     # bulk .aspx download (on-prem SP2016)
│   ├── collect-sharepoint-site-navigation.ps1       # nav/chrome collector (on-prem SP2016)
│   ├── collect-sharepoint-webpart-content.ps1       # web-part scan + content extraction (on-prem SP2016)
│   ├── collect-sharepoint-custom-forms.ps1          # custom list-form download (on-prem SP2016)
│   ├── collect-sharepoint-permissions.ps1           # role-assignment collector (on-prem or SPO REST)
│   ├── audit-sharepoint-managed-metadata.ps1 / audit-onprem-sharepoint-managed-metadata.ps1
│   ├── audit-onprem-sharepoint-schema-drift.ps1
│   ├── generate-sharepoint-discovery-report-set.ps1 # local-only report assembler, no tenant I/O
│   └── assets/
│       ├── webpart-migration-rules.json
│       └── form-classification-rules.json
├── assets/
│   ├── webpart-migration-rules.json
│   ├── master-discovery-meta-review-template.md
│   └── site-navigation-chrome-summary-template.md
├── skills/
│   ├── analyze-page-inventory/       # + real collector
│   ├── analyze-webpart-code/         # + real collector; narrative fields (businessIntent/
│   │                                 #   enforcementLevel/spfxAssessment) added 2026-08-11
│   ├── analyze-site-navigation/      # + real collector
│   ├── analyze-custom-forms/         # + real collector
│   ├── analyze-permissions/          # + real collector (built from scratch -- no real source
│   │                                 #   script existed; the source's own SKILL.md had a
│   │                                 #   copy-paste bug pointing at the wrong script)
│   ├── collect-sharepoint-inventory/ # new
│   ├── audit-managed-metadata/       # new
│   ├── audit-onprem-schema-drift/    # new
│   └── generate-discovery-report-set/# new -- a corrective rewrite, not a straight port: the
│                                      #   source asserted fixed conclusions regardless of scan
│                                      #   data; this version is genuinely conditional or
│                                      #   reports data as unavailable, never fabricates
└── tests/
```

## Stage 1 / Stage 2 split for web-part analysis

`analyze-webpart-behavior`'s deterministic Stage 1 grouping now carries basic
narrative fields (business intent, enforcement level, SPFx assessment) --
generic where structurally unambiguous, caller-supplied via rules otherwise.
The full judgment-driven disposition (MVP decision, pattern-collapse across
groups, evidence gaps) is Stage 2, performed by
`sharepoint-webpart-modernization-analysis-agent` in
`sharepoint-site-migration`, not by this plugin -- route there once this
skill's grouped output exists.

## Honest outcomes

Every analysis skill reports one of: `OBSERVED`, `EMPTY`, `PARTIAL`,
`UNAVAILABLE`, `FORBIDDEN`, `FAILED`. A missing input is `UNAVAILABLE` and no
output directory is created; an empty result is `EMPTY`, never a silent
pass. Collector scripts emit `Write-Warning` on failed calls rather than
silently returning an empty/fabricated result.

## Not yet built

An orchestration layer over this plugin's skills (the source repo's
`sp-discovery-agent.md` describes a 13-14 step guided discovery sequence)
does not exist yet -- this plugin currently has zero agents. It may become a
skill or an agent; not decided until it's actually built. See
`.agent/map-debt.md`'s 2026-08-11 entries for the full history and
`docs/reports/sharepoint-migration-*-source-inventory.md` for the source
audit this plugin's real executors were built from.

## Install

```bash
pip install -e plugins/sharepoint-site-assessment
python3 -m pytest plugins/sharepoint-site-assessment/tests/ -q --ignore=plugins/sharepoint-site-assessment/tests/test_discovery_inputs.py
```

(`test_discovery_inputs.py` has one pre-existing, unrelated test that calls
`os.geteuid()`, which doesn't exist on Windows -- tracked separately, not
part of this plugin's own test failures.)

## Skills by functional group

### Inventory, analysis and read-only assessment

- `sharepoint-analyze-custom-forms` -- Analyses an exported classic SharePoint custom list-form inventory, classifying each form as out-of-box, script-based, or InfoPath/custom-layout, and attaches a caller-supplied modernization strategy per...
- `sharepoint-analyze-page-inventory` -- Analyses an exported classic SharePoint page inventory, scoring per-page migration complexity, classifying web-part categories and emitting a disposition hint per page (migrate as-is, rebuild, retire), using a...
- `sharepoint-analyze-permissions` -- Analyses an exported classic SharePoint permissions snapshot, deriving groups, evaluated objects and the subset with broken permission inheritance, to produce a group provisioning worksheet and a broken-inheritance...
- `sharepoint-analyze-site-navigation` -- Analyses an exported classic SharePoint site navigation tree (top nav and quick launch), flattening it with per-node depth and child counts and computing max-depth statistics, to produce a navigation architecture...
- `sharepoint-analyze-webpart-behavior` -- Groups classic SharePoint web parts by functional behaviour (inline script, external helper scripts, text-only, empty, or unretrievable) so near-duplicate instances collapse into a reviewable set. Use when a...
- `sharepoint-audit-managed-metadata` -- Audits a live SharePoint site for Managed Metadata (Taxonomy) usage, covering term group and term-set discovery plus every list, library and site column bound to a Taxonomy field, for modern SPO (PnP.PowerShell) or...
- `sharepoint-audit-onprem-schema-drift` -- Compares field schemas between a set of source lists and a set of destination lists on a legacy on-prem SP2016 site, reporting missing fields, type mismatches, required-field mismatches, broken lookup references and...
- `sharepoint-collect-site-inventory` -- Collects a live SharePoint inventory: lists and libraries, list fields, library files and content-type/schema exports (modern SPO via PnP.PowerShell), plus full site crawls, quick item and storage counts and bulk...
- `sharepoint-compare-schema-exports` -- Compares two exported SharePoint schema snapshots (lists, content types, site columns, per-list fields) and reports additions, removals and per-property changes, plus a duplicate-display-name audit. Use to answer...
- `sharepoint-extract-calculated-columns` -- Finds calculated-type fields across an exported SharePoint schema and reports each one's Formula and any [FieldName]-referenced field names, distinguishing "formula captured" from "formula not present in this export"...
- `sharepoint-extract-choice-columns` -- Inventories Choice and MultiChoice fields from an exported SharePoint schema and renders them as a list and internal-name keyed overrides mapping, distinguishing "no options defined" from "options unknown". Use when...
- `sharepoint-generate-assessment-reports` -- Assembles a set of Markdown discovery reports (master page and chrome, script editor and custom code, problematic web parts, unique web part code review catalog, security and permissions, custom list forms) from...

## Previous identities

Skill and plugin names changed in the seven-domain migration (issue #6). Old names are not retained as aliases.

| Previous skill | Current skill | Previous plugin |
|---|---|---|
| `sharepoint-analyze-webpart-code` | `sharepoint-analyze-webpart-behavior` | `sharepoint-discovery` |
| `sharepoint-collect-sharepoint-inventory` | `sharepoint-collect-site-inventory` | `sharepoint-discovery` |
| `sharepoint-audit-schema` | `sharepoint-compare-schema-exports` | `sharepoint-discovery` |
| `sharepoint-extract-choice-fields` | `sharepoint-extract-choice-columns` | `sharepoint-discovery` |
| `sharepoint-generate-discovery-report-set` | `sharepoint-generate-assessment-reports` | `sharepoint-discovery` |

## Installing

See the repository [INSTALL.md](../../INSTALL.md). Example:

```text
/plugin install sharepoint-site-assessment@sharepoint-knowledge-workbench
```
