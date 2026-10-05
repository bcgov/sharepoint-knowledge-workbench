---
name: sharepoint-download-file
plugin: sharepoint-site-build-and-publish
description: Downloads a remote document, file, or page from a SharePoint Online library or site to a local directory with existence and size verification. Use when retrieving remote files for inspection, offline backup, or local processing. Zero tenant writes.
allowed-tools: Bash, Read, Write
examples:
  - "pwsh -File scripts/spo-download-file.ps1 -ServerRelativeUrl \"/sites/Site/Shared Documents/file.pdf\" -DestinationDir \"./downloads\" -Execute -ConfirmToken DOWNLOAD-SPO-FILE"
---

# Download File from SharePoint Online

Downloads a document, file, or page from a SharePoint Online library or folder to a local directory using PnP.PowerShell (`Get-PnPFile -AsFile`).

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Zero tenant writes: downloads content only; never modifies tenant state.
- Dry-run by default: running without `-Execute` validates connection configuration and prints the planned local destination path without downloading.
- Real execution requires `-Execute -ConfirmToken DOWNLOAD-SPO-FILE`.
- By default does not overwrite existing local files unless `-Overwrite` is passed.
- Requires PnP.PowerShell module with delegated/interactive or app-only authentication configured.

## Quick start

### 1. Dry Run (Preview download target)

```powershell
pwsh -File scripts/spo-download-file.ps1 `
  -ServerRelativeUrl "/sites/AG-CSB-INTRANET-DEV/Shared Documents/test2.html" `
  -DestinationDir ".\temp"
```

### 2. Live Download

```powershell
pwsh -File scripts/spo-download-file.ps1 `
  -ServerRelativeUrl "/sites/AG-CSB-INTRANET-DEV/Shared Documents/test2.html" `
  -DestinationDir ".\temp" `
  -Execute `
  -ConfirmToken DOWNLOAD-SPO-FILE
```

## Workflow

1. **Resolve Remote URL**: Identify the server-relative or site-relative URL of the file (e.g. `/sites/<site>/<library>/<file>`).
2. **Pre-flight Check**: Run dry-run to ensure the destination path is writable and determine if `-Overwrite` is needed.
3. **Execute Download**: Run with `-Execute -ConfirmToken DOWNLOAD-SPO-FILE`.
4. **Post-Download Verification**: Check that the local file exists and byte size matches expectations.

## Verification

Check local file arrival and size:
```powershell
Get-Item .\temp\test2.html | Select-Object Name, Length, LastWriteTime
```

## References

- Implementation: `scripts/spo-download-file.ps1`
- Connection helper: `scripts/Get-WorkbenchConnectionConfig.ps1`
