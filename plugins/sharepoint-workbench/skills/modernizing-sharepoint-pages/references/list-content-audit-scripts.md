# List content audit: model, scripts and audit config

## Contents

- [Business-key ground truth model](#business-key-ground-truth-model)
- [Audit config](#audit-config)
- [Scripts and tools](#scripts-and-tools)
- [Recording known issues](#recording-known-issues)

## Business-key ground truth model

When SharePoint list items or target lookup parent lists (for example a people or reference list) are re-migrated or
ID-shifted, lookup pointers can drop (`$null`), point to stale integer IDs, or misbind to the wrong entity through
string-matching collisions. The audit uses a business-key ground truth model:

1. Index on-premises source data by an immutable natural business key (the configured `key_columns`, default `Title`).
2. Translate source IDs of the parent list into verified target IDs through a deterministic mapping
   (`id-mapping-verified.json`).
3. Compare expected ground truth against actual live SharePoint Online state.
4. Output zero-PII metrics and export row-by-row variance reports (the evidence a human uses to decide on any separate repair).

## Audit config

Nothing about a specific site, list or column is built into the scripts. Describe the site being audited in an
`audit-config.json` (start from `scripts/audit-config.example.json`; keep your real copy out of version control):

| Key | Meaning |
| :--- | :--- |
| `lists` | Lists to audit. Default: every list that has a configured lookup. |
| `exclude_lists` | Lists to skip, for example lists owned by another integration. |
| `key_columns` | Business-key columns tried in order. Default: `["Title"]`. |
| `id_pattern` | Regex for business keys that are safe to print in reports. Anything else is masked. |
| `identity_mapping` | `{ "list": "<list>", "tiers": [ {"name": "<tier>", "columns": ["<col>", ...]} ] }`: how `analyze-list-mapping-assurance.py` matches source rows to target rows; earlier tiers win. |
| `lookups` | `{ "<list>": { "<spoColumn>": ["<onPremColumn>", "<targetList>"] } }`. Lookups whose target list is the identity list (`-IdentityListName`, or `identity_mapping.list` in the audit config) are translated through `id-mapping-verified.json`. |

The reconciler also accepts `-MatrixPath` (a wave dependency matrix) as an additional source of lookup definitions.
Connection details come from the `config-*.psd1` file passed as `-ConfigPath`; URLs belong there and nowhere else.

## Scripts and tools

| Script | Type | Description |
| :--- | :--- | :--- |
| `scripts/analyze-list-mapping-assurance.py` | Python 3 | Prerequisite: config-driven identity mapping. Reads the paired exports of the list named in the audit config's `identity_mapping` and matches source rows to target rows tier by tier on the configured columns, writing the zero-PII `id-mapping-verified.json` consumed by the analyzers. Supports `--delete-pii-after` to purge the raw CSVs once the mapping is built. |
| `scripts/export-list-content-pairs.ps1` | PowerShell 7 | Discovery step: populates paired CSV datasets of current list content from the on-premises source and SharePoint Online into `.agents/scratch/pii-data/`, for downstream variance analysis. Lists come from the audit config or `-ListName`; `-OnPremUrl` is required. |
| `scripts/audit-list-lookup-reconciliation.ps1` | PowerShell 7 | Config-driven. Extracts source ground truth, queries live SharePoint Online, reconciles lookups, and computes business-key suffix skew into `.agents/scratch/audit-reports/`. |
| `scripts/analyze-lookup-variances.py` (or `analyze-all-variances.py`) | Python 3 | Full-spectrum content, row and lookup variance auditor generating zero-PII reports in `.agents/scratch/audit-reports/`. Reads the audit config (`--audit-config`, default `<data-dir>/audit-config.json`). |
| `scripts/check-list-id-suffix-skew.ps1` | PowerShell 7 | Standalone read-only diagnostic measuring item ID vs business-key suffix shifts for one list (`-ListName`, optional `-KeyColumns`). |
| `scripts/audit-config.example.json` | Data (JSON) | Neutral example of the audit config. |

The audit skill has no repair script: repairs of lookup values are a separate, human-approved activity that belongs
to the migration skills, not to this read-only audit.

## Recording known issues

Keep a local, uncommitted note (for example in your migration project's `docs/` folder) of parity issues you have
already root-caused: affected list(s) and column(s), the observable symptom signature, the confirmed root cause, the
status (resolved, accepted-gap or needs-backfill) and the sanctioned remediation. Add an entry whenever an audit
confirms a fresh root cause for a recurring variance, instead of leaving the explanation only in a one-off analysis
document that can go stale. The scripts do not read this file.
