# Mode: Sync Navigation

Apply operations to SharePoint Online using PnP PowerShell.

## Dry-run (Default)

```powershell
pwsh -File scripts/sync-spo-navigation.ps1 -ConfigPath <config.psd1> -OpsPath <ops.json>
```

Reviews all create, update, and prune candidates without performing any tenant writes.

## Execution (Human-Gated)

```powershell
pwsh -File scripts/sync-spo-navigation.ps1 -ConfigPath <config.psd1> -OpsPath <ops.json> -Execute -ConfirmToken PROVISION-SPO-NAV
```

To enable node removal: add `-Prune`. Only pass `-Prune` after removals have been reviewed.

## Safety Guards
- Preflight verifies all update and prune targets before touching the tenant.
- A full JSON snapshot backup is saved before any mutation.
- Execution halts at the first encountered error.
- Idempotent: re-running with the same workbook produces 0 diffs.
