# Acceptance Criteria: sharepoint-audit-managed-metadata

- Skill slug: `sharepoint-audit-managed-metadata`.
- Target plugin: `sharepoint-site-assessment`.
- Purpose: Audits a live SharePoint site for Managed Metadata (Taxonomy) usage, covering term group and term-set discovery plus every list, library and site column bound to a Taxonomy field, for modern SPO (PnP.PowerShell) or legacy on-prem SP2016 (NTLM/Kerberos REST plus CSOM). Use ahead of a migration or schema-design decision to learn whether and where a site uses Managed Metadata.

## Constraints honored

- Reads only. Both scripts use `Get-PnP*` cmdlets, `Invoke-RestMethod` GET calls, or CSOM `ExecuteQuery()` calls that only load and read term-store objects. Zero writes.
- Never fabricate or silently drop a failure. Failed REST calls, PnP errors and an unresolvable Term Group are recorded as `Error` or `Found: false` fields in the JSON. A CSOM assembly or version failure on-prem is a non-fatal finding, not an exception.
- Both scripts perform live tenant I/O and the user runs them. On-prem uses NTLM/Kerberos because there is no Entra app-registration path in general use there.

## Verification passes

- Confirm the JSON exists at `-OutputPath`, then list any `Error` or `Found: false` entries as findings rather than treating the audit as clean.
- Focused plugin tests for this skill pass.
