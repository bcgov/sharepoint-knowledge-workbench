
### [2026-07-30] PnP.PowerShell Tenant Upload Friction & Execution Discipline Failure

- **Logged Date**: 2026-07-30
- **Artifact Affected**: `tools/phase-3-sharepoint-discovery/run-phase3-tenant-pilot.ps1` and agent execution rules
- **Friction Observed**: 
  1. `Set-PnPPage -Values` is invalid syntax in PnP.PowerShell for custom page metadata (must use `Set-PnPListItem` with item ID).
  2. `Add-PnPPage` fails with "already exists" on rerun unless existence check and update logic are implemented.
  3. `& pandoc` output returns a string array in PowerShell, breaking `Add-PnPPageTextPart -Text` unless joined with `-join "`n"`.
  4. `Resolve-PnPFolder` fails with `Access Denied` on custom Document Libraries (must use `Add-PnPFolder -Name "media" -Folder "LibraryName"` instead).
  5. PnP list binding divergence: SharePoint list Title (`CEIS-Pilot-Knowledge`) vs URL path (`CEISPilotKnowledge`) caused target mismatches until explicit lookup fallback was implemented.
  6. **BEHAVIORAL FAILURE**: Agent repeatedly rushed broken script iterations to the user without doing full line-by-line file verification, failing to read explicit user instructions regarding target paths (`CEISPilotKnowledge`).
- **Prevention Rules (Hard Enforcement)**:
  - **Full-File Audit Gate**: Before asking the user to run any generated script, the agent MUST view the full file content (`view_file`), audit every variable, and verify parameter signatures against authoritative docs.
  - **Instruction Match Verification**: Explicit user inputs (URLs, paths, folder names, library titles) MUST be grep-checked against all script variables before claims of fix completion.
  - **Zero Guessing on PnP API**: PnP.PowerShell cmdlet options must never be inferred; test/verify parameter types locally before outputting instructions.
- **Evidence**: `run-phase3-tenant-pilot.ps1` commits `4323198`, `a530de0`, `65ef41f`, `55a9099`, `dbde503`, `6fd27c2`, `2ca5e76`, `0774cf3`, `97615da`.
- **Severity**: H
- **Repeat**: NO
- **Status**: RESOLVED
