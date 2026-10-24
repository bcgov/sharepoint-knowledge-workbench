# Legacy mode: sharepoint-backup-agents

---
name: sharepoint-backup-agents
plugin: sharepoint-copilot-agents-and-skills
description: Read-only backup of named .agent files from a SharePoint site to a local directory. Use as a precaution before any tenant cleanup or agent change. Makes no tenant changes.
allowed-tools: Bash, Read
---

# Backup SharePoint Agents

Download named `.agent` files to a local directory. Idempotent: it always writes to the same output directory and overwrites in place.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Read-only: no tenant write of any kind.
- Two modes. **Named:** `-SitePath` and `-AgentFileNames` back up exactly the files the caller names. **Discovery:** `-All` (or omitting `-AgentFileNames`) scans the `Site Pages`, `AgentAssets` and `KnowledgePublications` libraries of the connected site for every `.agent` file and backs them all up. There is no hardcoded file list in either mode.
- `-ConfigFile` carries connection context only. When running an installed copy, pass it explicitly.

## Quick start

```powershell
pwsh -File scripts/backup-sharepoint-agents.ps1 -ConfigFile config.psd1 -SitePath "<site-relative folder>" -AgentFileNames @('agent-one.agent') -OutputDir ./backup

# or discover every .agent file in the standard agent libraries
pwsh -File scripts/backup-sharepoint-agents.ps1 -ConfigFile config.psd1 -All -OutputDir ./backup
```

## Workflow

1. Choose the mode: confirm the site-relative folder and exact `.agent` file names, or use `-All` to back up everything the standard libraries hold.
2. Run the script with `-OutputDir`.
3. Keep the backup for `sharepoint-restore-agents`.

## Verification

In named mode every named file exists in `-OutputDir`; a missing file is reported, not skipped. In discovery mode the printed count matches the files in `-OutputDir`.

## References

- [Safety, config and permissions](../agents-and-skills-safety-and-config.md): read for the gate model of every script, the `-ConfigFile` default caveat and the Copilot permission note.
- [Backup and restore](../agent-backup-restore-details.md): read for the backup parameters and the matching restore.


# Legacy mode: sharepoint-restore-agents

---
name: sharepoint-restore-agents
plugin: sharepoint-copilot-agents-and-skills
description: Restores .agent files from a local backup back to their tenant locations, dry-run by default with an explicit confirmation gate. Use to recover agents saved by the backup skill.
allowed-tools: Bash, Read
---

# Restore SharePoint Agents

Restore files saved by `sharepoint-backup-agents` to their tenant locations.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Dry run by default (zero tenant writes). Any write needs both `-Execute` and `-ConfirmExactTarget "CONFIRM-RESTORE"`; a single `-Execute` is rejected. A real run is a live tenant write that the user runs.
- `-Items` is a required explicit list of `{LocalPath, Url}` hashtables; it fails before any connection if a `LocalPath` does not exist. No default target list.
- Running a restored agent in the Copilot UI needs the user to be an explicit Site Owner, even if the restore succeeded.
- When running an installed copy, pass `-ConfigFile` explicitly.

## Quick start

```powershell
pwsh -File scripts/restore-sharepoint-agents.ps1 -ConfigFile config.psd1 -Items @(@{LocalPath='./backup/agent-one.agent'; Url='<server-relative url>'})
```

## Workflow

1. Build `-Items` from the backup.
2. Dry run and review what would be restored.
3. After the user confirms, rerun with `-Execute -ConfirmExactTarget "CONFIRM-RESTORE"`.

## Verification

The dry run lists exactly the items to restore; after a real run, each `.agent` is present at its `Url`.

## References

- [Safety, config and permissions](../agents-and-skills-safety-and-config.md): read for the gate model of every script, the `-ConfigFile` default caveat and the Copilot permission note.
- [Backup and restore](../agent-backup-restore-details.md): read for the restore parameters and tests.
