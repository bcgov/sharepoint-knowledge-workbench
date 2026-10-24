# Acceptance Criteria: sharepoint-generate-assessment-reports

- Skill slug: `sharepoint-generate-assessment-reports`.
- Target plugin: `sharepoint-site-assessment`.
- Purpose: Assembles a set of Markdown discovery reports (master page and chrome, script editor and custom code, problematic web parts, unique web part code review catalog, security and permissions, custom list forms) from previously collected SharePoint JSON/CSV export files. Use once discovery collection has produced its raw files and you need readable reports for human review. Pure local report assembly; no tenant I/O.

## Constraints honored

- Local only. It reads files (`Get-Content`, `Import-Csv`) and writes `.md` reports into `-AnalysisDir`; it never contacts a SharePoint tenant.
- Never assert a conclusion the data doesn't support. Each section checks its input first. A missing input yields `Unavailable -- no <file> input was found at <path>`, not a hardcoded default.
- The security and permissions report is generated only when `-PermissionsJson` is supplied and readable; otherwise it is skipped with a `Write-Warning`.
- The Script Editor verdict is computed from the real count (`No.` only at zero, otherwise `Conditional -- requires manual review.`), and the custom-forms summary reports the real count and asks for manual review of each flagged list.
- `-AnalysisDir` and `-SiteName` have no defaults; pass both.

## Verification passes

- Confirm each expected `.md` report exists in `-AnalysisDir`, and that any skipped report has a matching warning. A report set with unavailable sections is partial, not complete.
- Focused plugin tests for this skill pass.
