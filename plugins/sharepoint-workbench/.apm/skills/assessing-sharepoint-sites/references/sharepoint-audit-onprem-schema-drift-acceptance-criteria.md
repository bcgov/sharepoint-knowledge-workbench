# Acceptance Criteria: sharepoint-audit-onprem-schema-drift

- Skill slug: `sharepoint-audit-onprem-schema-drift`.
- Target plugin: `sharepoint-site-assessment`.
- Purpose: Compares field schemas between a set of source lists and a set of destination lists on a legacy on-prem SP2016 site, reporting missing fields, type mismatches, required-field mismatches, broken lookup references and workflow associations. Use for schema-drift root-cause analysis when a data copy or workflow fails, or ahead of a migration that depends on matching schemas.

## Constraints honored

- Site reads only: `Get-PnP*` cmdlets and CSOM `ExecuteQuery()` calls that load and read list, field and workflow objects. Zero writes; the script's own header enforces this as a hard rule.
- Never fabricate or silently skip. Failed `Get-PnPField` or `Get-PnPContentType` calls and workflow-association reads emit `Write-Warning` and leave the affected record set empty.
- Source and destination lists are always caller-supplied. No list names or sentinel fields are built in.
- The script performs live site I/O and the user runs it.

## Verification passes

- Confirm the five CSVs and `SchemaDrift-Report.md` exist in `-OutputDir`, and list every `Write-Warning` as a gap rather than a clean result.
- Focused plugin tests for this skill pass.
