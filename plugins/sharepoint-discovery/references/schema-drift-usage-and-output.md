# On-prem schema drift: usage, output and provenance

## Contents

- [What it compares](#what-it-compares)
- [Usage](#usage)
- [Auth](#auth)
- [Output](#output)
- [Related asset](#related-asset)
- [Provenance](#provenance)

## What it compares

Field schemas (by internal name) between caller-supplied source lists and caller-supplied
destination lists: missing fields, type mismatches, and required-field mismatches in either
direction. It also validates lookup-field references and inspects workflow associations across every
list on the site.

## Usage

```bash
pwsh -File scripts/audit-onprem-sharepoint-schema-drift.ps1 \
  -SiteUrl "https://sp2016.example.org/sites/Legacy" \
  -SourceListNames @('Matches_Received','All_Appearances') \
  -DestinationListPattern "Cal_*" \
  -OutputDir .\schema-drift-report

pwsh -File scripts/audit-onprem-sharepoint-schema-drift.ps1 \
  -SiteUrl "https://sp2016.example.org/sites/Legacy" \
  -SourceListNames @('Requests') \
  -DestinationListNames @('Archive_2024','Archive_2025') \
  -WatchFieldNames @('Case_ID','Status') \
  -UseCredential
```

`-SiteUrl` falls back to `SiteUrl` in the plugin's `config.psd1` if omitted. `-WatchFieldNames` is
optional and only narrows the dedicated "Field Types" section of the markdown output; the field
schema CSV and the mismatch comparison always cover every field on every list.

## Auth

`Connect-PnPOnline -UseWebLogin` (or `-Credentials` with `-UseCredential`). This is a documented
exception to the repository's modern-SPO `-Interactive` convention, since PnP.PowerShell supports
on-prem SP2016 via CSOM and web login rather than Entra app registrations. See the repository's
`sharepoint-ps1-authentication-convention.md` rule.

## Output

Written to `-OutputDir`: five CSVs (`SchemaDrift-ListSchema.csv`, `SchemaDrift-FieldSchema.csv`,
`SchemaDrift-ContentTypes.csv`, `SchemaDrift-SchemaMismatches.csv`,
`SchemaDrift-WorkflowDependencies.csv`) plus one markdown summary (`SchemaDrift-Report.md`) combining
all findings with a recommended-remediation section.

## Related asset

`assets/master-discovery-meta-review-template.md` is a generalized migration-readiness catalog
template from the same source project. It is a broader 13-domain site-modernization summary fed by
many discovery passes, not just schema comparison. This skill's output does not map onto its
placeholders directly, so it is a standalone asset for whoever assembles that broader catalog.

## Provenance

Ported and generalized from `plugins/sharepoint-migration/scripts/diagnose-onprem-schema-drift.ps1`
in the originating SharePoint migration repository. All hardcoded sentinel field names, list names,
wildcard patterns and project-specific report prose were removed in favor of explicit
`-SourceListNames`, `-DestinationListNames`, `-DestinationListPattern` and `-WatchFieldNames`
parameters.
