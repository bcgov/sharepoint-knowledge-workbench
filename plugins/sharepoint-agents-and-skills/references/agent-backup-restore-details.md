# Agent and native skill backup and restore

## Contents

- [Backup](#backup)
- [Restore](#restore)
- [Tests (source repository only)](#tests-source-repository-only)

## Backup

Read-only download of named files to a local directory, as a precaution before any tenant cleanup. No tenant change of any kind. Idempotent: it always writes to the same fixed output directory and overwrites in place.

- **Agents** (`backup-sharepoint-agents.ps1`): `-ConfigFile` (connection context only); `-SitePath` (required, the site-relative folder holding the `.agent` files); `-AgentFileNames` (required explicit list, no hardcoded
  default; generalized from an original script that hardcoded specific agent filenames); `-OutputDir`.
- **Native skills** (`backup-sharepoint-native-skills.ps1`): `-ConfigFile`; `-Items` (required explicit list of `{Url, Dest}` hashtables, no hardcoded target list); `-OutputDir`.

## Restore

New builds with no prior implementation. They restore files saved by the matching backup skill to their tenant locations (`.agent` files, or `AgentAssets` native-skill and template files).

- `-ConfigFile` (connection context only); `-Items` (required explicit list of `{LocalPath, Url}` hashtables). It fails before any connection attempt if any `LocalPath` does not exist.
- Dry run by default (zero tenant writes, displays exactly what would be restored). Any write needs both `-Execute` and `-ConfirmExactTarget "CONFIRM-RESTORE"`.
- No default target list; every restore target is explicit. The two-part confirmation matches `sharepoint-rollback-sharepoint-native-skill`'s pattern.

After restoring an `.agent`, running it in the SharePoint Copilot UI still needs the user to be an explicit Site Owner (see `agents-and-skills-safety-and-config.md`).

## Tests (source repository only)

`tests/unit/test_restore_sharepoint_agents.py` (3 tests: dry run performs zero writes; a missing confirmation is rejected with evidence written before failing; a missing local backup file fails before any tenant connection) and
`test_restore_sharepoint_native_skills.py` (4 tests: the same plus a wrong confirmation string is rejected). Both were written with the evidence-before-`Write-Error` ordering fix applied.
