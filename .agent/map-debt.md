
### [2026-07-30] PnP.PowerShell Modern Page & Document Library Upload Script Friction

- **Logged Date**: 2026-07-30
- **Artifact Affected**: `tools/phase-3-sharepoint-discovery/run-phase3-tenant-pilot.ps1`
- **Friction Observed**: 
  1. `Set-PnPPage -Values` is invalid syntax in PnP.PowerShell for custom page metadata (must use `Set-PnPListItem` with item ID).
  2. `Add-PnPPage` fails with "already exists" on rerun unless existence check and update logic are implemented.
  3. `& pandoc` output returns a string array in PowerShell, breaking `Add-PnPPageTextPart -Text` unless joined with `-join "`n"`.
  4. `Resolve-PnPFolder` fails with `Access Denied` on custom Document Libraries (must use `Add-PnPFolder -Name "media" -Folder "LibraryName"` instead).
  5. CAML queries for items inside subfolders require `<View Scope='RecursiveAll'>`.
- **Why It Was Not Fixed Now**: Fixed inline during Phase 3 tenant pilot execution.
- **Recommended Fix**: Update PnP.PowerShell authoring playbooks / templates to encode these 5 PnP.PowerShell modern-page patterns by default.
- **Evidence**: `run-phase3-tenant-pilot.ps1` commits `4323198`, `a530de0`, `65ef41f`, `55a9099`, `dbde503`, `6fd27c2`.
- **Severity**: M
- **Repeat**: NO
- **Status**: RESOLVED
