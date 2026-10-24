# Legacy mode: sharepoint-backup-native-skills

---
name: sharepoint-backup-native-skills
plugin: sharepoint-copilot-agents-and-skills
description: Read-only backup of named AgentAssets native-skill and template files from a SharePoint tenant to a local directory. Use as a precaution before tenant cleanup or a redeploy. Makes no tenant changes.
allowed-tools: Bash, Read
---

# Backup SharePoint Native Skills

Download named `AgentAssets` skill and template files to a local directory. Idempotent: same output directory, overwritten in place.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Read-only: no tenant write of any kind.
- `-Items` is a required explicit list of `{Url, Dest}` hashtables. No hardcoded target list.
- `-ConfigFile` carries connection context only. When running an installed copy, pass it explicitly.

## Quick start

```powershell
pwsh -File scripts/backup-sharepoint-native-skills.ps1 -ConfigFile config.psd1 -Items @(@{Url='AgentAssets/Skills/my-skill/SKILL.md'; Dest='my-skill.md'}) -OutputDir ./backup
```

## Workflow

1. Confirm the exact `Url` and local `Dest` for each file.
2. Run the script with `-OutputDir`.
3. Keep the backup for `sharepoint-restore-native-skills`, which consumes the same shape.

## Verification

Every listed file exists locally under `-OutputDir`.

## References

- [Safety, config and permissions](../agents-and-skills-safety-and-config.md): read for the gate model of every script, the `-ConfigFile` default caveat and the Copilot permission note.
- [Backup and restore](../agent-backup-restore-details.md): read for the backup parameters and the matching restore.


# Legacy mode: sharepoint-restore-native-skills

---
name: sharepoint-restore-native-skills
plugin: sharepoint-copilot-agents-and-skills
description: Restores AgentAssets native-skill and template files from a local backup back to their tenant locations, dry-run by default with an explicit confirmation gate. Use to recover files saved by the native-skill backup skill.
allowed-tools: Bash, Read
---

# Restore SharePoint Native Skills

Restore files saved by `sharepoint-backup-native-skills` to their `AgentAssets` locations.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Dry run by default (zero tenant writes, shows exactly what would be restored). Any write needs both `-Execute` and `-ConfirmExactTarget "CONFIRM-RESTORE"`; a wrong string is rejected. A real run is a live tenant write that the user runs.
- `-Items` is a required explicit list of `{LocalPath, Url}` hashtables; a missing `LocalPath` fails before any connection. No default target list.
- When running an installed copy, pass `-ConfigFile` explicitly.

## Quick start

```powershell
pwsh -File scripts/restore-sharepoint-native-skills.ps1 -ConfigFile config.psd1 -Items @(@{LocalPath='./backup/my-skill.md'; Url='AgentAssets/Skills/my-skill/SKILL.md'})
```

## Workflow

1. Build `-Items` from the backup.
2. Dry run and review.
3. After the user confirms, rerun with `-Execute -ConfirmExactTarget "CONFIRM-RESTORE"`.

## Verification

The dry run lists exactly the items to restore; after a real run, verify with `sharepoint-verify-native-skill`.

## References

- [Safety, config and permissions](../agents-and-skills-safety-and-config.md): read for the gate model of every script, the `-ConfigFile` default caveat and the Copilot permission note.
- [Backup and restore](../agent-backup-restore-details.md): read for the restore parameters and the evidence-ordering bug fix.
