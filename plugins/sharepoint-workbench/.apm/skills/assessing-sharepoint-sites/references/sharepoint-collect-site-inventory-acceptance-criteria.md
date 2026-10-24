# Acceptance Criteria: sharepoint-collect-site-inventory

- Skill slug: `sharepoint-collect-site-inventory`.
- Target plugin: `sharepoint-site-assessment`.
- Purpose: >-

## Constraints honored

- Reads only. All scripts use `Get-PnP*` cmdlets or `Invoke-RestMethod`/`Invoke-WebRequest` GET calls. Zero writes.
- Never fabricate or silently skip. Failed REST calls and PnP errors emit `Write-Warning` and leave the affected record set empty.
- The scripts perform live tenant I/O and the user runs them. On-prem uses NTLM/Kerberos REST, since there is no Entra app-registration path in general use there.

## Verification passes

- Confirm the output file or directory exists and list every `Write-Warning` as a gap rather than a clean result. For content inventories, check `manifest.json`: `COMPLETE` means collection succeeded within its declared scope; `EMPTY` means no files; `PARTIAL`/`FAILED` means inspect `errors.csv`. Partial/failed content collection exits nonzero and retains successful rows. Permission-trimmed objects can remain invisible even without errors; do not claim tenant-wide completeness.
- Focused plugin tests for this skill pass.
